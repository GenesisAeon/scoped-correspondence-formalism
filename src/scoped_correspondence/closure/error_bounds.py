"""Formal reduction error bounds (Michel & Siegle 2024).

Implements the L1 transient / stationary error bounds of Michel & Siegle,
"Formal Error Bounds for the State Space Reduction of Markov Chains",
Performance Evaluation 2024 (DOI 10.1016/j.peva.2024.102464;
arXiv:2403.07618).

Primary formulas (paper numbering as in arXiv:2403.07618v3, 6 Aug 2024 --
the extended version; checked 2026-10-01: Theorem 4 = DTMC bounds, §3.1;
Theorem 5 = CTMC bounds, §3.2):

* **Theorem 4** (DTMC). With error ``e_k^T = π_0^T Π^k A − p_0^T P^k``:
  - (4.1) precise sum form with ⟨|π_j|, |ΠA−AP| 1⟩;
  - (4.2) geometric form with ``||Π||_∞``;
  - (4.3) if ``Π`` is stochastic and ``π_0`` a probability vector:
    ``||e_k||_1 ≤ ||π_0^T A − p_0^T||_1 + k · ||Π A − A P||_∞``.

* **Theorem 5** (CTMC). With ``e_t^T = π_0^T e^{Θ t} A − p_0^T e^{Q t}``:
  - (5.1) integral form;
  - (5.2) exponential form with ``||Θ||_∞``;
  - (5.3) if ``Θ`` is a generator and ``π_0`` a probability vector:
    ``||e_t||_1 ≤ ||π_0^T A − p_0^T||_1 + t · ||Θ A − A Q||_∞``.

* **Corollary 10** (stationary distance-to-stationarity of ``π^T A``):
  ``||π^T A P − π^T A||_1 ≤ ||π||_1 ||Π A − A P||_∞
   + ||π^T Π − π^T||_1 ||A||_∞``,
  and if ``A`` is stochastic and ``π`` a probability vector:
  ``||π^T A P − π^T A||_1 ≤ ||Π A − A P||_∞ + ||π^T Π − π^T||_1``.

Norm convention (paper §2.1): vector ``||·||_1`` is the absolute sum;
matrix ``||·||_∞`` is the max absolute row sum. For two probability vectors,
total variation is ``TV = (1/2) ||·||_1``.

Compatibility with ``propagated_error_bound(delta_cl, k)`` from
``closure.core`` (CALL only; this module does not edit core.py):
that elementary bound is in **TV** on *projected* distributions with one-step
defect ``delta_cl = max_i TV((P C)_i, (C Q)_i)``. Michel–Siegle bounds are in
**L1** on the *full-state* error with residual ``||Π A − A P||_∞``. Norms,
residuals, and spaces therefore differ; when the residual is zero (dynamic-
exact aggregation, Def. 8 / Cor. 7) both give bound 0 for zero initial error.
See ``compare_to_propagated_error_bound`` and docs/error_bounds_core.md.

Scope of the transient bounds (Followup-Review-Fix R1/R2, 2026-10-01):
the reduced side (``A``, ``Π``/``Θ``, ``π_0``) may be general finite, but the
FULL dynamics must be a Markov chain -- ``P`` square row-stochastic,
``Q`` a square CTMC generator -- because the proofs use
``||x P||_1 ≤ ||x||_1`` resp. ``||x e^{Qt}||_1 ≤ ||x||_1``. Other inputs are
refused (``ScopeViolationError``); arbitrary full linear dynamics would need
additional amplification factors. ``norm="TV"`` additionally requires a
probability contract: stochastic lifting ``A``, probability vectors ``π_0``
and ``p_0`` and Markov reduced dynamics, so that both compared vectors are
probability distributions. The general CTMC branch uses
``φ(t, κ) = expm1(tκ)/κ`` with the continuous limit ``φ(t, 0) = t``
(no zero bound when the reduced dynamics vanish). Float evaluation, not an
interval-rigorous bound.

Does **not** import or mix with ``generator_lumpability`` (M11).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Sequence, Tuple, Union

import numpy as np

from scoped_correspondence.errors import ScopeViolationError

ArrayLike = Union[np.ndarray, Sequence[Sequence[float]], Sequence[float]]

SOURCE = (
    "Michel & Siegle, Formal Error Bounds for the State Space Reduction of "
    "Markov Chains, Performance Evaluation 2024; "
    "DOI 10.1016/j.peva.2024.102464; arXiv:2403.07618 (v3, 6 Aug 2024)"
)

# Paper theorem / equation tags used in ReductionErrorBound.theorem_ref
THM4_3 = "Theorem 4 (item 3) [arXiv:2403.07618]: ||e_k||_1 ≤ ||π0ᵀA−p0ᵀ||_1 + k·||ΠA−AP||_∞"
THM4_2 = "Theorem 4 (item 2) [arXiv:2403.07618]: geometric form with ||Π||_∞"
THM5_3 = "Theorem 5 (item 3) [arXiv:2403.07618]: ||e_t||_1 ≤ ||π0ᵀA−p0ᵀ||_1 + t·||ΘA−AQ||_∞"
THM5_2 = "Theorem 5 (item 2) [arXiv:2403.07618]: (e^{t||Θ||_∞}−1)/||Θ||_∞ form"
COR10 = (
    "Corollary 10 [arXiv:2403.07618]: "
    "||πᵀAP−πᵀA||_1 ≤ ||π||_1||ΠA−AP||_∞ + ||πᵀΠ−πᵀ||_1||A||_∞"
)
COR10_STOCH = (
    "Corollary 10 (stochastic A, probability π) [arXiv:2403.07618]: "
    "||πᵀAP−πᵀA||_1 ≤ ||ΠA−AP||_∞ + ||πᵀΠ−πᵀ||_1"
)


@dataclass(frozen=True)
class ReductionErrorBound:
    """Formal L1 (or TV) reduction error bound for a horizon.

    Attributes
    ----------
    horizon :
        Discrete steps ``k`` (DTMC) or continuous time ``t`` (CTMC).
        For stationary bounds, ``horizon`` is ``None`` (no time horizon).
    bound :
        Non-negative upper bound on ``||e||_1`` (or on TV if ``norm=="TV"``).
    norm :
        ``"L1"`` (paper default) or ``"TV"`` (= half L1 for probability diffs).
    theorem_ref :
        Concrete theorem / equation citation from Michel & Siegle 2024.
    assumptions :
        Stated hypotheses under which the cited formula applies.
    """

    horizon: Optional[float]
    bound: float
    norm: str
    theorem_ref: str
    assumptions: str


def _as_float_matrix(a: ArrayLike) -> np.ndarray:
    m = np.asarray(a, dtype=float)
    if m.ndim != 2:
        raise ScopeViolationError(f"expected 2D matrix, got shape {m.shape}")
    if not np.isfinite(m).all():
        raise ScopeViolationError("matrix must be finite")
    return m


def _as_float_vector(v: ArrayLike) -> np.ndarray:
    arr = np.asarray(v, dtype=float).reshape(-1)
    if arr.ndim != 1 or arr.size == 0:
        raise ScopeViolationError("expected non-empty 1D vector")
    if not np.isfinite(arr).all():
        raise ScopeViolationError("vector must be finite")
    return arr


def matrix_inf_norm(M: ArrayLike) -> float:
    """Matrix ∞-norm = max absolute row sum (Michel & Siegle §2.1)."""
    m = _as_float_matrix(M)
    return float(np.abs(m).sum(axis=1).max())


def vector_l1_norm(v: ArrayLike) -> float:
    """Vector L1 norm = sum of absolute entries (Michel & Siegle §2.1)."""
    return float(np.abs(_as_float_vector(v)).sum())


def is_row_stochastic(M: ArrayLike, tol: float = 1e-10) -> bool:
    """True iff all entries ≥ −tol and every row sums to 1 within tol."""
    m = _as_float_matrix(M)
    if (m < -tol).any():
        return False
    return bool(np.allclose(m.sum(axis=1), 1.0, atol=tol, rtol=0.0))


def is_probability_vector(v: ArrayLike, tol: float = 1e-10) -> bool:
    """True iff entries ≥ −tol and sum to 1 within tol."""
    arr = _as_float_vector(v)
    if (arr < -tol).any():
        return False
    return bool(abs(float(arr.sum()) - 1.0) <= tol)


def is_generator(M: ArrayLike, tol: float = 1e-10) -> bool:
    """True iff row sums ~0 and off-diagonal entries ≥ −tol (CTMC rate matrix)."""
    m = _as_float_matrix(M)
    if m.shape[0] != m.shape[1]:
        return False
    if not np.allclose(m.sum(axis=1), 0.0, atol=tol, rtol=0.0):
        return False
    off = m.copy()
    np.fill_diagonal(off, 0.0)
    if (off < -tol).any():
        return False
    return True


def dynamic_residual(Pi_or_Theta: ArrayLike, A: ArrayLike, P_or_Q: ArrayLike) -> np.ndarray:
    """Residual matrix ``Π A − A P`` (DTMC) or ``Θ A − A Q`` (CTMC).

    Zero residual ⇔ dynamic-exact aggregation (Def. 8 / Cor. 7).
    """
    red = _as_float_matrix(Pi_or_Theta)
    a = _as_float_matrix(A)
    full = _as_float_matrix(P_or_Q)
    if red.shape[1] != a.shape[0]:
        raise ScopeViolationError(
            f"reduced cols ({red.shape[1]}) must match A rows ({a.shape[0]})"
        )
    if a.shape[1] != full.shape[0] or full.shape[0] != full.shape[1]:
        raise ScopeViolationError(
            "A cols must match square full-chain dimension "
            f"(A={a.shape}, full={full.shape})"
        )
    if red.shape[0] != a.shape[0]:
        raise ScopeViolationError(
            f"reduced must be square m×m matching A rows; got {red.shape}, A={a.shape}"
        )
    return red @ a - a @ full


def residual_inf_norm(Pi_or_Theta: ArrayLike, A: ArrayLike, P_or_Q: ArrayLike) -> float:
    """``||Π A − A P||_∞`` or ``||Θ A − A Q||_∞`` (max abs row sum)."""
    return matrix_inf_norm(dynamic_residual(Pi_or_Theta, A, P_or_Q))


def initial_error_l1(pi0: ArrayLike, A: ArrayLike, p0: ArrayLike) -> float:
    """``||π_0^T A − p_0^T||_1`` (Michel & Siegle initial error)."""
    pi = _as_float_vector(pi0)
    a = _as_float_matrix(A)
    p = _as_float_vector(p0)
    if pi.shape[0] != a.shape[0]:
        raise ScopeViolationError("pi0 length must equal A rows (aggregated dim)")
    if p.shape[0] != a.shape[1]:
        raise ScopeViolationError("p0 length must equal A cols (full dim)")
    approx = pi @ a
    return vector_l1_norm(approx - p)


def _l1_bound_to_requested_norm(l1_bound: float, norm: str) -> float:
    if norm == "L1":
        return float(l1_bound)
    if norm == "TV":
        # For signed diffs of probability vectors: TV = (1/2) ||·||_1.
        return float(0.5 * l1_bound)
    raise ScopeViolationError(f"norm must be 'L1' or 'TV'; got {norm!r}")


def _require_markov_full(full: np.ndarray, continuous_time: bool) -> None:
    if full.shape[0] != full.shape[1]:
        raise ScopeViolationError(f"full dynamics must be square; got {full.shape}")
    if continuous_time:
        if not is_generator(full):
            raise ScopeViolationError(
                "full Q must be a CTMC generator (rows sum to 0, off-diagonal >= 0); "
                "the transient bound uses ||x e^{Qt}||_1 <= ||x||_1"
            )
    elif not is_row_stochastic(full):
        raise ScopeViolationError(
            "full P must be row-stochastic (row convention p_{k+1} = p_k P); "
            "the transient bound uses ||x P||_1 <= ||x||_1"
        )


def _require_tv_contract(red: np.ndarray, a: np.ndarray, pi: np.ndarray, p: np.ndarray,
                         continuous_time: bool) -> None:
    reduced_markov = is_generator(red) if continuous_time else is_row_stochastic(red)
    if not (is_row_stochastic(a) and is_probability_vector(pi) and is_probability_vector(p) and reduced_markov):
        raise ScopeViolationError(
            "norm='TV' needs a probability contract: row-stochastic A, probability "
            "vectors pi0 and p0, and Markov reduced dynamics; use norm='L1' for the "
            "general reduction"
        )


def _phi_ctmc(t: float, kappa: float) -> float:
    """int_0^t e^{kappa s} ds = expm1(t kappa)/kappa, continuous limit t at kappa = 0."""
    if kappa == 0.0:
        return float(t)
    return float(np.expm1(t * kappa) / kappa)


def _geom_dtmc(k: int, r: float) -> float:
    """sum_{j<k} r^j, evaluated without cancellation near r = 1."""
    if k == 0:
        return 0.0
    x = r - 1.0
    if x == 0.0:
        return float(k)
    if r == 0.0:
        return 1.0
    return float(np.expm1(k * np.log1p(x)) / x)


def transient_reduction_bound(
    Pi_or_Theta: ArrayLike,
    A: ArrayLike,
    P_or_Q: ArrayLike,
    pi0: ArrayLike,
    p0: ArrayLike,
    horizon: float,
    *,
    continuous_time: bool = False,
    norm: str = "L1",
) -> ReductionErrorBound:
    """L1 (or TV) transient reduction error bound — Theorems 4 / 5.

    Parameters
    ----------
    Pi_or_Theta :
        Aggregated step matrix ``Π`` (DTMC) or evolution matrix ``Θ`` (CTMC).
    A :
        Disaggregation matrix (paper's ``A``).
    P_or_Q :
        Full-chain transition matrix ``P`` or generator ``Q``.
    pi0, p0 :
        Aggregated / full initial vectors (row-vector convention in the paper;
        passed here as 1-D arrays).
    horizon :
        Integer steps ``k ≥ 0`` (DTMC) or time ``t ≥ 0`` (CTMC).
    continuous_time :
        If False, apply Theorem 4; if True, Theorem 5.
    norm :
        ``"L1"`` (paper) or ``"TV"`` (= half of the L1 bound).

    Notes
    -----
    Uses Theorem 4 item 3 / Theorem 5 item 3 when the stochastic / generator
    hypotheses hold; otherwise falls back to item 2 (geometric / exponential).
    Degenerate ``horizon == 0`` or zero residual → bound equals the initial
    error (0 when ``π_0^T A = p_0^T``).
    """
    if norm not in ("L1", "TV"):
        raise ScopeViolationError(f"norm must be 'L1' or 'TV'; got {norm!r}")
    if continuous_time:
        h = float(horizon)
        if not np.isfinite(h) or h < 0.0:
            raise ScopeViolationError(f"CTMC horizon t must be finite >= 0; got {horizon!r}")
    else:
        # Discrete steps: allow float equal to a non-negative integer.
        if isinstance(horizon, (float, np.floating)) and float(horizon) != int(horizon):
            raise ScopeViolationError(f"DTMC horizon k must be an integer >= 0; got {horizon!r}")
        h = int(horizon)
        if h < 0:
            raise ScopeViolationError(f"DTMC horizon k must be >= 0; got {horizon!r}")

    red = _as_float_matrix(Pi_or_Theta)
    a = _as_float_matrix(A)
    full = _as_float_matrix(P_or_Q)
    pi = _as_float_vector(pi0)
    p = _as_float_vector(p0)

    e0 = initial_error_l1(pi, a, p)
    r_inf = residual_inf_norm(red, a, full)
    _require_markov_full(full, continuous_time)
    if norm == "TV":
        _require_tv_contract(red, a, pi, p, continuous_time)
    pi_l1 = vector_l1_norm(pi)

    if continuous_time:
        if is_generator(red) and is_probability_vector(pi):
            # Theorem 5 item 3
            l1 = e0 + float(h) * r_inf
            return ReductionErrorBound(
                horizon=float(h),
                bound=_l1_bound_to_requested_norm(l1, norm),
                norm=norm,
                theorem_ref=THM5_3,
                assumptions=(
                    "Θ is a CTMC generator; π0 is a probability vector; "
                    "A arbitrary finite; full Q a CTMC generator (checked); bound on ||e_t||_1 (Thm 5.3)"
                ),
            )
        # Theorem 5 item 2
        theta_inf = matrix_inf_norm(red)
        # phi(t, 0) = t: vanishing reduced dynamics do NOT freeze the full chain
        l1 = e0 + pi_l1 * r_inf * _phi_ctmc(float(h), theta_inf)
        return ReductionErrorBound(
            horizon=float(h),
            bound=_l1_bound_to_requested_norm(float(l1), norm),
            norm=norm,
            theorem_ref=THM5_2,
            assumptions=(
                "general Θ (item 2); uses ||e^{Θu}||_∞ ≤ e^{u||Θ||_∞} (Lemma 2); "
                "full Q a CTMC generator (checked); bound on ||e_t||_1"
            ),
        )

    # Discrete time — Theorem 4
    k = int(h)
    if is_row_stochastic(red) and is_probability_vector(pi):
        # Theorem 4 item 3
        l1 = e0 + float(k) * r_inf
        return ReductionErrorBound(
            horizon=float(k),
            bound=_l1_bound_to_requested_norm(l1, norm),
            norm=norm,
            theorem_ref=THM4_3,
            assumptions=(
                "Π is row-stochastic; π0 is a probability vector; "
                "A arbitrary finite; full P row-stochastic (checked); bound on ||e_k||_1 (Thm 4.3)"
            ),
        )
    # Theorem 4 item 2
    pi_inf = matrix_inf_norm(red)
    geom = _geom_dtmc(k, pi_inf)
    l1 = e0 + pi_l1 * r_inf * geom
    return ReductionErrorBound(
        horizon=float(k),
        bound=_l1_bound_to_requested_norm(float(l1), norm),
        norm=norm,
        theorem_ref=THM4_2,
        assumptions=(
            "general Π (item 2); uses ||π_{k-1}||_1 ≤ ||π0||_1 ||Π||_∞^{k-1}; "
            "full P row-stochastic (checked); bound on ||e_k||_1"
        ),
    )


def stationary_reduction_bound(
    Pi: ArrayLike,
    A: ArrayLike,
    P: ArrayLike,
    pi: ArrayLike,
    *,
    norm: str = "L1",
) -> ReductionErrorBound:
    """Bound how far ``π^T A`` is from stationarity for ``P`` — Corollary 10.

    Returns an upper bound on ``||π^T A P − π^T A||_1`` (or its TV half).
    This measures distance-to-stationarity of the lifted stationary candidate,
    **not** ``||p − π^T A||_1`` to the true stationary law (see paper Remark
    after Cor. 10).

    Parameters
    ----------
    Pi, A, P :
        Aggregated step matrix, disaggregation, full transition matrix.
    pi :
        (Approximate) left eigenvector / stationary vector for ``Π``.
    norm :
        ``"L1"`` or ``"TV"``.
    """
    if norm not in ("L1", "TV"):
        raise ScopeViolationError(f"norm must be 'L1' or 'TV'; got {norm!r}")

    red = _as_float_matrix(Pi)
    a = _as_float_matrix(A)
    full = _as_float_matrix(P)
    piv = _as_float_vector(pi)
    if piv.shape[0] != red.shape[0]:
        raise ScopeViolationError("pi length must match Π dimension")

    r_inf = residual_inf_norm(red, a, full)
    # The L1 inequality is algebraic (πAP − πA = π(AP − ΠA) + (πΠ − π)A) and
    # holds for any finite matrices; only the TV reading needs both compared
    # vectors to be probability distributions.
    if norm == "TV" and not (is_row_stochastic(a) and is_probability_vector(piv) and is_row_stochastic(full)):
        raise ScopeViolationError(
            "norm='TV' needs row-stochastic A and P and a probability vector pi; use norm='L1'"
        )
    # ||π^T Π − π^T||_1
    pi_stat_defect = vector_l1_norm(piv @ red - piv)

    if is_row_stochastic(a) and is_probability_vector(piv):
        l1 = r_inf + pi_stat_defect
        return ReductionErrorBound(
            horizon=None,
            bound=_l1_bound_to_requested_norm(l1, norm),
            norm=norm,
            theorem_ref=COR10_STOCH,
            assumptions=(
                "A row-stochastic; π a probability vector; "
                "bound on ||πᵀ A P − πᵀ A||_1 (Cor. 10, stochastic case)"
            ),
        )

    pi_l1 = vector_l1_norm(piv)
    a_inf = matrix_inf_norm(a)
    l1 = pi_l1 * r_inf + pi_stat_defect * a_inf
    return ReductionErrorBound(
        horizon=None,
        bound=_l1_bound_to_requested_norm(l1, norm),
        norm=norm,
        theorem_ref=COR10,
        assumptions=(
            "general A, π (Cor. 10); bound on ||πᵀ A P − πᵀ A||_1"
        ),
    )


def compare_to_propagated_error_bound(
    michel_l1_bound: float,
    delta_cl: float,
    k: int,
) -> dict:
    """Compare Michel–Siegle L1 transient bound to ``propagated_error_bound``.

    Converts the Michel L1 bound to TV via ``TV = (1/2) L1`` and calls
    ``propagated_error_bound(delta_cl, k)`` from ``closure.core`` (compatibility
    only). Returns a dict with both values and an explanation when the
    inequality ``michel_tv ≤ propagated`` fails because norms/residuals differ.

    Parameters
    ----------
    michel_l1_bound :
        Bound on ``||e_k||_1`` from ``transient_reduction_bound`` (norm=L1).
    delta_cl :
        One-step closure defect as in ``closure_error`` / ``propagated_error_bound``.
    k :
        Discrete horizon (same ``k`` as in Theorem 4).
    """
    # CALL only — do not reimplement; keep core.py untouched.
    from scoped_correspondence.closure.core import propagated_error_bound

    if michel_l1_bound < 0:
        raise ScopeViolationError("michel_l1_bound must be >= 0")
    michel_tv = 0.5 * float(michel_l1_bound)
    elementary_tv = float(propagated_error_bound(float(delta_cl), int(k)))
    leq = michel_tv <= elementary_tv + 1e-12
    return {
        "michel_l1": float(michel_l1_bound),
        "michel_tv": michel_tv,
        "propagated_error_bound_tv": elementary_tv,
        "michel_tv_leq_propagated": leq,
        "note": (
            "Michel–Siegle: L1 on full-state error, residual ||ΠA−AP||_∞ "
            "(Thm 4). propagated_error_bound: TV on projected distributions, "
            "defect delta_cl = max_i TV((PC)_i,(CQ)_i). Different residuals/"
            "spaces; equality-to-zero when both residuals vanish (exact/"
            "dynamic-exact aggregation). Inequality michel_tv ≤ propagated "
            "is NOT guaranteed in general."
        ),
    }


def paper_example_matrices() -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Worked DTMC example from Michel & Siegle §3.4 / tightness discussion.

    Returns ``(P, A, Π)`` with ``||Π A − A P||_∞ = 1/4``::

        P = (1/4) · [[1,1,2],[1,2,1],[2,1,1]]
        A = [[1/2, 1/2, 0], [0, 0, 1]]
        Π = (1/8) · [[5, 3], [6, 2]]

    With ``π_0 = (1, 0)``, ``p_0 = π_0 A``, Theorem 4.3 gives
    ``||e_k||_1 ≤ k/4``.
    """
    P = (1.0 / 4.0) * np.array(
        [[1.0, 1.0, 2.0], [1.0, 2.0, 1.0], [2.0, 1.0, 1.0]], dtype=float
    )
    A = np.array([[0.5, 0.5, 0.0], [0.0, 0.0, 1.0]], dtype=float)
    Pi = (1.0 / 8.0) * np.array([[5.0, 3.0], [6.0, 2.0]], dtype=float)
    return P, A, Pi


__all__ = [
    "COR10",
    "COR10_STOCH",
    "SOURCE",
    "THM4_2",
    "THM4_3",
    "THM5_2",
    "THM5_3",
    "ReductionErrorBound",
    "compare_to_propagated_error_bound",
    "dynamic_residual",
    "initial_error_l1",
    "is_generator",
    "is_probability_vector",
    "is_row_stochastic",
    "matrix_inf_norm",
    "paper_example_matrices",
    "residual_inf_norm",
    "stationary_reduction_bound",
    "transient_reduction_bound",
    "vector_l1_norm",
]
