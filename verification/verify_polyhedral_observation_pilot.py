"""TP1 verification (CANDIDATE_PILOTS_ROADMAP.md): polyhedral observation pilot.

TP-C01 (Euler arithmetic; genus only under declared manifold premises),
TP-C02 (C8 vs C4+C4: shared coarse fibre, split by the refined
observation), TP-C03 (T^4 = I, det T = -1: rotoreflection), TP-C04 (exact
coplanarity vs a 1e-12 deviation). Controls derived independently here (the
assessment's companion script was not received).
"""
from __future__ import annotations

import json
import sys
from fractions import Fraction as F
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from scoped_correspondence.errors import ScopeViolationError
from scoped_correspondence.validation.polyhedral_observation_pilot import (
    ROTOREFLECTION,
    c4_plus_c4,
    c8,
    coarse_observation,
    coplanar_exact,
    euler_characteristic,
    euler_genus,
    graph_fibre,
    order_and_determinant,
    refined_observation,
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


def check_tp_c01_euler_without_genus_overreach():
    require(euler_characteristic(24, 36, 8) == -4, "24 - 36 + 8 = -4")
    require(euler_genus(24, 36, 8, closed=True, connected=True, orientable=True, vertex_links_are_circles=True) == 3,
            "chi = -4 gives g = 3 under the manifold premises")
    require(euler_genus(24, 36, 8, closed=True, connected=True, orientable=True, vertex_links_are_circles=False) is None,
            "without circle vertex links no genus statement (e.g. two complexes glued at a singular vertex)")
    require(raises(lambda: euler_genus(1, 0, 0, closed=True, connected=True, orientable=True, vertex_links_are_circles=True)),
            "odd 2 - chi is impossible for an orientable closed surface")
    return {"chi": -4, "genus_if_premises": 3}


def check_tp_c02_coarse_fibre_shared_refined_split():
    a, b = c8(), c4_plus_c4()
    require(coarse_observation(a) == coarse_observation(b) == (8, 8, (2,) * 8), "same V, E and degree sequence")
    require(a.components() == 1 and b.components() == 2, "1 vs 2 components: not isomorphic")
    coarse = graph_fibre([a, b], coarse_observation, coarse_observation(a))
    fine = graph_fibre([a, b], refined_observation, refined_observation(a))
    require(coarse.fiber == ("C8", "C4+C4") and fine.fiber == ("C8",), "refinement splits the shared coarse fibre")
    return {"coarse_fibre": list(coarse.fiber), "refined_fibre": list(fine.fiber),
            "note": "graph fact only; no polyhedron construction is certified by this"}


def check_tp_c03_rotoreflection():
    order, det = order_and_determinant(ROTOREFLECTION)
    require(order == 4 and det == -1, f"T^4 = I and det T = -1, got order {order}, det {det}")
    quarter_turn = [[0, 1, 0], [-1, 0, 0], [0, 0, 1]]
    require(order_and_determinant(quarter_turn) == (4, 1), "a pure quarter turn has det +1 -- a different transformation")
    return {"order": order, "det": det}


def check_tp_c04_exact_coplanarity():
    pts = [(0, 0, 0), (1, 0, 0), (0, 1, 0), (F(1, 3), F(2, 7), 0)]
    require(coplanar_exact(pts), "exactly coplanar rational points")
    near = pts[:3] + [(F(1, 3), F(2, 7), F(1, 10 ** 12))]
    require(not coplanar_exact(near), "a 1e-12 deviation is NOT rounded onto the plane in exact mode")
    require(raises(lambda: coplanar_exact([(0.0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1e-12)])), "floats refused in exact mode")
    return {"exact": True, "near_coplanar_detected": True}


CHECKS = [check_tp_c01_euler_without_genus_overreach, check_tp_c02_coarse_fibre_shared_refined_split,
          check_tp_c03_rotoreflection, check_tp_c04_exact_coplanarity]


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
    Path(__file__).with_name("verify_polyhedral_observation_pilot_results.json").write_text(
        json.dumps({"n_passed": n_passed, "n_total": len(CHECKS), "results": results}, indent=2, default=str), encoding="utf-8")
    return 0 if n_passed == len(CHECKS) else 1


if __name__ == "__main__":
    raise SystemExit(main())
