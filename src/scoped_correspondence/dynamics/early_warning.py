"""Early-warning signals / critical slowing down (Milestone 36).

Linearize the corrected cubic normal form (``dynamics.core``) at a stable
equilibrium and add additive noise: ``dX = -λ(X - x*) dt + σ dW``. The
stationary Ornstein-Uhlenbeck statistics are exact:

    Var(X)                = σ² / (2λ)
    Corr(X_t, X_{t+Δt})   = exp(-λ Δt)

As a fold bifurcation is approached (λ → 0⁺): Var → ∞, autocorrelation → 1.

This module **calls** ``dynamics.core.recovery_rate_at_equilibrium`` for λ
(it does **not** re-derive ``S_rec`` independently, and does **not** edit
``dynamics/core.py``). It is a pure translation of an existing quantity into
observable statistics — no new modelling assumption.

Explicitly independent of M14 (contraction), M29 (Landau), M33 (Fenichel/
GSPT), M34 (Floquet), and M35 (Panarchy/cusp): four separate `dynamics`
extensions computed from four different objects. `β_response` is NEVER
identified with `S_rec`, `Var`, or the autocorrelation here (FORMALISM.md
§2 / "Independence of beta_response" — unchanged).

Out of scope: any real-data estimator pipeline (window sizes, trend tests)
— that is `identifiability`/`validation` territory and is deliberately not
built here. This module stays on the Verification side (model computation),
never Validation (real-data testing), per the repo's VAL-SPLIT discipline.

Sources:
  - Scheffer, M. et al. (2009). Early-warning signals for critical
    transitions. Nature 461, 53-59. DOI 10.1038/nature08227.
  - **Mandatory counter-examples** (must accompany any use of this module):
    Boettiger, C. & Hastings, A. (2012). Quantifying limits to detection of
    early warning for critical transitions. J. R. Soc. Interface 9(75),
    2527-2539. DOI 10.1098/rsif.2012.0125 — quantifies false positive/
    negative rates at realistic sample sizes.
    Ditlevsen, P. D. & Johnsen, S. J. (2010). Tipping points: Early warning
    and wishful thinking. Geophys. Res. Lett. 37(19). DOI
    10.1029/2010GL044486 — the Dansgaard-Oeschger events are noise-induced,
    not bifurcation-induced: rising variance/autocorrelation is NECESSARY
    near λ→0 but NOT SUFFICIENT evidence of an approaching bifurcation.
"""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from typing import Any, Dict

from scoped_correspondence.dynamics.core import recovery_rate_at_equilibrium
from scoped_correspondence.errors import ScopeViolationError

SOURCE = "Scheffer et al. 2009 DOI 10.1038/nature08227"

COUNTEREXAMPLE_WARNING: str = (
    "MANDATORY COUNTEREXAMPLE: rising variance/autocorrelation as lambda->0 "
    "is NECESSARY but NOT SUFFICIENT evidence of an approaching bifurcation. "
    "Boettiger & Hastings 2012 (DOI 10.1098/rsif.2012.0125) quantify false "
    "positive/negative rates at realistic sample sizes; Ditlevsen & Johnsen "
    "2010 (DOI 10.1029/2010GL044486) show the Dansgaard-Oeschger events are "
    "noise-induced, not bifurcation-induced -- the signal can be present "
    "with no approaching bifurcation at all."
)

_SCOPE_NOTES: tuple[str, ...] = (
    "lambda comes from dynamics.core.recovery_rate_at_equilibrium (CALL "
    "only; no independent re-derivation; dynamics/core.py not edited)",
    "no real-data estimator pipeline (window sizes, trend tests) -- "
    "identifiability/validation territory, not built here",
    "beta_response is never identified with S_rec, Var, or autocorrelation "
    "(FORMALISM.md §2, Independence of beta_response)",
    "independent of M14 contraction, M29 Landau, M33 Fenichel/GSPT, "
    "M34 Floquet, M35 Panarchy/cusp -- four separate dynamics extensions",
)


