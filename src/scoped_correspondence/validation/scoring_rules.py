"""Proper scoring rules for probabilistic forecasts (Milestone 49).

MECHANISTIC_VALIDATION_ROADMAP.md package 3, response to
prompts/Answers/nicht_stationäre_Treiber/SCF_Review_f8e249f.md (Astra,
2026-09-21): "Bisher liefern alle Module Punktschätzungen (RMSE, AIC).
[...] Vorhersageintervalle [...] Log-Score für Zähl-/Ereignismodelle,
CRPS oder Intervall-Score für kontinuierliche Ziele" (Gneiting & Raftery
2007, JASA 102:359-378, DOI 10.1198/016214506000001437).

Two scoring rules, chosen to match what the mechanistic models can
actually produce (a point forecast plus either an empirical residual
distribution or a count-model mean), not a full predictive density:

- ``interval_score``: the proper scoring rule for a central prediction
  interval (Gneiting & Raftery 2007, eq. 43) -- rewards a narrow interval
  but penalizes it heavily for missing the observation. Used for the
  continuous targets (energy balance temperature, COVID incidence) with
  intervals built from LEAVE-ONE-ORIGIN-OUT empirical residual quantiles
  (see ``validation.mechanistic_probabilistic_evaluation`` -- NOT
  ``validation.conformal``'s split-conformal quantile, see
  CONFORMAL_EXCHANGEABILITY_WARNING below for why).
- ``poisson_log_score`` / ``poisson_prediction_interval``: for the ETAS
  count-model comparison, treating each model's point forecast as the
  mean of a Poisson predictive distribution -- an explicit, documented
  simplification (real ETAS counts are overdispersed relative to Poisson;
  this is used only as a COMMON, shared reference distribution across
  ETAS/persistence/constant-rate so scores are directly comparable, not
  as a claim that any of them is truly Poisson-distributed).
- ``neg_binom_log_score`` / ``fit_neg_binom_dispersion``: the NB2
  parametrization (mean ``mu``, dispersion ``alpha``, variance
  ``mu + alpha*mu^2``) used by
  ``validation.covid_observation_model`` (MECHANISTIC_VALIDATION_ROADMAP.md
  package 5) to TEST whether real raw daily COVID case counts are
  overdispersed relative to Poisson, rather than assuming it a priori
  (Astra, 2026-09-21: "Notwendigkeit über Residuen/Prognosescores
  prüfen, nicht a priori annehmen").

CONFORMAL_EXCHANGEABILITY_WARNING: ``validation.conformal`` (split
conformal, Lei et al. 2018) already documents its own coverage as
"marginal under exchangeability" -- but the rolling-origin residuals here
come from OVERLAPPING, serially-correlated calibration windows on
non-stationary series (the whole point of this repository's
NONSTATIONARY_ROADMAP.md work), which is exactly the setting where
exchangeability is NOT a safe default assumption. This module therefore
does NOT invoke ``validation.conformal`` for the mechanistic models;
prediction intervals instead use plain leave-one-origin-out empirical
quantiles (still not exchangeability-free, but not dressed up with a
conformal guarantee it cannot actually deliver here) or a Poisson
parametric interval (ETAS), with coverage EMPIRICALLY reported, not
assumed from a theorem that does not apply.
"""

from __future__ import annotations

from typing import Sequence, Tuple

import numpy as np
from scipy.optimize import minimize_scalar
from scipy.stats import nbinom as nbinom_dist
from scipy.stats import poisson as poisson_dist

from scoped_correspondence.errors import ScopeViolationError

SOURCE = (
    "Gneiting & Raftery 2007, Strictly Proper Scoring Rules, Prediction, and "
    "Estimation, JASA 102:359-378, DOI 10.1198/016214506000001437 (interval "
    "score, eq. 43; log score)."
)

CONFORMAL_EXCHANGEABILITY_WARNING = (
    "Rolling-origin residuals from overlapping calibration windows on "
    "non-stationary series are NOT exchangeable -- validation.conformal's "
    "split-conformal coverage guarantee does not apply here without further "
    "justification. This module uses leave-one-origin-out empirical "
    "quantiles / a Poisson parametric interval instead, with coverage "
    "reported empirically, not claimed from conformal theory."
)


def interval_score(lower: float, upper: float, observed: float, alpha: float) -> float:
    """Gneiting & Raftery 2007, eq. 43: proper score for a central (1-alpha) interval.

        IS = (upper - lower) + (2/alpha)*(lower - y)*1[y < lower] + (2/alpha)*(y - upper)*1[y > upper]

    Lower is better. Rewards a narrow interval; penalizes missing the
    observation proportionally to 2/alpha times the miss distance -- a
    proper scoring rule (an interval built with the correct nominal
    coverage minimizes its expectation), not an ad hoc penalty.
    """
    if upper < lower:
        raise ScopeViolationError(f"interval_score: upper ({upper!r}) must be >= lower ({lower!r})")
    if not (0.0 < alpha < 1.0):
        raise ScopeViolationError(f"interval_score: alpha must be in (0,1); got {alpha!r}")
    width = upper - lower
    penalty = 0.0
    if observed < lower:
        penalty = (2.0 / alpha) * (lower - observed)
    elif observed > upper:
        penalty = (2.0 / alpha) * (observed - upper)
    return float(width + penalty)


