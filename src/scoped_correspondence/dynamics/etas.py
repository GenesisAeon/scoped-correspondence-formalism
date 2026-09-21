"""ETAS (Epidemic-Type Aftershock Sequence) self-exciting point process, fit to real
earthquake data (Milestone 46).

NONSTATIONARY_ROADMAP.md package 5c, response to
prompts/Answers/nicht_stationäre_Treiber/SCF_Nichtstationaere_Treiber_und_Kippen.md
(Astra, 2026-09-21) section 5.4: a genuine earthquake-domain mechanistic
model instead of a homogeneous-Poisson constant-rate fit, and a direct
mechanistic test of the overdispersion finding already documented in
docs/earthquake_pilot.md (Fano factor 3.16, dispersion statistic D=60.01
on 19 df, p ~= 3.85e-6 against an equal-rate Poisson null).

Model (Ogata 1988, J. Am. Stat. Assoc. 83:9-27, DOI 10.1080/01621459.1988.10478560):

    lambda(t | H_t) = mu + sum_{t_i < t} K * exp(alpha*(M_i - M0)) / (t - t_i + c)^p

mu: constant background rate; K, c, p: Omori-Utsu aftershock-decay kernel
parameters; alpha: magnitude-productivity scaling; M0: catalog magnitude
of completeness (here the catalog's own minmagnitude=6.0 filter).

Log-likelihood on [0, T] (standard point-process form) requires the
compensator (integrated intensity):

    Lambda(T) = mu*T + sum_i K*exp(alpha*(M_i-M0)) * g(T - t_i; c, p)
    g(D; c, p) = [c^(1-p) - (D+c)^(1-p)] / (p-1)          (p != 1)
    g(D; c, p) = ln((D+c)/c)                               (p == 1)

    log L = sum_i log(lambda(t_i | H_{t_i})) - Lambda(T)

IMPORTANT SCOPE LIMITATIONS: this is a TEMPORAL-ONLY ETAS fit (no spatial
kernel) applied to a GLOBAL, multi-region M>=6.0 catalog. Real ETAS
practice fits a single well-defined regional sequence with its own
magnitude of completeness; pooling the whole globe means "aftershocks"
here can include unrelated, temporally-nearby events in different regions
that a spatial-temporal ETAS would correctly separate. The fitted
parameters therefore do NOT claim to recover physically calibrated,
region-specific Omori-Utsu constants -- they test only the qualitative
question of whether a self-exciting temporal kernel fits the pooled
global catalog better than an equal-rate Poisson null, as an honest
mechanistic explanation for the already-documented overdispersion.
"""

from __future__ import annotations

import csv
import datetime as dt
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
from scipy.optimize import minimize

from scoped_correspondence.errors import ScopeViolationError

SOURCE = (
    "Ogata 1988, J. Am. Stat. Assoc. 83:9-27, DOI 10.1080/01621459.1988.10478560 "
    "(ETAS model and its point-process log-likelihood / compensator form)."
)

DATA_PROVENANCE_NOTE = (
    "Real per-row data: data/usgs_earthquakes_m6plus_2000_2026.csv (USGS ComCat "
    "FDSN Event Web Service, public domain -- see data/real_data_manifest.json). "
    "TEMPORAL-ONLY fit on a pooled GLOBAL multi-region catalog -- a major "
    "documented simplification versus real regional ETAS practice; see module "
    "docstring."
)

SCOPE_WARNING = (
    "Temporal-only ETAS on a pooled global catalog is a qualitative "
    "self-excitation test, not a calibrated regional hazard model."
)


def load_catalog(path: str | Path, *, m0: float) -> Tuple[np.ndarray, np.ndarray]:
    """Load (times_in_days_since_first_event, magnitudes), sorted ascending by time."""
    p = Path(path)
    with p.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise ScopeViolationError("load_catalog: no rows found")
    rows_sorted = sorted(rows, key=lambda r: r["time"])
    t0 = dt.datetime.fromisoformat(rows_sorted[0]["time"].replace("Z", "+00:00"))
    times = np.array(
        [
            (dt.datetime.fromisoformat(r["time"].replace("Z", "+00:00")) - t0).total_seconds() / 86400.0
            for r in rows_sorted
        ]
    )
    mags = np.array([float(r["mag"]) for r in rows_sorted])
    if np.any(mags < m0):
        raise ScopeViolationError(f"load_catalog: found magnitude below m0={m0!r}")
    return times, mags


