#!/usr/bin/env python3
"""Mandatory synthetic controls for the G5 SPARC pilot (Plan §10.5).

Content basis: `SCF_GALAXY_DYNAMICS_IMPLEMENTATION_PLAN.md` §10.5 and
`docs/galaxy_pilot.md` (the real run). Purely synthetic -- no real SPARC
file is read here (category "math"); the genuine real-data pilot run
lives in `docs/galaxy_pilot.md`, reproduced manually in this session
against the local (non-committed) files, matching the established
`verify_hydrology_pilot.py` / `docs/hydrology_pilot.md` precedent.
"""
from __future__ import annotations

import datetime as dt
import json
import sys
from dataclasses import replace
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from scoped_correspondence.astrophysics import (  # noqa: E402
    BurkertProfile,
    HomologyScaling,
    circular_velocity_from_g,
)
from scoped_correspondence.validation.galaxy_pilot import (  # noqa: E402
    LOG_RHO_BOUNDS,
    LOG_RSCALE_KPC_BOUNDS,
    fit_burkert_descriptive,
    train_test_split_outer,
)
from scoped_correspondence.validation.sparc_data import (  # noqa: E402
    SparcComponentRow,
    combine_baryonic_v2,
    scale_distance,
)


def require(ok, msg):
    if not bool(ok):
        raise AssertionError(msg)


def near(a, b, atol=0.0, rtol=1e-9, msg=""):
    if not np.allclose(a, b, atol=atol, rtol=rtol):
        raise AssertionError(f"{msg}: {a!r} != {b!r} (atol={atol}, rtol={rtol})")


def _make_zero_baryon_rows(rho0, r0_pc, r_kpc_grid, v_obs_override=None, e_vobs=1.0):
    """Synthetic rows with zero baryonic contribution, so Vobs = the
    Burkert halo's own circular velocity exactly (isolates halo-parameter
    recovery from baryon-modelling choices)."""
    prof = BurkertProfile(rho0_msun_pc3=rho0, r0_pc=r0_pc)
    rows = []
    for i, rk in enumerate(r_kpc_grid):
        r_pc = rk * 1000.0
        v = float(prof.circular_velocity(r_pc)) if v_obs_override is None else float(v_obs_override[i])
        rows.append(SparcComponentRow(
            galaxy="SYN", D_mpc=10.0, R_kpc=float(rk), Vobs_kms=v, e_Vobs_kms=e_vobs,
            Vgas_kms=0.0, Vdisk_kms=0.0, Vbul_kms=0.0, SBdisk_sollum_pc2=0.0, SBbul_sollum_pc2=0.0,
        ))
    return rows


_TRUE_RHO0 = 0.03
_TRUE_R0_PC = 3000.0
_GRID_WIDE_KPC = np.geomspace(0.1, 20.0, 15)   # x = r/r0 from ~0.03 to ~6.7
_GRID_INNER_KPC = np.geomspace(0.05, 0.3, 15)  # x = r/r0 from ~0.017 to ~0.1, deep core only


# ---------------------------------------------------------------------------
def check_exact_noiseless_recovery_wide_range():
    """Plan §10.5: 'Burkert-generierte, ausreichend weit reichende Kurven:
    exakte rauschfreie Rückgewinnung innerhalb numerischer Toleranz.'"""
    rows = _make_zero_baryon_rows(_TRUE_RHO0, _TRUE_R0_PC, _GRID_WIDE_KPC)
    fit = fit_burkert_descriptive(rows, galaxy="SYN")
    require(fit.status == "converged", f"expected convergence, got {fit.status}")
    require(not fit.boundary_hit, "wide-range noiseless fit should not hit a declared bound")
    near(fit.rho0_msun_pc3, _TRUE_RHO0, rtol=1e-6, msg="rho0 recovery")
    near(fit.r0_pc, _TRUE_R0_PC, rtol=1e-6, msg="r0 recovery")
    return {"rho0_relerr": abs(fit.rho0_msun_pc3 - _TRUE_RHO0) / _TRUE_RHO0,
            "r0_relerr": abs(fit.r0_pc - _TRUE_R0_PC) / _TRUE_R0_PC}


