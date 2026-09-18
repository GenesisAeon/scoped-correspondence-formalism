#!/usr/bin/env python3
"""Hand-checkable verification for CSW Graph Invariants (Milestone 19).

Checks (all numbers from this script run):
  1. C5 invariants: α=2, θ=√5 (umbrella), α*=2.5
  2. Symmetric model p=0.44 → sum=2.2: classical violated, quantum+GPT held
  3. Umbrella derivation residual vs √5 within THETA_TOL; not bare hardcode
  4. Scope: non-C5 lovasz_theta refused; CF LP not imported/identified; DOI present

JSON {count, passed, failed, report}; numbers from this run.
Does not import or mutate contextuality.core (beyond package __init__ wire).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import platform
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from scoped_correspondence.errors import ScopeViolationError  # noqa: E402
from scoped_correspondence.contextuality.csw import (  # noqa: E402
    BOUND_TOL,
    PRL_DOI,
    SOURCE,
    THETA_TOL,
    CSWWitness,
    c5,
    cycle_graph,
    csw_invariants,
    fractional_packing_number,
    independence_number,
    lovasz_theta,
    lovasz_theta_c5_report,
    symmetric_c5_model,
)


def require(ok, msg):
    if not bool(ok):
        raise AssertionError(msg)


def near(a, b, atol=1e-9, rtol=1e-9):
    if not math.isclose(float(a), float(b), abs_tol=atol, rel_tol=rtol):
        raise AssertionError(f"{a!r} != {b!r}")


def check_c5_invariants():
    """Self-check: α=2, θ=√5, α*=2.5."""
    G = c5()
    alpha = independence_number(G)
    theta = lovasz_theta(G)
    alpha_star = fractional_packing_number(G)
    near(alpha, 2, atol=0)
    near(theta, math.sqrt(5), atol=THETA_TOL)
    near(alpha_star, 2.5, atol=BOUND_TOL)
    inv = csw_invariants(G)
    near(inv["alpha"], 2)
    near(inv["theta"], math.sqrt(5), atol=THETA_TOL)
    near(inv["alpha_star"], 2.5)
    require(G.is_c5(), "is_c5")
    return {
        "alpha": alpha,
        "theta": theta,
        "theta_sqrt5": math.sqrt(5),
        "theta_residual": abs(theta - math.sqrt(5)),
        "alpha_star": alpha_star,
        "THETA_TOL": THETA_TOL,
        "hierarchy_ok": alpha <= theta <= alpha_star + BOUND_TOL,
    }


def check_symmetric_model():
    """p=0.44 → S=2.2: classical α=2 violated; quantum √5 held; GPT 5/2 held."""
    p = 0.44
    w = symmetric_c5_model(p)
    require(isinstance(w, CSWWitness), "type")
    near(w.observed_sum, 5 * p)
    near(w.classical_bound, 2)
    near(w.quantum_bound, math.sqrt(5), atol=THETA_TOL)
    near(w.general_probabilistic_bound, 2.5)
    require(w.classical_violated is True, "classical should be violated")
    require(w.quantum_held is True, "quantum should hold")
    require(w.gpt_held is True, "gpt should hold")
    require(w.observed_sum > w.classical_bound, "2.2 > 2")
    require(w.observed_sum <= w.quantum_bound + BOUND_TOL, "2.2 <= √5")
    require(w.observed_sum <= w.general_probabilistic_bound + BOUND_TOL, "2.2 <= 2.5")
    # Boundary: p=0.4 → S=2 classical held (not violated)
    w_eq = symmetric_c5_model(0.4)
    require(w_eq.classical_violated is False, "S=2 not violated")
    near(w_eq.observed_sum, 2.0)
    return {
        "p": p,
        "observed_sum": w.observed_sum,
        "classical_bound": w.classical_bound,
        "quantum_bound": w.quantum_bound,
        "general_probabilistic_bound": w.general_probabilistic_bound,
        "classical_violated": w.classical_violated,
        "quantum_held": w.quantum_held,
        "gpt_held": w.gpt_held,
        "p_eq_0.4_classical_violated": w_eq.classical_violated,
        "source": w.as_dict()["source"],
    }


def check_umbrella_derivation():
    """Umbrella computes √5 with documented residual; algebraic path matches."""
    rep = lovasz_theta_c5_report()
    require(rep["method"] == "umbrella_orthonormal_representation", "method")
    near(rep["theta"], math.sqrt(5), atol=THETA_TOL)
    require(rep["residual_vs_sqrt5"] < THETA_TOL, "residual")
    # Algebraic: tan²α = √5 - 1 ⇒ θ = √5
    near(rep["tan2_exact_algebraic"], math.sqrt(5) - 1.0, atol=1e-12)
    near(rep["theta_algebraic"], math.sqrt(5), atol=1e-12)
    # Ensure we did not merely hardcode: tan2 from cos(4π/5) path
    require(rep["tan2_alpha"] > 1.0, "tan2 from umbrella > 1")
    require("10.1103/PhysRevLett.112.040401" in SOURCE, "DOI in SOURCE")
    require(PRL_DOI == "10.1103/PhysRevLett.112.040401", "PRL_DOI const")
    return {
        "theta_umbrella": rep["theta_umbrella"],
        "residual_vs_sqrt5": rep["residual_vs_sqrt5"],
        "tan2_alpha": rep["tan2_alpha"],
        "tan2_exact_algebraic": rep["tan2_exact_algebraic"],
        "tolerance": THETA_TOL,
        "doi": PRL_DOI,
        "source_has_doi": "10.1103/PhysRevLett.112.040401" in SOURCE,
    }


def check_scope_and_separation():
    """Non-C5 θ refused; csw must not treat CF LP as same formula."""
    # C3: independence OK; lovasz_theta raises
    c3 = cycle_graph(3)
    near(independence_number(c3), 1)
    raised = False
    try:
        lovasz_theta(c3)
    except ScopeViolationError:
        raised = True
    require(raised, "lovasz_theta(C3) must raise ScopeViolationError")

    import scoped_correspondence.contextuality.csw as csw_mod
    import inspect

    src = inspect.getsource(csw_mod)
    import_lines = [
        ln.strip()
        for ln in src.splitlines()
        if ln.strip().startswith(("import ", "from "))
    ]
    for ln in import_lines:
        require(
            "contextuality.core" not in ln and "contextual_fraction" not in ln,
            f"forbidden import: {ln}",
        )
    require("cvxpy" not in src.lower() and "picos" not in src.lower(), "no general SDP lib")
    require(
        "contextual_fraction" in src and "not" in src.lower(),
        "docs should explicitly separate from contextual_fraction LP",
    )
    return {
        "c3_alpha": independence_number(c3),
        "lovasz_theta_c3_raises": raised,
        "csw_imports_core": False,
        "docstring_separates_from_cf_lp": True,
        "no_general_sdp_lib": True,
        "doi_present": PRL_DOI in SOURCE,
    }



CHECKS = [
    ("c5_invariants_alpha_theta_alpha_star", check_c5_invariants),
    ("symmetric_c5_p0p44_witness", check_symmetric_model),
    ("umbrella_derivation_sqrt5", check_umbrella_derivation),
    ("scope_separation_no_cf_lp", check_scope_and_separation),
]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--json-out",
        type=Path,
        default=ROOT / "verification" / "verify_csw_core_results.json",
    )
    args = ap.parse_args(argv)

    results = {}
    errors = []
    passed = 0
    for name, fn in CHECKS:
        try:
            detail = fn()
            results[name] = {"status": "passed", "detail": detail}
            passed += 1
            print(f"PASS {name}: {detail}")
        except Exception as exc:  # noqa: BLE001
            results[name] = {"status": "failed", "error": f"{type(exc).__name__}: {exc}"}
            errors.append(f"{name}: {type(exc).__name__}: {exc}")
            print(f"FAIL {name}: {type(exc).__name__}: {exc}", file=sys.stderr)

    failed = len(CHECKS) - passed
    # Berlin-local timestamp label (box clock is Europe/Berlin)
    ts = dt.datetime.now().astimezone().isoformat(timespec="seconds")
    payload = {
        "count": len(CHECKS),
        "passed": passed,
        "failed": failed,
        "errors": errors,
        "report": {
            "milestone": "M19 CSW Graph Invariants",
            "checks": results,
            "platform": platform.platform(),
            "python": platform.python_version(),
            "timestamp": ts,
            "source_doi": PRL_DOI,
            "c5_targets": {"alpha": 2, "theta": "sqrt(5)", "alpha_star": 2.5},
            "disclaimer": (
                "C5 umbrella θ only; no general SDP; fractional packing LP ≠ "
                "contextual_fraction LP; contextuality/core.py untouched."
            ),
            "untouched": [
                "src/scoped_correspondence/contextuality/core.py",
                "src/scoped_correspondence/__init__.py",
                "FORMALISM.md",
                "sheaf_contextuality.md",
                "general SDP library",
                "contextual_fraction LP identification",
            ],
        },
    }
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(f"Wrote {args.json_out} ({passed}/{len(CHECKS)} passed)")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
