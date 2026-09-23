# Rate-dependent tracking vs. rate-induced tipping (Milestone 42/43)

**Status:** review package (synthetic control cases, not an empirical
claim about any real system) — see `NONSTATIONARY_ROADMAP.md` packages 3
and 4. Johann-OK required before any "core" promotion.

## Why this exists

`prompts/Answers/nicht_stationäre_Treiber/SCF_Nichtstationaere_Treiber_und_Kippen.md`
(Astra, 2026-09-21) section 5.1 points out a real gap: existing quasi-static
tools in this repo (`dynamics/panarchy_cusp.py`'s `hysteresis_sweep` /
`control_path_no_fold_crossing`, and a generic bifurcation-diagram sweep)
answer "does an equilibrium branch exist and stay linearly stable as a
parameter changes slowly?" That is a **frozen** (quasi-static) question.
It does **not** answer whether a real, actively-driven trajectory keeps
up with a *moving* stable equilibrium — a system whose frozen stability
never changes anywhere along a driver's path can still lose track of its
equilibrium and settle onto a different attractor if the driver moves
fast enough. This is called **rate-induced tipping**, distinct from
bifurcation-induced tipping (an eigenvalue crossing zero), noise-induced
tipping, or a viability-boundary violation (Ashwin, Wieczorek, Vitolo &
Cox 2012; Wieczorek, Xie & Ashwin 2023).

`dynamics/rate_dependent.py` keeps the two evaluations explicitly
separate, as requested:

- `frozen_equilibria_shifted_pitchfork(u)` — a snapshot: equilibria and
  local linear stability with the driver `u` held fixed. No time
  dependence.
- `integrate_trajectory(f, u_of_t, x0, t0, t1)` — genuine non-autonomous
  ODE integration (`scipy.integrate.solve_ivp`) with an explicit,
  externally supplied driver function `u(t)`. Not a quasi-static sweep.
- `classify_tracking(final_x, final_u, frozen_equilibria)` — compares the
  trajectory's final state to the frozen equilibria evaluated **at the
  final driver value**, to say which branch (if any) the trajectory
  settled onto.

## The canonical worked example

```
dx/dt = (x - u) - (x - u)^3,    u(t) = 1 + tanh(r*t)
```

**Correction (2026-09-21, external review by Astra):** substituting
`z = x - u(t)` for the ACTUAL time-dependent driver gives
`dz/dt = z - z^3 - u_dot(t)`, not the bare autonomous pitchfork form —
the earlier text here dropped the `-u_dot(t)` term, and that term is
exactly the rate-dependent tipping mechanism: it is what can push the
trajectory off the frozen branch it would otherwise track. The
implementation was never affected by this — `integrate_trajectory`
integrates the original, correct `x`-equation directly with the real
`u(t)`; only this explanatory shorthand was wrong.

The `z = x - u` substitution IS exactly `dz/dt = z - z^3` only for the
**frozen** analysis (`u` held constant, i.e. `u_dot = 0`), which is what
`frozen_equilibria_shifted_pitchfork` computes: equilibria `z=0`
(unstable, local derivative `+1`) and `z=+-1` (stable, local derivative
`-2`), translated back to `x=u`, `x=u+1`, `x=u-1`. **The local derivative
does not depend on `u` at all** — there is no frozen bifurcation anywhere
along any driver path for this model. `u(t)` is bounded and S-shaped; no
exponential driver is needed. The *actual* trajectory's tracking/switching
behavior is governed by the dropped `-u_dot(t)` term against this frozen
background, exactly as the rate-dependent-tipping literature (Ashwin et
al. 2012; Wieczorek et al. 2023) describes.

The system starts near the upper branch (`x-u = +1`) well before the
driver begins moving and is integrated well after it has finished:

| Rate `r` | Final relative state `x-u` | Tracked branch | Switched? |
|---|---:|---|---|
| 0.1 (slow) | +1.0000000000 | upper | **No** |
| 2.0 (fast) | -1.0000000000 | lower | **Yes** |

Both results reproduce `SCF_Nichtstationaere_Treiber_und_Kippen.md`
section 5.1 exactly, including the reported integration-refinement
differences (`1.487e-10` at r=0.1, `1.364e-08` at r=2.0 — the maximum
difference between a coarse and a much finer integration tolerance,
confirming the trajectory itself is numerically converged, not just
self-consistent).

**A rate sweep** (`r` from 0.05 to 5) shows tracking fails only above a
critical rate somewhere between 0.5 and 1.0 for this model — not for
every `r`, and not a coin flip: once switching starts, it persists for
all faster rates tested. This is a genuine RATE effect, matching the
mechanism's name.

## Scope

