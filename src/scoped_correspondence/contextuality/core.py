"""Contextuality core (F08 port + F13 scope guard).

1:1 port of verification/verify_sheaf_contextuality.py EmpiricalModel / CF API
into the review package. Mapping: sheaf_contextuality.md §§2–6 / F13.

Primary sources:
  arXiv:1102.0264  Abramsky & Brandenburger
  arXiv:1705.07918 Abramsky, Barbosa & Mansfield
"""
from __future__ import annotations

import itertools
from dataclasses import dataclass

import numpy as np

from scoped_correspondence.errors import ScopeViolationError

try:
    from scipy.optimize import linprog

    HAS_SCIPY = True
except ImportError:  # pragma: no cover
    HAS_SCIPY = False
    linprog = None


ARXIV_AB = "https://arxiv.org/abs/1102.0264"
ARXIV_CF = "https://arxiv.org/abs/1705.07918"
TOL = 1e-8

# F13 / sheaf_contextuality.md §6 — forced conscious decision (not auto-checkable).
F13_SCOPE_RISK = (
    "F13 / sheaf_contextuality.md §6: if all views y_α=π_α(z,c,t) are functions of "
    "the same assumed z, a joint distribution always exists trivially; positive CF "
    "would then be a modeling error, not true contextuality. Caller must actively "
    "pass assumes_independent_contexts=True only when per-context empirical models "
    "are independently specified primitives (not projections of one shared state)."
)


def require(ok, msg):
    if not bool(ok):
        raise AssertionError(msg)


def near(a, b, atol=1e-8, rtol=1e-7):
    if not np.allclose(a, b, atol=atol, rtol=rtol):
        raise AssertionError(f"{a!r} != {b!r}")


def _require_independent_contexts(assumes_independent_contexts) -> None:
    """No silent default: only explicit True proceeds (F13 scope guard)."""
    if assumes_independent_contexts is not True:
        raise ScopeViolationError(F13_SCOPE_RISK)


@dataclass(frozen=True)
class SheafScenario:
    """Measurement scenario <X, M, O> (Abramsky-Brandenburger)."""

    measurements: tuple
    contexts: tuple  # each context is a frozenset/tuple of measurement names
    outcomes: tuple

    def __post_init__(self):
        object.__setattr__(self, "measurements", tuple(self.measurements))
        object.__setattr__(self, "outcomes", tuple(self.outcomes))
        ctx = tuple(tuple(sorted(c)) for c in self.contexts)
        object.__setattr__(self, "contexts", ctx)

    @property
    def n_global(self):
        return len(self.outcomes) ** len(self.measurements)

    def global_assignments(self):
        for vals in itertools.product(self.outcomes, repeat=len(self.measurements)):
            yield dict(zip(self.measurements, vals))

    def local_sections(self, context):
        for vals in itertools.product(self.outcomes, repeat=len(context)):
            yield dict(zip(context, vals))


def bell_222_scenario():
    """Canonical (2,2,2) Alice/Bob Bell scenario."""
    X = ("a1", "a2", "b1", "b2")
    M = (("a1", "b1"), ("a1", "b2"), ("a2", "b1"), ("a2", "b2"))
    return SheafScenario(X, M, (0, 1))


