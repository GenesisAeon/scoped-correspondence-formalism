"""Crooks fluctuation theorem -- nonequilibrium work / free-energy ratios (Milestone 37).

Maps Gavin E. Crooks, Entropy production fluctuation theorem and the
nonequilibrium work relation for free energy differences,
Phys. Rev. E 60, 2721–2726 (1999);
DOI 10.1103/PhysRevE.60.2721; arXiv cond-mat/9901352.

For a forward protocol with work ``W`` and free-energy difference
``ΔF = F_B - F_A``, and inverse temperature ``β = 1/(k_B T)``:

    ω = β (W - ΔF)
    P_F(+ω) / P_R(-ω) = e^{+ω}
    ⟨ e^{-β W} ⟩ = e^{-β ΔF}          (Jarzynski equality)

``work_ratio`` returns ``(ω, e^ω)``. ``verify_crooks_ratio`` checks the
histogram / density ratio against ``e^ω``. ``jarzynski_estimate`` recovers
``ΔF`` from forward work samples via the exponential average.

**NOT** Onsager reciprocity ``L_ij = L_ji`` and **NOT** an identification of
Onsager ``L_ij`` with Schnakenberg affinities ``A_ij``. This module does
**not** construct Onsager matrices.

**NOT** Schnakenberg network thermodynamics (M18): no currents ``J_ij``, no
cycle affinities ``A_ij``, no bilinear entropy production
``σ = (1/2) Σ J A``. Crooks is a trajectory / work-ensemble fluctuation
theorem; Schnakenberg is a Markov-network affinity / current identity.
They are complementary, not merged.

Does **not** mutate ``thermo/core.py`` or ``thermo/schnakenberg.py``.
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
    "Phys. Rev. E 60, 2721–2726; "
    "DOI 10.1103/PhysRevE.60.2721; arXiv cond-mat/9901352"
)

_ONSAGER_NOTE = (
    "NOT Onsager L_ij/A_ij: Crooks does not identify Onsager linear-response "
    "coefficients with Schnakenberg affinities."
)

_SCHNAKENBERG_NOTE = (
    "NOT Schnakenberg M18: no J_ij / A_ij / bilinear σ; trajectory work "
    "fluctuation theorem only."
)

_DEFAULT_ASSUMPTIONS: tuple[str, ...] = (
    "canonical thermal bath at inverse temperature β > 0",
    "forward work W and free-energy difference ΔF = F_B - F_A (same energy units)",
    "ω = β(W - ΔF); Crooks ratio P_F(+ω)/P_R(-ω) = e^{+ω}",
    "Jarzynski: ⟨e^{-β W}⟩ = e^{-β ΔF} (forward ensemble)",
    _ONSAGER_NOTE,
    _SCHNAKENBERG_NOTE,
    "separate from thermo/core.py (M8 GENERIC) and thermo/schnakenberg.py (M18)",
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


def work_ratio(
    W: float,
    delta_F: float,
    beta: float,
) -> tuple[float, float]:
    """Crooks exponent ``ω = β(W - ΔF)`` and ratio factor ``e^ω``.

    Parameters
    ----------
    W :
        Forward-protocol work (same units as ``delta_F``).
    delta_F :
        Free-energy difference ``ΔF = F_B - F_A``.
    beta :
        Inverse temperature ``β = 1/(k_B T)``; must be ``> 0``.

    Returns
    -------
    omega, exp_omega : float, float
        ``ω = β(W - ΔF)`` and ``e^ω`` (the Crooks forward/reverse density ratio).

    Notes
    -----
    Control: ``W == ΔF`` ⇒ ``ω = 0``, ``e^ω = 1``.
    Mini-example: ``β=1``, ``ΔF=0``, ``W=1`` ⇒ ``ω=1``, ``e^ω = e ≈ 2.718281828``.

    NOT Onsager ``L_ij``/``A_ij``. NOT Schnakenberg M18.
    """
    w = _as_finite_scalar("W", W)
    df = _as_finite_scalar("delta_F", delta_F)
    b = _as_beta(beta)
    omega = b * (w - df)
    # Guard overflow on extreme ω; still finite for the hand-checkable examples.
    if abs(omega) > 700.0:
        raise ScopeViolationError(
            f"crooks: |ω|={abs(omega)} too large for safe exp; rescale W/ΔF/β"
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
    """Check ``P_F(+ω) / P_R(-ω) ≈ e^{β(W-ΔF)}`` (Crooks FT).

    Parameters
    ----------
    P_forward :
        Forward-process density / probability mass at work ``+W``
        (or at entropy production ``+ω``); must be ``> 0``.
    P_reverse :
        Reverse-process density / probability mass at work ``-W``
        (or at ``-ω``); must be ``> 0``.
    W, delta_F, beta :
        Same convention as :func:`work_ratio`.
    rtol, atol :
        Relative / absolute tolerances for ``math.isclose``-style comparison
        of the observed ratio against ``e^ω``.

    Returns
    -------
    report : dict
        Keys include ``ok``, ``omega``, ``exp_omega``, ``ratio_observed``,
        ``ratio_expected``, ``abs_err``, ``rel_err``.

    Raises
    ------
    ScopeViolationError
        On non-positive densities, non-finite inputs, or ``β ≤ 0``.

    Notes
    -----
    NOT Onsager ``L_ij``/``A_ij``. NOT Schnakenberg M18.
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
    """Jarzynski free-energy estimate ``ΔF̂ = -β⁻¹ ln ⟨e^{-β W}⟩``.

    Parameters
    ----------
    work_samples :
        1-D array of forward-protocol work values.
    beta :
        Inverse temperature ``β > 0``.

    Returns
    -------
    delta_F_hat : float
        Estimated free-energy difference.

    Notes
    -----
    Numerically stable log-mean-exp:
    ``ΔF̂ = -β⁻¹ ( m + ln mean(e^{-β(W-m/β wait)}) )`` with
    ``m = min(β W)`` shift, i.e. ``ΔF̂ = min(W) - β⁻¹ ln mean(e^{-β(W-min W)})``
    when all samples share the same ``β``.

    Gaussian toy: if ``W ∼ N(ΔF + σ² β / 2, σ²)``, the infinite-sample
    Jarzynski average recovers ``ΔF`` exactly.

    NOT Onsager ``L_ij``/``A_ij``. NOT Schnakenberg M18.
    """
    b = _as_beta(beta)
    arr = np.asarray(work_samples, dtype=float).ravel()
    if arr.size < 1:
        raise ScopeViolationError("crooks: work_samples must be nonempty")
    if not np.isfinite(arr).all():
        raise ScopeViolationError("crooks: work_samples must be finite")

    # Stable: ⟨e^{-βW}⟩ = e^{-β W_min} ⟨e^{-β(W-W_min)}⟩
    w_min = float(np.min(arr))
    shifted = np.exp(-b * (arr - w_min))
    mean_shifted = float(np.mean(shifted))
    if mean_shifted <= 0.0 or not np.isfinite(mean_shifted):
        raise ScopeViolationError("crooks: exponential average collapsed")
    # ΔF̂ = -β⁻¹ ln ⟨e^{-βW}⟩ = W_min - β⁻¹ ln mean_shifted
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
