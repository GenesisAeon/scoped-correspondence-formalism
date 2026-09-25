"""Small resource networks with repeated interventions (INTEGRATED_EXTENSION_ROADMAP.md
Paket C5) -- response to
prompts/Answers/nicht_stationäre_Treiber/SCF_INTEGRATED_EXTENSION_IMPLEMENTATION_PLAN.md,
section 9.

State ``x``, external supply ``u``, outflow (demand) ``d``, directed edge
flows ``f``, and incidence matrix ``B`` (each column has ``-1`` at its
origin node, ``+1`` at its destination -- internal flows conserve the total
resource):

    dx/dt = B @ f + u - d

**Whole-interval safety (plan section 9.2):** for a control interval of
length ``Delta`` with CONSTANT ``u``, ``f``, ``d`` held throughout, each
component of ``x`` is AFFINE in time, so checking both endpoints suffices.
With hard bounds ``x(0) >= x_lower >= 0`` and ``d(t) <= d_upper`` (allowing
genuine initial-state uncertainty), the robust sufficient condition is

    x_lower + Delta * (B @ f + u - d_upper) >= 0

**Distinct outcomes, never conflated** (plan's explicit requirement):
``certified_safe`` (the affine lower-bound trajectory stays >= 0 at both
endpoints), ``not_certified`` (``x_lower`` itself already has a negative
component AS A DECLARED UNCERTAINTY BOUND -- this means safety was NOT
established for every possible true initial state, NOT that the true state
is known to be unsafe), ``already_violated`` (``x_lower`` has a negative
component that is instead a CERTAIN, definite numeric state -- the
violation has already happened; ``solve_network_qp`` reports this
explicitly, see finding R2 below, rather than conflating it with
``not_certified``), and, when ``x_lower`` is certain and non-negative but
the end-of-interval bound is violated, EITHER ``boundary_touch`` (the
affine lower bound reaches exactly 0 at either endpoint, which is ALLOWED --
the safety sets here are closed) or ``strict_violation`` (strictly
negative). Astra's own worked example: three decoupled buffers
``x=(0.2,0.4,0.6)``, ``d=(1,1,1)``, minimal safe interventions for
``Delta=1`` are exactly ``(0.8,0.6,0.4)`` (sum 1.8, quadratic cost 1.16);
for ``Delta=2`` the minimum becomes ``(0.9,0.8,0.7)`` (sum 2.4, infeasible
under a shared rate budget of 2); holding the ``Delta=1``-adequate
intervention for 2 time units instead ends at ``x=(-0.2,-0.4,-0.6)``.

**Structural counter-check (mandatory, plan section 9.4):** adding a
freely-switchable-OFF edge to a network, with everything else unchanged,
can only WEAKLY IMPROVE the optimal value of the SAME cost function -- the
old feasible set (with that edge's flow fixed at 0) is a special case of the
new one. A claimed WORSE optimum after adding such an edge is a bug, not a
network effect, unless a NAMED additional mechanism (forced routing, delay,
a non-switchable flow, a connection cost, limited information) is
introduced.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Sequence, Tuple

import numpy as np
from scipy.optimize import minimize, linprog

from scoped_correspondence.errors import ScopeViolationError

_TOL = 1e-9


@dataclass(frozen=True)
class ResourceNetwork:
    n_nodes: int
    edges: Tuple[Tuple[int, int], ...]  # (origin, destination) per edge

    def incidence_matrix(self) -> np.ndarray:
        B = np.zeros((self.n_nodes, len(self.edges)))
        for e, (src, dst) in enumerate(self.edges):
            if not (0 <= src < self.n_nodes and 0 <= dst < self.n_nodes):
                raise ScopeViolationError(f"edge {(src, dst)!r} references a node outside range(0,{self.n_nodes})")
            if src == dst:
                raise ScopeViolationError(f"self-loop edge {(src, dst)!r} is not allowed")
            B[src, e] -= 1.0
            B[dst, e] += 1.0
        return B


@dataclass(frozen=True)
class SafetyCheckResult:
    status: str  # "certified_safe" | "not_certified" | "already_violated" | "boundary_touch" | "strict_violation"
    x_end_lower: np.ndarray
    violating_nodes: Tuple[int, ...]


def whole_interval_safety(
    x_lower: np.ndarray, B: np.ndarray, f: np.ndarray, u: np.ndarray, d_upper: np.ndarray, Delta: float,
    tol: float = _TOL,
) -> SafetyCheckResult:
    """Check the robust whole-interval safety condition (module docstring)."""
    if Delta < 0.0:
        raise ScopeViolationError(f"Delta must be >= 0; got {Delta!r}")
    if np.any(x_lower < -tol):
        return SafetyCheckResult(status="not_certified", x_end_lower=x_lower.copy(), violating_nodes=tuple(np.where(x_lower < -tol)[0].tolist()))

    x_end_lower = x_lower + Delta * (B @ f + u - d_upper)
    if np.all(x_end_lower >= -tol):
        touching = np.where(np.abs(x_end_lower) <= tol)[0]
        status = "boundary_touch" if len(touching) > 0 else "certified_safe"
        return SafetyCheckResult(status=status, x_end_lower=x_end_lower, violating_nodes=tuple())

    violating = tuple(np.where(x_end_lower < -tol)[0].tolist())
    return SafetyCheckResult(status="strict_violation", x_end_lower=x_end_lower, violating_nodes=violating)


def propagate_state(x: np.ndarray, B: np.ndarray, f: np.ndarray, u: np.ndarray, d: np.ndarray, Delta: float) -> np.ndarray:
    """The plain affine update ``x + Delta*(B@f + u - d)`` -- ALWAYS applied,
    regardless of sign. Kept separate from ``whole_interval_safety`` on
    purpose: that function's ``not_certified`` branch deliberately returns the
    input unchanged when ``x_lower`` carries genuine INITIAL-STATE
    UNCERTAINTY (a negative lower bound means "safety not established", not
    "the true state is already known to be negative") -- reusing it to
    propagate an actually-CERTAIN (if already negative, from a real prior
    violation) state would silently freeze the simulation instead of
    continuing to track the true, still-evolving trajectory."""
    if Delta < 0.0:
        raise ScopeViolationError(f"Delta must be >= 0; got {Delta!r}")
    return x + Delta * (B @ f + u - d)


def minimal_decoupled_intervention(x: np.ndarray, d: np.ndarray, Delta: float, u_max: Optional[np.ndarray] = None) -> np.ndarray:
    """Closed-form minimal safe intervention for DECOUPLED buffers (no edges):
    ``u_i = max(0, d_i - x_i/Delta)``, clipped at ``u_max`` if given (a clipped
    result may then be infeasible -- callers must check ``whole_interval_safety``
    afterward, this function does not silently pretend clipping preserves safety)."""
    if Delta <= 0.0:
        raise ScopeViolationError(f"Delta must be > 0; got {Delta!r}")
    u = np.maximum(0.0, d - x / Delta)
    if u_max is not None:
        u = np.minimum(u, u_max)
    return u


@dataclass(frozen=True)
class QPResult:
    u: np.ndarray
    f: np.ndarray
    cost: float
    feasible: bool
    status: str  # "solved" | "infeasible" | "optimizer_failed"
    safety: Optional[SafetyCheckResult]


def _lp_feasibility_check(
    x_lower: np.ndarray, d_upper: np.ndarray, B: np.ndarray, Delta: float,
    u_max: np.ndarray, edge_cap: np.ndarray, total_supply_cap: float, K: Optional[np.ndarray],
) -> bool:
    """Exact linear feasibility check for solve_network_qp's constraint set
    (dropping only the quadratic objective, which cannot affect feasibility)
    -- used to distinguish a genuine solver convergence failure
    (``optimizer_failed``) from a mathematically PROVEN empty feasible set
    (``infeasible``), see finding R5 in ``solve_network_qp``'s docstring.
    A single corner point failing tells us nothing about the rest of the
    feasible region; an LP's own infeasibility verdict is an actual proof."""
    n = x_lower.shape[0]
    m = B.shape[1]
    # safety: x_lower + Delta*(B@f + u - d_upper) >= 0  <=>  -Delta*u - Delta*B@f <= x_lower - Delta*d_upper
    A_ub = [np.hstack([-Delta * np.eye(n), -Delta * B])]
    b_ub = [x_lower - Delta * d_upper]
    # shared instantaneous supply budget: sum(u) <= total_supply_cap
    A_ub.append(np.concatenate([np.ones(n), np.zeros(m)]).reshape(1, -1))
    b_ub.append(np.array([total_supply_cap]))
    if K is not None:
        # upper capacity: x_lower + Delta*(B@f + u - d_upper) <= K  <=>  Delta*u + Delta*B@f <= K - x_lower + Delta*d_upper
        A_ub.append(np.hstack([Delta * np.eye(n), Delta * B]))
        b_ub.append(K - x_lower + Delta * d_upper)
    A_ub_mat = np.vstack(A_ub)
    b_ub_vec = np.concatenate(b_ub)
    bounds = [(0.0, float(u_max[i])) for i in range(n)] + [(0.0, float(edge_cap[e])) for e in range(m)]
    res = linprog(np.zeros(n + m), A_ub=A_ub_mat, b_ub=b_ub_vec, bounds=bounds, method="highs")
    return bool(res.success)


