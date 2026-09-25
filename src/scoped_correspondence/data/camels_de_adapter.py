"""Selective CAMELS-DE catchment selection and extraction (DOMAIN_EXPANSION_ROADMAP.md Paket B3b).

Response to prompts/Answers/nicht_stationäre_Treiber/SCF_Review_fcc9a43.md,
finding R7: the archive (Loritz et al. 2024, ESSD 16, 5625-5642, Zenodo DOI
10.5281/zenodo.13837553, license CC-BY-4.0) is a single ~2.18GB file, but
its host honors HTTP Range requests -- ``http_range_reader.HTTPRangeFile``
lets ``zipfile.ZipFile`` read the central directory and extract individual
members (attribute tables, or one catchment's timeseries CSV) without a
full download. A previous assessment that this pilot was blocked by the
archive's size was WRONG; corrected here.

Catchment SELECTION RULE (fixed BEFORE looking at any model's fit quality,
plan section 9.4): from the intersection of catchments present in all four
attribute tables (topographic, human-influence, climatic, hydrologic),

1. the observed flow record must cover at least 1991-01-01 through
   2020-12-31 (30 years, matching the plan's suggested split);
2. ``flow_perc_complete >= 95%`` over that record;
3. from the qualifying pool, split into UNREGULATED (``dams_num == 0``) and
   REGULATED (``dams_num > 0``) groups, each sorted by ``frac_snow``, and
   take the low/median/high-snow-fraction catchment from each group (3+3=6)
   -- deliberately spanning different retention/runoff characteristics
   (regulation, snow influence), not chosen by catchment area or by any
   model's later performance.

This selection is NOT claimed representative of Germany's 1582 CAMELS-DE
catchments -- it is a small, diverse technical pilot panel (plan section
9.4: "sechs Einzugsgebiete als überschaubares technisches Pilotpanel, nicht
als repräsentative Deutschlandstudie").
"""

from __future__ import annotations

import csv
import io
import zipfile
from dataclasses import dataclass
from typing import Any, Dict, List, Sequence, Tuple

import numpy as np

from scoped_correspondence.errors import ScopeViolationError
from scoped_correspondence.data.http_range_reader import HTTPRangeFile

SOURCE_URL = "https://zenodo.org/records/13837553/files/camels_de.zip"
CATALOG_URL = "https://zenodo.org/records/13837553"
LICENSE = "CC-BY-4.0"
DATA_PAPER = "Loritz et al. (2024), CAMELS-DE, Earth System Science Data 16, 5625-5642, DOI 10.5194/essd-16-5625-2024"

TOPOGRAPHIC_ATTRS_MEMBER = "CAMELS_DE_topographic_attributes.csv"
HUMANINFLUENCE_ATTRS_MEMBER = "CAMELS_DE_humaninfluence_attributes.csv"
CLIMATIC_ATTRS_MEMBER = "CAMELS_DE_climatic_attributes.csv"
HYDROLOGIC_ATTRS_MEMBER = "CAMELS_DE_hydrologic_attributes.csv"


def open_remote_archive(url: str = SOURCE_URL) -> zipfile.ZipFile:
    """Open the CAMELS-DE archive for selective member access via HTTP Range
    requests -- does NOT download the full ~2.18GB archive."""
    return zipfile.ZipFile(HTTPRangeFile(url))


def _read_csv_member(zf: zipfile.ZipFile, member: str) -> List[Dict[str, str]]:
    data = zf.read(member).decode("utf-8")
    return list(csv.DictReader(io.StringIO(data)))


def _to_float(value: str) -> float:
    return float("nan") if value in ("", "NA") else float(value)


@dataclass(frozen=True)
class CatchmentAttributes:
    gauge_id: str
    area_km2: float
    dams_num: float
    frac_snow: float
    flow_perc_complete: float
    flow_period_start: str
    flow_period_end: str


