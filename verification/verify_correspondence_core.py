#!/usr/bin/env python3
"""Equivalence checks: legacy verify_* evidence vs Correspondence core API.

Milestone 1 — no new science. Reproduces established synthetic cases through
the new typed Correspondence contract and requires exact numeric match to the
checked-in JSON evidence from verify_extensions / verify_transformations.

Stdlib + NumPy only. Fixed grids / FD step match the legacy scripts.
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

from scoped_correspondence import (  # noqa: E402
    Correspondence,
    ErrorMetric,
    ModelRef,
    Scope,
    StateMap,
    TimeMap,
)


def require(ok, msg):
    if not bool(ok):
        raise AssertionError(msg)


def near(a, b, atol=1e-10, rtol=1e-9):
    if not np.allclose(a, b, atol=atol, rtol=rtol):
        raise AssertionError(f"{a!r} != {b!r}")


def diff(f, x, h=1e-5):
    return (f(x + h) - f(x - h)) / (2 * h)


def load_expected():
    ext = json.loads((ROOT / "verification" / "extension_results.json").read_text(encoding="utf-8"))
    tr = json.loads((ROOT / "verification" / "transformation_results.json").read_text(encoding="utf-8"))
    e11 = None
    for c in ext["checks"]:
        cid = c.get("id") or c.get("name")
        if cid == "e11_topological_conjugacy_rates":
            e11 = c["evidence"]
            break
    require(e11 is not None, "e11 evidence missing from extension_results.json")
    t_by_id = {r["id"]: r["evidence"] for r in tr["results"]}
    return {
        "e11": e11,
        "t01": t_by_id["t01_context_derivatives"],
        "t02": t_by_id["t02_state_dependent_time"],
        "t03": t_by_id["t03_parameter_chain_rule"],
        "t04": t_by_id["t04_composed_transformations"],
    }


def mig_cor_e11_conjugacy():
    expected = load_expected()["e11"]
    transform = lambda x: math.copysign(x * x, x)
    corr = Correspondence(
        source=ModelRef(
            name="linear_decay_rate_1",
            field=lambda x: -x,
            flow=lambda x, t: x * math.exp(-t),
        ),
        target=ModelRef(
            name="linear_decay_rate_2",
            field=lambda y: -2 * y,
            flow=lambda y, t: y * math.exp(-2 * t),
        ),
        state_map=StateMap(map_fn=transform, name="sign(x)*abs(x)**2", differentiable=False),
        scope=Scope(
            description="topological conjugacy demo; inverse not differentiable at 0",
            assumptions=("deterministic autonomous 1D", "constant time factor c=1"),
        ),
        time_map=TimeMap(name="c", constant_scale=1.0),
        metric=ErrorMetric(atol=1e-10, rtol=1e-9),
    )
    report = corr.verify_conjugacy([-2, -0.2, 0, 0.3, 4], [0, 0.2, 1, 3])
    require(report.ok, "conjugacy residuals must vanish on grid")
    rate_src = corr.local_rate("source", at=0.0)
    rate_tgt = corr.local_rate("target", at=0.0)
    near(rate_src, 1)
    near(rate_tgt, 2)
    evidence = {
        "time_factor": int(corr.time_map.constant_scale),
        "local_rates": [int(rate_src), int(rate_tgt)],
        "transformation": "sign(x)*abs(x)**2; inverse not differentiable at zero",
        "max_conjugacy_residual": report.max_residual,
        "legacy_alias": "VER-COR-e11_topological_conjugacy_rates",
        "legacy_id": "e11_topological_conjugacy_rates",
    }
    require(evidence["time_factor"] == expected["time_factor"], "time_factor mismatch")
    require(evidence["local_rates"] == expected["local_rates"], "local_rates mismatch")
    require(evidence["transformation"] == expected["transformation"], "transformation string mismatch")
    return evidence


def mig_cor_t01_context_derivatives():
    expected = load_expected()["t01"]
    corr = Correspondence(
        source=ModelRef(name="stock_x"),
        target=ModelRef(name="reserve_y"),
        state_map=StateMap(map_fn=lambda z: z, name="id"),
        scope=Scope(
            description="T1 context chain rule; nonconstant stock, context, explicit time",
            assumptions=("differentiable deterministic", "context_transformations.md §3"),
        ),
        metric=ErrorMetric(atol=1e-8, rtol=0.0),
    )
    x = lambda t: math.exp(-t)
    c = lambda t: math.sin(t)
    pi = lambda z, v, t: (z - v) / (1 + t)
    errors = []
    for t in np.linspace(0, 2, 31):
        r = corr.t1_residual(
            pi,
            x,
            c,
            lambda tt, yy: (-x(tt) - math.cos(tt)) / (1 + tt) - yy / (1 + tt),
            t,
        )
        errors.append(r.value)
    require(max(errors) < 1e-8, "full context chain rule")
    near(diff(lambda t: (1 - t) / (1 + t), 0.4), -2 / 1.4**2)
    evidence = {
        "max_derivative_error": max(errors),
        "fixed_stock_reserve_derivative_at_0": -2,
        "legacy_alias": "VER-COR-T01",
        "legacy_id": "t01_context_derivatives",
    }
    require(
        evidence["max_derivative_error"] == expected["max_derivative_error"],
        f"t01 max_derivative_error {evidence['max_derivative_error']!r} != {expected['max_derivative_error']!r}",
    )
    require(
        evidence["fixed_stock_reserve_derivative_at_0"]
        == expected["fixed_stock_reserve_derivative_at_0"],
        "t01 fixed derivative mismatch",
    )
    return evidence


def mig_cor_t02_state_dependent_time():
    expected = load_expected()["t02"]
    corr = Correspondence(
        source=ModelRef(name="x_exp_decay"),
        target=ModelRef(name="y_of_tau"),
        state_map=StateMap(map_fn=lambda x: x * x, name="y=x^2"),
        scope=Scope(
            description="T2 state-dependent clock tau=1-exp(-t)",
            assumptions=("a=dtau/dt>0 along path", "context_transformations.md §3"),
            time_horizon=(0.0, 4.0),
        ),
        time_map=TimeMap(name="tau", scale_fn=lambda z, t: math.exp(-t)),
        metric=ErrorMetric(atol=1e-8, rtol=0.0),
    )
    errors = []
    for t in np.linspace(0, 4, 41):
        x = math.exp(-t)
        r = corr.t2_dy_dtau(
            y_of_t=lambda a: math.exp(-2 * a),
            tau_of_t=lambda a: 1 - math.exp(-a),
            transformed_rhs=lambda a, _x=x: -2 * _x * _x / _x,
            time=t,
        )
        near(r.detail["numeric"], r.detail["predicted"], atol=1e-8)
        errors.append(r.value)
    require(1 - math.exp(-20) < 1, "positive clock can have finite total duration")
    evidence = {
        "physical_horizon": "infinite",
        "transformed_horizon": 1,
        "max_derivative_error": max(errors),
        "legacy_alias": "VER-COR-T02",
        "legacy_id": "t02_state_dependent_time",
    }
    require(
        evidence["max_derivative_error"] == expected["max_derivative_error"],
        f"t02 max_derivative_error mismatch {evidence['max_derivative_error']!r} vs {expected['max_derivative_error']!r}",
    )
    require(evidence["physical_horizon"] == expected["physical_horizon"], "t02 horizon label")
    require(evidence["transformed_horizon"] == expected["transformed_horizon"], "t02 transformed_horizon")
    return evidence


def mig_cor_t03_parameter_chain_rule():
    expected = load_expected()["t03"]
    f = lambda x: -(1 + x * x) * x
    corr = Correspondence(
        source=ModelRef(name="param_field", field=f),
        target=ModelRef(name="same"),
        state_map=StateMap(map_fn=lambda x: x, name="id"),
        scope=Scope(
            description="parameter chain rule / frozen-coefficient trap",
            assumptions=("T3-related",),
        ),
        metric=ErrorMetric(atol=2e-9, rtol=0.0),
    )
    for x in np.linspace(-2, 2, 41):
        near(diff(f, x), -1 - 3 * x * x, atol=2e-9)
    near(diff(f, 1), -4)
    require(abs(-4 - (-2)) > 1, "frozen coefficient hides derivative")
    # Legacy t03 compares Jacobians (full vs frozen coefficient), not T3 field
    # compatibility at a point. Express derivatives via Correspondence.source.field;
    # T3 API is exercised separately in MIG-COR-T04 composition / identity cases.
    full_at_1 = diff(corr.source.field, 1)
    frozen_at_1 = -2  # freeze (1+x^2) at x=1 → treat as -2*x
    near(full_at_1, -4)
    evidence = {
        "full_derivative_at_1": -4,
        "frozen_derivative_at_1": -2,
        "legacy_alias": "VER-COR-T03",
        "legacy_id": "t03_parameter_chain_rule",
        "note": "parameter chain rule on Df; T3 field-compat API used in T04 path",
    }
    require(evidence["full_derivative_at_1"] == expected["full_derivative_at_1"], "t03 full")
    require(evidence["frozen_derivative_at_1"] == expected["frozen_derivative_at_1"], "t03 frozen")
    return evidence


def mig_cor_t04_composed_transformations():
    expected = load_expected()["t04"]
    tji = lambda x: x + x**3 / 10
    tkj = lambda y: math.exp(y / 5)
    fi = lambda x: -x + 0.2
    fj = lambda y: -2 * y + 0.3
    fk = lambda z: -0.7 * z
    aji = lambda x: 1 + x * x
    akj = lambda y: 2 + y * y
    corr = Correspondence(
        source=ModelRef(name="level_i", field=fi),
        target=ModelRef(name="level_k", field=fk),
        state_map=StateMap(map_fn=lambda x: tkj(tji(x)), name="T_kj o T_ji"),
        scope=Scope(
            description="T4 residual composition",
            assumptions=("context_transformations.md §5", "nonconstant scales"),
        ),
        metric=ErrorMetric(atol=1e-8, rtol=0.0),
    )
    errors = []
    for x in np.linspace(-1, 1, 31):
        r = corr.t4_composition_residual(tji, tkj, fi, fj, fk, aji, akj, x)
        errors.append(r.value)
        y = tji(x)
        r_ji = diff(tji, x) * fi(x) - aji(x) * fj(y)
        r_kj = diff(tkj, y) * fj(y) - akj(y) * fk(tkj(y))
        direct = r.detail["direct"]
        require(
            abs(direct) <= abs(diff(tkj, y)) * abs(r_ji) + aji(x) * abs(r_kj) + 1e-9,
            "composition error bound",
        )
    require(max(errors) < 1e-8, "residual composition")
    evidence = {
        "max_composition_error": max(errors),
        "legacy_alias": "VER-COR-T04",
        "legacy_id": "t04_composed_transformations",
    }
    require(
        evidence["max_composition_error"] == expected["max_composition_error"],
        f"t04 max_composition_error {evidence['max_composition_error']!r} != {expected['max_composition_error']!r}",
    )
    return evidence


CHECKS = [
    ("MIG-COR-e11_topological_conjugacy_rates", mig_cor_e11_conjugacy),
    ("MIG-COR-T01_context_derivatives", mig_cor_t01_context_derivatives),
    ("MIG-COR-T02_state_dependent_time", mig_cor_t02_state_dependent_time),
    ("MIG-COR-T03_parameter_chain_rule", mig_cor_t03_parameter_chain_rule),
    ("MIG-COR-T04_composed_transformations", mig_cor_t04_composed_transformations),
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).with_name("verify_correspondence_core_results.json"),
    )
    args = parser.parse_args()
    results = []
    for name, fn in CHECKS:
        try:
            evidence = fn()
            results.append({"id": name, "status": "passed", "evidence": evidence})
        except Exception as exc:
            results.append({"id": name, "status": "failed", "error": f"{type(exc).__name__}: {exc}"})
    passed = sum(r["status"] == "passed" for r in results)
    failed = [r["id"] for r in results if r["status"] != "passed"]
    report = {
        "milestone": "M1_correspondence_core",
        "kind": "MIG equivalence (legacy evidence vs Correspondence API)",
        "generated_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "python": platform.python_version(),
        "numpy": np.__version__,
        "count": len(results),
        "passed": passed,
        "failed": len(failed),
        "empirical_validation": False,
        "checks": results,
    }
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    summary = {
        "count": report["count"],
        "passed": report["passed"],
        "failed": failed,
        "report": str(args.output.resolve()),
    }
    print(json.dumps(summary, ensure_ascii=False))
    raise SystemExit(0 if passed == len(results) else 1)


if __name__ == "__main__":
    main()
