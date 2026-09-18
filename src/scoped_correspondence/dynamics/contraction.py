"""Contraction analysis for the 1-D cusp normal form (Milestone 14).

Maps Lohmiller & Slotine 1998 (DOI 10.1016/S0005-1098(98)00019-3): a smooth
system ``ẋ = f(x,t)`` is (globally) contracting with rate ``λ > 0`` in a
metric if the symmetric part of the Jacobian has eigenvalues ``≤ -λ``
everywhere. In one dimension with the Euclidean metric this reduces to

    f'(x) ≤ -λ  for all x.

For the cusp field ``f(x) = (-x³ + a x + b) / τ`` (``dynamics.core.cusp_field``),

    f'(x) = (-3 x² + a) / τ ,

so ``sup_x f'(x) = a/τ`` (attained at ``x = 0``). Global contraction in the
Euclidean 1-D metric therefore holds iff ``a < 0``, with certified rate

    λ = -a / τ = -sup f' .

When ``a ≥ 0`` the analytical rate is ``None``: this is the **bistability /
non-contraction scope** of the cusp (not a programming error). Multi-D
contraction metrics and new bistability formulas are out of scope for M14.

This module **calls** ``cusp_field`` only; it does not edit ``dynamics/core.py``.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, Optional, Sequence

from scoped_correspondence.dynamics.core import cusp_field
from scoped_correspondence.errors import ScopeViolationError

SOURCE = (
    "Lohmiller & Slotine 1998, "
    "On Contraction Analysis for Non-linear Systems, "
    "Automatica; DOI 10.1016/S0005-1098(98)00019-3"
)

METRIC_EUCLIDEAN_1D = "euclidean_1d"

_DEFAULT_ASSUMPTIONS: tuple[str, ...] = (
    "1-D Euclidean metric only — multi-D / Riemannian metrics out of scope (M14)",
    "sup f'(x) = a/tau at x=0 for cusp_field f=(-x^3+a*x+b)/tau "
    "with f'=(-3x^2+a)/tau",
    "global contraction iff a<0 with rate lambda=-a/tau; a>=0 → rate=None "
    "(bistability / non-contraction scope, not an error)",
    "numerical check uses finite differences on cusp_field (CALL only; "
    "dynamics/core.py not edited)",
    "b cancels in f'; verification uses b=0",
)


def contraction_rate_cusp(a: float, tau: float = 1.0) -> Optional[float]:
    """Analytical global contraction rate for the 1-D cusp field.

    For ``cusp_field`` ``f = (-x³ + a x + b) / τ`` with
    ``f' = (-3 x² + a) / τ``, one has ``sup f'(x) = a / τ`` at ``x = 0``.

    Parameters
    ----------
    a :
        Linear coefficient of the cubic normal form.
    tau :
        Time scale ``τ > 0``.

    Returns
    -------
    Optional[float]
        ``λ = -a / τ`` when ``a < 0`` (globally contracting).
        ``None`` when ``a ≥ 0`` (bistability / non-contraction scope —
        not an error).
    """
    if float(tau) <= 0.0:
        raise ScopeViolationError(
            f"contraction_rate_cusp: tau must be > 0; got {tau!r}"
        )
    aa = float(a)
    tt = float(tau)
    if aa < 0.0:
        return float(-aa / tt)
    return None


@dataclass(frozen=True)
class ContractionCertificate:
    """Certificate for 1-D Euclidean contraction of the cusp field.

    ``is_globally_contracting`` is True iff ``rate is not None`` (i.e. ``a < 0``)
    and — when produced by ``verify_contraction_bound`` — the finite-difference
    check ``f' ≤ -rate`` holds on the provided samples.
    """

    rate: Optional[float]
    a: float
    tau: float
    is_globally_contracting: bool
    metric: str = METRIC_EUCLIDEAN_1D
    source: str = SOURCE
    assumptions: tuple[str, ...] = _DEFAULT_ASSUMPTIONS
    max_estimated_fprime: Optional[float] = None
    n_samples: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _finite_diff_fprime(
    x: float,
    a: float,
    tau: float,
    eps: float = 1e-6,
) -> float:
    """Central finite difference of cusp_field (b=0); CALL only."""
    f_plus = cusp_field(x + eps, a, 0.0, tau)
    f_minus = cusp_field(x - eps, a, 0.0, tau)
    return float((f_plus - f_minus) / (2.0 * eps))


def verify_contraction_bound(
    a: float,
    tau: float,
    x_samples: Sequence[float],
    *,
    eps: float = 1e-6,
    atol: float = 1e-5,
) -> ContractionCertificate:
    """Numerically verify ``f' ≤ -rate`` on samples via finite differences.

    Calls ``cusp_field`` only (does not edit ``dynamics/core.py``).

    When ``contraction_rate_cusp(a, tau)`` is ``None`` (``a ≥ 0``), returns a
    certificate with ``is_globally_contracting=False`` without treating that as
    an error — bistability / non-contraction scope.

    When a positive rate is returned, estimates ``f'`` at each sample by a
    central difference of ``cusp_field`` and requires
    ``estimated_fprime ≤ -rate + atol``. Failure raises ``ScopeViolationError``.
    """
    if float(tau) <= 0.0:
        raise ScopeViolationError(
            f"verify_contraction_bound: tau must be > 0; got {tau!r}"
        )
    if float(eps) <= 0.0:
        raise ScopeViolationError(
            f"verify_contraction_bound: eps must be > 0; got {eps!r}"
        )

    aa = float(a)
    tt = float(tau)
    rate = contraction_rate_cusp(aa, tt)
    samples = [float(x) for x in x_samples]
    n = len(samples)

    if rate is None:
        # a >= 0: non-contraction / bistability scope — not an error.
        max_fp: Optional[float] = None
        if n > 0:
            estimates = [_finite_diff_fprime(x, aa, tt, eps=eps) for x in samples]
            max_fp = float(max(estimates))
        return ContractionCertificate(
            rate=None,
            a=aa,
            tau=tt,
            is_globally_contracting=False,
            metric=METRIC_EUCLIDEAN_1D,
            source=SOURCE,
            max_estimated_fprime=max_fp,
            n_samples=n,
        )

    if n < 1:
        raise ScopeViolationError(
            "verify_contraction_bound: need at least one x_sample when rate "
            f"is not None (a={aa}, tau={tt}, rate={rate})"
        )

    estimates = [_finite_diff_fprime(x, aa, tt, eps=eps) for x in samples]
    max_fp = float(max(estimates))
    bound = -float(rate)
    # Require f' <= -rate (+ atol slack for FD truncation).
    violators = [
        (x, fp)
        for x, fp in zip(samples, estimates)
        if fp > bound + float(atol)
    ]
    if violators:
        raise ScopeViolationError(
            "verify_contraction_bound: finite-diff f' exceeds -rate at "
            f"{len(violators)} sample(s); rate={rate}, bound={bound}, "
            f"worst={max(violators, key=lambda t: t[1])!r}, atol={atol}"
        )

    return ContractionCertificate(
        rate=float(rate),
        a=aa,
        tau=tt,
        is_globally_contracting=True,
        metric=METRIC_EUCLIDEAN_1D,
        source=SOURCE,
        max_estimated_fprime=max_fp,
        n_samples=n,
    )


def make_contraction_certificate(
    a: float,
    tau: float = 1.0,
) -> ContractionCertificate:
    """Build an analytical certificate (no numerical sampling).

    ``is_globally_contracting`` mirrors ``rate is not None``.
    """
    if float(tau) <= 0.0:
        raise ScopeViolationError(
            f"make_contraction_certificate: tau must be > 0; got {tau!r}"
        )
    aa = float(a)
    tt = float(tau)
    rate = contraction_rate_cusp(aa, tt)
    return ContractionCertificate(
        rate=rate if rate is None else float(rate),
        a=aa,
        tau=tt,
        is_globally_contracting=rate is not None,
        metric=METRIC_EUCLIDEAN_1D,
        source=SOURCE,
        max_estimated_fprime=None,
        n_samples=0,
    )


__all__ = [
    "METRIC_EUCLIDEAN_1D",
    "SOURCE",
    "ContractionCertificate",
    "contraction_rate_cusp",
    "make_contraction_certificate",
    "verify_contraction_bound",
]
