"""Crooks fluctuation theorem -- nonequilibrium work / free-energy ratios (Milestone 37).

Maps Gavin E. Crooks, Phys. Rev. E 60, 2721-2726 (1999);
DOI 10.1103/PhysRevE.60.2721; arXiv cond-mat/9901352.

    omega = beta (W - DeltaF)
    P_F(+omega) / P_R(-omega) = e^{+omega}
    <e^{-beta W}> = e^{-beta DeltaF}   (Jarzynski)

**NOT** Onsager reciprocity L_ij = L_ji and **NOT** an identification of
Onsager L_ij with Schnakenberg affinities A_ij. This module does
**not** construct Onsager matrices.

**NOT** Schnakenberg network thermodynamics (M18): no currents J_ij, no
cycle affinities A_ij, no bilinear entropy production sigma = (1/2) Sum J A.
Crooks is a trajectory / work-ensemble fluctuation theorem; Schnakenberg is
a Markov-network affinity / current identity. They are complementary, not merged.

Does **not** mutate thermo/core.py or thermo/schnakenberg.py.
No Metropolis Monte-Carlo engine; no path-integral sampler.
"""
from __future__ import annotations

from typing import Sequence

import numpy as np

from scoped_correspondence.errors import ScopeViolationError

ArrayLike = Sequence[float] | np.ndarray

SOURCE = (
    "Crooks 1999, Entropy production fluctuation theorem and the "
    "nonequilibrium work relation for free energy differences, "
    "Phys. Rev. E 60, 2721-2726; "
    "DOI 10.1103/PhysRevE.60.2721; arXiv cond-mat/9901352"
)

_ONSAGER_NOTE = (
    "NOT Onsager L_ij/A_ij: Crooks does not identify Onsager linear-response "
    "coefficients with Schnakenberg affinities."
)

_SCHNAKENBERG_NOTE = (
    "NOT Schnakenberg M18: no J_ij / A_ij / bilinear sigma; trajectory work "
    "fluctuation theorem only."
)

_DEFAULT_ASSUMPTIONS: tuple[str, ...] = (
    "canonical thermal bath at inverse temperature beta > 0",
    "forward work W and free-energy difference DeltaF = F_B - F_A",
    "omega = beta(W - DeltaF); Crooks ratio P_F(+omega)/P_R(-omega) = e^{+omega}",
    "Jarzynski: <e^{-beta W}> = e^{-beta DeltaF} (forward ensemble)",
    _ONSAGER_NOTE,
    _SCHNAKENBERG_NOTE,
    "separate from thermo/core.py (M8) and thermo/schnakenberg.py (M18)",
    "no Metropolis engine / path sampler shipped here",
)


def _as_finite_scalar(name: str, x: float) -> float:
    try:
        v = float(x)
    except (TypeError, ValueError) as exc:
        raise ScopeViolationError(f"crooks: {name} must be a real scalar") from exc
    if not np.isfinite(v):
        raise ScopeViolationError(f"crooks: {name} must be finite; got {v!r}")
    return v


def _as_beta(beta: float) -> float:
    b = _as_finite_scalar("beta", beta)
    if b <= 0.0:
        raise ScopeViolationError(f"crooks: beta must be > 0; got {b}")
    return b


def work_ratio(W: float, delta_F: float, beta: float) -> tuple[float, float]:
    """Crooks exponent omega = beta(W - DeltaF) and ratio factor e^omega.

    NOT Onsager L_ij/A_ij. NOT Schnakenberg M18.
    """
    w = _as_finite_scalar("W", W)
    df = _as_finite_scalar("delta_F", delta_F)
    b = _as_beta(beta)
    omega = b * (w - df)
    if abs(omega) > 700.0:
        raise ScopeViolationError(
            f"crooks: |omega|={abs(omega)} too large for safe exp; rescale W/DeltaF/beta"
        )
    return float(omega), float(np.exp(omega))


