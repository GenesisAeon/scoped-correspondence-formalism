"""Joint scenarios for the galaxy held-out comparison (Paket J7, plan §13.3).

Extends the existing ONE-AT-A-TIME sensitivity (``galaxy_pilot.
distance_inclination_sensitivity_mode_b``: D +- sigma, i +- sigma
separately) to a JOINT scenario grid over distance D, inclination i and the
disk / bulge mass-to-light ratios. Additive: ``galaxy_pilot.py`` (a verified
module) is not modified; its transformations and its held-out evaluation are
reused unchanged.

Per joint scenario point (plan §13.3):

1. the SAME physical transformation is applied to train AND test rows of
   every compared model (radii and baryonic components scale with D via
   ``scale_distance``; observed velocity and its error with i via
   ``scale_inclination``);
2. train/test radii stay the same points;
3. model parameters are refit on the transformed TRAINING radii only
   (``evaluate_baselines_on_holdout``);
4. losses are computed on the held-out outer radii;
5. invalid predictions, non-converged fits and boundary hits are reported.

Primary target: the DIFFERENCE of held-out losses between two baselines
(``primary_rmse_kms``, which is None when a baseline has any invalid test
point -- such scenarios are counted, never silently dropped). The grid is a
SCENARIO SPACE: counts of sign changes are not probabilities. a0 is not
fitted (that would be a different, separately named MOND variant).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, replace
from typing import Dict, List, Optional, Sequence, Tuple

from scoped_correspondence.errors import ScopeViolationError
from scoped_correspondence.validation.galaxy_pilot import HeldOutSplit, evaluate_baselines_on_holdout
from scoped_correspondence.validation.global_sensitivity import JointScenarioGrid
from scoped_correspondence.validation.sparc_data import SparcComponentRow, SparcMetadataRow, scale_distance, scale_inclination

REQUIRED = ("D_sigma", "i_sigma", "upsilon_d", "upsilon_b")


@dataclass(frozen=True)
class JointScenarioResult:
    point: Dict[str, float]
    scores: Dict[str, Optional[float]]  # baseline -> primary RMSE (None if any invalid test point)
    statuses: Dict[str, str]
    train_boundary_hits: Dict[str, bool]
    loss_difference: Optional[float]  # baseline_a - baseline_b, primary RMSE


@dataclass(frozen=True)
class JointSensitivityReport:
    galaxy: str
    baseline_a: str
    baseline_b: str
    grid: JointScenarioGrid
    results: Tuple[JointScenarioResult, ...]
    n_points: int
    n_comparable: int
    n_not_comparable: int
    min_difference: Optional[float]
    max_difference: Optional[float]
    n_a_better: int
    n_b_better: int
    notes: Tuple[str, ...]


def _transform(rows: Sequence[SparcComponentRow], alpha_D: float, i_ref: float, i_new: float) -> Tuple[SparcComponentRow, ...]:
    out = []
    for r in rows:
        R, vg = scale_distance(r.R_kpc, r.Vgas_kms, alpha_D)
        _, vd = scale_distance(r.R_kpc, r.Vdisk_kms, alpha_D)
        _, vb = scale_distance(r.R_kpc, r.Vbul_kms, alpha_D)
        vo, evo = scale_inclination(r.Vobs_kms, r.e_Vobs_kms, i_ref, i_new)
        out.append(replace(r, R_kpc=R, Vgas_kms=vg, Vdisk_kms=vd, Vbul_kms=vb, Vobs_kms=vo, e_Vobs_kms=evo,
                           D_mpc=r.D_mpc * alpha_D))
    return tuple(out)


def joint_holdout_sensitivity(galaxy: str, split: HeldOutSplit, meta_row: SparcMetadataRow, grid: JointScenarioGrid,
                              *, baseline_a: str, baseline_b: str) -> JointSensitivityReport:
    if set(grid.names) != set(REQUIRED):
        raise ScopeViolationError(f"grid must declare exactly {REQUIRED} (D and i in units of the catalogue sigma)")
    D_ref, i_ref = meta_row.D_mpc, meta_row.inc_deg
    results: List[JointScenarioResult] = []
    for pt in grid.points():
        D_new = D_ref + pt["D_sigma"] * meta_row.e_D_mpc
        i_new = i_ref + pt["i_sigma"] * meta_row.e_inc_deg
        if D_new <= 0 or not (0 < i_new < 90):
            raise ScopeViolationError(f"scenario {pt} leaves the physical range (D > 0, 0 < i < 90 deg)")
        alpha_D = D_new / D_ref
        s = HeldOutSplit(train_rows=_transform(split.train_rows, alpha_D, i_ref, i_new),
                         test_rows=_transform(split.test_rows, alpha_D, i_ref, i_new))
        scores = evaluate_baselines_on_holdout(galaxy, s, pt["upsilon_d"], pt["upsilon_b"])
        by = {sc.baseline: sc for sc in scores}
        if baseline_a not in by or baseline_b not in by:
            raise ScopeViolationError(f"unknown baseline; available: {sorted(by)}")
        prim = {k: v.primary_rmse_kms for k, v in by.items()}
        a, b = prim[baseline_a], prim[baseline_b]
        diff = None if a is None or b is None else a - b
        results.append(JointScenarioResult(dict(pt), prim, {k: v.status for k, v in by.items()},
                                           {k: v.train_boundary_hit for k, v in by.items()}, diff))
    diffs = [r.loss_difference for r in results if r.loss_difference is not None]
    notes = ["scenario grid without probabilities: counts of better/worse are NOT empirical probabilities",
             "a0 not fitted (fixed MOND variant)"]
    if any(any(r.train_boundary_hits.values()) for r in results):
        notes.append("at least one training fit hit a parameter bound in some scenario (see results)")
    return JointSensitivityReport(
        galaxy, baseline_a, baseline_b, grid, tuple(results), len(results), len(diffs), len(results) - len(diffs),
        min(diffs) if diffs else None, max(diffs) if diffs else None,
        sum(1 for d in diffs if d < 0), sum(1 for d in diffs if d > 0), tuple(notes))


__all__ = ["REQUIRED", "JointScenarioResult", "JointSensitivityReport", "joint_holdout_sensitivity"]
