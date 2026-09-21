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
from typing import Any, Dict, List, Sequence, Tuple

import numpy as np
from scipy.integrate import solve_ivp
from scipy.interpolate import interp1d
from scipy.linalg import expm
from scipy.optimize import least_squares

from scoped_correspondence.errors import ScopeViolationError
from scoped_correspondence.identifiability.profile_likelihood import (
    classify_identifiability,
    likelihood_interval,
)
from scoped_correspondence.identifiability.profile_likelihood_nlp import (
    profile_parameter_nlp,
)

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
    optimizer_status: int
    optimizer_message: str
    initial_guesses_tried: Tuple[Tuple[float, ...], ...]
    best_initial_guess: Tuple[float, ...]

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
            "optimizer_status": self.optimizer_status,
            "optimizer_message": self.optimizer_message,
            "initial_guesses_tried": [list(g) for g in self.initial_guesses_tried],
            "best_initial_guess": list(self.best_initial_guess),
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


def integrate_energy_balance_trajectory(F_vals: np.ndarray, params: EnergyBalanceParams) -> np.ndarray:
    """Public wrapper around :func:`_integrate_Ts_exact` given an :class:`EnergyBalanceParams`.

    For MECHANISTIC_VALIDATION_ROADMAP.md package 2: projects a
    CALIB-fitted model FORWARD through real (already-known/observed) CO2
    forcing beyond the calib window -- the standard "given forcing is
    known, how well does the fitted response model project the observed
    temperature" rolling-origin forecast setup, distinct from forecasting
    the forcing itself (not attempted here).
    """
    return _integrate_Ts_exact(F_vals, params.C_s, params.C_d, params.alpha, params.gamma, params.T0)


