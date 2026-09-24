"""COVID: separating latent renewal dynamics from the reporting/observation process (Milestone 56).

CAPABILITY_EXPANSION_ROADMAP.md Priority 2, response to Astra's 2026-09-24
capability assessment: "Beim COVID-Piloten wäre die natürliche Erweiterung
ein latentes Infektionsgeschehen mit Meldeverzug, Wochentagseffekten und
Überdispersion... Man kann [dann] unterscheiden, ob ein Modell die Dynamik
verfehlt oder ob der Beobachtungsprozess die Daten verzerrt."

SCOPE (explicit, not silently narrowed): a genuine reporting-DELAY model
needs a report-date x episode-date matrix (a "reporting triangle"); the
OWID/JHU daily series used throughout this repository is a single already-
finalized count per calendar day, with no such matrix available. Reporting
delay is therefore NOT modeled here — only the two components the
available data can actually support are added on top of the existing
renewal-equation dynamics (`covid_renewal.py`, unchanged): a WEEKDAY
reporting multiplier and NEGATIVE-BINOMIAL overdispersion (both fit on a
calib window strictly before any evaluated forecast origin, tested for
predictive benefit rather than assumed).

This directly answers Astra's request to compare OLD vs. NEW variants "auf
denselben festgelegten Prognoseursprüngen" (COVID_RENEWAL_ORIGINS_DAY_INDEX
/ COVID_RENEWAL_HORIZON_DAYS, unchanged from mechanistic_rolling_origin.py):
the DYNAMICS layer (renewal equation, `_covid_renewal_predictor_factory`)
is IDENTICAL between OLD and NEW -- only the observation layer changes,
isolating exactly what a better measurement model buys on top of the same
mechanistic point forecast:

- OLD: the renewal-equation point forecast (of the SMOOTHED
  `cases_7day_avg` incidence proxy) is used directly as a Poisson mean for
  the RAW daily count on the target calendar date.
- NEW: the same point forecast is multiplied by a fitted day-of-week
  reporting factor, then used as the mean of a negative-binomial
  distribution (dispersion fit on calib) for the RAW daily count.
"""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

import numpy as np

from scoped_correspondence.errors import ScopeViolationError
from scoped_correspondence.validation.covid_pilot import load_world_daily
from scoped_correspondence.validation.covid_observation_model import _lagged_means
from scoped_correspondence.validation.scoring_rules import (
    SOURCE as SCORING_SOURCE,
    fit_neg_binom_dispersion,
    neg_binom_log_score,
    neg_binom_prediction_interval,
    poisson_log_score,
    poisson_prediction_interval,
)
from scoped_correspondence.validation.mechanistic_rolling_origin import (
    COVID_RENEWAL_HORIZON_DAYS,
    COVID_RENEWAL_ORIGINS_DAY_INDEX,
    _covid_daily_series,
    _covid_renewal_predictor_factory,
)

SOURCE = SCORING_SOURCE
MIN_CALIB_DAYS = 14  # >= 2 full weeks, so every weekday appears at least twice
DEFAULT_COVERAGE = 0.8


def fit_weekday_multipliers(
    dates: Sequence[dt.date], observed_raw: Sequence[float], reference_mean: Sequence[float]
) -> Dict[int, float]:
    """Multiplicative day-of-week reporting factor, ``date.weekday()`` (Mon=0..Sun=6) -> factor.

    ``factor_raw[wd] = median(observed_raw[i] / reference_mean[i])`` over
    all ``i`` with that weekday, then renormalized so
    ``mean(factor.values()) == 1`` — a WITHIN-week redistribution that does
    not change the overall predicted level (a systematic upward or
    downward bias belongs to the mean forecast, not to this multiplier).
    All 7 weekdays must be present, else raises (a calibration window
    shorter than ~2 weeks cannot estimate a weekly pattern).
    """
    if not (len(dates) == len(observed_raw) == len(reference_mean)):
        raise ScopeViolationError("fit_weekday_multipliers: dates, observed_raw, reference_mean must have equal length")
    if len(dates) < MIN_CALIB_DAYS:
        raise ScopeViolationError(f"fit_weekday_multipliers: need >= {MIN_CALIB_DAYS} calib days; got {len(dates)}")
    for r in reference_mean:
        if not (float(r) > 0.0):
            raise ScopeViolationError(f"fit_weekday_multipliers: reference_mean entries must be > 0; got {r!r}")

    ratios_by_wd: Dict[int, List[float]] = {wd: [] for wd in range(7)}
    for d, o, r in zip(dates, observed_raw, reference_mean):
        ratios_by_wd[d.weekday()].append(float(o) / float(r))
    missing = [wd for wd, lst in ratios_by_wd.items() if not lst]
    if missing:
        raise ScopeViolationError(f"fit_weekday_multipliers: weekday(s) {missing} absent from the calib window")

    raw_factor = {wd: float(np.median(lst)) for wd, lst in ratios_by_wd.items()}
    mean_factor = float(np.mean(list(raw_factor.values())))
    if not (mean_factor > 0.0):
        raise ScopeViolationError("fit_weekday_multipliers: degenerate (non-positive) mean factor")
    return {wd: v / mean_factor for wd, v in raw_factor.items()}


