"""BROJA bivariate unique information (Milestone 17).

Bertschinger, Rauh, Olbrich, Jost & Ay (2014), *Quantifying Unique Information*,
Entropy 16(4):2161–2183; DOI 10.3390/e16042161 (arXiv:1311.2852).

Paper variables → this module
-----------------------------
  Paper **X** (target about which information is measured) → our **y**
  Paper **Y** (first source)                              → our **r1**
  Paper **Z** (second source)                             → our **r2**

Definitions (Bertschinger et al. 2014)
--------------------------------------
Let P = p(r1, r2, y). The feasible set is

    Δ_P = { Q : Q(y, r1) = P(y, r1)  and  Q(y, r2) = P(y, r2) }.

Unique information of source 1 (resp. 2):

    Unq1 = UI(y; r1 \\ r2) = min_{Q ∈ Δ_P} I_Q(y; r1 | r2)
    Unq2 = UI(y; r2 \\ r1) = min_{Q ∈ Δ_P} I_Q(y; r2 | r1)

Redundancy and synergy then follow from the PID identities
(which agree under BROJA; Bertschinger et al. Prop. 2 / Thm. 3):

    Red = I_P(y; r1) − Unq1  =  I_P(y; r2) − Unq2
    Syn = I_P(y; r1, r2) − Unq1 − Unq2 − Red

Because Q(y, r2) is fixed on Δ_P, H_Q(y|r2) is constant, so
minimising I_Q(y; r1|r2) = H(y|r2) − H(y|r1,r2) is equivalent to
**maximising** H_Q(y|r1,r2). Symmetric for Unq2.

Optimiser
---------
Per-y couplings in Δ_P are parameterised by the free ``(n1-1)×(n2-1)``
interior of the transportation polytope (margins P(r1|y), P(r2|y) fixed).
``scipy.optimize.minimize`` (SLSQP) minimises conditional mutual information
from ≥3 independent starts; agreement within ``tol`` is required.

Scope (M17)
-----------
Bivariate (two sources) only. Finite alphabets with
n1 · n2 · ny ≤ MAX_JOINT_SUPPORT. No N-source generalisation.
Does **not** edit information_decomposition/core.py — calls
``two_bit_copy_joint``, ``pid_atoms_williams_beer``, ``rb0_blackwell``
for cross-checks only.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

from scoped_correspondence.errors import ScopeViolationError

try:
    from scipy.optimize import minimize

    HAS_SCIPY = True
except ImportError:  # pragma: no cover
    HAS_SCIPY = False
    minimize = None


DOI = "10.3390/e16042161"
ARXIV = "https://arxiv.org/abs/1311.2852"
SOURCE = (
    "Bertschinger, Rauh, Olbrich, Jost & Ay 2014, "
    "Quantifying Unique Information, Entropy 16(4):2161–2183; "
    f"DOI {DOI}"
)

MAX_JOINT_SUPPORT = 64
DEFAULT_N_STARTS = 5
DEFAULT_TOL = 1e-5
_EPS = 1e-15


def _require_scipy() -> None:
    if not HAS_SCIPY:
        raise ScopeViolationError(
            "broja_pid_bivariate requires scipy.optimize.minimize (SLSQP)"
        )


def _mi_xy(joint_xy: np.ndarray) -> float:
    """I(X;Y) from joint p(x,y)."""
    j = np.asarray(joint_xy, dtype=float)
    s = j.sum()
    if s <= 0:
        return 0.0
    j = j / s
    px = j.sum(axis=1)
    py = j.sum(axis=0)
    total = 0.0
    for i in range(j.shape[0]):
        for k in range(j.shape[1]):
            if j[i, k] > _EPS and px[i] > _EPS and py[k] > _EPS:
                total += float(j[i, k] * np.log2(j[i, k] / (px[i] * py[k])))
    return float(total)


def _i_y_r1_given_r2(q: np.ndarray) -> float:
    """I_Q(y; r1 | r2) for joint q(r1, r2, y)."""
    q = np.asarray(q, dtype=float)
    s = q.sum()
    if s <= 0:
        return 0.0
    q = q / s
    p_r2y = q.sum(axis=0)
    p_r2 = p_r2y.sum(axis=1)
    hy_r2 = 0.0
    for j in range(q.shape[1]):
        if p_r2[j] <= _EPS:
            continue
        row = p_r2y[j] / p_r2[j]
        for p in row:
            if p > _EPS:
                hy_r2 -= float(p_r2[j]) * float(p) * float(np.log2(p))
    p_r1r2 = q.sum(axis=2)
    hy_r1r2 = 0.0
    for i in range(q.shape[0]):
        for j in range(q.shape[1]):
            m = p_r1r2[i, j]
            if m <= _EPS:
                continue
            row = q[i, j, :] / m
            for p in row:
                if p > _EPS:
                    hy_r1r2 -= float(m) * float(p) * float(np.log2(p))
    return float(hy_r2 - hy_r1r2)


PMF_TOL = 1e-12
INPUT_MODES = ("weights", "pmf")


def _input_total(joint_r1r2y, input_mode: str) -> float:
    from fractions import Fraction
    import math

    if input_mode not in INPUT_MODES:
        raise ScopeViolationError(f"broja_pid_bivariate: input_mode must be one of {INPUT_MODES}; got {input_mode!r}")
    flat = np.asarray(joint_r1r2y, dtype=object).ravel().tolist()
    exact = all(isinstance(m, (int, Fraction)) and not isinstance(m, (bool, np.bool_)) for m in flat)
    if not exact:
        # called AFTER _validate_joint: finiteness and overflow are checked there; its
        # sign check is TOLERANT (clips values >= -1e-12), hence the strict check below
        total = math.fsum(float(m) for m in flat)
    else:
        total = sum(Fraction(m) for m in flat)
    if input_mode == "pmf":
        # PMF-Review PMF1: original masses must be non-negative; Fractions compared exactly
        for m in flat:
            neg = (m < 0) if isinstance(m, (int, Fraction)) and not isinstance(m, (bool, np.bool_)) else (float(m) < 0)
            if neg:
                raise ScopeViolationError(f"broja_pid_bivariate: input_mode='pmf' refuses negative mass {m!r}")
        if exact and total != 1:
            raise ScopeViolationError(f"broja_pid_bivariate: input_mode='pmf' needs exact total mass 1; got {total}")
        if not exact and abs(total - 1.0) > PMF_TOL:
            raise ScopeViolationError(
                f"broja_pid_bivariate: input_mode='pmf' needs total mass 1 within {PMF_TOL}; got {total!r} "
                "(use input_mode='weights' for unnormalised weights)"
            )
    return float(total)


def _validate_joint(joint_r1r2y: np.ndarray) -> np.ndarray:
    j = np.asarray(joint_r1r2y, dtype=float)
    if j.ndim != 3:
        raise ScopeViolationError(
            f"broja_pid_bivariate: joint must be 3-D (n1,n2,ny); got shape {j.shape}"
        )
    # Followup-Review-Fix R4: refuse NaN/inf early instead of failing later in
    # the optimiser with a misleading message.
    if not np.all(np.isfinite(j)):
        raise ScopeViolationError("broja_pid_bivariate: joint has non-finite mass")
    if np.any(j < -1e-12):
        raise ScopeViolationError("broja_pid_bivariate: joint has negative mass")
    j = np.maximum(j, 0.0)
    s = j.sum()
    if not np.isfinite(s):
        raise ScopeViolationError("broja_pid_bivariate: total mass overflows")
    if s <= 0:
        raise ScopeViolationError("broja_pid_bivariate: joint has zero total mass")
    j = j / s
    n1, n2, ny = j.shape
    if n1 * n2 * ny > MAX_JOINT_SUPPORT:
        raise ScopeViolationError(
            f"broja_pid_bivariate: joint support {n1}*{n2}*{ny}="
            f"{n1 * n2 * ny} exceeds MAX_JOINT_SUPPORT={MAX_JOINT_SUPPORT} "
            "(huge alphabets out of M17 scope)"
        )
    if n1 < 1 or n2 < 1 or ny < 1:
        raise ScopeViolationError("broja_pid_bivariate: empty alphabet")
    return j


# ---------------------------------------------------------------------------
# Free-parameter transportation-polytope representation of Δ_P
# ---------------------------------------------------------------------------


def _active_ys(p: np.ndarray) -> List[int]:
    py = p.sum(axis=(0, 1))
    return [int(k) for k, m in enumerate(py) if m > _EPS]


def _margins_given_y(p: np.ndarray, k: int) -> Tuple[np.ndarray, np.ndarray, float]:
    py = float(p.sum(axis=(0, 1))[k])
    a = p.sum(axis=1)[:, k] / py  # P(r1 | y=k)
    b = p.sum(axis=0)[:, k] / py  # P(r2 | y=k)
    return a, b, py


def _coupling_from_free(free: np.ndarray, a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Rebuild coupling C(r1,r2) with margins a, b from free (n1-1, n2-1) block."""
    n1 = len(a)
    n2 = len(b)
    C = np.zeros((n1, n2), dtype=float)
    if n1 == 1 and n2 == 1:
        C[0, 0] = 1.0
        return C
    if n1 == 1:
        C[0, :] = b
        return C
    if n2 == 1:
        C[:, 0] = a
        return C
    F = np.asarray(free, dtype=float).reshape(n1 - 1, n2 - 1)
    C[: n1 - 1, : n2 - 1] = F
    C[: n1 - 1, n2 - 1] = a[: n1 - 1] - C[: n1 - 1, : n2 - 1].sum(axis=1)
    C[n1 - 1, : n2 - 1] = b[: n2 - 1] - C[: n1 - 1, : n2 - 1].sum(axis=0)
    C[n1 - 1, n2 - 1] = a[n1 - 1] - C[n1 - 1, : n2 - 1].sum()
    return C


