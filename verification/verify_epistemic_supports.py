"""H2 verification: minimal supports and inconsistency cores.

Pflichtprüfungen (Plan §7, H2 section): K1 vollständig (beide
Kardinalitäten), Löschzeugen, konstante wahre Aussage mit leerem
Support, widersprüchlicher Ausgangsfall, mehrere alternative Supports,
Budgetabbruch, unveränderte Hintergrundannahmen.

K1 (W={0,1}^3 for p,q,r; A1=p, A2=p=>q, A3=q=>r, A4=p=>r; target C=r) was
independently re-derived by hand before this file was written (see
`EPISTEMIC_AUDIT_ROADMAP.md` H0 section and its follow-up hand-trace for
H2): the deletion order [A1,A4,A3,A2] lands on {A1,A2,A3}, and the order
[A1,A2,A3,A4] lands on {A1,A4} -- both subset-minimal, neither smaller
than the other's cardinality alone determines "the" answer (S6). Adding
A5=not(r) to the full set is jointly unsatisfiable; order [A1,A2,A3,A4,A5]
lands on the core {A1,A4,A5}, and order [A1,A4,A2,A3,A5] lands on
{A1,A2,A3,A5} -- matching the plan's stated reference values exactly.
"""
from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from scoped_correspondence.epistemic.records import AssumptionSpec, ClaimSpec, FiniteDomainSpec
from scoped_correspondence.epistemic.supports import find_minimal_inconsistent_core, find_minimal_support
from scoped_correspondence.errors import ScopeViolationError


def require(condition, msg=""):
    if not condition:
        raise AssertionError(msg)


def _assump(id_, predicate, role="structural"):
    return AssumptionSpec(id=id_, text=id_, role=role, predicate=predicate)


def _k1_domain():
    candidates = tuple(itertools.product([False, True], repeat=3))
    return FiniteDomainSpec(id="k1_pqr", candidates=candidates, scope_text="all (p,q,r) in {0,1}^3")


def _k1_assumptions():
    a1 = _assump("A1_p", lambda w: w[0])
    a2 = _assump("A2_p_implies_q", lambda w: (not w[0]) or w[1])
    a3 = _assump("A3_q_implies_r", lambda w: (not w[1]) or w[2])
    a4 = _assump("A4_p_implies_r", lambda w: (not w[0]) or w[2])
    a5 = _assump("A5_not_r", lambda w: not w[2])
    return a1, a2, a3, a4, a5


def _k1_claim():
    return ClaimSpec(id="target_r", text="r", target=lambda w: bool(w[2]))


def check_k1_two_minimal_supports():
    """Two different deletion orders reproduce both hand-derived minimal
    supports {A1,A4} (cardinality 2) and {A1,A2,A3} (cardinality 3) for
    the SAME starting set and claim -- proving subset-minimal is not
    smallest-cardinality (S6)."""
    domain = _k1_domain()
    a1, a2, a3, a4, _a5 = _k1_assumptions()
    claim = _k1_claim()

    order_a = [a1, a2, a3, a4]
    r_a = find_minimal_support(domain, order_a, claim)
    require(r_a.search_complete, "K1 support search (order A) must complete")
    require(
        set(r_a.support_ids) == {"A1_p", "A4_p_implies_r"},
        f"order A should land on {{A1,A4}}, got {r_a.support_ids}",
    )

    order_b = [a1, a4, a3, a2]
    r_b = find_minimal_support(domain, order_b, claim)
    require(r_b.search_complete, "K1 support search (order B) must complete")
    require(
        set(r_b.support_ids) == {"A1_p", "A2_p_implies_q", "A3_q_implies_r"},
        f"order B should land on {{A1,A2,A3}}, got {r_b.support_ids}",
    )

    require(set(r_a.support_ids) != set(r_b.support_ids), "the two orders must yield genuinely different supports")
    require(len(r_a.support_ids) == 2 and len(r_b.support_ids) == 3, "cardinalities must be 2 and 3 respectively")
    return {"order_a_support": sorted(r_a.support_ids), "order_b_support": sorted(r_b.support_ids)}


