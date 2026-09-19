"""Viability — safe intervention transfer (core) + CBF (M16) + Nagumo (M28).

context_transformations.md section 8; worked_example_viability.md.
M16: scalar zeroing CBF (Ames et al. 2017 / 2019 ECC survey).
M28: Nagumo tangent-cone condition for polyhedra (Nagumo 1942).
Does not mutate ``viability/core.py``. Does not link CBF/Nagumo as a new
formula to ``has_safe_transfer``. M28 covers non-smooth polyhedra — a
different case class from M16, not a replacement.
"""

from scoped_correspondence.viability.core import (
    coupled_buffer_field,
    has_safe_transfer,
    orthant_action_demand,
    scalar_hitting_time,
    scalar_solution,
    shared_budget_conflict,
    unequal_rates_sum_derivatives,
)
from scoped_correspondence.viability.control_barrier import (
    ALPHA_LINEAR,
    SOURCE as CBF_SOURCE,
    BarrierCertificate,
    BarrierFunction,
    admissible_controls_cbf,
    cbf_condition,
    make_identity_barrier,
    verify_forward_invariance,
)
from scoped_correspondence.viability.nagumo import (
    SOURCE as NAGUMO_SOURCE,
    active_constraints,
    tangent_cone_condition,
    verify_polyhedral_viability,
)
from scoped_correspondence.errors import ScopeViolationError

__all__ = [
    # core (unchanged)
    "ScopeViolationError",
    "coupled_buffer_field",
    "has_safe_transfer",
    "orthant_action_demand",
    "scalar_hitting_time",
    "scalar_solution",
    "shared_budget_conflict",
    "unequal_rates_sum_derivatives",
    # M16 Control Barrier Functions (Ames et al. 2017 / 2019)
    "ALPHA_LINEAR",
    "CBF_SOURCE",
    "BarrierCertificate",
    "BarrierFunction",
    "admissible_controls_cbf",
    "cbf_condition",
    "make_identity_barrier",
    "verify_forward_invariance",
    # M28 Nagumo tangent cone for polyhedra (Nagumo 1942)
    "NAGUMO_SOURCE",
    "active_constraints",
    "tangent_cone_condition",
    "verify_polyhedral_viability",
]
