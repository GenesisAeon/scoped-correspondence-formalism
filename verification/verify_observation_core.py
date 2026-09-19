#!/usr/bin/env python3
"""Equivalence / formula checks for Observation core (Milestone 2).

Matches legacy verify_formalism.py checks:
  - p03_information_channel
  - c06_information_window

Plus Shannon–Hartley K_info and ScopeViolationError domain tests.
Stdlib + NumPy. JSON {count, passed, failed, report}; numbers from this run.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import platform
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from scoped_correspondence import (  # noqa: E402
    ScopeViolationError,
    channel_capacity,
    realized_rate,
    retention,
)
from scoped_correspondence.legacy import (  # noqa: E402
    information_retention_R,
    realized_eta,
    shannon_hartley_K,
)


def require(ok, msg):
    if not bool(ok):
        raise AssertionError(msg)


def near(a, b, atol=1e-12, rtol=1e-12):
    if not math.isclose(float(a), float(b), rel_tol=rtol, abs_tol=atol):
        raise AssertionError(f"{a!r} != {b!r}")


def entropy_binary(p: float) -> float:
    if not 0 <= p <= 1:
        raise ValueError("p outside [0,1]")
    return -sum(v * math.log2(v) for v in (p, 1 - p) if v)


def load_formalism_evidence(name: str):
    path = ROOT / "verification" / "verification_results.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    for c in data["checks"]:
        if c.get("name") == name:
            require(c["status"] == "passed", f"legacy {name} not passed")
            return c["evidence"]
    raise AssertionError(f"legacy evidence {name} missing")


def mig_obs_p03_information_channel():
    """Reproduce p03 via retention + realized_rate; exact match to legacy JSON."""
    expected = load_formalism_evidence("p03_information_channel")
    q, r, nu = 0.1, 0.2, 100.0
    q_total = q + r - 2 * q * r
    capacity = nu * (1 - entropy_binary(q))
    info_rate = nu * (1 - entropy_binary(q_total))
    eta = realized_rate(info_rate, capacity, rate_unit="bit/s", capacity_unit="bit/s")
    # R_info for binary source through the cascade: I(X;Z)/H(X)
    # Uniform binary: H(X)=1; I(X;Z)=1-H(q_total) bits per use -> rate form below.
    h_x = 1.0  # bit per use, uniform binary
    i_per_use = 1.0 - entropy_binary(q_total)
    r_info = retention(i_per_use, h_x, discrete=True)
    require(0 <= eta <= 1, "eta in [0,1]")
    near((info_rate * 10) / (capacity * 10), eta)
    require(capacity > info_rate > 0, "nontrivial degradation")
    near(capacity, expected["capacity_bits_per_second"])
    near(info_rate, expected["receiver_information_rate"])
    near(eta, expected["eta_info"])
    # legacy adapter parity
    near(realized_eta(info_rate, capacity, rate_unit="bit/s", capacity_unit="bit/s"), eta)
    near(information_retention_R(i_per_use, h_x), r_info)
    return {
        "channel": "memoryless binary symmetric",
        "capacity_bits_per_second": capacity,
        "receiver_information_rate": info_rate,
        "eta_info": eta,
        "R_info_per_use": r_info,
        "legacy_id": "p03_information_channel",
        "legacy_alias": "VER-OBS-p03_information_channel",
    }


def mig_obs_c06_information_window():
    """c06: raw I/C depends on window; rate/capacity is dimensionless & invariant."""
    expected = load_formalism_evidence("c06_information_window")
    # Legacy: values = [100*t/1000 for t in (1,10)]  -> absolute I/C (seconds)
    #          rates  = [100*t/(1000*t) for t in (1,10)] -> dimensionless
    raw_seconds = [100 * t / 1000 for t in (1, 10)]
    rate = 100.0  # bit/time
    capacity = 1000.0  # bit/time
    etas = [
        realized_rate(rate, capacity, rate_unit="bit/time", capacity_unit="bit/time")
        for _ in (1, 10)
    ]
    require(raw_seconds[0] != raw_seconds[1], "raw I/C should depend on window")
    near(etas[0], etas[1])
    near(raw_seconds[0], expected["raw_seconds"][0])
    near(raw_seconds[1], expected["raw_seconds"][1])
    near(etas[0], expected["dimensionless_fractions"][0])
    near(etas[1], expected["dimensionless_fractions"][1])
    # Absolute bit / capacity-rate must be rejected (would be a time).
    raised = False
    try:
        realized_rate(100.0, 1000.0, rate_unit="bit", capacity_unit="bit/time")
    except ScopeViolationError:
        raised = True
    require(raised, "absolute bit amount must raise ScopeViolationError")
    return {
        "raw_seconds": raw_seconds,
        "dimensionless_fractions": etas,
        "legacy_id": "c06_information_window",
        "legacy_alias": "VER-OBS-c06_information_window",
        "scope_violation_on_absolute_bits": True,
    }


def mig_obs_shannon_hartley_and_scope():
    """Shannon–Hartley K_info + retention domain ScopeViolationError."""
    k = channel_capacity(bandwidth=3000.0, snr=10.0 ** (30 / 10))  # 30 dB -> SNR=1000
    near(k, 3000.0 * math.log2(1.0 + 1000.0))
    near(shannon_hartley_K(1.0, 1.0), 1.0)  # log2(2)=1
    # Scope: continuous / bad H
    for kwargs in (
        dict(mutual_information=0.5, entropy=1.0, discrete=False),
        dict(mutual_information=0.5, entropy=0.0, discrete=True),
        dict(mutual_information=0.5, entropy=math.inf, discrete=True),
    ):
        try:
            retention(**kwargs)
            raise AssertionError(f"expected ScopeViolationError for {kwargs}")
        except ScopeViolationError:
            pass
    # capacity <= 0
    try:
        realized_rate(1.0, 0.0)
        raise AssertionError("expected ScopeViolationError for capacity 0")
    except ScopeViolationError:
        pass
    return {
        "K_info_B3000_SNR1000": k,
        "K_info_B1_SNR1": 1.0,
        "scope_violations_checked": 4,
        "formalism_rows": ["K_info", "R_info", "eta_info"],
    }


def mig_obs_audit_input_guards():
    """Audit findings: retention(nan,H) and realized_rate(rate>capacity)
    must raise ScopeViolationError instead of silently returning a number.

    retention(nan, 1.0) previously returned 1.0: `nan < -1e-15` is False,
    `r=nan` then fails BOTH bounds of `r<-1e-12 or r>1+1e-12` (also False
    for NaN), and `max(0.0, min(1.0, nan))` returns 1.0 because Python's
    min/max never replace their first argument on a NaN comparison.

    realized_rate(2.0, 1.0) previously returned 2.0 (eta_info=2): only a
    negative-eta check existed, no upper bound, even though K_info is
    defined as the maximum achievable rate (eta_info > 1 is a contradiction
    of that definition, not a valid over-100% reading).
    """
    raised_nan = False
    try:
        retention(float("nan"), 1.0)
    except ScopeViolationError:
        raised_nan = True
    require(raised_nan, "retention(nan, 1.0) must raise ScopeViolationError")

    raised_over_capacity = False
    try:
        realized_rate(2.0, 1.0)
    except ScopeViolationError:
        raised_over_capacity = True
    require(raised_over_capacity, "realized_rate(2.0, 1.0) (rate>capacity) must raise")

    # Legitimate eta_info==1.0 boundary case must still succeed.
    near(realized_rate(1.0, 1.0), 1.0)

    return {
        "retention_nan_raises": raised_nan,
        "realized_rate_over_capacity_raises": raised_over_capacity,
        "realized_rate_boundary_eta_1_ok": True,
    }


CHECKS = [
    ("MIG-OBS-p03_information_channel", mig_obs_p03_information_channel),
    ("MIG-OBS-c06_information_window", mig_obs_c06_information_window),
    ("MIG-OBS-shannon_hartley_and_scope", mig_obs_shannon_hartley_and_scope),
    ("audit_input_guards", mig_obs_audit_input_guards),
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).with_name("verify_observation_core_results.json"),
    )
    args = parser.parse_args()
    results = []
    for name, fn in CHECKS:
        try:
            evidence = fn()
            results.append({"id": name, "status": "passed", "evidence": evidence})
        except Exception as exc:
            results.append(
                {"id": name, "status": "failed", "error": f"{type(exc).__name__}: {exc}"}
            )
    passed = sum(r["status"] == "passed" for r in results)
    failed = [r["id"] for r in results if r["status"] != "passed"]
    report = {
        "milestone": "M2_observation_core",
        "kind": "MIG equivalence (legacy verify_formalism vs Observation API)",
        "generated_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "python": platform.python_version(),
        "numpy": np.__version__,
        "count": len(results),
        "passed": passed,
        "failed": len(failed),
        "empirical_validation": False,
        "checks": results,
    }
    args.output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    summary = {
        "count": report["count"],
        "passed": report["passed"],
        "failed": failed,
        "report": str(args.output.resolve()),
    }
    print(json.dumps(summary, ensure_ascii=False))
    raise SystemExit(0 if passed == len(results) else 1)


if __name__ == "__main__":
    main()
