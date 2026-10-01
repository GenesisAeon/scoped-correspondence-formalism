"""Split conformal prediction (Milestone 13).

Implements the split / inductive conformal quantile of Lei et al. 2018
(DOI 10.1080/01621459.2017.1307116) for absolute residuals. Coverage is
**marginal under exchangeability** of the calibration scores and the test
score — never claimed as guaranteed / exact / conditional.

This module is intentionally Cygnus-agnostic: it does not call
``validation.core`` APIs and does not mutate ``validation/core.py``.
Anti-leak discipline mirrors ``split_epochs`` (M6): calib and holdout
index sets must be disjoint (``VAL-CONF-LEAK-001``).
"""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from fractions import Fraction
from typing import Any, Dict, Optional, Sequence, Tuple

from scoped_correspondence.errors import ScopeViolationError

COVERAGE_MARGINAL_EXCHANGEABLE = "marginal_exchangeable"

_SOURCE = (
    "Lei, G'Sell, Rinaldo, Tibshirani & Wasserman 2018, "
    "Distribution-Free Predictive Inference for Regression, "
    "JASA; DOI 10.1080/01621459.2017.1307116"
)

_DEFAULT_ASSUMPTIONS: Tuple[str, ...] = (
    "coverage is marginal under exchangeability of calib residuals and the "
    "test residual — NOT conditional coverage",
    "coverage_kind is 'marginal_exchangeable' — NOT 'guaranteed' / 'exact'",
    "finite-sample +1 / ceiling order statistic: "
    "k = ceil((n+1)(1-alpha)); naive empirical (1-alpha)-quantile of the n "
    "residuals omits the test point's rank among n+1 exchangeable scores and "
    "does not guarantee P(Y_new in C) >= 1-alpha",
    "absolute residual scores |y - y_hat|; symmetric interval [y_hat-q, y_hat+q]",
    "weighted / adaptive / locally-weighted conformal is out of scope (M13)",
)


def _exact_alpha(alpha) -> Fraction:
    """alpha semantics (Followup-Review-Fix E4, SCF_REVIEW_J_SERIES_6b3a331):

    - ``Fraction`` / ``int``: exact.
    - decimal string such as ``"0.7"``: the exact decimal value (7/10).
    - ``float``: its exact BINARY value, ``Fraction(alpha)``. ``0.7`` is
      slightly below 7/10, so for n = 9 the rank is ceil(10 * 0.3000...04) = 4,
      while decimal 7/10 gives 3. The float result is conservative here, but no
      general statement about all floats follows -- pass ``Fraction(7, 10)`` or
      ``"0.7"`` to mean the decimal level.

    No rounding or epsilon shift before ``ceil`` (that could move true values
    above a rank boundary down)."""
    if isinstance(alpha, bool):
        raise ScopeViolationError("alpha must be a number, not bool")
    if isinstance(alpha, (Fraction, int)):
        return Fraction(alpha)
    if isinstance(alpha, str):
        try:
            return Fraction(alpha.strip())
        except (ValueError, ZeroDivisionError):
            raise ScopeViolationError(f"alpha string {alpha!r} is not a decimal/rational number") from None
    try:
        f = float(alpha)
    except (TypeError, ValueError):
        raise ScopeViolationError(f"unsupported alpha {alpha!r}") from None
    if not math.isfinite(f):
        raise ScopeViolationError(f"alpha must be finite; got {alpha!r}")
    return Fraction(f)


def calibrate_split_conformal(
    residuals: Sequence[float],
    alpha,
) -> float:
    """Return the split-conformal quantile ``q`` from calibration residuals.

    Parameters
    ----------
    residuals :
        Nonconformity scores on the calibration fold (typically
        ``|y_i - y_hat_i|``). Length ``n >= 1``.
    alpha :
        Miscoverage level in ``(0, 1)``. Target marginal coverage is
        ``1 - alpha``.

    Returns
    -------
    float
        The ``k``-th smallest residual (1-based order statistic), where

        ``k = ceil((n + 1) * (1 - alpha))``.

        If ``k == n + 1``, returns ``+inf``: there is no finite bound, and
        the resulting prediction interval is the WHOLE REAL LINE -- not an
        empty interval (Lei et al. Algorithm 2 / Theorem 2; wording
        corrected in J8, SCOPE_COMPOSITION_EVIDENCE_ROADMAP.md).

    Why the naive quantile breaks coverage
    --------------------------------------
    Taking the ordinary empirical ``(1 - alpha)``-quantile of the ``n``
    calibration residuals (or ``sorted[ceil(n*(1-alpha))-1]`` without the
    ``+1``) does **not** account for the test residual's rank among the
    ``n + 1`` exchangeable scores ``{R_1,...,R_n, R_{n+1}}``. The finite-
    sample guarantee ``P(Y_new ∈ C(X_new)) ≥ 1 - α`` under exchangeability
    requires the inflated order statistic with the ``(n + 1)`` correction
    and ceiling (Lei et al. 2018). Omitting it can undercover in finite
    samples even when residuals are i.i.d.
    """
    a = _exact_alpha(alpha)
    if not (0 < a < 1):
        raise ScopeViolationError(
            f"calibrate_split_conformal: alpha must be in (0, 1); got {alpha!r}"
        )
    vals = [float(r) for r in residuals]
    n = len(vals)
    if n < 1:
        raise ScopeViolationError(
            "calibrate_split_conformal: need at least one calibration residual"
        )
    for r in vals:
        if not math.isfinite(r) or r < 0.0:
            raise ScopeViolationError(
                f"calibrate_split_conformal: residuals must be finite and >= 0; "
                f"got {r!r}"
            )

    # Exact rank (Followup-Review-Fix E4): no float rounding, no epsilon.
    k = math.ceil((n + 1) * (1 - a))
    if k < 1:
        # Degenerate alpha→1 edge; still refuse rather than invent a quantile.
        raise ScopeViolationError(
            f"calibrate_split_conformal: computed k={k} < 1 for n={n}, alpha={alpha}"
        )
    if k == n + 1:
        return math.inf
    if k > n + 1:
        # Should not occur for alpha in (0,1), but keep explicit.
        return math.inf

    ordered = sorted(vals)
    return float(ordered[k - 1])  # 1-based k → 0-based index


