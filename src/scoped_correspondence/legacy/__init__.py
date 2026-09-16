"""Thin legacy adapters: historical CREP/UTAC/AFET/closure/viability names -> new APIs.

Does not edit the seven layer/extension markdown documents. Pure software bridge
so worked examples can later call the new core without rewriting documentation.
"""

from scoped_correspondence.legacy.adapters import (
    afet_pairwise_coupling,
    buffer_field,
    budget_conflict,
    circle_reconstruct,
    cubic_normal_form,
    cusp_dxdt,
    delta_cl,
    exact_closure_PC_CQ,
    gamma_domain_style,  # illustrative alias used in the M2 prompt
    generic_structure_check,
    influence_A,
    information_retention_R,
    onsager_L,
    realized_eta,
    safe_transfer_scalar,
    shannon_hartley_K,
    tv_horizon_bound,
    utac_recovery_rate,
    utac_sigmoid,
)

__all__ = [
    "afet_pairwise_coupling",
    "buffer_field",
    "budget_conflict",
    "circle_reconstruct",
    "cubic_normal_form",
    "cusp_dxdt",
    "delta_cl",
    "exact_closure_PC_CQ",
    "gamma_domain_style",
    "generic_structure_check",
    "influence_A",
    "information_retention_R",
    "onsager_L",
    "realized_eta",
    "safe_transfer_scalar",
    "shannon_hartley_K",
    "tv_horizon_bound",
    "utac_recovery_rate",
    "utac_sigmoid",
]
