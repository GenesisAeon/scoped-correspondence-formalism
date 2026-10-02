"""Cross-check of the delivered MU/candidate oracle against PRODUCTION code.

The external oracle `independent_controls.py` (in
prompts/Answers/nicht_stationäre_Treiber/SCF_MYONIUM_UND_KANDIDATEN_CLAUDE_PAKET.zip,
delivered with SCF_REVIEW_J_SERIES_6b3a331_CLAUDE.md §8; SHA-256 checked,
fresh run 29/29 identical) was missing when MU0-MU7 and the candidate pilots
were implemented: those were tested against self-derived values only
(DEEP_RESEARCH_BACKLOG.md, A). This script compares the oracle's recorded
values (verification/plan_controls/mu_candidate_oracle_results.json, a
byte-identical copy of the ZIP's independent_control_results.json) with what
the production modules compute for the same inputs.

The oracle is NOT imported or re-run here (it is not production code and
not ours); only its recorded numbers are read. SA-C01..C04 have no
production counterpart (SA0 was documentation only) and are listed as
not_applicable, never as passed.
"""
from __future__ import annotations

import json
import math
import sys
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from scoped_correspondence.errors import ScopeViolationError
from scoped_correspondence.muonium.design import events_for_relative_precision, phase_fisher, sigma_vs_flight_time
from scoped_correspondence.muonium.identifiability import counterphase_contrast, unwrapped_phase_report, velocity_calibration_bias
from scoped_correspondence.muonium.kinematics import Geometry, delta_g, eta, relative_displacement, single_path_drop, survival
from scoped_correspondence.muonium.likelihood import poisson_deviance, poisson_nll
from scoped_correspondence.validation.polyhedral_observation_pilot import (
    c4_plus_c4,
    c8,
    coarse_observation,
    coplanar_exact,
    euler_characteristic,
    euler_genus,
    order_and_determinant,
    refined_observation,
)
from scoped_correspondence.validation.stellar_pulse_observation import (
    peak_time,
    release_state,
    single_band_flux,
    two_band_identifiability,
    wind_transformed_radius,
)

ORACLE = ROOT / "verification" / "plan_controls" / "mu_candidate_oracle_results.json"


def require(c, m=""):
    if not c:
        raise AssertionError(m)


def close(a, b, rel=1e-12, m=""):
    require(math.isclose(float(a), float(b), rel_tol=rel, abs_tol=1e-15), f"{m}: {a} vs oracle {b}")


def oracle():
    d = json.loads(ORACLE.read_text(encoding="utf-8"))
    require(d["counts"] == {"passed": 29, "failed": 0}, "oracle record must be the delivered 29/29 run")
    return {c["id"]: c["values"] for c in d["cases"]}


# SI reference geometry of the oracle (MU-C03): g = 9.81, tau = 2.2 us, T = 2 tau, d = 100 nm, v = 2180 m/s
G, TAU, T, D, V = 9.81, 2.2e-6, 4.4e-6, 1e-7, 2180.0
GEOM = Geometry(L=V * T, d=D, v=V)


