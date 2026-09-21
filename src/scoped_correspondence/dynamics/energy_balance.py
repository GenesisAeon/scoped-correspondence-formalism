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
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
from scipy.integrate import solve_ivp
from scipy.interpolate import interp1d
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
        }


def _integrate_Ts(
    t: np.ndarray, F_interp, C_s: float, C_d: float, alpha: float, gamma: float, T0: float
) -> np.ndarray:
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


def fit_energy_balance_model(
    co2_path: str | Path,
    temp_path: str | Path,
    *,
    initial_guesses: List[Tuple[float, float, float, float, float]] | None = None,
) -> EnergyBalanceFitResult:
    """Fit (C_s, C_d, alpha, gamma, T0) to real CO2-forced temperature via least squares.

    IDENTIFIABILITY CAVEAT: with CO2-only forcing and a single historical
    annual temperature record, C_d and gamma in particular are only
    weakly and jointly constrained (multiple (C_d, gamma) combinations can
    give nearly the same surface-temperature trajectory) -- this function
    reports whichever fit among ``initial_guesses`` achieves the lowest
    RMSE, not a claim of a uniquely identified physical optimum. A
    profile-likelihood-style check (identifiability.profile_likelihood)
    would be needed to characterize this rigorously; not done here.
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

    co2_arr = np.array([co2[y] for y in years], dtype=float)
    Tobs = np.array([temp[y] for y in years], dtype=float)
    co2_ref = co2_arr[0]
    F_vals = co2_radiative_forcing(co2_arr, co2_ref)
    t = np.arange(len(years), dtype=float)
    F_interp = interp1d(t, F_vals, kind="linear", fill_value="extrapolate")

    def model_Ts(log_params: np.ndarray) -> np.ndarray:
        log_Cs, log_Cd, log_alpha, log_gamma, T0 = log_params
        return _integrate_Ts(t, F_interp, np.exp(log_Cs), np.exp(log_Cd), np.exp(log_alpha), np.exp(log_gamma), T0)

    def resid(log_params: np.ndarray) -> np.ndarray:
        return model_Ts(log_params) - Tobs

    if initial_guesses is None:
        initial_guesses = [
            (5.0, 70.0, 1.2, 0.7, -0.2),
            (3.0, 50.0, 1.5, 0.5, -0.3),
            (10.0, 120.0, 0.8, 1.0, -0.2),
            (7.0, 100.0, 1.0, 0.7, -0.2),
        ]

    best = None
    for Cs0, Cd0, alpha0, gamma0, T00 in initial_guesses:
        x0 = np.array([np.log(Cs0), np.log(Cd0), np.log(alpha0), np.log(gamma0), T00])
        try:
            res = least_squares(resid, x0, method="lm", xtol=1e-13, ftol=1e-13, gtol=1e-13, max_nfev=2000)
        except Exception:
            continue
        rmse = float(np.sqrt(np.mean(res.fun**2)))
        if best is None or rmse < best[0]:
            best = (rmse, res)

    if best is None:
        raise ScopeViolationError("fit_energy_balance_model: all optimizer starts failed")

    rmse, res = best
    log_Cs, log_Cd, log_alpha, log_gamma, T0 = res.x
    params = EnergyBalanceParams(
        C_s=float(np.exp(log_Cs)),
        C_d=float(np.exp(log_Cd)),
        alpha=float(np.exp(log_alpha)),
        gamma=float(np.exp(log_gamma)),
        T0=float(T0),
    )
    predicted = model_Ts(res.x)

    return EnergyBalanceFitResult(
        params=params,
        years=tuple(years),
        predicted_Ts=tuple(float(x) for x in predicted),
        observed_Ts=tuple(float(x) for x in Tobs),
        rmse=rmse,
        optimizer_success=bool(res.success),
        optimizer_cost=float(res.cost),
        n_starts_tried=len(initial_guesses),
    )


__all__ = [
    "SOURCE",
    "CO2_FORCING_COEFFICIENT",
    "DATA_PROVENANCE_NOTE",
    "EnergyBalanceParams",
    "EnergyBalanceFitResult",
    "co2_radiative_forcing",
    "load_annual_co2",
    "fit_energy_balance_model",
]
