"""Information decomposition core (F09 port + F12 TWO_BIT_COPY / Blackwell).

1:1 port of verification/verify_pid_rb.py PID / RB / EI_q API, plus Blackwell
RB(0) for finite non-binary Y via scipy.optimize.linprog (F12).
Mapping: pid_redundancy_bottleneck.md / F12.

Williams-Beer I_min atoms as basis; Kolchinsky RB(0)=Blackwell redundancy as modern
redundancy measure. NOT Rosas O-information as main metric. EI_q reported beside
PID never equated to Syn. Canonical (sources, target): micro -> macro.

Primary sources:
  arXiv:1004.2515  Williams & Beer
  arXiv:2405.07665 Kolchinsky (PMC11276267); ref impl ideas: github.com/artemyk/pid-as-ib
  Harder, Salge & Polani (2013) — TWO_BIT_COPY counterexample for I_min
"""
from __future__ import annotations

import itertools
import math

import numpy as np

try:
    from scipy.optimize import linprog, minimize

    HAS_SCIPY = True
except ImportError:  # pragma: no cover
    HAS_SCIPY = False
    linprog = minimize = None


ARXIV_WB = "https://arxiv.org/abs/1004.2515"
ARXIV_RB = "https://arxiv.org/abs/2405.07665"
TOL = 1e-9


def require(ok, msg):
    if not bool(ok):
        raise AssertionError(msg)


def near(a, b, atol=1e-8, rtol=1e-7):
    if not np.allclose(a, b, atol=atol, rtol=rtol):
        raise AssertionError(f"{a!r} != {b!r}")


def entropy(p):
    p = np.asarray(p, dtype=float).ravel()
    p = p[p > 0]
    return float(-np.sum(p * np.log2(p)))


def mi_xy(joint):
    """I(X;Y) from joint p(x,y)."""
    joint = np.asarray(joint, dtype=float)
    joint = joint / joint.sum()
    px = joint.sum(axis=1)
    py = joint.sum(axis=0)
    total = 0.0
    for i, j in np.ndindex(joint.shape):
        if joint[i, j] > 0 and px[i] > 0 and py[j] > 0:
            total += joint[i, j] * math.log2(joint[i, j] / (px[i] * py[j]))
    return float(total)


def specific_info(y_val, p_xy, axis_x=0):
    """I(Y=y; X) = D_KL(p(x|y) || p(x))."""
    joint = np.asarray(p_xy, dtype=float)
    joint = joint / joint.sum()
    if axis_x == 0:
        py = joint.sum(axis=0)
        px = joint.sum(axis=1)
        if py[y_val] <= 0:
            return 0.0
        px_given_y = joint[:, y_val] / py[y_val]
    else:
        py = joint.sum(axis=1)
        px = joint.sum(axis=0)
        if py[y_val] <= 0:
            return 0.0
        px_given_y = joint[y_val, :] / py[y_val]
    total = 0.0
    for i, p in enumerate(px_given_y):
        if p > 0 and px[i] > 0:
            total += p * math.log2(p / px[i])
    return float(total)


def i_min_two_sources(p_r1ys, p_r2ys, p_y):
    """I_min(Y; {R1}{R2}) = sum_y p(y) min(I(Y=y;R1), I(Y=y;R2))."""
    total = 0.0
    for y, py in enumerate(p_y):
        if py <= 0:
            continue
        i1 = specific_info(y, p_r1ys)
        i2 = specific_info(y, p_r2ys)
        total += py * min(i1, i2)
    return float(total)


def joint_from_samples(r1, r2, y, n1=None, n2=None, ny=None):
    r1 = np.asarray(r1, dtype=int)
    r2 = np.asarray(r2, dtype=int)
    y = np.asarray(y, dtype=int)
    n1 = int(r1.max()) + 1 if n1 is None else n1
    n2 = int(r2.max()) + 1 if n2 is None else n2
    ny = int(y.max()) + 1 if ny is None else ny
    joint = np.zeros((n1, n2, ny), dtype=float)
    for a, b, c in zip(r1, r2, y):
        joint[a, b, c] += 1.0
    joint /= joint.sum()
    return joint


