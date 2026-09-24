#!/usr/bin/env python3
"""Parallel linear reservoirs: exact update and memory kernel (DOMAIN_EXPANSION_ROADMAP.md Paket B3a).

Checks:

  1. Plan's fixed control numbers: S0=3, u=2, k=0.5, dt=1 -> S1
     exactly 3.393469340287367, mean discharge exactly 1.6065306597126332
     -- independently reproduced, then cross-checked against a high-
     precision ``scipy.integrate.solve_ivp`` run of the SAME ODE (not the
     module's own closed form).
  2. Two reservoirs with equal rates k1=k2 reduce to the single-reservoir
     total (their split is then unobservable from the total alone).
  3. alpha2=0 with a matching second initial state reduces exactly to the
     single-reservoir case (the second reservoir receives no inflow and,
     started appropriately, contributes nothing new).
  4. Label-swap invariance (1<->2): swapping which reservoir is "first"
     leaves the observed TOTAL discharge trajectory unchanged.
  5. Non-identifiability: two DIFFERENT initial storage splits with the
     SAME total S0 generally produce DIFFERENT total discharge shortly
     after -- the initial split is not identifiable from the total alone.
  6. k->0 continuous limit taken explicitly (S+alpha*u*dt), not relying on
     the general formula's numerical behavior as k*dt -> 0.
  7. Non-negativity: non-negative inputs/states never produce negative
     storage over many randomized trials.
  8. Exact convolution (arbitrary input) matches the discrete step
     recursion's implied instantaneous discharge on a piecewise-constant
     control case.
  9. ScopeViolationError guards.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

import numpy as np
from scipy.integrate import solve_ivp

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from scoped_correspondence.errors import ScopeViolationError  # noqa: E402
from scoped_correspondence.dynamics.linear_reservoirs import (  # noqa: E402
    reservoir_step, reservoir_interval_discharge, parallel_reservoir_step,
    parallel_reservoir_discharge, parallel_reservoir_interval_discharge,
    memory_kernel, convolution_discharge,
)


def require(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)


def check_plan_control_numbers():
    S1 = reservoir_step(3.0, 2.0, 0.5, 1.0)
    qbar = reservoir_interval_discharge(3.0, 2.0, 0.5, 1.0)
    require(abs(S1 - 3.393469340287367) < 1e-12, f"S1: got {S1}, want 3.393469340287367")
    require(abs(qbar - 1.6065306597126332) < 1e-12, f"qbar: got {qbar}, want 1.6065306597126332")

    def rhs(t, y):
        return [2.0 - 0.5 * y[0]]
    sol = solve_ivp(rhs, [0.0, 1.0], [3.0], t_eval=[1.0], rtol=1e-12, atol=1e-14)
    S1_ode = float(sol.y[0, -1])
    require(abs(S1 - S1_ode) < 1e-6, f"closed form {S1} vs independent ODE integration {S1_ode}")
    return {"S1": S1, "qbar": qbar, "S1_ode_cross_check": S1_ode}


def check_equal_rates_reduce_to_single():
    S1_single = reservoir_step(3.0, 2.0, 0.5, 1.0)
    new = parallel_reservoir_step([1.8, 1.2], 2.0, [0.6, 0.4], [0.5, 0.5], 1.0)
    require(abs(sum(new) - S1_single) < 1e-12, f"k1=k2 total {sum(new)} should equal single-reservoir {S1_single}")
    return {"total": sum(new), "single_reference": S1_single}


def check_alpha2_zero_reduces_to_single():
    S1_single = reservoir_step(3.0, 2.0, 0.5, 1.0)
    new = parallel_reservoir_step([3.0, 0.0], 2.0, [1.0, 0.0], [0.5, 0.9], 1.0)
    require(abs(sum(new) - S1_single) < 1e-12, f"alpha2=0 total {sum(new)} should equal single-reservoir {S1_single}")
    require(new[1] == 0.0, "second reservoir with alpha=0 and S0=0 must stay exactly 0")
    return {"total": sum(new), "single_reference": S1_single}


def check_label_swap_invariance():
    order_a = parallel_reservoir_step([1.8, 1.2], 2.0, [0.6, 0.4], [0.3, 0.8], 1.0)
    order_b = parallel_reservoir_step([1.2, 1.8], 2.0, [0.4, 0.6], [0.8, 0.3], 1.0)
    require(abs(sum(order_a) - sum(order_b)) < 1e-12,
            f"label-swapped configurations should give identical total: {sum(order_a)} vs {sum(order_b)}")
    return {"total_a": sum(order_a), "total_b": sum(order_b)}


def check_initial_split_not_identifiable_from_total_alone():
    """Same total S0=3, different splits -> generally DIFFERENT total discharge shortly after."""
    alphas, rates = [0.5, 0.5], [0.2, 2.0]
    split_1 = [3.0, 0.0]
    split_2 = [0.0, 3.0]
    new_1 = parallel_reservoir_step(split_1, 1.0, alphas, rates, 0.5)
    new_2 = parallel_reservoir_step(split_2, 1.0, alphas, rates, 0.5)
    require(abs(sum(split_1) - sum(split_2)) < 1e-12, "sanity: both splits must share the same total S0")
    require(abs(sum(new_1) - sum(new_2)) > 1e-3,
            f"different initial splits (same S0) should generally diverge in total discharge; "
            f"got {sum(new_1)} vs {sum(new_2)}")
    return {"total_after_split_1": sum(new_1), "total_after_split_2": sum(new_2)}


def check_k_zero_continuous_limit():
    S_new = reservoir_step(1.0, 2.0, 0.0, 0.5)
    require(S_new == 1.0 + 2.0 * 0.5, f"k=0 limit should be exactly S+alpha*u*dt; got {S_new}")
    # near-zero k should be numerically close to the k=0 limit (no catastrophic cancellation)
    S_tiny_k = reservoir_step(1.0, 2.0, 1e-10, 0.5)
    require(abs(S_tiny_k - S_new) < 1e-6, f"tiny k={1e-10} should be close to the k=0 limit; got {S_tiny_k} vs {S_new}")
    return {"k_zero": S_new, "k_tiny": S_tiny_k}


def check_nonnegativity():
    rng = np.random.default_rng(20260924)
    n = 2000
    for _ in range(n):
        s = reservoir_step(
            float(rng.uniform(0, 10)), float(rng.uniform(0, 5)), float(rng.uniform(0, 3)), float(rng.uniform(0.01, 2))
        )
        require(s >= 0.0, f"reservoir_step produced negative storage: {s}")
    return {"n_trials": n}


def check_convolution_matches_discrete_step():
    S1 = reservoir_step(3.0, 2.0, 0.5, 1.0)
    q_discrete_instantaneous = 0.5 * S1  # q(t) = k*S(t) for a single reservoir

    def u_func(s: float) -> float:
        return 2.0 if s < 1.0 else 0.0

    q_conv = convolution_discharge(1.0, [3.0], [1.0], [0.5], u_func)
    require(abs(q_conv - q_discrete_instantaneous) < 1e-8,
            f"convolution q(1)={q_conv} should match discrete instantaneous discharge {q_discrete_instantaneous}")

    # sanity: memory kernel integrates to 1 over [0, inf) for a single reservoir (alpha=1)
    from scipy.integrate import quad
    integral, _ = quad(lambda u: memory_kernel(u, [1.0], [0.5]), 0.0, 200.0)
    require(abs(integral - 1.0) < 1e-6, f"single-reservoir kernel should integrate to 1; got {integral}")
    return {"q_conv": q_conv, "q_discrete": q_discrete_instantaneous, "kernel_integral": integral}


def check_scope_violation_guards():
    try:
        reservoir_step(-1.0, 1.0, 0.5, 1.0)
        raise AssertionError("should reject negative storage")
    except ScopeViolationError:
        pass
    try:
        reservoir_step(1.0, 1.0, -0.5, 1.0)
        raise AssertionError("should reject negative rate")
    except ScopeViolationError:
        pass
    try:
        reservoir_step(1.0, 1.0, 0.5, -1.0)
        raise AssertionError("should reject negative dt")
    except ScopeViolationError:
        pass
    try:
        parallel_reservoir_step([1.0, 1.0], 1.0, [0.6, 0.5], [0.5, 0.5], 1.0)
        raise AssertionError("should reject alphas not summing to 1")
    except ScopeViolationError:
        pass
    try:
        reservoir_interval_discharge(1.0, 1.0, 0.5, 0.0)
        raise AssertionError("should reject dt=0 for interval discharge")
    except ScopeViolationError:
        pass
    return {"checked": 5}


CHECKS = [
    ("plan_control_numbers", check_plan_control_numbers),
    ("equal_rates_reduce_to_single", check_equal_rates_reduce_to_single),
    ("alpha2_zero_reduces_to_single", check_alpha2_zero_reduces_to_single),
    ("label_swap_invariance", check_label_swap_invariance),
    ("initial_split_not_identifiable_from_total_alone", check_initial_split_not_identifiable_from_total_alone),
    ("k_zero_continuous_limit", check_k_zero_continuous_limit),
    ("nonnegativity", check_nonnegativity),
    ("convolution_matches_discrete_step", check_convolution_matches_discrete_step),
    ("scope_violation_guards", check_scope_violation_guards),
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json-out", type=Path, default=Path(__file__).with_name("verify_linear_reservoirs_results.json"))
    args = parser.parse_args()

    report = {
        "package": "DOMAIN_EXPANSION_ROADMAP.md Paket B3a (linear reservoirs)",
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
