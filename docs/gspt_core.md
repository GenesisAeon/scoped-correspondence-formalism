# Fenichel / Geometric Singular Perturbation Theory (GSPT) (Milestone 33)

**Status:** review package only — not yet linked from README/GLOSSARY as accepted "core".
Johann-OK required before any core promotion.

## What this is

Typed Python helpers for the **hand-checkable** geometry of the classical
van-der-Pol **critical manifold**

\[
S(x) = \frac{x^3}{3} - x,
\]

as the minimal concrete instance of Fenichel's geometric singular perturbation
theory (GSPT). Fold points, normal hyperbolicity, and an **O(ε)** order
estimate for the distance between the critical manifold \(C_0\) and a
persisting slow manifold \(C_\varepsilon\) are exposed as pure functions —
no ODE integration, no canard / blow-up analysis.

```text
src/scoped_correspondence/
  dynamics/
    core.py           # UNCHANGED
    contraction.py    # UNCHANGED (M14 — not imported)
    landau.py         # UNCHANGED (M29 — not imported)
    gspt.py           # NEW — fold points + NH + O(ε) bound
```

**Independent of M14 contraction and M29 Landau.** This Baustein neither
imports those modules nor equates Fenichel normal hyperbolicity with metric
contraction rates or with mean-field / Ising scaling exponents. It also does
**not** identify \(S(x)\) with the cubic cusp normal form of `dynamics.core`
(FORMALISM.md §5).

Package-level `scoped_correspondence/__init__.py` is **not** rewritten here
(submodule-local wiring via `dynamics/__init__.py` only).

## Mapping

| Source | Claim / formula | API | Notes |
|---|---|---|---|
| Fenichel 1979 DOI 10.1016/0022-0396(79)90152-9 | NH ⇒ slow manifold \(C_\varepsilon\) persists, \(O(\varepsilon)\)-close to \(C_0\) | `is_normally_hyperbolic`, `slow_manifold_distance_bound` | order estimate only |
| Kuehn 2015 DOI 10.1007/978-3-319-12316-5 | van-der-Pol critical manifold \(S(x)=x^3/3-x\) | `critical_manifold_S`, `critical_manifold_fold_points` | textbook example |
| \(S'(x)=x^2-1=0\) | folds at \(x=\pm 1\), \(S=\mp 2/3\) | `critical_manifold_fold_points` | exact rationals |
| \(S'(x)\neq 0\) | normal hyperbolicity | `is_normally_hyperbolic` | True at 2, 0, 1.5; False at ±1 |

## Formulas

### Critical manifold (van der Pol)

\[
S(x) = \frac{x^3}{3} - x, \qquad S'(x) = x^2 - 1.
\]

### Fold points

\[
S'(x) = 0 \;\Rightarrow\; x = \pm 1,
\quad
S(+1) = -\tfrac{2}{3},\quad
S(-1) = +\tfrac{2}{3}.
\]

### Normal hyperbolicity

\[
\text{NH}(x) \;\Leftrightarrow\; S'(x) = x^2 - 1 \neq 0.
\]

Worked checks: NH True at \(x \in \{2,\,0,\,1.5\}\); False at \(x = \pm 1\).

### Slow-manifold distance (order estimate only)

On a normally hyperbolic branch, Fenichel guarantees
\(\mathrm{dist}(C_\varepsilon, C_0) = O(\varepsilon)\) for small \(\varepsilon > 0\).
`slow_manifold_distance_bound(epsilon, x)` returns \(|\varepsilon|\) as that
**order estimate** (no sharp Fenichel constant). Raises `ScopeViolationError`
if \(\varepsilon \le 0\) or if \(x\) is not normally hyperbolic.

## Scope fences

- Independent of M14 contraction and M29 Landau.
- No canard / blow-up analysis at the folds.
- No numerical ODE integration / trajectory residual.
- `dynamics/core.py` and package-root `__init__.py` untouched.
- No identification of van-der-Pol \(S(x)\) with the cusp cubic of FORMALISM.md §5.

## Sources

- Neil Fenichel, *Geometric singular perturbation theory for ordinary
  differential equations*, J. Differential Equations **31**, 53–98 (1979).
  DOI [10.1016/0022-0396(79)90152-9](https://doi.org/10.1016/0022-0396(79)90152-9).
- Christian Kuehn, *Multiple Time Scale Dynamics*, Springer Applied
  Mathematical Sciences (2015).
  DOI [10.1007/978-3-319-12316-5](https://doi.org/10.1007/978-3-319-12316-5).