class EmpiricalModel:
    """Family of local distributions e_C on O^C with margin compatibility."""

    def __init__(self, scenario: SheafScenario, tables: dict, check_margins: bool = True):
        self.scenario = scenario
        self.tables = {}
        for ctx in scenario.contexts:
            key = tuple(ctx)
            require(key in tables, f"missing table for context {key}")
            tab = {}
            for sec, p in tables[key].items():
                if isinstance(sec, tuple) and sec and isinstance(sec[0], tuple):
                    sk = tuple(sorted(sec))
                elif isinstance(sec, str):
                    sk = _section_key(dict(zip(ctx, (int(c) for c in sec))))
                elif isinstance(sec, dict):
                    sk = _section_key(sec)
                elif isinstance(sec, (tuple, list)):
                    sk = _section_key(dict(zip(ctx, sec)))
                else:
                    raise TypeError(f"bad section key type: {type(sec)}")
                tab[sk] = float(p)
            total = sum(tab.values())
            near(total, 1.0, atol=1e-9)
            self.tables[key] = tab
        self.compatible_margins = self._check_margins() if check_margins else True
        if check_margins:
            require(self.compatible_margins, "incompatible margins (signalling)")

    @classmethod
    def from_tables(cls, scenario, tables, check_margins=True):
        return cls(scenario, tables, check_margins=check_margins)

    def _check_margins(self):
        for c1, c2 in itertools.combinations(self.scenario.contexts, 2):
            inter = tuple(sorted(set(c1) & set(c2)))
            if not inter:
                continue
            m1 = self._marginal(c1, inter)
            m2 = self._marginal(c2, inter)
            for key in set(m1) | set(m2):
                if abs(m1.get(key, 0.0) - m2.get(key, 0.0)) > TOL:
                    return False
        return True

    def _marginal(self, context, subset):
        tab = self.tables[tuple(context)]
        out = {}
        for assign_items, p in tab.items():
            assign = dict(assign_items)
            key = tuple(sorted((m, assign[m]) for m in subset))
            out[key] = out.get(key, 0.0) + p
        return out

    def vector(self):
        """Flattened probability vector v^e indexed by <C,s>."""
        rows = []
        for ctx in self.scenario.contexts:
            for sec in self.scenario.local_sections(ctx):
                key = tuple(sorted(sec.items()))
                rows.append(self.tables[tuple(ctx)].get(key, 0.0))
        return np.asarray(rows, dtype=float)

    def incidence_matrix(self):
        """Incidence matrix M[<C,s>, g] = 1 iff g|_C = s."""
        globals_ = list(self.scenario.global_assignments())
        rows = []
        for ctx in self.scenario.contexts:
            for sec in self.scenario.local_sections(ctx):
                row = []
                for g in globals_:
                    ok = all(g[m] == sec[m] for m in ctx)
                    row.append(1.0 if ok else 0.0)
                rows.append(row)
        return np.asarray(rows, dtype=float), globals_


def _solve_lp_max_ones(M, v):
    """max 1·b s.t. M b <= v, b >= 0. Returns (optimum, b*)."""
    n = M.shape[1]
    c = -np.ones(n)
    bounds = [(0, None)] * n
    if HAS_SCIPY:
        res = linprog(c, A_ub=M, b_ub=v, bounds=bounds, method="highs")
        require(res.success, f"linprog failed: {res.message}")
        b = np.maximum(res.x, 0.0)
        return float(b.sum()), b
    b = np.zeros(n)
    step = 0.05
    for _ in range(20000):
        slack = v - M @ b
        viol = slack < -1e-12
        if viol.any():
            b = np.maximum(b - 0.1 * (M.T @ np.maximum(-slack, 0)), 0)
            continue
        room = M.T @ (slack > 1e-9).astype(float)
        b = np.maximum(b + step * (1.0 + 0.01 * room), 0)
        Mb = M @ b
        ratios = []
        for i in range(len(v)):
            if Mb[i] > v[i] + 1e-12 and Mb[i] > 0:
                ratios.append(v[i] / Mb[i])
        if ratios:
            b *= min(ratios)
    return float(b.sum()), b


def contextual_fraction(model: EmpiricalModel, assumes_independent_contexts=None):
    """Contextual fraction CF = 1 - NCF (Abramsky–Barbosa–Mansfield).

    F13 scope guard: assumes_independent_contexts must be passed as True.
    False or missing → ScopeViolationError (no silent default).
    """
    _require_independent_contexts(assumes_independent_contexts)
    M, _ = model.incidence_matrix()
    v = model.vector()
    ncf, b = _solve_lp_max_ones(M, v)
    ncf = min(max(ncf, 0.0), 1.0)
    cf = 1.0 - ncf
    return {"NCF": ncf, "CF": cf, "b_weight": float(b.sum())}