def weekday_adjusted_mean(date: dt.date, latent_mean: float, weekday_multipliers: Dict[int, float]) -> float:
    """``latent_mean * weekday_multipliers[date.weekday()]``."""
    if not (float(latent_mean) > 0.0):
        raise ScopeViolationError(f"weekday_adjusted_mean: latent_mean must be > 0; got {latent_mean!r}")
    wd = date.weekday()
    if wd not in weekday_multipliers:
        raise ScopeViolationError(f"weekday_adjusted_mean: weekday {wd} not in weekday_multipliers")
    return float(latent_mean) * float(weekday_multipliers[wd])


@dataclass(frozen=True)
class LatentObservationTrial:
    origin_day_index: int
    step: int
    target_date: str
    observed_raw: int
    old_predicted_mean: float
    old_log_score: float
    old_interval: Tuple[float, float]
    old_covered: bool
    new_predicted_mean: float
    new_log_score: float
    new_interval: Tuple[float, float]
    new_covered: bool

    def to_dict(self) -> Dict[str, Any]:
        return {
            "origin_day_index": self.origin_day_index, "step": self.step, "target_date": self.target_date,
            "observed_raw": self.observed_raw,
            "old_predicted_mean": self.old_predicted_mean, "old_log_score": self.old_log_score,
            "old_interval": list(self.old_interval), "old_covered": self.old_covered,
            "new_predicted_mean": self.new_predicted_mean, "new_log_score": self.new_log_score,
            "new_interval": list(self.new_interval), "new_covered": self.new_covered,
        }


@dataclass(frozen=True)
class LatentRenewalObservationReport:
    n_trials: int
    coverage_target: float
    n_calib_days: int
    weekday_multipliers: Dict[int, float]
    fitted_dispersion: float
    old_mean_log_score: float
    new_mean_log_score: float
    old_empirical_coverage: float
    new_empirical_coverage: float
    new_wins_log_score: bool
    trials: Tuple[LatentObservationTrial, ...]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "n_trials": self.n_trials,
            "coverage_target": self.coverage_target,
            "n_calib_days": self.n_calib_days,
            "weekday_multipliers": {str(k): v for k, v in self.weekday_multipliers.items()},
            "fitted_dispersion": self.fitted_dispersion,
            "old_mean_log_score": self.old_mean_log_score,
            "new_mean_log_score": self.new_mean_log_score,
            "old_empirical_coverage": self.old_empirical_coverage,
            "new_empirical_coverage": self.new_empirical_coverage,
            "new_wins_log_score": self.new_wins_log_score,
            "trials": [t.to_dict() for t in self.trials],
        }


