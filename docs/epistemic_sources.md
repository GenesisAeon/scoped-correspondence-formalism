# Epistemic layer — source register (H0)

Content basis: `SCF_ASSUMPTION_EVIDENCE_IMPLEMENTATION_PLAN.md` §15.
Classification per source: primary paper, formal artifact, official tool
documentation, or mere occasion for the topic — not independently
re-verified by this repository beyond what's stated.

| # | Source | Kind | Used for | Explicit limit |
|---|---|---|---|---|
| S1 | Benzmüller & Woltzenlogel Paleo, *Gödel's God in Isabelle/HOL*, AFP 2013 | Formal artifact | Example of explicit logical semantics, kept as a separate variant | No empirical existence claim; not added as an SCF dependency |
| S2 | Benzmüller & Woltzenlogel Paleo, *The Inconsistency in Gödel's Ontological Argument*, IJCAI 2016 | Primary paper (full text checked, §4) | Satisfiability-before-conclusion discipline | Gödel's original vs. Scott's variant kept distinct |
| S3 | Alloy Project, official tutorial (file system, assertions, scope) | Official tool documentation | Finite-scope counterexample-search semantics for H1 | Not an empirical proof that small scopes find all errors; Alloy itself not a dependency |
| S4 | Kupferman & Vardi, *Vacuity detection in temporal model checking*, STTT 2003 | Primary paper (abstract + metadata only; publisher full text not freely accessible in this check) | Motivates the antecedent-reachability check (§4.2) | Only the explicit finite antecedent check is implemented, not full CTL* vacuity analysis |
| S5 | Fisman, Kupferman, Sheinvald-Faragy, Vardi, *A Framework for Inherent Vacuity*, HVC 2008 | Primary paper (intro + definitions checked) | Motivation to examine claim FORM, not just implementation | Full temporal mutation/synthesis deferred |
| S6 | Marques-Silva & Janota, *Computing Minimal Sets on Propositional Formulae I*, arXiv:1402.3011v2 | Primary paper | Precise minimal-support/-core semantics for H2 (subset-minimal != smallest cardinality) | Finite reference algorithms only, no SAT-scale claim |
| S7 | Manski, *Identification and Statistical Decision Theory*, arXiv:2204.11318 | Primary paper (intro + §2-4 checked) | H3/H4: separating structural identification from statistical uncertainty | Finite SCF control cases don't replace general frequentist decision analysis |
| S8 | Manski, *Coping with Inductive Risk When Theories are Underdetermined*, arXiv:2602.00355v2 | Preprint (abstract, §2, §5 checked) | Direct bridge: underdetermination -> decision | Preprint status noted, not peer-review-confirmed; supports methodology only, not a specific SCF theory |
| S9 | Gorissen, Yanıkoğlu, den Hertog, *A Practical Guide to Robust Optimization*, arXiv:1501.02634 | Primary paper | Shared intervention over an uncertainty set, explicit information timing | K5 is a separately hand-derived special case; no universal safety guarantee outside the declared uncertainty set |
| S10 | Clarke, Grumberg, Jha, Lu, Veith, *Counterexample-guided Abstraction Refinement*, CAV 2000 | Primary paper | Later-extension perspective for coarsening/closure modules | Splitting an observation fiber alone does not implement full CEGAR (needs proven abstraction relations + path checking) |

## Occasion, not a source to implement

The [Spektrum.de article on Pascal/Gödel](https://www.spektrum.de/kolumne/kann-mathematik-die-existenz-gottes-beweisen/2343717)
is the conversational trigger for this package, not a technical source.
No "god-proof engine", no probability-of-God computation, and no
metaphysical SCF derivation are part of this layer — S1/S2 are referenced
only as concrete examples of the general methodological distinction in
`docs/epistemic_scope.md` (does C follow from A vs. is A satisfiable vs.
is A realized).
