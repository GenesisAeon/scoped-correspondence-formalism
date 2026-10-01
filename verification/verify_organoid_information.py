"""ON5 verification (ORGANOID_NETWORK_ROADMAP.md, plan section 10/ON5):
information, PID and directedness.

ON-C14 (XOR signature (0, 0, 1) and BROJA synergy 1 bit; copy signature
(1, 1, 1) and redundancy 1 bit; the existing cooperative-agents XOR task
agrees), ON-C15 (A = (U, 0), B = (0, U): directed information 1 bit, but
do(A1) does not change B2 -- never labelled causal), ON-C16 (block time equal
to the label: 1 bit confounding; randomised: 0), plus strict rejection of
non-normalised joints that the existing functions would renormalise.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from scoped_correspondence.errors import ScopeViolationError
from scoped_correspondence.validation.cooperative_agents_pilot import evaluate_xor_task
from scoped_correspondence.validation.modular_networks.information import (
    directed_report,
    information_signature,
    intervention_effect,
    label_confounding,
    pid_report,
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


def check_on_c14_signature_and_pid():
    xor = {(a, b, a ^ b): 0.25 for a in (0, 1) for b in (0, 1)}
    copy = {(s, s, s): 0.5 for s in (0, 1)}
    sx, sc = information_signature(xor), information_signature(copy)
    require(sx == (0.0, 0.0, 1.0), f"XOR signature (0, 0, 1), got {sx}")
    require(all(math.isclose(v, 1.0) for v in sc), f"copy signature (1, 1, 1), got {sc}")
    J = np.zeros((2, 2, 2))
    for (a, b, y), p in xor.items():
        J[a, b, y] = p
    px = pid_report(J)
    require(abs(px.synergy - 1) < 1e-6 and abs(px.redundancy) < 1e-6, f"XOR: synergy 1 bit, got {px}")
    require(px.converged and px.n_starts >= 3 and px.start_spread_bits < 1e-6, "solver actually run; convergence reported separately")
    Jc = np.zeros((2, 2, 2))
    for (a, b, y), p in copy.items():
        Jc[a, b, y] = p
    pc = pid_report(Jc)
    require(abs(pc.redundancy - 1) < 1e-6 and abs(pc.synergy) < 1e-6, f"copy: redundancy 1 bit, got {pc}")
    existing = evaluate_xor_task()
    require(abs(existing.pid.synergy - px.synergy) < 1e-6, "agrees with the existing cooperative-agents XOR task")
    return {"xor_signature": list(sx), "xor_synergy": px.synergy, "copy_redundancy": pc.redundancy}


def check_on_c15_directed_not_causal():
    joint = {((u, 0), (0, u)): 0.5 for u in (0, 1)}
    r = directed_report(joint)
    require(math.isclose(r.I_directed, 1.0, abs_tol=1e-12) and r.causal_claim is False, f"DI 1 bit, never causal; got {r}")

    def gen(u, do):
        a1 = do.get("A1", u)
        return {"A1": a1, "A2": 0, "B1": 0, "B2": u}  # B2 driven by U, not by A1

    require(intervention_effect(gen, {0: 0.5, 1: 0.5}, "A1", (0, 1), "B2") is False, "do(A1) leaves B2 unchanged")

    def gen_causal(u, do):
        a1 = do.get("A1", u)
        return {"A1": a1, "B2": a1}

    require(intervention_effect(gen_causal, {0: 0.5, 1: 0.5}, "A1", (0, 1), "B2") is True, "positive control: real effect detected")
    return {"I_directed": r.I_directed, "intervention_effect": False}


def check_on_c16_label_confounding():
    require(math.isclose(label_confounding({(s, s): 0.5 for s in (0, 1)}), 1.0), "block time = label: 1 bit")
    require(label_confounding({(s, t): 0.25 for s in (0, 1) for t in (0, 1)}) == 0.0, "randomised: 0 bit")
    return {"confounded": 1.0, "randomised": 0.0}


def check_strict_joints():
    require(raises(lambda: information_signature({(0, 0, 0): 0.5})), "non-normalised joint refused")
    require(raises(lambda: pid_report(np.full((2, 2, 2), 0.25))), "mass 2 refused (BROJA would renormalise)")
    require(raises(lambda: directed_report({((0,), (0,)): 0.7, ((1,), (1,)): 0.7})), "DI joint not normalised refused")
    require(raises(lambda: information_signature({(0, 0, 0): float("nan"), (1, 1, 1): 1.0})), "non-finite refused")
    return {"strict": True}


CHECKS = [check_on_c14_signature_and_pid, check_on_c15_directed_not_causal, check_on_c16_label_confounding, check_strict_joints]


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
    Path(__file__).with_name("verify_organoid_information_results.json").write_text(
        json.dumps({"n_passed": n_passed, "n_total": len(CHECKS), "results": results}, indent=2, default=str), encoding="utf-8")
    return 0 if n_passed == len(CHECKS) else 1


if __name__ == "__main__":
    raise SystemExit(main())
