"""Polyhedral observation pilot (TP0-TP1, candidate assessment 2026-10-01).

Purpose: a precise, small demonstration of observation fibres and lost
structural information -- NOT a polyhedron certifier and NOT a reproduction
of the genus-3 constructions (Mizhaev arXiv:2609.17700; Roest & Vigh
arXiv:2609.32998), whose coordinates were not audited here.

Levels kept apart (assessment section 3.1): key numbers (V, E, F, Euler
characteristic) -> incidence -> topological surface -> geometric
realisation -> observation map. Equality under a coarse observation map is
a statement about that map, not an identity of the objects.

TP-C01  Euler arithmetic: V - E + F = 24 - 36 + 8 = -4; IF the complex is a
        closed, connected, orientable 2-manifold (each vertex link a circle),
        then chi = 2 - 2g gives g = 3. The numbers alone do NOT establish
        those premises; ``euler_genus`` refuses without them.
TP-C02  C8 vs C4 + C4: same vertex count, edge count and degree sequence
        (all degree 2) -- a coarse observation cannot separate them; the
        refined observation 'number of connected components' (1 vs 2) can.
TP-C03  T(x, y, z) = (y, -x, -z): T^4 = I and det T = -1 -- an improper
        rotation (rotoreflection) generating an abstract cyclic group of
        order four; it is not a pure quarter turn.
TP-C04  Exact coplanarity of rational points vs a deviation of 1e-12:
        exact mode never rounds a nearly coplanar point onto the plane.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Dict, FrozenSet, Iterable, List, Optional, Sequence, Tuple

from scoped_correspondence.epistemic.observation_fibers import FiberReport, observation_fiber
from scoped_correspondence.epistemic.records import FiniteDomainSpec
from scoped_correspondence.errors import ScopeViolationError

Edge = Tuple[int, int]


@dataclass(frozen=True)
class SimpleGraph:
    name: str
    n: int
    edges: FrozenSet[Edge]

    @classmethod
    def from_edges(cls, name: str, n: int, edges: Iterable[Edge]) -> "SimpleGraph":
        es = frozenset(tuple(sorted(e)) for e in edges)
        if any(a == b or not (0 <= a < n and 0 <= b < n) for a, b in es):
            raise ScopeViolationError("invalid edge")
        return cls(name, n, es)

    def degree_sequence(self) -> Tuple[int, ...]:
        deg = [0] * self.n
        for a, b in self.edges:
            deg[a] += 1
            deg[b] += 1
        return tuple(sorted(deg))

    def components(self) -> int:
        parent = list(range(self.n))

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        for a, b in self.edges:
            parent[find(a)] = find(b)
        return len({find(v) for v in range(self.n)})


def cycle(name: str, n: int, offset: int = 0) -> List[Edge]:
    return [(offset + i, offset + (i + 1) % n) for i in range(n)]


def c8() -> SimpleGraph:
    return SimpleGraph.from_edges("C8", 8, cycle("C8", 8))


def c4_plus_c4() -> SimpleGraph:
    return SimpleGraph.from_edges("C4+C4", 8, cycle("a", 4) + cycle("b", 4, 4))


def coarse_observation(g: SimpleGraph) -> Tuple:
    """(V, E, degree sequence)."""
    return (g.n, len(g.edges), g.degree_sequence())


def refined_observation(g: SimpleGraph) -> Tuple:
    """Coarse observation plus the number of connected components."""
    return coarse_observation(g) + (g.components(),)


def graph_fibre(candidates: Sequence[SimpleGraph], observation, observed) -> FiberReport:
    """Fibre over a FINITE listed candidate set (existing H3 machinery)."""
    by = {g.name: g for g in candidates}
    dom = FiniteDomainSpec("graph_candidates", tuple(by), "listed graphs only", coverage="partial",
                           relationship_to_target_space="restricted_candidates")
    return observation_fiber(dom, [], lambda k: observation(by[k]), observed)


def euler_characteristic(V: int, E: int, F: int) -> int:
    return V - E + F


def euler_genus(V: int, E: int, F: int, *, closed: bool, connected: bool, orientable: bool, vertex_links_are_circles: bool) -> Optional[int]:
    """g from chi = 2 - 2g, ONLY for a closed connected orientable 2-manifold.
    Returns None (no statement) if any premise is not established; premises
    are declared by the caller, not checked here (that would be TP2)."""
    if not (closed and connected and orientable and vertex_links_are_circles):
        return None
    chi = euler_characteristic(V, E, F)
    if (2 - chi) % 2:
        raise ScopeViolationError("odd 2 - chi: not an orientable closed surface")
    return (2 - chi) // 2


def mat_mul(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3)] for i in range(3)]


def det3(m) -> int:
    return (m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1]) - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
            + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0]))


ROTOREFLECTION = [[0, 1, 0], [-1, 0, 0], [0, 0, -1]]  # T(x, y, z) = (y, -x, -z)


def order_and_determinant(m) -> Tuple[Optional[int], int]:
    ident = [[int(i == j) for j in range(3)] for i in range(3)]
    p = m
    for k in range(1, 13):
        if p == ident:
            return k, det3(m)
        p = mat_mul(p, m)
    return None, det3(m)


def coplanar_exact(points: Sequence[Sequence]) -> bool:
    """Four or more points with EXACT (int/Fraction) coordinates lie in one
    plane iff every 3x3 determinant of differences to the first point is 0.
    Floats are refused: a nearly coplanar point is never rounded onto the
    plane in exact mode (a numeric mode would need its own evidence status)."""
    pts = []
    for p in points:
        if any(isinstance(c, float) or isinstance(c, bool) or not isinstance(c, (int, Fraction)) for c in p):
            raise ScopeViolationError("exact coplanarity needs int/Fraction coordinates")
        pts.append([Fraction(c) for c in p])
    if len(pts) < 4:
        return True
    p0 = pts[0]
    d = [[c - c0 for c, c0 in zip(p, p0)] for p in pts[1:]]
    for i in range(len(d)):
        for j in range(i + 1, len(d)):
            for k in range(j + 1, len(d)):
                if det3([d[i], d[j], d[k]]) != 0:
                    return False
    return True


__all__ = ["SimpleGraph", "c8", "c4_plus_c4", "coarse_observation", "refined_observation", "graph_fibre", "euler_characteristic",
           "euler_genus", "ROTOREFLECTION", "order_and_determinant", "coplanar_exact"]
