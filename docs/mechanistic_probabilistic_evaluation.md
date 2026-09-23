# Prediction intervals + proper scoring rules for the 3 mechanistic models (Milestone 49/50)

**Status:** review package (real per-row data throughout) — see
`MECHANISTIC_VALIDATION_ROADMAP.md` package 3. Johann-OK required before
any "core" promotion.

## Why this exists

`prompts/Answers/nicht_stationäre_Treiber/SCF_Review_f8e249f.md` (Astra,
2026-09-21): "Bisher liefern alle Module Punktschätzungen (RMSE, AIC).
[...] Vorhersageintervalle [...] Log-Score für Zähl-/Ereignismodelle,
CRPS oder Intervall-Score für kontinuierliche Ziele" (Gneiting & Raftery
2007). This builds directly on `docs/mechanistic_rolling_origin.md`
(package 2): same origins, same predictors, now scored with genuine
predictive uncertainty instead of point-forecast RMSE alone.

**Why not `validation.conformal`?** That module already documents its own
coverage as "marginal under exchangeability." Rolling-origin residuals
here come from *overlapping, serially-correlated calibration windows* on
explicitly non-stationary series — exactly the setting where
exchangeability is not a safe default. Rather than dress up an
inapplicable guarantee, this package uses leave-one-origin-out (LOO)
empirical residual quantiles (continuous targets) or a Poisson parametric
interval (ETAS counts), with coverage reported *empirically*, not claimed
from a theorem that doesn't apply here.

## Update (2026-09-23): corrected for the interval-leakage fix — a more decisive undercoverage finding

**Correction (Astra, `SCF_Review_3e8dce3.md` finding 1 /
`SCF_Followup_1231f64.md`):** `leave_one_origin_out_intervals` originally
pooled calibration residuals from ALL other origins, including LATER
ones — a genuine look-ahead-bias bug (see
[docs/rate_dependent_tipping.md](rate_dependent_tipping.md) and
`MECHANISTIC_VALIDATION_ROADMAP.md` package 7 for the fix itself). Fixed:
calibration now uses only origins whose own target observation was
already available at the trial's origin (`origin' + step*step_size <=
origin`). Trials without enough such origins are honestly SKIPPED
(reported as `n_skipped_insufficient_lookback`), not silently included
or forced. The numbers below are the corrected, re-run results — the
tables previously here are superseded, not merely updated cosmetically.

## The headline finding, corrected: intervals are decisively UNDER-covered, not just imperfect

| Predictor | Nominal coverage | Observed coverage | Evaluated / skipped trials | Mean interval score (lower = better) |
|---|---:|---:|---:|---:|
| persistence | 80% | 67.5% | 40 / 15 | **0.4167 (best)** |
| last30 | 80% | 57.5% | 40 / 15 | 0.4624 |
| expanding | 80% | 65.0% | 40 / 15 | 0.4830 |
| **energy_balance_mechanistic** | 80% | **52.5% (worst)** | 40 / 15 | 0.5191 (worst) |

The mechanistic model is now worst on **both** interval score AND
coverage, not merely the least-efficient of four roughly-calibrated
models as the pre-fix numbers suggested — the corrected, leak-free
intervals are decisively too narrow for the model with the best point
forecasts. Point accuracy and predictive-interval quality remain
different questions; the corrected picture argues that distinction more
sharply, not more softly.

## COVID renewal: the point-forecast winner is not the interval winner — and none of the three are close to calibrated

| Predictor | Nominal coverage | Observed coverage | Evaluated / skipped trials | Mean interval score |
|---|---:|---:|---:|---:|
| persistence | 80% | **5.3% (worst)** | 19 / 23 | 46004.70 (worst) |
| exponential_extrapolation | 80% | 57.9% | 19 / 23 | 7246.40 |
| **renewal_constant_R** | 80% | 26.3% | 19 / 23 | **6048.43 (best)** |

`renewal_constant_R` still has the best interval score, consistent with
its package-2 RMSE win, but its observed coverage (26.3%) is barely a
third of the nominal 80% — decisively uncalibrated, not merely a
small-sample wrinkle. Persistence's coverage (5.3%, essentially always
missing) makes explicit how poorly a naive baseline's residual spread
represents genuine forecast uncertainty on this series.

**Reading:** with the leak fixed, more than half of all raw (origin,
step) trials for COVID (23 of 42) and over a quarter for the energy
balance (15 of 55) lack enough forward-only history to be scored at all
— the remaining, honestly-evaluated samples are SMALL (19–40 trials) and
plainly show underdispersed LOO intervals across every predictor tested.
This is now the primary, decisive result of this package, not a caveat
appended to an otherwise-clean calibration story.

## ETAS: Poisson log-score agrees with the point-forecast ranking

Each model's point forecast is treated as a Poisson mean — an explicit
simplification (real ETAS counts are overdispersed relative to Poisson),
used only as a common reference distribution so scores are comparable.

| Predictor | Mean Poisson log-score (lower = better) | Coverage (nominal 90%) |
|---|---:|---:|
| **persistence** | **5.356 (best)** | 0.667 |
| etas_first_order | 6.131 | 0.500 |
| constant_rate | 6.360 | 0.500 |

Consistent with package 2's RMSE finding: persistence wins here too. No
retuning, reported as-is.

## Honest small-sample caveat

Leave-one-origin-out quantiles use AT MOST 10 (energy balance, 11 origins
total) or 5 (COVID, 6 origins total) other origins per lead time — thin
deciles even before the leak fix. **Since the fix, the usable count is
smaller still and varies by step:** only strictly earlier origins (per
the corrected temporal-eligibility rule above) count, so later-horizon
steps for early origins are skipped entirely rather than calibrated from
too little history (`n_skipped_insufficient_lookback` in each report).
This is an exploratory diagnostic, consistent with this repository's
discipline of surfacing small-N limitations rather than dressing them up
as more than they are — and per the corrected coverage table above, the
diagnostic itself now shows the intervals to be decisively
under-calibrated, not merely thin.

## Verify

```bash
PYTHONPATH=src python verification/verify_mechanistic_probabilistic_evaluation.py
```

JSON report:
`verification/verify_mechanistic_probabilistic_evaluation_results.json`
— all numbers from **that** run.
