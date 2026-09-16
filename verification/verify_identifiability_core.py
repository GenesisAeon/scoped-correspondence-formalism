#!/usr/bin/env python3
"""Equivalence checks for Identifiability core (Milestone 5).

Matches legacy verify_extensions.py:
  - e02_sampling_alias_and_conditioning
  - e07_effective_information_ensembles
  - e08_fixed_ensemble_data_processing
  - e09_svd_does_not_imply_ei
  - e12_parameter_scaling_nonidentifiability
  - e15_predictive_states (optional bonus)

Stdlib + NumPy. JSON {count, passed, failed, report}; numbers from this run.
"""
from __future__ import annotations

import argparse
import datetime as dt
import itertools
import json
import math
import platform
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from scoped_correspondence import (  # noqa: E402
    ScopeViolationError,
    delay_amplification,
    delay_conditioning_report,
    effective_information_baseline,
    fixed_ensemble_data_processing,
    identifiability_jacobian_rank,
    indistinguishable_delay_vectors,
    parameter_scaling_invariance,
    predictive_states,
    svd_emergence_vs_ei,
)


def require(ok, msg):
    if not bool(ok):
        raise AssertionError(msg)


def near(a, b, atol=1e-10, rtol=1e-9):
    if not np.allclose(a, b, atol=atol, rtol=rtol):
        raise AssertionError(f"{a!r} != {b!r}")


def load_extension_evidence(name: str):
    path = ROOT / "verification" / "extension_results.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    for c in data["checks"]:
        if c.get("name") == name:
            require(c["status"] == "passed", f"legacy {name} not passed")
            return c["evidence"]
    raise AssertionError(f"legacy evidence {name} missing")


def mig_id_e02_sampling_alias_and_conditioning():
    """Reproduce e02 via delay_amplification / delay_conditioning_report."""
    expected = load_extension_evidence("e02_sampling_alias_and_conditioning")
    report = delay_conditioning_report(theta=0.7, alphas=(0.7, 0.01), n=8)
    near(report["indistinguishable_delay_vectors"], expected["indistinguishable_delay_vectors"])
    near(report["inverse_sine_factors"]["0.7"], expected["inverse_sine_factors"]["0.7"])
    near(report["inverse_sine_factors"]["0.01"], expected["inverse_sine_factors"]["0.01"])
    near(delay_amplification(0.7), expected["inverse_sine_factors"]["0.7"])
    near(delay_amplification(0.01), expected["inverse_sine_factors"]["0.01"])
    require(
        report["inverse_sine_factors"]["0.01"] > 50 * report["inverse_sine_factors"]["0.7"],
        "conditioning countercase",
    )
    vecs = indistinguishable_delay_vectors(0.7, 8)
    near(vecs, expected["indistinguishable_delay_vectors"])
    near(math.cos(0.7), math.cos(-0.7))
    # Singular alpha rejected
    try:
        delay_amplification(0.0)
        raise AssertionError("alpha=0 should raise ScopeViolationError")
    except ScopeViolationError:
        pass
    return {
        "indistinguishable_delay_vectors": report["indistinguishable_delay_vectors"],
        "inverse_sine_factors": report["inverse_sine_factors"],
        "legacy_id": "e02_sampling_alias_and_conditioning",
        "legacy_alias": "VER-REC-e02_sampling_alias_and_conditioning",
        "source": "identifiability.delay_*  <->  e02",
    }