def check_inner_radius_information_loss():
    """Plan §10.2/§10.5: an inner-only curve weakly determines r0.

    A perfect noiseless nonlinear fit can still lock onto the exact
    answer even for inner-only data (checked separately, informationally
    not a contradiction -- conditioning, not exact non-identifiability).
    The actual information loss shows up as much higher SENSITIVITY to
    realistic measurement noise: at a fixed noise level (sigma=2 km/s,
    matching a typical SPARC e_Vobs), the wide-range fit's r0 error stays
    within a few percent across 5 independent noise draws, while the
    inner-only fit's r0 error is consistently >10x larger."""
    wide_errs = []
    inner_errs = []
    for seed in range(5):
        rng = np.random.default_rng(seed)

        rows_true_wide = _make_zero_baryon_rows(_TRUE_RHO0, _TRUE_R0_PC, _GRID_WIDE_KPC)
        v_true_wide = np.array([r.Vobs_kms for r in rows_true_wide])
        v_noisy_wide = v_true_wide + rng.normal(0, 2.0, size=len(v_true_wide))
        rows_wide = _make_zero_baryon_rows(_TRUE_RHO0, _TRUE_R0_PC, _GRID_WIDE_KPC,
                                            v_obs_override=v_noisy_wide, e_vobs=2.0)
        fit_wide = fit_burkert_descriptive(rows_wide, galaxy="SYN")

        rows_true_inner = _make_zero_baryon_rows(_TRUE_RHO0, _TRUE_R0_PC, _GRID_INNER_KPC)
        v_true_inner = np.array([r.Vobs_kms for r in rows_true_inner])
        v_noisy_inner = v_true_inner + rng.normal(0, 2.0, size=len(v_true_inner))
        rows_inner = _make_zero_baryon_rows(_TRUE_RHO0, _TRUE_R0_PC, _GRID_INNER_KPC,
                                             v_obs_override=v_noisy_inner, e_vobs=2.0)
        fit_inner = fit_burkert_descriptive(rows_inner, galaxy="SYN")

        wide_errs.append(abs(fit_wide.r0_pc - _TRUE_R0_PC) / _TRUE_R0_PC)
        inner_errs.append(abs(fit_inner.r0_pc - _TRUE_R0_PC) / _TRUE_R0_PC)

    for w, i in zip(wide_errs, inner_errs):
        require(i > 10 * w, f"expected inner-only r0 error to be >10x the wide-range error, got inner={i}, wide={w}")

    return {"wide_r0_relerr": wide_errs, "inner_r0_relerr": inner_errs}


def check_sign_convention_700_not_900():
    """Plan §10.5 (also covered in G4's verify_sparc_adapter.py; re-asserted
    here as the pilot's own regression anchor, since it feeds Mode A/B directly)."""
    v2 = combine_baryonic_v2(v_gas=-10.0, v_disk=40.0, v_bul=0.0, upsilon_d=0.5, upsilon_b=0.7)
    near(v2, 700.0, rtol=1e-12, msg="v_bar^2")
    return {"v_bar_sq": v2}


def check_distance_scaling_matches_g2_homology():
    """Plan §10.5: 'Entfernungsskala ... Änderung: gemeinsame Transformation
    aller betroffenen Größen prüfen.' Distance-rescaling every row by
    alpha_D and refitting must recover exactly the G2 homology-scaled
    (rho0/alpha_D, r0*alpha_D) -- ties G2, G4 (scale_distance), and G5
    together, using each package's already-verified machinery."""
    rows = _make_zero_baryon_rows(_TRUE_RHO0, _TRUE_R0_PC, _GRID_WIDE_KPC)
    alpha_D = 2.5
    scaled_rows = []
    for r in rows:
        r_kpc_new, v_new = scale_distance(r.R_kpc, r.Vobs_kms, alpha_D)
        scaled_rows.append(replace(r, R_kpc=r_kpc_new, Vobs_kms=v_new, D_mpc=r.D_mpc * alpha_D))

    fit_scaled = fit_burkert_descriptive(scaled_rows, galaxy="SYN")
    target = HomologyScaling(alpha_D).scaled_burkert(BurkertProfile(rho0_msun_pc3=_TRUE_RHO0, r0_pc=_TRUE_R0_PC))

    near(fit_scaled.rho0_msun_pc3, target.rho0_msun_pc3, rtol=1e-6, msg="rho0 after distance rescaling")
    near(fit_scaled.r0_pc, target.r0_pc, rtol=1e-6, msg="r0 after distance rescaling")
    return {"rho0_scaled": fit_scaled.rho0_msun_pc3, "r0_scaled": fit_scaled.r0_pc}


