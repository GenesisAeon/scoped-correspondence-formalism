"""Universal bounds over whole rational boxes (Paket J5, plan section 11.2).

``certify_bound(expr, box, epsilon, budget, side)`` decides the claim

    for all x in box:  expr(x) <= epsilon      (side="upper")
    for all x in box:  expr(x) >= epsilon      (side="lower")

for the supported expression class (``assurance.expressions``), by:

1. validating expression, box, epsilon and budget;
2. computing the natural interval enclosure on a box;
3. if the enclosure already implies the bound -> the box is PROVED;
4. if an exactly evaluated point (midpoint, then corners) violates the
   bound -> COUNTEREXAMPLE (refuted; the rest of the domain need not be
   scanned); a box whose whole enclosure violates is also a witness;
5. otherwise bisect deterministically (widest axis, ties -> first
   variable in sorted order); the two halves cover the parent exactly;
6. at budget end the unresolved boxes are returned; no universal success.

A zero denominator at an exactly evaluated point gives
``undefined_on_domain`` with that point as witness. A denominator
enclosure containing 0 without such a point is only "not yet resolved"
(subdivide). An empty box makes the claim vacuously true and is flagged.

Every proved result stores the partition with its enclosures and can be
re-checked independently by ``recheck_certificate``. Numerical ODE output
is not a validated flow; this module proves algebraic statements only.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from fractions import Fraction
from itertools import product
from typing import Dict, List, Mapping, Optional, Tuple

from scoped_correspondence.assurance.expressions import Expr, UndefinedAtPoint, enclose, evaluate, to_text, validate
from scoped_correspondence.assurance.rational_intervals import DenominatorContainsZero, Interval
from scoped_correspondence.assurance.records import ProofReport
from scoped_correspondence.errors import ScopeViolationError

Box = Dict[str, Interval]


def _q(x, what) -> Fraction:
    if isinstance(x, bool) or isinstance(x, float) or not isinstance(x, (int, Fraction, str)):
        raise ScopeViolationError(f"{what} must be exact (int, Fraction or decimal string)")
    return Fraction(x)


def make_box(bounds: Mapping[str, Tuple]) -> Optional[Box]:
    """Exact box from {var: (lo, hi)}. Returns None for an EMPTY box
    (some lo > hi) so callers cannot silently use it."""
    out = {}
    for k, (lo, hi) in bounds.items():
        lo, hi = _q(lo, f"lower bound of {k}"), _q(hi, f"upper bound of {k}")
        if lo > hi:
            return None
        out[k] = Interval(lo, hi)
    return out


def _split(box: Box) -> Tuple[Box, Box]:
    names = sorted(box)
    widest = max(names, key=lambda n: (box[n].width, -names.index(n)))
    iv = box[widest]
    mid = (iv.lo + iv.hi) / 2
    left, right = dict(box), dict(box)
    left[widest] = Interval(iv.lo, mid)
    right[widest] = Interval(mid, iv.hi)
    return left, right


def _points(box: Box):
    names = sorted(box)
    yield {n: (box[n].lo + box[n].hi) / 2 for n in names}
    for corner in product(*[(box[n].lo, box[n].hi) for n in names]):
        yield dict(zip(names, corner))


def _ok(value: Fraction, eps: Fraction, side: str) -> bool:
    return value <= eps if side == "upper" else value >= eps


def _box_text(box: Box) -> Dict[str, List[str]]:
    return {n: [str(box[n].lo), str(box[n].hi)] for n in sorted(box)}


@dataclass(frozen=True)
class BoundCertificate:
    """Re-checkable content of a proved bound: expression, side, epsilon,
    domain and the partition with each box's enclosure."""

    expression: Expr
    side: str
    epsilon: Fraction
    domain: Box
    partition: Tuple[Tuple[Box, Interval], ...]


