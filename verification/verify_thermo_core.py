#!/usr/bin/env python3
"""Equivalence checks for Thermo / GENERIC core (Milestone 8).

Matches extension_results.json e10 / e13 EXACTLY (all e13 param combos),
plus projection cases for Pi=[[1,1]] and Pi=[[1,0]] from the heat example.
Does NOT edit verify_extensions.py, coupling/core.py, or layer docs.
"""
from __future__ import annotations

import argparse
import datetime as dt
import inspect
import itertools
import json
import platform
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from scoped_correspondence.thermo import (  # noqa: E402
    heat_generic_example,
    project_generic_structure,
    stochastic_inverse_not_detailed_balance,
)
from scoped_correspondence.coupling import check_generic_structure  # noqa: E402


def require(ok, msg):
    if not bool(ok):
        raise AssertionError(msg)


def near(a, b, atol=1e-10, rtol=1e-9):
    if not np.allclose(a, b, atol=atol, rtol=rtol):
        raise AssertionError(f"{a!r} != {b!r}")


def load_extension_results():
    path = ROOT / "verification" / "extension_results.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    by_name = {c["name"]: c for c in data["checks"]}
    return data, by_name


def legacy_evidence(name: str):
    _, by_name = load_extension_results()
    require(name in by_name, f"missing legacy {name}")
    require(by_name[name]["status"] == "passed", f"legacy {name} not passed")
    return by_name[name]["evidence"]


def t01_e13_all_param_combos():
    """Port e13 over all 32 parameter combinations; match extension_results.json."""
    expected = legacy_evidence("e13_generic_heat_structure")
    checked = 0
    productions = []
    last = None
    for ca, cb, conductance, ta, tb in itertools.product(
        [2.0, 5.0], [3.0, 7.0], [0.1, 3.0], [250.0, 310.0], [260.0, 310.0]
    ):
        report = heat_generic_example(ca, cb, conductance, ta, tb)
        require(report["generic_structure"]["ok"], f"GENERIC fail ca={ca}...")
        require(report["generic_structure"]["M_grad_E_zero"], "M@grad_E")
        require(report["generic_structure"]["J_antisymmetric"], "J anti")
        require(report["generic_structure"]["M_symmetric"], "M sym")
        require(report["generic_structure"]["M_psd"], "M psd")
        near(
            report["entropy_production"],
            conductance * (ta - tb) ** 2 / (ta * tb),
        )
        productions.append(report["entropy_production"])
        last = report
        checked += 1
    require(checked == 32, f"expected 32 combos, got {checked}")
    require(checked == expected["parameter_combinations"], "combo count vs legacy")
    require(
        expected["gradient_and_balance_checks"] is True,
        "legacy gradient_and_balance_checks",
    )
    require(
        expected["poisson_operator"] == last["poisson_operator"],
        "poisson_operator text",
    )
    # Representative entropy production (ca=2,cb=3,G=0.1,ta=250,tb=260)
    g_ref = 0.1
    ta_ref, tb_ref = 250.0, 260.0
    prod_ref = g_ref * (ta_ref - tb_ref) ** 2 / (ta_ref * tb_ref)
    near(productions[0], prod_ref)
    return {
        "parameter_combinations": checked,
        "gradient_and_balance_checks": True,
        "poisson_operator": last["poisson_operator"],
        "generic_structure_ok_all": True,
        "first_combo_entropy_production": float(productions[0]),
        "legacy_match": {
            "parameter_combinations": expected["parameter_combinations"],
            "gradient_and_balance_checks": expected["gradient_and_balance_checks"],
            "poisson_operator": expected["poisson_operator"],
        },
    }


