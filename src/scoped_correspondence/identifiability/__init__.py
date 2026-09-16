"""Identifiability core: conditioning, non-identifiability, EI baselines.

FORMALISM.md sections 10 and 12; legacy e02, e07, e08, e09, e12 (optional e15).
"""

from scoped_correspondence.identifiability.core import (
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
from scoped_correspondence.errors import ScopeViolationError

__all__ = [
    "ScopeViolationError",
    "delay_amplification",
    "delay_conditioning_report",
    "effective_information_baseline",
    "fixed_ensemble_data_processing",
    "identifiability_jacobian_rank",
    "indistinguishable_delay_vectors",
    "parameter_scaling_invariance",
    "predictive_states",
    "svd_emergence_vs_ei",
]
