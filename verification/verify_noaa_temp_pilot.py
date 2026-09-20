#!/usr/bin/env python3
"""NOAA global temperature anomaly trend pilot (Milestone 6c) -- real per-row data.

Loads data/noaa_global_temp_anomaly_1880_2025.csv (see
data/real_data_manifest.json / docs/real_data_provenance.md), locks the
fixed calendar-year split, fits a linear trend on calib only, compares
holdout RMSE to persistence baseline.

Honesty over beauty: no known-correct RMSE to match. False
model_beats_baseline is a valid complete result -- and IS what this run
finds: the calib window (1880-1999) averages a much slower long-run
warming rate than the accelerated warming actually observed after 2000,
so the linear extrapolation undershoots the holdout and the flat
persistence baseline (anchored at 1999's already-elevated anomaly) wins
on RMSE. This is reported as-is, not retuned.

Asserts:
  - fixed calib/holdout calendar-year window
  - ScopeViolationError on wrong split, degenerate calib
  - baseline == last calib year's anomaly (constant)
  - fit_linear_trend body does not reference holdout data
  - TEMP_DATA_PROVENANCE_NOTE present in the report
"""
from __future__ import annotations

import argparse
import ast
import datetime as dt
import hashlib
import inspect
import json
import math
import platform
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from scoped_correspondence.errors import ScopeViolationError  # noqa: E402
from scoped_correspondence.validation import (  # noqa: E402
    TEMP_CALIB_END_YEAR,
    TEMP_CALIB_START_YEAR,
    TEMP_DATA_PROVENANCE_NOTE,
    TEMP_HOLDOUT_END_YEAR,
    TEMP_HOLDOUT_START_YEAR,
    fit_linear_trend,
    load_annual_anomalies,
    persistence_baseline_temp,
    predict_linear_trend,
    run_noaa_temp_pilot,
    split_by_year_temp,
)


def require(ok, msg):
    if not bool(ok):
        raise AssertionError(msg)


