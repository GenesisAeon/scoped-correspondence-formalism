"""Identifiability core: conditioning, non-identifiability, EI baselines.

FORMALISM.md sections 10 and 12; legacy e02, e07, e08, e09, e12 (optional e15).

Milestone 20 (Profile Likelihood) and Milestone 23 (Fisher-Information
Sloppiness) are exported here as **submodule-local** additions; package-root
``scoped_correspondence.__init__`` is intentionally left untouched.
``identifiability.core`` and ``profile_likelihood`` are not edited by M23.

Milestone 47 (NLP Profile Likelihood, MECHANISTIC_VALIDATION_ROADMAP.md
package 1) is likewise exported submodule-locally; ``profile_likelihood.py``
is CALLED only (``classify_identifiability``/``likelihood_interval`` reused
directly, its own ``profile_parameter``'s 1-free-parameter restriction is
untouched) -- it generalizes profiling to models with more than one free
parameter via a real bounded NLP solver instead of 1-D golden section.
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
from scoped_correspondence.identifiability.fim_sloppiness import (
    SOURCE as FIM_SLOPPINESS_SOURCE,
    PRL_DOI as FIM_TRANSTRUM_DOI,
    RAJU_DOI as FIM_RAJU_DOI,
    eigenspectrum_report,
    exponential_decay_jacobian,
    fisher_information_matrix,
)
from scoped_correspondence.identifiability.profile_likelihood_nlp import (
    profile_parameter_nlp,
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
    # M23 Fisher-information sloppiness (submodule-local; core/PL untouched)
    "FIM_SLOPPINESS_SOURCE",
    "FIM_TRANSTRUM_DOI",
    "FIM_RAJU_DOI",
    "eigenspectrum_report",
    "exponential_decay_jacobian",
    "fisher_information_matrix",
    # M47 NLP profile likelihood (MECHANISTIC_VALIDATION_ROADMAP.md package 1)
    "profile_parameter_nlp",
]
