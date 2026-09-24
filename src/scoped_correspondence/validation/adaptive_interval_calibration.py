"""Adaptive prediction-interval calibration under changing conditions (Milestone 55).

CAPABILITY_EXPANSION_ROADMAP.md Priority 1, response to Astra's 2026-09-24
capability assessment (prompts/Answers/nicht_stationäre_Treiber/
SCF_Faehigkeiten_und_Ausbauplan_2026-09-24.md): "Zuerst eine robuste
einfache Referenz: vergangene Prognosefehler fortlaufend sammeln und daraus
nach Prognosehorizont getrennte Intervalle kalibrieren. Danach Adaptive
Conformal Inference beziehungsweise Conformal PID Control als Kandidaten
vergleichen."

Three calibration methods share the exact same causal quantile machinery
(strict temporal eligibility identical to
``mechanistic_probabilistic_evaluation.leave_one_origin_out_intervals``:
a score is only usable once its OWN target time has occurred, i.e.
``target_time <= current_origin``) and differ only in how the miscoverage
level ``alpha_t`` used for that quantile evolves over time:

- ``"rolling_reference"``: ``alpha_t`` is held fixed at ``alpha_target`` —
  the simple baseline Astra asked to compare against first.
- ``"aci"``: Adaptive Conformal Inference (Gibbs & Candès 2024, JMLR 25,
  https://www.jmlr.org/papers/v25/22-1218.html) — the online recursion
  ``alpha_{t+1} = alpha_t + gamma * (alpha_target - err_t)``.
- ``"pid"``: a Proportional+Integral SUBSET of Conformal PID Control
  (Angelopoulos, Candès & Tibshirani 2023, NeurIPS,
  https://papers.neurips.cc/paper_files/paper/2023/hash/47f2fad8c1111d07f83c91be7870f8db-Abstract-Conference.html).
  The Integral term is exactly the ACI recursion above (own learning rate
  ``gamma_i``); the Proportional term additionally reacts to the LOCAL
  miscoverage rate over a short recent window. **Scope limitation,
  documented rather than silently approximated:** the published method
  also includes a learned "scorecaster" component (a separate forecasting
  model for the quantile itself) and a bounded saturation link function on
  the integrator, neither of which is implemented here — see
  docs/adaptive_interval_calibration.md.

COVERAGE SEMANTICS WARNING (Astra, explicitly requested): both ACI and the
PID variant target ``alpha_target`` as a LONG-RUN AVERAGE miscoverage rate
over the sequence — this is a real, non-trivial guarantee for ACI under
arbitrary distribution shift (Gibbs & Candès 2024, Theorem 1), but it is
NOT a claim of correct coverage at every individual time point, and is
even less established for the simplified P+I variant implemented here,
which has no corresponding published guarantee of its own. Do not read
"the reported empirical coverage lands near 1-alpha_target" as evidence of
POINTWISE / CONDITIONAL calibration.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

import numpy as np

from scoped_correspondence.errors import ScopeViolationError
from scoped_correspondence.validation.rolling_origin import (
    RawHorizonPrediction,
    raw_predictions_by_horizon_step,
)
from scoped_correspondence.validation.scoring_rules import (
    SOURCE as SCORING_SOURCE,
    empirical_coverage,
    interval_score,
)
from scoped_correspondence.validation.mechanistic_rolling_origin import (
    COVID_RENEWAL_HORIZON_DAYS,
    COVID_RENEWAL_ORIGINS_DAY_INDEX,
    _covid_daily_series,
    _covid_exponential_extrapolation_predictor,
    _covid_persistence_predictor,
    _covid_renewal_predictor_factory,
    _energy_balance_mechanistic_predictor_factory,
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
SOURCE_ACI = (
    "Gibbs, I.; Candès, E. J. (2024): Conformal Inference for Online "
    "Prediction with Arbitrary Distribution Shifts. JMLR 25. "
    "https://www.jmlr.org/papers/v25/22-1218.html"
)
SOURCE_PID = (
    "Angelopoulos, A. N.; Candès, E. J.; Tibshirani, R. J. (2023): "
    "Conformal PID Control for Time Series Prediction. NeurIPS. "
    "https://papers.neurips.cc/paper_files/paper/2023/hash/"
    "47f2fad8c1111d07f83c91be7870f8db-Abstract-Conference.html"
)
PID_SCOPE_NOTE = (
    "Implements only the Proportional + Integral terms of Conformal PID "
    "Control; the published method's learned scorecaster and bounded "
    "saturation link are NOT implemented."
)

METHODS: Tuple[str, ...] = ("rolling_reference", "aci", "pid")
DEFAULT_ALPHA_TARGET = 0.2  # nominal 80% central interval, matches package 3
MIN_CAUSAL_SCORES = 3  # same lookback floor as leave_one_origin_out_intervals
_EPS_ALPHA = 1e-3  # keep alpha_t strictly inside (0,1) so a quantile level always exists


def aci_update_alpha(alpha_t: float, alpha_target: float, err_t: int, gamma: float) -> float:
    """Gibbs & Candès (2024) online update: ``alpha_{t+1} = alpha_t + gamma*(alpha_target - err_t)``.

    ``err_t=1`` (missed/miscovered) pushes ``alpha_t`` DOWN (higher nominal
    coverage level ``1-alpha_t`` next time -> wider interval). ``err_t=0``
    (covered) pushes it slightly UP (narrower interval), so that on a
    stationary sequence ``alpha_t`` settles near ``alpha_target``. Clipped
    to ``[_EPS_ALPHA, 1-_EPS_ALPHA]`` so a quantile level always exists.
    """
    if err_t not in (0, 1):
        raise ScopeViolationError(f"aci_update_alpha: err_t must be 0 or 1; got {err_t!r}")
    if not (0.0 < float(alpha_target) < 1.0):
        raise ScopeViolationError(f"aci_update_alpha: alpha_target must be in (0,1); got {alpha_target!r}")
    if not (float(gamma) > 0.0):
        raise ScopeViolationError(f"aci_update_alpha: gamma must be > 0; got {gamma!r}")
    new_alpha = float(alpha_t) + float(gamma) * (float(alpha_target) - int(err_t))
    return float(min(max(new_alpha, _EPS_ALPHA), 1.0 - _EPS_ALPHA))


def pid_update_alpha(
    alpha_t: float,
    alpha_target: float,
    err_t: int,
    *,
    gamma_i: float,
    recent_errs: Sequence[int],
    kp: float,
) -> float:
    """P+I subset of Conformal PID Control — see module docstring for scope.

    Integral term: identical recursion to :func:`aci_update_alpha` (own
    rate ``gamma_i``). Proportional term: ``kp * (alpha_target -
    local_miscoverage_rate)`` where ``local_miscoverage_rate`` is the mean
    of ``recent_errs`` (a short trailing window) — reacts to a recent run
    of misses/hits faster than the integral term alone, in the SAME sign
    convention (too many recent misses -> local_rate > alpha_target ->
    term is negative -> alpha_t decreases -> interval widens).
    """
    if err_t not in (0, 1):
        raise ScopeViolationError(f"pid_update_alpha: err_t must be 0 or 1; got {err_t!r}")
    if not (0.0 < float(alpha_target) < 1.0):
        raise ScopeViolationError(f"pid_update_alpha: alpha_target must be in (0,1); got {alpha_target!r}")
    if not (float(gamma_i) > 0.0):
        raise ScopeViolationError(f"pid_update_alpha: gamma_i must be > 0; got {gamma_i!r}")
    if not (float(kp) >= 0.0):
        raise ScopeViolationError(f"pid_update_alpha: kp must be >= 0; got {kp!r}")
    for e in recent_errs:
        if e not in (0, 1):
            raise ScopeViolationError(f"pid_update_alpha: recent_errs entries must be 0 or 1; got {e!r}")

    integral_term = float(gamma_i) * (float(alpha_target) - int(err_t))
    local_rate = (sum(recent_errs) / len(recent_errs)) if recent_errs else float(alpha_target)
    proportional_term = float(kp) * (float(alpha_target) - local_rate)
    new_alpha = float(alpha_t) + integral_term + proportional_term
    return float(min(max(new_alpha, _EPS_ALPHA), 1.0 - _EPS_ALPHA))


@dataclass(frozen=True)
class AdaptiveCalibrationTrial:
    origin: float
    step: int
    alpha_t: float
    q: float
    lower: float
    upper: float
    observed: float
    covered: bool
    interval_score: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "origin": self.origin, "step": self.step, "alpha_t": self.alpha_t, "q": self.q,
            "lower": self.lower, "upper": self.upper, "observed": self.observed,
            "covered": self.covered, "interval_score": self.interval_score,
        }


@dataclass(frozen=True)
class AdaptiveCalibrationReport:
    predictor_name: str
    method: str
    alpha_target: float
    n_trials: int
    n_skipped_insufficient_lookback: int
    empirical_coverage_value: float
    mean_width: float
    mean_interval_score: float
    trials: Tuple[AdaptiveCalibrationTrial, ...]
    skipped_trials: Tuple[Dict[str, Any], ...]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "predictor_name": self.predictor_name,
            "method": self.method,
            "alpha_target": self.alpha_target,
            "nominal_coverage": 1.0 - self.alpha_target,
            "n_trials": self.n_trials,
            "n_skipped_insufficient_lookback": self.n_skipped_insufficient_lookback,
            "empirical_coverage": self.empirical_coverage_value,
            "mean_width": self.mean_width,
            "mean_interval_score": self.mean_interval_score,
            "trials": [t.to_dict() for t in self.trials],
            "skipped_trials": [dict(s) for s in self.skipped_trials],
        }


def _run_one_step_sequence(
    preds: Sequence[RawHorizonPrediction],
    *,
    step: int,
    step_size: float,
    alpha_target: float,
    method: str,
    gamma: float,
    gamma_i: float,
    kp: float,
    proportional_window: int,
) -> Tuple[List[AdaptiveCalibrationTrial], List[Dict[str, Any]]]:
    if method not in METHODS:
        raise ScopeViolationError(f"_run_one_step_sequence: unknown method {method!r}; must be one of {METHODS}")
    trials_sorted = sorted((p for p in preds if p.step == step), key=lambda p: p.origin)
    alpha_t = float(alpha_target)
    recent_errs: List[int] = []
    seen: List[Tuple[float, float]] = []  # (this score's own target_time, abs_residual)
    out_trials: List[AdaptiveCalibrationTrial] = []
    skipped: List[Dict[str, Any]] = []
    for p in trials_sorted:
        target_time = p.origin + step * step_size
        eligible = [abs_r for (t_time, abs_r) in seen if t_time <= p.origin]
        if len(eligible) < MIN_CAUSAL_SCORES:
            skipped.append({
                "origin": p.origin, "step": step, "reason": "insufficient_lookback",
                "n_time_eligible_scores": len(eligible), "min_required": MIN_CAUSAL_SCORES,
            })
            seen.append((target_time, abs(p.observed - p.predicted)))
            continue

        level = min(max(1.0 - alpha_t, 1e-6), 1.0 - 1e-6)
        q = float(np.quantile(eligible, level))
        lower, upper = p.predicted - q, p.predicted + q
        covered = lower <= p.observed <= upper
        err_t = 0 if covered else 1
        score = interval_score(lower, upper, p.observed, alpha_target)
        out_trials.append(AdaptiveCalibrationTrial(
            origin=p.origin, step=step, alpha_t=alpha_t, q=q, lower=lower, upper=upper,
            observed=p.observed, covered=covered, interval_score=score,
        ))

        recent_errs.append(err_t)
        if len(recent_errs) > proportional_window:
            recent_errs.pop(0)
        if method == "aci":
            alpha_t = aci_update_alpha(alpha_t, alpha_target, err_t, gamma)
        elif method == "pid":
            alpha_t = pid_update_alpha(
                alpha_t, alpha_target, err_t, gamma_i=gamma_i, recent_errs=recent_errs, kp=kp
            )
        # "rolling_reference": alpha_t stays fixed at alpha_target.

        seen.append((target_time, abs(p.observed - p.predicted)))

    return out_trials, skipped


def run_calibration_sequence(
    preds: Sequence[RawHorizonPrediction],
    *,
    step: int,
    step_size: float,
    alpha_target: float = DEFAULT_ALPHA_TARGET,
    method: str,
    gamma: float = 0.05,
    gamma_i: float = 0.05,
    kp: float = 0.05,
    proportional_window: int = 5,
) -> AdaptiveCalibrationReport:
    """Run one calibration method over one predictor's same-horizon-step trials, in time order."""
    if not (0.0 < float(alpha_target) < 1.0):
        raise ScopeViolationError(f"run_calibration_sequence: alpha_target must be in (0,1); got {alpha_target!r}")
    if not (float(step_size) > 0.0):
        raise ScopeViolationError(f"run_calibration_sequence: step_size must be > 0; got {step_size!r}")
    if int(proportional_window) < 1:
        raise ScopeViolationError(f"run_calibration_sequence: proportional_window must be >= 1; got {proportional_window!r}")

    out_trials, skipped = _run_one_step_sequence(
        preds, step=step, step_size=step_size, alpha_target=alpha_target, method=method,
        gamma=gamma, gamma_i=gamma_i, kp=kp, proportional_window=proportional_window,
    )
    if not out_trials:
        raise ScopeViolationError(
            f"run_calibration_sequence: step={step} method={method!r} produced zero calibrated "
            f"trials ({len(skipped)} skipped for insufficient lookback)"
        )
    intervals = [(t.lower, t.upper) for t in out_trials]
    observed_list = [t.observed for t in out_trials]
    return AdaptiveCalibrationReport(
        predictor_name="<single-step>",
        method=method,
        alpha_target=float(alpha_target),
        n_trials=len(out_trials),
        n_skipped_insufficient_lookback=len(skipped),
        empirical_coverage_value=empirical_coverage(intervals, observed_list),
        mean_width=float(np.mean([t.upper - t.lower for t in out_trials])),
        mean_interval_score=float(np.mean([t.interval_score for t in out_trials])),
        trials=tuple(out_trials),
        skipped_trials=tuple(skipped),
    )


