"""Schnakenberg network thermodynamics — cycle affinities & entropy production (Milestone 18).

Maps Schnakenberg 1976, Network theory of microscopic and macroscopic behavior
of non-equilibrium systems, Rev. Mod. Phys. 48, 571;
DOI 10.1103/RevModPhys.48.571.

For a continuous-time Markov jump process with state probabilities ``p`` and
transition-rate matrix ``k`` (``k[i,j]`` = rate i → j; diagonal of a generator
is ignored by the current/affinity formulas):

    J_ij = p_i k_ij - p_j k_ji          (stationary probability current)
    A_ij = ln( p_i k_ij / (p_j k_ji) )  (cycle / edge affinity)
    σ    = (1/2) Σ_{i,j} J_ij A_ij      (entropy production rate)

σ is non-negative by construction for well-posed rates (J and A share sign);
negative numerical σ raises ``ScopeViolationError``.

**Onsager reciprocity** (L_ij = L_ji for linear response coefficients) is a
**near-equilibrium special case only**. It is **NOT** a general identity of
coupling matrices away from equilibrium. This module does not construct or
assert Onsager matrices.

Does **not** mutate ``thermo/core.py``. Does **not** merge with the M8
deterministic 3-cycle permutation example
(``stochastic_inverse_not_detailed_balance``). No general network-theory /
bond-graph library. No link to ecosystem σ ≈ 2.2.
"""
from __future__ import annotations

from typing import Sequence

import numpy as np

from scoped_correspondence.errors import ScopeViolationError

ArrayLike = Sequence[float] | np.ndarray

SOURCE = (
    "Schnakenberg 1976, Network theory of microscopic and macroscopic "
    "behavior of non-equilibrium systems, Rev. Mod. Phys. 48, 571; "
    "DOI 10.1103/RevModPhys.48.571"
)

_ONSAGER_NOTE = (
    "Onsager reciprocity is a near-equilibrium special case only — "
    "NOT a general identity of coupling matrices."
)

_DEFAULT_ASSUMPTIONS: tuple[str, ...] = (
    "finite discrete state space; p probability vector (nonnegative, sums to 1)",
    "k[i,j] = transition rate i→j (continuous-time Markov); diagonal unused for J,A",
    "entropy production σ = (1/2) Σ_ij J_ij A_ij (Schnakenberg 1976); σ >= 0",
    _ONSAGER_NOTE,
    "separate from M8 thermo/core.py (no merge with deterministic 3-cycle formula)",
    "no general network theory / bond-graph rewrite; no ecosystem σ=2.2 claim",
)


def _as_p_k(p: ArrayLike, k: ArrayLike) -> tuple[np.ndarray, np.ndarray]:
    p_arr = np.asarray(p, dtype=float).ravel()
    k_arr = np.asarray(k, dtype=float)
    if p_arr.ndim != 1 or p_arr.size < 2:
        raise ScopeViolationError(
            f"schnakenberg: p must be a length-n>=2 vector; got shape {p_arr.shape}"
        )
    n = p_arr.size
    if k_arr.ndim != 2 or k_arr.shape != (n, n):
        raise ScopeViolationError(
            f"schnakenberg: k must be ({n},{n}); got {k_arr.shape}"
        )
    if not np.isfinite(p_arr).all() or not np.isfinite(k_arr).all():
        raise ScopeViolationError("schnakenberg: p and k must be finite")
    if (p_arr < -1e-15).any():
        raise ScopeViolationError("schnakenberg: p must be nonnegative")
    if float(p_arr.sum()) <= 0:
        raise ScopeViolationError("schnakenberg: p must have positive mass")
    # Off-diagonal rates must be nonnegative (generator diagonal may be negative).
    off = k_arr.copy()
    np.fill_diagonal(off, 0.0)
    if (off < -1e-15).any():
        raise ScopeViolationError(
            "schnakenberg: off-diagonal k[i,j] must be nonnegative rates"
        )
    return p_arr, k_arr


