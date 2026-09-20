#!/usr/bin/env python3
"""Cygnus X-1 jet PA pilot (Milestone 6) -- ILLUSTRATIVE, not empirical.

DATA PROVENANCE (AUDIT_ROADMAP.md item 1 / A01, resolved 2026-09-20): the
per-epoch data/cygnus_x1_radio_epochs.yaml table is UNVERIFIED -- only 4
aggregate Prabu-2026 values are confirmed; the 18 individually dated
epochs have no confirmed archival source and their MJD/year fields show a
pattern consistent with AI interpolation. This script's numbers are a
correct, reproducible calculation on that data, not an independently
verified empirical validation -- see DATA_PROVENANCE_WARNING.

Loads data/cygnus_x1_radio_epochs.yaml, locks DatasetManifest split, fits
relaxation on calib only, compares holdout RMSE to persistence baseline.

Honesty over beauty: no known-correct RMSE to match. False
model_beats_baseline is a valid complete result.

Asserts:
  - fixed split indices (0..8 / 9..17) — first 9 / last 9 epochs
  - ScopeViolationError on wrong split
  - baseline == last calib jet_pa_deg (constant)
  - fit_relaxation_pa body does not reference holdout data
  - DATA_PROVENANCE_WARNING is present in the report and its own module
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import inspect
import json
import platform
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from scoped_correspondence.errors import ScopeViolationError  # noqa: E402
from scoped_correspondence.validation import (  # noqa: E402
    fit_relaxation_pa,
    load_cygnus_epochs,
    persistence_baseline,
    run_cygnus_pilot,
    split_epochs,
)
from scoped_correspondence.validation.core import (  # noqa: E402
    CALIB_INDICES,
    DATA_PROVENANCE_WARNING,
    HOLDOUT_INDICES,
    cygnus_pa_manifest,
)


def require(ok, msg):
    if not bool(ok):
        raise AssertionError(msg)


def _function_body_without_docstring(fn) -> str:
    src = inspect.getsource(fn)
    if '"""' not in src:
        return src
    parts = src.split('"""')
    if len(parts) >= 3:
        return parts[0] + '"""'.join(parts[2:])
    return src


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data",
        type=Path,
        default=ROOT / "data" / "cygnus_x1_radio_epochs.yaml",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).with_name("verify_cygnus_pilot_results.json"),
    )
    args = parser.parse_args()

    checks = []
    data_path = args.data.resolve()
    raw = data_path.read_bytes()
    sha256 = hashlib.sha256(raw).hexdigest()

    body = _function_body_without_docstring(fit_relaxation_pa).lower()
    illicit = [t for t in ("holdout", "hold_out") if t in body]
    require(not illicit, f"fit body must not reference holdout; found {illicit}")
    checks.append(
        {
            "id": "MIG-M6-fit_no_holdout_reference",
            "status": "passed",
            "evidence": {
                "fit_function": "fit_relaxation_pa",
                "holdout_tokens_in_body": illicit,
                "note": (
                    "fit_relaxation_pa receives only calib epochs; holdout is "
                    "used solely for RMSE after the fit returns."
                ),
            },
        }
    )

    require(CALIB_INDICES == tuple(range(0, 9)), "calib indices")
    require(HOLDOUT_INDICES == tuple(range(9, 18)), "holdout indices")
    epochs = load_cygnus_epochs(data_path)
    require(len(epochs) == 18, "18 epochs")
    calib_years = [epochs[i].year for i in CALIB_INDICES]
    hold_years = [epochs[i].year for i in HOLDOUT_INDICES]
    require(calib_years[0] == 2006.2 and calib_years[-1] == 2014.0, f"calib years {calib_years}")
    require(hold_years[0] == 2015.2 and hold_years[-1] == 2023.8, f"holdout years {hold_years}")
    # Prompt parenthetical said calib through 2015.2 / holdout from 2016.1; by
    # strict first-9/last-9 index split the boundary is 2014.0 | 2015.2. Documented.
    checks.append(
        {
            "id": "MIG-M6-fixed_split_indices",
            "status": "passed",
            "evidence": {
                "calib_indices": list(CALIB_INDICES),
                "holdout_indices": list(HOLDOUT_INDICES),
                "calib_years": calib_years,
                "holdout_years": hold_years,
                "year_label_note": (
                    "Johann protocol: first 9 / last 9 by index. Actual years "
                    "calib 2006.2-2014.0, holdout 2015.2-2023.8 (prompt "
                    "parenthetical 2006.2-2015.2 / 2016.1-2023.8 was approximate)."
                ),
            },
        }
    )

    manifest = cygnus_pa_manifest(data_path)
    calib, holdout = split_epochs(epochs, manifest)
    require(len(calib) == 9 and len(holdout) == 9, "9+9 split")

    snooped = False
    try:
        split_epochs(epochs, manifest, calib_indices=tuple(range(0, 10)))
    except ScopeViolationError:
        snooped = True
    require(snooped, "expected ScopeViolationError on wrong calib indices")
    snooped2 = False
    try:
        split_epochs(
            epochs,
            manifest,
            holdout_indices=tuple(range(8, 17)),
        )
    except ScopeViolationError:
        snooped2 = True
    require(snooped2, "expected ScopeViolationError on wrong holdout indices")
    checks.append(
        {
            "id": "MIG-M6-scope_violation_on_wrong_split",
            "status": "passed",
            "evidence": {"raised_on_wrong_calib": True, "raised_on_wrong_holdout": True},
        }
    )

    # Audit finding A09: split_epochs only checked that the CALLER's indices
    # matched the manifest's own indices, not that the manifest itself was
    # internally sound -- a manifest built with holdout_indices==calib_indices
    # passed silently and produced identical calib/holdout epoch lists (a
    # leak). DatasetManifest.__post_init__ now rejects overlapping/duplicate/
    # out-of-range indices at construction time, so dataclasses.replace()
    # with the audit's exact leaky substitution must raise immediately.
    import dataclasses as _dc

    leak_raised = False
    try:
        _dc.replace(manifest, holdout_indices=manifest.calib_indices)
    except ScopeViolationError:
        leak_raised = True
    require(leak_raised, "manifest with holdout==calib_indices must raise at construction")

    dup_raised = False
    try:
        _dc.replace(manifest, calib_indices=(0, 0, 1))
    except ScopeViolationError:
        dup_raised = True
    require(dup_raised, "manifest with duplicate indices must raise")

    range_raised = False
    try:
        _dc.replace(manifest, calib_indices=(0, 1, 999))
    except ScopeViolationError:
        range_raised = True
    require(range_raised, "manifest with out-of-range index must raise")

    checks.append(
        {
            "id": "audit_a09_manifest_disjointness",
            "status": "passed",
            "evidence": {
                "overlapping_calib_holdout_raises": leak_raised,
                "duplicate_indices_raises": dup_raised,
                "out_of_range_index_raises": range_raised,
                "canonical_manifest_unaffected": True,
                "qualification": (
                    "canonical cygnus_pa_manifest() always used disjoint fixed "
                    "indices; this hardens the DatasetManifest contract itself, "
                    "not evidence of a leak in the real run."
                ),
            },
        }
    )

    calib_pa = [e.jet_pa_deg for e in calib]
    base = persistence_baseline(calib_pa)
    require(base == calib_pa[-1], "baseline is last calib PA")
    require(base == epochs[8].jet_pa_deg, "baseline == epoch index 8 PA")
    checks.append(
        {
            "id": "MIG-M6-persistence_baseline_last_calib",
            "status": "passed",
            "evidence": {
                "baseline_value": base,
                "last_calib_year": epochs[8].year,
                "last_calib_jet_pa_deg": epochs[8].jet_pa_deg,
            },
        }
    )

    report, manifest_out, fit = run_cygnus_pilot(data_path)
    require(manifest_out.calib_indices == CALIB_INDICES, "manifest calib")
    require(report.n_holdout == 9, "9 holdout")
    require(
        report.model_beats_baseline
        == (report.model_rmse_holdout < report.baseline_rmse_holdout),
        "beats flag consistency",
    )
    require("calib" in str(fit.note).lower() or "calibration" in str(fit.note).lower(), "calib-only note")
    checks.append(
        {
            "id": "MIG-M6-pilot_run",
            "status": "passed",
            "evidence": {
                "model_rmse_holdout": report.model_rmse_holdout,
                "baseline_rmse_holdout": report.baseline_rmse_holdout,
                "model_beats_baseline": report.model_beats_baseline,
                "fitted_parameters": fit.to_dict(),
                "baseline_value": report.baseline_value,
                "no_gamma_jet_reuse": True,
                "macro": report.macro,
                "domain": report.domain,
            },
        }
    )

    # Hand-check RMSE formulas from this run
    model_pred = [
        fit.pa_eq + (fit.pa0 - fit.pa_eq) * np.exp(-fit.r * (e.year - fit.t_ref))
        for e in holdout
    ]
    base_pred = [base] * 9
    obs = [e.jet_pa_deg for e in holdout]
    hand_model = float(np.sqrt(np.mean([(o - p) ** 2 for o, p in zip(obs, model_pred)])))
    hand_base = float(np.sqrt(np.mean([(o - p) ** 2 for o, p in zip(obs, base_pred)])))
    require(abs(hand_model - report.model_rmse_holdout) < 1e-12, "model rmse hand check")
    require(abs(hand_base - report.baseline_rmse_holdout) < 1e-12, "baseline rmse hand check")
    checks.append(
        {
            "id": "MIG-M6-rmse_hand_recompute",
            "status": "passed",
            "evidence": {
                "hand_model_rmse": hand_model,
                "hand_baseline_rmse": hand_base,
                "holdout_observed_pa": obs,
                "model_predicted_pa": [float(x) for x in model_pred],
                "baseline_predicted_pa": base_pred,
            },
        }
    )

    require(
        DATA_PROVENANCE_WARNING in report.notes,
        "ValidationReport.notes must carry DATA_PROVENANCE_WARNING",
    )
    checks.append(
        {
            "id": "audit_a01_data_provenance_warning",
            "status": "passed",
            "evidence": {
                "data_provenance_warning": DATA_PROVENANCE_WARNING,
                "in_report_notes": True,
                "in_manifest_license_note": "UNVERIFIED" in manifest.license_note,
            },
        }
    )

    passed = sum(c["status"] == "passed" for c in checks)
    failed = [c["id"] for c in checks if c["status"] != "passed"]
    out = {
        "milestone": "M6_cygnus_pilot",
        "kind": "illustrative method demonstration on unverified per-epoch data (honesty over beauty)",
        "generated_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "python": platform.python_version(),
        "numpy": np.__version__,
        "data_path": str(data_path),
        "data_sha256": sha256,
        "data_bytes": len(raw),
        "source_package": "GenesisAeon/cygnus-jet-utac",
        "citations": list(manifest.citations),
        "manifest": manifest.to_dict(),
        "validation_report": report.to_dict(),
        "protocol": {
            "macro": "jet_pa_deg",
            "split": "first 9 calib / last 9 holdout (indices 0-8 / 9-17)",
            "baseline": "persistence = last calib jet_pa_deg constant",
            "metric": "RMSE on 9 holdout epochs",
            "no_gamma_jet_sigma_reuse": True,
            "retune_after_holdout": False,
        },
        "count": len(checks),
        "passed": passed,
        "failed": len(failed),
        "empirical_validation": False,
        "data_provenance_warning": DATA_PROVENANCE_WARNING,
        "checks": checks,
    }
    args.output.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    summary = {
        "count": out["count"],
        "passed": out["passed"],
        "failed": failed,
        "model_rmse_holdout": report.model_rmse_holdout,
        "baseline_rmse_holdout": report.baseline_rmse_holdout,
        "model_beats_baseline": report.model_beats_baseline,
        "fitted_pa_eq": fit.pa_eq,
        "fitted_r": fit.r,
        "data_sha256": sha256,
        "report": str(args.output.resolve()),
    }
    print(json.dumps(summary, ensure_ascii=False))
    raise SystemExit(0 if passed == len(checks) else 1)


if __name__ == "__main__":
    main()
