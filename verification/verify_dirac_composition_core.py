#!/usr/bin/env python3
"""Hand-checkable verification for Dirac Structure Composition (Milestone 12).

Checks (all numbers from this script run):
  1. Worked example J1=[[0,1],[-1,0]], J2=[[0,2],[-2,0]]
     → J_total skew (ok True); max|J^T+J|==0; interface power ==0 on ≥2 samples
  2. check_generic_structure called; only J_antisymmetric is the M12 claim
  3. Non-skew J1 raises ScopeViolationError

Stdlib + NumPy. JSON {count, passed, failed, report}; numbers from this run.
Calls real check_generic_structure via compose_skew_symmetric (core.py unchanged).
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

from scoped_correspondence.coupling.core import (  # noqa: E402
    GENERIC_STRUCTURE_TOL,
    check_generic_structure,
)
from scoped_correspondence.coupling.dirac_composition import (  # noqa: E402
    FEEDBACK,
    SOURCE,
    DiracCompositionResult,
    compose_skew_symmetric,
    interface_power_under_feedback,
)
from scoped_correspondence.errors import ScopeViolationError  # noqa: E402


def require(ok, msg):
    if not bool(ok):
        raise AssertionError(msg)


def near(a, b, atol=1e-12, rtol=1e-9):
    if not np.allclose(a, b, atol=atol, rtol=rtol):
        raise AssertionError(f"{a!r} != {b!r}")


def expected_J_total(J1, J2):
    """Default g1=g2=I closed-loop block form."""
    n = J1.shape[0]
    eye = np.eye(n)
    return np.block([[J1, -eye], [eye, J2]])


def check_worked_example():
    """J1, J2 from milestone brief → skew J_total; power exactly 0."""
    J1 = np.array([[0.0, 1.0], [-1.0, 0.0]])
    J2 = np.array([[0.0, 2.0], [-2.0, 0.0]])
    samples = [
        (np.array([1.0, 0.0]), np.array([0.0, 1.0])),
        (np.array([2.0, -1.0]), np.array([-3.0, 4.0])),
        (np.array([0.5, 0.5]), np.array([1.5, -2.5])),
    ]
    result = compose_skew_symmetric(
        J1, J2, FEEDBACK, power_samples=samples
    )

    require(isinstance(result, DiracCompositionResult), "result type")
    require(result.source == SOURCE, "source citation")
    require(FEEDBACK in result.source or "Cervera" in result.source, "Cervera")
    require(result.ok is True, f"ok True; report={result.antisymmetry_report}")

    Jt_exp = expected_J_total(J1, J2)
    near(result.J_total, Jt_exp)
    skew_res = float(np.max(np.abs(result.J_total.T + result.J_total)))
    require(skew_res == 0.0, f"skew residual must be exactly 0; got {skew_res}")
    require(
        result.antisymmetry_report["J_antisymmetric"] is True,
        "J_antisymmetric flag",
    )
    require(
        result.antisymmetry_report["residuals"]["max_abs_J_T_plus_J"] == 0.0,
        "residual max_abs_J_T_plus_J == 0",
    )

    # Interface power exactly 0 on ≥2 state/port vectors
    powers = [interface_power_under_feedback(y1, y2) for y1, y2 in samples]
    require(len(powers) >= 2, "≥2 power samples")
    for i, p in enumerate(powers):
        require(p == 0.0, f"interface power sample[{i}] exactly 0; got {p}")
    require(
        result.interface_power_max_abs == 0.0,
        f"interface_power_max_abs==0; got {result.interface_power_max_abs}",
    )

    # Explicit: only J claim — M was passed as zeros; do not assert M model
    require(
        "J composition" in result.disclaimer or "M" in result.disclaimer,
        "disclaimer mentions J-only / no M claim",
    )

    return {
        "name": "worked_example_J1_J2_feedback",
        "ok": result.ok,
        "J_total": result.J_total.tolist(),
        "skew_residual_max_abs_JT_plus_J": skew_res,
        "interface_power_samples": powers,
        "interface_power_max_abs": result.interface_power_max_abs,
        "n_power_samples": len(powers),
        "J_antisymmetric": result.antisymmetry_report["J_antisymmetric"],
        "source": result.source,
        "tol": GENERIC_STRUCTURE_TOL,
    }


def check_generic_call_surface():
    """compose path calls check_generic_structure; M12 reads J_antisymmetric only."""
    J1 = np.array([[0.0, 1.0], [-1.0, 0.0]])
    J2 = np.array([[0.0, 2.0], [-2.0, 0.0]])
    result = compose_skew_symmetric(J1, J2, "feedback")
    report = result.antisymmetry_report
    # Same keys as check_generic_structure
    for key in (
        "J_antisymmetric",
        "M_symmetric",
        "M_psd",
        "J_grad_S_zero",
        "M_grad_E_zero",
        "ok",
        "residuals",
        "disclaimer",
    ):
        require(key in report, f"report has {key}")

    # Direct call reproduces antisymmetry residual
    n = result.J_total.shape[0]
    direct = check_generic_structure(
        result.J_total,
        np.zeros((n, n)),
        np.zeros(n),
        np.zeros(n),
        tol=GENERIC_STRUCTURE_TOL,
    )
    near(
        direct["residuals"]["max_abs_J_T_plus_J"],
        report["residuals"]["max_abs_J_T_plus_J"],
    )
    require(direct["J_antisymmetric"] is True, "direct J_antisymmetric")
    # M12 claim surface is J only (zeros M is scaffolding, not an M claim)
    return {
        "name": "check_generic_structure_call_surface",
        "J_antisymmetric": report["J_antisymmetric"],
        "direct_max_abs_JT_plus_J": direct["residuals"]["max_abs_J_T_plus_J"],
        "m12_claim": "J_antisymmetric_only",
        "note": "M_* flags present from API but not claimed by M12",
    }


def check_nonskew_rejected():
    """Non-antisymmetric J1 must raise ScopeViolationError."""
    J1 = np.array([[0.0, 1.0], [0.5, 0.0]])  # not skew
    J2 = np.array([[0.0, 2.0], [-2.0, 0.0]])
    raised = False
    try:
        compose_skew_symmetric(J1, J2, FEEDBACK)
    except ScopeViolationError as exc:
        raised = True
        require("J1" in str(exc) or "antisymmetric" in str(exc), str(exc))
    require(raised, "expected ScopeViolationError for non-skew J1")
    return {"name": "nonskew_J1_rejected", "raised": True}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--json-out",
        type=Path,
        default=ROOT / "verification" / "verify_dirac_composition_core_results.json",
    )
    args = parser.parse_args(argv)

    checks = [
        check_worked_example,
        check_generic_call_surface,
        check_nonskew_rejected,
    ]
    report = []
    failed = []
    for fn in checks:
        try:
            report.append({"status": "passed", **fn()})
        except Exception as exc:  # noqa: BLE001 — collect all for JSON
            failed.append(fn.__name__)
            report.append(
                {"status": "failed", "name": fn.__name__, "error": repr(exc)}
            )

    payload = {
        "milestone": "M12",
        "title": "Dirac Structure Composition",
        "count": len(checks),
        "passed": len(checks) - len(failed),
        "failed": len(failed),
        "failed_names": failed,
        "report": report,
        "source": SOURCE,
        "doi": "10.1016/j.automatica.2006.08.014",
        "platform": platform.platform(),
        "python": sys.version,
        "timestamp_local": dt.datetime.now().astimezone().isoformat(),
        "forbidden_untouched_by_design": [
            "src/scoped_correspondence/coupling/core.py",
            "FORMALISM.md",
            "coupling_layer_afet.md",
            "closure/",
            "validation/",
            "src/scoped_correspondence/__init__.py",
        ],
    }
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: payload[k] for k in ("count", "passed", "failed", "failed_names")}, indent=2))
    if failed:
        print("FAILED:", failed, file=sys.stderr)
        return 1
    print("ALL PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