def check_k1_two_minimal_cores():
    """Same idea for inconsistency cores: adding A5=not(r) makes the full
    set unsatisfiable; two deletion orders reproduce both hand-derived
    minimal cores {A1,A4,A5} and {A1,A2,A3,A5}."""
    domain = _k1_domain()
    a1, a2, a3, a4, a5 = _k1_assumptions()

    order_a = [a1, a2, a3, a4, a5]
    r_a = find_minimal_inconsistent_core(domain, order_a)
    require(r_a.search_complete, "K1 core search (order A) must complete")
    require(
        set(r_a.core_ids) == {"A1_p", "A4_p_implies_r", "A5_not_r"},
        f"order A should land on {{A1,A4,A5}}, got {r_a.core_ids}",
    )

    order_b = [a1, a4, a2, a3, a5]
    r_b = find_minimal_inconsistent_core(domain, order_b)
    require(r_b.search_complete, "K1 core search (order B) must complete")
    require(
        set(r_b.core_ids) == {"A1_p", "A2_p_implies_q", "A3_q_implies_r", "A5_not_r"},
        f"order B should land on {{A1,A2,A3,A5}}, got {r_b.core_ids}",
    )
    require(set(r_a.core_ids) != set(r_b.core_ids), "the two orders must yield genuinely different cores")
    return {"order_a_core": sorted(r_a.core_ids), "order_b_core": sorted(r_b.core_ids)}


def check_deletion_witnesses_are_rechecked():
    """Every deletion step's `trial_report` is an independently produced
    `ClaimReport` for that exact trial subset -- re-evaluate the same
    subset directly and confirm it matches bit-for-bit, and confirm a
    `kept=True` step's report genuinely fails to entail (has a witness
    disproving entailment) while a `kept=False` step's report genuinely
    entails."""
    domain = _k1_domain()
    a1, a2, a3, a4, _a5 = _k1_assumptions()
    claim = _k1_claim()
    r = find_minimal_support(domain, [a1, a2, a3, a4], claim)
    require(len(r.steps) == 4, f"expected 4 deletion attempts (A1,A2,A3,A4 each tried once), got {len(r.steps)}")
    require(
        {s.assumption_id for s in r.steps if s.kept} == {"A1_p", "A4_p_implies_r"},
        f"A1 and A4 are essential in this order and must stay kept, got {[s.assumption_id for s in r.steps if s.kept]}",
    )
    for step in r.steps:
        require(step.trial_report.claim_id == claim.id, "trial_report must be for the same claim")
        if step.kept:
            require(
                step.trial_report.logical_status != "entailed_in_scope",
                f"a kept=True step must NOT show entailment, got {step.trial_report.logical_status}",
            )
        else:
            require(
                step.trial_report.logical_status == "entailed_in_scope",
                f"a kept=False (removed) step must show entailment, got {step.trial_report.logical_status}",
            )
    return {"n_steps": len(r.steps), "kept_ids": [s.assumption_id for s in r.steps if s.kept]}


def check_constant_true_claim_empty_support():
    """A claim that is true on every candidate needs NO assumptions at
    all -- the minimal support of the empty starting set is the empty
    set itself, not an error."""
    domain = FiniteDomainSpec(id="d5", candidates=tuple(range(5)), scope_text="0..4")
    claim_true = ClaimSpec(id="always_true", text="True", target=lambda w: True)
    r = find_minimal_support(domain, [], claim_true)
    require(r.search_complete, "empty-assumption search must complete")
    require(r.support_ids == (), f"expected empty support, got {r.support_ids}")
    require(len(r.steps) == 0, "nothing to try removing from an already-empty assumption set")
    return {"support_ids": r.support_ids}


def check_contradictory_starting_set_refused():
    """find_minimal_support must REFUSE to invent a support from a
    starting set that is already jointly unsatisfiable (n_admissible=0)
    -- support_ids stays None with an explanatory note, it is never
    silently treated as 'vacuously supports everything'."""
    domain = FiniteDomainSpec(id="d5b", candidates=tuple(range(5)), scope_text="0..4")
    a_lt2 = _assump("lt2", lambda w: w < 2)
    a_gt3 = _assump("gt3", lambda w: w > 3)
    claim = ClaimSpec(id="anything", text="True", target=lambda w: True)
    r = find_minimal_support(domain, [a_lt2, a_gt3], claim)
    require(r.support_ids is None, "a contradictory starting set must not produce a support")
    require(len(r.notes) > 0, "must explain why no support was produced")
    return {"support_ids": r.support_ids, "notes": r.notes}


