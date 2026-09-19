#!/usr/bin/env python3
"""Hand-checkable verification for Lie–Poisson / Casimir (Milestone 26).

Checks (all numbers from this script run):
  1. z=(1,2,3): J=hat_map(z) skew; C=|z|²/2 → residual max_abs==0, norm==0
  2. H with I=(1,2,3): dC/dt==0 and dH/dt==0 along ż = J ∇H
  3. Negative: grad_C'=(1,0,0) → residual ≠ 0
  4. Compatibility: casimir_residual.max_abs ==
     check_generic_structure(...).residuals['max_abs_J_grad_S'] (CALL core)
  5. Scope: finite-dim only; NOT fluid PDE; core.py not reimplemented;
     sources Arnold / Marsden–Ratiu DOIs present; exports wired

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

from scoped_correspondence.coupling.casimir import (  # noqa: E402
    ARNOLD_DOI,
    CASIMIR_RESIDUAL_TOL,
    MARSDEN_RATIU_DOI,
    SOURCE,
    casimir_residual,
    compare_to_generic_J_grad_S,
    hat_map,
    lie_poisson_vector_field,
    quadratic_casimir_grad,
    rigid_body_hamiltonian_grad,
    time_derivative_along_field,
)
from scoped_correspondence.coupling.core import (  # noqa: E402
    check_generic_structure,
)


def require(ok, msg):
    if not bool(ok):
        raise AssertionError(msg)


def near(a, b, atol=1e-12, rtol=1e-9):
    if not np.allclose(a, b, atol=atol, rtol=rtol):
        raise AssertionError(f"{a!r} != {b!r}")


def check_so3_casimir_zero():
    """z=(1,2,3), C=|z|²/2 → J∇C = 0 exactly."""
    z = np.array([1.0, 2.0, 3.0])
    J = hat_map(z)
    # skew: J^T + J == 0
    skew_res = float(np.max(np.abs(J.T + J)))
    require(skew_res == 0.0, f"hat_map must be skew; residual={skew_res}")
    # J v == z × v
    v = np.array([0.5, -1.0, 2.0])
    near(J @ v, np.cross(z, v))

    gC = quadratic_casimir_grad(z)
    near(gC, z)
    cas = casimir_residual(J, gC)
    require(cas["max_abs"] == 0.0, f"Casimir max_abs must be 0; got {cas['max_abs']}")
    require(cas["norm"] == 0.0, f"Casimir norm must be 0; got {cas['norm']}")
    require(cas["ok"] is True, "casimir ok")
    near(cas["J_grad_C"], np.zeros(3))
    return {
        "name": "so3_casimir_residual_zero",
        "z": z.tolist(),
        "J": J.tolist(),
        "skew_residual": skew_res,
        "grad_C": gC.tolist(),
        "max_abs": cas["max_abs"],
        "norm": cas["norm"],
        "ok": cas["ok"],
    }


def check_conservation_dC_dH():
    """Along rigid-body flow with I=(1,2,3): dC/dt=0 and dH/dt=0."""
    z = np.array([1.0, 2.0, 3.0])
    I = np.array([1.0, 2.0, 3.0])
    J = hat_map(z)
    gH = rigid_body_hamiltonian_grad(z, I)
    gC = quadratic_casimir_grad(z)
    z_dot = lie_poisson_vector_field(z, I)
    near(z_dot, J @ gH)
    near(z_dot, np.cross(z, gH))

    dC_dt = time_derivative_along_field(gC, z_dot)
    dH_dt = time_derivative_along_field(gH, z_dot)
    require(dC_dt == 0.0, f"dC/dt must be exactly 0; got {dC_dt}")
    require(abs(dH_dt) <= 1e-15, f"dH/dt must be ~0; got {dH_dt}")
    # Also: skew ⇒ ∇H·J∇H = 0
    require(abs(float(gH @ J @ gH)) <= 1e-15, "energy via skew")
    return {
        "name": "conservation_dC_dH",
        "z": z.tolist(),
        "I": I.tolist(),
        "Omega": gH.tolist(),
        "z_dot": z_dot.tolist(),
        "dC_dt": dC_dt,
        "dH_dt": dH_dt,
    }


def check_negative_grad():
    """grad_C' = (1,0,0) is NOT the Casimir gradient → residual ≠ 0."""
    z = np.array([1.0, 2.0, 3.0])
    J = hat_map(z)
    g_bad = np.array([1.0, 0.0, 0.0])
    cas = casimir_residual(J, g_bad)
    expected = np.cross(z, g_bad)  # (0, 3, -2)
    near(cas["J_grad_C"], expected)
    require(cas["max_abs"] != 0.0, "negative residual must be nonzero")
    require(cas["ok"] is False, "ok must be False")
    require(cas["max_abs"] == 3.0, f"expected max_abs=3; got {cas['max_abs']}")
    require(cas["norm"] == float(np.linalg.norm(expected)), "norm")
    return {
        "name": "negative_grad_C_prime",
        "grad_C_prime": g_bad.tolist(),
        "J_grad_C": cas["J_grad_C"].tolist(),
        "max_abs": cas["max_abs"],
        "norm": cas["norm"],
        "ok": cas["ok"],
    }


