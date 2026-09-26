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
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from ..astrophysics import (
    BurkertProfile,
    NFWProfile,
    baseline_total_g_halo,
    baseline_total_g_mond,
)
from .sparc_data import SparcComponentRow, SparcMetadataRow, combine_baryonic_v2


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
    """
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


def _predicted_v_obs(rows: Sequence[SparcComponentRow], rho0: float, r0_pc: float,
                      upsilon_d: float, upsilon_b: float) -> np.ndarray:
    prof = BurkertProfile(rho0_msun_pc3=rho0, r0_pc=r0_pc)
    r_pc, g_bar = baryon_g_kms2_per_pc(rows, upsilon_d, upsilon_b)
    g_halo = np.array([prof.g(r) for r in r_pc])
    g_total = g_bar + g_halo
    # g may be negative in pathological synthetic cases; guard before sqrt.
    g_total_safe = np.clip(g_total, 0.0, None)
    return np.sqrt(g_total_safe * r_pc)


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
    from scipy.optimize import least_squares

    v_obs = np.array([r.Vobs_kms for r in rows])
    e_vobs = np.array([r.e_Vobs_kms for r in rows])

    def resid(params, lo, hi):
        log_rho, log_r_kpc = params
        rho0 = 10 ** log_rho
        r0_pc = 10 ** log_r_kpc * 1000.0
        v_pred = _predicted_v_obs(rows, rho0, r0_pc, upsilon_d, upsilon_b)
        return (v_pred - v_obs) / e_vobs

    starts = [
        (np.mean(log_rho_bounds), np.mean(log_rscale_kpc_bounds)),
        (log_rho_bounds[0] + 0.5, log_rscale_kpc_bounds[0] + 0.5),
        (log_rho_bounds[1] - 0.5, log_rscale_kpc_bounds[1] - 0.5),
    ]

    def run(bounds):
        best = None
        for x0 in starts:
            sol = least_squares(resid, x0=x0, args=bounds, bounds=(
                [bounds[0][0], bounds[1][0]], [bounds[0][1], bounds[1][1]]))
            cost = float(np.sum(sol.fun ** 2))
            if best is None or cost < best[0]:
                best = (cost, sol)
        return best[1]

    sol = run((log_rho_bounds, log_rscale_kpc_bounds))
    log_rho, log_r_kpc = sol.x
    tol = 1e-6
    hit_lo_rho = abs(log_rho - log_rho_bounds[0]) < tol
    hit_hi_rho = abs(log_rho - log_rho_bounds[1]) < tol
    hit_lo_r = abs(log_r_kpc - log_rscale_kpc_bounds[0]) < tol
    hit_hi_r = abs(log_r_kpc - log_rscale_kpc_bounds[1]) < tol
    boundary_hit = hit_lo_rho or hit_hi_rho or hit_lo_r or hit_hi_r

    if boundary_hit:
        expanded_rho = (log_rho_bounds[0] - (1.0 if hit_lo_rho else 0.0),
                         log_rho_bounds[1] + (1.0 if hit_hi_rho else 0.0))
        expanded_r = (log_rscale_kpc_bounds[0] - (1.0 if hit_lo_r else 0.0),
                      log_rscale_kpc_bounds[1] + (1.0 if hit_hi_r else 0.0))
        sol2 = run((expanded_rho, expanded_r))
        log_rho2, log_r_kpc2 = sol2.x
        still_at_edge = (
            abs(log_rho2 - expanded_rho[0]) < tol or abs(log_rho2 - expanded_rho[1]) < tol or
            abs(log_r_kpc2 - expanded_r[0]) < tol or abs(log_r_kpc2 - expanded_r[1]) < tol
        )
        sol = sol2
        log_rho, log_r_kpc = log_rho2, log_r_kpc2
        boundary_hit = still_at_edge

    rho0 = 10 ** log_rho
    r0_pc = 10 ** log_r_kpc * 1000.0
    mu_h = rho0 * r0_pc
    psi = math.log10(rho0) + math.log10(r0_pc)
    eta = math.log10(r0_pc)
    v_pred = _predicted_v_obs(rows, rho0, r0_pc, upsilon_d, upsilon_b)
    rmse = float(np.sqrt(np.mean((v_pred - v_obs) ** 2)))
    status = "converged" if sol.success else "not_converged"

    return DescriptiveFitResult(
        galaxy=galaxy, rho0_msun_pc3=rho0, r0_pc=r0_pc, mu_h=mu_h,
        psi=psi, eta=eta, status=status, boundary_hit=boundary_hit, rmse_kms=rmse,
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


def evaluate_baselines_on_holdout(
    galaxy: str,
    split: HeldOutSplit,
    upsilon_d: float = 0.5,
    upsilon_b: float = 0.7,
) -> Tuple[PredictiveScore, ...]:
    """Fit Burkert (Baseline A) and NFW (Baseline B) halo parameters on
    `split.train_rows` only; evaluate all three baselines (A, B, C=MOND)
    on `split.test_rows`. Baryonic components at test radii are used as
    known covariates (Plan §10.3: 'bedingte radiale Extrapolation')."""
    fit_a = fit_burkert_descriptive(split.train_rows, galaxy=galaxy, upsilon_d=upsilon_d, upsilon_b=upsilon_b)
    halo_a = BurkertProfile(rho0_msun_pc3=fit_a.rho0_msun_pc3, r0_pc=fit_a.r0_pc)

    # Baseline B (NFW): same least-squares machinery, mapped onto NFW's own
    # (rho_s, r_s) scale parameters -- never mixed into Baseline A's column.
    from scipy.optimize import least_squares

    r_train_pc, g_bar_train = baryon_g_kms2_per_pc(split.train_rows, upsilon_d, upsilon_b)
    v_obs_train = np.array([r.Vobs_kms for r in split.train_rows])
    e_vobs_train = np.array([r.e_Vobs_kms for r in split.train_rows])

    def resid_nfw(params):
        log_rho_s, log_r_s_kpc = params
        prof = NFWProfile(rho_s_msun_pc3=10 ** log_rho_s, r_s_pc=10 ** log_r_s_kpc * 1000.0)
        g_halo = np.array([prof.g(r) for r in r_train_pc])
        g_total = np.clip(g_bar_train + g_halo, 0.0, None)
        v_pred = np.sqrt(g_total * r_train_pc)
        return (v_pred - v_obs_train) / e_vobs_train

    sol_b = least_squares(resid_nfw, x0=[np.mean(LOG_RHO_BOUNDS), np.mean(LOG_RSCALE_KPC_BOUNDS)],
                           bounds=([LOG_RHO_BOUNDS[0], LOG_RSCALE_KPC_BOUNDS[0]],
                                   [LOG_RHO_BOUNDS[1], LOG_RSCALE_KPC_BOUNDS[1]]))
    halo_b = NFWProfile(rho_s_msun_pc3=10 ** sol_b.x[0], r_s_pc=10 ** sol_b.x[1] * 1000.0)

    r_test_pc, g_bar_test = baryon_g_kms2_per_pc(split.test_rows, upsilon_d, upsilon_b)
    v_obs_test = np.array([r.Vobs_kms for r in split.test_rows])

    def baryon_g_fn(r_pc):
        r_pc = np.atleast_1d(r_pc)
        return np.array([g_bar_test[np.argmin(np.abs(r_test_pc - r))] for r in r_pc])

    scores = []
    for name, g_total in (
        ("A_burkert", g_bar_test + np.array([halo_a.g(r) for r in r_test_pc])),
        ("B_nfw", g_bar_test + np.array([halo_b.g(r) for r in r_test_pc])),
        ("C_mond", baseline_total_g_mond(baryon_g_fn, r_test_pc)),
    ):
        v_pred = np.sqrt(np.clip(g_total, 0.0, None) * r_test_pc)
        err = v_pred - v_obs_test
        scores.append(PredictiveScore(
            galaxy=galaxy, baseline=name,
            mae_kms=float(np.mean(np.abs(err))),
            rmse_kms=float(np.sqrt(np.mean(err ** 2))),
            n_test=len(split.test_rows),
        ))
    return tuple(scores)
