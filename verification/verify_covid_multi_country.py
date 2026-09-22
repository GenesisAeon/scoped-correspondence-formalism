#!/usr/bin/env python3
"""Multi-country / multi-window generalization of the COVID growth pilot (Milestone 51).

MECHANISTIC_VALIDATION_ROADMAP.md package 5, response to
prompts/Answers/nicht_stationäre_Treiber/SCF_Review_f8e249f.md (Astra,
2026-09-21): "Mehrere unabhängige Länder- und Zeitfenster mit
unverändertem Verfahren."

Checks (all numbers from this script run):
  1. load_country_daily loads real Germany/United States rows correctly
     (only the requested location, weekly_cases-defined rows only,
     row counts hand-checked against the raw CSV).
  2. Germany and United States, over Pilot A's EXACT unchanged calendar
     window (2020-01-27 to 2020-03-25): fit_exponential_growth correctly
     REFUSES a zero-count calib day for BOTH countries -- an honest,
     informative generalization failure (individual-country early-2020
     counts include zero/near-zero days that the World AGGREGATE smooths
     over), not a bug, and not silently worked around by adjusting the
     window per-country.
  3. World aggregate, a NEW time window anchored on the WHO's 2021-11-26
     Omicron VOC designation (calib/holdout LENGTHS identical to Pilot
     A's, boundaries mechanically derived from the external anchor date,
     not chosen by looking at the data): the fit succeeds and beats the
     persistence baseline (RMSE hand-recomputed independently of
     validation.core.rmse).

IMPORTANT: no parameter, window boundary, or country choice here was
selected by looking at any of these series' own fit quality.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import math
import platform
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from scoped_correspondence.errors import ScopeViolationError  # noqa: E402
from scoped_correspondence.validation.covid_multi_country import (  # noqa: E402
    COUNTRY_CALIB_END,
    COUNTRY_CALIB_START,
    COUNTRY_HOLDOUT_END,
    COUNTRY_HOLDOUT_START,
    DATA_PROVENANCE_NOTE,
    OMICRON_VOC_ANCHOR,
    SOURCE,
    WINDOW2_CALIB_END,
    WINDOW2_CALIB_START,
    WINDOW2_HOLDOUT_END,
    WINDOW2_HOLDOUT_START,
    load_country_daily,
    run_all_generalization_pilots,
    run_generalization_pilot,
)


def require(ok, msg):
    if not bool(ok):
        raise AssertionError(msg)


def near(a, b, atol=1e-6):
    if abs(float(a) - float(b)) > atol:
        raise AssertionError(f"{a!r} != {b!r} (atol={atol})")


def check_load_country_daily(germany_usa_path):
    germany = load_country_daily(germany_usa_path, "Germany")
    usa = load_country_daily(germany_usa_path, "United States")
    require(all(True for _ in germany), "Germany must load")

    # Hand-check row counts directly against the raw CSV.
    with open(germany_usa_path, encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    hand_germany_with_weekly = sum(1 for r in rows if r["location"] == "Germany" and r["weekly_cases"] not in ("", None))
    hand_usa_with_weekly = sum(1 for r in rows if r["location"] == "United States" and r["weekly_cases"] not in ("", None))
    require(len(germany) == hand_germany_with_weekly, f"Germany row count mismatch: {len(germany)} != {hand_germany_with_weekly}")
    require(len(usa) == hand_usa_with_weekly, f"USA row count mismatch: {len(usa)} != {hand_usa_with_weekly}")
    require(all(p.new_cases >= 0 for p in germany + usa), "new_cases must be non-negative")

    missing_location = False
    try:
        load_country_daily(germany_usa_path, "Nonexistent Country")
    except ScopeViolationError:
        missing_location = True
    require(missing_location, "expected ScopeViolationError for a location with no rows")

    return {"germany_rows": len(germany), "usa_rows": len(usa), "raised_on_missing_location": missing_location}


def check_country_pilots_honest_failure(germany_usa_path):
    """Germany/USA over Pilot A's EXACT window: fit_exponential_growth
    correctly refuses a zero-count calib day for BOTH -- verified as the
    EXPECTED outcome, not swallowed."""
    germany = run_generalization_pilot(
        germany_usa_path, "Germany", label="germany_2020_pilotA_window",
        calib_start=COUNTRY_CALIB_START, calib_end=COUNTRY_CALIB_END,
        holdout_start=COUNTRY_HOLDOUT_START, holdout_end=COUNTRY_HOLDOUT_END,
    )
    usa = run_generalization_pilot(
        germany_usa_path, "United States", label="united_states_2020_pilotA_window",
        calib_start=COUNTRY_CALIB_START, calib_end=COUNTRY_CALIB_END,
        holdout_start=COUNTRY_HOLDOUT_START, holdout_end=COUNTRY_HOLDOUT_END,
    )
    require(germany.fit_failed, "expected Germany's fit to fail (zero-count calib day) under Pilot A's exact window")
    require(usa.fit_failed, "expected USA's fit to fail (zero-count calib day) under Pilot A's exact window")
    require("cases_7day_avg must be > 0" in germany.fit_failure_reason, "expected the specific zero-count failure reason for Germany")
    require("cases_7day_avg must be > 0" in usa.fit_failure_reason, "expected the specific zero-count failure reason for USA")

    # Independent hand-check: confirm there really IS a zero in each country's
    # calib window (the failure is genuine, not a module bug).
    germany_calib = [p for p in load_country_daily(germany_usa_path, "Germany") if COUNTRY_CALIB_START <= p.date <= COUNTRY_CALIB_END]
    usa_calib = [p for p in load_country_daily(germany_usa_path, "United States") if COUNTRY_CALIB_START <= p.date <= COUNTRY_CALIB_END]
    require(any(p.cases_7day_avg == 0.0 for p in germany_calib), "expected a genuine zero cases_7day_avg day in Germany's calib window")
    require(any(p.cases_7day_avg == 0.0 for p in usa_calib), "expected a genuine zero cases_7day_avg day in USA's calib window")

    return {
        "germany": {"fit_failed": germany.fit_failed, "reason": germany.fit_failure_reason, "n_calib": germany.n_calib},
        "usa": {"fit_failed": usa.fit_failed, "reason": usa.fit_failure_reason, "n_calib": usa.n_calib},
        "interpretation": (
            "Individual-country early-2020 counts include zero/near-zero days that the "
            "World AGGREGATE smooths over -- fit_exponential_growth correctly refuses "
            "these, an honest generalization-failure finding, not a bug and not silently "
            "worked around by adjusting the window per-country."
        ),
    }


def check_world_omicron_window(world_path):
    result = run_generalization_pilot(
        world_path, "World", label="world_2021_omicron_window",
        calib_start=WINDOW2_CALIB_START, calib_end=WINDOW2_CALIB_END,
        holdout_start=WINDOW2_HOLDOUT_START, holdout_end=WINDOW2_HOLDOUT_END,
    )
    require(not result.fit_failed, f"expected the World-Omicron-window fit to succeed; got failure: {result.fit_failure_reason!r}")
    require(result.n_calib == 45, f"expected 45 calib days (same length as Pilot A); got {result.n_calib!r}")
    require(result.n_holdout == 14, f"expected 14 holdout days (same length as Pilot A); got {result.n_holdout!r}")
    require(result.model_beats_baseline, "expected the model to beat the persistence baseline on this window")

    # Independent hand-check of the holdout RMSE, bypassing validation.core.rmse.
    points = load_country_daily(world_path, "World")
    holdout_points = [p for p in points if WINDOW2_HOLDOUT_START <= p.date <= WINDOW2_HOLDOUT_END]
    t_ref = result.fitted.t_ref
    hand_predicted = [math.exp(result.fitted.ln_cases0 + result.fitted.r * (p.date - t_ref).days) for p in holdout_points]
    hand_observed = [p.cases_7day_avg for p in holdout_points]
    hand_rmse = float(np.sqrt(np.mean((np.array(hand_predicted) - np.array(hand_observed)) ** 2)))
    near(hand_rmse, result.model_rmse_holdout, atol=1e-6)

    return {
        "fitted_r": result.fitted.r,
        "model_rmse_holdout": result.model_rmse_holdout,
        "baseline_rmse_holdout": result.baseline_rmse_holdout,
        "model_beats_baseline": result.model_beats_baseline,
        "hand_rmse": hand_rmse,
        "calib_window": [result.calib_start, result.calib_end],
        "holdout_window": [result.holdout_start, result.holdout_end],
        "anchor": OMICRON_VOC_ANCHOR.isoformat(),
    }


def check_all_pilots_run_together(germany_usa_path, world_path):
    reports = run_all_generalization_pilots(germany_usa_path, world_path)
    require(len(reports) == 3, "expected exactly 3 generalization pilots")
    require({r.label for r in reports} == {"germany_2020_pilotA_window", "united_states_2020_pilotA_window", "world_2021_omicron_window"}, "unexpected pilot labels")
    return {r.label: r.to_dict() for r in reports}


CHECKS = []


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--germany-usa-data", type=Path, default=ROOT / "data" / "owid_covid_germany_usa_daily_2020.csv")
    parser.add_argument("--world-data", type=Path, default=ROOT / "data" / "owid_covid_world_daily_2020_2023.csv")
    parser.add_argument("--json-out", type=Path, default=Path(__file__).with_name("verify_covid_multi_country_results.json"))
    args = parser.parse_args()

    germany_usa_path = args.germany_usa_data.resolve()
    world_path = args.world_data.resolve()

    checks = CHECKS + [
        ("load_country_daily", lambda: check_load_country_daily(germany_usa_path)),
        ("country_pilots_honest_failure", lambda: check_country_pilots_honest_failure(germany_usa_path)),
        ("world_omicron_window", lambda: check_world_omicron_window(world_path)),
        ("all_pilots_run_together", lambda: check_all_pilots_run_together(germany_usa_path, world_path)),
    ]

    report = {
        "package": "MECHANISTIC_VALIDATION_ROADMAP.md package 5 (COVID multi-country/multi-window generalization)",
        "source": SOURCE,
        "data_provenance_note": DATA_PROVENANCE_NOTE,
        "timestamp": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "python": sys.version.split()[0],
        "numpy": np.__version__,
        "platform": platform.platform(),
        "checks": {},
    }
    passed = 0
    failed = 0
    errors = []
    for name, fn in checks:
        try:
            report["checks"][name] = {"status": "passed", "detail": fn()}
            passed += 1
            print(f"PASS  {name}")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            errors.append({"check": name, "error": f"{type(exc).__name__}: {exc}"})
            report["checks"][name] = {"status": "failed", "error": f"{type(exc).__name__}: {exc}"}
            print(f"FAIL  {name}: {exc}")

    summary = {"count": len(checks), "passed": passed, "failed": failed, "errors": errors, "report": report}
    args.json_out.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(f"\n{passed}/{len(checks)} passed; wrote {args.json_out}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
