# Separating latent renewal dynamics from the reporting/observation process

CAPABILITY_EXPANSION_ROADMAP.md Priority 2, response to Astra's 2026-09-24
capability assessment: "Man kann [dann] unterscheiden, ob ein Modell die
Dynamik verfehlt oder ob der Beobachtungsprozess die Daten verzerrt."
Module: [`validation/covid_latent_renewal_observation.py`](../src/scoped_correspondence/validation/covid_latent_renewal_observation.py).
Verification: [`verify_covid_latent_renewal_observation.py`](../verification/verify_covid_latent_renewal_observation.py)
(4/4 checks).

**Correction (2026-09-24, response to
[SCF_Review_dc5d82a.md](../prompts/Answers/nicht_stationäre_Treiber/SCF_Review_dc5d82a.md),
Astra finding R6):** the original version of this page bundled the weekday
correction and the negative-binomial distribution together and credited
their COMBINED effect to "the observation layer." An independent 2×2
ablation (below) shows this was an over-interpretation: negative-binomial
overdispersion ALONE is the real, strong finding; the weekday correction
on top of it actually *worsens* both log-score and coverage-adjacent
calibration on this exact window. The headline "2.4% → 73.8%" number is
reproducible and correct, but "the weekday correction fixed most of the
gap" was not — corrected below.

## Scope: what the data can and cannot support

Astra's suggestion named three observation-process components: reporting
delay, weekday effects, overdispersion. A genuine reporting-DELAY model
needs a report-date × episode-date matrix (a "reporting triangle"); the
OWID/JHU daily series used throughout this repository is a single
already-finalized count per calendar day, with no such matrix available.
**Reporting delay is therefore not modeled here** — only the two
components the available data can actually support are added:

- a **weekday reporting multiplier** (`fit_weekday_multipliers`): a
  day-of-week factor on the reported count, fit as the median ratio of raw
  count to a non-circular forward-only reference mean, normalized to
  average 1 across the week (so it redistributes counts within a week
  without changing the overall predicted level);
- **negative-binomial overdispersion** (reusing `scoring_rules
  .fit_neg_binom_dispersion`, already used by `covid_observation_model.py`).

Both are fit ONCE, on the days strictly before the first evaluated
forecast origin — entirely out-of-sample with respect to every scored
trial.

## Same dynamics, different observation layer — an isolated comparison

Astra's acceptance criterion: "Alte und neue Varianten auf denselben
festgelegten Prognoseursprüngen vergleichen." The comparison here uses the
IDENTICAL renewal-equation point forecast
(`mechanistic_rolling_origin._covid_renewal_predictor_factory`, unchanged)
at the same origins/horizons as `run_covid_renewal_rolling_origin_backtest`
(`COVID_RENEWAL_ORIGINS_DAY_INDEX` = day 25/30/35/40/45/50, 7-day horizon).
Only the observation layer changes:

- **OLD**: the point forecast (of the smoothed `cases_7day_avg` incidence
  proxy) is used directly as a Poisson mean for the RAW daily count on the
  target calendar date.
- **NEW**: the same point forecast × the fitted weekday multiplier for
  that specific calendar date is used as the mean of a negative-binomial
  distribution (dispersion fit on calib) for the RAW daily count.

Because the dynamics layer is held fixed, any difference in log-score or
coverage is attributable entirely to the observation-layer change.

## Real-data result

18 calib days (before day-index 25), 42 scored trials (6 origins × 7-day
horizon):

| | OLD (Poisson, renewal mean) | NEW (weekday × NB, same renewal mean) |
|---|---:|---:|
| Mean log-score (lower is better) | 1387.5 | **11.8** |
| Empirical coverage (nominal 80%) | 2.4% | **73.8%** |

A large, unambiguous win for the NEW variant over the OLD one. But which of
its two changes actually earns that win?

## The 2×2 ablation: it's the overdispersion, not the weekday correction

`run_covid_ablation_comparison` runs all four combinations (weekday: on/off
× distribution: Poisson/negative-binomial) on the SAME 42 trials, fitting a
SEPARATE dispersion for each mean variant (both still strictly pre-origin):

| Weekday correction | Distribution | Coverage (nominal 80%) | Mean log-score ↓ |
|---|---|---:|---:|
| No | Poisson | 2.38% | 1387.5 |
| Yes | Poisson | 0.00% | 2490.0 |
| **No** | **Negative-binomial** | **73.81%** | **10.2** |
| Yes | Negative-binomial | 73.81% | 11.8 |

**Negative-binomial overdispersion alone is the strong, robust finding.**
Adding the weekday correction on top *worsens* both the log-score
(10.2 → 11.8) and, on Poisson, actively destroys coverage (2.4% → 0.0%) —
the opposite of "fixes most of the gap." The coverage number happens to be
identical with or without the weekday term under NB here (73.81% both
ways), so the weekday correction is neutral-to-harmful on this window, not
helpful.

**Two further limits, stated explicitly:**

1. This does **not** retroactively explain the *earlier* 26.3%
   pooled-coverage finding from Priority 0/1
   (`leave_one_origin_out_intervals`, Milestone 50). That used a different,
   signed lo/hi-quantile construction on the *smoothed* incidence with 19
   evaluated cases — a different method and a different sample from this
   42-trial *raw*-count comparison. Holding the renewal dynamics fixed
   isolates what THIS specific observation-layer change buys on THIS
   specific comparison; it is not a mechanistic explanation of the earlier,
   differently-constructed result.
2. Holding the dynamics fixed isolates the effect of changing the
   *prediction distribution*, but a broad negative-binomial distribution
   can also partially absorb OTHER model misspecification. Improved
   calibration here is evidence the distribution fits better — it is not,
   by itself, proof that the underlying renewal dynamics are correct.

**Caveat on the recovered weekday pattern itself:** the fitted multipliers
(`{0: 1.05, 1: 0.84, 2: 0.19, 3: 1.39, 4: 1.79, 5: 0.84, 6: 0.89}`, Monday=0)
come from only 18 days (≈2.5 weeks) of early-2020 "World"-aggregated data —
a small window mixing many countries' independent reporting schedules. Given
the ablation above shows this correction does not help predictively on this
window, the specific pattern should be read as descriptive of this short,
aggregated calibration window, not as a validated global weekday effect.

## What this does not yet do

`persistence`'s 0% coverage under every calibration method in Priority 1
(`docs/adaptive_interval_calibration.md`) remains unaddressed here — that
predictor's underlying point forecast (last-known value) is, by
construction, a poor mean during exponential growth regardless of the
observation layer wrapped around it. Priority 2's fix targets the
observation process around an already-reasonable dynamics model
(`renewal_constant_R`); it cannot repair a dynamics model that is itself
the wrong shape for the regime.
