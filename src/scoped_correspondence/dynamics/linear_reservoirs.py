"""Parallel linear reservoirs: exact update, mass balance, and memory kernel (DOMAIN_EXPANSION_ROADMAP.md Paket B3a).

Response to prompts/Answers/nicht_stationäre_Treiber/
SCF_DOMAIN_EXPANSION_IMPLEMENTATION_PLAN.md, section 9.2-9.3: does a model
with TWO discharge time scales improve on a single reservoir under the SAME
input and observation? For reservoir ``j``,

    dS_j/dt = alpha_j*u(t) - k_j*S_j,    q(t) = sum_j k_j*S_j(t),
    alpha_j >= 0, sum_j alpha_j = 1

For CONSTANT input ``u`` over an interval ``[t, t+dt]`` this has the exact
closed form

    S_j(t+dt) = exp(-k_j*dt)*S_j(t) + alpha_j*u*(1-exp(-k_j*dt))/k_j

computed via ``-expm1(-k*dt)/k`` (not ``(1-exp(-k*dt))/k`` directly) for
numerical stability as ``k*dt -> 0``, where naive evaluation loses
precision to cancellation; the ``k=0`` limit (``S + alpha*u*dt``) is taken
explicitly rather than relying on the numerically-unstable form to survive
the limit. The mean discharge over the SAME interval follows from mass
balance, not from evaluating the kernel: ``qbar = (S(t)+u*dt-S(t+dt))/dt``.

For arbitrary (not necessarily piecewise-constant) input, the linear model
has an exact convolution representation

    q(t) = sum_j k_j*S_j(0)*e^{-k_j*t} + integral_0^t h(t-s)*u(s) ds,
    h(u) = sum_j alpha_j*k_j*e^{-k_j*u}

(the Mori-Zwanzig-style memory kernel already used in
``closure/linear_memory_projection.py``, specialized to this diagonal
case). Per the plan's explicit either/or (section 9.3), the more general
hidden-state-excitation extension of ``linear_memory_projection.py`` is
NOT built here; this direct convolution is implemented and checked instead.

**Correction (2026-09-24, response to
prompts/Answers/nicht_stationäre_Treiber/SCF_Review_fcc9a43.md, findings
R3+R3b -- two real numerical bugs):**

**R3: ``convolution_discharge`` completely missed FAST kernels.** The
naive quadrature integrated ``h(t-s)*u(s)`` directly over ``[0,t]`` with no
knowledge of the kernel's own timescale ``1/k``. For ``k=100000``, the
kernel is essentially a delta spike of width ``~1e-5`` concentrated at the
right edge ``s=t`` -- the adaptive quadrature's initial sample points can
miss it ENTIRELY, since nothing tells it where to look. Astra's exact
counterexample: ``S0=0, alpha=1, u=1, k=100000, t=1`` has the closed-form
answer ``1-e^{-100000} ≈ 1``, but the old code returned
``2.06e-45`` -- the kernel's mass was never sampled. Fixed by substituting
``v = k_j*(t-s)`` PER RESERVOIR before integrating: this rescales the
kernel's decay to exactly rate ``1`` in the transformed variable
regardless of ``k_j``, so the integrand ``e^{-v}`` always has an
O(1) natural scale for the quadrature, with the upper limit capped at
``min(k_j*t, 745)`` (``e^{-745}`` is already below the smallest positive
double) so the quadrature is never asked to cover an astronomically large,
uninformative flat-zero tail.

**R3b: ``reservoir_interval_discharge`` lost all precision for tiny
``dt``.** The mass-balance form ``(S(t)+u*dt-S(t+dt))/dt`` subtracts two
NEARLY EQUAL storage values when ``dt`` is small, then divides by the same
tiny ``dt`` -- amplifying whatever cancellation error remains. Astra's
exact counterexample: ``reservoir_interval_discharge(1, 0, 1, 1e-17)``
returned exactly ``0.0`` (total cancellation), while the true value
``(1-e^{-1e-17})/1e-17 ≈ 1``. Fixed by using the algebraically equivalent
but cancellation-free DIRECT form (never subtracting two close storage
values): with ``z=k*dt`` and ``E(z)=(1-e^{-z})/z`` (itself computed via
``-expm1(-z)/z``, exact even as ``z->0``),

    qbar = k*S0*E(z) + alpha*u*(1-E(z))

derived directly from the closed-form update (see
``verify_linear_reservoirs.py``'s ``r3b_...`` check for the algebraic
derivation), with ``k=0`` handled as an explicit exact limit (``qbar=0``:
a reservoir with no outflow rate has no discharge at all, by definition of
the ODE).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Sequence, Tuple

import numpy as np
from scipy.integrate import quad

from scoped_correspondence.errors import ScopeViolationError


def _validate_alphas_rates(alphas: Sequence[float], rates: Sequence[float]) -> None:
    if len(alphas) != len(rates):
        raise ScopeViolationError(f"alphas and rates must have equal length; got {len(alphas)} vs {len(rates)}")
    if len(alphas) == 0:
        raise ScopeViolationError("need at least one reservoir")
    if any(a < 0.0 for a in alphas):
        raise ScopeViolationError(f"alphas must all be >= 0; got {alphas!r}")
    if abs(sum(alphas) - 1.0) > 1e-9:
        raise ScopeViolationError(f"alphas must sum to 1; got sum={sum(alphas)!r}")
    if any(k < 0.0 for k in rates):
        raise ScopeViolationError(f"rates must all be >= 0; got {rates!r}")


def reservoir_step(storage: float, inflow_rate: float, rate: float, dt: float, alpha: float = 1.0) -> float:
    """Exact update of a single linear reservoir (``dS/dt = alpha*inflow_rate - rate*S``)
    over ``[t, t+dt]`` at CONSTANT ``inflow_rate``. ``rate=0`` is handled by an explicit
    continuous limit, not by relying on the general formula's numerical behavior there.
    """
    if dt < 0.0:
        raise ScopeViolationError(f"dt must be >= 0; got {dt!r}")
    if rate < 0.0:
        raise ScopeViolationError(f"rate must be >= 0; got {rate!r}")
    if storage < 0.0:
        raise ScopeViolationError(f"storage must be >= 0; got {storage!r}")
    if rate == 0.0:
        return float(storage + alpha * inflow_rate * dt)
    decay = np.exp(-rate * dt)
    gain = alpha * inflow_rate * (-np.expm1(-rate * dt)) / rate
    return float(decay * storage + gain)


def reservoir_interval_discharge(storage: float, inflow_rate: float, rate: float, dt: float, alpha: float = 1.0) -> float:
    """Mean discharge over ``[t, t+dt]`` via the DIRECT closed form (cancellation-free
    even for tiny ``dt`` -- see module docstring, finding R3b):

        qbar = rate*storage*E(z) + alpha*inflow_rate*(1-E(z)),   z = rate*dt,
        E(z) = (1-exp(-z))/z computed as -expm1(-z)/z

    NOT the mass-balance form ``(S(t)+alpha*inflow_rate*dt-S(t+dt))/dt``, which
    subtracts two nearly-equal storage values for small ``dt`` and loses all
    precision (Astra's exact counterexample: ``dt=1e-17`` gave ``0.0`` instead of
    the true value ``~1``).
    """
    if dt <= 0.0:
        raise ScopeViolationError(f"dt must be > 0; got {dt!r}")
    if rate < 0.0:
        raise ScopeViolationError(f"rate must be >= 0; got {rate!r}")
    if storage < 0.0:
        raise ScopeViolationError(f"storage must be >= 0; got {storage!r}")
    if rate == 0.0:
        return 0.0  # no outflow rate at all: discharge is identically zero (see module docstring).
    z = rate * dt
    E = -np.expm1(-z) / z
    return float(rate * storage * E + alpha * inflow_rate * (1.0 - E))


def parallel_reservoir_step(
    storages: Sequence[float], inflow_rate: float, alphas: Sequence[float], rates: Sequence[float], dt: float
) -> Tuple[float, ...]:
    """Exact update of ALL parallel reservoirs sharing the same constant total inflow,
    split by ``alphas`` (``sum(alphas)=1``)."""
    _validate_alphas_rates(alphas, rates)
    if len(storages) != len(alphas):
        raise ScopeViolationError(f"storages must match alphas/rates length; got {len(storages)} vs {len(alphas)}")
    return tuple(
        reservoir_step(s, inflow_rate, k, dt, alpha=a) for s, a, k in zip(storages, alphas, rates)
    )


def parallel_reservoir_discharge(storages: Sequence[float], rates: Sequence[float]) -> float:
    """Instantaneous total discharge ``q(t) = sum_j k_j*S_j(t)``."""
    if len(storages) != len(rates):
        raise ScopeViolationError(f"storages and rates must have equal length; got {len(storages)} vs {len(rates)}")
    return float(sum(k * s for s, k in zip(storages, rates)))


def parallel_reservoir_interval_discharge(
    storages: Sequence[float], inflow_rate: float, alphas: Sequence[float], rates: Sequence[float], dt: float
) -> float:
    """Mean TOTAL discharge over ``[t, t+dt]``: sum of each reservoir's own
    cancellation-free direct-form discharge (see ``reservoir_interval_discharge``,
    finding R3b) -- NOT a mass-balance subtraction on the summed storage, which
    has the same cancellation failure for small ``dt``.
    """
    if dt <= 0.0:
        raise ScopeViolationError(f"dt must be > 0; got {dt!r}")
    _validate_alphas_rates(alphas, rates)
    if len(storages) != len(alphas):
        raise ScopeViolationError(f"storages must match alphas/rates length; got {len(storages)} vs {len(alphas)}")
    return float(sum(
        reservoir_interval_discharge(s, inflow_rate, k, dt, alpha=a)
        for s, a, k in zip(storages, alphas, rates)
    ))


def memory_kernel(t: float, alphas: Sequence[float], rates: Sequence[float]) -> float:
    """Impulse-response kernel ``h(t) = sum_j alpha_j*k_j*e^{-k_j*t}``."""
    _validate_alphas_rates(alphas, rates)
    if t < 0.0:
        raise ScopeViolationError(f"t must be >= 0; got {t!r}")
    return float(sum(a * k * np.exp(-k * t) for a, k in zip(alphas, rates)))


_MAX_EXP_ARG = 745.0  # exp(-745) is already below the smallest positive normal double.


def convolution_discharge(
    t: float, initial_storages: Sequence[float], alphas: Sequence[float], rates: Sequence[float],
    inflow_fn: Callable[[float], float],
) -> float:
    """Exact continuous-time total discharge for ARBITRARY (not necessarily
    piecewise-constant) input ``inflow_fn``:

        q(t) = sum_j k_j*S_j(0)*e^{-k_j*t} + integral_0^t h(t-s)*inflow_fn(s) ds,
        h(u) = sum_j alpha_j*k_j*e^{-k_j*u}

    **Correction (finding R3):** the convolution term is now integrated
    SEPARATELY per reservoir ``j``, with the substitution ``v = k_j*(t-s)``
    applied BEFORE quadrature: this rescales reservoir ``j``'s exponential decay
    to exactly rate 1 in ``v`` regardless of how large ``k_j`` is, so the
    quadrature always sees an O(1)-scale integrand
    (``e^{-v} * inflow_fn(t - v/k_j)``) instead of one whose entire mass can sit
    in a region orders of magnitude narrower than the adaptive sampler's initial
    grid (the previous direct-``s`` integration missed such kernels ENTIRELY --
    see module docstring). The upper integration limit is capped at
    ``min(k_j*t, 745)`` since ``e^{-745}`` already underflows double precision,
    so no quadrature budget is spent on a provably negligible tail.
    A ``k_j=0`` reservoir contributes exactly 0 (see ``reservoir_interval_discharge``).
    """
    _validate_alphas_rates(alphas, rates)
    if len(initial_storages) != len(alphas):
        raise ScopeViolationError("initial_storages must match alphas/rates length")
    if t < 0.0:
        raise ScopeViolationError(f"t must be >= 0; got {t!r}")
    if t == 0.0:
        return parallel_reservoir_discharge(initial_storages, rates)

    initial_term = sum(k * s0 * np.exp(-k * t) for s0, k in zip(initial_storages, rates))

    conv_term = 0.0
    for a, k in zip(alphas, rates):
        if k == 0.0:
            continue  # zero-outflow-rate reservoir contributes nothing to discharge.
        v_max = min(k * t, _MAX_EXP_ARG)

        def integrand(v: float, k: float = k) -> float:
            return np.exp(-v) * inflow_fn(t - v / k)

        term, _ = quad(integrand, 0.0, v_max, limit=200)
        conv_term += a * term

    return float(initial_term + conv_term)


@dataclass(frozen=True)
class LinearReservoirSpec:
    alphas: Tuple[float, ...]
    rates: Tuple[float, ...]


__all__ = [
    "reservoir_step", "reservoir_interval_discharge",
    "parallel_reservoir_step", "parallel_reservoir_discharge", "parallel_reservoir_interval_discharge",
    "memory_kernel", "convolution_discharge", "LinearReservoirSpec",
]
