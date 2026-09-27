#!/usr/bin/env python3
"""Independent checks for H1 finite claim auditing (Plan §4.1/§4.2, §8).

Content basis: `SCF_ASSUMPTION_EVIDENCE_IMPLEMENTATION_PLAN.md` §8 and
`docs/epistemic_scope.md` §1-2. Purely synthetic/analytic (category "math").
K2 and K3 are the plan's own hand-derivable control cases, independently
re-verified in `EPISTEMIC_AUDIT_ROADMAP.md`'s H0 section before this code
was written.
"""
from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from scoped_correspondence.epistemic import (  # noqa: E402
    AssumptionSpec,
    ClaimSpec,
    FiniteDomainSpec,
    audit_finite_claim,
)


def require(ok, msg):
    if not bool(ok):
        raise AssertionError(msg)


def _assump(id_, pred, role="structural"):
    return AssumptionSpec(id=id_, text=id_, role=role, predicate=pred)


# ---------------------------------------------------------------------------
def check_four_complete_outcomes():
    """Plan §4.1's full table, each with `search_complete=True`."""
    domain = FiniteDomainSpec(id="bits3", candidates=tuple(range(8)), scope_text="3-bit int 0..7")

    # no_admissible_model_in_scope: assumption p AND not p (bit0==1 and bit0==0)
    a_contra = [_assump("p", lambda w: w & 1 == 1), _assump("notp", lambda w: w & 1 == 0)]
    claim = ClaimSpec(id="any", text="true", target=lambda w: True)
    r = audit_finite_claim(domain, a_contra, claim)
    require(r.logical_status == "no_admissible_model_in_scope", r.logical_status)
    require(r.search_complete, "expected complete search")
    require(r.n_admissible == 0, "expected zero admissible candidates")

    # entailed_in_scope: A = {w even}, C = {w < 8} always true on evens
    a_even = [_assump("even", lambda w: w % 2 == 0)]
    claim_lt8 = ClaimSpec(id="lt8", text="w<8", target=lambda w: w < 8)
    r2 = audit_finite_claim(domain, a_even, claim_lt8)
    require(r2.logical_status == "entailed_in_scope", r2.logical_status)
    require(r2.negative_witness is None and r2.positive_witness is not None, "entailed_in_scope witnesses")

    # negation_entailed_in_scope: A = {w even}, C = {w odd} never true on evens
    claim_odd = ClaimSpec(id="odd", text="w odd", target=lambda w: w % 2 == 1)
    r3 = audit_finite_claim(domain, a_even, claim_odd)
    require(r3.logical_status == "negation_entailed_in_scope", r3.logical_status)
    require(r3.positive_witness is None and r3.negative_witness is not None, "negation_entailed_in_scope witnesses")

    # underdetermined: A = {w < 6}, C = {w even} -- mixed on {0,1,2,3,4,5}
    a_lt6 = [_assump("lt6", lambda w: w < 6)]
    r4 = audit_finite_claim(domain, a_lt6, claim_lt8.__class__(id="even2", text="even", target=lambda w: w % 2 == 0))
    require(r4.logical_status == "underdetermined", r4.logical_status)
    require(r4.positive_witness is not None and r4.negative_witness is not None, "underdetermined needs both witnesses")

    return {"no_admissible": r.logical_status, "entailed": r2.logical_status,
            "negation": r3.logical_status, "underdetermined": r4.logical_status}


def check_counterexample_does_not_auto_prove_negation():
    """A negative witness refutes `entailed_in_scope`, but must not be
    silently upgraded to `negation_entailed_in_scope` when a positive
    witness ALSO exists -- order of the domain must not change the
    outcome (scanned reverse order here vs check_four_complete_outcomes)."""
    domain_rev = FiniteDomainSpec(id="bits3_rev", candidates=tuple(range(7, -1, -1)), scope_text="reverse order")
    a_lt6 = [_assump("lt6", lambda w: w < 6)]
    claim_even = ClaimSpec(id="even3", text="even", target=lambda w: w % 2 == 0)
    r = audit_finite_claim(domain_rev, a_lt6, claim_even)
    require(r.logical_status == "underdetermined", f"order should not change the outcome, got {r.logical_status}")
    return {"ok": True}


