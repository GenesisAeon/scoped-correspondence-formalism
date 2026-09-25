"""Linear-Gaussian state estimation and observability (INTEGRATED_EXTENSION_ROADMAP.md
Paket C1) -- response to prompts/Answers/nicht_stationäre_Treiber/
SCF_INTEGRATED_EXTENSION_IMPLEMENTATION_PLAN.md, section 5.

Model (plan section 5.1):

    x_{t+1} = F_t x_t + G_t u_t + w_t,    w_t ~ (0, W_t)
    y_t     = H_t x_t + D_t u_t + v_t,    v_t ~ (0, R_t)

``predict`` and ``update`` are separate functions (never fused into one
"filter step" that hides which formula produced which number). The posterior
covariance update uses the Joseph form

    P+ = (I - K H) P- (I - K H)^T + K R K^T

rather than the algebraically-equivalent but numerically fragile short form
``P+ = (I - K H) P-`` (the short form can produce a non-symmetric or
indefinite result under floating-point error; Joseph form stays symmetric
PSD by construction for any K). No step computes an explicit matrix inverse:
the gain solves ``S K^T = H P`` directly (``S`` symmetric, so ``S^{-1} =
S^{-T}``) via ``numpy.linalg.solve``.

**First-scope restriction (plan section 5.1):** ``update`` REQUIRES a
positive-definite innovation covariance ``S = H P H^T + R``. A singular or
near-singular ``S`` (e.g. a fully deterministic, noiseless observation of an
already-exactly-known quantity) raises ``ScopeViolationError`` explicitly --
this first scope does NOT silently fall back to a pseudoinverse or a
degenerate/singular Kalman update, which would require a separate,
carefully-derived formulation not attempted here.

Observability (plan section 5.3): ``observability_matrix`` builds the
standard ``O = [H; HF; HF^2; ...; HF^{n-1}]`` stack. ``observability_rank``
reports ``matrix_rank`` for a GIVEN concrete ``(F, H)`` pair -- this is a
statement about that specific numeric pair, not a symbolic/analytic
observability claim; near a rank-deficient point the numerically reported
rank can be sensitive to the singular-value tolerance, so
``observability_report`` additionally returns the full singular-value
spectrum of ``O`` so a caller can see how close to degenerate the given
instance actually is, instead of collapsing everything to one integer.

Hand-verified control case (plan section 5, independently re-derived in
``verify_linear_state_estimation.py``): ``F=diag(1/2,1/4)``, ``H=(1,1)``,
prior ``m-=(0,0)``, ``P-=I``, ``R=1``, ``y=3``, ``W=0`` gives exactly
``K=(1/3,1/3)``, ``m+=(1,1)``, ``P+=[[2/3,-1/3],[-1/3,2/3]]``; propagating
once more (no further observation) gives predicted next observation mean
``0.75`` and variance ``1.125``; ``det([H;HF])=-0.25`` (observable), while at
``F=0.5*I`` the observability matrix drops to rank 1 (the state DIFFERENCE
``x_1-x_2`` is invisible to ``H=(1,1)`` and, under equal decay, stays
invisible for all time).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np

from scoped_correspondence.errors import ScopeViolationError


def _as_matrix(x, shape, name: str) -> np.ndarray:
    arr = np.asarray(x, dtype=float)
    if arr.ndim == 1 and len(shape) == 2 and shape[1] == 1:
        arr = arr.reshape(-1, 1)
    if arr.shape != shape:
        raise ScopeViolationError(f"{name} must have shape {shape}; got {arr.shape}")
    if not np.all(np.isfinite(arr)):
        raise ScopeViolationError(f"{name} contains non-finite values")
    return arr


def _validate_covariance(M: np.ndarray, name: str, tol: float = 1e-9) -> None:
    """**Correction (2026-09-25, response to SCF_REVIEW_C0_C7_4ed0cd9.md finding
    R9 -- a real bug, independently reproduced before fixing):** ``update``
    checked ONLY that the innovation covariance ``S=HPH^T+R`` was positive
    definite -- but that check alone does not catch an invalid ``R`` (or
    ``P``/``W``) directly: a negative measurement variance can still leave
    ``S`` positive (``S`` is a SUM), and the mathematically-correct Joseph
    form then produces a NEGATIVE posterior variance from that invalid input
    (Astra's exact counterexample: ``P=[[1]]``, ``R=[[-0.5]]``, ``H=[[1]]``
    gives ``S=0.5>0`` -- passing the old check -- yet the posterior variance
    comes out to exactly ``-1``). **Fixed** by validating that every
    covariance matrix (``P`` at `KalmanState` CONSTRUCTION -- covering the
    public constructor directly, not only the exported functions --, and
    ``W``/``R`` at every ``predict``/``update`` call) is symmetric (checked
    BEFORE any numerical symmetrization, which is used only to absorb
    demonstrably small rounding deviations, never to silently accept a
    genuinely asymmetric input) and positive SEMI-definite. This is
    independent of, and in addition to, the existing strict positive-
    DEFINITE requirement on ``S`` itself.
    """
    if not np.allclose(M, M.T, atol=1e-9):
        raise ScopeViolationError(f"{name} must be symmetric; got {M!r}")
    eigvals = np.linalg.eigvalsh(0.5 * (M + M.T))
    if np.min(eigvals) < -tol:
        raise ScopeViolationError(
            f"{name} must be positive semi-definite; got minimum eigenvalue {float(np.min(eigvals))!r}"
        )


@dataclass(frozen=True)
class KalmanState:
    """A Gaussian belief ``N(mean, cov)`` over the state vector."""

    mean: np.ndarray  # shape (n,)
    cov: np.ndarray  # shape (n, n)

    def __post_init__(self) -> None:
        n = self.mean.shape[0]
        if self.mean.ndim != 1:
            raise ScopeViolationError(f"mean must be 1-D; got shape {self.mean.shape}")
        if self.cov.shape != (n, n):
            raise ScopeViolationError(f"cov must have shape ({n},{n}); got {self.cov.shape}")
        if not np.all(np.isfinite(self.cov)) or not np.all(np.isfinite(self.mean)):
            raise ScopeViolationError("mean and cov must be finite")
        _validate_covariance(self.cov, "cov")


def make_state(mean, cov) -> KalmanState:
    mean = np.atleast_1d(np.asarray(mean, dtype=float))
    n = mean.shape[0]
    cov = _as_matrix(cov, (n, n), "cov")
    return KalmanState(mean=mean, cov=cov)


def predict(state: KalmanState, F, W, G=None, u=None) -> KalmanState:
    """``x_{t+1} = F x_t + G u_t + w_t``, ``w_t ~ (0, W)``. ``G``/``u`` optional (no
    exogenous input this step)."""
    n = state.mean.shape[0]
    F = _as_matrix(F, (n, n), "F")
    W = _as_matrix(W, (n, n), "W")
    _validate_covariance(W, "W")
    mean_pred = F @ state.mean
    if (G is None) != (u is None):
        raise ScopeViolationError("G and u must be given together or not at all")
    if G is not None:
        u_arr = np.atleast_1d(np.asarray(u, dtype=float))
        G = _as_matrix(G, (n, u_arr.shape[0]), "G")
        mean_pred = mean_pred + G @ u_arr
    cov_pred = F @ state.cov @ F.T + W
    return KalmanState(mean=mean_pred, cov=cov_pred)


@dataclass(frozen=True)
class UpdateReport:
    """Everything a caller needs to audit one measurement update, not just the
    resulting posterior."""

    state: KalmanState
    innovation: np.ndarray  # y - predicted y, shape (m,)
    innovation_cov: np.ndarray  # S, shape (m, m)
    gain: np.ndarray  # K, shape (n, m)


def update(state: KalmanState, y, H, R, D=None, u=None, min_eig_ratio: float = 1e-10) -> UpdateReport:
    """``y = H x + D u + v``, ``v ~ (0, R)``. Requires the innovation covariance
    ``S = H P H^T + R`` to be positive definite (see module docstring) -- raises
    ``ScopeViolationError`` rather than silently degrading to a pseudoinverse.
    """
    n = state.mean.shape[0]
    y = np.atleast_1d(np.asarray(y, dtype=float))
    m = y.shape[0]
    H = _as_matrix(H, (m, n), "H")
    R = _as_matrix(R, (m, m), "R")
    _validate_covariance(R, "R")

    y_pred = H @ state.mean
    if (D is None) != (u is None):
        raise ScopeViolationError("D and u must be given together or not at all")
    if D is not None:
        u_arr = np.atleast_1d(np.asarray(u, dtype=float))
        D = _as_matrix(D, (m, u_arr.shape[0]), "D")
        y_pred = y_pred + D @ u_arr

    innovation = y - y_pred
    HP = H @ state.cov
    S = HP @ H.T + R
    S = 0.5 * (S + S.T)  # symmetrize away float round-off before the eigenvalue check

    eigvals = np.linalg.eigvalsh(S)
    max_eig = float(np.max(np.abs(eigvals)))
    min_eig = float(np.min(eigvals))
    if max_eig == 0.0 or min_eig <= min_eig_ratio * max_eig:
        raise ScopeViolationError(
            f"innovation covariance S is singular or near-singular "
            f"(min eig={min_eig!r}, max eig={max_eig!r}); this first scope requires a "
            f"strictly positive-definite S and does not implement a degenerate/singular "
            f"Kalman update"
        )

    # K^T solves S K^T = H P (S symmetric, so S^{-1} = S^{-T}); no explicit inverse.
    K = np.linalg.solve(S, HP).T
    mean_post = state.mean + K @ innovation
    I = np.eye(n)
    IKH = I - K @ H
    cov_post = IKH @ state.cov @ IKH.T + K @ R @ K.T  # Joseph form

    return UpdateReport(
        state=KalmanState(mean=mean_post, cov=cov_post),
        innovation=innovation,
        innovation_cov=S,
        gain=K,
    )


def observability_matrix(F, H, n: Optional[int] = None) -> np.ndarray:
    """Stack ``[H; HF; HF^2; ...; HF^{n-1}]`` (plan section 5.3)."""
    F = np.asarray(F, dtype=float)
    H = np.asarray(H, dtype=float)
    if F.ndim != 2 or F.shape[0] != F.shape[1]:
        raise ScopeViolationError(f"F must be square; got shape {F.shape}")
    if n is None:
        n = F.shape[0]
    if H.ndim == 1:
        H = H.reshape(1, -1)
    if H.shape[1] != F.shape[0]:
        raise ScopeViolationError(f"H columns must match F dimension; got H.shape={H.shape}, F.shape={F.shape}")
    rows = [H]
    cur = H
    for _ in range(n - 1):
        cur = cur @ F
        rows.append(cur)
    return np.vstack(rows)


@dataclass(frozen=True)
class ObservabilityReport:
    matrix: np.ndarray
    singular_values: np.ndarray
    rank: int
    n_states: int


def observability_report(F, H, n: Optional[int] = None, rtol: Optional[float] = None) -> ObservabilityReport:
    """Numeric observability diagnostic: full singular-value spectrum of ``O``
    alongside the collapsed integer rank, so a caller can see how close to
    degenerate a given ``(F, H)`` instance is instead of only a pass/fail rank
    (module docstring: analytic rank claims and numeric rank diagnostics are
    different things and must not be conflated)."""
    O = observability_matrix(F, H, n=n)
    sv = np.linalg.svd(O, compute_uv=False)
    rank = int(np.linalg.matrix_rank(O, tol=rtol))
    n_states = F.shape[0] if n is None else n
    return ObservabilityReport(matrix=O, singular_values=sv, rank=rank, n_states=n_states)


__all__ = [
    "KalmanState",
    "make_state",
    "predict",
    "UpdateReport",
    "update",
    "observability_matrix",
    "ObservabilityReport",
    "observability_report",
]