def empirical_coverage(intervals: Sequence[Tuple[float, float]], observations: Sequence[float]) -> float:
    """Fraction of observations falling within their (lower, upper) interval, inclusive."""
    if len(intervals) != len(observations):
        raise ScopeViolationError("empirical_coverage: intervals and observations must have the same length")
    if not intervals:
        raise ScopeViolationError("empirical_coverage: need at least one (interval, observation) pair")
    hits = sum(1 for (lo, hi), y in zip(intervals, observations) if lo <= y <= hi)
    return float(hits) / len(intervals)


def poisson_log_score(observed_count: int, predicted_mean: float) -> float:
    """Negative log-likelihood of ``observed_count`` under Poisson(predicted_mean).

    Lower is better (a proper scoring rule for count data under the
    explicit, documented Poisson simplification -- see module docstring).
    """
    if predicted_mean <= 0:
        raise ScopeViolationError(f"poisson_log_score: predicted_mean must be > 0; got {predicted_mean!r}")
    if observed_count < 0 or int(observed_count) != observed_count:
        raise ScopeViolationError(f"poisson_log_score: observed_count must be a non-negative integer; got {observed_count!r}")
    log_pmf = float(poisson_dist.logpmf(int(observed_count), predicted_mean))
    return -log_pmf


def poisson_prediction_interval(predicted_mean: float, coverage: float) -> Tuple[float, float]:
    """Central (coverage) prediction interval for Poisson(predicted_mean), via the exact quantile function.

    Returns (lower, upper) as the smallest integers k such that
    P(X<=lower) >= (1-coverage)/2 and P(X<=upper) >= 1-(1-coverage)/2 --
    the standard central Poisson interval (scipy.stats.poisson.ppf).
    """
    if predicted_mean <= 0:
        raise ScopeViolationError(f"poisson_prediction_interval: predicted_mean must be > 0; got {predicted_mean!r}")
    if not (0.0 < coverage < 1.0):
        raise ScopeViolationError(f"poisson_prediction_interval: coverage must be in (0,1); got {coverage!r}")
    alpha = 1.0 - coverage
    lower = float(poisson_dist.ppf(alpha / 2.0, predicted_mean))
    upper = float(poisson_dist.ppf(1.0 - alpha / 2.0, predicted_mean))
    return lower, upper


def _nb_mean_dispersion_to_n_p(mean: float, dispersion: float) -> Tuple[float, float]:
    """NB2 parametrization (mean, dispersion; variance = mean + dispersion*mean^2)
    converted to scipy.stats.nbinom's (n, p) parametrization
    (mean = n(1-p)/p, variance = n(1-p)/p^2 = mean/p)."""
    p = 1.0 / (1.0 + dispersion * mean)
    n = mean * p / (1.0 - p)
    return n, p


def neg_binom_log_score(observed_count: int, predicted_mean: float, dispersion: float) -> float:
    """Negative log-likelihood of ``observed_count`` under NB2(predicted_mean, dispersion).

    ``dispersion=0`` is the Poisson limit (variance=mean); ``dispersion>0``
    allows variance > mean (overdispersion). Lower is better.
    """
    if predicted_mean <= 0:
        raise ScopeViolationError(f"neg_binom_log_score: predicted_mean must be > 0; got {predicted_mean!r}")
    if dispersion < 0:
        raise ScopeViolationError(f"neg_binom_log_score: dispersion must be >= 0; got {dispersion!r}")
    if observed_count < 0 or int(observed_count) != observed_count:
        raise ScopeViolationError(f"neg_binom_log_score: observed_count must be a non-negative integer; got {observed_count!r}")
    if dispersion == 0.0:
        return poisson_log_score(observed_count, predicted_mean)
    n, p = _nb_mean_dispersion_to_n_p(predicted_mean, dispersion)
    return -float(nbinom_dist.logpmf(int(observed_count), n, p))


def fit_neg_binom_dispersion(observed_counts: Sequence[int], predicted_means: Sequence[float]) -> float:
    """MLE dispersion (NB2) given fixed per-observation predicted means.

    A single shared ``dispersion`` is fit across all (observed, predicted)
    pairs by 1-D maximum likelihood (``scipy.optimize.minimize_scalar`` on
    ``log(dispersion)`` for positivity) -- the means themselves are taken
    as given (e.g. an already-fitted smoothed rate), not refit here.
    """
    observed_counts = np.asarray(observed_counts)
    predicted_means = np.asarray(predicted_means, dtype=float)
    if len(observed_counts) != len(predicted_means):
        raise ScopeViolationError("fit_neg_binom_dispersion: observed_counts and predicted_means must have the same length")
    if len(observed_counts) < 2:
        raise ScopeViolationError("fit_neg_binom_dispersion: need >= 2 observations")
    if np.any(predicted_means <= 0):
        raise ScopeViolationError("fit_neg_binom_dispersion: all predicted_means must be > 0")

    def neg_ll(log_dispersion: float) -> float:
        dispersion = float(np.exp(log_dispersion))
        return float(sum(neg_binom_log_score(int(o), float(m), dispersion) for o, m in zip(observed_counts, predicted_means)))

    result = minimize_scalar(neg_ll, bounds=(-20.0, 20.0), method="bounded")
    if not result.success:
        raise ScopeViolationError(f"fit_neg_binom_dispersion: 1-D MLE failed to converge: {result.message}")
    return float(np.exp(result.x))


__all__ = [
    "SOURCE",
    "CONFORMAL_EXCHANGEABILITY_WARNING",
    "interval_score",
    "empirical_coverage",
    "poisson_log_score",
    "poisson_prediction_interval",
    "neg_binom_log_score",
    "fit_neg_binom_dispersion",
]
