# Distributed delays: does the SHAPE of a delay (not just its mean) matter for a downstream buffer?

INTEGRATED_EXTENSION_ROADMAP.md Paket C3 — response to
`prompts/Answers/nicht_stationäre_Treiber/SCF_INTEGRATED_EXTENSION_IMPLEMENTATION_PLAN.md`,
section 7. Modules:
[`dynamics/phase_type_delays.py`](../src/scoped_correspondence/dynamics/phase_type_delays.py)
(Erlang/phase-type chains, exact propagation),
[`validation/distributed_delay_pilot.py`](../src/scoped_correspondence/validation/distributed_delay_pilot.py)
(the plan's fixed pre-declared downstream-buffer experiment). Verification
(synthetic control cases only):
[`verify_phase_type_delays.py`](../verification/verify_phase_type_delays.py) (7/7),
[`verify_distributed_delay_pilot.py`](../verification/verify_distributed_delay_pilot.py) (7/7).

**Correction (2026-09-25, response to
[SCF_REVIEW_C0_C7_4ed0cd9.md](../prompts/Answers/nicht_stationäre_Treiber/SCF_REVIEW_C0_C7_4ed0cd9.md),
finding R4 — a real bug, independently reproduced before fixing, shared with
`docs/competing_first_passage.md`):** `validate_phase_type` relied only on
`np.linalg.solve(-T, ...)` succeeding to certify absorption. A NONTRIVIAL
closed 2-phase class (phases only cycling at rates 0.3/0.4, zero exit rate
from either) PASSED validation with a finite (`~3.15e16`, meaningless) mean
dwell time instead of raising. **Fixed** by an explicit graph-reachability
check (does every phase have a positive-rate path to some phase with a
positive exit rate?) performed BEFORE any linear solve — a structural,
floating-point-independent condition. All phases are required to reach an
exit (not only those reachable under the given `alpha`), since a `PhaseType`
object can be reused later with a different `alpha`.

**Correction (2026-09-25, response to
[SCF_REVIEW_C0_C7_4ed0cd9.md](../prompts/Answers/nicht_stationäre_Treiber/SCF_REVIEW_C0_C7_4ed0cd9.md),
finding R1 — a real bug, independently reproduced before fixing):** the
original event/extremum search scanned a dense (≥500-point) fixed grid per
segment, then refined a found bracket exactly with `brentq` — but the SEARCH
itself was not exhaustive: a dip narrower than the local grid spacing was
invisible to it. Astra's exact closed-form construction (`n=1`,
`R0=0.19281716266490573`) makes `R` dip to exactly `-1e-7` at
`t*≈1.0179568433377357` and recover — narrower than the grid could resolve —
so the old code reported `first_passage_time=None` while *simultaneously*
reporting a negative `R_min_value` at that very time, an internal
self-contradiction. **Fixed** by replacing the grid scan with an exact,
grid-free construction: for an Erlang(n) chain under constant input, the
output has the closed form `y(τ)=u+e^{-kτ}P(τ)` for a real polynomial `P` of
degree `≤n-1` computed directly from the current stage occupancies (cross-
checked to machine precision against the module's own exact propagation);
`y`'s stationary points are exactly the real roots of `P'-kP`
(`numpy.poly1d.roots`, not a grid), which partition each segment into pieces
where `R'` is provably monotone, in turn bracketing `R`'s own stationary
points exactly, in turn bracketing any `R=0` crossing exactly — no dip, no
matter how narrow, can be missed between two exactly-located breakpoints.
The fix recovers Astra's exact crossing time (`t*=1.017249819880103` vs. the
independently stated `1.0172498198798665`) and the exact `n=1` output peak
(`t=0.2`, height `0.9063462346100907`, matching Astra's independently stated
`0.90634623461` — the old `minimize_scalar`-based peak search had also been
only approximate: `t≈0.20000342107`, height `≈0.90634313394`). The **already-
published `n∈{1,2,4,8}` results below were essentially unaffected** — every
value changes only in the 6th–7th significant digit, since none of those
four particular cases sits as close to a hidden razor-thin dip as Astra's
adversarially constructed counterexample.

## Why a single lag isn't enough

A fixed time lag or a single exponential relaxation are both special cases of
a much richer family: an Erlang(n) chain of `n` sequential exponential
stages with the SAME total mean dwell time `tau` (rate `lambda=n/tau` per
stage) interpolates between a memoryless exponential delay (`n=1`) and an
increasingly sharp, clock-like fixed lag (`n→∞`) — same mean, very different
SHAPE. More generally, any phase-type distribution (row vector `alpha`,
transient subgenerator `T`, exit rates `r=-T@1`) gives

