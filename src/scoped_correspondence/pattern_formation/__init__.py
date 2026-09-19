"""Pattern formation / Turing instability (Milestone 30).

Independent Baustein — not an extension of ``dynamics``.

Schnakenberg 1979 (J Theor Biol) is a DIFFERENT paper than Schnakenberg 1976 (Rev Mod Phys) used in thermo/schnakenberg.py (M18) — different journal/year/claim; do not mix modules.

A future correspondence bridge to dynamics is structurally conceivable (Turing S_rec(k) would generalize dynamics.recovery_rate_at_equilibrium as S_rec(0)) but is NOT claimed or implemented here; a real conjugacy would need the correspondence contract with its own proof.
"""

from scoped_correspondence.pattern_formation.core import (
    DYNAMICS_BRIDGE_WARNING,
    SCHNAKENBERG_PAPER_WARNING,
    SOURCE,
    DispersionResult,
    JacobianStabilityResult,
    Schnakenberg1979SteadyState,
    TuringConditionsResult,
    critical_diffusivity_roots_schnakenberg,
    dispersion_relation,
    jacobian_stability,
    schnakenberg_1979_steady_state,
    turing_conditions,
)

__all__ = [
    "DYNAMICS_BRIDGE_WARNING",
    "SCHNAKENBERG_PAPER_WARNING",
    "SOURCE",
    "DispersionResult",
    "JacobianStabilityResult",
    "Schnakenberg1979SteadyState",
    "TuringConditionsResult",
    "critical_diffusivity_roots_schnakenberg",
    "dispersion_relation",
    "jacobian_stability",
    "schnakenberg_1979_steady_state",
    "turing_conditions",
]
