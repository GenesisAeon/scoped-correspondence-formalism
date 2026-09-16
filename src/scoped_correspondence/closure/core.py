"""Closure formulas: PC=CQ, delta_cl, TV bound, circle reconstruction.

FORMALISM.md section 9; emergence_and_closure.md sections 3-4;
worked_example_reconstruction.md.
"""

from __future__ import annotations

import math
from typing import Optional, Sequence, Tuple, Union

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


def total_variation_row(p: ArrayLike, q: ArrayLike) -> float:
    """TV between two discrete distributions (row vectors): (1/2) sum |p-q|."""
    p_arr = np.asarray(p, dtype=float).reshape(-1)
    q_arr = np.asarray(q, dtype=float).reshape(-1)
    if p_arr.shape != q_arr.shape:
        raise ScopeViolationError("TV requires equal-length rows")
    return float(0.5 * np.abs(p_arr - q_arr).sum())


def is_exact_closure(
    P: ArrayLike,
    C: ArrayLike,
    Q: ArrayLike,
    tol: float = 1e-10,
) -> bool:
    """Exact stochastic closure PC = CQ (FORMALISM.md section 9).

    P is N x N row-stochastic micro kernel, C is N x M partition (one 1 per
    row), Q is M x M candidate macro kernel. Returns True iff
    max |PC - CQ| <= tol (absolute elementwise, matching legacy allclose).
    """
    p = _as_float_matrix(P)
    c = _as_float_matrix(C)
    q = _as_float_matrix(Q)
    if p.shape[0] != p.shape[1]:
        raise ScopeViolationError(f"P must be square; got {p.shape}")
    if c.shape[0] != p.shape[0]:
        raise ScopeViolationError("C rows must match P dimension")
    if q.shape != (c.shape[1], c.shape[1]):
        raise ScopeViolationError("Q must be M x M with M = C.columns")
    if tol < 0:
        raise ScopeViolationError(f"tol must be >= 0; got {tol!r}")
    return bool(np.allclose(p @ c, c @ q, atol=tol, rtol=0.0))


def closure_error(P: ArrayLike, C: ArrayLike, Q: ArrayLike) -> float:
    """One-step closure defect delta_cl = max_i TV((PC)_i, (CQ)_i).

    Maps to FORMALISM.md section 9 ``delta_cl`` and emergence_and_closure.md
    section 3 (own elementary bound).
    """
    p = _as_float_matrix(P)
    c = _as_float_matrix(C)
    q = _as_float_matrix(Q)
    diff = p @ c - c @ q
    # Per-row TV: (1/2) L1
    row_tv = 0.5 * np.abs(diff).sum(axis=1)
    return float(row_tv.max())


def propagated_error_bound(delta_cl: float, k: int) -> float:
    """TV horizon bound min(1, k * delta_cl) for any initial distribution.

    emergence_and_closure.md section 3: TV(p P^k C, p C Q^k) <= min(1, k delta).
    """
    if delta_cl < 0:
        raise ScopeViolationError(f"delta_cl must be >= 0; got {delta_cl!r}")
    if not isinstance(k, (int, np.integer)) or int(k) < 0:
        raise ScopeViolationError(f"horizon k must be integer >= 0; got {k!r}")
    return float(min(1.0, int(k) * float(delta_cl)))


def reconstruct_from_projection(
    observed: ArrayLike,
    delayed: ArrayLike,
    alpha: float,
) -> Tuple[np.ndarray, np.ndarray]:
    """Circle delay-embedding reconstruction (worked_example_reconstruction.md section 1).

    For y = cos(theta), delay alpha = omega * tau with sin(alpha) != 0:

        sin(theta) = (y(t-tau) - y(t) cos alpha) / sin alpha

    Returns (reconstructed_theta, recovered_sine). Two coordinates suffice at
    intrinsic dimension d=1 in this concrete model — not a general Takens library.
    """
    y = np.asarray(observed, dtype=float)
    y_delay = np.asarray(delayed, dtype=float)
    if y.shape != y_delay.shape:
        raise ScopeViolationError("observed and delayed must share shape")
    s = math.sin(alpha)
    if abs(s) < 1e-15:
        raise ScopeViolationError(
            "reconstruct_from_projection: sin(alpha) ~ 0; delay is non-injective "
            "(worked_example_reconstruction.md: alpha = pi aliases +/- theta)"
        )
    recovered_sine = (y_delay - y * math.cos(alpha)) / s
    reconstructed = np.arctan2(recovered_sine, y)
    return reconstructed, recovered_sine


