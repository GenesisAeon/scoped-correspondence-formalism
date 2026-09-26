#!/usr/bin/env python3
"""Independent checks for G1 spherical halo profiles (Burkert/pseudo-
isothermal/NFW).

Content basis: `SCF_GALAXY_DYNAMICS_IMPLEMENTATION_PLAN.md` §6, §12.2 and
`docs/galaxy_dynamics_scope.md`. Purely synthetic/analytic -- no real
dataset is loaded (category "math").

Every check here uses a DIFFERENT computation route than the production
code in `astrophysics/spherical_profiles.py` (independent `scipy.integrate
.quad` line/volume integration, or hand-derived closed forms), per Plan
§12.2: "Kein Test darf denselben Hilfsalgorithmus zweimal aufrufen und
das als unabhängige Bestätigung verkaufen."
"""
from __future__ import annotations

import datetime as dt
import json
import math
import sys
from pathlib import Path

import numpy as np
from scipy import integrate

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from scoped_correspondence.astrophysics import (  # noqa: E402
    BurkertProfile,
    G_ASTRO_PC,
    NFWProfile,
    PseudoIsothermalProfile,
    accel_kms2_per_pc_to_si,
)


def require(ok, msg):
    if not bool(ok):
        raise AssertionError(msg)


def near(a, b, atol=0.0, rtol=1e-9, msg=""):
    if not np.allclose(a, b, atol=atol, rtol=rtol):
        raise AssertionError(f"{msg}: {a!r} != {b!r} (atol={atol}, rtol={rtol})")


# ---------------------------------------------------------------------------
# G0 reference case (docs/galaxy_dynamics_scope.md §6): rho0=0.05 M_sun/pc^3,
# r0=3 kpc, evaluated at r=r0. These numbers were already independently
# hand-verified in Paket G0 with plain Python `math` -- re-asserted here as
# a regression anchor against the production Burkert class.
def check_burkert_reference_case():
    rho0 = 0.05
    r0_pc = 3000.0  # 3 kpc
    prof = BurkertProfile(rho0_msun_pc3=rho0, r0_pc=r0_pc)

    near(prof.mu_h(), 150.0, rtol=1e-12, msg="mu_h")
    near(prof.sigma_col0(), 235.61944901923448, rtol=1e-12, msg="Sigma_col(0)")

    M_r0 = prof.enclosed_mass(r0_pc)
    near(M_r0, 2157240694.994271, rtol=1e-9, msg="M(<r0)")

    g_r0 = prof.g(r0_pc)  # (km/s)^2/pc
    g_r0_si = accel_kms2_per_pc_to_si(g_r0)
    near(g_r0_si, 3.3410253537355016e-11, rtol=1e-9, msg="g(r0) [SI]")

    v_c_r0 = prof.circular_velocity(r0_pc)
    near(v_c_r0, 55.61293113984166, rtol=1e-9, msg="v_c(r0)")

    return {"mu_h": prof.mu_h(), "M_r0": M_r0, "g_r0_si": g_r0_si, "v_c_r0": v_c_r0}


# ---------------------------------------------------------------------------
def _quad_enclosed_mass(density_fn, r_pc, r0_scale_pc):
    """M(<r) = integral_0^r 4*pi*r'^2*rho(r') dr', via independent quadrature.

    `r0_scale_pc` only sets the quadrature's `points` hint near x~1 for
    accuracy; it does not reuse any closed-form profile logic.
    """
    def integrand(rp):
        return 4.0 * math.pi * rp**2 * density_fn(rp)

    val, err = integrate.quad(integrand, 0.0, r_pc, limit=200, points=[r0_scale_pc])
    return val, err


def check_burkert_mass_quadrature():
    rho0, r0 = 0.02, 1500.0
    prof = BurkertProfile(rho0_msun_pc3=rho0, r0_pc=r0)
    results = {}
    for x in (0.01, 0.1, 1.0, 5.0, 50.0):
        r_pc = x * r0
        M_closed = prof.enclosed_mass(r_pc)
        M_quad, _ = _quad_enclosed_mass(prof.density, r_pc, r0)
        near(M_closed, M_quad, rtol=1e-6, atol=1.0, msg=f"Burkert mass quad x={x}")
        results[f"x={x}"] = {"closed": M_closed, "quad": M_quad}
    return results


def check_pseudo_isothermal_mass_quadrature():
    rho0, r0 = 0.03, 2000.0
    prof = PseudoIsothermalProfile(rho0_msun_pc3=rho0, r0_pc=r0)
    results = {}
    for x in (0.01, 0.1, 1.0, 5.0, 50.0):
        r_pc = x * r0
        M_closed = prof.enclosed_mass(r_pc)
        M_quad, _ = _quad_enclosed_mass(prof.density, r_pc, r0)
        near(M_closed, M_quad, rtol=1e-6, atol=1.0, msg=f"pseudo-iso mass quad x={x}")
        results[f"x={x}"] = {"closed": M_closed, "quad": M_quad}
    return results


