# Membership Core (Milestone 4 - review package)

**Status:** review package only - not yet linked from README/GLOSSARY as accepted "core".
Johann-OK required before any core promotion.

## What this is

Python APIs for binary overlapping membership `M_{eα}`, the additive
double-counting guard, and the joint executable control set **T5**. Not a
general viability-kernel / polytope solver and not weighted membership.

```text
src/scoped_correspondence/
  membership/
    __init__.py
    core.py
```

## Mapping to context_transformations.md

| Document (§) | Claim / formula | API | Notes |
|---|---|---|---|
| §1 | `M_{eα}(t) ∈ {0,1}`; multiple 1s per row allowed | `MembershipMatrix` | Binary only; weighted needs separate meaning |
| §1 | Distinct from partition matrix `C` | separate type (no shared base / cast) | Like `AijInfluence` vs `LijTransport` |
| §1 | `y_α = π_α(z, c, t)` | `view(pi, z, c, t, ...)` | Signature / call mechanism only |
| §1 table / §2 | Physical stock counted once; naive overlap sums double-count | `double_count_stocks(M, x)` | `total_naive = sum(M.T @ x)` vs `sum(x)` |
| §6 T5 | `U_joint = U_physical ∩ ⋂_α U_α` | `joint_control_set(...)` | Intervals / boxes in one shared control coordinate |
| §6 | Empty intersection = rule/resource conflict | `conflict: bool` on report | See design choice below |
| §6 + viability t10 | Shared-budget numbers via shared-system membership | `t10_via_membership` | Calls `viability.shared_budget_conflict` unchanged |

## Design choice: empty T5 → `conflict: bool` (not raise)

An empty `U_joint` is a **domain-level** rule or resource contradiction
(context_transformations.md §6, last paragraph of T5), not a programming
error. Reporting `conflict: True` / `empty: True` matches
`shared_budget_conflict`'s report style and lets callers inspect the outcome.
`ScopeViolationError` remains for malformed inputs (non-binary `M`, bad
shapes, non-finite interval bounds).

## Hand-checkable verification

`verification/verify_membership_core.py` covers:

1. Double-count naive vs correct (entity in two systems; difference explicit).
2. T5 nonempty intersection (2 systems, overlapping membership, concrete intervals).
3. T5 empty intersection (explicit `conflict=True`).
4. Cross-check t10 numbers exactly vs `viability.core.shared_budget_conflict`.

## Out of scope

Viability kernel solver; weighted `M ∈ [0,1]`; metarules `m' = H(...)`;
mutation of FORMALISM.md or layer/extension docs; changes to
`closure/`, `viability/`, `coupling/`, or other existing modules (call /
cross-check only).
