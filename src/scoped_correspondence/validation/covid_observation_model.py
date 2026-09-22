"""COVID count observation model: testing overdispersion, not assuming it (Milestone 52).

MECHANISTIC_VALIDATION_ROADMAP.md package 5, response to
prompts/Answers/nicht_stationäre_Treiber/SCF_Review_f8e249f.md (Astra,
2026-09-21): "latente Dynamik [...] Messprozess [...] explizit trennen
[...] Negativ-Binomial-Beobachtungsmodell für Überdispersion (Notwendigkeit
über Residuen/Prognosescores prüfen, nicht a priori annehmen)."

Uses the SAME real World COVID series and analysis window as
`covid_renewal.py` (2020-01-28 to 2020-03-25), but the RAW daily
`new_cases` column (not `cases_7day_avg`) as the observed count -- Astra's
explicit ask: "Echte tägliche Rohzahlen statt überlappender
Siebentagesmittel als Zählmodell-Eingabe."

Design (deliberately simple, explicitly scoped): treat the already-smoothed
`cases_7day_avg` as a given reference mean mu_t (NOT independently modeled
here -- a full latent-state/observation-process separation, e.g. a
state-space model estimating the true latent incidence, is a larger
undertaking left for future work), and ask whether the RAW day-to-day
count varies around that mean MORE than a Poisson model would predict.
Dispersion is fit on a CALIB half of the window and evaluated (Poisson vs.
negative-binomial log-score) on a HOLDOUT half -- anti-leak discipline
matching this repository's other calib/holdout pilots, so the comparison
is not circular.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np

from scoped_correspondence.errors import ScopeViolationError
from scoped_correspondence.validation.covid_pilot import DailyPoint, load_world_daily
from scoped_correspondence.validation.scoring_rules import (
    SOURCE as SCORING_SOURCE,
    fit_neg_binom_dispersion,
    neg_binom_log_score,
    poisson_log_score,
)

SOURCE = SCORING_SOURCE

ANALYSIS_WINDOW_START = "2020-01-28"
ANALYSIS_WINDOW_END = "2020-03-25"
# Split rule fixed BEFORE fitting, independent of any data feature: the
# window in half by day count (29/29 days for the 58-day window above).
CALIB_HOLDOUT_SPLIT_DATE = "2020-02-25"  # last calib day (inclusive)

DATA_PROVENANCE_NOTE = (
    "Real per-row data (see data/real_data_manifest.json entry "
    "owid_covid_world_daily_2020_2023); attribution required under CC BY "
    "4.0: 'Data: Our World in Data / Johns Hopkins University CSSE "
    "COVID-19 Data Repository.' Raw new_cases (NOT cases_7day_avg) is the "
    "observed count here -- the whole point of this module."
)


@dataclass(frozen=True)
class ObservationModelReport:
    n_calib: int
    n_holdout: int
    fitted_dispersion: float
    mean_poisson_log_score_holdout: float
    mean_neg_binom_log_score_holdout: float
    neg_binom_wins: bool
    per_holdout_day: Tuple[Dict[str, Any], ...]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "n_calib": self.n_calib,
            "n_holdout": self.n_holdout,
            "fitted_dispersion": self.fitted_dispersion,
            "mean_poisson_log_score_holdout": self.mean_poisson_log_score_holdout,
            "mean_neg_binom_log_score_holdout": self.mean_neg_binom_log_score_holdout,
            "neg_binom_wins": self.neg_binom_wins,
            "per_holdout_day": [dict(d) for d in self.per_holdout_day],
        }


def _load_windowed(data_path: str | Path) -> List[DailyPoint]:
    points = load_world_daily(data_path)
    windowed = [p for p in points if ANALYSIS_WINDOW_START <= p.date.isoformat() <= ANALYSIS_WINDOW_END]
    if not windowed:
        raise ScopeViolationError("_load_windowed: empty analysis window")
    return windowed


def run_covid_observation_model_comparison(data_path: str | Path) -> ObservationModelReport:
    """Poisson vs. negative-binomial log-score on REAL raw daily case counts.

    Dispersion is fit on CALIB days only (<= CALIB_HOLDOUT_SPLIT_DATE) and
    evaluated on HOLDOUT days only -- the mean itself (cases_7day_avg) is
    taken as given for both distributions, isolating the question "does
    allowing overdispersion around this mean improve the predictive
    score" from any question about the mean itself.
    """
    windowed = _load_windowed(data_path)
    calib = [p for p in windowed if p.date.isoformat() <= CALIB_HOLDOUT_SPLIT_DATE]
    holdout = [p for p in windowed if p.date.isoformat() > CALIB_HOLDOUT_SPLIT_DATE]
    if len(calib) < 10 or len(holdout) < 10:
        raise ScopeViolationError(f"run_covid_observation_model_comparison: too few calib/holdout days ({len(calib)}/{len(holdout)})")

    calib_observed = [int(round(p.new_cases)) for p in calib]
    calib_means = [p.cases_7day_avg for p in calib]
    dispersion = fit_neg_binom_dispersion(calib_observed, calib_means)

    per_day = []
    poisson_scores = []
    nb_scores = []
    for p in holdout:
        observed = int(round(p.new_cases))
        mu = p.cases_7day_avg
        ps = poisson_log_score(observed, mu)
        ns = neg_binom_log_score(observed, mu, dispersion)
        poisson_scores.append(ps)
        nb_scores.append(ns)
        per_day.append({"date": p.date.isoformat(), "observed": observed, "predicted_mean": mu, "poisson_log_score": ps, "neg_binom_log_score": ns})

    mean_poisson = float(np.mean(poisson_scores))
    mean_nb = float(np.mean(nb_scores))

    return ObservationModelReport(
        n_calib=len(calib),
        n_holdout=len(holdout),
        fitted_dispersion=dispersion,
        mean_poisson_log_score_holdout=mean_poisson,
        mean_neg_binom_log_score_holdout=mean_nb,
        neg_binom_wins=bool(mean_nb < mean_poisson),
        per_holdout_day=tuple(per_day),
    )


__all__ = [
    "SOURCE",
    "DATA_PROVENANCE_NOTE",
    "ANALYSIS_WINDOW_START",
    "ANALYSIS_WINDOW_END",
    "CALIB_HOLDOUT_SPLIT_DATE",
    "ObservationModelReport",
    "run_covid_observation_model_comparison",
]
