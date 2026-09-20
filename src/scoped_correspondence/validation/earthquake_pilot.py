"""USGS M>=6.0 earthquake annual-count pilot (Milestone 6d).

Real-data pilot built directly on a verified dataset (see
docs/real_data_provenance.md / data/real_data_manifest.json), structurally
analogous to the Cygnus/COVID/NOAA pilots: calib-only fit, persistence
baseline, honest holdout RMSE comparison, no retuning after seeing the
result.

Protocol (immutable before any fit -- fixed using round calendar
boundaries, not chosen by looking at the fit quality):
  - Macro: worldwide annual COUNT of earthquakes with magnitude >= 6.0
    (the source file's own minmagnitude filter; see
    data/real_data_manifest.json)
  - Calib window: 2000-2019 (twenty full calendar years)
  - Holdout window: 2020-2025 (six full calendar years; 2026 is EXCLUDED
    because the source catalog is truncated at 2026-09-20 and a partial
    year is not comparable to a full year)
  - Baseline: persistence = last calib year's (2019) count held constant
  - Metric: RMSE on the holdout years
  - Free params (the calib mean annual rate) estimated ONLY on calib; no
    holdout peeking

Model: a constant-rate (homogeneous Poisson process) prediction --
predicted_count(year) = mean annual count over calib, for every holdout
year. This is the standard textbook baseline model for a large-earthquake
occurrence process at the multi-decade timescale; no claim is made that
the true process is exactly Poisson, nor any connection to
percolation/core.py's branching-process framing without its own separate
derivation.

This is ONE domain, ONE macro, ONE fixed window. A model_beats_baseline
=False result is a VALID complete outcome and must not trigger a retune.
"""

from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple

from scoped_correspondence.errors import ScopeViolationError
from scoped_correspondence.validation.core import ValidationReport, rmse

# --- Fixed protocol (locked BEFORE fit) -------------------------------------

DOMAIN_NAME = "usgs-earthquakes-m6plus"
MACRO_NAME = "annual_count_m6plus"
MACRO_UNIT = "earthquakes/year"
SOURCE_RELATIVE = "data/usgs_earthquakes_m6plus_2000_2026.csv"
SOURCE_CITATION = (
    "USGS Earthquake Catalog (ComCat) via the FDSN Event Web Service; "
    "data/real_data_manifest.json entry usgs_earthquakes_m6plus_2000_2026"
)
CALIB_START_YEAR = 2000
CALIB_END_YEAR = 2019
HOLDOUT_START_YEAR = 2020
HOLDOUT_END_YEAR = 2025  # 2026 excluded: source catalog truncated at 2026-09-20

DATA_PROVENANCE_NOTE = (
    "Real per-row data (see data/real_data_manifest.json entry "
    "usgs_earthquakes_m6plus_2000_2026); U.S. Government work, public "
    "domain. This constant-rate fit does NOT claim any connection to "
    "percolation/core.py's branching-process threshold framing without "
    "its own separate derivation; see docs/structural_relations.md bridge "
    "B6 for the kind of comparison that WOULD need."
)


@dataclass(frozen=True)
class YearlyCount:
    year: int
    count: int


@dataclass(frozen=True)
class FittedConstantRate:
    mean_annual_count: float
    n_calib_years: int
    total_calib_events: int
    note: str = "fitted_parameters estimated exclusively on calibration years"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mean_annual_count": self.mean_annual_count,
            "n_calib_years": self.n_calib_years,
            "total_calib_events": self.total_calib_events,
            "note": self.note,
        }


def load_annual_counts(path: str | Path) -> List[YearlyCount]:
    """Count events per calendar year from the raw USGS CSV (structure-specific)."""
    p = Path(path)
    counts: Dict[int, int] = {}
    with p.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            mag = float(row["mag"])
            if mag < 6.0:
                raise ScopeViolationError(
                    f"load_annual_counts: expected only magnitude>=6.0 rows, got {mag!r}"
                )
            year = int(row["time"][:4])
            counts[year] = counts.get(year, 0) + 1
    if not counts:
        raise ScopeViolationError("load_annual_counts: no rows found")
    return [YearlyCount(year=y, count=counts[y]) for y in sorted(counts)]


