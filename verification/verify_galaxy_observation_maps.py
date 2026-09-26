#!/usr/bin/env python3
"""Independent checks for G3 control models and observation equivalence.

Content basis: `SCF_GALAXY_DYNAMICS_IMPLEMENTATION_PLAN.md` §8, §12.2 and
`docs/galaxy_dynamics_scope.md`. Purely synthetic/analytic -- no real
dataset is loaded (category "math").
"""
from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import fsolve

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from scoped_correspondence.astrophysics import (  # noqa: E402
    A0_SI,
    BurkertProfile,
    NFWProfile,
    baseline_total_g_halo,
    baseline_total_g_mond,
    circular_velocity_from_g,
    effective_density,
    mond_g_total,
    mond_g_total_simple_interpolation_NOT_INTERCHANGEABLE,
    mond_sigma_star_msun_pc2,
)


def require(ok, msg):
    if not bool(ok):
        raise AssertionError(msg)


def near(a, b, atol=0.0, rtol=1e-9, msg=""):
    if not np.allclose(a, b, atol=atol, rtol=rtol):
        raise AssertionError(f"{msg}: {a!r} != {b!r} (atol={atol}, rtol={rtol})")


# ---------------------------------------------------------------------------
def check_effective_density_recovers_burkert_profile():
    """The operator applied to a profile's OWN g(r) must return its OWN
    density -- an exact mathematical identity (Plan §8.1: 'Ein analytisch
    erzeugtes Kugelprofil durch den Operator zurückgewinnen'), here
    checked via central finite differences at moderate dynamic range."""
    prof = BurkertProfile(rho0_msun_pc3=0.04, r0_pc=1200.0)
    results = {}
    for x in (0.05, 0.3, 1.0, 3.0, 20.0):
        r = x * prof.r0_pc
        recovered = effective_density(prof.g, r)
        actual = prof.density(r)
        near(recovered, actual, rtol=1e-6, msg=f"effective_density recovery at x={x}")
        results[f"x={x}"] = {"recovered": recovered, "actual": actual}
    return results


def check_effective_density_no_silent_clipping_of_negative():
    """A g(r) decaying faster than any physical enclosed-mass profile
    (here g ~ 1/r^3) gives a genuinely NEGATIVE effective density
    everywhere -- must be returned as-is, never clipped to zero (Plan
    §8.1)."""

    def fast_decay_g(r):
        return 1.0e6 / r**3

    for r in (10.0, 100.0, 1000.0):
        rho = effective_density(fast_decay_g, r)
        require(rho < 0.0, f"expected a negative effective density at r={r}, got {rho}")
    return {"ok": True}


def check_identical_g_gives_identical_v_c():
    """'Identische g(r) müssen identische lokale Kreisgeschwindigkeiten
    ergeben' (Plan §8.1) -- checked against each profile's own method AND
    a MOND-total-g-derived value, both via the model-agnostic
    circular_velocity_from_g."""
    prof = BurkertProfile(rho0_msun_pc3=0.03, r0_pc=1800.0)
    for x in (0.2, 1.0, 5.0):
        r = x * prof.r0_pc
        g = prof.g(r)
        v_generic = circular_velocity_from_g(g, r)
        v_profile = prof.circular_velocity(r)
        near(v_generic, v_profile, rtol=1e-10, msg=f"v_c(g) vs profile.circular_velocity at x={x}")

    r = 5000.0
    g_N = 0.02  # arbitrary baryonic Newtonian acceleration, (km/s)^2/pc
    g_mond = mond_g_total(g_N)
    v_mond = circular_velocity_from_g(g_mond, r)
    # same g fed through the generic formula a second, independent way
    v_mond_again = np.sqrt(r * mond_g_total(g_N))
    near(v_mond, v_mond_again, rtol=1e-12, msg="v_c(g) reproducible from the same g")
    return {"ok": True}


# ---------------------------------------------------------------------------
def check_mond_reference_values():
    """Regression anchors from docs/galaxy_dynamics_scope.md / Plan §8.2,
    plus the declared asymptotic and boundary behaviour."""
    a0_internal = accel_ratio()
    near(mond_g_total(a0_internal) / a0_internal, 1.272019649514069, rtol=1e-9,
         msg="g/a0 at g_N=a0")

    near(mond_g_total(0.0), 0.0, atol=1e-12, msg="g_N=0 -> g=0")

    try:
        mond_g_total(-1.0)
        raise AssertionError("negative g_N should raise")
    except ValueError:
        pass

    # large g_N: g/g_N -> 1
    from scoped_correspondence.astrophysics.units import accel_si_to_kms2_per_pc
    a0 = accel_si_to_kms2_per_pc(A0_SI)
    g_N_large = 1.0e6 * a0
    g_large = mond_g_total(g_N_large)
    near(g_large / g_N_large, 1.0, rtol=1e-6, msg="deep-Newtonian limit g/g_N -> 1")

    # small g_N: g/sqrt(a0*g_N) -> 1
    g_N_small = 1.0e-6 * a0
    g_small = mond_g_total(g_N_small)
    near(g_small / np.sqrt(a0 * g_N_small), 1.0, rtol=1e-6, msg="deep-MOND limit g/sqrt(a0 g_N) -> 1")

    near(mond_sigma_star_msun_pc2(), 137.0180243872182, rtol=1e-9, msg="Sigma_M [Msun/pc^2]")

    return {"g_large_ratio": g_large / g_N_large, "g_small_ratio": g_small / np.sqrt(a0 * g_N_small)}


