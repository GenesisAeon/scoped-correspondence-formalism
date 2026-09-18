# Schnakenberg Network Thermodynamics Core (Milestone 18)

**Status:** review package only — not yet linked from README/GLOSSARY as accepted "core".
Johann-OK required before any core promotion.

## What this is

Typed Python checks for Schnakenberg (1976) network thermodynamics on a
finite-state continuous-time Markov jump process: probability currents,
edge / cycle affinities, and the bilinear entropy-production rate.

```text
src/scoped_correspondence/
  thermo/
    core.py            # UNCHANGED — do not edit (M8 GENERIC / e10 / e13)
    schnakenberg.py    # NEW — J, A, σ (Schnakenberg 1976)
    __init__.py        # submodule-local re-exports (package root untouched)
```

M18 does **not** mutate `thermo/core.py`, package-root
`scoped_correspondence/__init__.py`, `FORMALISM.md`, or
`coupling_layer_afet.md`. It does **not** merge with the M8 deterministic
3-cycle permutation formula (`stochastic_inverse_not_detailed_balance`).
No general network-theory / bond-graph library.

## Mapping

| Source | Claim / formula | API | Notes |
|---|---|---|---|
| Schnakenberg 1976, DOI 10.1103/RevModPhys.48.571 | \(J_{ij}=p_i k_{ij}-p_j k_{ji}\) | `stationary_currents` | antisymmetric current |
| same | \(A_{ij}=\ln(p_i k_{ij}/(p_j k_{ji}))\) | `cycle_affinity` | edge affinity |
| same | \(\sigma=\tfrac12\sum_{ij} J_{ij} A_{ij}\ge 0\) | `entropy_production_rate` | raises if σ < 0 |

## Formulas

### Stationary (probability) current

\[
J_{ij} = p_i k_{ij} - p_j k_{ji}.
\]

### Cycle / edge affinity

\[
A_{ij} = \ln\frac{p_i k_{ij}}{p_j k_{ji}}.
\]

### Entropy production rate

\[
\sigma = \frac12 \sum_{i,j} J_{ij}\, A_{ij}.
\]

The factor \(\tfrac12\) cancels double-counting of \((i,j)\) and \((j,i)\)
(since \(J_{ji}=-J_{ij}\) and \(A_{ji}=-A_{ij}\)).

### Onsager reciprocity (scope note)

**Onsager reciprocity** (\(L_{ij}=L_{ji}\) for linear-response coefficients)
is a **near-equilibrium special case only**. It is **NOT** a general
identity of coupling matrices away from equilibrium. This milestone does
not construct Onsager matrices.

## Worked example (3-cycle)

Clockwise rates \(=2\), counterclockwise rates \(=1\):

\[
k = \begin{pmatrix}
-3 & 2 & 1 \\
1 & -3 & 2 \\
2 & 1 & -3
\end{pmatrix},
\qquad
p = \bigl(\tfrac13,\tfrac13,\tfrac13\bigr).
\]

Stationarity: \(p\,k \approx 0\). Currents on CW edges:
\(J_{01}=J_{12}=J_{20}=\tfrac13\). Affinities: \(A=\ln 2\). Entropy
production:

\[
\sigma = \ln 2 \approx 0.693147.
\]

**Explicitly:** this \(\sigma=\ln 2\) has **no link** to any ecosystem
\(\sigma\approx 2.2\) figure.

### Second off-equilibrium case

CW \(=3\), CCW \(=1\), same uniform \(p\): \(J=\tfrac23\), \(A=\ln 3\),
\(\sigma=2\ln 3\approx 2.197224\). Again **no** ecosystem-\(\sigma\)
identity — the numerical proximity to \(2.2\) is coincidental and must
not be cross-linked.

## API surface

- `stationary_currents(p, k) -> ndarray`
- `cycle_affinity(p, k, i, j) -> float`
- `entropy_production_rate(p, k) -> float` (raises `ScopeViolationError` if σ < 0)
- `SOURCE` — Schnakenberg 1976 citation string with DOI

## Forbidden / out of scope

- Editing `thermo/core.py` or merging with M8 e10 3-cycle
- Package-root `__init__.py`, `FORMALISM.md`, `coupling_layer_afet.md`
- General network theory beyond the three Schnakenberg formulas above
- Claiming Onsager reciprocity as a general coupling-matrix identity
- Linking σ to ecosystem σ ≈ 2.2
