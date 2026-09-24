"""Queueing pilot: mean load vs. transient event risk, side by side (DOMAIN_EXPANSION_ROADMAP.md Paket B2).

Ties together ``dynamics.queueing`` (deterministic reflected fluid backlog)
and ``viability.first_passage_ctmc`` (stochastic M/M/1 first-passage) on a
SHARED question: does a mean-load description tell you what you need to
know about a short-term capacity event? Three models, kept explicitly
distinct rather than blended into one "queue score" (plan section 8.1):

- **deterministic_fluid_backlog** -- exact, no randomness; answers "does the
  reflected mean-flow trajectory itself cross the boundary?"
- **stochastic_hitting_probability** -- exact CTMC first-passage
  probability for the SAME mean arrival/service rates; answers "how likely
  is a boundary crossing, given the same average rates?"
- A mean/fluid model must never be reported as a "safety proof" for the
  stochastic question -- ``QueueingPilotReport`` keeps the two numbers in
  separate fields with no combined pass/fail collapsing them.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from scoped_correspondence.dynamics.queueing import fluid_queue_piecewise
from scoped_correspondence.viability.first_passage_ctmc import queue_hitting_probability
from scoped_correspondence.errors import ScopeViolationError


@dataclass(frozen=True)
class QueueingPilotReport:
    initial_count: float
    threshold: float
    horizon: float
    arrival_rate: float
    service_rate: float
    deterministic_peak_backlog: float
    deterministic_peak_time: float
    deterministic_boundary_crossed: bool
    stochastic_hitting_probability: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "initial_count": self.initial_count, "threshold": self.threshold, "horizon": self.horizon,
            "arrival_rate": self.arrival_rate, "service_rate": self.service_rate,
            "deterministic_peak_backlog": self.deterministic_peak_backlog,
            "deterministic_peak_time": self.deterministic_peak_time,
            "deterministic_boundary_crossed": self.deterministic_boundary_crossed,
            "stochastic_hitting_probability": self.stochastic_hitting_probability,
        }


def run_queueing_pilot(
    initial_count: float, threshold: float, horizon: float, arrival_rate: float, service_rate: float
) -> QueueingPilotReport:
    """Evaluate the SAME mean arrival/service rates under both the deterministic
    fluid backlog and the stochastic M/M/1 first-passage model, over ``[0, horizon]``.
    """
    if horizon <= 0.0:
        raise ScopeViolationError(f"run_queueing_pilot: horizon must be > 0; got {horizon!r}")

    fluid_traj = fluid_queue_piecewise(initial_count, [0.0, horizon], [arrival_rate], [service_rate])
    peak_time, peak_value = fluid_traj.peak()

    stochastic_p = queue_hitting_probability(
        int(round(initial_count)), int(round(threshold)), horizon, arrival_rate, service_rate
    )

    return QueueingPilotReport(
        initial_count=initial_count, threshold=threshold, horizon=horizon,
        arrival_rate=arrival_rate, service_rate=service_rate,
        deterministic_peak_backlog=peak_value, deterministic_peak_time=peak_time,
        deterministic_boundary_crossed=peak_value >= threshold,
        stochastic_hitting_probability=stochastic_p,
    )


__all__ = ["QueueingPilotReport", "run_queueing_pilot"]
