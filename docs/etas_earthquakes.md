# ETAS self-exciting point process, fit to the real USGS catalog (Milestone 46)

**Status:** review package (real per-row data; temporal-only fit on a
pooled global multi-region catalog, a major documented simplification) —
see `NONSTATIONARY_ROADMAP.md` package 5c. Johann-OK required before any
"core" promotion.

## Why this exists

`prompts/Answers/nicht_stationäre_Treiber/SCF_Nichtstationaere_Treiber_und_Kippen.md`
(Astra, 2026-09-21) section 5.4 recommends a genuine earthquake-domain
mechanistic model — ETAS (Ogata 1988) — instead of a homogeneous-Poisson
constant-rate fit. It also gives this module a direct target: the
overdispersion already found independently in `docs/earthquake_pilot.md`
(Fano factor 3.16 on the 20 calibration years, dispersion statistic
`D=60.01` on 19 df, `p≈3.85e-6` against an equal-rate Poisson null). ETAS
tests whether self-exciting clustering (aftershock sequences) is a
sufficient mechanistic explanation for that overdispersion.

```
lambda(t | H_t) = mu + sum_{t_i<t} K * exp(alpha*(M_i-M0)) / (t-t_i+c)^p
```

`mu`: constant background rate; `K, c, p`: Omori-Utsu aftershock-decay
kernel; `alpha`: magnitude-productivity scaling; `M0=6.0` is the
catalog's own magnitude-of-completeness (its `minmagnitude` filter).

## Real data

`data/usgs_earthquakes_m6plus_2000_2026.csv` — the same catalog used in
`docs/earthquake_pilot.md` (see `data/real_data_manifest.json`), no new
dataset needed. 3974 events, 2000-01 through 2026-09 (partial).

## Fit

`fit_etas_model()` fits `(mu, K, c, p, alpha)` via maximum likelihood
(Nelder-Mead on a log/logit-parametrized objective). **Correction
(2026-09-21, external review by Astra):** the default is a SINGLE
informed starting point, not multiple starts — this text previously said
"multiple Nelder-Mead starts," which was inaccurate. A single start is
used deliberately to fit within the verification suite's per-script time
budget (see `fit_etas_model`'s PERFORMANCE NOTE for why this is still
reliable: 140/250/~1400-evaluation budgets, and a second independently
written implementation, all land within 0.3 nats of the same optimum).
The fit is compared against the closed-form MLE homogeneous-Poisson null
(`mu_hat = N/T`) via AIC.

| Quantity | Value |
|---|---:|
| n_events | 3974 |
| `mu` (background rate, /day) | 0.2884 |
| `K` | 0.005541 |
| `c` (days) | 0.006088 |
| `p` | 1.0249 |
| `alpha` | 1.9756 |
| branching ratio | 1.024 |
| log-likelihood (ETAS) | -6887.10 |
| log-likelihood (null Poisson) | -7543.23 |
| AIC (ETAS) | 13784.21 |
| AIC (null Poisson) | 15088.46 |

From `verification/verify_etas_results.json` on the build machine. The
AIC gap (1304, decisively favoring ETAS) is stable across every tested
optimizer budget (140 / 250 / ~1400 Nelder-Mead evaluations all land
within 0.3 nats of the same log-likelihood — see the PERFORMANCE NOTE in
`fit_etas_model`'s docstring) — this is a genuinely converged basin, not
an artifact of the time-boxed default optimizer budget used here to stay
within the verification suite's per-script time limit.

**Two honest, interconnected findings, made visible rather than hidden:**

1. **`p` converges to ≈1.02, i.e. a very slowly decaying (near-logarithmic)
   aftershock kernel.** Real regional Omori-Utsu fits typically find
   larger `p` (roughly 1.0-1.5, but for well-isolated single sequences,
   not this pooled setting). This is plausibly an artifact of pooling many
   regions with genuinely different, faster individual decay rates:
   averaging many heterogeneous exponential-family decays across unrelated
   sequences tends to look like one much slower/heavier-tailed decay at
   the population level (see SCOPE LIMITATION below). Not a claim that
   real regional aftershock decay has `p≈1`.
2. **Branching ratio ≈1.02 — right at criticality**, not comfortably
   sub- or super-critical. Interpreted cautiously given finding 1: with a
   pooled catalog whose fitted kernel shape is itself a mixing artifact,
   this number should be read as "the pooled catalog exhibits about as
   much apparent self-excitation as a critical branching process," not as
   a precise physical branching-ratio estimate for global seismicity.

**Correction (2026-09-21, external review by Astra): the branching ratio
is far more fragile than finding 2 above suggested, and this needed
stating explicitly.** The branching ratio's kernel-time-integral
`c^(1-p)/(p-1)` runs to infinity; at the fitted `p=1.0249`, only
**≈30.0%** of that integral's mass falls within the catalog's own
9756-day span — roughly 70% comes from an extrapolated tail far beyond
anything the data actually observes. A pure sensitivity check (varying
only `p`, other fitted parameters held fixed — NOT a refit, NOT a
confidence interval) shows how much this matters:

| `p` | branching ratio |
|---:|---:|
| 1.015 | 1.62 |
| 1.0249 (fitted) | 1.02 |
| 1.04 | 0.69 |
| 1.06 | 0.51 |

A change in `p` of a few thousandths swings the branching ratio between
clearly super-critical and clearly sub-critical. Given finding 1 (that
`p` itself is plausibly a pooling artifact, not a well-identified
physical decay rate), **the "right at criticality" framing above should
be read as illustrative, not as a validated criticality claim** — the
robust part of this module's finding is the AIC comparison (self-excitation
present, decisively better than a Poisson null), not the specific
branching-ratio value.

## IMPORTANT SCOPE LIMITATION

This is a **TEMPORAL-ONLY** fit (no spatial kernel) on a **pooled global,
multi-region** catalog. Real ETAS practice fits a single well-defined
regional sequence with its own magnitude of completeness; pooling the
whole globe means two temporally-close but geographically unrelated
events (e.g. a Chile and a Japan earthquake) are treated by this model as
potential trigger/aftershock pairs, which a spatial-temporal ETAS would
correctly rule out. **The fitted parameters do not claim to recover
physically calibrated, region-specific Omori-Utsu constants.** This
module tests only the qualitative question of whether a self-exciting
temporal kernel explains the pooled catalog's overdispersion better than
an equal-rate Poisson null — not a hazard model, not a regional forecast.

## Verify

```bash
PYTHONPATH=src python verification/verify_etas.py
```

JSON report: `verification/verify_etas_results.json` — all numbers from
**that** run.
