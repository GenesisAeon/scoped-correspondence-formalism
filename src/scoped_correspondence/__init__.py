"""Scoped Correspondence Formalism - review package (Milestones 1-3).

Milestone 1: typed Correspondence contract.
Milestone 2: Observation / Dynamics / Coupling cores + legacy adapters.
Milestone 3: Closure / Reconstruction + Viability / Safe transfer.

This package does not replace FORMALISM.md or the layer documents; it is a
software adjunct for review. Correspondence / Observation / Dynamics /
Coupling are unchanged from M1-M2.
"""

from scoped_correspondence.correspondence import (
    Correspondence,
    CorrespondenceReport,
    ErrorMetric,
    ModelRef,
    Residual,
    Scope,
    StateMap,
    TimeMap,
)
from scoped_correspondence.errors import ScopeViolationError
from scoped_correspondence.observation import (
    channel_capacity,
    realized_rate,
    retention,
)
from scoped_correspondence.dynamics import (
    CubicNormalForm,
    cusp_field,
    fixed_points,
    recovery_rate_at_equilibrium,
    recovery_rate_from_relaxation,
    sigmoid_response,
)
from scoped_correspondence.coupling import (
    AijInfluence,
    GENERIC_STRUCTURE_TOL,
    LijTransport,
    PairwiseCoupling,
    check_generic_structure,
)
from scoped_correspondence.closure import (
    candidate_macro_kernel,
    closure_error,
    demo_matrices,
    is_exact_closure,
    memory_solution,
    partition_matrix,
    projected_memory_rhs,
    propagated_error_bound,
    reconstruct_from_projection,
    total_variation_row,
)
from scoped_correspondence.viability import (
    coupled_buffer_field,
    has_safe_transfer,
    orthant_action_demand,
    scalar_hitting_time,
    scalar_solution,
    shared_budget_conflict,
    unequal_rates_sum_derivatives,
)

__all__ = [
    # M1 correspondence
    "Correspondence",
    "CorrespondenceReport",
    "ErrorMetric",
    "ModelRef",
    "Residual",
    "Scope",
    "StateMap",
    "TimeMap",
    # errors
    "ScopeViolationError",
    # M2 observation
    "channel_capacity",
    "realized_rate",
    "retention",
    # M2 dynamics
    "CubicNormalForm",
    "cusp_field",
    "fixed_points",
    "recovery_rate_at_equilibrium",
    "recovery_rate_from_relaxation",
    "sigmoid_response",
    # M2 coupling
    "AijInfluence",
    "GENERIC_STRUCTURE_TOL",
    "LijTransport",
    "PairwiseCoupling",
    "check_generic_structure",
    # M3 closure
    "candidate_macro_kernel",
    "closure_error",
    "demo_matrices",
    "is_exact_closure",
    "memory_solution",
    "partition_matrix",
    "projected_memory_rhs",
    "propagated_error_bound",
    "reconstruct_from_projection",
    "total_variation_row",
    # M3 viability
    "coupled_buffer_field",
    "has_safe_transfer",
    "orthant_action_demand",
    "scalar_hitting_time",
    "scalar_solution",
    "shared_budget_conflict",
    "unequal_rates_sum_derivatives",
]

__version__ = "0.3.0a1"
