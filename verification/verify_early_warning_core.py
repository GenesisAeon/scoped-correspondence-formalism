#!/usr/bin/env python3
"""Hand-checkable verification for Early-Warning / CSD (Milestone 36).

Checks: a=0.5/0.05 examples; inverse λ̂; control far-from-fold; fence+sources;
scope/core CALL. Stdlib only. JSON {count,passed,failed,report}.
"""
from __future__ import annotations

import argparse, datetime as dt, inspect, json, math, platform, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from scoped_correspondence.dynamics.core import fixed_points, recovery_rate_at_equilibrium
from scoped_correspondence.dynamics import early_warning as ew
from scoped_correspondence.dynamics.early_warning import (
    EARLY_WARNING_COUNTEREXAMPLE_FENCE, SOURCE, control_far_from_fold,
    early_warning_at_cusp, estimate_lambda_from_ar1, lambda_from_cusp_equilibrium,
    ou_autocorrelation, ou_variance,
)
from scoped_correspondence.errors import ScopeViolationError


def require(ok, msg):
    if not bool(ok):
        raise AssertionError(msg)


def near(a, b, atol=1e-12, rtol=1e-9):
    if not math.isclose(float(a), float(b), abs_tol=atol, rel_tol=rtol):
        raise AssertionError(f"{a!r} != {b!r}")


def check_example_a05():
    a, b, tau, sigma2, delta_t = 0.5, 0.0, 1.0, 0.02, 1.0
    sigma = math.sqrt(sigma2)
    x_star = math.sqrt(a)
    roots = fixed_points(a, b)
    require(any(math.isclose(r, x_star, abs_tol=1e-12) for r in roots), f"roots {roots}")
    s_rec = recovery_rate_at_equilibrium(x_star, a, tau, b)
    near(s_rec, 1.0)
    lam = lambda_from_cusp_equilibrium(x_star, a, tau, b)
    near(lam, s_rec)
    var = ou_variance(sigma, lam)
    near(var, 0.01)
    rho = ou_autocorrelation(lam, delta_t)
    near(rho, math.exp(-1.0), atol=1e-12)
    near(rho, 0.3678794411714423, atol=1e-9)
    ind = early_warning_at_cusp(x_star, a, sigma, delta_t, tau=tau, b=b)
    near(ind.lam, 1.0); near(ind.variance, 0.01); near(ind.rho, rho)
    return {"a": a, "x_star": float(x_star), "S_rec_core": float(s_rec), "lam": float(lam),
            "variance": float(var), "variance_expected": 0.01, "rho": float(rho),
            "rho_expected_exp_m1": float(math.exp(-1.0)),
            "uses_recovery_rate_at_equilibrium_call": True}


def check_example_a005_and_inverse():
    a, b, tau, sigma2, delta_t = 0.05, 0.0, 1.0, 0.02, 1.0
    sigma = math.sqrt(sigma2)
    x_star = math.sqrt(a)
    s_rec = recovery_rate_at_equilibrium(x_star, a, tau, b)
    near(s_rec, 0.1)
    var = ou_variance(sigma, s_rec)
    near(var, 0.1)
    rho = ou_autocorrelation(s_rec, delta_t)
    near(rho, math.exp(-0.1), atol=1e-12)
    near(rho, 0.9048374180359595, atol=1e-9)
    lam_hat = estimate_lambda_from_ar1(math.exp(-0.1), delta_t)
    near(lam_hat, 0.1, atol=1e-15)
    lam_hat_brief = estimate_lambda_from_ar1(0.904837, delta_t)
    near(lam_hat_brief, 0.1, atol=5e-7)
    return {"a": a, "x_star": float(x_star), "S_rec_core": float(s_rec),
            "variance": float(var), "variance_expected": 0.1, "rho": float(rho),
            "rho_expected_exp_m01": float(math.exp(-0.1)),
            "lambda_hat_from_exp_m01": float(lam_hat),
            "lambda_hat_from_rho_0_904837": float(lam_hat_brief),
            "inverse_recovers_0_1": True}


def check_control_far_from_fold():
    sigma, delta_t = math.sqrt(0.02), 1.0
    summary = control_far_from_fold((2.0, 2.5), sigma, delta_t, tau=1.0, b=0.0)
    require(summary["var_rho_stable"], f"expected stable; got {summary}")
    for ind in summary["indicators"]:
        require(ind["lam"] >= 4.0, f"large λ; got {ind['lam']}")
        require(ind["rho"] < 0.05, f"small ρ; got {ind['rho']}")
        require(ind["variance"] < 0.01, f"small Var; got {ind['variance']}")
    near_crit = early_warning_at_cusp(math.sqrt(0.05), 0.05, sigma, delta_t)
    require(near_crit.rho > 0.9, "near-critical ρ large")
    require(near_crit.variance > summary["indicators"][0]["variance"] * 5, "Var contrast")
    summary["near_critical_contrast"] = near_crit.as_dict()
    return summary


