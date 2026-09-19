"""Floquet multipliers for a given 2×2 monodromy matrix (Milestone 34).

Given a monodromy matrix ``M = Φ(T)`` of the variational equation along a
``T``-periodic orbit, the **Floquet multipliers** are the eigenvalues ``μ``
of ``M``. They solve the characteristic polynomial

    μ² − (tr M) μ + (det M) = 0

for the 2×2 case. Orbital stability is read from the moduli: asymptotic
orbital stability requires all multipliers inside the unit disk (except the
trivial ``μ = 1`` of an autonomous phase direction, when present);
instability follows from any ``|μ| > 1``; multipliers on the unit circle
yield neutral / marginal behaviour.

This module accepts a **given** monodromy ``M`` and does **not** integrate
any ODE / variational equation. It is **not** M14 contraction analysis (plain: not M14)
(Lohmiller & Slotine metric contraction of the cusp field): Floquet is the
periodic-orbit linearisation, while M14 is global Euclidean contraction of
an equilibrium normal form. ``dynamics/core.py`` is not edited.

Primary source
--------------
G. Floquet, *Sur les équations différentielles linéaires à coefficients
périodiques*, Ann. sci. Éc. Norm. Sup. **12**, 47–88 (1883);
DOI 10.24033/asens.220.

Optional modern reference
-------------------------
R. Castelli & J.-P. Lessard, *Rigorous Numerics in Floquet Theory…*,
SIAM J. Appl. Dyn. Syst. (2013); DOI 10.1137/120873960.
"""

from __future__ import annotations

from typing import Sequence, Tuple, Union

import numpy as np

from scoped_correspondence.errors import ScopeViolationError

SOURCE = (
    "Floquet 1883, Sur les équations différentielles linéaires à "
    "coefficients périodiques, Ann. sci. Éc. Norm. Sup. 12, 47–88; "
    "DOI 10.24033/asens.220"
)

SOURCE_OPTIONAL = (
    "Castelli & Lessard 2013, Rigorous Numerics in Floquet Theory, "
    "SIAM J. Appl. Dyn. Syst.; DOI 10.1137/120873960"
)

# Classification labels (verbatim API contract for verify / docs)
STABILITY_STABLE = "stable"
STABILITY_UNSTABLE = "unstable"
STABILITY_NEUTRAL = "neutral"

_DEFAULT_ASSUMPTIONS: tuple[str, ...] = (
    "2×2 monodromy only — higher-dimensional Floquet out of scope (M34)",
    "NO ODE / variational integrator — M is given by the caller",
    "NOT M14 contraction (Lohmiller & Slotine); Floquet = periodic-orbit "
    "linearisation via eigenvalues of monodromy",
    "dynamics/core.py not edited; package-root __init__ not touched",
    "classify: stable iff all |μ|<1; unstable iff some |μ|>1; else neutral "
    "(includes double μ=1 / unit-circle cases — never mislabelled stable)",
)

ArrayLike = Union[np.ndarray, Sequence[Sequence[float]]]


def _as_2x2(M: ArrayLike) -> np.ndarray:
    """Validate and return a float 2×2 ndarray; raise ScopeViolationError else."""
    arr = np.asarray(M, dtype=float)
    if arr.ndim != 2 or arr.shape != (2, 2):
        raise ScopeViolationError(
            f"floquet_multipliers: M must be 2×2; got shape {getattr(arr, 'shape', None)!r}"
        )
    if not np.all(np.isfinite(arr)):
        raise ScopeViolationError(
            "floquet_multipliers: M entries must be finite"
        )
    return arr


def characteristic_polynomial_coeffs(M: ArrayLike) -> Tuple[float, float]:
    """Return ``(tr, det)`` so the char poly is ``μ² − tr·μ + det = 0``."""
    A = _as_2x2(M)
    tr = float(A[0, 0] + A[1, 1])
    det = float(A[0, 0] * A[1, 1] - A[0, 1] * A[1, 0])
    return tr, det


def multipliers_from_trace_det(tr: float, det: float) -> np.ndarray:
    """Solve ``μ² − tr·μ + det = 0``; return length-2 complex ndarray."""
    tr_f = float(tr)
    det_f = float(det)
    disc = tr_f * tr_f - 4.0 * det_f
    # Use complex sqrt so real negative discriminant becomes ±i cleanly
    sqrt_disc = np.sqrt(complex(disc))
    mu_plus = (tr_f + sqrt_disc) / 2.0
    mu_minus = (tr_f - sqrt_disc) / 2.0
    return np.asarray([mu_plus, mu_minus], dtype=complex)


