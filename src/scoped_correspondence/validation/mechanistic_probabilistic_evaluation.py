"""Prediction intervals + proper scoring rules for the 3 mechanistic models (Milestone 50).

MECHANISTIC_VALIDATION_ROADMAP.md package 3, response to
prompts/Answers/nicht_stationäre_Treiber/SCF_Review_f8e249f.md (Astra,
2026-09-21): "Bisher liefern alle Module Punktschätzungen (RMSE, AIC)."
Builds on package 2's rolling-origin infrastructure (same origins,
horizons, predictors, and -- for the energy-balance case -- the SAME
private predictor helpers, imported directly rather than reimplemented,
so numbers stay identical to package 2's own report) to add genuine
predictive uncertainty:

- ENERGY BALANCE / COVID RENEWAL (continuous targets): leave-one-origin-out
  empirical residual quantiles build a (1-alpha) interval around each
  point forecast, scored with the interval score (Gneiting & Raftery
  2007) and empirical coverage -- see
  ``scoring_rules.CONFORMAL_EXCHANGEABILITY_WARNING`` for why this is NOT
  ``validation.conformal``'s split-conformal quantile (rolling-origin
  residuals here are not exchangeable).
- ETAS (count target): each model's point forecast is treated as a
  Poisson mean (an explicit, documented simplification -- real ETAS
  counts are overdispersed relative to Poisson; this is used only as a
  COMMON reference distribution so scores are comparable across
  ETAS/persistence/constant-rate), scored with the Poisson log score and
  a Poisson prediction interval's empirical coverage.

HONEST SMALL-SAMPLE CAVEAT: leave-one-origin-out quantiles here come from
only 10 (energy balance) or 5 (COVID) other origins per lead time --
thin deciles, not a claim of well-estimated tail quantiles. Reported as
an exploratory diagnostic, consistent with this repository's discipline
of surfacing small-N limitations rather than dressing them up.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np

from scoped_correspondence.errors import ScopeViolationError
from scoped_correspondence.validation.rolling_origin import (
    RawHorizonPrediction,
    raw_predictions_by_horizon_step,
)
from scoped_correspondence.validation.scoring_rules import (
    SOURCE as SCORING_SOURCE,
    CONFORMAL_EXCHANGEABILITY_WARNING,
    empirical_coverage,
    interval_score,
    poisson_log_score,
    poisson_prediction_interval,
)
from scoped_correspondence.validation.mechanistic_rolling_origin import (
    COVID_RENEWAL_HORIZON_DAYS,
    COVID_RENEWAL_ORIGINS_DAY_INDEX,
    _covid_daily_series,
    _covid_exponential_extrapolation_predictor,
    _covid_persistence_predictor,
    _covid_renewal_predictor_factory,
    _energy_balance_mechanistic_predictor_factory,
    run_etas_forecast_check,
)
from scoped_correspondence.validation.noaa_temp_pilot import (
    ROLLING_ORIGIN_HORIZON_YEARS,
    ROLLING_ORIGIN_YEARS,
    _expanding_linear_predictor,
    _last_30_years_linear_predictor,
    _persistence_predictor,
)
from scoped_correspondence.dynamics.energy_balance import _load_overlap_series

SOURCE = SCORING_SOURCE

DEFAULT_INTERVAL_ALPHA = 0.2  # nominal 80% central interval
MIN_LOO_RESIDUALS = 3


@dataclass(frozen=True)
class LeaveOneOutIntervalReport:
    predictor_name: str
    alpha: float
    n_trials: int
    empirical_coverage_value: float
    mean_interval_score: float
    per_trial: Tuple[Dict[str, float], ...]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "predictor_name": self.predictor_name,
            "alpha": self.alpha,
            "nominal_coverage": 1.0 - self.alpha,
            "n_trials": self.n_trials,
            "empirical_coverage": self.empirical_coverage_value,
            "mean_interval_score": self.mean_interval_score,
            "per_trial": [dict(t) for t in self.per_trial],
        }


def leave_one_origin_out_intervals(
    raw_predictions: Dict[str, List[RawHorizonPrediction]],
    *,
    alpha: float = DEFAULT_INTERVAL_ALPHA,
) -> Dict[str, LeaveOneOutIntervalReport]:
    """Leave-one-origin-out empirical-quantile (1-alpha) intervals, per predictor.

    For each (origin, step) prediction, the interval is built from the
    alpha/2 and 1-alpha/2 empirical quantiles of that SAME predictor's
    residuals (observed-predicted) at the SAME step from every OTHER
    origin -- never including the trial's own residual (anti-leak, mirrors
    this repository's calib/holdout discipline elsewhere). NOT an
    exchangeability-based (conformal) guarantee -- see
    ``scoring_rules.CONFORMAL_EXCHANGEABILITY_WARNING``.
    """
    if not (0.0 < alpha < 1.0):
        raise ScopeViolationError(f"leave_one_origin_out_intervals: alpha must be in (0,1); got {alpha!r}")

    out: Dict[str, LeaveOneOutIntervalReport] = {}
    for name, preds in raw_predictions.items():
        residuals_by_step: Dict[int, List[Tuple[float, float]]] = {}
        for p in preds:
            residuals_by_step.setdefault(p.step, []).append((p.origin, p.observed - p.predicted))

        intervals: List[Tuple[float, float]] = []
        observed_list: List[float] = []
        per_trial: List[Dict[str, float]] = []
        for p in preds:
            loo_residuals = [r for (o, r) in residuals_by_step[p.step] if o != p.origin]
            if len(loo_residuals) < MIN_LOO_RESIDUALS:
                raise ScopeViolationError(
                    f"leave_one_origin_out_intervals: only {len(loo_residuals)} LOO residuals for "
                    f"{name!r} step {p.step!r}, need >= {MIN_LOO_RESIDUALS}"
                )
            lo_q = float(np.quantile(loo_residuals, alpha / 2.0))
            hi_q = float(np.quantile(loo_residuals, 1.0 - alpha / 2.0))
            lower, upper = p.predicted + lo_q, p.predicted + hi_q
            if upper < lower:
                lower, upper = upper, lower
            score = interval_score(lower, upper, p.observed, alpha)
            intervals.append((lower, upper))
            observed_list.append(p.observed)
            per_trial.append(
                {"origin": p.origin, "step": p.step, "lower": lower, "upper": upper, "observed": p.observed, "interval_score": score}
            )

        out[name] = LeaveOneOutIntervalReport(
            predictor_name=name,
            alpha=alpha,
            n_trials=len(per_trial),
            empirical_coverage_value=empirical_coverage(intervals, observed_list),
            mean_interval_score=float(np.mean([t["interval_score"] for t in per_trial])),
            per_trial=tuple(per_trial),
        )
    return out


def run_energy_balance_probabilistic_evaluation(
    co2_path: str | Path, temp_path: str | Path, *, alpha: float = DEFAULT_INTERVAL_ALPHA
) -> Dict[str, LeaveOneOutIntervalReport]:
    """LOO interval score + coverage for all 4 package-2 energy-balance predictors,
    pooling all 11 origins x 5 lead years = 55 trials per predictor.
    """
    years_all, Tobs_all, F_vals_all = _load_overlap_series(co2_path, temp_path)
    years_arr = np.array(years_all, dtype=float)
    predictor = _energy_balance_mechanistic_predictor_factory(years_all, F_vals_all)
    raw = raw_predictions_by_horizon_step(
        years_arr,
        Tobs_all,
        origins=ROLLING_ORIGIN_YEARS,
        max_horizon_steps=ROLLING_ORIGIN_HORIZON_YEARS,
        step_size=1.0,
        predictors={
            "persistence": _persistence_predictor,
            "expanding": _expanding_linear_predictor,
            "last30": _last_30_years_linear_predictor,
            "energy_balance_mechanistic": predictor,
        },
    )
    return leave_one_origin_out_intervals(raw, alpha=alpha)


def run_covid_renewal_probabilistic_evaluation(
    data_path: str | Path, *, alpha: float = DEFAULT_INTERVAL_ALPHA
) -> Dict[str, LeaveOneOutIntervalReport]:
    """LOO interval score + coverage for all 3 package-2 COVID predictors,
    pooling all 6 origins x 7 horizon days = 42 trials per predictor.
    """
    day_index, incidence, _dates = _covid_daily_series(data_path)
    raw = raw_predictions_by_horizon_step(
        day_index,
        incidence,
        origins=[float(o) for o in COVID_RENEWAL_ORIGINS_DAY_INDEX],
        max_horizon_steps=COVID_RENEWAL_HORIZON_DAYS,
        step_size=1.0,
        predictors={
            "persistence": _covid_persistence_predictor,
            "exponential_extrapolation": _covid_exponential_extrapolation_predictor,
            "renewal_constant_R": _covid_renewal_predictor_factory(),
        },
    )
    return leave_one_origin_out_intervals(raw, alpha=alpha)


def run_etas_probabilistic_evaluation(catalog_path: str | Path, *, coverage: float = 0.9) -> Dict[str, Dict[str, Any]]:
    """Poisson log-score + Poisson-interval empirical coverage for the 3 package-2
    ETAS-domain predictors (etas_first_order, persistence, constant_rate), on the
    SAME 6 holdout years -- refits nothing new (reuses run_etas_forecast_check).
    """
    result = run_etas_forecast_check(catalog_path)
    observed = [int(v) for v in result["observed_counts"]]

    out: Dict[str, Dict[str, Any]] = {}
    for name, key in (
        ("etas_first_order", "etas_first_order_predicted"),
        ("persistence", "persistence_predicted"),
        ("constant_rate", "constant_rate_predicted"),
    ):
        preds = result[key]
        log_scores = [poisson_log_score(o, p) for o, p in zip(observed, preds)]
        intervals = [poisson_prediction_interval(p, coverage) for p in preds]
        out[name] = {
            "predicted_means": preds,
            "mean_log_score": float(np.mean(log_scores)),
            "log_scores": log_scores,
            "coverage_target": coverage,
            "empirical_coverage": empirical_coverage(intervals, observed),
            "intervals": intervals,
        }
    return out


__all__ = [
    "SOURCE",
    "CONFORMAL_EXCHANGEABILITY_WARNING",
    "DEFAULT_INTERVAL_ALPHA",
    "LeaveOneOutIntervalReport",
    "leave_one_origin_out_intervals",
    "run_energy_balance_probabilistic_evaluation",
    "run_covid_renewal_probabilistic_evaluation",
    "run_etas_probabilistic_evaluation",
]
