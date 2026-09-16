"""Scoped Correspondence Formalism — review package (Milestones 1–2).

Milestone 1: typed Correspondence contract.
Milestone 2: Observation / Dynamics / Coupling cores + legacy adapters.

This package does not replace FORMALISM.md or the layer documents; it is a
software adjunct for review. Correspondence is unchanged from M1.
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
from scoped_correspondence.errors import ScopeViolationError
from scoped_correspondence.observation import (
    channel_capacity,
    realized_rate,
    retention,
)
from scoped_correspondence.dynamics import (
    CubicNormalForm,
    cusp_field,
    fixed_points,
    recovery_rate_at_equilibrium,
    recovery_rate_from_relaxation,
    sigmoid_response,
)
from scoped_correspondence.coupling import (
    AijInfluence,
    GENERIC_STRUCTURE_TOL,
    LijTransport,
    PairwiseCoupling,
    check_generic_structure,
)

__all__ = [
    # M1 correspondence
    "Correspondence",
    "CorrespondenceReport",
    "ErrorMetric",
    "ModelRef",
    "Residual",
    "Scope",
    "StateMap",
    "TimeMap",
    # errors
    "ScopeViolationError",
    # M2 observation
    "channel_capacity",
    "realized_rate",
    "retention",
    # M2 dynamics
    "CubicNormalForm",
    "cusp_field",
    "fixed_points",
    "recovery_rate_at_equilibrium",
    "recovery_rate_from_relaxation",
    "sigmoid_response",
    # M2 coupling
    "AijInfluence",
    "GENERIC_STRUCTURE_TOL",
    "LijTransport",
    "PairwiseCoupling",
    "check_generic_structure",
]

__version__ = "0.2.0a1"
