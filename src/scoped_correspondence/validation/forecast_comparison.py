"""Paired forecast comparison with applicability-gated inference (Paket J1).

SCOPE_COMPOSITION_EVIDENCE_ROADMAP.md package J1, plan
``prompts/Answers/nicht_stationäre_Treiber/SCF_SCOPE_COMPOSITION_EVIDENCE_IMPLEMENTATION_PLAN.md``
section 7. Documentation: ``docs/forecast_comparison.md``.

Additive adapter around ``validation/rolling_origin.py``: it pairs the RAW
per-(origin, step) predictions of two models (``RawHorizonPrediction``)
instead of testing aggregated RMSE values, and it does not replace any
existing backtest report.

For a pre-declared loss ``L`` the paired loss differences are

    d_t = L(y_t, yhat_A,t) - L(y_t, yhat_B,t)

(negative mean -> A had lower mean loss in the evaluated design). The
Diebold--Mariano statistic uses a Bartlett (Newey--West) HAC estimate of
the long-run variance with the finite convention of plan section 7:

    gamma_l = (1/n) sum_{t=l+1}^{n} (d_t - dbar)(d_{t-l} - dbar)
    V       = gamma_0 + 2 sum_{l=1}^{L} (1 - l/(L+1)) gamma_l
    DM      = dbar / sqrt(V / n)

What this module does NOT claim:

- The normal reference is asymptotic and conditional on (approximate)
  stationarity / weak dependence and finite moments of ``d_t``. Those
  assumptions are DECLARED by the caller (``InferenceApplicability``);
  this module cannot prove them from data. Without a declared
  justification the inferential fields stay ``None`` and only the
  descriptive comparison is reported.
- DM is not a general model-selection test for nested or estimated
  models; nested models are refused for automatic inference.
- "No significant difference" is NOT demonstrated equivalence
  (``equivalence_tested`` is always ``False`` here).
- Different series (catchments, galaxies, ...) are never concatenated into
  one artificial time series: results are formed per (series_id, horizon).
- Zero or numerically unusable variance is ``degenerate_variance`` -- never
  ``p = 0`` and never an automatic winner.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from fractions import Fraction
from statistics import NormalDist
from typing import Callable, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple, Union

from scoped_correspondence.errors import ScopeViolationError
from scoped_correspondence.validation.rolling_origin import RawHorizonPrediction

Number = Union[int, float, Fraction]

#: Pre-declared loss functions. The loss is chosen BEFORE evaluation and
#: stored by name in every result; no arbitrary callable is accepted, so a
#: result can always be reproduced from its stored loss name.
LOSSES: Dict[str, Callable[[Number, Number], Number]] = {
    "squared_error": lambda y, p: (y - p) * (y - p),
    "absolute_error": lambda y, p: abs(y - p),
}

INFERENCE_STATUSES = ("asymptotic_normal_reference", "not_applicable", "degenerate_variance")

#: Relative numerical guard for "degenerate variance" with float inputs:
#: V <= _DEGENERATE_REL * mean(d^2) is treated as zero. Exact (Fraction)
#: inputs only ever use V <= 0. This is a numerical guard, not a statistic.
_DEGENERATE_REL = 1e-12


def _is_finite(x: Number) -> bool:
    if isinstance(x, Fraction) or isinstance(x, int):
        return True
    return isinstance(x, float) and math.isfinite(x)


# ----------------------------------------------------------------- pairing --


@dataclass(frozen=True)
class PairedForecastRecord:
    """One observation with BOTH models' predictions for the same target,
    the same horizon and the same information set (same forecast origin)."""

    series_id: str
    origin: float
    target_time: float
    horizon: int
    observed: Number
    prediction_a: Number
    prediction_b: Number
    model_a_id: str
    model_b_id: str
    data_id: str
    split_id: str

    def to_dict(self) -> Dict[str, object]:
        return {k: _json_number(v) for k, v in self.__dict__.items()}


@dataclass(frozen=True)
class PairingIssue:
    origin: float
    horizon: int
    reason: str

    def to_dict(self) -> Dict[str, object]:
        return {"origin": self.origin, "horizon": self.horizon, "reason": self.reason}


@dataclass(frozen=True)
class PairingReport:
    """Result of joining two models' raw predictions. Nothing is dropped
    silently: every requested point is either paired, excluded (missing
    partner) or invalid (non-finite value), each with a reason."""

    series_id: str
    records: Tuple[PairedForecastRecord, ...]
    n_requested_a: int
    n_requested_b: int
    n_paired: int
    excluded: Tuple[PairingIssue, ...]
    invalid: Tuple[PairingIssue, ...]

    def to_dict(self) -> Dict[str, object]:
        return {
            "series_id": self.series_id,
            "n_requested_a": self.n_requested_a,
            "n_requested_b": self.n_requested_b,
            "n_paired": self.n_paired,
            "excluded": [i.to_dict() for i in self.excluded],
            "invalid": [i.to_dict() for i in self.invalid],
        }


def _index_raw(raw: Sequence[RawHorizonPrediction], side: str) -> Dict[Tuple[float, int], RawHorizonPrediction]:
    out: Dict[Tuple[float, int], RawHorizonPrediction] = {}
    for r in raw:
        key = (float(r.origin), int(r.step))
        if key in out:
            raise ScopeViolationError(f"pair_raw_predictions: duplicate (origin, step)={key!r} in model {side}")
        out[key] = r
    return out


def pair_raw_predictions(
    raw_a: Sequence[RawHorizonPrediction],
    raw_b: Sequence[RawHorizonPrediction],
    *,
    series_id: str,
    model_a_id: str,
    model_b_id: str,
    data_id: str,
    split_id: str,
    step_size: float,
) -> PairingReport:
    """Join two models' ``RawHorizonPrediction`` lists on (origin, step).

    - A key present on only one side is EXCLUDED with reason
      ``missing_partner_in_model_a``/``..._b`` -- counted, not dropped silently.
    - Different observed values under the same key are an INPUT ERROR
      (``ScopeViolationError``): the two predictions would not refer to the
      same observation.
    - A non-finite observed value or prediction makes the point INVALID
      (reason ``non_finite_value``).
    """
    if not series_id or not model_a_id or not model_b_id:
        raise ScopeViolationError("pair_raw_predictions: series_id and both model ids are required")
    if model_a_id == model_b_id:
        raise ScopeViolationError("pair_raw_predictions: model_a_id and model_b_id must differ")
    if not (isinstance(step_size, (int, float)) and math.isfinite(step_size) and step_size > 0):
        raise ScopeViolationError("pair_raw_predictions: step_size must be finite and > 0")
    ia = _index_raw(raw_a, "A")
    ib = _index_raw(raw_b, "B")
    records: List[PairedForecastRecord] = []
    excluded: List[PairingIssue] = []
    invalid: List[PairingIssue] = []
    for key in sorted(set(ia) | set(ib)):
        origin, step = key
        if key not in ib:
            excluded.append(PairingIssue(origin, step, "missing_partner_in_model_b"))
            continue
        if key not in ia:
            excluded.append(PairingIssue(origin, step, "missing_partner_in_model_a"))
            continue
        a, b = ia[key], ib[key]
        values = (a.observed, b.observed, a.predicted, b.predicted)
        if not all(_is_finite(v) for v in values):
            invalid.append(PairingIssue(origin, step, "non_finite_value"))
            continue
        if a.observed != b.observed:
            raise ScopeViolationError(
                f"pair_raw_predictions: observed values differ at (origin, step)={key!r}: "
                f"{a.observed!r} vs {b.observed!r} -- not the same observation"
            )
        records.append(
            PairedForecastRecord(
                series_id=series_id,
                origin=origin,
                target_time=origin + step * step_size,
                horizon=step,
                observed=a.observed,
                prediction_a=a.predicted,
                prediction_b=b.predicted,
                model_a_id=model_a_id,
                model_b_id=model_b_id,
                data_id=data_id,
                split_id=split_id,
            )
        )
    return PairingReport(
        series_id=series_id,
        records=tuple(records),
        n_requested_a=len(ia),
        n_requested_b=len(ib),
        n_paired=len(records),
        excluded=tuple(excluded),
        invalid=tuple(invalid),
    )


# ------------------------------------------------------------- inference ---


@dataclass(frozen=True)
class InferenceApplicability:
    """The caller's DECLARATION of whether the DM asymptotics may be used.

    This is an assumption with provenance, not something this module
    verifies. ``min_series_length`` has no default on purpose: what counts
    as "long enough" is a design decision of the comparison, not a
    universal constant (plan section 19.2: no invented numbers).
    """

    declared_justified: bool
    justification: str
    min_series_length: int
    nested_models: bool = False
    structural_break_suspected: bool = False
    temporal_order_clear: bool = True

    def __post_init__(self) -> None:
        if self.declared_justified and not self.justification.strip():
            raise ScopeViolationError("InferenceApplicability: a declared justification needs a nonempty text")
        if not isinstance(self.min_series_length, int) or self.min_series_length < 2:
            raise ScopeViolationError("InferenceApplicability: min_series_length must be an int >= 2")

    def to_dict(self) -> Dict[str, object]:
        return dict(self.__dict__)


def bartlett_hac_long_run_variance(d: Sequence[Number], lag: int) -> Number:
    """Bartlett/Newey--West long-run variance with the finite convention of
    plan section 7 (divisor ``n`` for every autocovariance). Works exactly
    for ``Fraction`` inputs. ``lag`` must satisfy ``0 <= lag < n``."""
    n = len(d)
    if n < 2:
        raise ScopeViolationError("bartlett_hac_long_run_variance: need at least 2 values")
    if not isinstance(lag, int) or isinstance(lag, bool) or lag < 0 or lag >= n:
        raise ScopeViolationError(f"bartlett_hac_long_run_variance: lag must be an int with 0 <= lag < n={n}, got {lag!r}")
    if not all(_is_finite(x) for x in d):
        raise ScopeViolationError("bartlett_hac_long_run_variance: non-finite value")
    mean = sum(d) / n
    dev = [x - mean for x in d]

    def gamma(l: int) -> Number:
        return sum(dev[t] * dev[t - l] for t in range(l, n)) / n

    v = gamma(0)
    for l in range(1, lag + 1):
        weight = 1 - Fraction(l, lag + 1)
        if not isinstance(v, Fraction) and not isinstance(v, int):
            weight = float(weight)
        v = v + 2 * weight * gamma(l)
    return v


@dataclass(frozen=True)
class PairedComparisonResult:
    """One comparison per (series_id, horizon). Descriptive and inferential
    fields are separate: the descriptive part is always filled, the
    inferential part only under ``inference_status ==
    'asymptotic_normal_reference'``."""

    series_id: str
    horizon: int
    loss: str
    model_a_id: str
    model_b_id: str
    data_id: str
    split_id: str
    n: int
    first_origin: float
    last_origin: float
    mean_loss_a: Number
    mean_loss_b: Number
    mean_loss_difference: Number
    descriptive_direction: str
    hac_lag: int
    lag_justification: str
    applicability: InferenceApplicability
    inference_status: str
    inference_reasons: Tuple[str, ...]
    long_run_variance: Optional[Number]
    standard_error: Optional[float]
    dm_statistic: Optional[float]
    p_value_two_sided: Optional[float]
    confidence_level: float
    confidence_interval: Optional[Tuple[float, float]]
    equivalence_tested: bool = False
    notes: Tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if self.inference_status not in INFERENCE_STATUSES:
            raise ValueError(f"inference_status must be one of {INFERENCE_STATUSES}")

    def to_dict(self) -> Dict[str, object]:
        out: Dict[str, object] = {}
        for k, v in self.__dict__.items():
            if k == "applicability":
                out[k] = v.to_dict()
            elif k == "confidence_interval" and v is not None:
                out[k] = [_json_number(x) for x in v]
            else:
                out[k] = _json_number(v) if not isinstance(v, tuple) else list(v)
        return out


def _json_number(v):
    if isinstance(v, Fraction):
        return {"numerator": v.numerator, "denominator": v.denominator}
    if isinstance(v, float) and not math.isfinite(v):
        raise ValueError("refusing to serialize a non-finite float (plan section 5.2)")
    return v


def _direction(mean_diff: Number) -> str:
    if mean_diff < 0:
        return "A_lower_mean_loss"
    if mean_diff > 0:
        return "B_lower_mean_loss"
    return "equal_mean_loss"


def _group(records: Iterable[PairedForecastRecord]) -> Dict[Tuple[str, int], List[PairedForecastRecord]]:
    groups: Dict[Tuple[str, int], List[PairedForecastRecord]] = {}
    for r in records:
        groups.setdefault((r.series_id, r.horizon), []).append(r)
    return groups


def compare_paired_forecasts(
    records: Sequence[PairedForecastRecord],
    *,
    loss: str,
    hac_lag: int,
    lag_justification: str,
    applicability: InferenceApplicability,
    confidence_level: float = 0.95,
) -> Tuple[PairedComparisonResult, ...]:
    """Compare model A against model B separately for every
    (series_id, horizon) present in ``records``; returns the results sorted
    by that key. Overlapping horizons are never pooled into one sample.

    Input errors (``ScopeViolationError``): unknown loss, empty records,
    mixed model/data/split ids within one group, duplicate origins within one
    group, non-finite values, missing lag justification, invalid level.
    """
    if loss not in LOSSES:
        raise ScopeViolationError(f"compare_paired_forecasts: loss must be one of {sorted(LOSSES)}, got {loss!r}")
    if not records:
        raise ScopeViolationError("compare_paired_forecasts: no records")
    if not lag_justification.strip():
        raise ScopeViolationError("compare_paired_forecasts: the HAC lag choice must be justified in text")
    if not (0.0 < confidence_level < 1.0):
        raise ScopeViolationError("compare_paired_forecasts: confidence_level must be in (0, 1)")
    loss_fn = LOSSES[loss]
    results: List[PairedComparisonResult] = []
    for (series_id, horizon), group in sorted(_group(records).items()):
        ids = {(r.model_a_id, r.model_b_id, r.data_id, r.split_id) for r in group}
        if len(ids) != 1:
            raise ScopeViolationError(f"compare_paired_forecasts: mixed model/data/split ids within series {series_id!r}, horizon {horizon}")
        group = sorted(group, key=lambda r: r.origin)
        origins = [r.origin for r in group]
        if len(set(origins)) != len(origins):
            raise ScopeViolationError(f"compare_paired_forecasts: duplicate origin within series {series_id!r}, horizon {horizon}")
        for r in group:
            if not all(_is_finite(v) for v in (r.observed, r.prediction_a, r.prediction_b)):
                raise ScopeViolationError("compare_paired_forecasts: non-finite value in records (use pair_raw_predictions to report them)")
        la = [loss_fn(r.observed, r.prediction_a) for r in group]
        lb = [loss_fn(r.observed, r.prediction_b) for r in group]
        d = [x - y for x, y in zip(la, lb)]
        n = len(d)
        mean_a, mean_b, mean_d = sum(la) / n, sum(lb) / n, sum(d) / n
        model_a_id, model_b_id, data_id, split_id = next(iter(ids))

        reasons: List[str] = []
        if not applicability.declared_justified:
            reasons.append("applicability_not_declared")
        if applicability.nested_models:
            reasons.append("nested_models")
        if applicability.structural_break_suspected:
            reasons.append("structural_break_suspected")
        if not applicability.temporal_order_clear:
            reasons.append("temporal_order_unclear")
        if n < applicability.min_series_length:
            reasons.append(f"series_too_short(n={n}<{applicability.min_series_length})")
        if hac_lag >= n:
            reasons.append(f"lag_not_smaller_than_n(lag={hac_lag},n={n})")

        V: Optional[Number] = None
        se = dm = p = None
        ci = None
        status = "not_applicable"
        if not reasons:
            V = bartlett_hac_long_run_variance(d, hac_lag)
            exact = all(isinstance(x, (Fraction, int)) for x in d)
            scale = sum(x * x for x in d) / n
            degenerate = V <= 0 if exact else (not math.isfinite(float(V)) or float(V) <= _DEGENERATE_REL * float(scale))
            if degenerate:
                status = "degenerate_variance"
                reasons.append("long_run_variance_zero_or_numerically_unusable")
            else:
                status = "asymptotic_normal_reference"
                se = math.sqrt(float(V) / n)
                dm = float(mean_d) / se
                p = math.erfc(abs(dm) / math.sqrt(2.0))
                z = NormalDist().inv_cdf(0.5 + confidence_level / 2.0)
                ci = (float(mean_d) - z * se, float(mean_d) + z * se)
        results.append(
            PairedComparisonResult(
                series_id=series_id,
                horizon=horizon,
                loss=loss,
                model_a_id=model_a_id,
                model_b_id=model_b_id,
                data_id=data_id,
                split_id=split_id,
                n=n,
                first_origin=group[0].origin,
                last_origin=group[-1].origin,
                mean_loss_a=mean_a,
                mean_loss_b=mean_b,
                mean_loss_difference=mean_d,
                descriptive_direction=_direction(mean_d),
                hac_lag=hac_lag,
                lag_justification=lag_justification,
                applicability=applicability,
                inference_status=status,
                inference_reasons=tuple(reasons),
                long_run_variance=V,
                standard_error=se,
                dm_statistic=dm,
                p_value_two_sided=p,
                confidence_level=confidence_level,
                confidence_interval=ci,
                notes=(
                    "negative mean_loss_difference favours model A in the evaluated design only",
                    "no significant difference is not demonstrated equivalence",
                ),
            )
        )
    return tuple(results)


# ------------------------------------------------------- multiple testing --


def holm_adjust(p_values: Sequence[Number]) -> List[Number]:
    """Holm (1979) step-down adjusted p-values, returned in ORIGINAL order.
    Exact for ``Fraction`` inputs. Values are capped at 1."""
    m = len(p_values)
    if m == 0:
        raise ScopeViolationError("holm_adjust: empty family")
    for p in p_values:
        if not _is_finite(p) or p < 0 or p > 1:
            raise ScopeViolationError(f"holm_adjust: p-values must lie in [0, 1], got {p!r}")
    order = sorted(range(m), key=lambda i: p_values[i])
    adjusted: List[Number] = [0] * m
    running: Number = 0
    for k, i in enumerate(order):
        candidate = (m - k) * p_values[i]
        candidate = min(candidate, 1)
        running = max(running, candidate)
        adjusted[i] = running
    return adjusted


@dataclass(frozen=True)
class DeclaredTestFamily:
    """A family of comparisons declared BEFORE evaluation. Members are
    (series_id, horizon) keys. A single p-value from an exploratory
    best-of-many search is not repaired by this correction."""

    family_id: str
    members: Tuple[Tuple[str, int], ...]
    declared_before_evaluation: bool
    description: str = ""

    def __post_init__(self) -> None:
        if not self.members:
            raise ScopeViolationError("DeclaredTestFamily: needs at least one member")
        if len(set(self.members)) != len(self.members):
            raise ScopeViolationError("DeclaredTestFamily: duplicate members")


@dataclass(frozen=True)
class HolmFamilyReport:
    family_id: str
    status: str  # "adjusted" | "incomplete_family" | "not_predeclared"
    members: Tuple[Tuple[str, int], ...]
    raw_p_values: Tuple[Optional[float], ...]
    adjusted_p_values: Optional[Tuple[float, ...]]
    members_without_inference: Tuple[Tuple[str, int], ...]


def holm_adjust_family(results: Sequence[PairedComparisonResult], family: DeclaredTestFamily) -> HolmFamilyReport:
    """Apply Holm to exactly the declared family. Results outside the family
    or family members without a result are input errors (no post-hoc
    selection of which comparisons count). Members whose inference was not
    applicable make the family ``incomplete_family`` -- no adjusted values
    are produced rather than silently shrinking the family."""
    by_key = {(r.series_id, r.horizon): r for r in results}
    if len(by_key) != len(results):
        raise ScopeViolationError("holm_adjust_family: duplicate (series_id, horizon) in results")
    extra = set(by_key) - set(family.members)
    missing = set(family.members) - set(by_key)
    if extra or missing:
        raise ScopeViolationError(f"holm_adjust_family: results must match the declared family exactly (extra={sorted(extra)}, missing={sorted(missing)})")
    raw = tuple(by_key[k].p_value_two_sided for k in family.members)
    without = tuple(k for k, p in zip(family.members, raw) if p is None)
    if not family.declared_before_evaluation:
        return HolmFamilyReport(family.family_id, "not_predeclared", family.members, raw, None, without)
    if without:
        return HolmFamilyReport(family.family_id, "incomplete_family", family.members, raw, None, without)
    return HolmFamilyReport(family.family_id, "adjusted", family.members, raw, tuple(holm_adjust(list(raw))), ())


# ------------------------------------------------------------ reporting ---


def describe_comparison(result: PairedComparisonResult) -> str:
    """A sentence that always names series/period, horizon, loss, effect size
    and inference status (plan section 7, Abnahme) -- there is no shorter
    'winner' formulation in this module."""
    period = f"origins {result.first_origin:g}..{result.last_origin:g}"
    effect = float(result.mean_loss_difference)
    head = (
        f"Series {result.series_id!r} ({period}, n={result.n}), horizon {result.horizon}, loss {result.loss}: "
        f"mean loss difference {result.model_a_id} - {result.model_b_id} = {effect:.6g} "
        f"({result.descriptive_direction})."
    )
    if result.inference_status == "asymptotic_normal_reference":
        lo, hi = result.confidence_interval  # type: ignore[misc]
        tail = (
            f" Inference: asymptotic normal reference under DECLARED applicability; DM={result.dm_statistic:.4g}, "
            f"two-sided p={result.p_value_two_sided:.4g}, {result.confidence_level:.0%} CI [{lo:.6g}, {hi:.6g}], "
            f"Bartlett HAC lag {result.hac_lag}. Not an equivalence test."
        )
    else:
        tail = f" Inference: {result.inference_status} ({', '.join(result.inference_reasons)}); descriptive comparison only."
    return head + tail


__all__ = [
    "LOSSES",
    "INFERENCE_STATUSES",
    "PairedForecastRecord",
    "PairingIssue",
    "PairingReport",
    "pair_raw_predictions",
    "InferenceApplicability",
    "bartlett_hac_long_run_variance",
    "PairedComparisonResult",
    "compare_paired_forecasts",
    "holm_adjust",
    "DeclaredTestFamily",
    "HolmFamilyReport",
    "holm_adjust_family",
    "describe_comparison",
]
