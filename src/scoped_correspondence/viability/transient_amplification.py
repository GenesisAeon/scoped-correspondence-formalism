"""Transient amplification via non-normal coupling (Milestone 58).

CAPABILITY_EXPANSION_ROADMAP.md Priority 4, response to Astra's 2026-09-24
capability assessment — her own "most interesting new mathematical
direction": **non-normal dynamics and transient amplification** (Trefethen,
Trefethen, Reddy & Driscoll 1993, Science 261, "Hydrodynamic Stability
Without Eigenvalues").

The canonical example: for

    A = [[-1, k], [0, -1]],    e^{At} = e^{-t} * [[1, k*t], [0, 1]]

BOTH eigenvalues are -1 (strictly stable — the system provably decays to
the origin). Yet for large enough ``k``, a perturbation entering through
the second (hidden/coupled) coordinate can be transiently AMPLIFIED by a
large factor before the guaranteed decay takes over. A dangerous
transition therefore does not require an unstable eigenvalue, and does not
require an exponentially growing external driver — coupling alone can
temporarily amplify an existing disturbance. This connects directly to
this repository's coupling/contraction/viability modules and offers an
additional explanation for the kind of tipping this repository's earlier
work (``dynamics/rate_dependent.py``) originally set out to study.

Three distinct outcomes, per Astra's explicit request, are kept separate
and are decided RIGOROUSLY from the matrix's eigenvalues (not just from a
finite simulation window, which can never itself prove a system returns):

- ``safe_no_violation`` — stable, and the trajectory never crosses the
  boundary (possibly after a large but sub-threshold excursion).
- ``transient_violation`` — stable (all eigenvalue real parts < 0, so
  return to the origin is GUARANTEED analytically), and the trajectory
  does cross the boundary at some finite time.
- ``unstable_not_yet_violated`` / ``unstable_violation_no_guaranteed_return``
  — at least one eigenvalue has non-negative real part, so eventual return
  is NOT guaranteed; a boundary crossing here is a genuine candidate for a
  permanent attractor change, not merely a transient excursion (whether or
  not it has already crossed within the simulated horizon).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Tuple

import numpy as np
from scipy.interpolate import CubicSpline
from scipy.linalg import expm
from scipy.linalg import norm as matrix_norm
from scipy.optimize import minimize_scalar

from scoped_correspondence.errors import ScopeViolationError

SOURCE = (
    "Trefethen, L. N.; Trefethen, A. E.; Reddy, S. C.; Driscoll, T. A. "
    "(1993): Hydrodynamic Stability Without Eigenvalues. Science 261, "
    "578-584."
)

SAFE_NO_VIOLATION = "safe_no_violation"
TRANSIENT_VIOLATION = "transient_violation"
UNSTABLE_NOT_YET_VIOLATED = "unstable_not_yet_violated"
UNSTABLE_VIOLATION = "unstable_violation_no_guaranteed_return"


def canonical_triangular_matrix(k: float) -> np.ndarray:
    """Trefethen et al.'s canonical example: ``A = [[-1, k], [0, -1]]``."""
    return np.array([[-1.0, float(k)], [0.0, -1.0]])


def canonical_matrix_exponential_closed_form(k: float, t: float) -> np.ndarray:
    """Closed form ``e^{At} = e^{-t} * [[1, k*t], [0, 1]]`` for the canonical example."""
    if t < 0.0:
        raise ScopeViolationError(f"canonical_matrix_exponential_closed_form: t must be >= 0; got {t!r}")
    return np.exp(-t) * np.array([[1.0, float(k) * t], [0.0, 1.0]])


def finite_time_gain(A: Any, t: float, norm_ord: int = 2) -> float:
    """``||e^{At}||`` (operator norm, default spectral/2-norm) at a single time ``t``."""
    if t < 0.0:
        raise ScopeViolationError(f"finite_time_gain: t must be >= 0; got {t!r}")
    M = expm(np.asarray(A, dtype=float) * float(t))
    return float(matrix_norm(M, ord=norm_ord))


def max_finite_time_gain(A: Any, t_max: float, norm_ord: int = 2) -> Tuple[float, float]:
    """``argmax`` and max of ``||e^{At}||`` over ``t in [0, t_max]`` via CONTINUOUS
    bounded optimization (``scipy.optimize.minimize_scalar``), not a grid search.
    """
    if t_max <= 0.0:
        raise ScopeViolationError(f"max_finite_time_gain: t_max must be > 0; got {t_max!r}")

    def neg_gain(t: float) -> float:
        return -finite_time_gain(A, t, norm_ord=norm_ord)

    res = minimize_scalar(neg_gain, bounds=(0.0, float(t_max)), method="bounded")
    if not res.success:
        raise ScopeViolationError(f"max_finite_time_gain: optimization failed: {res.message}")
    return float(res.x), float(-res.fun)


