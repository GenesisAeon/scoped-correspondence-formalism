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
    require(interval["flat_in_scanned_range"] is True, "flat ON THIS SCAN is exactly what was observed")
    # Corrected 2026-09-23 (Astra, SCF_Check_2cc4b5b.md): likelihood_interval
    # itself NEVER asserts established_unbounded=True from grid data alone
    # (see its docstring) -- a flat scan does not prove global unboundedness
    # (Astra's own max(|theta|-1,0)**2 counterexample is flat on a scan yet
    # globally BOUNDED). This model's non-identifiability is instead
    # established STRUCTURALLY, independent of any particular scan: for
    # theta1*theta2=6, theta2=6/theta1 makes chi2 EXACTLY zero for every
    # theta1 != 0, an algebraic fact, not a scan artifact.
    require(interval["established_unbounded"] is False, "likelihood_interval alone must never claim this")
    for t1 in fixed:
        require(t1 != 0.0, "test construction assumes theta1 != 0")
        near((t1 * (6.0 / t1) - 6.0) ** 2, 0.0, atol=1e-12)
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
            "flat_in_scanned_range": interval["flat_in_scanned_range"],
            "established_unbounded": interval["established_unbounded"],
            "unbounded_reason": interval["unbounded_reason"],
            "lower": interval["lower"],
            "upper": interval["upper"],
            "chi2_star": interval["chi2_star"],
            "threshold": interval["threshold"],
        },
        "structural_non_identifiability_check": "theta2=6/theta1 gives chi2=0 exactly for every scanned theta1 -- an algebraic fact, not a scan artifact",
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
    require(interval["flat_in_scanned_range"] is False, "a curved, bounded profile is not flat_in_scanned_range")
    require(interval["established_unbounded"] is False, "a bounded interval cannot be established_unbounded")
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


def check_open_at_grid_boundary_not_established():
    """Astra's exact adversarial example (SCF_Review_3e8dce3.md finding 4,
    SCF_Followup_1231f64.md): chi2=theta^2, threshold=1, scan only at
    {-0.5, 0, 0.5}. The TRUE global interval at this threshold is exactly
    [-1, 1] -- the narrow scan cannot see that. The API must still report
    ``unbounded=True`` (no finite endpoint was found WITHIN this scan,
    unchanged for backward compatibility) but must NOT claim
    ``established_unbounded=True`` -- that would assert a positive finding
    of non-identifiability that this narrow scan never established.
    Classification itself must be "identifiable" (curved), not "flat".
    """

    def chi2(theta):
        return float(theta[0]) ** 2

    fixed = [-0.5, 0.0, 0.5]
    profile = profile_parameter(chi2, 0, [0.0], fixed)
    classification = classify_identifiability(profile, atol=1e-8)
    require(classification == "identifiable", f"expected identifiable (curved), got {classification!r}")

    interval = likelihood_interval(profile, threshold=1.0)
    require(interval["unbounded"] is True, "no finite endpoint found within this narrow scan")
    require(interval["bounded"] is False, "must not be bounded")
    require(interval["unbounded_reason"] == "open_at_grid_boundary", f"reason={interval.get('unbounded_reason')!r}")
    require(interval["flat_in_scanned_range"] is False, "this profile is curved (identifiable), not flat")
    require(
        interval["established_unbounded"] is False,
        "open_at_grid_boundary must NOT simultaneously assert an established finding of unboundedness",
    )

    return {
        "chi2": "theta^2",
        "fixed_values": fixed,
        "true_global_interval_at_threshold_1": [-1.0, 1.0],
        "classification": classification,
        "interval": {
            "bounded": interval["bounded"],
            "unbounded": interval["unbounded"],
            "flat_in_scanned_range": interval["flat_in_scanned_range"],
            "established_unbounded": interval["established_unbounded"],
            "unbounded_reason": interval["unbounded_reason"],
        },
    }


