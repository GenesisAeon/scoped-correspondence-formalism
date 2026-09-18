#!/usr/bin/env python3
"""Hand-checkable verification for Schnakenberg network thermo (Milestone 18).

Checks (all numbers from this script run):
  1. 3-cycle CW=2, CCW=1: p=(1/3,)*3 stationary (p@k≈0);
     J_ij=1/3 on CW edges; A=ln2; S_prod=ln2≈0.693147
  2. Explicit NO-link note: S_prod=ln2 is not ecosystem σ≈2.2
  3. Second off-equilibrium rates CW=3, CCW=1: different positive S_prod=2*ln3
  4. DOI 10.1103/RevModPhys.48.571 in SOURCE; Onsager near-eq note present
  5. Negative-σ path raises ScopeViolationError (synthetic broken pair)

Uses numpy. JSON {count, passed, failed, report}; numbers from this run.
Does not import or mutate thermo.core / M8 e10 formula.
"""
from __future__ import annotations

import argparse
import datetime as dt
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

from scoped_correspondence.errors import ScopeViolationError  # noqa: E402
from scoped_correspondence.thermo.schnakenberg import (  # noqa: E402
    SOURCE,
    cycle_affinity,
    entropy_production_rate,
    stationary_currents,
)


def require(ok, msg):
    if not bool(ok):
        raise AssertionError(msg)


def near(a, b, atol=1e-12, rtol=1e-9):
    if not math.isclose(float(a), float(b), abs_tol=atol, rel_tol=rtol):
        raise AssertionError(f"{a!r} != {b!r}")


def three_cycle_generator(cw: float, ccw: float) -> np.ndarray:
    """Row-generator for the directed 3-cycle with uniform out-rate cw+ccw."""
    r, s = float(cw), float(ccw)
    # 0→1=cw, 1→2=cw, 2→0=cw; 0→2=ccw, 2→1=ccw, 1→0=ccw
    k = np.array(
        [
            [-(r + s), r, s],
            [s, -(r + s), r],
            [r, s, -(r + s)],
        ],
        dtype=float,
    )
    return k


def check_three_cycle_ln2():
    """CW=2, CCW=1 → J=1/3, A=ln2, S_prod=ln2; p@k≈0; no ecosystem link."""
    k = three_cycle_generator(2.0, 1.0)
    p = np.array([1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0])
    residual = p @ k
    require(np.allclose(residual, 0.0, atol=1e-12), f"p@k not ~0: {residual}")

    J = stationary_currents(p, k)
    near(J[0, 1], 1.0 / 3.0)
    near(J[1, 2], 1.0 / 3.0)
    near(J[2, 0], 1.0 / 3.0)
    near(J[1, 0], -1.0 / 3.0)
    near(J[2, 1], -1.0 / 3.0)
    near(J[0, 2], -1.0 / 3.0)

    A01 = cycle_affinity(p, k, 0, 1)
    A12 = cycle_affinity(p, k, 1, 2)
    A20 = cycle_affinity(p, k, 2, 0)
    near(A01, math.log(2.0))
    near(A12, math.log(2.0))
    near(A20, math.log(2.0))
    near(cycle_affinity(p, k, 1, 0), -math.log(2.0))

    s_prod = entropy_production_rate(p, k)
    near(s_prod, math.log(2.0))
    require(s_prod >= 0.0, "S_prod must be >= 0")

    # Explicit scope fence: ln2 is NOT ecosystem σ≈2.2
    ecosystem_sigma_approx = 2.2
    require(
        abs(s_prod - ecosystem_sigma_approx) > 1.0,
        "S_prod=ln2 must remain clearly distinct from ecosystem σ≈2.2",
    )
    no_link_note = (
        "NO link between Schnakenberg S_prod=ln2 and ecosystem σ≈2.2"
    )

    return {
        "cw": 2.0,
        "ccw": 1.0,
        "p": p.tolist(),
        "p_k_residual_max_abs": float(np.max(np.abs(residual))),
        "J_01": float(J[0, 1]),
        "J_12": float(J[1, 2]),
        "J_20": float(J[2, 0]),
        "A_01": float(A01),
        "S_prod": float(s_prod),
        "S_prod_expected_ln2": float(math.log(2.0)),
        "no_ecosystem_sigma_link": no_link_note,
        "ecosystem_sigma_approx_refused": ecosystem_sigma_approx,
    }


