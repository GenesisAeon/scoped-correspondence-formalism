"""Small validated expression trees for scope certification (Paket J5, §11.1).

Supported: constants, variables, +, -, *, unary minus, integer powers
n >= 0, and division (only where the denominator enclosure excludes 0).
No parsing, no ``eval``, no arbitrary Python callbacks -- a callback does
not become a provable expression by evaluating it more often.

Constants are exact. Decimal constants are given as strings ("0.1" is
exactly 1/10). A binary float is accepted only through ``Const.of_float``,
which keeps its EXACT binary value (0.1 -> 3602879701896397/36028797018963968)
and says so -- ``Fraction(str(float))`` would silently mean a different
number.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Dict, Mapping, Tuple, Union

from scoped_correspondence.assurance.rational_intervals import Interval
from scoped_correspondence.errors import ScopeViolationError


class UndefinedAtPoint(ArithmeticError):
    """Exact evaluation hit a zero denominator."""


@dataclass(frozen=True)
class Const:
    value: Fraction
    note: str = ""

    def __post_init__(self) -> None:
        v = self.value
        if isinstance(v, bool) or isinstance(v, float) or not isinstance(v, (int, Fraction, str)):
            raise ScopeViolationError("Const needs int, Fraction or a decimal string; use Const.of_float for a binary float")
        object.__setattr__(self, "value", Fraction(v))

    @classmethod
    def of_float(cls, x: float) -> "Const":
        return cls(Fraction(x), note=f"exact binary value of float {x!r}")


@dataclass(frozen=True)
class Var:
    name: str


@dataclass(frozen=True)
class Add:
    a: "Expr"
    b: "Expr"


@dataclass(frozen=True)
class Sub:
    a: "Expr"
    b: "Expr"


@dataclass(frozen=True)
class Mul:
    a: "Expr"
    b: "Expr"


@dataclass(frozen=True)
class Div:
    a: "Expr"
    b: "Expr"


@dataclass(frozen=True)
class Neg:
    a: "Expr"


@dataclass(frozen=True)
class Pow:
    a: "Expr"
    n: int

    def __post_init__(self) -> None:
        if isinstance(self.n, bool) or not isinstance(self.n, int) or self.n < 0:
            raise ScopeViolationError("Pow exponent must be an int >= 0")


Expr = Union[Const, Var, Add, Sub, Mul, Div, Neg, Pow]
_NODES = (Const, Var, Add, Sub, Mul, Div, Neg, Pow)


def validate(e: Expr) -> Tuple[str, ...]:
    """Raise on unsupported nodes; return the sorted variable names."""
    names = set()

    def walk(x):
        if not isinstance(x, _NODES):
            raise ScopeViolationError(f"unsupported expression node {type(x).__name__} (callbacks are not provable expressions)")
        if isinstance(x, Var):
            names.add(x.name)
        for child in ("a", "b"):
            if hasattr(x, child):
                walk(getattr(x, child))

    walk(e)
    return tuple(sorted(names))


def evaluate(e: Expr, point: Mapping[str, Fraction]) -> Fraction:
    """Exact rational value; raises ``UndefinedAtPoint`` on a zero denominator."""
    if isinstance(e, Const):
        return e.value
    if isinstance(e, Var):
        return Fraction(point[e.name])
    if isinstance(e, Add):
        return evaluate(e.a, point) + evaluate(e.b, point)
    if isinstance(e, Sub):
        return evaluate(e.a, point) - evaluate(e.b, point)
    if isinstance(e, Mul):
        return evaluate(e.a, point) * evaluate(e.b, point)
    if isinstance(e, Neg):
        return -evaluate(e.a, point)
    if isinstance(e, Pow):
        return evaluate(e.a, point) ** e.n
    if isinstance(e, Div):
        d = evaluate(e.b, point)
        if d == 0:
            raise UndefinedAtPoint(f"zero denominator at {dict(point)}")
        return evaluate(e.a, point) / d
    raise ScopeViolationError(f"unsupported node {type(e).__name__}")


def enclose(e: Expr, box: Mapping[str, Interval]) -> Interval:
    """Natural interval extension over ``box`` (contains the exact image).
    Raises ``DenominatorContainsZero`` if a denominator enclosure contains 0."""
    if isinstance(e, Const):
        return Interval.point(e.value)
    if isinstance(e, Var):
        return box[e.name]
    if isinstance(e, Add):
        return enclose(e.a, box) + enclose(e.b, box)
    if isinstance(e, Sub):
        return enclose(e.a, box) - enclose(e.b, box)
    if isinstance(e, Mul):
        return enclose(e.a, box) * enclose(e.b, box)
    if isinstance(e, Neg):
        return -enclose(e.a, box)
    if isinstance(e, Pow):
        return enclose(e.a, box).power(e.n)
    if isinstance(e, Div):
        return enclose(e.a, box) / enclose(e.b, box)
    raise ScopeViolationError(f"unsupported node {type(e).__name__}")


def to_text(e: Expr) -> str:
    if isinstance(e, Const):
        return str(e.value)
    if isinstance(e, Var):
        return e.name
    if isinstance(e, Neg):
        return f"(-{to_text(e.a)})"
    if isinstance(e, Pow):
        return f"({to_text(e.a)})^{e.n}"
    op = {Add: "+", Sub: "-", Mul: "*", Div: "/"}[type(e)]
    return f"({to_text(e.a)} {op} {to_text(e.b)})"


__all__ = ["UndefinedAtPoint", "Const", "Var", "Add", "Sub", "Mul", "Div", "Neg", "Pow", "Expr",
           "validate", "evaluate", "enclose", "to_text"]
