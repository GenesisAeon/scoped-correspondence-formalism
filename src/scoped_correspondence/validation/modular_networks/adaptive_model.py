"""Bounded adaptive dynamics (Paket ON3, plan §6).

Dimensionless two-time-scale model (fast steps k inside a trial, slow
training phase d):

    x_{k+1} = (1 - ell) x_k + ell tanh(A x_k + B u_k),   0 < ell <= 1, x_0 = 0

with B, u >= 0 (states stay in [0, 1)). Observation: y = H sum_{k in window}
w_k x_k + eps. Units are "model step" and dimensionless amplitude -- no
biological milliseconds or firing rates without calibration.

Resources (§6.2): N = 12 states, M in {1, 2, 3} equal modules, A_ij = row i
receives from column j, zero diagonal, A >= 0, every row sum gamma in (0, 1):
intra-module weight gamma (1 - c)/(n - 1), inter-module gamma c/(N - n); for
M = 1, gamma/(N - 1) and c is NOT applicable. A fixed TOTAL budget, not a
model of growing tissue. For N = 12, M = 2 with c = 6/11 and M = 3 with
c = 8/11 the matrix equals the M = 1 matrix exactly: module NAMES alone must
not create an advantage.

Adaptation (§6.4): delayed Hebb rule with a FIXED edge mask (diagonal and
forbidden edges stay zero permanently):

    G_ij = M_ij <x_{k+1,i} x_{k,j}>_train,  A~ = (1 - eta) A + eta G,
    A'_ij = gamma A~_ij / sum_j A~_ij,  0 <= eta < 1

It uses local pre/post activity only -- no stimulus labels, no target score.
It keeps every row sum gamma but NOT automatically the inter fraction c,
which is reported after each update. A changes only on training trials;
probe and test use frozen weights and reset the fast state.

Stability (§6.5): for frozen A and identical input, tanh is 1-Lipschitz and
||A||_inf = gamma, so ||F(x) - F(z)||_inf <= (1 - ell + ell gamma) ||x - z||_inf
-- a contraction certificate for frozen weights only, not a convergence
proof for the coupled learning process.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from fractions import Fraction
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from scoped_correspondence.errors import ScopeViolationError


def module_partition(N: int, M: int) -> List[int]:
    if M < 1 or N % M:
        raise ScopeViolationError("N must be divisible by M")
    n = N // M
    if M > 1 and n < 2:
        raise ScopeViolationError("modules need at least two states")
    return [i // n for i in range(N)]


def budget_adjacency(N: int, M: int, gamma, c=None):
    """Exact (Fraction) or float adjacency with row sums gamma."""
    if not (0 < gamma < 1):
        raise ScopeViolationError("gamma must lie in (0, 1)")
    mod = module_partition(N, M)
    n = N // M
    if M == 1:
        if c is not None:
            raise ScopeViolationError("c is not applicable for M = 1")
    elif c is None or not (0 <= c <= 1):
        raise ScopeViolationError("c in [0, 1] required for M > 1")
    zero = Fraction(0) if isinstance(gamma, Fraction) else 0.0
    A = [[zero] * N for _ in range(N)]
    for i in range(N):
        for j in range(N):
            if i == j:
                continue
            if M == 1:
                A[i][j] = gamma / (N - 1)
            elif mod[i] == mod[j]:
                A[i][j] = gamma * (1 - c) / (n - 1)
            else:
                A[i][j] = gamma * c / (N - n)
    return A, mod


def edge_mask(N: int, mod: Sequence[int], *, allow_inter: bool = True) -> List[List[int]]:
    """Permanent mask: no self-loops; optionally no inter-module edges."""
    return [[int(i != j and (allow_inter or mod[i] == mod[j])) for j in range(N)] for i in range(N)]


def inter_fraction(A, mod) -> List:
    out = []
    for i, row in enumerate(A):
        tot = sum(row)
        inter = sum(row[j] for j in range(len(row)) if mod[j] != mod[i])
        out.append(None if tot == 0 else inter / tot)
    return out


def hebb_update(A, pre_post_pairs: Sequence[Tuple[Sequence, Sequence]], mask, eta, gamma):
    """One adaptation step from TRAINING activity pairs (x_k, x_{k+1}).
    eta = 0 returns A exactly. Rows with a zero denominator are refused."""
    if not (0 <= eta < 1):
        raise ScopeViolationError("eta must lie in [0, 1)")
    N = len(A)
    if not pre_post_pairs:
        raise ScopeViolationError("need training activity")
    # Public-API domain (Followup-Review §5.3): validate the caller's mask,
    # weights, activities and gamma; the model RULE itself is unchanged.
    if not (0 < gamma < 1):
        raise ScopeViolationError("gamma must lie in (0, 1)")
    if any(len(r) != N for r in A) or len(mask) != N or any(len(r) != N for r in mask):
        raise ScopeViolationError("A and mask must be square N x N")
    if any(m not in (0, 1) for r in mask for m in r) or any(mask[i][i] for i in range(N)):
        raise ScopeViolationError("mask entries must be 0/1 with a zero diagonal (no self-loops)")
    for v in (x for r in A for x in r):
        if isinstance(v, bool) or not math.isfinite(float(v)) or v < 0:
            raise ScopeViolationError("weights must be finite and non-negative")
    for pre, post in pre_post_pairs:
        if len(pre) != N or len(post) != N:
            raise ScopeViolationError("activity vectors must have length N")
        if any(isinstance(v, bool) or not math.isfinite(float(v)) or v < 0 for v in list(pre) + list(post)):
            raise ScopeViolationError("activities must be finite and non-negative")
    G = [[0] * N for _ in range(N)]
    for pre, post in pre_post_pairs:
        for i in range(N):
            for j in range(N):
                G[i][j] += post[i] * pre[j]  # the edge mask is applied once, below
    m = len(pre_post_pairs)
    # int / int would silently turn exact inputs into floats
    G = [[Fraction(g, m) if isinstance(g, int) else g / m for g in row] for row in G]
    out = []
    for i in range(N):
        At = [((1 - eta) * A[i][j] + eta * G[i][j]) * mask[i][j] for j in range(N)]
        s = sum(At)
        if s <= 0:
            raise ScopeViolationError(f"row {i}: non-positive normalisation denominator")
        out.append([gamma * a / s for a in At])
    return out


def contraction_bound(ell, gamma):
    if not (0 < ell <= 1) or not (0 < gamma < 1):
        raise ScopeViolationError("0 < ell <= 1 and 0 < gamma < 1 required")
    return 1 - ell + ell * gamma


@dataclass(frozen=True)
class NetworkConfig:
    N: int
    M: int
    gamma: float
    c: Optional[float]
    ell: float
    input_states: Tuple[int, int]
    output_states: Tuple[int, ...]
    steps: int
    window: Tuple[int, ...]
    eta: float
    allow_inter: bool = True
    seeds: Dict[str, int] = field(default_factory=dict)  # topology, adaptation, decoder, test

    def describe(self) -> Dict[str, object]:
        return dict(self.__dict__)


def simulate_trial(A: np.ndarray, B: np.ndarray, u: np.ndarray, ell: float, steps: int) -> np.ndarray:
    """Fast dynamics from x_0 = 0 (reset per trial). Returns (steps+1, N)."""
    N = A.shape[0]
    x = np.zeros(N)
    traj = [x.copy()]
    for _ in range(steps):
        x = (1 - ell) * x + ell * np.tanh(A @ x + B @ u)
        traj.append(x.copy())
    return np.array(traj)


def observe_trial(traj: np.ndarray, H: np.ndarray, window: Sequence[int], rng: Optional[np.random.Generator], sigma: float) -> np.ndarray:
    y = H @ traj[list(window)].sum(axis=0)
    if sigma < 0:
        raise ScopeViolationError("sigma must be >= 0")
    if sigma > 0:
        y = y + rng.normal(scale=sigma, size=y.shape)
    return y


def input_matrix(N: int, inputs: Tuple[int, int], amplitude: float = 1.0) -> np.ndarray:
    """Two equally normalised input columns at the declared states."""
    B = np.zeros((N, 2))
    B[inputs[0], 0] = amplitude
    B[inputs[1], 1] = amplitude
    return B


def readout_matrix(N: int, outputs: Sequence[int]) -> np.ndarray:
    H = np.zeros((len(outputs), N))
    for r, o in enumerate(outputs):
        H[r, o] = 1.0
    return H


def adapt(A: np.ndarray, B: np.ndarray, cfg: NetworkConfig, stimuli: Sequence[np.ndarray], rng: np.random.Generator,
          n_trials: int, mask) -> Tuple[np.ndarray, List[List[Optional[float]]]]:
    """Training phase: random balanced stimulus order (adaptation RNG stream);
    returns the adapted A and the inter fraction after every update."""
    mod = module_partition(cfg.N, cfg.M)
    history = []
    A_cur = A.copy()
    order = np.array([t % len(stimuli) for t in range(n_trials)])
    rng.shuffle(order)
    for t in order:
        traj = simulate_trial(A_cur, B, stimuli[t], cfg.ell, cfg.steps)
        pairs = [(traj[k], traj[k + 1]) for k in range(cfg.steps)]
        A_cur = np.array(hebb_update(A_cur.tolist(), pairs, mask, cfg.eta, cfg.gamma))
        history.append(inter_fraction(A_cur.tolist(), mod))
    return A_cur, history


__all__ = ["module_partition", "budget_adjacency", "edge_mask", "inter_fraction", "hebb_update", "contraction_bound", "NetworkConfig",
           "simulate_trial", "observe_trial", "input_matrix", "readout_matrix", "adapt"]
