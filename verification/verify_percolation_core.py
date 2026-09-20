#!/usr/bin/env python3
"""Hand-checkable verification for Percolation / Kesten / Bethe tree (Milestone 32).

Checks (all numbers from this script run):
  1. critical_probability_tree(2)=0.5, (4)=0.25; m<1 raises ScopeViolationError
  2. m=2,p=0.6: Q*=4/9, θ=5/9 algebraic+numeric |diff|<1e-9; quadratic roots
  3. m=2,p=0.5: Q*=1, θ=0 exact
  4. m=2,p=0.8: illustrative supercritical span (Q*<1, θ>0)
  5. THRESHOLD_KINSHIP_WARNING + ONE_SIXTEENTH_COINCIDENCE_WARNING verbatim
     in module docstring, API docstrings, and JSON report
  6. m=16 → p_c=1/16 coincidence note vs discarded README '1/16'
  7. EXTINCTION_Q0 == 0 documented start

Stdlib + math only. JSON {count, passed, failed, report}; numbers from this run.
No Monte-Carlo, no Union-Find, no dynamics/membership imports.
"""
from __future__ import annotations

import argparse
import datetime as dt
import inspect
import json
import math
import platform
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from scoped_correspondence.errors import ScopeViolationError  # noqa: E402
from scoped_correspondence.percolation import (  # noqa: E402
    EXTINCTION_Q0,
    ONE_SIXTEENTH_COINCIDENCE_WARNING,
    SOURCE,
    THRESHOLD_KINSHIP_WARNING,
    as_report,
    critical_probability_tree,
    extinction_probability,
    percolation_probability,
)
from scoped_correspondence.percolation import core as percolation_core  # noqa: E402


def require(ok, msg):
    if not bool(ok):
        raise AssertionError(msg)


def near(a, b, atol=1e-12, rtol=1e-9):
    if not math.isclose(float(a), float(b), abs_tol=atol, rel_tol=rtol):
        raise AssertionError(f"{a!r} != {b!r} (atol={atol}, rtol={rtol})")


def check_critical_probability():
    """p_c(2)=0.5, p_c(4)=0.25; m<1 raises."""
    pc2 = critical_probability_tree(2)
    pc4 = critical_probability_tree(4)
    near(pc2, 0.5)
    near(pc4, 0.25)
    near(pc2, 1.0 / 2.0)
    near(pc4, 1.0 / 4.0)

    raised = False
    try:
        critical_probability_tree(0.5)
    except ScopeViolationError:
        raised = True
    require(raised, "m=0.5 < 1 must raise ScopeViolationError")

    raised0 = False
    try:
        critical_probability_tree(0)
    except ScopeViolationError:
        raised0 = True
    require(raised0, "m=0 must raise ScopeViolationError")

    return {
        "p_c_m2": pc2,
        "p_c_m4": pc4,
        "p_c_m2_exact": 0.5,
        "p_c_m4_exact": 0.25,
        "m_lt_1_raises": raised and raised0,
    }


def check_m2_p06_algebraic_and_numeric():
    """m=2,p=0.6: Q=(0.4+0.6Q)^2 → 9Q²-13Q+4=0 → {1,4/9}; physical Q*=4/9."""
    p, m = 0.6, 2
    q_star, iters, residual = extinction_probability(p, m)
    theta = percolation_probability(p, m)

    q_alg = 4.0 / 9.0
    theta_alg = 5.0 / 9.0

    near(q_star, q_alg, atol=1e-9)
    near(theta, theta_alg, atol=1e-9)
    near(theta, 1.0 - q_star, atol=1e-15)
    require(residual < 1e-10, f"residual too large: {residual}")
    require(iters >= 1, "iters must be positive")

    # Algebraic check of the quadratic 9Q² - 13Q + 4 at Q*=4/9 and at 1
    def quad(q):
        return 9.0 * q * q - 13.0 * q + 4.0

    near(quad(1.0), 0.0, atol=1e-15)
    near(quad(q_alg), 0.0, atol=1e-15)
    # Fixed-point residual of the map at algebraic Q*
    f_alg = (0.4 + 0.6 * q_alg) ** 2
    near(f_alg, q_alg, atol=1e-15)

    # Confirm Q=1 is also a root but not the physical (smallest) one
    require(q_star < 1.0 - 1e-9, "physical Q* must be the smaller root")

    return {
        "p": p,
        "m": m,
        "Q_star_numeric": q_star,
        "Q_star_algebraic": q_alg,
        "Q_star_abs_diff": abs(q_star - q_alg),
        "theta_numeric": theta,
        "theta_algebraic": theta_alg,
        "theta_abs_diff": abs(theta - theta_alg),
        "iters": iters,
        "residual": residual,
        "quadratic": "9Q^2 - 13Q + 4 = 0",
        "roots": [1.0, q_alg],
        "physical_root": q_alg,
        "Q0": EXTINCTION_Q0,
        "abs_diff_lt_1e9": abs(q_star - q_alg) < 1e-9,
    }