def check_empty_input_vs_empty_admissible_set():
    """Empty candidate tuple is an INPUT ERROR (raises); a nonempty domain
    where assumptions exclude everyone is a genuine RESULT."""
    try:
        FiniteDomainSpec(id="empty", candidates=(), scope_text="empty")
        raise AssertionError("expected ValueError for empty candidates")
    except ValueError:
        pass

    domain = FiniteDomainSpec(id="single", candidates=(1,), scope_text="one candidate")
    a_impossible = [_assump("gt10", lambda w: w > 10)]
    claim = ClaimSpec(id="any", text="true", target=lambda w: True)
    r = audit_finite_claim(domain, a_impossible, claim)
    require(r.logical_status == "no_admissible_model_in_scope", "nonempty domain, all excluded -> a real result")
    return {"ok": True}


def check_k2_vacuous_antecedent():
    """K2: A={not p}. p=>q holds on all of S_A, but p never holds there --
    antecedent_reachable_in_scope=False, vacuity_kind=antecedent_never_holds.
    Separately, A={p, not p} gives no_admissible_model_in_scope."""
    import itertools
    W = list(itertools.product([0, 1], repeat=3))  # (p,q,r)
    domain = FiniteDomainSpec(id="pqr", candidates=tuple(W), scope_text="K2 (p,q,r)")

    a_notp = [_assump("notp", lambda w: w[0] == 0)]
    claim_pq = ClaimSpec(id="p_implies_q", text="p=>q", target=lambda w: (not w[0]) or w[1],
                          antecedent=lambda w: bool(w[0]))
    r = audit_finite_claim(domain, a_notp, claim_pq)
    require(r.logical_status == "entailed_in_scope", f"p=>q should hold everywhere on notp, got {r.logical_status}")
    require(r.antecedent_reachable_in_scope is False, "p should never hold when A={not p}")
    require(r.vacuity_kind == "antecedent_never_holds", r.vacuity_kind)

    a_contra = [_assump("p", lambda w: w[0] == 1), _assump("notp2", lambda w: w[0] == 0)]
    r2 = audit_finite_claim(domain, a_contra, claim_pq)
    require(r2.logical_status == "no_admissible_model_in_scope", r2.logical_status)
    require(r2.antecedent_reachable_in_scope is None, "vacuity check skipped when S_A itself is empty")
    return {"vacuity_kind": r.vacuity_kind}


def check_k3_scope_extension_refutes():
    """K3: x^2<=1 holds on W={-1,0,1}; W'={-1,0,1,2} yields the exact
    counterexample x=2. `domain_relationship` field must be present so a
    caller can see this is `entire_finite_space`, not silently promoted to
    a claim about the full integers or reals."""
    domain_w = FiniteDomainSpec(id="W", candidates=(-1, 0, 1), scope_text="K3 W")
    domain_wp = FiniteDomainSpec(id="Wp", candidates=(-1, 0, 1, 2), scope_text="K3 W'")
    claim = ClaimSpec(id="x2le1", text="x^2<=1", target=lambda x: x * x <= 1)

    r = audit_finite_claim(domain_w, [], claim)
    require(r.logical_status == "entailed_in_scope", r.logical_status)
    require(r.domain_relationship == "entire_finite_space", r.domain_relationship)

    r2 = audit_finite_claim(domain_wp, [], claim)
    require(r2.logical_status == "negation_entailed_in_scope" or r2.logical_status == "underdetermined",
            f"expected a negative witness to appear on W', got {r2.logical_status}")
    require(r2.negative_witness == 2, f"expected the exact counterexample x=2, got {r2.negative_witness}")
    return {"counterexample": r2.negative_witness}


