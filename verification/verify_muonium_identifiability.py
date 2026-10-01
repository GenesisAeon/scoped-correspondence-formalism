"""MU4 verification (MUONIUM_GRAVITY_ROADMAP.md, plan section 10/MU4):
the eight identifiability counterexamples of plan section 7.

Kontrollen MU-C09 (rank 1 vs 2; A = 1, b = 2 from p = (3, 6)), MU-C10
(three parameters, rank 2 despite several flight times), MU-C11 (even
offset cancels, odd bias stays), MU-C14 (periodic alias, count level),
MU-C17 (commensurate times keep common aliases). The tests show explicitly
that more flight times and reversals do NOT remove every disturbance, and
that a finite observation fibre is no statement about all real parameters.
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
from scoped_correspondence.identifiability.exact_linear import analyze_affine_identifiability
from scoped_correspondence.identifiability.structural_reports import finite_candidate_fibre
from scoped_correspondence.muonium.forward import ForwardModel, VelocityClass, equal_time_bins
from scoped_correspondence.muonium.identifiability import (
    counterphase_contrast,
    offset_degeneracy,
    parity_table,
    unwrapped_phase_report,
    velocity_calibration_bias,
)
from scoped_correspondence.muonium.likelihood import multistart_fit

TAU, D, V = 2.2e-6, 100e-9, 2180.0
T = 2 * TAU
BINS = equal_time_bins(4.0, [0.0, math.pi / 2, math.pi, 3 * math.pi / 2])


def model(L, classes, tau=TAU):
    return ForwardModel(L=L, d=D, tau=tau, classes=tuple(classes), rate=2.0e6, background=1.0)


def require(c, m=""):
    if not c:
        raise AssertionError(m)


def raises(fn, exc=ScopeViolationError):
    try:
        fn()
    except exc:
        return True
    return False


def check_1_offset_degeneracy():
    r = offset_degeneracy(F(3))
    require(set(r.not_identifiable) == {"a", "phi0"} and r.identifiable == ("K a + phi0",) and r.witnesses[0]["rank"] == 1,
            "one flight time: only K a + phi0")
    m = model(V * T, [VelocityClass(V, 1.0, transmission=0.5, contrast=0.35)])
    c = 40.0
    shifted = ForwardModel(L=m.L, d=D, tau=TAU, classes=m.classes, rate=m.rate, background=m.background, phi0=-m.K(V) * c)
    require(all(math.isclose(x, y, rel_tol=1e-12) for x, y in zip(m.expected_counts(9.81, BINS), shifted.expected_counts(9.81 + c, BINS))),
            "count level: (a + c, phi0 - K c) gives identical expected counts -- any number of counts")
    return {"symmetry": r.witnesses[0]["symmetry"]}


def check_2_and_mu_c09_two_flight_times():
    one, _ = unwrapped_phase_report([1])
    two, r = unwrapped_phase_report([1, 4])
    require(one.witnesses[0]["rank"] == 1 and two.witnesses[0]["rank"] == 2 and set(two.identifiable) == {"A", "b"}, "rank 1 vs 2")
    sol = analyze_affine_identifiability([[1, 1], [4, 1]], observation=[3, 6])
    require(sol.particular_solution == (1, 2), f"p = (3, 6) -> A = 1, b = 2, got {sol.particular_solution}")
    require("common offset b" in two.assumptions and "correct calibration of u" in two.assumptions, "assumptions stated")
    return {"A_b": [str(x) for x in sol.particular_solution]}


def check_3_mu_c14_mu_c17_periodic_aliases():
    m = model(V * T, [VelocityClass(V, 1.0, transmission=0.5, contrast=0.35)])
    alias = D / T ** 2
    require(all(math.isclose(x, y, rel_tol=1e-9) for x, y in zip(m.expected_counts(9.81, BINS), m.expected_counts(9.81 + alias, BINS))),
            "a -> a + d/T^2: same expected counts")
    m2 = model(V * 2 * T, [VelocityClass(V, 1.0, transmission=0.5, contrast=0.35)])  # T2 = 2 T -> K2 = 4 K1
    require(math.isclose(m2.K(V), 4 * m.K(V), rel_tol=1e-12), "K2 = 4 K1")
    both = lambda a: m.expected_counts(a, BINS) + m2.expected_counts(a, BINS)
    require(all(math.isclose(x, y, rel_tol=1e-9) for x, y in zip(both(9.81), both(9.81 + alias))),
            "commensurate flight times keep the common alias d/T1^2")
    unwrapped, _ = unwrapped_phase_report([1, 4])
    require(unwrapped.witnesses[0]["rank"] == 2, "while the UNWRAPPED linear model has full rank -- full rank is not global uniqueness")
    return {"alias": alias}


def check_4_mu_c10_acceleration_like_disturbance():
    r, a = unwrapped_phase_report([1, 4, 9, 16], n_disturbances=1)
    require(a.rank == 2 and set(r.not_identifiable) == {"A", "B1"} and "A + B1" in r.identifiable,
            "three parameters, rank 2: A and B inseparable however many flight times")
    return {"rank": a.rank}


def check_5_mu_c11_reversal_parity():
    even_only = parity_table({"offset": "even"})
    require(even_only.identifiable == ("A",) and even_only.witnesses[0]["even_cancel_in_difference"] == ["offset"], "even offset cancels")
    with_odd = parity_table({"offset": "even", "magnetic_gradient": "odd"})
    require(with_odd.identifiable == ("A + magnetic_gradient",) and "A" in with_odd.not_identifiable, "odd bias stays with gravity")
    require(any("does not prove gravity" in n for n in with_odd.notes), "no 'reversal proves gravity' statement")
    require(raises(lambda: parity_table({"x": "mixed"})), "parity must be declared even or odd")
    rows = analyze_affine_identifiability([[1, 1, 1], [-1, -1, 1]])
    require(rows.rank == 2, "exact: (A, B, b) with p_s = s(A+B) + b has rank 2 of 3")
    return {"odd_remaining": with_odd.witnesses[0]["odd_remain_with_gravity"]}


def check_6_velocity_calibration():
    require(velocity_calibration_bias(F(1, 100)) == F(10201, 10000), "1 % velocity error -> 2.01 % acceleration error")
    require(raises(lambda: velocity_calibration_bias(0.01)), "exact input required")
    return {"ratio": "10201/10000"}


def check_7_contrast_loss():
    absF, mean_phase = counterphase_contrast()
    require(absF == 0.0 and math.isclose(mean_phase, math.pi / 2), "equal-weight 0 and pi: |F| = 0; the phase mean pi/2 pretends information")
    absF2, _ = counterphase_contrast((F(3, 4), F(1, 4)))
    require(math.isclose(absF2, 0.5), "unequal weights: partial contrast 1/2")
    return {"F": absF}


def check_8_selection_bias():
    v_slow, v_fast = 1500.0, 3000.0
    L = V * T
    classes = [VelocityClass(v_slow, 0.5, transmission=0.5, contrast=0.35), VelocityClass(v_fast, 0.5, transmission=0.5, contrast=0.35)]
    truth = model(L, classes)
    a_true = 9.81
    naive = model(L, classes, tau=1.0)  # tau effectively infinite: fits with the INCOMING mixture
    # Compare modulation phases (rate normalisations differ between the two models and are not the point):
    ph_truth = truth.modulation_phase(a_true)
    fit = multistart_fit(lambda x: (math.remainder(naive.modulation_phase(x[0]) - ph_truth, 2 * math.pi)) ** 2,
                         ["a"], [(a_true - 200.0, a_true + 200.0)], n_starts=8)
    bias = fit.best.x[0] - a_true
    require(abs(bias) > 1.0, f"fitting with the incoming mixture biases a (bias {bias})")
    det = truth.detected_weights()
    require(det[0] < 0.5 < det[1], "slow atoms decay more: the detected mixture is shifted to fast atoms")
    return {"bias_m_per_s2": bias, "detected_weights": det}


def check_finite_fibre_is_not_a_continuum_proof():
    m = model(V * T, [VelocityClass(V, 1.0, transmission=0.5, contrast=0.35)])
    K = m.K(V)
    cands = [(a, -K * (a - 9.81)) for a in (0.0, 9.81, 20.0)] + [(9.81, 0.3)]
    obs = lambda c: tuple(round(x, 6) for x in ForwardModel(L=m.L, d=D, tau=TAU, classes=m.classes, rate=m.rate,
                                                             background=m.background, phi0=c[1]).expected_counts(c[0], BINS))
    fib, rep = finite_candidate_fibre("muonium (a, phi0)", cands, obs, obs((9.81, 0.0)))
    require(len(fib.fiber) == 3 and (9.81, 0.3) not in fib.fiber, f"three listed candidates on the ridge share the observation: {fib.fiber}")
    require(any("LISTED candidates only" in n for n in rep.notes), "finite fibre is a statement about the list only")
    return {"fibre_size": len(fib.fiber)}


CHECKS = [
    check_1_offset_degeneracy,
    check_2_and_mu_c09_two_flight_times,
    check_3_mu_c14_mu_c17_periodic_aliases,
    check_4_mu_c10_acceleration_like_disturbance,
    check_5_mu_c11_reversal_parity,
    check_6_velocity_calibration,
    check_7_contrast_loss,
    check_8_selection_bias,
    check_finite_fibre_is_not_a_continuum_proof,
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
    out_path = Path(__file__).with_name("verify_muonium_identifiability_results.json")
    out_path.write_text(json.dumps({"n_passed": n_passed, "n_total": len(CHECKS), "results": results}, indent=2, default=str))
    print(f"Report written to {out_path}")
    return 0 if n_passed == len(CHECKS) else 1


if __name__ == "__main__":
    raise SystemExit(main())
