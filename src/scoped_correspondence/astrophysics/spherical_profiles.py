"""Spherical halo density profiles and comparable observables (G1).

Content basis: `SCF_GALAXY_DYNAMICS_IMPLEMENTATION_PLAN.md` §6 ("G1 --
Profile und wirklich vergleichbare Observablen") and
`docs/galaxy_dynamics_scope.md`.

Three genuinely different quantities (Plan §6.1) are kept as separate,
distinctly named methods and are never silently confused:

- **profile parameter product** ``mu_h = rho0 * r0`` -- a convenient
  combination of fit parameters, not itself a measured density.
- **true central column density** ``Sigma_col(0) = 2 * integral_0^inf
  rho(r) dr`` -- the actual projected surface density at the profile
  centre for the untruncated profile.
- an aperture-averaged projected density is a *third*, distinct quantity
  and is intentionally NOT implemented here; G1 only needs the first two.

All non-NFW profiles use the dimensionless-shape convention ``f(x) =
rho(r)/rho0``, ``x = r/r0``, ``f(0) = 1`` (Plan §6.1). NFW does not fit
this convention (its central density diverges) and is handled with its
own scale product ``rho_s * r_s``, which this module never calls
``mu_h`` and never treats as a finite central column density.

Internal unit basis: length in pc, density in M_sun/pc^3, mass in M_sun,
velocity in km/s, acceleration in (km/s)^2/pc (see `units.py`).
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from .units import G_ASTRO_PC


def _as_radius_array(r_pc):
    r = np.asarray(r_pc, dtype=float)
    if np.any(r < 0):
        raise ValueError("radius must be non-negative")
    return r


def _restore_shape(value: np.ndarray, like) -> "float | np.ndarray":
    """Return a Python float if `like` was a scalar, else the ndarray.

    `value` may be a shape-(1,) array even for scalar `like` (internal
    computations often go through `np.atleast_1d`); `.reshape(-1)[0]`
    handles that without numpy's stricter-than-`float()` 0-d requirement.
    """
    if np.ndim(like) == 0:
        return float(np.asarray(value).reshape(-1)[0])
    return value


@dataclass(frozen=True)
class BurkertProfile:
    """Burkert (1995) halo profile: ``f(x) = 1 / [(1+x)(1+x^2)]``.

    Finite central density (``f(0)=1``); the untruncated total mass grows
    logarithmically with radius -- there is no finite total mass (Plan
    §6.1 table).
    """

    rho0_msun_pc3: float
    r0_pc: float
    #: below this |x|, use the small-x Taylor series (Plan §6.2) instead
    #: of the closed-form mass bracket, which suffers catastrophic
    #: cancellation as x -> 0.
    series_switch_x: float = 1.0e-3

    def __post_init__(self) -> None:
        if self.rho0_msun_pc3 <= 0:
            raise ValueError("rho0 must be positive")
        if self.r0_pc <= 0:
            raise ValueError("r0 must be positive")

    def mu_h(self) -> float:
        """Profile parameter product ``rho0*r0`` [M_sun/pc^2]."""
        return self.rho0_msun_pc3 * self.r0_pc

    def sigma_col0(self) -> float:
        """True central column density ``(pi/2)*rho0*r0`` (Plan §6.1)."""
        return (math.pi / 2.0) * self.mu_h()

    def density(self, r_pc):
        """rho(r) [M_sun/pc^3]."""
        r = _as_radius_array(r_pc)
        x = r / self.r0_pc
        val = self.rho0_msun_pc3 / ((1.0 + x) * (1.0 + x**2))
        return _restore_shape(val, r_pc)

    def _mass_bracket(self, x: np.ndarray) -> np.ndarray:
        """``ln(1+x) + 0.5*ln(1+x^2) - arctan(x)``, stabilised near x=0.

        Independently re-derived via direct Taylor expansion (SCF_REVIEW_
        G0_G7_5563e67.md finding R1, confirmed 2026-09-26): with
        ``ln(1+x) = x - x^2/2 + x^3/3 - x^4/4 + x^5/5 - x^6/6 + x^7/7 -
        x^8/8``, ``0.5*ln(1+x^2) = x^2/2 - x^4/4 + x^6/6 - x^8/8``, and
        ``arctan(x) = x - x^3/3 + x^5/5 - x^7/7``, every term through
        ``x^2``, ``x^5``, ``x^6`` cancels and the ``x^3``/``x^7`` terms
        DOUBLE (they appear with the same sign in the ln-sum and via
        ``-(-arctan)``), giving ``bracket(x) = 2*x^3/3 - x^4/2 + 2*x^7/7 -
        x^8/4 = 2*(x^3/3 - x^4/4 + x^7/7 - x^8/8)``. The series below was
        previously missing this factor of 2 (docstring said "doubled
        here", the code did not), silently halving mass/acceleration and
        giving ``v_c`` only ``1/sqrt(2)`` of the correct value for
        ``x < series_switch_x`` -- see `verify_galaxy_profiles.py`'s
        `check_burkert_series_matches_closed_form_at_tiny_x` regression.
        """
        small = np.abs(x) < self.series_switch_x
        with np.errstate(all="ignore"):
            closed = np.log1p(x) + 0.5 * np.log1p(x**2) - np.arctan(x)
        series = 2.0 * (x**3 / 3.0 - x**4 / 4.0 + x**7 / 7.0 - x**8 / 8.0)
        return np.where(small, series, closed)

    def enclosed_mass(self, r_pc):
        """``M(<r)`` [M_sun], exact closed form / series bracket (Plan §6.2)."""
        r = _as_radius_array(r_pc)
        x = r / self.r0_pc
        bracket = self._mass_bracket(x)
        val = 2.0 * math.pi * self.rho0_msun_pc3 * self.r0_pc**3 * bracket
        return _restore_shape(val, r_pc)

    def g(self, r_pc):
        """Radial gravitational acceleration [(km/s)^2/pc].

        ``g(0) = 0`` exactly (finite central density, Plan §6.2); r must
        be non-negative, division by r^2 is only taken where r>0.
        """
        r = _as_radius_array(r_pc)
        r1 = np.atleast_1d(r)
        x1 = r1 / self.r0_pc
        bracket1 = self._mass_bracket(x1)
        mass_over_r2 = np.zeros_like(r1, dtype=float)
        nz = r1 > 0
        mass_over_r2[nz] = (
            2.0 * math.pi * self.rho0_msun_pc3 * self.r0_pc**3 * bracket1[nz] / r1[nz] ** 2
        )
        val = G_ASTRO_PC * mass_over_r2
        return _restore_shape(val, r_pc)

    def circular_velocity(self, r_pc):
        """``v_c(r) = sqrt(G*M(<r)/r)`` [km/s]; ``v_c(0) = 0`` exactly."""
        r = _as_radius_array(r_pc)
        M = np.atleast_1d(self.enclosed_mass(r))
        r1 = np.atleast_1d(r)
        val = np.zeros_like(r1, dtype=float)
        nz = r1 > 0
        val[nz] = np.sqrt(G_ASTRO_PC * M[nz] / r1[nz])
        return _restore_shape(val, r_pc)


@dataclass(frozen=True)
class PseudoIsothermalProfile:
    """Pseudo-isothermal halo profile: ``f(x) = 1 / (1+x^2)``.

    Finite central density; the untruncated total mass grows linearly
    with radius (Plan §6.1 table).
    """

    rho0_msun_pc3: float
    r0_pc: float
    series_switch_x: float = 1.0e-3

    def __post_init__(self) -> None:
        if self.rho0_msun_pc3 <= 0:
            raise ValueError("rho0 must be positive")
        if self.r0_pc <= 0:
            raise ValueError("r0 must be positive")

    def mu_h(self) -> float:
        return self.rho0_msun_pc3 * self.r0_pc

    def sigma_col0(self) -> float:
        """``pi*rho0*r0`` (Plan §6.1)."""
        return math.pi * self.mu_h()

    def density(self, r_pc):
        r = _as_radius_array(r_pc)
        x = r / self.r0_pc
        val = self.rho0_msun_pc3 / (1.0 + x**2)
        return _restore_shape(val, r_pc)

    def _mass_bracket(self, x: np.ndarray) -> np.ndarray:
        """``x - arctan(x)``, stabilised near x=0.

        Series: ``x^3/3 - x^5/5 + x^7/7`` (Taylor expansion of ``arctan``
        subtracted from ``x``).
        """
        small = np.abs(x) < self.series_switch_x
        with np.errstate(all="ignore"):
            closed = x - np.arctan(x)
        series = x**3 / 3.0 - x**5 / 5.0 + x**7 / 7.0
        return np.where(small, series, closed)

    def enclosed_mass(self, r_pc):
        """``M(<r) = 4*pi*rho0*r0^3*[x - arctan(x)]`` [M_sun]."""
        r = _as_radius_array(r_pc)
        x = r / self.r0_pc
        bracket = self._mass_bracket(x)
        val = 4.0 * math.pi * self.rho0_msun_pc3 * self.r0_pc**3 * bracket
        return _restore_shape(val, r_pc)

    def g(self, r_pc):
        r = _as_radius_array(r_pc)
        r1 = np.atleast_1d(r)
        x1 = r1 / self.r0_pc
        bracket1 = self._mass_bracket(x1)
        mass_over_r2 = np.zeros_like(r1, dtype=float)
        nz = r1 > 0
        mass_over_r2[nz] = (
            4.0 * math.pi * self.rho0_msun_pc3 * self.r0_pc**3 * bracket1[nz] / r1[nz] ** 2
        )
        val = G_ASTRO_PC * mass_over_r2
        return _restore_shape(val, r_pc)

    def circular_velocity(self, r_pc):
        r = _as_radius_array(r_pc)
        M = np.atleast_1d(self.enclosed_mass(r))
        r1 = np.atleast_1d(r)
        val = np.zeros_like(r1, dtype=float)
        nz = r1 > 0
        val[nz] = np.sqrt(G_ASTRO_PC * M[nz] / r1[nz])
        return _restore_shape(val, r_pc)


@dataclass(frozen=True)
class NFWProfile:
    """Navarro-Frenk-White profile: ``f(x) = 1 / [x*(1+x)^2]``.

    **Central density diverges** -- there is no finite central column
    density and no ``mu_h`` in the sense of the other two profiles. The
    only finite scale combination is ``rho_s * r_s``, kept under its own
    name (``scale_product``) so it is never confused with a Burkert-style
    finite central-density product (Plan §6.1: "`rho_s*r_s` ist ein
    endliches Skalenprodukt, keine endliche zentrale Dichte mal
    Kernradius").
    """

    rho_s_msun_pc3: float
    r_s_pc: float
    series_switch_x: float = 1.0e-3

    def __post_init__(self) -> None:
        if self.rho_s_msun_pc3 <= 0:
            raise ValueError("rho_s must be positive")
        if self.r_s_pc <= 0:
            raise ValueError("r_s must be positive")

    def scale_product(self) -> float:
        """``rho_s * r_s`` [M_sun/pc^2] -- finite, but NOT a central column density."""
        return self.rho_s_msun_pc3 * self.r_s_pc

    def sigma_col0(self):
        """Central column density is undefined (density diverges as r->0).

        Explicitly not offered as a finite number -- returns ``None``
        rather than silently producing an infinite or NaN "observable".
        """
        return None

    def density(self, r_pc):
        """rho(r) [M_sun/pc^3]; diverges as r -> 0 (r=0 raises)."""
        r = _as_radius_array(r_pc)
        if np.any(r == 0):
            raise ValueError("NFW central density diverges at r=0 -- not evaluable")
        x = r / self.r_s_pc
        val = self.rho_s_msun_pc3 / (x * (1.0 + x) ** 2)
        return _restore_shape(val, r_pc)

    def _mass_bracket(self, x: np.ndarray) -> np.ndarray:
        """``ln(1+x) - x/(1+x)``, stabilised near x=0.

        Series (own derivation, checked against `verify_galaxy_profiles.py`):
        ``x^2/2 - 2*x^3/3 + 3*x^4/4 - 4*x^5/5``.
        """
        small = np.abs(x) < self.series_switch_x
        with np.errstate(all="ignore"):
            closed = np.log1p(x) - x / (1.0 + x)
        series = x**2 / 2.0 - 2.0 * x**3 / 3.0 + 3.0 * x**4 / 4.0 - 4.0 * x**5 / 5.0
        return np.where(small, series, closed)

    def enclosed_mass(self, r_pc):
        """``M(<r) = 4*pi*rho_s*r_s^3*[ln(1+x) - x/(1+x)]`` [M_sun].

        ``M(0) = 0`` exactly despite the central density divergence (the
        divergence is integrable in 3D).
        """
        r = _as_radius_array(r_pc)
        x = r / self.r_s_pc
        bracket = self._mass_bracket(x)
        val = 4.0 * math.pi * self.rho_s_msun_pc3 * self.r_s_pc**3 * bracket
        return _restore_shape(val, r_pc)

    def g(self, r_pc):
        """Radial acceleration magnitude [(km/s)^2/pc], r > 0 only.

        **r=0 raises**, it is not evaluated as 0 (SCF_REVIEW_G0_G7_5563e67.md
        finding R4, confirmed 2026-09-26): unlike Burkert/pseudo-isothermal
        (finite central density -> g(r)->0 continuously as r->0), NFW's
        enclosed mass is `M(r) ~ 2*pi*rho_s*r_s*r^2` for small r, so
        `g(r) = G*M(r)/r^2 -> 2*pi*G*rho_s*r_s`, a NONZERO one-sided limit
        (independently re-derived and confirmed: 4.0536... (km/s)^2/pc for
        rho_s=0.05, r_s=3000 pc). The radial *direction* is additionally
        undefined exactly at the origin. Rather than silently return an
        arbitrary single number for an ill-defined vector field point
        (matching `density()`'s existing r=0 convention), this raises.
        Callers needing the one-sided scalar limit should evaluate at a
        small positive r (see `verify_galaxy_profiles.py`'s
        `check_nfw_nonzero_one_sided_central_limit`).
        """
        r = _as_radius_array(r_pc)
        if np.any(r == 0):
            raise ValueError("NFW g(r) is undefined at r=0 (direction undefined, "
                              "one-sided limit is nonzero -- see docstring)")
        r1 = np.atleast_1d(r)
        x1 = r1 / self.r_s_pc
        bracket1 = self._mass_bracket(x1)
        mass_over_r2 = (
            4.0 * math.pi * self.rho_s_msun_pc3 * self.r_s_pc**3 * bracket1 / r1 ** 2
        )
        val = G_ASTRO_PC * mass_over_r2
        return _restore_shape(val, r_pc)

    def circular_velocity(self, r_pc):
        r = _as_radius_array(r_pc)
        M = np.atleast_1d(self.enclosed_mass(r))
        r1 = np.atleast_1d(r)
        val = np.zeros_like(r1, dtype=float)
        nz = r1 > 0
        val[nz] = np.sqrt(G_ASTRO_PC * M[nz] / r1[nz])
        return _restore_shape(val, r_pc)