def t02_e10_stochastic_inverse_not_db():
    """Port e10; match extension_results.json evidence exactly."""
    expected = legacy_evidence("e10_inverse_is_not_detailed_balance")
    report = stochastic_inverse_not_detailed_balance()
    require(report["stochastic_inverse"] is True, "stochastic inverse")
    require(report["detailed_balance"] is False, "not detailed balance")
    require(
        report["forward_flow"] == expected["forward_flow"],
        f"forward_flow exact {report['forward_flow']} vs {expected['forward_flow']}",
    )
    require(
        report["reverse_flow"] == expected["reverse_flow"],
        f"reverse_flow exact {report['reverse_flow']} vs {expected['reverse_flow']}",
    )
    require(report["stochastic_inverse"] is expected["stochastic_inverse"], "si flag")
    require(report["detailed_balance"] is expected["detailed_balance"], "db flag")
    return {
        "stochastic_inverse": True,
        "detailed_balance": False,
        "forward_flow": report["forward_flow"],
        "reverse_flow": report["reverse_flow"],
        "mapping": report["mapping"],
    }


def _heat_m(ca=2.0, cb=3.0, conductance=0.1, ta=250.0, tb=260.0):
    return heat_generic_example(ca, cb, conductance, ta, tb)


def t03_projection_sum_wipes_dissipation():
    """Pi=[[1,1]]: M' = Pi@M@Pi.T = 0 from M@[1,1]=0; structure may pass."""
    heat = _heat_m()
    J = np.asarray(heat["J"], dtype=float)
    M = np.asarray(heat["M"], dtype=float)
    Pi = np.array([[1.0, 1.0]], dtype=float)
    # Explicit primes: total energy gradient in 1-D reduced coord is 1;
    # sum of 1/T components as a naive scalar (caller-supplied, not silent Pi@grad).
    grad_E_prime = np.array([1.0])
    grad_S_prime = np.array([float(sum(heat["grad_S"]))])
    out = project_generic_structure(J, M, Pi, grad_E_prime, grad_S_prime)
    Mp = np.asarray(out["M_prime"], dtype=float)
    near(Mp, [[0.0]])
    require("does NOT claim" in out["disclaimer"], "§9 disclaimer")
    require("valid reduced" in out["disclaimer"].lower() or "potentials" in out["disclaimer"],
            "potentials disclaimer")
    return {
        "Pi": Pi.tolist(),
        "M_prime": out["M_prime"],
        "J_prime": out["J_prime"],
        "generic_structure_ok": bool(out["generic_structure"]["ok"]),
        "dissipation_wiped": True,
        "valid_reduced_GENERIC": False,
        "disclaimer": out["disclaimer"],
        "note": "Structure may pass with wiped dissipation; NOT a claim of valid reduce (§9).",
    }


def t04_projection_single_reservoir_not_valid_reduce():
    """Pi=[[1,0]]: M'=M[0,0]=G*ta*tb; algebraically OK but NOT valid reduced GENERIC."""
    heat = _heat_m()
    J = np.asarray(heat["J"], dtype=float)
    M = np.asarray(heat["M"], dtype=float)
    G, ta, tb = heat["conductance"], heat["ta"], heat["tb"]
    Pi = np.array([[1.0, 0.0]], dtype=float)
    # Explicit primes (caller-supplied — no silent Pi@grad).
    # For 1×1 M' = G*ta*tb > 0, algebraic M'@grad_E'=0 forces grad_E_prime=[0].
    # That choice itself shows the primes are not a valid reduced energy potential (§9).
    grad_E_prime = np.array([0.0])
    grad_S_prime = np.array([heat["grad_S"][0]])
    out = project_generic_structure(J, M, Pi, grad_E_prime, grad_S_prime)
    Mp = np.asarray(out["M_prime"], dtype=float)
    near(Mp, [[G * ta * tb]])
    require(out["generic_structure"]["ok"], "algebraic structure may pass")
    require("does NOT claim" in out["disclaimer"], "§9 disclaimer present")
    return {
        "Pi": Pi.tolist(),
        "M_prime": out["M_prime"],
        "M_prime_00": float(Mp[0, 0]),
        "expected_G_ta_tb": float(G * ta * tb),
        "grad_E_prime": grad_E_prime.tolist(),
        "grad_S_prime": grad_S_prime.tolist(),
        "generic_structure_ok": True,
        "valid_reduced_GENERIC": False,
        "disclaimer": out["disclaimer"],
        "note": (
            "Algebraically OK (M'=G*ta*tb) but MUST note: NOT a valid reduced "
            "GENERIC system (coupling_layer_afet.md §9)."
        ),
    }


