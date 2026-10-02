"""J9 verification, part 2 (SCOPE_COMPOSITION_EVIDENCE_ROADMAP.md, plan §15.2):
exact interventional abstraction.

J-C19: micro X1 = U1, X2 = U2 (independent fair), Y = X1 xor X2; macro Z fair,
Ybar = Z; tau = (x1 xor x2, y). Declared micro interventions: none + the four
full do(X1=a, X2=b), mapped by a xor b -> all five exact, omega surjective
and order-preserving. Extension do(X1=1) -> do(Z=1): TV 1/2, AND (J0 finding
B3) an order violation; the alternative image 'no intervention' passes both
-- a concrete witness that not every other map fails.
Pflichtprüfungen: swapped variable names, non-surjective map, violated
order, missing intervention, one violating intervention among matching
ones, correlated exogenous causes, budget abort, exact vs numeric
comparison; every result carries its intervention scope.
"""
from __future__ import annotations

import json
import sys
from fractions import Fraction as F
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from scoped_correspondence.causal.abstraction import check_interventional_abstraction, extends, iv
from scoped_correspondence.causal.finite_scm import FiniteSCM, Mechanism, independent_exogenous
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


def micro_model(correlated=False):
    if correlated:
        names, dist = ("U1", "U2"), {(0, 0): F(1, 2), (1, 1): F(1, 2)}
    else:
        names, dist = independent_exogenous(U1=FAIR, U2=FAIR)
    return FiniteSCM("micro", ("X1", "X2", "Y"), {"X1": (0, 1), "X2": (0, 1), "Y": (0, 1)},
                     {"X1": Mechanism((), ("U1",), lambda pa, u: u["U1"]), "X2": Mechanism((), ("U2",), lambda pa, u: u["U2"]),
                      "Y": Mechanism(("X1", "X2"), (), lambda pa, u: pa["X1"] ^ pa["X2"])}, names, dist)


MACRO = FiniteSCM("macro", ("Z", "Ybar"), {"Z": (0, 1), "Ybar": (0, 1)},
                  {"Z": Mechanism((), ("U",), lambda pa, u: u["U"]), "Ybar": Mechanism(("Z",), (), lambda pa, u: pa["Z"])},
                  *independent_exogenous(U=FAIR))
TAU = lambda s: (s[0] ^ s[1], s[2])
MACRO_SET = [iv(), iv(Z=0), iv(Z=1)]
BASE = [(iv(), iv())] + [(iv(X1=a, X2=b), iv(Z=a ^ b)) for a in (0, 1) for b in (0, 1)]


def check_jc19_exact_abstraction():
    r = check_interventional_abstraction(micro_model(), MACRO, TAU, BASE, MACRO_SET)
    require(r.exact_abstraction and r.distributions_match and r.surjective and r.order_preserving, f"five exact interventions: {r}")
    require(len(r.checks) == 5 and all(c.total_variation == 0 for c in r.checks) and len(r.intervention_scope) == 5,
            "every declared intervention checked, scope reported")
    require(r.comparison == "exact", "exact Fraction comparison")
    return {"n_checked": 5, "scope": [list(map(list, s)) for s in r.intervention_scope]}


def check_jc19_failing_extension_and_b3():
    bad = check_interventional_abstraction(micro_model(), MACRO, TAU, BASE + [(iv(X1=1), iv(Z=1))], MACRO_SET)
    ext = [c for c in bad.checks if c.micro == iv(X1=1)][0]
    require(ext.total_variation == F(1, 2) and not bad.distributions_match, "extension: TV 1/2")
    require(not bad.order_preserving and (iv(X1=1), iv(X1=1, X2=1)) in bad.order_violations,
            "J0 B3: do(X1=1) <= do(X1=1,X2=1) -> do(Z=0), but do(Z=1) is not <= do(Z=0)")
    alt = check_interventional_abstraction(micro_model(), MACRO, TAU, BASE + [(iv(X1=1), iv())], MACRO_SET)
    require(alt.exact_abstraction, "alternative image 'no intervention' passes distribution AND order checks")
    require(any("says nothing about other" in n for n in bad.notes), "no claim that every other map fails")
    return {"extension_tv": str(ext.total_variation), "order_violation": True, "alternative_noop_exact": True}


