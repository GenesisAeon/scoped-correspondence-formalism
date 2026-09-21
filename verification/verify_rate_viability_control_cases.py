#!/usr/bin/env python3
"""Rate/viability control cases (Milestone 42/43, NONSTATIONARY package 4).

Response to prompts/Answers/nicht_stationäre_Treiber/SCF_Nichtstationaere_Treiber_und_Kippen.md
(Astra, 2026-09-21) section 8 package 4: "the case computed above [the
rate-induced tipping example from package 3] plus a buffer case: same
final load values, different tempo or different reserve."

Part A: local_chi_diagnostic applied to the package-3 cubic example --
chi_max, computed in closed form purely from the driver, correlates
exactly with the already-verified switching outcome.

Part B: a scalar buffer under a single transient load spike (same load
before and after), where the frozen state is safe at baseline and
(deliberately) unsafe at the frozen peak -- tests whether the actual
transient breaches the safety boundary depending on spike tempo (tau) and
safety reserve (b), which neither frozen check alone can decide.

Checks:
  1. chi_diagnostic_for_cubic_example: closed-form chi_max = r/2 matches a
     hand computation; chi_max exceeds/stays below 0.5 exactly where
     rate_induced_tipping_cubic_example switches/tracks (r=0.05..5.0).
  2. buffer_spike_viability_report: baseline always frozen-safe, peak
     always frozen-unsafe (by construction); transient_breach transitions
     from False to True as tau increases past a threshold between 0.5 and
     1.0 (tempo dimension) -- hand-verified against directly re-integrating
     the ODE with scipy independently of the module's own solve_ivp call.
  3. Same tau, varying b: transient_breach transitions from True to False
     as the reserve (|b|) increases past the trajectory's own minimum
     (reserve dimension).
  4. run_buffer_spike_trajectory raises ScopeViolationError for r<=0 and
     tau<=0; local_chi_diagnostic raises for non-positive restoring_rate
     or distance_to_boundary.
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
import scipy
from scipy.integrate import solve_ivp

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from scoped_correspondence.errors import ScopeViolationError  # noqa: E402
from scoped_correspondence.dynamics.rate_dependent import (  # noqa: E402
    chi_diagnostic_for_cubic_example,
    local_chi_diagnostic,
    rate_induced_tipping_cubic_example,
)
from scoped_correspondence.viability.rate_dependent_buffer import (  # noqa: E402
    buffer_spike_viability_report,
    run_buffer_spike_trajectory,
)


def require(ok, msg):
    if not bool(ok):
        raise AssertionError(msg)


def near(a, b, atol=1e-6):
    if abs(float(a) - float(b)) > atol:
        raise AssertionError(f"{a!r} != {b!r} (atol={atol})")


def check_chi_diagnostic_correlates_with_switching():
    rates = [0.05, 0.1, 0.2, 0.5, 1.0, 1.5, 2.0, 3.0, 5.0]
    rows = []
    for r in rates:
        res = chi_diagnostic_for_cubic_example(r)
        near(res.chi_max, r / 2.0, atol=1e-9)  # hand closed-form: chi_max = r/2
        rows.append({"r": r, "chi_max": res.chi_max, "switched": res.switched})
    require(all(row["switched"] == (row["chi_max"] >= 0.5) for row in rows), "chi_max>=0.5 must exactly predict switching for this model")
    require(not rows[0]["switched"] and rows[-1]["switched"], "sweep must span both tracking and switching")

    below = False
    try:
        local_chi_diagnostic(1.0, 1.0, 0.0, 1.0)
    except ScopeViolationError:
        below = True
    require(below, "expected ScopeViolationError for restoring_rate<=0")
    below2 = False
    try:
        local_chi_diagnostic(1.0, 1.0, 1.0, 0.0)
    except ScopeViolationError:
        below2 = True
    require(below2, "expected ScopeViolationError for distance_to_boundary<=0")

    return {"rows": rows, "critical_chi_between": [0.25, 0.5], "raised_on_nonpositive_inputs": True}


def check_buffer_spike_tempo_dimension():
    r, z_eq, b, U, W0, spike_height = 1.0, 0.0, -0.5, 0.0, 0.0, 1.0
    rows = []
    for tau in [0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0]:
        rep = buffer_spike_viability_report(r, z_eq, b, U, W0, spike_height, tau)
        require(rep.baseline_frozen_safe, f"baseline must be frozen-safe at tau={tau}")
        require(not rep.peak_frozen_safe, f"peak must be frozen-unsafe (by construction) at tau={tau}")
        rows.append({"tau": tau, "z_min": rep.trajectory.z_min, "transient_breach": rep.transient_breach})
    require(rows[0]["transient_breach"] is False, "fastest (smallest tau) spike must NOT breach")
    require(rows[-1]["transient_breach"] is True, "slowest (largest tau) spike must breach")
    breaches = [row["transient_breach"] for row in rows]
    first_breach = breaches.index(True)
    require(all(breaches[first_breach:]), "once breaching starts, all slower (larger tau) spikes must also breach")

    # Hand re-integration, independent of the module's own solve_ivp call, for one tau.
    tau_check = 1.0
    t0, t1 = -8 * tau_check - 5, 8 * tau_check + 5
    z0 = z_eq + (U - W0) / r

    def rhs(t, z):
        return [-r * (z[0] - z_eq) + U - (W0 + spike_height * math.exp(-((t / tau_check) ** 2)))]

    sol = solve_ivp(rhs, (t0, t1), [z0], rtol=1e-12, atol=1e-14, dense_output=True, max_step=tau_check / 40)
    require(sol.success, "hand re-integration must succeed")
    grid = np.linspace(t0, t1, 8001)
    hand_z_min = float(np.min(sol.sol(grid)[0]))
    module_z_min = next(row["z_min"] for row in rows if row["tau"] == tau_check)
    near(hand_z_min, module_z_min, atol=1e-4)

    return {"rows": rows, "hand_reintegration_z_min": hand_z_min, "module_z_min": module_z_min}


def check_buffer_spike_reserve_dimension():
    r, z_eq, U, W0, spike_height, tau = 1.0, 0.0, 0.0, 0.0, 1.0, 1.0
    rows = []
    for b in [-0.3, -0.5, -0.7, -0.9]:
        rep = buffer_spike_viability_report(r, z_eq, b, U, W0, spike_height, tau)
        rows.append({"b": b, "transient_breach": rep.transient_breach})
    require(rows[0]["transient_breach"] is True, "smallest reserve (b=-0.3) must breach")
    require(rows[-1]["transient_breach"] is False, "largest reserve (b=-0.9) must NOT breach")
    breaches = [row["transient_breach"] for row in rows]
    last_breach = len(breaches) - 1 - breaches[::-1].index(True)
    require(not any(breaches[last_breach + 1 :]), "once safe (larger reserve), all larger reserves must stay safe")
    return {"rows": rows, "fixed_tau": tau}


def check_scope_violations():
    r_le_0 = False
    try:
        run_buffer_spike_trajectory(0.0, 0.0, 0.0, 0.0, 1.0, 1.0)
    except ScopeViolationError:
        r_le_0 = True
    require(r_le_0, "expected ScopeViolationError for r<=0")

    tau_le_0 = False
    try:
        run_buffer_spike_trajectory(1.0, 0.0, 0.0, 0.0, 1.0, 0.0)
    except ScopeViolationError:
        tau_le_0 = True
    require(tau_le_0, "expected ScopeViolationError for tau<=0")

    return {"raised_on_r_le_0": r_le_0, "raised_on_tau_le_0": tau_le_0}


CHECKS = [
    ("chi_diagnostic_correlates_with_switching", check_chi_diagnostic_correlates_with_switching),
    ("buffer_spike_tempo_dimension", check_buffer_spike_tempo_dimension),
    ("buffer_spike_reserve_dimension", check_buffer_spike_reserve_dimension),
    ("scope_violations", check_scope_violations),
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json-out", type=Path, default=Path(__file__).with_name("verify_rate_viability_control_cases_results.json"))
    args = parser.parse_args()

    report = {
        "package": "NONSTATIONARY_ROADMAP.md package 4 (rate/viability control cases)",
        "source": "prompts/Answers/nicht_stationäre_Treiber/SCF_Nichtstationaere_Treiber_und_Kippen.md",
        "timestamp": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "python": sys.version.split()[0],
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "platform": platform.platform(),
        "checks": {},
        "disclaimer": (
            "Part A (chi diagnostic) and Part B (buffer spike) are synthetic control "
            "cases; no claim about any real driver, buffer, or safety system without "
            "its own separate model and identification."
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
