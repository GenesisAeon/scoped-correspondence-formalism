"""Shared scope / contract errors for the review package."""

from __future__ import annotations


class ScopeViolationError(ValueError):
    """Raised when a quantity is requested outside its declared validity domain.

    Used especially for Observation formulas that are only defined for discrete
    variables with finite positive entropy (FORMALISM.md §3), and for
    unit/time mismatches on eta_info.
    """

