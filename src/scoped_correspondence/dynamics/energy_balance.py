"""Two-layer energy balance model, calibrated to real CO2 forcing and temperature (Milestone 45).

NONSTATIONARY_ROADMAP.md package 5b, response to
prompts/Answers/nicht_stationäre_Treiber/SCF_Nichtstationaere_Treiber_und_Kippen.md
(Astra, 2026-09-21) section 5.4: "Klima -- ein getriebenes Zweischichten-
Energiebilanzmodell", a genuine climate-domain mechanistic model instead
of a bare linear-trend fit.

Model (Geoffroy et al. 2013, J. Climate 26:1841-1857, DOI 10.1175/JCLI-D-12-00195.1):

    C_s * dT_s/dt = F(t) - alpha*T_s - gamma*(T_s - T_d)
    C_d * dT_d/dt = gamma*(T_s - T_d)

T_s: surface temperature anomaly; T_d: deep-ocean temperature anomaly;
F(t): radiative forcing; alpha: climate feedback parameter; gamma:
surface-to-deep heat exchange coefficient; C_s, C_d: heat capacities.
Linear in the temperatures for fixed coefficients, yet produces delayed,
curved responses to a changing forcing -- no tipping point is built into
this form.

Forcing: CO2-only radiative forcing via the standard logarithmic formula
(Myhre et al. 1998, Geophys. Res. Lett. 25:2715-2718, DOI 10.1029/98GL01908):

    F(t) = 5.35 * ln(CO2(t) / CO2_ref)

using REAL Mauna Loa annual-mean CO2 (data/noaa_mauna_loa_co2_annual_1959_2025.txt,
NOAA GML, public domain) as CO2(t), CO2_ref = CO2 at the first available
year (1959).

IMPORTANT SCOPE LIMITATION: this is CO2-ONLY forcing. Real historical
radiative forcing also includes other well-mixed greenhouse gases,
aerosols (a significant, uncertain, partly-cooling contribution), and
volcanic/solar variability -- all omitted here. The fitted parameters
(C_s, C_d, alpha, gamma) therefore do NOT claim to recover the true
physical climate-system constants; they are calibrated to compensate for
the omitted forcings as best a CO2-only proxy can, and are expected to be
poorly identified individually from a single historical temperature
record alone (a well-known limitation in real climate science -- see
the identifiability caveat in ``fit_energy_balance_model``'s docstring).

REFERENCE-LEVEL CAVEAT: F is referenced to CO2 in the first available year
(1959), while the NOAA temperature series is a departure from the
1901-2000 mean -- these are two different baselines, not reconciled here.
A shift in that baseline is not fully absorbed by the free T0 parameter
alone (it would also require an additive forcing offset, since shifting
the temperature reference by delta requires shifting F by alpha*delta to
describe the same physics) -- flagged per external review (Astra,
2026-09-21) as an open modeling simplification, not fixed by adding a
6th free parameter given the already weak identifiability documented
below.

CORRECTION (2026-09-21, external review by Astra): the originally shipped
fit (RMSE 0.154 degC, unconstrained log-parametrized ``method="lm"``, 4
generic starting points) was independently found to sit in a poor local
optimum -- the SAME code, run in a different environment (newer
scipy/numpy), converged to RMSE 0.119 from the identical starting points,
and a more thorough refit reached RMSE ~0.090. This is now fixed by (a)
switching the optimizer's inner loop from ``solve_ivp`` (adaptive-step,
mildly non-smooth as an optimization objective) to an EXACT
matrix-exponential propagation of the same linear ODE under the same
piecewise-linear forcing (see ``_integrate_Ts_exact``; cross-checked
against ``_integrate_Ts``'s ``solve_ivp`` call to confirm they describe
the same physics), and (b) using ``scipy.optimize.least_squares`` with
``method="trf"`` and explicit, physically-motivated PARAMETER BOUNDS
(``PARAM_BOUNDS`` below) from several diverse starts, which now converges
to the SAME optimum from every tested start (a real robustness fix, not
just a lucky rerun). The unconstrained best fit found by external review
pushes ``alpha`` to a near-zero, unphysical value (~4.5e-5 W/m^2/K, i.e.
almost no radiative damping) -- a textbook overfitting/identifiability
pathology, not a better climate model. ``PARAM_BOUNDS`` excludes that
degenerate region; ``EnergyBalanceFitResult.at_bound`` reports whether the
returned fit still saturates a bound, which -- if true -- IS the honest
identifiability finding to report, not something to silently work around.
See docs/energy_balance.md for the corrected numbers and revised
(substantially weakened) aerosol-unmasking interpretation.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
from scipy.integrate import solve_ivp
from scipy.interpolate import interp1d
from scipy.linalg import expm
from scipy.optimize import least_squares

from scoped_correspondence.errors import ScopeViolationError

SOURCE = (
    "Geoffroy, Saint-Martin, Olivie, Voldoire, Bellon & Tyteca 2013, J. Climate "
    "26:1841-1857, DOI 10.1175/JCLI-D-12-00195.1 (two-layer energy balance model); "
    "Myhre, Highwood, Shine & Stordal 1998, Geophys. Res. Lett. 25:2715-2718, "
    "DOI 10.1029/98GL01908 (CO2 logarithmic forcing formula)."
)

CO2_FORCING_COEFFICIENT = 5.35  # Myhre et al. 1998, W/m^2

DATA_PROVENANCE_NOTE = (
    "Real per-row data: data/noaa_mauna_loa_co2_annual_1959_2025.txt (NOAA GML "
    "Mauna Loa annual-mean CO2, public domain) and "
    "data/noaa_global_temp_anomaly_1880_2025.csv (see "
    "data/real_data_manifest.json). CO2-ONLY forcing is a major documented "
    "simplification -- see module docstring."
)

# Physically-motivated bounds excluding a near-zero, unphysical climate
# feedback (alpha): Geoffroy et al. 2013's own CMIP5-model fits cluster
# roughly in this general order of magnitude for the fast-response mode.
# This is a plausibility bound, not a literature-matched point estimate --
# see the module docstring's CORRECTION note for why an unconstrained fit
# is rejected (it saturates near alpha=0, a modeling pathology).
PARAM_BOUNDS: Dict[str, Tuple[float, float]] = {
    "C_s": (0.5, 50.0),
    "C_d": (5.0, 500.0),
    "alpha": (0.3, 3.0),
    "gamma": (0.05, 5.0),
    "T0": (-2.0, 2.0),
}


def co2_radiative_forcing(co2_ppm: np.ndarray, co2_ref: float) -> np.ndarray:
    """F = 5.35 * ln(CO2/CO2_ref) (Myhre et al. 1998)."""
    co2_ppm = np.asarray(co2_ppm, dtype=float)
    if co2_ref <= 0:
        raise ScopeViolationError(f"co2_radiative_forcing: co2_ref must be > 0; got {co2_ref!r}")
    if np.any(co2_ppm <= 0):
        raise ScopeViolationError("co2_radiative_forcing: all CO2 values must be > 0")
    return CO2_FORCING_COEFFICIENT * np.log(co2_ppm / co2_ref)


def load_annual_co2(path: str | Path) -> Dict[int, float]:
    """Load NOAA GML's annual-mean CO2 text file (whitespace-separated, '#'-comment header)."""
    p = Path(path)
    out: Dict[int, float] = {}
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) < 2:
            continue
        out[int(parts[0])] = float(parts[1])
    if not out:
        raise ScopeViolationError("load_annual_co2: no data rows found")
    return out


