"""J6 verification (SCOPE_COMPOSITION_EVIDENCE_ROADMAP.md, plan section 12):
structural identifiability with a precise scope.

Pflichtprüfungen: exact affine cases (J-C11 incl. consistent / inconsistent
observations and domain restrictions), the analytic reservoir control
(J-C12, known / unknown initial condition and known c), discrete ambiguity
(J-C13: local vs global, positive domain), an explicit ``unsupported``
status outside the implemented scope, and the separation from numerical
rank: a full numerical Jacobian rank does NOT certify global uniqueness.
Connections: existing observation fibres (finite candidates, H3) and the
existing parameter_scaling_invariance example (identifiability/core.py).

Expected values from verification/plan_controls/j_series_independent_controls.py.
"""
from __future__ import annotations

import json
import sys
from fractions import Fraction as F
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from scoped_correspondence.correspondence.domains import RationalBox
from scoped_correspondence.errors import ScopeViolationError
from scoped_correspondence.identifiability.core import parameter_scaling_invariance
from scoped_correspondence.identifiability.exact_linear import analyze_affine_identifiability, is_identifiable_combination
from scoped_correspondence.identifiability.structural_reports import (
    finite_candidate_fibre,
    reservoir_decay_report,
    square_map_report,
    unsupported_report,
)
from scoped_correspondence.dimensions.pi_groups import same_pi_span


def require(c, m=""):
    if not c:
        raise AssertionError(m)


def raises(fn, exc=(ScopeViolationError, ValueError)):
    try:
        fn()
    except exc:
        return True
    return False


def check_jc11_exact_affine_fibre():
    A = [[1, 1], [2, 2]]
    r = analyze_affine_identifiability(A)
    require(r.rank == 1 and not r.globally_identifiable_on_Rp, "rank 1 of 2")
    require(same_pi_span([tuple(int(x) for x in v) for v in r.null_space], [(1, -1)]), f"null space must be span(1,-1), got {r.null_space}")
    require(is_identifiable_combination(A, [1, 1]) and not is_identifiable_combination(A, [1, 0]) and not is_identifiable_combination(A, [0, 1]),
            "sum identifiable, split not")
    obs = analyze_affine_identifiability(A, observation=[3, 6])
    require(obs.observation_consistent and obs.particular_solution == (3, 0), f"z=(3,6): fibre (3,0)+t(1,-1), got {obs.particular_solution}")
    bad = analyze_affine_identifiability(A, observation=[3, 7])
    require(bad.observation_consistent is False and "empty fibre" in bad.notes[0], "z=(3,7) not in the image: empty fibre, not identification")
    with_b = analyze_affine_identifiability(A, [1, 2], observation=[4, 8])
    require(with_b.observation_consistent and with_b.particular_solution == (3, 0), "offset b is subtracted exactly")
    require(analyze_affine_identifiability([[1, 0], [0, 1]]).globally_identifiable_on_Rp, "full column rank: globally identifiable on R^p")
    return {"rank": r.rank, "null": [[str(x) for x in v] for v in r.null_space]}


def check_parameter_domain_restriction():
    A = [[1, 1]]
    seg = analyze_affine_identifiability(A, observation=[2], parameter_domain=RationalBox(((0, 1), (1, 2))))
    require(seg.fibre_restriction_status == "exact" and seg.fibre_on_domain == (F(1), F(2)), f"segment t in [1,2], got {seg.fibre_on_domain}")
    point = analyze_affine_identifiability(A, observation=[2], parameter_domain=RationalBox(((0, 1), (0, 1))))
    require(point.fibre_on_domain == (F(1), F(1)) and any("single parameter point" in n for n in point.notes),
            "box [0,1]^2 leaves the single point (1,1): identified on this domain only")
    require(not point.globally_identifiable_on_Rp, "the R^p answer is unchanged by the domain statement")
    empty = analyze_affine_identifiability(A, observation=[5], parameter_domain=RationalBox(((0, 1), (0, 1))))
    require(empty.fibre_restriction_status == "empty", "observation 5 impossible on [0,1]^2")
    big = analyze_affine_identifiability([[1, 1, 1]], observation=[1], parameter_domain=RationalBox(((0, 1), (0, 1), (0, 1))))
    require(big.fibre_restriction_status == "not_evaluated", "2-D null space: restriction not evaluated, never assumed")
    require(raises(lambda: analyze_affine_identifiability([[1.0, 1.0]])), "float matrices are rejected (exactness)")
    return {"segment": [str(x) for x in seg.fibre_on_domain], "point": [str(x) for x in point.fibre_on_domain]}


