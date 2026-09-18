# Control Barrier Functions Core (Milestone 16)

**Status:** review package only — not yet linked from README/GLOSSARY as accepted "core".
Johann-OK required before any core promotion.

## What this is

Typed Python helpers for a **scalar zeroing control barrier function (CBF)**
following Ames, Xu, Grizzle & Tabuada 2017 and the Ames et al. 2019 ECC
survey. The module checks the CBF inequality on the scalar integrator
\(\dot x = u\) with identity barrier \(h(x)=x\) and linear class-\(\mathcal{K}\)
map \(\alpha(r)=r\). **No QP solver.**

```text
src/scoped_correspondence/
  viability/
    core.py              # UNCHANGED — has_safe_transfer / shared-budget; not edited
    control_barrier.py   # NEW — BarrierFunction + cbf_condition + certificate
```

M16 does **not** implement multi-D CBFs, nonlinear \(\alpha\), CLF–CBF
quadratic programs, or a viability-kernel solver. It does **not** call or
re-express `has_safe_transfer` as a CBF formula, and does **not** mutate
`viability/core.py`, `FORMALISM.md`, or the layer docs.

Package-level `scoped_correspondence/__init__.py` is **not** rewritten here
(submodule-local wiring via `viability/__init__.py` only).

## Mapping

| Source | Claim / formula | API | Notes |
|---|---|---|---|
| Ames et al. 2017, DOI 10.1109/TAC.2016.2638961 | zeroing CBF: \(L_f h + L_g h\, u + \alpha(h) \ge 0\) ⇒ forward invariance of \(C=\{h\ge 0\}\) | `cbf_condition`, `verify_forward_invariance` | QP / CLF–CBF mediation **omitted** |
| Ames et al. 2019 ECC, DOI 10.23919/ECC.2019.8796030 | survey: safety as CBF dual of CLF stability; class-\(\mathcal{K}\) \(\alpha\) | `BarrierFunction.alpha_kind="linear"` | only identity \(\alpha(r)=r\) |
| Nagumo / CBF theorem (via Ames 2017) | admissible controls \(\{u : L_f h + L_g h\, u + \alpha(h)\ge 0\}\) | `admissible_controls_cbf` | scalar half-line only |

## Formulas

### Control-affine plant and Lie derivatives

\[
\dot x = f(x) + g(x)\, u,\qquad
L_f h = \nabla h\cdot f,\qquad
L_g h = \nabla h\cdot g.
\]

### Zeroing CBF condition (Ames et al. 2017)

\[
L_f h(x) + L_g h(x)\, u + \alpha\bigl(h(x)\bigr) \ge 0.
\]

`cbf_condition(L_f_h, L_g_h, u, alpha_h)` returns the **margin**
\(L_f h + L_g h\, u + \alpha_h\). Safe iff margin \(\ge 0\).

### M16 scalar specialization

\[
\dot x = u\quad(f=0,\, g=1),\qquad h(x)=x,\qquad \alpha(r)=r.
\]

Then \(L_f h = 0\), \(L_g h = 1\), and the inequality collapses to

\[
u + x \ge 0.
\]

`admissible_controls_cbf` reports the half-line \(u \ge -x\).
`verify_forward_invariance(barrier, x, u)` returns a `BarrierCertificate`
with `safe: bool` and `margin: float` (`margin = u + x`).

### Out of scope (explicit)

- Multi-dimensional state / multi-input \(g(x)\)
- Nonlinear class-\(\mathcal{K}\) \(\alpha\) (e.g. \(\alpha(r)=r^3\))
- CLF–CBF quadratic programs (Ames 2017 §IV) — no solver
- Linking CBF as a new formula for `has_safe_transfer`

## Worked examples (hand-checkable)

### Example A (spec) — \(x = 0.2\)

| \(u\) | margin \(= u + x\) | safe? |
|---|---|---|
| \(-0.1\) | \(0.1\) | yes |
| \(-0.3\) | \(-0.1\) | no |

### Example B (cross-check) — \(x = 0.5\)

| \(u\) | margin \(= u + x\) | safe? |
|---|---|---|
| \(-0.2\) | \(0.3\) | yes |
| \(-0.6\) | \(-0.1\) | no |

Admissible set at \(x=0.5\): \(u \ge -0.5\).

### Nonlinear alpha refused

`BarrierFunction(h=..., alpha=lambda r: r**3)` raises `ScopeViolationError`
(only `alpha(r)=r` / `alpha_kind="linear"`).

## Hand-checkable verification

Run:

```bash
PYTHONPATH=src python verification/verify_control_barrier_core.py
```

Expect Example A margins \(0.1\) / \(-0.1\); Example B margins \(0.3\) / \(-0.1\);
nonlinear alpha refused; DOIs present in `source`.

## Untouched (forbidden)

- `src/scoped_correspondence/viability/core.py`
- `src/scoped_correspondence/__init__.py` (package root)
- `FORMALISM.md`
- layer docs: `context_transformations.md`, `coupling_layer_afet.md`,
  `system_layer_utac.md`, `information_layer_crep.md`,
  `sheaf_contextuality.md`, `pid_redundancy_bottleneck.md`,
  `emergence_and_closure.md`
- multi-D CBF / nonlinear \(\alpha\) / QP solver / `has_safe_transfer` rewrite
