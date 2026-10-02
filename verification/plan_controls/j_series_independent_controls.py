"""Independent re-derivation of the J-series control groups J-C01..J-C23.

Part of package J0 (SCOPE_COMPOSITION_EVIDENCE_ROADMAP.md). Plan:
prompts/Answers/nicht_stationäre_Treiber/SCF_SCOPE_COMPOSITION_EVIDENCE_IMPLEMENTATION_PLAN.md

This script is the plan's "independent plan arithmetic" layer (plan section
19.1), NOT a repository regression test: it imports nothing from SCF, uses
only the standard library (bool/int/Fraction), and was written from the plan
text before reading the plan's own `verify_plan_control_cases.py`. Where it
could, it deliberately uses a *different* algorithm than that bundle (e.g.
exact exponent-argument invariance instead of a float tolerance for J-C04,
exact polynomial integration for J-C14, active-path enumeration instead of
moralization for J-C23), so that agreement is evidence about the values and
not just about one shared implementation.

It is intentionally not named verify_*.py, so the repository suite runner
does not pick it up as a production check.

Usage:
    python verification/plan_controls/j_series_independent_controls.py \
        [--output verification/plan_controls/j_series_independent_controls_results.json]

License: GPL-3.0-or-later (same as the repository source code).
"""
from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from itertools import product
from pathlib import Path

RESULTS: dict[str, dict] = {}


def record(case_id: str, **values) -> None:
    RESULTS[case_id] = {k: _jsonable(v) for k, v in values.items()}


def _jsonable(v):
    if isinstance(v, F):
        return str(v)
    if isinstance(v, (list, tuple)):
        return [_jsonable(x) for x in v]
    if isinstance(v, dict):
        return {str(k): _jsonable(x) for k, x in v.items()}
    return v


# ---------------------------------------------------------------- helpers ---

def rank(rows: list[list[F]]) -> int:
    m = [[F(x) for x in r] for r in rows]
    r = 0
    ncols = len(m[0]) if m else 0
    for c in range(ncols):
        piv = next((i for i in range(r, len(m)) if m[i][c] != 0), None)
        if piv is None:
            continue
        m[r], m[piv] = m[piv], m[r]
        for i in range(len(m)):
            if i != r and m[i][c] != 0:
                f = m[i][c] / m[r][c]
                m[i] = [a - f * b for a, b in zip(m[i], m[r])]
        r += 1
    return r


def matvec_zero(rows, v) -> bool:
    return all(sum(F(a) * F(b) for a, b in zip(row, v)) == 0 for row in rows)


def matmul(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(len(b))) for j in range(len(b[0]))] for i in range(len(a))]


def weighted_quantile(scores, cal_weights, test_weight, alpha):
    """Smallest r with cumulative normalized mass >= 1-alpha, where the test
    point contributes mass test_weight at +infinity. Returns None for +inf."""
    total = sum(cal_weights) + test_weight
    need = (1 - alpha) * total
    cum = F(0)
    for s, w in sorted(zip(scores, cal_weights)):
        cum += w
        if cum >= need:
            return s
    return None


def tv(p: dict, q: dict) -> F:
    return sum(abs(p.get(k, F(0)) - q.get(k, F(0))) for k in set(p) | set(q)) / 2


# ------------------------------------------------------------------ J1 ---

