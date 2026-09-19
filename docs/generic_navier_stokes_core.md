# GENERIC ↔ Navier–Stokes viscous dissipation (Milestone 38)

**Status:** review package only — not yet linked from README/GLOSSARY as accepted "core".
Johann-OK required before any core promotion.

## What this is

Typed Python helpers for a **finite-dimensional two-cell** reduction of viscous
momentum exchange in the GENERIC formalism, with friction matrix

\[
M = \zeta\, T\, a a^{\mathsf T},\qquad
a = (1,-1,-v_1,v_2).
\]

```text
src/scoped_correspondence/
  coupling/
    core.py                      # UNCHANGED — GENERIC check; CALL only
    generic_navier_stokes.py     # NEW — two_cell_viscous_example
```

**Important:** `M` is the GENERIC *friction* / dissipative metric. It is
**NOT** `A_ij` (local dynamic influence) and **NOT** `L_ij` (Onsager
transport). Those remain separate types in `coupling.core` (FORMALISM.md §6).

M38 does **not** ship a continuum Navier–Stokes PDE solver, does **not**
mutate `coupling/core.py`, does **not** rewrite package-root
`scoped_correspondence/__init__.py`, and does **not** edit `FORMALISM.md` or
`coupling_layer_afet.md`. Submodule wiring is via `coupling/__init__.py` only.

## Sources (attribution)

| Source | Role | Notes |
|---|---|---|
| Grmela & Öttinger, PRE **56**, 6620 (1997), DOI 10.1103/PhysRevE.56.6620 | GENERIC formalism (Part I) | APS abstract is GENERIC, **not** claimed to be NS |
| Öttinger & Grmela, PRE **56**, 6633 (1997), DOI 10.1103/PhysRevE.56.6633 | GENERIC illustrations (Part II) | APS abstract is GENERIC, **not** claimed to be NS |
| Morrison, Phys. Lett. A **100**, 423 (1984), DOI 10.1016/0375-9601(84)90635-2 | Bracket formulation for irreversible classical fields | metriplectic / NS dissipation ancestry |
| Barham, Morrison & Zaidni, CNSNS **145**, 108683 (2025), DOI 10.1016/j.cnsns.2025.108683 | Thermodynamically consistent 1D thermal-fluid / NS–Fourier metriplectic discretization | **NS link** |

## Mapping

| Object | Formula | API |
|---|---|---|
| degeneracy vector | \(a=(1,-1,-v_1,v_2)\) | `two_cell_viscous_example` |
| energy gradient | \(\nabla E=(v_1,v_2,1,1)\) | same |
| entropy gradient | \(\nabla S=(0,0,1/T,1/T)\) | same |
| Poisson | \(J=0\) | same |
| friction | \(M=\zeta T\, a a^{\mathsf T}\) (**not** A_ij / L_ij) | same |
| structure check | CALL `check_generic_structure` | `coupling.core` unchanged |

## Worked example

At \(v_1=3\), \(v_2=1\), \(T=300\), \(\zeta=0.5\):

- \(a\cdot\nabla E=0\)
- \(M\nabla S=-a=(-1,1,3,-1)\)
- \(\dot p_1=-\zeta(v_1-v_2)=-1\)
- entropy production \(\zeta(v_1-v_2)^2/T=0.0066\ldots\)
- `check_generic_structure` → `ok=True`, all residuals `0.0`
- control \(v_1=v_2\) ⇒ \(M\nabla S=0\)

## Illustrative continuum viscosity

\(\eta=0.005\,\mathrm{Pa\cdot s}\) via \(\zeta=\eta A/\Delta y\) is
**illustrative only** — not an empirical calibration of the two-cell toy.

## Out of scope

- Continuum / 3D Navier–Stokes PDE solver
- Claiming Grmela/Öttinger APS abstracts *are* Navier–Stokes
- Equating GENERIC friction `M` with `A_ij` or `L_ij`
- Editing `coupling/core.py`, package-root `__init__.py`, `FORMALISM.md`,
  `coupling_layer_afet.md`
