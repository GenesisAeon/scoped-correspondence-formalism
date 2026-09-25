"""Concrete 3-node resource network experiment (INTEGRATED_EXTENSION_ROADMAP.md
Paket C5, plan section 9.4's declared panel) -- response to
prompts/Answers/nicht_stationäre_Treiber/SCF_INTEGRATED_EXTENSION_IMPLEMENTATION_PLAN.md.

Fixed panel, parameters declared BEFORE looking at any result: 3 nodes,
``x(0)=(0.6,0.6,0.6)``, upper node capacity 2, base load 0.3 per node,
extra load 0.9 at node 0 on ``[1,2)`` and at node 2 on ``[3,4)``, horizon 6.
``0<=u_i<=0.6``, shared instantaneous supply budget 0.9, edge capacity 0.4
per edge. Chain ``0->1->2`` plus an optional extra edge ``2->0``. Control
intervals compared: 0.25 and 1 (both evenly divide every load-change time,
so "known load changes only at interval boundaries" holds for either
choice). QP weights ``w_i=1``, ``v_e=0.1``.

Three strategies, simulated identically over the same load schedule:

- ``none``: fixed ``u=(0.3,0.3,0.3)``, no flows at all (``f=0``) -- never
  reacts to the load spikes.
- ``fixed_routing``: fixed ``u=(0.3,0.3,0.3)`` PLUS a constant routing rule
  ``f=(0.2,0.2)`` along the chain edges (never the extra edge) -- a
  declared but non-adaptive redistribution.
- ``optimized``: re-solves ``resource_network_control.solve_network_qp``
  at every control-interval boundary using that interval's OWN declared
  load (never a future one), holding the result constant through the
  interval.

A separate failure case blocks edge ``1->2`` on ``[3,4)`` -- declared known
to the controller from the start of the experiment (not fed back after the
fact once it happens), per the plan's explicit requirement.

Reported per run: minimal reserve (value, time, node), first touch at
``x<=0`` and strict violation ``x<0`` reported SEPARATELY (never conflated
-- see ``resource_network_control.py``'s status distinctions), cumulative
intervention cost, cumulative transported quantity, and every
non-``certified_safe``/``boundary_touch`` interval with its cause.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import numpy as np

from scoped_correspondence.errors import ScopeViolationError
from scoped_correspondence.viability.resource_network_control import (
    ResourceNetwork,
    whole_interval_safety,
    propagate_state,
    solve_network_qp,
)

LOAD_CHANGE_TIMES = (1.0, 2.0, 3.0, 4.0)  # also the edge-failure window's own boundaries

NETWORK = ResourceNetwork(n_nodes=3, edges=((0, 1), (1, 2), (2, 0)))
BASE_LOAD = 0.3
K_UPPER = 2.0
U_MAX = np.array([0.6, 0.6, 0.6])
EDGE_CAP = np.array([0.4, 0.4, 0.4])  # (0->1), (1->2), (2->0)
TOTAL_SUPPLY_CAP = 0.9
W = np.array([1.0, 1.0, 1.0])
V = np.array([0.1, 0.1, 0.1])
HORIZON = 6.0


def _demand(t: float) -> np.ndarray:
    d = np.full(3, BASE_LOAD)
    if 1.0 <= t < 2.0:
        d[0] += 0.9
    if 3.0 <= t < 4.0:
        d[2] += 0.9
    return d


def _validate_control_interval(control_interval: float) -> None:
    """**Correction (2026-09-25, response to SCF_REVIEW_C0_C7_4ed0cd9.md
    finding R7 -- a real bug, independently reproduced before fixing):** the
    original check only required ``control_interval`` to evenly divide the
    horizon, so ``control_interval=2.0`` was silently ACCEPTED -- sampling
    demand only at ``t=0,2,4`` and missing BOTH declared load spikes
    (``[1,2)`` and ``[3,4)``) entirely (``run_network_pilot("none", 2.0,
    False)`` reported ``min_reserve=0.6``, no touch, no violation -- while
    the identical baseline with the load plan fully respected reaches
    ``-0.3``). **Fixed** by requiring every declared load-change/failure time
    to also lie exactly on the control grid (a relative, scaled divisibility
    check, per the review's own suggestion, rather than an absolute
    tolerance) -- this pilot's own two officially compared values (0.25 and
    1) both satisfy this exactly; other choices are rejected rather than
    silently mis-simulated.
    """
    if not np.isfinite(control_interval) or control_interval <= 0.0:
        raise ScopeViolationError(f"control_interval must be finite and > 0; got {control_interval!r}")
    for t_event in (0.0, HORIZON) + LOAD_CHANGE_TIMES:
        ratio = t_event / control_interval
        if abs(ratio - round(ratio)) > 1e-9 * max(1.0, abs(ratio)):
            raise ScopeViolationError(
                f"control_interval={control_interval!r} does not evenly divide the declared load/failure "
                f"time {t_event!r} -- a coarser interval would silently sample straight past a load spike "
                f"(see module docstring, finding R7); use one of the two officially compared values (0.25, 1) "
                f"or another interval that evenly divides every declared event time"
            )


def _affine_interval_events(
    x0: np.ndarray, b: np.ndarray, L: float, t0: float, tol: float = 1e-9
) -> Tuple[Optional[float], Optional[float]]:
    """**Correction (2026-09-25, response to SCF_REVIEW_C0_C7_4ed0cd9.md
    finding R6 -- a real bug, independently reproduced before fixing):** the
    original code only checked interval ENDPOINTS on the CONTROL grid for a
    sign change, reporting the touch/violation time as whichever grid point
    happened to be closest -- giving DIFFERENT reported times
    (``Delta=1``: 2.0; ``Delta=0.25``: 1.75) for the exact SAME physical
    baseline trajectory, whose true touch time is
    ``1+0.6/0.9=5/3~1.6666666667`` (Astra's exact counterexample, using only
    the unmodified ``none`` baseline). **Fixed**: since ``x`` is affine
    within a held-constant-control interval (``x_i(t0+s)=x0_i+b_i*s``), the
    exact crossing time solves ``s=-x0_i/b_i`` directly -- independent of
    ``Delta`` entirely.

    Returns ``(touch_time, strict_violation_time)`` for style events
    occurring in ``[t0, t0+L]``, or ``None`` for either if no such event
    occurs in this interval. A "touch" is the first time some component
    reaches ``<=0``; "strict violation" is the first time some component is
    STRICTLY ``<0`` -- the review's own definition: a downward crossing's
    strict-violation infimum coincides with its touch time (the state is
    exactly zero only at that single instant), while a pure local-minimum
    touch that immediately recovers (checked via the FOLLOWING interval's own
    slope, by calling this function again with that interval's data) is
    never promoted to a strict violation.
    """
    touch_time: Optional[float] = None
    strict_time: Optional[float] = None
    for xi0, bi in zip(x0, b):
        if xi0 <= tol:
            t_touch_i = t0
        elif bi < -tol:
            s_star = -xi0 / bi
            t_touch_i = t0 + s_star if s_star <= L + tol else None
        else:
            t_touch_i = None
        if t_touch_i is not None and (touch_time is None or t_touch_i < touch_time):
            touch_time = min(t_touch_i, t0 + L)

        if xi0 < -tol:
            t_strict_i = t0
        elif xi0 <= tol and bi < -tol:
            t_strict_i = t0  # already at/below zero and still declining now
        elif bi < -tol:
            s_star = -xi0 / bi
            t_strict_i = t0 + s_star if s_star < L - tol else None  # crosses strictly INSIDE this interval
        else:
            t_strict_i = None
        if t_strict_i is not None and (strict_time is None or t_strict_i < strict_time):
            strict_time = t_strict_i
    return touch_time, strict_time


@dataclass(frozen=True)
class NetworkPilotResult:
    strategy: str
    control_interval: float
    edge_failure: bool
    min_reserve: float
    min_reserve_time: float
    min_reserve_node: int
    first_touch_time: Optional[float]
    strict_violation_time: Optional[float]
    cumulative_cost: float
    cumulative_transported: float
    infeasible_intervals: List[Tuple[float, str]] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "strategy": self.strategy, "control_interval": self.control_interval, "edge_failure": self.edge_failure,
            "min_reserve": self.min_reserve, "min_reserve_time": self.min_reserve_time, "min_reserve_node": self.min_reserve_node,
            "first_touch_time": self.first_touch_time, "strict_violation_time": self.strict_violation_time,
            "cumulative_cost": self.cumulative_cost, "cumulative_transported": self.cumulative_transported,
            "infeasible_intervals": self.infeasible_intervals,
        }


def run_network_pilot(strategy: str, control_interval: float, edge_failure: bool) -> NetworkPilotResult:
    if strategy not in ("none", "fixed_routing", "optimized"):
        raise ScopeViolationError(f"unknown strategy {strategy!r}")
    _validate_control_interval(control_interval)

    B = NETWORK.incidence_matrix()
    x = np.array([0.6, 0.6, 0.6])
    n_steps = int(round(HORIZON / control_interval))

    min_reserve, min_reserve_time, min_reserve_node = float(np.min(x)), 0.0, int(np.argmin(x))
    first_touch_time: Optional[float] = None
    strict_violation_time: Optional[float] = None
    if np.any(x <= 1e-9):
        first_touch_time = 0.0
    if np.any(x < -1e-9):
        strict_violation_time = 0.0

    cumulative_cost = 0.0
    cumulative_transported = 0.0
    infeasible_intervals: List[Tuple[float, str]] = []

    for step in range(n_steps):
        t0 = step * control_interval
        d = _demand(t0)
        edge_cap = EDGE_CAP.copy()
        if edge_failure and 3.0 <= t0 < 4.0:
            edge_cap[1] = 0.0  # edge (1->2) blocked

        if strategy == "none":
            u, f = np.array([BASE_LOAD, BASE_LOAD, BASE_LOAD]), np.zeros(3)
        elif strategy == "fixed_routing":
            u, f = np.array([BASE_LOAD, BASE_LOAD, BASE_LOAD]), np.array([0.2, 0.2, 0.0])
            if edge_failure and 3.0 <= t0 < 4.0:
                f = np.array([0.2, 0.0, 0.0])  # the fixed rule cannot use the blocked edge either
        else:
            result = solve_network_qp(
                NETWORK, x_lower=x, d_upper=d, Delta=control_interval, u_max=U_MAX, edge_cap=edge_cap,
                total_supply_cap=TOTAL_SUPPLY_CAP, w=W, v=V, K=np.full(3, K_UPPER),
            )
            if result.status != "solved":
                infeasible_intervals.append((t0, result.status))
                u, f = np.array([BASE_LOAD, BASE_LOAD, BASE_LOAD]), np.zeros(3)  # fall back to baseline for propagation
            else:
                u, f = result.u, result.f
                if result.safety.status not in ("certified_safe", "boundary_touch"):
                    infeasible_intervals.append((t0, result.safety.status))

        # `x` here is always a CERTAIN (exactly known) state, even when one of its
        # components is already negative from an earlier real violation -- that is
        # NOT the same situation as a genuinely uncertain x_lower bound, so a plain
        # already-negative x is labeled "already_violated" here rather than reusing
        # whole_interval_safety's "not_certified" (which would otherwise both
        # mislabel the cause and -- via x_end_lower -- silently freeze propagation;
        # see resource_network_control.propagate_state's docstring).
        if np.any(x < -1e-9):
            interval_status = "already_violated"
        else:
            interval_status = whole_interval_safety(x, B, f, u, d, control_interval).status
        if interval_status not in ("certified_safe", "boundary_touch") and strategy != "optimized":
            infeasible_intervals.append((t0, interval_status))

        cumulative_cost += control_interval * float(np.sum(W * u ** 2) + np.sum(V * f ** 2))
        cumulative_transported += control_interval * float(np.sum(f))

        x_end = propagate_state(x, B, f, u, d, control_interval)
        t_end = t0 + control_interval

        # min_reserve: x is AFFINE within this interval (u,f,d all held constant),
        # so its extremum over [0,L] is always at one of the two endpoints -- no
        # exact-breakpoint machinery needed here, unlike C3's exponential case.
        if float(np.min(x_end)) < min_reserve:
            min_reserve, min_reserve_time, min_reserve_node = float(np.min(x_end)), t_end, int(np.argmin(x_end))

        # Exact affine touch/strict-violation event times (finding R6 fix, see
        # _affine_interval_events docstring) -- never snapped to the control grid.
        b = B @ f + u - d
        touch_i, strict_i = _affine_interval_events(x, b, control_interval, t0)
        if first_touch_time is None and touch_i is not None:
            first_touch_time = touch_i
        if strict_violation_time is None and strict_i is not None:
            strict_violation_time = strict_i

        x = x_end

    return NetworkPilotResult(
        strategy=strategy, control_interval=control_interval, edge_failure=edge_failure,
        min_reserve=min_reserve, min_reserve_time=min_reserve_time, min_reserve_node=min_reserve_node,
        first_touch_time=first_touch_time, strict_violation_time=strict_violation_time,
        cumulative_cost=cumulative_cost, cumulative_transported=cumulative_transported,
        infeasible_intervals=infeasible_intervals,
    )


__all__ = ["NETWORK", "NetworkPilotResult", "run_network_pilot"]
