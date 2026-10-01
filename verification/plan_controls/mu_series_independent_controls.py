"""Independent re-derivation of the Muonium control groups MU-C01..MU-C17.

Part of package MU0 (MUONIUM_GRAVITY_ROADMAP.md). Plan:
prompts/Answers/nicht_stationäre_Treiber/SCF_MUONIUM_GRAVITY_IMPLEMENTATION_PLAN.md

Plan-arithmetic layer only (no SCF import, standard library only): exact
Fractions where the statement is algebraic, floats with stated tolerances
for the illustrative SI table. The plan refers to a companion script
``independent_controls.py`` ("29/29"); that script was NOT among the
received files, so nothing here is compared against it -- every value is
derived from the plan text and checked here.

Not a repository regression test (not named verify_*.py).

Usage:
    python verification/plan_controls/mu_series_independent_controls.py [--output FILE]

License: GPL-3.0-or-later.
"""
from __future__ import annotations

import argparse
import cmath
import json
import math
from fractions import Fraction as F
from pathlib import Path

RESULTS: dict[str, dict] = {}


def record(cid, **kw):
    RESULTS[cid] = {k: (str(v) if isinstance(v, F) else v) for k, v in kw.items()}


# illustrative design inputs of plan section 5.2 (NOT measured values)
G, TAU, D, V = 9.81, 2.2e-6, 100e-9, 2180.0
T = 2 * TAU


def mu_c01():
    delta = F(1, 10)
    eta = 2 * delta / (2 + delta)
    assert eta == F(2, 21)
    # eta undefined when a_mu + g_ref = 0  <=>  delta = -2
    assert 2 + F(-2) == 0
    record("MU-C01", delta=delta, eta=eta, eta_undefined_at_delta=-2)


def mu_c02():
    z0, u0, a, t = F(3, 7), F(-5, 3), F(11, 4), F(2, 9)
    z = lambda s: z0 + u0 * s + a * s * s / 2
    second = z(2 * t) - 2 * z(t) + z(0)
    assert second == a * t * t
    assert z(t) - z0 - u0 * t == a * t * t / 2  # single-path drop is a T^2 / 2
    record("MU-C02", second_difference=second, aT2=a * t * t, single_path_drop=a * t * t / 2)


def mu_c03():
    L = V * T
    drop_tau = G * TAU ** 2 / 2
    rel = G * T ** 2
    phase = 2 * math.pi * rel / D
    surv = math.exp(-2 * T / TAU)
    dphi_1pct = 0.01 * phase
    shift_1pct = 0.01 * rel
    expect = {"L": 9.592e-3, "drop_tau": 23.7402e-12, "rel": 189.9216e-12, "phase": 0.0119331260663604,
              "surv": 0.0183156388887342, "dphi": 119.3312607e-6, "shift": 1.899216e-12}
    got = {"L": L, "drop_tau": drop_tau, "rel": rel, "phase": phase, "surv": surv, "dphi": dphi_1pct, "shift": shift_1pct}
    for k in expect:
        assert math.isclose(got[k], expect[k], rel_tol=1e-9), (k, got[k], expect[k])
    # K(v) = 2 pi L^2 / (d v^2) = 2 pi T^2 / d for L = v T
    assert math.isclose(2 * math.pi * L ** 2 / (D * V ** 2), 2 * math.pi * T ** 2 / D, rel_tol=1e-12)
    record("MU-C03", **{k: got[k] for k in got})


def mu_c04():
    assert math.isclose(math.exp(-4), 0.0183156388887342, rel_tol=1e-14)
    # sigma(T) ~ exp(T/tau)/T^2 ; d log sigma / dT = 1/tau - 2/T = 0 at T = 2 tau
    tau = F(11, 5)  # any positive value; exact derivative check
    deriv = lambda t: 1 / tau - 2 / t
    assert deriv(2 * tau) == 0 and deriv(tau) < 0 and deriv(3 * tau) > 0
    s = lambda t: math.exp(t / 2.2) / t ** 2
    assert s(4.4) < s(4.3) and s(4.4) < s(4.5)
    record("MU-C04", survival_2T_at_T_2tau="exp(-4)", T_opt="2 tau", condition="fixed incoming budget, time-independent contrast")


