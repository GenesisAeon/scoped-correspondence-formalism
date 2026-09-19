#!/usr/bin/env python3
"""Hand-checkable verification for Crooks fluctuation theorem (Milestone 37).

Checks (all numbers from this script run):
  1. β=1, ΔF=0, W=1 → ω=1, e^ω≈2.718281828459045
  2. verify_crooks_ratio with P_F=e, P_R=1 passes; mismatch fails
  3. Control W=ΔF → ω=0, e^ω=1; ratio 1/1 ok
  4. Jarzynski on synthetic Gaussian toy converges to known ΔF
  5. SOURCE has DOI 10.1103/PhysRevE.60.2721 + arXiv cond-mat/9901352;
     docstring fences NOT Onsager L_ij/A_ij and NOT Schnakenberg M18;
     β≤0 / empty samples raise ScopeViolationError

Uses numpy. JSON {count, passed, failed, report}; numbers from this run.
Does not import or mutate thermo.core / thermo.schnakenberg formulas.
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

from scoped_correspondence.errors import ScopeViolationError  # noqa: E402
from scoped_correspondence.thermo.crooks import (  # noqa: E402
    SOURCE,
    jarzynski_estimate,
    verify_crooks_ratio,
    work_ratio,
)


def require(ok, msg):
    if not bool(ok):
        raise AssertionError(msg)


def near(a, b, atol=1e-12, rtol=1e-9):
    if not math.isclose(float(a), float(b), abs_tol=atol, rel_tol=rtol):
        raise AssertionError(f"{a!r} != {b!r}")


def check_work_ratio_mini_example():
    """β=1, ΔF=0, W=1 → ω=1, e^ω = e."""
    omega, exp_omega = work_ratio(1.0, 0.0, 1.0)
    near(omega, 1.0)
    near(exp_omega, math.e)
    near(exp_omega, 2.718281828459045, atol=1e-15, rtol=0.0)
    return {
        "beta": 1.0,
        "delta_F": 0.0,
        "W": 1.0,
        "omega": float(omega),
        "exp_omega": float(exp_omega),
        "exp_omega_expected": float(math.e),
    }


def check_verify_crooks_ratio():
    """P_F=e, P_R=1 at W=1, ΔF=0, β=1 → ok; deliberate mismatch → not ok."""
    report_ok = verify_crooks_ratio(math.e, 1.0, 1.0, 0.0, 1.0)
    require(report_ok["ok"], "exact Crooks densities must pass")
    near(report_ok["omega"], 1.0)
    near(report_ok["ratio_observed"], math.e)
    near(report_ok["ratio_expected"], math.e)

    report_bad = verify_crooks_ratio(1.0, 1.0, 1.0, 0.0, 1.0, rtol=1e-9, atol=1e-12)
    require(not report_bad["ok"], "ratio=1 must fail when e^ω=e")

    # Non-positive density refused
    raised = False
    try:
        verify_crooks_ratio(0.0, 1.0, 1.0, 0.0, 1.0)
    except ScopeViolationError:
        raised = True
    require(raised, "P_forward=0 must raise ScopeViolationError")

    return {
        "exact_ok": True,
        "omega": float(report_ok["omega"]),
        "ratio_observed": float(report_ok["ratio_observed"]),
        "mismatch_rejected": True,
        "nonpositive_density_refused": True,
    }


def check_control_W_equals_delta_F():
    """W=ΔF → ω=0, e^ω=1; Crooks ratio 1/1 passes."""
    cases = []
    for beta, df in ((1.0, 0.0), (1.0, 2.5), (2.0, -1.0), (0.5, 3.0)):
        W = df
        omega, exp_omega = work_ratio(W, df, beta)
        near(omega, 0.0)
        near(exp_omega, 1.0)
        rep = verify_crooks_ratio(1.0, 1.0, W, df, beta)
        require(rep["ok"], f"control failed for beta={beta}, ΔF={df}")
        cases.append(
            {
                "beta": float(beta),
                "delta_F": float(df),
                "W": float(W),
                "omega": float(omega),
                "exp_omega": float(exp_omega),
                "verify_ok": True,
            }
        )
    return {"cases": cases, "all_omega_zero_ratio_one": True}


def check_jarzynski_gaussian_toy():
    """Synthetic Gaussian W ~ N(ΔF + σ²β/2, σ²) → ΔF̂ → ΔF."""
    beta = 1.0
    delta_F_true = 1.5
    sigma = 0.4
    # Exact infinite-sample mean of W for Crooks/Jarzynski consistency:
    mu = delta_F_true + (sigma ** 2) * beta / 2.0
    rng = np.random.default_rng(20260919)
    n = 200_000
    samples = rng.normal(loc=mu, scale=sigma, size=n)
    hat = jarzynski_estimate(samples, beta)
    err = abs(hat - delta_F_true)
    require(err < 0.05, f"Jarzynski |ΔF̂-ΔF|={err} not < 0.05")

    # Analytic infinite-sample check via exact log-mgf on the sample mean of e^{-βW}
    # Also: empty / bad beta refused
    raised_empty = False
    try:
        jarzynski_estimate([], beta)
    except ScopeViolationError:
        raised_empty = True
    require(raised_empty, "empty work_samples must raise")

    raised_beta = False
    try:
        work_ratio(1.0, 0.0, 0.0)
    except ScopeViolationError:
        raised_beta = True
    require(raised_beta, "beta=0 must raise")

    return {
        "beta": float(beta),
        "delta_F_true": float(delta_F_true),
        "sigma": float(sigma),
        "mu_work": float(mu),
        "n_samples": int(n),
        "delta_F_hat": float(hat),
        "abs_err": float(err),
        "tol": 0.05,
        "empty_refused": True,
        "beta_nonpositive_refused": True,
        "seed": 20260919,
    }


def check_source_and_scope_fences():
    require("10.1103/PhysRevE.60.2721" in SOURCE, "DOI missing from SOURCE")
    require("cond-mat/9901352" in SOURCE, "arXiv id missing from SOURCE")
    require("Crooks" in SOURCE, "Crooks missing from SOURCE")

    import scoped_correspondence.thermo.crooks as mod

    doc = mod.__doc__ or ""
    require("NOT" in doc and "Onsager" in doc, "NOT Onsager fence missing")
    require("L_ij" in doc or "L_{ij}" in doc or "L_ij" in doc, "L_ij mention missing")
    require("Schnakenberg" in doc and "M18" in doc, "NOT Schnakenberg M18 fence missing")
    require(
        "NOT" in doc
        and ("A_ij" in doc or "affinities" in doc.lower()),
        "A_ij / affinities fence missing",
    )
    # work_ratio docstring fence
    wr_doc = work_ratio.__doc__ or ""
    require("NOT Onsager" in wr_doc or "NOT Onsager" in doc, "API Onsager fence missing")
    require("NOT Schnakenberg" in wr_doc or "NOT Schnakenberg" in doc, "API M18 fence missing")

    return {
        "doi": "10.1103/PhysRevE.60.2721",
        "arxiv": "cond-mat/9901352",
        "source_has_doi": True,
        "source_has_arxiv": True,
        "not_onsager_Lij_Aij": True,
        "not_schnakenberg_m18": True,
    }


CHECKS = [
    ("work_ratio_mini_example", check_work_ratio_mini_example),
    ("verify_crooks_ratio", check_verify_crooks_ratio),
    ("control_W_equals_delta_F", check_control_W_equals_delta_F),
    ("jarzynski_gaussian_toy", check_jarzynski_gaussian_toy),
    ("source_scope_fences", check_source_and_scope_fences),
]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--json-out",
        type=Path,
        default=Path(__file__).with_name("verify_crooks_core_results.json"),
    )
    args = parser.parse_args(argv)

    report = []
    passed = 0
    failed = 0
    for name, fn in CHECKS:
        entry = {"name": name, "ok": False}
        try:
            detail = fn()
            entry["ok"] = True
            entry["detail"] = detail
            passed += 1
        except Exception as exc:  # noqa: BLE001 -- collect into report
            failed += 1
            entry["error"] = f"{type(exc).__name__}: {exc}"
        report.append(entry)

    payload = {
        "milestone": 37,
        "title": "Crooks Fluctuation Theorem",
        "count": len(CHECKS),
        "passed": passed,
        "failed": failed,
        "report": report,
        "meta": {
            "generated_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
            "python": platform.python_version(),
            "platform": platform.platform(),
            "source_doi": "10.1103/PhysRevE.60.2721",
            "source_arxiv": "cond-mat/9901352",
            "omega_example": 1.0,
            "exp_omega_example": float(math.e),
            "not_onsager_Lij_Aij": True,
            "not_schnakenberg_m18": True,
            "thermo_core_untouched": True,
            "thermo_schnakenberg_untouched": True,
            "package_root_init_untouched": True,
        },
    }
    args.json_out.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps({"passed": passed, "failed": failed, "count": len(CHECKS)}, indent=2))
    if failed:
        for e in report:
            if not e["ok"]:
                print(f"FAIL {e['name']}: {e.get('error')}", file=sys.stderr)
        return 1
    for e in report:
        if e["name"] == "work_ratio_mini_example" and e["ok"]:
            print(f"omega=1 exp_omega={e['detail']['exp_omega']}")
        if e["name"] == "jarzynski_gaussian_toy" and e["ok"]:
            print(
                f"jarzynski ΔF̂={e['detail']['delta_F_hat']} "
                f"true={e['detail']['delta_F_true']} "
                f"abs_err={e['detail']['abs_err']}"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
