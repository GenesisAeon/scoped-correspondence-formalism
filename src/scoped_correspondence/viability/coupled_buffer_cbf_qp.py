"""From safety maps to bounded interventions: a two-buffer Control-Barrier-Function QP (Milestone 59).

CAPABILITY_EXPANSION_ROADMAP.md Priority 5, response to Astra's 2026-09-24
capability assessment: "Aus dem bestehenden skalaren Kontrollbarrieren-
Beispiel könnte ein Modell mit zwei gekoppelten Puffern, begrenzten
Stellgrößen und gemeinsamem Ressourcenbudget entstehen." Extends
``viability.control_barrier``'s scalar identity-barrier worked example
(``h(x)=x``, ``alpha(r)=r``, ``x_dot=u``) to TWO buffers with:

- a constant drain per buffer (``x_dot_i = -drain_i + u_i``, still
  control-affine, same relative-degree-one structure as the M16 module),
- a bounded control per buffer (``u_min_i <= u_i <= u_max_i``),
- a SHARED resource budget (``u_1 + u_2 <= budget``) — a single limited
  intervention capacity split between the two buffers, Astra's requested
  coupling.

The leading question this module answers, per Astra: **"Welcher zulässige
Eingriff verhindert eine Grenzverletzung — und wann reichen die
verfügbaren Mittel grundsätzlich nicht aus?"** Three variants are
compared on EVERY worked example — no intervention, a naive fixed rule
(replace exactly the drain), and the CBF-QP-optimized minimal-cost
intervention — reporting boundary violation, cost, and admissibility
(box bounds + shared budget) for each, with **infeasibility of the
optimization problem itself surfaced explicitly**, not silently
approximated or hidden behind a solver's generic failure message: the
closed-form per-buffer lower bound derived directly from the CBF
inequality is used as an INDEPENDENT feasibility certificate, not just
trusted from ``scipy``'s convergence flag.

**Correction (2026-09-24, response to
prompts/Answers/nicht_stationäre_Treiber/SCF_Review_dc5d82a.md, Astra
finding R4): instantaneous CBF satisfaction is NOT trajectory safety.**
The CBF margin ``-drain+u+x >= 0`` is a check of the inequality AT ONE
INSTANT — exactly the same caveat already documented for the scalar M16
example this module extends (``control_barrier.verify_forward_invariance``:
"a single passing instantaneous check does NOT by itself certify forward
invariance under a *held* ... control over time"), which this module
failed to carry forward into its own field naming and worked example.
Astra's concrete counterexample: the optimized ``u=(2,0)`` for buffer 1
(``drain=3, x=1``) satisfies the instantaneous margin exactly (``=0``),
but HOLDING that control constant gives the exact linear trajectory
``x1(t) = 1 - t``, which goes negative for any ``t > 1``. Worse, her
second calculation shows sustained safety is not even a question of
control-law sophistication here: with total drain ``5`` and budget ``3``,
``x1(t)+x2(t) <= 6 - 2t`` under ANY admissible allocation, so at least one
buffer is provably negative for ``t > 3`` regardless of how the budget is
split or re-split over time — the RESOURCE itself is insufficient for
sustained safety, a structurally different question from the instantaneous
QP's feasibility.

Every ``InterventionOutcome`` therefore now separates the two questions
explicitly: ``cbf_condition_satisfied_now`` (the original instantaneous
check, renamed from ``safe`` to make the scope unmistakable) and, when a
``horizon`` is supplied, ``sustained_safe_until_horizon`` /
``first_violation_time`` — computed from the EXACT closed-form trajectory
under the constant held control (``x_i(t) = x_i(0) + (u_i-drain_i)*t``,
linear, no numerical integration needed). A second worked example with a
budget that genuinely covers total drain is included specifically to make
the instantaneous-vs-sustained distinction demonstrable (Astra: "Soll
dauerhafte Sicherheit demonstriert werden, muss das Beispiel dafür
überhaupt genügend langfristige Ressourcen besitzen.") — the module does
NOT claim this "solves" sustained safety in general (a real closed-loop
controller would re-optimize as the state evolves, which this module still
does not simulate).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Sequence, Tuple

import numpy as np
from scipy.optimize import minimize

from scoped_correspondence.errors import ScopeViolationError

SOURCE = (
    "Ames, A. D.; Xu, X.; Grizzle, J. W.; Tabuada, P. (2017): Control "
    "Barrier Function Based Quadratic Programs for Safety Critical "
    "Systems. IEEE TAC 62, 3861-3876, DOI 10.1109/TAC.2016.2638961."
)

NO_INTERVENTION = "no_intervention"
FIXED_RULE = "fixed_rule"
OPTIMIZED_QP = "optimized_qp"


@dataclass(frozen=True)
class BufferSpec:
    """One buffer: ``x_dot = -drain + u``, identity CBF ``h(x)=x``, ``alpha(r)=r``
    (same barrier/class-K choice as ``viability.control_barrier``'s scalar M16 example).
    """
    drain: float
    x: float
    u_min: float
    u_max: float

    def __post_init__(self) -> None:
        if not (float(self.u_min) <= float(self.u_max)):
            raise ScopeViolationError(f"BufferSpec: u_min ({self.u_min}) must be <= u_max ({self.u_max})")


def cbf_margin(spec: BufferSpec, u: float) -> float:
    """``-drain + u + x`` — the M16-style CBF margin; safe iff ``>= 0``."""
    return float(-float(spec.drain) + float(u) + float(spec.x))


def cbf_lower_bound(spec: BufferSpec) -> float:
    """Minimal ``u`` satisfying the CBF inequality alone (ignoring box/budget): ``u >= drain - x``."""
    return float(spec.drain) - float(spec.x)


def held_control_violation_time(spec: BufferSpec, u: float) -> Optional[float]:
    """Exact time at which ``x(t) = x0 + (u-drain)*t`` first goes negative under a
    HELD (constant) control ``u`` — the closed-form solution of the linear buffer
    dynamics, no numerical integration needed. Returns ``None`` if it never does
    (``u >= drain``, i.e. the buffer is non-decreasing under this held control, AND
    it does not already start negative).

    **Correction (2026-09-24, response to Astra6.txt, finding 2a):** an already-
    negative starting state (``x0 < 0``) is checked FIRST, regardless of
    ``net_rate`` — the previous version checked ``net_rate >= 0`` first and
    returned ``None`` (never violates) even when the buffer was already unsafe
    at ``t=0``, silently hiding an already-existing violation whenever the
    control happened to be non-decreasing.
    """
    if float(spec.x) < 0.0:
        return 0.0
    net_rate = float(u) - float(spec.drain)
    if net_rate >= 0.0:
        return None
    return float(spec.x) / (-net_rate)


def sustained_safety_over_horizon(
    buffers: Sequence[BufferSpec], u: Sequence[float], horizon: float
) -> Tuple[bool, Optional[float]]:
    """Whether EVERY buffer stays non-negative for the full CLOSED interval
    ``[0, horizon]`` under the HELD control ``u``, and the earliest violation
    time across buffers if not (``None`` if none violate).

    **Correction (2026-09-24, response to Astra6.txt, finding 2b):** safety
    itself is now decided by Astra's exact reformulation for a held
    (piecewise-linear, monotonic) control: ``min(x0, x0 + (u-drain)*horizon)
    >= 0`` — the minimum of a linear function over a closed interval is
    always at one of its two endpoints, so this is exact and sidesteps the
    previous version's boundary bug, which used ``violation_time <= horizon``
    and therefore misclassified a trajectory that reaches EXACTLY zero AT the
    horizon (touching the boundary, not violating it) as unsafe.
    ``held_control_violation_time`` is still used, but only to report WHEN a
    genuine violation happens once one has already been established.
    """
    if len(buffers) != len(u):
        raise ScopeViolationError("sustained_safety_over_horizon: buffers and u must have the same length")
    if horizon <= 0.0:
        raise ScopeViolationError(f"sustained_safety_over_horizon: horizon must be > 0; got {horizon!r}")
    mins = [
        min(float(b.x), float(b.x) + (float(uu) - float(b.drain)) * float(horizon))
        for b, uu in zip(buffers, u)
    ]
    if all(m >= -1e-9 for m in mins):
        return True, None
    violation_times = [held_control_violation_time(b, uu) for b, uu in zip(buffers, u)]
    within_horizon = [vt for vt in violation_times if vt is not None and vt <= float(horizon) + 1e-9]
    return False, (min(within_horizon) if within_horizon else 0.0)


@dataclass(frozen=True)
class InterventionOutcome:
    label: str
    u: Optional[Tuple[float, float]]
    margins: Optional[Tuple[float, float]]
    cbf_condition_satisfied_now: bool
    admissible: bool
    cost: Optional[float]
    infeasible_problem: bool
    infeasibility_reason: Optional[str]
    horizon: Optional[float] = None
    sustained_safe_until_horizon: Optional[bool] = None
    first_violation_time: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "label": self.label,
            "u": list(self.u) if self.u is not None else None,
            "margins": list(self.margins) if self.margins is not None else None,
            "cbf_condition_satisfied_now": self.cbf_condition_satisfied_now,
            "admissible": self.admissible,
            "cost": self.cost,
            "infeasible_problem": self.infeasible_problem,
            "infeasibility_reason": self.infeasibility_reason,
            "horizon": self.horizon,
            "sustained_safe_until_horizon": self.sustained_safe_until_horizon,
            "first_violation_time": self.first_violation_time,
        }


def _effective_lower_bounds(buffers: Sequence[BufferSpec]) -> Tuple[float, ...]:
    return tuple(max(float(b.u_min), cbf_lower_bound(b)) for b in buffers)


def _cost(u: Sequence[float]) -> float:
    return float(sum(uu * uu for uu in u))


def evaluate_fixed_control(
    buffers: Sequence[BufferSpec], u: Sequence[float], budget: float, label: str, *, horizon: Optional[float] = None
) -> InterventionOutcome:
    """Evaluate ANY given control vector (used for both the no-intervention and fixed-rule variants).

    ``horizon``, if given, additionally checks sustained safety under this
    control HELD CONSTANT over ``[0, horizon]`` (see module docstring,
    Astra finding R4) — a strictly stronger, separate question from the
    instantaneous ``cbf_condition_satisfied_now``.
    """
    if len(buffers) != len(u):
        raise ScopeViolationError("evaluate_fixed_control: buffers and u must have the same length")
    margins = tuple(cbf_margin(b, uu) for b, uu in zip(buffers, u))
    cbf_now = all(m >= -1e-9 for m in margins)
    within_box = all(float(b.u_min) - 1e-9 <= uu <= float(b.u_max) + 1e-9 for b, uu in zip(buffers, u))
    within_budget = sum(u) <= float(budget) + 1e-9
    admissible = within_box and within_budget
    sustained: Optional[bool] = None
    first_violation: Optional[float] = None
    if horizon is not None:
        sustained, first_violation = sustained_safety_over_horizon(buffers, u, horizon)
    return InterventionOutcome(
        label=label, u=tuple(float(uu) for uu in u), margins=margins, cbf_condition_satisfied_now=cbf_now,
        admissible=admissible, cost=_cost(u), infeasible_problem=False, infeasibility_reason=None,
        horizon=horizon, sustained_safe_until_horizon=sustained, first_violation_time=first_violation,
    )


def solve_cbf_qp(buffers: Sequence[BufferSpec], budget: float, *, horizon: Optional[float] = None) -> InterventionOutcome:
    """Minimal-cost (``sum u_i^2``) intervention satisfying every buffer's CBF condition,
    each buffer's own box bounds, and the shared budget ``sum(u_i) <= budget``.

    Feasibility is decided FIRST by an independent closed-form argument (not by
    trusting the QP solver's convergence flag): each buffer's CBF condition
    folds into a per-buffer lower bound ``max(u_min_i, drain_i - x_i)``; if
    that already exceeds ``u_max_i`` for some buffer, no control satisfies
    that buffer's own CBF within its own bounds regardless of budget. If all
    per-buffer lower bounds are individually admissible but their SUM exceeds
    the shared budget, the shared resource is provably insufficient — Astra's
    "wann reichen die verfügbaren Mittel grundsätzlich nicht aus". Only in the
    remaining (provably feasible) case is ``scipy.optimize.minimize`` (SLSQP)
    invoked, starting from the closed-form point (which is itself already the
    analytic optimum for a monotonically increasing cost in ``u`` above its
    lower bound with a non-binding or exactly-binding budget) as a check that
    the general-purpose QP solve agrees with the closed form.
    """
    if len(buffers) != 2:
        raise ScopeViolationError(f"solve_cbf_qp: exactly 2 buffers supported; got {len(buffers)}")
    lowers = _effective_lower_bounds(buffers)
    for i, (b, lo) in enumerate(zip(buffers, lowers)):
        if lo > float(b.u_max) + 1e-9:
            return InterventionOutcome(
                label=OPTIMIZED_QP, u=None, margins=None, cbf_condition_satisfied_now=False, admissible=False, cost=None,
                infeasible_problem=True,
                infeasibility_reason=(
                    f"buffer {i}: CBF requires u >= {lo:.6g}, but u_max={b.u_max:.6g} -- "
                    "infeasible from this buffer's own bounds alone, independent of the shared budget"
                ),
                horizon=horizon,
            )
    total_lower = sum(lowers)
    if total_lower > float(budget) + 1e-9:
        return InterventionOutcome(
            label=OPTIMIZED_QP, u=None, margins=None, cbf_condition_satisfied_now=False, admissible=False, cost=None,
            infeasible_problem=True,
            infeasibility_reason=(
                f"sum of per-buffer CBF-minimal controls ({total_lower:.6g}) exceeds the shared "
                f"budget ({float(budget):.6g}) -- the resource itself is insufficient, not a solver failure"
            ),
            horizon=horizon,
        )

    x0 = np.array(lowers, dtype=float)
    bounds = [(float(b.u_min), float(b.u_max)) for b in buffers]
    # CBF folded directly into the lower end of `bounds` via `lowers`, replacing box lower bound
    # with the (possibly tighter) CBF-derived one, per buffer:
    bounds = [(lo, float(b.u_max)) for lo, b in zip(lowers, buffers)]
    constraints = [{"type": "ineq", "fun": lambda u: float(budget) - float(u[0]) - float(u[1])}]

    res = minimize(lambda u: _cost(u), x0=x0, method="SLSQP", bounds=bounds, constraints=constraints)
    if not res.success:
        raise ScopeViolationError(
            f"solve_cbf_qp: SLSQP failed to converge on a problem the closed-form check found "
            f"feasible: {res.message}"
        )
    u_star = tuple(float(v) for v in res.x)
    closed_form_cost = _cost(lowers)
    solver_cost = float(res.fun)
    if solver_cost > closed_form_cost + 1e-6:
        raise ScopeViolationError(
            f"solve_cbf_qp: SLSQP solution (cost={solver_cost}) is worse than the independently "
            f"derived closed-form optimum (cost={closed_form_cost}) -- solver did not find the "
            "true minimum"
        )
    margins = tuple(cbf_margin(b, uu) for b, uu in zip(buffers, u_star))
    sustained: Optional[bool] = None
    first_violation: Optional[float] = None
    if horizon is not None:
        sustained, first_violation = sustained_safety_over_horizon(buffers, u_star, horizon)
    return InterventionOutcome(
        label=OPTIMIZED_QP, u=u_star, margins=margins,
        cbf_condition_satisfied_now=all(m >= -1e-6 for m in margins),
        admissible=True, cost=solver_cost, infeasible_problem=False, infeasibility_reason=None,
        horizon=horizon, sustained_safe_until_horizon=sustained, first_violation_time=first_violation,
    )


def compare_intervention_strategies(
    buffers: Sequence[BufferSpec], budget: float, *, horizon: Optional[float] = None
) -> Dict[str, InterventionOutcome]:
    """No intervention (u=0) vs. fixed rule (u_i = drain_i) vs. CBF-QP-optimized, same buffers/budget.

    ``horizon``, if given, additionally reports sustained safety under each
    strategy's control HELD CONSTANT over ``[0, horizon]`` — see module
    docstring, Astra finding R4, for why this is a separate question from
    instantaneous CBF satisfaction.
    """
    if len(buffers) != 2:
        raise ScopeViolationError(f"compare_intervention_strategies: exactly 2 buffers supported; got {len(buffers)}")
    no_int = evaluate_fixed_control(buffers, (0.0, 0.0), budget, NO_INTERVENTION, horizon=horizon)
    fixed = evaluate_fixed_control(buffers, tuple(float(b.drain) for b in buffers), budget, FIXED_RULE, horizon=horizon)
    optimized = solve_cbf_qp(buffers, budget, horizon=horizon)
    return {NO_INTERVENTION: no_int, FIXED_RULE: fixed, OPTIMIZED_QP: optimized}


__all__ = [
    "SOURCE", "NO_INTERVENTION", "FIXED_RULE", "OPTIMIZED_QP",
    "BufferSpec", "InterventionOutcome",
    "cbf_margin", "cbf_lower_bound", "held_control_violation_time", "sustained_safety_over_horizon",
    "evaluate_fixed_control", "solve_cbf_qp", "compare_intervention_strategies",
]
