"""Profile likelihood for models with MORE THAN ONE free parameter (Milestone 47).

MECHANISTIC_VALIDATION_ROADMAP.md package 1, response to
prompts/Answers/nicht_stationäre_Treiber/SCF_Review_f8e249f.md (Astra,
2026-09-21): "explizite Prüfung ... anschließend Anschluss an die
vorhandenen Profile-Likelihood- und Identifizierbarkeitsmodule."

``identifiability/profile_likelihood.py`` (Milestone 20) is intentionally
restricted to ALGEBRAIC chi2 demos with AT MOST ONE free parameter (a 1-D
golden-section/grid refine) -- its own docstring explicitly disclaims
calling ODE integrators or a general NLP solver. Real fitted models like
``dynamics.energy_balance``'s 5-parameter calibration need the full Raue
et al. 2009 procedure: at each fixed value of the profiled parameter,
RE-OPTIMIZE every other ("free") parameter via a general nonlinear solver.

M20's ``profile_likelihood.py`` is used, NOT edited: ``classify_identifiability``
and ``likelihood_interval`` both operate on a generic ``Profile`` (a list of
``(fixed_value, chi2_min)`` pairs), independent of how ``chi2_min`` was
computed -- they are imported and reused here directly. Only
``profile_parameter``'s hard 1-free-parameter restriction is worked around,
via a new function that has no such restriction (any number of free
parameters), at the cost of relying on a real bounded nonlinear
least-squares solver rather than an exact 1-D search.
"""

from __future__ import annotations

from typing import Callable, List, Sequence, Tuple

import numpy as np
from scipy.optimize import least_squares

from scoped_correspondence.errors import ScopeViolationError
from scoped_correspondence.identifiability.profile_likelihood import (
    SOURCE as PROFILE_LIKELIHOOD_SOURCE,
    Profile,
)

SOURCE = PROFILE_LIKELIHOOD_SOURCE  # same Raue et al. 2009 method, generalized to p>2


def profile_parameter_nlp(
    residual_fn: Callable[[np.ndarray], np.ndarray],
    theta_init: Sequence[float],
    fixed_index: int,
    fixed_values: Sequence[float],
    bounds: Tuple[Sequence[float], Sequence[float]],
) -> Profile:
    """Profile one parameter of a general bounded nonlinear least-squares model.

    At each ``fixed_value``, re-optimizes ALL OTHER parameters (bounded
    ``scipy.optimize.least_squares``) to minimize
    ``chi2 = sum(residual_fn(theta)**2)``, holding
    ``theta[fixed_index] = fixed_value``. Warm-starts each grid point from
    the previous one's solution (helps convergence along a smooth scan).

    Returns the same ``Profile`` type as
    ``identifiability.profile_likelihood.profile_parameter`` --
    ``classify_identifiability``/``likelihood_interval`` from that module
    can be applied to the result unchanged.
    """
    if not callable(residual_fn):
        raise ScopeViolationError("profile_parameter_nlp: residual_fn must be callable")
    theta0 = np.asarray(theta_init, dtype=float)
    p = len(theta0)
    if fixed_index < 0 or fixed_index >= p:
        raise ScopeViolationError(f"profile_parameter_nlp: fixed_index={fixed_index!r} out of range for p={p}")
    if len(fixed_values) < 2:
        raise ScopeViolationError("profile_parameter_nlp: need >= 2 fixed_values")
    lb = np.asarray(bounds[0], dtype=float)
    ub = np.asarray(bounds[1], dtype=float)
    if len(lb) != p or len(ub) != p:
        raise ScopeViolationError("profile_parameter_nlp: bounds must match theta length")

    free_idx = [j for j in range(p) if j != fixed_index]
    out: List[Tuple[float, float]] = []
    theta_current = theta0.copy()

    for raw in fixed_values:
        fv = float(raw)
        if not np.isfinite(fv):
            raise ScopeViolationError(f"profile_parameter_nlp: fixed_values must be finite; got {raw!r}")

        def resid_free(free_vals: np.ndarray, fv: float = fv) -> np.ndarray:
            theta = theta_current.copy()
            theta[fixed_index] = fv
            for k, j in enumerate(free_idx):
                theta[j] = free_vals[k]
            return residual_fn(theta)

        if free_idx:
            x0_free = theta_current[free_idx]
            lb_free = lb[free_idx]
            ub_free = ub[free_idx]
            res = least_squares(
                resid_free, x0_free, bounds=(lb_free, ub_free), xtol=1e-12, ftol=1e-12, gtol=1e-12, max_nfev=2000
            )
            chi2_min = float(np.sum(res.fun**2))
            theta_current[fixed_index] = fv
            for k, j in enumerate(free_idx):
                theta_current[j] = res.x[k]
        else:
            theta_current[fixed_index] = fv
            chi2_min = float(np.sum(residual_fn(theta_current) ** 2))

        out.append((fv, chi2_min))

    return out


__all__ = ["SOURCE", "profile_parameter_nlp"]
