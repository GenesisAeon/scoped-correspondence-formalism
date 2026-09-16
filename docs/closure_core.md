# Closure Core (Milestone 3 - review package)

**Status:** review package only - not yet linked from README/GLOSSARY as accepted "core".
Johann-OK required before any core promotion.

## What this is

Python APIs for exact / approximate macro-closure (`PC=CQ`, `delta_cl`, TV horizon
bound) and the concrete circle delay-embedding reconstruction from the worked
example. Not a general Takens library and not a membership module.

```text
src/scoped_correspondence/
  closure/
    __init__.py
    core.py
  legacy/            # optional historical aliases
```

## Mapping to FORMALISM.md section 9 / emergence_and_closure.md

| Document symbol / claim | API | Notes |
|---|---|---|
| `PC = CQ` | `is_exact_closure(P, C, Q, tol=1e-10)` | Exact lumpability for finite Markov chains |
| `delta_cl = max_i TV((PC)_i,(CQ)_i)` | `closure_error(P, C, Q)` | One-step defect |
| `TV(p P^k C, p C Q^k) <= min(1, k delta_cl)` | `propagated_error_bound(delta_cl, k)` | Own elementary bound |
| Circle: two coords at d=1 | `reconstruct_from_projection(obs, delayed, alpha)` | worked_example_reconstruction.md section 1 |
| Projection needs memory | `memory_solution`, `projected_memory_rhs` | worked_example_reconstruction.md section 2 |

Helpers `partition_matrix`, `candidate_macro_kernel`, `demo_matrices` reproduce the
legacy extension matrices without claiming that `Q = Lambda P C` alone implies closure.

## Equivalence verification

`verification/verify_closure_core.py` matches legacy evidence exactly for:

- `e01_circle_reconstruction`
- `e03_projected_memory`
- `e04_exact_lumpability`
- `e05_nonclosed_aggregation`
- `e06_approximate_error_bound`
- `t07_unequal_rates_break_closure` (sum-closure break; also in viability verify)
- `t15_changing_partition_exact_closure`

Numbers come from the script run / checked-in JSON (`extension_results.json`,
`transformation_results.json`).

## Out of scope

Membership / shared resources, predictive states (`e15`), general delay-embedding
tooling, mutation of FORMALISM.md or layer/extension markdown.
