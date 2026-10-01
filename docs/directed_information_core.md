# Directed information I(Xⁿ→Yⁿ) (Milestone 22)

**Module:** `scoped_correspondence.observation.directed_information`  
**Sources:** Massey (1990), *Causality, feedback and directed information*, Proc. ISITA, pp. 303–305; Permuter, Weissman & Goldsmith (2009), *IEEE Trans. Inf. Theory* **55**(2):644–662.

## Definition (exact construction)

For jointly distributed discrete sequences \(X^n=(X_1,\ldots,X_n)\) and \(Y^n=(Y_1,\ldots,Y_n)\),

\[
I(X^n \to Y^n) \;=\; \sum_{i=1}^{n} I\bigl(X^i;\, Y_i \mid Y^{i-1}\bigr),
\]

with the convention \(Y^{0}=\emptyset\) (so the \(i=1\) term is \(I(X_1;Y_1)\)).  
Each summand is a conditional mutual information, hence \(\ge 0\). Massey's inequality:

\[
I(X^n \to Y^n) \;\le\; I(X^n; Y^n),
\]

with equality iff there is no feedback (\(X_{i+1}\)—\(X^i\)—\(Y^i\)). With nontrivial feedback the inequality is typically **strict**.

## Paper → code mapping

| Massey / Permuter et al. | This package |
| --- | --- |
| \(I(X^n \to Y^n)\) | `DirectedInformationReport.I_directed` |
| \(I(X^n; Y^n)\) | `DirectedInformationReport.I_mutual` |
| \(I(X^i; Y_i \mid Y^{i-1})\) | `summands[i-1]` |
| Binary entropy \(H(p)\) | `binary_entropy(p)` |

## BSC examples (hand-checkable)

Channel: \(Y_i = X_i \oplus Z_i\), \(Z_i\sim\mathrm{Bern}(p)\) i.i.d.  
Binary entropy \(H(p)=-p\log_2 p-(1-p)\log_2(1-p)\). For \(p=1/4\):

\[
H(1/4)=2-\tfrac34\log_2 3 \approx 0.811278124459.
\]

### With feedback (\(n=2\))

Construction: \(X_1\sim\mathrm{Bern}(1/2)\); \(X_2:=Y_1\) (encoder uses previous output); \(Y_i=X_i\oplus Z_i\).

\[
I(X^2\to Y^2)=1-H(p),\qquad I(X^2;Y^2)=1.
\]

For \(p=1/4\): \(I_\mathrm{dir}\approx 0.188721875541 < I_\mathrm{mutual}=1\).  
Summands: \(I(X_1;Y_1)=1-H(p)\), \(I(X^2;Y_2\mid Y_1)=0\).

### Without feedback (\(n=2\) or \(3\))

Construction: \(X_i\) i.i.d. \(\mathrm{Bern}(1/2)\), independent of past \(Y\); same BSC.

\[
I(X^n\to Y^n)=I(X^n;Y^n)=n\bigl(1-H(p)\bigr)
\]

(equality to machine precision). For \(n=2\), \(p=1/4\): both \(\approx 0.377443751082\).

## API

- `directed_information(joint_sequences) -> DirectedInformationReport`  
  `joint_sequences`: mapping `((x_1..x_n), (y_1..y_n)) -> mass`.
- `bsc_feedback_joint(p, n=2|3)`, `bsc_no_feedback_joint(p, n=2|3)`
- `bsc_feedback_vs_mutual(p=0.25, n=2)` — side-by-side report with analytics.
- `binary_entropy(p)` — hand-checkable \(H(p)\).

## Scope / non-goals (M22)

- Finite discrete alphabets, finite horizon \(n\in\{2,3\}\) for the BSC helpers.
- **No** continuous-time directed information.
- **No** identification with `EI_q` or PID atoms (those live under `information_decomposition`; this module does not import or equate them).
- Does **not** edit `observation/core.py` or package-root `__init__.py`.
- Does **not** edit `FORMALISM.md`.

## Input modes (2026-10-01)

`directed_information(joint, *, input_mode="weights" | "pmf")`. The modes
follow the follow-up review `SCF_FOLLOWUP_REVIEW_637bc1c` §5.

- **`"weights"`** (default, unchanged behaviour):
  - Finite, non-negative weights are renormalised.
  - Scaling all weights by one positive factor leaves the result unchanged.
- **`"pmf"`**: the input must be a probability distribution.
  - For `int`/`Fraction` masses the total must be exactly 1.
  - For float masses the total must satisfy `|total − 1| ≤ PMF_TOL = 1e-12`,
    computed with `math.fsum`.
  - Anything else raises `ScopeViolationError`.
- **Both modes:**
  - Non-finite, negative and zero-total inputs are refused (since the
    review fix R4, non-finite masses no longer vanish silently).
  - The report carries `input_mode` and `input_total_mass`, the total as
    passed.

Checks: `verification/verify_information_input_modes.py`.

## Verification

`verification/verify_directed_information_core.py` checks the BSC identities, non-negativity of summands, Massey inequality, and that forbidden files are untouched in the delivery tree.
