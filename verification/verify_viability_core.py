#!/usr/bin/env python3
"""Equivalence checks for Viability core (Milestone 3).

Matches legacy verify_transformations.py:
  - t05_scalar_boundary_and_hitting
  - t09_orthant_boundary_conditions
  - t10_shared_budget_conflict

Also cross-checks t07 via coupled_buffer_field (documented in closure verify).

Stdlib + NumPy. JSON {count, passed, failed, report}; numbers from this run.
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
    coupled_buffer_field,
    has_safe_transfer,
    orthant_action_demand,
    scalar_hitting_time,
    scalar_solution,
    shared_budget_conflict,
    unequal_rates_sum_derivatives,
)
from scoped_correspondence.legacy import (  # noqa: E402
    buffer_field,
    budget_conflict,
    safe_transfer_scalar,
)


def require(ok, msg):
    if not bool(ok):
        raise AssertionError(msg)


def near(a, b, atol=1e-10, rtol=1e-9):
    if not np.allclose(a, b, atol=atol, rtol=rtol):
        raise AssertionError(f"{a!r} != {b!r}")


def diff(f, x, h=1e-5):
    return (f(x + h) - f(x - h)) / (2 * h)


def load_transform_evidence(name: str):
    path = ROOT / "verification" / "transformation_results.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    for c in data["results"]:
        if c.get("id") == name:
            require(c["status"] == "passed", f"legacy {name} not passed")
            return c["evidence"]
    raise AssertionError(f"legacy evidence {name} missing")


def mig_via_t05_scalar_boundary_and_hitting():
    expected = load_transform_evidence("t05_scalar_boundary_and_hitting")
    r, eq, b, U, W, initial = 1.3, 0.8, 0.2, 0.1, 1.5, 1.4
    hit = scalar_hitting_time(r, eq, b, U, W, initial)
    near(scalar_solution(hit, r, eq, U, W, initial), b)
    require(
        scalar_solution(hit - 0.01, r, eq, U, W, initial) > b
        and scalar_solution(hit + 0.01, r, eq, U, W, initial) < b,
        "first crossing",
    )
    for t in np.linspace(0, hit + 0.1, 23):
        z = scalar_solution(t, r, eq, U, W, initial)
        near(diff(lambda s: scalar_solution(s, r, eq, U, W, initial), t), -r * (z - eq) + U - W)

    # Safe transfer: W too large -> not robustly invariant
    report_bad = has_safe_transfer(r, eq, b, U, W, z0=initial)
    require(not report_bad["ok"], "expected failed robust invariance")
    near(report_bad["hitting_time"], hit)
    # Critical load: W_crit = r(eq-b)+U
    critical = r * (eq - b) + U
    near(report_bad["W_crit"], critical)
    for offset in [-0.1, 0.0, 0.1]:
        near(-r * (b - eq) + U - (critical + offset), -offset)

    # Original worked-example numbers: r=1, zeq=1, b=0, U=0, W=1.5, z0=1 -> ln3
    original = math.log(3)
    near(scalar_hitting_time(1.0, 1.0, 0.0, 0.0, 1.5, 1.0), original)
    report_orig = safe_transfer_scalar(1.0, 1.0, 0.0, 0.0, 1.5, z0=1.0)
    require(not report_orig["ok"], "original case not invariant")
    # Feasible case: W=0.5 with U=0 stays in K
    report_ok = has_safe_transfer(1.0, 1.0, 0.0, 0.0, 0.5)
    require(report_ok["ok"], "W=0.5 should be robustly invariant")
    require(report_ok["executability"], "exec")
    require(report_ok["successor_compatibility"], "succ")
    require(report_ok["safe_representation"], "safe repr")

    evidence = {
        "general_hitting_time": hit,
        "original_hitting_time": original,
        "legacy_id": "t05_scalar_boundary_and_hitting",
        "legacy_alias": "VER-VIA-t05_scalar_boundary_and_hitting",
        "safe_transfer_ok_W0.5": report_ok["ok"],
        "safe_transfer_ok_W1.5": report_bad["ok"],
    }
    near(evidence["general_hitting_time"], expected["general_hitting_time"], atol=1e-15)
    near(evidence["original_hitting_time"], expected["original_hitting_time"], atol=1e-15)
    return evidence


def mig_via_t09_orthant_boundary_conditions():
    expected = load_transform_evidence("t09_orthant_boundary_conditions")
    rng = np.random.default_rng(3209)
    minima, conflicts = [], 0
    for _ in range(100):
        r = rng.uniform(0.1, 2, 2)
        e, b = rng.normal(size=(2, 2))
        W, k = rng.uniform(0, 2, 2), float(rng.uniform(0, 2))
        a = orthant_action_demand(r, e, b, W, k)
        for i in [0, 1]:
            for surplus in [0, 0.1, 2]:
                x = b.copy()
                x[1 - i] += surplus
                val = float(coupled_buffer_field(x, r, e, a, W, k)[i])
                minima.append(val)
                require(val >= -1e-12, "boundary points inward under common constant action")
        if a.sum() > 0.01:
            U = a.sum() - 0.01
            corner_without_action = coupled_buffer_field(b, r, e, [0, 0], W, k)
            required_total = float(np.maximum(0, -corner_without_action).sum())
            require(required_total > U, "insufficient common budget")
            conflicts += 1
            # Package conflict helper agrees
            report = shared_budget_conflict(r, e, W, k, U, b=b)
            require(report["conflict"], "shared_budget_conflict should flag")
    evidence = {
        "parameter_sets": 100,
        "boundary_evaluations": len(minima),
        "min_boundary_derivative": min(minima),
        "infeasible_budget_cases": conflicts,
        "legacy_id": "t09_orthant_boundary_conditions",
        "legacy_alias": "VER-VIA-t09_orthant_boundary_conditions",
    }
    require(evidence["parameter_sets"] == expected["parameter_sets"], "parameter_sets")
    require(
        evidence["boundary_evaluations"] == expected["boundary_evaluations"],
        "boundary_evaluations",
    )
    near(
        evidence["min_boundary_derivative"],
        expected["min_boundary_derivative"],
        atol=1e-15,
    )
    require(
        evidence["infeasible_budget_cases"] == expected["infeasible_budget_cases"],
        "infeasible_budget_cases",
    )
    return evidence


def mig_via_t10_shared_budget_conflict():
    expected = load_transform_evidence("t10_shared_budget_conflict")
    near(0.2 + 0.75 - 0.7, 0.25)
    report = shared_budget_conflict(
        r=[1, 1], e=[0.2, 0.2], W=[0.7, 0.7], k=0.5, U=0.75, b=[0, 0]
    )
    near(report["standalone_margin"], 0.25)
    near(report["required_joint_budget"], 1.0)
    near(report["available_budget"], 0.75)
    require(report["conflict"], "must conflict")
    corner = coupled_buffer_field(
        [0, 0], [1, 1], [0.2, 0.2], [0.375, 0.375], [0.7, 0.7], 0.5
    )
    near(corner, [-0.125, -0.125])
    near(report["corner_with_equal_split"], [-0.125, -0.125])
    near(
        coupled_buffer_field([0, 0], [1, 1], [0.2, 0.2], [0.5, 0.5], [0.7, 0.7], 0.5),
        [0, 0],
    )
    for k in [0, 0.5, 10, 1000]:
        near(
            buffer_field([0, 0], [1, 1], [0.2, 0.2], [0.375, 0.375], [0.7, 0.7], k),
            corner,
        )
    # Sufficient joint budget removes conflict
    ok_budget = budget_conflict(
        r=[1, 1], e=[0.2, 0.2], W=[0.7, 0.7], k=0.5, U=1.0, b=[0, 0]
    )
    require(not ok_budget["conflict"], "U=1 should suffice")
    evidence = {
        "standalone_margin": 0.25,
        "required_joint_budget": 1,
        "available_budget": 0.75,
        "legacy_id": "t10_shared_budget_conflict",
        "legacy_alias": "VER-VIA-t10_shared_budget_conflict",
        "conflict": True,
    }
    near(evidence["standalone_margin"], expected["standalone_margin"])
    require(
        evidence["required_joint_budget"] == expected["required_joint_budget"],
        "required",
    )
    near(evidence["available_budget"], expected["available_budget"])
    return evidence


def mig_via_t07_crosscheck_unequal_rates():
    """Optional cross-check shared with closure verify (same legacy id)."""
    expected = load_transform_evidence("t07_unequal_rates_break_closure")
    out = unequal_rates_sum_derivatives()
    require(not out["closed_in_sum"], "must break sum closure")
    evidence = {
        "same_sum": out["same_sum"],
        "two_derivatives": out["two_derivatives"],
        "legacy_id": "t07_unequal_rates_break_closure",
        "legacy_alias": "VER-VIA-t07_unequal_rates_break_closure",
    }
    require(evidence["same_sum"] == expected["same_sum"], "same_sum")
    require(evidence["two_derivatives"] == expected["two_derivatives"], "derivatives")
    return evidence


CHECKS = [
    ("MIG-VIA-t05_scalar_boundary_and_hitting", mig_via_t05_scalar_boundary_and_hitting),
    ("MIG-VIA-t09_orthant_boundary_conditions", mig_via_t09_orthant_boundary_conditions),
    ("MIG-VIA-t10_shared_budget_conflict", mig_via_t10_shared_budget_conflict),
    ("MIG-VIA-t07_unequal_rates_crosscheck", mig_via_t07_crosscheck_unequal_rates),
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).with_name("verify_viability_core_results.json"),
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
        "milestone": "M3_viability_core",
        "kind": "MIG equivalence (legacy transformations vs Viability API)",
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