def check_nfw_mass_quadrature():
    rho_s, r_s = 0.01, 5000.0
    prof = NFWProfile(rho_s_msun_pc3=rho_s, r_s_pc=r_s)
    results = {}
    # NFW density diverges at r=0 -> start the quadrature just above 0, but
    # compare M(<r) using the closed-form M(0)=0 boundary handled separately.
    for x in (0.01, 0.1, 1.0, 5.0, 50.0):
        r_pc = x * r_s
        M_closed = prof.enclosed_mass(r_pc)
        val, _ = integrate.quad(
            lambda rp: 4.0 * math.pi * rp**2 * prof.rho_s_msun_pc3 / ((rp / r_s) * (1.0 + rp / r_s) ** 2),
            0.0,
            r_pc,
            limit=200,
            points=[r_s],
        )
        near(M_closed, val, rtol=1e-6, atol=1.0, msg=f"NFW mass quad x={x}")
        results[f"x={x}"] = {"closed": M_closed, "quad": val}
    return results


# ---------------------------------------------------------------------------
def check_central_column_density_quadrature():
    """Sigma_col(0) = 2*integral_0^inf rho(r) dr, via independent quadrature
    truncated at a large multiple of r0 (profiles decay fast enough)."""
    rho0, r0 = 0.04, 1000.0

    burkert = BurkertProfile(rho0_msun_pc3=rho0, r0_pc=r0)
    val_b, _ = integrate.quad(lambda r: burkert.density(r), 0.0, np.inf, limit=200)
    near(2.0 * val_b, burkert.sigma_col0(), rtol=1e-6, msg="Burkert Sigma_col(0) quad")

    pseudo = PseudoIsothermalProfile(rho0_msun_pc3=rho0, r0_pc=r0)
    val_p, _ = integrate.quad(lambda r: pseudo.density(r), 0.0, np.inf, limit=200)
    near(2.0 * val_p, pseudo.sigma_col0(), rtol=1e-6, msg="pseudo-iso Sigma_col(0) quad")

    return {
        "burkert_quad_x2": 2.0 * val_b,
        "burkert_closed": burkert.sigma_col0(),
        "pseudo_quad_x2": 2.0 * val_p,
        "pseudo_closed": pseudo.sigma_col0(),
    }


def check_column_density_factors_are_pi_half_and_pi():
    """Table factors (Plan §6.1): Burkert pi/2, pseudo-isothermal pi -- not
    equal to each other, and not equal to mu_h itself."""
    prof_b = BurkertProfile(rho0_msun_pc3=0.1, r0_pc=100.0)
    prof_p = PseudoIsothermalProfile(rho0_msun_pc3=0.1, r0_pc=100.0)
    near(prof_b.sigma_col0() / prof_b.mu_h(), math.pi / 2.0, rtol=1e-12, msg="Burkert factor")
    near(prof_p.sigma_col0() / prof_p.mu_h(), math.pi, rtol=1e-12, msg="pseudo-iso factor")
    require(
        not math.isclose(prof_b.sigma_col0() / prof_b.mu_h(), prof_p.sigma_col0() / prof_p.mu_h()),
        "Burkert and pseudo-isothermal central-density factors must differ",
    )
    return {"burkert_factor": prof_b.sigma_col0() / prof_b.mu_h(),
            "pseudo_iso_factor": prof_p.sigma_col0() / prof_p.mu_h()}


# ---------------------------------------------------------------------------
def check_positivity_and_monotonic_mass():
    r_grid = np.geomspace(1.0, 1.0e5, 40)
    for prof in (
        BurkertProfile(rho0_msun_pc3=0.05, r0_pc=1000.0),
        PseudoIsothermalProfile(rho0_msun_pc3=0.05, r0_pc=1000.0),
        NFWProfile(rho_s_msun_pc3=0.01, r_s_pc=2000.0),
    ):
        M = np.array([prof.enclosed_mass(r) for r in r_grid])
        require(np.all(M > 0), f"{type(prof).__name__}: enclosed mass must be positive")
        require(np.all(np.diff(M) > 0), f"{type(prof).__name__}: enclosed mass must be strictly increasing")
        dens = np.array([prof.density(r) for r in r_grid])
        require(np.all(dens > 0), f"{type(prof).__name__}: density must be positive")
    return {"checked_profiles": 3, "grid_points": len(r_grid)}