def _load_overlap_series(co2_path: str | Path, temp_path: str | Path) -> Tuple[List[int], np.ndarray, np.ndarray]:
    """Shared loader for fit_energy_balance_model and profile_energy_balance_identifiability."""
    import csv

    co2 = load_annual_co2(co2_path)
    temp: Dict[int, float] = {}
    lines = [ln for ln in Path(temp_path).read_text(encoding="utf-8").splitlines() if ln and not ln.startswith("#")]
    for row in csv.DictReader(lines):
        temp[int(row["Year"])] = float(row["Departure from Average"])

    years = sorted(set(co2) & set(temp))
    if len(years) < 10:
        raise ScopeViolationError(f"_load_overlap_series: only {len(years)} overlapping years, need >= 10")
    if any(b - a != 1 for a, b in zip(years, years[1:])):
        raise ScopeViolationError("_load_overlap_series: overlapping years must be consecutive calendar years (no gaps)")

    co2_arr = np.array([co2[y] for y in years], dtype=float)
    Tobs = np.array([temp[y] for y in years], dtype=float)
    co2_ref = co2_arr[0]
    F_vals = co2_radiative_forcing(co2_arr, co2_ref)
    return years, Tobs, F_vals


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
    surface. See ``profile_energy_balance_identifiability`` for a rigorous
    per-parameter characterization via
    ``identifiability.profile_likelihood_nlp`` (Astra, 2026-09-21,
    MECHANISTIC_VALIDATION_ROADMAP.md package 1).

    Thin wrapper around :func:`fit_energy_balance_model_from_series` that
    loads the full real-data overlap; see that function to fit an
    arbitrary (e.g. calib-only, for rolling-origin backtesting) slice.
    """
    years, Tobs, F_vals = _load_overlap_series(co2_path, temp_path)
    return fit_energy_balance_model_from_series(years, Tobs, F_vals, initial_guesses=initial_guesses, bounds=bounds)


def fit_energy_balance_model_from_series(
    years: Sequence[int],
    Tobs: np.ndarray,
    F_vals: np.ndarray,
    *,
    initial_guesses: List[Tuple[float, float, float, float, float]] | None = None,
    bounds: Dict[str, Tuple[float, float]] | None = None,
) -> EnergyBalanceFitResult:
    """Fitting core, given already-sliced (years, Tobs, F_vals) arrays.

    Split out of :func:`fit_energy_balance_model` (MECHANISTIC_VALIDATION_ROADMAP.md
    package 2) so a rolling-origin backtest can refit on a CALIB-ONLY slice
    (years <= some origin) without needing separate CO2/temperature files
    on disk for every origin -- the caller slices the same real arrays.
    """
    years = list(years)
    Tobs = np.asarray(Tobs, dtype=float)
    F_vals = np.asarray(F_vals, dtype=float)
    if len(years) < 10:
        raise ScopeViolationError(f"fit_energy_balance_model_from_series: only {len(years)} years, need >= 10")
    if Tobs.shape != (len(years),) or F_vals.shape != (len(years),):
        raise ScopeViolationError("fit_energy_balance_model_from_series: years/Tobs/F_vals must have matching length")
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
    best_x0 = None
    for x0_raw in initial_guesses:
        x0 = np.clip(np.array(x0_raw, dtype=float), lb, ub)
        try:
            res = least_squares(resid, x0, method="trf", bounds=(lb, ub), xtol=1e-13, ftol=1e-13, gtol=1e-13, max_nfev=5000)
        except Exception:
            continue
        rmse = float(np.sqrt(np.mean(res.fun**2)))
        if best is None or rmse < best[0]:
            best = (rmse, res)
            best_x0 = x0_raw

    if best is None:
        raise ScopeViolationError("fit_energy_balance_model_from_series: all optimizer starts failed")

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
            f"fit_energy_balance_model_from_series: exact propagation and solve_ivp disagree by {cross_check_max_diff!r} "
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
        optimizer_status=int(res.status),
        optimizer_message=str(res.message),
        initial_guesses_tried=tuple(tuple(float(v) for v in g) for g in initial_guesses),
        best_initial_guess=tuple(float(v) for v in best_x0),
    )


@dataclass(frozen=True)
class ParameterProfile:
    name: str
    grid: Tuple[float, ...]
    chi2: Tuple[float, ...]
    classification: str
    likelihood_interval: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "grid": list(self.grid),
            "chi2": list(self.chi2),
            "classification": self.classification,
            "likelihood_interval": self.likelihood_interval,
        }


@dataclass(frozen=True)
class EnergyBalanceIdentifiabilityReport:
    profiles: Tuple[ParameterProfile, ...]
    fitted_params: EnergyBalanceParams
    chi2_at_fit: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "profiles": [p.to_dict() for p in self.profiles],
            "fitted_params": self.fitted_params.to_dict(),
            "chi2_at_fit": self.chi2_at_fit,
        }


def profile_energy_balance_identifiability(
    co2_path: str | Path,
    temp_path: str | Path,
    *,
    fit_result: EnergyBalanceFitResult | None = None,
    n_grid: int = 15,
    grid_half_width_frac: float = 0.5,
    likelihood_threshold: float = 1.0,
    bounds: Dict[str, Tuple[float, float]] | None = None,
) -> EnergyBalanceIdentifiabilityReport:
    """Profile-likelihood identifiability for all 5 fitted parameters (Milestone 47).

    MECHANISTIC_VALIDATION_ROADMAP.md package 1, response to Astra's
    2026-09-21 review: "Anschluss an die vorhandenen Profile-Likelihood-
    und Identifizierbarkeitsmodule." Uses
    ``identifiability.profile_likelihood_nlp.profile_parameter_nlp`` (a
    general bounded-NLP profiler; unlike
    ``identifiability.profile_likelihood.profile_parameter``, it is not
    restricted to a single free parameter) plus
    ``classify_identifiability``/``likelihood_interval`` from
    ``identifiability.profile_likelihood`` (reused unchanged).

    For each parameter, scans a grid of +-``grid_half_width_frac`` around
    its fitted value (clipped to ``bounds``), re-optimizing the other 4
    parameters at every grid point, and classifies the resulting profile
    as flat (practically non-identifiable on this scan), identifiable, or
    unresolved (scan too narrow to tell). A parameter sitting at a
    PARAM_BOUNDS boundary (see ``EnergyBalanceFitResult.at_bound``) will
    show an asymmetric or one-sided profile here -- consistent with, not
    contradicting, that finding.

    NORMALIZATION: the raw residual sum-of-squares (RSS) has no inherent
    scale, so a Wilks/Raue-et-al.-style ``likelihood_threshold=1.0`` (the
    standard approximate 1-sigma cut for one degree of freedom) is
    meaningless applied directly to RSS. This function instead profiles
    ``chi2 = RSS(theta) / sigma_hat_sq``, with the noise variance estimated
    from the fit itself via the standard reduced-chi-square estimator
    ``sigma_hat_sq = RSS_min / (n_years - n_params)`` -- the conventional
    choice when no independent measurement-noise estimate is available.

    HONEST WOBBLE: a profile's own minimum chi2 can occasionally sit
    slightly BELOW ``chi2_at_fit`` (by construction, exactly 62.0 for the
    shipped 67-year/5-parameter fit) -- not a bug, but itself evidence of
    the weak identifiability this function characterizes: a near-flat,
    multimodal objective surface means the reported "best of 6 starts" fit
    is not guaranteed to be the precise joint optimum along every
    direction a 1-parameter profile explores.
    """
    if fit_result is None:
        fit_result = fit_energy_balance_model(co2_path, temp_path)
    years, Tobs, F_vals = _load_overlap_series(co2_path, temp_path)

    bounds = bounds or PARAM_BOUNDS
    param_names = ["C_s", "C_d", "alpha", "gamma", "T0"]
    lb = np.array([bounds[name][0] for name in param_names])
    ub = np.array([bounds[name][1] for name in param_names])
    theta0 = np.array([getattr(fit_result.params, name) for name in param_names])

    n_obs = len(Tobs)
    n_params = len(param_names)
    if n_obs <= n_params:
        raise ScopeViolationError(f"profile_energy_balance_identifiability: need n_years > n_params; got {n_obs} <= {n_params}")
    rss_min = fit_result.rmse**2 * n_obs
    sigma_hat_sq = rss_min / (n_obs - n_params)
    if sigma_hat_sq <= 0:
        raise ScopeViolationError(f"profile_energy_balance_identifiability: non-positive sigma_hat_sq={sigma_hat_sq!r}")
    inv_sigma = 1.0 / np.sqrt(sigma_hat_sq)

    def resid(theta: np.ndarray) -> np.ndarray:
        C_s, C_d, alpha, gamma, T0 = theta
        return (_integrate_Ts_exact(F_vals, C_s, C_d, alpha, gamma, T0) - Tobs) * inv_sigma

    profiles = []
    for i, name in enumerate(param_names):
        center = float(theta0[i])
        half_width = grid_half_width_frac * max(abs(center), 0.1)
        lo = max(float(lb[i]), center - half_width)
        hi = min(float(ub[i]), center + half_width)
        if hi <= lo:
            lo, hi = float(lb[i]), float(ub[i])
        grid = np.linspace(lo, hi, n_grid)

        prof = profile_parameter_nlp(resid, theta0, i, grid, (lb, ub))
        classification = classify_identifiability(prof)
        li = likelihood_interval(prof, threshold=likelihood_threshold)
        profiles.append(
            ParameterProfile(
                name=name,
                grid=tuple(float(x) for x, _ in prof),
                chi2=tuple(float(c) for _, c in prof),
                classification=classification,
                likelihood_interval=li,
            )
        )

    chi2_at_fit = float(np.sum(resid(theta0) ** 2))
    return EnergyBalanceIdentifiabilityReport(profiles=tuple(profiles), fitted_params=fit_result.params, chi2_at_fit=chi2_at_fit)


__all__ = [
    "SOURCE",
    "CO2_FORCING_COEFFICIENT",
    "DATA_PROVENANCE_NOTE",
    "PARAM_BOUNDS",
    "EnergyBalanceParams",
    "EnergyBalanceFitResult",
    "ParameterProfile",
    "EnergyBalanceIdentifiabilityReport",
    "co2_radiative_forcing",
    "load_annual_co2",
    "fit_energy_balance_model",
    "fit_energy_balance_model_from_series",
    "integrate_energy_balance_trajectory",
    "profile_energy_balance_identifiability",
]
