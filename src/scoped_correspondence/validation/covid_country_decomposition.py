"""COVID World-vs-country decomposition (Milestone 6f; NONSTATIONARY_ROADMAP.md package 2).

Response to prompts/Answers/nicht_stationäre_Treiber/SCF_Nichtstationaere_Treiber_und_Kippen.md
(Astra, 2026-09-21) section 4 (heterogeneity/mixture identity) and section
8 package 2 ("COVID: Länderkomponenten statt nur Weltmittel"): Pilot A
(covid_pilot.py) fits ONE exponential rate to the World aggregate over
2020-01-27 to 2020-03-11 and finds it badly underestimates the holdout.
This module tests directly, on real per-country data, how much of that
failure is explained by CHANGING COUNTRY COMPOSITION (China's share of
world cases collapses from ~98% to <1% over the same window) rather than
a single global epidemiological rate change.

Decomposition: World(t) = China(t) + RestOfWorld(t) exactly (RestOfWorld
is computed as World minus China, not fetched separately -- see
data/real_data_manifest.json entry owid_covid_china_world_daily_2020).
Each component is fit its OWN constant exponential rate over calib
(reusing covid_pilot.fit_exponential_growth); the two component forecasts
are extrapolated SEPARATELY into holdout and summed to predict World.

Protocol (immutable before any fit -- fixed using the same external
2020-03-11 WHO-pandemic-declaration anchor and the same 2020-03-12 to
2020-03-25 holdout as Pilot A; calib starts ONE DAY LATER than Pilot A,
2020-01-28 instead of 2020-01-27, purely because China's weekly_cases in
this file is not yet defined on 2020-01-27 -- a data-availability
constraint, disclosed here, not a choice made to improve the result):
  - Macro: China_7day_avg, RestOfWorld_7day_avg, World_7day_avg (all
    weekly_cases/7 for the respective location)
  - Calib window: 2020-01-28 -- 2020-03-11
  - Holdout window: 2020-03-12 -- 2020-03-25 (identical to Pilot A)
  - Model: fit China's own rate and RestOfWorld's own rate independently
    on calib; extrapolate each separately into holdout; sum for the
    decomposed World prediction
  - Comparison models: (a) a single aggregate exponential fit on this
    same (1-day-later) window, for a fair apples-to-apples baseline
    against the decomposed model; (b) persistence (last calib World
    value, identical to Pilot A's baseline value by construction)
  - Metric: RMSE of the World prediction on the holdout window

This is ONE domain, ONE two-component decomposition, ONE fixed window.
No claim that a two-component split is the correct or complete
decomposition (a real analysis would use all ~200 countries); this
tests the qualitative hypothesis with the two largest, best-documented
components of the actual historical story (initial China outbreak vs.
the rest of the world) using genuinely real data. A result showing the
decomposed model does NOT improve on the aggregate would be an equally
valid, reportable outcome -- it happens not to be what was found here
(see docs/covid_pilot.md's Pilot D section), but this is reported before
any retuning, per the same discipline as every other pilot in this repo.
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
from scoped_correspondence.validation.covid_pilot import (
    DailyPoint,
    FittedExponentialGrowth,
    fit_exponential_growth,
    predict_exponential,
)

# --- Fixed protocol (locked BEFORE fit) -------------------------------------

DOMAIN_NAME = "owid-jhu-covid-china-vs-restofworld"
SOURCE_RELATIVE = "data/owid_covid_china_world_daily_2020.csv"
SOURCE_CITATION = (
    "Our World in Data COVID-19 dataset (JHU CSSE historical compact series); "
    "data/real_data_manifest.json entry owid_covid_china_world_daily_2020"
)
CALIB_START = "2020-01-28"  # one day later than Pilot A: China's weekly_cases undefined on 2020-01-27
CALIB_END = "2020-03-11"  # WHO pandemic declaration -- same external anchor as Pilot A
HOLDOUT_START = "2020-03-12"  # identical to Pilot A
HOLDOUT_END = "2020-03-25"  # identical to Pilot A

DATA_PROVENANCE_NOTE = (
    "Real per-row data (see data/real_data_manifest.json entry "
    "owid_covid_china_world_daily_2020); attribution required under "
    "CC BY 4.0: 'Data: Our World in Data / Johns Hopkins University CSSE "
    "COVID-19 Data Repository.' RestOfWorld is computed as World minus "
    "China from this file, not fetched as an independent series."
)


@dataclass(frozen=True)
class DecompositionReport:
    china_fit: FittedExponentialGrowth
    row_fit: FittedExponentialGrowth
    aggregate_fit_same_window: FittedExponentialGrowth
    decomposed_rmse_holdout: float
    aggregate_rmse_holdout: float
    persistence_rmse_holdout: float
    baseline_value: float
    n_calib: int
    n_holdout: int
    decomposed_beats_aggregate: bool
    decomposed_beats_persistence: bool

    def to_dict(self) -> Dict[str, Any]:
        return {
            "china_fit": self.china_fit.to_dict(),
            "row_fit": self.row_fit.to_dict(),
            "aggregate_fit_same_window": self.aggregate_fit_same_window.to_dict(),
            "decomposed_rmse_holdout": self.decomposed_rmse_holdout,
            "aggregate_rmse_holdout": self.aggregate_rmse_holdout,
            "persistence_rmse_holdout": self.persistence_rmse_holdout,
            "baseline_value": self.baseline_value,
            "n_calib": self.n_calib,
            "n_holdout": self.n_holdout,
            "decomposed_beats_aggregate": self.decomposed_beats_aggregate,
            "decomposed_beats_persistence": self.decomposed_beats_persistence,
        }


def load_china_world_series(
    path: str | Path,
) -> Tuple[List[DailyPoint], List[DailyPoint], List[DailyPoint]]:
    """Load China, World, and derived RestOfWorld (World - China) daily points.

    Only dates where BOTH China's and World's weekly_cases are defined are
    kept (structure-specific: China's first date in this file has an empty
    new_cases/weekly_cases field, not imputed).
    """
    p = Path(path)
    by_loc: Dict[str, Dict[str, dict]] = {}
    with p.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            if row["location"] not in ("China", "World"):
                raise ScopeViolationError(
                    f"load_china_world_series: expected only China/World rows, got {row['location']!r}"
                )
            by_loc.setdefault(row["location"], {})[row["date"]] = row
    if "China" not in by_loc or "World" not in by_loc:
        raise ScopeViolationError("load_china_world_series: both China and World rows are required")

    china_pts: List[DailyPoint] = []
    world_pts: List[DailyPoint] = []
    row_pts: List[DailyPoint] = []
    for date in sorted(set(by_loc["China"]) & set(by_loc["World"])):
        c_row = by_loc["China"][date]
        w_row = by_loc["World"][date]
        if not c_row["weekly_cases"] or not w_row["weekly_cases"]:
            continue
        china_weekly = float(c_row["weekly_cases"])
        world_weekly = float(w_row["weekly_cases"])
        row_weekly = world_weekly - china_weekly
        if row_weekly < 0:
            raise ScopeViolationError(
                f"load_china_world_series: RestOfWorld weekly_cases negative on {date} "
                f"(World={world_weekly!r} < China={china_weekly!r})"
            )
        china_pts.append(
            DailyPoint(
                date=dt.date.fromisoformat(date),
                new_cases=float(c_row["new_cases"] or 0.0),
                weekly_cases=china_weekly,
                cases_7day_avg=china_weekly / 7.0,
            )
        )
        world_pts.append(
            DailyPoint(
                date=dt.date.fromisoformat(date),
                new_cases=float(w_row["new_cases"] or 0.0),
                weekly_cases=world_weekly,
                cases_7day_avg=world_weekly / 7.0,
            )
        )
        row_pts.append(
            DailyPoint(
                date=dt.date.fromisoformat(date),
                new_cases=float(w_row["new_cases"] or 0.0) - float(c_row["new_cases"] or 0.0),
                weekly_cases=row_weekly,
                cases_7day_avg=row_weekly / 7.0,
            )
        )
    if not china_pts:
        raise ScopeViolationError("load_china_world_series: no overlapping dates with both weekly_cases defined")
    return china_pts, world_pts, row_pts


def _split(points: List[DailyPoint]) -> Tuple[List[DailyPoint], List[DailyPoint]]:
    calib = [p for p in points if CALIB_START <= p.date.isoformat() <= CALIB_END]
    holdout = [p for p in points if HOLDOUT_START <= p.date.isoformat() <= HOLDOUT_END]
    if not calib:
        raise ScopeViolationError("_split: empty calibration window")
    if not holdout:
        raise ScopeViolationError("_split: empty holdout window")
    return calib, holdout


def run_covid_country_decomposition(data_path: str | Path) -> Tuple[ValidationReport, DecompositionReport]:
    """China + RestOfWorld fit separately on calib, summed for the World holdout prediction."""
    china_pts, world_pts, row_pts = load_china_world_series(data_path)
    china_calib, china_hold = _split(china_pts)
    world_calib, world_hold = _split(world_pts)
    row_calib, row_hold = _split(row_pts)
    if not (len(china_calib) == len(world_calib) == len(row_calib)):
        raise ScopeViolationError("run_covid_country_decomposition: calib slices must be aligned across components")

    china_fit = fit_exponential_growth(china_calib)
    row_fit = fit_exponential_growth(row_calib)
    aggregate_fit = fit_exponential_growth(world_calib)  # single-rate fit on the SAME window, for a fair comparison

    hold_obs_world = [p.cases_7day_avg for p in world_hold]
    china_pred = [
        predict_exponential(float((p.date - china_fit.t_ref).days), r=china_fit.r, ln_cases0=china_fit.ln_cases0)
        for p in china_hold
    ]
    row_pred = [
        predict_exponential(float((p.date - row_fit.t_ref).days), r=row_fit.r, ln_cases0=row_fit.ln_cases0)
        for p in row_hold
    ]
    decomposed_pred = [c + r for c, r in zip(china_pred, row_pred)]
    aggregate_pred = [
        predict_exponential(
            float((p.date - aggregate_fit.t_ref).days), r=aggregate_fit.r, ln_cases0=aggregate_fit.ln_cases0
        )
        for p in world_hold
    ]
    baseline_value = world_calib[-1].cases_7day_avg
    baseline_pred = [baseline_value] * len(world_hold)

    decomposed_rmse = rmse(hold_obs_world, decomposed_pred)
    aggregate_rmse = rmse(hold_obs_world, aggregate_pred)
    persistence_rmse = rmse(hold_obs_world, baseline_pred)

    decomp = DecompositionReport(
        china_fit=china_fit,
        row_fit=row_fit,
        aggregate_fit_same_window=aggregate_fit,
        decomposed_rmse_holdout=decomposed_rmse,
        aggregate_rmse_holdout=aggregate_rmse,
        persistence_rmse_holdout=persistence_rmse,
        baseline_value=baseline_value,
        n_calib=len(world_calib),
        n_holdout=len(world_hold),
        decomposed_beats_aggregate=bool(decomposed_rmse < aggregate_rmse),
        decomposed_beats_persistence=bool(decomposed_rmse < persistence_rmse),
    )

    report = ValidationReport(
        domain=DOMAIN_NAME,
        macro="cases_7day_avg (China + RestOfWorld, summed to predict World)",
        split={
            "calib_start": CALIB_START,
            "calib_end": CALIB_END,
            "holdout_start": HOLDOUT_START,
            "holdout_end": HOLDOUT_END,
            "n_calib": decomp.n_calib,
            "n_holdout": decomp.n_holdout,
            "rule": (
                "calib starts one day later than Pilot A (2020-01-28, data "
                "availability, not choice); calib_end/holdout identical to Pilot A"
            ),
        },
        model_rmse_holdout=decomposed_rmse,
        baseline_rmse_holdout=persistence_rmse,
        model_beats_baseline=decomp.decomposed_beats_persistence,
        fitted_parameters=decomp.to_dict(),
        source_citation=SOURCE_CITATION,
        baseline_value=baseline_value,
        n_holdout=decomp.n_holdout,
        notes=(
            DATA_PROVENANCE_NOTE,
            "Decomposed (China+RestOfWorld, separately extrapolated, then summed) "
            "vs. a single aggregate exponential fit on the SAME window vs. persistence.",
            "fit_exponential_growth receives only calib points for each component; "
            "holdout used solely for RMSE.",
            "No claim of a complete or unique decomposition; two components only "
            "(China, RestOfWorld), matching the best-documented part of the "
            "historical story.",
        ),
    )
    return report, decomp


# --- Mixture effective-rate diagnostic (Astra section 4 identity) ---------


@dataclass(frozen=True)
class MixtureRatePoint:
    date: dt.date
    china_share: float
    mixture_effective_rate: float
    actual_local_rate: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "date": self.date.isoformat(),
            "china_share": self.china_share,
            "mixture_effective_rate": self.mixture_effective_rate,
            "actual_local_rate": self.actual_local_rate,
            "difference": self.actual_local_rate - self.mixture_effective_rate,
        }


def mixture_effective_rate_diagnostic(data_path: str | Path) -> List[MixtureRatePoint]:
    """Compare Astra's mixture identity r_eff(t) = w_China(t)*r_China + w_RoW(t)*r_RoW
    (using each component's OWN calib-fitted constant rate and the ACTUAL
    observed daily composition weights) against the World series' own
    actual local growth rate (centered 3-day log-difference), across the
    full available window (calib + holdout).

    This is a diagnostic, not a forecast: it uses the true weights at each
    date (not the idealized closed-form exponential-mixture weights from
    the synthetic example in SCF_Nichtstationaere_Treiber_und_Kippen.md
    section 4), so it can only be computed in-sample/retrospectively, and
    it says nothing about the earlier and separate reporting-artifact
    finding (China's Feb 12-13 case-definition change) except by showing
    where the mixture-implied rate and the actual local rate disagree.
    """
    china_pts, world_pts, row_pts = load_china_world_series(data_path)
    china_calib, _ = _split(china_pts)
    row_calib, _ = _split(row_pts)
    china_fit = fit_exponential_growth(china_calib)
    row_fit = fit_exponential_growth(row_calib)

    n = len(world_pts)
    if n < 3:
        raise ScopeViolationError("mixture_effective_rate_diagnostic: need >= 3 points for a centered local rate")

    points: List[MixtureRatePoint] = []
    for i in range(1, n - 1):
        china = china_pts[i].cases_7day_avg
        world = world_pts[i].cases_7day_avg
        row = row_pts[i].cases_7day_avg
        if world <= 0 or china < 0 or row < 0:
            raise ScopeViolationError(f"mixture_effective_rate_diagnostic: non-positive series value at {world_pts[i].date}")
        w_china = china / world
        w_row = row / world
        r_eff = w_china * china_fit.r + w_row * row_fit.r
        w_before = world_pts[i - 1].cases_7day_avg
        w_after = world_pts[i + 1].cases_7day_avg
        actual_local_rate = (math.log(w_after) - math.log(w_before)) / 2.0
        points.append(
            MixtureRatePoint(
                date=world_pts[i].date,
                china_share=w_china,
                mixture_effective_rate=r_eff,
                actual_local_rate=actual_local_rate,
            )
        )
    return points


__all__ = [
    "CALIB_START",
    "CALIB_END",
    "HOLDOUT_START",
    "HOLDOUT_END",
    "DATA_PROVENANCE_NOTE",
    "DecompositionReport",
    "load_china_world_series",
    "run_covid_country_decomposition",
    "MixtureRatePoint",
    "mixture_effective_rate_diagnostic",
]
