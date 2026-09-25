"""Distributed-delay pilot: does spreading a fixed-mean delay over more stages
change when a downstream buffer runs dry (INTEGRATED_EXTENSION_ROADMAP.md
Paket C3, plan section 7's fixed experiment)?

Fixed experiment: an Erlang(n) delay chain with mean dwell time
``tau=1`` for ``n in {1,2,4,8}``, driven by a rectangular input pulse
``u(t)=5`` on ``[0, 0.2)`` then ``0``, feeding a downstream buffer
``R(0)=0.1``, ``dR/dt = 0.4 - y(t)`` (``y`` the chain's output), over horizon
``5``. Event of interest: the first time ``R(t) <= 0``.

**Correction (2026-09-25, response to
prompts/Answers/nicht_stationäre_Treiber/SCF_REVIEW_C0_C7_4ed0cd9.md, finding
R1 -- a real bug, independently reproduced before fixing):** the original
implementation searched a dense (>=500-point) fixed grid per segment for a
sign change in ``R``, then refined with ``brentq``. This finds a bracket's
root exactly but the SEARCH ITSELF is not exhaustive: a narrow enough dip
between two grid points is invisible to it. Astra's exact counterexample
(``n=1``, ``R0=0.19281716266490573``) makes ``R`` dip to ``-1e-7`` at
``t*=1.0179568433377355`` and recover -- narrower than the grid spacing at
that point -- so the old code reported ``first_passage_time=None`` while
SIMULTANEOUSLY reporting a negative ``R_min_value`` at that exact same
time, an internal self-contradiction independently confirmed before this
fix.

**Fix: exact, grid-free event/extremum location**, using the fact that for
an Erlang(n) chain of rate ``k=n/tau`` driven by a CONSTANT input ``u``
(``u=u_pulse`` during the pulse, ``u=0`` after it) starting from a known
stage-occupancy vector ``z0``, the OUTPUT has the closed form

    y(tau) = u + exp(-k*tau) * P(tau)

for a real polynomial ``P`` of degree ``<= n-1`` with coefficients computed
directly from ``z0``, ``k`` and ``u`` (cross-checked to machine precision
against the module's own exact ``propagate_phase_type`` before this fix was
written). Consequently ``y'(tau) = exp(-k*tau) * (P'(tau) - k*P(tau))``, and
the exact stationary points of ``y`` in a segment are exactly the REAL,
IN-RANGE ROOTS of the polynomial ``Q = P' - k*P`` (found via
``numpy.poly1d.roots``, not a sampling grid). Between two consecutive such
points ``y`` is monotone, hence ``R' = inflow - y`` is monotone there too, so
its own (at most one) zero -- an ``R``-stationary point -- is found exactly
via a bracketed ``brentq`` call, never missed. Between two consecutive
``R``-stationary points, ``R`` itself is monotone, so a further bracketed
``brentq`` call finds any ``R=0`` crossing completely and exactly.
``R``'s and ``y``'s global extrema over a segment can then only occur AT one
of these finitely many exactly-located breakpoints (plus the segment's own
endpoints) -- never missed between them, regardless of how narrow a dip is.

**No reflection/clipping** (plan section 7): if ``R`` goes negative, the
simulation keeps running past that point with the SAME linear dynamics --
the buffer's value at the horizon is reported even if deeply negative,
giving diagnostic visibility into how far an uncorrected linear buffer model
would overshoot, never silently clamped to a physical floor.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Optional, Tuple

import numpy as np
from scipy.optimize import brentq

from scoped_correspondence.errors import ScopeViolationError
from scoped_correspondence.dynamics.phase_type_delays import (
    PhaseType,
    erlang_phase_type,
    validate_phase_type,
    propagate_linear_constant_input,
)

_IMAG_TOL = 1e-7


def _combined_system(pt: PhaseType, inflow: float) -> np.ndarray:
    """Build the (n+1)x(n+1) state matrix ``A`` for the combined
    (stages, buffer) system: ``dz/dt = z@T + u*alpha``, ``dR/dt = inflow -
    z@r``. The constant ``inflow`` term itself is carried in ``d``, not here."""
    n = pt.T.shape[0]
    A = np.zeros((n + 1, n + 1))
    A[:n, :n] = pt.T.T
    A[n, :n] = -pt.r
    return A


def _erlang_output_polynomial(z0: np.ndarray, k: float, u: float) -> np.poly1d:
    """``y(tau) = u + exp(-k*tau)*P(tau)`` for an Erlang(n,k) chain driven by
    constant input ``u`` over ``[0,tau]`` starting from stage occupancies
    ``z0`` (module docstring; verified to machine precision against
    ``propagate_phase_type`` in ``verify_distributed_delay_pilot.py``)."""
    n = len(z0)
    c = np.zeros(n)  # ascending powers of tau
    for m in range(n):
        j = n - 1 - m
        c[m] = k ** (m + 1) * z0[j] / math.factorial(m) - u * k ** m / math.factorial(m)
    return np.poly1d(c[::-1])  # numpy.poly1d wants descending-power coefficients


def _output_critical_points(z0: np.ndarray, k: float, u: float, tau_max: float) -> List[float]:
    """Exact interior (``0 < tau < tau_max``) stationary points of the segment's
    output ``y``, via the real roots of ``Q = P' - k*P`` -- never a sampling
    grid (module docstring)."""
    P = _erlang_output_polynomial(z0, k, u)
    Q = P.deriv() - k * P
    if np.allclose(Q.coeffs, 0.0, atol=1e-12):
        return []
    roots = Q.roots
    return sorted(
        float(r.real) for r in roots
        if abs(r.imag) < _IMAG_TOL and 1e-12 < r.real < tau_max - 1e-12
    )


def _r_stationary_points(z0: np.ndarray, k: float, u: float, inflow: float, seg_len: float) -> List[float]:
    """All exact interior points in ``(0, seg_len)`` where ``R' = inflow - y =
    0``, found by bracketing within each y-monotone sub-interval delimited by
    ``_output_critical_points`` (module docstring: R' is guaranteed monotone
    there, so at most one root per sub-interval, found completely)."""
    P = _erlang_output_polynomial(z0, k, u)

    def y_of(tau: float) -> float:
        return u + math.exp(-k * tau) * float(P(tau))

    def r_prime_of(tau: float) -> float:
        return inflow - y_of(tau)

    y_crit = _output_critical_points(z0, k, u, seg_len)
    level1 = [0.0] + y_crit + [seg_len]

    stationary: List[float] = []
    for a, b in zip(level1[:-1], level1[1:]):
        ra, rb = r_prime_of(a), r_prime_of(b)
        if ra * rb < 0.0:
            t_star = brentq(r_prime_of, a, b, xtol=1e-13, rtol=1e-13)
            stationary.append(t_star)
    return stationary


@dataclass(frozen=True)
class DistributedDelayResult:
    n_stages: int
    tau: float
    first_passage_time: Optional[float]  # None if R never reaches <= 0 within the horizon (an honest null result)
    R_at_horizon: float
    remaining_mass_at_horizon: float  # mass still in the delay stages, not yet exited as output
    output_peak_time: float
    output_peak_value: float
    R_min_time: float
    R_min_value: float
    trajectory: List[Tuple[float, float, float]]  # (t, R(t), y(t)) sampled diagnostic points

    def to_dict(self) -> dict:
        return {
            "n_stages": self.n_stages, "tau": self.tau, "first_passage_time": self.first_passage_time,
            "R_at_horizon": self.R_at_horizon, "remaining_mass_at_horizon": self.remaining_mass_at_horizon,
            "output_peak_time": self.output_peak_time, "output_peak_value": self.output_peak_value,
            "R_min_time": self.R_min_time, "R_min_value": self.R_min_value,
        }


def run_fixed_experiment(
    n_stages: int,
    tau: float = 1.0,
    u_pulse: float = 5.0,
    pulse_duration: float = 0.2,
    horizon: float = 5.0,
    R0: float = 0.1,
    inflow: float = 0.4,
    n_samples_per_segment: int = 50,
) -> DistributedDelayResult:
    if horizon <= 0.0 or pulse_duration < 0.0 or pulse_duration > horizon:
        raise ScopeViolationError(f"require 0 <= pulse_duration <= horizon; got {pulse_duration!r}, {horizon!r}")

    pt = erlang_phase_type(n_stages, tau)
    validate_phase_type(pt)
    A = _combined_system(pt, inflow)
    n = n_stages
    k = n / tau

    def d_of(u: float) -> np.ndarray:
        d = np.zeros(n + 1)
        d[:n] = u * pt.alpha
        d[n] = inflow
        return d

    def output_of(x: np.ndarray) -> float:
        return float(x[:n] @ pt.r)

    segments: List[Tuple[float, float, np.ndarray]] = []  # (seg_len, u, d)
    if pulse_duration > 0.0:
        segments.append((pulse_duration, u_pulse, d_of(u_pulse)))
    if horizon > pulse_duration:
        segments.append((horizon - pulse_duration, 0.0, d_of(0.0)))

    x0 = np.zeros(n + 1)
    x0[n] = R0

    first_passage: Optional[float] = None
    trajectory: List[Tuple[float, float, float]] = [(0.0, R0, output_of(x0))]
    x_cur = x0
    t_offset = 0.0

    if R0 <= 0.0:
        first_passage = 0.0

    R_min_time, R_min_value = 0.0, R0
    peak_time, peak_value = 0.0, output_of(x0)

    for seg_len, u_seg, d in segments:
        def R_of_s(s: float, x_start=x_cur, d=d) -> float:
            return propagate_linear_constant_input(x_start, A, d, s)[n]

        def y_of_s(s: float, x_start=x_cur, d=d) -> float:
            return output_of(propagate_linear_constant_input(x_start, A, d, s))

        z0 = x_cur[:n]

        # Exact breakpoints: y's own stationary points (Level 1) partition the
        # segment into y-monotone pieces; within each, R's own stationary
        # point (Level 2, at most one, found by bracketed brentq) is located
        # completely. R is guaranteed monotone between consecutive Level-2
        # breakpoints -- see module docstring.
        y_crit = _output_critical_points(z0, k, u_seg, seg_len)
        r_crit = _r_stationary_points(z0, k, u_seg, inflow, seg_len)
        breakpoints = sorted(set([0.0, seg_len] + y_crit + r_crit))

        # First-passage: scan consecutive breakpoint pairs in order (R is
        # monotone within each), find the FIRST sign change, refine exactly.
        if first_passage is None:
            R_at_bp = [R_of_s(s) for s in breakpoints]
            for i in range(len(breakpoints) - 1):
                a, b = breakpoints[i], breakpoints[i + 1]
                Ra, Rb = R_at_bp[i], R_at_bp[i + 1]
                if Ra <= 0.0:
                    first_passage = t_offset + a
                    break
                if Rb <= 0.0:
                    t_star = brentq(R_of_s, a, b, xtol=1e-13, rtol=1e-13)
                    first_passage = t_offset + t_star
                    break

        # R's global minimum over this segment can only occur at a breakpoint
        # (R is monotone strictly between them).
        for s in breakpoints:
            Rs = R_of_s(s)
            if Rs < R_min_value:
                R_min_value, R_min_time = Rs, t_offset + s

        # y's global maximum over this segment can only occur at one of y's
        # own stationary points or the segment's endpoints.
        for s in sorted(set([0.0, seg_len] + y_crit)):
            ys = y_of_s(s)
            if ys > peak_value:
                peak_value, peak_time = ys, t_offset + s

        for step in range(1, n_samples_per_segment + 1):
            s = seg_len * step / n_samples_per_segment
            xs = propagate_linear_constant_input(x_cur, A, d, s)
            trajectory.append((t_offset + s, float(xs[n]), output_of(xs)))

        x_cur = propagate_linear_constant_input(x_cur, A, d, seg_len)
        t_offset += seg_len

    if x_cur[n] < R_min_value:
        R_min_value, R_min_time = float(x_cur[n]), horizon

    return DistributedDelayResult(
        n_stages=n_stages, tau=tau, first_passage_time=first_passage,
        R_at_horizon=float(x_cur[n]), remaining_mass_at_horizon=float(np.sum(x_cur[:n])),
        output_peak_time=peak_time, output_peak_value=peak_value,
        R_min_time=R_min_time, R_min_value=R_min_value,
        trajectory=trajectory,
    )


__all__ = ["DistributedDelayResult", "run_fixed_experiment"]