def run_covid_latent_renewal_observation_comparison(
    data_path: str | Path, *, coverage: float = DEFAULT_COVERAGE
) -> LatentRenewalObservationReport:
    """Old (Poisson-on-renewal-mean) vs. new (weekday-adjusted negative-binomial) on the
    SAME forecast origins/horizons as ``run_covid_renewal_rolling_origin_backtest``.

    The weekday multipliers and NB dispersion are fit ONCE, on the days
    strictly BEFORE the first evaluated origin (``day_index < min(
    COVID_RENEWAL_ORIGINS_DAY_INDEX)``) -- entirely out-of-sample with
    respect to every scored trial, using the non-circular forward-only
    lagged mean (``covid_observation_model._lagged_means``) as the
    reference mean for both the weekday-ratio and dispersion fits.
    """
    if not (0.0 < float(coverage) < 1.0):
        raise ScopeViolationError(f"run_covid_latent_renewal_observation_comparison: coverage must be in (0,1); got {coverage!r}")

    day_index, incidence, dates_iso = _covid_daily_series(data_path)
    dates_dt = [dt.date.fromisoformat(s) for s in dates_iso]
    n = len(day_index)

    all_points = load_world_daily(data_path)
    raw_by_date = {p.date: p.new_cases for p in all_points}
    missing_raw = [d for d in dates_dt if d not in raw_by_date]
    if missing_raw:
        raise ScopeViolationError(
            f"run_covid_latent_renewal_observation_comparison: {len(missing_raw)} date(s) in the "
            "analysis window have no raw new_cases entry"
        )

    first_origin = int(min(COVID_RENEWAL_ORIGINS_DAY_INDEX))
    calib_dates_all = dates_dt[:first_origin]
    lagged, _dropped = _lagged_means(data_path, calib_dates_all)
    calib_dates = [d for d in calib_dates_all if d in lagged]
    if len(calib_dates) < MIN_CALIB_DAYS:
        raise ScopeViolationError(
            f"run_covid_latent_renewal_observation_comparison: only {len(calib_dates)} calib days "
            f"have a full lookback (need >= {MIN_CALIB_DAYS})"
        )
    calib_raw = [raw_by_date[d] for d in calib_dates]
    calib_ref_mean = [lagged[d] for d in calib_dates]

    weekday_mult = fit_weekday_multipliers(calib_dates, calib_raw, calib_ref_mean)
    calib_adjusted_mean = [weekday_adjusted_mean(d, m, weekday_mult) for d, m in zip(calib_dates, calib_ref_mean)]
    dispersion = fit_neg_binom_dispersion([int(round(v)) for v in calib_raw], calib_adjusted_mean)

    predictor = _covid_renewal_predictor_factory()

    trials: List[LatentObservationTrial] = []
    for origin in COVID_RENEWAL_ORIGINS_DAY_INDEX:
        origin_i = int(origin)
        calib_x = day_index[: origin_i + 1]
        calib_y = incidence[: origin_i + 1]
        for step in range(1, COVID_RENEWAL_HORIZON_DAYS + 1):
            target_idx = origin_i + step
            if target_idx >= n:
                continue
            test_x = np.array([float(target_idx)])
            old_mean = float(predictor(calib_x, calib_y, test_x)[0])
            if not (old_mean > 0.0):
                continue  # non-positive renewal projection: cannot build a count-model mean

            target_date = dates_dt[target_idx]
            observed_raw = int(round(raw_by_date[target_date]))

            old_score = poisson_log_score(observed_raw, old_mean)
            old_interval = poisson_prediction_interval(old_mean, coverage)
            old_covered = old_interval[0] <= observed_raw <= old_interval[1]

            new_mean = weekday_adjusted_mean(target_date, old_mean, weekday_mult)
            new_score = neg_binom_log_score(observed_raw, new_mean, dispersion)
            new_interval = neg_binom_prediction_interval(new_mean, dispersion, coverage)
            new_covered = new_interval[0] <= observed_raw <= new_interval[1]

            trials.append(LatentObservationTrial(
                origin_day_index=origin_i, step=step, target_date=target_date.isoformat(),
                observed_raw=observed_raw,
                old_predicted_mean=old_mean, old_log_score=old_score, old_interval=old_interval, old_covered=old_covered,
                new_predicted_mean=new_mean, new_log_score=new_score, new_interval=new_interval, new_covered=new_covered,
            ))

    if not trials:
        raise ScopeViolationError("run_covid_latent_renewal_observation_comparison: zero scored trials")

    old_scores = [t.old_log_score for t in trials]
    new_scores = [t.new_log_score for t in trials]
    old_cov = sum(1 for t in trials if t.old_covered) / len(trials)
    new_cov = sum(1 for t in trials if t.new_covered) / len(trials)

    return LatentRenewalObservationReport(
        n_trials=len(trials),
        coverage_target=float(coverage),
        n_calib_days=len(calib_dates),
        weekday_multipliers=weekday_mult,
        fitted_dispersion=dispersion,
        old_mean_log_score=float(np.mean(old_scores)),
        new_mean_log_score=float(np.mean(new_scores)),
        old_empirical_coverage=old_cov,
        new_empirical_coverage=new_cov,
        new_wins_log_score=bool(np.mean(new_scores) < np.mean(old_scores)),
        trials=tuple(trials),
    )


__all__ = [
    "SOURCE", "MIN_CALIB_DAYS", "DEFAULT_COVERAGE",
    "LatentObservationTrial", "LatentRenewalObservationReport",
    "fit_weekday_multipliers", "weekday_adjusted_mean",
    "run_covid_latent_renewal_observation_comparison",
]
