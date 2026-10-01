"""Stellar pulse vs observation operator (SK1-SK3, candidate assessment 2026-10-01).

A dimensionless release-and-relaxation NULL model -- NOT a model of
Sakurai's object, of thermonuclear ignition, convection or stellar
structure (assessment section 4.2):

    f' = -alpha f,   E' = alpha f - beta E,   Q' = beta E,   f(0) = 1, E(0) = Q(0) = 0

f + E + Q = 1. For alpha != beta: E(t) = alpha/(beta - alpha) (exp(-alpha t) - exp(-beta t));
alpha = beta: E(t) = alpha t exp(-alpha t). A pulse (rise and recovery)
already arises in this LINEAR coupled system; a later nonlinear rate must
explain a named additional finding against this control.

Observation (assessment 4.3): in a normalised single band F = L exp(-tau),
(L, tau) and (e L, tau + 1) are observationally equivalent. With a known
spectral shape and two known, different extinction coefficients k1 != k2
the log model log F_j = log L - k_j tau has rank 2 (exact, via J6) -- with an
unknown temperature/shape term per band it does not automatically.

Wind scaling (assessment 4.3): at fixed T, wind speed and clumping,
R* -> 4 R* with Mdot -> 8 Mdot keeps R* (v_inf / Mdot)^(2/3) invariant while
L ~ R*^2 scales by 16. The ALGEBRAIC invariance is exact; equality of real
normalised spectra stays a model-dependent approximation (not claimed).
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from fractions import Fraction
from typing import Optional, Sequence, Tuple

from scoped_correspondence.errors import ScopeViolationError
from scoped_correspondence.identifiability.exact_linear import analyze_affine_identifiability


@dataclass(frozen=True)
class ReleaseState:
    f: float
    E: float
    Q: float


def release_state(alpha: float, beta: float, t: float) -> ReleaseState:
    for v, n in ((alpha, "alpha"), (beta, "beta")):
        if not (math.isfinite(v) and v > 0):
            raise ScopeViolationError(f"{n} must be finite and > 0")
    if not (math.isfinite(t) and t >= 0):
        raise ScopeViolationError("t must be finite and >= 0")
    f = math.exp(-alpha * t)
    if alpha == beta:
        E = alpha * t * math.exp(-alpha * t)
    else:
        E = alpha / (beta - alpha) * (math.exp(-alpha * t) - math.exp(-beta * t))
    return ReleaseState(f, E, 1.0 - f - E)


def peak_time(alpha: float, beta: float) -> float:
    """argmax E(t): ln(beta/alpha)/(beta - alpha), limit 1/alpha for alpha = beta."""
    if alpha == beta:
        return 1.0 / alpha
    return math.log(beta / alpha) / (beta - alpha)


def single_band_flux(L: float, tau: float) -> float:
    return L * math.exp(-tau)


def two_band_identifiability(k: Sequence, *, unknown_shape_terms: bool = False):
    """Exact rank of log F_j = log L - k_j tau (+ s_j if the per-band shape is unknown)."""
    rows = []
    for j, kj in enumerate(k):
        row = [1, -Fraction(kj)]
        if unknown_shape_terms:
            row += [1 if i == j else 0 for i in range(len(k))]
        rows.append(row)
    return analyze_affine_identifiability(rows)


def wind_transformed_radius(R: Fraction, v_inf: Fraction, mdot: Fraction) -> Fraction:
    """R* (v_inf / Mdot)^(2/3) -- returned via its CUBE to stay exact:
    (R*^3 (v_inf/Mdot)^2)."""
    for x, n in ((R, "R"), (v_inf, "v_inf"), (mdot, "Mdot")):
        if isinstance(x, float) or Fraction(x) <= 0:
            raise ScopeViolationError(f"{n} must be an exact positive number")
    return Fraction(R) ** 3 * (Fraction(v_inf) / Fraction(mdot)) ** 2


__all__ = ["ReleaseState", "release_state", "peak_time", "single_band_flux", "two_band_identifiability", "wind_transformed_radius"]
