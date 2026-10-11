"""Independent re-derivation of the KV control cases MV-K1..MV-K4 ("Mittelwert gegen Verteilung").

Part of package KV0 (KOSMISCHE_VERERBUNG_SCF_ROADMAP.md). Plan:
prompts/Answers/nicht_stationäre_Treiber/KOSMISCHE_VERERBUNG_BESTANDSAUFNAHME_UND_PLAN.md, section 6.2
(and section 8: observation fibers, controlled Markov correspondence).

Plan-arithmetic layer only: no SCF import, standard library only, exact Fractions throughout.
Written from hand derivations before any production code. Not a repository regression test
(not named verify_*.py).

Model: two equal-mass gas parcels; metallicity in units u = 0.01 on the grid {0, 1, 2};
micro state (z1, z2). Observation h = mean metallicity; target f0 = pristine (Z = 0) mass fraction.

    python verification/plan_controls/kv_series_independent_controls.py [--output FILE]

License: GPL-3.0-or-later.
"""
from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from itertools import product
from pathlib import Path

STATES = list(product(range(3), repeat=2))  # index 3*z1 + z2, the order SCF tests will use
RESULTS: dict[str, dict] = {}


def mean(s):
    return F(s[0] + s[1], 2)


def f0(s):
    return F(sum(1 for z in s if z == 0), 2)


def multiset(s):
    return tuple(sorted(s))


def record(cid, **kw):
    def enc(v):
        if isinstance(v, F):
            return str(v)
        if isinstance(v, (list, tuple)):
            return [enc(x) for x in v]
        return v
    RESULTS[cid] = {k: enc(v) for k, v in kw.items()}


def step_kernel(g):
    """One star-formation step: a uniformly chosen parcel i (probability 1/2) gets z_i -> g(z_i)."""
    P = {s: {} for s in STATES}
    for s in STATES:
        for i in (0, 1):
            t = list(s)
            t[i] = g(s[i])
            t = tuple(t)
            P[s][t] = P[s].get(t, F(0)) + F(1, 2)
    return P


def mixing_kernel():
    """Sum-preserving redistribution: jump uniformly to any state with the same total metal."""
    P = {}
    for s in STATES:
        same = [t for t in STATES if sum(t) == sum(s)]
        P[s] = {t: F(1, len(same)) for t in same}
    return P


def max_defect(P, label):
    """Largest within-class spread of the lumped (block-sum) probabilities, as in the exact
    lumpability condition: (defect, (class, column, row_min, row_max)) or (0, None)."""
    classes = sorted({label(s) for s in STATES})
    best = (F(0), None)
    for c in classes:
        members = [s for s in STATES if label(s) == c]
        rows = {s: {k: sum((p for t, p in P[s].items() if label(t) == k), F(0)) for k in classes} for s in members}
        for k in classes:
            col = [rows[s][k] for s in members]
            d = max(col) - min(col)
            if d > best[0]:
                lo = min(members, key=lambda s: rows[s][k])
                hi = max(members, key=lambda s: rows[s][k])
                best = (d, (c, k, lo, hi))
    return best


def main() -> dict:
    # MV-K1: observation fibers of the mean, identified f0 values and the boolean claim f0 > 0
    for y in (F(0), F(1, 2), F(1), F(3, 2), F(2), F(5, 2)):
        fib = [s for s in STATES if mean(s) == y]
        values = sorted({f0(s) for s in fib})
        claim = sorted({f0(s) > 0 for s in fib})
        record(f"MV-K1 y={y}", fiber=[list(s) for s in fib], f0_values=values,
               point_identified=len(values) == 1, pristine_claim_values=claim, empty_fiber=len(fib) == 0)
    record("MV-K1 joint", n_classes_mean_f0=len({(mean(s), f0(s)) for s in STATES}),
           n_multisets=len({multiset(s) for s in STATES}),
           note="(mean, f0) separates all 6 multisets ONLY for 2 parcels on a 3-point grid; not a general identity")

    kernels = {
        "MV-K2": ("Pop-III-sensitive yield g(0)=2, g(z>=1)=min(z+1,2)", step_kernel(lambda z: 2 if z == 0 else min(z + 1, 2))),
        "MV-K3": ("Z-blind saturating yield g(z)=min(z+1,2)", step_kernel(lambda z: min(z + 1, 2))),
        "MV-K4": ("sum-preserving mixing", mixing_kernel()),
    }
    for cid, (desc, P) in kernels.items():
        assert all(sum(row.values()) == 1 for row in P.values()), cid
        d_mean, w_mean = max_defect(P, mean)
        d_ms, _ = max_defect(P, multiset)
        record(cid, kernel=desc, mean_partition_defect=d_mean,
               mean_worst=None if w_mean is None else [w_mean[0], w_mean[1], list(w_mean[2]), list(w_mean[3])],
               multiset_partition_defect=d_ms)

    event = [3 * s[0] + s[1] for s in STATES if f0(s) > 0]
    union = all(len({f0(s) > 0 for s in STATES if mean(s) == m}) == 1 for m in {mean(s) for s in STATES})
    record("MV-K4 event", pristine_present_indices=event, union_of_mean_classes=union)
    return RESULTS


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, default=None)
    res = main()
    text = json.dumps(res, indent=1, ensure_ascii=False) + "\n"
    if ap.parse_args().output:
        ap.parse_args().output.write_text(text, encoding="utf-8")
    print(text)
