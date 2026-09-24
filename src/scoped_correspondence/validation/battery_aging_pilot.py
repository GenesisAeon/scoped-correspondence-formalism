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

**Correction (2026-09-24, response to
prompts/Answers/nicht_stationäre_Treiber/SCF_Review_fcc9a43.md, finding R6
-- naming/scope, not a numerical bug):** the panel runner was previously
named ``run_leave_one_cell_out_panel``, which reads as a cross-cell
TRANSFER experiment (train on other cells, evaluate on a held-out one).
What it actually does is fit each cell's own model on that SAME cell's
temporal prefix and evaluate on that same cell's later cycles -- a
PERSONALIZED per-cell retrospective holdout, not a transfer claim. Renamed
to ``run_personalized_cell_panel`` to match what it does; a genuine
cross-cell transfer experiment (train hyperparameters on other cells only)
is not attempted here, and none of the three model families in
``capacity_degradation`` currently has a cross-cell hyperparameter to
select in the first place. Also added: an optional FIXED absolute
``n_train`` (plan section 11.4 point: "Feste Zyklusursprünge... statt
ausschließlich einer vom späteren Reihenende abhängigen 60-%-Position"),
and an explicit count of model-domain-violating (negative) extrapolated
predictions in each model's result, rather than silently including them
in the MAE average with no visible flag.
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
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "cell_id": self.cell_id, "n_cycles": self.n_cycles, "n_train": self.n_train, "n_test": self.n_test,
            "model_results": self.model_results,
            "observed_first_eol_cycle": self.observed_first_eol_cycle, "censored": self.censored,
            "metadata": self.metadata,
        }


def run_cell_pilot(
    cell_id: str, capacities: Sequence[float], c_eol: float, train_fraction: float = 0.6,
    n_train: Optional[int] = None, metadata: Optional[Dict[str, Any]] = None,
) -> CellPilotResult:
    """Temporal (never random) prefix/holdout split on ONE cell's own capacity
    series: fit each mean model on the training prefix only, evaluate MAE on the
    later held-out cycles of the SAME cell.

    ``n_train``, if given, is a FIXED absolute cycle count for the training
    prefix (e.g. 20, 40, 60 -- a deployment-realistic "prognosis origin" fixed
    in advance), taking precedence over ``train_fraction`` (a retrospective
    fraction-of-the-full-series holdout, which is legitimate but is NOT the
    same claim as evaluating from a pre-declared origin).
    """
    caps = np.asarray(capacities, dtype=float)
    n = len(caps)
    if n < 6:
        raise ScopeViolationError(f"need at least 6 capacity observations; got {n}")
    if n_train is not None:
        n_train_final = int(n_train)
    else:
        if not (0.0 < train_fraction < 1.0):
            raise ScopeViolationError(f"train_fraction must be in (0,1); got {train_fraction!r}")
        n_train_final = int(round(n * train_fraction))
    if n_train_final < 3 or n_train_final >= n - 1:
        raise ScopeViolationError(f"resulting n_train={n_train_final} gives an unusable split for n={n}")

    train_cycles = np.arange(n_train_final, dtype=float)
    test_cycles = np.arange(n_train_final, n, dtype=float)
    train_caps, test_caps = caps[:n_train_final], caps[n_train_final:]

    model_results: Dict[str, Dict[str, Any]] = {}
    for model in _MODELS:
        fit = fit_capacity_trend(train_cycles, train_caps, model)
        pred = mean_capacity(model, fit.params, test_cycles)
        n_negative = int(np.sum(pred < 0.0))
        mae = float(np.mean(np.abs(pred - test_caps)))
        eol_mean = first_mean_eol_crossing(fit, c_eol, float(n * 2))
        model_results[model] = {
            "params": fit.params, "mae_holdout": mae, "mean_eol_crossing_cycle": eol_mean,
            "n_negative_extrapolation_predictions": n_negative,
        }

    observed_below = np.where(caps <= c_eol)[0]
    observed_first = int(observed_below[0]) if len(observed_below) > 0 else None

    return CellPilotResult(
        cell_id=cell_id, n_cycles=n, n_train=n_train_final, n_test=n - n_train_final,
        model_results=model_results, observed_first_eol_cycle=observed_first,
        censored=observed_first is None, metadata=metadata,
    )


def run_personalized_cell_panel(
    cell_capacities: Dict[str, Sequence[float]], c_eol: float, train_fraction: float = 0.6,
    n_train: Optional[int] = None, cell_metadata: Optional[Dict[str, Dict[str, Any]]] = None,
) -> Dict[str, CellPilotResult]:
    """Run :func:`run_cell_pilot` independently for every cell -- each cell's fit
    uses ONLY its own observed prefix; no information crosses between cells.

    This is a PERSONALIZED per-cell panel (each cell's own temporal holdout),
    NOT a cross-cell transfer experiment (train on other cells, evaluate on a
    held-out one) -- see the module docstring's correction. ``cell_metadata``,
    if given, maps ``cell_id -> metadata dict`` (e.g. from
    ``data/nasa_battery_adapter.py``'s per-cycle metadata) and is attached to
    each cell's result unchanged.
    """
    if len(cell_capacities) == 0:
        raise ScopeViolationError("need at least one cell")
    cell_metadata = cell_metadata or {}
    return {
        cid: run_cell_pilot(cid, caps, c_eol, train_fraction, n_train=n_train, metadata=cell_metadata.get(cid))
        for cid, caps in cell_capacities.items()
    }


__all__ = ["CellPilotResult", "run_cell_pilot", "run_personalized_cell_panel"]
