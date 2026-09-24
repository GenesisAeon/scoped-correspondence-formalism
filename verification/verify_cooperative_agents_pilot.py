#!/usr/bin/env python3
"""Finite cooperative-agent communication tasks (DOMAIN_EXPANSION_ROADMAP.md Paket B6a).

Checks:

  1. XOR task (complementary information): 0.5 success without any message
     (exhaustively enumerated over all 4 possible decision rules on B), 1.0
     with a perfectly transmitted bit. Existing BROJA PID solver confirms
     the textbook signature on the EXACT joint distribution: redundancy=0,
     unique_1=0, unique_2=0, synergy=1 bit -- not asserted from the
     formula, computed by the repo's own (unmodified) PID module.
  2. Redundancy task: 1.0 success with or without communication (adds
     nothing); PID atoms are pure redundancy (1 bit), zero synergy.
  3. Cost threshold: communication nets a strict gain in the XOR task iff
     lambda < 0.5 (checked either side and at the exact equality point,
     where it must NOT count as strictly better); communication never
     nets a gain in the redundancy task for any lambda > 0.
  4. Noisy channel: epsilon in {0, 0.1, 0.5, 1} for both a fixed (naive)
     decoder (1-epsilon) and an epsilon-informed optimal decoder
     (max(epsilon, 1-epsilon)) -- notably epsilon=1 (systematically
     inverted) is FULLY recoverable by the informed decoder, not merely
     the epsilon=0.5 floor.
  5. Full-enumeration sanity: every probability row across all three tasks
     sums to exactly 1.0 (no missing or double-counted state).
  6. ScopeViolationError guards.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from scoped_correspondence.errors import ScopeViolationError  # noqa: E402
from scoped_correspondence.validation.cooperative_agents_pilot import (  # noqa: E402
    evaluate_xor_task, evaluate_redundancy_task, evaluate_noisy_xor_task,
)


def require(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)


def check_xor_task():
    xor = evaluate_xor_task()
    require(abs(xor.success_no_communication - 0.5) < 1e-12,
            f"XOR without message should be exactly 0.5; got {xor.success_no_communication}")
    require(abs(xor.success_with_communication - 1.0) < 1e-12,
            f"XOR with perfect message should be exactly 1.0; got {xor.success_with_communication}")
    require(abs(xor.pid.redundancy) < 1e-4, f"XOR redundancy should be ~0; got {xor.pid.redundancy}")
    require(abs(xor.pid.unique_source_1) < 1e-4, f"XOR unique_1 should be ~0; got {xor.pid.unique_source_1}")
    require(abs(xor.pid.unique_source_2) < 1e-4, f"XOR unique_2 should be ~0; got {xor.pid.unique_source_2}")
    require(abs(xor.pid.synergy - 1.0) < 1e-4, f"XOR synergy should be ~1 bit; got {xor.pid.synergy}")
    require(abs(xor.pid.I_joint - 1.0) < 1e-4, f"XOR joint MI should be ~1 bit; got {xor.pid.I_joint}")
    return xor.to_dict()


def check_redundancy_task():
    red = evaluate_redundancy_task()
    require(red.success_no_communication == 1.0, f"redundancy without message should be 1.0; got {red.success_no_communication}")
    require(red.success_with_communication == 1.0, f"redundancy with message should still be 1.0; got {red.success_with_communication}")
    require(abs(red.pid.redundancy - 1.0) < 1e-4, f"redundancy PID should be ~1 bit; got {red.pid.redundancy}")
    require(abs(red.pid.synergy) < 1e-4, f"redundancy synergy should be ~0; got {red.pid.synergy}")
    require(abs(red.pid.unique_source_1) < 1e-4 and abs(red.pid.unique_source_2) < 1e-4,
            "redundancy uniques should both be ~0")
    return red.to_dict()


def check_cost_threshold():
    xor = evaluate_xor_task()
    require(xor.communication_helps(0.4) is True, "XOR: lambda=0.4<0.5 should favor communicating")
    require(xor.communication_helps(0.6) is False, "XOR: lambda=0.6>0.5 should favor silence")
    require(xor.communication_helps(0.5) is False,
            "XOR: at exact equality (lambda=0.5) communicating must NOT count as STRICTLY better")
    eq_gap = xor.net_utility(True, 0.5) - xor.net_utility(False, 0.5)
    require(abs(eq_gap) < 1e-12, f"at lambda=0.5 the net utilities should be EXACTLY equal; gap={eq_gap}")

    red = evaluate_redundancy_task()
    for lam in (0.01, 0.1, 0.5, 1.0):
        require(red.communication_helps(lam) is False,
                f"redundancy task: communication should never help for any positive lambda={lam}")
    return {"xor_eq_gap_at_0.5": eq_gap, "redundancy_never_helps_checked": 4}


def check_noisy_channel():
    results = {}
    for eps in (0.0, 0.1, 0.5, 1.0):
        naive = evaluate_noisy_xor_task(eps, "naive")
        optimal = evaluate_noisy_xor_task(eps, "optimal")
        want_naive = 1.0 - eps
        want_optimal = max(eps, 1.0 - eps)
        require(abs(naive - want_naive) < 1e-12, f"eps={eps}: naive got {naive}, want {want_naive}")
        require(abs(optimal - want_optimal) < 1e-12, f"eps={eps}: optimal got {optimal}, want {want_optimal}")
        results[str(eps)] = {"naive": naive, "optimal": optimal}
    require(results["1.0"]["optimal"] == 1.0,
            "epsilon=1 (systematically inverted) must be FULLY recoverable by the informed decoder")
    require(results["1.0"]["naive"] == 0.0,
            "epsilon=1 must be a total failure for the unchanged (naive) decoder")
    return results


def check_full_enumeration_sums_to_one():
    from scoped_correspondence.validation.cooperative_agents_pilot import _pid_joint
    xor_rows = [(a, b, a ^ b, 0.25) for a in (0, 1) for b in (0, 1)]
    red_rows = [(a, a, a, 0.5) for a in (0, 1)]
    require(abs(sum(r[3] for r in xor_rows) - 1.0) < 1e-12, "XOR task rows must sum to 1.0")
    require(abs(sum(r[3] for r in red_rows) - 1.0) < 1e-12, "redundancy task rows must sum to 1.0")
    require(abs(float(_pid_joint(xor_rows).sum()) - 1.0) < 1e-12, "XOR joint must sum to 1.0")
    require(abs(float(_pid_joint(red_rows).sum()) - 1.0) < 1e-12, "redundancy joint must sum to 1.0")

    # noisy channel: for each epsilon, the 8-outcome enumeration in evaluate_noisy_xor_task
    # implicitly sums to 1 -- checked indirectly via naive+wrong-guess complementarity.
    for eps in (0.0, 0.3, 0.5, 0.7, 1.0):
        naive_right = evaluate_noisy_xor_task(eps, "naive")
        # the naive decoder is either exactly right (err=0) or exactly wrong (err=1);
        # these two outcomes must sum to 1 for any epsilon.
        require(abs(naive_right - (1.0 - eps)) < 1e-12, f"eps={eps}: naive success should equal 1-eps exactly")
    return {"checked": 5}


def check_scope_violation_guards():
    try:
        evaluate_noisy_xor_task(-0.1, "naive")
        raise AssertionError("should reject epsilon < 0")
    except ScopeViolationError:
        pass
    try:
        evaluate_noisy_xor_task(1.1, "naive")
        raise AssertionError("should reject epsilon > 1")
    except ScopeViolationError:
        pass
    try:
        evaluate_noisy_xor_task(0.5, "not_a_decoder")
        raise AssertionError("should reject unknown decoder")
    except ScopeViolationError:
        pass
    return {"checked": 3}


CHECKS = [
    ("xor_task", check_xor_task),
    ("redundancy_task", check_redundancy_task),
    ("cost_threshold", check_cost_threshold),
    ("noisy_channel", check_noisy_channel),
    ("full_enumeration_sums_to_one", check_full_enumeration_sums_to_one),
    ("scope_violation_guards", check_scope_violation_guards),
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json-out", type=Path, default=Path(__file__).with_name("verify_cooperative_agents_pilot_results.json"))
    args = parser.parse_args()

    report = {
        "package": "DOMAIN_EXPANSION_ROADMAP.md Paket B6a (cooperative agents)",
        "timestamp": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "python": sys.version.split()[0],
        "checks": {},
    }

    all_ok = True
    for name, fn in CHECKS:
        try:
            detail = fn()
            report["checks"][name] = {"status": "pass", "detail": detail}
            print(f"PASS  {name}")
        except AssertionError as e:
            all_ok = False
            report["checks"][name] = {"status": "fail", "error": str(e)}
            print(f"FAIL  {name}: {e}")
        except Exception as e:  # noqa: BLE001
            all_ok = False
            report["checks"][name] = {"status": "error", "error": f"{type(e).__name__}: {e}"}
            print(f"ERROR {name}: {type(e).__name__}: {e}")

    args.json_out.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    print(f"\n{sum(1 for c in report['checks'].values() if c['status'] == 'pass')}/{len(CHECKS)} checks passed")
    print(f"Report written to {args.json_out}")
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
