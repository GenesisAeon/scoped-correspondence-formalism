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
    """A tiny synthetic case, hand-computed independently of the module.

    Fixed 2026-09-23 in response to
    prompts/Answers/nicht_stationäre_Treiber/SCF_Review_3e8dce3.md
    (Astra, finding 1): 7 origins now (not 5), because the fixed function
    only calibrates a trial from STRICTLY EARLIER origins -- the first 3
    origins here lack enough earlier history and are skipped, and a new
    regression check (Astra's own suggested test) verifies that changing
    a LATER origin's observation does NOT change an EARLIER origin's
    already-reported interval.
    """
    origins = [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
    predicted = [10.0] * 7
    observed = [11.0, 9.0, 12.0, 8.0, 10.5, 13.0, 7.0]  # residuals: 1,-1,2,-2,0.5,3,-3
    step_size = 1.0
    alpha = 0.4

    def build_raw(obs):
        return {
            "p": [
                RawHorizonPrediction(origin=o, step=1, observed=ob, predicted=pred)
                for o, ob, pred in zip(origins, obs, predicted)
            ]
        }

    reports = leave_one_origin_out_intervals(build_raw(observed), alpha=alpha, step_size=step_size)
    report = reports["p"]
    # Origins 0,1,2 each have < 3 strictly-earlier same-step residuals
    # (origin=2 has only origins 0,1 earlier -> 2 < MIN_LOO_RESIDUALS=3) and
    # are skipped; origins 3,4,5,6 each have >= 3 earlier origins.
    require(report.n_skipped_insufficient_lookback == 3, f"expected 3 skipped trials, got {report.n_skipped_insufficient_lookback!r}")
    require(report.n_trials == 4, f"expected 4 trials (origins 3,4,5,6), got {report.n_trials!r}")

    # Hand-check trial for origin=3.0 (residual=-2): eligible LOO residuals
    # are ONLY from STRICTLY EARLIER origins (o' + step*step_size <= 3.0,
    # i.e. o' <= 2.0): origins 0,1,2 -> residuals [1, -1, 2]. Origins 4,5,6
    # (later) must NOT contribute, even though they share the same step.
    loo = [1.0, -1.0, 2.0]
    hand_lo = 10.0 + float(np.quantile(loo, 0.2))
    hand_hi = 10.0 + float(np.quantile(loo, 0.8))
    trial3 = next(t for t in report.per_trial if t["origin"] == 3.0)
    near(trial3["lower"], hand_lo, atol=1e-10)
    near(trial3["upper"], hand_hi, atol=1e-10)
    hand_score = interval_score(hand_lo, hand_hi, 8.0, alpha)
    near(trial3["interval_score"], hand_score, atol=1e-10)

    # CENTRAL REGRESSION TEST (Astra's own recommendation): "Spätere Daten
    # dürfen frühere Prognosen nicht verändern." Mutate the LATEST origin's
    # observation drastically and confirm origin=3's interval/score are
    # bit-identical -- this is exactly the failure mode Astra demonstrated
    # against the pre-fix code (an earlier interval moving from [1.2, 2.8]
    # to [1.2, 80.4] purely from a later origin's observation changing).
    mutated_observed = list(observed)
    mutated_observed[6] = 999.0
    reports_mutated = leave_one_origin_out_intervals(build_raw(mutated_observed), alpha=alpha, step_size=step_size)
    trial3_mutated = next(t for t in reports_mutated["p"].per_trial if t["origin"] == 3.0)
    later_data_changed_earlier_interval = (
        trial3_mutated["lower"] != trial3["lower"] or trial3_mutated["upper"] != trial3["upper"] or trial3_mutated["interval_score"] != trial3["interval_score"]
    )
    require(not later_data_changed_earlier_interval, "later origin's observation changed an earlier origin's interval -- data leakage regressed")

    too_few = False
    try:
        tiny_raw = {"p": [RawHorizonPrediction(origin=0.0, step=1, observed=1.0, predicted=1.0), RawHorizonPrediction(origin=1.0, step=1, observed=1.0, predicted=1.0)]}
        leave_one_origin_out_intervals(tiny_raw, alpha=0.2, step_size=1.0)
    except ScopeViolationError:
        too_few = True
    require(too_few, "expected ScopeViolationError when zero trials have sufficient lookback")

    return {
        "n_trials": report.n_trials,
        "n_skipped_insufficient_lookback": report.n_skipped_insufficient_lookback,
        "hand_lower_origin3": hand_lo,
        "hand_upper_origin3": hand_hi,
        "hand_interval_score_origin3": hand_score,
        "module_lower_origin3": trial3["lower"],
        "module_upper_origin3": trial3["upper"],
        "later_data_changed_earlier_interval": later_data_changed_earlier_interval,
        "raised_on_zero_valid_trials": too_few,
    }


def check_energy_balance_probabilistic(co2_path, temp_path):
    """55 raw (origin, step) pairs (11 origins x 5 lead years) exist, but per
    the finding-1 fix (SCF_Review_3e8dce3.md), only trials with >= 3
    STRICTLY EARLIER same-step origins are actually scored: origins are 5
    years apart (1969..2019), so origin index i has exactly i earlier
    origins available regardless of step -- the first 3 origins (i=0,1,2:
    1969,1974,1979) never reach the >=3 threshold for ANY step, so exactly
    3 origins x 5 steps = 15 trials are honestly skipped, leaving 40.
    """
    reports = run_energy_balance_probabilistic_evaluation(co2_path, temp_path)
    require(set(reports) == {"persistence", "expanding", "last30", "energy_balance_mechanistic"}, "unexpected predictor set")
    for name, rep in reports.items():
        require(rep.n_trials == 40, f"{name}: expected 40 time-eligible trials (55 raw - 15 insufficient-lookback), got {rep.n_trials!r}")
        require(rep.n_skipped_insufficient_lookback == 15, f"{name}: expected 15 skipped trials, got {rep.n_skipped_insufficient_lookback!r}")
        require(0.0 <= rep.empirical_coverage_value <= 1.0, f"{name}: coverage out of range")
        require(np.isfinite(rep.mean_interval_score) and rep.mean_interval_score > 0, f"{name}: interval score must be finite and positive")
    return {name: rep.to_dict() for name, rep in reports.items()}


def check_covid_renewal_probabilistic(data_path):
    """42 raw (origin, step) pairs (6 origins x 7 days) exist; per the
    finding-1 fix, origins are 5 days apart (day-index 25..50), horizon
    1-7 days. For steps 1-5, origin index i needs i earlier origins (>=3
    means index >=3: origins 40,45,50 qualify, 25/30/35 do not); for steps
    6-7, origin index i needs i-1 earlier origins that are also >= one
    full step-size gap away (>=3 means index >=4: origins 45,50 qualify).
    That is (3 origins x 5 steps) + (4 origins x 2 steps) = 23 skipped,
    leaving 19.
    """
    reports = run_covid_renewal_probabilistic_evaluation(data_path)
    require(set(reports) == {"persistence", "exponential_extrapolation", "renewal_constant_R"}, "unexpected predictor set")
    for name, rep in reports.items():
        require(rep.n_trials == 19, f"{name}: expected 19 time-eligible trials (42 raw - 23 insufficient-lookback), got {rep.n_trials!r}")
        require(rep.n_skipped_insufficient_lookback == 23, f"{name}: expected 23 skipped trials, got {rep.n_skipped_insufficient_lookback!r}")
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
