"""Epistemic layer (H0-H7): assumption/evidence auditing for SCF.

Content basis: `prompts/Answers/nicht_stationäre_Treiber/
SCF_ASSUMPTION_EVIDENCE_IMPLEMENTATION_PLAN.md` and `docs/epistemic_scope.md`
(H0 result-vocabulary register). "Epistemic" is the technical name for
this assumption/knowledge-auditing layer, not a new physical layer.

This subpackage is additive: it does not modify any existing SCF module.
See `EPISTEMIC_AUDIT_ROADMAP.md` for package status.
"""
from __future__ import annotations

from .decisions import ActionSetReport, DecisionReport, compare_decisions, uniform_safe_actions
from .finite import audit_finite_claim
from .observation_fibers import (
    FiberReport,
    IdentifiedSetReport,
    MacroObservabilityReport,
    identified_values,
    macro_dynamics_and_observability,
    observation_fiber,
)
from .records import AssumptionSpec, ClaimReport, ClaimSpec, FiniteDomainSpec
from .supports import (
    DeletionStep,
    InconsistentCoreReport,
    SupportReport,
    find_minimal_inconsistent_core,
    find_minimal_support,
)

__all__ = [
    "ActionSetReport",
    "AssumptionSpec",
    "ClaimReport",
    "ClaimSpec",
    "DecisionReport",
    "DeletionStep",
    "FiberReport",
    "FiniteDomainSpec",
    "IdentifiedSetReport",
    "InconsistentCoreReport",
    "MacroObservabilityReport",
    "SupportReport",
    "audit_finite_claim",
    "compare_decisions",
    "find_minimal_inconsistent_core",
    "find_minimal_support",
    "identified_values",
    "macro_dynamics_and_observability",
    "observation_fiber",
    "uniform_safe_actions",
]
