#!/usr/bin/env python3
"""Hand-checkable verification for Profile Likelihood (Milestone 20).

Checks (all numbers from this script run):
  1. Non-id product: chi2=(theta1*theta2-6)^2; profile theta1 in {1..5}
     → chi2_min≈0 all → classify "flat" → likelihood_interval unbounded
  2. Id control: chi2=(theta-3)^2; profile theta in {0..6}
     → "identifiable"; threshold=1 → finite interval [2, 4]
  3. Scope guards: empty fixed_values / bad index / multi-free raise
     ScopeViolationError
  4. SOURCE string contains Raue DOI 10.1093/bioinformatics/btp358

Stdlib + math only for the algebraic demos (no ODE / general NLP).
JSON {count, passed, failed, report}; numbers from this run.
Does not import or mutate identifiability.core.
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
from scoped_correspondence.identifiability.profile_likelihood import (  # noqa: E402
    SOURCE,
    classify_identifiability,
    likelihood_interval,
    profile_parameter,
)


def require(ok, msg):
    if not bool(ok):
        raise AssertionError(msg)


def near(a, b, atol=1e-8, rtol=1e-9):
    if not math.isclose(float(a), float(b), abs_tol=atol, rel_tol=rtol):
        raise AssertionError(f"{a!r} != {b!r} (atol={atol})")


def check_nonid_product_flat():
    """chi2=(t1*t2-6)^2; profile t1 in 1..5 → all chi2_min≈0 → flat, unbounded."""

    def chi2(theta):
        t1, t2 = float(theta[0]), float(theta[1])
        return (t1 * t2 - 6.0) ** 2

    fixed = [1.0, 2.0, 3.0, 4.0, 5.0]
    theta_init = [3.0, 2.0]
    profile = profile_parameter(chi2, 0, theta_init, fixed)
    require(len(profile) == 5, f"len={len(profile)}")
    chi2_mins = [y for _, y in profile]
    for v, y in profile:
        near(y, 0.0, atol=1e-6)
    classification = classify_identifiability(profile, atol=1e-8)
    require(classification == "flat", f"got {classification!r}")
    interval = likelihood_interval(profile, threshold=1.0)
    require(interval["unbounded"] is True, "must be unbounded")
    require(interval["bounded"] is False, "must not be bounded")
    require(
        interval["unbounded_reason"] == "flat_profile",
        f"reason={interval.get('unbounded_reason')!r}",
    )
    require(interval["lower"] is None and interval["upper"] is None, "ends None")
    require("10.1093/bioinformatics/btp358" in str(interval["source"]), "DOI")

    return {
        "chi2": "(theta1*theta2-6)^2",
        "fixed_values": fixed,
        "theta_init": theta_init,
        "profile": [[x, y] for x, y in profile],
        "chi2_mins": chi2_mins,
        "max_abs_chi2_min": max(abs(y) for y in chi2_mins),
        "classification": classification,
        "interval": {
            "bounded": interval["bounded"],
            "unbounded": interval["unbounded"],
            "unbounded_reason": interval["unbounded_reason"],
            "lower": interval["lower"],
            "upper": interval["upper"],
            "chi2_star": interval["chi2_star"],
            "threshold": interval["threshold"],
        },
    }


def check_id_quadratic_finite():
    """chi2=(theta-3)^2; profile 0..6 → identifiable; Delta=1 → [2,4]."""

    def chi2(theta):
        t = float(theta[0])
        return (t - 3.0) ** 2

    fixed = [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
    expected_chi2 = [(v - 3.0) ** 2 for v in fixed]
    profile = profile_parameter(chi2, 0, [3.0], fixed)
    require(len(profile) == 7, f"len={len(profile)}")
    for (v, y), ey in zip(profile, expected_chi2):
        near(v, v)  # noqa: identity — keep structure
        near(y, ey, atol=1e-12)

    classification = classify_identifiability(profile, atol=1e-8)
    require(classification == "identifiable", f"got {classification!r}")

    # Population variance of {9,4,1,0,1,4,9}
    ys = expected_chi2
    mean = sum(ys) / len(ys)
    var = sum((y - mean) ** 2 for y in ys) / len(ys)
    require(var > 1e-8, f"variance should be large; var={var}")

    threshold = 1.0
    interval = likelihood_interval(profile, threshold=threshold)
    require(interval["unbounded"] is False, "must be bounded")
    require(interval["bounded"] is True, "bounded True")
    near(interval["lower"], 2.0)
    near(interval["upper"], 4.0)
    near(interval["chi2_star"], 0.0)
    require(interval["values_in_set"] == [2.0, 3.0, 4.0], f"set={interval['values_in_set']}")
    require(interval["classification"] == "identifiable", "class in interval")

    return {
        "chi2": "(theta-3)^2",
        "fixed_values": fixed,
        "profile": [[x, y] for x, y in profile],
        "chi2_mins": [y for _, y in profile],
        "variance_chi2_min": var,
        "classification": classification,
        "threshold": threshold,
        "interval": {
            "bounded": interval["bounded"],
            "unbounded": interval["unbounded"],
            "lower": interval["lower"],
            "upper": interval["upper"],
            "chi2_star": interval["chi2_star"],
            "values_in_set": interval["values_in_set"],
        },
    }


def check_scope_guards():
    def chi2_2(theta):
        return (float(theta[0]) * float(theta[1]) - 6.0) ** 2

    def chi2_3(theta):
        return (float(theta[0]) + float(theta[1]) + float(theta[2])) ** 2

    raised = {}

    try:
        profile_parameter(chi2_2, 0, [1.0, 2.0], [])
        raised["empty_fixed"] = False
    except ScopeViolationError:
        raised["empty_fixed"] = True

    try:
        profile_parameter(chi2_2, 5, [1.0, 2.0], [1.0])
        raised["bad_index"] = False
    except ScopeViolationError:
        raised["bad_index"] = True

    try:
        # 3-D: fix index 0 → two free params → refused
        profile_parameter(chi2_3, 0, [1.0, 1.0, 1.0], [0.5])
        raised["multi_free"] = False
    except ScopeViolationError:
        raised["multi_free"] = True

    try:
        classify_identifiability([(1.0, 0.0)], atol=1e-8)
        raised["short_profile"] = False
    except ScopeViolationError:
        raised["short_profile"] = True

    require(all(raised.values()), f"scope guards: {raised}")
    return {"scope_guards": raised}


def check_source_doi():
    require("10.1093/bioinformatics/btp358" in SOURCE, f"SOURCE={SOURCE!r}")
    require("Raue" in SOURCE, "Raue in SOURCE")
    return {"source": SOURCE}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--json-out",
        type=Path,
        default=ROOT / "verification" / "verify_profile_likelihood_core_results.json",
    )
    args = parser.parse_args()

    checks = [
        ("nonid_product_flat", check_nonid_product_flat),
        ("id_quadratic_finite", check_id_quadratic_finite),
        ("scope_guards", check_scope_guards),
        ("source_doi", check_source_doi),
    ]
    report = []
    passed = 0
    failed = 0
    for name, fn in checks:
        try:
            evidence = fn()
            report.append({"name": name, "status": "passed", "evidence": evidence})
            passed += 1
            print(f"PASS  {name}")
        except Exception as exc:  # noqa: BLE001 — collect all
            report.append(
                {
                    "name": name,
                    "status": "failed",
                    "error": f"{type(exc).__name__}: {exc}",
                }
            )
            failed += 1
            print(f"FAIL  {name}: {type(exc).__name__}: {exc}")

    payload = {
        "milestone": 20,
        "title": "Profile Likelihood",
        "count": len(checks),
        "passed": passed,
        "failed": failed,
        "timestamp": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "platform": platform.platform(),
        "python": sys.version.split()[0],
        "source_doi": "10.1093/bioinformatics/btp358",
        "report": report,
    }
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {args.json_out}  passed={passed}/{len(checks)}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
