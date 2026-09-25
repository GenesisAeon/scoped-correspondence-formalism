# The value of a costly observation: when is it worth paying to know?

INTEGRATED_EXTENSION_ROADMAP.md Paket C6 — response to
`prompts/Answers/nicht_stationäre_Treiber/SCF_INTEGRATED_EXTENSION_IMPLEMENTATION_PLAN.md`,
section 10. Module:
[`validation/sequential_information_pilot.py`](../src/scoped_correspondence/validation/sequential_information_pilot.py)
(kept as one module rather than splitting out a separate
`observation/decision_value.py` core, per the plan's own guidance — "only
when a real second user exists"). Verification (synthetic control cases
only): [`verify_sequential_information_pilot.py`](../verification/verify_sequential_information_pilot.py) (6/6).

## The model

A binary hidden state flips with probability `p` per step; the belief
`b=P(X_t=1)` updates deterministically as `T(b)=p+(1-2p)*b` — a contraction
toward `0.5` at rate `|1-2p|` per step. At each of `H` decisions, the agent
either decides using its current belief alone (reward `max(b,1-b)`, its
probability of guessing right) or pays a fixed cost `c` for an immediate
PERFECT observation, then decides with certainty (reward `1-c`). The optimal
value function is the plain backward Bellman recursion

```
V_0(b) = 0
V_h(b) = max( max(b,1-b) + V_{h-1}(T(b)),   (1-c) + b*V_{h-1}(T(1)) + (1-b)*V_{h-1}(T(0)) )
```

— exact enumeration over a finite decision tree, no discretized POMDP solver
and no LLM dependency, per the plan's own first-scope restriction.

## Hand-verified control case (before any code was written)

`p=0.1`, `c=0.2`, 2 decisions from `b=0.5`. Never measuring: `1.0`. Always
measuring: `2*(1-0.2)=1.6`. Measuring once, then exploiting the resulting
near-certainty for the second decision:
`(1-0.2)+max(T(1),1-T(1))=1.7`. **`V_2(0.5)` is exactly `1.7`** — neither
naive extreme is optimal; measuring exactly once is.

**Message aging**: after a perfect observation of `X_0` with no further
information, the optimal hit rate for `X_d` is `1/2+1/2*|1-2p|^d`. For
`p=0.1`: `d=1→0.9`, `d=2→0.82`, `d=10→0.5536870912` — information decays
geometrically toward the uninformative `0.5` baseline, never abruptly.

## The "free option" property (mandatory check, verified over 2250 combinations)

Since "don't measure" is always one of the two branches in the recursion,
the OPTIONAL, priced observation can never make the optimum WORSE than a
policy that isn't even allowed to measure at all — checked over every
combination of `h∈{0..4}`, `b∈{0,0.2,0.5,0.7,1}`, `p∈{0,0.1,0.3,0.5,0.9}`,
`c∈{0,0.05,0.2,0.5,1,2}` (2250 trials): `bellman_value(...) >= value_never_measure(...)`
always holds, even for a very expensive `c=2` observation (in the worst
case, the optimal policy just never chooses to measure, matching the
never-measure baseline exactly rather than doing worse).

## Representative parameter panel (horizon 5, `b0=0.5`)

The reported `action` field is the OPTIMAL policy's **first** decision only
— NOT a claim about every subsequent decision, which can differ once the
belief has moved. Two structural findings emerge clearly from the panel
(`p∈{0,0.1,0.5,0.9}`, `c∈{0,0.1,0.2,0.5,0.6}`):

- **`p=0` (a state that never flips): "measure once, then coast."** The
  first decision is always "measure" (`action="measure"` even at the
  highest tested cost `c=0.6`), but the VALUE (`4.4` at `c=0.6`, horizon 5)
  is exactly `(1-c) + (H-1)*1 = 0.4+4 = 4.4` — pay once for certainty, then
  every remaining decision is free and always correct, since the state
  never changes again. The recursion never needs to measure a SECOND time
  here (confirmed by inspecting `V_{h-1}(1)` and `V_{h-1}(0)`, both equal to
  the "always correct, zero further cost" value).
- **`p=0.5` (an i.i.d. coin flip every step, no persistence at all):
  measuring is worthless for FUTURE decisions** (`T(b)=0.5` regardless of
  `b`), so the choice collapses to a per-step comparison of `0.5` (guess,
  free) against `1-c` (measure, paid): **exactly tied at `c=0.5`**
  (`action="tie"`), and `no_measure` becomes strictly optimal for any
  `c>0.5` (`action="no_measure"` at `c=0.6`) — a clean, closed-form
  threshold, not a numerical coincidence.
- **`p=0.1` and `p=0.9` give IDENTICAL values** at every tested `c` — an
  observed consequence of `|1-2p|` being the same (`0.8`) for both, which
  is what actually governs the belief's contraction rate; the panel does
  not separately re-derive this symmetry as its own hand-verified control
  case, but it is visible directly in the reported numbers.

## Symmetric error channel: a decoder that ignores when to invert

A uniform-prior bit passed through a binary symmetric channel with flip
probability `q` (`Y=X` w.p. `1-q`). The Bayes-**optimal** decoder achieves
accuracy `max(1-q,q)` — trusting `Y` directly when `q<0.5`, but INVERTING it
when `q>0.5` (an anti-correlated channel is still informative, once you know
to flip it). A **naive** decoder that always trusts `Y` directly gets
`1-q` regardless. At `q=0.3` (a channel better than random) both decoders
tie at `0.7` — there's nothing to invert. At `q=0.7` (a channel WORSE than
random) the optimal decoder still achieves `0.7` by inverting, while the
naive decoder gets only `0.3` — actively harmed by treating an
anti-correlated signal as if it were correlated.

## Scope

The full `(p, c, delay d, horizon H≤5)` cross-product panel named in the
plan is NOT exhaustively run here — the representative `(p,c)` panel above
(fixed horizon 5, no delay) demonstrates the same qualitative phenomena
(threshold behavior, measure-once-then-coast, worthless-information cases)
without the full combinatorial sweep. The `action` field is the optimal
FIRST decision only, not a full extracted policy table over all reachable
beliefs — a caller wanting the full per-belief policy can call
`bellman_value` again at any reached belief.
