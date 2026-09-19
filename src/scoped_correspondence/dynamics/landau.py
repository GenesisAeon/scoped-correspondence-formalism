"""Landau mean-field order-parameter scaling vs exact 2-D Ising (Milestone 29).

Self-falsification check for the corrected cubic normal form
``τ ẋ = -x³ + a x + b`` (``dynamics.core``; FORMALISM.md §5, Guckenheimer &
Holmes 1983). For ``b = 0`` and supercritical ``a > 0`` the stable branches
are the positive / negative roots of ``x³ - a x = 0``, i.e. ``x* = ±√a``.
The mean-field order-parameter exponent is therefore ``β_MF = 1/2``.

This module **calls** ``fixed_points(a, b=0)`` only; it does **not** duplicate
the ``√a`` formula and does **not** edit ``dynamics/core.py``.

Comparison to the exact 2-D Ising exponent ``β = 1/8`` (Yang 1952) is a
**hypothetical counterfactual** used for self-falsification: the cubic is a
mean-field / Landau normal form, so its observed ratios must match
``(a_i/a_j)^{1/2}``, not ``(a_i/a_j)^{1/8}``. The discrepancy factor
``2^{1/2 - 1/8} = 2^{3/8} ≈ 1.6818`` (for a four-fold change in ``a``) is
expected and documents that ``β_crit`` is **model-specific, not universal**
(FORMALISM.md §12).

Sources (do **not** cite Landau 1937):
  - Onsager 1944, Phys. Rev. 65, 117; DOI 10.1103/PhysRev.65.117
    (exact 2-D Ising critical temperature / critical ratio
    ``T_c / J = 2 / ln(1+√2) ≈ 2.269185314213022``).
  - Yang 1952, Phys. Rev. 85, 808; DOI 10.1103/PhysRev.85.808
    (exact spontaneous magnetization → ``β = 1/8``).
  - Guckenheimer & Holmes 1983, Nonlinear Oscillations…;
    DOI 10.1007/978-1-4612-1140-2 (normal-form / bifurcation context).

Out of scope for M29: spatial gradients, RG derivation of ``β = 1/8``,
links to thermo / closure, and any mutation of FORMALISM.md.
"""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from typing import Any, Dict

from scoped_correspondence.dynamics.core import fixed_points
from scoped_correspondence.errors import ScopeViolationError

MEAN_FIELD_BETA: float = 0.5
ISING_2D_BETA: float = 0.125  # Yang 1952, DOI 10.1103/PhysRev.85.808

# Verbatim mandatory warning — must appear in onsager_critical_ratio docstring
# AND as a text field in the verification JSON report.
ONSAGER_SIGMA_WARNING: str = (
    "WARNING: Onsager critical ratio ≈2.269185314213022 is accidentally "
    "near the discarded ecosystem σ≈2.2; this is coincidence only — "
    "do not identify them."
)

SOURCE = (
    "Onsager 1944 DOI 10.1103/PhysRev.65.117; "
    "Yang 1952 DOI 10.1103/PhysRev.85.808; "
    "Guckenheimer & Holmes 1983 DOI 10.1007/978-1-4612-1140-2"
)

_SCOPE_NOTES: tuple[str, ...] = (
    "mean-field β=1/2 from fixed_points(a,b=0) positive root (CALL only; "
    "no duplicate √a formula; dynamics/core.py not edited)",
    "ISING_2D_BETA=1/8 is a hypothetical counterfactual (Yang 1952), "
    "not claimed for the cubic normal form",
    "β_crit is model-specific, not universal (FORMALISM.md §12)",
    "no spatial gradient; no RG derivation of β=1/8; no thermo/closure link",
    "Onsager T_c/J must not be identified with discarded ecosystem σ≈2.2",
)


def mean_field_order_parameter(a: float) -> float:
    """Positive mean-field order parameter ``x* = √a`` via ``fixed_points``.

    For supercritical ``a > 0`` and ``b = 0``, ``fixed_points(a, 0)`` returns
    the three real roots ``[-√a, 0, +√a]`` (up to float noise at the origin).
    This function returns the **positive** root and does **not** re-derive
    ``√a`` independently.

    Parameters
    ----------
    a :
        Supercritical linear coefficient (``a > 0``).

    Returns
    -------
    float
        Positive equilibrium from ``fixed_points(a, b=0)``.

    Raises
    ------
    ScopeViolationError
        If ``a ≤ 0`` (no positive ordered branch for ``b = 0``).
    """
    aa = float(a)
    if aa <= 0.0:
        raise ScopeViolationError(
            f"mean_field_order_parameter: requires a > 0 (supercritical); got {a!r}"
        )
    roots = fixed_points(aa, 0.0)
    positive = [float(r) for r in roots if float(r) > 1e-12]
    if not positive:
        raise ScopeViolationError(
            f"mean_field_order_parameter: fixed_points({aa!r}, 0) returned no "
            f"positive root; got {roots!r}"
        )
    return max(positive)


