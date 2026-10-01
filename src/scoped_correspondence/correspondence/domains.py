"""Supported domains for scope contracts (Paket J4, plan section 10.1).

First version supports:

- ``FiniteSet``     -- explicit finite set of rational points.
- ``RationalBox``   -- closed axis-parallel box with rational bounds
                       (``lo > hi`` in any axis = empty, flagged explicitly).
- ``HalfspaceSet``  -- conjunction of exact rational linear inequalities
                       ``a . x <= c`` (optionally intersected with a box). This
                       is how a preimage under a general affine map is KEPT
                       when it is not a box -- it is never silently replaced
                       by a larger enclosing box (plan section 10.1).
- ``OpaquePredicate`` -- an arbitrary Python predicate: usable for POINT
                       membership only; it never yields a universal inclusion.

``Scope.contains`` in ``contract.py`` remains a point-membership test; the
functions here add exact universal statements for the supported classes.
Initial-state domains and whole-trajectory domains are different things:
x0 in D does not imply that the motion stays in D (invariance is its own
certificate, not provided here).
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import product
from typing import Callable, Optional, Sequence, Tuple, Union

from scoped_correspondence.assurance.records import ProofReport
from scoped_correspondence.errors import ScopeViolationError

Point = Tuple[Fraction, ...]


def _q(x, what="value") -> Fraction:
    if isinstance(x, bool) or not isinstance(x, (int, Fraction, str)):
        raise ScopeViolationError(f"{what} must be int, Fraction or a decimal string (exact), got {type(x).__name__}")
    return Fraction(x)


def as_point(p) -> Point:
    return tuple(_q(x, "coordinate") for x in (p if isinstance(p, (tuple, list)) else (p,)))


@dataclass(frozen=True)
class FiniteSet:
    points: Tuple[Point, ...]

    def __post_init__(self) -> None:
        pts = tuple(as_point(p) for p in self.points)
        if len({len(p) for p in pts}) > 1:
            raise ScopeViolationError("FiniteSet points must share one dimension")
        object.__setattr__(self, "points", tuple(dict.fromkeys(pts)))

    @property
    def dim(self) -> Optional[int]:
        return len(self.points[0]) if self.points else None

    @property
    def is_empty(self) -> bool:
        return not self.points

    def describe(self) -> dict:
        return {"kind": "finite_set", "points": [[str(x) for x in p] for p in self.points]}


@dataclass(frozen=True)
class RationalBox:
    bounds: Tuple[Tuple[Fraction, Fraction], ...]

    def __post_init__(self) -> None:
        if not self.bounds:
            raise ScopeViolationError("RationalBox needs at least one axis")
        object.__setattr__(self, "bounds", tuple((_q(lo, "lower bound"), _q(hi, "upper bound")) for lo, hi in self.bounds))

    @classmethod
    def interval(cls, lo, hi) -> "RationalBox":
        return cls(((lo, hi),))

    @property
    def dim(self) -> int:
        return len(self.bounds)

    @property
    def is_empty(self) -> bool:
        return any(lo > hi for lo, hi in self.bounds)

    def corners(self) -> Tuple[Point, ...]:
        return tuple(product(*[(lo, hi) for lo, hi in self.bounds]))

    def intersect(self, other: "RationalBox") -> "RationalBox":
        if other.dim != self.dim:
            raise ScopeViolationError("box dimensions differ")
        return RationalBox(tuple((max(a[0], b[0]), min(a[1], b[1])) for a, b in zip(self.bounds, other.bounds)))

    def describe(self) -> dict:
        return {"kind": "rational_box", "bounds": [[str(lo), str(hi)] for lo, hi in self.bounds], "empty": self.is_empty}


@dataclass(frozen=True)
class HalfspaceSet:
    """{x in box : a_i . x <= c_i for all i}; exact, possibly not a box."""

    box: RationalBox
    rows: Tuple[Tuple[Tuple[Fraction, ...], Fraction], ...]

    def __post_init__(self) -> None:
        rows = tuple((tuple(_q(a, "coefficient") for a in coeffs), _q(c, "rhs")) for coeffs, c in self.rows)
        if any(len(coeffs) != self.box.dim for coeffs, _ in rows):
            raise ScopeViolationError("halfspace coefficients must match the box dimension")
        object.__setattr__(self, "rows", rows)

    @property
    def dim(self) -> int:
        return self.box.dim

    def describe(self) -> dict:
        return {"kind": "halfspace_set", "box": self.box.describe(),
                "constraints": [{"a": [str(x) for x in a], "le": str(c)} for a, c in self.rows]}


@dataclass(frozen=True)
class OpaquePredicate:
    name: str
    fn: Callable[[Point], bool]

    def describe(self) -> dict:
        return {"kind": "opaque_predicate", "name": self.name}


Domain = Union[FiniteSet, RationalBox, HalfspaceSet, OpaquePredicate]


def domain_contains(domain: Domain, point) -> bool:
    """Exact point membership (opaque predicates are simply evaluated)."""
    p = as_point(point)
    if isinstance(domain, FiniteSet):
        return p in domain.points
    if isinstance(domain, RationalBox):
        if len(p) != domain.dim:
            raise ScopeViolationError("point dimension does not match the box")
        return all(lo <= x <= hi for x, (lo, hi) in zip(p, domain.bounds))
    if isinstance(domain, HalfspaceSet):
        return domain_contains(domain.box, p) and all(sum(a * x for a, x in zip(coeffs, p)) <= c for coeffs, c in domain.rows)
    if isinstance(domain, OpaquePredicate):
        return bool(domain.fn(p))
    raise ScopeViolationError(f"unsupported domain type {type(domain).__name__}")


def _report(claim, verdict, status, kind, reasons=(), witnesses=(), empty=False, exhausted=False) -> ProofReport:
    return ProofReport(claim=claim, method="correspondence.domains.certify_subset", verdict=verdict,
                       procedure_status=status, evidence_kind=kind, arithmetic="exact_rational",
                       empty_domain=empty, conclusion_complete=verdict in ("proved", "refuted"),
                       domain_exhausted=exhausted, reasons=tuple(reasons), witnesses=tuple(witnesses))


def certify_subset(inner: Domain, outer: Domain) -> ProofReport:
    """Universal inclusion ``inner subset outer`` for supported classes.

    proved/refuted are exact; an opaque OUTER predicate with a non-finite
    inner domain gives ``undecided`` (no universal inclusion without proof);
    an opaque INNER domain is ``unsupported_structure``. An empty inner
    domain is proved VACUOUSLY and flagged ``empty_domain``.
    """
    claim = f"{type(inner).__name__} subset {type(outer).__name__}"
    if isinstance(inner, OpaquePredicate):
        return _report(claim, "undecided", "unsupported_structure", "not_evaluated", ["opaque inner domain"])
    if getattr(inner, "is_empty", False):
        return _report(claim, "proved", "completed", "analytic_argument", ["empty inner domain: vacuous"], empty=True)
    if isinstance(inner, FiniteSet):
        for p in inner.points:
            if not domain_contains(outer, p):
                return _report(claim, "refuted", "completed", "exhaustive_finite", ["counterexample point"], [p])
        return _report(claim, "proved", "completed", "exhaustive_finite", ["every point checked"], exhausted=True)
    if isinstance(outer, OpaquePredicate):
        return _report(claim, "undecided", "completed", "not_evaluated",
                       ["opaque outer predicate: point checks only, no universal inclusion"])
    if isinstance(inner, RationalBox):
        if isinstance(outer, RationalBox):
            if outer.dim != inner.dim:
                raise ScopeViolationError("dimension mismatch")
            base = [lo for lo, _ in inner.bounds]
            for axis, ((ilo, ihi), (olo, ohi)) in enumerate(zip(inner.bounds, outer.bounds)):
                if ilo < olo or ihi > ohi:
                    w = list(base)
                    w[axis] = ilo if ilo < olo else ihi
                    return _report(claim, "refuted", "completed", "analytic_argument",
                                   [f"axis {axis}: {'lower' if ilo < olo else 'upper'} bound outside"], [tuple(w)])
            return _report(claim, "proved", "completed", "analytic_argument", ["axis-wise bound comparison"])
        if isinstance(outer, HalfspaceSet):
            # a box lies in a convex polyhedron iff all its corners do
            for c in inner.corners():
                if not domain_contains(outer, c):
                    return _report(claim, "refuted", "completed", "analytic_argument", ["corner outside"], [c])
            return _report(claim, "proved", "completed", "analytic_argument", ["all corners inside a convex set"])
        if isinstance(outer, FiniteSet):
            # a nonempty box with a nondegenerate axis has infinitely many points
            if all(lo == hi for lo, hi in inner.bounds):
                p = tuple(lo for lo, _ in inner.bounds)
                verdict = "proved" if domain_contains(outer, p) else "refuted"
                return _report(claim, verdict, "completed", "analytic_argument", ["degenerate box = one point"], [] if verdict == "proved" else [p])
            for c in inner.corners():
                if not domain_contains(outer, c):
                    return _report(claim, "refuted", "completed", "analytic_argument", ["corner outside the finite set"], [c])
            mid = tuple((lo + hi) / 2 for lo, hi in inner.bounds)
            if not domain_contains(outer, mid):
                return _report(claim, "refuted", "completed", "analytic_argument", ["midpoint outside the finite set"], [mid])
            return _report(claim, "refuted", "completed", "analytic_argument",
                           ["infinite box cannot lie in a finite set"],
                           [tuple((2 * lo + hi) / 3 if lo != hi else lo for lo, hi in inner.bounds)])
    if isinstance(inner, HalfspaceSet):
        return _report(claim, "undecided", "unsupported_structure", "not_evaluated",
                       ["inclusion of a general polyhedron requires vertex enumeration / LP: not implemented"])
    raise ScopeViolationError("unsupported domain combination")


@dataclass(frozen=True)
class AffineMap:
    """Exact affine map y = A x + b with rational entries."""

    A: Tuple[Tuple[Fraction, ...], ...]
    b: Tuple[Fraction, ...]
    name: str = "T"

    def __post_init__(self) -> None:
        A = tuple(tuple(_q(a, "matrix entry") for a in row) for row in self.A)
        b = tuple(_q(x, "offset") for x in self.b)
        if not A or len(A) != len(b) or len({len(r) for r in A}) != 1:
            raise ScopeViolationError("AffineMap: inconsistent shapes")
        object.__setattr__(self, "A", A)
        object.__setattr__(self, "b", b)

    @classmethod
    def scalar(cls, a, b=0, name="T") -> "AffineMap":
        return cls(((a,),), (b,), name)

    @classmethod
    def identity(cls, n: int, name="id") -> "AffineMap":
        return cls(tuple(tuple(Fraction(int(i == j)) for j in range(n)) for i in range(n)), tuple(Fraction(0) for _ in range(n)), name)

    @property
    def in_dim(self) -> int:
        return len(self.A[0])

    @property
    def out_dim(self) -> int:
        return len(self.A)

    def __call__(self, x) -> Point:
        p = as_point(x)
        if len(p) != self.in_dim:
            raise ScopeViolationError("AffineMap: input dimension mismatch")
        return tuple(sum(a * xi for a, xi in zip(row, p)) + bi for row, bi in zip(self.A, self.b))

    def then(self, other: "AffineMap") -> "AffineMap":
        """other o self."""
        if other.in_dim != self.out_dim:
            raise ScopeViolationError("AffineMap.then: dimension mismatch")
        A = tuple(tuple(sum(other.A[i][k] * self.A[k][j] for k in range(self.out_dim)) for j in range(self.in_dim)) for i in range(other.out_dim))
        b = tuple(sum(other.A[i][k] * self.b[k] for k in range(self.out_dim)) + other.b[i] for i in range(other.out_dim))
        return AffineMap(A, b, f"{other.name}o{self.name}")

    def inf_operator_norm(self) -> Fraction:
        """Exact induced infinity-norm (max absolute row sum) of A."""
        return max(sum(abs(a) for a in row) for row in self.A)


def preimage_constraint(T: AffineMap, target: RationalBox, within: RationalBox) -> Union[RationalBox, HalfspaceSet]:
    """``within ∩ T^{-1}(target)`` EXACTLY.

    If every output coordinate depends on at most one input coordinate the
    result is again a box (with correct handling of negative scale factors);
    otherwise the linear inequalities are kept symbolically as a
    ``HalfspaceSet`` -- never replaced by a larger box.
    """
    if target.dim != T.out_dim or within.dim != T.in_dim:
        raise ScopeViolationError("preimage_constraint: dimension mismatch")
    rows = []
    for i, (lo, hi) in enumerate(target.bounds):
        rows.append((T.A[i], hi - T.b[i]))
        rows.append((tuple(-a for a in T.A[i]), -(lo - T.b[i])))
    support = [[j for j, a in enumerate(row) if a != 0] for row in T.A]
    if all(len(s) <= 1 for s in support):
        bounds = [list(b) for b in within.bounds]
        empty = False
        for i, s in enumerate(support):
            lo, hi = target.bounds[i]
            if not s:  # constant output: either always inside or never
                if not (lo <= T.b[i] <= hi):
                    empty = True
                continue
            j = s[0]
            a = T.A[i][j]
            l, h = (lo - T.b[i]) / a, (hi - T.b[i]) / a
            if a < 0:
                l, h = h, l
            bounds[j][0] = max(bounds[j][0], l)
            bounds[j][1] = min(bounds[j][1], h)
        if empty:
            return RationalBox(tuple((Fraction(1), Fraction(0)) for _ in bounds))
        return RationalBox(tuple(tuple(b) for b in bounds))
    return HalfspaceSet(within, tuple(rows))


def sets_equal(a: Domain, b: Domain) -> ProofReport:
    """Exact equality for box/box and finite/finite; mutual inclusion
    otherwise where supported."""
    if isinstance(a, RationalBox) and isinstance(b, RationalBox):
        if a.is_empty and b.is_empty:
            return _report("A == B", "proved", "completed", "analytic_argument", ["both empty"], empty=True)
        ok = a.bounds == b.bounds
        return _report("A == B", "proved" if ok else "refuted", "completed", "analytic_argument", ["bound comparison"])
    r1, r2 = certify_subset(a, b), certify_subset(b, a)
    if r1.verdict == "proved" and r2.verdict == "proved":
        return _report("A == B", "proved", "completed", r1.evidence_kind, ["mutual inclusion"])
    if "refuted" in (r1.verdict, r2.verdict):
        w = r1.witnesses or r2.witnesses
        return _report("A == B", "refuted", "completed", r1.evidence_kind, ["one inclusion refuted"], w)
    return _report("A == B", "undecided", "unsupported_structure", "not_evaluated", ["inclusion undecided"])


__all__ = [
    "Point",
    "FiniteSet",
    "RationalBox",
    "HalfspaceSet",
    "OpaquePredicate",
    "Domain",
    "as_point",
    "domain_contains",
    "certify_subset",
    "AffineMap",
    "preimage_constraint",
    "sets_equal",
]
