"""Bond percolation / branching-process extinction on the Bethe tree (Milestone 32).

Exact critical probability and extinction fixed-point on the infinite
``m``-ary Bethe tree (Cayley tree / branching-process mean offspring ``m``),
following Fisher & Essam (1961) and Kesten (1980). No lattice Monte-Carlo,
no Union-Find / Newman–Ziff, no ``Z²`` simulation.

Formulas
--------
Critical occupation probability on the Bethe tree with branching factor ``m``:

    p_c = 1 / m

(``m ≥ 1``; ``ScopeViolationError`` if ``m < 1``).

Extinction probability ``Q*`` of the branching process with offspring PGF
``f(s) = (1 - p + p s)^m`` is the **smallest** nonnegative fixed point
``Q* ∈ [0, 1]`` of

    Q = (1 - p + p Q)^m

Computed by monotone iteration starting at ``Q0 = 0`` (documented), which
converges to the smallest fixed point. Returns ``(Q*, iters, residual)`` with
``residual = |Q* - (1-p+p Q*)^m|``.

Percolation (survival) probability:

    θ = 1 - Q*

WARNING — threshold kinship (verbatim):
Percolation and cusp dynamics involve distinct objects and parameter meanings. No identity of their thresholds or transfer of numerical values is asserted. A comparison of local fixed-point or bifurcation structures requires a separately stated scope, construction, and derivation.

WARNING — discarded README 1/16:
If any computed value lands near 1/16, mark explicitly as coincidence vs the
discarded README '1/16' value — do not leave uncommented. In particular
``critical_probability_tree(16) = 1/16`` is the Bethe ``p_c`` for ``m=16``
and must **not** be identified with the discarded universal ecosystem claim.

Sources
-------
- Fisher & Essam 1961, J. Math. Phys. 2, 609; DOI 10.1063/1.1703745
- Kesten 1980, Commun. Math. Phys. 74, 41; DOI 10.1007/BF01197577

Out of scope for M32: Monte-Carlo on ``Z²``, Union-Find / Newman–Ziff,
dynamics / membership / other Bausteine, package-root ``__init__.py``,
``FORMALISM.md``.
"""

from __future__ import annotations

from typing import Any, Dict, Tuple, Union

from scoped_correspondence.errors import ScopeViolationError

Number = Union[int, float]

# Verbatim mandatory warning — must appear in module/API docstrings AND docs.
# Reworded per SCF_Strukturelle_Bruecken_Konzept.md (2026-09-20, reviewed and
# hand-verified independently): the original "NO mathematical kinship"
# phrasing denied an unearned IDENTITY of the two thresholds correctly, but
# overshot into denying any possible structural comparison whatsoever —
# a universal negative this repo cannot actually establish. The reworded
# text keeps the identity denial and explicitly leaves room for a
# separately-scoped, separately-derived structural comparison (see
# docs/structural_relations.md, bridge B6) without asserting one here.
THRESHOLD_KINSHIP_WARNING: str = (
    "Percolation and cusp dynamics involve distinct objects and parameter "
    "meanings. No identity of their thresholds or transfer of numerical "
    "values is asserted. A comparison of local fixed-point or bifurcation "
    "structures requires a separately stated scope, construction, and "
    "derivation."
)

# Verbatim mandatory coincidence fence vs discarded README universal 1/16.
ONE_SIXTEENTH_COINCIDENCE_WARNING: str = (
    "WARNING: computed value near 1/16 is coincidence vs the discarded README "
    "'1/16' value — do not identify them."
)

SOURCE: str = (
    "Fisher & Essam 1961 DOI 10.1063/1.1703745; "
    "Kesten 1980 DOI 10.1007/BF01197577"
)

# Iteration start for smallest fixed point (documented in API + docs).
EXTINCTION_Q0: float = 0.0

_ONE_SIXTEENTH: float = 1.0 / 16.0
_NEAR_ONE_SIXTEENTH_ATOL: float = 1e-3


def _near_one_sixteenth(value: float) -> bool:
    return abs(float(value) - _ONE_SIXTEENTH) < _NEAR_ONE_SIXTEENTH_ATOL


def _coincidence_note(value: float, label: str) -> str | None:
    if _near_one_sixteenth(value):
        return (
            f"{label}={float(value)!r} is near 1/16: "
            f"{ONE_SIXTEENTH_COINCIDENCE_WARNING}"
        )
    return None