def select_pilot_catchments(
    zf: zipfile.ZipFile, min_completeness: float = 95.0,
    required_start: str = "1991-01-01", required_end: str = "2020-12-31",
) -> List[CatchmentAttributes]:
    """Apply the selection rule documented in the module docstring; returns
    exactly 6 catchments (3 unregulated + 3 regulated, low/median/high snow
    fraction within each group)."""
    topo = {r["gauge_id"]: r for r in _read_csv_member(zf, TOPOGRAPHIC_ATTRS_MEMBER)}
    human = {r["gauge_id"]: r for r in _read_csv_member(zf, HUMANINFLUENCE_ATTRS_MEMBER)}
    climatic = {r["gauge_id"]: r for r in _read_csv_member(zf, CLIMATIC_ATTRS_MEMBER)}
    hydro = {r["gauge_id"]: r for r in _read_csv_member(zf, HYDROLOGIC_ATTRS_MEMBER)}

    ids = sorted(set(topo) & set(human) & set(climatic) & set(hydro))
    rows: List[CatchmentAttributes] = []
    for gid in ids:
        t, hm, c, hy = topo[gid], human[gid], climatic[gid], hydro[gid]
        try:
            area = _to_float(t["area"])
            dams_num = _to_float(hm["dams_num"])
            frac_snow = _to_float(c["frac_snow"])
            completeness = _to_float(hy["flow_perc_complete"])
            start, end = hy["flow_period_start"], hy["flow_period_end"]
        except (KeyError, ValueError):
            continue
        if not (np.isfinite(area) and np.isfinite(frac_snow) and np.isfinite(completeness)) or not start or not end:
            continue
        dams_num = 0.0 if not np.isfinite(dams_num) else dams_num
        rows.append(CatchmentAttributes(gid, area, dams_num, frac_snow, completeness, start, end))

    candidates = [
        r for r in rows
        if r.flow_period_start <= required_start and r.flow_period_end >= required_end
        and r.flow_perc_complete >= min_completeness
    ]
    if len(candidates) < 6:
        raise ScopeViolationError(f"fewer than 6 candidates satisfy the selection rule; got {len(candidates)}")

    unregulated = sorted([r for r in candidates if r.dams_num == 0.0], key=lambda r: r.frac_snow)
    regulated = sorted([r for r in candidates if r.dams_num > 0.0], key=lambda r: r.frac_snow)
    if len(unregulated) < 3 or len(regulated) < 3:
        raise ScopeViolationError(
            f"need >=3 unregulated and >=3 regulated candidates; got {len(unregulated)} and {len(regulated)}"
        )

    def low_mid_high(seq: List[CatchmentAttributes]) -> List[CatchmentAttributes]:
        n = len(seq)
        return [seq[0], seq[n // 2], seq[-1]]

    return low_mid_high(unregulated) + low_mid_high(regulated)


def extract_catchment_timeseries(zf: zipfile.ZipFile, gauge_id: str) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Extract ``(dates, precipitation_mean, discharge_vol_obs)`` for one gauge_id
    from ``timeseries/CAMELS_DE_hydromet_timeseries_<gauge_id>.csv``. CRC-checked
    internally by ``zipfile`` (raises ``BadZipFile`` on mismatch)."""
    member = f"timeseries/CAMELS_DE_hydromet_timeseries_{gauge_id}.csv"
    rows = _read_csv_member(zf, member)
    if len(rows) == 0:
        raise ScopeViolationError(f"no rows found for {gauge_id} in {member}")
    dates = np.array([r["date"] for r in rows])
    precip = np.array([_to_float(r["precipitation_mean"]) for r in rows])
    discharge_vol = np.array([_to_float(r["discharge_vol_obs"]) for r in rows])
    return dates, precip, discharge_vol


__all__ = [
    "SOURCE_URL", "CATALOG_URL", "LICENSE", "DATA_PAPER",
    "open_remote_archive", "CatchmentAttributes", "select_pilot_catchments", "extract_catchment_timeseries",
]
