"""H3 verification: observation-dependent identification (K4, K8).

K4 (X={0,1,2}^2, h(x)=x1+x2, y=2 -> F(2)={(0,2),(1,1),(2,0)}; boolean
claim "both reserves >=1" holds only at (1,1); q=(x1-x2)^2 has the exact
value set {0,4}) and K8 (P=I4, partition {{0,1},{2,3}}, exact PC=CQ with
Q=I2, yet the micro event {1} is NOT a union of macro classes) were
independently re-derived by hand before this file was written (see
`EPISTEMIC_AUDIT_ROADMAP.md` H0 section) and match the plan's stated
reference values exactly.
"""
from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from scoped_correspondence.correspondence.controlled_markov import partition_indicator
from scoped_correspondence.epistemic.observation_fibers import (
    identified_values,
    macro_dynamics_and_observability,
    observation_fiber,
)
from scoped_correspondence.epistemic.records import AssumptionSpec, FiniteDomainSpec


def require(condition, msg=""):
    if not condition:
        raise AssertionError(msg)


def _assump(id_, predicate):
    return AssumptionSpec(id=id_, text=id_, role="structural", predicate=predicate)


def _k4_domain():
    candidates = tuple(itertools.product(range(3), repeat=2))  # X = {0,1,2}^2
    return FiniteDomainSpec(id="k4_reserves", candidates=candidates, scope_text="X={0,1,2}^2")


def check_k4_fiber_and_boolean_nonidentification():
    """F(2)={(0,2),(1,1),(2,0)}; the boolean claim 'both reserves >=1'
    holds only in (1,1) -- NOT identified at y=2 (fiber contains both
    truth values)."""
    domain = _k4_domain()
    h = lambda x: x[0] + x[1]
    fiber = observation_fiber(domain, [], h, 2)
    require(fiber.search_complete, "fiber scan must complete")
    require(not fiber.empty_fiber, "F(2) must be nonempty")
    require(set(fiber.fiber) == {(0, 2), (1, 1), (2, 0)}, f"expected F(2)={{(0,2),(1,1),(2,0)}}, got {set(fiber.fiber)}")

    both_at_least_1 = lambda x: bool(x[0] >= 1 and x[1] >= 1)
    q_bool = identified_values(fiber, both_at_least_1)
    require(not q_bool.point_identified, "the boolean claim must NOT be point-identified at y=2")
    require(set(q_bool.values) == {False, True}, f"expected both truth values present, got {q_bool.values}")
    return {"fiber": sorted(fiber.fiber), "bool_values": sorted(q_bool.values, key=str)}


def check_k4_disconnected_value_set_not_collapsed_to_interval():
    """q=(x1-x2)^2 at y=2 has the EXACT value set {0,4} -- min/max are
    reported as convenience fields alongside the set, but the set itself
    must never collapse into [0,4] (which would wrongly suggest 1 or 2
    are reachable)."""
    domain = _k4_domain()
    h = lambda x: x[0] + x[1]
    fiber = observation_fiber(domain, [], h, 2)
    q = lambda x: (x[0] - x[1]) ** 2
    report = identified_values(fiber, q)
    require(not report.point_identified, "q must not be point-identified at y=2")
    require(set(report.values) == {0, 4}, f"expected exact value set {{0,4}}, got {report.values}")
    require(2 not in report.values and 1 not in report.values, "the value set must not contain interpolated values")
    require(report.min_value == 0 and report.max_value == 4, "min/max convenience fields must still be correct")
    require(len(report.notes) > 0, "a non-point-identified result must explain itself in notes")
    return {"values": sorted(report.values), "min": report.min_value, "max": report.max_value}


