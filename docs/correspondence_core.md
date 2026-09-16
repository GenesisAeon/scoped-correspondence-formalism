# Correspondence Core (Milestone 1 — review package)

**Status:** review package only — not yet linked from README/GLOSSARY as accepted "core".
Johann-OK required before any core promotion.

## What this is

A minimal typed Python contract for a **Correspondence**: a relationship between two
model descriptions that carries state map, optional time map, scope, residual, and
error measure. Implements the Astra/ARCHITECTURE_ROADMAP sketch:

```text
Correspondence(source, target, state_map, scope, time_map=..., metric=...)
```

Package layout:

```text
src/scoped_correspondence/
  __init__.py
  correspondence/
    __init__.py
    contract.py
```

Import (from repo root): `PYTHONPATH=src` or `pip install -e .` with the bundled
minimal `pyproject.toml`.

## Content basis (no new science)

| Contract piece | Document basis |
|---|---|
| Conjugacy residual `T∘Φ_j^t − Φ_k^{c t}∘T` | FORMALISM.md §1 ("Selbstähnlichkeit präzise untersuchen") |
| Local rates / necessary condition `DT f_j = c f_k∘T` | FORMALISM.md §1; counterexample in extensions e11 |
| T1 context chain rule | context_transformations.md §3 |
| T2 state-dependent time `dy/dτ` | context_transformations.md §3 |
| T3 compatibility `DR F_fine = F∘R` | context_transformations.md §4–5 |
| T4 residual composition | context_transformations.md §5 ("Fehler bei mehreren Transformationsschritten") |

## Mapping table (old terms → new API)

| Old / document term | New API / role |
|---|---|
| transformationsgebundene Selbstähnlichkeit | `Correspondence` |
| `T` (Zustandsabbildung) | `StateMap` / `Correspondence.state_map` |
| Zeitskalierung `c` / `a=dτ/dt` | `TimeMap` (`constant_scale` or `scale_fn`) |
| `Φ_j^t`, `Φ_k^{ct}` | `ModelRef.flow` on source/target |
| Konjugation (Homöomorphismus T, exact) | `verify_conjugacy` with bijective `StateMap` in scope |
| Semikonjugation (Projektion) | same residual API; scope marks many-to-one |
| Geltungsbereich | `Scope` |
| Residuum / Fehlermaß | `Residual`, `ErrorMetric`, `CorrespondenceReport` |
| T1 | `Correspondence.t1_residual` |
| T2 | `Correspondence.t2_dy_dtau` |
| T3 | `Correspondence.t3_compatibility_residual` |
| T4 | `Correspondence.t4_composition_residual` |
| CREP / UTAC / AFET | Observation / Dynamics / Coupling (GLOSSARY) — not in this package yet |

## Equivalence verification

`verification/verify_correspondence_core.py` re-expresses ≥3 existing synthetic cases
through this API and checks numeric evidence against the already established JSON
results (old API vs new API). Seeds/grids match the legacy scripts; no new claims.

## Out of scope (later milestones)

Observation / Dynamics / Coupling modules, Closure / Viability / Membership,
GENERIC, Lean, empirical validation pipeline.