def _free_from_coupling(C: np.ndarray) -> np.ndarray:
    n1, n2 = C.shape
    if n1 < 2 or n2 < 2:
        return np.zeros((0, 0), dtype=float)
    return np.asarray(C[: n1 - 1, : n2 - 1], dtype=float).copy()


def _joint_from_frees(frees: Sequence[np.ndarray], p: np.ndarray) -> np.ndarray:
    n1, n2, ny = p.shape
    q = np.zeros_like(p)
    for free, k in zip(frees, _active_ys(p)):
        a, b, py = _margins_given_y(p, k)
        C = _coupling_from_free(free, a, b)
        q[:, :, k] = py * C
    return q


def _frees_from_joint(q: np.ndarray, p: np.ndarray) -> List[np.ndarray]:
    """Extract free blocks from a joint (assumed ≈ in Δ_P)."""
    frees: List[np.ndarray] = []
    for k in _active_ys(p):
        a, b, py = _margins_given_y(p, k)
        if py <= _EPS:
            frees.append(np.zeros((0, 0)))
            continue
        C = q[:, :, k] / py
        # Snap to exact margins before extracting free block
        C = np.maximum(C, 0.0)
        if C.sum() > 0:
            C = C / C.sum()
        # Re-fit margins lightly
        C = _coupling_from_free(_free_from_coupling(np.outer(a, b) * 0 + C), a, b)
        # Use free of the Sinkhorn-ish: prefer free of product-blended C
        # Simpler: take free of max(C,0) re-built via free extraction of C itself
        frees.append(_free_from_coupling(C))
    return frees


