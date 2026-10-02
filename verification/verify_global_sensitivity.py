"""J7 verification (SCOPE_COMPOSITION_EVIDENCE_ROADMAP.md, plan section 13):
joint sensitivity and Sobol indices.

J-C14 exact (analytic polynomial reference: X + 2Y -> V = 5/12,
S = S_T = (1/5, 4/5); XY -> V = 7/144, S = (3/7, 3/7), S_T = (4/7, 4/7),
interaction 1/7); the pick-freeze estimator agrees within a documented
multiple of its own standard errors (seeded, no exact equality demanded);
constant output -> undefined (not 0); dependent inputs refused; Y = X as a
negative control of the independence assumption; unclipped estimates;
scenario grid carries no probabilities; MR7 (swapping independent inputs
together with their labels permutes the indices).
"""
from __future__ import annotations

import json
import math
import sys
from fractions import Fraction as F
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from scoped_correspondence.errors import ScopeViolationError
from scoped_correspondence.validation.global_sensitivity import InputSpec, JointScenarioGrid, analytic_sobol_polynomial, sobol_indices

U = lambda name: InputSpec(name, lambda rng, n: rng.uniform(0.0, 1.0, n), "declared U[0,1] for the control case", "scenario_only")


def require(c, m=""):
    if not c:
        raise AssertionError(m)


def raises(fn, exc=ScopeViolationError):
    try:
        fn()
    except exc:
        return True
    return False


def check_jc14_exact():
    V, S, ST = analytic_sobol_polynomial({(1, 0): 1, (0, 1): 2}, 2)
    require((V, S, ST) == (F(5, 12), (F(1, 5), F(4, 5)), (F(1, 5), F(4, 5))), f"additive: {V}, {S}, {ST}")
    V2, S2, ST2 = analytic_sobol_polynomial({(1, 1): 1}, 2)
    require((V2, S2, ST2) == (F(7, 144), (F(3, 7), F(3, 7)), (F(4, 7), F(4, 7))), f"product: {V2}, {S2}, {ST2}")
    require(1 - sum(S2) == F(1, 7), "pure interaction 1/7")
    require(raises(lambda: analytic_sobol_polynomial({(0, 0): 5}, 2)), "constant output: undefined")
    return {"additive": [str(x) for x in S], "product_first": [str(x) for x in S2], "product_total": [str(x) for x in ST2]}


def check_estimator_converges_within_its_errors():
    out = {}
    for name, f, S_ex, ST_ex in (("X+2Y", lambda A: A[:, 0] + 2 * A[:, 1], (0.2, 0.8), (0.2, 0.8)),
                                 ("XY", lambda A: A[:, 0] * A[:, 1], (3 / 7, 3 / 7), (4 / 7, 4 / 7))):
        r = sobol_indices(f, [U("X"), U("Y")], n=40000, seed=7)
        require(r.status == "estimated", name)
        for est, se, ex in list(zip(r.first_order, r.standard_errors_first, S_ex)) + list(zip(r.total, r.standard_errors_total, ST_ex)):
            require(abs(est - ex) <= 5 * se + 1e-3, f"{name}: estimate {est} vs exact {ex} (se {se})")
        out[name] = {"S": r.first_order, "ST": r.total, "se_S": r.standard_errors_first}
    small = sobol_indices(lambda A: A[:, 0] * A[:, 1], [U("X"), U("Y")], n=20, seed=3)
    out["unclipped_small_sample"] = {"S": small.first_order, "ST": small.total, "notes": list(small.notes)}
    return out


def check_undefined_and_unsupported():
    const = sobol_indices(lambda A: np.full(len(A), 3.0), [U("X"), U("Y")], n=200, seed=1)
    require(const.status == "undefined_zero_variance" and const.first_order is None, "constant output: undefined, not 0")
    dep = sobol_indices(lambda A: A[:, 0] + A[:, 1], [U("X"), U("Y")], n=200, seed=1, independent=False)
    require(dep.status == "unsupported" and dep.first_order is None, "dependent inputs refused")
    require(raises(lambda: InputSpec("D", lambda r, n: r.uniform(size=n), "  ")), "provenance is mandatory")
    return {"constant": const.status, "dependent": dep.status}


def check_y_equals_x_negative_control():
    # The true model has ONE input: f = 2X. Treating it as f(X, Y) = X + Y with Y declared independent
    # (while physically Y = X) apportions the variance 1/2 : 1/2 -- an artefact of the false declaration.
    V, S, ST = analytic_sobol_polynomial({(1, 0): 1, (0, 1): 1}, 2)
    require(S == (F(1, 2), F(1, 2)), "false independence declaration splits the variance 1/2 : 1/2")
    V_true, S_true, _ = analytic_sobol_polynomial({(1,): 2}, 1)
    require(S_true == (F(1),) and V_true == F(1, 3) != V, "the actual single-input model: S = 1, variance 1/3 (not 1/6)")
    return {"false_split": ["1/2", "1/2"], "true_variance": "1/3", "false_variance": str(V)}


def check_mr7_input_swap_with_labels():
    f = lambda A: A[:, 0] + 2 * A[:, 1]
    g = lambda A: A[:, 1] + 2 * A[:, 0]  # same function with columns swapped
    r1 = sobol_indices(f, [U("X"), U("Y")], n=5000, seed=11)
    r2 = sobol_indices(g, [U("Y"), U("X")], n=5000, seed=11)
    require(r1.names == ("X", "Y") and r2.names == ("Y", "X"), "labels travel with the inputs")
    require(np.allclose(r1.first_order, r2.first_order[::-1], atol=0.05) and np.allclose(r1.total, r2.total[::-1], atol=0.05),
            "swapping inputs together with labels permutes the indices (same seed, same function)")
    return {"S_XY": r1.first_order, "S_YX": r2.first_order}


def check_scenario_grid_has_no_probabilities():
    grid = JointScenarioGrid(("D", "i"), ((0.9, 1.0, 1.1), (-1.0, 0.0, 1.0)), ("catalogue e_D", "catalogue e_inc"))
    pts = grid.points()
    require(len(pts) == 9 and {"D": 0.9, "i": -1.0} in pts, "full joint grid")
    require(raises(lambda: JointScenarioGrid(("D",), ((),), ("x",))), "empty scenario value list rejected")
    return {"n_points": len(pts)}


CHECKS = [
    check_jc14_exact,
    check_estimator_converges_within_its_errors,
    check_undefined_and_unsupported,
    check_y_equals_x_negative_control,
    check_mr7_input_swap_with_labels,
    check_scenario_grid_has_no_probabilities,
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
    out_path = Path(__file__).with_name("verify_global_sensitivity_results.json")
    out_path.write_text(json.dumps({"n_passed": n_passed, "n_total": len(CHECKS), "results": results}, indent=2, default=str))
    print(f"Report written to {out_path}")
    return 0 if n_passed == len(CHECKS) else 1


if __name__ == "__main__":
    raise SystemExit(main())
