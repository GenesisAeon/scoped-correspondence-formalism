# Two-layer energy balance model, calibrated to real data (Milestone 45)

**Status:** review package (real per-row data; CO2-only forcing, a major
documented simplification) — see `NONSTATIONARY_ROADMAP.md` package 5b.
Johann-OK required before any "core" promotion.

## Why this exists

`prompts/Answers/nicht_stationäre_Treiber/SCF_Nichtstationaere_Treiber_und_Kippen.md`
(Astra, 2026-09-21) section 5.4 recommends a genuine climate mechanistic
model — the two-layer energy balance model (Geoffroy et al. 2013) —
instead of a bare linear-trend fit for the climate domain. The model:

```
C_s * dT_s/dt = F(t) - alpha*T_s - gamma*(T_s - T_d)
C_d * dT_d/dt = gamma*(T_s - T_d)
```

separates surface temperature `T_s`, deep-ocean temperature `T_d`,
radiative forcing `F(t)`, climate feedback `alpha`, and surface-to-deep
heat exchange `gamma`. It is linear in the temperatures for fixed
coefficients, yet produces delayed, curved responses to a changing
forcing — no tipping point is built into this form.

## Real forcing data

`F(t) = 5.35 * ln(CO2(t)/CO2_ref)` (Myhre et al. 1998), using **real**
Mauna Loa annual-mean atmospheric CO2 concentration
(`data/noaa_mauna_loa_co2_annual_1959_2025.txt`, NOAA GML, public domain,
fetched directly from `https://gml.noaa.gov/webdata/ccgg/trends/co2/co2_annmean_mlo.txt`)
— **not** a synthetic or assumed exponential CO2 curve. `CO2_ref` is the
first available year, 1959.

**IMPORTANT SCOPE LIMITATION: this is CO2-ONLY forcing.** Real historical
radiative forcing also includes other well-mixed greenhouse gases,
aerosols (a significant, uncertain, partly-cooling contribution), and
volcanic/solar variability — all omitted here. The fitted parameters do
**not** claim to recover the true physical climate-system constants.

## Fit to the real NOAA temperature anomaly series

`fit_energy_balance_model()` fits `(C_s, C_d, alpha, gamma, T0)` via
nonlinear least squares (multiple initial guesses, best RMSE kept) to the
overlap window with real CO2 data: 1959–2025 (67 years).

| Quantity | Value |
|---|---:|
| RMSE | 0.154 °C |
| `C_s` | 6.91 (W·yr/m²/K) |
| `C_d` | 97.2 (W·yr/m²/K) |
| `alpha` | 0.98 (W/m²/K) |
| `gamma` | 0.70 (W/m²/K) |
| `T0` (1959 initial anomaly) | -0.20 °C |

All four rate/capacity parameters are strictly positive (a physically
necessary condition for a stable relaxation system) and of a plausible
order of magnitude for a global mean climate response. This RMSE is in
the same ballpark as the purely statistical rolling-origin last-30-years
linear fit from `docs/noaa_temp_pilot.md` (pooled RMSE 0.119 °C over a
different, shorter comparison) — a genuinely physical, CO2-driven
mechanistic model does not dramatically outperform a well-chosen local
statistical fit here, which is itself an honest, informative finding
given the missing non-CO2 forcings.

**Identifiability caveat:** with CO2-only forcing and a single historical
annual temperature record, `C_d` and `gamma` in particular are only
weakly and jointly constrained — multiple `(C_d, gamma)` combinations can
give nearly the same surface-temperature trajectory (a real, well-known
limitation in climate science: equilibrium climate sensitivity is
notoriously hard to pin down from the historical record alone, which is
why real assessments use step-response GCM experiments to identify these
parameters separately). No profile-likelihood-style identifiability check
(`identifiability.profile_likelihood`) is performed here; the reported
fit is the best among several optimizer starts, not a claim of a
uniquely identified physical optimum.

## An honest limitation, made visible

The model **undershoots observed warming more in the most recent decade
than in the earliest decade** of the overlap (mean residual
observed-minus-predicted: +0.10 °C in 1959–1968 vs. +0.24 °C in
2016–2025). This is consistent with a well-documented real effect: as
aerosol emissions have declined in recent decades (due to clean-air
policies), their partial masking of greenhouse-gas warming has
diminished, "unmasking" more of the CO2-driven signal than a CO2-only
model — with no aerosol term at all — can capture. This connects directly
to the same "a simple model calibrated over a heterogeneous or
incompletely-specified period underestimates recent acceleration" theme
found independently in `docs/covid_pilot.md` (Pilot A) and
`docs/noaa_temp_pilot.md`'s original linear-trend result, now traced to a
concrete, physically-motivated cause (missing aerosol forcing) rather
than left as an unexplained model failure.

## Verify

```bash
PYTHONPATH=src python verification/verify_energy_balance.py
```

JSON report: `verification/verify_energy_balance_results.json` — all
numbers from **that** run.
