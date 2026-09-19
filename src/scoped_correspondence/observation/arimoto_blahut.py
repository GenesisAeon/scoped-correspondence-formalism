"""Arimoto–Blahut channel capacity for finite DMCs (Milestone 25).

Sources
-------
* Arimoto, S. (1972). An algorithm for computing the capacity of arbitrary
  discrete memoryless channels. *IEEE Trans. Inf. Theory* **18**(1):14–20.
  DOI: 10.1109/TIT.1972.1054753.
* Blahut, R. E. (1972). Computation of channel capacity and rate-distortion
  functions. *IEEE Trans. Inf. Theory* **18**(4):460–473.
  DOI: 10.1109/TIT.1972.1054855.

  (This module implements only the **channel-capacity** half of Blahut's
  alternating iteration. Rate-distortion is explicitly out of scope.)

Definition (exact construction)
-------------------------------
Let ``Q`` be an ``|X| × |Y|`` row-stochastic channel matrix
(``Q[x, y] = P(Y=y | X=x)``).  The Shannon capacity of the DMC is

    C(Q)  =  max_{r ∈ Δ^{|X|-1}}  I(r ; Q)
          =  max_r  Σ_x Σ_y  r(x) Q(y|x) log  ( Q(y|x) / Σ_{x'} r(x') Q(y|x') )

in bits when ``log = log2``.  The Arimoto–Blahut (BA) iteration alternates:

1. Forward: ``p_t(y) = Σ_x r_t(x) Q(y|x)``.
2. Divergence scores: ``D_t(x) = D(Q(·|x) ‖ p_t)`` (KL in the chosen base).
3. Update: ``r_{t+1}(x) ∝ r_t(x) · b^{D_t(x)}`` (``b = 2`` for bits), then
   renormalize; ``I(r_t; Q) = Σ_x r_t(x) D_t(x)`` increases monotonically to ``C``.

Hand-checkable closed forms (computed in verification, not hardcoded here)
--------------------------------------------------------------------------
* **Z-channel** ``ε = 1/2``: ``Q = [[1,0],[1/2,1/2]]``.
  ``C = log2(1 + 1/4) = log2(5/4) ≈ 0.321928``; capacity-achieving
  ``r* = (3/5, 2/5) = (0.6, 0.4)`` (from maximizing ``h(α/2) − α``).
* **BSC** ``p = 0.1``: ``C = 1 − H₂(0.1) ≈ 0.531004``; ``r*`` uniform.
  From a uniform start the BA fixed point is immediate (0 further updates
  beyond tolerance).

Relation to ``observation.core.channel_capacity``
-------------------------------------------------
``core.channel_capacity`` is the continuous Shannon–Hartley formula
``B log2(1 + SNR)``.  This module is an **additional** discrete-memoryless
channel (DMC) capacity model via BA iteration.  It is **not** the same
object, does **not** replace Shannon–Hartley, and does **not** edit
``observation/core.py`` or package-root ``__init__.py``.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, Optional, Sequence, Tuple, Union

import numpy as np

from scoped_correspondence.errors import ScopeViolationError

SOURCE_ARIMOTO = (
    "Arimoto, S. (1972). An algorithm for computing the capacity of arbitrary "
    "discrete memoryless channels. IEEE Trans. Inf. Theory 18(1):14–20. "
    "DOI: 10.1109/TIT.1972.1054753."
)
SOURCE_BLAHUT = (
    "Blahut, R. E. (1972). Computation of channel capacity and rate-distortion "
    "functions. IEEE Trans. Inf. Theory 18(4):460–473. "
    "DOI: 10.1109/TIT.1972.1054855."
)
SOURCE = f"{SOURCE_ARIMOTO} | {SOURCE_BLAHUT}"

_EPS = 1e-15
_STOCHASTIC_ATOL = 1e-9
_MAX_ALPHABET = 256


ArrayLike = Union[np.ndarray, Sequence[Sequence[float]], Sequence[float]]


@dataclass(frozen=True)
class ArimotoBlahutResult:
    """Capacity and capacity-achieving input from Arimoto–Blahut iteration.

    Attributes
    ----------
    capacity :
        Estimated channel capacity ``C`` in bits (``log_base=2``) or nats
        (``log_base=e``).
    r_star :
        Capacity-achieving input distribution (probability vector over ``X``).
    iterations :
        Number of BA updates performed until ``|C_{t+1} − C_t| ≤ tol``
        (or ``max_iter``).
    mutual_information :
        ``I(r_star; Q)`` at termination (should match ``capacity``).
    converged :
        ``True`` if the tolerance criterion was met.
    log_base :
        Information unit base used (``2`` → bits).
    """

    capacity: float
    r_star: Tuple[float, ...]
    iterations: int
    mutual_information: float
    converged: bool
    log_base: float

    def as_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _as_channel_matrix(Q: ArrayLike) -> np.ndarray:
    try:
        arr = np.asarray(Q, dtype=float)
    except (TypeError, ValueError) as exc:
        raise ScopeViolationError(
            f"blahut_arimoto_capacity: Q must be array-like; got {type(Q)!r}"
        ) from exc
    if arr.ndim != 2:
        raise ScopeViolationError(
            f"blahut_arimoto_capacity: Q must be 2-D (|X|×|Y|); got shape {arr.shape!r}"
        )
    n_x, n_y = arr.shape
    if n_x < 1 or n_y < 1:
        raise ScopeViolationError(
            f"blahut_arimoto_capacity: Q must have positive dimensions; got {arr.shape!r}"
        )
    if n_x > _MAX_ALPHABET or n_y > _MAX_ALPHABET:
        raise ScopeViolationError(
            f"blahut_arimoto_capacity: alphabet size exceeds MAX={_MAX_ALPHABET}; "
            f"got shape {arr.shape!r}"
        )
    if not np.all(np.isfinite(arr)):
        raise ScopeViolationError(
            "blahut_arimoto_capacity: Q entries must be finite"
        )
    if np.any(arr < -_EPS):
        raise ScopeViolationError(
            "blahut_arimoto_capacity: Q must be non-negative (no negative "
            f"transition probabilities); min entry={float(arr.min())!r}"
        )
    # Clamp tiny numerical negatives to 0 after the check above.
    arr = np.maximum(arr, 0.0)
    row_sums = arr.sum(axis=1)
    if np.any(row_sums <= _EPS):
        raise ScopeViolationError(
            "blahut_arimoto_capacity: each row of Q must sum to 1 "
            f"(row-stochastic); got row sums={row_sums!r}"
        )
    if not np.allclose(row_sums, 1.0, atol=_STOCHASTIC_ATOL, rtol=0.0):
        raise ScopeViolationError(
            "blahut_arimoto_capacity: Q must be row-stochastic "
            f"(each row sums to 1 ± {_STOCHASTIC_ATOL}); got row sums={row_sums!r}"
        )
    # Renormalize tiny drift so probabilities are exact.
    return arr / row_sums[:, np.newaxis]


def _as_input_distribution(
    r: Optional[ArrayLike], n_x: int
) -> np.ndarray:
    if r is None:
        return np.full(n_x, 1.0 / n_x, dtype=float)
    try:
        vec = np.asarray(r, dtype=float).reshape(-1)
    except (TypeError, ValueError) as exc:
        raise ScopeViolationError(
            f"blahut_arimoto_capacity: r0 must be array-like; got {type(r)!r}"
        ) from exc
    if vec.shape != (n_x,):
        raise ScopeViolationError(
            f"blahut_arimoto_capacity: r0 length must equal |X|={n_x}; "
            f"got shape {vec.shape!r}"
        )
    if not np.all(np.isfinite(vec)):
        raise ScopeViolationError(
            "blahut_arimoto_capacity: r0 entries must be finite"
        )
    if np.any(vec < -_EPS):
        raise ScopeViolationError(
            "blahut_arimoto_capacity: r0 must be non-negative; "
            f"min={float(vec.min())!r}"
        )
    vec = np.maximum(vec, 0.0)
    s = float(vec.sum())
    if s <= _EPS:
        raise ScopeViolationError(
            "blahut_arimoto_capacity: r0 must be a probability vector "
            f"(positive mass); sum={s!r}"
        )
    if not np.isclose(s, 1.0, atol=_STOCHASTIC_ATOL, rtol=0.0):
        raise ScopeViolationError(
            "blahut_arimoto_capacity: r0 must sum to 1; "
            f"got sum={s!r}"
        )
    return vec / s


def mutual_information_dmc(
    r: ArrayLike,
    Q: ArrayLike,
    *,
    log_base: float = 2.0,
) -> float:
    """I(X;Y) for input ``r`` and row-stochastic DMC ``Q`` (bits if base 2)."""
    Qm = _as_channel_matrix(Q)
    rm = _as_input_distribution(r, Qm.shape[0])
    if log_base <= 0 or not np.isfinite(log_base):
        raise ScopeViolationError(
            f"mutual_information_dmc: log_base must be > 0; got {log_base!r}"
        )
    if np.isclose(log_base, 2.0):
        log_fn = np.log2
    elif np.isclose(log_base, np.e):
        log_fn = np.log
    else:
        log_fn = lambda z: np.log(z) / np.log(log_base)  # noqa: E731

    p = rm @ Qm
    D = _kl_rows(Qm, p, log_fn)
    return float(np.dot(rm, D))


def _kl_rows(Q: np.ndarray, p: np.ndarray, log_fn) -> np.ndarray:
    """Row-wise KL D(Q(·|x) ‖ p); 0 log 0 := 0."""
    p_safe = np.where(p > _EPS, p, 1.0)  # unused where Q==0
    out = np.zeros(Q.shape[0], dtype=float)
    for x in range(Q.shape[0]):
        qx = Q[x]
        s = 0.0
        for y in range(Q.shape[1]):
            qxy = float(qx[y])
            if qxy <= _EPS:
                continue
            py = float(p[y])
            if py <= _EPS:
                # Mass escapes to a zero-probability output: treat as +inf KL
                # contribution; BA will drive such inputs to zero mass.
                s = float("inf")
                break
            s += qxy * float(log_fn(qxy / py))
        out[x] = s
    return out


def blahut_arimoto_capacity(
    Q: ArrayLike,
    *,
    r0: Optional[ArrayLike] = None,
    tol: float = 1e-12,
    max_iter: int = 10_000,
    log_base: float = 2.0,
) -> ArimotoBlahutResult:
    """Arimoto–Blahut iteration for DMC capacity ``C(Q)`` and ``r*``.

    Parameters
    ----------
    Q :
        Row-stochastic channel matrix ``Q[x, y] = P(Y=y|X=x)``.  Negatives
        or non-row-stochastic rows raise ``ScopeViolationError``.
    r0 :
        Optional starting input distribution.  Default: uniform on ``X``.
    tol :
        Stop when ``|I_{t+1} − I_t| ≤ tol``.
    max_iter :
        Hard iteration cap.
    log_base :
        ``2`` → bits (default); ``e`` → nats.

    Returns
    -------
    ArimotoBlahutResult
        ``capacity`` (``C``), ``r_star`` (``r*``), ``iterations``, etc.

    Notes
    -----
    This is an additional finite-DMC capacity model.  It is **not** the
    Shannon–Hartley ``observation.core.channel_capacity(B, snr)``.
    Rate-distortion BA is **not** implemented.
    """
    Qm = _as_channel_matrix(Q)
    n_x, _n_y = Qm.shape
    r = _as_input_distribution(r0, n_x)

    if not (isinstance(tol, (int, float)) and float(tol) > 0):
        raise ScopeViolationError(
            f"blahut_arimoto_capacity: tol must be > 0; got {tol!r}"
        )
    if not (isinstance(max_iter, int) and max_iter >= 1):
        raise ScopeViolationError(
            f"blahut_arimoto_capacity: max_iter must be >= 1; got {max_iter!r}"
        )
    if log_base <= 0 or not np.isfinite(log_base):
        raise ScopeViolationError(
            f"blahut_arimoto_capacity: log_base must be > 0; got {log_base!r}"
        )

    if np.isclose(log_base, 2.0):
        log_fn = np.log2
        exp_fn = lambda d: np.power(2.0, d)  # noqa: E731
    elif np.isclose(log_base, np.e):
        log_fn = np.log
        exp_fn = np.exp
    else:
        log_fn = lambda z: np.log(z) / np.log(log_base)  # noqa: E731
        exp_fn = lambda d: np.power(log_base, d)  # noqa: E731

    I_prev = None
    converged = False
    iterations = 0
    I_cur = 0.0

    for t in range(max_iter):
        p = r @ Qm
        D = _kl_rows(Qm, p, log_fn)
        D_safe = np.where(np.isfinite(D), D, 0.0)
        I_cur = float(np.dot(r, D_safe))  # I(r_t; Q); monotone nondecreasing

        # Finite scores only; infinite D ⇒ zero weight after update.
        finite = np.isfinite(D)
        scores = np.zeros_like(D)
        scores[finite] = exp_fn(D[finite])
        weights = r * scores
        wsum = float(weights.sum())
        if wsum <= _EPS:
            raise ScopeViolationError(
                "blahut_arimoto_capacity: BA update produced zero mass "
                "(degenerate channel / output support)"
            )
        r_new = weights / wsum
        iterations = t + 1

        r_delta = float(np.max(np.abs(r_new - r)))
        fixed = r_delta <= max(float(tol), 1e-14)
        delta_ok = (
            I_prev is not None
            and abs(I_cur - I_prev) <= float(tol)
            and r_delta <= max(float(tol) * 10.0, 1e-12)
        )

        r = r_new
        if fixed or delta_ok:
            # Recompute I at the updated distribution for reporting.
            p2 = r @ Qm
            D2 = _kl_rows(Qm, p2, log_fn)
            I_cur = float(np.dot(r, np.where(np.isfinite(D2), D2, 0.0)))
            converged = True
            break
        I_prev = I_cur
    else:
        p = r @ Qm
        D = _kl_rows(Qm, p, log_fn)
        I_cur = float(np.dot(r, np.where(np.isfinite(D), D, 0.0)))
        converged = False

    # Final tidy: clip tiny negatives from float noise and renormalize.
    r = np.maximum(r, 0.0)
    r = r / r.sum()
    p = r @ Qm
    D = _kl_rows(Qm, p, log_fn)
    I_final = float(np.dot(r, np.where(np.isfinite(D), D, 0.0)))

    return ArimotoBlahutResult(
        capacity=I_final,
        r_star=tuple(float(x) for x in r),
        iterations=int(iterations),
        mutual_information=I_final,
        converged=bool(converged),
        log_base=float(log_base),
    )


def z_channel(epsilon: float) -> np.ndarray:
    """Binary Z-channel: ``Y=0`` if ``X=0``; if ``X=1``, flip to 0 w.p. ``ε``.

    Matrix rows ``X∈{0,1}``, columns ``Y∈{0,1}``::

        Q = [[1, 0], [ε, 1-ε]]
    """
    eps = float(epsilon)
    if not (0.0 <= eps <= 1.0):
        raise ScopeViolationError(
            f"z_channel: epsilon must be in [0,1]; got {eps!r}"
        )
    return np.array([[1.0, 0.0], [eps, 1.0 - eps]], dtype=float)


def bsc_channel(p: float) -> np.ndarray:
    """Binary symmetric channel with crossover ``p``.

        Q = [[1-p, p], [p, 1-p]]
    """
    pv = float(p)
    if not (0.0 <= pv <= 1.0):
        raise ScopeViolationError(
            f"bsc_channel: p must be in [0,1]; got {pv!r}"
        )
    return np.array([[1.0 - pv, pv], [pv, 1.0 - pv]], dtype=float)


def binary_entropy(p: float) -> float:
    """Binary entropy ``H₂(p)`` in bits (same convention as M22)."""
    pv = float(p)
    if not (0.0 <= pv <= 1.0):
        raise ScopeViolationError(
            f"binary_entropy: p must be in [0,1]; got {pv!r}"
        )
    if pv <= _EPS or pv >= 1.0 - _EPS:
        return 0.0
    return float(-pv * np.log2(pv) - (1.0 - pv) * np.log2(1.0 - pv))


def z_channel_capacity_closed_form(epsilon: float) -> Tuple[float, Tuple[float, float]]:
    """Closed-form Z-channel capacity and ``r*`` (bits).

    For ``ε ∈ (0,1)``::

        β = (1-ε) · ε^{ε/(1-ε)}
        C = log2(1 + β)

    Capacity-achieving ``α* = P(X=1)`` from the critical point of
    ``f(α) = H₂(α(1-ε)) − α H₂(ε)``::

        γ* = P(Y=1) = 1 / (1 + 2^{H₂(ε)/(1-ε)})
        α* = γ* / (1-ε)
        r* = (1-α*, α*)

    Special case M25: ``ε=1/2`` ⇒ ``C=log2(5/4)``, ``r*=(0.6,0.4)``.
    """
    eps = float(epsilon)
    if not (0.0 < eps < 1.0):
        raise ScopeViolationError(
            f"z_channel_capacity_closed_form: need ε∈(0,1); got {eps!r}"
        )
    # β = (1-ε) ε^{ε/(1-ε)}
    beta = (1.0 - eps) * (eps ** (eps / (1.0 - eps)))
    C = float(np.log2(1.0 + beta))
    # Capacity-achieving P(X=1)=α* from critical point of
    # f(α)=H₂(α(1-ε)) − α H₂(ε):
    # (1-ε) log2((1-α(1-ε))/(α(1-ε))) = H₂(ε)
    # ⇒ (1-α(1-ε))/(α(1-ε)) = 2^{H₂(ε)/(1-ε)}
    # ⇒ α = 1 / ((1-ε) (1 + 2^{H₂(ε)/(1-ε)}))? Let's derive carefully.
    #
    # Let γ = α(1-ε) = P(Y=1).  Then
    # f = H₂(γ) − (γ/(1-ε)) H₂(ε)
    # f'(γ)=0 ⇒ log2((1-γ)/γ) = H₂(ε)/(1-ε)
    # ⇒ (1-γ)/γ = 2^{H₂(ε)/(1-ε)}
    # ⇒ 1/γ − 1 = 2^{H₂(ε)/(1-ε)}
    # ⇒ γ* = 1 / (1 + 2^{H₂(ε)/(1-ε)})
    # ⇒ α* = γ*/(1-ε)
    H = binary_entropy(eps)
    gamma_star = 1.0 / (1.0 + (2.0 ** (H / (1.0 - eps))))
    alpha_star = gamma_star / (1.0 - eps)
    # Sanity: for ε=1/2, H=1, γ*=1/(1+2^2)=1/5=0.2, α*=0.4; C=log2(1.25).
    r_star = (float(1.0 - alpha_star), float(alpha_star))
    return C, r_star


__all__ = [
    "SOURCE",
    "SOURCE_ARIMOTO",
    "SOURCE_BLAHUT",
    "ArimotoBlahutResult",
    "blahut_arimoto_capacity",
    "mutual_information_dmc",
    "z_channel",
    "bsc_channel",
    "binary_entropy",
    "z_channel_capacity_closed_form",
]
