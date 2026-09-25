"""Competing first-passage targets and committors (INTEGRATED_EXTENSION_ROADMAP.md
Paket C4) -- response to
prompts/Answers/nicht_stationäre_Treiber/SCF_INTEGRATED_EXTENSION_IMPLEMENTATION_PLAN.md,
section 8 (transition-path-theory style committors, [S4] Metzner, Schütte,
Vanden-Eijnden 2009).

For a continuous-time Markov chain with generator ``L`` (zero row sums,
non-negative off-diagonal), two DISJOINT boundary sets ``A`` and ``B``, and
interior states ``D`` (everything else), the boundary time is
``tau = tau_A ∧ tau_B`` (whichever is hit first). The COMMITTOR
``q(x) = P(hit B before A | start at x)`` solves the boundary value problem

    q|_A = 0,   q|_B = 1,   L_DD @ q_D = -L_DB @ 1

and the expected time to the boundary ``m(x) = E[tau | start at x]`` solves

    L_DD @ m_D = -1

Both are LINEAR SOLVES, never an explicit matrix inverse. Both require that,
from every considered interior state, ``A ∪ B`` is reached almost surely --
otherwise ``L_DD`` can be singular (checked via the SAME solve that computes
the answer, raising ``ScopeViolationError`` rather than silently returning
garbage from a near-singular solve).

For a FINITE horizon ``H``, making both ``A`` and ``B`` absorbing and
computing ``expm(L*H)`` gives ``p_A(H)``, ``p_B(H)``, and
``p_unresolved(H) = 1 - p_A(H) - p_B(H)`` (all three sum to 1 by
construction, checked explicitly rather than assumed).

**Hand-verified control case** (independently re-derived, then checked in
``verify_competing_first_passage.py`` before this module was written): 4
states ordered ``(A, i, j, B)``; ``i->A`` rate 1, ``i->j`` rate 2, ``j->i``
rate 1, ``j->B`` rate 3. Solving ``3*q_i=2*q_j``, ``4*q_j=q_i+3`` gives
``(q_i, q_j) = (0.6, 0.9)``; mean times ``(m_i, m_j) = (0.6, 0.4)``; for
``H=1``, ``p_B = (0.467359895563, 0.829637179582)`` from ``i`` and ``j``
respectively. Rescaling every rate by a constant ``c`` leaves the committor
``q`` UNCHANGED and divides mean times by ``c``; rescaling ``H`` to ``H/c``
alongside the rates leaves the finite-horizon hitting probabilities
unchanged too (a pure time-reparametrization has no effect on WHERE you end
up, only WHEN).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Hashable, Mapping, Sequence, Tuple

import numpy as np
from scipy.linalg import expm

from scoped_correspondence.errors import ScopeViolationError


def _validate_generator(L: np.ndarray, tol: float = 1e-9) -> None:
    n = L.shape[0]
    if L.shape != (n, n):
        raise ScopeViolationError(f"L must be square; got shape {L.shape}")
    off_diag = L - np.diag(np.diag(L))
    if np.any(off_diag < -tol):
        raise ScopeViolationError("L must have non-negative off-diagonal entries (a valid generator)")
    row_sums = L.sum(axis=1)
    if not np.allclose(row_sums, 0.0, atol=1e-8):
        raise ScopeViolationError(f"L's rows must sum to 0 (a valid generator); got sums {row_sums!r}")


def _partition_indices(n: int, A: Sequence[int], B: Sequence[int]) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    A_arr, B_arr = np.asarray(sorted(set(A))), np.asarray(sorted(set(B)))
    if len(set(A) & set(B)) > 0:
        raise ScopeViolationError("A and B must be disjoint")
    if not set(A_arr.tolist()) <= set(range(n)) or not set(B_arr.tolist()) <= set(range(n)):
        raise ScopeViolationError("A and B must index states within range(n)")
    D_arr = np.array([i for i in range(n) if i not in set(A_arr.tolist()) | set(B_arr.tolist())])
    return A_arr, B_arr, D_arr


def _require_boundary_reachable(L: np.ndarray, D_arr: np.ndarray, boundary: np.ndarray, tol: float) -> None:
    """**Correction (2026-09-25, response to SCF_REVIEW_C0_C7_4ed0cd9.md finding
    R4 -- a real bug, independently reproduced before fixing):** a numerically
    successful ``np.linalg.solve`` is NOT proof that every interior state can
    reach the boundary. For a CLOSED interior class (e.g. two interior states
    that only transition between each other, never to ``A`` or ``B``),
    ``L_DD`` is exactly singular in exact arithmetic, but floating-point
    LAPACK can still return a FINITE (~3.15e16, a rounding artifact of a
    numerically near-singular system) result instead of raising -- silently
    reporting a garbage mean hitting time as if it were a real, finite
    answer, while the true value is infinite (absorption never happens).

    This function checks the actual GRAPH condition directly: does every
    state in ``D_arr`` have a directed path of strictly positive transition
    rates (through other ``D`` states, if needed) to some state in
    ``boundary``? This is checked BEFORE any linear solve, independent of
    floating-point conditioning -- never inferred from whether a solve
    happens to succeed.
    """
    n = L.shape[0]
    reachable = set(int(b) for b in boundary)
    changed = True
    while changed:
        changed = False
        for x in D_arr:
            x = int(x)
            if x in reachable:
                continue
            for y in range(n):
                if L[x, y] > tol and y in reachable:
                    reachable.add(x)
                    changed = True
                    break
    unreachable = [int(x) for x in D_arr if int(x) not in reachable]
    if unreachable:
        raise ScopeViolationError(
            f"interior state(s) {unreachable!r} cannot reach A union B via any positive-rate "
            f"path (a closed interior class) -- mean hitting time and committor are undefined "
            f"(infinite/ill-posed) here, not merely numerically fragile"
        )


def committor(L: np.ndarray, A: Sequence[int], B: Sequence[int], tol: float = 1e-9) -> np.ndarray:
    """``q(x) = P(hit B before A | start at x)`` for every state (0 on ``A``,
    1 on ``B``, solved on the interior ``D``)."""
    _validate_generator(L, tol)
    n = L.shape[0]
    A_arr, B_arr, D_arr = _partition_indices(n, A, B)
    q = np.zeros(n)
    q[B_arr] = 1.0
    if len(D_arr) == 0:
        return q
    _require_boundary_reachable(L, D_arr, np.concatenate([A_arr, B_arr]), tol)
    L_DD = L[np.ix_(D_arr, D_arr)]
    L_DB = L[np.ix_(D_arr, B_arr)]
    rhs = -(L_DB @ np.ones(len(B_arr)))
    try:
        q_D = np.linalg.solve(L_DD, rhs)
    except np.linalg.LinAlgError as e:
        raise ScopeViolationError(
            f"L_DD is singular -- some interior state may never reach A union B: {e}"
        ) from e
    q[D_arr] = q_D
    return q


def mean_hitting_time(L: np.ndarray, A: Sequence[int], B: Sequence[int], tol: float = 1e-9) -> np.ndarray:
    """``m(x) = E[tau_A ∧ tau_B | start at x]`` (0 on the boundary ``A∪B``,
    solved on the interior ``D``)."""
    _validate_generator(L, tol)
    n = L.shape[0]
    A_arr, B_arr, D_arr = _partition_indices(n, A, B)
    m = np.zeros(n)
    if len(D_arr) == 0:
        return m
    _require_boundary_reachable(L, D_arr, np.concatenate([A_arr, B_arr]), tol)
    L_DD = L[np.ix_(D_arr, D_arr)]
    try:
        m_D = np.linalg.solve(L_DD, -np.ones(len(D_arr)))
    except np.linalg.LinAlgError as e:
        raise ScopeViolationError(
            f"L_DD is singular -- some interior state may never reach A union B: {e}"
        ) from e
    if np.any(m_D < -tol):
        raise ScopeViolationError(f"solving for mean hitting time gave a negative value: {m_D!r}")
    m[D_arr] = m_D
    return m


@dataclass(frozen=True)
class FiniteHorizonResult:
    horizon: float
    p_hit: Dict[Hashable, np.ndarray]  # label -> per-start-state hitting probability by H
    p_unresolved: np.ndarray  # per-start-state probability of hitting NEITHER boundary set by H


def finite_horizon_hitting_probabilities(
    L: np.ndarray, H: float, boundary_sets: Mapping[Hashable, Sequence[int]], tol: float = 1e-8
) -> FiniteHorizonResult:
    """Make every state in every declared boundary set ABSORBING (zero out its
    row of ``L``) and compute ``expm(L*H)``; returns, for every original
    state, the probability of having hit each boundary set by time ``H``, plus
    the residual probability of having hit NEITHER (``p_unresolved``). All
    hitting probabilities plus ``p_unresolved`` sum to 1 for every start state
    -- checked explicitly, not assumed."""
    _validate_generator(L, tol)
    if H < 0.0:
        raise ScopeViolationError(f"H must be >= 0; got {H!r}")
    n = L.shape[0]
    all_boundary = set()
    for label, idxs in boundary_sets.items():
        idxs_set = set(idxs)
        if idxs_set & all_boundary:
            raise ScopeViolationError(f"boundary set {label!r} overlaps another declared boundary set")
        all_boundary |= idxs_set

    L_abs = L.copy()
    for idxs in boundary_sets.values():
        for i in idxs:
            L_abs[i, :] = 0.0

    E = expm(L_abs * H)
    p_hit = {label: E[:, list(idxs)].sum(axis=1) for label, idxs in boundary_sets.items()}
    total_hit = np.sum(np.vstack(list(p_hit.values())), axis=0) if p_hit else np.zeros(n)
    p_unresolved = 1.0 - total_hit
    if np.any(p_unresolved < -1e-6) or np.any(total_hit + p_unresolved - 1.0 > 1e-6):
        raise ScopeViolationError("hitting probabilities and unresolved probability failed to sum to 1")
    return FiniteHorizonResult(horizon=H, p_hit=p_hit, p_unresolved=np.clip(p_unresolved, 0.0, 1.0))


__all__ = [
    "committor",
    "mean_hitting_time",
    "FiniteHorizonResult",
    "finite_horizon_hitting_probabilities",
]
