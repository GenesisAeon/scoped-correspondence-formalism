"""J4 verification (SCOPE_COMPOSITION_EVIDENCE_ROADMAP.md, plan section 10):
domains, functional contracts, refinement and typed composition.

Pflichtprüfungen: J-C05 (preimage scope), J-C06 (time factor, horizon),
J-C07 (flow vs field error), J-C08 (refinement direction); incompatible
intermediate models / units / clocks / metrics; empty intersection;
missing Lipschitz certificate; positive/negative scales; identity;
associativity of exact maps with equivalent scope conditions (while
conservative bounds of different bracketings may differ); plus opaque
predicates, symbolic (non-box) preimages, the ProofReport invariants and the
evidence downgrade for sampled component bounds.

Expected values from verification/plan_controls/j_series_independent_controls.py.
"""
from __future__ import annotations

import json
import sys
from fractions import Fraction as F
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from scoped_correspondence.assurance.records import ProofReport, proof_report_from_claim_report
from scoped_correspondence.correspondence.composition import (
    CorrespondenceLink,
    LipschitzCertificate,
    Side,
    compose_correspondences,
    identity_link,
)
from scoped_correspondence.correspondence.contracts import FunctionalContract, check_refinement
from scoped_correspondence.correspondence.domains import (
    AffineMap,
    FiniteSet,
    HalfspaceSet,
    OpaquePredicate,
    RationalBox,
    certify_subset,
    domain_contains,
    preimage_constraint,
    sets_equal,
)
from scoped_correspondence.epistemic.finite import audit_finite_claim
from scoped_correspondence.epistemic.records import ClaimSpec, FiniteDomainSpec
from scoped_correspondence.errors import ScopeViolationError


def require(c, m=""):
    if not c:
        raise AssertionError(m)


def raises(fn, exc=(ScopeViolationError, ValueError)):
    try:
        fn()
    except exc:
        return True
    return False


A = Side("A", ("x",), ("m",), "t_A")
B = Side("B", ("y",), ("m",), "t_B")
C = Side("C", ("z",), ("m",), "t_C")
D = Side("D", ("w",), ("m",), "t_D")
UNIT = RationalBox.interval(0, 1)


def link(name, src, tgt, a, c, dom, horizon, **kw):
    return CorrespondenceLink(name, src, tgt, AffineMap.scalar(a), F(c), dom, F(horizon), **kw)


def check_jc05_preimage_scope():
    pre = preimage_constraint(AffineMap.scalar(2), UNIT, UNIT)
    require(isinstance(pre, RationalBox) and pre.bounds == ((F(0), F(1, 2)),), f"D12 must be [0,1/2], got {pre}")
    require(domain_contains(UNIT, F(3, 4)) and not domain_contains(UNIT, AffineMap.scalar(2)(F(3, 4))[0]), "x=3/4 maps to 3/2 outside D2")
    rep = compose_correspondences(link("T1", A, B, 2, F(1, 2), UNIT, 4), link("T2", B, C, 3, F(1, 2), UNIT, 1))
    require(rep.status == "composed" and rep.link.domain.bounds == ((F(0), F(1, 2)),), "composition must restrict the scope")
    require(not domain_contains(rep.link.domain, F(3, 4)), "3/4 must be outside the composite scope")
    return {"D12": rep.domain_report.declared_domain}


def check_jc06_time_factor_and_horizon():
    rep = compose_correspondences(link("T1", A, B, 2, F(1, 2), UNIT, 4), link("T2", B, C, 3, F(1, 2), UNIT, 1))
    require(rep.link.time_factor == F(1, 4), f"composite time factor 1/4, got {rep.link.time_factor}")
    require(rep.link.horizon == 2, f"H12 = min(4, 1/(1/2)) = 2, got {rep.link.horizon}")
    require(rep.link.state_map(F(1, 3)) == (F(2),), "composite map is 6x")
    require(raises(lambda: link("bad", A, B, 2, 0, UNIT, 1)) and raises(lambda: link("bad", A, B, 2, -1, UNIT, 1)),
            "non-positive time factors are input errors")
    return {"c12": str(rep.link.time_factor), "H12": str(rep.link.horizon)}


