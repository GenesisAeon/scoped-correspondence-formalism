# OWID/JHU World COVID growth-phase pilot (Milestone 6b)

**Status:** real-data growth-phase pilot (review package) on **verified**
per-row data — see `data/real_data_manifest.json` /
[docs/real_data_provenance.md](real_data_provenance.md). Johann-OK required
before any "core" promotion. Three pilots on the same data: **Pilot A**
(original, full calib window) finds `model_beats_baseline: false` — a
**valid complete** outcome, see "What the numbers say" below. Two
disclosed follow-ups, **Pilot B** (shorter post-trough window) and
**Pilot C** (change-point model), both find `model_beats_baseline: true`
— see "Pilot B and Pilot C" below. None of the three retunes another.

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

## Pilot B and Pilot C (disclosed follow-ups, 2026-09-20)

Johann asked to test both natural fixes suggested by Pilot A's own
diagnosis: a shorter, homogeneous window, and a change-point model. Both
are implemented as **separate, disclosed pilots** in
`validation/covid_pilot.py` — Pilot A's own protocol, code, and reported
result above are untouched.

### Pilot B — shorter window (`run_covid_pilot_short_window`)

Restart calib the day after Pilot A's own diagnosed local trough
(2020-02-25, the minimum of `cases_7day_avg` after the initial peak on
2020-02-14) through the same 2020-03-11 anchor; holdout is **identical**
to Pilot A (2020-03-12 to 2020-03-25), for direct comparison.

| Quantity | Value |
|---|---|
| calib window | 2020-02-26 -- 2020-03-11 (15 days) |
| model_rmse_holdout | 5980.65 |
| baseline_rmse_holdout | 15932.68 |
| model_beats_baseline | **True** |
| fitted r | 0.1210 /day |

Restricting the window to the visibly homogeneous post-trough rise fixes
the problem decisively: RMSE drops by roughly two thirds relative to the
baseline. This confirms the diagnosis in Pilot A — the exponential model
is fine on a genuinely single-phase window; it was the window choice, not
the model family, that failed.

### Pilot C — change-point model (`run_covid_pilot_changepoint`)

Instead of picking a window by eye, fit a two-segment (change-point)
log-linear model on Pilot A's **full, original** calib window
(2020-01-27 to 2020-03-11). The breakpoint is found by an exhaustive grid
search **within calib only** (minimizing the total residual sum of
squares of two independent log-linear fits, requiring at least 5 points
on each side); only the second (most recent) segment's fitted rate is
extrapolated into the same fixed holdout window as Pilot A.

| Quantity | Value |
|---|---|
| detected breakpoint | 2020-02-20 |
| segment 1 | 2020-01-27 -- 2020-02-20 (25 days), r = 0.0746 /day |
| segment 2 | 2020-02-21 -- 2020-03-11 (20 days), r = 0.0810 /day |
| model_rmse_holdout | 12603.00 |
| baseline_rmse_holdout | 15932.68 |
| model_beats_baseline | **True** |

The change-point model also beats the baseline, though less decisively
than Pilot B's hand-restarted window. **A genuinely interesting, honest
finding:** the RSS-minimizing breakpoint (2020-02-20) does **not**
coincide with the visually-obvious trough used in Pilot B (2020-02-25).
Independently re-scanning every valid candidate breakpoint (done in
`verification/verify_covid_pilot.py`) confirms 2020-02-20 truly minimizes
total RSS — it is not a search bug. The data shows why: China's Feb 12-13
case-definition change produced an artificial reporting plateau/spike
(`cases_7day_avg` roughly flat around 4300-4600 from Feb 13-19, then
dropping sharply from Feb 20), and minimizing total residual variance
across both segments finds that reporting-artifact boundary as the
dominant structural break, rather than the later, more epidemiologically
meaningful containment trough on Feb 25. The automated method is
therefore picking up a *measurement* discontinuity, not necessarily the
*epidemiological* one a human would choose — worth knowing before trusting
an automated change-point date as evidence of any real-world event.

### Comparing A, B, C

| Pilot | Calib window | n | model_beats_baseline | model RMSE |
|---|---|---|---|---|
| A (original) | 2020-01-27 -- 2020-03-11 | 45 | False | 17428.70 |
| B (post-trough restart) | 2020-02-26 -- 2020-03-11 | 15 | True | 5980.65 |
| C (change-point, segment 2) | 2020-02-21 -- 2020-03-11 | 20 | True | 12603.00 |

