# Chapman–Enskog / BGK transport closure (Milestone 40)

**Sources.**

* P. L. Bhatnagar, E. P. Gross, M. Krook, *A Model for Collision Processes in
  Gases. I. Small Amplitude Processes in Charged and Neutral One-Component
  Systems*, Phys. Rev. **94**, 511–525 (1954).
  DOI [10.1103/PhysRev.94.511](https://doi.org/10.1103/PhysRev.94.511)
* L. H. Holway, Jr., *New Statistical Models for Kinetic Theory: Methods of
  Construction*, Phys. Fluids **9**, 1658–1673 (1966).
  DOI [10.1063/1.1761920](https://doi.org/10.1063/1.1761920)

This milestone adds `scoped_correspondence.closure.chapman_enskog` — a
**separate** module implementing the **BGK route** to first-order
Chapman–Enskog transport coefficients. It does **not** edit
`closure/core.py` or `closure/error_bounds.py`, and does **not** implement
the Chapman–Cowling hard-sphere viscosity formula.

## Structural analogy (NOT identity)

Kinetic theory closes the Boltzmann hierarchy by projecting onto hydrodynamic
moments and expressing higher fluxes through lower ones — the same *pattern*
as exact/approximate macro-closure:

| Closure API | Kinetic analogue |
|-------------|------------------|
| Micro kernel / generator `P` | Boltzmann / BGK collision operator |
| Projection `C` | Moments `(ρ, u, T)` |
| Macro generator `Q` | Euler / Navier–Stokes |
| Exact closure `PC = CQ` | Local equilibrium (Euler; `τ → 0`) |
| Defect `δ_cl` / `closure_error` | Knudsen / nonequilibrium fluxes (`μ`, `κ`) |

This is a **structural analogy** to `is_exact_closure` / `closure_error`.
It is **not** identity with M11 generator lumpability, and **not** identity
with M21 Michel–Siegle reduction error bounds.

## What is implemented

| API | Formula |
|-----|---------|
| `bgk_transport_coefficients(p, tau, m, k_B=1)` | `μ = p·τ`, `κ = (5/2)(k_B/m)·p·τ` |
| `prandtl_number(mu, kappa, c_p)` | `Pr = μ·c_p / κ` |
| `relaxation_time_from_viscosity(mu, p)` | `τ = μ / p` |
| `mean_thermal_speed(T, m, k_B)` | `⟨v⟩ = √(8 k_B T / (π m))` (sanity only) |
| `mean_free_path_estimate(⟨v⟩, τ)` | `λ ≈ ⟨v⟩·τ` (order-of-magnitude) |

### BGK Prandtl number

With monatomic specific heat `c_p = (5/2)(k_B/m)`,

\[
\kappa = c_p · μ \quad\Rightarrow\quad Pr_{\mathrm{BGK}} = 1
\]

exactly. The physical monatomic Prandtl number is `Pr = 2/3`, so BGK overshoots
by the factor `3/2 = 1.5` (Holway 1966 motivates ES-BGK to restore `Pr = 2/3`).

### Hand-checkable unit example

`p = τ = m = k_B = 1`:

* `μ = 1`, `κ = 2.5`
* `c_p = 5/2` → `Pr = 1.0` exactly
* vs physical `2/3`: factor `1.5`

### Air order-of-magnitude sanity (not a precision claim)

At `T = 300 K`, `p = 101325 Pa`, dry-air viscosity `μ ≈ 1.846×10⁻⁵ Pa·s`:

* `τ = μ/p ≈ 1.8219×10⁻¹⁰ s`
* With dry-air molar mass `≈ 28.97 g/mol`, `⟨v⟩ ≈ 468.3 m/s`
* `λ ≈ ⟨v⟩·τ ≈ 8.53×10⁻⁸ m` (mean-free-path **order of magnitude** only)

### Control / degenerate case

`τ → 0` ⇒ `μ → 0` and `κ → 0` (local-equilibrium / Euler limit; exact
hydrodynamic closure in the Knudsen sense).

## Explicitly out of scope

* Chapman–Cowling hard-sphere `η = 5/(16√π) √(mT)/d²` (or equivalent)
* Full Boltzmann collision integral / numerical CE solvers
* Claiming identity with M11 lumpability or M21 L1/TV error bounds
* Editing `closure/core.py`, `closure/error_bounds.py`, or package-root
  `__init__.py`
