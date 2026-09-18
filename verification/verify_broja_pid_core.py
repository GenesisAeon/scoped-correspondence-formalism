#!/usr/bin/env python3
"""Hand-checkable verification for BROJA bivariate PID (Milestone 17).

Checks:
  1. TWO_BIT_COPY: BROJA Red≈0, Unq≈1 each, Syn≈0; side-by-side WB / RB0 / BROJA
  2. XOR: Red=0, Unq=0, Syn=1
  3. Redundant copy: Red=1, Unq=0, Syn=0
  4. Multi-start convergence (≥3 starts agree); DOI; PID sum; core.py not mutated
     (imports two_bit_copy_joint / pid_atoms_williams_beer / rb0_blackwell only)

JSON {count, passed, failed, report}; numbers from this run.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import platform
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import numpy as np  # noqa: E402

from scoped_correspondence.errors import ScopeViolationError  # noqa: E402
from scoped_correspondence.information_decomposition.broja import (  # noqa: E402
    DOI,
    SOURCE,
    BivariatePIDReport,
    broja_pid_bivariate,
    two_bit_copy_broja_report,
)
from scoped_correspondence.information_decomposition.core import (  # noqa: E402
    pid_atoms_williams_beer,
    rb0_blackwell,
    two_bit_copy_joint,
)


def require(ok, msg):
    if not bool(ok):
        raise AssertionError(msg)


def near(a, b, atol=1e-4, rtol=1e-6):
    if not math.isclose(float(a), float(b), abs_tol=atol, rel_tol=rtol):
        raise AssertionError(f"{a!r} != {b!r} (atol={atol})")


def check_two_bit_copy():
    """BROJA on TWO_BIT_COPY: Red≈0, Unq≈1 each, Syn≈0; side-by-side."""
    side = two_bit_copy_broja_report(n_starts=5, tol=1e-4)
    wb = side["williams_beer"]
    rb0 = side["blackwell_rb0"]["RB0"]
    b = side["broja"]

    # Williams-Beer known (misleading) atoms
    near(wb["Red"], 1.0)
    near(wb["Unq1"], 0.0)
    near(wb["Unq2"], 0.0)
    near(wb["Syn"], 1.0)
    near(wb["I_joint"], 2.0)

    # Blackwell RB(0)
    near(rb0, 0.0)

    # BROJA expected
    near(b["redundancy"], 0.0)
    near(b["unique_source_1"], 1.0)
    near(b["unique_source_2"], 1.0)
    near(b["synergy"], 0.0)
    near(b["I_joint"], 2.0)
    require(b["method"] == "broja", b["method"])
    require(DOI in b["doi"] or b["doi"] == DOI, b["doi"])
    require("10.3390/e16042161" in SOURCE, SOURCE)

    # Direct call path + PID sum
    j = two_bit_copy_joint()
    report = broja_pid_bivariate(j)
    require(isinstance(report, BivariatePIDReport), "type")
    report.assert_pid_sum(atol=1e-4)
    near(report.redundancy, 0.0)
    near(report.unique_source_1, 1.0)
    near(report.unique_source_2, 1.0)
    near(report.synergy, 0.0)

    # Cross-check core helpers still callable (core.py untouched contract)
    atoms = pid_atoms_williams_beer(j)
    near(atoms["Red"], 1.0)
    near(rb0_blackwell(j), 0.0)

    # Multi-start agreement
    require(len(report.unq1_optima) >= 3, "≥3 unq1 starts")
    require(len(report.unq2_optima) >= 3, "≥3 unq2 starts")
    require(report.converged is True, "converged")

    return {
        "williams_beer": wb,
        "blackwell_rb0": rb0,
        "broja": {
            "redundancy": report.redundancy,
            "unique_source_1": report.unique_source_1,
            "unique_source_2": report.unique_source_2,
            "synergy": report.synergy,
            "I_joint": report.I_joint,
            "unq1_optima": list(report.unq1_optima),
            "unq2_optima": list(report.unq2_optima),
        },
        "claim": side["claim"],
        "doi": DOI,
    }


def check_xor():
    """XOR gate: y = r1 XOR r2 → pure synergy."""
    j = np.zeros((2, 2, 2), dtype=float)
    for a in (0, 1):
        for b in (0, 1):
            j[a, b, a ^ b] = 0.25
    report = broja_pid_bivariate(j)
    report.assert_pid_sum(atol=1e-4)
    near(report.redundancy, 0.0)
    near(report.unique_source_1, 0.0)
    near(report.unique_source_2, 0.0)
    near(report.synergy, 1.0)
    near(report.I_joint, 1.0)
    return {
        "redundancy": report.redundancy,
        "unique_source_1": report.unique_source_1,
        "unique_source_2": report.unique_source_2,
        "synergy": report.synergy,
        "I_joint": report.I_joint,
    }


def check_redundant_copy():
    """r1 = r2 = y fair bit → pure redundancy."""
    j = np.zeros((2, 2, 2), dtype=float)
    j[0, 0, 0] = 0.5
    j[1, 1, 1] = 0.5
    report = broja_pid_bivariate(j)
    report.assert_pid_sum(atol=1e-4)
    near(report.redundancy, 1.0)
    near(report.unique_source_1, 0.0)
    near(report.unique_source_2, 0.0)
    near(report.synergy, 0.0)
    near(report.I_joint, 1.0)
    return {
        "redundancy": report.redundancy,
        "unique_source_1": report.unique_source_1,
        "unique_source_2": report.unique_source_2,
        "synergy": report.synergy,
        "I_joint": report.I_joint,
    }


def check_scope_and_doi():
    """Huge alphabet refused; n_starts < 3 refused; DOI present."""
    require("10.3390/e16042161" in DOI, DOI)
    require("10.3390/e16042161" in SOURCE, SOURCE)
    # 5*5*5 = 125 > MAX_JOINT_SUPPORT 64
    big = np.ones((5, 5, 5), dtype=float)
    big /= big.sum()
    try:
        broja_pid_bivariate(big)
        raise AssertionError("expected ScopeViolationError for huge alphabet")
    except ScopeViolationError:
        pass
    j = two_bit_copy_joint()
    try:
        broja_pid_bivariate(j, n_starts=2)
        raise AssertionError("expected ScopeViolationError for n_starts<3")
    except ScopeViolationError:
        pass
    return {"doi": DOI, "source": SOURCE, "huge_alphabet": "refused", "n_starts_lt_3": "refused"}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)

    checks = [
        ("two_bit_copy_side_by_side", check_two_bit_copy),
        ("xor_pure_synergy", check_xor),
        ("redundant_copy", check_redundant_copy),
        ("scope_and_doi", check_scope_and_doi),
    ]
    report = {
        "milestone": 17,
        "title": "BROJA bivariate unique information",
        "timestamp": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "platform": platform.platform(),
        "python": sys.version.split()[0],
        "results": {},
        "passed": [],
        "failed": [],
    }
    for name, fn in checks:
        try:
            report["results"][name] = fn()
            report["passed"].append(name)
            print(f"PASS {name}")
        except Exception as exc:  # noqa: BLE001
            report["failed"].append({"name": name, "error": f"{type(exc).__name__}: {exc}"})
            print(f"FAIL {name}: {type(exc).__name__}: {exc}")

    report["count"] = len(checks)
    report["n_passed"] = len(report["passed"])
    report["n_failed"] = len(report["failed"])
    report["ok"] = report["n_failed"] == 0

    out = args.json_out
    if out is None:
        out = Path(__file__).resolve().parent / "verify_broja_pid_core_results.json"
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote {out}")
    print(f"Summary: {report['n_passed']}/{report['count']} passed")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
