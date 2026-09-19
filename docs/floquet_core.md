# Floquet Multipliers Core (Milestone 34)

**Status:** review package only — not yet linked from README/GLOSSARY as accepted "core".
Johann-OK required before any core promotion.

## What this is

Typed Python helpers for **Floquet multipliers of a given 2×2 monodromy
matrix** ``M = Φ(T)``. Multipliers are the eigenvalues of ``M``; for the
2×2 case they solve

\[
\mu^2 - (\operatorname{tr} M)\,\mu + (\det M) = 0.
\]

Orbital stability is read from the moduli ``|μ|``. This milestone does
**not** integrate any ODE / variational equation — the monodromy is an
input. It is **not** M14 contraction analysis (Lohmiller & Slotine metric
contraction of the cusp field).

```text
src/scoped_correspondence/
  dynamics/
    core.py           # UNCHANGED — CALL-free here; not edited
    contraction.py    # M14 — orthogonal (equilibrium contraction metric)
    landau.py         # M29 — orthogonal
    floquet.py        # NEW — floquet_multipliers + classify_orbital_stability
    __init__.py       # WIRED — submodule-local export of M34
```

Package-level `scoped_correspondence/__init__.py` is **not** rewritten
(submodule-local wiring via `dynamics/__init__.py` only).
`dynamics/core.py` is **not** mutated.

## Mapping

| Source | Claim / formula | API | Notes |
|---|---|---|---|
| Floquet 1883, DOI 10.24033/asens.220 | multipliers = eigenvalues of monodromy ``M=Φ(T)`` | `floquet_multipliers` | 2×2 via char poly |
| Castelli & Lessard 2013, DOI 10.1137/120873960 (optional) | modern Floquet / monodromy numerics context | cited in `SOURCE_OPTIONAL` | no integrator here |
| orbital stability | all ``|μ|<1`` → stable; some ``|μ|>1`` → unstable; else neutral | `classify_orbital_stability` | double ``μ=1`` → **neutral**, not stable |
| M14 contraction | global Euclidean ``f'≤−λ`` for cusp | **not this module** | docstring disambiguates |

## Formulas

### Characteristic polynomial (2×2)

\[
\mu_\pm = \frac{\operatorname{tr} M \pm \sqrt{(\operatorname{tr} M)^2 - 4\det M}}{2}.
\]

Cross-check: ``numpy.linalg.eigvals(M)`` must agree (multiset).

### Classification

\[
\begin{cases}
\texttt{unstable} & \exists\, |\mu| > 1,\\
\texttt{stable}   & \forall\, |\mu| < 1,\\
\texttt{neutral}  & \text{otherwise (unit circle / double }\mu=1\text{)}.
\end{cases}
\]

## Worked examples (hand-checkable)

### Example A — neutral (``tr = 1.5``, ``det = 1``)

\[
\mu_\pm = \frac{1.5 \pm \sqrt{2.25 - 4}}{2} = \frac{1.5 \pm i\sqrt{1.75}}{2},
\qquad |\mu_\pm| = 1
\]

(area-preserving / unit-circle case) → ``classify_orbital_stability`` =
``neutral``.

### Example B — unstable (``tr = 2.5``, ``det = 1``)

\[
\mu_\pm = \frac{2.5 \pm \sqrt{6.25 - 4}}{2} = \frac{2.5 \pm 1.5}{2} \in \{2,\,0.5\}.
\]

``|μ|=2 > 1`` → ``unstable``.

### Example C — double ``μ = 1`` edge (``tr = 2``, ``det = 1``)

\[
\mu_\pm = 1 \quad\text{(double root)}.
\]

**Must not** be classified as ``stable`` → ``neutral``.

## Out of scope

- ODE / variational integration to *build* ``M``
- Dimension ``n ≠ 2``
- Editing ``dynamics/core.py`` or package-root ``__init__.py``
- Identifying Floquet with M14 contraction or M29 Landau

## Sources

- G. Floquet, *Sur les équations différentielles linéaires à coefficients
  périodiques*, Ann. sci. Éc. Norm. Sup. **12**, 47–88 (1883),
  DOI [10.24033/asens.220](https://doi.org/10.24033/asens.220)
- Optional: R. Castelli & J.-P. Lessard, SIAM J. Appl. Dyn. Syst. (2013),
  DOI [10.1137/120873960](https://doi.org/10.1137/120873960)
