"""Coupling core (ex-AFET): pairwise dynamics, A_ij / L_ij, GENERIC check.

FORMALISM.md §2 rows: A_ij, L_ij.
FORMALISM.md §6; coupling_layer_afet.md.

A_ij and L_ij are intentionally separate types with no shared base class —
FORMALISM.md §6: there is no general identity between eta_info, Panarchy,
A_ij and L_ij.

Milestone 12 (Dirac structure composition), Milestone 15 (Dissipativity /
supply rates), Milestone 26 (Lie–Poisson / Casimir invariants),
Milestone 38 (GENERIC ↔ Navier–Stokes viscous dissipation), and
Milestone 39 (Pecora–Carroll generalized / drive–response sync) are
exported here as **submodule-local** additions; package-root
``scoped_correspondence.__init__`` is intentionally left untouched.
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
from scoped_correspondence.coupling.casimir import (
    ARNOLD_DOI,
    CASIMIR_RESIDUAL_TOL,
    MARSDEN_RATIU_DOI,
    SOURCE as CASIMIR_SOURCE,
    casimir_residual,
    compare_to_generic_J_grad_S,
    hat_map,
    lie_poisson_vector_field,
    quadratic_casimir_grad,
    rigid_body_hamiltonian_grad,
    time_derivative_along_field,
)
from scoped_correspondence.coupling.generic_navier_stokes import (
    BARHAM_MORRISON_ZAIDNI_2025_DOI,
    FRICTION_NOT_AIJ_LIJ_WARNING,
    GRMELA_OTTINGER_I_DOI,
    ILLUSTRATIVE_ETA_PA_S,
    ILLUSTRATIVE_ZETA_NOTE,
    MORRISON_1984_DOI,
    OTTINGER_GRMELA_II_DOI,
    SOURCE as GENERIC_NS_SOURCE,
    as_report as generic_ns_as_report,
    two_cell_viscous_example,
)

from scoped_correspondence.coupling.generalized_sync import (
    BRIDGE_NOTE as GENERALIZED_SYNC_BRIDGE_NOTE,
    DOI as GENERALIZED_SYNC_DOI,
    LUHMANN_DISCLAIMER,
    SOURCE as GENERALIZED_SYNC_SOURCE,
    LinearDriveResponseResult,
    conditional_lyapunov_linear,
    linear_drive_response_map,
    sync_criterion_cle_negative,
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
    # M15 Dissipativity / supply rates (submodule-local)
    "STORAGE_INEQUALITY_TOL",
    "DISSIPATIVITY_SOURCE",
    "DissipativityCertificate",
    "check_storage_inequality",
    "make_dissipativity_certificate",
    "neutral_interconnection_supply",
    # M26 Lie–Poisson / Casimir (submodule-local; core.py CALL-only)
    "ARNOLD_DOI",
    "CASIMIR_RESIDUAL_TOL",
    "MARSDEN_RATIU_DOI",
    "CASIMIR_SOURCE",
    "casimir_residual",
    "compare_to_generic_J_grad_S",
    "hat_map",
    "lie_poisson_vector_field",
    "quadratic_casimir_grad",
    "rigid_body_hamiltonian_grad",
    "time_derivative_along_field",
    # M38 GENERIC ↔ Navier–Stokes viscous dissipation (submodule-local; core.py CALL-only)
    "BARHAM_MORRISON_ZAIDNI_2025_DOI",
    "FRICTION_NOT_AIJ_LIJ_WARNING",
    "GRMELA_OTTINGER_I_DOI",
    "ILLUSTRATIVE_ETA_PA_S",
    "ILLUSTRATIVE_ZETA_NOTE",
    "MORRISON_1984_DOI",
    "OTTINGER_GRMELA_II_DOI",
    "GENERIC_NS_SOURCE",
    "generic_ns_as_report",
    "two_cell_viscous_example",
    # M39 Pecora–Carroll generalized sync (submodule-local; core.py untouched)
    "GENERALIZED_SYNC_BRIDGE_NOTE",
    "GENERALIZED_SYNC_DOI",
    "LUHMANN_DISCLAIMER",
    "GENERALIZED_SYNC_SOURCE",
    "LinearDriveResponseResult",
    "conditional_lyapunov_linear",
    "linear_drive_response_map",
    "sync_criterion_cle_negative",
]
