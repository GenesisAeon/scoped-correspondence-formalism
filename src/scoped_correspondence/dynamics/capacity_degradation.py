"""Phenomenological battery capacity degradation and observation ablation (DOMAIN_EXPANSION_ROADMAP.md Paket B5a).

Response to prompts/Answers/nicht_stationäre_Treiber/
SCF_DOMAIN_EXPANSION_IMPLEMENTATION_PLAN.md, section 11.2: from a single
capacity series, irreversible aging, reversible/protocol-dependent
influences, and measurement error are GENERALLY NOT SEPARATELY
IDENTIFIABLE -- so this module restricts itself to phenomenological MEAN
capacity models plus an EXPLICIT observation-noise ablation, never claiming
the three physical components as separately proven.

Three deliberately simple mean models (``persistence``, ``linear``,
``power``) are each combined with two observation models (independent
residuals, or AR(1)-correlated residuals) -- a genuine 2x2 ablation that
separates the benefit of a better MEAN trend from the benefit of a better
OBSERVATION model, rather than conflating "more flexible model" with "wins
for one specific unexamined reason".

At ``a=0`` the power-law exponent ``p`` is not identified (the model
degenerates to the constant ``C0`` regardless of ``p``); at ``n=0`` the
mean is ``C0`` independent of ``p`` for ``p>0``. Both are documented model
degeneracies, not bugs.

**Correction (2026-09-24, response to
prompts/Answers/nicht_stationäre_Treiber/SCF_Review_fcc9a43.md, findings
R1+R2 -- two real bugs in the AR(1) forecast path):**

**R1: ``predict_capacity_distribution`` used ``residual_std`` (the TOTAL
observed residual spread) as the AR(1) INNOVATION standard deviation.**
For a stationary AR(1) process ``r[n+1] = phi*r[n] + eps[n]``, these are
different quantities related by ``Var(r) = sigma_eps^2 / (1-phi^2)`` --
using the total residual std as the innovation std inflates the simulated
variance by an extra factor of ``1/(1-phi^2)`` on top of the correct
value. Astra's reproduction (`phi=0.8`, true innovation SD ``0.01``,
n=12000): fitted `phi=0.7966`, actual innovation SD recovered from the AR
recursion `0.01001`, but the OLD code used `residual_std=0.01656` instead
-- a variance ratio of `2.736`, matching `1/(1-0.7966^2)=2.736` almost
exactly. Fixed by estimating and storing ``innovation_std`` SEPARATELY
(from the AR recursion's own one-step-ahead residuals
``r[1:] - phi*r[:-1]``), never conflated with ``residual_std``.

**R2: the same function advanced the AR residual by exactly ONE step per
REQUESTED OUTPUT ELEMENT, regardless of the actual gap between requested
cycle numbers.** A forecast for cycle 10 requested alone (``[10]``) was
therefore treated as 1 step ahead, while the SAME target cycle requested
as part of a dense array (``[1,...,10]``) was treated as 10 steps ahead --
two different answers for the identical question. Astra's exact
(noise-free) counterexample: constant mean, `phi=0.8`, last residual `1`
at cycle 0 -- sparse query ``[10]`` gave `2.8` (mean 2 + phi^1*1, WRONG),
dense query ``[1..10]`` gave the mathematically correct `2+phi^10=
2.1073741824`. Fixed by requiring an explicit ``origin_cycle`` parameter
and propagating the AR(1) process the ACTUAL number of cycles between
consecutive requested points (and from ``origin_cycle`` to the first
requested point), using the exact conditional mean/variance for a ``d``-step
AR(1) continuation: mean ``phi**d * r``, variance
``innovation_std**2 * sum_{k=0}^{d-1} phi**(2k)`` (``= innovation_std**2 *
(1-phi**(2d))/(1-phi**2)`` for ``phi != 0``). Verified: the marginal
distribution of a given target cycle is now IDENTICAL regardless of which
other output cycles are also requested (checked both by the deterministic
noise-free identity above and by matching the first two moments across
sparse/dense queries under randomness).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Sequence, Tuple

import numpy as np
from scipy.optimize import curve_fit, lsq_linear

from scoped_correspondence.errors import ScopeViolationError

MODEL_PERSISTENCE = "persistence"
MODEL_LINEAR = "linear"
MODEL_POWER = "power"
_VALID_MODELS = (MODEL_PERSISTENCE, MODEL_LINEAR, MODEL_POWER)


def mean_capacity(model_spec: str, params: Dict[str, float], n: np.ndarray) -> np.ndarray:
    """Mean capacity ``m(n)`` for the given fitted model. Returns the RAW model
    value, including possibly negative extrapolations -- callers must treat a
    negative value as a MODEL-DOMAIN VIOLATION (plan section 11.2), never as a
    physical capacity or silently clip it away.
    """
    n = np.asarray(n, dtype=float)
    if model_spec == MODEL_PERSISTENCE:
        return np.full_like(n, params["last_value"])
    if model_spec == MODEL_LINEAR:
        return params["C0"] - params["a"] * n
    if model_spec == MODEL_POWER:
        return params["C0"] - params["a"] * np.power(n, params["p"])
    raise ScopeViolationError(f"unknown model_spec: {model_spec!r}; must be one of {_VALID_MODELS}")


@dataclass(frozen=True)
class CapacityTrendFit:
    model_spec: str
    params: Dict[str, float]
    residual_std: float
    ar1_phi: Optional[float]
    train_cycles: Tuple[float, ...]
    train_capacity: Tuple[float, ...]
    innovation_std: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "model_spec": self.model_spec, "params": dict(self.params), "residual_std": self.residual_std,
            "ar1_phi": self.ar1_phi, "innovation_std": self.innovation_std, "n_train": len(self.train_cycles),
        }


def _fit_ar1(residuals: np.ndarray) -> Tuple[Optional[float], Optional[float]]:
    """OLS estimate of phi in r[n+1] = phi*r[n] + eps[n], clipped to (-1, 1), plus the
    INNOVATION standard deviation estimated from the AR recursion's own one-step-ahead
    residuals ``eps[n] = r[n+1] - phi*r[n]`` -- deliberately NOT the total residual std
    (see module docstring, SCF_Review_fcc9a43.md finding R1): for a stationary AR(1)
    process these differ by a factor of ``1/sqrt(1-phi^2)`` in standard deviation.
    """
    if len(residuals) < 3:
        return None, None
    x, y = residuals[:-1], residuals[1:]
    denom = float(np.sum(x * x))
    if denom <= 1e-12:
        phi = 0.0
    else:
        phi = float(np.clip(float(np.sum(x * y) / denom), -0.999, 0.999))
    innovations = y - phi * x
    innovation_std = float(np.std(innovations, ddof=1)) if len(innovations) > 1 else 0.0
    return phi, innovation_std


def fit_capacity_trend(
    train_cycles: Sequence[float], train_capacity: Sequence[float], model_spec: str, fit_ar1: bool = False
) -> CapacityTrendFit:
    """Fit ONLY on the given (training-prefix) cycles/capacities -- callers are
    responsible for ensuring no future cycle indices are passed in (plan section
    5.2's leakage protocol). ``a>=0`` (capacity cannot IMPROVE on average) is
    enforced as a bound in the least-squares fit, not clipped after the fact.
    """
    cycles = np.asarray(train_cycles, dtype=float)
    cap = np.asarray(train_capacity, dtype=float)
    if len(cycles) != len(cap):
        raise ScopeViolationError(f"train_cycles and train_capacity must match length; got {len(cycles)} vs {len(cap)}")
    if len(cycles) < 2:
        raise ScopeViolationError("need at least 2 training points")

    if model_spec == MODEL_PERSISTENCE:
        params = {"last_value": float(cap[-1])}
    elif model_spec == MODEL_LINEAR:
        design = np.column_stack([np.ones_like(cycles), -cycles])
        result = lsq_linear(design, cap, bounds=([-np.inf, 0.0], [np.inf, np.inf]))
        params = {"C0": float(result.x[0]), "a": float(result.x[1])}
    elif model_spec == MODEL_POWER:
        c0_guess = float(cap[0])
        span = max(float(cap[0] - cap[-1]), 1e-6)
        n_span = max(float(cycles[-1] - cycles[0]), 1.0)

        def model_fn(n, c0, a, p):
            return c0 - a * np.power(n, p)

        popt, _ = curve_fit(
            model_fn, cycles, cap, p0=[c0_guess, span / n_span, 1.0],
            bounds=([-np.inf, 0.0, 1e-6], [np.inf, np.inf, 10.0]), maxfev=20000,
        )
        params = {"C0": float(popt[0]), "a": float(popt[1]), "p": float(popt[2])}
    else:
        raise ScopeViolationError(f"unknown model_spec: {model_spec!r}; must be one of {_VALID_MODELS}")

    residuals = cap - mean_capacity(model_spec, params, cycles)
    residual_std = float(np.std(residuals, ddof=1)) if len(residuals) > 1 else 0.0
    ar1_phi, innovation_std = _fit_ar1(residuals) if fit_ar1 else (None, None)

    return CapacityTrendFit(
        model_spec=model_spec, params=params, residual_std=residual_std, ar1_phi=ar1_phi,
        train_cycles=tuple(cycles), train_capacity=tuple(cap), innovation_std=innovation_std,
    )


def predict_capacity_distribution(
    fit: CapacityTrendFit, origin_cycle: float, origin_residual: Optional[float],
    future_cycle_indices: Sequence[float], rng: np.random.Generator, n_samples: int = 1000,
) -> np.ndarray:
    """Simulate ``n_samples`` capacity trajectories over ``future_cycle_indices``.

    **Correction (SCF_Review_fcc9a43.md, finding R2):** the AR(1) residual is now
    propagated the ACTUAL number of cycles between ``origin_cycle`` and the first
    requested point, and between consecutive requested points -- NOT once per
    requested array element. This makes the marginal distribution of a given
    target cycle independent of which OTHER cycles are also requested (previously,
    requesting ``[10]`` alone vs. ``[1,...,10]`` gave two different answers for the
    same cycle 10). ``origin_cycle`` and every entry of ``future_cycle_indices``
    must be (numerically) integers, strictly increasing, and strictly greater than
    ``origin_cycle`` -- the AR(1) recursion is inherently a discrete-cycle process.

    If ``fit.ar1_phi`` is set, the residual propagates as an AR(1) process seeded
    from ``origin_residual`` (the last observed residual at ``origin_cycle``, or
    0.0 if unknown), using ``fit.innovation_std`` (NOT ``fit.residual_std`` -- see
    finding R1) and the exact ``d``-step conditional mean/variance
    (``phi**d * r``, ``innovation_std**2 * sum_{k=0}^{d-1} phi**(2k)``); otherwise
    each future residual is drawn independently with ``fit.residual_std``. Returns
    an array of shape ``(n_samples, len(future_cycle_indices))`` of MODEL-DOMAIN
    capacity values (may be negative -- see ``mean_capacity`` docstring; callers
    must treat negative values as a scope violation of the physical model, not a
    valid physical forecast).
    """
    future_n = np.asarray(future_cycle_indices, dtype=float)
    if len(future_n) == 0:
        raise ScopeViolationError("future_cycle_indices must be non-empty")
    if not np.all(np.isfinite(future_n)) or not np.isfinite(origin_cycle):
        raise ScopeViolationError("origin_cycle and future_cycle_indices must be finite")
    all_cycles = np.concatenate(([float(origin_cycle)], future_n))
    if np.any(np.diff(all_cycles) <= 0.0):
        raise ScopeViolationError("future_cycle_indices must be strictly increasing and > origin_cycle")
    if np.any(np.abs(all_cycles - np.round(all_cycles)) > 1e-9):
        raise ScopeViolationError("origin_cycle and future_cycle_indices must be (numerically) integers")

    means = mean_capacity(fit.model_spec, fit.params, future_n)

    if fit.ar1_phi is None:
        samples = np.empty((n_samples, len(future_n)))
        for i in range(n_samples):
            samples[i] = means + rng.normal(0.0, fit.residual_std, size=len(future_n))
        return samples

    phi = fit.ar1_phi
    innovation_var = float(fit.innovation_std) ** 2 if fit.innovation_std else 0.0
    gaps = np.round(np.diff(all_cycles)).astype(int)
    r_current = np.full(n_samples, float(origin_residual) if origin_residual is not None else 0.0)
    path = np.empty((n_samples, len(future_n)))
    for j, d in enumerate(gaps):
        mean_cont = (phi ** d) * r_current
        if phi == 0.0:
            var_cont = innovation_var if d > 0 else 0.0
        else:
            var_cont = innovation_var * (1.0 - phi ** (2 * d)) / (1.0 - phi ** 2)
        noise = rng.normal(0.0, np.sqrt(var_cont), size=n_samples) if var_cont > 0.0 else 0.0
        r_current = mean_cont + noise
        path[:, j] = r_current
    return means[np.newaxis, :] + path


def first_mean_eol_crossing(fit: CapacityTrendFit, c_eol: float, max_cycles: float) -> Optional[float]:
    """The predicted MEAN model's crossing point of ``c_eol`` -- explicitly NOT the
    same as the first OBSERVED crossing (plan section 11.3): this is a property of
    the fitted mean curve alone. Returns ``None`` if the mean curve does not cross
    within ``[0, max_cycles]``.

    **Correction (SCF_Review_fcc9a43.md, finding R4b):** the mean curve at ``n=0``
    is now checked FIRST for every model, not just persistence/degenerate-``a``
    cases. Previously, a linear or power fit whose value at ``n=0`` was ALREADY
    at or below ``c_eol`` (e.g. ``C0=1, a=0.1`` against ``c_eol=1.4``: the crossing
    condition ``C0 - a*n <= c_eol`` holds at ``n=0`` and would require solving for
    a NEGATIVE ``n_star``, which the old code then rejected as "no crossing")
    returned ``None`` instead of the correct ``0.0`` -- misreporting an
    already-past-EOL mean curve as never reaching EOL at all.
    """
    if c_eol != c_eol or max_cycles != max_cycles:  # NaN check without importing math/numpy scalar checks
        raise ScopeViolationError(f"c_eol and max_cycles must be finite; got c_eol={c_eol!r}, max_cycles={max_cycles!r}")
    if max_cycles < 0.0:
        raise ScopeViolationError(f"max_cycles must be >= 0; got {max_cycles!r}")

    if fit.model_spec == MODEL_PERSISTENCE:
        return 0.0 if fit.params["last_value"] <= c_eol else None
    if fit.model_spec == MODEL_LINEAR:
        if fit.params["C0"] <= c_eol:
            return 0.0
        a = fit.params["a"]
        if a <= 0.0:
            return None  # C0 > c_eol and mean never decreases: never crosses
        n_star = (fit.params["C0"] - c_eol) / a
        return float(n_star) if n_star <= max_cycles else None
    if fit.model_spec == MODEL_POWER:
        a, p, c0 = fit.params["a"], fit.params["p"], fit.params["C0"]
        if c0 <= c_eol:
            return 0.0
        if a <= 0.0:
            return None  # C0 > c_eol and mean never decreases: never crosses
        rhs = (c0 - c_eol) / a
        n_star = rhs ** (1.0 / p)
        return float(n_star) if n_star <= max_cycles else None
    raise ScopeViolationError(f"unknown model_spec: {fit.model_spec!r}")


__all__ = [
    "MODEL_PERSISTENCE", "MODEL_LINEAR", "MODEL_POWER",
    "mean_capacity", "CapacityTrendFit", "fit_capacity_trend",
    "predict_capacity_distribution", "first_mean_eol_crossing",
]