def check_jc07_flow_versus_field_error():
    lip = LipschitzCertificate(F(3), RationalBox.interval(-10, 10), True, "exact: |3y - 3y'| = 3|y - y'|")
    l1 = link("T1", A, B, 2, 2, RationalBox.interval(0, F(1, 2)), 1, flow_error_bound=F(1, 10), flow_error_evidence="analytic_argument",
              field_residual_bound=F(1), field_residual_evidence="analytic_argument")
    l2 = link("T2", B, C, 3, 3, RationalBox.interval(-10, 10), 10, flow_error_bound=F(1, 5), flow_error_evidence="analytic_argument",
              field_residual_bound=F(3), field_residual_evidence="analytic_argument", lipschitz=lip)
    rep = compose_correspondences(l1, l2)
    require(rep.flow_bound_report.verdict == "proved" and rep.link.flow_error_bound == F(1, 2), f"flow bound 1/2, got {rep.link.flow_error_bound}")
    require(rep.field_bound_report.values["M"] == 3 and rep.field_bound_report.values["A"] == 2, "M=3, A=|a1|=2")
    require(rep.link.field_residual_bound == 9, f"field bound 9, got {rep.link.field_residual_bound}")
    # the bound is attained at x=1/2 and r12(1/4)=15/2 (direct residual, plan J-C07)
    r12 = lambda x: 6 * x + 6
    require(r12(F(1, 2)) == 9 and r12(F(1, 4)) == F(15, 2) and all(r12(F(k, 8)) <= 9 for k in range(5)), "bound attained, never exceeded on [0,1/2]")
    require(rep.flow_bound_report.values["delta2"] == F(1, 5), "delta2 enters unscaled (evaluated at c1 t, not multiplied by c1)")
    return {"flow": str(rep.link.flow_error_bound), "field": str(rep.link.field_residual_bound)}


def check_jc08_refinement_direction():
    spec = FunctionalContract("spec", UNIT, F(1, 5), "abs", ("x",), ("m",), "t")
    impl = FunctionalContract("impl", RationalBox.interval(-1, 2), F(1, 10), "abs", ("x",), ("m",), "t")
    fwd, back = check_refinement(impl, spec), check_refinement(spec, impl)
    require(fwd.verdict == "proved", f"impl must refine spec: {fwd.reasons}")
    require(back.verdict == "refuted" and back.witnesses, f"spec must not refine impl, with witness: {back.reasons}")
    weaker = FunctionalContract("weak", RationalBox.interval(-1, 2), F(3, 10), "abs", ("x",), ("m",), "t")
    require(check_refinement(weaker, spec).verdict == "refuted", "larger error bound cannot refine")
    return {"forward": fwd.verdict, "backward": back.verdict, "witness": [str(x) for x in back.witnesses[0]]}


def check_incompatible_interfaces():
    l1 = link("T1", A, B, 2, 1, UNIT, 1)
    out = {}
    cases = {
        "model": Side("B2", ("y",), ("m",), "t_B"),
        "coordinates": Side("B", ("y_other",), ("m",), "t_B"),
        "units": Side("B", ("y",), ("km",), "t_B"),
        "clock": Side("B", ("y",), ("m",), "t_B_days"),
    }
    for k, side in cases.items():
        rep = compose_correspondences(l1, link("T2", side, C, 3, 1, UNIT, 1))
        require(rep.status == "incompatible" and rep.link is None and any(k[:5] in r for r in rep.reasons), f"{k}: must be incompatible, got {rep.reasons}")
        out[k] = rep.reasons[0]
    same_name = Side("B", ("q",), ("m",), "t_B")  # same model NAME, different interface
    require(compose_correspondences(l1, link("T2", same_name, C, 3, 1, UNIT, 1)).status == "incompatible",
            "equal model names are no compatibility proof")
    spec = FunctionalContract("spec", UNIT, F(1, 5), "abs", ("x",), ("m",), "t")
    other_metric = FunctionalContract("impl", UNIT, F(1, 10), "rel", ("x",), ("m",), "t")
    r = check_refinement(other_metric, spec)
    require(r.procedure_status == "incompatible" and r.verdict == "undecided", "metric mismatch is 'incompatible', not 'refuted'")
    return out


def check_empty_intersection_is_flagged():
    rep = compose_correspondences(link("T1", A, B, 2, 1, UNIT, 1), link("T2", B, C, 1, 1, RationalBox.interval(5, 6), 1))
    require(rep.status == "composed" and rep.domain_report.empty_domain and rep.link.domain.is_empty, "empty D12 must be flagged")
    require(any("vacuous" in r for r in rep.domain_report.reasons), "vacuity must be stated")
    vac = certify_subset(rep.link.domain, RationalBox.interval(100, 101))
    require(vac.verdict == "proved" and vac.empty_domain, "inclusion of an empty domain is vacuous and flagged")
    return {"empty": True}


