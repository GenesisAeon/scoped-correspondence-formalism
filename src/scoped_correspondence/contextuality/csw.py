"""CSW graph invariants — Cabello / Severini / Winter (Milestone 19).

Maps Cabello, Severini & Winter 2014, Phys. Rev. Lett. 112, 040401
(graph-theoretic approach to quantum correlations): for an exclusivity
graph G the hierarchy of bounds on a noncontextual / quantum / GPT
behaviour sum is

    α(G)  ≤  θ(G)  ≤  α*(G)

where α is the independence number (classical), θ the Lovász number
(quantum), and α* the fractional packing number (general probabilistic).

This module implements the C5 (pentagon) specialization that yields the
canonical numbers α=2, θ=√5, α*=5/2, via:

  * brute-force independence number,
  * Lovász umbrella orthonormal representation for θ(C5) (derived, not
    bare-hardcoded),
  * fractional packing LP over edge cliques for α*.

Out of scope: general SDP libraries for arbitrary graphs; identifying the
fractional-packing LP with the sheaf contextual_fraction LP in core.py
(different polytope / different objective — core.py is not imported).
"""
from __future__ import annotations

import itertools
import math
from dataclasses import asdict, dataclass
from typing import Any, Dict, Iterable, Optional, Sequence, Tuple

import numpy as np

from scoped_correspondence.errors import ScopeViolationError

try:
    from scipy.optimize import linprog

    HAS_SCIPY = True
except ImportError:  # pragma: no cover
    HAS_SCIPY = False
    linprog = None


# Cabello, Severini, Winter 2014 PRL 112, 040401
PRL_DOI = "10.1103/PhysRevLett.112.040401"
PRL_REF = (
    "Cabello, Severini & Winter 2014, Graph-Theoretic Approach to Quantum "
    "Correlations, Phys. Rev. Lett. 112, 040401; DOI 10.1103/PhysRevLett.112.040401"
)
SOURCE = PRL_REF
ARXIV = "https://arxiv.org/abs/1401.7081"

# Float tolerance for comparing computed θ(C5) to √5 and for bound checks.
# Umbrella geometry uses float64 trig; residual vs math.sqrt(5) is < 1e-15.
THETA_TOL = 1e-10
BOUND_TOL = 1e-9
# Max vertices for brute-force α / small LPs (C5 = 5).
_MAX_BRUTE = 16

_DEFAULT_ASSUMPTIONS: Tuple[str, ...] = (
    "exclusivity graph: adjacent vertices = mutually exclusive events (CSW 2014)",
    "classical bound = independence number α(G); quantum = Lovász θ(G); "
    "GPT = fractional packing α*(G)",
    "hierarchy α ≤ θ ≤ α* (Lovász sandwich)",
    "lovasz_theta: C5 via umbrella orthonormal representation — no general SDP",
    "fractional_packing_number LP ≠ contextual_fraction LP (core.py untouched)",
)


@dataclass(frozen=True)
class ExclusivityGraph:
    """Simple undirected exclusivity graph on vertices {0, …, n-1}.

    Parameters
    ----------
    n :
        Number of vertices.
    edges :
        Undirected edges as pairs ``(i, j)`` with ``i < j``.
    """

    n: int
    edges: frozenset

    def __post_init__(self) -> None:
        if self.n < 0:
            raise ScopeViolationError(f"ExclusivityGraph: n must be >= 0; got {self.n}")
        norm: set = set()
        for e in self.edges:
            if len(e) != 2:
                raise ScopeViolationError(f"bad edge {e!r}: need 2-tuple")
            a, b = int(e[0]), int(e[1])
            if not (0 <= a < self.n and 0 <= b < self.n):
                raise ScopeViolationError(f"edge {e!r} out of range for n={self.n}")
            if a == b:
                raise ScopeViolationError(f"loop edge {e!r} not allowed")
            norm.add((min(a, b), max(a, b)))
        object.__setattr__(self, "edges", frozenset(norm))

    def neighbors(self, i: int) -> frozenset:
        return frozenset(
            (b if a == i else a) for a, b in self.edges if a == i or b == i
        )

    def adjacency(self) -> np.ndarray:
        A = np.zeros((self.n, self.n), dtype=float)
        for a, b in self.edges:
            A[a, b] = 1.0
            A[b, a] = 1.0
        return A

    def is_cycle(self) -> bool:
        """True iff G is the cycle C_n (n-cycle, 2-regular connected)."""
        if self.n < 3 or len(self.edges) != self.n:
            return False
        for i in range(self.n):
            if len(self.neighbors(i)) != 2:
                return False
        # walk
        seen = {0}
        prev, cur = -1, 0
        for _ in range(self.n - 1):
            nxts = [j for j in self.neighbors(cur) if j != prev]
            if not nxts:
                return False
            prev, cur = cur, nxts[0]
            seen.add(cur)
        return len(seen) == self.n and 0 in self.neighbors(cur)

    def is_c5(self) -> bool:
        return self.n == 5 and self.is_cycle()