```
dz/dt = z@T + u(t)*alpha        y(t) = z@r
h(t) = alpha @ expm(T*t) @ r    E[dwell time] = alpha @ (-T)^{-1} @ 1
```

propagated EXACTLY under piecewise-constant input via the standard
augmented-matrix-exponential trick (no ODE-solver tolerance to tune, exact
even when `T` is singular).

## Hand-verified control values (before any code was written)

Both Erlang(1) (exponential, rate 1) and Erlang(2) (rate 2/stage) have mean
dwell time 1. `F_1(t)=1-e^{-t}`, `F_2(t)=1-e^{-2t}(1+2t)`:

| `t` | `F_1(t)` | `F_2(t)` |
|---:|---:|---:|
| 0.25 | 0.221199216929 | 0.090204010431 |
| 1 | 0.632120558829 | 0.593994150290 |
| 2 | 0.864664716763 | 0.908421805556 |

**The CDF ranking reverses between `t=0.25` and `t=2`**: Erlang(1) has
resolved more mass early (`0.221>0.090`), but Erlang(2) overtakes it by
`t=2` (`0.908>0.865`) — a smaller-variance delay is not uniformly "faster"
at every horizon, only in some aggregate/asymptotic sense. The Erlang(2)
impulse response `h_2(t)=4t*e^{-2t}` peaks exactly at `t=0.5` with height
`2/e=0.735758882343`.

## The fixed, pre-declared experiment (plan section 7)

Parameters fixed BEFORE looking at any result (plan's own requirement:
"seine Parameter werden aber nicht nach einer gewünschten Rangfolge
ausgewählt"): `n∈{1,2,4,8}`, `tau=1`, rectangular input pulse `u(t)=5` on
`[0,0.2)` then `0` (total pulse mass `5*0.2=1.0`), horizon `5`. The delayed
output `y(t)` feeds a downstream reserve `R(0)=0.1`, `dR/dt=0.4-y(t)`.
Event of interest: the first time `R(t)≤0` — **no reflection or silent
clipping at zero; the uninhibited trajectory stays visible for diagnosis.**

### A real bug caught before any result was reported

The first implementation checked ONLY the two endpoints of each
piecewise-constant-input segment for a sign change in `R`, which MISSES a
dip-and-recovery that happens strictly inside a segment. Since `R` here
first drops (while the delayed pulse output temporarily exceeds the 0.4
inflow) and later recovers (once the pulse's mass has mostly exited and
inflow dominates again), this bug reported `first_passage_time=None` for
all four `n` — a false negative. Fixed by densely scanning each segment's
closed-form `R(s)` for the first sign change and refining with `brentq`,
rather than trusting the segment endpoints alone; cross-checked afterward
by directly evaluating `R` at the reported crossing time (`|R|<1e-8`).

### Results

| `n` | First passage `R≤0` | `R` minimum | at `t=` | Output peak | at `t=` | Remaining mass at horizon |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | **0.406** | -0.0928 | 1.018 | 0.906 | 0.200 | 0.00746 |
| 2 | **0.845** | -0.0720 | 1.372 | 0.731 | 0.607 | 0.00060 |
| 4 | **1.037** | -0.1088 | 1.544 | 0.888 | 0.854 | 4.6e-6 |
| 8 | **1.093** | -0.1694 | 1.562 | 1.174 | 0.979 | 3.5e-10 |

**A genuine breach (`R≤0`) occurs for every `n` in this family** — the
downstream reserve is not automatically safe just because the average
inflow (`0.4/time`) exceeds the pulse's total mass rate. The breach time
increases with `n` (a more sharply-timed, later-peaking delay postpones
the first breach), but **the SEVERITY of the breach (how negative `R` gets)
and the output's peak height do NOT rank `n` the same way**: going from
`n=1` to `n=4`, the output peak actually SHRINKS (`0.906→0.888`) while the
buffer's minimum gets WORSE (`-0.0928→-0.1088`) — exactly the plan's own
caveat that a peak change and a buffer-minimum change need not move in the
same direction. Mass balance (remaining mass in the delay stages at the
horizon, plus the mass that has exited as output, integrated
independently) equals the total pulse mass `1.0` to within numerical
quadrature precision for every `n`, confirming no mass is created or lost
by the exact propagation.

## Scope

Only Erlang chains (a specific, one-parameter-family phase-type structure)
are exercised in the fixed experiment; the general phase-type machinery
(`PhaseType`, arbitrary `alpha`/`T`) is implemented and control-case verified
but not exercised on a non-Erlang example here. The buffer model is linear
and unconstrained (matching the plan's explicit "no clipping" requirement);
a physically constrained (non-negative reserve) variant is a separate,
harder problem not attempted. The experiment is not extended with additional
pre-declared cases beyond the one the plan specifies (though the plan
explicitly permits that as a future addition).
