#!/usr/bin/env python3
"""Hand-checkable verification for free_boundary / Stefan–Neumann (Milestone 31).

Checks (numbers from THIS script run; residuals recomputed from the equation,
not only hardcoded λ targets):

  1. Ste ∈ {1.0, 0.5, 0.1}: neumann_lambda; residual of
     λ·exp(λ²)·erf(λ) vs Ste/√π is < 1e-9; λ near ≈0.620063 / 0.464786 / 0.220016.
  2. Ste=1, α=1 mm²/s: s(100)≈12.40 mm, s(400)≈24.80 mm; ratio exactly 2
     (√t law) as own JSON field ``sqrt_t_ratio_s400_over_s100``.
  3. Control Ste=0.01: λ clearly smaller than for Ste=0.1.
  4. ScopeViolationError for Ste<=0 and for x outside [0, s(t)].
  5. Sources Kot 2017 + Bollati arXiv:1906.08601; no Stefan 1891 / Rubinstein 1971;
     docstring states NOT a viability subclass.

Stdlib only beyond package. JSON {count, passed, failed, report}.
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
from scoped_correspondence.free_boundary import (  # noqa: E402
    SOURCE,
    melt_front_position,
    neumann_lambda,
    stefan_number,
    temperature_profile,
)
from scoped_correspondence.free_boundary import core as fb_core  # noqa: E402


def require(ok, msg):
    if not bool(ok):
        raise AssertionError(msg)


def near(a, b, atol=1e-9, rtol=1e-6):
    if not math.isclose(float(a), float(b), abs_tol=atol, rel_tol=rtol):
        raise AssertionError(f"{a!r} != {b!r} (atol={atol}, rtol={rtol})")


def eqn_lhs(lam: float) -> float:
    return lam * math.exp(lam * lam) * math.erf(lam)


def eqn_residual(lam: float, ste: float) -> float:
    return abs(eqn_lhs(lam) - ste / math.sqrt(math.pi))


TARGETS = {
    1.0: 0.620063,
    0.5: 0.464786,
    0.1: 0.220016,
}


def check_neumann_roots_and_residuals():
    cases = []
    for ste, target in TARGETS.items():
        out = neumann_lambda(ste)
        lam = float(out["lambda"])
        res = eqn_residual(lam, ste)
        require(res < 1e-9, f"Ste={ste}: residual {res} >= 1e-9")
        near(out["residual"], res, atol=1e-14, rtol=1e-9)
        near(lam, target, atol=5e-6, rtol=1e-5)
        require(int(out["iterations"]) > 0, "iterations must be positive")
        cases.append(
            {
                "Ste": ste,
                "lambda": lam,
                "lambda_target_approx": target,
                "iterations": int(out["iterations"]),
                "residual_reported": float(out["residual"]),
                "residual_recomputed": res,
                "lhs": eqn_lhs(lam),
                "rhs_Ste_over_sqrt_pi": ste / math.sqrt(math.pi),
            }
        )
    return {
        "cases": cases,
        "max_residual": max(c["residual_recomputed"] for c in cases),
    }


def check_sqrt_t_law():
    ste = 1.0
    alpha = 1.0  # mm^2/s
    out = neumann_lambda(ste)
    lam = float(out["lambda"])
    s100 = melt_front_position(lam, alpha, 100.0)
    s400 = melt_front_position(lam, alpha, 400.0)
    ratio = s400 / s100
    near(s100, 12.40, atol=0.02, rtol=0.0)
    near(s400, 24.80, atol=0.02, rtol=0.0)
    require(ratio == 2.0, f"√t ratio must be exactly 2.0, got {ratio!r}")
    T0 = 1.0
    T_surface = temperature_profile(0.0, 100.0, lam, alpha, T0)
    T_front = temperature_profile(s100, 100.0, lam, alpha, T0)
    near(T_surface, T0, atol=1e-12)
    near(T_front, 0.0, atol=1e-12)
    return {
        "Ste": ste,
        "alpha_mm2_per_s": alpha,
        "lambda": lam,
        "s_100_mm": s100,
        "s_400_mm": s400,
        "sqrt_t_ratio_s400_over_s100": ratio,
        "T_surface_t100": T_surface,
        "T_front_t100": T_front,
    }


def check_control_small_Ste():
    out_small = neumann_lambda(0.01)
    out_ref = neumann_lambda(0.1)
    lam_s = float(out_small["lambda"])
    lam_r = float(out_ref["lambda"])
    require(lam_s < lam_r, f"expected λ(0.01)={lam_s} < λ(0.1)={lam_r}")
    require(lam_s < 0.15, f"λ(0.01) should be clearly small; got {lam_s}")
    require(eqn_residual(lam_s, 0.01) < 1e-9, "control residual")
    ste_api = stefan_number(1.0, 0.01, 1.0)
    near(ste_api, 0.01)
    return {
        "Ste_control": 0.01,
        "lambda_Ste_0_01": lam_s,
        "lambda_Ste_0_1": lam_r,
        "clearly_smaller": True,
        "stefan_number_api": ste_api,
        "residual_Ste_0_01": eqn_residual(lam_s, 0.01),
    }


def check_scope_violations():
    raised_ste = False
    try:
        neumann_lambda(0.0)
    except ScopeViolationError:
        raised_ste = True
    require(raised_ste, "Ste=0 must raise ScopeViolationError")

    raised_neg = False
    try:
        neumann_lambda(-1.0)
    except ScopeViolationError:
        raised_neg = True
    require(raised_neg, "Ste<0 must raise ScopeViolationError")

    out = neumann_lambda(1.0)
    lam = float(out["lambda"])
    alpha, t, T0 = 1.0, 100.0, 1.0
    s = melt_front_position(lam, alpha, t)

    raised_outside = False
    try:
        temperature_profile(s + 1.0, t, lam, alpha, T0)
    except ScopeViolationError:
        raised_outside = True
    require(raised_outside, "x > s(t) must raise ScopeViolationError")

    raised_neg_x = False
    try:
        temperature_profile(-0.1, t, lam, alpha, T0)
    except ScopeViolationError:
        raised_neg_x = True
    require(raised_neg_x, "x < 0 must raise ScopeViolationError")

    return {
        "Ste_le_0_raises": raised_ste and raised_neg,
        "x_outside_raises": raised_outside and raised_neg_x,
        "s_t_for_probe": s,
    }


def check_sources_and_viability_disclaimer():
    src = SOURCE
    doc = fb_core.__doc__ or ""
    init_doc = (
        __import__(
            "scoped_correspondence.free_boundary", fromlist=["__doc__"]
        ).__doc__
        or ""
    )
    combined = src + "\n" + doc + "\n" + init_doc
    low = combined.lower()

    require("10.1007/s10891-017-1638-2" in combined, "Kot 2017 DOI missing")
    require("1906.08601" in combined, "Bollati arXiv missing")
    require("kot" in low, "Kot name missing")
    require("bollati" in low, "Bollati name missing")

    # Forbidden citations must not appear as sources (SOURCE field only).
    # Docstring may mention them only as excluded.
    require("1891" not in src, "SOURCE must not cite Stefan 1891")
    require("1971" not in src, "SOURCE must not cite Rubinstein 1971")
    require("stefan" not in src.lower(), "SOURCE must not name Stefan")
    require("rubinstein" not in src.lower(), "SOURCE must not name Rubinstein")

    require(
        "not" in low and "viability" in low,
        "docstring must explain NOT a viability subclass",
    )
    require(
        "dynamic" in low
        and ("variable" in low or "s(t)" in low or "boundary" in low),
        "docstring must mention dynamic boundary variable",
    )

    return {
        "SOURCE": SOURCE,
        "cites_kot_2017_doi": True,
        "cites_bollati_arxiv_1906_08601": True,
        "stefan_1891_not_cited": True,
        "rubinstein_1971_not_cited": True,
        "not_viability_subclass_stated": True,
    }


CHECKS = [
    ("neumann_roots_and_residuals", check_neumann_roots_and_residuals),
    ("sqrt_t_law", check_sqrt_t_law),
    ("control_small_Ste", check_control_small_Ste),
    ("scope_violations", check_scope_violations),
    ("sources_and_viability_disclaimer", check_sources_and_viability_disclaimer),
]


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).with_name("verify_free_boundary_core_results.json"),
    )
    args = parser.parse_args(argv)

    results = []
    report = {}
    failed = 0
    for name, fn in CHECKS:
        try:
            detail = fn()
            results.append({"name": name, "ok": True, "detail": detail})
            report[name] = detail
        except Exception as exc:  # noqa: BLE001
            failed += 1
            err = f"{type(exc).__name__}: {exc}"
            results.append({"name": name, "ok": False, "error": err})
            report[name] = {"error": err}

    passed = len(CHECKS) - failed
    sqrt_ratio = None
    if isinstance(report.get("sqrt_t_law"), dict):
        sqrt_ratio = report["sqrt_t_law"].get("sqrt_t_ratio_s400_over_s100")

    payload = {
        "count": len(CHECKS),
        "passed": passed,
        "failed": failed,
        "sqrt_t_ratio_s400_over_s100": sqrt_ratio,
        "report": {
            **report,
            "meta": {
                "milestone": 31,
                "title": "Free Boundary / One-Phase Stefan–Neumann",
                "branch": "aeon/m31-free-boundary-stefan",
                "source": SOURCE,
                "python": platform.python_version(),
                "platform": platform.platform(),
                "utc": dt.datetime.now(dt.timezone.utc).isoformat(),
            },
        },
        "results": results,
    }

    args.out.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "passed": passed,
                "failed": failed,
                "count": len(CHECKS),
                "out": str(args.out),
            }
        )
    )
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