def j_c01():
    d = [F(-1), F(0), F(1), F(2)]
    n = len(d)
    mean = sum(d) / n
    dev = [x - mean for x in d]
    g = [sum(dev[t] * dev[t - l] for t in range(l, n)) / n for l in range(2)]
    L = 1
    V = g[0] + 2 * sum((1 - F(l, L + 1)) * g[l] for l in range(1, L + 1))
    var_mean = V / n
    se = F(5, 8)
    assert se * se == var_mean and se > 0  # exact square root check
    dm = mean / se
    assert (mean, g[0], g[1], V, se, dm) == (F(1, 2), F(5, 4), F(5, 16), F(25, 16), F(5, 8), F(4, 5))
    # sign flip under model swap, invariance under positive loss scaling
    neg = [-x for x in d]
    m2 = sum(neg) / n
    assert m2 / se == -dm
    scaled = [3 * x for x in d]
    ms = sum(scaled) / n
    devs = [x - ms for x in scaled]
    g0s = sum(x * x for x in devs) / n
    g1s = sum(devs[t] * devs[t - 1] for t in range(1, n)) / n
    Vs = g0s + g1s
    assert Vs == 9 * V  # se scales by 3, DM unchanged
    record("J-C01", mean=mean, gamma0=g[0], gamma1=g[1], V=V, se=se, dm=dm,
           note="arithmetic only; n=4 does not justify the asymptotic reference")


def j_c02():
    raw = [F(1, 100), F(4, 100), F(3, 100)]
    m = len(raw)
    order = sorted(range(m), key=lambda i: raw[i])
    adj = [F(0)] * m
    running = F(0)
    for rank_i, i in enumerate(order):
        running = max(running, min(F(1), (m - rank_i) * raw[i]))
        adj[i] = running
    assert adj == [F(3, 100), F(6, 100), F(6, 100)]
    record("J-C02", holm_adjusted_in_original_order=adj)


# ------------------------------------------------------------------ J2 ---

def j_c03():
    # columns T, l, g ; rows L, Time
    D = [[0, 1, 1], [1, 0, -2]]
    assert rank(D) == 2
    v = [2, -1, 1]
    assert matvec_zero(D, v)
    assert 3 - rank(D) == 1
    # basis-change invariance: any nonzero multiple is equally valid
    assert matvec_zero(D, [-4, 2, -2])
    # dims as (M, L, T): g = L T^-2 ; G = M^-1 L^3 T^-2
    g_dim, G_dim = (0, 1, -2), (-1, 3, -2)
    g_over_G = tuple(a - b for a, b in zip(g_dim, G_dim))
    assert g_over_G == (1, -2, 0)
    record("J-C03", rank=2, nullity=1, pi_exponents_T_l_g=v, g_over_G_MLT=list(g_over_G))


def j_c04():
    # M(t) = q/k + (M0 - q/k) exp(-k t). The solution is identical iff the
    # equilibrium q/k and the exponent argument k*t are identical; checked
    # exactly in Fraction, so no float tolerance is needed.
    M0, qy, ky, ty = F(3), F(5), F(2), F(2, 5)
    qd, kd, td = qy / 365, ky / 365, ty * 365
    assert qy / ky == qd / kd == F(5, 2)
    assert ky * ty == kd * td == F(4, 5)
    # halo reparametrization rho' = rho/lambda, r' = lambda r preserves rho*r.
    # The plan text (section 8) gives no numbers; the register value 12 uses
    # rho=6, r=2, lambda=3 from the plan's bundled script.
    rho, r, lam = F(6), F(2), F(3)
    assert (rho / lam) * (lam * r) == rho * r == 12
    # negative control: a different observable, e.g. rho*r^2, is NOT preserved
    assert (rho / lam) * (lam * r) ** 2 != rho * r ** 2
    record("J-C04", equilibrium=qy / ky, exponent_argument=ky * ty, M0=M0, rho_times_r=rho * r,
           arithmetic="exact Fraction on q/k and k*t (stronger than a float identity check)",
           plan_gap="rho, r, lambda are not stated in plan section 8; taken from bundle")


# ------------------------------------------------------------------ J4 ---

def j_c05():
    # T1(x)=2x, D1=D2=[0,1]; preimage of D2 under T1 is [0,1/2]
    D1 = (F(0), F(1))
    pre = (F(0) / 2, F(1) / 2)
    D12 = (max(D1[0], pre[0]), min(D1[1], pre[1]))
    assert D12 == (F(0), F(1, 2))
    x = F(3, 4)
    assert D1[0] <= x <= D1[1] and not (F(0) <= 2 * x <= F(1))
    record("J-C05", composite_domain=list(D12), witness_x=x, T1_of_witness=2 * x)


