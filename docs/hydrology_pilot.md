# Hydrology pilot: does a second discharge time scale help — on real German catchments

DOMAIN_EXPANSION_ROADMAP.md Paket B3b — response to
`prompts/Answers/nicht_stationäre_Treiber/SCF_DOMAIN_EXPANSION_IMPLEMENTATION_PLAN.md`,
section 9, and to
[SCF_Review_fcc9a43.md](../prompts/Answers/nicht_stationäre_Treiber/SCF_Review_fcc9a43.md)
finding R7. Modules:
[`data/http_range_reader.py`](../src/scoped_correspondence/data/http_range_reader.py),
[`data/camels_de_adapter.py`](../src/scoped_correspondence/data/camels_de_adapter.py),
[`validation/hydrology_pilot.py`](../src/scoped_correspondence/validation/hydrology_pilot.py).
Verification (synthetic/local-server-only, no network access needed):
[`verify_http_range_reader.py`](../verification/verify_http_range_reader.py) (4/4),
[`verify_hydrology_pilot.py`](../verification/verify_hydrology_pilot.py) (7/7).

**Correction (2026-09-25, response to
[SCF_INTEGRATED_EXTENSION_IMPLEMENTATION_PLAN.md](../prompts/Answers/nicht_stationäre_Treiber/SCF_INTEGRATED_EXTENSION_IMPLEMENTATION_PLAN.md),
Paket C0 — two real bugs in the code that produced the numbers below,
independently reproduced before fixing):**

