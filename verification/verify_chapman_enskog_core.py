#!/usr/bin/env python3
"""Hand-checkable verification for Chapman–Enskog / BGK closure (Milestone 40).

Checks (numbers from this script run):
  1. Unit example p=τ=m=k_B=1 → μ=1, κ=2.5; c_p=5/2 → Pr=1.0 exact;
     vs physical Pr=2/3 factor 1.5.
  2. Air sanity T=300K p=101325 μ=1.846e-5 → τ≈1.8219e-10 s;
     ⟨v⟩≈468.3 m/s; λ≈8.53e-8 m (order-of-magnitude).
  3. Control τ→0 ⇒ μ,κ→0; τ=0 exact zeros.
  4. Structural-analogy docstring / SOURCE present; no Chapman–Cowling
     hard-sphere η formula; closure package exports BGK APIs; CALL
     is_exact_closure / closure_error only as analogy (import check).

Stdlib + math. JSON {count, passed, failed, report}; numbers from this run.
Does not mutate closure.core / error_bounds; does not use hard-sphere η.
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

from scoped_correspondence.closure import chapman_enskog as ce  # noqa: E402
from scoped_correspondence.closure.chapman_enskog import (  # noqa: E402
    PR_BGK,
    PR_BGK_OVER_PHYSICAL,
    PR_MONATOMIC_PHYSICAL,
    SOURCE,
    bgk_transport_coefficients,
    mean_free_path_estimate,
    mean_thermal_speed,
    prandtl_number,
    relaxation_time_from_viscosity,
)
from scoped_correspondence.errors import ScopeViolationError  # noqa: E402


def require(ok, msg):
    if not bool(ok):
        raise AssertionError(msg)


def near(a, b, atol=1e-12, rtol=1e-12):
    if not math.isclose(float(a), float(b), abs_tol=atol, rel_tol=rtol):
        raise AssertionError(f"{a!r} != {b!r} (atol={atol}, rtol={rtol})")


def check_unit_bgk_prandtl():
    """p=τ=m=k_B=1 → μ=1, κ=2.5; Pr=1.0; factor 1.5 vs 2/3."""
    mu, kappa = bgk_transport_coefficients(1.0, 1.0, 1.0, k_B=1.0)
    near(mu, 1.0)
    near(kappa, 2.5)
    c_p = 5.0 / 2.0
    pr = prandtl_number(mu, kappa, c_p)
    near(pr, 1.0)
    near(pr, PR_BGK)
    near(PR_MONATOMIC_PHYSICAL, 2.0 / 3.0)
    near(PR_BGK / PR_MONATOMIC_PHYSICAL, 1.5)
    near(PR_BGK_OVER_PHYSICAL, 1.5)
    # Inverse: τ from μ,p
    near(relaxation_time_from_viscosity(mu, 1.0), 1.0)
    return {
        "mu": mu,
        "kappa": kappa,
        "c_p": c_p,
        "Pr_BGK": pr,
        "Pr_physical_monatomic": PR_MONATOMIC_PHYSICAL,
        "Pr_BGK_over_physical": PR_BGK / PR_MONATOMIC_PHYSICAL,
    }


def check_air_sanity():
    """Air T=300K p=101325 μ=1.846e-5 → τ, ⟨v⟩, λ order-of-magnitude."""
    T = 300.0
    p = 101325.0
    mu = 1.846e-5
    # Dry air molar mass (kg/mol) and constants (SI)
    M = 28.97e-3
    N_A = 6.02214076e23
    k_B = 1.380649e-23
    m = M / N_A

    tau = relaxation_time_from_viscosity(mu, p)
    near(tau, 1.8219e-10, atol=5e-15, rtol=1e-4)

    v_mean = mean_thermal_speed(T, m, k_B=k_B)
    near(v_mean, 468.3, atol=0.5, rtol=0.0)

    lam = mean_free_path_estimate(v_mean, tau)
    near(lam, 8.53e-8, atol=5e-10, rtol=0.01)

    # Consistency: μ,κ from (p,τ) recover input μ
    mu2, kappa2 = bgk_transport_coefficients(p, tau, m, k_B=k_B)
    near(mu2, mu, atol=1e-18, rtol=1e-12)
    c_p = (5.0 / 2.0) * (k_B / m)
    pr = prandtl_number(mu2, kappa2, c_p)
    near(pr, 1.0)

    return {
        "T_K": T,
        "p_Pa": p,
        "mu_Pa_s": mu,
        "m_kg": m,
        "tau_s": tau,
        "mean_speed_m_s": v_mean,
        "mean_free_path_m": lam,
        "Pr_BGK_air": pr,
        "note": "λ≈⟨v⟩·τ is order-of-magnitude only; not a precision claim",
    }


def check_tau_to_zero_control():
    """τ→0 ⇒ μ,κ→0; τ=0 exact zeros; rejects negative inputs."""
    mu0, k0 = bgk_transport_coefficients(101325.0, 0.0, 1.0, k_B=1.0)
    near(mu0, 0.0)
    near(k0, 0.0)

    # Tiny τ
    mu_eps, k_eps = bgk_transport_coefficients(1.0, 1e-16, 2.0, k_B=1.0)
    near(mu_eps, 1e-16)
    near(k_eps, (5.0 / 2.0) * (1.0 / 2.0) * 1e-16)

    raised = False
    try:
        bgk_transport_coefficients(1.0, -1.0, 1.0)
    except ScopeViolationError:
        raised = True
    require(raised, "expected ScopeViolationError for tau<0")

    raised_p = False
    try:
        relaxation_time_from_viscosity(1.0, 0.0)
    except ScopeViolationError:
        raised_p = True
    require(raised_p, "expected ScopeViolationError for p=0")

    return {
        "mu_tau0": mu0,
        "kappa_tau0": k0,
        "mu_tau_1e-16": mu_eps,
        "kappa_tau_1e-16": k_eps,
        "rejects_negative_tau": raised,
        "rejects_zero_p_inverse": raised_p,
    }


def check_docs_exports_and_no_hard_sphere():
    """SOURCE / analogy docstring; package exports; no hard-sphere η."""
    require("10.1103/PhysRev.94.511" in SOURCE, SOURCE)
    require("10.1063/1.1761920" in SOURCE, SOURCE)
    require("BGK" in SOURCE, SOURCE)

    mod_doc = ce.__doc__ or ""
    require("structural analogy" in mod_doc.lower() or "Structural analogy" in mod_doc, mod_doc[:200])
    require("is_exact_closure" in mod_doc, "missing is_exact_closure analogy")
    require("closure_error" in mod_doc, "missing closure_error analogy")
    require("NOT" in mod_doc or "not" in mod_doc, "missing NOT-identity wording")
    require("M11" in mod_doc and "M21" in mod_doc, "missing M11/M21 disclaimer")
    require(
        "hard-sphere" in mod_doc.lower() or "Chapman–Cowling" in mod_doc or "Chapman-Cowling" in mod_doc,
        "missing hard-sphere exclusion",
    )
    # Must not define Chapman–Cowling hard-sphere constant 5/(16√π)
    src_text = Path(ce.__file__).read_text(encoding="utf-8")
    require("16" not in src_text or "sqrt(pi)" not in src_text.replace(" ", "").lower()
            or "5/(16" not in src_text.replace(" ", ""), "suspicious hard-sphere formula")
    # Stronger: ban the classic CE hard-sphere prefactor pattern
    require("5/(16" not in src_text.replace(" ", "") and "5 / (16" not in src_text, src_text)

    # Package-level exports (wired __init__)
    import scoped_correspondence.closure as closure_pkg

    for name in (
        "bgk_transport_coefficients",
        "prandtl_number",
        "relaxation_time_from_viscosity",
    ):
        require(hasattr(closure_pkg, name), f"closure missing export {name}")
        require(name in closure_pkg.__all__, f"{name} not in __all__")

    # CALL analogy targets exist (do not claim identity)
    from scoped_correspondence.closure.core import closure_error, is_exact_closure

    require(callable(is_exact_closure) and callable(closure_error), "core CALL failed")

    return {
        "SOURCE": SOURCE,
        "exports": [
            "bgk_transport_coefficients",
            "prandtl_number",
            "relaxation_time_from_viscosity",
        ],
        "analogy_targets_callable": True,
        "hard_sphere_eta_absent": True,
        "doi_bgk": "10.1103/PhysRev.94.511",
        "doi_holway": "10.1063/1.1761920",
    }


def main():
    checks = [
        ("unit_bgk_prandtl", check_unit_bgk_prandtl),
        ("air_sanity", check_air_sanity),
        ("tau_to_zero_control", check_tau_to_zero_control),
        ("docs_exports_no_hard_sphere", check_docs_exports_and_no_hard_sphere),
    ]
    report = {
        "milestone": "M40",
        "module": "scoped_correspondence.closure.chapman_enskog",
        "timestamp_local": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "platform": platform.platform(),
        "python": sys.version.split()[0],
        "checks": {},
    }
    passed = 0
    failed = 0
    errors = []
    for name, fn in checks:
        try:
            report["checks"][name] = {"ok": True, "data": fn()}
            passed += 1
            print(f"PASS {name}")
        except Exception as exc:  # noqa: BLE001 — collect all failures
            failed += 1
            report["checks"][name] = {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
            errors.append(f"{name}: {exc}")
            print(f"FAIL {name}: {exc}")

    out = {
        "count": len(checks),
        "passed": passed,
        "failed": failed,
        "report": report,
        "errors": errors,
        "Pr_BGK": 1.0,
        "SOURCE": SOURCE,
    }
    out_path = Path(__file__).with_name("verify_chapman_enskog_core_results.json")
    out_path.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {out_path}")
    print(f"SUMMARY {passed}/{len(checks)} passed")
    if failed:
        sys.exit(1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
