"""Weighted split conformal prediction under covariate shift (Paket J8, plan §14).

Setting (Tibshirani, Barber, Candes & Ramdas 2019, S13): a predictor fixed
on a SEPARATE training set; calibration points i.i.d. from P; an independent
test point from Q with P(Y|X) = Q(Y|X) and Q_X << P_X; weights
w = dQ_X / dP_X known up to a positive factor. At a test point x:

    q(x) = Quantile_{1-alpha}( sum_i w(X_i)/(sum_j w(X_j) + w(x)) delta_{R_i}
                               + w(x)/(sum_j w(X_j) + w(x)) delta_{+inf} )

with the convention: the smallest score r whose cumulative normalised mass
reaches 1 - alpha (ties at the threshold resolve to that r). The test point's
own mass sits at +infinity and is NEVER omitted. For absolute residuals the
interval is [f(x) - q, f(x) + q]; q = +inf means the WHOLE REAL LINE (not an
empty interval).

The guarantee is MARGINAL over calibration and test point, not conditional
on a fixed x. It is inherited only for correct (known) weights:

- estimated weights -> ``guarantee_status = "not_inherited_estimated_weights"``;
- clipped weights   -> ``"not_inherited_procedure_changed"``;
- temporal autocorrelation or concept shift (P(Y|X) != Q(Y|X)) are not
  repaired by reweighting covariates.

Exact ``Fraction`` inputs give exact quantiles. Unbounded results are
reported with the explicit marker ``{"kind": "whole_real_line"}`` in JSON.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from fractions import Fraction
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

from scoped_correspondence.errors import ScopeViolationError

Num = Union[int, float, Fraction]
POSITIVE_INFINITY = {"kind": "positive_infinity"}
WHOLE_REAL_LINE = {"kind": "whole_real_line"}


def _finite_nonneg(x, what) -> Num:
    if isinstance(x, bool) or not isinstance(x, (int, float, Fraction)):
        raise ScopeViolationError(f"{what} must be a real number")
    if isinstance(x, float) and not math.isfinite(x):
        raise ScopeViolationError(f"{what} must be finite")
    if x < 0:
        raise ScopeViolationError(f"{what} must be >= 0")
    return x


def weighted_split_quantile(scores: Sequence[Num], calibration_weights: Sequence[Num], test_weight: Num, alpha: Num) -> Optional[Num]:
    """Returns the weighted conformal quantile, or None for +infinity."""
    if len(scores) != len(calibration_weights):
        raise ScopeViolationError("one weight per calibration score")
    if not (0 < alpha < 1):
        raise ScopeViolationError("alpha must lie in (0, 1)")
    for s in scores:
        if isinstance(s, float) and not math.isfinite(s):
            raise ScopeViolationError("scores must be finite")
    ws = [_finite_nonneg(w, "calibration weight") for w in calibration_weights]
    tw = _finite_nonneg(test_weight, "test weight")
    if tw <= 0:
        raise ScopeViolationError("the evaluated test point needs a positive weight (support condition Q_X << P_X)")
    total = sum(ws) + tw
    need = (1 - alpha) * total
    cum = 0
    for s, w in sorted(zip(scores, ws), key=lambda t: t[0]):
        cum += w
        if cum >= need:
            return s
    return None


@dataclass(frozen=True)
class WeightedConformalReport:
    alpha: Num
    weight_provenance: str  # "known_density_ratio" | "estimated"
    clipped: bool
    guarantee_status: str
    n_calibration: int
    effective_sample_size: float
    max_normalised_weight: float
    unbounded_fraction: Optional[float]
    empirical_coverage: Optional[float]
    mean_finite_width: Optional[float]
    intervals: Tuple[Any, ...]
    notes: Tuple[str, ...] = field(default_factory=tuple)


def _ess(ws: Sequence[float]) -> float:
    s, s2 = sum(ws), sum(w * w for w in ws)
    return 0.0 if s2 == 0 else s * s / s2


def weighted_conformal_intervals(
    cal_residuals: Sequence[float], cal_weights: Sequence[float], test_predictions: Sequence[float], test_weights: Sequence[float],
    alpha: float, *, weight_provenance: str, train_ids: Sequence = (), calibration_ids: Sequence = (),
    clip_at: Optional[float] = None, test_observed: Optional[Sequence[float]] = None,
) -> WeightedConformalReport:
    """Intervals for every test point plus the application report.

    ``train_ids`` / ``calibration_ids``: the training and calibration sets must
    be disjoint (the predictor is fixed on a separate set)."""
    if weight_provenance not in ("known_density_ratio", "estimated"):
        raise ScopeViolationError("weight_provenance must be 'known_density_ratio' or 'estimated'")
    if set(train_ids) & set(calibration_ids):
        raise ScopeViolationError("training and calibration sets overlap: the split-conformal guarantee needs separation")
    if len(test_predictions) != len(test_weights):
        raise ScopeViolationError("one weight per test point")
    cw = list(cal_weights)
    tws = list(test_weights)
    if clip_at is not None:
        cw = [min(w, clip_at) for w in cw]
        tws = [min(w, clip_at) for w in tws]
    intervals: List[Any] = []
    n_unb, widths, covered = 0, [], 0
    for k, (yhat, tw) in enumerate(zip(test_predictions, tws)):
        q = weighted_split_quantile(cal_residuals, cw, tw, alpha)
        if q is None:
            n_unb += 1
            intervals.append(WHOLE_REAL_LINE)
            if test_observed is not None:
                covered += 1
        else:
            intervals.append((yhat - q, yhat + q))
            widths.append(2 * q)
            if test_observed is not None and yhat - q <= test_observed[k] <= yhat + q:
                covered += 1
    status = ("inherited_under_stated_assumptions" if weight_provenance == "known_density_ratio" and clip_at is None
              else "not_inherited_procedure_changed" if clip_at is not None else "not_inherited_estimated_weights")
    total = sum(float(w) for w in cw)
    notes = ["marginal coverage over calibration and test point; not conditional on a fixed x",
             "requires P(Y|X) = Q(Y|X); reweighting covariates does not repair concept shift or autocorrelation"]
    n_test = len(test_predictions)
    return WeightedConformalReport(
        alpha, weight_provenance, clip_at is not None, status, len(cal_residuals), _ess([float(w) for w in cw]),
        0.0 if total == 0 else max(float(w) for w in cw) / total,
        None if n_test == 0 else n_unb / n_test,
        None if test_observed is None or n_test == 0 else covered / n_test,
        None if not widths else float(sum(widths)) / len(widths),
        tuple(intervals), tuple(notes))


__all__ = ["POSITIVE_INFINITY", "WHOLE_REAL_LINE", "weighted_split_quantile", "WeightedConformalReport", "weighted_conformal_intervals"]
