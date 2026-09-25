"""Dynamic value of information: when does an extra costly observation help a
sequence of decisions (INTEGRATED_EXTENSION_ROADMAP.md Paket C6) -- response
to prompts/Answers/nicht_stationäre_Treiber/SCF_INTEGRATED_EXTENSION_IMPLEMENTATION_PLAN.md,
section 10.

Binary hidden state ``X_t in {0,1}``, ``P(X_0=1)=0.5``, flips with
probability ``p`` per step. At each of ``H`` decision steps the agent either
(a) makes a decision using its current BELIEF ``b=P(X_t=1)`` alone (reward
``max(b,1-b)``, the probability of guessing correctly), or (b) pays cost
``c`` for an immediate PERFECT observation of the current state, then
decides with certainty (reward ``1-c``). The belief updates deterministically
between decisions via

    T(b) = p + (1-2p)*b

(a contraction toward 0.5 at rate ``|1-2p|`` per step -- ``T(b)-0.5 =
(1-2p)*(b-0.5)``). The optimal value function solves the Bellman recursion

    V_0(b) = 0
    V_h(b) = max( max(b,1-b) + V_{h-1}(T(b)),
                  (1-c) + b*V_{h-1}(T(1)) + (1-b)*V_{h-1}(T(0)) )

by plain backward recursion (no discretized POMDP solver, no LLM dependency
-- a finite, exactly enumerable decision tree for the small horizons used
here).

**Hand-verified control case** (independently re-derived, checked in
``verify_sequential_information_pilot.py`` before this module was written):
``p=0.1``, ``c=0.2``, 2 decisions starting from ``b=0.5``. Never measuring
gives ``1.0``; always measuring gives ``2*(1-0.2)=1.6``; measuring once then
exploiting persistence for the second decision gives
``(1-0.2)+max(T(1),1-T(1))=1.7``. The Bellman recursion's optimum,
``V_2(0.5)``, is exactly ``1.7`` -- the "measure once" strategy is optimal
here, neither of the two naive extremes.

**Message aging**: after a PERFECT observation of ``X_0`` with no further
information, the optimal hit rate for guessing ``X_d`` (``d`` steps later)
is ``1/2 + 1/2*|1-2p|^d`` (from the contraction rate above). For ``p=0.1``:
``d=1 -> 0.9``, ``d=2 -> 0.82``, ``d=10 -> 0.5536870912``.

**"Free option" property (mandatory check):** since "don't measure" is
always one of the two branches available in the Bellman recursion above,
the OPTIONAL, costly measurement can never make the optimal value WORSE than
a policy that is not even allowed to measure at all (``V_never``, the same
recursion with the measurement branch removed) -- for ANY ``c>=0``. A
violation of this would indicate a bug in the recursion, not a real
phenomenon (an optional, priced signal is a free option: you can always
decline it).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple

from scoped_correspondence.errors import ScopeViolationError


def belief_transition(b: float, p: float) -> float:
    if not (0.0 <= p <= 1.0):
        raise ScopeViolationError(f"p must be in [0,1]; got {p!r}")
    if not (0.0 <= b <= 1.0):
        raise ScopeViolationError(f"b must be in [0,1]; got {b!r}")
    return p + (1.0 - 2.0 * p) * b


def iterated_belief(b0: float, p: float, d: int) -> float:
    """``T`` applied ``d`` times, via the closed form
    ``0.5 + (1-2p)^d * (b0-0.5)`` (cross-checked against direct iteration in
    ``verify_sequential_information_pilot.py``)."""
    if d < 0:
        raise ScopeViolationError(f"d must be >= 0; got {d!r}")
    return 0.5 + (1.0 - 2.0 * p) ** d * (b0 - 0.5)


@dataclass(frozen=True)
class BellmanResult:
    value: float
    action: str  # "measure" | "no_measure" | "tie"


def bellman_value(horizon: int, b: float, p: float, c: float) -> BellmanResult:
    """Optimal expected total reward over ``horizon`` remaining decisions
    starting from belief ``b`` (module docstring). Plain recursion, no
    memoization needed at these horizons (each call branches into at most 2
    further beliefs, so the tree has at most ``2^horizon`` nodes)."""
    if horizon < 0:
        raise ScopeViolationError(f"horizon must be >= 0; got {horizon!r}")
    if c < 0.0:
        raise ScopeViolationError(f"c must be >= 0; got {c!r}")
    if horizon == 0:
        return BellmanResult(value=0.0, action="no_measure")

    no_measure = max(b, 1.0 - b) + bellman_value(horizon - 1, belief_transition(b, p), p, c).value
    measure = (
        (1.0 - c)
        + b * bellman_value(horizon - 1, belief_transition(1.0, p), p, c).value
        + (1.0 - b) * bellman_value(horizon - 1, belief_transition(0.0, p), p, c).value
    )
    if abs(no_measure - measure) < 1e-12:
        return BellmanResult(value=no_measure, action="tie")
    return BellmanResult(value=max(no_measure, measure), action=("measure" if measure > no_measure else "no_measure"))


def value_never_measure(horizon: int, b: float, p: float) -> float:
    """The SAME recursion with the measurement branch removed entirely --
    an independently-computed reference for the free-option check."""
    if horizon < 0:
        raise ScopeViolationError(f"horizon must be >= 0; got {horizon!r}")
    if horizon == 0:
        return 0.0
    return max(b, 1.0 - b) + value_never_measure(horizon - 1, belief_transition(b, p), p)


def optimal_hit_rate_after_perfect_observation(p: float, d: int) -> float:
    """``1/2 + 1/2*|1-2p|^d`` -- the optimal hit rate for guessing ``X_d``
    given a PERFECT observation of ``X_0`` and no further information
    (module docstring, "message aging")."""
    if d < 0:
        raise ScopeViolationError(f"d must be >= 0; got {d!r}")
    return 0.5 + 0.5 * abs(1.0 - 2.0 * p) ** d


@dataclass(frozen=True)
class ChannelDecoderResult:
    q: float
    optimal_accuracy: float
    naive_accuracy: float


def symmetric_channel_decoders(q: float) -> ChannelDecoderResult:
    """A uniform prior bit ``X`` passed through a binary symmetric channel
    with flip probability ``q`` (``Y=X`` w.p. ``1-q``, ``Y=1-X`` w.p. ``q``).
    The OPTIMAL (Bayes) decoder achieves accuracy ``max(1-q,q)`` -- trusting
    the raw output ``Y`` when ``q<0.5``, INVERTING it when ``q>0.5`` (a
    channel that is "wrong more often than right" is informative once you
    know to invert it). The NAIVE decoder always trusts ``Y`` directly
    (accuracy ``1-q`` even when that is worse than chance)."""
    if not (0.0 <= q <= 1.0):
        raise ScopeViolationError(f"q must be in [0,1]; got {q!r}")
    return ChannelDecoderResult(q=q, optimal_accuracy=max(1.0 - q, q), naive_accuracy=1.0 - q)


def parameter_panel(
    p_values=(0.0, 0.1, 0.5, 0.9), c_values=(0.0, 0.1, 0.2, 0.5, 0.6), horizon: int = 5, b0: float = 0.5
) -> Dict[Tuple[float, float], BellmanResult]:
    """Representative (p, c) panel at a fixed horizon and starting belief --
    not the full (p, c, delay, horizon) cross product named in the plan
    (deferred, see module docstring / docs/sequential_information_pilot.md
    for scope)."""
    return {(p, c): bellman_value(horizon, b0, p, c) for p in p_values for c in c_values}


__all__ = [
    "belief_transition",
    "iterated_belief",
    "BellmanResult",
    "bellman_value",
    "value_never_measure",
    "optimal_hit_rate_after_perfect_observation",
    "ChannelDecoderResult",
    "symmetric_channel_decoders",
    "parameter_panel",
]
