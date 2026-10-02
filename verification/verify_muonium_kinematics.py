"""MU1 verification (MUONIUM_GRAVITY_ROADMAP.md, plan section 10/MU1):
idealised three-plane kinematics, units and scope.

Kontrollen MU-C01..MU-C05, MU-C14 plus: unequal flight times rejected,
eta denominator zero reported as undefined, invalid geometry, non-finite
inputs; negative accelerations stay inside the scope. The J2 dimension
checker confirms that the phase is dimensionless.

Expected values from verification/plan_controls/mu_series_independent_controls.py
(illustrative design inputs, NOT measured values).
"""
from __future__ import annotations

import json
import math
import sys
from fractions import Fraction as F
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from scoped_correspondence.errors import ScopeViolationError
from scoped_correspondence.muonium.kinematics import (
    Geometry,
    check_flight_times,
    delta_g,
    eta,
    grating_offset_phase,
    gravity_phase,
    phase_is_dimensionless,
    relative_displacement,
    second_difference,
    single_path_drop,
    survival,
)

G, TAU, D, V = 9.81, 2.2e-6, 100e-9, 2180.0
T = 2 * TAU
GEOM = Geometry(L=V * T, d=D, v=V)


def require(c, m=""):
    if not c:
        raise AssertionError(m)


def raises(fn, exc=ScopeViolationError):
    try:
        fn()
    except exc:
        return True
    return False


def check_mu_c01_delta_eta():
    a = F(1089, 100)  # delta = 1/10 for g_ref = 99/10
    d = delta_g(a, F(99, 10))
    require(d == F(1, 10) and eta(a, F(99, 10)) == F(2, 21), "delta 1/10 -> eta 2/21")
    require(eta(F(-99, 10), F(99, 10)) is None, "a_mu = -g_ref: eta undefined (None), not an invented number")
    require(delta_g(F(-5), F(10)) == F(-3, 2), "negative a_mu allowed: no positivity assumption")
    require(raises(lambda: delta_g(1, 0)) and raises(lambda: delta_g(1, -2)), "g_ref must be > 0")
    return {"delta": "1/10", "eta": "2/21"}


def check_mu_c02_second_difference_exact():
    for z0, u0, a, t in ((F(3, 7), F(-5, 3), F(11, 4), F(2, 9)), (0, 0, F(-981, 100), F(1, 3))):
        require(second_difference(z0, u0, a, t) == a * t * t == relative_displacement(a, t), "z(2T)-2z(T)+z(0) = aT^2")
        require(single_path_drop(a, t) * 2 == relative_displacement(a, t), "single path drop is half the relative displacement")
    return {"identity": "aT^2"}


def check_mu_c03_reference_table():
    vals = {
        "L": float(GEOM.L), "drop_tau": single_path_drop(G, TAU), "rel": relative_displacement(G, T),
        "phase": gravity_phase(G, GEOM), "survival": survival(GEOM, TAU),
        "dphi_1pct": gravity_phase(0.01 * G, GEOM), "shift_1pct": relative_displacement(0.01 * G, T),
    }
    expect = {"L": 9.592e-3, "drop_tau": 23.7402e-12, "rel": 189.9216e-12, "phase": 0.0119331260663604,
              "survival": 0.0183156388887342, "dphi_1pct": 119.3312607e-6, "shift_1pct": 1.899216e-12}
    for k, e in expect.items():
        require(math.isclose(vals[k], e, rel_tol=1e-9), f"{k}: {vals[k]} vs {e}")
    # a grating shift h has the same phase as relative displacement: -2 pi h / d
    require(math.isclose(abs(grating_offset_phase(vals["shift_1pct"], D)), vals["dphi_1pct"], rel_tol=1e-12),
            "1 % of g equals a relative grating shift of 1.899216 pm in phase")
    return vals


def check_mu_c04_survival_and_optimum():
    require(math.isclose(survival(GEOM, TAU), math.exp(-4), rel_tol=1e-14), "T = 2 tau -> exp(-4)")
    sig = lambda t: math.exp(t / TAU) / t ** 2  # sigma_a(T) up to a constant, fixed incoming budget
    require(sig(2 * TAU) < sig(1.9 * TAU) and sig(2 * TAU) < sig(2.1 * TAU), "conditional optimum T = 2 tau")
    rel = survival(GEOM, TAU, lorentz_gamma=1.0000000001)
    require(rel > survival(GEOM, TAU), "time dilation lengthens the effective lifetime")
    require(raises(lambda: survival(GEOM, TAU, lorentz_gamma=0.5)), "gamma < 1 rejected")
    return {"survival": survival(GEOM, TAU)}


def check_mu_c05_units_and_velocity_calibration():
    g_si = Geometry(L=V * T, d=D, v=V)
    g_mm = Geometry(L=V * T * 1e3, d=D * 1e3, v=V * 1e3 / 1e6)  # mm and microseconds
    require(math.isclose(gravity_phase(G, g_si), gravity_phase(G * 1e3 / 1e12, g_mm), rel_tol=1e-12), "phase invariant under m->mm, s->us")
    require(phase_is_dimensionless(), "J2 check: K a is dimensionless")
    e = F(1, 100)
    true = Geometry(L=F(9592, 1000000), d=F(1, 10000000), v=F(2180))
    assumed = Geometry(L=true.L, d=true.d, v=true.v * (1 + e))
    a_true = F(981, 100)
    a_fit = a_true * true.K() / assumed.K()
    require(math.isclose(a_fit / float(a_true), float((1 + e) ** 2), rel_tol=1e-12), "a_fit/a_true = (1+e)^2 = 1.0201")
    return {"a_fit_over_a_true": a_fit / float(a_true)}


def check_mu_c14_periodic_alias():
    a1 = 3.7
    alias = a1 + D / T ** 2
    require(math.isclose(gravity_phase(alias, GEOM) - gravity_phase(a1, GEOM), 2 * math.pi, rel_tol=1e-12),
            "a -> a + d/T^2 shifts the phase by exactly 2 pi")
    return {"alias_step_m_per_s2": D / T ** 2}


def check_scope_rejections():
    require(raises(lambda: check_flight_times(T, 1.1 * T)), "unequal flight times are rejected")
    check_flight_times(T, T)
    require(raises(lambda: Geometry(L=0, d=D, v=V)) and raises(lambda: Geometry(L=1, d=-D, v=V)) and raises(lambda: Geometry(L=1, d=D, v=0)),
            "invalid geometry rejected")
    require(raises(lambda: Geometry(L=float("nan"), d=D, v=V)) and raises(lambda: relative_displacement(float("inf"), T)),
            "non-finite inputs rejected")
    require(gravity_phase(-G, GEOM) < 0 and relative_displacement(-G, T) < 0, "negative a stays inside the defined scope")
    require(raises(lambda: gravity_phase("9.81", GEOM)), "strings are not numbers here")
    return {"rejections": "ok"}


CHECKS = [
    check_mu_c01_delta_eta,
    check_mu_c02_second_difference_exact,
    check_mu_c03_reference_table,
    check_mu_c04_survival_and_optimum,
    check_mu_c05_units_and_velocity_calibration,
    check_mu_c14_periodic_alias,
    check_scope_rejections,
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
    out_path = Path(__file__).with_name("verify_muonium_kinematics_results.json")
    out_path.write_text(json.dumps({"n_passed": n_passed, "n_total": len(CHECKS), "results": results}, indent=2, default=str))
    print(f"Report written to {out_path}")
    return 0 if n_passed == len(CHECKS) else 1


if __name__ == "__main__":
    raise SystemExit(main())
