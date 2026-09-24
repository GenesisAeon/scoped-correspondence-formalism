# Parallel linear reservoirs: one time scale or two?

DOMAIN_EXPANSION_ROADMAP.md Paket B3a — response to
`prompts/Answers/nicht_stationäre_Treiber/SCF_DOMAIN_EXPANSION_IMPLEMENTATION_PLAN.md`,
section 9.2-9.3. Module:
[`dynamics/linear_reservoirs.py`](../src/scoped_correspondence/dynamics/linear_reservoirs.py).
Verification:
[`verify_linear_reservoirs.py`](../verification/verify_linear_reservoirs.py)
(11/11 checks).

**Correction (2026-09-24, response to
[SCF_Review_fcc9a43.md](../prompts/Answers/nicht_stationäre_Treiber/SCF_Review_fcc9a43.md),
findings R3+R3b — two real numerical bugs):**

- **R3:** `convolution_discharge` completely missed FAST kernels. A naive
  quadrature over `[0,t]` has no knowledge of a kernel's own timescale
  `1/k` — for `k=100000`, the kernel is essentially a delta spike of width
  `~1e-5` that the adaptive sampler's initial grid can miss entirely.
  Astra's exact counterexample (`S0=0, alpha=1, u=1, k=100000, t=1`, exact
  answer `1-e^-100000≈1`) returned `2.06e-45` from the old code. Fixed by
  substituting `v=k_j*(t-s)` PER RESERVOIR before integrating — this
  rescales every reservoir's decay to exactly rate `1` in `v`, so the
  quadrature always sees an O(1)-scale integrand regardless of `k_j`.
- **R3b:** `reservoir_interval_discharge` lost all precision for tiny
  `dt` — the mass-balance form subtracts two nearly-equal storage values
  and divides by the same tiny `dt`. `reservoir_interval_discharge(1,0,1,
  1e-17)` returned exactly `0.0` instead of the true `≈1`. Fixed by using
  the algebraically equivalent, cancellation-free direct form
  `qbar = k·S0·E(z) + α·u·(1-E(z))` (`z=k·dt`, `E(z)=(1-e^-z)/z` via
  `-expm1(-z)/z`), derived directly from the closed-form update — never
  subtracting two close storage values.

## The model

For reservoir `j`, `dS_j/dt = α_j·u(t) - k_j·S_j`, `q(t) = Σ_j k_j·S_j(t)`,
`α_j≥0`, `Σα_j=1`. Under CONSTANT input over `[t,t+Δ]` this is exact:

```
S_j(t+Δ) = e^{-k_jΔ}·S_j(t) + α_j·u·(1-e^{-k_jΔ})/k_j
```

computed as `-expm1(-kΔ)/k`, not `(1-exp(-kΔ))/k` directly — the naive
form loses precision to cancellation as `kΔ→0`; the `k=0` limit
(`S+α·u·Δ`) is taken explicitly rather than trusted to survive that limit
numerically (checked: `k=1e-10` agrees with the `k=0` closed form to
`<1e-6`). Plan's control numbers: `S0=3, u=2, k=0.5, Δ=1` → `S1
≈3.393469340287367`, mean discharge (via mass balance,
`q̄=(S0+uΔ-S1)/Δ`, not by evaluating the kernel) `≈1.6065306597126332` —
independently reproduced exactly, then cross-checked against a
high-precision `scipy.integrate.solve_ivp` run of the *same* ODE.

## Identifiability, checked explicitly

- **Two rates coinciding (`k1=k2`)** collapse to the single-reservoir
  total — the split becomes unobservable.
- **`α2=0`** with a matching second initial state reduces exactly to the
  single-reservoir case.
- **Label swap (`1↔2`)** leaves the observed total discharge trajectory
  unchanged — the model has no privileged ordering.
- **Different initial splits, same total `S0`** generally produce
  *different* total discharge shortly after — the initial partition
  between fast and slow storage is *not* identifiable from the observed
  total alone, confirmed as a genuine numerical divergence (not just a
  naming point).

## Memory kernel and convolution

For arbitrary (not necessarily piecewise-constant) input, the linear
model has an exact convolution representation,
`q(t) = Σ_j k_j·S_j(0)·e^{-k_jt} + ∫_0^t h(t-s)·u(s)ds`,
`h(u)=Σ_j α_j·k_j·e^{-k_ju}` — the same Mori-Zwanzig-style memory-kernel
idea already used in `closure/linear_memory_projection.py`, specialized to
this diagonal case. Checked against the discrete step recursion's implied
instantaneous discharge on a piecewise-constant control case (`<1e-8`
agreement), and the single-reservoir kernel is confirmed to integrate to
exactly `1` over `[0,∞)`.

Per the plan's explicit either/or (section 9.3), the more general
hidden-state-excitation extension of `linear_memory_projection.py`
(`∫B·exp(D(t-s))·f_z(s)ds` for a driven hidden block) was **not** built
here — this direct reservoir convolution was implemented and checked
instead, as the plan explicitly allows.

## Scope

Linear reservoirs only — no nonlinear runoff, snow, or evapotranspiration
processes (those are explicitly a later extension per plan section 9.2,
"nur bei klar benannter Restabweichung"). This module is purely
synthetic/analytic; the real CAMELS-DE data pilot (Paket B3b) is a
separate, not-yet-completed package.
