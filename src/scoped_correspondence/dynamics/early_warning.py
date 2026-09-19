"""Early-warning / critical slowing down indicators (Milestone 36).

Maps S_rec = λ from dynamics.core to OU/AR(1) EWS (Scheffer et al. 2009):
    Var_∞ = σ²/(2λ);  ρ(Δt) = exp(−λ·Δt).
CALLS recovery_rate_at_equilibrium for λ; does NOT reimplement S_rec;
does NOT edit dynamics/core.py.

MANDATORY SCOPE FENCE (verbatim):
Boettiger & Hastings 2012 DOI 10.1098/rsif.2012.0125; Ditlevsen & Johnsen 2010 DOI 10.1029/2010GL044486 — rising Var/ρ necessary near λ→0 but NOT sufficient; false alarms; D-O events noise-induced. Also: no Var/S_rec ≡ beta_response.

Sources: Scheffer et al. 2009 DOI 10.1038/nature08227;
Boettiger & Hastings 2012 DOI 10.1098/rsif.2012.0125;
Ditlevsen & Johnsen 2010 DOI 10.1029/2010GL044486.
"""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from typing import Any, Dict, Tuple

from scoped_correspondence.dynamics.core import recovery_rate_at_equilibrium
from scoped_correspondence.errors import ScopeViolationError

EARLY_WARNING_COUNTEREXAMPLE_FENCE: str = (
    "Boettiger & Hastings 2012 DOI 10.1098/rsif.2012.0125; Ditlevsen & Johnsen 2010 "
    "DOI 10.1029/2010GL044486 — rising Var/ρ necessary near λ→0 but NOT sufficient; "
    "false alarms; D-O events noise-induced. Also: no Var/S_rec ≡ beta_response."
)

SOURCE = (
    "Scheffer et al. 2009 DOI 10.1038/nature08227; "
    "Boettiger & Hastings 2012 DOI 10.1098/rsif.2012.0125; "
    "Ditlevsen & Johnsen 2010 DOI 10.1029/2010GL044486"
)


def ou_variance(sigma: float, lam: float) -> float:
    """Stationary OU variance Var_∞ = σ²/(2λ). Raises if λ≤0."""
    lam_f = float(lam)
    if lam_f <= 0.0:
        raise ScopeViolationError(
            f"ou_variance: requires lam = S_rec > 0; got {lam!r}"
        )
    sig = float(sigma)
    return float((sig * sig) / (2.0 * lam_f))


def ou_autocorrelation(lam: float, delta_t: float) -> float:
    """ρ(Δt) = exp(−λ·Δt)."""
    return float(math.exp(-float(lam) * float(delta_t)))


def estimate_lambda_from_ar1(rho: float, delta_t: float) -> float:
    """λ̂ = −ln(ρ)/Δt. Requires 0<ρ<1 and Δt≠0."""
    r = float(rho)
    dt = float(delta_t)
    if not (0.0 < r < 1.0):
        raise ScopeViolationError(
            f"estimate_lambda_from_ar1: requires 0 < rho < 1; got {rho!r}"
        )
    if dt == 0.0:
        raise ScopeViolationError(
            f"estimate_lambda_from_ar1: delta_t must be nonzero; got {delta_t!r}"
        )
    return float(-math.log(r) / dt)


def lambda_from_cusp_equilibrium(
    x: float, a: float, tau: float = 1.0, b: float = 0.0,
) -> float:
    """λ = S_rec via dynamics.core.recovery_rate_at_equilibrium (CALL only)."""
    return float(recovery_rate_at_equilibrium(float(x), float(a), float(tau), float(b)))


@dataclass(frozen=True)
class EarlyWarningIndicators:
    """OU EWS at a cusp equilibrium (lam from core S_rec)."""

    x_star: float
    a: float
    tau: float
    b: float
    lam: float
    sigma: float
    delta_t: float
    variance: float
    rho: float

    def as_dict(self) -> Dict[str, Any]:
        return asdict(self)


def early_warning_at_cusp(
    x: float, a: float, sigma: float, delta_t: float,
    tau: float = 1.0, b: float = 0.0,
) -> EarlyWarningIndicators:
    """Var/ρ at cusp eq using core S_rec for λ."""
    lam = lambda_from_cusp_equilibrium(x, a, tau, b)
    var = ou_variance(sigma, lam)
    rho = ou_autocorrelation(lam, delta_t)
    return EarlyWarningIndicators(
        x_star=float(x), a=float(a), tau=float(tau), b=float(b),
        lam=float(lam), sigma=float(sigma), delta_t=float(delta_t),
        variance=float(var), rho=float(rho),
    )


def control_far_from_fold(
    a_values: Tuple[float, float], sigma: float, delta_t: float,
    tau: float = 1.0, b: float = 0.0, rel_tol: float = 0.5,
) -> Dict[str, Any]:
    """Control: far from fold, Var/ρ stay moderate (no CSD blow-up)."""
    if len(a_values) != 2:
        raise ScopeViolationError(
            f"control_far_from_fold: need exactly two a values; got {a_values!r}"
        )
    results = []
    for a in a_values:
        aa = float(a)
        if aa <= 0.0:
            raise ScopeViolationError(
                f"control_far_from_fold: requires a > 0; got {a!r}"
            )
        ind = early_warning_at_cusp(math.sqrt(aa), aa, sigma, delta_t, tau=tau, b=b)
        results.append(ind)
    v0, v1 = results[0].variance, results[1].variance
    r0, r1 = results[0].rho, results[1].rho
    var_ratio = max(v0, v1) / min(v0, v1) if min(v0, v1) > 0 else float("inf")
    rho_gap = abs(r0 - r1)
    stable = (
        var_ratio < (1.0 + rel_tol) * (max(a_values) / min(a_values) + 1e-12) * 2
        and rho_gap < 0.5
        and max(r0, r1) < 0.85
    )
    return {
        "a_values": [float(a) for a in a_values],
        "indicators": [r.as_dict() for r in results],
        "variance_ratio": float(var_ratio),
        "rho_gap": float(rho_gap),
        "var_rho_stable": bool(stable),
        "note": "far from fold: λ large; Var/ρ do not show critical-slowing blow-up",
    }


__all__ = [
    "EARLY_WARNING_COUNTEREXAMPLE_FENCE",
    "SOURCE",
    "EarlyWarningIndicators",
    "ou_variance",
    "ou_autocorrelation",
    "estimate_lambda_from_ar1",
    "lambda_from_cusp_equilibrium",
    "early_warning_at_cusp",
    "control_far_from_fold",
]
