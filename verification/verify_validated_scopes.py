"""J5 verification (SCOPE_COMPOSITION_EVIDENCE_ROADMAP.md, plan section 11):
universal bounds over whole rational boxes, with separate results for
proved / refuted / undecided / undefined input.

Pflichtprüfungen: J-C09 (x(1-x): 33/128 natural bound on 64 cells, proves
<= 13/50, x=1/2 refutes <= 6/25, sharp 1/4 may stay undecided), J-C10
(x - x dependency, 1/x singular on [-1, 1]); exact boundary touch,
negative coefficients, denominator near zero, single vs repeated
variables, multi-dimensional boxes, full partition coverage, residual
boxes at budget end, empty domain, exact reconstruction of a certificate,
and at least one J4 residual certified over a box.

Expected values from verification/plan_controls/j_series_independent_controls.py.
"""
from __future__ import annotations

import json
import sys
from fractions import Fraction as F
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from scoped_correspondence.assurance.expressions import Add, Const, Div, Mul, Neg, Pow, Sub, Var, enclose, evaluate
from scoped_correspondence.assurance.rational_intervals import DenominatorContainsZero, Interval
from scoped_correspondence.assurance.scope_certification import certify_abs_bound, certify_bound, recheck_certificate
from scoped_correspondence.errors import ScopeViolationError

X, Y = Var("x"), Var("y")
P = Mul(X, Sub(Const(1), X))  # x(1-x)


def require(c, m=""):
    if not c:
        raise AssertionError(m)


def raises(fn, exc=(ScopeViolationError,)):
    try:
        fn()
    except exc:
        return True
    return False


def check_jc09_natural_bound_and_counterexample():
    uppers = [enclose(P, {"x": Interval(F(i, 64), F(i + 1, 64))}).hi for i in range(64)]
    require(max(uppers) == F(33, 128), f"64-cell natural upper bound must be 33/128, got {max(uppers)}")
    rep, cert = certify_bound(P, {"x": (0, 1)}, F(13, 50))
    require(rep.verdict == "proved" and cert is not None, f"p <= 13/50 must be proved: {rep.reasons}")
    ok, problems = recheck_certificate(cert)
    require(ok, f"certificate must re-check: {problems}")
    ref, _ = certify_bound(P, {"x": (0, 1)}, F(6, 25))
    require(ref.verdict == "refuted" and ref.witnesses[0]["x"] == "1/2" and ref.values["counterexample_value"] == F(1, 4),
            f"x=1/2 must refute 6/25: {ref.witnesses}")
    require(evaluate(P, {"x": F(0)}) == evaluate(P, {"x": F(1)}) == 0, "endpoints give 0")
    return {"proved_boxes": rep.values["proved_boxes"], "max_enclosure": str(rep.values["max_enclosure"]),
            "counterexample": ref.witnesses[0]}


def check_exact_boundary_touch_stays_undecided_or_proved_never_refuted():
    rep, _ = certify_bound(P, {"x": (0, 1)}, F(1, 4), budget=200)
    require(rep.verdict in ("undecided", "proved"), f"sharp bound 1/4 must not be refuted, got {rep.verdict}")
    require(rep.verdict == "undecided" and rep.procedure_status == "budget_exhausted" and rep.witnesses,
            "natural extension cannot close the sharp bound: budget stop with residual boxes (plan: 'unknown' allowed)")
    require(not rep.domain_exhausted and not rep.conclusion_complete, "a budget stop is not a conclusion")
    lin, _ = certify_bound(Add(Mul(Const(2), X), Const(1)), {"x": (0, 1)}, 3)
    require(lin.verdict == "proved", "2x+1 <= 3 touches the bound at x=1 exactly and is proved (enclosure exact for linear)")
    return {"sharp_quarter": rep.verdict, "residual_boxes": len(rep.witnesses)}


def check_jc10_dependency_and_singularity():
    e = Sub(X, X)
    require(enclose(e, {"x": Interval(0, 1)}) == Interval(-1, 1), "natural enclosure of x - x on [0,1] is [-1,1]")
    zero, _ = certify_bound(e, {"x": (0, 1)}, 0, budget=64)
    require(zero.verdict == "undecided", "no sharp zero bound without symbolic simplification")
    half, _ = certify_bound(e, {"x": (0, 1)}, F(1, 2))
    require(half.verdict == "proved", "a non-sharp bound becomes provable by subdivision")
    inv = Div(Const(1), X)
    require(raises(lambda: enclose(inv, {"x": Interval(-1, 1)}), DenominatorContainsZero), "1/x enclosure on [-1,1] must refuse")
    sing, _ = certify_bound(inv, {"x": (-1, 1)}, 1000)
    require(sing.verdict == "undefined_on_domain" and sing.witnesses[0]["x"] == "0", f"1/x on [-1,1]: undefined at 0, got {sing.verdict}")
    return {"x_minus_x": "[-1,1]", "reciprocal": sing.verdict}


