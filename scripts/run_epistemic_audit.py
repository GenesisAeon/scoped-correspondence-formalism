#!/usr/bin/env python3
"""Reproducible local CLI for the H0-H7 epistemic/assumption-evidence
layer (`EPISTEMIC_AUDIT_ROADMAP.md`): reproduces the K1-K6 and K8
headline results (K7, randomized-regret reduction, is an optional
deepening with no dedicated production module -- see H0's hand-trace)
by calling the actual `scoped_correspondence.epistemic` /
`validation.epistemic_buffer_pilot` production code directly (not the
`verify_epistemic_*.py` test scripts) -- this is a demonstration/report
CLI, not a substitute for the checked-in regression suite.

Purely finite/analytic/synthetic examples throughout -- no real dataset,
no network access. Writes files only when explicitly asked: `--out` for
the JSON summary, `--report-dir` for full JSON+Markdown exports of two
adapter reports and one integrated buffer-pilot report (Followup-Review-
Fix R8b, SCF_REVIEW_H0_H7_9dde420.md).

Usage:
    python scripts/run_epistemic_audit.py [--out epistemic_audit_summary.json] [--report-dir out/]
"""
from __future__ import annotations

import argparse
import itertools
import json
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import numpy as np  # noqa: E402

from scoped_correspondence.correspondence.contract import CorrespondenceReport, Residual  # noqa: E402
from scoped_correspondence.correspondence.controlled_markov import partition_indicator  # noqa: E402
from scoped_correspondence.epistemic.adapters import (  # noqa: E402
    claim_report_from_correspondence,
    claim_reports_from_macro_observability,
)
from scoped_correspondence.epistemic.decisions import compare_decisions, uniform_safe_actions  # noqa: E402
from scoped_correspondence.epistemic.finite import audit_finite_claim  # noqa: E402
from scoped_correspondence.epistemic.observation_fibers import (  # noqa: E402
    identified_values,
    macro_dynamics_and_observability,
    observation_fiber,
)
from scoped_correspondence.epistemic.records import AssumptionSpec, ClaimSpec, FiniteDomainSpec  # noqa: E402
from scoped_correspondence.epistemic.reporting import report_to_json, report_to_markdown  # noqa: E402
from scoped_correspondence.epistemic.supports import find_minimal_inconsistent_core, find_minimal_support  # noqa: E402
from scoped_correspondence.validation.epistemic_buffer_pilot import (  # noqa: E402
    K5_FIBER_STATES,
    evaluate_information_modes,
    minimal_uniform_intervention,
)


def _assump(id_, predicate):
    return AssumptionSpec(id=id_, text=id_, role="structural", predicate=predicate)


