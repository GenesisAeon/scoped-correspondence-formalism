"""H6a: adapters from existing SCF numerical reports into the epistemic
evidence vocabulary (Plan §4, §6.1; `docs/epistemic_scope.md`).

These wrap ALREADY EXISTING, already independently verified SCF
validation reports as `ClaimReport`s -- NEVER re-deriving or re-checking
the underlying numbers, and NEVER silently upgrading a numerically-
tolerant (float, atol/rtol) result into `exhaustive_finite`/exact status.
A `CorrespondenceReport` (`correspondence/contract.py`) is a finite
SAMPLE of (state, time) pairs checked under a numerical tolerance -- it
becomes `evidence_kind="numerical_sample"`, `domain_relationship=
"grid_of_continuous_space"` (the underlying source/target models are
typically continuous-state; a finite sample of them must never be
reported as if it exhausted that space). `empirical_status` defaults to
`"synthetic_only"` -- it is the CALLER's responsibility to pass
`"evaluated_on_declared_data"` when the sampled states/times actually
come from a declared real dataset; this adapter never infers that on its
own.

For K8-style macro correspondence (H3's `MacroObservabilityReport`,
itself wrapping `check_controlled_correspondence`'s float/tol-based
lumpability check and `is_union_of_classes`'s EXACT combinatorial check),
the two questions are kept as two SEPARATE `ClaimReport`s with two
different `evidence_kind`s -- dynamics exactness stays
`"numerical_sample"` (one concrete numeric kernel, not a symbolic proof
for every kernel satisfying some property), while event observability
stays `"exhaustive_finite"` (an exact, tolerance-free set-membership
check).
"""
from __future__ import annotations

import math
from typing import Optional, Tuple

from scoped_correspondence.correspondence.contract import CorrespondenceReport
from scoped_correspondence.errors import ScopeViolationError

from .observation_fibers import MacroObservabilityReport
from .records import EMPIRICAL_STATUSES, ClaimReport


def _require_empirical_status(empirical_status: str) -> None:
    if empirical_status not in EMPIRICAL_STATUSES:
        raise ValueError(f"empirical_status must be one of {EMPIRICAL_STATUSES}, got {empirical_status!r}")


def _is_finite_residual_value(value) -> bool:
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


#: Attached whenever the resulting claim's status is negation_entailed_in_scope
#: for an AGGREGATE ("holds on every sampled pair/action") proposition, so
#: that a single counterexample is never misread as "every pair/action
#: fails" (SCF_REVIEW_H0_H7_9dde420.md R4b: ¬∀w C(w) != ∀w ¬C(w)).
_AGGREGATE_NEGATION_NOTE = (
    "this claim is an AGGREGATE proposition over the whole sample ('every sampled candidate satisfies "
    "the correspondence'); negation_entailed_in_scope here means 'not every candidate passes' (at least "
    "one counterexample exists, given as negative_witness), NOT 'every candidate fails' -- other "
    "candidates may well still individually satisfy the correspondence",
)


def claim_report_from_correspondence(
    report: CorrespondenceReport,
    *,
    claim_id: str,
    empirical_status: str = "synthetic_only",
    notes: Tuple[str, ...] = (),
) -> ClaimReport:
    """Wrap a `CorrespondenceReport` as a `ClaimReport`. The claim is the
    AGGREGATE proposition 'the declared conjugacy holds on EVERY sampled
    (state, time) pair' -- `search_complete=True` refers only to that
    finite sample having been fully evaluated, NOT to any claim about the
    full (typically continuous) state/time space it was drawn from.

    **Followup-Review-Fix (SCF_REVIEW_H0_H7_9dde420.md R4a, R4b):** a
    non-finite residual is a COMPUTATION ERROR for that pair, never
    evidence of a negated correspondence -- it now produces `incomplete`
    with `n_errors>0`, not a confident `negation_entailed_in_scope`. A
    genuine (all-finite) tolerance violation still yields
    `negation_entailed_in_scope`, but that status is now explicitly
    documented (in `notes`) as negating the AGGREGATE proposition, not as
    claiming every individual pair fails.
    """
    _require_empirical_status(empirical_status)
    n_pairs = int(report.evidence.get("n_pairs", len(report.residuals)))
    n_nonfinite = sum(1 for r in report.residuals if not _is_finite_residual_value(r.value))

    if n_nonfinite > 0:
        first_bad = next(r for r in report.residuals if not _is_finite_residual_value(r.value))
        return ClaimReport(
            claim_id=claim_id,
            logical_status="incomplete",
            search_complete=False,
            arithmetic_kind="float",
            n_domain=n_pairs, n_evaluated=n_pairs, n_admissible=n_pairs, n_errors=n_nonfinite,
            positive_witness=None, negative_witness=None,
            has_positive_witness=False, has_negative_witness=False,
            all_candidates_scanned=True, domain_coverage="complete",
            evidence_kind="numerical_sample", empirical_status=empirical_status,
            domain_relationship="grid_of_continuous_space",
            notes=notes + (
                f"wraps correspondence.contract.CorrespondenceReport(kind={report.kind!r}); "
                f"{n_nonfinite} of {len(report.residuals)} sampled pair(s) produced a non-finite residual "
                "(a computation error) -- this is NOT evidence of a negated correspondence, status is "
                "incomplete, not negation_entailed_in_scope",
                f"first non-finite pair: at_state={first_bad.at_state!r}, at_time={first_bad.at_time!r}",
            ),
        )

    logical_status = "entailed_in_scope" if report.ok else "negation_entailed_in_scope"
    positive_witness = None
    negative_witness = None
    if report.ok:
        positive_witness = {"max_residual": report.max_residual, "n_pairs": n_pairs}
    else:
        worst = max(report.residuals, key=lambda r: r.value)
        negative_witness = {"at_state": worst.at_state, "at_time": worst.at_time, "residual": worst.value}

    return ClaimReport(
        claim_id=claim_id,
        logical_status=logical_status,
        search_complete=True,
        arithmetic_kind="float",
        n_domain=n_pairs,
        n_evaluated=n_pairs,
        n_admissible=n_pairs,
        n_errors=0,
        positive_witness=positive_witness,
        negative_witness=negative_witness,
        has_positive_witness=(positive_witness is not None),
        has_negative_witness=(negative_witness is not None),
        all_candidates_scanned=True,
        domain_coverage="complete",
        evidence_kind="numerical_sample",
        empirical_status=empirical_status,
        domain_relationship="grid_of_continuous_space",
        notes=notes + (
            f"wraps correspondence.contract.CorrespondenceReport(kind={report.kind!r}); "
            "tolerance-based (atol/rtol) sample, not an exact finite scan",
        ) + (_AGGREGATE_NEGATION_NOTE if not report.ok else ()),
    )


