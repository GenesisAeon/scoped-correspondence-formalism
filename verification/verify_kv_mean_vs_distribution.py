"""KV1 verification: "Mittelwert gegen Verteilung" (Kosmische Vererbung, Plan §6.2 / §8).

Control cases MV-K1..MV-K4 of KOSMISCHE_VERERBUNG_SCF_ROADMAP.md, hand-derived and independently
recomputed with Fractions BEFORE this file was written
(verification/plan_controls/kv_series_independent_controls.py, no SCF import), now checked against
the production APIs (epistemic/observation_fibers.py, correspondence/controlled_markov.py).

Model: two equal-mass gas parcels, metallicity in units u = 0.01 on the grid {0,1,2}; micro state
(z1, z2) with index 3*z1 + z2. Observation h = mean metallicity, target f0 = pristine mass fraction.
One star-formation step picks a parcel uniformly (1/2) and maps z -> g(z).

Result status: synthetic_only. Mathematical structure only -- no astrophysical or JWST claim.
"""
from __future__ import annotations

import itertools
import json
import sys
from fractions import Fraction as F
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from scoped_correspondence.correspondence.controlled_markov import (
    check_controlled_correspondence,
    check_lumpability,
    partition_indicator,
)
from scoped_correspondence.epistemic.observation_fibers import (
    identified_values,
    macro_dynamics_and_observability,
    observation_fiber,
)
from scoped_correspondence.epistemic.records import FiniteDomainSpec
from scoped_correspondence.errors import ScopeViolationError

STATES = tuple(itertools.product(range(3), repeat=2))
INDEX = {s: 3 * s[0] + s[1] for s in STATES}


def require(condition, msg=""):
    if not condition:
        raise AssertionError(msg)


def mean(s):
    return F(s[0] + s[1], 2)


def f0(s):
    return F(sum(1 for z in s if z == 0), 2)


def multiset(s):
    return tuple(sorted(s))


def _domain():
    return FiniteDomainSpec(
        id="kv_two_parcels", candidates=STATES,
        scope_text="two equal-mass parcels, Z in units 0.01 on {0,1,2}", arithmetic_kind="rational",
        units="Z in units of 0.01",
    )


def step_kernel(g):
    P = np.zeros((9, 9))
    for s in STATES:
        for i in (0, 1):
            t = list(s)
            t[i] = g(s[i])
            P[INDEX[s], INDEX[tuple(t)]] += 0.5
    return P


def mixing_kernel():
    P = np.zeros((9, 9))
    for s in STATES:
        same = [t for t in STATES if sum(t) == sum(s)]
        for t in same:
            P[INDEX[s], INDEX[t]] = 1.0 / len(same)
    return P


K2 = step_kernel(lambda z: 2 if z == 0 else min(z + 1, 2))  # Pop-III-sensitive yield
K3 = step_kernel(lambda z: min(z + 1, 2))                   # Z-blind, saturating yield
K4 = mixing_kernel()                                        # sum-preserving mixing
C_MEAN, ORDER_MEAN = partition_indicator([mean(s) for s in STATES])
C_MS, _ = partition_indicator([multiset(s) for s in STATES])


# ---------------------------------------------------------------- MV-K1 (observation fibers)
EXPECTED_K1 = {
    F(0): ({(0, 0)}, {F(1)}),
    F(1, 2): ({(0, 1), (1, 0)}, {F(1, 2)}),
    F(1): ({(0, 2), (1, 1), (2, 0)}, {F(0), F(1, 2)}),
    F(3, 2): ({(1, 2), (2, 1)}, {F(0)}),
    F(2): ({(2, 2)}, {F(0)}),
}


def check_k1_fibers_and_identified_f0_sets():
    """Fiber and f0 value set for every observable mean value; point-identified everywhere except y=1."""
    out = {}
    for y, (fib_exp, f0_exp) in EXPECTED_K1.items():
        fib = observation_fiber(_domain(), [], mean, y)
        require(fib.search_complete and fib.all_candidates_scanned, f"y={y}: scan must be complete")
        require(set(fib.fiber) == fib_exp, f"y={y}: fiber {set(fib.fiber)} != {fib_exp}")
        q = identified_values(fib, f0)
        require(set(q.values) == f0_exp, f"y={y}: f0 values {q.values} != {f0_exp}")
        require(q.point_identified == (len(f0_exp) == 1), f"y={y}: point_identified={q.point_identified}")
        out[str(y)] = {"fiber": sorted(fib.fiber), "f0": sorted(str(v) for v in q.values), "point_identified": q.point_identified}
    return out


