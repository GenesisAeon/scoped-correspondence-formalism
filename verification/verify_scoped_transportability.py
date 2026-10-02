"""J10 verification (SCOPE_COMPOSITION_EVIDENCE_ROADMAP.md, plan section 16):
one checked standardisation rule and finite counter-models.

J-C20 (source Z ~ Bern(1/2), target Z ~ Bern(3/4), Y = X xor Z: target
3/4 and 1/4, effect -1/2; the unweighted source effect 0 is wrong; missing
support -> not certified), J-C21 (two source-target families agree on all
available information, target value 1 vs 1/2), J-C23 (collider, descendant,
S-admissibility). Pflichtprüfungen: wrong direction of edge removal for
do(X), Z descendant of X, missing support, violated S-admissibility,
incomplete tables, budget limit, complete check of all available source
information for a counter-model pair.
"""
from __future__ import annotations

import json
import sys
from fractions import Fraction as F
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from scoped_correspondence.causal.finite_scm import BudgetExceeded, FiniteSCM, Mechanism, independent_exogenous, interventional_distribution, marginal
from scoped_correspondence.causal.selection_diagrams import DAG, d_separated, s_admissible
from scoped_correspondence.causal.transport import counter_model_witness, standardise
from scoped_correspondence.errors import ScopeViolationError

FAIR = {0: F(1, 2), 1: F(1, 2)}
DIAGRAM = DAG.from_edges([("S", "Z"), ("Z", "Y"), ("X", "Y")])


def require(c, m=""):
    if not c:
        raise AssertionError(m)


def raises(fn, exc=(ScopeViolationError,)):
    try:
        fn()
    except exc:
        return True
    return False


def xor_model(pz1):
    names, dist = independent_exogenous(UZ={0: 1 - pz1, 1: pz1}, UX=FAIR)
    return FiniteSCM(f"Z~Bern({pz1})", ("Z", "X", "Y"), {"Z": (0, 1), "X": (0, 1), "Y": (0, 1)},
                     {"Z": Mechanism((), ("UZ",), lambda pa, u: u["UZ"]), "X": Mechanism((), ("UX",), lambda pa, u: u["UX"]),
                      "Y": Mechanism(("X", "Z"), (), lambda pa, u: pa["X"] ^ pa["Z"])}, names, dist)


def do_table(model, x):
    """P(Y | do(X=x), Z=z) computed from the SOURCE model's interventional distribution."""
    d = interventional_distribution(model, {"X": x})
    out = {}
    for z in (0, 1):
        pz = sum(p for s, p in d.items() if s[0] == z)
        if pz > 0:
            out[(z,)] = {yv: sum(p for s, p in d.items() if s[0] == z and s[2] == yv) / pz for yv in (0, 1)}
    return out


def check_jc20_standardisation():
    src, tgt = xor_model(F(1, 2)), xor_model(F(3, 4))
    Qz = {(0,): F(1, 4), (1,): F(3, 4)}
    res = {x: standardise(DIAGRAM, x="X", y="Y", z=["Z"], s_nodes=["S"], x_value=x, source_do_table=do_table(src, x),
                          target_z=Qz, source_provenance="source_experiment") for x in (0, 1)}
    require(all(r.outcome == "certified_applicable" for r in res.values()), f"premises hold: {[r.reasons for r in res.values()]}")
    v0, v1 = res[0].value[1], res[1].value[1]
    require((v0, v1) == (F(3, 4), F(1, 4)) and v1 - v0 == F(-1, 2), f"target 3/4, 1/4, effect -1/2, got {v0}, {v1}")
    direct = [marginal(interventional_distribution(tgt, {"X": x}), 2)[1] for x in (0, 1)]
    require(direct == [F(3, 4), F(1, 4)], "cross-check: direct computation in the target model agrees")
    src_eff = marginal(interventional_distribution(src, {"X": 1}), 2)[1] - marginal(interventional_distribution(src, {"X": 0}), 2)[1]
    require(src_eff == 0, "the unweighted source effect is 0 -- transferring it unchanged would be wrong")
    return {"target": ["3/4", "1/4"], "effect": "-1/2", "source_effect": "0"}


def check_missing_support():
    src = xor_model(F(0))  # source never has Z = 1
    r = standardise(DIAGRAM, x="X", y="Y", z=["Z"], s_nodes=["S"], x_value=1, source_do_table=do_table(src, 1),
                    target_z={(0,): F(1, 4), (1,): F(3, 4)}, source_provenance="source_experiment")
    require(r.outcome == "not_certified_by_this_rule" and not r.premises["support"] and "non-transportability" in r.notes[0],
            "missing support: not certified -- and explicitly not a non-transportability proof")
    return {"outcome": r.outcome}


