# Free Boundary / One-Phase Stefan–Neumann (Milestone 31)

**Status:** review package only — not yet linked from README/GLOSSARY as accepted "core".
Johann-OK required before any core promotion.

## What this is

A **new** Baustein `free_boundary` for the classical **one-phase Stefan
problem** in the **Neumann similarity** form: the melt (or solidification)
front \(s(t)\) advances as \(s(t)=2\lambda\sqrt{\alpha t}\), where the
dimensionless root \(\lambda>0\) solves a transcendental equation involving
the **Stefan number** \(\mathrm{Ste}=c\,T_0/L\).

```text
src/scoped_correspondence/
  free_boundary/
    __init__.py
    core.py
```

M31 does **not** mutate `viability/` (core, Nagumo/M28, CBF/M16), package-root
`__init__.py`, `FORMALISM.md`, or the seven layer docs.

## Why this is NOT a viability subclass

`viability` (and related barrier / Nagumo checks) treats a safe set \(K\) as
**fixed** a priori: trajectories are tested for remaining inside \(K\).
In the Stefan problem the phase boundary \(s(t)\) is itself a **dynamic
variable** with its own motion law (latent-heat flux balance at the front).
It is not a fixed constraint set against which one merely checks membership.
Both independent research agents in the M31 round classified this as a
**separate Baustein** (not a `viability` extension) for that reason; the
module docstring repeats the same rationale.

## Sources

| Source | Role |
|---|---|
| V. A. Kot, *Journal of Engineering Physics and Thermophysics* 90(4), 889–917 (2017), DOI [10.1007/s10891-017-1638-2](https://doi.org/10.1007/s10891-017-1638-2) | Classical Stefan / Neumann-condition context |
| J. Bollati, M. F. Natale, J. A. Semitiel & D. A. Tarzia, arXiv:[1906.08601](https://arxiv.org/abs/1906.08601) | Exact transcendental form \(\lambda\exp(\lambda^2)\mathrm{erf}(\lambda)=\mathrm{Ste}/\sqrt{\pi}\) |

**Do not cite** the classical Stefan paper or the Rubinstein monograph as sources in this
milestone (no reliably verified DOI in the research round).

## Formulas

### Stefan number

\[
\mathrm{Ste} = \frac{c\,T_0}{L}
\]

API: `stefan_number(c, T0, L)`.

### Neumann root

For \(\lambda>0\):

\[
\lambda\,\mathrm{e}^{\lambda^2}\,\mathrm{erf}(\lambda) = \frac{\mathrm{Ste}}{\sqrt{\pi}}
\]

Solved by **bracketed bisection** (no bare Newton).  
API: `neumann_lambda(Ste, tol=1e-12)` → `{"lambda", "iterations", "residual"}`.  
`ScopeViolationError` if \(\mathrm{Ste}\le 0\).

### Melt-front position

\[
s(t) = 2\lambda\sqrt{\alpha\,t}
\]

API: `melt_front_position(lam, alpha, t)`.

### Temperature (liquid region only)

\[
T(x,t) = T_0\left(1 - \frac{\mathrm{erf}\!\big(x/(2\sqrt{\alpha t})\big)}{\mathrm{erf}(\lambda)}\right),
\qquad 0\le x\le s(t).
\]

API: `temperature_profile(x, t, lam, alpha, T0)`.  
`ScopeViolationError` if \(x\notin[0,s(t)]\) (one-phase model; no two-phase
extension).

## Hand-checkable example

| \(\mathrm{Ste}\) | \(\lambda\) (≈ target) |
|---|---|
| 1.0 | ≈ 0.620063 |
| 0.5 | ≈ 0.464786 |
| 0.1 | ≈ 0.220016 |

For **each** Ste, verification **re-evaluates**
\(\lambda\mathrm{e}^{\lambda^2}\mathrm{erf}(\lambda)\) against
\(\mathrm{Ste}/\sqrt{\pi}\) and requires residual \(<10^{-9}\) (not only a
hardcoded λ match).

Additional geometric check for \(\mathrm{Ste}=1\), \(\alpha=1\,\mathrm{mm}^2/\mathrm{s}\):

* \(s(100)\approx 12.40\,\mathrm{mm}\)
* \(s(400)\approx 24.80\,\mathrm{mm}\)
* ratio \(s(400)/s(100)=2\) exactly (\(\sqrt{t}\) law) — own JSON field
  `sqrt_t_ratio_s400_over_s100`.

Control: \(\mathrm{Ste}=0.01\) → \(\lambda\) clearly smaller than for
\(\mathrm{Ste}=0.1\).

## Out of scope

* Two-phase / general PDE free-boundary solvers.
* Treating `free_boundary` as a subclass or drop-in of `viability`.
* Mutations of `viability/`, package-root `__init__.py`, `FORMALISM.md`,
  seven layer docs.
* Citing the classical Stefan paper or the Rubinstein monograph as sources.
