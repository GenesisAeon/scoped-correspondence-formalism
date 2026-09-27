"""H1: finite claim auditing (Plan §4.1, §8; `docs/epistemic_scope.md` §1).

`audit_finite_claim` is the executable form of the result table in
`docs/epistemic_scope.md`. It never converts an unevaluated or erroring
candidate into a silent `False`/exclusion, and never upgrades a
budget-truncated search into a universal or non-existence claim.

**Followup-Review-Fix (SCF_REVIEW_H0_H7_9dde420.md):**
- R2: witness presence is tracked via explicit `have_positive`/
  `have_negative` flags, never via `witness is None` -- a candidate
  value of `None` is a legitimate witness and must not collide with
  "no witness found".
- R3: every predicate call (assumption, target, antecedent) goes through
  `records.evaluate_bool`, which raises on anything but a literal
  `True`/`False` -- `None`, `NaN`, and truthy strings become recorded
  evaluation errors, never silently coerced truth values.
- R5: `all_candidates_scanned` is now a SEPARATE field from
  `search_complete` (a specific conclusion, e.g. `underdetermined` via
  the two-witness early exit, can be certain long before every candidate
  is scanned); `domain_coverage` carries `FiniteDomainSpec.coverage`
  through instead of dropping it.
- R7: a separate `evaluation_budget` caps the TOTAL number of individual
  predicate calls (assumptions + target + antecedent, across BOTH the
  main scan and the antecedent-reachability pass) -- distinct from
  `budget`, which continues to cap the number of CANDIDATES scanned,
  unchanged from before this fix (existing callers of `budget=` keep
  their exact prior meaning).
"""
from __future__ import annotations

from typing import Any, List, Optional, Sequence

from .records import ClaimReport, ClaimSpec, FiniteDomainSpec, PredicateEvaluationError, evaluate_bool

DEFAULT_BUDGET = 4096
DEFAULT_EVALUATION_BUDGET = 1_000_000


class _EvaluationBudgetExhausted(Exception):
    """Internal signal: the shared predicate-evaluation budget ran out
    mid-candidate. Caught at the outer scan loop; never escapes
    `audit_finite_claim`."""


def _make_spender(evaluation_budget: int):
    spent = [0]

    def spend() -> None:
        if spent[0] >= evaluation_budget:
            raise _EvaluationBudgetExhausted()
        spent[0] += 1

    return spend, spent