- This is a single, textbook-canonical 1D example, chosen because its
  frozen equilibria and their stability are exactly solvable by hand
  (translation invariance of the pitchfork normal form) — not a claim
  that any real driver (climate forcing, epidemic reproduction number,
  etc.) follows this specific model or exhibits rate-induced tipping.
- `classify_tracking` raises `ScopeViolationError` if the trajectory's
  final state isn't close to any supplied stable equilibrium — it never
  silently guesses a branch.
- A quasi-static sweep (`panarchy_cusp.hysteresis_sweep`) and this
  module's frozen-equilibria evaluator answer a different question than
  `integrate_trajectory` does; NONSTATIONARY_ROADMAP.md package 3 exists
  precisely because conflating them would miss rate-induced tipping
  entirely.

## Package 4 — a local diagnostic, and the mirror-image buffer case (2026-09-21)

Astra's section 5.2 proposes a LOCAL diagnostic for whether a moving
equilibrium is being tracked, without claiming a universal threshold:

```
chi(t) = |D_u x*(u) * u_dot| / (kappa * d_boundary)
```

`local_chi_diagnostic()` implements this directly. For the canonical
worked example above, the stable-branch sensitivity `D_u x* = 1` and the
distance between stable and unstable branches `|x_stable - x_unstable| =
1` are both EXACT CONSTANTS independent of `u` — so `chi(t) = u_dot(t)/2`,
and its maximum is `chi_max = r/2` in closed form (since `u_dot(t) =
r*sech^2(r*t)` peaks at `t=0` with value `r`).

`chi_diagnostic_for_cubic_example(r)` computes this `chi_max` purely from
the driver's closed form and correlates it against the already-verified
actual outcome:

| `r` | `chi_max = r/2` | Switched? |
|---:|---:|---|
| 0.05 | 0.025 | No |
| 0.20 | 0.100 | No |
| 0.50 | 0.250 | No |
| **1.00** | **0.500** | **Yes** |
| 1.50 | 0.750 | Yes |
| 2.00 | 1.000 | Yes |
| 5.00 | 2.500 | Yes |

**Correction (2026-09-21, external review by Astra):** the table above
only brackets the transition loosely between `r=0.5` (chi=0.25, No) and
`r=1.0` (chi=0.5, Yes) — any threshold in that whole interval would fit
the coarse grid equally well, so "`chi_max >= 0.5` predicts switching
exactly" was an overclaim about precision, not a wrong direction. An
independently-verified finer sweep narrows it further:

| `r` | `chi_max = r/2` | Switched? |
|---:|---:|---|
| 0.6 | 0.30 | No |
| 0.7 | 0.35 | No |
| **0.8** | **0.40** | **Yes** |
| 0.9 | 0.45 | Yes |

The actual critical rate for this model sits between `r=0.7` and `r=0.8`
(critical `chi_max` between 0.35 and 0.40), not at 0.5. `chi` remains a
useful, correctly-directioned LOCAL diagnostic — larger `chi` reliably
means closer to switching — but identifying its precise critical value
would need continuation/interval search near the transition, not a
handful of grid points. Not a claim that 0.5 (or any other single number)
is a universal critical `chi` value for this or any other model.

### A mirror-image buffer case (`viability/rate_dependent_buffer.py`, Milestone 43)