def check_mu_kinematics(o):
    require(delta_g(F(11, 10), 1) == F(o["MU-C01"]["delta"]) and eta(F(11, 10), 1) == F(o["MU-C01"]["eta"]), "MU-C01")
    m3 = o["MU-C03"]["values"] if "values" in o["MU-C03"] else o["MU-C03"]
    close(GEOM.L, m3["gap_m"], m="MU-C03 gap")
    close(single_path_drop(G, TAU) * 1e12, m3["one_lifetime_sag_pm"], m="MU-C03 sag")
    close(relative_displacement(G, T) * 1e12, m3["relative_displacement_pm"], m="MU-C03 displacement")
    close(F(o["MU-C02"]["displacement_m_exact"]), relative_displacement(F(981, 100), F(44, 10 ** 7)), m="MU-C02 exact")
    require(relative_displacement(F(981, 100), F(44, 10 ** 7)) == F(o["MU-C02"]["displacement_m_exact"]), "MU-C02 exact equality")
    close(survival(GEOM, TAU), o["MU-C04"]["survival"], m="MU-C04 survival")
    s1 = sigma_vs_flight_time(1.0, 1.0, budget="incoming_atoms")
    for x, ref in zip((1, 2, 3), o["MU-C04"]["sigma_factors_x_1_2_3"]):
        close(sigma_vs_flight_time(float(x), 1.0, budget="incoming_atoms") / s1 * math.e, ref, m=f"MU-C04 sigma x={x}")
    best = min((sigma_vs_flight_time(t / 100, 1.0, budget="incoming_atoms"), t / 100) for t in range(50, 500))
    close(best[1], o["MU-C04"]["optimal_T_over_tau"], m="MU-C04 optimum")
    close(2 * math.pi / GEOM.K(), o["MU-C14"]["acceleration_alias_step_m_per_s2"], rel=1e-12, m="MU-C14 alias d/T^2")
    return {"MU-C01..C04, C14": "match"}


def check_mu_inference(o):
    require(float(velocity_calibration_bias(F(1, 100)) - 1) == o["MU-C05"]["relative_bias_for_1pct_velocity_error"], "MU-C05")
    require(counterphase_contrast()[0] <= o["MU-C06"]["cancelling_phasor_modulus"] + 1e-15, "MU-C06 cancelling phasor")
    require(poisson_nll([0], [0.0]) == o["MU-C08"]["nll_zero_zero"] and math.isinf(poisson_nll([1], [0.0])), "MU-C08 boundary")
    close(poisson_deviance([0], [2.0]), o["MU-C08"]["deviance_zero_two"], m="MU-C08 deviance")
    r1, r2 = unwrapped_phase_report([1])[1], unwrapped_phase_report([1, 4])[1]
    require((r1.rank, r2.rank) == (o["MU-C09"]["single_time_rank"], o["MU-C09"]["two_time_rank"]), "MU-C09 ranks")
    r3 = unwrapped_phase_report([1, 4, 9], n_disturbances=1)[1]
    require(r3.rank == o["MU-C10"]["rank"] and len(r3.null_space) == o["MU-C10"]["parameter_count"] - o["MU-C10"]["rank"], "MU-C10")
    four = phase_fisher([100] * 4, [0, math.pi / 2, math.pi, 3 * math.pi / 2], 0.2)
    quad = phase_fisher([100] * 4, [math.pi / 2, 3 * math.pi / 2] * 2, 0.2)
    close(four, o["MU-C12"]["I_phi_four_steps"], m="MU-C12 four steps")
    close(quad, o["MU-C12"]["I_phi_quadrature"], m="MU-C12 quadrature")
    phase = GEOM.K() * G
    close(phase, o["MU-C13"]["phase_1pct_rad"] / 0.01, rel=1e-12, m="MU-C13 phase")
    close(events_for_relative_precision(0.01, G, 0.35, GEOM.K()), o["MU-C13"]["detected_signal_events_for_1pct"], rel=1e-12, m="MU-C13 N")
    require(phase_fisher([100] * 4, [0, 1, 2, 3], 0.0) == o["MU-C16"]["fisher_information"], "MU-C16 zero contrast")
    return {"MU-C05, C06, C08..C10, C12, C13, C16": "match"}


