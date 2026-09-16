"""Identifiability formulas: conditioning, non-identifiability, EI baselines.

FORMALISM.md sections 10 and 12; legacy verify_extensions.py e02, e07, e08,
e09, e12 (optional e15).

Not a Dataset Manifest / Train-Holdout / real-data ValidationReport.
"""

from __future__ import annotations

import itertools
import math
from typing import Dict, Iterable, List, Optional, Sequence, Tuple, Union

import numpy as np

from scoped_correspondence.errors import ScopeViolationError

ArrayLike = Union[np.ndarray, Sequence[float], Sequence[Sequence[float]]]


def _as_float_vector(a: ArrayLike, *, name: str) -> np.ndarray:
    v = np.asarray(a, dtype=float).reshape(-1)
    if v.size == 0:
        raise ScopeViolationError(f"{name}: empty array")
    if not np.isfinite(v).all():
        raise ScopeViolationError(f"{name}: must be finite")
    return v


def _as_float_matrix(a: ArrayLike, *, name: str) -> np.ndarray:
    m = np.asarray(a, dtype=float)
    if m.ndim != 2:
        raise ScopeViolationError(f"{name}: expected 2D matrix, got shape {m.shape}")
    if not np.isfinite(m).all():
        raise ScopeViolationError(f"{name}: must be finite")
    return m


def _stochastic(p: ArrayLike, *, name: str = "P") -> np.ndarray:
    """Row-stochastic transition matrix (legacy verify_extensions.stochastic)."""
    p_arr = _as_float_matrix(p, name=name)
    if (p_arr < 0).any():
        raise ScopeViolationError(f"{name}: negative transition probability")
    row_sums = p_arr.sum(axis=1)
    if not np.allclose(row_sums, np.ones(len(p_arr)), atol=1e-10, rtol=1e-9):
        raise ScopeViolationError(f"{name}: rows must sum to 1")
    return p_arr


def _entropy(prob: ArrayLike) -> float:
    """Shannon entropy in bits (legacy verify_extensions.entropy)."""
    p = np.asarray(prob, dtype=float).reshape(-1)
    return float(-sum(x * math.log2(x) for x in p if x > 0))


def _mutual_channel(p: ArrayLike, q: ArrayLike) -> float:
    """I_q(input; output) for channel P under input distribution q (bits).

    Legacy verify_extensions.mutual_channel — EI_q(P) = I_q(Z_t; Z_{t+1}).
    """
    p_arr = _stochastic(p, name="P")
    q_arr = _as_float_vector(q, name="q")
    if q_arr.shape != (len(p_arr),):
        raise ScopeViolationError(
            f"q length {q_arr.shape[0]} != channel rows {len(p_arr)}"
        )
    if (q_arr < 0).any():
        raise ScopeViolationError("q: negative probability")
    if not np.isclose(q_arr.sum(), 1.0, atol=1e-10, rtol=1e-9):
        raise ScopeViolationError("q: must sum to 1")
    output = q_arr @ p_arr
    total = 0.0
    for i in range(len(q_arr)):
        for j in range(p_arr.shape[1]):
            if q_arr[i] > 0 and p_arr[i, j] > 0:
                total += q_arr[i] * p_arr[i, j] * math.log2(p_arr[i, j] / output[j])
    return float(total)


def _mi_joint(joint: ArrayLike) -> float:
    """Mutual information of a joint matrix (legacy verify_extensions.mi_joint)."""
    j = _as_float_matrix(joint, name="joint")
    if (j < 0).any():
        raise ScopeViolationError("joint: negative mass")
    px, py = j.sum(axis=1), j.sum(axis=0)
    return float(
        sum(
            j[i, k] * math.log2(j[i, k] / (px[i] * py[k]))
            for i, k in np.ndindex(j.shape)
            if j[i, k] > 0
        )
    )


def _partitions(n: int) -> Iterable[List[int]]:
    """All set-partitions of {0..n-1} as label lists (legacy partitions).

    For n=4 yields exactly 15 partitions (Bell number B_4 = 15).
    """
    if n < 1:
        raise ScopeViolationError(f"partitions: n must be >= 1; got {n}")

    def extend(labels: List[int]):
        if len(labels) == n:
            yield labels
        else:
            for label in range(max(labels) + 2):
                yield from extend(labels + [label])

    yield from extend([0])


