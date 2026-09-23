"""Profile likelihood for structural / practical identifiability (Milestone 20).

Implements the profile-likelihood construction of Raue et al. 2009
(DOI 10.1093/bioinformatics/btp358): for a parameter component ``theta_i``,

    chi2_PL(theta_i) = min_{theta_j, j != i} chi2(theta)

Practical non-identifiability appears as a **flat** profile (chi2_PL stays
near its minimum across the scanned grid); structural / practical
identifiability appears as a **curved** profile that rises above a
likelihood-ratio threshold, yielding a finite confidence interval.

This module is intentionally restricted to **algebraic** ``chi2`` demos
(product non-id; 1-D quadratic id). It does **not**:
  - call ODE integrators or general NLP / global solvers beyond a 1-D
    golden-section / grid refine over free parameters;
  - equate profile likelihood to Jacobian rank / SVD formulas in
    ``identifiability.core``;
  - mutate ``identifiability/core.py``, package-root ``__init__.py``,
    ``FORMALISM.md``, or the layer docs.
"""

from __future__ import annotations

import math
from typing import Callable, Dict, List, Optional, Sequence, Tuple, Union

from scoped_correspondence.errors import ScopeViolationError

Array1D = Sequence[float]
Profile = List[Tuple[float, float]]  # (fixed_value, chi2_min)

SOURCE = (
    "Raue, Kreutz, Maiwald, Bachmann, Schilling, Klingmüller & Timmer 2009, "
    "Structural and practical identifiability analysis of partially observed "
    "dynamical models by exploiting the profile likelihood, Bioinformatics; "
    "DOI 10.1093/bioinformatics/btp358"
)

_CLASS_FLAT = "flat"
_CLASS_IDENTIFIABLE = "identifiable"
_CLASS_UNRESOLVED = "unresolved_in_scan"

# Audit finding A07: a finite scan can only ever show that chi2 did not
# visibly curve WITHIN the sampled window — it can never prove the profile
# is flat beyond that window. A variance-based flatness test compares its
# statistic to an ABSOLUTE atol, so shrinking the scan span always
# eventually drives the observed variance below any fixed atol (variance
# shrinks quadratically with the span for a smooth chi2), even for a
# genuinely curved, fully identifiable parameter (audit example:
# chi2=theta^2 scanned at {-0.001,0,0.001} was classified "flat" although
# the true global interval at threshold=1 is exactly [-1,1]). Below this
# default minimum half-span, classify_identifiability refuses to call
# anything "flat" and reports "unresolved_in_scan" instead — distinct from
# a genuine flat_profile finding on a properly wide scan (see the M20
# non-identifiable product worked example, span=4, still correctly "flat").
_MIN_RESOLVABLE_SPAN = 1e-2

# Golden-section ratio for 1-D free-parameter refine (algebraic cases only).
_PHI = (1.0 + math.sqrt(5.0)) / 2.0
_RES_PHI = 2.0 - _PHI


def _as_theta(theta: Sequence[float]) -> List[float]:
    vals = [float(x) for x in theta]
    if not vals:
        raise ScopeViolationError("theta must be non-empty")
    for v in vals:
        if not math.isfinite(v):
            raise ScopeViolationError(f"theta components must be finite; got {v!r}")
    return vals


def _chi2_at(
    chi2_fn: Callable[[Sequence[float]], float],
    theta: Sequence[float],
) -> float:
    val = float(chi2_fn(theta))
    if not math.isfinite(val):
        raise ScopeViolationError(f"chi2_fn returned non-finite value {val!r}")
    return val


