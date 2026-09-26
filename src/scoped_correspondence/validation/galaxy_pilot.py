"""SPARC pilot: frozen selection, descriptive fit, held-out predictive test (G5).

Content basis: `SCF_GALAXY_DYNAMICS_IMPLEMENTATION_PLAN.md` §10 and
`docs/galaxy_dynamics_scope.md`. Depends only on already-verified G1-G4
machinery (`astrophysics.*`, `validation.sparc_data`) -- no new physics is
introduced here, only the pilot protocol itself.
"""
from __future__ import annotations

import hashlib
import math
from collections import defaultdict
from dataclasses import dataclass, field, replace
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from ..astrophysics import (
    BurkertProfile,
    NFWProfile,
    baseline_total_g_halo,
    baseline_total_g_mond,
)
from .sparc_data import (
    SparcComponentRow,
    SparcMetadataRow,
    combine_baryonic_v2,
    scale_distance,
    scale_inclination,
    validate_cross_table_consistency,
)


# ---------------------------------------------------------------------------
# 10.1 -- frozen selection
# ---------------------------------------------------------------------------
def _sha_key(galaxy_id: str) -> str:
    return hashlib.sha256(f"SCF-GALAXY-v1|{galaxy_id}".encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class FrozenSelection:
    dev_galaxies: Tuple[str, ...]
    eval_galaxies: Tuple[str, ...]
    n_eligible_total: int
    tercile_sizes: Tuple[int, int, int]
    tercile_report: Tuple[dict, ...]
    exclusions: Tuple[dict, ...]


def select_frozen_sample(
    meta_rows: Sequence[SparcMetadataRow],
    comp_rows: Sequence[SparcComponentRow],
    inc_min_deg: float = 30.0,
    inc_max_deg: float = 80.0,
    min_radial_points: int = 10,
) -> FrozenSelection:
    """Deterministic frozen 6+6 dev/eval selection (Plan §10.1).

    Eligibility: quality flag 1 or 2, positive distance, positive
    effective surface brightness, inclination in
    [`inc_min_deg`, `inc_max_deg`] (the upper bound is itself a pilot
    decision per the plan), and at least `min_radial_points` radial
    points in the component table.

    Sort by `log10(SBeff)` then galaxy ID; split into three nearly-equal
    contiguous terciles (sizes differ by at most 1, extra items go to the
    earlier terciles -- a deterministic, documented convention, since the
    plan does not fix how a non-multiple-of-3 remainder is placed).
    Within each tercile, rank by `sha256("SCF-GALAXY-v1|<ID>")` (tie: ID)
    and take the first four: first two -> development, next two ->
    evaluation.

    Raises if any tercile has fewer than 4 eligible galaxies (Plan §10.1:
    "die Protokolländerung vor Modellresultaten dokumentieren" -- this
    function refuses to proceed silently rather than document a deviation
    after the fact).

    Also runs `validate_cross_table_consistency` first (SCF_REVIEW_G0_G7_
    5563e67.md finding R5): neither table's own parser alone can catch a
    galaxy whose distance disagrees between metadata and component rows.
    """
    validate_cross_table_consistency(meta_rows, comp_rows)

    radial_counts: Dict[str, int] = defaultdict(int)
    for r in comp_rows:
        radial_counts[r.galaxy] += 1

    exclusions: List[dict] = []
    eligible: List[SparcMetadataRow] = []
    for m in meta_rows:
        reasons = []
        if m.Q not in (1, 2):
            reasons.append(f"Q={m.Q} not in {{1,2}}")
        if not (m.D_mpc > 0):
            reasons.append(f"D_mpc={m.D_mpc} not positive")
        if not (m.SBeff_sollum_pc2 > 0):
            reasons.append(f"SBeff={m.SBeff_sollum_pc2} not positive")
        if not (inc_min_deg <= m.inc_deg <= inc_max_deg):
            reasons.append(f"inc_deg={m.inc_deg} outside [{inc_min_deg},{inc_max_deg}]")
        n_rad = radial_counts.get(m.galaxy, 0)
        if n_rad < min_radial_points:
            reasons.append(f"only {n_rad} radial points, need >= {min_radial_points}")
        if reasons:
            exclusions.append({"galaxy": m.galaxy, "reasons": reasons})
        else:
            eligible.append(m)

    eligible_sorted = sorted(eligible, key=lambda m: (math.log10(m.SBeff_sollum_pc2), m.galaxy))

    n = len(eligible_sorted)
    base, rem = divmod(n, 3)
    sizes = tuple(base + (1 if i < rem else 0) for i in range(3))

    thirds: List[List[SparcMetadataRow]] = []
    idx = 0
    for s in sizes:
        thirds.append(eligible_sorted[idx:idx + s])
        idx += s

    dev: List[str] = []
    ev: List[str] = []
    tercile_report = []
    for t_idx, third in enumerate(thirds):
        if len(third) < 4:
            raise ValueError(
                f"tercile {t_idx} has only {len(third)} eligible galaxies (need >= 4) -- "
                f"protocol deviation must be documented before any model results (Plan §10.1)"
            )
        ranked = sorted(third, key=lambda m: (_sha_key(m.galaxy), m.galaxy))
        chosen = ranked[:4]
        dev.extend(m.galaxy for m in chosen[:2])
        ev.extend(m.galaxy for m in chosen[2:4])
        tercile_report.append({
            "tercile": t_idx,
            "n_eligible": len(third),
            "chosen": [m.galaxy for m in chosen],
            "dev": [m.galaxy for m in chosen[:2]],
            "eval": [m.galaxy for m in chosen[2:4]],
        })

    return FrozenSelection(
        dev_galaxies=tuple(dev),
        eval_galaxies=tuple(ev),
        n_eligible_total=n,
        tercile_sizes=sizes,
        tercile_report=tuple(tercile_report),
        exclusions=tuple(exclusions),
    )


# ---------------------------------------------------------------------------
# Shared helpers: baryonic acceleration and Mode A/B use the same v_bar^2
# combination (Plan §9.3), with the first transparent-baseline M/L ratios.
# ---------------------------------------------------------------------------
def galaxy_component_rows(comp_rows: Sequence[SparcComponentRow], galaxy: str) -> List[SparcComponentRow]:
    rows = [r for r in comp_rows if r.galaxy == galaxy]
    rows.sort(key=lambda r: r.R_kpc)
    return rows


def baryon_g_kms2_per_pc(rows: Sequence[SparcComponentRow], upsilon_d: float = 0.5, upsilon_b: float = 0.7):
    """g_bar(r) [(km/s)^2/pc] = v_bar^2/r for each row, r in pc."""
    r_pc = np.array([r.R_kpc * 1000.0 for r in rows])
    v2 = np.array([combine_baryonic_v2(r.Vgas_kms, r.Vdisk_kms, r.Vbul_kms, upsilon_d, upsilon_b) for r in rows])
    return r_pc, v2 / r_pc


# ---------------------------------------------------------------------------
# 10.2 -- Mode A: descriptive parameter analysis
# ---------------------------------------------------------------------------
#: First-pass declared computational bounds (Plan §10.2) -- NOT astronomical
#: population priors.
LOG_RHO_BOUNDS = (-4.0, 1.0)      # log10(rho0/[Msun/pc^3])
LOG_RSCALE_KPC_BOUNDS = (-2.0, 2.5)  # log10(r0/kpc)


@dataclass(frozen=True)
class DescriptiveFitResult:
    galaxy: str
    rho0_msun_pc3: float
    r0_pc: float
    mu_h: float
    psi: float
    eta: float
    status: str
    boundary_hit: bool
    rmse_kms: float
    n_invalid_points: int


@dataclass(frozen=True)
class HaloLeastSquaresFit:
    """Shared multi-start + one-decade-boundary-expansion fit result for
    ANY 2-log-parameter halo family (SCF_REVIEW_G0_G7_5563e67.md finding
    R2: NFW previously got a single start and no boundary expansion,
    unlike Burkert -- both now go through `_fit_halo_least_squares`)."""

    log_p1: float
    log_p2: float
    status: str
    boundary_hit: bool
    cost: float


def _fit_halo_least_squares(
    resid_fn,
    log_p1_bounds: Tuple[float, float],
    log_p2_bounds: Tuple[float, float],
) -> HaloLeastSquaresFit:
    """3 deterministic starts (bounds midpoint; each corner inset by 0.5
    dex) + a single one-decade expansion on whichever bound(s) are hit,
    reported via `boundary_hit` if still at an edge after expansion --
    identical discipline for every halo family that calls this."""
    from scipy.optimize import least_squares

    starts = [
        (np.mean(log_p1_bounds), np.mean(log_p2_bounds)),
        (log_p1_bounds[0] + 0.5, log_p2_bounds[0] + 0.5),
        (log_p1_bounds[1] - 0.5, log_p2_bounds[1] - 0.5),
    ]

    def run(b1, b2):
        best = None
        for x0 in starts:
            sol = least_squares(resid_fn, x0=x0, bounds=([b1[0], b2[0]], [b1[1], b2[1]]))
            cost = float(np.sum(sol.fun ** 2))
            if best is None or cost < best[0]:
                best = (cost, sol)
        return best

    tol = 1e-6
    cost, sol = run(log_p1_bounds, log_p2_bounds)
    p1, p2 = sol.x
    hit_lo1 = abs(p1 - log_p1_bounds[0]) < tol
    hit_hi1 = abs(p1 - log_p1_bounds[1]) < tol
    hit_lo2 = abs(p2 - log_p2_bounds[0]) < tol
    hit_hi2 = abs(p2 - log_p2_bounds[1]) < tol
    boundary_hit = hit_lo1 or hit_hi1 or hit_lo2 or hit_hi2

    if boundary_hit:
        exp1 = (log_p1_bounds[0] - (1.0 if hit_lo1 else 0.0), log_p1_bounds[1] + (1.0 if hit_hi1 else 0.0))
        exp2 = (log_p2_bounds[0] - (1.0 if hit_lo2 else 0.0), log_p2_bounds[1] + (1.0 if hit_hi2 else 0.0))
        cost2, sol2 = run(exp1, exp2)
        p1b, p2b = sol2.x
        still = (abs(p1b - exp1[0]) < tol or abs(p1b - exp1[1]) < tol or
                 abs(p2b - exp2[0]) < tol or abs(p2b - exp2[1]) < tol)
        sol, cost = sol2, cost2
        p1, p2 = p1b, p2b
        boundary_hit = still

    status = "converged" if sol.success else "not_converged"
    return HaloLeastSquaresFit(log_p1=p1, log_p2=p2, status=status, boundary_hit=boundary_hit, cost=cost)


def _predicted_v_obs_for_fitting(rows: Sequence[SparcComponentRow], rho0: float, r0_pc: float,
                                  upsilon_d: float, upsilon_b: float) -> np.ndarray:
    """OPTIMIZER-INTERNAL residual helper only -- NOT a final reported
    prediction. A negative intermediate `g_total` during optimization is
    a normal, numerically-necessary penalty device (clip-then-let-the-
    residual-grow), not a physical claim that v=0 there (SCF_REVIEW_
    G0_G7_5563e67.md finding R3: this distinction was previously blurred
    -- the FINAL reported RMSE/scores now go through
    `_predict_v_with_validity` instead, which reports invalid points
    explicitly rather than silently returning 0)."""
    prof = BurkertProfile(rho0_msun_pc3=rho0, r0_pc=r0_pc)
    r_pc, g_bar = baryon_g_kms2_per_pc(rows, upsilon_d, upsilon_b)
    g_halo = np.array([prof.g(r) for r in r_pc])
    g_total = g_bar + g_halo
    g_total_penalty = np.clip(g_total, 0.0, None)
    return np.sqrt(g_total_penalty * r_pc)


def _predict_v_with_validity(g_total: np.ndarray, r_pc: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """FINAL-reporting prediction (SCF_REVIEW_G0_G7_5563e67.md finding
    R3): a point with `g_total < 0` has no real circular orbit in this
    model -- `v_pred` there is `NaN`, never silently `0`. Returns
    `(v_pred, valid_mask)`; callers must compute scores only over
    `valid_mask` and report `sum(~valid_mask)` explicitly."""
    g_total = np.asarray(g_total, dtype=float)
    r_pc = np.asarray(r_pc, dtype=float)
    valid = g_total >= 0.0
    v_pred = np.full_like(g_total, np.nan, dtype=float)
    v_pred[valid] = np.sqrt(g_total[valid] * r_pc[valid])
    return v_pred, valid


def _final_rmse_and_invalid(rows: Sequence[SparcComponentRow], prof, upsilon_d: float, upsilon_b: float
                             ) -> Tuple[float, int]:
    """Validity-aware RMSE for a fitted profile against its OWN training/
    full curve -- the number actually reported in `DescriptiveFitResult`."""
    r_pc, g_bar = baryon_g_kms2_per_pc(rows, upsilon_d, upsilon_b)
    g_halo = np.array([prof.g(r) for r in r_pc])
    v_pred, valid = _predict_v_with_validity(g_bar + g_halo, r_pc)
    v_obs = np.array([r.Vobs_kms for r in rows])
    n_invalid = int(np.sum(~valid))
    if not np.any(valid):
        return float("nan"), n_invalid
    rmse = float(np.sqrt(np.mean((v_pred[valid] - v_obs[valid]) ** 2)))
    return rmse, n_invalid


def fit_burkert_descriptive(
    rows: Sequence[SparcComponentRow],
    galaxy: str = "",
    upsilon_d: float = 0.5,
    upsilon_b: float = 0.7,
    log_rho_bounds: Tuple[float, float] = LOG_RHO_BOUNDS,
    log_rscale_kpc_bounds: Tuple[float, float] = LOG_RSCALE_KPC_BOUNDS,
) -> DescriptiveFitResult:
    """Mode A (Plan §10.2): fit (rho0, r0) to the FULL curve via least
    squares in log-positive parameters, multiple deterministic starting
    points, declared bounds with a single one-decade expansion on a
    boundary hit (reported, not silently re-expanded further)."""
    v_obs = np.array([r.Vobs_kms for r in rows])
    e_vobs = np.array([r.e_Vobs_kms for r in rows])

    def resid(params):
        log_rho, log_r_kpc = params
        rho0 = 10 ** log_rho
        r0_pc = 10 ** log_r_kpc * 1000.0
        v_pred = _predicted_v_obs_for_fitting(rows, rho0, r0_pc, upsilon_d, upsilon_b)
        return (v_pred - v_obs) / e_vobs

    fit = _fit_halo_least_squares(resid, log_rho_bounds, log_rscale_kpc_bounds)
    rho0 = 10 ** fit.log_p1
    r0_pc = 10 ** fit.log_p2 * 1000.0
    mu_h = rho0 * r0_pc
    psi = math.log10(rho0) + math.log10(r0_pc)
    eta = math.log10(r0_pc)
    prof = BurkertProfile(rho0_msun_pc3=rho0, r0_pc=r0_pc)
    rmse, n_invalid = _final_rmse_and_invalid(rows, prof, upsilon_d, upsilon_b)

    return DescriptiveFitResult(
        galaxy=galaxy, rho0_msun_pc3=rho0, r0_pc=r0_pc, mu_h=mu_h,
        psi=psi, eta=eta, status=fit.status, boundary_hit=fit.boundary_hit,
        rmse_kms=rmse, n_invalid_points=n_invalid,
    )


# ---------------------------------------------------------------------------
# 10.3/10.4 -- Mode B: held-out outer-radius test
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class HeldOutSplit:
    train_rows: Tuple[SparcComponentRow, ...]
    test_rows: Tuple[SparcComponentRow, ...]


def train_test_split_outer(rows: Sequence[SparcComponentRow], train_frac: float = 0.70) -> HeldOutSplit:
    """Plan §10.3: sort by ascending radius, first `train_frac` are
    training, the remaining outer radii are test. Requires >=7 train and
    >=3 test points."""
    rows_sorted = sorted(rows, key=lambda r: r.R_kpc)
    n = len(rows_sorted)
    n_train = int(math.floor(train_frac * n))
    train = rows_sorted[:n_train]
    test = rows_sorted[n_train:]
    if len(train) < 7 or len(test) < 3:
        raise ValueError(f"galaxy has {len(train)} train / {len(test)} test radii; "
                          f"need >=7 train and >=3 test (Plan §10.3)")
    return HeldOutSplit(train_rows=tuple(train), test_rows=tuple(test))


@dataclass(frozen=True)
class PredictiveScore:
    galaxy: str
    baseline: str
    mae_kms: float
    rmse_kms: float
    n_test: int
    n_invalid: int
    train_status: str
    train_boundary_hit: bool


def _fit_nfw_holdout(split: HeldOutSplit, upsilon_d: float, upsilon_b: float) -> Tuple[NFWProfile, HaloLeastSquaresFit]:
    """Baseline B training fit -- goes through the SAME
    `_fit_halo_least_squares` as Baseline A (SCF_REVIEW_G0_G7_5563e67.md
    finding R2: previously a single start, no boundary expansion, and
    `sol.success` was discarded; a real NGC3109 fit hit the lower rho_s
    bound and this went unreported)."""
    r_train_pc, g_bar_train = baryon_g_kms2_per_pc(split.train_rows, upsilon_d, upsilon_b)
    v_obs_train = np.array([r.Vobs_kms for r in split.train_rows])
    e_vobs_train = np.array([r.e_Vobs_kms for r in split.train_rows])

    def resid_nfw(params):
        log_rho_s, log_r_s_kpc = params
        prof = NFWProfile(rho_s_msun_pc3=10 ** log_rho_s, r_s_pc=10 ** log_r_s_kpc * 1000.0)
        g_halo = np.array([prof.g(r) for r in r_train_pc])
        g_total_penalty = np.clip(g_bar_train + g_halo, 0.0, None)  # optimizer-internal penalty, see R3 docstring
        v_pred = np.sqrt(g_total_penalty * r_train_pc)
        return (v_pred - v_obs_train) / e_vobs_train

    fit = _fit_halo_least_squares(resid_nfw, LOG_RHO_BOUNDS, LOG_RSCALE_KPC_BOUNDS)
    halo_b = NFWProfile(rho_s_msun_pc3=10 ** fit.log_p1, r_s_pc=10 ** fit.log_p2 * 1000.0)
    return halo_b, fit


def evaluate_baselines_on_holdout(
    galaxy: str,
    split: HeldOutSplit,
    upsilon_d: float = 0.5,
    upsilon_b: float = 0.7,
) -> Tuple[PredictiveScore, ...]:
    """Fit Burkert (Baseline A) and NFW (Baseline B) halo parameters on
    `split.train_rows` only, with IDENTICAL fitting discipline for both
    (R2); evaluate all three baselines (A, B, C=MOND) on `split.test_rows`
    with explicit invalid-point handling instead of silent clipping (R3).
    Baryonic components at test radii are used as known covariates (Plan
    §10.3: 'bedingte radiale Extrapolation')."""
    fit_a_result = fit_burkert_descriptive(split.train_rows, galaxy=galaxy, upsilon_d=upsilon_d, upsilon_b=upsilon_b)
    halo_a = BurkertProfile(rho0_msun_pc3=fit_a_result.rho0_msun_pc3, r0_pc=fit_a_result.r0_pc)
    halo_b, fit_b = _fit_nfw_holdout(split, upsilon_d, upsilon_b)

    r_test_pc, g_bar_test = baryon_g_kms2_per_pc(split.test_rows, upsilon_d, upsilon_b)
    v_obs_test = np.array([r.Vobs_kms for r in split.test_rows])

    def baryon_g_fn(r_pc):
        r_pc = np.atleast_1d(r_pc)
        return np.array([g_bar_test[np.argmin(np.abs(r_test_pc - r))] for r in r_pc])

    def score_from_valid(name, v_pred, valid, train_status, train_boundary_hit):
        n_invalid = int(np.sum(~valid))
        if not np.any(valid):
            return PredictiveScore(galaxy=galaxy, baseline=name, mae_kms=float("nan"), rmse_kms=float("nan"),
                                    n_test=len(split.test_rows), n_invalid=n_invalid,
                                    train_status=train_status, train_boundary_hit=train_boundary_hit)
        err = v_pred[valid] - v_obs_test[valid]
        return PredictiveScore(
            galaxy=galaxy, baseline=name,
            mae_kms=float(np.mean(np.abs(err))), rmse_kms=float(np.sqrt(np.mean(err ** 2))),
            n_test=len(split.test_rows), n_invalid=n_invalid,
            train_status=train_status, train_boundary_hit=train_boundary_hit,
        )

    scores = []

    g_total_a = g_bar_test + np.array([halo_a.g(r) for r in r_test_pc])
    v_pred_a, valid_a = _predict_v_with_validity(g_total_a, r_test_pc)
    scores.append(score_from_valid("A_burkert", v_pred_a, valid_a, fit_a_result.status, fit_a_result.boundary_hit))

    g_total_b = g_bar_test + np.array([halo_b.g(r) for r in r_test_pc])
    v_pred_b, valid_b = _predict_v_with_validity(g_total_b, r_test_pc)
    scores.append(score_from_valid("B_nfw", v_pred_b, valid_b, fit_b.status, fit_b.boundary_hit))

    # Baseline C (MOND): mond_g_total itself requires g_N >= 0 (raises
    # otherwise) -- filter to g_bar_test >= 0 BEFORE calling it, rather
    # than letting one bad point abort the whole comparison while A/B
    # silently clipped theirs (R3's cross-model inconsistency).
    valid_c = g_bar_test >= 0.0
    v_pred_c = np.full_like(g_bar_test, np.nan, dtype=float)
    if np.any(valid_c):
        g_total_c_valid = baseline_total_g_mond(baryon_g_fn, r_test_pc[valid_c])
        v_pred_c_valid, valid_c_inner = _predict_v_with_validity(g_total_c_valid, r_test_pc[valid_c])
        idx = np.where(valid_c)[0]
        v_pred_c[idx[valid_c_inner]] = v_pred_c_valid[valid_c_inner]
        valid_c = np.zeros_like(valid_c)
        valid_c[idx[valid_c_inner]] = True
    scores.append(score_from_valid("C_mond", v_pred_c, valid_c, "n/a (no fit)", False))

    return tuple(scores)


# ---------------------------------------------------------------------------
# R6 (SCF_REVIEW_G0_G7_5563e67.md): real profile likelihood over psi, plus
# distance/inclination sensitivity -- `psi`/`eta` in DescriptiveFitResult
# are only the BEST FIT's coordinates, not a profile; this section adds
# the actual profile and a declared, non-test-selected sensitivity scan.
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class ProfileLikelihoodPoint:
    psi: float
    eta_min: float
    q: float
    status: str
    boundary_hit: bool
    feasible: bool


def profile_likelihood_burkert(
    rows: Sequence[SparcComponentRow],
    psi_grid: Sequence[float],
    upsilon_d: float = 0.5,
    upsilon_b: float = 0.7,
    log_rho_bounds: Tuple[float, float] = LOG_RHO_BOUNDS,
    log_rscale_kpc_bounds: Tuple[float, float] = LOG_RSCALE_KPC_BOUNDS,
) -> Tuple[ProfileLikelihoodPoint, ...]:
    """R6's concrete profile task: for each fixed `psi = log10(mu_h /
    [Msun pc^-2])`, minimize `chi2` over `eta = log10(r0/pc)` alone, with
    `rho0 = 10**(psi-eta)`, `r0 = 10**eta`.

    The declared bounds are on `log10(rho0/[Msun/pc^3])`
    (`log_rho_bounds`) and `log10(r0/kpc)` (`log_rscale_kpc_bounds`), NOT
    directly on `eta` or `psi-eta` -- converting correctly: `eta =
    log10(r0/pc) = log10(r0/kpc) + 3`, so the eta bound is
    `log_rscale_kpc_bounds` shifted by +3 (declared values -> eta in
    [1, 5.5]); `psi-eta = log10(rho0)` must lie in `log_rho_bounds`
    directly. The FEASIBLE eta range at a given `psi` is the
    intersection `eta in [max(eta_lo, psi-log_rho_bounds[1]),
    min(eta_hi, psi-log_rho_bounds[0])]` -- this depends on `psi`, unlike
    a fixed box (the mistake R6 explicitly warns against). A `psi` whose
    feasible interval is empty is marked `feasible=False`, never silently
    dropped or clamped.

    Uses the SAME optimizer-internal clip-as-penalty as `_predicted_v_obs_
    for_fitting` (this is 1-D exploration of a scalar objective, not a
    final reported prediction -- consistent with R3's fitting/reporting
    distinction).
    """
    from scipy.optimize import minimize_scalar

    v_obs = np.array([r.Vobs_kms for r in rows])
    e_vobs = np.array([r.e_Vobs_kms for r in rows])
    r_pc, g_bar = baryon_g_kms2_per_pc(rows, upsilon_d, upsilon_b)
    eta_bounds = (log_rscale_kpc_bounds[0] + 3.0, log_rscale_kpc_bounds[1] + 3.0)

    def chi2_at(eta: float, psi: float) -> float:
        rho0 = 10 ** (psi - eta)
        r0_pc = 10 ** eta
        prof = BurkertProfile(rho0_msun_pc3=rho0, r0_pc=r0_pc)
        g_halo = np.array([prof.g(r) for r in r_pc])
        g_total_penalty = np.clip(g_bar + g_halo, 0.0, None)
        v_pred = np.sqrt(g_total_penalty * r_pc)
        return float(np.sum(((v_pred - v_obs) / e_vobs) ** 2))

    points = []
    tol = 1e-6
    for psi in psi_grid:
        eta_lo = max(eta_bounds[0], psi - log_rho_bounds[1])
        eta_hi = min(eta_bounds[1], psi - log_rho_bounds[0])
        if eta_lo >= eta_hi:
            points.append(ProfileLikelihoodPoint(psi=float(psi), eta_min=float("nan"), q=float("nan"),
                                                   status="infeasible_bounds", boundary_hit=False, feasible=False))
            continue
        res = minimize_scalar(chi2_at, args=(psi,), bounds=(eta_lo, eta_hi), method="bounded")
        boundary_hit = abs(res.x - eta_lo) < tol or abs(res.x - eta_hi) < tol
        points.append(ProfileLikelihoodPoint(
            psi=float(psi), eta_min=float(res.x), q=float(res.fun),
            status="converged" if res.success else "not_converged",
            boundary_hit=bool(boundary_hit), feasible=True,
        ))
    return tuple(points)


@dataclass(frozen=True)
class SensitivityScenario:
    name: str
    rho0_msun_pc3: float
    r0_pc: float
    mu_h: float
    status: str
    boundary_hit: bool


def distance_inclination_sensitivity(
    rows: Sequence[SparcComponentRow],
    meta_row: SparcMetadataRow,
    upsilon_d: float = 0.5,
    upsilon_b: float = 0.7,
) -> Tuple[SensitivityScenario, ...]:
    """R6's concrete sensitivity task: reference + `D+-sigma_D` +
    `i+-sigma_i`, each an INDEPENDENTLY refit Mode-A descriptive fit
    (never selected by any test-set performance -- there is no test set
    in Mode A). Reported as SENSITIVITY, not a calibrated uncertainty band
    (Plan §10.4's own caution against that conflation).

    Physical distinction that a naive "rescale everything by alpha_D"
    would miss (re-derived from Plan §9.4 during R6, not assumed):
    `Vobs`/`e_Vobs` are direct spectroscopic (line-of-sight Doppler)
    measurements, independent of the ASSUMED distance -- only `R_kpc` and
    the baryonic components (`Vgas`/`Vdisk`/`Vbul`, distance-dependent via
    the assumed mass-to-light conversion) are rescaled by `scale_distance`
    when `D` changes (this is exactly why the plan states `g_obs=v_obs^2/r`
    stays distance-dependent while `g_bar` does not -- §9.4). Conversely,
    an inclination change re-derives `Vobs`/`e_Vobs` via `scale_inclination`
    and leaves radius/baryons untouched (inclination does not affect the
    assumed distance-to-radius conversion).
    """
    sigma_D = meta_row.e_D_mpc
    sigma_i = meta_row.e_inc_deg
    D_ref = meta_row.D_mpc
    i_ref = meta_row.inc_deg

    def refit(new_rows, name: str) -> SensitivityScenario:
        fit = fit_burkert_descriptive(new_rows, galaxy=meta_row.galaxy, upsilon_d=upsilon_d, upsilon_b=upsilon_b)
        return SensitivityScenario(name=name, rho0_msun_pc3=fit.rho0_msun_pc3, r0_pc=fit.r0_pc,
                                    mu_h=fit.mu_h, status=fit.status, boundary_hit=fit.boundary_hit)

    scenarios = [refit(rows, "reference")]

    for sign, label in ((+1.0, "D+sigma_D"), (-1.0, "D-sigma_D")):
        alpha_D = (D_ref + sign * sigma_D) / D_ref
        new_rows = []
        for r in rows:
            new_R_kpc, new_Vgas = scale_distance(r.R_kpc, r.Vgas_kms, alpha_D)
            _, new_Vdisk = scale_distance(r.R_kpc, r.Vdisk_kms, alpha_D)
            _, new_Vbul = scale_distance(r.R_kpc, r.Vbul_kms, alpha_D)
            new_rows.append(replace(r, R_kpc=new_R_kpc, Vgas_kms=new_Vgas,
                                     Vdisk_kms=new_Vdisk, Vbul_kms=new_Vbul,
                                     D_mpc=D_ref + sign * sigma_D))
        scenarios.append(refit(new_rows, label))

    for sign, label in ((+1.0, "i+sigma_i"), (-1.0, "i-sigma_i")):
        i_new = i_ref + sign * sigma_i
        new_rows = []
        for r in rows:
            new_Vobs, new_eVobs = scale_inclination(r.Vobs_kms, r.e_Vobs_kms, i_ref, i_new)
            new_rows.append(replace(r, Vobs_kms=new_Vobs, e_Vobs_kms=new_eVobs))
        scenarios.append(refit(new_rows, label))

    return tuple(scenarios)