def check_swapped_variable_names():
    # Swapping the two macro coordinates is UNDETECTABLE here by construction: Ybar = Z and
    # Y = X1 xor X2, so both coordinates are always equal. Stated explicitly, not counted as a detection.
    swapped = lambda s: (s[2], s[0] ^ s[1])
    r = check_interventional_abstraction(micro_model(), MACRO, swapped, BASE, MACRO_SET)
    nomatch = [c for c in r.checks if not c.match]
    require(r.distributions_match and not nomatch, "symmetric model: coordinate swap is invisible (documented limitation of this case)")
    tau_wrong = lambda s: (s[0], s[2])  # Z := X1 instead of X1 xor X2 (a name mix-up)
    r2 = check_interventional_abstraction(micro_model(), MACRO, tau_wrong, BASE, MACRO_SET)
    require(not r2.distributions_match, "mixing up which variable feeds Z breaks the abstraction")
    return {"swapped_coordinates_mismatches": len(nomatch), "wrong_variable_mismatches": sum(not c.match for c in r2.checks)}


def check_non_surjective_and_missing():
    omega = [(iv(), iv())] + [(iv(X1=a, X2=b), iv(Z=0)) for a, b in ((0, 0), (1, 1))]
    r = check_interventional_abstraction(micro_model(), MACRO, TAU, omega, MACRO_SET)
    require(not r.surjective and iv(Z=1) in r.unreached_macro and not r.exact_abstraction, "do(Z=1) never reached: not surjective")
    require(raises(lambda: check_interventional_abstraction(micro_model(), MACRO, TAU, [(iv(), iv(Z=2))], MACRO_SET)),
            "mapping outside the declared macro set rejected")
    require(raises(lambda: check_interventional_abstraction(micro_model(), MACRO, TAU, [(iv(), iv()), (iv(), iv(Z=0))], MACRO_SET)),
            "a micro intervention mapped twice rejected")
    return {"unreached": [list(map(list, m)) for m in r.unreached_macro]}


def check_single_violating_intervention():
    omega = list(BASE)
    omega[1] = (omega[1][0], iv(Z=1))  # do(X1=0,X2=0) wrongly mapped to do(Z=1)
    r = check_interventional_abstraction(micro_model(), MACRO, TAU, omega, MACRO_SET)
    require(sum(not c.match for c in r.checks) == 1 and not r.exact_abstraction, "one violating intervention suffices to refute")
    return {"violations": 1}


def check_correlated_exogenous_micro():
    r = check_interventional_abstraction(micro_model(correlated=True), MACRO, TAU, BASE, MACRO_SET)
    noop = [c for c in r.checks if c.micro == iv()][0]
    require(noop.total_variation == F(1, 2) and not r.exact_abstraction,
            "correlated U1 = U2 makes Z = 0 always in the micro model: the no-op check fails (TV 1/2)")
    return {"noop_tv": str(noop.total_variation)}


def check_budget_and_numeric_comparison():
    r = check_interventional_abstraction(micro_model(), MACRO, TAU, BASE, MACRO_SET, budget=10)
    require(r.status == "budget_exhausted" and r.exact_abstraction is None, "budget stop: no verdict")
    n = check_interventional_abstraction(micro_model(), MACRO, TAU, BASE, MACRO_SET, tol=1e-12)
    require(n.comparison == "numeric_tolerance" and any("not an exact equality proof" in x for x in n.notes), "numeric comparison labelled")
    require(extends(iv(), iv(X1=1)) and extends(iv(X1=1), iv(X1=1, X2=0)) and not extends(iv(X1=1), iv(X1=0, X2=0)), "order relation")
    return {"budget": r.status, "numeric": n.comparison}


CHECKS = [
    check_jc19_exact_abstraction,
    check_jc19_failing_extension_and_b3,
    check_swapped_variable_names,
    check_non_surjective_and_missing,
    check_single_violating_intervention,
    check_correlated_exogenous_micro,
    check_budget_and_numeric_comparison,
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
    out_path = Path(__file__).with_name("verify_causal_abstraction_results.json")
    out_path.write_text(json.dumps({"n_passed": n_passed, "n_total": len(CHECKS), "results": results}, indent=2, default=str))
    print(f"Report written to {out_path}")
    return 0 if n_passed == len(CHECKS) else 1


if __name__ == "__main__":
    raise SystemExit(main())
