# State estimation on parallel linear reservoirs: does correcting the storage estimate with the actual daily discharge help?

INTEGRATED_EXTENSION_ROADMAP.md Paket C1 — response to
`prompts/Answers/nicht_stationäre_Treiber/SCF_INTEGRATED_EXTENSION_IMPLEMENTATION_PLAN.md`,
section 5. Modules:
[`observation/linear_state_estimation.py`](../src/scoped_correspondence/observation/linear_state_estimation.py)
(generic linear-Gaussian Kalman core: predict/update, Joseph-form covariance,
observability), [`validation/hydrology_state_estimation.py`](../src/scoped_correspondence/validation/hydrology_state_estimation.py)
(daily-mean measurement operator connecting the filter to
`dynamics/linear_reservoirs.py`, noise calibration, the 2×2 real-data panel).
Verification (synthetic-only, no network access needed):
[`verify_linear_state_estimation.py`](../verification/verify_linear_state_estimation.py) (6/6),
[`verify_hydrology_state_estimation.py`](../verification/verify_hydrology_state_estimation.py) (7/7).

## Why this needed a purpose-built measurement operator

CAMELS-DE discharge (used throughout [`docs/hydrology_pilot.md`](hydrology_pilot.md))
is a **daily mean**, not an instantaneous sample. Reusing the instantaneous
operator `q(t) = sum_i k_i*S_i(t)` as the Kalman measurement model would
silently claim we observe something the data doesn't provide. Instead, for a
constant inflow `u` over `[t, t+Δ)` the SAME already-verified closed forms
from `dynamics/linear_reservoirs.py` (findings R3/R3b) give the exact
daily-mean state-space model

```
S(t+Δ) = F·S(t) + G·u(t) + w(t)         F_ii = e^{-k_iΔ}, G_i = alpha_i·Δ·E(k_iΔ)
qbar(t) = H·S(t) + D·u(t) + v(t)        H_i = k_i·E(k_iΔ), D = sum_i alpha_i·(1-E(k_iΔ))
E(z) = (1-e^{-z})/z, E(0)=1
```

cross-checked directly against `parallel_reservoir_step`/
`parallel_reservoir_interval_discharge` (two independent code paths, same
numbers to `<1e-10`) rather than only re-derived algebraically.

## Hand-verified control case (before any code was written)

`F=diag(1/2,1/4)`, `H=(1,1)`, prior `m⁻=(0,0)`, `P⁻=I`, `R=1`, `y=3`, `W=0`.
Independently re-derived by hand (and cross-checked a second, independent way
in `verify_linear_state_estimation.py` by conditioning the analytically
constructed JOINT Gaussian distribution of `(x_1,y_1)` directly, never by
calling the filter against itself):

`K=(1/3,1/3)ᵀ`, `m⁺=(1,1)ᵀ`, `P⁺=[[2/3,-1/3],[-1/3,2/3]]`; propagating once
more (no further observation) gives predicted next-observation mean `0.75`
and variance `1.125`. Observability: `det([H;HF])=-0.25` (rank 2, observable);
at `F=0.5·I` the observability matrix drops to rank 1 — the state
DIFFERENCE `x_1-x_2` is invisible to `H=(1,1)` and, under equal decay, stays
invisible for all time.

## Protocol (plan section 5.4/9.5)

Same 6 catchments and 1991–2005/2011–2020 train/test split as
`hydrology_pilot.py`, over the FULL contiguous calendar span (C0's fix — the
2006–2010 gap is genuinely simulated, never skipped). For each catchment and
each reservoir count (1 or 2, using the SAME already-fitted `(c, alphas,
rates)` from `hydrology_pilot._fit_1res`/`_fit_2res` for both variants below):

- **Process noise `W = w_scale·I`** chosen by an INNER time-ordered
  validation split strictly within the training period (first 80% fits, last
  20% validates a 1-day-ahead corrected forecast) — never touching the gap
  years or the test period.