def cycle_graph(n: int) -> ExclusivityGraph:
    """Cycle graph C_n (vertices 0..n-1, edges i~i+1 and 0~n-1)."""
    if n < 3:
        raise ScopeViolationError(f"cycle_graph: need n>=3; got {n}")
    edges = [(i, (i + 1) % n) for i in range(n)]
    return ExclusivityGraph(n, frozenset(edges))


def c5() -> ExclusivityGraph:
    """Canonical pentagon exclusivity graph C5."""
    return cycle_graph(5)


# ---------------------------------------------------------------------------
# α(G) — independence number (classical bound)
# ---------------------------------------------------------------------------


def independence_number(G: ExclusivityGraph) -> int:
    """Independence number α(G): size of a largest stable set.

    Brute-force enumeration over subsets (OK for |V| <= 16; C5 → 2).
    """
    if not isinstance(G, ExclusivityGraph):
        raise TypeError("independence_number: expected ExclusivityGraph")
    n = G.n
    if n > _MAX_BRUTE:
        raise ScopeViolationError(
            f"independence_number: n={n} > {_MAX_BRUTE}; brute force out of scope"
        )
    edge_set = G.edges
    best = 0
    for r in range(n + 1):
        for subset in itertools.combinations(range(n), r):
            ok = True
            for a, b in itertools.combinations(subset, 2):
                if (a, b) in edge_set:
                    ok = False
                    break
            if ok and r > best:
                best = r
    return int(best)


# ---------------------------------------------------------------------------
# θ(G) — Lovász number (quantum bound); C5 via umbrella
# ---------------------------------------------------------------------------


def _umbrella_theta_c5() -> Tuple[float, Dict[str, float]]:
    """Derive θ(C5) from the Lovász umbrella orthonormal representation.

    Construction (standard for odd cycles / C5):
      * handle vector c = (0, 0, 1) in R^3;
      * five unit vectors u_i at polar angle α from c, with azimuthal
        angles 4π i / 5 (pentagram ordering) so that graph-adjacent
        vertices subtend geometric angle 4π/5;
      * choose α so adjacent vectors are orthogonal:

            u_i · u_{i+1} = cos²α + sin²α cos(4π/5) = 0
            ⇒  tan²α = -1 / cos(4π/5)

      * Lovász value for this OR: θ = 1 / (c · u_i)² = 1 / cos²α
                                   = 1 + tan²α.

    With cos(4π/5) = -(1+√5)/4 one obtains tan²α = √5 - 1 and therefore
    θ = √5. We return the float computed from the trig identity (not a
    bare ``return math.sqrt(5)``), and document the residual vs √5.

    Tolerance
    ---------
    ``THETA_TOL = 1e-10``: |θ_umbrella - √5| must be below this (float64
    residual is typically < 1e-15).
    """
    cos_4pi5 = math.cos(4.0 * math.pi / 5.0)
    if cos_4pi5 >= 0:
        raise RuntimeError("umbrella: expected cos(4π/5) < 0")
    tan2_alpha = -1.0 / cos_4pi5
    theta = 1.0 + tan2_alpha  # = 1/cos²α
    sqrt5 = math.sqrt(5.0)
    residual = abs(theta - sqrt5)
    # Exact algebraic cross-check: cos(4π/5) = -(1+√5)/4 ⇒ tan²α = √5-1
    cos_exact = -(1.0 + sqrt5) / 4.0
    tan2_exact = -1.0 / cos_exact  # = √5 - 1
    theta_exact_path = 1.0 + tan2_exact
    detail = {
        "cos_4pi5": cos_4pi5,
        "tan2_alpha": tan2_alpha,
        "theta_umbrella": theta,
        "sqrt5": sqrt5,
        "residual_vs_sqrt5": residual,
        "tan2_exact_algebraic": tan2_exact,
        "theta_algebraic": theta_exact_path,
        "tolerance": THETA_TOL,
    }
    if residual > THETA_TOL:
        raise RuntimeError(
            f"umbrella θ(C5)={theta} far from √5={sqrt5} (residual {residual})"
        )
    return float(theta), detail


