"""H5 verification: integrated buffer pilot (K5 continuous case).

K5's exact table ((0,2)->u=(1,0) cost 1, (1,1)->u=(0,0) cost 0,
(2,0)->u=(0,1) cost 1), the B=1-impossible/B=2-possible shared-
intervention result, and the three information-mode worst-case costs
(A=2, B=1, C=1) were independently re-derived by hand before this file
was written (see `EPISTEMIC_AUDIT_ROADMAP.md` H0 section) and match the
plan's stated reference values exactly.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from scoped_correspondence.errors import ScopeViolationError
from scoped_correspondence.validation.epistemic_buffer_pilot import (
    K5_FIBER_STATES,
    evaluate_information_modes,
    minimal_uniform_intervention,
    sign_based_policy,
    statewise_minimal_intervention,
)
from scoped_correspondence.viability.coupled_buffer_cbf_qp import (
    BufferSpec,
    sustained_safety_over_horizon,
)


def require(condition, msg=""):
    if not condition:
        raise AssertionError(msg)


def check_statewise_minimal_intervention_matches_plan_table():
    """(0,2)->u=(1,0) cost 1; (1,1)->u=(0,0) cost 0; (2,0)->u=(0,1)
    cost 1 -- exactly the plan's hand-derived table."""
    expected = {(0.0, 2.0): ((1.0, 0.0), 1.0), (1.0, 1.0): ((0.0, 0.0), 0.0), (2.0, 0.0): ((0.0, 1.0), 1.0)}
    results = {}
    for state, (exp_u, exp_cost) in expected.items():
        outcome = statewise_minimal_intervention(state, budget=2.0)
        require(not outcome.infeasible_problem, f"{state}: must be feasible at budget=2")
        require(
            all(abs(a - b) < 1e-6 for a, b in zip(outcome.u, exp_u)),
            f"{state}: expected u={exp_u}, got {outcome.u}",
        )
        require(abs(outcome.cost - exp_cost) < 1e-6, f"{state}: expected cost={exp_cost}, got {outcome.cost}")
        require(outcome.sustained_safe_until_horizon, f"{state}: statewise-minimal intervention must be sustained-safe")
        results[str(state)] = {"u": outcome.u, "cost": outcome.cost}
    return results


def check_uniform_budget1_impossible_budget2_possible():
    """No shared u with u1+u2<=1 can be sustained-safe for ALL three
    fiber states; the closed-form minimal uniform intervention needs
    exactly budget 2, and it IS sustained-safe for all three."""
    u_min = minimal_uniform_intervention(K5_FIBER_STATES)
    require(abs(sum(u_min) - 2.0) < 1e-9, f"minimal uniform intervention must need budget exactly 2, got {sum(u_min)}")
    require(abs(u_min[0] - 1.0) < 1e-9 and abs(u_min[1] - 1.0) < 1e-9, f"expected u=(1,1), got {u_min}")

    for state in K5_FIBER_STATES:
        buffers = (BufferSpec(drain=1.0, x=state[0], u_min=0.0, u_max=1.0), BufferSpec(drain=1.0, x=state[1], u_min=0.0, u_max=1.0))
        ok, _ = sustained_safety_over_horizon(list(buffers), list(u_min), 1.0)
        require(ok, f"the closed-form minimal uniform intervention must be sustained-safe at {state}, but was not")

    # Now show every candidate uniform intervention with u1+u2<=1 (a fine
    # grid over the admissible box) fails for at least one fiber state --
    # an exhaustive grid check, not a proof, but corroborates the plan's
    # exact argument (u1>=1 from (0,2) AND u2>=1 from (2,0) forces
    # u1+u2>=2) without relying on it alone.
    import itertools
    n_grid = 21
    any_uniform_solution_at_budget1 = False
    for i, j in itertools.product(range(n_grid), repeat=2):
        u1 = i / (n_grid - 1)
        u2 = j / (n_grid - 1)
        if u1 + u2 > 1.0 + 1e-9:
            continue
        all_states_ok = True
        for state in K5_FIBER_STATES:
            buffers = (BufferSpec(drain=1.0, x=state[0], u_min=0.0, u_max=1.0), BufferSpec(drain=1.0, x=state[1], u_min=0.0, u_max=1.0))
            ok, _ = sustained_safety_over_horizon(list(buffers), [u1, u2], 1.0)
            if not ok:
                all_states_ok = False
                break
        if all_states_ok:
            any_uniform_solution_at_budget1 = True
            break
    require(not any_uniform_solution_at_budget1, "no grid point with u1+u2<=1 should be uniformly sustained-safe")
    return {"minimal_uniform_u": u_min, "minimal_uniform_budget": sum(u_min)}


