"""J9 verification, part 1 (SCOPE_COMPOSITION_EVIDENCE_ROADMAP.md, plan §15.1):
finite acyclic SCMs.

J-C18 (observation is not intervention: same observational distribution,
P(Y=1 | do(X=1)) = 1 vs 1/2, TV 1/2; an epistemic fibre over EXACTLY these
two candidates shows the ambiguity without claiming an enumeration of all
causal models); correlated exogenous causes; invalid DAG; undeclared parent
access; mechanism output outside the domain; probabilities not summing to
1 (never normalised); intervention outside the domain; budget abort; MR8
(renaming variables together with the interventions).
"""
from __future__ import annotations

import json
import sys
from fractions import Fraction as F
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from scoped_correspondence.causal.finite_scm import (
    BudgetExceeded,
    FiniteSCM,
    Mechanism,
    independent_exogenous,
    interventional_distribution,
    marginal,
    total_variation,
)
from scoped_correspondence.epistemic.observation_fibers import identified_values, observation_fiber
from scoped_correspondence.epistemic.records import FiniteDomainSpec
from scoped_correspondence.errors import ScopeViolationError

FAIR = {0: F(1, 2), 1: F(1, 2)}


def require(c, m=""):
    if not c:
        raise AssertionError(m)


def raises(fn, exc=(ScopeViolationError,)):
    try:
        fn()
    except exc:
        return True
    return False


def model(y_from: str, names=("X", "Y")):
    xn, yn = names
    un, ud = independent_exogenous(U=FAIR)
    y_mech = (Mechanism((xn,), (), lambda pa, u: pa[xn]) if y_from == "X" else Mechanism((), ("U",), lambda pa, u: u["U"]))
    return FiniteSCM(f"Y={y_from}", (xn, yn), {xn: (0, 1), yn: (0, 1)},
                     {xn: Mechanism((), ("U",), lambda pa, u: u["U"]), yn: y_mech}, un, ud)


def check_jc18_observation_is_not_intervention():
    m1, m2 = model("X"), model("U")
    o1, o2 = interventional_distribution(m1), interventional_distribution(m2)
    require(o1 == o2 == {(0, 0): F(1, 2), (1, 1): F(1, 2)}, "identical observational distributions")
    d1 = marginal(interventional_distribution(m1, {"X": 1}), 1)
    d2 = marginal(interventional_distribution(m2, {"X": 1}), 1)
    require(d1.get(1) == 1 and d2.get(1) == F(1, 2) and total_variation(d1, d2) == F(1, 2), "do(X=1): 1 vs 1/2, TV 1/2")
    models = {"Y=X": m1, "Y=U": m2}
    dom = FiniteDomainSpec("two_candidate_models", tuple(models), "exactly these two candidates", coverage="partial",
                           relationship_to_target_space="restricted_candidates")
    fib = observation_fiber(dom, [], lambda k: tuple(sorted(interventional_distribution(models[k]).items())), tuple(sorted(o1.items())))
    ids = identified_values(fib, lambda k: marginal(interventional_distribution(models[k], {"X": 1}), 1).get(1, F(0)))
    require(fib.n_fiber == 2 and set(ids.values) == {F(1), F(1, 2)} and not ids.point_identified,
            "the fibre over the two listed candidates is ambiguous for the interventional query")
    return {"P_do_x1": ["1", "1/2"], "tv": "1/2", "fibre": "2 listed candidates (no claim about all models)"}


def check_correlated_exogenous_representable():
    names = ("U1", "U2")
    corr = {(0, 0): F(1, 2), (1, 1): F(1, 2)}  # common cause: U1 = U2
    m = FiniteSCM("corr", ("X", "Y"), {"X": (0, 1), "Y": (0, 1)},
                  {"X": Mechanism((), ("U1",), lambda pa, u: u["U1"]), "Y": Mechanism((), ("U2",), lambda pa, u: u["U2"])}, names, corr)
    ind_names, ind = independent_exogenous(U1=FAIR, U2=FAIR)
    m_ind = FiniteSCM("ind", ("X", "Y"), {"X": (0, 1), "Y": (0, 1)},
                      {"X": Mechanism((), ("U1",), lambda pa, u: u["U1"]), "Y": Mechanism((), ("U2",), lambda pa, u: u["U2"])}, ind_names, ind)
    require(interventional_distribution(m) == {(0, 0): F(1, 2), (1, 1): F(1, 2)}, "correlated exogenous: X = Y always")
    require(len(interventional_distribution(m_ind)) == 4, "independent version differs -- independence is not assumed silently")
    return {"correlated_support": 2, "independent_support": 4}


