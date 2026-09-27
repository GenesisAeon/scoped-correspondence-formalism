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
from typing import Any, Callable, Dict, Sequence, Tuple

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


def _worst_case_uniform_cost_by_group(
    states: Sequence[Tuple[float, float]], key_fn: Callable[[Tuple[float, float]], Any], horizon: float,
) -> Tuple[Tuple[Tuple[Tuple[float, float], Tuple[float, ...]], ...], Tuple[bool, ...], float]:
    """Partition `states` by `key_fn` (the additional observation beyond
    the sum that already defines the fiber), then compute the minimal
    UNIFORM intervention WITHIN each group (states sharing the same
    observed key still need one shared action, since the key alone
    doesn't distinguish them further) -- Plan §12's "sum+minimum" mode:
    observing `min(x1,x2)` fully resolves the (1,1) group (cost 0) but
    leaves {(0,2),(2,0)} indistinguishable at m=0, which STILL needs the
    full uniform budget of 2 there."""
    groups: Dict[Any, list] = {}
    for s in states:
        groups.setdefault(key_fn(s), []).append(s)
    per_state = []
    safe = []
    worst = 0.0
    for group_states in groups.values():
        u_group = minimal_uniform_intervention(tuple(group_states))
        worst = max(worst, sum(u_group))
        for s in group_states:
            buffers = buffer_pair_for_state(s)
            ok, _ = sustained_safety_over_horizon(list(buffers), list(u_group), horizon)
            per_state.append((s, u_group))
            safe.append(ok)
    return tuple(per_state), tuple(safe), worst


def evaluate_information_modes(
    states: Sequence[Tuple[float, float]] = K5_FIBER_STATES, *, horizon: float = HORIZON,
) -> Dict[str, InformationModeResult]:
    """Plan §12's three information modes (Followup-Review-Fix
    SCF_REVIEW_H0_H7_9dde420.md R8a -- the plan asks for sum / sum+minimum
    / sum+sign, not sum / sign / full-state):

    A) sum only (already being on this fiber) -- one shared intervention
       for the whole fiber, no further observation;
    B) sum + minimum: observing `min(x1,x2)` before intervening fully
       resolves the (1,1) state (cost 0), but at `min=0` the two states
       {(0,2),(2,0)} remain indistinguishable -- a jointly safe
       intervention there STILL needs the full uniform budget of 2, so
       this mode's WORST CASE does not improve on mode A;
    C) sum + sign(x1-x2): a strictly finer observation that resolves all
       three states, dropping the worst case to 1.

    D) is an OPTIONAL extra comparison (full state observed, statewise
       CBF-QP-optimal per state) -- kept because it demonstrates the
       reachable optimum, not because the plan requires it.
    """
    results: Dict[str, InformationModeResult] = {}

    u_uniform = minimal_uniform_intervention(states)
    per_state_a, safe_a = [], []
    for s in states:
        buffers = buffer_pair_for_state(s)
        ok, _ = sustained_safety_over_horizon(list(buffers), list(u_uniform), horizon)
        per_state_a.append((s, u_uniform))
        safe_a.append(ok)
    results["A_sum_only"] = InformationModeResult(
        mode="A_sum_only",
        description="one shared u for the whole (sum-defined) fiber, no further observation before intervening",
        per_state_u=tuple(per_state_a), per_state_sustained_safe=tuple(safe_a),
        worst_case_cost=sum(u_uniform),
    )

    per_state_b, safe_b, worst_b = _worst_case_uniform_cost_by_group(states, lambda s: min(s[0], s[1]), horizon)
    results["B_sum_and_minimum"] = InformationModeResult(
        mode="B_sum_and_minimum",
        description="observe min(x1,x2) before intervening; resolves (1,1) but NOT {(0,2),(2,0)} at min=0, "
                     "which still needs a full budget-2 uniform intervention within that group",
        per_state_u=per_state_b, per_state_sustained_safe=safe_b,
        worst_case_cost=worst_b,
    )

    per_state_c, safe_c, costs_c = [], [], []
    for s in states:
        u = sign_based_policy(s)
        buffers = buffer_pair_for_state(s)
        ok, _ = sustained_safety_over_horizon(list(buffers), list(u), horizon)
        per_state_c.append((s, u))
        safe_c.append(ok)
        costs_c.append(sum(u))
    results["C_sum_and_sign"] = InformationModeResult(
        mode="C_sum_and_sign",
        description="observe sign(x1-x2) before intervening, choose a state-dependent u accordingly",
        per_state_u=tuple(per_state_c), per_state_sustained_safe=tuple(safe_c),
        worst_case_cost=max(costs_c),
    )

    per_state_d, safe_d, costs_d = [], [], []
    for s in states:
        outcome = statewise_minimal_intervention(s, budget=2.0, horizon=horizon)
        per_state_d.append((s, outcome.u))
        safe_d.append(bool(outcome.sustained_safe_until_horizon))
        costs_d.append(sum(outcome.u))
    results["D_full_state_statewise_optional_extra"] = InformationModeResult(
        mode="D_full_state_statewise_optional_extra",
        description="OPTIONAL extra comparison (not required by the plan): full state x observed, "
                     "statewise CBF-QP-optimal u per state",
        per_state_u=tuple(per_state_d), per_state_sustained_safe=tuple(safe_d),
        worst_case_cost=max(costs_d),
    )
    return results


__all__ = [
    "DRAIN", "U_MIN", "U_MAX", "HORIZON", "K5_FIBER_STATES",
    "InformationModeResult",
    "buffer_pair_for_state", "statewise_minimal_intervention", "minimal_uniform_intervention",
    "sign_based_policy", "evaluate_information_modes",
]
