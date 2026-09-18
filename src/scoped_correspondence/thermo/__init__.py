"""Thermodynamics — GENERIC helpers (M8) + Schnakenberg network thermo (M18).

FORMALISM adjunct for coupling_layer_afet.md §8–§9 (M8).
M18: Schnakenberg 1976 cycle affinities / entropy production
(DOI 10.1103/RevModPhys.48.571). Does not mutate ``thermo/core.py``.
Does not merge with the M8 deterministic 3-cycle formula.
"""

from scoped_correspondence.thermo.core import (
    heat_generic_example,
    project_generic_structure,
    stochastic_inverse_not_detailed_balance,
)
from scoped_correspondence.thermo.schnakenberg import (
    SOURCE as SCHNAKENBERG_SOURCE,
    cycle_affinity,
    entropy_production_rate,
    stationary_currents,
)

__all__ = [
    # M8 GENERIC / memory (unchanged core)
    "heat_generic_example",
    "project_generic_structure",
    "stochastic_inverse_not_detailed_balance",
    # M18 Schnakenberg network thermodynamics
    "SCHNAKENBERG_SOURCE",
    "stationary_currents",
    "cycle_affinity",
    "entropy_production_rate",
]
