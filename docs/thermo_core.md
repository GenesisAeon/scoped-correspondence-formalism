# Thermodynamics / GENERIC Core (Milestone 8)

**Status:** review package only — not yet linked from README/GLOSSARY as accepted "core".
Johann-OK required before any core promotion.

## What this is

Typed Python ports of extension checks **e10** (stochastic inverse ≠ detailed
balance) and **e13** (two-reservoir heat as GENERIC), plus a new congruence
projection helper that re-runs `check_generic_structure` on projected
operators. Mapping: `coupling_layer_afet.md` §§8–9.

```text
src/scoped_correspondence/
  thermo/
    __init__.py
    core.py
```

M8 **calls** `scoped_correspondence.coupling.check_generic_structure`; it does
**not** mutate `coupling/core.py`, `closure/core.py`, `FORMALISM.md`,
`coupling_layer_afet.md`, or the seven layer docs.

## Mapping to coupling_layer_afet.md / e10 / e13

| Document | Claim / formula | API | Legacy |
|---|---|---|---|
| §8 | \(\dot z = \mathbb{J}\nabla E + \mathbb{M}\nabla S_{th}\) structure | `heat_generic_example` → `check_generic_structure` | e13 |
| §3.2 / §8 | Heat: \(M = G T_A T_B\begin{bmatrix}1&-1\\-1&1\end{bmatrix}\), \(J=0\) | `heat_generic_example(ca,cb,G,ta,tb)` | e13 |
| §8 | \(\dot S_{th}=(\nabla S)^T M \nabla S = G(T_A-T_B)^2/(T_A T_B)\) | return key `entropy_production` | e13 |
| §9 | Stochastic inverse ≠ detailed balance (3-cycle) | `stochastic_inverse_not_detailed_balance` | e10 |
| §9 | Projection may wipe dissipation / invalid reduce | `project_generic_structure` | new |

## Formulas

### Heat GENERIC (e13)

Energies \(E=(C_A T_A,\, C_B T_B)\). With total energy \(E_{\mathrm{tot}}=z_A+z_B\),
\(\nabla E=[1,1]\). Entropy gradient \(\nabla S=(1/T_A,\,1/T_B)\) (analytic,
checked by central finite difference). Dissipation matrix

\[
\mathbb{M}=G\,T_A T_B\begin{pmatrix}1&-1\\-1&1\end{pmatrix},\qquad
\mathbb{J}=0.
\]

Heat current \(J_{\mathrm{heat}}=G(T_A-T_B)\); flow \(\mathbb{M}\nabla S=(-J_{\mathrm{heat}},\,J_{\mathrm{heat}})\);
entropy production \(G(T_A-T_B)^2/(T_A T_B)\ge 0\). Structure check uses
`grad_E=[1,1]` because \(\mathbb{M}[1,1]^\top=0\) already in e13.

### Stochastic inverse (e10)

Permutation matrix \(P\) for the 3-cycle \(0\to1\to2\to0\) is stochastically
invertible (\(P^{-1}\) row-stochastic, \(P P^{-1}=I\)) with uniform stationary
measure, yet the probability flow \(\mu_i P_{ij}\) is **not** symmetric
(\(f_{01}=1/3\), \(f_{10}=0\)) — hence **not** detailed balance
(`coupling_layer_afet.md` §9).

### Congruence projection (new)

\[
J'=\Pi J \Pi^\top,\qquad M'=\Pi M \Pi^\top.
\]

`project_generic_structure(J, M, Pi, grad_E_prime, grad_S_prime)` takes
**explicit** projected gradients — **no** silent default \(\Pi\nabla E\) /
\(\Pi\nabla S\). It only checks algebraic structure under congruence; it does
**not** claim \((\nabla E',\nabla S')\) are valid reduced energy/entropy
potentials (§9).

Verify cases from the heat example:

| \(\Pi\) | \(M'\) | Algebraic | Reduced GENERIC? |
|---|---|---|---|
| \([[1,1]]\) (sum) | \(0\) (from \(M[1,1]^\top=0\)) | may pass (wiped dissipation) | **No** claim |
| $[[1,0]]$ (single reservoir) | $M_{00}=G T_A T_B$ | may pass only with caller `grad_E'=[0]` (else $M'\nabla E'\ne0$) | **Not** a valid reduced GENERIC system |

## Hand-checkable verification

`verification/verify_thermo_core.py` matches e13 evidence against
`verification/extension_results.json` for **all 32** parameter combinations,
matches e10 evidence exactly, and records both \(\Pi\) projection cases with
\(M'\) and the §9 disclaimer.

## Out of scope

Mutation of `coupling/core.py`, `closure/core.py`, `FORMALISM.md`,
`coupling_layer_afet.md`, sheaf/PID docs, seven layer docs; ODE integration;
Mori–Zwanzig theory rewrite.
