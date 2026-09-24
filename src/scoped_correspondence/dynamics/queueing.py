"""Deterministic reflected fluid queue / backlog (DOMAIN_EXPANSION_ROADMAP.md Paket B2a).

Response to prompts/Answers/nicht_stationäre_Treiber/
SCF_DOMAIN_EXPANSION_IMPLEMENTATION_PLAN.md, section 8.2: "Wann verliert
eine gemittelte Lastbeschreibung die Information, die für ein kurzfristiges
Kapazitätsereignis nötig ist?"

For piecewise-constant arrival rate ``a(t)`` and service rate ``s(t)``, the
reflected fluid backlog satisfies, wherever it stays positive,

    dq/dt = a(t) - s(t),

with a reflecting lower barrier at ``q=0`` (a queue cannot go negative).
Within any interval where the net rate ``nu = a - s`` is CONSTANT, the
reflected process is exactly

    q(t+Delta) = max(0, q(t) + nu*Delta)                             (*)

This is exact for the WHOLE interval, not just an approximation: if
``nu >= 0`` the raw (unreflected) path never goes negative starting from
``q(t) >= 0``, so it never touches the barrier and (*) reduces to ordinary
linear growth. If ``nu < 0`` the raw path decreases monotonically; once it
would cross zero, reflection holds it AT exactly zero for the remainder of
the interval (still constant ``nu``, so it cannot rise back up on its own
within the same interval) — so the reflected trajectory over a
constant-rate interval is ALWAYS MONOTONIC (non-decreasing if ``nu>=0``,
non-increasing if ``nu<0``). This monotonicity is what makes exact,
sampling-free level-crossing detection possible: within one interval the
trajectory can cross any given level at most once, and the crossing time
solves a single linear equation.

**Genaue Aussage / Negativtest (plan section 4.2):** there are TWO distinct,
NOT-to-be-blended bridge stories built on the SAME ``q(t)`` trajectory:

1. **Direct identity** ``S ≡ q``: a stock literally equal to the backlog,
   ``dot(S) = I - O`` matching ``dot(q) = a - s``, with ``S=0`` ("empty")
   at exactly ``q=0`` -- the queue's own natural reflecting boundary.
2. **Remaining-reserve mapping** ``R = K - q`` (``stock_reserve_bridge``
   below): here ``R=0`` ("empty reserve") corresponds to ``q=K``, and
   ``R=K`` ("full reserve") corresponds to ``q=0`` -- the OPPOSITE
   correspondence from story 1. A constant outflow and a stock-dependent
   outflow ``k*S`` are NOT the same dynamics merely because both eventually
   "drain" — see ``verification/verify_queueing.py``'s
   ``negative_test_state_dependent_rate_differs``.

**Correction (2026-09-24, response to
prompts/Answers/nicht_stationäre_Treiber/SCF_Review_fcc9a43.md, minor
finding — an imprecise docstring claim, not a numerical bug):** an earlier
version of this docstring described both stories as "equivalent," which
incorrectly conflated ``q=0`` with "empty" under BOTH mappings at once (it
is only "empty" under story 1; under story 2 it is "full"). It also implied
``dot(R) = s - a`` holds as a blanket statement -- it does NOT hold AT the
queue's own reflecting boundary ``q=0``: there, a regulator term absorbs
the excess (``dq = (a-s)dt + dL``, ``dR = (s-a)dt - dL``, with ``dL``
active only while ``q=0``), so ``R`` stays pinned at ``K`` rather than
following ``s-a``. Example: ``q0=0, a=0, s=1, K=5`` keeps ``q≡0``
(reflected) and ``R≡5`` (constant) for as long as ``s>a`` -- NOT growing
at rate ``s-a=1`` as the un-regulated ODE would suggest. The VALUES
`stock_reserve_bridge` reports are unaffected by this (they are computed
as ``K - q(t)`` from the already-correctly-reflected ``q(t)``, never by
integrating the naive unreflected ODE) -- this correction is about the
docstring's own dynamical claim, not the returned numbers.
``stock_reserve_bridge`` below makes its OWN validity boundary
(``first_capacity_breach_time``, story 2's ``q=K``/``R=0`` event) explicit
rather than silently extending past it.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Sequence, Tuple

import numpy as np

from scoped_correspondence.errors import ScopeViolationError


@dataclass(frozen=True)
class FluidQueueTrajectory:
    """Exact piecewise-linear reflected backlog trajectory.

    ``breakpoints`` has length ``n+1`` (segment boundaries incl. start and
    end); ``segment_start_values``/``segment_end_values``/``net_rates`` each
    have length ``n``. Every quantity derived from this trajectory (value at
    an arbitrary time, first crossing of a level, the global peak) is
    computed EXACTLY from these closed-form linear segments — no sampling
    grid is involved anywhere in this module.
    """

    breakpoints: Tuple[float, ...]
    segment_start_values: Tuple[float, ...]
    segment_end_values: Tuple[float, ...]
    net_rates: Tuple[float, ...]

    def value_at(self, t: float) -> float:
        t = float(t)
        if t < self.breakpoints[0] or t > self.breakpoints[-1]:
            raise ScopeViolationError(
                f"value_at: t={t!r} outside trajectory range "
                f"[{self.breakpoints[0]}, {self.breakpoints[-1]}]"
            )
        for i in range(len(self.net_rates)):
            t0, t1 = self.breakpoints[i], self.breakpoints[i + 1]
            if t0 <= t <= t1:
                # Reflected: raw linear path clipped at 0. Monotonic per-segment (see
                # module docstring), so this closed form is exact even across the
                # reflection point within the segment.
                raw = self.segment_start_values[i] + self.net_rates[i] * (t - t0)
                return max(0.0, raw)
        raise ScopeViolationError(f"value_at: t={t!r} not covered by any segment")

    def first_upward_crossing(self, level: float) -> Optional[float]:
        """First ``t`` with ``q(t) >= level`` (closed boundary; the plan's
        ``tau_<=`` construction applied to reaching a level from below), or
        ``None`` if the level is never reached within the trajectory's horizon.
        """
        level = float(level)
        if self.segment_start_values[0] >= level:
            return self.breakpoints[0]
        for i in range(len(self.net_rates)):
            t0, t1 = self.breakpoints[i], self.breakpoints[i + 1]
            q0, nu = self.segment_start_values[i], self.net_rates[i]
            if q0 >= level:
                return t0
            if nu <= 0.0:
                continue  # monotonic non-increasing this segment; cannot rise to level > q0
            u = (level - q0) / nu
            dt = t1 - t0
            if 0.0 <= u <= dt:
                return t0 + u
        return None

    def peak(self) -> Tuple[float, float]:
        """Exact global maximum: since every segment is monotonic, extrema occur
        only at breakpoints."""
        values = list(self.segment_start_values) + [self.segment_end_values[-1]]
        idx = int(np.argmax(values))
        return self.breakpoints[idx], values[idx]


def fluid_queue_piecewise(
    initial_backlog: float,
    breakpoints: Sequence[float],
    arrival_rates: Sequence[float],
    service_rates: Sequence[float],
) -> FluidQueueTrajectory:
    """Exact reflected fluid backlog over piecewise-constant arrival/service rates.

    ``breakpoints`` are the ``n+1`` segment boundary times (strictly
    increasing); ``arrival_rates``/``service_rates`` give the constant rate
    on ``[breakpoints[i], breakpoints[i+1])`` for each of the ``n`` segments.
    """
    bp = [float(b) for b in breakpoints]
    a = [float(x) for x in arrival_rates]
    s = [float(x) for x in service_rates]
    initial_backlog = float(initial_backlog)
    if not np.isfinite(initial_backlog) or not all(np.isfinite(bp)) or not all(np.isfinite(a)) or not all(np.isfinite(s)):
        raise ScopeViolationError(
            "fluid_queue_piecewise: initial_backlog, breakpoints, arrival_rates, service_rates must all be finite"
        )
    if len(bp) < 2:
        raise ScopeViolationError("fluid_queue_piecewise: need at least 2 breakpoints (1 segment)")
    n = len(bp) - 1
    if len(a) != n or len(s) != n:
        raise ScopeViolationError(
            f"fluid_queue_piecewise: need {n} rates per array (len(breakpoints)-1); "
            f"got {len(a)} arrival rates, {len(s)} service rates"
        )
    for i in range(n):
        if bp[i + 1] <= bp[i]:
            raise ScopeViolationError(f"fluid_queue_piecewise: breakpoints must be strictly increasing; got {bp}")
    if any(x < 0.0 for x in a) or any(x < 0.0 for x in s):
        raise ScopeViolationError("fluid_queue_piecewise: arrival_rates and service_rates must all be >= 0")
    if initial_backlog < 0.0:
        raise ScopeViolationError(f"fluid_queue_piecewise: initial_backlog must be >= 0; got {initial_backlog!r}")

    q = float(initial_backlog)
    starts, ends, nus = [], [], []
    for i in range(n):
        nu = a[i] - s[i]
        dt = bp[i + 1] - bp[i]
        q_end = max(0.0, q + nu * dt)
        starts.append(q)
        ends.append(q_end)
        nus.append(nu)
        q = q_end

    return FluidQueueTrajectory(
        breakpoints=tuple(bp), segment_start_values=tuple(starts),
        segment_end_values=tuple(ends), net_rates=tuple(nus),
    )


@dataclass(frozen=True)
class StockReserveBridgeReport:
    """Bridge ``R(t) = K - q(t)`` (reserve remaining under a fixed capacity ``K``)
    from a fluid-queue backlog trajectory, up to the first point the bridge's
    own validity boundary is reached.

    **Preserved:** ``dot(R) = s - a`` exactly matches ``dot(q) = a - s`` up to
    sign, so every value of ``R`` reported here (``R(t) = K - q(t)`` for
    ``t <= first_capacity_breach_time``) is exact.

    **Lost / NOT extended automatically:** past ``first_capacity_breach_time``
    (where ``q`` first reaches ``K``, i.e. ``R`` first reaches ``0``), the
    fluid-QUEUE continuation (backlog keeps growing without limit, "R" keeps
    going negative) is generally NOT the same physical continuation as a
    bounded STOCK/reservoir that is empty (which cannot serve further demand
    at all — a distinct reflecting rule at the OTHER boundary). This report
    exposes ``first_capacity_breach_time`` explicitly rather than silently
    returning meaningless negative "reserve" values as though they still
    described a physical stock.
    """

    capacity: float
    reserve_values: Tuple[float, ...]
    at_times: Tuple[float, ...]
    first_capacity_breach_time: Optional[float]

    def valid_reserve_values(self) -> Tuple[Tuple[float, float], ...]:
        """Only the ``(t, R(t))`` pairs before the bridge's own validity boundary."""
        if self.first_capacity_breach_time is None:
            return tuple(zip(self.at_times, self.reserve_values))
        return tuple(
            (t, r) for t, r in zip(self.at_times, self.reserve_values)
            if t <= self.first_capacity_breach_time
        )


def stock_reserve_bridge(
    traj: FluidQueueTrajectory, capacity: float, at_times: Sequence[float]
) -> StockReserveBridgeReport:
    """``R(t) = capacity - q(t)`` at the requested times, with the bridge's own
    validity boundary (first time ``q`` reaches ``capacity``) reported explicitly
    rather than silently extended past it. See module/class docstrings.
    """
    capacity = float(capacity)
    if capacity <= 0.0:
        raise ScopeViolationError(f"stock_reserve_bridge: capacity must be > 0; got {capacity!r}")
    times = [float(t) for t in at_times]
    values = [capacity - traj.value_at(t) for t in times]
    breach = traj.first_upward_crossing(capacity)
    return StockReserveBridgeReport(
        capacity=capacity, reserve_values=tuple(values), at_times=tuple(times),
        first_capacity_breach_time=breach,
    )


__all__ = [
    "FluidQueueTrajectory", "fluid_queue_piecewise",
    "StockReserveBridgeReport", "stock_reserve_bridge",
]
