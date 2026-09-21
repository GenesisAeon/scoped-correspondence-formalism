"""NOAA global temperature anomaly trend pilot (Milestone 6c).

Real-data pilot built directly on a verified dataset (see
docs/real_data_provenance.md / data/real_data_manifest.json), structurally
analogous to the Cygnus and COVID pilots: calib-only fit, persistence
baseline, honest holdout RMSE comparison, no retuning after seeing the
result.

Protocol (immutable before any fit -- fixed using a round calendar
boundary, not chosen by looking at the fit quality):
  - Macro: annual global land+ocean temperature anomaly (degrees C,
    departure from the 1901-2000 average)
  - Calib window: 1880-1999 (the full 20th century as published)
  - Holdout window: 2000-2025 (the 21st century to date, fixed in advance)
  - Baseline: persistence = last calib year's (1999) anomaly held constant
  - Metric: RMSE on the holdout years
  - Free params (slope, intercept) estimated ONLY on calib via ordinary
    least squares; no holdout peeking

Trend model:
  anomaly(year) = intercept + slope * (year - year_ref)
with year_ref = first calib year (1880). This is the simplest possible
trend model (linear); it is not claimed to be the best physical model of
global temperature, and no claim is made that it holds outside the fixed
calib/holdout window.

This is ONE domain, ONE macro, ONE fixed window. No claim about the cubic
normal form in dynamics/core.py or any other Baustein without its own
separate derivation (see data/real_data_manifest.json's suggested-module
caveat for this dataset). A model_beats_baseline=False result is a VALID
complete outcome and must not trigger a retune.

Rolling-origin backtest (NONSTATIONARY_ROADMAP.md package 1, added
2026-09-21, disclosed follow-up informed by Astra's review of the single
1880-1999/2000-2025 split above -- that original split, its code, and its
result are untouched): run_noaa_rolling_origin_backtest() below applies
scoped_correspondence.validation.rolling_origin across 11 origins
(1969, 1974, ..., 2019), each with a 5-year test horizon, comparing
persistence, an expanding-window linear fit (1880 to the origin), and a
last-30-years linear fit. All three predictors are refit AT EVERY origin
using only data up to and including that origin -- no single split
choice determines the result.
"""

from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np

from scoped_correspondence.validation.rolling_origin import (
    RollingOriginReport,
    rolling_origin_backtest,
)

from scoped_correspondence.errors import ScopeViolationError
from scoped_correspondence.validation.core import ValidationReport, rmse

# --- Fixed protocol (locked BEFORE fit) -------------------------------------

DOMAIN_NAME = "noaa-global-temp-anomaly"
MACRO_NAME = "temp_anomaly_c"
MACRO_UNIT = "degrees Celsius (departure from 1901-2000 average)"
SOURCE_RELATIVE = "data/noaa_global_temp_anomaly_1880_2025.csv"
SOURCE_CITATION = (
    "NOAA NCEI Climate at a Glance: Global Time Series; "
    "data/real_data_manifest.json entry noaa_global_temp_anomaly_1880_2025"
)
CALIB_START_YEAR = 1880
CALIB_END_YEAR = 1999  # end of the 20th century -- external, round anchor
HOLDOUT_START_YEAR = 2000
HOLDOUT_END_YEAR = 2025  # last year present in the source file

DATA_PROVENANCE_NOTE = (
    "Real per-row data (see data/real_data_manifest.json entry "
    "noaa_global_temp_anomaly_1880_2025); U.S. Government work, public "
    "domain. This trend fit does NOT claim any connection to "
    "dynamics/core.py's cubic normal form or any other Baustein without "
    "its own separate derivation."
)


@dataclass(frozen=True)
class YearlyAnomaly:
    year: int
    anomaly_c: float


@dataclass(frozen=True)
class FittedLinearTrend:
    slope_c_per_year: float
    intercept_c: float
    year_ref: int
    n_calib: int
    note: str = "fitted_parameters estimated exclusively on calibration years"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "slope_c_per_year": self.slope_c_per_year,
            "intercept_c": self.intercept_c,
            "year_ref": self.year_ref,
            "n_calib": self.n_calib,
            "note": self.note,
        }