def onsager_critical_ratio() -> float:
    """Exact 2-D Ising critical ratio ``T_c / J = 2 / ln(1+√2)`` (Onsager 1944).

    Returns
    -------
    float
        ``2 / ln(1 + √2) ≈ 2.269185314213022``.

    WARNING: Onsager critical ratio ≈2.269185314213022 is accidentally near the discarded ecosystem σ≈2.2; this is coincidence only — do not identify them.
    """
    return float(2.0 / math.log(1.0 + math.sqrt(2.0)))


@dataclass(frozen=True)
class ScalingExponentComparison:
    """Order-parameter ratio comparison for self-falsification (M29).

    ``actual_ratio`` is ``x*(a1) / x*(a2)`` from ``fixed_points``.
    Mean-field prediction: ``(a1/a2)^{MEAN_FIELD_BETA}`` (``β = 1/2``).
    Hypothetical Ising prediction: ``(a1/a2)^{ISING_2D_BETA}`` (``β = 1/8``).

    Note: writing the scaling for the reciprocal order-parameter ratio gives
    ``x*(a2)/x*(a1) = (a2/a1)^β``; this report uses the ``> 1`` direction
    ``x*(a1)/x*(a2) = (a1/a2)^β`` so that the worked example
    ``a1=0.25, a2=0.0625`` yields ratio ``2.0`` (exact MF) and Ising
    hypothetical ``≈ 1.189``.
    """

    a1: float
    a2: float
    x_star_a1: float
    x_star_a2: float
    actual_ratio: float
    mean_field_ratio: float
    ising_hypothetical_ratio: float
    discrepancy_factor_mf_over_ising: float
    mean_field_beta: float
    ising_2d_beta: float
    matches_mean_field: bool
    beta_crit_note: str
    source: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def compare_scaling_exponents(a1: float, a2: float) -> ScalingExponentComparison:
    """Compare actual ``x*`` ratio to mean-field and hypothetical Ising scaling.

    Parameters
    ----------
    a1, a2 :
        Supercritical coefficients (``a > 0``). Order-parameter ratio is
        reported as ``x*(a1) / x*(a2)``.

    Returns
    -------
    ScalingExponentComparison
        Actual ratio from ``fixed_points``, mean-field ``(a1/a2)^{0.5}``,
        hypothetical Ising ``(a1/a2)^{0.125}``, and discrepancy factor
        ``MF / Ising``. When ``a1 == a2`` all ratios are ``1.0``.

    Notes
    -----
    The cubic is mean-field: agreement with ``β = 1/2`` and disagreement
    with ``β = 1/8`` is the intended self-falsification outcome.
    ``β_crit`` is model-specific, not universal (FORMALISM.md §12).
    """
    aa1 = float(a1)
    aa2 = float(a2)
    if aa1 <= 0.0 or aa2 <= 0.0:
        raise ScopeViolationError(
            f"compare_scaling_exponents: requires a1 > 0 and a2 > 0; "
            f"got a1={a1!r}, a2={a2!r}"
        )

    x1 = mean_field_order_parameter(aa1)
    x2 = mean_field_order_parameter(aa2)
    actual = float(x1 / x2)
    a_ratio = aa1 / aa2
    mf = float(a_ratio ** MEAN_FIELD_BETA)
    ising = float(a_ratio ** ISING_2D_BETA)
    factor = float(mf / ising) if ising != 0.0 else float("inf")
    matches = math.isclose(actual, mf, rel_tol=1e-9, abs_tol=1e-12)

    return ScalingExponentComparison(
        a1=aa1,
        a2=aa2,
        x_star_a1=x1,
        x_star_a2=x2,
        actual_ratio=actual,
        mean_field_ratio=mf,
        ising_hypothetical_ratio=ising,
        discrepancy_factor_mf_over_ising=factor,
        mean_field_beta=MEAN_FIELD_BETA,
        ising_2d_beta=ISING_2D_BETA,
        matches_mean_field=matches,
        beta_crit_note=(
            "beta_crit is model-specific, not universal (FORMALISM.md §12)"
        ),
        source=SOURCE,
    )


__all__ = [
    "MEAN_FIELD_BETA",
    "ISING_2D_BETA",
    "ONSAGER_SIGMA_WARNING",
    "SOURCE",
    "ScalingExponentComparison",
    "mean_field_order_parameter",
    "onsager_critical_ratio",
    "compare_scaling_exponents",
]
