"""H5: integrated buffer pilot -- K5's continuous case
(`docs/epistemic_buffer_pilot.md`; response to
`SCF_ASSUMPTION_EVIDENCE_IMPLEMENTATION_PLAN.md` §4.5-4.6).

Wires the H4 statewise-vs-uniform-feasibility distinction
(`epistemic/decisions.py`) together with the already existing,
independently verified two-buffer CBF-QP machinery
(`viability/coupled_buffer_cbf_qp.py`). No new safety or optimization
logic is added here -- this module only instantiates that existing
machinery for the exact K5 fiber and compares three declared
information modes.

Fiber: the same three states as K4's F(2)={(0,2),(1,1),(2,0)}. Dynamics
per buffer: x_dot_i = -1 + u_i, 0<=u_i<=1, shared budget u1+u2<=B,
horizon t in [0,1]. Because drain=1 and horizon=1 exactly here, the
plan's necessary-and-sufficient condition min{x_i(0), x_i(0)+u_i-1}>=0
coincides exactly with `sustained_safety_over_horizon`'s existing
closed-form min(x_i(0), x_i(0)+(u_i-drain)*horizon)>=0 -- this is a
special case of the existing formula, not a new one.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Sequence, Tuple

from scoped_correspondence.errors import ScopeViolationError
from scoped_correspondence.viability.coupled_buffer_cbf_qp import (
    BufferSpec,
    InterventionOutcome,
    solve_cbf_qp,
    sustained_safety_over_horizon,
)

DRAIN = 1.0
U_MIN = 0.0
U_MAX = 1.0
HORIZON = 1.0

#: The exact K4/K5 shared fiber F(2)={(0,2),(1,1),(2,0)}.
K5_FIBER_STATES: Tuple[Tuple[float, float], ...] = ((0.0, 2.0), (1.0, 1.0), (2.0, 0.0))


def buffer_pair_for_state(state: Tuple[float, float]) -> Tuple[BufferSpec, BufferSpec]:
    x1, x2 = state
    return (
        BufferSpec(drain=DRAIN, x=x1, u_min=U_MIN, u_max=U_MAX),
        BufferSpec(drain=DRAIN, x=x2, u_min=U_MIN, u_max=U_MAX),
    )


def statewise_minimal_intervention(state: Tuple[float, float], *, budget: float = 2.0, horizon: float = HORIZON) -> InterventionOutcome:
    """The CBF-QP-minimal intervention for ONE state, reusing `solve_cbf_qp` unchanged."""
    buffers = buffer_pair_for_state(state)
    return solve_cbf_qp(list(buffers), budget, horizon=horizon)


def minimal_uniform_intervention(
    states: Sequence[Tuple[float, float]] = K5_FIBER_STATES,
    *,
    drain: float = DRAIN,
    u_min: float = U_MIN,
    u_max: float = U_MAX,
) -> Tuple[float, ...]:
    """The smallest per-buffer-index `u=(u1,u2,...)` that is CBF-safe
    SIMULTANEOUSLY for every state in `states`, treating coordinate `i`
    as the same physical buffer across the whole fiber -- a genuinely
    shared, state-INDEPENDENT intervention, not a per-state optimum.

    Computed in closed form: for each buffer index, take the max over
    the fiber of that index's own CBF lower bound `drain - x_i`, clipped
    to `u_min` -- NOT via search. Raises if that requirement exceeds
    `u_max` for any buffer index (a genuinely uniform intervention is
    then impossible within the declared box bounds, independent of any
    shared budget)."""
    if len(states) == 0:
        raise ScopeViolationError("minimal_uniform_intervention requires a nonempty fiber")
    n = len(states[0])
    if any(len(s) != n for s in states):
        raise ScopeViolationError("every state in the fiber must have the same dimension")
    required = []
    for i in range(n):
        lo = max(float(u_min), max(float(drain) - float(s[i]) for s in states))
        if lo > float(u_max) + 1e-9:
            raise ScopeViolationError(
                f"buffer index {i}: a uniform intervention would need u >= {lo:.6g}, "
                f"exceeding u_max={u_max:.6g} for at least one state in the fiber"
            )
        required.append(lo)
    return tuple(required)


def sign_based_policy(state: Tuple[float, float]) -> Tuple[float, float]:
    """Mode B: a state-dependent policy that only needs sign(x1-x2), not
    the full state, before intervening."""
    x1, x2 = state
    if x1 < x2:
        return (1.0, 0.0)
    if x1 > x2:
        return (0.0, 1.0)
    return (0.0, 0.0)


@dataclass(frozen=True)
class InformationModeResult:
    mode: str
    description: str
    per_state_u: Tuple[Tuple[Tuple[float, float], Tuple[float, ...]], ...]
    per_state_sustained_safe: Tuple[bool, ...]
    worst_case_cost: float


def evaluate_information_modes(
    states: Sequence[Tuple[float, float]] = K5_FIBER_STATES, *, horizon: float = HORIZON,
) -> Dict[str, InformationModeResult]:
    """The three information modes of `docs/epistemic_buffer_pilot.md`:
    A) no observation, one shared intervention for the whole fiber;
    B) observe sign(x1-x2) before intervening, choose accordingly;
    C) observe the full state, statewise CBF-QP-optimal per state.

    A only needs `minimal_uniform_intervention`; B and C are cross-
    checked against `sustained_safety_over_horizon` state by state, the
    same existing function used throughout `viability.coupled_buffer_cbf_qp`.
    """
    results: Dict[str, InformationModeResult] = {}

    u_uniform = minimal_uniform_intervention(states)
    per_state_a, safe_a = [], []
    for s in states:
        buffers = buffer_pair_for_state(s)
        ok, _ = sustained_safety_over_horizon(list(buffers), list(u_uniform), horizon)
        per_state_a.append((s, u_uniform))
        safe_a.append(ok)
    results["A_no_observation_uniform"] = InformationModeResult(
        mode="A_no_observation_uniform",
        description="one shared u for the whole fiber, no observation before intervening",
        per_state_u=tuple(per_state_a), per_state_sustained_safe=tuple(safe_a),
        worst_case_cost=sum(u_uniform),
    )

    per_state_b, safe_b, costs_b = [], [], []
    for s in states:
        u = sign_based_policy(s)
        buffers = buffer_pair_for_state(s)
        ok, _ = sustained_safety_over_horizon(list(buffers), list(u), horizon)
        per_state_b.append((s, u))
        safe_b.append(ok)
        costs_b.append(sum(u))
    results["B_sign_of_difference"] = InformationModeResult(
        mode="B_sign_of_difference",
        description="observe sign(x1-x2) before intervening, choose a state-dependent u accordingly",
        per_state_u=tuple(per_state_b), per_state_sustained_safe=tuple(safe_b),
        worst_case_cost=max(costs_b),
    )

    per_state_c, safe_c, costs_c = [], [], []
    for s in states:
        outcome = statewise_minimal_intervention(s, budget=2.0, horizon=horizon)
        per_state_c.append((s, outcome.u))
        safe_c.append(bool(outcome.sustained_safe_until_horizon))
        costs_c.append(sum(outcome.u))
    results["C_full_state_statewise"] = InformationModeResult(
        mode="C_full_state_statewise",
        description="full state x observed, statewise CBF-QP-optimal u per state",
        per_state_u=tuple(per_state_c), per_state_sustained_safe=tuple(safe_c),
        worst_case_cost=max(costs_c),
    )
    return results


__all__ = [
    "DRAIN", "U_MIN", "U_MAX", "HORIZON", "K5_FIBER_STATES",
    "InformationModeResult",
    "buffer_pair_for_state", "statewise_minimal_intervention", "minimal_uniform_intervention",
    "sign_based_policy", "evaluate_information_modes",
]
