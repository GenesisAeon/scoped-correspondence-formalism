#!/usr/bin/env python3
"""Hand-checkable verification for Floquet Multipliers (Milestone 34).

Checks (all numbers from this script run):
  1. Example A: tr=1.5, det=1 → |μ|=1 → classify = neutral
  2. Example B: tr=2.5, det=1 → μ={2, 0.5} → classify = unstable
  3. Edge:     tr=2,   det=1 → double μ=1 → classify = neutral (NOT stable)
  4. Char-poly vs numpy.linalg.eigvals cross-check on companion monodromy
  5. Source cites Floquet 1883 DOI; docstring / module is NOT M14;
     ScopeViolationError on non-2×2

JSON {count, passed, failed, report}; numbers from this run.
No ODE integrator. dynamics/core.py not imported/edited.
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

import numpy as np  # noqa: E402

from scoped_correspondence.dynamics.floquet import (  # noqa: E402
    SOURCE,
    SOURCE_OPTIONAL,
    STABILITY_NEUTRAL,
    STABILITY_STABLE,
    STABILITY_UNSTABLE,
    classify_orbital_stability,
    classify_orbital_stability_matrix,
    floquet_multipliers,
    has_nontrivial_jordan_block,
    monodromy_from_trace_det,
    multipliers_from_trace_det,
)
from scoped_correspondence.errors import ScopeViolationError  # noqa: E402


def require(ok, msg):
    if not bool(ok):
        raise AssertionError(msg)


def near(a, b, atol=1e-9, rtol=1e-9):
    if not math.isclose(float(a), float(b), abs_tol=atol, rel_tol=rtol):
        raise AssertionError(f"{a!r} != {b!r}")


def cnear(a, b, atol=1e-9):
    if abs(complex(a) - complex(b)) > atol:
        raise AssertionError(f"{a!r} != {b!r}")


def sorted_mu(arr):
    return sorted((complex(z) for z in arr), key=lambda z: (z.real, z.imag))


def check_example_a_neutral():
    """tr=1.5 det=1 → |μ|=1 → neutral."""
    tr, det = 1.5, 1.0
    M = monodromy_from_trace_det(tr, det)
    mu = floquet_multipliers(M)
    require(len(mu) == 2, "two multipliers")
    mods = [abs(complex(z)) for z in mu]
    for r in mods:
        near(r, 1.0, atol=1e-12)
    # Hand formula: (1.5 ± i sqrt(1.75)) / 2
    disc = tr * tr - 4.0 * det  # -1.75
    near(disc, -1.75)
    sqrt_abs = math.sqrt(1.75)
    expected = [
        complex(tr / 2.0, +sqrt_abs / 2.0),
        complex(tr / 2.0, -sqrt_abs / 2.0),
    ]
    got = sorted_mu(mu)
    exp = sorted_mu(expected)
    for a, b in zip(got, exp):
        cnear(a, b, atol=1e-12)
    label = classify_orbital_stability(mu)
    require(label == STABILITY_NEUTRAL, f"expected neutral, got {label!r}")
    require(label != STABILITY_STABLE, "must not be stable")
    return {
        "tr": tr,
        "det": det,
        "M": M.tolist(),
        "multipliers": [{"real": z.real, "imag": z.imag, "abs": abs(z)} for z in got],
        "abs_all_one": True,
        "classification": label,
        "hand_disc": disc,
        "hand_sqrt_1_75": sqrt_abs,
    }


def check_example_b_unstable():
    """tr=2.5 det=1 → μ={2, 0.5} → unstable."""
    tr, det = 2.5, 1.0
    M = monodromy_from_trace_det(tr, det)
    mu = floquet_multipliers(M)
    got = sorted_mu(mu)
    # Hand: sqrt(2.25)=1.5 → (2.5±1.5)/2 ∈ {2, 0.5}
    near(math.sqrt(tr * tr - 4.0 * det), 1.5)
    expected = [complex(0.5), complex(2.0)]
    exp = sorted_mu(expected)
    for a, b in zip(got, exp):
        cnear(a, b, atol=1e-12)
        near(a.imag, 0.0, atol=1e-12)
    label = classify_orbital_stability(mu)
    require(label == STABILITY_UNSTABLE, f"expected unstable, got {label!r}")
    mods = sorted(abs(complex(z)) for z in mu)
    near(mods[0], 0.5)
    near(mods[1], 2.0)
    return {
        "tr": tr,
        "det": det,
        "M": M.tolist(),
        "multipliers": [{"real": z.real, "imag": z.imag, "abs": abs(z)} for z in got],
        "expected": [0.5, 2.0],
        "classification": label,
    }


def check_edge_double_mu_one_not_stable():
    """tr=2 det=1 → double μ=1 → neutral, NOT stable."""
    tr, det = 2.0, 1.0
    M = monodromy_from_trace_det(tr, det)
    mu = floquet_multipliers(M)
    for z in mu:
        cnear(z, 1.0 + 0j, atol=1e-12)
        near(abs(complex(z)), 1.0, atol=1e-12)
    label = classify_orbital_stability(mu)
    require(label == STABILITY_NEUTRAL, f"expected neutral, got {label!r}")
    require(label != STABILITY_STABLE, "double μ=1 must NOT be classified stable")
    # Also direct classify on [1,1]
    label2 = classify_orbital_stability([1.0, 1.0])
    require(label2 == STABILITY_NEUTRAL, "direct [1,1] → neutral")
    return {
        "tr": tr,
        "det": det,
        "M": M.tolist(),
        "multipliers": [complex(z).real for z in mu],
        "classification": label,
        "not_stable": True,
        "direct_ones_classification": label2,
    }


def check_charpoly_vs_eigvals():
    """Char poly μ²−tr μ+det=0 agrees with numpy.linalg.eigvals."""
    cases = [
        (1.5, 1.0),
        (2.5, 1.0),
        (2.0, 1.0),
        (0.0, 1.0),
        (-1.0, 0.5),
        (0.5, 0.1),  # both |μ|<1 → stable
    ]
    rows = []
    for tr, det in cases:
        M = monodromy_from_trace_det(tr, det)
        mu_api = floquet_multipliers(M)
        mu_poly = multipliers_from_trace_det(tr, det)
        mu_eig = np.linalg.eigvals(M)
        a = sorted_mu(mu_api)
        b = sorted_mu(mu_poly)
        c = sorted_mu(mu_eig)
        for x, y, z in zip(a, b, c):
            cnear(x, y, atol=1e-10)
            cnear(x, z, atol=1e-10)
        label = classify_orbital_stability(mu_api)
        rows.append(
            {
                "tr": tr,
                "det": det,
                "mu": [{"real": z.real, "imag": z.imag, "abs": abs(z)} for z in a],
                "classification": label,
                "eigvals_agree": True,
            }
        )
    # Explicit stable case
    stable_row = [r for r in rows if r["tr"] == 0.5 and r["det"] == 0.1][0]
    require(stable_row["classification"] == STABILITY_STABLE, "0.5/0.1 → stable")
    return {"cases": rows, "stable_example_tr_det": [0.5, 0.1]}


def check_source_not_m14_and_scope():
    """SOURCE has Floquet DOI; module text is not M14; bad shape raises."""
    require("Floquet" in SOURCE, "Floquet in SOURCE")
    require("10.24033/asens.220" in SOURCE, "Floquet DOI")
    require("10.1137/120873960" in SOURCE_OPTIONAL, "Lessard optional DOI")
    # Module docstring / source must disambiguate from M14
    import scoped_correspondence.dynamics.floquet as floq

    doc = floq.__doc__ or ""
    doc_l = doc.lower()
    require(
        ("not m14" in doc_l) or ("not** m14" in doc_l) or ("plain: not m14" in doc_l),
        "docstring must say not M14",
    )
    require("M14" in doc, "M14 mentioned for disambiguation")
    require("Lohmiller" in doc or "contraction" in doc.lower(), "contraction disambiguation")
    # Scope: non-2x2
    raised = False
    try:
        floquet_multipliers([[1.0]])
    except ScopeViolationError:
        raised = True
    require(raised, "1x1 must raise ScopeViolationError")
    raised3 = False
    try:
        floquet_multipliers(np.eye(3))
    except ScopeViolationError:
        raised3 = True
    require(raised3, "3x3 must raise ScopeViolationError")
    # Empty multipliers
    raised_empty = False
    try:
        classify_orbital_stability([])
    except ScopeViolationError:
        raised_empty = True
    require(raised_empty, "empty multipliers raise")
    return {
        "SOURCE": SOURCE,
        "SOURCE_OPTIONAL": SOURCE_OPTIONAL,
        "doc_mentions_not_m14": True,
        "scope_1x1_raises": raised,
        "scope_3x3_raises": raised3,
        "empty_raises": raised_empty,
        "STABILITY_LABELS": [STABILITY_STABLE, STABILITY_UNSTABLE, STABILITY_NEUTRAL],
    }


def check_audit_a08_jordan_block():
    """Audit A08: M=[[1,1],[0,1]] has both mu=1 (repeated, unit modulus) but
    is a non-trivial Jordan block -- M^n grows without bound (M^100 has a
    100 off-diagonal), contradicting the "neutral"/bounded reading of a
    multipliers-only classification. classify_orbital_stability_matrix
    must catch this via has_nontrivial_jordan_block and report unstable;
    the plain multipliers-only classify_orbital_stability is unchanged
    (still conservatively "neutral", since it cannot see M at all).
    """
    M = [[1.0, 1.0], [0.0, 1.0]]
    mu = floquet_multipliers(M)
    for z in mu:
        cnear(z, 1.0 + 0j, atol=1e-9)
    old_label = classify_orbital_stability(mu)
    require(old_label == STABILITY_NEUTRAL, f"multipliers-only stays neutral, got {old_label!r}")
    require(has_nontrivial_jordan_block(M), "M=[[1,1],[0,1]] must be flagged as a Jordan block")
    new_label = classify_orbital_stability_matrix(M)
    require(new_label == STABILITY_UNSTABLE, f"matrix-aware must be unstable, got {new_label!r}")
    M100 = np.linalg.matrix_power(np.asarray(M), 100)
    near(M100[0, 1], 100.0, atol=1e-6)
    # A genuinely diagonalizable repeated eigenvalue (M=I) must NOT be flagged.
    require(not has_nontrivial_jordan_block([[1.0, 0.0], [0.0, 1.0]]), "identity is diagonalizable, not a Jordan block")
    identity_label = classify_orbital_stability_matrix([[1.0, 0.0], [0.0, 1.0]])
    require(identity_label == STABILITY_NEUTRAL, f"M=I stays neutral, got {identity_label!r}")
    return {
        "M": M,
        "multipliers_only_classification": old_label,
        "is_jordan_block": True,
        "matrix_aware_classification": new_label,
        "M_power_100_offdiag": M100[0, 1],
        "identity_case_is_jordan_block": False,
        "identity_case_classification": identity_label,
    }


def check_audit_a08_autonomous_phase_mode():
    """Audit A08: multipliers [1, 0.5] classify neutral by default (the mu=1
    is not annotated as anything special). With has_known_phase_mode=True,
    the trivial mu=1 (autonomous flow direction) is excluded and the
    remaining transverse multiplier (0.5) alone determines stability ->
    stable. Ambiguous or missing phase-mode candidates must raise.
    """
    default_label = classify_orbital_stability([1.0, 0.5])
    require(default_label == STABILITY_NEUTRAL, f"default stays neutral, got {default_label!r}")
    phase_label = classify_orbital_stability([1.0, 0.5], has_known_phase_mode=True)
    require(phase_label == STABILITY_STABLE, f"transverse-only must be stable, got {phase_label!r}")

    raised_none = False
    try:
        classify_orbital_stability([2.0, 0.5], has_known_phase_mode=True)
    except ScopeViolationError:
        raised_none = True
    require(raised_none, "no mu==1 candidate must raise under has_known_phase_mode=True")

    raised_ambiguous = False
    try:
        classify_orbital_stability([1.0, 1.0, 0.5], has_known_phase_mode=True)
    except ScopeViolationError:
        raised_ambiguous = True
    require(raised_ambiguous, "two mu==1 candidates must raise as ambiguous")

    return {
        "multipliers": [1.0, 0.5],
        "default_classification": default_label,
        "phase_mode_classification": phase_label,
        "no_candidate_raises": raised_none,
        "ambiguous_candidates_raise": raised_ambiguous,
    }


CHECKS = [
    ("example_a_neutral_tr15_det1", check_example_a_neutral),
    ("example_b_unstable_tr25_det1", check_example_b_unstable),
    ("edge_double_mu_one_not_stable", check_edge_double_mu_one_not_stable),
    ("charpoly_vs_numpy_eigvals", check_charpoly_vs_eigvals),
    ("source_not_m14_and_scope", check_source_not_m14_and_scope),
    ("audit_a08_jordan_block", check_audit_a08_jordan_block),
    ("audit_a08_autonomous_phase_mode", check_audit_a08_autonomous_phase_mode),
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--json-out",
        type=Path,
        default=Path(__file__).with_name("verify_floquet_core_results.json"),
    )
    args = parser.parse_args()

    report = {
        "milestone": "M34",
        "title": "Floquet Multipliers (given 2×2 monodromy)",
        "timestamp_local": dt.datetime.now().isoformat(timespec="seconds"),
        "platform": platform.platform(),
        "numpy_version": np.__version__,
        "SOURCE": SOURCE,
        "SOURCE_OPTIONAL": SOURCE_OPTIONAL,
        "NOT_M14": True,
        "no_ode_integrator": True,
        "checks": {},
    }
    errors = []
    passed = 0
    for name, fn in CHECKS:
        try:
            detail = fn()
            report["checks"][name] = {"status": "passed", "detail": detail}
            passed += 1
            print(f"PASS {name}")
        except Exception as exc:  # noqa: BLE001
            report["checks"][name] = {"status": "failed", "error": repr(exc)}
            errors.append(f"{name}: {exc!r}")
            print(f"FAIL {name}: {exc!r}")

    failed = len(CHECKS) - passed
    out = {
        "count": len(CHECKS),
        "passed": passed,
        "failed": failed,
        "errors": errors,
        "report": report,
    }
    args.json_out.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(f"\n{passed}/{len(CHECKS)} passed; wrote {args.json_out}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
