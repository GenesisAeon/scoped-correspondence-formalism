"""Sensitivity and experimental design (Paket MU5, plan §8).

Local Fisher information for the phase-scan count model

    lambda_k = n_k (1 + C cos(alpha_k + phi)),   phi = K a + phi0

with n_k the expected (signal) events in step k:

    I_phi = sum_k n_k C^2 sin^2(alpha_k + phi) / (1 + C cos(alpha_k + phi))

(known normalisation and contrast, no background). For ideal quadrature
(all events at alpha + phi = pi/2) I_phi = N C^2, hence the LOCAL bound
sigma_a >= 1 / (C sqrt(N) K). A four-step scan at phi = 0 gives N C^2 / 2.

Free nuisance parameters need the JOINT information matrix; a singular
matrix is reported as singular -- never inverted with a pseudo-inverse
into apparent precision.

Budgets are always named: ``detected_events``, ``incoming_atoms`` or
``measurement_time``. With a fixed incoming budget and time-independent
contrast, N(T) = N0 exp(-2T/tau) and sigma_a(T) ~ exp(T/tau)/T^2 with the
conditional optimum T = 2 tau. Holding N fixed while claiming decay costs is
contradictory and is refused.

The 3.84 deviance threshold is an asymptotic 95 % reference for a regular
scalar parameter only; coverage is checked by simulation, not assumed.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Optional, Sequence, Tuple

import numpy as np

from scoped_correspondence.errors import ScopeViolationError

BUDGET_KINDS = ("detected_events", "incoming_atoms", "measurement_time")


def phase_fisher(n_per_step: Sequence[float], alphas: Sequence[float], C: float, phi: float = 0.0) -> float:
    if len(n_per_step) != len(alphas) or not alphas:
        raise ScopeViolationError("one expected event count per scan step")
    if not 0 <= C <= 1:
        raise ScopeViolationError("contrast must lie in [0, 1]")
    I = 0.0
    for n, a in zip(n_per_step, alphas):
        lam_rel = 1 + C * math.cos(a + phi)
        if lam_rel <= 0:
            raise ScopeViolationError("zero expected count in a scan step: local Fisher information undefined there")
        I += n * C * C * math.sin(a + phi) ** 2 / lam_rel
    return I


def sigma_a_local_bound(N: float, C: float, K: float) -> Optional[float]:
    """1 / (C sqrt(N) K); None when C = 0 or N = 0 (no information)."""
    if N < 0 or K <= 0:
        raise ScopeViolationError("N >= 0 and K > 0 required")
    if C == 0 or N == 0:
        return None
    return 1.0 / (C * math.sqrt(N) * K)


def events_for_relative_precision(rel: float, g: float, C: float, K: float) -> float:
    """Detected signal events N with 1 / (C sqrt(N) K) = rel * g (ideal local formula)."""
    if rel <= 0 or g <= 0 or not 0 < C <= 1 or K <= 0:
        raise ScopeViolationError("invalid inputs")
    return 1.0 / (C * K * rel * g) ** 2


@dataclass(frozen=True)
class FisherReport:
    names: Tuple[str, ...]
    matrix: Tuple[Tuple[float, ...], ...]
    rank: int
    singular: bool
    covariance_bound: Optional[Tuple[Tuple[float, ...], ...]]
    note: str


def joint_fisher(n_per_step: Sequence[float], alphas: Sequence[float], C: float, Ks: Sequence[float], *, free_offset: bool,
                 phi: float = 0.0, rank_tol: float = 1e-10) -> FisherReport:
    """Joint information for (a [, phi0]) when step k has sensitivity Ks[k]
    (different flight times allowed). With one flight time and a free
    offset the matrix is singular (counterexample 1 of MU4)."""
    if not (len(n_per_step) == len(alphas) == len(Ks)):
        raise ScopeViolationError("shape mismatch")
    names = ("a", "phi0") if free_offset else ("a",)
    M = np.zeros((len(names), len(names)))
    for n, al, K in zip(n_per_step, alphas, Ks):
        lam_rel = 1 + C * math.cos(al + phi)
        if lam_rel <= 0:
            raise ScopeViolationError("zero expected count in a step")
        dphi = -n * C * math.sin(al + phi)  # d lambda / d phi
        grad = np.array([dphi * K, dphi] if free_offset else [dphi * K])
        M += np.outer(grad, grad) / (n * lam_rel)
    s = np.linalg.svd(M, compute_uv=False)
    rank = int(np.sum(s > rank_tol * max(s.max(), 1e-300)))
    singular = rank < len(names)
    cov = None if singular else tuple(tuple(float(x) for x in row) for row in np.linalg.inv(M))
    note = ("singular information matrix: no finite variance bound; no pseudo-inverse is used"
            if singular else "local Cramer-Rao bound under the stated idealisations")
    return FisherReport(names, tuple(tuple(float(x) for x in row) for row in M), rank, singular, cov, note)


def sigma_vs_flight_time(T: float, tau: float, *, budget: str, N0: float = 1.0, C: float = 1.0, d: float = 1.0) -> float:
    """sigma_a(T) for a NAMED budget (ideal quadrature, K = 2 pi T^2 / d).

    incoming_atoms: N = N0 exp(-2T/tau)  -> optimum T = 2 tau
    detected_events: N = N0 fixed        -> sigma ~ 1/T^2 (no decay cost by construction)
    measurement_time: requires a rate model and is not offered here."""
    if budget not in BUDGET_KINDS:
        raise ScopeViolationError(f"budget must be one of {BUDGET_KINDS}")
    if budget == "measurement_time":
        raise ScopeViolationError("a measurement-time budget needs an explicit rate model; not provided")
    K = 2 * math.pi * T * T / d
    N = N0 * math.exp(-2 * T / tau) if budget == "incoming_atoms" else N0
    return 1.0 / (C * math.sqrt(N) * K)


@dataclass(frozen=True)
class CoverageResult:
    scenario: str
    n_reps: int
    seed: int
    covered: int
    coverage: float
    binomial_se: float
    unbounded: int
    interval_method: str
    notes: Tuple[str, ...]


def deviance_interval(nll_grid: np.ndarray, grid: np.ndarray, threshold: float = 3.84) -> Tuple[Optional[Tuple[float, float]], bool]:
    """Set {a : 2 (NLL(a) - min) <= threshold} on the grid. Returns
    ((lo, hi), touches_search_bound). A set that reaches the grid edge is
    flagged -- it is not a closed interval."""
    d = 2 * (nll_grid - nll_grid.min())
    inside = np.where(d <= threshold)[0]
    if inside.size == 0:
        return None, False
    touches = inside[0] == 0 or inside[-1] == len(grid) - 1
    return (float(grid[inside[0]]), float(grid[inside[-1]])), bool(touches)


__all__ = ["BUDGET_KINDS", "phase_fisher", "sigma_a_local_bound", "events_for_relative_precision", "FisherReport",
           "joint_fisher", "sigma_vs_flight_time", "CoverageResult", "deviance_interval"]
