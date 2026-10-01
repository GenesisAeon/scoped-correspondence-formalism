"""MU2 verification (MUONIUM_GRAVITY_ROADMAP.md, plan section 10/MU2):
finite velocity mixture and measurement operator.

Kontrollen MU-C06 (E[1/v^2] != 1/E[v]^2; counter-phase contrast 0),
MU-C07 (survival 1/4, 1/2 -> detected weights 1/3, 2/3), MU-C16 (no
contrast -> no acceleration information); null signal, F = 0 (no arg(0)),
C = 0 and C = 1, the sum of per-bin measurement times, invalid weights; the
exact single-velocity limit; the phase at the mean velocity does not
replace the mixture sum.
"""
from __future__ import annotations

import cmath
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from scoped_correspondence.errors import ScopeViolationError
from scoped_correspondence.muonium.forward import ForwardModel, ScanBin, VelocityClass as _VC, equal_time_bins, total_measurement_time


def VelocityClass(v, w, transmission=0.5, contrast=1.0, **kw):
    """Test helper: explicit A = 1/2 by default so that A (1 + C) <= 1 holds for C <= 1."""
    return _VC(v, w, transmission=transmission, contrast=contrast, **kw)

L, D, TAU = 9.592e-3, 100e-9, 2.2e-6


def require(c, m=""):
    if not c:
        raise AssertionError(m)


def raises(fn, exc=ScopeViolationError):
    try:
        fn()
    except exc:
        return True
    return False


def model(classes, **kw):
    return ForwardModel(L=L, d=D, tau=TAU, classes=tuple(classes), rate=1000.0, background=kw.pop("b", 2.0), **kw)


def check_single_velocity_limit():
    m = model([VelocityClass(2180.0, 1.0, contrast=0.35)])
    a = 9.81
    W, F = m.complex_contrast(a)
    phi = m.K(2180.0) * a
    require(abs(F - 0.35 * cmath.exp(1j * phi)) < 1e-15, "single class: F = C exp(i K a)")
    require(math.isclose(W, 0.5 * math.exp(-2 * L / (2180.0 * TAU)), rel_tol=1e-14), "W = A * survival (A = 1/2, eps = 1)")
    return {"phase": phi}


def check_mu_c06_mixture_is_not_mean_velocity():
    v1, v2 = 2180.0, 4360.0
    # E[1/v^2] vs 1/E[v]^2 with equal weights and the ratio 1:2 of MU-C06
    e_inv2 = 0.5 / v1 ** 2 + 0.5 / v2 ** 2
    inv_e = 1 / (0.75 * v2) ** 2
    require(math.isclose(e_inv2 * v1 ** 2, 5 / 8) and math.isclose(inv_e * v1 ** 2, 4 / 9), "5/8 vs 4/9 (scaled)")
    m = model([VelocityClass(v1, 0.5), VelocityClass(v2, 0.5)], b=0.0)
    a = 300.0
    phase_mix = m.modulation_phase(a)
    phase_mean_v = m.K(0.75 * v2) * a
    require(phase_mix is not None and abs(cmath.phase(cmath.exp(1j * (phase_mix - phase_mean_v)))) > 1e-3,
            "the phase at the mean velocity does not reproduce the mixture phase")
    # counter-phase classes: same v, phases 0 and pi via phi_sys -> |F| = 0 when weights balance after survival
    cp = model([VelocityClass(v1, 0.5), VelocityClass(v1, 0.5, phi_sys=math.pi)])
    W, F = cp.complex_contrast(0.0)
    require(abs(F) < 1e-15 and cp.modulation_phase(0.0) is None, "counter-phase contrast 0; phase undefined, not pi/2")
    return {"phase_mixture": phase_mix, "phase_at_mean_v": phase_mean_v}


