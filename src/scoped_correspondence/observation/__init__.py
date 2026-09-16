"""Observation core (ex-CREP): channel capacity, retention, realized rate.

FORMALISM.md §2 rows: K_info, R_info, eta_info.
FORMALISM.md §3; information_layer_crep.md.
"""

from scoped_correspondence.observation.core import (
    channel_capacity,
    realized_rate,
    retention,
)
from scoped_correspondence.errors import ScopeViolationError

__all__ = [
    "ScopeViolationError",
    "channel_capacity",
    "realized_rate",
    "retention",
]
