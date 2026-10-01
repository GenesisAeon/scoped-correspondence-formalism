"""Finite DAGs, d-separation and S-admissibility (Paket J10, plan §16.1).

d-separation via the moralised ancestral graph (Lauritzen): X _||_ Y | Z in a
DAG G iff X and Y are separated by Z in the moral graph of the ancestral set
of X u Y u Z. Explicit latent nodes are allowed (they are ordinary nodes
that are never conditioned on). General ADMG / sID machinery is NOT part of
this package.

do(X) graph G_{bar X}: all edges INTO X removed (not edges out of X).

S-admissibility (Pearl & Bareinboim 2014, S15): Z is S-admissible for the
effect of X on Y iff (Y _||_ S | X, Z) in G_{bar X}. The check evaluates a
DECLARED selection diagram; it does not learn the diagram from data.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, FrozenSet, Iterable, List, Sequence, Set, Tuple

from scoped_correspondence.errors import ScopeViolationError


@dataclass(frozen=True)
class DAG:
    nodes: FrozenSet[str]
    edges: FrozenSet[Tuple[str, str]]
    latent: FrozenSet[str] = frozenset()

    def __post_init__(self) -> None:
        for a, b in self.edges:
            if a not in self.nodes or b not in self.nodes:
                raise ScopeViolationError(f"edge {a}->{b} uses an undeclared node")
            if a == b:
                raise ScopeViolationError("self-loop")
        if not self.latent <= self.nodes:
            raise ScopeViolationError("latent nodes must be declared nodes")
        # acyclicity
        indeg = {n: 0 for n in self.nodes}
        for _, b in self.edges:
            indeg[b] += 1
        ready = [n for n in self.nodes if indeg[n] == 0]
        seen = 0
        while ready:
            n = ready.pop()
            seen += 1
            for a, b in self.edges:
                if a == n:
                    indeg[b] -= 1
                    if indeg[b] == 0:
                        ready.append(b)
        if seen != len(self.nodes):
            raise ScopeViolationError("graph has a cycle (not a DAG)")

    @classmethod
    def from_edges(cls, edges: Iterable[Tuple[str, str]], nodes: Iterable[str] = (), latent: Iterable[str] = ()) -> "DAG":
        e = frozenset(edges)
        n = set(nodes) | {x for ab in e for x in ab}
        return cls(frozenset(n), e, frozenset(latent))

    def parents(self, n: str) -> Set[str]:
        return {a for a, b in self.edges if b == n}

    def descendants(self, n: str) -> Set[str]:
        out, stack = set(), [n]
        while stack:
            cur = stack.pop()
            for a, b in self.edges:
                if a == cur and b not in out:
                    out.add(b)
                    stack.append(b)
        return out

    def ancestors_of(self, nodes: Iterable[str]) -> Set[str]:
        out, stack = set(nodes), list(nodes)
        while stack:
            cur = stack.pop()
            for p in self.parents(cur):
                if p not in out:
                    out.add(p)
                    stack.append(p)
        return out

    def do_graph(self, intervened: Iterable[str]) -> "DAG":
        """G_{bar X}: remove every edge INTO an intervened node."""
        xs = set(intervened)
        unknown = xs - self.nodes
        if unknown:
            raise ScopeViolationError(f"intervened nodes {sorted(unknown)} not in the graph")
        return DAG(self.nodes, frozenset((a, b) for a, b in self.edges if b not in xs), self.latent)


def d_separated(g: DAG, xs: Iterable[str], ys: Iterable[str], zs: Iterable[str]) -> bool:
    X, Y, Z = set(xs), set(ys), set(zs)
    for s in (X, Y, Z):
        if not s <= g.nodes:
            raise ScopeViolationError(f"unknown nodes {sorted(s - g.nodes)}")
    if X & Y:
        return False
    anc = g.ancestors_of(X | Y | Z)
    adj: Dict[str, Set[str]] = {n: set() for n in anc}
    for a, b in g.edges:
        if a in anc and b in anc:
            adj[a].add(b)
            adj[b].add(a)
    for child in anc:
        ps = [p for p in g.parents(child) if p in anc]
        for i in range(len(ps)):
            for j in range(i + 1, len(ps)):
                adj[ps[i]].add(ps[j])
                adj[ps[j]].add(ps[i])
    frontier = [x for x in X if x not in Z]
    seen = set(frontier)
    while frontier:
        cur = frontier.pop()
        if cur in Y:
            return False
        for nb in adj[cur]:
            if nb not in seen and nb not in Z:
                seen.add(nb)
                frontier.append(nb)
    return True


def s_admissible(g: DAG, s_nodes: Sequence[str], x: Sequence[str], y: Sequence[str], z: Sequence[str]) -> bool:
    """(Y _||_ S | X, Z) in G_{bar X}."""
    return d_separated(g.do_graph(x), s_nodes, y, list(x) + list(z))


__all__ = ["DAG", "d_separated", "s_admissible"]
