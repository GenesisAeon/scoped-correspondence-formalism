"""Paket PMF-Modus (recommendation of SCF_FOLLOWUP_REVIEW_637bc1c §5): optional
``input_mode="pmf"`` for directed_information and broja_pid_bivariate; the
documented ``"weights"`` mode stays the default.

Required controls (review §5): normalised distribution; the same distribution
with doubled mass; zero mass; negative and non-finite values; existing
information control cases. Plus: exact vs float semantics (exact total 1 for
int/Fraction, |total - 1| <= 1e-12 for floats), weight-scaling invariance in
``weights`` mode, reported ``input_mode`` / ``input_total_mass``, unknown mode
refused.

Expected values by hand: BSC(1/4) feedback n = 2 and the two-bit XOR / copy
joints have known information values (XOR synergy 1 bit, copy redundancy 1 bit;
for the feedback joint the pmf result must equal the weights result).
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
from scoped_correspondence.information_decomposition.broja import broja_pid_bivariate
from scoped_correspondence.observation.directed_information import bsc_feedback_joint, directed_information


def require(c, m=""):
    if not c:
        raise AssertionError(m)


def raises(fn):
    try:
        fn()
    except ScopeViolationError:
        return True
    return False


def _xor_joint(scale=1.0):
    J = np.zeros((2, 2, 2))
    for a in (0, 1):
        for b in (0, 1):
            J[a, b, a ^ b] = 0.25 * scale
    return J


def check_di_modes():
    j = bsc_feedback_joint(0.25, n=2)
    w = directed_information(j)
    p = directed_information(j, input_mode="pmf")
    require(w.input_mode == "weights" and p.input_mode == "pmf", "mode reported")
    require(math.isclose(w.I_directed, p.I_directed, abs_tol=1e-15) and abs(p.input_total_mass - 1) <= 1e-12, "normalised input: same result")
    doubled = {k: 2 * v for k, v in j.items()}
    require(raises(lambda: directed_information(doubled, input_mode="pmf")), "doubled mass refused in pmf mode")
    for c in (1e-3, 2.0, 7.0, 1e6):
        r = directed_information({k: c * v for k, v in j.items()})
        require(math.isclose(r.I_directed, w.I_directed, rel_tol=1e-12, abs_tol=1e-15), f"weights mode: scaling by {c} keeps the value")
        require(math.isclose(r.input_total_mass, c, rel_tol=1e-12), "original total reported")
    for bad in ({((0,), (0,)): 0.0, ((1,), (1,)): 0.0}, {((0,), (0,)): -0.5, ((1,), (1,)): 1.5},
                {((0,), (0,)): float("nan"), ((1,), (1,)): 1.0}, {((0,), (0,)): float("inf"), ((1,), (1,)): 1.0}):
        for mode in ("weights", "pmf"):
            require(raises(lambda: directed_information(bad, input_mode=mode)), f"{mode}: must refuse {bad}")
    exact = {((0,), (0,)): F(1, 3), ((1,), (1,)): F(1, 3), ((0,), (1,)): F(1, 3)}
    require(directed_information(exact, input_mode="pmf").input_total_mass == 1.0, "exact thirds sum to exactly 1")
    exact_off = {((0,), (0,)): F(1, 3), ((1,), (1,)): F(1, 3), ((0,), (1,)): F(1, 3) + F(1, 10 ** 15)}
    require(raises(lambda: directed_information(exact_off, input_mode="pmf")), "exact input: no float tolerance (1e-15 off is refused)")
    tenths = {(tuple((i >> b) & 1 for b in range(4)), (0, 0, 0, 0)): 0.1 for i in range(10)}  # ten distinct atoms
    require(len(tenths) == 10 and sum(tenths.values()) != 1.0, "float tenths do not sum to exactly 1.0 in binary")
    rt = directed_information(tenths, input_mode="pmf")  # must be accepted within PMF_TOL
    require(abs(rt.input_total_mass - 1) <= 1e-12, "float tenths accepted within the documented tolerance")
    require(raises(lambda: directed_information({k: 0.1 + 1e-10 for k in tenths}, input_mode="pmf")), "1e-9 total excess refused")
    require(raises(lambda: directed_information(j, input_mode="probabilities")), "unknown mode refused")
    return {"I_directed": w.I_directed}


def check_broja_modes():
    w = broja_pid_bivariate(_xor_joint())
    p = broja_pid_bivariate(_xor_joint(), input_mode="pmf")
    require(abs(p.synergy - 1) < 1e-6 and abs(w.synergy - p.synergy) < 1e-12, "XOR synergy 1 bit in both modes")
    require(p.input_mode == "pmf" and w.input_mode == "weights" and p.input_total_mass == 1.0, "mode and total reported")
    require(raises(lambda: broja_pid_bivariate(_xor_joint(2.0), input_mode="pmf")), "doubled mass refused in pmf mode")
    d = broja_pid_bivariate(_xor_joint(2.0))
    require(abs(d.synergy - w.synergy) < 1e-9 and d.input_total_mass == 2.0, "weights mode: doubled mass, same atoms")
    copy = np.zeros((2, 2, 2))
    copy[0, 0, 0] = copy[1, 1, 1] = F(1, 2)
    exact_copy = [[[F(1, 2), 0], [0, 0]], [[0, 0], [0, F(1, 2)]]]
    rc = broja_pid_bivariate(exact_copy, input_mode="pmf")
    require(abs(rc.redundancy - 1) < 1e-6, "exact copy joint: redundancy 1 bit")
    exact_bad = [[[F(1, 2), 0], [0, 0]], [[0, 0], [0, F(1, 2) + F(1, 10 ** 15)]]]
    require(raises(lambda: broja_pid_bivariate(exact_bad, input_mode="pmf")), "exact input: no tolerance")
    for bad in (np.zeros((2, 2, 2)), -_xor_joint(), np.full((2, 2, 2), float("nan"))):
        for mode in ("weights", "pmf"):
            require(raises(lambda: broja_pid_bivariate(bad, input_mode=mode)), f"{mode}: must refuse zero/negative/non-finite")
    require(raises(lambda: broja_pid_bivariate(_xor_joint(), input_mode="probabilities")), "unknown mode refused")
    return {"xor_synergy": p.synergy, "copy_redundancy": rc.redundancy}


CHECKS = [check_di_modes, check_broja_modes]


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
    Path(__file__).with_name("verify_information_input_modes_results.json").write_text(
        json.dumps({"n_passed": n_passed, "n_total": len(CHECKS), "results": results}, indent=2, default=str), encoding="utf-8")
    return 0 if n_passed == len(CHECKS) else 1


if __name__ == "__main__":
    raise SystemExit(main())
