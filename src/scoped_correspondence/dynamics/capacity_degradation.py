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

    def to_dict(self) -> Dict[str, Any]:
        return {
            "model_spec": self.model_spec, "params": dict(self.params), "residual_std": self.residual_std,
            "ar1_phi": self.ar1_phi, "n_train": len(self.train_cycles),
        }


def _fit_ar1(residuals: np.ndarray) -> Optional[float]:
    """OLS estimate of phi in r[n+1] = phi*r[n] + eps[n], clipped to (-1, 1)."""
    if len(residuals) < 3:
        return None
    x, y = residuals[:-1], residuals[1:]
    denom = float(np.sum(x * x))
    if denom <= 1e-12:
        return 0.0
    phi = float(np.sum(x * y) / denom)
    return float(np.clip(phi, -0.999, 0.999))


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
    ar1_phi = _fit_ar1(residuals) if fit_ar1 else None

    return CapacityTrendFit(
        model_spec=model_spec, params=params, residual_std=residual_std, ar1_phi=ar1_phi,
        train_cycles=tuple(cycles), train_capacity=tuple(cap),
    )


def predict_capacity_distribution(
    fit: CapacityTrendFit, origin_state: Optional[float], future_cycle_indices: Sequence[float],
    rng: np.random.Generator, n_samples: int = 1000,
) -> np.ndarray:
    """Simulate ``n_samples`` capacity trajectories over ``future_cycle_indices``.

    If ``fit.ar1_phi`` is set, residuals propagate as an AR(1) process seeded from
    ``origin_state`` (the last observed residual at the forecast origin, or 0.0 if
    unknown); otherwise each future residual is drawn independently. Returns an
    array of shape ``(n_samples, len(future_cycle_indices))`` of MODEL-DOMAIN
    capacity values (may be negative -- see ``mean_capacity`` docstring; callers
    must treat negative values as a scope violation of the physical model, not a
    valid physical forecast).
    """
    future_n = np.asarray(future_cycle_indices, dtype=float)
    means = mean_capacity(fit.model_spec, fit.params, future_n)
    samples = np.empty((n_samples, len(future_n)))
    for i in range(n_samples):
        if fit.ar1_phi is not None:
            r = float(origin_state) if origin_state is not None else 0.0
            path = np.empty(len(future_n))
            for j in range(len(future_n)):
                r = fit.ar1_phi * r + rng.normal(0.0, fit.residual_std)
                path[j] = r
            samples[i] = means + path
        else:
            samples[i] = means + rng.normal(0.0, fit.residual_std, size=len(future_n))
    return samples


def first_mean_eol_crossing(fit: CapacityTrendFit, c_eol: float, max_cycles: float) -> Optional[float]:
    """The predicted MEAN model's crossing point of ``c_eol`` -- explicitly NOT the
    same as the first OBSERVED crossing (plan section 11.3): this is a property of
    the fitted mean curve alone. Returns ``None`` if the mean curve does not cross
    within ``[0, max_cycles]``.
    """
    if fit.model_spec == MODEL_PERSISTENCE:
        return 0.0 if fit.params["last_value"] <= c_eol else None
    if fit.model_spec == MODEL_LINEAR:
        a = fit.params["a"]
        if a <= 0.0:
            return 0.0 if fit.params["C0"] <= c_eol else None
        n_star = (fit.params["C0"] - c_eol) / a
        return float(n_star) if 0.0 <= n_star <= max_cycles else None
    if fit.model_spec == MODEL_POWER:
        a, p, c0 = fit.params["a"], fit.params["p"], fit.params["C0"]
        if a <= 0.0:
            return 0.0 if c0 <= c_eol else None
        rhs = (c0 - c_eol) / a
        if rhs < 0.0:
            return None  # C0 - a*n^p never reaches c_eol from above for n>=0
        n_star = rhs ** (1.0 / p)
        return float(n_star) if 0.0 <= n_star <= max_cycles else None
    raise ScopeViolationError(f"unknown model_spec: {fit.model_spec!r}")


__all__ = [
    "MODEL_PERSISTENCE", "MODEL_LINEAR", "MODEL_POWER",
    "mean_capacity", "CapacityTrendFit", "fit_capacity_trend",
    "predict_capacity_distribution", "first_mean_eol_crossing",
]
