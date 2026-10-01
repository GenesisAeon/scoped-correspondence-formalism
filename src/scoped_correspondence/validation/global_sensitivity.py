"""Global (joint) sensitivity: Sobol first and total indices (Paket J7, plan §13).

Uncertainty model FIRST (plan §13.1), kept as four separate things:

- scenario space: which combinations are plausible/worth checking -- no
  probability follows from it (``JointScenarioGrid``);
- input distribution: an explicitly declared JOINT distribution; this module
  implements only INDEPENDENT inputs (product of declared marginals);
- measurement vs model uncertainty: recorded per input as provenance text;
- target quantity: chosen by the caller (parameter, prediction, test loss,
  difference of test losses).

Sobol indices for independent inputs and finite positive output variance:

    S_i  = Var(E[f | X_i]) / Var(f),   S_Ti = 1 - Var(E[f | X_-i]) / Var(f)

Pick-freeze estimators with independent sample matrices A, B and A_B^(i)
(= A with column i taken from B):

    S_i  ~ mean[ f(B) (f(A_B^(i)) - f(A)) ] / V
    S_Ti ~ mean[ (f(A) - f(A_B^(i)))^2 ] / (2 V)

V is the sample variance (divisor N-1) of the pooled f(A), f(B) values.
Finite-sample estimates may fall outside [0, 1]; they are NOT clipped.
Dependent inputs need a different decomposition (Kucherenko et al., S12)
and are refused (``unsupported``). For polynomials in independent U[0,1]
inputs, ``analytic_sobol_polynomial`` gives exact rational indices.
"""
from __future__ import annotations

import itertools
from dataclasses import dataclass, field
from fractions import Fraction
from typing import Callable, Dict, List, Mapping, Optional, Sequence, Tuple

import numpy as np

from scoped_correspondence.errors import ScopeViolationError


@dataclass(frozen=True)
class InputSpec:
    name: str
    sampler: Callable[[np.random.Generator, int], np.ndarray]  # independent marginal
    provenance: str  # e.g. "documented measurement error (catalogue e_D)" or "declared model-variant scenario"
    kind: str = "measurement"  # "measurement" | "model_variant" | "scenario_only"

    def __post_init__(self) -> None:
        if self.kind not in ("measurement", "model_variant", "scenario_only"):
            raise ScopeViolationError("kind must be measurement, model_variant or scenario_only")
        if not self.provenance.strip():
            raise ScopeViolationError("every input needs a provenance statement")


@dataclass(frozen=True)
class SobolReport:
    names: Tuple[str, ...]
    status: str  # "estimated" | "undefined_zero_variance" | "unsupported"
    first_order: Optional[Tuple[float, ...]]
    total: Optional[Tuple[float, ...]]
    variance: Optional[float]
    n_base: int
    seed: int
    estimator: str = "pick-freeze (Saltelli-type), variance with divisor N-1, not clipped"
    standard_errors_first: Optional[Tuple[float, ...]] = None
    standard_errors_total: Optional[Tuple[float, ...]] = None
    notes: Tuple[str, ...] = field(default_factory=tuple)


