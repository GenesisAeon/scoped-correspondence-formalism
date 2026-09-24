# Battery capacity: mean trend vs. observation noise, kept separate

DOMAIN_EXPANSION_ROADMAP.md Paket B5a — response to
`prompts/Answers/nicht_stationäre_Treiber/SCF_DOMAIN_EXPANSION_IMPLEMENTATION_PLAN.md`,
section 11.2. Module:
[`dynamics/capacity_degradation.py`](../src/scoped_correspondence/dynamics/capacity_degradation.py).
Verification:
[`verify_capacity_degradation.py`](../verification/verify_capacity_degradation.py)
(7/7 checks).

## Why not fit irreversible/reversible/noise separately?

From a single capacity series, irreversible aging, reversible
(protocol-dependent) effects, and measurement error are generally **not
separately identifiable** (plan section 11.2). This module deliberately
restricts itself to **phenomenological mean models** — `persistence`
(last observed value), `linear` (`C0-a·n`), `power` (`C0-a·n^p`) — plus an
explicit **2×2 observation ablation** (independent vs. AR(1)-correlated
residuals), which separates the benefit of a *better mean trend* from the
benefit of a *better observation model*, without claiming to have
identified the underlying physical mechanism.

## Exact recovery and the `p=1` special case

Noiseless synthetic linear (`C0=2, a=0.01`) and power-law (`C0=2, a=0.005,
p=1.5`) curves are recovered exactly by fitting the matching model family.
Fitting the **power** model to exactly **linear** data reproduces the
linear trend with essentially zero residual — the power law nests the
linear model at `p=1`, confirmed structurally (not merely asserted).

`a≥0` (capacity cannot improve on average) is enforced as a **bound in the
least-squares fit itself** (`scipy.optimize.lsq_linear`/`curve_fit` with
`a≥0` bounds), not clipped after the fact.

## Observation ablation: no pre-programmed gain

On a `n=500`-point series (large enough that OLS sampling noise in the
AR(1) coefficient estimate cannot itself cause a false result):

- **Independent residuals:** estimated AR(1) coefficient `|φ|<0.15` —
  no spurious correlation manufactured by the ablation block itself.
- **Genuinely correlated residuals** (`φ_true=0.8`): recovered to
  `|φ̂-φ_true|<0.1`.

## Two EOL notions, never conflated

`first_mean_eol_crossing` gives the **fitted mean curve's own** crossing
of a capacity threshold — a property of the model, not an event. A
simulated *observed* path's first crossing (via
`predict_capacity_distribution`, which propagates AR(1) residuals
correctly when active) is a separate, generally different number — the
module never reports one under the other's name.

## Model-domain violations, exposed not hidden

`mean_capacity` returns the raw model value, including negative
extrapolations far outside the training range — a negative "capacity" is
reported as exactly that (a model-domain violation the caller must
handle), never silently clipped to look physically plausible. Raw observed
capacity increases (a real bump, e.g. from a calendar rest) are preserved
untouched in `CapacityTrendFit.train_capacity` — no monotonizing
preprocessing that would hide exactly the observation question this module
exists to examine (plan section 11.2, "Nicht erzwingen").

## Scope

Phenomenological capacity trend and independent/AR(1) observation models
only — no electrochemical mechanism, no censoring/survival analysis yet
(deferred per plan section 11.3), and no claim that these three synthetic
model families exhaust real battery aging behavior. The real NASA PCoE
data pilot (Paket B5b) is a separate, not-yet-completed package.
