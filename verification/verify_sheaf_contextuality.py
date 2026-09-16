#!/usr/bin/env python3
"""Synthetic checks for F08 sheaf contextuality (optional module beside VB1).

Implements Abramsky-Brandenburger empirical models and Abramsky-Barbosa-Mansfield
contextual fraction via linear programming. NumPy + SciPy (linprog). Fixed seeds.
Not a mutation of FORMALISM.md / VB1; reports CF for stochastic overlaps separately.

Primary sources:
  arXiv:1102.0264  Abramsky & Brandenburger, New J. Phys. 13 113036 (2011)
  arXiv:1705.07918 Abramsky, Barbosa & Mansfield, Phys. Rev. Lett. 119 050504 (2017)
"""
from __future__ import annotations

import argparse
import datetime as dt
import itertools
import json
import math
from dataclasses import dataclass
from pathlib import Path
import platform

import numpy as np

try:
    from scipy.optimize import linprog
    HAS_SCIPY = True
except ImportError:  # pragma: no cover
    HAS_SCIPY = False
    linprog = None


ARXIV_AB = "https://arxiv.org/abs/1102.0264"
ARXIV_CF = "https://arxiv.org/abs/1705.07918"
TOL = 1e-8


def require(ok, msg):
    if not bool(ok):
        raise AssertionError(msg)


def near(a, b, atol=1e-8, rtol=1e-7):
    if not np.allclose(a, b, atol=atol, rtol=rtol):
        raise AssertionError(f"{a!r} != {b!r}")


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
        # lexicographic product over measurements in order
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
        # For every pair of contexts, marginals on intersection agree
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
    c = -np.ones(n)  # maximise sum b <=> minimise -sum b
    bounds = [(0, None)] * n
    if HAS_SCIPY:
        res = linprog(c, A_ub=M, b_ub=v, bounds=bounds, method="highs")
        require(res.success, f"linprog failed: {res.message}")
        b = np.maximum(res.x, 0.0)
        return float(b.sum()), b
    # Pure-numpy fallback: projected gradient ascent (documented; prefer SciPy)
    b = np.zeros(n)
    step = 0.05
    for _ in range(20000):
        grad = np.ones(n)
        slack = v - M @ b
        # projected: if any constraint tight and would increase, damp
        viol = slack < -1e-12
        if viol.any():
            # pull back
            b = np.maximum(b - 0.1 * (M.T @ np.maximum(-slack, 0)), 0)
            continue
        # feasible direction: increase components with room
        room = M.T @ (slack > 1e-9).astype(float)
        b = np.maximum(b + step * (1.0 + 0.01 * room), 0)
        # re-project onto Mb <= v by scaling if needed
        Mb = M @ b
        ratios = []
        for i in range(len(v)):
            if Mb[i] > v[i] + 1e-12 and Mb[i] > 0:
                ratios.append(v[i] / Mb[i])
        if ratios:
            b *= min(ratios)
    return float(b.sum()), b


def contextual_fraction(model: EmpiricalModel):
    M, _ = model.incidence_matrix()
    v = model.vector()
    ncf, b = _solve_lp_max_ones(M, v)
    ncf = min(max(ncf, 0.0), 1.0)
    cf = 1.0 - ncf
    return {"NCF": ncf, "CF": cf, "b_weight": float(b.sum())}


def has_global_section(model: EmpiricalModel, atol=TOL):
    """Exact feasibility of M d = v, d >= 0, 1·d = 1 (non-contextuality)."""
    M, _ = model.incidence_matrix()
    v = model.vector()
    n = M.shape[1]
    if HAS_SCIPY:
        # minimise 0 s.t. M d = v, d >= 0 (normalisation follows if margins ok)
        c = np.zeros(n)
        res = linprog(c, A_eq=M, b_eq=v, bounds=[(0, None)] * n, method="highs")
        if res.success and abs(res.x.sum() - 1.0) <= 1e-6:
            return True
        # also accept NCF ~ 1
        return contextual_fraction(model)["CF"] <= atol
    return contextual_fraction(model)["CF"] <= atol


