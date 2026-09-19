"""Dynamics formulas: beta_response, S_rec, corrected cubic (FORMALISM.md §4–§5)."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Callable, List, Sequence

from scoped_correspondence.errors import ScopeViolationError


def sigmoid_response(
    u: float,
    beta_response: float,
    theta_u: float,
    p_max: float = 1.0,
) -> float:
    """Static UTAC response curve p(u).

    FORMALISM.md §2 row ``beta_response`` (unit 1/[u]) and §4:

        p(u) = p_max / (1 + exp[-beta_response * (u - Theta_u)])

    This is a *static* curve; it does not fix a recovery timescale.
    Midpoint slope is ``p_max * beta_response / 4``.
    """
    return float(p_max / (1.0 + math.exp(-beta_response * (u - theta_u))))


def recovery_rate_from_relaxation(tau: float) -> float:
    """Local continuous recovery rate S_rec = 1/tau for dot z = -(z-p(u))/tau.

    Maps to FORMALISM.md §2 row ``S_rec`` (1/time) and §4.

    **Independence of beta_response (Review finding A):** for fixed control u,
    the linearization of ``dot z = -(z - p(u))/tau`` has eigenvalue -1/tau,
    so ``S_rec = 1/tau``. The sigmoid steepness ``beta_response`` enters only
    through the equilibrium location z* = p(u), never through this rate.
    Callers must not treat ``beta_response`` and ``S_rec`` as interchangeable
    (GLOSSARY / FORMALISM.md §2: different units 1/[u] vs 1/time).
    """
    if tau <= 0:
        raise ScopeViolationError(
            f"recovery_rate_from_relaxation: tau must be > 0; got {tau!r}"
        )
    return float(1.0 / tau)


def cusp_field(x: float, a: float, b: float, tau: float = 1.0) -> float:
    """Right-hand side of the corrected cubic: tau * dx/dt = -x^3 + a*x + b.

    Returns dx/dt = (-x^3 + a*x + b) / tau. FORMALISM.md §5.
    """
    if tau <= 0:
        raise ScopeViolationError(f"cusp_field: tau must be > 0; got {tau!r}")
    return float((-x**3 + a * x + b) / tau)


def _cbrt(x: float) -> float:
    return math.copysign(abs(x) ** (1.0 / 3.0), x)


def fixed_points(a: float, b: float) -> List[float]:
    """Distinct real roots of x^3 - a*x - b = 0 (equilibria of the cubic).

    Same Cardano / trigonometric forms as verify_formalism.real_cubic_roots
    (p02_cusp_region).

    Audit finding A04: the degenerate-case test used to compare the
    discriminant ``4a^3-27b^2`` against a fixed ABSOLUTE threshold
    (``1e-12``). Since the discriminant scales with ``a^3``/``b^2``, that
    threshold silently misclassified genuinely-three-distinct-real-root
    cases at small ``|a|,|b|`` as degenerate (e.g. ``a=1e-5, b=0`` has
    discriminant ``4e-15`` and three real roots ``0, ±0.00316...``, but
    the old code returned only ``[-0.0, 0.0]``). Fixed by comparing the
    discriminant against a RELATIVE tolerance scaled by the magnitude of
    the two terms being subtracted (``4|a|^3 + 27b^2``) — the standard
    fix for a cancellation-sensitive sign test — instead of a fixed
    absolute value. Verified across a=1e-3 down to a=1e-10 (b=0): all
    return three distinct roots with |root - sqrt(a)| at machine
    precision. Exact-fold cases (discriminant exactly 0, e.g. the
    Panarchy cusp worked example a=3,b=±2) are unaffected — 0 remains
    inside the relative-tolerance band around 0 for any scale.
    """
    discriminant = 4 * a**3 - 27 * b**2
    scale = 4 * abs(a) ** 3 + 27 * b**2
    tol = 1e-9 * scale if scale > 0.0 else 1e-12
    if discriminant > tol:
        angle = math.acos(max(-1.0, min(1.0, b / (2 * (a / 3) ** 1.5))))
        return sorted(
            2 * math.sqrt(a / 3) * math.cos((angle + 2 * k * math.pi) / 3)
            for k in range(3)
        )
    if discriminant < -tol:
        q = math.sqrt(b * b / 4 - a**3 / 27)
        return [_cbrt(b / 2 + q) + _cbrt(b / 2 - q)]
    if abs(a) + abs(b) < 1e-12:
        return [0.0]
    r = _cbrt(b / 2)
    return sorted([-r, 2 * r])


def recovery_rate_at_equilibrium(x: float, a: float, tau: float, b: float = 0.0) -> float:
    """S_rec at an equilibrium of the cubic: -d(dx/dt)/dx evaluated at x.

    For the field f(x) = (-x^3 + a*x + b)/tau, Df = (a - 3*x^2)/tau and
    S_rec := -Df. Special cases (FORMALISM.md §5, b=0, a>0):

        S_rec(0) = -a/tau   (unstable origin)
        S_rec(±sqrt(a)) = 2a/tau  (stable branches)

    For b != 0, x=0 is generally not an equilibrium; the local derivative is
    still returned but must not be labelled a recovery rate of a nonexistent
    fixed point at the origin.
    """
    if tau <= 0:
        raise ScopeViolationError(f"recovery_rate_at_equilibrium: tau must be > 0; got {tau!r}")
    # S_rec = -Df = -(a - 3 x^2)/tau = (3 x^2 - a)/tau
    # Note: verify_formalism uses observed = -derivative(cusp, x) which equals
    # -(a - 3x^2)/tau = (3x^2 - a)/tau. For b=0 at x=0: -a/tau; at ±sqrt(a): 2a/tau.
    _ = b  # retained for API clarity / future checks
    return float((3.0 * x * x - a) / tau)


@dataclass(frozen=True)
class CubicNormalForm:
    """Corrected cubic normal form tau*dx/dt = -x^3 + a*x + b (FORMALISM.md §5).

    x, a, b dimensionless; tau has a time unit. Potential
    U(x) = x^4/4 - a*x^2/2 - b*x is mathematical, not automatically free energy.
    """

    a: float
    b: float = 0.0
    tau: float = 1.0

    def __post_init__(self) -> None:
        if self.tau <= 0:
            raise ScopeViolationError(
                f"CubicNormalForm: tau must be > 0; got {self.tau!r}"
            )

    def field(self, x: float) -> float:
        return cusp_field(x, self.a, self.b, self.tau)

    def equilibria(self) -> List[float]:
        return fixed_points(self.a, self.b)

    def discriminant(self) -> float:
        return float(4 * self.a**3 - 27 * self.b**2)

    def s_rec(self, x: float) -> float:
        return recovery_rate_at_equilibrium(x, self.a, self.tau, self.b)

    def potential(self, x: float) -> float:
        return float(x**4 / 4 - self.a * x**2 / 2 - self.b * x)


__all__ = [
    "CubicNormalForm",
    "cusp_field",
    "fixed_points",
    "recovery_rate_at_equilibrium",
    "recovery_rate_from_relaxation",
    "sigmoid_response",
]
