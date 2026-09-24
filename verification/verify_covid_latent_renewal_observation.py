#!/usr/bin/env python3
"""COVID latent renewal dynamics vs. reporting/observation process (Milestone 56).

CAPABILITY_EXPANSION_ROADMAP.md Priority 2. Checks:

  1. ``fit_weekday_multipliers`` hand check: a synthetic 14-day series with
     a KNOWN weekday reporting pattern (weekends at half the weekday rate)
     recovers the exact expected normalized multipliers.
  2. ``weekday_adjusted_mean`` hand check + ScopeViolationError guards for
     both functions (missing weekday, non-positive means, short window).
  3. Real-data application on the SAME forecast origins/horizons as
     ``run_covid_renewal_rolling_origin_backtest``
     (COVID_RENEWAL_ORIGINS_DAY_INDEX / COVID_RENEWAL_HORIZON_DAYS,
     unchanged): the OLD (Poisson-on-renewal-mean) and NEW (weekday-
     adjusted negative-binomial) variants are compared with the SAME
     underlying renewal-equation dynamics -- reported as-is, whichever
     wins.
  4. Astra's 2026-09-24 (SCF_Review_dc5d82a.md, finding R6) full 2x2
     ablation (weekday: on/off x distribution: Poisson/negative-binomial),
     each mean variant with its OWN separately-fit dispersion: isolates
     that negative-binomial overdispersion alone is the strong finding
     (2.4% -> 73.8% coverage), while the weekday correction on top actually
     WORSENS both coverage-adjacent calibration and log-score on this exact
     42-trial window (10.2 -> 11.8) -- corrected from the earlier framing,
     which bundled both changes and credited their combined effect without
     isolating which one does the work.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from scoped_correspondence.errors import ScopeViolationError  # noqa: E402
from scoped_correspondence.validation.covid_latent_renewal_observation import (  # noqa: E402
    SOURCE, MIN_CALIB_DAYS, DEFAULT_COVERAGE,
    fit_weekday_multipliers, weekday_adjusted_mean,
    run_covid_latent_renewal_observation_comparison, run_covid_ablation_comparison,
)
from scoped_correspondence.validation.scoring_rules import (  # noqa: E402
    neg_binom_prediction_interval, poisson_prediction_interval, _nb_mean_dispersion_to_n_p,
)
from scipy.stats import nbinom as _nbinom_dist  # noqa: E402


def require(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)


def check_weekday_multiplier_hand_recovery():
    dates = [dt.date(2024, 1, 1) + dt.timedelta(days=i) for i in range(14)]  # Mon 2024-01-01
    require(dates[0].weekday() == 0, "sanity: 2024-01-01 must be a Monday")
    true_mult = {0: 1.0, 1: 1.0, 2: 1.0, 3: 1.0, 4: 1.0, 5: 0.5, 6: 0.5}
    reference_mean = [100.0] * 14
    observed_raw = [reference_mean[i] * true_mult[dates[i].weekday()] for i in range(14)]

    got = fit_weekday_multipliers(dates, observed_raw, reference_mean)
    mean_true = sum(true_mult.values()) / 7.0
    expected = {wd: v / mean_true for wd, v in true_mult.items()}
    for wd in range(7):
        require(abs(got[wd] - expected[wd]) < 1e-9, f"weekday {wd}: got {got[wd]}, want {expected[wd]}")

    adjusted = weekday_adjusted_mean(dates[0], 200.0, got)
    require(abs(adjusted - 200.0 * expected[0]) < 1e-9, f"weekday_adjusted_mean mismatch: {adjusted}")

    for bad_kwargs, exc_from in (
        (dict(dates=dates[:10], observed_raw=observed_raw[:10], reference_mean=reference_mean[:10]), "short_window"),
        (dict(dates=dates, observed_raw=observed_raw, reference_mean=[0.0] * 14), "nonpositive_reference"),
    ):
        try:
            fit_weekday_multipliers(**bad_kwargs)
            raise AssertionError(f"fit_weekday_multipliers should reject {exc_from}")
        except ScopeViolationError:
            pass

    only_six_weekdays_dates = [d for d in dates if d.weekday() != 6]
    only_six_ref = [100.0] * len(only_six_weekdays_dates)
    only_six_obs = [100.0] * len(only_six_weekdays_dates)
    try:
        fit_weekday_multipliers(only_six_weekdays_dates, only_six_obs, only_six_ref)
        raise AssertionError("fit_weekday_multipliers should reject a window missing one weekday entirely")
    except ScopeViolationError:
        pass

    try:
        weekday_adjusted_mean(dates[0], -5.0, got)
        raise AssertionError("weekday_adjusted_mean should reject a non-positive latent_mean")
    except ScopeViolationError:
        pass

    return {"recovered_multipliers": {str(k): v for k, v in got.items()}}


def check_real_data_application(covid_path):
    r = run_covid_latent_renewal_observation_comparison(covid_path, coverage=DEFAULT_COVERAGE)
    require(r.n_trials > 0, "zero trials")
    require(r.n_calib_days >= MIN_CALIB_DAYS, f"n_calib_days {r.n_calib_days} < {MIN_CALIB_DAYS}")
    require(r.fitted_dispersion >= 0.0, f"negative dispersion {r.fitted_dispersion}")
    require(0.0 <= r.old_empirical_coverage <= 1.0, "old coverage out of range")
    require(0.0 <= r.new_empirical_coverage <= 1.0, "new coverage out of range")
    require(np.isfinite(r.old_mean_log_score) and np.isfinite(r.new_mean_log_score), "non-finite mean log score")
    require(set(r.weekday_multipliers) == set(range(7)), "weekday_multipliers must cover all 7 weekdays")
    require(abs(sum(r.weekday_multipliers.values()) / 7.0 - 1.0) < 1e-9, "weekday_multipliers must average to 1")
    for t in r.trials:
        require(t.old_predicted_mean > 0.0 and t.new_predicted_mean > 0.0, "non-positive predicted mean in a trial")
        require(np.isfinite(t.old_log_score) and np.isfinite(t.new_log_score), "non-finite trial log score")
    return {
        "n_trials": r.n_trials,
        "n_calib_days": r.n_calib_days,
        "fitted_dispersion": round(r.fitted_dispersion, 4),
        "weekday_multipliers": {str(k): round(v, 4) for k, v in r.weekday_multipliers.items()},
        "old_mean_log_score": round(r.old_mean_log_score, 4),
        "new_mean_log_score": round(r.new_mean_log_score, 4),
        "old_empirical_coverage": round(r.old_empirical_coverage, 4),
        "new_empirical_coverage": round(r.new_empirical_coverage, 4),
        "new_wins_log_score": r.new_wins_log_score,
    }


def check_ablation_comparison(covid_path):
    """SCF_Review_dc5d82a.md finding R6: the full 2x2 ablation, checked against
    Astra's exact independently-computed numbers (matched to 3 decimal places
    when this check was written): dispersion 0.8207 (no weekday) / 0.9118
    (weekday); coverage 2.38% / 0.00% / 73.81% / 73.81%; mean log-score
    1387.465 / 2490.044 / 10.192 / 11.751 for (Poisson, no wd), (Poisson, wd),
    (NB, no wd), (NB, wd) respectively. Confirms NB alone is the strong
    finding and the weekday correction WORSENS both metrics here.
    """
    out = run_covid_ablation_comparison(covid_path, coverage=DEFAULT_COVERAGE)
    require(set(out) == {(False, False), (True, False), (False, True), (True, True)}, f"unexpected keys: {set(out)}")
    for key, v in out.items():
        require(v.n_trials > 0, f"{key}: zero trials")
        require(0.0 <= v.empirical_coverage <= 1.0, f"{key}: coverage out of range")
        require(np.isfinite(v.mean_log_score), f"{key}: non-finite log score")

    poisson_no_wd, poisson_wd = out[(False, False)], out[(True, False)]
    nb_no_wd, nb_wd = out[(False, True)], out[(True, True)]

    require(nb_no_wd.mean_log_score < poisson_no_wd.mean_log_score,
            "negative-binomial (no weekday) must massively beat Poisson (no weekday) on log-score")
    require(nb_no_wd.empirical_coverage > poisson_no_wd.empirical_coverage,
            "negative-binomial (no weekday) must beat Poisson (no weekday) on coverage")
    require(nb_wd.mean_log_score > nb_no_wd.mean_log_score,
            f"the weekday correction should WORSEN the NB log-score here ({nb_wd.mean_log_score} should exceed {nb_no_wd.mean_log_score})")
    require(abs(nb_wd.empirical_coverage - nb_no_wd.empirical_coverage) < 1e-9,
            "the weekday correction should not improve NB coverage on this window")

    return {key_str: v.to_dict() for key_str, v in
            (("poisson_no_weekday", poisson_no_wd), ("poisson_weekday", poisson_wd),
             ("nb_no_weekday", nb_no_wd), ("nb_weekday", nb_wd))}


def check_neg_binom_prediction_interval_against_scipy():
    mean, dispersion, coverage = 50.0, 0.3, 0.8
    got = neg_binom_prediction_interval(mean, dispersion, coverage)
    n, p = _nb_mean_dispersion_to_n_p(mean, dispersion)
    alpha = 1.0 - coverage
    want = (float(_nbinom_dist.ppf(alpha / 2.0, n, p)), float(_nbinom_dist.ppf(1.0 - alpha / 2.0, n, p)))
    require(got == want, f"neg_binom_prediction_interval vs direct scipy call: got {got}, want {want}")

    poisson_limit = neg_binom_prediction_interval(mean, 0.0, coverage)
    poisson_direct = poisson_prediction_interval(mean, coverage)
    require(poisson_limit == poisson_direct,
            f"neg_binom_prediction_interval at dispersion=0 must equal the Poisson interval exactly: "
            f"{poisson_limit} vs {poisson_direct}")

    for bad in (dict(predicted_mean=-1.0), dict(dispersion=-0.1), dict(coverage=1.5)):
        kwargs = dict(predicted_mean=mean, dispersion=dispersion, coverage=coverage)
        kwargs.update(bad)
        try:
            neg_binom_prediction_interval(**kwargs)
            raise AssertionError(f"neg_binom_prediction_interval should reject {bad}")
        except ScopeViolationError:
            pass
    return {"interval_at_mean_50_dispersion_0.3_coverage_0.8": list(got)}


CHECKS = [
    ("weekday_multiplier_hand_recovery", check_weekday_multiplier_hand_recovery),
    ("neg_binom_prediction_interval_against_scipy", check_neg_binom_prediction_interval_against_scipy),
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--covid-data", type=Path, default=ROOT / "data" / "owid_covid_world_daily_2020_2023.csv")
    parser.add_argument("--json-out", type=Path, default=Path(__file__).with_name("verify_covid_latent_renewal_observation_results.json"))
    args = parser.parse_args()
    covid_path = args.covid_data.resolve()

    checks = CHECKS + [
        ("real_data_application", lambda: check_real_data_application(covid_path)),
        ("ablation_comparison", lambda: check_ablation_comparison(covid_path)),
    ]

    report = {
        "package": "CAPABILITY_EXPANSION_ROADMAP.md Priority 2 (COVID latent renewal + observation)",
        "source": SOURCE,
        "default_coverage": DEFAULT_COVERAGE,
        "timestamp": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "python": sys.version.split()[0],
        "checks": {},
    }

    all_ok = True
    for name, fn in checks:
        try:
            detail = fn()
            report["checks"][name] = {"status": "pass", "detail": detail}
            print(f"PASS  {name}")
        except AssertionError as e:
            all_ok = False
            report["checks"][name] = {"status": "fail", "error": str(e)}
            print(f"FAIL  {name}: {e}")
        except Exception as e:  # noqa: BLE001
            all_ok = False
            report["checks"][name] = {"status": "error", "error": f"{type(e).__name__}: {e}"}
            print(f"ERROR {name}: {type(e).__name__}: {e}")

    args.json_out.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    print(f"\n{sum(1 for c in report['checks'].values() if c['status'] == 'pass')}/{len(checks)} checks passed")
    print(f"Report written to {args.json_out}")
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
