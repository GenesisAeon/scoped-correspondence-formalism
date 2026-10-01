"""J11 verification (SCOPE_COMPOSITION_EVIDENCE_ROADMAP.md, plan section 17):
existing Markov reduction bounds (closure/error_bounds.py) as contracts.

Pflichtprüfungen: J-C22 (L1 11/50 <= 2/5, TV 11/100 <= 1/5), L1/TV factor,
orientation of all matrices, stochastic lifting conditions, initial error,
mismatched time scales, incompatible intermediate states, existing
numerical bound vs rigorous (exact) bound; plus one existing real
reduction case (paper_example_matrices, 3 -> 2 states) with a complete
contract and an observation link composed through J4.

Expected values from verification/plan_controls/j_series_independent_controls.py.
"""
from __future__ import annotations

import json
import sys
from fractions import Fraction as F
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from scoped_correspondence.closure.contract_adapter import (
    ReductionContract,
    observation_link,
    reduction_contract_report,
    reduction_link,
)
from scoped_correspondence.closure.error_bounds import paper_example_matrices
from scoped_correspondence.correspondence.composition import compose_correspondences
from scoped_correspondence.errors import ScopeViolationError

P_C22 = [[F(4, 5), F(1, 5)], [F(1, 10), F(9, 10)]]
Q_C22 = [[F(7, 10), F(3, 10)], [F(1, 5), F(4, 5)]]
I2 = [[1, 0], [0, 1]]


def require(c, m=""):
    if not c:
        raise AssertionError(m)


def raises(fn, exc=(ScopeViolationError, ValueError)):
    try:
        fn()
    except exc:
        return True
    return False


def c22(norm="L1", **kw):
    return ReductionContract("jc22", ("s0", "s1"), ("s0", "s1"), "steps", False, 2, norm, **kw)


def check_jc22_l1_and_tv():
    l1 = reduction_contract_report(Q_C22, I2, P_C22, [1, 0], [1, 0], c22())
    require(l1.report.verdict == "proved" and l1.exact_bound == F(2, 5), f"L1 bound 2/5, got {l1.exact_bound}")
    require(l1.report.values["residual_inf_norm"] == F(1, 5) and l1.observed_error_l1 == F(11, 50), "||Q-P||inf = 1/5, error 11/50")
    tv = reduction_contract_report(Q_C22, I2, P_C22, [1, 0], [1, 0], c22("TV"))
    require(tv.exact_bound == F(1, 5) and tv.observed_error_l1 == F(11, 100), f"TV bound 1/5, TV error 11/100, got {tv.exact_bound}, {tv.observed_error_l1}")
    require(abs(l1.float_bound - 0.4) < 1e-12 and abs(tv.float_bound - 0.2) < 1e-12, "existing float function agrees")
    require(l1.report.arithmetic == "exact_rational" and not l1.notes[1:], f"no float/exact disagreement: {l1.notes}")
    return {"l1": str(l1.exact_bound), "tv": str(tv.exact_bound), "observed_l1": str(l1.observed_error_l1)}


def _paper():
    P, A, Pi = paper_example_matrices()
    P = [[F(int(round(v * 4)), 4) for v in row] for row in P]
    A = [[F(int(round(v * 2)), 2) for v in row] for row in A]
    Pi = [[F(int(round(v * 8)), 8) for v in row] for row in Pi]
    return P, A, Pi


PAPER = ReductionContract("paper_3to2", ("x1", "x2", "x3"), ("u", "v"), "steps", False, 4)


