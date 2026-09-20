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
outcome and must not trigger a retune. run_covid_pilot() above (Pilot A)
is NEVER changed after the fact -- its honest negative result stands
(see docs/covid_pilot.md).

Two DISCLOSED follow-up investigations, informed by Pilot A's own
diagnosis (not a silent retune of Pilot A -- Pilot A's protocol, code,
and reported result are untouched):

Pilot B -- run_covid_pilot_short_window(): tests whether a shorter,
visibly homogeneous window fixes the problem. Pilot A's own data shows a
clear local peak at 2020-02-14 and a local trough at 2020-02-25 (the
initial China/Hubei wave and its containment) BEFORE the monotonic global
rise resumes. Calib is restarted the day after that trough (2020-02-26)
through the same 2020-03-11 anchor; holdout is the SAME fixed window as
Pilot A (2020-03-12 to 2020-03-25) for direct comparability. Choosing the
trough as the new calib start uses information from Pilot A's diagnosis,
which is why this is reported as an investigative Pilot B, not folded
into Pilot A.

Pilot C -- run_covid_pilot_changepoint(): tests a two-segment
(change-point / segmented regression) model on Pilot A's ORIGINAL calib
window (2020-01-27 to 2020-03-11), instead of assuming one growth
regime. The breakpoint is found by grid search WITHIN CALIB ONLY (total
residual sum of squares of two independent log-linear fits, minimized
over candidate breakpoints with >= MIN_SEGMENT_POINTS on each side -- no
holdout peeking), then only the SECOND (most recent) segment's fitted
rate is used to extrapolate into the same fixed holdout window.
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

# --- Pilot B: shorter window starting after Pilot A's own diagnosed trough --

PEAK_DATE_IN_PILOT_A_CALIB = dt.date(2020, 2, 14)  # informational, not used in any fit
TROUGH_DATE_IN_PILOT_A_CALIB = dt.date(2020, 2, 25)  # informational, not used in any fit
CALIB_B_START = dt.date(2020, 2, 26)  # day after the trough
CALIB_B_END = CALIB_END  # same WHO anchor, for comparability with Pilot A/C

# --- Pilot C: change-point / segmented regression on Pilot A's full window --

MIN_SEGMENT_POINTS = 5  # minimum points required on each side of a breakpoint

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


# --- Pilot B: shorter window starting after Pilot A's own diagnosed trough --


def split_by_date_short_window(
    points: List[DailyPoint],
    *,
    calib_start: dt.date = CALIB_B_START,
    calib_end: dt.date = CALIB_B_END,
    holdout_start: dt.date = HOLDOUT_START,
    holdout_end: dt.date = HOLDOUT_END,
) -> Tuple[List[DailyPoint], List[DailyPoint]]:
    """Pilot B's own fixed split (post-trough calib, same holdout as Pilot A).

    A separate fixed protocol from ``split_by_date`` -- refuses any other
    split (same anti-data-snooping discipline), but for Pilot B's dates.
    """
    if (calib_start, calib_end) != (CALIB_B_START, CALIB_B_END) or (
        holdout_start,
        holdout_end,
    ) != (HOLDOUT_START, HOLDOUT_END):
        raise ScopeViolationError(
            "split_by_date_short_window: requested dates differ from Pilot "
            f"B's fixed protocol. requested calib=[{calib_start},{calib_end}] "
            f"holdout=[{holdout_start},{holdout_end}]; fixed calib="
            f"[{CALIB_B_START},{CALIB_B_END}] holdout=[{HOLDOUT_START},{HOLDOUT_END}]"
        )
    calib = [p for p in points if calib_start <= p.date <= calib_end]
    holdout = [p for p in points if holdout_start <= p.date <= holdout_end]
    if not calib:
        raise ScopeViolationError("split_by_date_short_window: empty calibration window")
    if not holdout:
        raise ScopeViolationError("split_by_date_short_window: empty holdout window")
    return calib, holdout


def run_covid_pilot_short_window(
    data_path: str | Path,
    *,
    domain: str = DOMAIN_NAME,
) -> Tuple[ValidationReport, FittedExponentialGrowth]:
    """Pilot B: same model/baseline/metric as Pilot A, shorter homogeneous calib.

    Calib restarts the day after Pilot A's own diagnosed local trough
    (2020-02-25); holdout is IDENTICAL to Pilot A for direct comparison.
    Does not modify or re-run Pilot A.
    """
    points = load_world_daily(data_path)
    calib, holdout = split_by_date_short_window(points)

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
            "calib_start": CALIB_B_START.isoformat(),
            "calib_end": CALIB_B_END.isoformat(),
            "holdout_start": HOLDOUT_START.isoformat(),
            "holdout_end": HOLDOUT_END.isoformat(),
            "n_calib": len(calib),
            "n_holdout": len(holdout),
            "rule": (
                "Pilot B: calib restarts the day after Pilot A's own "
                "diagnosed local trough (2020-02-25); same fixed holdout as "
                "Pilot A for direct comparison"
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
            "Pilot B: disclosed follow-up informed by Pilot A's diagnosis; "
            "Pilot A's own protocol, code, and result are unchanged.",
            "False model_beats_baseline is a VALID complete result -- no further retune.",
            "fit_exponential_growth receives only calib points; holdout used solely for RMSE.",
        ),
    )
    return report, fit


# --- Pilot C: change-point / segmented regression on Pilot A's full window --


