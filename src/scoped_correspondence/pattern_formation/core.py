"""Pattern formation / Turing instability (Milestone 30).

Independent Baustein for 2×2 reaction–diffusion linear Turing analysis
(activator–inhibitor / Schnakenberg 1979 kinetics). No PDE solver, no
spatial simulation, and **not** an extension of ``dynamics``.

Schnakenberg 1979 (J Theor Biol) is a DIFFERENT paper than Schnakenberg 1976 (Rev Mod Phys) used in thermo/schnakenberg.py (M18) — different journal/year/claim; do not mix modules.

A future correspondence bridge to dynamics is structurally conceivable (Turing S_rec(k) would generalize dynamics.recovery_rate_at_equilibrium as S_rec(0)) but is NOT claimed or implemented here; a real conjugacy would need the correspondence contract with its own proof.

Sources:
  - Turing 1952, Phil. Trans. R. Soc. Lond. B 237, 37–72;
    DOI 10.1098/rstb.1952.0012
  - Schnakenberg 1979, J. Theor. Biol. 81, 389–400;
    DOI 10.1016/0022-5193(79)90042-0
  - Murray 2003, Mathematical Biology II, Springer;
    DOI 10.1007/b98869
"""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from typing import Any, Dict, Mapping, Sequence, Union

from scoped_correspondence.errors import ScopeViolationError

ArrayLike = Union[Sequence[Sequence[float]], Mapping[str, Any]]

SOURCE = (
    "Turing 1952 DOI 10.1098/rstb.1952.0012; "
    "Schnakenberg 1979 DOI 10.1016/0022-5193(79)90042-0; "
    "Murray 2003 DOI 10.1007/b98869"
)

# Verbatim mandatory warnings (acceptance criteria) — must appear in module
# docstring AND in verification JSON report fields.
SCHNAKENBERG_PAPER_WARNING: str = (
    "Schnakenberg 1979 (J Theor Biol) is a DIFFERENT paper than "
    "Schnakenberg 1976 (Rev Mod Phys) used in thermo/schnakenberg.py (M18) — "
    "different journal/year/claim; do not mix modules."
)

DYNAMICS_BRIDGE_WARNING: str = (
    "A future correspondence bridge to dynamics is structurally conceivable "
    "(Turing S_rec(k) would generalize dynamics.recovery_rate_at_equilibrium "
    "as S_rec(0)) but is NOT claimed or implemented here; a real conjugacy "
    "would need the correspondence contract with its own proof."
)

_SCOPE_NOTES: tuple[str, ...] = (
    "independent Baustein; not an extension of dynamics/",
    SCHNAKENBERG_PAPER_WARNING,
    DYNAMICS_BRIDGE_WARNING,
    "no PDE solver / spatial simulation",
    "2x2 Jacobian linear Turing conditions only (Murray 2003)",
)


def _as_2x2(J: ArrayLike) -> tuple[float, float, float, float]:
    """Parse a 2×2 Jacobian as (f_u, f_v, g_u, g_v)."""
    if isinstance(J, Mapping):
        keys = ("f_u", "f_v", "g_u", "g_v")
        if all(k in J for k in keys):
            return (
                float(J["f_u"]),
                float(J["f_v"]),
                float(J["g_u"]),
                float(J["g_v"]),
            )
        raise ScopeViolationError(
            "jacobian Mapping must provide keys f_u, f_v, g_u, g_v"
        )
    try:
        rows = list(J)  # type: ignore[arg-type]
    except TypeError as exc:
        raise ScopeViolationError(
            f"jacobian_stability: J must be 2x2 sequence; got {type(J)!r}"
        ) from exc
    if len(rows) != 2:
        raise ScopeViolationError(
            f"jacobian_stability: J must be 2x2; got {len(rows)} rows"
        )
    r0 = list(rows[0])
    r1 = list(rows[1])
    if len(r0) != 2 or len(r1) != 2:
        raise ScopeViolationError(
            "jacobian_stability: J must be 2x2 (two columns per row)"
        )
    return float(r0[0]), float(r0[1]), float(r1[0]), float(r1[1])


def _trace_det(fu: float, fv: float, gu: float, gv: float) -> tuple[float, float]:
    return fu + gv, fu * gv - fv * gu


