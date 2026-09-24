#!/usr/bin/env python3
"""Transient amplification via non-normal coupling (Milestone 58).

CAPABILITY_EXPANSION_ROADMAP.md Priority 4. Checks:

  1. The canonical triangular matrix's closed-form ``e^{At}`` against a
     direct ``scipy.linalg.expm`` call.
  2. ``max_finite_time_gain`` degenerate case: with no coupling (``k=0``,
     a NORMAL/diagonal matrix), the finite-time gain can never exceed 1 and
     peaks exactly at ``t=0`` — no transient amplification is possible
     without non-normality, a clean edge-case check of the optimizer.
  3. An EXACT closed-form regression check for the two-buffer example:
     for ``x0=[0,1]`` and the canonical ``A=[[-1,k],[0,-1]]``, ``x1(t) =
     k*t*e^{-t}`` exactly, whose maximum is exactly at ``t=1`` with value
     ``k/e`` — derived independently by hand (not by re-running the
     module's own code) and checked against ``classify_two_buffer_transient``'s
     numerically-found peak.
  4. The three-way outcome classification (Astra's explicit request) on
     three worked cases: no coupling (safe, unaffected by the same
     perturbation that endangers the coupled case), coupled-but-stable
     (transient violation, GUARANTEED to return since both eigenvalues are
     negative), and unstable (violation with no guaranteed return) — the
     coupling strength and initial condition are otherwise IDENTICAL
     across the first two cases, isolating coupling as the sole cause of
     the difference.
  5. ScopeViolationError guards.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

import numpy as np
from scipy.linalg import expm

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from scoped_correspondence.errors import ScopeViolationError  # noqa: E402
from scoped_correspondence.viability.transient_amplification import (  # noqa: E402
    SOURCE, SAFE_NO_VIOLATION, TRANSIENT_VIOLATION, UNSTABLE_VIOLATION,
    canonical_triangular_matrix, canonical_matrix_exponential_closed_form,
    finite_time_gain, max_finite_time_gain, classify_two_buffer_transient,
)


def require(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)


def check_closed_form_against_expm():
    k = 5.0
    A = canonical_triangular_matrix(k)
    require(A.shape == (2, 2) and A[0, 0] == -1.0 and A[1, 1] == -1.0 and A[0, 1] == k and A[1, 0] == 0.0,
            "canonical_triangular_matrix shape/values wrong")
    max_diff = 0.0
    for t in (0.0, 0.1, 0.5, 1.0, 2.0, 5.0):
        got_direct = expm(A * t)
        got_closed = canonical_matrix_exponential_closed_form(k, t)
        max_diff = max(max_diff, float(np.max(np.abs(got_direct - got_closed))))
    require(max_diff < 1e-10, f"closed form vs expm max diff too large: {max_diff}")
    try:
        canonical_matrix_exponential_closed_form(k, -0.1)
        raise AssertionError("should reject negative t")
    except ScopeViolationError:
        pass
    return {"max_diff_closed_form_vs_expm": max_diff}


def check_no_coupling_gain_never_exceeds_one():
    A = canonical_triangular_matrix(0.0)  # diagonal, k=0 -> normal matrix
    t_star, peak = max_finite_time_gain(A, 20.0)
    require(abs(peak - 1.0) < 1e-4, f"k=0 peak gain should be (numerically) exactly 1; got {peak}")
    require(t_star < 1e-3, f"k=0 peak gain should occur at t=0; got t*={t_star}")
    for t in (0.0, 1.0, 5.0, 10.0):
        g = finite_time_gain(A, t)
        require(g <= 1.0 + 1e-9, f"k=0: gain at t={t} exceeds 1 ({g}) -- normal matrix cannot amplify")
    return {"t_star": t_star, "peak_gain": peak}


def check_exact_closed_form_peak_for_two_buffer_example():
    k = 2.0
    r = classify_two_buffer_transient(canonical_triangular_matrix(k), [0.0, 1.0], t_max=10.0, boundary=0.5, n_points=600)
    # Independently hand-derived: x1(t) = k*t*e^{-t} for x0=[0,1] on this canonical A;
    # d/dt(k*t*e^{-t}) = k*e^{-t}*(1-t) = 0 at t=1, value = k/e.
    want_peak_time = 1.0
    want_peak_value = k / np.e
    require(abs(r.peak_abs_x1_time - want_peak_time) < 1e-3,
            f"peak time: got {r.peak_abs_x1_time}, want {want_peak_time}")
    require(abs(r.peak_abs_x1_value - want_peak_value) < 1e-3,
            f"peak value: got {r.peak_abs_x1_value}, want {want_peak_value}")
    require(r.classification == TRANSIENT_VIOLATION, f"expected {TRANSIENT_VIOLATION}, got {r.classification}")
    return {"peak_time": r.peak_abs_x1_time, "peak_value": r.peak_abs_x1_value, "k_over_e": want_peak_value}


def check_three_way_classification():
    x0 = [0.0, 1.0]
    boundary = 0.5

    r_uncoupled = classify_two_buffer_transient([[-1.0, 0.0], [0.0, -1.0]], x0, t_max=10.0, boundary=boundary)
    require(r_uncoupled.classification == SAFE_NO_VIOLATION, f"uncoupled case: got {r_uncoupled.classification}")
    require(r_uncoupled.peak_abs_x1_value == 0.0, "uncoupled case: x1 should stay exactly 0 (no forcing on x1 at all)")

    r_stable_coupled = classify_two_buffer_transient([[-1.0, 2.0], [0.0, -1.0]], x0, t_max=10.0, boundary=boundary)
    require(r_stable_coupled.classification == TRANSIENT_VIOLATION, f"stable coupled case: got {r_stable_coupled.classification}")
    require(r_stable_coupled.is_asymptotically_stable, "stable coupled case should be classified asymptotically stable")

    r_unstable = classify_two_buffer_transient([[0.1, 2.0], [0.0, -1.0]], x0, t_max=10.0, boundary=boundary)
    require(r_unstable.classification == UNSTABLE_VIOLATION, f"unstable case: got {r_unstable.classification}")
    require(not r_unstable.is_asymptotically_stable, "unstable case should NOT be classified asymptotically stable")

    require(len({r_uncoupled.classification, r_stable_coupled.classification, r_unstable.classification}) == 3,
            "the three worked cases must produce three DIFFERENT classifications")

    return {
        "uncoupled": r_uncoupled.classification,
        "stable_coupled": r_stable_coupled.classification,
        "unstable": r_unstable.classification,
    }


def check_scope_violation_guards():
    for kwargs, label in (
        (dict(A=[[-1, 0], [0, -1], [0, 0]], x0=[0, 1], t_max=1.0, boundary=0.5), "non_2x2_A"),
        (dict(A=[[-1, 0], [0, -1]], x0=[0, 1, 2], t_max=1.0, boundary=0.5), "wrong_x0_shape"),
        (dict(A=[[-1, 0], [0, -1]], x0=[0, 1], t_max=-1.0, boundary=0.5), "negative_t_max"),
        (dict(A=[[-1, 0], [0, -1]], x0=[0, 1], t_max=1.0, boundary=-0.5), "negative_boundary"),
    ):
        try:
            classify_two_buffer_transient(**kwargs)
            raise AssertionError(f"classify_two_buffer_transient should reject {label}")
        except ScopeViolationError:
            pass

    try:
        finite_time_gain([[-1, 0], [0, -1]], -1.0)
        raise AssertionError("finite_time_gain should reject negative t")
    except ScopeViolationError:
        pass
    try:
        max_finite_time_gain([[-1, 0], [0, -1]], -1.0)
        raise AssertionError("max_finite_time_gain should reject non-positive t_max")
    except ScopeViolationError:
        pass
    return {"checked": 6}


CHECKS = [
    ("closed_form_against_expm", check_closed_form_against_expm),
    ("no_coupling_gain_never_exceeds_one", check_no_coupling_gain_never_exceeds_one),
    ("exact_closed_form_peak_for_two_buffer_example", check_exact_closed_form_peak_for_two_buffer_example),
    ("three_way_classification", check_three_way_classification),
    ("scope_violation_guards", check_scope_violation_guards),
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json-out", type=Path, default=Path(__file__).with_name("verify_transient_amplification_results.json"))
    args = parser.parse_args()

    report = {
        "package": "CAPABILITY_EXPANSION_ROADMAP.md Priority 4 (transient amplification)",
        "source": SOURCE,
        "timestamp": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "python": sys.version.split()[0],
        "checks": {},
    }

    all_ok = True
    for name, fn in CHECKS:
        try:
            detail = fn()
            report["checks"][name] = {"status": "pass", "detail": detail}
            print(f"PASS  {name}")
        except AssertionError as e:
            all_ok = False
            report["checks"][name] = {"status": "fail", "error": str(e)}
            print(f"FAIL  {name}: {e}")
        except Exception as e:  # noqa: BLE001
            all_ok = False
            report["checks"][name] = {"status": "error", "error": f"{type(e).__name__}: {e}"}
            print(f"ERROR {name}: {type(e).__name__}: {e}")

    args.json_out.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    print(f"\n{sum(1 for c in report['checks'].values() if c['status'] == 'pass')}/{len(CHECKS)} checks passed")
    print(f"Report written to {args.json_out}")
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
