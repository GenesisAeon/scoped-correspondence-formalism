"""Functional assume-guarantee contracts and refinement (Paket J4, plan §10.2).

A ``FunctionalContract`` states an assumption domain A and a guarantee: an
error bound under a NAMED metric, on named state coordinates, in named
units, on a named clock. Refinement in the functional special case:

    impl refines spec  <=>  spec.assumption ⊆ impl.assumption
                            and impl.error_bound <= spec.error_bound
                            (same metric, coordinates, units, clock)

i.e. the implementation accepts at least every specified input and
guarantees at least as much there. The full theory of reactive
assume-guarantee contracts (Benveniste et al., S07) is NOT implemented.
Mismatching metric/coordinates/units/clock is reported as
``incompatible`` -- a different outcome from "refinement refuted".
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Tuple

from scoped_correspondence.assurance.records import ProofReport
from scoped_correspondence.correspondence.domains import Domain, certify_subset
from scoped_correspondence.errors import ScopeViolationError


@dataclass(frozen=True)
class FunctionalContract:
    name: str
    assumption: Domain
    error_bound: Fraction
    metric: str
    coordinates: Tuple[str, ...]
    units: Tuple[str, ...]
    clock: str

    def __post_init__(self) -> None:
        b = self.error_bound
        if isinstance(b, bool) or not isinstance(b, (int, Fraction)):
            raise ScopeViolationError("error_bound must be exact (int/Fraction)")
        object.__setattr__(self, "error_bound", Fraction(b))
        if self.error_bound < 0:
            raise ScopeViolationError("error_bound must be >= 0")


def interface_mismatches(a: FunctionalContract, b: FunctionalContract) -> Tuple[str, ...]:
    out = []
    for attr in ("metric", "coordinates", "units", "clock"):
        if getattr(a, attr) != getattr(b, attr):
            out.append(f"{attr}: {getattr(a, attr)!r} != {getattr(b, attr)!r}")
    return tuple(out)


def check_refinement(impl: FunctionalContract, spec: FunctionalContract) -> ProofReport:
    claim = f"{impl.name} refines {spec.name}"
    mism = interface_mismatches(impl, spec)
    if mism:
        return ProofReport(claim=claim, method="contracts.check_refinement", verdict="undecided",
                           procedure_status="incompatible", evidence_kind="not_evaluated",
                           arithmetic="exact_rational", reasons=mism)
    inc = certify_subset(spec.assumption, impl.assumption)
    reasons = [f"assumption inclusion: {inc.verdict} ({'; '.join(inc.reasons)})"]
    bound_ok = impl.error_bound <= spec.error_bound
    reasons.append(f"error bound {impl.error_bound} <= {spec.error_bound}: {bound_ok}")
    if inc.verdict == "proved" and bound_ok:
        verdict, status = "proved", "completed"
    elif inc.verdict == "refuted" or not bound_ok:
        verdict, status = "refuted", "completed"
    else:
        verdict, status = "undecided", inc.procedure_status
    return ProofReport(claim=claim, method="contracts.check_refinement", verdict=verdict, procedure_status=status,
                       evidence_kind="analytic_argument" if verdict != "undecided" else "not_evaluated",
                       arithmetic="exact_rational", conclusion_complete=verdict in ("proved", "refuted"),
                       witnesses=inc.witnesses, depends_on=("correspondence.domains.certify_subset",),
                       reasons=tuple(reasons), values={"impl_bound": impl.error_bound, "spec_bound": spec.error_bound})


__all__ = ["FunctionalContract", "interface_mismatches", "check_refinement"]