@dataclass(frozen=True)
class TwoBufferTransientReport:
    t: Tuple[float, ...]
    x1: Tuple[float, ...]
    x2: Tuple[float, ...]
    eigenvalues: Tuple[complex, ...]
    max_eigenvalue_real_part: float
    is_asymptotically_stable: bool
    boundary: float
    peak_abs_x1_time: float
    peak_abs_x1_value: float
    exceeds_boundary: bool
    classification: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "t": list(self.t), "x1": list(self.x1), "x2": list(self.x2),
            "eigenvalues": [str(v) for v in self.eigenvalues],
            "max_eigenvalue_real_part": self.max_eigenvalue_real_part,
            "is_asymptotically_stable": self.is_asymptotically_stable,
            "boundary": self.boundary,
            "peak_abs_x1_time": self.peak_abs_x1_time,
            "peak_abs_x1_value": self.peak_abs_x1_value,
            "exceeds_boundary": self.exceeds_boundary,
            "classification": self.classification,
        }


def classify_two_buffer_transient(
    A: Any, x0: Any, t_max: float, boundary: float, n_points: int = 400
) -> TwoBufferTransientReport:
    """Simulate the coupled linear 2-buffer system ``dx/dt = A x`` from ``x0``,
    classify whether ``x1`` (the first component) transiently or permanently
    crosses ``boundary`` — see module docstring for the 4-way classification.
    """
    A_mat = np.asarray(A, dtype=float)
    if A_mat.shape != (2, 2):
        raise ScopeViolationError(f"classify_two_buffer_transient: A must be 2x2; got shape {A_mat.shape}")
    x0_vec = np.asarray(x0, dtype=float)
    if x0_vec.shape != (2,):
        raise ScopeViolationError(f"classify_two_buffer_transient: x0 must have shape (2,); got {x0_vec.shape}")
    if t_max <= 0.0:
        raise ScopeViolationError(f"classify_two_buffer_transient: t_max must be > 0; got {t_max!r}")
    if boundary <= 0.0:
        raise ScopeViolationError(f"classify_two_buffer_transient: boundary must be > 0 (a magnitude); got {boundary!r}")
    if n_points < 10:
        raise ScopeViolationError(f"classify_two_buffer_transient: n_points must be >= 10; got {n_points!r}")

    eigvals = np.linalg.eigvals(A_mat)
    max_real = float(np.max(eigvals.real))
    is_stable = max_real < 0.0

    t = np.linspace(0.0, float(t_max), int(n_points))
    traj = np.array([expm(A_mat * tt) @ x0_vec for tt in t])
    x1, x2 = traj[:, 0], traj[:, 1]

    spline = CubicSpline(t, x1)
    res = minimize_scalar(lambda tt: -abs(float(spline(tt))), bounds=(float(t[0]), float(t[-1])), method="bounded")
    peak_time = float(res.x)
    peak_value = float(spline(peak_time))
    exceeds = abs(peak_value) > float(boundary)

    if is_stable:
        classification = TRANSIENT_VIOLATION if exceeds else SAFE_NO_VIOLATION
    else:
        classification = UNSTABLE_VIOLATION if exceeds else UNSTABLE_NOT_YET_VIOLATED

    return TwoBufferTransientReport(
        t=tuple(float(v) for v in t), x1=tuple(float(v) for v in x1), x2=tuple(float(v) for v in x2),
        eigenvalues=tuple(complex(v) for v in eigvals), max_eigenvalue_real_part=max_real,
        is_asymptotically_stable=is_stable, boundary=float(boundary),
        peak_abs_x1_time=peak_time, peak_abs_x1_value=peak_value,
        exceeds_boundary=exceeds, classification=classification,
    )


__all__ = [
    "SOURCE",
    "SAFE_NO_VIOLATION", "TRANSIENT_VIOLATION", "UNSTABLE_NOT_YET_VIOLATED", "UNSTABLE_VIOLATION",
    "TwoBufferTransientReport",
    "canonical_triangular_matrix", "canonical_matrix_exponential_closed_form",
    "finite_time_gain", "max_finite_time_gain",
    "classify_two_buffer_transient",
]