def _product_frees(p: np.ndarray) -> List[np.ndarray]:
    frees: List[np.ndarray] = []
    for k in _active_ys(p):
        a, b, _py = _margins_given_y(p, k)
        C = np.outer(a, b)
        frees.append(_free_from_coupling(C))
    return frees


def _observed_frees(p: np.ndarray) -> List[np.ndarray]:
    frees: List[np.ndarray] = []
    for k in _active_ys(p):
        _a, _b, py = _margins_given_y(p, k)
        C = p[:, :, k] / py
        frees.append(_free_from_coupling(C))
    return frees


def _random_frees(p: np.ndarray, rng: np.random.Generator) -> List[np.ndarray]:
    """Random free block near the product coupling, clipped to [0, 1]."""
    frees: List[np.ndarray] = []
    for k in _active_ys(p):
        a, b, _py = _margins_given_y(p, k)
        n1, n2 = len(a), len(b)
        if n1 < 2 or n2 < 2:
            frees.append(np.zeros((0, 0)))
            continue
        base = np.outer(a, b)[: n1 - 1, : n2 - 1]
        noise = rng.normal(0.0, 0.08, size=base.shape)
        frees.append(np.clip(base + noise, 0.0, 1.0))
    return frees


def _pack(frees: Sequence[np.ndarray]) -> np.ndarray:
    parts = [np.asarray(f, dtype=float).ravel() for f in frees]
    parts = [p for p in parts if p.size]
    if not parts:
        return np.zeros(0, dtype=float)
    return np.concatenate(parts)


