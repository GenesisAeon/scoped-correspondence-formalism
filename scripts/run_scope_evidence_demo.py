"""Scope, composition and evidence demo (Paket J12, plan §18.1).

A light entry point that runs the six mandatory demonstrations of the J-series
and prints standard JSON (no NaN/Infinity; exact fractions as strings):

1. an initially incompatible chain and its correctly restricted scope (J4);
2. a continuous rational domain certificate and a counterexample (J5);
3. observationally equivalent but interventionally different models (J9);
4. a transportable query and one the rule does NOT certify (J10);
5. a forecast comparison with its inferential limit stated (J1);
6. a weighted calibration where unboundedness is visible (J8).

    python scripts/run_scope_evidence_demo.py [--only N ...] [--output FILE]

The existing specialised CLIs stay as they are; no plugin architecture.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from fractions import Fraction as F
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from scoped_correspondence.assurance.expressions import Const, Mul, Sub, Var  # noqa: E402
from scoped_correspondence.assurance.scope_certification import certify_bound  # noqa: E402
from scoped_correspondence.causal.finite_scm import FiniteSCM, Mechanism, independent_exogenous, interventional_distribution, marginal  # noqa: E402
from scoped_correspondence.causal.selection_diagrams import DAG  # noqa: E402
from scoped_correspondence.causal.transport import standardise  # noqa: E402
from scoped_correspondence.correspondence.composition import CorrespondenceLink, Side, compose_correspondences  # noqa: E402
from scoped_correspondence.correspondence.domains import AffineMap, RationalBox  # noqa: E402
from scoped_correspondence.validation.forecast_comparison import (  # noqa: E402
    InferenceApplicability,
    PairedForecastRecord,
    compare_paired_forecasts,
    describe_comparison,
)
from scoped_correspondence.validation.weighted_conformal import weighted_conformal_intervals  # noqa: E402


def js(v):
    if isinstance(v, F):
        return str(v)
    if isinstance(v, float) and not math.isfinite(v):
        return {"status": "positive_infinity" if v > 0 else ("negative_infinity" if v < 0 else "undefined")}
    if isinstance(v, dict):
        return {str(k): js(x) for k, x in v.items()}
    if isinstance(v, (list, tuple)):
        return [js(x) for x in v]
    return v


def demo_composition():
    A, B, B2, C = (Side("A", ("x",), ("m",), "t"), Side("B", ("y",), ("m",), "t"), Side("B", ("y",), ("km",), "t"),
                   Side("C", ("z",), ("m",), "t"))
    unit = RationalBox.interval(0, 1)
    l1 = CorrespondenceLink("T1", A, B, AffineMap.scalar(2), F(1, 2), unit, F(4))
    bad = compose_correspondences(l1, CorrespondenceLink("T2", B2, C, AffineMap.scalar(3), F(1, 2), unit, F(1)))
    good = compose_correspondences(l1, CorrespondenceLink("T2", B, C, AffineMap.scalar(3), F(1, 2), unit, F(1)))
    return {"incompatible_attempt": {"status": bad.status, "reasons": list(bad.reasons)},
            "after_fixing_units": {"status": good.status, "scope": good.domain_report.declared_domain,
                                   "time_factor": good.link.time_factor, "horizon": good.link.horizon}}


def demo_domain_certificate():
    p = Mul(Var("x"), Sub(Const(1), Var("x")))
    ok, _ = certify_bound(p, {"x": (0, 1)}, F(13, 50))
    no, _ = certify_bound(p, {"x": (0, 1)}, F(6, 25))
    return {"claim_proved": {"claim": ok.claim, "verdict": ok.verdict, "proved_boxes": ok.values["proved_boxes"]},
            "claim_refuted": {"claim": no.claim, "verdict": no.verdict, "counterexample": no.witnesses[0]}}


def demo_observation_vs_intervention():
    fair = {0: F(1, 2), 1: F(1, 2)}
    out = {}
    for name, ym in (("Y=X", Mechanism(("X",), (), lambda pa, u: pa["X"])), ("Y=U", Mechanism((), ("U",), lambda pa, u: u["U"]))):
        m = FiniteSCM(name, ("X", "Y"), {"X": (0, 1), "Y": (0, 1)}, {"X": Mechanism((), ("U",), lambda pa, u: u["U"]), "Y": ym},
                      *independent_exogenous(U=fair))
        out[name] = {"observational": {str(k): v for k, v in interventional_distribution(m).items()},
                     "P(Y=1|do(X=1))": marginal(interventional_distribution(m, {"X": 1}), 1).get(1, F(0))}
    return out


def demo_transport():
    g = DAG.from_edges([("S", "Z"), ("Z", "Y"), ("X", "Y")])
    table = {(0,): {0: F(1), 1: F(0)}, (1,): {0: F(0), 1: F(1)}}  # P(Y | do(X=0), Z=z) for Y = X xor Z
    ok = standardise(g, x="X", y="Y", z=["Z"], s_nodes=["S"], x_value=0, source_do_table=table,
                     target_z={(0,): F(1, 4), (1,): F(3, 4)}, source_provenance="source_experiment")
    g_bad = DAG.from_edges([("S", "Z"), ("S", "Y"), ("Z", "Y"), ("X", "Y")])
    no = standardise(g_bad, x="X", y="Y", z=["Z"], s_nodes=["S"], x_value=0, source_do_table=table,
                     target_z={(0,): F(1, 4), (1,): F(3, 4)}, source_provenance="source_experiment")
    return {"transportable": {"outcome": ok.outcome, "Q(Y=1|do(X=0))": ok.value[1]},
            "not_certified": {"outcome": no.outcome, "reasons": list(no.reasons), "note": list(no.notes)}}


def demo_forecast_comparison():
    d = [F(-1), F(0), F(1), F(2)]
    recs = [PairedForecastRecord("demo", float(t), float(t + 1), 1, 0, x + 2, 2, "A", "B", "demo", "demo") for t, x in enumerate(d)]
    (r,) = compare_paired_forecasts(recs, loss="absolute_error", hac_lag=1, lag_justification="J-C01 arithmetic",
                                    applicability=InferenceApplicability(True, "arithmetic demo only", 30))
    return {"sentence": describe_comparison(r), "inference_status": r.inference_status, "reasons": list(r.inference_reasons)}


def demo_weighted_calibration():
    rep = weighted_conformal_intervals([0.1, 0.2, 0.3, 0.4], [1.0, 1.0, 1.0, 1.0], [0.0, 0.0], [1.0, 9.0], 0.2,
                                       weight_provenance="known_density_ratio")
    return {"intervals": [iv if isinstance(iv, dict) else list(iv) for iv in rep.intervals],
            "unbounded_fraction": rep.unbounded_fraction, "guarantee_status": rep.guarantee_status,
            "effective_sample_size": rep.effective_sample_size}


DEMOS = {1: ("incompatible_chain_and_restricted_scope", demo_composition),
         2: ("continuous_domain_certificate_and_counterexample", demo_domain_certificate),
         3: ("observationally_equivalent_interventionally_different", demo_observation_vs_intervention),
         4: ("transportable_and_not_certified_query", demo_transport),
         5: ("forecast_comparison_with_inferential_limit", demo_forecast_comparison),
         6: ("weighted_calibration_with_visible_unboundedness", demo_weighted_calibration)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--only", nargs="*", type=int, default=None)
    ap.add_argument("--output", type=Path, default=None)
    args = ap.parse_args(argv)
    sel = args.only or sorted(DEMOS)
    out = {DEMOS[k][0]: js(DEMOS[k][1]()) for k in sel}
    text = json.dumps(out, indent=2, allow_nan=False, ensure_ascii=False)
    if args.output:
        args.output.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
