#!/usr/bin/env python3
"""Hand-checkable verification for Formal Concept Analysis (Milestone 27).

Checks:
  1. Ticket 4×3 MembershipMatrix → exactly 6 concepts (derived, not hard-coded)
  2. is_concept True for ≥2 of those concepts
  3. Negative: A={e1,e2}, B={s1} → is_concept False
     (A↑={s1} but {s1}↓={e1,e2,e3} ≠ A)
  4. Attribute implication s3 ⇒ s1 as a readable JSON field
  5. Scope: Ganter & Wille DOI; NextClosure documented as unused; no metarules

JSON {count, passed, failed, report}; numbers from this run.
Does not mutate membership.core.
"""
from __future__ import annotations

import argparse
import datetime as dt
import inspect
import json
import platform
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from scoped_correspondence.membership.core import MembershipMatrix  # noqa: E402
from scoped_correspondence.membership import formal_concept_analysis as fca  # noqa: E402
from scoped_correspondence.membership.formal_concept_analysis import (  # noqa: E402
    DOI,
    SOURCE,
    all_concepts,
    attribute_implication_from_extents,
    derive_down,
    derive_up,
    is_concept,
)


def require(ok, msg):
    if not bool(ok):
        raise AssertionError(msg)


def _labels(indices, prefix: str):
    return [f"{prefix}{i + 1}" for i in sorted(indices)]


def example_matrix() -> MembershipMatrix:
    """Ticket 4×3 formal context (entities × systems)."""
    return MembershipMatrix(
        [
            [1, 1, 0],  # e1: s1,s2
            [1, 0, 1],  # e2: s1,s3
            [1, 1, 1],  # e3: s1,s2,s3
            [0, 1, 0],  # e4: s2
        ],
        entity_names=("e1", "e2", "e3", "e4"),
        system_names=("s1", "s2", "s3"),
    )


def expected_concepts_labeled():
    return [
        ({"e1", "e2", "e3", "e4"}, set()),
        ({"e1", "e2", "e3"}, {"s1"}),
        ({"e1", "e3", "e4"}, {"s2"}),
        ({"e1", "e3"}, {"s1", "s2"}),
        ({"e2", "e3"}, {"s1", "s3"}),
        ({"e3"}, {"s1", "s2", "s3"}),
    ]


def concept_to_labels(A, B):
    return (set(_labels(A, "e")), set(_labels(B, "s")))


def check_six_concepts():
    M = example_matrix()
    concepts = all_concepts(M)
    require(len(concepts) == 6, f"expected 6 concepts, got {len(concepts)}")

    labeled = [concept_to_labels(A, B) for A, B in concepts]
    expected = expected_concepts_labeled()
    require(
        labeled == expected,
        f"concept list mismatch:\n got {labeled}\n want {expected}",
    )

    sizes = [len(A) for A, _ in concepts]
    require(sizes == sorted(sizes, reverse=True), f"not ordered by |A| desc: {sizes}")

    for A, B in concepts:
        require(is_concept(A, B, M), f"not a concept: {sorted(A)}, {sorted(B)}")

    return {
        "n_concepts": len(concepts),
        "concepts": [
            {
                "extent_indices": sorted(A),
                "intent_indices": sorted(B),
                "extent_labels": _labels(A, "e"),
                "intent_labels": _labels(B, "s"),
                "extent_size": len(A),
            }
            for A, B in concepts
        ],
        "ordered_by_extent_size_desc": True,
        "matrix": M.matrix.tolist(),
    }


def check_is_concept_positives():
    M = example_matrix()
    concepts = all_concepts(M)
    targets = [
        (frozenset({0, 1, 2}), frozenset({0})),       # ({e1,e2,e3},{s1})
        (frozenset({1, 2}), frozenset({0, 2})),       # ({e2,e3},{s1,s3})
    ]
    results = []
    for A, B in targets:
        ok = is_concept(A, B, M)
        require(ok, f"expected concept {sorted(A)},{sorted(B)}")
        require(any(a == A and b == B for a, b in concepts), "target missing from all_concepts")
        results.append(
            {
                "extent_labels": _labels(A, "e"),
                "intent_labels": _labels(B, "s"),
                "is_concept": ok,
            }
        )
    return {"checked": results, "n_checked": len(results)}