def floquet_multipliers(M: ArrayLike) -> np.ndarray:
    """Floquet multipliers = eigenvalues of the given 2×2 monodromy ``M``.

    Computed by solving the characteristic polynomial
    ``μ² − (tr M) μ + (det M) = 0`` and cross-checked against
    ``numpy.linalg.eigvals(M)``. No ODE integrator is used.

    Parameters
    ----------
    M :
        Real 2×2 monodromy matrix ``Φ(T)``.

    Returns
    -------
    np.ndarray
        Length-2 complex array of multipliers ``μ`` (order from the
        quadratic formula: ``(tr ± √(tr²−4 det))/2``).

    Raises
    ------
    ScopeViolationError
        If ``M`` is not a finite 2×2 array.

    Notes
    -----
    This is **not** M14 contraction analysis. Source: Floquet 1883,
    DOI 10.24033/asens.220 (optional: Castelli & Lessard 2013,
    DOI 10.1137/120873960).
    """
    A = _as_2x2(M)
    tr, det = characteristic_polynomial_coeffs(A)
    mu_char = multipliers_from_trace_det(tr, det)
    mu_eig = np.linalg.eigvals(A)
    # Cross-check: multisets agree (sort by real then imag)
    a = sorted(mu_char, key=lambda z: (z.real, z.imag))
    b = sorted(mu_eig, key=lambda z: (complex(z).real, complex(z).imag))
    for za, zb in zip(a, b):
        if abs(za - zb) > 1e-9:
            raise ScopeViolationError(
                f"floquet_multipliers: char-poly vs eigvals mismatch: "
                f"{mu_char!r} vs {mu_eig!r}"
            )
    return mu_char


def classify_orbital_stability(
    multipliers: Sequence[complex],
    *,
    atol: float = 1e-9,
    has_known_phase_mode: bool = False,
) -> str:
    """Classify orbital stability from Floquet-multiplier moduli alone.

    Rules (strict; the double-``μ=1`` edge is **neutral**, never ``stable``):

    - ``unstable`` — some ``|μ| > 1 + atol``
    - ``stable`` — all ``|μ| < 1 - atol``
    - ``neutral`` — otherwise (all ``|μ| ≤ 1`` and at least one ``|μ| ≈ 1``,
      including the area-preserving unit-circle case and the double root
      ``μ = 1`` when ``tr = 2``, ``det = 1``)

    Audit finding A08 (multipliers-only limitation): given only the
    multipliers (no matrix), this function **cannot** distinguish a
    diagonalizable repeated unit eigenvalue (bounded) from a non-trivial
    Jordan block (unbounded polynomial growth, e.g.
    ``M=[[1,1],[0,1]]``, both ``μ=1``, yet ``M^n`` has an unbounded
    off-diagonal entry) — that requires the actual matrix, see
    ``classify_orbital_stability_matrix``. This function alone therefore
    stays conservative and reports ``"neutral"`` for ANY unit-modulus
    multiplier; it never claims ``"stable"`` in that case, so it cannot
    silently certify the Jordan-block example as bounded.

    Audit finding A08 (autonomous phase mode): for an autonomous
    system's periodic orbit, exactly one multiplier is always trivially
    ``μ=1`` (the flow direction) and carries no information about
    transverse stability. Passing ``has_known_phase_mode=True`` tells
    this function that EXACTLY ONE multiplier equal to ``+1`` (not just
    ``|μ|=1`` generally) is that known trivial mode, and classification
    is then based on the REMAINING multipliers only. Without this flag
    (the default), a ``μ=1`` is treated the conservative way, as an
    unannotated unit-modulus multiplier — i.e. ``"neutral"``, not
    ``"stable"``, exactly as before.

    Parameters
    ----------
    multipliers :
        Iterable of complex Floquet multipliers.
    atol :
        Absolute tolerance for the unit-circle boundary.
    has_known_phase_mode :
        If ``True``, exactly one multiplier must equal ``+1`` (within
        ``atol``) and is excluded from the unit-circle check as the
        known autonomous phase direction; raises ``ScopeViolationError``
        if zero or more than one multiplier qualifies (ambiguous — this
        function will not guess which one is "the" phase mode).

    Returns
    -------
    str
        One of ``"stable"``, ``"unstable"``, ``"neutral"``.
    """
    mults = [complex(m) for m in multipliers]
    if not mults:
        raise ScopeViolationError(
            "classify_orbital_stability: empty multipliers"
        )
    if has_known_phase_mode:
        phase_idx = [
            i for i, m in enumerate(mults)
            if abs(m.imag) <= atol and abs(m.real - 1.0) <= atol
        ]
        if len(phase_idx) != 1:
            raise ScopeViolationError(
                "classify_orbital_stability: has_known_phase_mode=True "
                f"requires exactly one multiplier == +1 (within atol); "
                f"found {len(phase_idx)} candidates in {mults!r}"
            )
        mults = [m for i, m in enumerate(mults) if i != phase_idx[0]]
        if not mults:
            # Only the trivial phase mode existed (e.g. a 1x1 case) —
            # nothing transverse left to be unstable in.
            return STABILITY_STABLE

    mods = [abs(m) for m in mults]
    if any(r > 1.0 + atol for r in mods):
        return STABILITY_UNSTABLE
    if all(r < 1.0 - atol for r in mods):
        return STABILITY_STABLE
    return STABILITY_NEUTRAL


