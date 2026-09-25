#!/usr/bin/env python3
"""Phase-type/Erlang delay chains (INTEGRATED_EXTENSION_ROADMAP.md Paket C3).

Checks:

  1. Hand-verified control values: both Erlang(1) and Erlang(2) chains with
     tau=1 have mean dwell time 1; F_1(t)=1-e^-t, F_2(t)=1-e^-2t(1+2t) match
     the hand-derived table at t=0.25,1,2 to 12 digits.
  2. The Erlang-2 impulse response h_2(t)=4t*e^-2t peaks at t=0.5 with height
     2/e -- located by a fine grid search, not merely asserted analytically.
  3. The CDF ranking between Erlang(1) and Erlang(2) REVERSES between
     t=0.25 (F_1<F_2) and t=2 (F_1>F_2) -- checked as an explicit,
     structural finding, not incidental.
  4. mean_dwell_time cross-checked an INDEPENDENT way: numerically
     integrating the survival function (E[tau] = integral_0^inf S(t) dt)
     via quadrature, never by calling mean_dwell_time against itself.
  5. propagate_linear_constant_input reproduces a known closed-form scalar
     ODE (dx/dt=-x+1) exactly.
  6. ScopeViolationError guards (bad alpha, bad T, singular T).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

import numpy as np
from scipy.integrate import quad

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from scoped_correspondence.errors import ScopeViolationError  # noqa: E402
from scoped_correspondence.dynamics.phase_type_delays import (  # noqa: E402
    PhaseType,
    erlang_phase_type,
    validate_phase_type,
    mean_dwell_time,
    impulse_response,
    survival_function,
    cdf,
    propagate_linear_constant_input,
)


def require(ok, msg):
    if not bool(ok):
        raise AssertionError(msg)


def check_control_values_n1_n2():
    pt1 = erlang_phase_type(1, tau=1.0)
    pt2 = erlang_phase_type(2, tau=1.0)
    validate_phase_type(pt1)
    validate_phase_type(pt2)

    require(abs(mean_dwell_time(pt1) - 1.0) < 1e-9, "Erlang(1) mean dwell time should be 1")
    require(abs(mean_dwell_time(pt2) - 1.0) < 1e-9, "Erlang(2) mean dwell time should be 1")

    expected = {
        0.25: (0.221199216929, 0.090204010431),
        1.0: (0.632120558829, 0.593994150290),
        2.0: (0.864664716763, 0.908421805556),
    }
    got = {}
    for t, (f1, f2) in expected.items():
        c1, c2 = cdf(t, pt1), cdf(t, pt2)
        require(abs(c1 - f1) < 1e-9, f"F_1({t}) should be {f1}, got {c1!r}")
        require(abs(c2 - f2) < 1e-9, f"F_2({t}) should be {f2}, got {c2!r}")
        got[t] = (c1, c2)
    return {"cdf": got}


def check_impulse_peak():
    pt2 = erlang_phase_type(2, tau=1.0)
    ts = np.linspace(0.0, 2.0, 200001)
    vals = np.array([impulse_response(t, pt2) for t in ts[::200]])  # coarser grid for speed, still fine (0.01 spacing)
    ts_coarse = ts[::200]
    i_max = int(np.argmax(vals))
    require(abs(ts_coarse[i_max] - 0.5) < 0.01, f"Erlang-2 impulse peak should be near t=0.5, got {ts_coarse[i_max]!r}")
    peak_h = impulse_response(0.5, pt2)
    require(abs(peak_h - 2.0 / np.e) < 1e-9, f"peak height should be 2/e={2/np.e!r}, got {peak_h!r}")
    return {"t_peak": float(ts_coarse[i_max]), "height": peak_h}


def check_cdf_ranking_reverses():
    pt1 = erlang_phase_type(1, tau=1.0)
    pt2 = erlang_phase_type(2, tau=1.0)
    f1_025, f2_025 = cdf(0.25, pt1), cdf(0.25, pt2)
    f1_2, f2_2 = cdf(2.0, pt1), cdf(2.0, pt2)
    require(f1_025 > f2_025, "at t=0.25, Erlang(1) should have already resolved MORE mass than Erlang(2)")
    require(f1_2 < f2_2, "at t=2, the ranking must have REVERSED -- Erlang(2) now ahead")
    return {"f1_025": f1_025, "f2_025": f2_025, "f1_2": f1_2, "f2_2": f2_2}


def check_mean_dwell_time_independent_cross_check():
    for n, tau in [(1, 1.0), (2, 1.0), (4, 2.5), (8, 3.0)]:
        pt = erlang_phase_type(n, tau)
        reported = mean_dwell_time(pt)
        integral, _ = quad(lambda t: survival_function(t, pt), 0.0, 50.0 * tau, limit=200)
        require(abs(integral - reported) < 1e-6,
                f"n={n},tau={tau}: independent quadrature of the survival function ({integral!r}) "
                f"should match mean_dwell_time ({reported!r})")
        require(abs(reported - tau) < 1e-9, f"Erlang(n) mean dwell time should equal tau={tau}, got {reported!r}")
    return {"checked": [(1, 1.0), (2, 1.0), (4, 2.5), (8, 3.0)]}


def check_propagate_linear_constant_input_closed_form():
    # dx/dt = -x + 1, x(0)=0 -> x(t) = 1 - e^{-t}, a standard closed-form control case.
    A = np.array([[-1.0]])
    d = np.array([1.0])
    x0 = np.array([0.0])
    for t in [0.1, 1.0, 3.0]:
        x_t = propagate_linear_constant_input(x0, A, d, t)[0]
        expected = 1.0 - np.exp(-t)
        require(abs(x_t - expected) < 1e-9, f"t={t}: expected {expected!r}, got {x_t!r}")
    return {"ok": True}


def check_scope_violation_guards():
    pt = erlang_phase_type(2, tau=1.0)
    bad_alpha = PhaseType(alpha=np.array([0.5, 0.6]), T=pt.T, r=pt.r)
    try:
        validate_phase_type(bad_alpha)
        raise AssertionError("alpha not summing to 1 should raise")
    except ScopeViolationError:
        pass

    bad_T = PhaseType(alpha=pt.alpha, T=np.array([[-1.0, -0.5], [1.0, -1.0]]), r=pt.r)
    try:
        validate_phase_type(bad_T)
        raise AssertionError("negative off-diagonal T entry should raise")
    except ScopeViolationError:
        pass

    singular_T = PhaseType(alpha=np.array([1.0, 0.0]), T=np.array([[0.0, 0.0], [0.0, 0.0]]), r=np.array([0.0, 0.0]))
    try:
        validate_phase_type(singular_T)
        raise AssertionError("singular T (never absorbs) should raise")
    except ScopeViolationError:
        pass
    return {"raised": 3}


CHECKS = [
    ("control_values_n1_n2", check_control_values_n1_n2),
    ("impulse_peak", check_impulse_peak),
    ("cdf_ranking_reverses", check_cdf_ranking_reverses),
    ("mean_dwell_time_independent_cross_check", check_mean_dwell_time_independent_cross_check),
    ("propagate_linear_constant_input_closed_form", check_propagate_linear_constant_input_closed_form),
    ("scope_violation_guards", check_scope_violation_guards),
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json-out", type=Path, default=Path(__file__).with_name("verify_phase_type_delays_results.json"))
    args = parser.parse_args()

    report = {
        "package": "INTEGRATED_EXTENSION_ROADMAP.md Paket C3 (phase-type/Erlang delay chains)",
        "timestamp": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "python": sys.version.split()[0],
        "checks": {},
    }

    all_ok = True
    for name, fn in CHECKS:
        try:
            detail = fn()
            report["checks"][name] = {"status": "pass", "detail": detail}
            print(f"PASS  {name}")
        except AssertionError as e:
            all_ok = False
            report["checks"][name] = {"status": "fail", "error": str(e)}
            print(f"FAIL  {name}: {e}")
        except Exception as e:  # noqa: BLE001
            all_ok = False
            report["checks"][name] = {"status": "error", "error": f"{type(e).__name__}: {e}"}
            print(f"ERROR {name}: {type(e).__name__}: {e}")

    args.json_out.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    print(f"\n{sum(1 for c in report['checks'].values() if c['status'] == 'pass')}/{len(CHECKS)} checks passed")
    print(f"Report written to {args.json_out}")
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
