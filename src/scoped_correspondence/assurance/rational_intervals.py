"""Exact rational interval arithmetic (Paket J5, plan section 11.1).

Endpoints are ``fractions.Fraction``; every operation returns an interval
that CONTAINS the exact image set of the operation over its argument
intervals (natural interval extension). No floating point, no rounding --
so no directed rounding is needed. Dependency effects are NOT removed
(x - x on [0, 1] encloses to [-1, 1]); that is overestimation, never
underestimation.

Division by an interval that contains zero raises ``DenominatorContainsZero``;
it never produces an "infinite" or empty interval.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from scoped_correspondence.errors import ScopeViolationError


class DenominatorContainsZero(ArithmeticError):
    """The denominator enclosure contains 0: the quotient is not bounded by
    this enclosure (the function may or may not be defined on the box)."""


def _q(x) -> Fraction:
    if isinstance(x, bool) or not isinstance(x, (int, Fraction)):
        raise ScopeViolationError(f"interval endpoints must be exact (int/Fraction), got {type(x).__name__}")
    return Fraction(x)


@dataclass(frozen=True)
class Interval:
    lo: Fraction
    hi: Fraction

    def __post_init__(self) -> None:
        object.__setattr__(self, "lo", _q(self.lo))
        object.__setattr__(self, "hi", _q(self.hi))
        if self.lo > self.hi:
            raise ScopeViolationError(f"empty interval [{self.lo}, {self.hi}]")

    @classmethod
    def point(cls, x) -> "Interval":
        return cls(x, x)

    def contains(self, x) -> bool:
        return self.lo <= _q(x) <= self.hi

    def contains_zero(self) -> bool:
        return self.lo <= 0 <= self.hi

    @property
    def width(self) -> Fraction:
        return self.hi - self.lo

    def __add__(self, o: "Interval") -> "Interval":
        return Interval(self.lo + o.lo, self.hi + o.hi)

    def __sub__(self, o: "Interval") -> "Interval":
        return Interval(self.lo - o.hi, self.hi - o.lo)

    def __neg__(self) -> "Interval":
        return Interval(-self.hi, -self.lo)

    def __mul__(self, o: "Interval") -> "Interval":
        p = (self.lo * o.lo, self.lo * o.hi, self.hi * o.lo, self.hi * o.hi)
        return Interval(min(p), max(p))

    def reciprocal(self) -> "Interval":
        if self.contains_zero():
            raise DenominatorContainsZero(f"denominator enclosure [{self.lo}, {self.hi}] contains 0")
        return Interval(1 / self.hi, 1 / self.lo)

    def __truediv__(self, o: "Interval") -> "Interval":
        return self * o.reciprocal()

    def power(self, n: int) -> "Interval":
        """Exact image of x -> x**n for an integer n >= 0 (tight, not a
        repeated product: x**2 on [-1, 2] is [0, 4], not [-2, 4])."""
        if isinstance(n, bool) or not isinstance(n, int) or n < 0:
            raise ScopeViolationError("power exponent must be an int >= 0")
        if n == 0:
            return Interval(1, 1)
        a, b = self.lo ** n, self.hi ** n
        if n % 2 == 1:
            return Interval(a, b)
        if self.lo >= 0:
            return Interval(a, b)
        if self.hi <= 0:
            return Interval(b, a)
        return Interval(0, max(a, b))


__all__ = ["DenominatorContainsZero", "Interval"]