@dataclass(frozen=True)
class EnergyBalanceParams:
    C_s: float
    C_d: float
    alpha: float
    gamma: float
    T0: float

    def to_dict(self) -> Dict[str, float]:
        return {"C_s": self.C_s, "C_d": self.C_d, "alpha": self.alpha, "gamma": self.gamma, "T0": self.T0}


@dataclass(frozen=True)
class EnergyBalanceFitResult:
    params: EnergyBalanceParams
    years: Tuple[int, ...]
    predicted_Ts: Tuple[float, ...]
    observed_Ts: Tuple[float, ...]
    rmse: float
    optimizer_success: bool
    optimizer_cost: float
    n_starts_tried: int
    at_bound: Tuple[str, ...]
    solve_ivp_cross_check_max_diff: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "params": self.params.to_dict(),
            "years": list(self.years),
            "predicted_Ts": list(self.predicted_Ts),
            "observed_Ts": list(self.observed_Ts),
            "rmse": self.rmse,
            "optimizer_success": self.optimizer_success,
            "optimizer_cost": self.optimizer_cost,
            "n_starts_tried": self.n_starts_tried,
            "at_bound": list(self.at_bound),
            "solve_ivp_cross_check_max_diff": self.solve_ivp_cross_check_max_diff,
        }


def _integrate_Ts(
    t: np.ndarray, F_interp, C_s: float, C_d: float, alpha: float, gamma: float, T0: float
) -> np.ndarray:
    """Adaptive-step solve_ivp integration -- used ONLY as an independent cross-check
    on ``_integrate_Ts_exact`` (see that function's docstring for why it, not this
    one, drives the optimizer)."""

    def rhs(tt, y):
        Ts, Td = y
        F = float(F_interp(tt))
        dTs = (F - alpha * Ts - gamma * (Ts - Td)) / C_s
        dTd = (gamma * (Ts - Td)) / C_d
        return [dTs, dTd]

    sol = solve_ivp(rhs, (float(t[0]), float(t[-1])), [T0, T0], t_eval=t, rtol=1e-9, atol=1e-11, max_step=0.5)
    if not sol.success:
        raise ScopeViolationError(f"_integrate_Ts: solve_ivp failed: {sol.message}")
    return sol.y[0]