def _aggregation(labels: Sequence[int]) -> Tuple[np.ndarray, np.ndarray]:
    """Partition matrix C and left-inverse lift (legacy aggregation)."""
    labels_l = list(labels)
    if not labels_l:
        raise ScopeViolationError("aggregation: empty labels")
    c = np.eye(max(labels_l) + 1)[labels_l]
    lift = c.T / c.sum(axis=0)[:, None]
    if not np.allclose(lift @ c, np.eye(c.shape[1]), atol=1e-10, rtol=1e-9):
        raise ScopeViolationError("aggregation: lift @ C is not identity")
    return c, lift


def demo_ei_matrices() -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Legacy verify_extensions.matrices() block used by e07 / e09 block check.

    Returns (P_lumpable, P_bad, C, lift) for labels [0,0,0,1].
    """
    p = np.zeros((4, 4))
    p[:3, :3] = 1 / 3
    p[3, 3] = 1
    bad = np.eye(4)[[2, 3, 0, 1]]
    c, lift = _aggregation([0, 0, 0, 1])
    return p, bad, c, lift


# ---------------------------------------------------------------------------
# e02 — sampling alias & conditioning
# ---------------------------------------------------------------------------


def delay_amplification(alpha: float) -> float:
    """Conditioning factor 1/|sin alpha| (FORMALISM reconstruction / e02).

    Maps to legacy ``e02_sampling_alias_and_conditioning`` inverse-sine factors.
    When alpha approaches 0 or pi, reconstruction from delayed observations
    becomes numerically ill-conditioned.
    """
    a = float(alpha)
    if not math.isfinite(a):
        raise ScopeViolationError(f"delay_amplification: alpha must be finite; got {alpha!r}")
    s = abs(math.sin(a))
    if s == 0.0:
        raise ScopeViolationError(
            "delay_amplification: |sin(alpha)|=0 — singular delay geometry "
            "(alpha near 0 or pi); amplification undefined"
        )
    return float(1.0 / s)


def indistinguishable_delay_vectors(
    theta: float = 0.7,
    n: int = 8,
) -> List[float]:
    """Delay embedding vector cos(theta - j*pi) indistinguishable from -theta.

    Legacy e02: under alias sampling, vectors for +theta and -theta coincide
    because cos is even and the pi-spacing flips sign consistently.
    """
    t = float(theta)
    if not math.isfinite(t):
        raise ScopeViolationError(f"indistinguishable_delay_vectors: theta must be finite; got {theta!r}")
    if int(n) < 1:
        raise ScopeViolationError(f"indistinguishable_delay_vectors: n must be >= 1; got {n!r}")
    n_i = int(n)
    a = np.array([math.cos(t - j * math.pi) for j in range(n_i)], dtype=float)
    b = np.array([math.cos(-t - j * math.pi) for j in range(n_i)], dtype=float)
    if not np.allclose(a, b, atol=1e-10, rtol=1e-9):
        raise ScopeViolationError(
            "indistinguishable_delay_vectors: +theta and -theta vectors differ "
            "(unexpected for this alias geometry)"
        )
    return a.tolist()


def delay_conditioning_report(
    theta: float = 0.7,
    alphas: Sequence[float] = (0.7, 0.01),
    n: int = 8,
) -> Dict[str, object]:
    """Combined e02 report: alias vectors + inverse-sine amplification factors.

    Legacy evidence keys: indistinguishable_delay_vectors, inverse_sine_factors.
    """
    vectors = indistinguishable_delay_vectors(theta=theta, n=n)
    factors = {str(float(a)): delay_amplification(float(a)) for a in alphas}
    # Legacy countercase: amplification at 0.01 >> 50x amplification at 0.7
    if "0.01" in factors and "0.7" in factors:
        if not (factors["0.01"] > 50 * factors["0.7"]):
            raise ScopeViolationError(
                "delay_conditioning_report: expected conditioning countercase "
                "amplification(0.01) > 50 * amplification(0.7)"
            )
    return {
        "theta": float(theta),
        "indistinguishable_delay_vectors": vectors,
        "inverse_sine_factors": factors,
        "cos_theta_equals_cos_minus_theta": bool(
            math.isclose(math.cos(float(theta)), math.cos(-float(theta)), abs_tol=1e-15)
        ),
        "source": "verify_extensions.py e02_sampling_alias_and_conditioning",
    }


# ---------------------------------------------------------------------------
# e12 — parameter scaling non-identifiability
# ---------------------------------------------------------------------------


def parameter_scaling_invariance(
    sigma: float,
    gamma: float,
    scale: float,
) -> Dict[str, object]:
    """Reparametrization Gamma'=k*Gamma, sigma'=sigma/k leaves tanh(sigma*Gamma).

    FORMALISM.md section 12; legacy e12_parameter_scaling_nonidentifiability.
    """
    s = float(sigma)
    g = float(gamma)
    k = float(scale)
    if not all(math.isfinite(v) for v in (s, g, k)):
        raise ScopeViolationError("parameter_scaling_invariance: all args must be finite")
    if k == 0.0:
        raise ScopeViolationError("parameter_scaling_invariance: scale k must be nonzero")
    original = math.tanh(s * g)
    transformed = math.tanh((s / k) * (k * g))
    return {
        "sigma": s,
        "gamma": g,
        "scale": k,
        "sigma_prime": s / k,
        "gamma_prime": k * g,
        "original": float(original),
        "transformed": float(transformed),
        "abs_error": float(abs(original - transformed)),
        "invariant": bool(math.isclose(original, transformed, abs_tol=1e-12, rel_tol=0.0)),
        "identified_combination": "sigma*gamma (or sigma*a)",
        "source": "FORMALISM.md section 12; e12_parameter_scaling_nonidentifiability",
    }


def identifiability_jacobian_rank(
    sigma: float,
    a: float,
    g: ArrayLike,
    *,
    tol: float = 1e-10,
) -> int:
    """Rank of response Jacobian wrt (sigma, a) for tanh(sigma*a*g).

    Columns are collinear (product sigma*a is the identifiable combination),
    so rank is 1 for nontrivial g (legacy e12).
    """
    s = float(sigma)
    amp = float(a)
    g_arr = _as_float_vector(g, name="g")
    if not math.isfinite(s) or not math.isfinite(amp):
        raise ScopeViolationError("identifiability_jacobian_rank: sigma, a must be finite")
    if tol < 0:
        raise ScopeViolationError(f"tol must be >= 0; got {tol!r}")
    sech2 = 1.0 / np.cosh(s * amp * g_arr) ** 2
    jacobian = np.column_stack([amp * g_arr * sech2, s * g_arr * sech2])
    # Sanity: directional derivative along (sigma, -a) is zero.
    if not np.allclose(jacobian @ np.array([s, -amp]), np.zeros(len(g_arr)), atol=1e-8):
        raise ScopeViolationError(
            "identifiability_jacobian_rank: expected null direction (sigma, -a)"
        )
    return int(np.linalg.matrix_rank(jacobian, tol=tol))


# ---------------------------------------------------------------------------
# e09 — SVD emergence does not imply EI
# ---------------------------------------------------------------------------


def svd_emergence_vs_ei(
    P: Optional[ArrayLike] = None,
    *,
    spectral_tol: float = 1e-12,
    check_all_partitions: bool = True,
) -> Dict[str, object]:
    """Positive delta_svd need not imply positive EI (FORMALISM.md section 10).

    Legacy e09_svd_does_not_imply_ei: uniform 4x4 channel has
    singular values [1,0,0,0], delta_svd = 0.75, EI = 0 under uniform q;
    all 15 partitions of 4 states keep EI = 0.
    """
    if P is None:
        p = np.full((4, 4), 0.25)
    else:
        p = _stochastic(P, name="P")
    spectrum = np.linalg.svd(p, compute_uv=False)
    rank = int((spectrum > spectral_tol).sum())
    if rank < 1:
        raise ScopeViolationError("svd_emergence_vs_ei: matrix rank < 1")
    n = p.shape[0]
    delta_svd = float(spectrum.sum() * (1.0 / rank - 1.0 / n))
    q_uniform = np.full(n, 1.0 / n)
    ei = _mutual_channel(p, q_uniform)

    partition_count = 0
    if check_all_partitions:
        for labels in _partitions(n):
            c, lift = _aggregation(labels)
            reduced = lift @ p @ c
            # All rows equal (memoryless uniform channel stays flat under aggregation)
            if not np.allclose(reduced, np.tile(reduced[0], (len(reduced), 1)), atol=1e-10):
                raise ScopeViolationError(
                    "svd_emergence_vs_ei: reduced kernel rows not identical"
                )
            ei_red = _mutual_channel(reduced, np.full(len(reduced), 1.0 / len(reduced)))
            if not math.isclose(ei_red, 0.0, abs_tol=1e-12):
                raise ScopeViolationError(
                    f"svd_emergence_vs_ei: expected EI=0 on partition; got {ei_red}"
                )
            partition_count += 1

    return {
        "rank": rank,
        "singular_values": spectrum.tolist(),
        "delta_svd": delta_svd,
        "EI": float(ei),
        "all_partitions_checked": partition_count if check_all_partitions else None,
        "spectral_rank_tolerance": float(spectral_tol),
        "source": (
            "FORMALISM.md section 10 (SVD emergence does not imply EI gain); "
            "e09_svd_does_not_imply_ei"
        ),
    }


# ---------------------------------------------------------------------------
# e08 — fixed-ensemble data processing inequality
# ---------------------------------------------------------------------------


def fixed_ensemble_data_processing(
    *,
    seed: int = 1977,
    n_kernels: int = 10,
    n_states: int = 4,
) -> Dict[str, object]:
    """Fixed-ensemble DPI: macro MI <= micro MI for every partition (e08).

    For each random row-stochastic P and ensemble q, form joint = q[:,None]*P
    and compare I(micro) vs I(C^T joint C) over all partitions of n_states.
    For n_states=4 and n_kernels=10: 10 * 15 = 150 comparisons (legacy).
    """
    if n_states < 1 or n_kernels < 1:
        raise ScopeViolationError("fixed_ensemble_data_processing: sizes must be >= 1")
    rng = np.random.default_rng(int(seed))
    comparisons = 0
    max_gap = 0.0
    for _ in range(int(n_kernels)):
        p = rng.uniform(0.01, 1.0, (n_states, n_states))
        p /= p.sum(axis=1)[:, None]
        q = rng.uniform(0.01, 1.0, n_states)
        q /= q.sum()
        joint = q[:, None] * p
        micro = _mutual_channel(p, q)
        for labels in _partitions(n_states):
            c, _ = _aggregation(labels)
            macro = _mi_joint(c.T @ joint @ c)
            if macro > micro + 1e-12:
                raise ScopeViolationError(
                    f"fixed-ensemble DPI failed: macro={macro} > micro={micro}"
                )
            max_gap = max(max_gap, float(micro - macro))
            comparisons += 1
    return {
        "random_seed": int(seed),
        "n_kernels": int(n_kernels),
        "n_states": int(n_states),
        "fixed_ensemble_comparisons": comparisons,
        "max_micro_minus_macro": max_gap,
        "source": "verify_extensions.py e08_fixed_ensemble_data_processing",
    }


# ---------------------------------------------------------------------------
# e07 — EI baseline dependence
# ---------------------------------------------------------------------------


def effective_information_baseline(
    P: Optional[ArrayLike] = None,
    C: Optional[ArrayLike] = None,
    lift: Optional[ArrayLike] = None,
) -> Dict[str, object]:
    """EI under named intervention baselines (FORMALISM.md section 10 / e07).

    Default matrices match legacy ``matrices()``: lumpable 4-state block with
    partition labels [0,0,0,1]. Reports:
      - EI_uniform_micro  (q = uniform on 4)
      - EI_uniform_macro  (q = uniform on 2, kernel = lift @ P @ C)
      - EI_matched_micro  (q = q_macro @ lift on micro channel)
      - delta_EI = EI_uniform_macro - EI_uniform_micro

    Makes explicit that Delta-EI is only meaningful relative to a declared
    baseline intervention distribution (Typ 1 / section 10).
    """
    if P is None and C is None and lift is None:
        p, _bad, c, lift_m = demo_ei_matrices()
    else:
        if P is None or C is None or lift is None:
            raise ScopeViolationError(
                "effective_information_baseline: pass all of P, C, lift or none"
            )
        p = _stochastic(P, name="P")
        c = _as_float_matrix(C, name="C")
        lift_m = _as_float_matrix(lift, name="lift")
    n = p.shape[0]
    m = c.shape[1]
    qmacro = np.full(m, 1.0 / m)
    qmicro = np.full(n, 1.0 / n)
    kernel = lift_m @ p @ c
    # Candidate macro kernel need not be re-normalized beyond lift@P@C for the
    # exact lumpable demo (legacy uses lift @ p @ c directly in mutual_channel).
    ei_micro = _mutual_channel(p, qmicro)
    ei_macro = _mutual_channel(kernel, qmacro)
    matched_prep = qmacro @ lift_m
    matched = _mutual_channel(p, matched_prep)
    by_entropies = _entropy(qmicro @ p) - sum(
        qmicro[i] * _entropy(p[i]) for i in range(n)
    )
    return {
        "EI_uniform_micro": float(ei_micro),
        "EI_uniform_macro": float(ei_macro),
        "delta_EI": float(ei_macro - ei_micro),
        "EI_matched_micro": float(matched),
        "lifted_preparation": matched_prep.tolist(),
        "EI_uniform_micro_via_entropies": float(by_entropies),
        "baselines": {
            "uniform_micro": qmicro.tolist(),
            "uniform_macro": qmacro.tolist(),
            "matched_micro": matched_prep.tolist(),
        },
        "source": (
            "FORMALISM.md section 10 (Typ 1 / named baseline); "
            "e07_effective_information_ensembles"
        ),
    }


# ---------------------------------------------------------------------------
# e15 — predictive states (optional bonus)
# ---------------------------------------------------------------------------


def predictive_states(
    transition: Optional[ArrayLike] = None,
    *,
    history_len: int = 4,
    future_len: int = 3,
) -> Dict[str, object]:
    """Exact finite-state predictive states for a binary Markov channel (e15).

    Not a learned epsilon-machine. Default transition [[.8,.2],[.2,.8]]:
    two predictive states (last symbol). IID [[.5,.5],[.5,.5]]: one.
    """
    if transition is None:
        kern = np.array([[0.8, 0.2], [0.2, 0.8]], dtype=float)
    else:
        kern = _stochastic(transition, name="transition")
    if kern.shape != (2, 2):
        raise ScopeViolationError(
            f"predictive_states: binary channel expected; got shape {kern.shape}"
        )
    h_len = int(history_len)
    f_len = int(future_len)
    if h_len < 1 or f_len < 1:
        raise ScopeViolationError("predictive_states: history_len/future_len must be >= 1")

    def future_distribution(last: int, kernel: np.ndarray) -> np.ndarray:
        values = []
        for future in itertools.product([0, 1], repeat=f_len):
            probability = 1.0
            previous = last
            for symbol in future:
                probability *= kernel[previous, symbol]
                previous = symbol
            values.append(probability)
        return np.array(values, dtype=float)

    representatives: Dict[int, np.ndarray] = {}
    maximum_error = 0.0
    joint_paths = 0
    for history in itertools.product([0, 1], repeat=h_len):
        history_mass = 0.5
        for previous, following in zip(history, history[1:]):
            history_mass *= kern[previous, following]
        joint_masses = []
        for future in itertools.product([0, 1], repeat=f_len):
            path = history + future
            mass = 0.5
            for previous, following in zip(path, path[1:]):
                mass *= kern[previous, following]
            joint_masses.append(mass)
            joint_paths += 1
        conditioned = np.array(joint_masses, dtype=float) / history_mass
        reference = future_distribution(history[-1], kern)
        if not np.allclose(conditioned, reference, atol=1e-10, rtol=1e-9):
            raise ScopeViolationError("predictive_states: conditioning mismatch")
        maximum_error = max(maximum_error, float(np.abs(conditioned - reference).max()))
        if history[-1] in representatives:
            if not np.allclose(conditioned, representatives[history[-1]], atol=1e-10):
                raise ScopeViolationError(
                    "predictive_states: same last symbol, different futures"
                )
        representatives[history[-1]] = conditioned

    if np.allclose(kern[0], kern[1]):
        n_pred = 1
    else:
        n_pred = len(representatives)

    iid = np.full((2, 2), 0.5)
    iid_same = bool(
        np.allclose(future_distribution(0, iid), future_distribution(1, iid), atol=1e-12)
    )

    return {
        "persistent_binary_chain_predictive_states": int(n_pred),
        "iid_predictive_states": 1 if iid_same else 2,
        "joint_paths_enumerated": int(joint_paths),
        "max_conditioning_error": float(maximum_error),
        "scope": "exact finite-state examples, not a learned epsilon-machine",
        "source": "verify_extensions.py e15_predictive_states",
    }


__all__ = [
    "delay_amplification",
    "delay_conditioning_report",
    "demo_ei_matrices",
    "effective_information_baseline",
    "fixed_ensemble_data_processing",
    "identifiability_jacobian_rank",
    "indistinguishable_delay_vectors",
    "parameter_scaling_invariance",
    "predictive_states",
    "svd_emergence_vs_ei",
]
