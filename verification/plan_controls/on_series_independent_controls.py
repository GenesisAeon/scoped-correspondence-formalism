"""Independent re-derivation of the organoid-network control groups ON-C01..ON-C23.

Part of package ON0 (ORGANOID_NETWORK_ROADMAP.md). Plan:
prompts/Answers/nicht_stationäre_Treiber/SCF_ORGANOID_NETWORK_IMPLEMENTATION_PLAN.md

Plan-arithmetic layer only: no SCF import, standard library only, written
from the plan text and hand derivations BEFORE reading the bundled
``independent_organoid_controls.py``. Exact Fractions where the statement is
rational; information quantities in bits as floats with stated tolerances.
Not a repository regression test (not named verify_*.py).

    python verification/plan_controls/on_series_independent_controls.py [--output FILE]

License: GPL-3.0-or-later.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
from fractions import Fraction as F
from pathlib import Path

RESULTS: dict[str, dict] = {}


def record(cid, **kw):
    RESULTS[cid] = {k: (str(v) if isinstance(v, F) else v) for k, v in kw.items()}


def H(ps):
    return -sum(float(p) * math.log2(float(p)) for p in ps if p > 0)


def mi(joint: dict) -> float:
    """I(A;B) for a joint {(a, b): p}."""
    pa, pb = {}, {}
    for (a, b), p in joint.items():
        pa[a] = pa.get(a, 0) + p
        pb[b] = pb.get(b, 0) + p
    return sum(float(p) * math.log2(float(p) / (float(pa[a]) * float(pb[b]))) for (a, b), p in joint.items() if p > 0)


def W(d):
    return [[1 + d, 1 - d], [1 - d, 1 + d]]


def apply(Wm, u):
    return tuple(sum(Wm[i][j] * u[j] for j in range(2)) for i in range(2))


def on_c01():
    d = F(1, 2)
    y0, y1 = apply(W(d), (1, 0)), apply(W(d), (0, 1))
    assert y0 == (F(3, 2), F(1, 2)) and y1 == (F(1, 2), F(3, 2)) and sum(y0) == sum(y1) == 2
    for dd in (F(0), F(1, 3), F(1)):
        Wm = W(dd)
        assert Wm[0][0] * Wm[1][1] - Wm[0][1] * Wm[1][0] == 4 * dd
    record("ON-C01", y0=list(map(str, y0)), y1=list(map(str, y1)), det="4 delta")


def on_c02():
    d = F(1, 2)
    full = {(s, apply(W(d), (1 - s, s))): F(1, 2) for s in (0, 1)}
    summ = {(s, sum(apply(W(d), (1 - s, s)))): F(1, 2) for s in (0, 1)}
    assert math.isclose(mi(full), 1.0) and mi(summ) == 0.0
    fibre = [s for s in (0, 1) if sum(apply(W(d), (1 - s, s))) == 2]
    assert fibre == [0, 1]
    zero = {(s, apply(W(F(0)), (1 - s, s))): F(1, 2) for s in (0, 1)}
    assert mi(zero) == 0.0
    record("ON-C02", I_full=1.0, I_sum=0.0, coarse_fibre=fibre)


def on_c03():
    d = F(1, 2)
    perm = {(s, tuple(reversed(apply(W(d), (1 - s, s))))): F(1, 2) for s in (0, 1)}
    assert math.isclose(mi(perm), 1.0)
    record("ON-C03", I_after_sensor_permutation=1.0)


def on_c04():
    d = s = 0.5
    A = 0.5 * (1 + math.erf(abs(d) / s))
    Phi = 0.5 * (1 + math.erf((math.sqrt(2) * abs(d) / s) / math.sqrt(2)))
    assert math.isclose(A, 0.9213503964748575, rel_tol=1e-15) and math.isclose(A, Phi, rel_tol=1e-15)
    # sigma = 0 limits stated explicitly
    record("ON-C04", A_star=A, sigma0_delta0=0.5, sigma0_delta_pos=1.0)


def on_c05():
    joint = {(0, 1): F(1, 2), (1, 0): F(1, 2)}  # BSC with eps = 1 (deterministic flip)
    assert math.isclose(mi(joint), 1.0)
    naive = sum(p for (s, y), p in joint.items() if s == y)
    optimal = sum(p for (s, y), p in joint.items() if s == 1 - y)
    assert naive == 0 and optimal == 1
    record("ON-C05", I=1.0, naive_accuracy=0, optimal_accuracy=1)


def on_c06():
    e = F(1, 4)
    bsc = {(0, 0): (1 - e) / 2, (0, 1): e / 2, (1, 1): (1 - e) / 2, (1, 0): e / 2}
    p = F(1, 2)  # Z channel: 0 -> 0 always, 1 -> 0 with p
    z = {(0, 0): F(1, 2), (1, 0): p / 2, (1, 1): (1 - p) / 2}
    acc_bsc = bsc[(0, 0)] + bsc[(1, 1)]
    acc_z = z[(0, 0)] + z[(1, 1)]
    assert acc_bsc == acc_z == F(3, 4)
    Ib, Iz = mi(bsc), mi(z)
    assert math.isclose(Ib, 1 - H([F(1, 4), F(3, 4)]), rel_tol=1e-12) and abs(Ib - 0.188722) < 1e-6
    assert abs(Iz - 0.311278) < 1e-6
    C = math.log2(1 + (1 - float(p)) * float(p) ** (float(p) / (1 - float(p))))
    assert math.isclose(C, math.log2(5 / 4), rel_tol=1e-12)
    # capacity also >= I at the uniform prior, by a direct prior scan
    best = max(mi({(0, 0): 1 - q, (1, 0): q * p, (1, 1): q * (1 - p)}) for q in [F(k, 400) for k in range(1, 400)])
    assert best <= C + 1e-9 and C - best < 1e-4
    record("ON-C06", accuracy="3/4 both", I_bsc=Ib, I_z=Iz, C_z=C)


def on_c07():
    joint = {(s, (s, n)): F(1, 4) for s in (0, 1) for n in (0, 1)}
    jz = {}
    for (s, (_, n)), q in joint.items():
        jz[(s, n)] = jz.get((s, n), 0) + q
    assert math.isclose(mi(joint), 1.0) and mi(jz) == 0.0
    record("ON-C07", I_SY=1.0, I_SZ=0.0)


def on_c08():
    joint = {(s, s ^ h): F(1, 4) for s in (0, 1) for h in (0, 1)}
    j2 = {}
    for (s, y), q in joint.items():
        j2[(s, y)] = j2.get((s, y), 0) + q
    cond = sum(F(1, 2) * mi({(s, s ^ h): F(1, 2) for s in (0, 1)}) for h in (0, 1))
    assert mi(j2) == 0.0 and math.isclose(cond, 1.0)
    record("ON-C08", I_SY=0.0, I_SY_given_H=1.0)


def on_c09():
    before = {(s, s): F(1, 2) for s in (0, 1)}
    after = {(s, 1 - s): F(1, 2) for s in (0, 1)}
    frozen = sum(q for (s, y), q in after.items() if y == s)
    refit = sum(q for (s, y), q in after.items() if y == 1 - s)
    assert math.isclose(mi(before), 1.0) and math.isclose(mi(after), 1.0) and frozen == 0 and refit == 1
    record("ON-C09", frozen_decoder=0, refitted_decoder=1, information_bits=1.0)


def on_c10():
    prior1 = F(9, 10)
    acc = prior1
    balanced = (F(1) + F(0)) / 2
    assert acc == F(9, 10) and balanced == F(1, 2)
    record("ON-C10", accuracy=acc, balanced_accuracy=balanced, information=0)


def on_c11():
    A = [[F(0), F(1, 2), F(0)], [F(1, 4), F(0), F(1, 4)], [F(0), F(1, 2), F(0)]]
    pre, post = [1, 0, 0], [0, 1, 0]
    eta, gamma = F(1, 2), F(1, 2)
    mask = [[int(i != j) for j in range(3)] for i in range(3)]
    G = [[mask[i][j] * post[i] * pre[j] for j in range(3)] for i in range(3)]
    At = [[(1 - eta) * A[i][j] + eta * G[i][j] for j in range(3)] for i in range(3)]
    assert At[1] == [F(5, 8), 0, F(1, 8)]
    An = [[gamma * At[i][j] / sum(At[i]) for j in range(3)] for i in range(3)]
    assert An[1] == [F(5, 12), 0, F(1, 12)] and all(sum(r) == F(1, 2) for r in An)
    record("ON-C11", row2=list(map(str, An[1])), row_sums="1/2")


def on_c12():
    A = [[F(0), F(1, 2)], [F(1, 3), F(1, 6)]]
    eta = F(0)
    G = [[F(7), F(0)], [F(0), F(9)]]
    At = [[(1 - eta) * A[i][j] + eta * G[i][j] for j in range(2)] for i in range(2)]
    assert At == A
    ell = gamma = F(1, 2)
    assert 1 - ell + ell * gamma == F(3, 4)
    record("ON-C12", eta0_preserves=True, contraction_bound="3/4")


def on_c13():
    pts = {(0, 0): 0, (1, 1): 0, (0, 1): 1, (1, 0): 1}
    best = 0
    rng = range(-3, 4)
    for a, b, c in itertools.product(rng, rng, rng):
        for sign in (1, -1):
            acc = sum(1 for (x, y), lab in pts.items() if (int(sign * (a * x + b * y + c) > 0)) == lab)
            best = max(best, acc)
    assert best == 3
    # proof sketch: positive class needs b + c > 0 and a + c > 0, negative c <= 0 and a + b + c <= 0;
    # adding the two positive inequalities gives a + b + 2c > 0, contradicting (a + b + c) + c <= 0.
    record("ON-C13", best_single_affine_accuracy=F(3, 4), xor_decoder_accuracy=1)


def on_c14():
    xor = {(r1, r2, r1 ^ r2): F(1, 4) for r1 in (0, 1) for r2 in (0, 1)}
    copy = {(s, s, s): F(1, 2) for s in (0, 1)}

    def sig(j):
        m1 = {}
        m2 = {}
        m12 = {}
        for (a, b, y), q in j.items():
            m1[(a, y)] = m1.get((a, y), 0) + q
            m2[(b, y)] = m2.get((b, y), 0) + q
            m12[((a, b), y)] = m12.get(((a, b), y), 0) + q
        return mi(m1), mi(m2), mi(m12)

    assert sig(xor) == (0.0, 0.0, 1.0) and tuple(round(x, 12) for x in sig(copy)) == (1.0, 1.0, 1.0)
    record("ON-C14", xor_signature=[0, 0, 1], xor_pid="synergy 1 bit", copy_signature=[1, 1, 1], copy_pid="redundancy 1 bit")


def on_c15():
    # U fair; A = (U, 0), B = (0, U). I(A^2 -> B^2) = I(A1; B1) + I(A1, A2; B2 | B1)
    joint = {((u, 0), (0, u)): F(1, 2) for u in (0, 1)}
    t1 = mi({(a[0], b[0]): q for (a, b), q in joint.items()})
    t2 = mi({(a, b[1]): q for (a, b), q in joint.items()})  # B1 constant -> conditioning trivial
    assert t1 == 0.0 and math.isclose(t1 + t2, 1.0)
    cond_on_U = 0.0  # given U, A and B are deterministic: no remaining information
    do_a1 = {u: (0, u) for u in (0, 1)}  # do(A1 = a) leaves B = (0, U)
    assert all(do_a1[u][1] == u for u in (0, 1))
    record("ON-C15", directed_information=1.0, given_U=cond_on_U, do_A1_changes_B2=False)


def on_c16():
    confounded = {(s, s): F(1, 2) for s in (0, 1)}  # block time == label
    randomised = {(s, t): F(1, 4) for s in (0, 1) for t in (0, 1)}
    assert math.isclose(mi(confounded), 1.0) and mi(randomised) == 0.0
    record("ON-C16", I_confounded=1.0, I_randomised=0.0)


def on_c17():
    vals = [F(v) for v in (0, 1, 2, 3, 4)]
    n = len(vals)
    m = sum(vals) / n
    s2 = sum((v - m) ** 2 for v in vals) / (n - 1)
    assert s2 / n == F(1, 2)
    pooled = [v for v in vals for _ in range(100)]
    N = len(pooled)
    mp = sum(pooled) / N
    s2p = sum((v - mp) ** 2 for v in pooled) / (N - 1)
    assert s2p / N == F(2, 499)
    record("ON-C17", group_SEM2=s2 / n, wrong_pooled_SEM2=s2p / N, assumption="preparation values 0..4")


def on_c18():
    d = [1, 1, 1, 1, 1]
    obs = abs(sum(d))
    flips = list(itertools.product((1, -1), repeat=5))
    p = F(sum(1 for f in flips if abs(sum(a * b for a, b in zip(f, d))) >= obs), len(flips))
    assert p == F(1, 16)
    record("ON-C18", p=p)


def on_c19():
    assert F(1, 4) - F(3, 20) == F(1, 10)
    record("ON-C19", group_difference=F(1, 10))


def on_c20():
    train, test = [F(0), F(2)], [F(100)]
    assert set(map(str, train)) & set(map(str, test)) == set()
    assert sum(train) / 2 == 1 and (sum(train) + sum(test)) / 3 == 34
    record("ON-C20", train_mean=1, leaked_mean=34)


def on_c21():
    def valid(row):
        return all(isinstance(x, (int, F)) or (isinstance(x, float) and math.isfinite(x)) for x in row) and \
            all(x >= 0 for x in row) and sum(row) == 1

    assert valid([F(1, 2), F(1, 2)]) and not valid([F(3, 2), F(-1, 2)]) and not valid([F(1, 2), F(1, 3)]) and not valid([float("nan"), 1.0])
    record("ON-C21", rejected=["negative", "not normalised", "non-finite"])


def adjacency(N, M, gamma, c):
    n = N // M
    mod = [i // n for i in range(N)]
    A = [[F(0)] * N for _ in range(N)]
    for i in range(N):
        for j in range(N):
            if i == j:
                continue
            if M == 1:
                A[i][j] = gamma / (N - 1)
            elif mod[i] == mod[j]:
                A[i][j] = gamma * (1 - c) / (n - 1)
            else:
                A[i][j] = gamma * c / (N - n)
    return A, mod


def on_c22():
    g = F(4, 5)
    for M in (1, 2, 3):
        A, mod = adjacency(12, M, g, F(1, 4))
        assert all(sum(r) == g for r in A)
        if M > 1:
            inter = [sum(A[i][j] for j in range(12) if mod[j] != mod[i]) for i in range(12)]
            assert all(x == F(1, 5) for x in inter)
    record("ON-C22", row_sum="4/5", inter_weight="1/5")


def on_c23():
    g = F(4, 5)
    A1, _ = adjacency(12, 1, g, None)
    A2, _ = adjacency(12, 2, g, F(6, 11))
    A3, _ = adjacency(12, 3, g, F(8, 11))
    assert A1 == A2 == A3 and A1[0][1] == F(4, 55)
    record("ON-C23", off_diagonal="4/55", identical=True)


CASES = [globals()[f"on_c{i:02d}"] for i in range(1, 24)]


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
    summary = {"passed": len(CASES) - len(failed), "total": len(CASES), "failed": failed, "results": RESULTS, "imports_scf": False}
    if args.output:
        args.output.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{summary['passed']}/{len(CASES)} ON control groups independently re-derived")
    for f in failed:
        print("FAIL", *f)
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
