"""H1: finite claim auditing (Plan §4.1, §8; `docs/epistemic_scope.md` §1).

`audit_finite_claim` is the executable form of the result table in
`docs/epistemic_scope.md`. It never converts an unevaluated or erroring
candidate into a silent `False`/exclusion, and never upgrades a
budget-truncated search into a universal or non-existence claim.
"""
from __future__ import annotations

from typing import Any, Optional, Sequence

from .records import ClaimReport, ClaimSpec, FiniteDomainSpec

DEFAULT_BUDGET = 1_000_000


def audit_finite_claim(
    domain: FiniteDomainSpec,
    assumptions: Sequence,
    claim: ClaimSpec,
    *,
    budget: int = DEFAULT_BUDGET,
    evidence_kind: str = "exhaustive_finite",
    empirical_status: str = "not_tested",
) -> ClaimReport:
    """Evaluate `claim.target` over `{w in domain.candidates : all(a(w) for
    a in assumptions)}`, per the five-outcome table in
    `docs/epistemic_scope.md` §1.

    Early-exits once BOTH a positive and a negative witness are found
    (`underdetermined` is then certain regardless of the rest of the
    domain -- Plan §4.1: "zwei gegensätzliche Zeugen belegen
    Unterbestimmtheit bereits ohne Vollständigkeit"). Otherwise scans up
    to `budget` candidates; if the budget is exhausted before the domain
    is exhausted, `search_complete=False` and `logical_status` is
    `"incomplete"` UNLESS the double-witness case already fired -- an
    incomplete search never yields `entailed_in_scope`,
    `negation_entailed_in_scope`, or `no_admissible_model_in_scope`,
    since any of those require certainty over candidates not yet seen.

    A predicate exception (assumption or claim) is counted in `n_errors`
    and that candidate is skipped -- NOT treated as inadmissible, NOT
    treated as `False`. If `n_errors > 0`, the search is also incomplete
    in this same sense (an error means that specific candidate's status
    was never actually determined), again unless the double-witness case
    already fired first.
    """
    n_domain = len(domain.candidates)
    n_evaluated = 0
    n_admissible = 0
    n_errors = 0
    positive_witness: Optional[Any] = None
    negative_witness: Optional[Any] = None
    had_error = False
    ran_out_of_budget = False

    for w in domain.candidates:
        if n_evaluated >= budget:
            ran_out_of_budget = True
            break
        n_evaluated += 1
        try:
            admissible = all(bool(a.predicate(w)) for a in assumptions)
        except Exception:
            n_errors += 1
            had_error = True
            continue
        if not admissible:
            continue
        n_admissible += 1
        try:
            c_val = claim.target(w)
        except Exception:
            n_errors += 1
            had_error = True
            continue
        if not isinstance(c_val, bool):
            n_errors += 1
            had_error = True
            continue
        if c_val:
            if positive_witness is None:
                positive_witness = w
        else:
            if negative_witness is None:
                negative_witness = w
        if positive_witness is not None and negative_witness is not None:
            break  # underdetermined is already certain -- no further scan needed

    scanned_everything = (n_evaluated == n_domain) and not ran_out_of_budget
    both_witnesses = positive_witness is not None and negative_witness is not None

    if both_witnesses:
        logical_status = "underdetermined"
        search_complete = True  # this specific conclusion is certain, regardless of what's unscanned
    elif not scanned_everything or had_error:
        logical_status = "incomplete"
        search_complete = False
    elif n_admissible == 0:
        logical_status = "no_admissible_model_in_scope"
        search_complete = True
    elif negative_witness is None:
        logical_status = "entailed_in_scope"
        search_complete = True
    else:
        logical_status = "negation_entailed_in_scope"
        search_complete = True

    antecedent_reachable_in_scope = None
    vacuity_kind = None
    if claim.antecedent is not None:
        # S_{A,B} = {w in S_A : B(w)} -- Plan §4.2. Only meaningful to
        # assert emptiness/non-emptiness when the outer scan was complete
        # over the admissible set AND that set is nonempty -- an empty
        # S_A is a DIFFERENT case (no_admissible_model_in_scope, contra-
        # dictory assumptions), not a vacuous antecedent, so the vacuity
        # check is skipped (None) rather than guessed there too
        # (`docs/epistemic_scope.md` §2: distinct from contradictory
        # assumptions overall).
        if scanned_everything and not had_error and n_admissible > 0:
            reachable = False
            for w in domain.candidates:
                if all(bool(a.predicate(w)) for a in assumptions) and bool(claim.antecedent(w)):
                    reachable = True
                    break
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
        antecedent_reachable_in_scope=antecedent_reachable_in_scope,
        vacuity_kind=vacuity_kind,
        evidence_kind=evidence_kind,
        empirical_status=empirical_status,
        domain_relationship=domain.relationship_to_target_space,
    )
