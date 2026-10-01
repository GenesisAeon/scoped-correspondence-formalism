"""J3 verification (SCOPE_COMPOSITION_EVIDENCE_ROADMAP.md, plan section 9):
metamorphic relations -- compare results under transformations whose effect
is known mathematically, where individual target values are hard to state.

Each relation states its mathematical justification next to the check.
Relations whose production module does not exist yet are REGISTERED with
the package that activates them (J7, J8, J9) and reported as pending --
never counted as passed. J12 requires the full agreed set.

Implemented now:
  MR1 unit change (J-C04): reservoir solution invariant under year->day
      for random exact parameters (dimensions + linear_reservoirs).
  MR2 simultaneous permutation of micro states, macro classes and actions
      leaves controlled-Markov correspondence verdicts and defects invariant.
  MR3 identity and associativity of correspondences: composing with the
      identity map leaves the T4 residual unchanged; both bracketings of
      three linear maps give the same direct residual.
  MR4 A/B swap in the paired forecast comparison flips the sign of the mean
      difference and DM, leaves |DM| and p unchanged (random designs).
  MR5 split-conformal quantile: invariant under permutation of the
      calibration residuals and positively homogeneous under scaling.
Pending: MR6 common positive scaling of conformal weights (J8),
  MR7 swapping independent Sobol inputs with their labels (J7),
  MR8 renaming SCM variables together with the interventions (J9).
"""
from __future__ import annotations

import json
import math
import sys
from fractions import Fraction as F
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from scoped_correspondence.correspondence.contract import Correspondence, ModelRef, Scope, StateMap
from scoped_correspondence.correspondence.controlled_markov import check_controlled_correspondence, partition_indicator
from scoped_correspondence.dimensions.core import Dimension, rescale_for_base_unit_change
from scoped_correspondence.dynamics.linear_reservoirs import reservoir_step
from scoped_correspondence.validation.conformal import calibrate_split_conformal
from scoped_correspondence.validation.forecast_comparison import (
    InferenceApplicability,
    PairedForecastRecord,
    compare_paired_forecasts,
)

PENDING = {
    "MR6_weighted_conformal_common_weight_scaling": "J8",
    "MR7_sobol_input_swap_with_labels": "J7",
    "MR8_scm_variable_renaming_with_interventions": "J9",
}


def require(condition, msg=""):
    if not condition:
        raise AssertionError(msg)


def check_mr1_unit_change_reservoir():
    # Justification: M(t) = q/k + (M0 - q/k) exp(-k t); year->day maps
    # q -> q/365, k -> k/365, t -> 365 t, so q/k and k t are unchanged.
    rng = np.random.default_rng(11)
    flow, rate, time_dim = Dimension.of(M=1, T=-1), Dimension.of(T=-1), Dimension.of(T=1)
    worst = 0.0
    for _ in range(50):
        M0 = F(int(rng.integers(0, 50)), int(rng.integers(1, 9)))
        q = F(int(rng.integers(0, 40)), int(rng.integers(1, 7)))
        k = F(int(rng.integers(1, 30)), int(rng.integers(1, 11)))
        t = F(int(rng.integers(0, 20)), int(rng.integers(1, 9)))
        f = {"T": int(rng.choice([7, 12, 365, 8760]))}
        q2, k2, t2 = (rescale_for_base_unit_change(q, flow, f), rescale_for_base_unit_change(k, rate, f),
                      rescale_for_base_unit_change(t, time_dim, f))
        require(q2 / k2 == q / k and k2 * t2 == k * t, "exact invariants must hold")
        a = reservoir_step(float(M0), float(q), float(k), float(t))
        b = reservoir_step(float(M0), float(q2), float(k2), float(t2))
        worst = max(worst, abs(a - b) / max(1.0, abs(a)))
    require(worst < 1e-12, f"reservoir_step must be unit-invariant, worst rel diff {worst}")
    return {"cases": 50, "worst_rel_diff": worst}


