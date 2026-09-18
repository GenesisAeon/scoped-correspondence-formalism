"""Čech cohomology witness for contextuality (Milestone 24).

Abramsky / Mansfield / Barbosa 2012, arXiv:1111.3620 — relative Čech
obstruction of the support of an empirical model, specialized to
coefficient ring Z_2 (= GF(2)).

Semantics (AMB Prop. 4.5 / §8):
  * Non-vanishing obstruction ⇒ sufficient for contextuality
    (``proves_contextuality = obstruction_nonzero``).
  * Vanishing obstruction does **not** certify noncontextuality
    (Hardy-type false positives; never invert the witness).

Does **not** ship a general cohomology library. Does **not** mutate
``contextuality/core.py`` or ``csw.py`` — only *calls* EmpiricalModel
builders / ``contextual_fraction``. Does **not** equate CF with any
Čech invariant as "the same number".
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Iterable, Sequence

import numpy as np

from scoped_correspondence.contextuality.core import EmpiricalModel

ARXIV = "https://arxiv.org/abs/1111.3620"
SOURCE = (
    "Abramsky/Mansfield/Barbosa 2012 — The Cohomology of Non-Locality "
    "and Contextuality (arXiv:1111.3620)"
)
COEFFICIENT_RING = "Z_2"
DEGREE = 1  # relative H^1 obstruction class γ(s)
SUPPORT_TOL = 1e-12


# ---------------------------------------------------------------------------
# GF(2) linear algebra (specialized; not a general cohomology library)
# ---------------------------------------------------------------------------

def _gf2_rank(A: np.ndarray) -> int:
    """Row-reduce A over GF(2); return rank. A is modified in place."""
    if A.size == 0:
        return 0
    A = A % 2
    m, n = A.shape
    rank = 0
    row = 0
    for col in range(n):
        pivot = None
        for r in range(row, m):
            if A[r, col] % 2 == 1:
                pivot = r
                break
        if pivot is None:
            continue
        if pivot != row:
            A[[row, pivot]] = A[[pivot, row]]
        for r in range(m):
            if r != row and A[r, col] % 2 == 1:
                A[r, :] = (A[r, :] + A[row, :]) % 2
        rank += 1
        row += 1
        if row >= m:
            break
    return rank


def _gf2_solve(A: np.ndarray, b: np.ndarray) -> bool:
    """Return True iff A x = b is solvable over GF(2)."""
    A = np.asarray(A, dtype=np.int8) % 2
    b = np.asarray(b, dtype=np.int8).reshape(-1) % 2
    if A.ndim != 2:
        raise ValueError("A must be 2-D")
    m, n = A.shape
    if b.shape[0] != m:
        raise ValueError("b length mismatch")
    if m == 0:
        return True
    Aug = np.concatenate([A, b.reshape(-1, 1)], axis=1) % 2
    rank_A = _gf2_rank(A.copy())
    rank_Aug = _gf2_rank(Aug.copy())
    return rank_Aug == rank_A


# ---------------------------------------------------------------------------
# Support extraction
# ---------------------------------------------------------------------------

def _section_tuple(sec_key) -> tuple:
    """Normalize a table key ((m,o), ...) to a sorted tuple."""
    return tuple(sorted((m, int(o)) for m, o in sec_key))


def _restrict(section: tuple, subset: Sequence[str]) -> tuple:
    d = dict(section)
    return tuple(sorted((m, d[m]) for m in subset))


def _support_tables(model: EmpiricalModel, tol: float = SUPPORT_TOL) -> dict[tuple, list[tuple]]:
    """Map context → list of supported local sections (sorted tuples)."""
    out: dict[tuple, list[tuple]] = {}
    for ctx in model.scenario.contexts:
        key = tuple(ctx)
        tab = model.tables[key]
        secs = [_section_tuple(sk) for sk, p in tab.items() if float(p) > tol]
        secs.sort()
        out[key] = secs
    return out


# ---------------------------------------------------------------------------
# Relative Z_2 Čech obstruction (AMB §4, specialized to GF(2))
# ---------------------------------------------------------------------------

def _variable_index(support: dict[tuple, list[tuple]]) -> dict[tuple, int]:
    """Map (context, section) → column index."""
    idx: dict[tuple, int] = {}
    for ctx, secs in support.items():
        for s in secs:
            idx[(ctx, s)] = len(idx)
    return idx


def _compatibility_rows(
    support: dict[tuple, list[tuple]],
    var_index: dict[tuple, int],
) -> list[np.ndarray]:
    """Build δ⁰-style compatibility constraint rows over GF(2).

    For each unordered pair of contexts with nonempty intersection U, and each
    local assignment t on U that appears as a restriction of some supported
    section, enforce

        ∑_{s|U=t} x_{C_i,s}  =  ∑_{s|U=t} x_{C_j,s}   (mod 2).
    """
    contexts = list(support.keys())
    n = len(var_index)
    rows: list[np.ndarray] = []
    for i in range(len(contexts)):
        for j in range(i + 1, len(contexts)):
            ci, cj = contexts[i], contexts[j]
            inter = tuple(sorted(set(ci) & set(cj)))
            if not inter:
                continue
            # collect all t appearing from either side
            t_set: set[tuple] = set()
            for s in support[ci]:
                t_set.add(_restrict(s, inter))
            for s in support[cj]:
                t_set.add(_restrict(s, inter))
            for t in sorted(t_set):
                row = np.zeros(n, dtype=np.int8)
                for s in support[ci]:
                    if _restrict(s, inter) == t:
                        row[var_index[(ci, s)]] ^= 1
                for s in support[cj]:
                    if _restrict(s, inter) == t:
                        row[var_index[(cj, s)]] ^= 1
                if np.any(row):
                    rows.append(row)
    return rows


def _obstruction_vanishes_for_section(
    support: dict[tuple, list[tuple]],
    var_index: dict[tuple, int],
    rows: list[np.ndarray],
    ctx0: tuple,
    s0: tuple,
) -> bool:
    """AMB Prop. 4.3 over GF(2): fix r_{C0}=s0 (pure) and ask solvability.

    Fix x_{C0,s0}=1 and x_{C0,s}=0 for other supported sections in C0; solve
    the remaining compatibility equations for the free variables.
    """
    n = len(var_index)
    fixed = {var_index[(ctx0, s)]: (1 if s == s0 else 0) for s in support[ctx0]}
    free_cols = [c for c in range(n) if c not in fixed]
    if not rows:
        # no constraints: only need fixed assignment consistent with itself
        return True
    A_full = np.stack(rows, axis=0) % 2  # (m, n)
    b = np.zeros(A_full.shape[0], dtype=np.int8)
    # move fixed columns to RHS: A_free x_free = b - A_fixed x_fixed
    for col, val in fixed.items():
        if val:
            b = (b + A_full[:, col]) % 2
    if not free_cols:
        return bool(np.all(b % 2 == 0))
    A_free = A_full[:, free_cols]
    return _gf2_solve(A_free, b)


def _cech_obstruction_z2(model: EmpiricalModel) -> dict[str, Any]:
    """Compute relative Z_2 Čech obstruction diagnostics for ``model``."""
    support = _support_tables(model)
    var_index = _variable_index(support)
    rows = _compatibility_rows(support, var_index)
    if rows:
        A = np.stack(rows, axis=0) % 2
        coboundary_rank = _gf2_rank(A.copy())
    else:
        coboundary_rank = 0

    per_section: list[dict[str, Any]] = []
    n_nonzero = 0
    for ctx, secs in support.items():
        for s in secs:
            vanishes = _obstruction_vanishes_for_section(
                support, var_index, rows, ctx, s
            )
            if not vanishes:
                n_nonzero += 1
            per_section.append(
                {
                    "context": ctx,
                    "section": s,
                    "obstruction_vanishes": bool(vanishes),
                }
            )

    n_sections = len(per_section)
    # Sufficient condition: some local section has non-vanishing γ(s).
    obstruction_nonzero = n_nonzero > 0
    return {
        "obstruction_nonzero": bool(obstruction_nonzero),
        "obstruction_vanishes": not obstruction_nonzero,
        "degree": DEGREE,
        "coefficient_ring": COEFFICIENT_RING,
        "n_support_sections": n_sections,
        "n_sections_with_nonzero_obstruction": n_nonzero,
        "n_variables": len(var_index),
        "n_compatibility_constraints": len(rows),
        "coboundary_rank": int(coboundary_rank),
        "per_section": per_section,
        "arxiv": ARXIV,
        "source": SOURCE,
    }


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class CohomologyWitness:
    """Čech-cohomology contextuality witness (one-way implication only).

    ``proves_contextuality`` equals ``obstruction_nonzero`` and is **never**
    obtained by inverting a vanishing obstruction. Vanishing does **not**
    certify noncontextuality (AMB §8 / Hardy false positives).
    """

    obstruction_nonzero: bool
    degree: int
    coefficient_ring: str
    proves_contextuality: bool
    coboundary_rank: int
    n_support_sections: int
    n_sections_with_nonzero_obstruction: int
    arxiv: str = ARXIV
    source: str = SOURCE

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def cech_obstruction(model: EmpiricalModel) -> dict[str, Any]:
    """Z_2 relative Čech obstruction of ``model`` (AMB 2012).

    Intended for ``bell_222_scenario`` EmpiricalModels built via core helpers
    (``classical_factorizable_model``, ``pr_box_model``, …). Returns a dict
    including ``obstruction_nonzero``, ``coboundary_rank`` (GF(2) rank of the
    compatibility / coboundary constraint matrix), and per-section diagnostics.

    Does **not** claim noncontextuality when the obstruction vanishes.
    """
    if not isinstance(model, EmpiricalModel):
        raise TypeError("cech_obstruction expects an EmpiricalModel")
    return _cech_obstruction_z2(model)


def cech_witness(model: EmpiricalModel) -> CohomologyWitness:
    """Build a :class:`CohomologyWitness` from ``cech_obstruction(model)``.

    ``proves_contextuality`` is set **only** from ``obstruction_nonzero``
    (never ``not obstruction_vanishes`` as a certificate of noncontextuality —
    those are logically dual phrasings only when the implication is two-sided,
    which it is not).
    """
    ob = cech_obstruction(model)
    nonzero = bool(ob["obstruction_nonzero"])
    # CRITICAL: one-way only — do not invert vanishing into "noncontextual".
    proves = nonzero
    return CohomologyWitness(
        obstruction_nonzero=nonzero,
        degree=int(ob["degree"]),
        coefficient_ring=str(ob["coefficient_ring"]),
        proves_contextuality=proves,
        coboundary_rank=int(ob["coboundary_rank"]),
        n_support_sections=int(ob["n_support_sections"]),
        n_sections_with_nonzero_obstruction=int(
            ob["n_sections_with_nonzero_obstruction"]
        ),
    )


def report(model: EmpiricalModel) -> dict[str, Any]:
    """Bundle obstruction + witness fields (no CF identification)."""
    ob = cech_obstruction(model)
    w = cech_witness(model)
    return {
        **{k: ob[k] for k in (
            "obstruction_nonzero",
            "obstruction_vanishes",
            "degree",
            "coefficient_ring",
            "coboundary_rank",
            "n_support_sections",
            "n_sections_with_nonzero_obstruction",
            "n_variables",
            "n_compatibility_constraints",
            "arxiv",
            "source",
        )},
        "proves_contextuality": w.proves_contextuality,
        "witness": w.as_dict(),
    }


__all__ = [
    "ARXIV",
    "COEFFICIENT_RING",
    "DEGREE",
    "SOURCE",
    "SUPPORT_TOL",
    "CohomologyWitness",
    "cech_obstruction",
    "cech_witness",
    "report",
]
