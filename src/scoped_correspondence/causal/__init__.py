"""Finite causal models (Pakete J9/J10, SCOPE_COMPOSITION_EVIDENCE_ROADMAP.md).

``finite_scm``: finite acyclic structural causal models with an explicit
(possibly correlated) finite exogenous distribution and hard interventions.
``abstraction``: exact interventional abstraction checks between a micro
and a macro model over a DECLARED intervention set.
``selection_diagrams`` / ``transport``: d-separation, S-admissibility and
one checked standardisation rule (J10).

No graph learning, no causal claims about real data, no general
identification or transportability solver.
"""
