"""Count likelihood and estimation diagnostics (Paket MU3, plan §6.3).

Independent raw counts in the declared measurement model:

    n_j ~ Poisson(lambda_j),  NLL = sum_j [lambda_j - n_j log lambda_j + log(n_j!)]

Exact boundary cases: NLL(0; 0) = 0 and NLL(n > 0; 0) = +inf. There is NO
artificial positive floor that would make an impossible event possible.
Negative or non-integer counts and negative means are input errors.
Background-subtracted or lifetime-corrected values are not Poisson counts
and are not accepted (counts must be non-negative integers).

Poisson deviance  D = 2 sum_j [lambda_j - n_j + n_j log(n_j / lambda_j)]
(zero-count term 2 lambda_j) equals 2 (NLL - NLL_saturated); signed square
root residuals reproduce D as a sum of squares.

Fitting is wrapped ADDITIVELY here (the generic profile code in
identifiability/ is not changed): bounded multistart local optimisation
that records every run -- convergence, objective value, active bounds,
failures -- and groups the converged runs into distinct modes. Local
convergence is not global optimality; a multistart is no global proof.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Callable, List, Optional, Sequence, Tuple

import numpy as np
from scipy.optimize import minimize

from scoped_correspondence.errors import ScopeViolationError


def _check_counts(counts: Sequence) -> List[int]:
    out = []
    for n in counts:
        if isinstance(n, bool) or not isinstance(n, (int, np.integer)) or n < 0:
            raise ScopeViolationError(f"counts must be non-negative integers (raw Poisson counts), got {n!r}")
        out.append(int(n))
    return out


def _check_means(lams: Sequence[float]) -> List[float]:
    out = []
    for lam in lams:
        lam = float(lam)
        if not math.isfinite(lam) or lam < 0:
            raise ScopeViolationError(f"Poisson means must be finite and >= 0, got {lam!r}")
        out.append(lam)
    return out


def poisson_nll(counts: Sequence, means: Sequence[float]) -> float:
    """Exact-boundary NLL; returns math.inf for an impossible observation."""
    n, lam = _check_counts(counts), _check_means(means)
    if len(n) != len(lam):
        raise ScopeViolationError("counts and means must have the same length")
    total = 0.0
    for nj, lj in zip(n, lam):
        if lj == 0.0:
            if nj > 0:
                return math.inf
            continue
        total += lj - nj * math.log(lj) + math.lgamma(nj + 1)
    return total


def poisson_deviance(counts: Sequence, means: Sequence[float]) -> float:
    n, lam = _check_counts(counts), _check_means(means)
    total = 0.0
    for nj, lj in zip(n, lam):
        if nj == 0:
            total += 2 * lj
        elif lj == 0.0:
            return math.inf
        else:
            total += 2 * (lj - nj + nj * math.log(nj / lj))
    return total


def signed_root_residuals(counts: Sequence, means: Sequence[float]) -> List[float]:
    n, lam = _check_counts(counts), _check_means(means)
    out = []
    for nj, lj in zip(n, lam):
        d = poisson_deviance([nj], [lj])
        if math.isinf(d):
            raise ScopeViolationError("infinite deviance: an observed count has zero expected mean")
        out.append(math.copysign(math.sqrt(max(d, 0.0)), nj - lj))
    return out


@dataclass(frozen=True)
class Run:
    start: Tuple[float, ...]
    x: Tuple[float, ...]
    objective: float
    converged: bool
    message: str
    boundary_hit: Tuple[bool, ...]


@dataclass(frozen=True)
class Mode:
    x: Tuple[float, ...]
    objective: float
    n_runs: int
    boundary_hit: bool


@dataclass(frozen=True)
class FitReport:
    parameter_names: Tuple[str, ...]
    bounds: Tuple[Tuple[float, float], ...]
    runs: Tuple[Run, ...]
    modes: Tuple[Mode, ...]
    best: Optional[Mode]
    n_failed: int
    notes: Tuple[str, ...] = field(default_factory=tuple)


def multistart_fit(objective: Callable[[np.ndarray], float], names: Sequence[str], bounds: Sequence[Tuple[float, float]],
                   *, n_starts: int = 16, seed: int = 0, mode_tol: float = 1e-4, obj_tol: float = 1e-6) -> FitReport:
    """Bounded multistart (L-BFGS-B). Starts: a deterministic grid point per
    dimension combined with seeded uniform draws. Converged runs whose
    solutions differ by more than ``mode_tol`` (relative to the bound width)
    are separate modes; modes within ``obj_tol`` of the best objective are
    all reported -- never silently reduced to one."""
    if n_starts < 1:
        raise ScopeViolationError("n_starts must be >= 1")
    b = [(float(lo), float(hi)) for lo, hi in bounds]
    if any(not (math.isfinite(lo) and math.isfinite(hi) and lo < hi) for lo, hi in b):
        raise ScopeViolationError("bounds must be finite with lo < hi (search range must be explicit)")
    rng = np.random.default_rng(seed)
    starts = [np.array([lo + (hi - lo) * (k + 0.5) / n_starts for lo, hi in b]) for k in range(n_starts)]
    starts += [np.array([rng.uniform(lo, hi) for lo, hi in b]) for _ in range(n_starts)]
    runs: List[Run] = []
    failed = 0
    width = np.array([hi - lo for lo, hi in b])

    def safe(x):
        v = objective(np.asarray(x, dtype=float))
        return v if math.isfinite(v) else 1e300

    for s in starts:
        try:
            res = minimize(safe, s, method="L-BFGS-B", bounds=b)
            x = tuple(float(v) for v in res.x)
            obj = float(objective(np.asarray(x)))
            hit = tuple(bool(abs(xi - lo) <= 1e-9 * (hi - lo) or abs(xi - hi) <= 1e-9 * (hi - lo)) for xi, (lo, hi) in zip(x, b))
            runs.append(Run(tuple(float(v) for v in s), x, obj, bool(res.success) and math.isfinite(obj), str(res.message), hit))
        except Exception as exc:  # recorded, never hidden
            failed += 1
            runs.append(Run(tuple(float(v) for v in s), (), math.inf, False, f"exception: {exc}", tuple(False for _ in b)))
    ok = [r for r in runs if r.converged]
    modes: List[List[Run]] = []
    for r in sorted(ok, key=lambda r: r.objective):
        for group in modes:
            if np.all(np.abs((np.array(r.x) - np.array(group[0].x)) / width) <= mode_tol):
                group.append(r)
                break
        else:
            modes.append([r])
    mode_objs = [Mode(g[0].x, g[0].objective, len(g), any(any(x.boundary_hit) for x in g)) for g in modes]
    best = min(mode_objs, key=lambda m: m.objective) if mode_objs else None
    notes = ["local multistart: no global optimality claim"]
    if best is not None:
        near = [m for m in mode_objs if m.objective - best.objective <= obj_tol]
        if len(near) > 1:
            notes.append(f"{len(near)} distinct modes within {obj_tol} of the best objective: report all (possible aliases or degeneracy)")
        if best.boundary_hit:
            notes.append("best mode touches a search bound: an interval ending there is not closed")
    if failed or len(ok) < len(runs):
        notes.append(f"{len(runs) - len(ok)} run(s) did not converge or failed")
    return FitReport(tuple(names), tuple(b), tuple(runs), tuple(mode_objs), best, failed, tuple(notes))


__all__ = ["poisson_nll", "poisson_deviance", "signed_root_residuals", "Run", "Mode", "FitReport", "multistart_fit"]