def check_denominator_near_zero():
    inv = Div(Const(1), X)
    # (a) a real blow-up near 0: 1/x > 1000 for 0 < x < 1/1000 -> genuine counterexample
    near, _ = certify_bound(inv, {"x": (-1, F(1, 2))}, 1000, budget=300)
    require(near.verdict == "refuted" and near.values["counterexample_value"] > 1000,
            f"1/x <= 1000 on [-1,1/2] is false near 0+: must be refuted, got {near.verdict}")
    # (b) denominator only APPEARS to contain 0 (overestimation): x^2 - x + 1 >= 3/4 on [0,1],
    #     but its natural enclosure is [0, 2]; subdivision resolves it, max of the quotient is 4/3
    q = Div(Const(1), Add(Sub(Mul(X, X), X), Const(1)))
    require(raises(lambda: enclose(q, {"x": Interval(0, 1)}), DenominatorContainsZero), "precondition: overestimated denominator")
    res, rcert = certify_bound(q, {"x": (0, 1)}, 2)
    require(res.verdict == "proved" and res.values["singular_enclosures_split"] >= 1 and recheck_certificate(rcert)[0],
            "overestimated zero denominator is resolved by subdivision")
    # (c) defined everywhere except a point the dyadic bisection never hits: x/x on [-1, 1/2]
    xx, _ = certify_bound(Div(X, X), {"x": (-1, F(1, 2))}, 1, budget=300)
    require(xx.verdict == "undecided" and xx.procedure_status == "budget_exhausted" and any("contained 0" in r for r in xx.reasons),
            f"x/x: no counterexample, no proof; budget stop with a definition warning, got {xx.verdict} {xx.reasons}")
    away, cert = certify_bound(inv, {"x": (F(1, 1000), 1)}, 1000)
    require(away.verdict == "proved" and recheck_certificate(cert)[0], "1/x <= 1000 on [1/1000, 1] is proved")
    tight, _ = certify_bound(inv, {"x": (F(1, 1000), 1)}, 999)
    require(tight.verdict == "refuted", "1/x <= 999 fails at x=1/1000")
    return {"near_zero": near.verdict, "away": away.verdict}


def check_negative_coefficients_and_repeated_variables():
    e = Sub(Mul(Const(-3), Pow(X, 2)), Mul(Const(2), X))  # -3x^2 - 2x on [-1, 1]: max 1/3 at x=-1/3
    rep, cert = certify_bound(e, {"x": (-1, 1)}, F(1, 2))
    require(rep.verdict == "proved" and recheck_certificate(cert)[0], "-3x^2-2x <= 1/2 on [-1,1]")
    ref, _ = certify_bound(e, {"x": (-1, 1)}, F(1, 4))
    require(ref.verdict == "refuted", "-3x^2-2x <= 1/4 fails near x=-1/3")
    require(enclose(Pow(X, 2), {"x": Interval(-1, 2)}) == Interval(0, 4), "even power is tight, not x*x = [-2,4]")
    require(enclose(Mul(X, X), {"x": Interval(-1, 2)}) == Interval(-2, 4), "x*x natural extension overestimates (dependency)")
    return {"neg_coeff": rep.verdict}


def check_multidimensional_box_and_coverage():
    e = Add(Mul(X, Y), Sub(X, Y))  # xy + x - y on [0,1]x[0,2]: max 2 at (1,2)? 2+1-2=1; at (1,0)=1; max is 1
    rep, cert = certify_bound(e, {"x": (0, 1), "y": (0, 2)}, F(11, 10))
    require(rep.verdict == "proved", f"xy + x - y <= 11/10 on [0,1]x[0,2], got {rep.verdict}")
    ok, problems = recheck_certificate(cert)
    require(ok and len(cert.partition) == rep.values["proved_boxes"], f"partition must cover the 2-D domain: {problems}")
    low, _ = certify_bound(e, {"x": (0, 1), "y": (0, 2)}, -2, side="lower")
    require(low.verdict == "proved", "lower bound -2 holds (min is -2 at (0,2))")
    tight_low, _ = certify_bound(e, {"x": (0, 1), "y": (0, 2)}, F(-19, 10), side="lower")
    require(tight_low.verdict == "refuted" and tight_low.witnesses, "lower bound -19/10 fails at (0,2)")
    return {"proved_boxes": len(cert.partition)}


