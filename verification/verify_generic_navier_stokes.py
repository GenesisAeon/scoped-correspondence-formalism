#!/usr/bin/env python3
"""Hand-checkable verification for GENERIC ↔ NS viscous dissipation (M38).

Checks (numbers from this script run):
  1. Hand example v1=3, v2=1, T=300, ζ=0.5:
       a·∇E=0; M∇S=-a=(-1,1,3,-1); ṗ1=-1;
       σ=ζ(v1-v2)²/T=0.0066…; check_generic_structure ok
  2. Control v1=v2 → M∇S=0
  3. M is GENERIC friction NOT A_ij/L_ij (warning string present)
  4. CALL check_generic_structure (not reimplemented); sources present
  5. Illustrative η=0.005 Pa·s note; coupling exports wired

Stdlib + NumPy. JSON {count, passed, failed, report}.
"""
from __future__ import annotations

import argparse
import datetime as dt
import inspect
import json
import platform
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from scoped_correspondence.coupling.generic_navier_stokes import (  # noqa: E402
    BARHAM_MORRISON_ZAIDNI_2025_DOI,
    FRICTION_NOT_AIJ_LIJ_WARNING,
    GRMELA_OTTINGER_I_DOI,
    ILLUSTRATIVE_ETA_PA_S,
    ILLUSTRATIVE_ZETA_NOTE,
    MORRISON_1984_DOI,
    OTTINGER_GRMELA_II_DOI,
    SOURCE,
    as_report,
    two_cell_viscous_example,
)
from scoped_correspondence.coupling.core import (  # noqa: E402
    check_generic_structure,
)
import scoped_correspondence.coupling as coupling  # noqa: E402


def require(ok, msg):
    if not bool(ok):
        raise AssertionError(msg)


def near(a, b, atol=1e-12, rtol=1e-9):
    if not np.allclose(a, b, atol=atol, rtol=rtol):
        raise AssertionError(f"{a!r} != {b!r}")


def check_hand_example():
    """v1=3, v2=1, T=300, ζ=0.5 — hand numbers from the milestone brief."""
    ex = two_cell_viscous_example(3.0, 1.0, 300.0, 0.5)
    a = np.asarray(ex["a"], dtype=float)
    near(a, np.array([1.0, -1.0, -3.0, 1.0]))
    near(ex["grad_E"], np.array([3.0, 1.0, 1.0, 1.0]))
    near(ex["grad_S"], np.array([0.0, 0.0, 1.0 / 300.0, 1.0 / 300.0]))
    near(ex["J"], np.zeros((4, 4)))
    require(abs(ex["a_dot_grad_E"]) <= 1e-15, f"a·∇E={ex['a_dot_grad_E']}")
    near(ex["M_grad_S"], -a)
    near(ex["M_grad_S"], np.array([-1.0, 1.0, 3.0, -1.0]))
    near(ex["p1_dot"], -1.0)
    near(ex["expected_p1_dot"], -1.0)
    expected_sigma = 0.5 * (3.0 - 1.0) ** 2 / 300.0  # 0.0066…
    near(ex["entropy_production"], expected_sigma)
    near(ex["expected_entropy_production"], expected_sigma)
    st = ex["structure"]
    require(st["ok"] is True, f"structure not ok: {st}")
    # Residuals: equality residuals exactly 0; min_eig within GENERIC tol (1e-10)
    for k, v in st["residuals"].items():
        if k == "min_eig_M_sym":
            require(float(v) >= -1e-10, f"residual {k}={v}")
        else:
            require(abs(float(v)) <= 1e-12, f"residual {k}={v}")
    direct = check_generic_structure(ex["J"], ex["M"], ex["grad_E"], ex["grad_S"])
    require(direct["ok"] is True, "direct check_generic_structure failed")
    return {
        "name": "hand_example_v1_3_v2_1",
        "a": a.tolist(),
        "a_dot_grad_E": float(ex["a_dot_grad_E"]),
        "M_grad_S": np.asarray(ex["M_grad_S"]).tolist(),
        "p1_dot": float(ex["p1_dot"]),
        "entropy_production": float(ex["entropy_production"]),
        "expected_entropy_production": expected_sigma,
        "structure_ok": st["ok"],
        "residuals": {k: float(v) for k, v in st["residuals"].items()},
        "called_check_generic_structure": True,
    }


def check_control_equal_velocities():
    """v1=v2 → M∇S=0 (no irreversible drive)."""
    ex = two_cell_viscous_example(2.0, 2.0, 300.0, 0.5)
    near(ex["M_grad_S"], np.zeros(4))
    near(ex["p1_dot"], 0.0)
    near(ex["entropy_production"], 0.0)
    require(ex["structure"]["ok"] is True, "structure ok at equal v")
    return {
        "name": "control_v1_eq_v2",
        "M_grad_S": np.asarray(ex["M_grad_S"]).tolist(),
        "p1_dot": float(ex["p1_dot"]),
        "entropy_production": float(ex["entropy_production"]),
        "structure_ok": ex["structure"]["ok"],
    }