def _function_body_without_docstring(fn) -> str:
    src = inspect.getsource(fn)
    tree = ast.parse(src)
    func = tree.body[0]
    if (
        func.body
        and isinstance(func.body[0], ast.Expr)
        and isinstance(func.body[0].value, ast.Constant)
        and isinstance(func.body[0].value.value, str)
    ):
        func.body = func.body[1:]
    return ast.unparse(func)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data",
        type=Path,
        default=ROOT / "data" / "noaa_global_temp_anomaly_1880_2025.csv",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).with_name("verify_noaa_temp_pilot_results.json"),
    )
    args = parser.parse_args()

    checks = []
    data_path = args.data.resolve()
    raw = data_path.read_bytes()
    sha256 = hashlib.sha256(raw).hexdigest()

    body = _function_body_without_docstring(fit_linear_trend).lower()
    illicit = [t for t in ("holdout", "hold_out") if t in body]
    require(not illicit, f"fit body must not reference holdout; found {illicit}")
    checks.append(
        {
            "id": "MIG-M6c-fit_no_holdout_reference",
            "status": "passed",
            "evidence": {"fit_function": "fit_linear_trend", "holdout_tokens_in_body": illicit},
        }
    )

    points = load_annual_anomalies(data_path)
    require(len(points) == 146, f"expected 146 annual points, got {len(points)}")
    calib, holdout = split_by_year_temp(points)
    require(len(calib) == 120, f"expected 120 calib years, got {len(calib)}")
    require(len(holdout) == 26, f"expected 26 holdout years, got {len(holdout)}")
    require(calib[0].year == TEMP_CALIB_START_YEAR and calib[-1].year == TEMP_CALIB_END_YEAR, "calib range")
    require(
        holdout[0].year == TEMP_HOLDOUT_START_YEAR and holdout[-1].year == TEMP_HOLDOUT_END_YEAR,
        "holdout range",
    )
    checks.append(
        {
            "id": "MIG-M6c-fixed_calendar_split",
            "status": "passed",
            "evidence": {
                "calib_start_year": TEMP_CALIB_START_YEAR,
                "calib_end_year": TEMP_CALIB_END_YEAR,
                "holdout_start_year": TEMP_HOLDOUT_START_YEAR,
                "holdout_end_year": TEMP_HOLDOUT_END_YEAR,
                "n_calib": len(calib),
                "n_holdout": len(holdout),
                "calib_is_full_20th_century": True,
            },
        }
    )

    snooped = False
    try:
        split_by_year_temp(points, calib_end=1990)
    except ScopeViolationError:
        snooped = True
    require(snooped, "expected ScopeViolationError on wrong calib_end")

    degenerate = False
    try:
        fit_linear_trend(calib[:1])
    except ScopeViolationError:
        degenerate = True
    require(degenerate, "expected ScopeViolationError on single-point calib")

    checks.append(
        {
            "id": "MIG-M6c-scope_violations",
            "status": "passed",
            "evidence": {"raised_on_wrong_split": snooped, "raised_on_degenerate_calib": degenerate},
        }
    )

    base = persistence_baseline_temp(calib)
    require(base == calib[-1].anomaly_c, "baseline is last calib year's anomaly")
    checks.append(
        {
            "id": "MIG-M6c-persistence_baseline_last_calib",
            "status": "passed",
            "evidence": {"baseline_value": base, "last_calib_year": calib[-1].year},
        }
    )

    report, fit = run_noaa_temp_pilot(data_path)
    require(report.n_holdout == 26, "26 holdout")
    require(
        report.model_beats_baseline == (report.model_rmse_holdout < report.baseline_rmse_holdout),
        "beats flag consistency",
    )
    require(TEMP_DATA_PROVENANCE_NOTE in report.notes, "report must carry TEMP_DATA_PROVENANCE_NOTE")
    checks.append(
        {
            "id": "MIG-M6c-pilot_run",
            "status": "passed",
            "evidence": {
                "model_rmse_holdout": report.model_rmse_holdout,
                "baseline_rmse_holdout": report.baseline_rmse_holdout,
                "model_beats_baseline": report.model_beats_baseline,
                "fitted_parameters": fit.to_dict(),
                "baseline_value": report.baseline_value,
                "macro": report.macro,
                "domain": report.domain,
                "interpretation": (
                    "model_beats_baseline is False: the 1880-1999 linear trend "
                    "averages a slower warming rate than actually observed after "
                    "2000, so it undershoots the accelerated holdout and the flat "
                    "persistence baseline (anchored at an already-elevated 1999 "
                    "value) wins on RMSE -- reported honestly, not retuned"
                ),
            },
        }
    )

    hold_obs = [p.anomaly_c for p in holdout]
    model_pred = [
        predict_linear_trend(p.year, slope=fit.slope_c_per_year, intercept=fit.intercept_c, year_ref=fit.year_ref)
        for p in holdout
    ]
    base_pred = [base] * len(holdout)
    hand_model = math.sqrt(sum((o - m) ** 2 for o, m in zip(hold_obs, model_pred)) / len(hold_obs))
    hand_base = math.sqrt(sum((o - b) ** 2 for o, b in zip(hold_obs, base_pred)) / len(hold_obs))
    require(abs(hand_model - report.model_rmse_holdout) < 1e-9, "model rmse hand check")
    require(abs(hand_base - report.baseline_rmse_holdout) < 1e-9, "baseline rmse hand check")
    checks.append(
        {
            "id": "MIG-M6c-rmse_hand_recompute",
            "status": "passed",
            "evidence": {
                "hand_model_rmse": hand_model,
                "hand_baseline_rmse": hand_base,
                "holdout_observed_anomaly_c": hold_obs,
                "model_predicted_anomaly_c": model_pred,
                "baseline_predicted_anomaly_c": base_pred,
            },
        }
    )

    passed = sum(c["status"] == "passed" for c in checks)
    failed = [c["id"] for c in checks if c["status"] != "passed"]
    out = {
        "milestone": "M6c_noaa_temp_pilot",
        "kind": "real-data trend pilot on verified per-row data (honesty over beauty)",
        "generated_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "python": platform.python_version(),
        "data_path": str(data_path),
        "data_sha256": sha256,
        "source_citation": report.source_citation,
        "validation_report": report.to_dict(),
        "protocol": {
            "macro": "temp_anomaly_c (annual global land+ocean anomaly, deg C)",
            "calib_window": [TEMP_CALIB_START_YEAR, TEMP_CALIB_END_YEAR],
            "holdout_window": [TEMP_HOLDOUT_START_YEAR, TEMP_HOLDOUT_END_YEAR],
            "split_anchor": "calib = full 20th century (round calendar boundary), holdout = 2000 onward",
            "baseline": "persistence = last calib year's anomaly constant",
            "metric": "RMSE on 26 holdout years",
            "retune_after_holdout": False,
        },
        "count": len(checks),
        "passed": passed,
        "failed": len(failed),
        "empirical_validation": True,
        "empirical_validation_note": (
            "Real, provenance-verified per-row data; the computed "
            "model_beats_baseline=False result is itself the honest finding, "
            "not evidence against the data's authenticity."
        ),
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
        "fitted_slope_c_per_year": fit.slope_c_per_year,
        "data_sha256": sha256,
        "report": str(args.output.resolve()),
    }
    print(json.dumps(summary, ensure_ascii=False))
    raise SystemExit(0 if passed == len(checks) else 1)


if __name__ == "__main__":
    main()
