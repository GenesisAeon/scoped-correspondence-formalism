#!/usr/bin/env python3
"""Equivalence checks for Contextuality core (Milestone 7 / F08+F13).

Matches legacy verify_sheaf_contextuality_results.json s01–s06 EXACTLY, plus
ScopeViolationError tests for assumes_independent_contexts False/missing.
Does NOT edit verify_sheaf_contextuality.py.
"""
from __future__ import annotations

import argparse
import datetime as dt
import inspect
import itertools
import json
import platform
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from scoped_correspondence.contextuality import (  # noqa: E402
    ARXIV_AB,
    ARXIV_CF,
    EmpiricalModel,
    F13_SCOPE_RISK,
    SheafScenario,
    bell_222_scenario,
    chsh_table_i_model,
    classical_factorizable_model,
    contextual_fraction,
    has_global_section,
    pr_box_model,
    report,
)
from scoped_correspondence.errors import ScopeViolationError  # noqa: E402


def require(ok, msg):
    if not bool(ok):
        raise AssertionError(msg)


def near(a, b, atol=1e-10, rtol=1e-9):
    if not np.allclose(a, b, atol=atol, rtol=rtol):
        raise AssertionError(f"{a!r} != {b!r}")


def load_legacy():
    path = ROOT / "verification" / "verify_sheaf_contextuality_results.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    by_id = {c["id"]: c for c in data["checks"]}
    return data, by_id


def evidence(legacy_id: str):
    _, by_id = load_legacy()
    require(legacy_id in by_id, f"missing legacy {legacy_id}")
    require(by_id[legacy_id]["status"] == "passed", f"legacy {legacy_id} not passed")
    return by_id[legacy_id]["evidence"]


def s01_margin_compatibility_222():
    expected = evidence("s01_margin_compatibility_222")
    scenario = bell_222_scenario()
    classical = classical_factorizable_model(scenario)
    pr = pr_box_model(scenario)
    chsh = chsh_table_i_model(scenario)
    require(classical.compatible_margins, "classical margins")
    require(pr.compatible_margins, "PR margins")
    require(chsh.compatible_margins, "CHSH margins")
    out = {
        "scenario": "(2,2,2)",
        "classical_compatible": True,
        "pr_compatible": True,
        "chsh_table_i_compatible": True,
    }
    require(out == expected, f"s01 mismatch: {out} != {expected}")
    return out


def s02_classical_global_section():
    expected = evidence("s02_classical_global_section")
    scenario = bell_222_scenario()
    model = classical_factorizable_model(scenario)
    rep = report(model, assumes_independent_contexts=True)
    require(rep["has_global_section"], "classical global section")
    require(rep["CF"] <= 1e-7, f"classical CF~0, got {rep['CF']}")
    out = {"CF": rep["CF"], "NCF": rep["NCF"], "has_global_section": True}
    near(out["CF"], expected["CF"])
    near(out["NCF"], expected["NCF"])
    require(out["has_global_section"] is expected["has_global_section"], "has_global")
    # Exact JSON numbers
    require(out["CF"] == expected["CF"], f"CF exact {out['CF']} vs {expected['CF']}")
    require(out["NCF"] == expected["NCF"], f"NCF exact {out['NCF']} vs {expected['NCF']}")
    return out


def s03_pr_box_cf_one():
    expected = evidence("s03_pr_box_cf_one")
    scenario = bell_222_scenario()
    model = pr_box_model(scenario)
    rep = report(model, assumes_independent_contexts=True)
    require(abs(rep["CF"] - 1.0) <= 1e-6, f"PR CF=1, got {rep['CF']}")
    require(not rep["has_global_section"], "PR no global section")
    out = {
        "CF": rep["CF"],
        "NCF": rep["NCF"],
        "source": "arXiv:1705.07918 Table I (PR)",
    }
    require(out["CF"] == expected["CF"], "CF exact")
    require(out["NCF"] == expected["NCF"], "NCF exact")
    require(out["source"] == expected["source"], "source text")
    return out


