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
and are decided RIGOROUSLY from the matrix's eigenvalues where possible
(not just from a finite simulation window, which can never itself prove a
system returns):

- ``no_violation_in_horizon`` — stable, and the trajectory never crosses
  the boundary WITHIN THE GIVEN TIME WINDOW ``[0, t_max]`` (possibly after
  a large but sub-threshold excursion). This is explicitly a
  horizon-relative statement, not a permanent safety guarantee: stability
  only guarantees eventual return to the origin, not that no excursion
  beyond the boundary can occur at some later time outside the checked
  window (a short ``t_max`` can hide a violation that would appear at a
  slightly longer horizon — see
  ``verify_transient_amplification.py``'s
  ``short_horizon_hides_a_later_violation`` check).
- ``transient_violation`` — stable (all eigenvalue real parts < 0, so
  return to the origin is GUARANTEED analytically), and the trajectory
  does cross the boundary at some finite time WITHIN the checked window.
- ``unstable_not_yet_violated`` / ``unstable_violation_no_guaranteed_return``
  — at least one eigenvalue has non-negative real part, so eventual return
  is NOT guaranteed; a boundary crossing here is a genuine candidate for a
  permanent attractor change, not merely a transient excursion (whether or
  not it has already crossed within the simulated horizon).

**Correction (2026-09-24, response to
prompts/Answers/nicht_stationäre_Treiber/SCF_Review_dc5d82a.md, Astra
finding R3):** the peak-finding used to call ``scipy.optimize
.minimize_scalar(method="bounded")`` once over the WHOLE window — a
LOCAL, single-bracket optimizer, unsound for an oscillating trajectory
with many local extrema (Astra's counterexample: a rotating stable system,
``A=[[-0.1,-10],[10,-0.1]]``, where the true global peak
``|x1|≈0.9845`` at ``t≈0.156`` was missed entirely in favor of a
spurious local extremum ``0.525`` found near ``t≈6.4`` — even the raw
SAMPLED trajectory already contained a point exceeding the reported
boundary that the old code never compared against). Fixed by (1)
automatically increasing the sample count to resolve the fastest
oscillation frequency implied by the matrix's eigenvalues
(``_adequate_sample_count``), and (2) replacing the single local
optimization with the TRUE global extremum of the resulting cubic-spline
interpolant: every stationary point of the spline is found ANALYTICALLY
via ``CubicSpline.derivative().roots()`` (exact for a piecewise cubic, not
an iterative bracket search) and compared against the two endpoints —
between any two such points a cubic spline is strictly monotonic, so this
set of candidates is provably sufficient for the interpolant's global
extremum. The remaining, distinct source of error (how well the spline
interpolant approximates the true continuous trajectory) is bounded by
the adaptive resolution but not separately quantified here.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Tuple

import numpy as np
from scipy.interpolate import CubicSpline
from scipy.linalg import expm
from scipy.linalg import norm as matrix_norm

from scoped_correspondence.errors import ScopeViolationError

SOURCE = (
    "Trefethen, L. N.; Trefethen, A. E.; Reddy, S. C.; Driscoll, T. A. "
    "(1993): Hydrodynamic Stability Without Eigenvalues. Science 261, "
    "578-584."
)

NO_VIOLATION_IN_HORIZON = "no_violation_in_horizon"
TRANSIENT_VIOLATION = "transient_violation"
UNSTABLE_NOT_YET_VIOLATED = "unstable_not_yet_violated"
UNSTABLE_VIOLATION = "unstable_violation_no_guaranteed_return"

MIN_POINTS_PER_OSCILLATION_PERIOD = 40