`chi`'s denominator (`kappa * d_boundary`) assumes the frozen system
stays stable and on the SAFE side of its boundary throughout — it is not
meaningful once the frozen path itself crosses the boundary. Astra's
package 4 also asks for a buffer/viability control case ("same final
load values, different tempo or different reserve"), and the natural one
— a scalar buffer briefly overloaded by a transient demand spike that
returns to the same safe baseline load afterward — is exactly this
excluded case: the frozen state AT THE PEAK of the spike is deliberately
unsafe (`has_safe_transfer` correctly says so), while both the baseline
before and after the spike are frozen-safe.

Model: `z_dot = -r(z-z_eq) + U - W(t)`, the same scalar buffer as
`viability.core.has_safe_transfer`, with `W(t) = W0 + spike_height *
exp(-(t/tau)^2)` — a Gaussian spike of width `tau` above baseline `W0`,
returning to `W0`. With `r=1`, `z_eq=0`, `U=0`, `W0=0`, `spike_height=1`,
`b=-0.5`:

| Spike width `tau` (tempo) | Trajectory minimum `z_min` | Breaches `b=-0.5`? |
|---:|---:|---|
| 0.05 (fast) | -0.081 | No |
| 0.20 | -0.265 | No |
| **0.50** | **-0.495** | **No** (barely) |
| **1.00** | **-0.695** | **Yes** |
| 2.00 | -0.858 | Yes |
| 5.00 (slow) | -0.965 | Yes |

**This is the MIRROR IMAGE of the rate-induced tipping result above —
under FIXED PEAK HEIGHT:** there, faster driving was MORE dangerous (the
trajectory couldn't keep up with a moving multistable equilibrium and
tipped to the wrong attractor). Here, with the spike's peak height held
fixed while its width `tau` varies, faster (shorter) spikes are LESS
dangerous — the buffer's own relaxation acts as a low-pass filter and
attenuates brief disturbances, never letting the state get close to the
instantaneous frozen worst case; only spikes long enough relative to
`1/r` let the buffer catch up toward that worst case. Checking only the
frozen peak load ("this load, sustained, would be unsafe") is needlessly
conservative for a genuinely brief spike; checking only the frozen
baseline/endpoint loads misses the risk from a sufficiently sustained one.

**Correction (2026-09-21, external review by Astra): this conclusion
depends entirely on what is held fixed, and reverses under a different,
equally natural choice.** Holding the spike's peak height fixed while
`tau` shrinks also means the total EXTRA load delivered (`height *
sqrt(pi) * tau`, the Gaussian's integral) shrinks too — shorter pulses in
that table are not just faster, they are also *smaller* overall. Holding
the TOTAL extra load fixed instead (`equal_total_load_height(total_load,
tau) = total_load / (sqrt(pi) * tau)`, so shorter pulses must be taller
to deliver the same total) gives the opposite ranking, independently
verified:

| Spike width `tau` | Height (equal total load = 1) | `z_min` |
|---:|---:|---:|
| 0.05 (fast) | 11.28 | **-0.912** |
| 0.20 | 2.82 | -0.747 |
| 0.50 | 1.13 | -0.558 |
| 1.00 | 0.56 | -0.392 |
| 2.00 | 0.28 | -0.242 |
| 5.00 (slow) | 0.11 | **-0.109** |

Under equal total load, **shorter pulses are MORE dangerous** — a
short, concentrated pulse packs the same total load into less time,
overwhelming the buffer's relaxation before it can absorb it, while a
long, gentle pulse delivering the same total load lets the buffer keep
up. **Neither table is wrong; they answer different questions** (a
peak-limited disturbance vs. a total-energy-limited one), and a single
"faster is safer/more dangerous" claim, without saying which quantity is
held fixed, is not a well-posed statement for this system. A full
characterization would need a response surface over amplitude AND
duration jointly, not a single 1D sweep in either direction alone.

The **reserve** dimension, at fixed `tau=1.0` (`z_min=-0.695`): `b=-0.3`
and `b=-0.5` breach, `b=-0.7` and `b=-0.9` do not — a sharp transition
exactly at the trajectory's own minimum, as expected.

**Scope:** a single scalar linear buffer, one Gaussian spike shape; no
claim about any real resource, inventory, or safety system without its
own separate model. `local_chi_diagnostic` is intentionally NOT applied
here (its ScopeViolationError on a non-positive `distance_to_boundary`
guards exactly this case) since the frozen peak is unsafe by
construction, outside the diagnostic's stated scope.

**Structural bridge B7 (2026-09-21):** this buffer's trajectory is exactly
a convolution with its own impulse response `e^{-rt}` — the same linear
structure as `dynamics.energy_balance`'s two-layer model (a 2-exponential
impulse response there, instead of this buffer's single exponential). See
[docs/structural_relations.md](structural_relations.md#b7--linear-impulse-response-systems-energy-balance--rate-dependent-buffer).

## Package 6 — a genuine response surface, not a single 1-D sweep (2026-09-23)

Directly closes the open item above ("a full characterization would need
a response surface over amplitude AND duration jointly") and Astra's
package-6 request (`SCF_Review_3e8dce3.md`): "Schnitte bei gleicher
Spitzenlast und bei gleicher integrierter Last [...] Ergebniszustände
sollten mindestens Tracking, Wechsel, noch nicht entschieden, außerhalb
des Scopes und Integrationsfehler unterscheiden."

`viability.multidim_tipping_maps` composes the buffer and cubic modules
above UNCHANGED into genuine 2-D grids, classified into five outcome
states instead of a bare boolean: `tracking`, `switched`, `unresolved`
(numerically too close to the boundary to trust, given the trajectory's
own coarse/fine refinement error), `out_of_scope` (the frozen baseline
itself is not safe — not a valid "brief spike over a safe baseline"
scenario), and `integration_error` (the underlying solver itself failed).

### The two amplitude conventions, now on the SAME grid

`buffer_response_surface(..., amplitude_mode="peak_height" | "total_load")`
reproduces both of the 1-D tables above exactly as single-amplitude-column
slices of one function, confirming the new machinery is not silently
different from the already-verified 1-D case — then genuinely extends to
multiple amplitude values per call, which the 1-D sweeps never did.

### The reserve axis is (almost) free

**Hand-verified simplification:** the boundary `b` never appears in
`run_buffer_spike_trajectory`'s ODE — only in the after-the-fact
`z_min < b` check. So the critical reserve is EXACTLY the trajectory's
own minimum, `critical_b = z_min`, with no re-integration and no
root-finding needed per `b` value: `buffer_reserve_frontier` computes ONE
trajectory and classifies any number of `b` values from it directly. This
reproduces the doc's "sharp transition exactly at the trajectory's own
minimum" claim as an exact identity, not an observation:
`critical_b = -0.6947528523...` for `tau=1.0`, matching `z_min` to full
float precision.

**A genuine `out_of_scope` case:** setting `b=0.1` (above the frozen-safe
baseline threshold `b<=0` for these parameters) is correctly classified
`out_of_scope`, not silently forced into `tracking` or `switched` — the
scenario itself ("a brief spike over a safe baseline") does not apply
when even the baseline is unsafe. `b=0.0`, exactly at the threshold,
remains `tracking` (the frozen-safety condition uses `>=`, not `>`).

### The cubic model's reserve axis: a real null result, then a real effect

`tracking_response_surface(rs, x0_offsets)` adds `x0_offset` (how far onto
the stable branch the trajectory starts, i.e. its distance from the
unstable branch / decision boundary at `t0`) as a genuine second, reserve-like
axis alongside the rate `r`.

**At the module's own default `margin=10`** (the long pre-driving
relaxation window used throughout the canonical worked example above),
this axis is **empirically inert** — an honest null result, checked, not
assumed: at `r=0.8` (just past the critical rate), EVERY `x0_offset` from
0.05 to 2.0 switches identically. The mechanism: with `t0=-margin/r`, the
system has ~10 relaxation times to forget its initial condition and
settle onto the correct quasi-static branch trajectory before the driver
`u(t)=1+tanh(rt)` even begins moving substantially — so the starting
offset carries no memory into the decision.

**At a shorter `margin=3`**, real dependence appears near the critical
rate (`r=0.75`):

| `x0_offset` | Outcome | Final relative state `x-u` |
|---:|---|---:|
| 0.05 | switched | −1.000002 |
| 0.20 | switched | −1.000000 |
| 0.40 | switched | −0.999847 |
| **0.60** | **unresolved** | *(not settled by `t1`)* |
| 0.80 | tracking | +0.999666 |
| 1.00 | tracking | +0.999794 |
| 2.00 | tracking | +0.999874 |

The `unresolved` cell at `x0_offset=0.6` is a REAL, non-manufactured case
— `classify_tracking` genuinely raises because the trajectory has not
settled within its `1e-3` tolerance by `t1` (final `x-u≈0.978`, just
outside tolerance of the `+1` branch), correctly distinguished from a
genuine solver failure by this module (both raise the same exception type
from the reused, unmodified `dynamics.rate_dependent` module; this module
tells them apart by message content since the underlying module was not
edited to expose a structured failure reason).

**Reading:** reserve (how far onto a branch a trajectory starts) DOES
matter for rate-induced tipping — but only when the pre-driving
relaxation window is short enough that the system has not already
forgotten its initial condition. A sufficiently long "settling-in" period
before the real driving begins erases the effect entirely. Neither
finding is more "correct" than the other; they characterize different
regimes of the SAME model, exactly the kind of joint dependency a single
1-D sweep in either `r` or `x0_offset` alone would have missed.

### Scope

- Numerical maps are empirically determined boundaries from finite grids
  of independently-integrated trajectories — not a proven global
  threshold geometry. Wieczorek, Xie & Ashwin (2023)'s edge states and
  connecting orbits (referenced throughout this document's sources) would
  be the appropriate mathematical follow-up for a GLOBAL characterization
  of the tipping/tracking boundary; not attempted here.
- `integration_error` is defensively coded (a try/except around every
  grid cell) but not empirically triggered by any grid in this package —
  a genuine `solve_ivp` failure was only reproducible via a
  pathologically slow (near-hanging) parameter combination, deliberately
  not adopted as a test case.
- Astra's proposed further mathematical extension — time-dependent
  impulse-response kernels `G(t,s)=exp(-∫_s^t r(v)dv)` connecting buffer,
  energy-balance, timescale and tracking-error dynamics into one
  framework — remains a documented derivation/expansion proposal, not
  implemented or empirically validated here.

## Verify

```bash
PYTHONPATH=src python verification/verify_rate_dependent.py
PYTHONPATH=src python verification/verify_rate_viability_control_cases.py
PYTHONPATH=src python verification/verify_multidim_tipping_maps.py
```

JSON reports: `verification/verify_rate_dependent_results.json`,
`verification/verify_rate_viability_control_cases_results.json`, and
`verification/verify_multidim_tipping_maps_results.json` — all numbers
from **those** runs.
