#!/usr/bin/env python3
"""Hand-checkable verification for Chemical Organization Theory / COT (Milestone 41).

Checks (all numbers from this script run):
  1. WITHOUT r4: {a,b} reaction-closed, NOT self-maintaining (hand -v3>=0);
     only organization is empty set
  2. WITH r4: {a,b} is organization; witness v=(2,1,1,1); (Sv)_a=(Sv)_b=0
  3. Negative: {b} alone not self-maintaining (with and without r4)
  4. AUTOPOIESIS_SCOPE_WARNING verbatim in module/API/docs/JSON
  5. Regex/AST scan: no function/class/attribute identifier contains
     'closure' or 'closed' except mandated is_reaction_closed
  6. Sources DOIs present

Requires numpy+scipy. JSON {count, passed, failed, report}; numbers from this run.
No imports from closure/, membership/, or other Bausteine.
"""
from __future__ import annotations

import argparse
import ast
import datetime as dt
import inspect
import json
import platform
import re
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from scoped_correspondence.chemical_organization import (  # noqa: E402
    AUTOPOIESIS_SCOPE_WARNING,
    SOURCE,
    as_report,
    is_organization,
    is_reaction_closed,
    is_self_maintaining,
    maintenance_flux,
)
from scoped_correspondence.chemical_organization import core as cot_core  # noqa: E402

# ---------------------------------------------------------------------------
# Example network
# ---------------------------------------------------------------------------
# species_order = [a, b]
# r1: a→b, r2: b→a, r3: b→∅, r4: ∅→a

R1 = (frozenset({"a"}), frozenset({"b"}))
R2 = (frozenset({"b"}), frozenset({"a"}))
R3 = (frozenset({"b"}), frozenset())
R4 = (frozenset(), frozenset({"a"}))

REACTIONS_NO_R4 = [R1, R2, R3]
REACTIONS_WITH_R4 = [R1, R2, R3, R4]

SPECIES_ORDER = ["a", "b"]
S_NO_R4 = np.array(
    [
        [-1.0, 1.0, 0.0],
        [1.0, -1.0, -1.0],
    ]
)
S_WITH_R4 = np.array(
    [
        [-1.0, 1.0, 0.0, 1.0],
        [1.0, -1.0, -1.0, 0.0],
    ]
)

WITNESS_V = np.array([2.0, 1.0, 1.0, 1.0])

ALLOWED_CLOSED_NAMES = frozenset({"is_reaction_closed"})
FORBIDDEN_SUBSTR = ("closure", "closed")


def require(ok, msg):
    if not bool(ok):
        raise AssertionError(msg)


def near(a, b, atol=1e-9, rtol=1e-9):
    if not np.isclose(float(a), float(b), atol=atol, rtol=rtol):
        raise AssertionError(f"{a!r} != {b!r} (atol={atol}, rtol={rtol})")


def check_without_r4():
    """{a,b} closed but not self-maintaining; only org is ∅."""
    A = {"a", "b"}
    require(
        is_reaction_closed(A, REACTIONS_NO_R4) is True,
        "{a,b} must be reaction-closed without r4",
    )
    require(
        is_self_maintaining(A, REACTIONS_NO_R4, S_NO_R4, species_order=SPECIES_ORDER)
        is False,
        "{a,b} must NOT be self-maintaining without r4",
    )
    require(
        is_organization(A, REACTIONS_NO_R4, S_NO_R4, species_order=SPECIES_ORDER)
        is False,
        "{a,b} must not be an organization without r4",
    )

    # Hand proof: v1,v2,v3 >= 1 applicable; (Sv)_a + (Sv)_b = -v3 >= 0 ⇒ v3 <= 0
    # contradicts v3 >= 1.
    hand_sum_row = S_NO_R4.sum(axis=0)  # [-0, 0, -1] → only -v3
    require(list(hand_sum_row) == [0.0, 0.0, -1.0], f"unexpected sum row {hand_sum_row}")
    hand_contradiction = "sum_s (Sv)_s = -v3 >= 0 with v3>=1 impossible"

    empty = set()
    require(is_reaction_closed(empty, REACTIONS_NO_R4) is True, "∅ closed without r4")
    require(
        is_self_maintaining(
            empty, REACTIONS_NO_R4, S_NO_R4, species_order=SPECIES_ORDER
        )
        is True,
        "∅ self-maintaining without r4 (vacuous)",
    )
    require(
        is_organization(empty, REACTIONS_NO_R4, S_NO_R4, species_order=SPECIES_ORDER)
        is True,
        "∅ is organization without r4",
    )

    # Enumerate all subsets: only ∅ is organization
    orgs = []
    for mask in range(4):
        cand = set()
        if mask & 1:
            cand.add("a")
        if mask & 2:
            cand.add("b")
        if is_organization(
            cand, REACTIONS_NO_R4, S_NO_R4, species_order=SPECIES_ORDER
        ):
            orgs.append(frozenset(cand))
    require(orgs == [frozenset()], f"only ∅ should be org without r4; got {orgs}")

    return {
        "A_ab_reaction_closed": True,
        "A_ab_self_maintaining": False,
        "A_ab_organization": False,
        "hand_contradiction": hand_contradiction,
        "hand_sum_Sv_equals_minus_v3": True,
        "empty_is_organization": True,
        "organizations": [sorted(o) for o in orgs],
        "n_reactions": 3,
    }


