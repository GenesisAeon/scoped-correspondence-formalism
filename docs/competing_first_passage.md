# Competing first-passage targets: which boundary do you hit first, and does a lumped description agree?

INTEGRATED_EXTENSION_ROADMAP.md Paket C4 — response to
`prompts/Answers/nicht_stationäre_Treiber/SCF_INTEGRATED_EXTENSION_IMPLEMENTATION_PLAN.md`,
section 8 (transition-path-theory style committors, [S4] Metzner, Schütte &
Vanden-Eijnden 2009, *Transition Path Theory for Markov Jump Processes*,
Multiscale Model. Simul. 7(3), DOI 10.1137/070699500). Module:
[`viability/competing_first_passage.py`](../src/scoped_correspondence/viability/competing_first_passage.py).
Verification (synthetic control cases only):
[`verify_competing_first_passage.py`](../verification/verify_competing_first_passage.py) (5/5).

## The question

Many earlier viability modules ask "does state X breach a single safety
boundary?" Real systems often have TWO (or more) distinguishable outcomes —
a system might recover (`A`) or fail (`B`) — and the interesting question is
which one happens first, and with what probability, not just whether either
happens. For a continuous-time Markov chain with generator `L`, disjoint
boundary sets `A` and `B`, and interior states `D`, the **committor**
`q(x) = P(hit B before A | start at x)` and the **mean time to the boundary**
`m(x) = E[tau_A ∧ tau_B | start at x]` solve the linear boundary-value
problems

```
q|_A = 0,  q|_B = 1,  L_DD @ q_D = -L_DB @ 1
L_DD @ m_D = -1
```

— both plain linear solves, never an explicit matrix inverse, and both
require that `A ∪ B` is reached almost surely from every considered interior
state (checked via the same solve, not a separate heuristic — a singular
`L_DD` raises `ScopeViolationError` rather than returning a numerically
"close enough" garbage answer).

For a FINITE horizon `H`, making both `A` and `B` absorbing and computing
`expm(L*H)` gives `p_A(H)`, `p_B(H)`, and the residual
`p_unresolved(H) = 1 - p_A(H) - p_B(H)` — the boundary-value problem is the
`H→∞` limit of this, checked as two SEPARATE, cross-checked computations
rather than one formula assumed to specialize into the other.

## Hand-verified control case (before any code was written)

4 states ordered `(A, i, j, B)`; `i→A` rate 1, `i→j` rate 2, `j→i` rate 1,
`j→B` rate 3. Solving `3q_i=2q_j`, `4q_j=q_i+3` gives
**`(q_i, q_j) = (0.6, 0.9)`**; mean times **`(m_i, m_j) = (0.6, 0.4)`**; for
`H=1`, **`p_B = (0.467359895563, 0.829637179582)`** from `i` and `j`
respectively — all reproduced to `<1e-9` by the module.

**Rate rescaling invariance**, checked explicitly for three different
scale factors (`c=0.1, 2.0, 7.5`): multiplying every rate by `c` leaves the
committor `q` completely UNCHANGED (WHERE you end up doesn't depend on how
fast the clock runs) and divides mean hitting times by `c` exactly; rescaling
`H` to `H/c` alongside the rates leaves the finite-horizon hitting
probabilities unchanged too — a pure time-reparametrization changes only
WHEN, never WHERE.

## Bridge to Paket C2: does an exactly-lumpable chain's committor survive lumping?

Rather than re-deriving generator lumpability, this package reuses the
EXISTING, already-verified `closure.generator_lumpability.is_exact_generator_lumpability`
(`Q C = C Q_macro`) directly. A hand-constructed 6-state, 3-macro-class
generator (classes "Left"={0,1}, "Middle"={2,3}, "Right"={4,5}) is
confirmed exactly lumpable (`max|LC-CQ|~1e-16`) onto a 3-state macro chain.
Setting `A`="Left", `B`="Right" (both whole macro classes, per the C2
requirement that boundary sets be unions of whole partition blocks) and
`D`="Middle" (the 2 interior micro states):

- The two interior MICRO states 2 and 3 (same macro class) get an
  **identical committor** (`0.571428571...`) and **identical mean hitting
  time** (`1.428571...`) — as they must, since a valid macro description
  cannot distinguish them.
- Both values match the **macro chain's own committor/mean-time** computed
  directly on the 3-state reduced generator — the SAME numbers, from a
  completely different (smaller) linear system.
- The match holds **at the finite-horizon level too** (`H=1`:
  `p_B≈0.28767` from both the micro states and the macro chain), not only
  at the boundary-value-problem level — checked as two separate
  computations, since the plan explicitly asked for both.

## Scope

Only the two-boundary-set (`A` vs `B`) committor is implemented, matching
the plan's transition-path-theory framing; `finite_horizon_hitting_probabilities`
itself accepts arbitrarily many named boundary sets (useful beyond this
package), but the boundary-value-problem functions (`committor`,
`mean_hitting_time`) are specifically the two-set case. No real-data pilot
is attempted for this package — it is a purely analytic/control-case
capability, connectable to any existing generator in the repo (e.g. the
ETAS or ecological generators in `dynamics/`) as a future extension, not
built here.
