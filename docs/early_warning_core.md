# Early-Warning Signals / Critical Slowing Down (Milestone 36)

**Status:** review package — Johann-OK required before core promotion.
**Implemented directly by Claude** (not Aeon) because Aeon's Grok-agent
usage volume was exhausted for the next five days when this milestone
came up in Round 3; same review discipline applies (own branch, additive
only, hand-checkable worked example, Johann-OK before merge).

## What this is

Translates the existing `dynamics.core.recovery_rate_at_equilibrium`
(`S_rec`) into observable time-series statistics near a bifurcation:
rising variance and autocorrelation as `S_rec → 0` ("critical slowing
down"). This is a pure **model computation** (Verification side), not a
real-data estimator (that stays out of scope — see below).

```text
src/scoped_correspondence/
  dynamics/
    early_warning.py
```

Calls `dynamics.core.recovery_rate_at_equilibrium` and `fixed_points`
unchanged. Does **not** edit `dynamics/core.py`.

## Source

M. Scheffer et al., "Early-warning signals for critical transitions",
Nature 461, 53–59 (2009), DOI 10.1038/nature08227.

**Mandatory counter-example citations** (must accompany any use):
- C. Boettiger & A. Hastings, "Quantifying limits to detection of early
  warning for critical transitions", J. R. Soc. Interface 9(75),
  2527–2539 (2012), DOI 10.1098/rsif.2012.0125.
- P. D. Ditlevsen & S. J. Johnsen, "Tipping points: Early warning and
  wishful thinking", Geophys. Res. Lett. 37(19) (2010), DOI
  10.1029/2010GL044486.

Rising variance/autocorrelation as `λ→0` is **necessary but not
sufficient** evidence of an approaching bifurcation — the Dansgaard-
Oeschger events (Ditlevsen & Johnsen) are noise-induced, not
bifurcation-induced, and Boettiger & Hastings quantify false positive/
negative rates at realistic sample sizes.

## Formulas

Linearization at a stable equilibrium with recovery rate `λ = S_rec`,
plus additive noise: `dX = -λ(X-x*)dt + σdW`. Stationary
Ornstein-Uhlenbeck statistics (exact):

```
Var(X)                = σ² / (2λ)
Corr(X_t, X_{t+Δt})   = exp(-λΔt)
```

Inverse estimator: `λ̂ = -ln(ρ)/Δt`.

## Worked example (from the script run)

Cubic normal form, `b=0, τ=1`, stable branch `x*=√a`, `S_rec=2a`.
`σ²=0.02, Δt=1`:

| `a` | `x*=√a` | `S_rec=2a` | `Var=σ²/(2·S_rec)` | `ρ=e^(-S_rec)` |
|---|---|---|---|---|
| 0.5 | 0.7071 | 1.0 | 0.0100 | 0.367879 |
| 0.05 | 0.2236 | 0.1 | 0.1000 | 0.904837 |

Tenfold decrease in `S_rec` → tenfold increase in variance (ratio
exactly 10.0, checked in the script); autocorrelation rises from 0.368
to 0.905. Inverse estimator confirms `λ̂=0.1` recovers the `a=0.05`
input exactly.

## Out of scope

- Any real-data estimator pipeline (window sizes, trend tests) —
  `identifiability`/`validation` territory, not built here.
- Any identification of `S_rec`/`Var`/autocorrelation with
  `beta_response` (FORMALISM.md §2, "Independence of beta_response"
  rule, unchanged).
- Independent of M14 (contraction), M29 (Landau), M33 (Fenichel/GSPT),
  M34 (Floquet), M35 (Panarchy/cusp) — five separate `dynamics`
  extensions on five different objects, no cross-identification.

## Hand-checkable verification

`verification/verify_early_warning_core.py` covers: the worked-example
table above (with the exact 10x variance ratio), inverse-estimator
self-consistency, presence of both mandatory counter-example citations
in the module docstring and JSON report, a control case (two different
`(a,τ)` pairs engineered to share the same `S_rec` → identical
`Var`/`ρ`), and scope-violation raises (`λ≤0`, `ρ∉(0,1)`, `Δt<0`).