def memory_solution(
    t: Union[float, np.ndarray],
    x0: float,
    y0: float,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Analytic solution of x_dot=-x+y, y_dot=-x-2y (worked_example_reconstruction.md section 2).

    Returns (x, x_dot, y) with y = x_dot + x. Used to show projection needs memory.
    """
    t_arr = np.asarray(t, dtype=float)
    w = math.sqrt(3.0) / 2.0
    b = (0.5 * x0 + y0) / w
    q = x0 * np.cos(w * t_arr) + b * np.sin(w * t_arr)
    qp = -x0 * w * np.sin(w * t_arr) + b * w * np.cos(w * t_arr)
    x = np.exp(-1.5 * t_arr) * q
    xp = np.exp(-1.5 * t_arr) * (qp - 1.5 * q)
    y = xp + x
    return x, xp, y


def projected_memory_rhs(
    t: float,
    x0: float,
    y0: float,
    *,
    n_quad: int = 20001,
) -> float:
    """Scalar memory RHS for projected x (worked_example_reconstruction.md section 2):

        x_dot(t) = -x(t) + e^{-2t} y0 - int_0^t e^{-2(t-s)} x(s) ds

    Returns the RHS value (to compare with analytic x_dot).
    """
    if t < 0:
        raise ScopeViolationError(f"t must be >= 0; got {t!r}")
    if n_quad < 2:
        raise ScopeViolationError("n_quad must be >= 2")
    x_t, xp_t, _y = memory_solution(t, x0, y0)
    # Trapezoidal integral of e^{-2(t-s)} x(s)
    grid = np.linspace(0.0, float(t), int(n_quad))
    x_grid = memory_solution(grid, x0, y0)[0]
    values = np.exp(-2.0 * (float(t) - grid)) * x_grid
    if float(t) == 0.0:
        integral = 0.0
    else:
        h = float(t) / (len(grid) - 1)
        integral = h * (values[0] / 2.0 + values[-1] / 2.0 + values[1:-1].sum())
    x_scalar = float(np.asarray(x_t).reshape(-1)[0])
    return float(-x_scalar + math.exp(-2.0 * float(t)) * y0 - integral)


def partition_matrix(labels: Sequence[int]) -> Tuple[np.ndarray, np.ndarray]:
    """Build partition C (N x M) and uniform-in-block lift Lambda (M x N).

    C has one 1 per row; Lambda C = I_M. Used by lumpability examples
    (emergence_and_closure.md section 3).
    """
    labels_arr = np.asarray(list(labels), dtype=int)
    if labels_arr.ndim != 1 or labels_arr.size == 0:
        raise ScopeViolationError("labels must be a non-empty 1D sequence")
    if (labels_arr < 0).any():
        raise ScopeViolationError("labels must be non-negative")
    m = int(labels_arr.max()) + 1
    c = np.eye(m, dtype=float)[labels_arr]
    col_sums = c.sum(axis=0)
    if (col_sums <= 0).any():
        raise ScopeViolationError("each block must be non-empty")
    lift = c.T / col_sums[:, None]
    return c, lift


def candidate_macro_kernel(P: ArrayLike, C: ArrayLike, lift: ArrayLike) -> np.ndarray:
    """Q = Lambda P C (does NOT imply PC=CQ without exact closure)."""
    p = _as_float_matrix(P)
    c = _as_float_matrix(C)
    lam = _as_float_matrix(lift)
    q = lam @ p @ c
    # Match legacy stochastic(): validate row sums ~1, do not re-normalize
    # (re-normalization would perturb bit-identical evidence for e06).
    row_sums = q.sum(axis=1)
    if (row_sums <= 0).any():
        raise ScopeViolationError("candidate Q has a non-positive row sum")
    if not np.allclose(row_sums, np.ones(len(q)), atol=1e-10, rtol=1e-9):
        raise ScopeViolationError(
            "candidate Q rows must sum to 1; got " + repr(row_sums)
        )
    if (q < -1e-15).any():
        raise ScopeViolationError("candidate Q has negative entries")
    return q


def demo_matrices() -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Legacy extension matrices(): exact / nonclosed / approximate cases.

    Returns (p_exact_lumpable, p_bad_swap, C, lift) with labels [0,0,0,1].
    """
    p = np.zeros((4, 4), dtype=float)
    p[:3, :3] = 1.0 / 3.0
    p[3, 3] = 1.0
    bad = np.eye(4)[[2, 3, 0, 1]]
    c, lift = partition_matrix([0, 0, 0, 1])
    return p, bad, c, lift


__all__ = [
    "candidate_macro_kernel",
    "closure_error",
    "demo_matrices",
    "is_exact_closure",
    "memory_solution",
    "partition_matrix",
    "projected_memory_rhs",
    "propagated_error_bound",
    "reconstruct_from_projection",
    "total_variation_row",
]