def check_flat_in_scanned_range_is_not_global_unboundedness():
    """Astra's own counterexamples (SCF_Check_2cc4b5b.md): a profile that is
    exactly (or numerically) flat ON A FINITE SCAN can still have a
    perfectly BOUNDED true confidence set once the function is evaluated
    beyond that scan -- "flat_in_scanned_range" must never be conflated
    with "established_unbounded". Both counterexamples independently
    executed here, not just asserted.
    """
    # (a) chi2(theta) = max(|theta|-1, 0)^2: exactly flat (zero) on [-1,1],
    # but the TRUE confidence set at threshold=1 is the BOUNDED [-2, 2]
    # (chi2(+-2) = 1 exactly; chi2 grows immediately beyond +-1 outside the scan).
    def chi2_capped(theta: float) -> float:
        return max(abs(theta) - 1.0, 0.0) ** 2

    fixed_a = [-1.0, -0.5, 0.0, 0.5, 1.0]
    profile_a = [(f, chi2_capped(f)) for f in fixed_a]
    for _, y in profile_a:
        near(y, 0.0, atol=1e-15)
    classification_a = classify_identifiability(profile_a, atol=1e-8)
    require(classification_a == "flat", f"expected flat on this scan, got {classification_a!r}")
    interval_a = likelihood_interval(profile_a, threshold=1.0)
    require(interval_a["flat_in_scanned_range"] is True, "this scan IS exactly flat")
    require(interval_a["established_unbounded"] is False, "must not claim global unboundedness")
    # Independent evidence of the TRUE, bounded global set (not from the API):
    near(chi2_capped(2.0), 1.0, atol=1e-12)
    near(chi2_capped(-2.0), 1.0, atol=1e-12)
    require(chi2_capped(3.0) > 1.0, "chi2 exceeds threshold beyond the true bound at theta=3")
    true_global_set_a = [-2.0, 2.0]

    # (b) chi2(theta) = theta^4 scanned narrowly at [-0.1, 0, 0.1]: variance
    # ~2.2e-9 is below the default atol=1e-8, so also classified "flat" --
    # yet the true confidence set at threshold=1 is [-1, 1].
    def chi2_quartic(theta: float) -> float:
        return theta ** 4

    fixed_b = [-0.1, 0.0, 0.1]
    profile_b = [(f, chi2_quartic(f)) for f in fixed_b]
    variance_b = sum((y - sum(v for _, v in profile_b) / 3) ** 2 for _, y in profile_b) / 3
    require(variance_b < 1e-8, f"expected this narrow scan to trigger the flat classification; var={variance_b!r}")
    classification_b = classify_identifiability(profile_b, atol=1e-8)
    require(classification_b == "flat", f"expected flat on this narrow scan, got {classification_b!r}")
    interval_b = likelihood_interval(profile_b, threshold=1.0)
    require(interval_b["flat_in_scanned_range"] is True, "this narrow scan IS classified flat")
    require(interval_b["established_unbounded"] is False, "must not claim global unboundedness")
    near(chi2_quartic(1.0), 1.0, atol=1e-12)
    near(chi2_quartic(-1.0), 1.0, atol=1e-12)
    require(chi2_quartic(1.5) > 1.0, "chi2 exceeds threshold beyond the true bound at theta=1.5")
    true_global_set_b = [-1.0, 1.0]

    return {
        "capped_quadratic": {
            "chi2": "max(|theta|-1,0)^2",
            "fixed_values": fixed_a,
            "classification": classification_a,
            "flat_in_scanned_range": interval_a["flat_in_scanned_range"],
            "established_unbounded": interval_a["established_unbounded"],
            "true_global_confidence_set": true_global_set_a,
        },
        "narrow_quartic": {
            "chi2": "theta^4",
            "fixed_values": fixed_b,
            "variance": variance_b,
            "classification": classification_b,
            "flat_in_scanned_range": interval_b["flat_in_scanned_range"],
            "established_unbounded": interval_b["established_unbounded"],
            "true_global_confidence_set": true_global_set_b,
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
        ("open_at_grid_boundary_not_established", check_open_at_grid_boundary_not_established),
        ("flat_in_scanned_range_is_not_global_unboundedness", check_flat_in_scanned_range_is_not_global_unboundedness),
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
