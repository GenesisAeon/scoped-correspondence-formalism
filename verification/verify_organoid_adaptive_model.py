"""ON3 verification (ORGANOID_NETWORK_ROADMAP.md, plan section 10/ON3):
bounded adaptive dynamics.

ON-C11 (Hebb row (5/12, 0, 1/12), all row sums 1/2), ON-C12 (eta = 0 keeps A;
contraction bound 3/4 at ell = gamma = 1/2, plus an empirical contraction
check for frozen weights), ON-C22 (row sum 4/5; inter weight 1/5 at c = 1/4),
ON-C23 (M = 1/2/3 with c = 1, 6/11, 8/11 give the identical matrix with
off-diagonals 4/55 -- and identical trajectories under different module
names); permanently forbidden inter edges, positive normalisation
denominators, budget kept, weights frozen during probe/test. No "trio wins"
acceptance condition.
"""
from __future__ import annotations

import json
import sys
from fractions import Fraction as F
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from scoped_correspondence.errors import ScopeViolationError
from scoped_correspondence.validation.modular_networks.adaptive_model import (
    NetworkConfig,
    adapt,
    budget_adjacency,
    contraction_bound,
    edge_mask,
    hebb_update,
    inter_fraction,
    input_matrix,
    simulate_trial,
)


def require(c, m=""):
    if not c:
        raise AssertionError(m)


def raises(fn, exc=ScopeViolationError):
    try:
        fn()
    except exc:
        return True
    return False


def check_on_c11_hebb_row():
    A = [[F(0), F(1, 2), F(0)], [F(1, 4), F(0), F(1, 4)], [F(0), F(1, 2), F(0)]]
    mask = [[int(i != j) for j in range(3)] for i in range(3)]
    A2 = hebb_update(A, [((1, 0, 0), (0, 1, 0))], mask, F(1, 2), F(1, 2))
    require(A2[1] == [F(5, 12), 0, F(1, 12)], f"row 2 must be (5/12, 0, 1/12), got {A2[1]}")
    require(all(sum(r) == F(1, 2) for r in A2), "every row sum stays gamma = 1/2")
    return {"row2": [str(x) for x in A2[1]]}


def check_on_c12_eta_zero_and_contraction():
    A, mod = budget_adjacency(12, 3, F(4, 5), F(1, 4))
    mask = edge_mask(12, mod)
    pairs = [((F(1, 3),) * 12, (F(1, 2),) * 12)]
    require(hebb_update(A, pairs, mask, F(0), F(4, 5)) == A, "eta = 0 preserves A exactly")
    require(contraction_bound(F(1, 2), F(1, 2)) == F(3, 4), "bound 3/4 at ell = gamma = 1/2")
    Af = np.array([[float(x) for x in r] for r in budget_adjacency(12, 3, 0.5, 0.25)[0]])
    B = input_matrix(12, (0, 4))
    u = np.array([1.0, 0.0])
    rng = np.random.default_rng(1)
    worst = 0.0
    for _ in range(50):
        x, z = rng.uniform(0, 1, 12), rng.uniform(0, 1, 12)
        F_ = lambda v: 0.5 * v + 0.5 * np.tanh(Af @ v + B @ u)
        worst = max(worst, np.max(np.abs(F_(x) - F_(z))) / np.max(np.abs(x - z)))
    require(worst <= 0.75 + 1e-12, f"empirical Lipschitz ratio {worst} must respect 3/4")
    require(raises(lambda: contraction_bound(0, F(1, 2))) and raises(lambda: hebb_update(A, pairs, mask, F(1), F(4, 5))), "domain checks")
    return {"bound": "3/4", "empirical_max_ratio": worst, "scope": "frozen weights, identical inputs only"}


def check_on_c22_budget():
    g = F(4, 5)
    for M in (1, 2, 3):
        A, mod = budget_adjacency(12, M, g, None if M == 1 else F(1, 4))
        require(all(sum(r) == g for r in A), f"M={M}: row sums 4/5")
        if M > 1:
            inter = [sum(A[i][j] for j in range(12) if mod[j] != mod[i]) for i in range(12)]
            require(all(x == F(1, 5) for x in inter), f"M={M}: inter weight 1/5 per row")
    require(raises(lambda: budget_adjacency(12, 1, g, F(1, 4))), "c is not applicable for M = 1")
    return {"row_sum": "4/5", "inter": "1/5"}


def check_on_c23_identical_operator_under_module_names():
    g = F(4, 5)
    A1, _ = budget_adjacency(12, 1, g)
    A2, _ = budget_adjacency(12, 2, g, F(6, 11))
    A3, _ = budget_adjacency(12, 3, g, F(8, 11))
    require(A1 == A2 == A3 and A1[0][1] == F(4, 55), "identical matrix, off-diagonals 4/55")
    Af = np.array([[float(x) for x in r] for r in A1])
    B = input_matrix(12, (0, 4))
    trajs = [simulate_trial(np.array([[float(x) for x in r] for r in A]), B, np.array([1.0, 0.0]), 0.5, 20) for A in (A1, A2, A3)]
    require(all(np.array_equal(trajs[0], t) for t in trajs), "identical trajectories: module names create no advantage")
    return {"off_diagonal": "4/55"}


