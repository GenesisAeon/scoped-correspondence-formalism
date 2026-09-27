"""H6a/H6b verification: adapters to existing SCF reports.

H6a wraps `correspondence.contract.CorrespondenceReport` and H3's
`MacroObservabilityReport` (K8) as `ClaimReport`s without upgrading their
evidence_kind. H6b (optional) reuses the existing `BurkertProfile`/
`NFWProfile` astrophysics classes -- the SAME classes
`verify_galaxy_observation_maps.py::check_observation_equivalence_
cross_family_degeneracy` uses -- to frame that same two-radius
cross-family degeneracy in H3's identification vocabulary, without
duplicating that verify script's code. H6c (real SPARC reports) stays
explicitly deferred, per the plan and `EPISTEMIC_AUDIT_ROADMAP.md`.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import fsolve

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from scoped_correspondence.astrophysics import BurkertProfile, NFWProfile
from scoped_correspondence.correspondence.contract import CorrespondenceReport, Residual
from scoped_correspondence.correspondence.controlled_markov import partition_indicator
from scoped_correspondence.epistemic.adapters import (
    claim_report_from_correspondence,
    claim_reports_from_macro_observability,
)
from scoped_correspondence.epistemic.observation_fibers import macro_dynamics_and_observability
from scoped_correspondence.errors import ScopeViolationError


def require(condition, msg=""):
    if not condition:
        raise AssertionError(msg)


def check_correspondence_report_ok_wraps_as_entailed_numerical_sample():
    """A passing CorrespondenceReport becomes entailed_in_scope with
    evidence_kind='numerical_sample' and domain_relationship=
    'grid_of_continuous_space' -- never 'exhaustive_finite'."""
    residuals = tuple(Residual(value=1e-12, kind="conjugacy", at_state=float(i), at_time=1.0) for i in range(5))
    report = CorrespondenceReport(ok=True, max_residual=1e-12, residuals=residuals, evidence={"n_pairs": 5, "all_finite": True}, kind="conjugacy")
    claim = claim_report_from_correspondence(report, claim_id="test_conjugacy_ok")
    require(claim.logical_status == "entailed_in_scope", f"expected entailed_in_scope, got {claim.logical_status}")
    require(claim.evidence_kind == "numerical_sample", f"must stay numerical_sample, got {claim.evidence_kind}")
    require(claim.domain_relationship == "grid_of_continuous_space", f"expected grid_of_continuous_space, got {claim.domain_relationship}")
    require(claim.n_domain == 5 and claim.n_evaluated == 5, "n_domain/n_evaluated must reflect the sampled pairs")
    require(claim.empirical_status == "synthetic_only", "default empirical_status must be synthetic_only, never auto-upgraded")
    return {"logical_status": claim.logical_status, "evidence_kind": claim.evidence_kind}


def check_correspondence_report_failure_carries_worst_witness():
    """A failing CorrespondenceReport becomes negation_entailed_in_scope
    with a negative_witness pointing at the actual worst residual, not a
    generic 'it failed' placeholder."""
    residuals = (
        Residual(value=1e-12, kind="conjugacy", at_state=0.0, at_time=1.0),
        Residual(value=0.42, kind="conjugacy", at_state=1.0, at_time=2.0),
        Residual(value=1e-10, kind="conjugacy", at_state=2.0, at_time=1.0),
    )
    report = CorrespondenceReport(ok=False, max_residual=0.42, residuals=residuals, evidence={"n_pairs": 3, "all_finite": True}, kind="conjugacy")
    claim = claim_report_from_correspondence(report, claim_id="test_conjugacy_fail")
    require(claim.logical_status == "negation_entailed_in_scope", f"expected negation_entailed_in_scope, got {claim.logical_status}")
    require(claim.negative_witness is not None and claim.negative_witness["residual"] == 0.42, f"witness must point at the actual worst residual, got {claim.negative_witness}")
    require(claim.negative_witness["at_state"] == 1.0 and claim.negative_witness["at_time"] == 2.0, "witness must carry the exact state/time of the worst residual")
    return {"negative_witness": claim.negative_witness}


def check_invalid_empirical_status_rejected():
    residuals = (Residual(value=0.0, kind="conjugacy", at_state=0.0, at_time=0.0),)
    report = CorrespondenceReport(ok=True, max_residual=0.0, residuals=residuals, evidence={"n_pairs": 1, "all_finite": True}, kind="conjugacy")
    try:
        claim_report_from_correspondence(report, claim_id="bad", empirical_status="definitely_confirmed")
        raise AssertionError("an unrecognized empirical_status must raise, not silently accept")
    except ValueError:
        pass
    return {"rejected": True}


def check_k8_macro_observability_splits_into_two_separate_evidence_kinds():
    """K8 (P=I4, partition {{0,1},{2,3}}, event {1}) wrapped through the
    adapter yields TWO claims with two DIFFERENT evidence_kinds: dynamics
    (numerical_sample, since it is float/tol-based) and observability
    (exhaustive_finite, since is_union_of_classes is exact) -- never
    merged into one field."""
    C, _classes = partition_indicator([0, 0, 1, 1])
    P_identity = np.eye(4)
    macro_report = macro_dynamics_and_observability(
        P_by_action={"only_action": P_identity}, C=C, omega={"only_action": "only_macro"}, micro_event=[1],
    )
    dynamics_claim, observability_claim = claim_reports_from_macro_observability(
        macro_report, dynamics_claim_id="k8_dynamics", observability_claim_id="k8_observability",
    )
    require(dynamics_claim.logical_status == "entailed_in_scope", f"K8 dynamics must be entailed, got {dynamics_claim.logical_status}")
    require(dynamics_claim.evidence_kind == "numerical_sample", f"dynamics must stay numerical_sample, got {dynamics_claim.evidence_kind}")

    require(observability_claim.logical_status == "negation_entailed_in_scope", f"event {{1}} must NOT be observable, got {observability_claim.logical_status}")
    require(observability_claim.evidence_kind == "exhaustive_finite", f"observability must be exhaustive_finite, got {observability_claim.evidence_kind}")
    require(observability_claim.arithmetic_kind == "boolean", "observability check is a pure boolean set-membership fact")

    require(dynamics_claim.evidence_kind != observability_claim.evidence_kind, "the two claims must NEVER share one merged evidence_kind")
    return {
        "dynamics": {"status": dynamics_claim.logical_status, "evidence_kind": dynamics_claim.evidence_kind},
        "observability": {"status": observability_claim.logical_status, "evidence_kind": observability_claim.evidence_kind},
    }


def check_h6b_galaxy_two_radius_degeneracy_as_identification_example():
    """H6b (optional): the SAME BurkertProfile/NFWProfile classes used by
    `verify_galaxy_observation_maps.py::check_observation_equivalence_
    cross_family_degeneracy` reused here (not that verify script's code)
    to frame the same degeneracy in H3's vocabulary: the observation
    y=(g(r_a), g(r_b)) is matched EXACTLY by two structurally different
    families (Burkert vs NFW) -- the FAMILY/parametrization is NOT
    identified from y, even though y itself trivially is (by
    construction). The two profiles then diverge >10% at radii outside
    y, confirming this is a genuine degeneracy, not near-equality
    everywhere."""
    source = BurkertProfile(rho0_msun_pc3=0.03, r0_pc=2000.0)
    r_a, r_b = 1500.0, 6000.0
    y = (source.g(r_a), source.g(r_b))

    def eqs(params):
        log_rho_s, log_r_s = params
        prof = NFWProfile(rho_s_msun_pc3=10 ** log_rho_s, r_s_pc=10 ** log_r_s)
        return [prof.g(r_a) - y[0], prof.g(r_b) - y[1]]

    sol, info, ier, msg = fsolve(eqs, x0=[np.log10(0.01), np.log10(3000.0)], full_output=True)
    require(ier == 1, f"fsolve did not converge: {msg}")
    matched_nfw = NFWProfile(rho_s_msun_pc3=10 ** sol[0], r_s_pc=10 ** sol[1])

    require(abs(matched_nfw.g(r_a) - y[0]) / abs(y[0]) < 1e-6, "matched NFW must reproduce y at r_a")
    require(abs(matched_nfw.g(r_b) - y[1]) / abs(y[1]) < 1e-6, "matched NFW must reproduce y at r_b")

    # The observation y point-identifies itself (trivially), but does NOT
    # point-identify the family: two structurally different models
    # (Burkert vs NFW) both realize it exactly.
    families_matching_y = {"burkert", "nfw"}
    require(len(families_matching_y) > 1, "at least two distinct families realize the same observation y")

    out_of_sample = {}
    for r_c in (500.0, 12000.0, 30000.0):
        g_source = source.g(r_c)
        g_matched = matched_nfw.g(r_c)
        rel_diff = abs(g_source - g_matched) / g_source
        require(rel_diff > 0.1, f"expected genuine divergence outside y at r={r_c}, got rel_diff={rel_diff}")
        out_of_sample[f"r={r_c}"] = rel_diff

    return {"y": y, "families_matching_y": sorted(families_matching_y), "out_of_sample_rel_diffs": out_of_sample}


def check_r4a_nonfinite_residual_is_incomplete_not_confident_negation():
    """Followup-Review-Fix R4a (SCF_REVIEW_H0_H7_9dde420.md): a
    non-finite residual is a COMPUTATION ERROR, never evidence of a
    negated correspondence -- it must produce `incomplete` with
    `n_errors>0`, not a confident `negation_entailed_in_scope` with
    `n_errors=0`."""
    report = CorrespondenceReport(
        ok=False, max_residual=float("nan"),
        residuals=(Residual(value=float("nan"), kind="conjugacy", at_state=0.0, at_time=1.0),),
        evidence={"n_pairs": 1, "all_finite": False}, kind="conjugacy",
    )
    claim = claim_report_from_correspondence(report, claim_id="r4a_nonfinite")
    require(claim.logical_status == "incomplete", f"a non-finite residual must yield incomplete, got {claim.logical_status}")
    require(claim.n_errors == 1, f"the non-finite residual must be counted as an error, got n_errors={claim.n_errors}")
    require(not claim.search_complete, "a non-finite-residual result must not be search_complete")
    return {"logical_status": claim.logical_status, "n_errors": claim.n_errors}


def check_r4a_empty_action_set_is_rejected_not_vacuous_entailment():
    """Followup-Review-Fix R4a: an empty `P_by_action` must be rejected
    outright, never silently produce `dynamics_exact=True` via
    `all([])`."""
    C, _ = partition_indicator([0, 0, 1, 1])
    try:
        macro_dynamics_and_observability(P_by_action={}, C=C, omega={}, micro_event=[0, 1])
        raise AssertionError("an empty P_by_action must raise, not silently succeed vacuously")
    except ScopeViolationError:
        pass
    return {"rejected": True}


def check_r4b_mixed_pass_fail_note_clarifies_aggregate_quantifier():
    """Followup-Review-Fix R4b: when only SOME sampled pairs fail (all
    finite), the resulting `negation_entailed_in_scope` must carry an
    explicit note distinguishing '(not every pair passes' from 'every
    pair fails' -- ¬∀w C(w) != ∀w ¬C(w)."""
    mixed = CorrespondenceReport(
        ok=False, max_residual=1.0,
        residuals=(
            Residual(value=0.0, kind="conjugacy", at_state=0.0, at_time=0.0),
            Residual(value=1.0, kind="conjugacy", at_state=1.0, at_time=0.0),
        ),
        evidence={"n_pairs": 2, "all_finite": True}, kind="conjugacy",
    )
    claim = claim_report_from_correspondence(mixed, claim_id="r4b_mixed")
    require(claim.logical_status == "negation_entailed_in_scope", f"expected negation_entailed_in_scope, got {claim.logical_status}")
    require(
        any("AGGREGATE" in n for n in claim.notes),
        f"a genuine (non-error) negation must carry the aggregate-quantifier clarification note, got {claim.notes}",
    )
    return {"logical_status": claim.logical_status, "has_aggregate_note": True}


CHECKS = [
    check_correspondence_report_ok_wraps_as_entailed_numerical_sample,
    check_correspondence_report_failure_carries_worst_witness,
    check_invalid_empirical_status_rejected,
    check_k8_macro_observability_splits_into_two_separate_evidence_kinds,
    check_h6b_galaxy_two_radius_degeneracy_as_identification_example,
    check_r4a_nonfinite_residual_is_incomplete_not_confident_negation,
    check_r4a_empty_action_set_is_rejected_not_vacuous_entailment,
    check_r4b_mixed_pass_fail_note_clarifies_aggregate_quantifier,
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
    out_path = Path(__file__).with_name("verify_epistemic_adapters_results.json")
    out_path.write_text(json.dumps({"n_passed": n_passed, "n_total": len(CHECKS), "results": results}, indent=2, default=str))
    print(f"Report written to {out_path}")
    return 0 if n_passed == len(CHECKS) else 1


if __name__ == "__main__":
    raise SystemExit(main())
