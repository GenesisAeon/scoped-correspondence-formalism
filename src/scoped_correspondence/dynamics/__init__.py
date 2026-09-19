"""Dynamics core (ex-UTAC): sigmoid response, recovery rate, cubic normal form.

FORMALISM.md §2 rows: beta_response, S_rec, lambda_L (S_rec used here).
FORMALISM.md §4–§5; system_layer_utac.md.

Milestone 14 (Contraction Analysis) is exported here as a **submodule-local**
addition; package-root ``scoped_correspondence.__init__`` is intentionally
left untouched to avoid fighting parallel M15/M16 branches.

Milestone 29 (Landau Exponent Comparison / Self-Falsification) is likewise
exported submodule-locally; ``dynamics/core.py`` is CALLED only (not edited).

Milestone 36 (Early-Warning / Critical Slowing) exports OU Var / AR(1)
indicators that CALL ``recovery_rate_at_equilibrium`` for ``λ = S_rec``.
"""

from scoped_correspondence.dynamics.core import (
    CubicNormalForm,
    cusp_field,
    fixed_points,
    recovery_rate_at_equilibrium,
    recovery_rate_from_relaxation,
    sigmoid_response,
)
from scoped_correspondence.dynamics.contraction import (
    METRIC_EUCLIDEAN_1D,
    SOURCE as CONTRACTION_SOURCE,
    ContractionCertificate,
    contraction_rate_cusp,
    make_contraction_certificate,
    verify_contraction_bound,
)
from scoped_correspondence.dynamics.landau import (
    ISING_2D_BETA,
    MEAN_FIELD_BETA,
    ONSAGER_SIGMA_WARNING,
    SOURCE as LANDAU_SOURCE,
    ScalingExponentComparison,
    compare_scaling_exponents,
    mean_field_order_parameter,
    onsager_critical_ratio,
)
from scoped_correspondence.dynamics.early_warning import (
    EARLY_WARNING_COUNTEREXAMPLE_FENCE,
    SOURCE as EARLY_WARNING_SOURCE,
    EarlyWarningIndicators,
    control_far_from_fold,
    early_warning_at_cusp,
    estimate_lambda_from_ar1,
    lambda_from_cusp_equilibrium,
    ou_autocorrelation,
    ou_variance,
)

__all__ = [
    "CubicNormalForm",
    "cusp_field",
    "fixed_points",
    "recovery_rate_at_equilibrium",
    "recovery_rate_from_relaxation",
    "sigmoid_response",
    # M14 contraction analysis (submodule-local; package root __init__ untouched)
    "METRIC_EUCLIDEAN_1D",
    "CONTRACTION_SOURCE",
    "ContractionCertificate",
    "contraction_rate_cusp",
    "make_contraction_certificate",
    "verify_contraction_bound",
    # M29 Landau exponent comparison / self-falsification
    "MEAN_FIELD_BETA",
    "ISING_2D_BETA",
    "ONSAGER_SIGMA_WARNING",
    "LANDAU_SOURCE",
    "ScalingExponentComparison",
    "mean_field_order_parameter",
    "onsager_critical_ratio",
    "compare_scaling_exponents",
    # M36 Early-Warning / critical slowing (OU Var + AR(1); CALL S_rec)
    "EARLY_WARNING_COUNTEREXAMPLE_FENCE",
    "EARLY_WARNING_SOURCE",
    "EarlyWarningIndicators",
    "ou_variance",
    "ou_autocorrelation",
    "estimate_lambda_from_ar1",
    "lambda_from_cusp_equilibrium",
    "early_warning_at_cusp",
    "control_far_from_fold",
]
