"""J8 verification (SCOPE_COMPOSITION_EVIDENCE_ROADMAP.md, plan section 14):
weighted split conformal under covariate shift with a bounded guarantee.

J-C15 (quantiles 3, +inf, 2), J-C16 (full 32-case enumeration with the
PRODUCTION quantile: unweighted 40951/100000, weighted 1, unbounded
89991/100000), J-C17 (concept shift: coverage 0); ties at the threshold,
common weight scaling (MR6), zero weights, invalid weights, missing
train/calibration separation, missing support, small samples, clipping and
estimated weights do not inherit the guarantee, JSON of unbounded
intervals; the corrected +inf wording in validation/conformal.py; and a
pre-declared comparison with fixed (existing split conformal) and adaptive
(existing ACI update) calibration on a covariate-shift scenario.
"""
from __future__ import annotations

import inspect
import json
import math
import sys
from fractions import Fraction as F
from itertools import product
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from scoped_correspondence.errors import ScopeViolationError
from scoped_correspondence.validation import conformal as conformal_module
from scoped_correspondence.validation.adaptive_interval_calibration import aci_update_alpha
from scoped_correspondence.validation.conformal import calibrate_split_conformal
from scoped_correspondence.validation.weighted_conformal import WHOLE_REAL_LINE, weighted_conformal_intervals, weighted_split_quantile


def require(c, m=""):
    if not c:
        raise AssertionError(m)


def raises(fn, exc=ScopeViolationError):
    try:
        fn()
    except exc:
        return True
    return False


def check_jc15_quantiles_and_test_mass():
    s = [F(1), F(2), F(3)]
    q = [weighted_split_quantile(s, [1, 1, 1], 1, F(1, 4)), weighted_split_quantile(s, [1, 1, 1], 4, F(1, 4)),
         weighted_split_quantile(s, [1, 2, 1], 1, F(2, 5))]
    require(q == [F(3), None, F(2)], f"J-C15: (3, +inf, 2), got {q}")
    require(weighted_split_quantile(s, [1, 2, 1], 1, F(2, 5)) == 2, "tie at the threshold resolves to the score reaching it")
    require(weighted_split_quantile(s, [7, 7, 7], 28, F(1, 4)) is None and weighted_split_quantile(s, [5, 10, 5], 5, F(2, 5)) == 2,
            "MR6: common positive weight scaling changes nothing")
    return {"quantiles": ["3", "+inf", "2"]}


def check_jc16_full_enumeration_with_production_quantile():
    P = {0: F(9, 10), 1: F(1, 10)}
    Q = {0: F(1, 10), 1: F(9, 10)}
    w = {x: Q[x] / P[x] for x in P}
    alpha = F(1, 5)
    tot = cu = cw = unb = F(0)
    for bits in product((0, 1), repeat=5):
        cal, tgt = bits[:4], bits[4]
        pr = Q[tgt]
        for x in cal:
            pr *= P[x]
        tot += pr
        qu = weighted_split_quantile([F(x) for x in cal], [1] * 4, 1, alpha)
        qw = weighted_split_quantile([F(x) for x in cal], [w[x] for x in cal], w[tgt], alpha)
        cu += pr * (qu is None or tgt <= qu)
        cw += pr * (qw is None or tgt <= qw)
        unb += pr * (qw is None)
    require(tot == 1 and cu == F(40951, 100000) and cw == 1 and unb == F(89991, 100000), f"J-C16: {cu}, {cw}, {unb}")
    return {"unweighted": str(cu), "weighted": str(cw), "unbounded": str(unb),
            "reading": "coverage gain bought with mostly unbounded intervals -- coverage, width and unboundedness side by side"}


def check_jc17_concept_shift():
    q = weighted_split_quantile([F(0)] * 4, [1] * 4, 1, F(1, 5))
    require(q == 0 and not (1 <= q), "J-C17: quantile 0, target residual 1 not covered")
    return {"quantile": 0, "coverage": 0}


def check_input_validation_and_separation():
    require(raises(lambda: weighted_split_quantile([1, 2], [1, -1], 1, 0.1)), "negative weight")
    require(raises(lambda: weighted_split_quantile([1, 2], [1, float("inf")], 1, 0.1)), "non-finite weight")
    require(raises(lambda: weighted_split_quantile([1, 2], [1, 1], 0, 0.1)), "zero test weight = missing support")
    require(raises(lambda: weighted_split_quantile([1, 2], [1], 1, 0.1)), "length mismatch")
    require(weighted_split_quantile([1, 2], [0, 0], 1, F(1, 10)) is None, "all-zero calibration weights: only test mass -> unbounded")
    require(weighted_split_quantile([5], [1], 1, F(1, 2)) == 5 and weighted_split_quantile([5], [1], 1, F(1, 4)) is None,
            "n = 1: finite only for alpha >= 1/2")
    require(raises(lambda: weighted_conformal_intervals([1.0], [1.0], [0.0], [1.0], 0.1, weight_provenance="known_density_ratio",
                                                       train_ids=[1, 2], calibration_ids=[2, 3])),
            "overlapping training and calibration sets are refused")
    return {"validation": "ok"}