def check_leak_test_holdout_does_not_affect_training():
    """Plan §10.5: 'Lecktest: Änderungen an zurückgehaltenen v_obs dürfen
    Training, Parameter und Auswahl nicht ändern, nur Testscores.'"""
    rows = _make_zero_baryon_rows(_TRUE_RHO0, _TRUE_R0_PC, _GRID_WIDE_KPC, e_vobs=2.0)
    split_original = train_test_split_outer(rows)
    fit_original = fit_burkert_descriptive(split_original.train_rows, galaxy="SYN")

    corrupted = list(rows)
    for i, r in enumerate(corrupted):
        if r.R_kpc in {tr.R_kpc for tr in split_original.test_rows}:
            corrupted[i] = replace(r, Vobs_kms=r.Vobs_kms + 1000.0)  # wildly corrupt held-out points only

    split_corrupted = train_test_split_outer(corrupted)
    require(tuple(tr.R_kpc for tr in split_corrupted.train_rows) == tuple(tr.R_kpc for tr in split_original.train_rows),
            "corrupting held-out points must not change which radii are training radii")
    require(tuple(tr.Vobs_kms for tr in split_corrupted.train_rows) == tuple(tr.Vobs_kms for tr in split_original.train_rows),
            "corrupting held-out points must not change training Vobs values")

    fit_corrupted = fit_burkert_descriptive(split_corrupted.train_rows, galaxy="SYN")
    require(fit_corrupted.rho0_msun_pc3 == fit_original.rho0_msun_pc3,
            "training-only fit must be bit-identical regardless of held-out corruption")
    require(fit_corrupted.r0_pc == fit_original.r0_pc,
            "training-only fit must be bit-identical regardless of held-out corruption")
    return {"ok": True}


def check_observation_equivalence_same_g_same_vc():
    """Plan §10.5 (already independently verified in G3's own
    verify_galaxy_observation_maps.py -- re-asserted briefly here as this
    pilot's own record that it relies on that guarantee)."""
    prof = BurkertProfile(rho0_msun_pc3=0.02, r0_pc=1500.0)
    r_pc = 4000.0
    g = prof.g(r_pc)
    near(circular_velocity_from_g(g, r_pc), prof.circular_velocity(r_pc), rtol=1e-10, msg="v_c(g) vs profile method")
    return {"ok": True}


def check_boundary_hit_reported_for_out_of_bounds_truth():
    """Plan §10.5/§10.2: a fit pushed against a declared bound must be
    REPORTED as boundary-dependent, not silently accepted as converged
    truth. Uses a true rho0 far below the declared lower bound."""
    true_rho0_extreme = 10 ** (LOG_RHO_BOUNDS[0] - 3.0)  # 3 decades below the lower bound
    rows = _make_zero_baryon_rows(true_rho0_extreme, _TRUE_R0_PC, _GRID_WIDE_KPC)
    fit = fit_burkert_descriptive(rows, galaxy="SYN")
    require(fit.boundary_hit, "expected boundary_hit=True for a true value far outside the declared bounds")
    return {"fitted_rho0": fit.rho0_msun_pc3, "boundary_hit": fit.boundary_hit}


CHECKS = [
    ("exact_noiseless_recovery_wide_range", check_exact_noiseless_recovery_wide_range),
    ("inner_radius_information_loss", check_inner_radius_information_loss),
    ("sign_convention_700_not_900", check_sign_convention_700_not_900),
    ("distance_scaling_matches_g2_homology", check_distance_scaling_matches_g2_homology),
    ("leak_test_holdout_does_not_affect_training", check_leak_test_holdout_does_not_affect_training),
    ("observation_equivalence_same_g_same_vc", check_observation_equivalence_same_g_same_vc),
    ("boundary_hit_reported_for_out_of_bounds_truth", check_boundary_hit_reported_for_out_of_bounds_truth),
]


def main() -> int:
    report = {
        "package": "GALAXY_DYNAMICS_ROADMAP.md Paket G5 (mandatory synthetic controls, Plan §10.5)",
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

    out = Path(__file__).with_name("verify_galaxy_pilot_results.json")
    out.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    print(f"\n{sum(1 for c in report['checks'].values() if c['status'] == 'pass')}/{len(CHECKS)} checks passed")
    print(f"Report written to {out}")
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