def check_grid_of_continuous_space_flagged():
    """A domain declared as a grid over a continuous space must carry that
    label through to the report -- callers/documentation are responsible
    for never treating it as a global statement (Plan §4.1, Alloy S3)."""
    domain = FiniteDomainSpec(id="grid", candidates=(0.0, 0.5, 1.0), scope_text="grid sample",
                               relationship_to_target_space="grid_of_continuous_space")
    claim = ClaimSpec(id="nonneg", text="x>=0", target=lambda x: x >= 0.0)
    r = audit_finite_claim(domain, [], claim)
    require(r.domain_relationship == "grid_of_continuous_space", r.domain_relationship)
    require(r.logical_status == "entailed_in_scope", "the scope-local result itself is still valid")
    return {"domain_relationship": r.domain_relationship}


def check_abort_before_after_witnesses():
    """budget=0: abort before any evaluation -> incomplete, no witnesses.
    budget=1: sees exactly one candidate (a positive witness) -> still
    incomplete (can't certify entailment from a partial scan).
    budget=2 sees BOTH a positive and a negative witness (candidates 0
    and 1) before the budget itself would have run out -- the early-exit
    fires first, so this is `underdetermined` (already certain), not
    `incomplete` (Plan §4.1: "zwei gegensätzliche Zeugen belegen
    Unterbestimmtheit bereits ohne Vollständigkeit").
    A separately constructed case (reordered domain, only-even prefix)
    demonstrates the genuinely different situation where a witness is
    seen and THEN the budget runs out before the opposite witness is
    ever found: that one stays `incomplete`, but the witness already
    found is still reported (already-found witnesses stay meaningful)."""
    domain = FiniteDomainSpec(id="d10", candidates=tuple(range(10)), scope_text="0..9")
    claim_even = ClaimSpec(id="even4", text="even", target=lambda w: w % 2 == 0)

    r0 = audit_finite_claim(domain, [], claim_even, budget=0)
    require(r0.logical_status == "incomplete", r0.logical_status)
    require(not r0.search_complete, "budget=0 must not be search_complete")
    require(r0.positive_witness is None and r0.negative_witness is None, "budget=0 sees no candidates")

    r1 = audit_finite_claim(domain, [], claim_even, budget=1)
    require(r1.logical_status == "incomplete", r1.logical_status)
    require(r1.positive_witness == 0, "the one evaluated candidate (0) is even -> positive witness")
    require(r1.negative_witness is None, "budget=1 only sees candidate 0")

    r2 = audit_finite_claim(domain, [], claim_even, budget=2)
    require(r2.logical_status == "underdetermined",
            f"both witnesses found within budget=2 is certain underdetermined, got {r2.logical_status}")
    require(r2.search_complete, "the underdetermined conclusion itself is certain even though budget=2 < n_domain")
    require(r2.positive_witness == 0 and r2.negative_witness == 1,
            "candidates 0 and 1 give one witness of each kind within budget=2")

    domain_prefix_even = FiniteDomainSpec(
        id="d10_even_prefix", candidates=(0, 2, 4, 6, 8, 1, 3, 5, 7, 9), scope_text="evens then odds"
    )
    r3 = audit_finite_claim(domain_prefix_even, [], claim_even, budget=3)
    require(r3.logical_status == "incomplete",
            f"budget runs out after only a positive witness, before any negative one, got {r3.logical_status}")
    require(not r3.search_complete, "budget=3 exhausted before scanning the odd suffix")
    require(r3.positive_witness == 0 and r3.negative_witness is None,
            "only the even prefix was scanned before the budget ran out")

    return {
        "budget0": r0.logical_status,
        "budget1": r1.logical_status,
        "budget2": r2.logical_status,
        "budget3_even_prefix": r3.logical_status,
    }


