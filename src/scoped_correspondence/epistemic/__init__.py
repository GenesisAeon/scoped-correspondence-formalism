"""Epistemic layer (H0-H7): assumption/evidence auditing for SCF.

Content basis: `prompts/Answers/nicht_stationäre_Treiber/
SCF_ASSUMPTION_EVIDENCE_IMPLEMENTATION_PLAN.md` and `docs/epistemic_scope.md`
(H0 result-vocabulary register). "Epistemic" is the technical name for
this assumption/knowledge-auditing layer, not a new physical layer.

This subpackage is additive: it does not modify any existing SCF module.
See `EPISTEMIC_AUDIT_ROADMAP.md` for package status.
"""
from __future__ import annotations

from .finite import audit_finite_claim
from .records import AssumptionSpec, ClaimReport, ClaimSpec, FiniteDomainSpec

__all__ = [
    "AssumptionSpec",
    "ClaimReport",
    "ClaimSpec",
    "FiniteDomainSpec",
    "audit_finite_claim",
]
