"""Coupling core (ex-AFET): pairwise dynamics, A_ij / L_ij, GENERIC check.

FORMALISM.md §2 rows: A_ij, L_ij.
FORMALISM.md §6; coupling_layer_afet.md.

A_ij and L_ij are intentionally separate types with no shared base class —
FORMALISM.md §6: there is no general identity between eta_info, Panarchy,
A_ij and L_ij.
"""

from scoped_correspondence.coupling.core import (
    AijInfluence,
    GENERIC_STRUCTURE_TOL,
    LijTransport,
    PairwiseCoupling,
    check_generic_structure,
)

__all__ = [
    "AijInfluence",
    "GENERIC_STRUCTURE_TOL",
    "LijTransport",
    "PairwiseCoupling",
    "check_generic_structure",
]
