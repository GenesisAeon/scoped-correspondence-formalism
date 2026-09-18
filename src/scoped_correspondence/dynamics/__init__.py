"""Dynamics core (ex-UTAC): sigmoid response, recovery rate, cubic normal form.

FORMALISM.md §2 rows: beta_response, S_rec, lambda_L (S_rec used here).
FORMALISM.md §4–§5; system_layer_utac.md.

Milestone 14 (Contraction Analysis) is exported here as a **submodule-local**
addition; package-root ``scoped_correspondence.__init__`` is intentionally
left untouched to avoid fighting parallel M15/M16 branches.
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
]
