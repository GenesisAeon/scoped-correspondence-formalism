"""Controlled Markov correspondence under declared actions
(INTEGRATED_EXTENSION_ROADMAP.md Paket C2) -- response to
prompts/Answers/nicht_stationäre_Treiber/SCF_INTEGRATED_EXTENSION_IMPLEMENTATION_PLAN.md,
section 6.

For a finite controlled Markov chain with a row-stochastic MICRO kernel
``P^a`` per micro action ``a``, a row-stochastic MACRO kernel ``Q^b`` per
macro action ``b``, a deterministic partition ``C`` (a 0/1 indicator matrix,
one row per micro state, one column per macro class, exactly one 1 per row),
and an action map ``omega: micro action -> macro action``, EXACT controlled
correspondence means

    P^a C = C Q^{omega(a)}    for every declared micro action a.

Equivalently: for micro states ``i`` and ``i'`` in the SAME macro class, and
for any macro class ``k``, ``sum_{j in class k} P^a[i,j] == sum_{j in class
k} P^a[i',j]`` -- the aggregated ("lumped") transition probabilities out of a
class must not depend on WHICH micro state in that class you started from.
This is the classical exact/strong lumpability condition, applied per
declared action and consolidated through ``omega`` when several micro
actions share one macro action.

**No averaging that hides one failing action** (plan section 6): every
check below reports a result PER micro action, with the specific macro class
and micro row pair responsible for the largest violation -- never a single
pooled "average defect" number that could hide one badly-violating action
among several exact ones.

**Hand-verified control case** (independently reproduced in
``verify_controlled_correspondence.py`` before this module was written): 4
micro states, 2 classes ``{0,1}``, ``{2,3}``, partition
``C=[[1,0],[1,0],[0,1],[0,1]]``. Passive action ``(a,b)=(0.7,0.4)`` and
intervention action ``(a,b)=(0.8,0.1)`` both give an EXACT correspondence
for concrete, heterogeneous-within-class micro kernels, with
``Q_passive=[[0.7,0.3],[0.4,0.6]]`` and ``Q_intervention=[[0.8,0.2],
[0.1,0.9]]`` recovered exactly (max abs deviation ``~1e-16``). Replacing the
intervention's first two rows with ``[0.9,0,0.1,0]`` and ``[0,0.7,0,0.3]``
breaks exactness: state 0 reaches class 1 with probability 0.1, state 1 with
probability 0.3 -- no single macro row represents both; the best minimax
single-row candidate is 0.2, with maximum per-row error 0.1.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Hashable, Mapping, Optional, Sequence, Tuple

import numpy as np

from scoped_correspondence.errors import ScopeViolationError


def partition_indicator(labels: Sequence[Hashable]) -> Tuple[np.ndarray, Tuple[Hashable, ...]]:
    """Build the 0/1 indicator matrix ``C`` (n_states x n_classes) from a
    per-state class label list. Returns ``(C, class_order)``."""
    if len(labels) == 0:
        raise ScopeViolationError("labels must be non-empty")
    class_order = tuple(dict.fromkeys(labels))  # first-seen order, de-duplicated
    n = len(labels)
    k = len(class_order)
    C = np.zeros((n, k))
    index = {c: idx for idx, c in enumerate(class_order)}
    for i, lab in enumerate(labels):
        C[i, index[lab]] = 1.0
    return C, class_order


def _validate_partition(C: np.ndarray) -> None:
    if C.ndim != 2:
        raise ScopeViolationError(f"C must be 2-D; got shape {C.shape}")
    if not np.all((C == 0.0) | (C == 1.0)):
        raise ScopeViolationError("C must be a 0/1 indicator matrix")
    row_sums = C.sum(axis=1)
    if not np.allclose(row_sums, 1.0):
        raise ScopeViolationError("every micro state must belong to EXACTLY one macro class (each row of C sums to 1)")
    col_sums = C.sum(axis=0)
    if np.any(col_sums == 0.0):
        raise ScopeViolationError("every macro class must contain at least one micro state (no empty columns in C)")


def _validate_stochastic(P: np.ndarray, name: str) -> None:
    if P.ndim != 2 or P.shape[0] != P.shape[1]:
        raise ScopeViolationError(f"{name} must be a square micro kernel; got shape {P.shape}")
    if np.any(P < -1e-12):
        raise ScopeViolationError(f"{name} has a negative entry")
    if not np.allclose(P.sum(axis=1), 1.0, atol=1e-9):
        raise ScopeViolationError(f"{name} rows must sum to 1 (row-stochastic)")


@dataclass(frozen=True)
class ClassLumpabilityDefect:
    macro_class: int
    max_defect: float  # largest pairwise disagreement in block-sums within this class
    micro_row_pair: Tuple[int, int]  # the two micro states realizing max_defect
    macro_column: int  # which macro-class column the disagreement was largest in


@dataclass(frozen=True)
class ActionLumpabilityReport:
    micro_action: Hashable
    macro_action: Hashable
    exact: bool
    max_defect: float
    worst: Optional[ClassLumpabilityDefect]
    Q_estimate: np.ndarray  # per-class representative macro row (exact if exact=True, else the FIRST micro row's block-sums per class, for diagnostic display only)


def block_sums(P: np.ndarray, C: np.ndarray) -> np.ndarray:
    """``P @ C``: for every micro state, its vector of aggregated ("lumped")
    probabilities of landing in each macro class. Exact lumpability
    (restricted to ONE action) means every row of ``block_sums`` belonging to
    the same macro class is identical."""
    return P @ C


def check_lumpability(P: np.ndarray, C: np.ndarray, tol: float = 1e-9) -> Tuple[bool, float, Optional[ClassLumpabilityDefect], np.ndarray]:
    """Check exact lumpability of ONE micro kernel ``P`` under partition ``C``.
    Returns ``(exact, max_defect, worst_defect_or_None, Q_estimate)`` where
    ``Q_estimate`` is, per macro class, the block-sums row of the FIRST micro
    state in that class (the correct macro row when exact; a diagnostic
    "what would you get if you just picked one representative row" value
    otherwise -- never silently averaged across disagreeing rows)."""
    _validate_partition(C)
    _validate_stochastic(P, "P")
    n, k = C.shape
    bs = block_sums(P, C)
    class_members = [np.where(C[:, c] == 1.0)[0] for c in range(k)]
    Q_estimate = np.vstack([bs[members[0]] for members in class_members])

    max_defect = 0.0
    worst = None
    for c, members in enumerate(class_members):
        if len(members) < 2:
            continue
        sub = bs[members]  # (|class|, k)
        col_max = sub.max(axis=0)
        col_min = sub.min(axis=0)
        spread = col_max - col_min
        worst_col = int(np.argmax(spread))
        if spread[worst_col] > max_defect:
            max_defect = float(spread[worst_col])
            i_max = members[int(np.argmax(sub[:, worst_col]))]
            i_min = members[int(np.argmin(sub[:, worst_col]))]
            worst = ClassLumpabilityDefect(macro_class=c, max_defect=float(spread[worst_col]), micro_row_pair=(int(i_min), int(i_max)), macro_column=worst_col)
    return max_defect <= tol, max_defect, worst, Q_estimate


def check_controlled_correspondence(
    P_by_action: Mapping[Hashable, np.ndarray],
    C: np.ndarray,
    omega: Mapping[Hashable, Hashable],
    tol: float = 1e-9,
) -> Dict[Hashable, ActionLumpabilityReport]:
    """Check ``P^a C = C Q^{omega(a)}`` for EVERY declared micro action ``a``
    (module docstring). When several micro actions share one macro action via
    ``omega``, their induced ``Q`` estimates must ALSO agree with each other
    (not just be individually lumpable) -- checked by folding every action
    mapping to the same macro label into one combined lumpability check.

    Returns one report PER MICRO ACTION -- never a single pooled result.
    """
    _validate_partition(C)
    if set(P_by_action.keys()) != set(omega.keys()):
        raise ScopeViolationError("P_by_action and omega must declare the same set of micro actions")

    # Group micro actions by macro action so that shared-macro-action consistency
    # is checked jointly (a macro action's Q must be well-defined across ALL
    # micro actions that declare it, not just self-consistent within one).
    by_macro: Dict[Hashable, list] = {}
    for a, b in omega.items():
        by_macro.setdefault(b, []).append(a)

    reports: Dict[Hashable, ActionLumpabilityReport] = {}
    n = C.shape[0]
    for b, actions in by_macro.items():
        # Stack ALL micro states from ALL actions sharing this macro action into one
        # "super-check": treat each (action, state) pair as its own row, grouped by
        # macro class -- exact correspondence requires ALL of them to agree per class.
        all_block_sums = []
        owner = []  # (action, micro_state) per stacked row
        for a in actions:
            P = P_by_action[a]
            _validate_stochastic(P, f"P_by_action[{a!r}]")
            if P.shape[0] != n:
                raise ScopeViolationError(f"P_by_action[{a!r}] has {P.shape[0]} states, expected {n} (matching C)")
            bs = block_sums(P, C)
            all_block_sums.append(bs)
            owner.extend((a, i) for i in range(n))
        stacked = np.vstack(all_block_sums)  # (n_actions_sharing_b * n, k)

        k = C.shape[1]
        class_of_state = np.argmax(C, axis=1)
        # Build, for each macro class, the set of stacked-row indices belonging to it
        # (every action contributes its own micro states in the same class).
        class_row_indices = [
            [idx for idx, (a, i) in enumerate(owner) if class_of_state[i] == c] for c in range(k)
        ]

        max_defect_overall = 0.0
        worst_overall = None
        Q_estimate = np.vstack([stacked[class_row_indices[c][0]] for c in range(k)])
        for c in range(k):
            idxs = class_row_indices[c]
            if len(idxs) < 2:
                continue
            sub = stacked[idxs]
            spread = sub.max(axis=0) - sub.min(axis=0)
            worst_col = int(np.argmax(spread))
            if spread[worst_col] > max_defect_overall:
                max_defect_overall = float(spread[worst_col])
                local_max = idxs[int(np.argmax(sub[:, worst_col]))]
                local_min = idxs[int(np.argmin(sub[:, worst_col]))]
                worst_overall = ClassLumpabilityDefect(
                    macro_class=c, max_defect=float(spread[worst_col]),
                    micro_row_pair=(owner[local_min][1], owner[local_max][1]), macro_column=worst_col,
                )

        exact = max_defect_overall <= tol
        for a in actions:
            reports[a] = ActionLumpabilityReport(
                micro_action=a, macro_action=b, exact=exact,
                max_defect=max_defect_overall, worst=worst_overall, Q_estimate=Q_estimate,
            )
    return reports


def best_minimax_macro_row(P: np.ndarray, C: np.ndarray, macro_class: int) -> Tuple[np.ndarray, float]:
    """When a macro class is NOT exactly lumpable under ``P``, find the single
    macro row that MINIMIZES the maximum absolute error across that class's
    actual micro rows' block-sums (per-column midpoint of max/min -- the exact
    minimax point for the sup-norm). Returns ``(best_row, max_error)``."""
    _validate_partition(C)
    members = np.where(C[:, macro_class] == 1.0)[0]
    if len(members) == 0:
        raise ScopeViolationError(f"macro class {macro_class} has no micro states")
    bs = block_sums(P, C)[members]
    col_max, col_min = bs.max(axis=0), bs.min(axis=0)
    best_row = (col_max + col_min) / 2.0
    max_error = float(np.max((col_max - col_min) / 2.0))
    return best_row, max_error


def macro_events_from_micro_partition(C: np.ndarray) -> int:
    """Sanity utility: the number of DISTINCT macro "events" expressible as a
    union of whole partition blocks is ``2**k`` (every subset of the ``k``
    macro classes) -- returns ``k`` (the number of classes), from which a
    caller can enumerate. A micro event that is NOT a union of whole classes
    has no macro representation; see ``is_union_of_classes``."""
    _validate_partition(C)
    return int(C.shape[1])


def is_union_of_classes(micro_event: Sequence[int], C: np.ndarray) -> bool:
    """Check whether a set of micro states (``micro_event``) is exactly a
    UNION of whole partition blocks -- required for a "macro event" to be
    well-defined at all (plan section 6: events must be unions of whole
    partition blocks). A micro event that cuts across a class (contains some
    but not all of that class's states) has no valid macro representation."""
    _validate_partition(C)
    n = C.shape[0]
    event_set = set(micro_event)
    if not event_set.issubset(range(n)):
        raise ScopeViolationError(f"micro_event contains states outside range(0,{n})")
    class_of_state = np.argmax(C, axis=1)
    classes_touched = {class_of_state[i] for i in event_set}
    for c in classes_touched:
        full_class = set(np.where(class_of_state == c)[0].tolist())
        if not full_class.issubset(event_set):
            return False
    return True


def check_cost_consistency(
    cost_micro: Mapping[Tuple[int, Hashable], float],
    cost_macro: Mapping[Tuple[int, Hashable], float],
    C: np.ndarray,
    omega: Mapping[Hashable, Hashable],
    tol: float = 1e-9,
) -> Dict[Tuple[int, Hashable], float]:
    """Check ``c_X(x,a) == c_Y(C(x), omega(a))`` (plan section 6) for every
    declared ``(micro_state, micro_action)`` cost entry. Returns a dict of
    ``{(micro_state, micro_action): abs_error}`` for entries that VIOLATE
    ``tol`` -- empty if fully consistent. Never silently skips an entry whose
    macro counterpart is missing: that is itself reported as an infinite
    error (a genuinely undefined macro cost is not the same as a matching
    one)."""
    _validate_partition(C)
    class_of_state = np.argmax(C, axis=1)
    violations: Dict[Tuple[int, Hashable], float] = {}
    for (x, a), c_x in cost_micro.items():
        if a not in omega:
            raise ScopeViolationError(f"micro action {a!r} has no declared omega mapping")
        key_macro = (int(class_of_state[x]), omega[a])
        if key_macro not in cost_macro:
            violations[(x, a)] = float("inf")
            continue
        err = abs(c_x - cost_macro[key_macro])
        if err > tol:
            violations[(x, a)] = float(err)
    return violations


__all__ = [
    "partition_indicator",
    "block_sums",
    "check_lumpability",
    "ClassLumpabilityDefect",
    "ActionLumpabilityReport",
    "check_controlled_correspondence",
    "best_minimax_macro_row",
    "macro_events_from_micro_partition",
    "is_union_of_classes",
    "check_cost_consistency",
]
