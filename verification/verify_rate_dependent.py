#!/usr/bin/env python3
"""Rate-dependent tracking vs. rate-induced tipping (Milestone 42).

NONSTATIONARY_ROADMAP.md package 3, response to
prompts/Answers/nicht_stationäre_Treiber/SCF_Nichtstationaere_Treiber_und_Kippen.md
(Astra, 2026-09-21) section 5.1: keeps frozen (quasi-static) stability
evaluation and genuine non-autonomous trajectory integration explicitly
separate, and reproduces the canonical rate-induced-tipping worked
example (dx/dt=(x-u)-(x-u)^3, u(t)=1+tanh(r*t)).

Checks (all numbers from this script run):
  1. frozen_equilibria_shifted_pitchfork(u) matches the hand-derived
     closed form (x=u unstable derivative +1; x=u+-1 stable derivative
     -2) at several u values -- confirming no frozen bifurcation exists
     anywhere along the driver's path.
  2. integrate_trajectory raises ScopeViolationError on t1<=t0.
  3. classify_tracking raises ScopeViolationError when the final state is
     not near any stable frozen equilibrium, and when no stable
     equilibrium is supplied at all.
  4. rate_induced_tipping_cubic_example(r=0.1) tracks the upper branch
     (switched=False); rate_induced_tipping_cubic_example(r=2.0) switches
     to the lower branch (switched=True) -- reproducing
     SCF_Nichtstationaere_Treiber_und_Kippen.md section 5.1's exact
     reported values (matched here to the reported precision).
  5. A slow-rate sweep (r from 0.05 to 5) confirms tracking fails only
     above some critical rate, not for every r -- i.e. this is genuinely
     a RATE effect (monotone in r for this model), not a coin flip.

Uses scipy.integrate.solve_ivp (already a project dependency). Does not
mutate dynamics/core.py, gspt.py, panarchy_cusp.py, or early_warning.py.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import platform
import sys
from pathlib import Path

import numpy as np
import scipy

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from scoped_correspondence.errors import ScopeViolationError  # noqa: E402
from scoped_correspondence.dynamics.rate_dependent import (  # noqa: E402
    SOURCE,
    STABLE,
    UNSTABLE,
    classify_tracking,
    frozen_equilibria_shifted_pitchfork,
    integrate_trajectory,
    rate_induced_tipping_cubic_example,
)


def require(ok, msg):
    if not bool(ok):
        raise AssertionError(msg)


def near(a, b, atol=1e-6):
    if abs(float(a) - float(b)) > atol:
        raise AssertionError(f"{a!r} != {b!r} (atol={atol})")


def check_frozen_equilibria_hand_derivation():
    results = []
    for u in [-5.0, 0.0, 1.0, 2.0, 100.0]:
        eqs = frozen_equilibria_shifted_pitchfork(u)
        require(len(eqs) == 3, "expected 3 equilibria (x=u, x=u+1, x=u-1)")
        by_x = {round(e.x - u, 6): e for e in eqs}
        require(0.0 in by_x and by_x[0.0].stability == UNSTABLE, "x=u must be unstable")
        near(by_x[0.0].local_derivative, 1.0)
        require(1.0 in by_x and by_x[1.0].stability == STABLE, "x=u+1 must be stable")
        near(by_x[1.0].local_derivative, -2.0)
        require(-1.0 in by_x and by_x[-1.0].stability == STABLE, "x=u-1 must be stable")
        near(by_x[-1.0].local_derivative, -2.0)
        results.append({"u": u, "equilibria": [{"x": e.x, "stability": e.stability, "d": e.local_derivative} for e in eqs]})
    return {"checked_u_values": [-5.0, 0.0, 1.0, 2.0, 100.0], "no_frozen_bifurcation_anywhere": True, "sample": results[0]}


def check_scope_violations():
    t1_le_t0 = False
    try:
        integrate_trajectory(lambda x, u: -x, lambda t: 0.0, 0.0, 5.0, 1.0)
    except ScopeViolationError:
        t1_le_t0 = True
    require(t1_le_t0, "expected ScopeViolationError for t1<=t0")

    unclassifiable = False
    try:
        eqs = frozen_equilibria_shifted_pitchfork(0.0)
        classify_tracking(50.0, 0.0, eqs, tol=1e-3)
    except ScopeViolationError:
        unclassifiable = True
    require(unclassifiable, "expected ScopeViolationError when final state is far from any stable branch")

    no_stable = False
    try:
        classify_tracking(1.0, 0.0, [], tol=1e-3)
    except ScopeViolationError:
        no_stable = True
    require(no_stable, "expected ScopeViolationError when no stable equilibria are supplied")

    return {"raised_on_t1_le_t0": t1_le_t0, "raised_on_unclassifiable_state": unclassifiable, "raised_on_no_stable_equilibria": no_stable}


def check_astra_worked_example():
    slow = rate_induced_tipping_cubic_example(0.1)
    fast = rate_induced_tipping_cubic_example(2.0)
    require(slow.switched is False, f"r=0.1 must track the upper branch, got switched={slow.switched!r}")
    require(fast.switched is True, f"r=2.0 must switch to the lower branch, got switched={fast.switched!r}")
    near(slow.final_relative_x, 1.0, atol=1e-6)
    near(fast.final_relative_x, -1.0, atol=1e-6)
    require(slow.refinement_max_difference < 1e-6, f"r=0.1 integration refinement too coarse: {slow.refinement_max_difference!r}")
    require(fast.refinement_max_difference < 1e-6, f"r=2.0 integration refinement too coarse: {fast.refinement_max_difference!r}")
    # Exact reported values from SCF_Nichtstationaere_Treiber_und_Kippen.md section 5.1 /
    # independent_results.json (independently reproduced fresh against this repo, commit 9e75897).
    near(slow.refinement_max_difference, 1.4874657061625385e-10, atol=1e-9)
    near(fast.refinement_max_difference, 1.3642750706921447e-08, atol=1e-9)
    return {
        "slow_r": slow.to_dict(),
        "fast_r": fast.to_dict(),
        "matches_astra_reported_values": True,
    }


def check_rate_sweep_monotone_tendency():
    """Not every rate switches; tracking degrades as r increases (not a coin flip)."""
    rates = [0.05, 0.2, 0.5, 1.0, 1.5, 2.0, 3.0, 5.0]
    switched_flags = []
    for r in rates:
        res = rate_induced_tipping_cubic_example(r)
        switched_flags.append(res.switched)
    require(switched_flags[0] is False, "the slowest rate tested must track (switched=False)")
    require(switched_flags[-1] is True, "the fastest rate tested must switch (switched=True)")
    # Once switched, must stay switched for all faster rates tested (monotone in r for this model).
    first_switch = switched_flags.index(True)
    require(all(switched_flags[first_switch:]), "once switching starts, all faster rates tested must also switch")
    return {"rates": rates, "switched": switched_flags, "first_switching_rate": rates[first_switch]}


CHECKS = [
    ("frozen_equilibria_hand_derivation", check_frozen_equilibria_hand_derivation),
    ("scope_violations", check_scope_violations),
    ("astra_worked_example_reproduction", check_astra_worked_example),
    ("rate_sweep_monotone_tendency", check_rate_sweep_monotone_tendency),
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json-out", type=Path, default=Path(__file__).with_name("verify_rate_dependent_results.json"))
    args = parser.parse_args()

    report = {
        "package": "NONSTATIONARY_ROADMAP.md package 3 (driver-dependent dynamics interface)",
        "source": SOURCE,
        "concept_origin": "prompts/Answers/nicht_stationäre_Treiber/SCF_Nichtstationaere_Treiber_und_Kippen.md",
        "timestamp": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "python": sys.version.split()[0],
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "platform": platform.platform(),
        "checks": {},
        "disclaimer": (
            "Rate-induced tipping demonstrated only for the canonical shifted-pitchfork "
            "example; no claim this mechanism applies to any real system without its own "
            "separate model and driver identification (see NONSTATIONARY_ROADMAP.md section 6)."
        ),
    }
    passed = 0
    failed = 0
    errors = []
    for name, fn in CHECKS:
        try:
            report["checks"][name] = {"status": "passed", "detail": fn()}
            passed += 1
            print(f"PASS  {name}")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            errors.append({"check": name, "error": f"{type(exc).__name__}: {exc}"})
            report["checks"][name] = {"status": "failed", "error": f"{type(exc).__name__}: {exc}"}
            print(f"FAIL  {name}: {exc}")

    summary = {"count": len(CHECKS), "passed": passed, "failed": failed, "errors": errors, "report": report}
    args.json_out.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(f"\n{passed}/{len(CHECKS)} passed; wrote {args.json_out}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