def _minimize_1d_free(
    chi2_fn: Callable[[Sequence[float]], float],
    theta_base: List[float],
    free_index: int,
    search_lo: float,
    search_hi: float,
    n_grid: int = 41,
    refine_iters: int = 40,
) -> float:
    """Minimize chi2 over one free coordinate by coarse grid + golden refine.

    Algebraic-case helper only — not a general NLP / ODE solver.
    """
    if not (math.isfinite(search_lo) and math.isfinite(search_hi)):
        raise ScopeViolationError("free-parameter search bounds must be finite")
    if search_hi < search_lo:
        search_lo, search_hi = search_hi, search_lo
    if search_hi == search_lo:
        theta = list(theta_base)
        theta[free_index] = search_lo
        return _chi2_at(chi2_fn, theta)

    best_x = search_lo
    best_y = math.inf
    n = max(3, int(n_grid))
    for k in range(n):
        x = search_lo + (search_hi - search_lo) * k / (n - 1)
        theta = list(theta_base)
        theta[free_index] = x
        y = _chi2_at(chi2_fn, theta)
        if y < best_y:
            best_y = y
            best_x = x

    # Local golden-section refine in a window around the grid best.
    span = max(abs(search_hi - search_lo) * 0.15, 1e-6)
    a = max(search_lo, best_x - span)
    b = min(search_hi, best_x + span)
    if b <= a:
        return float(best_y)

    c = a + _RES_PHI * (b - a)
    d = b - _RES_PHI * (b - a)

    def f(x: float) -> float:
        theta = list(theta_base)
        theta[free_index] = x
        return _chi2_at(chi2_fn, theta)

    fc = f(c)
    fd = f(d)
    for _ in range(int(refine_iters)):
        if fc < fd:
            b, d, fd = d, c, fc
            c = a + _RES_PHI * (b - a)
            fc = f(c)
        else:
            a, c, fc = c, d, fd
            d = b - _RES_PHI * (b - a)
            fd = f(d)
        if abs(b - a) < 1e-12 * (1.0 + abs(a) + abs(b)):
            break
    return float(min(fc, fd, best_y))


def _free_search_bounds(
    theta_init: List[float],
    free_index: int,
) -> Tuple[float, float]:
    """Heuristic finite window around the free init for algebraic demos."""
    x0 = float(theta_init[free_index])
    # Cover the non-id product demo (theta2 ~ 6/theta1 for theta1 in 1..5)
    # and ordinary quadratic basins around the init.
    radius = max(20.0, 5.0 * abs(x0) + 5.0)
    return (x0 - radius, x0 + radius)


def profile_parameter(
    chi2_fn: Callable[[Sequence[float]], float],
    theta_fixed_index: int,
    theta_init: Sequence[float],
    fixed_values: Sequence[float],
) -> Profile:
    """Profile one parameter: return ``[(fixed_value, chi2_min), ...]``.

    Parameters
    ----------
    chi2_fn :
        Callable ``theta -> chi2`` (lower is better). Algebraic demos only.
    theta_fixed_index :
        Index ``i`` of the profiled component.
    theta_init :
        Initial / nominal full parameter vector (length ``p >= 1``).
    fixed_values :
        Grid of fixed values for ``theta[i]``.

    Returns
    -------
    list of (fixed_value, chi2_min)
        For each grid point, ``chi2_min = min_{j != i} chi2(theta)`` with
        ``theta[i]`` held fixed. When ``p == 1`` there are no free
        parameters and ``chi2_min = chi2([fixed_value])``.

    Notes
    -----
    Free-parameter minimization is a **1-D** grid + golden-section refine
    when exactly one free coordinate exists. Zero free coordinates are
    evaluated directly. Two or more free coordinates are refused
    (``ScopeViolationError``) — out of M20 algebraic scope; no general NLP.
    """
    if not callable(chi2_fn):
        raise ScopeViolationError("chi2_fn must be callable")
    theta0 = _as_theta(theta_init)
    p = len(theta0)
    i = int(theta_fixed_index)
    if i < 0 or i >= p:
        raise ScopeViolationError(
            f"theta_fixed_index={theta_fixed_index!r} out of range for p={p}"
        )
    if len(fixed_values) < 1:
        raise ScopeViolationError("fixed_values must be non-empty")

    free_indices = [j for j in range(p) if j != i]
    if len(free_indices) > 1:
        raise ScopeViolationError(
            "profile_parameter: M20 algebraic scope allows at most one free "
            f"parameter; got {len(free_indices)} free indices {free_indices}. "
            "No general NLP / ODE solver."
        )

    out: Profile = []
    for raw in fixed_values:
        fv = float(raw)
        if not math.isfinite(fv):
            raise ScopeViolationError(f"fixed_values must be finite; got {raw!r}")
        base = list(theta0)
        base[i] = fv
        if not free_indices:
            chi2_min = _chi2_at(chi2_fn, base)
        else:
            j = free_indices[0]
            lo, hi = _free_search_bounds(theta0, j)
            # Also try a wider positive-side window when init is positive
            # (covers theta2 = 6/theta1 for theta1 in {1..5}).
            chi2_min = _minimize_1d_free(chi2_fn, base, j, lo, hi)
            if lo > 0.05 or hi > 0.05:
                lo2, hi2 = 0.05, max(hi, 40.0)
                chi2_min = min(
                    chi2_min,
                    _minimize_1d_free(chi2_fn, base, j, lo2, hi2),
                )
            if lo < -0.05:
                lo3, hi3 = min(lo, -40.0), -0.05
                chi2_min = min(
                    chi2_min,
                    _minimize_1d_free(chi2_fn, base, j, lo3, hi3),
                )
        out.append((fv, float(chi2_min)))
    return out


