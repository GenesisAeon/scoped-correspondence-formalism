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

**Three distinct outcomes, never conflated** (plan's explicit requirement):
``certified_safe`` (the affine lower-bound trajectory stays >= 0 at both
endpoints), ``not_certified`` (``x_lower`` itself already has a negative
component -- this means safety was NOT established for every possible true
initial state, NOT that the true state is known to be unsafe), and, when
``x_lower`` is certain and the end-of-interval bound is violated, EITHER
``boundary_touch`` (the affine lower bound reaches exactly 0, which is
ALLOWED -- the safety sets here are closed) or ``strict_violation``
(strictly negative). Astra's own worked example: three decoupled buffers
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
from scipy.optimize import minimize

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
    status: str  # "certified_safe" | "not_certified" | "boundary_touch" | "strict_violation"
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
        # Distinguish "solver never converged" from "provably infeasible": check
        # whether u=u_max, f=0 (or f=edge_cap on a helpful topology) at least
        # satisfies the constraints; if even the most generous box point fails
        # safety, report infeasible; otherwise optimizer_failed.
        z_generous = np.concatenate([u_max, edge_cap])
        if np.all(safety_constraint(z_generous) >= -1e-6) and np.sum(u_max) <= total_supply_cap + 1e-9:
            return QPResult(u=np.full(n, np.nan), f=np.full(m, np.nan), cost=np.nan, feasible=False, status="optimizer_failed", safety=None)
        return QPResult(u=np.full(n, np.nan), f=np.full(m, np.nan), cost=np.nan, feasible=False, status="infeasible", safety=None)

    u_star, f_star = unpack(best.x)
    # Classify the SOLVED result directly from the (already solver-enforced >= 0)
    # constraint value -- NOT via whole_interval_safety's not_certified branch,
    # which exists for a genuinely UNCERTAIN x_lower bound and would otherwise
    # mislabel a solution that starts from an already-negative but perfectly
    # CERTAIN x_lower (the solver's own constraint already accounts for its sign).
    x_end = safety_constraint(best.x)
    touching = np.any(np.abs(x_end) <= 1e-7)
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