def check_friction_not_aij_lij():
    """Docstring / warning: M is GENERIC friction, not A_ij or L_ij."""
    mod = sys.modules["scoped_correspondence.coupling.generic_navier_stokes"]
    blob = (
        (inspect.getdoc(mod) or "")
        + "\n"
        + (inspect.getdoc(two_cell_viscous_example) or "")
        + "\n"
        + FRICTION_NOT_AIJ_LIJ_WARNING
    )
    require("A_ij" in blob or "A_ij" in FRICTION_NOT_AIJ_LIJ_WARNING, "A_ij mentioned")
    require("L_ij" in blob or "L_ij" in FRICTION_NOT_AIJ_LIJ_WARNING, "L_ij mentioned")
    require("friction" in blob.lower(), "friction mentioned")
    require("GENERIC" in FRICTION_NOT_AIJ_LIJ_WARNING, "GENERIC mentioned")
    require(
        "NOT" in FRICTION_NOT_AIJ_LIJ_WARNING.upper(),
        "explicit NOT A_ij/L_ij",
    )
    return {
        "name": "friction_not_aij_lij",
        "warning": FRICTION_NOT_AIJ_LIJ_WARNING,
        "ok": True,
    }


def check_sources_and_call():
    """Sources present; module CALLs check_generic_structure (no reimplementation)."""
    mod = sys.modules["scoped_correspondence.coupling.generic_navier_stokes"]
    src = inspect.getsource(mod)
    require("check_generic_structure" in src, "must CALL check_generic_structure")
    require("def check_generic_structure" not in src, "must NOT reimplement check")
    require(GRMELA_OTTINGER_I_DOI in SOURCE, "Grmela/Öttinger I DOI")
    require(OTTINGER_GRMELA_II_DOI in SOURCE, "Öttinger/Grmela II DOI")
    require(MORRISON_1984_DOI in SOURCE, "Morrison 1984 DOI")
    require(BARHAM_MORRISON_ZAIDNI_2025_DOI in SOURCE, "Barham–Morrison–Zaidni DOI")
    require(
        "NOT claimed to be NS" in SOURCE or "not claimed to be NS" in SOURCE.lower(),
        "abstract disclaimer",
    )
    require(abs(ILLUSTRATIVE_ETA_PA_S - 0.005) < 1e-15, "η=0.005")
    require("ILLUSTRATIVE" in ILLUSTRATIVE_ZETA_NOTE.upper(), "illustrative note")
    return {
        "name": "sources_and_call",
        "source": SOURCE,
        "dois": {
            "grmela_ottinger_i": GRMELA_OTTINGER_I_DOI,
            "ottinger_grmela_ii": OTTINGER_GRMELA_II_DOI,
            "morrison_1984": MORRISON_1984_DOI,
            "barham_morrison_zaidni_2025": BARHAM_MORRISON_ZAIDNI_2025_DOI,
        },
        "illustrative_eta_Pa_s": ILLUSTRATIVE_ETA_PA_S,
        "illustrative_note": ILLUSTRATIVE_ZETA_NOTE,
        "calls_check_generic_structure": True,
        "reimplements_check": False,
    }


def check_exports_wired():
    """coupling/__init__.py re-exports M38 API; package root / core untouched by design."""
    require(
        hasattr(coupling, "two_cell_viscous_example"),
        "export two_cell_viscous_example",
    )
    require(
        hasattr(coupling, "FRICTION_NOT_AIJ_LIJ_WARNING"),
        "export FRICTION_NOT_AIJ_LIJ_WARNING",
    )
    require("two_cell_viscous_example" in coupling.__all__, "in __all__")
    ex = two_cell_viscous_example(3.0, 1.0, 300.0, 0.5)
    rep = as_report(ex)
    require(rep["structure_ok"] is True, "report ok")
    require(abs(rep["p1_dot"] + 1.0) < 1e-12, "report p1_dot")
    return {
        "name": "exports_wired",
        "coupling_all_has_two_cell": "two_cell_viscous_example" in coupling.__all__,
        "report_structure_ok": rep["structure_ok"],
        "report_p1_dot": rep["p1_dot"],
        "package_root_untouched_by_design": True,
        "core_py_untouched_by_design": True,
    }


CHECKS = [
    ("hand_example_v1_3_v2_1", check_hand_example),
    ("control_v1_eq_v2", check_control_equal_velocities),
    ("friction_not_aij_lij", check_friction_not_aij_lij),
    ("sources_and_call", check_sources_and_call),
    ("exports_wired", check_exports_wired),
]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", type=Path, default=None)
    args = ap.parse_args(argv)
    report = {}
    failed = []
    for name, fn in CHECKS:
        try:
            report[name] = fn()
        except Exception as exc:  # noqa: BLE001
            failed.append({"name": name, "error": f"{type(exc).__name__}: {exc}"})
            report[name] = {"name": name, "error": f"{type(exc).__name__}: {exc}"}
    out = {
        "count": len(CHECKS),
        "passed": len(CHECKS) - len(failed),
        "failed": len(failed),
        "failures": failed,
        "milestone": 38,
        "forbidden_untouched_by_design": [
            "src/scoped_correspondence/coupling/core.py",
            "src/scoped_correspondence/__init__.py",
            "FORMALISM.md",
            "coupling_layer_afet.md",
        ],
        "key_numbers": {
            "a_dot_grad_E": 0.0,
            "M_grad_S": [-1.0, 1.0, 3.0, -1.0],
            "p1_dot": -1.0,
            "entropy_production": 0.5 * 4.0 / 300.0,
            "control_M_grad_S": [0.0, 0.0, 0.0, 0.0],
            "illustrative_eta_Pa_s": 0.005,
        },
        "meta": {
            "platform": platform.platform(),
            "python": platform.python_version(),
            "source": SOURCE,
            "timestamp": dt.datetime.now().isoformat(timespec="seconds"),
        },
        "report": report,
    }
    out_path = args.json or (
        Path(__file__).with_name("verify_generic_navier_stokes_results.json")
    )
    out_path.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {"passed": out["passed"], "failed": out["failed"], "json": str(out_path)}
        )
    )
    if failed:
        for f in failed:
            print("FAIL", f, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
