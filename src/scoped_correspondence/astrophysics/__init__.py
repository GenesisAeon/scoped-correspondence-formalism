"""Galaxy-dynamics domain (G0-G7).

Content basis: `prompts/Answers/nicht_stationäre_Treiber/
SCF_GALAXY_DYNAMICS_IMPLEMENTATION_PLAN.md` and
`docs/galaxy_dynamics_scope.md` (G0 source/units/hypothesis register).

This subpackage is additive: it does not modify any existing SCF module.
See `GALAXY_DYNAMICS_ROADMAP.md` for package status (G1 in progress).
"""
from __future__ import annotations

from .spherical_profiles import BurkertProfile, NFWProfile, PseudoIsothermalProfile
from .units import (
    A0_SI,
    G_ASTRO_KPC,
    G_ASTRO_PC,
    G_SI,
    MSUN_KG,
    PC_M,
    accel_kms2_per_pc_to_si,
    accel_si_to_kms2_per_pc,
    kpc_to_pc,
    mond_sigma_star_msun_pc2,
    pc_to_kpc,
    sigma_msun_pc2_to_si,
    sigma_si_to_msun_pc2,
)

__all__ = [
    "BurkertProfile",
    "NFWProfile",
    "PseudoIsothermalProfile",
    "A0_SI",
    "G_ASTRO_KPC",
    "G_ASTRO_PC",
    "G_SI",
    "MSUN_KG",
    "PC_M",
    "accel_kms2_per_pc_to_si",
    "accel_si_to_kms2_per_pc",
    "kpc_to_pc",
    "mond_sigma_star_msun_pc2",
    "pc_to_kpc",
    "sigma_msun_pc2_to_si",
    "sigma_si_to_msun_pc2",
]