def check_budget_abort_no_false_minimality():
    """With a subset_budget of 0, the deletion loop cannot try even the
    first candidate for removal, and with the base check consuming the
    single subset already, the search must abort with support_ids=None
    -- a budget abort must NEVER be reported as if it certified
    minimality."""
    domain = _k1_domain()
    a1, a2, a3, a4, _a5 = _k1_assumptions()
    claim = _k1_claim()
    r = find_minimal_support(domain, [a1, a2, a3, a4], claim, subset_budget=1)
    require(not r.search_complete, "subset_budget=1 must leave the search incomplete")
    require(r.support_ids is None, "an aborted search must not report any support as final")
    require(r.n_subsets_tried == 1, "only the base satisfiability/entailment check should have run")

    r_full = find_minimal_support(domain, [a1, a2, a3, a4], claim, subset_budget=10)
    require(r_full.search_complete and r_full.support_ids is not None, "a sufficient budget must still succeed")

    r_tiny_candidates = find_minimal_support(domain, [a1, a2, a3, a4], claim, candidate_budget=2)
    require(
        not r_tiny_candidates.search_complete and r_tiny_candidates.support_ids is None,
        "a too-small shared candidate-scan budget must also abort, not silently under-scan",
    )
    return {
        "subset_budget_1_status": (r.search_complete, r.support_ids),
        "subset_budget_10_status": (r_full.search_complete, r_full.support_ids),
        "candidate_budget_2_status": (r_tiny_candidates.search_complete, r_tiny_candidates.support_ids),
    }


def check_background_assumptions_never_removed_or_hidden():
    """A background assumption that is REQUIRED for entailment (without
    it, the claim is underdetermined) is applied on every trial but is
    never itself a removal candidate and never appears inside
    `support_ids` -- it is reported only in `background_ids`."""
    domain = _k1_domain()
    a1, a2, a3, a4, _a5 = _k1_assumptions()
    claim = _k1_claim()
    # a1 (p) moved to background: without it entailment breaks, so it must
    # stay applied throughout, yet never be a removal candidate nor show
    # up in support_ids.
    r = find_minimal_support(domain, [a2, a3, a4], claim, background=[a1])
    require(r.search_complete, "search with background must complete")
    require(r.background_ids == ("A1_p",), f"background_ids must list A1 unchanged, got {r.background_ids}")
    require("A1_p" not in r.support_ids, "background assumption must never appear inside support_ids")
    require(
        set(r.support_ids) == {"A4_p_implies_r"},
        f"with A1 fixed as background, deletable candidates reduce to {{A4}}, got {r.support_ids}",
    )
    return {"background_ids": r.background_ids, "support_ids": r.support_ids}


def check_r1_incomplete_removal_never_falsely_certifies_minimality():
    """Followup-Review-Fix R1 (SCF_REVIEW_H0_H7_9dde420.md): if a
    removal's re-check comes back `incomplete` (not a definite entailed/
    unsatisfiable verdict), that step's `kept` is `None` (unknown), NOT
    `True` (falsely 'confirmed necessary') -- and the whole result is
    flagged `minimality_verified=False`, never silently presented as a
    fully certified minimal support/core.

    Review's exact counterexamples: support W={0,1}, one everywhere-true
    assumption A, everywhere-true target C, candidate_budget=3 (the base
    check consumes 2, leaving only 1 for the removal re-check of A,
    which is then `incomplete`); core W={0,1}, A1 everywhere-false, A2
    everywhere-true, candidate_budget=5."""
    domain = FiniteDomainSpec(id="r1_w2", candidates=(0, 1), scope_text="{0,1}")
    A = _assump("A", lambda w: True)
    C = ClaimSpec(id="C_true", text="True", target=lambda w: True)
    r = find_minimal_support(domain, [A], C, candidate_budget=3)
    require(not r.minimality_verified, "an incomplete removal re-check must NOT be reported as verified-minimal")
    require(len(r.steps) == 1 and r.steps[0].kept is None, f"the inconclusive step's kept must be None, got {r.steps[0].kept if r.steps else 'no steps'}")
    require(r.steps[0].trial_report.logical_status == "incomplete", "the re-check itself must genuinely be incomplete")

    A1 = _assump("A1_false", lambda w: False)
    A2 = _assump("A2_true", lambda w: True)
    r_core = find_minimal_inconsistent_core(domain, [A1, A2], candidate_budget=5)
    require(not r_core.minimality_verified, "an incomplete core removal re-check must NOT be reported as verified-minimal")
    require(any(s.kept is None for s in r_core.steps), "at least one core-search step must be the unknown outcome")
    return {"support_minimality_verified": r.minimality_verified, "core_minimality_verified": r_core.minimality_verified}


