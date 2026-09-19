# Panarchy / Adaptive-Cycle as Cusp Extension (Milestone 35)

**Status:** optional / review package. Not a new Baustein; submodule-local
extension of `dynamics`. Package-root `scoped_correspondence/__init__.py`
is **not** rewritten. `dynamics/core.py` is **not** edited (CALL only).

## Retraction history — V≡Panarchy≡Onsager-L

An earlier (discarded) reading identified the mathematical cusp potential
`U(x) = x⁴/4 − a x²/2 − b x` with Holling/Panarchy “potential” and with
Onsager’s linear irreversible-thermodynamics matrix `L`. That triple
identity

```text
V ≡ Panarchy ≡ Onsager-L
```

is a **hard reject** of the scoped-correspondence review package
(`ALREADY_DONE.md` / research hard bans). It is **not** revived here.

| Layer | Object | Role in M35 |
|---|---|---|
| `dynamics.core` | corrected cubic `τ ẋ = −x³ + a x + b`; discriminant `4a³−27b²` | **formalization** (CALL) |
| Panarchy / adaptive cycle | Holling qualitative phases; Zwick cusp reading | **interpretation labels only** |
| Onsager `L` | linear irreversible thermo (thermo / GENERIC) | **out of scope; not identified** |

M35 is an **interpretation layer** over the existing cusp API: fold /
hysteresis geometry as the mathematical image of conservation→release.
There is **no proven ecological claim**. Zwick & Hughes 2017 is
**Abstract-verified**; fulltext was not seen.

**Mandatory fence (verbatim):**
does NOT revive V≡Panarchy≡Onsager-L; interpretation layer only, no proven
ecological claim; Abstract-verified Zwick 2017 fulltext not seen.

## What this is

```text
src/scoped_correspondence/
  dynamics/
    core.py            # UNCHANGED — fixed_points + CubicNormalForm.discriminant
    panarchy_cusp.py   # NEW — fold_thresholds + hysteresis_sweep
```

## Mapping

| Source | Claim / formula | API | Notes |
|---|---|---|---|
| cusp equilibria (FORMALISM.md §5) | `x³ − a x − b = 0` via `fixed_points` | `hysteresis_sweep` | CALL only |
| cusp discriminant | `Δ = 4a³ − 27b²` via `CubicNormalForm.discriminant` | internal + verify | CALL only |
| bifurcation set | `b_± = ±√(4a³/27)` | `fold_thresholds` | closed form of `Δ=0` |
| Zwick & Hughes 2017 DOI 10.1145/3145574.3145591 | adaptive cycle ↔ cusp fold/hysteresis | interpretation | Abstract-verified; fulltext not seen |
| Holling 1973 DOI 10.1146/annurev.es.04.110173.000245 | resilience / adaptive-cycle **context** | docs only | qualitative; no ODE in Holling |

## Formulas

### Fold thresholds

For `a > 0`, the cusp bifurcation set is `4a³ − 27b² = 0`, hence

\[
b_\pm(a) = \pm\sqrt{\frac{4a^3}{27}}.
\]

Worked example `a = 3`:

- `b_± = ±2`  (note: a research draft once wrote `±2/√3≈±1.1547` by dropping
  the factor `a^{3/2}=3√3` in `(2/√27)a^{3/2}`; the correct value is `±2`).
- At `b = 0`, `fixed_points(3, 0) → {−√3, 0, +√3}`.

Consistency check: `CubicNormalForm(3, ±2).discriminant() ≈ 0`.

### Hysteresis sweep

`hysteresis_sweep(a, b_values)` tracks a quasi-static **stable** branch under
a slow `b`-path by nearest-neighbour continuation among
`fixed_points(a, b)` stable roots (`S_rec = (3x²−a)/τ > 0`). When the tracked
branch disappears at a fold, the state **jumps** to the remaining stable
root. Jumps occur at the fold thresholds, **not** at `b = 0`.

Classic loop for `a = 3`, `b: −2 → +2 → −2`:

- forward: stay on lower branch until right fold `b = +2`, then jump up;
- return: stay on upper branch until left fold `b = −2`, then jump down;
- crossing `b = 0` inside the bistable region does **not** jump.

### Control — vary `a` at fixed `b` inside folds

`control_path_no_fold_crossing(a_values, b)` requires
`|b| < √(4a³/27)` for every sample. Discriminants stay positive; the
tracked branch varies continuously — **no jump without fold crossing**.

## Sources

- Holling, C. S. (1973). Resilience and Stability of Ecological Systems.
  *Annu. Rev. Ecol. Syst.* **4**, 1–23.
  DOI [10.1146/annurev.es.04.110173.000245](https://doi.org/10.1146/annurev.es.04.110173.000245)
  — **context only** (qualitative).
- Zwick, M. & Hughes, J. (2017). Formalizing the Panarchy Adaptive Cycle
  with the Cusp Catastrophe. *Proc. CSS*.
  DOI [10.1145/3145574.3145591](https://doi.org/10.1145/3145574.3145591)
  — Abstract-verified; fulltext not seen.

## Non-goals

- Do **not** revive `V≡Panarchy≡Onsager-L`.
- Do **not** introduce a `V_panarchy` symbol or mutate thermo / Onsager-L.
- Do **not** edit `dynamics/core.py` or package-root `__init__.py`.
- Do **not** claim a proven ecological theorem beyond cusp geometry.
