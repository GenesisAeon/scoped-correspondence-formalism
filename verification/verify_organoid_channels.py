"""ON2 verification (ORGANOID_NETWORK_ROADMAP.md, plan section 10/ON2):
measurement noise and finite channels.

ON-C04 (Bayes accuracy 0.9213503964748575 at delta = sigma = 1/2; the sum
observer sees identical class distributions; sigma = 0 limits), ON-C05 (BSC
with eps = 1: 1 bit, naive 0, optimal 1), ON-C06 (equal accuracy 3/4, BSC
I ~ 0.188722 vs Z-channel I ~ 0.311278, C = log2(5/4)), ON-C07 (Y = (S, N):
1 bit; Z = N: 0 bit), ON-C08 (Y = S xor H: 0 bit; given H: 1 bit), ON-C21
(negative, non-normalised, non-finite channels rejected); a missing class
gives an unknown row; data processing: coarsening adds no information.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from scoped_correspondence.errors import ScopeViolationError
from scoped_correspondence.observation.arimoto_blahut import mutual_information_dmc
from scoped_correspondence.validation.modular_networks.channels import (
    accuracy_of_identity_decoder,
    bayes_accuracy_gaussian,
    estimated_channel_report,
    exact_channel_report,
    validate_channel,
)


def require(c, m=""):
    if not c:
        raise AssertionError(m)


def raises(fn, exc=ScopeViolationError):
    try:
        fn()
    except exc:
        return True
    return False


def check_on_c04_gaussian_bayes():
    A = bayes_accuracy_gaussian(0.5, 0.5)
    require(math.isclose(A, 0.9213503964748575, rel_tol=1e-15), f"A* = {A}")
    require(bayes_accuracy_gaussian(0.0, 0.0) == 0.5 and bayes_accuracy_gaussian(0.3, 0.0) == 1.0, "sigma = 0 limits explicit")
    require(raises(lambda: bayes_accuracy_gaussian(0.5, -0.1)) and raises(lambda: bayes_accuracy_gaussian(float("nan"), 1.0)), "invalid noise")
    rng = np.random.default_rng(4)
    n = 200000
    m0, m1 = np.array([1.5, 0.5]), np.array([0.5, 1.5])
    y0 = m0 + rng.normal(scale=0.5, size=(n, 2))
    y1 = m1 + rng.normal(scale=0.5, size=(n, 2))
    acc = 0.5 * (np.mean(np.linalg.norm(y0 - m0, axis=1) < np.linalg.norm(y0 - m1, axis=1))
                 + np.mean(np.linalg.norm(y1 - m1, axis=1) < np.linalg.norm(y1 - m0, axis=1)))
    require(abs(acc - A) < 4 * math.sqrt(A * (1 - A) / (2 * n)), f"Monte Carlo nearest-mean accuracy {acc} vs {A}")
    s0, s1 = y0.sum(axis=1), y1.sum(axis=1)
    require(abs(s0.mean() - s1.mean()) < 0.01 and abs(s0.std() - s1.std()) < 0.01, "sum observer: same distribution for both classes")
    return {"A_star": A, "monte_carlo": float(acc)}


def check_on_c05_bsc_flip():
    r = exact_channel_report([[0, 1], [1, 0]], [0.5, 0.5], coding="identity")
    require(math.isclose(r.information_at_prior_bits, 1.0) and accuracy_of_identity_decoder([[0, 1], [1, 0]], [0.5, 0.5]) == 0.0,
            "eps = 1: 1 bit, naive accuracy 0")
    require(accuracy_of_identity_decoder([[1, 0], [0, 1]], [0.5, 0.5]) == 1.0, "after relabelling (optimal decoder) accuracy 1")
    return {"I": r.information_at_prior_bits}


def check_on_c06_equal_accuracy_different_information():
    bsc, z = [[0.75, 0.25], [0.25, 0.75]], [[1.0, 0.0], [0.5, 0.5]]
    require(accuracy_of_identity_decoder(bsc, [0.5, 0.5]) == accuracy_of_identity_decoder(z, [0.5, 0.5]) == 0.75, "both 3/4")
    rb, rz = exact_channel_report(bsc, [0.5, 0.5], coding="identity"), exact_channel_report(z, [0.5, 0.5], coding="identity")
    require(abs(rb.information_at_prior_bits - 0.188722) < 1e-6 and abs(rz.information_at_prior_bits - 0.311278) < 1e-6, "MI differ")
    require(rz.capacity_converged and math.isclose(rz.capacity_bits, math.log2(5 / 4), rel_tol=1e-8), f"C = log2(5/4), got {rz.capacity_bits}")
    return {"I_bsc": rb.information_at_prior_bits, "I_z": rz.information_at_prior_bits, "C_z": rz.capacity_bits}


def check_on_c07_on_c08_and_data_processing():
    # Y = (S, N) with fair independent N: outputs (s, n) in order 00, 01, 10, 11
    Qy = [[0.5, 0.5, 0, 0], [0, 0, 0.5, 0.5]]
    Qz = [[0.5, 0.5], [0.5, 0.5]]  # Z = N
    require(math.isclose(mutual_information_dmc([0.5, 0.5], Qy), 1.0) and abs(mutual_information_dmc([0.5, 0.5], Qz)) < 1e-15, "1 vs 0 bit")
    # Y = S xor H: marginal channel is uniform; given H it is a permutation
    Qxor = [[0.5, 0.5], [0.5, 0.5]]
    given_h = [mutual_information_dmc([0.5, 0.5], [[1, 0], [0, 1]]), mutual_information_dmc([0.5, 0.5], [[0, 1], [1, 0]])]
    require(abs(mutual_information_dmc([0.5, 0.5], Qxor)) < 1e-15 and all(math.isclose(g, 1.0) for g in given_h), "0 bit; given H 1 bit")
    rng = np.random.default_rng(9)
    for _ in range(20):
        Q = rng.dirichlet(np.ones(6), size=3)
        coarse = np.stack([Q[:, :2].sum(1), Q[:, 2:].sum(1)], axis=1)
        p = rng.dirichlet(np.ones(3))
        require(mutual_information_dmc(p, coarse) <= mutual_information_dmc(p, Q) + 1e-12, "coarsening adds no information")
    return {"I_SY": 1.0, "I_SZ": 0.0, "I_xor": 0.0, "I_xor_given_H": 1.0}


def check_on_c21_rejections_and_unknown_rows():
    require(raises(lambda: validate_channel([[1.5, -0.5], [0.5, 0.5]])), "negative entry")
    require(raises(lambda: validate_channel([[0.5, 0.3], [0.5, 0.5]])), "row not normalised (no silent renormalisation)")
    require(raises(lambda: validate_channel([[float("nan"), 1.0], [0.5, 0.5]])), "non-finite entry")
    rep = estimated_channel_report([[8, 2], [0, 0]], [0.5, 0.5], coding="threshold", window="w1", memory_assumption="reset per trial")
    require(rep.status == "unknown_row" and rep.rows[1] is None and rep.information_at_prior_bits is None and rep.capacity_bits is None,
            "a missing class gives an unknown row, no MI, no capacity")
    pc = estimated_channel_report([[8, 0], [1, 9]], [0.5, 0.5], coding="threshold", window="w1", memory_assumption="reset per trial", pseudocount=1)
    require(pc.status == "estimated" and any("pseudocount" in n for n in pc.notes) and pc.rows[0] == (0.9, 0.1), "pseudocounts visible")
    return {"unknown_row_status": rep.status}


CHECKS = [check_on_c04_gaussian_bayes, check_on_c05_bsc_flip, check_on_c06_equal_accuracy_different_information,
          check_on_c07_on_c08_and_data_processing, check_on_c21_rejections_and_unknown_rows]


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
    Path(__file__).with_name("verify_organoid_channels_results.json").write_text(
        json.dumps({"n_passed": n_passed, "n_total": len(CHECKS), "results": results}, indent=2, default=str), encoding="utf-8")
    return 0 if n_passed == len(CHECKS) else 1


if __name__ == "__main__":
    raise SystemExit(main())
