# From safety maps to bounded interventions: a two-buffer Control-Barrier-Function QP

CAPABILITY_EXPANSION_ROADMAP.md Priority 5, response to Astra's 2026-09-24
capability assessment: "Aus dem bestehenden skalaren Kontrollbarrieren-
Beispiel könnte ein Modell mit zwei gekoppelten Puffern, begrenzten
Stellgrößen und gemeinsamem Ressourcenbudget entstehen." Module:
[`viability/coupled_buffer_cbf_qp.py`](../src/scoped_correspondence/viability/coupled_buffer_cbf_qp.py).
Verification: [`verify_coupled_buffer_cbf_qp.py`](../verification/verify_coupled_buffer_cbf_qp.py)
(8/8 checks). Extends the existing scalar identity-barrier example
(`viability/control_barrier.py`, `h(x)=x`, `alpha(r)=r`) — same barrier
choice, now applied to two buffers with a constant drain each
(`x_dot_i = -drain_i + u_i`), bounded controls
(`u_min_i <= u_i <= u_max_i`), and a **shared** resource budget
(`u_1 + u_2 <= budget`).

**Correction (2026-09-24, response to
[SCF_Review_dc5d82a.md](../prompts/Answers/nicht_stationäre_Treiber/SCF_Review_dc5d82a.md),
Astra finding R4): instantaneous CBF satisfaction is not trajectory
safety.** The original version of this page called an outcome "safe"
purely on the basis of the instantaneous margin `-drain+u+x >= 0` — exactly
the same caveat already documented for the scalar M16 example this module
extends (`control_barrier.verify_forward_invariance`: "a single passing
instantaneous check does NOT by itself certify forward invariance under a
*held* ... control over time"), which this page failed to carry forward.
Astra's exact counterexample: the optimized `u=(2,0)` satisfies buffer 1's
margin exactly (`=0`), but HOLDING that control gives the closed-form
trajectory `x1(t) = 1 - t`, negative for any `t > 1`. Every result below
now separates the two questions explicitly: `cbf_condition_satisfied_now`
(renamed from `safe`) and, given an explicit `horizon`,
`sustained_safe_until_horizon` / `first_violation_time` — computed from the
EXACT closed-form trajectory under the held control (linear, no numerical
integration needed).

**Correction (2026-09-24, response to
[Astra6.txt](../prompts/Answers/nicht_stationäre_Treiber/Astra6.txt),
finding 2 — two real edge-case bugs in the code above).** (a) An
already-negative starting state must be reported unsafe at `t=0`
regardless of the held control's net rate — the previous
`held_control_violation_time` checked `net_rate >= 0` BEFORE checking
`x0 < 0`, so an already-unsafe buffer with a non-decreasing rate was
silently reported as "never violates." (b) A trajectory that reaches
EXACTLY zero AT the horizon (touching the boundary on the closed interval
`[0, horizon]`) must be reported safe, not unsafe — the previous
`sustained_safety_over_horizon` used `violation_time <= horizon`, which
conflated reaching the boundary with violating it. Astra's exact
counterexample for (b): `x0=1, drain=3, u=2, horizon=1` gives
`x(t)=1-t`, non-negative on the entire closed `[0,1]`, touching zero only
at the very last instant. Fixed by deciding safety directly from Astra's
exact reformulation for a held (linear, monotonic) control — the minimum
of a linear function over a closed interval is always at one of its two
endpoints: `min(x0, x0 + (u-drain)*horizon) >= 0`. `held_control_violation_time`
now checks `x0 < 0` first and is used only to report WHEN a genuine
violation occurs once one has already been established this way.

## The question this answers

Astra: **"Welcher zulässige Eingriff verhindert eine Grenzverletzung — und
wann reichen die verfügbaren Mittel grundsätzlich nicht aus?"** Three
variants are compared on every worked example, reporting boundary
violation, cost, AND admissibility for each — not just whether it's
instantaneously safe:

- **`no_intervention`** (`u=0`) — cheap, but not necessarily safe.
- **`fixed_rule`** (`u_i = drain_i`, replace exactly what's drained) — a
  naive policy that satisfies the CBF condition by construction (it exactly
  cancels the drain, so it is also automatically SUSTAINED-safe forever),
  but can easily be inadmissible under a shared budget.
- **`optimized_qp`** — the minimal-cost (`sum u_i²`) control satisfying
  every buffer's CBF condition NOW, its own bounds, AND the shared budget
  — with NO guarantee, by itself, of sustained safety (see below).

## Feasibility is decided analytically first, not left to the solver

Each buffer's CBF inequality (`-drain_i + u_i + x_i >= 0`) folds directly
into a per-buffer lower bound `max(u_min_i, drain_i - x_i)`. This gives an
INDEPENDENT, closed-form feasibility certificate with two genuinely
different failure modes, both surfaced explicitly rather than as a
generic solver-convergence failure:

1. **Own-bounds infeasibility** — a buffer's CBF-minimal control already
   exceeds its own `u_max`; no shared-budget amount can fix this.
2. **Budget infeasibility** — every buffer is individually fine, but the
   SUM of their CBF-minimal controls exceeds the shared budget; the
   resource itself, not any single buffer, is insufficient.

Only once the closed form confirms feasibility does `scipy.optimize
.minimize` (SLSQP) actually run — and its result is cross-checked against
the closed-form cost, raising a `ScopeViolationError` if the general
solver somehow returns something worse than the independently-derived
optimum (it never does in the worked examples, but the check exists so a
future change to the objective or constraints can't silently regress
without being caught).

## Worked example

Buffer 1 (`drain=3.0, x=1.0`) is running low and needs help; buffer 2
(`drain=2.0, x=5.0`) has comfortable margin. Both allow `u ∈ [0, 5]`.

**Budget = 3.0, horizon = 5.0:**

| Strategy | `u` | CBF now | Admissible | Sustained safe? | Cost |
|---|---|---|---|---|---:|
| No intervention | `(0, 0)` | ✗ (buffer 1 margin `-2`) | ✓ | ✗ (violates at `t≈0.33`) | 0 |
| Fixed rule | `(3, 2)` | ✓ | ✗ (`5 > 3` budget) | ✓ (forever) | 13 |
| **Optimized** | **`(2, 0)`** | ✓ | ✓ | **✗ (violates at `t=1`)** | **4** |

The optimizer finds exactly the hand-derivable *instantaneous* optimum:
buffer 1 gets its CBF-minimal `u=2`, buffer 2 needs nothing (its own margin
at `u=0` is already `+3`), total cost `4`. But HOLDING `u=(2,0)` constant,
buffer 1's exact trajectory is `x1(t) = 1 - t` — it satisfies the CBF
condition only at the instant it was computed, and drains to zero at
`t=1` exactly (matching Astra's hand derivation, `held_control_violation_time`
returns `1.0`). The "13 vs 4" cost comparison from before this correction
was therefore comparing an admissible-but-not-sustained-safe option against
an inadmissible-but-sustained-safe one — not two strategies safe over the
same horizon.

**Budget = 1.5** (infeasible): the sum of per-buffer CBF-minimal controls
(`2.0`) already exceeds the budget — reported explicitly as "sum of
per-buffer CBF-minimal controls (2) exceeds the shared budget (1.5)", not
as a silent solver failure or an unsafe best-effort answer.

## Does a bigger budget fix sustained safety? Not by itself.

Astra's second calculation: total drain here is `3+2=5`. With **budget =
5.0** (now covering total drain) and a 10-unit horizon:

| Strategy | `u` | Admissible | Sustained safe? | Cost |
|---|---|---|---|---:|
| Fixed rule | `(3, 2)` | ✓ | ✓ | 13 |
| **Optimized** | **`(2, 0)`** | ✓ | **✗ (still violates at `t=1`)** | **4** |

Even with enough TOTAL resource, the single-snapshot QP still picks the
cheapest *instantaneously* CBF-satisfying point — which need not be
sustained-safe, since it only spends what THIS INSTANT's margin requires,
not what keeps every buffer non-negative going forward. The naive fixed
rule happens to be sustained-safe here (it exactly cancels each drain,
forever), while the "smarter," cheaper QP is not. Finding the CHEAPEST
*sustained*-safe allocation is a genuinely different (trajectory-aware /
model-predictive-control-style) optimization problem that this module does
not solve — a natural, larger next step, not attempted here.

A budget below total drain makes sustained safety impossible regardless of
allocation or how often one re-optimizes: with total drain `5` and budget
`3`, `x1(t)+x2(t) <= 6 - 2t` under any admissible split, so at least one
buffer is negative for `t > 3` no matter how the budget is divided or
re-divided over time — the resource itself, not the control law, is the
limit (`sustained_safety_over_horizon` reports this directly from the
closed-form trajectory, not by trial and error).

## Scope

Two buffers only (matching Astra's explicit ask); the CBF barrier is the
same identity/linear-class-K choice as the existing scalar M16 module
(`h(x)=x`, `alpha(r)=r`) — nonlinear barriers, more than two buffers, and
model uncertainty (parameter intervals rather than exact known drains) are
not addressed here. `sustained_safety_over_horizon` checks a HELD
(constant) control's exact linear trajectory — it does not simulate a
closed-loop controller that re-optimizes as the state evolves, and does not
by itself find the cheapest sustained-safe allocation (see above). The
reported instantaneous guarantee is a model-based one (given the stated
drains and bounds, this control provably satisfies the CBF condition at
that instant); empirical reliability under a different or noisy real drain
process is a separate question this module does not address.
