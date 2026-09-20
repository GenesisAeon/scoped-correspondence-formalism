# Structural Relations Between Models (Milestone — Audit Package 9/10)

**Status:** review package — not yet linked from README/GLOSSARY as accepted
"core". Johann-OK required before any core promotion.

**Origin:** proposed in `SCF_Strukturelle_Bruecken_Konzept.md` (Johann/Aeon,
2026-09-20; independently reproduced and hand-verified by Claude the same
day — all 7 computational groups in the companion `verify_structural_bridges.py`
matched byte-for-byte on a fresh run, and the B3 Lyapunov identity and the
B4 entropy-production numbers were additionally re-derived by hand). This
document is the Package 9 (language) and Package 10 (report/scope schema)
response from `AUDIT_ROADMAP.md`.

## 1. The tension this resolves

The project's justified rule against unearned identities, universal number
transfers, and vocabulary-driven conclusions does **not** imply a general
denial of mathematical kinship. Several existing warning strings overshot
this line — for example the old `THRESHOLD_KINSHIP_WARNING`
("NO mathematical kinship; different objects") and `AUTOPOIESIS_SCOPE_WARNING`
("same words different objects, no shared base class") denied any possible
structural comparison, not just an unearned identity.

Three levels stay distinct:

1. **Objects and meaning** — a chemical reaction network, a membership
   relation, and a Markov chain describe different things.
2. **Mathematical structure** — two such objects can satisfy the same
   closure axioms, or be linked exactly by an operator identity.
3. **Transfer of statements** — which results actually carry over depends
   on the concrete map, the stated assumptions, and the property in
   question.

**Guiding rule for this project:** different objects may share an explicitly
named mathematical structure. Every claimed relation gets its own scope, a
checkable conservation law, and a statement about what information is lost.
Physical, causal, or empirical meaning needs its own separate justification.

## 2. Relation types (kept separate, not a ladder)

A shared structure schema, an approximation, and an equivalence answer
different questions — none is a "higher" version of another.

| Relation type | Precise statement | Required evidence |
|---|---|---|
| Shared structure schema | Two constructions satisfy the same explicitly named axioms. | Verify the axioms hold for both constructions. |
| Representation / homomorphism | A map preserves selected operations or relations. | Define the map, check preservation, name what is lost. |
| Operator intertwining | Evolution and translation commute, e.g. `PC = CQ`. | State operator spaces, orientation, equation, and quantifiers. |
| Galois connection / safe abstraction | Concretization and abstraction stand in an order relation. | Check the orders and the adjunction/inclusion condition. |
| Controlled approximation / limit | The deviation is bounded in a stated norm and range. | State the error measure, constants, parameter range, horizon. |
| Isomorphism / conjugacy | A suitable invertible map preserves the entire named structure. | Prove the inverse, regularity, and every claimed conserved property. |

A bare analogy may be recorded as a **search hypothesis**. It carries no
transfer rights on its own.

Evidence is described independently of relation type: analytically derived,
covered by a referenced theorem under checked hypotheses, exhaustively
checked on a finite case, sampled numerically, or empirically investigated.
"Analytically derived" does not automatically mean "proof-assistant
verified."

## 3. Bridge card — minimum content

A first implementation is a short document (or, as below, a verify script's
structured output) with these fields; a large class hierarchy is not
required.

| Field | Content |
|---|---|
| `objects` | Typed source/target objects, dimensions, units, meaning. |
| `relation_kind` | One of the relation types in section 2. |
| `construction` | The map, operator, relation, or construction creating the link. |
| `claim` | The concrete mathematical statement, quantifiers included. |
| `scope` | State range, parameters, boundary conditions, timescale, context. |
| `assumptions` | Every precondition, tagged: stated, checked, or unclear. |
| `preserved` | Which operations, orders, observables, or properties survive. |
| `lost_or_unchecked` | What is discarded, and what is merely unchecked. |
| `evidence` | Derivation or theorem, literature, computed case, tolerance, version. |
| `failure_witness` | A counter-example or diagnostic case refuting a stronger claim. |
| `transfer_rules` | Which conclusions this specific relation actually licenses. |

A card may hold several claims with different outcomes — see bridge B2's
"exact macro dynamics" (true) vs. a hidden thermodynamic quantity (a
separate, later bridge; see `AUDIT_ROADMAP.md` item 10 follow-ups B3-B6).
Result categories stay distinguishable: **shown in scope**, **refuted by a
witness in scope**, **undetermined**, **out of scope**, **invalid input**.
Missing evidence is not a disproof; an error state or an empty sample must
never count as passed (this repeats the same discipline already applied in
the A02-A09 correspondence/percolation/profile-likelihood fixes).

## 4. Relation to the existing correspondence contract

The dynamical `Correspondence` contract (`correspondence/contract.py`)
remains an important special case: for constant `c > 0`,
`T ∘ Φ_X^t = Φ_Y^{ct} ∘ T`. This document adds relation types that need no
time map at all — a closure operator should not be forced into a trajectory
comparison.

Chaining bridges needs its own proof, too. For compatible stochastic
matrices and exact equations `PC = CQ`, `QD = DR`, it follows directly that
`P(CD) = (CD)R`. For defects, purely algebraically,
`PCD - CDR = (PC - CQ)D + C(QD - DR)` — a quantitative error bound needs a
chosen norm and properties of `C, D`; entropy production or intervention
compatibility are not proven by this algebra alone.

