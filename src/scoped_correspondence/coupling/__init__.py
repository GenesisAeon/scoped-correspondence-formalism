"""Coupling core (ex-AFET): pairwise dynamics, A_ij / L_ij, GENERIC check.

FORMALISM.md §2 rows: A_ij, L_ij.
FORMALISM.md §6; coupling_layer_afet.md.

A_ij and L_ij are intentionally separate types with no shared base class —
FORMALISM.md §6: there is no general identity between eta_info, Panarchy,
A_ij and L_ij.

Milestone 12 (Dirac structure composition) and Milestone 15 (Dissipativity /
supply rates) are exported here as **submodule-local** additions; package-root
``scoped_correspondence.__init__`` is intentionally left untouched to avoid
fighting parallel M14/M16 branches.
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
from scoped_correspondence.coupling.dissipativity import (
    STORAGE_INEQUALITY_TOL,
    SOURCE as DISSIPATIVITY_SOURCE,
    DissipativityCertificate,
    check_storage_inequality,
    make_dissipativity_certificate,
    neutral_interconnection_supply,
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
    # M15 Dissipativity / supply rates (submodule-local; avoid M14/M16 fights)
    "STORAGE_INEQUALITY_TOL",
    "DISSIPATIVITY_SOURCE",
    "DissipativityCertificate",
    "check_storage_inequality",
    "make_dissipativity_certificate",
    "neutral_interconnection_supply",
]
