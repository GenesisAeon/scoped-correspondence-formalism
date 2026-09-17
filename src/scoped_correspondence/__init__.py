"""Scoped Correspondence Formalism - review package (Milestones 1-9).

Milestone 1: typed Correspondence contract.
Milestone 2: Observation / Dynamics / Coupling cores + legacy adapters.
Milestone 3: Closure / Reconstruction + Viability / Safe transfer.
Milestone 4: Membership / Shared resources (M_ea, T5).
Milestone 5: Identifiability / Baseline metrics (conditioning, EI, SVD).
Milestone 6: Validation / Cygnus jet_pa_deg real-data pilot.
Milestone 7: Optional modules hardening (contextuality F08/F13, information_decomposition F09/F12).
Milestone 8: Thermodynamics / GENERIC memory (heat e13, stochastic inverse e10, projection §9).
Milestone 9: Metarules (discrete m′=H, priority T5 wrap, unobserved-m closure A/B).

This package does not replace FORMALISM.md or the layer documents; it is a
software adjunct for review. Correspondence / Observation / Dynamics /
Coupling / Closure / Viability / Membership are unchanged from M1-M4.
membership/core.py and closure/core.py are not mutated by M9 — only
wrapped / called.
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
from scoped_correspondence.membership import (
    MembershipMatrix,
    double_count_stocks,
    joint_control_set,
    t10_via_membership,
    view,
)
from scoped_correspondence.identifiability import (
    delay_amplification,
    delay_conditioning_report,
    effective_information_baseline,
    fixed_ensemble_data_processing,
    identifiability_jacobian_rank,
    indistinguishable_delay_vectors,
    parameter_scaling_invariance,
    predictive_states,
    svd_emergence_vs_ei,
)
from scoped_correspondence.validation import (
    DatasetManifest,
    ValidationReport,
    fit_relaxation_pa,
    load_cygnus_epochs,
    persistence_baseline,
    run_cygnus_pilot,
    split_epochs,
)
from scoped_correspondence.contextuality import (
    EmpiricalModel,
    SheafScenario,
    bell_222_scenario,
    chsh_table_i_model,
    classical_factorizable_model,
    contextual_fraction,
    has_global_section,
    pr_box_model,
)
from scoped_correspondence.information_decomposition import (
    blackwell_redundancy_binary_y,
    ei_q_channel,
    i_min_two_sources,
    pid_atoms_williams_beer,
    rb0_blackwell,
    two_bit_copy_report,
)
from scoped_correspondence.thermo import (
    heat_generic_example,
    project_generic_structure,
    stochastic_inverse_not_detailed_balance,
)
from scoped_correspondence.metarules import (
    DESCRIPTIVE_ONLY,
    ENFORCED_RULE,
    MetaRuleUpdate,
    priority_joint_control_set,
    unobserved_metarule_breaks_closure,
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
    # M4 membership
    "MembershipMatrix",
    "double_count_stocks",
    "joint_control_set",
    "t10_via_membership",
    "view",
    # M5 identifiability
    "delay_amplification",
    "delay_conditioning_report",
    "effective_information_baseline",
    "fixed_ensemble_data_processing",
    "identifiability_jacobian_rank",
    "indistinguishable_delay_vectors",
    "parameter_scaling_invariance",
    "predictive_states",
    "svd_emergence_vs_ei",
    # M6 validation
    "DatasetManifest",
    "ValidationReport",
    "fit_relaxation_pa",
    "load_cygnus_epochs",
    "persistence_baseline",
    "run_cygnus_pilot",
    "split_epochs",
    # M7 contextuality (F08 + F13)
    "EmpiricalModel",
    "SheafScenario",
    "bell_222_scenario",
    "chsh_table_i_model",
    "classical_factorizable_model",
    "contextual_fraction",
    "has_global_section",
    "pr_box_model",
    # M7 information_decomposition (F09 + F12)
    "blackwell_redundancy_binary_y",
    "ei_q_channel",
    "i_min_two_sources",
    "pid_atoms_williams_beer",
    "rb0_blackwell",
    "two_bit_copy_report",
    # M8 thermo / GENERIC
    "heat_generic_example",
    "project_generic_structure",
    "stochastic_inverse_not_detailed_balance",
    # M9 metarules
    "DESCRIPTIVE_ONLY",
    "ENFORCED_RULE",
    "MetaRuleUpdate",
    "priority_joint_control_set",
    "unobserved_metarule_breaks_closure",
]

__version__ = "0.9.0a1"
