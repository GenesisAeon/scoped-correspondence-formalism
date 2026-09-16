"""Viability core: safe intervention transfer and shared-budget conflict.

context_transformations.md section 8; worked_example_viability.md.
Not a general viability-kernel solver.
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
from scoped_correspondence.errors import ScopeViolationError

__all__ = [
    "ScopeViolationError",
    "coupled_buffer_field",
    "has_safe_transfer",
    "orthant_action_demand",
    "scalar_hitting_time",
    "scalar_solution",
    "shared_budget_conflict",
    "unequal_rates_sum_derivatives",
]
