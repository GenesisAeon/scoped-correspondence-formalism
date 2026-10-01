"""One checked transport rule: standardisation (Paket J10, plan §16).

    Q(Y | do(X = x)) = sum_z P(Y | do(X = x), Z = z) Q(Z = z)

Preconditions (all checked, each failure named):

- Z are observed and not descendants of X in the selection diagram;
- Z is S-admissible: (Y _||_ S | X, Z) in G_{bar X} (a check of a DECLARED
  causal assumption, not learned from data);
- the source quantities are INTERVENTIONAL P(Y | do(x), Z = z) -- observational
  P(Y | X, Z) are not accepted in their place (the provenance field must say
  "source_experiment");
- support: every z with Q(z) > 0 has a source table entry.

Three DIFFERENT outcomes:

1. ``certified_applicable``    -- the formula follows under the checked premises;
2. ``not_certified_by_this_rule`` -- some premise fails or is unproven; this is
   NOT a proof of non-transportability;
3. ``non_identified_by_counter_models`` -- two admitted complete source-target
   model families agree on ALL available information and differ in the target
   quantity (``counter_model_witness``).

Not a general Pearl transportability / sID solver.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
from typing import Any, Callable, Dict, List, Mapping, Optional, Sequence, Tuple

from scoped_correspondence.causal.selection_diagrams import DAG, s_admissible
from scoped_correspondence.errors import ScopeViolationError

OUTCOMES = ("certified_applicable", "not_certified_by_this_rule", "non_identified_by_counter_models")


@dataclass(frozen=True)
class TransportResult:
    outcome: str
    value: Optional[Dict[Any, Fraction]]  # target P(Y = y | do(x)) per y, when certified
    premises: Dict[str, bool]
    reasons: Tuple[str, ...]
    source_provenance: str
    notes: Tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if self.outcome not in OUTCOMES:
            raise ValueError(f"outcome must be one of {OUTCOMES}")


def standardise(diagram: DAG, *, x: str, y: str, z: Sequence[str], s_nodes: Sequence[str], x_value: Any,
                source_do_table: Mapping[Tuple[Any, ...], Mapping[Any, Fraction]], target_z: Mapping[Tuple[Any, ...], Fraction],
                source_provenance: str) -> TransportResult:
    """``source_do_table[z_tuple][y_value] = P(Y = y | do(X = x_value), Z = z)`` from
    SOURCE EXPERIMENTS; ``target_z[z_tuple] = Q(Z = z)``."""
    premises: Dict[str, bool] = {}
    reasons: List[str] = []
    premises["source_quantities_interventional"] = source_provenance == "source_experiment"
    if not premises["source_quantities_interventional"]:
        reasons.append("source table is not interventional (P(Y|X,Z) cannot replace P(Y|do(X),Z) without further identification)")
    desc = diagram.descendants(x)
    premises["z_not_descendant_of_x"] = not (set(z) & desc)
    if not premises["z_not_descendant_of_x"]:
        reasons.append(f"Z contains descendants of X: {sorted(set(z) & desc)}")
    premises["z_observed"] = not (set(z) & diagram.latent)
    if not premises["z_observed"]:
        reasons.append("Z contains latent nodes")
    premises["s_admissible"] = s_admissible(diagram, s_nodes, [x], [y], z)
    if not premises["s_admissible"]:
        reasons.append("Z is not S-admissible: Y is not separated from S given X, Z in G_bar_X")
    total = sum(target_z.values(), Fraction(0))
    if total != 1 or any(p < 0 for p in target_z.values()):
        raise ScopeViolationError("target Q(Z) must be a probability table summing to exactly 1")
    missing = [zz for zz, p in target_z.items() if p > 0 and zz not in source_do_table]
    premises["support"] = not missing
    if missing:
        reasons.append(f"no source experiment for target z values {missing}: the rule cannot be evaluated empirically")
    for zz, row in source_do_table.items():
        if sum(row.values(), Fraction(0)) != 1:
            raise ScopeViolationError(f"source table row {zz} does not sum to 1 (incomplete table)")
    if not all(premises.values()):
        return TransportResult("not_certified_by_this_rule", None, premises, tuple(reasons), source_provenance,
                               ("not a proof of non-transportability",))
    ys = sorted({yy for row in source_do_table.values() for yy in row}, key=repr)
    val = {yy: sum((source_do_table[zz].get(yy, Fraction(0)) * p for zz, p in target_z.items() if p > 0), Fraction(0)) for yy in ys}
    return TransportResult("certified_applicable", val, premises, (), source_provenance,
                           ("follows from the checked premises of the DECLARED selection diagram",))


def counter_model_witness(family_a: Mapping[str, Any], family_b: Mapping[str, Any], available: Sequence[str], target: str) -> TransportResult:
    """Two complete source-target model families, given as dicts of computed
    quantities (exact). If they agree on EVERY listed available quantity and
    differ on the target, the target is not identified from that information."""
    missing = [k for k in list(available) + [target] if k not in family_a or k not in family_b]
    if missing:
        raise ScopeViolationError(f"both families must provide every quantity: missing {missing}")
    same = all(family_a[k] == family_b[k] for k in available)
    differ = family_a[target] != family_b[target]
    if same and differ:
        return TransportResult("non_identified_by_counter_models", None, {"agree_on_all_available": True, "differ_on_target": True},
                               (f"target {target}: {family_a[target]} vs {family_b[target]}",), "counter-model families",
                               (f"checked available quantities: {list(available)}",))
    return TransportResult("not_certified_by_this_rule", None, {"agree_on_all_available": same, "differ_on_target": differ},
                           ("the pair is not a non-identification witness",), "counter-model families")


__all__ = ["OUTCOMES", "TransportResult", "standardise", "counter_model_witness"]