def check_candidates(o):
    V_, E_, F_ = 12, 24, 8
    require(euler_characteristic(V_, E_, F_) == o["TP-C01"]["chi"], "TP-C01 chi")
    require(euler_genus(V_, E_, F_, closed=True, connected=True, orientable=True, vertex_links_are_circles=True) == o["TP-C01"]["conditional_genus"], "TP-C01 genus")
    require(coarse_observation(c8()) == coarse_observation(c4_plus_c4()), "TP-C02 same counts and degrees")
    require(refined_observation(c8())[-1] == len(o["TP-C02"]["component_sizes_C8"])
            and refined_observation(c4_plus_c4())[-1] == len(o["TP-C02"]["component_sizes_two_C4"]), "TP-C02 components")
    order, det = order_and_determinant([[0, -1, 0], [1, 0, 0], [0, 0, -1]])
    require((order, det) == (o["TP-C03"]["order"], o["TP-C03"]["generator_determinant"]), "TP-C03")
    eps = F(o["TP-C04"]["nonzero_determinant"])
    require(coplanar_exact([(0, 0, 0), (1, 0, 0), (0, 1, 0), (1, 1, 0)]) and not coplanar_exact([(0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, eps)]), "TP-C04")
    s = release_state(2.0, 1.0, math.log(2))
    close(peak_time(2.0, 1.0), o["SK-C01"]["peak_time"], m="SK-C01 peak")
    close(s.f, o["SK-C01"]["fuel_at_peak"], m="SK-C01 fuel")
    close(s.E, o["SK-C01"]["stored_energy_at_peak"], m="SK-C01 stored")
    close(s.Q, o["SK-C01"]["emitted_energy_at_peak"], m="SK-C01 emitted")
    (L1, t1), (L2, t2) = o["SK-C02"]["L_tau_pairs"]
    close(single_band_flux(L1, t1), single_band_flux(L2, t2), m="SK-C02 degeneracy")
    base = wind_transformed_radius(F(1), F(1), F(1))
    require(wind_transformed_radius(F(o["SK-C03"]["radius_factor"]), F(1), F(o["SK-C03"]["mass_loss_factor"])) / base
            == F(o["SK-C03"]["transformed_radius_factor"]) ** 3, "SK-C03 (cube form)")
    require(two_band_identifiability([1, 2]).rank == o["SK-C04"]["rank_distinct_coefficients"]
            and two_band_identifiability([1, 1]).rank == o["SK-C04"]["rank_equal_coefficients"], "SK-C04")
    return {"TP-C01..C04, SK-C01..C04": "match"}


def check_coverage_accounting(o):
    covered = {f"MU-C{i:02d}" for i in (1, 2, 3, 4, 5, 6, 8, 9, 10, 12, 13, 14, 16)} | {f"TP-C0{i}" for i in range(1, 5)} | {f"SK-C0{i}" for i in range(1, 5)}
    not_applicable = {f"SA-C0{i}" for i in range(1, 5)}
    rest = set(o) - covered - not_applicable
    require(rest == {"MU-C07", "MU-C11", "MU-C15", "MU-C17"}, f"unexpected uncovered set {sorted(rest)}")
    return {"production_crosschecked": len(covered), "not_applicable_SA_documentation_only": sorted(not_applicable),
            "oracle_only_no_direct_production_api": sorted(rest)}


CHECKS = [check_mu_kinematics, check_mu_inference, check_candidates, check_coverage_accounting]


def main():
    results, n_passed = {}, 0
    try:
        o = oracle()
    except Exception as e:
        print(f"ERROR loading oracle: {e}")
        return 1
    for check in CHECKS:
        name = check.__name__.removeprefix("check_")
        try:
            results[name] = check(o)
            print(f"PASS  {name}")
            n_passed += 1
        except AssertionError as e:
            results[name] = {"error": str(e)}
            print(f"FAIL  {name}: {e}")
        except Exception as e:
            results[name] = {"error": f"{type(e).__name__}: {e}"}
            print(f"ERROR {name}: {type(e).__name__}: {e}")
    print(f"\n{n_passed}/{len(CHECKS)} checks passed")
    Path(__file__).with_name("verify_mu_candidate_oracle_crosscheck_results.json").write_text(
        json.dumps({"n_passed": n_passed, "n_total": len(CHECKS), "results": results}, indent=2, default=str), encoding="utf-8")
    return 0 if n_passed == len(CHECKS) else 1


if __name__ == "__main__":
    raise SystemExit(main())
