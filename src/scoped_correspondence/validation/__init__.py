"""Validation / Uncertainty — Milestone 6 Cygnus pilot + Milestone 13 split conformal.

M6: calib/holdout RMSE vs persistence baseline for ``jet_pa_deg`` relaxation.
M6b: additive ``covid_pilot`` module -- OWID/JHU World COVID growth-phase
pilot on verified real per-row data (see docs/real_data_provenance.md).
Does not mutate ``validation/core.py``.
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
    # M13 split conformal (Lei et al. 2018)
    "COVERAGE_MARGINAL_EXCHANGEABLE",
    "SplitConformalReport",
    "assert_disjoint_calib_holdout",
    "calibrate_split_conformal",
    "make_split_conformal_report",
    "predict_interval",
]
