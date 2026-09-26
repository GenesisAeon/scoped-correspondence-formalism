"""Exact homology correspondence for spherical halo profiles (G2).

Content basis: `SCF_GALAXY_DYNAMICS_IMPLEMENTATION_PLAN.md` §7 ("G2 --
Exakte Homologie als SCF-Korrespondenz").

For `lambda > 0`, the scaling family `rho_lambda(r) = lambda^-1 *
rho(r/lambda)` (fixed profile shape, `rho0 -> rho0/lambda`, `r0 ->
lambda*r0`) preserves `mu_h = rho0*r0` and satisfies, at CORRESPONDING
radii `r` and `lambda*r` (never the same physical radius):

    M_lambda(<lambda*r) = lambda^2 * M(<r)
    g_lambda(lambda*r)  = g(r)
    v_c,lambda(lambda*r) = sqrt(lambda) * v_c(r)

For Newtonian test particles, `T_lambda(r,v) = (lambda*r, sqrt(lambda)*v)`
conjugates the phase-space flow with time scale `c = sqrt(lambda)` (Plan
§7.1 API convention -- in the SCF `Correspondence` interface, `target_time
= c * source_time`, so `c=sqrt(lambda)` is correct and `1/sqrt(lambda)`
would be wrong; a negative control for exactly this mistake lives in
`verification/verify_galaxy_homology.py`).

This is a statement about test-particle dynamics in prescribed fields --
NOT self-consistent stellar-distribution evolution, collisions,
cosmological expansion, or a relativistic metric. Non-scaled baryons and
fixed outer radii can break the correspondence (Plan §7.2 point-mass
counterexample, reproduced in the verification script).
"""
from __future__ import annotations

import math
from dataclasses import dataclass

from ..correspondence.contract import Correspondence, ModelRef, Scope, StateMap, TimeMap
from .spherical_profiles import BurkertProfile


@dataclass(frozen=True)
class HomologyScaling:
    """The scaling family for a fixed `lambda > 0` (Plan §7.1)."""

    lam: float

    def __post_init__(self) -> None:
        if self.lam <= 0:
            raise ValueError("lambda must be positive")

    def scaled_burkert(self, source: BurkertProfile) -> BurkertProfile:
        """`rho0 -> rho0/lambda`, `r0 -> lambda*r0`; profile shape unchanged."""
        return BurkertProfile(
            rho0_msun_pc3=source.rho0_msun_pc3 / self.lam,
            r0_pc=source.r0_pc * self.lam,
            series_switch_x=source.series_switch_x,
        )

    def state_map_rv(self) -> StateMap:
        """`T_lambda(r, v) = (lambda*r, sqrt(lambda)*v)` (Plan §7.1)."""
        lam = self.lam

        def _map(state):
            r, v = state
            return (lam * r, math.sqrt(lam) * v)

        return StateMap(map_fn=_map, name=f"T_lambda(r,v; lambda={lam})")

    def state_map_r_theta(self) -> StateMap:
        """`T_lambda(r, theta) = (lambda*r, theta)` -- circular-orbit encoding.

        The orbital angle is dimensionless and unaffected by the spatial
        rescaling; the period-scaling physics enters through the time_map
        (`c = sqrt(lambda)`), not this state map.
        """
        lam = self.lam
        return StateMap(
            map_fn=lambda state: (lam * state[0], state[1]),
            name=f"T_lambda(r,theta; lambda={lam})",
        )

    def time_map(self) -> TimeMap:
        """`c = sqrt(lambda)` (Plan §7.1: `target_time = c * source_time`)."""
        return TimeMap(name=f"time_scale(lambda={self.lam})", constant_scale=math.sqrt(self.lam))


def circular_orbit_flow(profile: BurkertProfile):
    """Analytic circular-orbit flow: `Phi^t(r, theta) = (r, theta + omega(r)*t)`.

    Scoped ONLY to circular orbits -- NOT a general Burkert flow (Plan
    §7.2: "Einen Kreisbahn-Ausdruck nicht als allgemeinen Burkert-Flow
    anbieten"). The time unit is whatever makes `pc / (km/s)` self
    consistent; the conjugacy identity being tested is a dimensionless
    functional equation, so this choice does not affect its validity.
    """

    def _flow(state, t):
        r, theta = state
        v_c = profile.circular_velocity(r)
        omega = v_c / r
        return (r, theta + omega * t)

    return _flow


def circular_orbit_correspondence(source: BurkertProfile, lam: float) -> Correspondence:
    """Build the G2 `Correspondence` for circular orbits under scaling `lambda`."""
    scaling = HomologyScaling(lam)
    target = scaling.scaled_burkert(source)
    return Correspondence(
        source=ModelRef(name="burkert_circular_source", flow=circular_orbit_flow(source)),
        target=ModelRef(name="burkert_circular_target", flow=circular_orbit_flow(target)),
        state_map=scaling.state_map_r_theta(),
        time_map=scaling.time_map(),
        scope=Scope(
            description="circular orbits only, r>0, finite time horizon",
            assumptions=(
                "circular orbit (fixed r, tangential v=v_c(r))",
                "test particle, no self-gravity of the orbiting body",
            ),
            state_ok=lambda state: state[0] > 0,
            time_horizon=(-1.0e6, 1.0e6),
        ),
    )


def radial_acceleration_identity_residual(source: BurkertProfile, lam: float, r_pc: float) -> float:
    """`|g_source(r) - g_target(lambda*r)|` for GENERAL (non-circular) states.

    Plan §7.1's vector-field theorem `DT_lambda F(z) = sqrt(lambda) *
    F_lambda(T_lambda z)`, for `F=(v,-g(r))` with Jacobian
    `diag(lambda, sqrt(lambda))`, reduces algebraically to `g_source(r) =
    g_target(lambda*r)` -- independent of the velocity component `v`.
    Checking this identity therefore covers "general initial states"
    (Plan §7.2: "für allgemeine Anfangszustände... den Vektorfeldsatz
    direkt prüfen") without integrating any ODE flow.
    """
    target = HomologyScaling(lam).scaled_burkert(source)
    return abs(source.g(r_pc) - target.g(lam * r_pc))