def has_nontrivial_jordan_block(M: ArrayLike, atol: float = 1e-9) -> bool:
    """True iff the 2×2 ``M`` has a repeated eigenvalue but is NOT diagonal-
    izable there (a genuine Jordan block, causing unbounded polynomial
    growth of ``M**n`` even though ``|μ|=1`` exactly for that eigenvalue).

    For a 2×2 matrix with a repeated eigenvalue ``λ`` (``tr=2λ``,
    ``det=λ²``), ``M`` is diagonalizable there iff ``M == λI`` exactly;
    any other ``M`` with that trace/det is a non-trivial Jordan block
    (audit example: ``M=[[1,1],[0,1]]``, ``λ=1``, ``M != I``).
    """
    A = _as_2x2(M)
    tr, det = characteristic_polynomial_coeffs(A)
    disc = tr * tr - 4.0 * det
    if abs(disc) > atol:
        return False  # distinct eigenvalues — no repeated root, no Jordan block
    lam = tr / 2.0
    return bool(np.max(np.abs(A - lam * np.eye(2))) > atol)


def classify_orbital_stability_matrix(
    M: ArrayLike,
    *,
    atol: float = 1e-9,
    has_known_phase_mode: bool = False,
) -> str:
    """Matrix-aware orbital-stability classification (recommended over the
    multipliers-only ``classify_orbital_stability`` whenever ``M`` itself
    is available).

    Computes multipliers via ``floquet_multipliers(M)`` and additionally
    checks for a non-trivial Jordan block at a repeated unit-modulus
    eigenvalue (``has_nontrivial_jordan_block``) — audit finding A08: a
    repeated ``μ=1`` alone is NOT sufficient evidence of bounded/neutral
    behaviour if the matrix is not actually diagonalizable there, since
    ``M**n`` then grows polynomially without bound. Such a case is
    reported ``"unstable"``, never ``"neutral"``.
    """
    A = _as_2x2(M)
    mu = floquet_multipliers(A)
    tr, det = characteristic_polynomial_coeffs(A)
    disc = tr * tr - 4.0 * det
    if abs(disc) <= atol and abs(abs(tr / 2.0) - 1.0) <= atol and has_nontrivial_jordan_block(A, atol=atol):
        return STABILITY_UNSTABLE
    return classify_orbital_stability(mu, atol=atol, has_known_phase_mode=has_known_phase_mode)


def monodromy_from_trace_det(tr: float, det: float) -> np.ndarray:
    """Companion monodromy with given trace/det (char poly ``μ²−tr μ+det``).

    Returns ``[[0, -det], [1, tr]]``. Convenience for hand-checkable examples;
    not required by the public M34 API surface beyond tests/docs.
    """
    return np.asarray([[0.0, -float(det)], [1.0, float(tr)]], dtype=float)


__all__ = [
    "SOURCE",
    "SOURCE_OPTIONAL",
    "STABILITY_STABLE",
    "STABILITY_UNSTABLE",
    "STABILITY_NEUTRAL",
    "characteristic_polynomial_coeffs",
    "multipliers_from_trace_det",
    "floquet_multipliers",
    "classify_orbital_stability",
    "monodromy_from_trace_det",
]