def s04_chsh_table_i_partial_cf():
    expected = evidence("s04_chsh_table_i_partial_cf")
    scenario = bell_222_scenario()
    model = chsh_table_i_model(scenario)
    rep = report(model, assumes_independent_contexts=True)
    require(0.0 < rep["CF"] < 1.0, f"0<CF<1, got {rep['CF']}")
    require(abs(rep["CF"] - 0.25) <= 1e-5, f"CF=1/4, got {rep['CF']}")
    out = {
        "CF": rep["CF"],
        "NCF": rep["NCF"],
        "source": "arXiv:1705.07918 Table I CHSH (angles 0, pi/3 on |Phi+>)",
        "literature_CF": 0.25,
        "chsh_value": 2.5,
    }
    require(out["CF"] == expected["CF"], "CF exact")
    require(out["NCF"] == expected["NCF"], "NCF exact")
    require(out["literature_CF"] == expected["literature_CF"], "lit CF")
    require(out["chsh_value"] == expected["chsh_value"], "chsh value")
    require(out["source"] == expected["source"], "source")
    return out


def s05_vb1_deterministic_contradiction():
    expected = evidence("s05_vb1_deterministic_contradiction")
    X = ("x", "y", "z")
    outcomes = (0, 1, 2)
    allow_xy = {(a, b) for a in outcomes for b in outcomes if a == b}
    allow_yz = {(a, b) for a in outcomes for b in outcomes if a == b}
    allow_xz = {(a, b) for a in outcomes for b in outcomes if b == a + 1}
    consistent = []
    for x, y, z in itertools.product(outcomes, repeat=3):
        if (x, y) in allow_xy and (y, z) in allow_yz and (x, z) in allow_xz:
            consistent.append({"x": x, "y": y, "z": z})
    require(len(consistent) == 0, "VB1 empty")
    scenario = SheafScenario(X, (("x", "y"), ("y", "z"), ("x", "z")), outcomes)
    require(scenario.n_global == 27, "3^3")
    out = {
        "global_assignments_consistent_with_support": 0,
        "n_global_checked": scenario.n_global,
        "has_global_section": False,
        "analogy": "context_transformations.md §2: x=y, y=z, z=x+1",
        "note": (
            "VB1 unchanged for deterministic stocks; sheaf module is separate. "
            "CF-LP skipped because pairwise deterministic constraints are already "
            "jointly empty (not a no-signalling empirical model)."
        ),
    }
    require(out == expected, f"s05 mismatch:\n{out}\n!=\n{expected}")
    return out


def s06_arxiv_links_documented():
    expected = evidence("s06_arxiv_links_documented")
    core_path = (
        ROOT / "src" / "scoped_correspondence" / "contextuality" / "core.py"
    )
    text = core_path.read_text(encoding="utf-8")
    require("1102.0264" in text and "1705.07918" in text, "arxiv ids in core")
    require(ARXIV_AB.startswith("https://arxiv.org"), "AB link")
    require(ARXIV_CF.startswith("https://arxiv.org"), "CF link")
    out = {
        "arxiv_ab": ARXIV_AB,
        "arxiv_cf": ARXIV_CF,
        "documented_in_script": True,
    }
    require(out == expected, f"s06 mismatch: {out} != {expected}")
    return out


