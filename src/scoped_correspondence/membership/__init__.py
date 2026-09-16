"""Membership core: overlapping belonging, double-count guard, joint control T5.

context_transformations.md sections 1, 2, and 6.
"""

from scoped_correspondence.membership.core import (
    MembershipMatrix,
    double_count_stocks,
    joint_control_set,
    t10_via_membership,
    view,
)
from scoped_correspondence.errors import ScopeViolationError

__all__ = [
    "ScopeViolationError",
    "MembershipMatrix",
    "double_count_stocks",
    "joint_control_set",
    "t10_via_membership",
    "view",
]