def mig_id_e07_effective_information_ensembles():
    """Reproduce e07 EI baseline numbers exactly."""
    expected = load_extension_evidence("e07_effective_information_ensembles")
    report = effective_information_baseline()
    near(report["EI_uniform_micro"], expected["EI_uniform_micro"])
    near(report["EI_uniform_macro"], expected["EI_uniform_macro"])
    near(report["delta_EI"], expected["delta_EI"])
    near(report["EI_matched_micro"], expected["EI_matched_micro"])
    near(report["lifted_preparation"], expected["lifted_preparation"])
    near(report["EI_uniform_macro"], 1.0)
    near(report["EI_matched_micro"], 1.0)
    near(report["EI_uniform_micro"], report["EI_uniform_micro_via_entropies"])
    # Hand: H([0.25,0.75]) = -0.25*log2(0.25)-0.75*log2(0.75)
    hand_h = -0.25 * math.log2(0.25) - 0.75 * math.log2(0.75)
    near(report["EI_uniform_micro"], hand_h)
    return {
        "EI_uniform_micro": report["EI_uniform_micro"],
        "EI_uniform_macro": report["EI_uniform_macro"],
        "delta_EI": report["delta_EI"],
        "EI_matched_micro": report["EI_matched_micro"],
        "lifted_preparation": report["lifted_preparation"],
        "legacy_id": "e07_effective_information_ensembles",
        "legacy_alias": "VER-INF-EI-e07_effective_information_ensembles",
        "source": "identifiability.effective_information_baseline  <->  e07",
    }


def mig_id_e08_fixed_ensemble_data_processing():
    """Reproduce e08: 150 fixed-ensemble DPI comparisons, seed 1977."""
    expected = load_extension_evidence("e08_fixed_ensemble_data_processing")
    report = fixed_ensemble_data_processing(seed=1977, n_kernels=10, n_states=4)
    near(report["random_seed"], expected["random_seed"])
    near(report["fixed_ensemble_comparisons"], expected["fixed_ensemble_comparisons"])
    require(report["fixed_ensemble_comparisons"] == 150, "10 kernels * 15 partitions")
    require(report["max_micro_minus_macro"] >= 0.0, "DPI gaps nonnegative")
    return {
        "random_seed": report["random_seed"],
        "fixed_ensemble_comparisons": report["fixed_ensemble_comparisons"],
        "max_micro_minus_macro": report["max_micro_minus_macro"],
        "legacy_id": "e08_fixed_ensemble_data_processing",
        "legacy_alias": "VER-INF-EI-e08_fixed_ensemble_data_processing",
        "source": "identifiability.fixed_ensemble_data_processing  <->  e08",
    }


def mig_id_e09_svd_does_not_imply_ei():
    """Reproduce e09: delta_svd=0.75, EI=0, 15 partitions."""
    expected = load_extension_evidence("e09_svd_does_not_imply_ei")
    report = svd_emergence_vs_ei()
    near(report["rank"], expected["rank"])
    near(report["singular_values"], expected["singular_values"])
    near(report["delta_svd"], expected["delta_svd"])
    near(report["delta_svd"], 0.75)
    near(report["EI"], expected["EI"])
    near(report["EI"], 0.0)
    near(report["all_partitions_checked"], expected["all_partitions_checked"])
    near(report["all_partitions_checked"], 15)
    # Hand: spectrum sum=1, rank=1, n=4 -> 1*(1/1 - 1/4)=0.75
    hand = float(sum(report["singular_values"]) * (1 / report["rank"] - 1 / 4))
    near(hand, 0.75)
    # Block-matrix spectral check from legacy (not exported API; sanity only)
    from scoped_correspondence.identifiability.core import demo_ei_matrices

    block, _, _, _ = demo_ei_matrices()
    bs = np.linalg.svd(block, compute_uv=False)
    near(bs, [1, 1, 0, 0])
    near(bs.sum() * (1 / 2 - 1 / 4), 0.5)
    return {
        "rank": report["rank"],
        "singular_values": report["singular_values"],
        "delta_svd": report["delta_svd"],
        "EI": report["EI"],
        "all_partitions_checked": report["all_partitions_checked"],
        "legacy_id": "e09_svd_does_not_imply_ei",
        "legacy_alias": "VER-DIAG-SVD-e09_svd_does_not_imply_ei",
        "source": "identifiability.svd_emergence_vs_ei  <->  e09 / FORMALISM section 10",
    }


