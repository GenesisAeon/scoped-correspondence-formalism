"""Unit conventions and boundary conversions for the galaxy-dynamics domain.

Content basis: `docs/galaxy_dynamics_scope.md` §1 (fixed numerical
conventions, Plan §5.3).

Internal numerical basis chosen for this package (Plan §5.3: "Im
numerischen Kern eine Einheitenbasis wählen; an Ein- und Ausgabegrenzen
konvertieren"): length in parsec (pc), density in M_sun/pc^3, mass in
M_sun, velocity in km/s. SI and kpc values only ever appear at explicit
conversion calls -- no function in this package silently mixes bases.
"""
from __future__ import annotations

import math

# Fixed computational conventions (not a claim of infinite-precision
# natural constants) -- see docs/galaxy_dynamics_scope.md §1.
G_SI = 6.67430e-11  # m^3 kg^-1 s^-2
PC_M = 3.085677581491367e16  # m
MSUN_KG = 1.98847e30  # kg
A0_SI = 1.2e-10  # m s^-2 -- external MOND input, never fit in this package
G_ASTRO_KPC = 4.301047329314801e-6  # kpc (km/s)^2 M_sun^-1
KPC_PC = 1000.0

# G in the internal (pc, M_sun, km/s) basis. G_ASTRO_KPC is defined for r
# in kpc: v^2 = G_ASTRO_KPC * M / r_kpc. Substituting r_kpc = r_pc/1000
# gives v^2 = (1000*G_ASTRO_KPC) * M / r_pc, so G_pc = 1000 * G_kpc (this
# matches the commonly cited G ~ 4.30091e-3 pc (km/s)^2 M_sun^-1).
G_ASTRO_PC = G_ASTRO_KPC * KPC_PC  # pc (km/s)^2 M_sun^-1


def kpc_to_pc(x_kpc: float) -> float:
    return x_kpc * KPC_PC


def pc_to_kpc(x_pc: float) -> float:
    return x_pc / KPC_PC


def accel_kms2_per_pc_to_si(a_kms2_per_pc: float) -> float:
    """(km/s)^2 / pc -> m/s^2."""
    return a_kms2_per_pc * 1.0e6 / PC_M


def accel_si_to_kms2_per_pc(a_si: float) -> float:
    """m/s^2 -> (km/s)^2 / pc."""
    return a_si * PC_M / 1.0e6


def sigma_msun_pc2_to_si(sigma_msun_pc2: float) -> float:
    """M_sun / pc^2 -> kg / m^2."""
    return sigma_msun_pc2 * MSUN_KG / PC_M**2


def sigma_si_to_msun_pc2(sigma_si: float) -> float:
    """kg / m^2 -> M_sun / pc^2."""
    return sigma_si * PC_M**2 / MSUN_KG


def mond_sigma_star_msun_pc2(a0_si: float = A0_SI) -> float:
    """MOND characteristic surface density Sigma_* = a0/(2 pi G) (Plan §8.2).

    Model-dependent (follows from the external MOND scale a0, not a halo
    measurement) -- see docs/galaxy_dynamics_scope.md §3.
    """
    sigma_si = a0_si / (2.0 * math.pi * G_SI)
    return sigma_si_to_msun_pc2(sigma_si)
