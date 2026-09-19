"""Dynamics core (ex-UTAC): sigmoid response, recovery rate, cubic normal form.

FORMALISM.md §2 rows: beta_response, S_rec, lambda_L (S_rec used here).
FORMALISM.md §4–§5; system_layer_utac.md.

Milestone 14 (Contraction Analysis) is exported here as a **submodule-local**
addition; package-root ``scoped_correspondence.__init__`` is intentionally
left untouched to avoid fighting parallel M15/M16 branches.

Milestone 29 (Landau Exponent Comparison / Self-Falsification) is likewise
exported submodule-locally; ``dynamics/core.py`` is CALLED only (not edited).

Milestone 35 (Panarchy / Adaptive-Cycle as Cusp extension) is likewise
exported submodule-locally; ``dynamics/core.py`` is CALLED only
(``fixed_points`` + ``CubicNormalForm.discriminant``); does NOT revive
V≡Panarchy≡Onsager-L.
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
from scoped_correspondence.dynamics.panarchy_cusp import (
    PANARCHY_V_ONSAGER_WARNING,
    SOURCE as PANARCHY_SOURCE,
    HysteresisSample,
    HysteresisSweepResult,
    control_path_no_fold_crossing,
    fold_thresholds,
    hysteresis_sweep,
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
    # M35 Panarchy / Adaptive-Cycle as Cusp extension
    "PANARCHY_V_ONSAGER_WARNING",
    "PANARCHY_SOURCE",
    "HysteresisSample",
    "HysteresisSweepResult",
    "fold_thresholds",
    "hysteresis_sweep",
    "control_path_no_fold_crossing",
]
