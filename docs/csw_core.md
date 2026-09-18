# CSW Graph Invariants Core (Milestone 19)

**Status:** review package only — not yet linked from README/GLOSSARY as accepted "core".
Johann-OK required before any core promotion.

## What this is

Typed Python helpers for the **Cabello–Severini–Winter (CSW) graph-theoretic
bounds** on quantum correlations (Cabello, Severini & Winter 2014,
Phys. Rev. Lett. 112, 040401). For an exclusivity graph \(G\) a behaviour
assigns probabilities \(p_i\) to vertices (events) with \(p_i + p_j \le 1\) on
edges; the sum \(S = \sum_i p_i\) obeys

\[
\alpha(G)\;\le\;\vartheta(G)\;\le\;\alpha^*(G)
\]

(classical / quantum / general-probabilistic). This milestone specializes to
the pentagon \(C_5\), which yields the canonical numbers

\[
\alpha(C_5)=2,\qquad \vartheta(C_5)=\sqrt{5},\qquad \alpha^*(C_5)=\tfrac{5}{2}.
\]

```text
src/scoped_correspondence/
  contextuality/
    core.py   # UNCHANGED — sheaf CF / global sections; not edited
    csw.py    # NEW — α / θ / α* + CSWWitness (C5 umbrella)
```

M19 does **not** ship a general SDP library for arbitrary graphs, does **not**
identify the fractional-packing LP with the sheaf `contextual_fraction` LP,
and does **not** mutate `contextuality/core.py`, `FORMALISM.md`, or
`sheaf_contextuality.md`.

Package-level `scoped_correspondence/__init__.py` is **not** rewritten here
(submodule-local wiring via `contextuality/__init__.py` only).

## Mapping

| Source | Claim / formula | API | Notes |
|---|---|---|---|
| CSW 2014 PRL 112, 040401 DOI 10.1103/PhysRevLett.112.040401 | classical bound = independence number \(\alpha(G)\) | `independence_number` | brute force; \(C_5\to 2\) |
| same | quantum bound = Lovász number \(\vartheta(G)\) | `lovasz_theta` | **C5 umbrella OR** derives \(\sqrt{5}\); no general SDP |
| same | GPT bound = fractional packing \(\alpha^*(G)\) | `fractional_packing_number` | edge LP; \(C_5\to 5/2\) |
| same | witness comparing observed sum to the three bounds | `CSWWitness`, `csw_witness`, `symmetric_c5_model` | `classical_violated` flag |

arXiv mirror: https://arxiv.org/abs/1401.7081

## Formulas

### Independence number (classical)

\[
\alpha(G) = \max\{|I| : I\subseteq V(G),\ \text{no edge inside } I\}.
\]

### Lovász number via umbrella (quantum; C5)

Orthonormal representation: unit vectors \(u_i\) with \(u_i\cdot u_j = 0\) on
edges; handle \(c\). Then \(\vartheta = \min 1/(c\cdot u_i)^2\) over OR + handle.

For \(C_5\), the **umbrella** places five unit vectors in \(\mathbb{R}^3\) at
polar angle \(\alpha\) from \(c=(0,0,1)\) with azimuthal angles \(4\pi i/5\)
(pentagram ordering so graph-adjacent vertices subtend \(4\pi/5\)):

\[
\cos^2\alpha + \sin^2\alpha\cos\frac{4\pi}{5} = 0
\quad\Rightarrow\quad
\tan^2\alpha = -\frac{1}{\cos(4\pi/5)}.
\]

Hence

\[
\vartheta(C_5) = \frac{1}{\cos^2\alpha} = 1 + \tan^2\alpha.
\]

With \(\cos(4\pi/5)=-(1+\sqrt{5})/4\) one gets \(\tan^2\alpha=\sqrt{5}-1\) and
\(\vartheta=\sqrt{5}\). The implementation returns the float from this trig
identity (not a bare `return math.sqrt(5)`), and checks
\(|\vartheta_{\mathrm{umbrella}}-\sqrt{5}| < \mathtt{THETA\_TOL}\) with
\(\mathtt{THETA\_TOL}=10^{-10}\).

### Fractional packing (GPT)

\[
\alpha^*(G)=\max\Bigl\{\sum_i x_i : x_i+x_j\le 1\ \forall\{i,j\}\in E,\ 0\le x_i\le 1\Bigr\}.
\]

For \(C_5\), symmetry gives \(x_i=\tfrac12\) and \(\alpha^*=\tfrac52\).

**Not the same LP as** `contextual_fraction` in `core.py` (different incidence
structure / objective; sheaf CF is untouched).

### Out of scope (explicit)

- General SDP for \(\vartheta(G)\) on arbitrary graphs
- Equating \(\alpha^*\) LP with sheaf `contextual_fraction`
- Editing `contextuality/core.py`, package-root `__init__.py`,
  `FORMALISM.md`, `sheaf_contextuality.md`

## Worked example (symmetric C5)

Take every vertex probability \(p\) (edge exclusivity requires \(p\le\tfrac12\)).
Observed sum \(S=5p\).

| \(p\) | \(S=5p\) | vs \(\alpha=2\) | vs \(\vartheta=\sqrt{5}\approx 2.236\) | vs \(\alpha^*=2.5\) |
|---|---|---|---|---|
| \(0.40\) | \(2.00\) | held (=) | held | held |
| \(0.44\) | \(2.20\) | **violated** | held | held |
| \(0.45\) | \(2.25\) | **violated** | **violated** | held |

Self-check: computed invariants match \(\alpha=2\), \(\vartheta=\sqrt{5}\),
\(\alpha^*=2.5\) within documented tolerances.

## API sketch

```python
from scoped_correspondence.contextuality import (
    c5, independence_number, lovasz_theta, fractional_packing_number,
    symmetric_c5_model, CSWWitness,
)

G = c5()
assert independence_number(G) == 2
assert abs(lovasz_theta(G) - 5**0.5) < 1e-10
assert fractional_packing_number(G) == 2.5

w = symmetric_c5_model(0.44)  # sum 2.2
assert w.classical_violated and w.quantum_held and w.gpt_held
```

## Verification

```text
PYTHONPATH=src python verification/verify_csw_core.py
```

Writes `verification/verify_csw_core_results.json` with numbers from the run.
