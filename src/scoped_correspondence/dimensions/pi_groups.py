"""Exact Buckingham-Pi basis (Paket J2, plan section 8).

For n quantities with dimension matrix D (rows: base dimensions, columns:
quantities) every v in ker D gives a dimensionless monomial
Pi = prod_j q_j^{v_j}; there are n - rank(D) independent groups.

Different null-space bases are equally valid. Callers and tests must
compare SPANS (``same_pi_span``), never a particular basis spelling. The
theorem yields no dynamics and no universal numerical prefactor.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import gcd
from typing import Dict, List, Sequence, Tuple

from scoped_correspondence.dimensions.core import BASE_DIMENSIONS, QuantitySpec
from scoped_correspondence.errors import ScopeViolationError


def _rref(rows: List[List[Fraction]]) -> Tuple[List[List[Fraction]], List[int]]:
    m = [list(r) for r in rows]
    pivots: List[int] = []
    r = 0
    ncols = len(m[0]) if m else 0
    for c in range(ncols):
        piv = next((i for i in range(r, len(m)) if m[i][c] != 0), None)
        if piv is None:
            continue
        m[r], m[piv] = m[piv], m[r]
        lead = m[r][c]
        m[r] = [x / lead for x in m[r]]
        for i in range(len(m)):
            if i != r and m[i][c] != 0:
                f = m[i][c]
                m[i] = [a - f * b for a, b in zip(m[i], m[r])]
        pivots.append(c)
        r += 1
        if r == len(m):
            break
    return m, pivots


def exact_rank(rows: Sequence[Sequence[Fraction]]) -> int:
    if not rows or not rows[0]:
        return 0
    return len(_rref([[Fraction(x) for x in r] for r in rows])[1])


def exact_null_space(rows: Sequence[Sequence[Fraction]], ncols: int) -> List[List[Fraction]]:
    """Exact rational basis of {v : rows v = 0}, one vector per free column."""
    if ncols < 1:
        raise ScopeViolationError("exact_null_space: need at least one column")
    mat = [[Fraction(x) for x in r] for r in rows if any(Fraction(x) != 0 for x in r)]
    if not mat:
        return [[Fraction(int(i == j)) for i in range(ncols)] for j in range(ncols)]
    rref, pivots = _rref(mat)
    free = [c for c in range(ncols) if c not in pivots]
    basis = []
    for f in free:
        v = [Fraction(0)] * ncols
        v[f] = Fraction(1)
        for row_i, pc in enumerate(pivots):
            v[pc] = -rref[row_i][f]
        basis.append(v)
    return basis


def _primitive_integer(v: Sequence[Fraction]) -> Tuple[int, ...]:
    """Scale a rational vector to coprime integers, first nonzero entry > 0."""
    den = 1
    for x in v:
        den = den * x.denominator // gcd(den, x.denominator)
    ints = [int(x * den) for x in v]
    g = 0
    for x in ints:
        g = gcd(g, abs(x))
    ints = [x // g for x in ints] if g else ints
    first = next((x for x in ints if x != 0), 0)
    if first < 0:
        ints = [-x for x in ints]
    return tuple(ints)


@dataclass(frozen=True)
class PiBasisReport:
    quantities: Tuple[str, ...]
    dimension_matrix: Tuple[Tuple[Fraction, ...], ...]  # rows = BASE_DIMENSIONS
    rank: int
    nullity: int
    basis: Tuple[Tuple[int, ...], ...]  # primitive integer exponent vectors
    monomials: Tuple[str, ...]
    note: str = "Any basis of the same span is equally valid; no dynamics or prefactor is implied."

    def to_dict(self) -> Dict[str, object]:
        return {
            "quantities": list(self.quantities),
            "rank": self.rank,
            "nullity": self.nullity,
            "basis": [list(b) for b in self.basis],
            "monomials": list(self.monomials),
            "note": self.note,
        }


def _monomial(names: Sequence[str], v: Sequence[int]) -> str:
    num = [f"{n}^{e}" if e != 1 else n for n, e in zip(names, v) if e > 0]
    den = [f"{n}^{-e}" if e != -1 else n for n, e in zip(names, v) if e < 0]
    top = "*".join(num) if num else "1"
    return top if not den else f"{top}/({'*'.join(den)})"


def buckingham_pi_basis(specs: Sequence[QuantitySpec]) -> PiBasisReport:
    """Exact Pi basis for the given quantities (order = column order).

    Empty input and duplicate names are input errors. Already dimensionless
    quantities each form a group on their own. A matrix of full column rank
    yields ``nullity == 0`` and an empty basis -- no dimensionless
    combination exists, which is a valid result, not an error.
    """
    if not specs:
        raise ScopeViolationError("buckingham_pi_basis: need at least one quantity")
    names = [s.name for s in specs]
    if len(set(names)) != len(names):
        raise ScopeViolationError("buckingham_pi_basis: duplicate quantity names")
    n = len(specs)
    matrix = [[specs[j].dimension.exponents[i] for j in range(n)] for i in range(len(BASE_DIMENSIONS))]
    rank = exact_rank(matrix)
    basis = [_primitive_integer(v) for v in exact_null_space(matrix, n)]
    if len(basis) != n - rank:
        raise AssertionError("internal: rank-nullity violated")
    return PiBasisReport(
        quantities=tuple(names),
        dimension_matrix=tuple(tuple(r) for r in matrix),
        rank=rank,
        nullity=n - rank,
        basis=tuple(basis),
        monomials=tuple(_monomial(names, v) for v in basis),
    )


def same_pi_span(a: Sequence[Sequence[int]], b: Sequence[Sequence[int]]) -> bool:
    """True iff two sets of exponent vectors span the same rational space."""
    if not a and not b:
        return True
    if not a or not b:
        return False
    ra = exact_rank([[Fraction(x) for x in v] for v in a])
    rb = exact_rank([[Fraction(x) for x in v] for v in b])
    rab = exact_rank([[Fraction(x) for x in v] for v in list(a) + list(b)])
    return ra == rb == rab


__all__ = ["exact_rank", "exact_null_space", "PiBasisReport", "buckingham_pi_basis", "same_pi_span"]
