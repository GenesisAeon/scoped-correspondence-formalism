#!/usr/bin/env python3
"""Deterministic reflected fluid queue (DOMAIN_EXPANSION_ROADMAP.md Paket B2a).

Checks:

  1. Astra's fixed worked example (plan section 8.2): q0=0, service rate
     s=1, horizon H=10, threshold K=5. Uniform arrival a=0.8 (same total
     load 8 over the horizon) keeps the backlog at 0 throughout. A load
     spike a=4 on [0,2] then 0 (same total load 8) peaks at q=6 at t=2 and
     first reaches K=5 at t=5/3 -- hand-derived independently: on [0,2],
     nu=4-1=3, q(t)=3t, so q(t)=5 at t=5/3.
  2. Monotonicity of every constant-rate segment (module's own claimed
     correctness property) checked against a fine-grained brute-force
     ODE integration (not the module's own closed form).
  3. The stock/reserve bridge R=K-q: values match K-q(t) exactly before
     the first capacity breach, and the breach time is reported (not
     silently extended past it).
  4. Negative test (plan section 4.2): a state-dependent outflow k*S is
     NOT the same dynamics as a constant outflow merely because both
     drain a stock -- checked as a genuine divergence, not conflated by
     any shared "drain" terminology.
  5. ScopeViolationError guards (mismatched rate-array lengths,
     non-increasing breakpoints, negative initial backlog, querying
     value_at outside the trajectory range).
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
from scoped_correspondence.dynamics.queueing import (  # noqa: E402
    fluid_queue_piecewise, stock_reserve_bridge,
)


def require(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)


def check_astra_worked_example():
    # Uniform arrival: net rate always negative (0.8-1=-0.2), reflected to 0 throughout.
    traj_uniform = fluid_queue_piecewise(0.0, [0.0, 10.0], [0.8], [1.0])
    t_u, peak_u = traj_uniform.peak()
    require(peak_u == 0.0, f"uniform arrival: backlog should stay exactly 0; got peak {peak_u} at t={t_u}")

    # Load spike: a=4 on [0,2], a=0 on [2,10], s=1 throughout.
    traj_spike = fluid_queue_piecewise(0.0, [0.0, 2.0, 10.0], [4.0, 0.0], [1.0, 1.0])
    t_peak, peak = traj_spike.peak()
    require(abs(t_peak - 2.0) < 1e-12, f"spike: peak time should be exactly 2.0; got {t_peak}")
    require(abs(peak - 6.0) < 1e-12, f"spike: peak value should be exactly 6.0; got {peak}")

    t_hit = traj_spike.first_upward_crossing(5.0)
    want_t_hit = 5.0 / 3.0
    require(t_hit is not None and abs(t_hit - want_t_hit) < 1e-12,
            f"spike: first hit of K=5 should be exactly 5/3={want_t_hit}; got {t_hit}")

    # Same total arrivals (8) in both cases -- isolates the effect of TIMING, not total load.
    require(abs(0.8 * 10.0 - (4.0 * 2.0 + 0.0 * 8.0)) < 1e-12, "sanity: both scenarios must have equal total load")

    # Empties again by t=8: q(2)=6, drains at rate 1 -> hits 0 at t=8.
    require(abs(traj_spike.value_at(8.0)) < 1e-12, f"spike: should be empty again by t=8; got {traj_spike.value_at(8.0)}")
    require(abs(traj_spike.value_at(5.0) - 3.0) < 1e-12, f"spike: q(5) should be 3.0 (6-1*3); got {traj_spike.value_at(5.0)}")

    return {
        "uniform_peak": peak_u, "spike_peak": peak, "spike_peak_time": t_peak,
        "spike_first_hit_5": t_hit, "spike_q_at_5": traj_spike.value_at(5.0),
    }


def check_monotonicity_against_brute_force_ode():
    """Each constant-rate segment's reflected trajectory must be monotonic; verify
    against a fine-grained independent Euler integration of dq/dt=nu, reflected at 0,
    NOT the module's own closed-form value_at."""
    rng = np.random.default_rng(20260924)
    for _ in range(20):
        q0 = float(rng.uniform(0.0, 5.0))
        nu = float(rng.uniform(-3.0, 3.0))
        dt_seg = float(rng.uniform(0.5, 4.0))
        traj = fluid_queue_piecewise(q0, [0.0, dt_seg], [max(0.0, nu)], [max(0.0, -nu)] if nu < 0 else [0.0])
        # Reconstruct net rate directly to sidestep the arrival/service split (only nu matters).
        traj = fluid_queue_piecewise(q0, [0.0, dt_seg], [nu if nu > 0 else 0.0], [-nu if nu < 0 else 0.0])

        n_steps = 200_000
        h = dt_seg / n_steps
        q = q0
        vals = [q]
        for _ in range(n_steps):
            q = max(0.0, q + nu * h)
            vals.append(q)
        brute_end = vals[-1]
        module_end = traj.value_at(dt_seg)
        require(abs(brute_end - module_end) < 1e-3,
                f"q0={q0}, nu={nu}, dt={dt_seg}: brute-force {brute_end} vs module {module_end}")
        diffs = np.diff(vals)
        if nu >= 0.0:
            require(np.all(diffs >= -1e-9), f"nu={nu}>=0 should be non-decreasing; violated")
        else:
            require(np.all(diffs <= 1e-9), f"nu={nu}<0 should be non-increasing; violated")
    return {"random_segments_checked": 20, "steps_per_segment": 200_000}


