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

import datetime as dt
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

LAGGED_MEAN_WINDOW_DAYS = 7

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
    n_calib_dropped_insufficient_lookback: int
    fitted_dispersion: float
    mean_poisson_log_score_holdout: float
    mean_neg_binom_log_score_holdout: float
    neg_binom_wins: bool
    per_holdout_day: Tuple[Dict[str, Any], ...]
    retrospective_fitted_dispersion: float
    retrospective_mean_poisson_log_score_holdout: float
    retrospective_mean_neg_binom_log_score_holdout: float
    retrospective_neg_binom_wins: bool

    def to_dict(self) -> Dict[str, Any]:
        return {
            "n_calib": self.n_calib,
            "n_holdout": self.n_holdout,
            "n_calib_dropped_insufficient_lookback": self.n_calib_dropped_insufficient_lookback,
            "fitted_dispersion": self.fitted_dispersion,
            "mean_poisson_log_score_holdout": self.mean_poisson_log_score_holdout,
            "mean_neg_binom_log_score_holdout": self.mean_neg_binom_log_score_holdout,
            "neg_binom_wins": self.neg_binom_wins,
            "per_holdout_day": [dict(d) for d in self.per_holdout_day],
            "retrospective_fitted_dispersion": self.retrospective_fitted_dispersion,
            "retrospective_mean_poisson_log_score_holdout": self.retrospective_mean_poisson_log_score_holdout,
            "retrospective_mean_neg_binom_log_score_holdout": self.retrospective_mean_neg_binom_log_score_holdout,
            "retrospective_neg_binom_wins": self.retrospective_neg_binom_wins,
        }


def _load_windowed(data_path: str | Path) -> List[DailyPoint]:
    points = load_world_daily(data_path)
    windowed = [p for p in points if ANALYSIS_WINDOW_START <= p.date.isoformat() <= ANALYSIS_WINDOW_END]
    if not windowed:
        raise ScopeViolationError("_load_windowed: empty analysis window")
    return windowed


def _lagged_means(data_path: str | Path, dates: List[dt.date]) -> Tuple[Dict[dt.date, float], List[dt.date]]:
    """Forward-only reference mean: mean of ``new_cases`` over the
    ``LAGGED_MEAN_WINDOW_DAYS`` calendar days STRICTLY BEFORE each date --
    never including the date's own count. Uses the FULL raw series (not
    just the analysis window) so early-window days still have lookback.
    Returns ``(means, dropped_dates)``: dates whose full lookback window
    is not available in the raw series (necessarily only possible right
    at the start of the whole loaded series -- here, the World series
    itself begins 2020-01-22, six days before this module's analysis
    window starts, so 2020-01-28 is the one date that cannot get a full
    7-day forward-only mean) are reported as dropped rather than silently
    padded with a partial window.

    Fixed 2026-09-23 in response to
    prompts/Answers/nicht_stationäre_Treiber/SCF_Review_3e8dce3.md
    (Astra): the previous ``predicted_mean`` was ``cases_7day_avg``, OWID's
    OWN trailing 7-day average, which by construction INCLUDES the day
    being "predicted" -- Astra's concrete counterexample: bumping the
    2020-03-12 count by +700 (with weekly aggregates updated consistently)
    moves that day's own "predicted_mean" by +100, purely mechanically.
    This lagged mean uses only ``new_cases`` from days already in the
    past relative to the date being scored.
    """
    all_points = load_world_daily(data_path)
    by_date: Dict[dt.date, float] = {p.date: p.new_cases for p in all_points}
    out: Dict[dt.date, float] = {}
    dropped: List[dt.date] = []
    for d in dates:
        window_days = [d - dt.timedelta(days=k) for k in range(1, LAGGED_MEAN_WINDOW_DAYS + 1)]
        missing = [w for w in window_days if w not in by_date]
        if missing:
            dropped.append(d)
            continue
        out[d] = float(np.mean([by_date[w] for w in window_days]))
    return out, dropped


