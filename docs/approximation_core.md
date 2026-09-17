# Approximation Certificates Core (Milestone 10)

**Status:** review package only — not yet linked from README/GLOSSARY as accepted "core".
Johann-OK required before any core promotion.

## What this is

Typed Python certificate that interprets existing conjugacy residuals of a
**fixed** `StateMap T` against an explicit error budget \(\varepsilon\).
Exact conjugacy (`ErrorMetric.near` zero) is the zero-error special case.

```text
src/scoped_correspondence/
  correspondence/
    contract.py          # UNCHANGED — conjugacy_residual / verify_conjugacy
    approximation.py     # NEW — ApproximationCertificate + verify_approximate_simulation
```

M10 **calls** `Correspondence.conjugacy_residual` / `verify_conjugacy` only.
It does **not** mutate `correspondence/contract.py`, `FORMALISM.md`, or the
seven layer docs.

## Mapping

| Source | Claim / formula | API | Notes |
|---|---|---|---|
| Girard & Pappas 2007, DOI 10.1109/TAC.2007.895849 | approximate simulation via pseudometric with budget \(\varepsilon\); exact = zero-error special case | `ApproximationCertificate`, `verify_approximate_simulation` | **fixed-\(T\) specialty only** |
| FORMALISM.md §1 | \(T\circ\Phi_j^t \approx \Phi_k^{ct}\circ T\) | residual from `conjugacy_residual` | unchanged contract |
| `correspondence/contract.py` | `conjugacy_residual` / `verify_conjugacy` | called, not edited | M1 API freeze |

## Formulas

### Conjugacy residual (existing)

\[
r(x,t) = \bigl\| T\bigl(\Phi_j^t(x)\bigr) - \Phi_k^{c\,t}\bigl(T(x)\bigr) \bigr\|_\infty
\]

(`Correspondence.conjugacy_residual`, FORMALISM.md §1).

### Fixed-map \(\varepsilon\)-certificate (this milestone)

\[
\mathrm{ok} \iff \max_{(x,t)\in\mathrm{sample}} r(x,t) \le \varepsilon
\]

with `relation_kind = "fixed_map_bound"`.

**Disclaimer (analogous to `check_generic_structure`):** an `ok=True`
certificate does **not** prove existence of a general (relational)
simulation / bisimulation relation in the sense of Girard & Pappas. It
only bounds the residuals of the **given fixed** `StateMap T` on the
sampled \((x,t)\) pairs inside the declared `Scope`.

## Worked example (analytic flows; no ODE integrate)

\[
\dot x = -x,\qquad \dot y = -y + 0.1,\qquad x(0)=y(0)=0.
\]

Exact solutions: \(x(t)=0\), \(y(t)=0.1(1-e^{-t})\). Hence

\[
|x(t)-y(t)| = 0.1(1-e^{-t}) \le 0.1 \quad \forall\, t\ge 0
\]

(limit \(0.1\) as \(t\to\infty\), never exceeded).

`Correspondence` with `source.flow` / `target.flow` from these exact
solutions, `state_map = StateMap(identity)`, time scale \(c=1\):

| \(\varepsilon\) | expected `ok` | reason |
|---|---|---|
| \(0.1\) | `True` | \(\max_t 0.1(1-e^{-t}) \le 0.1\) on \(t\in[0,10]\) |
| \(0.05\) | `False` | residual approaches \(0.1 > 0.05\) for large \(t\) |

Control: identical flows \(\Rightarrow\) `max_residual == 0`, any
\(\varepsilon \ge 0\) yields `ok=True`.

## Hand-checkable verification

`verification/verify_approximation_core.py` covers:

1. \(\varepsilon=0.1\) → `ok=True` (numbers from run).
2. \(\varepsilon=0.05\) → `ok=False` (numbers from run).
3. Zero-error identical flows → `max_residual==0`, `ok=True` for any
   \(\varepsilon\ge 0\).

## Out of scope

Mutation of `correspondence/contract.py`, `FORMALISM.md`, seven layer
docs; general relational simulation / bisimulation; `RelationKind` enum;
API changes to `CorrespondenceReport` / `Residual` / `ErrorMetric`;
renaming `thermo` / `conjugacy_residual` / `ErrorMetric`.
