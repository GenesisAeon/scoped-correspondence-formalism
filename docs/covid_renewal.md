# COVID renewal-equation R_t estimator (Milestone 44)

**Status:** review package (real per-row data; a deterministic point
estimate, not a full Bayesian re-implementation of EpiEstim) — see
`NONSTATIONARY_ROADMAP.md` package 5a. Johann-OK required before any
"core" promotion.

## Why this exists

`prompts/Answers/nicht_stationäre_Treiber/SCF_Nichtstationaere_Treiber_und_Kippen.md`
(Astra, 2026-09-21) section 5.4 recommends a genuine epidemiological
mechanistic model — the renewal equation with a time-varying reproduction
number `R_t` (Cori et al. 2013) — instead of "another global exponential
curve" for the COVID domain. This module implements the standard
instantaneous-`R` estimator, simplified to a deterministic point estimate
(no Bayesian/gamma-posterior smoothing, no sliding estimation window —
appropriately scoped, not a full EpiEstim reimplementation):

```
Lambda_t = sum_{s=1}^{S_max} w_s * I_{t-s}
R_t = I_t / Lambda_t
```

`w_s` is a discretized Gamma **generation-interval** distribution matched
to the serial-interval estimate of Nishiura, Linton & Akhmetzhanov (2020):
mean 4.7 days, sd 2.9 days. `I_t` is `cases_7day_avg` — the same smoothed
World series used throughout `covid_pilot.py` — **not** raw daily counts;
this inherits the moving-average autocorrelation caveat Astra's review
raised for early-warning use (a 7-day trailing mean induces lag-1
autocorrelation of 6/7 from pure arithmetic, independent of any real
signal), and the same caveat applies to `R_t`'s own smoothness here.

## Self-consistency check

For pure exponential growth `I_t = I_0 * e^{r t}`, the Wallinga & Lipsitch
(2007) closed-form relation `R = 1 / sum_s w_s * e^{-r s}` gives the
`R` implied by a growth rate `r`. The renewal-equation estimator and this
closed-form relation **must** agree exactly on a purely exponential
series — and they do, to floating-point precision (`instantaneous_r`
returns a constant series matching `wallinga_lipsitch_r(r)` exactly for a
synthetic `r=0.1` growth curve).

## Applied to the real World series

`run_covid_renewal_analysis()` computes `R_t` over the same window as
Pilot A (2020-01-28 to 2020-03-25):

| Period | `R_t` behavior |
|---|---|
| Late Feb 2020 (containment dip) | dips **below 1** |
| Mid-March 2020 (global acceleration) | rises to **1.5 – 1.9** |

This matches, via a completely independently-computed method, the
regime-change story already found in `docs/covid_pilot.md` (Pilot A's
single-rate failure) and `docs/covid_pilot.md`'s Pilot D (China vs.
RestOfWorld decomposition).

**Cross-check against the already-fitted exponential rates:** converting
Pilot A's near-flat fitted rate (`r=0.00744/day`) via Wallinga-Lipsitch
gives `R≈1.04` — right at the epidemic threshold, consistent with a
window that averages a declining and an accelerating sub-period. Pilot
B's fast-growth rate (`r=0.121/day`, the clean post-trough window) gives
`R≈1.68` — closely matching the directly-computed March `R_t` values
(1.5–1.9) from a **completely independent calculation** (the renewal
equation on daily incidence, vs. a log-linear OLS fit on the same
series). Two independent methods agreeing is a meaningful cross-check.

## Scope

- Deterministic point estimate only — no credible interval, no sliding
  estimation window (real EpiEstim implementations typically average
  over a several-day window to reduce noise); this trades some
  statistical robustness for a transparent, hand-checkable formula.
- Generation interval fixed to one literature estimate (Nishiura et al.
  2020); no sensitivity analysis across alternative serial-interval
  estimates is performed here.
- `cases_7day_avg` is a smoothed incidence proxy, not raw case counts —
  see the moving-average autocorrelation caveat above.
- No claim about reporting delay, ascertainment fraction, or changing
  country composition within `R_t` itself — those remain separate,
  documented open questions (see `docs/covid_pilot.md`'s Pilot D for the
  composition angle).

**Follow-up (2026-09-21, MECHANISTIC_VALIDATION_ROADMAP.md package 2):** a
genuine multi-origin, out-of-sample forecast check — projecting incidence
forward assuming R stays constant at its last calib estimate — beats both
persistence and a simple exponential extrapolation baseline. See
[docs/mechanistic_rolling_origin.md](mechanistic_rolling_origin.md).

**Structural bridge B8 (2026-09-21):** for constant `R`, this renewal
kernel's total mass IS the Hawkes & Oakes (1974) branching ratio — the
SAME general quantity as `etas.py`'s `etas_branching_ratio` for a
structurally different kernel. See
[docs/structural_relations.md](structural_relations.md#b8--positive-kernels--branching-operators-covid-renewal--etas-hawkes).

## Verify

```bash
PYTHONPATH=src python verification/verify_covid_renewal.py
```

JSON report: `verification/verify_covid_renewal_results.json` — all
numbers from **that** run.
