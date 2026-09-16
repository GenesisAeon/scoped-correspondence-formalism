#!/usr/bin/env python3
"""Hand-checkable verification for Membership core (Milestone 4).

Checks (all numbers from this script run):
  1. Double-count naive vs correct under overlapping membership
  2. T5 nonempty joint control set (interval intersection)
  3. T5 empty joint control set (explicit conflict)
  4. Cross-check t10 shared_budget_conflict via MembershipMatrix

Stdlib + NumPy. JSON {count, passed, failed, report}; numbers from this run.
No legacy MIG evidence file for M_eα / T5 (first dedicated checks).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import platform
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from scoped_correspondence import (  # noqa: E402
    MembershipMatrix,
    ScopeViolationError,
    double_count_stocks,
    joint_control_set,
    shared_budget_conflict,
    t10_via_membership,
    view,
)
from scoped_correspondence.closure import partition_matrix  # noqa: E402


def require(ok, msg):
    if not bool(ok):
        raise AssertionError(msg)


def near(a, b, atol=1e-10, rtol=1e-9):
    if not np.allclose(a, b, atol=atol, rtol=rtol):
        raise AssertionError(f"{a!r} != {b!r}")


def check_double_count_naive_vs_correct():
    """Entity e0 in two systems; x=[10,20,30] → naive 70, correct 60, diff 10."""
    M = MembershipMatrix(
        [
            [1, 1],  # e0 in α0 and α1
            [1, 0],  # e1 only α0
            [0, 1],  # e2 only α1
        ],
        entity_names=("e0", "e1", "e2"),
        system_names=("alpha0", "alpha1"),
    )
    x = np.array([10.0, 20.0, 30.0])
    report = double_count_stocks(M, x)
    # Hand check: M.T @ x = [10+20, 10+30] = [30, 40]; sum=70; sum(x)=60; diff=10
    near(report["per_system_naive"], [30.0, 40.0])
    near(report["total_naive"], 70.0)
    near(report["total_correct"], 60.0)
    near(report["double_count_difference"], 10.0)
    near(report["double_count_mass"], 10.0)
    require(report["double_count_difference"] == 10.0, "explicit difference must be 10")

    # Binary guard: weighted entry rejected
    try:
        MembershipMatrix([[0.5, 1.0]])
        raise AssertionError("weighted M should raise ScopeViolationError")
    except ScopeViolationError:
        pass

    # Separate type from closure partition C — no cast / shared identity
    C, _lift = partition_matrix([0, 0, 1])
    require(type(M) is not type(C), "MembershipMatrix must stay separate from C ndarray")
    require(not isinstance(M, type(C)), "no shared base with ndarray partition")

    # view(...) call mechanism
    y = view(lambda z, c, t: z[0] + (c or 0) + (t or 0), z=[1.0, 2.0], c=3.0, t=4.0, alpha=0)
    near(y, 8.0)

    return {
        "x": report["x"],
        "M": report["M"],
        "per_system_naive": report["per_system_naive"],
        "total_naive": report["total_naive"],
        "total_correct": report["total_correct"],
        "double_count_difference": report["double_count_difference"],
        "view_y": float(y),
        "source": "context_transformations.md sections 1-2",
    }


def check_t5_nonempty():
    """Two systems, overlapping membership; intervals intersect to [0.2, 0.8]."""
    M = MembershipMatrix(
        [
            [1, 1],  # shared entity
            [1, 0],
            [0, 1],
        ],
        entity_names=("e0", "e1", "e2"),
        system_names=("alpha0", "alpha1"),
    )
    require(M.n_systems == 2, "need two systems")
    require(int(M.matrix[0].sum()) == 2, "overlapping membership on e0")

    U_physical = (0.0, 1.0)
    U_alphas = [(0.0, 0.8), (0.2, 1.0)]
    # Hand: max(0,0,0.2)=0.2; min(1,0.8,1)=0.8 → [0.2, 0.8]
    report = joint_control_set(U_physical, U_alphas)
    near(report["U_joint"], [0.2, 0.8])
    require(not report["conflict"], "nonempty must not conflict")
    require(not report["empty"], "nonempty")
    return {
        "M": M.matrix.tolist(),
        "U_physical": list(U_physical),
        "U_alphas": [list(u) for u in U_alphas],
        "U_joint": report["U_joint"],
        "conflict": report["conflict"],
        "source": "context_transformations.md section 6 T5",
    }


def check_t5_empty_conflict():
    """Disjoint intervals → empty U_joint, conflict=True."""
    U_physical = (0.0, 1.0)
    U_alphas = [(0.0, 0.3), (0.5, 1.0)]
    # Hand: lo=max(0,0,0.5)=0.5; hi=min(1,0.3,1)=0.3 → empty
    report = joint_control_set(U_physical, U_alphas)
    require(report["U_joint"] is None, "empty intersection has U_joint=None")
    require(report["empty"], "empty")
    require(report["conflict"], "explicit conflict")
    return {
        "U_physical": list(U_physical),
        "U_alphas": [list(u) for u in U_alphas],
        "U_joint": report["U_joint"],
        "conflict": report["conflict"],
        "source": "context_transformations.md section 6 T5 empty = Regel-/Ressourcenwiderspruch",
    }


def check_t10_membership_crosscheck():
    """MembershipMatrix (2 entities, one shared system) matches shared_budget_conflict."""
    via_m = t10_via_membership()
    via_v = shared_budget_conflict(
        r=[1, 1], e=[0.2, 0.2], W=[0.7, 0.7], k=0.5, U=0.75, b=[0, 0]
    )
    near(via_m["a"], [0.5, 0.5])
    near(via_m["required_joint_budget"], 1.0)
    near(via_m["available_budget"], 0.75)
    require(via_m["conflict"] is True, "must conflict")
    near(via_m["a"], via_v["a"])
    near(via_m["required_joint_budget"], via_v["required_joint_budget"])
    near(via_m["available_budget"], via_v["available_budget"])
    near(via_m["standalone_margin"], via_v["standalone_margin"])
    require(via_m["conflict"] == via_v["conflict"], "conflict flags must match")
    near(via_m["M"], [[1.0], [1.0]])
    return {
        "M": via_m["M"],
        "a": via_m["a"],
        "required_joint_budget": via_m["required_joint_budget"],
        "available_budget": via_m["available_budget"],
        "standalone_margin": via_m["standalone_margin"],
        "conflict": via_m["conflict"],
        "matches_viability_shared_budget_conflict": True,
        "legacy_id": "t10_shared_budget_conflict",
        "source": "membership t10_via_membership ↔ viability.shared_budget_conflict",
    }


CHECKS = [
    ("MIG-MEM-double_count_naive_vs_correct", check_double_count_naive_vs_correct),
    ("MIG-MEM-t5_nonempty", check_t5_nonempty),
    ("MIG-MEM-t5_empty_conflict", check_t5_empty_conflict),
    ("MIG-MEM-t10_membership_crosscheck", check_t10_membership_crosscheck),
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).with_name("verify_membership_core_results.json"),
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
        "milestone": "M4_membership_core",
        "kind": "Hand-checkable membership / T5 checks + t10 viability cross-check",
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
