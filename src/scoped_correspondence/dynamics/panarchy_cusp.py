"""Panarchy / Adaptive-Cycle as Cusp extension (Milestone 35).

Interpretation layer over the corrected cubic normal form
``τ ẋ = -x³ + a x + b`` (``dynamics.core``; FORMALISM.md §5). Holling's
adaptive cycle (exploitation–conservation–release–reorganization) is
**qualitative**; the formal operationalization used here is the cusp
catastrophe geometry of Zwick & Hughes 2017 (fold / hysteresis as the
mathematical image of conservation→release).

This module **calls** ``fixed_points`` and ``CubicNormalForm.discriminant``
from ``dynamics.core`` only; it does **not** reimplement Cardano roots or
the cusp discriminant ``4a³ − 27b²``, and it does **not** edit
``dynamics/core.py``.

MANDATORY SCOPE FENCE (verbatim):
does NOT revive V≡Panarchy≡Onsager-L; interpretation layer only, no proven
ecological claim; Abstract-verified Zwick 2017 fulltext not seen.

Sources:
  - Holling 1973, Annu. Rev. Ecol. Syst. 4, 1–23;
    DOI 10.1146/annurev.es.04.110173.000245 (context only — qualitative).
  - Zwick & Hughes 2017, Proc. CSS;
    DOI 10.1145/3145574.3145591 (cusp formalization; Abstract-verified;
    fulltext not seen).

Out of scope: new symbol ``V_panarchy``; ecological proof claims;
mutating FORMALISM.md / thermo / Onsager-L; package-root ``__init__``.
"""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Sequence, Tuple

from scoped_correspondence.dynamics.core import CubicNormalForm, fixed_points
from scoped_correspondence.errors import ScopeViolationError

# Verbatim mandatory fence — must appear in module docstring AND as a text
# field in the verification JSON report.
PANARCHY_V_ONSAGER_WARNING: str = (
    "does NOT revive V≡Panarchy≡Onsager-L; interpretation layer only, no proven "
    "ecological claim; Abstract-verified Zwick 2017 fulltext not seen."
)

SOURCE = (
    "Holling 1973 DOI 10.1146/annurev.es.04.110173.000245 (context only); "
    "Zwick & Hughes 2017 DOI 10.1145/3145574.3145591"
)

_SCOPE_NOTES: tuple[str, ...] = (
    "formalization = cusp geometry via dynamics.core; "
    "Panarchy semantics = interpretation layer only",
    "CALL fixed_points + CubicNormalForm.discriminant; no reimplementation; "
    "dynamics/core.py not edited",
    "does NOT revive V≡Panarchy≡Onsager-L",
    "Holling 1973 qualitative context only; no proven ecological claim",
    "Zwick 2017 Abstract-verified; fulltext not seen",
    "no V_panarchy symbol; no thermo / Onsager-L identification",
)


def _cusp_discriminant(a: float, b: float) -> float:
    """Cusp discriminant ``4a³ − 27b²`` via ``CubicNormalForm.discriminant``.

    Does **not** recompute the polynomial; delegates to ``dynamics.core``.
    """
    return float(CubicNormalForm(float(a), float(b)).discriminant())


def fold_thresholds(a: float) -> Tuple[float, float]:
    """Fold (bifurcation) values of ``b`` for fixed ``a > 0``.

    On the cusp bifurcation set ``4a³ − 27b² = 0`` (discriminant zero),

        ``b_± = ± √(4a³ / 27)``.

    For the worked example ``a = 3`` this yields ``b_± = ±2``
    (equivalently ``± (2/√27) a^{3/2}``). Equilibria at ``b = 0`` are
    ``0, ±√a`` via ``fixed_points(a, 0)``.

    Parameters
    ----------
    a :
        Supercritical linear coefficient (``a > 0``). Required for real
        folds enclosing a bistable region.

    Returns
    -------
    (b_minus, b_plus) :
        Sorted pair ``(-√(4a³/27), +√(4a³/27))``.

    Raises
    ------
    ScopeViolationError
        If ``a ≤ 0`` (no real fold pair enclosing bistability).
    """
    aa = float(a)
    if aa <= 0.0:
        raise ScopeViolationError(
            f"fold_thresholds: requires a > 0 (bistable cusp region); got {a!r}"
        )
    # Closed form of discriminant = 0. Consistency with core is checked in
    # verify by evaluating CubicNormalForm(a, b_±).discriminant() ≈ 0.
    mag = math.sqrt((4.0 * aa**3) / 27.0)
    return (-mag, mag)