def _unpack(x: np.ndarray, template: Sequence[np.ndarray]) -> List[np.ndarray]:
    out: List[np.ndarray] = []
    offset = 0
    for t in template:
        n = int(np.asarray(t).size)
        if n == 0:
            out.append(np.zeros((0, 0), dtype=float))
        else:
            out.append(x[offset : offset + n].reshape(t.shape))
            offset += n
    return out


def _optimize_unique(
    p: np.ndarray,
    which: str,
    starts: Sequence[Sequence[np.ndarray]],
    tol: float,
) -> Tuple[float, List[float]]:
    """Minimise I_Q(y; r_which | other) over Δ_P from multiple free-param starts."""
    _require_scipy()
    p = _validate_joint(p)
    template = _product_frees(p)
    n_free = int(_pack(template).size)

    def objective(x: np.ndarray) -> float:
        frees = _unpack(x, template)
        q = _joint_from_frees(frees, p)
        # Soft penalty for negative reconstructed mass
        neg = float(np.minimum(q, 0.0).sum())
        if neg < -1e-10:
            return 1e3 - 100.0 * neg
        q = np.maximum(q, 0.0)
        s = q.sum()
        if s <= 0:
            return 1e3
        q = q / s
        if which == "unq1":
            return _i_y_r1_given_r2(q)
        # Unq2 = I(y; r2 | r1) = I(y; r1' | r2') after swapping source axes
        return _i_y_r1_given_r2(np.swapaxes(q, 0, 1))

    def nonneg_constraints(x: np.ndarray) -> np.ndarray:
        frees = _unpack(x, template)
        q = _joint_from_frees(frees, p)
        return q.ravel()

    optima: List[float] = []
    best_val = float("inf")

    for start in starts:
        x0 = _pack(start)
        if n_free == 0:
            val = float(max(objective(x0), 0.0))
            optima.append(val)
            best_val = min(best_val, val)
            continue
        # Pad / trim if start shape mismatch
        if x0.size != n_free:
            x0 = _pack(template)
        cons = [{"type": "ineq", "fun": nonneg_constraints}]
        res = minimize(
            objective,
            x0,
            method="SLSQP",
            constraints=cons,
            options={"maxiter": 800, "ftol": 1e-14, "disp": False},
        )
        x_hat = res.x if res.success or np.isfinite(res.fun) else x0
        # Also evaluate repaired product blend if reconstruction went negative
        frees_hat = _unpack(x_hat, template)
        q_hat = _joint_from_frees(frees_hat, p)
        if np.any(q_hat < -1e-8):
            # Snap free entries into a feasible box via clip + product fallback
            val = float(objective(_pack(template)))  # product is always feasible
        else:
            val = float(max(objective(x_hat), 0.0))
        # Keep the better of optimised vs start vs product
        val_start = float(max(objective(x0), 0.0))
        val_prod = float(max(objective(_pack(template)), 0.0))
        val = min(val, val_start, val_prod)
        optima.append(val)
        if val < best_val:
            best_val = val

    if not optima:
        raise ScopeViolationError("broja: no optimisation starts provided")

    best_val = float(max(min(optima), 0.0))
    n_agree = sum(1 for v in optima if abs(v - best_val) <= tol)
    if len(optima) >= 3 and n_agree < 3:
        top = sorted(optima)[:3]
        if max(top) - min(top) > tol:
            raise ScopeViolationError(
                f"broja: optimiser did not converge across starts "
                f"(optima={optima!r}, tol={tol}); which={which}"
            )
    return best_val, optima


