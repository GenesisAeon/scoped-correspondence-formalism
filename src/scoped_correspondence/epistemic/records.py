"""Shared record types for the epistemic layer (H1, Plan §6.1).

Content basis: `docs/epistemic_scope.md`. These are typed containers, not
a formal proof kernel -- predicates are ordinary Python callables,
registered explicitly by the caller (no free-text parsing, no `eval`,
Plan §6.3).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Optional, Tuple

#: Declared assumption roles (Plan §6.1).
ASSUMPTION_ROLES = ("structural", "measurement", "statistical", "numerical", "decision", "definition")

#: Declared domain/target-space relationships (Plan §6.1). A domain marked
#: `grid_of_continuous_space` must NEVER be reported as if it established a
#: global validity status over the underlying continuous space (Plan §4.1,
#: the Alloy-tutorial scope caution, S3) -- callers must check this field
#: before presenting any `ClaimReport` as more than scope-local.
DOMAIN_RELATIONSHIPS = ("entire_finite_space", "restricted_candidates", "grid_of_continuous_space")

#: Coverage of the declared domain relative to whatever the caller intended
#: to cover (Plan §6.1) -- independent of `DOMAIN_RELATIONSHIPS` above: a
#: `partial` coverage can mean "every supplied sample was checked, but the
#: claimed target space is not fully covered".
DOMAIN_COVERAGE = ("complete", "partial")

#: The five outcomes of `docs/epistemic_scope.md` §1.
LOGICAL_STATUSES = (
    "no_admissible_model_in_scope",
    "entailed_in_scope",
    "negation_entailed_in_scope",
    "underdetermined",
    "incomplete",
)

EVIDENCE_KINDS = ("exhaustive_finite", "numerical_sample", "analytic_argument", "empirical_evaluation", "not_evaluated")
EMPIRICAL_STATUSES = ("not_tested", "synthetic_only", "evaluated_on_declared_data")

#: Declared domain coverage relative to whatever the caller intended to cover
#: (Plan §6.1) -- see `FiniteDomainSpec.coverage`. Every downstream report
#: derived from a `FiniteDomainSpec` must carry this value through
#: (`domain_coverage` field below) rather than silently dropping it
#: (SCF_REVIEW_H0_H7_9dde420.md R5).
DOMAIN_COVERAGE_VALUES = ("complete", "partial")


class PredicateEvaluationError(Exception):
    """Raised by `evaluate_bool` when a declared bool-valued predicate
    raises, or returns anything other than the literal `True`/`False`.
    Callers MUST catch this and record an evaluation error -- never
    coerce the result into a truth value via `bool(...)` (Plan §6.3:
    "Bool-Prädikate liefern wirklich boolesche Ergebnisse; None, Strings
    oder fehlgeschlagene Berechnungen sind Fehler";
    SCF_REVIEW_H0_H7_9dde420.md R3)."""


def evaluate_bool(predicate: Callable[..., Any], *args: Any) -> bool:
    """Evaluate a declared bool predicate (single-argument like an
    assumption/claim/antecedent, or multi-argument like a safety
    predicate `safety(w, u)`) and return the literal `True`/`False`.
    Raises `PredicateEvaluationError` for a raised exception, or a
    non-bool return value (including truthy/falsy non-bool values like
    `None`, `float("nan")`, or a non-empty string) -- these must never be
    silently coerced via `bool(...)`, since that would turn a missing
    value or a computation error into a truth value."""
    try:
        result = predicate(*args)
    except Exception as e:  # noqa: BLE001 -- any predicate failure is an evaluation error, not a crash
        raise PredicateEvaluationError(f"{type(e).__name__}: {e}") from e
    if isinstance(result, bool):
        return result
    raise PredicateEvaluationError(f"predicate returned non-bool {result!r} ({type(result).__name__})")


@dataclass(frozen=True)
class AssumptionSpec:
    """One declared assumption `a: w -> bool`.

    `justification_status` (e.g. "asserted", "derived", "unverified") is
    kept SEPARATE from whether a given finite candidate satisfies the
    predicate -- the two questions ("is this assumption well-justified?"
    and "does candidate w satisfy it?") must never be conflated into one
    field (Plan §6.1).
    """

    id: str
    text: str
    role: str
    predicate: Callable[[Any], bool]
    justification_status: str = "asserted"
    source: str = ""
    background: Tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.role not in ASSUMPTION_ROLES:
            raise ValueError(f"role must be one of {ASSUMPTION_ROLES}, got {self.role!r}")
        if not self.id:
            raise ValueError("AssumptionSpec requires a nonempty stable id")


@dataclass(frozen=True)
class FiniteDomainSpec:
    """A declared, nonempty, finite, ORDERED (reproducible) candidate set.

    Empty `candidates` is an INPUT ERROR (raises), never silently treated
    as an empty admissible set (`docs/epistemic_scope.md` §1: those are
    different things -- empty input vs. a nonempty domain from which
    assumptions exclude every candidate)."""

    id: str
    candidates: Tuple[Any, ...]
    scope_text: str
    coverage: str = "complete"
    relationship_to_target_space: str = "entire_finite_space"
    arithmetic_kind: str = "boolean"
    units: str = ""
    version: str = "1"

    def __post_init__(self) -> None:
        if len(self.candidates) == 0:
            raise ValueError("FiniteDomainSpec requires a nonempty candidate tuple (empty input is an error, not a result)")
        if len(set(self.candidates)) != len(self.candidates):
            raise ValueError("FiniteDomainSpec candidates must be unique")
        if self.coverage not in DOMAIN_COVERAGE:
            raise ValueError(f"coverage must be one of {DOMAIN_COVERAGE}, got {self.coverage!r}")
        if self.relationship_to_target_space not in DOMAIN_RELATIONSHIPS:
            raise ValueError(f"relationship_to_target_space must be one of {DOMAIN_RELATIONSHIPS}")


@dataclass(frozen=True)
class ClaimSpec:
    """A claim `C: w -> bool` to audit against a `FiniteDomainSpec` under
    declared `AssumptionSpec`s, with an optional antecedent `B` for a
    conditional claim `B => C` (Plan §4.2 vacuity check)."""

    id: str
    text: str
    target: Callable[[Any], bool]
    antecedent: Optional[Callable[[Any], bool]] = None

    def __post_init__(self) -> None:
        if not self.id:
            raise ValueError("ClaimSpec requires a nonempty stable id")


@dataclass(frozen=True)
class ClaimReport:
    """Result of `audit_finite_claim`. Every axis is a SEPARATE field --
    no single collapsed confidence number (Plan §6.1)."""

    claim_id: str
    logical_status: str
    search_complete: bool
    arithmetic_kind: str
    n_domain: int
    n_evaluated: int
    n_admissible: int
    n_errors: int
    positive_witness: Optional[Any]
    negative_witness: Optional[Any]
    #: Total individual predicate calls actually made (assumptions +
    #: target + antecedent, across both the main scan and any
    #: antecedent-reachability pass) -- lets a caller (e.g. `supports.py`)
    #: decrement ONE shared `evaluation_budget` across nested calls
    #: (Plan §6.3; SCF_REVIEW_H0_H7_9dde420.md R7).
    n_predicate_evaluations: int = 0
    #: Whether a witness was actually found, INDEPENDENT of the witness's
    #: own value -- required because a candidate value can legitimately
    #: BE `None` (or any other falsy value), which must never be confused
    #: with "no witness found" (SCF_REVIEW_H0_H7_9dde420.md R2).
    has_positive_witness: bool = False
    has_negative_witness: bool = False
    #: Whether EVERY candidate in the declared domain was scanned without
    #: hitting any budget -- a SEPARATE question from `search_complete`
    #: (whether THIS SPECIFIC conclusion is already certain, e.g. via an
    #: early double-witness exit with candidates left unscanned;
    #: SCF_REVIEW_H0_H7_9dde420.md R5).
    all_candidates_scanned: bool = False
    #: Carries `FiniteDomainSpec.coverage` through -- never silently
    #: dropped (SCF_REVIEW_H0_H7_9dde420.md R5).
    domain_coverage: str = "complete"
    antecedent_reachable_in_scope: Optional[bool] = None
    vacuity_kind: Optional[str] = None
    evidence_kind: str = "exhaustive_finite"
    empirical_status: str = "not_tested"
    domain_relationship: str = "entire_finite_space"
    notes: Tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if self.logical_status not in LOGICAL_STATUSES:
            raise ValueError(f"logical_status must be one of {LOGICAL_STATUSES}, got {self.logical_status!r}")
        if self.domain_coverage not in DOMAIN_COVERAGE_VALUES:
            raise ValueError(f"domain_coverage must be one of {DOMAIN_COVERAGE_VALUES}, got {self.domain_coverage!r}")
