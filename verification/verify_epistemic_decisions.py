"""H4 verification: finite decisions under declared uncertainty (K5, K6).

K5 (fiber F(2)={(0,2),(1,1),(2,0)}, safety min{x_i(0), x_i(0)+u_i-1}>=0,
u1+u2<=B: every state individually controllable at B=1, but a SHARED
intervention needs B=2) and K6 (loss table: action A=[0,10] max_loss=10
max_regret=4, action B=[6,6] max_loss=6 max_regret=6 -- minimax picks B,
minimax-regret picks A; expected-loss crossover exactly at p=0.6) were
independently re-derived by hand before this file was written (see
`EPISTEMIC_AUDIT_ROADMAP.md` H0 section) and match the plan's stated
reference values exactly.

K5's finite reproduction here uses the discrete action set {0,1}^2 (the
plan's own minimal-cost table only ever needs 0/1 components) and reuses
the EXACT SAME fiber F(2) as K4 (`verify_epistemic_identification.py`)
via `observation_fiber` -- the plan explicitly notes K5 shares K4's
fiber.
"""
from __future__ import annotations

import itertools
import json
import sys
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from scoped_correspondence.epistemic.decisions import compare_decisions, uniform_safe_actions
from scoped_correspondence.epistemic.observation_fibers import observation_fiber
from scoped_correspondence.epistemic.records import FiniteDomainSpec
from scoped_correspondence.errors import ScopeViolationError


def require(condition, msg=""):
    if not condition:
        raise AssertionError(msg)


def _k5_fiber():
    """The exact same F(2) fiber as K4: X={0,1,2}^2, h=x1+x2, y=2."""
    domain = FiniteDomainSpec(id="k5_reserves", candidates=tuple(itertools.product(range(3), repeat=2)), scope_text="X={0,1,2}^2")
    return observation_fiber(domain, [], lambda x: x[0] + x[1], 2)


def _k5_safety(w, u):
    x1, x2 = w
    u1, u2 = u
    need1 = 1 if x1 == 0 else 0
    need2 = 1 if x2 == 0 else 0
    return u1 >= need1 and u2 >= need2


def check_k5_statewise_feasible_but_not_uniform_at_budget1():
    """At budget B=1 (actions (0,0),(1,0),(0,1)) every state in the fiber
    is INDIVIDUALLY controllable, but no single shared action serves all
    three -- U_uniform(F) is empty."""
    fiber = _k5_fiber()
    actions_b1 = [(0, 0), (1, 0), (0, 1)]
    report = uniform_safe_actions(fiber, actions_b1, _k5_safety)
    require(report.statewise_feasible, "every state must be individually controllable at budget 1")
    require(not report.uniformly_feasible, "no shared budget-1 action can serve all three states")
    require(report.uniform_safe_actions == (), "U_uniform(F) must be empty at budget 1")
    require(len(report.notes) > 0, "the statewise-but-not-uniform gap must be explicitly noted")
    per_state = dict(report.per_state_safe_actions)
    require(set(per_state[(0, 2)]) == {(1, 0)}, f"(0,2) needs u1=1, got {per_state[(0, 2)]}")
    require(set(per_state[(1, 1)]) == {(0, 0), (1, 0), (0, 1)}, f"(1,1) is safe under any budget-1 action, got {per_state[(1, 1)]}")
    require(set(per_state[(2, 0)]) == {(0, 1)}, f"(2,0) needs u2=1, got {per_state[(2, 0)]}")
    return {"statewise_feasible": report.statewise_feasible, "uniformly_feasible": report.uniformly_feasible}


def check_k5_uniform_feasible_at_budget2():
    """Adding the budget-2 action (1,1) makes the fiber uniformly
    feasible: U_uniform(F)={(1,1)}, exactly matching the plan's
    u1+u2>=2 impossibility-at-B=1 / possibility-at-B=2 result."""
    fiber = _k5_fiber()
    actions_b2 = [(0, 0), (1, 0), (0, 1), (1, 1)]
    report = uniform_safe_actions(fiber, actions_b2, _k5_safety)
    require(report.statewise_feasible, "statewise feasibility must still hold with a larger action set")
    require(report.uniformly_feasible, "budget 2 must make the fiber uniformly feasible")
    require(report.uniform_safe_actions == ((1, 1),), f"U_uniform(F) must be exactly {{(1,1)}}, got {report.uniform_safe_actions}")
    return {"uniform_safe_actions": report.uniform_safe_actions}


