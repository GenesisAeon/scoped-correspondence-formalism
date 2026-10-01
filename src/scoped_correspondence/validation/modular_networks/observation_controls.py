"""Exact observation and structure controls (Paket ON1, plan §5.1).

Response operator for a fair stimulus index S in {0, 1}, u_0 = (1, 0),
u_1 = (0, 1) and 0 <= delta <= 1:

    W(delta) = [[1 + delta, 1 - delta], [1 - delta, 1 + delta]],   y_S = W(delta) u_S

Column sums are 2 and det W = 4 delta. Observers: O_full(y) = y and
O_sum(y) = y_1 + y_2. O_sum is always 2: the SAME total activity carries no
information about S, while O_full separates the inputs for delta > 0 in the
NOISELESS case. delta is a GIVEN structural parameter here, not a learned
mechanism; the jump from 0 to 1 bit at arbitrarily small delta > 0 rests on
infinitely precise noiseless observation and is not a biological tipping
threshold.

Function (W), observation (O) and stimulus label (S) are separate inputs.
Exact equality is only used for exact (Fraction) responses; noisy float
similarity is never treated as exact equality (ON2 handles noise).
"""
from __future__ import annotations

import math
from fractions import Fraction
from typing import Callable, Dict, Sequence, Tuple

from scoped_correspondence.epistemic.observation_fibers import FiberReport, observation_fiber
from scoped_correspondence.epistemic.records import FiniteDomainSpec
from scoped_correspondence.errors import ScopeViolationError

Vector = Tuple[Fraction, ...]
STIMULI: Tuple[Vector, Vector] = ((Fraction(1), Fraction(0)), (Fraction(0), Fraction(1)))


def _exact(x, what) -> Fraction:
    if isinstance(x, bool) or isinstance(x, float) or not isinstance(x, (int, Fraction)):
        raise ScopeViolationError(f"{what} must be exact (int/Fraction); noisy floats belong to ON2")
    return Fraction(x)


def response_operator(delta) -> Tuple[Tuple[Fraction, Fraction], Tuple[Fraction, Fraction]]:
    d = _exact(delta, "delta")
    if not (0 <= d <= 1):
        raise ScopeViolationError("delta must lie in [0, 1]")
    return ((1 + d, 1 - d), (1 - d, 1 + d))


def respond(W, u: Sequence) -> Vector:
    if len(u) != 2 or len(W) != 2 or any(len(r) != 2 for r in W):
        raise ScopeViolationError("this control is two-dimensional")
    uu = [_exact(x, "input") for x in u]
    return tuple(sum(W[i][j] * uu[j] for j in range(2)) for i in range(2))


def observe_full(y: Vector) -> Vector:
    return tuple(y)


def observe_sum(y: Vector) -> Fraction:
    return sum(y, Fraction(0))


def sensor_permutation(y: Vector) -> Vector:
    """An invertible relabelling of the two sensors."""
    return tuple(reversed(y))


def exact_information_bits(delta, observer: Callable) -> Fraction:
    """I(S; O(W(delta) u_S)) for a fair S in the NOISELESS exact model: the
    observation is a deterministic function of S, so I = H(S) = 1 bit if the
    two observations differ and 0 otherwise (returned exactly as 0 or 1)."""
    W = response_operator(delta)
    o0, o1 = observer(respond(W, STIMULI[0])), observer(respond(W, STIMULI[1]))
    return Fraction(1) if o0 != o1 else Fraction(0)


def stimulus_fibre(delta, observer: Callable, observed) -> FiberReport:
    """Which stimuli are compatible with an observation (existing H3 fibre over
    the two declared stimuli)."""
    W = response_operator(delta)
    dom = FiniteDomainSpec("stimuli", (0, 1), "fair binary stimulus index", coverage="complete",
                           relationship_to_target_space="entire_finite_space")
    return observation_fiber(dom, [], lambda s: observer(respond(W, STIMULI[s])), observed)


__all__ = ["STIMULI", "response_operator", "respond", "observe_full", "observe_sum", "sensor_permutation",
           "exact_information_bits", "stimulus_fibre"]
