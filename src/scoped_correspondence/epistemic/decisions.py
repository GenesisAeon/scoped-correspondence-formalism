"""H4: finite decisions under declared uncertainty (Plan §4.5-4.6; K5, K6).

`uniform_safe_actions` separates two genuinely different statements about
a fiber `F` (Plan §4.5):

    statewise-feasible:  forall w in F, exists u: safe(w, u)   (a
                         state-dependent intervention may serve)
    uniformly feasible:  exists u, forall w in F: safe(w, u)   (ONE shared
                         intervention must serve every state in F)

`U_uniform(F) = intersection_{w in F} U_safe(w)`. Statewise feasibility
does NOT imply uniform feasibility (K5: at B=1 every state in the fiber
is individually controllable, but no single shared intervention serves
all three -- a common budget-1 intervention is only possible from B=2).

`compare_decisions` implements three explicitly DIFFERENT, non-
interchangeable comparison criteria over a finite, fully declared loss
table L(a, w) (Plan §4.6): minimax (worst-case loss), minimax-regret
(worst-case regret against the best achievable loss per state), and
expected loss (requires an EXPLICITLY supplied probability distribution
-- the number of candidate states is never treated as an implicit
uniform prior). K6 shows minimax and minimax-regret can disagree on the
SAME table, so neither may silently stand in for the other.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from fractions import Fraction
from typing import Any, Callable, Dict, Hashable, Mapping, Optional, Sequence, Tuple, Union

from scoped_correspondence.errors import ScopeViolationError

from .observation_fibers import FiberReport
from .records import PredicateEvaluationError, evaluate_bool

Number = Union[int, float, Fraction]

CRITERIA = ("minimax", "minimax_regret", "expected_loss")


def _require_finite(v: Number, where: str) -> None:
    if isinstance(v, (int, Fraction)):
        return
    if isinstance(v, float):
        if not math.isfinite(v):
            raise ScopeViolationError(f"{where} must be finite, got {v!r}")
        return
    raise ScopeViolationError(f"{where} must be int, float, or Fraction, got {type(v).__name__}")


@dataclass(frozen=True)
class ActionSetReport:
    fiber_size: int
    actions_considered: Tuple[Any, ...]
    per_state_safe_actions: Tuple[Tuple[Any, Tuple[Any, ...]], ...]
    statewise_feasible: bool
    uniformly_feasible: bool
    uniform_safe_actions: Tuple[Any, ...]
    domain_coverage: str = "complete"
    notes: Tuple[str, ...] = field(default_factory=tuple)


def uniform_safe_actions(
    fiber: FiberReport,
    actions: Sequence[Any],
    safety: Callable[[Any, Any], bool],
) -> ActionSetReport:
    """`U_uniform(F)` plus the statewise/uniform feasibility distinction."""
    if not fiber.search_complete:
        return ActionSetReport(
            fiber_size=fiber.n_fiber, actions_considered=tuple(actions), per_state_safe_actions=(),
            statewise_feasible=False, uniformly_feasible=False, uniform_safe_actions=(),
            domain_coverage=fiber.domain_coverage,
            notes=("the fiber was built from an incomplete scan -- no feasibility claim can be made",),
        )
    if fiber.empty_fiber:
        return ActionSetReport(
            fiber_size=0, actions_considered=tuple(actions), per_state_safe_actions=(),
            statewise_feasible=False, uniformly_feasible=False, uniform_safe_actions=(),
            domain_coverage=fiber.domain_coverage,
            notes=("empty fiber -- observation/model mismatch, feasibility is undefined, not vacuously true",),
        )

    per_state = []
    intersection = set(actions)
    statewise_ok = True
    n_safety_errors = 0
    for w in fiber.fiber:
        safe_here_list = []
        for u in actions:
            try:
                if evaluate_bool(safety, w, u):
                    safe_here_list.append(u)
            except PredicateEvaluationError:
                n_safety_errors += 1
                # An error is NEVER treated as "safe" -- it is excluded,
                # same as False, but counted separately so it is visible
                # rather than silently indistinguishable from a genuine
                # negative (SCF_REVIEW_H0_H7_9dde420.md R3).
        safe_here = tuple(safe_here_list)
        per_state.append((w, safe_here))
        if len(safe_here) == 0:
            statewise_ok = False
        intersection &= set(safe_here)

    uniform_actions = tuple(u for u in actions if u in intersection)
    uniformly_ok = len(uniform_actions) > 0

    notes = ()
    if statewise_ok and not uniformly_ok:
        notes = (
            "statewise-feasible but NOT uniformly feasible: every state individually has a safe action, "
            "but no single shared action is safe for all of them (Plan §4.5)",
        )
    elif not statewise_ok:
        notes = ("at least one state in the fiber has NO safe action at all -- statewise infeasible",)
    if n_safety_errors > 0:
        notes = notes + (
            f"safety predicate returned a non-bool value or raised for {n_safety_errors} (state, action) "
            "pair(s) -- treated as NOT safe, never as safe, but this is an evaluation error, not a "
            "confirmed negative",
        )

    return ActionSetReport(
        fiber_size=fiber.n_fiber, actions_considered=tuple(actions), per_state_safe_actions=tuple(per_state),
        statewise_feasible=statewise_ok, uniformly_feasible=uniformly_ok, uniform_safe_actions=uniform_actions,
        domain_coverage=fiber.domain_coverage, notes=notes,
    )


@dataclass(frozen=True)
class DecisionReport:
    criterion: str
    chosen_actions: Tuple[Hashable, ...]
    scores: Tuple[Tuple[Hashable, Number], ...]
    notes: Tuple[str, ...] = field(default_factory=tuple)


def compare_decisions(
    loss_matrix: Mapping[Hashable, Mapping[Hashable, Number]],
    *,
    criterion: str,
    probabilities: Optional[Mapping[Hashable, Number]] = None,
) -> DecisionReport:
    if criterion not in CRITERIA:
        raise ScopeViolationError(f"criterion must be one of {CRITERIA}, got {criterion!r}")
    actions = tuple(loss_matrix.keys())
    if len(actions) == 0:
        raise ScopeViolationError("loss_matrix must declare at least one action")

    state_sets = {frozenset(loss_matrix[a].keys()) for a in actions}
    if len(state_sets) != 1:
        raise ScopeViolationError("every action must declare losses for exactly the same set of states")
    states = tuple(loss_matrix[actions[0]].keys())
    if len(states) == 0:
        raise ScopeViolationError("loss_matrix must declare at least one state")

    for a in actions:
        for w in states:
            _require_finite(loss_matrix[a][w], f"loss_matrix[{a!r}][{w!r}]")

    scores: Dict[Hashable, Number] = {}
    if criterion == "minimax":
        for a in actions:
            scores[a] = max(loss_matrix[a][w] for w in states)
    elif criterion == "minimax_regret":
        best_per_state = {w: min(loss_matrix[a][w] for a in actions) for w in states}
        for a in actions:
            scores[a] = max(loss_matrix[a][w] - best_per_state[w] for w in states)
    else:  # expected_loss
        if probabilities is None:
            raise ScopeViolationError("criterion='expected_loss' requires explicit probabilities -- "
                                       "the number of candidate states is never an implicit uniform prior")
        if set(probabilities.keys()) != set(states):
            raise ScopeViolationError("probabilities must be declared for exactly the same states as loss_matrix")
        for w, p in probabilities.items():
            _require_finite(p, f"probabilities[{w!r}]")
            if p < 0 or p > 1:
                raise ScopeViolationError(f"probabilities[{w!r}]={p!r} must be in [0,1]")
        total = sum(probabilities.values())
        total_ok = (total == 1) if isinstance(total, (int, Fraction)) else math.isclose(float(total), 1.0, abs_tol=1e-9)
        if not total_ok:
            raise ScopeViolationError(f"probabilities must sum to 1, got {total!r}")
        for a in actions:
            scores[a] = sum(probabilities[w] * loss_matrix[a][w] for w in states)

    for a in actions:
        # Every INPUT loss was already checked finite above, but the
        # DERIVED score (a max/regret/expected-value combination) can
        # still overflow to +-inf in float arithmetic even from finite
        # inputs (e.g. subtracting two ~1e308 losses of opposite sign) --
        # that overflow must be a clear error, never a computed "tie"
        # between actions that were never actually equal
        # (SCF_REVIEW_H0_H7_9dde420.md R3 numeric addendum).
        if isinstance(scores[a], float) and not math.isfinite(scores[a]):
            raise ScopeViolationError(
                f"computed {criterion} score for action {a!r} is non-finite ({scores[a]!r}) -- likely float "
                "overflow from the loss magnitudes involved, not a genuine result; use smaller/scaled losses "
                "or exact (int/Fraction) arithmetic"
            )

    best_score = min(scores.values())
    chosen = tuple(a for a in actions if scores[a] == best_score)
    notes = ()
    if len(chosen) > 1:
        notes = (f"tie between {len(chosen)} actions at score {best_score!r} under criterion={criterion!r}",)
    return DecisionReport(
        criterion=criterion, chosen_actions=chosen,
        scores=tuple((a, scores[a]) for a in actions), notes=notes,
    )