def mu_c05():
    # unit change: phase K a is dimensionless and invariant (m -> mm, s -> us)
    phase_si = 2 * math.pi * G * T ** 2 / D
    g_mm_us2 = G * 1e3 / 1e12  # mm / us^2
    phase_other = 2 * math.pi * g_mm_us2 * (T * 1e6) ** 2 / (D * 1e3)
    assert math.isclose(phase_si, phase_other, rel_tol=1e-12)
    e = F(1, 100)
    ratio = (1 + e) ** 2
    assert ratio == F(10201, 10000)  # +2.01 %
    record("MU-C05", a_fit_over_a_true=ratio, percent_error="2.01")


def mu_c06():
    vs, w = (F(1), F(2)), (F(1, 2), F(1, 2))
    e_inv2 = sum(wi / vi ** 2 for wi, vi in zip(w, vs))
    e_v = sum(wi * vi for wi, vi in zip(w, vs))
    assert e_inv2 == F(5, 8) and 1 / e_v ** 2 == F(4, 9) and e_inv2 != 1 / e_v ** 2
    F_contrast = (cmath.exp(0j) + cmath.exp(1j * math.pi)) / 2
    assert abs(F_contrast) < 1e-15  # phases 0 and pi cancel
    assert math.isclose((0 + math.pi) / 2, math.pi / 2)  # the arithmetic phase mean pi/2 pretends information
    record("MU-C06", E_inv_v2=e_inv2, inv_E_v_sq=F(4, 9), counterphase_contrast=0)


def mu_c07():
    surv = (F(1, 4), F(1, 2))
    incoming = (F(1, 2), F(1, 2))
    det = [s * i for s, i in zip(surv, incoming)]
    tot = sum(det)
    weights = [d / tot for d in det]
    assert weights == [F(1, 3), F(2, 3)]
    record("MU-C07", detected_weights=[str(x) for x in weights])


def mu_c08():
    def nll(n, lam):
        if lam < 0 or n < 0:
            raise ValueError
        if lam == 0:
            return 0.0 if n == 0 else math.inf
        return lam - n * math.log(lam) + math.lgamma(n + 1)

    assert nll(0, 0) == 0.0 and nll(3, 0) == math.inf
    for n, lam in ((0, 2.5), (4, 2.5), (7, 9.0)):
        dev = 2 * (lam - n + (n * math.log(n / lam) if n > 0 else 0.0))
        sat = nll(n, n) if n > 0 else 0.0
        assert math.isclose(dev, 2 * (nll(n, lam) - sat), rel_tol=1e-12, abs_tol=1e-12)
    assert math.isclose(2 * (2.5 - 0), 5.0)  # zero-count deviance term 2 lambda
    record("MU-C08", nll_0_0=0, nll_pos_0="inf", deviance_equals_twice_nll_minus_saturated=True)


def rank(rows):
    m = [[F(x) for x in r] for r in rows]
    r = 0
    for c in range(len(m[0])):
        piv = next((i for i in range(r, len(m)) if m[i][c] != 0), None)
        if piv is None:
            continue
        m[r], m[piv] = m[piv], m[r]
        for i in range(len(m)):
            if i != r and m[i][c] != 0:
                f = m[i][c] / m[r][c]
                m[i] = [a - f * b for a, b in zip(m[i], m[r])]
        r += 1
    return r


def mu_c09():
    assert rank([[1, 1]]) == 1  # one flight time, (A, b)
    assert rank([[1, 1], [4, 1]]) == 2  # u = (1, 4)
    # p = (3, 6): A + b = 3, 4A + b = 6
    A = F(6 - 3, 4 - 1)
    b = 3 - A
    assert (A, b) == (1, 2)
    record("MU-C09", rank_one_time=1, rank_two_times=2, A=A, b=b)


def mu_c10():
    rows = [[u, u, 1] for u in (1, 4, 9, 16)]  # p = u (A + B) + b
    assert rank(rows) == 2
    record("MU-C10", rank_three_params_many_times=2)


