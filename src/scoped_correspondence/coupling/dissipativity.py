"""Dissipativity / supply rates (Milestone 15).

Maps Willems 1972 (DOI 10.1007/BF00276493): a dynamical system is
dissipative with respect to a supply rate ``w(u, y)`` if there exists a
storage function ``V`` satisfying the differential dissipation inequality

    V̇(x) ≤ w(u, y)

(checked numerically as ``V_dot <= w + tol``). Under the standard neutral
(power-preserving) interconnection of two ports

    u1 = -y2,  u2 = y1

the total supply ``y1·u1 + y2·u2`` vanishes identically, so the sum of
storage rates is non-increasing whenever each subsystem is dissipative
w.r.t. its port supply ``y·u``.

This module implements **only** the storage-inequality check and the
neutral-interconnection supply identity. It does **not** reinterpret
storage as thermodynamic energy/entropy, assert GENERIC structure, or
provide a network-theory / bond-graph library.

Disclaimer
----------
``DissipativityCertificate`` is a **general energy-balance / supply-rate
contract**. It is **NOT** a thermodynamic claim without further proof.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Sequence, Union

import numpy as np

from scoped_correspondence.errors import ScopeViolationError

ArrayLike = Union[float, Sequence[float], np.ndarray]

STORAGE_INEQUALITY_TOL: float = 1e-10

SOURCE = "Willems 1972, DOI 10.1007/BF00276493"

_DEFAULT_ASSUMPTIONS: tuple[str, ...] = (
    "differential storage inequality V_dot <= w + tol (Willems 1972)",
    "neutral interconnection supply y1·u1 + y2·u2 under u1=-y2, u2=y1",
    "general energy-balance / supply-rate contract only — NOT a "
    "thermodynamic claim without further proof",
    "no GENERIC / entropy-production / heat reinterpretation; "
    "no network-theory / bond-graph library",
)

_THERMO_DISCLAIMER = (
    "DissipativityCertificate is a general energy-balance / supply-rate "
    "contract (Willems 1972). It is NOT a thermodynamic claim without "
    "further proof: ok=True does not assert GENERIC structure, entropy "
    "production, heat balance, or any thermo reinterpretation of V."
)


@dataclass(frozen=True)
class DissipativityCertificate:
    """Pointwise dissipativity certificate for a storage inequality.

    Certifies ``V_dot <= supply + tol`` at the evaluated sample(s).

    This is a **general energy-balance / supply-rate contract** in the
    sense of Willems (1972). It is **NOT** a thermodynamic claim without
    further proof: ``ok=True`` does not assert GENERIC structure, entropy
    production, heat balance, or any thermo reinterpretation of the
    storage function ``V``.
    """

    V_dot: float
    supply: float
    tol: float
    ok: bool  # V_dot <= supply + tol
    assumptions: tuple[str, ...]
    source: str = SOURCE
    disclaimer: str = _THERMO_DISCLAIMER


def check_storage_inequality(
    V_dot: ArrayLike,
    w: ArrayLike,
    tol: float = STORAGE_INEQUALITY_TOL,
) -> bool:
    """Return True iff ``V_dot <= w + tol`` (elementwise if array-valued).

    Parameters
    ----------
    V_dot
        Storage-function time derivative(s).
    w
        Supply rate(s) ``w(u, y)``.
    tol
        Absolute numerical tolerance (default ``STORAGE_INEQUALITY_TOL``).

    Returns
    -------
    bool
        ``True`` when the differential dissipation inequality holds within
        ``tol`` at every sample.
    """
    if float(tol) < 0.0:
        raise ScopeViolationError(
            f"check_storage_inequality: tol must be >= 0; got {tol!r}"
        )
    vd = np.asarray(V_dot, dtype=float)
    ww = np.asarray(w, dtype=float)
    try:
        vd, ww = np.broadcast_arrays(vd, ww)
    except ValueError as exc:
        raise ScopeViolationError(
            f"check_storage_inequality: V_dot shape {vd.shape} incompatible "
            f"with w shape {ww.shape}"
        ) from exc
    return bool(np.all(vd <= ww + float(tol)))


def neutral_interconnection_supply(
    y1: ArrayLike,
    u1: ArrayLike,
    y2: ArrayLike,
    u2: ArrayLike,
) -> float:
    """Total supply ``y1·u1 + y2·u2`` of a two-port interconnection.

    Under the neutral (power-preserving) feedback ``u1 = -y2``,
    ``u2 = y1`` this quantity is identically zero when dimensions match.
    """
    a = np.asarray(y1, dtype=float).ravel()
    b = np.asarray(u1, dtype=float).ravel()
    c = np.asarray(y2, dtype=float).ravel()
    d = np.asarray(u2, dtype=float).ravel()
    if a.shape != b.shape:
        raise ScopeViolationError(
            f"neutral_interconnection_supply: y1/u1 shapes {a.shape}/{b.shape}"
        )
    if c.shape != d.shape:
        raise ScopeViolationError(
            f"neutral_interconnection_supply: y2/u2 shapes {c.shape}/{d.shape}"
        )
    return float(a @ b + c @ d)


def make_dissipativity_certificate(
    V_dot: ArrayLike,
    w: ArrayLike,
    tol: float = STORAGE_INEQUALITY_TOL,
    *,
    assumptions: Optional[tuple[str, ...]] = None,
) -> DissipativityCertificate:
    """Build a ``DissipativityCertificate`` from a storage / supply sample.

    Scalarizes array inputs by taking the max of ``V_dot - w`` (worst-case
    residual) so ``ok`` matches ``check_storage_inequality``.
    """
    vd = np.asarray(V_dot, dtype=float)
    ww = np.asarray(w, dtype=float)
    try:
        vd, ww = np.broadcast_arrays(vd, ww)
    except ValueError as exc:
        raise ScopeViolationError(
            "make_dissipativity_certificate: incompatible V_dot / w shapes"
        ) from exc
    residual = vd - ww
    flat_res = residual.ravel()
    idx = int(np.argmax(flat_res))
    vd_s = float(vd.ravel()[idx])
    w_s = float(ww.ravel()[idx])
    ok = check_storage_inequality(vd, ww, tol=tol)
    assum = assumptions if assumptions is not None else _DEFAULT_ASSUMPTIONS
    return DissipativityCertificate(
        V_dot=vd_s,
        supply=w_s,
        tol=float(tol),
        ok=ok,
        assumptions=tuple(assum),
    )


__all__ = [
    "STORAGE_INEQUALITY_TOL",
    "SOURCE",
    "DissipativityCertificate",
    "check_storage_inequality",
    "neutral_interconnection_supply",
    "make_dissipativity_certificate",
]
