"""Existing Markov reduction bounds as contracts (Paket J11, plan section 17).

Connects ``closure/error_bounds.py`` (Michel & Siegle 2024, S16) to the J4
contract structure. It does NOT implement a second reduction procedure:
the existing ``transient_reduction_bound`` is called as-is, and its float
result is reported as a ``floating_point_estimate``. When all inputs are
exact rationals and the hypotheses of Theorem 4 item 3 (DTMC) or Theorem 5
item 3 (CTMC) are verified EXACTLY, the same closed-form bound

    ||p_0 P^k - pi_0 Pi^k A||_1  <=  ||pi_0 A - p_0||_1 + k ||Pi A - A P||_inf

is additionally evaluated in exact rational arithmetic; only that value
carries a ``proved`` verdict. A float evaluation of a theoretical bound is
not a validated enclosure without rounding analysis (plan section 17).

Conventions checked (plan section 17 Pflichtprüfungen):

- row-vector convention: P, Pi row-stochastic (DTMC) or generators with
  zero row sums (CTMC); a column-stochastic matrix is reported as a
  possible ORIENTATION error, not silently transposed;
- lifting A (reduced -> full): rows nonnegative and summing to 1 for the
  TV statement; TV = L1/2 only for differences of probability vectors;
- the matrix inf-norm is the maximum absolute ROW sum;
- the reduction contract's state names and clock must match the
  observation link it is composed with (via J4 ``compose_correspondences``).

A downstream decision gets a guarantee only through a declared observation
operator with a stated norm bound (``observation_link``); none is implied.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
from typing import Optional, Sequence, Tuple

import numpy as np

from scoped_correspondence.assurance.records import ProofReport
from scoped_correspondence.closure.error_bounds import SOURCE, THM4_3, THM5_3, transient_reduction_bound
from scoped_correspondence.correspondence.composition import CorrespondenceLink, LipschitzCertificate, Side
from scoped_correspondence.correspondence.domains import AffineMap, RationalBox
from scoped_correspondence.errors import ScopeViolationError

Matrix = Sequence[Sequence]


def _is_exact(x) -> bool:
    return isinstance(x, (int, Fraction)) and not isinstance(x, bool)


def _all_exact(*mats) -> bool:
    for m in mats:
        for row in (m if isinstance(m[0], (list, tuple)) else [m]):
            if not all(_is_exact(v) for v in row):
                return False
    return True


def _F(m):
    if isinstance(m[0], (list, tuple)):
        return [[Fraction(v) for v in row] for row in m]
    return [Fraction(v) for v in m]


def _shape(m) -> Tuple[int, int]:
    return len(m), len(m[0])


def _row_sums(m):
    return [sum(row) for row in m]


def _col_sums(m):
    return [sum(m[i][j] for i in range(len(m))) for j in range(len(m[0]))]


def _matmul(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(len(b))) for j in range(len(b[0]))] for i in range(len(a))]


def _vecmat(v, m):
    return [sum(v[i] * m[i][j] for i in range(len(v))) for j in range(len(m[0]))]


@dataclass(frozen=True)
class ReductionContract:
    name: str
    full_states: Tuple[str, ...]
    reduced_states: Tuple[str, ...]
    clock: str  # e.g. "steps" (DTMC) or "time:h" (CTMC); must match composed links
    continuous_time: bool
    horizon: Fraction  # k (integer) or t
    norm: str = "L1"

    def __post_init__(self) -> None:
        if self.norm not in ("L1", "TV"):
            raise ScopeViolationError("norm must be 'L1' or 'TV'")
        h = self.horizon
        if isinstance(h, bool) or isinstance(h, float) or not isinstance(h, (int, Fraction)):
            raise ScopeViolationError("horizon must be exact (int/Fraction)")
        object.__setattr__(self, "horizon", Fraction(h))
        if self.horizon < 0:
            raise ScopeViolationError("horizon must be >= 0")
        if not self.continuous_time and self.horizon.denominator != 1:
            raise ScopeViolationError("DTMC horizon must be an integer number of steps")
        if self.continuous_time == (self.clock == "steps"):
            raise ScopeViolationError("clock 'steps' is for DTMC only; a CTMC needs a continuous clock label")


@dataclass(frozen=True)
class ReductionContractReport:
    report: ProofReport
    exact_bound: Optional[Fraction]
    float_bound: Optional[float]  # None when the existing function could not be called
    float_theorem: str
    hypotheses: Tuple[str, ...]
    violations: Tuple[str, ...]
    observed_error_l1: Optional[Fraction] = None
    notes: Tuple[str, ...] = field(default_factory=tuple)


def check_hypotheses(Pi, A, P, pi0, p0, contract: ReductionContract) -> Tuple[Tuple[str, ...], Tuple[str, ...]]:
    """Exact (for exact inputs) or tolerance-free structural checks. Returns
    (satisfied hypotheses, violations)."""
    ok, bad = [], []
    n, m = len(contract.full_states), len(contract.reduced_states)
    if _shape(P) != (n, n):
        bad.append(f"full-chain matrix shape {_shape(P)} does not match {n} declared full states")
    if _shape(Pi) != (m, m):
        bad.append(f"reduced matrix shape {_shape(Pi)} does not match {m} declared reduced states")
    if _shape(A) != (m, n):
        bad.append(f"lifting A must be reduced x full = {m}x{n} (row convention), got {_shape(A)}")
    if len(pi0) != m or len(p0) != n:
        bad.append("initial vectors do not match the declared state spaces")
    if bad:
        return tuple(ok), tuple(bad)
    exact = _all_exact(Pi, A, P, pi0, p0)
    eq = (lambda a, b: a == b) if exact else (lambda a, b: abs(a - b) <= 1e-12)
    target = 0 if contract.continuous_time else 1
    for label, M in (("full", P), ("reduced", Pi)):
        rs = _row_sums(M)
        if all(eq(s, target) for s in rs) and (contract.continuous_time or all(v >= 0 for row in M for v in row)):
            ok.append(f"{label} matrix rows sum to {target} (row-vector convention)")
        else:
            cs = _col_sums(M)
            hint = " -- columns sum to the target: possibly transposed (orientation)" if all(eq(s, target) for s in cs) else ""
            bad.append(f"{label} matrix is not {'a generator' if contract.continuous_time else 'row-stochastic'}{hint}")
        if contract.continuous_time and any(M[i][j] < 0 for i in range(len(M)) for j in range(len(M)) if i != j):
            bad.append(f"{label} generator has negative off-diagonal entries")
    if all(v >= 0 for v in pi0) and eq(sum(pi0), 1):
        ok.append("pi0 is a probability vector")
    else:
        bad.append("pi0 is not a probability vector (item-3 hypothesis)")
    lifting_stochastic = all(v >= 0 for row in A for v in row) and all(eq(s, 1) for s in _row_sums(A))
    p0_prob = all(v >= 0 for v in p0) and eq(sum(p0), 1)
    if lifting_stochastic:
        ok.append("lifting A is row-stochastic (each reduced state lifts to a distribution)")
    if p0_prob:
        ok.append("p0 is a probability vector")
    if contract.norm == "TV" and not (lifting_stochastic and p0_prob):
        bad.append("TV = L1/2 requires differences of probability vectors: stochastic lifting A and probability p0")
    return tuple(ok), tuple(bad)


def reduction_contract_report(Pi: Matrix, A: Matrix, P: Matrix, pi0, p0, contract: ReductionContract,
                              *, observe_exact_error: bool = True) -> ReductionContractReport:
    hyp, viol = check_hypotheses(Pi, A, P, pi0, p0, contract)
    k = contract.horizon
    # The existing float function is only called on structurally valid input;
    # with ANY violation it is not consulted (its own fallbacks, e.g. Thm 4.2
    # for a non-stochastic Pi, would otherwise produce a number for a
    # contract whose hypotheses failed).
    fb = None if viol else transient_reduction_bound(
        np.array(Pi, dtype=float), np.array(A, dtype=float), np.array(P, dtype=float),
        np.array(pi0, dtype=float), np.array(p0, dtype=float),
        float(k) if contract.continuous_time else int(k),
        continuous_time=contract.continuous_time, norm=contract.norm)
    float_bound = None if fb is None else fb.bound
    theorem = "" if fb is None else fb.theorem_ref
    claim = f"||e_{k}||_{'TV' if contract.norm == 'TV' else '1'} <= bound for {contract.name}"
    common = dict(claim=claim, method="closure.contract_adapter (Michel & Siegle Thm 4.3 / 5.3)",
                  depends_on=(SOURCE, THM5_3 if contract.continuous_time else THM4_3))
    if viol:
        rep = ProofReport(verdict="undecided", procedure_status="invalid_input", evidence_kind="not_evaluated",
                          arithmetic="boolean", reasons=viol, **common)
        return ReductionContractReport(rep, None, float_bound, theorem, hyp, viol)
    if not _all_exact(Pi, A, P, pi0, p0):
        rep = ProofReport(verdict="undecided", procedure_status="completed", evidence_kind="analytic_argument",
                          arithmetic="floating_point_estimate",
                          reasons=("inputs are floats: the theorem bound was evaluated in floating point only; "
                                   "not a validated enclosure without rounding analysis",),
                          values={"float_bound": float_bound, "theorem": theorem}, **common)
        return ReductionContractReport(rep, None, float_bound, theorem, hyp, viol)
    Pi_q, A_q, P_q, pi_q, p_q = _F(Pi), _F(A), _F(P), _F(pi0), _F(p0)
    resid = [[a - b for a, b in zip(r1, r2)] for r1, r2 in zip(_matmul(Pi_q, A_q), _matmul(A_q, P_q))]
    r_inf = max(sum(abs(v) for v in row) for row in resid)  # max absolute ROW sum
    e0 = sum(abs(a - b) for a, b in zip(_vecmat(pi_q, A_q), p_q))
    l1 = e0 + k * r_inf
    exact_bound = l1 / 2 if contract.norm == "TV" else l1
    observed = None
    notes = []
    if observe_exact_error and not contract.continuous_time:
        p_k, pi_k = list(p_q), list(pi_q)
        for _ in range(int(k)):
            p_k, pi_k = _vecmat(p_k, P_q), _vecmat(pi_k, Pi_q)
        err = sum(abs(a - b) for a, b in zip(p_k, _vecmat(pi_k, A_q)))
        observed = err / 2 if contract.norm == "TV" else err
        if observed > exact_bound:
            raise AssertionError("internal: exact error exceeds the theorem bound -- hypotheses or orientation wrong")
        notes.append(f"exact error at horizon: {observed} <= bound {exact_bound}")
    rep = ProofReport(verdict="proved", procedure_status="completed", evidence_kind="analytic_argument",
                      arithmetic="exact_rational", conclusion_complete=True,
                      reasons=(f"hypotheses verified exactly: {'; '.join(hyp)}",
                               "bound evaluated in exact rational arithmetic"),
                      values={"initial_error_l1": e0, "residual_inf_norm": r_inf, "horizon": k, "bound": exact_bound,
                              "float_bound_existing_function": float_bound, "observed_error": observed},
                      **common)
    if abs(float(exact_bound) - float_bound) > 1e-12 * max(1.0, float(exact_bound)):
        notes.append(f"WARNING: existing float bound {float_bound} differs from exact {exact_bound}")
    return ReductionContractReport(rep, exact_bound, float_bound, theorem, hyp, viol, observed, tuple(notes))


def reduction_link(contract: ReductionContract, A: Matrix, result: ReductionContractReport,
                   *, model_full: str, model_reduced: str) -> CorrespondenceLink:
    """J4 link 'reduced distribution -> full distribution' (pi -> pi A) whose
    flow error bound is the reduction bound (in the contract's norm).
    Only an exactly PROVED bound is passed on as analytic evidence."""
    if result.exact_bound is None or result.report.verdict != "proved":
        raise ScopeViolationError("only an exactly proved reduction bound can become a contract flow bound")
    A_q = _F(A)
    m, n = len(contract.reduced_states), len(contract.full_states)
    lift = AffineMap(tuple(tuple(A_q[i][j] for i in range(m)) for j in range(n)), tuple(Fraction(0) for _ in range(n)), "lift_A")
    unit = (f"probability[{contract.norm}]",)
    return CorrespondenceLink(
        name=f"reduction_{contract.name}",
        source=Side(model_reduced, contract.reduced_states, unit * m, contract.clock),
        target=Side(model_full, contract.full_states, unit * n, contract.clock),
        state_map=lift, time_factor=Fraction(1), domain=RationalBox(tuple((0, 1) for _ in range(m))),
        horizon=contract.horizon, flow_error_bound=result.exact_bound, flow_error_evidence="analytic_argument",
    )


def observation_link(contract: ReductionContract, weights: Sequence, *, model_full: str, observable: str) -> CorrespondenceLink:
    """Linear observable y = f . p of the full distribution, with the exact
    Hoelder certificate |f . e| <= max_i |f_i| * ||e||_1 (L1 norm). For a TV
    contract the constant doubles (||e||_1 = 2 TV)."""
    f = [Fraction(w) for w in weights] if all(_is_exact(w) for w in weights) else None
    if f is None:
        raise ScopeViolationError("observable weights must be exact")
    n = len(contract.full_states)
    if len(f) != n:
        raise ScopeViolationError("one weight per full state required")
    L = max(abs(w) for w in f) * (2 if contract.norm == "TV" else 1)
    unit = (f"probability[{contract.norm}]",)
    return CorrespondenceLink(
        name=f"observe_{observable}",
        source=Side(model_full, contract.full_states, unit * n, contract.clock),
        target=Side(f"{model_full}:{observable}", (observable,), ("observable",), contract.clock),
        state_map=AffineMap((tuple(f),), (Fraction(0),), observable), time_factor=Fraction(1),
        domain=RationalBox(tuple((0, 1) for _ in range(n))), horizon=contract.horizon,
        flow_error_bound=Fraction(0), flow_error_evidence="analytic_argument",
        lipschitz=LipschitzCertificate(L, RationalBox(tuple((0, 1) for _ in range(n))), True,
                                       f"exact Hoelder: |f.e| <= max|f| ||e||_1{' = 2 max|f| TV' if contract.norm == 'TV' else ''}"),
    )


__all__ = ["ReductionContract", "ReductionContractReport", "check_hypotheses", "reduction_contract_report",
           "reduction_link", "observation_link"]