def mig_id_e12_parameter_scaling_nonidentifiability():
    """Reproduce e12: tanh invariance + Jacobian rank 1."""
    expected = load_extension_evidence("e12_parameter_scaling_nonidentifiability")
    sigma = 2.2
    maximum = 0.0
    for gamma, scale in itertools.product(np.linspace(-2, 2, 31), [0.1, 2, 100]):
        report = parameter_scaling_invariance(sigma, float(gamma), float(scale))
        require(report["invariant"], "tanh must be invariant under scaling")
        near(report["original"], report["transformed"])
        maximum = max(maximum, report["abs_error"])
    near(maximum, expected["max_response_error"], atol=1e-15)
    a = 3.0
    g = np.linspace(-1, 1, 21)
    rank = identifiability_jacobian_rank(sigma, a, g)
    near(rank, expected["response_jacobian_rank"])
    near(rank, 1)
    require(rank == 1, "expected unidentifiable product sigma*a")
    return {
        "max_response_error": maximum,
        "response_jacobian_rank": rank,
        "identified_combination": expected["identified_combination"],
        "legacy_id": "e12_parameter_scaling_nonidentifiability",
        "legacy_alias": "VER-COR-e12_parameter_scaling_nonidentifiability",
        "source": "identifiability.parameter_scaling_*  <->  e12 / FORMALISM section 12",
    }


def mig_id_e15_predictive_states():
    """Optional bonus: reproduce e15 predictive-state counts."""
    expected = load_extension_evidence("e15_predictive_states")
    report = predictive_states()
    near(
        report["persistent_binary_chain_predictive_states"],
        expected["persistent_binary_chain_predictive_states"],
    )
    near(report["iid_predictive_states"], expected["iid_predictive_states"])
    near(report["joint_paths_enumerated"], expected["joint_paths_enumerated"])
    near(report["max_conditioning_error"], expected["max_conditioning_error"])
    near(report["persistent_binary_chain_predictive_states"], 2)
    near(report["iid_predictive_states"], 1)
    near(report["joint_paths_enumerated"], 128)
    return {
        "persistent_binary_chain_predictive_states": report[
            "persistent_binary_chain_predictive_states"
        ],
        "iid_predictive_states": report["iid_predictive_states"],
        "joint_paths_enumerated": report["joint_paths_enumerated"],
        "max_conditioning_error": report["max_conditioning_error"],
        "legacy_id": "e15_predictive_states",
        "legacy_alias": "VER-CLS-PRED-e15_predictive_states",
        "source": "identifiability.predictive_states  <->  e15",
    }


CHECKS = [
    ("MIG-ID-e02_sampling_alias_and_conditioning", mig_id_e02_sampling_alias_and_conditioning),
    ("MIG-ID-e07_effective_information_ensembles", mig_id_e07_effective_information_ensembles),
    ("MIG-ID-e08_fixed_ensemble_data_processing", mig_id_e08_fixed_ensemble_data_processing),
    ("MIG-ID-e09_svd_does_not_imply_ei", mig_id_e09_svd_does_not_imply_ei),
    ("MIG-ID-e12_parameter_scaling_nonidentifiability", mig_id_e12_parameter_scaling_nonidentifiability),
    ("MIG-ID-e15_predictive_states", mig_id_e15_predictive_states),
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).with_name("verify_identifiability_core_results.json"),
    )
    args = parser.parse_args()
    results = []
    for name, fn in CHECKS:
        try:
            evidence = fn()
            results.append({"id": name, "status": "passed", "evidence": evidence})
        except Exception as exc:
            results.append(
                {"id": name, "status": "failed", "error": f"{type(exc).__name__}: {exc}"}
            )
    passed = sum(r["status"] == "passed" for r in results)
    failed = [r["id"] for r in results if r["status"] != "passed"]
    report = {
        "milestone": "M5_identifiability_core",
        "kind": (
            "Legacy equivalence: e02/e07/e08/e09/e12 (+ optional e15) "
            "via identifiability.core"
        ),
        "generated_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "python": platform.python_version(),
        "numpy": np.__version__,
        "count": len(results),
        "passed": passed,
        "failed": len(failed),
        "empirical_validation": False,
        "checks": results,
    }
    args.output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    summary = {
        "count": report["count"],
        "passed": report["passed"],
        "failed": failed,
        "report": str(args.output.resolve()),
    }
    print(json.dumps(summary, ensure_ascii=False))
    raise SystemExit(0 if passed == len(results) else 1)


if __name__ == "__main__":
    main()
