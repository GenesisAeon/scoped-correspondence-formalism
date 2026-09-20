#!/usr/bin/env python3
"""OWID/JHU World COVID growth-phase pilot (Milestone 6b) -- real per-row data.

Loads data/owid_covid_world_daily_2020_2023.csv (see
data/real_data_manifest.json / docs/real_data_provenance.md), locks the
fixed calendar split, fits exponential growth on calib only, compares
holdout RMSE to persistence baseline.

Honesty over beauty: no known-correct RMSE to match. False
model_beats_baseline is a valid complete result -- and IS what this run
finds: the calib window (2020-01-27 to 2020-03-11) spans a real regime
change (the initial China outbreak, its containment/dip in late February,
then the onset of global spread), so a single log-linear fit badly
underestimates the accelerating holdout window and the flat persistence
baseline wins on RMSE. This is reported as-is, not retuned.

Asserts:
  - fixed calib/holdout calendar window
  - ScopeViolationError on wrong split, non-World rows, degenerate calib
  - baseline == last calib cases_7day_avg (constant)
  - fit_exponential_growth body does not reference holdout data
  - DATA_PROVENANCE_NOTE present in the report
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
    CALIB_END,
    CALIB_START,
    COVID_DATA_PROVENANCE_NOTE,
    HOLDOUT_END,
    HOLDOUT_START,
    fit_exponential_growth,
    load_world_daily,
    persistence_baseline_covid,
    predict_exponential,
    run_covid_pilot,
    split_by_date,
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
        default=ROOT / "data" / "owid_covid_world_daily_2020_2023.csv",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).with_name("verify_covid_pilot_results.json"),
    )
    args = parser.parse_args()

    checks = []
    data_path = args.data.resolve()
    raw = data_path.read_bytes()
    sha256 = hashlib.sha256(raw).hexdigest()

    body = _function_body_without_docstring(fit_exponential_growth).lower()
    illicit = [t for t in ("holdout", "hold_out") if t in body]
    require(not illicit, f"fit body must not reference holdout; found {illicit}")
    checks.append(
        {
            "id": "MIG-M6b-fit_no_holdout_reference",
            "status": "passed",
            "evidence": {"fit_function": "fit_exponential_growth", "holdout_tokens_in_body": illicit},
        }
    )

    points = load_world_daily(data_path)
    require(len(points) >= 59, f"expected at least 59 dated points, got {len(points)}")
    calib, holdout = split_by_date(points)
    require(len(calib) == 45, f"expected 45 calib days, got {len(calib)}")
    require(len(holdout) == 14, f"expected 14 holdout days, got {len(holdout)}")
    require(calib[0].date == CALIB_START, "calib start")
    require(calib[-1].date == CALIB_END, "calib end")
    require(holdout[0].date == HOLDOUT_START, "holdout start")
    require(holdout[-1].date == HOLDOUT_END, "holdout end")
    checks.append(
        {
            "id": "MIG-M6b-fixed_calendar_split",
            "status": "passed",
            "evidence": {
                "calib_start": CALIB_START.isoformat(),
                "calib_end": CALIB_END.isoformat(),
                "holdout_start": HOLDOUT_START.isoformat(),
                "holdout_end": HOLDOUT_END.isoformat(),
                "n_calib": len(calib),
                "n_holdout": len(holdout),
                "calib_end_is_who_pandemic_declaration": True,
            },
        }
    )

    # Scope violations: wrong split, non-World row, degenerate calib
    snooped = False
    try:
        split_by_date(points, calib_end=dt.date(2020, 3, 1))
    except ScopeViolationError:
        snooped = True
    require(snooped, "expected ScopeViolationError on wrong calib_end")

    degenerate = False
    try:
        fit_exponential_growth(calib[:1])
    except ScopeViolationError:
        degenerate = True
    require(degenerate, "expected ScopeViolationError on single-point calib")

    checks.append(
        {
            "id": "MIG-M6b-scope_violations",
            "status": "passed",
            "evidence": {"raised_on_wrong_split": snooped, "raised_on_degenerate_calib": degenerate},
        }
    )

    base = persistence_baseline_covid(calib)
    require(base == calib[-1].cases_7day_avg, "baseline is last calib cases_7day_avg")
    checks.append(
        {
            "id": "MIG-M6b-persistence_baseline_last_calib",
            "status": "passed",
            "evidence": {
                "baseline_value": base,
                "last_calib_date": calib[-1].date.isoformat(),
                "last_calib_weekly_cases": calib[-1].weekly_cases,
            },
        }
    )

    report, fit = run_covid_pilot(data_path)
    require(report.n_holdout == 14, "14 holdout")
    require(
        report.model_beats_baseline == (report.model_rmse_holdout < report.baseline_rmse_holdout),
        "beats flag consistency",
    )
    require(COVID_DATA_PROVENANCE_NOTE in report.notes, "report must carry COVID_DATA_PROVENANCE_NOTE")
    checks.append(
        {
            "id": "MIG-M6b-pilot_run",
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
                    "model_beats_baseline is False: the calib window spans a real "
                    "regime change (initial China outbreak, containment dip, then "
                    "global-wave onset), so the single log-linear fit "
                    "underestimates the accelerating holdout and the flat "
                    "persistence baseline wins on RMSE -- reported honestly, not retuned"
                ),
            },
        }
    )

    # Hand-check RMSE formulas from this run
    hold_obs = [p.cases_7day_avg for p in holdout]
    model_pred = [
        predict_exponential(float((p.date - fit.t_ref).days), r=fit.r, ln_cases0=fit.ln_cases0)
        for p in holdout
    ]
    base_pred = [base] * len(holdout)
    hand_model = math.sqrt(sum((o - m) ** 2 for o, m in zip(hold_obs, model_pred)) / len(hold_obs))
    hand_base = math.sqrt(sum((o - b) ** 2 for o, b in zip(hold_obs, base_pred)) / len(hold_obs))
    require(abs(hand_model - report.model_rmse_holdout) < 1e-9, "model rmse hand check")
    require(abs(hand_base - report.baseline_rmse_holdout) < 1e-9, "baseline rmse hand check")
    checks.append(
        {
            "id": "MIG-M6b-rmse_hand_recompute",
            "status": "passed",
            "evidence": {
                "hand_model_rmse": hand_model,
                "hand_baseline_rmse": hand_base,
                "holdout_observed_cases_7day_avg": hold_obs,
                "model_predicted_cases_7day_avg": model_pred,
                "baseline_predicted_cases_7day_avg": base_pred,
            },
        }
    )

    passed = sum(c["status"] == "passed" for c in checks)
    failed = [c["id"] for c in checks if c["status"] != "passed"]
    out = {
        "milestone": "M6b_covid_pilot",
        "kind": "real-data growth-phase pilot on verified per-row data (honesty over beauty)",
        "generated_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "python": platform.python_version(),
        "data_path": str(data_path),
        "data_sha256": sha256,
        "source_citation": report.source_citation,
        "attribution_required": "CC BY 4.0: Data: Our World in Data / Johns Hopkins University CSSE COVID-19 Data Repository.",
        "validation_report": report.to_dict(),
        "protocol": {
            "macro": "cases_7day_avg (weekly_cases / 7)",
            "calib_window": [CALIB_START.isoformat(), CALIB_END.isoformat()],
            "holdout_window": [HOLDOUT_START.isoformat(), HOLDOUT_END.isoformat()],
            "split_anchor": "calib_end = WHO pandemic declaration (2020-03-11), holdout = fixed next 14 days",
            "baseline": "persistence = last calib cases_7day_avg constant",
            "metric": "RMSE on 14 holdout days",
            "retune_after_holdout": False,
        },
        "count": len(checks),
        "passed": passed,
        "failed": len(failed),
        "empirical_validation": True,
        "empirical_validation_note": (
            "Real, provenance-verified per-row data (unlike the Cygnus pilot, "
            "see validation.core.DATA_PROVENANCE_WARNING); the computed "
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
        "fitted_r": fit.r,
        "data_sha256": sha256,
        "report": str(args.output.resolve()),
    }
    print(json.dumps(summary, ensure_ascii=False))
    raise SystemExit(0 if passed == len(checks) else 1)


if __name__ == "__main__":
    main()
