#!/usr/bin/env python3
"""Adaptive prediction-interval calibration (Milestone 55).

CAPABILITY_EXPANSION_ROADMAP.md Priority 1, response to Astra's 2026-09-24
capability assessment. Checks:

  1. Hand-arithmetic check of ``aci_update_alpha`` (Gibbs & Candès 2024)
     and ``pid_update_alpha`` (P+I subset of Angelopoulos et al. 2023)
     against independently recomputed numbers, plus their ScopeViolation
     guards and boundary clipping.
  2. A synthetic regime-shift regression test: after a persistent shift in
     residual magnitude, ACI's alpha_t recursion reacts within a handful
     of misses, while the fixed "rolling_reference" method (same causal
     quantile machinery, alpha_t held constant) needs many more
     post-shift points before its pooled empirical quantile catches up —
     checked as a strict, quantitative comparison (fewer post-shift misses
     for ACI than for the reference), not just eyeballed.
  3. A causal-ordering ("no lookahead") regression test: running the
     calibration sequence on a PREFIX of the trials reproduces byte-for-
     byte identical alpha_t/interval/coverage decisions for those same
     early trials as running it on the FULL sequence — later data must
     never change an earlier decision (same discipline as
     leave_one_origin_out_intervals's anti-leak regression test).
  4. Real-data application: energy-balance and COVID-renewal calibration
     comparisons (rolling_reference / aci / pid) run to completion with
     finite, in-range coverage/width/interval-score for every predictor —
     reported as-is, whichever method wins.
  5. Astra's 2026-09-24 (SCF_Review_dc5d82a.md) findings, as regression
     tests: R2 — under an overlapping-horizon origin/step configuration,
     changing ONLY a not-yet-elapsed target value must not change any
     earlier origin's already-issued alpha_t/interval (this failed before
     the pending_feedback fix and passes after it; the pre-existing
     no_lookahead_prefix_replay check does not catch this class of bug).
     R5 — a strictly increasing error sequence gives 0% empirical coverage
     forever despite alpha_t saturating at its clipped floor, demonstrating
     that the clipped ACI/PID implementations here do not automatically
     inherit the published long-run-average coverage guarantee.
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
from scoped_correspondence.validation.rolling_origin import RawHorizonPrediction  # noqa: E402
from scoped_correspondence.validation.adaptive_interval_calibration import (  # noqa: E402
    SOURCE, SOURCE_ACI, SOURCE_PID, PID_SCOPE_NOTE, METHODS, DEFAULT_ALPHA_TARGET,
    aci_update_alpha, pid_update_alpha,
    run_calibration_sequence, run_adaptive_calibration_comparison,
    run_energy_balance_calibration_comparison, run_covid_renewal_calibration_comparison,
)


def require(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)


def check_aci_update_hand_arithmetic():
    got = aci_update_alpha(0.2, 0.2, 1, 0.1)
    want = 0.2 + 0.1 * (0.2 - 1)
    require(abs(got - want) < 1e-12, f"aci miss update: got {got}, want {want}")

    got = aci_update_alpha(0.2, 0.2, 0, 0.1)
    want = 0.2 + 0.1 * (0.2 - 0)
    require(abs(got - want) < 1e-12, f"aci hit update: got {got}, want {want}")

    got = aci_update_alpha(0.01, 0.2, 1, 1.0)
    require(got == 1e-3, f"aci clipping at lower bound: got {got}, want 1e-3")

    got = aci_update_alpha(0.99, 0.2, 0, 1.0)
    require(got == 1.0 - 1e-3, f"aci clipping at upper bound: got {got}, want {1.0-1e-3}")

    for bad in (dict(err_t=2), dict(alpha_target=1.5), dict(gamma=0.0)):
        kwargs = dict(alpha_t=0.2, alpha_target=0.2, err_t=1, gamma=0.1)
        kwargs.update(bad)
        try:
            aci_update_alpha(**kwargs)
            raise AssertionError(f"aci_update_alpha should reject {bad}")
        except ScopeViolationError:
            pass
    return {"miss_update": got if False else None, "checked": 6}


def check_pid_update_hand_arithmetic():
    got = pid_update_alpha(0.2, 0.2, 1, gamma_i=0.1, recent_errs=[1, 1, 0, 0], kp=0.05)
    integral = 0.1 * (0.2 - 1)
    proportional = 0.05 * (0.2 - 0.5)
    want = 0.2 + integral + proportional
    require(abs(got - want) < 1e-12, f"pid update: got {got}, want {want}")

    got_no_recent = pid_update_alpha(0.2, 0.2, 0, gamma_i=0.1, recent_errs=[], kp=0.05)
    want_no_recent = 0.2 + 0.1 * (0.2 - 0) + 0.05 * (0.2 - 0.2)
    require(abs(got_no_recent - want_no_recent) < 1e-12,
            f"pid update with empty recent_errs falls back to alpha_target: got {got_no_recent}, want {want_no_recent}")

    for bad in (dict(err_t=7), dict(gamma_i=0.0), dict(kp=-0.1), dict(recent_errs=[2])):
        kwargs = dict(alpha_t=0.2, alpha_target=0.2, err_t=1, gamma_i=0.1, recent_errs=[1, 0], kp=0.05)
        kwargs.update(bad)
        try:
            pid_update_alpha(**kwargs)
            raise AssertionError(f"pid_update_alpha should reject {bad}")
        except ScopeViolationError:
            pass
    return {"checked": 6}


def _synthetic_regime_shift_preds(n_pre: int = 30, n_post: int = 20) -> list[RawHorizonPrediction]:
    """Deterministic step=1 sequence: |residual| oscillates in [0.5,1.5] for
    n_pre origins, then jumps to oscillate in [7.5,8.5] for n_post origins
    (a persistent regime shift with within-regime variability, so the
    causal empirical quantile is not degenerate at a single constant).
    """
    preds = []
    for t in range(1, n_pre + n_post + 1):
        origin = float(t)
        if t <= n_pre:
            residual = 1.0 + 0.5 * np.sin(t)
        else:
            residual = 8.0 + 0.5 * np.sin(t)
        preds.append(RawHorizonPrediction(origin=origin, step=1, observed=float(residual), predicted=0.0))
    return preds


def check_aci_recovers_faster_after_regime_shift():
    n_pre, n_post = 30, 20
    preds = _synthetic_regime_shift_preds(n_pre, n_post)

    ref = run_calibration_sequence(preds, step=1, step_size=1.0, alpha_target=0.2, method="rolling_reference")
    aci = run_calibration_sequence(preds, step=1, step_size=1.0, alpha_target=0.2, method="aci", gamma=0.1)

    def n_misses_in_window(report, origin_lo, origin_hi):
        return sum(1 for t in report.trials if origin_lo <= t.origin <= origin_hi and not t.covered)

    window_lo, window_hi = n_pre + 1, n_pre + 10  # first 10 post-shift trials
    ref_misses = n_misses_in_window(ref, window_lo, window_hi)
    aci_misses = n_misses_in_window(aci, window_lo, window_hi)

    require(ref_misses >= 5, f"reference should undercover badly right after the shift; got {ref_misses}/10 misses")
    require(aci_misses < ref_misses,
            f"ACI should recover faster than the fixed reference after a persistent shift; "
            f"aci_misses={aci_misses} ref_misses={ref_misses}")
    return {"n_pre": n_pre, "n_post": n_post, "window": [window_lo, window_hi],
            "reference_misses": ref_misses, "aci_misses": aci_misses}


def check_no_lookahead_prefix_replay():
    preds = _synthetic_regime_shift_preds(30, 20)
    prefix = [p for p in preds if p.origin <= 37]  # 30 pre-shift + 7 post-shift

    for method, kwargs in (
        ("rolling_reference", {}),
        ("aci", {"gamma": 0.1}),
        ("pid", {"gamma_i": 0.1, "kp": 0.05, "proportional_window": 5}),
    ):
        full = run_calibration_sequence(preds, step=1, step_size=1.0, alpha_target=0.2, method=method, **kwargs)
        part = run_calibration_sequence(prefix, step=1, step_size=1.0, alpha_target=0.2, method=method, **kwargs)
        n = len(part.trials)
        require(n > 0, f"{method}: prefix run produced zero trials")
        require(len(full.trials) >= n, f"{method}: full run has fewer trials than prefix")
        for i in range(n):
            ft, pt = full.trials[i], part.trials[i]
            require(ft.origin == pt.origin, f"{method}: trial {i} origin mismatch {ft.origin} vs {pt.origin}")
            require(abs(ft.alpha_t - pt.alpha_t) < 1e-12,
                    f"{method}: trial {i} (origin {ft.origin}) alpha_t differs between full and prefix run "
                    f"({ft.alpha_t} vs {pt.alpha_t}) — later data leaked into an earlier decision")
            require(abs(ft.lower - pt.lower) < 1e-9 and abs(ft.upper - pt.upper) < 1e-9,
                    f"{method}: trial {i} interval differs between full and prefix run")
            require(ft.covered == pt.covered, f"{method}: trial {i} coverage decision differs")
    return {"methods_checked": list(METHODS), "prefix_trials": n}


def check_real_data_application(co2_path, temp_path, covid_path):
    eb = run_energy_balance_calibration_comparison(co2_path, temp_path)
    cv = run_covid_renewal_calibration_comparison(covid_path)

    summary = {"energy_balance": {}, "covid_renewal": {}}
    for label, comparison in (("energy_balance", eb), ("covid_renewal", cv)):
        for predictor_name, methods in comparison.items():
            require(set(methods) == set(METHODS), f"{label}/{predictor_name}: missing methods, got {set(methods)}")
            summary[label][predictor_name] = {}
            for method, r in methods.items():
                require(r.n_trials > 0, f"{label}/{predictor_name}/{method}: zero trials")
                require(0.0 <= r.empirical_coverage_value <= 1.0,
                        f"{label}/{predictor_name}/{method}: coverage out of range ({r.empirical_coverage_value})")
                require(np.isfinite(r.mean_width) and r.mean_width >= 0.0,
                        f"{label}/{predictor_name}/{method}: mean_width not finite/non-negative")
                require(np.isfinite(r.mean_interval_score),
                        f"{label}/{predictor_name}/{method}: mean_interval_score not finite")
                summary[label][predictor_name][method] = {
                    "n_trials": r.n_trials,
                    "empirical_coverage": round(r.empirical_coverage_value, 4),
                    "mean_width": round(r.mean_width, 4),
                    "mean_interval_score": round(r.mean_interval_score, 4),
                }
    return summary


def check_no_future_leakage_via_alpha_t_under_overlapping_horizons():
    """SCF_Review_dc5d82a.md finding R2: with origin spacing 1 and step (horizon) 3,
    origin=6's own trial targets t=9. Origin=6 has exactly MIN_CAUSAL_SCORES=3
    time-eligible past scores (origins 1,2,3 -> targets 4,5,6), so it IS scored --
    and its own outcome must not affect any origin whose real time is still < 9
    (i.e. origins 7 and 8), only origins >= 9.
    """
    def make_preds(target9_value):
        preds = []
        for origin in range(1, 15):
            target = origin + 3
            obs = target9_value if target == 9 else 1.0 + 0.1 * np.sin(origin)
            preds.append(RawHorizonPrediction(origin=float(origin), step=3, observed=float(obs), predicted=0.0))
        return preds

    preds_a = make_preds(1.0)
    preds_b = make_preds(100.0)  # only the not-yet-elapsed target=9 value differs
    for method, kwargs in (("aci", dict(gamma=0.1)), ("pid", dict(gamma_i=0.1, kp=0.05, proportional_window=5))):
        r_a = run_calibration_sequence(preds_a, step=3, step_size=1.0, alpha_target=0.2, method=method, **kwargs)
        r_b = run_calibration_sequence(preds_b, step=3, step_size=1.0, alpha_target=0.2, method=method, **kwargs)
        require(len(r_a.trials) == len(r_b.trials), f"{method}: trial count mismatch")
        saw_a_divergence_after_9 = False
        for ta, tb in zip(r_a.trials, r_b.trials):
            if ta.origin < 9.0:
                require(abs(ta.alpha_t - tb.alpha_t) < 1e-12,
                        f"{method}: LEAK at origin={ta.origin} (target=9 not yet elapsed): "
                        f"alpha_t {ta.alpha_t} vs {tb.alpha_t}")
                require(abs(ta.lower - tb.lower) < 1e-9 and abs(ta.upper - tb.upper) < 1e-9,
                        f"{method}: LEAK at origin={ta.origin}: interval differs")
            elif abs(ta.alpha_t - tb.alpha_t) > 1e-12:
                saw_a_divergence_after_9 = True
        require(saw_a_divergence_after_9,
                f"{method}: sanity check -- scenarios should legitimately diverge once target=9 elapses")
    return {"checked_methods": ["aci", "pid"], "leak_free_before_target_elapses": True}


def check_capped_variant_can_permanently_fail_to_cover():
    """SCF_Review_dc5d82a.md finding R5: a strictly increasing error sequence
    (observed = t+1 against a constant zero forecast) gives 0% empirical coverage
    forever -- alpha_t saturates at its clipped floor, but no quantile built from
    strictly-smaller past values can ever bound a strictly-larger future one. This
    demonstrates the clipped ACI/PID implementations here do NOT automatically
    inherit Gibbs & Candès's published long-run-average coverage guarantee.
    """
    preds = [RawHorizonPrediction(origin=float(t), step=1, observed=float(t + 1), predicted=0.0)
             for t in range(1, 200)]
    r = run_calibration_sequence(preds, step=1, step_size=1.0, alpha_target=0.2, method="aci", gamma=0.1)
    require(r.n_trials > 100, f"expected many scored trials; got {r.n_trials}")
    require(r.empirical_coverage_value == 0.0, f"expected 0.0 coverage; got {r.empirical_coverage_value}")
    require(r.trials[-1].alpha_t <= 1e-3 + 1e-9, f"alpha_t should have saturated near its floor; got {r.trials[-1].alpha_t}")
    return {"n_trials": r.n_trials, "empirical_coverage": r.empirical_coverage_value, "final_alpha_t": r.trials[-1].alpha_t}


CHECKS = [
    ("aci_update_hand_arithmetic", check_aci_update_hand_arithmetic),
    ("pid_update_hand_arithmetic", check_pid_update_hand_arithmetic),
    ("aci_recovers_faster_after_regime_shift", check_aci_recovers_faster_after_regime_shift),
    ("no_lookahead_prefix_replay", check_no_lookahead_prefix_replay),
    ("no_future_leakage_via_alpha_t_under_overlapping_horizons", check_no_future_leakage_via_alpha_t_under_overlapping_horizons),
    ("capped_variant_can_permanently_fail_to_cover", check_capped_variant_can_permanently_fail_to_cover),
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--co2-data", type=Path, default=ROOT / "data" / "noaa_mauna_loa_co2_annual_1959_2025.txt")
    parser.add_argument("--temp-data", type=Path, default=ROOT / "data" / "noaa_global_temp_anomaly_1880_2025.csv")
    parser.add_argument("--covid-data", type=Path, default=ROOT / "data" / "owid_covid_world_daily_2020_2023.csv")
    parser.add_argument("--json-out", type=Path, default=Path(__file__).with_name("verify_adaptive_interval_calibration_results.json"))
    args = parser.parse_args()

    co2_path = args.co2_data.resolve()
    temp_path = args.temp_data.resolve()
    covid_path = args.covid_data.resolve()

    checks = CHECKS + [
        ("real_data_application", lambda: check_real_data_application(co2_path, temp_path, covid_path)),
    ]

    report = {
        "package": "CAPABILITY_EXPANSION_ROADMAP.md Priority 1 (adaptive interval calibration)",
        "source": SOURCE,
        "source_aci": SOURCE_ACI,
        "source_pid": SOURCE_PID,
        "pid_scope_note": PID_SCOPE_NOTE,
        "default_alpha_target": DEFAULT_ALPHA_TARGET,
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
