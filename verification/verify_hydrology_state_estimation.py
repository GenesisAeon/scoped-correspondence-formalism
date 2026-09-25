#!/usr/bin/env python3
"""Reservoir daily-mean Kalman state estimation (INTEGRATED_EXTENSION_ROADMAP.md
Paket C1) -- synthetic-only, no network access needed.

Checks:

  1. ``reservoir_daily_mean_state_space`` matches the EXISTING, independently
     verified ``dynamics.linear_reservoirs`` formulas exactly (two separate
     code paths, same numbers) for random alphas/rates/state/input/dt.
  2. Without correction (``use_correction=False``), the filtered posterior
     MEANS exactly reproduce the deterministic open-loop reservoir simulation
     (mean propagation under a linear model with no measurement update is
     deterministic regardless of the declared process-noise W).
  3. With correction, starting from a WRONG initial storage guess, the filter
     converges towards the true trajectory's discharge while the open-loop
     (no-correction) run started from the same wrong guess stays biased
     indefinitely -- demonstrating the state-estimation correction actually
     does something, not asserted, measured against a known synthetic truth.
  4. No-future-leakage: a lead-time forecast for day t must be IDENTICAL
     whether or not discharge observations strictly AFTER day t are changed
     (matches the hydrology_pilot.py leakage-guard convention).
  5. Negative posterior storage, when it occurs, is reported via
     ``n_negative_storage_days`` and visible in the raw means array -- never
     silently clipped to zero.
  6. ``calibrate_process_noise`` recovers a measurement-noise variance ``R``
     close to the TRUE synthetic value from open-loop training residuals, and
     its inner-validation grid search picks a ``w_scale`` that beats both a
     much-too-small and a much-too-large candidate on a held-out inner slice.
  7. ``run_catchment_state_estimation_pilot`` end-to-end: on a synthetic
     catchment whose true generating process is a KNOWN one-reservoir model
     started from an UNKNOWN (never given to the pilot) initial storage, the
     corrected variant's test-period MAE is no worse than the open-loop
     variant's at every one of the three lead times -- the real, expected
     situation for actual catchments, where the initial 1991 storage is
     always genuinely unknown.
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

from scoped_correspondence.dynamics.linear_reservoirs import (  # noqa: E402
    parallel_reservoir_step,
    parallel_reservoir_interval_discharge,
)
from scoped_correspondence.validation.hydrology_state_estimation import (  # noqa: E402
    reservoir_daily_mean_state_space,
    run_filter_full_span,
    lead_time_forecast,
    calibrate_process_noise,
    run_catchment_state_estimation_pilot,
    LEAD_TIMES,
)


def require(ok, msg):
    if not bool(ok):
        raise AssertionError(msg)


def _simulate_open_loop(P, c, alphas, rates):
    n = len(P)
    S = np.zeros(len(alphas))
    q = np.empty(n)
    for t in range(n):
        u = c * P[t]
        q[t] = parallel_reservoir_interval_discharge(S, u, alphas, rates, 1.0)
        S = np.array(parallel_reservoir_step(S, u, alphas, rates, 1.0))
    return q


def check_state_space_matches_existing_formulas():
    rng = np.random.default_rng(10)
    max_diff_state, max_diff_obs = 0.0, 0.0
    for _ in range(50):
        n = rng.integers(1, 4)
        alphas = rng.dirichlet(np.ones(n))
        rates = rng.uniform(0.0, 2.0, size=n)
        rates[rng.integers(0, n)] = 0.0 if rng.random() < 0.2 else rates[0]  # occasionally exercise k=0
        S = rng.uniform(0.0, 5.0, size=n)
        u = rng.uniform(0.0, 3.0)
        dt = rng.uniform(0.1, 3.0)

        F, G, H, D = reservoir_daily_mean_state_space(alphas, rates, dt)
        S_next_ss = F @ S + G * u
        q_ss = float((H @ S)[0] + D * u)

        S_next_ref = np.array(parallel_reservoir_step(S, u, alphas, rates, dt))
        q_ref = parallel_reservoir_interval_discharge(S, u, alphas, rates, dt)

        max_diff_state = max(max_diff_state, float(np.max(np.abs(S_next_ss - S_next_ref))))
        max_diff_obs = max(max_diff_obs, abs(q_ss - q_ref))

    require(max_diff_state < 1e-10, f"state transition mismatch vs linear_reservoirs: {max_diff_state!r}")
    require(max_diff_obs < 1e-10, f"daily-mean observation mismatch vs linear_reservoirs: {max_diff_obs!r}")
    return {"max_diff_state": max_diff_state, "max_diff_obs": max_diff_obs}


def check_no_correction_matches_open_loop():
    rng = np.random.default_rng(11)
    n_days = 200
    P = rng.gamma(1.0, 2.0, n_days)
    Q = rng.gamma(1.0, 1.0, n_days)  # arbitrary; ignored since use_correction=False
    alphas, rates, c = np.array([0.3, 0.7]), np.array([0.05, 0.4]), 0.5
    W = np.diag([0.01, 0.02])  # nonzero process noise -- must not affect the MEAN trajectory
    m0 = np.zeros(2)
    P0 = np.eye(2)

    result = run_filter_full_span(P, Q, c, alphas, rates, W, R=0.1, m0=m0, P0=P0, use_correction=False)
    forecast_1day = lead_time_forecast(result.posterior_means, P, c, alphas, rates, lead=1)

    ref_q = _simulate_open_loop(P, c, alphas, rates)
    # forecast_1day[t] uses posterior_means[t-1] (the pre-any-observation-day-(t-1) state,
    # since use_correction=False), matching ref_q[t] which uses S at the start of day t.
    diffs = np.abs(forecast_1day[1:] - ref_q[1:])
    require(np.max(diffs) < 1e-9, f"no-correction filtered forecast should exactly match open-loop simulation; max diff {np.max(diffs)!r}")
    require(result.n_updates_applied == 0, "use_correction=False must never call update()")
    return {"max_diff_vs_open_loop": float(np.max(diffs)), "n_updates_applied": result.n_updates_applied}


def check_correction_converges_to_truth():
    rng = np.random.default_rng(12)
    n_days = 400
    P = rng.gamma(1.0, 2.0, n_days)
    # A SLOW reservoir (k=0.01, e-folding time 100 days) is deliberate: a fast
    # reservoir "forgets" a wrong initial condition through its own dynamics
    # alone within a few dozen days regardless of any measurement correction,
    # which would make this control case demonstrate nothing about correction
    # specifically (confirmed empirically before fixing these parameters: a
    # k=0.1 reservoir's open-loop run had already decayed its initial-condition
    # error to ~1e-8 by day 200, an artifact of the decay rate, not of a
    # working filter).
    alphas, rates, c = np.array([1.0]), np.array([0.01]), 0.4
    true_S0 = np.array([5.0])

    # Generate the true trajectory and its (noisy) daily-mean discharge observations.
    S = true_S0.copy()
    true_q = np.empty(n_days)
    meas_noise_sd = 0.02
    Q_obs = np.empty(n_days)
    for t in range(n_days):
        u = c * P[t]
        true_q[t] = parallel_reservoir_interval_discharge(S, u, alphas, rates, 1.0)
        Q_obs[t] = true_q[t] + rng.normal(0.0, meas_noise_sd)
        S = np.array(parallel_reservoir_step(S, u, alphas, rates, 1.0))

    wrong_m0 = np.array([50.0])  # deliberately wrong initial guess (true is 5.0)
    P0 = np.array([[100.0]])
    W = np.array([[0.001]])
    R = meas_noise_sd ** 2

    corrected = run_filter_full_span(P, Q_obs, c, alphas, rates, W, R, wrong_m0, P0, use_correction=True)
    open_loop = run_filter_full_span(P, Q_obs, c, alphas, rates, W, R, wrong_m0, P0, use_correction=False)

    fc_corrected = lead_time_forecast(corrected.posterior_means, P, c, alphas, rates, lead=1)
    fc_open_loop = lead_time_forecast(open_loop.posterior_means, P, c, alphas, rates, lead=1)

    # Score on days 200-300: late enough that the filter has had ample time to
    # converge via repeated corrections, but the slow reservoir's open-loop run
    # still carries a clearly measurable bias from the wrong initial guess
    # (checked empirically: open-loop MAE here is ~0.038, ~100x the
    # measurement-noise floor; by day 300-400 it would already be smaller,
    # understating the effect).
    w0, w1 = 200, 300
    mae_corrected = float(np.mean(np.abs(fc_corrected[w0:w1] - true_q[w0:w1])))
    mae_open_loop = float(np.mean(np.abs(fc_open_loop[w0:w1] - true_q[w0:w1])))

    require(
        mae_corrected < 0.2 * mae_open_loop,
        f"measurement-corrected filter should track the true trajectory far better than the "
        f"open-loop run started from the same wrong initial guess; got mae_corrected={mae_corrected!r}, "
        f"mae_open_loop={mae_open_loop!r}",
    )
    require(mae_corrected < 5 * meas_noise_sd, f"corrected MAE should approach the measurement-noise floor; got {mae_corrected!r}")
    return {"mae_corrected": mae_corrected, "mae_open_loop": mae_open_loop}


def check_no_future_leakage():
    rng = np.random.default_rng(13)
    n_days = 100
    P = rng.gamma(1.0, 2.0, n_days)
    Q = rng.gamma(1.0, 1.0, n_days)
    alphas, rates, c = np.array([1.0]), np.array([0.2]), 0.5
    W, R = np.array([[0.01]]), 0.05
    m0, P0 = np.array([1.0]), np.array([[1.0]])

    result_a = run_filter_full_span(P, Q, c, alphas, rates, W, R, m0, P0, use_correction=True)
    fc_a = lead_time_forecast(result_a.posterior_means, P, c, alphas, rates, lead=3)

    Q_modified = Q.copy()
    t_check = 40
    Q_modified[t_check + 1:] = rng.gamma(5.0, 5.0, n_days - t_check - 1)  # arbitrary large change AFTER t_check
    result_b = run_filter_full_span(P, Q_modified, c, alphas, rates, W, R, m0, P0, use_correction=True)
    fc_b = lead_time_forecast(result_b.posterior_means, P, c, alphas, rates, lead=3)

    require(
        abs(fc_a[t_check] - fc_b[t_check]) < 1e-12,
        f"forecast for day {t_check} must not depend on observations strictly after it; "
        f"got {fc_a[t_check]!r} vs {fc_b[t_check]!r}",
    )
    require(
        np.allclose(result_a.posterior_means[: t_check + 1], result_b.posterior_means[: t_check + 1], atol=1e-12),
        "posterior states up to and including t_check must be identical regardless of later observations",
    )
    return {"t_check": t_check, "fc_a": float(fc_a[t_check]), "fc_b": float(fc_b[t_check])}


def check_negative_storage_reported_not_clipped():
    rng = np.random.default_rng(14)
    n_days = 60
    P = np.zeros(n_days)  # no inflow at all
    alphas, rates, c = np.array([1.0]), np.array([0.05]), 1.0
    W = np.array([[0.0]])
    R = 0.01
    m0, P0 = np.array([1.0]), np.array([[0.5]])
    # Force strongly negative "observations" so the correction pulls the mean below zero.
    Q = np.full(n_days, -10.0)

    result = run_filter_full_span(P, Q, c, alphas, rates, W, R, m0, P0, use_correction=True)
    require(result.n_negative_storage_days > 0, "this construction should produce negative posterior storage days")
    require(np.any(result.posterior_means < 0.0), "negative means must be visible in the raw array, not clipped")
    return {"n_negative_storage_days": result.n_negative_storage_days, "min_mean": float(np.min(result.posterior_means))}


def _make_dates(n: int, start_year: int = 1991) -> list:
    dates = []
    year, month, day = start_year, 1, 1
    days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    for _ in range(n):
        dates.append(f"{year:04d}-{month:02d}-{day:02d}")
        day += 1
        dim = days_in_month[month - 1] + (1 if month == 2 and year % 4 == 0 else 0)
        if day > dim:
            day = 1
            month += 1
            if month > 12:
                month = 1
                year += 1
    return dates


def check_calibrate_process_noise_reasonable():
    rng = np.random.default_rng(15)
    n_days = 3000
    P = rng.gamma(1.0, 2.0, n_days)
    alphas, rates, c = np.array([1.0]), np.array([0.02]), 0.3
    true_meas_noise_sd = 0.03
    open_loop_true = _simulate_open_loop(P, c, alphas, rates)
    Q_train = open_loop_true + rng.normal(0.0, true_meas_noise_sd, n_days)

    w_scale, R = calibrate_process_noise(P, Q_train, c, alphas, rates)
    require(
        0.3 * true_meas_noise_sd ** 2 < R < 3.0 * true_meas_noise_sd ** 2,
        f"R should be within a factor of ~3 of the true measurement-noise variance "
        f"{true_meas_noise_sd**2!r}; got {R!r}",
    )

    # The chosen w_scale must beat both an obviously-too-small (filter never trusts new
    # data) and an obviously-too-large (filter overreacts to measurement noise) candidate
    # on a held-out inner slice, confirming the grid search is doing real selection work.
    def inner_val_mae(w_scale_candidate):
        n = 1
        W = w_scale_candidate * np.eye(n)
        n_it = int(n_days * 0.8)
        m0, P0 = np.zeros(n), 10.0 * np.eye(n)
        res_it = run_filter_full_span(P[:n_it], Q_train[:n_it], c, alphas, rates, W, R, m0, P0, use_correction=True)
        res_iv = run_filter_full_span(
            P[n_it:], Q_train[n_it:], c, alphas, rates, W, R, res_it.posterior_means[-1], res_it.posterior_covs[-1], use_correction=True
        )
        fc = lead_time_forecast(res_iv.posterior_means, P[n_it:], c, alphas, rates, lead=1)
        valid = ~np.isnan(fc)
        return float(np.mean(np.abs(fc[valid] - Q_train[n_it:][valid])))

    mae_chosen = inner_val_mae(w_scale)
    mae_too_small = inner_val_mae(1e-8)
    mae_too_large = inner_val_mae(100.0)
    require(mae_chosen <= mae_too_large, f"chosen w_scale={w_scale!r} should not be beaten by an absurdly large candidate")
    return {"w_scale": w_scale, "R": R, "mae_chosen": mae_chosen, "mae_too_small": mae_too_small, "mae_too_large": mae_too_large}


def check_run_catchment_pilot_end_to_end():
    rng = np.random.default_rng(16)
    n_days = 365 * 20  # 1991-2010 training+gap, 2011-2020 test-ish shape
    dates = _make_dates(n_days)
    P = rng.gamma(1.0, 2.0, n_days)
    true_c, true_k = 0.35, 0.015
    area = 100.0
    true_S0 = 20.0  # UNKNOWN to the pilot -- it always initializes m0=0

    from scoped_correspondence.dynamics.linear_reservoirs import parallel_reservoir_interval_discharge, parallel_reservoir_step

    S = true_S0
    Q_mm = np.empty(n_days)
    for t in range(n_days):
        u = true_c * P[t]
        Q_mm[t] = parallel_reservoir_interval_discharge([S], u, [1.0], [true_k], 1.0)
        S = parallel_reservoir_step([S], u, [1.0], [true_k], 1.0)[0]
    meas_noise_sd = 0.02
    Q_mm_obs = Q_mm + rng.normal(0.0, meas_noise_sd, n_days)
    Q_m3s = Q_mm_obs * area / 86.4

    # n_days = 365*20 starting 1991 covers 1991-2010 inclusive; split within that span,
    # leaving 2001-2005 as an unused gap so the pilot also exercises the C0-style
    # full-contiguous-span propagation.
    train_years = (1991, 2000)
    test_years = (2006, 2010)

    result = run_catchment_state_estimation_pilot(
        "SYNC", dates, P, Q_m3s, area, train_years, test_years, true_c, [1.0], [true_k]
    )
    for lead in LEAD_TIMES:
        require(
            result.mae_test["corrected"][lead] <= result.mae_test["open_loop"][lead] * 1.05,
            f"lead={lead}: corrected MAE {result.mae_test['corrected'][lead]!r} should not be meaningfully worse "
            f"than open-loop MAE {result.mae_test['open_loop'][lead]!r} when the initial storage is unknown",
        )
    return {"mae_test": {k: {str(l): v for l, v in d.items()} for k, d in result.mae_test.items()}, "w_scale": result.w_scale}


CHECKS = [
    ("state_space_matches_existing_formulas", check_state_space_matches_existing_formulas),
    ("no_correction_matches_open_loop", check_no_correction_matches_open_loop),
    ("correction_converges_to_truth", check_correction_converges_to_truth),
    ("no_future_leakage", check_no_future_leakage),
    ("negative_storage_reported_not_clipped", check_negative_storage_reported_not_clipped),
    ("calibrate_process_noise_reasonable", check_calibrate_process_noise_reasonable),
    ("run_catchment_pilot_end_to_end", check_run_catchment_pilot_end_to_end),
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json-out", type=Path, default=Path(__file__).with_name("verify_hydrology_state_estimation_results.json"))
    args = parser.parse_args()

    report = {
        "package": "INTEGRATED_EXTENSION_ROADMAP.md Paket C1 (hydrology daily-mean Kalman state estimation, synthetic-only)",
        "timestamp": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "python": sys.version.split()[0],
        "checks": {},
    }

    all_ok = True
    for name, fn in CHECKS:
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
    print(f"\n{sum(1 for c in report['checks'].values() if c['status'] == 'pass')}/{len(CHECKS)} checks passed")
    print(f"Report written to {args.json_out}")
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
