"""Evidence adapter and real-data window (Paket MU6, plan §10/MU6).

Maps MU results onto the EXISTING evidence vocabularies of the epistemic
layer (no new vocabulary):

    plan wording             -> evidence_kind        , empirical_status
    synthetic simulation     -> "numerical_sample"   , "synthetic_only"
    algebraic / analytic     -> "analytic_argument"  , "not_tested"
    finite audit             -> "exhaustive_finite"  , "not_tested"
    real data (when allowed) -> "empirical_evaluation", "evaluated_on_declared_data"

Every record also carries ``record_kind`` so that a REAL SOURCE, a
SYNTHETIC MEASUREMENT and a FUTURE PROJECTION can never be confused in a
CLI or JSON output.

Real-data window: the data reference of the source paper (MU-S5,
DOI 10.3929/ethz-c-000802445) is CSV under "In Copyright - Non-Commercial
Use Permitted" (checked via DataCite on 2026-10-01); its schema has not
been inspected. It therefore must not be committed, and no decoder is
written against a guessed schema: the branch is ``deferred``. Even when
opened later (local, hash-checked, uncommitted), it may calibrate beam or
detection parameters only -- never stand in for an unmeasured gravity value.
A skipped data check is reported as ``skipped``, never as ``passed``.
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from typing import Any, Dict, Tuple

from scoped_correspondence.epistemic.records import EMPIRICAL_STATUSES, EVIDENCE_KINDS
from scoped_correspondence.errors import ScopeViolationError

RECORD_KINDS = ("real_source_metadata", "synthetic_measurement", "analytic_result", "finite_audit", "future_projection")
_MAP = {
    "synthetic_measurement": ("numerical_sample", "synthetic_only"),
    "analytic_result": ("analytic_argument", "not_tested"),
    "finite_audit": ("exhaustive_finite", "not_tested"),
    "future_projection": ("not_evaluated", "not_tested"),
    "real_source_metadata": ("not_evaluated", "not_tested"),
}

REAL_DATA_STATUS = {
    "source_id": "MU-S5",
    "doi": "10.3929/ethz-c-000802445",
    "status": "deferred",
    "license": "In Copyright - Non-Commercial Use Permitted (rightsstatements.org InC-NC/1.0)",
    "format": "text/csv (DataCite metadata)",
    "schema_checked": False,
    "may_be_committed": False,
    "allowed_use_if_opened": "local, hash-checked, uncommitted; calibration of beam/detection parameters only",
    "checked_on": "2026-10-01 via DataCite API (DOI resolver and repository returned 429/500)",
}


@dataclass(frozen=True)
class EvidenceRecord:
    record_kind: str
    claim: str
    source_ids: Tuple[str, ...]
    assumptions: Tuple[str, ...]
    values: Dict[str, Any] = field(default_factory=dict)
    limitations: Tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.record_kind not in RECORD_KINDS:
            raise ScopeViolationError(f"record_kind must be one of {RECORD_KINDS}")
        if self.record_kind == "real_source_metadata" and any(k.startswith("g_mu") or k == "a_mu" for k in self.values):
            raise ScopeViolationError("a source-metadata record cannot carry a muonium gravity value (none has been measured)")

    @property
    def evidence_kind(self) -> str:
        return _MAP[self.record_kind][0]

    @property
    def empirical_status(self) -> str:
        return _MAP[self.record_kind][1]

    def to_dict(self) -> Dict[str, Any]:
        assert self.evidence_kind in EVIDENCE_KINDS and self.empirical_status in EMPIRICAL_STATUSES
        return {"record_kind": self.record_kind, "evidence_kind": self.evidence_kind,
                "empirical_status": self.empirical_status, "claim": self.claim,
                "source_ids": list(self.source_ids), "assumptions": list(self.assumptions),
                "values": {k: json_safe(v) for k, v in self.values.items()}, "limitations": list(self.limitations)}


def json_safe(v: Any) -> Any:
    """Standard JSON: non-finite floats become explicit status markers."""
    if isinstance(v, float):
        if math.isnan(v):
            return {"status": "undefined"}
        if math.isinf(v):
            return {"status": "positive_infinity" if v > 0 else "negative_infinity"}
        return v
    if isinstance(v, (list, tuple)):
        return [json_safe(x) for x in v]
    if isinstance(v, dict):
        return {str(k): json_safe(x) for k, x in v.items()}
    if v is None or isinstance(v, (int, str, bool)):
        return v
    return str(v)


def dumps(obj: Any) -> str:
    return json.dumps(json_safe(obj), indent=2, allow_nan=False, sort_keys=True)


def real_data_check() -> Dict[str, Any]:
    """The real-data branch as a check result: 'skipped' (deferred), never 'passed'."""
    return {"check": "muonium_real_beam_data", "result": "skipped", "reason": REAL_DATA_STATUS["status"],
            "details": dict(REAL_DATA_STATUS)}


__all__ = ["RECORD_KINDS", "REAL_DATA_STATUS", "EvidenceRecord", "json_safe", "dumps", "real_data_check"]
