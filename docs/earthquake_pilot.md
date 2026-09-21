# USGS M>=6.0 earthquake annual-count pilot (Milestone 6d)

**Status:** real-data constant-rate pilot (review package) on **verified**
per-row data — see `data/real_data_manifest.json` /
[docs/real_data_provenance.md](real_data_provenance.md). Johann-OK required
before any "core" promotion. A `model_beats_baseline: false` result is a
**valid complete** outcome, and IS the result of this run.

## Mapping to ROADMAP.md §3

1. States, boundaries, inputs, timescales, observations — worldwide annual
   count of earthquakes with magnitude >= 6.0, 2000-2025 (2026 excluded,
   partial year).
2. Transformation / time map — constant-rate (homogeneous Poisson)
   prediction: `predicted_count(year) = mean annual count over calib`.
3. Domain of expected relation + error measure — calib-only fit; holdout
   RMSE.
4. Comparison models + separate prediction data — **persistence baseline**
   (last calib year's count held constant) vs. constant-rate model; fixed
   calendar split (2000-2019 calib, 2020-2025 holdout) locked **before**
   fit.
5. Uncertainty / counterfindings allowed — including "no gain beyond
   baseline", which is what happened here.

This pilot is **one domain, one macro, one fixed window**. No claim about
`percolation/core.py`'s branching-process threshold framing without its
own separate derivation (a genuine future bridge candidate, see
`docs/structural_relations.md`).

## Data file

`data/usgs_earthquakes_m6plus_2000_2026.csv` — see
`data/real_data_manifest.json` entry `usgs_earthquakes_m6plus_2000_2026`
for exact source URL, retrieval timestamp, sha256. U.S. Government work,
public domain, no attribution required. All rows have USGS review status
`reviewed` (checked, not just assumed) -- but review status describes the
processing state of *existing* catalog rows, not overall catalog
completeness; it does not by itself rule out that additional matching
events from recent years are still being added to the catalog
(correction per `SCF_Nichtstationaere_Treiber_und_Kippen.md`, 2026-09-21).

## Protocol (immutable)

| Item | Value |
|---|---|
| Macro | annual count of M>=6.0 earthquakes worldwide |
| Calib window | 2000 -- 2019 (20 full calendar years) |
| Holdout window | 2020 -- 2025 (6 full calendar years) |
| Excluded | 2026 (partial year; source catalog truncated at 2026-09-20) |
| Baseline | persistence = last calib year's (2019) count |
| Metric | RMSE on 6 holdout years |
| Free params | mean annual rate over calib only |

## What the numbers say

From `verification/verify_earthquake_pilot_results.json` on the build
machine:

| Quantity | Value |
|---|---|
| model_rmse_holdout | 28.78 |
| baseline_rmse_holdout | 22.96 |
| model_beats_baseline | **False** |
| fitted mean annual rate | 153.95 /year (3079 events over 20 years) |
| baseline (2019 count) | 145 |
| holdout observed counts | 121, 157, 127, 147, 99, 145 (2020-2025) |

**Why the model loses:** the 20-year calib average (153.95/year) sits
above most of the holdout years, which include a notably quiet year
(2024, 99 events); **correction (2026-09-21, caught in independent review
by Astra):** this document previously and incorrectly stated that no
holdout year matches or exceeds the calib mean -- 2021 (157 events) does
exceed it. The flat persistence baseline still happens to anchor closer
to the holdout's actual range overall because 2019's count (145) was
already somewhat below the calib mean, but the "no year exceeds it" claim
itself was wrong and is retracted here.

**Independent follow-up finding (Astra, 2026-09-21):** a dispersion check
on the 20 calib years finds sample variance/mean (Fano factor) of 3.16
(mean 153.95, variance 486.26). Under an independent, equal-rate Poisson
model this ratio should be 1; the approximate dispersion statistic is
`D=60.01` on 19 degrees of freedom, upper-tail `p≈3.85e-6` against that
null. This is an exploratory diagnostic, not a mechanism test — it is
consistent with event clustering (e.g. aftershock sequences, which
self-exciting point processes like ETAS model explicitly), a genuinely
heterogeneous/time-varying rate, or catalog effects, and does not by
itself decide between them or establish any tipping behavior. It does
mean a simple homogeneous-Poisson description is too narrow for this
series' variance, independent of the RMSE comparison above.

This is a different mechanism from the COVID and NOAA findings — there is
no known regime change in large-earthquake occurrence over this period.
The RMSE result here should be read as ordinary sampling variability in a
modest, overdispersed count series rather than as the same kind of
structural (regime-change) failure as the COVID/NOAA cases. Reported
as-is, per protocol — **no retuning after seeing this result.**

## Verify

```bash
PYTHONPATH=src python verification/verify_earthquake_pilot.py
```

JSON report: `verification/verify_earthquake_pilot_results.json` — all
numbers from **that** run.