def compensator_g(D: np.ndarray, c: float, p: float) -> np.ndarray:
    """Integral of the Omori-Utsu kernel 1/(s+c)^p over s in [0, D]."""
    D = np.asarray(D, dtype=float)
    if abs(p - 1.0) < 1e-9:
        return np.log((D + c) / c)
    return (c ** (1 - p) - (D + c) ** (1 - p)) / (p - 1)


def _neg_log_lik_core(
    log_params: np.ndarray,
    times: np.ndarray,
    mags: np.ndarray,
    m0: float,
    i_idx: np.ndarray,
    j_idx: np.ndarray,
    dt_ij: np.ndarray,
    t_end: float,
) -> float:
    """Shared fast implementation given precomputed causal-pair indices.

    ``i_idx``/``j_idx``/``dt_ij`` depend only on ``times`` (via
    ``np.tril_indices``, since sorted ``times`` makes "j triggers i" exactly
    "j < i"), never on the fitted parameters -- callers that evaluate this
    many times for the same catalog (i.e. an optimizer) should build them
    ONCE and reuse them, which is the whole point of splitting this out from
    :func:`etas_neg_log_likelihood`. Restricting to the ``j < i`` pairs (via
    ``tril_indices``, half the full N^2 matrix) also means the power
    operation is only ever evaluated on genuinely causal, positive
    ``dt_ij + c`` bases -- unlike a dense ``np.where(mask, ..., ...)`` form,
    there is no masked-out branch to accidentally raise an invalid base to a
    non-integer power.

    ``t_end`` is the EXPLICIT end of the observation window (Astra,
    2026-09-21: "Beobachtungsbeginn/-ende explizit ... statt erster/letzter
    Ereigniszeit") -- callers pass ``times[-1]`` to reproduce the original
    implicit behavior, or a later value (e.g. "today", if no qualifying
    event has occurred since the catalog's last one) for a more honest
    compensator integral.
    """
    log_mu, log_K, log_c, log_pm1, alpha = log_params
    mu = np.exp(log_mu)
    K = np.exp(log_K)
    c = np.exp(log_c)
    p = 1.0 + np.exp(log_pm1)

    N = len(times)
    excitation = K * np.exp(alpha * (mags - m0))
    contrib = excitation[j_idx] / np.power(dt_ij + c, p)
    lam = mu + np.bincount(i_idx, weights=contrib, minlength=N)
    if np.any(lam <= 0) or not np.all(np.isfinite(lam)):
        return 1e12

    compensator = mu * t_end + np.sum(excitation * compensator_g(t_end - times, c, p))
    ll = np.sum(np.log(lam)) - compensator
    if not np.isfinite(ll):
        return 1e12
    return -ll


def etas_neg_log_likelihood(
    log_params: np.ndarray,
    times: np.ndarray,
    mags: np.ndarray,
    *,
    m0: float,
    t_end: float | None = None,
) -> float:
    """Negative log-likelihood in a log/logit parametrization for unconstrained optimization.

    log_params = (log_mu, log_K, log_c, log(p-1), alpha); p = 1 + exp(log(p-1)) > 1.
    Builds the causal-pair index arrays fresh on every call -- convenient
    and correct for a single evaluation (e.g. the independent hand-check in
    verify_etas.py), but :func:`fit_etas_model` uses :func:`_neg_log_lik_core`
    directly with indices built once, since an optimizer calls this hundreds
    of times against the same fixed ``times``/``mags``.

    ``t_end`` defaults to ``times[-1]`` (the original implicit behavior) if
    not given; pass an explicit value to use a different observation-window
    end (see ``_neg_log_lik_core``).
    """
    times = np.asarray(times, dtype=float)
    mags = np.asarray(mags, dtype=float)
    if t_end is None:
        t_end = float(times[-1])
    i_idx, j_idx = np.tril_indices(len(times), k=-1)
    dt_ij = times[i_idx] - times[j_idx]
    return _neg_log_lik_core(log_params, times, mags, m0, i_idx, j_idx, dt_ij, float(t_end))


@dataclass(frozen=True)
class ETASParams:
    mu: float
    K: float
    c: float
    p: float
    alpha: float

    def to_dict(self) -> Dict[str, float]:
        return {"mu": self.mu, "K": self.K, "c": self.c, "p": self.p, "alpha": self.alpha}