def check_k4_refinement_shrinks_identified_set():
    """Refining the observation from h_c=x1+x2 to h_f=(x1+x2, min(x1,x2))
    (so that h_c = r o h_f, r = projection onto the first component)
    strictly shrinks the reachable value sets: both refined fibers'
    Q-sets are proper, nonempty subsets of the coarse Q-set {0,4}. The
    m=0 sub-fiber additionally demonstrates the plan's exact point (§4.4):
    m=min(x1,x2) SUFFICES to point-identify the boolean claim (False, since
    min=0 means at least one reserve is 0) and this q (4, since both (0,2)
    and (2,0) give the same squared difference) WITHOUT distinguishing the
    two underlying states themselves -- the raw state x is NOT
    point-identified at m=0, only these two derived quantities are."""
    domain = _k4_domain()
    q = lambda x: (x[0] - x[1]) ** 2
    both_at_least_1 = lambda x: bool(x[0] >= 1 and x[1] >= 1)

    coarse_fiber = observation_fiber(domain, [], lambda x: x[0] + x[1], 2)
    coarse_q = identified_values(coarse_fiber, q)
    require(set(coarse_q.values) == {0, 4}, f"coarse Q-set must be {{0,4}}, got {coarse_q.values}")

    h_fine = lambda x: (x[0] + x[1], min(x[0], x[1]))

    fine_fiber_m1 = observation_fiber(domain, [], h_fine, (2, 1))
    require(set(fine_fiber_m1.fiber) == {(1, 1)}, f"m=1 sub-fiber must be exactly {{(1,1)}}, got {set(fine_fiber_m1.fiber)}")
    fine_q_m1 = identified_values(fine_fiber_m1, q)
    require(fine_q_m1.point_identified and fine_q_m1.values == (0,), "m=1 sub-fiber must point-identify q=0")
    fine_bool_m1 = identified_values(fine_fiber_m1, both_at_least_1)
    require(fine_bool_m1.point_identified and fine_bool_m1.values == (True,), "m=1 sub-fiber must point-identify the boolean claim as True")

    fine_fiber_m0 = observation_fiber(domain, [], h_fine, (2, 0))
    require(set(fine_fiber_m0.fiber) == {(0, 2), (2, 0)}, f"m=0 sub-fiber must be exactly {{(0,2),(2,0)}}, got {set(fine_fiber_m0.fiber)}")
    fine_q_m0 = identified_values(fine_fiber_m0, q)
    require(fine_q_m0.point_identified and fine_q_m0.values == (4,), "m=0 sub-fiber must point-identify q=4 (both states give (x1-x2)^2=4)")
    fine_bool_m0 = identified_values(fine_fiber_m0, both_at_least_1)
    require(
        fine_bool_m0.point_identified and fine_bool_m0.values == (False,),
        "m=0 sub-fiber must point-identify the boolean claim as False -- m suffices for the CLAIM even here",
    )
    fine_state_m0 = identified_values(fine_fiber_m0, lambda x: x)
    require(
        not fine_state_m0.point_identified and set(fine_state_m0.values) == {(0, 2), (2, 0)},
        "the RAW STATE must remain unresolved at m=0 -- m identifies the claim and q without identifying the state itself",
    )

    require(set(fine_q_m1.values) <= set(coarse_q.values), "refined value set at m=1 must be a subset of the coarse one")
    require(set(fine_q_m0.values) <= set(coarse_q.values), "refined value set at m=0 must be a subset of the coarse one")
    return {
        "coarse_q": sorted(coarse_q.values),
        "fine_q_m1": fine_q_m1.values,
        "fine_q_m0": fine_q_m0.values,
    }


def check_empty_fiber_is_flagged_not_perfect_identification():
    """y=6 is unreachable in X={0,1,2}^2 (max sum is 4) -- the fiber is
    empty, and this must be reported as a mismatch, never as vacuous
    point-identification."""
    domain = _k4_domain()
    fiber = observation_fiber(domain, [], lambda x: x[0] + x[1], 6)
    require(fiber.empty_fiber, "y=6 must give an empty fiber")
    require(len(fiber.notes) > 0, "an empty fiber must carry an explanatory note")
    report = identified_values(fiber, lambda x: (x[0] - x[1]) ** 2)
    require(not report.point_identified, "an empty fiber must never be reported as point-identified")
    require(report.values == (), "an empty fiber's value set must be empty, not vacuously anything")
    return {"empty": fiber.empty_fiber, "notes": fiber.notes}