def check_central_limits():
    burkert = BurkertProfile(rho0_msun_pc3=0.05, r0_pc=1000.0)
    pseudo = PseudoIsothermalProfile(rho0_msun_pc3=0.05, r0_pc=1000.0)
    nfw = NFWProfile(rho_s_msun_pc3=0.01, r_s_pc=2000.0)

    for prof in (burkert, pseudo, nfw):
        near(prof.enclosed_mass(0.0), 0.0, atol=1e-8, msg=f"{type(prof).__name__} M(0)")
        near(prof.g(0.0), 0.0, atol=1e-12, msg=f"{type(prof).__name__} g(0)")
        near(prof.circular_velocity(0.0), 0.0, atol=1e-8, msg=f"{type(prof).__name__} v_c(0)")

    # Burkert/pseudo-isothermal: finite central density -> f(0)=1.
    near(burkert.density(0.0), burkert.rho0_msun_pc3, rtol=1e-12, msg="Burkert f(0)=1")
    near(pseudo.density(0.0), pseudo.rho0_msun_pc3, rtol=1e-12, msg="pseudo-iso f(0)=1")

    # NFW: central density is explicitly not evaluable (diverges) and
    # sigma_col0() must not silently produce a finite number.
    try:
        nfw.density(0.0)
        raise AssertionError("NFW density at r=0 should raise (divergent), not return a finite value")
    except ValueError:
        pass
    require(nfw.sigma_col0() is None, "NFW sigma_col0() must be None (undefined), not a fabricated finite number")

    return {"ok": True}


def check_series_closed_form_continuity():
    """The small-x series and closed form must agree smoothly across the
    switch point -- no jump discontinuity from the numerical stabilisation."""
    for prof, series_switch_x in (
        (BurkertProfile(rho0_msun_pc3=0.05, r0_pc=100.0), None),
        (PseudoIsothermalProfile(rho0_msun_pc3=0.05, r0_pc=100.0), None),
        (NFWProfile(rho_s_msun_pc3=0.02, r_s_pc=100.0), None),
    ):
        sw = prof.series_switch_x
        r_lo = (sw * 0.5) * (prof.r0_pc if hasattr(prof, "r0_pc") else prof.r_s_pc)
        r_hi = (sw * 2.0) * (prof.r0_pc if hasattr(prof, "r0_pc") else prof.r_s_pc)
        M_lo = prof.enclosed_mass(r_lo)
        M_hi = prof.enclosed_mass(r_hi)
        require(0.0 < M_lo < M_hi, f"{type(prof).__name__}: mass must strictly increase across the series/closed-form switch")
        # relative jump should be commensurate with the change in r, not a
        # discontinuity artefact (loose bound: within an order of magnitude
        # of the r ratio-cubed, since M ~ r^3 near the origin).
        ratio_r3 = (r_hi / r_lo) ** 3
        ratio_M = M_hi / M_lo
        require(ratio_M < 50 * ratio_r3, f"{type(prof).__name__}: suspicious jump at series/closed-form switch")
    return {"ok": True}


def check_nfw_scale_product_not_confused_with_mu_h():
    """NFW's finite rho_s*r_s must be a distinctly-named quantity, never
    exposed as mu_h() or a finite sigma_col0()."""
    nfw = NFWProfile(rho_s_msun_pc3=0.02, r_s_pc=3000.0)
    require(not hasattr(nfw, "mu_h"), "NFWProfile must not expose mu_h() (would imply a finite central density product)")
    near(nfw.scale_product(), 0.02 * 3000.0, rtol=1e-12, msg="NFW scale_product")
    require(nfw.sigma_col0() is None, "NFW sigma_col0 must stay None")
    return {"scale_product": nfw.scale_product()}


CHECKS = [
    ("burkert_reference_case_g0_regression", check_burkert_reference_case),
    ("burkert_mass_quadrature", check_burkert_mass_quadrature),
    ("pseudo_isothermal_mass_quadrature", check_pseudo_isothermal_mass_quadrature),
    ("nfw_mass_quadrature", check_nfw_mass_quadrature),
    ("central_column_density_quadrature", check_central_column_density_quadrature),
    ("column_density_factors_pi_half_and_pi", check_column_density_factors_are_pi_half_and_pi),
    ("positivity_and_monotonic_mass", check_positivity_and_monotonic_mass),
    ("central_limits_M0_g0_vc0", check_central_limits),
    ("series_closed_form_continuity", check_series_closed_form_continuity),
    ("nfw_scale_product_not_mu_h", check_nfw_scale_product_not_confused_with_mu_h),
]


def main() -> int:
    report = {
        "package": "GALAXY_DYNAMICS_ROADMAP.md Paket G1 (spherical halo profiles, synthetic/analytic only)",
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

    out = Path(__file__).with_name("verify_galaxy_profiles_results.json")
    out.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    print(f"\n{sum(1 for c in report['checks'].values() if c['status'] == 'pass')}/{len(CHECKS)} checks passed")
    print(f"Report written to {out}")
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
