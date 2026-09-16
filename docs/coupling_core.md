# Coupling Core (Milestone 2 - review package)

**Status:** review package only - not yet linked from README/GLOSSARY as accepted "core".
Johann-OK required before any core promotion.

## What this is

Python APIs for the coupling layer (ex-AFET): pairwise additive coupling,
separate A_ij / L_ij types, and a GENERIC **structure** check.

```text
src/scoped_correspondence/
  coupling/
    __init__.py
    core.py
  legacy/            # historical AFET names
```

## Mapping to FORMALISM.md section 2

| section-2 symbol | API | Notes |
|---|---|---|
| `A_ij` | `AijInfluence` | Local dynamic influence; unit [z_i]/([z_j]*time) |
| `L_ij` | `LijTransport` | Thermodynamic transport; unit [J_i]/[X_j] |
| (pairwise form) | `PairwiseCoupling` | z_dot_i = f_i + sum g_ij (FORMALISM.md section 6) |
| GENERIC ops | `check_generic_structure(J, M, grad_E, grad_S)` | Structure only |

## No shared base for A_ij and L_ij

FORMALISM.md section 6: there is **no general identity** between eta_info, Panarchy,
A_ij and L_ij. `AijInfluence` and `LijTransport` are separate frozen
dataclasses with **no shared project base class**.

## GENERIC tolerance

`GENERIC_STRUCTURE_TOL = 1e-10` (absolute) for:
J^T=-J, M^T=M, M psd, J grad_S = 0, M grad_E = 0.

Passing the check does **not** claim an arbitrary coupling model is GENERIC
(no microscopic derivation, no full Jacobi-identity proof, no calibration claim).

## Equivalence verification

`verification/verify_coupling_core.py` matches **p06_heat_balance_and_relaxation**
from `verify_formalism.py` exactly (equilibrium, transverse rate, trajectory
J/X/L/entropy production).

## Legacy adapters

`afet_pairwise_coupling`, `influence_A`, `onsager_L`, `generic_structure_check`
map to Coupling APIs. Layer markdown documents are not edited.
