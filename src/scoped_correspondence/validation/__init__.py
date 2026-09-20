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
    CALIB_END,
    CALIB_START,
    DATA_PROVENANCE_NOTE as COVID_DATA_PROVENANCE_NOTE,
    HOLDOUT_END,
    HOLDOUT_START,
    DailyPoint,
    FittedExponentialGrowth,
    fit_exponential_growth,
    load_world_daily,
    persistence_baseline_covid,
    predict_exponential,
    run_covid_pilot,
    split_by_date,
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
    # M13 split conformal (Lei et al. 2018)
    "COVERAGE_MARGINAL_EXCHANGEABLE",
    "SplitConformalReport",
    "assert_disjoint_calib_holdout",
    "calibrate_split_conformal",
    "make_split_conformal_report",
    "predict_interval",
]