def _adequate_sample_count(eigvals: np.ndarray, t_max: float, n_points: int, safety_factor: int = 1) -> int:
    """Raise ``n_points`` if needed so the fastest oscillation implied by ``eigvals``
    (largest ``|Im(eigenvalue)|``) gets at least
    :data:`MIN_POINTS_PER_OSCILLATION_PERIOD` samples per period over ``[0, t_max]``.
    Real (non-oscillating) eigenvalues leave ``n_points`` unchanged. ``safety_factor``
    multiplies the requirement (use ``2`` for quantities like a matrix NORM, which can
    complete a full up-down cycle twice as fast as the underlying trajectory itself).
    """
    max_imag = float(np.max(np.abs(eigvals.imag))) if len(eigvals) else 0.0
    if max_imag <= 1e-12:
        return int(n_points)
    period = 2.0 * np.pi / max_imag
    needed = int(np.ceil((float(t_max) / period) * MIN_POINTS_PER_OSCILLATION_PERIOD * int(safety_factor))) + 1
    return max(int(n_points), needed)


def _spline_global_extremum(t: np.ndarray, y: np.ndarray, *, absolute: bool = False) -> Tuple[float, float]:
    """Global extremum of the cubic-spline interpolant through ``(t, y)``.

    Finds EVERY stationary point of the spline analytically
    (``CubicSpline.derivative().roots()``) plus the two endpoints, and
    returns whichever candidate maximizes ``y`` (or ``|y|`` if
    ``absolute``) — provably sufficient for a piecewise-cubic
    interpolant's global extremum (see module docstring). NOT a claim
    about the true underlying continuous function beyond the interpolant's
    own approximation error.
    """
    spline = CubicSpline(t, y)
    deriv = spline.derivative()
    roots = deriv.roots(extrapolate=False)
    roots = roots[(roots >= t[0]) & (roots <= t[-1])]
    candidates = np.concatenate(([t[0], t[-1]], roots))
    values = spline(candidates)
    key = np.abs(values) if absolute else values
    idx = int(np.argmax(key))
    return float(candidates[idx]), float(values[idx])


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


def max_finite_time_gain(A: Any, t_max: float, norm_ord: int = 2, n_points: int = 200) -> Tuple[float, float]:
    """``argmax`` and max of ``||e^{At}||`` over ``t in [0, t_max]``.

    **Correction (2026-09-24, Astra finding R3):** previously used a single
    ``scipy.optimize.minimize_scalar(method="bounded")`` call over the
    whole window — a LOCAL bracket search, unsound for a gain curve that
    can oscillate (e.g. a matrix with complex eigenvalues). Now samples the
    gain curve at a resolution that automatically increases with the
    matrix's fastest oscillation frequency (``_adequate_sample_count``,
    with an extra safety factor since a norm/magnitude quantity can
    complete an up-down cycle twice as fast as the underlying trajectory),
    then finds the cubic-spline interpolant's TRUE global extremum
    analytically (``_spline_global_extremum``) rather than trusting a
    single local search.
    """
    if t_max <= 0.0:
        raise ScopeViolationError(f"max_finite_time_gain: t_max must be > 0; got {t_max!r}")
    A_mat = np.asarray(A, dtype=float)
    eigvals = np.linalg.eigvals(A_mat)
    n = _adequate_sample_count(eigvals, float(t_max), n_points, safety_factor=2)
    t = np.linspace(0.0, float(t_max), n)
    gains = np.array([finite_time_gain(A_mat, tt, norm_ord=norm_ord) for tt in t])
    t_star, peak = _spline_global_extremum(t, gains)
    return t_star, peak


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

    n_adequate = _adequate_sample_count(eigvals, float(t_max), int(n_points))
    t = np.linspace(0.0, float(t_max), n_adequate)
    traj = np.array([expm(A_mat * tt) @ x0_vec for tt in t])
    x1, x2 = traj[:, 0], traj[:, 1]

    peak_time, peak_value = _spline_global_extremum(t, x1, absolute=True)
    exceeds = abs(peak_value) > float(boundary)

    if is_stable:
        classification = TRANSIENT_VIOLATION if exceeds else NO_VIOLATION_IN_HORIZON
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
    "NO_VIOLATION_IN_HORIZON", "TRANSIENT_VIOLATION", "UNSTABLE_NOT_YET_VIOLATED", "UNSTABLE_VIOLATION",
    "TwoBufferTransientReport",
    "canonical_triangular_matrix", "canonical_matrix_exponential_closed_form",
    "finite_time_gain", "max_finite_time_gain",
    "classify_two_buffer_transient",
]