def pid_atoms_williams_beer(joint_r1r2y):
    """Williams-Beer I_min PID for two sources.

    joint shape (n1, n2, ny) = p(r1, r2, y).
    Returns Red, Unq1, Unq2, Syn, I_joint.
    """
    j = np.asarray(joint_r1r2y, dtype=float)
    j = j / j.sum()
    n1, n2, ny = j.shape
    p_y = j.sum(axis=(0, 1))
    p_r1y = j.sum(axis=1)
    p_r2y = j.sum(axis=0)
    i_r1 = mi_xy(p_r1y)
    i_r2 = mi_xy(p_r2y)
    flat = j.reshape(n1 * n2, ny)
    i_joint = mi_xy(flat)
    red = i_min_two_sources(p_r1y, p_r2y, p_y)
    unq1 = i_r1 - red
    unq2 = i_r2 - red
    syn = i_joint - unq1 - unq2 - red
    return {
        "Red": float(red),
        "Unq1": float(unq1),
        "Unq2": float(unq2),
        "Syn": float(syn),
        "I_joint": float(i_joint),
        "I_R1": float(i_r1),
        "I_R2": float(i_r2),
        "measure": "williams_beer_I_min",
    }


def assert_nonnegative_atoms(atoms, atol=1e-8):
    for k in ("Red", "Unq1", "Unq2", "Syn"):
        require(atoms[k] >= -atol, f"{k} negative: {atoms[k]}")
    near(
        atoms["Red"] + atoms["Unq1"] + atoms["Unq2"] + atoms["Syn"],
        atoms["I_joint"],
        atol=1e-7,
    )
    return True


def ei_q_channel(P, q):
    """EI_q(P)=I_q(Z_t; Z_{t+1}) for row-stochastic P and input q."""
    P = np.asarray(P, dtype=float)
    q = np.asarray(q, dtype=float)
    q = q / q.sum()
    near(P.sum(axis=1), np.ones(len(P)))
    out = q @ P
    total = 0.0
    for i in range(len(q)):
        for j in range(P.shape[1]):
            if q[i] > 0 and P[i, j] > 0 and out[j] > 0:
                total += q[i] * P[i, j] * math.log2(P[i, j] / out[j])
    return float(total)


def compare_to_EI_q(channel, q, sources_target_joint):
    """Report EI_q beside PID; never equate Syn=EI."""
    atoms = pid_atoms_williams_beer(sources_target_joint)
    ei = ei_q_channel(channel, q)
    return {
        "EI_q": ei,
        "pid_summary": {k: atoms[k] for k in ("Red", "Unq1", "Unq2", "Syn", "I_joint")},
        "claim": "EI_q reported beside PID; Syn is not identified with EI_q",
    }


def blackwell_redundancy_binary_y(joints_sy):
    """Exact Blackwell I_cap for sources with binary Y via posterior intersection.

    For each source s, collect posterior p(Y=1|x) values. A Q ⪯_Y X_s requires
    that every posterior of Q lies in conv{posteriors of X_s}. Intersection of
    convex hulls of source posteriors yields feasible Q-posteriors; maximise I(Q;Y)
    over distributions supported on that intersection (binary Y: endpoints suffice).
    """
    intervals = []
    py_global = None
    for j in joints_sy:
        j = np.asarray(j, dtype=float)
        j = j / j.sum()
        py = j.sum(axis=0)
        if py_global is None:
            py_global = py
        px = j.sum(axis=1)
        posts = []
        for x in range(j.shape[0]):
            if px[x] <= 0:
                continue
            posts.append(j[x, 1] / px[x])
        lo, hi = min(posts), max(posts)
        intervals.append((lo, hi))
    lo = max(a for a, _ in intervals)
    hi = min(b for _, b in intervals)
    if lo > hi + 1e-12:
        return 0.0
    py1 = float(py_global[1])
    candidates = []
    for p0, p1 in ((lo, hi), (lo, lo), (hi, hi)):
        if abs(p1 - p0) < 1e-15:
            candidates.append(0.0)
            continue
        w = (py1 - p1) / (p0 - p1)
        if w < -1e-9 or w > 1 + 1e-9:
            continue
        w = min(max(w, 0.0), 1.0)
        hy = entropy(py_global)
        hy_q = w * _bin_ent(p0) + (1 - w) * _bin_ent(p1)
        candidates.append(hy - hy_q)
    candidates.append(0.0)
    return float(max(candidates))


