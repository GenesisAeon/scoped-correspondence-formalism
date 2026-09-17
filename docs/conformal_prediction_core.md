# Split Conformal Prediction Core (Milestone 13)

**Status:** review package only — not yet linked from README/GLOSSARY as accepted "core".
Johann-OK required before any core promotion.

## What this is

Typed Python helpers for **split / inductive conformal prediction** on absolute
residuals, following Lei et al. 2018. Coverage is recorded as
`coverage_kind = "marginal_exchangeable"` — **not** guaranteed / exact /
conditional.

```text
src/scoped_correspondence/
  validation/
    core.py          # UNCHANGED — Cygnus PA pilot (M6); not edited
    conformal.py     # NEW — calibrate_split_conformal + predict_interval + report
```

M13 does **not** apply conformal intervals to Cygnus data, does **not**
implement weighted / adaptive conformal, and does **not** mutate
`validation/core.py`, `FORMALISM.md`, or the layer docs.

Package-level `scoped_correspondence/__init__.py` is **not** rewritten here
(submodule-local wiring via `validation/__init__.py` only — avoids fighting
parallel M11/M12 branches on the shared package `__init__`).

## Mapping

| Source | Claim / formula | API | Notes |
|---|---|---|---|
| Lei et al. 2018, DOI 10.1080/01621459.2017.1307116 | split conformal: \(k=\lceil(n+1)(1-\alpha)\rceil\)-th calib residual; \(C(x)=[\hat\mu(x)-q,\hat\mu(x)+q]\) | `calibrate_split_conformal`, `predict_interval` | finite-sample marginal under exchangeability |
| Lei et al. 2018 Thm. 2 | \(P(Y_{n+1}\in C)\ge 1-\alpha\) if i.i.d. / exchangeable | `SplitConformalReport.coverage_kind` | always `"marginal_exchangeable"` |
| M6 `split_epochs` | refuse index snooping / leakage | `assert_disjoint_calib_holdout` | `VAL-CONF-LEAK-001` |

## Formulas

### Split conformal quantile

Given calibration residuals \(R_1,\ldots,R_n\) (typically \(|y_i-\hat y_i|\)) and
miscoverage \(\alpha\in(0,1)\):

\[
k = \bigl\lceil (n+1)(1-\alpha) \bigr\rceil,\qquad
q = R_{(k)}
\]

(the \(k\)-th smallest residual; if \(k=n+1\), \(q=+\infty\)).

**Why the naive quantile breaks coverage.** The ordinary empirical
\((1-\alpha)\)-quantile of the \(n\) residuals (no \(+1\)) ignores the test
residual's rank among the \(n+1\) exchangeable scores. Finite-sample
marginal coverage \(P(Y_{\mathrm{new}}\in C)\ge 1-\alpha\) under
exchangeability requires the inflated order statistic with the \((n+1)\)
correction and ceiling (Lei et al. 2018). Omitting it can undercover in
finite samples even for i.i.d. residuals.

### Prediction interval

\[
C(\hat y) = [\hat y - q,\ \hat y + q]
\]

(`predict_interval`).

### Coverage kind (disclaimer)

`coverage_kind` is **always** `"marginal_exchangeable"`. An interval built
this way does **not** claim:

- guaranteed / exact coverage in every finite draw without exchangeability,
- conditional coverage given \(X=x\),
- validity after adaptive / weighted residual reweighting (out of scope).

## Worked examples (hand-checkable)

### Example A (spec)

Residuals \(R=(1,1,2,3)\), \(\alpha=0.2\):

\[
n=4,\quad (n+1)(1-\alpha)=5\cdot 0.8=4,\quad k=\lceil 4\rceil=4,\quad q=R_{(4)}=3.
\]

For \(\hat y=10\): \(C=[7,13]\).

### Example B (independent)

Residuals \(R=(0.5,1.0,1.5,2.0,4.0)\), \(\alpha=0.25\):

\[
n=5,\quad (n+1)(1-\alpha)=6\cdot 0.75=4.5,\quad k=\lceil 4.5\rceil=5,\quad q=R_{(5)}=4.0.
\]

For \(\hat y=10\): \(C=[6,14]\).

### Anti-leak (`VAL-CONF-LEAK-001`)

`assert_disjoint_calib_holdout([0,1,2],[2,3])` raises `ScopeViolationError`
(overlap at index `2`). Disjoint sets pass. Same spirit as M6
`split_epochs` refusing non-manifest index sets.

## Hand-checkable verification

Run:

```bash
PYTHONPATH=src python verification/verify_conformal_prediction_core.py
```

Expect Example A → `q=3`, interval `[7,13]`; Example B → `q=4`, `[6,14]`;
leak guard fires on overlap; `coverage_kind == "marginal_exchangeable"`.

## Untouched (forbidden)

- `src/scoped_correspondence/validation/core.py`
- `FORMALISM.md`
- layer docs: `context_transformations.md`, `coupling_layer_afet.md`,
  `system_layer_utac.md`, `information_layer_crep.md`,
  `sheaf_contextuality.md`, `pid_redundancy_bottleneck.md`,
  `emergence_and_closure.md`
- Cygnus data application / weighted / adaptive conformal