@dataclass(frozen=True)
class JacobianStabilityResult:
    """Homogeneous (k=0) Routh–Hurwitz stability for a 2×2 Jacobian."""

    stable: bool
    trace: float
    det: float
    condition_trace_neg: bool
    condition_det_pos: bool
    scope_notes: tuple[str, ...] = _SCOPE_NOTES

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class TuringConditionsResult:
    """Four classical Turing instability conditions plus critical wave number."""

    turing_unstable: bool
    trace: float
    det: float
    condition_i_trace_neg: bool
    condition_ii_det_pos: bool
    condition_iii_diffusive: bool
    condition_iv_discriminant: bool
    h: float  # D_v f_u + D_u g_v
    k_c_sq: float | None
    k_c_sq_from_det: float | None
    k_c_sq_agree: bool | None
    D_u: float
    D_v: float
    f_u: float
    f_v: float
    g_u: float
    g_v: float
    scope_notes: tuple[str, ...] = _SCOPE_NOTES
    source: str = SOURCE

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class DispersionResult:
    """Dispersion: Re(λ_max) of J − k² diag(D_u, D_v)."""

    k: float
    k_sq: float
    re_lambda_max: float
    eigenvalues: tuple[complex, ...]
    D_u: float
    D_v: float
    scope_notes: tuple[str, ...] = _SCOPE_NOTES

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["eigenvalues"] = [
            {"re": float(z.real), "im": float(z.imag)} for z in self.eigenvalues
        ]
        return d


@dataclass(frozen=True)
class Schnakenberg1979SteadyState:
    """Homogeneous steady state and Jacobian for Schnakenberg 1979 kinetics."""

    a: float
    b: float
    u_star: float
    v_star: float
    f_u: float
    f_v: float
    g_u: float
    g_v: float
    jacobian: tuple[tuple[float, float], tuple[float, float]]
    trace: float
    det: float
    paper_warning: str = SCHNAKENBERG_PAPER_WARNING
    dynamics_bridge_warning: str = DYNAMICS_BRIDGE_WARNING
    source: str = SOURCE
    scope_notes: tuple[str, ...] = _SCOPE_NOTES

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def jacobian_stability(J: ArrayLike) -> JacobianStabilityResult:
    """Homogeneous stability: tr(J)<0 AND det(J)>0 (2×2 Routh–Hurwitz).

    Parameters
    ----------
    J :
        2×2 Jacobian ``[[f_u, f_v], [g_u, g_v]]`` or mapping with those keys.

    Returns
    -------
    JacobianStabilityResult
        ``stable`` iff both Routh–Hurwitz inequalities hold.

    Raises
    ------
    ScopeViolationError
        If ``J`` is not 2×2.
    """
    fu, fv, gu, gv = _as_2x2(J)
    tr, det = _trace_det(fu, fv, gu, gv)
    c_tr = tr < 0.0
    c_det = det > 0.0
    return JacobianStabilityResult(
        stable=bool(c_tr and c_det),
        trace=float(tr),
        det=float(det),
        condition_trace_neg=bool(c_tr),
        condition_det_pos=bool(c_det),
    )


