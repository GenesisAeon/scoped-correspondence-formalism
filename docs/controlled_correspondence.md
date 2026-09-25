# Controlled Markov correspondence: does a macro action label actually summarize a micro action?

INTEGRATED_EXTENSION_ROADMAP.md Paket C2 — response to
`prompts/Answers/nicht_stationäre_Treiber/SCF_INTEGRATED_EXTENSION_IMPLEMENTATION_PLAN.md`,
section 6. Module:
[`correspondence/controlled_markov.py`](../src/scoped_correspondence/correspondence/controlled_markov.py).
Verification (synthetic control cases only):
[`verify_controlled_correspondence.py`](../verification/verify_controlled_correspondence.py) (5/5).

## The question

Existing `correspondence/` machinery checks whether a state map and a time
map preserve dynamics for an UNCONTROLLED system. Real interventions are
declared per ACTION: a micro-level policy might distinguish "raise the
sluice gate 10cm" from "raise it 20cm," while the macro model only knows
"intervene" vs. "don't." This package checks exactly when that
simplification is exact — not assumed — for a finite controlled Markov
chain: a row-stochastic micro kernel `P^a` per micro action `a`, a
row-stochastic macro kernel `Q^b` per macro action `b`, a deterministic
partition `C` of micro states into macro classes, and an action map `omega`
collapsing micro actions to macro actions. Exact correspondence means

```
P^a C = C Q^{omega(a)}          for every declared micro action a
```

i.e. classical exact/strong lumpability, checked SEPARATELY for every
declared action (plan section 6: "no averaging that hides one failing
action").

## Hand-verified control case (before any code was written)

4 micro states, 2 classes `{0,1}` and `{2,3}`, `C=[[1,0],[1,0],[0,1],[0,1]]`.
Two micro kernels with deliberately HETEROGENEOUS within-class rows (to
demonstrate exactness doesn't require identical rows, only identical
aggregated block sums):

```
P_passive =                          P_intervention =
  0.50 0.20 0.20 0.10                  0.50 0.30 0.10 0.10
  0.10 0.60 0.05 0.25                  0.20 0.60 0.15 0.05
  0.30 0.10 0.40 0.20                  0.05 0.05 0.70 0.20
  0.15 0.25 0.30 0.30                  0.02 0.08 0.30 0.60
```

Both give an EXACT correspondence (max abs deviation `~1e-16`, `P@C - C@Q`):

```
Q_passive      = [[0.7, 0.3], [0.4, 0.6]]
Q_intervention = [[0.8, 0.2], [0.1, 0.9]]
```

matching the plan's `(a,b)=(0.7,0.4)` (passive) and `(a,b)=(0.8,0.1)`
(intervention) exactly, independently for any starting state or state
sequence.

## Negative case: exactness is fragile, and the module says exactly how it fails

Replacing the intervention's first two rows with `[0.9,0,0.1,0]` and
`[0,0.7,0,0.3]` (both still valid stochastic rows) breaks exactness: state 0
now reaches class 1 with probability 0.1, state 1 with probability 0.3 — no
single macro row can represent both micro states in class 0 any more.
`check_lumpability` reports this as a defect of `0.2` (the spread between
0.1 and 0.3) attributed to macro class 0's column-1 entry, with the exact
pair of responsible micro states. `best_minimax_macro_row` reports the best
SINGLE replacement value `0.2` (the midpoint) with maximum remaining error
`0.1` — matching the plan's stated `minimax value 0.2, max row-TV-error 0.1`
exactly. Crucially, `check_controlled_correspondence` reports this only
against the `intervention` action — `passive`, unaffected, is still reported
as exact, demonstrating the "no averaging across actions" requirement in
practice, not merely as a design intent.

## Events, costs, and admissibility (plan section 6, additional checks)

- **`is_union_of_classes`**: a "macro event" (e.g. "the system is in an
  unsafe macro state") is only well-defined if it corresponds to a UNION of
  WHOLE partition blocks. `{0,1}` (class 0) and `{2,3}` (class 1) are valid;
  `{0,2}` — cutting across both classes — is not, and the function says so
  rather than silently returning a value for an ill-posed micro event.
- **`check_cost_consistency`**: checks `c_X(x,a) = c_Y(C(x), omega(a))` for
  every declared `(micro_state, micro_action)` cost entry, reporting the
  exact mismatched entries and their error magnitude — and treats a
  genuinely MISSING macro counterpart as an infinite-error violation, never
  as a silently-skipped entry (a real cost value that happens to have no
  macro counterpart at all is a worse problem than one that merely
  disagrees, and must not be reported as "no violations found").

## Scope

Only exact (not approximate) controlled lumpability is checked here — this
package reports the exact defect and the exact minimax single-row
replacement when correspondence fails, but does not attempt an approximate
aggregation bound analogous to `closure/`'s memory-projection error metrics.
Admissibility-constraint consistency under action refinement (which micro
actions are available at a micro state vs. which macro actions are available
at its macro class) is not separately implemented — the cost-consistency and
event-union checks above are the concrete, worked pieces of plan section 6
actually built here.