## 5. Pilot bridges (implemented and checked)

Two pilots are implemented as a runnable, hand-checkable verify script:
`verification/verify_structural_bridges_b1_b2.py`. Both use **only existing
repo APIs** (`chemical_organization.core.is_reaction_closed`,
`membership.formal_concept_analysis.derive_up/derive_down`,
`membership.core.MembershipMatrix`, `closure.core.is_exact_closure`) —
no new production module, no mutation of any existing Baustein.

### B1 — Reaction closure ↔ Formal Concept Analysis

**Relation kind:** shared structure schema, strengthened to an exact
representation on an explicitly constructed context.

For a finite species set `U` and reactions `R → P` with `R, P ⊆ U`, let
`F(A) = A ∪ ⋃_{R⊆A} P`. Repeated application to a fixpoint defines
`cl_R(A)`, the smallest reaction-closed superset of `A`; it is extensive,
monotone, and idempotent — the three closure-operator axioms, which the FCA
double-derivation `A ↦ A↑↓` also satisfies on any context.

**Construction:** choose FCA objects = species, attributes = all
reaction-closed subsets of `U`, incidence = set membership. Then
`A'' = ⋂ {B ⊆ U : B reaction-closed, A ⊆ B} = cl_R(A)` — a genuine
representation, not a coincidence of vocabulary, but only on this
purpose-built context; an arbitrary existing membership matrix does not
satisfy it automatically (checked below).

**Checked case:** `a → b`, `b → c`. Closed sets: `∅, {c}, {b,c}, {a,b,c}`.
All eight subsets of `{a,b,c}` agree between the FCA double-derivation on
the constructed context and `cl_R`; the identity (single-attribute)
context gives a different closure for `{a}`.

**Preserved:** extensivity, monotonicity, idempotence; the closure values
themselves on the constructed context.

**Lost / out of scope:** stoichiometric self-maintenance is not one of the
three closure axioms; `PC = CQ` Markov closure is not automatically a
power-set closure operator either. The module boundary
(`chemical_organization` vs. `membership.formal_concept_analysis` vs.
`closure`) stays as-is; no shared base class is introduced.

**Source:** Dittrich & Speroni di Fenizio (2007), DOI 10.1007/s11538-006-9130-8
(reaction closure); Ganter & Wille, *Formal Concept Analysis* (1999), DOI
10.1007/978-3-642-59830-2 (Galois derivation). The FCA representation
construction above is derived in this document, not claimed as a citation.

### B2 — Markovian closure ↔ operator intertwining

**Relation kind:** operator intertwining, exact on distributions and on
observables.

Let `P, Q` be row-stochastic transition matrices and `C` a binary
aggregation with exactly one `1` per micro-row. A macro-observable `g`
becomes a micro-observable via `Cg`. Then
`PC = CQ ⟺ P(Cg) = C(Qg)` for all `g`; applying the same equation to a row
distribution `p` gives `(pP)C = (pC)Q`, and by induction `PⁿC = CQⁿ` for all
`n ≥ 0`.

**Checked case:** a 4-state chain aggregated to 2 macro-states with macro
matrix `[[0.7, 0.3], [0.4, 0.6]]`. `is_exact_closure(P, C, Q)` holds (max
defect at machine precision); checked for powers `n ∈ {0, 1, 2, 5, 10}` and
for both observable-basis vectors. Perturbing one micro-row by `0.05`
breaks row-wise agreement of `P_bad C`, i.e. breaks exact lumpability, as
expected.

**Preserved:** the operator equation itself, and everything derivable from
it purely algebraically (all finite powers, all observable expectations
through `C`).

**Lost / out of scope:** a finite Koopman matrix fitted from data is not
automatically this kind of exact closure; invariance of the chosen
observable space needs a separate check. Entropy production and other
thermodynamic quantities are **not** implied to be preserved by `PC = CQ`
alone (see the hidden-dissipation counter-example recorded as future bridge
B4 in the source concept document — deferred, tracked in
`AUDIT_ROADMAP.md`).

**Source:** Koopman (1931), DOI 10.1073/pnas.17.5.315; Brunton et al.
(2016), DOI 10.1371/journal.pone.0150171, for the operator perspective this
finite stochastic case specializes.

## 6. Deferred (tracked, not implemented here)

The source concept document proposes four more worked bridges (B3
synchronization↔contraction, B4 hidden entropy production, B5 Turing
dispersion↔spectral stability, B6 Bethe percolation↔cusp bifurcation) and a
six-topic follow-on research program (abstract interpretation, Koopman/
Mori-Zwanzig, thermodynamically-consistent coarse-graining, Chemical
Reaction Network Theory, composed stability/viability guarantees, causal
abstraction). These are **not implemented in this pass** — see
`AUDIT_ROADMAP.md` for the tracked follow-up order. `prompts/Answers/
SCF_Strukturelle_Bruecken_Konzept.md` and its verification package
(`SCF_Strukturelle_Bruecken_Rechenbelege.zip`) carry the full derivations
and the eleven primary-source citations.
