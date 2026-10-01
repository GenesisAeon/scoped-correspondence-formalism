"""Identifiability counterexamples and interventions (Paket MU4, plan §7).

Built on the J6 layer: unwrapped (linear) phase models are analysed EXACTLY
with ``identifiability.exact_linear``; results are ``StructuralReport``s
whose ``method``/``scope`` fields keep apart

- an analytically proved degeneracy (exact affine / analytic argument),
- a finite, completely checked candidate list (``finite_candidate_fibre``),
- statements about the periodic COUNT model (aliases), which a full rank of
  the unwrapped linear model does NOT exclude.

The eight mandatory counterexamples of plan §7:

1. one flight time + unknown offset: (a, phi0) -> (a + c, phi0 - K c);
2. two flight times (u = 1, 4): (A, b) locally separable -- given a common
   offset and a correct calibration;
3. phase periodicity: a -> a + d / T^2; commensurate times keep common aliases;
4. acceleration-like disturbance: p = u (A + B) + b never separates A and B;
5. orientation reversal: an even offset cancels, an odd bias stays (parity table);
6. velocity calibration: a_fit / a_true = (1 + e)^2;
7. contrast loss: equal-weight phases 0 and pi have zero contrast;
8. non-identical selection: fitting with the incoming instead of the detected
   velocity mixture biases the inferred acceleration.

No statement "reversal proves gravity" is made; more counts do not remove
a structural degeneracy.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from fractions import Fraction
from typing import Dict, List, Sequence, Tuple

from scoped_correspondence.errors import ScopeViolationError
from scoped_correspondence.identifiability.exact_linear import analyze_affine_identifiability, is_identifiable_combination
from scoped_correspondence.identifiability.structural_reports import StructuralReport


def _q(x, what) -> Fraction:
    if isinstance(x, bool) or isinstance(x, float) or not isinstance(x, (int, Fraction)):
        raise ScopeViolationError(f"{what} must be exact (int/Fraction) for the exact unwrapped-phase analysis")
    return Fraction(x)


def offset_degeneracy(K) -> StructuralReport:
    """Counterexample 1: phi = K a + phi0 at ONE flight time."""
    K = _q(K, "K")
    r = analyze_affine_identifiability([[K, 1]])
    return StructuralReport(
        "unwrapped phase phi = K a + phi0 (one flight time)", "exact_affine", "global", "R^2 (a, phi0)",
        identifiable=("K a + phi0",) if is_identifiable_combination([[K, 1]], [K, 1]) else (),
        not_identifiable=("a", "phi0"),
        witnesses=({"symmetry": "(a, phi0) -> (a + c, phi0 - K c)", "rank": r.rank, "null_space": [str(x) for x in r.null_space[0]]},),
        notes=("structural: more counts at the same flight time do not remove it",),
    )


def unwrapped_phase_report(us: Sequence, *, n_disturbances: int = 0) -> Tuple[StructuralReport, object]:
    """Counterexamples 2 and 4: p_j = u_j (A + B_1 + ... ) + b with a common
    offset b. Columns: A, B_1..B_k (same scaling u_j), b."""
    rows = [[_q(u, "u")] * (1 + n_disturbances) + [Fraction(1)] for u in us]
    r = analyze_affine_identifiability(rows)
    names = ["A"] + [f"B{i + 1}" for i in range(n_disturbances)] + ["b"]
    ident, nonid = [], []
    for i, n in enumerate(names):
        e = [0] * len(names)
        e[i] = 1
        (ident if is_identifiable_combination(rows, e) else nonid).append(n)
    if n_disturbances:
        e = [0] + [1] * n_disturbances + [0]
        e[0] = 1
        if is_identifiable_combination(rows, e):
            ident.append("A + " + " + ".join(names[1:-1]))
    return StructuralReport(
        f"unwrapped phases at u = {[str(u) for u in us]} with {n_disturbances} acceleration-like disturbance(s)",
        "exact_affine", "global", "R^p", tuple(ident), tuple(nonid),
        witnesses=({"rank": r.rank, "n_parameters": len(names)},),
        assumptions=("common offset b", "correct calibration of u", "phases already unwrapped (linear model)"),
        notes=("full rank of the UNWRAPPED linear model does not imply global uniqueness of the periodic count model",),
    ), r


def parity_table(parities: Dict[str, str]) -> StructuralReport:
    """Counterexample 5: orientation s in {+1, -1}. Gravity is odd in s.
    Each declared contribution is 'even' (cancels in p_+ - p_-) or 'odd'
    (stays with gravity in the difference)."""
    for k, v in parities.items():
        if v not in ("even", "odd"):
            raise ScopeViolationError("parity must be 'even' or 'odd'")
    odd = sorted(k for k, v in parities.items() if v == "odd")
    even = sorted(k for k, v in parities.items() if v == "even")
    return StructuralReport(
        "orientation reversal p_s = s (A + odd terms) + even terms", "analytic_argument", "global", "declared parities",
        identifiable=("A + " + " + ".join(odd),) if odd else ("A",), not_identifiable=(("A",) + tuple(odd)) if odd else (),
        witnesses=({"even_cancel_in_difference": even, "odd_remain_with_gravity": odd},),
        assumptions=("perfect reversal of the sensitive axis (an apparatus rebuild is not automatically a perfect reversal)",),
        notes=("reversal separates even offsets only; it does not prove gravity",),
    )


def velocity_calibration_bias(e) -> Fraction:
    """Counterexample 6 (single-velocity model): v_assumed = (1 + e) v_true
    gives a_fit / a_true = (1 + e)^2."""
    e = _q(e, "e")
    if e <= -1:
        raise ScopeViolationError("1 + e must be positive")
    return (1 + e) ** 2


def counterphase_contrast(weights=(Fraction(1, 2), Fraction(1, 2))) -> Tuple[float, float]:
    """Counterexample 7: two classes with phases 0 and pi. Returns
    (|F|, arithmetic phase mean). |F| = 0 for equal weights while the naive
    phase mean pi/2 pretends a definite phase."""
    w0, w1 = (float(_q(w, "weight")) for w in weights)
    F = (w0 * 1 + w1 * -1) / (w0 + w1)
    return abs(F), (0 + math.pi) / 2


__all__ = ["offset_degeneracy", "unwrapped_phase_report", "parity_table", "velocity_calibration_bias", "counterphase_contrast"]