def _integrate_Ts_exact(F_vals: np.ndarray, C_s: float, C_d: float, alpha: float, gamma: float, T0: float) -> np.ndarray:
    """Exact matrix-exponential propagation of the SAME linear ODE, one unit
    time-step (calendar year) at a time, under piecewise-LINEAR forcing
    between consecutive annual F values.

    This augments the 2-state (T_s, T_d) linear system with 2 extra states
    that make the piecewise-linear forcing itself part of a single, larger
    LINEAR autonomous system over each unit step -- a standard trick (the
    same forcing is exactly representable this way because it is linear in
    t within each step) that lets ``scipy.linalg.expm`` propagate the exact
    solution with no discretization error and no adaptive-step non-smoothness.

    Used as the optimizer's objective in ``fit_energy_balance_model``
    instead of ``_integrate_Ts`` (external review, Astra 2026-09-21): an
    adaptive-step black-box solver's tiny step-to-step irregularities were
    confusing the optimizer into stopping at a poor local optimum in some
    environments while reporting ``success=True`` in all of them --
    ``fit_energy_balance_model`` cross-checks the two integrators agree
    (``solve_ivp_cross_check_max_diff``) to confirm this is the same
    physics, not a different model.
    """
    A = np.zeros((4, 4))
    A[0, :3] = [-(alpha + gamma) / C_s, gamma / C_s, 1.0 / C_s]
    A[1, :2] = [gamma / C_d, -gamma / C_d]
    A[2, 3] = 1.0
    E = expm(A)
    state = np.array([T0, T0])
    out = [T0]
    for k in range(len(F_vals) - 1):
        state = (E @ np.r_[state, F_vals[k], F_vals[k + 1] - F_vals[k]])[:2]
        out.append(state[0])
    return np.array(out)


