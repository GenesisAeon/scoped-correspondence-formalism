"""Mori-Zwanzig-style exact memory reduction for linear systems (Milestone 57).

CAPABILITY_EXPANSION_ROADMAP.md Priority 3, response to Astra's 2026-09-24
capability assessment: "Die Mori-Zwanzig-Perspektive erklärt, weshalb das
Eliminieren verborgener Zustände Gedächtnis und einen vom verborgenen
Anfangszustand abhängigen Restterm erzeugt" (Chorin, Hald & Kupferman
2000, PNAS 97, 2968-2973).

Setup: a linear system with one OBSERVED scalar ``x`` coupled to an
arbitrary-dimensional HIDDEN block ``z`` (``n_z >= 1``, so this covers
both Astra's "two-state" and "three-state" reference cases and beyond):

    dx/dt = A*x + B @ z + f(t)      (external forcing acts on x only)
    dz/dt = C * x + D @ z

Eliminating ``z`` exactly (variation of constants on the linear ``z``
equation, then substituting back) gives a closed, EXACT integro-
differential equation for ``x`` alone:

    dx/dt = A*x(t) + INT_0^t K(t-s)*x(s) ds + B @ expm(D*t) @ z0 + f(t)

with the exact memory kernel ``K(u) = B @ expm(D*u) @ C`` (a scalar
function of the lag ``u``) and an explicit residual term depending on the
HIDDEN initial state ``z0`` — precisely the two features Chorin, Hald &
Kupferman attribute to eliminating hidden state: a memory term and an
initial-hidden-state-dependent remainder. The scalar exponential kernel
used elsewhere in this repository's recovery-rate examples
(``exp[-INT_s^t r(v)dv]``, constant-rate case ``exp[-r*(t-s)]``) is the
``n_z=1`` special case of this ``K``.

Three variants are compared, all against the SAME ground truth (the full
``(x,z)`` system, numerically integrated to high precision — this is the
one exact quantity available; the memory equation above is an exact
REWRITING of the same dynamics, not a different, independently checkable
trajectory):

- **exact** — the full ``(x,z)`` system (ground truth for ``x(t)``).
- **memoryless** — ``dx/dt = A*x(t) + f(t)``, dropping the hidden
  coupling entirely (the naive Markov/closure approximation this
  repository's ``closure/`` module otherwise tests for VALID cases —
  here it is deliberately WRONG by construction, to see how badly).
- **finite_memory** — ``dx/dt = A*x(t) + INT_{max(0,t-W)}^{t}
  K(t-s)*x(s) ds + f(t)`` for a finite memory window ``W``: keeps the
  memory term but truncates it and drops the ``B @ expm(D*t) @ z0`` term
  (as if the hidden state's own initial condition had already been
  forgotten) — solved by a fixed-step explicit Euler scheme with a
  precomputed kernel lookup table (first-order accurate; adequate for the
  comparison here, not a claim of high-precision integration).

Per Astra's explicit request, comparison metrics go beyond mean state
error: the location and value of ``x(t)``'s MINIMUM (found by continuous
optimization on a cubic-spline interpolant, not a grid argmin — same
discipline as ``viability.rate_dependent_buffer`` after its Paket-6 grid-
search-bug fix) and the time of first crossing a given boundary (found by
root-finding on the same interpolant, not nearest-grid-point).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional, Tuple

import numpy as np
from scipy.integrate import solve_ivp
from scipy.interpolate import CubicSpline
from scipy.linalg import expm
from scipy.optimize import brentq, minimize_scalar

from scoped_correspondence.errors import ScopeViolationError

SOURCE = (
    "Chorin, A. J.; Hald, O. H.; Kupferman, R. (2000): Optimal prediction and "
    "the Mori-Zwanzig representation of irreversible processes. PNAS 97, "
    "2968-2973."
)


def _as_row(v: Any, n: int) -> np.ndarray:
    arr = np.atleast_1d(np.asarray(v, dtype=float)).reshape(1, -1)
    if arr.shape[1] != n:
        raise ScopeViolationError(f"expected a length-{n} vector; got shape {arr.shape}")
    return arr


def _as_col(v: Any, n: int) -> np.ndarray:
    arr = np.atleast_1d(np.asarray(v, dtype=float)).reshape(-1, 1)
    if arr.shape[0] != n:
        raise ScopeViolationError(f"expected a length-{n} vector; got shape {arr.shape}")
    return arr


def exact_memory_kernel(B: Any, D: Any, C: Any) -> Callable[[float], float]:
    """``K(u) = B @ expm(D*u) @ C`` — the exact scalar memory kernel for eliminating
    the hidden block ``z`` from ``dx/dt = A*x + B@z``, ``dz/dt = C*x + D@z``.
    """
    D_mat = np.atleast_2d(np.asarray(D, dtype=float))
    n_z = D_mat.shape[0]
    if D_mat.shape[1] != n_z:
        raise ScopeViolationError(f"exact_memory_kernel: D must be square; got shape {D_mat.shape}")
    B_row = _as_row(B, n_z)
    C_col = _as_col(C, n_z)

    def K(u: float) -> float:
        if u < 0:
            raise ScopeViolationError(f"exact_memory_kernel: u must be >= 0; got {u!r}")
        return float((B_row @ expm(D_mat * u) @ C_col)[0, 0])

    return K


def simulate_full_system(
    A: float, B: Any, D: Any, C: Any, x0: float, z0: Any,
    forcing: Callable[[float], float], t_eval: np.ndarray,
) -> Tuple[np.ndarray, np.ndarray]:
    """Ground truth: numerically integrate the full (x, z) linear system."""
    D_mat = np.atleast_2d(np.asarray(D, dtype=float))
    n_z = D_mat.shape[0]
    B_row = _as_row(B, n_z)
    C_col = _as_col(C, n_z)
    z0_vec = _as_col(z0, n_z).flatten()
    y0 = np.concatenate([[float(x0)], z0_vec])

    def rhs(t: float, y: np.ndarray) -> np.ndarray:
        x, z = y[0], y[1:]
        dx = float(A) * x + float(B_row @ z) + float(forcing(t))
        dz = C_col.flatten() * x + D_mat @ z
        return np.concatenate([[dx], dz])

    sol = solve_ivp(rhs, (float(t_eval[0]), float(t_eval[-1])), y0, t_eval=t_eval, rtol=1e-11, atol=1e-13)
    if not sol.success:
        raise ScopeViolationError(f"simulate_full_system: integration failed: {sol.message}")
    return sol.y[0], sol.y[1:]


def simulate_memoryless_approximation(
    A: float, x0: float, forcing: Callable[[float], float], t_eval: np.ndarray
) -> np.ndarray:
    """``dx/dt = A*x + f(t)`` — drops the hidden coupling entirely."""
    def rhs(t: float, y: np.ndarray) -> np.ndarray:
        return [float(A) * y[0] + float(forcing(t))]

    sol = solve_ivp(rhs, (float(t_eval[0]), float(t_eval[-1])), [float(x0)], t_eval=t_eval, rtol=1e-11, atol=1e-13)
    if not sol.success:
        raise ScopeViolationError(f"simulate_memoryless_approximation: integration failed: {sol.message}")
    return sol.y[0]


def simulate_finite_memory_approximation(
    A: float, B: Any, D: Any, C: Any, x0: float,
    forcing: Callable[[float], float], t_span: Tuple[float, float],
    memory_window: float, n_steps: int = 4000,
) -> Tuple[np.ndarray, np.ndarray]:
    """Fixed-step explicit Euler for ``dx/dt = A*x(t) + INT_{max(0,t-W)}^t K(t-s)x(s)ds + f(t)``.

    Drops the ``B @ expm(D*t) @ z0`` initial-hidden-state term (as if the
    hidden state's own history before ``t=0`` had already relaxed away) and
    truncates the memory integral to the trailing window ``memory_window``.
    First-order accurate (explicit Euler); a precomputed kernel lookup
    table keeps the per-step trapezoid cheap even though the kernel itself
    needs a matrix exponential.
    """
    if memory_window <= 0.0:
        raise ScopeViolationError(f"simulate_finite_memory_approximation: memory_window must be > 0; got {memory_window!r}")
    if n_steps < 10:
        raise ScopeViolationError(f"simulate_finite_memory_approximation: n_steps must be >= 10; got {n_steps!r}")
    kernel = exact_memory_kernel(B, D, C)
    t0, t1 = float(t_span[0]), float(t_span[1])
    if not (t1 > t0):
        raise ScopeViolationError("simulate_finite_memory_approximation: t_span must be increasing")

    ts = np.linspace(t0, t1, int(n_steps) + 1)
    dt = ts[1] - ts[0]
    window_steps = max(1, int(round(memory_window / dt)))
    kernel_table = np.array([kernel(k * dt) for k in range(window_steps + 1)])

    xs = np.zeros(n_steps + 1)
    xs[0] = float(x0)
    for i in range(n_steps):
        t = ts[i]
        lo = max(0, i - window_steps)
        if i - lo >= 1:
            hist_x = xs[lo : i + 1]
            ker_vals = kernel_table[i - lo :: -1][: len(hist_x)]
            mem = float(np.trapz(ker_vals * hist_x, dx=dt))
        else:
            mem = 0.0
        dxdt = float(A) * xs[i] + mem + float(forcing(t))
        xs[i + 1] = xs[i] + dt * dxdt
    return ts, xs


def _continuous_min(t: np.ndarray, x: np.ndarray) -> Tuple[float, float]:
    spline = CubicSpline(t, x)
    res = minimize_scalar(lambda tt: float(spline(tt)), bounds=(float(t[0]), float(t[-1])), method="bounded")
    return float(res.x), float(res.fun)


def _first_downward_crossing(t: np.ndarray, x: np.ndarray, boundary: float) -> Optional[float]:
    spline = CubicSpline(t, x)
    vals = spline(t) - float(boundary)
    for i in range(len(t) - 1):
        if vals[i] >= 0.0 and vals[i + 1] < 0.0:
            return float(brentq(lambda tt: float(spline(tt)) - float(boundary), t[i], t[i + 1]))
    return None


@dataclass(frozen=True)
class MemoryProjectionComparison:
    t: Tuple[float, ...]
    x_exact: Tuple[float, ...]
    x_memoryless: Tuple[float, ...]
    x_finite_memory: Tuple[float, ...]
    memory_window: float
    mean_abs_error_memoryless: float
    mean_abs_error_finite_memory: float
    exact_min_time: float
    exact_min_value: float
    memoryless_min_time: float
    memoryless_min_value: float
    finite_memory_min_time: float
    finite_memory_min_value: float
    boundary: float
    exact_crossing_time: Optional[float]
    memoryless_crossing_time: Optional[float]
    finite_memory_crossing_time: Optional[float]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "t": list(self.t), "x_exact": list(self.x_exact),
            "x_memoryless": list(self.x_memoryless), "x_finite_memory": list(self.x_finite_memory),
            "memory_window": self.memory_window,
            "mean_abs_error_memoryless": self.mean_abs_error_memoryless,
            "mean_abs_error_finite_memory": self.mean_abs_error_finite_memory,
            "exact_min_time": self.exact_min_time, "exact_min_value": self.exact_min_value,
            "memoryless_min_time": self.memoryless_min_time, "memoryless_min_value": self.memoryless_min_value,
            "finite_memory_min_time": self.finite_memory_min_time, "finite_memory_min_value": self.finite_memory_min_value,
            "boundary": self.boundary,
            "exact_crossing_time": self.exact_crossing_time,
            "memoryless_crossing_time": self.memoryless_crossing_time,
            "finite_memory_crossing_time": self.finite_memory_crossing_time,
        }


def run_memory_projection_comparison(
    A: float, B: Any, D: Any, C: Any, x0: float, z0: Any,
    forcing: Callable[[float], float], t_span: Tuple[float, float],
    *, memory_window: float, boundary: float, n_points: int = 400, n_steps_finite: int = 4000,
) -> MemoryProjectionComparison:
    t = np.linspace(float(t_span[0]), float(t_span[1]), int(n_points))
    x_exact, _z_exact = simulate_full_system(A, B, D, C, x0, z0, forcing, t)
    x_memless = simulate_memoryless_approximation(A, x0, forcing, t)
    ts_fine, x_fine = simulate_finite_memory_approximation(
        A, B, D, C, x0, forcing, t_span, memory_window, n_steps=n_steps_finite
    )
    x_finite_on_t = np.interp(t, ts_fine, x_fine)

    mae_memless = float(np.mean(np.abs(x_memless - x_exact)))
    mae_finite = float(np.mean(np.abs(x_finite_on_t - x_exact)))

    exact_min_t, exact_min_v = _continuous_min(t, x_exact)
    memless_min_t, memless_min_v = _continuous_min(t, x_memless)
    finite_min_t, finite_min_v = _continuous_min(t, x_finite_on_t)

    exact_cross = _first_downward_crossing(t, x_exact, boundary)
    memless_cross = _first_downward_crossing(t, x_memless, boundary)
    finite_cross = _first_downward_crossing(t, x_finite_on_t, boundary)

    return MemoryProjectionComparison(
        t=tuple(float(v) for v in t),
        x_exact=tuple(float(v) for v in x_exact),
        x_memoryless=tuple(float(v) for v in x_memless),
        x_finite_memory=tuple(float(v) for v in x_finite_on_t),
        memory_window=float(memory_window),
        mean_abs_error_memoryless=mae_memless,
        mean_abs_error_finite_memory=mae_finite,
        exact_min_time=exact_min_t, exact_min_value=exact_min_v,
        memoryless_min_time=memless_min_t, memoryless_min_value=memless_min_v,
        finite_memory_min_time=finite_min_t, finite_memory_min_value=finite_min_v,
        boundary=float(boundary),
        exact_crossing_time=exact_cross,
        memoryless_crossing_time=memless_cross,
        finite_memory_crossing_time=finite_cross,
    )


__all__ = [
    "SOURCE",
    "MemoryProjectionComparison",
    "exact_memory_kernel",
    "simulate_full_system",
    "simulate_memoryless_approximation",
    "simulate_finite_memory_approximation",
    "run_memory_projection_comparison",
]
