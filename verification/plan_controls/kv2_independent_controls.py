"""Independent re-derivation of the KV2 control cases (mean dynamics vs f0 identifiability, with memory).

Part of package KV2 (KOSMISCHE_VERERBUNG_SCF_ROADMAP.md). Follows Astra's review note of 2026-10-12:
"Does the mean today determine the future mean?" and "does the mean determine f0?" are SEPARATE questions,
even for a linear rule; delayed returns are state (memory).

Plan-arithmetic layer only: no SCF import, standard library only, exact Fractions. Not a regression test.

Discrete-time two-zone model, every quantity exact:
  zone i has gas mass m_i and metal mass q_i (Z_i = q_i / m_i); a return buffer holds, per zone, the gas and metal
  mass that stars formed in the PREVIOUS step give back (lifetime = 1 step).
  One step:  (1) add the buffered returns to their zone;
             (2) star formation s_i = e * m_i takes gas of the zone's composition (metal s_i * Z_i);
                 next step returns gas R * s_i and metal R * s_i * Z_i + y(Z_i) * s_i (net yield rule y);
             (3) symmetric exchange: a fraction k of each zone's gas (with its metal) moves to the other zone.
  Observation h = mean metallicity Zbar = (q_1 + q_2) / (m_1 + m_2); f0 = gas-mass fraction of zones with Z < z_crit.

    python verification/plan_controls/kv2_independent_controls.py [--output FILE]

License: GPL-3.0-or-later.
"""
from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from pathlib import Path

E, R, K = F(1, 10), F(3, 10), F(1, 10)
Z_CRIT = F(1, 100000)
RULES = {
    "L": lambda z: F(1, 100),                                   # Z-blind constant net yield
    "P3": lambda z: F(3, 100) if z < Z_CRIT else F(1, 100),    # threshold: pristine gas gets a higher yield
    "S": lambda z: R * min(F(1, 30), max(F(1, 25) - z, F(0))), # Z-blind but saturated (counter-model)
}
RESULTS: dict[str, dict] = {}


def state(zs, masses=(F(1), F(1)), buffer=((F(0), F(0)), (F(0), F(0)))):
    return {"m": list(masses), "q": [m * z for m, z in zip(masses, zs)], "buf": [list(b) for b in buffer]}


def step(st, rule, k):
    m, q = list(st["m"]), list(st["q"])
    for i in (0, 1):                                    # (1) returns
        m[i] += st["buf"][i][0]
        q[i] += st["buf"][i][1]
    buf = []
    for i in (0, 1):                                    # (2) star formation
        z = q[i] / m[i]
        s = E * m[i]
        m[i] -= s
        q[i] -= s * z
        buf.append([R * s, R * s * z + rule(z) * s])
    dm, dq = K * k, None                                # (3) exchange (k is a multiplier on K: 0 or 1)
    m2 = [m[0] - dm * m[0] + dm * m[1], m[1] - dm * m[1] + dm * m[0]]
    q2 = [q[0] - dm * q[0] + dm * q[1], q[1] - dm * q[1] + dm * q[0]]
    return {"m": m2, "q": q2, "buf": buf}


def zbar(st):
    return sum(st["q"]) / sum(st["m"])


def f0(st):
    return sum(m for m, q in zip(st["m"], st["q"]) if q / m < Z_CRIT) / sum(st["m"])


def run(st, rule, k, n):
    out = [zbar(st)]
    for _ in range(n):
        st = step(st, rule, k)
        out.append(zbar(st))
    return out


def record(cid, **kw):
    RESULTS[cid] = {key: ([str(x) for x in v] if isinstance(v, list) else str(v) if isinstance(v, F) else v) for key, v in kw.items()}


def main() -> dict:
    A = state((F(0), F(1, 50)))          # heterogeneous: one pristine zone
    B = state((F(1, 100), F(1, 100)))    # homogeneous
    # KV2-C1: f0 identifiability at t = 0 -- same mean, different f0 (independent of any rule)
    record("KV2-C1", zbar_A=zbar(A), zbar_B=zbar(B), f0_A=f0(A), f0_B=f0(B), identified=f0(A) == f0(B))
    # KV2-C2: mean dynamics -- same observed mean, empty buffers: does the future mean agree? (3 steps, k in {0, 1})
    for rule in RULES:
        for k in (0, 1):
            a, b = run(A, RULES[rule], k, 3), run(B, RULES[rule], k, 3)
            record(f"KV2-C2 {rule} k={k}", zbar_A=a, zbar_B=b, equal_all_steps=a == b,
                   r_step3=(a[3] - b[3]) / b[3])
    # KV2-C3: memory -- linear rule, SAME zones and SAME current mean, but different return buffer (history):
    # the future mean differs, so Zbar alone is not a complete state even for L.
    B_buf = state((F(1, 100), F(1, 100)), buffer=((F(1, 20), F(1, 1000)), (F(0), F(0))))
    B_buf2 = state((F(1, 100), F(1, 100)), buffer=((F(1, 20), F(1, 2000)), (F(0), F(0))))
    a, b = run(B_buf, RULES["L"], 1, 2), run(B_buf2, RULES["L"], 1, 2)
    record("KV2-C3 L memory", zbar_now_1=a[0], zbar_now_2=b[0], zbar_next_1=a[1], zbar_next_2=b[1], equal_next=a[1] == b[1])
    # KV2-C4: closure of the AGGREGATED state for L: (sum m, sum q, sum buffer gas, sum buffer metal) after one step
    # depends only on the aggregated state -- checked on A and B (same aggregate) and on a third state C with the
    # same aggregate but different split.
    C = state((F(1, 200), F(3, 200)))
    agg = lambda st: (sum(st["m"]), sum(st["q"]), sum(x[0] for x in st["buf"]), sum(x[1] for x in st["buf"]))
    for k in (0, 1):
        nxt = [agg(step(s, RULES["L"], k)) for s in (A, B, C)]
        record(f"KV2-C4 L aggregate k={k}", same_aggregate_before=len({agg(s) for s in (A, B, C)}) == 1,
               same_aggregate_after=len(set(nxt)) == 1, aggregate_after=[str(x) for x in nxt[0]])
        nxt_p3 = [agg(step(s, RULES["P3"], k)) for s in (A, B)]
        record(f"KV2-C4 P3 aggregate k={k}", same_aggregate_after=len(set(nxt_p3)) == 1)
    return RESULTS


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, default=None)
    a = ap.parse_args()
    res = main()
    text = json.dumps(res, indent=1, ensure_ascii=False) + "\n"
    if a.output:
        a.output.write_text(text, encoding="utf-8")
    print(text)