def t05_project_signature_no_silent_grad_default():
    """grad_E_prime / grad_S_prime are required positional params (no Pi@grad default)."""
    sig = inspect.signature(project_generic_structure)
    params = list(sig.parameters)
    require("grad_E_prime" in params, "grad_E_prime in signature")
    require("grad_S_prime" in params, "grad_S_prime in signature")
    for name in ("grad_E_prime", "grad_S_prime"):
        p = sig.parameters[name]
        require(
            p.default is inspect.Parameter.empty,
            f"{name} must not have a silent default",
        )
    # Omitting primes must TypeError
    heat = _heat_m()
    J = np.asarray(heat["J"])
    M = np.asarray(heat["M"])
    Pi = np.array([[1.0, 1.0]])
    raised = False
    try:
        project_generic_structure(J, M, Pi)  # type: ignore[call-arg]
    except TypeError:
        raised = True
    require(raised, "omitting grad primes must TypeError")
    # Docstring must carry §9 disclaimer language
    doc = project_generic_structure.__doc__ or ""
    require("does **not** claim" in doc or "does not claim" in doc.lower(), "doc claim")
    require("§9" in doc or "§9" in doc or "§9" in doc, "doc §9")
    require("no" in doc.lower() and "silent" in doc.lower(), "doc silent default")
    return {
        "grad_E_prime_required": True,
        "grad_S_prime_required": True,
        "omitting_primes_raises_TypeError": True,
        "docstring_has_section9_disclaimer": True,
    }


def t06_heat_calls_check_generic_structure():
    """Sanity: heat example structure matches direct check_generic_structure call."""
    heat = _heat_m()
    direct = check_generic_structure(
        np.asarray(heat["J"]),
        np.asarray(heat["M"]),
        heat["grad_E"],
        heat["grad_S"],
    )
    require(direct["ok"] is True, "direct ok")
    require(heat["generic_structure"]["ok"] is True, "heat ok")
    near(
        heat["generic_structure"]["residuals"]["max_abs_M_grad_E"],
        direct["residuals"]["max_abs_M_grad_E"],
    )
    return {
        "direct_ok": True,
        "heat_ok": True,
        "grad_E": heat["grad_E"],
        "entropy_production": heat["entropy_production"],
    }


CHECKS = [
    ("t01_e13_all_param_combos", t01_e13_all_param_combos),
    ("t02_e10_stochastic_inverse_not_db", t02_e10_stochastic_inverse_not_db),
    ("t03_projection_sum_wipes_dissipation", t03_projection_sum_wipes_dissipation),
    ("t04_projection_single_reservoir_not_valid_reduce", t04_projection_single_reservoir_not_valid_reduce),
    ("t05_project_signature_no_silent_grad_default", t05_project_signature_no_silent_grad_default),
    ("t06_heat_calls_check_generic_structure", t06_heat_calls_check_generic_structure),
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).with_name("verify_thermo_core_results.json"),
    )
    args = parser.parse_args()
    results = []
    for name, fn in CHECKS:
        try:
            ev = fn()
            results.append({"id": name, "status": "passed", "evidence": ev})
        except Exception as exc:
            results.append(
                {"id": name, "status": "failed", "error": f"{type(exc).__name__}: {exc}"}
            )
    passed = sum(r["status"] == "passed" for r in results)
    failed = [r["id"] for r in results if r["status"] != "passed"]
    report_obj = {
        "milestone": "M8_thermo_core",
        "kind": "Legacy equivalence e10/e13 + projection §9 cases",
        "generated_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "python": platform.python_version(),
        "numpy": np.__version__,
        "count": len(results),
        "passed": passed,
        "failed": len(failed),
        "legacy_results": "verification/extension_results.json",
        "checks": results,
    }
    args.output.write_text(
        json.dumps(report_obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    summary = {
        "count": report_obj["count"],
        "passed": report_obj["passed"],
        "failed": failed,
        "report": str(args.output.resolve()),
    }
    print(json.dumps(summary, ensure_ascii=False))
    raise SystemExit(0 if not failed else 1)


if __name__ == "__main__":
    main()
