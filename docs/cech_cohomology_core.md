# Čech Cohomology Witness Core (Milestone 24)

**Status:** review package only — not yet linked from README/GLOSSARY as accepted "core".
Johann-OK required before any core promotion.

## What this is

Typed Python helpers for the **Abramsky–Mansfield–Barbosa (AMB) relative Čech
obstruction** of an empirical model's support (Abramsky, Mansfield & Barbosa
2012, arXiv:1111.3620). Given a no-signalling EmpiricalModel on a measurement
cover \(\mathcal{U}\), the support determines an abelian-presheaf of formal
linear combinations of local sections; the relative class
\(\gamma(s)\in\check{H}^{1}(\mathcal{U},\mathcal{F}_{\bar{C}})\) is an
obstruction to extending a supported local section \(s\).

This milestone specializes to **coefficient ring \(\mathbb{Z}_2\)** (= GF(2))
and computes the obstruction via **compatibility / coboundary linear algebra
over GF(2)** (no general cohomology library).

```text
src/scoped_correspondence/
  contextuality/
    core.py         # UNCHANGED — sheaf CF / builders; CALL only
    csw.py          # UNCHANGED — M19; not edited
    cohomology.py   # NEW — Z_2 Čech obstruction + CohomologyWitness
```

M24 does **not** ship a general cohomology library, does **not** mutate
`contextuality/core.py` or `csw.py`, does **not** rewrite package-root
`scoped_correspondence/__init__.py`, and does **not** edit `FORMALISM.md` or
`sheaf_contextuality.md`. Submodule wiring is via `contextuality/__init__.py`
only.

## One-way implication (critical)

| Obstruction | Conclusion allowed |
|---|---|
| **non-vanishing** | sufficient for contextuality → `proves_contextuality=True` |
| **vanishing** | **no certificate** of noncontextuality (AMB §8 / Hardy false positives) |

**Forbidden:** `is_contextual = not obstruction_vanishes` (or any dual that
treats vanishing as a noncontextuality proof). The API sets

```text
proves_contextuality  =  obstruction_nonzero
```

and nothing else. Cross-checks against the sheaf `contextual_fraction` LP are
diagnostic only — Čech rank / flags are **not** identified with CF as the
same number.

## Mapping

| Source | Claim | API | Notes |
|---|---|---|---|
| AMB 2012 arXiv:1111.3620 §4 | relative Čech obstruction \(\gamma(s)\) | `cech_obstruction` | Z_2 specialization |
| same Prop. 4.3–4.5 | non-vanishing ⇒ contextual | `CohomologyWitness.proves_contextuality` | one-way only |
| same §5 PR-box | all support sections obstruct | `pr_box_model(bell_222)` → nonzero | machine-check over GF(2) |
| same (classical) | extendable ⇒ obstruction vanishes | `classical_factorizable_model(bell_222)` → vanishes | |
| coboundary / compatibility matrix | GF(2) rank diagnostic | `coboundary_rank` | not a general cohom lib |

arXiv: https://arxiv.org/abs/1111.3620

## Algorithm (Z_2, specialized)

1. Extract the **support** of each context (\(p > 0\)).
2. Introduce a GF(2) variable \(x_{C,s}\) per supported local section.
3. For every pair of overlapping contexts and every restriction \(t\) on the
   intersection, enforce the **compatibility / coboundary** equation
   \(\sum_{s|_{U}=t} x_{C_i,s} = \sum_{s|_{U}=t} x_{C_j,s} \pmod{2}\).
4. For each candidate section \(s_0\in\operatorname{supp}(e_{C_0})\), fix
   \(x_{C_0,s_0}=1\) and other \(C_0\)-variables to \(0\); test solvability of
   the remaining system (AMB Prop. 4.3 over GF(2)).
5. `obstruction_nonzero` iff **some** support section fails solvability
   (sufficient for contextuality).

`coboundary_rank` is the GF(2) rank of the compatibility constraint matrix
(diagnostic; not equated with CF).

## Examples (bell_222)

| Model | Obstruction | CF (cross-check) | `proves_contextuality` |
|---|---|---|---|
| `classical_factorizable_model` | vanishes | \(0\) | `False` |
| `pr_box_model` | nonzero (all 8 sections) | \(1\) | `True` |

Vanishing on the classical model does **not** by itself prove noncontextuality
in the cohomology calculus; CF / global-section LP remains the bilateral test.
The mandatory negative test in
`verification/verify_cech_cohomology_core.py` forbids inverted witness logic.

## Forbidden

- General cohomology library / arbitrary covers beyond this specialized Z_2 path
- Equating CF and Čech invariants as the same number
- Editing `FORMALISM.md`, `sheaf_contextuality.md`
- Editing package-root `__init__.py`, `contextuality/core.py`, `csw.py`
