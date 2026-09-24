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

**Correction (2026-09-24, response to
prompts/Answers/nicht_stationäre_Treiber/Astra6.txt, finding 1): the
above fix still missed fast, NON-oscillating spikes.** ``_adequate_sample
_count`` only looked at eigenvalues' IMAGINARY parts; a large negative
REAL part (fast decay, no oscillation at all) never triggered extra
resolution. Astra's counterexample: an accelerated canonical matrix,
``A=[[-100,1000],[0,-100]]``, ``x0=[0,1]`` — exactly ``x1(t) =
1000*t*e^{-100t}``, true peak ``e^{-1}*10 ≈ 3.67879`` at ``t=0.01``. With
the default 400-point grid over ``t_max=10``, the spacing (0.025) is far
coarser than the decay time constant (0.01), so the spike falls entirely
inside the FIRST grid cell and even the spline interpolant never sees it
(reported peak was 2.159, classification wrongly ``no_violation_in_horizon``
even though the boundary 3.0 is genuinely exceeded; ``max_finite_time_gain``
reported 1.0 instead of >3.7 for the same reason). Fixed two ways: (1)
``_adequate_sample_count`` now also resolves the fastest REAL decay/growth
rate, not just oscillation, fixing ``max_finite_time_gain`` and the
reported trajectory's fidelity; (2) far more importantly,
``classify_two_buffer_transient``'s peak search no longer depends on
sampling density AT ALL — every component of the homogeneous 2x2 system
``dx/dt = A x`` satisfies the SAME scalar 2nd-order constant-coefficient
ODE given by ``A``'s characteristic polynomial (``x'' - tr(A) x' +
det(A) x = 0``), which has an exact closed form and exact interior
stationary points in all three cases (real-distinct roots, repeated
real root, complex-conjugate roots) — computed by
``_analytic_component_critical_times`` and compared against the two
endpoints via the EXACT (``expm``) trajectory value, not an interpolant.

**Correction (2026-09-24, response to
prompts/Answers/nicht_stationäre_Treiber/SCF_DOMAIN_EXPANSION_IMPLEMENTATION_PLAN.md,
Paket B0): the branch selection in ``_analytic_component_critical_times``
was itself unit-dependent.** It compared the discriminant ``D = tr(A)^2 -
4*det(A)`` against an ABSOLUTE threshold ``±1e-9``. Under a pure time-unit
rescaling ``A -> c*A``, ``t_max -> t_max/c`` (the trajectory is identical,
just relabeled in time: ``x_new(s) = x_old(c*s)``), ``D`` itself scales as
``c^2`` and can be pushed arbitrarily close to (but not at) an absolute
zero threshold purely by choice of units, even though the SYSTEM is
nowhere near a repeated-eigenvalue degeneracy. Astra's counterexample:
``A=[[-0.1,-10],[10,-0.1]]``, ``x0=[0,1]``, ``H=10``, boundary ``0.95``
(complex-conjugate case, ``D=-400``, true global peak
``|x1(t*)|=|sin|`` term at ``t*=arctan(100)/10≈0.15607966601082315``,
value ``≈0.9844639845000666`` — correctly found by the code as-is: peak
``0.9844639845000663``, classification ``transient_violation``). Rescaled
by ``c=1e-6`` (``A_new=c*A``, ``H_new=H/c=1e7``, same ``x0``, same
boundary — an EXACT time relabeling of the identical trajectory, so the
peak height and classification must be unchanged and the peak time must
scale by ``1/c``): ``D_new = c^2*D = -4.0000e-10``, which fails BOTH
``D_new < -1e-9`` and ``D_new > 1e-9`` under the old absolute test, so the
code incorrectly fell into the repeated-root branch, found no interior
critical point, and reported the horizon endpoint as the peak (``0.186``
at ``t=1e7``) — wrongly classified ``no_violation_in_horizon``. Fixed by
comparing a SCALE-INVARIANT relative discriminant ``D / scale`` against a
dimensionless ``1e-9``, where ``scale = max(tr(A)^2, 4*|det(A)|)``: under
``A -> c*A``, both ``D`` and ``scale`` scale as ``c^2``, so their ratio is
exactly invariant, and the branch selected is now a genuine property of
the matrix's SHAPE, not its units. ``scale == 0`` (forces ``D == 0`` too,
e.g. the zero matrix or any nilpotent ``A``) is routed directly to the
repeated-root branch. Verified for ``c in {1e-6, 1, 1e6}`` — see
``verify_transient_amplification.py``'s
``astra_b0_scale_invariant_discriminant_classification`` check.
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

# Dimensionless: compared against D/scale (see _analytic_component_critical_times),
# not against D directly -- makes the branch choice invariant under A -> c*A.
_REL_DISCRIMINANT_EPS = 1e-9


