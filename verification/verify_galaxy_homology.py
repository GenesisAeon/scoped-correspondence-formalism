#!/usr/bin/env python3
"""Independent checks for G2 exact homology correspondence.

Content basis: `SCF_GALAXY_DYNAMICS_IMPLEMENTATION_PLAN.md` §7, §12.2 and
`docs/galaxy_dynamics_scope.md`. Purely synthetic/analytic -- no real
dataset is loaded (category "math").

Positive control reproduces the plan's own worked lambda=4 example
exactly. Negative controls reproduce the plan's own counterexamples
(wrong time factor, fixed instead of corresponding radius, changed
profile shape, unscaled point mass) and require them to show a genuine,
measurable violation -- not merely a different label (Plan §7.2:
"Verwendete Gegenbeispiele müssen eine messbare Verletzung erzeugen,
nicht lediglich eine andere Benennung.").
"""
from __future__ import annotations

import datetime as dt
import json
import math
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from scoped_correspondence.astrophysics import (  # noqa: E402
    BurkertProfile,
    HomologyScaling,
    NFWProfile,
    circular_orbit_correspondence,
    radial_acceleration_identity_residual,
)
from scoped_correspondence.correspondence.contract import (  # noqa: E402
    Correspondence,
    ModelRef,
    Scope,
    StateMap,
    TimeMap,
)
from scoped_correspondence.astrophysics.galaxy_homology import circular_orbit_flow  # noqa: E402


def require(ok, msg):
    if not bool(ok):
        raise AssertionError(msg)


def near(a, b, atol=0.0, rtol=1e-9, msg=""):
    if not np.allclose(a, b, atol=atol, rtol=rtol):
        raise AssertionError(f"{msg}: {a!r} != {b!r} (atol={atol}, rtol={rtol})")


# ---------------------------------------------------------------------------
def check_positive_control_reference_case_lambda4():
    """Plan §7.2's worked example, reproduced exactly."""
    source = BurkertProfile(rho0_msun_pc3=0.05, r0_pc=3000.0)  # r0=3 kpc
    lam = 4.0
    scaling = HomologyScaling(lam)
    target = scaling.scaled_burkert(source)

    near(target.rho0_msun_pc3, 0.0125, rtol=1e-12, msg="rho0_target")
    near(target.r0_pc, 12000.0, rtol=1e-12, msg="r0_target [pc] (12 kpc)")
    near(target.mu_h(), source.mu_h(), rtol=1e-12, msg="mu_h invariant")
    near(target.mu_h(), 150.0, rtol=1e-12, msg="mu_h_target = 150")

    r_source_pc = 3000.0
    r_target_pc = lam * r_source_pc  # 12 kpc

    M_source = source.enclosed_mass(r_source_pc)
    M_target = target.enclosed_mass(r_target_pc)
    near(M_target / M_source, 16.0, rtol=1e-9, msg="M_target/M_source = lambda^2 = 16")

    g_source = source.g(r_source_pc)
    g_target = target.g(r_target_pc)
    near(g_target / g_source, 1.0, rtol=1e-9, msg="g_target/g_source = 1")

    v_source = source.circular_velocity(r_source_pc)
    v_target = target.circular_velocity(r_target_pc)
    near(v_target / v_source, 2.0, rtol=1e-9, msg="v_target/v_source = sqrt(lambda) = 2")

    period_source = 2.0 * math.pi * r_source_pc / v_source
    period_target = 2.0 * math.pi * r_target_pc / v_target
    near(period_target / period_source, 2.0, rtol=1e-9, msg="period_target/period_source = sqrt(lambda) = 2")

    return {
        "M_ratio": M_target / M_source,
        "g_ratio": g_target / g_source,
        "v_ratio": v_target / v_source,
        "period_ratio": period_target / period_source,
    }


