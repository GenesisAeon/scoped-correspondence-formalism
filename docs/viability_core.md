# Viability Core (Milestone 3 - review package)

**Status:** review package only - not yet linked from README/GLOSSARY as accepted "core".
Johann-OK required before any core promotion.

## What this is

Python APIs for **safe intervention transfer** in the scalar buffer case and for the
coupled-buffer **shared-budget conflict**. Not a general polytope / level-set
viability-kernel solver (that remains a later, larger module per ARCHITECTURE_ROADMAP).

```text
src/scoped_correspondence/
  viability/
    __init__.py
    core.py
  legacy/            # optional historical aliases
```

## Mapping to context_transformations.md section 8

| Document claim | API | Notes |
|---|---|---|
| Ausfuhrbarkeit / Nachfolgervertraglichkeit / sichere Darstellung | `has_safe_transfer(r, z_eq, b, U, W, ...)` | Scalar specialization of section-8 triple; identity projection |
| Robust controlled invariance of K=[b, inf) | same (`boundary_inward = r(z_eq-b)+U-W`) | worked_example_viability.md section 2 |
| Hitting time V1 | `scalar_hitting_time`, `scalar_solution` | Finite contact when z_* < b < z0 |
| Shared budget V8-V9 / r10 | `shared_budget_conflict`, `orthant_action_demand` | Joint a1+a2 vs U |
| Coupled field V2 | `coupled_buffer_field` | Two buffers with exchange k |

### Section-8 specialization (scalar)

For identity `pi` and open-loop `u=U`:

1. **Executability:** `U` admissible on `[0,U]`.
2. **Successor compatibility:** dynamics closed in the observed scalar `z`.
3. **Safe representation:** `K_hat = K = [b, +inf)`.

Together with a macro policy that keeps the macro set, this yields robust transfer
for every micro state in `pi^{-1}(K_hat)` — here the whole half-line `K`.

## Equivalence verification

`verification/verify_viability_core.py` matches legacy evidence exactly for:

- `t05_scalar_boundary_and_hitting`
- `t09_orthant_boundary_conditions`
- `t10_shared_budget_conflict`

(and cross-checks `t07` unequal rates via `unequal_rates_sum_derivatives` /
`coupled_buffer_field`).

## Out of scope

General viability kernels, membership (`M_ea`), predictive states, mutation of
FORMALISM.md or layer/extension markdown, changes to M1/M2 modules.
