"""OWID/JHU global COVID-19 growth-phase pilot (Milestone 6b).

Real-data pilot built directly on a verified dataset (see
docs/real_data_provenance.md / data/real_data_manifest.json), structurally
analogous to the Cygnus pilot (validation/core.py) but resting on confirmed
real per-row data instead of an unverified one -- see
validation.core.DATA_PROVENANCE_WARNING for what went wrong there.

Protocol (immutable before any fit -- fixed here using external, independently
documented calendar milestones, not chosen by looking at the fit quality):
  - Macro: cases_7day_avg = weekly_cases / 7 (trailing 7-day mean daily new
    cases, World aggregate; reduces weekday reporting artifacts present in
    the raw new_cases column)
  - Calib window: 2020-01-27 (first date with weekly_cases defined in the
    source file) through 2020-03-11 (WHO declared COVID-19 a pandemic on
    this date -- an externally documented milestone, not fit-derived)
  - Holdout window: 2020-03-12 through 2020-03-25 (the 14 days immediately
    following, a round number fixed in advance)
  - Baseline: persistence = last calib cases_7day_avg held constant
  - Metric: RMSE on the holdout window
  - Free params (r, ln_cases0) estimated ONLY on calib via ordinary least
    squares on ln(cases_7day_avg); no holdout peeking

Growth model:
  cases(t) = cases0 * exp(r * (t - t_ref))
with t_ref = first calib date, t in days. This is the standard early-phase
epidemic growth model (locally linear SIR near the epidemic threshold); it
is not claimed to hold outside the fixed calib/holdout window, and no
universality claim is made about any other disease, wave, or country.

This is ONE domain, ONE macro, ONE fixed window. No cross-wave, cross-domain,
or cross-country claim (same scope discipline as validation/core.py's
Cygnus pilot). A model_beats_baseline=False result is a VALID complete
outcome and must not trigger a retune.
"""

from __future__ import annotations

import csv
import datetime as dt
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple

from scoped_correspondence.errors import ScopeViolationError
from scoped_correspondence.validation.core import ValidationReport, rmse

# --- Fixed protocol (locked BEFORE fit) -------------------------------------

DOMAIN_NAME = "owid-jhu-covid-world"
MACRO_NAME = "cases_7day_avg"
MACRO_UNIT = "cases/day"
SOURCE_RELATIVE = "data/owid_covid_world_daily_2020_2023.csv"
SOURCE_CITATION = (
    "Our World in Data COVID-19 dataset (JHU CSSE historical compact series); "
    "data/real_data_manifest.json entry owid_covid_world_daily_2020_2023"
)
CALIB_START = dt.date(2020, 1, 27)
CALIB_END = dt.date(2020, 3, 11)  # WHO pandemic declaration -- external anchor
HOLDOUT_START = dt.date(2020, 3, 12)
HOLDOUT_END = dt.date(2020, 3, 25)  # 14 days after CALIB_END, fixed in advance

DATA_PROVENANCE_NOTE = (
    "Real per-row data (see data/real_data_manifest.json entry "
    "owid_covid_world_daily_2020_2023); attribution required under "
    "CC BY 4.0: 'Data: Our World in Data / Johns Hopkins University CSSE "
    "COVID-19 Data Repository.'"
)


@dataclass(frozen=True)
class DailyPoint:
    """One World-aggregate daily row with the derived smoothed macro."""

    date: dt.date
    new_cases: float
    weekly_cases: float
    cases_7day_avg: float


@dataclass(frozen=True)
class FittedExponentialGrowth:
    r: float
    ln_cases0: float
    cases0: float
    t_ref: dt.date
    n_calib: int
    note: str = "fitted_parameters estimated exclusively on calibration days"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "r": self.r,
            "ln_cases0": self.ln_cases0,
            "cases0": self.cases0,
            "t_ref": self.t_ref.isoformat(),
            "n_calib": self.n_calib,
            "note": self.note,
        }


def load_world_daily(path: str | Path) -> List[DailyPoint]:
    """Load World-aggregate rows with weekly_cases defined (structure-specific)."""
    p = Path(path)
    points: List[DailyPoint] = []
    with p.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            if row["location"] != "World":
                raise ScopeViolationError(
                    f"load_world_daily: expected only World rows, got {row['location']!r}"
                )
            wk = row["weekly_cases"]
            if wk in ("", None):
                continue  # first 5 rows before a 7-day trailing window exists
            date = dt.date.fromisoformat(row["date"])
            weekly_cases = float(wk)
            points.append(
                DailyPoint(
                    date=date,
                    new_cases=float(row["new_cases"]),
                    weekly_cases=weekly_cases,
                    cases_7day_avg=weekly_cases / 7.0,
                )
            )
    if not points:
        raise ScopeViolationError("load_world_daily: no rows with weekly_cases found")
    return points


