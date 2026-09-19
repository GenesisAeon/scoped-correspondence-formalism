"""Lie-Poisson / Casimir invariants (Milestone 26).

Finite-dimensional so(3)* rigid-body Lie-Poisson + quadratic Casimir.
Arnold 1966 DOI 10.5802/aif.233; Marsden & Ratiu 1999 DOI 10.1007/978-0-387-21792-5.

Implements casimir_residual(J, grad_C) and hat_map(z). Calls check_generic_structure
(does not reimplement or edit coupling/core.py).

Finite-dimensional only. NOT a fluid PDE / continuum Lie-Poisson implementation
(no Euler on Diff(mu), no Vlasov, no ideal MHD). Does NOT claim coupling IS fluid
dynamics. Does NOT ship a general Casimir-finder.
"""

from __future__ import annotations

from typing import Mapping, Sequence, Tuple, Union

import numpy as np

from scoped_correspondence.errors import ScopeViolationError

ArrayLike = Union[Sequence[float], np.ndarray]

CASIMIR_RESIDUAL_TOL: float = 1e-10

SOURCE = (
    "Arnold 1966 DOI 10.5802/aif.233; "
    "Marsden & Ratiu 1999 DOI 10.1007/978-0-387-21792-5 "
    "(finite-dim so(3)* only; NOT fluid PDE)"
)

ARNOLD_DOI = "10.5802/aif.233"
MARSDEN_RATIU_DOI = "10.1007/978-0-387-21792-5"

_DEFAULT_ASSUMPTIONS: Tuple[str, ...] = (
    "finite-dimensional Lie-Poisson on so(3)* via hat_map; NOT fluid PDE",
    "Casimir residual is pointwise ker(J) check only — not a general Casimir finder",
    "does NOT claim coupling IS fluid dynamics",
    "compatibility with GENERIC via CALL to check_generic_structure (core unchanged)",
)


def hat_map(z: ArrayLike) -> np.ndarray:
    """so(3) hat map: z |-> hat(z) with hat(z) v = z x v. J(z)=hat_map(z) on so(3)*."""
    z = np.asarray(z, dtype=float).ravel()
    if z.shape != (3,):
        raise ScopeViolationError(
            f"hat_map: expected length-3 vector; got shape {z.shape}"
        )
    z1, z2, z3 = float(z[0]), float(z[1]), float(z[2])
    return np.array(
        [[0.0, -z3, z2], [z3, 0.0, -z1], [-z2, z1, 0.0]],
        dtype=float,
    )


def casimir_residual(J: ArrayLike, grad_C: ArrayLike) -> dict:
    """Return J@grad_C, Euclidean norm, and max_abs (matches max_abs_J_grad_S)."""
    J = np.asarray(J, dtype=float)
    gC = np.asarray(grad_C, dtype=float).ravel()
    if J.ndim != 2 or J.shape[0] != J.shape[1]:
        raise ScopeViolationError(
            f"casimir_residual: J must be square; got shape {J.shape}"
        )
    n = J.shape[0]
    if gC.shape != (n,):
        raise ScopeViolationError(
            f"casimir_residual: grad_C length must match n={n}; got {gC.shape}"
        )
    resid = J @ gC
    max_abs = float(np.max(np.abs(resid))) if n else 0.0
    norm = float(np.linalg.norm(resid))
    return {
        "J_grad_C": resid,
        "norm": norm,
        "max_abs": max_abs,
        "ok": max_abs <= CASIMIR_RESIDUAL_TOL,
        "tol": CASIMIR_RESIDUAL_TOL,
    }


def rigid_body_hamiltonian_grad(z: ArrayLike, inertia: ArrayLike) -> np.ndarray:
    """grad H for H = (1/2) sum z_i^2 / I_i; returns Omega = z/I."""
    z = np.asarray(z, dtype=float).ravel()
    I = np.asarray(inertia, dtype=float).ravel()
    if z.shape != (3,) or I.shape != (3,):
        raise ScopeViolationError(
            "rigid_body_hamiltonian_grad: z and inertia must be length-3"
        )
    if np.any(I == 0.0):
        raise ScopeViolationError(
            "rigid_body_hamiltonian_grad: inertia components must be nonzero"
        )
    return z / I


def lie_poisson_vector_field(z: ArrayLike, inertia: ArrayLike) -> np.ndarray:
    """z_dot = hat(z) grad H for so(3)* rigid body."""
    z = np.asarray(z, dtype=float).ravel()
    return hat_map(z) @ rigid_body_hamiltonian_grad(z, inertia)


def time_derivative_along_field(grad_F: ArrayLike, z_dot: ArrayLike) -> float:
    """dF/dt = grad F · z_dot."""
    g = np.asarray(grad_F, dtype=float).ravel()
    zd = np.asarray(z_dot, dtype=float).ravel()
    if g.shape != zd.shape:
        raise ScopeViolationError(
            "time_derivative_along_field: grad_F and z_dot shape mismatch"
        )
    return float(np.dot(g, zd))


def quadratic_casimir_grad(z: ArrayLike) -> np.ndarray:
    """grad C for C = |z|^2 / 2; equals z."""
    z = np.asarray(z, dtype=float).ravel()
    if z.shape != (3,):
        raise ScopeViolationError(
            f"quadratic_casimir_grad: expected length-3; got {z.shape}"
        )
    return z.copy()


def compare_to_generic_J_grad_S(
    J: ArrayLike,
    grad_C: ArrayLike,
    *,
    M: ArrayLike | None = None,
    grad_E: ArrayLike | None = None,
    tol: float | None = None,
) -> Mapping[str, object]:
    """CALL check_generic_structure; compare casimir max_abs to max_abs_J_grad_S."""
    from scoped_correspondence.coupling.core import (  # noqa: WPS433
        GENERIC_STRUCTURE_TOL,
        check_generic_structure,
    )

    J_arr = np.asarray(J, dtype=float)
    gC = np.asarray(grad_C, dtype=float).ravel()
    n = J_arr.shape[0]
    if M is None:
        M = np.zeros((n, n), dtype=float)
    if grad_E is None:
        grad_E = np.zeros(n, dtype=float)
    kw = {"tol": float(tol) if tol is not None else GENERIC_STRUCTURE_TOL}
    report = check_generic_structure(J_arr, M, grad_E, gC, **kw)
    cas = casimir_residual(J_arr, gC)
    generic_max = float(report["residuals"]["max_abs_J_grad_S"])
    return {
        "casimir": cas,
        "generic_report": report,
        "max_abs_match": bool(cas["max_abs"] == generic_max),
        "casimir_max_abs": cas["max_abs"],
        "generic_max_abs_J_grad_S": generic_max,
        "source": SOURCE,
        "assumptions": _DEFAULT_ASSUMPTIONS,
    }


__all__ = [
    "ARNOLD_DOI",
    "CASIMIR_RESIDUAL_TOL",
    "MARSDEN_RATIU_DOI",
    "SOURCE",
    "casimir_residual",
    "compare_to_generic_J_grad_S",
    "hat_map",
    "lie_poisson_vector_field",
    "quadratic_casimir_grad",
    "rigid_body_hamiltonian_grad",
    "time_derivative_along_field",
]
