# Dynamics Core (Milestone 2 - review package)

**Status:** review package only - not yet linked from README/GLOSSARY as accepted "core".
Johann-OK required before any core promotion.

## What this is

Python APIs for the system / dynamics layer (ex-UTAC): static sigmoid response,
relaxation recovery rate S_rec, and the corrected cubic normal form.

```text
src/scoped_correspondence/
  dynamics/
    __init__.py
    core.py
  legacy/            # historical UTAC names
```

## Mapping to FORMALISM.md section 2

| section-2 symbol | API | Notes |
|---|---|---|
| `beta_response` | `sigmoid_response(u, beta_response, theta_u, p_max)` | Static curve only; unit 1/[u] |
| `S_rec` | `recovery_rate_from_relaxation(tau)` -> 1/tau | Independent of beta_response |
| `S_rec` (cubic) | `recovery_rate_at_equilibrium` / `CubicNormalForm.s_rec` | At eq.: S_rec(0)=-a/tau, S_rec(+/-sqrt(a))=2a/tau for b=0 |

## beta_response vs S_rec (Review finding A)

For z_dot = -(z - p(u))/tau with fixed u, S_rec = 1/tau. The sigmoid steepness
beta_response only shifts the equilibrium location z*=p(u) and never enters
the recovery rate. Units differ (1/[u] vs 1/time); the APIs are separate
functions so the two cannot be conflated.

## Equivalence verification

`verification/verify_dynamics_core.py` matches **p02_cusp_region** and
**p01_cusp_branches_and_time** from `verify_formalism.py` exactly (roots,
discriminants, recovery rates / signs).

## Legacy adapters

`utac_sigmoid`, `utac_recovery_rate`, `cusp_dxdt`, `cubic_normal_form`,
`gamma_domain_style` map to Dynamics APIs. Layer markdown documents are not edited.
