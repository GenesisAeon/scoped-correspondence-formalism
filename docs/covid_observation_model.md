# COVID count observation model: testing overdispersion, not assuming it (Milestone 52)

**Status:** review package (real per-row data) — see
`MECHANISTIC_VALIDATION_ROADMAP.md` package 5. Johann-OK required before
any "core" promotion.

## Why this exists

`prompts/Answers/nicht_stationäre_Treiber/SCF_Review_f8e249f.md` (Astra,
2026-09-21): "latente Dynamik [...] Messprozess [...] explizit trennen
[...] Negativ-Binomial-Beobachtungsmodell für Überdispersion (Notwendigkeit
über Residuen/Prognosescores prüfen, nicht a priori annehmen)" and "Echte
tägliche Rohzahlen statt überlappender Siebentagesmittel als
Zählmodell-Eingabe."

Every prior COVID module in this repository (`covid_pilot.py`,
`covid_renewal.py`, `covid_country_decomposition.py`) uses
`cases_7day_avg` — a smoothed proxy — as both the fitted quantity and the
evaluated quantity. This module is the first to use the **raw daily
`new_cases`** column as the observed count, and to ask a genuinely
different question: given an already-smoothed reference mean, how much
does the real day-to-day count vary around it — and is a Poisson model
(variance = mean) enough, or is the data overdispersed (variance > mean)?

**Deliberately simple, explicitly scoped design:** `cases_7day_avg` is
taken as a GIVEN reference mean `μ_t` (not independently modeled here — a
full latent-state/observation-process separation, e.g. a state-space
model estimating the true latent incidence, is a larger undertaking left
for future work). The question asked is narrower but still real: does
allowing overdispersion around this already-smoothed mean improve the
predictive score for the raw count?

## Method

Dispersion (NB2 parametrization: mean `μ`, variance `μ + α·μ²`) is fit by
maximum likelihood on a CALIB half of the analysis window and evaluated
(Poisson vs. negative-binomial log-score) on a disjoint HOLDOUT half —
the same window split in half by day count as `covid_renewal.py`'s own
window (2020-01-28 to 2020-03-25), calib ending 2020-02-25. This
anti-leak split means the comparison is not circular: the dispersion
parameter is never fit on the same days it is scored against.

## Result: decisive, not marginal, overdispersion

| Quantity | Value |
|---|---:|
| n_calib / n_holdout | 29 / 29 |
| Fitted dispersion α | 0.539 |
| Mean Poisson log-score (holdout) | 944.5 |
| Mean negative-binomial log-score (holdout) | 9.71 |

The negative-binomial model wins by roughly two orders of magnitude. This
is not a marginal statistical refinement — a naive Poisson-around-the-
smoothed-mean model is a catastrophically bad description of real raw
daily counts. This makes physical sense: raw daily case counts carry
strong day-of-week reporting artifacts (weekend reporting lags, batch
corrections) that `cases_7day_avg` smooths away by construction — so of
course the *smoothed* mean, treated as if it were a Poisson mean for the
*raw* count, looks wildly overdispersed. Astra's suspicion is confirmed
resoundingly, and the dispersion was genuinely TESTED (via a disjoint
calib/holdout split), not assumed.

**What this does NOT establish:** this result does not by itself
disentangle true epidemiological overdispersion (e.g. superspreading
events) from pure reporting/measurement artifacts (weekday effects,
backfill) — both would produce the same signature here. Separating them
would need the fuller latent-state/observation-process model noted above
as future work.

## Verify

```bash
PYTHONPATH=src python verification/verify_covid_observation_model.py
```

JSON report: `verification/verify_covid_observation_model_results.json`
— all numbers from **that** run.
