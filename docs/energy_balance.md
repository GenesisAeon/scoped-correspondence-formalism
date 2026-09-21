# Two-layer energy balance model, calibrated to real data (Milestone 45)

**Status:** review package (real per-row data; CO2-only forcing, a major
documented simplification) — see `NONSTATIONARY_ROADMAP.md` package 5b.
Johann-OK required before any "core" promotion.

**CORRECTION (2026-09-21, external review by Astra):** the fit originally
reported here (RMSE 0.154 °C) was found to be a poorly-converged local
optimum — the identical code, run in a different environment
(newer scipy/numpy), converged to RMSE 0.119 °C from the same starting
points, and a broader search reached RMSE ~0.090 °C. This has been fixed
by switching the optimizer's inner loop to an exact matrix-exponential
integrator (avoiding `solve_ivp`'s adaptive-step non-smoothness as an
optimization objective) plus explicit, physically-motivated parameter
bounds and several diverse starting points, which now converges to the
*same* optimum regardless of starting point — a real robustness fix, not
a lucky rerun. **The previously reported "aerosol-unmasking" residual
asymmetry has been substantially walked back** — see below; it was
largely an artifact of the poor convergence, not a robust finding.

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
bounded nonlinear least squares (exact matrix-exponential propagation,
`scipy.optimize.least_squares(method="trf")`, explicit physically-motivated
`PARAM_BOUNDS`, several diverse starting points, best RMSE kept — all
converge to the same optimum) to the overlap window with real CO2 data:
1959–2025 (67 years).

| Quantity | Value |
|---|---:|
| RMSE | 0.0904 °C |
| `C_s` | 7.37 (W·yr/m²/K) |
| `C_d` | 63.86 (W·yr/m²/K) |
| `alpha` | **0.30 (W/m²/K) — saturates its lower bound** |
| `gamma` | 1.57 (W/m²/K) |
| `T0` (1959 initial anomaly) | -0.019 °C |
| exact-vs-`solve_ivp` cross-check max diff | 8.1e-8 °C |

**`alpha` saturating its lower bound is the important, honestly-reported
finding here — not the improved RMSE.** `PARAM_BOUNDS` restricts `alpha`
to `[0.3, 3.0]` specifically to exclude a degenerate, unphysical
near-zero-feedback region (an *unconstrained* refit — performed only as
an external-review diagnostic, not shipped — pushes `alpha` to ~4.5e-5,
i.e. almost no radiative damping, a textbook overfitting artifact rather
than a better climate model). That the *constrained* optimum still sits
exactly at the physically-motivated floor shows this CO2-only model
cannot pin down the climate feedback parameter from this single
historical record even when unphysical solutions are excluded by
construction — a stronger identifiability warning than a mere
"weakly constrained" caveat.

This RMSE (0.090 °C) now modestly *beats* the purely statistical
rolling-origin last-30-years linear fit from `docs/noaa_temp_pilot.md`
(pooled RMSE 0.119 °C over a different, shorter comparison window) — but
given the bound-saturation above, this should NOT be read as evidence of
a well-identified mechanistic advantage; it is fully consistent with a
flexible-enough linear system finding a good in-sample fit while its
individual parameters remain poorly determined.

**Identifiability caveat:** with CO2-only forcing and a single historical
annual temperature record, `C_d` and `gamma` (and now demonstrably
`alpha`) are only weakly constrained — multiple parameter combinations
can give nearly the same surface-temperature trajectory (a real,
well-known limitation in climate science: equilibrium climate sensitivity
is notoriously hard to pin down from the historical record alone, which
is why real assessments use step-response GCM experiments to identify
these parameters separately). No profile-likelihood-style identifiability
check (`identifiability.profile_likelihood`) is performed here; the
reported fit is the best among several bounded optimizer starts (which
now agree with each other, unlike the original unbounded fit), not a
claim of a uniquely identified physical optimum.

**Reference-level caveat (flagged by external review):** `F` is
referenced to CO2 in 1959, while the NOAA temperature series is a
departure from the 1901–2000 mean — two different baselines, not
reconciled here. A baseline shift is not fully absorbed by the free `T0`
parameter alone (it would also require an additive forcing offset); not
fixed by adding a 6th free parameter given the identifiability problems
already documented above.

## A retracted interpretation, corrected in the open

**The originally reported "aerosol-unmasking" residual asymmetry (+0.10 °C
early vs. +0.24 °C recent) was substantially an artifact of the
poorly-converged fit documented in the CORRECTION above, not primarily a
real physical signal.** Under the corrected, robust fit, the asymmetry
shrinks by roughly an order of magnitude: mean residual
(observed-minus-predicted) is **-0.009 °C in 1959–1968** vs. **+0.026 °C
in 2016–2025**. The recent residual is still (barely) larger, but both
values are now close to zero and far too small to confidently attribute
to a specific omitted forcing such as aerosols.

This is retracted here explicitly, in the open, rather than quietly
edited away: a wrong confident causal narrative was built on top of an
insufficiently-verified numerical result. The genuinely robust, honest
finding from this module is the identifiability warning above (`alpha`
saturating its bound), not a story about aerosol unmasking. The general
"a simple model calibrated over an incompletely-specified period can
underestimate acceleration" theme connecting `docs/covid_pilot.md` (Pilot
A) and `docs/noaa_temp_pilot.md`'s original linear-trend result still
stands independently of this correction — but this module no longer
claims to have traced it to a specific physical cause here.

## Verify

```bash
PYTHONPATH=src python verification/verify_energy_balance.py
```

JSON report: `verification/verify_energy_balance_results.json` — all
numbers from **that** run.
