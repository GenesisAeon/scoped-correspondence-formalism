"""KV2 verification: mean dynamics and f0 identifiability are SEPARATE questions (with memory).

Kosmische Vererbung, SCF side (KOSMISCHE_VERERBUNG_SCF_ROADMAP.md, KV2), following Astra's review note of
2026-10-12. Control values were hand-derived and independently recomputed with Fractions BEFORE this file
(verification/plan_controls/kv2_independent_controls.py, no SCF import). Here they are checked with the production
observation-fiber API over a finite, declared state space.

Model (exact Fractions): two zones with gas m_i and metal q_i, a one-step return buffer per zone (memory),
star formation e*m_i of the zone's composition, net yield rule y(Z), symmetric exchange K. Rules: L (Z-blind),
P3 (threshold), S (saturated, no Pop-III special case). Observation h = mean metallicity Zbar.

All statements are "under the rules and the declared state space examined here": a finite counterexample proves
non-identifiability; agreement on the finite space proves nothing beyond it. Result status: synthetic_only.
"""
from __future__ import annotations

import itertools
import json
import sys
from fractions import Fraction as F
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from scoped_correspondence.epistemic.observation_fibers import identified_values, observation_fiber
from scoped_correspondence.epistemic.records import FiniteDomainSpec

E, R, K = F(1, 10), F(3, 10), F(1, 10)
Z_CRIT = F(1, 100000)
RULES = {
    "L": lambda z: F(1, 100),
    "P3": lambda z: F(3, 100) if z < Z_CRIT else F(1, 100),
    "S": lambda z: R * min(F(1, 30), max(F(1, 25) - z, F(0))),
}
GRID = (F(0), F(1, 100), F(1, 50))


def require(condition, msg=""):
    if not condition:
        raise AssertionError(msg)


# A state is a hashable tuple: (m1, q1, m2, q2, bm1, bq1, bm2, bq2)
def make(z1, z2, buf=(F(0), F(0), F(0), F(0))):
    return (F(1), z1, F(1), z2, *buf)


def step(s, rule, k):
    m, q = [s[0], s[2]], [s[1], s[3]]
    m[0] += s[4]; q[0] += s[5]; m[1] += s[6]; q[1] += s[7]
    buf = []
    for i in (0, 1):
        z = q[i] / m[i]
        st = E * m[i]
        m[i] -= st
        q[i] -= st * z
        buf += [R * st, R * st * z + rule(z) * st]
    d = K * k
    m2 = (m[0] - d * m[0] + d * m[1], m[1] - d * m[1] + d * m[0])
    q2 = (q[0] - d * q[0] + d * q[1], q[1] - d * q[1] + d * q[0])
    return (m2[0], q2[0], m2[1], q2[1], *buf)


def zbar(s):
    return (s[1] + s[3]) / (s[0] + s[2])


def f0(s):
    return sum(m for m, q in ((s[0], s[1]), (s[2], s[3])) if q / m < Z_CRIT) / (s[0] + s[2])


def future_zbar(rule, k, n):
    def target(s):
        for _ in range(n):
            s = step(s, rule, k)
        return zbar(s)
    return target


def aggregate(s):
    return (s[0] + s[2], s[1] + s[3], s[4] + s[6], s[5] + s[7])


def domain_empty_buffers():
    return FiniteDomainSpec(id="kv2_two_zones_empty_buffer", candidates=tuple(make(a, b) for a, b in itertools.product(GRID, repeat=2)),
                            scope_text="two equal-mass zones, Z on {0, 1/100, 1/50}, empty return buffer",
                            relationship_to_target_space="restricted_candidates", arithmetic_kind="rational")


def domain_with_history():
    base = [make(a, b) for a, b in itertools.product(GRID, repeat=2)]
    hist = [make(F(1, 100), F(1, 100), (F(1, 20), F(1, 1000), F(0), F(0))),
            make(F(1, 100), F(1, 100), (F(1, 20), F(1, 2000), F(0), F(0)))]
    return FiniteDomainSpec(id="kv2_two_zones_with_history", candidates=tuple(base + hist),
                            scope_text="as kv2_two_zones_empty_buffer plus two states with a non-empty return buffer (history)",
                            relationship_to_target_space="restricted_candidates", arithmetic_kind="rational")


def check_c1_mean_does_not_identify_f0():
    """y = 1/100: fiber {(0,1/50), (1/100,1/100), (1/50,0)}; f0 in {0, 1/2} -- not identified, for ANY rule."""
    fib = observation_fiber(domain_empty_buffers(), [], zbar, F(1, 100))
    require(fib.search_complete and len(fib.fiber) == 3, f"fiber {fib.fiber}")
    q = identified_values(fib, f0)
    require(not q.point_identified and set(q.values) == {F(0), F(1, 2)}, f"f0 values {q.values}")
    return {"fiber_size": len(fib.fiber), "f0_values": sorted(str(v) for v in q.values)}


