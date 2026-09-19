#!/usr/bin/env python3
"""Hand-checkable verification for Panarchy/Cusp extension (Milestone 35).

Checks (all numbers from this script run):
  1. a=3, b=0: fixed_points → 0, ±√3; fold_thresholds(3)=±2;
     CubicNormalForm(3,±2).discriminant()≈0 (CALL core, no reimplementation)
  2. hysteresis_sweep(3, b: -2→+2→-2): jumps at folds (±2), NOT at b=0
  3. Control: fixed b inside folds, vary a → no jump without fold crossing
  4. PANARCHY_V_ONSAGER_WARNING verbatim in module docstring AND JSON;
     sources cite Holling 1973 + Zwick 2017; no V≡Panarchy≡Onsager-L revival
  5. dynamics/core.py API used: fixed_points + CubicNormalForm.discriminant;
     fold closed form matches discriminant=0

Stdlib only (math). JSON {count, passed, failed, report}; numbers from this run.
Calls real fixed_points / discriminant (dynamics/core.py unchanged; CALL only).
"""
from __future__ import annotations

import argparse
import datetime as dt
import inspect
import json
import math
import platform
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from scoped_correspondence.dynamics.core import (  # noqa: E402
    CubicNormalForm,
    fixed_points,
)
from scoped_correspondence.dynamics import panarchy_cusp as pc  # noqa: E402
from scoped_correspondence.dynamics.panarchy_cusp import (  # noqa: E402
    PANARCHY_V_ONSAGER_WARNING,
    SOURCE,
    control_path_no_fold_crossing,
    fold_thresholds,
    hysteresis_sweep,
)
from scoped_correspondence.errors import ScopeViolationError  # noqa: E402


def require(ok, msg):
    if not bool(ok):
        raise AssertionError(msg)


def near(a, b, atol=1e-12, rtol=1e-9):
    if not math.isclose(float(a), float(b), abs_tol=atol, rel_tol=rtol):
        raise AssertionError(f"{a!r} != {b!r}")


def check_equilibria_and_folds():
    """a=3: equilibria 0,±√3 at b=0; folds ±2; discriminant CALL ≈0 at folds."""
    a = 3.0
    roots = fixed_points(a, 0.0)
    require(len(roots) == 3, f"expected 3 roots, got {roots!r}")
    near(roots[0], -math.sqrt(3.0))
    near(roots[1], 0.0)
    near(roots[2], math.sqrt(3.0))

    b_m, b_p = fold_thresholds(a)
    near(b_m, -2.0)
    near(b_p, 2.0)
    # Explicit formula ±√(4a³/27)
    mag = math.sqrt((4.0 * a**3) / 27.0)
    near(b_p, mag)
    near(abs(b_m), mag)

    # CALL CubicNormalForm.discriminant — must be ~0 at folds (no reimplementation)
    d_plus = CubicNormalForm(a, b_p).discriminant()
    d_minus = CubicNormalForm(a, b_m).discriminant()
    near(d_plus, 0.0, atol=1e-10)
    near(d_minus, 0.0, atol=1e-10)
    d_mid = CubicNormalForm(a, 0.0).discriminant()
    require(d_mid > 0.0, f"bistable interior discriminant should be >0; got {d_mid}")

    raised = False
    try:
        fold_thresholds(0.0)
    except ScopeViolationError:
        raised = True
    require(raised, "a<=0 must raise ScopeViolationError")

    return {
        "a": a,
        "equilibria_b0": [float(r) for r in roots],
        "expected_equilibria": [-math.sqrt(3.0), 0.0, math.sqrt(3.0)],
        "fold_minus": float(b_m),
        "fold_plus": float(b_p),
        "fold_formula_mag": float(mag),
        "discriminant_at_fold_plus": float(d_plus),
        "discriminant_at_fold_minus": float(d_minus),
        "discriminant_at_b0": float(d_mid),
        "uses_fixed_points_call": True,
        "uses_cubic_discriminant_call": True,
        "a_le_0_raises": raised,
        "note_research_slip_2_over_sqrt3": (
            "Research draft wrote folds ±2/√3≈±1.1547 for a=3 by dropping "
            "a^{3/2}=3√3 in (2/√27)a^{3/2}; correct fold_thresholds(3)=±2."
        ),
    }


