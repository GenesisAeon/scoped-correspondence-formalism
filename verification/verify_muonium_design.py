"""MU5 verification (MUONIUM_GRAVITY_ROADMAP.md, plan section 10/MU5):
design, Fisher information and a small conditional coverage study.

Kontrollen MU-C04 (T = 2 tau optimum for a fixed INCOMING budget), MU-C12
(I_phi = 8 for the four-step scan vs 16 at quadrature, N = 400, C = 0.2),
MU-C13 (~5.73265035e8 detected events for 1 %), MU-C16 (no contrast -> no
information); singular Fisher matrix reported (no pseudo-inverse); a
reproducible coverage study with PRE-DECLARED scenarios and binomial
uncertainty: correct model, omitted offset, non-identifiable joint fit.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from scoped_correspondence.errors import ScopeViolationError
from scoped_correspondence.muonium.design import (
    deviance_interval,
    events_for_relative_precision,
    joint_fisher,
    phase_fisher,
    sigma_a_local_bound,
    sigma_vs_flight_time,
)
from scoped_correspondence.muonium.likelihood import poisson_nll

G, TAU, D = 9.81, 2.2e-6, 100e-9
T = 2 * TAU
K = 2 * math.pi * T ** 2 / D
ALPHAS = [0.0, math.pi / 2, math.pi, 3 * math.pi / 2]


def require(c, m=""):
    if not c:
        raise AssertionError(m)


def raises(fn, exc=ScopeViolationError):
    try:
        fn()
    except exc:
        return True
    return False


def check_mu_c12_scan_vs_quadrature():
    scan = phase_fisher([100.0] * 4, ALPHAS, 0.2)
    quad = phase_fisher([400.0], [math.pi / 2], 0.2)
    require(math.isclose(scan, 8.0, rel_tol=1e-12) and math.isclose(quad, 16.0, rel_tol=1e-12), f"I_phi 8 vs 16, got {scan}, {quad}")
    return {"scan": scan, "quadrature": quad}


def check_mu_c13_events_for_one_percent():
    N = events_for_relative_precision(0.01, G, 0.35, K)
    require(math.isclose(N, 5.73265035e8, rel_tol=1e-8), f"N = {N}")
    require(math.isclose(sigma_a_local_bound(N, 0.35, K), 0.01 * G, rel_tol=1e-12), "consistency with the local bound")
    return {"N": N}


def check_mu_c16_no_contrast():
    require(phase_fisher([100.0] * 4, ALPHAS, 0.0) == 0.0 and sigma_a_local_bound(1e6, 0.0, K) is None,
            "C = 0: zero information, no finite bound")
    return {"I": 0.0}


def check_mu_c04_budget_named_optimum():
    ts = np.linspace(0.5 * TAU, 4 * TAU, 701)
    s = [sigma_vs_flight_time(t, TAU, budget="incoming_atoms") for t in ts]
    t_opt = ts[int(np.argmin(s))]
    require(abs(t_opt - 2 * TAU) <= (ts[1] - ts[0]), f"incoming budget: optimum at 2 tau, got {t_opt / TAU} tau")
    s_det = [sigma_vs_flight_time(t, TAU, budget="detected_events") for t in ts]
    require(int(np.argmin(s_det)) == len(ts) - 1, "fixed DETECTED events: no decay cost, sigma falls monotonically (different budget, different answer)")
    require(raises(lambda: sigma_vs_flight_time(T, TAU, budget="measurement_time")) and raises(lambda: sigma_vs_flight_time(T, TAU, budget="atoms")),
            "budget must be named and modelled")
    return {"T_opt_over_tau": t_opt / TAU}


def check_singular_fisher_not_pseudo_inverted():
    one = joint_fisher([100.0] * 4, ALPHAS, 0.3, [K] * 4, free_offset=True)
    require(one.singular and one.covariance_bound is None and one.rank == 1, "one flight time + free offset: singular, no variance bound")
    two = joint_fisher([100.0] * 8, ALPHAS * 2, 0.3, [K] * 4 + [4 * K] * 4, free_offset=True)
    require(not two.singular and two.covariance_bound is not None, "two flight times: regular (locally)")
    known = joint_fisher([100.0] * 4, ALPHAS, 0.3, [K] * 4, free_offset=False)
    require(math.isclose(known.matrix[0][0], phase_fisher([100.0] * 4, ALPHAS, 0.3) * K * K, rel_tol=1e-12), "I_a = I_phi K^2")
    return {"single_time_rank": one.rank, "two_time_rank": two.rank}


def _coverage(scenario, *, reps=300, seed=11):
    """Pre-declared scenarios (fixed BEFORE running):
    correct           -- fit a with phi0 known (= 0), truth phi0 = 0;
    omitted_offset    -- truth phi0 = 0.15 rad, fit assumes phi0 = 0;
    nonidentifiable   -- fit a with phi0 profiled out at one flight time.
    Search range: a in g_ref +- 0.45 d/T^2 (declared, excludes aliases)."""
    rng = np.random.default_rng(seed)
    C, n_step, a_true = 0.35, 4000.0, G
    grid = np.linspace(a_true - 0.45 * D / T ** 2, a_true + 0.45 * D / T ** 2, 1801)
    phi0_true = 0.15 if scenario == "omitted_offset" else 0.0
    lam = lambda a, phi0: np.array([n_step * (1 + C * math.cos(al + K * a + phi0)) for al in ALPHAS])
    covered = unbounded = 0
    for _ in range(reps):
        counts = rng.poisson(lam(a_true, phi0_true)).tolist()
        if scenario == "nonidentifiable":
            # profile over phi0 on a fine grid: NLL depends only on K a + phi0 -> flat in a
            phis = np.linspace(-math.pi, math.pi, 181)
            nll = np.array([min(poisson_nll(counts, lam(a, p).tolist()) for p in phis) for a in grid[::30]])
            ival, touches = deviance_interval(nll, grid[::30])
        else:
            nll = np.array([poisson_nll(counts, lam(a, 0.0).tolist()) for a in grid])
            ival, touches = deviance_interval(nll, grid)
        if touches:
            unbounded += 1
        if ival and ival[0] <= a_true <= ival[1]:
            covered += 1
    cov = covered / reps
    return cov, math.sqrt(cov * (1 - cov) / reps) if 0 < cov < 1 else 1 / reps, unbounded, reps


def check_coverage_study():
    cov_ok, se_ok, unb_ok, n = _coverage("correct")
    require(abs(cov_ok - 0.95) <= 3 * max(se_ok, math.sqrt(0.95 * 0.05 / n)) and unb_ok == 0,
            f"correct model: coverage {cov_ok:.3f} +- {se_ok:.3f} consistent with 0.95 (3 SE), no bound hits")
    cov_off, se_off, _, _ = _coverage("omitted_offset")
    require(cov_off < 0.5, f"omitted offset: coverage collapses ({cov_off:.3f}) -- a documented negative result, not hidden")
    cov_ni, _, unb_ni, n_ni = _coverage("nonidentifiable", reps=40)
    require(unb_ni == n_ni, f"non-identifiable joint fit: every interval reaches the search bounds ({unb_ni}/{n_ni})")
    return {"correct": {"coverage": cov_ok, "se": se_ok, "reps": n, "seed": 11},
            "omitted_offset": {"coverage": cov_off, "se": se_off},
            "nonidentifiable": {"intervals_touching_bounds": f"{unb_ni}/{n_ni}"},
            "threshold": "3.84 (asymptotic reference for a regular scalar parameter)"}


CHECKS = [
    check_mu_c12_scan_vs_quadrature,
    check_mu_c13_events_for_one_percent,
    check_mu_c16_no_contrast,
    check_mu_c04_budget_named_optimum,
    check_singular_fisher_not_pseudo_inverted,
    check_coverage_study,
]


def main():
    results = {}
    n_passed = 0
    for check in CHECKS:
        name = check.__name__.removeprefix("check_")
        try:
            results[name] = check()
            print(f"PASS  {name}")
            n_passed += 1
        except AssertionError as e:
            results[name] = {"error": str(e)}
            print(f"FAIL  {name}: {e}")
        except Exception as e:
            results[name] = {"error": f"{type(e).__name__}: {e}"}
            print(f"ERROR {name}: {type(e).__name__}: {e}")
    print(f"\n{n_passed}/{len(CHECKS)} checks passed")
    out_path = Path(__file__).with_name("verify_muonium_design_results.json")
    out_path.write_text(json.dumps({"n_passed": n_passed, "n_total": len(CHECKS), "results": results}, indent=2, default=str))
    print(f"Report written to {out_path}")
    return 0 if n_passed == len(CHECKS) else 1


if __name__ == "__main__":
    raise SystemExit(main())