def _random_lumpable(rng, sizes, n_actions):
    """Micro kernels that are exactly lumpable for the block partition."""
    n = sum(sizes)
    labels = [c for c, s in enumerate(sizes) for _ in range(s)]
    k = len(sizes)
    out = {}
    for a in range(n_actions):
        Q = rng.dirichlet(np.ones(k), size=k)
        P = np.zeros((n, n))
        for i in range(n):
            for c in range(k):
                members = [j for j in range(n) if labels[j] == c]
                w = rng.dirichlet(np.ones(len(members)))
                P[i, members] = Q[labels[i], c] * w
        out[f"a{a}"] = P
    return out, labels


def check_mr2_markov_permutation_invariance():
    # Justification: relabelling micro states (Pi P Pi^T, Pi C), macro classes
    # (C sigma^T) and actions is a change of names; P^a C = C Q^{omega(a)}
    # holds before iff it holds after, with the same defect sizes.
    rng = np.random.default_rng(5)
    results = []
    for trial in range(10):
        P_by, labels = _random_lumpable(rng, [2, 3, 1], 2)
        if trial % 2:  # break exactness in half of the trials
            P = P_by["a1"].copy()
            P[0] = rng.dirichlet(np.ones(P.shape[0]))
            P_by["a1"] = P
        omega = {"a0": "m0", "a1": "m1"}
        C, _ = partition_indicator(labels)
        base = check_controlled_correspondence(P_by, C, omega)
        perm = rng.permutation(len(labels))
        Pi = np.eye(len(labels))[perm]
        sigma = np.eye(C.shape[1])[rng.permutation(C.shape[1])]
        P_perm = {f"b_{a}": Pi @ P @ Pi.T for a, P in P_by.items()}
        omega_perm = {f"b_{a}": f"M_{b}" for a, b in omega.items()}
        C_perm = Pi @ C @ sigma.T
        moved = check_controlled_correspondence(P_perm, C_perm, omega_perm)
        for a in P_by:
            r0, r1 = base[a], moved[f"b_{a}"]
            require(r0.exact == r1.exact, f"trial {trial}: exactness must be invariant")
            require(abs(r0.max_defect - r1.max_defect) < 1e-12, f"trial {trial}: defect must be invariant")
        results.append(all(r.exact for r in base.values()))
    require(any(results) and not all(results), "both exact and inexact cases must occur")
    return {"trials": 10, "exact_trials": sum(results)}


def _corr():
    return Correspondence(ModelRef("A"), ModelRef("B"), StateMap(lambda x: x), Scope("test"))


def check_mr3_identity_and_associativity():
    # Justification: r_12 = (DT_2 o T_1) r_1 + a_1 (r_2 o T_1). With T_2 = id,
    # a_2 = 1, f_C = f_B the second residual vanishes and DT_2 = 1, so the
    # composite residual equals r_1. For linear maps, (T3 o T2) o T1 and
    # T3 o (T2 o T1) are the same map with the same time factor, so their
    # direct residuals coincide.
    c = _corr()
    fA, fB, fC, fD = (lambda x: -x + 0.3 * x * x), (lambda y: -2 * y), (lambda z: -4 * z), (lambda w: -1.5 * w)
    t1, t2, t3 = (lambda x: 2 * x), (lambda y: 3 * y), (lambda z: -0.5 * z)
    a1, a2, a3 = (lambda x: 0.5), (lambda y: 0.5), (lambda z: 1.7)
    ident = lambda y: y
    one = lambda y: 1.0
    worst_id = worst_assoc = 0.0
    for x in np.linspace(-1.0, 1.0, 9):
        r1_only = 2 * fA(x) - a1(x) * fB(t1(x))
        r = c.t4_composition_residual(t1, ident, fA, fB, fB, a1, one, x)
        worst_id = max(worst_id, abs(r.detail["direct"] - r1_only), abs(r.detail["r_kj"]), r.value)
        t21 = lambda xx: t2(t1(xx))
        t32 = lambda yy: t3(t2(yy))
        left = c.t4_composition_residual(t21, t3, fA, fC, fD, lambda xx: a1(xx) * a2(t1(xx)), a3, x)
        right = c.t4_composition_residual(t1, t32, fA, fB, fD, a1, lambda yy: a2(yy) * a3(t2(yy)), x)
        # r.value = |direct - composed| is the T4 identity itself: it must
        # vanish for EVERY bracketing, not only agree between them.
        worst_assoc = max(worst_assoc, abs(left.detail["direct"] - right.detail["direct"]), left.value, right.value)
    require(worst_id < 1e-7, f"identity composition must leave r_1 unchanged, worst {worst_id}")
    require(worst_assoc < 1e-6, f"both bracketings must give the same direct residual, worst {worst_assoc}")
    return {"identity_worst": worst_id, "associativity_worst": worst_assoc,
            "note": "finite-difference derivatives inside t4_composition_residual; tolerances reflect that"}


