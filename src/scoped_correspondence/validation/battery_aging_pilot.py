"""Battery aging pilot: per-cell held-out capacity error, EOL crossing, censoring (DOMAIN_EXPANSION_ROADMAP.md Paket B5b).

Dataset-agnostic: operates on already-extracted per-cell discharge capacity
series (see ``data/nasa_battery_adapter.py`` for the NASA PCoE parser).
Fits each of the three ``capacity_degradation`` mean models on a
cell's OWN training PREFIX, evaluates mean-absolute error on that SAME
cell's held-out suffix (temporal split, never a random row shuffle), and
reports the mean model's own EOL-crossing point separately from the
observed series' actual first crossing -- including CENSORING when the
observed series never crosses within the recorded window (plan section
11.3: "RUL > verbleibender Beobachtungszeitraum ist dann die verfügbare
Information").
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Sequence

import numpy as np

from scoped_correspondence.errors import ScopeViolationError
from scoped_correspondence.dynamics.capacity_degradation import (
    fit_capacity_trend, mean_capacity, first_mean_eol_crossing,
    MODEL_PERSISTENCE, MODEL_LINEAR, MODEL_POWER,
)

_MODELS = (MODEL_PERSISTENCE, MODEL_LINEAR, MODEL_POWER)


@dataclass(frozen=True)
class CellPilotResult:
    cell_id: str
    n_cycles: int
    n_train: int
    n_test: int
    model_results: Dict[str, Dict[str, Any]]
    observed_first_eol_cycle: Optional[int]
    censored: bool

    def to_dict(self) -> Dict[str, Any]:
        return {
            "cell_id": self.cell_id, "n_cycles": self.n_cycles, "n_train": self.n_train, "n_test": self.n_test,
            "model_results": self.model_results,
            "observed_first_eol_cycle": self.observed_first_eol_cycle, "censored": self.censored,
        }


def run_cell_pilot(cell_id: str, capacities: Sequence[float], c_eol: float, train_fraction: float = 0.6) -> CellPilotResult:
    """Temporal (never random) prefix/holdout split on ONE cell's own capacity
    series: fit each mean model on the training prefix only, evaluate MAE on the
    later held-out cycles of the SAME cell."""
    caps = np.asarray(capacities, dtype=float)
    n = len(caps)
    if n < 6:
        raise ScopeViolationError(f"need at least 6 capacity observations; got {n}")
    if not (0.0 < train_fraction < 1.0):
        raise ScopeViolationError(f"train_fraction must be in (0,1); got {train_fraction!r}")
    n_train = int(round(n * train_fraction))
    if n_train < 3 or n_train >= n - 1:
        raise ScopeViolationError(f"train_fraction={train_fraction} gives an unusable split for n={n}")

    train_cycles = np.arange(n_train, dtype=float)
    test_cycles = np.arange(n_train, n, dtype=float)
    train_caps, test_caps = caps[:n_train], caps[n_train:]

    model_results: Dict[str, Dict[str, Any]] = {}
    for model in _MODELS:
        fit = fit_capacity_trend(train_cycles, train_caps, model)
        pred = mean_capacity(model, fit.params, test_cycles)
        mae = float(np.mean(np.abs(pred - test_caps)))
        eol_mean = first_mean_eol_crossing(fit, c_eol, float(n * 2))
        model_results[model] = {"params": fit.params, "mae_holdout": mae, "mean_eol_crossing_cycle": eol_mean}

    observed_below = np.where(caps <= c_eol)[0]
    observed_first = int(observed_below[0]) if len(observed_below) > 0 else None

    return CellPilotResult(
        cell_id=cell_id, n_cycles=n, n_train=n_train, n_test=n - n_train,
        model_results=model_results, observed_first_eol_cycle=observed_first,
        censored=observed_first is None,
    )


def run_leave_one_cell_out_panel(
    cell_capacities: Dict[str, Sequence[float]], c_eol: float, train_fraction: float = 0.6
) -> Dict[str, CellPilotResult]:
    """Run :func:`run_cell_pilot` independently for every cell -- each cell's fit
    uses ONLY its own observed prefix; no information crosses between cells (a
    genuine leave-one-cell-out evaluation requires this for any claim of transfer,
    even though the per-cell fitting itself here is personalized, not zero-shot).
    """
    if len(cell_capacities) == 0:
        raise ScopeViolationError("need at least one cell")
    return {cid: run_cell_pilot(cid, caps, c_eol, train_fraction) for cid, caps in cell_capacities.items()}


__all__ = ["CellPilotResult", "run_cell_pilot", "run_leave_one_cell_out_panel"]