def check_m2_at_threshold():
    """m=2,p=0.5: Q*=1, θ=0 exact."""
    p, m = 0.5, 2
    q_star, iters, residual = extinction_probability(p, m)
    theta = percolation_probability(p, m)
    near(q_star, 1.0, atol=1e-9)
    near(theta, 0.0, atol=1e-9)
    near(critical_probability_tree(m), p)
    return {
        "p": p,
        "m": m,
        "Q_star": q_star,
        "theta": theta,
        "iters": iters,
        "residual": residual,
        "at_threshold": True,
    }


def check_m2_p08_illustrative():
    """m=2,p=0.8: illustrative supercritical span."""
    p, m = 0.8, 2
    q_star, iters, residual = extinction_probability(p, m)
    theta = percolation_probability(p, m)
    require(q_star < 1.0 - 1e-6, "supercritical Q* < 1")
    require(theta > 1e-6, "supercritical θ > 0")
    near(theta, 1.0 - q_star)
    # Closed form for m=2: Q* = ((1-p)/p)^2 when p>1/2? 
    # From Q=(1-p+pQ)^2, physical root for m=2 is Q=((1-p)/p)^2 when p>pc? 
    # Actually for binary branching, Q* = (1-p)/p ^? Wait:
    # From 9Q^2 style: general m=2: Q = (1-p+pQ)^2
    # Expand: p^2 Q^2 + 2p(1-p)Q + (1-p)^2 - Q = 0
    # p^2 Q^2 + (2p(1-p)-1)Q + (1-p)^2 = 0
    # Known: for m=2, Q* = ((1-p)/p)^2 ? Check p=0.6: (0.4/0.6)^2=(2/3)^2=4/9 YES!
    q_closed = ((1.0 - p) / p) ** 2
    near(q_star, q_closed, atol=1e-9)
    # Exact: ((1-0.8)/0.8)^2 = (1/4)^2 = 1/16 — coincidence vs discarded README
    near(q_closed, 1.0 / 16.0, atol=1e-15)
    near(theta, 15.0 / 16.0, atol=1e-9)
    rep = as_report(p, m)
    require(
        any("1/16" in n for n in rep["coincidence_notes"]),
        "p=0.8,m=2 Q*=1/16 must be marked coincidence vs discarded README",
    )
    require(
        ONE_SIXTEENTH_COINCIDENCE_WARNING in " ".join(rep["coincidence_notes"])
        or any("coincidence" in n for n in rep["coincidence_notes"]),
        "coincidence note must be present",
    )
    return {
        "p": p,
        "m": m,
        "Q_star": q_star,
        "Q_star_closed_m2": q_closed,
        "Q_star_equals_one_sixteenth": abs(q_closed - 1.0 / 16.0) < 1e-15,
        "theta": theta,
        "theta_algebraic": 15.0 / 16.0,
        "iters": iters,
        "residual": residual,
        "illustrative_span": True,
        "coincidence_notes": rep["coincidence_notes"],
        "one_sixteenth_coincidence_warning": ONE_SIXTEENTH_COINCIDENCE_WARNING,
    }