def check_negative_not_concept():
    M = example_matrix()
    A = frozenset({0, 1})  # {e1,e2}
    B = frozenset({0})     # {s1}
    up = derive_up(A, M)
    down = derive_down(B, M)
    ok = is_concept(A, B, M)
    require(ok is False, "negative pair must not be a concept")
    require(up == frozenset({0}), f"A↑ expected {{0}}, got {up}")
    require(down == frozenset({0, 1, 2}), f"{{s1}}↓ expected {{0,1,2}}, got {down}")
    require(down != A, "extent mismatch is the reason")
    return {
        "A_labels": _labels(A, "e"),
        "B_labels": _labels(B, "s"),
        "derive_up_A": _labels(up, "s"),
        "derive_down_B": _labels(down, "e"),
        "is_concept": ok,
        "reason": "A↑={s1} but {s1}↓={e1,e2,e3} ≠ A={e1,e2}",
    }


def check_implication_s3_implies_s1():
    M = example_matrix()
    concepts = all_concepts(M)
    target_A, target_B = frozenset({1, 2}), frozenset({0, 2})
    require(
        any(a == target_A and b == target_B for a, b in concepts),
        "missing concept ({e2,e3},{s1,s3})",
    )
    # s3 index=2, s1 index=0
    report = attribute_implication_from_extents(2, 0, M)
    require(report["holds"] is True, "s3 should imply s1")
    require("s3" in report["statement"] and "s1" in report["statement"], report["statement"])
    return {
        "from_concept": {
            "extent_labels": ["e2", "e3"],
            "intent_labels": ["s1", "s3"],
        },
        "implication": report,
        "readable_field": report["statement"],
    }


def check_scope():
    src = inspect.getsource(fca)
    doc = inspect.getdoc(fca) or ""
    blob = src + "\n" + doc
    require("10.1007/978-3-642-59830-2" in DOI, f"bad DOI constant: {DOI}")
    require("Ganter" in SOURCE and "Wille" in SOURCE, SOURCE)
    require("NextClosure" in blob, "must mention NextClosure")
    require(
        "not" in blob.lower() and "NextClosure" in blob,
        "must state NextClosure is not used / out of scope",
    )
    require("from scoped_correspondence.metarules" not in src, "no metarules import")
    require("import scoped_correspondence.metarules" not in src, "no metarules import")
    require(
        "brute" in blob.lower() or "power" in blob.lower(),
        "must document brute-force / power-set approach",
    )
    require("MembershipMatrix" in src, "must use MembershipMatrix")
    return {
        "doi": DOI,
        "source": SOURCE,
        "mentions_nextclosure_out_of_scope": "NextClosure" in blob,
        "imports_metarules": False,
        "uses_membership_matrix": True,
    }


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)

    checks = [
        ("six_concepts_from_matrix", check_six_concepts),
        ("is_concept_positives", check_is_concept_positives),
        ("negative_not_concept", check_negative_not_concept),
        ("implication_s3_implies_s1", check_implication_s3_implies_s1),
        ("scope_ganter_wille", check_scope),
    ]

    report = {}
    passed = 0
    failed = 0
    errors = []
    for name, fn in checks:
        try:
            report[name] = fn()
            passed += 1
            print(f"PASS {name}")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            errors.append({"check": name, "error": f"{type(exc).__name__}: {exc}"})
            report[name] = {"error": f"{type(exc).__name__}: {exc}"}
            print(f"FAIL {name}: {exc}")

    out = {
        "count": len(checks),
        "passed": passed,
        "failed": failed,
        "errors": errors,
        "report": report,
        "meta": {
            "milestone": 27,
            "module": "membership.formal_concept_analysis",
            "doi": DOI,
            "source": SOURCE,
            "python": platform.python_version(),
            "platform": platform.platform(),
            "timestamp_local": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
            "forbidden_untouched": [
                "membership/core.py",
                "scoped_correspondence/__init__.py",
                "FORMALISM.md",
                "context_transformations.md",
            ],
        },
    }

    # Readable top-level implication field (ticket requirement)
    if "implication_s3_implies_s1" in report and "implication" in report.get(
        "implication_s3_implies_s1", {}
    ):
        out["implication"] = report["implication_s3_implies_s1"]["implication"]

    json_path = args.json_out or (
        ROOT / "verification" / "verify_formal_concept_analysis_results.json"
    )
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"JSON → {json_path}")
    print(f"RESULT {passed}/{len(checks)} passed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
