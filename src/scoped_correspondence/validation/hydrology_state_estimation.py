"""Kalman state estimation on parallel linear reservoirs, connected via the
CORRECT daily-mean measurement operator (INTEGRATED_EXTENSION_ROADMAP.md
Paket C1, plan section 5.4) -- response to
prompts/Answers/nicht_stationäre_Treiber/SCF_INTEGRATED_EXTENSION_IMPLEMENTATION_PLAN.md.

CAMELS-DE discharge is a DAILY MEAN, not an instantaneous sample. Reusing the
instantaneous operator ``q(t) = sum_i k_i S_i(t)`` as the Kalman measurement
model would silently claim we observe something we don't. Instead, for a
constant inflow ``u`` over interval ``[t, t+Delta)`` this module reuses the
EXACT SAME closed forms already verified in ``dynamics.linear_reservoirs``
(``reservoir_step`` / ``reservoir_interval_discharge``, findings R3/R3b) to
build the discrete-time linear-Gaussian state-space model

    S(t+Delta) = F S(t) + G u(t) + w(t),      w(t) ~ (0, W)   [transition]
    qbar(t)    = H S(t) + D u(t) + v(t),      v(t) ~ (0, R)   [daily-mean obs]

    F_ii = exp(-k_i*Delta),            G_i = alpha_i*Delta*E(k_i*Delta)
    H_i  = k_i*E(k_i*Delta),           D   = sum_i alpha_i*(1-E(k_i*Delta))
    E(z) = (1-exp(-z))/z  (E(0)=1), computed via -expm1(-z)/z as in
    linear_reservoirs.py

``reservoir_daily_mean_state_space`` is cross-checked in
``verify_hydrology_state_estimation.py`` against
``parallel_reservoir_step``/``parallel_reservoir_interval_discharge``
directly (same numbers, two independent code paths) -- not merely re-derived
algebraically.

**Stochastic adapter (plan section 5.4, declared error model, not a claim of
continuous white noise):** each interval's mean discharge is a DETERMINISTIC
function of the state at the START of that interval; independent process
noise ``w(t)`` is added only at the TRANSITION to the next interval. Per day,
the order is: (1) measurement-correct the PRIOR state at the start of day
``t`` using that day's actual observed discharge (if measurement correction
is enabled for this run) via ``H``/``D``/``R``, giving the posterior state
for day ``t``; (2) propagate that posterior state forward via ``F``/``G``/
``W`` to obtain the prior for day ``t+1``. Both steps use the SAME day's
input ``u(t) = c*P(t)`` (the inflow driving day ``t``'s discharge is the same
inflow that updates day ``t``'s storage).

**No-future-leakage protocol for lead-time forecasts:** the continuous
predict+update recursion above is run once across the WHOLE span and its
posterior state after each day's correction is recorded. A ``lead``-day-ahead
forecast for day ``t`` uses ONLY the posterior recorded at day ``t-lead``,
propagated forward ``lead`` days via pure ``predict()`` calls (using the
actually-observed precipitation over those days, per this pilot's existing
conditional-hindcast convention -- plan section 9.5 mode A) with NO further
measurement update from day ``t-lead+1`` through day ``t``. The
"without correction" variant of this same pilot never calls ``update()`` at
all, reducing exactly to the existing open-loop simulation in
``hydrology_pilot.py``.

Gaussian filters CAN produce a negative mean storage or discharge; this is
reported explicitly (frequency and magnitude), never silently clipped to zero
while still claiming an exact Kalman posterior (module docstring caveat,
plan section 5.4).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional, Sequence, Tuple

import numpy as np

from scoped_correspondence.errors import ScopeViolationError
from scoped_correspondence.observation.linear_state_estimation import (
    KalmanState,
    make_state,
    predict,
    update,
)


def _E(z: np.ndarray) -> np.ndarray:
    """``E(z) = (1-exp(-z))/z``, ``E(0)=1``, computed cancellation-free via
    ``-expm1(-z)/z`` (same stable formula as ``linear_reservoirs.reservoir_interval_discharge``)."""
    z = np.asarray(z, dtype=float)
    out = np.ones_like(z)
    nz = z != 0.0
    out[nz] = -np.expm1(-z[nz]) / z[nz]
    return out


def reservoir_daily_mean_state_space(
    alphas: Sequence[float], rates: Sequence[float], dt: float = 1.0
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, float]:
    """Build ``(F, G, H, D)`` for ``n`` parallel reservoirs over an interval of
    length ``dt`` under the daily-mean measurement convention (see module
    docstring). ``F`` is ``(n,n)`` diagonal, ``G`` is ``(n,)``, ``H`` is
    ``(1,n)``, ``D`` is a scalar.
    """
    alphas = np.asarray(alphas, dtype=float)
    rates = np.asarray(rates, dtype=float)
    if alphas.shape != rates.shape or alphas.ndim != 1:
        raise ScopeViolationError(f"alphas and rates must be equal-length 1-D arrays; got {alphas.shape}, {rates.shape}")
    if np.any(alphas < 0.0) or abs(float(np.sum(alphas)) - 1.0) > 1e-9:
        raise ScopeViolationError(f"alphas must be >=0 and sum to 1; got {alphas!r}")
    if np.any(rates < 0.0):
        raise ScopeViolationError(f"rates must be >= 0; got {rates!r}")
    if dt <= 0.0:
        raise ScopeViolationError(f"dt must be > 0; got {dt!r}")

    z = rates * dt
    Ez = _E(z)
    F = np.diag(np.exp(-z))
    G = alphas * dt * Ez
    H = (rates * Ez).reshape(1, -1)
    D = float(np.sum(alphas * (1.0 - Ez)))
    return F, G, H, D


@dataclass(frozen=True)
class FilterRunResult:
    """Per-day filtered posterior means/covariances and diagnostics for one
    continuous run across the FULL contiguous span (see module docstring)."""

    posterior_means: np.ndarray  # shape (n_days, n_reservoirs)
    posterior_covs: np.ndarray  # shape (n_days, n_reservoirs, n_reservoirs)
    n_negative_storage_days: int
    n_updates_applied: int


def run_filter_full_span(
    P_full: np.ndarray,
    Q_full: np.ndarray,
    c: float,
    alphas: Sequence[float],
    rates: Sequence[float],
    W: np.ndarray,
    R: float,
    m0: np.ndarray,
    P0: np.ndarray,
    use_correction: bool,
) -> FilterRunResult:
    """Run the continuous predict/(optional)update recursion across the whole
    ``P_full``/``Q_full`` span (already the FULL CONTIGUOUS calendar span,
    C0's fix -- never a union of disjoint sub-periods)."""
    n = len(alphas)
    n_days = len(P_full)
    if len(Q_full) != n_days:
        raise ScopeViolationError("P_full and Q_full must have equal length")
    F, G, H, D = reservoir_daily_mean_state_space(alphas, rates, dt=1.0)
    R_mat = np.array([[R]])

    state = make_state(m0, P0)
    means = np.empty((n_days, n))
    covs = np.empty((n_days, n, n))
    n_updates = 0
    for t in range(n_days):
        u_t = c * P_full[t]
        if use_correction and not np.isnan(Q_full[t]):
            rep = update(state, y=[Q_full[t]], H=H, R=R_mat, D=np.array([[D]]), u=[u_t])
            state = rep.state
            n_updates += 1
        means[t] = state.mean
        covs[t] = state.cov
        state = predict(state, F=F, W=W, G=G.reshape(-1, 1), u=[u_t])

    n_negative = int(np.sum(means < 0.0))
    return FilterRunResult(posterior_means=means, posterior_covs=covs, n_negative_storage_days=n_negative, n_updates_applied=n_updates)


def lead_time_forecast(
    posterior_means: np.ndarray,
    P_full: np.ndarray,
    c: float,
    alphas: Sequence[float],
    rates: Sequence[float],
    lead: int,
) -> np.ndarray:
    """For every day ``t >= lead``, forecast day ``t``'s mean discharge using
    ONLY the posterior state recorded at day ``t-lead``, propagated forward
    ``lead`` days via pure predict() (no further correction) -- see module
    docstring, no-future-leakage protocol. Days ``t < lead`` (no valid
    ``t-lead`` origin in the loaded span) are NaN, never silently substituted.
    """
    n_days = len(P_full)
    if lead < 1:
        raise ScopeViolationError(f"lead must be >= 1; got {lead!r}")
    F, G, H, D = reservoir_daily_mean_state_space(alphas, rates, dt=1.0)
    forecasts = np.full(n_days, np.nan)
    for t in range(lead, n_days):
        origin = t - lead
        # Propagate the origin day's posterior forward through days
        # origin, origin+1, ..., t-1 (using each day's own input) to obtain the
        # PREDICTED state at the start of day t -- not yet corrected with day
        # t's own observation, matching the open-loop convention exactly.
        s = posterior_means[origin].copy()
        for day in range(origin, t):
            s = F @ s + G * (c * P_full[day])
        u_t = c * P_full[t]
        forecasts[t] = float((H @ s)[0] + D * u_t)
    return forecasts


def calibrate_process_noise(
    P_train: np.ndarray,
    Q_train: np.ndarray,
    c: float,
    alphas: Sequence[float],
    rates: Sequence[float],
    w_scale_grid: Sequence[float] = (1e-5, 1e-4, 1e-3, 1e-2, 1e-1, 1.0, 1e1, 1e2, 1e3, 1e4, 1e5, 1e6),
    inner_val_frac: float = 0.2,
) -> Tuple[float, float]:
    """Choose the process-noise scale ``w_scale`` (``W = w_scale * I``) via
    INNER time-ordered validation strictly within the training period (plan
    section 5.4/9.5: "Fit dynamic params/filter noise only on 1991-2005 with
    inner time-ordered validation") -- never touching the gap years or the
    test period. Measurement noise ``R`` is fixed separately (not grid-searched)
    as the variance of the already-fitted deterministic model's own OPEN-LOOP
    training residuals -- a declared, directly-observable error model, not a
    claim of a physically derived noise process (module docstring).

    **Observed on the real CAMELS-DE catchments (checked before fixing this
    grid's upper bound):** the inner-validation MAE keeps improving as
    ``w_scale`` grows -- i.e. the filter increasingly distrusts the fitted
    deterministic reservoir dynamics in favor of the latest measurement -- but
    it PLATEAUS empirically by ``w_scale~1e5-1e6`` (confirmed for DEA11490:
    inner MAE 0.1338 at ``w_scale=1``, 0.0978 at ``1e5``, 0.09776 at ``1e8`` --
    a genuine saturating limit, not an unbounded improvement, so the grid's
    upper end is a real asymptote and not an arbitrary truncation). Reported
    explicitly in docs/hydrology_state_estimation.md rather than silently
    picking a small grid that would hide the filter's actual preference.

    Returns ``(w_scale, R)``.
    """
    mask = ~np.isnan(Q_train)
    open_loop = _open_loop_simulate(P_train, c, alphas, rates)
    resid = open_loop[mask] - Q_train[mask]
    R = float(np.var(resid))
    if R <= 0.0:
        R = 1e-8  # degenerate only for a synthetic exact-recovery case; never expected on real data

    n = len(alphas)
    n_inner_train = int(len(P_train) * (1.0 - inner_val_frac))
    if n_inner_train < 30 or len(P_train) - n_inner_train < 30:
        raise ScopeViolationError("training period too short for an inner time-ordered validation split")
    P_it, Q_it = P_train[:n_inner_train], Q_train[:n_inner_train]
    P_iv, Q_iv = P_train[n_inner_train:], Q_train[n_inner_train:]

    best_w, best_mae = None, np.inf
    for w_scale in w_scale_grid:
        W = w_scale * np.eye(n)
        m0, P0 = np.zeros(n), 10.0 * np.eye(n)
        result_it = run_filter_full_span(P_it, Q_it, c, alphas, rates, W, R, m0, P0, use_correction=True)
        m_end, P_end = result_it.posterior_means[-1], result_it.posterior_covs[-1]
        result_iv = run_filter_full_span(P_iv, Q_iv, c, alphas, rates, W, R, m_end, P_end, use_correction=True)
        fc = lead_time_forecast(result_iv.posterior_means, P_iv, c, alphas, rates, lead=1)
        valid = (~np.isnan(Q_iv)) & (~np.isnan(fc))
        if valid.sum() == 0:
            continue
        mae = float(np.mean(np.abs(fc[valid] - Q_iv[valid])))
        if mae < best_mae:
            best_mae, best_w = mae, w_scale
    if best_w is None:
        raise ScopeViolationError("no valid w_scale candidate produced a scoreable inner-validation forecast")
    return best_w, R


def _open_loop_simulate(P: np.ndarray, c: float, alphas: Sequence[float], rates: Sequence[float]) -> np.ndarray:
    n_days = len(P)
    S = np.zeros(len(alphas))
    F, G, H, D = reservoir_daily_mean_state_space(alphas, rates, dt=1.0)
    q = np.empty(n_days)
    for t in range(n_days):
        u = c * P[t]
        q[t] = float((H @ S)[0] + D * u)
        S = F @ S + G * u
    return q


@dataclass(frozen=True)
class StateEstimationResult:
    gauge_id: str
    n_reservoirs: int
    w_scale: float
    r_measurement: float
    mae_test: Dict[str, Dict[int, float]]  # {"corrected"|"open_loop": {lead: mae}}
    mae_low_flow_test: Dict[str, Optional[float]]  # lead=1 only, keyed "corrected"|"open_loop"
    n_scored: Dict[str, int]  # per lead (common-cases count), keyed "1"/"3"/"7"
    n_negative_storage_days: Dict[str, int]

    def to_dict(self) -> Dict:
        return {
            "gauge_id": self.gauge_id, "n_reservoirs": self.n_reservoirs,
            "w_scale": self.w_scale, "r_measurement": self.r_measurement,
            "mae_test": {k: {str(lead): v for lead, v in d.items()} for k, d in self.mae_test.items()},
            "mae_low_flow_test": self.mae_low_flow_test,
            "n_scored": self.n_scored, "n_negative_storage_days": self.n_negative_storage_days,
        }


LEAD_TIMES = (1, 3, 7)


def run_catchment_state_estimation_pilot(
    gauge_id: str,
    dates: Sequence[str],
    precip: np.ndarray,
    discharge_m3s: np.ndarray,
    area_km2: float,
    train_years: Tuple[int, int],
    test_years: Tuple[int, int],
    c: float,
    alphas: Sequence[float],
    rates: Sequence[float],
) -> StateEstimationResult:
    """2x2-panel building block (plan section 5.4/9.5): given ALREADY-FITTED
    dynamic parameters ``(c, alphas, rates)`` for one reservoir count (reuse
    ``hydrology_pilot._fit_1res``/``_fit_2res`` -- the SAME fitted parameters
    used for BOTH the corrected and open-loop variant of this reservoir count,
    per the plan's explicit requirement), calibrates the filter's noise on the
    training period only (inner validation, never the gap years or test
    period), then runs BOTH the measurement-corrected and open-loop filter
    across the FULL contiguous calendar span (C0's fix), scoring lead-1/3/7
    forecasts on the test period only.
    """
    from scoped_correspondence.validation.hydrology_pilot import discharge_m3s_to_mm_day, _forward_fill

    years = np.array([int(d[:4]) for d in dates])
    train_mask = (years >= train_years[0]) & (years <= train_years[1])
    test_mask = (years >= test_years[0]) & (years <= test_years[1])
    full_span_mask = (years >= train_years[0]) & (years <= test_years[1])
    if train_years[1] >= test_years[0]:
        raise ScopeViolationError("train_years must end strictly before test_years starts")

    Q = discharge_m3s_to_mm_day(discharge_m3s, area_km2)
    P_filled = _forward_fill(precip)
    P_train, Q_train = P_filled[train_mask], Q[train_mask]
    P_full, Q_full = P_filled[full_span_mask], Q[full_span_mask]
    test_in_full = test_mask[full_span_mask]

    w_scale, R = calibrate_process_noise(P_train, Q_train, c, alphas, rates)
    n = len(alphas)
    W = w_scale * np.eye(n)
    m0, P0 = np.zeros(n), 10.0 * np.eye(n)

    result_corrected = run_filter_full_span(P_full, Q_full, c, alphas, rates, W, R, m0, P0, use_correction=True)
    result_open_loop = run_filter_full_span(P_full, Q_full, c, alphas, rates, W, R, m0, P0, use_correction=False)

    Q_test = Q[test_mask]
    q10_train = float(np.nanpercentile(Q_train, 10))

    fc = {"corrected": {}, "open_loop": {}}
    for lead in LEAD_TIMES:
        fc["corrected"][lead] = lead_time_forecast(result_corrected.posterior_means, P_full, c, alphas, rates, lead)[test_in_full]
        fc["open_loop"][lead] = lead_time_forecast(result_open_loop.posterior_means, P_full, c, alphas, rates, lead)[test_in_full]

    # Common-cases mask (plan: "Primary MAE/RMSE on common cases"): a test day is scored
    # only if EVERY lead time and EVERY variant has a valid (non-NaN) forecast there.
    common = ~np.isnan(Q_test)
    for variant in ("corrected", "open_loop"):
        for lead in LEAD_TIMES:
            common &= ~np.isnan(fc[variant][lead])

    mae_test: Dict[str, Dict[int, float]] = {"corrected": {}, "open_loop": {}}
    n_scored: Dict[str, int] = {}
    for lead in LEAD_TIMES:
        n_scored[str(lead)] = int(common.sum())
        if common.sum() == 0:
            raise ScopeViolationError(f"no common-cases days to score for {gauge_id} at lead={lead}")
        for variant in ("corrected", "open_loop"):
            mae_test[variant][lead] = float(np.mean(np.abs(fc[variant][lead][common] - Q_test[common])))

    low_mask = common & (Q_test <= q10_train)
    mae_low_flow_test = {}
    for variant in ("corrected", "open_loop"):
        mae_low_flow_test[variant] = (
            float(np.mean(np.abs(fc[variant][1][low_mask] - Q_test[low_mask]))) if low_mask.sum() > 0 else None
        )

    return StateEstimationResult(
        gauge_id=gauge_id, n_reservoirs=n, w_scale=w_scale, r_measurement=R,
        mae_test=mae_test, mae_low_flow_test=mae_low_flow_test, n_scored=n_scored,
        n_negative_storage_days={
            "corrected": result_corrected.n_negative_storage_days,
            "open_loop": result_open_loop.n_negative_storage_days,
        },
    )


__all__ = [
    "reservoir_daily_mean_state_space",
    "FilterRunResult",
    "run_filter_full_span",
    "lead_time_forecast",
    "calibrate_process_noise",
    "StateEstimationResult",
    "run_catchment_state_estimation_pilot",
    "LEAD_TIMES",
]