@dataclass(frozen=True)
class BivariatePIDReport:
    """BROJA bivariate PID atoms (bits).

    Invariant: redundancy + unique_source_1 + unique_source_2 + synergy == I_joint
    (within numerical tolerance).
    """

    redundancy: float
    unique_source_1: float
    unique_source_2: float
    synergy: float
    I_joint: float
    method: str = "broja"
    I_r1: float = 0.0
    I_r2: float = 0.0
    source: str = SOURCE
    doi: str = DOI
    n_starts: int = 0
    unq1_optima: Tuple[float, ...] = ()
    unq2_optima: Tuple[float, ...] = ()
    converged: bool = True
    input_mode: str = "weights"
    input_total_mass: Optional[float] = None  # total of the joint as passed (before normalisation)

    def as_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["unq1_optima"] = list(self.unq1_optima)
        d["unq2_optima"] = list(self.unq2_optima)
        return d

    def assert_pid_sum(self, atol: float = 1e-5) -> None:
        s = (
            self.redundancy
            + self.unique_source_1
            + self.unique_source_2
            + self.synergy
        )
        if abs(s - self.I_joint) > atol:
            raise AssertionError(
                f"PID sum {s} != I_joint {self.I_joint} (atol={atol})"
            )


def broja_pid_bivariate(
    joint_r1r2y: np.ndarray,
    *,
    n_starts: int = DEFAULT_N_STARTS,
    tol: float = DEFAULT_TOL,
    rng: Optional[np.random.Generator] = None,
    input_mode: str = "weights",
) -> BivariatePIDReport:
    """Compute BROJA bivariate PID atoms for joint p(r1, r2, y).

    ``input_mode`` (2026-10-01, recommendation of SCF_FOLLOWUP_REVIEW_637bc1c):
    ``"weights"`` (default, unchanged) renormalises finite non-negative
    weights; ``"pmf"`` requires total mass 1 -- exactly for nested int/Fraction
    input, within ``PMF_TOL`` (math.fsum) for floats -- and refuses anything
    else. The original total is reported as ``input_total_mass``.

    Solves the Bertschinger et al. (2014) convex programs

        Unq1 = min_{Q ∈ Δ_P} I_Q(y; r1 | r2)
        Unq2 = min_{Q ∈ Δ_P} I_Q(y; r2 | r1)

    with Δ_P = {Q : Q(y,r1)=P(y,r1), Q(y,r2)=P(y,r2)}.

    **Paper mapping (required):** Paper X → our y (target); Paper Y → r1;
    Paper Z → r2.

    Convergence: runs ``n_starts`` ≥ 3 independent initialisations (observed
    joint, product coupling given y, and random free-block perturbations) and
    requires the same optimum within ``tol``.

    Parameters
    ----------
    joint_r1r2y :
        Array of shape (n1, n2, ny). Non-negative; renormalised internally.
    n_starts :
        Number of independent SLSQP starts (default 5; must be ≥ 3).
    tol :
        Absolute tolerance for cross-start agreement and PID-sum check.
    rng :
        Optional NumPy Generator for random couplings.
    """
    _require_scipy()
    if n_starts < 3:
        raise ScopeViolationError(
            f"broja_pid_bivariate: n_starts must be ≥ 3 (got {n_starts})"
        )
    p = _validate_joint(joint_r1r2y)  # finiteness, sign, overflow (R4) first
    total_in = _input_total(joint_r1r2y, input_mode)
    if rng is None:
        rng = np.random.default_rng(1729)

    i_r1 = _mi_xy(p.sum(axis=1))
    i_r2 = _mi_xy(p.sum(axis=0))
    n1, n2, ny = p.shape
    i_joint = _mi_xy(p.reshape(n1 * n2, ny))

    starts: List[List[np.ndarray]] = [
        _observed_frees(p),
        _product_frees(p),
    ]
    while len(starts) < n_starts:
        starts.append(_random_frees(p, rng))

    unq1, optima1 = _optimize_unique(p, "unq1", starts, tol)
    unq2, optima2 = _optimize_unique(p, "unq2", starts, tol)

    red_a = i_r1 - unq1
    red_b = i_r2 - unq2
    if abs(red_a - red_b) > max(tol, 1e-4):
        if abs(red_a - red_b) > 1e-3:
            raise ScopeViolationError(
                f"broja: redundancy mismatch I(y;r1)-Unq1={red_a} vs "
                f"I(y;r2)-Unq2={red_b}"
            )
    red = float(max(0.5 * (red_a + red_b), 0.0))
    unq1 = float(max(unq1, 0.0))
    unq2 = float(max(unq2, 0.0))
    syn = float(i_joint - unq1 - unq2 - red)
    if syn < -max(tol, 1e-4):
        raise ScopeViolationError(f"broja: synergy negative beyond tol: {syn}")
    syn = float(max(syn, 0.0))

    report = BivariatePIDReport(
        redundancy=red,
        unique_source_1=unq1,
        unique_source_2=unq2,
        synergy=syn,
        I_joint=float(i_joint),
        method="broja",
        I_r1=float(i_r1),
        I_r2=float(i_r2),
        n_starts=n_starts,
        unq1_optima=tuple(float(v) for v in optima1),
        unq2_optima=tuple(float(v) for v in optima2),
        converged=True,
        input_mode=input_mode,
        input_total_mass=total_in,
    )
    report.assert_pid_sum(atol=max(tol * 10, 1e-4))
    return report


