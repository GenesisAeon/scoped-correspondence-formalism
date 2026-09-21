"""Rate-dependent (non-autonomous) tracking vs. rate-induced tipping (Milestone 42).

NONSTATIONARY_ROADMAP.md package 3, response to
prompts/Answers/nicht_stationäre_Treiber/SCF_Nichtstationaere_Treiber_und_Kippen.md
(Astra, 2026-09-21) section 5.1: a quasi-static (frozen-parameter) branch
sweep -- e.g. panarchy_cusp.py's hysteresis_sweep -- answers "does an
equilibrium branch exist/stay stable as a parameter changes slowly", but
does NOT by itself answer whether a REAL trajectory, driven by a
genuinely time-dependent (non-autonomous) forcing, keeps up with a moving
stable equilibrium. Those are different questions: a system whose frozen
linear stability never changes (no bifurcation along the driver's path)
can still lose track of its moving equilibrium and settle onto a
different attractor if the driver moves fast enough relative to the
system's own relaxation rate -- RATE-INDUCED TIPPING (as opposed to
bifurcation-induced tipping, where an eigenvalue crosses zero; see
Ashwin, Wieczorek, Vitolo & Cox 2012 and Wieczorek, Xie & Ashwin 2023).

This module keeps the two evaluations explicitly SEPARATE, as Astra's
review asked:
  - ``frozen_equilibria`` / ``frozen_stability``: evaluate the equilibria
    and local linear stability of the system with the driver ``u`` held
    FIXED at a given value -- a snapshot, no time dependence.
  - ``integrate_trajectory``: genuinely integrate the non-autonomous ODE
    dx/dt = f(x, u(t)) forward in time, with u(t) an explicit, externally
    supplied driver function -- not a quasi-static sweep.
  - ``classify_tracking``: after integration, compare the trajectory's
    final state to the frozen equilibria AT THE FINAL DRIVER VALUE, to
    say whether the system tracked a particular branch or ended up near
    a different one.

Canonical worked example (reproduces Ashwin et al. 2012's rate-induced
tipping mechanism on the folded/pitchfork normal form, and the exact
numerical case independently derived and checked in
SCF_Nichtstationaere_Treiber_und_Kippen.md section 5.1):

    dx/dt = (x - u) - (x - u)^3,   u(t) = 1 + tanh(r*t)

Substituting z = x - u gives dz/dt = z - z^3 (the autonomous pitchfork
normal form) -- the frozen equilibria are z=0 (unstable) and z=+-1
(stable), i.e. x = u, x = u+1, x = u-1, with local derivative exactly -2
at both stable branches and +1 at the unstable one, INDEPENDENT of u:
there is no frozen bifurcation anywhere along this driver's path. u(t)
is bounded and S-shaped (an unbounded/exponential driver is not needed
for rate-induced tipping). Whether the real trajectory tracks the upper
branch (x-u -> +1) or switches to the lower branch (x-u -> -1) as the
driver moves from u~0 to u~2 depends only on how FAST the driver moves
(the rate r), not on any change in frozen stability.

Sources
-------
P. Ashwin, S. Wieczorek, R. Vitolo, P. Cox, *Tipping Points in Open
Systems: Bifurcation, Noise-induced and Rate-dependent Examples in the
Climate System*, Phil. Trans. R. Soc. A 370, 1166-1184 (2012);
DOI 10.1098/rsta.2011.0306.

S. Wieczorek, C. Xie, P. Ashwin, *Rate-induced Tipping: Thresholds, Edge
States and Connecting Orbits*, Nonlinearity 36, 3238-3293 (2023);
DOI 10.1088/1361-6544/accb37.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, List, Sequence, Tuple

import numpy as np
from scipy.integrate import solve_ivp

from scoped_correspondence.errors import ScopeViolationError

SOURCE = (
    "Ashwin, Wieczorek, Vitolo & Cox 2012, Phil. Trans. R. Soc. A 370, "
    "1166-1184, DOI 10.1098/rsta.2011.0306; Wieczorek, Xie & Ashwin 2023, "
    "Nonlinearity 36, 3238-3293, DOI 10.1088/1361-6544/accb37."
)

STABLE = "stable"
UNSTABLE = "unstable"


@dataclass(frozen=True)
class FrozenEquilibrium:
    x: float
    stability: str
    local_derivative: float


@dataclass(frozen=True)
class TrackingResult:
    r: float
    t0: float
    t1: float
    final_x: float
    final_u: float
    final_relative_x: float
    tracked_branch: str
    switched: bool
    frozen_equilibria_at_end: Tuple[FrozenEquilibrium, ...]
    refinement_max_difference: float

    def to_dict(self) -> dict:
        return {
            "r": self.r,
            "t0": self.t0,
            "t1": self.t1,
            "final_x": self.final_x,
            "final_u": self.final_u,
            "final_relative_x": self.final_relative_x,
            "tracked_branch": self.tracked_branch,
            "switched": self.switched,
            "frozen_equilibria_at_end": [
                {"x": e.x, "stability": e.stability, "local_derivative": e.local_derivative}
                for e in self.frozen_equilibria_at_end
            ],
            "refinement_max_difference": self.refinement_max_difference,
        }


def frozen_equilibria_shifted_pitchfork(u: float) -> Tuple[FrozenEquilibrium, ...]:
    """Equilibria of dx/dt=(x-u)-(x-u)^3 with u FROZEN (no time dependence).

    z=x-u satisfies dz/dt=z-z^3: equilibria z=0 (unstable, dz'/dz=+1) and
    z=+-1 (stable, dz'/dz=-2). Translated back: x=u (unstable), x=u+1 and
    x=u-1 (stable). The local derivative does not depend on u -- there is
    no frozen bifurcation anywhere along any driver path for this model.
    """
    return (
        FrozenEquilibrium(x=u, stability=UNSTABLE, local_derivative=1.0),
        FrozenEquilibrium(x=u + 1.0, stability=STABLE, local_derivative=-2.0),
        FrozenEquilibrium(x=u - 1.0, stability=STABLE, local_derivative=-2.0),
    )


def integrate_trajectory(
    f: Callable[[float, float], float],
    u_of_t: Callable[[float], float],
    x0: float,
    t0: float,
    t1: float,
    *,
    rtol: float = 1e-9,
    atol: float = 1e-11,
    max_step: float = 0.1,
):
    """Integrate dx/dt = f(x, u(t)) from t0 to t1, starting at x(t0)=x0.

    Genuine non-autonomous trajectory integration -- NOT a quasi-static
    sweep. Raises ScopeViolationError if the integrator itself reports
    failure (never silently returns a non-converged solution).
    """
    if t1 <= t0:
        raise ScopeViolationError(f"integrate_trajectory: t1 must be > t0; got t0={t0!r}, t1={t1!r}")

    def rhs(t, x):
        return [f(x[0], u_of_t(t))]

    sol = solve_ivp(rhs, (t0, t1), [x0], rtol=rtol, atol=atol, dense_output=True, max_step=max_step)
    if not sol.success:
        raise ScopeViolationError(f"integrate_trajectory: solve_ivp failed: {sol.message}")
    return sol


def classify_tracking(
    final_x: float,
    final_u: float,
    frozen_equilibria: Sequence[FrozenEquilibrium],
    *,
    tol: float = 1e-3,
) -> FrozenEquilibrium:
    """Which frozen (stable) equilibrium branch, evaluated AT final_u, is
    the trajectory's final state closest to? Raises ScopeViolationError if
    no stable branch is within ``tol`` (the state is not classifiable as
    having settled onto any known branch).
    """
    stable = [e for e in frozen_equilibria if e.stability == STABLE]
    if not stable:
        raise ScopeViolationError("classify_tracking: no stable frozen equilibria supplied")
    best = min(stable, key=lambda e: abs(final_x - e.x))
    if abs(final_x - best.x) > tol:
        raise ScopeViolationError(
            f"classify_tracking: final_x={final_x!r} is not within tol={tol!r} of any stable "
            f"frozen equilibrium at u={final_u!r} (closest: x={best.x!r}); trajectory may not "
            "have reached a settled state, or the model/window needs review"
        )
    return best


def rate_induced_tipping_cubic_example(
    r: float,
    *,
    x0_offset: float = 1.0,
    margin: float = 10.0,
) -> TrackingResult:
    """The canonical worked example: dx/dt=(x-u)-(x-u)^3, u(t)=1+tanh(r*t).

    Starts near the UPPER branch (x-u = +``x0_offset``, default +1) well
    before the driver begins moving (t0 = -margin/r) and integrates to
    well after it has finished moving (t1 = margin/r + 2*margin), matching
    the construction in SCF_Nichtstationaere_Treiber_und_Kippen.md section
    5.1. Refines the integration tolerance and reports the maximum
    difference between the coarse and fine solutions on a shared grid, as
    an explicit numerical-convergence check (not just a single solve_ivp
    call trusted at face value).
    """
    if r <= 0:
        raise ScopeViolationError(f"rate_induced_tipping_cubic_example: r must be > 0; got {r!r}")

    def driver(t: float) -> float:
        return 1.0 + np.tanh(r * t)

    def f(x: float, u: float) -> float:
        return (x - u) - (x - u) ** 3

    t0 = -margin / r
    t1 = margin / r + 2.0 * margin
    x0 = driver(t0) + x0_offset

    coarse = integrate_trajectory(f, driver, x0, t0, t1, rtol=1e-9, atol=1e-11, max_step=0.1)
    fine = integrate_trajectory(f, driver, x0, t0, t1, rtol=1e-11, atol=1e-13, max_step=0.05)
    grid = np.linspace(t0, t1, 3001)
    refinement_max_diff = float(np.max(np.abs(coarse.sol(grid) - fine.sol(grid))))

    final_x = float(coarse.y[0, -1])
    final_u = float(driver(t1))
    final_relative_x = final_x - final_u
    frozen_at_end = frozen_equilibria_shifted_pitchfork(final_u)
    tracked = classify_tracking(final_x, final_u, frozen_at_end, tol=1e-3)
    switched = tracked.x < final_u  # the lower branch (x=u-1) means the tracked upper branch was lost

    return TrackingResult(
        r=r,
        t0=t0,
        t1=t1,
        final_x=final_x,
        final_u=final_u,
        final_relative_x=final_relative_x,
        tracked_branch="upper (x-u=+1)" if not switched else "lower (x-u=-1)",
        switched=switched,
        frozen_equilibria_at_end=frozen_at_end,
        refinement_max_difference=refinement_max_diff,
    )


__all__ = [
    "SOURCE",
    "STABLE",
    "UNSTABLE",
    "FrozenEquilibrium",
    "TrackingResult",
    "frozen_equilibria_shifted_pitchfork",
    "integrate_trajectory",
    "classify_tracking",
    "rate_induced_tipping_cubic_example",
]