def j_c06():
    # linear 1-D fields f(x)=lam*x, maps T(x)=t*x: DT f = a (f o T) <=> t*lamA = a*lamB*t
    lamA, lamB, lamC, t1, t2 = F(-1), F(-2), F(-4), F(2), F(3)
    a1 = (t1 * lamA) / (lamB * t1)
    a2 = (t2 * lamB) / (lamC * t2)
    assert (a1, a2) == (F(1, 2), F(1, 2))
    t12 = t1 * t2
    a12 = (t12 * lamA) / (lamC * t12)
    assert a12 == a1 * a2 == F(1, 4)
    H1, H2 = F(4), F(1)
    H12 = min(H1, H2 / a1)
    assert H12 == 2
    record("J-C06", c1=a1, c2=a2, composite_time_factor=a12, horizon=H12)


def j_c07():
    L2, d1, d2 = F(3), F(1, 10), F(1, 5)
    flow = L2 * d1 + d2
    assert flow == F(1, 2)
    # vector-field residuals, coefficients of (const, x)
    fA = lambda x: x
    fB = lambda y: F(0)
    fC = lambda z: F(-1)
    T1 = lambda x: 2 * x
    T2 = lambda y: 3 * y
    a1, a2 = F(2), F(3)
    r1 = lambda x: 2 * fA(x) - a1 * fB(T1(x))
    r2 = lambda y: 3 * fB(y) - a2 * fC(T2(y))
    r12_formula = lambda x: 3 * r1(x) + a1 * r2(T1(x))
    r12_direct = lambda x: 6 * fA(x) - (a1 * a2) * fC(T2(T1(x)))
    for x in [F(0), F(1, 4), F(1, 2), F(-7, 3)]:
        assert r12_formula(x) == r12_direct(x) == 6 * x + 6
    M, eps1, A, eps2 = F(3), max(abs(r1(F(0))), abs(r1(F(1, 2)))), abs(a1), F(3)
    bound = M * eps1 + A * eps2
    assert bound == 9 and r12_direct(F(1, 2)) == 9 and r12_direct(F(1, 4)) == F(15, 2)
    record("J-C07", flow_bound=flow, field_bound=bound, residual_at_quarter=r12_direct(F(1, 4)),
           bound_attained_at=F(1, 2))


def j_c08():
    spec = ((F(0), F(1)), F(1, 5))
    impl = ((F(-1), F(2)), F(1, 10))

    def refines(i, s):
        (il, iu), ie = i
        (sl, su), se = s
        return il <= sl and su <= iu and ie <= se

    assert refines(impl, spec) and not refines(spec, impl)
    record("J-C08", impl_refines_spec=True, spec_refines_impl=False)


# ------------------------------------------------------------------ J5 ---

def imul(a, b):
    ps = [a[0] * b[0], a[0] * b[1], a[1] * b[0], a[1] * b[1]]
    return (min(ps), max(ps))


def j_c09():
    uppers = []
    for i in range(64):
        x = (F(i, 64), F(i + 1, 64))
        one_minus = (1 - x[1], 1 - x[0])
        uppers.append(imul(x, one_minus)[1])
    top = max(uppers)
    assert top == F(33, 128)
    assert top <= F(13, 50)
    p = lambda x: x * (1 - x)
    assert p(F(1, 2)) == F(1, 4) > F(6, 25)
    assert p(F(0)) == p(F(1)) == 0
    record("J-C09", max_natural_upper_64=top, proves_le=F(13, 50), refutes_le=F(6, 25),
           counterexample_x=F(1, 2), true_max=F(1, 4))