def check_validation_errors():
    un, ud = independent_exogenous(U=FAIR)
    cyc = lambda: FiniteSCM("c", ("X", "Y"), {"X": (0, 1), "Y": (0, 1)},
                            {"X": Mechanism(("Y",), (), lambda pa, u: pa["Y"]), "Y": Mechanism(("X",), (), lambda pa, u: pa["X"])}, un, ud)
    require(raises(cyc), "cycle rejected (not a DAG)")
    sneaky = FiniteSCM("s", ("X", "Y"), {"X": (0, 1), "Y": (0, 1)},
                       {"X": Mechanism((), ("U",), lambda pa, u: u["U"]), "Y": Mechanism((), ("U",), lambda pa, u: pa["X"])}, un, ud)
    require(raises(lambda: interventional_distribution(sneaky)), "reading an undeclared parent is rejected")
    out = FiniteSCM("o", ("X",), {"X": (0, 1)}, {"X": Mechanism((), ("U",), lambda pa, u: u["U"] + 5)}, un, ud)
    require(raises(lambda: interventional_distribution(out)), "mechanism output outside the domain rejected")
    require(raises(lambda: FiniteSCM("p", ("X",), {"X": (0, 1)}, {"X": Mechanism((), ("U",), lambda pa, u: u["U"])}, ("U",),
                                     {(0,): F(1, 2), (1,): F(1, 3)})), "probabilities summing to 5/6 are an error, never normalised")
    require(raises(lambda: FiniteSCM("q", ("X",), {"X": (0, 1)}, {"X": Mechanism((), ("U",), lambda pa, u: u["U"])}, ("U",),
                                     {(0,): 0.5, (1,): 0.5})), "float probabilities rejected (exactness)")
    require(raises(lambda: interventional_distribution(model("X"), {"X": 2})), "intervention value outside the domain")
    require(raises(lambda: interventional_distribution(model("X"), {"Z": 1})), "intervention on an unknown variable")
    return {"validation": "ok"}


def check_budget_abort():
    names, dist = independent_exogenous(**{f"U{i}": FAIR for i in range(6)})  # 64 combinations
    m = FiniteSCM("b", ("X",), {"X": (0, 1)}, {"X": Mechanism((), ("U0",), lambda pa, u: u["U0"])}, names, dist)
    require(raises(lambda: interventional_distribution(m, budget=10), (BudgetExceeded,)), "budget abort raises, no conclusion")
    return {"combinations": 64, "budget": 10}


def check_mr8_renaming_invariance():
    a, b = model("X"), model("X", names=("A", "B"))
    for do_x, do_a in (({}, {}), ({"X": 1}, {"A": 1}), ({"Y": 0}, {"B": 0})):
        require(interventional_distribution(a, do_x) == interventional_distribution(b, do_a), "renaming variables with interventions changes nothing")
    return {"cases": 3}


CHECKS = [
    check_jc18_observation_is_not_intervention,
    check_correlated_exogenous_representable,
    check_validation_errors,
    check_budget_abort,
    check_mr8_renaming_invariance,
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
    out_path = Path(__file__).with_name("verify_finite_causal_models_results.json")
    out_path.write_text(json.dumps({"n_passed": n_passed, "n_total": len(CHECKS), "results": results}, indent=2, default=str))
    print(f"Report written to {out_path}")
    return 0 if n_passed == len(CHECKS) else 1


if __name__ == "__main__":
    raise SystemExit(main())
