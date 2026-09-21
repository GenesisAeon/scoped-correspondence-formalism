# Rate-dependent tracking vs. rate-induced tipping (Milestone 42)

**Status:** review package (synthetic control case, not an empirical
claim about any real system) — see `NONSTATIONARY_ROADMAP.md` package 3.
Johann-OK required before any "core" promotion.

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

Substituting `z = x - u` gives the autonomous pitchfork normal form
`dz/dt = z - z^3`: equilibria `z=0` (unstable, local derivative `+1`) and
`z=+-1` (stable, local derivative `-2`), translated back to `x=u`,
`x=u+1`, `x=u-1`. **The local derivative does not depend on `u` at all** —
there is no frozen bifurcation anywhere along any driver path for this
model. `u(t)` is bounded and S-shaped; no exponential driver is needed.

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

## Verify

```bash
PYTHONPATH=src python verification/verify_rate_dependent.py
```

JSON report: `verification/verify_rate_dependent_results.json` — all
numbers from **that** run.
