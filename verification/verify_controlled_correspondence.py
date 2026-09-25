#!/usr/bin/env python3
"""Controlled Markov correspondence (INTEGRATED_EXTENSION_ROADMAP.md Paket C2).

Checks:

  1. Hand-verified positive control case: 4 micro states, 2 classes, two
     declared micro actions (passive, intervention) with heterogeneous
     within-class micro kernels both give EXACT correspondence, recovering
     Q_passive=[[0.7,0.3],[0.4,0.6]] and Q_intervention=[[0.8,0.2],[0.1,0.9]]
     to numerical precision.
  2. Negative control case: replacing the intervention's first two rows
     breaks exactness for THAT action only (passive stays exact -- no
     averaging that hides one failing action); the detected defect and the
     best single-row minimax replacement match the hand-derived values
     (defect 0.2, minimax row value 0.2, max error 0.1).
  3. ``is_union_of_classes``: a micro event that is exactly one or both whole
     classes is valid; one that cuts across a class is not.
  4. ``check_cost_consistency`` detects both an exact match and a genuine
     mismatch, and treats a missing macro counterpart as a violation (never
     silently skipped).
  5. ScopeViolationError guards (non-partition C, non-stochastic P,
     mismatched action sets).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from scoped_correspondence.errors import ScopeViolationError  # noqa: E402
from scoped_correspondence.correspondence.controlled_markov import (  # noqa: E402
    partition_indicator,
    check_lumpability,
    check_controlled_correspondence,
    best_minimax_macro_row,
    is_union_of_classes,
    check_cost_consistency,
)


def require(ok, msg):
    if not bool(ok):
        raise AssertionError(msg)


C, CLASSES = partition_indicator([0, 0, 1, 1])

P_PASSIVE = np.array([
    [0.5, 0.2, 0.2, 0.1],
    [0.1, 0.6, 0.05, 0.25],
    [0.3, 0.1, 0.4, 0.2],
    [0.15, 0.25, 0.3, 0.3],
])
P_INTERVENTION = np.array([
    [0.5, 0.3, 0.1, 0.1],
    [0.2, 0.6, 0.15, 0.05],
    [0.05, 0.05, 0.7, 0.2],
    [0.02, 0.08, 0.3, 0.6],
])
Q_PASSIVE = np.array([[0.7, 0.3], [0.4, 0.6]])
Q_INTERVENTION = np.array([[0.8, 0.2], [0.1, 0.9]])


def check_positive_case_exact():
    exact_p, defect_p, worst_p, Qest_p = check_lumpability(P_PASSIVE, C)
    exact_i, defect_i, worst_i, Qest_i = check_lumpability(P_INTERVENTION, C)
    require(exact_p, f"passive should be exactly lumpable, defect={defect_p!r}")
    require(exact_i, f"intervention should be exactly lumpable, defect={defect_i!r}")
    require(np.allclose(Qest_p, Q_PASSIVE, atol=1e-9), f"Q_passive mismatch: {Qest_p!r}")
    require(np.allclose(Qest_i, Q_INTERVENTION, atol=1e-9), f"Q_intervention mismatch: {Qest_i!r}")

    omega = {"passive": "passive", "intervention": "intervention"}
    reports = check_controlled_correspondence({"passive": P_PASSIVE, "intervention": P_INTERVENTION}, C, omega)
    require(reports["passive"].exact and reports["intervention"].exact, "both actions should report exact")
    return {"defect_p": defect_p, "defect_i": defect_i, "Q_passive": Qest_p.tolist(), "Q_intervention": Qest_i.tolist()}


def check_negative_case_detects_violation():
    P_bad = P_INTERVENTION.copy()
    P_bad[0] = [0.9, 0.0, 0.1, 0.0]
    P_bad[1] = [0.0, 0.7, 0.0, 0.3]

    exact, defect, worst, _ = check_lumpability(P_bad, C)
    require(not exact, "modified intervention kernel must be detected as non-lumpable")
    require(abs(defect - 0.2) < 1e-9, f"defect should be 0.2 (0.3-0.1 spread in class-1 column), got {defect!r}")
    require(worst is not None and worst.macro_class == 0, "violation should be attributed to macro class 0")

    best_row, max_err = best_minimax_macro_row(P_bad, C, macro_class=0)
    require(abs(best_row[1] - 0.2) < 1e-9, f"minimax macro-class-1 probability should be 0.2, got {best_row[1]!r}")
    require(abs(max_err - 0.1) < 1e-9, f"minimax max error should be 0.1, got {max_err!r}")

    omega = {"passive": "passive", "intervention": "intervention"}
    reports = check_controlled_correspondence({"passive": P_PASSIVE, "intervention": P_bad}, C, omega)
    require(reports["passive"].exact, "passive action must STILL report exact -- no averaging across actions")
    require(not reports["intervention"].exact, "intervention action must report the violation")
    require(abs(reports["intervention"].max_defect - 0.2) < 1e-9, "per-action report must carry the correct defect")
    return {"defect": defect, "best_row": best_row.tolist(), "max_err": max_err}


def check_is_union_of_classes():
    require(is_union_of_classes([0, 1], C), "class 0 alone should be a valid macro event")
    require(is_union_of_classes([2, 3], C), "class 1 alone should be a valid macro event")
    require(is_union_of_classes([0, 1, 2, 3], C), "both classes together should be a valid macro event")
    require(not is_union_of_classes([0, 2], C), "{0,2} cuts across both classes -- must NOT be a valid macro event")
    require(not is_union_of_classes([0], C), "a single state from a 2-state class must NOT be a valid macro event")
    return {"ok": True}


def check_cost_consistency_detects_mismatch():
    omega = {"passive": "passive", "intervention": "intervention"}
    cost_macro = {(0, "passive"): 1.0, (1, "passive"): 2.0, (0, "intervention"): 1.5, (1, "intervention"): 2.5}
    cost_micro_ok = {
        (0, "passive"): 1.0, (1, "passive"): 1.0, (2, "passive"): 2.0, (3, "passive"): 2.0,
        (0, "intervention"): 1.5, (2, "intervention"): 2.5,
    }
    violations_ok = check_cost_consistency(cost_micro_ok, cost_macro, C, omega)
    require(len(violations_ok) == 0, f"consistent costs should have no violations, got {violations_ok!r}")

    cost_micro_bad = dict(cost_micro_ok)
    cost_micro_bad[(1, "passive")] = 999.0  # inconsistent with cost_macro[(0,"passive")]=1.0
    violations_bad = check_cost_consistency(cost_micro_bad, cost_macro, C, omega)
    require((1, "passive") in violations_bad, "the deliberately mismatched entry must be reported")
    require(violations_bad[(1, "passive")] > 900.0, "reported error magnitude should reflect the actual mismatch")

    cost_macro_incomplete = {(0, "passive"): 1.0, (1, "passive"): 2.0, (0, "intervention"): 1.5}  # (1,"intervention") missing
    violations_missing = check_cost_consistency(cost_micro_ok, cost_macro_incomplete, C, omega)
    require((2, "intervention") in violations_missing and violations_missing[(2, "intervention")] == float("inf"),
            "a genuinely missing macro counterpart must be reported as an infinite-error violation, never silently skipped")
    return {"violations_ok": violations_ok, "violations_bad": {str(k): v for k, v in violations_bad.items()}}


def check_scope_violation_guards():
    bad_C = np.array([[1, 0], [0, 0], [0, 1], [0, 1]])  # row 1 sums to 0, not a valid partition row
    try:
        check_lumpability(P_PASSIVE, bad_C)
        raise AssertionError("non-partition C should raise ScopeViolationError")
    except ScopeViolationError:
        pass

    bad_P = P_PASSIVE.copy()
    bad_P[0, 0] += 0.5  # rows no longer sum to 1
    try:
        check_lumpability(bad_P, C)
        raise AssertionError("non-stochastic P should raise ScopeViolationError")
    except ScopeViolationError:
        pass

    try:
        check_controlled_correspondence({"passive": P_PASSIVE}, C, {"passive": "passive", "intervention": "intervention"})
        raise AssertionError("mismatched action sets should raise ScopeViolationError")
    except ScopeViolationError:
        pass
    return {"raised": 3}


CHECKS = [
    ("positive_case_exact", check_positive_case_exact),
    ("negative_case_detects_violation", check_negative_case_detects_violation),
    ("is_union_of_classes", check_is_union_of_classes),
    ("cost_consistency_detects_mismatch", check_cost_consistency_detects_mismatch),
    ("scope_violation_guards", check_scope_violation_guards),
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json-out", type=Path, default=Path(__file__).with_name("verify_controlled_correspondence_results.json"))
    args = parser.parse_args()

    report = {
        "package": "INTEGRATED_EXTENSION_ROADMAP.md Paket C2 (controlled Markov correspondence)",
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
