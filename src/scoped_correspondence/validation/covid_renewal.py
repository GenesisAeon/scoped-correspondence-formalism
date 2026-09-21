"""COVID renewal-equation R_t estimator (Milestone 44; NONSTATIONARY_ROADMAP.md package 5a).

Response to prompts/Answers/nicht_stationäre_Treiber/SCF_Nichtstationaere_Treiber_und_Kippen.md
(Astra, 2026-09-21) section 5.4: "COVID -- Erneuerungsmodelle mit
zeitvariablem R" -- a domain-specific mechanistic model, replacing "one
more global exponential curve" with the standard epidemiological renewal
equation.

Cori et al. (2013) instantaneous reproduction number, simplified to a
DETERMINISTIC POINT ESTIMATE (no Bayesian/gamma-posterior smoothing, no
sliding estimation window -- appropriately scoped, not a full EpiEstim
reimplementation):

    Lambda_t = sum_{s=1}^{S_max} w_s * I_{t-s}
    R_t = I_t / Lambda_t

where w_s (s=1..S_max, sum to 1) is a discretized generation-interval
distribution and I_t the incidence (here: cases_7day_avg from the same
World series as covid_pilot.py's Pilot A -- a SMOOTHED proxy for
incidence, not raw daily counts; this inherits the moving-average
autocorrelation artifact Astra's review noted for early-warning use, and
the same caveat applies to R_t's own smoothness here, not just its level).

Generation interval: discretized Gamma matching the serial-interval
estimate of Nishiura, Linton & Akhmetzhanov (2020), mean=4.7 days,
sd=2.9 days (Int J Infect Dis 93:284-286, DOI 10.1016/j.ijid.2020.02.060).

Cross-check: for pure exponential growth I_t=I_0*e^{r t}, the Wallinga &
Lipsitch (2007) relation

    R = 1 / sum_s w_s * e^{-r s}

(Proc R Soc B 274:599-604, DOI 10.1098/rspb.2006.3754) gives the R implied
by a fitted growth rate r -- this lets the directly-computed R_t series be
cross-checked against the exponential rates already independently fitted
in covid_pilot.py's Pilot A/B/C, without importing or reusing their fit
functions (kept as a genuinely separate calculation).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
from scipy.stats import gamma as gamma_dist

from scoped_correspondence.errors import ScopeViolationError
from scoped_correspondence.validation.covid_pilot import DailyPoint, load_world_daily

SOURCE = (
    "Cori et al. 2013, Am J Epidemiol 178:1505-1512, DOI 10.1093/aje/kwt133 "
    "(renewal-equation instantaneous R); Nishiura, Linton & Akhmetzhanov 2020, "
    "Int J Infect Dis 93:284-286, DOI 10.1016/j.ijid.2020.02.060 (serial interval "
    "mean=4.7d, sd=2.9d); Wallinga & Lipsitch 2007, Proc R Soc B 274:599-604, "
    "DOI 10.1098/rspb.2006.3754 (exponential-rate-to-R relation)."
)

GENERATION_INTERVAL_MEAN_DAYS = 4.7
GENERATION_INTERVAL_SD_DAYS = 2.9
DEFAULT_S_MAX = 20

DATA_PROVENANCE_NOTE = (
    "Real per-row data (see data/real_data_manifest.json entry "
    "owid_covid_world_daily_2020_2023); attribution required under "
    "CC BY 4.0: 'Data: Our World in Data / Johns Hopkins University CSSE "
    "COVID-19 Data Repository.' Incidence proxy is cases_7day_avg "
    "(smoothed), not raw daily counts -- inherits the moving-average "
    "autocorrelation caveat from the early-warning discussion."
)


def discretized_generation_interval(
    mean_days: float = GENERATION_INTERVAL_MEAN_DAYS,
    sd_days: float = GENERATION_INTERVAL_SD_DAYS,
    s_max: int = DEFAULT_S_MAX,
) -> np.ndarray:
    """Discretized Gamma generation-interval weights w[0..s_max], w[0]=0, sum(w)=1.

    Standard discretization: w_s proportional to CDF(s+0.5) - CDF(s-0.5)
    for s=1..s_max, using a Gamma distribution matched to the given mean
    and standard deviation (shape k=mean^2/sd^2, scale theta=sd^2/mean).
    No mass is assigned to s=0 (no zero-day generation interval).
    """
    if mean_days <= 0 or sd_days <= 0:
        raise ScopeViolationError(
            f"discretized_generation_interval: mean_days and sd_days must be > 0; "
            f"got mean_days={mean_days!r}, sd_days={sd_days!r}"
        )
    if s_max < 2:
        raise ScopeViolationError(f"discretized_generation_interval: s_max must be >= 2; got {s_max!r}")
    theta = sd_days**2 / mean_days
    k = mean_days / theta
    edges = np.arange(0, s_max + 2, dtype=float) - 0.5
    cdf = gamma_dist.cdf(edges, a=k, scale=theta)
    w = np.diff(cdf)
    w[0] = 0.0
    total = w.sum()
    if total <= 0:
        raise ScopeViolationError("discretized_generation_interval: degenerate weights (sum <= 0)")
    return w / total


def instantaneous_r(incidence: np.ndarray, weights: np.ndarray) -> np.ndarray:
    """R_t(t) = I_t / Lambda_t for t >= len(weights)-1; NaN where Lambda_t<=0.

    ``incidence`` receives ONLY past-and-current values through the
    convolution below -- no future incidence is used at any t (a genuine
    causal, real-time-computable estimator, not a smoothed/centered one).
    """
    incidence = np.asarray(incidence, dtype=float)
    weights = np.asarray(weights, dtype=float)
    s_max = len(weights) - 1
    if len(incidence) <= s_max:
        raise ScopeViolationError(
            f"instantaneous_r: incidence series (len={len(incidence)}) too short for s_max={s_max}"
        )
    n = len(incidence)
    r_t = np.full(n, np.nan)
    for t in range(s_max, n):
        lam = float(np.dot(weights[1 : s_max + 1], incidence[t - s_max : t][::-1]))
        if lam > 0:
            r_t[t] = incidence[t] / lam
    return r_t


def wallinga_lipsitch_r(r: float, weights: np.ndarray) -> float:
    """R implied by exponential growth rate r, given generation-interval weights.

    Wallinga & Lipsitch (2007): R = 1 / sum_s w_s * e^{-r s}.
    """
    weights = np.asarray(weights, dtype=float)
    s_max = len(weights) - 1
    s = np.arange(1, s_max + 1, dtype=float)
    denom = float(np.sum(weights[1 : s_max + 1] * np.exp(-r * s)))
    if denom <= 0:
        raise ScopeViolationError(f"wallinga_lipsitch_r: degenerate denominator for r={r!r}")
    return 1.0 / denom


@dataclass(frozen=True)
class RenewalReport:
    dates: Tuple[str, ...]
    r_t: Tuple[float, ...]
    generation_interval_mean_days: float
    generation_interval_sd_days: float
    s_max: int
    wallinga_lipsitch_cross_check: Dict[str, float]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dates": list(self.dates),
            "r_t": list(self.r_t),
            "generation_interval_mean_days": self.generation_interval_mean_days,
            "generation_interval_sd_days": self.generation_interval_sd_days,
            "s_max": self.s_max,
            "wallinga_lipsitch_cross_check": dict(self.wallinga_lipsitch_cross_check),
        }


def run_covid_renewal_analysis(
    data_path: str | Path,
    *,
    window_start: str = "2020-01-28",
    window_end: str = "2020-03-25",
    s_max: int = DEFAULT_S_MAX,
    cross_check_rates: Dict[str, float] | None = None,
) -> RenewalReport:
    """Compute R_t over the fixed window and cross-check against given exponential rates.

    ``cross_check_rates``: a name->r mapping (e.g. from independently
    running covid_pilot.py's Pilot A/B/C fits) to convert via
    Wallinga & Lipsitch and report alongside the directly-computed R_t
    series, for comparison -- this function does not itself call or
    import any fitting routine from covid_pilot.py.
    """
    points: List[DailyPoint] = load_world_daily(data_path)
    windowed = [p for p in points if window_start <= p.date.isoformat() <= window_end]
    if not windowed:
        raise ScopeViolationError("run_covid_renewal_analysis: empty window")
    dates = tuple(p.date.isoformat() for p in windowed)
    incidence = np.array([p.cases_7day_avg for p in windowed], dtype=float)

    weights = discretized_generation_interval(s_max=s_max)
    r_t = instantaneous_r(incidence, weights)

    cross_check: Dict[str, float] = {}
    if cross_check_rates:
        for name, r in cross_check_rates.items():
            cross_check[name] = wallinga_lipsitch_r(r, weights)

    return RenewalReport(
        dates=dates,
        r_t=tuple(float(x) for x in r_t),
        generation_interval_mean_days=GENERATION_INTERVAL_MEAN_DAYS,
        generation_interval_sd_days=GENERATION_INTERVAL_SD_DAYS,
        s_max=s_max,
        wallinga_lipsitch_cross_check=cross_check,
    )


__all__ = [
    "SOURCE",
    "GENERATION_INTERVAL_MEAN_DAYS",
    "GENERATION_INTERVAL_SD_DAYS",
    "DEFAULT_S_MAX",
    "DATA_PROVENANCE_NOTE",
    "RenewalReport",
    "discretized_generation_interval",
    "instantaneous_r",
    "wallinga_lipsitch_r",
    "run_covid_renewal_analysis",
]
