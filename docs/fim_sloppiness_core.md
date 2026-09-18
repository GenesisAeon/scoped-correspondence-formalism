# Fisher-Information Sloppiness Core (Milestone 23)

**Status:** review package only — not yet linked from README/GLOSSARY as accepted "core".
Johann-OK required before any core promotion.

## What this is

Typed Python helpers for **Fisher-information geometry / sloppiness** following
Transtrum, Machta & Sethna 2011
(DOI [10.1103/PhysRevE.83.036701](https://doi.org/10.1103/PhysRevE.83.036701))
and the stiff / sloppy eigendirection language of Raju et al. 2018
(Phys. Rev. E 98, 052112; DOI [10.1103/PhysRevE.98.052112](https://doi.org/10.1103/PhysRevE.98.052112)).

Given an observation Jacobian \(J = \partial f / \partial \theta\)
(shape \(n_{\mathrm{obs}} \times n_{\mathrm{params}}\)) and homogeneous noise
scale \(\sigma > 0\),

\[
g = \frac{J^{\mathsf{T}} J}{\sigma^{2}}.
\]

The eigenspectrum of \(g\) separates **stiff** directions (large \(\lambda\):
well-constrained combinations of parameters) from **sloppy** directions
(small \(\lambda\): poorly constrained). Anisotropy \(\lambda_{\max}/\lambda_{\min}\)
quantifies the metric spread.

```text
src/scoped_correspondence/
  identifiability/
    core.py                  # UNCHANGED — Jacobian/SVD/EI; not edited
    profile_likelihood.py    # UNCHANGED — M20 PL; not edited
    fim_sloppiness.py        # NEW — FIM + eigenspectrum / anisotropy
```

M23 does **not** equate FIM / anisotropy to `identifiability_jacobian_rank`
(SVD rank of \(J\)) as the same formula; does **not** implement general ODE
forward models; does **not** mutate `identifiability/core.py`,
`profile_likelihood.py`, package-root `scoped_correspondence/__init__.py`,
`FORMALISM.md`, or the layer docs.

Package-level wiring is **submodule-local** via `identifiability/__init__.py`
only.

## Mapping (sources)

| Source | Claim / formula | API | Notes |
|---|---|---|---|
| Transtrum/Machta/Sethna 2011 DOI 10.1103/PhysRevE.83.036701 | \(g = J^{\mathsf{T}}J/\sigma^{2}\) | `fisher_information_matrix` | algebraic Jacobian demos |
| Transtrum/Machta/Sethna 2011; Raju et al. 2018 | stiff = large \(\lambda\), sloppy = small \(\lambda\) | `eigenspectrum_report` | descending eigenvalues |
| Raju et al. 2018 PRE 98, 052112 | anisotropy \(\lambda_{\max}/\lambda_{\min}\) | `eigenspectrum_report["anisotropy"]` | identity → 1 |
| (contrast) M5 Jacobian / SVD rank | local structural rank | `identifiability.core` | **not** rewritten as FIM |

## Formulas

### Fisher information (Gaussian noise)

\[
g_{ab}
  = \frac{1}{\sigma^{2}}
    \sum_{i=1}^{n_{\mathrm{obs}}}
      \frac{\partial f_i}{\partial \theta_a}
      \frac{\partial f_i}{\partial \theta_b}
  = \bigl(J^{\mathsf{T}} J / \sigma^{2}\bigr)_{ab}.
\]

### Eigenspectrum / anisotropy

With \(g v_k = \lambda_k v_k\) and \(\lambda_1 \ge \cdots \ge \lambda_p > 0\),

\[
\mathrm{anisotropy}
  = \frac{\lambda_{\max}}{\lambda_{\min}}
  = \frac{\lambda_1}{\lambda_p}.
\]

- **Stiff direction:** \(v_1\) (largest \(\lambda\)).
- **Sloppy direction:** \(v_p\) (smallest \(\lambda\)).
- **Isotropic control:** \(g = I\) ⇒ all \(\lambda = 1\) ⇒ anisotropy \(= 1\).

Singular / non-positive \(\lambda_{\min}\) is out of scope for this helper
(`ScopeViolationError`).

## Hand-derivable demo

Model \(f(\theta_1,\theta_2,t)=\theta_1\exp(-\theta_2 t)\) at two times
\(t\in\{t_1,t_2\}\):

\[
\frac{\partial f}{\partial \theta_1}=\mathrm{e}^{-\theta_2 t},\qquad
\frac{\partial f}{\partial \theta_2}=-\theta_1 t\,\mathrm{e}^{-\theta_2 t}.
\]

Concrete run (\(\theta=(1,1)\), \(t=\{1,2\}\), \(\sigma=1\)) — numbers from
`verification/verify_fim_sloppiness_core.py`:

| Quantity | Value (from run) |
|---|---|
| \(\lambda_{\max}\) (stiff) | ≈ 0.35527 |
| \(\lambda_{\min}\) (sloppy) | ≈ 0.006977 |
| anisotropy \(\lambda_{\max}/\lambda_{\min}\) | ≈ 50.92 |
| isotropic \(g=I\) anisotropy | 1.0 |

Helper `exponential_decay_jacobian(theta, times)` returns the analytic \(J\)
above (demo only — not a general ODE sensitivity engine).

## API

```python
from scoped_correspondence.identifiability.fim_sloppiness import (
    fisher_information_matrix,
    eigenspectrum_report,
    exponential_decay_jacobian,
)

J = exponential_decay_jacobian([1.0, 1.0], [1.0, 2.0])
g = fisher_information_matrix(J, sigma=1.0)
rep = eigenspectrum_report(g)
# rep["anisotropy"], rep["stiff_direction"], rep["sloppy_direction"]
```

## Forbidden / untouched

- Do **not** edit `identifiability/core.py` or `profile_likelihood.py`.
- Do **not** edit package-root `scoped_correspondence/__init__.py`.
- Do **not** edit `FORMALISM.md` or the layer docs.
- Do **not** equate FIM to Jacobian-rank / SVD as the same formula.
- Do **not** add general ODE model frameworks.

## Verification

```text
PYTHONPATH=src python verification/verify_fim_sloppiness_core.py
```

Writes `verification/verify_fim_sloppiness_core_results.json`.
