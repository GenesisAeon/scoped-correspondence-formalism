"""Synthetic benchmark and evidence report (Paket ON6a, plan §8, §9, ON6a).

A small, PRE-DECLARED list of conditions (the configuration is written to
disk before any result is interpreted):

- frozen vs adapted weights (eta = 0 vs eta > 0),
- full vs aggregated (sum) observation,
- identical operator under different module names (M = 1 vs M = 3, c = 8/11),
- spatially shared vs separate inputs (both input states in one module vs in
  different modules), and
- a drift counterexample (frozen weights; the readout sites are remapped in a
  later epoch: an invertible change, so the information is unchanged, but the
  frozen decoder can degrade while the refitted one does not).

Unit of replication: one simulation RUN (its own topology/adaptation/decoder/
test seeds) -- never a trial. Per run the pre-declared contrast is
Delta = balanced_accuracy_after - balanced_accuracy_before (refitted decoder),
compared between conditions at run level. Simulation seeds are not
biological replicates.

The deterministic CI check asserts INVARIANTS (budgets, determinism,
identical-operator equality, record vocabulary, drift counterexample), never
an effect direction or a p < 0.05 gate; unclear or absent advantages stay in
the report. Scores, information and resources are never merged into an index.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from scoped_correspondence.epistemic.records import EMPIRICAL_STATUSES, EVIDENCE_KINDS
from scoped_correspondence.errors import ScopeViolationError
from scoped_correspondence.validation.modular_networks.adaptive_model import (
    adapt,
    budget_adjacency,
    edge_mask,
    input_matrix,
    module_partition,
    simulate_trial,
)
from scoped_correspondence.validation.modular_networks.decoders import (
    NearestMeanDecoder,
    balanced_accuracy,
    check_split,
    group_mean_and_sem2,
)

ALLOWED_COMBINATIONS = {
    ("exhaustive_finite", "synthetic_only"),
    ("analytic_argument", "not_tested"),
    ("numerical_sample", "synthetic_only"),
    ("empirical_evaluation", "evaluated_on_declared_data"),
    ("not_evaluated", "not_tested"),
}


@dataclass(frozen=True)
class OrganoidEvidenceRecord:
    claim: str
    evidence_kind: str
    empirical_status: str
    scope_id: str
    configuration_id: str
    dataset_hash: Optional[str]
    preparation_id: Optional[str]
    split_id: Optional[str]
    measurement_map: str
    decoder_mode: str
    stationarity_assumption: str
    memory_assumption: str
    prior: str
    sample_counts: Dict[str, int]
    excluded_units: Tuple[str, ...]
    uncertainty_method: str
    optimization_status: str
    limitations: Tuple[str, ...]
    search_complete: Optional[bool] = None
    all_candidates_scanned: Optional[bool] = None
    value: Optional[object] = None

    def __post_init__(self):
        if self.evidence_kind not in EVIDENCE_KINDS or self.empirical_status not in EMPIRICAL_STATUSES:
            raise ScopeViolationError("unknown evidence vocabulary")
        if (self.evidence_kind, self.empirical_status) not in ALLOWED_COMBINATIONS:
            raise ScopeViolationError(f"combination ({self.evidence_kind}, {self.empirical_status}) not allowed")
        if self.empirical_status == "evaluated_on_declared_data" and not self.dataset_hash:
            raise ScopeViolationError("real-data evidence needs a dataset hash")


@dataclass(frozen=True)
class Condition:
    name: str
    M: int
    c: Optional[float]
    inputs: Tuple[int, int]
    observation: str  # "full" | "sum"
    eta: float
    drift: str = "none"  # "none" | "sensor_reversal" (later epoch remaps the readout sites)


DEFAULT_OUTPUTS = (2, 3, 6, 7, 10, 11)


@dataclass(frozen=True)
class BenchmarkConfig:
    N: int = 12
    gamma: float = 0.8
    ell: float = 0.5
    steps: int = 12
    window: Tuple[int, ...] = tuple(range(6, 13))
    sigma: float = 0.15
    amplitude: float = 0.6
    n_adapt_trials: int = 40
    n_trials_per_stimulus: int = 50
    train_fraction: float = 0.8
    n_runs: int = 6
    base_seed: int = 20261001
    # "paired_v2" (Followup-Review §5.1, 2026-10-01): per later epoch ONE
    # dataset and ONE split; the refitted decoder is trained on its training
    # part and BOTH decoders are scored on the same test trials. The earlier
    # "independent_v1" protocol drew separate data/splits for the two decoders.
    protocol: str = "paired_v2"
    outputs: Tuple[int, ...] = DEFAULT_OUTPUTS
    conditions: Tuple[Condition, ...] = (
        Condition("M3_separate_full_frozen", 3, 0.25, (0, 4), "full", 0.0),
        Condition("M3_separate_full_adapted", 3, 0.25, (0, 4), "full", 0.3),
        Condition("M3_shared_full_adapted", 3, 0.25, (0, 1), "full", 0.3),
        Condition("M3_separate_sum_adapted", 3, 0.25, (0, 4), "sum", 0.3),
        Condition("M1_uniform_adapted", 1, None, (0, 4), "full", 0.3),
        Condition("M3_c8_11_adapted", 3, 8 / 11, (0, 4), "full", 0.3),
        Condition("M3_separate_full_drift_frozen_weights", 3, 0.25, (0, 4), "full", 0.0, drift="sensor_reversal"),
    )

    def to_json(self) -> Dict:
        d = asdict(self)
        d["conditions"] = [asdict(c) for c in self.conditions]
        return d

    @classmethod
    def from_json(cls, d: Dict) -> "BenchmarkConfig":
        d = dict(d)
        d["conditions"] = tuple(Condition(**{**c, "inputs": tuple(c["inputs"])}) for c in d["conditions"])
        for k in ("window", "outputs"):
            d[k] = tuple(d[k])
        return cls(**d)

    def configuration_id(self) -> str:
        return hashlib.sha256(json.dumps(self.to_json(), sort_keys=True).encode()).hexdigest()[:16]


def _seeds(cfg: BenchmarkConfig, run: int) -> Dict[str, int]:
    base = cfg.base_seed + 1000 * run
    return {"topology": base + 1, "adaptation": base + 2, "decoder": base + 3, "test": base + 4}


def _observe(traj: np.ndarray, cfg: BenchmarkConfig, cond: Condition, rng: np.random.Generator, drift: str) -> np.ndarray:
    outputs = list(cfg.outputs)
    if drift == "sensor_reversal":
        outputs = outputs[::-1]  # invertible remap: information unchanged
    elif drift != "none":
        raise ScopeViolationError(f"unknown drift {drift!r}")
    v = traj[list(cfg.window)].sum(axis=0)[outputs]
    v = v + rng.normal(scale=cfg.sigma, size=v.shape)
    return v if cond.observation == "full" else np.array([v.sum()])


def _dataset(A, B, cfg, cond, rng, drift):
    X, y = [], []
    stimuli = (np.array([1.0, 0.0]), np.array([0.0, 1.0]))
    for s in (0, 1):
        traj = simulate_trial(A, B, stimuli[s], cfg.ell, cfg.steps)  # deterministic dynamics, noisy observation
        for _ in range(cfg.n_trials_per_stimulus):
            X.append(_observe(traj, cfg, cond, rng, drift))
            y.append(s)
    return np.array(X), y


def _split(n: int, frac: float, rng: np.random.Generator):
    idx = rng.permutation(n)
    k = int(round(frac * n))
    return sorted(idx[:k].tolist()), sorted(idx[k:].tolist())


def run_condition(cfg: BenchmarkConfig, cond: Condition, run: int) -> Dict[str, object]:
    seeds = _seeds(cfg, run)
    A_list, mod = budget_adjacency(cfg.N, cond.M, cfg.gamma, cond.c)
    A0 = np.array(A_list, dtype=float)
    mask = edge_mask(cfg.N, mod)
    B = input_matrix(cfg.N, cond.inputs, cfg.amplitude)
    rng_dec, rng_test = np.random.default_rng(seeds["decoder"]), np.random.default_rng(seeds["test"])

    if cfg.protocol != "paired_v2":
        raise ScopeViolationError(f"unsupported evaluation protocol {cfg.protocol!r}")

    def epoch(A, drift, tag):
        """One dataset and one split per epoch; trial and split ids recorded."""
        X, y = _dataset(A, B, cfg, cond, rng_test, drift)
        tr, te = _split(len(y), cfg.train_fraction, rng_dec)
        ids_tr, ids_te = [f"{tag}:trial{i}" for i in tr], [f"{tag}:trial{i}" for i in te]
        check_split(ids_tr, ids_te)
        refit = NearestMeanDecoder().fit(X[tr], [y[i] for i in tr])
        return X, y, tr, te, refit, {"epoch": tag, "train_ids": ids_tr, "test_ids": ids_te}

    def score(dec, X, y, te):
        return balanced_accuracy([y[i] for i in te], dec.predict(X[te]))

    Xb, yb, _, teb, dec_before, split_before = epoch(A0, "none", "before")
    before = score(dec_before, Xb, yb, teb)
    if cond.eta > 0:
        A1, hist = adapt(A0, B, _cfg_shim(cfg, cond), (np.array([1.0, 0.0]), np.array([0.0, 1.0])),
                         np.random.default_rng(seeds["adaptation"]), cfg.n_adapt_trials, mask)
    else:
        A1, hist = A0.copy(), []
    Xa, ya, _, tea, dec_after, split_after = epoch(A1, cond.drift, "after")
    after_refit = score(dec_after, Xa, ya, tea)
    after_frozen = score(dec_before, Xa, ya, tea)  # SAME test trials as the refitted decoder
    if not np.allclose(A1.sum(axis=1), cfg.gamma):
        raise ScopeViolationError("budget violated")
    inter = [float(x) for x in hist[-1]] if hist else None
    return {"run": run, "seeds": seeds, "before": before, "after_refitted": after_refit, "after_frozen": after_frozen,
            "delta_refitted": after_refit - before, "frozen_minus_refitted_paired": after_frozen - after_refit,
            "split_ids": {"before": split_before, "after": split_after}, "A_after_hash": hashlib.sha256(np.round(A1, 12).tobytes()).hexdigest()[:16],
            "final_inter_fraction_mean": (float(np.mean(inter)) if inter else None)}


def _cfg_shim(cfg: BenchmarkConfig, cond: Condition):
    from scoped_correspondence.validation.modular_networks.adaptive_model import NetworkConfig
    return NetworkConfig(cfg.N, cond.M, cfg.gamma, cond.c, cfg.ell, cond.inputs, cfg.outputs, cfg.steps, cfg.window, cond.eta)


def run_benchmark(cfg: BenchmarkConfig, config_path: Path) -> Dict[str, object]:
    """Writes the configuration FIRST, then runs every condition for every
    run and summarises per condition at run level."""
    config_path = Path(config_path)
    if not config_path.exists():
        raise ScopeViolationError("configuration file must be saved before running (pre-declaration)")
    saved = BenchmarkConfig.from_json(json.loads(config_path.read_text(encoding="utf-8")))
    if saved.configuration_id() != cfg.configuration_id():
        raise ScopeViolationError("running configuration differs from the saved one")
    per_condition = {}
    for cond in cfg.conditions:
        runs = [run_condition(cfg, cond, r) for r in range(cfg.n_runs)]
        deltas = [r["delta_refitted"] for r in runs]
        m, sem2 = group_mean_and_sem2(deltas)
        per_condition[cond.name] = {"condition": asdict(cond), "runs": runs, "delta_mean": m, "delta_sem": float(np.sqrt(sem2)),
                                    "after_frozen_mean": float(np.mean([r["after_frozen"] for r in runs])),
                                    "after_refitted_mean": float(np.mean([r["after_refitted"] for r in runs]))}
    records = [
        OrganoidEvidenceRecord(
            claim=f"{name}: run-level contrast Delta (refitted balanced accuracy after - before)",
            evidence_kind="numerical_sample", empirical_status="synthetic_only", scope_id="organoid_synthetic_v1",
            configuration_id=cfg.configuration_id(), dataset_hash=None, preparation_id=None, split_id="random 80/20 per run",
            measurement_map=pc["condition"]["observation"], decoder_mode="refitted and frozen (both reported)",
            stationarity_assumption="fixed dynamics within an epoch", memory_assumption="state reset per trial",
            prior="balanced stimuli", sample_counts={"runs": cfg.n_runs, "trials_per_stimulus": cfg.n_trials_per_stimulus},
            excluded_units=(), uncertainty_method="SEM over runs (runs are the unit)", optimization_status="no tuning on test labels",
            limitations=("synthetic model, not a biological mechanism", "no three-module threshold implied",
                         "simulation seeds are not biological replicates"),
            value={"delta_mean": pc["delta_mean"], "delta_sem": pc["delta_sem"]})
        for name, pc in per_condition.items()
    ]
    return {"configuration_id": cfg.configuration_id(), "config": cfg.to_json(), "conditions": per_condition,
            "records": [asdict(r) for r in records],
            "not_evaluated": ["real organoid data (ON6b, data gates)", "information/PID of the simulated channel at scale"],
            "interpretation": "descriptive; no effect direction is required or asserted"}


__all__ = ["ALLOWED_COMBINATIONS", "OrganoidEvidenceRecord", "Condition", "BenchmarkConfig", "run_condition", "run_benchmark"]
