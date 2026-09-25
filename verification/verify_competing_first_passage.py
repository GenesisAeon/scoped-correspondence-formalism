#!/usr/bin/env python3
"""Competing first-passage targets and committors (INTEGRATED_EXTENSION_ROADMAP.md
Paket C4).

Checks:

  1. Hand-verified 4-state control case: committor (0.6, 0.9), mean hitting
     times (0.6, 0.4), and finite-horizon (H=1) hitting probability to B
     (0.467359895563, 0.829637179582) from states i and j respectively.
  2. Rate rescaling invariance: multiplying every rate by a constant c leaves
     the committor UNCHANGED, divides mean hitting times by c, and leaves
     finite-horizon hitting probabilities unchanged when H is rescaled to
     H/c alongside the rates.
  3. A singular L_DD (an interior state that can never reach A union B)
     raises ScopeViolationError for both committor and mean_hitting_time.
  4. Bridge to Paket C2 (exact generator lumpability, reusing the EXISTING
     closure.generator_lumpability.is_exact_generator_lumpability rather
     than re-implementing it): a hand-constructed 6-state, 3-macro-class
     exactly lumpable generator gives IDENTICAL committor and mean-hitting-
     time values for the two micro states in the same interior macro class,
     matching the 3-state macro chain's own committor/mean-time exactly --
     checked at BOTH the boundary-value-problem level and via finite
     horizons, not just one.
  5. Finite-horizon hitting probabilities plus the unresolved probability
     sum to 1 for every start state, checked explicitly.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from scoped_correspondence.errors import ScopeViolationError  # noqa: E402
from scoped_correspondence.viability.competing_first_passage import (  # noqa: E402
    committor,
    mean_hitting_time,
    finite_horizon_hitting_probabilities,
)
from scoped_correspondence.closure.generator_lumpability import is_exact_generator_lumpability  # noqa: E402


def require(ok, msg):
    if not bool(ok):
        raise AssertionError(msg)


# order: A, i, j, B
L4 = np.array([
    [0.0, 0.0, 0.0, 0.0],
    [1.0, -3.0, 2.0, 0.0],
    [0.0, 1.0, -4.0, 3.0],
    [0.0, 0.0, 0.0, 0.0],
])


def check_control_case_committor_and_mean_time():
    q = committor(L4, A=[0], B=[3])
    m = mean_hitting_time(L4, A=[0], B=[3])
    require(abs(q[1] - 0.6) < 1e-9 and abs(q[2] - 0.9) < 1e-9, f"committor should be (0.6,0.9), got {q[1:3]!r}")
    require(abs(m[1] - 0.6) < 1e-9 and abs(m[2] - 0.4) < 1e-9, f"mean hitting times should be (0.6,0.4), got {m[1:3]!r}")
    return {"q_i": q[1], "q_j": q[2], "m_i": m[1], "m_j": m[2]}


def check_control_case_finite_horizon():
    res = finite_horizon_hitting_probabilities(L4, H=1.0, boundary_sets={"A": [0], "B": [3]})
    p_B = res.p_hit["B"]
    require(abs(p_B[1] - 0.467359895563) < 1e-9, f"p_B from i should be 0.467359895563, got {p_B[1]!r}")
    require(abs(p_B[2] - 0.829637179582) < 1e-9, f"p_B from j should be 0.829637179582, got {p_B[2]!r}")
    totals = res.p_hit["A"] + res.p_hit["B"] + res.p_unresolved
    require(np.allclose(totals, 1.0, atol=1e-9), f"hitting probs + unresolved should sum to 1; got {totals!r}")
    return {"p_B": p_B.tolist(), "p_unresolved": res.p_unresolved.tolist()}


def check_rate_rescaling_invariance():
    q_base = committor(L4, A=[0], B=[3])
    m_base = mean_hitting_time(L4, A=[0], B=[3])
    for c in (0.1, 2.0, 7.5):
        L_scaled = L4 * c
        q_scaled = committor(L_scaled, A=[0], B=[3])
        m_scaled = mean_hitting_time(L_scaled, A=[0], B=[3])
        require(np.allclose(q_scaled, q_base, atol=1e-9), f"c={c}: committor should be scale-invariant")
        require(np.allclose(m_scaled, m_base / c, atol=1e-9), f"c={c}: mean hitting time should scale as 1/c")

        res_base = finite_horizon_hitting_probabilities(L4, H=1.0, boundary_sets={"A": [0], "B": [3]})
        res_scaled = finite_horizon_hitting_probabilities(L_scaled, H=1.0 / c, boundary_sets={"A": [0], "B": [3]})
        require(np.allclose(res_scaled.p_hit["B"], res_base.p_hit["B"], atol=1e-9),
                f"c={c}: finite-horizon hitting probabilities should be invariant under (rates*c, H/c)")
    return {"checked_c": [0.1, 2.0, 7.5]}


def check_singular_L_DD_raises():
    # State 1 is interior but only connects to itself and never to A or B (isolated cycle).
    L_bad = np.array([
        [0.0, 0.0, 0.0, 0.0],
        [2.0, -2.0, 0.0, 0.0],  # only reaches state 0... wait this DOES reach A; construct genuinely unreachable case
        [0.0, 0.0, -1.0, 0.0],  # row sums to -1, NOT a valid generator on its own but isolates state 2
        [0.0, 0.0, 0.0, 0.0],
    ])
    # Fix state 2 to be a valid generator row that never leaves {2} (self-loop only has no meaning;
    # make it point only to itself via a zero effective generator row -- L_DD singular).
    L_bad[2, 2] = 0.0
    try:
        committor(L_bad, A=[0], B=[3])
        raise AssertionError("an interior state that never reaches A union B should raise ScopeViolationError")
    except ScopeViolationError:
        pass
    try:
        mean_hitting_time(L_bad, A=[0], B=[3])
        raise AssertionError("mean_hitting_time should also raise for the same singular case")
    except ScopeViolationError:
        pass
    return {"raised": 2}


def check_bridge_to_c2_lumpability():
    L6 = np.array([
        [-0.9, 0.4, 0.3, 0.2, 0.0, 0.0],
        [0.6, -1.1, 0.35, 0.15, 0.0, 0.0],
        [0.1, 0.2, -1.2, 0.5, 0.25, 0.15],
        [0.05, 0.25, 0.4, -1.1, 0.1, 0.3],
        [0.0, 0.0, 0.3, 0.3, -0.9, 0.3],
        [0.0, 0.0, 0.5, 0.1, 0.5, -1.1],
    ])
    C = np.array([[1, 0, 0], [1, 0, 0], [0, 1, 0], [0, 1, 0], [0, 0, 1], [0, 0, 1]], dtype=float)
    Q = np.array([[-0.5, 0.5, 0.0], [0.3, -0.7, 0.4], [0.0, 0.6, -0.6]])
    require(is_exact_generator_lumpability(L6, C, Q, tol=1e-9), "L6 must be exactly lumpable w.r.t. C onto Q")

    A, B, D = [0, 1], [4, 5], [2, 3]
    q_micro = committor(L6, A=A, B=B)
    m_micro = mean_hitting_time(L6, A=A, B=B)
    require(abs(q_micro[2] - q_micro[3]) < 1e-9, "the two interior micro states in the SAME macro class must get the SAME committor")
    require(abs(m_micro[2] - m_micro[3]) < 1e-9, "the two interior micro states in the SAME macro class must get the SAME mean hitting time")

    q_macro = committor(Q, A=[0], B=[2])
    m_macro = mean_hitting_time(Q, A=[0], B=[2])
    require(abs(q_micro[2] - q_macro[1]) < 1e-9, f"micro committor ({q_micro[2]!r}) must match the macro chain's own committor ({q_macro[1]!r})")
    require(abs(m_micro[2] - m_macro[1]) < 1e-9, f"micro mean time ({m_micro[2]!r}) must match the macro chain's own mean time ({m_macro[1]!r})")

    res_micro = finite_horizon_hitting_probabilities(L6, H=1.0, boundary_sets={"A": A, "B": B})
    res_macro = finite_horizon_hitting_probabilities(Q, H=1.0, boundary_sets={"A": [0], "B": [2]})
    require(abs(res_micro.p_hit["B"][2] - res_macro.p_hit["B"][1]) < 1e-9,
            "finite-horizon micro/macro hitting probabilities must ALSO agree, not just the BVP-level committor")
    return {
        "q_micro_interior": q_micro[2:4].tolist(), "q_macro_interior": float(q_macro[1]),
        "p_B_H1_micro": float(res_micro.p_hit["B"][2]), "p_B_H1_macro": float(res_macro.p_hit["B"][1]),
    }


CHECKS = [
    ("control_case_committor_and_mean_time", check_control_case_committor_and_mean_time),
    ("control_case_finite_horizon", check_control_case_finite_horizon),
    ("rate_rescaling_invariance", check_rate_rescaling_invariance),
    ("singular_L_DD_raises", check_singular_L_DD_raises),
    ("bridge_to_c2_lumpability", check_bridge_to_c2_lumpability),
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json-out", type=Path, default=Path(__file__).with_name("verify_competing_first_passage_results.json"))
    args = parser.parse_args()

    report = {
        "package": "INTEGRATED_EXTENSION_ROADMAP.md Paket C4 (competing first-passage targets and committors)",
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
