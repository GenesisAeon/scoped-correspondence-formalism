"""Contextuality: sheaf CF / global sections (core) + CSW (M19) + Čech (M24).

FORMALISM adjunct for F08; sheaf_contextuality.md §§2–6 / F13.
Legacy anchors: verification/verify_sheaf_contextuality.py (s01–s06).

M19: Cabello–Severini–Winter 2014 PRL 112, 040401 graph invariants
(α / θ / α* on exclusivity graphs; C5 specialization). Does **not** mutate
``contextuality/core.py`` and does **not** identify the fractional-packing
LP with ``contextual_fraction``.

M24: Abramsky–Mansfield–Barbosa 2012 arXiv:1111.3620 relative Čech
obstruction over Z_2. Does **not** mutate ``core.py`` / ``csw.py``; does
**not** invert a vanishing obstruction into a noncontextuality certificate.
"""

from scoped_correspondence.contextuality.core import (
    ARXIV_AB,
    ARXIV_CF,
    EmpiricalModel,
    F13_SCOPE_RISK,
    SheafScenario,
    bell_222_scenario,
    chsh_table_i_model,
    classical_factorizable_model,
    contextual_fraction,
    has_global_section,
    pr_box_model,
    report,
)
from scoped_correspondence.contextuality.csw import (
    ARXIV as CSW_ARXIV,
    BOUND_TOL,
    PRL_DOI,
    SOURCE as CSW_SOURCE,
    THETA_TOL,
    CSWWitness,
    ExclusivityGraph,
    c5,
    csw_invariants,
    csw_witness,
    cycle_graph,
    fractional_packing_number,
    independence_number,
    lovasz_theta,
    lovasz_theta_c5_report,
    report as csw_report,
    symmetric_c5_model,
)
from scoped_correspondence.contextuality.cohomology import (
    ARXIV as CECH_ARXIV,
    COEFFICIENT_RING,
    DEGREE as CECH_DEGREE,
    SOURCE as CECH_SOURCE,
    CohomologyWitness,
    cech_obstruction,
    cech_witness,
    report as cech_report,
)
from scoped_correspondence.errors import ScopeViolationError

__all__ = [
    # core (unchanged exports)
    "ARXIV_AB",
    "ARXIV_CF",
    "EmpiricalModel",
    "F13_SCOPE_RISK",
    "ScopeViolationError",
    "SheafScenario",
    "bell_222_scenario",
    "chsh_table_i_model",
    "classical_factorizable_model",
    "contextual_fraction",
    "has_global_section",
    "pr_box_model",
    "report",
    # M19 CSW graph invariants (Cabello / Severini / Winter 2014)
    "BOUND_TOL",
    "CSW_ARXIV",
    "CSW_SOURCE",
    "CSWWitness",
    "ExclusivityGraph",
    "PRL_DOI",
    "THETA_TOL",
    "c5",
    "csw_invariants",
    "csw_report",
    "csw_witness",
    "cycle_graph",
    "fractional_packing_number",
    "independence_number",
    "lovasz_theta",
    "lovasz_theta_c5_report",
    "symmetric_c5_model",
    # M24 Čech cohomology witness (Abramsky / Mansfield / Barbosa 2012)
    "CECH_ARXIV",
    "CECH_DEGREE",
    "CECH_SOURCE",
    "COEFFICIENT_RING",
    "CohomologyWitness",
    "cech_obstruction",
    "cech_report",
    "cech_witness",
]
