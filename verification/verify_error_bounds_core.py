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


def raises_scope(fn):
    try:
        fn()
    except ScopeViolationError:
        return True
    return False


def _ctmc_actual_l1(theta, A, Q, pi0, p0, t):
    """Independent reference: exact matrix exponentials (scipy), no SCF code."""
    from scipy.linalg import expm

    theta, A, Q = (np.asarray(x, dtype=float) for x in (theta, A, Q))
    return float(np.abs(np.asarray(pi0) @ expm(theta * t) @ A - np.asarray(p0) @ expm(Q * t)).sum())


def check_review_r1_ctmc_zero_dynamics():
    """Followup-Review-Fix R1 (SCF_REVIEW_J_SERIES_6b3a331): general CTMC branch.

    Theta = (0), A = (1/2, 0), pi0 = (2), p0 = (1, 0), Q = [[-1, 1], [0, 0]], t = 1.
    Hand derivation: e' = pi(Theta A - A Q) + e Q, ||x e^{Qt}||_1 <= ||x||_1, so
    B = e0 + ||pi0||_1 ||Theta A - A Q||_inf phi(t, kappa) with phi(t, 0) = t:
    e0 = 0, ||A Q||_inf = ||(-1/2, 1/2)|| = 1  =>  B = 2 >= 2 (1 - e^-1).
    Old code returned 0 (also at kappa = 1e-20 by cancellation in exp(x) - 1).
    """
    Q = [[-1.0, 1.0], [0.0, 0.0]]
    A = [[0.5, 0.0]]
    actual = _ctmc_actual_l1([[0.0]], A, Q, [2.0], [1.0, 0.0], 1.0)
    near(actual, 2 * (1 - math.exp(-1)), atol=1e-12)
    out = {"actual": actual}
    for eps in (0.0, 1e-20):
        b = transient_reduction_bound([[eps]], A, Q, [2.0], [1.0, 0.0], 1, continuous_time=True)
        near(b.bound, 2.0, atol=1e-12)
        require(b.bound >= actual, f"bound {b.bound} must cover the actual error {actual}")
        out[f"bound_kappa_{eps}"] = b.bound
    # t = 0: only the initial error
    near(transient_reduction_bound([[0.0]], A, Q, [2.0], [1.0, 0.0], 0.0, continuous_time=True).bound, 0.0)
    # vanishing residual in the general branch (pi0 not a probability vector): tight bound 1
    Qg = [[-1.0, 1.0], [2.0, -2.0]]
    bz = transient_reduction_bound(Qg, np.eye(2), Qg, [2.0, 0.0], [1.0, 0.0], 3.0, continuous_time=True)
    near(bz.bound, 1.0)
    near(_ctmc_actual_l1(Qg, np.eye(2), Qg, [2.0, 0.0], [1.0, 0.0], 3.0), 1.0, atol=1e-12)
    # ordinary control: Theta = (1), kappa = 1 => B = 2 * 3/2 * (e - 1) = 3 (e - 1)
    bn = transient_reduction_bound([[1.0]], A, Q, [2.0], [1.0, 0.0], 1.0, continuous_time=True)
    near(bn.bound, 3 * (math.e - 1), atol=1e-12)
    an = _ctmc_actual_l1([[1.0]], A, Q, [2.0], [1.0, 0.0], 1.0)
    require(an <= bn.bound, f"actual {an} must not exceed {bn.bound}")
    out.update({"ordinary_bound": bn.bound, "ordinary_actual": an})
    return out


def check_review_r2_full_markov_and_tv_contract():
    """Followup-Review-Fix R2: the full dynamics must be Markov; TV has its own contract.

    Counterexample Pi = (1), A = (1, 0), P = diag(2, 1), pi0 = (1), p0 = (1, 0), k = 2:
    p_2 = (4, 0), reconstruction (1, 0), actual L1 error 3 > old bound 2.
    """
    P_bad = np.diag([2.0, 1.0])
    p2 = np.array([1.0, 0.0]) @ np.linalg.matrix_power(P_bad, 2)
    near(np.abs(np.array([1.0, 0.0]) - p2).sum(), 3.0)
    require(raises_scope(lambda: transient_reduction_bound([[1.0]], [[1.0, 0.0]], P_bad, [1.0], [1.0, 0.0], 2)),
            "non-stochastic full P must be refused")
    require(raises_scope(lambda: transient_reduction_bound([[0.0]], [[1.0, 0.0]], [[1.0, -1.0], [0.0, 0.0]], [1.0], [1.0, 0.0],
                                                           1.0, continuous_time=True)),
            "invalid generator (negative off-diagonal) must be refused")
    P_cols = np.array([[0.5, 1.0], [0.5, 0.0]])  # column-stochastic: transposed orientation
    require(raises_scope(lambda: transient_reduction_bound([[1.0]], [[1.0, 0.0]], P_cols, [1.0], [1.0, 0.0], 1)),
            "transposed (column-stochastic) P must be refused")
    # valid general L1 reduction stays supported: Pi not stochastic, A non-stochastic lift
    P = np.array([[0.5, 0.5], [0.25, 0.75]])
    Pi, A, pi0, p0 = np.array([[0.9]]), np.array([[0.6, 0.6]]), np.array([1.5]), np.array([1.0, 0.0])
    b = transient_reduction_bound(Pi, A, P, pi0, p0, 3)
    actual = max(float(np.abs(pi0 @ np.linalg.matrix_power(Pi, k) @ A - p0 @ np.linalg.matrix_power(P, k)).sum()) for k in (3,))
    require(actual <= b.bound + 1e-12 and "Theorem 4 (item 2)" in b.theorem_ref, f"general L1: {actual} <= {b.bound}")
    # TV needs the probability contract
    require(raises_scope(lambda: transient_reduction_bound(Pi, A, P, pi0, p0, 3, norm="TV")),
            "TV with non-stochastic lifting must be refused")
    P0, A0, Pi0 = paper_example_matrices()
    tv = transient_reduction_bound(Pi0, A0, P0, [1.0, 0.0], [0.5, 0.5, 0.0], 4, norm="TV")
    near(tv.bound, 0.5)
    # stationary: L1 is algebraic (any P), TV needs stochastic A, P and probability pi
    st = stationary_reduction_bound([[1.0]], [[1.0, 0.0]], P_bad, [1.0])
    near(st.bound, np.abs(np.array([1.0, 0.0]) @ P_bad - np.array([1.0, 0.0])).sum())  # = 1, tight here
    require(raises_scope(lambda: stationary_reduction_bound([[1.0]], [[1.0, 0.0]], P_bad, [1.0], norm="TV")),
            "stationary TV with non-stochastic P must be refused")
    return {"general_l1_bound": b.bound, "general_l1_actual": actual, "stationary_l1_any_P": st.bound}


CHECKS = [
    ("paper_dtmc_thm4", check_paper_dtmc_thm4),
    ("ctmc_thm5_exact", check_ctmc_thm5_exact),
    ("stationary_cor10", check_stationary_cor10),
    ("compatibility_core_call", check_compatibility_and_core_call),
    ("review_r1_ctmc_zero_dynamics", check_review_r1_ctmc_zero_dynamics),
    ("review_r2_full_markov_and_tv_contract", check_review_r2_full_markov_and_tv_contract),
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
