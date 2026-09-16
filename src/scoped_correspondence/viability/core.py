"""Viability formulas: safe intervention transfer and shared-budget conflict.

context_transformations.md section 8; worked_example_viability.md.
Not a general polytope / level-set viability-kernel solver.
"""

from __future__ import annotations

import math
from typing import Dict, Mapping, Optional, Sequence, Tuple, Union

import numpy as np

from scoped_correspondence.errors import ScopeViolationError

ArrayLike = Union[np.ndarray, Sequence[float]]


def coupled_buffer_field(
    x: ArrayLike,
    r: ArrayLike,
    e: ArrayLike,
    u: ArrayLike,
    w: ArrayLike,
    k: float,
) -> np.ndarray:
    """Coupled two-buffer RHS (worked_example_viability.md V2):

        x_dot_i = -r_i (x_i - e_i) + u_i - w_i + k (x_j - x_i)
    """
    x_a, r_a, e_a, u_a, w_a = (np.asarray(v, dtype=float) for v in (x, r, e, u, w))
    for name, arr in (("x", x_a), ("r", r_a), ("e", e_a), ("u", u_a), ("w", w_a)):
        if arr.shape != (2,):
            raise ScopeViolationError(f"{name} must have shape (2,); got {arr.shape}")
    return -r_a * (x_a - e_a) + u_a - w_a + float(k) * (x_a[::-1] - x_a)


def orthant_action_demand(
    r: ArrayLike,
    e: ArrayLike,
    b: ArrayLike,
    W: ArrayLike,
    k: float,
) -> np.ndarray:
    """Minimal nonnegative corner actions a_i (worked_example_viability.md V8):

        a_i = max(0, W_i - r_i(e_i - b_i) - k(b_j - b_i))
    """
    r_a, e_a, b_a, W_a = (np.asarray(v, dtype=float) for v in (r, e, b, W))
    demand = W_a - r_a * (e_a - b_a) - float(k) * (b_a[::-1] - b_a)
    return np.maximum(0.0, demand)


def scalar_hitting_time(
    r: float,
    z_eq: float,
    b: float,
    U: float,
    W: float,
    z0: float,
) -> float:
    """First contact time t_hit under constant u=U, w=W (worked_example V1).

        z_* = z_eq + (U - W)/r
        t_hit = (1/r) log((z0 - z_*)/(b - z_*))   when z_* < b < z0
    """
    if r <= 0:
        raise ScopeViolationError(f"r must be > 0; got {r!r}")
    steady = z_eq + (U - W) / r
    if not (steady < b < z0):
        raise ScopeViolationError(
            "scalar_hitting_time requires z_* < b < z0 for finite first contact; "
            f"got z_*={steady!r}, b={b!r}, z0={z0!r}"
        )
    return float(math.log((z0 - steady) / (b - steady)) / r)


def scalar_solution(
    t: float,
    r: float,
    z_eq: float,
    U: float,
    W: float,
    z0: float,
) -> float:
    """z(t) = z_* + (z0 - z_*) e^{-r t} under constant u=U, w=W."""
    if r <= 0:
        raise ScopeViolationError(f"r must be > 0; got {r!r}")
    steady = z_eq + (U - W) / r
    return float(steady + (z0 - steady) * math.exp(-r * t))


def has_safe_transfer(
    r: float,
    z_eq: float,
    b: float,
    U: float,
    W: float,
    *,
    z0: Optional[float] = None,
) -> Dict[str, object]:
    """Safe intervention transfer for the scalar buffer (context_transformations.md section 8).

    Identity projection (macro state = micro scalar z). The three section-8
    conditions specialize as:

    - Executability: constant u=U is admissible (0 <= U and control set nonempty).
    - Successor compatibility: autonomous closed dynamics in z under (U,W).
    - Safe representation: K_hat = K = [b, +inf) (pi^{-1}(K_hat)subseteq K).

    Robust controlled invariance of the entire K under worst-case w=W holds iff

        r(z_eq - b) + U - W >= 0

    (worked_example_viability.md section 2). Returns a report dict with
    ``ok`` and the three condition flags — not a general viability kernel.
    """
    if r <= 0:
        raise ScopeViolationError(f"r must be > 0; got {r!r}")
    if U < 0 or W < 0:
        raise ScopeViolationError(f"U and W must be >= 0; got U={U!r}, W={W!r}")

    # Executability: open-loop constant max control is in U(z)=[0,U].
    executability = bool(U >= 0.0)

    # Successor compatibility: scalar model is closed in z (no hidden state).
    successor_compatibility = True

    # Safe representation: identity projection preserves K.
    safe_representation = True

    boundary_inward = float(r * (z_eq - b) + U - W)
    robust_invariance = boundary_inward >= -1e-15

    ok = bool(
        executability
        and successor_compatibility
        and safe_representation
        and robust_invariance
    )

    report: Dict[str, object] = {
        "ok": ok,
        "executability": executability,
        "successor_compatibility": successor_compatibility,
        "safe_representation": safe_representation,
        "boundary_inward": boundary_inward,
        "W_crit": float(r * (z_eq - b) + U),
        "robust_invariance_of_K": robust_invariance,
        "source": "context_transformations.md section 8; worked_example_viability.md section 2",
    }
    if z0 is not None:
        report["z0"] = float(z0)
        if not robust_invariance and z0 > b:
            try:
                report["hitting_time"] = scalar_hitting_time(r, z_eq, b, U, W, z0)
            except ScopeViolationError:
                report["hitting_time"] = None
    return report


