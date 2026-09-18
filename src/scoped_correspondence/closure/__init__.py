"""Closure core: exact/approximate macro-closure, circle reconstruction, CTMC generator lumpability,
formal reduction error bounds (M21).

FORMALISM.md section 9; emergence_and_closure.md; worked_example_reconstruction.md;
M11: Buchholz 1994 / Michel & Siegle 2024 generator lumpability;
M21: Michel & Siegle 2024 formal reduction error bounds (arXiv:2403.07618).
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
from scoped_correspondence.closure.error_bounds import (
    ReductionErrorBound,
    compare_to_propagated_error_bound,
    paper_example_matrices,
    residual_inf_norm,
    stationary_reduction_bound,
    transient_reduction_bound,
)
from scoped_correspondence.closure.generator_lumpability import (
    generator_closure_error,
    is_exact_generator_lumpability,
)
from scoped_correspondence.errors import ScopeViolationError

__all__ = [
    "ScopeViolationError",
    "ReductionErrorBound",
    "candidate_macro_kernel",
    "closure_error",
    "compare_to_propagated_error_bound",
    "demo_matrices",
    "generator_closure_error",
    "is_exact_closure",
    "is_exact_generator_lumpability",
    "memory_solution",
    "paper_example_matrices",
    "partition_matrix",
    "projected_memory_rhs",
    "propagated_error_bound",
    "reconstruct_from_projection",
    "residual_inf_norm",
    "stationary_reduction_bound",
    "total_variation_row",
    "transient_reduction_bound",
]
