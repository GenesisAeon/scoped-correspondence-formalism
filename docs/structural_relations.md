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

Four pilots are implemented, each as a runnable, hand-checkable verify
script, none introducing a new production module or shared base
class/API. B1/B2 (2026-09-20): `verification/verify_structural_bridges_b1_b2.py`,
using **only existing repo APIs**
(`chemical_organization.core.is_reaction_closed`,
`membership.formal_concept_analysis.derive_up/derive_down`,
`membership.core.MembershipMatrix`, `closure.core.is_exact_closure`).
B7/B8 (2026-09-21, MECHANISTIC_VALIDATION_ROADMAP.md package 4):
`verification/verify_structural_bridges_b7_b8.py`, using **only existing
repo APIs** (`dynamics.energy_balance.fit_energy_balance_model` /
`integrate_energy_balance_trajectory`,
`viability.rate_dependent_buffer.run_buffer_spike_trajectory`,
`validation.covid_renewal.discretized_generation_interval` /
`wallinga_lipsitch_r`, `dynamics.etas.etas_branching_ratio`). The B3-B6
numbers are reserved for the concept document's own deferred bridges (see
section 6) — B7/B8 continue the sequence rather than reuse them.

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

### B7 — Linear impulse-response systems: energy balance ↔ rate-dependent buffer

**Relation kind:** shared structure schema (linear time-invariant systems
driven by an external input), strengthened to an exact representation
(the trajectory of each system equals a convolution with its own impulse
response) on each system's own fixed-coefficient regime.

**Origin:** `prompts/Answers/nicht_stationäre_Treiber/SCF_Review_f8e249f.md`
(Astra, 2026-09-21), "Die mathematisch ergiebigste neue Verbindung":
"EBM/Puffer über Impulsantworten" — MECHANISTIC_VALIDATION_ROADMAP.md
package 4.

**Objects:** `dynamics.energy_balance`'s two-layer model, a 2-state linear
system `dx/dt = Ax + BF(t)`, `T_s = Cx` with
`A = [[-(alpha+gamma)/C_s, gamma/C_s], [gamma/C_d, -gamma/C_d]]`,
`B = [1/C_s, 0]^T`, `C = [1, 0]`; `viability.rate_dependent_buffer`'s
scalar buffer, a 1-state linear system `dx/dt = -r*x + u(t)`, `z = x + z_eq`
with `u(t) = U - W(t)`.

**Construction:** for a linear time-invariant system, the solution
decomposes as `x(t) = C e^{At} x(0) + ∫_0^t [C e^{A(t-s)} B] * input(s) ds`
— a homogeneous (initial-condition decay) term plus a CONVOLUTION of the
input with the system's own impulse response `h(t) = C e^{At} B`. For the
buffer (1-D), `h(t) = e^{-rt}` exactly — a single relaxation timescale.
For the energy balance model (2-D), `h(t)` is a sum of two real decaying
exponentials `w_1 e^{lambda_1 t} + w_2 e^{lambda_2 t}` via the eigendecomposition
of `A` — a genuine fast/slow relaxation, not assumed but *checked*: for
the currently-shipped fit, eigenvalues are real and negative
(-0.2747, -0.00364), giving timescales ≈3.64 years (fast, surface) and
≈274 years (slow, deep ocean) — a 75x separation. The Laplace-domain
transfer function `G(s) = C(sI-A)^-1 B` for the energy balance model
matches Astra's own closed-form formula
`G(s) = (C_d*s+gamma) / ((C_s*s+alpha+gamma)(C_d*s+gamma) - gamma^2)`
exactly (checked at `s ∈ {0.1, 0.5, 1.0, 2.3}`, agreement to machine
precision).

**Claim:** both systems' production-function trajectories are
independently reproduced via direct convolution (homogeneous term +
numerical quadrature, NOT calling `solve_ivp`/`scipy.linalg.expm` again)
and agree with `integrate_energy_balance_trajectory` / the buffer's own
`z_min` to `1e-6`–`1e-11`.

**Scope:** each system's own FIXED coefficients (the currently-fitted
`(C_s, C_d, alpha, gamma)` for the energy balance model; the constant `r`
for the buffer) over the checked time range.

**Assumptions:** linearity and time-invariance of `A`/`B`/`C` — stated
and checked (both models are genuinely linear ODEs with constant
coefficients as already implemented; no new assumption is introduced by
this bridge).

**Preserved:** the exact trajectory (both homogeneous and forced
response); the transfer-function representation; the fast/slow
decomposition for the 2-state case.

