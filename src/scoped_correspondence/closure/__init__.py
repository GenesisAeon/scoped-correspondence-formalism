"""Closure core: exact/approximate macro-closure, circle reconstruction, CTMC generator lumpability.

FORMALISM.md section 9; emergence_and_closure.md; worked_example_reconstruction.md;
M11: Buchholz 1994 / Michel & Siegle 2024 generator lumpability.
"""

from scoped_correspondence.closure.core import (
    candidate_macro_kernel,
    closure_error,
    demo_matrices,
    is_exact_closure,
    memory_solution,
    partition_matrix,
    projected_memory_rhs,
    propagated_error_bound,
    reconstruct_from_projection,
    total_variation_row,
)
from scoped_correspondence.closure.generator_lumpability import (
    generator_closure_error,
    is_exact_generator_lumpability,
)
from scoped_correspondence.errors import ScopeViolationError

__all__ = [
    "ScopeViolationError",
    "candidate_macro_kernel",
    "closure_error",
    "demo_matrices",
    "generator_closure_error",
    "is_exact_closure",
    "is_exact_generator_lumpability",
    "memory_solution",
    "partition_matrix",
    "projected_memory_rhs",
    "propagated_error_bound",
    "reconstruct_from_projection",
    "total_variation_row",
]