def s07_f13_scope_guard():
    """ScopeViolationError when assumes_independent_contexts is False or missing."""
    scenario = bell_222_scenario()
    model = classical_factorizable_model(scenario)
    # False
    raised_false = False
    try:
        contextual_fraction(model, assumes_independent_contexts=False)
    except ScopeViolationError as exc:
        raised_false = True
        require("y_α=π_α(z,c,t)" in str(exc) or "y_α=π_α" in str(exc), "F13 risk text")
        require("modeling error" in str(exc) or "modelling error" in str(exc)
                or "modeling error" in F13_SCOPE_RISK, "modeling error phrase")
        require(str(exc) == F13_SCOPE_RISK or F13_SCOPE_RISK in str(exc)
                or "joint distribution always exists trivially" in str(exc),
                "trivial joint phrase")
    require(raised_false, "False must raise ScopeViolationError")
    raised_false_hgs = False
    try:
        has_global_section(model, assumes_independent_contexts=False)
    except ScopeViolationError:
        raised_false_hgs = True
    require(raised_false_hgs, "has_global_section False must raise")

    # Missing (default / omit)
    raised_missing = False
    try:
        contextual_fraction(model)
    except ScopeViolationError:
        raised_missing = True
    require(raised_missing, "missing assumes_independent_contexts must raise")
    raised_missing_hgs = False
    try:
        has_global_section(model)
    except ScopeViolationError:
        raised_missing_hgs = True
    require(raised_missing_hgs, "has_global_section missing must raise")

    # True works
    cf = contextual_fraction(model, assumes_independent_contexts=True)
    require(cf["CF"] == 0.0, "True path still CF=0")

    # Signature: no silent True default
    sig = inspect.signature(contextual_fraction)
    param = sig.parameters["assumes_independent_contexts"]
    require(
        param.default is None or param.default is inspect.Parameter.empty
        or param.default is not True,
        "must not default to True",
    )
    return {
        "false_raises_ScopeViolationError": True,
        "missing_raises_ScopeViolationError": True,
        "true_allows_CF": True,
        "risk_text_contains_y_alpha": "y_α=π_α(z,c,t)" in F13_SCOPE_RISK,
        "risk_text_contains_trivial_joint": "joint distribution always exists trivially"
        in F13_SCOPE_RISK,
        "mapping": "sheaf_contextuality.md §6 / F13",
    }


CHECKS = [
    ("s01_margin_compatibility_222", s01_margin_compatibility_222),
    ("s02_classical_global_section", s02_classical_global_section),
    ("s03_pr_box_cf_one", s03_pr_box_cf_one),
    ("s04_chsh_table_i_partial_cf", s04_chsh_table_i_partial_cf),
    ("s05_vb1_deterministic_contradiction", s05_vb1_deterministic_contradiction),
    ("s06_arxiv_links_documented", s06_arxiv_links_documented),
    ("s07_f13_scope_guard", s07_f13_scope_guard),
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).with_name("verify_contextuality_core_results.json"),
    )
    args = parser.parse_args()
    results = []
    for name, fn in CHECKS:
        try:
            ev = fn()
            results.append({"id": name, "status": "passed", "evidence": ev})
        except Exception as exc:
            results.append(
                {"id": name, "status": "failed", "error": f"{type(exc).__name__}: {exc}"}
            )
    passed = sum(r["status"] == "passed" for r in results)
    failed = [r["id"] for r in results if r["status"] != "passed"]
    report_obj = {
        "milestone": "M7_contextuality_core",
        "kind": "Legacy equivalence s01–s06 + F13 ScopeViolationError guard",
        "generated_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "python": platform.python_version(),
        "numpy": np.__version__,
        "scipy": __import__("scipy").__version__,
        "count": len(results),
        "passed": passed,
        "failed": len(failed),
        "legacy_results": "verification/verify_sheaf_contextuality_results.json",
        "arxiv": {"abramsky_brandenburger": ARXIV_AB, "contextual_fraction": ARXIV_CF},
        "checks": results,
    }
    args.output.write_text(
        json.dumps(report_obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    summary = {
        "count": report_obj["count"],
        "passed": report_obj["passed"],
        "failed": failed,
        "report": str(args.output.resolve()),
    }
    print(json.dumps(summary, ensure_ascii=False))
    raise SystemExit(0 if not failed else 1)


if __name__ == "__main__":
    main()