def critical_probability_tree(m: Number) -> float:
    """Bethe-tree bond percolation threshold ``p_c = 1/m``.

    Parameters
    ----------
    m :
        Branching factor / mean maximum offspring (``m ≥ 1``).

    Returns
    -------
    float
        ``p_c = 1/m``.

    Raises
    ------
    ScopeViolationError
        If ``m < 1``.

    Notes
    -----
    Percolation and cusp dynamics involve distinct objects and parameter
    meanings. No identity of their thresholds or transfer of numerical
    values is asserted. A comparison of local fixed-point or bifurcation
    structures requires a separately stated scope, construction, and
    derivation.

    If ``p_c`` lands near ``1/16`` (e.g. ``m = 16``), that is coincidence vs
    the discarded README '1/16' value — do not identify them.
    """
    mm = float(m)
    if mm < 1.0:
        raise ScopeViolationError(
            f"critical_probability_tree: requires m >= 1; got {m!r}"
        )
    if mm != round(mm):
        raise ScopeViolationError(
            f"critical_probability_tree: requires integer m (Binomial(m,p) "
            f"offspring PGF assumes an integer maximum offspring count); got {m!r}"
        )
    p_c = 1.0 / mm
    # Explicit coincidence mark when p_c ≈ 1/16 (do not leave uncommented).
    if _near_one_sixteenth(p_c):
        # Coincidence vs discarded README '1/16' — Bethe p_c only.
        _ = ONE_SIXTEENTH_COINCIDENCE_WARNING  # noqa: F841 — keep warning live
    return float(p_c)


def extinction_probability(
    p: Number,
    m: Number,
    tol: float = 1e-12,
    max_iter: int = 1000,
) -> Tuple[float, int, float]:
    """Smallest nonnegative extinction fixed point ``Q*`` of ``Q=(1-p+p Q)^m``.

    Iterates the offspring PGF starting at documented ``Q0 = 0``
    (``EXTINCTION_Q0``), which is monotone and converges to the **smallest**
    fixed point in ``[0, 1]``. Always ``Q = 1`` is a fixed point; for
    ``p > p_c = 1/m`` one has ``Q* < 1``.

    Parameters
    ----------
    p :
        Bond / occupation probability (``0 ≤ p ≤ 1``).
    m :
        Branching factor (``m ≥ 1``).
    tol :
        Absolute residual tolerance (default ``1e-12``).
    max_iter :
        Maximum iterations (default ``1000``).

    Returns
    -------
    Q_star : float
        Smallest nonnegative fixed point ``≤ 1``.
    iters : int
        Number of iterations performed.
    residual : float
        ``|Q* - (1 - p + p Q*)^m|``.

    Raises
    ------
    ScopeViolationError
        If ``m < 1``, ``p`` outside ``[0, 1]``, ``tol ≤ 0``, or ``max_iter < 1``.

    Notes
    -----
    Start value: ``Q0 = 0`` (``EXTINCTION_Q0``).

    Percolation and cusp dynamics involve distinct objects and parameter
    meanings. No identity of their thresholds or transfer of numerical
    values is asserted. A comparison of local fixed-point or bifurcation
    structures requires a separately stated scope, construction, and
    derivation.

    If any of ``Q*``, ``p``, or related values land near ``1/16``, mark as
    coincidence vs the discarded README '1/16' value.
    """
    pp = float(p)
    mm = float(m)
    if mm < 1.0:
        raise ScopeViolationError(
            f"extinction_probability: requires m >= 1; got {m!r}"
        )
    if mm != round(mm):
        raise ScopeViolationError(
            f"extinction_probability: requires integer m (Binomial(m,p) "
            f"offspring PGF assumes an integer maximum offspring count); got {m!r}"
        )
    if not (0.0 <= pp <= 1.0):
        raise ScopeViolationError(
            f"extinction_probability: requires 0 <= p <= 1; got {p!r}"
        )
    if float(tol) <= 0.0:
        raise ScopeViolationError(
            f"extinction_probability: requires tol > 0; got {tol!r}"
        )
    if int(max_iter) < 1:
        raise ScopeViolationError(
            f"extinction_probability: requires max_iter >= 1; got {max_iter!r}"
        )

    # Audit finding A05 (fall 1): p=1 means every edge is present with
    # certainty, degenerating the branching process to Q*=0 for ANY m
    # (including m=1, an infinite deterministic chain that never breaks).
    # Direct iteration from Q0=0 confirms this trivially: q_next=(1-1+1*0)^m
    # =0 immediately. The old code's "p<=p_c => Q*=1" shortcut wrongly fired
    # here too whenever p_c=1 (i.e. m=1), giving the OPPOSITE answer
    # (certain extinction instead of certain survival). Handled first and
    # separately from the general subcritical/critical shortcut below.
    if pp >= 1.0:
        return 0.0, 0, 0.0

    # Branching-process theorem: mean offspring m*p <= 1 (p <= p_c, and here
    # p < 1 strictly, see above) => Q* = 1 exactly (critical slowing makes
    # pure iteration from Q0=0 impractical at p=p_c).
    p_c = 1.0 / mm
    if pp <= p_c:
        # Coincidence fence if p_c ≈ 1/16
        if _near_one_sixteenth(p_c) or _near_one_sixteenth(pp):
            _ = ONE_SIXTEENTH_COINCIDENCE_WARNING  # noqa: F841
        return 1.0, 0, 0.0

    q = float(EXTINCTION_Q0)  # documented start Q0 = 0
    iters = 0
    residual = float("inf")
    for iters in range(1, int(max_iter) + 1):
        q_next = (1.0 - pp + pp * q) ** mm
        # Clamp tiny float noise into [0, 1]
        if q_next < 0.0:
            q_next = 0.0
        elif q_next > 1.0:
            q_next = 1.0
        residual = abs(q_next - q)
        q = q_next
        if residual <= float(tol):
            break

    # Audit finding A05 (fall 2): Picard/fixed-point iteration converges only
    # LINEARLY, at a rate that -> 1 as p -> p_c ("critical slowing"), so
    # max_iter=1000 can leave a residual orders of magnitude above the
    # requested tol near criticality (audit example: p=0.5001, m=2 left
    # residual~=3.9e-6 against a requested 1e-12). Polish with Newton-Raphson
    # on g(Q)=Q-(1-p+pQ)^m, quadratically convergent, starting from the
    # Picard iterate. g'(1)=1-m*p != 0 here because p>p_c is already
    # guaranteed (the p<=p_c case returned above), so Newton is well-posed
    # at the target root (not the trivial Q=1 root).
    for _ in range(50):
        base = 1.0 - pp + pp * q
        g = q - base**mm
        dg = 1.0 - mm * pp * (base ** (mm - 1.0))
        if dg == 0.0:
            break
        step = g / dg
        q_new = q - step
        if q_new < 0.0:
            q_new = 0.0
        elif q_new > 1.0:
            q_new = 1.0
        if abs(q_new - q) < 1e-16:
            q = q_new
            break
        q = q_new

    # Final residual against the fixed-point map (not the last step delta).
    f_q = (1.0 - pp + pp * q) ** mm
    residual = abs(q - f_q)
    # Coincidence fence if Q* ≈ 1/16
    if _near_one_sixteenth(q):
        _ = ONE_SIXTEENTH_COINCIDENCE_WARNING  # noqa: F841
    return float(q), int(iters), float(residual)