def run_adaptive_calibration_comparison(
    raw_predictions: Dict[str, List[RawHorizonPrediction]],
    *,
    step_size: float,
    max_horizon_steps: int,
    alpha_target: float = DEFAULT_ALPHA_TARGET,
    gamma: float = 0.05,
    gamma_i: float = 0.05,
    kp: float = 0.05,
    proportional_window: int = 5,
) -> Dict[str, Dict[str, AdaptiveCalibrationReport]]:
    """For each predictor, run all of :data:`METHODS`, pooling all horizon steps
    into one headline report per (predictor, method) — same pooling convention as
    ``mechanistic_probabilistic_evaluation.leave_one_origin_out_intervals``.
    """
    out: Dict[str, Dict[str, AdaptiveCalibrationReport]] = {}
    for name, preds in raw_predictions.items():
        out[name] = {}
        for method in METHODS:
            all_trials: List[AdaptiveCalibrationTrial] = []
            all_skipped: List[Dict[str, Any]] = []
            for step in range(1, int(max_horizon_steps) + 1):
                if not any(p.step == step for p in preds):
                    continue
                trials, skipped = _run_one_step_sequence(
                    preds, step=step, step_size=step_size, alpha_target=alpha_target, method=method,
                    gamma=gamma, gamma_i=gamma_i, kp=kp, proportional_window=proportional_window,
                )
                all_trials.extend(trials)
                all_skipped.extend(skipped)
            if not all_trials:
                raise ScopeViolationError(
                    f"run_adaptive_calibration_comparison: {name!r}/{method!r} produced zero "
                    "trials across all horizon steps"
                )
            intervals = [(t.lower, t.upper) for t in all_trials]
            observed_list = [t.observed for t in all_trials]
            out[name][method] = AdaptiveCalibrationReport(
                predictor_name=name,
                method=method,
                alpha_target=float(alpha_target),
                n_trials=len(all_trials),
                n_skipped_insufficient_lookback=len(all_skipped),
                empirical_coverage_value=empirical_coverage(intervals, observed_list),
                mean_width=float(np.mean([t.upper - t.lower for t in all_trials])),
                mean_interval_score=float(np.mean([t.interval_score for t in all_trials])),
                trials=tuple(all_trials),
                skipped_trials=tuple(all_skipped),
            )
    return out


