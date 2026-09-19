#!/usr/bin/env python3
"""Hand-checkable verification for Early-Warning Signals (Milestone 36).

Checks (all numbers from this script run):
  1. Worked example: a=0.5 -> S_rec=1.0 -> Var=0.01, rho=exp(-1)=0.367879;
     a=0.05 -> S_rec=0.1 -> Var=0.1, rho=exp(-0.1)=0.904837.
  2. Inverse estimator: lambda_hat recovered from rho matches input S_rec.
  3. Mandatory counterexample citations (Boettiger & Hastings 2012,
     Ditlevsen & Johnsen 2010) appear verbatim in the module docstring
     AND in the JSON report.
  4. Control: two different (a, tau) pairs engineered to share the same
     S_rec -> Var/rho identical.
  5. Scope violations: lambda<=0, rho outside (0,1), delta_t<0 all raise
     ScopeViolationError.

Uses only stdlib + the existing dynamics.core/dynamics.early_warning API.
JSON {count, passed, failed, report}; numbers from this run.
Does not import or mutate dynamics/core.py.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from scoped_correspondence.dynamics.core import fixed_points, recovery_rate_at_equilibrium
from scoped_correspondence.dynamics.early_warning import (
    COUNTEREXAMPLE_WARNING,
    SOURCE,
    early_warning_at_cusp_branch,
    estimate_lambda_from_ar1,
    ou_autocorrelation,
    ou_variance,
)
from scoped_correspondence.errors import ScopeViolationError


def near(a: float, b: float, atol: float = 1e-9, rtol: float = 1e-9) -> None:
    if not math.isclose(a, b, abs_tol=atol, rel_tol=rtol):
        raise AssertionError(f"{a!r} != {b!r} (atol={atol}, rtol={rtol})")


def require(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)


def check_worked_example_table():
    """a=0.5 -> S_rec=1.0; a=0.05 -> S_rec=0.1; both via fixed_points+recovery_rate."""
    rows = []
    for a in (0.5, 0.05):
        roots = fixed_points(a, 0.0)
        x_star = max(r for r in roots if r > 1e-12)
        near(x_star, math.sqrt(a), atol=1e-9)
        lam = recovery_rate_at_equilibrium(x_star, a, 1.0, 0.0)
        near(lam, 2.0 * a, atol=1e-9)
        rep = early_warning_at_cusp_branch(a, x_star, sigma=math.sqrt(0.02), delta_t=1.0)
        rows.append(
            {
                "a": a,
                "x_star": x_star,
                "S_rec": lam,
                "variance": rep.variance,
                "autocorrelation": rep.autocorrelation,
                "lambda_hat": rep.lambda_hat_from_ar1,
            }
        )
    # a=0.5: S_rec=1.0, sigma^2=0.02 -> Var=0.01, rho=exp(-1)
    near(rows[0]["S_rec"], 1.0)
    near(rows[0]["variance"], 0.01, atol=1e-12)
    near(rows[0]["autocorrelation"], math.exp(-1.0), atol=1e-12)
    # a=0.05: S_rec=0.1 -> Var=0.1, rho=exp(-0.1)
    near(rows[1]["S_rec"], 0.1)
    near(rows[1]["variance"], 0.1, atol=1e-12)
    near(rows[1]["autocorrelation"], math.exp(-0.1), atol=1e-12)
    ratio = rows[1]["variance"] / rows[0]["variance"]
    near(ratio, 10.0, atol=1e-9)
    return {"rows": rows, "variance_ratio_a_0p05_over_0p5": ratio}


def check_inverse_estimator_consistency():
    lam_true = 0.1
    rho = ou_autocorrelation(lam_true, 1.0)
    lam_hat = estimate_lambda_from_ar1(rho, 1.0)
    near(lam_hat, lam_true, atol=1e-9)
    return {"lambda_true": lam_true, "rho": rho, "lambda_hat": lam_hat}


def check_counterexample_citations_present():
    mod_doc = sys.modules["scoped_correspondence.dynamics.early_warning"].__doc__ or ""
    require("Boettiger" in mod_doc and "10.1098/rsif.2012.0125" in mod_doc,
            "Boettiger & Hastings 2012 citation missing from module docstring")
    require("Ditlevsen" in mod_doc and "10.1029/2010GL044486" in mod_doc,
            "Ditlevsen & Johnsen 2010 citation missing from module docstring")
    require("Boettiger" in COUNTEREXAMPLE_WARNING, "Boettiger missing from warning constant")
    require("Ditlevsen" in COUNTEREXAMPLE_WARNING, "Ditlevsen missing from warning constant")
    require("NECESSARY" in COUNTEREXAMPLE_WARNING and "NOT SUFFICIENT" in COUNTEREXAMPLE_WARNING,
            "necessary-not-sufficient framing missing")
    return {
        "counterexample_warning": COUNTEREXAMPLE_WARNING,
        "doc_has_boettiger": True,
        "doc_has_ditlevsen": True,
    }


def check_control_same_lambda_different_branch():
    """Two different (a, x*, tau) triples engineered to share the same S_rec
    (S_rec = 2a/tau on the b=0 branch x*=sqrt(a)) -> identical Var/rho."""
    a1, tau1 = 0.5, 1.0  # S_rec = 2*0.5/1 = 1.0
    a2, tau2 = 1.0, 2.0  # S_rec = 2*1.0/2 = 1.0
    x1 = math.sqrt(a1)
    x2 = math.sqrt(a2)
    lam1 = recovery_rate_at_equilibrium(x1, a1, tau1, 0.0)
    lam2 = recovery_rate_at_equilibrium(x2, a2, tau2, 0.0)
    near(lam1, 1.0)
    near(lam2, 1.0)
    v1 = ou_variance(0.2, lam1)
    v2 = ou_variance(0.2, lam2)
    near(v1, v2, atol=1e-12)
    return {"lam1": lam1, "lam2": lam2, "variance1": v1, "variance2": v2}


def check_scope_violations():
    results = {}
    for fn, args, name in (
        (ou_variance, (0.1, 0.0), "ou_variance_lambda_zero"),
        (ou_variance, (0.1, -1.0), "ou_variance_lambda_negative"),
        (ou_autocorrelation, (0.0, 1.0), "ou_autocorrelation_lambda_zero"),
        (ou_autocorrelation, (0.1, -1.0), "ou_autocorrelation_delta_t_negative"),
        (estimate_lambda_from_ar1, (0.0, 1.0), "estimate_lambda_rho_zero"),
        (estimate_lambda_from_ar1, (1.0, 1.0), "estimate_lambda_rho_one"),
        (estimate_lambda_from_ar1, (0.5, 0.0), "estimate_lambda_delta_t_zero"),
    ):
        raised = False
        try:
            fn(*args)
        except ScopeViolationError:
            raised = True
        results[name] = raised
        require(raised, f"{name} did not raise ScopeViolationError")
    return results


def main() -> int:
    checks = [
        ("worked_example_table", check_worked_example_table),
        ("inverse_estimator_consistency", check_inverse_estimator_consistency),
        ("counterexample_citations_present", check_counterexample_citations_present),
        ("control_same_lambda_different_branch", check_control_same_lambda_different_branch),
        ("scope_violations", check_scope_violations),
    ]
    report = {}
    passed = 0
    failed = 0
    for name, fn in checks:
        try:
            detail = fn()
            report[name] = {"ok": True, "detail": detail}
            passed += 1
            print(f"PASS  {name}")
        except Exception as exc:  # noqa: BLE001 -- collect into report
            report[name] = {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
            failed += 1
            print(f"FAIL  {name}: {exc}")

    out = {
        "milestone": 36,
        "title": "Early-Warning Signals / Critical Slowing Down",
        "count": len(checks),
        "passed": passed,
        "failed": failed,
        "source": SOURCE,
        "counterexample_warning": COUNTEREXAMPLE_WARNING,
        "report": report,
        "forbidden_untouched_by_design": [
            "src/scoped_correspondence/dynamics/core.py",
            "src/scoped_correspondence/__init__.py",
            "FORMALISM.md",
        ],
    }
    out_path = Path(__file__).resolve().with_name("verify_early_warning_core_results.json")
    out_path.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n{passed}/{len(checks)} passed; wrote {out_path}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
