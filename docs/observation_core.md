# Observation Core (Milestone 2 - review package)

**Status:** review package only - not yet linked from README/GLOSSARY as accepted "core".
Johann-OK required before any core promotion.

## What this is

Python APIs for the information / observation layer (ex-CREP): channel capacity
`K_info`, discrete retention `R_info`, and realized rate `eta_info`.

```text
src/scoped_correspondence/
  observation/
    __init__.py
    core.py
  errors.py          # ScopeViolationError
  legacy/            # historical CREP names
```

## Mapping to FORMALISM.md section 2

| section-2 symbol | API | Notes |
|---|---|---|
| `K_info` | `channel_capacity(bandwidth, snr)` | Shannon-Hartley B*log2(1+P/N); Bit/time |
| `R_info` | `retention(mutual_information, entropy, *, discrete=True)` | I/H; only for discrete X with 0<H<inf |
| `eta_info` | `realized_rate(rate, capacity, *, rate_unit, capacity_unit)` | rate/K_info; same channel and time unit |

## ScopeViolationError choices

- `retention(..., discrete=False)` raises (no silent differential-entropy substitution; FORMALISM.md section 3).
- `retention` with H<=0 or H=inf raises.
- `realized_rate` with absolute bit tags (`bit` / `bits` without time) raises (quotient would be a duration; c06).
- `realized_rate` with capacity<=0 raises.
- Bit vs nat mismatch between rate and capacity raises.

## Equivalence verification

`verification/verify_observation_core.py` matches legacy evidence from
`verify_formalism.py` for **p03_information_channel** and **c06_information_window**
exactly (numeric values from the script run / checked-in JSON).

## Legacy adapters

`scoped_correspondence.legacy`: `shannon_hartley_K`, `information_retention_R`,
`realized_eta` map to the new Observation APIs. Layer markdown documents are not edited.
