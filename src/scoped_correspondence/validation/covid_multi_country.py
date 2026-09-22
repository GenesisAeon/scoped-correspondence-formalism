"""Multi-country / multi-window generalization of the COVID growth pilot (Milestone 51).

MECHANISTIC_VALIDATION_ROADMAP.md package 5, response to
prompts/Answers/nicht_stationäre_Treiber/SCF_Review_f8e249f.md (Astra,
2026-09-21): "Mehrere unabhängige Länder- und Zeitfenster mit
unverändertem Verfahren (nicht nur die bereits bekannte
China/Rest-Zerlegung auf demselben März-2020-Fenster)."

Applies `covid_pilot.py`'s EXISTING, UNCHANGED exponential-growth fitting
procedure (`fit_exponential_growth`, `predict_exponential`,
`persistence_baseline_covid`) -- imported, never reimplemented or
retuned -- to:

1. TWO NEW COUNTRIES (Germany, United States) over the EXACT SAME fixed
   calendar window as Pilot A/B (2020-01-27 to 2020-03-25) -- tests
   whether the same procedure generalizes across countries, not just
   the already-known World/China decomposition.
2. ONE NEW TIME WINDOW (World aggregate, anchored on the WHO's 2021-11-26
   designation of Omicron as a Variant of Concern -- an externally
   documented milestone, chosen the SAME way Pilot A's own window was
   anchored on the WHO pandemic declaration, NOT by looking at the data)
   -- tests whether the procedure generalizes across TIME, using the
   already-stored World series (data/owid_covid_world_daily_2020_2023.csv
   already covers late 2021).

No parameter, window boundary, or country choice here was selected by
looking at any of these series' own fit quality -- all boundaries are
either the SAME as Pilot A/B (country test) or mechanically derived from
an external date with the SAME calib/holdout LENGTHS as Pilot A (window
test), matching this repository's anti-data-snooping discipline
throughout.

model_beats_baseline=False is a VALID, complete result for any of these
new pilots and must not trigger a retune (same discipline as
covid_pilot.py's own Pilot A).
"""

from __future__ import annotations

import csv
import datetime as dt
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple

from scoped_correspondence.errors import ScopeViolationError
from scoped_correspondence.validation.core import rmse
from scoped_correspondence.validation.covid_pilot import (
    DailyPoint,
    FittedExponentialGrowth,
    fit_exponential_growth,
    persistence_baseline_covid,
    predict_exponential,
)

SOURCE = (
    "Applies validation.covid_pilot's existing, unchanged exponential-growth "
    "fitting procedure to new countries and a new time window, per Astra's "
    "2026-09-21 review of commit f8e249f (SCF_Review_f8e249f.md)."
)

DATA_PROVENANCE_NOTE = (
    "Germany/United States: real per-row data (see data/real_data_manifest.json "
    "entry owid_covid_germany_usa_daily_2020); attribution required under CC BY "
    "4.0: 'Data: Our World in Data / Johns Hopkins University CSSE COVID-19 "
    "Data Repository.' Omicron-window World data reuses the already-stored, "
    "already-verified data/owid_covid_world_daily_2020_2023.csv -- no new fetch."
)

# --- Fixed protocol #1: SAME calendar window as Pilot A/B, applied UNCHANGED to new countries. ---
COUNTRY_CALIB_START = dt.date(2020, 1, 27)
COUNTRY_CALIB_END = dt.date(2020, 3, 11)
COUNTRY_HOLDOUT_START = dt.date(2020, 3, 12)
COUNTRY_HOLDOUT_END = dt.date(2020, 3, 25)

# --- Fixed protocol #2: SAME procedure, independent time window anchored on an
# externally documented milestone (WHO's 2021-11-26 Omicron VOC designation),
# with the SAME calib (45 days) / holdout (14 days) LENGTHS as Pilot A. ---
OMICRON_VOC_ANCHOR = dt.date(2021, 11, 26)
WINDOW2_CALIB_START = dt.date(2021, 10, 13)
WINDOW2_CALIB_END = OMICRON_VOC_ANCHOR
WINDOW2_HOLDOUT_START = dt.date(2021, 11, 27)
WINDOW2_HOLDOUT_END = dt.date(2021, 12, 10)


def load_country_daily(path: str | Path, location: str) -> List[DailyPoint]:
    """Generalizes covid_pilot.load_world_daily to an arbitrary ``location`` string.

    Reuses the SAME DailyPoint shape and the SAME weekly_cases/7 smoothing
    convention -- rows for other locations in the same file are simply
    skipped (not an error; the source file always contains many locations).
    """
    p = Path(path)
    points: List[DailyPoint] = []
    with p.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            if row["location"] != location:
                continue
            wk = row["weekly_cases"]
            if wk in ("", None):
                continue
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
        raise ScopeViolationError(f"load_country_daily: no rows with weekly_cases found for location={location!r}")
    return points


def _split_fixed_window(
    points: List[DailyPoint], calib_start: dt.date, calib_end: dt.date, holdout_start: dt.date, holdout_end: dt.date
) -> Tuple[List[DailyPoint], List[DailyPoint]]:
    if calib_end >= holdout_start:
        raise ScopeViolationError("_split_fixed_window: calib_end must be before holdout_start")
    calib = [p for p in points if calib_start <= p.date <= calib_end]
    holdout = [p for p in points if holdout_start <= p.date <= holdout_end]
    if not calib:
        raise ScopeViolationError("_split_fixed_window: empty calibration window")
    if not holdout:
        raise ScopeViolationError("_split_fixed_window: empty holdout window")
    return calib, holdout


