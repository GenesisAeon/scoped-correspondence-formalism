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

from typing import Optional, Tuple

from scoped_correspondence.correspondence.contract import CorrespondenceReport

from .observation_fibers import MacroObservabilityReport
from .records import EMPIRICAL_STATUSES, ClaimReport


def _require_empirical_status(empirical_status: str) -> None:
    if empirical_status not in EMPIRICAL_STATUSES:
        raise ValueError(f"empirical_status must be one of {EMPIRICAL_STATUSES}, got {empirical_status!r}")


def claim_report_from_correspondence(
    report: CorrespondenceReport,
    *,
    claim_id: str,
    empirical_status: str = "synthetic_only",
    notes: Tuple[str, ...] = (),
) -> ClaimReport:
    """Wrap a `CorrespondenceReport` as a `ClaimReport`. The claim is 'the
    declared conjugacy holds on the sampled (state, time) pairs' --
    `search_complete=True` refers only to that finite sample having been
    fully evaluated, NOT to any claim about the full (typically
    continuous) state/time space it was drawn from."""
    _require_empirical_status(empirical_status)
    n_pairs = int(report.evidence.get("n_pairs", len(report.residuals)))
    logical_status = "entailed_in_scope" if report.ok else "negation_entailed_in_scope"

    positive_witness = None
    negative_witness = None
    if report.ok:
        positive_witness = {"max_residual": report.max_residual, "n_pairs": n_pairs}
    else:
        finite_residuals = [r for r in report.residuals if r.value == r.value and abs(r.value) != float("inf")]
        worst = max(finite_residuals, key=lambda r: r.value, default=None)
        if worst is not None:
            negative_witness = {"at_state": worst.at_state, "at_time": worst.at_time, "residual": worst.value}
        else:
            negative_witness = {"note": "non-finite residual present; see report.evidence['all_finite']"}

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
        evidence_kind="numerical_sample",
        empirical_status=empirical_status,
        domain_relationship="grid_of_continuous_space",
        notes=notes + (
            f"wraps correspondence.contract.CorrespondenceReport(kind={report.kind!r}); "
            "tolerance-based (atol/rtol) sample, not an exact finite scan",
        ),
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
        evidence_kind="numerical_sample",
        empirical_status=empirical_status,
        domain_relationship="restricted_candidates",
        notes=(
            "wraps epistemic.observation_fibers.MacroObservabilityReport.dynamics_exact "
            "(check_controlled_correspondence, float tolerance); one concrete declared kernel per "
            "action, not a symbolic proof for every kernel satisfying some property",
        ),
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
