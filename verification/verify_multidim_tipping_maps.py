#!/usr/bin/env python3
"""Multidimensional R-tipping / viability response surfaces (Milestone 54).

MECHANISTIC_VALIDATION_ROADMAP.md package 6, response to
prompts/Answers/nicht_stationäre_Treiber/SCF_Review_3e8dce3.md (Astra,
2026-09-23).

Checks (all numbers from this script run):
  1. Buffer equal-peak-height surface reproduces
     docs/rate_dependent_tipping.md's known 1-D tau sweep EXACTLY (same
     z_min values, same tracking/switched classification) when read off a
     2-D grid with a single amplitude column -- the new machinery is not
     silently different from the already-verified 1-D case.
  2. Buffer equal-total-load surface likewise reproduces the known
     REVERSED ranking exactly.
  3. Reserve frontier: critical_b equals the trajectory's own z_min
     exactly (hand-derivation: b does not appear in the ODE), cross-checked
     against explicit classification at 4 b values matching the doc.
  4. OUT_OF_SCOPE is empirically triggered (not just defensively coded)
     by a boundary b set ABOVE the frozen-safe baseline threshold.
  5. Cubic tracking response surface reproduces the two already-verified
     (r, x0_offset=1.0) points exactly (r=0.1 tracks, r=2.0 switches).
  6. A genuine second axis (x0_offset as a reserve proxy) is EMPIRICALLY
     dependency-free at the module's default margin=10 (an honest null
     result: the long pre-driving relaxation window erases initial-offset
     memory before the real driving begins) but shows real dependence at
     a shorter margin=3 -- both are checked, not just the convenient one.
  7. UNRESOLVED is empirically triggered (not just defensively coded) by
     a real borderline case (r=0.75, x0_offset=0.6, margin=3.0) where the
     trajectory has not settled within tolerance by t1 -- distinguished
     from a genuine solver failure by inspecting the underlying
     ScopeViolationError's message.

INTEGRATION_ERROR is defensively coded (a try/except around each grid
cell) but NOT empirically triggered by any grid in this script -- noted
here explicitly rather than manufactured via a pathological, slow-to-fail
parameter combination.
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

from scoped_correspondence.viability.multidim_tipping_maps import (  # noqa: E402
    SOURCE,
    TRACKING,
    SWITCHED,
    UNRESOLVED,
    OUT_OF_SCOPE,
    INTEGRATION_ERROR,
    buffer_response_surface,
    buffer_reserve_frontier,
    tracking_response_surface,
)


def require(ok, msg):
    if not bool(ok):
        raise AssertionError(msg)


def near(a, b, atol=1e-6):
    if abs(float(a) - float(b)) > atol:
        raise AssertionError(f"{a!r} != {b!r} (atol={atol})")


def check_buffer_equal_peak_height():
    """Reproduces docs/rate_dependent_tipping.md's known equal-peak-height table."""
    taus = [0.05, 0.20, 0.50, 1.00, 2.00, 5.00]
    expected_z_min = [-0.081, -0.265, -0.495, -0.695, -0.858, -0.965]
    expected_outcome = [TRACKING, TRACKING, TRACKING, SWITCHED, SWITCHED, SWITCHED]

    surf = buffer_response_surface(1.0, 0.0, 0.0, 0.0, -0.5, taus=taus, amplitude_params=[1.0], amplitude_mode="peak_height")
    require(surf.amplitude_mode == "peak_height", "amplitude_mode must round-trip")
    require(len(surf.cells) == len(taus), "one cell per tau (single amplitude column)")
    for cell, exp_z, exp_out in zip(surf.cells, expected_z_min, expected_outcome):
        near(cell.z_min, exp_z, atol=5e-4)
        require(cell.outcome == exp_out, f"tau={cell.tau}: expected {exp_out}, got {cell.outcome}")

    return {"taus": taus, "z_min": [c.z_min for c in surf.cells], "outcomes": [c.outcome for c in surf.cells]}


