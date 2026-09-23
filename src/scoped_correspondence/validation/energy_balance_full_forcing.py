"""CO2-only vs. full (total) forcing comparison for the energy balance model (Milestone 53).

MECHANISTIC_VALIDATION_ROADMAP.md package 5, response to
prompts/Answers/nicht_stationäre_Treiber/SCF_Review_f8e249f.md (Astra,
2026-09-21): "Für die Energiebilanz: die 2026 veröffentlichten 'Indicators
of Global Climate Change 2025' (Forster et al. 2026, Zenodo-archiviert)
als nächste reale Datenquelle für vollständigeres Forcing (CO2-only vs.
Gesamtforcing-Vergleich)."

Uses REAL, freshly-fetched effective radiative forcing (ERF) data from the
ClimateIndicator/data repository (pinned git tag v2026.06.02, matching the
version Astra's review cites) -- data/real_data_manifest.json entry
climateindicator_erf_best_aggregates_1750_2025. This file's own "CO2"
column and "total" column (ALL forcings: CO2, other well-mixed
greenhouse gases, aerosols, ozone, contrails, land use, solar, volcanic)
let this module refit `dynamics.energy_balance.fit_energy_balance_model_from_series`
-- completely UNCHANGED, reused directly -- with two different real
forcing inputs, answering the CO2-only-vs-full-forcing question directly
rather than by proxy.

This is a SEPARATE calculation from `dynamics.energy_balance`'s own
Myhre-formula CO2 forcing (from Mauna Loa CO2 concentrations): as a
sanity cross-check, the two independently-sourced CO2-only forcing
estimates should roughly agree in the overlap period, which this module
verifies before drawing any RMSE conclusion.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np

from scoped_correspondence.errors import ScopeViolationError
from scoped_correspondence.dynamics.energy_balance import (
    EnergyBalanceFitResult,
    fit_energy_balance_model_from_series,
)

SOURCE = (
    "Smith, Walsh, Gillett, Hausfather, Palmer, von Schuckmann, Ribes, Forster "
    "et al., Indicators of Global Climate Change 2025, DOI 10.5281/zenodo.7883757 "
    "(effective radiative forcing best-estimate aggregates, ClimateIndicator/data "
    "repository, pinned git tag v2026.06.02)."
)

DATA_PROVENANCE_NOTE = (
    "Real per-row data (see data/real_data_manifest.json entry "
    "climateindicator_erf_best_aggregates_1750_2025); CC BY 4.0, attribution "
    "required: 'Indicators of Global Climate Change 2025, DOI 10.5281/zenodo.7883757.'"
)


def load_erf_series(path: str | Path) -> Dict[int, Dict[str, float]]:
    """year -> {'CO2': ..., 'total': ..., 'anthro': ...} from the ERF aggregates CSV.

    ``time`` in the source file is a mid-year value (e.g. 1959.5 for
    calendar year 1959); the calendar year is recovered by flooring.
    """
    p = Path(path)
    out: Dict[int, Dict[str, float]] = {}
    with p.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            year = int(float(row["time"]))
            out[year] = {
                "CO2": float(row["CO2"]),
                "total": float(row["total"]),
                "anthro": float(row["anthro"]),
            }
    if not out:
        raise ScopeViolationError("load_erf_series: no rows found")
    return out


@dataclass(frozen=True)
class ForcingComparisonReport:
    years: Tuple[int, ...]
    co2_forcing_cross_check_max_abs_diff: float
    fit_co2_only_erf: EnergyBalanceFitResult
    fit_total_forcing: EnergyBalanceFitResult
    fit_co2_only_myhre: EnergyBalanceFitResult
    total_forcing_beats_co2_only_raw_reference: bool
    fit_co2_only_erf_rereferenced: EnergyBalanceFitResult
    fit_total_forcing_rereferenced: EnergyBalanceFitResult
    fit_co2_only_myhre_rereferenced: EnergyBalanceFitResult
    total_forcing_beats_co2_only_rereferenced: bool

    def to_dict(self) -> Dict[str, Any]:
        return {
            "years": list(self.years),
            "co2_forcing_cross_check_max_abs_diff": self.co2_forcing_cross_check_max_abs_diff,
            "fit_co2_only_erf": self.fit_co2_only_erf.to_dict(),
            "fit_total_forcing": self.fit_total_forcing.to_dict(),
            "fit_co2_only_myhre": self.fit_co2_only_myhre.to_dict(),
            "total_forcing_beats_co2_only_raw_reference": self.total_forcing_beats_co2_only_raw_reference,
            "fit_co2_only_erf_rereferenced": self.fit_co2_only_erf_rereferenced.to_dict(),
            "fit_total_forcing_rereferenced": self.fit_total_forcing_rereferenced.to_dict(),
            "fit_co2_only_myhre_rereferenced": self.fit_co2_only_myhre_rereferenced.to_dict(),
            "total_forcing_beats_co2_only_rereferenced": self.total_forcing_beats_co2_only_rereferenced,
        }


def run_co2_vs_full_forcing_comparison(erf_path: str | Path, co2_path: str | Path, temp_path: str | Path) -> ForcingComparisonReport:
    """Refits the SAME (unchanged) energy balance model with 3 different real
    forcing inputs over their common overlap window: (a) this module's ERF
    "CO2" column, (b) this module's ERF "total" (all forcings) column, and
    (c) dynamics.energy_balance's own Myhre-formula CO2-only forcing (from
    Mauna Loa concentrations) -- (a) and (c) are cross-checked for rough
    agreement (both are independently-sourced CO2-only estimates) before
    comparing (a)/(b)'s RMSE.

    Reports BOTH a "raw_reference" comparison (each series' own native
    baseline: ERF columns relative to 1750, Myhre relative to 1959) AND a
    "rereferenced" comparison (all three series shifted so F=0 in the
    first overlap year, matching the Myhre convention already used
    elsewhere in this repo) side by side.

    Fixed 2026-09-23 in response to
    prompts/Answers/nicht_stationäre_Treiber/SCF_Review_3e8dce3.md
    (Astra, finding 5): the original version aligned reference levels ONLY
    for the co2_forcing_cross_check_max_abs_diff sanity check above, but
    fed the UN-aligned (raw-baseline) series into the actual fits used for
    the total_forcing_beats_co2_only headline comparison. Astra's
    sensitivity check (unchanged fit function, only re-referencing each
    series to its own 1959 value) showed the original ranking can already
    REVERSE under a reasonable alternative reference convention -- so the
    original single "total forcing beats CO2-only" claim was not robust to
    a choice this module never made explicit or consistent.

    This is NOT a full physically-consistent re-initialization (Astra
    notes the model's transformation T'=T-delta strictly requires
    F'=F-alpha*delta, not just F zeroed at t=0; a fully principled fix
    would model an explicit forcing/observation offset or a physically
    motivated deep-ocean initial condition instead) -- both variants are
    reported so neither is silently treated as the sole correct answer,
    and the reference-dependence itself is now a visible, checked number
    (see verify_energy_balance_full_forcing.py) rather than a hidden
    assumption.
    """
    from scoped_correspondence.dynamics.energy_balance import _load_overlap_series

    erf = load_erf_series(erf_path)
    years_myhre, Tobs_myhre, F_myhre = _load_overlap_series(co2_path, temp_path)

    years = sorted(set(years_myhre) & set(erf))
    if len(years) < 10:
        raise ScopeViolationError(f"run_co2_vs_full_forcing_comparison: only {len(years)} overlapping years, need >= 10")
    if any(b - a != 1 for a, b in zip(years, years[1:])):
        raise ScopeViolationError("run_co2_vs_full_forcing_comparison: overlapping years must be consecutive calendar years")

    myhre_by_year = dict(zip(years_myhre, F_myhre))
    tobs_by_year = dict(zip(years_myhre, Tobs_myhre))

    Tobs = np.array([tobs_by_year[y] for y in years])
    F_co2_erf = np.array([erf[y]["CO2"] for y in years])
    F_total = np.array([erf[y]["total"] for y in years])
    F_co2_myhre = np.array([myhre_by_year[y] for y in years])

    # ERF's CO2 column is relative to its own 1750 baseline; the Myhre formula
    # here is relative to the first overlap year (1959). Compare their SHAPE
    # (both re-referenced to year[0]) rather than their absolute level, since
    # the two use different (but each internally consistent) baselines.
    co2_erf_rel = F_co2_erf - F_co2_erf[0]
    co2_myhre_rel = F_co2_myhre - F_co2_myhre[0]
    cross_check_diff = float(np.max(np.abs(co2_erf_rel - co2_myhre_rel)))

    fit_co2_erf = fit_energy_balance_model_from_series(years, Tobs, F_co2_erf)
    fit_total = fit_energy_balance_model_from_series(years, Tobs, F_total)
    fit_co2_myhre = fit_energy_balance_model_from_series(years, Tobs, F_co2_myhre)

    # Consistent-baseline variant: every series shifted to F=0 in the first
    # overlap year (years[0]), so the three fits differ ONLY in forcing
    # composition/shape, not in an arbitrary absolute-level choice.
    F_co2_erf_ref = F_co2_erf - F_co2_erf[0]
    F_total_ref = F_total - F_total[0]
    F_co2_myhre_ref = F_co2_myhre - F_co2_myhre[0]
    fit_co2_erf_ref = fit_energy_balance_model_from_series(years, Tobs, F_co2_erf_ref)
    fit_total_ref = fit_energy_balance_model_from_series(years, Tobs, F_total_ref)
    fit_co2_myhre_ref = fit_energy_balance_model_from_series(years, Tobs, F_co2_myhre_ref)

    return ForcingComparisonReport(
        years=tuple(years),
        co2_forcing_cross_check_max_abs_diff=cross_check_diff,
        fit_co2_only_erf=fit_co2_erf,
        fit_total_forcing=fit_total,
        fit_co2_only_myhre=fit_co2_myhre,
        total_forcing_beats_co2_only_raw_reference=bool(fit_total.rmse < fit_co2_erf.rmse),
        fit_co2_only_erf_rereferenced=fit_co2_erf_ref,
        fit_total_forcing_rereferenced=fit_total_ref,
        fit_co2_only_myhre_rereferenced=fit_co2_myhre_ref,
        total_forcing_beats_co2_only_rereferenced=bool(fit_total_ref.rmse < fit_co2_erf_ref.rmse),
    )


__all__ = [
    "SOURCE",
    "DATA_PROVENANCE_NOTE",
    "ForcingComparisonReport",
    "load_erf_series",
    "run_co2_vs_full_forcing_comparison",
]
