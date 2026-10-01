"""Typed composition of correspondences (Paket J4, plan sections 10.2-10.3).

A ``CorrespondenceLink`` T: A -> B carries everything that must MATCH before
two links may be chained: model ids, state coordinates, units and clocks on
both sides -- equal model NAMES alone are not a compatibility proof
(plan §10.2). Maps are exact affine maps; time factors are positive
constants (state-dependent time maps stay in the existing point/numeric
routines, plan §10.3 last paragraph).

Composite domain:  D12 = D1 ∩ T1^{-1}(D2)   (exact; kept symbolic if not a box)
Composite horizon: H12 = min(H1, H2 / c1)    (H in the respective source time)
Composite clock factor: c12 = c1 * c2

Two DIFFERENT error calculations (plan §10.3):

- Flow error: if T2 is L2-Lipschitz on the relevant region INCLUDING the
  connecting segments (a declared certificate), then
      delta12(t) <= L2 * delta1(t) + delta2(c1 t).
  The second bound is evaluated at the mapped time, NOT multiplied by c1.
  Without a Lipschitz certificate no composite flow bound is produced.
- Vector-field residual: r12 = (DT2 o T1) r1 + a1 (r2 o T1), so
      |r12| <= M eps1 + A eps2,
  M bounding the operator norm of DT2 (on T1(D12)), A bounding |a1|.
  A small field residual is NOT by itself an equally small flow error.

Different conservative bounds for different bracketings may differ without
violating associativity of the underlying maps.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
from typing import Optional, Tuple

from scoped_correspondence.assurance.records import ProofReport
from scoped_correspondence.correspondence.domains import (
    AffineMap,
    Domain,
    HalfspaceSet,
    RationalBox,
    preimage_constraint,
)
from scoped_correspondence.errors import ScopeViolationError


def _q(x, what) -> Fraction:
    if isinstance(x, bool) or not isinstance(x, (int, Fraction)):
        raise ScopeViolationError(f"{what} must be exact (int/Fraction), got {type(x).__name__}")
    return Fraction(x)


@dataclass(frozen=True)
class Side:
    """One end of a link: model identity and its state interface."""

    model_id: str
    coordinates: Tuple[str, ...]
    units: Tuple[str, ...]
    clock: str


@dataclass(frozen=True)
class LipschitzCertificate:
    """Declared Lipschitz constant of a map on a region that must include the
    connecting segments of the composed trajectories."""

    constant: Fraction
    region: Domain
    covers_connecting_segments: bool
    evidence: str  # e.g. "exact: operator norm of a linear map"

    def __post_init__(self) -> None:
        object.__setattr__(self, "constant", _q(self.constant, "Lipschitz constant"))
        if self.constant < 0:
            raise ScopeViolationError("Lipschitz constant must be >= 0")


@dataclass(frozen=True)
class CorrespondenceLink:
    name: str
    source: Side
    target: Side
    state_map: AffineMap
    time_factor: Fraction  # c > 0: source time t corresponds to target time c t
    domain: Domain  # initial-state domain in source coordinates
    horizon: Fraction  # in source time
    flow_error_bound: Optional[Fraction] = None  # sup over [0, horizon]
    flow_error_evidence: str = "not_evaluated"  # analytic_argument | numerical_sample | not_evaluated
    field_residual_bound: Optional[Fraction] = None  # sup |r| over domain
    field_residual_evidence: str = "not_evaluated"
    lipschitz: Optional[LipschitzCertificate] = None  # of state_map

    def __post_init__(self) -> None:
        object.__setattr__(self, "time_factor", _q(self.time_factor, "time factor"))
        object.__setattr__(self, "horizon", _q(self.horizon, "horizon"))
        if self.time_factor <= 0:
            raise ScopeViolationError("time_factor must be a positive constant")
        if self.horizon < 0:
            raise ScopeViolationError("horizon must be >= 0")
        for attr in ("flow_error_bound", "field_residual_bound"):
            v = getattr(self, attr)
            if v is not None:
                object.__setattr__(self, attr, _q(v, attr))
        if self.state_map.in_dim != len(self.source.coordinates) or self.state_map.out_dim != len(self.target.coordinates):
            raise ScopeViolationError("state_map dimensions must match the declared coordinates")


@dataclass(frozen=True)
class CompositionReport:
    status: str  # "composed" | "incompatible"
    reasons: Tuple[str, ...]
    link: Optional[CorrespondenceLink]
    domain_report: Optional[ProofReport] = None
    flow_bound_report: Optional[ProofReport] = None
    field_bound_report: Optional[ProofReport] = None
    notes: Tuple[str, ...] = field(default_factory=tuple)


def identity_link(side: Side, domain: Domain, horizon) -> CorrespondenceLink:
    n = len(side.coordinates)
    return CorrespondenceLink(f"id_{side.model_id}", side, side, AffineMap.identity(n), Fraction(1), domain, horizon,
                              flow_error_bound=Fraction(0), flow_error_evidence="analytic_argument",
                              field_residual_bound=Fraction(0),
                              field_residual_evidence="analytic_argument",
                              lipschitz=LipschitzCertificate(Fraction(1), domain, True, "exact: identity"))


def compatibility(l1: CorrespondenceLink, l2: CorrespondenceLink) -> Tuple[str, ...]:
    out = []
    a, b = l1.target, l2.source
    if a.model_id != b.model_id:
        out.append(f"intermediate model differs: {a.model_id!r} vs {b.model_id!r}")
    if a.coordinates != b.coordinates:
        out.append(f"state coordinates differ: {a.coordinates} vs {b.coordinates}")
    if a.units != b.units:
        out.append(f"units differ: {a.units} vs {b.units}")
    if a.clock != b.clock:
        out.append(f"clocks differ: {a.clock!r} vs {b.clock!r}")
    return tuple(out)


_EVIDENCE_ORDER = ("not_evaluated", "numerical_sample", "analytic_argument")


def _weakest(*kinds: str) -> str:
    """Weakest component evidence wins; unknown kinds count as not_evaluated."""
    ranks = [(_EVIDENCE_ORDER.index(k) if k in _EVIDENCE_ORDER else 0) for k in kinds]
    return _EVIDENCE_ORDER[min(ranks)]


def _within_box(d: Domain) -> RationalBox:
    if isinstance(d, RationalBox):
        return d
    if isinstance(d, HalfspaceSet):
        return d.box
    raise ScopeViolationError("composition currently needs box or halfspace domains for the first link")


def compose_correspondences(l1: CorrespondenceLink, l2: CorrespondenceLink, *,
                            dT2_norm_bound: Optional[Fraction] = None,
                            a1_abs_bound: Optional[Fraction] = None) -> CompositionReport:
    """Compose l2 after l1 (A -> B -> C). See module docstring.

    ``dT2_norm_bound`` / ``a1_abs_bound`` are the M and A of the field
    residual bound; for affine T2 the exact induced inf-norm is used when
    ``dT2_norm_bound`` is omitted (with a note), and for a constant time
    factor a1 = c1 when ``a1_abs_bound`` is omitted.
    """
    mism = compatibility(l1, l2)
    if mism:
        return CompositionReport("incompatible", mism, None)
    if not isinstance(l2.domain, RationalBox):
        return CompositionReport("incompatible", ("second link domain must be a RationalBox for an exact preimage",), None)
    within = _within_box(l1.domain)
    pre = preimage_constraint(l1.state_map, l2.domain, within)
    if isinstance(l1.domain, HalfspaceSet):
        rows = l1.domain.rows + (pre.rows if isinstance(pre, HalfspaceSet) else ())
        box = pre if isinstance(pre, RationalBox) else pre.box
        d12: Domain = HalfspaceSet(box, rows)
    else:
        d12 = pre
    empty = isinstance(d12, RationalBox) and d12.is_empty
    domain_report = ProofReport(
        claim="D12 = D1 ∩ T1^{-1}(D2)", method="domains.preimage_constraint", verdict="proved",
        procedure_status="completed", evidence_kind="analytic_argument", arithmetic="exact_rational",
        declared_domain=d12.describe(), empty_domain=empty, conclusion_complete=True,
        reasons=("exact preimage of a box under an affine map",) + (("EMPTY composite domain: every for-all statement is vacuous",) if empty else ()),
    )
    c1, c2 = l1.time_factor, l2.time_factor
    horizon = min(l1.horizon, l2.horizon / c1)
    notes = []

    # flow error: L2 * delta1 + delta2 (delta2 evaluated at the mapped time c1 t)
    if l1.flow_error_bound is None or l2.flow_error_bound is None:
        flow_report = ProofReport(claim="composite flow error bound", method="lipschitz + triangle inequality",
                                  verdict="undecided", procedure_status="unsupported_structure",
                                  evidence_kind="not_evaluated", arithmetic="exact_rational",
                                  reasons=("a component flow error bound is missing",))
        flow = None
    elif l2.lipschitz is None or not l2.lipschitz.covers_connecting_segments:
        flow_report = ProofReport(claim="composite flow error bound", method="lipschitz + triangle inequality",
                                  verdict="undecided", procedure_status="unsupported_structure",
                                  evidence_kind="not_evaluated", arithmetic="exact_rational",
                                  reasons=("no Lipschitz certificate for T2 covering the connecting segments",))
        flow = None
    else:
        flow = l2.lipschitz.constant * l1.flow_error_bound + l2.flow_error_bound
        fev = _weakest(l1.flow_error_evidence, l2.flow_error_evidence)
        fverdict = {"analytic_argument": "proved", "numerical_sample": "observed_pass"}.get(fev, "undecided")
        flow_report = ProofReport(claim=f"sup_[0,{horizon}] delta12 <= {flow}", method="L2*delta1 + delta2(c1 t)",
                                  verdict=fverdict, procedure_status="completed", evidence_kind=fev,
                                  arithmetic="exact_rational", conclusion_complete=fverdict == "proved",
                                  reasons=(f"component flow evidence: {l1.flow_error_evidence}, {l2.flow_error_evidence}",),
                                  depends_on=(f"Lipschitz certificate: {l2.lipschitz.evidence}",
                                              f"component bounds of {l1.name}, {l2.name}"),
                                  values={"L2": l2.lipschitz.constant, "delta1": l1.flow_error_bound,
                                          "delta2": l2.flow_error_bound, "bound": flow})

    # field residual: M eps1 + A eps2
    if l1.field_residual_bound is None or l2.field_residual_bound is None:
        field_report = ProofReport(claim="composite field residual bound", method="T4: M eps1 + A eps2",
                                   verdict="undecided", procedure_status="unsupported_structure",
                                   evidence_kind="not_evaluated", arithmetic="exact_rational",
                                   reasons=("a component field residual bound is missing",))
        field_bound = None
    else:
        M = dT2_norm_bound if dT2_norm_bound is not None else l2.state_map.inf_operator_norm()
        if dT2_norm_bound is None:
            notes.append("M = exact induced inf-norm of the affine T2")
        A = a1_abs_bound if a1_abs_bound is not None else abs(c1)
        field_bound = Fraction(M) * l1.field_residual_bound + Fraction(A) * l2.field_residual_bound
        weakest = _weakest(l1.field_residual_evidence, l2.field_residual_evidence)
        verdict = {"analytic_argument": "proved", "numerical_sample": "observed_pass"}.get(weakest, "undecided")
        field_report = ProofReport(claim=f"sup |r12| <= {field_bound}", method="T4: M eps1 + A eps2", verdict=verdict,
                                   procedure_status="completed", evidence_kind=weakest,
                                   arithmetic="exact_rational", conclusion_complete=verdict == "proved",
                                   reasons=("component evidence: " + ", ".join((l1.field_residual_evidence, l2.field_residual_evidence)),
                                            "a small field residual is not by itself an equally small flow error"),
                                   values={"M": Fraction(M), "eps1": l1.field_residual_bound, "A": Fraction(A),
                                           "eps2": l2.field_residual_bound, "bound": field_bound})

    link = CorrespondenceLink(
        name=f"{l2.name}o{l1.name}", source=l1.source, target=l2.target,
        state_map=l1.state_map.then(l2.state_map), time_factor=c1 * c2, domain=d12, horizon=horizon,
        flow_error_bound=flow, flow_error_evidence=flow_report.evidence_kind, field_residual_bound=field_bound,
        field_residual_evidence=field_report.evidence_kind,
        lipschitz=None if (l1.lipschitz is None or l2.lipschitz is None) else LipschitzCertificate(
            l1.lipschitz.constant * l2.lipschitz.constant, d12,
            l1.lipschitz.covers_connecting_segments and l2.lipschitz.covers_connecting_segments,
            f"product of ({l1.lipschitz.evidence}) and ({l2.lipschitz.evidence})"),
    )
    return CompositionReport("composed", (), link, domain_report, flow_report, field_report, tuple(notes))


__all__ = ["Side", "LipschitzCertificate", "CorrespondenceLink", "CompositionReport", "identity_link",
           "compatibility", "compose_correspondences"]
