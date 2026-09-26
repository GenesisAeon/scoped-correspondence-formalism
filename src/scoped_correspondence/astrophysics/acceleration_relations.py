"""Effective-density observation operator and declared MOND control case (G3).

Content basis: `SCF_GALAXY_DYNAMICS_IMPLEMENTATION_PLAN.md` §8 ("G3 --
Kontrollmodelle und Beobachtungsäquivalenz").

Internal unit basis matches the rest of this package: length in pc,
density in M_sun/pc^3, acceleration in (km/s)^2/pc (see `units.py`); MOND
constants (`a0`) convert at the boundary via `units.accel_si_to_kms2_per_pc`.
"""
from __future__ import annotations

import math

import numpy as np

from .units import A0_SI, G_ASTRO_PC, accel_si_to_kms2_per_pc


def effective_density(g_fn, r_pc, rel_step: float = 1e-6):
    """Newtonian effective density from a spherical acceleration profile.

    ``rho_eff(r) = 1/(4 pi G r^2) * d/dr[r^2 g(r)]`` (Plan §8.1), for a
    smooth, spherical, inward-directed acceleration profile ``g_fn`` and
    ``r > 0``. The derivative is a central finite difference at relative
    step ``rel_step`` -- ``g_fn`` need not have a known closed form
    (it may itself be a sum of baryon + halo + MOND terms).

    A NEGATIVE result is returned as-is. This function never clips a
    negative "phantom" density to zero (Plan §8.1: "Negative effektive
    Restdichten nicht stillschweigend auf null setzen") -- a negative
    value is a genuine, meaningful output (e.g. where a declared
    baryon-only subtraction overshoots ``rho_eff``).

    A central point mass at r=0 needs an ADDITIONAL distributional
    contribution not captured by this r>0 formula alone (Plan §8.1) --
    this function only ever evaluates the smooth r>0 part.
    """
    r = np.asarray(r_pc, dtype=float)
    if np.any(r <= 0):
        raise ValueError("effective_density requires r > 0")
    h = r * rel_step

    def r2g(rr):
        return rr**2 * g_fn(rr)

    d_r2g = (r2g(r + h) - r2g(r - h)) / (2.0 * h)
    return d_r2g / (4.0 * math.pi * G_ASTRO_PC * r**2)


def mond_g_total(g_N, a0_si: float = A0_SI):
    """Declared MOND control case (Plan §8.2), standard interpolation
    ``mu_M(x) = x/sqrt(1+x^2)``, solved algebraically for ``g``:

    ``g = sqrt((g_N^2 + g_N*sqrt(g_N^2 + 4*a0^2)) / 2)``

    ``g_N`` and the returned ``g`` are both in the internal (km/s)^2/pc
    basis; ``a0_si`` is converted at the boundary. ``g_N < 0`` is outside
    this scalar model's declared scope and raises (Plan §8.2: "negative
    Eingaben sind in diesem skalaren Modell außerhalb des
    Geltungsbereichs"). At ``g_N=0`` this returns exactly 0.
    """
    g_N = np.asarray(g_N, dtype=float)
    if np.any(g_N < 0):
        raise ValueError("g_N < 0 is outside the declared MOND control-case scope")
    a0 = accel_si_to_kms2_per_pc(a0_si)
    inner = g_N**2 + 4.0 * a0**2
    return np.sqrt((g_N**2 + g_N * np.sqrt(inner)) / 2.0)


def mond_g_total_simple_interpolation_NOT_INTERCHANGEABLE(g_N, a0_si: float = A0_SI):
    """The alternative "simple" interpolation function ``mu(x) = x/(1+x)``.

    Solves ``mu(g/a0)*g = g_N`` algebraically: ``g^2 - g_N*g - g_N*a0 = 0``
    -> ``g = (g_N + sqrt(g_N^2 + 4*g_N*a0)) / 2``.

    **NOT interchangeable with `mond_g_total`** (Plan §8.2): its
    untruncated central phantom column density diverges logarithmically
    (Milgrom 2009 [S2], docs/galaxy_dynamics_scope.md §3). That divergence
    is cited from the source, not independently re-derived numerically
    here -- an ad-hoc numeric attempt at reproducing it (central finite
    differences over a ~10-order-of-magnitude radius range) produced
    unreliable roundoff-dominated results during G3 development and was
    deliberately NOT shipped as a verification check; asserting a
    specific numeric divergence pattern from that calculation would have
    been dishonest given the numerical instability actually observed.
    This function exists only so it is never silently reintroduced as if
    equivalent to `mond_g_total`; `check_simple_interpolation_differs_
    from_standard` in `verify_galaxy_observation_maps.py` only confirms
    the two give measurably different results, not the divergence claim.
    """
    g_N = np.asarray(g_N, dtype=float)
    if np.any(g_N < 0):
        raise ValueError("g_N < 0 is outside the declared MOND control-case scope")
    a0 = accel_si_to_kms2_per_pc(a0_si)
    return (g_N + np.sqrt(g_N**2 + 4.0 * g_N * a0)) / 2.0


def circular_velocity_from_g(g, r_pc):
    """Model-agnostic ``v_c(r) = sqrt(r*g(r))`` (local Newtonian relation).

    Used to check "identische g(r) müssen identische lokale
    Kreisgeschwindigkeiten ergeben" (Plan §8.1) against each profile's own
    `circular_velocity` method, independently of which model sourced `g`.
    """
    g = np.asarray(g, dtype=float)
    r = np.asarray(r_pc, dtype=float)
    if np.any(r <= 0):
        raise ValueError("circular_velocity_from_g requires r > 0")
    if np.any(g < 0):
        raise ValueError("g must be non-negative (inward-directed magnitude)")
    return np.sqrt(r * g)


def baseline_total_g_halo(baryon_g_fn, halo, r_pc):
    """Baseline A/B (Plan §8.3): baryons + a declared spherical halo
    (`halo` is any object with a `.g(r_pc)` method, e.g. `BurkertProfile`
    for Baseline A or `NFWProfile` for Baseline B)."""
    return baryon_g_fn(r_pc) + halo.g(r_pc)


def baseline_total_g_mond(baryon_g_fn, r_pc, a0_si: float = A0_SI):
    """Baseline C (Plan §8.2/§8.3): algebraic MOND relation applied to the
    baryonic Newtonian acceleration alone. Declared here as a comparison
    model for rotation curves ONLY -- not a claim of a complete modified-
    Poisson field solver for disk geometries (Plan §8.2)."""
    g_N = baryon_g_fn(r_pc)
    return mond_g_total(g_N, a0_si=a0_si)