def check_empty_and_incomplete_fiber_never_vacuously_feasible():
    """An empty fiber (y=6 is unreachable) and an incomplete scan
    (budget cut short) must both refuse to report feasibility, never
    default to True."""
    domain = FiniteDomainSpec(id="k5b", candidates=tuple(itertools.product(range(3), repeat=2)), scope_text="X={0,1,2}^2")
    empty_fiber = observation_fiber(domain, [], lambda x: x[0] + x[1], 6)
    r_empty = uniform_safe_actions(empty_fiber, [(0, 0), (1, 1)], _k5_safety)
    require(not r_empty.statewise_feasible and not r_empty.uniformly_feasible, "an empty fiber must never be reported as feasible")

    incomplete_fiber = observation_fiber(domain, [], lambda x: x[0] + x[1], 2, budget=1)
    require(not incomplete_fiber.search_complete, "budget=1 must not scan the full 9-candidate domain")
    r_incomplete = uniform_safe_actions(incomplete_fiber, [(0, 0), (1, 1)], _k5_safety)
    require(not r_incomplete.statewise_feasible and not r_incomplete.uniformly_feasible, "an incomplete fiber must never be reported as feasible")
    return {"empty_ok": r_empty.uniformly_feasible, "incomplete_ok": r_incomplete.uniformly_feasible}


def _k6_loss_matrix():
    return {"A": {"s1": 0, "s2": 10}, "B": {"s1": 6, "s2": 6}}


def check_k6_minimax_and_minimax_regret_disagree():
    """Minimax picks B (worst-case loss 6 < 10); minimax-regret picks A
    (worst-case regret 4 < 6) -- the two criteria must NOT be
    interchangeable on the same table."""
    lm = _k6_loss_matrix()
    r_minimax = compare_decisions(lm, criterion="minimax")
    require(r_minimax.chosen_actions == ("B",), f"minimax must choose B alone, got {r_minimax.chosen_actions}")
    scores = dict(r_minimax.scores)
    require(scores["A"] == 10 and scores["B"] == 6, f"minimax scores must be A=10,B=6, got {scores}")

    r_regret = compare_decisions(lm, criterion="minimax_regret")
    require(r_regret.chosen_actions == ("A",), f"minimax_regret must choose A alone, got {r_regret.chosen_actions}")
    regret_scores = dict(r_regret.scores)
    require(regret_scores["A"] == 4 and regret_scores["B"] == 6, f"regret scores must be A=4,B=6, got {regret_scores}")

    require(r_minimax.chosen_actions != r_regret.chosen_actions, "the two criteria must disagree on this table")
    return {"minimax_scores": dict(r_minimax.scores), "regret_scores": dict(r_regret.scores)}


def check_k6_expected_loss_crossover_at_p_0_6():
    """With p=P(s2) as an exact Fraction, the expected-loss decision
    ties exactly at p=3/5=0.6: below it A wins, above it B wins, and at
    the boundary itself both are tied."""
    lm = _k6_loss_matrix()

    below = compare_decisions(lm, criterion="expected_loss", probabilities={"s1": Fraction(41, 100), "s2": Fraction(59, 100)})
    require(below.chosen_actions == ("A",), f"below p=0.6, A must win, got {below.chosen_actions}")

    above = compare_decisions(lm, criterion="expected_loss", probabilities={"s1": Fraction(39, 100), "s2": Fraction(61, 100)})
    require(above.chosen_actions == ("B",), f"above p=0.6, B must win, got {above.chosen_actions}")

    at_boundary = compare_decisions(lm, criterion="expected_loss", probabilities={"s1": Fraction(2, 5), "s2": Fraction(3, 5)})
    require(set(at_boundary.chosen_actions) == {"A", "B"}, f"exactly at p=0.6 both must tie, got {at_boundary.chosen_actions}")
    require(len(at_boundary.notes) > 0, "a tie must be explicitly noted")
    return {"below_p0.6": below.chosen_actions, "above_p0.6": above.chosen_actions, "at_p0.6": at_boundary.chosen_actions}