def check_minimal_uniform_intervention_infeasible_beyond_box():
    """If the box bound u_max is too small to ever cover the fiber's own
    worst-case requirement, minimal_uniform_intervention must raise, not
    silently clip or return a wrong answer."""
    try:
        minimal_uniform_intervention(K5_FIBER_STATES, u_max=0.5)
        raise AssertionError("u_max=0.5 must be infeasible for a fiber that needs u_i=1 at some index")
    except ScopeViolationError:
        pass
    return {"raised": True}


def check_sign_based_policy_matches_statewise_and_uniform_costs():
    """Mode B (sign(x1-x2)) reproduces exactly the plan's per-state
    minimal interventions in THIS example, and its worst-case cost (1)
    matches full-state observation (mode C), strictly better than
    no-observation uniform (mode A, cost 2)."""
    expected_u = {(0.0, 2.0): (1.0, 0.0), (1.0, 1.0): (0.0, 0.0), (2.0, 0.0): (0.0, 1.0)}
    for state, exp_u in expected_u.items():
        u = sign_based_policy(state)
        require(u == exp_u, f"{state}: sign-based policy expected {exp_u}, got {u}")
        buffers = (BufferSpec(drain=1.0, x=state[0], u_min=0.0, u_max=1.0), BufferSpec(drain=1.0, x=state[1], u_min=0.0, u_max=1.0))
        ok, _ = sustained_safety_over_horizon(list(buffers), list(u), 1.0)
        require(ok, f"sign-based policy at {state} must be sustained-safe")
    return {"per_state_u": {str(k): v for k, v in expected_u.items()}}


