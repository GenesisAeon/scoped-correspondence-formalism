#!/usr/bin/env python3
"""Dynamic value of information (INTEGRATED_EXTENSION_ROADMAP.md Paket C6).

Checks:

  1. Hand-verified control case: p=0.1, c=0.2, horizon 2, b0=0.5. Never
     measuring gives 1.0; always measuring gives 1.6; measuring once then
     exploiting persistence gives 1.7. The Bellman optimum V_2(0.5) is
     exactly 1.7, and the optimal FIRST action is "measure".
  2. Message aging: optimal hit rate for X_d after a perfect observation of
     X_0, p=0.1: d=1 -> 0.9, d=2 -> 0.82, d=10 -> 0.5536870912.
  3. iterated_belief's closed form matches direct repeated application of
     belief_transition, for several (b0, p, d).
  4. Free-option property: bellman_value(h,b,p,c) >= value_never_measure(h,b,p)
     for every tested (h,b,p,c) with c>=0 -- an optional, priced observation
     can never make the optimum worse.
  5. Symmetric channel decoders: q=0.3 (channel better than random) gives
     optimal_accuracy==naive_accuracy==0.7; q=0.7 (channel WORSE than
     random) gives optimal_accuracy=0.7 but naive_accuracy=0.3 -- the naive
     decoder is actively harmed by failing to invert an anti-correlated
     channel, the optimal decoder is not.
  6. ScopeViolationError guards (out-of-range p/b/q, negative c/horizon/d).
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
from scoped_correspondence.validation.sequential_information_pilot import (  # noqa: E402
    belief_transition,
    iterated_belief,
    bellman_value,
    value_never_measure,
    optimal_hit_rate_after_perfect_observation,
    symmetric_channel_decoders,
)


def require(ok, msg):
    if not bool(ok):
        raise AssertionError(msg)


def check_control_case_v2_0_5():
    p, c = 0.1, 0.2
    never = value_never_measure(2, 0.5, p)
    always_manual = 2 * (1.0 - c)
    measure_once_manual = (1.0 - c) + max(belief_transition(1.0, p), 1.0 - belief_transition(1.0, p))
    require(abs(never - 1.0) < 1e-12, f"never-measure value should be 1.0, got {never!r}")
    require(abs(always_manual - 1.6) < 1e-12, f"always-measure value should be 1.6, got {always_manual!r}")
    require(abs(measure_once_manual - 1.7) < 1e-9, f"measure-once value should be 1.7, got {measure_once_manual!r}")

    result = bellman_value(2, 0.5, p, c)
    require(abs(result.value - 1.7) < 1e-9, f"V_2(0.5) should be exactly 1.7, got {result.value!r}")
    require(result.action == "measure", f"the optimal first action at b=0.5,h=2 should be 'measure', got {result.action!r}")
    return {"never": never, "always": always_manual, "measure_once": measure_once_manual, "bellman": result.value, "action": result.action}


def check_message_aging_control_values():
    p = 0.1
    expected = {1: 0.9, 2: 0.82, 10: 0.5536870912}
    got = {}
    for d, exp in expected.items():
        rate = optimal_hit_rate_after_perfect_observation(p, d)
        require(abs(rate - exp) < 1e-9, f"d={d}: expected hit rate {exp}, got {rate!r}")
        got[d] = rate
    return got


def check_iterated_belief_matches_direct_iteration():
    for b0 in (0.0, 0.3, 0.5, 0.8, 1.0):
        for p in (0.0, 0.1, 0.3, 0.5, 0.9):
            for d in (0, 1, 3, 7):
                b_direct = b0
                for _ in range(d):
                    b_direct = belief_transition(b_direct, p)
                b_closed = iterated_belief(b0, p, d)
                require(abs(b_direct - b_closed) < 1e-9,
                        f"b0={b0},p={p},d={d}: direct iteration ({b_direct!r}) != closed form ({b_closed!r})")
    return {"ok": True}


def check_free_option_property():
    trials = 0
    for h in (0, 1, 2, 3, 4):
        for b in (0.0, 0.2, 0.5, 0.7, 1.0):
            for p in (0.0, 0.1, 0.3, 0.5, 0.9):
                for c in (0.0, 0.05, 0.2, 0.5, 1.0, 2.0):
                    trials += 1
                    v_opt = bellman_value(h, b, p, c).value
                    v_never = value_never_measure(h, b, p)
                    require(v_opt >= v_never - 1e-9,
                            f"h={h},b={b},p={p},c={c}: optional measurement gave a WORSE optimum "
                            f"({v_opt!r}) than never having the option ({v_never!r})")
    return {"trials": trials}


def check_symmetric_channel_decoders():
    r_good = symmetric_channel_decoders(0.3)
    require(abs(r_good.optimal_accuracy - 0.7) < 1e-12, f"q=0.3 optimal accuracy should be 0.7, got {r_good.optimal_accuracy!r}")
    require(abs(r_good.naive_accuracy - 0.7) < 1e-12, f"q=0.3 naive accuracy should also be 0.7, got {r_good.naive_accuracy!r}")

    r_bad = symmetric_channel_decoders(0.7)
    require(abs(r_bad.optimal_accuracy - 0.7) < 1e-12, f"q=0.7 optimal accuracy should be 0.7 (invert), got {r_bad.optimal_accuracy!r}")
    require(abs(r_bad.naive_accuracy - 0.3) < 1e-12, f"q=0.7 naive accuracy should be 0.3 (never inverts), got {r_bad.naive_accuracy!r}")
    require(r_bad.optimal_accuracy > r_bad.naive_accuracy, "for an anti-correlated channel, the optimal decoder must beat the naive one")
    return {"q_0.3": r_good.__dict__, "q_0.7": r_bad.__dict__}


def check_scope_violation_guards():
    for fn, args in [
        (belief_transition, (0.5, 1.5)),
        (belief_transition, (1.5, 0.5)),
        (bellman_value, (-1, 0.5, 0.1, 0.2)),
        (bellman_value, (2, 0.5, 0.1, -0.1)),
        (iterated_belief, (0.5, 0.1, -1)),
        (optimal_hit_rate_after_perfect_observation, (0.1, -1)),
        (symmetric_channel_decoders, (1.5,)),
    ]:
        try:
            fn(*args)
            raise AssertionError(f"{fn.__name__}{args!r} should have raised ScopeViolationError")
        except ScopeViolationError:
            pass
    return {"raised": 7}


CHECKS = [
    ("control_case_v2_0_5", check_control_case_v2_0_5),
    ("message_aging_control_values", check_message_aging_control_values),
    ("iterated_belief_matches_direct_iteration", check_iterated_belief_matches_direct_iteration),
    ("free_option_property", check_free_option_property),
    ("symmetric_channel_decoders", check_symmetric_channel_decoders),
    ("scope_violation_guards", check_scope_violation_guards),
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json-out", type=Path, default=Path(__file__).with_name("verify_sequential_information_pilot_results.json"))
    args = parser.parse_args()

    report = {
        "package": "INTEGRATED_EXTENSION_ROADMAP.md Paket C6 (dynamic value of information)",
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
