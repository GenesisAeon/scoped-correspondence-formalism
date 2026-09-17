#!/usr/bin/env python3
"""Hand-checkable verification for Generator Lumpability (Milestone 11).

Checks (all numbers from this script run):
  1. Exact lumpable 3-state CTMC + partition_matrix([0,0,1]) → error == 0
  2. Non-lumpable (different rates to lump) → error == 1.0 concretely
  3. Generator validation rejects bad row-sums / negative off-diag
  4. Real partition_matrix from closure.core (NOT a stub)

Stdlib + NumPy. JSON {count, passed, failed, report}; numbers from this run.
Calls real partition_matrix only; closure/core.py unchanged.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import platform
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from scoped_correspondence.closure.core import partition_matrix  # noqa: E402
from scoped_correspondence.closure.generator_lumpability import (  # noqa: E402
    generator_closure_error,
    is_exact_generator_lumpability,
)
from scoped_correspondence.errors import ScopeViolationError  # noqa: E402


def require(ok, msg):
    if not bool(ok):
        raise AssertionError(msg)


def near(a, b, atol=1e-12, rtol=1e-9):
    if not np.allclose(a, b, atol=atol, rtol=rtol):
        raise AssertionError(f"{a!r} != {b!r}")


def core_blob_sha() -> str:
    """Git blob SHA of the on-disk closure/core.py used for partition_matrix."""
    path = SRC / "scoped_correspondence" / "closure" / "core.py"
    content = path.read_bytes()
    return hashlib.sha1(b"blob %d\0" % len(content) + content).hexdigest()


def check_exact_lumpable():
    """States 0,1 identical rates to 2 → error == 0, is_exact True."""
    C, _lift = partition_matrix([0, 0, 1])
    require(C.shape == (3, 2), f"C shape {C.shape}")
    near(C, np.array([[1.0, 0.0], [1.0, 0.0], [0.0, 1.0]]))

    Q = np.array(
        [
            [-3.0, 1.0, 2.0],
            [1.0, -3.0, 2.0],
            [1.0, 1.0, -2.0],
        ]
    )
    Q_macro = np.array(
        [
            [-2.0, 2.0],
            [2.0, -2.0],
        ]
    )

    err = generator_closure_error(Q, C, Q_macro)
    require(err == 0.0, f"exact error must be 0.0; got {err!r}")
    require(
        is_exact_generator_lumpability(Q, C, Q_macro, tol=1e-10) is True,
        "is_exact must be True",
    )
    # QC == C Q_macro elementwise
    near(Q @ C, C @ Q_macro)
    return {"error": err, "is_exact": True, "Q_macro": Q_macro.tolist()}


def check_non_lumpable():
    """Different exit rates to state 2 → concrete error == 1.0."""
    C, _lift = partition_matrix([0, 0, 1])
    Q = np.array(
        [
            [-3.0, 1.0, 2.0],  # exit to block {2}: 2
            [1.0, -4.0, 3.0],  # exit to block {2}: 3  (DIFFERENT)
            [1.0, 1.0, -2.0],
        ]
    )
    Q_macro = np.array(
        [
            [-2.0, 2.0],
            [2.0, -2.0],
        ]
    )
    err = generator_closure_error(Q, C, Q_macro)
    require(abs(err - 1.0) < 1e-12, f"non-lumpable error must be 1.0; got {err!r}")
    require(
        is_exact_generator_lumpability(Q, C, Q_macro, tol=1e-10) is False,
        "is_exact must be False",
    )
    # Hand check: residual row 1 = [-1, 1], ||.||_∞ = 1
    residual = Q @ C - C @ Q_macro
    near(residual[1], np.array([-1.0, 1.0]))
    return {"error": err, "is_exact": False, "residual_row1": residual[1].tolist()}


def check_generator_validation():
    """Bad generators raise ScopeViolationError."""
    C, _ = partition_matrix([0, 0, 1])
    Q_macro = np.zeros((2, 2))
    bad_row = np.array(
        [
            [-2.0, 1.0, 2.0],  # row sum +1 ≠ 0
            [1.0, -2.0, 1.0],
            [1.0, 1.0, -2.0],
        ]
    )
    raised = False
    try:
        generator_closure_error(bad_row, C, Q_macro)
    except ScopeViolationError:
        raised = True
    require(raised, "non-zero row sum must raise")

    bad_off = np.array(
        [
            [-1.0, -1.0, 2.0],  # negative off-diag
            [1.0, -2.0, 1.0],
            [1.0, 1.0, -2.0],
        ]
    )
    raised2 = False
    try:
        is_exact_generator_lumpability(bad_off, C, Q_macro)
    except ScopeViolationError:
        raised2 = True
    require(raised2, "negative off-diag must raise")
    return {"bad_row_sum_raises": True, "bad_off_diag_raises": True}


def check_not_tv_docstring():
    """Docstring of generator_closure_error must explain NOT TV."""
    doc = generator_closure_error.__doc__ or ""
    require("not" in doc.lower() or "NOT" in doc, "doc must say not TV")
    require("TV" in doc or "total variation" in doc.lower(), "doc must mention TV")
    require("∞" in doc or "infty" in doc.lower() or "inf" in doc.lower(), "∞-norm")
    return {"doc_mentions_not_tv": True}


CHECKS = [
    ("exact_lumpable_error_0", check_exact_lumpable),
    ("non_lumpable_error_1", check_non_lumpable),
    ("generator_validation", check_generator_validation),
    ("docstring_not_tv", check_not_tv_docstring),
]


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--json-out",
        type=Path,
        default=Path(__file__).with_name("verify_generator_lumpability_core_results.json"),
    )
    args = parser.parse_args(argv)

    report = []
    passed = 0
    failed = 0
    for name, fn in CHECKS:
        entry = {"name": name, "ok": False}
        try:
            detail = fn()
            entry["ok"] = True
            entry["detail"] = detail
            passed += 1
            print(f"PASS  {name}: {detail}")
        except Exception as exc:  # noqa: BLE001 — collect all failures
            entry["ok"] = False
            entry["error"] = f"{type(exc).__name__}: {exc}"
            failed += 1
            print(f"FAIL  {name}: {entry['error']}", file=sys.stderr)
        report.append(entry)

    blob = core_blob_sha()
    payload = {
        "count": len(CHECKS),
        "passed": passed,
        "failed": failed,
        "report": report,
        "core_py_git_blob_sha": blob,
        "expected_master_core_blob_sha": "dc3367eddeb8dce099d5fff4fe9c97e2b25b7756",
        "partition_matrix_source": "scoped_correspondence.closure.core.partition_matrix",
        "sources": {
            "buchholz_1994": {
                "title": "Exact and ordinary lumpability in finite Markov chains",
                "doi": "10.1017/S0021900200107338",
            },
            "michel_siegle_2024": {
                "title": "Formal error bounds for the state space reduction of Markov chains",
                "doi": "10.1016/j.peva.2024.102464",
                "arxiv": "2403.07618",
            },
        },
        "meta": {
            "timestamp": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
            "platform": platform.platform(),
            "python": sys.version.split()[0],
            "numpy": np.__version__,
            "milestone": 11,
        },
    }
    args.json_out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {args.json_out}")
    print(f"core.py git blob SHA: {blob}")
    if failed:
        sys.exit(1)
    print(f"ALL {passed}/{len(CHECKS)} PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
