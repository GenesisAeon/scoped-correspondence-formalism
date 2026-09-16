"""Membership formulas: M_eα, double-count guard, joint control set T5.

context_transformations.md sections 1, 2, and 6.
Not a viability-kernel solver; not weighted membership.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, Optional, Sequence, Tuple, Union

import numpy as np

from scoped_correspondence.errors import ScopeViolationError

ArrayLike = Union[np.ndarray, Sequence[Sequence[float]], Sequence[float]]
Interval = Tuple[float, float]


def _as_binary_matrix(a: ArrayLike) -> np.ndarray:
    m = np.asarray(a, dtype=float)
    if m.ndim != 2:
        raise ScopeViolationError(f"MembershipMatrix: expected 2D matrix, got shape {m.shape}")
    if m.size == 0:
        raise ScopeViolationError("MembershipMatrix: matrix must be non-empty")
    if not np.isfinite(m).all():
        raise ScopeViolationError("MembershipMatrix: matrix must be finite")
    # Binary only in this milestone (context_transformations.md section 1).
    if not np.isin(m, (0.0, 1.0)).all():
        raise ScopeViolationError(
            "MembershipMatrix: M_eα must be binary in {0,1}. "
            "Weighted entries in [0,1] are NOT probability or stock-share weights "
            "and need a separate meaning (context_transformations.md section 1); "
            "they are out of scope for this milestone."
        )
    return m.astype(float)


@dataclass(frozen=True)
class MembershipMatrix:
    """Binary membership M_{eα}(t) ∈ {0,1} (entities × systems).

    context_transformations.md section 1: multiple 1s per row are allowed
    (overlapping membership). Distinct from closure ``partition_matrix`` C,
    which assigns *states* to observation classes with one 1 per row — no
    shared base class and no cast between the two (same discipline as
    ``AijInfluence`` vs ``LijTransport`` in coupling).

    M is NOT a probability or stock-share matrix. A weighted variant would
    need its own meaning for the weights; only binary values are covered here.
    """

    matrix: np.ndarray
    entity_names: Tuple[str, ...] = ()
    system_names: Tuple[str, ...] = ()

    def __post_init__(self) -> None:
        mat = _as_binary_matrix(self.matrix)
        object.__setattr__(self, "matrix", mat)
        n_e, n_a = mat.shape
        if self.entity_names and len(self.entity_names) != n_e:
            raise ScopeViolationError(
                f"entity_names length {len(self.entity_names)} != n_entities {n_e}"
            )
        if self.system_names and len(self.system_names) != n_a:
            raise ScopeViolationError(
                f"system_names length {len(self.system_names)} != n_systems {n_a}"
            )

    @property
    def n_entities(self) -> int:
        return int(self.matrix.shape[0])

    @property
    def n_systems(self) -> int:
        return int(self.matrix.shape[1])

    def members_of(self, alpha: int) -> np.ndarray:
        """Entity indices with M[e, α] = 1."""
        if not (0 <= alpha < self.n_systems):
            raise ScopeViolationError(f"system index {alpha} out of range")
        return np.flatnonzero(self.matrix[:, alpha] > 0.5)

    def systems_of(self, entity: int) -> np.ndarray:
        """System indices with M[e, α] = 1."""
        if not (0 <= entity < self.n_entities):
            raise ScopeViolationError(f"entity index {entity} out of range")
        return np.flatnonzero(self.matrix[entity] > 0.5)


def view(
    pi: Callable[..., object],
    z: object,
    c: object = None,
    t: object = None,
    *,
    alpha: Optional[int] = None,
) -> object:
    """Generic projection y_α = π_α(z, c, t) (context_transformations.md §1).

    Call mechanism / signature only — no new physics. ``pi`` is the caller-
    supplied projection for view α; ``alpha`` is optional metadata for the
    caller and is not interpreted here.
    """
    del alpha  # metadata for callers / docs; projection is already α-specific
    try:
        return pi(z, c, t)
    except TypeError:
        # Allow projections that omit unused context/time arguments.
        try:
            return pi(z, c)
        except TypeError:
            return pi(z)


def double_count_stocks(
    M: MembershipMatrix,
    x: ArrayLike,
) -> Dict[str, object]:
    """Naive vs correct stock totals under overlapping membership (§1 table / §2).

    Physical stock x_e is the same under a fixed measurement definition and
    time. Naive per-system sums ``M.T @ x`` double-count multi-members; the
    correct physical total counts each entity once: ``sum(x)``.

    Returns both sides and the explicit double-count difference.
    """
    x_a = np.asarray(x, dtype=float).reshape(-1)
    if x_a.shape != (M.n_entities,):
        raise ScopeViolationError(
            f"x length {x_a.shape[0]} != n_entities {M.n_entities}"
        )
    if not np.isfinite(x_a).all():
        raise ScopeViolationError("x must be finite")

    per_system_naive = M.matrix.T @ x_a
    total_naive = float(per_system_naive.sum())
    total_correct = float(x_a.sum())
    # Extra weight from multi-membership: (row_sum - 1)_+ per entity
    membership_counts = M.matrix.sum(axis=1)
    double_count_mass = float(((membership_counts - 1.0).clip(min=0.0) * x_a).sum())
    return {
        "x": x_a.tolist(),
        "M": M.matrix.tolist(),
        "per_system_naive": per_system_naive.tolist(),
        "total_naive": total_naive,
        "total_correct": total_correct,
        "double_count_difference": float(total_naive - total_correct),
        "double_count_mass": double_count_mass,
        "source": "context_transformations.md sections 1-2 (additive balance / no double-count)",
    }


def _normalize_interval(interval: Interval, *, name: str) -> Interval:
    if len(interval) != 2:
        raise ScopeViolationError(f"{name}: interval must be (lo, hi); got {interval!r}")
    lo, hi = float(interval[0]), float(interval[1])
    if not (np.isfinite(lo) and np.isfinite(hi)):
        raise ScopeViolationError(f"{name}: interval bounds must be finite")
    if lo > hi:
        # Already empty as an interval representation.
        return (lo, hi)
    return (lo, hi)


def joint_control_set(
    U_physical: Interval,
    U_alphas: Sequence[Interval],
) -> Dict[str, object]:
    """Joint executable control set T5 (context_transformations.md section 6):

        U_joint = U_physical ∩ (∩_α U_α)

    Interval / axis-aligned box case only (one shared scalar control
    coordinate). No general polytope library.

    Design choice — empty intersection → ``conflict: True`` (not raise):
    An empty U_joint is a domain-level rule/resource contradiction (§6), not
    an API misuse. Callers must inspect ``conflict`` / ``empty`` the same way
    ``shared_budget_conflict`` reports ``conflict: bool``. ``ScopeViolationError``
    is reserved for malformed inputs (non-finite bounds, bad shapes).
    """
    phys = _normalize_interval(U_physical, name="U_physical")
    if len(U_alphas) == 0:
        raise ScopeViolationError("U_alphas must contain at least one system control set")

    lo, hi = phys
    intervals = [phys]
    for i, U_a in enumerate(U_alphas):
        ia = _normalize_interval(U_a, name=f"U_alphas[{i}]")
        intervals.append(ia)
        lo = max(lo, ia[0])
        hi = min(hi, ia[1])

    empty = bool(lo > hi)
    joint: Optional[Interval] = None if empty else (float(lo), float(hi))
    return {
        "U_physical": list(phys),
        "U_alphas": [list(u) for u in intervals[1:]],
        "U_joint": None if joint is None else list(joint),
        "empty": empty,
        "conflict": empty,
        "source": "context_transformations.md section 6 formula T5",
    }


def t10_via_membership(
    M: Optional[MembershipMatrix] = None,
) -> Dict[str, object]:
    """Reproduce t10 shared-budget numbers via a MembershipMatrix (§6 cross-check).

    Two entities belong to exactly one common system (M shape (2,1), both 1).
    Action demands and conflict are obtained by calling
    ``viability.core.shared_budget_conflict`` unchanged — membership only
    declares the shared-system relation; it does not rewrite viability.

    Default numbers (legacy t10 / worked_example_viability.md section 5):
        r=[1,1], e=[0.2,0.2], W=[0.7,0.7], k=0.5, U=0.75
        → a=[0.5,0.5], required_joint=1, conflict=True
    """
    from scoped_correspondence.viability.core import shared_budget_conflict

    if M is None:
        M = MembershipMatrix(
            [[1], [1]],
            entity_names=("e0", "e1"),
            system_names=("shared",),
        )
    else:
        if M.n_entities != 2 or M.n_systems != 1:
            raise ScopeViolationError(
                "t10_via_membership expects M shape (2,1) — two entities in "
                f"exactly one common system; got {M.matrix.shape}"
            )
        if not np.array_equal(M.matrix, np.ones((2, 1))):
            raise ScopeViolationError(
                "t10_via_membership expects both entities members of the "
                f"single system; got M={M.matrix.tolist()}"
            )

    report = shared_budget_conflict(
        r=[1.0, 1.0],
        e=[0.2, 0.2],
        W=[0.7, 0.7],
        k=0.5,
        U=0.75,
        b=[0.0, 0.0],
    )
    return {
        "M": M.matrix.tolist(),
        "entity_names": list(M.entity_names) if M.entity_names else ["e0", "e1"],
        "system_names": list(M.system_names) if M.system_names else ["shared"],
        "a": report["a"],
        "required_joint_budget": report["required_joint_budget"],
        "available_budget": report["available_budget"],
        "standalone_margin": report["standalone_margin"],
        "conflict": report["conflict"],
        "viability_report": report,
        "source": (
            "MembershipMatrix shared-system relation + "
            "viability.core.shared_budget_conflict (t10 cross-check); "
            "context_transformations.md section 6 / worked_example_viability.md section 5"
        ),
    }


__all__ = [
    "MembershipMatrix",
    "double_count_stocks",
    "joint_control_set",
    "t10_via_membership",
    "view",
]
