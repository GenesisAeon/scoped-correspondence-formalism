#!/usr/bin/env python3
"""Hand-checkable verification for Pattern Formation / Turing (Milestone 30).

Checks (all numbers from this script run):
  1. schnakenberg_1979_steady_state(0.1, 0.9): u*=1.0, v*=0.9;
     J f_u=0.8, f_v=1.0, g_u=-1.8, g_v=-1.0; tr=-0.2, det=1.0;
     jacobian_stability True
  2. D_u=1: solve 0.64 D_v^2 - 5.6 D_v + 1 = 0 → D_v_c≈8.567627 (larger),
     smaller≈0.182373; at D_v_c both k_c^2 formulas ≈0.341641 agree;
     turing_conditions True for D_v=1.2*D_v_c
  3. Dispersion at k_c: D_v=0.99*D_v_c → Re<0; D_v_c → Re≈0;
     D_v=1.2*D_v_c → Re>0
  4. Control D_v=1 → turing_conditions fails (iv) [also (iii)]
  5. Both mandatory warnings verbatim in module/API docstrings AND JSON;
     SOURCE cites Turing/Schnakenberg 1979/Murray; no PDE solver

Stdlib only (math). JSON {count, passed, failed, report}; numbers from this run.
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

from scoped_correspondence.errors import ScopeViolationError  # noqa: E402
from scoped_correspondence.pattern_formation.core import (  # noqa: E402
    DYNAMICS_BRIDGE_WARNING,
    SCHNAKENBERG_PAPER_WARNING,
    SOURCE,
    critical_diffusivity_roots_schnakenberg,
    dispersion_relation,
    jacobian_stability,
    schnakenberg_1979_steady_state,
    turing_conditions,
)
import scoped_correspondence.pattern_formation.core as pf_core  # noqa: E402


def require(ok, msg):
    if not bool(ok):
        raise AssertionError(msg)


def near(a, b, atol=1e-9, rtol=1e-9):
    if not math.isclose(float(a), float(b), abs_tol=atol, rel_tol=rtol):
        raise AssertionError(f"{a!r} != {b!r} (atol={atol}, rtol={rtol})")


def check_schnakenberg_steady_state():
    """a=0.1, b=0.9 → u*=1, v*=0.9; J and tr/det as specified."""
    a, b = 0.1, 0.9
    ss = schnakenberg_1979_steady_state(a, b)
    near(ss.u_star, 1.0)
    near(ss.v_star, 0.9)
    near(ss.f_u, 0.8)
    near(ss.f_v, 1.0)
    near(ss.g_u, -1.8)
    near(ss.g_v, -1.0)
    near(ss.trace, -0.2)
    near(ss.det, 1.0)

    J = ss.jacobian
    stab = jacobian_stability(J)
    require(stab.stable is True, "homogeneous must be stable")
    near(stab.trace, -0.2)
    near(stab.det, 1.0)
    require(stab.condition_trace_neg is True, "tr<0")
    require(stab.condition_det_pos is True, "det>0")

    raised = False
    try:
        schnakenberg_1979_steady_state(-1.0, -1.0)
    except ScopeViolationError:
        raised = True
    require(raised, "a+b<=0 must raise ScopeViolationError")

    return {
        "a": a,
        "b": b,
        "u_star": ss.u_star,
        "v_star": ss.v_star,
        "f_u": ss.f_u,
        "f_v": ss.f_v,
        "g_u": ss.g_u,
        "g_v": ss.g_v,
        "trace": ss.trace,
        "det": ss.det,
        "jacobian_stable": stab.stable,
        "a_plus_b_le_0_raises": raised,
        "paper_warning_on_result": ss.paper_warning,
        "dynamics_bridge_warning_on_result": ss.dynamics_bridge_warning,
    }


def check_critical_Dv_and_kc():
    """Quadratic 0.64 Dv^2 - 5.6 Dv + 1 = 0; kc^2 both formulas agree."""
    a, b, Du = 0.1, 0.9, 1.0
    ss = schnakenberg_1979_steady_state(a, b)
    roots = critical_diffusivity_roots_schnakenberg(a, b, Du)
    # Coefficients for documentation: A=f_u^2=0.64, B=2*f_u*Du*g_v-4*Du*det=-5.6
    near(roots["A"], 0.64)
    near(roots["B"], -5.6)
    near(roots["C"], 1.0)
    Dv_c = roots["D_v_c"]
    Dv_lo = roots["D_v_smaller"]
    near(Dv_c, 8.567627457812105, atol=1e-9)
    near(Dv_lo, 0.18237254218789398, atol=1e-9)
    # Verify quadratic residual
    for Dv in (Dv_c, Dv_lo):
        near(0.64 * Dv * Dv - 5.6 * Dv + 1.0, 0.0, atol=1e-10)

    tc = turing_conditions(ss.jacobian, Du, Dv_c)
    require(tc.condition_i_trace_neg is True, "(i)")
    require(tc.condition_ii_det_pos is True, "(ii)")
    require(tc.condition_iii_diffusive is True, "(iii) at larger root")
    # At equality (iv) is NOT strictly >; turing_unstable False at exact critical
    require(tc.condition_iv_discriminant is False, "(iv) equality → not strict")
    require(tc.k_c_sq is not None, "k_c_sq defined")
    require(tc.k_c_sq_from_det is not None, "k_c_sq_from_det defined")
    near(tc.k_c_sq, 0.34164078649987384, atol=1e-9)
    near(tc.k_c_sq_from_det, 0.34164078649987384, atol=1e-9)
    near(tc.k_c_sq, tc.k_c_sq_from_det, atol=1e-12)
    require(tc.k_c_sq_agree is True, "k_c^2 formulas must agree at criticality")

    # Slightly above critical → Turing unstable
    tc_above = turing_conditions(ss.jacobian, Du, 1.2 * Dv_c)
    require(tc_above.turing_unstable is True, "1.2*Dv_c must be Turing-unstable")

    # Smaller root fails (iii)
    tc_lo = turing_conditions(ss.jacobian, Du, Dv_lo)
    require(tc_lo.condition_iii_diffusive is False, "smaller root fails (iii)")

    return {
        "quadratic": "0.64*D_v^2 - 5.6*D_v + 1 = 0",
        "A": roots["A"],
        "B": roots["B"],
        "C": roots["C"],
        "D_v_c_larger": Dv_c,
        "D_v_smaller": Dv_lo,
        "k_c_sq": tc.k_c_sq,
        "k_c_sq_from_det": tc.k_c_sq_from_det,
        "k_c_sq_agree": tc.k_c_sq_agree,
        "turing_at_critical_strict_iv": tc.condition_iv_discriminant,
        "turing_unstable_at_1_2_Dv_c": tc_above.turing_unstable,
        "smaller_root_fails_iii": not tc_lo.condition_iii_diffusive,
    }


def check_dispersion_across_criticality():
    """Re(lambda_max) at k_c: stable / marginal / unstable."""
    a, b, Du = 0.1, 0.9, 1.0
    ss = schnakenberg_1979_steady_state(a, b)
    roots = critical_diffusivity_roots_schnakenberg(a, b, Du)
    Dv_c = roots["D_v_c"]
    # Use critical k from the critical D_v (onset wave number)
    tc_c = turing_conditions(ss.jacobian, Du, Dv_c)
    k_c = math.sqrt(tc_c.k_c_sq)

    cases = {}
    for label, factor in (("below_0_99", 0.99), ("critical", 1.0), ("above_1_2", 1.2)):
        Dv = factor * Dv_c
        # Evaluate at the critical onset k_c (fixed) for clean crossing
        d = dispersion_relation(ss.jacobian, Du, Dv, k_c)
        cases[label] = {
            "D_v": Dv,
            "factor": factor,
            "k": k_c,
            "re_lambda_max": d.re_lambda_max,
        }

    require(cases["below_0_99"]["re_lambda_max"] < 0.0, "0.99*Dv_c must be stable Re<0")
    near(cases["critical"]["re_lambda_max"], 0.0, atol=1e-9)
    require(cases["above_1_2"]["re_lambda_max"] > 0.0, "1.2*Dv_c must be unstable Re>0")

    raised = False
    try:
        dispersion_relation(ss.jacobian, Du, Dv_c, -1.0)
    except ScopeViolationError:
        raised = True
    require(raised, "k<0 must raise")

    return {
        "k_c": k_c,
        "k_c_sq": tc_c.k_c_sq,
        "D_v_c": Dv_c,
        "cases": cases,
        "k_neg_raises": raised,
    }


def check_control_Dv_eq_1():
    """Control: D_v=1 → Turing fails (iv); also fails (iii)."""
    a, b, Du = 0.1, 0.9, 1.0
    ss = schnakenberg_1979_steady_state(a, b)
    tc = turing_conditions(ss.jacobian, Du, 1.0)
    require(tc.condition_i_trace_neg is True, "(i) still holds")
    require(tc.condition_ii_det_pos is True, "(ii) still holds")
    require(tc.condition_iii_diffusive is False, "(iii) fails at Dv=1")
    require(tc.condition_iv_discriminant is False, "(iv) fails at Dv=1")
    require(tc.turing_unstable is False, "not Turing-unstable")
    near(tc.h, -0.2)
    return {
        "D_u": Du,
        "D_v": 1.0,
        "h": tc.h,
        "condition_i": tc.condition_i_trace_neg,
        "condition_ii": tc.condition_ii_det_pos,
        "condition_iii": tc.condition_iii_diffusive,
        "condition_iv": tc.condition_iv_discriminant,
        "turing_unstable": tc.turing_unstable,
        "fails_iv": not tc.condition_iv_discriminant,
    }


def check_warnings_and_sources():
    """Both mandatory warnings verbatim; SOURCE; no PDE claims."""
    w1 = SCHNAKENBERG_PAPER_WARNING
    w2 = DYNAMICS_BRIDGE_WARNING
    require(
        w1
        == (
            "Schnakenberg 1979 (J Theor Biol) is a DIFFERENT paper than "
            "Schnakenberg 1976 (Rev Mod Phys) used in thermo/schnakenberg.py (M18) — "
            "different journal/year/claim; do not mix modules."
        ),
        "SCHNAKENBERG_PAPER_WARNING must be verbatim",
    )
    require(
        w2
        == (
            "A future correspondence bridge to dynamics is structurally conceivable "
            "(Turing S_rec(k) would generalize dynamics.recovery_rate_at_equilibrium "
            "as S_rec(0)) but is NOT claimed or implemented here; a real conjugacy "
            "would need the correspondence contract with its own proof."
        ),
        "DYNAMICS_BRIDGE_WARNING must be verbatim",
    )

    mod_doc = pf_core.__doc__ or ""
    require(w1 in mod_doc, "paper warning missing from module docstring")
    require(w2 in mod_doc, "bridge warning missing from module docstring")

    tc_doc = turing_conditions.__doc__ or ""
    require(w1 in tc_doc, "paper warning missing from turing_conditions docstring")
    require(w2 in tc_doc, "bridge warning missing from turing_conditions docstring")

    ss_doc = schnakenberg_1979_steady_state.__doc__ or ""
    require(w1 in ss_doc, "paper warning missing from schnakenberg_1979 docstring")

    disp_doc = dispersion_relation.__doc__ or ""
    require(w2 in disp_doc, "bridge warning missing from dispersion_relation docstring")

    require("10.1098/rstb.1952.0012" in SOURCE, "Turing DOI")
    require("10.1016/0022-5193(79)90042-0" in SOURCE, "Schnakenberg 1979 DOI")
    require("10.1007/b98869" in SOURCE, "Murray DOI")
    require("1976" not in SOURCE or "Schnakenberg 1979" in SOURCE, "SOURCE ok")

    # No PDE solver / spatial simulation in this module's public API names
    public = [n for n in dir(pf_core) if not n.startswith("_")]
    forbidden_names = {"solve_pde", "simulate", "finite_difference", "fft_rd"}
    require(
        not (forbidden_names & set(public)),
        f"forbidden PDE API leaked: {forbidden_names & set(public)}",
    )

    return {
        "SCHNAKENBERG_PAPER_WARNING": w1,
        "DYNAMICS_BRIDGE_WARNING": w2,
        "SOURCE": SOURCE,
        "warnings_in_module_doc": True,
        "warnings_in_api_docs": True,
        "no_pde_solver_api": True,
    }


CHECKS = [
    ("schnakenberg_steady_state", check_schnakenberg_steady_state),
    ("critical_Dv_and_kc", check_critical_Dv_and_kc),
    ("dispersion_across_criticality", check_dispersion_across_criticality),
    ("control_Dv_eq_1", check_control_Dv_eq_1),
    ("warnings_and_sources", check_warnings_and_sources),
]


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument(
        "--json-out",
        type=Path,
        default=Path(__file__).with_name("verify_pattern_formation_core_results.json"),
    )
    args = p.parse_args(argv)

    report = {
        "milestone": 30,
        "module": "pattern_formation",
        "started_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "platform": platform.platform(),
        "python": sys.version,
        "checks": {},
        "SCHNAKENBERG_PAPER_WARNING": SCHNAKENBERG_PAPER_WARNING,
        "DYNAMICS_BRIDGE_WARNING": DYNAMICS_BRIDGE_WARNING,
        "SOURCE": SOURCE,
    }
    passed = 0
    failed = 0
    errors = []
    for name, fn in CHECKS:
        try:
            report["checks"][name] = {"ok": True, "data": fn()}
            passed += 1
            print(f"PASS  {name}")
        except Exception as exc:  # noqa: BLE001 — collect all failures
            failed += 1
            report["checks"][name] = {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
            errors.append(f"{name}: {exc}")
            print(f"FAIL  {name}: {exc}")

    summary = {
        "count": len(CHECKS),
        "passed": passed,
        "failed": failed,
        "report": report,
    }
    args.json_out.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"\n{passed}/{len(CHECKS)} passed; results → {args.json_out}")
    if failed:
        print("FAILURES:")
        for e in errors:
            print(" ", e)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
