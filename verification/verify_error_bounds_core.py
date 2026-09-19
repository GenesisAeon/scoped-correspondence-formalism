#!/usr/bin/env python3
"""Hand-checkable verification for Formal Reduction Error Bounds (Milestone 21).

Checks (numbers from this script run):
  1. Paper §3.4 DTMC example: ‖ΠA−AP‖_∞ = 1/4; k=4 ⇒ Thm 4.3 bound = 1.0;
     k=0 ⇒ bound 0; residual 0 identity ⇒ bound 0.
  2. CTMC Thm 5.3: exact generator aggregation ⇒ bound 0 at t>0.
  3. Cor. 10 stationary: paper example ⇒ bound = 1/4 (π exact for Π).
  4. Compatibility: compare_to_propagated_error_bound on paper example
     (michel_tv=0.5 ≤ propagated(0.25,4)=1.0); CALL is_exact_closure /
     closure_error / propagated_error_bound on exact partition case
     (both frameworks report 0). SOURCE cites arXiv:2403.07618 + DOI.

Stdlib + numpy. JSON {count, passed, failed, report}; numbers from this run.
Does not import generator_lumpability; does not mutate closure.core.
"""
from __future__ import annotations

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

import numpy as np

from scoped_correspondence.closure.core import (  # noqa: E402
    closure_error,
    is_exact_closure,
    partition_matrix,
    propagated_error_bound,
)
from scoped_correspondence.closure.error_bounds import (  # noqa: E402
    SOURCE,
    ReductionErrorBound,
    compare_to_propagated_error_bound,
    paper_example_matrices,
    residual_inf_norm,
    stationary_reduction_bound,
    transient_reduction_bound,
)
from scoped_correspondence.errors import ScopeViolationError  # noqa: E402


def require(ok, msg):
    if not bool(ok):
        raise AssertionError(msg)


def near(a, b, atol=1e-12, rtol=1e-12):
    if not math.isclose(float(a), float(b), abs_tol=atol, rel_tol=rtol):
        raise AssertionError(f"{a!r} != {b!r} (atol={atol})")


def check_paper_dtmc_thm4():
    """Paper §3.4: residual 1/4; Thm 4.3 bound k/4; k=0 → 0; exact id → 0."""
    P, A, Pi = paper_example_matrices()
    r = residual_inf_norm(Pi, A, P)
    near(r, 0.25)
    pi0 = np.array([1.0, 0.0])
    p0 = pi0 @ A
    near(np.abs(p0 - np.array([0.5, 0.5, 0.0])).sum(), 0.0)

    b4 = transient_reduction_bound(Pi, A, P, pi0, p0, 4)
    require(isinstance(b4, ReductionErrorBound), "type")
    near(b4.bound, 1.0)
    near(b4.horizon, 4.0)
    require(b4.norm == "L1", b4.norm)
    require("Theorem 4" in b4.theorem_ref, b4.theorem_ref)
    require("item 3" in b4.theorem_ref or "4.3" in b4.theorem_ref, b4.theorem_ref)

    b0 = transient_reduction_bound(Pi, A, P, pi0, p0, 0)
    near(b0.bound, 0.0)

    # Degenerate: identity aggregation (exact)
    P2 = np.array([[0.5, 0.5], [0.25, 0.75]], dtype=float)
    A2 = np.eye(2)
    b_ex = transient_reduction_bound(P2, A2, P2, [1.0, 0.0], [1.0, 0.0], 7)
    near(b_ex.bound, 0.0)
    near(residual_inf_norm(P2, A2, P2), 0.0)

    # TV half of L1
    b_tv = transient_reduction_bound(Pi, A, P, pi0, p0, 4, norm="TV")
    near(b_tv.bound, 0.5)
    require(b_tv.norm == "TV", b_tv.norm)

    return {
        "residual_inf": r,
        "bound_k4_L1": b4.bound,
        "bound_k0_L1": b0.bound,
        "bound_exact_L1": b_ex.bound,
        "bound_k4_TV": b_tv.bound,
        "theorem_ref": b4.theorem_ref,
    }


def check_ctmc_thm5_exact():
    """Thm 5.3: Θ=Q, A=I ⇒ residual 0 ⇒ bound 0."""
    Q = np.array([[-1.0, 1.0], [2.0, -2.0]], dtype=float)
    Theta = Q.copy()
    A = np.eye(2)
    bt = transient_reduction_bound(
        Theta, A, Q, [1.0, 0.0], [1.0, 0.0], 3.5, continuous_time=True
    )
    near(bt.bound, 0.0)
    near(bt.horizon, 3.5)
    require("Theorem 5" in bt.theorem_ref, bt.theorem_ref)
    # Non-exact CTMC: scale residual
    Theta_bad = np.array([[-0.5, 0.5], [1.0, -1.0]], dtype=float)
    bb = transient_reduction_bound(
        Theta_bad, A, Q, [1.0, 0.0], [1.0, 0.0], 2.0, continuous_time=True
    )
    require(bb.bound > 0.0, f"expected positive, got {bb.bound}")
    require("Theorem 5" in bb.theorem_ref, bb.theorem_ref)
    return {
        "exact_bound": bt.bound,
        "inexact_bound_t2": bb.bound,
        "theorem_ref_exact": bt.theorem_ref,
    }


