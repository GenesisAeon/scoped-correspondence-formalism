"""ON1 verification (ORGANOID_NETWORK_ROADMAP.md, plan section 10/ON1):
exact observation and structure controls.

ON-C01 (W(1/2) responses, sums 2, det W = 4 delta), ON-C02 (full observer
1 bit, sum observer 0 bit, coarse fibre contains both stimuli; delta = 0 gives
0 bit for both), ON-C03 (invertible sensor permutation keeps the
information); delta outside [0, 1], invalid dimensions, non-finite / float
inputs in exact mode rejected. Expected values from
verification/plan_controls/on_series_independent_controls.py.
"""
from __future__ import annotations

import json
import sys
from fractions import Fraction as F
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from scoped_correspondence.errors import ScopeViolationError
from scoped_correspondence.validation.modular_networks.observation_controls import (
    STIMULI,
    exact_information_bits,
    observe_full,
    observe_sum,
    respond,
    response_operator,
    sensor_permutation,
    stimulus_fibre,
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


def check_on_c01_operator():
    W = response_operator(F(1, 2))
    y0, y1 = respond(W, STIMULI[0]), respond(W, STIMULI[1])
    require(y0 == (F(3, 2), F(1, 2)) and y1 == (F(1, 2), F(3, 2)), f"responses, got {y0}, {y1}")
    require(observe_sum(y0) == observe_sum(y1) == 2, "column sums 2: identical total activity")
    for d in (F(0), F(1, 3), F(1)):
        Wd = response_operator(d)
        require(Wd[0][0] * Wd[1][1] - Wd[0][1] * Wd[1][0] == 4 * d, "det W = 4 delta")
    return {"y0": [str(x) for x in y0], "y1": [str(x) for x in y1]}


def check_on_c02_full_vs_sum_observer():
    require(exact_information_bits(F(1, 2), observe_full) == 1 and exact_information_bits(F(1, 2), observe_sum) == 0,
            "full 1 bit, sum 0 bit")
    require(exact_information_bits(F(1, 10 ** 9), observe_full) == 1, "noiseless: any delta > 0 gives 1 bit (no tipping claim)")
    require(exact_information_bits(0, observe_full) == 0 == exact_information_bits(0, observe_sum), "delta = 0: 0 bit for both")
    fib = stimulus_fibre(F(1, 2), observe_sum, F(2))
    require(fib.fiber == (0, 1), "the coarse (sum) fibre contains both stimuli")
    fine = stimulus_fibre(F(1, 2), observe_full, (F(3, 2), F(1, 2)))
    require(fine.fiber == (0,), "the full observation identifies the stimulus")
    return {"I_full": 1, "I_sum": 0, "sum_fibre": list(fib.fiber)}


def check_on_c03_sensor_permutation():
    perm = lambda y: sensor_permutation(observe_full(y))
    require(exact_information_bits(F(1, 2), perm) == 1, "invertible sensor relabelling keeps the information")
    return {"I_permuted": 1}


def check_rejections():
    require(raises(lambda: response_operator(F(3, 2))) and raises(lambda: response_operator(-1)), "delta outside [0, 1]")
    require(raises(lambda: response_operator(0.5)), "float delta refused in the exact model (noise belongs to ON2)")
    require(raises(lambda: respond(response_operator(F(1, 2)), (1, 0, 0))), "invalid dimension")
    require(raises(lambda: respond(response_operator(F(1, 2)), (float("nan"), 0))), "non-finite input")
    return {"rejections": "ok"}


CHECKS = [check_on_c01_operator, check_on_c02_full_vs_sum_observer, check_on_c03_sensor_permutation, check_rejections]


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
    Path(__file__).with_name("verify_organoid_observation_controls_results.json").write_text(
        json.dumps({"n_passed": n_passed, "n_total": len(CHECKS), "results": results}, indent=2, default=str), encoding="utf-8")
    return 0 if n_passed == len(CHECKS) else 1


if __name__ == "__main__":
    raise SystemExit(main())
