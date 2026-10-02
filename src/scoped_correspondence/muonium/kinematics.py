"""Idealised three-plane kinematics, units and scope (Paket MU1, plan §4-§5).

Model (plan §5.1): three equidistant planes at times 0, T, 2T with grating
spacing L, period d, constant longitudinal velocity v (T = L/v) and constant
transverse acceleration a along a declared sensitive axis:

    z(t) = z0 + u0 t + a t^2 / 2
    relative displacement  Delta z = z(2T) - 2 z(T) + z(0) = a T^2
    single-path drop after T          = a T^2 / 2      (a DIFFERENT quantity)
    phase  phi_g = K(v) a,   K(v) = 2 pi L^2 / (d v^2) = 2 pi T^2 / d
    grating combination h = G3 - 2 G2 + G1 gives a phase offset -2 pi h / d
    survival over 2T (non-relativistic): S = exp(-2 L / (v tau))

The relative displacement eliminates z0 and u0. ``h`` and a free common
phase offset are NOT separately identifiable (both shift the phase).

Scope: L, d, v, T positive and finite; EQUAL flight times; constant
acceleration on the path; known sensitive axis. Unequal times, accelerated
beams, diffraction and device effects are separate extensions (rejected
here, not silently approximated). Negative accelerations are allowed:
no positivity is assumed for a_mu.

Internally SI. Exact inputs (int/Fraction) give exact rational results for
everything except functions of pi and exp, which are returned as floats.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from fractions import Fraction
from typing import Optional, Union

from scoped_correspondence.dimensions.core import Div, Dimension, Mul, Pow, Q, QuantitySpec, check_dimension
from scoped_correspondence.errors import ScopeViolationError

Num = Union[int, Fraction, float]


def _num(x, what: str, *, positive: bool = False) -> Num:
    if isinstance(x, bool) or not isinstance(x, (int, Fraction, float)):
        raise ScopeViolationError(f"{what} must be a real number, got {type(x).__name__}")
    if isinstance(x, float) and not math.isfinite(x):
        raise ScopeViolationError(f"{what} must be finite")
    if positive and not x > 0:
        raise ScopeViolationError(f"{what} must be > 0 (scope of the idealised model)")
    return x


@dataclass(frozen=True)
class Geometry:
    """Three equidistant planes. ``axis`` documents the sensitive axis and
    its sign convention (positive towards the local reference acceleration)."""

    L: Num  # plane spacing [m]
    d: Num  # grating period [m]
    v: Num  # longitudinal velocity [m/s]
    axis: str = "vertical, positive towards local g_ref"

    def __post_init__(self) -> None:
        _num(self.L, "L", positive=True)
        _num(self.d, "d", positive=True)
        _num(self.v, "v", positive=True)

    @property
    def T(self) -> Num:
        return self.L / self.v

    def K(self) -> float:
        """Phase per unit acceleration [s^2/m]: 2 pi L^2 / (d v^2)."""
        return 2 * math.pi * float(Fraction(self.L) ** 2 / (Fraction(self.d) * Fraction(self.v) ** 2)
                                   if not any(isinstance(x, float) for x in (self.L, self.d, self.v))
                                   else self.L ** 2 / (self.d * self.v ** 2))


def check_flight_times(t1: Num, t2: Num) -> None:
    """The model needs t(plane2) - t(plane1) == t(plane3) - t(plane2)."""
    _num(t1, "first flight time", positive=True)
    _num(t2, "second flight time", positive=True)
    if t1 != t2:
        raise ScopeViolationError("unequal flight times are outside the idealised model (needs a new derivation)")


def second_difference(z0: Num, u0: Num, a: Num, T: Num) -> Num:
    _num(T, "T", positive=True)
    z = lambda t: z0 + u0 * t + a * t * t / 2
    return z(2 * T) - 2 * z(T) + z(0)


def relative_displacement(a: Num, T: Num) -> Num:
    """Delta z = a T^2 (third-grating relative displacement)."""
    _num(a, "a")
    _num(T, "T", positive=True)
    return a * T * T


def single_path_drop(a: Num, T: Num) -> Num:
    """a T^2 / 2 -- the drop of ONE trajectory after time T."""
    _num(a, "a")
    _num(T, "T", positive=True)
    return a * T * T / 2


def gravity_phase(a: Num, geom: Geometry) -> float:
    return geom.K() * float(_num(a, "a"))


def grating_offset_phase(h: Num, d: Num) -> float:
    """Phase offset -2 pi h / d of the grating combination h = G3 - 2 G2 + G1."""
    return -2 * math.pi * float(_num(h, "h")) / float(_num(d, "d", positive=True))


def survival(geom: Geometry, tau: Num, *, lorentz_gamma: Optional[Num] = None) -> float:
    """Survival between plane 1 and plane 3: exp(-2 L / (v tau_eff)),
    tau_eff = gamma tau if a Lorentz factor is given. The rate reference is
    plane 1; losses already contained in a measured rate must not be applied
    again (documented, cannot be checked here)."""
    _num(tau, "tau", positive=True)
    t_eff = tau if lorentz_gamma is None else _num(lorentz_gamma, "gamma", positive=True) * tau
    if lorentz_gamma is not None and lorentz_gamma < 1:
        raise ScopeViolationError("Lorentz factor must be >= 1")
    return math.exp(-2 * float(geom.L) / (float(geom.v) * float(t_eff)))


def delta_g(a_mu: Num, g_ref: Num) -> Num:
    """delta = (a_mu - g_ref) / g_ref, g_ref > 0 (declared reference incl. projection)."""
    _num(a_mu, "a_mu")
    _num(g_ref, "g_ref", positive=True)
    return (a_mu - g_ref) / g_ref


def eta(a_mu: Num, g_ref: Num) -> Optional[Num]:
    """eta = 2 (a_mu - g_ref) / (a_mu + g_ref) = 2 delta / (2 + delta).
    Returns None (undefined, with the caller expected to report why) when
    a_mu + g_ref == 0 -- never an invented value."""
    _num(a_mu, "a_mu")
    _num(g_ref, "g_ref", positive=True)
    den = a_mu + g_ref
    if den == 0:
        return None
    return 2 * (a_mu - g_ref) / den


def phase_is_dimensionless() -> bool:
    """J2 cross-check: K a = 2 pi L^2 a / (d v^2) is dimensionless."""
    specs = {
        "L": QuantitySpec("L", Dimension.of(L=1)),
        "d": QuantitySpec("d", Dimension.of(L=1)),
        "v": QuantitySpec("v", Dimension.of(L=1, T=-1)),
        "a": QuantitySpec("a", Dimension.of(L=1, T=-2)),
    }
    expr = Div(Mul(Pow(Q("L"), 2), Q("a")), Mul(Q("d"), Pow(Q("v"), 2)))
    rep = check_dimension(expr, specs)
    return rep.status == "consistent" and rep.dimension.is_dimensionless


__all__ = [
    "Geometry",
    "check_flight_times",
    "second_difference",
    "relative_displacement",
    "single_path_drop",
    "gravity_phase",
    "grating_offset_phase",
    "survival",
    "delta_g",
    "eta",
    "phase_is_dimensionless",
]
