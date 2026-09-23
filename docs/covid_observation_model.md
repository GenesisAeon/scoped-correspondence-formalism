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
window (2020-01-28 to 2020-03-25), calib ending 2020-02-25.

**Correction (2026-09-23, response to
[`SCF_Review_3e8dce3.md`](../prompts/Answers/nicht_stationäre_Treiber/SCF_Review_3e8dce3.md),
Astra, finding 2):** the sentence that used to stand here — "this
anti-leak split means the comparison is not circular" — was wrong. The
calib/holdout split protects the *dispersion* parameter from circularity,
but the reference mean `μ_t` originally used (`cases_7day_avg`) is OWID's
OWN trailing 7-day average, which **includes the day being scored** on
both calib and holdout days regardless of the split. Astra's concrete
counterexample: on 2020-03-12 (observation 6,756, reference mean
5,033.29), increasing only that day's count by 700 (with weekly
aggregates updated consistently) raises its own "predicted mean" by
exactly 100 — a day cannot un-circularly predict itself. **Fixed** by
introducing a genuinely forward-only reference mean: the average of
`new_cases` over the 7 calendar days *strictly before* the scored day
(`_lagged_means`, `LAGGED_MEAN_WINDOW_DAYS`), which never uses the
scored day's own count. Six early-window calib days (2020-01-28 through
2020-02-02) cannot get a full 7-day lookback from the loaded raw series
and are honestly excluded rather than padded (see
`n_calib_dropped_insufficient_lookback`).

## Result: decisive, not marginal, overdispersion — survives the fix

| Quantity | Forward-only lagged mean (PRIMARY, non-circular) | Retrospective `cases_7day_avg` (kept for comparison only) |
|---|---:|---:|
| n_calib / n_holdout | 23 / 29 | 23 / 29 |
| Fitted dispersion α | 0.750 | 0.503 |
| Mean Poisson log-score (holdout) | 1692.76 | 944.52 |
| Mean negative-binomial log-score (holdout) | 9.95 | 9.68 |

Fixing the circularity does not weaken the finding — it strengthens it.
With a genuine forward-only mean, the raw Poisson misfit is actually
**worse** than the original (circular) numbers suggested (1692.76 vs.
944.52): the retrospective mean partially "cheats" by already knowing
part of the answer, which flatters Poisson's apparent fit. The
negative-binomial model still wins decisively either way (α fitted
positive — 0.750 in the primary, forward-only column — with a
log-score improvement of two orders of magnitude in both columns) — this
is not a marginal statistical refinement. **Correction (2026-09-23,
Astra, `SCF_Followup_1231f64.md`):** the fitted dispersion being positive
is not itself a significance test, and this comparison is made **at a
given, externally supplied mean** (the lagged or retrospective reference
mean) — it does not by itself rule out that part of the negative-binomial
advantage reflects a misspecified mean curve or reporting-delay/trend-lag
effects rather than epidemiological overdispersion alone. The wording
here previously said "positive and significant," which claimed a formal
inference test that was never run; corrected. What makes physical sense
and remains well supported: raw daily case counts carry strong
day-of-week reporting artifacts (weekend reporting lags, batch
corrections) that any 7-day averaging smooths away by construction — so
a Poisson model built around either kind of smoothed mean looks wildly
overdispersed for the *raw* count. Astra's original overdispersion
suspicion is confirmed resoundingly at this given mean, and now on a
genuinely circularity-free forecast-quality basis, not merely a
descriptive one — separating that overdispersion cleanly from a possible
mean-specification error remains a documented open question (see the
"What this does NOT establish" scope note above).

**Retained for transparency, explicitly relabeled:** the
`cases_7day_avg`-based comparison (right column) is kept as a
**descriptive** view of dispersion around a retrospective smoothing
value — informative about the raw/smoothed variance relationship, but
NOT a circularity-free forecast-quality result, and not the number this
module leads with going forward.

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
