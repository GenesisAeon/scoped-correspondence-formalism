"""Lie–Poisson / Casimir invariants (Milestone 26).

Finite-dimensional so(3)* rigid-body example of a Lie–Poisson structure and
its quadratic Casimir. Maps Arnold (1966) and Marsden & Ratiu (1999) for the
finite-dimensional setting only.

This module implements:
  - ``casimir_residual(J, grad_C)`` — evaluate ``J @ grad_C`` and its norms
  - ``hat_map(z)`` — the so(3) hat isomorphism R^3 → so(3) used as the
    Lie–Poisson tensor ``J(z) = hat(z)`` on so(3)*

Compatibility with GENERIC (Milestone coupling core): for a GENERIC structure
check, the Casimir residual's ``max_abs`` matches
``check_generic_structure(...).residuals["max_abs_J_grad_S"]`` when
``grad_C == grad_S``. This module **calls** ``check_generic_structure``; it
does **not** reimplement or edit ``coupling/core.py``.

Scope / disclaimers
-------------------
- **Finite-dimensional only.** This is **NOT** a fluid PDE / continuum
  Lie–Poisson implementation (no Euler equations on Diff(μ), no Vlasov,
  no ideal MHD bracket).
- Does **NOT** claim that the coupling layer **is** fluid dynamics.
- Does **NOT** ship a general Casimir-finder (no algorithm that searches
  for Casimirs of arbitrary Poisson tensors).
- Passing residual ≈ 0 certifies only that ``grad_C`` lies in ker(J) at the
  evaluated point; it does not certify a global Casimir for an unstated
  Poisson structure.

Sources
-------
- Arnold, V. (1966). Sur la géométrie différentielle des groupes de Lie de
  dimension infinie et ses applications à l'hydrodynamique des fluides
  parfaits. Ann. Inst. Fourier 16(1):319–361. DOI 10.5802/aif.233
  (finite-dim so(3) rigid-body reduction used here; **not** the fluid PDE).
- Marsden, J. E. & Ratiu, T. S. (1999). Introduction to Mechanics and
  Symmetry, 2nd ed. Springer. DOI 10.1007/978-0-387-21792-5
  (Lie–Poisson brackets, Casimirs; so(3)* rigid body).
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
    "finite-dimensional Lie–Poisson on so(3)* via hat_map; NOT fluid PDE",
    "Casimir residual is pointwise ker(J) check only — not a general Casimir finder",
    "does NOT claim coupling IS fluid dynamics",
    "compatibility with GENERIC via CALL to check_generic_structure (core unchanged)",
)


def hat_map(z: ArrayLike) -> np.ndarray:
    """so(3) hat isomorphism: z ↦ẑ ∈ so(3), with ẑ v = z × v.

    For the rigid-body Lie–Poisson structure on so(3)* ≅ R^3 the Poisson
    tensor at momentum ``z`` is ``J(z) = hat_map(z)`` (skew-symmetric), so

        ż = J(z) ∇H = z × ∇H.

    Parameters
    ----------
    z :
        Length-3 vector.

    Returns
    -------
    ndarray, shape (3, 3)
        Skew-symmetric matrix for ``z = (z1, z2, z3)``::

            [[  0, -z3,  z2 ],
             [ z3,   0, -z1 ],
             [-z2,  z1,   0 ]]
    """
    z = np.asarray(z, dtype=float).ravel()
    if z.shape != (3,):
        raise ScopeViolationError(
            f"hat_map: expected length-3 vector; got shape {z.shape}"
        )
    z1, z2, z3 = float(z[0]), float(z[1]), float(z[2])
    return np.array(
        [
            [0.0, -z3, z2],
            [z3, 0.0, -z1],
            [-z2, z1, 0.0],
        ],
        dtype=float,
    )


def casimir_residual(
    J: ArrayLike,
    grad_C: ArrayLike,
) -> dict:
    """Evaluate the Casimir residual ``J @ grad_C`` and its norms.

    For a Casimir function ``C`` of a Poisson tensor ``J``, one has
    ``J ∇C = 0`` identically (on the domain). This helper returns the
    pointwise residual vector and norms; it does **not** search for
    Casimirs.

    Returns
    -------
    dict
        ``J_grad_C`` : ndarray — ``J @ grad_C``
        ``norm`` : float — Euclidean ``||J @ grad_C||_2``
        ``max_abs`` : float — ``max | (J @ grad_C)_i |``
          (matches ``check_generic_structure`` residual key
          ``max_abs_J_grad_S`` when ``grad_C == grad_S``)
        ``ok`` : bool — ``max_abs <= CASIMIR_RESIDUAL_TOL``
        ``tol`` : float
    """
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
    """∇H for rigid-body energy H = (1/2) Σ z_i² / I_i  (principal axes).

    With ``Ω_i = z_i / I_i`` one has ``∇_z H = Ω``, so
    ``ż = hat(z) Ω = z × Ω``.
    """
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


def lie_poisson_vector_field(
    z: ArrayLike,
    inertia: ArrayLike,
) -> np.ndarray:
    """ż = hat(z) ∇H for the so(3)* rigid body with principal inertia ``I``."""
    z = np.asarray(z, dtype=float).ravel()
    J = hat_map(z)
    gH = rigid_body_hamiltonian_grad(z, inertia)
    return J @ gH


def time_derivative_along_field(
    grad_F: ArrayLike,
    z_dot: ArrayLike,
) -> float:
    """dF/dt = ∇F · ż along a vector field."""
    g = np.asarray(grad_F, dtype=float).ravel()
    zd = np.asarray(z_dot, dtype=float).ravel()
    if g.shape != zd.shape:
        raise ScopeViolationError(
            "time_derivative_along_field: grad_F and z_dot shape mismatch"
        )
    return float(np.dot(g, zd))


def quadratic_casimir_grad(z: ArrayLike) -> np.ndarray:
    """∇C for C = |z|² / 2  (so(3)* Casimir). Equals ``z`` itself."""
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
    """Call ``check_generic_structure`` and compare Casimir residual to
    ``residuals['max_abs_J_grad_S']``.

    Does **not** reimplement the GENERIC check — imports and calls
    ``scoped_correspondence.coupling.core.check_generic_structure``.
    """
    # Local import keeps casimir importable even if core is mid-refactor;
    # M26 forbids editing core.py and forbids reimplementing this check.
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
    kw = {}
    if tol is not None:
        kw["tol"] = float(tol)
    else:
        kw["tol"] = GENERIC_STRUCTURE_TOL

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
