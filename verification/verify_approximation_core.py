#!/usr/bin/env python3
"""Hand-checkable verification for Approximation Certificates (Milestone 10).

Checks (all numbers from this script run):
  1. Worked example eps=0.1  → ok True  (analytic flows; max_residual <= 0.1)
  2. Worked example eps=0.05 → ok False (max_residual approaches 0.1)
  3. Zero-error identical flows → max_residual == 0, any eps>=0 ok True

Stdlib + NumPy. JSON {count, passed, failed, report}; numbers from this run.
Calls real Correspondence.conjugacy_residual / verify_conjugacy via
verify_approximate_simulation (contract.py unchanged).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import platform
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from scoped_correspondence.correspondence import (  # noqa: E402
    FIXED_MAP_BOUND,
    ApproximationCertificate,
    Correspondence,
    ModelRef,
    Scope,
    StateMap,
    verify_approximate_simulation,
)


def require(ok, msg):
    if not bool(ok):
        raise AssertionError(msg)


def near(a, b, atol=1e-12, rtol=1e-9):
    if not np.allclose(a, b, atol=atol, rtol=rtol):
        raise AssertionError(f"{a!r} != {b!r}")


def _identity_map(x):
    return x


def build_decay_offset_correspondence():
    """ẋ=-x, ẏ=-y+0.1, x(0)=y(0)=0 — analytic flows, identity T.

    Exact: x(t)=x0*e^{-t}; y(t)=0.1+(y0-0.1)*e^{-t}.
    From 0: x(t)=0, y(t)=0.1(1-e^{-t}).
    """

    def source_flow(state, time):
        x0 = float(state)
        return x0 * math.exp(-float(time))

    def target_flow(state, time):
        y0 = float(state)
        t = float(time)
        return 0.1 + (y0 - 0.1) * math.exp(-t)

    scope = Scope(
        description="decay vs offset-decay, identity T, t in [0,10]",
        assumptions=(
            "analytic exact solutions (no numerical ODE integrate)",
            "StateMap identity — fixed_map_bound specialty only",
        ),
        time_horizon=(0.0, 10.0),
    )
    return Correspondence(
        source=ModelRef(name="decay", flow=source_flow, notes="dx/dt=-x"),
        target=ModelRef(
            name="offset_decay", flow=target_flow, notes="dy/dt=-y+0.1"
        ),
        state_map=StateMap(map_fn=_identity_map, name="identity"),
        scope=scope,
    )


def build_identical_flow_correspondence():
    """Identical source/target flows → exact conjugacy with identity T."""

    def flow(state, time):
        return float(state) * math.exp(-float(time))

    scope = Scope(
        description="identical decay flows, identity T",
        assumptions=("source.flow == target.flow",),
        time_horizon=(0.0, 5.0),
    )
    return Correspondence(
        source=ModelRef(name="decay_L", flow=flow),
        target=ModelRef(name="decay_R", flow=flow),
        state_map=StateMap(map_fn=_identity_map, name="identity"),
        scope=scope,
    )


def check_eps_0_1_ok():
    """epsilon=0.1 → ok True for t in [0,10] grid."""
    corr = build_decay_offset_correspondence()
    times = list(np.linspace(0.0, 10.0, 101))
    states = [0.0]
    cert = verify_approximate_simulation(corr, states, times, epsilon=0.1)

    require(isinstance(cert, ApproximationCertificate), "type")
    require(cert.relation_kind == FIXED_MAP_BOUND, "relation_kind fixed_map_bound")
    require(cert.relation_kind not in ("simulation", "bisimulation"), "not sim/bisim")
    require(cert.epsilon == 0.1, "epsilon recorded")
    require(cert.ok is True, f"ok True expected; max_residual={cert.max_residual}")
    require(cert.max_residual <= 0.1, f"max_residual={cert.max_residual} <= 0.1")
    # Analytic: at t=10, r=0.1*(1-exp(-10))
    analytic_at_10 = 0.1 * (1.0 - math.exp(-10.0))
    require(
        cert.max_residual >= analytic_at_10 - 1e-15,
        "max_residual should reach near asymptotic bound on [0,10]",
    )
    near(cert.max_residual, analytic_at_10, atol=1e-12)
    require(
        "Girard" in cert.source and "10.1109/TAC.2007.895849" in cert.source,
        "source cites Girard & Pappas DOI",
    )
    require(
        any("NOT prove" in a or "does NOT prove" in a for a in cert.assumptions),
        "disclaimer in assumptions",
    )
    # Cross-check one residual via conjugacy_residual directly
    r_direct = corr.conjugacy_residual(0.0, 10.0)
    near(r_direct.value, analytic_at_10, atol=1e-12)

    return {
        "epsilon": cert.epsilon,
        "ok": cert.ok,
        "max_residual": cert.max_residual,
        "analytic_residual_at_t10": analytic_at_10,
        "relation_kind": cert.relation_kind,
        "n_residuals": len(cert.residuals),
        "source": cert.source,
        "direct_conjugacy_residual_t10": r_direct.value,
    }


def check_eps_0_05_fail():
    """epsilon=0.05 → ok False (approaches 0.1)."""
    corr = build_decay_offset_correspondence()
    times = list(np.linspace(0.0, 10.0, 101))
    states = [0.0]
    cert = verify_approximate_simulation(corr, states, times, epsilon=0.05)

    require(cert.ok is False, f"ok False expected; max_residual={cert.max_residual}")
    require(cert.max_residual > 0.05, f"max_residual={cert.max_residual} > 0.05")
    require(cert.epsilon == 0.05, "epsilon recorded")
    require(cert.relation_kind == FIXED_MAP_BOUND, "relation_kind")
    analytic_at_10 = 0.1 * (1.0 - math.exp(-10.0))
    near(cert.max_residual, analytic_at_10, atol=1e-12)

    return {
        "epsilon": cert.epsilon,
        "ok": cert.ok,
        "max_residual": cert.max_residual,
        "analytic_residual_at_t10": analytic_at_10,
        "relation_kind": cert.relation_kind,
        "n_residuals": len(cert.residuals),
    }


def check_zero_error_identical():
    """Identical flows → max_residual==0, any eps>=0 ok True."""
    corr = build_identical_flow_correspondence()
    times = list(np.linspace(0.0, 5.0, 21))
    states = [0.0, 1.0, -0.5]
    out = {}
    for eps in (0.0, 1e-12, 0.1, 1.0):
        cert = verify_approximate_simulation(corr, states, times, epsilon=eps)
        require(cert.max_residual == 0.0, f"max_residual==0 got {cert.max_residual}")
        require(cert.ok is True, f"ok True for eps={eps}")
        require(cert.relation_kind == FIXED_MAP_BOUND, "relation_kind")
        out[f"eps_{eps}"] = {
            "epsilon": cert.epsilon,
            "ok": cert.ok,
            "max_residual": cert.max_residual,
            "n_residuals": len(cert.residuals),
        }
    # Also confirm verify_conjugacy exact ok under default metric
    report = corr.verify_conjugacy(states, times)
    require(report.ok is True, "exact conjugacy ok")
    require(report.max_residual == 0.0, "exact max_residual 0")
    out["verify_conjugacy_ok"] = report.ok
    out["verify_conjugacy_max_residual"] = report.max_residual
    return out


CHECKS = [
    ("eps_0_1_ok", check_eps_0_1_ok),
    ("eps_0_05_fail", check_eps_0_05_fail),
    ("zero_error_identical", check_zero_error_identical),
]


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument(
        "--json-out",
        type=Path,
        default=Path(__file__).with_name("verify_approximation_core_results.json"),
    )
    args = p.parse_args(argv)

    report = {
        "milestone": "M10 Approximation Certificates",
        "timestamp": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "numpy": np.__version__,
        "checks": {},
        "source_doi": "10.1109/TAC.2007.895849",
        "relation_kind": FIXED_MAP_BOUND,
        "disclaimer": (
            "Certificate does NOT prove existence of a general simulation "
            "relation — fixed StateMap T specialty only "
            "(analogous to check_generic_structure disclaimer)."
        ),
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
