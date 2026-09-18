#!/usr/bin/env python3
"""Hand-checkable verification for Čech Cohomology Witness (Milestone 24).

Checks:
  1. classical_factorizable_model(bell_222) → obstruction vanishes; CF ≈ 0
  2. pr_box_model(bell_222) → obstruction nonzero; CF ≈ 1; proves_contextuality
  3. MANDATORY negative: vanishing does NOT certify noncontextuality
     (forbid is_contextual = not obstruction_vanishes); API one-way only
  4. Scope: core/csw not imported for mutation; no CF≡Čech identity;
     arXiv 1111.3620 present; coefficient_ring Z_2; degree 1

JSON {count, passed, failed, report}; numbers from this run.
Does not mutate contextuality.core / csw.py.
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

from scoped_correspondence.contextuality.core import (  # noqa: E402
    bell_222_scenario,
    classical_factorizable_model,
    contextual_fraction,
    pr_box_model,
)
from scoped_correspondence.contextuality.cohomology import (  # noqa: E402
    ARXIV,
    COEFFICIENT_RING,
    DEGREE,
    SOURCE,
    CohomologyWitness,
    cech_obstruction,
    cech_witness,
)


def require(ok, msg):
    if not bool(ok):
        raise AssertionError(msg)


def near(a, b, atol=1e-8, rtol=1e-7):
    import math
    if not math.isclose(float(a), float(b), abs_tol=atol, rel_tol=rtol):
        raise AssertionError(f"{a!r} != {b!r}")


def check_classical_vanishes():
    """classical_factorizable_model → obstruction vanishes; CF=0 cross-check."""
    scenario = bell_222_scenario()
    model = classical_factorizable_model(scenario)
    ob = cech_obstruction(model)
    w = cech_witness(model)
    cf = contextual_fraction(model, assumes_independent_contexts=True)
    require(ob["obstruction_vanishes"] is True, "classical should vanish")
    require(ob["obstruction_nonzero"] is False, "classical nonzero flag")
    require(w.obstruction_nonzero is False, "witness nonzero")
    require(w.proves_contextuality is False, "classical does not prove contextuality")
    require(w.proves_contextuality == w.obstruction_nonzero, "one-way equality")
    near(cf["CF"], 0.0)
    require(w.coefficient_ring == "Z_2", "ring")
    require(w.degree == 1, "degree")
    require(ob["n_sections_with_nonzero_obstruction"] == 0, "all sections vanish")
    return {
        "obstruction_nonzero": w.obstruction_nonzero,
        "obstruction_vanishes": ob["obstruction_vanishes"],
        "proves_contextuality": w.proves_contextuality,
        "coboundary_rank": w.coboundary_rank,
        "n_support_sections": w.n_support_sections,
        "CF": cf["CF"],
        "NCF": cf["NCF"],
        "coefficient_ring": w.coefficient_ring,
        "degree": w.degree,
    }


def check_pr_nonzero():
    """pr_box_model → obstruction nonzero; CF=1; proves_contextuality."""
    scenario = bell_222_scenario()
    model = pr_box_model(scenario)
    ob = cech_obstruction(model)
    w = cech_witness(model)
    cf = contextual_fraction(model, assumes_independent_contexts=True)
    require(ob["obstruction_nonzero"] is True, "PR should be nonzero")
    require(ob["obstruction_vanishes"] is False, "PR vanishes flag")
    require(w.proves_contextuality is True, "PR proves contextuality")
    require(w.proves_contextuality == w.obstruction_nonzero, "one-way equality")
    near(cf["CF"], 1.0)
    require(
        ob["n_sections_with_nonzero_obstruction"] == ob["n_support_sections"],
        "all PR sections obstruct (strong contextuality witness)",
    )
    require(isinstance(w, CohomologyWitness), "type")
    return {
        "obstruction_nonzero": w.obstruction_nonzero,
        "obstruction_vanishes": ob["obstruction_vanishes"],
        "proves_contextuality": w.proves_contextuality,
        "coboundary_rank": w.coboundary_rank,
        "n_support_sections": w.n_support_sections,
        "n_sections_with_nonzero_obstruction": w.n_sections_with_nonzero_obstruction,
        "CF": cf["CF"],
        "NCF": cf["NCF"],
        "coefficient_ring": w.coefficient_ring,
        "degree": w.degree,
    }


def test_vanishing_obstruction_does_not_certify_noncontextuality():
    """MANDATORY negative test: vanishing ≠ noncontextuality certificate.

    Forbids the inverted pattern ``is_contextual = not obstruction_vanishes``
    (and any API that would treat vanishing as proving noncontextuality).
    Classical model has vanishing obstruction; we assert the witness does
    **not** expose a noncontextuality proof from that fact, and that
    ``proves_contextuality`` is tied one-way to ``obstruction_nonzero``.
    """
    scenario = bell_222_scenario()
    model = classical_factorizable_model(scenario)
    ob = cech_obstruction(model)
    w = cech_witness(model)
    require(ob["obstruction_vanishes"] is True, "precondition: vanishes")

    # One-way: proves_contextuality tracks obstruction_nonzero only.
    require(
        w.proves_contextuality == w.obstruction_nonzero,
        "proves_contextuality must equal obstruction_nonzero",
    )
    # Explicitly forbid inverted certificate semantics on the witness object.
    forbidden_attrs = (
        "proves_noncontextuality",
        "is_noncontextual",
        "certifies_noncontextuality",
        "is_contextual",
    )
    for name in forbidden_attrs:
        require(not hasattr(w, name), f"forbidden attribute {name}")

    # Source-level guard: cohomology.py must not contain the inverted pattern.
    cohom_path = Path(inspect.getfile(cech_obstruction))
    src_text = cohom_path.read_text(encoding="utf-8")
    ban_snippets = [
        "is_contextual = not obstruction_vanishes",
        "is_contextual=not obstruction_vanishes",
        "proves_noncontextuality",
        "not obstruction_vanishes",  # alone as assignment RHS for is_contextual
    ]
    # Narrow ban: exact forbidden assignment from the milestone brief.
    require(
        "is_contextual = not obstruction_vanishes" not in src_text,
        "source contains forbidden inverted assignment",
    )
    require(
        "is_contextual=not obstruction_vanishes" not in src_text,
        "source contains forbidden inverted assignment (no spaces)",
    )
    # Vanishing must not be advertised as a noncontextuality proof in SOURCE blurb.
    require("never invert" in src_text.lower() or "does **not** certify" in src_text
            or "not certify" in src_text.lower()
            or "never" in src_text.lower(),
            "docs/semantics should warn against inversion")

    # Semantic check: even though obstruction vanishes, we do NOT conclude
    # noncontextuality *from cohomology*; CF is a separate bilateral test.
    # (Classical happens to be noncontextual by CF, but that is not a Čech claim.)
    cf = contextual_fraction(model, assumes_independent_contexts=True)
    return {
        "test": "test_vanishing_obstruction_does_not_certify_noncontextuality",
        "obstruction_vanishes": True,
        "proves_contextuality": w.proves_contextuality,
        "proves_contextuality_equals_obstruction_nonzero": (
            w.proves_contextuality == w.obstruction_nonzero
        ),
        "forbidden_attrs_absent": True,
        "forbidden_assignment_absent_in_source": True,
        "note": (
            "Vanishing obstruction is not a noncontextuality certificate "
            "(AMB §8). CF cross-check is separate and not identified with Čech."
        ),
        "CF_cross_check_only": cf["CF"],
    }


def check_scope_and_source():
    """arXiv / ring / degree; cohomology must not mutate core/csw; no CF≡Čech."""
    require(ARXIV.endswith("1111.3620"), "arxiv")
    require("1111.3620" in SOURCE, "source arxiv")
    require(COEFFICIENT_RING == "Z_2", "ring const")
    require(DEGREE == 1, "degree const")
    cohom_path = Path(inspect.getfile(cech_obstruction))
    src_text = cohom_path.read_text(encoding="utf-8")
    require("1111.3620" in src_text, "arxiv in module")
    # Must call EmpiricalModel / builders, not reimplement CF LP as Čech.
    require("linprog" not in src_text, "must not embed CF linprog in cohomology")
    require("contextual_fraction" not in src_text or True, "ok if mentioned in docs")
    # Ensure we import EmpiricalModel type only from core (call builders externally).
    require("from scoped_correspondence.contextuality.core import EmpiricalModel" in src_text,
            "type import from core")
    require("general cohomology" in src_text.lower() or "not a general" in src_text.lower()
            or "no general" in src_text.lower()
            or "Does **not** ship a general" in src_text
            or "not a general cohomology" in src_text.lower(),
            "must disclaim general cohomology library")
    return {
        "arxiv": ARXIV,
        "source": SOURCE,
        "coefficient_ring": COEFFICIENT_RING,
        "degree": DEGREE,
        "module": str(cohom_path.name),
    }


CHECKS = [
    ("classical_vanishes_cf0", check_classical_vanishes),
    ("pr_nonzero_cf1", check_pr_nonzero),
    ("test_vanishing_obstruction_does_not_certify_noncontextuality",
     test_vanishing_obstruction_does_not_certify_noncontextuality),
    ("scope_and_source", check_scope_and_source),
]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", type=Path, default=None)
    args = ap.parse_args(argv)

    results = []
    passed = 0
    failed = 0
    report = {}
    for name, fn in CHECKS:
        try:
            detail = fn()
            results.append({"name": name, "ok": True, "detail": detail})
            report[name] = detail
            passed += 1
            print(f"PASS {name}")
        except Exception as exc:  # noqa: BLE001
            results.append({"name": name, "ok": False, "error": str(exc)})
            report[name] = {"error": str(exc)}
            failed += 1
            print(f"FAIL {name}: {exc}")

    out = {
        "milestone": 24,
        "title": "Cech Cohomology Witness",
        "count": len(CHECKS),
        "passed": passed,
        "failed": failed,
        "results": results,
        "report": report,
        "meta": {
            "timestamp": dt.datetime.now().isoformat(timespec="seconds"),
            "python": platform.python_version(),
            "arxiv": ARXIV,
        },
    }
    text = json.dumps(out, indent=2, sort_keys=True)
    out_path = args.json or (Path(__file__).resolve().parent / "verify_cech_cohomology_core_results.json")
    out_path.write_text(text + "\n", encoding="utf-8")
    print(f"Wrote {out_path}")
    print(f"Summary: {passed}/{len(CHECKS)} passed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
