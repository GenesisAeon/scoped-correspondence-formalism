# Dirac Structure Composition Core (Milestone 12)

**Status:** review package only — not yet linked from README/GLOSSARY as accepted "core".
Johann-OK required before any core promotion.

## What this is

Typed Python composition of two skew-symmetric structure matrices \(J_1, J_2\)
under a **power-preserving** feedback interconnection, yielding a closed-loop
\(J_{\mathrm{total}}\) that remains skew-symmetric. Maps the Dirac-structure
composition theorem of Cervera, van der Schaft & Baños (2007).

```text
src/scoped_correspondence/
  coupling/
    core.py                 # UNCHANGED — check_generic_structure called only
    dirac_composition.py    # NEW — compose_skew_symmetric (+ helpers)
    __init__.py             # submodule-local re-exports (package root untouched)
```

M12 **calls** `check_generic_structure` only (reads `J_antisymmetric`).
It does **not** mutate `coupling/core.py`, `FORMALISM.md`,
`coupling_layer_afet.md`, `closure/`, `validation/`, or any bond-graph library.
Package-root `scoped_correspondence/__init__.py` is intentionally **not**
edited (avoid merge fights with parallel M11/M13).

## Mapping

| Source | Claim / formula | API | Notes |
|---|---|---|---|
| Cervera, van der Schaft & Baños 2007, DOI 10.1016/j.automatica.2006.08.014 | power-conserving interconnection of Dirac structures is again a Dirac structure; ISO-PH case = graph of skew map | `compose_skew_symmetric`, `DiracCompositionResult` | **J composition only** |
| Feedback interconnection | \(u_1=-y_2\), \(u_2=y_1\) ⇒ \(y_1\cdot u_1+y_2\cdot u_2=0\) | `PowerPreservingInterconnection`, `interface_power_under_feedback` | identically zero |
| `coupling/core.py` | `check_generic_structure` antisymmetry | called, not edited | M2 API freeze |

## Formulas

### ISO-PH structure (graph of skew map)

\[
\dot x = J\,\partial_x H + g\,u,\qquad y = g^\top\,\partial_x H,\qquad J^\top=-J.
\]

### Power-preserving feedback

\[
u_1 = -y_2,\qquad u_2 = y_1
\quad\Rightarrow\quad
y_1\cdot u_1 + y_2\cdot u_2 = 0.
\]

### Closed-loop \(J_{\mathrm{total}}\)

\[
J_{\mathrm{total}}
=
\begin{bmatrix}
J_1 & -g_1 g_2^\top \\
g_2 g_1^\top & J_2
\end{bmatrix}.
\]

Default ports: \(g_1=g_2=I\) when \(\dim J_1=\dim J_2\).

**Disclaimer:** `ok=True` certifies \(J_{\mathrm{total}}^\top=-J_{\mathrm{total}}\)
via `check_generic_structure` (`J_antisymmetric` only). It does **not** claim
a resistive \(M\) structure, full Jacobi identity beyond skew-symmetry, or that
an arbitrary model is GENERIC / Dirac.

## Worked example

\[
J_1=\begin{bmatrix}0&1\\-1&0\end{bmatrix},\quad
J_2=\begin{bmatrix}0&2\\-2&0\end{bmatrix},\quad
g_1=g_2=I_2.
\]

\[
J_{\mathrm{total}}
=
\begin{bmatrix}
0&1&-1&0\\
-1&0&0&-1\\
1&0&0&2\\
0&1&-2&0
\end{bmatrix}.
\]

- \(\max|J_{\mathrm{total}}^\top+J_{\mathrm{total}}|=0\) (skew).
- For any port vectors \(y_1,y_2\in\mathbb{R}^2\):
  \(y_1\cdot(-y_2)+y_2\cdot y_1=0\) (interface power exactly 0; ≥2 samples).

## Hand-checkable verification

`verification/verify_dirac_composition_core.py` checks:

1. Worked example → `ok=True`, skew residual 0, power max-abs 0 on ≥2 samples.
2. `check_generic_structure` called on \(J_{\mathrm{total}}\) with zero \(M\) (no M claim).
3. Non-skew input \(J_1\) raises `ScopeViolationError`.

## Import

```python
from scoped_correspondence.coupling.dirac_composition import (
    compose_skew_symmetric,
)
# or, submodule-local:
from scoped_correspondence.coupling import compose_skew_symmetric
```

Package-root `import scoped_correspondence as sc; sc.compose_skew_symmetric`
is **not** wired in this milestone.
