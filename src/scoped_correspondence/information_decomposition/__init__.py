"""Information decomposition: Williams-Beer PID + Blackwell RB(0) (F09/F12).

FORMALISM adjunct for F09; pid_redundancy_bottleneck.md / F12 TWO_BIT_COPY.
Legacy anchors: verification/verify_pid_rb.py (p01–p07).
"""

from scoped_correspondence.information_decomposition.core import (
    ARXIV_RB,
    ARXIV_WB,
    blackwell_redundancy_binary_y,
    blackwell_redundancy_finite_y,
    compare_to_EI_q,
    ei_q_channel,
    i_min_two_sources,
    pid_atoms,
    pid_atoms_williams_beer,
    rb0_blackwell,
    two_bit_copy_joint,
    two_bit_copy_report,
)

__all__ = [
    "ARXIV_RB",
    "ARXIV_WB",
    "blackwell_redundancy_binary_y",
    "blackwell_redundancy_finite_y",
    "compare_to_EI_q",
    "ei_q_channel",
    "i_min_two_sources",
    "pid_atoms",
    "pid_atoms_williams_beer",
    "rb0_blackwell",
    "two_bit_copy_joint",
    "two_bit_copy_report",
]
