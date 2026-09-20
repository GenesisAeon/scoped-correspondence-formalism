"""Chemical Organization Theory (COT) — Milestone 41.

Dittrich & Speroni di Fenizio 2007; Fontana & Buss 1994.
Reaction-closed + self-maintaining (linprog) ⇒ organization.

This Baustein does NOT fully formalize Autopoiesis; name
chemical_organization not autopoiesis. Reaction closure, formal-concept
closure, and Markovian closure have different semantics. This does not
rule out structural relations between selected constructions (see
docs/structural_relations.md, bridge B1). Such relations must specify
the objects, maps, preserved properties, and limitations; they do not
imply shared physical meaning or require shared implementation
inheritance.
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