@dataclass(frozen=True)
class ETASFitResult:
    params: ETASParams
    n_events: int
    T_days: float
    m0: float
    log_lik_etas: float
    log_lik_null_poisson: float
    aic_etas: float
    aic_null_poisson: float
    branching_ratio: float
    optimizer_success: bool
    n_starts_tried: int
    optimizer_status: int
    optimizer_message: str
    initial_guess_used: Tuple[float, float, float, float, float]
    t_start: float
    t_end: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "params": self.params.to_dict(),
            "n_events": self.n_events,
            "T_days": self.T_days,
            "m0": self.m0,
            "log_lik_etas": self.log_lik_etas,
            "log_lik_null_poisson": self.log_lik_null_poisson,
            "aic_etas": self.aic_etas,
            "aic_null_poisson": self.aic_null_poisson,
            "branching_ratio": self.branching_ratio,
            "optimizer_success": self.optimizer_success,
            "n_starts_tried": self.n_starts_tried,
            "optimizer_status": self.optimizer_status,
            "optimizer_message": self.optimizer_message,
            "initial_guess_used": list(self.initial_guess_used),
            "t_start": self.t_start,
            "t_end": self.t_end,
        }


def null_poisson_log_likelihood(times: np.ndarray, *, t_start: float = 0.0, t_end: float | None = None) -> float:
    """Closed-form log-likelihood of the MLE-fit homogeneous Poisson null (mu_hat = N/(t_end-t_start)).

    ``t_start``/``t_end`` default to 0.0/``times[-1]`` (the original
    implicit behavior: observation window = [first event, last event]) --
    pass explicit values for a fair AIC comparison against an ETAS fit
    using a different observation window (Astra, 2026-09-21).
    """
    N = len(times)
    if t_end is None:
        t_end = float(times[-1])
    window = float(t_end) - float(t_start)
    if window <= 0:
        raise ScopeViolationError(f"null_poisson_log_likelihood: t_end must be > t_start; got t_start={t_start!r}, t_end={t_end!r}")
    mu_hat = N / window
    return float(N * np.log(mu_hat) - mu_hat * window)


def etas_branching_ratio(K: float, c: float, p: float, alpha: float, mags: np.ndarray, m0: float) -> float:
    """Expected number of direct offspring per event: K * mean(exp(alpha*(M-M0))) * c^(1-p)/(p-1).

    The kernel's own time-integral from 0 to infinity is c^(1-p)/(p-1) for
    p > 1 (finite only in that regime); the magnitude factor is averaged
    over the OBSERVED magnitude distribution, not assumed. Values near or
    above 1 indicate a super-/near-critical (heavily self-exciting) regime.
    """
    if p <= 1.0:
        raise ScopeViolationError(f"etas_branching_ratio: p must be > 1 for a finite kernel integral; got {p!r}")
    kernel_integral = c ** (1 - p) / (p - 1)
    magnitude_factor = float(np.mean(np.exp(alpha * (mags - m0))))
    return float(K * magnitude_factor * kernel_integral)