def fit_energy_balance_model(
    co2_path: str | Path,
    temp_path: str | Path,
    *,
    initial_guesses: List[Tuple[float, float, float, float, float]] | None = None,
    bounds: Dict[str, Tuple[float, float]] | None = None,
) -> EnergyBalanceFitResult:
    """Fit (C_s, C_d, alpha, gamma, T0) to real CO2-forced temperature via bounded least squares.

    Uses the exact matrix-exponential propagation (``_integrate_Ts_exact``)
    as the optimizer's objective, ``scipy.optimize.least_squares`` with
    ``method="trf"`` and explicit bounds (default ``PARAM_BOUNDS``), and
    several diverse starting points -- see the module docstring's
    CORRECTION note (2026-09-21) for why this replaced an earlier
    unbounded, ``solve_ivp``-driven fit that was found (by external review)
    to be both poorly converged AND environment-sensitive.

    IDENTIFIABILITY CAVEAT: with CO2-only forcing and a single historical
    annual temperature record, this system remains weakly identified --
    even under the physically-motivated ``PARAM_BOUNDS``, the returned fit
    may still saturate a bound (reported in ``EnergyBalanceFitResult.at_bound``).
    A saturated bound is NOT hidden or treated as a successful fit; it is
    the honest identifiability finding this function is designed to
    surface. A profile-likelihood-style check
    (``identifiability.profile_likelihood``) would be needed to
    characterize this rigorously; not done here.
    """
    import csv

    co2 = load_annual_co2(co2_path)
    temp: Dict[int, float] = {}
    lines = [ln for ln in Path(temp_path).read_text(encoding="utf-8").splitlines() if ln and not ln.startswith("#")]
    for row in csv.DictReader(lines):
        temp[int(row["Year"])] = float(row["Departure from Average"])

    years = sorted(set(co2) & set(temp))
    if len(years) < 10:
        raise ScopeViolationError(f"fit_energy_balance_model: only {len(years)} overlapping years, need >= 10")
    if any(b - a != 1 for a, b in zip(years, years[1:])):
        raise ScopeViolationError("fit_energy_balance_model: overlapping years must be consecutive calendar years (no gaps)")

    co2_arr = np.array([co2[y] for y in years], dtype=float)
    Tobs = np.array([temp[y] for y in years], dtype=float)
    co2_ref = co2_arr[0]
    F_vals = co2_radiative_forcing(co2_arr, co2_ref)
    t = np.arange(len(years), dtype=float)

    bounds = bounds or PARAM_BOUNDS
    param_names = ["C_s", "C_d", "alpha", "gamma", "T0"]
    lb = np.array([bounds[name][0] for name in param_names])
    ub = np.array([bounds[name][1] for name in param_names])

    def model_Ts(params: np.ndarray) -> np.ndarray:
        C_s, C_d, alpha, gamma, T0 = params
        return _integrate_Ts_exact(F_vals, C_s, C_d, alpha, gamma, T0)

    def resid(params: np.ndarray) -> np.ndarray:
        return model_Ts(params) - Tobs

    if initial_guesses is None:
        initial_guesses = [
            (6.9, 97.2, 0.98, 0.70, -0.20),
            (5.0, 70.0, 1.2, 0.7, -0.2),
            (3.0, 50.0, 1.5, 0.5, -0.3),
            (10.0, 120.0, 0.8, 1.0, -0.2),
            (15.0, 200.0, 0.5, 1.5, 0.0),
            (2.0, 20.0, 2.5, 0.2, -0.5),
        ]

    best = None
    for x0_raw in initial_guesses:
        x0 = np.clip(np.array(x0_raw, dtype=float), lb, ub)
        try:
            res = least_squares(resid, x0, method="trf", bounds=(lb, ub), xtol=1e-13, ftol=1e-13, gtol=1e-13, max_nfev=5000)
        except Exception:
            continue
        rmse = float(np.sqrt(np.mean(res.fun**2)))
        if best is None or rmse < best[0]:
            best = (rmse, res)

    if best is None:
        raise ScopeViolationError("fit_energy_balance_model: all optimizer starts failed")

    rmse, res = best
    C_s, C_d, alpha, gamma, T0 = res.x
    params = EnergyBalanceParams(C_s=float(C_s), C_d=float(C_d), alpha=float(alpha), gamma=float(gamma), T0=float(T0))
    predicted = model_Ts(res.x)

    rel_tol = 1e-6
    at_bound = tuple(
        name
        for name, value in zip(param_names, res.x)
        if abs(value - bounds[name][0]) < rel_tol * max(1.0, abs(bounds[name][0]))
        or abs(value - bounds[name][1]) < rel_tol * max(1.0, abs(bounds[name][1]))
    )

    F_interp = interp1d(t, F_vals, kind="linear", fill_value="extrapolate")
    predicted_solve_ivp = _integrate_Ts(t, F_interp, C_s, C_d, alpha, gamma, T0)
    cross_check_max_diff = float(np.max(np.abs(predicted - predicted_solve_ivp)))
    if cross_check_max_diff > 1e-3:
        raise ScopeViolationError(
            f"fit_energy_balance_model: exact propagation and solve_ivp disagree by {cross_check_max_diff!r} "
            "at the fitted parameters -- they should describe the same physics"
        )

    return EnergyBalanceFitResult(
        params=params,
        years=tuple(years),
        predicted_Ts=tuple(float(x) for x in predicted),
        observed_Ts=tuple(float(x) for x in Tobs),
        rmse=rmse,
        optimizer_success=bool(res.success),
        optimizer_cost=float(res.cost),
        n_starts_tried=len(initial_guesses),
        at_bound=at_bound,
        solve_ivp_cross_check_max_diff=cross_check_max_diff,
    )


__all__ = [
    "SOURCE",
    "CO2_FORCING_COEFFICIENT",
    "DATA_PROVENANCE_NOTE",
    "PARAM_BOUNDS",
    "EnergyBalanceParams",
    "EnergyBalanceFitResult",
    "co2_radiative_forcing",
    "load_annual_co2",
    "fit_energy_balance_model",
]
