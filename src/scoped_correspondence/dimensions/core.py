"""Dimensions, units, quantity kinds and expression checking (Paket J2).

Plan ``SCF_SCOPE_COMPOSITION_EVIDENCE_IMPLEMENTATION_PLAN.md`` section 8.

Three things are kept apart on purpose:

- **Dimension** (``Dimension``): a vector of RATIONAL exponents over the
  seven SI base dimensions. Metre and kilometre have the same dimension.
- **Unit** (``Unit``): a numerical scale (and, for affine scales such as
  degrees Celsius, an offset) relative to the coherent SI unit of a
  dimension. Metre and kilometre differ here.
- **Kind** (``QuantitySpec.kind``): an optional semantic label (e.g.
  ``"energy"`` vs ``"torque"``). Equal dimension does NOT make two kinds
  interchangeable; adding different kinds of the same dimension is
  dimensionally consistent but produces a semantic WARNING.

An abstract dimensionless SCF quantity is simply ``Dimension.none()``; it is
never given an invented SI unit.

Expressions are small validated trees (``Q``, ``Const``, ``Add``, ``Sub``,
``Mul``, ``Div``, ``Pow``, ``Func``) -- no parsing, no ``eval``.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
from typing import Dict, List, Mapping, Optional, Tuple, Union

from scoped_correspondence.errors import ScopeViolationError

#: SI base dimensions in a fixed order: mass, length, time, temperature,
#: electric current, amount of substance, luminous intensity.
BASE_DIMENSIONS: Tuple[str, ...] = ("M", "L", "T", "Theta", "I", "N", "J")

Rational = Union[int, Fraction]


def _as_fraction(x, what: str) -> Fraction:
    if isinstance(x, bool) or not isinstance(x, (int, Fraction)):
        raise ScopeViolationError(f"{what} must be an int or Fraction (exact), got {type(x).__name__}: {x!r}")
    return Fraction(x)


@dataclass(frozen=True)
class Dimension:
    """Exact dimension vector over ``BASE_DIMENSIONS`` with rational exponents."""

    exponents: Tuple[Fraction, ...]

    def __post_init__(self) -> None:
        if len(self.exponents) != len(BASE_DIMENSIONS):
            raise ScopeViolationError(f"Dimension needs {len(BASE_DIMENSIONS)} exponents")
        object.__setattr__(self, "exponents", tuple(_as_fraction(e, "dimension exponent") for e in self.exponents))

    @classmethod
    def of(cls, **powers: Rational) -> "Dimension":
        unknown = set(powers) - set(BASE_DIMENSIONS)
        if unknown:
            raise ScopeViolationError(f"unknown base dimension(s) {sorted(unknown)}; use {BASE_DIMENSIONS}")
        return cls(tuple(_as_fraction(powers.get(b, 0), f"exponent of {b}") for b in BASE_DIMENSIONS))

    @classmethod
    def none(cls) -> "Dimension":
        return cls(tuple(Fraction(0) for _ in BASE_DIMENSIONS))

    @property
    def is_dimensionless(self) -> bool:
        return all(e == 0 for e in self.exponents)

    def __mul__(self, other: "Dimension") -> "Dimension":
        return Dimension(tuple(a + b for a, b in zip(self.exponents, other.exponents)))

    def __truediv__(self, other: "Dimension") -> "Dimension":
        return Dimension(tuple(a - b for a, b in zip(self.exponents, other.exponents)))

    def __pow__(self, p: Rational) -> "Dimension":
        q = _as_fraction(p, "power")
        return Dimension(tuple(a * q for a in self.exponents))

    def as_dict(self) -> Dict[str, str]:
        return {b: str(e) for b, e in zip(BASE_DIMENSIONS, self.exponents) if e != 0}

    def __str__(self) -> str:
        parts = [f"{b}^{e}" if e != 1 else b for b, e in zip(BASE_DIMENSIONS, self.exponents) if e != 0]
        return " ".join(parts) if parts else "1"


@dataclass(frozen=True)
class Unit:
    """A unit of a given dimension: ``value_SI = scale * value + offset``.

    ``offset != 0`` marks an AFFINE scale (e.g. degree Celsius). Affine
    units are only meaningful for absolute values of that dimension; they
    must not be multiplied, divided or raised to powers as if they were
    multiplicative units (``Unit.is_affine``). A temperature DIFFERENCE in
    degree Celsius converts with the scale only.
    """

    name: str
    dimension: Dimension
    scale: Fraction
    offset: Fraction = Fraction(0)

    def __post_init__(self) -> None:
        object.__setattr__(self, "scale", _as_fraction(self.scale, "unit scale"))
        object.__setattr__(self, "offset", _as_fraction(self.offset, "unit offset"))
        if self.scale <= 0:
            raise ScopeViolationError("unit scale must be > 0")

    @property
    def is_affine(self) -> bool:
        return self.offset != 0


def convert(value: Rational, from_unit: Unit, to_unit: Unit, *, difference: bool = False) -> Fraction:
    """Exact conversion between two units of the SAME dimension.

    ``difference=True`` converts a difference (offsets cancel). Converting
    between different dimensions is an input error.
    """
    v = _as_fraction(value, "value")
    if from_unit.dimension != to_unit.dimension:
        raise ScopeViolationError(f"cannot convert {from_unit.name} ({from_unit.dimension}) to {to_unit.name} ({to_unit.dimension})")
    if difference:
        return v * from_unit.scale / to_unit.scale
    si = from_unit.scale * v + from_unit.offset
    return (si - to_unit.offset) / to_unit.scale


def multiplicative_scale(unit: Unit) -> Fraction:
    """The factor to use when a unit appears inside a product, quotient or
    power. Refuses affine units (degree Celsius, ...): ``2 degC * 3 m`` has
    no meaning as a multiplicative quantity; convert to an absolute scale
    (kelvin) or treat the value explicitly as a difference first."""
    if unit.is_affine:
        raise ScopeViolationError(f"{unit.name} is an affine unit (offset {unit.offset}); it has no multiplicative scale")
    return unit.scale


def rescale_for_base_unit_change(value: Rational, dimension: Dimension, factors: Mapping[str, Rational]) -> Fraction:
    """Re-express a multiplicative quantity after changing base units.

    ``factors[b]`` is how many NEW units make one OLD unit of base dimension
    ``b`` (e.g. ``{"T": 365}`` for year -> day). The value transforms as
    ``value * prod_b factors[b] ** exponent_b``. Only integer exponents are
    allowed where the factor is not a perfect power (exactness).
    """
    v = _as_fraction(value, "value")
    for b, f in factors.items():
        if b not in BASE_DIMENSIONS:
            raise ScopeViolationError(f"unknown base dimension {b!r}")
        fac = _as_fraction(f, f"factor for {b}")
        if fac <= 0:
            raise ScopeViolationError("base unit factors must be > 0")
        e = dimension.exponents[BASE_DIMENSIONS.index(b)]
        if e.denominator != 1:
            raise ScopeViolationError(f"non-integer exponent {e} for {b}: exact rescaling not supported")
        v *= fac ** int(e)
    return v


@dataclass(frozen=True)
class QuantitySpec:
    """A named quantity with its dimension and an optional semantic kind."""

    name: str
    dimension: Dimension
    kind: Optional[str] = None
    note: str = ""

    def __post_init__(self) -> None:
        if not self.name:
            raise ScopeViolationError("QuantitySpec needs a name")


# ------------------------------------------------------------ expressions --


@dataclass(frozen=True)
class Q:
    """Reference to a declared quantity by name."""

    name: str


@dataclass(frozen=True)
class Const:
    """A dimensionless (by default) exact constant."""

    value: Rational
    dimension: Dimension = field(default_factory=Dimension.none)


@dataclass(frozen=True)
class Add:
    left: "Expr"
    right: "Expr"


@dataclass(frozen=True)
class Sub:
    left: "Expr"
    right: "Expr"


@dataclass(frozen=True)
class Mul:
    left: "Expr"
    right: "Expr"


@dataclass(frozen=True)
class Div:
    left: "Expr"
    right: "Expr"


@dataclass(frozen=True)
class Pow:
    base: "Expr"
    exponent: Rational


#: Functions whose argument must be dimensionless (and whose value is).
DIMENSIONLESS_FUNCTIONS = ("exp", "log", "sin", "cos", "tanh")


@dataclass(frozen=True)
class Func:
    name: str
    arg: "Expr"


Expr = Union[Q, Const, Add, Sub, Mul, Div, Pow, Func]


@dataclass(frozen=True)
class DimensionCheckReport:
    """``status`` is ``"consistent"`` or ``"inconsistent"``. Semantic warnings
    (different kinds with equal dimension) never change the status: they
    are a different question from dimensional consistency."""

    status: str
    dimension: Optional[Dimension]
    violations: Tuple[str, ...]
    semantic_warnings: Tuple[str, ...]
    kinds: Tuple[str, ...] = ()

    def to_dict(self) -> Dict[str, object]:
        return {
            "status": self.status,
            "dimension": None if self.dimension is None else self.dimension.as_dict(),
            "violations": list(self.violations),
            "semantic_warnings": list(self.semantic_warnings),
        }


def check_dimension(expression: Expr, specs: Mapping[str, QuantitySpec]) -> DimensionCheckReport:
    """Exact dimensional check of a validated expression tree.

    Returns the expression's dimension if consistent, otherwise every
    violation with its path. Unknown quantity names and unsupported node
    types are input errors (``ScopeViolationError``), not violations.
    """
    violations: List[str] = []
    warnings: List[str] = []

    def walk(e, path: str) -> Tuple[Optional[Dimension], Optional[str]]:
        if isinstance(e, Q):
            if e.name not in specs:
                raise ScopeViolationError(f"check_dimension: unknown quantity {e.name!r} at {path}")
            s = specs[e.name]
            return s.dimension, s.kind
        if isinstance(e, Const):
            _as_fraction(e.value, "constant value")
            return e.dimension, None
        if isinstance(e, (Add, Sub)):
            dl, kl = walk(e.left, path + ".left")
            dr, kr = walk(e.right, path + ".right")
            if dl is None or dr is None:
                return None, None
            op = "+" if isinstance(e, Add) else "-"
            if dl != dr:
                violations.append(f"{path}: cannot {op} [{dl}] and [{dr}]")
                return None, None
            if kl and kr and kl != kr:
                warnings.append(f"{path}: {op} of equal dimension [{dl}] but different kinds {kl!r} and {kr!r}")
                return dl, None
            return dl, kl or kr
        if isinstance(e, (Mul, Div)):
            dl, _ = walk(e.left, path + ".left")
            dr, _ = walk(e.right, path + ".right")
            if dl is None or dr is None:
                return None, None
            return (dl * dr if isinstance(e, Mul) else dl / dr), None
        if isinstance(e, Pow):
            p = _as_fraction(e.exponent, "power")
            d, _ = walk(e.base, path + ".base")
            return (None if d is None else d ** p), None
        if isinstance(e, Func):
            if e.name not in DIMENSIONLESS_FUNCTIONS:
                raise ScopeViolationError(f"check_dimension: unsupported function {e.name!r}; supported {DIMENSIONLESS_FUNCTIONS}")
            d, _ = walk(e.arg, path + ".arg")
            if d is not None and not d.is_dimensionless:
                violations.append(f"{path}: argument of {e.name} must be dimensionless, got [{d}]")
                return None, None
            return (Dimension.none() if d is not None else None), None
        raise ScopeViolationError(f"check_dimension: unsupported node {type(e).__name__} at {path}")

    dim, _ = walk(expression, "expr")
    if violations:
        return DimensionCheckReport("inconsistent", None, tuple(violations), tuple(warnings))
    return DimensionCheckReport("consistent", dim, (), tuple(warnings))


__all__ = [
    "BASE_DIMENSIONS",
    "Dimension",
    "Unit",
    "convert",
    "multiplicative_scale",
    "rescale_for_base_unit_change",
    "QuantitySpec",
    "Q",
    "Const",
    "Add",
    "Sub",
    "Mul",
    "Div",
    "Pow",
    "Func",
    "DIMENSIONLESS_FUNCTIONS",
    "DimensionCheckReport",
    "check_dimension",
]
