"""Chemical Organization Theory (COT) — closed + self-maintaining sets (Milestone 41).

Algebraic / stoichiometric organizations after Dittrich & Speroni di Fenizio
(2007) and Fontana & Buss (1994). A set ``A`` of species is an **organization**
iff it is reaction-closed and (stoichiometrically) self-maintaining.

Definitions (this module)
-------------------------
**Reaction-closed** (``is_reaction_closed``): every reaction whose reactant
species all lie in ``A`` has all product species in ``A``.

**Self-maintaining** (``is_self_maintaining``, LP / mass-maintenance form):
there exists a flux ``v ≥ 0`` such that (1) ``v_r > 0`` for every reaction
applicable inside ``A`` (reactants ⊆ ``A``), (2) ``v_r = 0`` otherwise, and
(3) ``(S v)_s ≥ 0`` for every species ``s ∈ A``. Feasibility is decided by
``scipy.optimize.linprog`` (HiGHS), using the scale-invariant lower bound
``v_r ≥ 1`` on applicable reactions.

**Organization** (``is_organization``): both of the above.

WARNING — Autopoiesis / naming / word collisions (verbatim):
This Baustein does NOT fully formalize Autopoiesis; name chemical_organization not autopoiesis; word collisions with closure Baustein (PC=CQ) AND M27 FCA lattice — same words different objects, no shared base class.

Hard naming rule (identifiers): no function/class/attribute name may contain
``closure`` or ``closed``, except the mandated API name ``is_reaction_closed``.

Sources
-------
- Dittrich & Speroni di Fenizio 2007, Bull. Math. Biol. 69, 1199–1231;
  DOI 10.1007/s11538-006-9130-8
- Fontana & Buss 1994, Bull. Math. Biol. 56, 1–64; DOI 10.1007/BF02458289

Out of scope for M41: full Maturana–Varela autopoiesis (membrane / topology);
mutating other Bausteine, package-root ``__init__.py``, or ``FORMALISM.md``.
"""

from __future__ import annotations

from typing import (
    AbstractSet,
    Any,
    Dict,
    Hashable,
    Iterable,
    List,
    Mapping,
    Optional,
    Sequence,
    Tuple,
    Union,
)

import numpy as np
from scipy.optimize import linprog

from scoped_correspondence.errors import ScopeViolationError

Species = Hashable
Reaction = Tuple[AbstractSet[Species], AbstractSet[Species]]  # (reactants, products)

# Verbatim mandatory disclaimer — must appear in module/API docstrings AND docs.
AUTOPOIESIS_SCOPE_WARNING: str = (
    "This Baustein does NOT fully formalize Autopoiesis; name "
    "chemical_organization not autopoiesis; word collisions with closure "
    "Baustein (PC=CQ) AND M27 FCA lattice — same words different objects, "
    "no shared base class."
)

SOURCE: str = (
    "Dittrich & Speroni di Fenizio 2007 DOI 10.1007/s11538-006-9130-8; "
    "Fontana & Buss 1994 DOI 10.1007/BF02458289"
)

# LP lower bound on fluxes of applicable reactions (scale-invariant > 0).
_APPLICABLE_FLUX_LB: float = 1.0


def _as_species_set(A: Union[AbstractSet[Species], Iterable[Species]]) -> frozenset:
    return frozenset(A)


def _normalize_reactions(
    reactions: Sequence[Reaction],
) -> List[Tuple[frozenset, frozenset]]:
    out: List[Tuple[frozenset, frozenset]] = []
    for i, rxn in enumerate(reactions):
        if not isinstance(rxn, (tuple, list)) or len(rxn) != 2:
            raise ScopeViolationError(
                f"reactions[{i}] must be (reactants, products); got {rxn!r}"
            )
        reactants, products = rxn
        try:
            out.append((frozenset(reactants), frozenset(products)))
        except TypeError as exc:
            raise ScopeViolationError(
                f"reactions[{i}] reactants/products must be iterable of hashables"
            ) from exc
    return out


def _infer_species_order(
    A: AbstractSet[Species],
    reactions: Sequence[Tuple[frozenset, frozenset]],
    species_order: Optional[Sequence[Species]],
) -> List[Species]:
    if species_order is not None:
        order = list(species_order)
        if len(order) != len(set(order)):
            raise ScopeViolationError("species_order must not contain duplicates")
        return order
    universe: set = set(A)
    for reac, prod in reactions:
        universe |= set(reac)
        universe |= set(prod)
    # Prefer stable sorted order when species are mutually comparable.
    try:
        return sorted(universe)  # type: ignore[type-var]
    except TypeError:
        return list(universe)


