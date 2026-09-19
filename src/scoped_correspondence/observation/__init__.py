"""Observation core (ex-CREP): channel capacity, retention, realized rate.

FORMALISM.md §2 rows: K_info, R_info, eta_info.
FORMALISM.md §3; information_layer_crep.md.

Milestone 22 (Directed Information) and Milestone 25 (Arimoto–Blahut DMC
capacity) are exported here as **submodule-local** additions; package-root
``scoped_correspondence.__init__`` is intentionally left untouched.
``observation.core`` is not edited.
"""

from scoped_correspondence.observation.core import (
    channel_capacity,
    realized_rate,
    retention,
)
from scoped_correspondence.observation.directed_information import (
    SOURCE as DIRECTED_INFORMATION_SOURCE,
    DirectedInformationReport,
    binary_entropy,
    bsc_feedback_joint,
    bsc_feedback_vs_mutual,
    bsc_no_feedback_joint,
    directed_information,
    mutual_information_sequences,
)
from scoped_correspondence.observation.arimoto_blahut import (
    SOURCE as ARIMOTO_BLAHUT_SOURCE,
    SOURCE_ARIMOTO,
    SOURCE_BLAHUT,
    ArimotoBlahutResult,
    blahut_arimoto_capacity,
    bsc_channel,
    mutual_information_dmc,
    z_channel,
    z_channel_capacity_closed_form,
)
from scoped_correspondence.errors import ScopeViolationError

__all__ = [
    "ScopeViolationError",
    "channel_capacity",
    "realized_rate",
    "retention",
    # M22 directed information (submodule-local; package root __init__ untouched)
    "DIRECTED_INFORMATION_SOURCE",
    "DirectedInformationReport",
    "binary_entropy",
    "bsc_feedback_joint",
    "bsc_feedback_vs_mutual",
    "bsc_no_feedback_joint",
    "directed_information",
    "mutual_information_sequences",
    # M25 Arimoto–Blahut DMC capacity (submodule-local; core untouched)
    "ARIMOTO_BLAHUT_SOURCE",
    "SOURCE_ARIMOTO",
    "SOURCE_BLAHUT",
    "ArimotoBlahutResult",
    "blahut_arimoto_capacity",
    "bsc_channel",
    "mutual_information_dmc",
    "z_channel",
    "z_channel_capacity_closed_form",
]
