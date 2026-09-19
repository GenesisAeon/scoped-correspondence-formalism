# Lie–Poisson / Casimir Invariants (Milestone 26)

**Status:** review package only — not yet linked from README/GLOSSARY as accepted "core".
Johann-OK required before any core promotion.

## What this is

Typed Python helpers for the **finite-dimensional** so(3)* rigid-body
Lie–Poisson structure and its quadratic Casimir
\(C(z)=|z|^2/2\), following Arnold (1966) and Marsden & Ratiu (1999).

```text
src/scoped_correspondence/
  coupling/
    core.py       # UNCHANGED — GENERIC check; CALL only
    casimir.py    # NEW — hat_map, casimir_residual, so(3)* example
```

M26 does **not** implement fluid PDEs / continuum Lie–Poisson brackets, does
**not** ship a general Casimir-finder, does **not** mutate `coupling/core.py`,
does **not** rewrite package-root `scoped_correspondence/__init__.py`, and does
**not** edit `FORMALISM.md` or `coupling_layer_afet.md`. Submodule wiring is
via `coupling/__init__.py` only.

**Disclaimer:** this does **NOT** claim that the coupling layer **is** fluid
dynamics. The so(3)* example is a finite-dimensional pedagogical /
diagnostic structure check only.

## Mapping

| Source | Claim | API | Notes |
|---|---|---|---|
| Arnold 1966 DOI 10.5802/aif.233 | so(3) rigid-body reduction | `hat_map`, `lie_poisson_vector_field` | finite-dim only |
| Marsden & Ratiu 1999 DOI 10.1007/978-0-387-21792-5 | Lie–Poisson + Casimir | `casimir_residual`, `quadratic_casimir_grad` | ker(J) check |
| GENERIC core (CALL) | `J @ grad_S == 0` residual | `compare_to_generic_J_grad_S` | matches `max_abs_J_grad_S` |

## Worked example

At \(z=(1,2,3)\):

- \(J=\widehat{z}\) is skew (`max|J^T+J|=0`)
- \(C=|z|^2/2\) ⇒ \(\nabla C=z\) ⇒ `casimir_residual` → `max_abs=0`, `norm=0`
- Rigid body with \(I=(1,2,3)\): \(\dot z=z\times\Omega\), \(\Omega_i=z_i/I_i\)
  ⇒ \(dC/dt=0\) and \(dH/dt=0\)
- Negative: \(\nabla C'=(1,0,0)\) ⇒ residual \(\max=3\neq0\)

## Compatibility with GENERIC

```python
from scoped_correspondence.coupling.casimir import compare_to_generic_J_grad_S, hat_map
from scoped_correspondence.coupling.core import check_generic_structure  # CALL only

J = hat_map([1, 2, 3])
# casimir_residual(...).max_abs  ==  report["residuals"]["max_abs_J_grad_S"]
```

`compare_to_generic_J_grad_S` **calls** `check_generic_structure`; it does not
reimplement the structure check.

## Out of scope

- Fluid / continuum Lie–Poisson (Euler on \(\mathrm{Diff}(\mu)\), Vlasov, MHD)
- General Casimir search for arbitrary Poisson tensors
- Editing `coupling/core.py`, package-root `__init__.py`, `FORMALISM.md`,
  `coupling_layer_afet.md`