def check_k1_y1_is_a_set_not_an_interval():
    """At y=1, f0 is {0, 1/2}: two values, reported as a set; min/max are convenience fields only."""
    q = identified_values(observation_fiber(_domain(), [], mean, F(1)), f0)
    require(not q.point_identified, "f0 must NOT be point-identified at y=1")
    require(len(q.values) == 2 and set(q.values) == {F(0), F(1, 2)}, f"expected exactly {{0, 1/2}}, got {q.values}")
    require(F(1, 4) not in q.values, "an interval midpoint must not appear as an identified value")
    require(any("NOT point-identified" in n for n in q.notes), "the report must say NOT point-identified")
    return {"values": sorted(str(v) for v in q.values), "min": str(q.min_value), "max": str(q.max_value)}


def check_k1_pristine_claim_not_identifiable_at_y1():
    """The boolean claim 'pristine gas present' (f0 > 0) takes both truth values in the fiber of y=1."""
    q = identified_values(observation_fiber(_domain(), [], mean, F(1)), lambda s: f0(s) > 0)
    require(not q.point_identified and set(q.values) == {False, True}, f"expected {{False, True}}, got {q.values}")
    q0 = identified_values(observation_fiber(_domain(), [], mean, F(1, 2)), lambda s: f0(s) > 0)
    require(q0.point_identified and q0.values == (True,), f"at y=1/2 the claim must be identified True, got {q0.values}")
    return {"y=1": sorted(q.values), "y=1/2": list(q0.values)}


def check_k1_empty_fiber_is_mismatch_not_identification():
    """y=5/2 lies outside the model space: empty fiber, flagged, never 'identified'."""
    fib = observation_fiber(_domain(), [], mean, F(5, 2))
    require(fib.search_complete and fib.empty_fiber, "y=5/2 must give a complete scan with an empty fiber")
    require(any("mismatch" in n for n in fib.notes), "empty fiber must be flagged as a mismatch")
    q = identified_values(fib, f0)
    require(not q.point_identified and q.values == (), "an empty fiber must not identify anything")
    return {"notes": list(fib.notes)}


def check_k1_joint_observation_identifies_f0():
    """Observing (mean, f0) point-identifies f0 everywhere (trivially) and gives 6 classes = 6 multisets.
    Valid for 2 parcels on a 3-point grid only; not a general identity."""
    h2 = lambda s: (mean(s), f0(s))
    ys = sorted({h2(s) for s in STATES})
    require(len(ys) == 6 and len({multiset(s) for s in STATES}) == 6, "expected 6 joint classes = 6 multisets")
    for y in ys:
        require(identified_values(observation_fiber(_domain(), [], h2, y), f0).point_identified, f"{y}: not identified")
    return {"n_joint_classes": len(ys)}


# ---------------------------------------------------------------- MV-K2..K4 (dynamics)
def check_kernels_row_stochastic_and_convention_guard():
    """All kernels are row-stochastic; the transposed (column-convention) K2 is rejected (Plan §8 boundary)."""
    for name, P in (("K2", K2), ("K3", K3), ("K4", K4)):
        require(np.all(P >= 0) and np.allclose(P.sum(axis=1), 1.0), f"{name} must be row-stochastic")
    require(not np.allclose(K2.T.sum(axis=1), 1.0), "K2^T must NOT be row-stochastic (else the guard proves nothing)")
    try:
        check_lumpability(K2.T, C_MEAN)
    except ScopeViolationError:
        return {"transposed_K2_rejected": True}
    raise AssertionError("a column-stochastic kernel must be rejected by check_lumpability")


def check_k2_pop3_mean_not_lumpable_multiset_exact():
    """Pop-III-sensitive yield: mean partition max_defect = 1 in class h=1, column h=3/2
    ((0,2) -> h=1 or h=2 each 1/2; (1,1) -> h=3/2 surely); multiset partition exact."""
    exact, d, worst, _ = check_lumpability(K2, C_MEAN)
    require(not exact and abs(d - 1.0) < 1e-12, f"expected defect 1, got exact={exact} d={d}")
    require(worst.macro_class == ORDER_MEAN.index(F(1)), f"worst class must be h=1, got {ORDER_MEAN[worst.macro_class]}")
    require(worst.macro_column == ORDER_MEAN.index(F(3, 2)), f"worst column must be h=3/2, got {ORDER_MEAN[worst.macro_column]}")
    require(set(worst.micro_row_pair) == {INDEX[(0, 2)], INDEX[(1, 1)]}, f"worst rows must be (0,2),(1,1); got {worst.micro_row_pair}")
    exact_ms, d_ms, _, _ = check_lumpability(K2, C_MS)
    require(exact_ms and d_ms < 1e-12, f"multiset partition must be exact, got d={d_ms}")
    return {"mean_defect": d, "worst_rows": list(worst.micro_row_pair), "multiset_defect": d_ms}