def sobol_indices(f: Callable[[np.ndarray], np.ndarray], inputs: Sequence[InputSpec], *, n: int, seed: int,
                  independent: bool = True, var_tol: float = 1e-14) -> SobolReport:
    """f maps an (N, k) array to N outputs. ``independent=False`` is refused
    (dependent inputs need another decomposition)."""
    names = tuple(s.name for s in inputs)
    if not independent:
        return SobolReport(names, "unsupported", None, None, None, n, seed,
                           notes=("dependent inputs: first/total Sobol indices of independent inputs would be misleading",))
    if n < 2 or not inputs:
        raise ScopeViolationError("need n >= 2 and at least one input")
    rng = np.random.default_rng(seed)
    k = len(inputs)
    A = np.column_stack([s.sampler(rng, n) for s in inputs])
    B = np.column_stack([s.sampler(rng, n) for s in inputs])
    fA, fB = np.asarray(f(A), dtype=float), np.asarray(f(B), dtype=float)
    V = float(np.var(np.concatenate([fA, fB]), ddof=1))
    if not np.isfinite(V) or V <= var_tol * max(1.0, float(np.mean(np.concatenate([fA, fB]) ** 2))):
        return SobolReport(names, "undefined_zero_variance", None, None, V, n, seed,
                           notes=("output variance is zero: Sobol indices are undefined (not 0)",))
    S, ST, seS, seST = [], [], [], []
    for i in range(k):
        ABi = A.copy()
        ABi[:, i] = B[:, i]
        fABi = np.asarray(f(ABi), dtype=float)
        y1 = fB * (fABi - fA)
        y2 = (fA - fABi) ** 2 / 2
        S.append(float(y1.mean() / V))
        ST.append(float(y2.mean() / V))
        seS.append(float(y1.std(ddof=1) / np.sqrt(n) / V))
        seST.append(float(y2.std(ddof=1) / np.sqrt(n) / V))
    notes = []
    if any(s < 0 or s > 1 for s in S + ST):
        notes.append("some finite-sample estimates lie outside [0, 1]; reported unclipped")
    return SobolReport(names, "estimated", tuple(S), tuple(ST), V, n, seed, standard_errors_first=tuple(seS),
                       standard_errors_total=tuple(seST), notes=tuple(notes))


# --- exact reference for polynomials in independent U[0,1] inputs ------------

Poly = Dict[Tuple[int, ...], Fraction]


def _integrate(p: Poly, axis: int) -> Poly:
    out: Poly = {}
    for mono, c in p.items():
        e = list(mono)
        val = c / (e[axis] + 1)
        e[axis] = 0
        out[tuple(e)] = out.get(tuple(e), Fraction(0)) + val
    return out


def _mul(p: Poly, q: Poly) -> Poly:
    out: Poly = {}
    for m1, a in p.items():
        for m2, b in q.items():
            m = tuple(x + y for x, y in zip(m1, m2))
            out[m] = out.get(m, Fraction(0)) + a * b
    return out


def _expect(p: Poly, k: int) -> Fraction:
    for ax in range(k):
        p = _integrate(p, ax)
    return p.get(tuple([0] * k), Fraction(0))


def _var(p: Poly, k: int) -> Fraction:
    return _expect(_mul(p, p), k) - _expect(p, k) ** 2


def analytic_sobol_polynomial(p: Mapping[Tuple[int, ...], object], k: int) -> Tuple[Fraction, Tuple[Fraction, ...], Tuple[Fraction, ...]]:
    """Exact (V, S, S_T) for a polynomial {exponent tuple: coefficient} in k
    independent U[0,1] inputs. Raises for zero variance (undefined)."""
    poly: Poly = {tuple(m): Fraction(c) for m, c in p.items()}
    if any(len(m) != k for m in poly):
        raise ScopeViolationError("exponent tuples must have length k")
    V = _var(poly, k)
    if V == 0:
        raise ScopeViolationError("zero output variance: Sobol indices undefined")
    S, ST = [], []
    for i in range(k):
        cond_i = poly
        for ax in range(k):
            if ax != i:
                cond_i = _integrate(cond_i, ax)  # E[f | X_i]
        cond_rest = _integrate(poly, i)  # E[f | X_-i]
        S.append(_var(cond_i, k) / V)
        ST.append(1 - _var(cond_rest, k) / V)
    return V, tuple(S), tuple(ST)


@dataclass(frozen=True)
class JointScenarioGrid:
    """A scenario space: a full grid of declared values per input. It carries
    NO probabilities; frequencies of 'winners' over it are not empirical
    probabilities."""

    names: Tuple[str, ...]
    values: Tuple[Tuple[float, ...], ...]
    provenance: Tuple[str, ...]

    def __post_init__(self) -> None:
        if not (len(self.names) == len(self.values) == len(self.provenance)):
            raise ScopeViolationError("names, values and provenance must align")
        if any(len(v) == 0 for v in self.values):
            raise ScopeViolationError("every input needs at least one scenario value")

    def points(self) -> List[Dict[str, float]]:
        return [dict(zip(self.names, combo)) for combo in itertools.product(*self.values)]


__all__ = ["InputSpec", "SobolReport", "sobol_indices", "analytic_sobol_polynomial", "JointScenarioGrid"]