def turing_conditions(
    J: ArrayLike,
    D_u: float,
    D_v: float,
) -> TuringConditionsResult:
    """Classical four Turing conditions for a 2×2 reaction–diffusion system.

    With Jacobian entries ``f_u, f_v, g_u, g_v`` and diffusivities ``D_u, D_v > 0``:

    (i)   ``tr = f_u + g_v < 0``
    (ii)  ``det = f_u g_v − f_v g_u > 0``
    (iii) ``h = D_v f_u + D_u g_v > 0``
    (iv)  ``h² > 4 D_u D_v det``

    When (iii) holds, the critical wave number squared is

    ``k_c² = h / (2 D_u D_v)``.

    At the onset of Turing instability (equality in (iv)), this agrees with

    ``k_c² = sqrt(det / (D_u D_v))``.

    Schnakenberg 1979 (J Theor Biol) is a DIFFERENT paper than Schnakenberg 1976 (Rev Mod Phys) used in thermo/schnakenberg.py (M18) — different journal/year/claim; do not mix modules.

    A future correspondence bridge to dynamics is structurally conceivable (Turing S_rec(k) would generalize dynamics.recovery_rate_at_equilibrium as S_rec(0)) but is NOT claimed or implemented here; a real conjugacy would need the correspondence contract with its own proof.

    Parameters
    ----------
    J :
        2×2 Jacobian.
    D_u, D_v :
        Positive diffusivities.

    Returns
    -------
    TuringConditionsResult

    Raises
    ------
    ScopeViolationError
        If diffusivities are not positive or ``J`` is not 2×2.
    """
    du = float(D_u)
    dv = float(D_v)
    if not (du > 0.0 and dv > 0.0):
        raise ScopeViolationError(
            f"turing_conditions: require D_u > 0 and D_v > 0; got D_u={D_u!r}, D_v={D_v!r}"
        )
    if not (math.isfinite(du) and math.isfinite(dv)):
        raise ScopeViolationError("turing_conditions: diffusivities must be finite")

    fu, fv, gu, gv = _as_2x2(J)
    tr, det = _trace_det(fu, fv, gu, gv)
    h = dv * fu + du * gv
    c_i = tr < 0.0
    c_ii = det > 0.0
    c_iii = h > 0.0
    c_iv = (h * h) > (4.0 * du * dv * det)

    k_c_sq: float | None = None
    k_c_sq_from_det: float | None = None
    agree: bool | None = None
    if c_iii and du > 0.0 and dv > 0.0:
        k_c_sq = h / (2.0 * du * dv)
        if det > 0.0:
            k_c_sq_from_det = math.sqrt(det / (du * dv))
            # Agreement is exact at criticality (equality in iv); report
            # relative closeness when both are defined.
            agree = math.isclose(
                float(k_c_sq), float(k_c_sq_from_det), rel_tol=1e-9, abs_tol=1e-12
            )

    return TuringConditionsResult(
        turing_unstable=bool(c_i and c_ii and c_iii and c_iv),
        trace=float(tr),
        det=float(det),
        condition_i_trace_neg=bool(c_i),
        condition_ii_det_pos=bool(c_ii),
        condition_iii_diffusive=bool(c_iii),
        condition_iv_discriminant=bool(c_iv),
        h=float(h),
        k_c_sq=None if k_c_sq is None else float(k_c_sq),
        k_c_sq_from_det=None if k_c_sq_from_det is None else float(k_c_sq_from_det),
        k_c_sq_agree=agree,
        D_u=du,
        D_v=dv,
        f_u=float(fu),
        f_v=float(fv),
        g_u=float(gu),
        g_v=float(gv),
    )


def dispersion_relation(
    J: ArrayLike,
    D_u: float,
    D_v: float,
    k: float,
) -> DispersionResult:
    """Dispersion relation: Re(λ_max) of ``J − k² diag(D_u, D_v)``.

    For Fourier mode wave number ``k ≥ 0``, the linearized RD operator on
    that mode is the 2×2 matrix ``A(k) = J − k² D`` with
    ``D = diag(D_u, D_v)``. Returns the largest real part among eigenvalues
    of ``A(k)`` (growth rate; positive ⇒ linearly unstable at that ``k``).

    A future correspondence bridge to dynamics is structurally conceivable (Turing S_rec(k) would generalize dynamics.recovery_rate_at_equilibrium as S_rec(0)) but is NOT claimed or implemented here; a real conjugacy would need the correspondence contract with its own proof.

    Parameters
    ----------
    J :
        2×2 Jacobian at the homogeneous steady state.
    D_u, D_v :
        Positive diffusivities.
    k :
        Wave number (``k ≥ 0``).

    Returns
    -------
    DispersionResult

    Raises
    ------
    ScopeViolationError
        If diffusivities are not positive or ``k < 0``.
    """
    du = float(D_u)
    dv = float(D_v)
    kk = float(k)
    if not (du > 0.0 and dv > 0.0):
        raise ScopeViolationError(
            f"dispersion_relation: require D_u > 0 and D_v > 0; got D_u={D_u!r}, D_v={D_v!r}"
        )
    if kk < 0.0 or not math.isfinite(kk):
        raise ScopeViolationError(
            f"dispersion_relation: require k ≥ 0 finite; got {k!r}"
        )

    fu, fv, gu, gv = _as_2x2(J)
    k2 = kk * kk
    # A = [[f_u - k² D_u, f_v], [g_u, g_v - k² D_v]]
    a11 = fu - k2 * du
    a12 = fv
    a21 = gu
    a22 = gv - k2 * dv
    # Characteristic polynomial λ² − tr λ + det = 0
    tr = a11 + a22
    det = a11 * a22 - a12 * a21
    disc = tr * tr - 4.0 * det
    if disc >= 0.0:
        s = math.sqrt(disc)
        lam1 = 0.5 * (tr + s)
        lam2 = 0.5 * (tr - s)
        eigs = (complex(lam1, 0.0), complex(lam2, 0.0))
        re_max = max(lam1, lam2)
    else:
        s = math.sqrt(-disc)
        re = 0.5 * tr
        im = 0.5 * s
        eigs = (complex(re, im), complex(re, -im))
        re_max = re

    return DispersionResult(
        k=kk,
        k_sq=float(k2),
        re_lambda_max=float(re_max),
        eigenvalues=eigs,
        D_u=du,
        D_v=dv,
    )