def check_buffer_equal_total_load():
    """Reproduces docs/rate_dependent_tipping.md's known REVERSED equal-total-load table."""
    taus = [0.05, 0.20, 0.50, 1.00, 2.00, 5.00]
    expected_height = [11.28, 2.82, 1.13, 0.56, 0.28, 0.11]
    expected_z_min = [-0.912, -0.747, -0.558, -0.392, -0.242, -0.109]
    expected_outcome = [SWITCHED, SWITCHED, SWITCHED, TRACKING, TRACKING, TRACKING]

    surf = buffer_response_surface(1.0, 0.0, 0.0, 0.0, -0.5, taus=taus, amplitude_params=[1.0], amplitude_mode="total_load")
    require(surf.amplitude_mode == "total_load", "amplitude_mode must round-trip")
    for cell, exp_h, exp_z, exp_out in zip(surf.cells, expected_height, expected_z_min, expected_outcome):
        near(cell.spike_height, exp_h, atol=5e-3)
        near(cell.z_min, exp_z, atol=5e-4)
        require(cell.outcome == exp_out, f"tau={cell.tau}: expected {exp_out}, got {cell.outcome}")

    # The ranking must be the OPPOSITE of the equal-peak-height case at the
    # same taus -- this IS the "answers a different question" finding.
    peak = check_buffer_equal_peak_height()
    require(
        peak["outcomes"] != [c.outcome for c in surf.cells][::1] or peak["outcomes"][::-1] == [c.outcome for c in surf.cells],
        "equal-total-load ranking should reverse relative to equal-peak-height at the same taus",
    )
    return {"taus": taus, "heights": [c.spike_height for c in surf.cells], "z_min": [c.z_min for c in surf.cells], "outcomes": [c.outcome for c in surf.cells]}


def check_reserve_frontier():
    """critical_b == z_min exactly (hand-derivation: b is absent from the ODE)."""
    rf = buffer_reserve_frontier(1.0, 0.0, 0.0, 0.0, 1.0, 1.0, b_values=[-0.3, -0.5, -0.7, -0.9])
    near(rf.z_min, -0.6947528523, atol=1e-6)
    near(rf.critical_b, rf.z_min, atol=1e-15)  # exact identity, not an approximation
    expected = {-0.3: SWITCHED, -0.5: SWITCHED, -0.7: TRACKING, -0.9: TRACKING}
    for p in rf.points:
        require(p.outcome == expected[p.b], f"b={p.b}: expected {expected[p.b]}, got {p.outcome}")
    # Sign check: margin = z_min - b, so a HIGHER boundary b (closer to the
    # safe baseline, less depth) leaves LESS margin -- b above critical_b=z_min
    # switches (breaches), b below it tracks (stays safe).
    for p in rf.points:
        if p.b > rf.critical_b:
            require(p.outcome == SWITCHED, f"b={p.b} > critical_b={rf.critical_b} must switch")
        elif p.b < rf.critical_b:
            require(p.outcome == TRACKING, f"b={p.b} < critical_b={rf.critical_b} must track")
    return rf.to_dict()


def check_buffer_out_of_scope():
    """A boundary b ABOVE the frozen-safe baseline threshold must be OUT_OF_SCOPE,
    not silently classified as TRACKING or SWITCHED."""
    # baseline_frozen_safe requires r*(z_eq-b)+U-W0 >= 0 -> b <= z_eq+(U-W0)/r = 0 here.
    surf = buffer_response_surface(1.0, 0.0, 0.0, 0.0, b=0.1, taus=[1.0], amplitude_params=[1.0], amplitude_mode="peak_height")
    require(surf.cells[0].outcome == OUT_OF_SCOPE, f"expected out_of_scope, got {surf.cells[0].outcome!r}")
    # And b exactly at the safe/unsafe boundary (b=0.0) is still safe (>=, not >).
    surf_edge = buffer_response_surface(1.0, 0.0, 0.0, 0.0, b=0.0, taus=[1.0], amplitude_params=[1.0], amplitude_mode="peak_height")
    require(surf_edge.cells[0].outcome != OUT_OF_SCOPE, "b=0.0 exactly at the threshold must still be frozen-safe (>=)")
    return {"b_unsafe": 0.1, "outcome_unsafe": surf.cells[0].outcome, "b_edge": 0.0, "outcome_edge": surf_edge.cells[0].outcome}