def _adequate_sample_count(eigvals: np.ndarray, t_max: float, n_points: int, safety_factor: int = 1) -> int:
    """Raise ``n_points`` if needed so the fastest TIMESCALE implied by ``eigvals`` —
    oscillation (``|Im|``) OR fast decay/growth (``|Re|``) — gets at least
    :data:`MIN_POINTS_PER_OSCILLATION_PERIOD` samples per characteristic time over
    ``[0, t_max]``. **Correction (2026-09-24, Astra6.txt finding 1):** previously only
    considered ``|Im(eigenvalue)|``, so a large negative real part (fast decay, no
    oscillation) never triggered extra resolution — a fast spike could fall entirely
    inside one grid cell and be missed even by the spline-based global extremum search.
    ``safety_factor`` multiplies the requirement (use ``2`` for quantities like a matrix
    NORM, which can complete a full up-down cycle twice as fast as the trajectory itself).
    """
    if len(eigvals) == 0:
        return int(n_points)
    rates = np.maximum(np.abs(eigvals.real), np.abs(eigvals.imag))
    max_rate = float(np.max(rates))
    if max_rate <= 1e-12:
        return int(n_points)
    characteristic_time = 1.0 / max_rate
    needed = int(np.ceil((float(t_max) / characteristic_time) * MIN_POINTS_PER_OSCILLATION_PERIOD * int(safety_factor))) + 1
    return max(int(n_points), needed)


def _analytic_component_critical_times(A: np.ndarray, x0: np.ndarray, component: int, t_max: float) -> list[float]:
    """EXACT interior stationary points (``0 < t < t_max``) of ``x_component(t)`` for the
    homogeneous linear system ``dx/dt = A x``, ``x(0) = x0`` (2x2 ``A``).

    Every component of a 2-state linear system satisfies the SAME scalar 2nd-order
    constant-coefficient ODE given by ``A``'s characteristic polynomial:

        x'' - tr(A)*x' + det(A)*x = 0,   x(0) = x0[component], x'(0) = (A@x0)[component]

    Solved exactly per the sign of the discriminant ``D = tr(A)^2 - 4*det(A)``
    (real-distinct / repeated / complex-conjugate roots) — exact and robust, with no
    eigenvector computation or degeneracy handling needed. This is what makes the peak
    search for these 2x2 systems independent of any sampling density (Astra6.txt finding 1).
    """
    y0 = float(x0[component])
    y0dot = float((A @ x0)[component])
    tr = float(np.trace(A))
    det = float(np.linalg.det(A))
    D = tr * tr - 4.0 * det
    # Scale-invariant branch test (Astra's Paket B0 finding): D itself scales as c^2
    # under A -> c*A, so comparing it to an ABSOLUTE epsilon lets pure unit choice flip
    # the branch. `scale` scales the same way (c^2), so D/scale is exactly invariant.
    scale = max(tr * tr, 4.0 * abs(det))
    rel_D = 0.0 if scale <= 0.0 else D / scale
    candidates: list[float] = []

    if rel_D > _REL_DISCRIMINANT_EPS:
        sqrt_d = float(np.sqrt(D))
        r1 = (tr + sqrt_d) / 2.0
        r2 = (tr - sqrt_d) / 2.0
        # y0 = C1 + C2 ; y0dot = C1*r1 + C2*r2
        c1 = (y0dot - r2 * y0) / (r1 - r2)
        c2 = y0 - c1
        # derivative zero: C1*r1*exp(r1 t) + C2*r2*exp(r2 t) = 0
        num = -(c2 * r2)
        den = c1 * r1
        if abs(den) > 1e-300 and (num / den) > 0.0:
            t_star = float(np.log(num / den) / (r1 - r2))
            if 0.0 < t_star < t_max:
                candidates.append(t_star)
    elif rel_D < -_REL_DISCRIMINANT_EPS:
        alpha = tr / 2.0
        omega = float(np.sqrt(-D)) / 2.0
        c1 = y0
        c2 = (y0dot - alpha * y0) / omega
        # derivative zero: (alpha*C1+omega*C2)*cos(wt) + (alpha*C2-omega*C1)*sin(wt) = 0
        # <=> R*cos(wt - psi) = 0, psi = atan2(Q, P), zero at wt = psi + pi/2 + k*pi
        p_coef = alpha * c1 + omega * c2
        q_coef = alpha * c2 - omega * c1
        psi = float(np.arctan2(q_coef, p_coef))
        theta0 = psi + np.pi / 2.0
        k_lo = int(np.floor((0.0 - theta0) / np.pi)) - 1
        k_hi = int(np.ceil((omega * t_max - theta0) / np.pi)) + 1
        for k in range(k_lo, k_hi + 1):
            t_k = float((theta0 + k * np.pi) / omega)
            if 0.0 < t_k < t_max:
                candidates.append(t_k)
    else:
        r = tr / 2.0
        c1 = y0
        c2 = y0dot - r * y0
        if abs(r) > 1e-300 and abs(c2) > 1e-300:
            t_star = float(-(c2 + r * c1) / (r * c2))
            if 0.0 < t_star < t_max:
                candidates.append(t_star)
    return candidates


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

    The peak search itself is EXACT and independent of ``n_points``: see
    ``_analytic_component_critical_times`` (module docstring, Astra6.txt
    finding 1). ``n_points`` only controls the resolution of the reported
    ``t``/``x1``/``x2`` trajectory arrays for inspection/plotting.
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

    critical_times = _analytic_component_critical_times(A_mat, x0_vec, component=0, t_max=float(t_max))
    candidate_times = [0.0, float(t_max)] + critical_times
    candidate_values = [float((expm(A_mat * ct) @ x0_vec)[0]) for ct in candidate_times]
    best_idx = int(np.argmax(np.abs(candidate_values)))
    peak_time, peak_value = candidate_times[best_idx], candidate_values[best_idx]
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