def check_missing_lipschitz_gives_no_flow_bound():
    l1 = link("T1", A, B, 2, 1, UNIT, 1, flow_error_bound=F(1, 10), flow_error_evidence="analytic_argument")
    no_lip = link("T2", B, C, 3, 1, RationalBox.interval(-5, 5), 1, flow_error_bound=F(1, 5), flow_error_evidence="analytic_argument")
    rep = compose_correspondences(l1, no_lip)
    require(rep.flow_bound_report.verdict == "undecided" and rep.link.flow_error_bound is None, "no Lipschitz certificate -> no flow bound")
    partial = link("T2", B, C, 3, 1, RationalBox.interval(-5, 5), 1, flow_error_bound=F(1, 5), flow_error_evidence="analytic_argument",
                   lipschitz=LipschitzCertificate(F(3), RationalBox.interval(-5, 5), False, "only on the states, not the segments"))
    require(compose_correspondences(l1, partial).link.flow_error_bound is None, "certificate must cover connecting segments")
    sampled = link("T2", B, C, 3, 1, RationalBox.interval(-5, 5), 1, flow_error_bound=F(1, 5), flow_error_evidence="numerical_sample",
                   lipschitz=LipschitzCertificate(F(3), RationalBox.interval(-5, 5), True, "exact"))
    rs = compose_correspondences(l1, sampled).flow_bound_report
    require(rs.verdict == "observed_pass" and rs.evidence_kind == "numerical_sample", "a sampled component bound downgrades the composite")
    return {"no_lipschitz": "undecided", "sampled": rs.verdict}


def check_positive_and_negative_scales():
    pre_neg = preimage_constraint(AffineMap.scalar(-2, 1), UNIT, RationalBox.interval(-5, 5))
    require(pre_neg.bounds == ((F(0), F(1, 2)),), f"-2x+1 in [0,1] <=> x in [0,1/2], got {pre_neg.bounds}")
    const = preimage_constraint(AffineMap.scalar(0, 3), UNIT, UNIT)
    require(const.is_empty, "a constant map outside the target gives an empty preimage")
    neg = link("Tneg", A, B, -2, 1, UNIT, 1)
    rep = compose_correspondences(neg, link("T2", B, C, 1, 1, RationalBox.interval(-1, 0), 1))
    require(rep.link.domain.bounds == ((F(0), F(1, 2)),), "negative state scale handled exactly")
    return {"neg_preimage": [str(x) for x in pre_neg.bounds[0]]}


def check_identity_and_associativity():
    l1 = link("T1", A, B, 2, F(1, 2), UNIT, 4, flow_error_bound=F(1, 10), flow_error_evidence="analytic_argument",
              lipschitz=LipschitzCertificate(F(2), RationalBox.interval(-9, 9), True, "exact"))
    l2 = link("T2", B, C, 3, F(1, 2), RationalBox.interval(0, F(3, 2)), 3, flow_error_bound=F(1, 5), flow_error_evidence="analytic_argument",
              lipschitz=LipschitzCertificate(F(3), RationalBox.interval(-9, 9), True, "exact"))
    l3 = link("T3", C, D, F(-1, 2), 2, RationalBox.interval(-1, F(9, 4)), 5, flow_error_bound=F(1, 7), flow_error_evidence="analytic_argument",
              lipschitz=LipschitzCertificate(F(1, 2), RationalBox.interval(-9, 9), True, "exact"))
    left = compose_correspondences(l1, identity_link(B, RationalBox.interval(-9, 9), 100))
    require(left.link.state_map.A == l1.state_map.A and left.link.time_factor == l1.time_factor, "T o id = T")
    require(sets_equal(left.link.domain, l1.domain).verdict == "proved", "identity keeps the scope")
    right = compose_correspondences(identity_link(A, RationalBox.interval(-9, 9), 100), l1)
    require(sets_equal(right.link.domain, l1.domain).verdict == "proved" and right.link.horizon == l1.horizon, "id o T keeps scope and horizon")
    ab_c = compose_correspondences(compose_correspondences(l1, l2).link, l3).link
    a_bc = compose_correspondences(l1, compose_correspondences(l2, l3).link).link
    require(ab_c.state_map.A == a_bc.state_map.A and ab_c.state_map.b == a_bc.state_map.b, "maps associate exactly")
    require(ab_c.time_factor == a_bc.time_factor and ab_c.horizon == a_bc.horizon, "time factors and horizons associate")
    require(sets_equal(ab_c.domain, a_bc.domain).verdict == "proved", f"scope conditions must coincide: {ab_c.domain} vs {a_bc.domain}")
    # With constant component bounds both bracketings give
    # L3 (L2 d1 + d2) + d3 = L3 L2 d1 + (L3 d2 + d3) -- equal here by
    # distributivity. They MAY differ in general (e.g. region-dependent
    # Lipschitz constants), which is allowed; maps and scopes may not differ.
    # L2 = 3, L3 = 1/2, d1 = 1/10, d2 = 1/5, d3 = 1/7  ->  1/2 * (3/10 + 1/5) + 1/7 = 11/28
    require(ab_c.flow_error_bound == a_bc.flow_error_bound == F(1, 2) * (F(3) * F(1, 10) + F(1, 5)) + F(1, 7) == F(11, 28),
            "constant-bound case: both bracketings equal L3(L2 d1 + d2) + d3")
    return {"(l1 l2) l3 flow": str(ab_c.flow_error_bound), "l1 (l2 l3) flow": str(a_bc.flow_error_bound),
            "note": "equal here by distributivity of constant bounds; may differ in general without violating map associativity"}