def j_c10():
    x = (F(0), F(1))
    diff = (x[0] - x[1], x[1] - x[0])
    assert diff == (F(-1), F(1))
    y = (F(-1), F(1))
    reciprocal_defined = not (y[0] <= 0 <= y[1])
    assert reciprocal_defined is False
    record("J-C10", natural_x_minus_x=list(diff), reciprocal_on_minus1_1="undefined: 0 in denominator box")


# ------------------------------------------------------------------ J6 ---

def j_c11():
    A = [[1, 1], [2, 2]]
    assert rank(A) == 1 and matvec_zero(A, [1, -1])
    # c^T theta identifiable iff c in row space: (1,1) yes, (1,0) no
    assert rank(A + [[1, 1]]) == 1 and rank(A + [[1, 0]]) == 2
    record("J-C11", rank=1, nullvector=[1, -1], identifiable=["theta1+theta2"], not_identifiable=["theta1"])


def j_c12():
    k, c, x0, lam = F(2), F(3), F(5), F(7)
    y0, dy0 = c * x0, -k * c * x0
    assert (y0, dy0) == (15, -30) and -dy0 / y0 == k
    c2, x02 = c / lam, lam * x0
    assert (c2, x02) == (F(3, 7), F(35)) and c2 * x02 == y0 and -k * c2 * x02 == dy0
    record("J-C12", y0=y0, dy0=dy0, k=k, product=c * x0, transformed=[c2, x02])


def j_c13():
    fiber = [t for t in (F(-2), F(2)) if t * t == 4]
    assert fiber == [F(-2), F(2)]
    # theta^2 - 4 has degree 2, so these are all real roots
    assert 2 * F(2) == 4  # derivative nonzero -> local injectivity at 2
    assert [t for t in fiber if t > 0] == [F(2)]
    record("J-C13", fiber=fiber, derivative_at_2=4, positive_restriction=[F(2)])


# ------------------------------------------------------------------ J7 ---
# polynomials in (x, y) as {(i, j): coeff}; X, Y independent U[0,1]

def pmul(p, q):
    out = {}
    for (i, j), a in p.items():
        for (k, l), b in q.items():
            out[(i + k, j + l)] = out.get((i + k, j + l), F(0)) + a * b
    return out


def integrate(p, var):
    out = {}
    for (i, j), a in p.items():
        if var == "x":
            key, val = (0, j), a / (i + 1)
        else:
            key, val = (i, 0), a / (j + 1)
        out[key] = out.get(key, F(0)) + val
    return out


def expect(p):
    return integrate(integrate(p, "x"), "y").get((0, 0), F(0))


def var(p):
    return expect(pmul(p, p)) - expect(p) ** 2


def sobol(p):
    V = var(p)
    g_x = integrate(p, "y")  # E[f | X]
    g_y = integrate(p, "x")  # E[f | Y]
    S = (var(g_x) / V, var(g_y) / V)
    ST = (1 - var(g_y) / V, 1 - var(g_x) / V)
    return V, S, ST


def j_c14():
    V, S, ST = sobol({(1, 0): F(1), (0, 1): F(2)})
    assert (V, S, ST) == (F(5, 12), (F(1, 5), F(4, 5)), (F(1, 5), F(4, 5)))
    V2, S2, ST2 = sobol({(1, 1): F(1)})
    assert (V2, S2, ST2) == (F(7, 144), (F(3, 7), F(3, 7)), (F(4, 7), F(4, 7)))
    assert 1 - sum(S2) == F(1, 7)
    assert var({(0, 0): F(5)}) == 0  # constant output: indices undefined
    record("J-C14", additive=dict(V=V, S=list(S), ST=list(ST)),
           product=dict(V=V2, S=list(S2), ST=list(ST2), interaction=F(1, 7)),
           constant_output_variance=0)


# ------------------------------------------------------------------ J8 ---

