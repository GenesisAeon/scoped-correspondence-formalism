"""ON4 verification (ORGANOID_NETWORK_ROADMAP.md, plan section 10/ON4):
decoders and hierarchical comparison.

ON-C09 (code inversion: frozen decoder 0, refitted 1, information unchanged),
ON-C10 (constant decoder, prior 9/10: accuracy 9/10, balanced 1/2),
ON-C13 (best single affine threshold on XOR 3/4, XOR feature decoder 1),
ON-C17 (preparation-level SEM^2 1/2 vs wrongly pooled 2/499),
ON-C18 (five positive differences: exact sign-flip p = 1/16),
ON-C19 (group difference 1/4 - 3/20 = 1/10),
ON-C20 (train/test leakage refused; standardisation fitted on train only).
"""
from __future__ import annotations

import json
import sys
from fractions import Fraction as F
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from scoped_correspondence.errors import ScopeViolationError
from scoped_correspondence.validation.modular_networks.decoders import (
    ConstantDecoder,
    NearestMeanDecoder,
    Standardiser,
    accuracy,
    balanced_accuracy,
    best_single_affine_threshold_accuracy_xor,
    check_split,
    compare_groups,
    evaluate_split,
    preparation_summaries,
    group_mean_and_sem2,
    sign_flip_test,
    xor_feature_decoder,
)
from scoped_correspondence.validation.modular_networks.channels import exact_channel_report


def require(c, m=""):
    if not c:
        raise AssertionError(m)


def raises(fn, exc=ScopeViolationError):
    try:
        fn()
    except exc:
        return True
    return False


def check_on_c09_on_c10_scores_are_not_information():
    X_before = np.array([[1.0, 0.0], [0.0, 1.0]] * 10)
    y = [0, 1] * 10
    dec = NearestMeanDecoder().fit(X_before, y)
    X_after = X_before[:, ::-1]  # code inverted after adaptation
    frozen = accuracy(y, dec.predict(X_after))
    refit = accuracy(y, NearestMeanDecoder().fit(X_after, y).predict(X_after))
    I_before = exact_channel_report([[1, 0], [0, 1]], [0.5, 0.5], coding="identity").information_at_prior_bits
    I_after = exact_channel_report([[0, 1], [1, 0]], [0.5, 0.5], coding="identity").information_at_prior_bits
    require(frozen == 0 and refit == 1 and I_before == I_after == 1.0, "frozen 0, refitted 1, information 1 bit both")
    y10 = [1] * 9 + [0]
    pred = ConstantDecoder(1).predict([None] * 10)
    require(accuracy(y10, pred) == 0.9 and balanced_accuracy(y10, pred) == 0.5, "constant decoder: 9/10 vs balanced 1/2")
    require(raises(lambda: balanced_accuracy([1, 1], [1, 1])), "balanced accuracy needs two classes")
    return {"frozen": frozen, "refitted": refit, "accuracy": 0.9, "balanced": 0.5}


def check_on_c13_xor_linear_limit():
    require(best_single_affine_threshold_accuracy_xor() == F(3, 4), "best single affine threshold 3/4")
    require(best_single_affine_threshold_accuracy_xor(range(-6, 7)) == F(3, 4), "wider coefficient grid still 3/4 (proof in roadmap)")
    require(all(xor_feature_decoder(a, b) == (a ^ b) for a in (0, 1) for b in (0, 1)), "non-linear feature decoder 1")
    return {"linear": "3/4", "xor_feature": 1}


def check_on_c17_replication_unit():
    vals = [F(v) for v in range(5)]
    m, sem2 = group_mean_and_sem2(vals)
    pooled = [v for v in vals for _ in range(100)]
    _, wrong = group_mean_and_sem2(pooled)
    require(sem2 == F(1, 2) and wrong == F(2, 499), "preparation SEM^2 1/2; pooled trials 2/499 (pseudo-replication)")
    require(raises(lambda: group_mean_and_sem2([F(1)])), "one preparation is not a group")
    summ = preparation_summaries({"P1": [1.0, 0.0], "P2": [1.0]})
    dup = preparation_summaries({"P1": [1.0, 0.0] * 50, "P2": [1.0] * 100})
    require(len(summ) == len(dup) == 2 and summ == dup, "duplicated trials do not add preparations")
    return {"sem2_preparation": "1/2", "sem2_pooled_wrong": "2/499"}


def check_on_c18_on_c19_group_comparison():
    require(sign_flip_test([1, 1, 1, 1, 1]) == F(1, 16), "exact sign-flip p = 2/32")
    require(sign_flip_test([1, -1, 1, -1]) == 1, "balanced differences: p = 1")
    trio = {f"T{i}": v for i, v in enumerate([F(1, 4)] * 5)}
    duo = {f"D{i}": v for i, v in enumerate([F(3, 20)] * 4)}
    cmp_ = compare_groups("trio", trio, "duo", duo)
    require(cmp_.difference == F(1, 10) and cmp_.unit == "preparation", "difference 1/10 at preparation level")
    require(raises(lambda: compare_groups("a", {"P": 1, "Q": 2}, "b", {"P": 1, "R": 3})), "preparation in both groups refused")
    return {"p_sign_flip": "1/16", "difference": "1/10"}


def check_on_c20_leakage():
    require(raises(lambda: check_split(["t1", "t2"], ["t2", "t3"])), "overlapping trial ids refused")
    check_split(["t1", "t2"], ["t3"])
    X = np.array([[0.0, 1.0], [1.0, 0.0], [0.1, 0.9], [0.9, 0.1]])
    y = [0, 1, 0, 1]
    require(raises(lambda: evaluate_split(["a", "b"], X[:2], y[:2], ["b", "c"], X[2:], y[2:])), "production splitter refuses leakage")
    ev = evaluate_split(["a", "b"], X[:2], y[:2], ["c", "d"], X[2:], y[2:])
    require(ev.decoder_mode == "refitted" and ev.accuracy == 1.0, "clean split evaluates")
    train, test = np.array([[0.0], [2.0]]), np.array([[100.0]])
    s = Standardiser.fit(train)
    require(s.mean[0] == 1.0, "standardisation fitted on training only: mean 1")
    leaked = Standardiser.fit(np.vstack([train, test]))
    require(leaked.mean[0] == 34.0, "fitting on train+test would give 34 -- documented counterexample")
    return {"train_mean": 1.0, "leaked_mean": 34.0}


CHECKS = [check_on_c09_on_c10_scores_are_not_information, check_on_c13_xor_linear_limit, check_on_c17_replication_unit,
          check_on_c18_on_c19_group_comparison, check_on_c20_leakage]


def main():
    results, n_passed = {}, 0
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
    Path(__file__).with_name("verify_organoid_decoders_results.json").write_text(
        json.dumps({"n_passed": n_passed, "n_total": len(CHECKS), "results": results}, indent=2, default=str), encoding="utf-8")
    return 0 if n_passed == len(CHECKS) else 1


if __name__ == "__main__":
    raise SystemExit(main())
