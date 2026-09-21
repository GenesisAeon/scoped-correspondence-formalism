# Real Data Provenance (added 2026-09-20)

**Status:** raw data + provenance record for all datasets, and a
validation pilot on each: [docs/covid_pilot.md](covid_pilot.md)
(Milestone 6b, plus follow-ups B/C/D), [docs/noaa_temp_pilot.md](noaa_temp_pilot.md)
(Milestone 6c, plus a rolling-origin backtest), [docs/earthquake_pilot.md](earthquake_pilot.md)
(Milestone 6d). See also [NONSTATIONARY_ROADMAP.md](../NONSTATIONARY_ROADMAP.md)
for the follow-on work program (Astra's review, 2026-09-21). Johann-OK
required before any "core" promotion.

## Why this file exists

`AUDIT_ROADMAP.md` item 1 found that `data/cygnus_x1_radio_epochs.yaml`'s
per-epoch granularity was very likely AI-interpolated to four real
aggregate values, not a real archival transcription — see
`docs/cygnus_pilot.md` and `validation/core.DATA_PROVENANCE_WARNING`. To
avoid repeating that failure mode, every dataset below was fetched
**directly from its primary public source** with the exact URL/query
recorded, at a specific timestamp, and its sha256 stored in
`data/real_data_manifest.json` — never compiled from a paper description,
never copied from another package without checking that package's own
data lineage first.

Before using any of these files in code, verify them against the manifest:

```bash
PYTHONPATH=src python verification/verify_real_data_provenance.py
```

## Datasets

### `usgs_earthquakes_m6plus_2000_2026.csv`

- **Source:** USGS Earthquake Catalog (ComCat) via the FDSN Event Web
  Service — a live, queryable government seismological catalog.
- **Exact query:**
  `https://earthquake.usgs.gov/fdsnws/event/1/query?format=csv&starttime=2000-01-01&endtime=2026-09-20&minmagnitude=6.0&orderby=time`
- **Retrieved:** 2026-09-20T17:49:00Z. **License:** U.S. Government work,
  public domain.
- **Content:** 3974 earthquakes worldwide, magnitude ≥ 6.0, 2000-01-01
  through 2026-09-20. Raw API response, byte-for-byte.
- **Pilot built:** [docs/earthquake_pilot.md](earthquake_pilot.md)
  (Milestone 6d, `src/scoped_correspondence/validation/earthquake_pilot.py`,
  `verification/verify_earthquake_pilot.py`) — constant-rate
  (homogeneous-Poisson) annual-count model vs. persistence baseline on a
  fixed 2000-2019 calib / 2020-2025 holdout calendar split. Honest result:
  `model_beats_baseline=False` (ordinary sampling variability in a modest
  count series, not a structural regime change like COVID/NOAA). A
  magnitude-frequency (Gutenberg-Richter) comparison against
  `percolation/core.py`'s branching-process threshold framing (a genuine
  structural-relations bridge candidate per `docs/structural_relations.md`
  §2) remains open future work.

### `noaa_global_temp_anomaly_1880_2025.csv`

- **Source:** NOAA National Centers for Environmental Information (NCEI),
  Climate at a Glance: Global Time Series.
- **Exact query:**
  `https://www.ncei.noaa.gov/access/monitoring/climate-at-a-glance/global/time-series/globe/land_ocean/12/12/1880-2026/data.csv`
  (parameters select the annual Jan-Dec global land+ocean series).
- **Retrieved:** 2026-09-20T17:51:20Z. **License:** U.S. Government work,
  public domain.
- **Content:** 146 annual values (1880-2025), degrees Celsius departure
  from the 1901-2000 average. Includes NOAA's own `#`-prefixed header
  comment lines (title/units/base period) exactly as served.
- **Pilot built:** [docs/noaa_temp_pilot.md](noaa_temp_pilot.md)
  (Milestone 6c, `src/scoped_correspondence/validation/noaa_temp_pilot.py`,
  `verification/verify_noaa_temp_pilot.py`) — linear trend fit vs.
  persistence baseline on a fixed 1880-1999 calib / 2000-2025 holdout
  calendar split. Honest result: `model_beats_baseline=False` (the same
  structural failure mode as the COVID pilot on a completely different
  domain -- the calib window's average rate undershoots the actual
  post-2000 acceleration). Explicitly **not** proposed as data for the
  cubic normal form in `dynamics/core.py` without its own separately
  derived and checked model.