def j_c15():
    s = [F(1), F(2), F(3)]
    q1 = weighted_quantile(s, [F(1)] * 3, F(1), F(1, 4))
    q2 = weighted_quantile(s, [F(1)] * 3, F(4), F(1, 4))
    q3 = weighted_quantile(s, [F(1), F(2), F(1)], F(1), F(2, 5))
    assert (q1, q2, q3) == (F(3), None, F(2))
    # mutant: dropping the test-point mass at +inf changes case 2
    assert weighted_quantile(s, [F(1)] * 3, F(0), F(1, 4)) == F(3)
    # common positive scaling changes nothing
    assert weighted_quantile(s, [F(7)] * 3, F(28), F(1, 4)) is None
    record("J-C15", quantiles=["3", "+inf", "2"])


def j_c16():
    P = {0: F(9, 10), 1: F(1, 10)}
    Q = {0: F(1, 10), 1: F(9, 10)}
    w = {x: Q[x] / P[x] for x in P}
    assert w == {0: F(1, 9), 1: F(9)}
    alpha = F(1, 5)
    tot = cov_u = cov_w = unb = F(0)
    for bits in product((0, 1), repeat=5):
        cal, tgt = bits[:4], bits[4]
        pr = Q[tgt]
        for x in cal:
            pr *= P[x]
        tot += pr
        # residual = |Y - 0| = X
        qu = weighted_quantile(list(cal), [F(1)] * 4, F(1), alpha)
        qw = weighted_quantile(list(cal), [w[x] for x in cal], w[tgt], alpha)
        cov_u += pr * (qu is None or tgt <= qu)
        cov_w += pr * (qw is None or tgt <= qw)
        unb += pr * (qw is None)
    assert tot == 1
    assert cov_u == F(40951, 100000) and cov_w == 1 and unb == F(89991, 100000)
    record("J-C16", unweighted_coverage=cov_u, weighted_coverage=cov_w, prob_unbounded=unb,
           cases_enumerated=32)


def j_c17():
    q = weighted_quantile([F(0)] * 4, [F(1)] * 4, F(1), F(1, 5))
    assert q == 0 and not (F(1) <= q)
    record("J-C17", quantile=q, coverage=0, reason="concept shift violates P(Y|X)=Q(Y|X)")


# ---------------------------------------------------------------- J9 ---

def dist(exo: dict, f):
    out = {}
    for u, p in exo.items():
        k = f(u)
        out[k] = out.get(k, F(0)) + p
    return out


def j_c18():
    fair = {0: F(1, 2), 1: F(1, 2)}
    obs1 = dist(fair, lambda u: (u, u))          # X=U, Y=X
    obs2 = dist(fair, lambda u: (u, u))          # X=U, Y=U
    assert obs1 == obs2
    do1 = dist(fair, lambda u: 1)                # Y under do(X=1), model 1
    do2 = dist(fair, lambda u: u)                # model 2
    assert do1 == {1: F(1)} and do2 == fair and tv(do1, do2) == F(1, 2)
    record("J-C18", observational_equal=True, p_y1_do_x1=[do1.get(1), do2.get(1)], tv=tv(do1, do2))


