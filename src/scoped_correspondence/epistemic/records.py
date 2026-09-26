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
    antecedent_reachable_in_scope: Optional[bool] = None
    vacuity_kind: Optional[str] = None
    evidence_kind: str = "exhaustive_finite"
    empirical_status: str = "not_tested"
    domain_relationship: str = "entire_finite_space"
    notes: Tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if self.logical_status not in LOGICAL_STATUSES:
            raise ValueError(f"logical_status must be one of {LOGICAL_STATUSES}, got {self.logical_status!r}")
