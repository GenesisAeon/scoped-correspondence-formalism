"""Directed information I(X^n → Y^n) (Milestone 22).

Sources
-------
* Massey, J. L. (1990). Causality, feedback and directed information.
  In *Proc. Int. Symp. Inf. Theory Appl. (ISITA)*, pp. 303–305.
* Permuter, H. H., Weissman, T. & Goldsmith, A. J. (2009).
  Finite state channels with time-invariant deterministic feedback.
  *IEEE Trans. Inf. Theory* **55**(2):644–662.

Definition (exact construction)
-------------------------------
For jointly distributed discrete sequences ``X^n = (X_1,...,X_n)`` and
``Y^n = (Y_1,...,Y_n)``,

    I(X^n → Y^n)  :=  Σ_{i=1}^{n}  I(X^i ; Y_i | Y^{i-1})

with the convention ``Y^{0} = ∅`` so the i=1 term is ``I(X_1; Y_1)``.
Each summand is a conditional mutual information and is therefore ≥ 0.
The total satisfies Massey's inequality

    I(X^n → Y^n)  ≤  I(X^n ; Y^n),

with equality if and only if there is no feedback in the sense that
``X_{i+1} — X^i — Y^i`` (equivalently: the input process is causally
conditionally independent of past outputs).  With nontrivial feedback the
inequality is typically strict.

BSC example (hand-checkable; binary entropy H(p))
-------------------------------------------------
Binary symmetric channel ``Y_i = X_i ⊕ Z_i``, ``Z_i ~ Bern(p)`` i.i.d.,
``H(p) = -p log2(p) - (1-p) log2(1-p)``.

* **With feedback (n=2):** ``X_1 ~ Bern(1/2)``, ``X_2 := Y_1`` (encoder
  uses the previous output).  Then

      I(X^2 → Y^2) = 1 - H(p) ,   I(X^2 ; Y^2) = 1 ,

  so ``I_dir < I_mutual`` for ``p ∈ (0, 1/2)``.  Summands:
  ``I(X_1;Y_1)=1-H(p)``, ``I(X^2;Y_2|Y_1)=0``.

* **Without feedback (n=2):** ``X_i`` i.i.d. Bern(1/2), independent of
  past ``Y``.  Then ``I_dir = I_mutual = 2(1-H(p))`` to machine precision.

Scope (M22)
-----------
Finite discrete alphabets, finite horizon ``n``.  No continuous-time
directed information.  Directed information is **not** identified with
``EI_q`` or PID atoms (those live under ``information_decomposition``;
this module does not import or equate them).  Does **not** edit
``observation/core.py`` or package-root ``__init__.py``.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict, dataclass
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple, Union

import math

from scoped_correspondence.errors import ScopeViolationError

SOURCE_MASSEY = (
    "Massey, J. L. (1990). Causality, feedback and directed information. "
    "Proc. ISITA, pp. 303–305."
)
SOURCE_PERMUTE = (
    "Permuter, H. H., Weissman, T. & Goldsmith, A. J. (2009). "
    "Finite state channels with time-invariant deterministic feedback. "
    "IEEE Trans. Inf. Theory 55(2):644–662."
)
SOURCE = f"{SOURCE_MASSEY} | {SOURCE_PERMUTE}"

JointSequences = Mapping[Tuple[Tuple[int, ...], Tuple[int, ...]], float]
_EPS = 1e-15
_MAX_N = 12
_MAX_SUPPORT = 4096


def binary_entropy(p: float) -> float:
    """Binary entropy H(p) in bits; hand-checkable for rational p.

    H(p) = -p log2(p) - (1-p) log2(1-p), with H(0)=H(1)=0.
    Example: H(1/4) = 2 - (3/4) log2(3) ≈ 0.811278124459.
    """
    p = float(p)
    if not (0.0 <= p <= 1.0):
        raise ScopeViolationError(
            f"binary_entropy: p must be in [0,1]; got {p!r}"
        )
    if p <= _EPS or p >= 1.0 - _EPS:
        return 0.0
    return float(-p * math.log2(p) - (1.0 - p) * math.log2(1.0 - p))


def _normalize_joint(joint: JointSequences) -> Dict[
    Tuple[Tuple[int, ...], Tuple[int, ...]], float
]:
    if not isinstance(joint, Mapping) or len(joint) == 0:
        raise ScopeViolationError(
            "directed_information: joint_sequences must be a non-empty "
            "mapping ((x_1..x_n), (y_1..y_n)) -> probability"
        )
    if len(joint) > _MAX_SUPPORT:
        raise ScopeViolationError(
            f"directed_information: joint support {len(joint)} exceeds "
            f"MAX_SUPPORT={_MAX_SUPPORT}"
        )
    out: Dict[Tuple[Tuple[int, ...], Tuple[int, ...]], float] = {}
    total = 0.0
    n_ref: Optional[int] = None
    for key, mass in joint.items():
        if (
            not isinstance(key, tuple)
            or len(key) != 2
            or not isinstance(key[0], tuple)
            or not isinstance(key[1], tuple)
        ):
            raise ScopeViolationError(
                "directed_information: keys must be "
                "((x_1,...,x_n), (y_1,...,y_n)); "
                f"got {key!r}"
            )
        xs, ys = key
        if len(xs) != len(ys):
            raise ScopeViolationError(
                "directed_information: |X^n| and |Y^n| lengths must match; "
                f"got n_x={len(xs)}, n_y={len(ys)}"
            )
        n = len(xs)
        if n < 1 or n > _MAX_N:
            raise ScopeViolationError(
                f"directed_information: require 1 <= n <= {_MAX_N}; got n={n}"
            )
        if n_ref is None:
            n_ref = n
        elif n != n_ref:
            raise ScopeViolationError(
                "directed_information: inconsistent sequence length across "
                f"atoms; saw n={n_ref} and n={n}"
            )
        m = float(mass)
        # Followup-Review-Fix R4: NaN fails both comparisons below and would be
        # dropped silently; non-finite masses are invalid, not "zero weight".
        if not math.isfinite(m):
            raise ScopeViolationError(
                f"directed_information: non-finite mass {m!r} at {key!r}"
            )
        if m < -_EPS:
            raise ScopeViolationError(
                f"directed_information: negative mass {m!r} at {key!r}"
            )
        if m > _EPS:
            out[(tuple(int(v) for v in xs), tuple(int(v) for v in ys))] = (
                out.get(
                    (tuple(int(v) for v in xs), tuple(int(v) for v in ys)), 0.0
                )
                + m
            )
            total += m
    if not math.isfinite(total):
        raise ScopeViolationError(
            "directed_information: total mass overflows (non-finite sum of finite weights)"
        )
    if total <= _EPS:
        raise ScopeViolationError(
            "directed_information: joint_sequences has total mass ≈ 0"
        )
    return {k: v / total for k, v in out.items()}


def _entropy_of_counter(counter: Mapping[Any, float]) -> float:
    total = float(sum(counter.values()))
    if total <= _EPS:
        return 0.0
    h = 0.0
    for m in counter.values():
        if m > _EPS:
            q = m / total
            h -= q * math.log2(q)
    return float(h)


def _marginal(
    joint: Mapping[Tuple[Tuple[int, ...], Tuple[int, ...]], float],
    which: str,
) -> Dict[Any, float]:
    """Marginal over selected coordinates.

    which ∈ {"x", "y", "xy", "x_prefix:i", "y_prefix:i", "y_i",
             "x_prefix_y_prefix:i", "x_prefix_y_i_y_prefix:i"}
    """
    c: Dict[Any, float] = defaultdict(float)
    for (xs, ys), m in joint.items():
        if which == "x":
            key: Any = xs
        elif which == "y":
            key = ys
        elif which == "xy":
            key = (xs, ys)
        elif which.startswith("x_prefix:"):
            i = int(which.split(":")[1])
            key = xs[:i]
        elif which.startswith("y_prefix:"):
            i = int(which.split(":")[1])
            key = ys[:i] if i > 0 else ()
        elif which.startswith("y_at:"):
            i = int(which.split(":")[1])
            key = ys[i - 1]
        elif which.startswith("x_prefix_y_prefix:"):
            i = int(which.split(":")[1])
            key = (xs[:i], ys[: i - 1] if i > 1 else ())
        elif which.startswith("y_i_y_prefix:"):
            i = int(which.split(":")[1])
            key = (ys[i - 1], ys[: i - 1] if i > 1 else ())
        elif which.startswith("x_prefix_y_i_y_prefix:"):
            i = int(which.split(":")[1])
            key = (xs[:i], ys[i - 1], ys[: i - 1] if i > 1 else ())
        else:
            raise ScopeViolationError(f"unknown marginal selector {which!r}")
        c[key] += m
    return dict(c)


def conditional_mutual_information_summand(
    joint: JointSequences, i: int
) -> float:
    """Compute I(X^i ; Y_i | Y^{i-1}) from a joint over (X^n, Y^n).

    Uses the entropy identity
        I(A;B|C) = H(A,C) + H(B,C) - H(C) - H(A,B,C)
    with A=X^i, B=Y_i, C=Y^{i-1}.
    """
    j = _normalize_joint(joint)
    n = len(next(iter(j))[0])
    if not (1 <= i <= n):
        raise ScopeViolationError(
            f"summand index i must satisfy 1 <= i <= n={n}; got {i}"
        )
    # H(X^i, Y^{i-1})
    h_ac = _entropy_of_counter(_marginal(j, f"x_prefix_y_prefix:{i}"))
    # H(Y_i, Y^{i-1})
    h_bc = _entropy_of_counter(_marginal(j, f"y_i_y_prefix:{i}"))
    # H(Y^{i-1})
    h_c = (
        _entropy_of_counter(_marginal(j, f"y_prefix:{i - 1}"))
        if i > 1
        else 0.0
    )
    # H(X^i, Y_i, Y^{i-1})
    h_abc = _entropy_of_counter(_marginal(j, f"x_prefix_y_i_y_prefix:{i}"))
    val = h_ac + h_bc - h_c - h_abc
    return float(max(0.0, val))  # clip tiny negative FP


def mutual_information_sequences(joint: JointSequences) -> float:
    """I(X^n ; Y^n) = H(X^n) + H(Y^n) - H(X^n, Y^n)."""
    j = _normalize_joint(joint)
    hx = _entropy_of_counter(_marginal(j, "x"))
    hy = _entropy_of_counter(_marginal(j, "y"))
    hxy = _entropy_of_counter(_marginal(j, "xy"))
    return float(max(0.0, hx + hy - hxy))


@dataclass(frozen=True)
class DirectedInformationReport:
    """Report for I(X^n → Y^n) vs I(X^n; Y^n)."""

    I_directed: float
    I_mutual: float
    summands: Tuple[float, ...]
    n: int
    method: str = "massey_directed_information"
    source: str = SOURCE
    input_mode: str = "weights"
    input_total_mass: Optional[float] = None  # total of the masses as passed (before normalisation)

    def as_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["summands"] = list(self.summands)
        return d

    @property
    def gap(self) -> float:
        """I_mutual - I_directed (≥ 0 by Massey)."""
        return float(self.I_mutual - self.I_directed)


PMF_TOL = 1e-12
INPUT_MODES = ("weights", "pmf")


def _input_total(joint: JointSequences, input_mode: str):
    """Total mass as passed; in ``pmf`` mode it must be 1 -- EXACTLY for
    int/Fraction masses, within ``PMF_TOL`` (math.fsum) for floats."""
    from fractions import Fraction

    if input_mode not in INPUT_MODES:
        raise ScopeViolationError(f"directed_information: input_mode must be one of {INPUT_MODES}; got {input_mode!r}")
    masses = list(joint.values())
    exact = all(isinstance(m, (int, Fraction)) and not isinstance(m, bool) for m in masses)
    total = sum(Fraction(m) for m in masses) if exact else math.fsum(float(m) for m in masses)
    if input_mode == "pmf":
        if exact and total != 1:
            raise ScopeViolationError(f"directed_information: input_mode='pmf' needs exact total mass 1; got {total}")
        if not exact and abs(total - 1.0) > PMF_TOL:
            raise ScopeViolationError(
                f"directed_information: input_mode='pmf' needs total mass 1 within {PMF_TOL}; got {total!r} "
                "(use input_mode='weights' for unnormalised weights)"
            )
    return float(total)


def directed_information(
    joint_sequences: JointSequences,
    *,
    input_mode: str = "weights",
) -> DirectedInformationReport:
    """Compute I(X^n → Y^n) = Σ_i I(X^i ; Y_i | Y^{i-1}).

    Parameters
    ----------
    joint_sequences:
        Mapping from ``((x_1,...,x_n), (y_1,...,y_n))`` to probability mass
        (renormalised if needed).  Finite discrete alphabets only.

    Returns
    -------
    DirectedInformationReport
        ``I_directed``, ``I_mutual``, per-step ``summands``, horizon ``n``.

    Notes
    -----
    This is Massey directed information.  It is **not** the same formula as
    ``EI_q`` or PID unique/redundancy/synergy atoms; those are separate
    constructions under ``information_decomposition`` and are not linked here.

    ``input_mode`` (2026-10-01, recommendation of SCF_FOLLOWUP_REVIEW_637bc1c):
    ``"weights"`` (default, unchanged) renormalises finite non-negative
    weights -- scaling all weights by one positive factor leaves the result
    unchanged; ``"pmf"`` requires a probability distribution (exact total 1 for
    int/Fraction masses, ``|total - 1| <= PMF_TOL`` for floats) and refuses
    anything else. Both modes refuse non-finite and negative masses. Within the
    float tolerance the masses are renormalised technically; the original
    total is reported as ``input_total_mass``.
    """
    j = _normalize_joint(joint_sequences)  # validates finiteness, sign, keys
    total_in = _input_total(joint_sequences, input_mode)
    n = len(next(iter(j))[0])
    summands = tuple(
        conditional_mutual_information_summand(j, i) for i in range(1, n + 1)
    )
    for k, s in enumerate(summands, start=1):
        if s < -1e-12:
            raise ScopeViolationError(
                f"directed_information: summand i={k} is negative: {s!r}"
            )
    i_dir = float(sum(summands))
    i_mut = mutual_information_sequences(j)
    # Massey: I_dir <= I_mut (allow tiny FP slack)
    if i_dir > i_mut + 1e-9:
        raise ScopeViolationError(
            f"directed_information: Massey violated: I_dir={i_dir} > "
            f"I_mutual={i_mut}"
        )
    return DirectedInformationReport(
        I_directed=i_dir,
        I_mutual=i_mut,
        summands=summands,
        n=n,
        input_mode=input_mode,
        input_total_mass=total_in,
    )


def bsc_feedback_joint(p: float, n: int = 2) -> JointSequences:
    """Joint PMF for BSC(p) with the feedback encoder X_i := Y_{i-1} (i≥2).

    Exact construction
    ------------------
    * ``X_1 ~ Bern(1/2)`` independent of noises.
    * ``Z_i ~ Bern(p)`` i.i.d., independent of ``X_1``.
    * Channel: ``Y_i = X_i ⊕ Z_i``.
    * Feedback law: ``X_i = Y_{i-1}`` for ``i = 2,...,n``
      (deterministic use of the previous output).

    For ``n=2`` this yields the hand-checkable identities
    ``I_dir = 1 - H(p)``, ``I_mutual = 1``.
    """
    p = float(p)
    if not (0.0 <= p <= 1.0):
        raise ScopeViolationError(f"bsc_feedback_joint: p in [0,1]; got {p!r}")
    if n not in (2, 3):
        raise ScopeViolationError(
            "bsc_feedback_joint: M22 ships n=2 or n=3 only; "
            f"got n={n}"
        )
    joint: Dict[Tuple[Tuple[int, ...], Tuple[int, ...]], float] = defaultdict(
        float
    )

    def noise_prob(z: int) -> float:
        return p if z == 1 else (1.0 - p)

    # Enumerate X1 and all Z^n
    from itertools import product

    for x1 in (0, 1):
        for zs in product((0, 1), repeat=n):
            xs = [0] * n
            ys = [0] * n
            xs[0] = x1
            ys[0] = xs[0] ^ zs[0]
            mass = 0.5 * math.prod(noise_prob(z) for z in zs)
            for i in range(1, n):
                xs[i] = ys[i - 1]  # feedback
                ys[i] = xs[i] ^ zs[i]
            key = (tuple(xs), tuple(ys))
            joint[key] += mass
    return dict(joint)


def bsc_no_feedback_joint(p: float, n: int = 2) -> JointSequences:
    """Joint PMF for BSC(p) with open-loop i.i.d. Bern(1/2) inputs (no feedback).

    Exact construction
    ------------------
    * ``X_i`` i.i.d. Bern(1/2), independent of all ``Z_j`` and past ``Y``.
    * ``Z_i ~ Bern(p)`` i.i.d.
    * ``Y_i = X_i ⊕ Z_i``.

    Then ``I(X^n → Y^n) = I(X^n ; Y^n) = n (1 - H(p))`` (equality to
    machine precision).
    """
    p = float(p)
    if not (0.0 <= p <= 1.0):
        raise ScopeViolationError(
            f"bsc_no_feedback_joint: p in [0,1]; got {p!r}"
        )
    if n not in (2, 3):
        raise ScopeViolationError(
            "bsc_no_feedback_joint: M22 ships n=2 or n=3 only; "
            f"got n={n}"
        )
    from itertools import product

    joint: Dict[Tuple[Tuple[int, ...], Tuple[int, ...]], float] = defaultdict(
        float
    )

    def noise_prob(z: int) -> float:
        return p if z == 1 else (1.0 - p)

    for xs in product((0, 1), repeat=n):
        for zs in product((0, 1), repeat=n):
            ys = tuple(xs[i] ^ zs[i] for i in range(n))
            mass = (0.5**n) * math.prod(noise_prob(z) for z in zs)
            joint[(xs, ys)] += mass
    return dict(joint)


def bsc_feedback_vs_mutual(
    p: float = 0.25, n: int = 2
) -> Dict[str, Any]:
    """Side-by-side BSC reports: feedback (strict inequality) vs no-feedback.

    Default ``p=1/4`` so ``H(p)`` is hand-checkable:
    ``H(1/4) = 2 - (3/4) log2(3)``.
    """
    hp = binary_entropy(p)
    fb = directed_information(bsc_feedback_joint(p, n=n))
    no = directed_information(bsc_no_feedback_joint(p, n=n))
    return {
        "p": p,
        "n": n,
        "H_p": hp,
        "with_feedback": fb.as_dict(),
        "without_feedback": no.as_dict(),
        "analytic_n2_feedback": {
            "I_directed": 1.0 - hp if n == 2 else None,
            "I_mutual": 1.0 if n == 2 else None,
            "note": "n=2 identities: I_dir=1-H(p), I_mut=1",
        },
        "analytic_no_feedback": {
            "I_directed": n * (1.0 - hp),
            "I_mutual": n * (1.0 - hp),
        },
        "source": SOURCE,
    }


__all__ = [
    "SOURCE",
    "SOURCE_MASSEY",
    "SOURCE_PERMUTE",
    "DirectedInformationReport",
    "binary_entropy",
    "bsc_feedback_joint",
    "bsc_feedback_vs_mutual",
    "bsc_no_feedback_joint",
    "conditional_mutual_information_summand",
    "directed_information",
    "mutual_information_sequences",
]
