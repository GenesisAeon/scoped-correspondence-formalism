#!/usr/bin/env python3
"""Hand-checkable verification for Nagumo tangent cone (Milestone 28).

Checks (all numbers from this script run):
  1. Box K=[-1,1]^2, A_sys=[[-1,0.5],[-0.5,-1]]: all 4 edges (>=20 pts)
     + 4 corners satisfy Nagumo; corner f-vectors match ticket.
  2. Negative: A_sys that violates corner (1,1) → ok=False.
  3. active_constraints / DOI / non-replace-M16 docstring signal.

Stdlib + numpy. JSON {count, passed, failed, report}; numbers from this run.
Does not import or mutate viability.core / control_barrier.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import platform
import sys
from pathlib import Path
from typing import Callable, List, Sequence, Tuple

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from scoped_correspondence.viability.nagumo import (  # noqa: E402
    SOURCE,
    active_constraints,
    tangent_cone_condition,
    verify_polyhedral_viability,
)


def require(ok, msg):
    if not bool(ok):
        raise AssertionError(msg)


def near(a, b, atol=1e-12, rtol=1e-9):
    if not math.isclose(float(a), float(b), abs_tol=atol, rel_tol=rtol):
        raise AssertionError(f"{a!r} != {b!r}")


# Box K = [-1,1]^2 as A z <= b:
#   z1 <= 1,  -z1 <= 1,  z2 <= 1,  -z2 <= 1
A_BOX = np.array(
    [
        [1.0, 0.0],
        [-1.0, 0.0],
        [0.0, 1.0],
        [0.0, -1.0],
    ],
    dtype=float,
)
B_BOX = np.array([1.0, 1.0, 1.0, 1.0], dtype=float)

A_SYS_GOOD = np.array([[-1.0, 0.5], [-0.5, -1.0]], dtype=float)
# Outward-pointing linear field: violates corner (1,1)
A_SYS_BAD = np.array([[1.0, 0.0], [0.0, 1.0]], dtype=float)

N_EDGE = 21  # >= 20 points per edge (inclusive endpoints share corners)


def make_f(A_sys: np.ndarray) -> Callable[[Sequence[float]], List[float]]:
    A = np.asarray(A_sys, dtype=float)

    def f(z: Sequence[float]) -> List[float]:
        return (A @ np.asarray(z, dtype=float)).tolist()

    return f


def edge_samples(edge: str, n: int = N_EDGE) -> List[List[float]]:
    """Uniform samples on one edge of [-1,1]^2 (including endpoints)."""
    ts = np.linspace(-1.0, 1.0, n)
    pts: List[List[float]] = []
    for t in ts:
        t = float(t)
        if edge == "z1=+1":
            pts.append([1.0, t])
        elif edge == "z1=-1":
            pts.append([-1.0, t])
        elif edge == "z2=+1":
            pts.append([t, 1.0])
        elif edge == "z2=-1":
            pts.append([t, -1.0])
        else:
            raise ValueError(edge)
    return pts


CORNERS: List[Tuple[str, List[float], List[float]]] = [
    # name, z, expected f under A_SYS_GOOD
    ("(1,1)", [1.0, 1.0], [-0.5, -1.5]),
    ("(1,-1)", [1.0, -1.0], [-1.5, 0.5]),
    ("(-1,1)", [-1.0, 1.0], [1.5, -0.5]),
    ("(-1,-1)", [-1.0, -1.0], [0.5, 1.5]),
]


def check_edges_and_corners():
    """Ticket example: A_sys good → all 4 edges + 4 corners ok."""
    f = make_f(A_SYS_GOOD)
    edge_names = ["z1=+1", "z1=-1", "z2=+1", "z2=-1"]
    edge_reports = {}
    all_samples: List[List[float]] = []

    for name in edge_names:
        samples = edge_samples(name, N_EDGE)
        require(len(samples) >= 20, f"{name}: need >=20 pts, got {len(samples)}")
        report = verify_polyhedral_viability(A_BOX, B_BOX, f, samples)
        require(report["ok"] is True, f"edge {name} failed: {report}")
        # Spot-check ticket formula on z1=+1: f1 = -1 + 0.5*z2 in [-1.5, -0.5]
        if name == "z1=+1":
            f1_vals = [float(f(z)[0]) for z in samples]
            require(min(f1_vals) >= -1.5 - 1e-12, f1_vals)
            require(max(f1_vals) <= -0.5 + 1e-12, f1_vals)
            require(all(v <= 1e-12 for v in f1_vals), f1_vals)
        edge_reports[name] = {
            "n_samples": report["n_samples"],
            "ok": report["ok"],
            "n_failed": report["n_failed"],
            "f1_range_on_z1_eq_1": (
                [min(f1_vals), max(f1_vals)] if name == "z1=+1" else None
            ),
        }
        all_samples.extend(samples)

    corner_reports = {}
    for cname, z, f_expected in CORNERS:
        f_z = f(z)
        near(f_z[0], f_expected[0])
        near(f_z[1], f_expected[1])
        detail = tangent_cone_condition(z, f_z, A_BOX, B_BOX)
        require(detail["ok"] is True, f"corner {cname}: {detail}")
        require(len(detail["active_indices"]) == 2, detail["active_indices"])
        require(all(m <= 1e-12 for m in detail["margins"]), detail["margins"])
        corner_reports[cname] = {
            "z": z,
            "f_z": f_z,
            "f_expected": f_expected,
            "ok": detail["ok"],
            "margins": detail["margins"],
            "active_indices": detail["active_indices"],
        }

    # Combined sweep (dedupe not required — verify just needs samples)
    combined = verify_polyhedral_viability(A_BOX, B_BOX, f, all_samples)
    require(combined["ok"] is True, combined)

    return {
        "A_sys": A_SYS_GOOD.tolist(),
        "K": "[-1,1]^2",
        "A_box": A_BOX.tolist(),
        "b_box": B_BOX.tolist(),
        "n_per_edge": N_EDGE,
        "edges": edge_reports,
        "corners": corner_reports,
        "combined_ok": combined["ok"],
        "combined_n_samples": combined["n_samples"],
        "source": SOURCE,
    }


def check_negative_corner_violation():
    """Construct A_sys that violates corner (1,1) → ok=False."""
    f_bad = make_f(A_SYS_BAD)
    z = [1.0, 1.0]
    f_z = f_bad(z)
    near(f_z[0], 1.0)
    near(f_z[1], 1.0)
    detail = tangent_cone_condition(z, f_z, A_BOX, B_BOX)
    require(detail["ok"] is False, f"expected violation at (1,1): {detail}")
    require(any(m > 0 for m in detail["margins"]), detail["margins"])

    # Good A_sys still ok at same corner (control)
    f_good = make_f(A_SYS_GOOD)
    detail_good = tangent_cone_condition(z, f_good(z), A_BOX, B_BOX)
    require(detail_good["ok"] is True, detail_good)

    # verify_polyhedral_viability on just this corner
    report = verify_polyhedral_viability(A_BOX, B_BOX, f_bad, [z])
    require(report["ok"] is False, report)
    require(report["n_failed"] == 1, report)

    return {
        "A_sys_bad": A_SYS_BAD.tolist(),
        "corner": z,
        "f_z": f_z,
        "ok": detail["ok"],
        "margins": detail["margins"],
        "active_indices": detail["active_indices"],
        "verify_ok": report["ok"],
        "n_failed": report["n_failed"],
        "good_A_sys_still_ok_at_same_corner": detail_good["ok"],
    }


def check_active_constraints_and_source():
    """Unit checks for active set + provenance / non-replace-M16."""
    # Interior: no active
    require(active_constraints([0.0, 0.0], A_BOX, B_BOX) == [], "interior")
    # Edge z1=1: index 0 only
    require(active_constraints([1.0, 0.0], A_BOX, B_BOX) == [0], "edge z1=1")
    # Corner (1,1): indices 0 and 2
    require(active_constraints([1.0, 1.0], A_BOX, B_BOX) == [0, 2], "corner")

    require("10.11429/ppmsj1919.24.0_551" in SOURCE, SOURCE)
    require("Nagumo" in SOURCE, SOURCE)

    # Docstring / module signal: different case class, not a replacement for M16
    import scoped_correspondence.viability.nagumo as nagumo_mod

    doc = nagumo_mod.__doc__ or ""
    require("non-smooth" in doc.lower() or "non-smooth" in doc, doc[:200])
    require("not a replacement" in doc.lower() or "different case class" in doc.lower(), doc)
    require("M16" in doc, "doc must mention M16")

    # Vacuous interior point via tangent_cone_condition
    interior = tangent_cone_condition([0.0, 0.0], [1.0, 1.0], A_BOX, B_BOX)
    require(interior["ok"] is True, interior)
    require(interior["active_indices"] == [], interior)

    return {
        "interior_active": [],
        "edge_z1_eq_1_active": [0],
        "corner_11_active": [0, 2],
        "source_has_doi": True,
        "doc_mentions_non_smooth_and_not_replacement": True,
        "interior_vacuous_ok": True,
    }


CHECKS = [
    ("edges_and_corners_A_sys_good", check_edges_and_corners),
    ("negative_corner_violation", check_negative_corner_violation),
    ("active_constraints_and_source", check_active_constraints_and_source),
]


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument(
        "--json-out",
        type=Path,
        default=Path(__file__).with_name("verify_nagumo_tangent_cone_results.json"),
    )
    args = p.parse_args(argv)

    report = {
        "milestone": "M28 Nagumo Tangent Cone for Polyhedra",
        "timestamp": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "checks": {},
        "source_doi": "10.11429/ppmsj1919.24.0_551",
        "disclaimer": (
            "Polyhedral Nagumo / Bouligand tangent-cone check only. "
            "Caller-supplied boundary samples; no viability-kernel solver; "
            "no curved boundaries. Covers non-smooth polyhedra — different "
            "case class from M16 CBF, not a replacement. Does not mutate "
            "viability/core.py or control_barrier.py."
        ),
        "untouched": [
            "src/scoped_correspondence/viability/core.py",
            "src/scoped_correspondence/viability/control_barrier.py",
            "src/scoped_correspondence/__init__.py",
            "FORMALISM.md",
            "context_transformations.md",
            "worked_example_viability.md",
            "viability-kernel / Saint-Pierre solver",
            "curved boundaries",
            "M28-replaces-M16 claim",
        ],
    }
    passed = 0
    failed = 0
    errors = []
    for name, fn in CHECKS:
        try:
            report["checks"][name] = {"status": "passed", "detail": fn()}
            passed += 1
            print(f"PASS  {name}")
        except Exception as exc:  # noqa: BLE001 — collect all failures
            failed += 1
            errors.append({"check": name, "error": f"{type(exc).__name__}: {exc}"})
            report["checks"][name] = {
                "status": "failed",
                "error": f"{type(exc).__name__}: {exc}",
            }
            print(f"FAIL  {name}: {exc}")

    summary = {
        "count": len(CHECKS),
        "passed": passed,
        "failed": failed,
        "errors": errors,
        "report": report,
    }
    args.json_out.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(f"\n{passed}/{len(CHECKS)} passed; wrote {args.json_out}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
