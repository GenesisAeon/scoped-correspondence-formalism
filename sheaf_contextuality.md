# Sheaf Contextuality (F08) — optional module beside VB1

Revision package F08/F09, 16 September 2026 (Europe/Berlin). **Does not mutate** `FORMALISM.md` or Verträglichkeitsbedingung 1 (VB1). VB1 remains for deterministic stocks; this module reports contextual fraction for stochastic / multi-view overlaps as a **separate optional** analysis.

Definitions and checks: [`verification/verify_sheaf_contextuality.py`](verification/verify_sheaf_contextuality.py). Numbers below are **from that script run** only ([`verification/verify_sheaf_contextuality_results.json`](verification/verify_sheaf_contextuality_results.json)).

## 1. Primary sources

| Work | Identifiers |
|---|---|
| Abramsky & Brandenburger, *The sheaf-theoretic structure of non-locality and contextuality* | [arXiv:1102.0264](https://arxiv.org/abs/1102.0264); New J. Phys. 13 113036 (2011); DOI [10.1088/1367-2630/13/11/113036](https://doi.org/10.1088/1367-2630/13/11/113036) |
| Abramsky, Barbosa & Mansfield, *The contextual fraction as a measure of contextuality* | [arXiv:1705.07918](https://arxiv.org/abs/1705.07918); Phys. Rev. Lett. 119, 050504 (2017); DOI [10.1103/PhysRevLett.119.050504](https://doi.org/10.1103/PhysRevLett.119.050504) |

## 2. Formulas

**Measurement scenario:** \(\langle X,\mathcal{M},O\rangle\) — measurements \(X\), contexts \(\mathcal{M}\) (anti-chain of maximal compatible sets), outcomes \(O\).

**Event sheaf:** for \(U\subseteq X\), \(\mathcal{E}(U)=O^U\) (sections = outcome assignments). Restrictions \(s\mapsto s|_U\).

**Empirical model:** for each \(C\in\mathcal{M}\) a distribution \(e_C\) on \(O^C\), with **compatible margins** (generalised no-signalling):

\[
\forall C,C'\in\mathcal{M}:\quad
e_C\big|_{C\cap C'} = e_{C'}\big|_{C\cap C'}.
\]

**Global section:** a distribution \(d\) on \(O^X\) with \(d|_C=e_C\) for all \(C\). **Contextuality** \(\Leftrightarrow\) no such \(d\) exists.

**Incidence matrix:**

\[
\mathbf{M}[\langle C,s\rangle, g]
=
\begin{cases}
1 & \text{if } g|_C = s,\\
0 & \text{otherwise.}
\end{cases}
\]

Non-contextuality: \(\exists\,\mathbf{d}\ge\mathbf{0}\) with \(\mathbf{M}\,\mathbf{d}=\mathbf{v}^e\) and \(\mathbf{1}\cdot\mathbf{d}=1\).

**Contextual fraction** (Abramsky–Barbosa–Mansfield):

\[
e = \lambda\, e^{\mathrm{NC}} + (1-\lambda)\, e',\qquad
\mathsf{NCF}(e)=\max\lambda,\qquad
\mathsf{CF}(e)=1-\mathsf{NCF}(e).
\]

LP form:

\[
\max_{\mathbf{b}}\;\mathbf{1}\cdot\mathbf{b}
\quad\text{s.t.}\quad
\mathbf{M}\,\mathbf{b}\le\mathbf{v}^e,\quad \mathbf{b}\ge\mathbf{0}.
\]

Then \(\mathsf{NCF}(e)=\mathbf{1}\cdot\mathbf{b}^\*\), \(\mathsf{CF}(e)=1-\mathsf{NCF}(e)\). Values in \([0,1]\); \(\mathsf{CF}=1\) iff strong contextuality.

**LP backend in verify script:** `scipy.optimize.linprog` (HiGHS).

## 3. Mapping to VB1 (separate module)

| Local (Revision 3.2 / VB1) | Sheaf module |
|---|---|
| Back-maps \(R_{\alpha e}=R_{\beta e}=x_e\) | Restriction to shared measurement \(e\) |
| Compatible combinations \(\subset\) product space | Compatible family \(\{e_C\}\) |
| Contradiction \(x=y\), \(y=z\), \(z=x+1\) | Empty space of global sections (deterministic) |
| **Not replaced** | Marginal-compatible but no global \(d\) \(\Rightarrow\) \(\mathsf{CF}>0\) as a **finding**, not a modelling bug |

Johann decision: VB1 **unchanged** for deterministic stocks; sheaf is optional beside it.

## 4. Minimal API

```text
SheafScenario(X, contexts, outcomes)
EmpiricalModel.from_tables(scenario, tables)   # checks margin compatibility
has_global_section(model) -> bool
contextual_fraction(model) -> {NCF, CF}
report(model) -> {compatible_margins, NCF, CF, has_global_section, ...}
```

## 5. Worked numbers (from script run)

Tolerance for “CF ≈ 0”: absolute \(10^{-7}\) (classical factorisable). CHSH match to literature \(1/4\): absolute \(10^{-5}\).

| Case | Expectation | Script result |
|---|---|---|
| Classical factorisable \(P=1/4\) | `has_global_section=True`, CF≈0 | **CF = 0.0**, NCF = 1.0, has_global_section = True |
| PR-box (Table I right, arXiv:1705.07918) | CF = 1 | **CF = 1.0**, NCF = 0.0 |
| CHSH QM Table I (angles \(0,\pi/3\) on \(\lvert\Phi^+\rangle\), same paper) | \(0<\mathrm{CF}<1\) | **CF = 0.25**, NCF = 0.75 (matches literature CF = 1/4; CHSH value 2.5) |
| VB1 deterministic \(x=y,y=z,z=x+1\) over \(\{0,1,2\}\) | no global assignment | **0** of 27 globals consistent with support; has_global_section = False |

Margin compatibility on (2,2,2) Alice/Bob: classical, PR, and CHSH Table I all **compatible** (script `s01`).

JSON summary printed by the verify script:

```json
{"count": 6, "passed": 6, "failed": []}
```

## 6. Relation to CREP-UTAC-AFET

Use CF when several stochastic views of overlapping quantities are margin-compatible yet admit no joint explanation. Do **not** silently rewrite VB1: if stocks are deterministic and contradictory, keep the VB1 empty-assignment reading; optionally run the sheaf smoke test for analogy.

First toy may be unphysical (PR-box) to harden CF infrastructure against known values before GenesisAeon cases.