def check_with_r4():
    """{a,b} is organization; witness v=(2,1,1,1); Sv=0."""
    A = {"a", "b"}
    require(is_reaction_closed(A, REACTIONS_WITH_R4) is True, "{a,b} closed with r4")
    require(
        is_self_maintaining(
            A, REACTIONS_WITH_R4, S_WITH_R4, species_order=SPECIES_ORDER
        )
        is True,
        "{a,b} self-maintaining with r4",
    )
    require(
        is_organization(A, REACTIONS_WITH_R4, S_WITH_R4, species_order=SPECIES_ORDER)
        is True,
        "{a,b} organization with r4",
    )

    # Hand witness
    Sv_hand = S_WITH_R4 @ WITNESS_V
    near(Sv_hand[0], 0.0)
    near(Sv_hand[1], 0.0)
    require(
        list(WITNESS_V) == [2.0, 1.0, 1.0, 1.0],
        "documented witness must be (2,1,1,1)",
    )

    flux = maintenance_flux(
        A, REACTIONS_WITH_R4, S_WITH_R4, species_order=SPECIES_ORDER
    )
    require(flux is not None, "maintenance_flux must return a vector")
    require(np.all(flux >= -1e-12), "flux must be nonnegative")
    # Applicable all four ⇒ each >= 1
    require(np.all(flux >= 1.0 - 1e-9), f"all applicable fluxes >= 1; got {flux}")
    Sv = S_WITH_R4 @ flux
    require(np.all(Sv >= -1e-7), f"Sv on all species must be >= 0; got {Sv}")
    near(Sv[0], 0.0, atol=1e-6)
    near(Sv[1], 0.0, atol=1e-6)

    # Empty set not reaction-closed with inflow r4
    require(
        is_reaction_closed(set(), REACTIONS_WITH_R4) is False,
        "∅ not reaction-closed when r4 present",
    )
    require(
        is_organization(set(), REACTIONS_WITH_R4, S_WITH_R4, species_order=SPECIES_ORDER)
        is False,
        "∅ not organization with r4",
    )

    rep = as_report(A, REACTIONS_WITH_R4, S_WITH_R4, species_order=SPECIES_ORDER)
    require(rep["is_organization"] is True, "as_report organization")
    require(rep["maintenance_flux"] is not None, "as_report flux")

    return {
        "A_ab_reaction_closed": True,
        "A_ab_self_maintaining": True,
        "A_ab_organization": True,
        "witness_v": [2.0, 1.0, 1.0, 1.0],
        "Sv_hand_a": float(Sv_hand[0]),
        "Sv_hand_b": float(Sv_hand[1]),
        "linprog_flux": [float(x) for x in flux],
        "linprog_Sv_a": float(Sv[0]),
        "linprog_Sv_b": float(Sv[1]),
        "empty_reaction_closed": False,
        "empty_organization": False,
        "n_reactions": 4,
    }