def j_c19():
    exo = {(u1, u2): F(1, 4) for u1, u2 in product((0, 1), repeat=2)}

    def micro(do: dict):
        def f(u):
            x1 = do.get("X1", u[0])
            x2 = do.get("X2", u[1])
            return (x1, x2, x1 ^ x2)
        return dist(exo, f)

    tau = lambda s: (s[0] ^ s[1], s[2])
    fairZ = {0: F(1, 2), 1: F(1, 2)}

    def macro(do: dict):
        return dist(fairZ, lambda z: (do.get("Z", z), do.get("Z", z)))

    def push(d):
        return dist(d, tau)

    interventions = [{}] + [{"X1": a, "X2": b} for a, b in product((0, 1), repeat=2)]
    omega = {0: {}}
    for idx, i in enumerate(interventions[1:], start=1):
        omega[idx] = {"Z": i["X1"] ^ i["X2"]}
    for idx, i in enumerate(interventions):
        assert push(micro(i)) == macro(omega[idx])
    assert {tuple(sorted(v.items())) for v in omega.values()} == {(), (("Z", 0),), (("Z", 1),)}  # surjective

    def leq(i, j):  # j extends i
        return all(k in j and j[k] == v for k, v in i.items())

    def order_preserving(ints, om):
        return all(leq(om[a], om[b]) for a in range(len(ints)) for b in range(len(ints)) if leq(ints[a], ints[b]))

    assert order_preserving(interventions, omega)

    ext = interventions + [{"X1": 1}]
    om_bad = dict(omega)
    om_bad[len(ext) - 1] = {"Z": 1}
    d_tv = tv(push(micro({"X1": 1})), macro({"Z": 1}))
    assert d_tv == F(1, 2)
    # finding beyond the plan text: the declared extension ALSO violates order preservation
    assert not order_preserving(ext, om_bad)
    # and a different image (no-op) passes both checks -> not every mapping fails
    om_alt = dict(omega)
    om_alt[len(ext) - 1] = {}
    assert push(micro({"X1": 1})) == macro({}) and order_preserving(ext, om_alt)
    record("J-C19", exact_interventions=5, surjective=True, order_preserving=True,
           extension_tv=d_tv, extension_order_preserving=False,
           alternative_image_noop_passes=True)


# ---------------------------------------------------------------- J10 ---

def j_c20():
    for pz1, expect0, expect1 in ((F(1, 2), F(1, 2), F(1, 2)), (F(3, 4), F(3, 4), F(1, 4))):
        Z = {0: 1 - pz1, 1: pz1}
        p_y1 = [sum(p for z, p in Z.items() if (x ^ z) == 1) for x in (0, 1)]
        assert p_y1 == [expect0, expect1]
    # standardization: source P(Y|do(x),z) is deterministic x^z; reweight by target Q(z)
    Qz = {0: F(1, 4), 1: F(3, 4)}
    std = [sum(Qz[z] * (1 if (x ^ z) == 1 else 0) for z in (0, 1)) for x in (0, 1)]
    assert std == [F(3, 4), F(1, 4)] and std[1] - std[0] == F(-1, 2)
    # negative support control: source without z=1 cannot supply P(Y|do(x),Z=1)
    source_support = {0}
    assert not set(Qz) <= source_support
    record("J-C20", source=[F(1, 2), F(1, 2)], target=std, target_effect=F(-1, 2))


def j_c21():
    fair = {0: F(1, 2), 1: F(1, 2)}
    src_obs = dist(fair, lambda u: (u, u))
    src_do = {x: dist(fair, lambda u, x=x: (x, x)) for x in (0, 1)}  # Y=X in source for both families
    fam = {
        1: dict(tgt_obs=dist(fair, lambda u: (u, u)), tgt_do1=dist(fair, lambda u: 1)),
        2: dict(tgt_obs=dist(fair, lambda u: (u, u)), tgt_do1=dist(fair, lambda u: u)),
    }
    assert fam[1]["tgt_obs"] == fam[2]["tgt_obs"]
    assert src_obs == {(0, 0): F(1, 2), (1, 1): F(1, 2)} and all(src_do[x] == {(x, x): F(1)} for x in (0, 1))
    v1, v2 = fam[1]["tgt_do1"].get(1, F(0)), fam[2]["tgt_do1"].get(1, F(0))
    assert (v1, v2) == (F(1), F(1, 2))
    record("J-C21", target_value=[v1, v2], all_available_info_equal=True)


