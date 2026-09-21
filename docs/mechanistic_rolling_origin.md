# Common temporal forecast evaluation for the 3 mechanistic models (Milestone 48)

**Status:** review package (real per-row data throughout) — see
`MECHANISTIC_VALIDATION_ROADMAP.md` package 2. Johann-OK required before
any "core" promotion.

## Why this exists

`prompts/Answers/nicht_stationäre_Treiber/SCF_Review_f8e249f.md` (Astra,
2026-09-21): "jedes neue Modell wurde bisher gegen sein EIGENES
Trainingsfenster bewertet ... nicht gegen dieselben Zielgrößen, Ursprünge
und Horizonte wie die anderen." `validation/rolling_origin.py`
(NONSTATIONARY_ROADMAP.md package 1) already exists as a generic,
already-verified rolling-origin backtest harness. This module is its
**first application** to `covid_renewal.py`, `energy_balance.py`, and
`etas.py` — three genuinely different data-generating processes, each
adapted to its own natural forecasting target rather than forced into one
shape.

Model selection (bounds, initial guesses, generation-interval parameters)
was fixed by the already-shipped fitting functions **before** this module
ran — nothing here was tuned by looking at rolling-origin performance.

## Energy balance: beats every statistical baseline, at every horizon

Reuses `noaa_temp_pilot.py`'s **exact** 11 origins (1969–2019, step 5) and
5-year horizon, adding one predictor: refit the two-layer energy balance
model on calib-only years, then project it forward through **real,
already-observed** CO2 forcing (a "given future forcing is known"
forecast — not a forecast of the forcing itself).

| Predictor | Pooled RMSE (°C) |
|---|---:|
| persistence | 0.1376 |
| expanding-window linear | 0.1343 |
| last-30-years linear | 0.1171 |
| **energy_balance_mechanistic** | **0.1064** |

The mechanistic model wins outright — and not just on average: broken
down by lead year (1–5 years ahead, RMSE reported *separately* per
horizon, not pooled — directly answering Astra's "Fehler getrennt nach
Horizont" ask):

| Lead year | persistence | last30 | energy_balance_mechanistic |
|---:|---:|---:|---:|
| 1 | 0.097 | 0.107 | **0.092** |
| 2 | 0.132 | 0.117 | **0.112** |
| 3 | 0.139 | 0.099 | **0.098** |
| 4 | 0.156 | 0.144 | **0.122** |
| 5 | 0.156 | 0.113 | **0.106** |

The mechanistic model wins or ties at every single lead year — a robust,
not cherry-picked, result. This is a genuinely positive finding for a
CO2-only mechanistic model, earned through real out-of-sample testing,
not in-sample fit quality.

## COVID renewal: constant-R projection beats both baselines

Several origins (day-index 25, 30, 35, 40, 45, 50 within the same
January–March 2020 window used by `covid_renewal.py`'s own analysis and
Pilot A/B/C), 7-day horizon. The renewal predictor projects incidence
forward assuming R stays constant at its last calib-window estimate
(`project_incidence_constant_r`) — a standard, explicitly-flagged
epidemiological forecasting *assumption*, not a claim that R actually
stays constant.

| Predictor | Pooled RMSE (cases/day) |
|---|---:|
| persistence | 5696 |
| simple exponential extrapolation | 2012 |
| **renewal_constant_R** | **1029** |

## ETAS earthquakes: an honest, unforced mixed result

A point process needs a different adaptation: reuses
`earthquake_pilot.py`'s **exact** calib/holdout split (2000–2019 /
2020–2025) and its persistence/constant-rate baselines. ETAS is fit on
calib-only events using the explicit `t_end=2020-01-01` observation
window (MECHANISTIC_VALIDATION_ROADMAP.md package 1), then
`etas_expected_count_first_order` gives each holdout year's expected
count.

| Holdout year | Observed | ETAS (first-order) | Persistence | Constant-rate |
|---:|---:|---:|---:|---:|
| 2020 | 121 | 119.1 | 145 | 153.95 |
| 2021 | 157 | 116.0 | 145 | 153.95 |
| 2022 | 127 | 114.8 | 145 | 153.95 |
| 2023 | 147 | 114.1 | 145 | 153.95 |
| 2024 | 99 | 113.9 | 145 | 153.95 |
| 2025 | 145 | 113.1 | 145 | 153.95 |
| **RMSE** | | **26.31** | **22.96** | **28.78** |

**Reported as-is, no retuning after seeing this:** ETAS does **not** beat
the simple persistence baseline here (26.3 vs 23.0), though it does beat
the homogeneous-Poisson constant-rate baseline (28.8). This is a genuine,
unforced mixed result, not a win dressed up as one.

Two things worth noting honestly:
- The calib-only branching ratio here is **0.854** (subcritical) —
  notably different from the **1.02** (near-critical) found when fitting
  on the *full* catalog (NONSTATIONARY_ROADMAP.md package 5c /
  MECHANISTIC_VALIDATION_ROADMAP.md package 1). The branching ratio is
  not even stable across different fitting windows, reinforcing the
  fragility already documented there.
- `etas_expected_count_first_order` is explicitly a **first-order**
  approximation (background rate + direct triggering from calib history
  only) — it excludes "offspring of offspring" newly triggered within the
  forecast window itself, which matters more as the branching ratio
  approaches or exceeds 1. Since the calib-only ratio (0.854) is
  comfortably subcritical here, this is a genuine (if still approximate)
  lower bound; it would NOT be a trustworthy point forecast had the
  calib-only fit landed at or above criticality (see
  `etas_expected_count_first_order`'s own docstring).

## Verify

```bash
PYTHONPATH=src python verification/verify_mechanistic_rolling_origin.py
```

JSON report: `verification/verify_mechanistic_rolling_origin_results.json`
— all numbers from **that** run.