All three use the identical holdout window (2020-03-12 to 2020-03-25),
baseline definition, and metric — only the calib window and the fitted
rate(s) differ. No result here retunes another; each is a separately
protocolled, separately checked computation on the same underlying real,
provenance-verified data.

## Pilot D — country decomposition (NONSTATIONARY_ROADMAP.md package 2, 2026-09-21)

Pilots B and C fix Pilot A's problem by choosing a different **time**
window. Astra's review (section 4) proposed a complementary, orthogonal
diagnosis: does changing **country composition** alone explain part of
the apparent World rate acceleration, even holding each country's own
rate constant? `covid_country_decomposition.py`
(`data/owid_covid_china_world_daily_2020.csv`, real China + World rows
from the same OWID/JHU source, RestOfWorld computed as World minus China)
tests this directly.

**Composition shift, real data:** China's share of world cases_7day_avg
collapses from **98.49% on 2020-01-28 to 0.12% on 2020-03-25** — matching
the well-documented shift of the pandemic's epicenter away from China
through February and March 2020.

**Component rates, fit independently on the same calib window as Pilot A
(here 2020-01-28 -- 2020-03-11, one day later than Pilot A because
China's `weekly_cases` is undefined on 2020-01-27 in this file):**

| Component | Fitted rate r (per day) | Interpretation |
|---|---:|---|
| China | -0.07116 | declining (matches documented containment) |
| RestOfWorld | +0.14590 | doubling every ~4.75 days |
| World (single aggregate fit, same window) | +0.00225 | nearly flat -- an average of a shrinking large component and a fast-growing small one |

**Decomposed model** (extrapolate China's and RestOfWorld's own fitted
rates *separately* into the holdout window, then sum for the World
prediction) vs. the same-window aggregate fit vs. persistence:

| Model | RMSE on 2020-03-12 -- 2020-03-25 |
|---|---:|
| Decomposed (China + RestOfWorld, summed) | **6668.83** |
| Aggregate (single fit, same window) | 17686.65 |
| Persistence | 15932.68 |

The decomposed model beats both alternatives by a wide margin — comparable
to Pilot B's fix, but reached via a completely different, complementary
route (spatial decomposition rather than a shorter time window). This
directly confirms, on real data, Astra's qualitative mixture-identity
argument (section 4): a single blended rate over a period of shifting
country composition systematically misrepresents the dynamics, even
though each component's own within-period rate may be simple and roughly
constant.

**Mixture effective-rate diagnostic:** `mixture_effective_rate_diagnostic()`
computes Astra's identity `r_eff(t) = w_China(t)*r_China + w_RoW(t)*r_RoW`
using the ACTUAL observed daily composition weights and the two fitted
constant rates above, and compares it to the World series' own actual
local growth rate (centered 3-day log-difference) at every date:

| Date | China share | Mixture-implied rate | Actual local rate | Difference |
|---|---:|---:|---:|---:|
| 2020-01-29 | 0.984 | -0.068 | +0.206 | +0.273 |
| 2020-02-19 | 0.981 | -0.067 | -0.325 | -0.258 |
| 2020-02-26 | 0.614 | +0.013 | +0.107 | +0.095 |
| 2020-03-04 | 0.158 | +0.112 | +0.099 | -0.012 |
| 2020-03-18 | 0.001 | +0.146 | +0.162 | +0.017 |

The mixture-implied rate tracks the actual local rate reasonably well
from late February onward (differences shrink to ~0.01-0.02) but is far
off in late January/February (differences of 0.2-0.3, including a sharp
actual-rate swing to -0.325 around 2020-02-19 that the smooth
composition-shift story cannot produce). That large early discrepancy
lines up with China's documented Feb 12-13 case-definition change
(PAHO/WHO, see `SCF_Nichtstationaere_Treiber_und_Kippen.md` reference R1)
-- a reporting artifact localized within China's own series, not a
composition effect and not a genuine within-component rate change. This
partially answers Astra's own open question from Pilot C: composition
shift explains the *later* acceleration well but does **not** explain the
*earlier* artifact-driven swing, which needs its own separate accounting.

**Scope:** two components only (China, RestOfWorld); a complete analysis
would decompose all ~200 countries. No claim that this two-component
split is the unique or best decomposition -- it tests the qualitative
hypothesis using the two largest, best-documented parts of the actual
historical story.

## Verify

```bash
PYTHONPATH=src python verification/verify_covid_pilot.py
PYTHONPATH=src python verification/verify_covid_country_decomposition.py
```

JSON reports: `verification/verify_covid_pilot_results.json` and
`verification/verify_covid_country_decomposition_results.json` — all
numbers from **those** runs.