def check_hysteresis_jumps_at_folds():
    """Sweep b -2→+2→-2 at a=3: jumps at folds, not at b=0."""
    a = 3.0
    # Dense path through -2 → +2 → -2
    forward = [ -2.0 + 4.0 * i / 40 for i in range(41) ]  # -2 .. +2
    backward = [ 2.0 - 4.0 * i / 40 for i in range(1, 41) ]  # +2 .. -2 (skip dup +2)
    b_values = forward + backward

    # Start on lower branch near left fold
    res = hysteresis_sweep(a, b_values, x0=-2.0)
    near(res.fold_minus, -2.0)
    near(res.fold_plus, 2.0)
    require(len(res.jump_indices) >= 1, f"expected ≥1 jump; got {res.jump_indices}")

    # All jump b-values must lie near a fold (|b|≈2), never near 0
    for jb in res.jump_b_values:
        dist_fold = min(abs(jb - 2.0), abs(jb + 2.0))
        require(
            dist_fold < 0.15,
            f"jump at b={jb} not near fold ±2 (dist_fold={dist_fold})",
        )
        require(abs(jb) > 1.0, f"jump at b={jb} suspiciously near 0")

    # Sample exactly at b=0 on both legs: no jumped flag
    zero_samples = [s for s in res.samples if abs(s.b) < 1e-12]
    require(len(zero_samples) >= 1, "expected samples at b≈0")
    for s in zero_samples:
        require(not s.jumped, f"unexpected jump flag at b=0: {s}")

    # Forward leg ends near upper branch after right-fold jump; return near lower
    # after left-fold jump (classic hysteresis).
    mid_forward = res.samples[20]  # near b=0 going up
    # After completing forward to +2 and starting back, x should be on upper
    # until left fold.
    xs_at_zero_fwd = [s.x for s in res.samples[:41] if abs(s.b) < 1e-9]
    xs_at_zero_back = [s.x for s in res.samples[41:] if abs(s.b) < 1e-9]
    require(xs_at_zero_fwd, "no b≈0 on forward leg")
    require(xs_at_zero_back, "no b≈0 on return leg")
    # Lower branch x<0 on forward (started low); upper x>0 on return
    require(xs_at_zero_fwd[0] < 0.0, f"forward at b=0 should be lower; got {xs_at_zero_fwd}")
    require(xs_at_zero_back[0] > 0.0, f"return at b=0 should be upper; got {xs_at_zero_back}")

    return {
        "a": a,
        "n_b_samples": len(b_values),
        "fold_minus": res.fold_minus,
        "fold_plus": res.fold_plus,
        "jump_indices": list(res.jump_indices),
        "jump_b_values": list(res.jump_b_values),
        "n_jumps": len(res.jump_indices),
        "x_at_b0_forward": float(xs_at_zero_fwd[0]),
        "x_at_b0_return": float(xs_at_zero_back[0]),
        "jumps_at_folds_not_at_b0": True,
        "mid_forward_b": float(mid_forward.b),
        "mid_forward_x": float(mid_forward.x),
        "mid_forward_jumped": bool(mid_forward.jumped),
    }


def check_control_no_jump_without_fold():
    """Fixed b inside folds while varying a — continuous, no jump."""
    b = 0.5
    # a from 4 down to 2.5: fold mag at a=2.5 is √(4*15.625/27)=√(62.5/27)≈1.52 > 0.5
    a_values = [4.0, 3.5, 3.0, 2.5]
    for aa in a_values:
        bm, bp = fold_thresholds(aa)
        require(bm < b < bp, f"b={b} not inside folds for a={aa}: ({bm},{bp})")

    out = control_path_no_fold_crossing(a_values, b, x0=None)
    require(out["any_jump"] is False, f"unexpected jump: {out}")
    require(out["fold_ok"] is True, "discriminants should stay positive")
    require(all(d > 0.0 for d in out["discriminants"]), "disc>0 required")
    # Path continuous: successive |Δx| small relative to √a
    xs = out["x_path"]
    for i in range(1, len(xs)):
        require(
            abs(xs[i] - xs[i - 1]) < 0.5,
            f"large step without fold: {xs[i-1]} → {xs[i]}",
        )

    return {
        "b_fixed": b,
        "a_values": a_values,
        "x_path": xs,
        "discriminants": out["discriminants"],
        "any_jump": out["any_jump"],
        "fold_ok": out["fold_ok"],
        "no_jump_without_fold_crossing": True,
    }


