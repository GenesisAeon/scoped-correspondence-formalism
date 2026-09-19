"""Nagumo tangent-cone condition for polyhedra (Milestone 28).

Maps Mitio Nagumo 1942 (DOI 10.11429/ppmsj1919.24.0_551; English
translation Menner & Lavretsky arXiv:2406.18614): a closed set K is
forward invariant for the ODE ż = f(z) iff f(z) lies in the Bouligand
tangent cone T_K(z) at every boundary point z ∈ ∂K.

For a polyhedron K = {z : A z ≤ b} the tangent cone at z reduces to
the half-space constraints on the *active* rows:

    T_K(z) = { v : A[i] · v ≤ 0  for every i with A[i] · z = b[i] }.

Hence the Nagumo condition is exactly A[i] · f(z) ≤ 0 for every active i.
This covers **non-smooth** polyhedra / boxes, where no single smooth
barrier h exists at a corner — a different case class from M16's scalar
zeroing CBF (`control_barrier.py`), not a replacement for it.

Does **not** implement a viability-kernel solver (Saint-Pierre), curved
boundaries, or any edit of ``viability/core.py`` / ``control_barrier.py``.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Mapping, Sequence, Tuple, Union

import numpy as np

from scoped_correspondence.errors import ScopeViolationError

ArrayLike = Union[np.ndarray, Sequence[Sequence[float]], Sequence[float]]

SOURCE = (
    "Nagumo 1942, Über die Lage der Integralkurven gewöhnlicher "
    "Differentialgleichungen, Proc. Physico-Mathematical Society of Japan "
    "24:551–559; DOI 10.11429/ppmsj1919.24.0_551 "
    "(translation: Menner & Lavretsky arXiv:2406.18614)"
)

_DEFAULT_ASSUMPTIONS: Tuple[str, ...] = (
    "polyhedral constraint set K = {z : A z <= b} only — curved / nonlinear "
    "boundaries out of scope",
    "Nagumo / Bouligand tangent-cone condition: A[i]·f(z) <= 0 for every "
    "active constraint i at boundary point z (Nagumo 1942)",
    "covers non-smooth polyhedra (corners / edges) where no single smooth "
    "barrier h exists — different case class from M16 CBF, not a replacement",
    "caller supplies boundary samples; no viability-kernel / Saint-Pierre "
    "solver (viability/core.py docstring already excludes that)",
    "does not mutate viability/core.py or control_barrier.py",
)


def _as_1d(z: ArrayLike, name: str = "z") -> np.ndarray:
    arr = np.asarray(z, dtype=float).reshape(-1)
    if arr.ndim != 1 or arr.size == 0:
        raise ScopeViolationError(f"{name} must be a nonempty 1-D vector; got shape {np.asarray(z).shape}")
    if not np.all(np.isfinite(arr)):
        raise ScopeViolationError(f"{name} must be finite; got {arr!r}")
    return arr


def _as_Ab(A: ArrayLike, b: ArrayLike) -> Tuple[np.ndarray, np.ndarray]:
    A_a = np.asarray(A, dtype=float)
    b_a = np.asarray(b, dtype=float).reshape(-1)
    if A_a.ndim != 2:
        raise ScopeViolationError(f"A must be 2-D (m×n); got shape {A_a.shape}")
    if A_a.shape[0] != b_a.shape[0]:
        raise ScopeViolationError(
            f"A rows ({A_a.shape[0]}) must match b length ({b_a.shape[0]})"
        )
    if A_a.size == 0:
        raise ScopeViolationError("A must be nonempty")
    if not np.all(np.isfinite(A_a)) or not np.all(np.isfinite(b_a)):
        raise ScopeViolationError("A and b must be finite")
    return A_a, b_a


def active_constraints(
    z: ArrayLike,
    A: ArrayLike,
    b: ArrayLike,
    tol: float = 1e-9,
) -> List[int]:
    """Indices of active polyhedral constraints at ``z``.

    For K = {x : A x ≤ b}, constraint ``i`` is active when
    ``|A[i]·z - b[i]| ≤ tol`` (equivalently A[i]·z ≈ b[i] within ``tol``).

    Returns a list of row indices (ints), sorted ascending.
    """
    if tol < 0:
        raise ScopeViolationError(f"tol must be >= 0; got {tol!r}")
    z_a = _as_1d(z, "z")
    A_a, b_a = _as_Ab(A, b)
    if z_a.shape[0] != A_a.shape[1]:
        raise ScopeViolationError(
            f"z dim ({z_a.shape[0]}) must match A columns ({A_a.shape[1]})"
        )
    residuals = A_a @ z_a - b_a
    active = [int(i) for i in range(A_a.shape[0]) if abs(float(residuals[i])) <= float(tol)]
    return active


def tangent_cone_condition(
    z: ArrayLike,
    f_z: ArrayLike,
    A: ArrayLike,
    b: ArrayLike,
    tol: float = 1e-9,
) -> Dict[str, Any]:
    """Nagumo tangent-cone condition at one point ``z``.

    For every active constraint ``i`` (A[i]·z ≈ b[i]), require
    ``A[i] · f_z ≤ tol``. Returns

    - ``ok``: True iff every active residual A[i]·f_z ≤ tol
    - ``margins``: list of A[i]·f_z for each active i (≤ 0 means inward /
      tangent; > 0 means outward violation)
    - ``active_indices``: the active row indices
    - ``source``, ``assumptions``: provenance

    Interior points (no active constraints) vacuously satisfy Nagumo
    (``ok=True``, empty margins).
    """
    if tol < 0:
        raise ScopeViolationError(f"tol must be >= 0; got {tol!r}")
    z_a = _as_1d(z, "z")
    f_a = _as_1d(f_z, "f_z")
    A_a, b_a = _as_Ab(A, b)
    if z_a.shape[0] != A_a.shape[1]:
        raise ScopeViolationError(
            f"z dim ({z_a.shape[0]}) must match A columns ({A_a.shape[1]})"
        )
    if f_a.shape[0] != A_a.shape[1]:
        raise ScopeViolationError(
            f"f_z dim ({f_a.shape[0]}) must match A columns ({A_a.shape[1]})"
        )

    idxs = active_constraints(z_a, A_a, b_a, tol=tol)
    margins: List[float] = []
    for i in idxs:
        margins.append(float(A_a[i] @ f_a))
    ok = all(m <= float(tol) for m in margins)
    return {
        "ok": bool(ok),
        "margins": margins,
        "active_indices": list(idxs),
        "z": z_a.tolist(),
        "f_z": f_a.tolist(),
        "source": SOURCE,
        "assumptions": list(_DEFAULT_ASSUMPTIONS),
    }


def verify_polyhedral_viability(
    A: ArrayLike,
    b: ArrayLike,
    f: Callable[[Sequence[float]], ArrayLike],
    boundary_samples: Sequence[ArrayLike],
    tol: float = 1e-9,
) -> Dict[str, Any]:
    """Check Nagumo on a caller-provided list of boundary samples.

    Does **not** sample the boundary or solve a viability kernel — the
    caller supplies ``boundary_samples``. At each sample ``z``, evaluates
    ``f(z)`` and ``tangent_cone_condition(z, f(z), A, b, tol)``.

    Returns aggregate ``ok`` (True iff every sample passes) plus per-point
    details.
    """
    if not callable(f):
        raise ScopeViolationError("f must be callable: f(z) -> f_z")
    A_a, b_a = _as_Ab(A, b)
    if len(boundary_samples) == 0:
        raise ScopeViolationError(
            "boundary_samples must be a nonempty sequence (caller provides "
            "samples; no kernel solver / auto-sampler)"
        )

    results: List[Dict[str, Any]] = []
    n_failed = 0
    for raw in boundary_samples:
        z_a = _as_1d(raw, "boundary sample")
        if z_a.shape[0] != A_a.shape[1]:
            raise ScopeViolationError(
                f"sample dim ({z_a.shape[0]}) must match A columns ({A_a.shape[1]})"
            )
        try:
            f_raw = f(z_a.tolist())
        except Exception as exc:  # noqa: BLE001 — surface as scope violation
            raise ScopeViolationError(
                f"f(z) raised {type(exc).__name__}: {exc}"
            ) from exc
        detail = tangent_cone_condition(z_a, f_raw, A_a, b_a, tol=tol)
        if not detail["ok"]:
            n_failed += 1
        results.append(detail)

    return {
        "ok": bool(n_failed == 0),
        "n_samples": len(results),
        "n_failed": int(n_failed),
        "n_passed": int(len(results) - n_failed),
        "tol": float(tol),
        "results": results,
        "source": SOURCE,
        "assumptions": list(_DEFAULT_ASSUMPTIONS),
        "note": (
            "Sample-based Nagumo check on a polyhedron; not a viability-kernel "
            "solver. Covers non-smooth polyhedra — different case class from "
            "M16 CBF, not a replacement."
        ),
    }


__all__ = [
    "SOURCE",
    "active_constraints",
    "tangent_cone_condition",
    "verify_polyhedral_viability",
]