def solve_network_qp(
    network: ResourceNetwork,
    x_lower: np.ndarray,
    d_upper: np.ndarray,
    Delta: float,
    u_max: np.ndarray,
    edge_cap: np.ndarray,
    total_supply_cap: float,
    w: np.ndarray,
    v: np.ndarray,
    K: Optional[np.ndarray] = None,
    n_restarts: int = 6,
    seed: int = 0,
) -> QPResult:
    """Minimize ``sum_i w_i*u_i^2 + sum_e v_e*f_e^2`` subject to whole-interval
    safety (module docstring), edge capacities, a shared instantaneous supply
    budget, and box bounds -- via ``scipy.optimize.minimize`` (SLSQP), matching
    the repo's existing convention (``viability.coupled_buffer_cbf_qp``).
    Multiple random restarts are used as a PRACTICAL robustness check for this
    convex-but-solved-numerically problem (a full closed-form or active-set
    certificate is not attempted here for the general network case -- see
    module docstring and docs/resource_network_control.md for scope).
    `optimizer_failed` is reported distinctly from `infeasible`: a failed
    solver run is NOT proof that no feasible point exists.

    ``QPResult.feasible`` reflects TRUE WHOLE-INTERVAL safety
    (``min(x_lower, x_end) >= 0`` componentwise), never merely "the solver
    converged": when ``x_lower`` already has a negative component, ``status``
    can still be ``"solved"`` (a recovery action was found), but
    ``feasible=False`` and ``safety.status="already_violated"`` (finding R2
    -- see module docstring).
    """
    B = network.incidence_matrix()
    n, m = network.n_nodes, len(network.edges)
    if np.any(w < 0.0) or np.any(v < 0.0):
        raise ScopeViolationError("QP weights w, v must be non-negative")

    def unpack(z):
        return z[:n], z[n:]

    def cost_fn(z):
        u, f = unpack(z)
        return float(np.sum(w * u ** 2) + np.sum(v * f ** 2))

    def safety_constraint(z):
        u, f = unpack(z)
        return x_lower + Delta * (B @ f + u - d_upper)  # >= 0

    constraints = [{"type": "ineq", "fun": safety_constraint}, {"type": "ineq", "fun": lambda z: total_supply_cap - np.sum(unpack(z)[0])}]
    if K is not None:
        def capacity_constraint(z):
            u, f = unpack(z)
            return K - (x_lower + Delta * (B @ f + u - d_upper))
        constraints.append({"type": "ineq", "fun": capacity_constraint})

    bounds = [(0.0, float(u_max[i])) for i in range(n)] + [(0.0, float(edge_cap[e])) for e in range(m)]

    rng = np.random.default_rng(seed)
    best = None
    any_success = False
    for trial in range(n_restarts):
        z0 = np.array([rng.uniform(lo, hi) for lo, hi in bounds])
        res = minimize(cost_fn, z0, method="SLSQP", bounds=bounds, constraints=constraints, options={"maxiter": 300, "ftol": 1e-12})
        if res.success:
            any_success = True
            if best is None or res.fun < best.fun - 1e-9:
                best = res

    if best is None:
        # **Correction (2026-09-25, response to SCF_REVIEW_C0_C7_4ed0cd9.md
        # finding R5 -- a real bug, independently reproduced before fixing):**
        # the original fallback checked ONLY the single "most generous" corner
        # (u=u_max, f=edge_cap) and reported "infeasible" if THAT ONE POINT
        # failed -- but a feasible witness can exist elsewhere even when the
        # generous corner itself fails (maximal individual flows can jointly
        # exceed a SHARED budget, or maximal edge flow can drain a source
        # node). Astra's exact counterexample: 3 decoupled buffers,
        # x_lower=(0.2,0.4,0.6), d_upper=(1,1,1), Delta=1, u_max=(1,1,1),
        # budget=2 -- the feasible witness u=(0.8,0.6,0.4) (sum 1.8) exists,
        # but the generous corner (sum 3) violates the budget, so the old
        # code wrongly reported "infeasible" whenever all SLSQP restarts
        # failed to converge on this otherwise-easy problem.
        #
        # Fixed: solve a SEPARATE, EXACT linear feasibility problem with the
        # SAME constraints (dropping only the quadratic objective) via
        # ``scipy.optimize.linprog``. An LP's infeasibility verdict is an
        # actual mathematical proof (not a single-point heuristic); if the LP
        # finds ANY feasible point, the quadratic solver's failure is
        # reported honestly as ``optimizer_failed``, never as ``infeasible``.
        if _lp_feasibility_check(x_lower, d_upper, B, Delta, u_max, edge_cap, total_supply_cap, K):
            return QPResult(u=np.full(n, np.nan), f=np.full(m, np.nan), cost=np.nan, feasible=False, status="optimizer_failed", safety=None)
        return QPResult(u=np.full(n, np.nan), f=np.full(m, np.nan), cost=np.nan, feasible=False, status="infeasible", safety=None)

    u_star, f_star = unpack(best.x)
    x_end = safety_constraint(best.x)  # x_lower + Delta*(B@f_star + u_star - d_upper), solver-enforced >= -tol

    # **Correction (2026-09-25, response to SCF_REVIEW_C0_C7_4ed0cd9.md finding
    # R2 -- a real bug, independently reproduced before fixing):** a PREVIOUS
    # version of this function classified the result using ONLY x_end (the
    # solver-enforced constraint value), never re-checking x_lower's own sign.
    # For an already-negative x_lower, the solver can find a "recovery" action
    # that brings the state back to exactly 0 by the interval's END while the
    # actual affine trajectory stays STRICTLY NEGATIVE for the entire interval
    # up to that instant -- Astra's exact counterexample: 1 node, no edges,
    # x_lower=-0.1, d=0, Delta=1, u_max=1, budget=1 gives u~0.1,
    # x(t)=-0.1+0.1t, negative for every 0<=t<1, yet the old code reported
    # status=solved, feasible=True, safety.status=boundary_touch -- claiming
    # whole-interval safety for a trajectory that was never safe at all.
    # Fixed: whole-interval safety for an AFFINE trajectory requires
    # ``min(x_lower, x_end) >= 0`` componentwise (checking both endpoints
    # suffices exactly because the trajectory is affine -- module docstring).
    # A negative x_lower here is CERTAIN (the caller passed a definite numeric
    # state, not a declared uncertainty bound), so it is reported as
    # ``already_violated`` -- distinct from ``not_certified``, which
    # ``whole_interval_safety`` reserves for a genuinely uncertain lower bound
    # -- with ``feasible=False``: the solver still found a valid RECOVERY
    # action (``status="solved"``), but that is not the same claim as
    # certified whole-interval safety.
    if np.any(x_lower < -1e-9):
        safety = SafetyCheckResult(
            status="already_violated", x_end_lower=x_end,
            violating_nodes=tuple(np.where(x_lower < -1e-9)[0].tolist()),
        )
        return QPResult(u=u_star, f=f_star, cost=float(best.fun), feasible=False, status="solved", safety=safety)

    touching = np.any(np.abs(x_end) <= 1e-7) or np.any(np.abs(x_lower) <= 1e-9)
    safety = SafetyCheckResult(
        status=("boundary_touch" if touching else "certified_safe"), x_end_lower=x_end, violating_nodes=tuple(),
    )
    return QPResult(u=u_star, f=f_star, cost=float(best.fun), feasible=True, status="solved", safety=safety)


__all__ = [
    "ResourceNetwork",
    "SafetyCheckResult",
    "whole_interval_safety",
    "minimal_decoupled_intervention",
    "QPResult",
    "solve_network_qp",
]
