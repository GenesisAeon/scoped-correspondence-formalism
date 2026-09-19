#!/usr/bin/env python3
"""Hand-checkable verification for Landau Exponent Comparison (Milestone 29).

Checks (all numbers from this script run):
  1. mean_field_order_parameter(0.25)=0.5, (0.0625)=0.25 via fixed_points CALL
  2. compare_scaling_exponents(0.25, 0.0625): actual=MF=2.0; Ising≈1.189;
     discrepancy factor ≈1.682; beta_crit model-specific note present
  3. Control a1=a2 → all ratios 1.0
  4. onsager_critical_ratio() ≈ 2.269185314213022; ONSAGER_SIGMA_WARNING
     appears verbatim in docstring AND JSON report field
  5. MEAN_FIELD_BETA=0.5, ISING_2D_BETA=0.125; sources cite Onsager/Yang/
     Guckenheimer & Holmes; no Landau 1937 citation

Stdlib only (math). JSON {count, passed, failed, report}; numbers from this run.
Calls real fixed_points (dynamics/core.py unchanged; CALL only).
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

from scoped_correspondence.dynamics.core import fixed_points  # noqa: E402
from scoped_correspondence.dynamics.landau import (  # noqa: E402
    ISING_2D_BETA,
    MEAN_FIELD_BETA,
    ONSAGER_SIGMA_WARNING,
    SOURCE,
    compare_scaling_exponents,
    mean_field_order_parameter,
    onsager_critical_ratio,
)
from scoped_correspondence.errors import ScopeViolationError  # noqa: E402


def require(ok, msg):
    if not bool(ok):
        raise AssertionError(msg)


def near(a, b, atol=1e-12, rtol=1e-9):
    if not math.isclose(float(a), float(b), abs_tol=atol, rel_tol=rtol):
        raise AssertionError(f"{a!r} != {b!r}")


def check_order_parameter_via_fixed_points():
    """x*(0.25)=0.5, x*(0.0625)=0.25; must match fixed_points positive root."""
    a1, a2 = 0.25, 0.0625
    x1 = mean_field_order_parameter(a1)
    x2 = mean_field_order_parameter(a2)
    near(x1, 0.5)
    near(x2, 0.25)

    roots1 = fixed_points(a1, 0.0)
    roots2 = fixed_points(a2, 0.0)
    pos1 = max(r for r in roots1 if r > 1e-12)
    pos2 = max(r for r in roots2 if r > 1e-12)
    near(x1, pos1)
    near(x2, pos2)
    # Must NOT be an independent math.sqrt re-implementation path that
    # diverges from fixed_points (identity via CALL).
    near(x1, math.sqrt(a1))
    near(x2, math.sqrt(a2))

    raised = False
    try:
        mean_field_order_parameter(0.0)
    except ScopeViolationError:
        raised = True
    require(raised, "a<=0 must raise ScopeViolationError")

    return {
        "a1": a1,
        "a2": a2,
        "x_star_a1": x1,
        "x_star_a2": x2,
        "fixed_points_positive_a1": float(pos1),
        "fixed_points_positive_a2": float(pos2),
        "uses_fixed_points_call": True,
        "a_le_0_raises": raised,
    }


def check_scaling_example():
    """a1=0.25, a2=0.0625 → ratio 2.0 exact MF; Ising≈1.189; factor≈1.68."""
    a1, a2 = 0.25, 0.0625
    cmp_ = compare_scaling_exponents(a1, a2)
    near(cmp_.x_star_a1, 0.5)
    near(cmp_.x_star_a2, 0.25)
    near(cmp_.actual_ratio, 2.0)
    near(cmp_.mean_field_ratio, 2.0)
    near(cmp_.ising_hypothetical_ratio, (a1 / a2) ** 0.125)
    near(cmp_.ising_hypothetical_ratio, 1.189207115002721, atol=1e-12)
    near(cmp_.discrepancy_factor_mf_over_ising, 2.0 / cmp_.ising_hypothetical_ratio)
    near(cmp_.discrepancy_factor_mf_over_ising, 1.6817928305074292, atol=1e-12)
    require(cmp_.matches_mean_field is True, "must match mean-field")
    near(cmp_.mean_field_beta, MEAN_FIELD_BETA)
    near(cmp_.ising_2d_beta, ISING_2D_BETA)
    near(MEAN_FIELD_BETA, 0.5)
    near(ISING_2D_BETA, 0.125)
    require(
        "model-specific" in cmp_.beta_crit_note.lower()
        and "not universal" in cmp_.beta_crit_note.lower()
        and "§12" in cmp_.beta_crit_note,
        f"beta_crit note missing FORMALISM §12 language: {cmp_.beta_crit_note!r}",
    )
    return {
        "a1": a1,
        "a2": a2,
        "x_star_a1": cmp_.x_star_a1,
        "x_star_a2": cmp_.x_star_a2,
        "actual_ratio": cmp_.actual_ratio,
        "mean_field_ratio": cmp_.mean_field_ratio,
        "ising_hypothetical_ratio": cmp_.ising_hypothetical_ratio,
        "discrepancy_factor_mf_over_ising": cmp_.discrepancy_factor_mf_over_ising,
        "matches_mean_field": cmp_.matches_mean_field,
        "beta_crit_note": cmp_.beta_crit_note,
        "MEAN_FIELD_BETA": MEAN_FIELD_BETA,
        "ISING_2D_BETA": ISING_2D_BETA,
    }


def check_control_equal_a():
    """a1=a2 → all ratios 1.0."""
    a = 0.25
    cmp_ = compare_scaling_exponents(a, a)
    near(cmp_.actual_ratio, 1.0)
    near(cmp_.mean_field_ratio, 1.0)
    near(cmp_.ising_hypothetical_ratio, 1.0)
    near(cmp_.discrepancy_factor_mf_over_ising, 1.0)
    require(cmp_.matches_mean_field is True, "control must match MF")
    return {
        "a1": a,
        "a2": a,
        "actual_ratio": cmp_.actual_ratio,
        "mean_field_ratio": cmp_.mean_field_ratio,
        "ising_hypothetical_ratio": cmp_.ising_hypothetical_ratio,
        "discrepancy_factor_mf_over_ising": cmp_.discrepancy_factor_mf_over_ising,
    }


def check_onsager_and_sigma_warning():
    """Onsager ratio + mandatory σ≈2.2 coincidence warning (docstring + JSON)."""
    ratio = onsager_critical_ratio()
    expected = 2.0 / math.log(1.0 + math.sqrt(2.0))
    near(ratio, expected)
    near(ratio, 2.269185314213022, atol=1e-15)

    doc = onsager_critical_ratio.__doc__ or ""
    require(
        ONSAGER_SIGMA_WARNING in doc,
        "ONSAGER_SIGMA_WARNING must appear verbatim in onsager_critical_ratio docstring",
    )
    require("σ≈2.2" in ONSAGER_SIGMA_WARNING or "sigma" in ONSAGER_SIGMA_WARNING.lower(),
            "warning must mention discarded σ≈2.2")
    require(
        abs(ratio - 2.2) < 0.1,
        "sanity: Onsager ratio is numerically near 2.2 (coincidence only)",
    )
    require(
        abs(ratio - 2.2) > 0.05,
        "Onsager ratio must remain distinguishable from exactly 2.2",
    )
    return {
        "onsager_critical_ratio": ratio,
        "onsager_critical_ratio_expected": expected,
        "ONSAGER_SIGMA_WARNING": ONSAGER_SIGMA_WARNING,
        "warning_in_docstring": ONSAGER_SIGMA_WARNING in doc,
        "ecosystem_sigma_approx_refused": 2.2,
    }


def check_sources_no_landau_1937():
    """Cite Onsager / Yang / Guckenheimer & Holmes; forbid Landau 1937."""
    require("10.1103/PhysRev.65.117" in SOURCE, "Onsager DOI missing")
    require("10.1103/PhysRev.85.808" in SOURCE, "Yang DOI missing")
    require("10.1007/978-1-4612-1140-2" in SOURCE, "Guckenheimer & Holmes DOI missing")
    require("Onsager" in SOURCE, "Onsager name missing")
    require("Yang" in SOURCE, "Yang name missing")
    require("Guckenheimer" in SOURCE, "Guckenheimer name missing")
    landau_mod = Path(SRC / "scoped_correspondence" / "dynamics" / "landau.py")
    text = landau_mod.read_text(encoding="utf-8")
    # Any mention of Landau 1937 must be an explicit non-citation / forbid note
    for line in text.splitlines():
        low = line.strip().lower().replace("*", "")
        if "landau" in low and "1937" in low:
            forbid_ok = (
                "not cite" in low
                or "do not cite" in low
                or "dont cite" in low
                or "forbid" in low
                or "do not" in low
            )
            require(
                forbid_ok,
                f"affirmative Landau 1937 citation forbidden: {line!r}",
            )
    require("Landau, L." not in text, "Landau, L. bibliographic cite forbidden")
    return {
        "SOURCE": SOURCE,
        "cites_onsager": "10.1103/PhysRev.65.117" in SOURCE,
        "cites_yang": "10.1103/PhysRev.85.808" in SOURCE,
        "cites_guckholmes": "10.1007/978-1-4612-1140-2" in SOURCE,
        "landau_1937_not_cited_as_source": True,
    }


CHECKS = [
    ("order_parameter_via_fixed_points", check_order_parameter_via_fixed_points),
    ("scaling_example_a1_0.25_a2_0.0625", check_scaling_example),
    ("control_equal_a", check_control_equal_a),
    ("onsager_and_sigma_warning", check_onsager_and_sigma_warning),
    ("sources_no_landau_1937", check_sources_no_landau_1937),
]


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--json-out",
        type=Path,
        default=Path(__file__).with_name("verify_landau_exponent_comparison_results.json"),
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

    # Top-level mandatory warning field (verbatim) for parent/JSON consumers
    report["ONSAGER_SIGMA_WARNING"] = ONSAGER_SIGMA_WARNING
    report["meta"] = {
        "milestone": 29,
        "title": "Landau Exponent Comparison / Self-Falsification",
        "platform": platform.platform(),
        "python": sys.version.split()[0],
        "utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "source": SOURCE,
        "MEAN_FIELD_BETA": MEAN_FIELD_BETA,
        "ISING_2D_BETA": ISING_2D_BETA,
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
        "ONSAGER_SIGMA_WARNING": ONSAGER_SIGMA_WARNING,
    }
    args.json_out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"\n{passed}/{len(CHECKS)} passed; wrote {args.json_out}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
