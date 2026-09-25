# Small resource networks: does connecting buffers with switchable flows ever make safety worse?

INTEGRATED_EXTENSION_ROADMAP.md Paket C5 — response to
`prompts/Answers/nicht_stationäre_Treiber/SCF_INTEGRATED_EXTENSION_IMPLEMENTATION_PLAN.md`,
section 9. Module:
[`viability/resource_network_control.py`](../src/scoped_correspondence/viability/resource_network_control.py).
Verification (synthetic control cases only):
[`verify_resource_network_control.py`](../verification/verify_resource_network_control.py) (6/6).
See also [`resource_network_pilot.md`](resource_network_pilot.md) for the
concrete 3-node network experiment.

**Correction (2026-09-25, response to
[SCF_REVIEW_C0_C7_4ed0cd9.md](../prompts/Answers/nicht_stationäre_Treiber/SCF_REVIEW_C0_C7_4ed0cd9.md),
finding R2 — a real bug, independently reproduced before fixing):**
`solve_network_qp`'s own result classification checked ONLY the solver-
enforced END-of-interval constraint value, never re-checking `x_lower`'s own
sign. For an already-negative `x_lower`, the solver can find a "recovery"
action that brings the state back to exactly 0 by the interval's end while
the actual affine trajectory stays STRICTLY NEGATIVE the entire time up to
that instant. Astra's exact counterexample: 1 node, no edges, `x_lower=-0.1`,
`d=0`, `Delta=1`, `u_max=1`, budget `1` — the solver finds `u≈0.1`,
`x(t)=-0.1+0.1t`, negative for every `0<=t<1`, yet the code reported
`status=solved, feasible=True, safety.status=boundary_touch` — claiming
whole-interval safety for a trajectory that was never safe at all. **Fixed**
by requiring `min(x_lower, x_end) >= 0` componentwise (both endpoints,
exploiting affineness) for any `certified_safe`/`boundary_touch` verdict; a
certain (definite, not merely uncertain) negative `x_lower` is now reported
as its own status, `already_violated` (distinct from `not_certified`, which
`whole_interval_safety` reserves for a genuinely uncertain lower bound) with
`feasible=False` — even though `status="solved"` still correctly indicates
a valid RECOVERY action was found. The hand-verified decoupled control case
is unaffected and independently re-confirmed unchanged by this fix.

**Correction (2026-09-25, response to
[SCF_REVIEW_C0_C7_4ed0cd9.md](../prompts/Answers/nicht_stationäre_Treiber/SCF_REVIEW_C0_C7_4ed0cd9.md),
finding R5 — a real bug, independently reproduced before fixing):** when
every SLSQP restart failed to converge, `solve_network_qp` checked ONLY the
single "most generous" corner (`u=u_max`, `f=edge_cap`) and reported
`infeasible` if THAT ONE POINT failed a constraint — but a feasible witness
can exist elsewhere even when the generous corner itself fails (maximal
individual flows can jointly exceed a SHARED budget; maximal edge flow can
drain a source node). Astra's exact counterexample: 3 decoupled buffers,
`x=(0.2,0.4,0.6)`, `d=(1,1,1)`, `Delta=1`, `u_max=(1,1,1)`, budget `2` — the
feasible witness `u=(0.8,0.6,0.4)` (sum `1.8`) exists, but the generous
corner (sum `3`) violates the budget, so a forced solver failure (reproduced
via `n_restarts=0`, without needing to break SLSQP itself) wrongly reported
`infeasible`. **Fixed** by solving a SEPARATE, EXACT linear feasibility
problem with the same constraints (dropping only the quadratic objective)
via `scipy.optimize.linprog`: an LP's own infeasibility verdict is an actual
mathematical proof, unlike a single corner point. `optimizer_failed` is now
reported whenever the LP finds ANY feasible point; a genuinely infeasible
problem still correctly reports `infeasible`.

## Model

State `x`, external supply `u`, outflow (demand) `d`, directed edge flows
`f`, incidence matrix `B` (each column has `-1` at its origin, `+1` at its
destination — internal flows conserve the total resource):

```
dx/dt = B @ f + u - d
```

The existing two-buffer CBF/QP case (`viability/coupled_buffer_cbf_qp.py`)
is the special case with zero edges, unchanged.