def check_supported_domain_classes():
    fs = FiniteSet(((0,), (F(1, 2),), (1,)))
    require(certify_subset(fs, UNIT).verdict == "proved" and certify_subset(fs, UNIT).domain_exhausted, "finite subset proved by enumeration")
    require(certify_subset(UNIT, fs).verdict == "refuted", "a nondegenerate interval is not inside a finite set")
    opaque = OpaquePredicate("x<=1", lambda p: p[0] <= 1)
    require(domain_contains(opaque, (F(1, 2),)), "opaque predicate supports point membership")
    r = certify_subset(UNIT, opaque)
    require(r.verdict == "undecided", "opaque outer predicate yields no universal inclusion")
    require(certify_subset(opaque, UNIT).procedure_status == "unsupported_structure", "opaque inner domain unsupported")
    box2 = RationalBox(((0, 1), (0, 1)))
    shear = AffineMap(((1, 1),), (0,))  # x + y in [0, 1]
    pre = preimage_constraint(shear, UNIT, box2)
    require(isinstance(pre, HalfspaceSet), "a non-box preimage stays symbolic, never an enlarged box")
    require(domain_contains(pre, (F(1, 2), F(1, 2))) and not domain_contains(pre, (1, 1)), "symbolic preimage exact")
    require(certify_subset(RationalBox(((0, F(1, 2)), (0, F(1, 2)))), pre).verdict == "proved", "box in polyhedron via corners")
    require(raises(lambda: RationalBox.interval(0.1, 1)), "float bounds are rejected (exactness)")
    return {"symbolic_preimage": pre.describe()["kind"]}


def check_report_invariants_and_adapter():
    require(raises(lambda: ProofReport("c", "m", "proved", "budget_exhausted", "analytic_argument", "exact_rational")),
            "a budget stop cannot prove")
    require(raises(lambda: ProofReport("c", "m", "proved", "completed", "numerical_sample", "floating_point_estimate")),
            "a sample cannot prove")
    require(raises(lambda: ProofReport("c", "m", "proved", "completed", "analytic_argument", "exact_rational",
                                       values={"x": float("inf")}).to_json()), "float infinity is not serialisable")
    rep = check_refinement(FunctionalContract("i", RationalBox.interval(-1, 2), F(1, 10), "abs", ("x",), ("m",), "t"),
                           FunctionalContract("s", UNIT, F(1, 5), "abs", ("x",), ("m",), "t"))
    blob = json.loads(rep.to_json())
    require(blob["values"]["impl_bound"] == {"numerator": 1, "denominator": 10}, "Fractions serialised exactly")
    require(len(rep.certificate_id) == 64, "certificate id is a content hash")
    cr = audit_finite_claim(FiniteDomainSpec("d", (0, 1, 2), "toy"), [], ClaimSpec("c", "x<3", lambda x: x < 3))
    pr = proof_report_from_claim_report(cr, claim="x<3 on {0,1,2}")
    require(pr.verdict == "proved" and pr.evidence_kind == cr.evidence_kind and "entailed_in_scope" in pr.reasons[0],
            "adapter references the finite audit without reinterpretation")
    return {"certificate_id": rep.certificate_id[:12]}


CHECKS = [
    check_jc05_preimage_scope,
    check_jc06_time_factor_and_horizon,
    check_jc07_flow_versus_field_error,
    check_jc08_refinement_direction,
    check_incompatible_interfaces,
    check_empty_intersection_is_flagged,
    check_missing_lipschitz_gives_no_flow_bound,
    check_positive_and_negative_scales,
    check_identity_and_associativity,
    check_supported_domain_classes,
    check_report_invariants_and_adapter,
]


def main():
    results = {}
    n_passed = 0
    for check in CHECKS:
        name = check.__name__.removeprefix("check_")
        try:
            results[name] = check()
            print(f"PASS  {name}")
            n_passed += 1
        except AssertionError as e:
            results[name] = {"error": str(e)}
            print(f"FAIL  {name}: {e}")
        except Exception as e:
            results[name] = {"error": f"{type(e).__name__}: {e}"}
            print(f"ERROR {name}: {type(e).__name__}: {e}")
    print(f"\n{n_passed}/{len(CHECKS)} checks passed")
    out_path = Path(__file__).with_name("verify_correspondence_contracts_results.json")
    out_path.write_text(json.dumps({"n_passed": n_passed, "n_total": len(CHECKS), "results": results}, indent=2, default=str))
    print(f"Report written to {out_path}")
    return 0 if n_passed == len(CHECKS) else 1


if __name__ == "__main__":
    raise SystemExit(main())
