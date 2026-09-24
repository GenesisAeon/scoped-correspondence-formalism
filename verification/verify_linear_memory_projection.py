#!/usr/bin/env python3
"""Mori-Zwanzig exact memory reduction for linear systems (Milestone 57).

CAPABILITY_EXPANSION_ROADMAP.md Priority 3. Checks:

  1. ``exact_memory_kernel`` hand check for a 1-hidden-state (scalar
     exponential) AND a 2-hidden-state (diagonal D, sum of two
     exponentials) case, both against an independently written closed-form
     expression -- not against the module's own ``expm`` call.
  2. Regression: with the hidden state starting at ``z0=0`` and a memory
     window covering the FULL simulated interval, the finite-memory
     approximation must closely reproduce the exact full-system trajectory
     (the two dropped simplifications -- the initial-hidden-state term and
     window truncation -- are both switched off in this configuration).
  3. ScopeViolationError guards (negative kernel lag, non-square/mismatched
     shapes, non-positive memory_window, too few Euler steps, non-
     increasing t_span).
  4. Full comparison on a stable, moderately-coupled worked example:
     memoryless drops the hidden coupling entirely and the finite-memory
     approximation (partial window) is checked to beat it on ALL FOUR of
     Astra's requested metrics -- mean absolute error, minimum value,
     minimum time, and boundary-crossing time -- not just one of them.
  5. Astra's 2026-09-24 (SCF_Review_dc5d82a.md, finding R3) regression:
     ``_continuous_min`` used to call a single local
     ``scipy.optimize.minimize_scalar`` bracket search, unsound for an
     oscillating trajectory -- the same failure mode Astra demonstrated in
     ``viability.transient_amplification``. Checked here directly against
     an independent brute-force fine grid on an oscillating example.
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
from scoped_correspondence.closure.linear_memory_projection import (  # noqa: E402
    SOURCE,
    exact_memory_kernel, simulate_full_system, simulate_memoryless_approximation,
    simulate_finite_memory_approximation, run_memory_projection_comparison,
    _continuous_min,
)


def require(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)


def check_kernel_hand_arithmetic():
    K1 = exact_memory_kernel([0.6], [[-2.0]], [0.6])
    for u in (0.0, 0.5, 1.0, 3.0):
        got = K1(u)
        want = 0.6 * 0.6 * np.exp(-2.0 * u)
        require(abs(got - want) < 1e-12, f"1-hidden-state kernel at u={u}: got {got}, want {want}")

    K2 = exact_memory_kernel([0.5, 0.3], [[-1.0, 0.0], [0.0, -3.0]], [0.5, 0.3])
    for u in (0.0, 0.5, 1.0, 2.0):
        got = K2(u)
        want = 0.5 * 0.5 * np.exp(-1.0 * u) + 0.3 * 0.3 * np.exp(-3.0 * u)
        require(abs(got - want) < 1e-9, f"2-hidden-state kernel at u={u}: got {got}, want {want}")

    try:
        K1(-0.1)
        raise AssertionError("exact_memory_kernel should reject negative lag")
    except ScopeViolationError:
        pass
    try:
        exact_memory_kernel([0.5], [[-1.0, 0.0], [0.0, -1.0]], [0.5])
        raise AssertionError("exact_memory_kernel should reject B shape mismatched with D")
    except ScopeViolationError:
        pass
    return {"checked_u_values": [0.0, 0.5, 1.0, 2.0, 3.0]}


def check_finite_memory_matches_exact_when_window_covers_full_history():
    A, B, D, C = -0.5, [0.6], [[-1.0]], [0.6]
    x0, z0 = 1.0, [0.0]
    def forcing(t):
        return -5.0 * np.exp(-((t - 5.0) / 0.5) ** 2)

    t = np.linspace(0.0, 20.0, 400)
    x_exact, _ = simulate_full_system(A, B, D, C, x0, z0, forcing, t)
    ts_fine, x_fine = simulate_finite_memory_approximation(A, B, D, C, x0, forcing, (0.0, 20.0), memory_window=20.0, n_steps=8000)
    x_fine_on_t = np.interp(t, ts_fine, x_fine)
    max_diff = float(np.max(np.abs(x_fine_on_t - x_exact)))
    require(max_diff < 0.01, f"full-window finite-memory should closely match exact when z0=0; max_diff={max_diff}")
    return {"max_diff_full_window_vs_exact": max_diff}


def check_scope_violation_guards():
    A, B, D, C = -0.5, [0.6], [[-1.0]], [0.6]
    def forcing(t):
        return 0.0

    for kwargs, label in (
        (dict(memory_window=-1.0, n_steps=100), "negative_window"),
        (dict(memory_window=1.0, n_steps=2), "too_few_steps"),
    ):
        try:
            simulate_finite_memory_approximation(A, B, D, C, 1.0, forcing, (0.0, 5.0), **kwargs)
            raise AssertionError(f"simulate_finite_memory_approximation should reject {label}")
        except ScopeViolationError:
            pass

    try:
        simulate_finite_memory_approximation(A, B, D, C, 1.0, forcing, (5.0, 5.0), memory_window=1.0, n_steps=100)
        raise AssertionError("simulate_finite_memory_approximation should reject a non-increasing t_span")
    except ScopeViolationError:
        pass
    return {"checked": 3}


def check_full_comparison_beats_memoryless_on_all_metrics():
    A, B, D, C = -0.5, [0.6], [[-1.0]], [0.6]
    x0, z0 = 1.0, [0.0]
    def forcing(t):
        return -5.0 * np.exp(-((t - 5.0) / 0.5) ** 2)

    r = run_memory_projection_comparison(A, B, D, C, x0, z0, forcing, (0.0, 20.0), memory_window=2.0, boundary=-2.9)

    require(r.mean_abs_error_finite_memory < r.mean_abs_error_memoryless,
            f"finite-memory MAE ({r.mean_abs_error_finite_memory}) should beat memoryless ({r.mean_abs_error_memoryless})")

    err_min_memless = abs(r.memoryless_min_value - r.exact_min_value)
    err_min_finite = abs(r.finite_memory_min_value - r.exact_min_value)
    require(err_min_finite < err_min_memless,
            f"finite-memory minimum-value error ({err_min_finite}) should beat memoryless ({err_min_memless})")

    err_min_time_memless = abs(r.memoryless_min_time - r.exact_min_time)
    err_min_time_finite = abs(r.finite_memory_min_time - r.exact_min_time)
    require(err_min_time_finite < err_min_time_memless,
            f"finite-memory minimum-TIME error ({err_min_time_finite}) should beat memoryless ({err_min_time_memless})")

    require(r.exact_crossing_time is not None and r.memoryless_crossing_time is not None and r.finite_memory_crossing_time is not None,
            "all three variants should cross this boundary for this worked example")
    err_cross_memless = abs(r.memoryless_crossing_time - r.exact_crossing_time)
    err_cross_finite = abs(r.finite_memory_crossing_time - r.exact_crossing_time)
    require(err_cross_finite < err_cross_memless,
            f"finite-memory crossing-time error ({err_cross_finite}) should beat memoryless ({err_cross_memless})")

    return {
        "mean_abs_error_memoryless": round(r.mean_abs_error_memoryless, 4),
        "mean_abs_error_finite_memory": round(r.mean_abs_error_finite_memory, 4),
        "exact_min_value": round(r.exact_min_value, 4), "exact_min_time": round(r.exact_min_time, 4),
        "memoryless_min_value": round(r.memoryless_min_value, 4), "memoryless_min_time": round(r.memoryless_min_time, 4),
        "finite_memory_min_value": round(r.finite_memory_min_value, 4), "finite_memory_min_time": round(r.finite_memory_min_time, 4),
        "exact_crossing_time": round(r.exact_crossing_time, 4),
        "memoryless_crossing_time": round(r.memoryless_crossing_time, 4),
        "finite_memory_crossing_time": round(r.finite_memory_crossing_time, 4),
    }


def check_continuous_min_global_not_local():
    """SCF_Review_dc5d82a.md finding R3: on an oscillating trajectory, a single
    local ``scipy.optimize.minimize_scalar`` bracket search can miss the true
    global minimum entirely (Astra demonstrated -0.71905 vs. a true -0.98446 on
    a related oscillating example). Checked here against an independent
    brute-force fine grid on x(t) = exp(-0.1t)*sin(10t).
    """
    t = np.linspace(0.0, 10.0, 2000)
    x = np.exp(-0.1 * t) * np.sin(10.0 * t)
    t_star, val = _continuous_min(t, x)

    t_fine = np.linspace(0.0, 10.0, 4_000_000)
    x_fine = np.exp(-0.1 * t_fine) * np.sin(10.0 * t_fine)
    true_min = float(x_fine.min())
    true_min_time = float(t_fine[np.argmin(x_fine)])

    require(abs(val - true_min) < 1e-3, f"module min {val} should match brute-force global min {true_min}")
    require(abs(t_star - true_min_time) < 1e-2, f"module min time {t_star} should match brute-force time {true_min_time}")
    return {"module_min": val, "module_min_time": t_star, "true_min": true_min, "true_min_time": true_min_time}


CHECKS = [
    ("kernel_hand_arithmetic", check_kernel_hand_arithmetic),
    ("finite_memory_matches_exact_when_window_covers_full_history", check_finite_memory_matches_exact_when_window_covers_full_history),
    ("scope_violation_guards", check_scope_violation_guards),
    ("full_comparison_beats_memoryless_on_all_metrics", check_full_comparison_beats_memoryless_on_all_metrics),
    ("continuous_min_global_not_local", check_continuous_min_global_not_local),
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json-out", type=Path, default=Path(__file__).with_name("verify_linear_memory_projection_results.json"))
    args = parser.parse_args()

    report = {
        "package": "CAPABILITY_EXPANSION_ROADMAP.md Priority 3 (linear memory projection)",
        "source": SOURCE,
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
