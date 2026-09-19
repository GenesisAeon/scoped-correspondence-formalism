"""Membership core: overlapping belonging, double-count guard, joint control T5.

context_transformations.md sections 1, 2, and 6.

M27: Formal Concept Analysis (Ganter & Wille 1999) on MembershipMatrix —
see ``formal_concept_analysis`` (does not mutate ``core.py``).
"""

from scoped_correspondence.membership.core import (
    MembershipMatrix,
    double_count_stocks,
    joint_control_set,
    t10_via_membership,
    view,
)
from scoped_correspondence.membership.formal_concept_analysis import (
    DOI as FCA_DOI,
    SOURCE as FCA_SOURCE,
    all_concepts,
    attribute_implication_from_extents,
    derive_down,
    derive_up,
    is_concept,
)
from scoped_correspondence.errors import ScopeViolationError

__all__ = [
    "ScopeViolationError",
    "MembershipMatrix",
    "double_count_stocks",
    "joint_control_set",
    "t10_via_membership",
    "view",
    # M27 Formal Concept Analysis (Ganter & Wille 1999)
    "FCA_DOI",
    "FCA_SOURCE",
    "all_concepts",
    "attribute_implication_from_extents",
    "derive_down",
    "derive_up",
    "is_concept",
]
