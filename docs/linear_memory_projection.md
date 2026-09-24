# Shared operator structures and memory: exact Mori-Zwanzig reduction for linear systems

CAPABILITY_EXPANSION_ROADMAP.md Priority 3, response to Astra's 2026-09-24
capability assessment: "Die Mori-Zwanzig-Perspektive erklärt, weshalb das
Eliminieren verborgener Zustände Gedächtnis und einen vom verborgenen
Anfangszustand abhängigen Restterm erzeugt" (Chorin, Hald & Kupferman 2000,
PNAS 97, 2968-2973). Module:
[`closure/linear_memory_projection.py`](../src/scoped_correspondence/closure/linear_memory_projection.py).
Verification: [`verify_linear_memory_projection.py`](../verification/verify_linear_memory_projection.py)
(4/4 checks).

## The exact reduction

A linear system with one observed scalar `x` coupled to an
arbitrary-dimensional hidden block `z`:

```
dx/dt = A*x + B @ z + f(t)      (forcing acts on x only)
dz/dt = C*x + D @ z
```

Eliminating `z` exactly (variation of constants) gives a closed
integro-differential equation for `x` alone:

```
dx/dt = A*x(t) + ∫₀ᵗ K(t-s)·x(s) ds + B @ expm(D·t) @ z0 + f(t)
```

with the **exact memory kernel** `K(u) = B @ expm(D·u) @ C`. This is
precisely the two features Chorin, Hald & Kupferman attribute to
eliminating hidden state: a memory term, and a remainder depending on the
hidden initial condition `z0`. The scalar exponential recovery kernel used
elsewhere in this repository (`exp[-∫ₛᵗ r(v)dv]`, constant-rate case
`exp[-r(t-s)]`) is the `n_z=1` special case of this `K` — this module
generalizes it to an arbitrary hidden dimension and derives it from first
principles rather than positing it, matching Astra's request to work
toward "gemeinsame Operatorstrukturen" (shared operator structures) rather
than a collection of unrelated examples. `exact_memory_kernel` is checked
against an independently written closed form both for `n_z=1` (single
exponential) and `n_z=2` with diagonal `D` (sum of two exponentials) — a
concrete instance of Astra's "Zwei- und Dreizustandsmodelle mit
analytischer Referenz" request.

## Three variants, four comparison metrics

- **exact** — the full `(x,z)` system, numerically integrated to high
  precision (the one available ground truth; the memory equation above is
  an exact rewriting of the same dynamics, not an independently
  verifiable trajectory).
- **memoryless** — `dx/dt = A*x(t) + f(t)`, dropping the hidden coupling
  entirely.
- **finite_memory** — the exact memory equation with the integral
  truncated to a trailing window `W` and the `B @ expm(D·t) @ z0` term
  dropped (solved by a fixed-step explicit Euler scheme with a
  precomputed kernel lookup table — first-order accurate, adequate for
  this comparison, not a high-precision claim).

Per Astra's explicit request, comparison goes beyond mean state error: the
trajectory's minimum (value AND time) is found by continuous optimization
on a cubic-spline interpolant — not a grid `argmin` (the same discipline
`viability.rate_dependent_buffer` adopted after its Paket-6 grid-search
bug) — and the first boundary-crossing time is found by root-finding on
the same interpolant.

## Regression check: does the reduction actually match?

With the hidden state starting at `z0=0` and a memory window covering the
*entire* simulated interval, both simplifications the finite-memory
variant makes (dropping the `z0` term, truncating the window) are switched
off — so it should closely reproduce the exact trajectory. It does: max
deviation `< 0.01` over a 20-time-unit run (`verify_linear_memory_projection.py`,
`finite_memory_matches_exact_when_window_covers_full_history`), confirming
both the kernel derivation and the Euler solver are correct, independent
of the illustrative example below.

## Worked example: does partial memory actually help?

A stable, moderately-coupled system (`A=-0.5`, `B=C=0.6`, `D=-1.0`,
eigenvalues `{-0.1, -1.4}`, so genuinely stable — not merely slowly
divergent) driven by a Gaussian forcing pulse, memory window `W=2.0`
(twice the kernel's own decay time of 1.0):

| Metric | memoryless | finite_memory (W=2.0) | exact |
|---|---:|---:|---:|
| Mean absolute error | 0.711 | **0.149** | — |
| Minimum value | −3.069 | **−3.006** | −2.946 |
| Minimum time | 5.543 | **5.630** | 5.626 |
| Boundary crossing (b=−2.9) | 5.336 | **5.439** | 5.495 |

The finite-memory approximation wins on **all four** metrics, not just
the mean — including getting the crossing time within 0.06 time units of
the true value, versus 0.16 for dropping the memory term entirely.
Interesting direction of the memoryless error here: it OVERESTIMATES the
dip's severity (predicts a deeper minimum, reached earlier, and an earlier
boundary crossing) rather than missing it — a "false alarm" failure mode,
not a "missed danger" one. Both directions are real possibilities
depending on system parameters; this is reported as the direction this
particular worked example actually produced, not selected to fit a
preferred narrative.

## Scope

This module handles LINEAR systems only (the elimination step relies on
`z`'s dynamics being linear in `x` and `z`); nonlinear hidden-state
elimination is a substantially harder problem (the actual subject of the
broader Mori-Zwanzig / optimal-prediction literature) and is out of scope
here. The finite-memory solver is first-order-accurate explicit Euler,
adequate for the comparisons in this document but not a high-precision
integrator — a stiffer or faster-decaying kernel would need a finer step
or a proper implicit/quadrature scheme.
