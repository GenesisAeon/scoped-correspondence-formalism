# Multi-country / multi-window generalization of the COVID growth pilot (Milestone 51)

**Status:** review package (real per-row data) — see
`MECHANISTIC_VALIDATION_ROADMAP.md` package 5. Johann-OK required before
any "core" promotion.

## Why this exists

`prompts/Answers/nicht_stationäre_Treiber/SCF_Review_f8e249f.md` (Astra,
2026-09-21): "Mehrere unabhängige Länder- und Zeitfenster mit
unverändertem Verfahren (nicht nur die bereits bekannte
China/Rest-Zerlegung auf demselben März-2020-Fenster)."

`covid_pilot.py`'s `fit_exponential_growth` / `predict_exponential` /
`persistence_baseline_covid` are reused **completely unchanged** —
imported, never reimplemented or retuned — and applied to two new
countries over Pilot A's exact original window, plus the World aggregate
over a new, independent time window. No parameter, window boundary, or
country choice was selected by looking at any of these series' own fit
quality.

## Test 1 — same window, new countries (Germany, United States)

Real per-row data freshly fetched from the same OWID/JHU source
(`data/real_data_manifest.json` entry
`owid_covid_germany_usa_daily_2020`), filtered to Germany and the United
States, over Pilot A's **exact, unmodified** calendar window (calib
2020-01-27 to 2020-03-11, holdout 2020-03-12 to 2020-03-25).

**Result: both fits fail outright** — `fit_exponential_growth` correctly
refuses a zero-`cases_7day_avg` calib day (Germany: 2020-02-18; United
States: 2020-02-20; the log-linear fit is undefined at zero). This is not
a bug and not silently worked around by shifting the window per country
(which would break "unverändertes Verfahren"). It is itself an honest,
informative generalization result: **individual-country early-2020
counts include zero/near-zero days that the World AGGREGATE smooths
over** — Pilot A's own procedure, which works fine on the aggregate,
genuinely does not carry over to individual countries in this earliest
window without modification. This connects directly to the
China/Rest-of-World finding in `docs/covid_pilot.md` (Pilot D): country
composition and heterogeneity already mattered there too, from a
different angle.

## Test 2 — same procedure, new time window (World, Omicron wave)

The World aggregate (already-stored, already-verified
`data/owid_covid_world_daily_2020_2023.csv` — no new fetch needed), over
a window anchored on the WHO's 2021-11-26 designation of Omicron as a
Variant of Concern — an externally documented milestone, chosen the SAME
way Pilot A's own window was anchored on the WHO pandemic declaration.
Calib/holdout **lengths** are identical to Pilot A's (45 / 14 days);
boundaries are mechanically derived from the anchor date, not chosen by
looking at the data (calib 2021-10-13 to 2021-11-26, holdout 2021-11-27
to 2021-12-10).

| Quantity | Value |
|---|---:|
| Fitted growth rate `r` | 0.0079 /day |
| Model RMSE (holdout) | 19181 |
| Persistence baseline RMSE (holdout) | 42841 |
| Model beats baseline | **True** |

The unchanged procedure **succeeds and beats the baseline** on this
independent, later wave — a genuinely positive generalization result,
earned honestly (no retuning, boundaries fixed before looking at the
fit).

## Honest summary

The SAME unchanged procedure gives three different, all-informative
outcomes across three independent applications: fails outright on two
individual countries in the earliest window (a real data-sparsity issue,
not a bug), and succeeds on a different wave of the World aggregate. This
is a more complete and more honest picture of "does this procedure
generalize" than any single additional test alone would give.

## Verify

```bash
PYTHONPATH=src python verification/verify_covid_multi_country.py
```

JSON report: `verification/verify_covid_multi_country_results.json` —
all numbers from **that** run.
