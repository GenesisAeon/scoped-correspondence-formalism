"""GENERIC ↔ Navier–Stokes viscous dissipation (Milestone 38).

Two-cell finite-dimensional reduction of viscous momentum exchange with
GENERIC friction matrix ``M = ζ T a aᵀ``.

**Important:** ``M`` here is the GENERIC *friction* / dissipative metric
operator. It is **NOT** ``A_ij`` (local dynamic influence) and **NOT**
``L_ij`` (Onsager transport). Those remain separate types in
``coupling.core`` (FORMALISM.md §6).

Sources
-------
- Grmela & Öttinger, Phys. Rev. E **56**, 6620 (1997),
  DOI 10.1103/PhysRevE.56.6620 — GENERIC formalism (Part I).
- Öttinger & Grmela, Phys. Rev. E **56**, 6633 (1997),
  DOI 10.1103/PhysRevE.56.6633 — GENERIC illustrations (Part II).
  *Do NOT claim the APS abstracts of these papers are Navier–Stokes*;
  they introduce GENERIC structure. The NS/viscous link is pedagogical
  via the discrete two-cell example below and/or:
- Morrison, Phys. Lett. A **100**, 423 (1984),
  DOI 10.1016/0375-9601(84)90635-2 — bracket formulation for irreversible
  classical fields (metriplectic / NS dissipation ancestry).
- Barham, Morrison & Zaidni, Commun. Nonlinear Sci. Numer. Simul. **145**,
  108683 (2025), DOI 10.1016/j.cnsns.2025.108683 — thermodynamically
  consistent 1D thermal-fluid / Navier–Stokes–Fourier metriplectic
  discretization (NS link).

Calls ``coupling.core.check_generic_structure`` — does **not** reimplement
or edit ``coupling/core.py``. Package-root ``__init__`` untouched.
"""

from __future__ import annotations

from typing import Any, Dict, Mapping, Sequence, Tuple, Union

import numpy as np

from scoped_correspondence.coupling.core import check_generic_structure
from scoped_correspondence.errors import ScopeViolationError

ArrayLike = Union[Sequence[float], np.ndarray]

SOURCE = (
    "Grmela & Öttinger PRE 56 6620 (DOI 10.1103/PhysRevE.56.6620) & "
    "Öttinger & Grmela PRE 56 6633 (DOI 10.1103/PhysRevE.56.6633) "
    "[GENERIC itself; APS abstracts are NOT claimed to be NS]; "
    "Morrison 1984 DOI 10.1016/0375-9601(84)90635-2; "
    "Barham–Morrison–Zaidni 2025 DOI 10.1016/j.cnsns.2025.108683 "
    "[NS / metriplectic thermal-fluid link]"
)

GRMELA_OTTINGER_I_DOI = "10.1103/PhysRevE.56.6620"
OTTINGER_GRMELA_II_DOI = "10.1103/PhysRevE.56.6633"
MORRISON_1984_DOI = "10.1016/0375-9601(84)90635-2"
BARHAM_MORRISON_ZAIDNI_2025_DOI = "10.1016/j.cnsns.2025.108683"

# Illustrative continuum viscosity → discrete ζ only (NOT a calibration).
# ζ = η A / Δy with η = 0.005 Pa·s is documented as illustrative only.
ILLUSTRATIVE_ETA_PA_S: float = 0.005
ILLUSTRATIVE_ZETA_NOTE = (
    "η = 0.005 Pa·s via ζ = η A / Δy is ILLUSTRATIVE ONLY — "
    "not an empirical calibration of the two-cell toy."
)

FRICTION_NOT_AIJ_LIJ_WARNING = (
    "M is GENERIC friction (dissipative metric), NOT A_ij and NOT L_ij "
    "(FORMALISM.md §6; no shared base)."
)

_DEFAULT_ASSUMPTIONS: Tuple[str, ...] = (
    "finite-dimensional two-cell viscous exchange; NOT continuum NS PDE solver",
    "J = 0 (purely dissipative toy); reversible Euler/pressure block omitted",
    "M = ζ T a aᵀ is GENERIC friction — NOT A_ij, NOT L_ij",
    "η = 0.005 Pa·s ↔ ζ = η A / Δy is illustrative only",
    "structure via CALL to check_generic_structure (core.py unchanged)",
    "Grmela/Öttinger PRE abstracts are GENERIC, not claimed to be NS",
)


def _as_float(name: str, value: float) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError) as exc:
        raise ScopeViolationError(
            f"two_cell_viscous_example: {name} must be float-convertible"
        ) from exc
    if not np.isfinite(out):
        raise ScopeViolationError(
            f"two_cell_viscous_example: {name} must be finite; got {out}"
        )
    return out