def stationary_currents(p: ArrayLike, k: ArrayLike) -> np.ndarray:
    """Probability currents J_ij = p_i k_ij - p_j k_ji.

    Parameters
    ----------
    p :
        Stationary (or instantaneous) probability vector, length n.
    k :
        Rate matrix; ``k[i, j]`` is the transition rate i → j.
        Generator diagonal entries are unused (currents for i == j are 0).

    Returns
    -------
    J : ndarray, shape (n, n)
        Antisymmetric current matrix (up to numerical tolerance).

    Notes
    -----
    Onsager reciprocity is a near-equilibrium special case only — NOT a general identity of coupling matrices.
    """
    p_arr, k_arr = _as_p_k(p, k)
    n = p_arr.size
    J = np.zeros((n, n), dtype=float)
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            J[i, j] = float(p_arr[i] * k_arr[i, j] - p_arr[j] * k_arr[j, i])
    return J


def cycle_affinity(p: ArrayLike, k: ArrayLike, i: int, j: int) -> float:
    """Edge / cycle affinity A_ij = ln( p_i k_ij / (p_j k_ji) ).

    Parameters
    ----------
    p, k :
        As in ``stationary_currents``.
    i, j :
        State indices (must differ; both forward and reverse rates > 0).

    Returns
    -------
    A_ij : float

    Raises
    ------
    ScopeViolationError
        If i == j, indices out of range, or either directed rate (times
        probability) is non-positive so the log is undefined.

    Notes
    -----
    Onsager reciprocity is a near-equilibrium special case only — NOT a general identity of coupling matrices.
    """
    p_arr, k_arr = _as_p_k(p, k)
    n = p_arr.size
    i = int(i)
    j = int(j)
    if i == j:
        raise ScopeViolationError("cycle_affinity: i and j must differ")
    if not (0 <= i < n and 0 <= j < n):
        raise ScopeViolationError(
            f"cycle_affinity: indices out of range for n={n}; got i={i}, j={j}"
        )
    fwd = float(p_arr[i] * k_arr[i, j])
    rev = float(p_arr[j] * k_arr[j, i])
    if fwd <= 0.0 or rev <= 0.0:
        raise ScopeViolationError(
            f"cycle_affinity: need p_i k_ij > 0 and p_j k_ji > 0; "
            f"got fwd={fwd}, rev={rev} for ({i},{j})"
        )
    return float(np.log(fwd / rev))


def entropy_production_rate(p: ArrayLike, k: ArrayLike) -> float:
    """Entropy production rate σ = (1/2) Σ_{i,j} J_ij A_ij.

    Uses the Schnakenberg bilinear form. Only pairs with both directed rates
    positive (so A_ij is defined) contribute; vanishing rates contribute 0
    when the corresponding current is also 0.

    Raises
    ------
    ScopeViolationError
        If the computed σ is negative (outside the thermodynamic scope), or
        if a nonzero current appears on a one-way edge where affinity is
        undefined.

    Notes
    -----
    Onsager reciprocity is a near-equilibrium special case only — NOT a general identity of coupling matrices.
    This σ is **not** the ecosystem σ ≈ 2.2 figure; no cross-domain identity.
    """
    p_arr, k_arr = _as_p_k(p, k)
    n = p_arr.size
    J = stationary_currents(p_arr, k_arr)
    total = 0.0
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            fwd = float(p_arr[i] * k_arr[i, j])
            rev = float(p_arr[j] * k_arr[j, i])
            if fwd <= 0.0 and rev <= 0.0:
                continue
            if fwd <= 0.0 or rev <= 0.0:
                # One-way edge: affinity undefined. Allow only if current ~ 0.
                if abs(J[i, j]) > 1e-12:
                    raise ScopeViolationError(
                        f"entropy_production_rate: nonzero current on one-way "
                        f"edge ({i},{j}) with fwd={fwd}, rev={rev}; affinity "
                        f"undefined (Schnakenberg scope)."
                    )
                continue
            A = float(np.log(fwd / rev))
            total += float(J[i, j]) * A
    sigma = 0.5 * total
    if sigma < -1e-12:
        raise ScopeViolationError(
            f"entropy_production_rate: σ must be >= 0 (2nd law / Schnakenberg); "
            f"got {sigma}. Onsager reciprocity is a near-equilibrium special case only — NOT a general identity of coupling matrices."
        )
    if sigma < 0.0:
        sigma = 0.0
    return float(sigma)


__all__ = [
    "SOURCE",
    "stationary_currents",
    "cycle_affinity",
    "entropy_production_rate",
]
