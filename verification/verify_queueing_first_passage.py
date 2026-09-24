#!/usr/bin/env python3
"""M/M/1 exact first-passage probability (DOMAIN_EXPANSION_ROADMAP.md Paket B2b).

Checks:

  1. Plan's fixed reference: lambda=1, mu=2, K=2, n0=0, H=1 -> exactly
     0.1777365760981911 (hand-derived independently via the same absorbing-
     generator construction, run separately from the module during review).
  2. Arrivals-only reduction (mu=0): must equal the closed-form Poisson tail
     P(Poisson(lambda*H) >= K-n0) = 1-2/e for lambda=1, K=2, H=1.
  3. Edge cases: H=0 (must be 0 unless already at K), already-at/above-K
     (must be exactly 1.0 regardless of rates/horizon), lambda=0 (K then
     unreachable from below, must be 0), all handled by the SAME
     construction without special-case branches beyond the initial
     already-reached shortcut.
  4. Independent second implementation: an event-driven (Gillespie-style)
     simulation with a fixed seed must agree with the exact matrix-
     exponential answer within a pre-declared Monte Carlo tolerance.
  5. Piecewise-rate construction: splitting one constant-rate horizon into
     several equal-rate segments must reproduce the single-segment answer
     (order of composition matters in general; this is the check that
     splitting alone, with IDENTICAL rates, changes nothing).
  6. Distinguishing the stationary tail P(N>=K) from P(max_{t<=H} N_t>=K):
     for a queue with rho<1, the finite-horizon hitting probability must
     NOT equal the (unrelated) stationary tail probability -- checked as a
     genuine numerical divergence, not a naming distinction only.
  7. ScopeViolationError guards.
  8. SCF_Review_fcc9a43.md finding R5 (defense in depth): non-integer/NaN
     count states and NaN rates must raise a clean ScopeViolationError, not
     a raw numpy TypeError/IndexError from being used directly as an array
     size/index.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

import numpy as np
from scipy.linalg import expm
from scipy.stats import poisson

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from scoped_correspondence.errors import ScopeViolationError  # noqa: E402
from scoped_correspondence.viability.first_passage_ctmc import (  # noqa: E402
    mm1_absorbing_generator, queue_hitting_probability,
    queue_hitting_probability_piecewise, simulate_mm1_first_passage,
)


def require(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)


def check_plan_reference_value():
    p = queue_hitting_probability(0, 2, 1.0, 1.0, 2.0)
    want = 0.1777365760981911
    require(abs(p - want) < 1e-12, f"got {p}, want {want}")
    return {"p": p, "want": want}


def check_arrivals_only_poisson_reduction():
    p = queue_hitting_probability(0, 2, 1.0, 1.0, 0.0)
    want = 1.0 - 2.0 / np.e
    require(abs(p - want) < 1e-10, f"got {p}, want {want}")
    # independent cross-check via scipy.stats.poisson, not hand-derived constant
    want_scipy = 1.0 - poisson.cdf(1, mu=1.0)  # P(Poisson(1)>=2) = 1-P(N<=1)
    require(abs(p - want_scipy) < 1e-10, f"got {p}, scipy poisson gives {want_scipy}")
    return {"p": p, "want_closed_form": want, "want_scipy": want_scipy}


def check_edge_cases():
    require(queue_hitting_probability(0, 2, 0.0, 1.0, 2.0) == 0.0, "H=0 with n0<K must be exactly 0")
    require(queue_hitting_probability(2, 2, 1.0, 1.0, 2.0) == 1.0, "n0==K must be exactly 1")
    require(queue_hitting_probability(5, 2, 1.0, 1.0, 2.0) == 1.0, "n0>K must be exactly 1")
    require(queue_hitting_probability(0, 2, 5.0, 0.0, 2.0) == 0.0, "lambda=0 with n0<K must be exactly 0 (K unreachable)")
    require(queue_hitting_probability(0, 0, 1.0, 1.0, 2.0) == 1.0, "K=0 means n0=0 is already at the boundary")
    return {"checked": 5}


def check_independent_simulation_agrees():
    p_exact = queue_hitting_probability(0, 2, 1.0, 1.0, 2.0)
    sim = simulate_mm1_first_passage(0, 2, 1.0, 1.0, 2.0, n_trials=300_000, seed=20260924)
    # pre-declared Monte Carlo tolerance: 5 std devs of a Bernoulli(p_exact, n) proportion
    se = (p_exact * (1 - p_exact) / sim.n_trials) ** 0.5
    tol = 5 * se
    require(abs(sim.empirical_probability - p_exact) < tol,
            f"simulation {sim.empirical_probability} vs exact {p_exact}, tol={tol}")
    return {"exact": p_exact, "simulated": sim.empirical_probability, "tolerance_5sigma": tol, "n_trials": sim.n_trials}


def check_piecewise_reduces_to_single_segment():
    single = queue_hitting_probability(0, 2, 1.0, 1.0, 2.0)
    two_equal = queue_hitting_probability_piecewise(0, 2, [(0.5, 1.0, 2.0), (0.5, 1.0, 2.0)])
    four_equal = queue_hitting_probability_piecewise(0, 2, [(0.25, 1.0, 2.0)] * 4)
    require(abs(single - two_equal) < 1e-9, f"2-segment split diverges: {single} vs {two_equal}")
    require(abs(single - four_equal) < 1e-9, f"4-segment split diverges: {single} vs {four_equal}")

    # genuinely different piecewise rates: a rate change partway through must NOT equal
    # the "averaged constant rate" answer (matrix exponentials of different generators
    # do not commute / a time-order-sensitive construction).
    piecewise_varying = queue_hitting_probability_piecewise(0, 2, [(0.5, 2.0, 1.0), (0.5, 0.0, 1.0)])
    averaged_rate_wrong = queue_hitting_probability(0, 2, 1.0, 1.0, 1.0)  # naive average of (2,1) and (0,1)
    require(abs(piecewise_varying - averaged_rate_wrong) > 1e-6,
            "sanity: a genuinely time-varying rate schedule should NOT equal the naively "
            f"averaged-generator answer; got {piecewise_varying} vs {averaged_rate_wrong}")
    return {"single": single, "two_equal": two_equal, "four_equal": four_equal,
            "piecewise_varying": piecewise_varying, "averaged_rate_wrong": averaged_rate_wrong}


def check_stationary_tail_differs_from_finite_horizon_hitting():
    """rho=lambda/mu<1 stable queue: the stationary tail P(N>=K) is NOT the finite-
    horizon hitting probability P(max_{t<=H} N_t>=K) -- must differ numerically."""
    lam, mu, K = 0.5, 1.0, 5
    rho = lam / mu
    stationary_tail = rho ** K  # P(N>=K) = sum_{n>=K} (1-rho)*rho^n = rho^K
    finite_horizon = queue_hitting_probability(0, K, 2.0, lam, mu)
    require(abs(stationary_tail - finite_horizon) > 1e-3,
            f"stationary tail {stationary_tail} should differ from finite-horizon hitting {finite_horizon}")
    return {"stationary_tail": stationary_tail, "finite_horizon_hitting": finite_horizon, "rho": rho}


def check_scope_violation_guards():
    for kwargs, label in (
        (dict(initial_count=-1, threshold=2, horizon=1.0, arrival_rate=1.0, service_rate=1.0), "negative_n0"),
        (dict(initial_count=0, threshold=-1, horizon=1.0, arrival_rate=1.0, service_rate=1.0), "negative_threshold"),
        (dict(initial_count=0, threshold=2, horizon=-1.0, arrival_rate=1.0, service_rate=1.0), "negative_horizon"),
        (dict(initial_count=0, threshold=2, horizon=1.0, arrival_rate=-1.0, service_rate=1.0), "negative_arrival_rate"),
    ):
        try:
            queue_hitting_probability(**kwargs)
            raise AssertionError(f"should reject {label}")
        except ScopeViolationError:
            pass
    try:
        mm1_absorbing_generator(-1, 1.0, 1.0)
        raise AssertionError("should reject negative threshold in generator builder")
    except ScopeViolationError:
        pass
    try:
        queue_hitting_probability_piecewise(0, 2, [])
        raise AssertionError("should reject empty rate_segments")
    except ScopeViolationError:
        pass
    return {"checked": 6}


def check_r5_defense_in_depth_count_validation():
    """SCF_Review_fcc9a43.md finding R5 (defense in depth): non-integer/NaN count
    states must raise a clean ScopeViolationError, not a raw numpy TypeError/
    IndexError from being used directly as an array size/index."""
    for kwargs, label in (
        (dict(initial_count=0.4, threshold=2, horizon=1.0, arrival_rate=1.0, service_rate=1.0), "non_integer_initial_count"),
        (dict(initial_count=0, threshold=2.5, horizon=1.0, arrival_rate=1.0, service_rate=1.0), "non_integer_threshold"),
        (dict(initial_count=float("nan"), threshold=2, horizon=1.0, arrival_rate=1.0, service_rate=1.0), "nan_initial_count"),
        (dict(initial_count=0, threshold=2, horizon=1.0, arrival_rate=float("nan"), service_rate=1.0), "nan_arrival_rate"),
    ):
        try:
            queue_hitting_probability(**kwargs)
            raise AssertionError(f"should reject {label}")
        except ScopeViolationError:
            pass
    return {"checked": 4}


CHECKS = [
    ("plan_reference_value", check_plan_reference_value),
    ("arrivals_only_poisson_reduction", check_arrivals_only_poisson_reduction),
    ("edge_cases", check_edge_cases),
    ("independent_simulation_agrees", check_independent_simulation_agrees),
    ("piecewise_reduces_to_single_segment", check_piecewise_reduces_to_single_segment),
    ("stationary_tail_differs_from_finite_horizon_hitting", check_stationary_tail_differs_from_finite_horizon_hitting),
    ("scope_violation_guards", check_scope_violation_guards),
    ("r5_defense_in_depth_count_validation", check_r5_defense_in_depth_count_validation),
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json-out", type=Path, default=Path(__file__).with_name("verify_queueing_first_passage_results.json"))
    args = parser.parse_args()

    report = {
        "package": "DOMAIN_EXPANSION_ROADMAP.md Paket B2b (M/M/1 first-passage)",
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
