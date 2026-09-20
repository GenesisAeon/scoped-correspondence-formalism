"""Validation / Uncertainty — Milestone 6 Cygnus pilot + Milestone 13 split conformal.

M6: calib/holdout RMSE vs persistence baseline for ``jet_pa_deg`` relaxation.
M6b: additive ``covid_pilot`` module -- OWID/JHU World COVID growth-phase
pilot on verified real per-row data (see docs/real_data_provenance.md).
M6c: additive ``noaa_temp_pilot`` module -- NOAA global temperature anomaly
trend pilot on verified real per-row data.
M6d: additive ``earthquake_pilot`` module -- USGS M>=6.0 earthquake
annual-count pilot on verified real per-row data.
None of M6b/M6c/M6d mutate ``validation/core.py``.
M13: split conformal prediction (Lei et al. 2018); additive ``conformal`` module.
Does not mutate ``validation/core.py``.
"""

from scoped_correspondence.validation.core import (
    DATA_PROVENANCE_WARNING,
    DatasetManifest,
    Epoch,
    FittedRelaxation,
    ValidationReport,
    fit_relaxation_pa,
    load_cygnus_epochs,
    persistence_baseline,
    predict_relaxation_pa,
    rmse,
    run_cygnus_pilot,
    split_epochs,
)
from scoped_correspondence.validation.covid_pilot import (
    CALIB_B_END,
    CALIB_B_START,
    CALIB_END,
    CALIB_START,
    DATA_PROVENANCE_NOTE as COVID_DATA_PROVENANCE_NOTE,
    HOLDOUT_END,
    HOLDOUT_START,
    MIN_SEGMENT_POINTS,
    PEAK_DATE_IN_PILOT_A_CALIB,
    TROUGH_DATE_IN_PILOT_A_CALIB,
    ChangepointFit,
    DailyPoint,
    FittedExponentialGrowth,
    fit_changepoint_growth,
    fit_exponential_growth,
    load_world_daily,
    persistence_baseline_covid,
    predict_exponential,
    run_covid_pilot,
    run_covid_pilot_changepoint,
    run_covid_pilot_short_window,
    split_by_date,
    split_by_date_short_window,
)
from scoped_correspondence.validation.noaa_temp_pilot import (
    CALIB_END_YEAR as TEMP_CALIB_END_YEAR,
    CALIB_START_YEAR as TEMP_CALIB_START_YEAR,
    DATA_PROVENANCE_NOTE as TEMP_DATA_PROVENANCE_NOTE,
    HOLDOUT_END_YEAR as TEMP_HOLDOUT_END_YEAR,
    HOLDOUT_START_YEAR as TEMP_HOLDOUT_START_YEAR,
    FittedLinearTrend,
    YearlyAnomaly,
    fit_linear_trend,
    load_annual_anomalies,
    persistence_baseline_temp,
    predict_linear_trend,
    run_noaa_temp_pilot,
    split_by_year as split_by_year_temp,
)
from scoped_correspondence.validation.earthquake_pilot import (
    CALIB_END_YEAR as QUAKE_CALIB_END_YEAR,
    CALIB_START_YEAR as QUAKE_CALIB_START_YEAR,
    DATA_PROVENANCE_NOTE as QUAKE_DATA_PROVENANCE_NOTE,
    HOLDOUT_END_YEAR as QUAKE_HOLDOUT_END_YEAR,
    HOLDOUT_START_YEAR as QUAKE_HOLDOUT_START_YEAR,
    FittedConstantRate,
    YearlyCount,
    fit_constant_rate,
    load_annual_counts,
    persistence_baseline_quake,
    run_earthquake_pilot,
    split_by_year as split_by_year_quake,
)
from scoped_correspondence.validation.conformal import (
    COVERAGE_MARGINAL_EXCHANGEABLE,
    SplitConformalReport,
    assert_disjoint_calib_holdout,
    calibrate_split_conformal,
    make_split_conformal_report,
    predict_interval,
)

__all__ = [
    # M6 Cygnus pilot
    "DATA_PROVENANCE_WARNING",
    "DatasetManifest",
    "Epoch",
    "FittedRelaxation",
    "ValidationReport",
    "fit_relaxation_pa",
    "load_cygnus_epochs",
    "persistence_baseline",
    "predict_relaxation_pa",
    "rmse",
    "run_cygnus_pilot",
    "split_epochs",
    # M6b covid_pilot (OWID/JHU World COVID growth-phase, verified real data)
    "CALIB_START",
    "CALIB_END",
    "HOLDOUT_START",
    "HOLDOUT_END",
    "COVID_DATA_PROVENANCE_NOTE",
    "DailyPoint",
    "FittedExponentialGrowth",
    "fit_exponential_growth",
    "load_world_daily",
    "persistence_baseline_covid",
    "predict_exponential",
    "run_covid_pilot",
    "split_by_date",
    "PEAK_DATE_IN_PILOT_A_CALIB",
    "TROUGH_DATE_IN_PILOT_A_CALIB",
    "CALIB_B_START",
    "CALIB_B_END",
    "split_by_date_short_window",
    "run_covid_pilot_short_window",
    "MIN_SEGMENT_POINTS",
    "ChangepointFit",
    "fit_changepoint_growth",
    "run_covid_pilot_changepoint",
    # M6c noaa_temp_pilot (NOAA global temperature anomaly, verified real data)
    "TEMP_CALIB_START_YEAR",
    "TEMP_CALIB_END_YEAR",
    "TEMP_HOLDOUT_START_YEAR",
    "TEMP_HOLDOUT_END_YEAR",
    "TEMP_DATA_PROVENANCE_NOTE",
    "YearlyAnomaly",
    "FittedLinearTrend",
    "fit_linear_trend",
    "load_annual_anomalies",
    "persistence_baseline_temp",
    "predict_linear_trend",
    "run_noaa_temp_pilot",
    "split_by_year_temp",
    # M6d earthquake_pilot (USGS M>=6.0 annual counts, verified real data)
    "QUAKE_CALIB_START_YEAR",
    "QUAKE_CALIB_END_YEAR",
    "QUAKE_HOLDOUT_START_YEAR",
    "QUAKE_HOLDOUT_END_YEAR",
    "QUAKE_DATA_PROVENANCE_NOTE",
    "YearlyCount",
    "FittedConstantRate",
    "fit_constant_rate",
    "load_annual_counts",
    "persistence_baseline_quake",
    "run_earthquake_pilot",
    "split_by_year_quake",
    # M13 split conformal (Lei et al. 2018)
    "COVERAGE_MARGINAL_EXCHANGEABLE",
    "SplitConformalReport",
    "assert_disjoint_calib_holdout",
    "calibrate_split_conformal",
    "make_split_conformal_report",
    "predict_interval",
]