def run_energy_balance_calibration_comparison(
    co2_path: str | Path, temp_path: str | Path, *, alpha_target: float = DEFAULT_ALPHA_TARGET, **kwargs: Any
) -> Dict[str, Dict[str, AdaptiveCalibrationReport]]:
    years_all, Tobs_all, F_vals_all = _load_overlap_series(co2_path, temp_path)
    years_arr = np.array(years_all, dtype=float)
    predictor = _energy_balance_mechanistic_predictor_factory(years_all, F_vals_all)
    raw = raw_predictions_by_horizon_step(
        years_arr, Tobs_all,
        origins=ROLLING_ORIGIN_YEARS, max_horizon_steps=ROLLING_ORIGIN_HORIZON_YEARS, step_size=1.0,
        predictors={
            "persistence": _persistence_predictor,
            "expanding": _expanding_linear_predictor,
            "last30": _last_30_years_linear_predictor,
            "energy_balance_mechanistic": predictor,
        },
    )
    return run_adaptive_calibration_comparison(
        raw, step_size=1.0, max_horizon_steps=ROLLING_ORIGIN_HORIZON_YEARS, alpha_target=alpha_target, **kwargs
    )


def run_covid_renewal_calibration_comparison(
    data_path: str | Path, *, alpha_target: float = DEFAULT_ALPHA_TARGET, **kwargs: Any
) -> Dict[str, Dict[str, AdaptiveCalibrationReport]]:
    day_index, incidence, _dates = _covid_daily_series(data_path)
    raw = raw_predictions_by_horizon_step(
        day_index, incidence,
        origins=[float(o) for o in COVID_RENEWAL_ORIGINS_DAY_INDEX],
        max_horizon_steps=COVID_RENEWAL_HORIZON_DAYS, step_size=1.0,
        predictors={
            "persistence": _covid_persistence_predictor,
            "exponential_extrapolation": _covid_exponential_extrapolation_predictor,
            "renewal_constant_R": _covid_renewal_predictor_factory(),
        },
    )
    return run_adaptive_calibration_comparison(
        raw, step_size=1.0, max_horizon_steps=COVID_RENEWAL_HORIZON_DAYS, alpha_target=alpha_target, **kwargs
    )


__all__ = [
    "SOURCE", "SOURCE_ACI", "SOURCE_PID", "PID_SCOPE_NOTE", "METHODS", "DEFAULT_ALPHA_TARGET",
    "MIN_CAUSAL_SCORES",
    "AdaptiveCalibrationTrial", "AdaptiveCalibrationReport",
    "aci_update_alpha", "pid_update_alpha",
    "run_calibration_sequence", "run_adaptive_calibration_comparison",
    "run_energy_balance_calibration_comparison", "run_covid_renewal_calibration_comparison",
]
