"""Map old symbol / function names from layer docs onto Milestone-2 APIs."""

from __future__ import annotations

from typing import Mapping, Optional, Sequence, Tuple

import numpy as np

from scoped_correspondence.coupling import (
    AijInfluence,
    LijTransport,
    PairwiseCoupling,
    check_generic_structure,
)
from scoped_correspondence.dynamics import (
    CubicNormalForm,
    cusp_field,
    recovery_rate_from_relaxation,
    sigmoid_response,
)
from scoped_correspondence.observation import (
    channel_capacity,
    realized_rate,
    retention,
)


# --- Observation / CREP -------------------------------------------------


def shannon_hartley_K(bandwidth: float, snr: float) -> float:
    """Legacy name for ``channel_capacity`` (information_layer_crep.md §3)."""
    return channel_capacity(bandwidth, snr)


def information_retention_R(
    mutual_information: float,
    entropy: float,
    *,
    discrete: bool = True,
) -> float:
    """Legacy name for ``retention`` (R_info)."""
    return retention(mutual_information, entropy, discrete=discrete)


def realized_eta(
    rate: float,
    capacity: float,
    *,
    rate_unit: str = "bit/time",
    capacity_unit: str = "bit/time",
) -> float:
    """Legacy name for ``realized_rate`` (eta_info / V-role instance)."""
    return realized_rate(
        rate, capacity, rate_unit=rate_unit, capacity_unit=capacity_unit
    )


# --- Dynamics / UTAC ----------------------------------------------------


def utac_sigmoid(
    u: float,
    beta_response: float,
    theta_u: float,
    p_max: float = 1.0,
) -> float:
    """Legacy static response p(u) (system_layer_utac.md §3)."""
    return sigmoid_response(u, beta_response, theta_u, p_max)


def utac_recovery_rate(tau: float) -> float:
    """Legacy S_rec = 1/tau (independent of beta_response)."""
    return recovery_rate_from_relaxation(tau)


def cusp_dxdt(x: float, a: float, b: float, tau: float = 1.0) -> float:
    """Legacy cubic RHS (system_layer_utac.md §5)."""
    return cusp_field(x, a, b, tau)


def cubic_normal_form(a: float, b: float = 0.0, tau: float = 1.0) -> CubicNormalForm:
    """Legacy constructor for the corrected cubic family."""
    return CubicNormalForm(a=a, b=b, tau=tau)


def gamma_domain_style(tau: float) -> float:
    """Illustrative M2-prompt alias: domain-style recovery from relaxation time.

    Historically some packages used a Gamma-like label near recovery; this
    adapter only forwards to ``recovery_rate_from_relaxation`` and does not
    redefine science.
    """
    return recovery_rate_from_relaxation(tau)


# --- Coupling / AFET ----------------------------------------------------


def afet_pairwise_coupling(
    f: Mapping,
    g: Optional[Mapping] = None,
    names: Sequence[str] = (),
) -> PairwiseCoupling:
    """Legacy name for ``PairwiseCoupling`` (coupling_layer_afet.md §2)."""
    return PairwiseCoupling(f=f, g=g or {}, names=names)


def influence_A(matrix, state_names: Tuple[str, ...] = ()) -> AijInfluence:
    """Legacy A_ij influence matrix (no shared base with L)."""
    return AijInfluence(matrix=np.asarray(matrix, dtype=float), state_names=state_names)


def onsager_L(matrix, force_names: Tuple[str, ...] = ()) -> LijTransport:
    """Legacy L_ij transport matrix (no shared base with A)."""
    return LijTransport(matrix=np.asarray(matrix, dtype=float), force_names=force_names)


def generic_structure_check(J, M, grad_E, grad_S, *, tol: float = 1e-10) -> dict:
    """Legacy name for ``check_generic_structure`` (structure only)."""
    return check_generic_structure(J, M, grad_E, grad_S, tol=tol)


__all__ = [
    "afet_pairwise_coupling",
    "cubic_normal_form",
    "cusp_dxdt",
    "gamma_domain_style",
    "generic_structure_check",
    "influence_A",
    "information_retention_R",
    "onsager_L",
    "realized_eta",
    "shannon_hartley_K",
    "utac_recovery_rate",
    "utac_sigmoid",
]
