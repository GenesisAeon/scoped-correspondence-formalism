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
    """Mean discharge over ``[t, t+dt]`` via MASS BALANCE (not by evaluating the
    instantaneous kernel): ``qbar = (S(t) + alpha*inflow_rate*dt - S(t+dt)) / dt``.
    """
    if dt <= 0.0:
        raise ScopeViolationError(f"dt must be > 0; got {dt!r}")
    storage_end = reservoir_step(storage, inflow_rate, rate, dt, alpha=alpha)
    return float((storage + alpha * inflow_rate * dt - storage_end) / dt)


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
    """Mean TOTAL discharge over ``[t, t+dt]`` via mass balance on the summed storage."""
    if dt <= 0.0:
        raise ScopeViolationError(f"dt must be > 0; got {dt!r}")
    _validate_alphas_rates(alphas, rates)
    total_start = float(sum(storages))
    new_storages = parallel_reservoir_step(storages, inflow_rate, alphas, rates, dt)
    total_end = float(sum(new_storages))
    return (total_start + inflow_rate * dt - total_end) / dt


def memory_kernel(t: float, alphas: Sequence[float], rates: Sequence[float]) -> float:
    """Impulse-response kernel ``h(t) = sum_j alpha_j*k_j*e^{-k_j*t}``."""
    _validate_alphas_rates(alphas, rates)
    if t < 0.0:
        raise ScopeViolationError(f"t must be >= 0; got {t!r}")
    return float(sum(a * k * np.exp(-k * t) for a, k in zip(alphas, rates)))


def convolution_discharge(
    t: float, initial_storages: Sequence[float], alphas: Sequence[float], rates: Sequence[float],
    inflow_fn: Callable[[float], float],
) -> float:
    """Exact continuous-time total discharge for ARBITRARY (not necessarily
    piecewise-constant) input ``inflow_fn``:

        q(t) = sum_j k_j*S_j(0)*e^{-k_j*t} + integral_0^t h(t-s)*inflow_fn(s) ds

    The convolution integral is evaluated by numerical quadrature (``scipy.integrate.quad``)
    -- an INDEPENDENT continuous-time representation, checked against the discrete
    step-recursion on piecewise-constant inputs as a control case (see
    ``verify_linear_reservoirs.py``).
    """
    _validate_alphas_rates(alphas, rates)
    if len(initial_storages) != len(alphas):
        raise ScopeViolationError("initial_storages must match alphas/rates length")
    if t < 0.0:
        raise ScopeViolationError(f"t must be >= 0; got {t!r}")
    if t == 0.0:
        return parallel_reservoir_discharge(initial_storages, rates)

    initial_term = sum(k * s0 * np.exp(-k * t) for s0, k in zip(initial_storages, rates))

    def integrand(s: float) -> float:
        return memory_kernel(t - s, alphas, rates) * inflow_fn(s)

    conv_term, _ = quad(integrand, 0.0, t, limit=200)
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
