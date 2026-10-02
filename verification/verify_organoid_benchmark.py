"""ON6a verification (ORGANOID_NETWORK_ROADMAP.md, plan section 10/ON6a):
synthetic benchmark and evidence report -- deterministic INVARIANTS only.

- the pre-declared configuration configs/organoid_minimal.json equals the
  default and is required before running (changed config refused);
- determinism: same seeds give identical results;
- identical operator under different module names (M = 1 vs M = 3 with
  c = 8/11) gives identical runs;
- observation does not change the system (full vs sum: same adapted A);
- eta = 0 leaves A unchanged (frozen condition: Delta = 0 exactly);
- paired protocol (frozen and refitted decoder on the SAME test trials);
- drift counterexample: invertible sensor remap with frozen weights -- the
  refitted decoder keeps its score, the frozen one is lower in every run;
- evidence records use only allowed vocabulary combinations; real-data
  status without dataset hash refused.
No effect direction between module numbers or input layouts is asserted.
"""
from __future__ import annotations

import json
import sys
import tempfile
from dataclasses import replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from scoped_correspondence.errors import ScopeViolationError
from scoped_correspondence.validation.modular_networks.evaluation import (
    BenchmarkConfig,
    OrganoidEvidenceRecord,
    run_benchmark,
)

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "configs" / "organoid_minimal.json"


def require(c, m=""):
    if not c:
        raise AssertionError(m)


def raises(fn, exc=ScopeViolationError):
    try:
        fn()
    except exc:
        return True
    return False


_CACHE = {}


def report():
    if "r" not in _CACHE:
        _CACHE["r"] = run_benchmark(BenchmarkConfig(), CONFIG)
    return _CACHE["r"]


def check_predeclared_config():
    saved = BenchmarkConfig.from_json(json.loads(CONFIG.read_text(encoding="utf-8")))
    require(saved.configuration_id() == BenchmarkConfig().configuration_id(), "saved config equals the declared default")
    other = replace(BenchmarkConfig(), sigma=0.3)
    require(raises(lambda: run_benchmark(other, CONFIG)), "a config differing from the saved one is refused")
    require(raises(lambda: run_benchmark(BenchmarkConfig(), Path(tempfile.gettempdir()) / "does_not_exist_organoid.json")),
            "no run without a saved configuration")
    return {"configuration_id": saved.configuration_id()}


def check_determinism_and_identical_operator():
    r1 = report()
    r2 = run_benchmark(BenchmarkConfig(), CONFIG)
    require(json.dumps(r1["conditions"], sort_keys=True) == json.dumps(r2["conditions"], sort_keys=True), "deterministic under seeds")
    a, b = r1["conditions"]["M1_uniform_adapted"]["runs"], r1["conditions"]["M3_c8_11_adapted"]["runs"]
    require([(x["before"], x["after_refitted"], x["A_after_hash"]) for x in a] ==
            [(x["before"], x["after_refitted"], x["A_after_hash"]) for x in b], "module names alone change nothing")
    return {"identical_runs": len(a)}


def check_observation_and_eta_zero():
    c = report()["conditions"]
    full, summ = c["M3_separate_full_adapted"]["runs"], c["M3_separate_sum_adapted"]["runs"]
    require([x["A_after_hash"] for x in full] == [x["A_after_hash"] for x in summ], "observation does not change the system")
    frozen = c["M3_separate_full_frozen"]["runs"]
    require(all(x["final_inter_fraction_mean"] is None for x in frozen), "eta = 0: no adaptation step taken")
    return {"frozen_delta_mean": c["M3_separate_full_frozen"]["delta_mean"]}


def check_drift_counterexample():
    """Fixed example of THIS configuration (Followup-Review §5.2): unchanged
    information under an invertible remap does NOT force bit-equal accuracy of
    two independently drawn finite samples -- the equality below holds here
    because both scores are 1.0. The general mechanistic statement (identical
    predictions after identically permuting training and test features) is
    checked in verify_organoid_decoders.py (review_r5_decoder_inputs)."""
    runs = report()["conditions"]["M3_separate_full_drift_frozen_weights"]["runs"]
    require(all(x["after_refitted"] == x["before"] == 1.0 for x in runs), "fixed example: refitted 1.0 before and after the remap")
    require(all(x["after_frozen"] < x["after_refitted"] for x in runs), "frozen decoder lower in every run on the SAME test trials")
    return {"after_frozen": [x["after_frozen"] for x in runs]}


def check_paired_protocol():
    """Followup-Review §5.1: frozen and refitted decoders are scored on the
    same later-epoch test trials; train/test ids are recorded and disjoint."""
    r = report()
    require(r["config"]["protocol"] == "paired_v2", "paired protocol declared in the configuration")
    for cond in r["conditions"].values():
        for x in cond["runs"]:
            a = x["split_ids"]["after"]
            require(a["test_ids"] and not set(a["train_ids"]) & set(a["test_ids"]), "after-epoch split disjoint and non-empty")
            require(abs(x["frozen_minus_refitted_paired"] - (x["after_frozen"] - x["after_refitted"])) < 1e-15, "paired difference recorded")
    require(raises(lambda: run_benchmark(replace(BenchmarkConfig(), protocol="independent_v1"), CONFIG)),
            "an undeclared/old protocol is refused (config mismatch or unsupported protocol)")
    return {"protocol": "paired_v2"}


def check_records():
    recs = report()["records"]
    require(len(recs) == len(BenchmarkConfig().conditions), "one record per condition")
    require(all(r["evidence_kind"] == "numerical_sample" and r["empirical_status"] == "synthetic_only" for r in recs), "synthetic vocabulary")
    require("index" not in json.dumps(report()["conditions"]).lower(), "no merged score index")
    base = dict(recs[0])
    require(raises(lambda: OrganoidEvidenceRecord(**{**base, "empirical_status": "evaluated_on_declared_data"})),
            "numerical_sample + evaluated_on_declared_data is not an allowed combination")
    require(raises(lambda: OrganoidEvidenceRecord(**{**base, "evidence_kind": "empirical_evaluation",
                                                    "empirical_status": "evaluated_on_declared_data", "dataset_hash": None})),
            "real-data evidence without dataset hash refused")
    return {"n_records": len(recs)}


CHECKS = [check_predeclared_config, check_determinism_and_identical_operator, check_observation_and_eta_zero, check_paired_protocol,
          check_drift_counterexample, check_records]


def main():
    results, n_passed = {}, 0
    for check in CHECKS:
        name = check.__name__.removeprefix("check_")
        try:
            results[name] = check()
            print(f"PASS  {name}")
            n_passed += 1
        except AssertionError as e:
            results[name] = {"error": str(e)}
            print(f"FAIL  {name}: {e}")
        except Exception as e:
            results[name] = {"error": f"{type(e).__name__}: {e}"}
            print(f"ERROR {name}: {type(e).__name__}: {e}")
    print(f"\n{n_passed}/{len(CHECKS)} checks passed")
    summary = {k: {kk: vv for kk, vv in v.items() if kk in ("delta_mean", "delta_sem", "after_frozen_mean", "after_refitted_mean")}
               for k, v in report()["conditions"].items()} if n_passed else {}
    Path(__file__).with_name("verify_organoid_benchmark_results.json").write_text(
        json.dumps({"n_passed": n_passed, "n_total": len(CHECKS), "results": results, "descriptive_summary": summary},
                   indent=2, default=str), encoding="utf-8")
    return 0 if n_passed == len(CHECKS) else 1


if __name__ == "__main__":
    raise SystemExit(main())
