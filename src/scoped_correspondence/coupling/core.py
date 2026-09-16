"""Coupling formulas: pairwise additive coupling, A_ij, L_ij, GENERIC structure.

FORMALISM.md §6 / coupling_layer_afet.md.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, Mapping, Optional, Sequence, Tuple

import numpy as np

from scoped_correspondence.errors import ScopeViolationError

# Default absolute tolerance for GENERIC structure equalities / PSD margin.
# Documented: structure check only; never claims an arbitrary model is GENERIC.
GENERIC_STRUCTURE_TOL: float = 1e-10

State = float
VectorField1 = Callable[[State, Optional[float]], float]
CouplingTerm = Callable[[State, State, Optional[float]], float]


@dataclass
class PairwiseCoupling:
    """Pairwise additive coupling (FORMALISM.md §6):

        dot z_i = f_i(z_i, u_i) + sum_{j != i} g_ij(z_i, z_j, u)

    Local maps ``f`` and pairwise maps ``g`` are callables; this type does not
    assert thermodynamics or GENERIC structure by itself.
    """

    f: Mapping[str, VectorField1]
    g: Mapping[Tuple[str, str], CouplingTerm] = field(default_factory=dict)
    names: Sequence[str] = ()

    def __post_init__(self) -> None:
        if not self.names:
            object.__setattr__(self, "names", tuple(self.f.keys()))
        missing = [n for n in self.names if n not in self.f]
        if missing:
            raise ScopeViolationError(
                f"PairwiseCoupling: missing local fields for {missing}"
            )

    def rhs(
        self,
        state: Mapping[str, float],
        controls: Optional[Mapping[str, float]] = None,
        u_shared: Optional[float] = None,
    ) -> Dict[str, float]:
        """Evaluate dot z_i for each named component."""
        controls = controls or {}
        out: Dict[str, float] = {}
        for i in self.names:
            zi = float(state[i])
            ui = controls.get(i)
            total = float(self.f[i](zi, ui))
            for j in self.names:
                if j == i:
                    continue
                key = (i, j)
                if key in self.g:
                    total += float(self.g[key](zi, float(state[j]), u_shared))
            out[i] = total
        return out


@dataclass(frozen=True)
class AijInfluence:
    """Local dynamic influence A_ij ≈ ∂f_i / ∂z_j.

    FORMALISM.md §2 row ``A_ij``: unit [z_i]/([z_j]·Zeit).
    Distinct from ``LijTransport`` — no shared base (FORMALISM.md §6).
    """

    matrix: np.ndarray
    state_names: Tuple[str, ...] = ()
    unit_note: str = "[z_i]/([z_j]*time)"

    def __post_init__(self) -> None:
        object.__setattr__(self, "matrix", np.asarray(self.matrix, dtype=float))
        if self.matrix.ndim != 2 or self.matrix.shape[0] != self.matrix.shape[1]:
            raise ScopeViolationError(
                f"AijInfluence: matrix must be square; got shape {self.matrix.shape}"
            )

    @property
    def n(self) -> int:
        return int(self.matrix.shape[0])


@dataclass(frozen=True)
class LijTransport:
    """Linear thermodynamic transport coefficients L_ij with J = L X.

    FORMALISM.md §2 row ``L_ij``: unit [J_i]/[X_j].
    Distinct from ``AijInfluence`` — no shared base (FORMALISM.md §6).
    Entropy production X^T L X uses the symmetric part L_s = (L+L^T)/2.
    """

    matrix: np.ndarray
    force_names: Tuple[str, ...] = ()
    unit_note: str = "[J_i]/[X_j]"

    def __post_init__(self) -> None:
        object.__setattr__(self, "matrix", np.asarray(self.matrix, dtype=float))
        if self.matrix.ndim != 2 or self.matrix.shape[0] != self.matrix.shape[1]:
            raise ScopeViolationError(
                f"LijTransport: matrix must be square; got shape {self.matrix.shape}"
            )

    @property
    def n(self) -> int:
        return int(self.matrix.shape[0])

    def symmetric_part(self) -> np.ndarray:
        L = self.matrix
        return 0.5 * (L + L.T)

    def flux(self, forces: Sequence[float]) -> np.ndarray:
        return self.matrix @ np.asarray(forces, dtype=float)

    def entropy_production(self, forces: Sequence[float]) -> float:
        X = np.asarray(forces, dtype=float)
        return float(X @ self.matrix @ X)


def check_generic_structure(
    J: np.ndarray,
    M: np.ndarray,
    grad_E: Sequence[float],
    grad_S: Sequence[float],
    *,
    tol: float = GENERIC_STRUCTURE_TOL,
) -> dict:
    """Check GENERIC structural conditions (coupling_layer_afet.md §8).

    Requires:
      - J^T = -J  (antisymmetric)
      - M^T = M and M >= 0 (symmetric positive semidefinite)
      - J @ grad_S == 0
      - M @ grad_E == 0

    This is a **structure check only**. Passing does not claim that an
    arbitrary coupling model *is* GENERIC (no microscopic derivation, no
    Jacobi identity verification beyond the antisymmetry of J, no claim of
    empirical calibration). Numeric tolerance defaults to
    ``GENERIC_STRUCTURE_TOL`` (= 1e-10 absolute).

    Returns a dict with boolean flags and measured residuals.
    """
    J = np.asarray(J, dtype=float)
    M = np.asarray(M, dtype=float)
    gE = np.asarray(grad_E, dtype=float).ravel()
    gS = np.asarray(grad_S, dtype=float).ravel()

    if J.shape != M.shape or J.ndim != 2 or J.shape[0] != J.shape[1]:
        raise ScopeViolationError(
            f"check_generic_structure: J and M must be square and same shape; "
            f"got J={J.shape}, M={M.shape}"
        )
    n = J.shape[0]
    if gE.shape != (n,) or gS.shape != (n,):
        raise ScopeViolationError(
            f"check_generic_structure: grad_E/grad_S length must match n={n}"
        )

    anti_res = float(np.max(np.abs(J.T + J)))
    sym_res = float(np.max(np.abs(M.T - M)))
    eig_min = float(np.linalg.eigvalsh(0.5 * (M + M.T)).min()) if n else 0.0
    j_gs = float(np.max(np.abs(J @ gS)))
    m_ge = float(np.max(np.abs(M @ gE)))

    report = {
        "J_antisymmetric": anti_res <= tol,
        "M_symmetric": sym_res <= tol,
        "M_psd": eig_min >= -tol,
        "J_grad_S_zero": j_gs <= tol,
        "M_grad_E_zero": m_ge <= tol,
        "tol": tol,
        "residuals": {
            "max_abs_J_T_plus_J": anti_res,
            "max_abs_M_T_minus_M": sym_res,
            "min_eig_M_sym": eig_min,
            "max_abs_J_grad_S": j_gs,
            "max_abs_M_grad_E": m_ge,
        },
        "disclaimer": (
            "Structure check only; does not assert that the coupling model "
            "is GENERIC (FORMALISM.md §6 / coupling_layer_afet.md §8)."
        ),
    }
    report["ok"] = all(
        report[k]
        for k in (
            "J_antisymmetric",
            "M_symmetric",
            "M_psd",
            "J_grad_S_zero",
            "M_grad_E_zero",
        )
    )
    return report


__all__ = [
    "AijInfluence",
    "GENERIC_STRUCTURE_TOL",
    "LijTransport",
    "PairwiseCoupling",
    "check_generic_structure",
]