def claim_reports_from_macro_observability(
    report: MacroObservabilityReport,
    *,
    dynamics_claim_id: str,
    observability_claim_id: str,
    empirical_status: str = "synthetic_only",
) -> Tuple[ClaimReport, ClaimReport]:
    """Wrap H3's `MacroObservabilityReport` as TWO separate `ClaimReport`s
    -- dynamics correspondence (numerical_sample) and event observability
    (exhaustive_finite) -- never merged into one, per K8 (Plan: "Dynamik-
    verträglichkeit und Aussagebeobachtbarkeit sind separate
    Anforderungen")."""
    _require_empirical_status(empirical_status)
    n_actions = len(report.dynamics_reports)
    if n_actions == 0:
        # Defense in depth: macro_dynamics_and_observability itself already
        # refuses an empty P_by_action, but a hand-built MacroObservabilityReport
        # could still reach here (SCF_REVIEW_H0_H7_9dde420.md R4a).
        raise ScopeViolationError("claim_reports_from_macro_observability requires at least one declared micro action")

    dynamics_logical_status = "entailed_in_scope" if report.dynamics_exact else "negation_entailed_in_scope"
    dynamics_negative_witness = None
    dynamics_positive_witness = None
    if report.dynamics_exact:
        dynamics_positive_witness = {"n_actions": n_actions}
    else:
        worst_action, worst_report = max(report.dynamics_reports.items(), key=lambda kv: kv[1].max_defect)
        dynamics_negative_witness = {
            "micro_action": worst_action, "macro_action": worst_report.macro_action, "max_defect": worst_report.max_defect,
        }
    dynamics_claim = ClaimReport(
        claim_id=dynamics_claim_id,
        logical_status=dynamics_logical_status,
        search_complete=True,
        arithmetic_kind="float",
        n_domain=n_actions,
        n_evaluated=n_actions,
        n_admissible=n_actions,
        n_errors=0,
        positive_witness=dynamics_positive_witness,
        negative_witness=dynamics_negative_witness,
        has_positive_witness=(dynamics_positive_witness is not None),
        has_negative_witness=(dynamics_negative_witness is not None),
        all_candidates_scanned=True,
        domain_coverage="complete",
        evidence_kind="numerical_sample",
        empirical_status=empirical_status,
        domain_relationship="restricted_candidates",
        notes=(
            "wraps epistemic.observation_fibers.MacroObservabilityReport.dynamics_exact "
            "(check_controlled_correspondence, float tolerance); one concrete declared kernel per "
            "action, not a symbolic proof for every kernel satisfying some property",
        ) + (_AGGREGATE_NEGATION_NOTE if not report.dynamics_exact else ()),
    )

    observability_logical_status = "entailed_in_scope" if report.event_is_union_of_classes else "negation_entailed_in_scope"
    observability_claim = ClaimReport(
        claim_id=observability_claim_id,
        logical_status=observability_logical_status,
        search_complete=True,
        arithmetic_kind="boolean",
        n_domain=1,
        n_evaluated=1,
        n_admissible=1,
        n_errors=0,
        positive_witness={"micro_event": report.micro_event} if report.event_is_union_of_classes else None,
        negative_witness=None if report.event_is_union_of_classes else {"micro_event": report.micro_event},
        has_positive_witness=report.event_is_union_of_classes,
        has_negative_witness=not report.event_is_union_of_classes,
        all_candidates_scanned=True,
        domain_coverage="complete",
        evidence_kind="exhaustive_finite",
        empirical_status=empirical_status,
        domain_relationship="entire_finite_space",
        notes=(
            "wraps epistemic.observation_fibers.MacroObservabilityReport.event_is_union_of_classes "
            "(is_union_of_classes, exact combinatorial set-membership check, no numerical tolerance)",
        ),
    )
    return dynamics_claim, observability_claim


__all__ = ["claim_report_from_correspondence", "claim_reports_from_macro_observability"]