def has_global_section(model: EmpiricalModel, assumes_independent_contexts=None, atol=TOL):
    """Exact feasibility of M d = v, d >= 0 (non-contextuality).

    F13 scope guard: assumes_independent_contexts must be passed as True.
    False or missing → ScopeViolationError (no silent default).
    """
    _require_independent_contexts(assumes_independent_contexts)
    M, _ = model.incidence_matrix()
    v = model.vector()
    n = M.shape[1]
    if HAS_SCIPY:
        c = np.zeros(n)
        res = linprog(c, A_eq=M, b_eq=v, bounds=[(0, None)] * n, method="highs")
        if res.success and abs(res.x.sum() - 1.0) <= 1e-6:
            return True
        return (
            contextual_fraction(model, assumes_independent_contexts=True)["CF"] <= atol
        )
    return contextual_fraction(model, assumes_independent_contexts=True)["CF"] <= atol


def report(model: EmpiricalModel, assumes_independent_contexts=None):
    """Bundle CF / global-section report (requires F13 confirmation)."""
    _require_independent_contexts(assumes_independent_contexts)
    cf = contextual_fraction(model, assumes_independent_contexts=True)
    return {
        "compatible_margins": bool(model.compatible_margins),
        "NCF": cf["NCF"],
        "CF": cf["CF"],
        "has_global_section": has_global_section(model, assumes_independent_contexts=True),
        "arxiv_ab": ARXIV_AB,
        "arxiv_cf": ARXIV_CF,
        "lp_backend": "scipy.optimize.linprog" if HAS_SCIPY else "numpy_projected_ascent",
        "assumes_independent_contexts": True,
    }


def _section_key(assign):
    return tuple(sorted(assign.items()))


def _table_from_flat(ctx, probs_00_01_10_11):
    """Map flat (00,01,10,11) probs to section dict for a 2-measurement context."""
    keys = ((0, 0), (0, 1), (1, 0), (1, 1))
    out = {}
    for k, p in zip(keys, probs_00_01_10_11):
        out[_section_key(dict(zip(ctx, k)))] = float(p)
    return out


def classical_factorizable_model(scenario):
    """Independent fair coins: P(ab|xy)=1/4 — non-contextual, CF=0."""
    tables = {}
    for ctx in scenario.contexts:
        tables[tuple(ctx)] = _table_from_flat(ctx, (0.25, 0.25, 0.25, 0.25))
    return EmpiricalModel.from_tables(scenario, tables)


def pr_box_model(scenario):
    """PR-box (Table I right, arXiv:1705.07918): strong contextuality, CF=1."""
    tables = {}
    xy = {
        ("a1", "b1"): (0, 0),
        ("a1", "b2"): (0, 1),
        ("a2", "b1"): (1, 0),
        ("a2", "b2"): (1, 1),
    }
    for ctx in scenario.contexts:
        x, y = xy[tuple(ctx)]
        target = (x * y) % 2
        probs = []
        for a, b in ((0, 0), (0, 1), (1, 0), (1, 1)):
            probs.append(0.5 if (a ^ b) == target else 0.0)
        tables[tuple(ctx)] = _table_from_flat(ctx, probs)
    return EmpiricalModel.from_tables(scenario, tables)


def chsh_table_i_model(scenario):
    """CHSH QM table from arXiv:1705.07918 Table I (angles 0, pi/3 on |Phi+>)."""
    raw = {
        ("a1", "b1"): (0.5, 0.0, 0.0, 0.5),
        ("a1", "b2"): (3 / 8, 1 / 8, 1 / 8, 3 / 8),
        ("a2", "b1"): (3 / 8, 1 / 8, 1 / 8, 3 / 8),
        ("a2", "b2"): (1 / 8, 3 / 8, 3 / 8, 1 / 8),
    }
    tables = {ctx: _table_from_flat(ctx, raw[ctx]) for ctx in scenario.contexts}
    return EmpiricalModel.from_tables(scenario, tables)