def ou_variance(sigma: float, lam: float) -> float:
    """Stationary Ornstein-Uhlenbeck variance ``Var = σ² / (2λ)``.

    Parameters
    ----------
    sigma :
        Noise amplitude (``σ > 0``, or ``σ == 0`` degenerate case allowed).
    lam :
        Recovery rate ``λ`` (must be ``> 0`` — a stable equilibrium).

    Raises
    ------
    ScopeViolationError
        If ``lam <= 0`` (variance diverges or is undefined for an unstable
        or marginal equilibrium).
    """
    if lam <= 0.0:
        raise ScopeViolationError(
            f"ou_variance: requires lambda > 0 (stable equilibrium); got {lam!r}"
        )
    if sigma < 0.0:
        raise ScopeViolationError(f"ou_variance: sigma must be >= 0; got {sigma!r}")
    return float((sigma * sigma) / (2.0 * lam))


def ou_autocorrelation(lam: float, delta_t: float) -> float:
    """Lag-``Δt`` autocorrelation ``ρ = exp(-λ·Δt)`` of the stationary OU process.

    Raises
    ------
    ScopeViolationError
        If ``lam <= 0`` or ``delta_t < 0``.
    """
    if lam <= 0.0:
        raise ScopeViolationError(
            f"ou_autocorrelation: requires lambda > 0; got {lam!r}"
        )
    if delta_t < 0.0:
        raise ScopeViolationError(
            f"ou_autocorrelation: delta_t must be >= 0; got {delta_t!r}"
        )
    return float(math.exp(-lam * delta_t))


def estimate_lambda_from_ar1(rho: float, delta_t: float) -> float:
    """Inverse of ``ou_autocorrelation``: ``λ̂ = -ln(ρ)/Δt``.

    Parameters
    ----------
    rho :
        Observed lag-1 autocorrelation, ``0 < ρ < 1``.
    delta_t :
        Sampling interval (``> 0``).

    Raises
    ------
    ScopeViolationError
        If ``rho`` is not in ``(0, 1)`` or ``delta_t <= 0``.
    """
    if not (0.0 < rho < 1.0):
        raise ScopeViolationError(
            f"estimate_lambda_from_ar1: requires 0 < rho < 1; got {rho!r}"
        )
    if delta_t <= 0.0:
        raise ScopeViolationError(
            f"estimate_lambda_from_ar1: delta_t must be > 0; got {delta_t!r}"
        )
    return float(-math.log(rho) / delta_t)


@dataclass(frozen=True)
class EarlyWarningReport:
    """OU early-warning statistics at a cusp equilibrium (M36).

    ``lam`` is obtained by calling ``recovery_rate_at_equilibrium`` on the
    given cusp equilibrium ``x`` — never re-derived independently.
    """

    a: float
    b: float
    tau: float
    x_star: float
    lam: float
    sigma: float
    delta_t: float
    variance: float
    autocorrelation: float
    lambda_hat_from_ar1: float
    source: str
    counterexample_warning: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def early_warning_at_cusp_branch(
    a: float,
    x_star: float,
    sigma: float,
    delta_t: float,
    *,
    b: float = 0.0,
    tau: float = 1.0,
) -> EarlyWarningReport:
    """Early-warning statistics at a given cusp equilibrium ``x_star``.

    Calls ``recovery_rate_at_equilibrium(x_star, a, tau, b)`` for ``λ``
    (CALL only), then derives ``Var``, autocorrelation, and the inverse
    estimate ``λ̂`` from that same ``λ`` — a self-consistency chain, not an
    independent computation.

    Raises
    ------
    ScopeViolationError
        If the resulting ``λ`` is not ``> 0`` (i.e. ``x_star`` is not on a
        stable branch) — propagated from ``ou_variance``/``ou_autocorrelation``.
    """
    lam = recovery_rate_at_equilibrium(x_star, a, tau, b)
    var = ou_variance(sigma, lam)
    rho = ou_autocorrelation(lam, delta_t)
    lam_hat = estimate_lambda_from_ar1(rho, delta_t) if 0.0 < rho < 1.0 else float("nan")
    return EarlyWarningReport(
        a=float(a),
        b=float(b),
        tau=float(tau),
        x_star=float(x_star),
        lam=float(lam),
        sigma=float(sigma),
        delta_t=float(delta_t),
        variance=var,
        autocorrelation=rho,
        lambda_hat_from_ar1=lam_hat,
        source=SOURCE,
        counterexample_warning=COUNTEREXAMPLE_WARNING,
    )


__all__ = [
    "SOURCE",
    "COUNTEREXAMPLE_WARNING",
    "EarlyWarningReport",
    "ou_variance",
    "ou_autocorrelation",
    "estimate_lambda_from_ar1",
    "early_warning_at_cusp_branch",
]
