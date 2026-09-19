#!/usr/bin/env python3
"""Hand-checkable verification for Fisher-Information Sloppiness (Milestone 23).

Checks (all numbers from this script run):
  1. Exponential decay f=theta1*exp(-theta2*t) at t={1,2}, theta=(1,1), sigma=1
     -> hand Jacobian; FIM; stiff/sloppy; anisotropy ~ 50.92
  2. Isotropic control: g=I -> anisotropy == 1.0
  3. Scope: sigma<=0 / empty J / non-square g / singular g raise
     ScopeViolationError
  4. SOURCE / DOIs present; FIM formula is J.T@J/sigma^2 (not equated to
     jacobian_rank)

JSON {count, passed, failed, report}; numbers from this run.
Does not import or mutate identifiability.core / profile_likelihood.
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

import numpy as np  # noqa: E402

from scoped_correspondence.errors import ScopeViolationError  # noqa: E402
from scoped_correspondence.identifiability.fim_sloppiness import (  # noqa: E402
    PRL_DOI,
    RAJU_DOI,
    SOURCE,
    eigenspectrum_report,
    exponential_decay_jacobian,
    fisher_information_matrix,
)


def require(ok, msg):
    if not bool(ok):
        raise AssertionError(msg)


def near(a, b, atol=1e-9, rtol=1e-9):
    if not math.isclose(float(a), float(b), abs_tol=atol, rel_tol=rtol):
        raise AssertionError(f"{a!r} != {b!r} (atol={atol}, rtol={rtol})")


def check_exponential_decay_sloppy():
    """Hand Jacobian + FIM for f=theta1*exp(-theta2*t) at t={1,2}, theta=(1,1), sigma=1."""
    theta = [1.0, 1.0]
    times = [1.0, 2.0]
    sigma = 1.0

    J = exponential_decay_jacobian(theta, times)
    # Hand-derived entries
    e1 = math.exp(-1.0)
    e2 = math.exp(-2.0)
    J_hand = np.array([[e1, -1.0 * 1.0 * e1], [e2, -1.0 * 2.0 * e2]], dtype=float)
    require(J.shape == (2, 2), f"J.shape={J.shape}")
    require(np.allclose(J, J_hand, atol=1e-12), "J mismatch vs hand formula")

    g = fisher_information_matrix(J, sigma)
    g_hand = (J_hand.T @ J_hand) / (sigma ** 2)
    require(np.allclose(g, g_hand, atol=1e-12), "g mismatch vs J.T@J/sigma^2")
    require(np.allclose(g, g.T, atol=1e-14), "g not symmetric")

    rep = eigenspectrum_report(g)
    evals = rep["eigenvalues"]
    require(len(evals) == 2, f"len(evals)={len(evals)}")
    require(evals[0] >= evals[1], "eigenvalues not descending")
    near(rep["lambda_max"], evals[0])
    near(rep["lambda_min"], evals[1])
    near(rep["anisotropy"], evals[0] / evals[1])

    # Concrete expected band from hand eigh (documented ~50.92)
    require(rep["anisotropy"] > 10.0, f"expected strong anisotropy; got {rep['anisotropy']}")
    require(rep["anisotropy"] < 200.0, f"anisotropy unexpectedly huge: {rep['anisotropy']}")
    near(rep["lambda_max"], 0.3552717, atol=1e-5, rtol=1e-5)
    near(rep["lambda_min"], 0.00697706, atol=1e-6, rtol=1e-5)
    near(rep["anisotropy"], 50.9199678, atol=1e-4, rtol=1e-5)

    # Stiff / sloppy are unit eigenvectors (up to sign)
    stiff = np.asarray(rep["stiff_direction"], dtype=float)
    sloppy = np.asarray(rep["sloppy_direction"], dtype=float)
    near(np.linalg.norm(stiff), 1.0, atol=1e-9)
    near(np.linalg.norm(sloppy), 1.0, atol=1e-9)
    near(abs(float(stiff @ sloppy)), 0.0, atol=1e-8)

    # Rayleigh quotients recover eigenvalues
    near(float(stiff @ g @ stiff), rep["lambda_max"], atol=1e-8)
    near(float(sloppy @ g @ sloppy), rep["lambda_min"], atol=1e-8)

    require("10.1103/PhysRevE.83.036701" in SOURCE, "Transtrum DOI missing")
    require("10.1103/PhysRevE.98.052112" in SOURCE or "052112" in SOURCE, "Raju")
    require(PRL_DOI in str(rep.get("doi_transtrum", "")), "doi_transtrum")
    require(RAJU_DOI in str(rep.get("doi_raju", "")), "doi_raju")

    return {
        "model": "f=theta1*exp(-theta2*t)",
        "theta": theta,
        "times": times,
        "sigma": sigma,
        "jacobian": J.tolist(),
        "jacobian_hand": J_hand.tolist(),
        "fim": g.tolist(),
        "eigenvalues": evals,
        "lambda_max": rep["lambda_max"],
        "lambda_min": rep["lambda_min"],
        "anisotropy": rep["anisotropy"],
        "stiff_direction": rep["stiff_direction"],
        "sloppy_direction": rep["sloppy_direction"],
        "formula": "g = J.T @ J / sigma**2",
        "note": "NOT equated to identifiability_jacobian_rank (SVD rank of J)",
    }


def check_isotropic_identity():
    """Identity FIM -> anisotropy exactly 1."""
    g = np.eye(3)
    rep = eigenspectrum_report(g)
    near(rep["anisotropy"], 1.0, atol=1e-12)
    near(rep["lambda_max"], 1.0, atol=1e-12)
    near(rep["lambda_min"], 1.0, atol=1e-12)
    require(all(math.isclose(x, 1.0, abs_tol=1e-12) for x in rep["eigenvalues"]), "evals")
    return {
        "fim": "identity_3x3",
        "anisotropy": rep["anisotropy"],
        "eigenvalues": rep["eigenvalues"],
        "lambda_max": rep["lambda_max"],
        "lambda_min": rep["lambda_min"],
    }


def check_scope_guards():
    """Bad sigma / empty J / non-square / singular -> ScopeViolationError."""
    cases = []

    def expect(label, fn):
        try:
            fn()
            raise AssertionError(f"{label}: expected ScopeViolationError")
        except ScopeViolationError as exc:
            cases.append({"label": label, "raised": type(exc).__name__, "msg": str(exc)[:120]})

    expect("sigma_nonpositive", lambda: fisher_information_matrix([[1.0, 0.0]], 0.0))
    expect("sigma_negative", lambda: fisher_information_matrix([[1.0]], -1.0))
    expect("empty_jacobian", lambda: fisher_information_matrix([], 1.0))
    expect(
        "non_square_g",
        lambda: eigenspectrum_report([[1.0, 0.0], [0.0, 1.0], [0.0, 0.0]]),
    )
    # Singular FIM (rank-1): lambda_min=0 -> anisotropy undefined under scoped API
    expect(
        "singular_fim",
        lambda: eigenspectrum_report([[1.0, 0.0], [0.0, 0.0]]),
    )
    expect(
        "bad_theta_len",
        lambda: exponential_decay_jacobian([1.0], [1.0, 2.0]),
    )
    require(len(cases) == 6, f"expected 6 scope cases; got {len(cases)}")
    return {"cases": cases}


def check_not_jacobian_rank_formula():
    """Sanity: FIM is J.T@J/sigma^2; distinct from rank(J) as a quantity."""
    J = exponential_decay_jacobian([1.0, 1.0], [1.0, 2.0])
    g = fisher_information_matrix(J, 1.0)
    # Rank of J is 2 (full); anisotropy is >>1 -- different diagnostics
    rank_J = int(np.linalg.matrix_rank(J, tol=1e-10))
    rep = eigenspectrum_report(g)
    require(rank_J == 2, f"rank(J)={rank_J}")
    require(rep["anisotropy"] > 1.0 + 1e-6, "anisotropy should exceed 1")
    # Explicit formula check already in check 1; record contrast here
    return {
        "jacobian_rank": rank_J,
        "fim_anisotropy": rep["anisotropy"],
        "contrast": (
            "jacobian_rank reports numerical rank of J (structural); "
            "fim anisotropy reports lambda_max/lambda_min of g=J.T@J/sigma^2 (metric). "
            "Same J, different formulas -- not equated."
        ),
        "source_has_transtrum_doi": "10.1103/PhysRevE.83.036701" in SOURCE,
        "source_has_raju_doi": "052112" in SOURCE,
    }


CHECKS = [
    ("exponential_decay_sloppy", check_exponential_decay_sloppy),
    ("isotropic_identity", check_isotropic_identity),
    ("scope_guards", check_scope_guards),
    ("not_jacobian_rank_formula", check_not_jacobian_rank_formula),
]


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--json-out",
        type=Path,
        default=Path(__file__).with_name("verify_fim_sloppiness_core_results.json"),
    )
    args = p.parse_args(argv)

    report = {}
    passed = 0
    failed = 0
    errors = []
    for name, fn in CHECKS:
        try:
            report[name] = fn()
            passed += 1
            print(f"PASS {name}")
        except Exception as exc:  # noqa: BLE001 -- collect all failures
            failed += 1
            errors.append({"check": name, "error": f"{type(exc).__name__}: {exc}"})
            report[name] = {"error": f"{type(exc).__name__}: {exc}"}
            print(f"FAIL {name}: {exc}")

    payload = {
        "milestone": 23,
        "name": "fisher_information_sloppiness",
        "count": len(CHECKS),
        "passed": passed,
        "failed": failed,
        "errors": errors,
        "report": report,
        "meta": {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "timestamp_local": dt.datetime.now().isoformat(timespec="seconds"),
            "source": SOURCE,
            "doi_transtrum": PRL_DOI,
            "doi_raju": RAJU_DOI,
        },
    }
    args.json_out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {args.json_out}")
    print(f"summary: {passed}/{len(CHECKS)} passed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