def _is_stable(x: float, a: float, tau: float = 1.0) -> bool:
    """Local asymptotic stability of cubic equilibrium: ``S_rec = (3x² − a)/τ > 0``."""
    return (3.0 * float(x) * float(x) - float(a)) / float(tau) > 1e-12


def _stable_equilibria(a: float, b: float) -> List[float]:
    """Stable real equilibria via ``fixed_points`` (CALL only)."""
    roots = fixed_points(float(a), float(b))
    return [float(r) for r in roots if _is_stable(r, a)]


@dataclass(frozen=True)
class HysteresisSample:
    """One sample along a hysteresis control path ``b ↦ x*(b)``."""

    b: float
    x: float
    n_equilibria: int
    n_stable: int
    discriminant: float
    jumped: bool


@dataclass(frozen=True)
class HysteresisSweepResult:
    """Result of ``hysteresis_sweep`` along a sequence of ``b`` values."""

    a: float
    fold_minus: float
    fold_plus: float
    samples: Tuple[HysteresisSample, ...]
    jump_indices: Tuple[int, ...]
    jump_b_values: Tuple[float, ...]
    scope_notes: Tuple[str, ...] = _SCOPE_NOTES

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["scope_notes"] = list(self.scope_notes)
        d["samples"] = [asdict(s) for s in self.samples]
        d["jump_indices"] = list(self.jump_indices)
        d["jump_b_values"] = list(self.jump_b_values)
        return d


def hysteresis_sweep(
    a: float,
    b_values: Sequence[float],
    *,
    x0: float | None = None,
) -> HysteresisSweepResult:
    """Track a quasi-static branch under slow ``b`` sweep (cusp hysteresis).

    At each ``b``, equilibria come from ``fixed_points(a, b)`` (CALL only).
    The selected state continues the previous branch by nearest-neighbour
    among **stable** roots. When the previous branch disappears at a fold
    (discriminant crossing through zero), the tracker jumps to the remaining
    stable equilibrium — the mathematical image of conservation→release in
    the Zwick cusp reading of the adaptive cycle.

    Jumps occur at the **fold thresholds**, not at ``b = 0``. Control paths
    that stay inside the fold pair (discriminant ``> 0``) while varying ``a``
    produce no jump without fold crossing (see verification).

    Parameters
    ----------
    a :
        Fixed cusp parameter ``a > 0``.
    b_values :
        Ordered control samples (e.g. ``-2 → +2 → -2`` for ``a = 3``).
    x0 :
        Optional initial state; default = largest stable root at the first
        ``b`` (upper branch start).

    Returns
    -------
    HysteresisSweepResult
        Samples, fold thresholds, and detected jump locations.

    Raises
    ------
    ScopeViolationError
        If ``a ≤ 0``, empty ``b_values``, or no stable equilibrium exists
        at the start of the sweep.
    """
    aa = float(a)
    if aa <= 0.0:
        raise ScopeViolationError(
            f"hysteresis_sweep: requires a > 0; got {a!r}"
        )
    bs = [float(b) for b in b_values]
    if not bs:
        raise ScopeViolationError("hysteresis_sweep: b_values must be non-empty")

    b_m, b_p = fold_thresholds(aa)
    samples: List[HysteresisSample] = []
    jump_indices: List[int] = []
    jump_b_values: List[float] = []

    # Initialize on a stable branch.
    roots0 = fixed_points(aa, bs[0])
    stable0 = _stable_equilibria(aa, bs[0])
    if not stable0:
        raise ScopeViolationError(
            f"hysteresis_sweep: no stable equilibrium at b={bs[0]!r}, a={aa!r}; "
            f"roots={roots0!r}"
        )
    if x0 is None:
        x_prev = max(stable0)
    else:
        x_prev = float(x0)
        # Snap to nearest stable root at start.
        x_prev = min(stable0, key=lambda r: abs(r - x_prev))

    for i, b in enumerate(bs):
        roots = fixed_points(aa, b)
        stable = _stable_equilibria(aa, b)
        disc = _cusp_discriminant(aa, b)
        jumped = False
        if not stable:
            raise ScopeViolationError(
                f"hysteresis_sweep: no stable equilibrium at b={b!r}, a={aa!r}"
            )
        # Prefer continuation of previous branch among stable roots.
        candidate = min(stable, key=lambda r: abs(r - x_prev))
        # Detect fold-induced jump: nearest stable is far from previous state
        # relative to inter-branch separation (order √a).
        sep = math.sqrt(max(aa, 0.0))
        if abs(candidate - x_prev) > 0.5 * sep and i > 0:
            # Confirm previous branch is gone: no stable root near x_prev.
            near_prev = [r for r in stable if abs(r - x_prev) <= 0.5 * sep]
            if not near_prev:
                jumped = True
                jump_indices.append(i)
                jump_b_values.append(b)
        x_sel = candidate
        samples.append(
            HysteresisSample(
                b=b,
                x=float(x_sel),
                n_equilibria=len(roots),
                n_stable=len(stable),
                discriminant=float(disc),
                jumped=jumped,
            )
        )
        x_prev = x_sel

    return HysteresisSweepResult(
        a=aa,
        fold_minus=float(b_m),
        fold_plus=float(b_p),
        samples=tuple(samples),
        jump_indices=tuple(jump_indices),
        jump_b_values=tuple(jump_b_values),
        scope_notes=_SCOPE_NOTES,
    )