- **Finding A:** the persistence baseline's prediction for the FIRST test
  day used that day's OWN target value (`pred_persist_test[0] =
  Q_test[0]`) — a self-referential, artificially perfect "prediction"
  instead of the actually prior day's discharge. Reproduced exactly:
  `Q_test=[10,12,13]` gave `[10,10,12]` (day 0 predicts itself).
- **Finding B:** the reservoir state was propagated across
  `train_mask | test_mask` — the union of only the two disjoint periods —
  silently skipping the ~1826 days (2006–2010) strictly between training
  and test. The state at the end of 2005 was fed directly into the first
  simulated test day as if zero time had passed. Reproduced exactly on a
  synthetic exact-generator case with a real gap: the old union
  construction gave MAE `~1.1×10⁻³` against the true trajectory; the
  fixed full-calendar-span construction gives MAE `0.0` (identical to
  the true trajectory).

Both fixed by simulating over the FULL CONTIGUOUS calendar span from the
start of training through the end of testing (never a union of disjoint
sub-periods) — new regression checks `c0_finding_a_...` and
`c0_finding_b_...` in `verify_hydrology_pilot.py`. **Measured impact on
the 6 real catchments below: small.** Every catchment's best-model ranking
is UNCHANGED (persistence still wins overall on all 6; the two-reservoir
model still beats the one-reservoir model on all 6) — the corrected
numbers differ from the original ones only in the 3rd–4th significant
digit for most catchments, because these reservoirs' fitted decay rates
are fast enough, and the actually-observed 2006–2010 precipitation drives
the state to a comparable regime by 2011 regardless of the 2005 starting
condition. This is a property of these 6 catchments' specific dynamics,
not a general guarantee — a catchment with much slower reservoir decay or
a longer gap could show a materially different, uncorrected result. The
tables below show the CORRECTED numbers only.

## This pilot was previously (wrongly) called blocked

An earlier assessment treated the CAMELS-DE data pilot as blocked because
the archive is a single ~2.18GB Zenodo file with no per-catchment download
option. **Astra's second review (finding R7) demonstrated this was
incorrect**: the archive's HTTP host honors byte-range requests. A small
buffered file-like object (`HTTPRangeFile`, verified with an explicit
"the server actually returned HTTP 206" check — it aborts rather than
silently falling back to a full download if a server ignores `Range`)
lets `zipfile.ZipFile` read the central directory and extract individual
members directly. Total data transferred for this entire pilot — 4
attribute tables plus 6 full 70-year daily timeseries — was **under 20MB**,
against a 2.18GB archive.

License: **CC-BY-4.0** (unlike the NASA battery case, this permits
redistributing small derived excerpts) — confirmed via the Zenodo API
(`license.id: "cc-by-4.0"`). Attribution: Loritz, R. et al. (2024).
CAMELS-DE: hydro-meteorological time series and attributes for 1582
catchments in Germany. *Earth System Science Data* 16, 5625–5642. DOI:
10.5194/essd-16-5625-2024.

## Catchment selection (fixed before looking at any model's fit)

From the 1582 catchments, filtered to those with a flow record covering
1991–2020 and ≥95% completeness (196 candidates), split into unregulated
(`dams_num==0`) and regulated (`dams_num>0`) groups, each sorted by
`frac_snow`, taking the low/median/high-snow-fraction catchment from each
group — 3 + 3 = 6, spanning different retention and runoff
characteristics. **Not claimed representative** of Germany's 1582
catchments — a small, diverse technical pilot panel (plan section 9.4).

| Gauge ID | Area (km²) | Dams | Snow frac. | Completeness | Record |
|---|---:|---:|---:|---:|---|
| DEA11490 | 129.4 | 0 (unregulated) | 0.02 | 98.8% | 1951–2020 |
| DE211310 | 722.1 | 0 (unregulated) | 0.09 | 100.0% | 1951–2020 |
| DEE10610 | 24.4 | 0 (unregulated) | 0.25 | 100.0% | 1951–2020 |
| DEA11180 | 4264.3 | 14 (regulated) | 0.03 | 100.0% | 1951–2020 |
| DE110500 | 68.1 | 2 (regulated) | 0.08 | 100.0% | 1951–2020 |
| DEG10330 | 123.2 | 4 (regulated) | 0.19 | 100.0% | 1951–2020 |

Small derived excerpts (date, `precipitation_mean`, `discharge_vol_obs` —
3 of the original 22 columns, no row filtering) are committed at
`data/camels_de/CAMELS_DE_<gauge_id>_precip_discharge.csv`, manifest
entries in `data/real_data_manifest.json` (hash-verified by
`verify_real_data_provenance.py`).

## Model panel and protocol

Conditional hindcast (plan section 9.5, mode A — actually observed
precipitation used throughout, including the test period; **no operational
forecast claimed**). Training 1991–2005 (15 years), test 2011–2020 (10
years, disjoint and later); 2006–2010 not used (no cross-catchment
hyperparameter needs tuning beyond what each catchment's own training
period already determines). Driving input `u(t) = c·P(t)`, `c` an
effective runoff coefficient fitted on the training period only — **not a
complete water balance with identified evapotranspiration**. Discharge
converted `mm/day = 86.4·(m³/s)/area_km²` (plan section 9.4). Four
compared models: persistence (previous day), seasonal climatology
(day-of-month/day-of-year mean from training only), one linear reservoir,
two parallel linear reservoirs (`dynamics.linear_reservoirs`, unchanged
from Paket B3a — including the R3/R3b numerical fixes from Paket 8).

## Real results (test period 2011–2020, MAE in mm/day)

| Gauge | Persistence | Seasonal | 1-Reservoir | 2-Reservoir | Best |
|---|---:|---:|---:|---:|---|
| DEA11490 | **0.064** | 0.129 | 0.123 | 0.100 | persistence |
| DE211310 | **0.095** | 0.412 | 0.424 | 0.413 | persistence |
| DEE10610 | **0.561** | 1.547 | 1.356 | 1.237 | persistence |
| DEA11180 | **0.078** | 0.371 | 0.357 | 0.352 | persistence |
| DE110500 | **0.384** | 1.115 | 0.876 | 0.873 | persistence |
| DEG10330 | **0.233** | 1.158 | 1.098 | 1.096 | persistence |

**Persistence wins overall MAE on all 6 catchments, decisively.** This is
an honest, negative-for-the-mechanistic-models result, reported as such
(plan section 3: "Erfolg bedeutet nicht, dass ein komplexeres Modell
gewinnt"; a "sauber belegtes Null- oder Negativergebnis" is a complete
result). It is also an expected hydrological pattern: daily river
discharge has strong day-to-day autocorrelation, and a two-parameter
(or four-parameter) precipitation-only conceptual model, fit once on 15
years and never updated, is not expected to beat a same-day-lag baseline
in raw MAE over a full decade — a fair comparison, since ALL models here
receive the SAME allowed information (plan section 5.2, point 6), and
persistence itself is one of the plan's own prescribed baselines
(section 9.2), not a late addition to make the mechanistic models look
worse.

**But the two-reservoir model DOES beat the one-reservoir model on all 6
catchments** (0.100<0.123, 0.413<0.424, 1.237<1.356, 0.352<0.357,
0.873<0.876, 1.096<1.098) — a consistent, if sometimes small, improvement
from adding the second time scale, answering the plan's actual central
question about time-scale structure independently of whether either beats
persistence.

### Low-flow window (test-period days below the training 10th percentile)

| Gauge | Persistence | Seasonal | 1-Reservoir | 2-Reservoir | n days |
|---|---:|---:|---:|---:|---:|
| DEA11490 | **0.012** | 0.192 | 0.095 | 0.082 | 279 |
| DE211310 | **0.016** | 0.244 | 0.291 | 0.325 | 578 |
| DEE10610 | **0.036** | 1.020 | 0.733 | 0.825 | 943 |
| DEA11180 | **0.013** | 0.257 | 0.200 | 0.199 | 726 |
| DE110500 | **0.014** | 0.775 | 0.465 | 0.496 | 840 |
| DEG10330 | **0.013** | 0.509 | 0.680 | 0.701 | 572 |

Persistence wins even more decisively during low flow (discharge changes
very slowly day-to-day at low flow — again an expected pattern, not a
modeling failure). The two-reservoir model beats the one-reservoir model
on low-flow days at 2 of 6 catchments (DEA11490, DEA11180) and loses at
the other 4 — a genuinely **mixed** result for the low-flow question
specifically, reported without adjustment.

## A real data-quality finding, fixed in the pipeline

An isolated single missing day in a 70-year daily series (DEA11490,
DE110500) initially poisoned the WHOLE persistence-baseline MAE into
`NaN` via `np.mean` over an array containing one `NaN` lag value — fixed
by scoring persistence over its own valid subset (excluding only the
specific day whose lag source was missing) and reporting the exact
`n_scored` count per baseline explicitly (`CatchmentHydroResult.n_scored`),
rather than silently dropping to a smaller but unstated sample or
propagating `NaN` through the whole metric.

## Scope

Six catchments, one country, one climate regime — not a claim about
arbitrary catchments or climates (plan section 9.4's own caveat). The
`c` runoff coefficient is a single effective parameter, not a validated
physical evapotranspiration estimate. `forecast_as_of_origin` mode (plan
section 9.5, mode B — using only information actually available at a real
forecast origin) is explicitly NOT attempted here; this pilot is entirely
`conditional_hindcast`.