def shared_budget_conflict(
    r: ArrayLike,
    e: ArrayLike,
    W: ArrayLike,
    k: float,
    U: float,
    b: ArrayLike = (0.0, 0.0),
) -> Dict[str, object]:
    """Coupled-buffer shared-budget conflict (r10 / t10_shared_budget_conflict).

    Each task alone may be feasible with full budget U, yet both together need
    a1+a2 > U at the common corner (worked_example_viability.md section 5, V9).

    Default numbers matching legacy t10:
        r=[1,1], e=[0.2,0.2], W=[0.7,0.7], k=0.5, U=0.75, b=[0,0]
        -> a=[0.5,0.5], required_joint=1, standalone_margin=0.25, conflict=True
    """
    r_a = np.asarray(r, dtype=float)
    e_a = np.asarray(e, dtype=float)
    W_a = np.asarray(W, dtype=float)
    b_a = np.asarray(b, dtype=float)
    if U < 0:
        raise ScopeViolationError(f"U must be >= 0; got {U!r}")

    a = orthant_action_demand(r_a, e_a, b_a, W_a, k)
    required = float(a.sum())
    # Standalone margin for task i with exclusive access to U against W_i:
    # r_i(e_i - b_i) + U - W_i  (exchange term vanishes if evaluating single stock
    # in isolation with the same parameters as the worked example when k terms
    # cancel at the symmetric corner — use the table value from section 5).
    # For the symmetric worked example: 0.2 + U - 0.7.
    standalone_margins = r_a * (e_a - b_a) + U - W_a
    corner_with_equal_split = coupled_buffer_field(
        b_a, r_a, e_a, np.array([U / 2.0, U / 2.0]), W_a, k
    )
    corner_with_demand = coupled_buffer_field(b_a, r_a, e_a, a, W_a, k)
    conflict = required > U + 1e-15
    return {
        "a": a.tolist(),
        "required_joint_budget": required,
        "available_budget": float(U),
        "standalone_margins": standalone_margins.tolist(),
        "standalone_margin": float(standalone_margins.min())
        if standalone_margins.size
        else float("nan"),
        "conflict": bool(conflict),
        "corner_with_equal_split": corner_with_equal_split.tolist(),
        "corner_with_required_actions": corner_with_demand.tolist(),
        "source": "worked_example_viability.md section 5; context_transformations.md section 8 r10",
    }


def unequal_rates_sum_derivatives(
    rates: ArrayLike = (1.0, 2.0),
    k: float = 0.7,
    states: Sequence[ArrayLike] = ((1.0, 0.0), (0.0, 1.0)),
) -> Dict[str, object]:
    """Same sum, distinct sum-derivatives when r1 != r2 (t07).

    Demonstrates broken sum-closure under unequal recovery rates.
    """
    r = np.asarray(rates, dtype=float)
    derivatives = []
    for x in states:
        dx = coupled_buffer_field(x, r, [0.0, 0.0], [0.0, 0.0], [0.0, 0.0], k)
        derivatives.append(float(dx.sum()))
    s0 = float(np.asarray(states[0], dtype=float).sum())
    return {
        "same_sum": s0,
        "two_derivatives": derivatives,
        "closed_in_sum": bool(abs(derivatives[0] - derivatives[1]) <= 1e-15),
    }


__all__ = [
    "coupled_buffer_field",
    "has_safe_transfer",
    "orthant_action_demand",
    "scalar_hitting_time",
    "scalar_solution",
    "shared_budget_conflict",
    "unequal_rates_sum_derivatives",
]
