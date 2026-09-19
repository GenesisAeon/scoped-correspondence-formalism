#!/usr/bin/env python3
"""Hand-checkable verification for Fenichel / GSPT (Milestone 33).

Checks (all numbers from this script run):
  1. critical_manifold_fold_points: (1, -2/3), (-1, +2/3) exact
  2. is_normally_hyperbolic: True at x=2,0,1.5; False at ±1
  3. S / S' analytic identities at those points; S'(±1)=0
  4. slow_manifold_distance_bound(ε,x)=|ε| on NH; ScopeViolation at folds / ε≤0
  5. Sources Fenichel 1979 + Kuehn 2015 DOIs; INDEPENDENCE_WARNING verbatim;
     no import of contraction / landau

Stdlib only (math). JSON {count, passed, failed, report}; numbers from this run.
Does not mutate dynamics/core.py; independent of M14/M29.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import platform
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from scoped_correspondence.dynamics import gspt as gspt_mod  # noqa: E402
from scoped_correspondence.dynamics.gspt import (  # noqa: E402
    INDEPENDENCE_WARNING,
    SOURCE,
    FoldPoint,
    critical_manifold_S,
    critical_manifold_S_prime,
    critical_manifold_fold_points,
    is_normally_hyperbolic,
    slow_manifold_distance_bound,
)
from scoped_correspondence.errors import ScopeViolationError  # noqa: E402


def require(ok, msg):
    if not bool(ok):
        raise AssertionError(msg)


def near(a, b, atol=1e-15, rtol=1e-12):
    if not math.isclose(float(a), float(b), abs_tol=atol, rel_tol=rtol):
        raise AssertionError(f"{a!r} != {b!r}")


def check_fold_points_exact():
    """Folds at x=±1, S=∓2/3 exact."""
    folds = critical_manifold_fold_points()
    require(len(folds) == 2, f"expected 2 folds, got {len(folds)}")
    f_pos, f_neg = folds
    require(isinstance(f_pos, FoldPoint) and isinstance(f_neg, FoldPoint), "FoldPoint type")
    near(f_pos.x, 1.0)
    near(f_pos.s, -2.0 / 3.0)
    near(f_neg.x, -1.0)
    near(f_neg.s, 2.0 / 3.0)
    # Cross-check against S
    near(critical_manifold_S(1.0), -2.0 / 3.0)
    near(critical_manifold_S(-1.0), 2.0 / 3.0)
    near(critical_manifold_S(1.0), f_pos.s)
    near(critical_manifold_S(-1.0), f_neg.s)
    return {
        "fold_plus": f_pos.to_dict(),
        "fold_minus": f_neg.to_dict(),
        "S_at_plus_1": critical_manifold_S(1.0),
        "S_at_minus_1": critical_manifold_S(-1.0),
        "expected_S_plus": -2.0 / 3.0,
        "expected_S_minus": 2.0 / 3.0,
    }


def check_normally_hyperbolic_example():
    """NH True at 2, 0, 1.5; False at ±1. S' values match x²-1."""
    cases_true = {
        2.0: 3.0,
        0.0: -1.0,
        1.5: 1.25,
    }
    detail = {"true_cases": {}, "false_cases": {}}
    for x, s_prime_expected in cases_true.items():
        nh = is_normally_hyperbolic(x)
        sp = critical_manifold_S_prime(x)
        require(nh is True, f"expected NH True at x={x}, got {nh}")
        near(sp, s_prime_expected)
        near(sp, x * x - 1.0)
        detail["true_cases"][str(x)] = {
            "x": x,
            "is_normally_hyperbolic": nh,
            "S_prime": sp,
            "S_prime_expected": s_prime_expected,
        }
    for x in (1.0, -1.0):
        nh = is_normally_hyperbolic(x)
        sp = critical_manifold_S_prime(x)
        require(nh is False, f"expected NH False at x={x}, got {nh}")
        near(sp, 0.0)
        detail["false_cases"][str(x)] = {
            "x": x,
            "is_normally_hyperbolic": nh,
            "S_prime": sp,
        }
    return detail


def check_S_identities():
    """S(x)=x³/3−x at a few hand points; S'(±1)=0."""
    samples = {
        0.0: 0.0,
        1.0: -2.0 / 3.0,
        -1.0: 2.0 / 3.0,
        2.0: 2.0 / 3.0,  # 8/3 - 2 = 8/3 - 6/3 = 2/3
        3.0: 6.0,  # 9 - 3 = 6
    }
    out = {}
    for x, expected in samples.items():
        got = critical_manifold_S(x)
        near(got, expected)
        out[str(x)] = {"S": got, "S_expected": expected}
    near(critical_manifold_S_prime(1.0), 0.0)
    near(critical_manifold_S_prime(-1.0), 0.0)
    out["S_prime_at_folds"] = {
        "plus_1": critical_manifold_S_prime(1.0),
        "minus_1": critical_manifold_S_prime(-1.0),
    }
    return out