def run_k1_k2_k3(results: dict) -> None:
    """H1/H2: minimal supports/cores (K1), vacuous antecedent (K2), scope
    extension counterexample (K3)."""
    domain = FiniteDomainSpec(id="k1_pqr", candidates=tuple(itertools.product([False, True], repeat=3)), scope_text="{0,1}^3")
    a1, a2, a3, a4 = (
        _assump("A1_p", lambda w: w[0]),
        _assump("A2_p_implies_q", lambda w: (not w[0]) or w[1]),
        _assump("A3_q_implies_r", lambda w: (not w[1]) or w[2]),
        _assump("A4_p_implies_r", lambda w: (not w[0]) or w[2]),
    )
    a5 = _assump("A5_not_r", lambda w: not w[2])
    claim_r = ClaimSpec(id="target_r", text="r", target=lambda w: bool(w[2]))

    support_1 = find_minimal_support(domain, [a1, a4, a3, a2], claim_r).support_ids
    support_2 = find_minimal_support(domain, [a1, a2, a3, a4], claim_r).support_ids
    core_1 = find_minimal_inconsistent_core(domain, [a1, a2, a3, a4, a5]).core_ids
    core_2 = find_minimal_inconsistent_core(domain, [a1, a4, a2, a3, a5]).core_ids
    results["K1_minimal_supports"] = {"support_A": sorted(support_1), "support_B": sorted(support_2)}
    results["K1_minimal_inconsistent_cores"] = {"core_A": sorted(core_1), "core_B": sorted(core_2)}

    a_not_p = _assump("A_not_p", lambda w: w[0] == 0)
    claim_p_implies_q = ClaimSpec(
        id="p_implies_q", text="p=>q", target=lambda w: (not w[0]) or w[1], antecedent=lambda w: bool(w[0]),
    )
    r_k2 = audit_finite_claim(domain, [a_not_p], claim_p_implies_q)
    results["K2_vacuous_antecedent"] = {
        "logical_status": r_k2.logical_status, "antecedent_reachable_in_scope": r_k2.antecedent_reachable_in_scope,
        "vacuity_kind": r_k2.vacuity_kind,
    }

    domain_w = FiniteDomainSpec(id="k3_w", candidates=(-1, 0, 1), scope_text="{-1,0,1}")
    domain_w_ext = FiniteDomainSpec(id="k3_w_ext", candidates=(-1, 0, 1, 2), scope_text="{-1,0,1,2}")
    claim_bounded = ClaimSpec(id="x_sq_le_1", text="x^2<=1", target=lambda x: x * x <= 1)
    r_w = audit_finite_claim(domain_w, [], claim_bounded)
    r_w_ext = audit_finite_claim(domain_w_ext, [], claim_bounded)
    results["K3_scope_extension"] = {
        "status_on_W": r_w.logical_status, "status_on_W_extended": r_w_ext.logical_status,
        "counterexample": r_w_ext.negative_witness,
    }


def run_k4_k8(results: dict) -> None:
    """H3: K4 fiber/identification, K8 dynamics-vs-observability."""
    domain = FiniteDomainSpec(id="k4_reserves", candidates=tuple(itertools.product(range(3), repeat=2)), scope_text="{0,1,2}^2")
    fiber = observation_fiber(domain, [], lambda x: x[0] + x[1], 2)
    q = identified_values(fiber, lambda x: (x[0] - x[1]) ** 2)
    both_ge1 = identified_values(fiber, lambda x: bool(x[0] >= 1 and x[1] >= 1))
    results["K4_fiber"] = {"fiber": sorted(fiber.fiber), "q_value_set": sorted(q.values), "boolean_claim_values": sorted(both_ge1.values, key=str)}

    C, _classes = partition_indicator([0, 0, 1, 1])
    macro_report = macro_dynamics_and_observability(
        P_by_action={"only_action": np.eye(4)}, C=C, omega={"only_action": "only_macro"}, micro_event=[1],
    )
    results["K8_dynamics_vs_observability"] = {
        "dynamics_exact": macro_report.dynamics_exact, "event_1_is_union_of_classes": macro_report.event_is_union_of_classes,
    }