def verify_crooks_ratio(
    P_forward: float,
    P_reverse: float,
    W: float,
    delta_F: float,
    beta: float,
    *,
    rtol: float = 1e-9,
    atol: float = 1e-12,
) -> dict:
    """Check P_F(+omega)/P_R(-omega) ~= e^{beta(W-DeltaF)} (Crooks FT).

    NOT Onsager L_ij/A_ij. NOT Schnakenberg M18.
    """
    pf = _as_finite_scalar("P_forward", P_forward)
    pr = _as_finite_scalar("P_reverse", P_reverse)
    if pf <= 0.0 or pr <= 0.0:
        raise ScopeViolationError(
            "crooks: P_forward and P_reverse must be > 0 for a Crooks ratio"
        )
    rtol_v = _as_finite_scalar("rtol", rtol)
    atol_v = _as_finite_scalar("atol", atol)
    if rtol_v < 0.0 or atol_v < 0.0:
        raise ScopeViolationError("crooks: rtol and atol must be nonnegative")

    omega, exp_omega = work_ratio(W, delta_F, beta)
    ratio_obs = pf / pr
    abs_err = abs(ratio_obs - exp_omega)
    rel_err = abs_err / max(abs(exp_omega), 1e-300)
    ok = bool(np.isclose(ratio_obs, exp_omega, rtol=rtol_v, atol=atol_v))
    return {
        "ok": ok,
        "omega": float(omega),
        "exp_omega": float(exp_omega),
        "ratio_observed": float(ratio_obs),
        "ratio_expected": float(exp_omega),
        "abs_err": float(abs_err),
        "rel_err": float(rel_err),
        "P_forward": float(pf),
        "P_reverse": float(pr),
        "W": float(_as_finite_scalar("W", W)),
        "delta_F": float(_as_finite_scalar("delta_F", delta_F)),
        "beta": float(_as_beta(beta)),
    }


def jarzynski_estimate(work_samples: ArrayLike, beta: float) -> float:
    """Jarzynski free-energy estimate DeltaF_hat = -beta^{-1} ln <e^{-beta W}>.

    NOT Onsager L_ij/A_ij. NOT Schnakenberg M18.
    """
    b = _as_beta(beta)
    arr = np.asarray(work_samples, dtype=float).ravel()
    if arr.size < 1:
        raise ScopeViolationError("crooks: work_samples must be nonempty")
    if not np.isfinite(arr).all():
        raise ScopeViolationError("crooks: work_samples must be finite")

    w_min = float(np.min(arr))
    shifted = np.exp(-b * (arr - w_min))
    mean_shifted = float(np.mean(shifted))
    if mean_shifted <= 0.0 or not np.isfinite(mean_shifted):
        raise ScopeViolationError("crooks: exponential average collapsed")
    return float(w_min - np.log(mean_shifted) / b)


def as_report(
    W: float,
    delta_F: float,
    beta: float,
    *,
    P_forward: float | None = None,
    P_reverse: float | None = None,
    work_samples: ArrayLike | None = None,
) -> dict:
    """Bundle Crooks / Jarzynski scalars for JSON verification reports."""
    omega, exp_omega = work_ratio(W, delta_F, beta)
    out: dict = {
        "source": SOURCE,
        "assumptions": list(_DEFAULT_ASSUMPTIONS),
        "W": float(_as_finite_scalar("W", W)),
        "delta_F": float(_as_finite_scalar("delta_F", delta_F)),
        "beta": float(_as_beta(beta)),
        "omega": float(omega),
        "exp_omega": float(exp_omega),
        "onsager_note": _ONSAGER_NOTE,
        "schnakenberg_note": _SCHNAKENBERG_NOTE,
    }
    if P_forward is not None and P_reverse is not None:
        out["crooks_check"] = verify_crooks_ratio(
            P_forward, P_reverse, W, delta_F, beta
        )
    if work_samples is not None:
        out["jarzynski_delta_F_hat"] = float(
            jarzynski_estimate(work_samples, beta)
        )
    return out