def schnakenberg_1979_steady_state(a: float, b: float) -> Schnakenberg1979SteadyState:
    """Homogeneous steady state and Jacobian for Schnakenberg 1979 kinetics.

    Kinetics (Schnakenberg 1979, J. Theor. Biol.):

        ``du/dt = a − u + u² v``, ``dv/dt = b − u² v``.

    Steady state: ``u* = a + b``, ``v* = b / (a + b)²`` (requires ``a + b ≠ 0``).

    Jacobian entries at ``(u*, v*)``:

        ``f_u = (b − a) / (a + b)``, ``f_v = (a + b)²``,
        ``g_u = −2 b / (a + b)``, ``g_v = −(a + b)²``.

    Schnakenberg 1979 (J Theor Biol) is a DIFFERENT paper than Schnakenberg 1976 (Rev Mod Phys) used in thermo/schnakenberg.py (M18) — different journal/year/claim; do not mix modules.

    Parameters
    ----------
    a, b :
        Nonnegative Schnakenberg parameters with ``a + b > 0``.

    Returns
    -------
    Schnakenberg1979SteadyState

    Raises
    ------
    ScopeViolationError
        If ``a + b ≤ 0`` or parameters are non-finite.
    """
    aa = float(a)
    bb = float(b)
    if not (math.isfinite(aa) and math.isfinite(bb)):
        raise ScopeViolationError(
            f"schnakenberg_1979_steady_state: a, b must be finite; got a={a!r}, b={b!r}"
        )
    s = aa + bb
    if s <= 0.0:
        raise ScopeViolationError(
            f"schnakenberg_1979_steady_state: require a + b > 0; got a={a!r}, b={b!r}"
        )

    u_star = s
    v_star = bb / (s * s)
    f_u = (bb - aa) / s
    f_v = s * s
    g_u = -2.0 * bb / s
    g_v = -(s * s)
    tr, det = _trace_det(f_u, f_v, g_u, g_v)

    return Schnakenberg1979SteadyState(
        a=aa,
        b=bb,
        u_star=float(u_star),
        v_star=float(v_star),
        f_u=float(f_u),
        f_v=float(f_v),
        g_u=float(g_u),
        g_v=float(g_v),
        jacobian=((float(f_u), float(f_v)), (float(g_u), float(g_v))),
        trace=float(tr),
        det=float(det),
    )


def critical_diffusivity_roots_schnakenberg(
    a: float = 0.1,
    b: float = 0.9,
    D_u: float = 1.0,
) -> Dict[str, float]:
    """Solve equality (iv) for ``D_v`` given Schnakenberg (a,b) and ``D_u``.

    For the worked example ``a=0.1, b=0.9, D_u=1`` the quadratic is

    ``0.64 D_v² − 5.6 D_v + 1 = 0``,

    with roots ``D_v_c ≈ 8.567627`` (larger, Turing-relevant) and
    ``≈ 0.182373`` (smaller; fails condition (iii) for this Jacobian).

    Helper for verification / docs; not required for the core Turing API.
    """
    ss = schnakenberg_1979_steady_state(a, b)
    du = float(D_u)
    if du <= 0.0:
        raise ScopeViolationError("D_u must be positive")
    fu, fv, gu, gv = ss.f_u, ss.f_v, ss.g_u, ss.g_v
    det = ss.det
    # h = D_v f_u + D_u g_v; (h)² = 4 D_u D_v det
    # (f_u²) D_v² + 2 f_u D_u g_v D_v + D_u² g_v² − 4 D_u det D_v = 0
    # A D_v² + B D_v + C = 0 with
    A = fu * fu
    B = 2.0 * fu * du * gv - 4.0 * du * det
    C = (du * gv) * (du * gv)
    if abs(A) < 1e-18:
        raise ScopeViolationError("f_u≈0; quadratic in D_v degenerates")
    disc = B * B - 4.0 * A * C
    if disc < 0.0:
        raise ScopeViolationError(f"no real D_v critical roots; disc={disc}")
    s = math.sqrt(disc)
    r1 = (-B + s) / (2.0 * A)
    r2 = (-B - s) / (2.0 * A)
    lo, hi = (r1, r2) if r1 < r2 else (r2, r1)
    return {
        "A": float(A),
        "B": float(B),
        "C": float(C),
        "D_v_smaller": float(lo),
        "D_v_larger": float(hi),
        "D_v_c": float(hi),
        "D_u": du,
        "f_u": fu,
        "g_v": gv,
        "det": det,
    }
