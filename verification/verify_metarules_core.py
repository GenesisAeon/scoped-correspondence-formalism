#!/usr/bin/env python3
"""Hand-checkable verification for Metarules core (Milestone 9).

Checks (all numbers from this script run):
  1. Priority on empty T5 cut → nonempty + names dropped requirement
  2. Unobserved-m Case A: closure_error == 0, is_exact_closure True
  3. Unobserved-m Case B: closure_error > 0 with concrete number
  4. Nonempty raw cut → priority identical to joint_control_set
  (+ MetaRuleUpdate named variants)

Stdlib + NumPy. JSON {count, passed, failed, report}; numbers from this run.
Calls real membership.joint_control_set and closure.* APIs (wrap/call only).
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

from scoped_correspondence.membership import joint_control_set  # noqa: E402
from scoped_correspondence.metarules import (  # noqa: E402
    DESCRIPTIVE_ONLY,
    ENFORCED_RULE,
    MetaRuleUpdate,
    priority_joint_control_set,
    unobserved_metarule_breaks_closure,
)


def require(ok, msg):
    if not bool(ok):
        raise AssertionError(msg)


def near(a, b, atol=1e-10, rtol=1e-9):
    if not np.allclose(a, b, atol=atol, rtol=rtol):
        raise AssertionError(f"{a!r} != {b!r}")


def check_meta_rule_update_variants():
    """Discrete H wraps; both named variants distinguishable in return."""

    def H(m, z, c, u, t):
        return {"priority": "alpha0", "step": (m or 0) + 1, "z": z}

    desc = MetaRuleUpdate.apply(
        H, m=0, z=1, c=None, u=None, t=0, variant=DESCRIPTIVE_ONLY
    )
    enf = MetaRuleUpdate.apply(
        H, m=0, z=1, c=None, u=None, t=0, variant=ENFORCED_RULE
    )
    rd, re = desc.as_report(), enf.as_report()
    require(rd["variant"] == DESCRIPTIVE_ONLY, "descriptive variant name")
    require(re["variant"] == ENFORCED_RULE, "enforced variant name")
    require(rd["affects_observation_first"] is True, "descriptive → π first")
    require(
        rd["can_change_interventions_and_trajectory"] is False,
        "descriptive does not change interventions",
    )
    require(re["affects_observation_first"] is False, "enforced not π-only")
    require(
        re["can_change_interventions_and_trajectory"] is True,
        "enforced can change interventions/trajectory",
    )
    require(
        DESCRIPTIVE_ONLY in rd["named_variants"]
        and ENFORCED_RULE in rd["named_variants"],
        "both named variants documented in return",
    )
    require(desc.m_next["step"] == 1, "H applied")
    return {
        "descriptive_only": {
            "variant": rd["variant"],
            "affects_observation_first": rd["affects_observation_first"],
            "can_change_interventions_and_trajectory": rd[
                "can_change_interventions_and_trajectory"
            ],
        },
        "enforced_rule": {
            "variant": re["variant"],
            "affects_observation_first": re["affects_observation_first"],
            "can_change_interventions_and_trajectory": re[
                "can_change_interventions_and_trajectory"
            ],
        },
        "named_variants": list(rd["named_variants"].keys()),
        "source": "context_transformations.md §6 MetaRuleUpdate variants",
    }


def check_priority_empty_cut_yields_nonempty():
    """Same intervals as verify_membership_core t5_empty_conflict.

    Raw cut empty; priority drops alpha[0]=(0,0.3) →
    U_physical ∩ (0.5,1.0) = (0.5, 1.0) nonempty.
    """
    U_physical = (0.0, 1.0)
    U_alphas = [(0.0, 0.3), (0.5, 1.0)]
    raw = joint_control_set(U_physical, U_alphas)
    require(raw["conflict"] is True, "raw must conflict (t5_empty_conflict)")
    require(raw["U_joint"] is None, "raw U_joint None")

    m = {
        "drop_alpha_index": 0,
        "drop_alpha_name": "alpha0_low",
    }
    report = priority_joint_control_set(
        U_physical,
        U_alphas,
        m,
        alpha_names=("alpha0_low", "alpha1_high"),
    )
    require(report["priority_applied"] is True, "priority must apply")
    require(report["raw"]["conflict"] is True, "raw conflict preserved")
    near(report["U_joint"], [0.5, 1.0])
    require(not report["empty"], "after priority nonempty")
    require(not report["conflict"], "after priority no conflict")
    require(
        report["dropped_requirement_name"] == "alpha0_low",
        "must name dropped requirement",
    )
    require(
        report["dropped_requirement_index"] == 0,
        "must record dropped index",
    )
    require(
        report["both_requirements_satisfied_simultaneously"] is False,
        "§6: both NOT satisfied at once",
    )
    require(
        "NOT satisfied at once" in report["note"]
        or "not satisfied at once" in report["note"].lower(),
        "note must state both not satisfied at once",
    )
    return {
        "U_physical": list(U_physical),
        "U_alphas": [list(u) for u in U_alphas],
        "raw_conflict": raw["conflict"],
        "raw_U_joint": raw["U_joint"],
        "U_joint_after_priority": report["U_joint"],
        "dropped_requirement_index": report["dropped_requirement_index"],
        "dropped_requirement_name": report["dropped_requirement_name"],
        "both_requirements_satisfied_simultaneously": report[
            "both_requirements_satisfied_simultaneously"
        ],
        "legacy_parallel": "MIG-MEM-t5_empty_conflict",
        "source": "context_transformations.md §6 T5 priority",
    }


def check_priority_nonempty_identical_to_joint():
    """Nonempty raw cut → priority identical to joint_control_set."""
    U_physical = (0.0, 1.0)
    U_alphas = [(0.0, 0.8), (0.2, 1.0)]
    # Hand: [0.2, 0.8] nonempty (same as MIG-MEM-t5_nonempty)
    raw = joint_control_set(U_physical, U_alphas)
    require(not raw["conflict"], "raw nonempty")
    near(raw["U_joint"], [0.2, 0.8])

    # m would drop alpha 0 if conflict — but conflict is False, so unused
    report = priority_joint_control_set(
        U_physical,
        U_alphas,
        m={"drop_alpha_index": 0},
        alpha_names=("alpha0", "alpha1"),
    )
    require(report["priority_applied"] is False, "no priority on nonempty")
    require(report["dropped_requirement"] is None, "nothing dropped")
    near(report["U_joint"], raw["U_joint"])
    require(
        report["U_joint"] == raw["U_joint"],
        "U_joint must be identical to joint_control_set",
    )
    require(
        report["both_requirements_satisfied_simultaneously"] is True,
        "both satisfied when raw nonempty",
    )
    return {
        "U_physical": list(U_physical),
        "U_alphas": [list(u) for u in U_alphas],
        "raw_U_joint": raw["U_joint"],
        "priority_U_joint": report["U_joint"],
        "identical_to_joint_control_set": report["U_joint"] == raw["U_joint"],
        "priority_applied": report["priority_applied"],
        "source": "context_transformations.md §6 T5 nonempty identity",
    }


def check_unobserved_case_A_exact():
    """Case A: m=z → is_exact_closure True, closure_error == 0."""
    full = unobserved_metarule_breaks_closure()
    A = full["case_A"]
    require(A["is_exact_closure"] is True, "Case A must be exact")
    near(A["closure_error"], 0.0, atol=1e-15)
    require(A["closure_error"] == 0.0, "Case A error must be exactly 0")
    return {
        "is_exact_closure": A["is_exact_closure"],
        "closure_error": A["closure_error"],
        "Q": A["Q"],
        "frame": A["frame"],
        "apis_called": full["apis_called"],
        "source": "context_transformations.md §6 + closure e04-style APIs",
    }


def check_unobserved_case_B_breaks():
    """Case B: independent fair-coin m → not exact, error > 0 with number."""
    full = unobserved_metarule_breaks_closure()
    B = full["case_B"]
    require(B["is_exact_closure"] is False, "Case B must not be exact")
    require(B["closure_error"] > 0, "Case B error must be > 0")
    # Hand: same-z rows disagree completely on next macro → delta_cl = 0.5
    near(B["closure_error"], 0.5, atol=1e-15)
    return {
        "is_exact_closure": B["is_exact_closure"],
        "closure_error": B["closure_error"],
        "Q": B["Q"],
        "frame": B["frame"],
        "concrete_error_number": B["closure_error"],
        "source": "context_transformations.md §6 + closure e05-style APIs",
    }


CHECKS = [
    ("MIG-MR-meta_rule_update_variants", check_meta_rule_update_variants),
    ("MIG-MR-priority_empty_cut_nonempty", check_priority_empty_cut_yields_nonempty),
    ("MIG-MR-priority_nonempty_identical", check_priority_nonempty_identical_to_joint),
    ("MIG-MR-unobserved_case_A_exact", check_unobserved_case_A_exact),
    ("MIG-MR-unobserved_case_B_breaks", check_unobserved_case_B_breaks),
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).with_name("verify_metarules_core_results.json"),
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
        "milestone": "M9_metarules_core",
        "kind": (
            "Hand-checkable metarules checks: MetaRuleUpdate variants, "
            "priority T5 wrap, unobserved-m A/B closure"
        ),
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
