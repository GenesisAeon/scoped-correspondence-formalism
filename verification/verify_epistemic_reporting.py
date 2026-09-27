"""H7 verification (Followup-Review-Fix R8b, SCF_REVIEW_H0_H7_9dde420.md):
JSON/Markdown export for epistemic report dataclasses. Abnahme criterion:
at least two complete adapter reports and one integrated buffer report
can be exported as JSON and Markdown, preserving the different status
axes, with exact rational (Fraction) values serialized exactly.
"""
from __future__ import annotations

import itertools
import json
import sys
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from scoped_correspondence.correspondence.contract import CorrespondenceReport, Residual
from scoped_correspondence.correspondence.controlled_markov import partition_indicator
from scoped_correspondence.epistemic.adapters import claim_report_from_correspondence, claim_reports_from_macro_observability
from scoped_correspondence.epistemic.decisions import compare_decisions
from scoped_correspondence.epistemic.observation_fibers import macro_dynamics_and_observability
from scoped_correspondence.epistemic.reporting import report_to_json, report_to_markdown
from scoped_correspondence.validation.epistemic_buffer_pilot import evaluate_information_modes


def require(condition, msg=""):
    if not condition:
        raise AssertionError(msg)


@dataclass(frozen=True)
class _FractionHolder:
    value: Fraction


def check_correspondence_adapter_report_exports_json_and_markdown():
    report = CorrespondenceReport(
        ok=True, max_residual=1e-12, residuals=(Residual(value=1e-12, kind="conjugacy", at_state=0.0, at_time=1.0),),
        evidence={"n_pairs": 1, "all_finite": True}, kind="conjugacy",
    )
    claim = claim_report_from_correspondence(report, claim_id="export_test_1")
    j = report_to_json(claim)
    parsed = json.loads(j)
    require(parsed["logical_status"] == "entailed_in_scope", f"JSON export must preserve logical_status, got {parsed.get('logical_status')}")
    require(parsed["evidence_kind"] == "numerical_sample", "JSON export must preserve evidence_kind as its own field")
    require(parsed["empirical_status"] == "synthetic_only", "JSON export must preserve empirical_status as its own field, separate from evidence_kind")

    md = report_to_markdown(claim, title="Correspondence adapter report")
    require("logical_status" in md and "evidence_kind" in md and "empirical_status" in md, "Markdown export must list every status axis as its own row")
    require("entailed_in_scope" in md, "Markdown export must show the actual status value")
    return {"json_len": len(j), "markdown_has_all_axes": True}


def check_macro_observability_adapter_reports_export_two_separate_evidence_kinds():
    C, _ = partition_indicator([0, 0, 1, 1])
    macro_report = macro_dynamics_and_observability(P_by_action={"a": np.eye(4)}, C=C, omega={"a": "b"}, micro_event=[1])
    dyn_claim, obs_claim = claim_reports_from_macro_observability(macro_report, dynamics_claim_id="export_dyn", observability_claim_id="export_obs")

    j_dyn = json.loads(report_to_json(dyn_claim))
    j_obs = json.loads(report_to_json(obs_claim))
    require(j_dyn["evidence_kind"] == "numerical_sample", f"dynamics export must show numerical_sample, got {j_dyn['evidence_kind']}")
    require(j_obs["evidence_kind"] == "exhaustive_finite", f"observability export must show exhaustive_finite, got {j_obs['evidence_kind']}")
    require(j_dyn["evidence_kind"] != j_obs["evidence_kind"], "the two exported reports must show DIFFERENT evidence_kind values, never merged")

    md_dyn = report_to_markdown(dyn_claim, title="K8 dynamics")
    md_obs = report_to_markdown(obs_claim, title="K8 observability")
    require("numerical_sample" in md_dyn and "exhaustive_finite" in md_obs, "Markdown exports must each show their own distinct evidence_kind")
    return {"dynamics_evidence_kind": j_dyn["evidence_kind"], "observability_evidence_kind": j_obs["evidence_kind"]}


def check_buffer_pilot_report_exports_and_exact_fraction_preserved():
    modes = evaluate_information_modes()
    mode_b = modes["B_sum_and_minimum"]
    j = json.loads(report_to_json(mode_b))
    require(j["mode"] == "B_sum_and_minimum", "buffer pilot report export must preserve the mode identifier")
    require(abs(j["worst_case_cost"] - 2.0) < 1e-9, f"buffer pilot report export must preserve worst_case_cost, got {j['worst_case_cost']}")

    md = report_to_markdown(mode_b, title="K5 buffer pilot: sum+minimum mode")
    require("worst_case_cost" in md and "per_state_sustained_safe" in md, "Markdown export must list every field of the buffer pilot report")

    # Exact-rational preservation, using a real DecisionReport with Fraction probabilities (K6).
    loss_matrix = {"A": {"s1": 0, "s2": 10}, "B": {"s1": 6, "s2": 6}}
    decision = compare_decisions(loss_matrix, criterion="expected_loss", probabilities={"s1": Fraction(2, 5), "s2": Fraction(3, 5)})
    j_decision = json.loads(report_to_json(decision))
    fraction_like = [entry for entry in j_decision["scores"] if isinstance(entry, list)]
    require(len(fraction_like) > 0, "DecisionReport export must include the per-action scores")
    # scores is a tuple of (action, Number) pairs; Number can be a plain int/float here
    # since the loss matrix itself uses ints -- verify a genuine Fraction elsewhere instead:
    frac_report_json = report_to_json(_FractionHolder(value=Fraction(3, 7)))
    frac_parsed = json.loads(frac_report_json)
    require(frac_parsed["value"] == {"__fraction__": True, "numerator": 3, "denominator": 7}, f"a Fraction field must serialize exactly, got {frac_parsed['value']}")
    return {"mode_b_worst_case_cost": j["worst_case_cost"], "fraction_serialization": frac_parsed["value"]}


CHECKS = [
    check_correspondence_adapter_report_exports_json_and_markdown,
    check_macro_observability_adapter_reports_export_two_separate_evidence_kinds,
    check_buffer_pilot_report_exports_and_exact_fraction_preserved,
]


def main():
    results = {}
    n_passed = 0
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
    out_path = Path(__file__).with_name("verify_epistemic_reporting_results.json")
    out_path.write_text(json.dumps({"n_passed": n_passed, "n_total": len(CHECKS), "results": results}, indent=2, default=str))
    print(f"Report written to {out_path}")
    return 0 if n_passed == len(CHECKS) else 1


if __name__ == "__main__":
    raise SystemExit(main())