def check_generic_compatibility():
    """casimir_residual.max_abs matches check_generic_structure max_abs_J_grad_S.

    CALLS check_generic_structure — does not reimplement.
    """
    z = np.array([1.0, 2.0, 3.0])
    J = hat_map(z)
    # True Casimir grad → both zero
    gS = quadratic_casimir_grad(z)
    cmp_ok = compare_to_generic_J_grad_S(J, gS)
    require(cmp_ok["max_abs_match"] is True, "max_abs must match (Casimir)")
    require(cmp_ok["casimir_max_abs"] == 0.0, "casimir max_abs 0")
    require(cmp_ok["generic_max_abs_J_grad_S"] == 0.0, "generic max_abs 0")
    require(cmp_ok["generic_report"]["J_grad_S_zero"] is True, "J_grad_S_zero")
    require(cmp_ok["generic_report"]["J_antisymmetric"] is True, "J skew")

    # Direct CALL (explicit) — same numbers
    report = check_generic_structure(
        J, np.zeros((3, 3)), np.zeros(3), gS
    )
    cas = casimir_residual(J, gS)
    require(
        cas["max_abs"] == report["residuals"]["max_abs_J_grad_S"],
        "direct equality with max_abs_J_grad_S",
    )

    # Non-Casimir grad → both nonzero and equal
    g_bad = np.array([1.0, 0.0, 0.0])
    cmp_bad = compare_to_generic_J_grad_S(J, g_bad)
    require(cmp_bad["max_abs_match"] is True, "max_abs match (negative)")
    require(cmp_bad["casimir_max_abs"] == 3.0, "bad casimir max_abs")
    require(cmp_bad["generic_max_abs_J_grad_S"] == 3.0, "bad generic max_abs")
    require(cmp_bad["generic_report"]["J_grad_S_zero"] is False, "not zero")

    # Ensure compare_to_generic literally calls check_generic_structure
    src = inspect.getsource(compare_to_generic_J_grad_S)
    require("check_generic_structure" in src, "must call check_generic_structure")
    require("max_abs_J_grad_S" in src, "must read max_abs_J_grad_S")

    return {
        "name": "generic_compatibility",
        "casimir_zero_max_abs": cmp_ok["casimir_max_abs"],
        "generic_zero_max_abs_J_grad_S": cmp_ok["generic_max_abs_J_grad_S"],
        "casimir_bad_max_abs": cmp_bad["casimir_max_abs"],
        "generic_bad_max_abs_J_grad_S": cmp_bad["generic_max_abs_J_grad_S"],
        "max_abs_match_zero": cmp_ok["max_abs_match"],
        "max_abs_match_bad": cmp_bad["max_abs_match"],
        "called_check_generic_structure": True,
    }


