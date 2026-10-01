"""Real-data pilot for the paired forecast comparison (Paket J1).

SCOPE_COMPOSITION_EVIDENCE_ROADMAP.md package J1, plan section 7 ("Kontrollen
und Pilot"). Connects ``validation/forecast_comparison.py`` to an EXISTING,
provenance-checked real series: the NOAA global annual land+ocean anomaly
1880-2025 (``data/noaa_global_temp_anomaly_1880_2025.csv``, see
``data/real_data_manifest.json``), using predictors that already exist in
``validation/noaa_temp_pilot.py``.

Pre-declared design (fixed in code BEFORE any result was looked at; see
``docs/forecast_comparison.md`` section 4):

- Model A: last-30-years linear trend, refit at every origin
  (``noaa_temp_pilot._last_30_years_linear_predictor``).
- Model B: persistence (``noaa_temp_pilot._persistence_predictor``).
- Origins: every year 1960..(2025 - h); horizons h = 1 and h = 5, each its
  own comparison (overlapping 5-year windows are never pooled with h=1).
- Loss: squared error.
- HAC lag: max(h - 1, floor(4 (n/100)^(2/9))) -- the h-1 term covers the
  MA(h-1) overlap of optimal h-step errors, the Newey-West rule-of-thumb term
  some additional serial dependence. This is a documented convention, NOT
  a claim that it suffices for every dependence structure.
- PRIMARY result: descriptive only. The record is a single, trending
  realisation of the climate system; stationarity of the loss differences
  over 1960-2025 is not established, so no inference is released.
- SECONDARY result (explicitly labelled conditional): the same comparison
  with stationarity DECLARED as an assumption, to show what DM would say
  IF that assumption held. It is reported next to, never instead of, the
  primary result.

There is no obligation to find a significant difference (plan section 7).
"""
from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Tuple

import numpy as np

from scoped_correspondence.errors import ScopeViolationError
from scoped_correspondence.validation.forecast_comparison import (
    InferenceApplicability,
    PairedComparisonResult,
    PairingReport,
    compare_paired_forecasts,
    pair_raw_predictions,
)
from scoped_correspondence.validation.noaa_temp_pilot import (
    _last_30_years_linear_predictor,
    _persistence_predictor,
    load_annual_anomalies,
)
from scoped_correspondence.validation.rolling_origin import raw_predictions_by_horizon_step

DATA_ID = "noaa_global_temp_anomaly_1880_2025"
FIRST_ORIGIN = 1960
HORIZONS: Tuple[int, ...] = (1, 5)
LOSS = "squared_error"
MODEL_A = "last_30_years_linear"
MODEL_B = "persistence"

PRIMARY_APPLICABILITY = InferenceApplicability(
    declared_justified=False,
    justification="",
    min_series_length=30,
)
CONDITIONAL_APPLICABILITY = InferenceApplicability(
    declared_justified=True,
    justification=(
        "CONDITIONAL SENSITIVITY ONLY: approximate stationarity and weak dependence of the "
        "loss differences over the evaluated origins are ASSUMED, not tested."
    ),
    min_series_length=30,
)


def newey_west_rule_lag(n: int) -> int:
    return int(math.floor(4.0 * (n / 100.0) ** (2.0 / 9.0)))


def declared_lag(horizon: int, n: int) -> int:
    return max(horizon - 1, newey_west_rule_lag(n))


def verify_against_manifest(repo_root: Path) -> Dict[str, str]:
    manifest = json.loads((repo_root / "data" / "real_data_manifest.json").read_text(encoding="utf-8"))
    entry = next((d for d in manifest["datasets"] if d["id"] == DATA_ID), None)
    if entry is None:
        raise ScopeViolationError(f"{DATA_ID} not in real_data_manifest.json")
    path = repo_root / entry["file"]
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != entry["sha256"]:
        raise ScopeViolationError(f"sha256 mismatch for {path}: {digest} != {entry['sha256']}")
    return {"file": entry["file"], "sha256": digest, "license": entry["license"]}


@dataclass(frozen=True)
class NoaaPairedComparisonPilot:
    provenance: Dict[str, str]
    pairing: Tuple[PairingReport, ...]
    primary: Tuple[PairedComparisonResult, ...]
    conditional: Tuple[PairedComparisonResult, ...]


def run_noaa_paired_comparison(repo_root: Path) -> NoaaPairedComparisonPilot:
    provenance = verify_against_manifest(repo_root)
    points = load_annual_anomalies(repo_root / provenance["file"])
    years = np.array([p.year for p in points], dtype=float)
    temps = np.array([p.anomaly_c for p in points], dtype=float)
    last_year = int(years[-1])
    pairings = []
    primary = []
    conditional = []
    for h in HORIZONS:
        origins = [float(o) for o in range(FIRST_ORIGIN, last_year - h + 1)]
        raw = raw_predictions_by_horizon_step(
            years, temps, origins=origins, max_horizon_steps=h, step_size=1.0,
            predictors={MODEL_A: _last_30_years_linear_predictor, MODEL_B: _persistence_predictor},
        )
        only_h = {k: [r for r in v if r.step == h] for k, v in raw.items()}
        rep = pair_raw_predictions(
            only_h[MODEL_A], only_h[MODEL_B], series_id="noaa_global_annual", model_a_id=MODEL_A,
            model_b_id=MODEL_B, data_id=DATA_ID, split_id=f"annual_origins_{FIRST_ORIGIN}_{last_year - h}_h{h}",
            step_size=1.0,
        )
        pairings.append(rep)
        lag = declared_lag(h, rep.n_paired)
        just = f"max(h-1={h - 1}, Newey-West rule floor(4(n/100)^(2/9))={newey_west_rule_lag(rep.n_paired)}) for n={rep.n_paired}"
        primary += compare_paired_forecasts(rep.records, loss=LOSS, hac_lag=lag, lag_justification=just, applicability=PRIMARY_APPLICABILITY)
        conditional += compare_paired_forecasts(rep.records, loss=LOSS, hac_lag=lag, lag_justification=just, applicability=CONDITIONAL_APPLICABILITY)
    return NoaaPairedComparisonPilot(provenance, tuple(pairings), tuple(primary), tuple(conditional))


__all__ = [
    "DATA_ID",
    "FIRST_ORIGIN",
    "HORIZONS",
    "LOSS",
    "MODEL_A",
    "MODEL_B",
    "PRIMARY_APPLICABILITY",
    "CONDITIONAL_APPLICABILITY",
    "newey_west_rule_lag",
    "declared_lag",
    "verify_against_manifest",
    "NoaaPairedComparisonPilot",
    "run_noaa_paired_comparison",
]
