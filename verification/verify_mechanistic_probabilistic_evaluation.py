#!/usr/bin/env python3
"""Prediction intervals + proper scoring rules for the 3 mechanistic models (Milestone 49/50).

MECHANISTIC_VALIDATION_ROADMAP.md package 3, response to
prompts/Answers/nicht_stationäre_Treiber/SCF_Review_f8e249f.md (Astra,
2026-09-21): "Bisher liefern alle Module Punktschätzungen (RMSE, AIC)."

Checks (all numbers from this script run):
  1. scoring_rules hand checks: interval_score against a direct arithmetic
     recomputation (inside and outside the interval); poisson_log_score
     against scipy.stats.poisson.logpmf directly; poisson_prediction_interval
     against scipy.stats.poisson.ppf directly; empirical_coverage on a tiny
     hand-built example; ScopeViolationError paths.
  2. leave_one_origin_out_intervals on a tiny synthetic raw-predictions
     dict: the function's output is compared against an independent,
     manually-computed leave-one-out quantile and interval score for one
     specific trial.
  3. Energy balance probabilistic evaluation: all 4 package-2 predictors
     produce finite coverage/interval-score values (55 trials each: 11
     origins x 5 lead years). Reported as-is: the mechanistic model's
     interval score is actually WORSE than the simple baselines' here,
     even though its POINT forecasts (package 2) were better -- a
     genuine, unforced illustration of why point accuracy and predictive-
     interval quality are different questions.
  4. COVID renewal probabilistic evaluation: all 3 package-2 predictors
     produce finite coverage/interval-score values (42 trials each).
     renewal_constant_R has the best (lowest) interval score, consistent
     with its point-forecast win in package 2.
  5. ETAS probabilistic evaluation (Poisson log-score/coverage): reuses
     package 2's already-computed predictions (no new ETAS fit). Reported
     as-is: persistence has the best (lowest) mean log-score, consistent
     with its point-forecast win in package 2.

IMPORTANT: leave-one-origin-out quantiles use only 10 (energy balance) or
5 (COVID) other origins per lead time -- an explicitly small-sample,
exploratory diagnostic, not a claim of well-estimated tail quantiles.
NOT an exchangeability-based (conformal) guarantee -- see
scoring_rules.CONFORMAL_EXCHANGEABILITY_WARNING.
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
from scipy.stats import poisson as poisson_dist

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from scoped_correspondence.errors import ScopeViolationError  # noqa: E402
from scoped_correspondence.validation.scoring_rules import (  # noqa: E402
    SOURCE,
    CONFORMAL_EXCHANGEABILITY_WARNING,
    empirical_coverage,
    interval_score,
    poisson_log_score,
    poisson_prediction_interval,
)
from scoped_correspondence.validation.rolling_origin import RawHorizonPrediction  # noqa: E402
from scoped_correspondence.validation.mechanistic_probabilistic_evaluation import (  # noqa: E402
    DEFAULT_INTERVAL_ALPHA,
    leave_one_origin_out_intervals,
    run_covid_renewal_probabilistic_evaluation,
    run_energy_balance_probabilistic_evaluation,
    run_etas_probabilistic_evaluation,
)


def require(ok, msg):
    if not bool(ok):
        raise AssertionError(msg)


def near(a, b, atol=1e-8):
    if abs(float(a) - float(b)) > atol:
        raise AssertionError(f"{a!r} != {b!r} (atol={atol})")


def check_scoring_rules_hand_checks():
    # interval_score: inside the interval -> score == width.
    s_inside = interval_score(2.0, 5.0, 3.5, 0.2)
    near(s_inside, 3.0, atol=1e-12)
    # below lower: width + (2/alpha)*(lower-y)
    s_below = interval_score(2.0, 5.0, 0.0, 0.2)
    near(s_below, (5.0 - 2.0) + (2.0 / 0.2) * (2.0 - 0.0), atol=1e-12)
    # above upper: width + (2/alpha)*(y-upper)
    s_above = interval_score(2.0, 5.0, 9.0, 0.2)
    near(s_above, (5.0 - 2.0) + (2.0 / 0.2) * (9.0 - 5.0), atol=1e-12)

    bad_bounds = False
    try:
        interval_score(5.0, 2.0, 3.0, 0.2)
    except ScopeViolationError:
        bad_bounds = True
    require(bad_bounds, "expected ScopeViolationError for upper < lower")

    bad_alpha = False
    try:
        interval_score(2.0, 5.0, 3.0, 1.5)
    except ScopeViolationError:
        bad_alpha = True
    require(bad_alpha, "expected ScopeViolationError for alpha outside (0,1)")

    # poisson_log_score vs scipy directly.
    hand_ls = -float(poisson_dist.logpmf(7, 5.5))
    near(poisson_log_score(7, 5.5), hand_ls, atol=1e-12)

    # poisson_prediction_interval vs scipy.ppf directly.
    lam, cov = 12.0, 0.9
    hand_lo = float(poisson_dist.ppf((1 - cov) / 2, lam))
    hand_hi = float(poisson_dist.ppf(1 - (1 - cov) / 2, lam))
    lo, hi = poisson_prediction_interval(lam, cov)
    near(lo, hand_lo, atol=1e-12)
    near(hi, hand_hi, atol=1e-12)

    cov_val = empirical_coverage([(0.0, 2.0), (5.0, 6.0), (1.0, 1.0)], [1.0, 10.0, 1.0])
    near(cov_val, 2.0 / 3.0, atol=1e-12)

    bad_pred_mean = False
    try:
        poisson_log_score(3, -1.0)
    except ScopeViolationError:
        bad_pred_mean = True
    require(bad_pred_mean, "expected ScopeViolationError for non-positive predicted_mean")

    return {
        "interval_score_inside": s_inside,
        "interval_score_below": s_below,
        "interval_score_above": s_above,
        "poisson_log_score_hand": hand_ls,
        "poisson_interval_hand": [hand_lo, hand_hi],
        "empirical_coverage_hand": cov_val,
        "raised_on_bad_bounds": bad_bounds,
        "raised_on_bad_alpha": bad_alpha,
        "raised_on_bad_pred_mean": bad_pred_mean,
    }


def check_leave_one_origin_out_intervals_hand_check():
    """A tiny synthetic case, hand-computed independently of the module."""
    # Predictor "p": step=1 predictions at 5 origins, residuals (observed-predicted)
    # deliberately chosen so we can hand-verify one trial's LOO quantiles.
    origins = [0.0, 1.0, 2.0, 3.0, 4.0]
    predicted = [10.0, 10.0, 10.0, 10.0, 10.0]
    observed = [11.0, 9.0, 12.0, 8.0, 10.5]  # residuals: 1, -1, 2, -2, 0.5
    raw = {
        "p": [
            RawHorizonPrediction(origin=o, step=1, observed=obs, predicted=pred)
            for o, obs, pred in zip(origins, observed, predicted)
        ]
    }
    alpha = 0.4
    reports = leave_one_origin_out_intervals(raw, alpha=alpha)
    report = reports["p"]
    require(report.n_trials == 5, "expected 5 trials")

    # Hand-check trial for origin=0.0 (residual=1): LOO residuals are the other 4:
    # [-1, 2, -2, 0.5]. Interval = predicted + quantile(loo, [0.2, 0.8]).
    loo = [-1.0, 2.0, -2.0, 0.5]
    hand_lo = 10.0 + float(np.quantile(loo, 0.2))
    hand_hi = 10.0 + float(np.quantile(loo, 0.8))
    trial0 = next(t for t in report.per_trial if t["origin"] == 0.0)
    near(trial0["lower"], hand_lo, atol=1e-10)
    near(trial0["upper"], hand_hi, atol=1e-10)
    hand_score = interval_score(hand_lo, hand_hi, 11.0, alpha)
    near(trial0["interval_score"], hand_score, atol=1e-10)

    too_few = False
    try:
        tiny_raw = {"p": [RawHorizonPrediction(origin=0.0, step=1, observed=1.0, predicted=1.0), RawHorizonPrediction(origin=1.0, step=1, observed=1.0, predicted=1.0)]}
        leave_one_origin_out_intervals(tiny_raw, alpha=0.2)
    except ScopeViolationError:
        too_few = True
    require(too_few, "expected ScopeViolationError for too few LOO residuals")

    return {
        "n_trials": report.n_trials,
        "hand_lower_origin0": hand_lo,
        "hand_upper_origin0": hand_hi,
        "hand_interval_score_origin0": hand_score,
        "module_lower_origin0": trial0["lower"],
        "module_upper_origin0": trial0["upper"],
        "raised_on_too_few_loo_residuals": too_few,
    }


def check_energy_balance_probabilistic(co2_path, temp_path):
    reports = run_energy_balance_probabilistic_evaluation(co2_path, temp_path)
    require(set(reports) == {"persistence", "expanding", "last30", "energy_balance_mechanistic"}, "unexpected predictor set")
    for name, rep in reports.items():
        require(rep.n_trials == 55, f"{name}: expected 55 trials (11 origins x 5 lead years), got {rep.n_trials!r}")
        require(0.0 <= rep.empirical_coverage_value <= 1.0, f"{name}: coverage out of range")
        require(np.isfinite(rep.mean_interval_score) and rep.mean_interval_score > 0, f"{name}: interval score must be finite and positive")
    return {name: rep.to_dict() for name, rep in reports.items()}


def check_covid_renewal_probabilistic(data_path):
    reports = run_covid_renewal_probabilistic_evaluation(data_path)
    require(set(reports) == {"persistence", "exponential_extrapolation", "renewal_constant_R"}, "unexpected predictor set")
    for name, rep in reports.items():
        require(rep.n_trials == 42, f"{name}: expected 42 trials (6 origins x 7 days), got {rep.n_trials!r}")
        require(0.0 <= rep.empirical_coverage_value <= 1.0, f"{name}: coverage out of range")
        require(np.isfinite(rep.mean_interval_score) and rep.mean_interval_score > 0, f"{name}: interval score must be finite and positive")
    return {name: rep.to_dict() for name, rep in reports.items()}


def check_etas_probabilistic(catalog_path):
    result = run_etas_probabilistic_evaluation(catalog_path)
    require(set(result) == {"etas_first_order", "persistence", "constant_rate"}, "unexpected predictor set")
    for name, d in result.items():
        require(np.isfinite(d["mean_log_score"]), f"{name}: mean_log_score must be finite")
        require(0.0 <= d["empirical_coverage"] <= 1.0, f"{name}: coverage out of range")
    return result


CHECKS = [
    ("scoring_rules_hand_checks", check_scoring_rules_hand_checks),
    ("leave_one_origin_out_intervals_hand_check", check_leave_one_origin_out_intervals_hand_check),
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--co2-data", type=Path, default=ROOT / "data" / "noaa_mauna_loa_co2_annual_1959_2025.txt")
    parser.add_argument("--temp-data", type=Path, default=ROOT / "data" / "noaa_global_temp_anomaly_1880_2025.csv")
    parser.add_argument("--quake-data", type=Path, default=ROOT / "data" / "usgs_earthquakes_m6plus_2000_2026.csv")
    parser.add_argument("--covid-data", type=Path, default=ROOT / "data" / "owid_covid_world_daily_2020_2023.csv")
    parser.add_argument("--json-out", type=Path, default=Path(__file__).with_name("verify_mechanistic_probabilistic_evaluation_results.json"))
    args = parser.parse_args()

    co2_path = args.co2_data.resolve()
    temp_path = args.temp_data.resolve()
    quake_path = args.quake_data.resolve()
    covid_path = args.covid_data.resolve()

    checks = CHECKS + [
        ("energy_balance_probabilistic", lambda: check_energy_balance_probabilistic(co2_path, temp_path)),
        ("covid_renewal_probabilistic", lambda: check_covid_renewal_probabilistic(covid_path)),
        ("etas_probabilistic", lambda: check_etas_probabilistic(quake_path)),
    ]

    report = {
        "package": "MECHANISTIC_VALIDATION_ROADMAP.md package 3 (probabilistic evaluation)",
        "source": SOURCE,
        "conformal_exchangeability_warning": CONFORMAL_EXCHANGEABILITY_WARNING,
        "default_interval_alpha": DEFAULT_INTERVAL_ALPHA,
        "timestamp": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "python": sys.version.split()[0],
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "platform": platform.platform(),
        "checks": {},
        "disclaimer": (
            "Leave-one-origin-out quantiles use a small number of other origins per "
            "lead time -- an exploratory diagnostic, not a claim of well-estimated "
            "tail quantiles or conformal coverage."
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
