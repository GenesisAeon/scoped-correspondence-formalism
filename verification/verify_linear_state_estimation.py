#!/usr/bin/env python3
"""Linear-Gaussian state estimation core (INTEGRATED_EXTENSION_ROADMAP.md Paket C1).

Checks:

  1. Hand-derived control-case update: F=diag(1/2,1/4), H=(1,1), m-=0, P-=I,
     R=1, y=3, W=0 gives exactly K=(1/3,1/3), m+=(1,1),
     P+=[[2/3,-1/3],[-1/3,2/3]] (independently re-derived by hand before this
     script was written; see module docstring of linear_state_estimation.py).
  2. Predicting one more step (no further observation) from that exact
     posterior gives predicted next-observation mean 0.75 and variance 1.125.
  3. Observability control case: det([H;HF])=-0.25 (rank 2, observable) for
     F=diag(1/2,1/4); at F=0.5*I the observability matrix drops to rank 1
     (the state DIFFERENCE is invisible to H=(1,1) under equal decay).
  4. Joseph-form posterior covariance is symmetric and positive semi-definite
     for a batch of random well-conditioned (F,H,P,R) instances -- not merely
     asserted, checked via eigenvalues.
  5. Independent method cross-check (never call the same filter function
     twice against itself): the posterior of a two-step linear-Gaussian model
     is computed TWO independent ways -- (a) this module's predict()+update(),
     (b) direct conditioning of the analytically-derived JOINT Gaussian
     distribution of (x1, y1) via the standard Gaussian conditioning formula
     -- and the two must agree to numerical precision.
  6. A singular innovation covariance (H=0 row, R=0) raises
     ScopeViolationError rather than silently falling back to a pseudoinverse.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from scoped_correspondence.errors import ScopeViolationError  # noqa: E402
from scoped_correspondence.observation.linear_state_estimation import (  # noqa: E402
    make_state,
    predict,
    update,
    observability_matrix,
    observability_report,
)


def require(ok, msg):
    if not bool(ok):
        raise AssertionError(msg)


def allclose(a, b, atol=1e-9, msg=""):
    a, b = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    require(np.allclose(a, b, atol=atol), f"{msg}: {a!r} != {b!r}")


def check_control_case_update():
    F = np.diag([0.5, 0.25])
    H = np.array([[1.0, 1.0]])
    W = np.zeros((2, 2))
    R = np.array([[1.0]])
    prior = make_state([0.0, 0.0], np.eye(2))

    rep = update(prior, y=[3.0], H=H, R=R)
    allclose(rep.gain.flatten(), [1.0 / 3.0, 1.0 / 3.0], msg="gain K")
    allclose(rep.state.mean, [1.0, 1.0], msg="posterior mean m+")
    allclose(rep.state.cov, [[2.0 / 3.0, -1.0 / 3.0], [-1.0 / 3.0, 2.0 / 3.0]], msg="posterior cov P+")
    allclose(rep.innovation, [3.0], msg="innovation")
    allclose(rep.innovation_cov, [[3.0]], msg="innovation covariance S")
    return {"K": rep.gain.flatten().tolist(), "m_plus": rep.state.mean.tolist(), "P_plus": rep.state.cov.tolist()}


def check_predict_after_update_control_case():
    F = np.diag([0.5, 0.25])
    W = np.zeros((2, 2))
    R = np.array([[1.0]])
    H = np.array([[1.0, 1.0]])
    prior = make_state([0.0, 0.0], np.eye(2))
    rep = update(prior, y=[3.0], H=H, R=R)

    next_state = predict(rep.state, F=F, W=W)
    pred_mean = float((H @ next_state.mean)[0])
    pred_var = float((H @ next_state.cov @ H.T + R)[0, 0])
    require(abs(pred_mean - 0.75) < 1e-9, f"predicted next observation mean should be 0.75, got {pred_mean!r}")
    require(abs(pred_var - 1.125) < 1e-9, f"predicted next observation variance should be 1.125, got {pred_var!r}")
    return {"pred_mean": pred_mean, "pred_var": pred_var}


def check_observability_control_case():
    F_obs = np.diag([0.5, 0.25])
    H = np.array([[1.0, 1.0]])
    O = observability_matrix(F_obs, H)
    det = float(np.linalg.det(O))
    require(abs(det - (-0.25)) < 1e-9, f"det([H;HF]) should be -0.25, got {det!r}")
    rep_obs = observability_report(F_obs, H)
    require(rep_obs.rank == 2, f"F=diag(1/2,1/4) with H=(1,1) should be observable (rank 2), got {rep_obs.rank}")

    F_unobs = 0.5 * np.eye(2)
    rep_unobs = observability_report(F_unobs, H)
    require(rep_unobs.rank == 1, f"F=0.5*I with H=(1,1) should have observability rank 1, got {rep_unobs.rank}")
    require(
        rep_unobs.singular_values[-1] < 1e-9,
        f"the smallest singular value of O should be ~0 at the degenerate point, got {rep_unobs.singular_values[-1]!r}",
    )
    return {"det_obs": det, "rank_obs": rep_obs.rank, "rank_unobs": rep_unobs.rank, "sv_unobs": rep_unobs.singular_values.tolist()}


def check_joseph_form_symmetric_psd():
    rng = np.random.default_rng(1)
    for trial in range(20):
        n = rng.integers(1, 4)
        m = rng.integers(1, 3)
        A = rng.normal(size=(n, n))
        P = A @ A.T + n * np.eye(n)  # SPD
        H = rng.normal(size=(m, n))
        B = rng.normal(size=(m, m))
        R = B @ B.T + m * np.eye(m)  # SPD
        prior = make_state(rng.normal(size=n), P)
        rep = update(prior, y=rng.normal(size=m), H=H, R=R)
        cov = rep.state.cov
        require(np.allclose(cov, cov.T, atol=1e-8), f"trial {trial}: posterior cov not symmetric")
        eigvals = np.linalg.eigvalsh(cov)
        require(np.min(eigvals) > -1e-8, f"trial {trial}: posterior cov has a negative eigenvalue {np.min(eigvals)!r}")
    return {"trials": 20}


def check_independent_conditioning_cross_check():
    """Never call predict()+update() against itself: build the JOINT Gaussian
    distribution of (x1, y1) analytically and condition it directly with the
    textbook Gaussian-conditioning formula, then compare to predict()+update()."""
    rng = np.random.default_rng(2)
    F = np.array([[0.9, 0.2], [-0.1, 0.7]])
    W0 = np.array([[0.3, 0.05], [0.05, 0.2]])
    H = np.array([[1.0, 0.5]])
    R = np.array([[0.4]])
    P0 = np.array([[1.0, 0.1], [0.1, 0.8]])
    m0 = np.array([0.3, -0.2])
    y_obs = np.array([1.1])

    # Method A: this module's predict() then update().
    prior = make_state(m0, P0)
    pred = predict(prior, F=F, W=W0)
    repA = update(pred, y=y_obs, H=H, R=R)

    # Method B: independent direct joint-Gaussian conditioning.
    # x1 = F x0 + w0  ->  mean F@m0, cov F P0 F^T + W0  (identical algebra to predict(),
    # but written out here independently rather than calling predict() again).
    m1 = F @ m0
    P1 = F @ P0 @ F.T + W0
    # y1 = H x1 + v1  -> joint (x1,y1) is Gaussian with
    #   Cov(x1,y1) = P1 H^T,   Cov(y1) = H P1 H^T + R
    cov_x1_y1 = P1 @ H.T
    cov_y1 = H @ P1 @ H.T + R
    m_y1 = H @ m1
    # Standard Gaussian conditioning: E[x1|y1] = m1 + Cov(x1,y1) Cov(y1)^-1 (y1-m_y1)
    gain_B = cov_x1_y1 @ np.linalg.inv(cov_y1)
    m1_post = m1 + (gain_B @ (y_obs - m_y1))
    P1_post = P1 - gain_B @ cov_x1_y1.T

    allclose(repA.state.mean, m1_post, atol=1e-8, msg="cross-check posterior mean")
    allclose(repA.state.cov, P1_post, atol=1e-8, msg="cross-check posterior cov")
    return {"mean_A": repA.state.mean.tolist(), "mean_B": m1_post.tolist()}


def check_singular_innovation_raises():
    prior = make_state([0.0], np.array([[1.0]]))
    H = np.array([[0.0]])  # observes nothing about the state
    R = np.array([[0.0]])  # and has zero measurement noise -> S = 0, singular
    try:
        update(prior, y=[5.0], H=H, R=R)
        raise AssertionError("singular innovation covariance should raise ScopeViolationError")
    except ScopeViolationError:
        pass
    return {"raised": True}


CHECKS = [
    ("control_case_update", check_control_case_update),
    ("predict_after_update_control_case", check_predict_after_update_control_case),
    ("observability_control_case", check_observability_control_case),
    ("joseph_form_symmetric_psd", check_joseph_form_symmetric_psd),
    ("independent_conditioning_cross_check", check_independent_conditioning_cross_check),
    ("singular_innovation_raises", check_singular_innovation_raises),
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json-out", type=Path, default=Path(__file__).with_name("verify_linear_state_estimation_results.json"))
    args = parser.parse_args()

    report = {
        "package": "INTEGRATED_EXTENSION_ROADMAP.md Paket C1 (linear-Gaussian state estimation core)",
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
