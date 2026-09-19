#!/usr/bin/env python3
"""Equivalence checks for Closure core (Milestone 3).

Matches legacy verify_extensions.py / verify_transformations.py:
  - e01_circle_reconstruction
  - e03_projected_memory
  - e04_exact_lumpability
  - e05_nonclosed_aggregation
  - e06_approximate_error_bound
  - t07_unequal_rates_break_closure
  - t15_changing_partition_exact_closure

Stdlib + NumPy. JSON {count, passed, failed, report}; numbers from this run.
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
    ScopeViolationError,
    candidate_macro_kernel,
    closure_error,
    coupled_buffer_field,
    demo_matrices,
    is_exact_closure,
    memory_solution,
    partition_matrix,
    projected_memory_rhs,
    propagated_error_bound,
    reconstruct_from_projection,
)
from scoped_correspondence.legacy import (  # noqa: E402
    circle_reconstruct,
    delta_cl,
    exact_closure_PC_CQ,
    tv_horizon_bound,
)


def require(ok, msg):
    if not bool(ok):
        raise AssertionError(msg)


def near(a, b, atol=1e-10, rtol=1e-9):
    if not np.allclose(a, b, atol=atol, rtol=rtol):
        raise AssertionError(f"{a!r} != {b!r}")


def derivative(f, x, step=1e-5):
    return (f(x + step) - f(x - step)) / (2 * step)


def load_extension_evidence(name: str):
    path = ROOT / "verification" / "extension_results.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    for c in data["checks"]:
        if c.get("name") == name:
            require(c["status"] == "passed", f"legacy {name} not passed")
            return c["evidence"]
    raise AssertionError(f"legacy evidence {name} missing")


def load_transform_evidence(name: str):
    path = ROOT / "verification" / "transformation_results.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    for c in data["results"]:
        if c.get("id") == name:
            require(c["status"] == "passed", f"legacy {name} not passed")
            return c["evidence"]
    raise AssertionError(f"legacy evidence {name} missing")


def mig_cl_e01_circle_reconstruction():
    expected = load_extension_evidence("e01_circle_reconstruction")
    alpha = 0.7
    phases = np.linspace(-math.pi, math.pi, 257, endpoint=False)
    observed = np.cos(phases)
    delayed = np.cos(phases - alpha)
    reconstructed, recovered_sine = reconstruct_from_projection(observed, delayed, alpha)
    near(recovered_sine, np.sin(phases))
    angle_error = np.angle(np.exp(1j * (reconstructed - phases)))
    near(angle_error, 0)
    # Legacy adapter alias
    rec2, sine2 = circle_reconstruct(observed, delayed, alpha)
    near(rec2, reconstructed)
    near(sine2, recovered_sine)
    # Non-injective delay must raise
    try:
        reconstruct_from_projection(observed, delayed, math.pi)
        raise AssertionError("expected ScopeViolationError for alpha=pi")
    except ScopeViolationError:
        pass
    evidence = {
        "intrinsic_dimension": 1,
        "sufficient_coordinates_in_this_model": 2,
        "max_angle_error": float(np.max(np.abs(angle_error))),
        "legacy_id": "e01_circle_reconstruction",
        "legacy_alias": "VER-CL-e01_circle_reconstruction",
    }
    near(evidence["max_angle_error"], expected["max_angle_error"], atol=1e-15)
    require(
        evidence["intrinsic_dimension"] == expected["intrinsic_dimension"],
        "intrinsic_dimension",
    )
    require(
        evidence["sufficient_coordinates_in_this_model"]
        == expected["sufficient_coordinates_in_this_model"],
        "sufficient_coordinates",
    )
    return evidence


def mig_cl_e03_projected_memory():
    expected = load_extension_evidence("e03_projected_memory")
    residuals = []
    for x0, y0 in [(0.0, 1.0), (0.0, -1.0), (1.2, -0.7)]:
        for t in [0.1, 0.5, 1.0, 2.0]:
            x, xp, y = memory_solution(t, x0, y0)
            dx_numeric = derivative(lambda s: memory_solution(s, x0, y0)[0], t)
            dy_numeric = derivative(lambda s: memory_solution(s, x0, y0)[2], t)
            near(dx_numeric, -x + y, atol=2e-9)
            near(dy_numeric, -x - 2 * y, atol=2e-9)
            rhs = projected_memory_rhs(t, x0, y0)
            near(rhs, xp, atol=2e-8)
            residuals.append(float(abs(rhs - float(np.asarray(xp)))))
    near(memory_solution(0, 0, 1)[1], 1)
    near(memory_solution(0, 0, -1)[1], -1)
    evidence = {
        "max_memory_residual": max(residuals),
        "same_observation_distinct_drifts": [1, -1],
        "legacy_id": "e03_projected_memory",
        "legacy_alias": "VER-CL-e03_projected_memory",
    }
    near(evidence["max_memory_residual"], expected["max_memory_residual"], atol=1e-12)
    require(
        evidence["same_observation_distinct_drifts"]
        == expected["same_observation_distinct_drifts"],
        "drifts",
    )
    return evidence


def mig_cl_e04_exact_lumpability():
    expected = load_extension_evidence("e04_exact_lumpability")
    p, _bad, c, lift = demo_matrices()
    q = candidate_macro_kernel(p, c, lift)
    near(q, np.eye(2))
    require(is_exact_closure(p, c, q), "PC=CQ must hold")
    require(exact_closure_PC_CQ(p, c, q), "legacy alias")
    near(closure_error(p, c, q), 0.0, atol=1e-15)
    near(p @ c, c @ q)
    for k in range(11):
        near(np.linalg.matrix_power(p, k) @ c, c @ np.linalg.matrix_power(q, k))
        near(propagated_error_bound(0.0, k), 0.0)
    alternate_lift = np.array([[1.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 1.0]])
    near(alternate_lift @ c, np.eye(2))
    near(alternate_lift @ p @ c, q)
    evidence = {
        "macro_kernel": q.tolist(),
        "horizons_checked": 11,
        "lift_independent": True,
        "legacy_id": "e04_exact_lumpability",
        "legacy_alias": "VER-CL-e04_exact_lumpability",
    }
    require(evidence["macro_kernel"] == expected["macro_kernel"], "macro_kernel")
    require(evidence["horizons_checked"] == expected["horizons_checked"], "horizons")
    require(evidence["lift_independent"] is True, "lift_independent")
    return evidence


def mig_cl_e05_nonclosed_aggregation():
    expected = load_extension_evidence("e05_nonclosed_aggregation")
    _p_good, p, c, lift = demo_matrices()
    # Legacy e05 uses the *bad* swap matrix as P
    q = candidate_macro_kernel(p, c, lift)
    near((p @ c)[0], [1, 0])
    near((p @ c)[1], [0, 1])
    require(not is_exact_closure(p, c, q), "invalid closure was accepted")
    delta = closure_error(p, c, q)
    require(delta > 0, "positive closure defect")
    truth = np.linalg.matrix_power(p, 2) @ c
    reduced = c @ np.linalg.matrix_power(q, 2)
    require(not np.allclose(truth, reduced), "hidden resetting undetected")
    two_step_error = float(np.abs(truth - reduced).sum(axis=1).max() / 2)
    evidence = {
        "same_macro_distinct_next_rows": (p @ c)[:2].tolist(),
        "two_step_error": two_step_error,
        "legacy_id": "e05_nonclosed_aggregation",
        "legacy_alias": "VER-CL-e05_nonclosed_aggregation",
    }
    require(
        evidence["same_macro_distinct_next_rows"]
        == expected["same_macro_distinct_next_rows"],
        "next rows",
    )
    near(evidence["two_step_error"], expected["two_step_error"], atol=1e-15)
    return evidence


def mig_cl_e06_approximate_error_bound():
    expected = load_extension_evidence("e06_approximate_error_bound")
    p, bad, c, lift = demo_matrices()
    # Mix exact and bad as in legacy
    mixed = 0.96 * p + 0.04 * bad
    # Legacy stochastic() validates row sums but does not re-normalize.
    near(mixed.sum(axis=1), np.ones(len(mixed)))
    q = candidate_macro_kernel(mixed, c, lift)
    delta = closure_error(mixed, c, q)
    near(delta, delta_cl(mixed, c, q))
    require(0 < delta < 0.1, "expected nontrivial small closure defect")
    errors = []
    for k in range(21):
        difference = (
            np.linalg.matrix_power(mixed, k) @ c
            - c @ np.linalg.matrix_power(q, k)
        )
        error = float(np.abs(difference).sum(axis=1).max() / 2)
        bound = propagated_error_bound(delta, k)
        near(bound, tv_horizon_bound(delta, k))
        require(error <= bound + 1e-12, "TV horizon bound failed")
        errors.append(error)
    evidence = {
        "delta": delta,
        "max_error": max(errors),
        "horizons": 21,
        "all_pure_initial_states_checked": True,
        "legacy_id": "e06_approximate_error_bound",
        "legacy_alias": "VER-CL-e06_approximate_error_bound",
    }
    near(evidence["delta"], expected["delta"], atol=1e-15)
    near(evidence["max_error"], expected["max_error"], atol=1e-15)
    require(evidence["horizons"] == expected["horizons"], "horizons")
    return evidence


def mig_cl_t07_unequal_rates_break_closure():
    expected = load_transform_evidence("t07_unequal_rates_break_closure")
    rates = [
        float(
            coupled_buffer_field(x, [1, 2], [0, 0], [0, 0], [0, 0], 0.7).sum()
        )
        for x in ([1, 0], [0, 1])
    ]
    near(rates, [-1, -2])
    require(rates[0] != rates[1], "equal sum has distinct future derivatives")
    evidence = {
        "same_sum": 1,
        "two_derivatives": list(map(float, rates)),
        "legacy_id": "t07_unequal_rates_break_closure",
        "legacy_alias": "VER-CL-t07_unequal_rates_break_closure",
    }
    require(evidence["same_sum"] == expected["same_sum"], "same_sum")
    require(evidence["two_derivatives"] == expected["two_derivatives"], "derivatives")
    return evidence


def mig_cl_t15_changing_partition_exact_closure():
    expected = load_transform_evidence("t15_changing_partition_exact_closure")
    c0 = np.eye(2)[[0, 0, 1, 1]]
    swap = np.array([[0.0, 1.0], [1.0, 0.0]])
    c1 = c0 @ swap
    p = np.eye(4)
    # Exact time-varying closure with matching partition: P C1 = C0 swap
    near(p @ c1, c0 @ swap)
    wrong = float(np.max(np.abs(p @ c0 - c0 @ swap)))
    require(wrong == 1, "using old partition yields wrong condition")
    # With the *correct* next partition, treat Q = swap as macro kernel relating
    # C_t -> C_{t+1}: check is_exact style equality p@c1 == c0@swap
    require(np.allclose(p @ c1, c0 @ swap), "changing-partition exact step")
    micro = np.array([0.1, 0.2, 0.3, 0.4])
    macro = micro @ c0
    c = c0.copy()
    for _ in range(7):
        c = c @ swap
        macro = macro @ swap
        near(micro @ c, macro)
    evidence = {
        "exact_error": 0,
        "wrong_old_partition_error": wrong,
        "steps": 7,
        "legacy_id": "t15_changing_partition_exact_closure",
        "legacy_alias": "VER-CL-t15_changing_partition_exact_closure",
    }
    require(evidence["exact_error"] == expected["exact_error"], "exact_error")
    near(evidence["wrong_old_partition_error"], expected["wrong_old_partition_error"])
    require(evidence["steps"] == expected["steps"], "steps")
    return evidence


def mig_cl_audit_nonstochastic_rejected():
    """Audit finding: is_exact_closure(2*I, I, 2*I) returned True.

    PC=CQ holds trivially for P=Q=2*I (2I@I == I@2I), but P=2I is not a
    valid row-stochastic micro kernel (rows sum to 2, not 1) -- "exact
    closure" (FORMALISM.md section 9) is only defined for stochastic P
    and Q, and checking the algebraic identity alone silently certified a
    non-stochastic matrix pair that satisfies it for unrelated reasons.
    """
    p_bad = 2.0 * np.eye(2)
    c = np.eye(2)
    q_bad = 2.0 * np.eye(2)
    raised_p = False
    try:
        is_exact_closure(p_bad, c, np.eye(2))
    except ScopeViolationError:
        raised_p = True
    require(raised_p, "non-stochastic P (2I) must raise")

    raised_q = False
    try:
        is_exact_closure(np.eye(2), c, q_bad)
    except ScopeViolationError:
        raised_q = True
    require(raised_q, "non-stochastic Q (2I) must raise")

    raised_both = False
    try:
        is_exact_closure(p_bad, c, q_bad)
    except ScopeViolationError:
        raised_both = True
    require(raised_both, "audit exact counter-example is_exact_closure(2I,I,2I) must raise")

    # A genuinely stochastic identity closure must still pass.
    require(is_exact_closure(np.eye(2), c, np.eye(2)), "P=Q=I stochastic closure must hold")

    return {
        "nonstochastic_P_raises": raised_p,
        "nonstochastic_Q_raises": raised_q,
        "audit_example_2I_raises": raised_both,
        "stochastic_identity_still_ok": True,
    }


CHECKS = [
    ("MIG-CL-e01_circle_reconstruction", mig_cl_e01_circle_reconstruction),
    ("MIG-CL-e03_projected_memory", mig_cl_e03_projected_memory),
    ("MIG-CL-e04_exact_lumpability", mig_cl_e04_exact_lumpability),
    ("MIG-CL-e05_nonclosed_aggregation", mig_cl_e05_nonclosed_aggregation),
    ("MIG-CL-e06_approximate_error_bound", mig_cl_e06_approximate_error_bound),
    ("MIG-CL-t07_unequal_rates_break_closure", mig_cl_t07_unequal_rates_break_closure),
    ("MIG-CL-t15_changing_partition_exact_closure", mig_cl_t15_changing_partition_exact_closure),
    ("audit_nonstochastic_rejected", mig_cl_audit_nonstochastic_rejected),
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).with_name("verify_closure_core_results.json"),
    )
    args = parser.parse_args()
    results = []
    for name, fn in CHECKS:
        try:
            evidence = fn()
            results.append({"id": name, "status": "passed", "evidence": evidence})
        except Exception as exc:
            results.append(
                {"id": name, "status": "failed", "error": f"{type(exc).__name__}: {exc}"}
            )
    passed = sum(r["status"] == "passed" for r in results)
    failed = [r["id"] for r in results if r["status"] != "passed"]
    report = {
        "milestone": "M3_closure_core",
        "kind": "MIG equivalence (legacy extensions/transformations vs Closure API)",
        "generated_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "python": platform.python_version(),
        "numpy": np.__version__,
        "count": len(results),
        "passed": passed,
        "failed": len(failed),
        "empirical_validation": False,
        "checks": results,
    }
    args.output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
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
