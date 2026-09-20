# Percolation / Kesten / Bethe-tree Branching (Milestone 32)

**Status:** review package only — not yet linked from README/GLOSSARY as accepted "core".
Johann-OK required before any core promotion.

## What this is

Exact bond-percolation / branching-process formulas on the infinite
**Bethe tree** (Cayley tree) with branching factor \(m\): critical occupation
probability \(p_c = 1/m\), extinction fixed point
\(Q = (1-p+pQ)^m\), and percolation probability \(\theta = 1-Q^*\).
Mapping: Fisher & Essam (1961), Kesten (1980).

```text
src/scoped_correspondence/
  percolation/
    __init__.py
    core.py
```

M32 does **not** run Monte-Carlo on \(\mathbb{Z}^2\), does **not** use
Union-Find / Newman–Ziff, and does **not** mutate `dynamics/`, `membership/`,
other Bausteine, package-root `__init__.py`, or `FORMALISM.md`.

## Mandatory warnings (verbatim)

**WARNING — threshold kinship:**
Percolation and cusp dynamics involve distinct objects and parameter meanings. No identity of their thresholds or transfer of numerical values is asserted. A comparison of local fixed-point or bifurcation structures requires a separately stated scope, construction, and derivation.

**WARNING — discarded README 1/16:**
If any computed value lands near 1/16, mark explicitly as coincidence vs the discarded README '1/16' value — do not leave uncommented.
In particular `critical_probability_tree(16) = 0.0625 = 1/16` is the Bethe \(p_c\) for \(m=16\) only — **coincidence** vs the discarded universal ecosystem claim in README Status ("universelle Zahlenwerte wie … 1/16").

## Mapping

| Source | Claim / formula | API | Notes |
|---|---|---|---|
| Fisher & Essam 1961 DOI 10.1063/1.1703745 | Bethe / branching \(p_c = 1/m\) | `critical_probability_tree` | `ScopeViolationError` if \(m<1\) |
| Kesten 1980 DOI 10.1007/BF01197577 | percolation / critical phenomena context | module sources | no \(\mathbb{Z}^2\) MC |
| branching-process PGF | \(Q=(1-p+pQ)^m\); smallest \(Q^*\in[0,1]\) | `extinction_probability` | start \(Q_0=0\) |
| survival | \(\theta=1-Q^*\) | `percolation_probability` | |

## Formulas

### Critical probability

\[
p_c(m) = \frac{1}{m},\qquad m \ge 1.
\]

Examples: \(m=2\Rightarrow p_c=1/2\); \(m=4\Rightarrow p_c=1/4\).

### Extinction fixed point

Offspring PGF \(f(s)=(1-p+ps)^m\). Iterate from documented start
\(Q_0 = 0\) (`EXTINCTION_Q0`) until residual \(\le\) `tol`:

\[
Q_{n+1} = (1-p+p Q_n)^m
\to Q^\*.
\]

For \(p \le p_c = 1/m\) the branching-process theorem gives \(Q^*=1\) exactly (returned without iteration). Returns `(Q_star, iters, residual)` with
\(\mathrm{residual}=|Q^\*-(1-p+pQ^\*)^m|\).

### Percolation probability

\[
\theta(p,m) = 1 - Q^\*(p,m).
\]

## Worked example \(m=2\)

| \(p\) | Algebraic | Numeric | Notes |
|---|---|---|---|
| \(p_c=0.5\) | \(p_c=1/2\) exact | `0.5` | |
| \(p=0.5\) | \(Q^*=1\), \(\theta=0\) | exact | at threshold |
| \(p=0.6\) | \(Q=(0.4+0.6Q)^2\) → \(9Q^2-13Q+4=0\) → roots \(\{1,4/9\}\); physical \(Q^*=4/9\), \(\theta=5/9\) | \(Q^*\approx 0.444444\ldots\), \(\theta\approx 0.555555\ldots\); \(\lvert\mathrm{diff}\rvert<10^{-9}\) | both algebraic **and** numeric |
| \(p=0.8\) | \(Q^*=((1-p)/p)^2=(1/4)^2=1/16\), \(\theta=15/16\) | \(Q^*=0.0625\), \(\theta=0.9375\) | **COINCIDENCE:** \(Q^*=1/16\) is Bethe algebra only — coincidence vs the discarded README '1/16' value — do not identify them. |

Also \(m=4\Rightarrow p_c=0.25\).

## Hand-checkable verification

`verification/verify_percolation_core.py` covers at minimum:

1. `critical_probability_tree(2)==0.5`, `(4)==0.25`; `m<1` raises.
2. \(m=2,p=0.6\): \(Q^*\approx 4/9\), \(\theta\approx 5/9\); algebraic residual of quadratic; \(\lvert\mathrm{num}-4/9\rvert<10^{-9}\).
3. \(m=2,p=0.5\): \(Q^*=1\), \(\theta=0\).
4. \(m=2,p=0.8\): \(Q^*=1/16\), \(\theta=15/16\) — **coincidence** vs discarded README '1/16' (must be marked, not left uncommented).
5. Both mandatory warnings present verbatim in module / API / docs / JSON.
6. `m=16` → \(p_c=1/16\) coincidence note vs discarded README value.

## Out of scope

Monte-Carlo on \(\mathbb{Z}^2\); Union-Find / Newman–Ziff; mutation of
`dynamics/`, `membership/`, other Bausteine, package-root `__init__.py`,
`FORMALISM.md`; any claim that percolation \(p_c\) is the dynamics cusp
threshold \(4a^3>27b^2\); any identification of Bethe \(1/16\) with the
discarded universal README value.
