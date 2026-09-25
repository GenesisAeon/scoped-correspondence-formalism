"""Hydrology pilot: one vs. two discharge time scales on real CAMELS-DE catchments (DOMAIN_EXPANSION_ROADMAP.md Paket B3b).

Dataset-agnostic: operates on already-extracted per-catchment daily
``(precipitation_mean, discharge_mm_day)`` series (see
``data/camels_de_adapter.py`` for the CAMELS-DE selective extractor). Fits
persistence, a seasonal-climatology reference, a single linear reservoir,
and two parallel linear reservoirs (reusing ``dynamics.linear_reservoirs``
UNCHANGED) on a catchment's TRAINING period, evaluates MAE on a later,
disjoint TEST period (conditional hindcast: uses the actually observed
precipitation during the test period too, plan section 9.5 mode A -- never
claims an operational forecast).

The driving input is ``u(t) = c * P(t)`` (plan section 9.2): ``c`` is an
effective, TRAINING-ONLY-fitted runoff coefficient, not a claim of a
complete water balance with identified actual evapotranspiration.

**Correction (2026-09-25, response to
prompts/Answers/nicht_stationäre_Treiber/SCF_INTEGRATED_EXTENSION_IMPLEMENTATION_PLAN.md,
Paket C0 -- two real bugs, independently reproduced before fixing):**

**Finding A:** the persistence baseline's prediction for the FIRST test day
used that day's OWN target value (``pred_persist_test[0] = Q_test[0]``),
giving it a free, artificially perfect prediction instead of the actually
prior day's discharge. Reproduced exactly: for ``Q_test=[10,12,13]`` the
old code gave ``[10,10,12]`` (day 0 predicts itself).

**Finding B:** the reservoir state was propagated across ``train_mask |
test_mask`` -- the UNION of only the two disjoint periods -- silently
skipping every day strictly between the training and test windows (e.g.
2006-2010 between a 1991-2005 training period and a 2011-2020 test
period). The state at the end of training was fed directly into the first
simulated test day as if zero time had passed, instead of draining/filling
through the actual intervening ~1826 days. Reproduced exactly: a
2005-2011 stand-in span with 2005-only training and 2011-only test gave
672 combined days instead of the true 2352 calendar days.

Both are fixed by simulating over the FULL CONTIGUOUS calendar span from
the start of training through the end of testing (``full_span_mask``,
never a union of disjoint sub-periods) -- this correctly propagates state
through any gap years (never used for fitting or scoring) and gives the
persistence baseline access to the actual prior-day value, including the
last gap-year day immediately before the first test day.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Sequence, Tuple

import numpy as np
from scipy.optimize import minimize

from scoped_correspondence.errors import ScopeViolationError
from scoped_correspondence.dynamics.linear_reservoirs import parallel_reservoir_step, parallel_reservoir_interval_discharge


def discharge_m3s_to_mm_day(discharge_m3s: np.ndarray, area_km2: float) -> np.ndarray:
    """``q_mm_day = 86.4 * q_m3_s / area_km2`` (plan section 9.4)."""
    if area_km2 <= 0.0:
        raise ScopeViolationError(f"area_km2 must be > 0; got {area_km2!r}")
    return 86.4 * discharge_m3s / area_km2


def _forward_fill(x: np.ndarray) -> np.ndarray:
    """Forward-fill NaNs (used only for the DRIVING precipitation input to keep the
    reservoir simulation defined day-to-day; NaN target discharge days are excluded
    from scoring via an explicit mask, never imputed)."""
    x = x.copy()
    nan_mask = np.isnan(x)
    if not nan_mask.any():
        return x
    idx = np.where(~nan_mask, np.arange(len(x)), 0)
    np.maximum.accumulate(idx, out=idx)
    return x[idx]


def _simulate_1res(P: np.ndarray, c: float, k: float) -> np.ndarray:
    n = len(P)
    S = 0.0
    q = np.empty(n)
    for t in range(n):
        u = c * P[t]
        q[t] = parallel_reservoir_interval_discharge([S], u, [1.0], [k], 1.0)
        S = parallel_reservoir_step([S], u, [1.0], [k], 1.0)[0]
    return q


def _simulate_2res(P: np.ndarray, c: float, k1: float, k2: float, alpha1: float) -> np.ndarray:
    n = len(P)
    S = [0.0, 0.0]
    alphas, ks = [alpha1, 1.0 - alpha1], [k1, k2]
    q = np.empty(n)
    for t in range(n):
        u = c * P[t]
        q[t] = parallel_reservoir_interval_discharge(S, u, alphas, ks, 1.0)
        S = list(parallel_reservoir_step(S, u, alphas, ks, 1.0))
    return q


def _fit_1res(P_train: np.ndarray, Q_train: np.ndarray, n_restarts_seeds=((0.3, 0.1), (0.5, 0.3), (0.7, 0.05))):
    mask = ~np.isnan(Q_train)

    def loss(x):
        c, k = x
        if not (0.0 < c <= 1.0 and 1e-4 < k < 5.0):
            return 1e6
        pred = _simulate_1res(P_train, c, k)
        return float(np.mean((pred[mask] - Q_train[mask]) ** 2))

    best = None
    for c0, k0 in n_restarts_seeds:
        res = minimize(loss, [c0, k0], method="Nelder-Mead", options={"maxiter": 200})
        if best is None or res.fun < best.fun:
            best = res
    return {"c": float(best.x[0]), "k": float(best.x[1])}, float(best.fun)


def _fit_2res(P_train: np.ndarray, Q_train: np.ndarray,
              n_restarts_seeds=((0.3, 0.02, 0.3, 0.5), (0.5, 0.05, 0.5, 0.3))):
    mask = ~np.isnan(Q_train)

    def loss(x):
        c, k_slow, dk, alpha1 = x
        k1, k2 = k_slow, k_slow + dk
        if not (0.0 < c <= 1.0 and 1e-4 < k1 < 5.0 and dk > 1e-4 and k2 < 5.0 and 0.0 <= alpha1 <= 1.0):
            return 1e6
        pred = _simulate_2res(P_train, c, k1, k2, alpha1)
        return float(np.mean((pred[mask] - Q_train[mask]) ** 2))

    best = None
    for c0, ks0, dk0, a0 in n_restarts_seeds:
        res = minimize(loss, [c0, ks0, dk0, a0], method="Nelder-Mead", options={"maxiter": 300})
        if best is None or res.fun < best.fun:
            best = res
    c, k_slow, dk, alpha1 = best.x
    k1, k2 = k_slow, k_slow + dk
    # report with k_fast >= k_slow convention (label-swap identifiability, B3a)
    k_fast, k_slow_out, alpha_fast = (k2, k1, 1.0 - alpha1) if k2 > k1 else (k1, k2, alpha1)
    return {"c": float(c), "k_fast": float(k_fast), "k_slow": float(k_slow_out), "alpha_fast": float(alpha_fast)}, float(best.fun)


@dataclass(frozen=True)
class CatchmentHydroResult:
    gauge_id: str
    area_km2: float
    n_train_days: int
    n_test_days: int
    fit_1res: Dict[str, float]
    fit_2res: Dict[str, float]
    mae_test: Dict[str, float]
    mae_low_flow_test: Dict[str, Optional[float]]
    q10_train_mm_day: float
    n_low_flow_test_days: int
    n_scored: Dict[str, int]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "gauge_id": self.gauge_id, "area_km2": self.area_km2,
            "n_train_days": self.n_train_days, "n_test_days": self.n_test_days,
            "fit_1res": self.fit_1res, "fit_2res": self.fit_2res,
            "mae_test": self.mae_test, "mae_low_flow_test": self.mae_low_flow_test,
            "q10_train_mm_day": self.q10_train_mm_day, "n_low_flow_test_days": self.n_low_flow_test_days,
            "n_scored": self.n_scored,
        }


def run_catchment_hydro_pilot(
    gauge_id: str, dates: Sequence[str], precip: np.ndarray, discharge_m3s: np.ndarray, area_km2: float,
    train_years: Tuple[int, int], test_years: Tuple[int, int],
) -> CatchmentHydroResult:
    """Conditional hindcast (plan section 9.5, mode A): fit persistence/seasonal/
    1-reservoir/2-reservoir on ``train_years``, evaluate MAE on the disjoint,
    LATER ``test_years`` using the actually observed precipitation throughout
    (never claims an operational forecast, plan section 9.5's explicit caveat).
    """
    years = np.array([int(d[:4]) for d in dates])
    train_mask = (years >= train_years[0]) & (years <= train_years[1])
    test_mask = (years >= test_years[0]) & (years <= test_years[1])
    if train_mask.sum() < 100 or test_mask.sum() < 100:
        raise ScopeViolationError(f"insufficient train/test coverage for {gauge_id}")
    if train_years[1] >= test_years[0]:
        raise ScopeViolationError("train_years must end strictly before test_years starts")

    Q = discharge_m3s_to_mm_day(discharge_m3s, area_km2)
    P_filled = _forward_fill(precip)

    P_train, Q_train = P_filled[train_mask], Q[train_mask]
    fit1, _ = _fit_1res(P_train, Q_train)
    fit2, _ = _fit_2res(P_train, Q_train)

    # Finding B fix: simulate over the FULL CONTIGUOUS span from the start of training
    # through the end of testing -- not just the union of the two disjoint periods --
    # so any gap years (e.g. 2006-2010 between a 1991-2005/2011-2020 split) are actually
    # propagated through the reservoir state instead of silently skipped.
    full_span_mask = (years >= train_years[0]) & (years <= test_years[1])
    P_full, Q_full = P_filled[full_span_mask], Q[full_span_mask]
    train_in_full = train_mask[full_span_mask]
    test_in_full = test_mask[full_span_mask]

    pred1_full = _simulate_1res(P_full, fit1["c"], fit1["k"])
    pred2_full = _simulate_2res(P_full, fit2["c"], fit2["k_fast"], fit2["k_slow"], fit2["alpha_fast"])
    pred1_test, pred2_test = pred1_full[test_in_full], pred2_full[test_in_full]

    Q_test = Q[test_mask]
    dates_test = np.asarray(dates)[test_mask]
    valid_test = ~np.isnan(Q_test)

    # Finding A fix: shift the FULL span's discharge series by one day (using the actual
    # prior day's observed value, including the last gap-year day for the first test day),
    # not the test period's own first value predicting itself. A day with no predecessor
    # anywhere in the loaded data (only possible at the very start of the full span, i.e.
    # if that ever fell inside the test period) is marked NaN, never silently substituted.
    pred_persist_full = np.concatenate([[np.nan], Q_full[:-1]])
    pred_persist_test = pred_persist_full[test_in_full]
    doy_train = np.array([d[5:10] for d in np.asarray(dates)[train_mask]])
    doy_test = np.array([d[5:10] for d in dates_test])
    doy_mean: Dict[str, float] = {}
    for d, q in zip(doy_train, Q_train):
        if not np.isnan(q):
            doy_mean.setdefault(d, []).append(q)  # type: ignore[arg-type]
    doy_mean = {d: float(np.mean(v)) for d, v in doy_mean.items()}  # type: ignore[arg-type]
    global_mean_train = float(np.nanmean(Q_train))
    pred_seasonal_test = np.array([doy_mean.get(d, global_mean_train) for d in doy_test])

    m = valid_test
    # persistence's OWN source day (t-1, or Q_test[0] itself for the first test day) can be
    # missing even on a day where the TARGET Q_test[i] is present (an isolated single-day
    # gap in a decades-long daily series) -- that must not silently poison the whole metric
    # via a stray NaN propagating through np.mean. Each baseline is scored over ITS OWN
    # valid subset, with the sample count reported explicitly rather than hidden.
    m_persist = m & ~np.isnan(pred_persist_test)

    def masked_mae(pred: np.ndarray, mask: np.ndarray) -> Tuple[float, int]:
        n_valid = int(mask.sum())
        if n_valid == 0:
            raise ScopeViolationError("no valid days to score this baseline against")
        return float(np.mean(np.abs(pred[mask] - Q_test[mask]))), n_valid

    mae_persist, n_persist = masked_mae(pred_persist_test, m_persist)
    mae_seasonal, n_seasonal = masked_mae(pred_seasonal_test, m)
    mae_1res, n_1res = masked_mae(pred1_test, m)
    mae_2res, n_2res = masked_mae(pred2_test, m)
    mae_test = {"persistence": mae_persist, "seasonal": mae_seasonal, "one_reservoir": mae_1res, "two_reservoir": mae_2res}
    n_scored = {"persistence": n_persist, "seasonal": n_seasonal, "one_reservoir": n_1res, "two_reservoir": n_2res}

    q10_train = float(np.nanpercentile(Q_train, 10))
    low_mask = m & (Q_test <= q10_train)
    low_mask_persist = m_persist & (Q_test <= q10_train)
    n_low = int(low_mask.sum())

    def low_mae(pred: np.ndarray, mask: np.ndarray) -> Optional[float]:
        return float(np.mean(np.abs(pred[mask] - Q_test[mask]))) if mask.sum() > 0 else None

    mae_low = {
        "persistence": low_mae(pred_persist_test, low_mask_persist), "seasonal": low_mae(pred_seasonal_test, low_mask),
        "one_reservoir": low_mae(pred1_test, low_mask), "two_reservoir": low_mae(pred2_test, low_mask),
    }

    return CatchmentHydroResult(
        gauge_id=gauge_id, area_km2=area_km2,
        n_train_days=int((~np.isnan(Q_train)).sum()), n_test_days=int(m.sum()),
        fit_1res=fit1, fit_2res=fit2, mae_test=mae_test, mae_low_flow_test=mae_low,
        q10_train_mm_day=q10_train, n_low_flow_test_days=n_low, n_scored=n_scored,
    )


__all__ = ["discharge_m3s_to_mm_day", "CatchmentHydroResult", "run_catchment_hydro_pilot"]
