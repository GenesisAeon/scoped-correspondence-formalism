# Formal Concept Analysis on MembershipMatrix (Milestone 27)

**Status:** review package only — not yet linked from README/GLOSSARY as accepted "core".
Johann-OK required before any core promotion.

## What this is

Binary entity×system membership `MembershipMatrix` is literally a **formal
context** `(G, M, I)` in the sense of Ganter & Wille (1999):

| FCA | Membership |
|---|---|
| objects \(G\) | entities (rows) |
| attributes \(M\) | systems (columns) |
| incidence \(I\) | ones of `MembershipMatrix.matrix` |

This milestone adds Galois derivation operators and concept enumeration on top
of the existing binary matrix — **no weighted membership**, no change to
`membership/core.py`.

```text
src/scoped_correspondence/
  membership/
    core.py                      # UNTOUCHED — MembershipMatrix only called
    formal_concept_analysis.py   # NEW — derive_up / derive_down / all_concepts / is_concept
    __init__.py                  # wired M27 exports (submodule-local)
```

Package-root `scoped_correspondence/__init__.py` is **not** touched.
`FORMALISM.md` and `context_transformations.md` are **not** touched.

## Operators (Ganter & Wille 1999)

\[
A^{\uparrow} = \{\alpha \mid \forall e\in A:\; M_{e\alpha}=1\}
\qquad
B^{\downarrow} = \{e \mid \forall\alpha\in B:\; M_{e\alpha}=1\}
\]

A pair `(A, B)` is a **formal concept** iff \(A^{\uparrow}=B\) and \(B^{\downarrow}=A\).

Vacuous cases: \(A=\emptyset\Rightarrow A^{\uparrow}=\) all systems;
\(B=\emptyset\Rightarrow B^{\downarrow}=\) all entities.

## API

| Function | Role |
|---|---|
| `derive_up(entity_indices, M)` | intent \(A^{\uparrow}\) |
| `derive_down(system_indices, M)` | extent \(B^{\downarrow}\) |
| `is_concept(A, B, M)` | closure check |
| `all_concepts(M)` | all concepts, ordered by \(\lvert A\rvert\) descending |
| `attribute_implication_from_extents(α, β, M)` | report whether extent({α}) ⊆ extent({β}) |

### Why no NextClosure

`all_concepts` brute-forces the power set of the **smaller** side
(\(O(2^{\min(n_e,n_\alpha)}\cdot\mathrm{poly})\)). Repo matrices are small;
NextClosure / Close-by-One are out of scope for M27 (documented in the module
docstring).

## Worked example (4×3)

```text
M = [[1,1,0],   # e1: s1,s2
     [1,0,1],   # e2: s1,s3
     [1,1,1],   # e3: s1,s2,s3
     [0,1,0]]   # e4: s2
```

Exactly **6** concepts (derived, not hard-coded):

| extent A | intent B |
|---|---|
| {e1,e2,e3,e4} | ∅ |
| {e1,e2,e3} | {s1} |
| {e1,e3,e4} | {s2} |
| {e1,e3} | {s1,s2} |
| {e2,e3} | {s1,s3} |
| {e3} | {s1,s2,s3} |

**Implication (readable JSON field):** from concept `({e2,e3},{s1,s3})`,
extent({s3})={e2,e3} ⊆ extent({s1})={e1,e2,e3}, so membership in **s3**
implies membership in **s1** on this dataset.

**Negative test:** `A={e1,e2}`, `B={s1}` is **not** a concept —
`A↑={s1}` but `{s1}↓={e1,e2,e3}≠A`.

## Source

B. Ganter & R. Wille, *Formal Concept Analysis: Mathematical Foundations*,
Springer Berlin Heidelberg (1999), DOI [10.1007/978-3-642-59830-2](https://doi.org/10.1007/978-3-642-59830-2).

## Explicit non-goals

- Weighted / continuous membership
- NextClosure or other large-context algorithms
- Links to the metarules package or other modules
- Edits to `FORMALISM.md`, `context_transformations.md`, package-root `__init__.py`, or `membership/core.py`
