# Transient amplification via non-normal coupling

CAPABILITY_EXPANSION_ROADMAP.md Priority 4 — Astra's own "most interesting
new mathematical direction" from her 2026-09-24 capability assessment:
non-normal dynamics and transient amplification (Trefethen, Trefethen,
Reddy & Driscoll 1993, Science 261, "Hydrodynamic Stability Without
Eigenvalues"). Module:
[`viability/transient_amplification.py`](../src/scoped_correspondence/viability/transient_amplification.py).
Verification: [`verify_transient_amplification.py`](../verification/verify_transient_amplification.py)
(5/5 checks).

## The point, in one matrix

```
A = [[-1, k], [0, -1]],    e^{At} = e^{-t} * [[1, k·t], [0, 1]]
```

Both eigenvalues of `A` are `-1` — the system is strictly, provably
stable. Yet for large `k`, a disturbance entering through the second
coordinate is transiently AMPLIFIED before decay takes over. **A
dangerous transition therefore does not require an unstable eigenvalue,
and does not require an exponentially growing external driver** —
coupling alone can temporarily amplify an existing disturbance. This adds
a genuinely different mechanism to this repository's existing account of
tipping (`dynamics/rate_dependent.py`, `viability/rate_dependent_buffer.py`),
which so far explained dangerous transitions via driving RATE, not via
non-normal COUPLING STRUCTURE.

`canonical_matrix_exponential_closed_form` matches `scipy.linalg.expm`
directly to numerical precision. `max_finite_time_gain` finds the peak of
`‖e^{At}‖` over `t` by continuous bounded optimization (not a grid
search); at `k=0` (a diagonal, NORMAL matrix) the gain never exceeds 1 and
peaks exactly at `t=0` — no amplification is possible without
non-normality, a clean sanity check of both the optimizer and the concept.

## An exact, hand-derivable regression check

For `x0=[0,1]` (a perturbation entering only the hidden/coupled
coordinate) on the canonical matrix, the closed form gives

```
x1(t) = k·t·e^{-t}
```

exactly — with maximum exactly at `t=1`, value `k/e`. This was derived
independently (not by re-running the module) and checked against
`classify_two_buffer_transient`'s numerically-found peak: both the peak
time and peak value match to `<1e-3`.

## Three outcomes, decided rigorously — not just simulated

Astra's explicit request: "Transiente Grenzverletzung, dauerhafter
Attraktorwechsel und bloß großer, aber zulässiger Ausschlag bleiben
verschiedene Ergebnisse." The classification is decided from the matrix's
EIGENVALUES, not merely from what a finite simulation window happens to
show (a finite window can never itself prove eventual return):

- **`safe_no_violation`** — stable, trajectory never crosses the boundary.
- **`transient_violation`** — stable (all eigenvalue real parts `< 0`),
  boundary IS crossed — return to the origin is analytically GUARANTEED,
  so this is provably temporary.
- **`unstable_not_yet_violated`** / **`unstable_violation_no_guaranteed_return`**
  — at least one eigenvalue has non-negative real part; a crossing here is
  a genuine candidate for a permanent attractor change, since nothing
  guarantees eventual return.

## Worked example: coupling alone causes the difference

Same initial perturbation (`x0=[0,1]`), same boundary (`0.5`), only the
coupling/stability changes:

| Case | Matrix | Eigenvalues | Peak `|x1|` | Classification |
|---|---|---|---:|---|
| No coupling | `[[-1,0],[0,-1]]` | `{-1,-1}` | **0** (exactly) | `safe_no_violation` |
| Coupled, stable | `[[-1,2],[0,-1]]` | `{-1,-1}` | **0.736** (`=2/e`) | `transient_violation` |
| Coupled, unstable | `[[0.1,2],[0,-1]]` | `{0.1,-1}` | growing, unbounded | `unstable_violation_no_guaranteed_return` |

The FIRST two rows share identical eigenvalues on the diagonal decay rate
and an identical perturbation — the only difference is the off-diagonal
coupling `k`. With `k=0`, `x1` is completely unaffected (it has no term
depending on `x2` at all, so it stays exactly at its initial value 0
forever). With `k=2`, the exact same perturbation on `x2` produces a
transient excursion that crosses the boundary before decaying back to
0 — coupling alone, not instability, not an external driver, causes the
violation.

## Scope

Restricted to 2×2 LINEAR systems (matches the canonical Trefethen et al.
example and Astra's suggested two-coupled-buffer extension). Larger
non-normal systems, nonlinear coupling, and a genuine bounded-intervention
response (Priority 5) are separate, not-yet-addressed extensions.
