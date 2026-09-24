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
(``"charge"``, ``"discharge"``, or ``"impedance"``) and, for discharge
cycles, a ``"data"`` dict containing a ``"Capacity"`` field (measured
discharge capacity in Ah for that cycle) -- confirmed against NASA's own
README.txt shipped inside the dataset archive.
"""

from __future__ import annotations

from typing import Any, Dict, List

from scoped_correspondence.errors import ScopeViolationError

SOURCE_URL = "https://phm-datasets.s3.amazonaws.com/NASA/5.+Battery+Data+Set.zip"
CATALOG_URL = "https://data.nasa.gov/dataset/li-ion-battery-aging-datasets"
LICENSE_STATUS = (
    "unspecified (NASA's own CKAN catalog API, "
    "https://data.nasa.gov/api/3/action/package_show?id=li-ion-battery-aging-datasets, "
    "reports license_title='License not specified' as of 2026-09-24)"
)


def extract_discharge_capacities(battery_struct: Dict[str, Any]) -> List[float]:
    """Extract the per-discharge-cycle ``Capacity`` (Ah) series, IN ORDER, from a
    parsed battery struct (``scipy.io.loadmat(path, simplify_cells=True)[cell_name]``).
    Charge and impedance cycles are skipped; only ``type == "discharge"`` cycles
    carry a directly measured discharge capacity.
    """
    if "cycle" not in battery_struct:
        raise ScopeViolationError("battery_struct must have a 'cycle' key")
    cycles = battery_struct["cycle"]
    capacities: List[float] = []
    for entry in cycles:
        if entry.get("type") != "discharge":
            continue
        data = entry.get("data", {})
        if "Capacity" not in data:
            raise ScopeViolationError("a discharge cycle is missing its 'Capacity' field")
        capacities.append(float(data["Capacity"]))
    if len(capacities) == 0:
        raise ScopeViolationError("no discharge cycles found in battery_struct")
    return capacities


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


__all__ = ["SOURCE_URL", "CATALOG_URL", "LICENSE_STATUS", "extract_discharge_capacities", "synthetic_fixture"]