def check_masks_budget_and_frozen_weights():
    A, mod = budget_adjacency(12, 3, 0.8, 0.25)
    mask = edge_mask(12, mod, allow_inter=False)
    A0 = np.array([[a * m for a, m in zip(r, mr)] for r, mr in zip(A, mask)])
    A0 = np.array([row * 0.8 / row.sum() for row in A0])
    cfg = NetworkConfig(12, 3, 0.8, 0.0, 0.5, (0, 4), (10, 11), 12, tuple(range(6, 13)), 0.3, allow_inter=False,
                        seeds={"adaptation": 3})
    B = input_matrix(12, (0, 4))
    A_ad, hist = adapt(A0, B, cfg, [np.array([1.0, 0.0]), np.array([0.0, 1.0])], np.random.default_rng(3), 20, mask)
    require(all(A_ad[i, j] == 0 for i in range(12) for j in range(12) if mod[i] != mod[j]), "forbidden inter edges stay zero permanently")
    require(all(A_ad[i, i] == 0 for i in range(12)), "no self-loops after adaptation")
    # exact one-step control: activity on ALL states, so the unmasked Hebb term is
    # positive on the diagonal and on the forbidden edge 0 <- 2
    A3 = [[F(0), F(1, 2), F(0)], [F(1, 4), F(0), F(1, 4)], [F(0), F(1, 2), F(0)]]
    m3 = [[0, 1, 0], [1, 0, 1], [0, 1, 0]]
    A3n = hebb_update(A3, [((1, 1, 1), (1, 1, 1))], m3, F(1, 2), F(1, 2))
    require(all(A3n[i][j] == 0 for i in range(3) for j in range(3) if not m3[i][j]), "masked entries stay exactly zero")
    require(A3n[1] == [F(1, 4), 0, F(1, 4)] and A3n[0] == [0, F(1, 2), 0], "masked exact step")
    require(np.allclose(A_ad.sum(axis=1), 0.8), "row budget gamma kept")
    require(all(all(f == 0 for f in h) for h in hist), "inter fraction reported after each update (0 here)")
    before = A_ad.copy()
    simulate_trial(A_ad, B, np.array([1.0, 0.0]), 0.5, 12)
    require(np.array_equal(before, A_ad), "probe/test simulation does not change A")
    with_inter = edge_mask(12, mod)
    A_i, hist_i = adapt(np.array(A, dtype=float), B, cfg, [np.array([1.0, 0.0]), np.array([0.0, 1.0])], np.random.default_rng(3), 20, with_inter)
    require(np.allclose(A_i.sum(axis=1), 0.8), "budget kept with inter edges allowed")
    require(len(hist_i) == 20 and all(len(h) == 12 and all(0 <= f <= 1 for f in h) for h in hist_i),
            "inter fraction reported per row after every update")
    drift = max(abs(f - 0.25) for f in hist_i[-1])
    return {"final_inter_fraction_rows_0_2": [round(x, 4) for x in hist_i[-1]][:3], "max_drift_from_c": drift,
            "note": "Hebb keeps row sums, not c; the drift is reported, not asserted in a direction"}


def check_review_hebb_input_domain():
    """Followup-Review §5.3: a caller-supplied mask with a 1 on the diagonal
    used to create self-loops; invalid masks, weights, activities and gamma
    are now refused (the model rule is unchanged)."""
    A = [[F(0), F(1, 2), F(0)], [F(1, 4), F(0), F(1, 4)], [F(0), F(1, 2), F(0)]]
    ok_mask = [[0, 1, 0], [1, 0, 1], [0, 1, 0]]
    act = [((1, 1, 1), (1, 1, 1))]
    diag_mask = [[1, 1, 0], [1, 0, 1], [0, 1, 0]]
    require(raises(lambda: hebb_update(A, act, diag_mask, F(1, 2), F(1, 2))), "diagonal 1 in the mask refused")
    require(raises(lambda: hebb_update(A, act, [[0, 2, 0], [1, 0, 1], [0, 1, 0]], F(1, 2), F(1, 2))), "mask values other than 0/1")
    require(raises(lambda: hebb_update(A, act, [[0, 1], [1, 0]], F(1, 2), F(1, 2))), "mask shape")
    require(raises(lambda: hebb_update(A, [((1, -1, 1), (1, 1, 1))], ok_mask, F(1, 2), F(1, 2))), "negative activity")
    require(raises(lambda: hebb_update(A, [((1, float("nan"), 1), (1, 1, 1))], ok_mask, F(1, 2), F(1, 2))), "non-finite activity")
    require(raises(lambda: hebb_update([[0, -1, 0], [1, 0, 1], [0, 1, 0]], act, ok_mask, F(1, 2), F(1, 2))), "negative weight")
    require(raises(lambda: hebb_update(A, act, ok_mask, F(1, 2), F(3, 2))), "gamma outside (0, 1)")
    require(hebb_update(A, act, ok_mask, F(1, 2), F(1, 2))[1] == [F(1, 4), 0, F(1, 4)], "valid call unchanged")
    return {"refusals": 7}


CHECKS = [check_on_c11_hebb_row, check_review_hebb_input_domain, check_on_c12_eta_zero_and_contraction, check_on_c22_budget,
          check_on_c23_identical_operator_under_module_names, check_masks_budget_and_frozen_weights]


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
    Path(__file__).with_name("verify_organoid_adaptive_model_results.json").write_text(
        json.dumps({"n_passed": n_passed, "n_total": len(CHECKS), "results": results}, indent=2, default=str), encoding="utf-8")
    return 0 if n_passed == len(CHECKS) else 1


if __name__ == "__main__":
    raise SystemExit(main())
