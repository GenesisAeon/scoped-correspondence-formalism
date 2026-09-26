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

Both searches share ONE running candidate-scan budget across every
nested `audit_finite_claim` call (Plan §6.3: "Die Gesamtgrenze gilt auch
über verschachtelte Supportprüfungen hinweg"), plus a separate cap on
how many assumption subsets are tried in total.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Sequence, Tuple

from .finite import audit_finite_claim
from .records import AssumptionSpec, ClaimReport, ClaimSpec, FiniteDomainSpec

DEFAULT_SUBSET_BUDGET = 4096
DEFAULT_CANDIDATE_BUDGET = 1_000_000

#: Used internally by `find_minimal_inconsistent_core` to probe pure
#: satisfiability via `audit_finite_claim` without needing a caller-
#: supplied claim -- an always-true target never produces a negative
#: witness, so the resulting `logical_status` reduces to exactly
#: `no_admissible_model_in_scope` (S_A empty) vs. `entailed_in_scope`
#: (S_A nonempty) vs. `incomplete` (budget ran out).
_SATISFIABILITY_PROBE = ClaimSpec(id="_satisfiability_probe", text="w -> True", target=lambda w: True)


@dataclass(frozen=True)
class DeletionStep:
    """One tentative removal in the deletion search, with its own
    independently re-checked `ClaimReport` as the concrete witness
    (Plan §4.3: "Für jede Entfernung muss ein konkreter Zeuge
    ausgegeben und erneut geprüft werden")."""

    assumption_id: str
    kept: bool  # True: removing this assumption would break the property, so it stays. False: removed permanently.
    trial_report: ClaimReport


@dataclass(frozen=True)
class SupportReport:
    claim_id: str
    starting_ids: Tuple[str, ...]
    background_ids: Tuple[str, ...]
    support_ids: Optional[Tuple[str, ...]]
    steps: Tuple[DeletionStep, ...]
    search_complete: bool
    n_subsets_tried: int
    n_candidate_scans_used: int
    notes: Tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class InconsistentCoreReport:
    starting_ids: Tuple[str, ...]
    background_ids: Tuple[str, ...]
    core_ids: Optional[Tuple[str, ...]]
    steps: Tuple[DeletionStep, ...]
    search_complete: bool
    n_subsets_tried: int
    n_candidate_scans_used: int
    notes: Tuple[str, ...] = field(default_factory=tuple)


def find_minimal_support(
    domain: FiniteDomainSpec,
    assumptions: Sequence[AssumptionSpec],
    claim: ClaimSpec,
    *,
    background: Sequence[AssumptionSpec] = (),
    subset_budget: int = DEFAULT_SUBSET_BUDGET,
    candidate_budget: int = DEFAULT_CANDIDATE_BUDGET,
) -> SupportReport:
    starting_ids = tuple(a.id for a in assumptions)
    background_ids = tuple(a.id for a in background)
    remaining = candidate_budget
    n_subsets_tried = 0

    def check(subset):
        nonlocal remaining, n_subsets_tried
        n_subsets_tried += 1
        report = audit_finite_claim(domain, list(background) + list(subset), claim, budget=remaining)
        remaining -= report.n_evaluated
        return report

    survivors = list(assumptions)
    base_report = check(survivors)
    if base_report.logical_status != "entailed_in_scope":
        return SupportReport(
            claim_id=claim.id,
            starting_ids=starting_ids,
            background_ids=background_ids,
            support_ids=None,
            steps=(),
            search_complete=base_report.search_complete,
            n_subsets_tried=n_subsets_tried,
            n_candidate_scans_used=candidate_budget - remaining,
            notes=(
                f"starting set does not entail the claim in scope (status={base_report.logical_status}); "
                "a deletion search requires an already satisfiable, already-entailing starting set",
            ),
        )

    steps = []
    for a in assumptions:
        if a.id not in {x.id for x in survivors}:
            continue  # already removed in an earlier step
        if n_subsets_tried >= subset_budget or remaining <= 0:
            return SupportReport(
                claim_id=claim.id,
                starting_ids=starting_ids,
                background_ids=background_ids,
                support_ids=None,
                steps=tuple(steps),
                search_complete=False,
                n_subsets_tried=n_subsets_tried,
                n_candidate_scans_used=candidate_budget - remaining,
                notes=("budget exhausted before the deletion search finished",),
            )
        trial = [x for x in survivors if x.id != a.id]
        trial_report = check(trial)
        kept = trial_report.logical_status != "entailed_in_scope"
        if not kept:
            survivors = trial
        steps.append(DeletionStep(assumption_id=a.id, kept=kept, trial_report=trial_report))

    return SupportReport(
        claim_id=claim.id,
        starting_ids=starting_ids,
        background_ids=background_ids,
        support_ids=tuple(x.id for x in survivors),
        steps=tuple(steps),
        search_complete=True,
        n_subsets_tried=n_subsets_tried,
        n_candidate_scans_used=candidate_budget - remaining,
    )


def find_minimal_inconsistent_core(
    domain: FiniteDomainSpec,
    assumptions: Sequence[AssumptionSpec],
    *,
    background: Sequence[AssumptionSpec] = (),
    subset_budget: int = DEFAULT_SUBSET_BUDGET,
    candidate_budget: int = DEFAULT_CANDIDATE_BUDGET,
) -> InconsistentCoreReport:
    starting_ids = tuple(a.id for a in assumptions)
    background_ids = tuple(a.id for a in background)
    remaining = candidate_budget
    n_subsets_tried = 0

    def check(subset):
        nonlocal remaining, n_subsets_tried
        n_subsets_tried += 1
        report = audit_finite_claim(domain, list(background) + list(subset), _SATISFIABILITY_PROBE, budget=remaining)
        remaining -= report.n_evaluated
        return report

    survivors = list(assumptions)
    base_report = check(survivors)
    if base_report.logical_status != "no_admissible_model_in_scope":
        return InconsistentCoreReport(
            starting_ids=starting_ids,
            background_ids=background_ids,
            core_ids=None,
            steps=(),
            search_complete=base_report.search_complete,
            n_subsets_tried=n_subsets_tried,
            n_candidate_scans_used=candidate_budget - remaining,
            notes=(
                f"starting set is not jointly unsatisfiable in scope (status={base_report.logical_status}); "
                "a core search requires an already-unsatisfiable starting set",
            ),
        )

    steps = []
    for a in assumptions:
        if a.id not in {x.id for x in survivors}:
            continue
        if n_subsets_tried >= subset_budget or remaining <= 0:
            return InconsistentCoreReport(
                starting_ids=starting_ids,
                background_ids=background_ids,
                core_ids=None,
                steps=tuple(steps),
                search_complete=False,
                n_subsets_tried=n_subsets_tried,
                n_candidate_scans_used=candidate_budget - remaining,
                notes=("budget exhausted before the deletion search finished",),
            )
        trial = [x for x in survivors if x.id != a.id]
        trial_report = check(trial)
        kept = trial_report.logical_status != "no_admissible_model_in_scope"
        if not kept:
            survivors = trial
        steps.append(DeletionStep(assumption_id=a.id, kept=kept, trial_report=trial_report))

    return InconsistentCoreReport(
        starting_ids=starting_ids,
        background_ids=background_ids,
        core_ids=tuple(x.id for x in survivors),
        steps=tuple(steps),
        search_complete=True,
        n_subsets_tried=n_subsets_tried,
        n_candidate_scans_used=candidate_budget - remaining,
    )
