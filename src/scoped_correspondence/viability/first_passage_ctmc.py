"""M/M/1 queue: exact first-passage probability to a capacity level (DOMAIN_EXPANSION_ROADMAP.md Paket B2b).

Response to prompts/Answers/nicht_stationäre_Treiber/
SCF_DOMAIN_EXPANSION_IMPLEMENTATION_PLAN.md, section 8.3: **the stationary
tail probability P(N>=K) is NOT the same question as P(max_{t<=H} N_t>=K)**
-- a mean-load or steady-state description can look perfectly safe while a
genuine transient excursion to the capacity boundary is likely within a
finite horizon.

For an M/M/1 queue (Poisson arrivals rate ``lambda``, exponential service
rate ``mu``), restrict to the finite state space ``{0, 1, ..., K}`` and make
``K`` ABSORBING (all outgoing transitions from ``K`` removed). This is exact
for the UNBOUNDED M/M/1 chain's first-passage event to level ``K`` --
states above ``K`` are irrelevant to "when do we first reach K", so no
artificial upper truncation is needed. With row-vector convention
``p'(t) = p(t) Q``:

    P(tau_K <= H) = [p_0 * exp(H*Q_abs)]_K

where ``p_0`` is a unit row vector at the initial count and ``Q_abs`` is the
generator with row ``K`` zeroed out (absorbing). This construction requires
NO special-casing for ``H=0``, ``lambda=0``, or ``mu=0`` -- each reduces
correctly through the SAME matrix exponential (``H=0`` gives the identity;
``lambda=0`` makes ``K`` unreachable from below; ``mu=0`` collapses the
chain to a pure-birth/Poisson process, reproducing the closed-form Poisson
tail exactly -- see ``verify_queueing_first_passage.py``).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence, Tuple

import numpy as np
from scipy.linalg import expm

from scoped_correspondence.errors import ScopeViolationError


def _validate_rates(arrival_rate: float, service_rate: float) -> None:
    if not np.isfinite(arrival_rate) or not np.isfinite(service_rate):
        raise ScopeViolationError(f"rates must be finite; got arrival_rate={arrival_rate!r}, service_rate={service_rate!r}")
    if arrival_rate < 0.0 or service_rate < 0.0:
        raise ScopeViolationError(
            f"rates must be >= 0; got arrival_rate={arrival_rate!r}, service_rate={service_rate!r}"
        )


def _validate_count_state(value: float, name: str) -> int:
    """CTMC states are discrete customer counts -- reject NaN/Inf/non-integer values
    with a clear message instead of letting them reach a numpy array index/size and
    raise an unrelated TypeError/IndexError."""
    if not np.isfinite(value):
        raise ScopeViolationError(f"{name} must be finite; got {value!r}")
    if value < 0.0 or abs(value - round(value)) > 1e-9:
        raise ScopeViolationError(f"{name} must be a non-negative integer (CTMC count state); got {value!r}")
    return int(round(value))


def mm1_absorbing_generator(threshold: int, arrival_rate: float, service_rate: float) -> np.ndarray:
    """The ``(threshold+1) x (threshold+1)`` CTMC generator for states ``0..threshold``
    of an M/M/1 queue, with state ``threshold`` made ABSORBING (row zeroed)."""
    threshold = _validate_count_state(threshold, "threshold")
    _validate_rates(arrival_rate, service_rate)
    n = threshold + 1
    Q = np.zeros((n, n))
    for state in range(threshold):
        Q[state, state + 1] += arrival_rate
        if state > 0:
            Q[state, state - 1] += service_rate
        Q[state, state] = -float(np.sum(Q[state]))
    # row `threshold` stays all zero: absorbing.
    return Q


def queue_hitting_probability(
    initial_count: int, threshold: int, horizon: float, arrival_rate: float, service_rate: float
) -> float:
    """``P(tau_threshold <= horizon)`` for an M/M/1 queue started at ``initial_count``.

    Handles ``horizon=0``, already-reached ``threshold`` (``initial_count >= threshold``),
    ``arrival_rate=0`` (threshold then unreachable from below), and ``service_rate=0``
    (pure-birth/Poisson reduction) all through the SAME construction -- no branching
    needed for any of these beyond the initial "already reached" shortcut.
    """
    initial_count = _validate_count_state(initial_count, "initial_count")
    threshold = _validate_count_state(threshold, "threshold")
    if not np.isfinite(horizon):
        raise ScopeViolationError(f"horizon must be finite; got {horizon!r}")
    if horizon < 0.0:
        raise ScopeViolationError(f"horizon must be >= 0; got {horizon!r}")
    _validate_rates(arrival_rate, service_rate)
    if initial_count >= threshold:
        return 1.0  # already at/above the (closed) boundary: tau=0 <= horizon trivially.

    Q = mm1_absorbing_generator(threshold, arrival_rate, service_rate)
    p0 = np.zeros(threshold + 1)
    p0[initial_count] = 1.0
    pT = p0 @ expm(Q * float(horizon))
    return float(pT[threshold])


def queue_hitting_probability_piecewise(
    initial_count: int, threshold: int, rate_segments: Sequence[Tuple[float, float, float]]
) -> float:
    """As :func:`queue_hitting_probability`, but for piecewise-constant rates:
    ``rate_segments`` is a sequence of ``(duration, arrival_rate, service_rate)``
    applied IN TIME ORDER. Matrix exponentials are multiplied sequentially --
    a generator averaged over the whole horizon is generally NOT the same
    evolution (matrix exponentials of different generators do not commute in
    general), so no shortcut of "average the rates first" is taken here.
    """
    initial_count = _validate_count_state(initial_count, "initial_count")
    threshold = _validate_count_state(threshold, "threshold")
    if len(rate_segments) == 0:
        raise ScopeViolationError("rate_segments must be non-empty")
    if initial_count >= threshold:
        return 1.0

    p = np.zeros(threshold + 1)
    p[initial_count] = 1.0
    for duration, arrival_rate, service_rate in rate_segments:
        if duration < 0.0:
            raise ScopeViolationError(f"segment duration must be >= 0; got {duration!r}")
        Q = mm1_absorbing_generator(threshold, arrival_rate, service_rate)
        p = p @ expm(Q * float(duration))
    return float(p[threshold])


@dataclass(frozen=True)
class SimulationResult:
    empirical_probability: float
    n_trials: int
    n_absorbed: int
    seed: int


def simulate_mm1_first_passage(
    initial_count: int, threshold: int, horizon: float, arrival_rate: float, service_rate: float,
    n_trials: int, seed: int,
) -> SimulationResult:
    """Event-driven (Gillespie-style) simulation of the SAME first-passage event,
    as an independent second implementation of the model (not a copy of the
    matrix-exponential code path). Fixed seed for reproducibility. At each rate
    change (there are none within a single call here; see the piecewise variant's
    own test) a fresh exponential clock would be redrawn -- within one constant-rate
    call, standard CTMC simulation (draw holding time ~Exp(total_rate), pick the
    next transition by relative rate) applies throughout.
    """
    if initial_count < 0 or threshold < 0 or n_trials <= 0:
        raise ScopeViolationError("invalid simulate_mm1_first_passage arguments")
    if horizon < 0.0:
        raise ScopeViolationError(f"horizon must be >= 0; got {horizon!r}")
    _validate_rates(arrival_rate, service_rate)
    rng = np.random.default_rng(seed)

    if initial_count >= threshold:
        return SimulationResult(1.0, n_trials, n_trials, seed)

    n_absorbed = 0
    for _ in range(n_trials):
        t = 0.0
        n = initial_count
        absorbed = False
        while t < horizon:
            rate_up = arrival_rate
            rate_down = service_rate if n > 0 else 0.0
            total_rate = rate_up + rate_down
            if total_rate <= 0.0:
                break  # no further transitions possible; will never reach threshold
            t += rng.exponential(1.0 / total_rate)
            if t > horizon:
                break
            if rng.uniform(0.0, total_rate) < rate_up:
                n += 1
            else:
                n -= 1
            if n >= threshold:
                absorbed = True
                break
        if absorbed:
            n_absorbed += 1
    return SimulationResult(n_absorbed / n_trials, n_trials, n_absorbed, seed)


__all__ = [
    "mm1_absorbing_generator", "queue_hitting_probability",
    "queue_hitting_probability_piecewise", "SimulationResult", "simulate_mm1_first_passage",
]