### `owid_covid_world_daily_2020_2023.csv`

- **Source:** Our World in Data COVID-19 dataset, JHU CSSE historical
  compact series (`public/data/jhu/full_data.csv` in `owid/covid-19-data`
  on GitHub), filtered client-side to `location == "World"` only.
- **Exact query:**
  `https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/jhu/full_data.csv`
  (the full file covers 232 locations; only the "World" rows were kept
  here — see `data/real_data_manifest.json` for the exact filter).
- **Retrieved:** 2026-09-20T17:50:10Z. **License:** CC BY 4.0 (Our World
  in Data); underlying counts originally from Johns Hopkins CSSE.
  **Attribution required** when used/published: "Data: Our World in Data
  / Johns Hopkins University CSSE COVID-19 Data Repository."
- **Content:** 1143 daily rows, 2020-01-22 through 2023-03-09: global new
  and total cases/deaths, plus weekly/biweekly rollups.
- **Pilot built:** [docs/covid_pilot.md](covid_pilot.md) (Milestone 6b,
  `src/scoped_correspondence/validation/covid_pilot.py`,
  `verification/verify_covid_pilot.py`) — exponential growth fit vs.
  persistence baseline on a fixed calib/holdout calendar split. Honest
  result: `model_beats_baseline=False` (the calib window spans a real
  regime change -- initial outbreak, containment dip, then global-wave
  onset -- so a single growth-rate fit underestimates the accelerating
  holdout). Reported as-is, not retuned. A growth-phase comparison against
  `percolation/core.py`'s threshold framing remains open future work.

### `owid_covid_china_world_daily_2020.csv`

- **Source:** same OWID/JHU compact series as above, filtered client-side
  to `location in ('China','World')` and dates `2020-01-22` through
  `2020-03-25`; RestOfWorld is computed as World minus China, not fetched
  as an independent series.
- **Exact query:** identical source URL to `owid_covid_world_daily_2020_2023.csv`
  (re-fetched 2026-09-21; sha256 of the full source file confirmed
  unchanged since the 2026-09-20 retrieval).
- **Retrieved:** 2026-09-21T10:18:31Z. **License / attribution:** same as
  above (CC BY 4.0, Our World in Data / JHU CSSE).
- **Content:** 128 rows (64 dates x 2 locations). China's first date has
  an empty `new_cases`/`weekly_cases` field in the source file (kept as-is).
- **Pilot built:** [docs/covid_pilot.md](covid_pilot.md) "Pilot D" section
  (Milestone 6f, NONSTATIONARY_ROADMAP.md package 2,
  `src/scoped_correspondence/validation/covid_country_decomposition.py`,
  `verification/verify_covid_country_decomposition.py`) -- decomposes
  Pilot A's World aggregate into China (declining, r=-0.0712/day) and
  RestOfWorld (r=+0.1459/day) components, fit independently and summed to
  predict the holdout. Result: the decomposed model (RMSE 6668.83) beats
  both a same-window aggregate fit (17686.65) and persistence (15932.68)
  by a wide margin, confirming Astra's mixture-identity hypothesis that
  changing country composition, not only within-country rate change,
  drives much of Pilot A's apparent acceleration. A mixture
  effective-rate diagnostic further shows this explains the *later* part
  of the window well but not an early rate swing tied to China's
  documented Feb 12-13 case-definition change.

## Ground rules going forward

- Every new "real data" file added to this repo needs an entry in
  `data/real_data_manifest.json` (source URL, exact query/filter, retrieval
  timestamp, sha256, license) and a matching section here — no exceptions,
  including for data that "looks" well-sourced.
- A dataset compiled or summarized by an AI assistant from a paper's prose
  (rather than downloaded directly from a primary archive, API, or the
  paper's own supplementary data files) does not qualify for this file;
  it must be labeled unverified/illustrative, as `docs/cygnus_pilot.md`
  now is.
- Building an actual validation pilot on one of these (comparable to
  Milestone 6) is separate future work, not implied by this file's
  existence.
