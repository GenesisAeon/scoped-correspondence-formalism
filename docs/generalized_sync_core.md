# Generalized / Drive–Response Synchronisation (Milestone 39)

**Status:** review package only — Johann-OK required before any "core" promotion.

**Source:** L. M. Pecora & T. L. Carroll, *Synchronization in chaotic systems*,
Phys. Rev. Lett. **64**, 821–824 (1990), DOI `10.1103/PhysRevLett.64.821`.

## What this is

A **mathematical** drive–response synchronisation criterion (conditional
Lyapunov exponents / CLE) for coupled dynamical systems, exported under
`coupling` as `generalized_sync.py`.

This is **not** Luhmann sociology. Historical inspiration for the project
mentioned "structural coupling"; Pecora–Carroll is an independent dynamical
systems theory that happens to use an everyday word in the same neighbourhood.
Docstring / module stance:

> mathematische Fassung im Sinne dynamischer Mitführung, KEINE
> Luhmann-Soziologie, KEINE Gleichsetzung.

```text
src/scoped_correspondence/
  coupling/
    generalized_sync.py   # NEW (M39)
    __init__.py           # wired exports only
```

M39 does **not** mutate `coupling/core.py`, `dynamics/contraction.py`, or
package-root `scoped_correspondence/__init__.py`.

## Mandatory bridge note (verbatim)

> Das CLE<0-Kriterium hier ähnelt strukturell der bereits gemergten
> Kontraktionsanalyse (M14, `dynamics/contraction.py`, Lohmiller &
> Slotine 1998) — beide sind Vorzeichenkriterien an einer
> Variationsgleichung. Das ist KEINE Identität: M14 prüft globale
> metrische Kontraktion EINES Systems, dieses Modul prüft
> Drive-Response-Synchronisation ZWISCHEN zwei gekoppelten Systemen in
> `coupling`. Eine mögliche künftige `correspondence`-Brücke zwischen
> den beiden Kriterien ist denkbar, aber HIER NICHT behauptet oder
> implementiert — offener, unbewiesener Kandidat, analog zum
> dokumentierten Turing↔dynamics-Brückenkandidaten in
> `pattern_formation/core.py`.

## Mapping

| Source | Claim / formula | API | Notes |
|---|---|---|---|
| Pecora & Carroll 1990 | all CLE \(<0\) ⇒ response syncs to drive | `conditional_lyapunov_linear`, `linear_drive_response_map` | linear special cases only |
| scalar variational \(\delta\dot y = a\,\delta y\) | CLE \(= a\); sync \(\Leftrightarrow a<0\) | `conditional_lyapunov_linear(a)` | |
| drive \(\dot x=-x\), response \(\dot y=-ky+cx\) | \(\varphi=c/(k-1)\) (\(k\neq 1\)), CLE \(=-k\) | `linear_drive_response_map(c,k)` | `ScopeViolationError` if \(k=1\) |

## Formulas

### Conditional Lyapunov (linear scalar)

\[
\delta\dot y = a\,\delta y \quad\Rightarrow\quad \mathrm{CLE}=a.
\]

Asymptotic synchronisation of the response variation iff \(a<0\).

### Linear drive–response map

Drive \(\dot x = -x\), response \(\dot y = -k y + c x\). Ansatz \(y=\varphi x\):

\[
\varphi = \frac{c}{k-1}\quad(k\neq 1),\qquad \mathrm{CLE}=-k.
\]

- **Map exists** (`map_exists`): formal \(\varphi\) is defined (\(k\neq 1\)).
- **Sync achieved** (`sync_achieved`): \(\mathrm{CLE}<0\) (i.e. \(k>0\)).

These are **separate fields**. A formal map can exist without synchronisation.

### Worked example (from verify script)

- \(c=4\), \(k=3\): \(\varphi=2\), CLE \(=-3<0\) → `map_exists=True`, `sync_achieved=True`.
  Hand check: \(\frac{d}{dt}(y-2x)=-3(y-2x)\).
- \(c=4\), \(k=-1\): \(\varphi=-2\), CLE \(=+1>0\) → `map_exists=True`, `sync_achieved=False`.
- \(k=1\): `ScopeViolationError` (denominator vanishes).

## Explicitly out of scope

- Chaotic / high-dimensional examples (e.g. Lorenz drive).
- Mutation of `coupling/core.py` or `dynamics/contraction.py`.
- Claiming CLE \(<0\) ≡ M14 global contraction rate.
- Luhmann quotations or sociological justification.
- Identification with GENERIC \(L,M\) or \(A_{ij}\equiv L_{ij}\).

## Verification

```bash
PYTHONPATH=src python verification/verify_generalized_sync_core.py
```

Writes `verification/verify_generalized_sync_core_results.json` with the
verbatim `BRIDGE_NOTE` text field and numeric fields from the script run.