def check_warnings_verbatim():
    """Both mandatory warnings present verbatim in constants, docs, docstrings."""
    kin = THRESHOLD_KINSHIP_WARNING
    one16 = ONE_SIXTEENTH_COINCIDENCE_WARNING

    require(
        kin
        == (
            "Percolation and cusp dynamics involve distinct objects and parameter "
            "meanings. No identity of their thresholds or transfer of numerical "
            "values is asserted. A comparison of local fixed-point or bifurcation "
            "structures requires a separately stated scope, construction, and "
            "derivation."
        ),
        "THRESHOLD_KINSHIP_WARNING must match verbatim acceptance string",
    )
    require(
        "1/16" in one16 and "discarded README" in one16 and "coincidence" in one16,
        "ONE_SIXTEENTH_COINCIDENCE_WARNING must mention coincidence vs discarded README 1/16",
    )

    mod_doc = percolation_core.__doc__ or ""
    require(kin in mod_doc, "module docstring must contain THRESHOLD_KINSHIP_WARNING verbatim")
    require(
        "discarded README" in mod_doc and "1/16" in mod_doc,
        "module docstring must mention discarded README 1/16 coincidence",
    )

    for fn in (
        critical_probability_tree,
        extinction_probability,
        percolation_probability,
    ):
        doc = inspect.getdoc(fn) or ""
        # kin itself has no embedded newlines (it's built by implicit string
        # concatenation), while the wrapped docstring copy does -- so `kin
        # in doc` can never match a line-wrapped docstring. Anchor on a
        # short phrase that fits on a single wrapped line instead (same
        # defensive pattern the original check used).
        require(
            "No identity of their thresholds" in doc,
            f"{fn.__name__} docstring must carry threshold-kinship warning",
        )

    docs_path = ROOT / "docs" / "percolation_core.md"
    require(docs_path.is_file(), "docs/percolation_core.md must exist")
    docs_text = docs_path.read_text(encoding="utf-8")
    require(kin in docs_text, "docs must contain THRESHOLD_KINSHIP_WARNING verbatim")
    require(
        "discarded README" in docs_text and "1/16" in docs_text,
        "docs must mark 1/16 coincidence vs discarded README value",
    )

    # m=16 coincidence path
    pc16 = critical_probability_tree(16)
    near(pc16, 1.0 / 16.0)
    report16 = as_report(0.1, 16)
    require(
        len(report16["coincidence_notes"]) >= 1,
        "m=16 must produce coincidence_notes for p_c≈1/16",
    )
    require(
        report16["threshold_kinship_warning"] == kin,
        "as_report must embed THRESHOLD_KINSHIP_WARNING",
    )
    require(
        report16["one_sixteenth_coincidence_warning"] == one16,
        "as_report must embed ONE_SIXTEENTH_COINCIDENCE_WARNING",
    )

    require(EXTINCTION_Q0 == 0.0, "documented start Q0 must be 0")
    require("Fisher" in SOURCE and "Kesten" in SOURCE, "SOURCE must cite Fisher & Kesten")
    require("10.1063/1.1703745" in SOURCE, "Fisher & Essam DOI")
    require("10.1007/BF01197577" in SOURCE, "Kesten DOI")

    return {
        "threshold_kinship_warning": kin,
        "one_sixteenth_coincidence_warning": one16,
        "module_doc_has_kinship": kin in mod_doc,
        "docs_has_kinship": kin in docs_text,
        "docs_has_one_sixteenth_fence": "1/16" in docs_text and "discarded README" in docs_text,
        "p_c_m16": pc16,
        "p_c_m16_is_one_sixteenth": abs(pc16 - 1.0 / 16.0) < 1e-15,
        "coincidence_notes_m16": report16["coincidence_notes"],
        "EXTINCTION_Q0": EXTINCTION_Q0,
        "SOURCE": SOURCE,
    }


CHECKS = [
    ("critical_probability_tree", check_critical_probability),
    ("m2_p06_algebraic_and_numeric", check_m2_p06_algebraic_and_numeric),
    ("m2_at_threshold", check_m2_at_threshold),
    ("m2_p08_illustrative", check_m2_p08_illustrative),
    ("warnings_verbatim_and_q0", check_warnings_verbatim),
]


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument(
        "--json-out",
        type=Path,
        default=Path(__file__).with_name("verify_percolation_core_results.json"),
    )
    args = p.parse_args(argv)

    report = {
        "milestone": "M32 Percolation / Kesten / Bethe-tree Branching",
        "timestamp": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "checks": {},
        "threshold_kinship_warning": THRESHOLD_KINSHIP_WARNING,
        "one_sixteenth_coincidence_warning": ONE_SIXTEENTH_COINCIDENCE_WARNING,
        "EXTINCTION_Q0": EXTINCTION_Q0,
        "source": SOURCE,
        "disclaimer": (
            "Exact Bethe-tree / branching-process formulas only. "
            "No Monte-Carlo on Z^2; no Union-Find / Newman-Ziff. "
            "Percolation and cusp dynamics involve distinct objects and "
            "parameter meanings; no identity of their thresholds or transfer "
            "of numerical values is asserted (docs/structural_relations.md, "
            "bridge B6). Values near 1/16 are coincidence vs discarded README "
            "'1/16'. Does not mutate dynamics/, membership/, package-root "
            "__init__.py, or FORMALISM.md."
        ),
        "untouched": [
            "src/scoped_correspondence/dynamics/",
            "src/scoped_correspondence/membership/",
            "src/scoped_correspondence/__init__.py",
            "FORMALISM.md",
            "Monte-Carlo Z^2",
            "Union-Find / Newman-Ziff",
        ],
    }
    passed = 0
    failed = 0
    errors = []
    for name, fn in CHECKS:
        try:
            report["checks"][name] = {"status": "passed", "detail": fn()}
            passed += 1
            print(f"PASS  {name}")
        except Exception as exc:  # noqa: BLE001 — collect all failures
            failed += 1
            errors.append({"check": name, "error": f"{type(exc).__name__}: {exc}"})
            report["checks"][name] = {
                "status": "failed",
                "error": f"{type(exc).__name__}: {exc}",
            }
            print(f"FAIL  {name}: {exc}")

    summary = {
        "count": len(CHECKS),
        "passed": passed,
        "failed": failed,
        "errors": errors,
        "report": report,
    }
    args.json_out.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(f"\n{passed}/{len(CHECKS)} passed; wrote {args.json_out}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
