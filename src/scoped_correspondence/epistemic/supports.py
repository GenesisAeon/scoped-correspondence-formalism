"""H2: minimal supports and inconsistency cores (Plan §4.3, §6.2; S6:
Marques-Silva & Janota, subset-minimal != smallest cardinality).

`find_minimal_support` and `find_minimal_inconsistent_core` both use the
same deletion procedure: start from a starting set that already has the
required property (satisfiable-and-entails-C for a support; jointly
unsatisfiable for a core -- Plan §4.3: "Ein Löschverfahren darf für den
Support nur von einer erfüllbaren, bereits tragenden Ausgangsmenge
starten"), then try removing each assumption in the exact order the
caller supplied `assumptions`, keeping the removal only if the property
still holds afterward. Each removal attempt is independently re-checked
via `audit_finite_claim` and its full `ClaimReport` (including its
witness) is kept in the step trace -- never just a boolean.

Subset-minimal is NOT smallest-cardinality: trying assumptions in a
different order can (and for K1, deliberately does) land on a different,
equally valid minimal support/core. Callers who want a specific one of
several alternatives choose the order; there is no hidden "find all"
mode (Plan §4.3: "Standardmäßig reicht ein deterministisch gefundener
minimaler Support/Kern").

`background` assumptions are always applied but are never candidates for
removal, and are always reported separately (`background_ids`) -- they
must never be silently folded into, or hidden from, the reported
"minimal" result (Plan §4.3, last sentence).

Both searches share a running candidate-scan budget AND a running
predicate-evaluation budget across every nested `audit_finite_claim`
call (Plan §6.3: "Die Gesamtgrenze gilt auch über verschachtelte
Supportprüfungen hinweg"), plus a separate cap on how many assumption
subsets are tried in total -- `subset_budget=0` blocks even the initial
base check, it is not a "the deletion loop never starts but the base
check still runs" carve-out.

**Followup-Review-Fix (SCF_REVIEW_H0_H7_9dde420.md):**
- R1: a removal decision has THREE possible outcomes, not two --
  confirmed removable, confirmed necessary, or UNKNOWN (the re-check
  itself was `incomplete`). An unknown outcome is conservatively kept
  (never silently treated as "must keep" in a way that still claims full
  minimality) and marks the whole result `minimality_verified=False`.
- R6: duplicate assumption IDs (across `assumptions` and `background`
  together) are rejected up front -- deletion-by-ID would otherwise
  remove several distinct predicates that happen to share an ID at once,
  silently hiding redundancy.
- R7: `subset_budget`, `candidate_budget`, and `evaluation_budget` are
  three separately configurable limits; `subset_budget=0` now also
  blocks the base check, and `evaluation_budget` is shared across every
  nested `audit_finite_claim` call via `ClaimReport.n_predicate_evaluations`.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Sequence, Tuple

from scoped_correspondence.errors import ScopeViolationError

from .finite import audit_finite_claim
from .records import AssumptionSpec, ClaimReport, ClaimSpec, FiniteDomainSpec

DEFAULT_SUBSET_BUDGET = 4096
DEFAULT_CANDIDATE_BUDGET = 4096
DEFAULT_EVALUATION_BUDGET = 1_000_000

#: Used internally by `find_minimal_inconsistent_core` to probe pure
#: satisfiability via `audit_finite_claim` without needing a caller-
#: supplied claim -- an always-true target never produces a negative
#: witness, so the resulting `logical_status` reduces to exactly
#: `no_admissible_model_in_scope` (S_A empty) vs. `entailed_in_scope`
#: (S_A nonempty) vs. `incomplete` (budget ran out).
_SATISFIABILITY_PROBE = ClaimSpec(id="_satisfiability_probe", text="w -> True", target=lambda w: True)


def _validate_unique_ids(assumptions: Sequence[AssumptionSpec], background: Sequence[AssumptionSpec]) -> None:
    seen = {}
    for a in list(background) + list(assumptions):
        if a.id in seen and seen[a.id] is not a:
            raise ScopeViolationError(
                f"duplicate assumption id {a.id!r}: assumption ids must be unique across `assumptions` and "
                "`background` together -- a deletion search removes/keeps assumptions BY id, so a shared id "
                "would silently act on every assumption carrying it at once"
            )
        seen[a.id] = a


@dataclass(frozen=True)
class DeletionStep:
    """One tentative removal in the deletion search, with its own
    independently re-checked `ClaimReport` as the concrete witness
    (Plan §4.3: "Für jede Entfernung muss ein konkreter Zeuge
    ausgegeben und erneut geprüft werden").

    `kept` is a TRI-STATE outcome (SCF_REVIEW_H0_H7_9dde420.md R1):
    `False` = confirmed removable, `True` = confirmed necessary, `None`
    = unknown (the re-check itself came back `incomplete` -- the
    assumption is conservatively kept, but this does NOT certify it is
    actually necessary)."""

    assumption_id: str
    kept: Optional[bool]
    trial_report: ClaimReport


@dataclass(frozen=True)
class SupportReport:
    claim_id: str
    starting_ids: Tuple[str, ...]
    background_ids: Tuple[str, ...]
    support_ids: Optional[Tuple[str, ...]]
    steps: Tuple[DeletionStep, ...]
    search_complete: bool
    minimality_verified: bool
    n_subsets_tried: int
    n_candidate_scans_used: int
    n_predicate_evaluations_used: int
    domain_coverage: str = "complete"
    notes: Tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class InconsistentCoreReport:
    starting_ids: Tuple[str, ...]
    background_ids: Tuple[str, ...]
    core_ids: Optional[Tuple[str, ...]]
    steps: Tuple[DeletionStep, ...]
    search_complete: bool
    minimality_verified: bool
    n_subsets_tried: int
    n_candidate_scans_used: int
    n_predicate_evaluations_used: int
    domain_coverage: str = "complete"
    notes: Tuple[str, ...] = field(default_factory=tuple)


def find_minimal_support(
    domain: FiniteDomainSpec,
    assumptions: Sequence[AssumptionSpec],
    claim: ClaimSpec,
    *,
    background: Sequence[AssumptionSpec] = (),
    subset_budget: int = DEFAULT_SUBSET_BUDGET,
    candidate_budget: int = DEFAULT_CANDIDATE_BUDGET,
    evaluation_budget: int = DEFAULT_EVALUATION_BUDGET,
) -> SupportReport:
    _validate_unique_ids(assumptions, background)
    starting_ids = tuple(a.id for a in assumptions)
    background_ids = tuple(a.id for a in background)
    remaining_candidates = candidate_budget
    remaining_evaluations = evaluation_budget
    n_subsets_tried = 0

    def check(subset) -> Optional[ClaimReport]:
        nonlocal remaining_candidates, remaining_evaluations, n_subsets_tried
        if n_subsets_tried >= subset_budget or remaining_candidates <= 0 or remaining_evaluations <= 0:
            return None
        n_subsets_tried += 1
        report = audit_finite_claim(
            domain, list(background) + list(subset), claim, budget=remaining_candidates, evaluation_budget=remaining_evaluations,
        )
        remaining_candidates -= report.n_evaluated
        remaining_evaluations -= report.n_predicate_evaluations
        return report

    def budget_exhausted_report(steps, minimality_verified) -> SupportReport:
        return SupportReport(
            claim_id=claim.id, starting_ids=starting_ids, background_ids=background_ids,
            support_ids=None, steps=tuple(steps), search_complete=False, minimality_verified=minimality_verified,
            n_subsets_tried=n_subsets_tried,
            n_candidate_scans_used=candidate_budget - remaining_candidates,
            n_predicate_evaluations_used=evaluation_budget - remaining_evaluations,
            domain_coverage=domain.coverage,
            notes=("budget exhausted before the deletion search finished",),
        )

    survivors = list(assumptions)
    base_report = check(survivors)
    if base_report is None:
        return budget_exhausted_report([], True)
    if base_report.logical_status != "entailed_in_scope":
        return SupportReport(
            claim_id=claim.id, starting_ids=starting_ids, background_ids=background_ids,
            support_ids=None, steps=(), search_complete=base_report.search_complete, minimality_verified=True,
            n_subsets_tried=n_subsets_tried,
            n_candidate_scans_used=candidate_budget - remaining_candidates,
            n_predicate_evaluations_used=evaluation_budget - remaining_evaluations,
            domain_coverage=domain.coverage,
            notes=(
                f"starting set does not entail the claim in scope (status={base_report.logical_status}); "
                "a deletion search requires an already satisfiable, already-entailing starting set",
            ),
        )

    steps = []
    minimality_verified = True
    for a in assumptions:
        if a.id not in {x.id for x in survivors}:
            continue  # already removed in an earlier step
        trial = [x for x in survivors if x.id != a.id]
        trial_report = check(trial)
        if trial_report is None:
            return budget_exhausted_report(steps, minimality_verified)
        if trial_report.logical_status == "entailed_in_scope":
            kept = False
            survivors = trial
        elif trial_report.logical_status == "incomplete":
            kept = None
            minimality_verified = False
        else:
            kept = True
        steps.append(DeletionStep(assumption_id=a.id, kept=kept, trial_report=trial_report))

    return SupportReport(
        claim_id=claim.id, starting_ids=starting_ids, background_ids=background_ids,
        support_ids=tuple(x.id for x in survivors), steps=tuple(steps), search_complete=True,
        minimality_verified=minimality_verified,
        n_subsets_tried=n_subsets_tried,
        n_candidate_scans_used=candidate_budget - remaining_candidates,
        n_predicate_evaluations_used=evaluation_budget - remaining_evaluations,
        domain_coverage=domain.coverage,
        notes=() if minimality_verified else (
            "at least one removal attempt was inconclusive (incomplete) -- the returned set is a "
            "PROVISIONAL support, minimality is NOT fully verified",
        ),
    )


def find_minimal_inconsistent_core(
    domain: FiniteDomainSpec,
    assumptions: Sequence[AssumptionSpec],
    *,
    background: Sequence[AssumptionSpec] = (),
    subset_budget: int = DEFAULT_SUBSET_BUDGET,
    candidate_budget: int = DEFAULT_CANDIDATE_BUDGET,
    evaluation_budget: int = DEFAULT_EVALUATION_BUDGET,
) -> InconsistentCoreReport:
    _validate_unique_ids(assumptions, background)
    starting_ids = tuple(a.id for a in assumptions)
    background_ids = tuple(a.id for a in background)
    remaining_candidates = candidate_budget
    remaining_evaluations = evaluation_budget
    n_subsets_tried = 0

    def check(subset) -> Optional[ClaimReport]:
        nonlocal remaining_candidates, remaining_evaluations, n_subsets_tried
        if n_subsets_tried >= subset_budget or remaining_candidates <= 0 or remaining_evaluations <= 0:
            return None
        n_subsets_tried += 1
        report = audit_finite_claim(
            domain, list(background) + list(subset), _SATISFIABILITY_PROBE,
            budget=remaining_candidates, evaluation_budget=remaining_evaluations,
        )
        remaining_candidates -= report.n_evaluated
        remaining_evaluations -= report.n_predicate_evaluations
        return report

    def budget_exhausted_report(steps, minimality_verified) -> InconsistentCoreReport:
        return InconsistentCoreReport(
            starting_ids=starting_ids, background_ids=background_ids, core_ids=None,
            steps=tuple(steps), search_complete=False, minimality_verified=minimality_verified,
            n_subsets_tried=n_subsets_tried,
            n_candidate_scans_used=candidate_budget - remaining_candidates,
            n_predicate_evaluations_used=evaluation_budget - remaining_evaluations,
            domain_coverage=domain.coverage,
            notes=("budget exhausted before the deletion search finished",),
        )

    survivors = list(assumptions)
    base_report = check(survivors)
    if base_report is None:
        return budget_exhausted_report([], True)
    if base_report.logical_status != "no_admissible_model_in_scope":
        return InconsistentCoreReport(
            starting_ids=starting_ids, background_ids=background_ids, core_ids=None,
            steps=(), search_complete=base_report.search_complete, minimality_verified=True,
            n_subsets_tried=n_subsets_tried,
            n_candidate_scans_used=candidate_budget - remaining_candidates,
            n_predicate_evaluations_used=evaluation_budget - remaining_evaluations,
            domain_coverage=domain.coverage,
            notes=(
                f"starting set is not jointly unsatisfiable in scope (status={base_report.logical_status}); "
                "a core search requires an already-unsatisfiable starting set",
            ),
        )

    steps = []
    minimality_verified = True
    for a in assumptions:
        if a.id not in {x.id for x in survivors}:
            continue
        trial = [x for x in survivors if x.id != a.id]
        trial_report = check(trial)
        if trial_report is None:
            return budget_exhausted_report(steps, minimality_verified)
        if trial_report.logical_status == "no_admissible_model_in_scope":
            kept = False
            survivors = trial
        elif trial_report.logical_status == "incomplete":
            kept = None
            minimality_verified = False
        else:
            kept = True
        steps.append(DeletionStep(assumption_id=a.id, kept=kept, trial_report=trial_report))

    return InconsistentCoreReport(
        starting_ids=starting_ids, background_ids=background_ids,
        core_ids=tuple(x.id for x in survivors), steps=tuple(steps), search_complete=True,
        minimality_verified=minimality_verified,
        n_subsets_tried=n_subsets_tried,
        n_candidate_scans_used=candidate_budget - remaining_candidates,
        n_predicate_evaluations_used=evaluation_budget - remaining_evaluations,
        domain_coverage=domain.coverage,
        notes=() if minimality_verified else (
            "at least one removal attempt was inconclusive (incomplete) -- the returned core is a "
            "PROVISIONAL core, minimality is NOT fully verified",
        ),
    )
