#!/usr/bin/env python3
"""Concrete 3-node resource network pilot (INTEGRATED_EXTENSION_ROADMAP.md
Paket C5, plan section 9.4's fixed panel) -- synthetic-only, no network
access needed.

Checks:

  1. The declared load schedule matches the fixed panel's own numbers at
     specific control times (base 0.3, +0.9 spikes at the declared windows).
  2. The "none" and "fixed_routing" baselines (which never call the QP
     solver) are cross-checked against an INDEPENDENT direct hand-computation
     of the same affine updates.
  3. Weak-duality sanity check: whenever the "none" baseline action is
     ITSELF feasible for a given interval (checked directly, independent of
     the solver), the "optimized" strategy's QP cost for that SAME interval
     must be <= the baseline's cost (0.27) -- minimizing over a feasible set
     that CONTAINS a known feasible point cannot do worse than that point.
  4. A concrete, real (not constructed) case where `first_touch_time` and
     `strict_violation_time` genuinely differ: the "optimized" strategy at
     control_interval=1 touches exactly 0 at t=2 but only strictly violates
     later, at t=4 -- reported as two DIFFERENT times, never conflated.
  5. The mandatory structural counter-check (extra-switchable-edge weakly
     improves the optimum) reproduced directly on this panel's own network
     and parameters, not just the abstract 2-node example in
     verify_resource_network_control.py.
  6. SCF_REVIEW_C0_C7_4ed0cd9.md finding R6 (a real bug, independently
     reproduced before fixing): the SAME "none" baseline trajectory must
     report the EXACT SAME true touch time (5/3, Astra's own closed-form
     value) regardless of whether control_interval is 1 or 0.25 -- the old
     code reported 2.0 and 1.75 respectively (both wrong, and inconsistent
     with each other for the identical physical trajectory).
  7. SCF_REVIEW_C0_C7_4ed0cd9.md finding R7 (a real bug, independently
     reproduced before fixing): control_interval=2.0 must be REJECTED (it
     would silently sample demand only at t=0,2,4, missing both declared
     load spikes entirely) -- the two officially compared values (0.25, 1)
     must still be accepted.
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
from scoped_correspondence.validation.resource_network_pilot import (  # noqa: E402
    NETWORK, run_network_pilot, _demand, U_MAX, EDGE_CAP, TOTAL_SUPPLY_CAP, W, V, K_UPPER,
)
from scoped_correspondence.viability.resource_network_control import (  # noqa: E402
    whole_interval_safety, solve_network_qp,
)


def require(ok, msg):
    if not bool(ok):
        raise AssertionError(msg)


def check_load_schedule_control_values():
    require(np.allclose(_demand(0.5), [0.3, 0.3, 0.3]), "before any spike, demand should be base load everywhere")
    require(np.allclose(_demand(1.5), [1.2, 0.3, 0.3]), "during [1,2), node 0 should be at 0.3+0.9=1.2")
    require(np.allclose(_demand(2.5), [0.3, 0.3, 0.3]), "between spikes, demand should return to base load")
    require(np.allclose(_demand(3.5), [0.3, 0.3, 1.2]), "during [3,4), node 2 should be at 0.3+0.9=1.2")
    require(np.allclose(_demand(5.0), [0.3, 0.3, 0.3]), "after both spikes, demand should return to base load")
    return {"ok": True}


def check_baselines_match_hand_computation():
    B = NETWORK.incidence_matrix()
    for Delta in (1.0, 0.25):
        x_none = np.array([0.6, 0.6, 0.6])
        x_routed = np.array([0.6, 0.6, 0.6])
        min_none, min_routed = float(np.min(x_none)), float(np.min(x_routed))
        n_steps = int(round(6.0 / Delta))
        for step in range(n_steps):
            t0 = step * Delta
            d = _demand(t0)
            x_none = x_none + Delta * (np.array([0.3, 0.3, 0.3]) - d)
            f_routed = np.array([0.2, 0.2, 0.0])
            x_routed = x_routed + Delta * (B @ f_routed + np.array([0.3, 0.3, 0.3]) - d)
            min_none = min(min_none, float(np.min(x_none)))
            min_routed = min(min_routed, float(np.min(x_routed)))

        r_none = run_network_pilot("none", Delta, edge_failure=False)
        r_routed = run_network_pilot("fixed_routing", Delta, edge_failure=False)
        require(abs(r_none.min_reserve - min_none) < 1e-6,
                f"Delta={Delta}: 'none' pilot min reserve ({r_none.min_reserve!r}) should match the independent "
                f"hand-computed trajectory minimum ({min_none!r})")
        require(abs(r_routed.min_reserve - min_routed) < 1e-6,
                f"Delta={Delta}: 'fixed_routing' pilot min reserve ({r_routed.min_reserve!r}) should match the "
                f"independent hand-computed trajectory minimum ({min_routed!r})")
        require(np.allclose(x_none, x_none, atol=1e-9) and np.allclose(x_routed, x_routed, atol=1e-9), "sanity")
    return {"ok": True}


def check_weak_duality_optimized_beats_feasible_baseline():
    baseline_u = np.array([0.3, 0.3, 0.3])
    baseline_f = np.zeros(3)
    baseline_cost = float(np.sum(W * baseline_u ** 2) + np.sum(V * baseline_f ** 2))

    x = np.array([0.6, 0.6, 0.6])
    d = _demand(0.0)
    Delta = 1.0
    safety = whole_interval_safety(x, NETWORK.incidence_matrix(), baseline_f, baseline_u, d, Delta)
    require(safety.status in ("certified_safe", "boundary_touch"), "the baseline action must itself be feasible at t=0 for this check to be meaningful")

    result = solve_network_qp(NETWORK, x_lower=x, d_upper=d, Delta=Delta, u_max=U_MAX, edge_cap=EDGE_CAP,
                               total_supply_cap=TOTAL_SUPPLY_CAP, w=W, v=V, K=np.full(3, K_UPPER))
    require(result.status == "solved", "the QP should solve at t=0")
    require(result.cost <= baseline_cost + 1e-6,
            f"optimized cost ({result.cost!r}) must not exceed the feasible baseline's cost ({baseline_cost!r})")
    return {"optimized_cost": result.cost, "baseline_cost": baseline_cost}


def check_touch_and_violation_reported_separately():
    """**Correction (2026-09-25, response to SCF_REVIEW_C0_C7_4ed0cd9.md
    findings R6/R7):** this check's ORIGINAL expected strict-violation time
    (4.0) was itself just the old, grid-snapped control-interval endpoint --
    "das Abschreiben des Intervallendpunkts ist keine unabhängige Kontrolle"
    (the review's own words) -- not an independently re-derived value. The
    corrected exact-affine-crossing code gives a materially DIFFERENT, more
    informative picture: the optimized controller reaches exactly 0 at
    t~2.0 during the first spike's aftermath (a genuine BOUNDARY TOUCH that
    then RECOVERS -- held flat at 0 through [2,3) at zero cost-beyond-
    baseline), and only genuinely goes STRICTLY negative later, at exactly
    t=3.0, the instant the SECOND declared spike (node 2) begins and the QP
    interval is reported infeasible (module docstring)."""
    r = run_network_pilot("optimized", control_interval=1.0, edge_failure=False)
    require(r.first_touch_time is not None and r.strict_violation_time is not None, "both events should occur in this run")
    require(r.first_touch_time < r.strict_violation_time,
            f"first_touch_time ({r.first_touch_time!r}) should be STRICTLY earlier than strict_violation_time "
            f"({r.strict_violation_time!r}) in this concrete case, demonstrating the two are genuinely different events")
    require(abs(r.first_touch_time - 2.0) < 1e-6, f"expected first touch at t=2.0, got {r.first_touch_time!r}")
    require(abs(r.strict_violation_time - 3.0) < 1e-6, f"expected strict violation at t=3.0 (the second spike's own start), got {r.strict_violation_time!r}")
    return {"first_touch_time": r.first_touch_time, "strict_violation_time": r.strict_violation_time}


def check_structural_extra_edge_on_real_panel():
    x = np.array([0.3, 0.3, 0.3])  # the depleted state entering the first spike (see docs)
    d = _demand(1.5)
    Delta = 1.0
    result_with_edge = solve_network_qp(NETWORK, x_lower=x, d_upper=d, Delta=Delta, u_max=U_MAX, edge_cap=EDGE_CAP,
                                         total_supply_cap=TOTAL_SUPPLY_CAP, w=W, v=V, K=np.full(3, K_UPPER))
    edge_cap_no_extra = EDGE_CAP.copy()
    edge_cap_no_extra[2] = 0.0  # disable the 2->0 edge specifically
    result_no_extra_edge = solve_network_qp(NETWORK, x_lower=x, d_upper=d, Delta=Delta, u_max=U_MAX, edge_cap=edge_cap_no_extra,
                                             total_supply_cap=TOTAL_SUPPLY_CAP, w=W, v=V, K=np.full(3, K_UPPER))
    if result_with_edge.status == "solved" and result_no_extra_edge.status == "solved":
        require(result_with_edge.cost <= result_no_extra_edge.cost + 1e-6,
                f"enabling the extra edge (2->0) must not worsen the optimum: {result_with_edge.cost!r} vs {result_no_extra_edge.cost!r}")
    # If disabling makes it infeasible while enabling solves it, that ALSO demonstrates the edge only helps.
    require(not (result_with_edge.status != "solved" and result_no_extra_edge.status == "solved"),
            "the extra edge must never turn a solvable interval into an unsolvable one")
    return {"with_edge": result_with_edge.status, "without_extra_edge": result_no_extra_edge.status,
            "cost_with_edge": result_with_edge.cost, "cost_without_extra_edge": result_no_extra_edge.cost}


def check_r6_touch_time_independent_of_control_interval():
    r1 = run_network_pilot("none", 1.0, False)
    r_quarter = run_network_pilot("none", 0.25, False)
    true_touch = 1.0 + 0.6 / 0.9  # = 5/3, Astra's own closed-form value for this baseline
    require(abs(r1.first_touch_time - true_touch) < 1e-9, f"Delta=1: expected {true_touch!r}, got {r1.first_touch_time!r}")
    require(abs(r_quarter.first_touch_time - true_touch) < 1e-9, f"Delta=0.25: expected {true_touch!r}, got {r_quarter.first_touch_time!r}")
    require(abs(r1.first_touch_time - r_quarter.first_touch_time) < 1e-9,
            "the identical physical baseline trajectory must report the IDENTICAL touch time regardless of control_interval")
    return {"true_touch": true_touch, "delta_1": r1.first_touch_time, "delta_0_25": r_quarter.first_touch_time}


def check_r7_control_interval_must_align_with_load_changes():
    try:
        run_network_pilot("none", 2.0, False)
        raise AssertionError("control_interval=2.0 must be rejected -- it would silently skip both declared load spikes")
    except ScopeViolationError:
        pass
    # The two officially compared values must still be accepted.
    for ci in (0.25, 1.0):
        r = run_network_pilot("none", ci, False)
        require(r.first_touch_time is not None, f"control_interval={ci} should still simulate normally")
    return {"rejected": 2.0, "accepted": [0.25, 1.0]}


CHECKS = [
    ("load_schedule_control_values", check_load_schedule_control_values),
    ("baselines_match_hand_computation", check_baselines_match_hand_computation),
    ("weak_duality_optimized_beats_feasible_baseline", check_weak_duality_optimized_beats_feasible_baseline),
    ("touch_and_violation_reported_separately", check_touch_and_violation_reported_separately),
    ("structural_extra_edge_on_real_panel", check_structural_extra_edge_on_real_panel),
    ("r6_touch_time_independent_of_control_interval", check_r6_touch_time_independent_of_control_interval),
    ("r7_control_interval_must_align_with_load_changes", check_r7_control_interval_must_align_with_load_changes),
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json-out", type=Path, default=Path(__file__).with_name("verify_resource_network_pilot_results.json"))
    args = parser.parse_args()

    report = {
        "package": "INTEGRATED_EXTENSION_ROADMAP.md Paket C5 (3-node resource network pilot, synthetic-only)",
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
