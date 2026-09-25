# The 3-node network pilot: does redistributing resources actually help against a known demand spike?

INTEGRATED_EXTENSION_ROADMAP.md Paket C5, plan section 9.4's concrete panel
— response to
`prompts/Answers/nicht_stationäre_Treiber/SCF_INTEGRATED_EXTENSION_IMPLEMENTATION_PLAN.md`.
Module:
[`validation/resource_network_pilot.py`](../src/scoped_correspondence/validation/resource_network_pilot.py),
building on [`resource_network_control.py`](resource_network_control.md).
Verification (synthetic-only, no network access needed):
[`verify_resource_network_pilot.py`](../verification/verify_resource_network_pilot.py) (7/7).

## The fixed panel (parameters declared before looking at any result)

3 nodes, `x(0)=(0.6,0.6,0.6)`, upper node capacity 2, base load 0.3/node,
extra load 0.9 at node 0 on `[1,2)` and at node 2 on `[3,4)`, horizon 6.
`0≤u_i≤0.6`, shared instantaneous supply budget 0.9, edge capacity 0.4 per
edge. Chain `0→1→2` plus an optional extra edge `2→0`. Control intervals
compared: 0.25 and 1 (both evenly divide every load-change time). QP
weights `w_i=1`, `v_e=0.1`. Three strategies: **none** (fixed
`u=(0.3,0.3,0.3)`, no flows), **fixed_routing** (same `u`, plus a constant
`f=(0.2,0.2)` along the chain), **optimized** (re-solves the QP at every
control-interval boundary using only that interval's own declared load).
A separate failure case blocks edge `1→2` on `[3,4)`, declared known to the
controller from the start.

**By design, node 0's demand spike (`0.3+0.9=1.2`) exceeds what the network
can possibly deliver** (`u_max=0.6` plus the incoming edge's capacity `0.4`
gives at most `1.0<1.2`) — a genuine, deliberately infeasible stress case,
not a bug in the panel. The interesting comparison is HOW each strategy
copes with an unavoidable shortfall, not whether any of them fully avoids
it. Per the plan's own instruction, these are declared model demonstrations, not empirical network data.

## A real bug caught before any result was reported

The first implementation reused `resource_network_control.whole_interval_safety`
directly to both classify AND propagate the state at every step. That
function's `not_certified` status and its associated (frozen) `x_end_lower`
are deliberately designed for a caller who passes a genuinely UNCERTAIN
lower bound (a negative `x_lower` there means "safety not established for
every possible true state," not "the true state is already known and
negative"). Once a node's CERTAIN, exactly-known state went negative from a
real earlier violation, this reuse silently STOPPED propagating that node's
trajectory altogether — freezing it at its already-violated value instead
of continuing to evolve under the actually-applied `u`/`f`. This understated
later trajectories' severity and mislabeled the cause as "not_certified"
rather than "already violated." Caught via an independent hand-computation
cross-check for the `none`/`fixed_routing` baselines
(`verify_resource_network_pilot.py`'s `baselines_match_hand_computation`
check disagreed with the pilot's own numbers). Fixed by adding a dedicated
`propagate_state` function (always applies the plain affine update,
regardless of sign) and classifying an already-negative CERTAIN state as
`already_violated`, a status distinct from `not_certified`. The same
reasoning also affected `solve_network_qp`'s own result classification,
fixed the same way (a solved QP's result state is always safe by
construction of its own constraint, regardless of whether `x_lower` started
negative).

## A second real bug, caught by an independent review after the first result was published

**Correction (2026-09-25, response to
[SCF_REVIEW_C0_C7_4ed0cd9.md](../prompts/Answers/nicht_stationäre_Treiber/SCF_REVIEW_C0_C7_4ed0cd9.md),
findings R6 and R7 — both real bugs, independently reproduced before
fixing):**

- **R6:** event times (`first_touch_time`, `strict_violation_time`) were
  computed by checking only interval ENDPOINTS on the CONTROL grid, snapping
  the reported time to whichever grid point happened to be closest. The SAME
  physical `none`-baseline trajectory reported `t=2.0` at `Δ=1` and `t=1.75`
  at `Δ=0.25` — two DIFFERENT numbers for one unchanged trajectory. Astra's
  own closed-form value for that exact baseline (node 0: reserve `0.6` before
  `t=1`, net slope `-0.9` on `[1,2)`) is `t*=1+0.6/0.9=5/3≈1.6666666667`.
  **Fixed** by computing the exact affine crossing time within the interval
  where it truly occurs (`x` is affine whenever `u`,`f`,`d` are held
  constant, so the crossing solves a trivial linear equation) — now `Δ=1`
  and `Δ=0.25` both report `1.6666666667` exactly, independent of the
  control interval entirely.
- **R7:** `run_network_pilot` only checked that `control_interval` evenly
  divides the horizon, so `control_interval=2.0` was silently ACCEPTED —
  sampling demand only at `t=0,2,4` and missing BOTH declared load spikes
  (`[1,2)` and `[3,4)`) completely (`min_reserve` came back `0.6`, i.e. no
  breach detected at all, for the identical `none` baseline that truly
  reaches `-0.3`). **Fixed** by requiring every declared load-change/failure
  time to also lie exactly on the control grid — a relative, scaled
  divisibility check, not an absolute tolerance — so only the two officially
  compared values (`0.25`, `1`) and other genuinely compatible intervals are
  accepted; anything else is rejected rather than silently mis-simulated.

The corrected code also revealed that the review's OWN suggested definition
("the infimum of times where `x<0` strictly coincides with the touch time
for a genuine downward crossing, but not for a pure local-minimum touch that
recovers") produces a materially more informative picture for `optimized`
at `Δ=1` than the old, coincidentally-similar-looking numbers: it now shows
a genuine TOUCH-then-RECOVER at `t≈2.0` (held flat at exactly `0` through
`[2,3)`, not a violation) followed by a FRESH strict violation at exactly
`t=3.0` — the very instant the second spike begins — rather than the old
(uncorrected) numbers that happened to also read "2.0" and "4.0" for
different, wrong reasons. `min_reserve` was unaffected by either bug (it
was already computed correctly at interval endpoints, since `x` is affine
and provably attains its extremum only at an endpoint within a held-constant
interval).

## Real results (test period = the full declared 6-time-unit horizon)

| Strategy | Δ | Failure | Min reserve | at `t=` | First touch | Strict violation | Cumulative cost | Transported |
|---|---:|:---:|---:|---:|---:|---:|---:|---:|
| none | 1 | no | **-0.300** | 2.0 | 1.6667 | 1.6667 | 1.620 | 0.0 |
| none | 0.25 | no | **-0.300** | 2.0 | 1.6667 | 1.6667 | 1.620 | 0.0 |
| fixed_routing | 1 | no | **-1.500** | 6.0 | 1.3636 | 1.3636 | 1.668 | 2.400 |
| fixed_routing | 0.25 | no | **-1.500** | 6.0 | 1.3636 | 1.3636 | 1.668 | 2.400 |
| optimized | 1 | no | **-0.900** | 4.0 | 2.0000 | 3.0000 | 1.430 | 0.590 |
| optimized | 0.25 | no | **-0.675** | 2.0 | 1.2500 | 1.2500 | 1.283 | ~0.0 |

Every reported time above is now the EXACT affine crossing time — identical
between `Δ=1` and `Δ=0.25` for the `none` and `fixed_routing` baselines,
since those strategies never re-decide their action based on the control
interval at all, so their physical trajectory literally cannot depend on
`Δ`. `optimized`'s times DO legitimately differ between `Δ=1` and `Δ=0.25`,
since that strategy actually re-decides its action at every control-interval
boundary, so a finer `Δ` genuinely changes its behavior (and, per the
myopia finding below, changes it for the worse at `Δ=0.25`).

(The declared edge failure on `[3,4)` changes only the `fixed_routing` and
`optimized` intervention costs/transported amounts marginally — the minimum
reserve, first-touch, and strict-violation times are UNCHANGED for every
strategy, since by `t=3` all three strategies are already deep in a
cascading shortfall from the first spike and the blocked edge is not on
either strategy's active recovery path at that point.)

**`fixed_routing` ends up WORSE than doing nothing at all** — after the
first spike passes, `fixed_routing`'s constant `f=(0.2,0.2)` rule keeps
draining node 0 by 0.2/time-unit indefinitely (the redistribution rule has
no way to know the emergency has passed), while `none`'s already-violated
state simply stays flat once demand returns to baseline (`u=0.3` exactly
matches `d=0.3` again). By the horizon, `fixed_routing` has reached `-1.5`
versus `none`'s `-0.3` — a genuinely counter-intuitive but mechanistically
clear result: a non-adaptive redistribution rule can actively make matters
**worse** once its original justification has expired, not merely fail to
help.

**`optimized` is myopic and pays for it.** Because the QP is re-solved
independently at every interval boundary using ONLY that interval's own
safety requirement (never a forecast of the KNOWN future spike), it has NO
incentive to preserve reserve ahead of time — during the calm `[0,1)`
window it finds that doing NOTHING (`u≈0`) already keeps the interval safe
(`x` merely needs to stay `≥0` by `t=1`, and `0.6-0.3=0.3≥0` even without
any supply), so it minimizes cost by supplying almost nothing, entering the
first spike with LESS reserve (`x≈0.3`) than the constant-policy baselines
(`x=0.6`, unchanged, since they were already injecting `u=0.3` all along).
This matches the plan's own explicit caution (section 9.2): **"a successful
first QP proves neither infinite safety nor recursive feasibility."** A
myopic, per-interval-only optimizer can do WORSE at the moment of a known
future spike than a naive constant policy, precisely because minimizing
immediate cost has no reason to build a margin for a demand event it isn't
asked to anticipate. At `Δ=1`, `optimized` still ends up better than
`fixed_routing` overall (`-0.9` vs `-1.5`) because it stops discharging once
things go wrong; at `Δ=0.25` it is worse than `none` at the minimum
(`-0.675` vs `-0.3`) specifically because of this pre-spike depletion
effect being resolved at finer time resolution.

**`first_touch_time` and `strict_violation_time` genuinely differ** for
`optimized` at `Δ=1`: it exactly touches `x=0` at `t≈2.0` (a genuine
`boundary_touch` — held flat at exactly `0` through the following interval,
not a violation) but only strictly goes negative later, at exactly `t=3.0`,
the very instant the SECOND declared spike begins — a concrete demonstration
that these two events are not interchangeable, per the plan's explicit
requirement. At the finer `Δ=0.25`, this same strategy's touch and strict
violation instead coincide (both `t=1.25`) — a genuine downward crossing
with no intervening recovery, illustrating that whether a touch recovers or
not is itself a real, control-interval-dependent property of the myopic
optimizer's behavior, not an artifact of how event times are computed.

## Scope

`fixed_routing`'s "help or hurt" verdict and `optimized`'s myopia are
properties of THESE declared parameters and strategies, not general claims
about redistribution or optimization. A receding-horizon (model-predictive)
variant of the "optimized" strategy that explicitly anticipates the KNOWN
future spike would very plausibly do better — not built here, since the
plan's own literal specification is a per-interval-only re-optimization.
The mandatory structural counter-check (an added switchable edge can only
weakly improve the QP optimum) is verified directly on this panel's own
network and states, separate from the abstract 2-node example in
`resource_network_control.md`.
