#!/usr/bin/env python3
"""Resource network control core (INTEGRATED_EXTENSION_ROADMAP.md Paket C5).

Checks:

  1. Hand-verified decoupled control case: x=(0.2,0.4,0.6), d=(1,1,1).
     Delta=1 minimal safe intervention is exactly (0.8,0.6,0.4) (sum 1.8,
     quadratic cost 1.16); Delta=2 needs (0.9,0.8,0.7) (sum 2.4, infeasible
     under a shared budget of 2); holding the Delta=1 intervention for 2
     time units ends at x=(-0.2,-0.4,-0.6).
  2. whole_interval_safety reports all FOUR distinct statuses on purpose-
     built cases: certified_safe, boundary_touch (x ends at exactly 0, which
     is ALLOWED), strict_violation, and not_certified (an uncertain initial
     state whose lower bound is already negative).
  3. solve_network_qp on a fully DECOUPLED network (no edges) matches the
     closed-form minimal_decoupled_intervention's cost -- an independent
     cross-check of the general QP solver against an exact formula.
  4. Structural counter-check: adding a freely-switchable-off edge to a
     network can only WEAKLY IMPROVE (never worsen) the QP's optimal cost.
  5. The infeasible path is correctly distinguished from a hypothetical
     solver failure (an "infeasible" verdict requires that even the most
     generous box point fails safety).
  6. SCF_REVIEW_C0_C7_4ed0cd9.md finding R2 (a real bug, independently
     reproduced before fixing): solve_network_qp must never report
     feasible=True / boundary_touch for a trajectory that starts NEGATIVE
     and only reaches 0 by the interval's end -- Astra's exact
     counterexample (1 node, no edges, x_lower=-0.1, d=0, Delta=1, u_max=1,
     budget=1) is now reported as feasible=False, safety.status=
     "already_violated", distinct from the "not_certified" status reserved
     for a genuinely uncertain lower bound.
  7. SCF_REVIEW_C0_C7_4ed0cd9.md finding R5 (a real bug, independently
     reproduced before fixing): forcing zero solver restarts on a problem
     with a KNOWN feasible witness (3 decoupled buffers,
     x=(0.2,0.4,0.6), d=(1,1,1), Delta=1, u_max=(1,1,1), budget=2 -- witness
     u=(0.8,0.6,0.4), sum 1.8) used to report "infeasible" because the
     single "most generous corner" checked (sum 3) violates the shared
     budget -- even though a real feasible point exists elsewhere. Now
     reports "optimizer_failed" (confirmed via an exact LP feasibility
     check, not a single corner point); a genuinely infeasible problem still
     correctly reports "infeasible".
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from scoped_correspondence.viability.resource_network_control import (  # noqa: E402
    ResourceNetwork,
    whole_interval_safety,
    minimal_decoupled_intervention,
    solve_network_qp,
)


def require(ok, msg):
    if not bool(ok):
        raise AssertionError(msg)


DECOUPLED_NET = ResourceNetwork(n_nodes=3, edges=())
X0 = np.array([0.2, 0.4, 0.6])
D0 = np.array([1.0, 1.0, 1.0])


def check_decoupled_control_case():
    u1 = minimal_decoupled_intervention(X0, D0, Delta=1.0)
    require(np.allclose(u1, [0.8, 0.6, 0.4], atol=1e-9), f"Delta=1 minimal intervention should be (0.8,0.6,0.4), got {u1!r}")
    require(abs(float(np.sum(u1)) - 1.8) < 1e-9, "sum should be 1.8")
    require(abs(float(np.sum(u1 ** 2)) - 1.16) < 1e-9, f"quadratic cost should be 1.16, got {np.sum(u1**2)!r}")

    u2 = minimal_decoupled_intervention(X0, D0, Delta=2.0)
    require(np.allclose(u2, [0.9, 0.8, 0.7], atol=1e-9), f"Delta=2 minimal intervention should be (0.9,0.8,0.7), got {u2!r}")
    require(abs(float(np.sum(u2)) - 2.4) < 1e-9, "sum should be 2.4")
    require(np.sum(u2) > 2.0, "Delta=2's minimal sum should exceed the shared budget of 2 (infeasible)")

    x_after = X0 + 2.0 * (u1 - D0)
    require(np.allclose(x_after, [-0.2, -0.4, -0.6], atol=1e-9), f"holding Delta=1's intervention for 2 units should end at (-0.2,-0.4,-0.6), got {x_after!r}")
    return {"u1": u1.tolist(), "u2": u2.tolist(), "x_after_2units": x_after.tolist()}


def check_safety_status_distinctions():
    B = DECOUPLED_NET.incidence_matrix()
    f_empty = np.zeros(0)

    r_safe = whole_interval_safety(X0, B, f_empty, u=D0, d_upper=D0, Delta=1.0)
    require(r_safe.status == "certified_safe", f"u=d exactly should be certified_safe, got {r_safe.status!r}")

    u_boundary = minimal_decoupled_intervention(X0, D0, Delta=1.0)  # exactly reaches 0 at at least one node
    r_touch = whole_interval_safety(X0, B, f_empty, u=u_boundary, d_upper=D0, Delta=1.0)
    require(r_touch.status == "boundary_touch", f"the minimal intervention should exactly touch 0, got {r_touch.status!r}")

    r_violation = whole_interval_safety(X0, B, f_empty, u=np.zeros(3), d_upper=D0, Delta=1.0)
    require(r_violation.status == "strict_violation", f"no intervention at all should strictly violate, got {r_violation.status!r}")
    require(set(r_violation.violating_nodes) == {0, 1, 2}, f"all 3 nodes should be violating, got {r_violation.violating_nodes!r}")

    x_uncertain_lower = np.array([0.2, -0.1, 0.6])  # node 1's lower bound is already negative
    r_uncertain = whole_interval_safety(x_uncertain_lower, B, f_empty, u=D0, d_upper=D0, Delta=1.0)
    require(r_uncertain.status == "not_certified", f"a negative x_lower should be not_certified (not 'unsafe'), got {r_uncertain.status!r}")
    return {"safe": r_safe.status, "touch": r_touch.status, "violation": r_violation.status, "uncertain": r_uncertain.status}


def check_qp_matches_closed_form_decoupled():
    u_closed = minimal_decoupled_intervention(X0, D0, Delta=1.0)
    cost_closed = float(np.sum(u_closed ** 2))

    result = solve_network_qp(
        DECOUPLED_NET, x_lower=X0, d_upper=D0, Delta=1.0,
        u_max=np.array([2.0, 2.0, 2.0]), edge_cap=np.zeros(0),
        total_supply_cap=10.0, w=np.array([1.0, 1.0, 1.0]), v=np.zeros(0),
    )
    require(result.status == "solved", f"decoupled QP should solve, got status {result.status!r}")
    require(abs(result.cost - cost_closed) < 1e-6, f"QP cost ({result.cost!r}) should match the closed-form cost ({cost_closed!r})")
    require(np.allclose(result.u, u_closed, atol=1e-4), f"QP solution ({result.u!r}) should match the closed form ({u_closed!r})")
    return {"qp_cost": result.cost, "closed_form_cost": cost_closed}


def check_structural_extra_edge_weakly_improves():
    # 2-node network: node 0 has surplus, node 1 has a deficit it must cover via
    # external supply u alone (no edge) vs. optionally via a 0->1 edge too.
    x_lower = np.array([1.0, 0.05])
    d_upper = np.array([0.5, 1.0])
    u_max = np.array([2.0, 2.0])
    w = np.array([1.0, 1.0])

    net_no_edge = ResourceNetwork(n_nodes=2, edges=((0, 1),))
    result_no_edge = solve_network_qp(
        net_no_edge, x_lower, d_upper, Delta=1.0, u_max=u_max, edge_cap=np.array([0.0]),
        total_supply_cap=10.0, w=w, v=np.array([0.1]),
    )
    result_with_edge = solve_network_qp(
        net_no_edge, x_lower, d_upper, Delta=1.0, u_max=u_max, edge_cap=np.array([2.0]),
        total_supply_cap=10.0, w=w, v=np.array([0.1]),
    )
    require(result_no_edge.status == "solved" and result_with_edge.status == "solved", "both variants should solve")
    require(
        result_with_edge.cost <= result_no_edge.cost + 1e-6,
        f"enabling the edge must not make the optimum WORSE: with-edge cost {result_with_edge.cost!r} "
        f"vs. edge-disabled cost {result_no_edge.cost!r}",
    )
    return {"cost_no_edge": result_no_edge.cost, "cost_with_edge": result_with_edge.cost}


def check_infeasible_distinct_from_optimizer_failed():
    result = solve_network_qp(
        DECOUPLED_NET, x_lower=X0, d_upper=D0, Delta=1.0,
        u_max=np.array([0.01, 0.01, 0.01]),  # far too small to cover d=1 anywhere
        edge_cap=np.zeros(0), total_supply_cap=10.0, w=np.array([1.0, 1.0, 1.0]), v=np.zeros(0),
    )
    require(result.status == "infeasible", f"an unreachable safety target should report 'infeasible', got {result.status!r}")
    require(not result.feasible, "infeasible result must have feasible=False")
    return {"status": result.status}


def check_r2_negative_start_not_certified_safe():
    net = ResourceNetwork(n_nodes=1, edges=())
    x_lower = np.array([-0.1])
    d_upper = np.array([0.0])
    result = solve_network_qp(
        net, x_lower=x_lower, d_upper=d_upper, Delta=1.0,
        u_max=np.array([1.0]), edge_cap=np.zeros(0), total_supply_cap=1.0,
        w=np.array([1.0]), v=np.zeros(0),
    )
    require(result.status == "solved", f"the recovery action itself should still be found (status='solved'), got {result.status!r}")
    require(not result.feasible, "a trajectory that starts negative must NOT be reported as feasible, even if it recovers by the interval's end")
    require(result.safety.status == "already_violated",
            f"a CERTAIN negative x_lower must be labeled 'already_violated', not 'not_certified' or 'boundary_touch'; got {result.safety.status!r}")

    # Independently confirm the actual trajectory is negative throughout [0,1).
    u = float(result.u[0])
    for t in (0.0, 0.25, 0.5, 0.75, 0.99):
        require(x_lower[0] + u * t < 0.0, f"t={t}: trajectory should still be negative, got {x_lower[0] + u * t!r}")
    return {"u": result.u.tolist(), "safety_status": result.safety.status, "feasible": result.feasible}


def check_r5_solver_failure_not_reported_as_infeasible():
    net = ResourceNetwork(n_nodes=3, edges=())
    x0 = np.array([0.2, 0.4, 0.6])
    d0 = np.array([1.0, 1.0, 1.0])
    # Force zero restarts -- the solver never even attempts to converge --
    # but a known feasible witness u=(0.8,0.6,0.4) (sum 1.8 <= budget 2) exists.
    result = solve_network_qp(
        net, x_lower=x0, d_upper=d0, Delta=1.0, u_max=np.array([1.0, 1.0, 1.0]),
        edge_cap=np.zeros(0), total_supply_cap=2.0, w=np.array([1.0, 1.0, 1.0]), v=np.zeros(0),
        n_restarts=0,
    )
    require(result.status == "optimizer_failed",
            f"a solver failure with a KNOWN feasible witness elsewhere must report 'optimizer_failed', got {result.status!r}")

    # A genuinely infeasible problem (target unreachable at any box point) must
    # still correctly report 'infeasible', not be swept into 'optimizer_failed'.
    result_genuine = solve_network_qp(
        net, x_lower=x0, d_upper=d0, Delta=1.0, u_max=np.array([0.01, 0.01, 0.01]),
        edge_cap=np.zeros(0), total_supply_cap=10.0, w=np.array([1.0, 1.0, 1.0]), v=np.zeros(0),
    )
    require(result_genuine.status == "infeasible", f"a genuinely infeasible problem should still report 'infeasible', got {result_genuine.status!r}")
    return {"forced_failure_status": result.status, "genuine_infeasible_status": result_genuine.status}


CHECKS = [
    ("decoupled_control_case", check_decoupled_control_case),
    ("safety_status_distinctions", check_safety_status_distinctions),
    ("qp_matches_closed_form_decoupled", check_qp_matches_closed_form_decoupled),
    ("structural_extra_edge_weakly_improves", check_structural_extra_edge_weakly_improves),
    ("infeasible_distinct_from_optimizer_failed", check_infeasible_distinct_from_optimizer_failed),
    ("r2_negative_start_not_certified_safe", check_r2_negative_start_not_certified_safe),
    ("r5_solver_failure_not_reported_as_infeasible", check_r5_solver_failure_not_reported_as_infeasible),
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json-out", type=Path, default=Path(__file__).with_name("verify_resource_network_control_results.json"))
    args = parser.parse_args()

    report = {
        "package": "INTEGRATED_EXTENSION_ROADMAP.md Paket C5 (resource network control core)",
        "timestamp": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "python": sys.version.split()[0],
        "checks": {},
    }

    all_ok = True
    for name, fn in CHECKS:
        try:
            detail = fn()
            report["checks"][name] = {"status": "pass", "detail": detail}
            print(f"PASS  {name}")
        except AssertionError as e:
            all_ok = False
            report["checks"][name] = {"status": "fail", "error": str(e)}
            print(f"FAIL  {name}: {e}")
        except Exception as e:  # noqa: BLE001
            all_ok = False
            report["checks"][name] = {"status": "error", "error": f"{type(e).__name__}: {e}"}
            print(f"ERROR {name}: {type(e).__name__}: {e}")

    args.json_out.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    print(f"\n{sum(1 for c in report['checks'].values() if c['status'] == 'pass')}/{len(CHECKS)} checks passed")
    print(f"Report written to {args.json_out}")
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
