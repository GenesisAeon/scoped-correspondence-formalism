# Early-Warning / Critical Slowing Down (Milestone 36)

**Status:** optional / review package. Not a new Baustein; submodule-local
extension of `dynamics`. Package-root `scoped_correspondence/__init__.py`
is **not** rewritten. `dynamics/core.py` is **not** edited (CALL only).

## What this is

Scheffer et al. (2009) translate critical slowing — recovery rate
`λ = S_rec → 0⁺` near a bifurcation — into **observable** time-series
statistics: rising variance and rising lag-1 autocorrelation. This milestone
wires those OU / AR(1) formulas to the existing cusp recovery rate

```text
λ = S_rec = recovery_rate_at_equilibrium(x, a, tau, b)
```

from `dynamics.core` (FORMALISM.md §5). It does **not** reimplement `S_rec`.

```text
src/scoped_correspondence/
  dynamics/
    core.py              # UNCHANGED — recovery_rate_at_equilibrium
    early_warning.py     # NEW — ou_variance, ou_autocorrelation, …
```

## Formulas

### Stationary OU variance

For `dx = −λ x dt + σ dW` with `λ > 0`,

\[
\mathrm{Var}_\infty = \frac{\sigma^2}{2\lambda}.
\]

API: `ou_variance(sigma, lam)`. Raises `ScopeViolationError` if `λ ≤ 0`.

### Autocorrelation

\[
\rho(\Delta t) = \exp(-\lambda \cdot \Delta t).
\]

API: `ou_autocorrelation(lam, delta_t)`.

### Inverse AR(1)

\[
\hat\lambda = -\frac{\ln\rho}{\Delta t}.
\]

API: `estimate_lambda_from_ar1(rho, delta_t)`.

### Link to cusp `S_rec`

For the corrected cubic `τ ẋ = −x³ + a x + b` at a stable branch
(e.g. `b = 0`, `x* = ±√a`, `a > 0`):

\[
S_{\mathrm{rec}}(x^*) = \frac{2a}{\tau}
\]

via `recovery_rate_at_equilibrium` (CALL core — not reimplemented here).

### Worked example

`b = 0`, `τ = 1`, `σ² = 0.02`, `Δt = 1`:

| `a` | `x*` | `S_rec = 2a` | `Var = σ²/(2λ)` | `ρ = e^{−λ}` |
|---|---|---|---|---|
| 0.5 | `√0.5` | 1.0 | 0.01 | ≈ 0.367879 |
| 0.05 | `√0.05` | 0.1 | 0.1 | ≈ 0.904837 |

Inverse: `estimate_lambda_from_ar1(0.904837, 1) → 0.1` exactly (to float
tolerance of `e^{−0.1}`).

**Control:** far from the fold (large `a`, large `λ`), variance and
autocorrelation stay moderate across two parameter sets — no critical-slowing
blow-up.

## Counterexample section — necessary ≠ sufficient

**Mandatory fence (verbatim):**
Boettiger & Hastings 2012 DOI 10.1098/rsif.2012.0125; Ditlevsen & Johnsen 2010 DOI 10.1029/2010GL044486 — rising Var/ρ necessary near λ→0 but NOT sufficient; false alarms; D-O events noise-induced. Also: no Var/S_rec ≡ beta_response.

Rising variance / autocorrelation is a **necessary** signature of
`λ → 0` under the OU linearization, but it is **not sufficient** to conclude
that a bifurcation is imminent:

| Paper | Claim relevant to M36 |
|---|---|
| Boettiger & Hastings 2012 DOI 10.1098/rsif.2012.0125 | Early-warning indicators can produce **false alarms**; statistical detectability is limited. |
| Ditlevsen & Johnsen 2010 DOI 10.1029/2010GL044486 | Dansgaard–Oeschger (D-O) events can be **noise-induced** transitions without approaching a bifurcation — so rising indicators need not precede them. |
| Scheffer et al. 2009 DOI 10.1038/nature08227 | Primary framing: variance + autocorrelation as EWS under critical slowing. |

Also hard fence: **no** identification `Var` / `S_rec` ≡ `beta_response`.
Those are different quantities (units: variance vs 1/time vs 1/[u]); see
`recovery_rate_from_relaxation` docstring (“Independence of beta_response”).

## Mapping

| Source | Claim / formula | API | Notes |
|---|---|---|---|
| `dynamics.core` | `S_rec = (3x² − a)/τ` | `lambda_from_cusp_equilibrium` | CALL only |
| Scheffer 2009 | Var↑, ρ↑ as λ→0 | `ou_variance`, `ou_autocorrelation` | primary EWS |
| OU / AR(1) inverse | `λ̂ = −ln(ρ)/Δt` | `estimate_lambda_from_ar1` | exact inverse |
| Boettiger & Hastings 2012 | false alarms | docs + fence | necessary ≠ sufficient |
| Ditlevsen & Johnsen 2010 | D-O noise-induced | docs + fence | no bifurcation required |

## Sources

- Scheffer, M. et al. (2009). Early-warning signals for critical transitions.
  *Nature* **461**, 53–59.
  DOI [10.1038/nature08227](https://doi.org/10.1038/nature08227)
- Boettiger, C. & Hastings, A. (2012). Early warning signals and the
  prosecutor's fallacy. *J. R. Soc. Interface*.
  DOI [10.1098/rsif.2012.0125](https://doi.org/10.1098/rsif.2012.0125)
- Ditlevsen, P. D. & Johnsen, S. J. (2010). Tipping points: Early warning and
  wishful thinking. *Geophys. Res. Lett.* **37**, L19703.
  DOI [10.1029/2010GL044486](https://doi.org/10.1029/2010GL044486)

## Out of scope

- Editing `dynamics/core.py` or package-root `__init__.py`
- Equating `Var` / `S_rec` with `beta_response`
- Claiming rising Var/ρ is **sufficient** for an impending bifurcation
- Merging parallel M33–M35 branches (wire only what is on master + this module)
