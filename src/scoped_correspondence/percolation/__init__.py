"""Percolation / Kesten / Bethe-tree branching (Milestone 32).

Fisher & Essam 1961; Kesten 1980. Exact Bethe-tree ``p_c = 1/m`` and
extinction fixed point ``Q = (1-p+p Q)^m`` — no Monte-Carlo on ``Z²``.
"""

from scoped_correspondence.percolation.core import (
    EXTINCTION_Q0,
    ONE_SIXTEENTH_COINCIDENCE_WARNING,
    SOURCE,
    THRESHOLD_KINSHIP_WARNING,
    as_report,
    critical_probability_tree,
    extinction_probability,
    percolation_probability,
)

__all__ = [
    "EXTINCTION_Q0",
    "ONE_SIXTEENTH_COINCIDENCE_WARNING",
    "SOURCE",
    "THRESHOLD_KINSHIP_WARNING",
    "as_report",
    "critical_probability_tree",
    "extinction_probability",
    "percolation_probability",
]
