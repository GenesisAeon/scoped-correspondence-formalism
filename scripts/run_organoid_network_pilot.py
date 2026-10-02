"""Organoid-network pilot CLI (Paket ON7, ORGANOID_NETWORK_ROADMAP.md).

    python scripts/run_organoid_network_pilot.py --scenario exact --output out/exact.json
    python scripts/run_organoid_network_pilot.py --scenario adaptive --config configs/organoid_minimal.json --output out/adaptive.json
    python scripts/run_organoid_network_pilot.py --scenario confounds --output out/confounds.json
    python scripts/run_organoid_network_pilot.py --scenario real --data DIR   # ON6b: refused (data gates)

Synthetic, methodological pilot. No three-module threshold, no causal or
learning claim; the real-data mode is refused until an ON6b dataset with
provenance (docs/real_data_provenance.md) exists -- never an empty success.
"""
from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from scoped_correspondence.validation.modular_networks.channels import bayes_accuracy_gaussian, exact_channel_report
from scoped_correspondence.validation.modular_networks.decoders import (
    best_single_affine_threshold_accuracy_xor,
    group_mean_and_sem2,
    sign_flip_test,
)
from scoped_correspondence.validation.modular_networks.evaluation import BenchmarkConfig, run_benchmark
from scoped_correspondence.validation.modular_networks.information import (
    directed_report,
    information_signature,
    label_confounding,
)
from scoped_correspondence.validation.modular_networks.observation_controls import (
    exact_information_bits,
    observe_full,
    observe_sum,
)


def scenario_exact():
    d = Fraction(1, 2)
    return {
        "evidence_kind": "exhaustive_finite", "empirical_status": "synthetic_only",
        "full_observer_bits": str(exact_information_bits(d, observe_full)),
        "sum_observer_bits": str(exact_information_bits(d, observe_sum)),
        "bayes_accuracy_delta_sigma_half": bayes_accuracy_gaussian(0.5, 0.5),
        "bsc_vs_z_at_accuracy_3_4": {
            "bsc_bits": exact_channel_report([[0.75, 0.25], [0.25, 0.75]], [0.5, 0.5], coding="identity").information_at_prior_bits,
            "z_bits": exact_channel_report([[1.0, 0.0], [0.5, 0.5]], [0.5, 0.5], coding="identity").information_at_prior_bits,
        },
        "xor_signature": list(information_signature({(a, b, a ^ b): 0.25 for a in (0, 1) for b in (0, 1)})),
        "xor_best_single_affine": str(best_single_affine_threshold_accuracy_xor()),
    }


def scenario_confounds():
    vals = [Fraction(v) for v in range(5)]
    return {
        "evidence_kind": "exhaustive_finite", "empirical_status": "synthetic_only",
        "block_time_equals_label_bits": label_confounding({(s, s): 0.5 for s in (0, 1)}),
        "randomised_bits": label_confounding({(s, t): 0.25 for s in (0, 1) for t in (0, 1)}),
        "common_driver_directed_information": directed_report({((u, 0), (0, u)): 0.5 for u in (0, 1)}).I_directed,
        "common_driver_causal_claim": False,
        "sem2_preparation_vs_pooled": [str(group_mean_and_sem2(vals)[1]),
                                       str(group_mean_and_sem2([v for v in vals for _ in range(100)])[1])],
        "sign_flip_p_five_positive": str(sign_flip_test([1] * 5)),
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--scenario", choices=("exact", "adaptive", "confounds", "real"), required=True)
    ap.add_argument("--config", type=Path, default=ROOT / "configs" / "organoid_minimal.json")
    ap.add_argument("--data", type=Path, default=None)
    ap.add_argument("--output", type=Path, default=None)
    a = ap.parse_args(argv)
    if a.scenario == "real":
        print("ON6b real-data mode: blocked -- no organoid dataset with provenance, licence and preparation IDs is "
              "available (see ORGANOID_NETWORK_ROADMAP.md, ON6b; DEEP_RESEARCH_BACKLOG.md D2).", file=sys.stderr)
        return 2
    if a.scenario == "exact":
        out = scenario_exact()
    elif a.scenario == "confounds":
        out = scenario_confounds()
    else:
        if not a.config.exists():
            print(f"configuration {a.config} missing: the run must be pre-declared", file=sys.stderr)
            return 2
        cfg = BenchmarkConfig.from_json(json.loads(a.config.read_text(encoding="utf-8")))
        out = run_benchmark(cfg, a.config)
    text = json.dumps(out, indent=2, default=str, allow_nan=False)
    if a.output:
        a.output.parent.mkdir(parents=True, exist_ok=True)
        a.output.write_text(text + "\n", encoding="utf-8")
        print(f"wrote {a.output}")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