def check_guarantee_inheritance_and_json():
    base = dict(cal_residuals=[0.1, 0.2, 0.3, 0.4], cal_weights=[1.0, 1.0, 1.0, 1.0], test_predictions=[0.0, 1.0],
                test_weights=[1.0, 9.0], alpha=0.2)
    ok = weighted_conformal_intervals(**base, weight_provenance="known_density_ratio")
    require(ok.guarantee_status == "inherited_under_stated_assumptions", "known weights inherit (under the assumptions)")
    require(ok.intervals[1] == WHOLE_REAL_LINE and ok.unbounded_fraction == 0.5, "large test weight -> whole real line, counted")
    est = weighted_conformal_intervals(**base, weight_provenance="estimated")
    clip = weighted_conformal_intervals(**base, weight_provenance="known_density_ratio", clip_at=2.0)
    require(est.guarantee_status == "not_inherited_estimated_weights" and clip.guarantee_status == "not_inherited_procedure_changed",
            "estimated or clipped weights do not inherit the guarantee")
    blob = json.dumps([iv if isinstance(iv, dict) else list(iv) for iv in ok.intervals], allow_nan=False)
    require('"whole_real_line"' in blob, "unbounded interval serialised as explicit marker")
    require(math.isclose(ok.effective_sample_size, 4.0), "effective sample size reported")
    return {"statuses": [ok.guarantee_status, est.guarantee_status, clip.guarantee_status]}


def check_conformal_inf_wording_corrected():
    doc = inspect.getdoc(conformal_module.calibrate_split_conformal)
    require("empty finite interval" not in doc and "WHOLE REAL LINE" in doc, "q = +inf documented as the whole real line, not empty")
    return {"wording": "corrected"}


def check_comparison_fixed_adaptive_weighted():
    """Pre-declared covariate-shift scenario: X ~ U[0,1] under P, density 2x
    under Q (w = 2x known), Y = eps * (0.1 + x), predictor 0, alpha = 0.1,
    n_cal = 100 from P, 50 test points from Q, 300 replications (seed 2)."""
    rng = np.random.default_rng(2)
    alpha, reps, n_cal, n_test = 0.1, 300, 100, 50
    cov = {"fixed": [], "weighted": [], "aci": []}
    unb = []
    for _ in range(reps):
        xc = rng.uniform(size=n_cal)
        rc = np.abs(rng.normal(size=n_cal) * (0.1 + xc))
        xt = np.sqrt(rng.uniform(size=n_test))  # density 2x
        yt = rng.normal(size=n_test) * (0.1 + xt)
        q_fixed = calibrate_split_conformal(rc, alpha)
        cov["fixed"].append(np.mean(np.abs(yt) <= q_fixed))
        rep = weighted_conformal_intervals(rc.tolist(), (2 * xc).tolist(), [0.0] * n_test, (2 * xt).tolist(), alpha,
                                           weight_provenance="known_density_ratio", test_observed=yt.tolist())
        cov["weighted"].append(rep.empirical_coverage)
        unb.append(rep.unbounded_fraction)
        a_t, hits, pool = alpha, [], list(rc)
        for y in yt:  # ACI on the test stream, recalibrating on the growing pool of observed residuals
            q = calibrate_split_conformal(pool, min(max(a_t, 1e-6), 1 - 1e-6))
            err = int(abs(y) > q)
            hits.append(1 - err)
            a_t = aci_update_alpha(a_t, alpha, err, 0.05)
            pool.append(abs(y))
        cov["aci"].append(np.mean(hits))
    m = {k: float(np.mean(v)) for k, v in cov.items()}
    se = {k: float(np.std(v, ddof=1) / math.sqrt(reps)) for k, v in cov.items()}
    require(m["weighted"] >= 0.9 - 3 * se["weighted"], f"weighted marginal coverage {m['weighted']:.3f} must reach 0.9 within 3 SE")
    require(m["fixed"] < m["weighted"] - 3 * se["fixed"], f"unweighted split conformal undercovers under this shift: {m['fixed']:.3f}")
    return {"mean_coverage": m, "se": se, "mean_unbounded_fraction_weighted": float(np.mean(unb)),
            "reading": "comparison under ONE pre-declared shift; ACI targets long-run sequential coverage, a different guarantee"}


CHECKS = [
    check_jc15_quantiles_and_test_mass,
    check_jc16_full_enumeration_with_production_quantile,
    check_jc17_concept_shift,
    check_input_validation_and_separation,
    check_guarantee_inheritance_and_json,
    check_conformal_inf_wording_corrected,
    check_comparison_fixed_adaptive_weighted,
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
    out_path = Path(__file__).with_name("verify_weighted_conformal_results.json")
    out_path.write_text(json.dumps({"n_passed": n_passed, "n_total": len(CHECKS), "results": results}, indent=2, default=str))
    print(f"Report written to {out_path}")
    return 0 if n_passed == len(CHECKS) else 1


if __name__ == "__main__":
    raise SystemExit(main())
