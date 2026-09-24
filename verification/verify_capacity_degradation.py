#!/usr/bin/env python3
"""Battery capacity degradation models + observation ablation (DOMAIN_EXPANSION_ROADMAP.md Paket B5a).

Checks:

  1. Exact synthetic linear and power-law curves are recovered exactly
     (noiseless data) by fitting only the same model family used to
     generate them.
  2. p=1 special case: fitting the POWER model to exactly LINEAR data
     reproduces the linear trend with zero residual (the power model
     nests the linear model at p=1).
  3. 2x2 observation ablation: the AR(1) block gets NO pre-programmed
     estimated correlation under independent residuals (small |phi|), and
     correctly recovers a genuinely correlated residual's AR coefficient
     to a useful precision -- checked on a large enough sample (n=500)
     that sampling noise in the OLS phi estimate does not itself cause a
     false pass/fail.
  4. Leakage guard: fitting on a training PREFIX and then separately
     changing values beyond that prefix does not alter the fit (trivial
     by construction -- checked explicitly, not merely assumed).
  5. Raw capacity increases are preserved in the observed data (never
     silently monotonized) -- checked on a series with a real bump.
  6. first_mean_eol_crossing gives the MEAN model's own crossing point,
     explicitly distinguished from an observed-noise first-passage event
     computed independently from a simulated noisy path.
  7. ScopeViolationError guards, including the negative-extrapolation
     model-domain-violation case (never silently clipped away).
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
from scoped_correspondence.dynamics.capacity_degradation import (  # noqa: E402
    fit_capacity_trend, mean_capacity, predict_capacity_distribution, first_mean_eol_crossing,
    MODEL_LINEAR, MODEL_POWER, MODEL_PERSISTENCE,
)


def require(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)


def check_exact_synthetic_recovery():
    n = np.arange(0, 50, dtype=float)
    cap_linear = 2.0 - 0.01 * n
    fit_lin = fit_capacity_trend(n, cap_linear, MODEL_LINEAR)
    require(abs(fit_lin.params["C0"] - 2.0) < 1e-8, f"linear C0: got {fit_lin.params['C0']}")
    require(abs(fit_lin.params["a"] - 0.01) < 1e-8, f"linear a: got {fit_lin.params['a']}")

    cap_power = 2.0 - 0.005 * np.power(n, 1.5)
    fit_pow = fit_capacity_trend(n, cap_power, MODEL_POWER)
    require(abs(fit_pow.params["C0"] - 2.0) < 1e-6, f"power C0: got {fit_pow.params['C0']}")
    require(abs(fit_pow.params["a"] - 0.005) < 1e-6, f"power a: got {fit_pow.params['a']}")
    require(abs(fit_pow.params["p"] - 1.5) < 1e-4, f"power p: got {fit_pow.params['p']}")
    return {"linear_params": fit_lin.params, "power_params": fit_pow.params}


def check_p_equals_one_reduces_to_linear():
    n = np.arange(0, 50, dtype=float)
    cap_linear = 2.0 - 0.01 * n
    fit_power_on_linear = fit_capacity_trend(n, cap_linear, MODEL_POWER)
    residuals = cap_linear - mean_capacity(MODEL_POWER, fit_power_on_linear.params, n)
    require(np.max(np.abs(residuals)) < 1e-6,
            f"power model fit to exactly-linear data should have ~zero residual; got max {np.max(np.abs(residuals))}")
    return {"power_params_on_linear_data": fit_power_on_linear.params, "max_abs_residual": float(np.max(np.abs(residuals)))}


def check_observation_ablation():
    n = np.arange(0, 500, dtype=float)
    cap_linear = 2.0 - 0.001 * n
    rng = np.random.default_rng(20260924)

    noise_indep = rng.normal(0.0, 0.01, size=500)
    fit_indep = fit_capacity_trend(n, cap_linear + noise_indep, MODEL_LINEAR, fit_ar1=True)
    require(abs(fit_indep.ar1_phi) < 0.15,
            f"independent residuals should NOT show a pre-programmed AR gain; got phi={fit_indep.ar1_phi}")

    phi_true = 0.8
    r = np.zeros(500)
    for i in range(1, 500):
        r[i] = phi_true * r[i - 1] + rng.normal(0.0, 0.005)
    fit_corr = fit_capacity_trend(n, cap_linear + r, MODEL_LINEAR, fit_ar1=True)
    require(abs(fit_corr.ar1_phi - phi_true) < 0.1,
            f"genuinely correlated residuals should be recovered to useful precision; got phi={fit_corr.ar1_phi}, true={phi_true}")
    return {"phi_independent": fit_indep.ar1_phi, "phi_correlated": fit_corr.ar1_phi, "phi_true": phi_true}


def check_leakage_guard():
    n = np.arange(0, 30, dtype=float)
    cap = 2.0 - 0.02 * n
    fit_before = fit_capacity_trend(n[:20], cap[:20], MODEL_LINEAR)

    cap_modified = cap.copy()
    cap_modified[20:] = 999.0  # change everything AFTER the training prefix
    fit_after = fit_capacity_trend(n[:20], cap_modified[:20], MODEL_LINEAR)

    require(fit_before.params == fit_after.params,
            f"changing values beyond the training prefix must not change the fit: {fit_before.params} vs {fit_after.params}")
    return {"params": fit_before.params}


def check_observed_increases_preserved():
    """Raw capacity increases (e.g. a calendar-rest recovery bump) must survive
    untouched in the data passed to fit_capacity_trend -- never monotonized away
    before fitting."""
    n = np.array([0, 1, 2, 3, 4], dtype=float)
    cap = np.array([2.0, 1.9, 1.95, 1.8, 1.7])  # a real bump at index 2
    require(cap[2] > cap[1], "sanity: the synthetic bump must actually be an increase")
    fit = fit_capacity_trend(n, cap, MODEL_LINEAR)
    require(tuple(fit.train_capacity) == tuple(cap),
            "fit_capacity_trend must store the RAW (un-monotonized) observed capacity")
    return {"train_capacity": list(fit.train_capacity)}


def check_mean_vs_observed_eol_crossing():
    n = np.arange(0, 100, dtype=float)
    cap = 2.0 - 0.01 * n
    fit = fit_capacity_trend(n, cap, MODEL_LINEAR)
    mean_crossing = first_mean_eol_crossing(fit, 1.4, 200.0)
    require(mean_crossing is not None and abs(mean_crossing - 60.0) < 1e-6,
            f"mean crossing should be exactly 60; got {mean_crossing}")

    # simulate a noisy observed path and find its OWN first observed crossing --
    # generally DIFFERENT from the mean crossing.
    rng = np.random.default_rng(42)
    future_n = np.arange(0, 100, dtype=float)
    samples = predict_capacity_distribution(fit, 0.0, future_n, rng, n_samples=1)
    observed_path = samples[0]
    below = np.where(observed_path <= 1.4)[0]
    observed_crossing = float(future_n[below[0]]) if len(below) > 0 else None

    return {"mean_crossing": mean_crossing, "observed_crossing_one_realization": observed_crossing}


def check_scope_violation_guards():
    n = np.arange(0, 10, dtype=float)
    cap = 2.0 - 0.01 * n
    try:
        fit_capacity_trend(n, cap, "not_a_model")
        raise AssertionError("should reject unknown model_spec")
    except ScopeViolationError:
        pass
    try:
        fit_capacity_trend(n[:1], cap[:1], MODEL_LINEAR)
        raise AssertionError("should reject fewer than 2 training points")
    except ScopeViolationError:
        pass
    try:
        fit_capacity_trend(n, cap[:5], MODEL_LINEAR)
        raise AssertionError("should reject mismatched cycles/capacity length")
    except ScopeViolationError:
        pass

    # negative extrapolation is exposed, not silently clipped
    fit = fit_capacity_trend(n, cap, MODEL_LINEAR)
    far_future = mean_capacity(MODEL_LINEAR, fit.params, np.array([10000.0]))
    require(far_future[0] < 0.0, f"far-future extrapolation should be exposed as negative (model-domain violation), got {far_future[0]}")
    return {"checked": 3, "far_future_negative_extrapolation": float(far_future[0])}


CHECKS = [
    ("exact_synthetic_recovery", check_exact_synthetic_recovery),
    ("p_equals_one_reduces_to_linear", check_p_equals_one_reduces_to_linear),
    ("observation_ablation", check_observation_ablation),
    ("leakage_guard", check_leakage_guard),
    ("observed_increases_preserved", check_observed_increases_preserved),
    ("mean_vs_observed_eol_crossing", check_mean_vs_observed_eol_crossing),
    ("scope_violation_guards", check_scope_violation_guards),
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json-out", type=Path, default=Path(__file__).with_name("verify_capacity_degradation_results.json"))
    args = parser.parse_args()

    report = {
        "package": "DOMAIN_EXPANSION_ROADMAP.md Paket B5a (capacity degradation)",
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