def report(model: EmpiricalModel):
    cf = contextual_fraction(model)
    return {
        "compatible_margins": bool(model.compatible_margins),
        "NCF": cf["NCF"],
        "CF": cf["CF"],
        "has_global_section": has_global_section(model),
        "arxiv_ab": ARXIV_AB,
        "arxiv_cf": ARXIV_CF,
        "lp_backend": "scipy.optimize.linprog" if HAS_SCIPY else "numpy_projected_ascent",
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
    # a⊕b = x y with x=0 for a1, x=1 for a2; y=0 for b1, y=1 for b2
    tables = {}
    xy = {("a1", "b1"): (0, 0), ("a1", "b2"): (0, 1),
          ("a2", "b1"): (1, 0), ("a2", "b2"): (1, 1)}
    for ctx in scenario.contexts:
        x, y = xy[tuple(ctx)]
        target = (x * y) % 2
        # P(a,b)=1/2 if a⊕b==target else 0
        probs = []
        for a, b in ((0, 0), (0, 1), (1, 0), (1, 1)):
            probs.append(0.5 if (a ^ b) == target else 0.0)
        tables[tuple(ctx)] = _table_from_flat(ctx, probs)
    return EmpiricalModel.from_tables(scenario, tables)


def chsh_table_i_model(scenario):
    """CHSH QM table from arXiv:1705.07918 Table I (angles 0, pi/3 on |Phi+>)."""
    # Left table in Table I of the CF paper
    raw = {
        ("a1", "b1"): (0.5, 0.0, 0.0, 0.5),
        ("a1", "b2"): (3 / 8, 1 / 8, 1 / 8, 3 / 8),
        ("a2", "b1"): (3 / 8, 1 / 8, 1 / 8, 3 / 8),
        ("a2", "b2"): (1 / 8, 3 / 8, 3 / 8, 1 / 8),
    }
    tables = {ctx: _table_from_flat(ctx, raw[ctx]) for ctx in scenario.contexts}
    return EmpiricalModel.from_tables(scenario, tables)


# ---- tests ----

def s01_margin_compatibility_222():
    scenario = bell_222_scenario()
    model = classical_factorizable_model(scenario)
    require(model.compatible_margins, "classical margins must agree")
    pr = pr_box_model(scenario)
    require(pr.compatible_margins, "PR-box is no-signalling")
    chsh = chsh_table_i_model(scenario)
    require(chsh.compatible_margins, "CHSH Table I is no-signalling")
    return {
        "scenario": "(2,2,2)",
        "classical_compatible": True,
        "pr_compatible": True,
        "chsh_table_i_compatible": True,
    }


def s02_classical_global_section():
    scenario = bell_222_scenario()
    model = classical_factorizable_model(scenario)
    rep = report(model)
    require(rep["has_global_section"], "classical must have global section")
    require(rep["CF"] <= 1e-7, f"classical CF~0, got {rep['CF']}")
    return {"CF": rep["CF"], "NCF": rep["NCF"], "has_global_section": True}


def s03_pr_box_cf_one():
    scenario = bell_222_scenario()
    model = pr_box_model(scenario)
    rep = report(model)
    require(abs(rep["CF"] - 1.0) <= 1e-6, f"PR-box CF=1, got {rep['CF']}")
    require(not rep["has_global_section"], "PR-box has no global section")
    return {"CF": rep["CF"], "NCF": rep["NCF"], "source": "arXiv:1705.07918 Table I (PR)"}


def s04_chsh_table_i_partial_cf():
    scenario = bell_222_scenario()
    model = chsh_table_i_model(scenario)
    rep = report(model)
    require(0.0 < rep["CF"] < 1.0, f"expected 0<CF<1, got {rep['CF']}")
    # Literature: CHSH S=5/2 => normalised violation (5/2-2)/(4-2)=1/4; CF equals max norm. violation
    require(abs(rep["CF"] - 0.25) <= 1e-5, f"Table I CF should be 1/4, got {rep['CF']}")
    return {
        "CF": rep["CF"],
        "NCF": rep["NCF"],
        "source": "arXiv:1705.07918 Table I CHSH (angles 0, pi/3 on |Phi+>)",
        "literature_CF": 0.25,
        "chsh_value": 2.5,
    }


def s05_vb1_deterministic_contradiction():
    """Three views x=y, y=z, z=x+1: no global assignment (VB1 smoke; separate from CF).

    Deterministic section check on the event sheaf (not a probabilistic empirical model).
    Incompatible deterministic pairwise constraints already yield an empty global section;
    margin-compatible CF is therefore not applicable — report empty assignment only.
    """
    X = ("x", "y", "z")
    outcomes = (0, 1, 2)
    # Allowed local sections (deterministic)
    allow_xy = {(a, b) for a in outcomes for b in outcomes if a == b}
    allow_yz = {(a, b) for a in outcomes for b in outcomes if a == b}
    allow_xz = {(a, b) for a in outcomes for b in outcomes if b == a + 1}  # z=x+1
    consistent = []
    for x, y, z in itertools.product(outcomes, repeat=3):
        if (x, y) in allow_xy and (y, z) in allow_yz and (x, z) in allow_xz:
            consistent.append({"x": x, "y": y, "z": z})
    require(len(consistent) == 0, "VB1 contradiction must have empty global assignments")
    # Also: even as 0-1 possibilistic supports, no global g with all restrictions allowed
    scenario = SheafScenario(X, (("x", "y"), ("y", "z"), ("x", "z")), outcomes)
    n_global = scenario.n_global
    require(n_global == 27, "3^3 globals")
    return {
        "global_assignments_consistent_with_support": 0,
        "n_global_checked": n_global,
        "has_global_section": False,
        "analogy": "context_transformations.md §2: x=y, y=z, z=x+1",
        "note": "VB1 unchanged for deterministic stocks; sheaf module is separate. CF-LP skipped because pairwise deterministic constraints are already jointly empty (not a no-signalling empirical model).",
    }


def s06_arxiv_links_documented():
    text = Path(__file__).read_text(encoding="utf-8")
    require("1102.0264" in text and "1705.07918" in text, "arxiv ids missing in script")
    require(ARXIV_AB.startswith("https://arxiv.org"), "AB link")
    require(ARXIV_CF.startswith("https://arxiv.org"), "CF link")
    return {"arxiv_ab": ARXIV_AB, "arxiv_cf": ARXIV_CF, "documented_in_script": True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).with_name("verify_sheaf_contextuality_results.json"),
    )
    args = parser.parse_args()
    require(HAS_SCIPY, "scipy.optimize.linprog required for CF LP (listed in requirements)")
    checks = [
        ("s01_margin_compatibility_222", s01_margin_compatibility_222),
        ("s02_classical_global_section", s02_classical_global_section),
        ("s03_pr_box_cf_one", s03_pr_box_cf_one),
        ("s04_chsh_table_i_partial_cf", s04_chsh_table_i_partial_cf),
        ("s05_vb1_deterministic_contradiction", s05_vb1_deterministic_contradiction),
        ("s06_arxiv_links_documented", s06_arxiv_links_documented),
    ]
    results = []
    for name, fn in checks:
        try:
            evidence = fn()
            results.append({"id": name, "status": "passed", "evidence": evidence})
        except Exception as exc:
            results.append({"id": name, "status": "failed", "error": f"{type(exc).__name__}: {exc}"})
    passed = sum(r["status"] == "passed" for r in results)
    failed = [r["id"] for r in results if r["status"] != "passed"]
    report_obj = {
        "module": "F08_sheaf_contextuality",
        "revision_package": "F08_F09_2026-09-16",
        "generated_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "python": platform.python_version(),
        "numpy": np.__version__,
        "scipy": __import__("scipy").__version__,
        "lp_backend": "scipy.optimize.linprog",
        "count": len(results),
        "passed": passed,
        "failed": len(failed),
        "arxiv": {"abramsky_brandenburger": ARXIV_AB, "contextual_fraction": ARXIV_CF},
        "vb1_policy": "unchanged; sheaf is separate optional module",
        "checks": results,
    }
    args.output.write_text(json.dumps(report_obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    summary = {"count": len(results), "passed": passed, "failed": failed, "report": str(args.output.resolve())}
    print(json.dumps(summary, ensure_ascii=False))
    raise SystemExit(0 if not failed else 1)


if __name__ == "__main__":
    main()
