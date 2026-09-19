"""Control Barrier Functions — scalar zeroing CBF (Milestone 16).

Maps Ames, Xu, Grizzle & Tabuada 2017
(DOI 10.1109/TAC.2016.2638961) and the Ames et al. 2019 ECC survey
(DOI 10.23919/ECC.2019.8796030): a continuously differentiable barrier
h defines the safe set C = {x | h(x) >= 0}; forward invariance of C
follows from the CBF inequality on the control-affine dynamics

    x_dot = f(x) + g(x) u

    L_f h(x) + L_g h(x) u + alpha(h(x)) >= 0

for an extended class-K function alpha. This module implements the
**scalar** specialization

    x_dot = u,   h(x) = x,   alpha(r) = r   (linear / identity class-K)

so that L_f h = 0, L_g h = 1 and the CBF condition collapses to

    u + x >= 0.

No QP solver, no multi-D state, no nonlinear alpha. Does **not** call
or re-express ``has_safe_transfer`` (viability/core.py untouched).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Callable, Dict, Tuple

from scoped_correspondence.errors import ScopeViolationError

_SOURCE_2017 = (
    "Ames, Xu, Grizzle & Tabuada 2017, "
    "Control Barrier Function Based Quadratic Programs for Safety Critical "
    "Systems, IEEE TAC; DOI 10.1109/TAC.2016.2638961"
)
_SOURCE_2019 = (
    "Ames, Coogan, Egerstedt, Notomista, Sreenath & Tabuada 2019, "
    "Control Barrier Functions: Theory and Applications, ECC; "
    "DOI 10.23919/ECC.2019.8796030"
)
SOURCE = f"{_SOURCE_2017}; survey: {_SOURCE_2019}"

ALPHA_LINEAR = "linear"

_DEFAULT_ASSUMPTIONS: Tuple[str, ...] = (
    "scalar control-affine dynamics x_dot = u only (f=0, g=1); multi-D out of scope",
    "alpha is the linear / identity class-K map alpha(r)=r — nonlinear alpha out of scope",
    "zeroing CBF condition: L_f h + L_g h * u + alpha(h) >= 0 (Ames et al. 2017)",
    "safe set C = {x | h(x) >= 0}; certificate implies forward invariance of C "
    "under the checked control (Nagumo / CBF theorem), not a viability kernel",
    "no QP / CLF-CBF quadratic program — inequality check only (Ames 2017 QP omitted)",
    "does not call or redefine has_safe_transfer (viability/core.py unchanged)",
)

# Sample points used to refuse nonlinear alpha at construction time.
_ALPHA_PROBE: Tuple[float, ...] = (-2.0, -0.5, 0.0, 0.25, 0.7, 1.0, 3.5)


def _require_identity_h(h: Callable[[float], float]) -> None:
    """Refuse any h that is not the identity on probe points.

    Audit finding A06: the old code only checked h(x)==x AT THE SINGLE
    EVALUATION POINT of a later call (inside _scalar_lie_derivatives),
    which h(x)=1-x satisfies exactly at x=0.5 (1-0.5=0.5) despite being a
    completely different function with h'=-1, not h'=1. That let an
    unsupported barrier through with a silently wrong L_g_h=1, producing
    a wrong safety margin/verdict. Mirrors the existing _require_linear_alpha
    probe check: verify identity STRUCTURALLY, on multiple points, at
    construction time — not pointwise, after the fact, on whatever x a
    caller later happens to pass in.
    """
    for s in _ALPHA_PROBE:
        try:
            val = float(h(s))
        except Exception as exc:  # noqa: BLE001 — surface as scope violation
            raise ScopeViolationError(
                f"BarrierFunction: h must be callable on floats; "
                f"h({s!r}) raised {type(exc).__name__}: {exc}"
            ) from exc
        if abs(val - float(s)) > 1e-12:
            raise ScopeViolationError(
                "BarrierFunction: only the identity barrier h(x)=x is "
                f"supported (M16); h({s!r})={val!r} != {s!r}. Matching h(x)=x "
                "at a single evaluation point does not establish h is the "
                "identity function (e.g. h(x)=1-x also matches at x=0.5)."
            )


def _require_linear_alpha(alpha: Callable[[float], float]) -> None:
    """Refuse any alpha that is not the identity on probe points."""
    for s in _ALPHA_PROBE:
        try:
            val = float(alpha(s))
        except Exception as exc:  # noqa: BLE001 — surface as scope violation
            raise ScopeViolationError(
                f"BarrierFunction: alpha must be callable on floats; "
                f"alpha({s!r}) raised {type(exc).__name__}: {exc}"
            ) from exc
        if abs(val - float(s)) > 1e-12:
            raise ScopeViolationError(
                "BarrierFunction: only linear alpha(h)=h is supported "
                f"(M16); alpha({s!r})={val!r} != {s!r}. "
                "Nonlinear / non-identity class-K maps are out of scope."
            )


@dataclass(frozen=True)
class BarrierFunction:
    """Scalar barrier h with linear class-K alpha (identity).

    Parameters
    ----------
    h :
        Callable ``h(x) -> float``. Safe set is ``{x | h(x) >= 0}``.
    alpha :
        Callable ``alpha(r) -> float``. **Must** satisfy ``alpha(r) = r``
        on the probe set (linear / identity class-K only).
    alpha_kind :
        Must be ``\"linear\"``. Any other value raises ``ScopeViolationError``.
    """

    h: Callable[[float], float]
    alpha: Callable[[float], float]
    alpha_kind: str = ALPHA_LINEAR

    def __post_init__(self) -> None:
        if self.alpha_kind != ALPHA_LINEAR:
            raise ScopeViolationError(
                f"BarrierFunction: alpha_kind must be {ALPHA_LINEAR!r}; "
                f"got {self.alpha_kind!r}. Nonlinear alpha is out of scope (M16)."
            )
        if not callable(self.h):
            raise ScopeViolationError("BarrierFunction: h must be callable")
        if not callable(self.alpha):
            raise ScopeViolationError("BarrierFunction: alpha must be callable")
        _require_identity_h(self.h)
        _require_linear_alpha(self.alpha)

    def eval_h(self, x: float) -> float:
        return float(self.h(float(x)))

    def eval_alpha(self, r: float) -> float:
        # Identity by construction, but call through for transparency.
        return float(self.alpha(float(r)))


@dataclass(frozen=True)
class BarrierCertificate:
    """CBF inequality certificate at a single (x, u).

    ``safe`` is True iff ``margin >= 0``, where

        margin = L_f h + L_g h * u + alpha(h(x)).

    For the scalar integrator with h(x)=x and alpha(r)=r this is ``u + x``.
    """

    safe: bool
    margin: float
    x: float
    u: float
    h_x: float
    alpha_h: float
    L_f_h: float
    L_g_h: float
    assumptions: Tuple[str, ...] = _DEFAULT_ASSUMPTIONS
    source: str = SOURCE

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["assumptions"] = list(self.assumptions)
        return d


def cbf_condition(
    L_f_h: float,
    L_g_h: float,
    u: float,
    alpha_h: float,
) -> float:
    """Return the CBF margin ``L_f_h + L_g_h * u + alpha_h``.

    The inequality ``cbf_condition(...) >= 0`` is the Ames et al. 2017
    zeroing-CBF condition (no QP). Safe iff the returned margin is
    nonnegative.
    """
    # Round to 12 dp so hand-checkable margins (e.g. -0.1) are exact in JSON
    # despite IEEE binary float dust on sums like -0.3 + 0.2.
    return float(round(float(L_f_h) + float(L_g_h) * float(u) + float(alpha_h), 12))


def _scalar_lie_derivatives(barrier: BarrierFunction, x: float) -> Tuple[float, float, float, float]:
    """Lie derivatives for the scalar integrator x_dot = u under barrier h.

    Assumes relative degree one with g=1, f=0 on the identity barrier
    h(x)=x used in the M16 worked example. For a general scalar h we
    still take the control-affine model x_dot = u, so

        L_f h = 0,   L_g h = h'(x).

    M16 only certifies the identity barrier h(x)=x (h'=1). Any other h
    raises ``ScopeViolationError`` so we never silently mis-state L_g.
    """
    x_f = float(x)
    h_x = barrier.eval_h(x_f)
    # Enforce the M16 worked-example barrier h(x)=x (relative degree 1, L_g=1).
    if abs(h_x - x_f) > 1e-12:
        raise ScopeViolationError(
            "admissible_controls_cbf / verify_forward_invariance: M16 supports "
            f"only the identity barrier h(x)=x; got h({x_f!r})={h_x!r}."
        )
    alpha_h = barrier.eval_alpha(h_x)
    L_f_h = 0.0
    L_g_h = 1.0
    return h_x, alpha_h, L_f_h, L_g_h


def admissible_controls_cbf(
    barrier: BarrierFunction,
    x: float,
) -> Dict[str, Any]:
    """Admissible control set for scalar ``x_dot = u`` under ``barrier``.

    With ``h(x)=x`` and ``alpha(r)=r`` the CBF inequality is ``u + x >= 0``,
    i.e. the half-line ``u >= -x``. Returns a report dict (not a QP).
    """
    h_x, alpha_h, L_f_h, L_g_h = _scalar_lie_derivatives(barrier, x)
    # L_f + L_g u + alpha_h >= 0  ⇒  u >= -(L_f + alpha_h) / L_g  (L_g=1)
    if abs(L_g_h) < 1e-15:
        raise ScopeViolationError(
            "admissible_controls_cbf: L_g_h ≈ 0 (relative degree issue); "
            "scalar identity barrier requires L_g_h = 1"
        )
    u_min = -(L_f_h + alpha_h) / L_g_h
    return {
        "x": float(x),
        "h_x": h_x,
        "alpha_h": alpha_h,
        "L_f_h": L_f_h,
        "L_g_h": L_g_h,
        "u_min": float(u_min),
        "constraint": "u + x >= 0",
        "admissible": f"u >= {u_min}",
        "dynamics": "x_dot = u",
        "source": SOURCE,
        "assumptions": list(_DEFAULT_ASSUMPTIONS),
    }


def verify_forward_invariance(
    barrier: BarrierFunction,
    x: float,
    u: float,
) -> BarrierCertificate:
    """Check the CBF inequality at ONE instantaneous ``(x, u)`` pair.

    Returns a ``BarrierCertificate`` with ``margin = u + x`` when
    ``h(x)=x`` and ``alpha(r)=r``, and ``safe = (margin >= 0)``.

    Audit finding A06 (local-vs-global): a single passing instantaneous
    check does NOT by itself certify forward invariance under a *held*
    or *policy* control over time — the CBF inequality would need to
    keep holding along the resulting trajectory, which requires either a
    fresh check at each new state or an explicit feedback law u(x). A
    passing certificate here is evidence at that one sampled point only,
    not a proof that a constant ``u`` remains safe as ``x`` evolves.
    """
    h_x, alpha_h, L_f_h, L_g_h = _scalar_lie_derivatives(barrier, x)
    margin = cbf_condition(L_f_h, L_g_h, u, alpha_h)
    return BarrierCertificate(
        safe=bool(margin >= -1e-15),
        margin=float(margin),
        x=float(x),
        u=float(u),
        h_x=h_x,
        alpha_h=alpha_h,
        L_f_h=L_f_h,
        L_g_h=L_g_h,
    )


def make_identity_barrier() -> BarrierFunction:
    """Factory: ``h(x)=x``, ``alpha(r)=r`` (M16 worked-example barrier)."""
    return BarrierFunction(
        h=lambda x: float(x),
        alpha=lambda r: float(r),
        alpha_kind=ALPHA_LINEAR,
    )


__all__ = [
    "ALPHA_LINEAR",
    "SOURCE",
    "BarrierCertificate",
    "BarrierFunction",
    "admissible_controls_cbf",
    "cbf_condition",
    "make_identity_barrier",
    "verify_forward_invariance",
]
