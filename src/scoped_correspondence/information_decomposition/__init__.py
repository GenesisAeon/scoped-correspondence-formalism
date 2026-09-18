"""Information decomposition: Williams-Beer PID + Blackwell RB(0) + BROJA (F09/F12/M17).

FORMALISM adjunct for F09; pid_redundancy_bottleneck.md / F12 TWO_BIT_COPY.
BROJA bivariate unique information: Bertschinger et al. 2014 DOI 10.3390/e16042161.
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
from scoped_correspondence.information_decomposition.broja import (
    ARXIV as ARXIV_BROJA,
    DOI as DOI_BROJA,
    SOURCE as SOURCE_BROJA,
    BivariatePIDReport,
    broja_pid_bivariate,
    two_bit_copy_broja_report,
)

__all__ = [
    "ARXIV_RB",
    "ARXIV_WB",
    "ARXIV_BROJA",
    "DOI_BROJA",
    "SOURCE_BROJA",
    "BivariatePIDReport",
    "blackwell_redundancy_binary_y",
    "blackwell_redundancy_finite_y",
    "broja_pid_bivariate",
    "compare_to_EI_q",
    "ei_q_channel",
    "i_min_two_sources",
    "pid_atoms",
    "pid_atoms_williams_beer",
    "rb0_blackwell",
    "two_bit_copy_broja_report",
    "two_bit_copy_joint",
    "two_bit_copy_report",
]
