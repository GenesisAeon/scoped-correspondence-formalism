"""Finite acyclic structural causal models (Paket J9, plan §15.1).

Endogenous variables have finite domains and DETERMINISTIC mechanisms;
randomness comes only from an explicit finite JOINT distribution of the
exogenous variables, so common exogenous causes (correlated U) are
representable and independence is never assumed silently.

A hard intervention do(V = v) replaces V's structural equation by the
constant v (v must lie in V's domain). Validation covers: DAG (no cycles,
parents are declared endogenous variables), mechanisms read ONLY their
declared parents and exogenous inputs (enforced by guarded mappings),
mechanism outputs lie in the declared domain (checked on EVERY evaluated
assignment -- parent combinations that are never reached under any
exogenous value or declared intervention are not evaluated),
exogenous probabilities are nonnegative and sum to exactly 1 (exact
Fractions) -- inputs that do not sum to one are an error, never normalised
-- and an explicit enumeration budget.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
from typing import Any, Callable, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

from scoped_correspondence.errors import ScopeViolationError

Assignment = Tuple[Any, ...]
Distribution = Dict[Assignment, Fraction]


class BudgetExceeded(RuntimeError):
    """Enumeration budget exhausted -- no conclusion drawn."""


class _Guarded(dict):
    def __init__(self, data: Mapping[str, Any], allowed: Iterable[str], owner: str, what: str):
        super().__init__(data)
        self._allowed = set(allowed)
        self._owner, self._what = owner, what

    def __getitem__(self, k):
        if k not in self._allowed:
            raise ScopeViolationError(f"mechanism of {self._owner!r} read undeclared {self._what} {k!r}")
        return super().__getitem__(k)

    def get(self, k, default=None):
        return self[k] if k in self else default


@dataclass(frozen=True)
class Mechanism:
    parents: Tuple[str, ...]
    exogenous: Tuple[str, ...]
    fn: Callable[[Mapping[str, Any], Mapping[str, Any]], Any]


@dataclass(frozen=True)
class FiniteSCM:
    name: str
    order: Tuple[str, ...]  # declared endogenous variable order (output tuple order)
    domains: Mapping[str, Tuple[Any, ...]]
    mechanisms: Mapping[str, Mechanism]
    exogenous_names: Tuple[str, ...]
    exogenous_distribution: Mapping[Assignment, Fraction]  # joint distribution over exogenous_names
    budget: int = 100_000

    def __post_init__(self) -> None:
        if set(self.order) != set(self.domains) or set(self.order) != set(self.mechanisms):
            raise ScopeViolationError("order, domains and mechanisms must declare the same endogenous variables")
        for v, m in self.mechanisms.items():
            bad = set(m.parents) - set(self.order)
            if bad:
                raise ScopeViolationError(f"{v}: parents {sorted(bad)} are not endogenous variables")
            if v in m.parents:
                raise ScopeViolationError(f"{v}: self-loop")
            badu = set(m.exogenous) - set(self.exogenous_names)
            if badu:
                raise ScopeViolationError(f"{v}: undeclared exogenous inputs {sorted(badu)}")
        self.topological_order()  # raises on cycles
        total = Fraction(0)
        for u, p in self.exogenous_distribution.items():
            if len(u) != len(self.exogenous_names):
                raise ScopeViolationError("exogenous assignment length mismatch")
            if isinstance(p, bool) or not isinstance(p, (int, Fraction)):
                raise ScopeViolationError("exogenous probabilities must be exact (int/Fraction)")
            if p < 0:
                raise ScopeViolationError("negative exogenous probability")
            total += p
        if total != 1:
            raise ScopeViolationError(f"exogenous probabilities sum to {total}, not 1 (never normalised silently)")
        if len(self.exogenous_distribution) * max(1, len(self.order)) > self.budget:
            raise BudgetExceeded("model enumeration exceeds the declared budget")

    def topological_order(self) -> List[str]:
        indeg = {v: len(self.mechanisms[v].parents) for v in self.order}
        children: Dict[str, List[str]] = {v: [] for v in self.order}
        for v in self.order:
            for p in self.mechanisms[v].parents:
                children[p].append(v)
        ready = [v for v in self.order if indeg[v] == 0]
        out = []
        while ready:
            v = ready.pop(0)
            out.append(v)
            for c in children[v]:
                indeg[c] -= 1
                if indeg[c] == 0:
                    ready.append(c)
        if len(out) != len(self.order):
            raise ScopeViolationError("the causal graph has a cycle (not a DAG)")
        return out

    def edges(self) -> List[Tuple[str, str]]:
        return [(p, v) for v in self.order for p in self.mechanisms[v].parents]

    def solve(self, u: Assignment, do: Optional[Mapping[str, Any]] = None) -> Assignment:
        do = dict(do or {})
        uval = dict(zip(self.exogenous_names, u))
        val: Dict[str, Any] = {}
        for v in self.topological_order():
            if v in do:
                val[v] = do[v]
                continue
            m = self.mechanisms[v]
            x = m.fn(_Guarded({p: val[p] for p in m.parents}, m.parents, v, "parent"),
                     _Guarded({k: uval[k] for k in m.exogenous}, m.exogenous, v, "exogenous input"))
            if x not in self.domains[v]:
                raise ScopeViolationError(f"mechanism of {v!r} produced {x!r} outside its domain {self.domains[v]}")
            val[v] = x
        return tuple(val[v] for v in self.order)


def validate_intervention(model: FiniteSCM, do: Mapping[str, Any]) -> None:
    for k, v in do.items():
        if k not in model.domains:
            raise ScopeViolationError(f"intervention on unknown variable {k!r}")
        if v not in model.domains[k]:
            raise ScopeViolationError(f"intervention value {v!r} outside the domain of {k!r}")


def interventional_distribution(model: FiniteSCM, do: Optional[Mapping[str, Any]] = None, *, budget: Optional[int] = None) -> Distribution:
    do = dict(do or {})
    validate_intervention(model, do)
    limit = model.budget if budget is None else budget
    if len(model.exogenous_distribution) > limit:
        raise BudgetExceeded(f"{len(model.exogenous_distribution)} exogenous combinations exceed the budget {limit}")
    out: Distribution = {}
    for u, p in model.exogenous_distribution.items():
        if p == 0:
            continue
        s = model.solve(u, do)
        out[s] = out.get(s, Fraction(0)) + p
    return out


def pushforward_distribution(dist: Mapping[Assignment, Fraction], tau: Callable[[Assignment], Assignment]) -> Distribution:
    out: Distribution = {}
    for s, p in dist.items():
        k = tau(s)
        out[k] = out.get(k, Fraction(0)) + p
    return out


def marginal(dist: Mapping[Assignment, Fraction], index: int) -> Dict[Any, Fraction]:
    out: Dict[Any, Fraction] = {}
    for s, p in dist.items():
        out[s[index]] = out.get(s[index], Fraction(0)) + p
    return out


def total_variation(p: Mapping, q: Mapping) -> Fraction:
    return sum((abs(Fraction(p.get(k, 0)) - Fraction(q.get(k, 0))) for k in set(p) | set(q)), Fraction(0)) / 2


def independent_exogenous(**marginals: Mapping[Any, Fraction]) -> Tuple[Tuple[str, ...], Dict[Assignment, Fraction]]:
    """Convenience for EXPLICITLY declared independent exogenous variables:
    returns (names, product distribution)."""
    names = tuple(marginals)
    dist: Dict[Assignment, Fraction] = {(): Fraction(1)}
    for n in names:
        nxt: Dict[Assignment, Fraction] = {}
        for a, p in dist.items():
            for v, q in marginals[n].items():
                nxt[a + (v,)] = p * Fraction(q)
        dist = nxt
    return names, dist


__all__ = ["BudgetExceeded", "Mechanism", "FiniteSCM", "validate_intervention", "interventional_distribution",
           "pushforward_distribution", "marginal", "total_variation", "independent_exogenous"]
