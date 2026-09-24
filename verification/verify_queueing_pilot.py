#!/usr/bin/env python3
"""Queueing pilot: mean load vs. transient risk, kept explicitly separate
(DOMAIN_EXPANSION_ROADMAP.md Paket B2).

Checks:

  1. The combined report's two fields must not be conflated: a case with
     rho<1 (stable mean, deterministic fluid backlog reflects to exactly 0
     throughout) still carries a non-trivial stochastic hitting probability
     -- exactly Astra's point that a mean-load description says nothing
     about a genuine finite-horizon event risk.
  2. Both sub-models reproduce their own already-verified module functions
     exactly (this pilot adds no new math of its own, only composition).
  3. ScopeViolationError guard.
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
from scoped_correspondence.validation.queueing_pilot import run_queueing_pilot  # noqa: E402
from scoped_correspondence.dynamics.queueing import fluid_queue_piecewise  # noqa: E402
from scoped_correspondence.viability.first_passage_ctmc import queue_hitting_probability  # noqa: E402


def require(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)


def check_mean_safe_but_stochastic_risky():
    r = run_queueing_pilot(0, 5, 10.0, 0.5, 1.0)
    require(r.deterministic_boundary_crossed is False,
            "deterministic fluid model (rho<1, arrival<service) should never cross the boundary")
    require(r.deterministic_peak_backlog == 0.0, f"deterministic peak should be exactly 0; got {r.deterministic_peak_backlog}")
    require(r.stochastic_hitting_probability > 0.01,
            f"stochastic hitting probability should be clearly non-trivial; got {r.stochastic_hitting_probability}")
    return r.to_dict()


def check_pilot_matches_underlying_modules_exactly():
    r = run_queueing_pilot(1.0, 4.0, 6.0, 0.9, 1.0)
    traj = fluid_queue_piecewise(1.0, [0.0, 6.0], [0.9], [1.0])
    t_peak, peak = traj.peak()
    p = queue_hitting_probability(1, 4, 6.0, 0.9, 1.0)
    require(r.deterministic_peak_backlog == peak, "pilot's deterministic peak must match the underlying module exactly")
    require(r.deterministic_peak_time == t_peak, "pilot's deterministic peak time must match the underlying module exactly")
    require(r.stochastic_hitting_probability == p, "pilot's stochastic probability must match the underlying module exactly")
    return {"peak": peak, "t_peak": t_peak, "p": p}


def check_scope_violation_guard():
    try:
        run_queueing_pilot(0, 5, -1.0, 0.5, 1.0)
        raise AssertionError("should reject non-positive horizon")
    except ScopeViolationError:
        pass
    return {"checked": 1}


CHECKS = [
    ("mean_safe_but_stochastic_risky", check_mean_safe_but_stochastic_risky),
    ("pilot_matches_underlying_modules_exactly", check_pilot_matches_underlying_modules_exactly),
    ("scope_violation_guard", check_scope_violation_guard),
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json-out", type=Path, default=Path(__file__).with_name("verify_queueing_pilot_results.json"))
    args = parser.parse_args()

    report = {
        "package": "DOMAIN_EXPANSION_ROADMAP.md Paket B2 (queueing pilot composition)",
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
