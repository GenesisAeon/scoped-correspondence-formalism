"""H3: observation-dependent identification (Plan §4.4; K4, K8).

For a deterministic exact observation ``h`` and observed value ``y``:

    F_A(y) = {w in S_A : h(w) == y}          (the observation fiber)
    Q_A(y) = {target(w) : w in F_A(y)}       (the identified-value set)

A boolean claim is identifiable at ``y`` iff the nonempty fiber contains
only ONE truth value. A numeric target is point-identified at ``y`` iff
``Q_A(y)`` has exactly one element. Several possible values are reported
as a SET -- never collapsed into `[min, max]` (K4: q=(x1-x2)^2 at y=2 has
the exact value set {0,4}; reporting the interval [0,4] alone would
wrongly suggest 1 or 2 are reachable). An empty fiber is a mismatch
between the observation and the declared model space, NOT a form of
"perfect identification" -- it is flagged, never silently reported as
point-identified.

`macro_dynamics_and_observability` wraps the existing controlled-Markov
correspondence machinery (`correspondence/controlled_markov.py`) to show
K8's distinction side by side: exact macro DYNAMICS correspondence
(``P^a C = C Q^omega(a)``, via `check_controlled_correspondence`) and
macro OBSERVABILITY of one specific event (via `is_union_of_classes`)
are separate requirements -- one can hold exactly while the other fails.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Hashable, Mapping, Optional, Sequence, Tuple

import numpy as np

from scoped_correspondence.correspondence.controlled_markov import (
    ActionLumpabilityReport,
    check_controlled_correspondence,
    is_union_of_classes,
)
from scoped_correspondence.errors import ScopeViolationError

from .records import AssumptionSpec, FiniteDomainSpec, PredicateEvaluationError, evaluate_bool

DEFAULT_BUDGET = 4096
DEFAULT_EVALUATION_BUDGET = 1_000_000


@dataclass(frozen=True)
class FiberReport:
    domain_id: str
    observed: Any
    fiber: Tuple[Any, ...]
    n_admissible: int
    n_fiber: int
    empty_fiber: bool
    search_complete: bool
    n_evaluated: int
    n_errors: int = 0
    all_candidates_scanned: bool = False
    domain_coverage: str = "complete"
    notes: Tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class IdentifiedSetReport:
    values: Tuple[Any, ...]  # distinct target values across the fiber, first-seen order -- the authoritative result
    point_identified: bool
    fiber_size: int
    search_complete: bool
    min_value: Optional[Any] = None  # convenience only for orderable values; NEVER a substitute for `values`
    max_value: Optional[Any] = None
    n_errors: int = 0
    domain_coverage: str = "complete"
    notes: Tuple[str, ...] = field(default_factory=tuple)


def observation_fiber(
    domain: FiniteDomainSpec,
    assumptions: Sequence[AssumptionSpec],
    observation: Callable[[Any], Any],
    observed: Any,
    *,
    budget: int = DEFAULT_BUDGET,
    evaluation_budget: int = DEFAULT_EVALUATION_BUDGET,
) -> FiberReport:
    """F_A(y) over `{w in domain.candidates : all assumptions hold}`.

    **Followup-Review-Fix (SCF_REVIEW_H0_H7_9dde420.md R3, R5, R7):**
    assumption predicates go through `records.evaluate_bool` (an error is
    counted in `n_errors` and excludes the candidate, never silently
    admits or excludes it as if it were a clean truth value);
    `all_candidates_scanned`/`domain_coverage` are exposed separately
    from `search_complete`; `evaluation_budget` caps total predicate
    calls, separate from `budget`'s candidate-scan cap.
    """
    n_evaluated = 0
    n_admissible = 0
    n_errors = 0
    n_predicate_evaluations = 0
    fiber = []
    ran_out_of_budget = False
    ran_out_of_evaluation_budget = False
    for w in domain.candidates:
        if n_evaluated >= budget:
            ran_out_of_budget = True
            break
        admissible = True
        candidate_errored = False
        for a in assumptions:
            if n_predicate_evaluations >= evaluation_budget:
                ran_out_of_evaluation_budget = True
                break
            n_predicate_evaluations += 1
            try:
                if not evaluate_bool(a.predicate, w):
                    admissible = False
                    break
            except PredicateEvaluationError:
                n_errors += 1
                candidate_errored = True
                break
        if ran_out_of_evaluation_budget:
            break
        n_evaluated += 1
        if candidate_errored or not admissible:
            continue
        n_admissible += 1
        if observation(w) == observed:
            fiber.append(w)

    all_candidates_scanned = (n_evaluated == len(domain.candidates)) and not ran_out_of_budget and not ran_out_of_evaluation_budget
    search_complete = all_candidates_scanned and n_errors == 0

    notes = []
    if ran_out_of_budget:
        notes.append("candidate budget exhausted before the whole domain was scanned")
    if ran_out_of_evaluation_budget:
        notes.append("evaluation_budget exhausted before the whole domain was scanned")
    if n_errors > 0:
        notes.append(f"{n_errors} candidate(s) had an assumption predicate evaluation error -- excluded, fiber membership for them is unknown, not confirmed absent")
    if search_complete and len(fiber) == 0:
        notes.append("empty fiber: the observation is incompatible with the declared model space under these "
                      "assumptions -- this is a mismatch, not a (vacuously good) identification result")

    return FiberReport(
        domain_id=domain.id, observed=observed, fiber=tuple(fiber),
        n_admissible=n_admissible, n_fiber=len(fiber), empty_fiber=(len(fiber) == 0),
        search_complete=search_complete, n_evaluated=n_evaluated, n_errors=n_errors,
        all_candidates_scanned=all_candidates_scanned, domain_coverage=domain.coverage,
        notes=tuple(notes),
    )


def identified_values(fiber: FiberReport, target: Callable[[Any], Any]) -> IdentifiedSetReport:
    """Q_A(y) for a given `target`, computed over an already-built `FiberReport`.

    **Followup-Review-Fix (SCF_REVIEW_H0_H7_9dde420.md R3 numeric
    addendum):** `target` may return any hashable value INCLUDING
    `float("inf")`/`float("-inf")` -- an explicitly extended-real
    point-identified value is a legitimate result and is never banned.
    `float("nan")` is rejected as an evaluation error instead: `nan != nan`
    makes set/equality-based distinctness unreliable, so treating it as an
    ordinary "value" could silently fabricate spurious distinct entries.
    """
    if not fiber.search_complete:
        return IdentifiedSetReport(
            values=(), point_identified=False, fiber_size=fiber.n_fiber, search_complete=False,
            domain_coverage=fiber.domain_coverage,
            notes=("the fiber itself was built from an incomplete or errored scan -- no identification claim can be made",),
        )
    if fiber.empty_fiber:
        return IdentifiedSetReport(
            values=(), point_identified=False, fiber_size=0, search_complete=True,
            domain_coverage=fiber.domain_coverage,
            notes=("empty fiber -- observation/model mismatch, not identification",),
        )

    values = []
    seen = set()
    n_errors = 0
    for w in fiber.fiber:
        try:
            v = target(w)
        except Exception as e:  # noqa: BLE001 -- a target evaluation failure is an error, not a value
            n_errors += 1
            continue
        if isinstance(v, float) and math.isnan(v):
            n_errors += 1
            continue
        if v not in seen:
            seen.add(v)
            values.append(v)

    min_value = None
    max_value = None
    try:
        min_value = min(values)
        max_value = max(values)
    except TypeError:
        pass  # values are not mutually orderable (e.g. non-numeric) -- min/max simply stay unavailable

    notes = []
    if len(values) > 1:
        notes.append("NOT point-identified: multiple distinct values -- report the value set, not an interval spanning it")
    if n_errors > 0:
        notes.append(f"{n_errors} candidate(s) in the fiber had a target evaluation error or NaN result -- "
                      "excluded from the value set, this result is NOT a certified complete identification")
    return IdentifiedSetReport(
        values=tuple(values), point_identified=(len(values) == 1 and n_errors == 0), fiber_size=len(fiber.fiber),
        search_complete=(n_errors == 0), min_value=min_value, max_value=max_value, n_errors=n_errors,
        domain_coverage=fiber.domain_coverage, notes=tuple(notes),
    )


@dataclass(frozen=True)
class MacroObservabilityReport:
    """K8: dynamics compatibility and claim/event observability are
    SEPARATE fields, deliberately never merged into one pass/fail."""

    dynamics_exact: bool
    dynamics_reports: Dict[Hashable, ActionLumpabilityReport]
    micro_event: Tuple[int, ...]
    event_is_union_of_classes: bool
    notes: Tuple[str, ...] = field(default_factory=tuple)


def macro_dynamics_and_observability(
    P_by_action: Mapping[Hashable, np.ndarray],
    C: np.ndarray,
    omega: Mapping[Hashable, Hashable],
    micro_event: Sequence[int],
    *,
    tol: float = 1e-9,
) -> MacroObservabilityReport:
    if len(P_by_action) == 0:
        # Followup-Review-Fix (SCF_REVIEW_H0_H7_9dde420.md R4a): `all([])`
        # would make `dynamics_exact=True` vacuously true for zero
        # declared actions -- an empty action set is a caller error here,
        # not evidence of anything.
        raise ScopeViolationError("macro_dynamics_and_observability requires at least one declared micro action in P_by_action")
    dynamics_reports = check_controlled_correspondence(P_by_action, C, omega, tol=tol)
    dynamics_exact = all(r.exact for r in dynamics_reports.values())
    event_ok = is_union_of_classes(micro_event, C)
    notes = ()
    if dynamics_exact and not event_ok:
        notes = (
            "exact macro dynamics (P^a C = C Q^omega(a) for every declared action) does NOT imply this "
            "specific event is macro-observable -- these are separate requirements (K8)",
        )
    return MacroObservabilityReport(
        dynamics_exact=dynamics_exact, dynamics_reports=dynamics_reports,
        micro_event=tuple(micro_event), event_is_union_of_classes=event_ok, notes=notes,
    )
