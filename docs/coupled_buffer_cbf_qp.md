# From safety maps to bounded interventions: a two-buffer Control-Barrier-Function QP

CAPABILITY_EXPANSION_ROADMAP.md Priority 5, response to Astra's 2026-09-24
capability assessment: "Aus dem bestehenden skalaren Kontrollbarrieren-
Beispiel könnte ein Modell mit zwei gekoppelten Puffern, begrenzten
Stellgrößen und gemeinsamem Ressourcenbudget entstehen." Module:
[`viability/coupled_buffer_cbf_qp.py`](../src/scoped_correspondence/viability/coupled_buffer_cbf_qp.py).
Verification: [`verify_coupled_buffer_cbf_qp.py`](../verification/verify_coupled_buffer_cbf_qp.py)
(6/6 checks). Extends the existing scalar identity-barrier example
(`viability/control_barrier.py`, `h(x)=x`, `alpha(r)=r`) — same barrier
choice, now applied to two buffers with a constant drain each
(`x_dot_i = -drain_i + u_i`), bounded controls
(`u_min_i <= u_i <= u_max_i`), and a **shared** resource budget
(`u_1 + u_2 <= budget`).

## The question this answers

Astra: **"Welcher zulässige Eingriff verhindert eine Grenzverletzung — und
wann reichen die verfügbaren Mittel grundsätzlich nicht aus?"** Three
variants are compared on every worked example, reporting boundary
violation, cost, AND admissibility for each — not just whether it's safe:

- **`no_intervention`** (`u=0`) — cheap, but not necessarily safe.
- **`fixed_rule`** (`u_i = drain_i`, replace exactly what's drained) — a
  naive policy that IS safe by construction (it exactly cancels the
  drain), but can easily be inadmissible under a shared budget.
- **`optimized_qp`** — the minimal-cost (`sum u_i²`) control satisfying
  every buffer's CBF condition, its own bounds, AND the shared budget.

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

**Budget = 3.0** (feasible):

| Strategy | `u` | Safe | Admissible | Cost |
|---|---|---|---|---:|
| No intervention | `(0, 0)` | ✗ (buffer 1 margin `-2`) | ✓ | 0 |
| Fixed rule | `(3, 2)` | ✓ | ✗ (`5 > 3` budget) | 13 |
| **Optimized** | **`(2, 0)`** | ✓ | ✓ | **4** |

The optimizer finds exactly the hand-derivable optimum: buffer 1 gets its
CBF-minimal `u=2`, buffer 2 needs nothing (`u=0`, since its own margin at
`u=0` is already `+3`), total cost `4` — beating the naive fixed rule's
cost of `13` by more than 3× while ALSO being budget-admissible where the
fixed rule is not.

**Budget = 1.5** (infeasible): the sum of per-buffer CBF-minimal controls
(`2.0`) already exceeds the budget — reported explicitly as "sum of
per-buffer CBF-minimal controls (2) exceeds the shared budget (1.5)", not
as a silent solver failure or an unsafe best-effort answer.

## Scope

Two buffers only (matching Astra's explicit ask); the CBF barrier is the
same identity/linear-class-K choice as the existing scalar M16 module
(`h(x)=x`, `alpha(r)=r`) — nonlinear barriers, more than two buffers, and
model uncertainty (parameter intervals rather than exact known drains) are
not addressed here. The reported guarantee is a model-based one (given the
stated drains and bounds, this control provably satisfies the CBF
condition); empirical reliability under a different or noisy real drain
process is a separate question this module does not address.
