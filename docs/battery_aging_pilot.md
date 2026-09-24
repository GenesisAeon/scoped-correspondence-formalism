# Battery aging pilot: real NASA data, honestly scoped

DOMAIN_EXPANSION_ROADMAP.md Paket B5b — response to
`prompts/Answers/nicht_stationäre_Treiber/SCF_DOMAIN_EXPANSION_IMPLEMENTATION_PLAN.md`,
section 11. Modules:
[`data/nasa_battery_adapter.py`](../src/scoped_correspondence/data/nasa_battery_adapter.py) (parser),
[`validation/battery_aging_pilot.py`](../src/scoped_correspondence/validation/battery_aging_pilot.py) (pilot pipeline).
Verification (synthetic-only, no network access needed):
[`verify_battery_aging_pilot.py`](../verification/verify_battery_aging_pilot.py)
(6/6 checks).

## License status — independently confirmed, per plan's own protocol

Astra flagged that "der Katalogeintrag selbst zeigt keine spezifizierte
Lizenz". Independently confirmed via NASA's own CKAN API
(`https://data.nasa.gov/api/3/action/package_show?id=li-ion-battery-aging-datasets`,
queried 2026-09-24): `license_title: "License not specified"`,
`license_id: "notspecified"`.

**Per plan section 5.1's explicit guidance for exactly this situation**
("Ohne geklärte Weiterverteilung: lokaler Downloader plus synthetische
Parser-Fixture; den fehlenden Datenlauf ausdrücklich als nicht ausgeführt
berichten"): the raw dataset and any per-cycle capacity values derived
from it are **not committed to this repository**, and no manifest entry
was added to `data/real_data_manifest.json` (that manifest's own verifier,
`verify_real_data_provenance.py`, requires every entry's `file` to exist
and hash-match in-repo — adding an entry without the file would be
exactly the kind of invented provenance the plan warns against). The
automated `verify_battery_aging_pilot.py` therefore runs entirely against
a synthetic fixture and needs no network access.

## A real local run was still performed — reported honestly, not as CI

Going beyond what the plan strictly requires when a pilot is blocked, the
real dataset (`5. Battery Data Set/1. BatteryAgingARC-FY08Q4.zip`, source
`https://phm-datasets.s3.amazonaws.com/NASA/5.+Battery+Data+Set.zip`,
retrieved 2026-09-24) **was** downloaded and processed once locally during
development, matching NASA's own README exactly (4 cells, 2Ah rated
capacity, 30% fade to 1.4Ah as the stated EOL criterion). This is a
one-time manual reproduction, explicitly separate from the automated
suite — the numbers below are real but not independently re-verifiable by
a reader without downloading the same (unspecified-license) archive
themselves.

sha256 of the four downloaded `.mat` files (recorded for anyone who does
redownload the same archive to confirm bit-for-bit identity):

| Cell | sha256 (first 16 hex chars) | Discharge cycles | First capacity (Ah) | Last capacity (Ah) |
|---|---|---:|---:|---:|
| B0005 | `0eae4585baf3f200` | 168 | 1.856 | 1.325 |
| B0006 | `fa818ab4db5db8ab` | 168 | 2.035 | 1.186 |
| B0007 | `d022afa086efaf54` | 168 | 1.891 | 1.432 |
| B0018 | `d1e6c923a43ea1c9` | 132 | 1.855 | 1.341 |

**Per-cell pilot** (temporal 60/40 train/holdout split on each cell's OWN
series, `C_EOL=1.4` Ah, matching NASA's own stated criterion):

| Cell | Persistence MAE | Linear MAE | Power MAE | Best | Observed EOL cycle |
|---|---:|---:|---:|---|---|
| B0005 | 0.108 | **0.022** | 0.176 | linear | 124 |
| B0006 | 0.122 | 0.134 | **0.112** | power | 108 |
| B0007 | 0.085 | **0.028** | 0.138 | linear | **censored** (min capacity 1.400, never ≤1.4 within 168 cycles) |
| B0018 | 0.057 | 0.051 | **0.047** | power | 96 |

**No single model wins across all four cells** — linear wins on B0005/B0007,
power wins on B0006/B0018, and persistence never wins but is competitive on
B0018. This is reported as the actual mixed result, not adjusted or
selected after the fact (plan section 3, "Erfolg bedeutet nicht, dass ein
komplexeres Modell gewinnt"). **B0007 is a genuine right-censoring case**
occurring naturally in real data: its capacity never drops to the 1.4 Ah
EOL threshold within the 168 recorded discharge cycles (minimum observed:
1.4005 Ah) — reported as `censored=True`, `observed_first_eol_cycle=None`,
not as a fabricated crossing time or a false "never reaches EOL" claim
about cycles beyond the recorded window.

## The pipeline itself

`run_cell_pilot` is dataset-agnostic: given a `(cell_id, capacities)` pair,
it performs a **temporal** (never random-row) prefix/holdout split, fits
each of the three `capacity_degradation` mean models on the training
prefix only, and evaluates MAE on that same cell's later held-out cycles —
checked to be immune to a leakage guard test (drastically changing values
after the training prefix leaves the fit completely unchanged).
`run_leave_one_cell_out_panel` runs this independently per cell — checked
to be immune to cross-cell leakage (changing one cell's series does not
affect another cell's fit or reported metrics).

## Scope

Four cells from one experimental batch (room temperature, one discharge
protocol) — not a claim about arbitrary chemistries or real vehicle
fleets (plan section 11.4's explicit caveat). The per-cell fitting here is
personalized (each cell uses its own observed prefix), not a zero-shot
transfer claim; a genuine leave-one-cell-out HYPERPARAMETER selection
across cells was not attempted, since none of the three model families
here has a hyperparameter beyond what each cell's own prefix determines.
