"""Contextuality core: sheaf CF / global sections with F13 scope guard.

FORMALISM adjunct for F08; sheaf_contextuality.md §§2–6 / F13.
Legacy anchors: verification/verify_sheaf_contextuality.py (s01–s06).
"""

from scoped_correspondence.contextuality.core import (
    ARXIV_AB,
    ARXIV_CF,
    EmpiricalModel,
    F13_SCOPE_RISK,
    SheafScenario,
    bell_222_scenario,
    chsh_table_i_model,
    classical_factorizable_model,
    contextual_fraction,
    has_global_section,
    pr_box_model,
    report,
)
from scoped_correspondence.errors import ScopeViolationError

__all__ = [
    "ARXIV_AB",
    "ARXIV_CF",
    "EmpiricalModel",
    "F13_SCOPE_RISK",
    "ScopeViolationError",
    "SheafScenario",
    "bell_222_scenario",
    "chsh_table_i_model",
    "classical_factorizable_model",
    "contextual_fraction",
    "has_global_section",
    "pr_box_model",
    "report",
]