def check_certificate_tampering_is_detected():
    rep, cert = certify_bound(P, {"x": (0, 1)}, F(13, 50))
    from dataclasses import replace
    dropped = replace(cert, partition=cert.partition[1:])
    ok, problems = recheck_certificate(dropped)
    require(not ok and any("volume" in p for p in problems), "a missing partition box must be detected")
    b0, e0 = cert.partition[0]
    forged = replace(cert, partition=((b0, Interval(e0.lo, e0.hi - F(1, 1000))),) + cert.partition[1:])
    require(not recheck_certificate(forged)[0], "a forged enclosure must be detected")
    stricter = replace(cert, epsilon=F(1, 5))
    require(not recheck_certificate(stricter)[0], "re-using the partition for a stricter bound must fail")
    return {"tamper_checks": 3}


def check_budget_residual_boxes_and_empty_domain():
    rep, _ = certify_bound(P, {"x": (0, 1)}, F(13, 50), budget=2)
    require(rep.verdict == "undecided" and rep.procedure_status == "budget_exhausted" and rep.witnesses,
            "budget 2 must stop with residual boxes")
    empty, cert = certify_bound(P, {"x": (1, 0)}, -5)
    require(empty.verdict == "proved" and empty.empty_domain and cert is None, "empty box: vacuous, flagged, no certificate")
    require(raises(lambda: certify_bound(P, {"x": (0, 1)}, 0.26)), "float epsilon rejected")
    require(raises(lambda: certify_bound(P, {"x": (0, 1)}, 1, budget=0)), "budget must be >= 1")
    require(raises(lambda: certify_bound(P, {"y": (0, 1)}, 1)), "unbounded variable is an input error")
    require(raises(lambda: certify_bound(lambda x: x, {"x": (0, 1)}, 1)), "a Python callback is not a provable expression")
    require(Const("0.1").value == F(1, 10) and Const.of_float(0.1).value != F(1, 10), "decimal string vs exact binary float are different numbers")
    return {"residual_boxes": len(rep.witnesses)}


def check_j4_residual_certified_over_box():
    # J-C07 field case: T1 = 2x, T2 = 3y, f_A = x, f_B = 0, f_C = -1, a1 = 2, a2 = 3.
    fA, fB, fC = X, Const(0), Const(-1)
    r1 = Sub(Mul(Const(2), fA), Mul(Const(2), fB))       # DT1 f_A - a1 f_B(T1 x)
    r2 = Sub(Mul(Const(3), fB), Mul(Const(3), fC))       # DT2 f_B - a2 f_C(T2 y), constant in y
    r12 = Add(Mul(Const(3), r1), Mul(Const(2), r2))      # (DT2 o T1) r1 + a1 (r2 o T1)
    rep, cert = certify_abs_bound(r12, {"x": (0, F(1, 2))}, 9)
    require(rep.verdict == "proved" and cert.verdict == "proved", "|r12| <= 9 on [0, 1/2] proved (J-C07 field bound)")
    sharp, _ = certify_bound(r12, {"x": (0, F(1, 2))}, F(89, 10))
    require(sharp.verdict == "refuted" and sharp.witnesses[0]["x"] == "1/2", "the bound 9 is attained at x = 1/2")
    require(evaluate(r12, {"x": F(1, 4)}) == F(15, 2), "r12(1/4) = 15/2")
    return {"abs_bound": 9, "attained_at": "1/2"}


CHECKS = [
    check_jc09_natural_bound_and_counterexample,
    check_exact_boundary_touch_stays_undecided_or_proved_never_refuted,
    check_jc10_dependency_and_singularity,
    check_denominator_near_zero,
    check_negative_coefficients_and_repeated_variables,
    check_multidimensional_box_and_coverage,
    check_certificate_tampering_is_detected,
    check_budget_residual_boxes_and_empty_domain,
    check_j4_residual_certified_over_box,
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
    out_path = Path(__file__).with_name("verify_validated_scopes_results.json")
    out_path.write_text(json.dumps({"n_passed": n_passed, "n_total": len(CHECKS), "results": results}, indent=2, default=str))
    print(f"Report written to {out_path}")
    return 0 if n_passed == len(CHECKS) else 1


if __name__ == "__main__":
    raise SystemExit(main())
