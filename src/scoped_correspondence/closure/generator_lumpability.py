"""Continuous-time Markov generator lumpability (Milestone 11).

Exact condition: Q C = C Q_macro for infinitesimal generator Q and partition
matrix C. Calls ``partition_matrix`` from closure.core only — does not mutate
closure/core.py.

Sources:
  - Buchholz 1994, DOI 10.1017/S0021900200107338
  - Michel & Siegle 2024, DOI 10.1016/j.peva.2024.102464 / arXiv 2403.07618
"""

from __future__ import annotations

from typing import Sequence, Union

import numpy as np

from scoped_correspondence.errors import ScopeViolationError

ArrayLike = Union[np.ndarray, Sequence[Sequence[float]], Sequence[float]]


def _as_float_matrix(a: ArrayLike) -> np.ndarray:
    m = np.asarray(a, dtype=float)
    if m.ndim != 2:
        raise ScopeViolationError(f"expected 2D matrix, got shape {m.shape}")
    if not np.isfinite(m).all():
        raise ScopeViolationError("matrix must be finite")
    return m


def _validate_generator(q: np.ndarray) -> None:
    """Row-sum ~0 and off-diagonal entries >= 0 (CTMC infinitesimal generator)."""
    if q.shape[0] != q.shape[1]:
        raise ScopeViolationError(f"Q must be square; got {q.shape}")
    row_sums = q.sum(axis=1)
    if not np.allclose(row_sums, 0.0, atol=1e-10, rtol=0.0):
        raise ScopeViolationError(
            "Q row sums must be ~0 (infinitesimal generator); got " + repr(row_sums)
        )
    n = q.shape[0]
    off = q.copy()
    np.fill_diagonal(off, 0.0)
    if (off < -1e-15).any():
        raise ScopeViolationError(
            "Q off-diagonal entries must be >= 0 (transition rates)"
        )
    # Diagonals should be <= 0 for a rate matrix; implied by row-sum 0 + off>=0,
    # but reject explicit positive diagonals that sneak past float noise.
    if (np.diag(q) > 1e-12).any():
        raise ScopeViolationError("Q diagonal entries must be <= 0")


def is_exact_generator_lumpability(
    Q: ArrayLike,
    C: ArrayLike,
    Q_macro: ArrayLike,
    tol: float = 1e-10,
) -> bool:
    """Exact CTMC generator lumpability: Q C = C Q_macro.

    Q is an N x N infinitesimal generator (row sums ~0, off-diag >= 0),
    C is N x M partition (one 1 per row; from ``partition_matrix``),
    Q_macro is M x M candidate macro generator.

    Returns True iff max |Q C - C Q_macro| <= tol (absolute elementwise).
    """
    q = _as_float_matrix(Q)
    c = _as_float_matrix(C)
    q_macro = _as_float_matrix(Q_macro)
    _validate_generator(q)
    if tol < 0:
        raise ScopeViolationError(f"tol must be >= 0; got {tol!r}")
    if c.shape[0] != q.shape[0]:
        raise ScopeViolationError("C rows must match Q dimension")
    if q_macro.shape != (c.shape[1], c.shape[1]):
        raise ScopeViolationError("Q_macro must be M x M with M = C.columns")
    # Macro candidate should also be a generator when exact; validate softly
    # only when claiming exact equality at the given tol.
    return bool(np.allclose(q @ c, c @ q_macro, atol=tol, rtol=0.0))


def generator_closure_error(
    Q: ArrayLike,
    C: ArrayLike,
    Q_macro: ArrayLike,
) -> float:
    """Generator closure defect: max_i ||(Q C)_i - (C Q_macro)_i||_∞.

    Uses the row-wise infinity norm on the residual rate matrix, **not**
    total variation. TV is (1/2)||·||_1 on probability rows and assumes
    nonnegative mass summing to 1; generator residuals are signed rate
    vectors with row sum ~0, so TV is dimensionally and conceptually wrong.
    The ∞-norm matches Michel & Siegle's continuous-time residual growth
    rate controlled by ||Θ A − A Q||_∞ (here A ↔ C, Q ↔ micro generator).
    """
    q = _as_float_matrix(Q)
    c = _as_float_matrix(C)
    q_macro = _as_float_matrix(Q_macro)
    _validate_generator(q)
    if c.shape[0] != q.shape[0]:
        raise ScopeViolationError("C rows must match Q dimension")
    if q_macro.shape != (c.shape[1], c.shape[1]):
        raise ScopeViolationError("Q_macro must be M x M with M = C.columns")
    residual = q @ c - c @ q_macro
    # Per-row L_∞, then max over micro states
    row_inf = np.max(np.abs(residual), axis=1)
    return float(row_inf.max())


__all__ = [
    "generator_closure_error",
    "is_exact_generator_lumpability",
]