def check_reproducible_witnesses_stable_ids():
    """Re-running the same audit gives bit-identical witnesses and status
    (no hidden randomness), and re-evaluating the assumptions on the
    reported witness directly confirms it independently."""
    domain = FiniteDomainSpec(id="d20", candidates=tuple(range(20)), scope_text="0..19")
    a = [_assump("lt15", lambda w: w < 15)]
    claim = ClaimSpec(id="ge10", text="w>=10", target=lambda w: w >= 10)
    r1 = audit_finite_claim(domain, a, claim)
    r2 = audit_finite_claim(domain, a, claim)
    require(r1.logical_status == r2.logical_status, "must be deterministic")
    require(r1.positive_witness == r2.positive_witness and r1.negative_witness == r2.negative_witness, "deterministic witnesses")
    if r1.positive_witness is not None:
        w = r1.positive_witness
        require(all(x.predicate(w) for x in a), "reported positive witness must independently satisfy all assumptions")
        require(claim.target(w) is True, "reported positive witness must independently satisfy the claim")
    return {"status": r1.logical_status}


def check_predicate_error_stays_error_not_silent_removal():
    """A candidate whose predicate raises is counted as an error and the
    search is forced incomplete -- it is NEVER silently treated as
    inadmissible (which would let a real negative witness disappear and
    falsely yield entailed_in_scope)."""
    domain = FiniteDomainSpec(id="d5", candidates=(0, 1, 2, 3, 4), scope_text="0..4")

    def flaky_claim(w):
        if w == 3:
            raise ZeroDivisionError("boom")
        return True  # every OTHER candidate satisfies the claim

    claim = ClaimSpec(id="flaky", text="flaky", target=flaky_claim)
    r = audit_finite_claim(domain, [], claim)
    require(r.n_errors == 1, f"expected exactly 1 error, got {r.n_errors}")
    require(r.logical_status == "incomplete",
            f"a predicate error must force 'incomplete', not a false 'entailed_in_scope', got {r.logical_status}")
    require(r.positive_witness is not None, "the non-erroring candidates should still yield a positive witness")
    return {"n_errors": r.n_errors, "status": r.logical_status}


def check_r2_none_candidate_does_not_collide_with_no_witness_sentinel():
    """Followup-Review-Fix R2 (SCF_REVIEW_H0_H7_9dde420.md): `None` is a
    legitimate candidate value and must not be confused with "no witness
    found" -- `has_positive_witness`/`has_negative_witness` track presence
    independently of the witness's own value."""
    d1 = FiniteDomainSpec(id="r2_d1", candidates=(None,), scope_text="(None,)")
    c1 = ClaimSpec(id="r2_c1", text="False", target=lambda w: False)
    r1 = audit_finite_claim(d1, [], c1)
    require(r1.logical_status == "negation_entailed_in_scope", f"W=(None,), C=False must be negation_entailed_in_scope, got {r1.logical_status}")
    require(r1.has_negative_witness and r1.negative_witness is None, "the witness value None must still be recognized as a FOUND witness")

    d2 = FiniteDomainSpec(id="r2_d2", candidates=(None, 0), scope_text="(None,0)")
    c2 = ClaimSpec(id="r2_c2", text="w is not None", target=lambda w: w is not None)
    r2 = audit_finite_claim(d2, [], c2)
    require(r2.logical_status == "underdetermined", f"W=(None,0) must be underdetermined, got {r2.logical_status}")
    require(r2.has_positive_witness and r2.has_negative_witness, "both witnesses must be recognized as found")

    d3 = FiniteDomainSpec(id="r2_d3", candidates=(0, None), scope_text="(0,None)")
    r3 = audit_finite_claim(d3, [], c2)
    require(r3.logical_status == "underdetermined", f"W=(0,None) must also be underdetermined, got {r3.logical_status}")
    return {"r2_d1_status": r1.logical_status, "r2_d2_status": r2.logical_status, "r2_d3_status": r3.logical_status}