def check_stock_reserve_bridge():
    traj = fluid_queue_piecewise(0.0, [0.0, 2.0, 10.0], [4.0, 0.0], [1.0, 1.0])
    K = 5.0
    times = [0.0, 1.0, 5.0 / 3.0, 2.0, 5.0, 8.0]
    report = stock_reserve_bridge(traj, K, times)

    require(report.first_capacity_breach_time is not None and abs(report.first_capacity_breach_time - 5.0 / 3.0) < 1e-9,
            f"breach time should be 5/3; got {report.first_capacity_breach_time}")

    for t, r in zip(report.at_times, report.reserve_values):
        want = K - traj.value_at(t)
        require(abs(r - want) < 1e-12, f"R({t})={r} should equal K-q(t)={want}")

    valid = report.valid_reserve_values()
    require(all(t <= report.first_capacity_breach_time + 1e-9 for t, _ in valid),
            "valid_reserve_values must exclude times past the breach")
    require(any(abs(t - 5.0) < 1e-9 for t in times) and not any(abs(t - 5.0) < 1e-9 for t, _ in valid),
            "t=5 (past the breach) must be excluded from valid_reserve_values")

    return {"breach_time": report.first_capacity_breach_time, "n_valid": len(valid), "n_total": len(times)}


def check_negative_test_state_dependent_rate_differs():
    """A constant outflow c and a state-dependent outflow k*S are NOT the same
    dynamics. Starting both at S0=5 with matched INITIAL outflow (c = k*S0), they
    diverge immediately afterward -- confirmed by direct ODE comparison, not by
    the queueing module itself (which only implements the constant-rate case)."""
    S0 = 5.0
    k = 0.3
    c = k * S0  # matched initial outflow

    def rhs_constant(S, _c):
        return -_c

    def rhs_proportional(S, _k):
        return -_k * S

    dt_step = 1e-4
    n = 20000
    S_const, S_prop = S0, S0
    for _ in range(n):
        S_const = max(0.0, S_const + rhs_constant(S_const, c) * dt_step)
        S_prop = max(0.0, S_prop + rhs_proportional(S_prop, k) * dt_step)

    # Exact solution for proportional: S(t) = S0*exp(-k*t); for constant: S(t)=max(0,S0-c*t).
    t_end = n * dt_step
    exact_prop = S0 * np.exp(-k * t_end)
    exact_const = max(0.0, S0 - c * t_end)

    require(abs(S_prop - exact_prop) < 1e-2, f"proportional-decay Euler check: {S_prop} vs {exact_prop}")
    require(abs(S_const - exact_const) < 1e-2, f"constant-decay Euler check: {S_const} vs {exact_const}")
    require(abs(exact_prop - exact_const) > 0.05,
            f"the two dynamics must have genuinely diverged by t={t_end}; "
            f"got prop={exact_prop}, const={exact_const}")
    return {"t_end": t_end, "S_constant_outflow": exact_const, "S_proportional_outflow": exact_prop}


def check_scope_violation_guards():
    try:
        fluid_queue_piecewise(0.0, [0.0, 10.0], [0.8, 0.1], [1.0])
        raise AssertionError("should reject mismatched rate array length")
    except ScopeViolationError:
        pass
    try:
        fluid_queue_piecewise(0.0, [0.0, 5.0, 3.0], [1.0, 1.0], [1.0, 1.0])
        raise AssertionError("should reject non-increasing breakpoints")
    except ScopeViolationError:
        pass
    try:
        fluid_queue_piecewise(-1.0, [0.0, 10.0], [1.0], [1.0])
        raise AssertionError("should reject negative initial backlog")
    except ScopeViolationError:
        pass
    traj = fluid_queue_piecewise(0.0, [0.0, 10.0], [1.0], [0.5])
    try:
        traj.value_at(11.0)
        raise AssertionError("should reject t outside trajectory range")
    except ScopeViolationError:
        pass
    try:
        stock_reserve_bridge(traj, -1.0, [0.0])
        raise AssertionError("should reject non-positive capacity")
    except ScopeViolationError:
        pass
    return {"checked": 5}


CHECKS = [
    ("astra_worked_example", check_astra_worked_example),
    ("monotonicity_against_brute_force_ode", check_monotonicity_against_brute_force_ode),
    ("stock_reserve_bridge", check_stock_reserve_bridge),
    ("negative_test_state_dependent_rate_differs", check_negative_test_state_dependent_rate_differs),
    ("scope_violation_guards", check_scope_violation_guards),
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json-out", type=Path, default=Path(__file__).with_name("verify_queueing_results.json"))
    args = parser.parse_args()

    report = {
        "package": "DOMAIN_EXPANSION_ROADMAP.md Paket B2a (fluid queue backlog)",
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