**Lost / out of scope:** parameter IDENTIFIABILITY is a separate question
(package 1 already found `C_s`, `C_d`, `alpha` practically unidentified
for the energy balance model — this bridge says nothing new about that,
it only concerns the exact input-output MAP for whatever coefficients are
given). Nothing here claims the buffer and the energy balance model are
the SAME system — only that they are both instances of the same linear
convolution structure, at different state dimension.

**Failure witness:** a time-varying relaxation rate (`r=1` for `t<0`,
`r=2` for `t>=0` in the buffer) breaks the FIXED-impulse-response
convolution by a large margin (checked: true trajectory at `t=3` is
`-0.0123`; the WRONG fixed-`r=1` convolution gives `-0.1133`, a
difference of `0.101` — three orders of magnitude larger than the
same-system agreement above). Confirms the bridge genuinely requires
time-invariance, not just "any linear-looking system."

**Evidence:** `verification/verify_structural_bridges_b7_b8.py`,
check `B7_impulse_response_representation` (2/2 total, this script).
Uses only `dynamics.energy_balance.fit_energy_balance_model` /
`integrate_energy_balance_trajectory` and
`viability.rate_dependent_buffer.run_buffer_spike_trajectory` — no new
production module, no shared "impulse-response API".

**Transfer rules:** licenses treating both models' forced responses as
convolutions when reasoning about memory/filtering behavior (e.g. why a
brief load spike is attenuated by a buffer with fast relaxation, or why
the energy balance model has a decades-long "committed warming" tail from
its slow eigenmode) — does NOT license transferring parameter estimates,
identifiability results, or stability conclusions between the two models.

### B8 — Positive kernels / branching operators: COVID renewal ↔ ETAS-Hawkes

**Relation kind:** shared structure schema (both are self-exciting /
renewal processes driven by a nonnegative kernel over past events),
strengthened to an exact quantitative identity: total kernel mass equals
expected direct offspring count (Hawkes & Oakes 1974). This identity
needs **no stationarity assumption** — see the 2026-09-23 correction
below for what stationarity actually requires and why `R=1.68` does not
have it.

**Origin:** `prompts/Answers/nicht_stationäre_Treiber/SCF_Review_f8e249f.md`
(Astra, 2026-09-21): "Renewal/ETAS-Hawkes über positive Kerne und
Verzweigungsoperatoren [...] für ein stationäres lineares Hawkes-Modell
[...] ist die Gesamtmasse seines mittleren Kerns die erwartete Zahl
direkter Nachkommen" — MECHANISTIC_VALIDATION_ROADMAP.md package 4.

**Objects:** `validation.covid_renewal`'s renewal equation
`Lambda_t = Σ_s w_s I_{t-s}`, `I_t = R_t Λ_t`, generation-interval weights
`w_s` (`Σ_s w_s = 1`); `dynamics.etas`'s self-exciting kernel
`Σ_i K exp(alpha(M_i-M0)) / (t-t_i+c)^p` with branching ratio
`n = K E[exp(alpha(M-M0))] c^(1-p)/(p-1)` (`etas_branching_ratio`).

**Construction:** for CONSTANT `R`, the renewal recursion
`I_t = R Σ_s w_s I_{t-s}` has reproduction kernel `phi_s = R w_s`, with
total mass `Σ_s phi_s = R Σ_s w_s = R` (checked: `Σ_s w_s = 1` exactly;
`R * Σ_s w_s = R` exactly for `R=1.68`, Pilot B's Wallinga-Lipsitch-implied
value). By Hawkes & Oakes (1974, *A cluster process representation of a
self-exciting process*, J. Appl. Probab. 11:493-503, DOI 10.2307/3212693),
this total kernel mass IS the expected number of direct offspring per
event — i.e. **`R` itself is the branching ratio**, computed by the exact
same general principle (total kernel mass = expected direct offspring
count) that `etas_branching_ratio` already implements for the
structurally different Omori-Utsu kernel. **This part requires only that
`R` be constant over the recursion, not that the resulting process be
stationary.**

**Correction (2026-09-23, response to
[`SCF_Review_3e8dce3.md`](../prompts/Answers/nicht_stationäre_Treiber/SCF_Review_3e8dce3.md),
Astra, finding 3):** an earlier version of this section additionally
claimed that constant `R` makes the renewal recursion "exactly a
**stationary** linear Hawkes/branching recursion." That additional claim
is **wrong** and has been removed. Constant coefficients do not by
themselves guarantee a stationary process distribution. For a linear
Hawkes process with positive immigration `mu` and finite stationary mean,
the mean-value equation

```
lambda_bar = mu + n * lambda_bar   =>   lambda_bar = mu / (1 - n)
```

