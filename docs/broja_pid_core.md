# BROJA bivariate unique information (Milestone 17)

**Module:** `scoped_correspondence.information_decomposition.broja`  
**Source:** Bertschinger, Rauh, Olbrich, Jost & Ay (2014), *Quantifying Unique Information*, Entropy **16**(4):2161–2183; **DOI [10.3390/e16042161](https://doi.org/10.3390/e16042161)** (arXiv:1311.2852).

## Paper → code mapping

| Bertschinger et al. 2014 | This package |
| --- | --- |
| **X** (target) | **y** |
| **Y** (source 1) | **r1** |
| **Z** (source 2) | **r2** |

## Definitions

Given empirical joint \(P = p(r_1,r_2,y)\), the BROJA feasible set is

\[
\Delta_P = \{ Q : Q(y,r_1)=P(y,r_1),\; Q(y,r_2)=P(y,r_2) \}.
\]

Unique informations:

\[
\begin{aligned}
\mathrm{Unq}_1 &= \mathrm{UI}(y;\, r_1\setminus r_2) = \min_{Q\in\Delta_P} I_Q(y;\, r_1\mid r_2), \\
\mathrm{Unq}_2 &= \mathrm{UI}(y;\, r_2\setminus r_1) = \min_{Q\in\Delta_P} I_Q(y;\, r_2\mid r_1).
\end{aligned}
\]

Because \(Q(y,r_2)\) is fixed on \(\Delta_P\), \(H_Q(y\mid r_2)\) is constant, so minimising
\(I_Q(y;r_1\mid r_2)=H(y\mid r_2)-H(y\mid r_1,r_2)\) equals **maximising** \(H_Q(y\mid r_1,r_2)\).

Redundancy and synergy (Bertschinger et al., identities that agree under BROJA):

\[
\begin{aligned}
\mathrm{Red} &= I_P(y;r_1)-\mathrm{Unq}_1 = I_P(y;r_2)-\mathrm{Unq}_2, \\
\mathrm{Syn} &= I_P(y;r_1,r_2)-\mathrm{Unq}_1-\mathrm{Unq}_2-\mathrm{Red}.
\end{aligned}
\]

Invariant checked by `BivariatePIDReport.assert_pid_sum`:

\[
\mathrm{Red}+\mathrm{Unq}_1+\mathrm{Unq}_2+\mathrm{Syn} = I(y;\,r_1,r_2).
\]

## API

- `broja_pid_bivariate(joint_r1r2y) -> BivariatePIDReport`  
  Fields: `redundancy`, `unique_source_1`, `unique_source_2`, `synergy`, `I_joint`, `method="broja"`.
- Convex opt via `scipy.optimize.minimize` (SLSQP) on free \((n_1-1)\times(n_2-1)\)
  transportation-polytope parameters per \(y\).
- **Convergence:** ≥3 independent starts (observed joint, product coupling given \(y\),
  random free-block perturbations); optima must agree within `tol`.
- `two_bit_copy_broja_report()` — side-by-side Williams-Beer / Blackwell RB(0) / BROJA
  (calls `two_bit_copy_joint`, `pid_atoms_williams_beer`, `rb0_blackwell` from
  `information_decomposition.core`; **core.py is not edited**).

## TWO_BIT_COPY (canonical cross-check)

Independent fair bits \(A,B\); target \(Y=(A,B)\) (4-valued). Expected:

| Measure | Red | Unq1 | Unq2 | Syn |
| --- | --- | --- | --- | --- |
| Williams-Beer \(I_{\min}\) | 1 | 0 | 0 | 1 |
| Blackwell / Kolchinsky RB(0) | 0 (redundancy only) | — | — | — |
| **BROJA** | **≈0** | **≈1** | **≈1** | **≈0** |

BROJA agrees with Blackwell on the unique bits; Williams-Beer \(I_{\min}\) redundancy is misleading here (Harder, Salge & Polani 2013).

## Scope / out of scope (M17)

- **In:** bivariate (two sources), small finite alphabets (`n1·n2·ny ≤ 64`).
- **Out:** N-source generalisation; huge alphabets; edits to package-root
  `__init__.py`, `information_decomposition/core.py`, `FORMALISM.md`,
  `pid_redundancy_bottleneck.md`.

## Input modes (2026-10-01)

`broja_pid_bivariate(joint, ..., input_mode="weights" | "pmf")`. The modes
follow the follow-up review `SCF_FOLLOWUP_REVIEW_637bc1c` §5.

- **`"weights"`** (default, unchanged behaviour):
  - Finite, non-negative weights are renormalised.
  - A doubled mass gives the same atoms.
- **`"pmf"`**:
  - Nested `int`/`Fraction` input must sum to exactly 1.
  - Float input must sum to 1 within `PMF_TOL = 1e-12`, computed with
    `math.fsum`.
- **Both modes:**
  - Non-finite masses, negative masses and overflowing totals are refused
    first (review fix R4).
  - The report carries `input_mode` and `input_total_mass`.

Checks: `verification/verify_information_input_modes.py`.

## Verification

```bash
PYTHONPATH=src python verification/verify_broja_pid_core.py
```

JSON: `verification/verify_broja_pid_core_results.json`.