- **Measurement noise `R`** fixed as the variance of the already-fitted
  model's own OPEN-LOOP training residuals — a declared, directly observable
  error model, not a claim of a physically derived noise process.
- **Corrected variant**: predict/update recursion across the whole span,
  correcting with that day's own actual discharge each day.
- **Open-loop variant**: the SAME recursion with `update()` never called —
  reduces exactly to `hydrology_pilot.py`'s existing deterministic simulation
  (checked bit-for-bit in `verify_hydrology_state_estimation.py`).
- **Lead-time forecasts** (1/3/7 days) use ONLY the posterior recorded at
  day `t-lead`, propagated forward via pure `predict()` with no further
  correction — no future target measurement ever enters a single forecast
  (checked explicitly: changing observations after day `t` cannot change the
  forecast for day `t`).
- **Common-cases scoring**: a test day is scored only if every lead time and
  every variant has a valid forecast there (plan: "Primary MAE/RMSE on
  common cases"). Low-flow threshold (`q10`) taken from training only.

**A real, reported finding, not a hidden grid boundary:** the inner-validation
search always selects the LARGEST tested process-noise scale
(`w_scale=1e6`) for every catchment and every reservoir count. Checked before
fixing the grid's range that this is a genuine plateau, not an artifact of a
grid that was too narrow: for DEA11490's one-reservoir model, inner-validation
MAE is `0.1338` at `w_scale=1`, `0.0978` at `w_scale=1e5`, and `0.09776` at
`w_scale=1e8` — i.e. the filter's inner-validation optimum keeps pushing
toward trusting the LATEST measurement far more than the fitted deterministic
reservoir dynamics, but the improvement itself saturates. Practically this
means the corrected filter's behavior is closer to "the storage value that
exactly reproduces yesterday's observed discharge, decayed forward one day"
than to "the deterministic reservoir trajectory" — exploiting the same strong
day-to-day discharge autocorrelation that made persistence win in
`hydrology_pilot.py`, but routed through the fitted reservoir's own decay
dynamics for multi-day extrapolation.

## Real results (test period 2011–2020, MAE in mm/day, common-cases scoring)

### One reservoir

| Gauge | Corrected, lead 1 | Corrected, lead 3 | Corrected, lead 7 | Open-loop (any lead) | Persistence (from hydrology_pilot.md) |
|---|---:|---:|---:|---:|---:|
| DEA11490 | **0.061** | 0.099 | 0.111 | 0.123 | 0.064 |
| DE211310 | 0.103 | 0.201 | 0.288 | 0.424 | **0.095** |
| DEE10610 | 0.699 | 1.126 | 1.319 | 1.356 | **0.561** |
| DEA11180 | 0.082 | 0.165 | 0.249 | 0.357 | **0.078** |
| DE110500 | 0.408 | 0.688 | 0.839 | 0.876 | **0.384** |
| DEG10330 | 0.273 | 0.595 | 0.878 | 1.098 | **0.233** |

### Two reservoirs

| Gauge | Corrected, lead 1 | Corrected, lead 3 | Corrected, lead 7 | Open-loop (any lead) | Persistence |
|---|---:|---:|---:|---:|---:|
| DEA11490 | **0.056** | 0.081 | 0.091 | 0.100 | 0.064 |
| DE211310 | 0.103 | 0.199 | 0.278 | 0.413 | **0.095** |
| DEE10610 | 0.750 | 1.033 | 1.117 | 1.237 | **0.561** |
| DEA11180 | 0.083 | 0.162 | 0.239 | 0.352 | **0.078** |
| DE110500 | 0.407 | 0.661 | 0.789 | 0.873 | **0.384** |
| DEG10330 | 0.293 | 0.621 | 0.891 | 1.096 | **0.233** |

**Bolded = best of {corrected-lead-1, persistence} per row.**

**State correction dramatically improves the mechanistic models at every
catchment and every lead time** — 1-day-ahead MAE drops by 30–75% relative
to the same catchment's own open-loop MAE (e.g. DEG10330 one-reservoir:
1.098→0.273, a 75% reduction). This is a genuinely positive result for the
mechanistic model, in contrast to `hydrology_pilot.py`'s open-loop finding
that persistence always won.

