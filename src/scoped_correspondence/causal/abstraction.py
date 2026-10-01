"""Exact interventional abstraction between finite SCMs (Paket J9, plan §15.2).

For a micro model, a macro model, a state map tau and a DECLARED
intervention map omega (micro intervention -> macro intervention), checks
for EVERY declared micro intervention i:

    tau_# P_micro^{do(i)} = P_macro^{do(omega(i))}

and, as SEPARATE properties of the chosen exact transformation (Rubenstein
et al. 2017, S14, Definition 3): omega is surjective onto the declared macro
intervention set and order-preserving, where i <= j iff j extends i (j sets
every variable i sets, to the same value). This is equality of
INTERVENTIONAL distributions; it does not imply equality of counterfactual
couplings. A failing declared omega says nothing about other omegas.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
from typing import Any, Callable, Dict, List, Mapping, Optional, Sequence, Tuple

from scoped_correspondence.causal.finite_scm import (
    Assignment,
    BudgetExceeded,
    FiniteSCM,
    interventional_distribution,
    pushforward_distribution,
    total_variation,
)
from scoped_correspondence.errors import ScopeViolationError

Intervention = Tuple[Tuple[str, Any], ...]  # sorted (var, value) pairs; () = no intervention


def iv(**kw) -> Intervention:
    return tuple(sorted(kw.items()))


def extends(i: Intervention, j: Intervention) -> bool:
    """i <= j: j sets every variable that i sets, to the same value."""
    dj = dict(j)
    return all(k in dj and dj[k] == v for k, v in i)


@dataclass(frozen=True)
class InterventionCheck:
    micro: Intervention
    macro: Intervention
    total_variation: Fraction
    match: bool


@dataclass(frozen=True)
class AbstractionReport:
    status: str  # "completed" | "budget_exhausted" | "invalid_input"
    exact_abstraction: Optional[bool]
    distributions_match: Optional[bool]
    surjective: Optional[bool]
    order_preserving: Optional[bool]
    checks: Tuple[InterventionCheck, ...]
    order_violations: Tuple[Tuple[Intervention, Intervention], ...]
    unreached_macro: Tuple[Intervention, ...]
    comparison: str  # "exact" (Fractions) | "numeric_tolerance"
    intervention_scope: Tuple[Intervention, ...]
    notes: Tuple[str, ...] = field(default_factory=tuple)


def check_interventional_abstraction(
    micro: FiniteSCM, macro: FiniteSCM, tau: Callable[[Assignment], Assignment],
    omega: Sequence[Tuple[Intervention, Intervention]], macro_interventions: Sequence[Intervention],
    *, budget: int = 100_000, tol: Optional[float] = None,
) -> AbstractionReport:
    """``omega`` lists (micro, macro) pairs: the declared micro intervention set is
    exactly its first components. ``tol=None`` compares exactly (Fractions);
    a numeric tolerance is reported as such."""
    micro_set = [m for m, _ in omega]
    if len(set(micro_set)) != len(micro_set):
        raise ScopeViolationError("omega maps a micro intervention twice")
    if any(M not in macro_interventions for _, M in omega):
        raise ScopeViolationError("omega maps onto an intervention outside the declared macro set")
    scope = tuple(micro_set)
    checks: List[InterventionCheck] = []
    used = 0
    try:
        for m, M in omega:
            used += len(micro.exogenous_distribution) + len(macro.exogenous_distribution)
            if used > budget:
                raise BudgetExceeded("abstraction check exceeded its budget")
            pm = pushforward_distribution(interventional_distribution(micro, dict(m), budget=budget), tau)
            pM = interventional_distribution(macro, dict(M), budget=budget)
            d = total_variation(pm, pM)
            ok = d == 0 if tol is None else float(d) <= tol
            checks.append(InterventionCheck(m, M, d, ok))
    except BudgetExceeded as exc:
        return AbstractionReport("budget_exhausted", None, None, None, None, tuple(checks), (), (),
                                 "exact" if tol is None else "numeric_tolerance", scope,
                                 (str(exc), "a budget stop decides nothing about the remaining interventions"))
    surj_missing = tuple(M for M in macro_interventions if M not in {M2 for _, M2 in omega})
    violations = tuple((a, b) for a, _ in omega for b, _ in omega
                       if a != b and extends(a, b) and not extends(dict(omega)[a], dict(omega)[b]))
    dist_ok = all(c.match for c in checks)
    notes = ["equality of interventional distributions only; no counterfactual identity",
             "a failure of THIS declared omega says nothing about other intervention maps"]
    if tol is not None:
        notes.append(f"numeric comparison with tolerance {tol}: not an exact equality proof")
    return AbstractionReport("completed", dist_ok and not surj_missing and not violations, dist_ok, not surj_missing,
                             not violations, tuple(checks), violations, surj_missing,
                             "exact" if tol is None else "numeric_tolerance", scope, tuple(notes))


__all__ = ["Intervention", "iv", "extends", "InterventionCheck", "AbstractionReport", "check_interventional_abstraction"]