def check_four_information_modes_table():
    """Followup-Review-Fix R8a (SCF_REVIEW_H0_H7_9dde420.md): the plan's
    THREE required modes are sum-only, sum+minimum, sum+sign -- not
    sum-only/sign/full-state. Sum-only (A) needs worst-case cost 2;
    sum+minimum (B) does NOT improve on that worst case (the {(0,2),(2,0)}
    group at min=0 still needs a uniform budget of 2); sum+sign (C) drops
    the worst case to 1. D (full state) is kept only as an optional extra
    comparison, per the review's explicit allowance."""
    modes = evaluate_information_modes()
    require(
        set(modes.keys()) == {"A_sum_only", "B_sum_and_minimum", "C_sum_and_sign", "D_full_state_statewise_optional_extra"},
        f"unexpected mode keys: {sorted(modes.keys())}",
    )

    mode_a = modes["A_sum_only"]
    require(abs(mode_a.worst_case_cost - 2.0) < 1e-9, f"mode A worst-case cost must be 2, got {mode_a.worst_case_cost}")
    require(all(mode_a.per_state_sustained_safe), "mode A must be sustained-safe at every fiber state")

    mode_b = modes["B_sum_and_minimum"]
    require(abs(mode_b.worst_case_cost - 2.0) < 1e-9, f"mode B (sum+minimum) must NOT improve the worst case -- still 2, got {mode_b.worst_case_cost}")
    require(all(mode_b.per_state_sustained_safe), "mode B must be sustained-safe at every fiber state")
    per_state_b = dict(mode_b.per_state_u)
    require(tuple(per_state_b[(1.0, 1.0)]) == (0.0, 0.0), f"the min=1 group (1,1) must resolve to the zero-cost action, got {per_state_b[(1.0, 1.0)]}")
    require(sum(per_state_b[(0.0, 2.0)]) == 2.0 and per_state_b[(0.0, 2.0)] == per_state_b[(2.0, 0.0)],
            "the min=0 group {(0,2),(2,0)} must share ONE uniform budget-2 action, not be resolved individually")

    mode_c = modes["C_sum_and_sign"]
    require(abs(mode_c.worst_case_cost - 1.0) < 1e-9, f"mode C (sum+sign) worst-case cost must be 1, got {mode_c.worst_case_cost}")
    require(all(mode_c.per_state_sustained_safe), "mode C must be sustained-safe at every fiber state")

    mode_d = modes["D_full_state_statewise_optional_extra"]
    require(abs(mode_d.worst_case_cost - 1.0) < 1e-9, f"mode D (optional, full state) worst-case cost must be 1, got {mode_d.worst_case_cost}")
    require(all(mode_d.per_state_sustained_safe), "mode D must be sustained-safe at every fiber state")

    require(mode_a.worst_case_cost > mode_c.worst_case_cost, "sum-only must be strictly worse than sum+sign")
    require(abs(mode_a.worst_case_cost - mode_b.worst_case_cost) < 1e-9, "sum+minimum must tie with sum-only's worst case in THIS example (it does not help)")
    require(abs(mode_c.worst_case_cost - mode_d.worst_case_cost) < 1e-9, "sum+sign and full-state must tie in THIS example")
    return {"A": mode_a.worst_case_cost, "B": mode_b.worst_case_cost, "C": mode_c.worst_case_cost, "D": mode_d.worst_case_cost}


def check_reused_functions_are_the_existing_unmodified_ones():
    """Sanity: the pilot's `sustained_safety_over_horizon` import IS the
    same function object as the one already independently verified in
    `verify_coupled_buffer_cbf_qp.py` -- no shadowing, no local
    reimplementation."""
    import scoped_correspondence.validation.epistemic_buffer_pilot as pilot_module
    import scoped_correspondence.viability.coupled_buffer_cbf_qp as viability_module
    require(
        pilot_module.sustained_safety_over_horizon is viability_module.sustained_safety_over_horizon,
        "the pilot must reuse the existing sustained_safety_over_horizon, not a local copy",
    )
    require(
        pilot_module.solve_cbf_qp is viability_module.solve_cbf_qp,
        "the pilot must reuse the existing solve_cbf_qp, not a local copy",
    )
    return {"same_function_objects": True}


CHECKS = [
    check_statewise_minimal_intervention_matches_plan_table,
    check_uniform_budget1_impossible_budget2_possible,
    check_minimal_uniform_intervention_infeasible_beyond_box,
    check_sign_based_policy_matches_statewise_and_uniform_costs,
    check_four_information_modes_table,
    check_reused_functions_are_the_existing_unmodified_ones,
]


def main():
    results = {}
    n_passed = 0
    for check in CHECKS:
        name = check.__name__.removeprefix("check_")
        try:
            results[name] = check()
            print(f"PASS  {name}")
            n_passed += 1
        except AssertionError as e:
            results[name] = {"error": str(e)}
            print(f"FAIL  {name}: {e}")
        except Exception as e:
            results[name] = {"error": f"{type(e).__name__}: {e}"}
            print(f"ERROR {name}: {type(e).__name__}: {e}")
    print(f"\n{n_passed}/{len(CHECKS)} checks passed")
    out_path = Path(__file__).with_name("verify_epistemic_buffer_pilot_results.json")
    out_path.write_text(json.dumps({"n_passed": n_passed, "n_total": len(CHECKS), "results": results}, indent=2, default=str))
    print(f"Report written to {out_path}")
    return 0 if n_passed == len(CHECKS) else 1


if __name__ == "__main__":
    raise SystemExit(main())
