"""Thin legacy adapters: historical CREP/UTAC/AFET names -> new APIs.

Does not edit the seven layer/extension markdown documents. Pure software bridge
so worked examples can later call the new core without rewriting documentation.
"""

from scoped_correspondence.legacy.adapters import (
    afet_pairwise_coupling,
    cubic_normal_form,
    cusp_dxdt,
    gamma_domain_style,  # illustrative alias used in the M2 prompt
    generic_structure_check,
    influence_A,
    information_retention_R,
    onsager_L,
    realized_eta,
    shannon_hartley_K,
    utac_recovery_rate,
    utac_sigmoid,
)

__all__ = [
    "afet_pairwise_coupling",
    "cubic_normal_form",
    "cusp_dxdt",
    "gamma_domain_style",
    "generic_structure_check",
    "influence_A",
    "information_retention_R",
    "onsager_L",
    "realized_eta",
    "shannon_hartley_K",
    "utac_recovery_rate",
    "utac_sigmoid",
]
