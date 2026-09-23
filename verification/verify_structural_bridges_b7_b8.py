#!/usr/bin/env python3
"""Hand-checkable verification for structural bridges B7 and B8.

MECHANISTIC_VALIDATION_ROADMAP.md package 4, response to
prompts/Answers/nicht_stationäre_Treiber/SCF_Review_f8e249f.md (Astra,
2026-09-21) section "Die mathematisch ergiebigste neue Verbindung":
docs/structural_relations.md's bridge-card schema (objects, relation_kind,
construction, claim, scope, assumptions, preserved, lost_or_unchecked,
evidence, failure_witness, transfer_rules), continuing the B1/B2
numbering. Uses ONLY existing repo APIs -- NO new production module, no
shared "kernel API" (Astra's explicit caution: "NICHT als vorschnelle
gemeinsame Kernel-API"):
  - dynamics.energy_balance.fit_energy_balance_model /
    integrate_energy_balance_trajectory
  - viability.rate_dependent_buffer.run_buffer_spike_trajectory
  - validation.covid_renewal.discretized_generation_interval /
    wallinga_lipsitch_r
  - dynamics.etas.etas_branching_ratio

Checks (all numbers from this script run):
  B7 (linear impulse-response systems): the energy balance model's state
     matrix A has two real, negative eigenvalues (fast ~3.6yr / slow
     ~274yr relaxation, matching the module's own "fast/slow relaxation"
     language) -- NOT a decaying oscillation. Its transfer function
     C(sI-A)^-1 B matches Astra's closed-form formula exactly at several
     s values. BOTH the energy balance trajectory and the buffer's
     trajectory are independently reproduced via direct convolution with
     their impulse response (homogeneous term + quadrature, NOT calling
     solve_ivp/matrix-exponential again) and agree with the production
     functions' own output to high precision. FAILURE WITNESS: a
     time-varying relaxation rate breaks the fixed-impulse-response
     convolution by a large margin (not a rounding-level disagreement).
  B8 (positive kernels / branching operators, Hawkes & Oakes 1974): the
     discretized generation-interval weights sum to 1 (their own total
     kernel mass at R=1); for constant R, the renewal kernel R*w_s has
     total mass exactly R -- i.e. R itself IS the Hawkes & Oakes
     branching ratio for this stationary linear process, computed by the
     SAME general principle (total kernel mass = expected direct
     offspring count) as etas_branching_ratio's K*E[...]*kernel_integral,
     applied to a different concrete kernel. FAILURE WITNESS (by
     reference to already-verified results elsewhere in this repo, not
     recomputed here): real R_t is NOT constant (covid_renewal.py's own
     directly-computed series dips below 1 and rises above 1.5 within
     the same window) -- exactly why project_incidence_constant_r
     (package 2) needed to assume constant R, and its forecast errors
     are the visible cost of that assumption; ETAS's own branching ratio
     is similarly fragile (package 1: only ~30% of kernel mass within
     the observed catalog span) for a structurally different reason (a
     power-law vs. exponential-family kernel tail).

JSON {count, passed, failed, report}; numbers from this run. Does not
mutate dynamics/, viability/, or validation/.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import platform
import sys
from pathlib import Path

import numpy as np
import scipy
from scipy.integrate import quad, solve_ivp
from scipy.interpolate import interp1d
from scipy.optimize import brentq

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from scoped_correspondence.dynamics.energy_balance import (  # noqa: E402
    _load_overlap_series,
    fit_energy_balance_model,
    integrate_energy_balance_trajectory,
)
from scoped_correspondence.viability.rate_dependent_buffer import run_buffer_spike_trajectory  # noqa: E402
from scoped_correspondence.validation.covid_renewal import (  # noqa: E402
    discretized_generation_interval,
    wallinga_lipsitch_r,
)
from scoped_correspondence.dynamics.etas import etas_branching_ratio  # noqa: E402


def require(ok, msg):
    if not bool(ok):
        raise AssertionError(msg)


def near(a, b, atol=1e-6):
    if abs(float(a) - float(b)) > atol:
        raise AssertionError(f"{a!r} != {b!r} (atol={atol})")


def check_b7_impulse_response_representation(co2_path, temp_path):
    fit = fit_energy_balance_model(co2_path, temp_path)
    p = fit.params
    Cs, Cd, alpha, gamma, T0 = p.C_s, p.C_d, p.alpha, p.gamma, p.T0

    A = np.array([[-(alpha + gamma) / Cs, gamma / Cs], [gamma / Cd, -gamma / Cd]])
    B = np.array([1.0 / Cs, 0.0])
    C = np.array([1.0, 0.0])

    eigvals, eigvecs = np.linalg.eig(A)
    require(np.allclose(eigvals.imag, 0.0), "eigenvalues must be real (over-damped, not oscillatory)")
    eigvals = eigvals.real
    require(np.all(eigvals < 0), "both eigenvalues must be negative (stable relaxation)")
    fast_rate, slow_rate = min(eigvals), max(eigvals)  # more negative = faster decay; closer to 0 = slower
    fast_timescale_years = -1.0 / fast_rate
    slow_timescale_years = -1.0 / slow_rate
    require(slow_timescale_years > 10 * fast_timescale_years, "expected a genuine fast/slow timescale separation")

    # Transfer function G(s) = C(sI-A)^-1 B, matched against Astra's closed-form formula.
    transfer_checks = []
    for s in (0.1, 0.5, 1.0, 2.3):
        g_statespace = float(C @ np.linalg.inv(s * np.eye(2) - A) @ B)
        g_astra = (Cd * s + gamma) / ((Cs * s + alpha + gamma) * (Cd * s + gamma) - gamma**2)
        near(g_statespace, g_astra, atol=1e-9)
        transfer_checks.append({"s": s, "G_state_space": g_statespace, "G_astra_formula": g_astra})

    # Convolution representation vs. the production function's own output.
    years_all, Tobs_all, F_vals_all = _load_overlap_series(co2_path, temp_path)
    t = np.arange(len(years_all), dtype=float)
    F_interp = interp1d(t, F_vals_all, kind="linear", fill_value="extrapolate")

    Vinv = np.linalg.inv(eigvecs)
    coeffs = (C @ eigvecs) * (Vinv @ B)

    def h(tau):
        return float(np.real(np.sum(coeffs * np.exp(eigvals * tau))))

    def homogeneous(t_target):
        weights = Vinv @ np.array([T0, T0])
        return float(np.real(np.sum((C @ eigvecs) * weights * np.exp(eigvals * t_target))))

    def convolution_value(t_target, n_points=4000):
        ss = np.linspace(0.0, t_target, n_points)
        integrand = np.array([h(t_target - s) * float(F_interp(s)) for s in ss])
        return float(np.trapezoid(integrand, ss))

    production = integrate_energy_balance_trajectory(F_vals_all, p)
    conv_checks = []
    for idx in (30, len(t) - 1):
        y_conv = homogeneous(t[idx]) + convolution_value(t[idx])
        y_prod = float(production[idx])
        near(y_conv, y_prod, atol=1e-4)
        conv_checks.append({"year_index": idx, "convolution": y_conv, "production": y_prod, "diff": abs(y_conv - y_prod)})

    # --- Buffer: same LTI convolution representation, its own (1-state) impulse response. ---
    r, z_eq, U, W0, spike_height, tau = 1.0, 0.0, 0.0, 0.0, 1.0, 1.0
    traj = run_buffer_spike_trajectory(r, z_eq, U, W0, spike_height, tau)
    t0 = traj.t0

    def W(s):
        return W0 + spike_height * np.exp(-((s / tau) ** 2))

    x0 = (U - W0) / r

    def x_of_t(t_target):
        homog = x0 * np.exp(-r * (t_target - t0))
        integral, _ = quad(lambda s: np.exp(-r * (t_target - s)) * (U - W(s)), t0, t_target, limit=400)
        return homog + integral

    z_conv = z_eq + x_of_t(traj.z_min_time)
    near(z_conv, traj.z_min, atol=1e-6)

    # FAILURE WITNESS: a time-varying relaxation rate breaks the fixed-impulse-response
    # convolution by a LARGE margin (not a rounding-level disagreement).
    def r_of_t(tt):
        return 1.0 if tt < 0 else 2.0

    def rhs_time_varying(tt, z):
        return [-r_of_t(tt) * (z[0] - z_eq) + U - W(tt)]

    t0w, t1w = -13.0, 13.0
    z0w = z_eq + (U - W0) / r_of_t(t0w)
    sol = solve_ivp(rhs_time_varying, (t0w, t1w), [z0w], rtol=1e-12, atol=1e-14, dense_output=True, max_step=0.01)
    t_check = 3.0
    z_true = float(sol.sol(t_check)[0])

    def x_of_t_fixed_r1(t_target):
        homog = ((U - W0) / 1.0) * np.exp(-1.0 * (t_target - t0w))
        integral, _ = quad(lambda s: np.exp(-1.0 * (t_target - s)) * (U - W(s)), t0w, t_target, limit=400)
        return homog + integral

    z_wrong_conv = z_eq + x_of_t_fixed_r1(t_check)
    witness_diff = abs(z_true - z_wrong_conv)
    require(witness_diff > 0.05, f"expected the fixed-impulse-response convolution to disagree substantially under a time-varying rate; got diff={witness_diff!r}")

    return {
        "energy_balance_params": p.to_dict(),
        "eigenvalues": eigvals.tolist(),
        "fast_timescale_years": fast_timescale_years,
        "slow_timescale_years": slow_timescale_years,
        "transfer_function_checks": transfer_checks,
        "convolution_vs_production_checks": conv_checks,
        "buffer_convolution_check": {"module_z_min": traj.z_min, "convolution_z_min": z_conv, "diff": abs(z_conv - traj.z_min)},
        "failure_witness_time_varying_rate": {
            "true_trajectory_at_t3": z_true,
            "wrong_fixed_impulse_response_convolution_at_t3": z_wrong_conv,
            "diff": witness_diff,
        },
    }


def check_b8_positive_kernel_branching_operator():
    w = discretized_generation_interval()
    total_mass_at_R1 = float(np.sum(w))
    near(total_mass_at_R1, 1.0, atol=1e-12)

    # For constant R, the renewal kernel phi_s = R * w_s has total mass EXACTLY R --
    # i.e. R itself is the Hawkes & Oakes (1974) branching ratio for this process.
    R_test = 1.68  # Pilot B's Wallinga-Lipsitch-implied R (validation.covid_renewal, already established)
    kernel_total_mass = float(R_test * np.sum(w))
    near(kernel_total_mass, R_test, atol=1e-12)

    # Cross-check: R_test itself IS the Wallinga-Lipsitch-consistent quantity for some
    # growth rate r (round-trip: r -> R -> confirm R*sum(w) reproduces the same R).
    # (Uses wallinga_lipsitch_r only as an independent sanity anchor, not a new claim.)
    r_from_R = brentq(lambda r: wallinga_lipsitch_r(r, w) - R_test, -1.0, 1.0)
    R_roundtrip = wallinga_lipsitch_r(r_from_R, w)
    near(R_roundtrip, R_test, atol=1e-9)

    # Same GENERAL PRINCIPLE (total kernel mass = expected direct offspring count),
    # applied to a structurally different kernel (Omori-Utsu power-law vs. Gamma
    # generation interval) -- computed via the EXISTING etas_branching_ratio, not a
    # new shared API.
    mags = np.array([6.0, 6.5, 7.0, 6.2])
    K, c, p_etas, alpha_etas, m0 = 0.05, 0.1, 1.3, 1.5, 6.0
    n_etas = etas_branching_ratio(K, c, p_etas, alpha_etas, mags, m0)
    require(n_etas > 0, "etas_branching_ratio must be positive (a genuine offspring-count quantity)")

    # Corrected 2026-09-23 in response to
    # prompts/Answers/nicht_stationäre_Treiber/SCF_Review_3e8dce3.md
    # (Astra, finding 3): the kernel-mass identity above (R * sum(w) == R)
    # is correct and needs no stationarity assumption. What was WRONG in
    # docs/structural_relations.md was the FURTHER claim that constant R
    # makes the renewal recursion "exactly a stationary linear Hawkes
    # process" -- constant coefficients do not by themselves guarantee a
    # stationary process distribution. For a linear Hawkes process with
    # positive immigration mu and finite stationary mean, the mean
    # equation lambda_bar = mu + n*lambda_bar => lambda_bar = mu/(1-n)
    # requires the SUBCRITICAL case n < 1 (Hawkes & Oakes 1974). R_test =
    # 1.68 is SUPERCRITICAL (n > 1): plugging it into the "stationary"
    # formula with mu=1 gives a NEGATIVE mean rate -- mathematically
    # impossible for a point-process intensity -- which is exactly why
    # R=1.68 is a COUNTEREXAMPLE to the stationarity claim, not supporting
    # evidence for it. A genuinely subcritical R=0.8 gives a finite,
    # positive stationary mean, as the theory requires.
    mu_immigration = 1.0
    R_subcritical = 0.8
    stationary_mean_subcritical = mu_immigration / (1.0 - R_subcritical)
    require(
        np.isfinite(stationary_mean_subcritical) and stationary_mean_subcritical > 0.0,
        "subcritical R=0.8 must give a finite, positive stationary mean",
    )
    near(stationary_mean_subcritical, 5.0, atol=1e-12)  # 1.0 / (1 - 0.8) = 5.0 exactly

    stationary_mean_at_R_test = mu_immigration / (1.0 - R_test)  # R_test=1.68, superctitical
    require(
        stationary_mean_at_R_test < 0.0,
        "R_test=1.68 (superctitical) must give a NEGATIVE 'stationary mean' -- the "
        "mathematical impossibility that shows constant R does NOT imply a stationary "
        "process here (this is the counterexample, not a supporting computation)",
    )
    near(stationary_mean_at_R_test, -1.0 / 0.68, atol=1e-9)  # matches Astra's -1.4706 by hand

    return {
        "generation_interval_total_mass_at_R1": total_mass_at_R1,
        "R_test": R_test,
        "renewal_kernel_total_mass": kernel_total_mass,
        "r_from_R_roundtrip": r_from_R,
        "R_roundtrip_check": R_roundtrip,
        "etas_branching_ratio_example": n_etas,
        "subcritical_example": {
            "R": R_subcritical,
            "mu_immigration": mu_immigration,
            "stationary_mean": stationary_mean_subcritical,
            "interpretation": "genuinely stationary (n<1): finite positive mean, as theory requires",
        },
        "superctitical_counterexample": {
            "R": R_test,
            "mu_immigration": mu_immigration,
            "would_be_stationary_mean": stationary_mean_at_R_test,
            "interpretation": (
                "R=1.68 is superctitical (n>1): the 'stationary mean' formula gives an "
                "impossible negative rate -- constant R does NOT make this a stationary "
                "Hawkes process; the kernel-mass identity (R*sum(w)=R) still holds and needs "
                "no stationarity, but the stationarity CLAIM in the prior docs text was wrong"
            ),
        },
        "failure_witness_time_varying_R": (
            "NOT recomputed here -- by reference to already-verified results: "
            "covid_renewal.py's own directly-computed R_t dips below 1 (late Feb 2020) "
            "and rises above 1.5 (mid-March 2020) within the SAME window (docs/covid_renewal.md); "
            "project_incidence_constant_r (package 2) had to explicitly ASSUME constant R "
            "for exactly this reason, and its real-data forecast errors "
            "(docs/mechanistic_rolling_origin.md, docs/mechanistic_probabilistic_evaluation.md) "
            "are the visible cost of that assumption not holding exactly."
        ),
        "failure_witness_etas_kernel_fragility": (
            "NOT recomputed here -- by reference to package 1: only ~30% of the ETAS "
            "kernel's total mass falls within the observed catalog span (docs/etas_earthquakes.md), "
            "a structurally DIFFERENT fragility (power-law vs. exponential-family kernel tail) "
            "from the renewal case's time-varying-R issue -- both are the SAME kind of "
            "quantity (total kernel mass) failing for different underlying reasons."
        ),
    }


CHECKS = [
    ("B8_positive_kernel_branching_operator", check_b8_positive_kernel_branching_operator),
]


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--co2-data", type=Path, default=ROOT / "data" / "noaa_mauna_loa_co2_annual_1959_2025.txt")
    p.add_argument("--temp-data", type=Path, default=ROOT / "data" / "noaa_global_temp_anomaly_1880_2025.csv")
    p.add_argument("--json-out", type=Path, default=Path(__file__).with_name("verify_structural_bridges_b7_b8_results.json"))
    args = p.parse_args(argv)

    co2_path = args.co2_data.resolve()
    temp_path = args.temp_data.resolve()
    checks = [("B7_impulse_response_representation", lambda: check_b7_impulse_response_representation(co2_path, temp_path))] + CHECKS

    report = {
        "package": "MECHANISTIC_VALIDATION_ROADMAP.md package 4 (structural bridges B7, B8)",
        "source_document": "docs/structural_relations.md",
        "concept_origin": "prompts/Answers/nicht_stationäre_Treiber/SCF_Review_f8e249f.md",
        "timestamp": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "python": sys.version.split()[0],
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "platform": platform.platform(),
        "checks": {},
        "disclaimer": (
            "Two additional bridges (B7, B8), continuing docs/structural_relations.md's "
            "B1/B2 numbering. Uses only existing repo APIs; no new production module; "
            "no shared kernel API (Astra's explicit caution); does not mutate "
            "dynamics/, viability/, or validation/."
        ),
    }
    passed = 0
    failed = 0
    errors = []
    for name, fn in checks:
        try:
            report["checks"][name] = {"status": "passed", "detail": fn()}
            passed += 1
            print(f"PASS  {name}")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            errors.append({"check": name, "error": f"{type(exc).__name__}: {exc}"})
            report["checks"][name] = {"status": "failed", "error": f"{type(exc).__name__}: {exc}"}
            print(f"FAIL  {name}: {exc}")

    summary = {"count": len(checks), "passed": passed, "failed": failed, "errors": errors, "report": report}
    args.json_out.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(f"\n{passed}/{len(checks)} passed; wrote {args.json_out}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