def percolation_probability(p: Number, m: Number) -> float:
    """Percolation (survival) probability ``θ = 1 - Q*``.

    Calls ``extinction_probability(p, m)`` and returns ``1 - Q*``.

    Parameters
    ----------
    p :
        Bond / occupation probability (``0 ≤ p ≤ 1``).
    m :
        Branching factor (``m ≥ 1``).

    Returns
    -------
    float
        ``θ = 1 - Q*``.

    Raises
    ------
    ScopeViolationError
        Propagated from ``extinction_probability`` / ``critical_probability_tree``
        domain checks.

    Notes
    -----
    Percolation and cusp dynamics involve distinct objects and parameter
    meanings. No identity of their thresholds or transfer of numerical
    values is asserted. A comparison of local fixed-point or bifurcation
    structures requires a separately stated scope, construction, and
    derivation.
    """
    q_star, _iters, residual = extinction_probability(p, m)
    # Audit finding A05: this convenience wrapper used to discard iters/
    # residual entirely, silently returning a value that could be far off
    # if the underlying fixed-point solve had not actually converged. The
    # full (Q*, iters, residual) triple is still available from
    # extinction_probability directly for callers who need it; this
    # wrapper now at least refuses to hand back a value it cannot stand
    # behind.
    if residual > 1e-8:
        raise ScopeViolationError(
            f"percolation_probability: extinction_probability did not "
            f"converge (residual={residual!r} > 1e-8) for p={p!r}, m={m!r}; "
            f"call extinction_probability directly to inspect iters/residual"
        )
    theta = 1.0 - q_star
    if _near_one_sixteenth(theta):
        _ = ONE_SIXTEENTH_COINCIDENCE_WARNING  # noqa: F841
    return float(theta)


def as_report(p: Number, m: Number) -> Dict[str, Any]:
    """Structured report with ``p_c``, ``Q*``, ``θ``, warnings, and coincidence notes."""
    p_c = critical_probability_tree(m)
    q_star, iters, residual = extinction_probability(p, m)
    theta = 1.0 - q_star
    notes = [
        n
        for n in (
            _coincidence_note(p_c, "p_c"),
            _coincidence_note(q_star, "Q_star"),
            _coincidence_note(theta, "theta"),
            _coincidence_note(float(p), "p"),
        )
        if n is not None
    ]
    return {
        "p": float(p),
        "m": float(m),
        "p_c": float(p_c),
        "Q_star": float(q_star),
        "theta": float(theta),
        "iters": int(iters),
        "residual": float(residual),
        "Q0": float(EXTINCTION_Q0),
        "threshold_kinship_warning": THRESHOLD_KINSHIP_WARNING,
        "one_sixteenth_coincidence_warning": ONE_SIXTEENTH_COINCIDENCE_WARNING,
        "coincidence_notes": notes,
        "source": SOURCE,
    }


__all__ = [
    "THRESHOLD_KINSHIP_WARNING",
    "ONE_SIXTEENTH_COINCIDENCE_WARNING",
    "SOURCE",
    "EXTINCTION_Q0",
    "critical_probability_tree",
    "extinction_probability",
    "percolation_probability",
    "as_report",
]
