"""One-phase Stefan / Neumann free-boundary similarity solution (Milestone 31).

NEW Baustein ``free_boundary`` — **not** a viability subclass.

``viability/core.py`` (and M28 Nagumo / M16 CBF) treat a safe set ``K`` as
**fixed** a priori. In the classical one-phase Stefan problem the phase
boundary ``s(t)`` is itself a **dynamic variable** with its own motion law
(latent-heat flux balance at the front), not a fixed constraint set against
which trajectories are checked. Hence this is a separate package — not a
viability extension.

Sources (exclude the classical Stefan paper and the Rubinstein
monograph — no reliably verified DOI for those in the M31 research round):

  - V. A. Kot, "Solution of the Classical Stefan Problem: Neumann Condition",
    Journal of Engineering Physics and Thermophysics 90(4), 889–917 (2017),
    DOI 10.1007/s10891-017-1638-2.
  - J. Bollati, M. F. Natale, J. A. Semitiel & D. A. Tarzia,
    "Approximate solutions to the one-phase Stefan problem with non-linear
    temperature-dependent thermal conductivity", arXiv:1906.08601
    (exact transcendental form
    ``λ·exp(λ²)·erf(λ) = Ste/√π`` for ``λ > 0``).

Scope: 1-D one-phase Neumann similarity solution only. No two-phase PDE
solver; no mutation of ``viability/`` or package-root ``__init__.py``.
"""

from __future__ import annotations

import math
from typing import Any, Dict, Mapping, Union

from scoped_correspondence.errors import ScopeViolationError

SOURCE = (
    "Kot 2017 DOI 10.1007/s10891-017-1638-2; "
    "Bollati et al. arXiv:1906.08601"
)

_SCOPE_NOTES: tuple[str, ...] = (
    "NOT a viability subclass: boundary s(t) is a dynamic variable with its "
    "own motion law, not a fixed set K to check against",
    "1-D one-phase Neumann similarity solution only — no two-phase PDE",
    "transcendental root via bracketed bisection (no bare Newton)",
    "temperature_profile defined only on the liquid region 0 <= x <= s(t)",
    "sources: Kot 2017 + Bollati et al. arXiv:1906.08601 only "
    "(classical Stefan paper / Rubinstein monograph excluded)",
)

Number = Union[int, float]


def stefan_number(c: Number, T0: Number, L: Number) -> float:
    """Stefan number ``Ste = c · T0 / L``.

    Parameters
    ----------
    c :
        Specific heat capacity (same temperature units as ``T0``).
    T0 :
        Driving temperature difference (surface vs melting point).
    L :
        Latent heat of fusion (same energy units as ``c·T0``).

    Returns
    -------
    float
        ``Ste = c*T0/L``. Must be positive for ``neumann_lambda``.

    Raises
    ------
    ScopeViolationError
        If ``L`` is zero / non-finite, or inputs are non-finite.
    """
    c_f = float(c)
    T0_f = float(T0)
    L_f = float(L)
    if not math.isfinite(c_f) or not math.isfinite(T0_f) or not math.isfinite(L_f):
        raise ScopeViolationError(
            f"c, T0, L must be finite; got c={c!r}, T0={T0!r}, L={L!r}"
        )
    if L_f == 0.0:
        raise ScopeViolationError("L (latent heat) must be nonzero")
    return c_f * T0_f / L_f


def _neumann_lhs(lam: float) -> float:
    """Left-hand side ``λ · exp(λ²) · erf(λ)`` (Bollati et al. arXiv:1906.08601)."""
    return lam * math.exp(lam * lam) * math.erf(lam)


def _neumann_f(lam: float, ste: float) -> float:
    """``f(λ) = λ·exp(λ²)·erf(λ) - Ste/√π``; root at ``f(λ*) = 0``."""
    return _neumann_lhs(lam) - ste / math.sqrt(math.pi)


def neumann_lambda(Ste: Number, tol: float = 1e-12) -> Dict[str, Any]:
    """Solve ``λ·exp(λ²)·erf(λ) = Ste/√π`` for ``λ > 0`` by bisection.

    Bracketed bisection only (robust; no bare Newton without a bracket).
    The transcendental equation is the exact one-phase Neumann root as
    stated in Bollati et al. arXiv:1906.08601 (and classical Neumann /
    Kot 2017 context).

    Parameters
    ----------
    Ste :
        Stefan number ``c·T0/L``; must be ``> 0``.
    tol :
        Absolute half-width tolerance on the ``λ`` bracket (default ``1e-12``).

    Returns
    -------
    dict
        ``{"lambda": λ, "iterations": n, "residual": |f(λ)|}`` where
        ``f(λ) = λ·exp(λ²)·erf(λ) - Ste/√π``.

    Raises
    ------
    ScopeViolationError
        If ``Ste <= 0`` or non-finite, or ``tol`` is invalid.
    """
    ste = float(Ste)
    tol_f = float(tol)
    if not math.isfinite(ste):
        raise ScopeViolationError(f"Ste must be finite; got {Ste!r}")
    if ste <= 0.0:
        raise ScopeViolationError(
            f"Stefan number Ste must be > 0 for Neumann root; got Ste={ste}"
        )
    if not math.isfinite(tol_f) or tol_f <= 0.0:
        raise ScopeViolationError(f"tol must be finite and > 0; got {tol!r}")

    # f(0+) < 0; f → +∞ as λ → ∞. Expand upper bracket until f(hi) > 0.
    lo = 0.0
    hi = 1.0
    f_hi = _neumann_f(hi, ste)
    expand = 0
    while f_hi <= 0.0:
        hi *= 2.0
        f_hi = _neumann_f(hi, ste)
        expand += 1
        if expand > 60 or not math.isfinite(f_hi):
            raise ScopeViolationError(
                f"failed to bracket Neumann root for Ste={ste}"
            )

    iterations = 0
    while (hi - lo) > tol_f:
        mid = 0.5 * (lo + hi)
        f_mid = _neumann_f(mid, ste)
        if f_mid > 0.0:
            hi = mid
        else:
            lo = mid
        iterations += 1
        if iterations > 10_000:
            raise ScopeViolationError(
                f"bisection did not converge within 10000 iterations "
                f"(Ste={ste}, tol={tol_f})"
            )

    lam = 0.5 * (lo + hi)
    residual = abs(_neumann_f(lam, ste))
    return {
        "lambda": float(lam),
        "iterations": int(iterations),
        "residual": float(residual),
    }