requires the **subcritical** case `n < 1` — only then does the classical
stationary cluster representation (Hawkes & Oakes 1974) apply. The
`R=1.68` value checked above is **superctitical** (`n > 1`): plugging it
into the formula above with `mu=1` gives `1 / (1 - 1.68) ≈ -1.4706` — a
**negative** mean rate, which is impossible for a point-process
intensity. `R=1.68` is therefore a **counterexample** to the stationarity
claim, not supporting evidence for it; as a model of **nonstationary
branching growth** (a genuinely super-critical, still-growing epidemic
phase), `R=1.68` remains entirely sensible. A genuinely subcritical value
such as `R=0.8` DOES give a finite, positive stationary mean
(`1/(1-0.8)=5.0` for `mu=1`) — see
`verification/verify_structural_bridges_b7_b8.py`'s
`subcritical_example` / `superctitical_counterexample` fields for both
computed side by side.

Two further distinctions the original text elided, now made explicit:
a **deterministic** incidence recursion (as implemented in
`covid_renewal.py`) is not itself a stochastic point process — a precise
bridge must state whether it preserves kernel mass, a mean-value
equation, a conditional intensity, or the full process distribution (this
section only ever claimed the first: kernel mass). The renewal side also
runs in **discrete** time while the Hawkes/ETAS side is continuous-time;
this document does not construct an explicit discrete-to-continuous-time
correspondence, and none is claimed.

**Claim (corrected):** the renewal model's `R` and ETAS's `n` are the
same KIND of quantity (total mass of a nonnegative offspring kernel) —
this holds for ANY constant `R`, subcritical or supercritical. Reading
`R`/`n` additionally as branching ratios of a *stationary* cluster
process requires the separate, stricter subcritical condition `n < 1`,
which `R=1.68` does not satisfy.

**Scope:** the kernel-mass identity holds while `R` is genuinely constant
over the window considered; the stationary-process reading holds
additionally only in the subcritical case (`R<1`, `n<1`). The ETAS side
already integrates its kernel over an infinite horizon by construction
(`etas_branching_ratio`'s own docstring), independent of this
correction.

**Assumptions:** stationarity of `R` (checked to be the load-bearing one
below); a well-defined, integrable kernel on each side (checked:
`Σ_s w_s` converges by construction — `s_max` truncation; ETAS's kernel
integral is finite exactly when `p>1`, already enforced by
`etas_branching_ratio`'s own `ScopeViolationError`).

**Preserved:** the total-kernel-mass identity itself, and (for the
renewal case) the round-trip consistency with `wallinga_lipsitch_r`
(checked: solving for the growth rate `r` implied by `R=1.68` and
reconverting reproduces `R=1.68` to `1e-9`).

**Lost / out of scope:** no claim that COVID incidence and earthquake
occurrence are the same PHENOMENON — only that a scalar summary of "how
much a process's own past feeds its future" is computed by the same
general formula in both domains. Multi-type branching (a nonnegative
matrix, spectral radius as the threshold) is NOT implemented here — noted
by Astra as a further, deferred extension.

**Failure witnesses (by reference to already-verified results elsewhere
in this repo, not recomputed here — both are the SAME kind of quantity
failing for DIFFERENT structural reasons):**
1. Real `R_t` is NOT constant: `covid_renewal.py`'s own directly-computed
   series dips below 1 (late Feb 2020) and rises above 1.5 (mid-March
   2020) within the same window (`docs/covid_renewal.md`) — exactly why
   `project_incidence_constant_r` (package 2) had to explicitly ASSUME
   constant `R`, and its real-data forecast errors
   (`docs/mechanistic_rolling_origin.md`,
   `docs/mechanistic_probabilistic_evaluation.md`) are the visible cost
   of that assumption not holding exactly.
2. ETAS's own branching ratio is fragile for a DIFFERENT reason: only
   ~30% of its kernel's total mass falls within the observed catalog
   span (package 1, `docs/etas_earthquakes.md`) — a power-law-tail
   truncation issue that the renewal model's exponential-family
   (Gamma-distributed) generation interval, compactly summed to
   `s_max=20` days, does not share.

**Evidence:** `verification/verify_structural_bridges_b7_b8.py`, check
`B8_positive_kernel_branching_operator` (2/2 total, this script). Uses
only `validation.covid_renewal.discretized_generation_interval` /
`wallinga_lipsitch_r` and `dynamics.etas.etas_branching_ratio` — no new
production module, no shared "kernel API" (Astra's explicit caution
against one).

**Transfer rules:** licenses interpreting `R` (under a
constant-R/stationarity reading) and ETAS's `n` as instances of the same
general branching-ratio concept when discussing near-critical dynamics
across domains — does NOT license treating COVID's compactly-supported
generation interval and ETAS's power-law Omori-Utsu tail as
interchangeable, and does NOT extend to the multi-type / spectral-radius
generalization, which remains unimplemented.

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
