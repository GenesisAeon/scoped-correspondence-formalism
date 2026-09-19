# Pattern Formation / Turing Instability (Milestone 30)

**Status:** review package only — not yet linked from README/GLOSSARY as accepted "core".
Johann-OK required before any core promotion.

## What this is

Typed Python wrappers for the classical **2×2 reaction–diffusion Turing
instability** conditions (homogeneous Routh–Hurwitz, four Turing
inequalities, dispersion relation \(\operatorname{Re}\lambda_{\max}(k)\),
and the Schnakenberg 1979 homogeneous steady state / Jacobian).

```text
src/scoped_correspondence/
  pattern_formation/
    __init__.py
    core.py
```

M30 is a **new independent Baustein**. It does **not** extend
`dynamics/`, does **not** mutate `thermo/schnakenberg.py` (M18),
`FORMALISM.md`, package-root `__init__.py`, or any layer docs. There is
**no** PDE solver and **no** spatial simulation.

## Mandatory scope warnings (verbatim)

1. Schnakenberg 1979 (J Theor Biol) is a DIFFERENT paper than Schnakenberg 1976 (Rev Mod Phys) used in thermo/schnakenberg.py (M18) — different journal/year/claim; do not mix modules.

2. A future correspondence bridge to dynamics is structurally conceivable (Turing S_rec(k) would generalize dynamics.recovery_rate_at_equilibrium as S_rec(0)) but is NOT claimed or implemented here; a real conjugacy would need the correspondence contract with its own proof.

## Sources

| Source | Claim used here | DOI |
|---|---|---|
| Turing 1952, Phil. Trans. R. Soc. Lond. B 237 | linear RD instability / morphogenesis | 10.1098/rstb.1952.0012 |
| Schnakenberg 1979, J. Theor. Biol. 81 | kinetics \(a-u+u^2v\), \(b-u^2v\); steady state / Jacobian | 10.1016/0022-5193(79)90042-0 |
| Murray 2003, Mathematical Biology II | four Turing conditions; \(k_c^2\) formulas | 10.1007/b98869 |

Do **not** confuse Schnakenberg 1979 with Schnakenberg 1976 (Rev. Mod. Phys.; M18 network thermodynamics).

## Mapping

| Claim / formula | API | Notes |
|---|---|---|
| Homogeneous RH: \(\operatorname{tr} J<0\) and \(\det J>0\) | `jacobian_stability` | \(k=0\) only |
| Four Turing conditions (i)–(iv) | `turing_conditions` | returns \(k_c^2\) when (iii) holds |
| \(\operatorname{Re}\lambda_{\max}\) of \(J-k^2\operatorname{diag}(D_u,D_v)\) | `dispersion_relation` | stdlib characteristic polynomial |
| Schnakenberg 1979 SS + Jacobian | `schnakenberg_1979_steady_state` | distinct from M18 |

## Formulas

### Homogeneous stability (2×2)

\[
\operatorname{tr} J = f_u + g_v < 0,\qquad
\det J = f_u g_v - f_v g_u > 0.
\]

### Turing conditions (Murray 2003)

With diffusivities \(D_u, D_v > 0\) and \(h = D_v f_u + D_u g_v\):

1. \(\operatorname{tr} J < 0\)
2. \(\det J > 0\)
3. \(h > 0\)
4. \(h^2 > 4 D_u D_v \det J\)

Critical wave number (when (iii) holds):

\[
k_c^2 = \frac{h}{2 D_u D_v}.
\]

At the onset of instability (equality in (iv)):

\[
k_c^2 = \sqrt{\frac{\det J}{D_u D_v}}.
\]

### Dispersion

\[
A(k) = J - k^2 \operatorname{diag}(D_u, D_v),\qquad
S(k) = \operatorname{Re}\lambda_{\max}\bigl(A(k)\bigr).
\]

### Schnakenberg 1979

\[
u^* = a+b,\qquad v^* = \frac{b}{(a+b)^2},
\]

\[
f_u = \frac{b-a}{a+b},\quad
f_v = (a+b)^2,\quad
g_u = -\frac{2b}{a+b},\quad
g_v = -(a+b)^2.
\]

## Worked example (numbers from verification run)

Parameters \(a=0.1\), \(b=0.9\):

- \(u^*=1.0\), \(v^*=0.9\)
- \(J\): \(f_u=0.8\), \(f_v=1.0\), \(g_u=-1.8\), \(g_v=-1.0\)
- \(\operatorname{tr}=-0.2\), \(\det=1.0\) (homogeneous stable)

With \(D_u=1\), equality (iv) is the quadratic

\[
0.64\, D_v^2 - 5.6\, D_v + 1 = 0,
\]

roots \(D_{v,c}\approx 8.567627\) (larger, Turing-relevant) and
\(\approx 0.182373\) (smaller; fails (iii) for this \(J\)).

At \(D_v = D_{v,c}\) (larger root):

\[
k_c^2 \approx 0.341641
\]

from **both** formulas (must agree).

Dispersion at that \(k_c\):

| \(D_v\) | \(\operatorname{Re}\lambda_{\max}\) |
|---|---|
| \(0.99\, D_{v,c}\) | \(< 0\) (stable) |
| \(D_{v,c}\) | \(\approx 0\) (marginal) |
| \(1.2\, D_{v,c}\) | \(> 0\) (unstable) |

Control: \(D_v=1\) → `turing_conditions` fails (iv) [also (iii)].

## Hand-checkable verification

`verification/verify_pattern_formation_core.py` covers at minimum:

1. Schnakenberg SS / Jacobian / tr / det for \(a=0.1,b=0.9\).
2. Critical \(D_v\) roots of \(0.64 D_v^2-5.6 D_v+1=0\); \(k_c^2\) agreement.
3. Dispersion stable / marginal / unstable across \(0.99,1,1.2\times D_{v,c}\).
4. Control \(D_v=1\) fails Turing (iv).
5. Both mandatory warnings present verbatim in docstrings and JSON.

## Out of scope

- Any mutation of existing Bausteine (`dynamics/`, `thermo/`, package-root
  `__init__.py`, `FORMALISM.md`, layer docs).
- PDE / finite-difference / spectral spatial simulation.
- Claiming a conjugacy to `dynamics.recovery_rate_at_equilibrium`.
- Mixing Schnakenberg 1979 (this module) with Schnakenberg 1976 (M18).
- \(n>2\) species Turing theory.