def check_negative_b_alone():
    """{b} alone is not self-maintaining."""
    B = {"b"}
    # Without r4: applicable r2, r3 → (Sv)_b = -v2 - v3 < 0
    sm_no = is_self_maintaining(
        B, REACTIONS_NO_R4, S_NO_R4, species_order=SPECIES_ORDER
    )
    require(sm_no is False, "{b} must not be self-maintaining without r4")
    # With r4: applicable r2, r3, r4 (∅⊆{b}); (Sv)_b = -v2 - v3 still < 0
    sm_yes = is_self_maintaining(
        B, REACTIONS_WITH_R4, S_WITH_R4, species_order=SPECIES_ORDER
    )
    require(sm_yes is False, "{b} must not be self-maintaining with r4")
    # Also not reaction-closed (r2 produces a)
    require(is_reaction_closed(B, REACTIONS_NO_R4) is False, "{b} not closed (r2)")
    require(is_reaction_closed(B, REACTIONS_WITH_R4) is False, "{b} not closed (r2/r4)")
    return {
        "B_self_maintaining_without_r4": False,
        "B_self_maintaining_with_r4": False,
        "B_reaction_closed_without_r4": False,
        "B_reaction_closed_with_r4": False,
    }


def check_warning_verbatim():
    """AUTOPOIESIS_SCOPE_WARNING present verbatim in constants, docs, docstrings."""
    warn = AUTOPOIESIS_SCOPE_WARNING
    expected = (
        "This Baustein does NOT fully formalize Autopoiesis; name "
        "chemical_organization not autopoiesis. Reaction closure, formal-concept "
        "closure, and Markovian closure have different semantics. This does not "
        "rule out structural relations between selected constructions (see "
        "docs/structural_relations.md, bridge B1). Such relations must specify "
        "the objects, maps, preserved properties, and limitations; they do not "
        "imply shared physical meaning or require shared implementation "
        "inheritance."
    )
    require(warn == expected, "AUTOPOIESIS_SCOPE_WARNING must match verbatim")

    mod_doc = cot_core.__doc__ or ""
    require(warn in mod_doc, "module docstring must contain warning verbatim")

    for fn in (
        is_reaction_closed,
        is_self_maintaining,
        is_organization,
        maintenance_flux,
    ):
        doc = inspect.getdoc(fn) or ""
        require(
            "does NOT fully formalize Autopoiesis" in doc
            or warn in doc,
            f"{fn.__name__} docstring must carry Autopoiesis scope warning",
        )

    docs_path = ROOT / "docs" / "chemical_organization_core.md"
    require(docs_path.is_file(), "docs/chemical_organization_core.md must exist")
    docs_text = docs_path.read_text(encoding="utf-8")
    require(warn in docs_text, "docs must contain AUTOPOIESIS_SCOPE_WARNING verbatim")
    require("chemical_organization not autopoiesis" in docs_text, "docs naming fence")
    require(
        "formal-concept closure" in docs_text and "structural_relations.md" in docs_text,
        "docs must reference the reworded structural-relations bridge note",
    )

    require("10.1007/s11538-006-9130-8" in SOURCE, "Dittrich DOI")
    require("10.1007/BF02458289" in SOURCE, "Fontana DOI")
    require("Dittrich" in SOURCE and "Fontana" in SOURCE, "SOURCE authors")

    rep = as_report({"a", "b"}, REACTIONS_WITH_R4, S_WITH_R4, species_order=SPECIES_ORDER)
    require(rep["autopoiesis_scope_warning"] == warn, "as_report embeds warning")
    require(rep["source"] == SOURCE, "as_report embeds SOURCE")

    return {
        "autopoiesis_scope_warning": warn,
        "module_doc_has_warning": warn in mod_doc,
        "docs_has_warning": warn in docs_text,
        "source": SOURCE,
        "as_report_has_warning": rep["autopoiesis_scope_warning"] == warn,
    }


def _collect_identifiers(tree: ast.AST) -> list[str]:
    names: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.append(node.name)
            for arg in node.args.args + node.args.kwonlyargs:
                names.append(arg.arg)
            if node.args.vararg:
                names.append(node.args.vararg.arg)
            if node.args.kwarg:
                names.append(node.args.kwarg.arg)
        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            names.append(node.id)
        elif isinstance(node, ast.Attribute) and isinstance(node.ctx, ast.Store):
            names.append(node.attr)
        elif isinstance(node, ast.alias):
            names.append(node.asname or node.name.split(".")[-1])
        elif isinstance(node, ast.arg):
            names.append(node.arg)
    return names