def melt_front_position(lam: Number, alpha: Number, t: Number) -> float:
    """Melt-front position ``s(t) = 2 · λ · √(α · t)``.

    Parameters
    ----------
    lam :
        Neumann root ``λ > 0`` from ``neumann_lambda``.
    alpha :
        Thermal diffusivity ``α > 0``.
    t :
        Time ``t >= 0``.

    Returns
    -------
    float
        Front position ``s(t)``.

    Raises
    ------
    ScopeViolationError
        If ``lam``, ``alpha``, or ``t`` violate the similarity-domain
        assumptions (``lam > 0``, ``alpha > 0``, ``t >= 0``, all finite).
    """
    lam_f = float(lam)
    alpha_f = float(alpha)
    t_f = float(t)
    if not math.isfinite(lam_f) or not math.isfinite(alpha_f) or not math.isfinite(t_f):
        raise ScopeViolationError(
            f"lam, alpha, t must be finite; got lam={lam!r}, alpha={alpha!r}, t={t!r}"
        )
    if lam_f <= 0.0:
        raise ScopeViolationError(f"lam must be > 0; got {lam_f}")
    if alpha_f <= 0.0:
        raise ScopeViolationError(f"alpha (diffusivity) must be > 0; got {alpha_f}")
    if t_f < 0.0:
        raise ScopeViolationError(f"t must be >= 0; got {t_f}")
    return 2.0 * lam_f * math.sqrt(alpha_f * t_f)


def temperature_profile(
    x: Number,
    t: Number,
    lam: Number,
    alpha: Number,
    T0: Number,
) -> float:
    """One-phase liquid temperature ``T(x,t)`` on ``0 <= x <= s(t)``.

    Formula (Neumann similarity solution):

        T(x,t) = T0 · (1 - erf(x / (2√(α t))) / erf(λ))

    for ``0 <= x <= s(t)`` with ``s(t) = 2 λ √(α t)``. Outside the liquid
    region the one-phase model is undefined → ``ScopeViolationError``.

    Why **not** a viability subclass: ``s(t)`` is a dynamic free boundary
    with its own motion law, not a fixed set ``K`` to check membership
    against.

    Parameters
    ----------
    x, t, lam, alpha, T0 :
        Position, time, Neumann root, diffusivity, surface temperature
        difference.

    Returns
    -------
    float
        Temperature in the liquid phase.

    Raises
    ------
    ScopeViolationError
        If ``x`` is outside ``[0, s(t)]``, or parameters are invalid
        (``t <= 0`` needed for the erf similarity form at finite ``x``,
        ``lam > 0``, ``alpha > 0``).
    """
    x_f = float(x)
    t_f = float(t)
    lam_f = float(lam)
    alpha_f = float(alpha)
    T0_f = float(T0)
    for name, val in (
        ("x", x_f),
        ("t", t_f),
        ("lam", lam_f),
        ("alpha", alpha_f),
        ("T0", T0_f),
    ):
        if not math.isfinite(val):
            raise ScopeViolationError(f"{name} must be finite; got {val!r}")
    if lam_f <= 0.0:
        raise ScopeViolationError(f"lam must be > 0; got {lam_f}")
    if alpha_f <= 0.0:
        raise ScopeViolationError(f"alpha must be > 0; got {alpha_f}")
    if t_f <= 0.0:
        raise ScopeViolationError(
            f"t must be > 0 for the similarity temperature profile; got {t_f}"
        )

    s_t = melt_front_position(lam_f, alpha_f, t_f)
    # Inclusive endpoints: x=0 (surface) and x=s(t) (front, T→0 relative).
    if x_f < 0.0 or x_f > s_t * (1.0 + 1e-14) + 1e-15:
        raise ScopeViolationError(
            f"x={x_f} outside liquid region [0, s(t)={s_t}] "
            f"(one-phase model; no two-phase extension)"
        )
    if x_f > s_t:
        x_f = s_t  # clamp numerical overshoot inside tolerance

    denom = math.erf(lam_f)
    if denom == 0.0:
        raise ScopeViolationError("erf(lam) is zero — lam too small")
    arg = x_f / (2.0 * math.sqrt(alpha_f * t_f))
    return T0_f * (1.0 - math.erf(arg) / denom)


def as_report_fields(result: Mapping[str, Any]) -> Dict[str, Any]:
    """Shallow copy helper for verification JSON (identity on dict results)."""
    return dict(result)