def split_by_date(
    points: List[DailyPoint],
    *,
    calib_start: dt.date = CALIB_START,
    calib_end: dt.date = CALIB_END,
    holdout_start: dt.date = HOLDOUT_START,
    holdout_end: dt.date = HOLDOUT_END,
) -> Tuple[List[DailyPoint], List[DailyPoint]]:
    """Split by fixed calendar dates; refuse any other split (anti data-snooping)."""
    if (calib_start, calib_end) != (CALIB_START, CALIB_END) or (
        holdout_start,
        holdout_end,
    ) != (HOLDOUT_START, HOLDOUT_END):
        raise ScopeViolationError(
            "split_by_date: requested dates differ from the fixed protocol "
            f"(anti data-snooping). requested calib=[{calib_start},{calib_end}] "
            f"holdout=[{holdout_start},{holdout_end}]; fixed calib="
            f"[{CALIB_START},{CALIB_END}] holdout=[{HOLDOUT_START},{HOLDOUT_END}]"
        )
    if calib_end >= holdout_start:
        raise ScopeViolationError(
            "split_by_date: calib_end must be before holdout_start "
            f"(got calib_end={calib_end}, holdout_start={holdout_start})"
        )
    calib = [p for p in points if calib_start <= p.date <= calib_end]
    holdout = [p for p in points if holdout_start <= p.date <= holdout_end]
    if not calib:
        raise ScopeViolationError("split_by_date: empty calibration window")
    if not holdout:
        raise ScopeViolationError("split_by_date: empty holdout window")
    return calib, holdout


def fit_exponential_growth(calib: List[DailyPoint]) -> FittedExponentialGrowth:
    """Ordinary least squares on ln(cases_7day_avg) vs. days since t_ref.

    Receives ONLY calib points -- this function body never references a
    holdout window or any date outside its ``calib`` argument.
    """
    if len(calib) < 2:
        raise ScopeViolationError("fit_exponential_growth: need >= 2 calib points")
    t_ref = calib[0].date
    xs = [float((p.date - t_ref).days) for p in calib]
    ys = []
    for p in calib:
        if not (p.cases_7day_avg > 0.0):
            raise ScopeViolationError(
                f"fit_exponential_growth: cases_7day_avg must be > 0 for log-fit, "
                f"got {p.cases_7day_avg!r} on {p.date}"
            )
        ys.append(math.log(p.cases_7day_avg))
    n = len(xs)
    x_mean = sum(xs) / n
    y_mean = sum(ys) / n
    sxx = sum((x - x_mean) ** 2 for x in xs)
    sxy = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys))
    if sxx <= 0.0:
        raise ScopeViolationError("fit_exponential_growth: degenerate calib window (sxx<=0)")
    r = sxy / sxx
    ln_cases0 = y_mean - r * x_mean
    return FittedExponentialGrowth(
        r=r,
        ln_cases0=ln_cases0,
        cases0=math.exp(ln_cases0),
        t_ref=t_ref,
        n_calib=n,
    )


def predict_exponential(t_days: float, *, r: float, ln_cases0: float) -> float:
    """cases(t) = exp(ln_cases0 + r*t)."""
    return math.exp(ln_cases0 + r * t_days)


def persistence_baseline_covid(calib: List[DailyPoint]) -> float:
    """Last calib cases_7day_avg, held constant on all holdout days."""
    if not calib:
        raise ScopeViolationError("persistence_baseline_covid: empty calib")
    return calib[-1].cases_7day_avg


def run_covid_pilot(
    data_path: str | Path,
    *,
    domain: str = DOMAIN_NAME,
) -> Tuple[ValidationReport, FittedExponentialGrowth]:
    """Load -> fixed date split -> fit (calib) -> baseline -> holdout RMSE."""
    points = load_world_daily(data_path)
    calib, holdout = split_by_date(points)

    fit = fit_exponential_growth(calib)  # calib only -- holdout not referenced
    base = persistence_baseline_covid(calib)

    hold_obs = [p.cases_7day_avg for p in holdout]
    model_pred = [
        predict_exponential(
            float((p.date - fit.t_ref).days), r=fit.r, ln_cases0=fit.ln_cases0
        )
        for p in holdout
    ]
    base_pred = [base] * len(holdout)

    model_rmse = rmse(hold_obs, model_pred)
    baseline_rmse = rmse(hold_obs, base_pred)
    beats = bool(model_rmse < baseline_rmse)

    report = ValidationReport(
        domain=domain,
        macro=MACRO_NAME,
        split={
            "calib_start": CALIB_START.isoformat(),
            "calib_end": CALIB_END.isoformat(),
            "holdout_start": HOLDOUT_START.isoformat(),
            "holdout_end": HOLDOUT_END.isoformat(),
            "n_calib": len(calib),
            "n_holdout": len(holdout),
            "rule": (
                "calib ends at the WHO pandemic declaration (2020-03-11, an "
                "externally documented milestone); holdout is the fixed next "
                "14 days -- both fixed before any fit"
            ),
        },
        model_rmse_holdout=model_rmse,
        baseline_rmse_holdout=baseline_rmse,
        model_beats_baseline=beats,
        fitted_parameters=fit.to_dict(),
        source_citation=SOURCE_CITATION,
        baseline_value=base,
        n_holdout=len(holdout),
        notes=(
            DATA_PROVENANCE_NOTE,
            "False model_beats_baseline is a VALID complete result -- no retune.",
            "fit_exponential_growth receives only calib points; holdout used solely for RMSE.",
            "Exponential growth is a local early-phase model; no claim beyond "
            "the fixed calib/holdout window, no cross-wave or cross-country claim.",
        ),
    )
    return report, fit


__all__ = [
    "CALIB_START",
    "CALIB_END",
    "HOLDOUT_START",
    "HOLDOUT_END",
    "DATA_PROVENANCE_NOTE",
    "DailyPoint",
    "FittedExponentialGrowth",
    "fit_exponential_growth",
    "load_world_daily",
    "persistence_baseline_covid",
    "predict_exponential",
    "run_covid_pilot",
    "split_by_date",
]
