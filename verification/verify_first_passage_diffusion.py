#!/usr/bin/env python3
"""Brownian motion with drift: lower-barrier first-passage (DOMAIN_EXPANSION_ROADMAP.md Paket B4).

Checks:

  1. Plan's fixed control values at x0=1, sigma=1, H=1: mu=0 ->
     2*Phi(-1)=0.31731050786291415; mu=1 -> 0.09041777356648555 despite
     E[X_1]=2 -- a positive expected reserve does NOT imply low hitting risk.
  2. Infinite-horizon ever-hitting probability exp(-2*mu*x0/sigma^2) for
     mu>0, distinguished from any finite-horizon extrapolation.
  3. Unit-scaling invariance: t'=t/c, mu'=c*mu, sigma'=sqrt(c)*sigma,
     H'=H/c must leave P(tau_0<=H) exactly unchanged, for c spanning 12
     orders of magnitude.
  4. Deterministic (sigma=0) limit and edge cases: H=0, x0<=0 (already at
     the boundary), mu>=0 with sigma=0 (never hits), mu<0 with sigma=0
     (hits exactly at x0/(-mu)).
  5. Monotonicity: hitting probability is non-decreasing in horizon and
     non-increasing in initial reserve x0, for a fixed drift/diffusion.
  6. Independent Monte Carlo cross-check (fine time grid, fixed seed,
     large sample) within a pre-declared tolerance.
  7. Brownian-bridge crossing probability control value and
     ScopeViolationError guards.
  8. SCF_Review_fcc9a43.md finding R4a: a constant, noiseless path never
     moves, so it never hits 0 -- checked against the old bug (mu<=0
     checked before sigma=0).
  9. SCF_Review_fcc9a43.md finding R5: NaN inputs must be rejected, not
     silently laundered into a plausible-looking probability via min()/max().
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

import numpy as np
from scipy.stats import norm

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from scoped_correspondence.errors import ScopeViolationError  # noqa: E402
from scoped_correspondence.viability.first_passage_diffusion import (  # noqa: E402
    diffusion_lower_hitting_probability, diffusion_ever_hitting_probability,
    brownian_bridge_crossing_probability,
)


def require(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)


def check_plan_control_values():
    p0 = diffusion_lower_hitting_probability(1.0, 0.0, 1.0, 1.0)
    p1 = diffusion_lower_hitting_probability(1.0, 1.0, 1.0, 1.0)
    want0 = 2.0 * norm.cdf(-1.0)
    want1 = 0.09041777356648555
    require(abs(p0 - want0) < 1e-12, f"mu=0: got {p0}, want {want0}")
    require(abs(p1 - want1) < 1e-12, f"mu=1: got {p1}, want {want1}")
    require(1.0 + 1.0 * 1.0 == 2.0, "sanity: E[X_1]=x0+mu*H=2 for this case")
    require(p1 < 0.5, "despite E[X_1]=2>0, the hitting probability should still be a real, non-trivial number")
    return {"p_mu0": p0, "p_mu1": p1, "e_x1": 2.0}


def check_infinite_horizon_ever_hitting():
    p_inf = diffusion_ever_hitting_probability(1.0, 1.0, 1.0)
    want = np.exp(-2.0)
    require(abs(p_inf - want) < 1e-14, f"got {p_inf}, want {want}")
    # sanity: must exceed the finite-horizon H=1 probability (more time to hit -> more likely)
    p_h1 = diffusion_lower_hitting_probability(1.0, 1.0, 1.0, 1.0)
    require(p_inf > p_h1, f"infinite-horizon ever-hit {p_inf} should exceed finite H=1 hit {p_h1}")
    # mu<=0: certain eventual hit
    require(diffusion_ever_hitting_probability(1.0, 0.0, 1.0) == 1.0, "mu=0 must hit eventually a.s.")
    require(diffusion_ever_hitting_probability(1.0, -1.0, 1.0) == 1.0, "mu<0 must hit eventually a.s.")
    return {"p_ever_mu1": p_inf, "p_finite_h1_mu1": p_h1}


def check_unit_scaling_invariance():
    x0, mu, sigma, H = 1.0, 1.0, 1.0, 1.0
    base = diffusion_lower_hitting_probability(x0, mu, sigma, H)
    results = {}
    for c in (1e-6, 1e-3, 1.0, 1e3, 1e6):
        p = diffusion_lower_hitting_probability(x0, c * mu, np.sqrt(c) * sigma, H / c)
        require(abs(p - base) < 1e-10, f"c={c}: got {p}, base {base}")
        results[str(c)] = p
    return {"base": base, "rescaled": results}


def check_deterministic_and_edge_cases():
    require(diffusion_lower_hitting_probability(1.0, 0.0, 1.0, 0.0) == 0.0, "H=0, x0>0 must give 0")
    require(diffusion_lower_hitting_probability(0.0, 1.0, 1.0, 5.0) == 1.0, "x0=0 already at boundary")
    require(diffusion_lower_hitting_probability(-1.0, 1.0, 1.0, 5.0) == 1.0, "x0<0 already past boundary")
    require(diffusion_lower_hitting_probability(2.0, 0.5, 0.0, 100.0) == 0.0,
            "sigma=0, mu>0: deterministic path moves away from 0 forever")
    t_star = 2.0 / 1.0  # x0=2, mu=-1
    require(diffusion_lower_hitting_probability(2.0, -1.0, 0.0, t_star - 0.5) == 0.0,
            "sigma=0, mu<0: should not have hit yet just before t_star")
    require(diffusion_lower_hitting_probability(2.0, -1.0, 0.0, t_star + 0.5) == 1.0,
            "sigma=0, mu<0: should have hit by just after t_star")
    return {"t_star": t_star, "checked": 6}


def check_monotonicity():
    x0, mu, sigma = 1.0, 0.2, 1.0
    horizons = [0.1, 0.5, 1.0, 5.0, 20.0]
    probs = [diffusion_lower_hitting_probability(x0, mu, sigma, h) for h in horizons]
    require(all(probs[i] <= probs[i + 1] + 1e-12 for i in range(len(probs) - 1)),
            f"hitting probability should be non-decreasing in horizon; got {probs}")

    reserves = [0.5, 1.0, 2.0, 5.0]
    probs_x0 = [diffusion_lower_hitting_probability(x, mu, sigma, 5.0) for x in reserves]
    require(all(probs_x0[i] >= probs_x0[i + 1] - 1e-12 for i in range(len(probs_x0) - 1)),
            f"hitting probability should be non-increasing in initial reserve; got {probs_x0}")
    return {"probs_vs_horizon": probs, "probs_vs_x0": probs_x0}


def check_monte_carlo_cross_check():
    """Independent second implementation: coarse Euler-Maruyama simulation with a
    fixed seed, pre-declared tolerance (6 std devs of a Bernoulli proportion).

    **Correction (SCF_Review_fcc9a43.md, minor finding):** a POPULATION-level
    discrete-time-grid hitting probability is a legitimate lower bound on the
    true continuous-time probability (a grid can only MISS crossings that
    happen strictly between two sampled points, never fabricate one) -- but a
    FINITE Monte Carlo SAMPLE of that population quantity is a random estimate
    with its own sampling noise, and is NOT guaranteed to fall below the exact
    value on every run. The old test asserted a strict, near-zero-tolerance
    one-sided bound (``p_mc <= p_exact + 1e-9``) that conflated the population
    fact with a per-sample guarantee -- removed here. The two-sided statistical
    tolerance below already covers "not too far above or below"; no additional
    directional assertion is made on a single finite sample.
    """
    x0, mu, sigma, H = 1.0, 1.0, 1.0, 1.0
    p_exact = diffusion_lower_hitting_probability(x0, mu, sigma, H)

    rng = np.random.default_rng(20260924)
    n_paths = 40_000
    n_steps = 400
    dt_step = H / n_steps
    hits = 0
    for _ in range(n_paths):
        x = x0
        for _ in range(n_steps):
            x += mu * dt_step + sigma * np.sqrt(dt_step) * rng.standard_normal()
            if x <= 0.0:
                hits += 1
                break
    p_mc = hits / n_paths
    se = (p_exact * (1 - p_exact) / n_paths) ** 0.5
    tol = 6 * se
    require(abs(p_mc - p_exact) < tol, f"Monte Carlo {p_mc} vs exact {p_exact}, tol={tol}")
    return {"exact": p_exact, "monte_carlo": p_mc, "n_paths": n_paths, "n_steps": n_steps, "tolerance": tol}


def check_r4a_deterministic_ever_hitting():
    """SCF_Review_fcc9a43.md finding R4a: a constant, noiseless path (x0=1, mu=0,
    sigma=0) never moves, so it never hits 0 -- diffusion_ever_hitting_probability
    must return 0.0, not 1.0 (the old code checked mu<=0 before sigma==0)."""
    require(diffusion_ever_hitting_probability(1.0, 0.0, 0.0) == 0.0,
            f"constant path must never hit 0; got {diffusion_ever_hitting_probability(1.0, 0.0, 0.0)}")
    require(diffusion_ever_hitting_probability(1.0, -1.0, 0.0) == 1.0,
            "deterministic downward drift must hit 0 in finite time")
    require(diffusion_ever_hitting_probability(1.0, 0.5, 0.0) == 0.0,
            "deterministic upward drift must never hit 0")
    # regressions: genuine diffusion cases unaffected by the reordering
    require(diffusion_ever_hitting_probability(1.0, 0.0, 1.0) == 1.0, "regression: driftless diffusion hits a.s.")
    require(diffusion_ever_hitting_probability(1.0, -1.0, 1.0) == 1.0, "regression: negative-drift diffusion hits a.s.")
    require(abs(diffusion_ever_hitting_probability(1.0, 1.0, 1.0) - np.exp(-2.0)) < 1e-14, "regression: positive-drift value")
    return {"checked": 6}


def check_r5_nan_rejected():
    """SCF_Review_fcc9a43.md finding R5: NaN inputs must be rejected, not silently
    laundered into a plausible-looking probability via min()/max()."""
    for fn, args in (
        (diffusion_lower_hitting_probability, (float("nan"), 1.0, 1.0, 1.0)),
        (diffusion_lower_hitting_probability, (1.0, float("nan"), 1.0, 1.0)),
        (diffusion_ever_hitting_probability, (float("nan"), 1.0, 1.0)),
        (brownian_bridge_crossing_probability, (float("nan"), 1.0, 1.0, 1.0)),
    ):
        try:
            fn(*args)
            raise AssertionError(f"{fn.__name__}{args} should reject NaN input")
        except ScopeViolationError:
            pass
    return {"checked": 4}


def check_bridge_and_scope_guards():
    b = brownian_bridge_crossing_probability(1.0, 1.0, 1.0, 1.0)
    require(abs(b - np.exp(-2.0)) < 1e-14, f"got {b}, want {np.exp(-2.0)}")

    for kwargs, label in (
        (dict(x=0.0, y=1.0, sigma=1.0, delta=1.0), "x_zero"),
        (dict(x=1.0, y=-1.0, sigma=1.0, delta=1.0), "y_negative"),
        (dict(x=1.0, y=1.0, sigma=0.0, delta=1.0), "sigma_zero"),
        (dict(x=1.0, y=1.0, sigma=1.0, delta=0.0), "delta_zero"),
    ):
        try:
            brownian_bridge_crossing_probability(**kwargs)
            raise AssertionError(f"should reject {label}")
        except ScopeViolationError:
            pass

    try:
        diffusion_lower_hitting_probability(1.0, 0.0, 1.0, -1.0)
        raise AssertionError("should reject negative horizon")
    except ScopeViolationError:
        pass
    try:
        diffusion_lower_hitting_probability(1.0, 0.0, -1.0, 1.0)
        raise AssertionError("should reject negative sigma")
    except ScopeViolationError:
        pass
    return {"bridge_value": b, "checked_guards": 6}


CHECKS = [
    ("plan_control_values", check_plan_control_values),
    ("infinite_horizon_ever_hitting", check_infinite_horizon_ever_hitting),
    ("unit_scaling_invariance", check_unit_scaling_invariance),
    ("deterministic_and_edge_cases", check_deterministic_and_edge_cases),
    ("monotonicity", check_monotonicity),
    ("monte_carlo_cross_check", check_monte_carlo_cross_check),
    ("bridge_and_scope_guards", check_bridge_and_scope_guards),
    ("r4a_deterministic_ever_hitting", check_r4a_deterministic_ever_hitting),
    ("r5_nan_rejected", check_r5_nan_rejected),
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json-out", type=Path, default=Path(__file__).with_name("verify_first_passage_diffusion_results.json"))
    args = parser.parse_args()

    report = {
        "package": "DOMAIN_EXPANSION_ROADMAP.md Paket B4 (diffusion first-passage)",
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