def certify_bound(expr: Expr, bounds: Mapping[str, Tuple], epsilon, *, budget: int = 4096, side: str = "upper") -> Tuple[ProofReport, Optional[BoundCertificate]]:
    if side not in ("upper", "lower"):
        raise ScopeViolationError("side must be 'upper' or 'lower'")
    if isinstance(budget, bool) or not isinstance(budget, int) or budget < 1:
        raise ScopeViolationError("budget must be an int >= 1")
    eps = _q(epsilon, "epsilon")
    names = validate(expr)
    missing = set(names) - set(bounds)
    if missing:
        raise ScopeViolationError(f"box does not bound the variable(s) {sorted(missing)}")
    claim = f"for all x in box: {to_text(expr)} {'<=' if side == 'upper' else '>='} {eps}"
    box = make_box(bounds)
    base = dict(claim=claim, method="assurance.scope_certification.certify_bound (natural interval extension + bisection)",
                arithmetic="exact_rational", declared_domain={k: [str(a), str(b)] for k, (a, b) in ((k, (Fraction(v[0]), Fraction(v[1]))) for k, v in bounds.items())})
    if box is None:
        return ProofReport(verdict="proved", procedure_status="completed", evidence_kind="analytic_argument",
                           empty_domain=True, conclusion_complete=True, reasons=("empty box: vacuously true, not a usable guarantee",), **base), None
    queue = deque([box])
    proved: List[Tuple[Box, Interval]] = []
    evaluations = 0
    singular_boxes = 0
    while queue:
        if evaluations >= budget:
            residual = [_box_text(b) for b in queue]
            return ProofReport(verdict="undecided", procedure_status="budget_exhausted", evidence_kind="not_evaluated",
                               conclusion_complete=False, domain_exhausted=False, witnesses=tuple(residual),
                               reasons=(f"budget {budget} exhausted with {len(queue)} unresolved box(es); proved {len(proved)}",
                                        "a budget stop proves nothing universal")
                                       + ((f"{singular_boxes} denominator enclosure(s) contained 0: the expression may be "
                                           "undefined or unbounded near the residual boxes (definition precondition not established)",)
                                          if singular_boxes else ()),
                               values={"evaluations": evaluations, "proved_boxes": len(proved), "unresolved_boxes": len(queue),
                                       "singular_enclosures_split": singular_boxes}, **base), None
        b = queue.popleft()
        evaluations += 1
        # exact point checks first: a counterexample or a singular point ends the search
        for p in _points(b):
            try:
                v = evaluate(expr, p)
            except UndefinedAtPoint:
                return ProofReport(verdict="undefined_on_domain", procedure_status="completed", evidence_kind="analytic_argument",
                                   conclusion_complete=True, witnesses=({k: str(x) for k, x in p.items()},),
                                   reasons=("zero denominator at an exactly evaluated point of the domain",),
                                   values={"evaluations": evaluations}, **base), None
            if not _ok(v, eps, side):
                return ProofReport(verdict="refuted", procedure_status="completed", evidence_kind="analytic_argument",
                                   conclusion_complete=True, domain_exhausted=False,
                                   witnesses=({k: str(x) for k, x in p.items()},),
                                   reasons=(f"counterexample: value {v} violates the bound",),
                                   values={"evaluations": evaluations, "counterexample_value": v}, **base), None
        try:
            enc = enclose(expr, b)
        except DenominatorContainsZero:
            singular_boxes += 1
            if all(iv.width == 0 for iv in b.values()):
                continue  # unreachable: a point box would have raised UndefinedAtPoint above
            queue.extend(_split(b))
            continue
        if (enc.hi <= eps) if side == "upper" else (enc.lo >= eps):
            proved.append((b, enc))
        elif (enc.lo > eps) if side == "upper" else (enc.hi < eps):
            # cannot happen without a violating point (enclosure contains the image), kept as a guard
            raise AssertionError("internal: enclosure excludes the bound but no violating point was found")
        elif all(iv.width == 0 for iv in b.values()):
            proved.append((b, enc))  # point box: exact value already checked
        else:
            queue.extend(_split(b))
    cert = BoundCertificate(expr, side, eps, box, tuple(proved))
    return ProofReport(verdict="proved", procedure_status="completed", evidence_kind="analytic_argument",
                       conclusion_complete=True, domain_exhausted=True,
                       reasons=(f"{len(proved)} box(es) proved by exact rational enclosure", "partition covers the domain"),
                       depends_on=("assurance.rational_intervals.Interval (exact natural extension)",),
                       values={"evaluations": evaluations, "proved_boxes": len(proved), "singular_enclosures_split": singular_boxes,
                               "max_enclosure": max((e.hi for _, e in proved), default=None) if side == "upper" else None,
                               "min_enclosure": min((e.lo for _, e in proved), default=None) if side == "lower" else None},
                       **base), cert


def certify_abs_bound(expr: Expr, bounds: Mapping[str, Tuple], epsilon, *, budget: int = 4096) -> Tuple[ProofReport, ProofReport]:
    """|expr| <= epsilon as two separate claims (upper and lower); both
    reports are returned unchanged -- no merged verdict."""
    from scoped_correspondence.assurance.expressions import Neg

    up, _ = certify_bound(expr, bounds, epsilon, budget=budget, side="upper")
    lo, _ = certify_bound(Neg(expr), bounds, epsilon, budget=budget, side="upper")
    return up, lo


def _volume(box: Box, axes) -> Fraction:
    v = Fraction(1)
    for n in axes:
        v *= box[n].width
    return v


def recheck_certificate(cert: BoundCertificate) -> Tuple[bool, List[str]]:
    """Independent re-check of a stored certificate: each partition box lies
    in the domain, its stored enclosure is reproduced exactly and implies the
    bound, boxes do not overlap in volume, and their volumes sum to the
    domain volume (over the non-degenerate axes)."""
    problems: List[str] = []
    axes = [n for n in sorted(cert.domain) if cert.domain[n].width > 0]
    total = Fraction(0)
    for i, (b, enc) in enumerate(cert.partition):
        if any(not (cert.domain[n].lo <= b[n].lo and b[n].hi <= cert.domain[n].hi) for n in cert.domain):
            problems.append(f"box {i} not inside the domain")
        try:
            again = enclose(cert.expression, b)
        except DenominatorContainsZero:
            problems.append(f"box {i}: enclosure no longer computable")
            continue
        if again != enc:
            problems.append(f"box {i}: stored enclosure not reproduced")
        if (cert.side == "upper" and again.hi > cert.epsilon) or (cert.side == "lower" and again.lo < cert.epsilon):
            if not all(b[n].width == 0 for n in b):
                problems.append(f"box {i}: enclosure does not imply the bound")
        total += _volume(b, axes)
    for i in range(len(cert.partition)):
        for j in range(i + 1, len(cert.partition)):
            bi, bj = cert.partition[i][0], cert.partition[j][0]
            overlap = Fraction(1)
            for n in axes:
                overlap *= max(Fraction(0), min(bi[n].hi, bj[n].hi) - max(bi[n].lo, bj[n].lo))
            if overlap > 0:
                problems.append(f"boxes {i} and {j} overlap")
    if axes and total != _volume(cert.domain, axes):
        problems.append(f"partition volume {total} != domain volume {_volume(cert.domain, axes)}")
    return (not problems), problems


__all__ = ["make_box", "BoundCertificate", "certify_bound", "certify_abs_bound", "recheck_certificate"]
