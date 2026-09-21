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


__all__ = ["OriginResult", "RollingOriginReport", "rolling_origin_backtest"]
