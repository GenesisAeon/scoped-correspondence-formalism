"""Structural identifiability reports with a precise scope (Paket J6, §12).

One report type for three DIFFERENT kinds of statement, kept apart in the
``method`` and ``scope`` fields:

- ``exact_affine``           -- proved by exact linear algebra
                                (``exact_linear.analyze_affine_identifiability``);
- ``analytic_argument``      -- a documented analytic derivation for a named
                                model family, with its witnesses checked exactly;
- ``finite_candidate_fibre`` -- an exhaustive scan of a FINITE candidate list
                                (``epistemic.observation_fibers``); never a
                                statement about all real parameters.

``scope`` is ``global`` (on the stated parameter domain), ``local`` (near a
stated point) or ``unsupported``. A numerically full Jacobian rank does not
certify global uniqueness; Fisher information, profile likelihood and
structural identifiability are separate results and are not merged here.
General nonlinear (rational ODE) identifiability is out of scope; an
optional SIAN / StructuralIdentifiability.jl adapter would have to keep its
own local/global/generic classes and probability parameters (plan §12).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
from typing import Any, Callable, Optional, Sequence, Tuple

from scoped_correspondence.epistemic.observation_fibers import FiberReport, observation_fiber
from scoped_correspondence.epistemic.records import FiniteDomainSpec
from scoped_correspondence.errors import ScopeViolationError
from scoped_correspondence.identifiability.exact_linear import analyze_affine_identifiability, is_identifiable_combination

METHODS = ("exact_affine", "analytic_argument", "finite_candidate_fibre", "unsupported")
SCOPES = ("global", "local", "unsupported")


@dataclass(frozen=True)
class StructuralReport:
    model: str
    method: str
    scope: str
    parameter_domain: str
    identifiable: Tuple[str, ...]
    not_identifiable: Tuple[str, ...]
    witnesses: Tuple[Any, ...] = ()
    assumptions: Tuple[str, ...] = ()
    notes: Tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if self.method not in METHODS:
            raise ValueError(f"method must be one of {METHODS}")
        if self.scope not in SCOPES:
            raise ValueError(f"scope must be one of {SCOPES}")


def _q(x, what) -> Fraction:
    if isinstance(x, bool) or isinstance(x, float) or not isinstance(x, (int, Fraction)):
        raise ScopeViolationError(f"{what} must be exact")
    return Fraction(x)


def reservoir_decay_report(k, c, x0, lam, *, c_known: bool = False, x0_known: bool = False) -> StructuralReport:
    """J-C12: dx/dt = -k x, y = c x with k, c, x0 > 0, ideal continuous
    observation of y. From y(0) = c x0 and y'(0) = -k c x0 one obtains
    k = -y'(0)/y(0) and the product c x0; (c, x0) -> (c/lam, lam x0)
    leaves every y(t) unchanged. Positivity excludes the zero signal.

    The product statement is cross-checked by EXACT affine analysis in log
    coordinates: log y(0) = log c + log x0 is affine with A = [[1, 1]]
    (valid because of positivity)."""
    k, c, x0, lam = (_q(v, n) for v, n in ((k, "k"), (c, "c"), (x0, "x0"), (lam, "lambda")))
    if min(k, c, x0, lam) <= 0:
        raise ScopeViolationError("J-C12 family requires k, c, x0, lambda > 0 (zero signal excluded on purpose)")
    y0, dy0 = c * x0, -k * c * x0
    c2, x02 = c / lam, lam * x0
    same = (c2 * x02 == y0) and (-k * c2 * x02 == dy0)  # y(t) = y0 exp(-k t) for both
    log_affine = analyze_affine_identifiability([[1, 1]])  # (log c, log x0)
    if c_known and x0_known:
        raise ScopeViolationError("declare at most one of c / x0 as known")
    if x0_known:
        return StructuralReport("reservoir_decay y=c x, x'=-k x", "analytic_argument", "global", "k, c > 0; initial condition x0 known",
                                ("k", "c"), (), (), ("initial condition x0 known exactly", "continuous noiseless observation"),
                                (f"c = y(0)/x0 = {y0 / x0}",))
    if c_known:
        return StructuralReport("reservoir_decay y=c x, x'=-k x", "analytic_argument", "global", "k, x0 > 0; c known",
                                ("k", "x0"), (), (), ("c known exactly", "continuous noiseless observation"),
                                (f"x0 = y(0)/c = {y0 / c}",))
    return StructuralReport(
        "reservoir_decay y=c x, x'=-k x", "analytic_argument", "global", "k, c, x0 > 0",
        identifiable=("k", "c*x0"), not_identifiable=("c", "x0"),
        witnesses=({"theta": (str(k), str(c), str(x0)), "theta_prime": (str(k), str(c2), str(x02)), "same_output": same},),
        assumptions=("positivity of k, c, x0", "continuous noiseless observation of y"),
        notes=(f"y(0) = {y0}, y'(0) = {dy0}, k = {-dy0 / y0}",
               f"log-coordinate exact affine check: rank {log_affine.rank} of 2, sum (= log of the product) identifiable: "
               f"{is_identifiable_combination([[1, 1]], [1, 1])}, split identifiable: {is_identifiable_combination([[1, 1]], [1, 0])}"),
    )


def square_map_report(y, theta_star) -> StructuralReport:
    """J-C13: y = theta^2. For a rational perfect square y > 0 the fibre on R
    is {-sqrt(y), sqrt(y)}: locally identifiable at theta* != 0 (derivative
    2 theta* != 0), not globally on R; on theta > 0 only sqrt(y) remains."""
    y, t = _q(y, "y"), _q(theta_star, "theta*")
    if t * t != y:
        raise ScopeViolationError("theta* must satisfy theta*^2 = y")
    if y <= 0:
        raise ScopeViolationError("this report covers y > 0 only (y = 0 has derivative 0 at the only root)")
    root = abs(t)
    fibre = (-root, root)
    return StructuralReport(
        "y = theta^2", "analytic_argument", "local", f"R (global: not identifiable); theta > 0: identifiable",
        identifiable=(f"theta near {t} (local)", "theta on theta > 0 (global on that domain)"),
        not_identifiable=("theta on R (global)",),
        witnesses=({"fibre": [str(v) for v in fibre], "derivative_at_theta_star": str(2 * t)},),
        notes=("a polynomial of degree 2 has at most these two real roots; both are checked exactly",),
    )


def finite_candidate_fibre(model: str, candidates: Sequence[Any], observation: Callable[[Any], Any], observed: Any) -> Tuple[FiberReport, StructuralReport]:
    """Exhaustive fibre over a FINITE candidate list (existing H3 machinery).
    The structural report states explicitly that nothing follows for
    parameters outside the list."""
    dom = FiniteDomainSpec(id=f"{model}_candidates", candidates=tuple(candidates), scope_text="declared finite candidates",
                           coverage="partial", relationship_to_target_space="restricted_candidates")
    fib = observation_fiber(dom, [], observation, observed)
    rep = StructuralReport(model, "finite_candidate_fibre", "unsupported" if not fib.search_complete else "global",
                           f"finite candidate list of size {len(candidates)} (restricted_candidates)",
                           identifiable=() if fib.n_fiber != 1 else (f"unique among the listed candidates: {fib.fiber[0]!r}",),
                           not_identifiable=() if fib.n_fiber <= 1 else (f"{fib.n_fiber} listed candidates share the observation",),
                           witnesses=tuple(fib.fiber),
                           notes=("statement about the LISTED candidates only, not about all real parameters",))
    return fib, rep


def unsupported_report(model: str, reason: str) -> StructuralReport:
    return StructuralReport(model, "unsupported", "unsupported", "n/a", (), (), notes=(reason,))


__all__ = ["METHODS", "SCOPES", "StructuralReport", "reservoir_decay_report", "square_map_report",
           "finite_candidate_fibre", "unsupported_report"]