def _validate_stoich(
    stoich_matrix: np.ndarray,
    n_reactions: int,
    n_species: int,
) -> np.ndarray:
    S = np.asarray(stoich_matrix, dtype=float)
    if S.ndim != 2:
        raise ScopeViolationError(
            f"stoich_matrix must be 2-D; got shape {S.shape!r}"
        )
    if S.shape[1] != n_reactions:
        raise ScopeViolationError(
            f"stoich_matrix columns ({S.shape[1]}) must equal "
            f"len(reactions) ({n_reactions})"
        )
    if S.shape[0] != n_species:
        raise ScopeViolationError(
            f"stoich_matrix rows ({S.shape[0]}) must equal "
            f"len(species_order) ({n_species})"
        )
    if not np.all(np.isfinite(S)):
        raise ScopeViolationError("stoich_matrix must be finite")
    return S


def is_reaction_closed(
    A: Union[AbstractSet[Species], Iterable[Species]],
    reactions: Sequence[Reaction],
) -> bool:
    """Return True iff ``A`` is reaction-closed under ``reactions``.

    ``A`` is reaction-closed when every reaction whose reactants are all in
    ``A`` has all of its products in ``A`` (Dittrich & Speroni di Fenizio
    2007 — algebraic closedness; Fontana & Buss 1994 operational closure as
    precursor). Empty reactant sets (inflow ``∅ → …``) are applicable to
    every ``A``, including the empty set.

    Parameters
    ----------
    A :
        Candidate species set.
    reactions :
        Sequence of ``(reactants, products)`` sets.

    Returns
    -------
    bool

    Notes
    -----
    This Baustein does NOT fully formalize Autopoiesis; name
    chemical_organization not autopoiesis; word collisions with closure
    Baustein (PC=CQ) AND M27 FCA lattice — same words different objects,
    no shared base class.
    """
    species = _as_species_set(A)
    rxns = _normalize_reactions(reactions)
    for reactants, products in rxns:
        if reactants <= species:
            if not (products <= species):
                return False
    return True


def _applicable_indices(
    species: AbstractSet[Species],
    reactions: Sequence[Tuple[frozenset, frozenset]],
) -> List[int]:
    return [i for i, (reac, _prod) in enumerate(reactions) if reac <= species]


def maintenance_flux(
    A: Union[AbstractSet[Species], Iterable[Species]],
    reactions: Sequence[Reaction],
    stoich_matrix: Union[np.ndarray, Sequence[Sequence[float]]],
    *,
    species_order: Optional[Sequence[Species]] = None,
) -> Optional[np.ndarray]:
    """Return a self-maintenance flux ``v`` for ``A``, or ``None`` if none exists.

    Solves the Dittrich mass-maintenance LP via ``scipy.optimize.linprog``:
    applicable fluxes ``≥ 1``, non-applicable fluxes ``= 0``, and
    ``(S v)_s ≥ 0`` for all ``s ∈ A``. Returns one feasible ``v`` (HiGHS)
    or ``None``.

    Notes
    -----
    This Baustein does NOT fully formalize Autopoiesis; name
    chemical_organization not autopoiesis; word collisions with closure
    Baustein (PC=CQ) AND M27 FCA lattice — same words different objects,
    no shared base class.
    """
    species = _as_species_set(A)
    rxns = _normalize_reactions(reactions)
    order = _infer_species_order(species, rxns, species_order)
    S = _validate_stoich(np.asarray(stoich_matrix, dtype=float), len(rxns), len(order))

    order_index: Dict[Species, int] = {s: i for i, s in enumerate(order)}
    missing = [s for s in species if s not in order_index]
    if missing:
        raise ScopeViolationError(
            f"species in A missing from species_order / inferred universe: {missing!r}"
        )

    applicable = _applicable_indices(species, rxns)
    n_r = len(rxns)

    # Vacuous case: no applicable reactions ⇒ zero flux maintains nothing.
    if not applicable:
        return np.zeros(n_r, dtype=float)

    if not species:
        # Empty A with applicable reactions (e.g. ∅→a): species constraints
        # are vacuous; any positive applicable flux is feasible.
        v = np.zeros(n_r, dtype=float)
        for i in applicable:
            v[i] = _APPLICABLE_FLUX_LB
        return v

    row_idx = [order_index[s] for s in sorted(species, key=lambda x: order_index[x])]
    S_A = S[row_idx, :]

    c = np.zeros(n_r, dtype=float)
    bounds = []
    app_set = set(applicable)
    for i in range(n_r):
        if i in app_set:
            bounds.append((_APPLICABLE_FLUX_LB, None))
        else:
            bounds.append((0.0, 0.0))

    # S_A @ v >= 0  ⟺  -S_A @ v <= 0
    result = linprog(
        c,
        A_ub=-S_A,
        b_ub=np.zeros(S_A.shape[0], dtype=float),
        bounds=bounds,
        method="highs",
    )
    if not result.success or result.x is None:
        return None
    return np.asarray(result.x, dtype=float)


