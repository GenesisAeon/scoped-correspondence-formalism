"""Chapman–Enskog / BGK transport coefficients as a kinetic closure defect (M40).

Implements the **BGK route** to first-order Chapman–Enskog hydrodynamics:
given pressure ``p`` and BGK relaxation time ``τ``, the Newtonian shear
viscosity and Fourier heat conductivity are

    μ = p · τ
    κ = (5/2) · (k_B / m) · p · τ

(Bhatnagar–Gross–Krook 1954; monatomic ideal gas). The BGK Prandtl number
is exactly ``Pr = μ c_p / κ = 1`` when ``c_p = (5/2)(k_B/m)``, whereas the
physical monatomic value is ``Pr = 2/3`` — a known BGK defect (factor 3/2),
addressed e.g. by Holway's ES-BGK model (1966).

**Structural analogy (NOT identity).** Mapping kinetic → macro moments and
closing the stress/heat flux is the same *pattern* as
``is_exact_closure`` / ``closure_error`` (``PC ≈ CQ``, defect ``δ_cl``): the
micro operator is the Boltzmann/BGK collision operator, the projection is
onto hydrodynamic moments ``(ρ, u, T)``, and the macro generator is
Euler/Navier–Stokes. This is a **structural analogy** only — it is **not**
identity with M11 generator lumpability nor with M21 Michel–Siegle reduction
error bounds. This module does **not** edit ``closure/core.py`` or
``closure/error_bounds.py``, and does **not** implement the Chapman–Cowling
hard-sphere viscosity formula.

Sources
-------
* P. L. Bhatnagar, E. P. Gross, M. Krook, *A Model for Collision Processes
  in Gases. I.*, Phys. Rev. **94**, 511–525 (1954).
  DOI 10.1103/PhysRev.94.511
* L. H. Holway, Jr., *New Statistical Models for Kinetic Theory: Methods of
  Construction*, Phys. Fluids **9**, 1658–1673 (1966).
  DOI 10.1063/1.1761920
"""

from __future__ import annotations

from typing import Tuple, Union

from scoped_correspondence.errors import ScopeViolationError

Number = Union[int, float]

SOURCE = (
    "BGK 1954 Phys. Rev. 94, 511 (DOI 10.1103/PhysRev.94.511); "
    "Holway 1966 Phys. Fluids 9, 1658 (DOI 10.1063/1.1761920); "
    "BGK first-order Chapman–Enskog: μ=p·τ, κ=(5/2)(k_B/m)·p·τ, Pr_BGK=1"
)

# Known BGK Prandtl defect vs physical monatomic gas
PR_BGK = 1.0
PR_MONATOMIC_PHYSICAL = 2.0 / 3.0
PR_BGK_OVER_PHYSICAL = 1.5  # 1 / (2/3) = 3/2


def _finite_nonneg(name: str, x: Number, *, allow_zero: bool = True) -> float:
    try:
        v = float(x)
    except (TypeError, ValueError) as exc:
        raise ScopeViolationError(f"{name} must be a real number; got {x!r}") from exc
    if not (v == v) or v in (float("inf"), float("-inf")):  # NaN / inf
        raise ScopeViolationError(f"{name} must be finite; got {x!r}")
    if allow_zero:
        if v < 0.0:
            raise ScopeViolationError(f"{name} must be >= 0; got {x!r}")
    else:
        if v <= 0.0:
            raise ScopeViolationError(f"{name} must be > 0; got {x!r}")
    return v


def bgk_transport_coefficients(
    p: Number,
    tau: Number,
    m: Number,
    k_B: Number = 1.0,
) -> Tuple[float, float]:
    """BGK first-order Chapman–Enskog transport coefficients ``(μ, κ)``.

    Parameters
    ----------
    p :
        Pressure (same units as desired viscosity·1/time).
    tau :
        BGK relaxation time ``τ ≥ 0``. The hydrodynamic (exact-closure)
        control is ``τ → 0`` ⇒ ``μ, κ → 0``.
    m :
        Particle mass ``m > 0``.
    k_B :
        Boltzmann constant (default ``1`` in natural units).

    Returns
    -------
    mu, kappa :
        Shear viscosity ``μ = p · τ`` and heat conductivity
        ``κ = (5/2) · (k_B / m) · p · τ``.

    Notes
    -----
    Structural analogy to ``is_exact_closure`` / ``closure_error`` only —
    not identity with M11 lumpability or M21 error bounds. Does **not** use
    the Chapman–Cowling hard-sphere ``η`` formula.
    """
    p_v = _finite_nonneg("p", p, allow_zero=True)
    tau_v = _finite_nonneg("tau", tau, allow_zero=True)
    m_v = _finite_nonneg("m", m, allow_zero=False)
    k_v = _finite_nonneg("k_B", k_B, allow_zero=False)

    mu = p_v * tau_v
    kappa = (5.0 / 2.0) * (k_v / m_v) * p_v * tau_v
    return float(mu), float(kappa)


def prandtl_number(mu: Number, kappa: Number, c_p: Number) -> float:
    """Prandtl number ``Pr = μ · c_p / κ``.

    For BGK with monatomic ``c_p = (5/2)(k_B/m)``, the identity
    ``κ = c_p · μ`` implies ``Pr = 1`` exactly (BGK defect vs physical
    monatomic ``Pr = 2/3``; ratio ``3/2`` — see Holway 1966).
    """
    mu_v = _finite_nonneg("mu", mu, allow_zero=True)
    kappa_v = _finite_nonneg("kappa", kappa, allow_zero=False)
    c_p_v = _finite_nonneg("c_p", c_p, allow_zero=False)
    return float(mu_v * c_p_v / kappa_v)


def relaxation_time_from_viscosity(mu: Number, p: Number) -> float:
    """Invert ``μ = p · τ`` → ``τ = μ / p`` (BGK / first CE).

    Parameters
    ----------
    mu :
        Shear viscosity ``μ ≥ 0``.
    p :
        Pressure ``p > 0``.
    """
    mu_v = _finite_nonneg("mu", mu, allow_zero=True)
    p_v = _finite_nonneg("p", p, allow_zero=False)
    return float(mu_v / p_v)


def mean_thermal_speed(T: Number, m: Number, k_B: Number = 1.0) -> float:
    """Maxwell mean speed ``⟨v⟩ = sqrt(8 k_B T / (π m))`` (order-of-magnitude).

    Used only for mean-free-path sanity estimates ``λ ~ ⟨v⟩ · τ``; not part of
    the BGK transport closure itself.
    """
    import math

    T_v = _finite_nonneg("T", T, allow_zero=False)
    m_v = _finite_nonneg("m", m, allow_zero=False)
    k_v = _finite_nonneg("k_B", k_B, allow_zero=False)
    return float(math.sqrt(8.0 * k_v * T_v / (math.pi * m_v)))


def mean_free_path_estimate(mean_speed: Number, tau: Number) -> float:
    """Order-of-magnitude mean free path ``λ ≈ ⟨v⟩ · τ``."""
    v = _finite_nonneg("mean_speed", mean_speed, allow_zero=True)
    tau_v = _finite_nonneg("tau", tau, allow_zero=True)
    return float(v * tau_v)


__all__ = [
    "PR_BGK",
    "PR_BGK_OVER_PHYSICAL",
    "PR_MONATOMIC_PHYSICAL",
    "SOURCE",
    "bgk_transport_coefficients",
    "mean_free_path_estimate",
    "mean_thermal_speed",
    "prandtl_number",
    "relaxation_time_from_viscosity",
]