def classify_identifiability(
    profile: Sequence[Tuple[float, float]],
    atol: float = 1e-8,
    min_resolvable_span: float = _MIN_RESOLVABLE_SPAN,
) -> str:
    """Classify a profile as ``"flat"``, ``"identifiable"``, or
    ``"unresolved_in_scan"``.

    Uses the sample variance of the profiled ``chi2_min`` values:

    - ``"unresolved_in_scan"`` if the scanned grid's span
      (``max(fixed_value) - min(fixed_value)``) is below
      ``min_resolvable_span`` — a scan this narrow cannot distinguish a
      genuinely flat profile from a curved one whose curvature only shows
      up over a wider window (audit finding A07: chi2=theta^2 scanned at
      {-0.001,0,0.001} has variance ~2e-13, far below any reasonable
      atol, despite being fully identifiable with global interval [-1,1]
      at threshold=1). This check runs BEFORE the variance test, on the
      grid alone, regardless of the observed chi2 values.
    - ``"flat"`` if ``Var(chi2_min) < atol`` on a sufficiently wide scan
      (practically non-identifiable on the scanned grid — Raue et al.
      2009 flat-profile signature);
    - ``"identifiable"`` otherwise.

    Parameters
    ----------
    profile :
        Output of :func:`profile_parameter`.
    atol :
        Absolute variance threshold (default ``1e-8``).
    min_resolvable_span :
        Minimum grid half-span (``max(x)-min(x)``) required before a
        "flat" call is trusted (default ``1e-2``, see module notes).
    """
    if len(profile) < 2:
        raise ScopeViolationError(
            "classify_identifiability: need at least 2 profile points"
        )
    atol_f = float(atol)
    if not math.isfinite(atol_f) or atol_f < 0.0:
        raise ScopeViolationError(f"atol must be finite and >= 0; got {atol!r}")
    span_f = float(min_resolvable_span)
    if not math.isfinite(span_f) or span_f < 0.0:
        raise ScopeViolationError(
            f"min_resolvable_span must be finite and >= 0; got {min_resolvable_span!r}"
        )

    xs = [float(x) for x, _ in profile]
    ys = [float(chi2) for _, chi2 in profile]
    for y in ys:
        if not math.isfinite(y):
            raise ScopeViolationError(
                f"classify_identifiability: non-finite chi2_min in profile: {y!r}"
            )

    scan_span = max(xs) - min(xs)
    if scan_span < span_f:
        return _CLASS_UNRESOLVED

    n = len(ys)
    mean = sum(ys) / n
    var = sum((y - mean) ** 2 for y in ys) / n  # population variance on the grid
    if var < atol_f:
        return _CLASS_FLAT
    return _CLASS_IDENTIFIABLE


