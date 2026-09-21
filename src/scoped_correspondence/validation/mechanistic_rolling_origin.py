"""Common temporal forecast evaluation for the three mechanistic models (Milestone 48).

MECHANISTIC_VALIDATION_ROADMAP.md package 2, response to
prompts/Answers/nicht_stationäre_Treiber/SCF_Review_f8e249f.md (Astra,
2026-09-21): "jedes neue Modell wurde bisher gegen sein EIGENES
Trainingsfenster bewertet ... nicht gegen dieselben Zielgrößen, Ursprünge
und Horizonte wie die anderen." ``validation/rolling_origin.py``
(NONSTATIONARY_ROADMAP.md package 1) already exists generically; this
module is its FIRST application to ``covid_renewal.py``, ``energy_balance.py``,
and ``etas.py`` -- each adapted to its own natural forecasting target,
sharing the SAME generic harness and, where the domain already has an
established protocol (NOAA rolling-origin years/horizon; the earthquake
pilot's calib/holdout split), the exact SAME origins/baselines for a fair
comparison.

Three domains, three different adaptations (a single interface cannot
paper over genuinely different data-generating processes):

- ENERGY BALANCE: same annual-series shape as ``noaa_temp_pilot.py`` --
  reuses its EXACT origins (1969..2019, step 5) and horizon (5 years) via
  the SAME ``rolling_origin_backtest`` call, adding one new predictor
  (refit the two-layer EBM on calib-only years, project forward through
  REAL, already-known CO2 forcing -- a "given future forcing is known"
  forecast, not a forecast of the forcing itself).
- ETAS EARTHQUAKES: a point process, not a continuous series -- reuses
  ``earthquake_pilot.py``'s EXACT calib/holdout split (2000-2019/2020-2025)
  and its existing persistence/constant-rate baselines, adding the ETAS
  model's first-order expected count per holdout year (see
  ``etas_expected_count_first_order``'s own caveat: NOT a full
  branching-cascade expectation, and the branching ratio here is
  near/above 1 -- explicitly flagged, not hidden).
- COVID RENEWAL: forecasts near-term case counts via the constant-R
  renewal projection (``project_incidence_constant_r``) against
  persistence and a simple exponential extrapolation, using several
  origins within the same March-2020 window already used by Pilot A/B/C
  and ``covid_renewal.py``'s own R_t estimate.

Model selection (bounds, initial guesses, generation-interval parameters)
is fixed BEFORE this module runs, by the already-shipped fitting
functions -- no parameter here was chosen by looking at rolling-origin
performance.
"""

from __future__ import annotations

import csv
import datetime as dt
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

from scoped_correspondence.errors import ScopeViolationError
from scoped_correspondence.validation.rolling_origin import (
    HorizonStepReport,
    RollingOriginReport,
    error_by_horizon_step,
    rolling_origin_backtest,
)
from scoped_correspondence.validation.noaa_temp_pilot import (
    ROLLING_ORIGIN_HORIZON_YEARS,
    ROLLING_ORIGIN_YEARS,
    _expanding_linear_predictor,
    _last_30_years_linear_predictor,
    _persistence_predictor,
)
from scoped_correspondence.validation.earthquake_pilot import (
    CALIB_END_YEAR as QUAKE_CALIB_END_YEAR,
    CALIB_START_YEAR as QUAKE_CALIB_START_YEAR,
    HOLDOUT_END_YEAR as QUAKE_HOLDOUT_END_YEAR,
    HOLDOUT_START_YEAR as QUAKE_HOLDOUT_START_YEAR,
    fit_constant_rate,
    load_annual_counts,
    persistence_baseline_quake,
    split_by_year,
)
from scoped_correspondence.dynamics.energy_balance import (
    _load_overlap_series,
    fit_energy_balance_model_from_series,
    integrate_energy_balance_trajectory,
)
from scoped_correspondence.dynamics.etas import (
    etas_branching_ratio,
    etas_expected_count_first_order,
    fit_etas_model_from_series,
    load_catalog as etas_load_catalog,
)
from scoped_correspondence.validation.covid_pilot import load_world_daily
from scoped_correspondence.validation.covid_renewal import (
    discretized_generation_interval,
    instantaneous_r,
    project_incidence_constant_r,
)

