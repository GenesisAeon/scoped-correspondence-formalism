# Brownian motion with drift: a positive mean does not mean low risk

DOMAIN_EXPANSION_ROADMAP.md Paket B4 — response to
`prompts/Answers/nicht_stationäre_Treiber/SCF_DOMAIN_EXPANSION_IMPLEMENTATION_PLAN.md`,
section 10. Module:
[`viability/first_passage_diffusion.py`](../src/scoped_correspondence/viability/first_passage_diffusion.py).
Verification:
[`verify_first_passage_diffusion.py`](../verification/verify_first_passage_diffusion.py)
(7/7 checks).

## The point, in one number

For `X_t = x0 + μt + σW_t` (a reserve with expected growth), `x0=1, μ=1,
σ=1, H=1`: the expected reserve at the end of the horizon is
`E[X_1] = x0 + μH = 2` — comfortably positive. Yet the probability of ever
having touched `0` during `[0,1]` is **`0.0904` (≈9%)** — a genuine,
non-negligible chance of a boundary breach along the way, invisible to any
statement about the mean trajectory alone. (For zero drift, `μ=0`, the same
setup gives `2·Φ(-1)≈0.3173`.)

## The formula and its numerical care

Classical reflection-principle result for a diffusion with drift hitting a
lower barrier from above:

```
P(τ_0 ≤ H) = Φ((-x0-μH)/(σ√H)) + exp(-2μx0/σ²)·Φ((-x0+μH)/(σ√H))
```

The exponential factor and the second CDF term are combined via
**`scipy.special.logsumexp` in log space**, not multiplied directly: each
piece can individually fall far outside representable float range (a large
negative `μ` makes the exponential factor huge, exactly where the CDF term
becomes correspondingly tiny) while their *product* is an ordinary
probability. Computing in log space avoids an intermediate
overflow/underflow that direct multiplication would risk.

## Distinguishing two genuinely different questions

- **Finite-horizon hitting**, `diffusion_lower_hitting_probability` — "how
  likely is a breach within THIS horizon?"
- **Infinite-horizon ever-hitting**, `diffusion_ever_hitting_probability` —
  `exp(-2μx0/σ²)` for `μ>0` (certain, `=1`, for `μ≤0`) — a DIFFERENT,
  unconditional statement about the process's entire future, never to be
  read off from a finite scan (plan section 10.1's explicit warning).
  Verified `> ` the corresponding finite-horizon value, as it must be.

## Edge cases and unit invariance

`x0≤0` (already at/below the barrier) returns `1.0` immediately; `H=0`
returns `0.0` (for `x0>0`); `σ=0` reduces to the deterministic straight
line (`μ≥0`: never hits; `μ<0`: hits exactly at `t*=x0/(-μ)`). Time-unit
rescaling `t'=t/c, μ'=cμ, σ'=√c·σ, H'=H/c` (the correct joint scaling for a
Brownian motion with drift, NOT just `μ'=cμ` alone — the noise term scales
with `√dt`) leaves the hitting probability EXACTLY unchanged, verified
across `c ∈ {1e-6,...,1e6}`.

## Independent checks

An independent coarse Euler–Maruyama simulation (fixed seed) agrees with
the exact formula within a pre-declared 6σ Monte Carlo tolerance —
verified also to be a slight *under*-count (the discrete time grid only
checks at grid points, so it structurally cannot over-detect crossings
relative to the true continuous-time hitting event). A companion function,
`brownian_bridge_crossing_probability`, gives the conditional probability
that a bridge between two positive endpoints touched 0 *between* the grid
points — `exp(-2xy/(σ²Δ))` — the tool a finer discrete-time simulation
would need to avoid under-counting; not used by the hitting-probability
formula itself (which is already exact), but included as the documented
fix for exactly that under-detection.

## Scope

Constant drift and diffusion only; no reflection, jumps, or
state-dependent noise. Not a model of a bounded physical reservoir with
its own reflecting/absorbing behavior — a purely mathematical reference for
"how much does averaging over paths hide" that other modules (e.g. the
queueing pilot's stochastic side) can be checked against.