def accel_ratio():
    """a0 expressed in the internal (km/s)^2/pc basis, for the g/a0 check."""
    from scoped_correspondence.astrophysics.units import accel_si_to_kms2_per_pc

    return accel_si_to_kms2_per_pc(A0_SI)


def check_simple_interpolation_differs_from_standard():
    """The 'simple' function x/(1+x) must NOT be silently identical to the
    standard mu_M -- guards against an implementation bug that would
    defeat the whole point of keeping them distinct (Plan §8.2). The
    logarithmic-divergence claim itself is cited from Milgrom (2009), not
    independently re-derived numerically here (see the docstring of
    mond_g_total_simple_interpolation_NOT_INTERCHANGEABLE)."""
    a0 = accel_ratio()
    for g_N in (0.01 * a0, a0, 100.0 * a0):
        g_std = mond_g_total(g_N)
        g_simple = mond_g_total_simple_interpolation_NOT_INTERCHANGEABLE(g_N)
        require(abs(g_std - g_simple) / g_std > 1e-3,
                f"standard and simple interpolation should differ measurably at g_N={g_N}, "
                f"got {g_std} vs {g_simple}")
    return {"ok": True}


# ---------------------------------------------------------------------------
def check_baselines_are_structurally_distinct():
    """Baselines A (Burkert), B (NFW), C (MOND) must give measurably
    different total g(r) for the same baryonic component and comparable
    halo scale (Plan §8.3) -- otherwise they would be redundant."""
    burkert = BurkertProfile(rho0_msun_pc3=0.03, r0_pc=2000.0)
    nfw = NFWProfile(rho_s_msun_pc3=0.01, r_s_pc=3000.0)

    def baryon_g(r):
        # a small constant-ish baryonic contribution for illustration
        return 1.0e-3 * np.ones_like(np.asarray(r, dtype=float))

    r = 4000.0
    gA = baseline_total_g_halo(baryon_g, burkert, r)
    gB = baseline_total_g_halo(baryon_g, nfw, r)
    gC = baseline_total_g_mond(baryon_g, r)

    require(abs(gA - gB) / gA > 1e-3, "Baseline A and B should differ (different halo profile family)")
    require(abs(gA - gC) / gA > 1e-3, "Baseline A and C should differ (halo vs MOND)")
    require(abs(gB - gC) / gB > 1e-3, "Baseline B and C should differ (halo vs MOND)")
    return {"gA": float(gA), "gB": float(gB), "gC": float(gC)}


def check_observation_equivalence_cross_family_degeneracy():
    """Exact cross-family degeneracy demonstration (Plan §8.1:
    'verschiedene Parametrisierungen können dieselbe Observable
    erzeugen'): fit an NFW profile's two free parameters to match a fixed
    Burkert profile's g(r) EXACTLY at two chosen radii, then show the two
    profiles genuinely diverge (>10%) at radii NOT used in the fit --
    i.e. these two structurally different models are observationally
    indistinguishable at the fitted points but make different
    predictions elsewhere."""
    source = BurkertProfile(rho0_msun_pc3=0.03, r0_pc=2000.0)
    r_a, r_b = 1500.0, 6000.0
    target_a, target_b = source.g(r_a), source.g(r_b)

    def eqs(params):
        log_rho_s, log_r_s = params
        prof = NFWProfile(rho_s_msun_pc3=10 ** log_rho_s, r_s_pc=10 ** log_r_s)
        return [prof.g(r_a) - target_a, prof.g(r_b) - target_b]

    sol, info, ier, msg = fsolve(eqs, x0=[np.log10(0.01), np.log10(3000.0)], full_output=True)
    require(ier == 1, f"fsolve did not converge: {msg}")
    matched = NFWProfile(rho_s_msun_pc3=10 ** sol[0], r_s_pc=10 ** sol[1])

    near(matched.g(r_a), target_a, rtol=1e-6, msg="matched at r_a")
    near(matched.g(r_b), target_b, rtol=1e-6, msg="matched at r_b")

    out_of_sample_diffs = {}
    for r_c in (500.0, 12000.0, 30000.0):
        g_source = source.g(r_c)
        g_matched = matched.g(r_c)
        rel_diff = abs(g_source - g_matched) / g_source
        require(rel_diff > 0.1, f"expected genuine out-of-sample divergence at r={r_c}, got rel_diff={rel_diff}")
        out_of_sample_diffs[f"r={r_c}"] = rel_diff

    return {
        "nfw_rho_s": matched.rho_s_msun_pc3,
        "nfw_r_s": matched.r_s_pc,
        "out_of_sample_rel_diffs": out_of_sample_diffs,
    }


CHECKS = [
    ("effective_density_recovers_burkert_profile", check_effective_density_recovers_burkert_profile),
    ("effective_density_no_silent_clipping_of_negative", check_effective_density_no_silent_clipping_of_negative),
    ("identical_g_gives_identical_v_c", check_identical_g_gives_identical_v_c),
    ("mond_reference_values", check_mond_reference_values),
    ("simple_interpolation_differs_from_standard", check_simple_interpolation_differs_from_standard),
    ("baselines_are_structurally_distinct", check_baselines_are_structurally_distinct),
    ("observation_equivalence_cross_family_degeneracy", check_observation_equivalence_cross_family_degeneracy),
]


def main() -> int:
    report = {
        "package": "GALAXY_DYNAMICS_ROADMAP.md Paket G3 (control models and observation equivalence, synthetic/analytic only)",
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

    out = Path(__file__).with_name("verify_galaxy_observation_maps_results.json")
    out.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    print(f"\n{sum(1 for c in report['checks'].values() if c['status'] == 'pass')}/{len(CHECKS)} checks passed")
    print(f"Report written to {out}")
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
