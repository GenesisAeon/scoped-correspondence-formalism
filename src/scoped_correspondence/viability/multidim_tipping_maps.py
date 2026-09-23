"""Multidimensional R-tipping / viability response surfaces (Milestone 54).

MECHANISTIC_VALIDATION_ROADMAP.md package 6, response to
prompts/Answers/nicht_stationäre_Treiber/SCF_Review_3e8dce3.md (Astra,
2026-09-23): "Paket 6 ist bereits der passende nächste größere Inhalt.
Besonders informativ wären Schnitte bei gleicher Spitzenlast und bei
gleicher integrierter Last. Ergebniszustände sollten mindestens Tracking,
Wechsel, noch nicht entschieden, außerhalb des Scopes und
Integrationsfehler unterscheiden." Also directly closes the open item in
docs/rate_dependent_tipping.md: "A full characterization would need a
response surface over amplitude AND duration jointly, not a single 1D
sweep in either direction alone."

This module does NOT reimplement the underlying dynamics --
``viability.rate_dependent_buffer`` and ``dynamics.rate_dependent`` are
imported and called UNCHANGED, per this repo's discipline of composing
existing, already-verified building blocks rather than duplicating them.
It adds two things neither module had: (1) a genuine 2-D grid instead of
single 1-D sweeps, varying amplitude/duration/reserve as SEPARATE axes,
with each amplitude convention (fixed peak height vs. fixed total load)
kept as its own explicitly-labeled slice rather than conflated; (2) a
5-way outcome classification (TRACKING, SWITCHED, UNRESOLVED,
OUT_OF_SCOPE, INTEGRATION_ERROR) instead of a bare boolean, so numerical
uncertainty near a boundary and genuine scope violations are surfaced
rather than silently forced into "safe" or "breach".

HAND-VERIFIED SIMPLIFICATION: the buffer boundary ``b`` does not appear
anywhere in ``run_buffer_spike_trajectory``'s ODE
(``z_dot = -r(z-z_eq) + U - W(t)``) -- only in the after-the-fact
``z_min < b`` comparison. This means sweeping the RESERVE axis never
needs a new integration: one trajectory per (amplitude, tau) cell already
determines the outcome for EVERY value of ``b`` simultaneously (the
critical reserve is exactly ``b* = z_min``). ``buffer_reserve_frontier``
exploits this directly instead of re-integrating per ``b`` value.

Global threshold geometry (edge states, connecting orbits; Wieczorek, Xie
& Ashwin 2023) is explicitly NOT attempted here -- these are empirically
determined boundaries from a finite grid of trajectories, not a proven
global geometric characterization. Flagged as follow-up, not silently
implied.

CORRECTION (2026-09-23, external follow-up review by Astra,
SCF_Followup_1231f64.md): the initial version of this module classified
buffer cells using a GLOBAL grid-max ODE-refinement difference as the
uncertainty proxy, while ``run_buffer_spike_trajectory`` located the
trajectory minimum via a fixed 4001-point grid argmin. A closed-form
counterexample showed the grid-based minimum can differ from the true
continuous minimum by ~100x the uncertainty band being used to decide
trustworthiness -- enough to misclassify a genuine boundary breach as
safe right at the margin. Fixed at the source
(``rate_dependent_buffer.run_buffer_spike_trajectory`` now finds the
TRUE continuous minimum via bounded scalar optimization on the dense ODE
solution) and classification here now uses the ODE uncertainty EVALUATED
AT that minimum's own time (``z_min_ode_uncertainty``), not a global grid
maximum. See ``verify_multidim_tipping_maps.py``'s
``buffer_continuous_minimum_regression`` check, which uses Astra's own
closed-form Gaussian-pulse convolution as an independent oracle.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Sequence, Tuple

import numpy as np

from scoped_correspondence.errors import ScopeViolationError
from scoped_correspondence.dynamics.rate_dependent import (
    SOURCE as RATE_DEPENDENT_SOURCE,
    TrackingResult,
    rate_induced_tipping_cubic_example,
)
from scoped_correspondence.viability.core import has_safe_transfer
from scoped_correspondence.viability.rate_dependent_buffer import (
    BufferSpikeTrajectory,
    equal_total_load_height,
    run_buffer_spike_trajectory,
)

SOURCE = RATE_DEPENDENT_SOURCE

TRACKING = "tracking"
SWITCHED = "switched"
UNRESOLVED = "unresolved"
OUT_OF_SCOPE = "out_of_scope"
INTEGRATION_ERROR = "integration_error"

_VALID_OUTCOMES = (TRACKING, SWITCHED, UNRESOLVED, OUT_OF_SCOPE, INTEGRATION_ERROR)

# How many multiples of the trajectory's own coarse/fine refinement
# difference the margin to the boundary must exceed before a classification
# is trusted -- inside this band, numerical uncertainty alone could flip the
# verdict, so it is reported as UNRESOLVED rather than guessed.
DEFAULT_UNRESOLVED_SAFETY_FACTOR = 10.0


# --------------------------------------------------------------------------
# Buffer spike (viability.rate_dependent_buffer) response surfaces
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class BufferMapCell:
    tau: float
    amplitude_param: float  # spike_height (peak mode) or total_extra_load (total-load mode)
    spike_height: float
    z_min: float
    outcome: str
    z_min_ode_uncertainty: float
    z_min_grid_search_error: float
    margin_to_boundary: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tau": self.tau,
            "amplitude_param": self.amplitude_param,
            "spike_height": self.spike_height,
            "z_min": self.z_min,
            "outcome": self.outcome,
            "z_min_ode_uncertainty": self.z_min_ode_uncertainty,
            "z_min_grid_search_error": self.z_min_grid_search_error,
            "margin_to_boundary": self.margin_to_boundary,
        }


@dataclass(frozen=True)
class BufferResponseSurface:
    amplitude_mode: str  # "peak_height" | "total_load"
    r: float
    z_eq: float
    U: float
    W0: float
    b: float
    taus: Tuple[float, ...]
    amplitude_params: Tuple[float, ...]
    cells: Tuple[BufferMapCell, ...]  # row-major: tau-major, amplitude-minor

    def to_dict(self) -> Dict[str, Any]:
        return {
            "amplitude_mode": self.amplitude_mode,
            "r": self.r,
            "z_eq": self.z_eq,
            "U": self.U,
            "W0": self.W0,
            "b": self.b,
            "taus": list(self.taus),
            "amplitude_params": list(self.amplitude_params),
            "cells": [c.to_dict() for c in self.cells],
        }

    def outcome_grid(self) -> List[List[str]]:
        """[row=tau][col=amplitude_param] outcome labels, for compact display."""
        n_amp = len(self.amplitude_params)
        return [
            [c.outcome for c in self.cells[i * n_amp : (i + 1) * n_amp]]
            for i in range(len(self.taus))
        ]


def _classify_buffer_cell(
    z_min: float,
    z_min_uncertainty: float,
    b: float,
    *,
    baseline_frozen_safe: bool,
    unresolved_safety_factor: float,
) -> str:
    """Classify by margin = z_min - b against an uncertainty-scaled tolerance.

    ``z_min_uncertainty`` must be the uncertainty of ``z_min`` ITSELF (its
    ODE-tolerance error at the located minimum's time -- see
    ``BufferSpikeTrajectory.z_min_ode_uncertainty``), not a global,
    grid-max refinement difference that need not bound the error AT the
    minimum specifically (Astra, SCF_Followup_1231f64.md).
    """
    if not baseline_frozen_safe:
        return OUT_OF_SCOPE
    margin = z_min - b
    tol = unresolved_safety_factor * z_min_uncertainty
    if abs(margin) <= tol:
        return UNRESOLVED
    return TRACKING if margin > 0 else SWITCHED


def _buffer_cell(
    r: float,
    z_eq: float,
    U: float,
    W0: float,
    b: float,
    spike_height: float,
    tau: float,
    amplitude_param: float,
    *,
    unresolved_safety_factor: float,
) -> BufferMapCell:
    baseline = has_safe_transfer(r, z_eq, b, U, W0)
    baseline_safe = bool(baseline["ok"])
    try:
        traj: BufferSpikeTrajectory = run_buffer_spike_trajectory(r, z_eq, U, W0, spike_height, tau)
    except ScopeViolationError:
        return BufferMapCell(
            tau=tau,
            amplitude_param=amplitude_param,
            spike_height=spike_height,
            z_min=float("nan"),
            outcome=INTEGRATION_ERROR,
            z_min_ode_uncertainty=float("nan"),
            z_min_grid_search_error=float("nan"),
            margin_to_boundary=float("nan"),
        )
    outcome = _classify_buffer_cell(
        traj.z_min,
        traj.z_min_ode_uncertainty,
        b,
        baseline_frozen_safe=baseline_safe,
        unresolved_safety_factor=unresolved_safety_factor,
    )
    return BufferMapCell(
        tau=tau,
        amplitude_param=amplitude_param,
        spike_height=spike_height,
        z_min=traj.z_min,
        outcome=outcome,
        z_min_ode_uncertainty=traj.z_min_ode_uncertainty,
        z_min_grid_search_error=traj.z_min_grid_search_error,
        margin_to_boundary=traj.z_min - b,
    )


def buffer_response_surface(
    r: float,
    z_eq: float,
    U: float,
    W0: float,
    b: float,
    taus: Sequence[float],
    amplitude_params: Sequence[float],
    *,
    amplitude_mode: str = "peak_height",
    unresolved_safety_factor: float = DEFAULT_UNRESOLVED_SAFETY_FACTOR,
) -> BufferResponseSurface:
    """2-D (tau x amplitude) response surface at a FIXED reserve ``b``.

    ``amplitude_mode="peak_height"``: ``amplitude_params`` are
    ``spike_height`` values directly ("Schnitte bei gleicher Spitzenlast"
    -- each column is one fixed peak height, swept across tau).
    ``amplitude_mode="total_load"``: ``amplitude_params`` are total extra
    load values, converted per-tau via
    ``equal_total_load_height`` ("Schnitte bei gleicher integrierter
    Last") -- so the SAME column represents the same total delivered load
    at every tau, with the peak height varying instead.

    Every cell is computed from an independent, freshly-integrated
    trajectory (this module calls ``run_buffer_spike_trajectory``
    unchanged) -- no interpolation between grid points.
    """
    if amplitude_mode not in ("peak_height", "total_load"):
        raise ScopeViolationError(f"buffer_response_surface: amplitude_mode must be 'peak_height' or 'total_load'; got {amplitude_mode!r}")
    if len(taus) < 1 or len(amplitude_params) < 1:
        raise ScopeViolationError("buffer_response_surface: taus and amplitude_params must be non-empty")
    for t in taus:
        if not (np.isfinite(t) and t > 0.0):
            raise ScopeViolationError(f"buffer_response_surface: all taus must be finite and > 0; got {t!r}")
    for a in amplitude_params:
        if not (np.isfinite(a) and a > 0.0):
            raise ScopeViolationError(f"buffer_response_surface: all amplitude_params must be finite and > 0; got {a!r}")

    cells: List[BufferMapCell] = []
    for tau in taus:
        for amp in amplitude_params:
            spike_height = float(amp) if amplitude_mode == "peak_height" else equal_total_load_height(float(amp), float(tau))
            cells.append(
                _buffer_cell(
                    r, z_eq, U, W0, b, spike_height, float(tau), float(amp),
                    unresolved_safety_factor=unresolved_safety_factor,
                )
            )

    return BufferResponseSurface(
        amplitude_mode=amplitude_mode,
        r=r, z_eq=z_eq, U=U, W0=W0, b=b,
        taus=tuple(float(t) for t in taus),
        amplitude_params=tuple(float(a) for a in amplitude_params),
        cells=tuple(cells),
    )


@dataclass(frozen=True)
class ReserveFrontierPoint:
    b: float
    outcome: str
    margin_to_boundary: float

    def to_dict(self) -> Dict[str, Any]:
        return {"b": self.b, "outcome": self.outcome, "margin_to_boundary": self.margin_to_boundary}


@dataclass(frozen=True)
class ReserveFrontierReport:
    r: float
    z_eq: float
    U: float
    W0: float
    spike_height: float
    tau: float
    z_min: float
    critical_b: float
    z_min_ode_uncertainty: float
    z_min_grid_search_error: float
    points: Tuple[ReserveFrontierPoint, ...]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "r": self.r, "z_eq": self.z_eq, "U": self.U, "W0": self.W0,
            "spike_height": self.spike_height, "tau": self.tau,
            "z_min": self.z_min, "critical_b": self.critical_b,
            "z_min_ode_uncertainty": self.z_min_ode_uncertainty,
            "z_min_grid_search_error": self.z_min_grid_search_error,
            "points": [p.to_dict() for p in self.points],
        }


def buffer_reserve_frontier(
    r: float, z_eq: float, U: float, W0: float, spike_height: float, tau: float,
    b_values: Sequence[float],
    *,
    unresolved_safety_factor: float = DEFAULT_UNRESOLVED_SAFETY_FACTOR,
) -> ReserveFrontierReport:
    """Reserve (``b``) sweep at FIXED amplitude/tempo -- needs only ONE integration.

    ``b`` does not appear in ``run_buffer_spike_trajectory``'s ODE, only in
    the after-the-fact boundary comparison -- so the critical reserve is
    EXACTLY the trajectory's own minimum, ``critical_b = z_min``, with no
    root-finding needed. This is verified directly against a sign check at
    each supplied ``b`` value: since ``margin = z_min - b``, a boundary
    BELOW ``z_min`` leaves positive margin (TRACKING), a boundary ABOVE
    ``z_min`` leaves negative margin (SWITCHED) -- up to the numerical
    uncertainty tolerance -- rather than assumed.

    Corrected 2026-09-23 (Astra, SCF_Followup_1231f64.md): this docstring
    previously swapped "above"/"below" relative to ``z_min``; the
    implementation and its verify-script sign check always had the
    direction right, only this text was wrong.
    """
    if len(b_values) < 1:
        raise ScopeViolationError("buffer_reserve_frontier: b_values must be non-empty")
    traj = run_buffer_spike_trajectory(r, z_eq, U, W0, spike_height, tau)
    points = []
    for b in b_values:
        baseline = has_safe_transfer(r, z_eq, float(b), U, W0)
        outcome = _classify_buffer_cell(
            traj.z_min, traj.z_min_ode_uncertainty, float(b),
            baseline_frozen_safe=bool(baseline["ok"]),
            unresolved_safety_factor=unresolved_safety_factor,
        )
        points.append(ReserveFrontierPoint(b=float(b), outcome=outcome, margin_to_boundary=traj.z_min - float(b)))
    return ReserveFrontierReport(
        r=r, z_eq=z_eq, U=U, W0=W0, spike_height=spike_height, tau=tau,
        z_min=traj.z_min, critical_b=traj.z_min,
        z_min_ode_uncertainty=traj.z_min_ode_uncertainty,
        z_min_grid_search_error=traj.z_min_grid_search_error,
        points=tuple(points),
    )


# --------------------------------------------------------------------------
# Rate-induced tipping cubic example (dynamics.rate_dependent) response surface
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class CubicMapCell:
    r: float
    x0_offset: float
    final_relative_x: float
    outcome: str
    refinement_max_difference: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "r": self.r,
            "x0_offset": self.x0_offset,
            "final_relative_x": self.final_relative_x,
            "outcome": self.outcome,
            "refinement_max_difference": self.refinement_max_difference,
        }


@dataclass(frozen=True)
class CubicResponseSurface:
    rs: Tuple[float, ...]
    x0_offsets: Tuple[float, ...]
    margin: float
    cells: Tuple[CubicMapCell, ...]  # row-major: r-major, x0_offset-minor

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rs": list(self.rs),
            "x0_offsets": list(self.x0_offsets),
            "margin": self.margin,
            "cells": [c.to_dict() for c in self.cells],
        }

    def outcome_grid(self) -> List[List[str]]:
        n_x0 = len(self.x0_offsets)
        return [
            [c.outcome for c in self.cells[i * n_x0 : (i + 1) * n_x0]]
            for i in range(len(self.rs))
        ]


def _classify_cubic_cell(result: TrackingResult, *, unresolved_safety_factor: float) -> str:
    # Stable branches sit exactly 2 apart in x-u (at +1 and -1); the
    # unstable branch (the actual decision boundary) is exactly midway, at
    # x-u=0 -- so the margin to the NEAREST side of that boundary is
    # |final_relative_x| itself, regardless of which branch was tracked.
    margin = abs(result.final_relative_x)
    tol = unresolved_safety_factor * result.refinement_max_difference
    if margin <= tol:
        return UNRESOLVED
    return SWITCHED if result.switched else TRACKING


def tracking_response_surface(
    rs: Sequence[float],
    x0_offsets: Sequence[float],
    *,
    margin: float = 10.0,
    unresolved_safety_factor: float = DEFAULT_UNRESOLVED_SAFETY_FACTOR,
) -> CubicResponseSurface:
    """2-D (r x x0_offset) tracking/switching map for the canonical cubic example.

    ``x0_offset`` (the starting distance above the driver, i.e. how far
    onto the upper stable branch the trajectory begins) plays the role of
    a RESERVE axis here: ``x0_offset=1.0`` starts exactly on the stable
    branch (the module's original default); ``x0_offset`` closer to 0
    starts closer to the unstable branch (the boundary) and is
    conservative to expect switching from; ``x0_offset`` above 1 starts
    further from the boundary. ``r`` remains the RATE axis. Reuses
    ``rate_induced_tipping_cubic_example`` UNCHANGED per grid cell.
    """
    if len(rs) < 1 or len(x0_offsets) < 1:
        raise ScopeViolationError("tracking_response_surface: rs and x0_offsets must be non-empty")
    for r in rs:
        if not (np.isfinite(r) and r > 0.0):
            raise ScopeViolationError(f"tracking_response_surface: all rs must be finite and > 0; got {r!r}")

    cells: List[CubicMapCell] = []
    for r in rs:
        for x0 in x0_offsets:
            try:
                result = rate_induced_tipping_cubic_example(float(r), x0_offset=float(x0), margin=margin)
            except ScopeViolationError as exc:
                # rate_induced_tipping_cubic_example wraps two DIFFERENT
                # failure modes in the same exception type: integrate_trajectory
                # raises "solve_ivp failed: ..." on a genuine solver failure;
                # classify_tracking raises "... is not within tol=... of any
                # stable frozen equilibrium ..." when the trajectory has NOT
                # yet settled near either known branch by t1 (a real,
                # empirically-encountered case at r=0.75, x0_offset=0.6,
                # margin=3.0 -- not manufactured). These are conceptually
                # different: the first is INTEGRATION_ERROR, the second is
                # exactly Astra's "noch nicht entschieden" (UNRESOLVED) --
                # distinguished here by message content since the underlying,
                # already-verified module is reused unchanged rather than
                # edited to expose a structured failure reason.
                msg = str(exc)
                outcome = UNRESOLVED if "classify_tracking" in msg else INTEGRATION_ERROR
                cells.append(
                    CubicMapCell(r=float(r), x0_offset=float(x0), final_relative_x=float("nan"), outcome=outcome, refinement_max_difference=float("nan"))
                )
                continue
            outcome = _classify_cubic_cell(result, unresolved_safety_factor=unresolved_safety_factor)
            cells.append(
                CubicMapCell(
                    r=float(r), x0_offset=float(x0),
                    final_relative_x=result.final_relative_x,
                    outcome=outcome,
                    refinement_max_difference=result.refinement_max_difference,
                )
            )
    return CubicResponseSurface(rs=tuple(float(r) for r in rs), x0_offsets=tuple(float(x) for x in x0_offsets), margin=margin, cells=tuple(cells))


__all__ = [
    "SOURCE",
    "TRACKING",
    "SWITCHED",
    "UNRESOLVED",
    "OUT_OF_SCOPE",
    "INTEGRATION_ERROR",
    "DEFAULT_UNRESOLVED_SAFETY_FACTOR",
    "BufferMapCell",
    "BufferResponseSurface",
    "buffer_response_surface",
    "ReserveFrontierPoint",
    "ReserveFrontierReport",
    "buffer_reserve_frontier",
    "CubicMapCell",
    "CubicResponseSurface",
    "tracking_response_surface",
]