def check_mu_c07_detected_mixture():
    v1 = 2 * L / (TAU * math.log(4))  # survival 1/4
    v2 = 2 * L / (TAU * math.log(2))  # survival 1/2
    m = model([VelocityClass(v1, 0.5), VelocityClass(v2, 0.5)])
    require(math.isclose(m.survival(v1), 0.25, rel_tol=1e-12) and math.isclose(m.survival(v2), 0.5, rel_tol=1e-12), "survival 1/4, 1/2")
    w = m.detected_weights()
    require(math.isclose(w[0], 1 / 3, rel_tol=1e-12) and math.isclose(w[1], 2 / 3, rel_tol=1e-12), f"detected 1/3, 2/3, got {w}")
    return {"detected": w}


def check_mu_c16_no_contrast_no_information():
    m = model([VelocityClass(2180.0, 1.0, contrast=0.0)])
    bins = equal_time_bins(4.0, [0.0, math.pi / 2, math.pi, 3 * math.pi / 2])
    require(m.expected_counts(0.0, bins) == m.expected_counts(50.0, bins), "C = 0: counts do not depend on a")
    require(m.modulation_phase(1.0) is None, "C = 0: phase undefined")
    full = model([VelocityClass(2180.0, 1.0, transmission=0.5, contrast=1.0)])
    counts = full.expected_counts(0.0, [ScanBin(1.0, math.pi - full.K(2180.0) * 0.0)])
    require(math.isclose(counts[0], 2.0, rel_tol=1e-12), "C = 1 at destructive phase: only background remains")
    return {"C0": "no information", "C1_dark_fringe": counts[0]}


def check_null_signal():
    m = model([VelocityClass(2180.0, 1.0, efficiency=0.0)], b=3.0)
    W, F = m.complex_contrast(9.81)
    require(W == 0 and F is None and m.detected_weights() is None, "no detected signal: W = 0, F undefined")
    require(m.expected_counts(9.81, [ScanBin(2.0, 0.3)]) == [6.0], "counts = background only")
    return {"W": 0}


def check_measurement_times_per_bin():
    bins = equal_time_bins(12.0, [0.0, 1.0, 2.0])
    require(math.isclose(total_measurement_time(bins), 12.0) and all(math.isclose(b.t, 4.0) for b in bins), "per-bin times sum to the total")
    m = model([VelocityClass(2180.0, 1.0, contrast=0.2)], b=0.0)
    c_split = sum(m.expected_counts(1.0, bins))
    c_wrong = sum(m.expected_counts(1.0, [ScanBin(12.0, b.alpha) for b in bins]))
    require(math.isclose(c_wrong, 3 * c_split, rel_tol=1e-12), "re-using the total time per bin would triple the counts")
    return {"total": 12.0}


def check_invalid_inputs():
    require(raises(lambda: model([VelocityClass(2180.0, 0.6), VelocityClass(3000.0, 0.6)])), "weights must sum to 1")
    require(raises(lambda: VelocityClass(2180.0, -0.1)) and raises(lambda: VelocityClass(2180.0, 0.0)), "weights must be positive")
    require(raises(lambda: VelocityClass(2180.0, 1.0, contrast=1.2)) and raises(lambda: VelocityClass(2180.0, 1.0, efficiency=-0.1)),
            "C and eps in [0, 1]")
    require(raises(lambda: model([VelocityClass(2180.0, 1.0, transmission=0.8, contrast=0.5)])), "A (1 + C) <= 1 for a probability")
    require(raises(lambda: ScanBin(1.0, 0.0, s=2)) and raises(lambda: ScanBin(0.0, 0.0)), "orientation and positive bin time")
    require(raises(lambda: VelocityClass(float("inf"), 1.0)), "non-finite velocity")
    return {"rejections": "ok"}


CHECKS = [
    check_single_velocity_limit,
    check_mu_c06_mixture_is_not_mean_velocity,
    check_mu_c07_detected_mixture,
    check_mu_c16_no_contrast_no_information,
    check_null_signal,
    check_measurement_times_per_bin,
    check_invalid_inputs,
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
    out_path = Path(__file__).with_name("verify_muonium_forward_results.json")
    out_path.write_text(json.dumps({"n_passed": n_passed, "n_total": len(CHECKS), "results": results}, indent=2, default=str))
    print(f"Report written to {out_path}")
    return 0 if n_passed == len(CHECKS) else 1


if __name__ == "__main__":
    raise SystemExit(main())
