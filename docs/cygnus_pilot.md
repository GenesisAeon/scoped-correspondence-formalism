# Cygnus X-1 jet PA pilot (Milestone 6)

**Status:** illustrative method demonstration (review package), **not** an
independently verified empirical validation. Johann-OK required before any
"core" promotion. A `model_beats_baseline: false` result is a **valid
complete** outcome — do not retune the split or parameters after seeing
holdout.

**Data provenance (added 2026-09-20, AUDIT_ROADMAP.md item 1 / A01):** the
per-epoch table in `data/cygnus_x1_radio_epochs.yaml` is **unverified**.
Only 4 aggregate values are confirmed from Prabu et al. 2026 (initial/final
jet position angle, 18-year observation baseline) — see the sibling
package `GenesisAeon/cygnus-jet-utac`'s `data/prabu2026_measurements.yaml`.
No source for the 18 individually dated epochs (per-row MJD, PA, flux) was
found, and the declared `year`/`mjd` fields diverge by a systematically
growing amount (0 days in 2007 up to ~90 days by 2020) — consistent with
AI interpolation to the 4 real aggregate numbers, not archival
transcription. The RMSE numbers below are a correct, reproducible
calculation on that data; they are not evidence of real-world predictive
skill until a genuine per-epoch source is confirmed.

## Mapping to ROADMAP.md §3

ROADMAP §3 asks for one limited self-similarity claim checked with:

1. States, boundaries, inputs, timescales, observations — here: VLBI jet
   position angle `jet_pa_deg` (deg) over 18 epochs (2006.2–2023.8).
2. Transformation / time map — relaxation
   `pa(t) = pa_eq + (pa0 - pa_eq)*exp(-r*(t - t_ref))` with `t` = epoch year.
3. Domain of expected relation + error measure — calib-only fit; holdout RMSE.
4. Comparison models + separate prediction data — **persistence baseline**
   (last calib PA held constant) vs relaxation; temporal first-9 / last-9 split
   locked in `DatasetManifest` **before** fit.
5. Uncertainty / counterfindings allowed — including "no gain beyond baseline".

This pilot is **one domain, one macro**. No cross-domain universality claim
(ROADMAP §3 item 4 / domain comparison is out of scope).

## Dynamics helpers used

From `src/scoped_correspondence/dynamics/core.py`:

- `recovery_rate_from_relaxation(tau)` — when fitted `r > 0`, set `tau = 1/r`
  and record `S_rec = recovery_rate_from_relaxation(tau)` (equals `r`).
- `recovery_rate_at_equilibrium` — **not** used: it is the cubic normal-form
  local rate, not the PA relaxation ODE.

No other modules were modified except package exports calling validation.

## Data file

`data/cygnus_x1_radio_epochs.yaml` copied **1:1** from
`GenesisAeon/cygnus-jet-utac` (same path under that package). Citations from
YAML header: Stirling et al. 2001, Rushton et al. 2011, Miller-Jones et al. 2021,
Prabu et al. 2026.

**Do not invent numbers.** Do **not** reuse cygnus-jet-utac σ / Γ_jet /
efficiency (documented circularity in `worked_example_cygnus_jet_utac.md`).

## Protocol (immutable)

| Item | Value |
|---|---|
| Macro | `jet_pa_deg` only |
| Split | calib indices 0..8, holdout 9..17 (first 9 / last 9) |
| Baseline | persistence = last calib `jet_pa_deg` |
| Metric | RMSE on 9 holdout epochs |
| Free params | `(pa_eq, r)` on calib only; `t_ref`, `pa0` fixed from first calib epoch |

Actual years under this index split: calib **2006.2–2014.0**, holdout
**2015.2–2023.8**. (Prompt parenthetical year ranges were approximate.)

## Verify

```bash
PYTHONPATH=src python verification/verify_cygnus_pilot.py
```

JSON report: `verification/verify_cygnus_pilot_results.json` — all numbers from
**that** run.


## Latest verify numbers (this artifact build)

From `verification/verify_cygnus_pilot_results.json` on the build machine:

| Quantity | Value |
|---|---|
| model_rmse_holdout | 3.0710033393836396 |
| baseline_rmse_holdout | 3.704501765869917 |
| model_beats_baseline | True |
| pa_eq | 8416.303430278667 |
| r | 0.00015000000000000001 |
| baseline (last calib PA) | 38.8 |

Note: LS with `r >= 0` yields large `pa_eq` and small `r` (near-linear drift;
weakly identified as relaxation). Reported honestly. No Γ_jet / σ reuse.
Re-run on the target machine to refresh JSON from that environment.
