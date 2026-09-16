#!/usr/bin/env python3
"""Equivalence checks for Dynamics core (Milestone 2).

Matches legacy verify_formalism.py:
  - p02_cusp_region
  - p01_cusp_branches_and_time

Plus sigmoid / S_rec independence from beta_response (c01-style).
Stdlib + NumPy. JSON {count, passed, failed, report}.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import platform
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from scoped_correspondence import (  # noqa: E402
    CubicNormalForm,
    cusp_field,
    fixed_points,
    recovery_rate_at_equilibrium,
    recovery_rate_from_relaxation,
    sigmoid_response,
)
from scoped_correspondence.legacy import (  # noqa: E402
    cubic_normal_form,
    gamma_domain_style,
    utac_recovery_rate,
    utac_sigmoid,
)


def require(ok, msg):
    if not bool(ok):
        raise AssertionError(msg)


def near(a, b, atol=1e-9, rtol=1e-9):
    if not math.isclose(float(a), float(b), rel_tol=rtol, abs_tol=atol):
        raise AssertionError(f"{a!r} != {b!r}")


def derivative(function, x: float, h: float = 1e-5) -> float:
    return (function(x + h) - function(x - h)) / (2 * h)


def load_formalism_evidence(name: str):
    path = ROOT / "verification" / "verification_results.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    for c in data["checks"]:
        if c.get("name") == name:
            require(c["status"] == "passed", f"legacy {name} not passed")
            return c["evidence"]
    raise AssertionError(f"legacy evidence {name} missing")


def mig_dyn_p02_cusp_region():
    expected = load_formalism_evidence("p02_cusp_region")
    records = []
    cases = ((1.0, 0.0, 3), (1.0, 0.2, 3), (1.0, 1.0, 1), (-1.0, 0.3, 1), (0.0, 0.0, 1), (3.0, 2.0, 2))
    for (a, b, count), exp in zip(cases, expected):
        roots = fixed_points(a, b)
        require(len(roots) == count, f"unexpected root count for a={a},b={b}")
        for x in roots:
            near(cusp_field(x, a, b), 0.0)
        disc = 4 * a**3 - 27 * b**2
        # Exact match to legacy roots (same algorithm)
        require(len(roots) == len(exp["roots"]), "root count vs legacy")
        for got, want in zip(roots, exp["roots"]):
            near(got, want, atol=1e-12)
        near(disc, exp["discriminant"], atol=1e-12)
        records.append({"a": a, "b": b, "discriminant": disc, "roots": roots})
    return {
        "records": records,
        "legacy_id": "p02_cusp_region",
        "legacy_alias": "VER-DYN-p02_cusp_region",
    }


def mig_dyn_p01_cusp_branches_and_time():
    expected = load_formalism_evidence("p01_cusp_branches_and_time")
    records = []
    for a in (0.25, 1.0, 4.0):
        for tau in (0.5, 1.0, 10.0):
            for x in (-math.sqrt(a), 0.0, math.sqrt(a)):
                near(cusp_field(x, a, 0.0, tau), 0.0)
                observed = -derivative(lambda y: cusp_field(y, a, 0.0, tau), x)
                expected_s = -a / tau if x == 0 else 2 * a / tau
                near(observed, expected_s, atol=2e-8)
                api_s = recovery_rate_at_equilibrium(x, a, tau, b=0.0)
                near(api_s, expected_s, atol=1e-12)
                model = CubicNormalForm(a=a, b=0.0, tau=tau)
                near(model.s_rec(x), expected_s, atol=1e-12)
                if x == 0:
                    near(-tau * observed, a, atol=2e-8)
                records.append({"a": a, "tau": tau, "x": x, "recovery": observed})
    require(len(records) == expected["equilibria_checked"], "equilibria_checked count")
    # Exact match on the legacy "examples" slice records[3:6]
    for got, want in zip(records[3:6], expected["examples"]):
        near(got["a"], want["a"])
        near(got["tau"], want["tau"])
        near(got["x"], want["x"])
        near(got["recovery"], want["recovery"], atol=1e-12)
    return {
        "equilibria_checked": len(records),
        "examples": records[3:6],
        "legacy_id": "p01_cusp_branches_and_time",
        "legacy_alias": "VER-DYN-p01_cusp_branches_and_time",
    }


def mig_dyn_sigmoid_srec_independence():
    """beta_response must not be conflatable with S_rec (Review finding A / c01)."""
    beta = 4.0
    p = lambda u: sigmoid_response(u, beta_response=beta, theta_u=0.0, p_max=1.0)
    slope = derivative(p, 0.0)
    near(slope, 1.0, atol=1e-9)  # p_max * beta / 4 = 1
    rates = []
    for tau in (1.0, 10.0):
        s = recovery_rate_from_relaxation(tau)
        # Same sigmoid (fixed beta) admits distinct recovery rates via tau.
        rates.append(s)
        near(s, 1.0 / tau)
        near(utac_recovery_rate(tau), s)
        near(gamma_domain_style(tau), s)
    require(rates[0] != rates[1], "same sigmoid must allow distinct S_rec via tau")
    # Changing beta_response must not change S_rec from tau
    s_ref = recovery_rate_from_relaxation(2.5)
    for beta_alt in (0.5, 4.0, 40.0):
        _ = sigmoid_response(0.0, beta_alt, 0.0, 1.0)
        near(recovery_rate_from_relaxation(2.5), s_ref)
    near(utac_sigmoid(0.0, 4.0, 0.0, 1.0), 0.5)
    near(cubic_normal_form(1.0, 0.0, 1.0).s_rec(0.0), -1.0)
    return {
        "beta": beta,
        "midpoint_slope": slope,
        "recovery_rates": rates,
        "s_rec_independent_of_beta_response": True,
        "formalism_rows": ["beta_response", "S_rec"],
    }


CHECKS = [
    ("MIG-DYN-p02_cusp_region", mig_dyn_p02_cusp_region),
    ("MIG-DYN-p01_cusp_branches_and_time", mig_dyn_p01_cusp_branches_and_time),
    ("MIG-DYN-sigmoid_srec_independence", mig_dyn_sigmoid_srec_independence),
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).with_name("verify_dynamics_core_results.json"),
    )
    args = parser.parse_args()
    results = []
    for name, fn in CHECKS:
        try:
            evidence = fn()
            results.append({"id": name, "status": "passed", "evidence": evidence})
        except Exception as exc:
            results.append(
                {"id": name, "status": "failed", "error": f"{type(exc).__name__}: {exc}"}
            )
    passed = sum(r["status"] == "passed" for r in results)
    failed = [r["id"] for r in results if r["status"] != "passed"]
    report = {
        "milestone": "M2_dynamics_core",
        "kind": "MIG equivalence (legacy verify_formalism vs Dynamics API)",
        "generated_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "python": platform.python_version(),
        "numpy": np.__version__,
        "count": len(results),
        "passed": passed,
        "failed": len(failed),
        "empirical_validation": False,
        "checks": results,
    }
    args.output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    summary = {
        "count": report["count"],
        "passed": report["passed"],
        "failed": failed,
        "report": str(args.output.resolve()),
    }
    print(json.dumps(summary, ensure_ascii=False))
    raise SystemExit(0 if passed == len(results) else 1)


if __name__ == "__main__":
    main()