def load_annual_anomalies(path: str | Path) -> List[YearlyAnomaly]:
    """Load NOAA's annual anomaly series, skipping its own '#' comment header."""
    p = Path(path)
    lines = p.read_text(encoding="utf-8").splitlines()
    data_lines = [ln for ln in lines if ln and not ln.startswith("#")]
    points: List[YearlyAnomaly] = []
    for row in csv.DictReader(data_lines):
        points.append(YearlyAnomaly(year=int(row["Year"]), anomaly_c=float(row["Departure from Average"])))
    if not points:
        raise ScopeViolationError("load_annual_anomalies: no data rows found")
    return points


def split_by_year(
    points: List[YearlyAnomaly],
    *,
    calib_start: int = CALIB_START_YEAR,
    calib_end: int = CALIB_END_YEAR,
    holdout_start: int = HOLDOUT_START_YEAR,
    holdout_end: int = HOLDOUT_END_YEAR,
) -> Tuple[List[YearlyAnomaly], List[YearlyAnomaly]]:
    """Split by fixed calendar years; refuse any other split (anti data-snooping)."""
    if (calib_start, calib_end) != (CALIB_START_YEAR, CALIB_END_YEAR) or (
        holdout_start,
        holdout_end,
    ) != (HOLDOUT_START_YEAR, HOLDOUT_END_YEAR):
        raise ScopeViolationError(
            "split_by_year: requested years differ from the fixed protocol "
            f"(anti data-snooping). requested calib=[{calib_start},{calib_end}] "
            f"holdout=[{holdout_start},{holdout_end}]; fixed calib="
            f"[{CALIB_START_YEAR},{CALIB_END_YEAR}] holdout="
            f"[{HOLDOUT_START_YEAR},{HOLDOUT_END_YEAR}]"
        )
    if calib_end >= holdout_start:
        raise ScopeViolationError(
            "split_by_year: calib_end must be before holdout_start "
            f"(got calib_end={calib_end}, holdout_start={holdout_start})"
        )
    calib = [p for p in points if calib_start <= p.year <= calib_end]
    holdout = [p for p in points if holdout_start <= p.year <= holdout_end]
    if not calib:
        raise ScopeViolationError("split_by_year: empty calibration window")
    if not holdout:
        raise ScopeViolationError("split_by_year: empty holdout window")
    return calib, holdout


def fit_linear_trend(calib: List[YearlyAnomaly]) -> FittedLinearTrend:
    """Ordinary least squares on anomaly_c vs. years since year_ref.

    Receives ONLY calib points -- this function body never references a
    holdout window or any year outside its ``calib`` argument.
    """
    if len(calib) < 2:
        raise ScopeViolationError("fit_linear_trend: need >= 2 calib points")
    year_ref = calib[0].year
    xs = [float(p.year - year_ref) for p in calib]
    ys = [p.anomaly_c for p in calib]
    n = len(xs)
    x_mean = sum(xs) / n
    y_mean = sum(ys) / n
    sxx = sum((x - x_mean) ** 2 for x in xs)
    sxy = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys))
    if sxx <= 0.0:
        raise ScopeViolationError("fit_linear_trend: degenerate calib window (sxx<=0)")
    slope = sxy / sxx
    intercept = y_mean - slope * x_mean
    return FittedLinearTrend(
        slope_c_per_year=slope,
        intercept_c=intercept,
        year_ref=year_ref,
        n_calib=n,
    )


def predict_linear_trend(year: int, *, slope: float, intercept: float, year_ref: int) -> float:
    """anomaly(year) = intercept + slope*(year - year_ref)."""
    return intercept + slope * (year - year_ref)


def persistence_baseline_temp(calib: List[YearlyAnomaly]) -> float:
    """Last calib year's anomaly, held constant on all holdout years."""
    if not calib:
        raise ScopeViolationError("persistence_baseline_temp: empty calib")
    return calib[-1].anomaly_c