def _bin_ent(p):
    p = min(max(float(p), 0.0), 1.0)
    if p <= 0 or p >= 1:
        return 0.0
    return float(-(p * math.log2(p) + (1 - p) * math.log2(1 - p)))


def _source_posteriors(joint_sy):
    """Return list of p(Y|x) rows for positive-mass x; and p(Y)."""
    j = np.asarray(joint_sy, dtype=float)
    j = j / j.sum()
    py = j.sum(axis=0)
    px = j.sum(axis=1)
    posts = []
    for x in range(j.shape[0]):
        if px[x] <= TOL:
            continue
        posts.append(j[x, :] / px[x])
    return posts, py


def _point_in_all_hulls_lp(posts_per_source, direction=None):
    """Solve LP: extremize direction·q (or find any) over q in ∩_s conv(posts_s).

    Variables: q[0..m-1], and for each source s mixing weights λ_s[x].
    Returns optimal q or None if infeasible.
    """
    require(HAS_SCIPY, "scipy.optimize.linprog required for non-binary Blackwell RB(0)")
    m = len(posts_per_source[0][0])
    # layout: [q_0..q_{m-1}] + concat_s λ_s
    n_lambda = sum(len(posts) for posts in posts_per_source)
    n = m + n_lambda
    if direction is None:
        c = np.zeros(n)
    else:
        c = np.zeros(n)
        c[:m] = -np.asarray(direction, dtype=float)  # maximise direction·q
    # equality: sum q = 1; for each source s: q = λ_s @ Posts_s; sum λ_s = 1
    A_eq = []
    b_eq = []
    # sum q = 1
    row = np.zeros(n)
    row[:m] = 1.0
    A_eq.append(row)
    b_eq.append(1.0)
    offset = m
    for posts in posts_per_source:
        P = np.asarray(posts, dtype=float)  # (n_x, m)
        n_x = P.shape[0]
        # q - P.T @ λ = 0
        for y in range(m):
            row = np.zeros(n)
            row[y] = 1.0
            row[offset : offset + n_x] = -P[:, y]
            A_eq.append(row)
            b_eq.append(0.0)
        # sum λ = 1
        row = np.zeros(n)
        row[offset : offset + n_x] = 1.0
        A_eq.append(row)
        b_eq.append(1.0)
        offset += n_x
    bounds = [(0.0, None)] * n
    res = linprog(
        c,
        A_eq=np.asarray(A_eq),
        b_eq=np.asarray(b_eq),
        bounds=bounds,
        method="highs",
    )
    if not res.success:
        return None
    q = np.maximum(res.x[:m], 0.0)
    s = q.sum()
    if s <= 0:
        return None
    return q / s


def _intersection_vertices(posts_per_source, n_directions=64, seed=1201):
    """Approximate vertices of ∩ conv hulls by LP pushes in many directions."""
    m = len(posts_per_source[0][0])
    rng = np.random.default_rng(seed)
    verts = []

    def _add(q):
        if q is None:
            return
        for v in verts:
            if np.allclose(v, q, atol=1e-8):
                return
        verts.append(q)

    # coordinate / simplex extremes
    for e in np.eye(m):
        _add(_point_in_all_hulls_lp(posts_per_source, direction=e))
        _add(_point_in_all_hulls_lp(posts_per_source, direction=-e))
    # random directions on sphere
    for _ in range(n_directions):
        d = rng.normal(size=m)
        nrm = np.linalg.norm(d)
        if nrm < 1e-15:
            continue
        _add(_point_in_all_hulls_lp(posts_per_source, direction=d / nrm))
    # always include barycenter solve (feasibility witness)
    _add(_point_in_all_hulls_lp(posts_per_source, direction=None))
    # include raw source posteriors that happen to lie in all hulls
    for posts in posts_per_source:
        for p in posts:
            ok = True
            # check membership via LP with tiny objective, forcing q≈p
            # cheaper: try direction toward p from barycenter
            _add(_point_in_all_hulls_lp(posts_per_source, direction=p))
    return verts


