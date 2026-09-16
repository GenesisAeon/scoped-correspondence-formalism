# Identifiability Core (Milestone 5 - review package)

**Status:** review package only - not yet linked from README/GLOSSARY as accepted "core".
Johann-OK required before any core promotion.

## What this is

Python APIs for observation conditioning, parameter non-identifiability,
SVD-vs-EI decoupling, fixed-ensemble data-processing inequality, and
effective-information baseline dependence. Exact legacy anchors from
`verification/verify_extensions.py` (e02, e07, e08, e09, e12; optional e15).

Not a Dataset Manifest / Train-Holdout split / real-data ValidationReport
(that half of the Uncertainty & Validation roadmap needs Johann's domain
decision first — see `ROADMAP.md` section 3 and prompt `11_teil2_...`).

```text
src/scoped_correspondence/
  identifiability/
    __init__.py
    core.py
```

## Mapping to FORMALISM.md sections 10 / 12

| Document | Claim / formula | API | Legacy |
|---|---|---|---|
| Reconstruction / e02 | Conditioning factor `1/\|sin alpha\|`; alias delay vectors for `+/- theta` | `delay_amplification`, `indistinguishable_delay_vectors`, `delay_conditioning_report` | e02 |
| §12 | Reparametrization `Gamma'=k Gamma`, `sigma'=sigma/k` leaves `tanh(sigma Gamma)` | `parameter_scaling_invariance` | e12 |
| §12 | Response Jacobian wrt `(sigma, a)` for `tanh(sigma a g)` has rank 1 | `identifiability_jacobian_rank` | e12 |
| §10 | Typ 1 = specified advantage vs a **named** baseline; positive SVD emergence does **not** imply positive EI gain | `svd_emergence_vs_ei` | e09 |
| §10 / EI | Fixed-ensemble DPI: macro MI ≤ micro MI under shared `q` | `fixed_ensemble_data_processing` | e08 |
| §10 | `EI_q(P)=I_q(Z_t;Z_{t+1})`; ΔEI only relative to declared intervention distributions | `effective_information_baseline` | e07 |
| (bonus) | Exact finite-state predictive states (not a learned ε-machine) | `predictive_states` | e15 |

## Exact legacy targets (from this script run)

| Quantity | Value |
|---|---|
| `delta_svd` (uniform 4×4) | `0.75` |
| `EI` on that channel (uniform q) | `0` |
| Partitions checked (e09 / Bell B₄) | `15` |
| `EI_uniform_macro` / `EI_matched_micro` | `1` |
| Jacobian rank (`sigma*a`) | `1` |
| Fixed-ensemble comparisons (seed 1977) | `150` (= 10 × 15) |

## Hand-checkable verification

`verification/verify_identifiability_core.py` covers MIG-ID checks for
e02, e07, e08, e09, e12, and optional e15, matching
`verification/extension_results.json` evidence keys exactly.

## Out of scope

Dataset Manifest; Train/Holdout; real-data pilot; continuous sensor-noise
models; mutation of FORMALISM.md or layer/extension docs; changes to
`correspondence/`, `observation/`, `dynamics/`, `coupling/`, `closure/`,
`viability/`, `membership/`, or `legacy/` (call / cross-check only).