def check_warning_and_sources():
    """Verbatim fence in docstring + constant; sources; no hard-reject revival."""
    mod_doc = inspect.getdoc(pc) or ""
    require(
        PANARCHY_V_ONSAGER_WARNING in mod_doc
        or (
            "does NOT revive V≡Panarchy≡Onsager-L" in mod_doc
            and "interpretation layer only" in mod_doc
            and "Abstract-verified Zwick 2017 fulltext not seen" in mod_doc
        ),
        "module docstring missing mandatory fence text",
    )
    require(
        PANARCHY_V_ONSAGER_WARNING
        == (
            "does NOT revive V≡Panarchy≡Onsager-L; interpretation layer only, no proven "
            "ecological claim; Abstract-verified Zwick 2017 fulltext not seen."
        ),
        "PANARCHY_V_ONSAGER_WARNING constant drifted from verbatim mandate",
    )
    require("10.1146/annurev.es.04.110173.000245" in SOURCE, "Holling DOI missing")
    require("10.1145/3145574.3145591" in SOURCE, "Zwick DOI missing")
    require("Holling" in SOURCE, "Holling name missing")
    require("Zwick" in SOURCE, "Zwick name missing")
    # Hard-reject must not be asserted as identity
    bad = "V ≡ Panarchy ≡ Onsager-L is true"
    require(bad not in mod_doc, "must not revive discarded identity")
    require("does NOT revive" in PANARCHY_V_ONSAGER_WARNING, "fence polarity wrong")

    return {
        "PANARCHY_V_ONSAGER_WARNING": PANARCHY_V_ONSAGER_WARNING,
        "SOURCE": SOURCE,
        "warning_in_module_docstring": (
            "does NOT revive V≡Panarchy≡Onsager-L" in mod_doc
        ),
        "holling_doi": "10.1146/annurev.es.04.110173.000245",
        "zwick_doi": "10.1145/3145574.3145591",
        "fulltext_seen": False,
        "abstract_verified": True,
        "revives_V_Panarchy_Onsager_L": False,
    }


def check_core_call_only():
    """Confirm fold formula matches core discriminant zero-set; CALL path."""
    a = 3.0
    b_m, b_p = fold_thresholds(a)
    # Reconstruct |b| from solving CubicNormalForm.discriminant()==0 numerically
    # by checking sign change / zero — already done in check 1; here assert
    # source wiring: panarchy imports fixed_points + CubicNormalForm from core.
    src = inspect.getsource(pc)
    require("from scoped_correspondence.dynamics.core import" in src, "core import missing")
    require("fixed_points" in src, "fixed_points not referenced")
    require("CubicNormalForm" in src, "CubicNormalForm not referenced")
    require("def fixed_points" not in src, "must not reimplement fixed_points")
    # No local Cardano / acos root solver
    require("math.acos" not in src, "must not reimplement trig Cardano")
    require("_cbrt" not in src, "must not reimplement cube-root Cardano")

    # Spot-check: interior vs exterior region via core discriminant
    d_in = CubicNormalForm(a, 0.0).discriminant()
    d_out = CubicNormalForm(a, 3.0).discriminant()
    require(d_in > 0 and d_out < 0, f"region signs unexpected: in={d_in}, out={d_out}")
    n_in = len(fixed_points(a, 0.0))
    n_out = len(fixed_points(a, 3.0))
    require(n_in == 3 and n_out == 1, f"root counts: in={n_in}, out={n_out}")

    return {
        "fold_minus": b_m,
        "fold_plus": b_p,
        "discriminant_interior_b0": float(d_in),
        "discriminant_exterior_b3": float(d_out),
        "n_roots_interior": n_in,
        "n_roots_exterior": n_out,
        "reimplements_fixed_points": False,
        "calls_core_discriminant": True,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--json-out",
        type=Path,
        default=Path(__file__).with_name("verify_panarchy_cusp_core_results.json"),
    )
    args = parser.parse_args()

    checks = [
        ("equilibria_and_folds", check_equilibria_and_folds),
        ("hysteresis_jumps_at_folds", check_hysteresis_jumps_at_folds),
        ("control_no_jump_without_fold", check_control_no_jump_without_fold),
        ("warning_and_sources", check_warning_and_sources),
        ("core_call_only", check_core_call_only),
    ]
    report = {
        "milestone": "M35",
        "title": "Panarchy / Adaptive-Cycle as Cusp Extension",
        "timestamp_local": dt.datetime.now().isoformat(timespec="seconds"),
        "platform": platform.platform(),
        "python": sys.version,
        "PANARCHY_V_ONSAGER_WARNING": PANARCHY_V_ONSAGER_WARNING,
        "SOURCE": SOURCE,
        "checks": {},
    }
    passed = 0
    failed = 0
    failures = []
    for name, fn in checks:
        try:
            report["checks"][name] = {"ok": True, "data": fn()}
            passed += 1
            print(f"PASS  {name}")
        except Exception as exc:  # noqa: BLE001 — collect all failures
            failed += 1
            failures.append(name)
            report["checks"][name] = {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
            print(f"FAIL  {name}: {exc}")

    out = {
        "count": len(checks),
        "passed": passed,
        "failed": failed,
        "failures": failures,
        "report": report,
    }
    args.json_out.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote {args.json_out}  ({passed}/{len(checks)} passed)")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
