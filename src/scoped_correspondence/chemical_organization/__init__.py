"""Chemical Organization Theory (COT) — Milestone 41.

Dittrich & Speroni di Fenizio 2007; Fontana & Buss 1994.
Reaction-closed + self-maintaining (linprog) ⇒ organization.

This Baustein does NOT fully formalize Autopoiesis; name
chemical_organization not autopoiesis; word collisions with closure
Baustein (PC=CQ) AND M27 FCA lattice — same words different objects,
no shared base class.
"""

from scoped_correspondence.chemical_organization.core import (
    AUTOPOIESIS_SCOPE_WARNING,
    SOURCE,
    as_report,
    is_organization,
    is_reaction_closed,
    is_self_maintaining,
    maintenance_flux,
)

__all__ = [
    "AUTOPOIESIS_SCOPE_WARNING",
    "SOURCE",
    "as_report",
    "is_organization",
    "is_reaction_closed",
    "is_self_maintaining",
    "maintenance_flux",
]