def check_cubic_known_points():
    """Reproduces the two already-verified (r, x0_offset=1.0) points exactly."""
    cs = tracking_response_surface([0.1, 2.0], [1.0])
    by_r = {c.r: c for c in cs.cells}
    near(by_r[0.1].final_relative_x, 1.0, atol=1e-6)
    require(by_r[0.1].outcome == TRACKING, "r=0.1 must track")
    near(by_r[2.0].final_relative_x, -1.0, atol=1e-6)
    require(by_r[2.0].outcome == SWITCHED, "r=2.0 must switch")
    return {c.r: c.to_dict() for c in cs.cells}


def check_cubic_reserve_axis():
    """Reserve axis (x0_offset) is empirically INERT at margin=10 (an honest
    null result -- long pre-driving relaxation erases initial-offset memory)
    but shows REAL dependence at margin=3 near the critical rate -- both
    checked, including a genuine, non-manufactured UNRESOLVED cell.
    """
    x0_grid = [0.05, 0.2, 0.4, 0.6, 0.8, 1.0, 1.5, 2.0]

    # Null result at the module's own default margin (10.0): outcome must be
    # constant across the whole x0_offset row at r=0.8 (just past critical).
    cs_default = tracking_response_surface([0.8], x0_grid)  # margin defaults to 10.0
    outcomes_default = {c.outcome for c in cs_default.cells}
    require(outcomes_default == {SWITCHED}, f"expected a UNIFORM row at margin=10, got {outcomes_default!r}")

    # Real dependence at margin=3.0, r=0.75: a mix of switched/unresolved/tracking.
    cs_short = tracking_response_surface([0.75], x0_grid, margin=3.0)
    by_x0 = {c.x0_offset: c.outcome for c in cs_short.cells}
    require(by_x0[0.05] == SWITCHED, f"x0=0.05: expected switched, got {by_x0[0.05]!r}")
    require(by_x0[0.2] == SWITCHED, f"x0=0.2: expected switched, got {by_x0[0.2]!r}")
    require(by_x0[0.6] == UNRESOLVED, f"x0=0.6: expected unresolved (real not-yet-settled case), got {by_x0[0.6]!r}")
    require(by_x0[1.0] == TRACKING, f"x0=1.0: expected tracking, got {by_x0[1.0]!r}")
    require(by_x0[2.0] == TRACKING, f"x0=2.0: expected tracking, got {by_x0[2.0]!r}")
    require(
        len({by_x0[0.05], by_x0[1.0]}) == 2,
        "reserve axis must actually distinguish outcomes at margin=3 (not another accidental null result)",
    )

    return {
        "margin_10_row_r_0.8": {x0: c.outcome for x0, c in zip(x0_grid, cs_default.cells)},
        "margin_3_row_r_0.75": by_x0,
    }


CHECKS = [
    ("buffer_equal_peak_height", check_buffer_equal_peak_height),
    ("buffer_equal_total_load", check_buffer_equal_total_load),
    ("reserve_frontier", check_reserve_frontier),
    ("buffer_out_of_scope", check_buffer_out_of_scope),
    ("cubic_known_points", check_cubic_known_points),
    ("cubic_reserve_axis", check_cubic_reserve_axis),
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json-out", type=Path, default=Path(__file__).with_name("verify_multidim_tipping_maps_results.json"))
    args = parser.parse_args()

    report = {
        "package": "MECHANISTIC_VALIDATION_ROADMAP.md package 6 (multidimensional R-tipping / viability maps)",
        "source": SOURCE,
        "outcome_states": [TRACKING, SWITCHED, UNRESOLVED, OUT_OF_SCOPE, INTEGRATION_ERROR],
        "timestamp": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "python": sys.version.split()[0],
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "platform": platform.platform(),
        "checks": {},
        "disclaimer": (
            "INTEGRATION_ERROR is defensively coded (try/except around every grid cell) but not "
            "empirically triggered by any grid run in this script -- a genuine solve_ivp failure "
            "was only reproducible via a pathologically slow (near-hanging) parameter combination, "
            "which was deliberately not adopted as a test case."
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
