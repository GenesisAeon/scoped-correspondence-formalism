"""SK1-SK3 verification (CANDIDATE_PILOTS_ROADMAP.md): stellar pulse vs
observation operator. Controls derived independently here (the assessment's
companion script was not received).

SK-C01: release model -- conservation, positivity, alpha = beta limit,
        peak at t = ln 2 for alpha = 2, beta = 1 with f = 1/4, E = 1/2, Q = 1/4.
SK-C02: single band F = L exp(-tau): (1, 0) and (e, 1) give the same flux.
SK-C04: two known, different extinction coefficients: rank 2 (exact, J6);
        an unknown per-band shape term removes that again; k1 = k2 gives rank 1.
SK-C03: R* -> 4 R*, Mdot -> 8 Mdot keeps R* (v/Mdot)^(2/3); L scales by 16.
"""
from __future__ import annotations

import json
import math
import sys
from fractions import Fraction as F
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from scoped_correspondence.errors import ScopeViolationError
from scoped_correspondence.validation.stellar_pulse_observation import (
    peak_time,
    release_state,
    single_band_flux,
    two_band_identifiability,
    wind_transformed_radius,
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


def check_sk_c01_release_pulse():
    t = peak_time(2.0, 1.0)
    require(math.isclose(t, math.log(2), rel_tol=1e-15), "peak at t = ln 2")
    s = release_state(2.0, 1.0, t)
    require(math.isclose(s.f, 0.25) and math.isclose(s.E, 0.5) and math.isclose(s.Q, 0.25, abs_tol=1e-15), f"(1/4, 1/2, 1/4), got {s}")
    worst = 0.0
    for a, b in ((2.0, 1.0), (0.3, 5.0), (1.0, 1.0), (1.0, 1.0 + 1e-9)):
        for tt in (0.0, 0.1, 1.0, 3.0, 20.0):
            st = release_state(a, b, tt)
            require(min(st.f, st.E, st.Q) >= -1e-12, "positivity")
            worst = max(worst, abs(st.f + st.E + st.Q - 1))
    require(worst < 1e-12, "conservation f + E + Q = 1")
    # alpha = beta = 1 alone cannot detect a missing factor alpha (found by the mutation run); use alpha = 2 too
    for a in (1.0, 2.0):
        lim, near = release_state(a, a, 2.0), release_state(a, a + 1e-7, 2.0)
        require(math.isclose(lim.E, near.E, rel_tol=1e-6), f"alpha = beta = {a} is the continuous limit")
    require(release_state(2.0, 1.0, 0.0).E == 0 and release_state(2.0, 1.0, 40.0).E < 1e-12, "rise and recovery: a pulse in a linear system")
    return {"t_peak": t, "state_at_peak": [s.f, s.E, s.Q]}


def check_sk_c02_single_band_degeneracy():
    require(math.isclose(single_band_flux(1.0, 0.0), single_band_flux(math.e, 1.0), rel_tol=1e-15), "(1,0) ~ (e,1)")
    r = two_band_identifiability([F(1)])
    require(r.rank == 1 and not r.globally_identifiable_on_Rp, "one band: (log L, tau) not separable")
    return {"rank_single_band": r.rank}


def check_sk_c04_two_known_extinctions():
    r = two_band_identifiability([F(1), F(5, 2)])
    require(r.rank == 2 and r.globally_identifiable_on_Rp, "two known, different k: rank 2")
    same = two_band_identifiability([F(1), F(1)])
    require(same.rank == 1, "identical k: rank 1")
    unknown = two_band_identifiability([F(1), F(5, 2)], unknown_shape_terms=True)
    require(not unknown.globally_identifiable_on_Rp, "unknown per-band shape terms: not identifiable again")
    return {"known_k_rank": r.rank, "unknown_shape_rank": unknown.rank, "n_params_unknown_shape": unknown.n_parameters}


def check_sk_c03_wind_scaling():
    base = wind_transformed_radius(F(1), F(1000), F(1))
    scaled = wind_transformed_radius(F(4), F(1000), F(8))
    require(base == scaled, "R*(v/Mdot)^(2/3) invariant under (4 R*, 8 Mdot) -- exact via the cube")
    require(F(4) ** 2 == 16, "L ~ R*^2 at fixed T scales by 16")
    require(raises(lambda: wind_transformed_radius(1.0, F(1), F(1))), "exact inputs required")
    return {"invariant": True, "luminosity_factor": 16, "note": "algebraic invariance only; spectral identity not claimed"}


CHECKS = [check_sk_c01_release_pulse, check_sk_c02_single_band_degeneracy, check_sk_c04_two_known_extinctions, check_sk_c03_wind_scaling]


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
    Path(__file__).with_name("verify_stellar_pulse_observation_results.json").write_text(
        json.dumps({"n_passed": n_passed, "n_total": len(CHECKS), "results": results}, indent=2, default=str), encoding="utf-8")
    return 0 if n_passed == len(CHECKS) else 1


if __name__ == "__main__":
    raise SystemExit(main())