**But it still does not overturn `hydrology_pilot.py`'s persistence
comparison at 5 of the 6 catchments.** Only at **DEA11490** does the
corrected filter (both reservoir counts) beat persistence outright at
lead 1 (0.056–0.061 vs. 0.064) — DEA11490 is the smallest, fastest-responding
catchment in the panel. At the other 5, corrected lead-1 MAE remains above
persistence, though at DE211310 and DEA11180 the gap is now small (0.103 vs.
0.095; 0.082 vs. 0.078). As expected, MAE grows monotonically with lead time
at every catchment (forecast uncertainty compounds), and by lead 7 the
corrected model is generally closer to (sometimes above) the open-loop MAE.

### Low-flow window (test-period days below the training 10th percentile), lead 1 only

| Gauge | Corrected, 1-res | Corrected, 2-res | Open-loop, 1-res | Open-loop, 2-res | Persistence |
|---|---:|---:|---:|---:|---:|
| DEA11490 | **0.0115** | 0.0428 | 0.095 | 0.082 | 0.012 |
| DE211310 | 0.0456 | 0.0492 | 0.291 | 0.325 | **0.016** |
| DEE10610 | 0.315 | 0.404 | 0.733 | 0.825 | **0.036** |
| DEA11180 | 0.0377 | 0.0387 | 0.200 | 0.199 | **0.013** |
| DE110500 | 0.147 | 0.153 | 0.465 | 0.496 | **0.014** |
| DEG10330 | 0.121 | 0.133 | 0.680 | 0.701 | **0.013** |

Same pattern, sharpened: correction is a large improvement over open-loop at
low flow everywhere, and at DEA11490's one-reservoir variant it narrowly beats
persistence too (0.0115 vs. 0.012) — the only such case in the whole panel.
Everywhere else persistence still wins low-flow decisively, consistent with
`hydrology_pilot.py`'s finding that discharge changes very slowly day-to-day
at low flow.

## Gaussian filters can produce negative storage — reported, not hidden

The measurement-corrected filter produced a **negative posterior mean
storage on a non-trivial fraction of days at every single catchment**
(module docstring caveat, plan section 5.4) — from 67 days (DEA11180,
1-reservoir, out of ~5479 full-span days) to 3436 days (DEE10610,
2-reservoir). This is an expected consequence of an UNCONSTRAINED
linear-Gaussian filter with `w_scale` pushed this high (see above): when a
day's actual discharge is lower than what the fitted dynamics alone would
predict, the correction can pull the estimated storage below zero rather
than being clipped at a physical floor. **This is reported explicitly and
was never clipped to zero while still reporting these as exact Kalman
posteriors** — a physically constrained (non-negative) filter is a separate,
harder problem not attempted here.

## Scope

Six catchments, one country, one climate regime — same panel and same
caveat as `hydrology_pilot.py`, not claimed representative. Noise
calibration uses a single global `w_scale`/`R` per catchment/reservoir-count
combination, not a time-varying or state-dependent noise model. The
observability analysis (`observability_matrix`/`observability_report` in
`linear_state_estimation.py`) is implemented and control-case verified but
not separately run on the fitted per-catchment `(F, H)` pairs here — a
2-reservoir catchment's own `F`/`H` observability could be checked as a
direct follow-up. **C1c** (a NEW, metadata-pre-selected confirmation panel
of 6 different CAMELS-DE catchments, selection rule fixed before seeing any
result) is explicitly deferred, not attempted in this package — the existing
6 catchments are already an "exploration panel," not independent
confirmation, per the plan's own requirement.
