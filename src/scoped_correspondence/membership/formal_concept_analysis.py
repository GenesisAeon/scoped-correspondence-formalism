"""Formal Concept Analysis on MembershipMatrix (Milestone 27).

Binary entities×systems membership is a formal context (G, M, I) in the sense
of Ganter & Wille (1999): G = entities, M = systems, I = the ones of
``MembershipMatrix.matrix``. This module implements the Galois derivation
operators and enumerates formal concepts (A, B) with A↑ = B and B↓ = A.

Source: B. Ganter & R. Wille, *Formal Concept Analysis: Mathematical
Foundations*, Springer (1999), DOI 10.1007/978-3-642-59830-2.

Scope (explicit non-goals for this milestone):
  - No weighted / continuous membership — binary only, as MembershipMatrix.
  - No NextClosure (or other large-context algorithms): brute-force over the
    power set of the smaller side is enough for the matrix sizes in this repo
    (documented below on ``all_concepts``).
  - No link to the metarules package — membership-only extension.
  - Does not mutate ``membership/core.py``.
"""

from __future__ import annotations

from itertools import combinations
from typing import FrozenSet, Iterable, List, Sequence, Tuple

import numpy as np

from scoped_correspondence.errors import ScopeViolationError
from scoped_correspondence.membership.core import MembershipMatrix

DOI = "10.1007/978-3-642-59830-2"
SOURCE = (
    "Ganter & Wille, Formal Concept Analysis: Mathematical Foundations, "
    "Springer 1999, DOI 10.1007/978-3-642-59830-2"
)

IndexSet = FrozenSet[int]
Concept = Tuple[IndexSet, IndexSet]


def _as_index_set(
    indices: Iterable[int],
    *,
    n: int,
    kind: str,
) -> IndexSet:
    out: List[int] = []
    for i in indices:
        ii = int(i)
        if not (0 <= ii < n):
            raise ScopeViolationError(f"{kind} index {ii} out of range [0, {n})")
        out.append(ii)
    return frozenset(out)


def derive_up(entity_indices: Iterable[int], M: MembershipMatrix) -> IndexSet:
    """Intent operator A↑ — systems shared by every entity in A.

    A↑ = { α : ∀ e ∈ A, M[e, α] = 1 }.

    Vacuous case: A = ∅ ⇒ A↑ = all systems (every α satisfies the empty
    universal quantifier).
    """
    if not isinstance(M, MembershipMatrix):
        raise ScopeViolationError("derive_up expects a MembershipMatrix")
    A = _as_index_set(entity_indices, n=M.n_entities, kind="entity")
    if not A:
        return frozenset(range(M.n_systems))
    mat = M.matrix
    # Column α is in the intent iff every selected row has a 1 there.
    mask = np.ones(M.n_systems, dtype=bool)
    for e in A:
        mask &= mat[e] > 0.5
    return frozenset(int(i) for i in np.flatnonzero(mask))


def derive_down(system_indices: Iterable[int], M: MembershipMatrix) -> IndexSet:
    """Extent operator B↓ — entities that belong to every system in B.

    B↓ = { e : ∀ α ∈ B, M[e, α] = 1 }.

    Vacuous case: B = ∅ ⇒ B↓ = all entities.
    """
    if not isinstance(M, MembershipMatrix):
        raise ScopeViolationError("derive_down expects a MembershipMatrix")
    B = _as_index_set(system_indices, n=M.n_systems, kind="system")
    if not B:
        return frozenset(range(M.n_entities))
    mat = M.matrix
    mask = np.ones(M.n_entities, dtype=bool)
    for a in B:
        mask &= mat[:, a] > 0.5
    return frozenset(int(i) for i in np.flatnonzero(mask))


def is_concept(
    A: Iterable[int],
    B: Iterable[int],
    M: MembershipMatrix,
) -> bool:
    """True iff (A, B) is a formal concept: A↑ = B and B↓ = A."""
    if not isinstance(M, MembershipMatrix):
        raise ScopeViolationError("is_concept expects a MembershipMatrix")
    A_set = _as_index_set(A, n=M.n_entities, kind="entity")
    B_set = _as_index_set(B, n=M.n_systems, kind="system")
    return derive_up(A_set, M) == B_set and derive_down(B_set, M) == A_set


