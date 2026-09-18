# Contraction Analysis Core (Milestone 14)

**Status:** review package only — not yet linked from README/GLOSSARY as accepted "core".
Johann-OK required before any core promotion.

## What this is

Typed Python helpers for **1-D Euclidean contraction analysis** of the cusp
normal form ``τ ẋ = -x³ + a x + b``, following Lohmiller & Slotine 1998.
When ``a < 0`` the field is globally contracting with rate ``λ = -a/τ``;
when ``a ≥ 0`` the analytical rate is ``None`` (bistability / non-contraction
scope — not an error).

```text
src/scoped_correspondence/
  dynamics/
    core.py           # UNCHANGED — cusp_field / CubicNormalForm (CALL only)
    contraction.py    # NEW — contraction_rate_cusp + ContractionCertificate
```

M14 does **not** introduce multi-D contraction metrics, does **not** add a
new bistability formula, and does **not** mutate ``dynamics/core.py``,
``FORMALISM.md``, or the layer docs.

Package-level `scoped_correspondence/__init__.py` is **not** rewritten here
(submodule-local wiring via `dynamics/__init__.py` only — avoids fighting
parallel M15/M16 branches on the shared package `__init__`).

## Mapping

| Source | Claim / formula | API | Notes |
|---|---|---|---|
| Lohmiller & Slotine 1998, DOI 10.1016/S0005-1098(98)00019-3 | contraction: ``f' ≤ -λ`` everywhere (1-D Euclidean) | `contraction_rate_cusp`, `ContractionCertificate` | rate ``λ = -sup f'`` when ``sup f' < 0`` |
| cusp field (FORMALISM.md §5) | ``f = (-x³+ax+b)/τ``, ``f' = (-3x²+a)/τ``, ``sup f' = a/τ`` at ``x=0`` | `verify_contraction_bound` | finite-diff on `cusp_field` (CALL only) |
| cusp bistability | ``a ≥ 0`` → no global Euclidean contraction | `rate is None` | scope, not `ScopeViolationError` |

## Formulas

### Jacobian of the cusp field

\[
f(x) = \frac{-x^3 + a x + b}{\tau},\qquad
f'(x) = \frac{-3x^2 + a}{\tau}.
\]

Since ``-3x² ≤ 0``,

\[
\sup_x f'(x) = \frac{a}{\tau}\quad\text{(attained at }x=0\text{)}.
\]

### Global contraction rate

\[
\lambda =
\begin{cases}
-a/\tau & \text{if }a < 0,\\
\text{undefined (``None``)} & \text{if }a \ge 0.
\end{cases}
\]

When ``a < 0``, ``f'(x) ≤ a/τ = -λ`` for all ``x``, so the system is globally
contracting in the Euclidean 1-D metric with rate ``λ``
(Lohmiller & Slotine 1998).

### Numerical bound check

`verify_contraction_bound(a, tau, x_samples)` estimates ``f'`` at each sample
by a central finite difference of `cusp_field` (``b=0``; ``core.py`` called,
not edited) and requires ``estimated_f' ≤ -rate + atol`` whenever
``rate is not None``.

## Worked examples (hand-checkable)

### Example A — contracting (``a = -1``, ``τ = 1``)

\[
\sup f' = a/\tau = -1,\qquad \lambda = -a/\tau = 1.0.
\]

`is_globally_contracting = True`. Finite-diff on a grid including ``x=0``
confirms ``f' ≤ -1``.

### Example B — bistability scope (``a = 1``, ``τ = 1``)

\[
\sup f' = 1 > 0 \implies \text{rate = None},\quad
\text{is_globally_contracting = False}.
\]

This is **not** an error: the cusp is in its bistable / non-contracting
regime. Callers must not treat ``None`` as a failure of the API.

### Example C — scaled (``a = -2``, ``τ = 2``)

\[
\lambda = -(-2)/2 = 1.0.
\]

Same rate as Example A; time-scale and linear coefficient cancel.

## Out of scope (M14)

- Multi-dimensional / Riemannian contraction metrics
- New bistability formulas beyond returning ``rate=None`` for ``a≥0``
- Edits to ``dynamics/core.py``, package-root `__init__.py`, `FORMALISM.md`,
  or layer docs (`system_layer_utac.md`, …)

## Source

Lohmiller, W. & Slotine, J.-J. E. (1998). On Contraction Analysis for
Non-linear Systems. *Automatica*, 34(6), 683–696.
DOI [10.1016/S0005-1098(98)00019-3](https://doi.org/10.1016/S0005-1098(98)00019-3).