def predict_interval(y_hat: float, q: float) -> Tuple[float, float]:
    """Symmetric split-conformal interval ``[y_hat - q, y_hat + q]``."""
    yh = float(y_hat)
    qq = float(q)
    if not math.isfinite(yh):
        raise ScopeViolationError(f"predict_interval: y_hat must be finite; got {y_hat!r}")
    if qq < 0.0 or (not math.isfinite(qq) and not math.isinf(qq)):
        raise ScopeViolationError(f"predict_interval: q must be >= 0; got {q!r}")
    lo = yh - qq
    hi = yh + qq
    return (float(lo), float(hi))


def assert_disjoint_calib_holdout(
    calib_indices: Sequence[int],
    holdout_indices: Sequence[int],
) -> None:
    """Anti-leak guard (``VAL-CONF-LEAK-001``).

    Calib and holdout index sets must be disjoint — same discipline as
    ``validation.core.split_epochs`` refusing index snooping. Overlap
    would let calibration residuals be computed on points later scored as
    holdout, breaking the exchangeability argument for marginal coverage.

    Raises
    ------
    ScopeViolationError
        If the index sets intersect, or either set is empty.
    """
    calib = tuple(int(i) for i in calib_indices)
    holdout = tuple(int(i) for i in holdout_indices)
    if len(calib) == 0 or len(holdout) == 0:
        raise ScopeViolationError(
            "VAL-CONF-LEAK-001: calib_indices and holdout_indices must both be "
            f"non-empty; got calib={calib!r} holdout={holdout!r}"
        )
    overlap = sorted(set(calib) & set(holdout))
    if overlap:
        raise ScopeViolationError(
            "VAL-CONF-LEAK-001: calib/holdout indices overlap (anti-leak). "
            f"overlap={overlap}; calib={calib}; holdout={holdout}"
        )


@dataclass(frozen=True)
class SplitConformalReport:
    """Typed report for a split-conformal calibration + interval.

    ``coverage_kind`` is always ``\"marginal_exchangeable\"`` — never
    ``\"guaranteed\"`` / ``\"exact\"`` / ``\"conditional\"``. Finite-sample
    marginal coverage under exchangeability is the Lei et al. 2018 claim;
    this report does not assert stronger guarantees.
    """

    q: float
    alpha: float
    n_calib: int
    y_hat: float
    interval: Tuple[float, float]
    coverage_kind: str  # MUST be "marginal_exchangeable"
    calib_indices: Tuple[int, ...]
    holdout_indices: Tuple[int, ...]
    assumptions: Tuple[str, ...]
    source: str = _SOURCE

    def __post_init__(self) -> None:
        if self.coverage_kind != COVERAGE_MARGINAL_EXCHANGEABLE:
            raise ValueError(
                f"SplitConformalReport.coverage_kind must be "
                f"{COVERAGE_MARGINAL_EXCHANGEABLE!r}; got {self.coverage_kind!r}. "
                f"Do not use 'guaranteed'/'exact'/'conditional'."
            )

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["interval"] = list(self.interval)
        d["assumptions"] = list(self.assumptions)
        d["calib_indices"] = list(self.calib_indices)
        d["holdout_indices"] = list(self.holdout_indices)
        # JSON-friendly inf
        if math.isinf(self.q):
            d["q"] = "inf"
        return d


def make_split_conformal_report(
    residuals: Sequence[float],
    alpha: float,
    y_hat: float,
    *,
    calib_indices: Sequence[int],
    holdout_indices: Sequence[int],
) -> SplitConformalReport:
    """Calibrate + predict with mandatory anti-leak index check.

    Calls ``assert_disjoint_calib_holdout`` first (``VAL-CONF-LEAK-001``),
    then ``calibrate_split_conformal`` and ``predict_interval``. Does not
    touch Cygnus data or ``validation.core``.
    """
    assert_disjoint_calib_holdout(calib_indices, holdout_indices)
    q = calibrate_split_conformal(residuals, alpha)
    interval = predict_interval(y_hat, q)
    return SplitConformalReport(
        q=q,
        alpha=float(alpha),
        n_calib=len(tuple(residuals)),
        y_hat=float(y_hat),
        interval=interval,
        coverage_kind=COVERAGE_MARGINAL_EXCHANGEABLE,
        calib_indices=tuple(int(i) for i in calib_indices),
        holdout_indices=tuple(int(i) for i in holdout_indices),
        assumptions=_DEFAULT_ASSUMPTIONS,
    )


__all__ = [
    "COVERAGE_MARGINAL_EXCHANGEABLE",
    "SplitConformalReport",
    "assert_disjoint_calib_holdout",
    "calibrate_split_conformal",
    "make_split_conformal_report",
    "predict_interval",
]