def check_k8_exact_dynamics_but_event_not_observable():
    """P=I4, partition {{0,1},{2,3}}: exact PC=CQ with Q=I2, but the
    micro event {1} is NOT a union of macro classes -- dynamics
    compatibility and event observability are reported as two SEPARATE
    fields, never merged."""
    C, _classes = partition_indicator([0, 0, 1, 1])
    P_identity = np.eye(4)
    report = macro_dynamics_and_observability(
        P_by_action={"only_action": P_identity}, C=C, omega={"only_action": "only_macro"}, micro_event=[1],
    )
    require(report.dynamics_exact, "P=I4 under this partition must be exactly lumpable")
    require(not report.event_is_union_of_classes, "the singleton event {1} must NOT be a union of classes")
    require(len(report.notes) > 0, "the exact-dynamics-but-not-observable combination must be explicitly noted")

    q_estimate = report.dynamics_reports["only_action"].Q_estimate
    require(np.allclose(q_estimate, np.eye(2)), f"Q must be I2, got {q_estimate}")

    report_full_class = macro_dynamics_and_observability(
        P_by_action={"only_action": P_identity}, C=C, omega={"only_action": "only_macro"}, micro_event=[0, 1],
    )
    require(report_full_class.event_is_union_of_classes, "the FULL class {0,1} must be a union of classes")
    require(len(report_full_class.notes) == 0, "no caveat is needed when the event IS observable")
    return {
        "dynamics_exact": report.dynamics_exact,
        "event_1_observable": report.event_is_union_of_classes,
        "event_01_observable": report_full_class.event_is_union_of_classes,
    }


def check_fiber_budget_abort_not_silently_complete():
    """A budget too small to scan the whole domain must abort with
    search_complete=False, and `identified_values` must refuse to draw
    an identification conclusion from that incomplete fiber."""
    domain = _k4_domain()  # 9 candidates
    fiber = observation_fiber(domain, [], lambda x: x[0] + x[1], 2, budget=2)
    require(not fiber.search_complete, "budget=2 must not scan the full 9-candidate domain")
    report = identified_values(fiber, lambda x: (x[0] - x[1]) ** 2)
    require(not report.search_complete, "identified_values must propagate incompleteness")
    require(not report.point_identified, "an incomplete fiber must never be reported as point-identified")
    return {"fiber_search_complete": fiber.search_complete, "report_search_complete": report.search_complete}


def check_r5_domain_coverage_propagates_through_fiber_and_identification():
    """Followup-Review-Fix R5 (SCF_REVIEW_H0_H7_9dde420.md): a domain
    declared `coverage="partial"` must have that value carried all the
    way through FiberReport and IdentifiedSetReport -- not silently
    dropped/identical to a `"complete"` domain."""
    d_partial = FiniteDomainSpec(id="partial_sample", candidates=(0, 1, 2), scope_text="a partial sample", coverage="partial")
    d_complete = FiniteDomainSpec(id="complete_sample", candidates=(0, 1, 2), scope_text="the whole space", coverage="complete")
    fiber_p = observation_fiber(d_partial, [], lambda w: w, 1)
    fiber_c = observation_fiber(d_complete, [], lambda w: w, 1)
    require(fiber_p.domain_coverage == "partial", f"FiberReport must carry coverage='partial' through, got {fiber_p.domain_coverage}")
    require(fiber_c.domain_coverage == "complete", f"FiberReport must carry coverage='complete' through, got {fiber_c.domain_coverage}")

    id_p = identified_values(fiber_p, lambda w: w * 2)
    require(id_p.domain_coverage == "partial", f"IdentifiedSetReport must carry coverage through from its fiber, got {id_p.domain_coverage}")
    return {"fiber_partial_coverage": fiber_p.domain_coverage, "identified_partial_coverage": id_p.domain_coverage}


CHECKS = [
    check_k4_fiber_and_boolean_nonidentification,
    check_k4_disconnected_value_set_not_collapsed_to_interval,
    check_k4_refinement_shrinks_identified_set,
    check_empty_fiber_is_flagged_not_perfect_identification,
    check_k8_exact_dynamics_but_event_not_observable,
    check_fiber_budget_abort_not_silently_complete,
    check_r5_domain_coverage_propagates_through_fiber_and_identification,
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
    out_path = Path(__file__).with_name("verify_epistemic_identification_results.json")
    out_path.write_text(json.dumps({"n_passed": n_passed, "n_total": len(CHECKS), "results": results}, indent=2, default=str))
    print(f"Report written to {out_path}")
    return 0 if n_passed == len(CHECKS) else 1


if __name__ == "__main__":
    raise SystemExit(main())
