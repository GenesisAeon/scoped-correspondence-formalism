# Contextuality Core (Milestone 7 — optional module hardening)

**Status:** review package only — not yet linked from README/GLOSSARY as accepted "core".
Johann-OK required before any core promotion.

## What this is

Typed Python port of F08 sheaf contextuality (Abramsky–Brandenburger empirical
models + Abramsky–Barbosa–Mansfield contextual fraction) from
`verification/verify_sheaf_contextuality.py`, plus an **F13 scope guard** that
was previously prose-only in `sheaf_contextuality.md` §6.

```text
src/scoped_correspondence/
  contextuality/
    __init__.py
    core.py
```

## Mapping to sheaf_contextuality.md / F08 / F13

| Document | Claim / formula | API | Legacy |
|---|---|---|---|
| §2 | Empirical model + margin compatibility | `EmpiricalModel`, `bell_222_scenario` | s01 |
| §2 | Contextual fraction LP / NCF | `contextual_fraction` | s02–s04 |
| §2 | Global section existence | `has_global_section` | s02–s03 |
| §5 | Classical / PR-box / CHSH Table I numbers | `classical_factorizable_model`, `pr_box_model`, `chsh_table_i_model` | s02–s04 |
| §5 | VB1 deterministic empty section (smoke) | (verify-only, not a CF call) | s05 |
| §6 / **F13** | Shared-state pushforward is not contextuality | `assumes_independent_contexts=True` required; else `ScopeViolationError` | new |

## F13 scope guard

`contextual_fraction(...)` and `has_global_section(...)` take a **mandatory**
flag `assumes_independent_contexts` with **no silent True default**. Passing
`False` or omitting the argument raises `ScopeViolationError` with the F13 risk
text: if all views \(y_\alpha=\pi_\alpha(z,c,t)\) are functions of the same
assumed \(z\), a joint distribution always exists trivially; positive CF would
then be a modelling error, not true contextuality. The caller must actively
pass `True` when per-context tables are independently specified primitives.

## Exact legacy targets (from verify_sheaf_contextuality_results.json)

| Case | Value |
|---|---|
| Classical CF / NCF | `0.0` / `1.0` |
| PR-box CF / NCF | `1.0` / `0.0` |
| CHSH Table I CF / NCF | `0.25` / `0.75` |
| VB1 consistent globals | `0` of `27` |

## Hand-checkable verification

`verification/verify_contextuality_core.py` matches s01–s06 evidence against
`verification/verify_sheaf_contextuality_results.json` and asserts
`ScopeViolationError` for `False` / missing `assumes_independent_contexts`.

## Out of scope

Mutation of `sheaf_contextuality.md` / `FORMALISM.md`; changes to
`correspondence/`, `observation/`, `dynamics/`, `coupling/`, `closure/`,
`viability/`, `membership/`, `identifiability/`, `validation/`; edits to
legacy `verify_sheaf_contextuality.py`.
