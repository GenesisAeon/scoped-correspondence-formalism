#!/usr/bin/env python3
"""Distributed-delay downstream-buffer pilot (INTEGRATED_EXTENSION_ROADMAP.md
Paket C3, plan section 7's fixed pre-declared experiment) -- synthetic-only,
no network access needed.

Checks:

  1. The fixed experiment (n in {1,2,4,8}, tau=1, pulse u=5 on [0,0.2),
     horizon 5, R(0)=0.1, dR/dt=0.4-y(t)) finds a REAL first-passage event
     (R<=0) for every n, with the crossing time strictly increasing in n
     (more spread-out/concentrated-later delay chains postpone the breach).
  2. The root-finder's reported first-passage time is cross-checked by direct
     evaluation: R at that exact time is ~0 to high precision.
  3. Peak output and minimum buffer level do NOT rank catchments in the same
     order (plan section 7's explicit caveat) -- concretely, n=4 has a
     SMALLER output peak than n=1 but a WORSE (more negative) buffer minimum,
     checked as an explicit pair of inequalities, not asserted in the
     abstract.
  4. Mass-balance identity: total mass still in the delay stages at the
     horizon, plus the mass that has exited as output (integrated via an
     independent trapezoidal quadrature over the recorded trajectory), must
     equal the total pulse mass (u_pulse * pulse_duration = 1.0) for every n.
  5. ScopeViolationError guards (pulse longer than horizon).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from scoped_correspondence.errors import ScopeViolationError  # noqa: E402
from scoped_correspondence.validation.distributed_delay_pilot import run_fixed_experiment  # noqa: E402


def require(ok, msg):
    if not bool(ok):
        raise AssertionError(msg)


def check_first_passage_ordering():
    results = {n: run_fixed_experiment(n) for n in (1, 2, 4, 8)}
    for n, r in results.items():
        require(r.first_passage_time is not None, f"n={n}: expected a real first-passage event, got None")
    times = [results[n].first_passage_time for n in (1, 2, 4, 8)]
    require(times == sorted(times), f"first-passage time should strictly increase with n; got {times!r}")
    require(len(set(round(t, 6) for t in times)) == 4, "all four first-passage times should be distinct")
    return {n: r.first_passage_time for n, r in results.items()}


def check_first_passage_matches_R_zero():
    from scoped_correspondence.validation.distributed_delay_pilot import _combined_system
    from scoped_correspondence.dynamics.phase_type_delays import erlang_phase_type, propagate_linear_constant_input

    for n in (1, 2, 4, 8):
        r = run_fixed_experiment(n)
        pt = erlang_phase_type(n, 1.0)
        A = _combined_system(pt, inflow=0.4)
        t_star = r.first_passage_time
        if t_star <= 0.2:
            d = np.zeros(n + 1); d[:n] = 5.0 * pt.alpha; d[n] = 0.4
            x0 = np.zeros(n + 1); x0[n] = 0.1
            R_check = propagate_linear_constant_input(x0, A, d, t_star)[n]
        else:
            d1 = np.zeros(n + 1); d1[:n] = 5.0 * pt.alpha; d1[n] = 0.4
            x0 = np.zeros(n + 1); x0[n] = 0.1
            x_mid = propagate_linear_constant_input(x0, A, d1, 0.2)
            d2 = np.zeros(n + 1); d2[n] = 0.4
            R_check = propagate_linear_constant_input(x_mid, A, d2, t_star - 0.2)[n]
        require(abs(R_check) < 1e-8, f"n={n}: R at reported first_passage_time should be ~0, got {R_check!r}")
    return {"ok": True}


def check_peak_and_minimum_need_not_move_together():
    r1 = run_fixed_experiment(1)
    r4 = run_fixed_experiment(4)
    require(r4.output_peak_value < r1.output_peak_value,
            f"n=4's output peak ({r4.output_peak_value!r}) should be SMALLER than n=1's ({r1.output_peak_value!r})")
    require(r4.R_min_value < r1.R_min_value,
            f"n=4's buffer minimum ({r4.R_min_value!r}) should be WORSE (more negative) than n=1's ({r1.R_min_value!r}) "
            f"-- demonstrating peak and minimum-buffer rankings need not move together")
    return {
        "peak_n1": r1.output_peak_value, "peak_n4": r4.output_peak_value,
        "R_min_n1": r1.R_min_value, "R_min_n4": r4.R_min_value,
    }


def check_mass_balance():
    for n in (1, 2, 4, 8):
        r = run_fixed_experiment(n, n_samples_per_segment=4000)
        ts = np.array([p[0] for p in r.trajectory])
        ys = np.array([p[2] for p in r.trajectory])
        # Manual trapezoidal rule (np.trapz was removed in numpy 2.4; avoid depending
        # on either the old or the new `np.trapezoid` name).
        exited_mass = float(np.sum(0.5 * (ys[1:] + ys[:-1]) * np.diff(ts)))
        total_pulse_mass = 5.0 * 0.2
        balance = r.remaining_mass_at_horizon + exited_mass
        require(abs(balance - total_pulse_mass) < 1e-3,
                f"n={n}: remaining_mass ({r.remaining_mass_at_horizon!r}) + exited_mass "
                f"({exited_mass!r}) should equal total pulse mass {total_pulse_mass!r}; got {balance!r}")
    return {"ok": True}


def check_scope_violation_guards():
    try:
        run_fixed_experiment(2, pulse_duration=10.0, horizon=5.0)
        raise AssertionError("pulse longer than horizon should raise ScopeViolationError")
    except ScopeViolationError:
        pass
    return {"raised": 1}


CHECKS = [
    ("first_passage_ordering", check_first_passage_ordering),
    ("first_passage_matches_R_zero", check_first_passage_matches_R_zero),
    ("peak_and_minimum_need_not_move_together", check_peak_and_minimum_need_not_move_together),
    ("mass_balance", check_mass_balance),
    ("scope_violation_guards", check_scope_violation_guards),
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json-out", type=Path, default=Path(__file__).with_name("verify_distributed_delay_pilot_results.json"))
    args = parser.parse_args()

    report = {
        "package": "INTEGRATED_EXTENSION_ROADMAP.md Paket C3 (distributed-delay downstream-buffer pilot)",
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