def mu_c11():
    assert rank([[1, 1], [-1, 1]]) == 2  # p_s = s A + b separates A and b
    assert rank([[1, 1, 1], [-1, -1, 1]]) == 2  # with odd bias s B: A and B stay inseparable (3 params)
    A, B, b = F(2), F(1, 3), F(5)
    p = {s: s * (A + B) + b for s in (1, -1)}
    assert p[1] - p[-1] == 2 * (A + B)  # even offset cancels, odd bias stays
    record("MU-C11", even_offset_cancels=True, odd_bias_remains=True)


def mu_c12():
    N, C = 400, F(1, 5)
    # four equal phase steps alpha in {0, pi/2, pi, 3pi/2} at phi = 0, known normalisation:
    # I_phi = sum (N/4)^2 C^2 sin^2(alpha) / ((N/4)(1 + C cos alpha)); sin^2 = 0,1,0,1 where cos = 1,0,-1,0
    I_scan = sum(F(N, 4) * C ** 2 * s2 / (1 + C * c) for s2, c in ((0, 1), (1, 0), (0, -1), (1, 0)))
    assert I_scan == N * C ** 2 / 2 == 8
    I_quad = N * C ** 2  # all N at quadrature
    assert I_quad == 16
    record("MU-C12", I_phi_four_step=I_scan, I_phi_quadrature=I_quad)


def mu_c13():
    C = 0.35
    K = 2 * math.pi * T ** 2 / D
    N = 1.0 / (C * K * 0.01 * G) ** 2
    assert math.isclose(N, 5.73265035e8, rel_tol=1e-8), N
    assert math.isclose(0.01 * G * T ** 2, 1.899216e-12, rel_tol=1e-9)
    record("MU-C13", events_for_1pct=N, equivalent_grating_shift_m=0.01 * G * T ** 2)


def mu_c14():
    # K = 2 pi T^2 / d; a -> a + d/T^2 shifts the phase by exactly 2 pi
    Tq, dq = F(22, 5), F(1, 10)  # symbolic-scale exact check (units irrelevant)
    K_over_2pi = Tq ** 2 / dq
    assert K_over_2pi * (dq / Tq ** 2) == 1
    record("MU-C14", alias_step="d/T^2", phase_shift="2 pi")


def mu_c15():
    C, lam0 = 0.3, 1000.0
    counts = lambda phi: lam0 * (1 + C * math.cos(math.pi / 2 + phi))  # quadrature: 1 - C sin(phi)
    assert counts(0.1) < counts(0.0) < counts(-0.1)  # sign: counts decrease with phi
    phi = 0.4
    inv = math.asin((1 - counts(phi) / lam0) / C)
    assert math.isclose(inv, phi, rel_tol=1e-12)
    assert math.isclose(counts(math.pi - phi), counts(phi), rel_tol=1e-12)  # global ambiguity
    record("MU-C15", local_arcsin_inverse=True, global_alias="pi - phi")


def mu_c16():
    C = 0.0
    lam = lambda a: 100 * (1 + C * math.cos(1.7 * a))
    assert lam(0.0) == lam(3.0)
    record("MU-C16", fisher_information=0, reason="no contrast")


def mu_c17():
    K1 = F(3)
    K2 = 4 * K1
    da = F(1) / K1  # in units of 2 pi: phase1 shifts by 1 turn
    assert K1 * da == 1 and K2 * da == 4  # both shift by integer turns -> common alias
    record("MU-C17", common_alias_turns=[1, 4])


CASES = [mu_c01, mu_c02, mu_c03, mu_c04, mu_c05, mu_c06, mu_c07, mu_c08, mu_c09,
         mu_c10, mu_c11, mu_c12, mu_c13, mu_c14, mu_c15, mu_c16, mu_c17]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, default=None)
    args = ap.parse_args()
    failed = []
    for c in CASES:
        try:
            c()
        except AssertionError as e:
            failed.append((c.__name__, repr(e)))
    summary = {"passed": len(CASES) - len(failed), "total": len(CASES), "failed": failed, "results": RESULTS,
               "imports_scf": False, "companion_oracle_available": False}
    if args.output:
        args.output.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{summary['passed']}/{len(CASES)} MU control groups independently re-derived")
    for f in failed:
        print("FAIL", *f)
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
