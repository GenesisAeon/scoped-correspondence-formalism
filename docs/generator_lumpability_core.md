# Generator Lumpability Core (Milestone 11)

**Status:** review package only — not yet linked from README/GLOSSARY as accepted "core".
Johann-OK required before any core promotion.

## What this is

Continuous-time Markov **infinitesimal generator** lumpability for a fixed
partition matrix \(C\):

\[
Q\,C = C\,Q_{\mathrm{macro}}
\]

```text
src/scoped_correspondence/
  closure/
    core.py                     # UNCHANGED — partition_matrix called only
    generator_lumpability.py    # NEW — is_exact_generator_lumpability + generator_closure_error
```

M11 **calls** `partition_matrix` from `closure.core` only. It does **not**
mutate `closure/core.py`, `FORMALISM.md`, coupling/, validation/, or the
seven layer docs. Exports are **submodule-local** (`closure/__init__.py`) so
parallel M10/M12/M13 branches do not fight over root `__init__.py` /
`pyproject.toml`.

## Mapping

| Source | Claim / formula | API | Notes |
|---|---|---|---|
| Buchholz 1994, DOI [10.1017/S0021900200107338](https://doi.org/10.1017/S0021900200107338) | exact / ordinary lumpability; aggregated chain recovers exact stationary & transient quantities when exact | `is_exact_generator_lumpability` | finite MC aggregation |
| Michel & Siegle 2024, DOI [10.1016/j.peva.2024.102464](https://doi.org/10.1016/j.peva.2024.102464) / [arXiv 2403.07618](https://arxiv.org/abs/2403.07618) | CTMC aggregation residual; error growth rate controlled by \(\|\Theta A - A Q\|_\infty\) | `generator_closure_error` | ∞-norm on rate residual, not TV |
| `closure/core.py` | `partition_matrix(labels)` → \(C\) | called, not edited | M3 API freeze |
| Discrete analog (M3) | \(P C = C Q\) with TV defect \(\delta_{cl}\) | `is_exact_closure` / `closure_error` | stochastic kernels; separate from generators |

## Formulas

### Generator constraints

\(Q \in \mathbb{R}^{N\times N}\) is an infinitesimal generator iff

- \(\sum_j Q_{ij} = 0\) for every row \(i\);
- \(Q_{ij} \ge 0\) for \(i \ne j\) (off-diagonal rates).

### Exact lumpability

Given partition \(C \in \{0,1\}^{N\times M}\) (one 1 per row) and macro
generator \(Q_{\mathrm{macro}} \in \mathbb{R}^{M\times M}\):

\[
\mathrm{exact} \iff Q C = C Q_{\mathrm{macro}}
\quad\text{(elementwise absolute tolerance)}.
\]

### Closure defect (∞-norm, not TV)

\[
\delta_Q = \max_{i=1,\ldots,N}\ \bigl\| (Q C)_i - (C Q_{\mathrm{macro}})_i \bigr\|_\infty
\]

**Why not total variation?** TV is \(\tfrac12\|\cdot\|_1\) on probability
rows (nonnegative, sum to 1). Generator residuals are **signed rate
vectors** with row sum \(\approx 0\); TV is the wrong geometry and the
wrong units. The row ∞-norm matches Michel & Siegle's continuous-time
residual growth rate controlled by \(\|\Theta A - A Q\|_\infty\)
(identification: \(A \leftrightarrow C\), micro generator \(\leftrightarrow Q\)).

## Worked example (3-state micro; `partition_matrix([0,0,1])`)

Blocks: \(\{0,1\}\) → macro 0, \(\{2\}\) → macro 1.
\(C\) from real `partition_matrix([0,0,1])`:

\[
C = \begin{pmatrix} 1 & 0 \\ 1 & 0 \\ 0 & 1 \end{pmatrix}
\]

### Exact lumpable

States 0 and 1 have **identical** exit rate to state 2:

\[
Q = \begin{pmatrix}
-3 & 1 & 2 \\
 1 &-3 & 2 \\
 1 & 1 &-2
\end{pmatrix},\qquad
Q_{\mathrm{macro}} = \begin{pmatrix}
-2 & 2 \\
 2 &-2
\end{pmatrix}
\]

Then \(Q C = C Q_{\mathrm{macro}}\) and `generator_closure_error` \(= 0\).

### Non-lumpable

Different exit rates to state 2 (\(2\) vs \(3\)):

\[
Q' = \begin{pmatrix}
-3 & 1 & 2 \\
 1 &-4 & 3 \\
 1 & 1 &-2
\end{pmatrix}
\]

With the same \(Q_{\mathrm{macro}}\): residual row 1 is \((-1,\,1)\), so
`generator_closure_error` \(= 1.0\).

## Hand-checkable verification

`verification/verify_generator_lumpability_core.py` — imports real
`partition_matrix` from `closure.core` (blob SHA of master `core.py`
recorded in JSON). Expects exact error \(0.0\) and non-lumpable error
\(1.0\).

## Forbidden (must stay untouched)

`FORMALISM.md`, seven layer docs, `coupling/`, `validation/`,
`closure/core.py` (call only).