def check_slow_manifold_distance_bound():
    """O(ε) order estimate = |ε| on NH; ScopeViolation at folds / ε≤0."""
    eps = 0.01
    x_nh = 2.0
    bound = slow_manifold_distance_bound(eps, x_nh)
    near(bound, abs(eps))
    near(slow_manifold_distance_bound(eps, 0.0), abs(eps))
    near(slow_manifold_distance_bound(eps, 1.5), abs(eps))

    fold_raised = False
    try:
        slow_manifold_distance_bound(eps, 1.0)
    except ScopeViolationError:
        fold_raised = True
    require(fold_raised, "fold x=1 must raise ScopeViolationError")

    fold_m_raised = False
    try:
        slow_manifold_distance_bound(eps, -1.0)
    except ScopeViolationError:
        fold_m_raised = True
    require(fold_m_raised, "fold x=-1 must raise ScopeViolationError")

    eps_raised = False
    try:
        slow_manifold_distance_bound(0.0, 2.0)
    except ScopeViolationError:
        eps_raised = True
    require(eps_raised, "epsilon<=0 must raise ScopeViolationError")

    neg_raised = False
    try:
        slow_manifold_distance_bound(-0.1, 2.0)
    except ScopeViolationError:
        neg_raised = True
    require(neg_raised, "epsilon<0 must raise ScopeViolationError")

    return {
        "epsilon": eps,
        "x_nh": x_nh,
        "bound": bound,
        "bound_equals_abs_epsilon": bound == abs(eps),
        "order_estimate_only": True,
        "fold_plus_raises": fold_raised,
        "fold_minus_raises": fold_m_raised,
        "epsilon_le_0_raises": eps_raised,
        "epsilon_neg_raises": neg_raised,
    }


def check_sources_and_independence():
    """Fenichel + Kuehn DOIs; independence warning; no contraction/landau import."""
    require("10.1016/0022-0396(79)90152-9" in SOURCE, "Fenichel DOI missing")
    require("10.1007/978-3-319-12316-5" in SOURCE, "Kuehn DOI missing")
    require("Fenichel" in SOURCE, "Fenichel name missing")
    require("Kuehn" in SOURCE, "Kuehn name missing")
    require(
        INDEPENDENCE_WARNING == "Independent of M14 contraction and M29 Landau.",
        f"INDEPENDENCE_WARNING mismatch: {INDEPENDENCE_WARNING!r}",
    )
    # Module docstring must carry the independence fence
    mod_doc = (gspt_mod.__doc__ or "")
    mod_doc_plain = mod_doc.lower().replace("*", "")
    require(
        "independent of m14 contraction" in mod_doc_plain
        and "m29 landau" in mod_doc_plain,
        "module docstring missing M14/M29 independence language",
    )
    # API docstrings
    for fn in (
        critical_manifold_fold_points,
        is_normally_hyperbolic,
        slow_manifold_distance_bound,
    ):
        doc = fn.__doc__ or ""
        require(
            "Independent of M14 contraction and M29 Landau" in doc,
            f"{fn.__name__} docstring missing independence sentence",
        )
    # Source file must not import contraction or landau (docstring may mention them)
    src_path = Path(gspt_mod.__file__)
    text = src_path.read_text(encoding="utf-8")
    import_lines = [
        ln.strip()
        for ln in text.splitlines()
        if ln.strip().startswith(("import ", "from "))
    ]
    joined = "\n".join(import_lines)
    require(
        "contraction" not in joined,
        f"gspt.py must not import contraction (M14); imports={import_lines!r}",
    )
    require(
        "landau" not in joined,
        f"gspt.py must not import landau (M29); imports={import_lines!r}",
    )
    require(
        "scoped_correspondence.dynamics.core" not in joined,
        "gspt.py must not import dynamics.core (independent geometry)",
    )
    return {
        "SOURCE": SOURCE,
        "INDEPENDENCE_WARNING": INDEPENDENCE_WARNING,
        "cites_fenichel": "10.1016/0022-0396(79)90152-9" in SOURCE,
        "cites_kuehn": "10.1007/978-3-319-12316-5" in SOURCE,
        "independence_in_module_doc": True,
        "independence_in_api_docs": True,
        "no_contraction_import": True,
        "no_landau_import": True,
    }


CHECKS = [
    ("fold_points_exact", check_fold_points_exact),
    ("normally_hyperbolic_example", check_normally_hyperbolic_example),
    ("S_identities", check_S_identities),
    ("slow_manifold_distance_bound", check_slow_manifold_distance_bound),
    ("sources_and_independence", check_sources_and_independence),
]


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--json-out",
        type=Path,
        default=Path(__file__).with_name("verify_gspt_core_results.json"),
    )
    args = p.parse_args(argv)

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
            print(f"PASS  {name}")
        except Exception as exc:  # noqa: BLE001 — collect all failures
            results.append({"name": name, "ok": False, "error": f"{type(exc).__name__}: {exc}"})
            report[name] = {"error": f"{type(exc).__name__}: {exc}"}
            failed += 1
            print(f"FAIL  {name}: {exc}")

    report["INDEPENDENCE_WARNING"] = INDEPENDENCE_WARNING
    report["meta"] = {
        "milestone": 33,
        "title": "Fenichel / GSPT Critical Manifold",
        "platform": platform.platform(),
        "python": sys.version.split()[0],
        "utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "source": SOURCE,
        "INDEPENDENCE_WARNING": INDEPENDENCE_WARNING,
        "forbidden_untouched": [
            "src/scoped_correspondence/dynamics/core.py",
            "src/scoped_correspondence/__init__.py",
            "FORMALISM.md",
        ],
    }

    payload = {
        "count": len(CHECKS),
        "passed": passed,
        "failed": failed,
        "results": results,
        "report": report,
        "INDEPENDENCE_WARNING": INDEPENDENCE_WARNING,
    }
    args.json_out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"\n{passed}/{len(CHECKS)} passed; wrote {args.json_out}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