def check_existing_reduction_case_full_contract():
    P, A, Pi = _paper()
    p0 = [sum(F(1) * A[0][j] for _ in [0]) for j in range(3)]  # pi0 A with pi0 = (1, 0)
    rep = reduction_contract_report(Pi, A, P, [1, 0], p0, PAPER)
    require(rep.report.verdict == "proved", f"paper example must be proved: {rep.report.reasons}")
    require(rep.report.values["residual_inf_norm"] == F(1, 4) and rep.exact_bound == 1, f"||Pi A - A P||inf = 1/4, bound k/4 = 1, got {rep.exact_bound}")
    require(rep.observed_error_l1 is not None and rep.observed_error_l1 <= rep.exact_bound, "exact error stays below the bound")
    require(any("row-stochastic (each reduced state" in h for h in rep.hypotheses), "stochastic lifting recorded as satisfied")
    return {"bound": str(rep.exact_bound), "observed": str(rep.observed_error_l1), "hypotheses": list(rep.hypotheses)}


def check_composed_observation_link():
    P, A, Pi = _paper()
    p0 = [A[0][j] for j in range(3)]
    rep = reduction_contract_report(Pi, A, P, [1, 0], p0, PAPER)
    red = reduction_link(PAPER, A, rep, model_full="chain3", model_reduced="chain2")
    obs = observation_link(PAPER, [0, 1, 2], model_full="chain3", observable="mean_index")
    comp = compose_correspondences(red, obs)
    require(comp.status == "composed" and comp.flow_bound_report.verdict == "proved", f"composition must succeed: {comp.reasons}")
    require(comp.link.flow_error_bound == 2, f"|f.e| <= max|f| * bound = 2 * 1 = 2, got {comp.link.flow_error_bound}")
    # exact observable error at k = 4 must respect the composed bound
    def vm(v, m):
        return [sum(v[i] * m[i][j] for i in range(len(v))) for j in range(len(m[0]))]
    pk, pik = list(p0), [F(1), F(0)]
    for _ in range(4):
        pk, pik = vm(pk, P), vm(pik, Pi)
    lifted = vm(pik, A)
    obs_err = abs(sum(f * (a - b) for f, a, b in zip([0, 1, 2], pk, lifted)))
    require(obs_err <= comp.link.flow_error_bound, f"observable error {obs_err} must not exceed {comp.link.flow_error_bound}")
    other_clock = observation_link(ReductionContract("x", PAPER.full_states, PAPER.reduced_states, "time:h", True, 4), [0, 1, 2],
                                   model_full="chain3", observable="mean_index")
    require(compose_correspondences(red, other_clock).status == "incompatible", "mismatched time scales must not compose")
    other_states = observation_link(ReductionContract("y", ("a", "b", "c"), PAPER.reduced_states, "steps", False, 4), [0, 1, 2],
                                    model_full="chain3", observable="mean_index")
    require(compose_correspondences(red, other_states).status == "incompatible", "incompatible intermediate states must not compose")
    return {"composed_bound": str(comp.link.flow_error_bound), "observable_error": str(obs_err)}


def check_orientation_errors_detected():
    PT = [[P_C22[j][i] for j in range(2)] for i in range(2)]
    rep = reduction_contract_report(Q_C22, I2, PT, [1, 0], [1, 0], c22())
    require(rep.report.procedure_status == "invalid_input" and any("transposed" in v for v in rep.violations),
            f"a transposed full matrix must be flagged as an orientation problem: {rep.violations}")
    A_wrong = [[1, 0, 0], [0, 1, 0]]  # 2x3 given where full=2, reduced=3 would be needed
    bad = reduction_contract_report(Q_C22, A_wrong, P_C22, [1, 0], [1, 0], c22())
    require(bad.report.procedure_status == "invalid_input" and any("lifting A" in v for v in bad.violations), "lifting shape mismatch")
    return {"violations": list(rep.violations)}


