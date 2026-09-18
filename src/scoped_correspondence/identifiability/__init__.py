"""Identifiability core: conditioning, non-identifiability, EI baselines.

FORMALISM.md sections 10 and 12; legacy e02, e07, e08, e09, e12 (optional e15).

Milestone 20 (Profile Likelihood) is exported here as a **submodule-local**
addition; package-root ``scoped_correspondence.__init__`` is intentionally
left untouched. ``identifiability.core`` is not edited.
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
from scoped_correspondence.identifiability.profile_likelihood import (
    SOURCE as PROFILE_LIKELIHOOD_SOURCE,
    classify_identifiability,
    likelihood_interval,
    profile_parameter,
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
    # M20 profile likelihood (submodule-local; package root __init__ untouched)
    "PROFILE_LIKELIHOOD_SOURCE",
    "classify_identifiability",
    "likelihood_interval",
    "profile_parameter",
]