def check_mr4_forecast_ab_swap():
    # Justification: d_t changes sign under A<->B, so mean and DM flip sign;
    # the HAC variance is a quadratic form in d, hence unchanged.
    rng = np.random.default_rng(23)
    ok = InferenceApplicability(True, "metamorphic test", 2)
    worst = 0.0
    for trial in range(20):
        n = int(rng.integers(8, 60))
        obs = rng.normal(size=n)
        pa, pb = obs + rng.normal(scale=rng.uniform(0.2, 1.5), size=n), obs + rng.normal(scale=rng.uniform(0.2, 1.5), size=n)
        lag = int(rng.integers(0, 4))
        mk = lambda A, B, ia, ib: [PairedForecastRecord("s", float(t), float(t + 1), 1, float(obs[t]), float(A[t]), float(B[t]), ia, ib, "d", "s")
                                   for t in range(n)]
        (ab,) = compare_paired_forecasts(mk(pa, pb, "A", "B"), loss="absolute_error", hac_lag=lag, lag_justification="mr", applicability=ok)
        (ba,) = compare_paired_forecasts(mk(pb, pa, "B", "A"), loss="absolute_error", hac_lag=lag, lag_justification="mr", applicability=ok)
        require(ab.inference_status == ba.inference_status, "status must be invariant")
        if ab.dm_statistic is not None:
            worst = max(worst, abs(ab.dm_statistic + ba.dm_statistic), abs(ab.p_value_two_sided - ba.p_value_two_sided))
        require(math.isclose(ab.mean_loss_difference, -ba.mean_loss_difference, rel_tol=1e-12, abs_tol=1e-15), "mean flips")
    require(worst < 1e-10, f"DM must flip and p stay, worst {worst}")
    return {"trials": 20, "worst": worst}


def check_mr5_conformal_permutation_and_scaling():
    # Justification: the quantile is an order statistic of the multiset of
    # residuals (permutation invariant) and order statistics commute with
    # multiplication by c > 0.
    rng = np.random.default_rng(31)
    for _ in range(30):
        n = int(rng.integers(1, 40))
        alpha = float(rng.choice([0.05, 0.1, 0.2, 0.25, 0.5]))
        res = np.abs(rng.normal(size=n))
        q = calibrate_split_conformal(res, alpha)
        q_perm = calibrate_split_conformal(rng.permutation(res), alpha)
        c = float(rng.uniform(0.1, 10.0))
        q_scaled = calibrate_split_conformal(c * res, alpha)
        require(q == q_perm, "permutation of calibration residuals must not change q")
        if math.isinf(q):
            require(math.isinf(q_scaled), "+inf stays +inf under scaling")
        else:
            require(math.isclose(q_scaled, c * q, rel_tol=1e-12), "q must scale with c")
    return {"trials": 30}


def check_pending_relations_are_explicit():
    # Not a pass of those relations: documents which package activates them.
    require(set(PENDING.values()) == {"J7", "J8", "J9"}, "pending relations must name their activating package")
    return {"pending": PENDING, "status": "not_evaluated_yet"}


CHECKS = [
    check_mr1_unit_change_reservoir,
    check_mr2_markov_permutation_invariance,
    check_mr3_identity_and_associativity,
    check_mr4_forecast_ab_swap,
    check_mr5_conformal_permutation_and_scaling,
    check_pending_relations_are_explicit,
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
    print(f"\n{n_passed}/{len(CHECKS)} checks passed (pending relations: {sorted(PENDING)})")
    out_path = Path(__file__).with_name("verify_metamorphic_relations_results.json")
    out_path.write_text(json.dumps({"n_passed": n_passed, "n_total": len(CHECKS), "pending_relations": PENDING,
                                    "results": results}, indent=2, default=str))
    print(f"Report written to {out_path}")
    return 0 if n_passed == len(CHECKS) else 1


if __name__ == "__main__":
    raise SystemExit(main())
