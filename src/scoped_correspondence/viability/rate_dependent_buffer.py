"""Rate-dependent buffer viability under a transient load spike (Milestone 43).

NONSTATIONARY_ROADMAP.md package 4, response to
prompts/Answers/nicht_stationäre_Treiber/SCF_Nichtstationaere_Treiber_und_Kippen.md
(Astra, 2026-09-21) section 5.2 (moving equilibria, adaptation time,
buffer) and section 8 package 4 ("Der oben gerechnete Fall sowie ein
Pufferfall: gleiche Belastungsendwerte, unterschiedliches Tempo oder
unterschiedliche Reserve").

Uses the SAME scalar buffer model as viability/core.has_safe_transfer
(z_dot = -r(z-z_eq) + U - W) but with a genuinely time-varying load W(t):
a single Gaussian-shaped spike of height ``spike_height`` above a
baseline ``W0``, returning to ``W0`` afterward -- so the load has the
SAME value before and after the spike (Astra's "gleiche
Belastungsendwerte"). The baseline W0 is frozen-safe
(has_safe_transfer(...,W0)=True); the frozen state AT THE PEAK load
(W0+spike_height) is deliberately UNSAFE (has_safe_transfer(...,
W0+spike_height)=False) -- this is not a control-case flaw, it is the
whole point: whether the REAL, time-varying trajectory actually breaches
the safety boundary during the transient depends on the spike's TEMPO
(how fast it rises and falls, relative to the buffer's own relaxation
rate r) and on the RESERVE (how far the safety threshold b sits below the
baseline equilibrium) -- not only on whether the frozen peak load would
be sustainable forever.

This is the mirror-image lesson to dynamics/rate_dependent.py's
rate-induced tipping: there, checking ONLY frozen (quasi-static)
stability along a driver's path MISSES a real risk that fast driving
creates (the frozen stability never changes, yet the trajectory still
tips). Here, checking ONLY the frozen state at the worst instantaneous
load can be OVERLY conservative for a transient that is fast relative to
the buffer's own relaxation -- a sufficiently brief spike gets
attenuated by the buffer's own inertia and may never come close to the
frozen worst case. Because the frozen path here DOES cross the safety
boundary at its peak, dynamics.rate_dependent.local_chi_diagnostic is not
applicable in this module (it assumes the frozen system stays on the
safe side throughout) -- see docs/rate_dependent_tipping.md.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import minimize_scalar

from scoped_correspondence.errors import ScopeViolationError
from scoped_correspondence.viability.core import has_safe_transfer


@dataclass(frozen=True)
class BufferSpikeTrajectory:
    r: float
    z_eq: float
    U: float
    W0: float
    spike_height: float
    tau: float
    t0: float
    t1: float
    z_min: float
    z_min_time: float
    refinement_max_difference: float
    z_min_ode_uncertainty: float
    z_min_grid_search_error: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "r": self.r,
            "z_eq": self.z_eq,
            "U": self.U,
            "W0": self.W0,
            "spike_height": self.spike_height,
            "tau": self.tau,
            "t0": self.t0,
            "t1": self.t1,
            "z_min": self.z_min,
            "z_min_time": self.z_min_time,
            "refinement_max_difference": self.refinement_max_difference,
            "z_min_ode_uncertainty": self.z_min_ode_uncertainty,
            "z_min_grid_search_error": self.z_min_grid_search_error,
        }


@dataclass(frozen=True)
class BufferSpikeViabilityReport:
    trajectory: BufferSpikeTrajectory
    baseline_frozen_safe: bool
    peak_frozen_safe: bool
    transient_breach: bool
    boundary: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "trajectory": self.trajectory.to_dict(),
            "baseline_frozen_safe": self.baseline_frozen_safe,
            "peak_frozen_safe": self.peak_frozen_safe,
            "transient_breach": self.transient_breach,
            "boundary": self.boundary,
        }


def _load(t: float, W0: float, spike_height: float, tau: float) -> float:
    return W0 + spike_height * np.exp(-((t / tau) ** 2))


def run_buffer_spike_trajectory(
    r: float,
    z_eq: float,
    U: float,
    W0: float,
    spike_height: float,
    tau: float,
    *,
    span_taus: float = 8.0,
    margin: float = 5.0,
) -> BufferSpikeTrajectory:
    """Integrate z_dot = -r(z-z_eq) + U - W(t) through a single Gaussian load spike.

    W(t) = W0 + spike_height*exp(-(t/tau)^2): equals W0 far before and far
    after the spike (same load value at both ends), peaks at W0+spike_height
    at t=0. Starts at the baseline steady state z_eq+(U-W0)/r, well before
    the spike (t0 = -span_taus*tau - margin), integrated well after it
    (t1 = span_taus*tau + margin). Refines the integration tolerance and
    reports the max difference between a coarse and a much finer solve, as
    an explicit numerical-convergence check.

    z_min is the TRUE CONTINUOUS minimum of the fine solution's dense
    output, found by bounded scalar minimization -- NOT a grid argmin.

    Fixed 2026-09-23 in response to
    prompts/Answers/nicht_stationäre_Treiber/SCF_Followup_1231f64.md
    (Astra): the previous version located the minimum via
    ``np.argmin`` over a fixed 4001-point grid. Astra found a closed-form
    counterexample (r=tau=spike_height=1, z_eq=U=W0=0, a Gaussian-pulse
    convolution integral) where the true continuous minimum
    (-0.6947532810...) differs from the grid-based minimum
    (-0.6947528523...) by 4.29e-7 -- more than 100x the ODE-tolerance-based
    uncertainty band (3.28e-9) that was being used to decide whether a
    boundary classification was trustworthy. Near a safety boundary set
    close to the trajectory's own minimum, this let a genuine breach be
    misclassified as safe. ``z_min_ode_uncertainty`` (coarse vs. fine
    solution difference EVALUATED AT the located minimum's time, not a
    global grid-max) is now the uncertainty proxy classification code
    should use; ``z_min_grid_search_error`` records the size of the fixed
    bug for transparency (the gap between the old grid method and the new
    continuous one on THIS call).
    """
    if r <= 0:
        raise ScopeViolationError(f"run_buffer_spike_trajectory: r must be > 0; got {r!r}")
    if tau <= 0:
        raise ScopeViolationError(f"run_buffer_spike_trajectory: tau must be > 0; got {tau!r}")

    t0 = -span_taus * tau - margin
    t1 = span_taus * tau + margin
    z0 = z_eq + (U - W0) / r

    def rhs(t, z):
        return [-r * (z[0] - z_eq) + U - _load(t, W0, spike_height, tau)]

    max_step = tau / 20.0
    coarse = solve_ivp(rhs, (t0, t1), [z0], rtol=1e-10, atol=1e-12, dense_output=True, max_step=max_step)
    fine = solve_ivp(rhs, (t0, t1), [z0], rtol=1e-12, atol=1e-14, dense_output=True, max_step=max_step / 2.0)
    if not coarse.success:
        raise ScopeViolationError(f"run_buffer_spike_trajectory: solve_ivp failed: {coarse.message}")
    if not fine.success:
        raise ScopeViolationError(f"run_buffer_spike_trajectory: solve_ivp (fine) failed: {fine.message}")

    grid = np.linspace(t0, t1, 4001)
    z_coarse = coarse.sol(grid)[0]
    z_fine = fine.sol(grid)[0]
    refinement_max_diff = float(np.max(np.abs(z_coarse - z_fine)))

    # Old (buggy) grid-based minimum, kept only to quantify the fixed error.
    i_min_grid = int(np.argmin(z_coarse))
    z_min_grid = float(z_coarse[i_min_grid])

    # TRUE continuous minimum: bounded scalar minimization of the FINE
    # solution's dense (continuous) output -- not a grid search.
    opt = minimize_scalar(lambda t: float(fine.sol(t)[0]), bounds=(t0, t1), method="bounded", options={"xatol": 1e-12})
    if not opt.success:
        raise ScopeViolationError(f"run_buffer_spike_trajectory: continuous minimum search failed: {opt.message}")
    z_min = float(opt.fun)
    z_min_time = float(opt.x)

    # ODE-tolerance uncertainty EVALUATED AT the located minimum's time
    # (not a global grid-max difference) -- the uncertainty that actually
    # matters for trusting a boundary classification near this minimum.
    z_min_ode_uncertainty = float(abs(float(coarse.sol(z_min_time)[0]) - float(fine.sol(z_min_time)[0])))

    return BufferSpikeTrajectory(
        r=r,
        z_eq=z_eq,
        U=U,
        W0=W0,
        spike_height=spike_height,
        tau=tau,
        t0=t0,
        t1=t1,
        z_min=z_min,
        z_min_time=z_min_time,
        refinement_max_difference=refinement_max_diff,
        z_min_ode_uncertainty=z_min_ode_uncertainty,
        z_min_grid_search_error=float(abs(z_min_grid - z_min)),
    )


def equal_total_load_height(total_extra_load: float, tau: float) -> float:
    """Spike height so that the total EXTRA load (integral of spike_height*exp(-(t/tau)^2)
    over all t) equals ``total_extra_load``, since that integral is
    spike_height*sqrt(pi)*tau.

    CORRECTION (2026-09-21, external review by Astra): the module's
    existing "shorter pulses are safer" finding holds the PEAK height
    fixed while tau varies -- which means shorter pulses also carry LESS
    total load. Holding the total load fixed instead (via this height)
    is a genuine second control case, and REVERSES the conclusion: see
    ``docs/rate_dependent_tipping.md``. Neither framing is wrong; they
    answer different questions (peak-limited vs. total-energy-limited
    disturbances), and a single "faster is safer/more dangerous" claim
    without saying which is held fixed is not identified.
    """
    if total_extra_load <= 0:
        raise ScopeViolationError(f"equal_total_load_height: total_extra_load must be > 0; got {total_extra_load!r}")
    if tau <= 0:
        raise ScopeViolationError(f"equal_total_load_height: tau must be > 0; got {tau!r}")
    return float(total_extra_load / (np.sqrt(np.pi) * tau))


def buffer_spike_viability_report(
    r: float,
    z_eq: float,
    b: float,
    U: float,
    W0: float,
    spike_height: float,
    tau: float,
) -> BufferSpikeViabilityReport:
    """Combines frozen safety at baseline/peak load with the actual transient minimum.

    baseline_frozen_safe: has_safe_transfer at the constant load W0.
    peak_frozen_safe: has_safe_transfer at the constant load W0+spike_height
    (expected False for a genuine spike scenario -- documented, not an error).
    transient_breach: whether the actual integrated trajectory's minimum
    crosses below b, which depends on tau (tempo) and b (reserve), NOT
    decidable from either frozen check alone.
    """
    baseline = has_safe_transfer(r, z_eq, b, U, W0)
    peak = has_safe_transfer(r, z_eq, b, U, W0 + spike_height)
    traj = run_buffer_spike_trajectory(r, z_eq, U, W0, spike_height, tau)
    return BufferSpikeViabilityReport(
        trajectory=traj,
        baseline_frozen_safe=bool(baseline["ok"]),
        peak_frozen_safe=bool(peak["ok"]),
        transient_breach=bool(traj.z_min < b),
        boundary=float(b),
    )


__all__ = [
    "BufferSpikeTrajectory",
    "BufferSpikeViabilityReport",
    "run_buffer_spike_trajectory",
    "buffer_spike_viability_report",
    "equal_total_load_height",
]