def check_k3_saturation_alone_breaks_mean_sufficiency():
    """Z-blind saturating yield g(z)=min(z+1,2): mean partition defect 1/2 (class h=1), multiset exact.
    Counter-model: mean insufficiency alone is NOT evidence of Pop-III-specific physics."""
    exact, d, worst, _ = check_lumpability(K3, C_MEAN)
    require(not exact and abs(d - 0.5) < 1e-12, f"expected defect 1/2, got exact={exact} d={d}")
    require(worst.macro_class == ORDER_MEAN.index(F(1)), f"worst class must be h=1, got {ORDER_MEAN[worst.macro_class]}")
    i, j = worst.micro_row_pair
    bs = K3 @ C_MEAN
    require(abs(abs(bs[i, worst.macro_column] - bs[j, worst.macro_column]) - 0.5) < 1e-12, "reported rows must differ by 1/2")
    exact_ms, d_ms, _, _ = check_lumpability(K3, C_MS)
    require(exact_ms, f"multiset partition must be exact, got d={d_ms}")
    return {"mean_defect": d, "multiset_defect": d_ms}


def check_k4_exact_mean_dynamics_but_pristine_event_not_observable():
    """Sum-preserving mixing: mean partition exactly lumpable, yet 'pristine present' = {0,1,2,3,6}
    is not a union of mean classes -- dynamics and event observability are separate (K8)."""
    event = [INDEX[s] for s in STATES if f0(s) > 0]
    require(event == [0, 1, 2, 3, 6], f"event indices {event}")
    rep = macro_dynamics_and_observability({"mix": K4}, C_MEAN, {"mix": "mix"}, event)
    require(rep.dynamics_exact, "mixing must give exact mean dynamics")
    require(not rep.event_is_union_of_classes, "the pristine event must NOT be a union of mean classes")
    require(rep.notes, "the report must state that exact dynamics does not imply event observability")
    rep_ms = macro_dynamics_and_observability({"mix": K4}, C_MS, {"mix": "mix"}, event)
    require(rep_ms.event_is_union_of_classes, "under the multiset partition the event must be observable")
    return {"mean_dynamics_exact": rep.dynamics_exact, "event_union_mean": rep.event_is_union_of_classes,
            "event_union_multiset": rep_ms.event_is_union_of_classes}


def check_negative_control_mixing_plus_pop3_not_exact_per_action():
    """Two declared micro actions sharing ONE macro action ('step'): mixing (exact alone) and Pop-III
    yield (not exact). The joint check must report non-exact for BOTH -- no averaging that hides one."""
    reps = check_controlled_correspondence({"mix": K4, "pop3": K2}, C_MEAN, {"mix": "step", "pop3": "step"})
    require(not reps["mix"].exact and not reps["pop3"].exact, "shared macro action must fail for both")
    reps_sep = check_controlled_correspondence({"mix": K4, "pop3": K2}, C_MEAN, {"mix": "m", "pop3": "p"})
    require(reps_sep["mix"].exact and not reps_sep["pop3"].exact, "separately declared: mix exact, pop3 not")
    return {"shared_defect": reps["pop3"].max_defect, "separate_mix_exact": reps_sep["mix"].exact}


CHECKS = [
    check_k1_fibers_and_identified_f0_sets,
    check_k1_y1_is_a_set_not_an_interval,
    check_k1_pristine_claim_not_identifiable_at_y1,
    check_k1_empty_fiber_is_mismatch_not_identification,
    check_k1_joint_observation_identifies_f0,
    check_kernels_row_stochastic_and_convention_guard,
    check_k2_pop3_mean_not_lumpable_multiset_exact,
    check_k3_saturation_alone_breaks_mean_sufficiency,
    check_k4_exact_mean_dynamics_but_pristine_event_not_observable,
    check_negative_control_mixing_plus_pop3_not_exact_per_action,
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
    out_path = Path(__file__).with_name("verify_kv_mean_vs_distribution_results.json")
    out_path.write_text(json.dumps({"n_passed": n_passed, "n_total": len(CHECKS), "evidence_kind": "exhaustive_finite",
                                    "empirical_status": "synthetic_only", "results": results}, indent=2, default=str),
                        encoding="utf-8")
    print(f"Report written to {out_path}")
    return 0 if n_passed == len(CHECKS) else 1


if __name__ == "__main__":
    raise SystemExit(main())