def run_k5_k6(results: dict) -> None:
    """H4/H5: K5 finite+continuous uniform-vs-statewise, K6 minimax vs minimax-regret."""
    domain = FiniteDomainSpec(id="k5_finite", candidates=tuple(itertools.product(range(3), repeat=2)), scope_text="{0,1,2}^2")
    fiber = observation_fiber(domain, [], lambda x: x[0] + x[1], 2)

    def safety(w, u):
        x1, x2 = w
        u1, u2 = u
        return u1 >= (1 if x1 == 0 else 0) and u2 >= (1 if x2 == 0 else 0)

    r_b1 = uniform_safe_actions(fiber, [(0, 0), (1, 0), (0, 1)], safety)
    r_b2 = uniform_safe_actions(fiber, [(0, 0), (1, 0), (0, 1), (1, 1)], safety)
    u_min = minimal_uniform_intervention(K5_FIBER_STATES)
    modes = evaluate_information_modes()
    results["K5_finite_uniform_vs_statewise"] = {
        "budget1_statewise_feasible": r_b1.statewise_feasible, "budget1_uniformly_feasible": r_b1.uniformly_feasible,
        "budget2_uniformly_feasible": r_b2.uniformly_feasible, "budget2_uniform_safe_actions": r_b2.uniform_safe_actions,
    }
    results["K5_continuous_buffer_pilot"] = {
        "minimal_uniform_u": u_min, "minimal_uniform_budget": sum(u_min),
        "information_modes_worst_case_cost": {name: r.worst_case_cost for name, r in modes.items()},
    }

    loss_matrix = {"A": {"s1": 0, "s2": 10}, "B": {"s1": 6, "s2": 6}}
    r_minimax = compare_decisions(loss_matrix, criterion="minimax")
    r_regret = compare_decisions(loss_matrix, criterion="minimax_regret")
    r_below = compare_decisions(loss_matrix, criterion="expected_loss", probabilities={"s1": Fraction(41, 100), "s2": Fraction(59, 100)})
    r_at = compare_decisions(loss_matrix, criterion="expected_loss", probabilities={"s1": Fraction(2, 5), "s2": Fraction(3, 5)})
    r_above = compare_decisions(loss_matrix, criterion="expected_loss", probabilities={"s1": Fraction(39, 100), "s2": Fraction(61, 100)})
    results["K6_minimax_vs_minimax_regret"] = {
        "minimax_chosen": r_minimax.chosen_actions, "minimax_regret_chosen": r_regret.chosen_actions,
        "expected_loss_below_p0.6": r_below.chosen_actions, "expected_loss_at_p0.6": r_at.chosen_actions,
        "expected_loss_above_p0.6": r_above.chosen_actions,
    }


def run_report_exports(report_dir: Path) -> None:
    """Followup-Review-Fix R8b: export at least two complete adapter
    reports and one integrated buffer-pilot report as BOTH JSON and
    Markdown, via the shared `epistemic.reporting` module -- demonstrates
    the export capability end to end rather than leaving it untested."""
    report_dir.mkdir(parents=True, exist_ok=True)

    corr_report = CorrespondenceReport(
        ok=True, max_residual=1e-12, residuals=(Residual(value=1e-12, kind="conjugacy", at_state=0.0, at_time=1.0),),
        evidence={"n_pairs": 1, "all_finite": True}, kind="conjugacy",
    )
    claim = claim_report_from_correspondence(corr_report, claim_id="cli_export_correspondence")

    C, _classes = partition_indicator([0, 0, 1, 1])
    macro_report = macro_dynamics_and_observability(P_by_action={"a": np.eye(4)}, C=C, omega={"a": "b"}, micro_event=[1])
    dyn_claim, obs_claim = claim_reports_from_macro_observability(macro_report, dynamics_claim_id="cli_export_k8_dynamics", observability_claim_id="cli_export_k8_observability")

    modes = evaluate_information_modes()
    buffer_report = modes["B_sum_and_minimum"]

    for name, report in [
        ("adapter_correspondence", claim),
        ("adapter_k8_dynamics", dyn_claim),
        ("adapter_k8_observability", obs_claim),
        ("buffer_pilot_sum_and_minimum", buffer_report),
    ]:
        (report_dir / f"{name}.json").write_text(report_to_json(report))
        (report_dir / f"{name}.md").write_text(report_to_markdown(report, title=name))
    print(f"Report exports written to {report_dir}", file=sys.stderr)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=None, help="Optional path to write the summary as JSON.")
    parser.add_argument("--report-dir", type=Path, default=None, help="Optional directory to export full JSON+Markdown reports into.")
    args = parser.parse_args()

    results: dict = {}
    run_k1_k2_k3(results)
    run_k4_k8(results)
    run_k5_k6(results)

    print(json.dumps(results, indent=2, default=str))
    if args.out is not None:
        args.out.write_text(json.dumps(results, indent=2, default=str))
        print(f"\nWritten to {args.out}", file=sys.stderr)
    if args.report_dir is not None:
        run_report_exports(args.report_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
