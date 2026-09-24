#!/usr/bin/env python3
"""From safety maps to bounded interventions: two-buffer CBF-QP (Milestone 59).

CAPABILITY_EXPANSION_ROADMAP.md Priority 5. Checks:

  1. Hand arithmetic for ``cbf_margin`` / ``cbf_lower_bound``.
  2. ``BufferSpec`` construction guard (``u_min > u_max`` rejected).
  3. Two DISTINCT infeasibility reasons, both surfaced explicitly rather
     than via a generic solver failure: (a) a buffer whose own CBF-minimal
     control already exceeds its own ``u_max``, independent of budget;
     (b) both buffers individually admissible, but their combined
     CBF-minimal cost exceeds the SHARED budget.
  4. A feasible case where the QP's numerical solution is checked against
     an independently hand-derived closed-form optimum (not just against
     the module's own internal cross-check).
  5. The full three-way comparison (no intervention / fixed rule /
     optimized) on one worked example, checked against Astra's explicit
     reporting requirement: violation, cost, AND admissibility must differ
     meaningfully across the three -- specifically here, the naive fixed
     rule satisfies the CBF condition instantaneously but is INADMISSIBLE
     (exceeds the shared budget), while the optimized intervention is both
     instantaneously CBF-satisfying and admissible at lower cost.
  6. ScopeViolationError guards for shape/count mismatches.
  7. Astra's 2026-09-24 (SCF_Review_dc5d82a.md, finding R4) correction:
     instantaneous CBF satisfaction is not trajectory safety.
     ``held_control_violation_time`` is checked against Astra's exact hand
     derivation (holding the optimized u1=2 constant gives x1(t)=1-t,
     violating at t=1 exactly); the full comparison at budget=3 confirms
     the optimized solution is instantaneously CBF-satisfying but NOT
     sustained-safe over a horizon, while the (budget-inadmissible) fixed
     rule IS sustained-safe forever; a second worked example with a budget
     that covers total drain shows the fixed rule becoming admissible AND
     sustained-safe while the cheaper optimized point still is not --
     demonstrating "cheapest instantaneously-safe" and "sustained-safe"
     are genuinely different questions, not solved by this module alone.
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
from scoped_correspondence.viability.coupled_buffer_cbf_qp import (  # noqa: E402
    SOURCE, NO_INTERVENTION, FIXED_RULE, OPTIMIZED_QP,
    BufferSpec, cbf_margin, cbf_lower_bound, held_control_violation_time, sustained_safety_over_horizon,
    evaluate_fixed_control, solve_cbf_qp, compare_intervention_strategies,
)


def require(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)


def check_hand_arithmetic():
    b = BufferSpec(drain=3.0, x=1.0, u_min=0.0, u_max=5.0)
    require(cbf_lower_bound(b) == 2.0, f"cbf_lower_bound: got {cbf_lower_bound(b)}, want 2.0")
    require(cbf_margin(b, 0.0) == -2.0, f"cbf_margin(u=0): got {cbf_margin(b, 0.0)}, want -2.0")
    require(cbf_margin(b, 2.0) == 0.0, f"cbf_margin(u=2): got {cbf_margin(b, 2.0)}, want 0.0")
    require(cbf_margin(b, 5.0) == 3.0, f"cbf_margin(u=5): got {cbf_margin(b, 5.0)}, want 3.0")

    try:
        BufferSpec(drain=1.0, x=1.0, u_min=5.0, u_max=0.0)
        raise AssertionError("BufferSpec should reject u_min > u_max")
    except ScopeViolationError:
        pass
    return {"lower_bound": cbf_lower_bound(b)}


def check_own_bounds_infeasibility():
    b1 = BufferSpec(drain=10.0, x=0.0, u_min=0.0, u_max=5.0)
    b2 = BufferSpec(drain=0.0, x=5.0, u_min=0.0, u_max=5.0)
    r = solve_cbf_qp([b1, b2], budget=1000.0)  # huge budget -- must still be infeasible
    require(r.infeasible_problem, "expected infeasible_problem=True for an own-bounds violation")
    require("own bounds" in r.infeasibility_reason, f"reason should cite own bounds: {r.infeasibility_reason}")
    return {"reason": r.infeasibility_reason}


def check_budget_infeasibility():
    b1 = BufferSpec(drain=3.0, x=1.0, u_min=0.0, u_max=5.0)
    b2 = BufferSpec(drain=2.0, x=5.0, u_min=0.0, u_max=5.0)
    r = solve_cbf_qp([b1, b2], budget=1.5)  # each buffer individually fine, sum (2.0) > budget (1.5)
    require(r.infeasible_problem, "expected infeasible_problem=True for a budget violation")
    require("shared budget" in r.infeasibility_reason, f"reason should cite the shared budget: {r.infeasibility_reason}")
    return {"reason": r.infeasibility_reason}


def check_feasible_case_against_hand_derived_optimum():
    b1 = BufferSpec(drain=3.0, x=1.0, u_min=0.0, u_max=5.0)
    b2 = BufferSpec(drain=2.0, x=5.0, u_min=0.0, u_max=5.0)
    # Hand derivation: buffer 1 needs u1 >= 3-1=2; buffer 2 needs u2 >= max(0, 2-5)=0.
    # Cost u1^2+u2^2 is increasing in each u_i above its own lower bound, and the
    # budget (3.0) exactly covers the sum of lower bounds (2.0) -- so the true
    # optimum is (2.0, 0.0), cost 4.0, independent of the solver.
    r = solve_cbf_qp([b1, b2], budget=3.0)
    require(not r.infeasible_problem, "expected a feasible solution")
    require(abs(r.u[0] - 2.0) < 1e-6 and abs(r.u[1] - 0.0) < 1e-6, f"u mismatch: {r.u}")
    require(abs(r.cost - 4.0) < 1e-6, f"cost mismatch: {r.cost}")
    require(r.cbf_condition_satisfied_now and r.admissible, "feasible optimum should satisfy the CBF condition now and be admissible")
    return {"u": list(r.u), "cost": r.cost}


def check_three_way_comparison():
    b1 = BufferSpec(drain=3.0, x=1.0, u_min=0.0, u_max=5.0)
    b2 = BufferSpec(drain=2.0, x=5.0, u_min=0.0, u_max=5.0)
    out = compare_intervention_strategies([b1, b2], budget=3.0)
    require(set(out) == {NO_INTERVENTION, FIXED_RULE, OPTIMIZED_QP}, f"unexpected keys: {set(out)}")

    no_int = out[NO_INTERVENTION]
    require(not no_int.cbf_condition_satisfied_now, "no_intervention should violate the CBF condition now (buffer 1 drains below its margin)")
    require(no_int.admissible, "no_intervention (u=0) should trivially be within bounds and budget")
    require(no_int.cost == 0.0, "no_intervention cost should be 0")

    fixed = out[FIXED_RULE]
    require(fixed.cbf_condition_satisfied_now, "fixed_rule (u_i=drain_i) should itself satisfy every CBF condition")
    require(not fixed.admissible, "fixed_rule should be INADMISSIBLE here -- it exceeds the shared budget")

    opt = out[OPTIMIZED_QP]
    require(opt.cbf_condition_satisfied_now and opt.admissible, "optimized_qp should satisfy the CBF condition now and be admissible")
    require(opt.cost < fixed.cost, f"optimized cost ({opt.cost}) should beat the fixed rule's cost ({fixed.cost})")

    require(len({no_int.cbf_condition_satisfied_now, fixed.admissible, opt.cbf_condition_satisfied_now and opt.admissible}) >= 2,
            "the three strategies should not all report the same outcome")
    return {
        "no_intervention": no_int.to_dict(),
        "fixed_rule": fixed.to_dict(),
        "optimized_qp": opt.to_dict(),
    }


def check_scope_violation_guards():
    b1 = BufferSpec(drain=3.0, x=1.0, u_min=0.0, u_max=5.0)
    b2 = BufferSpec(drain=2.0, x=5.0, u_min=0.0, u_max=5.0)
    b3 = BufferSpec(drain=1.0, x=1.0, u_min=0.0, u_max=5.0)

    try:
        evaluate_fixed_control([b1, b2], [0.0], budget=1.0, label="x")
        raise AssertionError("evaluate_fixed_control should reject mismatched lengths")
    except ScopeViolationError:
        pass
    try:
        solve_cbf_qp([b1, b2, b3], budget=1.0)
        raise AssertionError("solve_cbf_qp should reject != 2 buffers")
    except ScopeViolationError:
        pass
    try:
        compare_intervention_strategies([b1, b2, b3], budget=1.0)
        raise AssertionError("compare_intervention_strategies should reject != 2 buffers")
    except ScopeViolationError:
        pass
    return {"checked": 3}


def check_instantaneous_safety_is_not_trajectory_safety():
    """SCF_Review_dc5d82a.md finding R4. Astra's exact hand derivation: holding
    the optimized u1=2 constant on buffer1 (drain=3, x=1) gives x1(t)=1-t,
    negative for t>1. The optimized_qp solution satisfies the CBF condition
    NOW but is not SUSTAINED-safe; the (budget-inadmissible) fixed rule, which
    exactly replaces the drain, is sustained-safe forever.
    """
    b1 = BufferSpec(drain=3.0, x=1.0, u_min=0.0, u_max=5.0)
    b2 = BufferSpec(drain=2.0, x=5.0, u_min=0.0, u_max=5.0)

    vt = held_control_violation_time(b1, 2.0)
    require(vt is not None and abs(vt - 1.0) < 1e-9, f"expected violation at t=1 exactly; got {vt}")

    out = compare_intervention_strategies([b1, b2], budget=3.0, horizon=5.0)
    opt = out[OPTIMIZED_QP]
    require(opt.cbf_condition_satisfied_now, "optimized_qp must still satisfy the CBF condition instantaneously")
    require(opt.sustained_safe_until_horizon is False, "optimized_qp must NOT be sustained-safe over the horizon")
    require(opt.first_violation_time is not None and abs(opt.first_violation_time - 1.0) < 1e-9,
            f"optimized_qp's first_violation_time should be exactly 1.0; got {opt.first_violation_time}")

    fixed = out[FIXED_RULE]
    require(fixed.sustained_safe_until_horizon is True, "fixed_rule (replaces the drain exactly) should be sustained-safe forever")
    require(fixed.first_violation_time is None, "fixed_rule should report no violation time")

    # Second worked example: a budget that covers TOTAL drain (5) makes the fixed
    # rule both admissible AND sustained-safe, while the cheaper instantaneous
    # optimum still is not -- "cheapest CBF-now" and "sustained-safe" are
    # genuinely different questions, not solved by a single-snapshot QP alone.
    out2 = compare_intervention_strategies([b1, b2], budget=5.0, horizon=10.0)
    fixed2, opt2 = out2[FIXED_RULE], out2[OPTIMIZED_QP]
    require(fixed2.admissible and fixed2.sustained_safe_until_horizon,
            "with budget covering total drain, fixed_rule should be admissible AND sustained-safe")
    require(opt2.admissible and opt2.cbf_condition_satisfied_now and not opt2.sustained_safe_until_horizon,
            "optimized_qp should remain admissible/CBF-satisfying-now but still not sustained-safe even with a larger budget")
    require(opt2.cost < fixed2.cost, "optimized_qp should still be cheaper instantaneously, despite not being sustained-safe")

    return {
        "violation_time_hand_check": vt,
        "budget_3_optimized": opt.to_dict(), "budget_3_fixed": fixed.to_dict(),
        "budget_5_optimized_sustained": opt2.sustained_safe_until_horizon,
        "budget_5_fixed_sustained": fixed2.sustained_safe_until_horizon,
    }


CHECKS = [
    ("hand_arithmetic", check_hand_arithmetic),
    ("own_bounds_infeasibility", check_own_bounds_infeasibility),
    ("budget_infeasibility", check_budget_infeasibility),
    ("feasible_case_against_hand_derived_optimum", check_feasible_case_against_hand_derived_optimum),
    ("three_way_comparison", check_three_way_comparison),
    ("scope_violation_guards", check_scope_violation_guards),
    ("instantaneous_safety_is_not_trajectory_safety", check_instantaneous_safety_is_not_trajectory_safety),
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json-out", type=Path, default=Path(__file__).with_name("verify_coupled_buffer_cbf_qp_results.json"))
    args = parser.parse_args()

    report = {
        "package": "CAPABILITY_EXPANSION_ROADMAP.md Priority 5 (coupled buffer CBF-QP)",
        "source": SOURCE,
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