## Whole-interval safety, and three outcomes that must not be conflated

For a control interval of length `Δ` with `u`, `f`, `d` held CONSTANT, every
component of `x` is affine in time, so checking both interval endpoints
suffices. With hard bounds `x(0)≥x_lower≥0` and `d(t)≤d_upper` (allowing
genuine initial-state uncertainty), the robust sufficient condition is

```
x_lower + Δ(Bf + u - d_upper) ≥ 0
```

`whole_interval_safety` reports FOUR distinct outcomes, matching the plan's
explicit requirement to never conflate them:

- **`certified_safe`**: both endpoints of the affine lower-bound trajectory
  are `≥0` (with a strict margin).
- **`boundary_touch`**: the trajectory reaches EXACTLY `0` at the interval's
  end. This is ALLOWED — the plan's own safety sets here are closed
  (`x=0` at the interval's end is a valid, safe state) — so a first touch at
  `x≤0` is explicitly NOT the same event as a strict violation `x<0`.
- **`strict_violation`**: the end-of-interval lower bound is strictly
  negative at one or more nodes (named explicitly).
- **`not_certified`**: `x_lower` itself already has a negative component.
  This means safety was **not established for every possible true initial
  state** — it does **not** mean the true state is known to be unsafe. Only
  reached when the caller has declared real initial-state uncertainty; a
  certain (`x_lower=x`) case never produces this status from a
  physically-non-negative starting point.

## Hand-verified control case (before any code was written)

Three DECOUPLED buffers, `x=(0.2,0.4,0.6)`, `d=(1,1,1)`, `0≤u_i≤2`, a shared
rate budget of 2:

- For `Δ=1`, the minimal safe intervention is exactly `(0.8,0.6,0.4)` (sum
  `1.8`, quadratic cost `1.16`) — `boundary_touch`, not a violation.
- For `Δ=2`, the minimum becomes `(0.9,0.8,0.7)` (sum `2.4`) —
  **infeasible** under the shared budget of 2 (a longer interval needs a
  materially larger intervention, not just double).
- Holding the `Δ=1`-adequate intervention for 2 time units instead (rather
  than re-optimizing after the first interval) ends at
  `x=(-0.2,-0.4,-0.6)` — a genuine `strict_violation` for every node.

`solve_network_qp` on this same decoupled case (zero edges) is
cross-checked directly against the closed-form `minimal_decoupled_intervention`
and matches its cost to `<1e-6` — an independent-formula cross-check of the
general numerical QP solver, not merely "the optimizer converged."

## Structural counter-check (mandatory, plan section 9.4)

Adding a freely-switchable-OFF edge to a network, everything else held
fixed, can only WEAKLY IMPROVE the optimal value of the same cost function
— the old feasible set (with the new edge's flow pinned at `f=0`) is a
special case of the new, larger feasible set. Checked directly on a 2-node
example (node 0 has surplus, node 1 has a deficit only coverable by
external supply `u` alone or, when enabled, also by a `0→1` edge): the
with-edge optimum cost is `≤` the edge-disabled optimum cost. A claimed
WORSE optimum after merely adding an optional edge — with no named extra
mechanism (forced routing, delay, a non-switchable flow, a connection cost,
limited information) — is treated as a bug, per the plan's own instruction.

## `optimizer_failed` is not `infeasible`

`solve_network_qp` distinguishes a genuinely UNREACHABLE safety target
(`infeasible`: even the most generous box point — `u=u_max`, `f=edge_cap` —
fails the safety constraint or the shared supply budget) from a solver run
that failed to converge for other reasons (`optimizer_failed`) — the latter
is never silently reported as proof that no feasible point exists.

## Scope

The QP solver's robustness relies on multiple random restarts converging to
the same optimum (`scipy.optimize.minimize`, SLSQP) — a practical check
consistent with existing repo convention (`hydrology_pilot.py`'s multi-seed
fits), not a closed-form or full active-set optimality certificate for the
general (non-decoupled) network case; the decoupled case IS cross-checked
against an exact closed form. Only lossless, piecewise-constant-held flows
are modeled (plan's own first-scope restriction) — transport delay
(explicit in-transit intermediate states) is explicitly deferred to a
follow-up connecting to Paket C3.