def is_self_maintaining(
    A: Union[AbstractSet[Species], Iterable[Species]],
    reactions: Sequence[Reaction],
    stoich_matrix: Union[np.ndarray, Sequence[Sequence[float]]],
    *,
    species_order: Optional[Sequence[Species]] = None,
) -> bool:
    """Return True iff ``A`` admits a self-maintenance flux (linprog).

    Uses ``scipy.optimize.linprog`` (HiGHS) on the stoichiometric LP:
    ``v_r ≥ 1`` for every reaction with reactants ⊆ ``A``, ``v_r = 0``
    otherwise, and ``(S v)_s ≥ 0`` for all ``s ∈ A``.

    Parameters
    ----------
    A :
        Candidate species set.
    reactions :
        Sequence of ``(reactants, products)`` sets (applicability).
    stoich_matrix :
        Array of shape ``(len(species_order), len(reactions))``; column ``j``
        is the net stoichiometric change of reaction ``j``.
    species_order :
        Row labels of ``stoich_matrix``. If omitted, inferred as
        ``sorted(A ∪ species appearing in reactions)``.

    Returns
    -------
    bool

    Notes
    -----
    This Baustein does NOT fully formalize Autopoiesis; name
    chemical_organization not autopoiesis; word collisions with closure
    Baustein (PC=CQ) AND M27 FCA lattice — same words different objects,
    no shared base class.
    """
    return maintenance_flux(A, reactions, stoich_matrix, species_order=species_order) is not None


def is_organization(
    A: Union[AbstractSet[Species], Iterable[Species]],
    reactions: Sequence[Reaction],
    stoich_matrix: Union[np.ndarray, Sequence[Sequence[float]]],
    *,
    species_order: Optional[Sequence[Species]] = None,
) -> bool:
    """Return True iff ``A`` is an organization (reaction-closed and self-maintaining).

    Equivalent to ``is_reaction_closed(A, reactions) and
    is_self_maintaining(A, reactions, stoich_matrix, …)``.

    Notes
    -----
    This Baustein does NOT fully formalize Autopoiesis; name
    chemical_organization not autopoiesis; word collisions with closure
    Baustein (PC=CQ) AND M27 FCA lattice — same words different objects,
    no shared base class.
    """
    if not is_reaction_closed(A, reactions):
        return False
    return is_self_maintaining(
        A, reactions, stoich_matrix, species_order=species_order
    )


def as_report(
    A: Union[AbstractSet[Species], Iterable[Species]],
    reactions: Sequence[Reaction],
    stoich_matrix: Union[np.ndarray, Sequence[Sequence[float]]],
    *,
    species_order: Optional[Sequence[Species]] = None,
) -> Dict[str, Any]:
    """Structured report: closed / self-maintaining / organization + flux witness."""
    species = _as_species_set(A)
    rxns = _normalize_reactions(reactions)
    order = _infer_species_order(species, rxns, species_order)
    S = _validate_stoich(np.asarray(stoich_matrix, dtype=float), len(rxns), len(order))
    flux = maintenance_flux(species, rxns, S, species_order=order)
    reaction_ok = is_reaction_closed(species, rxns)
    self_ok = flux is not None
    Sv = None
    if flux is not None and species:
        idx = [order.index(s) for s in sorted(species, key=lambda x: order.index(x))]
        Sv = (S @ flux)[idx]
        Sv = [float(x) for x in Sv]
    return {
        "A": sorted(species, key=lambda x: str(x)),
        "n_reactions": len(rxns),
        "species_order": list(order),
        "is_reaction_closed": bool(reaction_ok),
        "is_self_maintaining": bool(self_ok),
        "is_organization": bool(reaction_ok and self_ok),
        "maintenance_flux": None if flux is None else [float(x) for x in flux],
        "Sv_on_A": Sv,
        "autopoiesis_scope_warning": AUTOPOIESIS_SCOPE_WARNING,
        "source": SOURCE,
    }


__all__ = [
    "AUTOPOIESIS_SCOPE_WARNING",
    "SOURCE",
    "is_reaction_closed",
    "is_self_maintaining",
    "is_organization",
    "maintenance_flux",
    "as_report",
]