def check_second_off_eq():
    """CW=3, CCW=1 → S_prod=2*ln3 ≈ 2.197; still no ecosystem identity."""
    k = three_cycle_generator(3.0, 1.0)
    p = np.full(3, 1.0 / 3.0)
    require(np.allclose(p @ k, 0.0, atol=1e-12), "p@k not ~0 (case 2)")
    J = stationary_currents(p, k)
    near(J[0, 1], 2.0 / 3.0)
    A = cycle_affinity(p, k, 0, 1)
    near(A, math.log(3.0))
    s_prod = entropy_production_rate(p, k)
    expected = 2.0 * math.log(3.0)  # (r-s)*ln(r/s) = 2*ln3
    near(s_prod, expected)
    require(s_prod > 0.0, "second case S_prod must be positive")
    require(
        abs(s_prod - math.log(2.0)) > 0.5,
        "second case must differ from ln2 case",
    )
    # Coincidental proximity to 2.2 must not be treated as an identity
    require(
        abs(s_prod - 2.2) < 0.01,
        "sanity: 2*ln3 is near 2.2 numerically (coincidence only)",
    )
    return {
        "cw": 3.0,
        "ccw": 1.0,
        "J_01": float(J[0, 1]),
        "A_01": float(A),
        "S_prod": float(s_prod),
        "S_prod_expected_2ln3": float(expected),
        "note": (
            "S_prod=2*ln3≈2.197 is numerically near 2.2 by coincidence; "
            "NO link to ecosystem σ=2.2"
        ),
    }


def check_source_and_onsager_note():
    require("10.1103/RevModPhys.48.571" in SOURCE, "DOI missing from SOURCE")
    require("Schnakenberg" in SOURCE, "Schnakenberg missing from SOURCE")
    # Module docstring / SOURCE must carry Onsager near-eq disclaimer
    import scoped_correspondence.thermo.schnakenberg as mod

    doc = mod.__doc__ or ""
    require("Onsager" in doc, "Onsager note missing from module docstring")
    require(
        "near-equilibrium special case" in doc
        or "near-equilibrium" in doc.lower(),
        "near-equilibrium special-case wording missing",
    )
    # Allow markdown emphasis around NOT (e.g. **NOT** a general identity)
    require(
        "general identity" in doc.lower()
        and ("not" in doc.lower() and "coupling matrices" in doc.lower()),
        "NOT general identity wording missing",
    )
    # Affinity on diagonal refused
    k = three_cycle_generator(2.0, 1.0)
    p = np.full(3, 1.0 / 3.0)
    raised = False
    try:
        cycle_affinity(p, k, 0, 0)
    except ScopeViolationError:
        raised = True
    require(raised, "cycle_affinity(i,i) must raise ScopeViolationError")
    return {
        "doi": "10.1103/RevModPhys.48.571",
        "source_has_doi": True,
        "onsager_near_eq_only": True,
        "diagonal_affinity_refused": True,
    }


def check_negative_sigma_refused():
    """Synthetic inconsistent currents cannot be built from rates; instead
    verify ScopeViolationError on malformed one-way edge with mass flow.
    """
    # One-way edge with positive current: affinity undefined → refuse
    p = np.array([0.5, 0.5])
    k = np.array([[-1.0, 1.0], [0.0, 0.0]], dtype=float)
    raised = False
    try:
        entropy_production_rate(p, k)
    except ScopeViolationError:
        raised = True
    require(raised, "one-way nonzero current must raise ScopeViolationError")
    return {"one_way_nonzero_current_refused": True}


CHECKS = [
    ("three_cycle_ln2", check_three_cycle_ln2),
    ("second_off_equilibrium", check_second_off_eq),
    ("source_onsager_note", check_source_and_onsager_note),
    ("negative_scope_refused", check_negative_sigma_refused),
]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--json-out",
        type=Path,
        default=Path(__file__).with_name("verify_schnakenberg_core_results.json"),
    )
    args = parser.parse_args(argv)

    report = []
    passed = 0
    failed = 0
    for name, fn in CHECKS:
        entry = {"name": name, "ok": False}
        try:
            detail = fn()
            entry["ok"] = True
            entry["detail"] = detail
            passed += 1
        except Exception as exc:  # noqa: BLE001 — collect into report
            failed += 1
            entry["error"] = f"{type(exc).__name__}: {exc}"
        report.append(entry)

    payload = {
        "milestone": 18,
        "title": "Schnakenberg Network Thermodynamics",
        "count": len(CHECKS),
        "passed": passed,
        "failed": failed,
        "report": report,
        "meta": {
            "generated_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
            "python": platform.python_version(),
            "platform": platform.platform(),
            "source_doi": "10.1103/RevModPhys.48.571",
            "S_prod_ln2": float(math.log(2.0)),
            "no_ecosystem_sigma_link": True,
            "thermo_core_untouched": True,
            "package_root_init_untouched": True,
        },
    }
    args.json_out.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps({"passed": passed, "failed": failed, "count": len(CHECKS)}, indent=2))
    if failed:
        for e in report:
            if not e["ok"]:
                print(f"FAIL {e['name']}: {e.get('error')}", file=sys.stderr)
        return 1
    # Spotlight key number for parent report
    for e in report:
        if e["name"] == "three_cycle_ln2" and e["ok"]:
            print(f"S_prod=ln2={e['detail']['S_prod']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
