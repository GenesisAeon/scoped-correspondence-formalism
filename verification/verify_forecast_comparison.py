"""J1 verification (SCOPE_COMPOSITION_EVIDENCE_ROADMAP.md, plan section 7):
paired forecast comparison with applicability-gated DM/HAC inference.

Every Pflichtprüfung of plan section 7 has an explicit check below:
J-C01 (Bartlett-HAC arithmetic, exact), J-C02 (Holm), model swap flips the
sign, positive loss scaling leaves DM unchanged, constant differences
(degenerate variance), wrong pairing, missing partners, different
horizons, invalid numbers, pre-declared test family -- plus the
applicability gates (not declared, nested, structural break, too short),
lag validation, no concatenation of different series, the mandatory
"winner sentence" content and standard-conformant JSON.

Expected values come from the independent J0 derivation
(verification/plan_controls/j_series_independent_controls.py), not from
this module.
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
from scoped_correspondence.validation.forecast_comparison import (
    DeclaredTestFamily,
    InferenceApplicability,
    PairedForecastRecord,
    bartlett_hac_long_run_variance,
    compare_paired_forecasts,
    describe_comparison,
    holm_adjust,
    holm_adjust_family,
    pair_raw_predictions,
)
from scoped_correspondence.validation.rolling_origin import RawHorizonPrediction, raw_predictions_by_horizon_step


def require(condition, msg=""):
    if not condition:
        raise AssertionError(msg)


def raises(fn, exc=ScopeViolationError):
    try:
        fn()
    except exc:
        return True
    return False


OK = InferenceApplicability(declared_justified=True, justification="synthetic control: declared for the arithmetic test", min_series_length=2)
NOT_DECLARED = InferenceApplicability(declared_justified=False, justification="", min_series_length=2)


def _records(d_values, *, series="s", horizon=1, a="A", b="B", observed=0):
    """Absolute-error records with loss_a - loss_b == d exactly: observed 0,
    prediction_b = 2 (loss 2), prediction_a = d + 2 (>= 0 here)."""
    out = []
    for t, d in enumerate(d_values):
        out.append(PairedForecastRecord(series, float(t), float(t + horizon), horizon, observed, d + 2, 2, a, b, "data", "split"))
    return out


# ------------------------------------------------------------------ checks --


def check_jc01_bartlett_hac_exact():
    d = [F(-1), F(0), F(1), F(2)]
    V = bartlett_hac_long_run_variance(d, 1)
    require(V == F(25, 16), f"V must be 25/16 exactly, got {V}")
    require(V / 4 == F(25, 64), "V/n must be 25/64 (se = 5/8)")
    res = compare_paired_forecasts(_records(d), loss="absolute_error", hac_lag=1,
                                   lag_justification="J-C01 fixed lag", applicability=OK)
    (r,) = res
    require(r.mean_loss_difference == F(1, 2), f"mean must be 1/2, got {r.mean_loss_difference}")
    require(r.long_run_variance == F(25, 16), "result must carry the exact long-run variance")
    require(abs(r.standard_error - 0.625) < 1e-15 and abs(r.dm_statistic - 0.8) < 1e-15, f"se/DM wrong: {r.standard_error}, {r.dm_statistic}")
    require(r.inference_status == "asymptotic_normal_reference")
    require(r.descriptive_direction == "B_lower_mean_loss", "positive mean difference favours B")
    # lag 0 for comparison: V = gamma0 = 5/4
    require(bartlett_hac_long_run_variance(d, 0) == F(5, 4))
    return {"V": str(V), "se": r.standard_error, "dm": r.dm_statistic, "note": "arithmetic only; n=4 does not justify asymptotics"}


def check_jc02_holm_original_order():
    adj = holm_adjust([F(1, 100), F(4, 100), F(3, 100)])
    require(adj == [F(3, 100), F(6, 100), F(6, 100)], f"Holm must be (.03,.06,.06), got {adj}")
    require(holm_adjust([F(9, 10), F(8, 10)]) == [F(1), F(1)], "Holm values are capped at 1")
    require(raises(lambda: holm_adjust([])) and raises(lambda: holm_adjust([F(3, 2)])), "empty family / p>1 are input errors")
    return {"adjusted": [str(x) for x in adj]}


def check_model_swap_flips_sign():
    rng = np.random.default_rng(1)
    obs = rng.normal(size=40)
    pa, pb = obs + rng.normal(scale=0.5, size=40), obs + rng.normal(scale=0.8, size=40)
    rec_ab = [PairedForecastRecord("s", float(t), float(t + 1), 1, float(obs[t]), float(pa[t]), float(pb[t]), "A", "B", "d", "sp") for t in range(40)]
    rec_ba = [PairedForecastRecord("s", float(t), float(t + 1), 1, float(obs[t]), float(pb[t]), float(pa[t]), "B", "A", "d", "sp") for t in range(40)]
    (ab,) = compare_paired_forecasts(rec_ab, loss="squared_error", hac_lag=2, lag_justification="test", applicability=OK)
    (ba,) = compare_paired_forecasts(rec_ba, loss="squared_error", hac_lag=2, lag_justification="test", applicability=OK)
    require(math.isclose(ab.mean_loss_difference, -ba.mean_loss_difference, rel_tol=1e-12), "mean difference must flip sign")
    require(math.isclose(ab.dm_statistic, -ba.dm_statistic, rel_tol=1e-12), "DM must flip sign")
    require(math.isclose(ab.p_value_two_sided, ba.p_value_two_sided, rel_tol=1e-12), "two-sided p must be unchanged")
    return {"dm_ab": ab.dm_statistic, "dm_ba": ba.dm_statistic}


def check_positive_loss_scaling_leaves_dm_unchanged():
    d = [F(-1), F(0), F(1), F(2), F(-3), F(5)]
    base = compare_paired_forecasts(_records(d), loss="absolute_error", hac_lag=1, lag_justification="t", applicability=OK)[0]
    # scaling observed and both predictions by c scales absolute losses by c
    c = F(7, 3)
    scaled = [PairedForecastRecord(r.series_id, r.origin, r.target_time, r.horizon, r.observed * c, r.prediction_a * c, r.prediction_b * c, "A", "B", "data", "split") for r in _records(d)]
    s = compare_paired_forecasts(scaled, loss="absolute_error", hac_lag=1, lag_justification="t", applicability=OK)[0]
    require(s.long_run_variance == base.long_run_variance * c * c, "V must scale by c^2 exactly")
    require(math.isclose(s.dm_statistic, base.dm_statistic, rel_tol=1e-12), "DM must be invariant under positive loss scaling")
    # squared loss: scaling data by c scales losses by c^2 -- DM again unchanged
    sq_base = compare_paired_forecasts(_records(d), loss="squared_error", hac_lag=1, lag_justification="t", applicability=OK)[0]
    sq_s = compare_paired_forecasts(scaled, loss="squared_error", hac_lag=1, lag_justification="t", applicability=OK)[0]
    require(math.isclose(sq_s.dm_statistic, sq_base.dm_statistic, rel_tol=1e-12), "DM invariant for squared loss too")
    return {"dm": base.dm_statistic}


def check_constant_differences_are_degenerate():
    # float version FIRST: constant 0.1 differences leave a rounding-level,
    # nonzero V -- without the numerical guard this would yield a huge DM and
    # a tiny p-value (a false "certain winner"), not an exception.
    # observed y varies, prediction_a = y + 0.1, prediction_b = y: the absolute-loss
    # difference is mathematically 0.1 everywhere but differs in the last bits.
    ys = [0.37 * t + 1.1 for t in range(10)]
    recs = [PairedForecastRecord("s", float(t), float(t + 1), 1, y, y + 0.1, y, "A", "B", "d", "sp") for t, y in enumerate(ys)]
    d_float = [abs(y - (y + 0.1)) for y in ys]
    require(len(set(d_float)) > 1, "test precondition: differences must actually vary at rounding level")
    (rf,) = compare_paired_forecasts(recs, loss="absolute_error", hac_lag=2, lag_justification="t", applicability=OK)
    require(rf.inference_status == "degenerate_variance", f"float constant d must be degenerate, got {rf.inference_status} DM={rf.dm_statistic}")
    require(rf.p_value_two_sided is None, "float constant d must not produce a p-value")
    (r,) = compare_paired_forecasts(_records([F(1)] * 10), loss="absolute_error", hac_lag=2, lag_justification="t", applicability=OK)
    require(r.inference_status == "degenerate_variance", f"constant d must be degenerate, got {r.inference_status}")
    require(r.p_value_two_sided is None and r.dm_statistic is None and r.confidence_interval is None, "no p=0 and no DM for degenerate variance")
    require(r.descriptive_direction == "B_lower_mean_loss", "descriptive comparison stays available")
    return {"status": r.inference_status, "float_status": rf.inference_status}


def check_wrong_pairing_is_input_error():
    a = [RawHorizonPrediction(1.0, 1, 5.0, 4.0)]
    b = [RawHorizonPrediction(1.0, 1, 6.0, 4.5)]  # different observed under same key
    require(raises(lambda: pair_raw_predictions(a, b, series_id="s", model_a_id="A", model_b_id="B", data_id="d", split_id="sp", step_size=1.0)),
            "different observed values under the same key must be an input error")
    dup = [RawHorizonPrediction(1.0, 1, 5.0, 4.0), RawHorizonPrediction(1.0, 1, 5.0, 4.1)]
    require(raises(lambda: pair_raw_predictions(dup, a, series_id="s", model_a_id="A", model_b_id="B", data_id="d", split_id="sp", step_size=1.0)),
            "duplicate keys on one side must be an input error")
    require(raises(lambda: pair_raw_predictions(a, a, series_id="s", model_a_id="A", model_b_id="A", data_id="d", split_id="sp", step_size=1.0)),
            "identical model ids must be rejected")
    return {"wrong_pairing": "rejected"}


def check_missing_partners_are_counted():
    a = [RawHorizonPrediction(float(o), 1, float(o), float(o) + 0.1) for o in range(5)]
    b = [RawHorizonPrediction(float(o), 1, float(o), float(o) - 0.2) for o in range(2, 7)]
    rep = pair_raw_predictions(a, b, series_id="s", model_a_id="A", model_b_id="B", data_id="d", split_id="sp", step_size=1.0)
    require((rep.n_requested_a, rep.n_requested_b, rep.n_paired) == (5, 5, 3), f"counts wrong: {rep.to_dict()}")
    reasons = sorted(i.reason for i in rep.excluded)
    require(reasons == ["missing_partner_in_model_a"] * 2 + ["missing_partner_in_model_b"] * 2, f"reasons wrong: {reasons}")
    require(all(r.target_time == r.origin + 1.0 for r in rep.records), "target_time = origin + step*step_size")
    return rep.to_dict()


def check_invalid_numbers_are_reported():
    a = [RawHorizonPrediction(0.0, 1, 1.0, float("nan")), RawHorizonPrediction(1.0, 1, 1.0, 2.0)]
    b = [RawHorizonPrediction(0.0, 1, 1.0, 1.5), RawHorizonPrediction(1.0, 1, 1.0, float("inf"))]
    rep = pair_raw_predictions(a, b, series_id="s", model_a_id="A", model_b_id="B", data_id="d", split_id="sp", step_size=1.0)
    require(rep.n_paired == 0 and [i.reason for i in rep.invalid] == ["non_finite_value"] * 2, f"invalid not reported: {rep.to_dict()}")
    bad = [PairedForecastRecord("s", 0.0, 1.0, 1, 1.0, float("nan"), 1.0, "A", "B", "d", "sp")]
    require(raises(lambda: compare_paired_forecasts(bad, loss="squared_error", hac_lag=0, lag_justification="t", applicability=OK)),
            "non-finite records passed directly must be an input error")
    return {"invalid": len(rep.invalid)}


def check_horizons_are_never_pooled():
    x = np.arange(60, dtype=float)
    y = 0.05 * x + np.sin(x / 3.0)
    preds = raw_predictions_by_horizon_step(
        x, y, origins=list(range(10, 50)), max_horizon_steps=3, step_size=1.0,
        predictors={"persist": lambda cx, cy, tx: np.full(tx.shape, cy[-1]),
                    "mean": lambda cx, cy, tx: np.full(tx.shape, cy.mean())},
    )
    rep = pair_raw_predictions(preds["persist"], preds["mean"], series_id="synthetic", model_a_id="persist",
                               model_b_id="mean", data_id="synthetic_sine", split_id="origins_10_49", step_size=1.0)
    res = compare_paired_forecasts(rep.records, loss="squared_error", hac_lag=2, lag_justification="h-1 for h<=3, synthetic", applicability=OK)
    require([r.horizon for r in res] == [1, 2, 3] and all(r.n == 40 for r in res), f"one result per horizon with n=40 each, got {[(r.horizon, r.n) for r in res]}")
    return {"horizons": [r.horizon for r in res], "dm": [r.dm_statistic for r in res]}


def check_series_are_not_concatenated():
    recs = _records([F(1), F(-1), F(2), F(0)], series="catchment_1") + _records([F(3), F(1), F(-2), F(5)], series="catchment_2")
    res = compare_paired_forecasts(recs, loss="absolute_error", hac_lag=1, lag_justification="t", applicability=OK)
    require([r.series_id for r in res] == ["catchment_1", "catchment_2"] and all(r.n == 4 for r in res), "each series reported separately")
    mixed = _records([F(1)] * 3) + _records([F(1)] * 3, a="A2")
    require(raises(lambda: compare_paired_forecasts(mixed, loss="absolute_error", hac_lag=0, lag_justification="t", applicability=OK)),
            "mixed model ids within one series/horizon must be an input error")
    return {"series": [r.series_id for r in res]}


def check_applicability_gates():
    d = [F(x) for x in (-1, 0, 1, 2, -2, 3, 1, 0)]
    cases = {
        "not_declared": (NOT_DECLARED, "applicability_not_declared"),
        "nested": (InferenceApplicability(True, "x", 2, nested_models=True), "nested_models"),
        "break": (InferenceApplicability(True, "x", 2, structural_break_suspected=True), "structural_break_suspected"),
        "order": (InferenceApplicability(True, "x", 2, temporal_order_clear=False), "temporal_order_unclear"),
        "short": (InferenceApplicability(True, "x", 50), "series_too_short"),
    }
    out = {}
    for name, (app, reason) in cases.items():
        (r,) = compare_paired_forecasts(_records(d), loss="absolute_error", hac_lag=1, lag_justification="t", applicability=app)
        require(r.inference_status == "not_applicable", f"{name}: must be not_applicable, got {r.inference_status}")
        require(any(x.startswith(reason) for x in r.inference_reasons), f"{name}: reason {reason} missing in {r.inference_reasons}")
        require(r.dm_statistic is None and r.p_value_two_sided is None and r.long_run_variance is None, f"{name}: inferential fields must stay empty")
        require(r.mean_loss_difference == F(1, 2), f"{name}: descriptive comparison must be preserved")
        out[name] = list(r.inference_reasons)
    require(raises(lambda: InferenceApplicability(True, "  ", 10)), "declared justification needs text")
    require(raises(lambda: InferenceApplicability(True, "x", 1)), "min_series_length must be >= 2")
    return out


def check_lag_validation():
    d = [F(1), F(2), F(3)]
    require(raises(lambda: bartlett_hac_long_run_variance(d, -1)), "negative lag")
    require(raises(lambda: bartlett_hac_long_run_variance(d, 3)), "lag >= n")
    require(raises(lambda: bartlett_hac_long_run_variance(d, True)), "bool is not a lag")
    require(raises(lambda: compare_paired_forecasts(_records(d), loss="absolute_error", hac_lag=1, lag_justification=" ", applicability=OK)),
            "lag choice must be justified")
    require(raises(lambda: compare_paired_forecasts(_records(d), loss="log_score", hac_lag=1, lag_justification="t", applicability=OK)),
            "unknown loss must be rejected")
    (r,) = compare_paired_forecasts(_records(d), loss="absolute_error", hac_lag=5, lag_justification="t", applicability=OK)
    require(r.inference_status == "not_applicable" and any(x.startswith("lag_not_smaller_than_n") for x in r.inference_reasons), "lag >= n gates inference")
    return {"lag_checks": "ok"}


def check_predeclared_family():
    rng = np.random.default_rng(7)
    recs = []
    for s in ("s1", "s2", "s3"):
        obs = rng.normal(size=30)
        pa, pb = obs + rng.normal(scale=0.5, size=30), obs + rng.normal(scale=0.9, size=30)
        recs += [PairedForecastRecord(s, float(t), float(t + 1), 1, float(obs[t]), float(pa[t]), float(pb[t]), "A", "B", "d", "sp") for t in range(30)]
    res = compare_paired_forecasts(recs, loss="squared_error", hac_lag=1, lag_justification="t", applicability=OK)
    fam = DeclaredTestFamily("three_series", (("s1", 1), ("s2", 1), ("s3", 1)), declared_before_evaluation=True)
    rep = holm_adjust_family(res, fam)
    require(rep.status == "adjusted" and rep.adjusted_p_values == tuple(holm_adjust(list(rep.raw_p_values))), "family adjusted with Holm")
    require(raises(lambda: holm_adjust_family(res, DeclaredTestFamily("two", (("s1", 1), ("s2", 1)), True))), "results outside the family are an input error")
    require(raises(lambda: holm_adjust_family(res[:2], fam)), "missing family members are an input error")
    post_hoc = holm_adjust_family(res, DeclaredTestFamily("ph", fam.members, declared_before_evaluation=False))
    require(post_hoc.status == "not_predeclared" and post_hoc.adjusted_p_values is None, "non-predeclared family is not corrected")
    gated = compare_paired_forecasts(recs, loss="squared_error", hac_lag=1, lag_justification="t", applicability=InferenceApplicability(True, "x", 31))
    inc = holm_adjust_family(gated, fam)
    require(inc.status == "incomplete_family" and len(inc.members_without_inference) == 3, "members without inference make the family incomplete")
    return {"raw": list(rep.raw_p_values), "adjusted": list(rep.adjusted_p_values)}


def check_winner_sentence_and_json():
    d = [F(x) for x in (-1, 0, 1, 2, -2, 3, 1, 0)]
    (r,) = compare_paired_forecasts(_records(d), loss="absolute_error", hac_lag=1, lag_justification="t", applicability=OK)
    text = describe_comparison(r)
    for needle in ("'s'", "origins 0..7", "n=8", "horizon 1", "absolute_error", "mean loss difference", "asymptotic normal reference", "Not an equivalence test"):
        require(needle in text, f"sentence must contain {needle!r}: {text}")
    (g,) = compare_paired_forecasts(_records(d), loss="absolute_error", hac_lag=1, lag_justification="t", applicability=NOT_DECLARED)
    require("descriptive comparison only" in describe_comparison(g), "gated sentence must say descriptive only")
    blob = json.dumps(r.to_dict(), allow_nan=False)
    require('"equivalence_tested": false' in blob, "JSON must state that no equivalence test was made")
    json.dumps(g.to_dict(), allow_nan=False)
    return {"sentence": text}


CHECKS = [
    check_jc01_bartlett_hac_exact,
    check_jc02_holm_original_order,
    check_model_swap_flips_sign,
    check_positive_loss_scaling_leaves_dm_unchanged,
    check_constant_differences_are_degenerate,
    check_wrong_pairing_is_input_error,
    check_missing_partners_are_counted,
    check_invalid_numbers_are_reported,
    check_horizons_are_never_pooled,
    check_series_are_not_concatenated,
    check_applicability_gates,
    check_lag_validation,
    check_predeclared_family,
    check_winner_sentence_and_json,
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
    out_path = Path(__file__).with_name("verify_forecast_comparison_results.json")
    out_path.write_text(json.dumps({"n_passed": n_passed, "n_total": len(CHECKS), "results": results}, indent=2, default=str))
    print(f"Report written to {out_path}")
    return 0 if n_passed == len(CHECKS) else 1


if __name__ == "__main__":
    raise SystemExit(main())
