# NOAA global temperature anomaly trend pilot (Milestone 6c)

**Status:** real-data trend pilot (review package) on **verified** per-row
data — see `data/real_data_manifest.json` /
[docs/real_data_provenance.md](real_data_provenance.md). Johann-OK required
before any "core" promotion. A `model_beats_baseline: false` result is a
**valid complete** outcome, and IS the result of this run.

## Mapping to ROADMAP.md §3

1. States, boundaries, inputs, timescales, observations — annual global
   land+ocean temperature anomaly (degrees C, departure from the
   1901-2000 average), 1880-2025.
2. Transformation / time map — linear trend
   `anomaly(year) = intercept + slope*(year - year_ref)`.
3. Domain of expected relation + error measure — calib-only fit; holdout
   RMSE.
4. Comparison models + separate prediction data — **persistence baseline**
   (last calib year's anomaly held constant) vs. linear trend; fixed
   calendar split (full 20th century calib, 21st century holdout) locked
   **before** fit.
5. Uncertainty / counterfindings allowed — including "no gain beyond
   baseline", which is what happened here.

This pilot is **one domain, one macro, one fixed window**. No claim about
`dynamics/core.py`'s cubic normal form or any other Baustein without its
own separate derivation.

## Data file

`data/noaa_global_temp_anomaly_1880_2025.csv` — see
`data/real_data_manifest.json` entry `noaa_global_temp_anomaly_1880_2025`
for exact source URL, retrieval timestamp, sha256. U.S. Government work,
public domain, no attribution required.

## Protocol (immutable)

| Item | Value |
|---|---|
| Macro | annual anomaly, degrees C |
| Calib window | 1880 -- 1999 (full 20th century, a round calendar boundary) |
| Holdout window | 2000 -- 2025 (21st century to date) |
| Baseline | persistence = last calib year's (1999) anomaly |
| Metric | RMSE on 26 holdout years |
| Free params | `(slope, intercept)` via OLS, calib only |

## What the numbers say

From `verification/verify_noaa_temp_pilot_results.json` on the build
machine:

| Quantity | Value |
|---|---|
| model_rmse_holdout | 0.4604 |
| baseline_rmse_holdout | 0.4301 |
| model_beats_baseline | **False** |
| fitted slope | 0.005324 °C/year |
| baseline (1999 anomaly) | 0.40 °C |

**Why the model loses:** this is structurally the same failure mode as
the COVID Pilot A ([docs/covid_pilot.md](covid_pilot.md)) on a completely
different domain. The 120-year calib window averages a much slower
warming rate (~0.0053 °C/year) than the acceleration actually observed
after 2000 — the model's own well-documented "hiatus" decades (roughly
1945-1975, aerosol cooling) pull the single linear fit's slope down.
Extrapolated forward, the model predicts anomalies around 0.28-0.30 °C
for the early 2000s, well below the observed 0.40-0.60 °C range, while
the flat persistence baseline (anchored at 1999's already-elevated 0.40
°C) tracks the early holdout years more closely.

This is reported as-is, per protocol — **no retuning of the window after
seeing this result.** Combined with the COVID finding, it is a second,
independent illustration (different domain, different mechanism, same
structural failure) of why a single trend estimated over a period that
itself contains a rate change is an unreliable extrapolator, even though
each sub-period may be well-described by its own simple model. No
cross-domain universality is claimed from two examples; it is recorded
here as an honest observation worth keeping in mind.

## Verify

```bash
PYTHONPATH=src python verification/verify_noaa_temp_pilot.py
```

JSON report: `verification/verify_noaa_temp_pilot_results.json` — all
numbers from **that** run.
