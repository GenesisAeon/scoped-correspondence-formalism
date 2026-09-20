# Chemical Organization Theory / COT (Milestone 41)

**Status:** review package only — not yet linked from README/GLOSSARY as accepted "core".
Johann-OK required before any core promotion.

## What this is

Algebraic / stoichiometric **chemical organizations** after
Dittrich & Speroni di Fenizio (2007) and Fontana & Buss (1994): a set of
species is an organization iff it is **reaction-closed** and
**(stoichiometrically) self-maintaining**.

```text
src/scoped_correspondence/
  chemical_organization/
    __init__.py
    core.py
```

M41 does **not** fully formalize Autopoiesis, does **not** mutate other
Bausteine, package-root `__init__.py`, or `FORMALISM.md`.

## Mandatory disclaimer (verbatim)

**WARNING — Autopoiesis / naming / word collisions:**
This Baustein does NOT fully formalize Autopoiesis; name chemical_organization not autopoiesis. Reaction closure, formal-concept closure, and Markovian closure have different semantics. This does not rule out structural relations between selected constructions (see docs/structural_relations.md, bridge B1). Such relations must specify the objects, maps, preserved properties, and limitations; they do not imply shared physical meaning or require shared implementation inheritance.

Hard naming rule: no function/class/attribute identifier may contain
`closure` or `closed`, except the mandated API name `is_reaction_closed`.
(English prose in docs/docstrings may discuss the other Bausteine.)

## Mapping

| Source | Claim / formula | API | Notes |
|---|---|---|---|
| Dittrich & Speroni di Fenizio 2007 DOI 10.1007/s11538-006-9130-8 | organization = closed ∧ mass-maintaining | `is_organization` | LP form under name `is_self_maintaining` |
| Fontana & Buss 1994 DOI 10.1007/BF02458289 | operational closure / self-maintenance precursor | module sources | not full autopoiesis |
| algebraic closedness | reactants ⊆ A ⇒ products ⊆ A | `is_reaction_closed` | empty reactants = inflow |
| mass-maintenance LP | ∃ v: v_app≥1, v_other=0, (Sv)_A≥0 | `is_self_maintaining` / `maintenance_flux` | `scipy.optimize.linprog` |

## Formulas

### Reaction-closed

\[
\forall (R\to P)\in\mathcal{R}:\quad R\subseteq A \;\Rightarrow\; P\subseteq A.
\]

### Self-maintaining (mass-maintenance LP)

Let \(S\) be the stoichiometric matrix (rows = `species_order`, columns =
reactions). Let \(I(A)\) be the indices of reactions with reactants
\(\subseteq A\). Then \(A\) is self-maintaining iff there exists \(v\ge 0\) with

\[
v_r \ge 1\ \forall r\in I(A),\qquad
v_r = 0\ \forall r\notin I(A),\qquad
(Sv)_s \ge 0\ \forall s\in A.
\]

(Scale-invariant form of \(v_r>0\) on applicable reactions.)

### Organization

\[
\mathrm{is\_organization}(A)
=\mathrm{is\_reaction\_closed}(A)
\land\mathrm{is\_self\_maintaining}(A).
\]

## Worked example — species \(\{a,b\}\)

Reactions:

- \(r_1\): \(a\to b\)
- \(r_2\): \(b\to a\)
- \(r_3\): \(b\to\emptyset\)
- \(r_4\): \(\emptyset\to a\) (optional inflow)

Stoichiometry with `species_order = [a, b]`:

\[
S_{\text{with }r_4}
=
\begin{pmatrix}
-1 & 1 & 0 & 1 \\
1 & -1 & -1 & 0
\end{pmatrix}
,\qquad
S_{\text{without }r_4}
=
\begin{pmatrix}
-1 & 1 & 0 \\
1 & -1 & -1
\end{pmatrix}.
\]

### WITHOUT \(r_4\)

- \(\{a,b\}\) is **reaction-closed** (all products of applicable reactions stay in \(\{a,b\}\)).
- \(\{a,b\}\) is **NOT self-maintaining**: applicable \(\{r_1,r_2,r_3\}\) forces \(v_1,v_2,v_3\ge 1\); adding the two species inequalities yields \(-v_3\ge 0\), contradicting \(v_3\ge 1\).
- Only organization: \(\emptyset\) (vacuous applicable set; reaction-closed).

### WITH \(r_4\)

- \(\{a,b\}\) is an **organization** with witness \(v=(2,1,1,1)\):
  \((Sv)_a = -2+1+0+1 = 0\), \((Sv)_b = 2-1-1+0 = 0\).
- \(\emptyset\) is **not** reaction-closed (inflow \(\emptyset\to a\) produces \(a\notin\emptyset\)).

### Negative

- \(\{b\}\) alone is **not** self-maintaining (and typically not reaction-closed: \(b\to a\) produces \(a\)).

## Sources

- Dittrich, P. & Speroni di Fenizio, P. (2007). Chemical Organisation Theory.
  *Bull. Math. Biol.* **69**, 1199–1231. DOI [10.1007/s11538-006-9130-8](https://doi.org/10.1007/s11538-006-9130-8)
- Fontana, W. & Buss, L. W. (1994). “The arrival of the fittest”: Toward a
  theory of biological organization. *Bull. Math. Biol.* **56**, 1–64.
  DOI [10.1007/BF02458289](https://doi.org/10.1007/BF02458289)

## Out of scope

- Full Maturana–Varela autopoiesis (spatial membrane / topological boundary)
- Shared base class with `closure` (PC=CQ) or M27 FCA concept lattice
- Mutations of other Baustein directories, package-root `__init__.py`, `FORMALISM.md`
