#!/usr/bin/env python3
"""COVID World-vs-country decomposition (Milestone 6f) -- real per-row data.

NONSTATIONARY_ROADMAP.md package 2, response to
prompts/Answers/nicht_stationäre_Treiber/SCF_Nichtstationaere_Treiber_und_Kippen.md
(Astra, 2026-09-21) section 4 (heterogeneity/mixture identity): tests how
much of Pilot A's failure (covid_pilot.py, single exponential fit on the
World aggregate) is explained by China's share of world cases collapsing
from ~98% to <1% over the same window, rather than a genuine global rate
change.

Asserts:
  - loader rejects a non-China/World row and a negative RestOfWorld count
  - China's own fitted rate is negative (declining, matches the
    documented containment of the initial outbreak) and RestOfWorld's is
    positive and much larger in magnitude
  - the decomposed (China+RestOfWorld, separately extrapolated, then
    summed) model beats BOTH the same-window aggregate fit AND persistence
  - hand-recomputed RMSE for all three (decomposed, aggregate, persistence)
  - the mixture effective-rate diagnostic reproduces a handful of
    independently hand-computed (china_share, r_eff, actual_local_rate)
    triples
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
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
from scoped_correspondence.validation.covid_country_decomposition import (  # noqa: E402
    CALIB_END,
    CALIB_START,
    DATA_PROVENANCE_NOTE,
    HOLDOUT_END,
    HOLDOUT_START,
    load_china_world_series,
    mixture_effective_rate_diagnostic,
    run_covid_country_decomposition,
)
from scoped_correspondence.validation.covid_pilot import fit_exponential_growth, predict_exponential  # noqa: E402


def require(ok, msg):
    if not bool(ok):
        raise AssertionError(msg)


def near(a, b, atol=1e-9):
    if abs(float(a) - float(b)) > atol:
        raise AssertionError(f"{a!r} != {b!r} (atol={atol})")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data",
        type=Path,
        default=ROOT / "data" / "owid_covid_china_world_daily_2020.csv",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).with_name("verify_covid_country_decomposition_results.json"),
    )
    args = parser.parse_args()

    checks = []
    data_path = args.data.resolve()
    raw = data_path.read_bytes()
    sha256 = hashlib.sha256(raw).hexdigest()

    # Loader scope violations
    import csv
    import tempfile

    bad_location_raised = False
    with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, newline="") as tmp:
        tmp.write("date,location,new_cases,new_deaths,total_cases,total_deaths,weekly_cases,weekly_deaths,biweekly_cases,biweekly_deaths\n")
        tmp.write("2020-01-22,China,1,0,1,0,,,,\n")
        tmp.write("2020-01-22,Italy,1,0,1,0,,,,\n")
        tmp_path = Path(tmp.name)
    try:
        load_china_world_series(tmp_path)
    except ScopeViolationError:
        bad_location_raised = True
    finally:
        tmp_path.unlink(missing_ok=True)
    require(bad_location_raised, "expected ScopeViolationError on a non-China/World row")

    negative_row_raised = False
    with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, newline="") as tmp:
        tmp.write("date,location,new_cases,new_deaths,total_cases,total_deaths,weekly_cases,weekly_deaths,biweekly_cases,biweekly_deaths\n")
        tmp.write("2020-01-22,China,100,0,100,0,700,0,,\n")
        tmp.write("2020-01-22,World,50,0,50,0,350,0,,\n")  # World < China -> negative RestOfWorld
        tmp_path = Path(tmp.name)
    try:
        load_china_world_series(tmp_path)
    except ScopeViolationError:
        negative_row_raised = True
    finally:
        tmp_path.unlink(missing_ok=True)
    require(negative_row_raised, "expected ScopeViolationError on negative RestOfWorld")

    checks.append(
        {
            "id": "audit_loader_scope_violations",
            "status": "passed",
            "evidence": {"raised_on_non_china_world_row": bad_location_raised, "raised_on_negative_row": negative_row_raised},
        }
    )

    report, decomp = run_covid_country_decomposition(data_path)
    require(decomp.china_fit.r < 0, f"China's fitted rate must be negative (declining), got {decomp.china_fit.r!r}")
    require(decomp.row_fit.r > 0, f"RestOfWorld's fitted rate must be positive, got {decomp.row_fit.r!r}")
    require(decomp.row_fit.r > abs(decomp.china_fit.r), "RestOfWorld's growth must exceed China's decline in magnitude")
    require(decomp.decomposed_beats_aggregate, "decomposed model must beat the same-window aggregate fit")
    require(decomp.decomposed_beats_persistence, "decomposed model must beat persistence")
    checks.append(
        {
            "id": "audit_component_rates_and_decomposition_wins",
            "status": "passed",
            "evidence": {
                "china_r": decomp.china_fit.r,
                "row_r": decomp.row_fit.r,
                "aggregate_r_same_window": decomp.aggregate_fit_same_window.r,
                "decomposed_rmse": decomp.decomposed_rmse_holdout,
                "aggregate_rmse": decomp.aggregate_rmse_holdout,
                "persistence_rmse": decomp.persistence_rmse_holdout,
                "decomposed_beats_aggregate": decomp.decomposed_beats_aggregate,
                "decomposed_beats_persistence": decomp.decomposed_beats_persistence,
            },
        }
    )
    require(DATA_PROVENANCE_NOTE in report.notes, "report must carry DATA_PROVENANCE_NOTE")

    china_pts0, world_pts0, _ = load_china_world_series(data_path)
    first_share = china_pts0[0].cases_7day_avg / world_pts0[0].cases_7day_avg
    last_share = china_pts0[-1].cases_7day_avg / world_pts0[-1].cases_7day_avg
    near(first_share, 0.9849, atol=1e-3)
    near(last_share, 0.0012, atol=1e-3)
    checks.append(
        {
            "id": "audit_composition_shift_headline",
            "status": "passed",
            "evidence": {
                "first_date": china_pts0[0].date.isoformat(),
                "first_china_share": first_share,
                "last_date": china_pts0[-1].date.isoformat(),
                "last_china_share": last_share,
            },
        }
    )

    # Hand recompute all three RMSEs directly from the raw CSV, independent of the module's internals.
    china_pts, world_pts, row_pts = load_china_world_series(data_path)
    china_calib = [p for p in china_pts if CALIB_START <= p.date.isoformat() <= CALIB_END]
    world_calib = [p for p in world_pts if CALIB_START <= p.date.isoformat() <= CALIB_END]
    row_calib = [p for p in row_pts if CALIB_START <= p.date.isoformat() <= CALIB_END]
    china_hold = [p for p in china_pts if HOLDOUT_START <= p.date.isoformat() <= HOLDOUT_END]
    world_hold = [p for p in world_pts if HOLDOUT_START <= p.date.isoformat() <= HOLDOUT_END]
    row_hold = [p for p in row_pts if HOLDOUT_START <= p.date.isoformat() <= HOLDOUT_END]

    china_fit = fit_exponential_growth(china_calib)
    row_fit = fit_exponential_growth(row_calib)
    agg_fit = fit_exponential_growth(world_calib)

    hold_obs = [p.cases_7day_avg for p in world_hold]
    china_pred = [predict_exponential(float((p.date - china_fit.t_ref).days), r=china_fit.r, ln_cases0=china_fit.ln_cases0) for p in china_hold]
    row_pred = [predict_exponential(float((p.date - row_fit.t_ref).days), r=row_fit.r, ln_cases0=row_fit.ln_cases0) for p in row_hold]
    decomposed_pred = [c + r for c, r in zip(china_pred, row_pred)]
    agg_pred = [predict_exponential(float((p.date - agg_fit.t_ref).days), r=agg_fit.r, ln_cases0=agg_fit.ln_cases0) for p in world_hold]
    base = world_calib[-1].cases_7day_avg
    base_pred = [base] * len(world_hold)

    hand_decomposed_rmse = math.sqrt(sum((o - p) ** 2 for o, p in zip(hold_obs, decomposed_pred)) / len(hold_obs))
    hand_agg_rmse = math.sqrt(sum((o - p) ** 2 for o, p in zip(hold_obs, agg_pred)) / len(hold_obs))
    hand_base_rmse = math.sqrt(sum((o - b) ** 2 for o, b in zip(hold_obs, base_pred)) / len(hold_obs))
    near(hand_decomposed_rmse, decomp.decomposed_rmse_holdout)
    near(hand_agg_rmse, decomp.aggregate_rmse_holdout)
    near(hand_base_rmse, decomp.persistence_rmse_holdout)
    require(base == 31217.0 / 7.0, "baseline must match Pilot A's World baseline value exactly")
    checks.append(
        {
            "id": "audit_rmse_hand_recompute",
            "status": "passed",
            "evidence": {
                "hand_decomposed_rmse": hand_decomposed_rmse,
                "hand_aggregate_rmse": hand_agg_rmse,
                "hand_persistence_rmse": hand_base_rmse,
                "matches_pilot_a_baseline_value": True,
            },
        }
    )

    # Mixture effective-rate diagnostic: hand-recompute 3 checkpoints independently.
    diag = mixture_effective_rate_diagnostic(data_path)
    require(len(diag) == len(world_pts) - 2, "diagnostic must cover all interior points")
    by_date = {p.date.isoformat(): p for p in diag}
    spot_checks = {}
    for date_str in ["2020-01-29", "2020-02-26", "2020-03-18"]:
        point = by_date[date_str]
        idx = next(i for i, p in enumerate(world_pts) if p.date.isoformat() == date_str)
        china_v = china_pts[idx].cases_7day_avg
        world_v = world_pts[idx].cases_7day_avg
        row_v = row_pts[idx].cases_7day_avg
        hand_w_china = china_v / world_v
        hand_r_eff = hand_w_china * china_fit.r + (row_v / world_v) * row_fit.r
        w_before = world_pts[idx - 1].cases_7day_avg
        w_after = world_pts[idx + 1].cases_7day_avg
        hand_local_rate = (math.log(w_after) - math.log(w_before)) / 2.0
        near(point.china_share, hand_w_china, atol=1e-12)
        near(point.mixture_effective_rate, hand_r_eff, atol=1e-9)
        near(point.actual_local_rate, hand_local_rate, atol=1e-12)
        spot_checks[date_str] = point.to_dict()
    checks.append(
        {
            "id": "audit_mixture_rate_diagnostic_hand_recompute",
            "status": "passed",
            "evidence": {"spot_checked_dates": spot_checks},
        }
    )

    passed = sum(c["status"] == "passed" for c in checks)
    failed = [c["id"] for c in checks if c["status"] != "passed"]
    out = {
        "milestone": "M6f_covid_country_decomposition",
        "kind": "real-data heterogeneity-decomposition pilot on verified per-row data (honesty over beauty)",
        "generated_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "python": platform.python_version(),
        "data_path": str(data_path),
        "data_sha256": sha256,
        "source_citation": report.source_citation,
        "attribution_required": "CC BY 4.0: Data: Our World in Data / Johns Hopkins University CSSE COVID-19 Data Repository.",
        "validation_report": report.to_dict(),
        "count": len(checks),
        "passed": passed,
        "failed": len(failed),
        "checks": checks,
    }
    args.output.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    summary = {
        "count": out["count"],
        "passed": out["passed"],
        "failed": failed,
        "decomposed_rmse": decomp.decomposed_rmse_holdout,
        "aggregate_rmse": decomp.aggregate_rmse_holdout,
        "persistence_rmse": decomp.persistence_rmse_holdout,
        "china_r": decomp.china_fit.r,
        "row_r": decomp.row_fit.r,
        "data_sha256": sha256,
        "report": str(args.output.resolve()),
    }
    print(json.dumps(summary, ensure_ascii=False))
    raise SystemExit(0 if passed == len(checks) else 1)


if __name__ == "__main__":
    main()