def check_r3_invalid_predicate_returns_become_errors_not_truth():
    """Followup-Review-Fix R3: an assumption/antecedent returning `None`,
    `float("nan")`, or a truthy non-empty string must be an evaluation
    error, never silently coerced into `True` via `bool(...)`."""
    domain = FiniteDomainSpec(id="r3_d", candidates=(0, 1, 2), scope_text="{0,1,2}")
    claim_true = ClaimSpec(id="r3_true", text="True", target=lambda w: True)

    r_none = audit_finite_claim(domain, [_assump("a_none", lambda w: None)], claim_true)
    require(r_none.n_errors == 3 and r_none.n_admissible == 0, f"assumption returning None must error on every candidate, got n_errors={r_none.n_errors}, n_admissible={r_none.n_admissible}")

    r_nan = audit_finite_claim(domain, [_assump("a_nan", lambda w: float("nan"))], claim_true)
    require(r_nan.n_errors == 3 and r_nan.n_admissible == 0, f"assumption returning NaN must error (NaN is truthy in Python), got n_errors={r_nan.n_errors}")

    r_str = audit_finite_claim(domain, [_assump("a_str", lambda w: "false")], claim_true)
    require(r_str.n_errors == 3 and r_str.n_admissible == 0, f"assumption returning the string 'false' must error (non-empty string is truthy), got n_errors={r_str.n_errors}")

    claim_ant_none = ClaimSpec(id="r3_ant_none", text="True", target=lambda w: True, antecedent=lambda w: None)
    r_ant = audit_finite_claim(domain, [], claim_ant_none)
    require(r_ant.antecedent_reachable_in_scope is None, f"an erroring antecedent must yield antecedent_reachable_in_scope=None, not a false-certified 'never holds', got {r_ant.antecedent_reachable_in_scope}")
    require(r_ant.vacuity_kind is None, "vacuity_kind must not be set from an antecedent evaluation error")
    return {"none_errors": r_none.n_errors, "nan_errors": r_nan.n_errors, "str_errors": r_str.n_errors, "antecedent_reachable": r_ant.antecedent_reachable_in_scope}


def check_r5_all_candidates_scanned_separate_from_search_complete():
    """Followup-Review-Fix R5: `search_complete` (this conclusion is
    certain) and `all_candidates_scanned` (every candidate was actually
    scanned) are separate fields -- the two-witness early exit can make
    the former True while the latter is False."""
    domain = FiniteDomainSpec(id="r5_d10", candidates=tuple(range(10)), scope_text="0..9")
    claim_even = ClaimSpec(id="r5_even", text="even", target=lambda w: w % 2 == 0)
    r = audit_finite_claim(domain, [], claim_even, budget=2)
    require(r.logical_status == "underdetermined" and r.search_complete, "budget=2 must still certify underdetermined")
    require(not r.all_candidates_scanned, f"only 2 of 10 candidates were scanned, all_candidates_scanned must be False, got {r.all_candidates_scanned}")
    require(r.n_evaluated == 2 and r.n_domain == 10, "n_evaluated/n_domain must show the actual partial scan size")

    domain_partial = FiniteDomainSpec(id="r5_partial", candidates=(0, 1, 2), scope_text="partial sample", coverage="partial")
    r_partial = audit_finite_claim(domain_partial, [], ClaimSpec(id="r5_true", text="True", target=lambda w: True))
    require(r_partial.domain_coverage == "partial", f"domain_coverage must be carried through from FiniteDomainSpec, got {r_partial.domain_coverage}")
    return {"all_candidates_scanned": r.all_candidates_scanned, "domain_coverage": r_partial.domain_coverage}


