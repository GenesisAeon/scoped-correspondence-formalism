# Dissipativity / Supply Rates Core (Milestone 15)

**Status:** review package only — not yet linked from README/GLOSSARY as accepted "core".
Johann-OK required before any core promotion.

## What this is

Typed Python checks for Willems dissipativity: a storage function \(V\) and
supply rate \(w(u,y)\) satisfying the differential dissipation inequality

\[
\dot V(x) \le w(u,y)
\]

(numerically: `V_dot <= w + tol`). Neutral (power-preserving) interconnection
of two ports yields vanishing total supply.

```text
src/scoped_correspondence/
  coupling/
    core.py                 # UNCHANGED — do not edit
    dirac_composition.py    # UNCHANGED — do not edit (M12)
    dissipativity.py        # NEW — storage inequality + neutral supply
    __init__.py             # submodule-local re-exports (package root untouched)
```

M15 does **not** mutate `coupling/core.py`, `coupling/dirac_composition.py`,
`FORMALISM.md`, `coupling_layer_afet.md`, `closure/`, `validation/`, or any
network-theory / bond-graph library. Package-root
`scoped_correspondence/__init__.py` is intentionally **not** edited (avoid
merge fights with parallel M14/M16).

## Mapping

| Source | Claim / formula | API | Notes |
|---|---|---|---|
| Willems 1972, DOI 10.1007/BF00276493 | dissipativity via storage \(V\) and supply \(w\): \(\dot V \le w\) | `check_storage_inequality`, `DissipativityCertificate` | energy-balance contract |
| Neutral interconnection | \(u_1=-y_2\), \(u_2=y_1\) ⇒ \(y_1\cdot u_1+y_2\cdot u_2=0\) | `neutral_interconnection_supply` | identically zero when dims match |

## Formulas

### Storage inequality

\[
\dot V(x) \le w(u,y) + \mathrm{tol}.
\]

### Neutral interconnection supply

\[
w_{\mathrm{total}} = y_1\cdot u_1 + y_2\cdot u_2.
\]

With \(u_1=-y_2\), \(u_2=y_1\): \(w_{\mathrm{total}}=0\).

### Worked example (two LTI ports)

Each subsystem:

\[
\dot x = -x + u,\qquad y = x,\qquad V = \tfrac12 x^2
\quad\Rightarrow\quad
\dot V = -x^2 + y\cdot u.
\]

Under neutral feedback \(u_1=-y_2\), \(u_2=y_1\) the total supply vanishes and

\[
\dot V_{\mathrm{total}} = -(x_1^2 + x_2^2).
\]

At \((x_1,x_2)=(1,2)\): \(\dot V_{\mathrm{total}} = -5\) exactly.
At \((x_1,x_2)=(0.5,1.5)\): \(\dot V_{\mathrm{total}} = -2.5\) exactly.

**Disclaimer:** `DissipativityCertificate` is a **general energy-balance /
supply-rate contract**. It is **NOT** a thermodynamic claim without further
proof (no GENERIC / entropy / heat reinterpretation of \(V\)).

## API surface

- `check_storage_inequality(V_dot, w, tol) -> bool`
- `neutral_interconnection_supply(y1, u1, y2, u2) -> float`
- `DissipativityCertificate` (frozen dataclass; thermo disclaimer in docstring)
- `make_dissipativity_certificate(V_dot, w, tol) -> DissipativityCertificate`
- `STORAGE_INEQUALITY_TOL` (= `1e-10`)
- `SOURCE` / `DISSIPATIVITY_SOURCE` (= Willems 1972 DOI)

## Forbidden (untouched by design)

- `src/scoped_correspondence/coupling/core.py`
- `src/scoped_correspondence/coupling/dirac_composition.py`
- `src/scoped_correspondence/__init__.py` (package root)
- `FORMALISM.md`, `coupling_layer_afet.md`
- thermo reinterpretation of storage; network theory / bond-graph library
- `closure/`, `validation/` trees

## Verification

```text
PYTHONPATH=src python verification/verify_dissipativity_core.py
```

Hand-checkable cases: \(\dot V=-5\) at \((1,2)\); second state pair; one
intentional violate → `check_storage_inequality` returns `False`.