SOURCE = (
    "This module applies validation.rolling_origin (already-verified generic "
    "harness) to dynamics.energy_balance, dynamics.etas, and "
    "validation.covid_renewal for the first time, per Astra's 2026-09-21 "
    "review of commit f8e249f (SCF_Review_f8e249f.md)."
)


# --- Energy balance ----------------------------------------------------------


def _energy_balance_mechanistic_predictor_factory(years_all: List[int], F_vals_all: np.ndarray):
    """Caches the calib-only refit by origin (``calib_x``'s content) --
    ``error_by_horizon_step`` calls this predictor once per (origin, step)
    pair, and refitting from scratch on every call would needlessly repeat
    the SAME fit up to ``max_horizon_steps`` times per origin.
    """
    year_to_idx = {y: i for i, y in enumerate(years_all)}
    fit_cache: Dict[Tuple[int, ...], object] = {}

    def predictor(calib_x: np.ndarray, calib_y: np.ndarray, test_x: np.ndarray) -> np.ndarray:
        calib_years = [int(y) for y in calib_x]
        test_years = [int(y) for y in test_x]
        cache_key = tuple(calib_years)
        fit = fit_cache.get(cache_key)
        if fit is None:
            F_calib = F_vals_all[[year_to_idx[y] for y in calib_years]]
            fit = fit_energy_balance_model_from_series(calib_years, calib_y, F_calib)
            fit_cache[cache_key] = fit
        combined_years = list(range(calib_years[0], test_years[-1] + 1))
        F_combined = F_vals_all[[year_to_idx[y] for y in combined_years]]
        pred_combined = integrate_energy_balance_trajectory(F_combined, fit.params)
        pred_by_year = dict(zip(combined_years, pred_combined))
        return np.array([pred_by_year[y] for y in test_years])

    return predictor


def run_energy_balance_rolling_origin_analysis(
    co2_path: str | Path, temp_path: str | Path
) -> Tuple[RollingOriginReport, HorizonStepReport]:
    """Same 11 origins (1969..2019, step 5) and 5-year horizon as
    ``noaa_temp_pilot.run_noaa_rolling_origin_backtest``, with a 4th
    predictor added: the two-layer energy balance model, refit on
    calib-only years and projected forward through REAL (already-observed)
    CO2 forcing. Returns BOTH the pooled report and a per-lead-year
    breakdown (Astra's "Fehler getrennt nach Horizont" ask) from a SINGLE
    shared predictor cache -- the pooled and per-step analyses share the
    exact same 11 calib-only refits rather than repeating them (each
    energy-balance refit, with its solve_ivp cross-check, is not free).
    """
    years_all, Tobs_all, F_vals_all = _load_overlap_series(co2_path, temp_path)
    years_arr = np.array(years_all, dtype=float)
    shared_predictor = _energy_balance_mechanistic_predictor_factory(years_all, F_vals_all)

    pooled = rolling_origin_backtest(
        years_arr,
        Tobs_all,
        origins=ROLLING_ORIGIN_YEARS,
        horizon=ROLLING_ORIGIN_HORIZON_YEARS,
        predictors={
            "persistence": _persistence_predictor,
            "expanding": _expanding_linear_predictor,
            "last30": _last_30_years_linear_predictor,
            "energy_balance_mechanistic": shared_predictor,
        },
    )
    by_horizon = error_by_horizon_step(
        years_arr,
        Tobs_all,
        origins=ROLLING_ORIGIN_YEARS,
        max_horizon_steps=ROLLING_ORIGIN_HORIZON_YEARS,
        step_size=1.0,
        predictors={
            "persistence": _persistence_predictor,
            "last30": _last_30_years_linear_predictor,
            "energy_balance_mechanistic": shared_predictor,
        },
    )
    return pooled, by_horizon


# --- ETAS earthquakes ---------------------------------------------------------


def _etas_catalog_t0(catalog_path: str | Path) -> dt.datetime:
    p = Path(catalog_path)
    with p.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    rows_sorted = sorted(rows, key=lambda r: r["time"])
    return dt.datetime.fromisoformat(rows_sorted[0]["time"].replace("Z", "+00:00"))