def check_tie_handling_reports_all_tied_actions():
    """Two actions with identical loss rows must both be reported as
    chosen under minimax -- a tie is never arbitrarily broken."""
    lm = {"A": {"s1": 0, "s2": 10}, "B": {"s1": 6, "s2": 6}, "C": {"s1": 6, "s2": 6}}
    r = compare_decisions(lm, criterion="minimax")
    require(set(r.chosen_actions) == {"B", "C"}, f"B and C must tie under minimax, got {r.chosen_actions}")
    require(len(r.notes) > 0, "a tie must be explicitly noted")
    return {"chosen": sorted(r.chosen_actions)}


def check_loss_matrix_validation_rejects_bad_inputs():
    """Non-finite losses, mismatched state sets across actions, a
    missing probability distribution for expected_loss, and
    probabilities that don't sum to 1 must all raise, never silently
    substitute a default."""
    try:
        compare_decisions({"A": {"s1": float("inf"), "s2": 0}, "B": {"s1": 0, "s2": 0}}, criterion="minimax")
        raise AssertionError("infinite loss must raise ScopeViolationError")
    except ScopeViolationError:
        pass

    try:
        compare_decisions({"A": {"s1": float("nan"), "s2": 0}, "B": {"s1": 0, "s2": 0}}, criterion="minimax")
        raise AssertionError("NaN loss must raise ScopeViolationError")
    except ScopeViolationError:
        pass

    try:
        compare_decisions({"A": {"s1": 0, "s2": 1}, "B": {"s1": 0}}, criterion="minimax")
        raise AssertionError("mismatched state sets must raise ScopeViolationError")
    except ScopeViolationError:
        pass

    try:
        compare_decisions(_k6_loss_matrix(), criterion="expected_loss")
        raise AssertionError("expected_loss without probabilities must raise ScopeViolationError")
    except ScopeViolationError:
        pass

    try:
        compare_decisions(_k6_loss_matrix(), criterion="expected_loss", probabilities={"s1": 0.5, "s2": 0.6})
        raise AssertionError("probabilities not summing to 1 must raise ScopeViolationError")
    except ScopeViolationError:
        pass
    return {"all_rejections_raised": True}


def check_no_uniform_feasible_action_result_is_explicit():
    """When U_uniform(F) is empty, the report says so explicitly
    (`uniformly_feasible=False`, `uniform_safe_actions=()`), and this is
    distinguishable from the empty-fiber case by `fiber_size>0`."""
    fiber = _k5_fiber()
    actions_no_shared_solution = [(0, 0), (1, 0), (0, 1)]
    report = uniform_safe_actions(fiber, actions_no_shared_solution, _k5_safety)
    require(report.fiber_size == 3, "the fiber itself must be nonempty here")
    require(not report.uniformly_feasible and report.uniform_safe_actions == (), "must explicitly report no uniform action")
    return {"fiber_size": report.fiber_size, "uniform_safe_actions": report.uniform_safe_actions}


CHECKS = [
    check_k5_statewise_feasible_but_not_uniform_at_budget1,
    check_k5_uniform_feasible_at_budget2,
    check_empty_and_incomplete_fiber_never_vacuously_feasible,
    check_k6_minimax_and_minimax_regret_disagree,
    check_k6_expected_loss_crossover_at_p_0_6,
    check_tie_handling_reports_all_tied_actions,
    check_loss_matrix_validation_rejects_bad_inputs,
    check_no_uniform_feasible_action_result_is_explicit,
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
    out_path = Path(__file__).with_name("verify_epistemic_decisions_results.json")
    out_path.write_text(json.dumps({"n_passed": n_passed, "n_total": len(CHECKS), "results": results}, indent=2, default=str))
    print(f"Report written to {out_path}")
    return 0 if n_passed == len(CHECKS) else 1


if __name__ == "__main__":
    raise SystemExit(main())
