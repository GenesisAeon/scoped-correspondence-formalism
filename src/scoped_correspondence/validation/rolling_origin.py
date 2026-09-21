"""Rolling-origin backtesting utility (Milestone 6e; NONSTATIONARY_ROADMAP.md package 1).

Generic evaluation harness: given a time-indexed series, a set of forecast
origins, and a horizon, repeatedly split into (data up to and including the
origin) vs. (the next ``horizon`` x-units), call each named predictor
function on the calib slice, and pool the resulting per-origin squared
errors into one RMSE per predictor across ALL origins together.

This implements the evaluation protocol from
``prompts/Answers/nicht_stationäre_Treiber/SCF_Nichtstationaere_Treiber_und_Kippen.md``
section 7 ("Zeitlich rollierend auswerten", Astra, 2026-09-21): a single
train/test split (as used in the original Cygnus/COVID/NOAA/earthquake
pilots) stays useful and honest for those pilots' own disclosed results,
but a materially more robust comparison between competing simple models
needs MANY origins, not one -- otherwise "model beats baseline" or vice
versa can depend heavily on which single split happened to be chosen.

Predictors receive ONLY the calib slice (x, y with x <= origin) -- the
test slice is never passed to a predictor callable, enforced by
construction (not by convention in the predictor's own docstring).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List, Sequence, Tuple

import numpy as np

from scoped_correspondence.errors import ScopeViolationError
from scoped_correspondence.validation.core import rmse

Predictor = Callable[[np.ndarray, np.ndarray, np.ndarray], np.ndarray]


@dataclass(frozen=True)
class OriginResult:
    origin: float
    n_calib: int
    n_test: int
    rmse_by_predictor: Dict[str, float]

    def to_dict(self) -> Dict[str, object]:
        return {
            "origin": self.origin,
            "n_calib": self.n_calib,
            "n_test": self.n_test,
            "rmse_by_predictor": dict(self.rmse_by_predictor),
        }


@dataclass(frozen=True)
class RollingOriginReport:
    origins: Tuple[float, ...]
    horizon: float
    predictor_names: Tuple[str, ...]
    per_origin: Tuple[OriginResult, ...]
    pooled_rmse: Dict[str, float]

    def to_dict(self) -> Dict[str, object]:
        return {
            "origins": list(self.origins),
            "horizon": self.horizon,
            "predictor_names": list(self.predictor_names),
            "per_origin": [r.to_dict() for r in self.per_origin],
            "pooled_rmse": dict(self.pooled_rmse),
        }


def rolling_origin_backtest(
    x: Sequence[float],
    y: Sequence[float],
    *,
    origins: Sequence[float],
    horizon: float,
    predictors: Dict[str, Predictor],
) -> RollingOriginReport:
    """Evaluate each predictor at every origin; pool RMSE across all test points.

    ``x``, ``y``: the full series, sorted strictly ascending by ``x``.
    ``origins``: candidate forecast origins; each must be a value present
    in ``x``. ``horizon``: the test window at a given origin is
    ``(origin, origin + horizon]`` in ``x``-units. ``predictors[name](calib_x,
    calib_y, test_x) -> predicted y at test_x``; each predictor sees ONLY
    the calib slice (``x <= origin``), never ``test_x``'s corresponding
    ``y`` values, and never any ``x`` beyond the origin.
    """
    x_arr = np.asarray(x, dtype=float)
    y_arr = np.asarray(y, dtype=float)
    if x_arr.shape != y_arr.shape:
        raise ScopeViolationError("rolling_origin_backtest: x and y must have the same shape")
    if x_arr.ndim != 1 or x_arr.size < 2:
        raise ScopeViolationError("rolling_origin_backtest: x must be a 1D series with >= 2 points")
    if not np.all(np.diff(x_arr) > 0):
        raise ScopeViolationError("rolling_origin_backtest: x must be strictly increasing")
    if not predictors:
        raise ScopeViolationError("rolling_origin_backtest: need at least one predictor")
    if horizon <= 0:
        raise ScopeViolationError("rolling_origin_backtest: horizon must be > 0")
    if not origins:
        raise ScopeViolationError("rolling_origin_backtest: need at least one origin")

    per_origin: List[OriginResult] = []
    pooled_sq_err: Dict[str, List[float]] = {name: [] for name in predictors}
    for origin in origins:
        if not np.any(x_arr == origin):
            raise ScopeViolationError(f"rolling_origin_backtest: origin {origin!r} not present in x")
        calib_mask = x_arr <= origin
        test_mask = (x_arr > origin) & (x_arr <= origin + horizon)
        n_calib = int(calib_mask.sum())
        n_test = int(test_mask.sum())
        if n_calib < 2:
            raise ScopeViolationError(f"rolling_origin_backtest: origin {origin!r} has < 2 calib points")
        if n_test == 0:
            raise ScopeViolationError(
                f"rolling_origin_backtest: origin {origin!r} has no test points within horizon {horizon!r}"
            )
        calib_x = x_arr[calib_mask]
        calib_y = y_arr[calib_mask]
        test_x = x_arr[test_mask]
        test_y = y_arr[test_mask]
        rmse_by_predictor: Dict[str, float] = {}
        for name, fn in predictors.items():
            pred = np.asarray(fn(calib_x, calib_y, test_x), dtype=float)
            if pred.shape != test_x.shape:
                raise ScopeViolationError(
                    f"rolling_origin_backtest: predictor {name!r} must return one prediction per test point"
                )
            rmse_by_predictor[name] = rmse(test_y, pred)
            pooled_sq_err[name].extend(((test_y - pred) ** 2).tolist())
        per_origin.append(
            OriginResult(origin=float(origin), n_calib=n_calib, n_test=n_test, rmse_by_predictor=rmse_by_predictor)
        )

    pooled_rmse = {name: float(np.sqrt(np.mean(errs))) for name, errs in pooled_sq_err.items()}
    return RollingOriginReport(
        origins=tuple(float(o) for o in origins),
        horizon=float(horizon),
        predictor_names=tuple(predictors.keys()),
        per_origin=tuple(per_origin),
        pooled_rmse=pooled_rmse,
    )


@dataclass(frozen=True)
class HorizonStepReport:
    steps: Tuple[int, ...]
    predictor_names: Tuple[str, ...]
    rmse_by_step: Dict[str, Dict[int, float]]

    def to_dict(self) -> Dict[str, object]:
        return {
            "steps": list(self.steps),
            "predictor_names": list(self.predictor_names),
            "rmse_by_step": {name: dict(by_step) for name, by_step in self.rmse_by_step.items()},
        }


def error_by_horizon_step(
    x: Sequence[float],
    y: Sequence[float],
    *,
    origins: Sequence[float],
    max_horizon_steps: int,
    step_size: float,
    predictors: Dict[str, Predictor],
) -> HorizonStepReport:
    """Pool squared error SEPARATELY per horizon step (1, 2, ..., max_horizon_steps).

    MECHANISTIC_VALIDATION_ROADMAP.md package 2, response to Astra's
    2026-09-21 review: :func:`rolling_origin_backtest` pools ALL test
    points within a horizon window into one RMSE per predictor per origin
    -- this additive, non-destructive companion instead evaluates each
    predictor at exactly ONE future point ``origin + k*step_size`` for
    each step ``k=1..max_horizon_steps``, separately, and pools across
    origins WITHIN each step. Requires ``x`` to actually contain each
    ``origin + k*step_size`` point queried (a ``ScopeViolationError`` is
    raised otherwise, same anti-guessing discipline as
    ``rolling_origin_backtest``). ``rolling_origin_backtest`` itself is
    untouched by this addition.
    """
    x_arr = np.asarray(x, dtype=float)
    y_arr = np.asarray(y, dtype=float)
    if x_arr.shape != y_arr.shape:
        raise ScopeViolationError("error_by_horizon_step: x and y must have the same shape")
    if not np.all(np.diff(x_arr) > 0):
        raise ScopeViolationError("error_by_horizon_step: x must be strictly increasing")
    if not predictors:
        raise ScopeViolationError("error_by_horizon_step: need at least one predictor")
    if max_horizon_steps < 1:
        raise ScopeViolationError("error_by_horizon_step: max_horizon_steps must be >= 1")
    if step_size <= 0:
        raise ScopeViolationError("error_by_horizon_step: step_size must be > 0")
    if not origins:
        raise ScopeViolationError("error_by_horizon_step: need at least one origin")

    pooled_sq_err: Dict[str, Dict[int, List[float]]] = {name: {k: [] for k in range(1, max_horizon_steps + 1)} for name in predictors}
    for origin in origins:
        if not np.any(x_arr == origin):
            raise ScopeViolationError(f"error_by_horizon_step: origin {origin!r} not present in x")
        calib_mask = x_arr <= origin
        calib_x = x_arr[calib_mask]
        calib_y = y_arr[calib_mask]
        for k in range(1, max_horizon_steps + 1):
            target_x = origin + k * step_size
            matches = np.where(np.isclose(x_arr, target_x, atol=1e-9))[0]
            if len(matches) == 0:
                raise ScopeViolationError(f"error_by_horizon_step: step target {target_x!r} (origin={origin!r}, k={k!r}) not present in x")
            test_x = x_arr[matches[:1]]
            test_y = y_arr[matches[:1]]
            for name, fn in predictors.items():
                pred = np.asarray(fn(calib_x, calib_y, test_x), dtype=float)
                if pred.shape != test_x.shape:
                    raise ScopeViolationError(f"error_by_horizon_step: predictor {name!r} must return one prediction per test point")
                pooled_sq_err[name][k].append(float((test_y[0] - pred[0]) ** 2))

    rmse_by_step = {
        name: {k: float(np.sqrt(np.mean(errs))) for k, errs in by_step.items()} for name, by_step in pooled_sq_err.items()
    }
    return HorizonStepReport(
        steps=tuple(range(1, max_horizon_steps + 1)),
        predictor_names=tuple(predictors.keys()),
        rmse_by_step=rmse_by_step,
    )


__all__ = ["OriginResult", "RollingOriginReport", "rolling_origin_backtest", "HorizonStepReport", "error_by_horizon_step"]
