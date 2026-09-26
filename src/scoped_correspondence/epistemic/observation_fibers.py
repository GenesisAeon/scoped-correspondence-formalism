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

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Hashable, Mapping, Optional, Sequence, Tuple

import numpy as np

from scoped_correspondence.correspondence.controlled_markov import (
    ActionLumpabilityReport,
    check_controlled_correspondence,
    is_union_of_classes,
)

from .records import AssumptionSpec, FiniteDomainSpec

DEFAULT_BUDGET = 1_000_000


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
    notes: Tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class IdentifiedSetReport:
    values: Tuple[Any, ...]  # distinct target values across the fiber, first-seen order -- the authoritative result
    point_identified: bool
    fiber_size: int
    search_complete: bool
    min_value: Optional[Any] = None  # convenience only for orderable values; NEVER a substitute for `values`
    max_value: Optional[Any] = None
    notes: Tuple[str, ...] = field(default_factory=tuple)


def observation_fiber(
    domain: FiniteDomainSpec,
    assumptions: Sequence[AssumptionSpec],
    observation: Callable[[Any], Any],
    observed: Any,
    *,
    budget: int = DEFAULT_BUDGET,
) -> FiberReport:
    """F_A(y) over `{w in domain.candidates : all assumptions hold}`."""
    n_evaluated = 0
    n_admissible = 0
    fiber = []
    for w in domain.candidates:
        if n_evaluated >= budget:
            return FiberReport(
                domain_id=domain.id, observed=observed, fiber=tuple(fiber),
                n_admissible=n_admissible, n_fiber=len(fiber), empty_fiber=(len(fiber) == 0),
                search_complete=False, n_evaluated=n_evaluated,
                notes=("budget exhausted before the whole domain was scanned",),
            )
        n_evaluated += 1
        if not all(bool(a.predicate(w)) for a in assumptions):
            continue
        n_admissible += 1
        if observation(w) == observed:
            fiber.append(w)

    notes = ()
    if len(fiber) == 0:
        notes = ("empty fiber: the observation is incompatible with the declared model space under these "
                  "assumptions -- this is a mismatch, not a (vacuously good) identification result",)
    return FiberReport(
        domain_id=domain.id, observed=observed, fiber=tuple(fiber),
        n_admissible=n_admissible, n_fiber=len(fiber), empty_fiber=(len(fiber) == 0),
        search_complete=True, n_evaluated=n_evaluated, notes=notes,
    )


def identified_values(fiber: FiberReport, target: Callable[[Any], Any]) -> IdentifiedSetReport:
    """Q_A(y) for a given `target`, computed over an already-built `FiberReport`."""
    if not fiber.search_complete:
        return IdentifiedSetReport(
            values=(), point_identified=False, fiber_size=fiber.n_fiber, search_complete=False,
            notes=("the fiber itself was built from an incomplete scan -- no identification claim can be made",),
        )
    if fiber.empty_fiber:
        return IdentifiedSetReport(
            values=(), point_identified=False, fiber_size=0, search_complete=True,
            notes=("empty fiber -- observation/model mismatch, not identification",),
        )

    values = []
    seen = set()
    for w in fiber.fiber:
        v = target(w)
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

    notes = ()
    if len(values) > 1:
        notes = (f"NOT point-identified: {len(values)} distinct values -- report the value set, "
                  "not an interval spanning it",)
    return IdentifiedSetReport(
        values=tuple(values), point_identified=(len(values) == 1), fiber_size=len(fiber.fiber),
        search_complete=True, min_value=min_value, max_value=max_value, notes=notes,
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
