# Formal reduction error bounds (Milestone 21)

**Source.** Michel & Siegle, *Formal Error Bounds for the State Space Reduction of
Markov Chains*, Performance Evaluation **2024**,
DOI [10.1016/j.peva.2024.102464](https://doi.org/10.1016/j.peva.2024.102464),
arXiv:[2403.07618](https://arxiv.org/abs/2403.07618). Theorem numbering as in
**v3** (6 August 2024, the extended version; checked 2026-10-01: Theorem 4 =
DTMC bounds §3.1, Theorem 5 = CTMC bounds §3.2).

This milestone adds `scoped_correspondence.closure.error_bounds` — a **separate**
module that implements the paper's L1 transient / stationary bounds. It does
**not** edit `closure/core.py` or `generator_lumpability.py`, and does not mix
with M11 generator lumpability.

## What is implemented

| API | Paper formula |
|-----|---------------|
| `ReductionErrorBound` | Carrier: `horizon`, `bound`, `norm` (`L1` or `TV`), `theorem_ref`, `assumptions` |
| `transient_reduction_bound(...)` | **Theorem 4** (DTMC) / **Theorem 5** (CTMC) |
| `stationary_reduction_bound(...)` | **Corollary 10** |
| `residual_inf_norm(Π, A, P)` | `‖ΠA − AP‖_∞` (or `‖ΘA − AQ‖_∞`) |
| `paper_example_matrices()` | Worked DTMC from §3.4 with `‖ΠA − AP‖_∞ = 1/4` |
| `compare_to_propagated_error_bound` | Compatibility bridge to `propagated_error_bound` (CALL only) |

### Theorem 4 (DTMC), item 3 — primary discrete bound

If `Π` is row-stochastic and `π₀` is a probability vector,

\[
\|e_k\|_1 \le \|\pi_0^\top A - p_0^\top\|_1 + k \cdot \|\Pi A - A P\|_\infty,
\]

where \(e_k^\top = \pi_0^\top \Pi^k A - p_0^\top P^k\). Item 2 (geometric form with
`‖Π‖_∞`) is used automatically when the stochastic hypotheses fail.

### Theorem 5 (CTMC), item 3 — primary continuous bound

If `Θ` is a generator and `π₀` is a probability vector,

\[
\|e_t\|_1 \le \|\pi_0^\top A - p_0^\top\|_1 + t \cdot \|\Theta A - A Q\|_\infty.
\]

### Corollary 10 — stationary distance-to-stationarity

For stochastic `A` and probability `π`,

\[
\|\pi^\top A P - \pi^\top A\|_1 \le \|\Pi A - A P\|_\infty + \|\pi^\top \Pi - \pi^\top\|_1.
\]

This bounds how far the *lifted* candidate `πᵀA` is from being stationary for
`P` — **not** `‖p − πᵀA‖_1` to the true stationary law (paper Remark after Cor. 10).

### Norms

Paper §2.1: vector `‖·‖_1` = absolute sum; matrix `‖·‖_∞` = max absolute row sum.
For probability-vector differences, total variation is `TV = (1/2) ‖·‖_1`. Pass
`norm="TV"` to report the half-L1 bound.

## Scope of the inputs (Followup-Review-Fix R1/R2, 2026-10-01)

These rules follow the external review `SCF_REVIEW_J_SERIES_6b3a331_CLAUDE.md`.

- **Reduced side.** The reduced side may be general finite: the lifting
  `A`, `Π`/`Θ` and `π_0` are not restricted.
- **Full dynamics must be a Markov chain.**
  - `P` must be square and row-stochastic. The row convention is
    `p_{k+1} = p_k P`.
  - `Q` must be a square CTMC generator.
  - The reason: the proofs use `‖xP‖_1 ≤ ‖x‖_1` and `‖x e^{Qt}‖_1 ≤ ‖x‖_1`.
  - Other inputs raise `ScopeViolationError`.
  - Review counterexample: `P = diag(2, 1)` with `k = 2` had a true error of
    3 but an old bound of 2.
  - Arbitrary full linear dynamics would need extra amplification factors.
- **`norm="TV"` contract.** TV requires all of the following:
  - a row-stochastic lifting `A`;
  - probability vectors `π_0` and `p_0`;
  - Markov reduced dynamics.

  Then both compared vectors are probability distributions.
- **Stationary bound (Cor. 10).**
  - In L1 it holds for any finite matrices, because
    `πAP − πA = π(AP − ΠA) + (πΠ − π)A` is an algebraic identity.
  - In TV it additionally needs row-stochastic `A` and `P` and a probability
    vector `π`.
- **General CTMC branch.**
  - It uses `φ(t, κ) = expm1(tκ)/κ` with `κ = ‖Θ‖_∞`.
  - The continuous limit is `φ(t, 0) = t`.
  - Previously, `Θ = 0` (and, through cancellation, `Θ = 1e-20`) gave a
    **zero** bound. For the review example the bound is now 2, against a true
    error of `2(1 − e^{-1}) ≈ 1.264`.
  - This is a float evaluation, not an interval-rigorous bound.

## Degenerate cases

- `horizon = 0` (or `t = 0`) → bound equals the initial error only.
- `‖Θ‖_∞ = 0` in the general CTMC branch → bound `e_0 + ‖π_0‖_1 ‖ΘA − AQ‖_∞ · t`
  (vanishing reduced dynamics do not freeze the full chain).
- `‖ΠA − AP‖_∞ = 0` and matching initial condition → bound `0` (dynamic-exact /
  exact aggregation; Def. 8 / Cor. 7).
- Exact identity aggregation (`A = I`, `Π = P`) → residual `0`, bound `0`.

## Compatibility with `propagated_error_bound`

`propagated_error_bound(delta_cl, k) = min(1, k · delta_cl)` from `closure.core`
is an elementary **TV** bound on *projected* distributions with one-step defect

\[
\delta_{cl} = \max_i \mathrm{TV}\bigl((PC)_i,\ (CQ)_i\bigr).
\]

Michel–Siegle uses **L1** on the *full-state* error with residual `‖ΠA − AP‖_∞`.
Different norms, residuals, and state spaces — the inequality
`michel_tv ≤ propagated` is **not** guaranteed in general.

**Documented agreement.** When both residuals vanish (exact / dynamic-exact
aggregation), both bounds are `0`. For the paper §3.4 example with
`‖ΠA − AP‖_∞ = 1/4`, `k = 4`, and a conservative `delta_cl = 1/4`, one has

- Michel L1 bound = `1.0` → TV view `0.5`
- `propagated_error_bound(0.25, 4) = 1.0`
- so `michel_tv ≤ propagated` holds in this case
  (`compare_to_propagated_error_bound(1.0, 0.25, 4)["michel_tv_leq_propagated"] is True`).

`error_bounds` only **calls** `propagated_error_bound` / uses `is_exact_closure`
and `closure_error` in verification — it does not reimplement or edit them.

## Worked numbers (paper §3.4)

```text
P  = (1/4) · [[1,1,2],[1,2,1],[2,1,1]]
A  = [[1/2, 1/2, 0], [0, 0, 1]]
Π  = (1/8) · [[5, 3], [6, 2]]
‖Π A − A P‖_∞ = 1/4
π₀ = (1, 0),  p₀ = π₀ A = (1/2, 1/2, 0)   # initial error 0
⇒  ‖e_k‖_1 ≤ k/4     (Theorem 4 item 3)
k=4 ⇒ bound = 1.0
```

## Forbidden / untouched

- package-root `scoped_correspondence/__init__.py`
- `closure/core.py`, `closure/generator_lumpability.py`
- `FORMALISM.md`, `emergence_and_closure.md`
- no Markov-library dependency; no mix with M11 generator APIs
