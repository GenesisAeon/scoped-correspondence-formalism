"""Thermodynamics -- GENERIC (M8) + Schnakenberg (M18) + Crooks FT (M37).

FORMALISM adjunct for coupling_layer_afet.md §8–§9 (M8).
M18: Schnakenberg 1976 cycle affinities / entropy production
(DOI 10.1103/RevModPhys.48.571).
M37: Crooks 1999 fluctuation theorem / Jarzynski estimate
(DOI 10.1103/PhysRevE.60.2721; arXiv cond-mat/9901352).

Does not mutate ``thermo/core.py`` or ``thermo/schnakenberg.py``.
Does not merge Crooks with Schnakenberg affinities or Onsager ``L_ij``.
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
from scoped_correspondence.thermo.crooks import (
    SOURCE as CROOKS_SOURCE,
    as_report as crooks_as_report,
    jarzynski_estimate,
    verify_crooks_ratio,
    work_ratio,
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
    # M37 Crooks fluctuation theorem
    "CROOKS_SOURCE",
    "work_ratio",
    "verify_crooks_ratio",
    "jarzynski_estimate",
    "crooks_as_report",
]
