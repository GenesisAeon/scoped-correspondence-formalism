"""Measurement noise and finite channels (Paket ON2, plan §5.2, §7.2).

Gaussian control: Y = W u_S + eps, eps ~ N(0, sigma^2 I_2), equal priors.
The mean distance is 2 sqrt(2) |delta| and the optimal (Bayes) accuracy is

    A*(delta, sigma) = Phi(sqrt(2) |delta| / sigma) = (1 + erf(|delta| / sigma)) / 2

with the sigma = 0 limits stated explicitly (delta = 0 -> 1/2, else 1). The
SUM observer sees the same distribution for both classes at any noise.
Accuracy alone does not determine the mutual information (ON-C06).

Finite channels Q[s, z] = P(Z = z | S = s): validated STRICTLY before any
existing API is called (non-negative, finite, rows summing to 1) -- the
existing ``directed_information`` / ``broja`` renormalise silently, ON does
not rely on that (ON0 finding B1). A missing stimulus class is an UNKNOWN
channel row: no information or capacity is computed, never a uniform default.
Capacity uses the existing Arimoto-Blahut implementation for the FIXED
memoryless channel model and reports ``converged``; it is the capacity of the
composite system -> measurement -> code channel, not of the organoid.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

import numpy as np

from scoped_correspondence.errors import ScopeViolationError
from scoped_correspondence.observation.arimoto_blahut import blahut_arimoto_capacity, mutual_information_dmc


def bayes_accuracy_gaussian(delta: float, sigma: float) -> float:
    for v, n in ((delta, "delta"), (sigma, "sigma")):
        if not math.isfinite(v):
            raise ScopeViolationError(f"{n} must be finite")
    if sigma < 0:
        raise ScopeViolationError("sigma must be >= 0")
    if sigma == 0:
        return 0.5 if delta == 0 else 1.0  # noiseless limit -- not an empirical result
    return 0.5 * (1.0 + math.erf(abs(delta) / sigma))


def validate_channel(Q: Sequence[Sequence[float]], *, tol: float = 1e-12) -> np.ndarray:
    M = np.asarray(Q, dtype=float)
    if M.ndim != 2 or M.shape[0] < 1 or M.shape[1] < 1:
        raise ScopeViolationError("channel must be a non-empty 2-D matrix")
    if not np.all(np.isfinite(M)):
        raise ScopeViolationError("channel contains non-finite entries")
    if np.any(M < 0):
        raise ScopeViolationError("channel contains negative entries")
    if not np.allclose(M.sum(axis=1), 1.0, atol=tol, rtol=0):
        raise ScopeViolationError("channel rows must sum to 1 (no silent renormalisation)")
    return M


def validate_prior(r: Sequence[float], n: int, *, tol: float = 1e-12) -> np.ndarray:
    p = np.asarray(r, dtype=float)
    if p.shape != (n,) or not np.all(np.isfinite(p)) or np.any(p < 0) or abs(p.sum() - 1) > tol:
        raise ScopeViolationError("prior must be a finite probability vector over the stimuli")
    return p


@dataclass(frozen=True)
class ChannelReport:
    prior: Tuple[float, ...]
    rows: Tuple[Optional[Tuple[float, ...]], ...]  # None = unknown row (missing class)
    contingency: Optional[Tuple[Tuple[int, ...], ...]]
    sample_counts: Tuple[int, ...]
    coding: str
    window: str
    memory_assumption: str
    estimator: str
    pseudocount: float
    information_at_prior_bits: Optional[float]
    capacity_bits: Optional[float]
    capacity_converged: Optional[bool]
    status: str  # "exact_pmf" | "estimated" | "unknown_row"
    notes: Tuple[str, ...] = field(default_factory=tuple)


def exact_channel_report(Q, prior, *, coding: str, window: str = "exact model", memory_assumption: str = "memoryless, reset per trial") -> ChannelReport:
    M = validate_channel(Q)
    p = validate_prior(prior, M.shape[0])
    I = mutual_information_dmc(p, M)
    ba = blahut_arimoto_capacity(M)
    return ChannelReport(tuple(map(float, p)), tuple(tuple(map(float, r)) for r in M), None, (), coding, window, memory_assumption,
                         "exact PMF", 0.0, float(I), float(ba.capacity), bool(ba.converged), "exact_pmf",
                         ("capacity of the FIXED channel model; the optimising prior need not be biologically realisable",))


def estimated_channel_report(contingency: Sequence[Sequence[int]], prior, *, coding: str, window: str, memory_assumption: str,
                             pseudocount: float = 0.0) -> ChannelReport:
    """Rows estimated from counts n[s, z]. A row with zero counts is UNKNOWN:
    no information or capacity is reported. Pseudocounts are an explicit,
    visible regularisation assumption."""
    C = np.asarray(contingency, dtype=float)
    if C.ndim != 2 or np.any(C < 0) or not np.all(np.isfinite(C)) or np.any(C != np.round(C)):
        raise ScopeViolationError("contingency must hold non-negative integer counts")
    if pseudocount < 0 or not math.isfinite(pseudocount):
        raise ScopeViolationError("pseudocount must be finite and >= 0")
    p = validate_prior(prior, C.shape[0])
    counts = tuple(int(x) for x in C.sum(axis=1))
    rows: List[Optional[Tuple[float, ...]]] = []
    for r in C:
        if r.sum() == 0:
            rows.append(None)
        else:
            rr = (r + pseudocount) / (r.sum() + pseudocount * C.shape[1])
            rows.append(tuple(map(float, rr)))
    cont = tuple(tuple(int(x) for x in r) for r in C)
    notes = []
    if pseudocount > 0:
        notes.append(f"pseudocount {pseudocount} added to every cell (regularisation assumption)")
    if any(r is None for r in rows):
        return ChannelReport(tuple(map(float, p)), tuple(rows), cont, counts, coding, window, memory_assumption,
                             "plug-in", pseudocount, None, None, None, "unknown_row",
                             tuple(notes) + ("a stimulus class has no observations: its channel row is unknown -- no uniform default",))
    M = validate_channel(rows)
    ba = blahut_arimoto_capacity(M)
    return ChannelReport(tuple(map(float, p)), tuple(rows), cont, counts, coding, window, memory_assumption, "plug-in", pseudocount,
                         float(mutual_information_dmc(p, M)), float(ba.capacity), bool(ba.converged), "estimated",
                         tuple(notes) + ("plug-in estimate from finite counts: biased; no capacity from a single accuracy value",))


def accuracy_of_identity_decoder(Q, prior) -> float:
    M = validate_channel(Q)
    p = validate_prior(prior, M.shape[0])
    if M.shape[0] != M.shape[1]:
        raise ScopeViolationError("identity decoding needs a square channel")
    return float(sum(p[s] * M[s, s] for s in range(M.shape[0])))


__all__ = ["bayes_accuracy_gaussian", "validate_channel", "validate_prior", "ChannelReport", "exact_channel_report",
           "estimated_channel_report", "accuracy_of_identity_decoder"]