@dataclass(frozen=True)
class GeneralizationPilotReport:
    label: str
    location: str
    calib_start: str
    calib_end: str
    holdout_start: str
    holdout_end: str
    n_calib: int
    n_holdout: int
    fit_failed: bool
    fit_failure_reason: str | None
    fitted: FittedExponentialGrowth | None = None
    model_rmse_holdout: float | None = None
    baseline_rmse_holdout: float | None = None
    baseline_value: float | None = None
    model_beats_baseline: bool | None = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "label": self.label,
            "location": self.location,
            "calib_start": self.calib_start,
            "calib_end": self.calib_end,
            "holdout_start": self.holdout_start,
            "holdout_end": self.holdout_end,
            "n_calib": self.n_calib,
            "n_holdout": self.n_holdout,
            "fit_failed": self.fit_failed,
            "fit_failure_reason": self.fit_failure_reason,
            "fitted": self.fitted.to_dict() if self.fitted is not None else None,
            "model_rmse_holdout": self.model_rmse_holdout,
            "baseline_rmse_holdout": self.baseline_rmse_holdout,
            "baseline_value": self.baseline_value,
            "model_beats_baseline": self.model_beats_baseline,
        }


def run_generalization_pilot(
    path: str | Path,
    location: str,
    *,
    label: str,
    calib_start: dt.date,
    calib_end: dt.date,
    holdout_start: dt.date,
    holdout_end: dt.date,
) -> GeneralizationPilotReport:
    """fit_exponential_growth/predict_exponential/persistence_baseline_covid,
    UNCHANGED from covid_pilot.py, applied to an arbitrary (location, fixed
    window) pair.

    HONEST FAILURE HANDLING: fit_exponential_growth correctly REFUSES a
    zero-count day (log-fit is undefined at 0) -- rather than silently
    adjusting the window per-country (which would break "unverändertes
    Verfahren"), a fit failure here is reported as a genuine, informative
    result in its own right (fit_failed=True), not swallowed or worked
    around. Individual-country early-2020 counts include zero/near-zero
    days that the World AGGREGATE smooths over -- this is real epidemic
    data behavior, not a bug.
    """
    points = load_country_daily(path, location)
    calib, holdout = _split_fixed_window(points, calib_start, calib_end, holdout_start, holdout_end)

    try:
        fitted = fit_exponential_growth(calib)
    except ScopeViolationError as exc:
        return GeneralizationPilotReport(
            label=label,
            location=location,
            calib_start=calib_start.isoformat(),
            calib_end=calib_end.isoformat(),
            holdout_start=holdout_start.isoformat(),
            holdout_end=holdout_end.isoformat(),
            n_calib=len(calib),
            n_holdout=len(holdout),
            fit_failed=True,
            fit_failure_reason=str(exc),
        )

    predicted = [predict_exponential((p.date - fitted.t_ref).days, r=fitted.r, ln_cases0=fitted.ln_cases0) for p in holdout]
    observed = [p.cases_7day_avg for p in holdout]
    baseline_value = persistence_baseline_covid(calib)
    baseline_predicted = [baseline_value] * len(holdout)

    model_rmse = rmse(observed, predicted)
    baseline_rmse = rmse(observed, baseline_predicted)

    return GeneralizationPilotReport(
        label=label,
        location=location,
        calib_start=calib_start.isoformat(),
        calib_end=calib_end.isoformat(),
        holdout_start=holdout_start.isoformat(),
        holdout_end=holdout_end.isoformat(),
        n_calib=len(calib),
        n_holdout=len(holdout),
        fit_failed=False,
        fit_failure_reason=None,
        fitted=fitted,
        model_rmse_holdout=model_rmse,
        baseline_rmse_holdout=baseline_rmse,
        baseline_value=baseline_value,
        model_beats_baseline=bool(model_rmse < baseline_rmse),
    )


def run_all_generalization_pilots(germany_usa_path: str | Path, world_path: str | Path) -> Tuple[GeneralizationPilotReport, ...]:
    """The 3 new pilots: Germany (2020 window), United States (2020 window),
    World (Omicron-anchored 2021 window) -- SAME procedure, 3 independent
    (country, window) applications.
    """
    reports = [
        run_generalization_pilot(
            germany_usa_path, "Germany", label="germany_2020_pilotA_window",
            calib_start=COUNTRY_CALIB_START, calib_end=COUNTRY_CALIB_END,
            holdout_start=COUNTRY_HOLDOUT_START, holdout_end=COUNTRY_HOLDOUT_END,
        ),
        run_generalization_pilot(
            germany_usa_path, "United States", label="united_states_2020_pilotA_window",
            calib_start=COUNTRY_CALIB_START, calib_end=COUNTRY_CALIB_END,
            holdout_start=COUNTRY_HOLDOUT_START, holdout_end=COUNTRY_HOLDOUT_END,
        ),
        run_generalization_pilot(
            world_path, "World", label="world_2021_omicron_window",
            calib_start=WINDOW2_CALIB_START, calib_end=WINDOW2_CALIB_END,
            holdout_start=WINDOW2_HOLDOUT_START, holdout_end=WINDOW2_HOLDOUT_END,
        ),
    ]
    return tuple(reports)


__all__ = [
    "SOURCE",
    "DATA_PROVENANCE_NOTE",
    "COUNTRY_CALIB_START",
    "COUNTRY_CALIB_END",
    "COUNTRY_HOLDOUT_START",
    "COUNTRY_HOLDOUT_END",
    "OMICRON_VOC_ANCHOR",
    "WINDOW2_CALIB_START",
    "WINDOW2_CALIB_END",
    "WINDOW2_HOLDOUT_START",
    "WINDOW2_HOLDOUT_END",
    "GeneralizationPilotReport",
    "load_country_daily",
    "run_generalization_pilot",
    "run_all_generalization_pilots",
]
