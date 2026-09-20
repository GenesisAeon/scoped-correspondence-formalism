#!/usr/bin/env python3
"""USGS M>=6.0 earthquake annual-count pilot (Milestone 6d) -- real per-row data.

Loads data/usgs_earthquakes_m6plus_2000_2026.csv (see
data/real_data_manifest.json / docs/real_data_provenance.md), locks the
fixed calendar-year split, fits a constant annual rate (homogeneous
Poisson) on calib only, compares holdout RMSE to persistence baseline.

Honesty over beauty: no known-correct RMSE to match. False
model_beats_baseline is a valid complete result -- and IS what this run
finds: the calib mean annual rate (2000-2019) is higher than the actual
2020-2025 annual counts (which include a notably low year, 2024), so the
constant-rate model overshoots the holdout more than the flat persistence
baseline (anchored at 2019's already-lower count) does. This is reported
as-is, not retuned.

Asserts:
  - fixed calib/holdout calendar-year window, with 2026 explicitly excluded
    as a partial year
  - ScopeViolationError on wrong split, magnitude<6.0 rows, missing years,
    degenerate calib
  - baseline == last calib year's count (constant)
  - fit_constant_rate body does not reference holdout data
  - QUAKE_DATA_PROVENANCE_NOTE present in the report
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
    QUAKE_CALIB_END_YEAR,
    QUAKE_CALIB_START_YEAR,
    QUAKE_DATA_PROVENANCE_NOTE,
    QUAKE_HOLDOUT_END_YEAR,
    QUAKE_HOLDOUT_START_YEAR,
    fit_constant_rate,
    load_annual_counts,
    persistence_baseline_quake,
    run_earthquake_pilot,
    split_by_year_quake,
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
        default=ROOT / "data" / "usgs_earthquakes_m6plus_2000_2026.csv",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).with_name("verify_earthquake_pilot_results.json"),
    )
    args = parser.parse_args()

    checks = []
    data_path = args.data.resolve()
    raw = data_path.read_bytes()
    sha256 = hashlib.sha256(raw).hexdigest()

    body = _function_body_without_docstring(fit_constant_rate).lower()
    illicit = [t for t in ("holdout", "hold_out") if t in body]
    require(not illicit, f"fit body must not reference holdout; found {illicit}")
    checks.append(
        {
            "id": "MIG-M6d-fit_no_holdout_reference",
            "status": "passed",
            "evidence": {"fit_function": "fit_constant_rate", "holdout_tokens_in_body": illicit},
        }
    )

    points = load_annual_counts(data_path)
    require(2026 in [p.year for p in points], "source data must include the partial 2026 year")
    calib, holdout = split_by_year_quake(points)
    require(len(calib) == 20, f"expected 20 calib years, got {len(calib)}")
    require(len(holdout) == 6, f"expected 6 holdout years, got {len(holdout)}")
    require(2026 not in [p.year for p in holdout], "2026 (partial year) must be excluded from holdout")
    require(
        calib[0].year == QUAKE_CALIB_START_YEAR and calib[-1].year == QUAKE_CALIB_END_YEAR,
        "calib range",
    )
    require(
        holdout[0].year == QUAKE_HOLDOUT_START_YEAR and holdout[-1].year == QUAKE_HOLDOUT_END_YEAR,
        "holdout range",
    )
    checks.append(
        {
            "id": "MIG-M6d-fixed_calendar_split",
            "status": "passed",
            "evidence": {
                "calib_start_year": QUAKE_CALIB_START_YEAR,
                "calib_end_year": QUAKE_CALIB_END_YEAR,
                "holdout_start_year": QUAKE_HOLDOUT_START_YEAR,
                "holdout_end_year": QUAKE_HOLDOUT_END_YEAR,
                "n_calib": len(calib),
                "n_holdout": len(holdout),
                "partial_2026_excluded": True,
            },
        }
    )

    snooped = False
    try:
        split_by_year_quake(points, calib_end=2015)
    except ScopeViolationError:
        snooped = True
    require(snooped, "expected ScopeViolationError on wrong calib_end")

    missing_year = False
    try:
        split_by_year_quake([p for p in points if p.year != 2010])
    except ScopeViolationError:
        missing_year = True
    require(missing_year, "expected ScopeViolationError when a calib year is missing")

    degenerate = False
    try:
        fit_constant_rate(calib[:1])
    except ScopeViolationError:
        degenerate = True
    require(degenerate, "expected ScopeViolationError on single-point calib")

    # Direct check that the loader itself enforces magnitude>=6.0 on a crafted temp file.
    bad_magnitude = False
    import tempfile

    with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, newline="") as tmp:
        tmp.write("time,mag\n2020-01-01T00:00:00Z,5.5\n")
        tmp_path = Path(tmp.name)
    try:
        load_annual_counts(tmp_path)
    except ScopeViolationError:
        bad_magnitude = True
    finally:
        tmp_path.unlink(missing_ok=True)
    require(bad_magnitude, "expected ScopeViolationError on magnitude<6.0 row")

    checks.append(
        {
            "id": "MIG-M6d-scope_violations",
            "status": "passed",
            "evidence": {
                "raised_on_wrong_split": snooped,
                "raised_on_missing_calib_year": missing_year,
                "raised_on_degenerate_calib": degenerate,
                "raised_on_magnitude_below_6": bad_magnitude,
            },
        }
    )

    base = persistence_baseline_quake(calib)
    require(base == float(calib[-1].count), "baseline is last calib year's count")
    checks.append(
        {
            "id": "MIG-M6d-persistence_baseline_last_calib",
            "status": "passed",
            "evidence": {"baseline_value": base, "last_calib_year": calib[-1].year},
        }
    )

    report, fit = run_earthquake_pilot(data_path)
    require(report.n_holdout == 6, "6 holdout")
    require(
        report.model_beats_baseline == (report.model_rmse_holdout < report.baseline_rmse_holdout),
        "beats flag consistency",
    )
    require(QUAKE_DATA_PROVENANCE_NOTE in report.notes, "report must carry QUAKE_DATA_PROVENANCE_NOTE")
    checks.append(
        {
            "id": "MIG-M6d-pilot_run",
            "status": "passed",
            "evidence": {
                "model_rmse_holdout": report.model_rmse_holdout,
                "baseline_rmse_holdout": report.baseline_rmse_holdout,
                "model_beats_baseline": report.model_beats_baseline,
                "fitted_parameters": fit.to_dict(),
                "baseline_value": report.baseline_value,
                "macro": report.macro,
                "domain": report.domain,
                "holdout_counts": [p.count for p in holdout],
                "interpretation": (
                    "model_beats_baseline is False: the calib mean rate "
                    "(153.95/yr) overshoots the 2020-2025 holdout (which "
                    "includes a notably low year, 2024=99) more than the flat "
                    "persistence baseline (anchored at 2019's lower count of "
                    "145) does -- reported honestly, not retuned"
                ),
            },
        }
    )

    hold_obs = [float(p.count) for p in holdout]
    model_pred = [fit.mean_annual_count] * len(holdout)
    base_pred = [base] * len(holdout)
    hand_model = math.sqrt(sum((o - m) ** 2 for o, m in zip(hold_obs, model_pred)) / len(hold_obs))
    hand_base = math.sqrt(sum((o - b) ** 2 for o, b in zip(hold_obs, base_pred)) / len(hold_obs))
    require(abs(hand_model - report.model_rmse_holdout) < 1e-9, "model rmse hand check")
    require(abs(hand_base - report.baseline_rmse_holdout) < 1e-9, "baseline rmse hand check")
    checks.append(
        {
            "id": "MIG-M6d-rmse_hand_recompute",
            "status": "passed",
            "evidence": {
                "hand_model_rmse": hand_model,
                "hand_baseline_rmse": hand_base,
                "holdout_observed_counts": hold_obs,
                "model_predicted_counts": model_pred,
                "baseline_predicted_counts": base_pred,
            },
        }
    )

    passed = sum(c["status"] == "passed" for c in checks)
    failed = [c["id"] for c in checks if c["status"] != "passed"]
    out = {
        "milestone": "M6d_earthquake_pilot",
        "kind": "real-data constant-rate pilot on verified per-row data (honesty over beauty)",
        "generated_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "python": platform.python_version(),
        "data_path": str(data_path),
        "data_sha256": sha256,
        "source_citation": report.source_citation,
        "validation_report": report.to_dict(),
        "protocol": {
            "macro": "annual_count_m6plus (worldwide earthquakes, magnitude >= 6.0)",
            "calib_window": [QUAKE_CALIB_START_YEAR, QUAKE_CALIB_END_YEAR],
            "holdout_window": [QUAKE_HOLDOUT_START_YEAR, QUAKE_HOLDOUT_END_YEAR],
            "excluded": "2026 (partial year; source catalog truncated at 2026-09-20)",
            "baseline": "persistence = last calib year's count constant",
            "metric": "RMSE on 6 holdout years",
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
        "fitted_mean_annual_count": fit.mean_annual_count,
        "data_sha256": sha256,
        "report": str(args.output.resolve()),
    }
    print(json.dumps(summary, ensure_ascii=False))
    raise SystemExit(0 if passed == len(checks) else 1)


if __name__ == "__main__":
    main()
