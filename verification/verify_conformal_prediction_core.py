#!/usr/bin/env python3
"""Hand-checkable verification for Split Conformal Prediction (Milestone 13).

Checks (all numbers from this script run):
  1. Example A: R=(1,1,2,3), alpha=0.2 → q=3; y_hat=10 → [7,13]
  2. Example B: R=(0.5,1.0,1.5,2.0,4.0), alpha=0.25 → q=4; y_hat=10 → [6,14]
  3. VAL-CONF-LEAK-001: overlapping calib/holdout indices raise ScopeViolationError
  4. coverage_kind is always "marginal_exchangeable" (never guaranteed/exact)

Stdlib only (math). JSON {count, passed, failed, report}; numbers from this run.
Does not import or mutate validation.core / Cygnus data.
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

from scoped_correspondence.errors import ScopeViolationError  # noqa: E402
from scoped_correspondence.validation.conformal import (  # noqa: E402
    COVERAGE_MARGINAL_EXCHANGEABLE,
    SplitConformalReport,
    assert_disjoint_calib_holdout,
    calibrate_split_conformal,
    make_split_conformal_report,
    predict_interval,
)


def require(ok, msg):
    if not bool(ok):
        raise AssertionError(msg)


def near(a, b, atol=1e-12, rtol=1e-9):
    if not math.isclose(float(a), float(b), abs_tol=atol, rel_tol=rtol):
        raise AssertionError(f"{a!r} != {b!r}")


def check_example_a():
    """R=(1,1,2,3), alpha=0.2 → n=4, ceil(5*0.8)=4 → q=3; [7,13]."""
    residuals = (1.0, 1.0, 2.0, 3.0)
    alpha = 0.2
    n = len(residuals)
    k = int(math.ceil((n + 1) * (1.0 - alpha)))
    require(k == 4, f"k expected 4, got {k}")
    q = calibrate_split_conformal(residuals, alpha)
    near(q, 3.0)
    lo, hi = predict_interval(10.0, q)
    near(lo, 7.0)
    near(hi, 13.0)

    report = make_split_conformal_report(
        residuals,
        alpha,
        10.0,
        calib_indices=(0, 1, 2, 3),
        holdout_indices=(4, 5),
    )
    require(isinstance(report, SplitConformalReport), "type")
    near(report.q, 3.0)
    require(report.interval == (7.0, 13.0), f"interval={report.interval}")
    require(
        report.coverage_kind == COVERAGE_MARGINAL_EXCHANGEABLE,
        f"coverage_kind={report.coverage_kind}",
    )
    require(
        report.coverage_kind not in ("guaranteed", "exact", "conditional"),
        "must not claim guaranteed/exact/conditional",
    )
    require("10.1080/01621459.2017.1307116" in report.source, "DOI in source")
    require(any("+1" in a or "n+1" in a for a in report.assumptions), "+1 note")

    return {
        "residuals": list(residuals),
        "alpha": alpha,
        "n": n,
        "k": k,
        "q": q,
        "y_hat": 10.0,
        "interval": [lo, hi],
        "coverage_kind": report.coverage_kind,
        "source": report.source,
    }


def check_example_b():
    """Independent: R=(0.5,1,1.5,2,4), alpha=0.25 → ceil(6*0.75)=5 → q=4; [6,14]."""
    residuals = (0.5, 1.0, 1.5, 2.0, 4.0)
    alpha = 0.25
    n = len(residuals)
    k = int(math.ceil((n + 1) * (1.0 - alpha)))
    require(k == 5, f"k expected 5, got {k}")
    q = calibrate_split_conformal(residuals, alpha)
    near(q, 4.0)
    lo, hi = predict_interval(10.0, q)
    near(lo, 6.0)
    near(hi, 14.0)

    # Naive quantile without +1 would use ceil(n*(1-alpha))=ceil(3.75)=4 → R_(4)=2.0
    # and undercover relative to the finite-sample rule.
    naive_k = int(math.ceil(n * (1.0 - alpha)))
    ordered = sorted(residuals)
    naive_q = ordered[naive_k - 1]
    require(naive_q == 2.0, f"naive_q sanity={naive_q}")
    require(q > naive_q, "finite-sample q strictly larger than naive here")

    return {
        "residuals": list(residuals),
        "alpha": alpha,
        "n": n,
        "k": k,
        "q": q,
        "y_hat": 10.0,
        "interval": [lo, hi],
        "naive_k_without_plus1": naive_k,
        "naive_q_without_plus1": naive_q,
        "note": "naive empirical quantile undercovers vs (n+1) ceiling rule",
    }


def check_val_conf_leak_001():
    """Overlapping calib/holdout indices must raise (anti-leak)."""
    # Disjoint: OK
    assert_disjoint_calib_holdout((0, 1, 2), (3, 4, 5))

    # Overlap at 2: must fire
    raised = False
    err_msg = ""
    try:
        assert_disjoint_calib_holdout((0, 1, 2), (2, 3, 4))
    except ScopeViolationError as exc:
        raised = True
        err_msg = str(exc)
    require(raised, "expected ScopeViolationError on overlap")
    require("VAL-CONF-LEAK-001" in err_msg, f"tag in message: {err_msg}")
    require("overlap" in err_msg.lower(), f"overlap mentioned: {err_msg}")

    # make_split_conformal_report must also refuse overlap before calibrating
    raised2 = False
    try:
        make_split_conformal_report(
            (1.0, 2.0, 3.0),
            0.2,
            10.0,
            calib_indices=(0, 1),
            holdout_indices=(1, 2),
        )
    except ScopeViolationError as exc:
        raised2 = True
        require("VAL-CONF-LEAK-001" in str(exc), str(exc))
    require(raised2, "make_split_conformal_report must enforce leak guard")

    return {
        "test_id": "VAL-CONF-LEAK-001",
        "disjoint_ok": True,
        "overlap_raises": True,
        "overlap_indices_example": {"calib": [0, 1, 2], "holdout": [2, 3, 4]},
        "message_tag": "VAL-CONF-LEAK-001",
        "via_make_report": True,
    }


def check_coverage_kind_frozen():
    """coverage_kind must refuse guaranteed/exact."""
    bad = False
    try:
        SplitConformalReport(
            q=1.0,
            alpha=0.1,
            n_calib=3,
            y_hat=0.0,
            interval=(-1.0, 1.0),
            coverage_kind="guaranteed",
            calib_indices=(0,),
            holdout_indices=(1,),
            assumptions=(),
        )
    except ValueError:
        bad = True
    require(bad, "must reject coverage_kind='guaranteed'")

    bad2 = False
    try:
        SplitConformalReport(
            q=1.0,
            alpha=0.1,
            n_calib=3,
            y_hat=0.0,
            interval=(-1.0, 1.0),
            coverage_kind="exact",
            calib_indices=(0,),
            holdout_indices=(1,),
            assumptions=(),
        )
    except ValueError:
        bad2 = True
    require(bad2, "must reject coverage_kind='exact'")

    return {
        "rejected_guaranteed": True,
        "rejected_exact": True,
        "canonical": COVERAGE_MARGINAL_EXCHANGEABLE,
    }


def check_review_e4_exact_alpha():
    """Followup-Review-Fix E4 (SCF_REVIEW_J_SERIES_6b3a331): n = 9, residuals 1..9.

    Hand derivation: decimal alpha = 7/10 -> k = ceil(10 * 3/10) = 3 -> q = 3.
    Float 0.7 is the binary value 0.69999999999999995559..., so
    1 - alpha = 0.30000000000000004440... and k = ceil(3.0000000000000004...) = 4.
    Both are exact statements about their inputs; the float one is conservative
    here, which is not a general statement about all floats.
    """
    from fractions import Fraction

    res = list(range(1, 10))
    require(Fraction(0.7) < Fraction(7, 10), "the float 0.7 lies below 7/10")
    near(calibrate_split_conformal(res, 0.7), 4.0)
    near(calibrate_split_conformal(res, Fraction(7, 10)), 3.0)
    near(calibrate_split_conformal(res, "0.7"), 3.0)
    near(calibrate_split_conformal(res, " 7/10 "), 3.0)
    for bad in ("seven", True, float("nan"), "1", Fraction(0)):
        try:
            calibrate_split_conformal(res, bad)
        except ScopeViolationError:
            continue
        raise AssertionError(f"alpha {bad!r} must be refused")
    # Followup-Review F2 (SCF_FOLLOWUP_REVIEW_637bc1c): float results are NOT
    # generally unchanged vs the old float pipeline. Fraction(0.3) < 3/10 ->
    # 10 (1 - alpha) > 7 -> rank 8 (old float rounding gave 7); decimal "0.3" -> 7.
    near(calibrate_split_conformal(range(1, 10), 0.3), 8.0)
    near(calibrate_split_conformal(range(1, 10), "0.3"), 7.0)
    near(calibrate_split_conformal(range(1, 20), 0.15), 18.0)
    near(calibrate_split_conformal(range(1, 20), "0.15"), 17.0)
    # opposite direction: Fraction(0.44) > 44/100, exact 25 * (1 - alpha) < 14, so
    # rank 14 (old float product rounded above 14 -> 15, over-conservative);
    # 14 still satisfies k >= (n + 1)(1 - alpha) for the given binary value.
    require(Fraction(0.44) > Fraction(44, 100), "binary 0.44 lies above 44/100")
    near(calibrate_split_conformal(range(1, 25), 0.44), 14.0)
    near(calibrate_split_conformal(range(1, 25), "0.44"), 14.0)
    require(14 >= 25 * (1 - Fraction(0.44)) > 13, "rank 14 is the minimal valid rank for the binary value")
    # whole-real-line case stays legitimate: n = 1, alpha = 1/4 -> k = ceil(2 * 3/4) = 2 = n + 1
    require(math.isinf(calibrate_split_conformal([5.0], Fraction(1, 4))), "k = n + 1 gives +inf (whole line)")
    return {"float_0_7_q": 4.0, "decimal_7_10_q": 3.0}


CHECKS = [
    ("example_a_q3_interval_7_13", check_example_a),
    ("review_e4_exact_alpha", check_review_e4_exact_alpha),
    ("example_b_q4_interval_6_14", check_example_b),
    ("VAL-CONF-LEAK-001", check_val_conf_leak_001),
    ("coverage_kind_marginal_exchangeable", check_coverage_kind_frozen),
]


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument(
        "--json-out",
        type=Path,
        default=Path(__file__).with_name("verify_conformal_prediction_core_results.json"),
    )
    args = p.parse_args(argv)

    report = {
        "milestone": "M13 Split Conformal Prediction",
        "timestamp": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "checks": {},
        "source_doi": "10.1080/01621459.2017.1307116",
        "coverage_kind": COVERAGE_MARGINAL_EXCHANGEABLE,
        "disclaimer": (
            "Coverage is marginal under exchangeability — NOT guaranteed/exact/"
            "conditional. Finite-sample +1/ceiling order statistic required; "
            "naive empirical quantile can undercover (Lei et al. 2018)."
        ),
        "untouched": [
            "src/scoped_correspondence/validation/core.py",
            "FORMALISM.md",
            "Cygnus data application",
            "weighted/adaptive conformal",
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