def control_path_no_fold_crossing(
    a_values: Sequence[float],
    b: float,
    *,
    x0: float | None = None,
) -> Dict[str, Any]:
    """Vary ``a`` at fixed ``b`` **inside** the fold pair — no hysteresis jump.

    Requires ``|b| < fold_thresholds(a).plus`` for every ``a`` in the path
    (strictly inside the bistable region). Tracks one stable branch; reports
    ``any_jump=False`` when no fold is crossed.

    Parameters
    ----------
    a_values :
        Ordered supercritical ``a > 0`` samples.
    b :
        Fixed asymmetry parameter with ``|b|`` inside all fold pairs.
    x0 :
        Optional initial state on a stable branch.

    Returns
    -------
    dict
        ``a_values``, ``b``, ``x_path``, ``discriminants``, ``any_jump``,
        ``fold_ok``.
    """
    aa_list = [float(a) for a in a_values]
    bb = float(b)
    if not aa_list:
        raise ScopeViolationError("control_path_no_fold_crossing: a_values empty")
    for aa in aa_list:
        if aa <= 0.0:
            raise ScopeViolationError(
                f"control_path_no_fold_crossing: requires a > 0; got {aa!r}"
            )
        b_m, b_p = fold_thresholds(aa)
        if not (b_m < bb < b_p):
            raise ScopeViolationError(
                f"control_path_no_fold_crossing: b={bb!r} not strictly inside "
                f"folds ({b_m!r}, {b_p!r}) for a={aa!r}"
            )

    x_path: List[float] = []
    discs: List[float] = []
    any_jump = False
    x_prev: float | None = None
    for i, aa in enumerate(aa_list):
        stable = _stable_equilibria(aa, bb)
        if not stable:
            raise ScopeViolationError(
                f"control_path_no_fold_crossing: no stable eq at a={aa!r}, b={bb!r}"
            )
        if x_prev is None:
            if x0 is None:
                x_sel = max(stable)
            else:
                x_sel = min(stable, key=lambda r: abs(r - float(x0)))
        else:
            x_sel = min(stable, key=lambda r: abs(r - x_prev))
            sep = math.sqrt(aa)
            if abs(x_sel - x_prev) > 0.5 * sep:
                near = [r for r in stable if abs(r - x_prev) <= 0.5 * sep]
                if not near:
                    any_jump = True
        x_path.append(float(x_sel))
        discs.append(_cusp_discriminant(aa, bb))
        x_prev = x_sel
        _ = i

    return {
        "a_values": aa_list,
        "b": bb,
        "x_path": x_path,
        "discriminants": discs,
        "any_jump": bool(any_jump),
        "fold_ok": all(d > 0.0 for d in discs),
        "scope_notes": list(_SCOPE_NOTES),
    }


__all__ = [
    "PANARCHY_V_ONSAGER_WARNING",
    "SOURCE",
    "HysteresisSample",
    "HysteresisSweepResult",
    "fold_thresholds",
    "hysteresis_sweep",
    "control_path_no_fold_crossing",
]
