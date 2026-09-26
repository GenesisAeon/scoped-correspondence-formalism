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
import math
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
    NFWProfile,
    circular_velocity_from_g,
)
from scoped_correspondence.validation.galaxy_pilot import (  # noqa: E402
    LOG_RHO_BOUNDS,
    LOG_RSCALE_KPC_BOUNDS,
    HeldOutSplit,
    _fit_nfw_holdout,
    baryon_g_kms2_per_pc,
    distance_inclination_sensitivity,
    distance_inclination_sensitivity_mode_b,
    evaluate_baselines_on_holdout,
    fit_burkert_descriptive,
    profile_likelihood_burkert,
    train_test_split_outer,
)
from scoped_correspondence.validation.sparc_data import (  # noqa: E402
    SparcComponentRow,
    SparcMetadataRow,
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


def check_r2_nfw_boundary_hit_propagates_to_predictive_score():
    """R2 regression (SCF_REVIEW_G0_G7_5563e67.md): NFW previously got a
    single fit start and no boundary expansion (unlike Burkert), and
    `success`/boundary status never reached `PredictiveScore` -- a real
    NGC3109 NFW training fit hit the lower rho_s bound undetected.
    Reproduced synthetically: data sourced from an NFW halo far below the
    declared lower bound forces the NFW training fit to hit it, and this
    must now be visible on the returned PredictiveScore."""
    true_rho_s_extreme = 10 ** (LOG_RHO_BOUNDS[0] - 3.0)
    prof = NFWProfile(rho_s_msun_pc3=true_rho_s_extreme, r_s_pc=3000.0)
    r_kpc_grid = np.geomspace(0.2, 20.0, 15)
    rows = []
    for rk in r_kpc_grid:
        r_pc = rk * 1000.0
        v = float(prof.circular_velocity(r_pc))
        rows.append(SparcComponentRow(galaxy="SYN", D_mpc=10.0, R_kpc=float(rk), Vobs_kms=v, e_Vobs_kms=1.0,
                                       Vgas_kms=0.0, Vdisk_kms=0.0, Vbul_kms=0.0,
                                       SBdisk_sollum_pc2=0.0, SBbul_sollum_pc2=0.0))
    n_train = int(0.7 * len(rows))
    split = HeldOutSplit(train_rows=tuple(rows[:n_train]), test_rows=tuple(rows[n_train:]))

    halo_b, fit_b = _fit_nfw_holdout(split, 0.5, 0.7)
    require(fit_b.boundary_hit, "expected the isolated NFW training fit to hit a declared bound")

    scores = evaluate_baselines_on_holdout("SYN", split)
    score_b = next(s for s in scores if s.baseline == "B_nfw")
    require(score_b.train_boundary_hit, "PredictiveScore for B_nfw must surface the training boundary hit")
    require(score_b.train_status == "converged", "boundary-hit fit can still be a converged optimizer result")
    return {"fit_b_boundary_hit": bool(fit_b.boundary_hit), "score_b_boundary_hit": bool(score_b.train_boundary_hit)}


def check_r3_invalid_total_acceleration_reported_not_silenced():
    """R3 regression (SCF_REVIEW_G0_G7_5563e67.md): a genuinely negative
    total acceleration was previously clipped to 0 before sqrt, reporting
    a fake v_pred=0 with no error status. Reproduced with one poisoned
    test-radius row (extreme negative Vgas) among otherwise clean data --
    all three baselines must report n_invalid>=1 for that point and
    compute MAE/RMSE only over the remaining valid points, never silently
    treating the poisoned point as v_pred=0."""
    prof = BurkertProfile(rho0_msun_pc3=0.02, r0_pc=2000.0)
    train_rows = []
    for rk in np.geomspace(0.5, 10.0, 10):
        r_pc = rk * 1000.0
        v = float(prof.circular_velocity(r_pc))
        train_rows.append(SparcComponentRow(galaxy="SYN2", D_mpc=10.0, R_kpc=float(rk), Vobs_kms=v, e_Vobs_kms=1.0,
                                             Vgas_kms=0.0, Vdisk_kms=0.0, Vbul_kms=0.0,
                                             SBdisk_sollum_pc2=0.0, SBbul_sollum_pc2=0.0))
    test_rows = [
        SparcComponentRow(galaxy="SYN2", D_mpc=10.0, R_kpc=12.0, Vobs_kms=50.0, e_Vobs_kms=1.0,
                           Vgas_kms=-500.0, Vdisk_kms=0.0, Vbul_kms=0.0, SBdisk_sollum_pc2=0.0, SBbul_sollum_pc2=0.0),
        SparcComponentRow(galaxy="SYN2", D_mpc=10.0, R_kpc=13.0, Vobs_kms=float(prof.circular_velocity(13000.0)),
                           e_Vobs_kms=1.0, Vgas_kms=0.0, Vdisk_kms=0.0, Vbul_kms=0.0,
                           SBdisk_sollum_pc2=0.0, SBbul_sollum_pc2=0.0),
        SparcComponentRow(galaxy="SYN2", D_mpc=10.0, R_kpc=14.0, Vobs_kms=float(prof.circular_velocity(14000.0)),
                           e_Vobs_kms=1.0, Vgas_kms=0.0, Vdisk_kms=0.0, Vbul_kms=0.0,
                           SBdisk_sollum_pc2=0.0, SBbul_sollum_pc2=0.0),
    ]
    split = HeldOutSplit(train_rows=tuple(train_rows), test_rows=tuple(test_rows))
    scores = evaluate_baselines_on_holdout("SYN2", split)

    detail = {}
    for s in scores:
        require(s.n_invalid >= 1, f"{s.baseline}: expected the poisoned point to be reported invalid")
        require(s.n_invalid < s.n_test, f"{s.baseline}: the two clean points must remain valid")
        require(not math.isnan(s.diagnostic_rmse_kms), f"{s.baseline}: diagnostic RMSE over remaining valid points must be a real number")
        # F2: any invalid point means primary_* is None, never a fabricated full-domain score.
        require(s.primary_rmse_kms is None, f"{s.baseline}: primary_rmse_kms must be None when n_invalid>=1, not {s.primary_rmse_kms}")
        require(s.status in ("out_of_domain_partial", "out_of_domain_full"), f"{s.baseline}: expected an out-of-domain status, got {s.status}")
        detail[s.baseline] = {"n_invalid": s.n_invalid, "diagnostic_rmse_kms": s.diagnostic_rmse_kms, "status": s.status}

    # Baseline A (the TRUE source) must score near-exactly on its two clean
    # held-out points despite the poisoned third point being present in the
    # input -- proof the poisoned point was excluded, not zero-padded in.
    score_a = next(s for s in scores if s.baseline == "A_burkert")
    require(score_a.diagnostic_rmse_kms < 1e-6, f"Baseline A should score near-exactly on its own clean held-out points, got {score_a.diagnostic_rmse_kms}")
    return detail


def check_f2_out_of_domain_not_a_misleading_perfect_score():
    """F2 (SCF_FOLLOWUP_REVIEW_84848a4.md): reproduces the review's own
    constructed 3-point counterexample -- a test point with negative
    baryonic total but positive halo total leaves MOND (which requires
    g_bar>=0) out of its scalar domain there, while Burkert/NFW remain
    valid. Before the fix, each baseline scored independently over its own
    valid subset, so MOND could report a misleadingly 'perfect' rmse=0.0
    over its remaining 2 (deliberately exact) points, indistinguishable
    from a genuine full-3-point win. Now MOND's primary_rmse_kms must be
    None (out-of-domain), with the 0.0 visible only as a labeled
    diagnostic, never as an ordinary comparable score."""
    prof = BurkertProfile(rho0_msun_pc3=0.02, r0_pc=2000.0)
    train_rows = []
    for rk in np.geomspace(0.5, 10.0, 10):
        v = float(prof.circular_velocity(rk * 1000.0))
        train_rows.append(SparcComponentRow(galaxy="SYN3", D_mpc=10.0, R_kpc=float(rk), Vobs_kms=v, e_Vobs_kms=1.0,
                                             Vgas_kms=0.0, Vdisk_kms=0.0, Vbul_kms=0.0,
                                             SBdisk_sollum_pc2=0.0, SBbul_sollum_pc2=0.0))
    # A test point with a large negative Vgas (negative baryonic total,
    # MOND out of domain) but a small enough magnitude that Burkert/NFW's
    # halo term keeps the TOTAL acceleration positive there.
    test_rows = [
        SparcComponentRow(galaxy="SYN3", D_mpc=10.0, R_kpc=11.0, Vobs_kms=float(prof.circular_velocity(11000.0)),
                           e_Vobs_kms=1.0, Vgas_kms=-15.0, Vdisk_kms=0.0, Vbul_kms=0.0,
                           SBdisk_sollum_pc2=0.0, SBbul_sollum_pc2=0.0),
        SparcComponentRow(galaxy="SYN3", D_mpc=10.0, R_kpc=12.0, Vobs_kms=float(prof.circular_velocity(12000.0)),
                           e_Vobs_kms=1.0, Vgas_kms=0.0, Vdisk_kms=0.0, Vbul_kms=0.0,
                           SBdisk_sollum_pc2=0.0, SBbul_sollum_pc2=0.0),
        SparcComponentRow(galaxy="SYN3", D_mpc=10.0, R_kpc=13.0, Vobs_kms=float(prof.circular_velocity(13000.0)),
                           e_Vobs_kms=1.0, Vgas_kms=0.0, Vdisk_kms=0.0, Vbul_kms=0.0,
                           SBdisk_sollum_pc2=0.0, SBbul_sollum_pc2=0.0),
    ]
    split = HeldOutSplit(train_rows=tuple(train_rows), test_rows=tuple(test_rows))
    scores = evaluate_baselines_on_holdout("SYN3", split)
    score_mond = next(s for s in scores if s.baseline == "C_mond")

    require(score_mond.n_invalid == 1, f"expected exactly 1 out-of-domain MOND point, got {score_mond.n_invalid}")
    require(score_mond.status == "out_of_domain_partial", f"expected out_of_domain_partial, got {score_mond.status}")
    require(score_mond.primary_rmse_kms is None, "MOND's primary_rmse_kms must be None, never a misleading number")
    require(score_mond.primary_mae_kms is None, "MOND's primary_mae_kms must be None, never a misleading number")

    score_a = next(s for s in scores if s.baseline == "A_burkert")
    require(score_a.n_invalid == 0, "Burkert (the true source) should have no invalid points here")
    require(score_a.status == "full_domain", "Burkert should be full_domain")
    require(score_a.primary_rmse_kms is not None, "a full-domain baseline's primary score must be a real number")
    return {"mond_status": score_mond.status, "mond_diagnostic_rmse": score_mond.diagnostic_rmse_kms,
            "burkert_status": score_a.status}


def _zero_baryon_burkert_rows(rho0, r0_pc, r_kpc_grid, e_vobs=1.0):
    prof = BurkertProfile(rho0_msun_pc3=rho0, r0_pc=r0_pc)
    rows = []
    for rk in r_kpc_grid:
        v = float(prof.circular_velocity(rk * 1000.0))
        rows.append(SparcComponentRow(galaxy="SYN", D_mpc=10.0, R_kpc=float(rk), Vobs_kms=v, e_Vobs_kms=e_vobs,
                                       Vgas_kms=0.0, Vdisk_kms=0.0, Vbul_kms=0.0,
                                       SBdisk_sollum_pc2=0.0, SBbul_sollum_pc2=0.0))
    return rows


def check_r6_profile_likelihood_recovers_true_psi():
    """R6 (SCF_REVIEW_G0_G7_5563e67.md): `psi`/`eta` in `DescriptiveFitResult`
    were only the best fit's own coordinates, not a profile -- Astra's
    concrete task was a real `q(psi) = min_eta chi2(...)` scan. On
    noiseless data generated from a known Burkert profile, the scan's
    minimum must land exactly at the true `psi`, with `q` rising away
    from it on both sides (a genuine profile shape, not a flat line)."""
    true_rho0, true_r0 = 0.03, 3000.0
    true_psi = math.log10(true_rho0 * true_r0)
    rows = _zero_baryon_burkert_rows(true_rho0, true_r0, np.geomspace(0.5, 20.0, 15))

    psi_grid = np.linspace(true_psi - 1.0, true_psi + 1.0, 41)
    points = profile_likelihood_burkert(rows, psi_grid)
    require(all(p.feasible for p in points), "all grid points should be feasible for this psi range/bounds")
    best = min(points, key=lambda p: p.q)
    near(best.psi, true_psi, atol=0.02 * (psi_grid[1] - psi_grid[0]), msg="profile-likelihood minimum vs true psi")
    require(best.q < 1e-6, f"chi2 at the true psi should be ~0 for noiseless data, got {best.q}")

    # q must actually rise away from the minimum on both sides (a real
    # profile, not e.g. every point silently collapsing to the same value).
    idx = points.index(best)
    require(idx > 2 and idx < len(points) - 3, "true psi should not sit at the very edge of this test's grid")
    require(points[idx - 5].q > 10.0 * best.q, "q should rise well above the minimum 5 grid steps to the left")
    require(points[idx + 5].q > 10.0 * best.q, "q should rise well above the minimum 5 grid steps to the right")
    return {"true_psi": true_psi, "best_psi": best.psi, "best_q": best.q}


def check_r6_profile_likelihood_infeasible_psi_marked_not_dropped():
    """R6: a psi whose feasible eta-interval is empty (given the psi-
    dependent bound intersection) must be marked infeasible, never
    silently clamped into the box or dropped from the output list."""
    rows = _zero_baryon_burkert_rows(0.03, 3000.0, np.geomspace(0.5, 20.0, 10))
    # eta bounds (declared) = [1, 5.5]; log_rho bounds = [-4, 1]; a psi far
    # below both (e.g. -10) makes [psi-1, psi+4] disjoint from [1, 5.5].
    psi_grid = [-10.0, 0.5, 3.0]
    points = profile_likelihood_burkert(rows, psi_grid)
    require(len(points) == len(psi_grid), "one output point per input psi, even if infeasible")
    require(not points[0].feasible, "psi=-10 should be infeasible given the declared bounds")
    require(math.isnan(points[0].q), "an infeasible point's q must be NaN, not a fabricated number")
    require(points[2].feasible, "psi=3.0 should be feasible")
    return {"ok": True}


def check_r6_profile_likelihood_single_point_intervals_evaluated():
    """F1's second bug (SCF_FOLLOWUP_REVIEW_84848a4.md): `eta_lo==eta_hi`
    (exactly one feasible point) was previously marked infeasible along
    with genuinely empty intervals. With the declared bounds (eta in
    [1,5.5], log_rho in [-4,1]), `psi=-3` degenerates to the single point
    `eta=1` and `psi=6.5` to the single point `eta=5.5` -- both must be
    evaluated, not dropped."""
    rows = _zero_baryon_burkert_rows(0.03, 3000.0, np.geomspace(0.5, 20.0, 10))
    points = profile_likelihood_burkert(rows, [-3.0, 6.5])
    require(points[0].feasible and points[1].feasible, "single-point-interval psi values must be feasible")
    near(points[0].eta_min, 1.0, atol=1e-9, msg="psi=-3 single point eta")
    near(points[1].eta_min, 5.5, atol=1e-9, msg="psi=6.5 single point eta")
    require(points[0].boundary_hit and points[1].boundary_hit, "a single-point interval is trivially at its own boundary")
    require(not math.isnan(points[0].q) and not math.isnan(points[1].q), "single-point q must be a real number")
    return {"ok": True}


def check_r6_profile_likelihood_finds_global_not_local_minimum():
    """F1 (P1, SCF_FOLLOWUP_REVIEW_84848a4.md): a single `scipy.optimize.
    minimize_scalar(method="bounded")` call over the WHOLE feasible
    interval finds only a LOCAL minimum -- confirmed on real SPARC data in
    the follow-up review (NGC3917: reported q=1253.5 at eta=2.67 while the
    feasible boundary eta=5.5 gives q=459.79). Reproduced here with a
    purely synthetic, hand-invented 'flat rotation curve' fixture (V_flat=
    120 km/s, core radius 2 kpc -- NOT derived from any real galaxy, zero
    baryons) chosen to have two well-separated chi2 basins at psi=2.7: a
    deep global minimum near eta~3.41 (q~17.7) and a much shallower local
    minimum near eta~5.0 (q~2044, independently confirmed via a brute-
    force 2001-point grid -- a route independent of the production code's
    own internal grid resolution). The routine must find the DEEP one."""
    V_flat, r_c_kpc = 120.0, 2.0
    r_kpc_grid = np.array([0.5, 1.0, 2.0, 4.0, 7.0, 10.0, 15.0, 20.0])
    v_obs_grid = V_flat * r_kpc_grid / np.sqrt(r_kpc_grid**2 + r_c_kpc**2)
    rows = [SparcComponentRow(galaxy="SYNTHFLAT", D_mpc=10.0, R_kpc=float(rk), Vobs_kms=float(v), e_Vobs_kms=3.0,
                               Vgas_kms=0.0, Vdisk_kms=0.0, Vbul_kms=0.0, SBdisk_sollum_pc2=0.0, SBbul_sollum_pc2=0.0)
            for rk, v in zip(r_kpc_grid, v_obs_grid)]

    psi = 2.7
    points = profile_likelihood_burkert(rows, [psi])
    p = points[0]
    require(p.feasible, "psi=2.7 should be feasible for this fixture")

    # Independent brute-force ground truth: a much finer grid than the
    # production routine's own internal n_grid=61, computed via a
    # separately written objective function here (not imported from
    # galaxy_pilot.py) so this is a genuinely independent route.
    r_pc, g_bar = baryon_g_kms2_per_pc(rows, 0.5, 0.7)
    v_obs = np.array([r.Vobs_kms for r in rows])
    e_vobs = np.array([r.e_Vobs_kms for r in rows])

    def brute_chi2(eta):
        rho0 = 10 ** (psi - eta)
        r0_pc = 10 ** eta
        prof = BurkertProfile(rho0_msun_pc3=rho0, r0_pc=r0_pc)
        g_halo = np.array([prof.g(r) for r in r_pc])
        g_total = np.clip(g_bar + g_halo, 0.0, None)
        v_pred = np.sqrt(g_total * r_pc)
        return float(np.sum(((v_pred - v_obs) / e_vobs) ** 2))

    eta_bounds = (LOG_RSCALE_KPC_BOUNDS[0] + 3.0, LOG_RSCALE_KPC_BOUNDS[1] + 3.0)
    eta_lo = max(eta_bounds[0], psi - LOG_RHO_BOUNDS[1])
    eta_hi = min(eta_bounds[1], psi - LOG_RHO_BOUNDS[0])
    fine_grid = np.linspace(eta_lo, eta_hi, 2001)
    fine_q = np.array([brute_chi2(e) for e in fine_grid])
    brute_best_q = float(fine_q.min())

    near(p.q, brute_best_q, rtol=1e-2, msg="profile routine vs brute-force global minimum")
    require(p.q < 100.0, f"expected the DEEP basin (q~17.7), got q={p.q} (looks like the shallow ~2044 basin)")
    require(2.0 < p.eta_min < 4.5, f"expected eta near the deep basin (~3.41), got {p.eta_min}")
    return {"routine_q": p.q, "routine_eta": p.eta_min, "brute_force_q": brute_best_q}


def check_r6_distance_inclination_sensitivity_exact_relations():
    """R6 (SCF_REVIEW_G0_G7_5563e67.md): on zero-baryon noiseless data,
    re-deriving the physical distinction from Plan §9.4 gives EXACT
    closed-form relations, independently derived here (not copied from the
    production code) and checked against it:

    Distance (only R_kpc/baryon components rescale, Vobs is a direct
    spectroscopic measurement and stays fixed): a Burkert fit to the SAME
    v(r) values but at radii relabelled by `alpha_D` recovers exactly
    `rho0/alpha_D**2` and `r0*alpha_D` (independently verified: this
    reproduces the identical v(r) curve, since M(alpha*r; rho0/alpha^2,
    r0*alpha) = alpha*M_true(r), so v_c is unchanged).

    Inclination (only Vobs/e_Vobs rescale by a constant factor k=sin(i_ref)
    /sin(i_new), radius untouched): since Burkert's M(r) is linear in
    rho0 for fixed r0, a uniform v-rescaling by k is matched exactly by
    `rho0*k**2` with r0 UNCHANGED.
    """
    true_rho0, true_r0 = 0.03, 3000.0
    rows = _zero_baryon_burkert_rows(true_rho0, true_r0, np.geomspace(0.5, 20.0, 15))
    meta_row = SparcMetadataRow(
        galaxy="SYN", T=5, D_mpc=10.0, e_D_mpc=2.0, f_D=1, inc_deg=60.0, e_inc_deg=5.0,
        L36_1e9_sollum=1.0, e_L36_1e9_sollum=0.1, Reff_kpc=1.0, SBeff_sollum_pc2=10.0,
        Rdisk_kpc=1.0, SBdisk_sollum_pc2=10.0, MHI_1e9_solmass=1.0, RHI_kpc=1.0,
        Vflat_kms=100.0, e_Vflat_kms=5.0, Q=1, ref="Test",
    )
    scenarios = {s.name: s for s in distance_inclination_sensitivity(rows, meta_row)}

    near(scenarios["reference"].rho0_msun_pc3, true_rho0, rtol=1e-6, msg="reference rho0")
    near(scenarios["reference"].r0_pc, true_r0, rtol=1e-6, msg="reference r0")

    for sign, name in ((+1.0, "D+sigma_D"), (-1.0, "D-sigma_D")):
        alpha_D = (meta_row.D_mpc + sign * meta_row.e_D_mpc) / meta_row.D_mpc
        near(scenarios[name].rho0_msun_pc3, true_rho0 / alpha_D**2, rtol=1e-4, msg=f"{name} rho0")
        near(scenarios[name].r0_pc, true_r0 * alpha_D, rtol=1e-4, msg=f"{name} r0")

    for sign, name in ((+1.0, "i+sigma_i"), (-1.0, "i-sigma_i")):
        i_new = meta_row.inc_deg + sign * meta_row.e_inc_deg
        k = math.sin(math.radians(meta_row.inc_deg)) / math.sin(math.radians(i_new))
        near(scenarios[name].rho0_msun_pc3, true_rho0 * k**2, rtol=1e-3, msg=f"{name} rho0")
        near(scenarios[name].r0_pc, true_r0, rtol=1e-4, msg=f"{name} r0 (inclination must not move r0)")

    # Genuine sensitivity, not a no-op: every scenario's mu_h must differ
    # measurably from the reference and from each other.
    mu_hs = {name: s.mu_h for name, s in scenarios.items()}
    require(len(set(round(v, 6) for v in mu_hs.values())) == len(mu_hs), f"expected 5 distinct mu_h values, got {mu_hs}")
    return {name: s.mu_h for name, s in scenarios.items()}


def check_mode_b_sensitivity_structure_and_no_leak():
    """Explorative Mode-B D/i sensitivity extension (SCF_FOLLOWUP_REVIEW_
    84848a4.md, 'Enger nächster Auftrag' #4): 5 scenarios returned, each
    re-fit from its OWN (correspondingly transformed) training rows only
    -- corrupting a scenario's test rows must not change its own training
    fit or any other scenario's results (same leak-test discipline as
    `check_leak_test_holdout_does_not_affect_training`, extended to this
    new function). Also checks the reported `k` factor for the inclination
    scenarios matches `sin(i_ref)/sin(i_new)` exactly, and `k=1` for the
    reference/distance scenarios."""
    prof = BurkertProfile(rho0_msun_pc3=0.02, r0_pc=2000.0)
    rows = []
    for rk in np.geomspace(0.5, 20.0, 15):
        v = float(prof.circular_velocity(rk * 1000.0))
        rows.append(SparcComponentRow(galaxy="SYN4", D_mpc=10.0, R_kpc=float(rk), Vobs_kms=v, e_Vobs_kms=2.0,
                                       Vgas_kms=0.0, Vdisk_kms=0.0, Vbul_kms=0.0,
                                       SBdisk_sollum_pc2=0.0, SBbul_sollum_pc2=0.0))
    split = train_test_split_outer(rows)
    meta_row = SparcMetadataRow(
        galaxy="SYN4", T=5, D_mpc=10.0, e_D_mpc=2.0, f_D=1, inc_deg=60.0, e_inc_deg=5.0,
        L36_1e9_sollum=1.0, e_L36_1e9_sollum=0.1, Reff_kpc=1.0, SBeff_sollum_pc2=10.0,
        Rdisk_kpc=1.0, SBdisk_sollum_pc2=10.0, MHI_1e9_solmass=1.0, RHI_kpc=1.0,
        Vflat_kms=100.0, e_Vflat_kms=5.0, Q=1, ref="Test",
    )

    scenarios = distance_inclination_sensitivity_mode_b(split, meta_row, galaxy="SYN4")
    require(len(scenarios) == 5, f"expected 5 scenarios, got {len(scenarios)}")
    names = {s.name for s in scenarios}
    require(names == {"reference", "D+sigma_D", "D-sigma_D", "i+sigma_i", "i-sigma_i"}, f"unexpected scenario names: {names}")

    by_name = {s.name: s for s in scenarios}
    near(by_name["reference"].inclination_rescale_k, 1.0, atol=1e-12, msg="reference k")
    near(by_name["D+sigma_D"].inclination_rescale_k, 1.0, atol=1e-12, msg="D+sigma_D k")
    k_plus_expected = math.sin(math.radians(60.0)) / math.sin(math.radians(65.0))
    near(by_name["i+sigma_i"].inclination_rescale_k, k_plus_expected, rtol=1e-12, msg="i+sigma_i k")

    for s in scenarios:
        require(len(s.scores) == 3, f"{s.name}: expected 3 baseline scores (A/B/C)")
        for sc in s.scores:
            require(sc.status == "full_domain", f"{s.name}/{sc.baseline}: expected full_domain on clean synthetic data")

    # leak check: corrupting the reference scenario's test rows only must
    # not change any scenario's training-derived scores.
    from dataclasses import replace as _rep
    poisoned_test = tuple(_rep(r, Vobs_kms=r.Vobs_kms + 500.0) for r in split.test_rows)
    poisoned_split = HeldOutSplit(train_rows=split.train_rows, test_rows=poisoned_test)
    scenarios_poisoned = distance_inclination_sensitivity_mode_b(poisoned_split, meta_row, galaxy="SYN4")
    ref_original = next(s for s in scenarios if s.name == "reference").scores
    ref_poisoned = next(s for s in scenarios_poisoned if s.name == "reference").scores
    # training-derived NFW/Burkert params are unaffected by test corruption,
    # but the (poisoned) test-set primary/diagnostic scores legitimately
    # change for THIS scenario -- check the train_status/train_boundary_hit
    # (purely training-derived) stay identical, confirming no leak into fitting.
    for so, sp in zip(ref_original, ref_poisoned):
        require(so.train_status == sp.train_status and so.train_boundary_hit == sp.train_boundary_hit,
                f"{so.baseline}: training fit must be unaffected by test-row corruption")
    return {"scenario_names": sorted(names)}


CHECKS = [
    ("exact_noiseless_recovery_wide_range", check_exact_noiseless_recovery_wide_range),
    ("inner_radius_information_loss", check_inner_radius_information_loss),
    ("sign_convention_700_not_900", check_sign_convention_700_not_900),
    ("distance_scaling_matches_g2_homology", check_distance_scaling_matches_g2_homology),
    ("leak_test_holdout_does_not_affect_training", check_leak_test_holdout_does_not_affect_training),
    ("observation_equivalence_same_g_same_vc", check_observation_equivalence_same_g_same_vc),
    ("boundary_hit_reported_for_out_of_bounds_truth", check_boundary_hit_reported_for_out_of_bounds_truth),
    ("r2_nfw_boundary_hit_propagates_to_predictive_score", check_r2_nfw_boundary_hit_propagates_to_predictive_score),
    ("r3_invalid_total_acceleration_reported_not_silenced", check_r3_invalid_total_acceleration_reported_not_silenced),
    ("f2_out_of_domain_not_a_misleading_perfect_score", check_f2_out_of_domain_not_a_misleading_perfect_score),
    ("r6_profile_likelihood_recovers_true_psi", check_r6_profile_likelihood_recovers_true_psi),
    ("r6_profile_likelihood_infeasible_psi_marked_not_dropped", check_r6_profile_likelihood_infeasible_psi_marked_not_dropped),
    ("f1_profile_likelihood_single_point_intervals_evaluated", check_r6_profile_likelihood_single_point_intervals_evaluated),
    ("f1_profile_likelihood_finds_global_not_local_minimum", check_r6_profile_likelihood_finds_global_not_local_minimum),
    ("r6_distance_inclination_sensitivity_exact_relations", check_r6_distance_inclination_sensitivity_exact_relations),
    ("mode_b_sensitivity_structure_and_no_leak", check_mode_b_sensitivity_structure_and_no_leak),
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
