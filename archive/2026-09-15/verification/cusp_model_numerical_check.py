"""Numerical verification of two claims from system_layer_utac.md (2026-09-15):

1. a = -S(Theta), i.e. the cusp splitting factor equals the negative of the
   Information-layer Stability (S = -lambda_max) evaluated at the reference
   point R_ctrl = Theta. Checked via direct numerical linearization of the
   drift, not assumed from the closed-form derivative.

2. Latitude (basin-stability-estimated distance to the saddle) matches the
   analytic saddle distance sqrt(a) for the symmetric cusp potential
   V(x) = x^4/4 - (a/2)x^2, x = R_ctrl - Theta, b=0.

This is a synthetic/toy dynamical system, not a real GenesisAeon package --
it validates that our derived formulas are numerically self-consistent, not
that any real-world CREP_critical~=0.84 claim holds. See DESIGN.md.
"""

from __future__ import annotations

import numpy as np

RNG = np.random.default_rng(20260915)


def drift(x: float, a: float, b: float = 0.0) -> float:
    """dx/dt = -dV/dx for V(x) = x^4/4 - (a/2)x^2 - b*x."""
    return -(x**3 - a * x - b)


def numerical_lambda_max(a: float, b: float, x_star: float, eps: float = 1e-6) -> float:
    """Local linearization eigenvalue at x_star, via central finite difference
    of the drift itself -- not the closed-form derivative -- so this is a
    genuine independent numerical check, not a restatement of the algebra."""
    return (drift(x_star + eps, a, b) - drift(x_star - eps, a, b)) / (2 * eps)


def check_a_equals_minus_S_theta() -> None:
    print("=== Check 1: a = -S(Theta) ===")
    for a in [-1.0, -0.3, 0.0, 0.3, 1.0, 2.5]:
        lambda_max = numerical_lambda_max(a, b=0.0, x_star=0.0)
        S_theta = -lambda_max
        predicted_a = -S_theta
        print(
            f"a={a:6.3f}  numerical lambda_max(0)={lambda_max:7.4f}  "
            f"S(Theta)={S_theta:7.4f}  -S(Theta)={predicted_a:7.4f}  "
            f"match={'OK' if abs(predicted_a - a) < 1e-6 else 'MISMATCH'}"
        )


def simulate_langevin(x0: float, a: float, b: float, dt: float, steps: int, noise: float) -> np.ndarray:
    x = np.empty(steps)
    x[0] = x0
    cur = x0
    sqrt_dt = np.sqrt(dt)
    for i in range(1, steps):
        cur = cur + drift(cur, a, b) * dt + noise * sqrt_dt * RNG.normal()
        x[i] = cur
    return x


def basin_stability_latitude(a: float, stable_branch: float, n_trials: int = 400) -> float:
    """Monte-Carlo basin-stability-style estimate of the distance from the
    stable branch to the basin edge: perturb by increasing amounts, run the
    (noiseless) deterministic flow forward, find the largest perturbation
    that still returns to the original branch."""
    displacements = np.linspace(0.01, 3.0, 300)
    for d in displacements:
        # perturb TOWARD and past the saddle at x=0 (the actual basin edge),
        # not away from it -- pushing away from the saddle stays in the same
        # basin forever for this potential shape.
        x = stable_branch - d
        # deterministic relaxation, no noise -- pure basin test
        for _ in range(20000):
            x = x + drift(x, a, 0.0) * 0.001
        # did it end up back near stable_branch, or did it cross to the other side?
        if abs(x - stable_branch) > 0.5:
            return d  # this displacement was enough to escape -- edge found
    return displacements[-1]  # never escaped within tested range


def check_latitude() -> None:
    print("\n=== Check 2: Latitude (Basin-Stability estimate) vs analytic sqrt(a) ===")
    for a in [0.5, 1.0, 2.0, 4.0]:
        stable_branch = np.sqrt(a)  # one of the two stable minima at x=+sqrt(a)
        analytic_latitude = stable_branch - 0.0  # distance to saddle at x=0
        estimated = basin_stability_latitude(a, stable_branch)
        rel_err = abs(estimated - analytic_latitude) / analytic_latitude
        print(
            f"a={a:4.2f}  stable branch at x={stable_branch:6.4f}  "
            f"analytic Latitude (saddle distance)={analytic_latitude:6.4f}  "
            f"Basin-Stability-estimated={estimated:6.4f}  "
            f"rel.err={rel_err*100:5.2f}%"
        )


if __name__ == "__main__":
    check_a_equals_minus_S_theta()
    check_latitude()