def blackwell_redundancy_finite_y(joints_sy):
    """Blackwell I_cap for finite (possibly non-binary) Y via linprog (F12).

    1) Approximate vertices of the intersection of source posterior convex hulls
       by directional LPs (scipy.optimize.linprog).
    2) Maximise I(Q;Y)=H(Y)-∑_k w_k H(v_k) over mixtures of those vertices that
       reproduce p(Y) — this second step is itself a linprog in the weights w.
    """
    require(HAS_SCIPY, "scipy.optimize.linprog required for finite-Y Blackwell RB(0)")
    posts_per_source = []
    py = None
    for j in joints_sy:
        posts, py_j = _source_posteriors(j)
        require(len(posts) >= 1, "source has no positive-mass outcomes")
        posts_per_source.append(posts)
        if py is None:
            py = py_j
    hy = entropy(py)
    verts = _intersection_vertices(posts_per_source)
    require(len(verts) >= 1, "empty Blackwell intersection (unexpected)")
    # Drop near-duplicates already handled; ensure p_Y itself is available
    # (always in intersection). Add it so I=0 is feasible.
    py = np.asarray(py, dtype=float)
    py = py / py.sum()
    has_py = any(np.allclose(v, py, atol=1e-7) for v in verts)
    if not has_py:
        verts.append(py.copy())
    r = len(verts)
    m = len(py)
    # min ∑ w_k H(v_k)  s.t.  V w = p_Y,  1·w = 1, w >= 0
    H_v = np.array([entropy(v) for v in verts], dtype=float)
    c = H_v  # minimise conditional entropy
    A_eq = np.vstack([np.asarray(verts, dtype=float).T, np.ones((1, r))])
    b_eq = np.concatenate([py, [1.0]])
    res = linprog(c, A_eq=A_eq, b_eq=b_eq, bounds=[(0, None)] * r, method="highs")
    if not res.success:
        # Fallback: single atom at p_Y → I=0
        return 0.0
    w = np.maximum(res.x, 0.0)
    if w.sum() > 0:
        w = w / w.sum()
    hy_q = float(np.dot(w, H_v))
    return float(max(hy - hy_q, 0.0))


def rb0_blackwell(joint_r1r2y):
    """RB(0) = Blackwell redundancy I_cap for two sources about Y.

    Binary Y: closed-form posterior-interval method (legacy exact).
    Non-binary finite Y: linprog vertex/mixture method (F12 TWO_BIT_COPY).
    """
    j = np.asarray(joint_r1r2y, dtype=float)
    j = j / j.sum()
    p_r1y = j.sum(axis=1)
    p_r2y = j.sum(axis=0)
    if j.shape[2] == 2:
        return blackwell_redundancy_binary_y([p_r1y, p_r2y])
    return blackwell_redundancy_finite_y([p_r1y, p_r2y])


def two_bit_copy_joint():
    """TWO_BIT_COPY (F12): independent fair bits A,B; Y=(A,B) 4-valued.

    Encoding Y: 0=(0,0), 1=(0,1), 2=(1,0), 3=(1,1).
    """
    j = np.zeros((2, 2, 4), dtype=float)
    for a, b in itertools.product((0, 1), repeat=2):
        y = 2 * a + b
        j[a, b, y] = 0.25
    return j


def two_bit_copy_report():
    """Side-by-side Williams-Beer I_min Red vs Blackwell RB(0) for TWO_BIT_COPY."""
    j = two_bit_copy_joint()
    atoms = pid_atoms_williams_beer(j)
    rb0 = rb0_blackwell(j)
    return {
        "Red_williams_beer": atoms["Red"],
        "RB0_blackwell": rb0,
        "Unq1": atoms["Unq1"],
        "Unq2": atoms["Unq2"],
        "Syn": atoms["Syn"],
        "I_joint": atoms["I_joint"],
        "claim": (
            "Williams-Beer I_min Red=1 is misleading on TWO_BIT_COPY; "
            "Blackwell/Kolchinsky RB(0)=0 is the correct redundancy "
            "(Harder/Salge/Polani 2013; Kolchinsky arXiv:2405.07665). "
            "Both reported side by side (like EI_q beside PID)."
        ),
        "arxiv_wb": ARXIV_WB,
        "arxiv_rb": ARXIV_RB,
    }


def pid_atoms(sources, target, measure="williams_beer"):
    """API: sources = (r1_array, r2_array), target = y_array."""
    require(measure == "williams_beer", "only williams_beer implemented as basis")
    r1, r2 = sources
    joint = joint_from_samples(r1, r2, target)
    return pid_atoms_williams_beer(joint)