def likelihood_interval(
    profile: Sequence[Tuple[float, float]],
    threshold: float,
) -> Dict[str, object]:
    """Likelihood-ratio confidence set from a profile.

    Following Raue et al. 2009, the confidence set at threshold ``Delta`` is

        { theta_i  |  chi2_PL(theta_i) - chi2*  <=  Delta }

    where ``chi2* = min chi2_PL`` on the supplied grid.

    Flat profiles (variance of ``chi2_min`` below a tight default) are
    reported as **explicitly unbounded** — no finite lower/upper endpoint.

    CORRECTION (2026-09-23, external follow-up review by Astra,
    SCF_Followup_1231f64.md): ``unbounded=True`` is set for THREE distinct
    reasons (``flat_profile``, ``open_at_grid_boundary``,
    ``unresolved_in_scan``), but only ``flat_profile`` is an ESTABLISHED
    finding (a wide-enough scan whose variance genuinely fails to
    distinguish from flat) — the other two mean only "no finite endpoint
    was found WITHIN this scan", which is a weaker, inconclusive claim, not
    a positive finding of unboundedness. The new ``established_unbounded``
    field makes this distinction machine-readable: ``True`` only for
    ``flat_profile``; ``False`` for ``open_at_grid_boundary`` and
    ``unresolved_in_scan`` (and, trivially, for the bounded case).
    ``unbounded`` itself is UNCHANGED for backward compatibility (it still
    means "no finite two-sided interval was resolved from this call") —
    callers that need the stronger, established claim should check
    ``established_unbounded``, not ``unbounded``, per Astra's point that a
    scan-boundary status "should not simultaneously assert an established
    unboundedness."

    Returns
    -------
    dict
        ``bounded`` (bool), ``lower`` / ``upper`` (float or None),
        ``chi2_star``, ``threshold``, ``values_in_set`` (list of fixed
        values inside the set), ``unbounded`` (bool), ``established_unbounded``
        (bool — True only for ``unbounded_reason == "flat_profile"``),
        ``unbounded_reason`` (``\"flat_profile\"`` | ``\"open_at_grid_boundary\"``
        | ``\"unresolved_in_scan\"`` | None), ``classification``, ``source``.
    """
    if len(profile) < 1:
        raise ScopeViolationError("likelihood_interval: empty profile")
    thr = float(threshold)
    if not math.isfinite(thr) or thr < 0.0:
        raise ScopeViolationError(
            f"likelihood_interval: threshold must be finite and >= 0; got {threshold!r}"
        )

    xs = [float(x) for x, _ in profile]
    ys = [float(y) for _, y in profile]
    for y in ys:
        if not math.isfinite(y):
            raise ScopeViolationError(
                f"likelihood_interval: non-finite chi2_min in profile: {y!r}"
            )

    chi2_star = min(ys)
    # Points inside the LR set
    in_set = [xs[k] for k in range(len(xs)) if ys[k] - chi2_star <= thr + 1e-15]

    classification = (
        classify_identifiability(profile, atol=1e-8)
        if len(profile) >= 2
        else _CLASS_IDENTIFIABLE
    )

    if classification == _CLASS_UNRESOLVED:
        return {
            "bounded": False,
            "unbounded": True,
            "established_unbounded": False,
            "unbounded_reason": "unresolved_in_scan",
            "lower": None,
            "upper": None,
            "chi2_star": chi2_star,
            "threshold": thr,
            "values_in_set": list(in_set),
            "classification": classification,
            "source": SOURCE,
            "note": (
                "scan span too narrow to distinguish a flat profile from a "
                "curved one whose curvature only appears over a wider "
                "window (audit finding A07) — this is NOT a claim that the "
                "parameter is non-identifiable, only that this scan cannot "
                "tell; widen fixed_values to resolve"
            ),
        }

    if classification == _CLASS_FLAT:
        return {
            "bounded": False,
            "unbounded": True,
            "established_unbounded": True,
            "unbounded_reason": "flat_profile",
            "lower": None,
            "upper": None,
            "chi2_star": chi2_star,
            "threshold": thr,
            "values_in_set": list(in_set),
            "classification": classification,
            "source": SOURCE,
        }

    if not in_set:
        # Threshold too tight relative to grid — empty finite set.
        return {
            "bounded": True,
            "unbounded": False,
            "established_unbounded": False,
            "unbounded_reason": None,
            "lower": None,
            "upper": None,
            "chi2_star": chi2_star,
            "threshold": thr,
            "values_in_set": [],
            "classification": classification,
            "source": SOURCE,
            "empty": True,
        }

    lower = min(in_set)
    upper = max(in_set)

    # Open at grid boundary: confidence set touches either endpoint of the
    # scanned grid AND that endpoint's chi2 is still within threshold →
    # interval may continue outside the grid (practically unbounded on side).
    x_min_grid = min(xs)
    x_max_grid = max(xs)
    open_lo = abs(lower - x_min_grid) <= 1e-15 and (
        ys[xs.index(lower)] - chi2_star <= thr + 1e-15
    )
    # xs.index is fine for unique grids; for duplicates use first match OK.
    open_hi = abs(upper - x_max_grid) <= 1e-15 and (
        ys[xs.index(upper)] - chi2_star <= thr + 1e-15
    )

    if open_lo or open_hi:
        return {
            "bounded": False,
            "unbounded": True,
            "established_unbounded": False,
            "unbounded_reason": "open_at_grid_boundary",
            "lower": None if open_lo else lower,
            "upper": None if open_hi else upper,
            "chi2_star": chi2_star,
            "threshold": thr,
            "values_in_set": list(in_set),
            "classification": classification,
            "source": SOURCE,
            "open_lower": open_lo,
            "open_upper": open_hi,
        }

    return {
        "bounded": True,
        "unbounded": False,
        "established_unbounded": False,
        "unbounded_reason": None,
        "lower": lower,
        "upper": upper,
        "chi2_star": chi2_star,
        "threshold": thr,
        "values_in_set": list(in_set),
        "classification": classification,
        "source": SOURCE,
    }


__all__ = [
    "SOURCE",
    "profile_parameter",
    "classify_identifiability",
    "likelihood_interval",
]
