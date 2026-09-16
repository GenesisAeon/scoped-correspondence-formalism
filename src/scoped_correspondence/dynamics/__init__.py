"""Dynamics core (ex-UTAC): sigmoid response, recovery rate, cubic normal form.

FORMALISM.md §2 rows: beta_response, S_rec, lambda_L (S_rec used here).
FORMALISM.md §4–§5; system_layer_utac.md.
"""

from scoped_correspondence.dynamics.core import (
    CubicNormalForm,
    cusp_field,
    fixed_points,
    recovery_rate_at_equilibrium,
    recovery_rate_from_relaxation,
    sigmoid_response,
)

__all__ = [
    "CubicNormalForm",
    "cusp_field",
    "fixed_points",
    "recovery_rate_at_equilibrium",
    "recovery_rate_from_relaxation",
    "sigmoid_response",
]
