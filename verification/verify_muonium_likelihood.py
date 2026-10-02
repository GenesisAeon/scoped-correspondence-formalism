"""MU3 verification (MUONIUM_GRAVITY_ROADMAP.md, plan section 10/MU3):
count likelihood and estimation diagnostics.

Kontrollen MU-C08 (Poisson null cases, deviance = 2 (NLL - saturated)),
MU-C14 (periodic aliases: every mode in the search range is reported),
MU-C15 (quadrature sign; arcsin inversion is local only); synthetic
expected values reproduced; no negative / non-integer counts; search bound
hits, optimiser failures and non-convergence stay visible; no global claim
from a multistart.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from scoped_correspondence.errors import ScopeViolationError
from scoped_correspondence.muonium.forward import ForwardModel, VelocityClass, equal_time_bins
from scoped_correspondence.muonium.likelihood import multistart_fit, poisson_deviance, poisson_nll, signed_root_residuals

TAU, D, V = 2.2e-6, 100e-9, 2180.0
T = 2 * TAU
L = V * T
ALIAS = D / T ** 2
MODEL = ForwardModel(L=L, d=D, tau=TAU, classes=(VelocityClass(V, 1.0, transmission=0.5, contrast=0.35),), rate=2.0e6, background=1.0)
BINS = equal_time_bins(4.0, [0.0, math.pi / 2, math.pi, 3 * math.pi / 2])
A_TRUE = 9.81


def require(c, m=""):
    if not c:
        raise AssertionError(m)


def raises(fn, exc=ScopeViolationError):
    try:
        fn()
    except exc:
        return True
    return False


def synthetic_counts(seed=3):
    lam = MODEL.expected_counts(A_TRUE, BINS)
    return [int(x) for x in np.random.default_rng(seed).poisson(lam)], lam


def check_mu_c08_null_cases_and_deviance():
    require(poisson_nll([0], [0.0]) == 0.0, "NLL(0;0) = 0")
    require(poisson_nll([3], [0.0]) == math.inf, "NLL(n>0;0) = inf: no artificial floor")
    for n, lam in ((0, 2.5), (4, 2.5), (7, 9.0), (12, 3.2)):
        sat = poisson_nll([n], [float(n)]) if n > 0 else 0.0
        require(math.isclose(poisson_deviance([n], [lam]), 2 * (poisson_nll([n], [lam]) - sat), rel_tol=1e-12, abs_tol=1e-12),
                f"deviance = 2 (NLL - saturated) at n={n}, lambda={lam}")
    require(poisson_deviance([0], [2.5]) == 5.0, "zero-count deviance term 2 lambda")
    counts, lam = synthetic_counts()
    r = signed_root_residuals(counts, lam)
    require(math.isclose(sum(x * x for x in r), poisson_deviance(counts, lam), rel_tol=1e-12), "signed roots reproduce D")
    require(raises(lambda: poisson_nll([-1], [1.0])) and raises(lambda: poisson_nll([1.5], [1.0])) and raises(lambda: poisson_nll([True], [1.0])),
            "negative, non-integer or boolean counts rejected")
    require(raises(lambda: poisson_nll([1], [-0.1])), "negative mean rejected")
    return {"deviance_zero_count": 5.0}


def check_synthetic_expected_values_reproduced():
    lam = MODEL.expected_counts(A_TRUE, BINS)
    W, F = MODEL.complex_contrast(A_TRUE)
    manual = [b.t * MODEL.background + b.t * MODEL.rate * W * (1 + (complex(math.cos(b.alpha), math.sin(b.alpha)) * F).real) for b in BINS]
    require(all(math.isclose(x, y, rel_tol=1e-14) for x, y in zip(lam, manual)), "expected counts reproduce the forward formula")
    counts, _ = synthetic_counts()
    fit = multistart_fit(lambda x: poisson_nll(counts, MODEL.expected_counts(x[0], BINS)), ["a"], [(A_TRUE - 0.4 * ALIAS, A_TRUE + 0.4 * ALIAS)], n_starts=8)
    require(fit.best is not None and abs(fit.best.x[0] - A_TRUE) < 0.05 * ALIAS, f"recovers a near truth within one period, got {fit.best}")
    return {"a_hat": fit.best.x[0], "alias_period": ALIAS}


def check_mu_c14_all_alias_modes_reported():
    counts, _ = synthetic_counts()
    nll = lambda x: poisson_nll(counts, MODEL.expected_counts(x[0], BINS))
    fit = multistart_fit(nll, ["a"], [(A_TRUE - 0.5 * ALIAS, A_TRUE + 2.5 * ALIAS)], n_starts=24, obj_tol=1e-6)
    best = fit.best.objective
    near = sorted(m.x[0] for m in fit.modes if m.objective - best <= 1e-6)
    require(len(near) >= 3, f"three alias modes expected in the range, got {near}")
    gaps = [b - a for a, b in zip(near, near[1:])]
    require(all(math.isclose(g, ALIAS, rel_tol=1e-3) for g in gaps), f"modes separated by d/T^2 = {ALIAS}: {gaps}")
    require(any("distinct modes" in n for n in fit.notes), "the report says that several modes exist")
    return {"modes": near, "period": ALIAS}


def check_mu_c15_quadrature_sign_and_local_inverse():
    C, lam0 = 0.3, 1000.0
    counts = lambda phi: lam0 * (1 + C * math.cos(math.pi / 2 + phi))
    require(counts(0.1) < counts(0.0) < counts(-0.1), "at quadrature the count decreases with phi")
    phi = 0.4
    require(math.isclose(math.asin((1 - counts(phi) / lam0) / C), phi, rel_tol=1e-12), "arcsin inverts locally")
    require(math.isclose(counts(math.pi - phi), counts(phi), rel_tol=1e-12), "pi - phi gives the same count: no global inversion")
    return {"local_only": True}


def check_bounds_and_failures_visible():
    counts, _ = synthetic_counts()
    nll = lambda x: poisson_nll(counts, MODEL.expected_counts(x[0], BINS))
    edge = multistart_fit(nll, ["a"], [(A_TRUE + 0.1 * ALIAS, A_TRUE + 0.3 * ALIAS)], n_starts=6)
    require(edge.best.boundary_hit and any("search bound" in n for n in edge.notes), "a search range excluding the optimum reports a bound hit")

    def flaky(x):
        if x[0] > 0.5:
            raise RuntimeError("model evaluation failed")
        return (x[0] - 0.2) ** 2

    rep = multistart_fit(flaky, ["a"], [(0.0, 1.0)], n_starts=4)
    require(rep.n_failed > 0 and any("did not converge or failed" in n for n in rep.notes), "failed runs are counted, not hidden")
    require(any("no global optimality claim" in n for n in rep.notes), "multistart makes no global claim")
    require(raises(lambda: multistart_fit(flaky, ["a"], [(0.0, math.inf)])), "the search range must be explicit and finite")
    return {"edge_note": [n for n in edge.notes if "bound" in n][0], "failed_runs": rep.n_failed}


CHECKS = [
    check_mu_c08_null_cases_and_deviance,
    check_synthetic_expected_values_reproduced,
    check_mu_c14_all_alias_modes_reported,
    check_mu_c15_quadrature_sign_and_local_inverse,
    check_bounds_and_failures_visible,
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
    out_path = Path(__file__).with_name("verify_muonium_likelihood_results.json")
    out_path.write_text(json.dumps({"n_passed": n_passed, "n_total": len(CHECKS), "results": results}, indent=2, default=str))
    print(f"Report written to {out_path}")
    return 0 if n_passed == len(CHECKS) else 1


if __name__ == "__main__":
    raise SystemExit(main())