def check_jc21_counter_models():
    def fam(target_y_from):
        un, ud = independent_exogenous(U=FAIR)
        src = FiniteSCM("src", ("X", "Y"), {"X": (0, 1), "Y": (0, 1)},
                        {"X": Mechanism((), ("U",), lambda pa, u: u["U"]), "Y": Mechanism(("X",), (), lambda pa, u: pa["X"])}, un, ud)
        ym = Mechanism(("X",), (), lambda pa, u: pa["X"]) if target_y_from == "X" else Mechanism((), ("U",), lambda pa, u: u["U"])
        tgt = FiniteSCM("tgt", ("X", "Y"), {"X": (0, 1), "Y": (0, 1)}, {"X": Mechanism((), ("U",), lambda pa, u: u["U"]), "Y": ym}, un, ud)
        return {"source_obs": interventional_distribution(src), "source_do_x0": interventional_distribution(src, {"X": 0}),
                "source_do_x1": interventional_distribution(src, {"X": 1}), "target_obs": interventional_distribution(tgt),
                "target_P_y1_do_x1": marginal(interventional_distribution(tgt, {"X": 1}), 1).get(1, F(0))}
    a, b = fam("X"), fam("U")
    avail = ["source_obs", "source_do_x0", "source_do_x1", "target_obs"]
    r = counter_model_witness(a, b, avail, "target_P_y1_do_x1")
    require(r.outcome == "non_identified_by_counter_models" and (a["target_P_y1_do_x1"], b["target_P_y1_do_x1"]) == (F(1), F(1, 2)),
            "agree on all available information, differ on the target (1 vs 1/2)")
    b_bad = dict(b, target_obs={(0, 1): F(1, 2), (1, 0): F(1, 2)})
    require(counter_model_witness(a, b_bad, avail, "target_P_y1_do_x1").outcome == "not_certified_by_this_rule",
            "if ANY available quantity differs, the pair is no witness")
    require(raises(lambda: counter_model_witness(a, b, avail + ["missing_quantity"], "target_P_y1_do_x1")), "every listed quantity must be provided")
    return {"target_values": ["1", "1/2"]}


def check_jc23_graph():
    col = DAG.from_edges([("A", "C"), ("B", "C"), ("C", "D")])
    require(d_separated(col, ["A"], ["B"], []) and not d_separated(col, ["A"], ["B"], ["C"]) and not d_separated(col, ["A"], ["B"], ["D"]),
            "collider closed; conditioning on C or its descendant D opens it")
    require(d_separated(DIAGRAM, ["S"], ["Y"], ["X", "Z"]) and not d_separated(DIAGRAM, ["S"], ["Y"], ["X"]), "S separated given X,Z; not given X")
    require(raises(lambda: DAG.from_edges([("A", "B"), ("B", "A")])), "cycle rejected")
    return {"collider": "ok"}


def check_wrong_edge_removal_direction():
    g = DAG.from_edges([("S", "X"), ("U", "X"), ("U", "Y"), ("X", "Y")], latent=["U"])
    require(s_admissible(g, ["S"], ["X"], ["Y"], []), "correct G_bar_X (edges INTO X removed): S admissible with Z = {}")
    wrong = DAG(g.nodes, frozenset((a, b) for a, b in g.edges if a != "X"), g.latent)  # removes edges OUT of X
    require(not d_separated(wrong, ["S"], ["Y"], ["X"]), "removing edges OUT of X instead would open S -> X <- U -> Y")
    return {"correct": True, "wrong_direction_detected": True}


def check_premise_failures():
    src = xor_model(F(1, 2))
    good = dict(x="X", y="Y", s_nodes=["S"], x_value=1, source_do_table=do_table(src, 1), target_z={(0,): F(1, 4), (1,): F(3, 4)})
    desc = DAG.from_edges([("S", "Z"), ("X", "Z"), ("Z", "Y"), ("X", "Y")])
    r1 = standardise(desc, z=["Z"], source_provenance="source_experiment", **good)
    require(r1.outcome == "not_certified_by_this_rule" and not r1.premises["z_not_descendant_of_x"], "Z descendant of X")
    direct = DAG.from_edges([("S", "Z"), ("S", "Y"), ("Z", "Y"), ("X", "Y")])
    r2 = standardise(direct, z=["Z"], source_provenance="source_experiment", **good)
    require(not r2.premises["s_admissible"], "S -> Y violates S-admissibility")
    r3 = standardise(DIAGRAM, z=["Z"], source_provenance="observational", **good)
    require(not r3.premises["source_quantities_interventional"], "observational P(Y|X,Z) is not accepted in place of P(Y|do(X),Z)")
    bad_table = dict(good, source_do_table={(0,): {0: F(1, 2)}, (1,): {0: F(1, 2), 1: F(1, 2)}})
    require(raises(lambda: standardise(DIAGRAM, z=["Z"], source_provenance="source_experiment", **bad_table)), "incomplete table row rejected")
    big = xor_model(F(1, 2))
    require(raises(lambda: interventional_distribution(big, {"X": 1}, budget=2), (BudgetExceeded,)),
            "budget limit while building source tables: no result")
    return {"premise_checks": "ok"}


CHECKS = [
    check_jc20_standardisation,
    check_missing_support,
    check_jc21_counter_models,
    check_jc23_graph,
    check_wrong_edge_removal_direction,
    check_premise_failures,
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
    out_path = Path(__file__).with_name("verify_scoped_transportability_results.json")
    out_path.write_text(json.dumps({"n_passed": n_passed, "n_total": len(CHECKS), "results": results}, indent=2, default=str))
    print(f"Report written to {out_path}")
    return 0 if n_passed == len(CHECKS) else 1


if __name__ == "__main__":
    raise SystemExit(main())
