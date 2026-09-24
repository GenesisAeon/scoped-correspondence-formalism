"""Parser for the NASA PCoE Li-ion battery aging dataset's .mat structure (DOMAIN_EXPANSION_ROADMAP.md Paket B5b).

Response to prompts/Answers/nicht_stationäre_Treiber/
SCF_DOMAIN_EXPANSION_IMPLEMENTATION_PLAN.md, section 11.1: NASA's own data
catalog (queried via the CKAN API, ``https://data.nasa.gov/api/3/action/
package_show?id=li-ion-battery-aging-datasets``) reports
``license_title: "License not specified"`` -- Astra's flagged concern,
independently confirmed. **Per plan section 5.1's explicit guidance for
exactly this situation ("Ohne geklärte Weiterverteilung: lokaler
Downloader plus synthetische Parser-Fixture"), this module parses the
dataset's structure but the raw/derived per-cycle capacity data are NOT
committed to this repository.** A real pilot run (four cells, B0005/6/7/18
from ``1. BatteryAgingARC-FY08Q4.zip``) was performed locally against the
actual downloaded data during development -- see docs/battery_aging_pilot.md
for the resulting numbers, reported as a one-time manual reproduction, not
as part of the automated CI (which runs only against the synthetic fixture
below, requiring no network access or redistributed data).

This parser expects the structure produced by
``scipy.io.loadmat(path, simplify_cells=True)[cell_name]`` -- a dict with a
``"cycle"`` key holding a list of per-cycle dicts, each with a ``"type"``
(``"charge"``, ``"discharge"``, or ``"impedance"``), an ``"ambient_
temperature"``, a ``"time"`` (start-of-cycle MATLAB date vector) and, for
discharge cycles, a ``"data"`` dict containing a ``"Capacity"`` field
(measured discharge capacity in Ah for that cycle) -- confirmed against
NASA's own README.txt shipped inside the dataset archive.

**Correction (2026-09-24, response to
prompts/Answers/nicht_stationäre_Treiber/SCF_Review_fcc9a43.md, finding R6
-- a real scope gap, not a numerical bug): the parser previously discarded
every field except capacity and cycle order.** Without the ORIGINAL
discharge position (within the full charge/discharge/impedance sequence),
ambient temperature, or timestamp, a later analysis cannot distinguish a
genuine protocol change (temperature shift, discharge cutoff-voltage
change) from ordinary aging, nor locate a missing/skipped cycle. Fixed by
``extract_discharge_records``, which retains this metadata per discharge
cycle; ``extract_discharge_capacities`` is now a thin wrapper over it
(same validation behavior, unchanged return type, for existing callers).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from scoped_correspondence.errors import ScopeViolationError

SOURCE_URL = "https://phm-datasets.s3.amazonaws.com/NASA/5.+Battery+Data+Set.zip"
CATALOG_URL = "https://data.nasa.gov/dataset/li-ion-battery-aging-datasets"
LICENSE_STATUS = (
    "unspecified (NASA's own CKAN catalog API, "
    "https://data.nasa.gov/api/3/action/package_show?id=li-ion-battery-aging-datasets, "
    "reports license_title='License not specified' as of 2026-09-24)"
)


@dataclass(frozen=True)
class DischargeRecord:
    discharge_index: int  # 0-based index among DISCHARGE cycles only (matches the old capacities list order)
    cycle_index: int  # 0-based index in the FULL charge/discharge/impedance sequence
    capacity: float
    ambient_temperature: Optional[float]
    time: Optional[Any]  # raw MATLAB date-vector as returned by scipy.io.loadmat, unmodified

    def to_dict(self) -> Dict[str, Any]:
        return {
            "discharge_index": self.discharge_index, "cycle_index": self.cycle_index,
            "capacity": self.capacity, "ambient_temperature": self.ambient_temperature,
            "time": list(self.time) if self.time is not None else None,
        }


def extract_discharge_records(battery_struct: Dict[str, Any]) -> List[DischargeRecord]:
    """Extract per-discharge-cycle records, IN ORDER, retaining the metadata needed
    to later distinguish a genuine protocol change (temperature, cutoff voltage)
    from ordinary aging, or to locate a missing/skipped cycle -- not just the bare
    capacity value and its position among discharge cycles alone.
    """
    if "cycle" not in battery_struct:
        raise ScopeViolationError("battery_struct must have a 'cycle' key")
    cycles = battery_struct["cycle"]
    records: List[DischargeRecord] = []
    for cycle_index, entry in enumerate(cycles):
        if entry.get("type") != "discharge":
            continue
        data = entry.get("data", {})
        if "Capacity" not in data:
            raise ScopeViolationError("a discharge cycle is missing its 'Capacity' field")
        records.append(DischargeRecord(
            discharge_index=len(records), cycle_index=cycle_index, capacity=float(data["Capacity"]),
            ambient_temperature=entry.get("ambient_temperature"), time=entry.get("time"),
        ))
    if len(records) == 0:
        raise ScopeViolationError("no discharge cycles found in battery_struct")
    return records


def extract_discharge_capacities(battery_struct: Dict[str, Any]) -> List[float]:
    """Extract the per-discharge-cycle ``Capacity`` (Ah) series, IN ORDER -- a thin
    wrapper over :func:`extract_discharge_records` for callers that only need the
    bare capacity series (same validation behavior, unchanged return type).
    """
    return [r.capacity for r in extract_discharge_records(battery_struct)]


def synthetic_fixture() -> Dict[str, Any]:
    """A minimal fixture matching the REAL dataset's structure exactly (verified
    against the actual NASA .mat files during development), for testing the
    parser without any network access or redistributed data. Deliberately
    includes charge and impedance entries interleaved with discharge entries,
    matching the real interleaving pattern, so the type-filtering logic is
    exercised the same way it would be on real data.
    """
    return {
        "cycle": [
            {"type": "charge", "ambient_temperature": 24, "data": {"Voltage_measured": [4.2]}},
            {"type": "discharge", "ambient_temperature": 24, "data": {"Capacity": 1.856}},
            {"type": "impedance", "ambient_temperature": 24, "data": {}},
            {"type": "charge", "ambient_temperature": 24, "data": {"Voltage_measured": [4.2]}},
            {"type": "discharge", "ambient_temperature": 24, "data": {"Capacity": 1.846}},
            {"type": "impedance", "ambient_temperature": 24, "data": {}},
            {"type": "charge", "ambient_temperature": 24, "data": {"Voltage_measured": [4.2]}},
            {"type": "discharge", "ambient_temperature": 24, "data": {"Capacity": 1.835}},
        ],
    }


__all__ = [
    "SOURCE_URL", "CATALOG_URL", "LICENSE_STATUS",
    "DischargeRecord", "extract_discharge_records", "extract_discharge_capacities", "synthetic_fixture",
]
