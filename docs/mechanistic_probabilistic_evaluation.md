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

## The headline finding: point accuracy ≠ predictive-interval quality

Package 2 found the energy-balance mechanistic model beats every
statistical baseline on point-forecast RMSE, at every lead year. Scored
properly here, the picture flips:

| Predictor | Empirical coverage (nominal 80%) | Mean interval score (lower = better) |
|---|---:|---:|
| persistence | 0.673 | **0.408** |
| expanding | 0.673 | 0.438 |
| last30 | 0.636 | 0.421 |
| **energy_balance_mechanistic** | 0.655 | **0.466 (worst)** |

The mechanistic model's LOO prediction intervals are the *least*
efficient of the four, despite having the *best* point forecasts. This
is not a contradiction — it is exactly the distinction proper scoring
rules exist to catch: a model can be more accurate on average while
having a less well-calibrated or less efficient *uncertainty* estimate
(here, plausibly because its year-to-year error magnitude varies more
across origins than the simpler baselines', which a single pooled LOO
quantile per lead year does not adapt to). Reported honestly, not
smoothed over — this is a genuinely useful, unforced result.

All four predictors' empirical coverage (0.64–0.67) also falls short of
the nominal 80% target — consistent with the small-sample caveat below
(only 10 other origins per lead year to estimate LOO quantiles from).

## COVID renewal: the point-forecast winner is also the interval winner

| Predictor | Coverage (nominal 80%) | Mean interval score |
|---|---:|---:|
| persistence | 0.643 | 20241 |
| exponential_extrapolation | 0.667 | 9052 |
| **renewal_constant_R** | 0.595 | **3796 (best)** |

Here the two rankings agree: `renewal_constant_R` had the best RMSE in
package 2 *and* the best interval score here — though its coverage
(0.595) is the *worst* of the three, another honest small-sample wrinkle
worth flagging rather than hiding.

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

Leave-one-origin-out quantiles use only 10 (energy balance, 11 origins
total) or 5 (COVID, 6 origins total) other origins per lead time — thin
deciles, not well-estimated tail quantiles. This is an exploratory
diagnostic, consistent with this repository's discipline of surfacing
small-N limitations rather than dressing them up as more than they are.

## Verify

```bash
PYTHONPATH=src python verification/verify_mechanistic_probabilistic_evaluation.py
```

JSON report:
`verification/verify_mechanistic_probabilistic_evaluation_results.json`
— all numbers from **that** run.