def lovasz_theta(G: ExclusivityGraph) -> float:
    """Lovász number θ(G) — quantum bound in the CSW hierarchy.

    **C5 only** in this milestone: computed via the umbrella orthonormal
    representation (derives √5; see ``_umbrella_theta_c5``). General SDP
    solvers for arbitrary graphs are out of scope (ScopeViolationError).

    Tolerance: result agrees with ``math.sqrt(5)`` within ``THETA_TOL``
    (1e-10).
    """
    if not isinstance(G, ExclusivityGraph):
        raise TypeError("lovasz_theta: expected ExclusivityGraph")
    if not G.is_c5():
        raise ScopeViolationError(
            "lovasz_theta: M19 supports the C5 umbrella construction only "
            f"(got n={G.n}, is_cycle={G.is_cycle()}). "
            "General SDP for arbitrary graphs is out of scope."
        )
    theta, _ = _umbrella_theta_c5()
    return theta


def lovasz_theta_c5_report() -> Dict[str, Any]:
    """Return θ(C5) plus umbrella derivation diagnostics (for docs/verify)."""
    theta, detail = _umbrella_theta_c5()
    detail["theta"] = theta
    detail["method"] = "umbrella_orthonormal_representation"
    detail["source"] = SOURCE
    return detail


# ---------------------------------------------------------------------------
# α*(G) — fractional packing number (GPT bound)
# ---------------------------------------------------------------------------


def fractional_packing_number(G: ExclusivityGraph) -> float:
    """Fractional packing number α*(G) (CSW general-probabilistic bound).

    LP (fractional stable-set / packing over cliques; for triangle-free G
    the maximal cliques are the edges):

        max  Σ_i x_i
        s.t. x_i + x_j ≤ 1   for every edge {i,j}
             0 ≤ x_i ≤ 1

    For C5 the optimum is 5/2 (symmetric x_i = 1/2).

    This is **not** the sheaf ``contextual_fraction`` LP in
    ``contextuality/core.py`` (different incidence matrix / objective).
    """
    if not isinstance(G, ExclusivityGraph):
        raise TypeError("fractional_packing_number: expected ExclusivityGraph")
    n = G.n
    if n > _MAX_BRUTE:
        raise ScopeViolationError(
            f"fractional_packing_number: n={n} > {_MAX_BRUTE} out of scope"
        )
    if n == 0:
        return 0.0

    # Fast path: C5 closed form (still verified against LP when scipy present).
    if G.is_c5():
        alpha_star = 2.5
        if HAS_SCIPY:
            lp_val = _fractional_packing_lp(G)
            if abs(lp_val - alpha_star) > BOUND_TOL:
                raise RuntimeError(
                    f"C5 α* LP={lp_val} != 5/2 (tol {BOUND_TOL})"
                )
        return float(alpha_star)

    return float(_fractional_packing_lp(G) if HAS_SCIPY else _fractional_packing_greedy(G))


def _fractional_packing_lp(G: ExclusivityGraph) -> float:
    """Solve α* via scipy.optimize.linprog (HiGHS)."""
    if not HAS_SCIPY:
        raise ScopeViolationError("fractional_packing_number: scipy required for LP")
    n = G.n
    c = -np.ones(n)  # maximize sum x
    A_ub = []
    b_ub = []
    for a, b in G.edges:
        row = np.zeros(n)
        row[a] = 1.0
        row[b] = 1.0
        A_ub.append(row)
        b_ub.append(1.0)
    # Also x_i ≤ 1 (singleton cliques); bounds handle this
    bounds = [(0.0, 1.0)] * n
    if not A_ub:
        return float(n)  # empty graph
    res = linprog(
        c,
        A_ub=np.asarray(A_ub, dtype=float),
        b_ub=np.asarray(b_ub, dtype=float),
        bounds=bounds,
        method="highs",
    )
    if not res.success:
        raise RuntimeError(f"fractional packing LP failed: {res.message}")
    return float(-res.fun)


def _fractional_packing_greedy(G: ExclusivityGraph) -> float:
    """Fallback without scipy: for 2-regular cycles, α* = n/2."""
    if G.is_cycle() and G.n >= 3:
        return float(G.n) / 2.0
    raise ScopeViolationError(
        "fractional_packing_number: scipy unavailable and graph is not a cycle; "
        "install scipy or use cycle_graph / c5()."
    )


