# Epistemic layer — result semantics (H0 register)

**Status:** H0 register, review package — not yet linked from README/GLOSSARY
as accepted "core". Content basis: `SCF_ASSUMPTION_EVIDENCE_IMPLEMENTATION_PLAN.md`
§4. This document fixes the RESULT VOCABULARY before any code exists, so
later packages (H1–H5) implement against an already-agreed contract
rather than inventing status strings ad hoc.

## 1. Finite claim evaluation (§4.1)

Given a finite candidate set `W`, assumptions `A` (each a predicate on
`W`), and a claim `C` (also a predicate on `W`):

```
S_A = {w in W : a(w) is True for all a in A}
S_A^+ = {w in S_A : C(w)}
S_A^- = {w in S_A : not C(w)}
```

| `logical_status` | Condition | Meaning |
|---|---|---|
| `no_admissible_model_in_scope` | `S_A` empty | assumptions jointly unsatisfiable in this scope |
| `entailed_in_scope` | `S_A` nonempty, `S_A^-` empty | `C` holds for every admissible candidate |
| `negation_entailed_in_scope` | `S_A` nonempty, `S_A^+` empty | `not C` holds for every admissible candidate |
| `underdetermined` | both `S_A^+` and `S_A^-` nonempty | a positive AND a negative witness are both reported |
| `incomplete` | search aborted before full evaluation | any witness already found remains meaningful; universal claims and non-existence must NOT be inferred |

`search_complete: bool` is always reported separately from `logical_status`.
A counterexample refutes a universal claim outright; it never
automatically proves the negation "universal" without checking `S_A^+`
too (that would itself require re-deriving `negation_entailed_in_scope`,
not assuming it).

Empty `W` (empty *input*) is an input error, not a result. A nonempty `W`
from which `A` excludes every candidate (`S_A` empty) is a genuine
mathematical result (`no_admissible_model_in_scope`), never silently
treated as "no counterexample = proven".

## 2. Non-vacuous antecedents (§4.2)

For a conditional claim `B => C`, additionally check
`S_{A,B} = {w in S_A : B(w)}`. If `S_A` is nonempty but `S_{A,B}` is
empty, the implication can hold formally while never applying to a real
case: `antecedent_reachable_in_scope=False`,
`vacuity_kind="antecedent_never_holds"`. This is distinct from
`no_admissible_model_in_scope` (contradictory assumptions overall).

## 3. Minimal supports and inconsistency cores (§4.3)

`B ⊆ A` is a **subset-minimal supporting assumption set** for `C` iff
`S_B` is nonempty, `C` holds on all of `S_B`, and removing ANY single
element of `B` breaks one of those two conditions (a witness exists after
removal).

`K ⊆ A` is a **subset-minimal inconsistency core** iff `S_K` is empty and
removing any single element of `K` makes it nonempty again.

"Subset-minimal" is NOT "smallest cardinality" — multiple distinct
minimal supports/cores of different sizes can coexist (confirmed in K1:
`{A1,A4}` size 2 and `{A1,A2,A3}` size 3, both minimal). A deletion-based
search starts only from an already-satisfiable, already-supporting set;
satisfiability is not monotone under arbitrary subsets of "satisfiable
AND implies C" combined, so this distinction must never be abstracted
away. Minimal supports are logical dependencies relative to `W`, not
causal necessity or empirical credibility — background assumptions kept
fixed throughout must be listed separately, never hidden inside a
reported "minimal" set.

## 4. Observation fibers and identifiable targets (§4.4)

For a deterministic exact observation `h` and observed value `y`:

```
F_A(y) = {w in S_A : h(w) = y}
Q_A(y) = {q(w) : w in F_A(y)}
```

- A boolean claim is identified at `y` iff the nonempty fiber contains
  only one truth value.
- A numeric target is point-identified at `y` iff `Q_A(y)` has exactly
  one value.
- Multiple possible values are reported as a SET (a disconnected set like
  `{0,4}` is never collapsed to an interval `[0,4]`, which would falsely
  suggest intermediate values are possible — confirmed in K4).
- An empty fiber is an incompatibility between the observation and the
  declared model space, not "especially good identification".

If `h_c = r ∘ h_f` (a coarser observation derived from a finer one), every
fine fiber is contained in exactly one coarse fiber, so the set of
possible target values can only shrink or stay the same under this
refinement — holds for fixed assumptions and exact observations; changing
the noise model or tolerance is NOT this kind of refinement.

A tolerance relation like `|h(w)-y| <= eps` may later define compatible
candidates, but is not generally transitive and must not be silently
turned into equivalence classes via clustering in the exact path.

## 5. Claim-knowledge vs. action-knowledge (§4.5)

For a state `w`, `U_safe(w)` is the set of admissible safe interventions.
Over a fiber `F` (no further observation available):

```
U_uniform(F) = intersection over w in F of U_safe(w)
```

Two DIFFERENT statements, both tracked as explicit separate flags:

- `statewise_feasible`: `for all w in F, exists u: safe(w,u)` (a
  state-DEPENDENT action is allowed)
- `uniformly_feasible`: `exists u, for all w in F: safe(w,u)` (a SHARED
  action is required)

An observation-based policy `pi` may only depend on values actually
available: `exists pi, for all w: safe(w, pi(h(w)))`. For finite
one-step problems with no additional coupling between observation
classes, such a policy exists iff every reachable fiber has a uniform
feasible action — NOT a general theorem about POMDPs, dynamic games, or
infinite horizons.

## 6. Decisions under remaining ambiguity (§4.6)

After a hard feasibility check, compare a finite loss table `L(a,w)`:

```
a_worst  in argmin_a max_{w in F} L(a,w)                      (minimax)
a_regret in argmin_a max_{w in F} [L(a,w) - min_b L(b,w)]      (minimax-regret)
```

`F`, the action set, and the loss values are explicit inputs. Minimax and
minimax-regret are DIFFERENT, both selectable criteria (confirmed
distinct in K6) — neither is universally "correct" without a value
judgement. Probabilities are used only when an explicit distribution is
declared; the number of candidates in a list is never treated as an
implicit prior. Loss/expectation functions accept only finite values:
`+-inf`, NaN, and invalid probabilities are errors, never silently
clipped or renormalized. A very large finite utility is never a semantic
stand-in for infinite utility.

## Status categories carried through every report (§6.1, not a single traffic light)

`evidence_kind`: `exhaustive_finite`, `numerical_sample`,
`analytic_argument`, `empirical_evaluation`, `not_evaluated`.
`empirical_status` (separate axis): `not_tested`, `synthetic_only`,
`evaluated_on_declared_data`. No global `confidence=0.97` that collapses
these axes into one number. A source citation is not a machine-checked
proof certificate; a hash secures a byte reference, not scientific
correctness.
