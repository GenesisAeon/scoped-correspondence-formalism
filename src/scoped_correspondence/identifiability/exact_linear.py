"""Exact affine structural identifiability (Paket J6, plan section 12).

Observation map z = A theta + b with a RATIONAL matrix A. On the unrestricted
parameter space R^p:

- the observation fibre of z is the affine set {theta0 + N t} (theta0 a
  particular solution, N a null-space basis of A), or EMPTY if z is not in
  the image (an inconsistent observation, not an identification result);
- a linear combination c^T theta is uniquely determined by the
  observation iff c lies in the row space of A.

A parameter domain can make individual fibres smaller. It is reported
explicitly: on R^p the answer above is exact; for a rational box domain and
a ONE-dimensional null space the fibre restricted to the box is computed
exactly (a line segment, possibly a single point); for larger null spaces
the restriction effect is reported as ``not_evaluated`` -- never assumed.

This is not a general nonlinear identifiability solver; a numerically full
Jacobian rank does not certify global uniqueness (see structural_reports).
Exact linear algebra is shared with ``dimensions.pi_groups``.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import List, Optional, Sequence, Tuple

from scoped_correspondence.correspondence.domains import RationalBox
from scoped_correspondence.dimensions.pi_groups import exact_null_space, exact_rank
from scoped_correspondence.errors import ScopeViolationError


def _exact_matrix(A) -> List[List[Fraction]]:
    rows = []
    for r in A:
        row = []
        for v in r:
            if isinstance(v, bool) or isinstance(v, float) or not isinstance(v, (int, Fraction, str)):
                raise ScopeViolationError("matrix entries must be exact (int, Fraction or decimal string)")
            row.append(Fraction(v))
        rows.append(row)
    if not rows or len({len(r) for r in rows}) != 1 or not rows[0]:
        raise ScopeViolationError("A must be a nonempty rectangular matrix")
    return rows


def _solve_particular(A: List[List[Fraction]], z: List[Fraction]) -> Optional[List[Fraction]]:
    """One exact solution of A theta = z (free variables = 0), or None."""
    m, p = len(A), len(A[0])
    M = [row[:] + [z[i]] for i, row in enumerate(A)]
    pivots = []
    r = 0
    for c in range(p):
        piv = next((i for i in range(r, m) if M[i][c] != 0), None)
        if piv is None:
            continue
        M[r], M[piv] = M[piv], M[r]
        lead = M[r][c]
        M[r] = [x / lead for x in M[r]]
        for i in range(m):
            if i != r and M[i][c] != 0:
                f = M[i][c]
                M[i] = [a - f * b for a, b in zip(M[i], M[r])]
        pivots.append(c)
        r += 1
    for i in range(r, m):
        if M[i][p] != 0:
            return None
    theta = [Fraction(0)] * p
    for i, c in enumerate(pivots):
        theta[c] = M[i][p]
    return theta


@dataclass(frozen=True)
class AffineIdentifiabilityReport:
    rank: int
    n_parameters: int
    null_space: Tuple[Tuple[Fraction, ...], ...]
    globally_identifiable_on_Rp: bool
    parameter_domain: str
    observation: Optional[Tuple[Fraction, ...]] = None
    observation_consistent: Optional[bool] = None
    particular_solution: Optional[Tuple[Fraction, ...]] = None
    fibre_on_domain: Optional[Tuple[Fraction, Fraction]] = None  # t-range along the 1-D null direction
    fibre_restriction_status: str = "not_applicable"  # exact | not_evaluated | not_applicable | empty
    notes: Tuple[str, ...] = ()


def is_identifiable_combination(A, c) -> bool:
    """c^T theta is determined by A theta (+ b) on R^p  <=>  c in rowspace(A)."""
    Aq = _exact_matrix(A)
    cq = _exact_matrix([c])[0]
    if len(cq) != len(Aq[0]):
        raise ScopeViolationError("combination vector length must equal the number of parameters")
    return exact_rank(Aq + [cq]) == exact_rank(Aq)


def analyze_affine_identifiability(A, b=None, *, observation=None, parameter_domain: Optional[RationalBox] = None) -> AffineIdentifiabilityReport:
    Aq = _exact_matrix(A)
    m, p = len(Aq), len(Aq[0])
    bq = [Fraction(0)] * m if b is None else _exact_matrix([b])[0]
    if len(bq) != m:
        raise ScopeViolationError("b must have one entry per observation row")
    rank = exact_rank(Aq)
    null = tuple(tuple(v) for v in exact_null_space(Aq, p)) if rank < p else ()
    domain_text = "R^p (unrestricted)" if parameter_domain is None else f"rational box {parameter_domain.describe()['bounds']}"
    notes = []
    if parameter_domain is not None and parameter_domain.dim != p:
        raise ScopeViolationError("parameter_domain dimension must equal the number of parameters")
    if observation is None:
        return AffineIdentifiabilityReport(rank, p, null, rank == p, domain_text,
                                           notes=("global statement on R^p; a restricted domain can shrink fibres",))
    z = _exact_matrix([observation])[0]
    if len(z) != m:
        raise ScopeViolationError("observation length must equal the number of rows")
    theta0 = _solve_particular(Aq, [zi - bi for zi, bi in zip(z, bq)])
    if theta0 is None:
        return AffineIdentifiabilityReport(rank, p, null, rank == p, domain_text, tuple(z), False,
                                           notes=("observation not in the image of the model: empty fibre (a model/data mismatch, not identification)",))
    restriction, t_range = "not_applicable", None
    if parameter_domain is not None:
        if not null:
            inside = all(lo <= x <= hi for x, (lo, hi) in zip(theta0, parameter_domain.bounds))
            restriction = "exact" if inside else "empty"
        elif len(null) == 1:
            v = null[0]
            lo_t, hi_t = None, None
            empty = False
            for x0, vi, (lo, hi) in zip(theta0, v, parameter_domain.bounds):
                if vi == 0:
                    if not (lo <= x0 <= hi):
                        empty = True
                    continue
                a, c = (lo - x0) / vi, (hi - x0) / vi
                a, c = min(a, c), max(a, c)
                lo_t = a if lo_t is None else max(lo_t, a)
                hi_t = c if hi_t is None else min(hi_t, c)
            if empty or (lo_t is not None and lo_t > hi_t):
                restriction = "empty"
            else:
                restriction, t_range = "exact", (lo_t, hi_t)
                if lo_t == hi_t:
                    notes.append("the domain restriction leaves a single parameter point: identified ON THIS DOMAIN only")
        else:
            restriction = "not_evaluated"
            notes.append("null space of dimension > 1: the restriction of the fibre to the box is not evaluated (would need LP)")
    return AffineIdentifiabilityReport(rank, p, null, rank == p, domain_text, tuple(z), True, tuple(theta0), t_range, restriction, tuple(notes))


__all__ = ["AffineIdentifiabilityReport", "is_identifiable_combination", "analyze_affine_identifiability"]
