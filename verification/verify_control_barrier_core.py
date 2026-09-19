#!/usr/bin/env python3
"""Hand-checkable verification for Control Barrier Functions (Milestone 16).

Checks (all numbers from this script run):
  1. Example A: x=0.2; u=-0.1 → margin 0.1 safe; u=-0.3 → margin -0.1 unsafe
  2. Example B: x=0.5; u=-0.2 → margin 0.3 safe; u=-0.6 → margin -0.1 unsafe
  3. admissible_controls_cbf: at x=0.2, u_min=-0.2 (constraint u+x>=0)
  4. nonlinear alpha refused; non-identity h refused; DOIs in source

Stdlib only (math). JSON {count, passed, failed, report}; numbers from this run.
Does not import or mutate viability.core / has_safe_transfer.
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
from scoped_correspondence.viability.control_barrier import (  # noqa: E402
    ALPHA_LINEAR,
    SOURCE,
    BarrierCertificate,
    BarrierFunction,
    admissible_controls_cbf,
    cbf_condition,
    make_identity_barrier,
    verify_forward_invariance,
)


def require(ok, msg):
    if not bool(ok):
        raise AssertionError(msg)


def near(a, b, atol=1e-12, rtol=1e-9):
    if not math.isclose(float(a), float(b), abs_tol=atol, rel_tol=rtol):
        raise AssertionError(f"{a!r} != {b!r}")


def check_example_a():
    """x=0.2: u=-0.1 → margin 0.1 safe; u=-0.3 → margin -0.1 unsafe."""
    barrier = make_identity_barrier()
    x = 0.2

    # Direct cbf_condition (L_f=0, L_g=1, alpha_h=h(x)=x)
    m_safe = cbf_condition(0.0, 1.0, -0.1, x)
    m_unsafe = cbf_condition(0.0, 1.0, -0.3, x)
    near(m_safe, 0.1)
    near(m_unsafe, -0.1)

    cert_safe = verify_forward_invariance(barrier, x, -0.1)
    cert_unsafe = verify_forward_invariance(barrier, x, -0.3)
    require(isinstance(cert_safe, BarrierCertificate), "type safe")
    require(isinstance(cert_unsafe, BarrierCertificate), "type unsafe")
    near(cert_safe.margin, 0.1)
    near(cert_unsafe.margin, -0.1)
    require(cert_safe.safe is True, f"safe flag={cert_safe.safe}")
    require(cert_unsafe.safe is False, f"unsafe flag={cert_unsafe.safe}")
    near(cert_safe.margin, cert_safe.u + cert_safe.x)
    require("10.1109/TAC.2016.2638961" in cert_safe.source, "2017 DOI")
    require("10.23919/ECC.2019.8796030" in cert_safe.source, "2019 DOI")

    return {
        "x": x,
        "u_safe": -0.1,
        "margin_safe": cert_safe.margin,
        "safe": cert_safe.safe,
        "u_unsafe": -0.3,
        "margin_unsafe": cert_unsafe.margin,
        "unsafe_flag": cert_unsafe.safe,
        "constraint": "u + x >= 0",
        "source": cert_safe.source,
    }


def check_example_b():
    """Cross-check: x=0.5; u=-0.2 → 0.3 safe; u=-0.6 → -0.1 unsafe."""
    barrier = make_identity_barrier()
    x = 0.5
    cert_safe = verify_forward_invariance(barrier, x, -0.2)
    cert_unsafe = verify_forward_invariance(barrier, x, -0.6)
    near(cert_safe.margin, 0.3)
    near(cert_unsafe.margin, -0.1)
    require(cert_safe.safe is True, "B safe")
    require(cert_unsafe.safe is False, "B unsafe")

    adm = admissible_controls_cbf(barrier, x)
    near(adm["u_min"], -0.5)
    require(adm["constraint"] == "u + x >= 0", adm["constraint"])

    return {
        "x": x,
        "u_safe": -0.2,
        "margin_safe": cert_safe.margin,
        "safe": cert_safe.safe,
        "u_unsafe": -0.6,
        "margin_unsafe": cert_unsafe.margin,
        "unsafe_flag": cert_unsafe.safe,
        "u_min": adm["u_min"],
        "constraint": adm["constraint"],
    }


def check_admissible_at_x02():
    """At x=0.2, admissible set is u >= -0.2."""
    barrier = make_identity_barrier()
    adm = admissible_controls_cbf(barrier, 0.2)
    near(adm["u_min"], -0.2)
    near(adm["L_f_h"], 0.0)
    near(adm["L_g_h"], 1.0)
    near(adm["h_x"], 0.2)
    near(adm["alpha_h"], 0.2)
    require(adm["constraint"] == "u + x >= 0", adm["constraint"])
    require(adm["dynamics"] == "x_dot = u", adm["dynamics"])
    # Boundary control u = u_min is safe (margin 0)
    cert_boundary = verify_forward_invariance(barrier, 0.2, adm["u_min"])
    near(cert_boundary.margin, 0.0)
    require(cert_boundary.safe is True, "boundary safe")
    return {
        "x": 0.2,
        "u_min": adm["u_min"],
        "L_f_h": adm["L_f_h"],
        "L_g_h": adm["L_g_h"],
        "boundary_margin": cert_boundary.margin,
        "boundary_safe": cert_boundary.safe,
        "constraint": adm["constraint"],
    }


def check_nonlinear_alpha_refused():
    """Nonlinear alpha and non-linear alpha_kind must raise."""
    raised = False
    err = ""
    try:
        BarrierFunction(h=lambda x: float(x), alpha=lambda r: r ** 3)
    except ScopeViolationError as exc:
        raised = True
        err = str(exc)
    require(raised, "expected ScopeViolationError for alpha(r)=r**3")
    require("linear" in err.lower() or "alpha" in err.lower(), err)

    raised2 = False
    try:
        BarrierFunction(
            h=lambda x: float(x),
            alpha=lambda r: float(r),
            alpha_kind="cubic",
        )
    except ScopeViolationError:
        raised2 = True
    require(raised2, "alpha_kind='cubic' must raise")

    # Non-identity h refused at CONSTRUCTION (audit finding A06: a barrier
    # like h(x)=1-x can match h(x)=x at one evaluation point -- e.g. at
    # x=0.5 -- without being the identity function; the old code only
    # checked pointwise inside verify_forward_invariance/admissible_
    # controls_cbf on whatever x a caller later passed, which such a
    # non-identity h can pass by accident. Checked structurally on
    # multiple probe points at construction time instead, same pattern
    # already used for alpha).
    raised3 = False
    try:
        BarrierFunction(
            h=lambda x: float(x) - 1.0,  # h(x)=x-1 != identity
            alpha=lambda r: float(r),
        )
    except ScopeViolationError as exc:
        raised3 = True
        require("identity" in str(exc).lower() or "h(x)=x" in str(exc), str(exc))
    require(raised3, "non-identity h must raise at BarrierFunction construction")

    # A barrier that only coincidentally matches h(x)=x at ONE point
    # (h(x)=1-x matches at x=0.5) must also be refused.
    raised4 = False
    try:
        BarrierFunction(h=lambda x: 1.0 - float(x), alpha=lambda r: float(r))
    except ScopeViolationError as exc:
        raised4 = True
        require("identity" in str(exc).lower() or "h(x)=x" in str(exc), str(exc))
    require(raised4, "h(x)=1-x (matches h(x)=x only at x=0.5) must still raise")

    require(ALPHA_LINEAR == "linear", ALPHA_LINEAR)
    require("10.1109/TAC.2016.2638961" in SOURCE, SOURCE)
    require("10.23919/ECC.2019.8796030" in SOURCE, SOURCE)

    return {
        "nonlinear_alpha_raises": True,
        "alpha_kind_cubic_raises": True,
        "non_identity_h_raises": True,
        "alpha_kind_canonical": ALPHA_LINEAR,
        "source_has_2017_doi": True,
        "source_has_2019_doi": True,
    }


CHECKS = [
    ("example_a_x0p2_margins", check_example_a),
    ("example_b_x0p5_crosscheck", check_example_b),
    ("admissible_controls_x0p2", check_admissible_at_x02),
    ("nonlinear_alpha_and_scope", check_nonlinear_alpha_refused),
]


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument(
        "--json-out",
        type=Path,
        default=Path(__file__).with_name("verify_control_barrier_core_results.json"),
    )
    args = p.parse_args(argv)

    report = {
        "milestone": "M16 Control Barrier Functions",
        "timestamp": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "checks": {},
        "source_doi_2017": "10.1109/TAC.2016.2638961",
        "source_doi_2019": "10.23919/ECC.2019.8796030",
        "disclaimer": (
            "Scalar zeroing CBF only (x_dot=u, h(x)=x, alpha(r)=r). "
            "No QP, no multi-D, no nonlinear alpha. Does not call or "
            "redefine has_safe_transfer (viability/core.py untouched)."
        ),
        "untouched": [
            "src/scoped_correspondence/viability/core.py",
            "src/scoped_correspondence/__init__.py",
            "FORMALISM.md",
            "has_safe_transfer linkage",
            "multi-D / nonlinear alpha / QP solver",
        ],
    }
    passed = 0
    failed = 0
    errors = []
    for name, fn in CHECKS:
        try:
            report["checks"][name] = {"status": "passed", "detail": fn()}
            passed += 1
            print(f"PASS  {name}")
        except Exception as exc:  # noqa: BLE001 — collect all failures
            failed += 1
            errors.append({"check": name, "error": f"{type(exc).__name__}: {exc}"})
            report["checks"][name] = {
                "status": "failed",
                "error": f"{type(exc).__name__}: {exc}",
            }
            print(f"FAIL  {name}: {exc}")

    summary = {
        "count": len(CHECKS),
        "passed": passed,
        "failed": failed,
        "errors": errors,
        "report": report,
    }
    args.json_out.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(f"\n{passed}/{len(CHECKS)} passed; wrote {args.json_out}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