def active_path_exists(edges, a, b, given):
    """d-connection via explicit enumeration of simple undirected paths
    (a different algorithm from moralization or Bayes-ball)."""
    given = set(given)
    children = {}
    parents = {}
    for u, v in edges:
        children.setdefault(u, set()).add(v)
        parents.setdefault(v, set()).add(u)

    def desc(n):
        seen, stack = set(), [n]
        while stack:
            for c in children.get(stack.pop(), ()):
                if c not in seen:
                    seen.add(c)
                    stack.append(c)
        return seen

    nbrs = {}
    for u, v in edges:
        nbrs.setdefault(u, set()).add(v)
        nbrs.setdefault(v, set()).add(u)

    def paths(cur, path):
        if cur == b:
            yield path
            return
        for n in nbrs.get(cur, ()):
            if n not in path:
                yield from paths(n, path + [n])

    for p in paths(a, [a]):
        ok = True
        for i in range(1, len(p) - 1):
            prev, mid, nxt = p[i - 1], p[i], p[i + 1]
            collider = mid in children.get(prev, ()) and mid in children.get(nxt, ())
            if collider:
                if not (mid in given or desc(mid) & given):
                    ok = False
                    break
            elif mid in given:
                ok = False
                break
        if ok:
            return True
    return False


def j_c23():
    col = [("A", "C"), ("B", "C"), ("C", "D")]
    assert not active_path_exists(col, "A", "B", [])
    assert active_path_exists(col, "A", "B", ["C"])
    assert active_path_exists(col, "A", "B", ["D"])
    sel = [("S", "Z"), ("Z", "Y"), ("X", "Y")]
    # G_{bar X}: remove edges INTO X (there are none here)
    g_bar_x = [(u, v) for u, v in sel if v != "X"]
    assert not active_path_exists(g_bar_x, "S", "Y", ["X", "Z"])
    assert active_path_exists(g_bar_x, "S", "Y", ["X"])
    record("J-C23", collider_marginal_separated=True, conditioning_on_C_opens=True,
           conditioning_on_D_opens=True, S_sep_Y_given_XZ=True, S_sep_Y_given_X=False)


# ---------------------------------------------------------------- J11 ---

def j_c22():
    P = [[F(4, 5), F(1, 5)], [F(1, 10), F(9, 10)]]
    Q = [[F(7, 10), F(3, 10)], [F(1, 5), F(4, 5)]]
    assert all(sum(r) == 1 for r in P + Q)
    p0 = [[F(1), F(0)]]
    inf_norm = max(sum(abs(Q[i][j] - P[i][j]) for j in range(2)) for i in range(2))
    p2 = matmul(matmul(p0, P), P)[0]
    q2 = matmul(matmul(p0, Q), Q)[0]
    l1 = sum(abs(a - b) for a, b in zip(p2, q2))
    k = 2
    bound = F(0) + k * inf_norm  # initial error 0, lifting = identity
    assert inf_norm == F(1, 5) and p2 == [F(33, 50), F(17, 50)] and q2 == [F(11, 20), F(9, 20)]
    assert l1 == F(11, 50) and bound == F(2, 5) and l1 <= bound
    assert l1 / 2 == F(11, 100) and bound / 2 == F(1, 5)
    record("J-C22", inf_norm=inf_norm, p0P2=p2, p0Q2=q2, l1=l1, l1_bound=bound, tv=l1 / 2, tv_bound=bound / 2)


CASES = [j_c01, j_c02, j_c03, j_c04, j_c05, j_c06, j_c07, j_c08, j_c09, j_c10, j_c11, j_c12,
         j_c13, j_c14, j_c15, j_c16, j_c17, j_c18, j_c19, j_c20, j_c21, j_c22, j_c23]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, default=None)
    args = ap.parse_args()
    failed = []
    for case in CASES:
        try:
            case()
        except AssertionError as exc:
            failed.append((case.__name__, repr(exc)))
    passed = len(CASES) - len(failed)
    summary = {"passed": passed, "total": len(CASES), "failed": failed, "results": RESULTS,
               "imports_scf": False}
    if args.output:
        args.output.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{passed}/{len(CASES)} J-series control groups independently re-derived")
    for name, err in failed:
        print("FAIL", name, err)
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
