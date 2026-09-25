"""Distributed-delay pilot: does spreading a fixed-mean delay over more stages
change when a downstream buffer runs dry (INTEGRATED_EXTENSION_ROADMAP.md
Paket C3, plan section 7's fixed experiment)?

Fixed experiment: an Erlang(n) delay chain with mean dwell time
``tau=1`` for ``n in {1,2,4,8}``, driven by a rectangular input pulse
``u(t)=5`` on ``[0, 0.2)`` then ``0``, feeding a downstream buffer
``R(0)=0.1``, ``dR/dt = 0.4 - y(t)`` (``y`` the chain's output), over horizon
``5``. Event of interest: the first time ``R(t) <= 0``.

The combined (``n`` delay-chain stages + 1 buffer) system is linear with
PIECEWISE-CONSTANT input (one break at the pulse's end), so it is propagated
EXACTLY via ``dynamics.phase_type_delays.propagate_linear_constant_input``
within each constant-input segment, and the first-passage time is located by
root-finding directly on that exact closed form (``scipy.optimize.brentq``)
-- never by scanning a fixed time grid and accepting whichever grid point
happens to be closest.

**No reflection/clipping** (plan section 7): if ``R`` goes negative, the
simulation keeps running past that point with the SAME linear dynamics --
the buffer's value at the horizon is reported even if deeply negative,
giving diagnostic visibility into how far an uncorrected linear buffer model
would overshoot, never silently clamped to a physical floor.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple

import numpy as np
from scipy.optimize import brentq, minimize_scalar

from scoped_correspondence.errors import ScopeViolationError
from scoped_correspondence.dynamics.phase_type_delays import (
    PhaseType,
    erlang_phase_type,
    validate_phase_type,
    propagate_linear_constant_input,
)


def _combined_system(pt: PhaseType, inflow: float) -> np.ndarray:
    """Build the (n+1)x(n+1) state matrix ``A`` for the combined
    (stages, buffer) system: ``dz/dt = z@T + u*alpha``, ``dR/dt = inflow -
    z@r``. The constant ``inflow`` term itself is carried in ``d``, not here."""
    n = pt.T.shape[0]
    A = np.zeros((n + 1, n + 1))
    A[:n, :n] = pt.T.T
    A[n, :n] = -pt.r
    return A


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

    def d_of(u: float) -> np.ndarray:
        d = np.zeros(n + 1)
        d[:n] = u * pt.alpha
        d[n] = inflow
        return d

    def output_of(x: np.ndarray) -> float:
        return float(x[:n] @ pt.r)

    segments: List[Tuple[float, np.ndarray]] = []
    if pulse_duration > 0.0:
        segments.append((pulse_duration, d_of(u_pulse)))
    if horizon > pulse_duration:
        segments.append((horizon - pulse_duration, d_of(0.0)))

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

    for seg_len, d in segments:
        def R_of_s(s: float, x_start=x_cur, d=d) -> float:
            return propagate_linear_constant_input(x_start, A, d, s)[n]

        def y_of_s(s: float, x_start=x_cur, d=d) -> float:
            return output_of(propagate_linear_constant_input(x_start, A, d, s))

        R_start = x_cur[n]
        x_end = propagate_linear_constant_input(x_cur, A, d, seg_len)
        R_end = x_end[n]

        if first_passage is None:
            # A same-sign check on the segment's ENDPOINTS ALONE would miss a
            # dip-and-recovery strictly inside the segment (R can go negative and
            # come back up before the segment ends) -- bracket the first crossing
            # using a dense scan of consecutive sample points instead, then refine
            # the bracket found this way with brentq for an exact crossing time.
            n_scan = max(n_samples_per_segment, 500)
            s_grid = np.linspace(0.0, seg_len, n_scan + 1)
            R_grid = np.array([R_start] + [R_of_s(s) for s in s_grid[1:]])
            below = np.where(R_grid <= 0.0)[0]
            if len(below) > 0:
                i = int(below[0])
                if i == 0:
                    first_passage = t_offset  # R was already <= 0 at the segment's start
                else:
                    t_star = brentq(R_of_s, s_grid[i - 1], s_grid[i], xtol=1e-12, rtol=1e-12)
                    first_passage = t_offset + t_star

        # Refine this segment's R-minimum and output-peak exactly (bounded scalar
        # optimization on the closed-form propagate_linear_constant_input, not just
        # whichever sample point happens to be closest).
        res_min = minimize_scalar(R_of_s, bounds=(0.0, seg_len), method="bounded")
        if res_min.fun < R_min_value:
            R_min_value, R_min_time = float(res_min.fun), t_offset + float(res_min.x)
        res_max = minimize_scalar(lambda s: -y_of_s(s), bounds=(0.0, seg_len), method="bounded")
        if -res_max.fun > peak_value:
            peak_value, peak_time = float(-res_max.fun), t_offset + float(res_max.x)

        for k in range(1, n_samples_per_segment + 1):
            s = seg_len * k / n_samples_per_segment
            xs = propagate_linear_constant_input(x_cur, A, d, s)
            trajectory.append((t_offset + s, float(xs[n]), output_of(xs)))

        x_cur = x_end
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
