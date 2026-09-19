# Landau Exponent Comparison / Self-Falsification (Milestone 29)

**Status:** review package only — not yet linked from README/GLOSSARY as accepted "core".
Johann-OK required before any core promotion.

## What this is

Typed Python helpers that compare the **mean-field** order-parameter scaling of
the corrected cubic normal form ``τ ẋ = -x³ + a x + b`` (``dynamics.core``,
FORMALISM.md §5) against the **exact 2-D Ising** exponent ``β = 1/8``
(Yang 1952) as a **hypothetical counterfactual**. The cubic is mean-field:
observed ratios must match ``β = 1/2`` and disagree with ``β = 1/8``. That
disagreement is the intended **self-falsification** outcome and documents that
``β_crit`` is **model-specific, not universal** (FORMALISM.md §12).

```text
src/scoped_correspondence/
  dynamics/
    core.py           # UNCHANGED — fixed_points (CALL only)
    landau.py         # NEW — mean_field_order_parameter + compare_scaling_exponents
```

M29 does **not** introduce spatial gradients, does **not** derive ``β = 1/8``
via RG, does **not** link to thermo / closure, and does **not** mutate
``dynamics/core.py``, ``FORMALISM.md``, or the layer docs.

Package-level `scoped_correspondence/__init__.py` is **not** rewritten here
(submodule-local wiring via `dynamics/__init__.py` only).

## Mapping

| Source | Claim / formula | API | Notes |
|---|---|---|---|
| cubic equilibria (FORMALISM.md §5; Guckenheimer & Holmes 1983) | ``b=0, a>0`` → ``x* = ±√a`` via ``fixed_points`` | `mean_field_order_parameter` | CALL only — no duplicate ``√a`` |
| mean-field Landau scaling | ``β_MF = 1/2`` | `MEAN_FIELD_BETA` | expected match |
| Yang 1952 DOI 10.1103/PhysRev.85.808 | exact 2-D Ising ``β = 1/8`` | `ISING_2D_BETA` | hypothetical counterfactual |
| Onsager 1944 DOI 10.1103/PhysRev.65.117 | ``T_c/J = 2/ln(1+√2) ≈ 2.269185314213022`` | `onsager_critical_ratio` | **not** ecosystem ``σ≈2.2`` |
| FORMALISM.md §12 | ``β_crit`` model-specific, not universal | `ScalingExponentComparison.beta_crit_note` | self-falsification |

## Formulas

### Mean-field order parameter

For ``b = 0`` and ``a > 0``,

\[
x^*(a) = \text{positive root of } \texttt{fixed\_points}(a, 0)
       = \sqrt{a}.
\]

Do **not** re-implement ``√a`` outside ``fixed_points``.

### Scaling comparison

\[
R_{\mathrm{actual}} = \frac{x^*(a_1)}{x^*(a_2)},\qquad
R_{\mathrm{MF}} = \Bigl(\frac{a_1}{a_2}\Bigr)^{1/2},\qquad
R_{\mathrm{Ising}} = \Bigl(\frac{a_1}{a_2}\Bigr)^{1/8}.
\]

(Equivalently ``x^*(a_2)/x^*(a_1) = (a_2/a_1)^β``; the report uses the
``R > 1`` direction for the worked example.)

Worked example ``a_1 = 0.25``, ``a_2 = 0.0625``:

- ``x* = 0.5`` and ``0.25``
- ``R_actual = R_MF = 2.0`` (exact mean-field)
- ``R_Ising ≈ 1.189207``
- discrepancy factor ``R_MF / R_Ising ≈ 1.681793``

Control ``a_1 = a_2`` → all ratios ``1.0``.

### Onsager critical ratio (scope fence)

\[
\frac{T_c}{J} = \frac{2}{\ln(1+\sqrt{2})} \approx 2.269185314213022.
\]

**WARNING: Onsager critical ratio ≈2.269185314213022 is accidentally near the discarded ecosystem σ≈2.2; this is coincidence only — do not identify them.**

## Sources

- Onsager, L. (1944). Crystal Statistics. I. A Two-Dimensional Model with an
  Order-Disorder Transition. *Phys. Rev.* **65**, 117.
  DOI [10.1103/PhysRev.65.117](https://doi.org/10.1103/PhysRev.65.117)
- Yang, C. N. (1952). The Spontaneous Magnetization of a Two-Dimensional Ising
  Model. *Phys. Rev.* **85**, 808.
  DOI [10.1103/PhysRev.85.808](https://doi.org/10.1103/PhysRev.85.808)
- Guckenheimer, J. & Holmes, P. (1983). *Nonlinear Oscillations, Dynamical
  Systems, and Bifurcations of Vector Fields*.
  DOI [10.1007/978-1-4612-1140-2](https://doi.org/10.1007/978-1-4612-1140-2)

**Do not cite Landau 1937.**

## Out of scope / forbidden

- Spatial gradient / Ginzburg–Landau PDE terms
- RG derivation of ``β = 1/8``
- Links to thermo / closure modules
- Mutation of ``FORMALISM.md``, ``dynamics/core.py``, package-root ``__init__.py``
