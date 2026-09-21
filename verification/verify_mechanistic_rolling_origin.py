#!/usr/bin/env python3
"""Common temporal forecast evaluation across the 3 mechanistic models (Milestone 48).

MECHANISTIC_VALIDATION_ROADMAP.md package 2, response to
prompts/Answers/nicht_stationäre_Treiber/SCF_Review_f8e249f.md (Astra,
2026-09-21): validation.rolling_origin's already-verified generic harness,
applied for the FIRST time to energy_balance.py, etas.py, and
covid_renewal.py, each adapted to its own natural forecasting target.

Checks (all numbers from this script run):
  1. Energy balance rolling-origin: reuses the EXACT SAME origins
     (1969..2019, step 5) and horizon (5 years) as
     noaa_temp_pilot.run_noaa_rolling_origin_backtest, for a directly
     comparable result; all 4 predictors' pooled RMSE are finite and
     positive; ONE origin's mechanistic prediction is independently
     hand-recomputed (direct fit_energy_balance_model_from_series +
     integrate_energy_balance_trajectory call on manually-sliced arrays)
     and compared to the harness's own per-origin RMSE for that origin.
  2. Energy balance horizon-step breakdown: RMSE reported separately per
     lead year (1..5), not pooled -- responds directly to Astra's
     "Fehler getrennt nach Horizont ausweisen" ask.
  3. ETAS forecast check: fits ETAS on calib-only events (2000-2019,
     explicit t_end=2020-01-01 observation window), computes the
     first-order expected count per holdout year (2020-2025) via
     etas_expected_count_first_order, and compares against
     earthquake_pilot.py's OWN already-established persistence and
     constant-rate baselines on the EXACT SAME holdout years -- the
     holdout observed counts are cross-checked against that pilot's own
     documented values (121,157,127,147,99,145) as an integrity check.
     Reported as-is, no retuning: ETAS does NOT beat the persistence
     baseline here (RMSE 26.3 vs 23.0), though it does beat the
     homogeneous-Poisson constant-rate baseline (28.8) -- a genuine,
     unforced mixed result.
  4. COVID renewal rolling-origin: several origins within the same
     March-2020 window as covid_renewal.py's own analysis, 7-day horizon;
     all 3 predictors' pooled RMSE finite and positive.

IMPORTANT: model selection (bounds, initial guesses, generation-interval
parameters) is fixed by the already-shipped fitting functions BEFORE this
script runs -- nothing here was tuned by looking at rolling-origin
performance.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import platform
import sys
from pathlib import Path

import numpy as np
import scipy

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from scoped_correspondence.validation.mechanistic_rolling_origin import (  # noqa: E402
    SOURCE,
    COVID_RENEWAL_HORIZON_DAYS,
    COVID_RENEWAL_ORIGINS_DAY_INDEX,
    run_covid_renewal_rolling_origin_backtest,
    run_energy_balance_rolling_origin_analysis,
    run_etas_forecast_check,
)
from scoped_correspondence.validation.noaa_temp_pilot import (  # noqa: E402
    ROLLING_ORIGIN_HORIZON_YEARS,
    ROLLING_ORIGIN_YEARS,
)
from scoped_correspondence.dynamics.energy_balance import (  # noqa: E402
    _load_overlap_series,
    fit_energy_balance_model_from_series,
    integrate_energy_balance_trajectory,
)


def require(ok, msg):
    if not bool(ok):
        raise AssertionError(msg)


def near(a, b, atol=1e-6):
    if abs(float(a) - float(b)) > atol:
        raise AssertionError(f"{a!r} != {b!r} (atol={atol})")


def check_energy_balance_rolling_origin_and_horizon(co2_path, temp_path):
    """Runs the pooled AND per-horizon-step analyses via the SAME shared-cache
    call (avoids a third redundant set of 11 calib-only refits in this
    check on top of the module's own internal sharing).
    """
    report, horizon_report = run_energy_balance_rolling_origin_analysis(co2_path, temp_path)
    require(report.origins == tuple(float(y) for y in ROLLING_ORIGIN_YEARS), "must reuse NOAA's exact origins")
    require(report.horizon == float(ROLLING_ORIGIN_HORIZON_YEARS), "must reuse NOAA's exact horizon")
    require(set(report.predictor_names) == {"persistence", "expanding", "last30", "energy_balance_mechanistic"}, "unexpected predictor set")
    for name, val in report.pooled_rmse.items():
        require(np.isfinite(val) and val > 0, f"{name}: pooled RMSE must be finite and positive, got {val!r}")

    require(horizon_report.steps == tuple(range(1, ROLLING_ORIGIN_HORIZON_YEARS + 1)), "unexpected step range")
    for name, by_step in horizon_report.rmse_by_step.items():
        require(set(by_step) == set(horizon_report.steps), f"{name}: missing steps")
        for k, v in by_step.items():
            require(np.isfinite(v) and v > 0, f"{name} step {k}: RMSE must be finite and positive, got {v!r}")

    # Independent hand-check: pick one origin, refit+project directly (bypassing the
    # module's private predictor closure/cache), and confirm it matches the harness's
    # own per-origin RMSE for the mechanistic predictor.
    check_origin = 1999.0
    origin_result = next(o for o in report.per_origin if o.origin == check_origin)
    years_all, Tobs_all, F_vals_all = _load_overlap_series(co2_path, temp_path)
    year_to_idx = {y: i for i, y in enumerate(years_all)}
    calib_years = [y for y in years_all if y <= check_origin]
    test_years = [y for y in years_all if check_origin < y <= check_origin + ROLLING_ORIGIN_HORIZON_YEARS]
    calib_Tobs = np.array([Tobs_all[year_to_idx[y]] for y in calib_years])
    F_calib = np.array([F_vals_all[year_to_idx[y]] for y in calib_years])
    fit = fit_energy_balance_model_from_series(calib_years, calib_Tobs, F_calib)
    combined_years = list(range(calib_years[0], test_years[-1] + 1))
    F_combined = np.array([F_vals_all[year_to_idx[y]] for y in combined_years])
    pred_combined = integrate_energy_balance_trajectory(F_combined, fit.params)
    pred_by_year = dict(zip(combined_years, pred_combined))
    hand_pred = np.array([pred_by_year[y] for y in test_years])
    test_obs = np.array([Tobs_all[year_to_idx[y]] for y in test_years])
    hand_rmse = float(np.sqrt(np.mean((hand_pred - test_obs) ** 2)))
    near(hand_rmse, origin_result.rmse_by_predictor["energy_balance_mechanistic"], atol=1e-8)

    return {
        "pooled_rmse": report.pooled_rmse,
        "rmse_by_step": {name: dict(by_step) for name, by_step in horizon_report.rmse_by_step.items()},
        "hand_checked_origin": check_origin,
        "hand_rmse": hand_rmse,
        "harness_rmse": origin_result.rmse_by_predictor["energy_balance_mechanistic"],
    }


def check_etas_forecast(catalog_path):
    result = run_etas_forecast_check(catalog_path)
    require(result["holdout_years"] == [2020, 2021, 2022, 2023, 2024, 2025], "must reuse earthquake_pilot.py's exact holdout years")
    require(
        result["observed_counts"] == [121.0, 157.0, 127.0, 147.0, 99.0, 145.0],
        f"holdout observed counts must match earthquake_pilot.py's own documented values; got {result['observed_counts']!r}",
    )
    for key in ("rmse_etas_first_order", "rmse_persistence", "rmse_constant_rate"):
        require(np.isfinite(result[key]) and result[key] > 0, f"{key} must be finite and positive")
    require(np.isfinite(result["calib_branching_ratio"]) and result["calib_branching_ratio"] > 0, "branching ratio must be finite and positive")
    return result


def check_covid_renewal_rolling_origin(data_path):
    report = run_covid_renewal_rolling_origin_backtest(data_path)
    require(report.origins == tuple(float(o) for o in COVID_RENEWAL_ORIGINS_DAY_INDEX), "must reuse the declared origins")
    require(report.horizon == float(COVID_RENEWAL_HORIZON_DAYS), "must reuse the declared horizon")
    require(set(report.predictor_names) == {"persistence", "exponential_extrapolation", "renewal_constant_R"}, "unexpected predictor set")
    for name, val in report.pooled_rmse.items():
        require(np.isfinite(val) and val > 0, f"{name}: pooled RMSE must be finite and positive, got {val!r}")
    return {"pooled_rmse": report.pooled_rmse}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--co2-data", type=Path, default=ROOT / "data" / "noaa_mauna_loa_co2_annual_1959_2025.txt")
    parser.add_argument("--temp-data", type=Path, default=ROOT / "data" / "noaa_global_temp_anomaly_1880_2025.csv")
    parser.add_argument("--quake-data", type=Path, default=ROOT / "data" / "usgs_earthquakes_m6plus_2000_2026.csv")
    parser.add_argument("--covid-data", type=Path, default=ROOT / "data" / "owid_covid_world_daily_2020_2023.csv")
    parser.add_argument("--json-out", type=Path, default=Path(__file__).with_name("verify_mechanistic_rolling_origin_results.json"))
    args = parser.parse_args()

    co2_path = args.co2_data.resolve()
    temp_path = args.temp_data.resolve()
    quake_path = args.quake_data.resolve()
    covid_path = args.covid_data.resolve()

    checks = [
        ("energy_balance_rolling_origin_and_horizon", lambda: check_energy_balance_rolling_origin_and_horizon(co2_path, temp_path)),
        ("etas_forecast_check", lambda: check_etas_forecast(quake_path)),
        ("covid_renewal_rolling_origin", lambda: check_covid_renewal_rolling_origin(covid_path)),
    ]

    report = {
        "package": "MECHANISTIC_VALIDATION_ROADMAP.md package 2 (common temporal forecast evaluation)",
        "source": SOURCE,
        "timestamp": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "python": sys.version.split()[0],
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "platform": platform.platform(),
        "checks": {},
        "disclaimer": (
            "No parameter here was chosen by looking at rolling-origin performance; "
            "model selection is fixed by the already-shipped fitting functions."
        ),
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
