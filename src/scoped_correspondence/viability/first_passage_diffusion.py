"""Brownian motion with drift: exact lower-barrier first-passage probability (DOMAIN_EXPANSION_ROADMAP.md Paket B4).

Response to prompts/Answers/nicht_stationäre_Treiber/
SCF_DOMAIN_EXPANSION_IMPLEMENTATION_PLAN.md, section 10: **a positive
EXPECTED reserve does not imply a vanishing probability of touching a lower
boundary at some point along the way.** For

    X_t = x0 + mu*t + sigma*W_t,    x0 > 0, sigma > 0,
    tau_0 = inf{t >= 0 : X_t <= 0}

the classical reflection-principle result for Brownian motion with drift
(Sigman; Huang, "Maximum of Brownian Motion with Drift") gives

    P(tau_0 <= H) = Phi((-x0 - mu*H) / (sigma*sqrt(H)))
                  + exp(-2*mu*x0/sigma^2) * Phi((-x0 + mu*H) / (sigma*sqrt(H)))

Both terms are combined in LOG SPACE (``scipy.special.logsumexp``) rather
than computed and added directly: the exponential factor
``exp(-2*mu*x0/sigma^2)`` and the second normal-CDF term can each
individually be far outside representable float range while their PRODUCT
is a perfectly ordinary probability in ``[0,1]`` -- direct multiplication
can overflow/underflow an intermediate value that the final sum would not.
"""

from __future__ import annotations

import numpy as np
from scipy.special import log_ndtr, logsumexp

from scoped_correspondence.errors import ScopeViolationError


def diffusion_lower_hitting_probability(x0: float, mu: float, sigma: float, horizon: float) -> float:
    """``P(tau_0 <= horizon)`` for ``X_t = x0 + mu*t + sigma*W_t`` hitting the
    lower barrier 0, for ``horizon >= 0``. Handles ``horizon=0``, ``x0<=0``
    (already at/below the barrier), and ``sigma=0`` (deterministic path) as
    explicit special cases; the general formula (log-space stable) covers
    everything else.
    """
    x0 = float(x0)
    mu = float(mu)
    sigma = float(sigma)
    horizon = float(horizon)
    if horizon < 0.0:
        raise ScopeViolationError(f"horizon must be >= 0; got {horizon!r}")
    if sigma < 0.0:
        raise ScopeViolationError(f"sigma must be >= 0; got {sigma!r}")

    if x0 <= 0.0:
        return 1.0  # already at/below the (closed) lower boundary: tau=0 <= horizon trivially.
    if horizon == 0.0:
        return 0.0  # x0 > 0 and no time has elapsed.

    if sigma == 0.0:
        # Deterministic path X_t = x0 + mu*t.
        if mu >= 0.0:
            return 0.0  # never decreases; x0 > 0 means it never reaches 0.
        t_star = x0 / (-mu)
        return 1.0 if t_star <= horizon else 0.0

    sqrt_h = np.sqrt(horizon)
    a = (-x0 - mu * horizon) / (sigma * sqrt_h)
    b = (-x0 + mu * horizon) / (sigma * sqrt_h)
    log_term1 = log_ndtr(a)
    log_term2 = (-2.0 * mu * x0 / (sigma * sigma)) + log_ndtr(b)
    log_p = logsumexp([log_term1, log_term2])
    return float(min(1.0, np.exp(log_p)))


def diffusion_ever_hitting_probability(x0: float, mu: float, sigma: float) -> float:
    """``P(tau_0 < infinity)`` -- the INFINITE-horizon ever-hitting probability,
    ``exp(-2*mu*x0/sigma^2)`` for ``mu > 0`` (positive drift, away from the
    barrier), ``1.0`` for ``mu <= 0`` (barrier is eventually reached almost
    surely for a driftless or downward-drifting process). This is a genuinely
    DIFFERENT statement from any finite-horizon scan and must never be
    extrapolated from one (plan section 10.1).
    """
    x0 = float(x0)
    mu = float(mu)
    sigma = float(sigma)
    if sigma < 0.0:
        raise ScopeViolationError(f"sigma must be >= 0; got {sigma!r}")
    if x0 <= 0.0:
        return 1.0
    if mu <= 0.0:
        return 1.0
    if sigma == 0.0:
        return 0.0  # mu > 0, deterministic path moves away from 0 forever.
    return float(np.exp(-2.0 * mu * x0 / (sigma * sigma)))


def brownian_bridge_crossing_probability(x: float, y: float, sigma: float, delta: float) -> float:
    """``P(bridge touches 0 during [t, t+delta] | X_t=x, X_{t+delta}=y)`` for
    ``x > 0``, ``y > 0`` -- the conditional Brownian-bridge crossing
    probability ``exp(-2*x*y/(sigma^2*delta))``. Only valid under CONSTANT
    diffusion coefficient ``sigma`` and both endpoints strictly positive
    (plan section 10.3); a time-grid simulation that only checks endpoints
    would silently miss exactly the crossings this quantifies.
    """
    x, y, sigma, delta = float(x), float(y), float(sigma), float(delta)
    if x <= 0.0 or y <= 0.0:
        raise ScopeViolationError(
            f"brownian_bridge_crossing_probability requires both endpoints > 0; got x={x!r}, y={y!r}"
        )
    if sigma <= 0.0 or delta <= 0.0:
        raise ScopeViolationError(f"sigma and delta must be > 0; got sigma={sigma!r}, delta={delta!r}")
    return float(np.exp(-2.0 * x * y / (sigma * sigma * delta)))


__all__ = [
    "diffusion_lower_hitting_probability",
    "diffusion_ever_hitting_probability",
    "brownian_bridge_crossing_probability",
]
