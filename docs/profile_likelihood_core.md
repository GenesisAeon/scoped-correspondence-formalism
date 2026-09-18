# Profile Likelihood Core (Milestone 20)

**Status:** review package only — not yet linked from README/GLOSSARY as accepted "core".
Johann-OK required before any core promotion.

## What this is

Typed Python helpers for **profile likelihood** following Raue et al. 2009
(DOI [10.1093/bioinformatics/btp358](https://doi.org/10.1093/bioinformatics/btp358)).
Given an algebraic cost \(\chi^2(\theta)\), the profile of component \(\theta_i\) is

\[
\chi^2_{\mathrm{PL}}(\theta_i)
  = \min_{\theta_j,\, j\neq i} \chi^2(\theta).
\]

A **flat** profile (near-constant \(\chi^2_{\mathrm{PL}}\) on the scanned grid)
signals practical non-identifiability; a **curved** profile that rises above a
likelihood-ratio threshold yields a finite confidence interval.

```text
src/scoped_correspondence/
  identifiability/
    core.py                  # UNCHANGED — Jacobian/SVD/EI baselines; not edited
    profile_likelihood.py    # NEW — profile_parameter + classify + interval
```

M20 does **not** implement ODE forward models, general multi-parameter NLP,
or equate profile likelihood to `identifiability_jacobian_rank` / SVD as the
same formula. It does **not** mutate `identifiability/core.py`, package-root
`scoped_correspondence/__init__.py`, `FORMALISM.md`, or the layer docs.

Package-level wiring is **submodule-local** via `identifiability/__init__.py`
only.

## Mapping (Raue et al. 2009)

| Source | Claim / formula | API | Notes |
|---|---|---|---|
| Raue et al. 2009, DOI 10.1093/bioinformatics/btp358 | \(\chi^2_{\mathrm{PL}}(\theta_i)=\min_{j\neq i}\chi^2(\theta)\) | `profile_parameter` | algebraic \(\chi^2\) demos only |
| Raue et al. 2009 | flat profile ⇒ practically non-identifiable | `classify_identifiability` | `"flat"` iff \(\mathrm{Var}(\chi^2_{\min}) < \mathrm{atol}\) |
| Raue et al. 2009 | LR set \(\{\theta_i:\chi^2_{\mathrm{PL}}-\chi^{2*}\le\Delta_\alpha\}\) | `likelihood_interval` | flat profiles report **unbounded** explicitly |
| (contrast) M5 Jacobian / SVD rank | local structural tests | `identifiability.core` | **not** rewritten as profile PL |

## Formulas

### Profile likelihood

For fixed grid values \(v\) of \(\theta_i\),

\[
\chi^2_{\min}(v)
  = \min_{\theta_{\setminus i}} \chi^2(\theta)\Big|_{\theta_i=v}.
\]

`profile_parameter(chi2_fn, theta_fixed_index, theta_init, fixed_values)`
returns `[(v, chi2_min(v)), ...]`. Free-parameter minimization is a **1-D**
coarse grid + golden-section refine (at most one free coordinate). Zero free
coordinates (1-D \(\theta\)) evaluate \(\chi^2([v])\) directly. Two or more
free coordinates raise `ScopeViolationError` (no general NLP).

### Classification

\[
\mathrm{classify} =
\begin{cases}
\texttt{"flat"} & \text{if }\mathrm{Var}(\{\chi^2_{\min}(v)\}) < \mathrm{atol}, \\
\texttt{"identifiable"} & \text{otherwise.}
\end{cases}
\]

### Likelihood-ratio interval

With \(\chi^{2*}=\min_v \chi^2_{\min}(v)\) and threshold \(\Delta\ge 0\),

\[
\mathcal{C}_\Delta
  = \{ v : \chi^2_{\min}(v) - \chi^{2*} \le \Delta \}.
\]

- **Flat** profiles → `unbounded=True`, `unbounded_reason="flat_profile"`,
  `lower=upper=None`.
- **Identifiable** profiles whose in-set is strictly inside the scanned grid
  → finite `lower` / `upper` from the discrete grid.
- In-set touching a grid endpoint → `open_at_grid_boundary` (may continue
  outside the scan).

### Out of scope (explicit)

- ODE / dynamical-model integration inside the profile loop
- General multi-parameter NLP / global optimization beyond 1-D algebraic refine
- Equating PL to Jacobian rank or SVD emergence formulas in `core.py`
- Editing `FORMALISM.md` or layer docs

## Worked examples (hand-checkable)

### A — Non-identifiable product (flat)

\[
\chi^2(\theta_1,\theta_2) = (\theta_1\cdot\theta_2 - 6)^2.
\]

Profile \(\theta_1\in\{1,2,3,4,5\}\) with \(\theta_{\mathrm{init}}=(3,2)\):
for each fixed \(\theta_1=v\), choosing \(\theta_2=6/v\) gives
\(\chi^2_{\min}=0\). All five minima are 0 → variance 0 → **`"flat"`**.
`likelihood_interval(..., threshold=1.0)` reports **unbounded**
(`unbounded_reason="flat_profile"`).

### B — Identifiable quadratic (control)

\[
\chi^2(\theta) = (\theta - 3)^2.
\]

Profile \(\theta\in\{0,1,2,3,4,5,6\}\): \(\chi^2_{\min}\) values are
\(9,4,1,0,1,4,9\) → variance \(\gg 0\) → **`"identifiable"`**.
With threshold \(\Delta=1\), the LR set on the grid is \(\{2,3,4\}\)
→ finite interval **`[2, 4]`**.

## Verification

```bash
PYTHONPATH=src python verification/verify_profile_likelihood_core.py
```

Writes `verification/verify_profile_likelihood_core_results.json`.

## Source

Raue, A., Kreutz, C., Maiwald, T., Bachmann, J., Schilling, M., Klingmüller, U.,
& Timmer, J. (2009). Structural and practical identifiability analysis of
partially observed dynamical models by exploiting the profile likelihood.
*Bioinformatics*, 25(15), 1923–1929.
DOI: [10.1093/bioinformatics/btp358](https://doi.org/10.1093/bioinformatics/btp358)
