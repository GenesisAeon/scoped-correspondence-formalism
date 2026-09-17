"""Dirac structure composition via skew-symmetric J interconnection (Milestone 12).

Maps Cervera, van der Schaft & Baños 2007
(DOI 10.1016/j.automatica.2006.08.014): power-conserving interconnection of
port-Hamiltonian systems yields a Dirac structure that is the composition of
the subsystem Dirac structures. For input-state-output PH systems the Dirac
structure is the graph of a skew-symmetric map involving J and the port map g;
composition under the standard feedback interconnection

    u1 = -y2,  u2 = y1

preserves skew-symmetry of the closed-loop structure matrix J_total and
annihilates interface power (y1·u1 + y2·u2 = 0).

This module implements **only** skew-symmetric J composition (no M / resistive
claims). Antisymmetry of J_total is verified by calling
``check_generic_structure`` (``coupling/core.py`` unchanged) and reading the
``J_antisymmetric`` flag; M-related flags are not interpreted as M12 claims.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Optional, Sequence, Union

import numpy as np

from scoped_correspondence.coupling.core import (
    GENERIC_STRUCTURE_TOL,
    check_generic_structure,
)
from scoped_correspondence.errors import ScopeViolationError

FEEDBACK = "feedback"
SOURCE = (
    "Cervera, van der Schaft & Baños 2007, "
    "DOI 10.1016/j.automatica.2006.08.014"
)

_DEFAULT_ASSUMPTIONS: tuple[str, ...] = (
    "J composition only — no M / resistive / GENERIC-model claim",
    "power-preserving feedback interconnection: u1=-y2, u2=y1 "
    "(y1·u1 + y2·u2 = 0 identically)",
    "antisymmetry of J_total verified via check_generic_structure "
    "J_antisymmetric flag only (coupling/core.py called, not edited)",
    "Dirac / port-Hamiltonian composition specialty "
    "(Cervera et al. 2007); not a bond-graph library",
)


@dataclass(frozen=True)
class PowerPreservingInterconnection:
    """Standard feedback interconnection of two power ports.

    Constraints
    -----------
    ``u1 = -y2``, ``u2 = y1``  ⇒  ``y1·u1 + y2·u2 = 0`` identically.

    Port maps ``g1`` (shape ``(n1, m)``) and ``g2`` (shape ``(n2, m)``)
    enter the closed-loop structure as off-diagonal blocks
    ``± g1 g2ᵀ`` / ``± g2 g1ᵀ``.  When omitted, both default to the
    identity of size ``n1`` (requires ``n1 == n2``).
    """

    kind: str = FEEDBACK
    g1: Optional[np.ndarray] = None
    g2: Optional[np.ndarray] = None

    def __post_init__(self) -> None:
        if self.kind != FEEDBACK:
            raise ScopeViolationError(
                f"PowerPreservingInterconnection: only kind={FEEDBACK!r} "
                f"is supported; got {self.kind!r}"
            )
        if self.g1 is not None:
            object.__setattr__(self, "g1", np.asarray(self.g1, dtype=float))
        if self.g2 is not None:
            object.__setattr__(self, "g2", np.asarray(self.g2, dtype=float))


@dataclass(frozen=True)
class DiracCompositionResult:
    """Result of composing two skew-symmetric structure matrices.

    ``ok`` mirrors ``antisymmetry_report['J_antisymmetric']`` only.
    M-related keys in ``antisymmetry_report`` are present because
    ``check_generic_structure`` requires an M argument; they are **not**
    M12 claims (see ``disclaimer``).
    """

    J_total: np.ndarray
    interconnection: PowerPreservingInterconnection
    antisymmetry_report: dict
    ok: bool  # J_total skew (J_antisymmetric)
    interface_power_max_abs: float
    assumptions: tuple[str, ...]
    source: str = SOURCE
    disclaimer: str = (
        "J composition / skew check only; does not assert a resistive M "
        "structure, Jacobi identity beyond J^T=-J, or that an arbitrary "
        "model is GENERIC / Dirac (coupling_layer_afet.md §8 analogue)."
    )


def _as_square(J: np.ndarray, name: str) -> np.ndarray:
    J = np.asarray(J, dtype=float)
    if J.ndim != 2 or J.shape[0] != J.shape[1]:
        raise ScopeViolationError(
            f"compose_skew_symmetric: {name} must be square; got {J.shape}"
        )
    return J


def _require_skew(J: np.ndarray, name: str, tol: float) -> None:
    """Pre-check that J is skew; uses check_generic_structure (call only)."""
    n = J.shape[0]
    M0 = np.zeros((n, n), dtype=float)
    z = np.zeros(n, dtype=float)
    report = check_generic_structure(J, M0, z, z, tol=tol)
    if not report["J_antisymmetric"]:
        raise ScopeViolationError(
            f"compose_skew_symmetric: {name} is not antisymmetric within "
            f"tol={tol}; residual={report['residuals']['max_abs_J_T_plus_J']}"
        )


def _parse_interconnection(
    interconnection: Union[str, Mapping[str, Any], PowerPreservingInterconnection],
) -> PowerPreservingInterconnection:
    if isinstance(interconnection, PowerPreservingInterconnection):
        return interconnection
    if isinstance(interconnection, str):
        if interconnection != FEEDBACK:
            raise ScopeViolationError(
                f"compose_skew_symmetric: interconnection string must be "
                f"{FEEDBACK!r}; got {interconnection!r}"
            )
        return PowerPreservingInterconnection(kind=FEEDBACK)
    if isinstance(interconnection, Mapping):
        kind = str(interconnection.get("kind", FEEDBACK))
        return PowerPreservingInterconnection(
            kind=kind,
            g1=interconnection.get("g1"),
            g2=interconnection.get("g2"),
        )
    raise ScopeViolationError(
        "compose_skew_symmetric: interconnection must be "
        f"{FEEDBACK!r}, a mapping, or PowerPreservingInterconnection"
    )


def _resolve_ports(
    n1: int,
    n2: int,
    ic: PowerPreservingInterconnection,
) -> tuple[np.ndarray, np.ndarray]:
    if ic.g1 is None and ic.g2 is None:
        if n1 != n2:
            raise ScopeViolationError(
                "compose_skew_symmetric: default identity ports require "
                f"n1==n2; got n1={n1}, n2={n2}. Pass g1, g2 with equal "
                "column count m."
            )
        eye = np.eye(n1, dtype=float)
        return eye, eye
    if ic.g1 is None or ic.g2 is None:
        raise ScopeViolationError(
            "compose_skew_symmetric: supply both g1 and g2, or neither"
        )
    g1 = np.asarray(ic.g1, dtype=float)
    g2 = np.asarray(ic.g2, dtype=float)
    if g1.ndim != 2 or g1.shape[0] != n1:
        raise ScopeViolationError(
            f"compose_skew_symmetric: g1 shape must be (n1, m)=({n1}, m); "
            f"got {g1.shape}"
        )
    if g2.ndim != 2 or g2.shape[0] != n2:
        raise ScopeViolationError(
            f"compose_skew_symmetric: g2 shape must be (n2, m)=({n2}, m); "
            f"got {g2.shape}"
        )
    if g1.shape[1] != g2.shape[1]:
        raise ScopeViolationError(
            f"compose_skew_symmetric: g1, g2 must share port dim m; "
            f"got {g1.shape[1]} vs {g2.shape[1]}"
        )
    return g1, g2


def interface_power(y1: Sequence[float], u1: Sequence[float],
                    y2: Sequence[float], u2: Sequence[float]) -> float:
    """Instantaneous interface power y1·u1 + y2·u2."""
    a = np.asarray(y1, dtype=float).ravel()
    b = np.asarray(u1, dtype=float).ravel()
    c = np.asarray(y2, dtype=float).ravel()
    d = np.asarray(u2, dtype=float).ravel()
    if a.shape != b.shape or c.shape != d.shape:
        raise ScopeViolationError(
            "interface_power: y/u pairs must have matching shapes"
        )
    return float(a @ b + c @ d)


def interface_power_under_feedback(
    y1: Sequence[float], y2: Sequence[float]
) -> float:
    """Power under u1=-y2, u2=y1 (identically zero when dims match)."""
    y1a = np.asarray(y1, dtype=float).ravel()
    y2a = np.asarray(y2, dtype=float).ravel()
    if y1a.shape != y2a.shape:
        raise ScopeViolationError(
            "interface_power_under_feedback: y1 and y2 must match for "
            f"default feedback; got {y1a.shape} vs {y2a.shape}"
        )
    return interface_power(y1a, -y2a, y2a, y1a)


def compose_skew_symmetric(
    J1: np.ndarray,
    J2: np.ndarray,
    interconnection: Union[
        str, Mapping[str, Any], PowerPreservingInterconnection
    ] = FEEDBACK,
    *,
    tol: float = GENERIC_STRUCTURE_TOL,
    power_samples: Optional[Sequence[tuple[Sequence[float], Sequence[float]]]] = None,
) -> DiracCompositionResult:
    """Compose two antisymmetric J matrices under power-preserving feedback.

    Closed-loop structure (ISO-PH feedback ``u1=-y2``, ``u2=y1``)::

        J_total = [[ J1,       -g1 @ g2.T ],
                   [ g2 @ g1.T,  J2       ]]

    Parameters
    ----------
    J1, J2
        Square skew-symmetric structure matrices (pre-checked).
    interconnection
        ``\"feedback\"`` (default), a mapping with optional ``g1``/``g2``,
        or a ``PowerPreservingInterconnection``.
    tol
        Absolute tolerance forwarded to ``check_generic_structure``.
    power_samples
        Optional sequence of ``(y1, y2)`` pairs for interface-power checks.
        If omitted, two default port vectors are used.

    Returns
    -------
    DiracCompositionResult
        With ``ok`` equal to the ``J_antisymmetric`` flag of
        ``check_generic_structure`` on ``J_total`` (M args are zeros and
        are **not** claimed).
    """
    J1a = _as_square(J1, "J1")
    J2a = _as_square(J2, "J2")
    _require_skew(J1a, "J1", tol)
    _require_skew(J2a, "J2", tol)

    ic = _parse_interconnection(interconnection)
    n1, n2 = J1a.shape[0], J2a.shape[0]
    g1, g2 = _resolve_ports(n1, n2, ic)
    ic_resolved = PowerPreservingInterconnection(kind=FEEDBACK, g1=g1, g2=g2)

    # Feedback closed-loop J (Cervera et al. 2007 / ISO-PH interconnection)
    off_12 = -(g1 @ g2.T)
    off_21 = g2 @ g1.T
    # Clear signed-zero artifacts from -0.0 * I blocks for stable JSON/hand checks
    off_12 = np.where(np.abs(off_12) < 1e-15, 0.0, off_12)
    off_21 = np.where(np.abs(off_21) < 1e-15, 0.0, off_21)
    J_total = np.block([[J1a, off_12], [off_21, J2a]])
    J_total = np.where(np.abs(J_total) < 1e-15, 0.0, J_total)

    n = n1 + n2
    M0 = np.zeros((n, n), dtype=float)
    z = np.zeros(n, dtype=float)
    report = check_generic_structure(J_total, M0, z, z, tol=tol)
    # M12 claim surface: antisymmetry only
    ok = bool(report["J_antisymmetric"])

    if power_samples is None:
        m = g1.shape[1]
        # ≥2 port vectors (as y1, y2) for the interface power check
        power_samples = [
            (np.ones(m), np.arange(1, m + 1, dtype=float)),
            (np.arange(m, dtype=float) + 0.5, (-1.0) ** np.arange(m)),
        ]

    powers = [
        abs(interface_power_under_feedback(y1, y2))
        for y1, y2 in power_samples
    ]
    if len(powers) < 2:
        raise ScopeViolationError(
            "compose_skew_symmetric: need ≥2 power_samples "
            f"(got {len(powers)})"
        )
    power_max = float(max(powers))

    return DiracCompositionResult(
        J_total=J_total,
        interconnection=ic_resolved,
        antisymmetry_report=report,
        ok=ok,
        interface_power_max_abs=power_max,
        assumptions=_DEFAULT_ASSUMPTIONS,
    )


__all__ = [
    "FEEDBACK",
    "SOURCE",
    "PowerPreservingInterconnection",
    "DiracCompositionResult",
    "compose_skew_symmetric",
    "interface_power",
    "interface_power_under_feedback",
]