def check_r6_duplicate_assumption_ids_rejected():
    """Followup-Review-Fix R6: two DIFFERENT predicates sharing the same
    id must be rejected up front, both within `assumptions` and across
    `assumptions`/`background` -- deletion-by-id would otherwise silently
    remove/keep several distinct predicates at once."""
    domain = FiniteDomainSpec(id="r6_w2", candidates=(0, 1), scope_text="{0,1}")
    dup1 = _assump("same", lambda w: w == 0)
    dup2 = _assump("same", lambda w: True)
    claim = ClaimSpec(id="c_r6", text="w==0", target=lambda w: w == 0)
    try:
        find_minimal_support(domain, [dup1, dup2], claim)
        raise AssertionError("duplicate ids within `assumptions` must raise")
    except ScopeViolationError:
        pass
    try:
        find_minimal_support(domain, [dup1], claim, background=[dup2])
        raise AssertionError("a duplicate id shared between `assumptions` and `background` must also raise")
    except ScopeViolationError:
        pass
    # A genuinely unique-id case must remain unaffected.
    unique_a = _assump("unique_a", lambda w: w == 0)
    r = find_minimal_support(domain, [unique_a], claim)
    require(r.support_ids == ("unique_a",), "a valid unique-id case must be unaffected by the new validation")
    return {"rejections_raised": True, "unique_case_support_ids": r.support_ids}


def check_r7_subset_budget_zero_blocks_base_check():
    """Followup-Review-Fix R7: `subset_budget=0` must block even the
    INITIAL base satisfiability/entailment check, not just the deletion
    loop -- previously an empty assumption list still got a 'complete'
    empty support back despite subset_budget=0."""
    domain = FiniteDomainSpec(id="r7_w2", candidates=(0, 1), scope_text="{0,1}")
    claim_true = ClaimSpec(id="c_r7", text="True", target=lambda w: True)
    r = find_minimal_support(domain, [], claim_true, subset_budget=0)
    require(r.n_subsets_tried == 0, f"subset_budget=0 must prevent even the base check from running, got n_subsets_tried={r.n_subsets_tried}")
    require(not r.search_complete and r.support_ids is None, "subset_budget=0 must abort, not return a 'complete' empty support")
    return {"n_subsets_tried": r.n_subsets_tried, "search_complete": r.search_complete}


CHECKS = [
    check_k1_two_minimal_supports,
    check_k1_two_minimal_cores,
    check_deletion_witnesses_are_rechecked,
    check_constant_true_claim_empty_support,
    check_contradictory_starting_set_refused,
    check_budget_abort_no_false_minimality,
    check_background_assumptions_never_removed_or_hidden,
    check_r1_incomplete_removal_never_falsely_certifies_minimality,
    check_r6_duplicate_assumption_ids_rejected,
    check_r7_subset_budget_zero_blocks_base_check,
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
    out_path = Path(__file__).with_name("verify_epistemic_supports_results.json")
    out_path.write_text(json.dumps({"n_passed": n_passed, "n_total": len(CHECKS), "results": results}, indent=2, default=str))
    print(f"Report written to {out_path}")
    return 0 if n_passed == len(CHECKS) else 1


if __name__ == "__main__":
    raise SystemExit(main())
