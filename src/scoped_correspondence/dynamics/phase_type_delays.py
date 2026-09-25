"""Distributed delays via phase-type/Erlang chains (INTEGRATED_EXTENSION_ROADMAP.md
Paket C3) -- response to
prompts/Answers/nicht_stationäre_Treiber/SCF_INTEGRATED_EXTENSION_IMPLEMENTATION_PLAN.md,
section 7.

An Erlang(n) delay chain with total mean dwell time ``tau`` (rate
``lambda=n/tau`` per stage) is the special case, of a general PHASE-TYPE
delay, with row vector ``alpha`` (how the input enters the transient
stages), transient subgenerator ``T`` (off-diagonal >= 0, diagonal < 0, row
sums <= 0), and exit-rate vector ``r = -T @ 1`` (the mass leaving the system
entirely from each stage, distinct from mass merely moving BETWEEN stages):

    dz/dt = z @ T + u(t) * alpha,     y(t) = z @ r
    h(t) = alpha @ expm(T*t) @ r      (impulse response / delay-time density)
    E[dwell time] = alpha @ (-T)^{-1} @ 1   (solved, never an explicit inverse)

``z`` is a ROW vector of stage occupancies; the module works throughout in
row-vector convention to match the plan's own notation.

**Hand-verified control values** (independently re-derived, then checked in
``verify_phase_type_delays.py`` before any pilot code was written): both
``n=1`` (exponential, rate 1) and ``n=2`` (Erlang-2, rate 2 per stage) have
mean dwell time 1. ``F_1(t)=1-e^{-t}``, ``F_2(t)=1-e^{-2t}(1+2t)``:
``F_1(0.25)=0.221199216929``, ``F_2(0.25)=0.090204010431``;
``F_1(1)=0.632120558829``, ``F_2(1)=0.593994150290``;
``F_1(2)=0.864664716763``, ``F_2(2)=0.908421805556`` -- **the CDF ranking
reverses between horizons** (a smaller-variance delay is not uniformly
"faster" at every horizon). The Erlang-2 impulse response
``h_2(t)=4t*e^{-2t}`` peaks at ``t=0.5`` with height ``2/e=0.735758882343``.

**Exact propagation under piecewise-constant input** uses the standard
augmented-matrix-exponential trick (``propagate_linear_constant_input``):
for ``dx/dt = A x + d`` with CONSTANT ``d`` over ``[0, dt]``,

    [x(dt); 1] = expm([[A, d], [0, 0]] * dt) @ [x(0); 1]

which is exact and well-defined even when ``A`` is singular (no explicit
matrix inverse, no ODE solver tolerance to tune) -- reused for both the bare
phase-type stage vector and, in ``validation/distributed_delay_pilot.py``,
the combined (stages + downstream buffer) system.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

import numpy as np
from scipy.linalg import expm

from scoped_correspondence.errors import ScopeViolationError


@dataclass(frozen=True)
class PhaseType:
    alpha: np.ndarray  # (n,) initial-entry distribution, sums to 1
    T: np.ndarray  # (n,n) transient subgenerator
    r: np.ndarray  # (n,) exit rates, r = -T @ 1


def erlang_phase_type(n: int, tau: float) -> PhaseType:
    """Erlang(n) chain with total mean dwell time ``tau`` (rate ``lambda=n/tau``
    per stage, input entering stage 0 only, output leaving stage ``n-1`` only)."""
    if n < 1:
        raise ScopeViolationError(f"n must be >= 1; got {n!r}")
    if tau <= 0.0:
        raise ScopeViolationError(f"tau must be > 0; got {tau!r}")
    lam = n / tau
    T = -lam * np.eye(n)
    for i in range(n - 1):
        T[i, i + 1] = lam
    r = -T @ np.ones(n)
    alpha = np.zeros(n)
    alpha[0] = 1.0
    return PhaseType(alpha=alpha, T=T, r=r)


def validate_phase_type(pt: PhaseType, tol: float = 1e-9) -> None:
    alpha, T, r = pt.alpha, pt.T, pt.r
    n = T.shape[0]
    if T.shape != (n, n):
        raise ScopeViolationError(f"T must be square; got {T.shape}")
    if alpha.shape != (n,) or r.shape != (n,):
        raise ScopeViolationError("alpha and r must have shape (n,) matching T")
    if np.any(alpha < -tol) or abs(float(np.sum(alpha)) - 1.0) > 1e-6:
        raise ScopeViolationError(f"alpha must be a probability vector; got {alpha!r}")
    off_diag = T - np.diag(np.diag(T))
    if np.any(off_diag < -tol):
        raise ScopeViolationError("T must have non-negative off-diagonal entries (a valid subgenerator)")
    if np.any(np.diag(T) > tol):
        raise ScopeViolationError("T must have non-positive diagonal entries")
    row_sums = T @ np.ones(n)
    if np.any(row_sums > tol):
        raise ScopeViolationError("T's row sums must be <= 0 (a valid subgenerator)")
    if not np.allclose(r, -row_sums, atol=1e-9):
        raise ScopeViolationError("r must equal -T @ 1 exactly")
    if np.any(r < -tol):
        raise ScopeViolationError("exit rates r must be non-negative")

    # **Correction (2026-09-25, response to SCF_REVIEW_C0_C7_4ed0cd9.md finding
    # R4 -- a real bug, independently reproduced before fixing):** relying on
    # ``np.linalg.solve(-T, ...)`` succeeding as the ONLY absorption check is
    # not sufficient: for a phase that never reaches an exit (e.g. two phases
    # that only transition between each other, with r=(0,0)), ``-T`` is
    # exactly singular in exact arithmetic, but floating-point LAPACK can
    # still return a FINITE (~3.15e16, a rounding artifact) "mean dwell time"
    # instead of raising -- while the true value is infinite (this phase
    # never absorbs at all). Checked directly here via the GRAPH condition,
    # independent of floating-point conditioning: does every phase have a
    # directed path of strictly positive rates to some phase with a positive
    # EXIT rate? (ALL phases are required, not only those reachable under
    # ``alpha`` -- the stricter, unambiguous choice the review asked to be
    # decided explicitly, since a PhaseType can be reused with a different
    # ``alpha`` later.)
    has_direct_exit = r > tol
    reachable = set(np.where(has_direct_exit)[0].tolist())
    changed = True
    while changed:
        changed = False
        for i in range(n):
            if i in reachable:
                continue
            for j in range(n):
                if T[i, j] > tol and j in reachable:
                    reachable.add(i)
                    changed = True
                    break
    unreachable = [i for i in range(n) if i not in reachable]
    if unreachable:
        raise ScopeViolationError(
            f"phase(s) {unreachable!r} cannot reach any exit via a positive-rate path -- "
            f"this phase-type never absorbs from there (infinite mean dwell time), not merely "
            f"numerically fragile"
        )

    # Absorption a.s. from every state reachable under alpha requires T to be
    # non-singular (a genuinely defective/never-absorbing phase-type is out of
    # scope here) -- checked via the SAME solve used by mean_dwell_time, ON
    # TOP OF (never instead of) the graph check above.
    try:
        m = np.linalg.solve(-T, np.ones(n))
    except np.linalg.LinAlgError as e:
        raise ScopeViolationError(f"T is singular -- no finite mean dwell time from every stage: {e}") from e
    if np.any(m < -tol):
        raise ScopeViolationError(f"solving -T @ m = 1 gave a negative mean dwell time from some stage: {m!r}")


def mean_dwell_time(pt: PhaseType) -> float:
    """``E[tau] = alpha @ (-T)^{-1} @ 1``, computed via ``solve``, never an
    explicit inverse."""
    n = pt.T.shape[0]
    m = np.linalg.solve(-pt.T, np.ones(n))
    return float(pt.alpha @ m)


def impulse_response(t: float, pt: PhaseType) -> float:
    """``h(t) = alpha @ expm(T*t) @ r`` -- the delay-time probability density."""
    if t < 0.0:
        raise ScopeViolationError(f"t must be >= 0; got {t!r}")
    return float(pt.alpha @ expm(pt.T * t) @ pt.r)


def survival_function(t: float, pt: PhaseType) -> float:
    """``P(dwell time > t) = alpha @ expm(T*t) @ 1``."""
    if t < 0.0:
        raise ScopeViolationError(f"t must be >= 0; got {t!r}")
    n = pt.T.shape[0]
    return float(pt.alpha @ expm(pt.T * t) @ np.ones(n))


def cdf(t: float, pt: PhaseType) -> float:
    return 1.0 - survival_function(t, pt)


def propagate_linear_constant_input(x0: np.ndarray, A: np.ndarray, d: np.ndarray, dt: float) -> np.ndarray:
    """Exact ``x(dt)`` for ``dx/dt = A x + d`` with CONSTANT ``d`` over
    ``[0, dt]``, via the augmented-matrix-exponential trick (module docstring)
    -- exact even when ``A`` is singular, no ODE solver tolerance involved."""
    n = x0.shape[0]
    if A.shape != (n, n) or d.shape != (n,):
        raise ScopeViolationError(f"shape mismatch: x0={x0.shape}, A={A.shape}, d={d.shape}")
    if dt < 0.0:
        raise ScopeViolationError(f"dt must be >= 0; got {dt!r}")
    M = np.zeros((n + 1, n + 1))
    M[:n, :n] = A
    M[:n, n] = d
    x_aug = np.concatenate([x0, [1.0]])
    result = expm(M * dt) @ x_aug
    return result[:n]


def propagate_phase_type(z0: np.ndarray, pt: PhaseType, u: float, dt: float) -> np.ndarray:
    """Exact stage-occupancy vector ``z(dt)`` under CONSTANT input ``u`` over
    ``[0, dt]`` (row-vector convention: ``dz/dt = z @ T + u*alpha``)."""
    A = pt.T.T
    d = u * pt.alpha
    return propagate_linear_constant_input(z0, A, d, dt)


__all__ = [
    "PhaseType",
    "erlang_phase_type",
    "validate_phase_type",
    "mean_dwell_time",
    "impulse_response",
    "survival_function",
    "cdf",
    "propagate_linear_constant_input",
    "propagate_phase_type",
]
