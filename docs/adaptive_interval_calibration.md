# Adaptive prediction-interval calibration

CAPABILITY_EXPANSION_ROADMAP.md Priority 1, response to Astra's 2026-09-24
capability assessment: "Zuerst eine robuste einfache Referenz ... danach
Adaptive Conformal Inference beziehungsweise Conformal PID Control als
Kandidaten vergleichen." Module:
[`validation/adaptive_interval_calibration.py`](../src/scoped_correspondence/validation/adaptive_interval_calibration.py).
Verification: [`verify_adaptive_interval_calibration.py`](../verification/verify_adaptive_interval_calibration.py)
(5/5 checks).

## Three methods, one causal quantile machine

All three methods use the exact same strict-temporal-eligibility causal
quantile as `mechanistic_probabilistic_evaluation.leave_one_origin_out_intervals`
(a residual is only usable once its OWN target time has occurred relative
to the current forecast origin — no lookahead). They differ only in how
the miscoverage level `alpha_t` used for that quantile evolves:

- **`rolling_reference`** — `alpha_t` fixed at the nominal `alpha_target`.
  The simple baseline Astra asked to compare against first: "vergangene
  Prognosefehler fortlaufend sammeln und daraus ... Intervalle
  kalibrieren."
- **`aci`** — Adaptive Conformal Inference (Gibbs & Candès 2024, JMLR 25):
  `alpha_{t+1} = alpha_t + gamma*(alpha_target - err_t)`. A miss pushes
  `alpha_t` down (wider interval next time); a hit pushes it slightly up.
- **`pid`** — a **Proportional + Integral subset** of Conformal PID
  Control (Angelopoulos, Candès & Tibshirani 2023, NeurIPS). The Integral
  term is exactly the ACI recursion (own rate `gamma_i`); the Proportional
  term additionally reacts to the local miscoverage rate over a short
  trailing window. **Not implemented:** the published method's learned
  "scorecaster" (a separate forecasting model for the quantile itself) and
  its bounded saturation link function on the integrator — this is
  explicitly a partial implementation, not the full algorithm.

## Coverage semantics — read this before citing a coverage number

ACI's real guarantee (Gibbs & Candès 2024, Theorem 1) is a **long-run
average** miscoverage rate near `alpha_target` under *arbitrary*
distribution shift — a genuine and non-trivial result. It is **not** a
claim of correct coverage at any individual time point, and there is no
published guarantee at all for the simplified P+I variant used here for
`pid`. An empirical coverage number landing near `1 - alpha_target` in the
tables below is evidence of long-run average calibration, not pointwise
or conditional calibration.

## Synthetic regression test: does the adaptive recursion actually help?

A deterministic regime-shift sequence (residual magnitude oscillating in
`[0.5, 1.5]` for 30 steps, then jumping to oscillate in `[7.5, 8.5]` for
20 more) shows the mechanism working as intended: in the first 10
post-shift trials, the fixed `rolling_reference` method misses badly
(its pooled empirical quantile is still dominated by 30 pre-shift points)
while `aci` reacts within a handful of misses and recovers noticeably
faster — checked as a strict quantitative comparison in
`check_aci_recovers_faster_after_regime_shift`, not just eyeballed. A
companion `check_no_lookahead_prefix_replay` check confirms all three
methods are exactly causal: replaying only a prefix of a sequence
reproduces byte-identical `alpha_t`/interval/coverage decisions for the
overlapping early trials.

## Real-data results (nominal 80% interval, `alpha_target=0.2`)

**Energy balance** (11 origins × 5 lead years pooled, `n=40` per
predictor/method) — notably better than the 52.5% pooled coverage
previously reported by the leave-one-origin-out module (which uses a
different, asymmetric lo/hi-quantile construction on SIGNED residuals; this
module uses a single symmetric quantile on ABSOLUTE residuals, a
methodologically different but equally legitimate construction — the two
numbers are not directly comparable, and both are reported honestly under
their own name rather than picking the more flattering one):

| Predictor | rolling_reference | aci | pid |
|---|---:|---:|---:|
| persistence | 75.0% | 75.0% | 72.5% |
| expanding | 77.5% | 72.5% | 70.0% |
| last30 | 85.0% | 85.0% | 85.0% |
| energy_balance_mechanistic | 72.5% | 70.0% | 75.0% |

No method dominates here — all three land within a few points of each
other and of the 80% nominal target. On this pilot, at this sample size
(`n=40`), the simple `rolling_reference` is already reasonably calibrated;
the online adaptation does not show a clear advantage (nor a clear
disadvantage) over it.

**COVID renewal** (6 origins × 7-day horizon, `n=19` per predictor/method)
— a starkly different, and instructive, result:

| Predictor | rolling_reference | aci | pid |
|---|---:|---:|---:|
| persistence | 0.0% | 0.0% | 0.0% |
| exponential_extrapolation | 57.9% | 57.9% | 52.6% |
| renewal_constant_R | 57.9% | 57.9% | 57.9% |

`persistence` gets **0% coverage under all three methods** — the
underlying 2020 exponential-growth window makes every new residual larger
than every previously observed one, so no quantile built only from past
residuals (however its confidence level is chosen) can ever catch up. This
is a genuine limitation of any purely residual-quantile-based approach
(adaptive or not) against a monotonically escalating error sequence, not a
bug in the adaptive recursions — the honest conclusion is that this
predictor needs a structurally different uncertainty model (see Priority 2,
latent renewal dynamics with an explicit observation model), not a
better-tuned calibration wrapper. For the other two COVID predictors, all
three methods again land within a few points of each other; `n=19` is too
small to distinguish them meaningfully.

## Bottom line

The mechanism (ACI reacting faster than a fixed reference after a
persistent shift) is real and demonstrated on a controlled synthetic
example. On the repository's actual pilots, sample sizes are small enough
(`n=19`–`40`) and — for COVID `persistence` — the failure mode severe
enough, that the adaptive methods neither clearly help nor hurt relative
to the simple rolling reference. This is reported as-is rather than
picking whichever run looks best.
