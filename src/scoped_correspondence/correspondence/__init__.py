"""Correspondence core: typed maps between models with scope and residual."""

from scoped_correspondence.correspondence.contract import (
    Correspondence,
    CorrespondenceReport,
    ErrorMetric,
    ModelRef,
    Residual,
    Scope,
    StateMap,
    TimeMap,
)
from scoped_correspondence.correspondence.approximation import (
    FIXED_MAP_BOUND,
    ApproximationCertificate,
    verify_approximate_simulation,
)

__all__ = [
    "Correspondence",
    "CorrespondenceReport",
    "ErrorMetric",
    "ModelRef",
    "Residual",
    "Scope",
    "StateMap",
    "TimeMap",
    # M10 approximation certificates (fixed StateMap specialty)
    "FIXED_MAP_BOUND",
    "ApproximationCertificate",
    "verify_approximate_simulation",
]