# ---------------------------------------------------------------------------
def check_vector_field_identity_general_states():
    """Algebraic vector-field identity g_source(r) = g_target(lambda*r),
    covering general (non-circular) radial states (Plan §7.1/§7.2)."""
    source = BurkertProfile(rho0_msun_pc3=0.03, r0_pc=1800.0)
    results = {}
    for lam in (0.5, 1.0, 2.0, 4.0, 9.0):
        for x in (0.01, 0.3, 1.0, 3.0, 20.0):
            r_pc = x * source.r0_pc
            residual = radial_acceleration_identity_residual(source, lam, r_pc)
            scale = abs(source.g(r_pc)) + 1e-30
            require(residual / scale < 1e-9,
                    f"vector-field identity violated at lambda={lam}, x={x}: residual/scale={residual/scale}")
            results[f"lambda={lam},x={x}"] = residual / scale
    return results


# ---------------------------------------------------------------------------
def check_circular_orbit_conjugacy():
    """SCF Correspondence.verify_conjugacy on the analytic circular-orbit
    flow (Plan §7.2: 'Der Flow-Test kann zuerst mit analytischen
    Kreisbahnen ... erfolgen')."""
    source = BurkertProfile(rho0_msun_pc3=0.04, r0_pc=2500.0)
    reports = {}
    for lam in (0.25, 1.0, 3.0, 4.0, 10.0):
        corr = circular_orbit_correspondence(source, lam)
        states = [(x * source.r0_pc, theta0) for x in (0.05, 0.5, 1.0, 5.0) for theta0 in (0.0, 1.3, -2.1)]
        times = [-50.0, 0.0, 1.0, 37.5]
        report = corr.verify_conjugacy(states, times)
        require(report.ok, f"circular-orbit conjugacy failed at lambda={lam}: max_residual={report.max_residual}")
        require(report.max_residual < 1e-8, f"circular-orbit residual too large at lambda={lam}: {report.max_residual}")
        reports[f"lambda={lam}"] = report.max_residual
    return reports


# ---------------------------------------------------------------------------
def check_negative_control_wrong_time_factor():
    """Using c=1/sqrt(lambda) instead of c=sqrt(lambda) must break the
    conjugacy measurably (Plan §7.1: 'Der Kehrwert wäre in dieser
    Schnittstelle falsch.')."""
    source = BurkertProfile(rho0_msun_pc3=0.04, r0_pc=2500.0)
    lam = 4.0
    scaling = HomologyScaling(lam)
    target = scaling.scaled_burkert(source)
    wrong_corr = Correspondence(
        source=ModelRef(name="source", flow=circular_orbit_flow(source)),
        target=ModelRef(name="target", flow=circular_orbit_flow(target)),
        state_map=scaling.state_map_r_theta(),
        time_map=TimeMap(name="wrong_time_scale", constant_scale=1.0 / math.sqrt(lam)),
        scope=Scope(description="wrong-time-factor negative control", state_ok=lambda s: s[0] > 0),
    )
    states = [(source.r0_pc, 0.0)]
    times = [10.0]
    report = wrong_corr.verify_conjugacy(states, times)
    require(not report.ok, "wrong time factor should break conjugacy, but verify_conjugacy reported ok=True")
    require(report.max_residual > 1e-3, f"wrong time factor residual too small to be a real violation: {report.max_residual}")
    return {"max_residual": report.max_residual}


def check_negative_control_fixed_radius_instead_of_corresponding():
    """Comparing g at the SAME physical radius (instead of r and lambda*r)
    must generally show a mismatch (Plan §7.2 negative control list)."""
    source = BurkertProfile(rho0_msun_pc3=0.02, r0_pc=1000.0)
    lam = 4.0
    target = HomologyScaling(lam).scaled_burkert(source)
    r_pc = 1500.0
    g_source = source.g(r_pc)
    g_target_same_r = target.g(r_pc)  # WRONG: should be target.g(lam*r_pc)
    g_target_corresponding_r = target.g(lam * r_pc)  # correct comparison

    near(g_target_corresponding_r, g_source, rtol=1e-9, msg="corresponding-radius comparison must match")
    require(
        abs(g_target_same_r - g_source) / abs(g_source) > 1e-3,
        "fixed-radius (non-corresponding) comparison should generally mismatch, but didn't -- weak negative control",
    )
    return {
        "g_source": g_source,
        "g_target_same_r_wrong": g_target_same_r,
        "g_target_corresponding_r_correct": g_target_corresponding_r,
    }


