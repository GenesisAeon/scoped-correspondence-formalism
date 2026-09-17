"""Thermodynamic / GENERIC helpers (Milestone 8).

Ports e10 / e13 from verification/verify_extensions.py and adds an explicit
congruence projection helper for GENERIC structure (coupling_layer_afet.md §8–§9).

This module CALLS ``check_generic_structure``; it does not mutate coupling/core.py.
No ODE integration; no Mori–Zwanzig rewrite.
"""
from __future__ import annotations

from typing import Sequence

import numpy as np

from scoped_correspondence.coupling import check_generic_structure
from scoped_correspondence.errors import ScopeViolationError

ArrayLike = Sequence[float] | np.ndarray


def _near(actual, expected, atol=1e-10, rtol=1e-9) -> None:
    if not np.allclose(actual, expected, atol=atol, rtol=rtol):
        raise AssertionError(f"{actual!r} != {expected!r}")


def _require(condition, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def heat_generic_example(
    ca: float,
    cb: float,
    conductance: float,
    ta: float,
    tb: float,
) -> dict:
    """Two-reservoir heat exchange as a GENERIC structure (e13 port).

    Ports ``e13_generic_heat_structure`` from ``verification/verify_extensions.py``
    for a single parameter combination, then calls ``check_generic_structure``.

    Mapping (coupling_layer_afet.md §8 / §3.2):
      - Energies: E = (C_A T_A, C_B T_B); E(z) = z_A + z_B so grad_E = [1, 1]
      - Entropy gradient: grad_S = (1/T_A, 1/T_B) (analytic + finite-difference)
      - M = G·T_A·T_B · [[1,-1],[-1,1]]; J = 0
      - Heat current J_heat = G (T_A - T_B); entropy production G (T_A-T_B)^2/(T_A T_B)

    Returns a dict with energies, gradients, M, flow, production, and the
    ``check_generic_structure`` report (grad_E=[1,1], J=zeros(2,2)).
    """
    ca = float(ca)
    cb = float(cb)
    conductance = float(conductance)
    ta = float(ta)
    tb = float(tb)
    if min(ca, cb, conductance, ta, tb) <= 0:
        raise ScopeViolationError(
            "heat_generic_example: ca, cb, conductance, ta, tb must be positive"
        )

    energy = np.array([ca * ta, cb * tb], dtype=float)

    def entropy_fn(e: np.ndarray) -> float:
        return float(
            ca * np.log((e[0] / ca) / 300.0) + cb * np.log((e[1] / cb) / 300.0)
        )

    gradient = np.array([1.0 / ta, 1.0 / tb], dtype=float)
    numeric = []
    for axis in range(2):
        v = np.zeros(2)
        v[axis] = 1e-3
        numeric.append((entropy_fn(energy + v) - entropy_fn(energy - v)) / (2e-3))
    _near(gradient, numeric, atol=1e-10)

    m = conductance * ta * tb * np.array([[1.0, -1.0], [-1.0, 1.0]], dtype=float)
    _near(m, m.T)
    _require(np.linalg.eigvalsh(m).min() >= -1e-10, "M not PSD")
    _near(m @ np.ones(2), 0)

    flow = m @ gradient
    heat_current = conductance * (ta - tb)
    _near(flow, [-heat_current, heat_current])
    production = float(gradient @ m @ gradient)
    _near(production, conductance * (ta - tb) ** 2 / (ta * tb))
    _require(production >= -1e-12, "negative entropy production")
    _near(flow.sum(), 0)

    j = np.zeros((2, 2), dtype=float)
    grad_e = np.array([1.0, 1.0], dtype=float)
    structure = check_generic_structure(j, m, grad_e, gradient)

    return {
        "ca": ca,
        "cb": cb,
        "conductance": conductance,
        "ta": ta,
        "tb": tb,
        "energy": energy.tolist(),
        "grad_S": gradient.tolist(),
        "grad_S_numeric": [float(x) for x in numeric],
        "grad_E": grad_e.tolist(),
        "J": j.tolist(),
        "M": m.tolist(),
        "flow": flow.tolist(),
        "heat_current": float(heat_current),
        "entropy_production": production,
        "M_ones_zero": True,
        "poisson_operator": "identically zero; Jacobi identity trivial",
        "generic_structure": structure,
    }


def stochastic_inverse_not_detailed_balance() -> dict:
    """3-cycle: stochastic inverse exists but detailed balance fails (e10 port).

    Ports ``e10_inverse_is_not_detailed_balance`` from
    ``verification/verify_extensions.py`` 1:1.

    Reference: coupling_layer_afet.md §9 — stochastic invertibility, stationary
    detailed balance, and thermodynamic reversibility are not synonyms. The
    3-cycle permutation makes that separation explicit.
    """
    p = np.eye(3)[[1, 2, 0]]
    inverse = np.linalg.inv(p)
    # stochastic() checks from e10
    inv = np.asarray(inverse, dtype=float)
    _require(inv.ndim == 2 and np.isfinite(inv).all(), "finite matrix required")
    _require((inv >= 0).all(), "negative transition probability")
    _near(inv.sum(axis=1), np.ones(len(inv)))
    _near(p @ inv, np.eye(3))
    mu = np.full(3, 1.0 / 3.0)
    _near(mu @ p, mu)
    flow = mu[:, None] * p
    _require(not np.allclose(flow, flow.T), "cycle incorrectly passed detailed balance")
    _near(flow[0, 1], 1.0 / 3.0)
    _near(flow[1, 0], 0.0)
    return {
        "P": p.tolist(),
        "P_inverse": inv.tolist(),
        "stochastic_inverse": True,
        "detailed_balance": False,
        "stationary": mu.tolist(),
        "forward_flow": float(flow[0, 1]),
        "reverse_flow": float(flow[1, 0]),
        "mapping": "coupling_layer_afet.md §9 / e10_inverse_is_not_detailed_balance",
    }


def project_generic_structure(
    J: ArrayLike,
    M: ArrayLike,
    Pi: ArrayLike,
    grad_E_prime: ArrayLike,
    grad_S_prime: ArrayLike,
    *,
    tol: float | None = None,
) -> dict:
    """Congruence-project GENERIC operators and re-check algebraic structure.

    Computes
      J' = Pi @ J @ Pi.T
      M' = Pi @ M @ Pi.T
    then calls ``check_generic_structure(J', M', grad_E_prime, grad_S_prime)``.

    ``grad_E_prime`` and ``grad_S_prime`` are **explicit caller-supplied**
    gradients in the projected coordinates. There is **no** silent default
    such as ``Pi @ grad_E`` / ``Pi @ grad_S`` — the caller must pass the primes
    for the reduced system (ticket M8 / coupling_layer_afet.md §9).

    **Disclaimer (must-read):** this only checks algebraic GENERIC structure
    under congruence. It does **not** claim that ``(grad_E_prime, grad_S_prime)``
    are valid reduced energy/entropy potentials (§9). Scale change /
    projection can wipe dissipation, create memory, or leave a Markov
    description that is not a valid reduced GENERIC system even when the
    algebraic flags pass.

    Returns J', M', the structure report, and a fixed disclaimer string.
    """
    J_arr = np.asarray(J, dtype=float)
    M_arr = np.asarray(M, dtype=float)
    Pi_arr = np.asarray(Pi, dtype=float)
    gEp = np.asarray(grad_E_prime, dtype=float).ravel()
    gSp = np.asarray(grad_S_prime, dtype=float).ravel()

    if J_arr.ndim != 2 or M_arr.ndim != 2 or J_arr.shape != M_arr.shape:
        raise ScopeViolationError(
            f"project_generic_structure: J and M must be square same shape; "
            f"got J={J_arr.shape}, M={M_arr.shape}"
        )
    n = J_arr.shape[0]
    if J_arr.shape[0] != J_arr.shape[1]:
        raise ScopeViolationError("project_generic_structure: J must be square")
    if Pi_arr.ndim != 2 or Pi_arr.shape[1] != n:
        raise ScopeViolationError(
            f"project_generic_structure: Pi must be (k,{n}); got {Pi_arr.shape}"
        )
    k = Pi_arr.shape[0]
    if gEp.shape != (k,) or gSp.shape != (k,):
        raise ScopeViolationError(
            f"project_generic_structure: grad_E_prime/grad_S_prime length must "
            f"match k={k}; got {gEp.shape}, {gSp.shape}"
        )

    Jp = Pi_arr @ J_arr @ Pi_arr.T
    Mp = Pi_arr @ M_arr @ Pi_arr.T

    kwargs = {}
    if tol is not None:
        kwargs["tol"] = float(tol)
    structure = check_generic_structure(Jp, Mp, gEp, gSp, **kwargs)

    disclaimer = (
        "Only checks algebraic structure under congruence; does NOT claim "
        "(grad_E', grad_S') are valid reduced energy/entropy potentials "
        "(coupling_layer_afet.md §9)."
    )
    return {
        "J_prime": Jp.tolist(),
        "M_prime": Mp.tolist(),
        "grad_E_prime": gEp.tolist(),
        "grad_S_prime": gSp.tolist(),
        "Pi": Pi_arr.tolist(),
        "generic_structure": structure,
        "disclaimer": disclaimer,
        "note": (
            "grad_E_prime / grad_S_prime are caller-supplied for projected "
            "coords; no silent Pi@grad default."
        ),
    }


__all__ = [
    "heat_generic_example",
    "project_generic_structure",
    "stochastic_inverse_not_detailed_balance",
]