def check_forbidden_identifier_names():
    """Regex/AST scan of new source files for forbidden identifier substrings."""
    pkg = ROOT / "src" / "scoped_correspondence" / "chemical_organization"
    files = sorted(pkg.glob("*.py"))
    require(len(files) >= 2, "expected __init__.py and core.py")

    offenders: list[dict] = []
    scanned: list[str] = []
    # Also regex-scan raw text for def/class lines as belt-and-suspenders
    def_class_re = re.compile(
        r"^\s*(?:async\s+)?(?:def|class)\s+([A-Za-z_][A-Za-z0-9_]*)",
        re.MULTILINE,
    )
    # Annotated / plain assignments at module level: NAME = or NAME:
    assign_re = re.compile(
        r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*(?::[^=\n]+)?=",
        re.MULTILINE,
    )

    for path in files:
        text = path.read_text(encoding="utf-8")
        scanned.append(str(path.relative_to(ROOT)))
        tree = ast.parse(text, filename=str(path))
        idents = set(_collect_identifiers(tree))
        idents.update(def_class_re.findall(text))
        idents.update(assign_re.findall(text))
        for name in sorted(idents):
            lower = name.lower()
            hit = None
            for sub in FORBIDDEN_SUBSTR:
                if sub in lower:
                    hit = sub
                    break
            if hit is None:
                continue
            if name in ALLOWED_CLOSED_NAMES:
                continue
            offenders.append(
                {"file": str(path.relative_to(ROOT)), "name": name, "substr": hit}
            )

    require(
        not offenders,
        f"forbidden identifier names found: {offenders}",
    )
    # Positive: mandated API present
    core_text = (pkg / "core.py").read_text(encoding="utf-8")
    require(
        re.search(r"\bdef is_reaction_closed\b", core_text),
        "is_reaction_closed must be defined",
    )
    require(
        re.search(r"\bdef is_self_maintaining\b", core_text),
        "is_self_maintaining must be defined",
    )
    require(
        re.search(r"\bdef is_organization\b", core_text),
        "is_organization must be defined",
    )
    # No 'closure' as identifier substring at all
    require(
        all(o["substr"] != "closure" for o in offenders) or not offenders,
        "no identifier may contain 'closure'",
    )

    return {
        "scanned_files": scanned,
        "allowed_exception": sorted(ALLOWED_CLOSED_NAMES),
        "forbidden_substrings": list(FORBIDDEN_SUBSTR),
        "offenders": offenders,
        "scan_clean": len(offenders) == 0,
        "mandated_api_present": True,
    }


CHECKS = [
    ("without_r4", check_without_r4),
    ("with_r4", check_with_r4),
    ("negative_b_alone", check_negative_b_alone),
    ("warning_verbatim", check_warning_verbatim),
    ("forbidden_identifier_names", check_forbidden_identifier_names),
]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--json-out",
        type=Path,
        default=ROOT / "verification" / "verify_chemical_organization_core_results.json",
    )
    args = parser.parse_args(argv)

    report = {
        "milestone": "M41",
        "baustein": "chemical_organization",
        "timestamp": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "platform": platform.platform(),
        "python": sys.version.split()[0],
        "numpy": np.__version__,
        "checks": {},
        "autopoiesis_scope_warning": AUTOPOIESIS_SCOPE_WARNING,
        "source": SOURCE,
    }
    passed = 0
    failed = 0
    errors = []
    for name, fn in CHECKS:
        try:
            report["checks"][name] = fn()
            report["checks"][name]["_status"] = "passed"
            passed += 1
        except Exception as exc:  # noqa: BLE001 — collect all check failures
            failed += 1
            report["checks"][name] = {"_status": "failed", "error": repr(exc)}
            errors.append(f"{name}: {exc!r}")

    out = {
        "count": len(CHECKS),
        "passed": passed,
        "failed": failed,
        "errors": errors,
        "report": report,
    }
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"count": out["count"], "passed": out["passed"], "failed": out["failed"]}, indent=2))
    if failed:
        print("FAILURES:", *errors, sep="\n  ")
        sys.exit(1)
    print(f"OK {passed}/{len(CHECKS)} → {args.json_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