def check_c2_mean_dynamics_rule_dependent():
    """Empty buffers: the future mean (3 steps) is point-identified by the current mean for L at every observed value,
    and NOT for P3 and S at y = 1/100 (k in {0, 1})."""
    dom = domain_empty_buffers()
    ys = sorted({zbar(s) for s in dom.candidates})
    out = {}
    for rule in RULES:
        for k in (0, 1):
            ident = {str(y): identified_values(observation_fiber(dom, [], zbar, y), future_zbar(RULES[rule], k, 3)).point_identified for y in ys}
            out[f"{rule} k={k}"] = ident
            if rule == "L":
                require(all(ident.values()), f"L must be identified everywhere, got {ident}")
            else:
                require(not ident[str(F(1, 100))], f"{rule} k={k} must NOT be identified at y=1/100")
    q = identified_values(observation_fiber(dom, [], zbar, F(1, 100)), future_zbar(RULES["L"], 1, 2))
    require(q.values == (F(103, 9300),), f"L k=1, 2 steps: expected 103/9300, got {q.values}")
    return out


def check_c2_hand_values_p3_s():
    """Exact 3-step means from the independent controls: P3 A 41/3100 vs B 113/9300 (r = 10/113);
    S (k=0) A 844/72075 vs B 286/24025 (r = -7/429), S (k=1) A 677/57660 (r = -47/3432)."""
    A, B = make(F(0), F(1, 50)), make(F(1, 100), F(1, 100))
    p3a, p3b = future_zbar(RULES["P3"], 1, 3)(A), future_zbar(RULES["P3"], 1, 3)(B)
    require((p3a, p3b) == (F(41, 3100), F(113, 9300)) and (p3a - p3b) / p3b == F(10, 113), f"P3 {p3a} {p3b}")
    s0 = future_zbar(RULES["S"], 0, 3)(A), future_zbar(RULES["S"], 0, 3)(B)
    s1 = future_zbar(RULES["S"], 1, 3)(A)
    require(s0 == (F(844, 72075), F(286, 24025)) and (s0[0] - s0[1]) / s0[1] == F(-7, 429), f"S k=0 {s0}")
    require(s1 == F(677, 57660) and (s1 - s0[1]) / s0[1] == F(-47, 3432), f"S k=1 {s1}")
    return {"r_P3": "10/113", "r_S_k0": "-7/429", "r_S_k1": "-47/3432"}


def check_c3_memory_breaks_mean_sufficiency_even_for_l():
    """With history in the state space, L's next mean is NOT identified by the current mean (21/2050 vs 1/100)."""
    q = identified_values(observation_fiber(domain_with_history(), [], zbar, F(1, 100)), future_zbar(RULES["L"], 1, 1))
    require(not q.point_identified and {F(21, 2050), F(1, 100)} <= set(q.values), f"values {q.values}")
    return {"next_mean_values": sorted(str(v) for v in q.values)}


def check_c4_aggregate_state_closes_l_not_p3():
    """Observing the aggregate (total gas, total metal, total buffered gas, total buffered metal) point-identifies L's
    next aggregate on the whole history domain; for P3 it does not (A and B share the aggregate)."""
    dom = domain_with_history()
    aggs = sorted({aggregate(s) for s in dom.candidates})
    nxt = lambda rule: (lambda s: aggregate(step(s, RULES[rule], 1)))
    l_ok = all(identified_values(observation_fiber(dom, [], aggregate, a), nxt("L")).point_identified for a in aggs)
    require(l_ok, "L: aggregate must be closed on the declared domain")
    a0 = aggregate(make(F(0), F(1, 50)))
    p3 = identified_values(observation_fiber(dom, [], aggregate, a0), nxt("P3"))
    require(not p3.point_identified, "P3: aggregate must NOT be closed")
    return {"n_aggregate_classes": len(aggs), "L_closed": l_ok, "P3_closed": p3.point_identified}


CHECKS = [
    check_c1_mean_does_not_identify_f0,
    check_c2_mean_dynamics_rule_dependent,
    check_c2_hand_values_p3_s,
    check_c3_memory_breaks_mean_sufficiency_even_for_l,
    check_c4_aggregate_state_closes_l_not_p3,
]


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
    out = Path(__file__).with_name("verify_kv2_mean_dynamics_and_f0_results.json")
    out.write_text(json.dumps({"n_passed": n_passed, "n_total": len(CHECKS), "evidence_kind": "exhaustive_finite",
                               "empirical_status": "synthetic_only", "scope": "declared finite state space and rules L/P3/S only",
                               "results": results}, indent=2, default=str), encoding="utf-8")
    print(f"Report written to {out}")
    return 0 if n_passed == len(CHECKS) else 1


if __name__ == "__main__":
    raise SystemExit(main())
