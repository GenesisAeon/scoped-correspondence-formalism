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


@dataclass(frozen=True)
class InterventionOutcome:
    label: str
    u: Optional[Tuple[float, float]]
    margins: Optional[Tuple[float, float]]
    safe: bool
    admissible: bool
    cost: Optional[float]
    infeasible_problem: bool
    infeasibility_reason: Optional[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "label": self.label,
            "u": list(self.u) if self.u is not None else None,
            "margins": list(self.margins) if self.margins is not None else None,
            "safe": self.safe,
            "admissible": self.admissible,
            "cost": self.cost,
            "infeasible_problem": self.infeasible_problem,
            "infeasibility_reason": self.infeasibility_reason,
        }


def _effective_lower_bounds(buffers: Sequence[BufferSpec]) -> Tuple[float, ...]:
    return tuple(max(float(b.u_min), cbf_lower_bound(b)) for b in buffers)


def _cost(u: Sequence[float]) -> float:
    return float(sum(uu * uu for uu in u))


def evaluate_fixed_control(
    buffers: Sequence[BufferSpec], u: Sequence[float], budget: float, label: str
) -> InterventionOutcome:
    """Evaluate ANY given control vector (used for both the no-intervention and fixed-rule variants)."""
    if len(buffers) != len(u):
        raise ScopeViolationError("evaluate_fixed_control: buffers and u must have the same length")
    margins = tuple(cbf_margin(b, uu) for b, uu in zip(buffers, u))
    safe = all(m >= -1e-9 for m in margins)
    within_box = all(float(b.u_min) - 1e-9 <= uu <= float(b.u_max) + 1e-9 for b, uu in zip(buffers, u))
    within_budget = sum(u) <= float(budget) + 1e-9
    admissible = within_box and within_budget
    return InterventionOutcome(
        label=label, u=tuple(float(uu) for uu in u), margins=margins, safe=safe, admissible=admissible,
        cost=_cost(u), infeasible_problem=False, infeasibility_reason=None,
    )


def solve_cbf_qp(buffers: Sequence[BufferSpec], budget: float) -> InterventionOutcome:
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
                label=OPTIMIZED_QP, u=None, margins=None, safe=False, admissible=False, cost=None,
                infeasible_problem=True,
                infeasibility_reason=(
                    f"buffer {i}: CBF requires u >= {lo:.6g}, but u_max={b.u_max:.6g} -- "
                    "infeasible from this buffer's own bounds alone, independent of the shared budget"
                ),
            )
    total_lower = sum(lowers)
    if total_lower > float(budget) + 1e-9:
        return InterventionOutcome(
            label=OPTIMIZED_QP, u=None, margins=None, safe=False, admissible=False, cost=None,
            infeasible_problem=True,
            infeasibility_reason=(
                f"sum of per-buffer CBF-minimal controls ({total_lower:.6g}) exceeds the shared "
                f"budget ({float(budget):.6g}) -- the resource itself is insufficient, not a solver failure"
            ),
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
    return InterventionOutcome(
        label=OPTIMIZED_QP, u=u_star, margins=margins,
        safe=all(m >= -1e-6 for m in margins),
        admissible=True, cost=solver_cost, infeasible_problem=False, infeasibility_reason=None,
    )


def compare_intervention_strategies(buffers: Sequence[BufferSpec], budget: float) -> Dict[str, InterventionOutcome]:
    """No intervention (u=0) vs. fixed rule (u_i = drain_i) vs. CBF-QP-optimized, same buffers/budget."""
    if len(buffers) != 2:
        raise ScopeViolationError(f"compare_intervention_strategies: exactly 2 buffers supported; got {len(buffers)}")
    no_int = evaluate_fixed_control(buffers, (0.0, 0.0), budget, NO_INTERVENTION)
    fixed = evaluate_fixed_control(buffers, tuple(float(b.drain) for b in buffers), budget, FIXED_RULE)
    optimized = solve_cbf_qp(buffers, budget)
    return {NO_INTERVENTION: no_int, FIXED_RULE: fixed, OPTIMIZED_QP: optimized}


__all__ = [
    "SOURCE", "NO_INTERVENTION", "FIXED_RULE", "OPTIMIZED_QP",
    "BufferSpec", "InterventionOutcome",
    "cbf_margin", "cbf_lower_bound",
    "evaluate_fixed_control", "solve_cbf_qp", "compare_intervention_strategies",
]