def _day_offset(t0: dt.datetime, calendar_date_iso: str) -> float:
    d = dt.datetime.fromisoformat(calendar_date_iso).replace(tzinfo=dt.timezone.utc)
    return (d - t0).total_seconds() / 86400.0


def run_etas_forecast_check(catalog_path: str | Path, *, m0: float = 6.0) -> Dict[str, object]:
    """ETAS vs. the earthquake_pilot.py baselines, on the EXACT SAME calib/holdout split.

    Fits ETAS on calib-only events (calendar years 2000-2019, using the
    explicit t_end=2020-01-01 observation window from
    ``fit_etas_model_from_series`` -- MECHANISTIC_VALIDATION_ROADMAP.md
    package 1), then computes the FIRST-ORDER expected count
    (``etas_expected_count_first_order``) for each holdout year
    (2020-2025) and compares its RMSE against the already-established
    persistence and constant-rate baselines.

    HONEST CAVEAT, surfaced not hidden: if the calib-fitted branching
    ratio is >= 1 (as already found for the full catalog in package 1),
    the first-order expected count EXCLUDES a potentially large
    offspring-of-offspring contribution and should not be read as a
    calibrated point forecast -- only as a lower-bound diagnostic.
    """
    t0 = _etas_catalog_t0(catalog_path)
    t_calib_end = _day_offset(t0, "2020-01-01T00:00:00")
    t_holdout_end = _day_offset(t0, "2026-01-01T00:00:00")

    times, mags = etas_load_catalog(catalog_path, m0=m0)
    calib_mask = times < t_calib_end
    times_calib = times[calib_mask]
    mags_calib = mags[calib_mask]

    fit = fit_etas_model_from_series(times_calib, mags_calib, m0=m0, t_end=t_calib_end)
    branching = etas_branching_ratio(fit.params.K, fit.params.c, fit.params.p, fit.params.alpha, mags_calib, m0)
    near_or_above_critical = bool(branching >= 1.0)

    counts = load_annual_counts(catalog_path)
    calib_counts, holdout_counts = split_by_year(
        counts,
        calib_start=QUAKE_CALIB_START_YEAR,
        calib_end=QUAKE_CALIB_END_YEAR,
        holdout_start=QUAKE_HOLDOUT_START_YEAR,
        holdout_end=QUAKE_HOLDOUT_END_YEAR,
    )
    persistence_pred = persistence_baseline_quake(calib_counts)
    constant_rate = fit_constant_rate(calib_counts).mean_annual_count

    etas_preds = []
    for yc in holdout_counts:
        window_start = _day_offset(t0, f"{yc.year}-01-01T00:00:00")
        window_end = _day_offset(t0, f"{yc.year + 1}-01-01T00:00:00")
        etas_preds.append(etas_expected_count_first_order(fit.params, times_calib, mags_calib, m0, window_start, window_end))

    observed = np.array([yc.count for yc in holdout_counts], dtype=float)
    etas_preds_arr = np.array(etas_preds, dtype=float)
    persistence_arr = np.full(len(holdout_counts), persistence_pred)
    constant_rate_arr = np.full(len(holdout_counts), constant_rate)

    def rmse(a: np.ndarray, b: np.ndarray) -> float:
        return float(np.sqrt(np.mean((a - b) ** 2)))

    return {
        "holdout_years": [yc.year for yc in holdout_counts],
        "observed_counts": observed.tolist(),
        "etas_first_order_predicted": etas_preds_arr.tolist(),
        "persistence_predicted": persistence_arr.tolist(),
        "constant_rate_predicted": constant_rate_arr.tolist(),
        "rmse_etas_first_order": rmse(observed, etas_preds_arr),
        "rmse_persistence": rmse(observed, persistence_arr),
        "rmse_constant_rate": rmse(observed, constant_rate_arr),
        "calib_branching_ratio": branching,
        "branching_ratio_near_or_above_critical": near_or_above_critical,
        "caveat": (
            "branching_ratio >= 1: the first-order expected count excludes a "
            "potentially large offspring-of-offspring contribution and is a "
            "lower-bound diagnostic, NOT a calibrated point forecast."
            if near_or_above_critical
            else "branching_ratio < 1: the first-order approximation is a "
            "genuine (if still approximate) lower bound on the true expected count."
        ),
    }


