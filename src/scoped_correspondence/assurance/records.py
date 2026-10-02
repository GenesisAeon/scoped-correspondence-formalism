"""``ProofReport`` and ``ClaimBundle`` (J4; design: docs/scope_composition_design.md §2).

Separate axes, never one collapsed confidence value (plan section 5.1):

- ``verdict``: proved / refuted / undecided / undefined_on_domain, plus
  ``observed_pass`` / ``observed_fail`` for sample-based checks.
- ``procedure_status``: completed / budget_exhausted / invalid_input /
  unsupported_structure / numerical_failure / incompatible.
- ``evidence_kind`` and ``empirical_status``: the vocabularies of
  ``epistemic.records`` (imported).
- ``arithmetic``: exact_rational / validated_enclosure / floating_point_estimate.
- ``conclusion_complete`` vs ``domain_exhausted``: a counterexample can end a
  refutation without scanning the whole domain; a budget stop without one
  proves nothing universal.
- ``empty_domain``: a for-all claim over an empty domain is vacuously true;
  it is flagged, never presented as a usable guarantee.

JSON output (``to_json``) uses ``allow_nan=False`` and serialises Fractions
exactly; unbounded values must be explicit markers, never float infinity.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from fractions import Fraction
from typing import Any, Dict, Optional, Tuple

from scoped_correspondence.epistemic.records import EMPIRICAL_STATUSES, EVIDENCE_KINDS

VERDICTS = ("proved", "refuted", "undecided", "undefined_on_domain", "observed_pass", "observed_fail")
PROCEDURE_STATUSES = (
    "completed",
    "budget_exhausted",
    "invalid_input",
    "unsupported_structure",
    "numerical_failure",
    "incompatible",
)
ARITHMETIC_KINDS = ("exact_rational", "validated_enclosure", "floating_point_estimate", "boolean")
ASSUMPTION_ORIGINS = ("given", "derived", "empirically_supported")


@dataclass(frozen=True)
class AssumptionUse:
    id: str
    origin: str
    text: str = ""

    def __post_init__(self) -> None:
        if self.origin not in ASSUMPTION_ORIGINS:
            raise ValueError(f"assumption origin must be one of {ASSUMPTION_ORIGINS}")


@dataclass(frozen=True)
class ProofReport:
    claim: str
    method: str
    verdict: str
    procedure_status: str
    evidence_kind: str
    arithmetic: str
    declared_domain: Any = None
    checked_domain: Any = None
    empty_domain: bool = False
    empirical_status: str = "not_tested"
    conclusion_complete: bool = False
    domain_exhausted: bool = False
    assumptions: Tuple[AssumptionUse, ...] = ()
    witnesses: Tuple[Any, ...] = ()
    depends_on: Tuple[str, ...] = ()
    reasons: Tuple[str, ...] = ()
    values: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.verdict not in VERDICTS:
            raise ValueError(f"verdict must be one of {VERDICTS}, got {self.verdict!r}")
        if self.procedure_status not in PROCEDURE_STATUSES:
            raise ValueError(f"procedure_status must be one of {PROCEDURE_STATUSES}, got {self.procedure_status!r}")
        if self.evidence_kind not in EVIDENCE_KINDS:
            raise ValueError(f"evidence_kind must be one of {EVIDENCE_KINDS}")
        if self.empirical_status not in EMPIRICAL_STATUSES:
            raise ValueError(f"empirical_status must be one of {EMPIRICAL_STATUSES}")
        if self.arithmetic not in ARITHMETIC_KINDS:
            raise ValueError(f"arithmetic must be one of {ARITHMETIC_KINDS}")
        if self.verdict == "proved" and self.procedure_status != "completed":
            raise ValueError("a 'proved' verdict requires procedure_status='completed'")
        if self.procedure_status == "budget_exhausted" and self.verdict == "proved":
            raise ValueError("a budget stop never proves a universal claim")
        if self.verdict == "proved" and self.evidence_kind == "numerical_sample":
            raise ValueError("a numerical sample cannot carry a 'proved' verdict (use observed_pass)")

    def to_dict(self) -> Dict[str, Any]:
        return {k: _ser(v) for k, v in self.__dict__.items()}

    def to_json(self, *, indent: Optional[int] = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, allow_nan=False, sort_keys=True)

    @property
    def certificate_id(self) -> str:
        """Content hash of the serialised report: IDENTIFIES the content, it
        does not prove it (plan section 5.2)."""
        return hashlib.sha256(self.to_json(indent=None).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class ClaimBundle:
    """A typed collection of reports; no aggregate verdict is computed --
    heterogeneous claims are not summed into one 'verified' flag."""

    title: str
    reports: Tuple[ProofReport, ...]

    def by_verdict(self) -> Dict[str, int]:
        out: Dict[str, int] = {}
        for r in self.reports:
            out[r.verdict] = out.get(r.verdict, 0) + 1
        return out

    def to_json(self) -> str:
        return json.dumps({"title": self.title, "reports": [r.to_dict() for r in self.reports],
                           "by_verdict": self.by_verdict()}, indent=2, allow_nan=False, sort_keys=True)


def _ser(v: Any) -> Any:
    if isinstance(v, Fraction):
        return {"numerator": v.numerator, "denominator": v.denominator}
    if isinstance(v, float) and v != v:
        raise ValueError("NaN is not serialisable in a ProofReport")
    if isinstance(v, float) and v in (float("inf"), float("-inf")):
        raise ValueError("float infinity is not serialisable; use an explicit marker")
    if hasattr(v, "to_dict"):
        return v.to_dict()
    if isinstance(v, AssumptionUse):
        return {"id": v.id, "origin": v.origin, "text": v.text}
    if isinstance(v, (tuple, list)):
        return [_ser(x) for x in v]
    if isinstance(v, dict):
        return {str(k): _ser(x) for k, x in v.items()}
    return v


def proof_report_from_claim_report(claim_report, *, claim: str) -> ProofReport:
    """Adapter: REFERENCE an existing finite-domain ``ClaimReport`` without
    reinterpreting it. The logical status maps as follows; anything else
    stays 'undecided' with the original status kept in ``reasons``."""
    mapping = {
        "entailed_in_scope": ("proved", "completed"),
        "negation_entailed_in_scope": ("refuted", "completed"),
        "underdetermined": ("undecided", "completed"),
        "incomplete": ("undecided", "budget_exhausted"),
        "no_admissible_model_in_scope": ("undecided", "completed"),
    }
    verdict, status = mapping[claim_report.logical_status]
    return ProofReport(
        claim=claim,
        method="epistemic.finite.audit_finite_claim (adapter)",
        verdict=verdict,
        procedure_status=status,
        evidence_kind=claim_report.evidence_kind,
        arithmetic="boolean",
        empty_domain=claim_report.logical_status == "no_admissible_model_in_scope",
        empirical_status=claim_report.empirical_status,
        conclusion_complete=claim_report.search_complete,
        domain_exhausted=claim_report.all_candidates_scanned,
        reasons=(f"source logical_status={claim_report.logical_status}",
                 f"domain_relationship={claim_report.domain_relationship}"),
    )


__all__ = [
    "VERDICTS",
    "PROCEDURE_STATUSES",
    "ARITHMETIC_KINDS",
    "ASSUMPTION_ORIGINS",
    "AssumptionUse",
    "ProofReport",
    "ClaimBundle",
    "proof_report_from_claim_report",
]
