# Crooks Fluctuation Theorem Core (Milestone 37)

**Status:** review package only -- not yet linked from README/GLOSSARY as accepted "core".
Johann-OK required before any core promotion.

## What this is

Typed Python checks for the Crooks (1999) nonequilibrium work fluctuation
theorem and the Jarzynski free-energy estimator on a forward work ensemble.

```text
src/scoped_correspondence/
  thermo/
    core.py            # UNCHANGED -- do not edit (M8 GENERIC / e10 / e13)
    schnakenberg.py    # UNCHANGED -- do not edit (M18)
    crooks.py          # NEW -- ω, e^ω, Crooks ratio check, Jarzynski ΔF̂
    __init__.py        # submodule-local re-exports (package root untouched)
```

M37 does **not** mutate `thermo/core.py`, `thermo/schnakenberg.py`,
package-root `scoped_correspondence/__init__.py`, `FORMALISM.md`, or
`coupling_layer_afet.md`. It does **not** merge with Schnakenberg
currents/affinities and does **not** identify Onsager `L_ij` with
affinities `A_ij`. No Metropolis / path-integral sampler.

## Mapping

| Source | Claim / formula | API | Notes |
|---|---|---|---|
| Crooks 1999, DOI 10.1103/PhysRevE.60.2721 | \(\omega=\beta(W-\Delta F)\) | `work_ratio` | returns \((\omega,e^\omega)\) |
| same; arXiv cond-mat/9901352 | \(P_F(+\omega)/P_R(-\omega)=e^{+\omega}\) | `verify_crooks_ratio` | density ratio check |
| same (Jarzynski equality) | \(\langle e^{-\beta W}\rangle=e^{-\beta\Delta F}\) | `jarzynski_estimate` | \(\Delta\hat F=-\beta^{-1}\ln\langle e^{-\beta W}\rangle\) |

## Formulas

### Crooks exponent and ratio

\[
\omega = \beta\,(W - \Delta F),\qquad
\frac{P_F(+\omega)}{P_R(-\omega)} = e^{+\omega}.
\]

Equivalently, at a fixed work value \(W\),

\[
\frac{P_F(W)}{P_R(-W)} = e^{\beta(W-\Delta F)}.
\]

### Jarzynski equality

\[
\langle e^{-\beta W}\rangle_F = e^{-\beta\Delta F}
\quad\Rightarrow\quad
\Delta\hat F = -\beta^{-1}\ln\langle e^{-\beta W}\rangle_F.
\]

### Scope fences

- **NOT Onsager** \(L_{ij}/A_{ij}\): this milestone does not construct
  linear-response Onsager matrices and does not identify them with
  Schnakenberg affinities.
- **NOT Schnakenberg M18**: no \(J_{ij}\), no cycle affinity \(A_{ij}\),
  no bilinear \(\sigma=\tfrac12\sum J A\). Crooks is a trajectory /
  work-ensemble fluctuation theorem.

## Worked examples

### Mini-example (hand-checkable)

\(\beta=1\), \(\Delta F=0\), \(W=1\):

\[
\omega = 1,\qquad e^{\omega}=e\approx 2.718281828459045.
\]

With densities \(P_F=e\), \(P_R=1\), `verify_crooks_ratio` reports `ok=True`.

### Control (equilibrium work)

\(W=\Delta F\) (any \(\beta>0\)): \(\omega=0\), \(e^{\omega}=1\).
Ratio \(P_F/P_R=1\) passes the Crooks check.

### Jarzynski Gaussian toy

Draw \(W\sim\mathcal N(\Delta F + \sigma^2\beta/2,\,\sigma^2)\). The
infinite-sample exponential average recovers \(\Delta F\) exactly; finite
samples converge for large \(N\) (stable log-mean-exp in
`jarzynski_estimate`).

## Source

Gavin E. Crooks, *Entropy production fluctuation theorem and the
nonequilibrium work relation for free energy differences*, Phys. Rev. E
**60**, 2721–2726 (1999).

- DOI: `10.1103/PhysRevE.60.2721`
- arXiv: `cond-mat/9901352`

## Untouched (confirm after apply: `git diff --name-only`)

- `src/scoped_correspondence/thermo/core.py`
- `src/scoped_correspondence/thermo/schnakenberg.py`
- `src/scoped_correspondence/__init__.py` (package root)
- `FORMALISM.md`, layer docs

## Branch

`aeon/m37-crooks-fluctuation-theorem` from `origin/master`. **NO merge.**