# ---------------------------------------------------------------------------
# CSWWitness
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CSWWitness:
    """CSW bound witness for an observed exclusivity-graph behaviour sum.

    Attributes
    ----------
    classical_bound :
        α(G) — largest classical noncontextual value of the sum.
    quantum_bound :
        θ(G) — Lovász quantum bound.
    general_probabilistic_bound :
        α*(G) — fractional packing / GPT bound.
    observed_sum :
        Σ_i p_i for the assigned event probabilities.
    classical_violated :
        True iff ``observed_sum > classical_bound`` (beyond float tol).
    """

    classical_bound: float
    quantum_bound: float
    general_probabilistic_bound: float
    observed_sum: float
    classical_violated: bool

    @property
    def quantum_held(self) -> bool:
        return self.observed_sum <= self.quantum_bound + BOUND_TOL

    @property
    def gpt_held(self) -> bool:
        return self.observed_sum <= self.general_probabilistic_bound + BOUND_TOL

    def as_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["quantum_held"] = self.quantum_held
        d["gpt_held"] = self.gpt_held
        d["source"] = SOURCE
        d["doi"] = PRL_DOI
        return d


def csw_witness(
    G: ExclusivityGraph,
    node_probs: Sequence[float],
) -> CSWWitness:
    """Build a ``CSWWitness`` from per-vertex probabilities on G.

    ``observed_sum = sum(node_probs)``. Probabilities must be in [0, 1]
    and satisfy the exclusivity constraints p_i + p_j ≤ 1 on edges
    (else ScopeViolationError — not a valid exclusive behaviour).
    """
    if not isinstance(G, ExclusivityGraph):
        raise TypeError("csw_witness: expected ExclusivityGraph")
    if len(node_probs) != G.n:
        raise ScopeViolationError(
            f"csw_witness: len(node_probs)={len(node_probs)} != n={G.n}"
        )
    probs = [float(p) for p in node_probs]
    for i, p in enumerate(probs):
        if p < -BOUND_TOL or p > 1.0 + BOUND_TOL:
            raise ScopeViolationError(
                f"csw_witness: node_probs[{i}]={p} not in [0,1]"
            )
    for a, b in G.edges:
        if probs[a] + probs[b] > 1.0 + BOUND_TOL:
            raise ScopeViolationError(
                f"csw_witness: exclusivity violated on edge ({a},{b}): "
                f"{probs[a]}+{probs[b]} > 1"
            )
    observed = float(sum(probs))
    alpha = float(independence_number(G))
    # θ only for C5 in M19; for other graphs refuse quantum bound computation
    if G.is_c5():
        theta = float(lovasz_theta(G))
    else:
        raise ScopeViolationError(
            "csw_witness: quantum_bound (θ) only available for C5 in M19"
        )
    alpha_star = float(fractional_packing_number(G))
    classical_violated = observed > alpha + BOUND_TOL
    return CSWWitness(
        classical_bound=alpha,
        quantum_bound=theta,
        general_probabilistic_bound=alpha_star,
        observed_sum=observed,
        classical_violated=classical_violated,
    )


def symmetric_c5_model(p: float) -> CSWWitness:
    """Symmetric C5 behaviour: every vertex has probability ``p``, sum ``5p``.

    Classical α=2 is violated when ``5p > 2`` (i.e. ``p > 2/5``).
    Quantum θ=√5 holds while ``5p ≤ √5``; GPT α*=5/2 while ``5p ≤ 5/2``.
    Requires ``0 ≤ p ≤ 1/2`` (edge exclusivity p+p ≤ 1).
    """
    p = float(p)
    if p < 0 or p > 0.5 + BOUND_TOL:
        raise ScopeViolationError(
            f"symmetric_c5_model: need 0 <= p <= 1/2 for exclusivity; got {p}"
        )
    return csw_witness(c5(), (p, p, p, p, p))


def csw_invariants(G: ExclusivityGraph) -> Dict[str, float]:
    """Return ``{alpha, theta, alpha_star}`` for G (θ requires C5)."""
    out: Dict[str, float] = {
        "alpha": float(independence_number(G)),
        "alpha_star": float(fractional_packing_number(G)),
    }
    if G.is_c5():
        out["theta"] = float(lovasz_theta(G))
    return out


def report(G: Optional[ExclusivityGraph] = None) -> Dict[str, Any]:
    """Bundle C5 invariants + umbrella diagnostics + source mapping."""
    g = G if G is not None else c5()
    inv = csw_invariants(g)
    umbrella = lovasz_theta_c5_report() if g.is_c5() else {}
    return {
        "n": g.n,
        "is_c5": g.is_c5(),
        "invariants": inv,
        "umbrella": umbrella,
        "assumptions": list(_DEFAULT_ASSUMPTIONS),
        "source": SOURCE,
        "doi": PRL_DOI,
        "arxiv": ARXIV,
        "not_contextual_fraction_lp": True,
        "no_general_sdp": True,
    }