def run_covid_observation_model_comparison(data_path: str | Path) -> ObservationModelReport:
    """Poisson vs. negative-binomial log-score on REAL raw daily case counts.

    PRIMARY result uses a forward-only lagged 7-day mean (``_lagged_means``,
    computed from days strictly before the scored day) as the reference
    mean for both distributions -- non-circular: the day being scored
    never contributes to its own reference mean. Dispersion is fit on
    CALIB days only (<= CALIB_HOLDOUT_SPLIT_DATE) and evaluated on
    disjoint HOLDOUT days.

    A SEPARATE, explicitly-labeled ``retrospective_*`` result reproduces
    the module's original design (OWID's own ``cases_7day_avg``, which
    includes the scored day itself) for comparison -- kept as a
    descriptive view of dispersion around a retrospective smoothing
    value, per Astra's suggestion, NOT presented as a circularity-free
    forecast-quality result.
    """
    windowed = _load_windowed(data_path)
    calib_all = [p for p in windowed if p.date.isoformat() <= CALIB_HOLDOUT_SPLIT_DATE]
    holdout = [p for p in windowed if p.date.isoformat() > CALIB_HOLDOUT_SPLIT_DATE]
    if len(calib_all) < 10 or len(holdout) < 10:
        raise ScopeViolationError(f"run_covid_observation_model_comparison: too few calib/holdout days ({len(calib_all)}/{len(holdout)})")

    lagged, dropped_dates = _lagged_means(data_path, [p.date for p in windowed])
    dropped_in_holdout = [d for d in dropped_dates if d in {p.date for p in holdout}]
    if dropped_in_holdout:
        raise ScopeViolationError(
            f"run_covid_observation_model_comparison: {len(dropped_in_holdout)} HOLDOUT day(s) "
            f"lack a full {LAGGED_MEAN_WINDOW_DAYS}-day lookback -- widen the raw series or the "
            "analysis window, holdout days must never be dropped silently"
        )

    calib = [p for p in calib_all if p.date in lagged]
    if len(calib) < 10:
        raise ScopeViolationError(
            f"run_covid_observation_model_comparison: only {len(calib)} of {len(calib_all)} calib "
            f"days have a full {LAGGED_MEAN_WINDOW_DAYS}-day forward-only lookback"
        )

    calib_observed = [int(round(p.new_cases)) for p in calib]
    calib_means_lagged = [lagged[p.date] for p in calib]
    dispersion = fit_neg_binom_dispersion(calib_observed, calib_means_lagged)

    calib_means_retro = [p.cases_7day_avg for p in calib]
    dispersion_retro = fit_neg_binom_dispersion(calib_observed, calib_means_retro)

    per_day = []
    poisson_scores = []
    nb_scores = []
    poisson_scores_retro = []
    nb_scores_retro = []
    for p in holdout:
        observed = int(round(p.new_cases))

        mu = lagged[p.date]
        ps = poisson_log_score(observed, mu)
        ns = neg_binom_log_score(observed, mu, dispersion)
        poisson_scores.append(ps)
        nb_scores.append(ns)

        mu_retro = p.cases_7day_avg
        ps_retro = poisson_log_score(observed, mu_retro)
        ns_retro = neg_binom_log_score(observed, mu_retro, dispersion_retro)
        poisson_scores_retro.append(ps_retro)
        nb_scores_retro.append(ns_retro)

        per_day.append(
            {
                "date": p.date.isoformat(),
                "observed": observed,
                "predicted_mean": mu,
                "poisson_log_score": ps,
                "neg_binom_log_score": ns,
                "retrospective_predicted_mean": mu_retro,
                "retrospective_poisson_log_score": ps_retro,
                "retrospective_neg_binom_log_score": ns_retro,
            }
        )

    mean_poisson = float(np.mean(poisson_scores))
    mean_nb = float(np.mean(nb_scores))
    mean_poisson_retro = float(np.mean(poisson_scores_retro))
    mean_nb_retro = float(np.mean(nb_scores_retro))

    return ObservationModelReport(
        n_calib=len(calib),
        n_holdout=len(holdout),
        n_calib_dropped_insufficient_lookback=len(dropped_dates),
        fitted_dispersion=dispersion,
        mean_poisson_log_score_holdout=mean_poisson,
        mean_neg_binom_log_score_holdout=mean_nb,
        neg_binom_wins=bool(mean_nb < mean_poisson),
        per_holdout_day=tuple(per_day),
        retrospective_fitted_dispersion=dispersion_retro,
        retrospective_mean_poisson_log_score_holdout=mean_poisson_retro,
        retrospective_mean_neg_binom_log_score_holdout=mean_nb_retro,
        retrospective_neg_binom_wins=bool(mean_nb_retro < mean_poisson_retro),
    )


__all__ = [
    "SOURCE",
    "DATA_PROVENANCE_NOTE",
    "ANALYSIS_WINDOW_START",
    "ANALYSIS_WINDOW_END",
    "CALIB_HOLDOUT_SPLIT_DATE",
    "LAGGED_MEAN_WINDOW_DAYS",
    "ObservationModelReport",
    "run_covid_observation_model_comparison",
]
