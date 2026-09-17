"""Coupling core (ex-AFET): pairwise dynamics, A_ij / L_ij, GENERIC check.

FORMALISM.md §2 rows: A_ij, L_ij.
FORMALISM.md §6; coupling_layer_afet.md.

A_ij and L_ij are intentionally separate types with no shared base class —
FORMALISM.md §6: there is no general identity between eta_info, Panarchy,
A_ij and L_ij.

Milestone 12 (Dirac structure composition) is exported here as a
**submodule-local** addition; package-root ``scoped_correspondence.__init__``
is intentionally left untouched to avoid fighting parallel M11/M13 branches.
"""

from scoped_correspondence.coupling.core import (
    AijInfluence,
    GENERIC_STRUCTURE_TOL,
    LijTransport,
    PairwiseCoupling,
    check_generic_structure,
)
from scoped_correspondence.coupling.dirac_composition import (
    FEEDBACK,
    SOURCE,
    DiracCompositionResult,
    PowerPreservingInterconnection,
    compose_skew_symmetric,
    interface_power,
    interface_power_under_feedback,
)

__all__ = [
    "AijInfluence",
    "GENERIC_STRUCTURE_TOL",
    "LijTransport",
    "PairwiseCoupling",
    "check_generic_structure",
    # M12 Dirac composition (submodule-local; package root __init__ untouched)
    "FEEDBACK",
    "SOURCE",
    "DiracCompositionResult",
    "PowerPreservingInterconnection",
    "compose_skew_symmetric",
    "interface_power",
    "interface_power_under_feedback",
]