def check_fence_and_sources():
    fence = EARLY_WARNING_COUNTEREXAMPLE_FENCE
    require(fence in (ew.__doc__ or ""), "fence missing from module docstring")
    require("Boettiger & Hastings 2012 DOI 10.1098/rsif.2012.0125" in fence, "Boettiger")
    require("Ditlevsen & Johnsen 2010 DOI 10.1029/2010GL044486" in fence, "Ditlevsen")
    require("NOT sufficient" in fence and "false alarms" in fence, "necessary≠sufficient")
    require("noise-induced" in fence, "D-O")
    require("no Var/S_rec ≡ beta_response" in fence, "beta_response")
    require("10.1038/nature08227" in SOURCE, "Scheffer")
    docs_text = (ROOT / "docs" / "early_warning_core.md").read_text(encoding="utf-8")
    require("Counterexample" in docs_text, "docs Counterexample")
    require("10.1098/rsif.2012.0125" in docs_text and "10.1029/2010GL044486" in docs_text, "docs DOIs")
    require("beta_response" in docs_text, "docs beta_response")
    return {"EARLY_WARNING_COUNTEREXAMPLE_FENCE": fence, "SOURCE": SOURCE,
            "fence_in_module_docstring": True, "docs_has_counterexample_section": True,
            "cites_scheffer_2009": True, "cites_boettiger_hastings_2012": True,
            "cites_ditlevsen_johnsen_2010": True, "no_var_srec_equiv_beta_response": True}


def check_scope_and_core_call():
    raised = False
    try: ou_variance(1.0, 0.0)
    except ScopeViolationError: raised = True
    require(raised, "λ=0 must raise")
    raised_neg = False
    try: ou_variance(1.0, -0.1)
    except ScopeViolationError: raised_neg = True
    require(raised_neg, "λ<0 must raise")
    src = inspect.getsource(lambda_from_cusp_equilibrium)
    require("recovery_rate_at_equilibrium" in src, "must call core")
    mod_src = Path(ew.__file__).read_text(encoding="utf-8")
    require("from scoped_correspondence.dynamics.core import recovery_rate_at_equilibrium" in mod_src,
            "must import from core")
    return {"lam_le_0_raises": True, "calls_recovery_rate_at_equilibrium": True,
            "reimplements_S_rec": False, "dynamics_core_edited": False}


CHECKS = [
    ("example_a_0_5", check_example_a05),
    ("example_a_0_05_and_inverse", check_example_a005_and_inverse),
    ("control_far_from_fold", check_control_far_from_fold),
    ("fence_and_sources", check_fence_and_sources),
    ("scope_and_core_call", check_scope_and_core_call),
]


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--json-out", type=Path, default=None)
    args = p.parse_args(argv)
    report = {
        "milestone": "M36", "title": "Early-Warning / Critical Slowing Down",
        "timestamp": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "platform": platform.platform(), "python": sys.version.split()[0],
        "EARLY_WARNING_COUNTEREXAMPLE_FENCE": EARLY_WARNING_COUNTEREXAMPLE_FENCE,
        "SOURCE": SOURCE, "checks": {},
    }
    failures = []
    for name, fn in CHECKS:
        try:
            report["checks"][name] = {"ok": True, "data": fn()}
        except Exception as e:
            report["checks"][name] = {"ok": False, "error": f"{type(e).__name__}: {e}"}
            failures.append(name)
    out = {"count": len(CHECKS), "passed": len(CHECKS) - len(failures),
           "failed": len(failures), "failures": failures, "report": report}
    text = json.dumps(out, indent=2, sort_keys=True)
    print(text)
    json_path = args.json_out or Path(__file__).with_name("verify_early_warning_core_results.json")
    json_path.write_text(text + "\n", encoding="utf-8")
    print(f"WROTE {json_path}", file=sys.stderr)
    if failures:
        print(f"FAILED {len(failures)}/{len(CHECKS)}: {failures}", file=sys.stderr)
        return 1
    print(f"PASSED {len(CHECKS)}/{len(CHECKS)}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
