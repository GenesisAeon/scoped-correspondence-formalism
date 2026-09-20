# OWID/JHU World COVID growth-phase pilot (Milestone 6b)

**Status:** real-data growth-phase pilot (review package) on **verified**
per-row data — see `data/real_data_manifest.json` /
[docs/real_data_provenance.md](real_data_provenance.md). Johann-OK required
before any "core" promotion. A `model_beats_baseline: false` result is a
**valid complete** outcome, and IS the result of this run — see "What the
numbers say" below.

## Mapping to ROADMAP.md §3

1. States, boundaries, inputs, timescales, observations — here: World
   aggregate `cases_7day_avg` (cases/day, trailing 7-day mean of
   `weekly_cases/7` to reduce weekday reporting noise), 2020-01-27 through
   2020-03-25.
2. Transformation / time map — exponential growth
   `cases(t) = cases0 * exp(r*(t - t_ref))`, `t` in days since `t_ref`
   (first calib date).
3. Domain of expected relation + error measure — calib-only fit; holdout
   RMSE.
4. Comparison models + separate prediction data — **persistence baseline**
   (last calib `cases_7day_avg` held constant) vs exponential growth; fixed
   calendar split locked **before** fit.
5. Uncertainty / counterfindings allowed — including "no gain beyond
   baseline", which is exactly what happened here.

This pilot is **one domain, one macro, one fixed window**. No cross-wave,
cross-country, or cross-domain universality claim.

## Data file

`data/owid_covid_world_daily_2020_2023.csv` — see
`data/real_data_manifest.json` entry `owid_covid_world_daily_2020_2023` for
exact source URL, retrieval timestamp, sha256, and license. **Attribution
required** (CC BY 4.0): "Data: Our World in Data / Johns Hopkins University
CSSE COVID-19 Data Repository."

Unlike the Cygnus pilot (`docs/cygnus_pilot.md`), this per-row data is
independently confirmed real (OWID's compact JHU-sourced series, filtered
to `location == "World"`, no values altered) — the honest negative result
below is a finding about the model, not a data-authenticity concern.

## Protocol (immutable)

| Item | Value |
|---|---|
| Macro | `cases_7day_avg = weekly_cases / 7` |
| Calib window | 2020-01-27 -- 2020-03-11 (45 days) |
| Holdout window | 2020-03-12 -- 2020-03-25 (14 days) |
| Split anchor | `calib_end` = WHO declared COVID-19 a pandemic on 2020-03-11 (an externally documented milestone, not fit-derived); holdout = the fixed next 14 days |
| Baseline | persistence = last calib `cases_7day_avg` |
| Metric | RMSE on 14 holdout days |
| Free params | `(r, ln_cases0)` via OLS on `ln(cases_7day_avg)`, calib only |

## What the numbers say

From `verification/verify_covid_pilot_results.json` on the build machine:

| Quantity | Value |
|---|---|
| model_rmse_holdout | 17428.70 |
| baseline_rmse_holdout | 15932.68 |
| model_beats_baseline | **False** |
| fitted r | 0.007436 /day |
| fitted cases0 | 1739.9 |
| baseline (last calib cases_7day_avg) | 4459.6 |

**Why the model loses:** the calib window (2020-01-27 to 2020-03-11) is
not a single monotonic growth phase. Log(`cases_7day_avg`) rises from
5.83 (Jan 27) to a local peak of 8.40 (mid-Feb, the initial China/Hubei
outbreak), falls back to 6.71 by Feb 26 (China's outbreak was contained;
a well-documented case-definition change also affected reporting around
that time), then rises again through March 11 as global spread began
(Italy, Iran, South Korea and others). A single log-linear fit across
this whole window is pulled toward a weak net rate (`r=0.0074/day`,
implausibly slow for an unmitigated outbreak) by averaging across a
genuine regime change. The holdout window (2020-03-12 to 2020-03-25) then
shows the real, much faster global acceleration
(`cases_7day_avg` rises from 5033 to 37021, a factor of 7.4 over 13 days,
i.e. roughly doubling every ~4.5 days) that the diluted fit badly underestimates — so the flat persistence
baseline, despite being a naive constant, tracks the holdout's early
values more closely on RMSE than the model's near-flat, too-low
prediction curve does.

This is reported as-is, per protocol — **no retuning of the window after
seeing this result.** It is a genuine illustration of why a single
global growth-rate estimate across a regime change is unreliable, on real
verified data, which is a more useful and honest outcome than a
cherry-picked window that happens to "win."

## Verify

```bash
PYTHONPATH=src python verification/verify_covid_pilot.py
```

JSON report: `verification/verify_covid_pilot_results.json` — all numbers
from **that** run.