def check_lifting_conditions_and_tv_factor():
    A_nonstoch = [[F(1, 2), 0], [0, 1]]
    l1 = reduction_contract_report(Q_C22, A_nonstoch, P_C22, [1, 0], [F(1, 2), 0], c22())
    require(l1.report.verdict == "proved", "Thm 4.3 L1 bound does not need a stochastic lifting")
    require(not any("lifting A is row-stochastic" in h for h in l1.hypotheses), "non-stochastic lifting must not be recorded as stochastic")
    tv = reduction_contract_report(Q_C22, A_nonstoch, P_C22, [1, 0], [F(1, 2), 0], c22("TV"))
    require(tv.report.procedure_status == "invalid_input" and any("TV = L1/2" in v for v in tv.violations),
            "TV is refused without probability-vector differences")
    full = reduction_contract_report(Q_C22, I2, P_C22, [1, 0], [1, 0], c22())
    half = reduction_contract_report(Q_C22, I2, P_C22, [1, 0], [1, 0], c22("TV"))
    require(half.exact_bound * 2 == full.exact_bound, "TV bound is exactly half the L1 bound")
    return {"tv_refused": True}


def check_initial_error_enters_exactly():
    rep = reduction_contract_report(Q_C22, I2, P_C22, [1, 0], [0, 1], c22())
    require(rep.report.values["initial_error_l1"] == 2 and rep.exact_bound == 2 + F(2, 5), f"e0 = 2, bound 12/5, got {rep.exact_bound}")
    require(rep.observed_error_l1 <= rep.exact_bound, "observed error within bound")
    return {"bound": str(rep.exact_bound)}


def check_time_scale_and_input_validation():
    require(raises(lambda: ReductionContract("x", ("a",), ("a",), "steps", True, 1)), "CTMC with 'steps' clock is an input error")
    require(raises(lambda: ReductionContract("x", ("a",), ("a",), "time:h", False, 1)), "DTMC with continuous clock is an input error")
    require(raises(lambda: ReductionContract("x", ("a",), ("a",), "steps", False, F(3, 2))), "non-integer DTMC horizon")
    G = [[F(-1), F(1)], [F(2), F(-2)]]
    T = [[F(-1), F(1)], [F(1), F(-1)]]
    ct = ReductionContract("ctmc", ("a", "b"), ("a", "b"), "time:h", True, F(1, 2))
    rep = reduction_contract_report(T, I2, G, [1, 0], [1, 0], ct)
    require(rep.report.verdict == "proved" and rep.exact_bound == F(1, 2) * 2, f"CTMC: t * ||T - G||inf = 1/2 * 2 = 1, got {rep.exact_bound}")
    require(abs(rep.float_bound - 1.0) < 1e-12, "existing CTMC float bound agrees")
    return {"ctmc_bound": str(rep.exact_bound)}


def check_numerical_bound_is_not_a_proof():
    Pf = [[0.8, 0.2], [0.1, 0.9]]
    Qf = [[0.7, 0.3], [0.2, 0.8]]
    rep = reduction_contract_report(Qf, [[1.0, 0.0], [0.0, 1.0]], Pf, [1.0, 0.0], [1.0, 0.0], c22())
    require(rep.report.verdict == "undecided" and rep.report.arithmetic == "floating_point_estimate" and rep.exact_bound is None,
            "float inputs: estimate only, never 'proved'")
    require(abs(rep.float_bound - 0.4) < 1e-9, "the existing float bound is still reported")
    require(raises(lambda: reduction_link(c22(), [[1.0, 0.0], [0.0, 1.0]], rep, model_full="a", model_reduced="b")),
            "an unproved bound cannot become a contract flow bound")
    return {"float_bound": rep.float_bound}


CHECKS = [
    check_jc22_l1_and_tv,
    check_existing_reduction_case_full_contract,
    check_composed_observation_link,
    check_orientation_errors_detected,
    check_lifting_conditions_and_tv_factor,
    check_initial_error_enters_exactly,
    check_time_scale_and_input_validation,
    check_numerical_bound_is_not_a_proof,
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
    out_path = Path(__file__).with_name("verify_reduction_contracts_results.json")
    out_path.write_text(json.dumps({"n_passed": n_passed, "n_total": len(CHECKS), "results": results}, indent=2, default=str))
    print(f"Report written to {out_path}")
    return 0 if n_passed == len(CHECKS) else 1


if __name__ == "__main__":
    raise SystemExit(main())
