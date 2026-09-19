# Nagumo Tangent Cone for Polyhedra (Milestone 28)

**Status:** review package only — not yet linked from README/GLOSSARY as accepted "core".
Johann-OK required before any core promotion.

## What this is

Typed Python helpers for the **Nagumo / Bouligand tangent-cone condition**
on a polyhedron \(K = \{z : A z \le b\}\), following Nagumo 1942
(DOI 10.11429/ppmsj1919.24.0_551). The module checks
\(A[i]\cdot f(z) \le 0\) for every *active* constraint at caller-supplied
boundary samples. **No viability-kernel solver. No curved boundaries.**

```text
src/scoped_correspondence/
  viability/
    core.py              # UNCHANGED — has_safe_transfer / shared-budget; not edited
    control_barrier.py   # UNCHANGED — M16 scalar CBF; not edited
    nagumo.py            # NEW — active_constraints + tangent_cone_condition
```

M28 covers **non-smooth** polyhedra / boxes (corners and edges), where no
single smooth barrier \(h\) exists. It is a **different case class** from
M16's scalar zeroing CBF — **not a replacement** for M16, and not "better",
just applicable where M16's smooth-\(h\) assumption fails.

Package-level `scoped_correspondence/__init__.py` is **not** rewritten here
(submodule-local wiring via `viability/__init__.py` only).

## Mapping

| Source | Claim / formula | API | Notes |
|---|---|---|---|
| Nagumo 1942, DOI 10.11429/ppmsj1919.24.0_551 | \(f(z) \in T_K(z)\) on \(\partial K\) ⇔ forward invariance of closed \(K\) | `tangent_cone_condition`, `verify_polyhedral_viability` | Bouligand contingent cone |
| Polyhedral specialization | \(T_K(z)=\{v:A[i]\cdot v\le 0,\ i\in I(z)\}\) | `active_constraints` | \(I(z)=\{i:A[i]\cdot z=b[i]\}\) |
| viability/core.py | scalar interval \(K=[b,\infty)\) via `has_safe_transfer` | (untouched) | M28 extends the *case class*, does not rewrite core |
| M16 control_barrier.py | smooth zeroing CBF \(h\) | (untouched) | different case class (smooth vs non-smooth) |

## Formulas

### Polyhedron and active set

\[
K = \{ z \in \mathbb{R}^n : A z \le b \},\qquad
I(z) = \{ i : A[i]\cdot z = b[i] \}.
\]

`active_constraints(z, A, b, tol)` returns \(I(z)\) within tolerance `tol`.

### Bouligand tangent cone (polyhedral)

\[
T_K(z) = \{ v : A[i]\cdot v \le 0 \ \text{for all}\ i \in I(z) \}.
\]

### Nagumo condition

\[
\forall\, i \in I(z):\quad A[i]\cdot f(z) \le 0.
\]

`tangent_cone_condition(z, f_z, A, b, tol)` returns `ok`, `margins`
(\(= A[i]\cdot f_z\) per active \(i\); \(\le 0\) means inward/tangent), and
`active_indices`.

`verify_polyhedral_viability(A, b, f, boundary_samples)` applies the check
at every caller-provided sample — **no auto-sampler / kernel solver**.

### Out of scope (explicit)

- Viability-kernel / Saint-Pierre algorithm
- Curved / nonlinear boundaries (only polyhedra / boxes)
- Editing `viability/core.py` or `control_barrier.py`
- Claiming M28 "replaces" M16

## Worked example (hand-checkable)

Linear system \(\dot z = A_{\mathrm{sys}} z\) with

\[
A_{\mathrm{sys}} = \begin{pmatrix}-1 & 0.5 \\ -0.5 & -1\end{pmatrix},
\qquad
K = [-1,1]^2
\]

encoded as four inequalities \(z_1\le 1,\ -z_1\le 1,\ z_2\le 1,\ -z_2\le 1\).

### Edges (active single constraint)

| Edge | \(f\) component | Range on edge | Nagumo |
|---|---|---|---|
| \(z_1=1\) (\(z_2\in[-1,1]\)) | \(f_1=-1+0.5 z_2\) | \([-1.5,-0.5]\) | \(f_1\le 0\) ✓ |
| \(z_1=-1\) | \(f_1=1+0.5 z_2\) | \([0.5,1.5]\) | \(-f_1\le 0\) ✓ |
| \(z_2=1\) | \(f_2=-0.5 z_1-1\) | \([-1.5,-0.5]\) | \(f_2\le 0\) ✓ |
| \(z_2=-1\) | \(f_2=-0.5 z_1+1\) | \([0.5,1.5]\) | \(-f_2\le 0\) ✓ |

Sweep: ≥ 20 points per edge.

### Corners (two active constraints)

| Corner | \(f(z)\) | Active half-spaces | ok? |
|---|---|---|---|
| \((1,1)\) | \((-0.5,-1.5)\) | \(f_1\le 0,\ f_2\le 0\) | yes |
| \((1,-1)\) | \((-1.5,0.5)\) | \(f_1\le 0,\ -f_2\le 0\) | yes |
| \((-1,1)\) | \((1.5,-0.5)\) | \(-f_1\le 0,\ f_2\le 0\) | yes |
| \((-1,-1)\) | \((0.5,1.5)\) | \(-f_1\le 0,\ -f_2\le 0\) | yes |

### Negative control

A deliberately outward \(A_{\mathrm{sys}}\) (e.g. identity) violates corner
\((1,1)\) → `ok=False` at that corner.

## Hand-checkable verification

Run:

```bash
PYTHONPATH=src python verification/verify_nagumo_tangent_cone.py
```

Expect all four edges (≥20 pts each) and four corners `ok=True` with the
corner \(f\)-vectors above; negative \(A_{\mathrm{sys}}\) yields `ok=False`
at one corner; DOI present in `source`.

## Untouched (forbidden)

- `src/scoped_correspondence/viability/core.py`
- `src/scoped_correspondence/viability/control_barrier.py`
- `src/scoped_correspondence/__init__.py` (package root)
- `FORMALISM.md`, `context_transformations.md`, `worked_example_viability.md`
- layer docs: `coupling_layer_afet.md`, `system_layer_utac.md`,
  `information_layer_crep.md`, `sheaf_contextuality.md`,
  `pid_redundancy_bottleneck.md`, `emergence_and_closure.md`
- viability-kernel solver / curved boundaries / "M28 replaces M16" claim