def check_scope_and_exports():
    """Finite-dim only; NOT fluid PDE; DOIs; submodule exports; no core edit."""
    cas_path = Path(inspect.getfile(casimir_residual))
    src_text = cas_path.read_text(encoding="utf-8")
    require(ARNOLD_DOI in src_text and ARNOLD_DOI in SOURCE, "Arnold DOI")
    require(MARSDEN_RATIU_DOI in src_text and MARSDEN_RATIU_DOI in SOURCE, "MR DOI")
    require("NOT fluid PDE" in src_text or "not fluid PDE" in src_text.lower()
            or "NOT a fluid PDE" in src_text, "fluid PDE disclaimer")
    require("finite-dim" in src_text.lower() or "finite-dimensional" in src_text.lower(),
            "finite-dim scope")
    require("not claim" in src_text.lower() or "NOT claim" in src_text
            or "does **not** claim" in src_text.lower()
            or "Does **NOT** claim" in src_text, "no fluid-dynamics claim")
    require("general Casimir" in src_text or "general Casimir-finder" in src_text
            or "not a general Casimir" in src_text.lower()
            or "Does **NOT** ship a general Casimir" in src_text, "no Casimir finder")
    # Must not reimplement GENERIC residual logic — call only
    require("from scoped_correspondence.coupling.core import" in src_text, "imports core")
    require("check_generic_structure" in src_text, "names check_generic_structure")
    # No continuum solver implementations (disclaimer words are allowed).
    for banned_impl in ("def navier_stokes", "def vlasov_", "def continuum_bracket",
                        "def euler_fluid"):
        require(banned_impl not in src_text.lower(), f"banned impl {banned_impl}")

    from scoped_correspondence.coupling import (
        CASIMIR_SOURCE,
        casimir_residual as cr,
        hat_map as hm,
        compare_to_generic_J_grad_S as cmp,
    )
    require(cr is casimir_residual and hm is hat_map and cmp is compare_to_generic_J_grad_S,
            "exports identity")
    require("10.5802/aif.233" in CASIMIR_SOURCE, "export SOURCE DOI")
    require(CASIMIR_RESIDUAL_TOL == 1e-10, "tol")
    return {
        "name": "scope_and_exports",
        "SOURCE": SOURCE,
        "arnold_doi": ARNOLD_DOI,
        "marsden_ratiu_doi": MARSDEN_RATIU_DOI,
        "module": cas_path.name,
        "tol": CASIMIR_RESIDUAL_TOL,
    }


CHECKS = [
    ("so3_casimir_residual_zero", check_so3_casimir_zero),
    ("conservation_dC_dH", check_conservation_dC_dH),
    ("negative_grad_C_prime", check_negative_grad),
    ("generic_compatibility", check_generic_compatibility),
    ("scope_and_exports", check_scope_and_exports),
]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", type=Path, default=None)
    args = ap.parse_args(argv)

    results = []
    passed = 0
    failed = 0
    report = {}
    for name, fn in CHECKS:
        try:
            detail = fn()
            results.append({"name": name, "ok": True, "detail": detail})
            report[name] = detail
            passed += 1
            print(f"PASS {name}")
        except Exception as exc:  # noqa: BLE001
            results.append({"name": name, "ok": False, "error": str(exc)})
            report[name] = {"error": str(exc)}
            failed += 1
            print(f"FAIL {name}: {exc}")

    out = {
        "milestone": 26,
        "title": "Lie-Poisson / Casimir Invariants",
        "count": len(CHECKS),
        "passed": passed,
        "failed": failed,
        "results": results,
        "report": report,
        "key_zeros": {
            "casimir_max_abs_at_z_1_2_3": report.get("so3_casimir_residual_zero", {}).get("max_abs"),
            "casimir_norm_at_z_1_2_3": report.get("so3_casimir_residual_zero", {}).get("norm"),
            "dC_dt": report.get("conservation_dC_dH", {}).get("dC_dt"),
            "dH_dt": report.get("conservation_dC_dH", {}).get("dH_dt"),
            "negative_max_abs": report.get("negative_grad_C_prime", {}).get("max_abs"),
            "generic_match_zero": report.get("generic_compatibility", {}).get(
                "max_abs_match_zero"
            ),
        },
        "forbidden_untouched_by_design": [
            "src/scoped_correspondence/coupling/core.py",
            "src/scoped_correspondence/__init__.py",
            "FORMALISM.md",
            "coupling_layer_afet.md",
        ],
        "meta": {
            "timestamp": dt.datetime.now().isoformat(timespec="seconds"),
            "python": platform.python_version(),
            "platform": platform.platform(),
            "source": SOURCE,
            "arnold_doi": ARNOLD_DOI,
            "marsden_ratiu_doi": MARSDEN_RATIU_DOI,
        },
    }
    text = json.dumps(out, indent=2, sort_keys=True)
    out_path = args.json or (
        Path(__file__).resolve().parent / "verify_casimir_residual_results.json"
    )
    out_path.write_text(text + "\n", encoding="utf-8")
    print(f"Wrote {out_path}")
    print(f"Summary: {passed}/{len(CHECKS)} passed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
