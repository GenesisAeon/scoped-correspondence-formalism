"""Fenichel / Geometric Singular Perturbation Theory (GSPT) helpers (Milestone 33).

Implements the **hand-checkable** critical-manifold geometry for the classical
van-der-Pol critical manifold

    S(x) = x³/3 − x,

with fold points where S'(x) = x² − 1 = 0 (i.e. x = ±1) and normal
hyperbolicity wherever S'(x) ≠ 0. Fenichel's theorem then guarantees, for
sufficiently small ε > 0, a locally invariant slow manifold C_ε that stays
O(ε)-close to the critical manifold C_0 on normally hyperbolic branches
(Fenichel 1979; Kuehn 2015).

Independent of M14 contraction and M29 Landau.

This module is **independent of M14 contraction analysis and of M29 Landau
exponent comparison**: it neither imports ``dynamics.contraction`` /
``dynamics.landau`` nor equates Fenichel normal hyperbolicity with metric
contraction rates or with mean-field / Ising scaling exponents. It likewise
does **not** edit ``dynamics/core.py`` and does **not** identify the
van-der-Pol critical manifold with the cubic cusp normal form of
``dynamics.core`` (FORMALISM.md §5).

Fast–slow system (standard singularly perturbed form)::

    ε ẋ = f(x, y),    ẏ = g(x, y)

Critical manifold C_0 = {(x, y) : f(x, y) = 0}. For the van-der-Pol example
f(x, y) = y − S(x) with S(x) = x³/3 − x, so C_0 is the graph y = S(x).

Sources:
  - Fenichel 1979, J. Differential Equations 31, 53–98;
    DOI 10.1016/0022-0396(79)90152-9
  - Kuehn 2015, Multiple Time Scale Dynamics;
    DOI 10.1007/978-3-319-12316-5

Out of scope for M33: canard / blow-up analysis at the folds, numerical
ODE integration, and any mutation of FORMALISM.md or package-root
``scoped_correspondence.__init__``.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, Tuple

from scoped_correspondence.errors import ScopeViolationError

SOURCE = (
    "Fenichel 1979 DOI 10.1016/0022-0396(79)90152-9; "
    "Kuehn 2015 DOI 10.1007/978-3-319-12316-5"
)

# Verbatim independence fence — must appear in module / API docstrings
# AND as a text field in the verification JSON report.
INDEPENDENCE_WARNING: str = (
    "Independent of M14 contraction and M29 Landau."
)

_SCOPE_NOTES: tuple[str, ...] = (
    "van-der-Pol critical manifold S(x)=x³/3−x; folds at S'(x)=0",
    "normal hyperbolicity ⇔ S'(x)=x²−1 ≠ 0 (Fenichel 1979)",
    "slow_manifold_distance_bound is an O(ε) order estimate only "
    "(no sharp Fenichel constant)",
    "independent of M14 contraction and M29 Landau",
    "no canard / blow-up; no ODE integration; core.py untouched",
)


def critical_manifold_S(x: float) -> float:
    """Critical-manifold graph ``S(x) = x³/3 − x`` (van der Pol).

    Parameters
    ----------
    x :
        Fast-variable coordinate on the critical manifold graph.

    Returns
    -------
    float
        ``S(x) = x**3 / 3 - x``.
    """
    xx = float(x)
    return xx * xx * xx / 3.0 - xx


def critical_manifold_S_prime(x: float) -> float:
    """Derivative ``S'(x) = x² − 1`` of the van-der-Pol critical manifold.

    Parameters
    ----------
    x :
        Fast-variable coordinate.

    Returns
    -------
    float
        ``x**2 - 1``. Zero exactly at the fold points ``x = ±1``.
    """
    xx = float(x)
    return xx * xx - 1.0


@dataclass(frozen=True)
class FoldPoint:
    """A fold of the critical manifold where normal hyperbolicity is lost.

    Attributes
    ----------
    x :
        Fast coordinate of the fold (``S'(x) = 0``).
    s :
        Slow/graph value ``S(x)`` at the fold.
    """

    x: float
    s: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def critical_manifold_fold_points() -> Tuple[FoldPoint, FoldPoint]:
    """Exact fold points of ``S(x) = x³/3 − x``.

    Solving ``S'(x) = x² − 1 = 0`` yields ``x = ±1``. Evaluating ``S``:

    - ``S(+1) = 1/3 − 1 = −2/3``
    - ``S(−1) = −1/3 − (−1) = +2/3``

    so the folds are ``(x, S) = (+1, −2/3)`` and ``(−1, +2/3)``
    (i.e. folds at ``x = ±1``, ``S = ∓2/3``).

    Returns
    -------
    tuple[FoldPoint, FoldPoint]
        ``(FoldPoint(1, -2/3), FoldPoint(-1, +2/3))`` with exact floats
        ``±1.0`` and ``±2/3``.

    Notes
    -----
    Independent of M14 contraction and M29 Landau.
    """
    return (
        FoldPoint(x=1.0, s=-2.0 / 3.0),
        FoldPoint(x=-1.0, s=2.0 / 3.0),
    )


def is_normally_hyperbolic(x: float) -> bool:
    """Return whether ``S'(x) = x² − 1 ≠ 0`` (normal hyperbolicity).

    On the van-der-Pol critical manifold the transverse linearisation is
    governed by ``S'(x)``. Fenichel's persistence of a slow manifold
    requires normal hyperbolicity, i.e. ``S'(x) ≠ 0``. At the fold points
    ``x = ±1`` this fails and canard / blow-up analysis begins (out of
    scope for M33).

    Parameters
    ----------
    x :
        Fast-variable coordinate on ``C_0``.

    Returns
    -------
    bool
        ``True`` iff ``x**2 - 1 != 0`` (within exact float comparison of
        the analytic derivative). Worked checks: ``True`` at
        ``x ∈ {2, 0, 1.5}``; ``False`` at ``x = ±1``.

    Notes
    -----
    Independent of M14 contraction and M29 Landau. Attracting
    (``S' > 0`` for this sign convention of ``f = y − S``) vs repelling
    (``S' < 0``) is **not** distinguished here — only the NH predicate.
    """
    return critical_manifold_S_prime(x) != 0.0


def slow_manifold_distance_bound(epsilon: float, x: float) -> float:
    """O(ε) order-of-magnitude distance estimate ``dist(C_ε, C_0)``.

    Fenichel 1979 guarantees that on a normally hyperbolic branch the
    perturbed slow manifold stays **O(ε)**-close to ``C_0`` for small
    enough ``ε > 0``. This helper returns the **order estimate**
    ``|ε|`` itself (constant factor absorbed into the big-O); it does
    **not** compute a sharp Fenichel constant, a Hausdorff distance, or
    a numerical trajectory residual.

    Parameters
    ----------
    epsilon :
        Singular perturbation parameter (must be ``> 0``).
    x :
        Fast coordinate on a **normally hyperbolic** branch of ``C_0``.

    Returns
    -------
    float
        ``abs(epsilon)`` as an O(ε) order estimate.

    Raises
    ------
    ScopeViolationError
        If ``epsilon ≤ 0`` or if ``x`` is not normally hyperbolic
        (fold / loss of NH).

    Notes
    -----
    Independent of M14 contraction and M29 Landau. Order estimate only.
    """
    eps = float(epsilon)
    if eps <= 0.0:
        raise ScopeViolationError(
            f"slow_manifold_distance_bound: requires epsilon > 0; got {epsilon!r}"
        )
    if not is_normally_hyperbolic(x):
        raise ScopeViolationError(
            f"slow_manifold_distance_bound: x={x!r} is not normally hyperbolic "
            f"(S'(x)={critical_manifold_S_prime(x)!r}); Fenichel O(ε) estimate "
            f"applies only away from folds"
        )
    return abs(eps)