def check_jc12_reservoir_known_and_unknown_initial_condition():
    r = reservoir_decay_report(2, 3, 5, 7)
    require(set(r.identifiable) == {"k", "c*x0"} and set(r.not_identifiable) == {"c", "x0"}, f"k and c*x0 only: {r}")
    w = r.witnesses[0]
    require(w["same_output"] and w["theta_prime"] == ("2", "3/7", "35"), f"lambda=7 witness (3/7, 35): {w}")
    require("y(0) = 15, y'(0) = -30, k = 2" in r.notes[0], f"control values: {r.notes[0]}")
    require("sum (= log of the product) identifiable: True, split identifiable: False" in r.notes[1], "log-affine cross-check")
    rc = reservoir_decay_report(2, 3, 5, 7, c_known=True)
    require(set(rc.identifiable) == {"k", "x0"} and not rc.not_identifiable, "c known removes the ambiguity")
    rx = reservoir_decay_report(2, 3, 5, 7, x0_known=True)
    require(set(rx.identifiable) == {"k", "c"} and not rx.not_identifiable and "c = y(0)/x0 = 3" in rx.notes[0],
            "known initial condition identifies c")
    require(raises(lambda: reservoir_decay_report(2, 0, 5, 7)), "zero signal excluded by positivity")
    require(raises(lambda: reservoir_decay_report(2, 3, 5, 7, c_known=True, x0_known=True)), "contradictory knowledge declaration")
    return {"identifiable": list(r.identifiable)}


def check_jc13_local_versus_global():
    r = square_map_report(4, 2)
    require(r.scope == "local" and r.witnesses[0]["fibre"] == ["-2", "2"] and r.witnesses[0]["derivative_at_theta_star"] == "4",
            f"fibre {{-2,2}}, derivative 4: {r.witnesses}")
    require("theta on R (global)" in r.not_identifiable and any("theta > 0" in s for s in r.identifiable), "global on R: no; on theta>0: yes")
    require(raises(lambda: square_map_report(4, 3)), "theta* must solve the equation")
    require(raises(lambda: square_map_report(0, 0)), "y = 0 (zero derivative) is outside this report")
    return {"fibre": r.witnesses[0]["fibre"]}


def check_numerical_full_rank_is_not_global_uniqueness():
    J = np.array([[2.0 * 2.0]])  # d(theta^2)/dtheta at theta = 2
    require(np.linalg.matrix_rank(J) == 1, "numerically full Jacobian rank at theta = 2")
    r = square_map_report(4, 2)
    require(r.not_identifiable == ("theta on R (global)",), "yet NOT globally identifiable on R: rank says local only")
    inv = parameter_scaling_invariance(1.5, 2.0, 7.0)
    log_aff = analyze_affine_identifiability([[1, 1]])  # (log sigma, log gamma) -> log(sigma*gamma)
    require(inv["invariant"] and log_aff.rank == 1 and is_identifiable_combination([[1, 1]], [1, 1]),
            "existing scaling example: only sigma*gamma identifiable, matching the exact log-affine analysis")
    return {"jacobian_rank": 1, "global": "not identifiable"}


def check_finite_candidate_fibre_is_not_a_real_line_statement():
    fib, rep = finite_candidate_fibre("y=theta^2", (-2, -1, 0, 1, 2), lambda t: t * t, 4)
    require(fib.fiber == (-2, 2) and rep.method == "finite_candidate_fibre", "listed fibre {-2, 2}")
    require(any("LISTED candidates only" in n for n in rep.notes), "must say: listed candidates only")
    fib2, rep2 = finite_candidate_fibre("y=theta^2", (0, 1, 2), lambda t: t * t, 4)
    require(fib2.fiber == (2,) and rep2.identifiable and "unique among the listed" in rep2.identifiable[0],
            "unique among a positive candidate list -- not a statement about R")
    return {"fibre": list(fib.fiber)}


def check_unsupported_outside_scope():
    r = unsupported_report("rational ODE x' = theta1 x^2 / (theta2 + x)", "general nonlinear ODE identifiability is not implemented (optional SIAN adapter)")
    require(r.scope == "unsupported" and r.method == "unsupported" and not r.identifiable and not r.not_identifiable,
            "outside the implemented scope: explicit 'unsupported', no claim either way")
    return {"status": r.scope}


CHECKS = [
    check_jc11_exact_affine_fibre,
    check_parameter_domain_restriction,
    check_jc12_reservoir_known_and_unknown_initial_condition,
    check_jc13_local_versus_global,
    check_numerical_full_rank_is_not_global_uniqueness,
    check_finite_candidate_fibre_is_not_a_real_line_statement,
    check_unsupported_outside_scope,
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
    out_path = Path(__file__).with_name("verify_structural_identifiability_results.json")
    out_path.write_text(json.dumps({"n_passed": n_passed, "n_total": len(CHECKS), "results": results}, indent=2, default=str))
    print(f"Report written to {out_path}")
    return 0 if n_passed == len(CHECKS) else 1


if __name__ == "__main__":
    raise SystemExit(main())
