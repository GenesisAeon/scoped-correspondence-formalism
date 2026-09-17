# Metarules Core (Milestone 9)

**Status:** review package only — not yet linked from README/GLOSSARY as accepted "core".
Johann-OK required before any core promotion.

## What this is

Typed Python wrappers for **discrete / event** metarule state \(m\), a
**priority** wrap of the joint control set **T5**, and a concrete A/B pair
showing that **unobserved** \(m\) can break otherwise closed \(z\)-dynamics.
Mapping: `context_transformations.md` §6.

```text
src/scoped_correspondence/
  metarules/
    __init__.py
    core.py
```

M9 **wraps** `membership.joint_control_set` and **calls**
`closure.partition_matrix` / `candidate_macro_kernel` / `is_exact_closure` /
`closure_error`. It does **not** mutate `membership/core.py`,
`closure/core.py`, `FORMALISM.md`, `context_transformations.md`, or the
seven layer docs.

## Mapping to context_transformations.md §6

| Document (§) | Claim / formula | API | Notes |
|---|---|---|---|
| §6 Metaregel | rule state \(m\); discrete \(m'=H(m,z,c,u,t)\) | `MetaRuleUpdate` | event/discrete only |
| §6 (last sentence of Metaregel ¶) | descriptive-only \(m\) change → affects \(\pi\) first; enforced rule → can change interventions and physical trajectory | `MetaRuleUpdate.variant` ∈ `{descriptive_only, enforced_rule}` | named distinguishable variants in return |
| §6 T5 | \(\mathcal U_{joint}(z,c,m,t)=\mathcal U_{physical}\cap\bigcap_\alpha\mathcal U_\alpha\) | wrap of `membership.joint_control_set` | no \(m\) arg on membership — wrap only |
| §6 T5 (last sentence) | empty cut = conflict; priority may **explicitly drop** one requirement; does **not** satisfy both at once | `priority_joint_control_set` | report names dropped req |
| §6 | unobserved \(m\) can make a closed description unclosed | `unobserved_metarule_breaks_closure` | A/B pair only |

## Formulas

### Discrete update

\[
m' = H(m,z,c,u,t)
\]

(event / discrete). Continuous or stochastic metarule ODEs are out of scope.

**Variants** (same §6 sentence):

* `descriptive_only` — observer / description choice; affects \(\pi\)
  (observation) first; does not by itself change interventions or the
  physical trajectory.
* `enforced_rule` — actually enforced; can change interventions and
  thereby the physical trajectory.

### Priority wrap of T5

1. Call `membership.joint_control_set(U_physical, U_alphas)` **unchanged**.
2. Only if `conflict=True` (empty cut): apply priority metarule \(m\) that
   **explicitly drops one** \(U_\alpha\) (index/name from \(m\)) and recompute
   \(\mathcal U_{physical}\cap\bigcap_{\alpha\neq\alpha_\*}\mathcal U_\alpha\).
3. Report names **which** requirement was dropped and records
   `both_requirements_satisfied_simultaneously: False`.

When the raw intersection is nonempty, priority is a no-op and
`U_joint` is identical to `joint_control_set`.

### Unobserved \(m\) vs closure (A/B)

Joint state \((z,m)\in\{0,1\}^2\) (4 states), ordered
\((0,0),(0,1),(1,0),(1,1)\). Project to \(z\) via
`closure.partition_matrix([0,0,1,1])` (call only; same APIs as e04/e05).

| Case | Dynamics | `is_exact_closure` | `closure_error` |
|---|---|---|---|
| A | \(m=z\) synchronized; next depends only on current \(z\) | `True` | `0` |
| B | \(m\) independent fair coin; \(z'=z\oplus m\), \(m'\sim\mathrm{Bern}(1/2)\) | `False` | `0.5` (concrete) |

No general HMM aggregation theory beyond this A/B pair.

## Hand-checkable verification

`verification/verify_metarules_core.py` covers at minimum:

1. Priority on empty cut (t5-style disjoint intervals) → nonempty
   `U_joint` + named dropped requirement +
   `both_requirements_satisfied_simultaneously is False`.
2. Case A: `closure_error == 0`, exact closure.
3. Case B: `closure_error > 0` with concrete number (`0.5`).
4. Nonempty raw cut → priority identical to `joint_control_set`.

## Out of scope

Mutation of `membership/core.py`, `closure/core.py`, `FORMALISM.md`,
`context_transformations.md`, seven layer docs; continuous / stochastic
metarule update; general HMM aggregation beyond A/B; adding an `m`
argument to `membership.joint_control_set`.