def _powerset(n: int) -> Iterable[IndexSet]:
    elems = range(n)
    return (
        frozenset(combo)
        for r in range(n + 1)
        for combo in combinations(elems, r)
    )


def all_concepts(M: MembershipMatrix) -> List[Concept]:
    """Enumerate all formal concepts (A, B) of MembershipMatrix M.

    A concept satisfies A↑ = B and B↓ = A (Ganter & Wille 1999). Enumeration
    is brute-force over subsets of the *smaller* side (entities or systems),
    closing each subset via the Galois connection. That is O(2^{min(n_e,n_a)}
    · poly(n_e, n_a)) — adequate for the small binary matrices in this repo.
    NextClosure / Close-by-One are deliberately *not* implemented here (out of
    scope for Milestone 27; see module docstring).

    Returns concepts ordered by |A| descending (largest extent first = lattice
    top first), with ties broken by sorted extent tuple.
    """
    if not isinstance(M, MembershipMatrix):
        raise ScopeViolationError("all_concepts expects a MembershipMatrix")

    concepts: dict[tuple[tuple[int, ...], tuple[int, ...]], Concept] = {}

    # Iterate the smaller power set; each closed pair is unique.
    if M.n_entities <= M.n_systems:
        for A0 in _powerset(M.n_entities):
            B = derive_up(A0, M)
            A = derive_down(B, M)
            key = (tuple(sorted(A)), tuple(sorted(B)))
            concepts[key] = (A, B)
    else:
        for B0 in _powerset(M.n_systems):
            A = derive_down(B0, M)
            B = derive_up(A, M)
            key = (tuple(sorted(A)), tuple(sorted(B)))
            concepts[key] = (A, B)

    ordered = sorted(
        concepts.values(),
        key=lambda ab: (-len(ab[0]), tuple(sorted(ab[0])), tuple(sorted(ab[1]))),
    )
    return ordered


def attribute_implication_from_extents(
    premise_system: int,
    conclusion_system: int,
    M: MembershipMatrix,
) -> dict:
    """Report whether membership in ``premise_system`` implies ``conclusion_system``.

    Attribute implication α → β holds in the context iff every entity that
    belongs to α also belongs to β, i.e. extent({α}) ⊆ extent({β}).
    Readable report for verification JSON (not a full implication basis).
    """
    if not isinstance(M, MembershipMatrix):
        raise ScopeViolationError("attribute_implication_from_extents expects MembershipMatrix")
    if not (0 <= premise_system < M.n_systems):
        raise ScopeViolationError(f"system index {premise_system} out of range")
    if not (0 <= conclusion_system < M.n_systems):
        raise ScopeViolationError(f"system index {conclusion_system} out of range")

    ext_p = derive_down({premise_system}, M)
    ext_c = derive_down({conclusion_system}, M)
    holds = ext_p <= ext_c

    def _label(i: int, names: Sequence[str], prefix: str) -> str:
        if names and i < len(names) and names[i]:
            return str(names[i])
        return f"{prefix}{i + 1}"

    s_names = M.system_names
    e_names = M.entity_names
    p_lab = _label(premise_system, s_names, "s")
    c_lab = _label(conclusion_system, s_names, "s")
    ext_p_lab = sorted(_label(e, e_names, "e") for e in ext_p)
    ext_c_lab = sorted(_label(e, e_names, "e") for e in ext_c)

    return {
        "premise_system_index": premise_system,
        "conclusion_system_index": conclusion_system,
        "premise_label": p_lab,
        "conclusion_label": c_lab,
        "extent_premise": sorted(ext_p),
        "extent_conclusion": sorted(ext_c),
        "extent_premise_labels": ext_p_lab,
        "extent_conclusion_labels": ext_c_lab,
        "holds": holds,
        "statement": (
            f"membership in {p_lab} implies membership in {c_lab}"
            if holds
            else f"membership in {p_lab} does not imply membership in {c_lab}"
        ),
        "from_concept_hint": (
            f"extent({{{p_lab}}}) = {{{', '.join(ext_p_lab)}}} "
            f"⊆ extent({{{c_lab}}}) = {{{', '.join(ext_c_lab)}}}"
        ),
        "source": SOURCE,
    }


__all__ = [
    "DOI",
    "SOURCE",
    "Concept",
    "IndexSet",
    "attribute_implication_from_extents",
    "all_concepts",
    "derive_down",
    "derive_up",
    "is_concept",
]