def fit_etas_model(
    catalog_path: str | Path,
    *,
    m0: float = 6.0,
    initial_guesses: List[Tuple[float, float, float, float, float]] | None = None,
    maxiter: int = 140,
    t_end: float | None = None,
) -> ETASFitResult:
    """Fit (mu, K, c, p, alpha) to a real earthquake catalog via MLE (Nelder-Mead).

    Compares against the closed-form MLE homogeneous-Poisson null via AIC.
    See module docstring for the temporal-only / pooled-global-catalog
    scope limitation.

    PERFORMANCE NOTE: this is an exact O(N^2) point-process likelihood
    (N=3974 for the shipped catalog); a single Nelder-Mead evaluation costs
    ~0.5s even with the causal-pair (j<i only) ``bincount`` form used by
    :func:`_neg_log_lik_core`. To stay within the verification suite's
    per-script time budget, the default here is a SINGLE, physically
    motivated informed starting point (unlike e.g. ``energy_balance.py``'s
    4 generic starts) rather than a multi-start search, and ``maxiter=140``
    rather than a tight convergence tolerance -- ``optimizer_success`` is
    therefore typically False (the Nelder-Mead simplex has not fully
    shrunk), but this is NOT the same as a poor fit: independent offline
    testing found the negative log-likelihood at 140, 250, and a fully
    converged ~1400-evaluation budget all agree to within 0.3 nats
    (-6886.98 / -6886.75 / -6886.73), i.e. the optimizer reaches the same
    basin quickly and then spends the remaining budget on sub-nat
    refinement. Callers wanting a more thorough (and much slower) refit can
    pass a larger ``maxiter`` and/or additional ``initial_guesses``.

    IDENTIFIABILITY NOTE: on this pooled GLOBAL catalog, the fit
    consistently drives ``p`` towards its lower boundary (p -> 1, i.e. a
    very slowly decaying, near-logarithmic aftershock kernel) across every
    tested starting point and budget. This is plausibly an artifact of
    pooling many regions with genuinely different (and typically larger,
    p~1.0-1.5) regional Omori-Utsu decay rates -- averaging heterogeneous
    exponential-family decays over many unrelated sequences tends to look
    like a single much slower/heavier-tailed decay at the population level.
    This is a real, honest limitation of the global-pooling simplification,
    not a claim that real regional aftershock decay has p~1.

    OBSERVATION WINDOW (Astra, 2026-09-21): ``t_end`` defaults to the last
    event's own time (the original implicit behavior), but can be set
    explicitly -- e.g. to "today" in days-since-first-event -- when no
    qualifying event has occurred between the catalog's last event and the
    actual end of observation, which changes the compensator integral (a
    longer quiet tail after the last event is real information the
    implicit default silently discards). Pre-history before the first
    event (t<0) is NOT modeled here -- a separate, harder extension left
    for future work (see MECHANISTIC_VALIDATION_ROADMAP.md package 1).
    """
    times, mags = load_catalog(catalog_path, m0=m0)
    N = len(times)
    t_start = 0.0
    if t_end is None:
        t_end = float(times[-1])
    else:
        t_end = float(t_end)
        if t_end < float(times[-1]):
            raise ScopeViolationError(f"fit_etas_model: t_end={t_end!r} must be >= the last event time {times[-1]!r}")
    if N < 100:
        raise ScopeViolationError(f"fit_etas_model: only {N} events, need >= 100")

    i_idx, j_idx = np.tril_indices(N, k=-1)
    dt_ij = times[i_idx] - times[j_idx]

    if initial_guesses is None:
        branching_guess = 0.3
        mu0 = (N / t_end) * (1.0 - branching_guess)
        # A single informed start: c0/p0/alpha0 chosen near the basin found by
        # independent offline exploration (see PERFORMANCE NOTE above), the
        # same spirit as energy_balance.py's hand-chosen plausible starts.
        initial_guesses = [(mu0, 0.006, 0.006, 1.05, 1.9)]

    best = None
    best_x0 = None
    for mu0, K0, c0, p0, alpha0 in initial_guesses:
        x0 = np.array([np.log(mu0), np.log(K0), np.log(c0), np.log(p0 - 1.0), alpha0])
        res = minimize(
            lambda x: _neg_log_lik_core(x, times, mags, m0, i_idx, j_idx, dt_ij, t_end),
            x0,
            method="Nelder-Mead",
            options={"maxiter": maxiter, "maxfev": maxiter, "xatol": 1e-5, "fatol": 1e-3, "adaptive": True},
        )
        if best is None or res.fun < best[0]:
            best = (res.fun, res)
            best_x0 = (mu0, K0, c0, p0, alpha0)

    nll, res = best
    log_mu, log_K, log_c, log_pm1, alpha = res.x
    mu = float(np.exp(log_mu))
    K = float(np.exp(log_K))
    c = float(np.exp(log_c))
    p = float(1.0 + np.exp(log_pm1))
    params = ETASParams(mu=mu, K=K, c=c, p=p, alpha=float(alpha))

    ll_etas = -float(nll)
    ll_null = null_poisson_log_likelihood(times, t_start=t_start, t_end=t_end)
    branching = etas_branching_ratio(K, c, p, float(alpha), mags, m0)

    return ETASFitResult(
        params=params,
        n_events=N,
        T_days=t_end,
        m0=m0,
        log_lik_etas=ll_etas,
        log_lik_null_poisson=ll_null,
        aic_etas=float(2 * 5 - 2 * ll_etas),
        aic_null_poisson=float(2 * 1 - 2 * ll_null),
        branching_ratio=branching,
        optimizer_success=bool(res.success),
        n_starts_tried=len(initial_guesses),
        optimizer_status=int(res.status),
        optimizer_message=str(res.message),
        initial_guess_used=tuple(float(v) for v in best_x0),
        t_start=t_start,
        t_end=t_end,
    )


__all__ = [
    "SOURCE",
    "DATA_PROVENANCE_NOTE",
    "SCOPE_WARNING",
    "ETASParams",
    "ETASFitResult",
    "load_catalog",
    "compensator_g",
    "etas_neg_log_likelihood",
    "null_poisson_log_likelihood",
    "etas_branching_ratio",
    "fit_etas_model",
]