def split_by_year(
    points: List[YearlyCount],
    *,
    calib_start: int = CALIB_START_YEAR,
    calib_end: int = CALIB_END_YEAR,
    holdout_start: int = HOLDOUT_START_YEAR,
    holdout_end: int = HOLDOUT_END_YEAR,
) -> Tuple[List[YearlyCount], List[YearlyCount]]:
    """Split by fixed calendar years; refuse any other split (anti data-snooping)."""
    if (calib_start, calib_end) != (CALIB_START_YEAR, CALIB_END_YEAR) or (
        holdout_start,
        holdout_end,
    ) != (HOLDOUT_START_YEAR, HOLDOUT_END_YEAR):
        raise ScopeViolationError(
            "split_by_year: requested years differ from the fixed protocol "
            f"(anti data-snooping). requested calib=[{calib_start},{calib_end}] "
            f"holdout=[{holdout_start},{holdout_end}]; fixed calib="
            f"[{CALIB_START_YEAR},{CALIB_END_YEAR}] holdout="
            f"[{HOLDOUT_START_YEAR},{HOLDOUT_END_YEAR}]"
        )
    if calib_end >= holdout_start:
        raise ScopeViolationError(
            "split_by_year: calib_end must be before holdout_start "
            f"(got calib_end={calib_end}, holdout_start={holdout_start})"
        )
    calib = [p for p in points if calib_start <= p.year <= calib_end]
    holdout = [p for p in points if holdout_start <= p.year <= holdout_end]
    if len(calib) != (calib_end - calib_start + 1):
        raise ScopeViolationError(
            f"split_by_year: expected {calib_end - calib_start + 1} full calib "
            f"years, got {len(calib)} (missing years would silently bias the rate)"
        )
    if len(holdout) != (holdout_end - holdout_start + 1):
        raise ScopeViolationError(
            f"split_by_year: expected {holdout_end - holdout_start + 1} full "
            f"holdout years, got {len(holdout)} (missing years would silently bias RMSE)"
        )
    return calib, holdout


def fit_constant_rate(calib: List[YearlyCount]) -> FittedConstantRate:
    """Mean annual count over calib (homogeneous-Poisson rate estimate).

    Receives ONLY calib points -- this function body never references a
    holdout window or any year outside its ``calib`` argument.
    """
    if len(calib) < 2:
        raise ScopeViolationError("fit_constant_rate: need >= 2 calib years")
    total = sum(p.count for p in calib)
    return FittedConstantRate(
        mean_annual_count=total / len(calib),
        n_calib_years=len(calib),
        total_calib_events=total,
    )


def persistence_baseline_quake(calib: List[YearlyCount]) -> float:
    """Last calib year's count, held constant on all holdout years."""
    if not calib:
        raise ScopeViolationError("persistence_baseline_quake: empty calib")
    return float(calib[-1].count)


def run_earthquake_pilot(
    data_path: str | Path,
    *,
    domain: str = DOMAIN_NAME,
) -> Tuple[ValidationReport, FittedConstantRate]:
    """Load -> fixed year split -> fit (calib) -> baseline -> holdout RMSE."""
    points = load_annual_counts(data_path)
    calib, holdout = split_by_year(points)

    fit = fit_constant_rate(calib)  # calib only -- holdout not referenced
    base = persistence_baseline_quake(calib)

    hold_obs = [float(p.count) for p in holdout]
    model_pred = [fit.mean_annual_count] * len(holdout)
    base_pred = [base] * len(holdout)

    model_rmse = rmse(hold_obs, model_pred)
    baseline_rmse = rmse(hold_obs, base_pred)
    beats = bool(model_rmse < baseline_rmse)

    report = ValidationReport(
        domain=domain,
        macro=MACRO_NAME,
        split={
            "calib_start_year": CALIB_START_YEAR,
            "calib_end_year": CALIB_END_YEAR,
            "holdout_start_year": HOLDOUT_START_YEAR,
            "holdout_end_year": HOLDOUT_END_YEAR,
            "n_calib": len(calib),
            "n_holdout": len(holdout),
            "rule": (
                "calib is 2000-2019 (20 full calendar years); holdout is "
                "2020-2025 (6 full calendar years); 2026 excluded as a "
                "partial year (source catalog truncated at 2026-09-20) -- "
                "both fixed before any fit"
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
            "fit_constant_rate receives only calib points; holdout used solely for RMSE.",
            "2026 excluded as a partial year; all reviewed-status events only "
            "(source catalog has no unreviewed rows in this magnitude range).",
        ),
    )
    return report, fit


__all__ = [
    "CALIB_START_YEAR",
    "CALIB_END_YEAR",
    "HOLDOUT_START_YEAR",
    "HOLDOUT_END_YEAR",
    "DATA_PROVENANCE_NOTE",
    "YearlyCount",
    "FittedConstantRate",
    "fit_constant_rate",
    "load_annual_counts",
    "persistence_baseline_quake",
    "run_earthquake_pilot",
    "split_by_year",
]