def run_noaa_temp_pilot(
    data_path: str | Path,
    *,
    domain: str = DOMAIN_NAME,
) -> Tuple[ValidationReport, FittedLinearTrend]:
    """Load -> fixed year split -> fit (calib) -> baseline -> holdout RMSE."""
    points = load_annual_anomalies(data_path)
    calib, holdout = split_by_year(points)

    fit = fit_linear_trend(calib)  # calib only -- holdout not referenced
    base = persistence_baseline_temp(calib)

    hold_obs = [p.anomaly_c for p in holdout]
    model_pred = [
        predict_linear_trend(p.year, slope=fit.slope_c_per_year, intercept=fit.intercept_c, year_ref=fit.year_ref)
        for p in holdout
    ]
    base_pred = [base] * len(holdout)

    model_rmse = rmse(hold_obs, model_pred)
    baseline_rmse = rmse(hold_obs, base_pred)
    beats = bool(model_rmse < baseline_rmse)

    report = ValidationReport(
        domain=domain,
        macro=MACRO_NAME,
        split={
            "calib_start_year": CALIB_START_YEAR,
            "calib_end_year": CALIB_END_YEAR,
            "holdout_start_year": HOLDOUT_START_YEAR,
            "holdout_end_year": HOLDOUT_END_YEAR,
            "n_calib": len(calib),
            "n_holdout": len(holdout),
            "rule": (
                "calib is the full published 20th century (1880-1999, a round "
                "calendar boundary); holdout is 2000 through the last year in "
                "the source file -- both fixed before any fit"
            ),
        },
        model_rmse_holdout=model_rmse,
        baseline_rmse_holdout=baseline_rmse,
        model_beats_baseline=beats,
        fitted_parameters=fit.to_dict(),
        source_citation=SOURCE_CITATION,
        baseline_value=base,
        n_holdout=len(holdout),
        notes=(
            DATA_PROVENANCE_NOTE,
            "False model_beats_baseline is a VALID complete result -- no retune.",
            "fit_linear_trend receives only calib points; holdout used solely for RMSE.",
            "Linear trend over 1880-1999 is a simple baseline model, not a "
            "claim about the physical mechanism of global warming.",
        ),
    )
    return report, fit


# --- Rolling-origin backtest (NONSTATIONARY_ROADMAP.md package 1) ----------

ROLLING_ORIGIN_YEARS: Tuple[int, ...] = tuple(range(1969, 2020, 5))  # 1969,1974,...,2019
ROLLING_ORIGIN_HORIZON_YEARS = 5


def _ols_intercept_slope(x: np.ndarray, y: np.ndarray) -> Tuple[float, float]:
    x_mean = float(x.mean())
    y_mean = float(y.mean())
    sxx = float(((x - x_mean) ** 2).sum())
    sxy = float(((x - x_mean) * (y - y_mean)).sum())
    slope = sxy / sxx
    intercept = y_mean - slope * x_mean
    return intercept, slope


def _persistence_predictor(calib_x: np.ndarray, calib_y: np.ndarray, test_x: np.ndarray) -> np.ndarray:
    return np.full(test_x.shape, calib_y[-1], dtype=float)


def _expanding_linear_predictor(calib_x: np.ndarray, calib_y: np.ndarray, test_x: np.ndarray) -> np.ndarray:
    origin = calib_x[-1]
    intercept, slope = _ols_intercept_slope(calib_x - origin, calib_y)
    return intercept + slope * (test_x - origin)


def _last_30_years_linear_predictor(calib_x: np.ndarray, calib_y: np.ndarray, test_x: np.ndarray) -> np.ndarray:
    origin = calib_x[-1]
    mask = calib_x >= origin - 29
    intercept, slope = _ols_intercept_slope(calib_x[mask] - origin, calib_y[mask])
    return intercept + slope * (test_x - origin)


def run_noaa_rolling_origin_backtest(data_path: str | Path) -> RollingOriginReport:
    """11 origins (1969..2019, step 5), 5-year horizon each: persistence vs.
    expanding-window linear vs. last-30-years linear, all refit at every
    origin from data up to and including that origin only.
    """
    points = load_annual_anomalies(data_path)
    years = np.array([p.year for p in points], dtype=float)
    temps = np.array([p.anomaly_c for p in points], dtype=float)
    return rolling_origin_backtest(
        years,
        temps,
        origins=ROLLING_ORIGIN_YEARS,
        horizon=ROLLING_ORIGIN_HORIZON_YEARS,
        predictors={
            "persistence": _persistence_predictor,
            "expanding": _expanding_linear_predictor,
            "last30": _last_30_years_linear_predictor,
        },
    )


__all__ = [
    "CALIB_START_YEAR",
    "CALIB_END_YEAR",
    "HOLDOUT_START_YEAR",
    "HOLDOUT_END_YEAR",
    "DATA_PROVENANCE_NOTE",
    "YearlyAnomaly",
    "FittedLinearTrend",
    "fit_linear_trend",
    "load_annual_anomalies",
    "persistence_baseline_temp",
    "predict_linear_trend",
    "run_noaa_temp_pilot",
    "split_by_year",
    "ROLLING_ORIGIN_YEARS",
    "ROLLING_ORIGIN_HORIZON_YEARS",
    "run_noaa_rolling_origin_backtest",
]
