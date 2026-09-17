"""Validation / Uncertainty — Milestone 6 Cygnus jet PA pilot.

First real-data pilot: calib/holdout RMSE vs persistence baseline for
``jet_pa_deg`` relaxation. Does not reuse cygnus-jet-utac σ / Γ_jet.
"""

from scoped_correspondence.validation.core import (
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

__all__ = [
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
]
