"""Metarules: discrete rule-state update, priority T5 wrap, unobserved-m closure.

context_transformations.md section 6.

This module WRAPS ``membership.joint_control_set`` and CALLS
``closure.partition_matrix`` / ``is_exact_closure`` / ``closure_error`` /
``candidate_macro_kernel``. It does **not** mutate membership/core.py or
closure/core.py.

Scope: discrete / event metarule updates only — no continuous or stochastic
metarule ODEs; no general HMM aggregation theory beyond the A/B pair.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Literal, Mapping, Optional, Sequence, Tuple, Union

import numpy as np

from scoped_correspondence.errors import ScopeViolationError
from scoped_correspondence.membership import joint_control_set
from scoped_correspondence.closure import (
    candidate_macro_kernel,
    closure_error,
    is_exact_closure,
    partition_matrix,
)

Interval = Tuple[float, float]
ArrayLike = Union[np.ndarray, Sequence[Sequence[float]], Sequence[float]]

# Named distinguishable variants (§6 last sentence of the Metaregel paragraph).
DESCRIPTIVE_ONLY = "descriptive_only"
ENFORCED_RULE = "enforced_rule"
MetaRuleVariant = Literal["descriptive_only", "enforced_rule"]

_VARIANT_DOC = {
    DESCRIPTIVE_ONLY: (
        "descriptive-only m change → affects π (observation) first; "
        "does not by itself change interventions or the physical trajectory"
    ),
    ENFORCED_RULE: (
        "enforced rule → can change interventions and thereby the physical "
        "trajectory"
    ),
}


@dataclass(frozen=True)
class MetaRuleUpdate:
    """Typed wrapper for discrete / event metarule update m′ = H(m, z, c, u, t).

    context_transformations.md §6: a metarule may be fixed or evolve via a
    discrete update or event. Continuous / stochastic metarule dynamics are
    out of scope for this milestone.

    Two named distinguishable variants (same §6 sentence):

    * ``descriptive_only`` — observer / description choice; affects π first.
    * ``enforced_rule`` — actually enforced; can change interventions and
      the physical trajectory.
    """

    m_prev: object
    m_next: object
    z: object
    c: object
    u: object
    t: object
    variant: str
    H_name: str = "H"

    def __post_init__(self) -> None:
        if self.variant not in (DESCRIPTIVE_ONLY, ENFORCED_RULE):
            raise ScopeViolationError(
                f"MetaRuleUpdate.variant must be {DESCRIPTIVE_ONLY!r} or "
                f"{ENFORCED_RULE!r}; got {self.variant!r}"
            )

    @property
    def affects_observation_first(self) -> bool:
        return self.variant == DESCRIPTIVE_ONLY

    @property
    def can_change_interventions_and_trajectory(self) -> bool:
        return self.variant == ENFORCED_RULE

    @property
    def variant_documentation(self) -> str:
        return _VARIANT_DOC[self.variant]

    def as_report(self) -> Dict[str, object]:
        """Structured return naming both distinguishable variants."""
        return {
            "m_prev": self.m_prev,
            "m_next": self.m_next,
            "z": self.z,
            "c": self.c,
            "u": self.u,
            "t": self.t,
            "variant": self.variant,
            "H_name": self.H_name,
            "affects_observation_first": self.affects_observation_first,
            "can_change_interventions_and_trajectory": (
                self.can_change_interventions_and_trajectory
            ),
            "variant_documentation": self.variant_documentation,
            "named_variants": {
                DESCRIPTIVE_ONLY: _VARIANT_DOC[DESCRIPTIVE_ONLY],
                ENFORCED_RULE: _VARIANT_DOC[ENFORCED_RULE],
            },
            "source": (
                "context_transformations.md §6: "
                "m′=H(m,z,c,u,t) discrete/event; "
                "descriptive-only vs enforced rule"
            ),
        }

    @classmethod
    def apply(
        cls,
        H,
        m: object,
        z: object = None,
        c: object = None,
        u: object = None,
        t: object = None,
        *,
        variant: str,
        H_name: str = "H",
    ) -> "MetaRuleUpdate":
        """Evaluate discrete H and wrap as MetaRuleUpdate.

        ``H`` is a caller-supplied map ``H(m, z, c, u, t) -> m_next``
        (event / discrete only). ``variant`` selects the named interpretation.
        """
        if variant not in (DESCRIPTIVE_ONLY, ENFORCED_RULE):
            raise ScopeViolationError(
                f"variant must be {DESCRIPTIVE_ONLY!r} or {ENFORCED_RULE!r}; "
                f"got {variant!r}"
            )
        try:
            m_next = H(m, z, c, u, t)
        except TypeError:
            try:
                m_next = H(m, z, c, u)
            except TypeError:
                try:
                    m_next = H(m, z, c)
                except TypeError:
                    try:
                        m_next = H(m, z)
                    except TypeError:
                        m_next = H(m)
        return cls(
            m_prev=m,
            m_next=m_next,
            z=z,
            c=c,
            u=u,
            t=t,
            variant=variant,
            H_name=H_name,
        )


def _parse_drop_spec(
    m: object,
    U_alphas: Sequence[Interval],
    alpha_names: Optional[Sequence[str]],
) -> Tuple[int, str]:
    """Extract which U_α to drop from metarule state m (index and/or name)."""
    n = len(U_alphas)
    if n < 1:
        raise ScopeViolationError("U_alphas must be non-empty")

    drop_index: Optional[int] = None
    drop_name: Optional[str] = None

    if isinstance(m, Mapping):
        if "drop_alpha_index" in m:
            drop_index = int(m["drop_alpha_index"])
        elif "drop_index" in m:
            drop_index = int(m["drop_index"])
        if "drop_alpha_name" in m:
            drop_name = str(m["drop_alpha_name"])
        elif "drop_name" in m:
            drop_name = str(m["drop_name"])
        if drop_index is None and drop_name is None:
            raise ScopeViolationError(
                "priority metarule m must name drop_alpha_index/drop_index "
                "or drop_alpha_name/drop_name"
            )
    elif isinstance(m, (int, np.integer)):
        drop_index = int(m)
    else:
        raise ScopeViolationError(
            "priority metarule m must be an int index or a mapping with "
            "drop_alpha_index / drop_alpha_name; got "
            f"{type(m).__name__}"
        )

    names: Tuple[str, ...]
    if alpha_names is not None:
        if len(alpha_names) != n:
            raise ScopeViolationError(
                f"alpha_names length {len(alpha_names)} != len(U_alphas) {n}"
            )
        names = tuple(str(x) for x in alpha_names)
    else:
        names = tuple(f"alpha[{i}]" for i in range(n))

    if drop_index is None:
        # Resolve name → index
        assert drop_name is not None
        matches = [i for i, nm in enumerate(names) if nm == drop_name]
        if len(matches) != 1:
            raise ScopeViolationError(
                f"drop_alpha_name {drop_name!r} not uniquely found in "
                f"{list(names)}"
            )
        drop_index = matches[0]
    else:
        if not (0 <= drop_index < n):
            raise ScopeViolationError(
                f"drop_alpha_index {drop_index} out of range for "
                f"{n} U_alphas"
            )
        if drop_name is None:
            drop_name = names[drop_index]
        elif drop_name != names[drop_index]:
            raise ScopeViolationError(
                f"drop_alpha_name {drop_name!r} inconsistent with index "
                f"{drop_index} (name {names[drop_index]!r})"
            )

    return drop_index, drop_name


def priority_joint_control_set(
    U_physical: Interval,
    U_alphas: Sequence[Interval],
    m: object,
    *,
    alpha_names: Optional[Sequence[str]] = None,
) -> Dict[str, object]:
    """Priority wrap of T5 (context_transformations.md §6).

    1. Call ``membership.joint_control_set(U_physical, U_alphas)`` **unchanged**.
    2. Only if ``conflict=True`` (empty cut): apply priority metarule ``m`` that
       **explicitly drops one** ``U_α`` (index/name from ``m``) and recompute
       the intersection over the remaining sets.
    3. Report names **which** requirement was dropped and states that both
       requirements are **not** satisfied at once (§6 last sentence of T5).

    When the raw intersection is nonempty, the priority path is a no-op and
    the returned ``U_joint`` is identical to ``joint_control_set``.
    """
    raw = joint_control_set(U_physical, U_alphas)

    base = {
        "U_physical": raw["U_physical"],
        "U_alphas": raw["U_alphas"],
        "raw": raw,
        "source": (
            "context_transformations.md §6 T5 + priority metarule wrap; "
            "calls membership.joint_control_set unchanged"
        ),
    }

    if not raw["conflict"]:
        # Nonempty raw cut → priority identical to joint_control_set
        return {
            **base,
            "priority_applied": False,
            "conflict": False,
            "empty": False,
            "U_joint": raw["U_joint"],
            "dropped_requirement": None,
            "dropped_requirement_index": None,
            "dropped_requirement_name": None,
            "both_requirements_satisfied_simultaneously": True,
            "note": (
                "raw intersection nonempty; priority metarule not applied; "
                "U_joint identical to membership.joint_control_set"
            ),
        }

    # Empty cut — apply priority: explicitly drop one U_α
    drop_index, drop_name = _parse_drop_spec(m, U_alphas, alpha_names)
    remaining = [U for i, U in enumerate(U_alphas) if i != drop_index]
    if len(remaining) == 0:
        raise ScopeViolationError(
            "priority drop left no U_α; need at least one remaining "
            "requirement to recompute the intersection"
        )

    after = joint_control_set(U_physical, remaining)
    return {
        **base,
        "priority_applied": True,
        "conflict": after["conflict"],
        "empty": after["empty"],
        "U_joint": after["U_joint"],
        "U_alphas_after_drop": after["U_alphas"],
        "dropped_requirement": {
            "index": drop_index,
            "name": drop_name,
            "U_alpha": list(
                (float(U_alphas[drop_index][0]), float(U_alphas[drop_index][1]))
            ),
        },
        "dropped_requirement_index": drop_index,
        "dropped_requirement_name": drop_name,
        # §6: priority drops one requirement; it does NOT satisfy both at once
        "both_requirements_satisfied_simultaneously": False,
        "after_priority": after,
        "note": (
            f"raw U_joint empty (conflict); priority metarule explicitly "
            f"dropped requirement {drop_name!r} (index {drop_index}); "
            f"both original U_α requirements are NOT satisfied at once "
            f"(context_transformations.md §6)"
        ),
    }


def _joint_state_index(z: int, m: int) -> int:
    """Index in {0,1,2,3} for (z,m) ∈ {0,1}² ordered (0,0),(0,1),(1,0),(1,1)."""
    return 2 * int(z) + int(m)


def unobserved_metarule_breaks_closure() -> Dict[str, object]:
    """Unobserved discrete m can break otherwise closed z-dynamics (§6).

    Joint state (z, m) ∈ {0,1}² (4 states). Project to z via
    ``closure.partition_matrix`` (call only — same APIs as e04/e05).

    Case A — ``m = z`` (deterministic sync): exact closure, ``closure_error==0``.
    Case B — ``m`` independent fair coin modulating z transitions:
    not exact, ``closure_error > 0`` with a concrete number.

    No general HMM aggregation theory beyond this A/B pair.
    """
    # Ordering: (z,m) = (0,0), (0,1), (1,0), (1,1) → labels for z-projection
    labels = [0, 0, 1, 1]
    C, lift = partition_matrix(labels)

    # --- Case A: m=z synchronized ---
    # next_m = next_z; next_z depends only on current z (lumpable).
    # From z=0: stay at (0,0) w.p. 0.7, go to (1,1) w.p. 0.3
    # From z=1: stay at (1,1) w.p. 0.7, go to (0,0) w.p. 0.3
    P_A = np.zeros((4, 4), dtype=float)
    for s in (0, 1):  # current z=0
        P_A[s, _joint_state_index(0, 0)] = 0.7
        P_A[s, _joint_state_index(1, 1)] = 0.3
    for s in (2, 3):  # current z=1
        P_A[s, _joint_state_index(1, 1)] = 0.7
        P_A[s, _joint_state_index(0, 0)] = 0.3
    Q_A = candidate_macro_kernel(P_A, C, lift)
    exact_A = is_exact_closure(P_A, C, Q_A)
    err_A = closure_error(P_A, C, Q_A)

    # --- Case B: m independent fair coin; z' = z XOR m ---
    # m' ~ Bern(1/2) each step; current m modulates the z transition.
    P_B = np.zeros((4, 4), dtype=float)
    # (0,0): m=0 → z'=0; m' fair → (0,0), (0,1)
    P_B[0, 0] = 0.5
    P_B[0, 1] = 0.5
    # (0,1): m=1 → z'=1; m' fair → (1,0), (1,1)
    P_B[1, 2] = 0.5
    P_B[1, 3] = 0.5
    # (1,0): m=0 → z'=1; m' fair → (1,0), (1,1)
    P_B[2, 2] = 0.5
    P_B[2, 3] = 0.5
    # (1,1): m=1 → z'=0; m' fair → (0,0), (0,1)
    P_B[3, 0] = 0.5
    P_B[3, 1] = 0.5
    Q_B = candidate_macro_kernel(P_B, C, lift)
    exact_B = is_exact_closure(P_B, C, Q_B)
    err_B = closure_error(P_B, C, Q_B)

    return {
        "joint_states": ["(0,0)", "(0,1)", "(1,0)", "(1,1)"],
        "state_ordering": "index = 2*z + m",
        "projection": "z via closure.partition_matrix(labels=[0,0,1,1])",
        "C": C.tolist(),
        "lift": lift.tolist(),
        "case_A": {
            "description": "m=z synchronized (descriptive/enforced sync)",
            "P": P_A.tolist(),
            "Q": Q_A.tolist(),
            "is_exact_closure": bool(exact_A),
            "closure_error": float(err_A),
            "frame": "unobserved m equals z — projection to z is closed",
        },
        "case_B": {
            "description": (
                "m independent fair coin modulating z transitions "
                "(z' = z XOR m; m' ~ Bern(1/2))"
            ),
            "P": P_B.tolist(),
            "Q": Q_B.tolist(),
            "is_exact_closure": bool(exact_B),
            "closure_error": float(err_B),
            "frame": (
                "unobserved m — same-z microstates disagree on next macro; "
                "breaks closure"
            ),
        },
        "apis_called": [
            "closure.partition_matrix",
            "closure.candidate_macro_kernel",
            "closure.is_exact_closure",
            "closure.closure_error",
        ],
        "source": (
            "context_transformations.md §6: unobserved m can make an "
            "otherwise closed description unclosed; same closure APIs as e04/e05"
        ),
    }


__all__ = [
    "DESCRIPTIVE_ONLY",
    "ENFORCED_RULE",
    "MetaRuleUpdate",
    "priority_joint_control_set",
    "unobserved_metarule_breaks_closure",
]