def two_cell_viscous_example(
    v1: float,
    v2: float,
    T: float,
    zeta: float,
) -> Dict[str, Any]:
    """Build the two-cell GENERIC viscous example and structure-check it.

    State ordering ``x = (p1, p2, e1, e2)`` (momenta + internal energies).
    Velocities ``v1, v2`` enter the degeneracy vector and energy gradient.

    Constructs
    ----------
    - ``a = (1, -1, -v1, v2)``
    - ``∇E = (v1, v2, 1, 1)``
    - ``∇S = (0, 0, 1/T, 1/T)``
    - ``J = 0`` (4×4)
    - ``M = ζ T a aᵀ``  — GENERIC **friction**, not A_ij / L_ij

    Then **calls** ``check_generic_structure(J, M, ∇E, ∇S)``.

    Hand-check (v1=3, v2=1, T=300, ζ=0.5)
    --------------------------------------
    - ``a · ∇E = 0``
    - ``M ∇S = -a = (-1, 1, 3, -1)``
    - ``ṗ1 = -ζ (v1 - v2) = -1``
    - entropy production ``ζ (v1 - v2)² / T = 0.0066…``
    - control ``v1 = v2`` ⇒ ``M ∇S = 0``

    Parameters
    ----------
    v1, v2 :
        Cell velocities.
    T :
        Absolute temperature (same in both cells for this toy); must be > 0.
    zeta :
        Discrete friction coefficient (≥ 0). Continuum illustration:
        ``ζ = η A / Δy`` with ``η = 0.005 Pa·s`` is **illustrative only**.
    """
    v1 = _as_float("v1", v1)
    v2 = _as_float("v2", v2)
    T = _as_float("T", T)
    zeta = _as_float("zeta", zeta)
    if T <= 0.0:
        raise ScopeViolationError(
            f"two_cell_viscous_example: T must be > 0; got {T}"
        )
    if zeta < 0.0:
        raise ScopeViolationError(
            f"two_cell_viscous_example: zeta must be ≥ 0; got {zeta}"
        )

    a = np.array([1.0, -1.0, -v1, v2], dtype=float)
    grad_E = np.array([v1, v2, 1.0, 1.0], dtype=float)
    grad_S = np.array([0.0, 0.0, 1.0 / T, 1.0 / T], dtype=float)
    J = np.zeros((4, 4), dtype=float)
    # M = ζ T a aᵀ — GENERIC friction (NOT A_ij, NOT L_ij)
    M = (zeta * T) * np.outer(a, a)

    a_dot_grad_E = float(np.dot(a, grad_E))
    M_grad_S = M @ grad_S
    M_grad_E = M @ grad_E
    # Irreversible rates: ẋ = J ∇E + M ∇S = M ∇S
    x_dot = M_grad_S.copy()
    p1_dot = float(x_dot[0])  # = -ζ (v1 - v2)
    expected_p1_dot = -zeta * (v1 - v2)
    # Entropy production σ = ∇S · M ∇S = ζ (v1 - v2)² / T
    entropy_production = float(grad_S @ M_grad_S)
    expected_entropy_production = zeta * (v1 - v2) ** 2 / T

    structure = check_generic_structure(J, M, grad_E, grad_S)

    return {
        "v1": v1,
        "v2": v2,
        "T": T,
        "zeta": zeta,
        "a": a,
        "grad_E": grad_E,
        "grad_S": grad_S,
        "J": J,
        "M": M,
        "a_dot_grad_E": a_dot_grad_E,
        "M_grad_S": M_grad_S,
        "M_grad_E": M_grad_E,
        "x_dot": x_dot,
        "p1_dot": p1_dot,
        "expected_p1_dot": expected_p1_dot,
        "entropy_production": entropy_production,
        "expected_entropy_production": expected_entropy_production,
        "structure": structure,
        "friction_not_aij_lij": FRICTION_NOT_AIJ_LIJ_WARNING,
        "illustrative_eta_note": ILLUSTRATIVE_ZETA_NOTE,
        "illustrative_eta_Pa_s": ILLUSTRATIVE_ETA_PA_S,
        "source": SOURCE,
        "assumptions": list(_DEFAULT_ASSUMPTIONS),
    }


def as_report(example: Mapping[str, Any]) -> Dict[str, Any]:
    """JSON-serializable summary of a ``two_cell_viscous_example`` result."""
    structure = example["structure"]
    residuals = structure.get("residuals", {})

    def _list(x: Any) -> Any:
        arr = np.asarray(x, dtype=float)
        if arr.ndim == 0:
            return float(arr)
        return arr.tolist()

    return {
        "v1": float(example["v1"]),
        "v2": float(example["v2"]),
        "T": float(example["T"]),
        "zeta": float(example["zeta"]),
        "a": _list(example["a"]),
        "grad_E": _list(example["grad_E"]),
        "grad_S": _list(example["grad_S"]),
        "J": _list(example["J"]),
        "M": _list(example["M"]),
        "a_dot_grad_E": float(example["a_dot_grad_E"]),
        "M_grad_S": _list(example["M_grad_S"]),
        "M_grad_E": _list(example["M_grad_E"]),
        "x_dot": _list(example["x_dot"]),
        "p1_dot": float(example["p1_dot"]),
        "expected_p1_dot": float(example["expected_p1_dot"]),
        "entropy_production": float(example["entropy_production"]),
        "expected_entropy_production": float(
            example["expected_entropy_production"]
        ),
        "structure_ok": bool(structure.get("ok")),
        "structure_flags": {
            k: bool(structure[k])
            for k in (
                "J_antisymmetric",
                "M_symmetric",
                "M_psd",
                "J_grad_S_zero",
                "M_grad_E_zero",
            )
            if k in structure
        },
        "residuals": {k: float(v) for k, v in residuals.items()},
        "friction_not_aij_lij": example["friction_not_aij_lij"],
        "illustrative_eta_note": example["illustrative_eta_note"],
        "illustrative_eta_Pa_s": float(example["illustrative_eta_Pa_s"]),
        "source": example["source"],
        "assumptions": list(example["assumptions"]),
        "disclaimer": structure.get("disclaimer", ""),
    }


__all__ = [
    "BARHAM_MORRISON_ZAIDNI_2025_DOI",
    "FRICTION_NOT_AIJ_LIJ_WARNING",
    "GRMELA_OTTINGER_I_DOI",
    "ILLUSTRATIVE_ETA_PA_S",
    "ILLUSTRATIVE_ZETA_NOTE",
    "MORRISON_1984_DOI",
    "OTTINGER_GRMELA_II_DOI",
    "SOURCE",
    "as_report",
    "two_cell_viscous_example",
]
