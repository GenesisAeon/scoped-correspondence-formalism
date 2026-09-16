"""Scoped Correspondence Formalism — review package (Milestone 1).

This package exposes a minimal typed Correspondence contract. It does not
replace FORMALISM.md or the layer documents; it is a software adjunct for review.
"""

from scoped_correspondence.correspondence import (
    Correspondence,
    CorrespondenceReport,
    ErrorMetric,
    ModelRef,
    Residual,
    Scope,
    StateMap,
    TimeMap,
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
]

__version__ = "0.1.0a1"