@dataclass(frozen=True)
class ChangepointFit:
    breakpoint_date: dt.date
    n_segment1: int
    n_segment2: int
    segment1: FittedExponentialGrowth
    segment2: FittedExponentialGrowth
    rss_segment1: float
    rss_segment2: float
    total_rss: float
    candidates_tried: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "breakpoint_date": self.breakpoint_date.isoformat(),
            "n_segment1": self.n_segment1,
            "n_segment2": self.n_segment2,
            "segment1": self.segment1.to_dict(),
            "segment2": self.segment2.to_dict(),
            "rss_segment1": self.rss_segment1,
            "rss_segment2": self.rss_segment2,
            "total_rss": self.total_rss,
            "candidates_tried": self.candidates_tried,
        }


def _log_fit_rss(segment: List[DailyPoint], fit: FittedExponentialGrowth) -> float:
    """Residual sum of squares of a log-linear fit on its own segment."""
    rss = 0.0
    for p in segment:
        t_days = float((p.date - fit.t_ref).days)
        y_pred = fit.ln_cases0 + fit.r * t_days
        y_obs = math.log(p.cases_7day_avg)
        rss += (y_obs - y_pred) ** 2
    return rss


def fit_changepoint_growth(
    calib: List[DailyPoint],
    *,
    min_segment_points: int = MIN_SEGMENT_POINTS,
) -> ChangepointFit:
    """Grid search for a single breakpoint minimizing total two-segment RSS.

    Receives ONLY calib points -- the breakpoint search, both segment fits,
    and their residuals are computed entirely within ``calib``; this
    function never references a holdout window.
    """
    n = len(calib)
    if n < 2 * min_segment_points:
        raise ScopeViolationError(
            f"fit_changepoint_growth: need >= {2 * min_segment_points} calib "
            f"points for two segments of >= {min_segment_points} each; got {n}"
        )
    best: Tuple[float, int, FittedExponentialGrowth, FittedExponentialGrowth, float, float] | None = None
    tried = 0
    for i in range(min_segment_points, n - min_segment_points):
        seg1 = calib[: i + 1]
        seg2 = calib[i + 1 :]
        tried += 1
        fit1 = fit_exponential_growth(seg1)
        fit2 = fit_exponential_growth(seg2)
        rss1 = _log_fit_rss(seg1, fit1)
        rss2 = _log_fit_rss(seg2, fit2)
        total = rss1 + rss2
        if best is None or total < best[0]:
            best = (total, i, fit1, fit2, rss1, rss2)
    assert best is not None
    total, i, fit1, fit2, rss1, rss2 = best
    return ChangepointFit(
        breakpoint_date=calib[i].date,
        n_segment1=i + 1,
        n_segment2=n - i - 1,
        segment1=fit1,
        segment2=fit2,
        rss_segment1=rss1,
        rss_segment2=rss2,
        total_rss=total,
        candidates_tried=tried,
    )


def run_covid_pilot_changepoint(
    data_path: str | Path,
    *,
    domain: str = DOMAIN_NAME,
) -> Tuple[ValidationReport, ChangepointFit]:
    """Pilot C: two-segment change-point fit on Pilot A's full calib window.

    The breakpoint is found within calib only (grid search minimizing total
    RSS); only the second (most recent) segment's rate is used to
    extrapolate into the same fixed holdout window as Pilot A. Does not
    modify or re-run Pilot A.
    """
    points = load_world_daily(data_path)
    calib, holdout = split_by_date(points)  # same fixed calib/holdout as Pilot A

    cp = fit_changepoint_growth(calib)
    base = persistence_baseline_covid(calib)

    hold_obs = [p.cases_7day_avg for p in holdout]
    model_pred = [
        predict_exponential(
            float((p.date - cp.segment2.t_ref).days),
            r=cp.segment2.r,
            ln_cases0=cp.segment2.ln_cases0,
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
                "Pilot C: same fixed calib/holdout as Pilot A; a breakpoint "
                "is grid-searched within calib only (min RSS), and only the "
                "second segment's rate is extrapolated into holdout"
            ),
        },
        model_rmse_holdout=model_rmse,
        baseline_rmse_holdout=baseline_rmse,
        model_beats_baseline=beats,
        fitted_parameters=cp.to_dict(),
        source_citation=SOURCE_CITATION,
        baseline_value=base,
        n_holdout=len(holdout),
        notes=(
            DATA_PROVENANCE_NOTE,
            "Pilot C: disclosed follow-up informed by Pilot A's diagnosis; "
            "Pilot A's own protocol, code, and result are unchanged.",
            "Breakpoint and both segment fits computed entirely within calib "
            "(no holdout peeking); only the second segment's rate is "
            "extrapolated forward.",
            "False model_beats_baseline is a VALID complete result -- no further retune.",
        ),
    )
    return report, cp


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
    # Pilot B: shorter post-trough window
    "PEAK_DATE_IN_PILOT_A_CALIB",
    "TROUGH_DATE_IN_PILOT_A_CALIB",
    "CALIB_B_START",
    "CALIB_B_END",
    "split_by_date_short_window",
    "run_covid_pilot_short_window",
    # Pilot C: change-point / segmented regression
    "MIN_SEGMENT_POINTS",
    "ChangepointFit",
    "fit_changepoint_growth",
    "run_covid_pilot_changepoint",
]