def check_r7_evaluation_budget_caps_total_predicate_calls():
    """Followup-Review-Fix R7: `evaluation_budget` caps the TOTAL number
    of individual predicate calls (assumptions + target), separately
    from `budget` (candidates scanned)."""
    domain = FiniteDomainSpec(id="r7_d3", candidates=(0, 1, 2), scope_text="{0,1,2}")
    a_true = _assump("r7_a", lambda w: True)
    claim_true = ClaimSpec(id="r7_true", text="True", target=lambda w: True)
    # Each candidate costs 2 predicate calls (1 assumption + 1 target); 3
    # candidates would need 6 total -- capping evaluation_budget at 3
    # must abort partway through, well before the candidate budget (4096
    # default) would ever intervene.
    r = audit_finite_claim(domain, [a_true], claim_true, evaluation_budget=3)
    require(not r.search_complete, f"evaluation_budget=3 must abort before all 3 candidates are fully resolved, got search_complete={r.search_complete}")
    require(r.n_predicate_evaluations <= 3, f"n_predicate_evaluations must respect the evaluation_budget cap, got {r.n_predicate_evaluations}")
    require(r.n_evaluated < 3, f"fewer than all 3 candidates should have been fully resolved, got n_evaluated={r.n_evaluated}")

    r_full = audit_finite_claim(domain, [a_true], claim_true, evaluation_budget=1_000_000)
    require(r_full.search_complete and r_full.n_evaluated == 3, "a generous evaluation_budget must still complete normally")
    return {"tiny_budget_n_evaluated": r.n_evaluated, "tiny_budget_n_predicate_evaluations": r.n_predicate_evaluations}


CHECKS = [
    ("four_complete_outcomes", check_four_complete_outcomes),
    ("counterexample_does_not_auto_prove_negation", check_counterexample_does_not_auto_prove_negation),
    ("empty_input_vs_empty_admissible_set", check_empty_input_vs_empty_admissible_set),
    ("k2_vacuous_antecedent", check_k2_vacuous_antecedent),
    ("k3_scope_extension_refutes", check_k3_scope_extension_refutes),
    ("grid_of_continuous_space_flagged", check_grid_of_continuous_space_flagged),
    ("abort_before_after_witnesses", check_abort_before_after_witnesses),
    ("reproducible_witnesses_stable_ids", check_reproducible_witnesses_stable_ids),
    ("predicate_error_stays_error_not_silent_removal", check_predicate_error_stays_error_not_silent_removal),
    ("r2_none_candidate_does_not_collide_with_no_witness_sentinel", check_r2_none_candidate_does_not_collide_with_no_witness_sentinel),
    ("r3_invalid_predicate_returns_become_errors_not_truth", check_r3_invalid_predicate_returns_become_errors_not_truth),
    ("r5_all_candidates_scanned_separate_from_search_complete", check_r5_all_candidates_scanned_separate_from_search_complete),
    ("r7_evaluation_budget_caps_total_predicate_calls", check_r7_evaluation_budget_caps_total_predicate_calls),
]


def main() -> int:
    report = {
        "package": "EPISTEMIC_AUDIT_ROADMAP.md Paket H1 (finite claims, synthetic/analytic only)",
        "timestamp": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "python": sys.version.split()[0],
        "checks": {},
    }
    all_ok = True
    for name, fn in CHECKS:
        try:
            detail = fn()
            report["checks"][name] = {"status": "pass", "detail": detail}
            print(f"PASS  {name}")
        except AssertionError as e:
            all_ok = False
            report["checks"][name] = {"status": "fail", "error": str(e)}
            print(f"FAIL  {name}: {e}")
        except Exception as e:  # noqa: BLE001
            all_ok = False
            report["checks"][name] = {"status": "error", "error": f"{type(e).__name__}: {e}"}
            print(f"ERROR {name}: {type(e).__name__}: {e}")

    out = Path(__file__).with_name("verify_epistemic_finite_results.json")
    out.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    print(f"\n{sum(1 for c in report['checks'].values() if c['status'] == 'pass')}/{len(CHECKS)} checks passed")
    print(f"Report written to {out}")
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