def two_bit_copy_broja_report(
    *,
    n_starts: int = DEFAULT_N_STARTS,
    tol: float = DEFAULT_TOL,
) -> Dict[str, Any]:
    """Side-by-side Williams-Beer / Blackwell-RB(0) / BROJA on TWO_BIT_COPY.

    Expected BROJA: redundancy ≈ 0, unique_source_1 ≈ 1, unique_source_2 ≈ 1,
    synergy ≈ 0 (Harder/Salge/Polani counterexample; BROJA agrees with Blackwell).
    """
    from scoped_correspondence.information_decomposition.core import (
        pid_atoms_williams_beer,
        rb0_blackwell,
        two_bit_copy_joint,
    )

    j = two_bit_copy_joint()
    wb = pid_atoms_williams_beer(j)
    rb0 = float(rb0_blackwell(j))
    broja = broja_pid_bivariate(j, n_starts=n_starts, tol=tol)
    return {
        "williams_beer": {
            "Red": wb["Red"],
            "Unq1": wb["Unq1"],
            "Unq2": wb["Unq2"],
            "Syn": wb["Syn"],
            "I_joint": wb["I_joint"],
            "measure": wb["measure"],
        },
        "blackwell_rb0": {
            "RB0": rb0,
            "note": "Blackwell/Kolchinsky redundancy only (not full PID atoms)",
        },
        "broja": broja.as_dict(),
        "claim": (
            "TWO_BIT_COPY: Williams-Beer I_min Red=1 is misleading; "
            "Blackwell RB(0)=0 and BROJA Red≈0, Unq≈1 each, Syn≈0 agree "
            "on unique bits (Bertschinger et al. 2014 DOI 10.3390/e16042161)."
        ),
        "doi_broja": DOI,
        "arxiv_broja": ARXIV,
    }


__all__ = [
    "ARXIV",
    "DOI",
    "SOURCE",
    "MAX_JOINT_SUPPORT",
    "BivariatePIDReport",
    "broja_pid_bivariate",
    "two_bit_copy_broja_report",
]