def check_stationary_cor10():
    """Cor. 10 on paper example: π stationary for Π ⇒ bound = ‖ΠA−AP‖_∞ = 1/4."""
    P, A, Pi = paper_example_matrices()
    # Left eigenvector for eigenvalue 1
    w, v = np.linalg.eig(Pi.T)
    idx = int(np.argmin(np.abs(w - 1.0)))
    pi = np.real(v[:, idx])
    pi = pi / pi.sum()
    near(np.abs(pi @ Pi - pi).sum(), 0.0, atol=1e-10)
    st = stationary_reduction_bound(Pi, A, P, pi)
    near(st.bound, 0.25)
    require(st.horizon is None, str(st.horizon))
    require("Corollary 10" in st.theorem_ref, st.theorem_ref)
    return {
        "pi": pi.tolist(),
        "bound_L1": st.bound,
        "theorem_ref": st.theorem_ref,
    }


def check_compatibility_and_core_call():
    """Michel TV ≤ propagated on paper example; exact partition → both 0."""
    P, A, Pi = paper_example_matrices()
    pi0 = np.array([1.0, 0.0])
    p0 = pi0 @ A
    b = transient_reduction_bound(Pi, A, P, pi0, p0, 4)
    near(b.bound, 1.0)
    cmp_ = compare_to_propagated_error_bound(b.bound, 0.25, 4)
    near(cmp_["michel_tv"], 0.5)
    near(cmp_["propagated_error_bound_tv"], 1.0)
    require(cmp_["michel_tv_leq_propagated"] is True, str(cmp_))

    # Exact lumpable partition: CALL core helpers
    # Two identical states → one macro
    P_ex = np.array(
        [
            [0.0, 0.5, 0.5],
            [0.5, 0.0, 0.5],
            [0.5, 0.5, 0.0],
        ],
        dtype=float,
    )
    # Better: strongly lumpable chain
    P_ex = np.array(
        [
            [0.1, 0.4, 0.5],
            [0.1, 0.4, 0.5],
            [0.2, 0.3, 0.5],
        ],
        dtype=float,
    )
    C, lift = partition_matrix([0, 0, 1])
    # For exact ordinary lumpability of first two states outgoing to macros:
    # rows 0,1 identical ⇒ PC = C Q with Q = lift @ P @ C
    Q = lift @ P_ex @ C
    require(is_exact_closure(P_ex, C, Q), "expected exact closure")
    near(closure_error(P_ex, C, Q), 0.0)
    near(propagated_error_bound(0.0, 10), 0.0)

    # Michel view with A = lift (disaggregation), Π = Q: residual should be ~0
    # when aggregation is ordinary-lumpable with uniform-in-block lift matching.
    # For ordinary lumpability, ΛΠ = PΛ with Λ=C, not necessarily ΠA=AP.
    # Use identity A on a dynamic-exact pair instead:
    A_id = np.eye(3)
    Pi_id = P_ex.copy()
    b_id = transient_reduction_bound(Pi_id, A_id, P_ex, [1, 0, 0], [1, 0, 0], 5)
    near(b_id.bound, 0.0)
    cmp0 = compare_to_propagated_error_bound(0.0, 0.0, 5)
    require(cmp0["michel_tv_leq_propagated"] is True, str(cmp0))
    near(cmp0["michel_tv"], 0.0)
    near(cmp0["propagated_error_bound_tv"], 0.0)

    require("2403.07618" in SOURCE, SOURCE)
    require("10.1016/j.peva.2024.102464" in SOURCE, SOURCE)
    require("generator_lumpability" not in SOURCE.lower(), "must not mix M11")

    # Scope guard
    try:
        transient_reduction_bound(Pi, A, P, pi0, p0, -1)
        raise AssertionError("expected ScopeViolationError for k<0")
    except ScopeViolationError:
        pass

    return {
        "paper_compare": cmp_,
        "exact_closure_error": closure_error(P_ex, C, Q),
        "exact_michel_bound": b_id.bound,
        "zero_compare": cmp0,
        "SOURCE": SOURCE,
    }


CHECKS = [
    ("paper_dtmc_thm4", check_paper_dtmc_thm4),
    ("ctmc_thm5_exact", check_ctmc_thm5_exact),
    ("stationary_cor10", check_stationary_cor10),
    ("compatibility_core_call", check_compatibility_and_core_call),
]


def main():
    report = {
        "milestone": "M21",
        "title": "Formal Reduction Error Bounds",
        "timestamp": dt.datetime.now().isoformat(timespec="seconds"),
        "platform": platform.platform(),
        "python": sys.version.split()[0],
        "checks": {},
    }
    passed = failed = 0
    for name, fn in CHECKS:
        try:
            report["checks"][name] = {"ok": True, "data": fn()}
            passed += 1
            print(f"PASS {name}")
        except Exception as exc:  # noqa: BLE001 — report all failures
            report["checks"][name] = {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
            failed += 1
            print(f"FAIL {name}: {type(exc).__name__}: {exc}")
    report["count"] = len(CHECKS)
    report["passed"] = passed
    report["failed"] = failed
    out = Path(__file__).with_name("verify_error_bounds_core_results.json")
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {out} ({passed}/{len(CHECKS)})")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