def audit_finite_claim(
    domain: FiniteDomainSpec,
    assumptions: Sequence,
    claim: ClaimSpec,
    *,
    budget: int = DEFAULT_BUDGET,
    evaluation_budget: int = DEFAULT_EVALUATION_BUDGET,
    evidence_kind: str = "exhaustive_finite",
    empirical_status: str = "not_tested",
) -> ClaimReport:
    """Evaluate `claim.target` over `{w in domain.candidates : all(a(w) for
    a in assumptions)}`, per the five-outcome table in
    `docs/epistemic_scope.md` §1.

    Early-exits once BOTH a positive and a negative witness are found
    (`underdetermined` is then certain regardless of the rest of the
    domain -- Plan §4.1). Otherwise scans up to `budget` candidates; if
    the budget is exhausted before the domain is exhausted,
    `search_complete=False` and `logical_status` is `"incomplete"`
    UNLESS the double-witness case already fired.

    `evaluation_budget` separately caps the TOTAL number of individual
    predicate calls (Plan §6.3) shared across the main scan AND the
    antecedent-reachability pass -- a nested/second pass never gets a
    fresh unbounded budget.

    A predicate exception or non-bool return (assumption, target, or
    antecedent) is counted in `n_errors` and that candidate is skipped --
    NOT treated as inadmissible, NOT treated as `False`.
    """
    n_domain = len(domain.candidates)
    n_evaluated = 0
    n_admissible = 0
    n_errors = 0
    positive_witness: Optional[Any] = None
    negative_witness: Optional[Any] = None
    have_positive = False
    have_negative = False
    had_error = False
    ran_out_of_budget = False
    ran_out_of_evaluation_budget = False
    notes: List[str] = []

    spend, spent_counter = _make_spender(evaluation_budget)

    for w in domain.candidates:
        if n_evaluated >= budget:
            ran_out_of_budget = True
            break
        try:
            admissible = True
            candidate_errored = False
            for a in assumptions:
                spend()
                try:
                    if not evaluate_bool(a.predicate, w):
                        admissible = False
                        break
                except PredicateEvaluationError:
                    n_errors += 1
                    had_error = True
                    candidate_errored = True
                    break
            n_evaluated += 1
            if candidate_errored or not admissible:
                continue
            n_admissible += 1
            spend()
            try:
                c_val = evaluate_bool(claim.target, w)
            except PredicateEvaluationError:
                n_errors += 1
                had_error = True
                continue
            if c_val:
                if not have_positive:
                    positive_witness = w
                    have_positive = True
            else:
                if not have_negative:
                    negative_witness = w
                    have_negative = True
            if have_positive and have_negative:
                break  # underdetermined is already certain -- no further scan needed
        except _EvaluationBudgetExhausted:
            ran_out_of_evaluation_budget = True
            break

    all_candidates_scanned = (n_evaluated == n_domain) and not ran_out_of_budget and not ran_out_of_evaluation_budget
    both_witnesses = have_positive and have_negative

    if both_witnesses:
        logical_status = "underdetermined"
        search_complete = True  # this specific conclusion is certain, regardless of what's unscanned
    elif not all_candidates_scanned or had_error:
        logical_status = "incomplete"
        search_complete = False
    elif n_admissible == 0:
        logical_status = "no_admissible_model_in_scope"
        search_complete = True
    elif not have_negative:
        logical_status = "entailed_in_scope"
        search_complete = True
    else:
        logical_status = "negation_entailed_in_scope"
        search_complete = True

    if ran_out_of_evaluation_budget:
        notes.append("evaluation_budget exhausted during the main scan")

    antecedent_reachable_in_scope = None
    vacuity_kind = None
    if claim.antecedent is not None and all_candidates_scanned and not had_error and n_admissible > 0:
        # S_{A,B} = {w in S_A : B(w)} -- Plan §4.2. Only meaningful to
        # assert emptiness/non-emptiness when the outer scan was complete
        # over a nonempty admissible set (a DIFFERENT case from
        # no_admissible_model_in_scope -- docs/epistemic_scope.md §2).
        reachable = False
        antecedent_had_error = False
        antecedent_budget_exhausted = False
        try:
            for w in domain.candidates:
                skip = False
                admissible = True
                for a in assumptions:
                    spend()
                    try:
                        if not evaluate_bool(a.predicate, w):
                            admissible = False
                            break
                    except PredicateEvaluationError:
                        antecedent_had_error = True
                        skip = True
                        break
                if skip or not admissible:
                    continue
                spend()
                try:
                    if evaluate_bool(claim.antecedent, w):
                        reachable = True
                        break
                except PredicateEvaluationError:
                    antecedent_had_error = True
                    continue
        except _EvaluationBudgetExhausted:
            antecedent_budget_exhausted = True

        if antecedent_budget_exhausted:
            antecedent_reachable_in_scope = None
            notes.append("antecedent reachability check aborted: evaluation_budget exhausted")
        elif antecedent_had_error and not reachable:
            antecedent_reachable_in_scope = None
            notes.append(
                "antecedent reachability check hit a predicate evaluation error before finding a "
                "witness -- result is unknown, NOT certified 'antecedent never holds'"
            )
        else:
            antecedent_reachable_in_scope = reachable
            if not reachable:
                vacuity_kind = "antecedent_never_holds"

    return ClaimReport(
        claim_id=claim.id,
        logical_status=logical_status,
        search_complete=search_complete,
        arithmetic_kind=domain.arithmetic_kind,
        n_domain=n_domain,
        n_evaluated=n_evaluated,
        n_admissible=n_admissible,
        n_errors=n_errors,
        positive_witness=positive_witness,
        negative_witness=negative_witness,
        n_predicate_evaluations=spent_counter[0],
        has_positive_witness=have_positive,
        has_negative_witness=have_negative,
        all_candidates_scanned=all_candidates_scanned,
        domain_coverage=domain.coverage,
        antecedent_reachable_in_scope=antecedent_reachable_in_scope,
        vacuity_kind=vacuity_kind,
        evidence_kind=evidence_kind,
        empirical_status=empirical_status,
        domain_relationship=domain.relationship_to_target_space,
        notes=tuple(notes),
    )