def check_negative_control_changed_profile_shape():
    """Comparing a Burkert source against an NFW 'target' under the same
    lambda (instead of a genuinely scaled Burkert target) must not satisfy
    the homology identity (Plan §7.2 negative control list: 'geänderte
    Profilform')."""
    source = BurkertProfile(rho0_msun_pc3=0.02, r0_pc=1000.0)
    lam = 4.0
    # An NFW profile is deliberately NOT a lambda-scaled copy of `source` --
    # it is a different profile family entirely, tuned to a similar mu_h-like
    # scale product only to make this a fair (not strawman) comparison.
    mismatched_target = NFWProfile(rho_s_msun_pc3=source.rho0_msun_pc3 / lam, r_s_pc=source.r0_pc * lam)
    r_pc = 1500.0
    g_source = source.g(r_pc)
    g_mismatched = mismatched_target.g(lam * r_pc)
    require(
        abs(g_mismatched - g_source) / abs(g_source) > 1e-3,
        "changed profile shape should break the homology identity, but didn't -- weak negative control",
    )
    return {"g_source": g_source, "g_mismatched_target": g_mismatched}


def check_negative_control_unscaled_point_mass():
    """Plan §7.2's explicit counterexample: G=1, source halo mass 1 at
    r=1, plus a central point mass 1, gives g=2 at r=1. Under lambda=2 the
    scaled halo has mass 4 at r=2 (M ~ lambda^2), so WITH the point mass
    left unscaled at 1, g(2) = (4+1)/4 = 1.25, not 2. Only a co-scaled
    point mass of 4 restores g(2) = (4+4)/4 = 2."""
    G = 1.0
    lam = 2.0

    def g_with_point_mass(halo_mass_enclosed, point_mass, r):
        return G * (halo_mass_enclosed + point_mass) / r**2

    g_source = g_with_point_mass(halo_mass_enclosed=1.0, point_mass=1.0, r=1.0)
    near(g_source, 2.0, rtol=1e-12, msg="g_source baseline")

    halo_mass_target = (lam**2) * 1.0  # = 4
    g_target_unscaled_point = g_with_point_mass(halo_mass_enclosed=halo_mass_target, point_mass=1.0, r=lam * 1.0)
    near(g_target_unscaled_point, 1.25, rtol=1e-12, msg="unscaled point mass gives 1.25, not 2")
    require(
        abs(g_target_unscaled_point - g_source) > 0.5,
        "unscaled point mass should measurably break homology (1.25 vs 2), but didn't",
    )

    point_mass_target_scaled = (lam**2) * 1.0  # = 4 -- co-scaled like the halo mass
    g_target_scaled_point = g_with_point_mass(halo_mass_enclosed=halo_mass_target, point_mass=point_mass_target_scaled, r=lam * 1.0)
    near(g_target_scaled_point, 2.0, rtol=1e-12, msg="co-scaled point mass restores g=2")

    return {
        "g_source": g_source,
        "g_target_unscaled_point_mass": g_target_unscaled_point,
        "g_target_scaled_point_mass": g_target_scaled_point,
    }


CHECKS = [
    ("positive_control_reference_case_lambda4", check_positive_control_reference_case_lambda4),
    ("vector_field_identity_general_states", check_vector_field_identity_general_states),
    ("circular_orbit_conjugacy", check_circular_orbit_conjugacy),
    ("negative_control_wrong_time_factor", check_negative_control_wrong_time_factor),
    ("negative_control_fixed_radius_instead_of_corresponding", check_negative_control_fixed_radius_instead_of_corresponding),
    ("negative_control_changed_profile_shape", check_negative_control_changed_profile_shape),
    ("negative_control_unscaled_point_mass", check_negative_control_unscaled_point_mass),
]


def main() -> int:
    report = {
        "package": "GALAXY_DYNAMICS_ROADMAP.md Paket G2 (exact homology correspondence, synthetic/analytic only)",
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

    out = Path(__file__).with_name("verify_galaxy_homology_results.json")
    out.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    print(f"\n{sum(1 for c in report['checks'].values() if c['status'] == 'pass')}/{len(CHECKS)} checks passed")
    print(f"Report written to {out}")
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