# --- COVID renewal -------------------------------------------------------------

COVID_RENEWAL_ORIGINS_DAY_INDEX: Tuple[int, ...] = (25, 30, 35, 40, 45, 50)
COVID_RENEWAL_HORIZON_DAYS = 7


def _covid_daily_series(data_path: str | Path, *, window_start: str = "2020-01-22", window_end: str = "2020-03-25"):
    points = load_world_daily(data_path)
    windowed = [p for p in points if window_start <= p.date.isoformat() <= window_end]
    if not windowed:
        raise ScopeViolationError("_covid_daily_series: empty window")
    dates = [p.date for p in windowed]
    if any((b - a).days != 1 for a, b in zip(dates, dates[1:])):
        raise ScopeViolationError("_covid_daily_series: window must have no missing calendar days")
    day_index = np.arange(len(windowed), dtype=float)
    incidence = np.array([p.cases_7day_avg for p in windowed], dtype=float)
    return day_index, incidence, tuple(d.isoformat() for d in dates)


def _covid_persistence_predictor(calib_x: np.ndarray, calib_y: np.ndarray, test_x: np.ndarray) -> np.ndarray:
    return np.full(test_x.shape, calib_y[-1], dtype=float)


def _covid_exponential_extrapolation_predictor(calib_x: np.ndarray, calib_y: np.ndarray, test_x: np.ndarray) -> np.ndarray:
    """Simple exponential extrapolation (log-linear OLS on the last 14 calib days) -- the
    same style of baseline as covid_pilot.py's Pilot A/B fits, kept independent of them.
    """
    n_recent = min(14, len(calib_x))
    x_recent = calib_x[-n_recent:]
    y_recent = calib_y[-n_recent:]
    if np.any(y_recent <= 0):
        raise ScopeViolationError("_covid_exponential_extrapolation_predictor: non-positive incidence in log-fit window")
    log_y = np.log(y_recent)
    origin = x_recent[-1]
    x_centered = x_recent - origin
    x_mean = x_centered.mean()
    slope = float(((x_centered - x_mean) * (log_y - log_y.mean())).sum() / ((x_centered - x_mean) ** 2).sum())
    intercept = float(log_y.mean() - slope * x_mean)
    return np.exp(intercept + slope * (test_x - origin))


def _covid_renewal_predictor_factory():
    weights = discretized_generation_interval()

    def predictor(calib_x: np.ndarray, calib_y: np.ndarray, test_x: np.ndarray) -> np.ndarray:
        r_t = instantaneous_r(calib_y, weights)
        valid = r_t[np.isfinite(r_t)]
        if len(valid) == 0:
            raise ScopeViolationError("_covid_renewal_predictor: no valid R_t estimate in calib window")
        r_last = float(valid[-1])
        n_steps = int(round(test_x[-1] - calib_x[-1]))
        projected = project_incidence_constant_r(calib_y, weights, r_last, n_steps)
        origin_idx = int(round(calib_x[-1]))
        offsets = np.array([int(round(tx)) - origin_idx for tx in test_x])
        return projected[offsets - 1]

    return predictor


def run_covid_renewal_rolling_origin_backtest(data_path: str | Path) -> RollingOriginReport:
    """Multiple origins within the same March-2020 window as covid_renewal.py's
    own analysis window and Pilot A/B/C's fitting window; 7-day horizon.
    """
    day_index, incidence, _dates = _covid_daily_series(data_path)
    return rolling_origin_backtest(
        day_index,
        incidence,
        origins=[float(o) for o in COVID_RENEWAL_ORIGINS_DAY_INDEX],
        horizon=float(COVID_RENEWAL_HORIZON_DAYS),
        predictors={
            "persistence": _covid_persistence_predictor,
            "exponential_extrapolation": _covid_exponential_extrapolation_predictor,
            "renewal_constant_R": _covid_renewal_predictor_factory(),
        },
    )


__all__ = [
    "SOURCE",
    "run_energy_balance_rolling_origin_analysis",
    "run_etas_forecast_check",
    "run_covid_renewal_rolling_origin_backtest",
    "COVID_RENEWAL_ORIGINS_DAY_INDEX",
    "COVID_RENEWAL_HORIZON_DAYS",
]
