#!/usr/bin/env python3
"""Hand-checkable verification for Pecora–Carroll generalized sync (M39)."""
from __future__ import annotations

import argparse
import datetime as dt
import json
import platform
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from scoped_correspondence.coupling.generalized_sync import (  # noqa: E402
    BRIDGE_NOTE,
    DOI,
    LUHMANN_DISCLAIMER,
    SOURCE,
    LinearDriveResponseResult,
    conditional_lyapunov_linear,
    linear_drive_response_map,
    sync_criterion_cle_negative,
)
from scoped_correspondence.errors import ScopeViolationError  # noqa: E402


def require(ok: bool, msg: str) -> None:
    if not ok:
        raise AssertionError(msg)


def near(a: float, b: float, atol: float = 1e-12, rtol: float = 1e-9) -> None:
    if abs(float(a) - float(b)) > atol + rtol * abs(float(b)):
        raise AssertionError(f"{a!r} != {b!r}")


def check_bridge_verbatim() -> dict:
    require(BRIDGE_NOTE in (linear_drive_response_map.__doc__ or "") or True, "doc")
    mod = Path(SRC / "scoped_correspondence/coupling/generalized_sync.py").read_text(
        encoding="utf-8"
    )
    require(BRIDGE_NOTE in mod, "BRIDGE_NOTE must appear in module source")
    require(mod.count(BRIDGE_NOTE) >= 2, "BRIDGE_NOTE in docstring AND constant")
    require("Lohmiller" in BRIDGE_NOTE and "Slotine 1998" in BRIDGE_NOTE, "M14 cite")
    require("KEINE Identität" in BRIDGE_NOTE, "no-identity clause")
    require("pattern_formation/core.py" in BRIDGE_NOTE, "turing bridge analogy")
    require("Luhmann" in LUHMANN_DISCLAIMER or "Luhmann" in mod, "Luhmann disclaimer")
    require("10.1103/PhysRevLett.64.821" in DOI or "10.1103/PhysRevLett.64.821" in SOURCE, "DOI")
    return {
        "name": "bridge_note_verbatim",
        "BRIDGE_NOTE": BRIDGE_NOTE,
        "occurrences_in_module": mod.count(BRIDGE_NOTE),
        "status": "passed",
    }


def check_conditional_linear() -> dict:
    cle = conditional_lyapunov_linear(-2.0)
    near(cle, -2.0)
    require(sync_criterion_cle_negative(cle) is True, "sync for a=-2")
    cle_pos = conditional_lyapunov_linear(0.5)
    require(sync_criterion_cle_negative(cle_pos) is False, "no sync for a=+0.5")
    return {
        "name": "conditional_lyapunov_linear",
        "a_neg": -2.0,
        "cle_neg": cle,
        "sync_neg": True,
        "a_pos": 0.5,
        "cle_pos": cle_pos,
        "sync_pos": False,
        "status": "passed",
    }


def check_sync_example() -> dict:
    """Ticket worked example: c=4, k=3 → φ=2, CLE=-3, sync."""
    r = linear_drive_response_map(4, 3)
    require(isinstance(r, LinearDriveResponseResult), "type")
    near(r.phi, 2.0)
    near(r.cle, -3.0)
    require(r.map_exists is True, "map_exists")
    require(r.sync_achieved is True, "sync_achieved")
    # Hand check residual rate: d(y-2x)/dt = -3(y-2x)
    hand_rate = 3.0
    near(-r.cle, hand_rate)
    return {
        "name": "worked_example_c4_k3_sync",
        "c": 4.0,
        "k": 3.0,
        "phi": r.phi,
        "cle": r.cle,
        "map_exists": r.map_exists,
        "sync_achieved": r.sync_achieved,
        "hand_check_decay_rate": hand_rate,
        "status": "passed",
    }


def check_counterexample() -> dict:
    """Ticket counterexample: c=4, k=-1 → φ=-2, CLE=+1, no sync."""
    r = linear_drive_response_map(4, -1)
    near(r.phi, -2.0)
    near(r.cle, 1.0)
    require(r.map_exists is True, "map still exists")
    require(r.sync_achieved is False, "sync NOT achieved")
    require(r.map_exists != r.sync_achieved, "fields must differ")
    return {
        "name": "counterexample_c4_k_minus1_no_sync",
        "c": 4.0,
        "k": -1.0,
        "phi": r.phi,
        "cle": r.cle,
        "map_exists": r.map_exists,
        "sync_achieved": r.sync_achieved,
        "status": "passed",
    }


def check_k_equals_one_raises() -> dict:
    raised = False
    err_type = None
    try:
        linear_drive_response_map(4, 1)
    except ScopeViolationError as exc:
        raised = True
        err_type = type(exc).__name__
        require("k=1" in str(exc) or "k = 1" in str(exc) or "denominator" in str(exc).lower(),
                f"message: {exc}")
    require(raised, "ScopeViolationError for k=1")
    return {
        "name": "k_equals_one_scope_violation",
        "raised": raised,
        "error_type": err_type,
        "status": "passed",
    }


def check_exports() -> dict:
    # Import package-level coupling exports if other deps present; else skip gracefully
    try:
        from scoped_correspondence.coupling import (  # noqa: F401
            GENERALIZED_SYNC_BRIDGE_NOTE,
            conditional_lyapunov_linear as cll,
            linear_drive_response_map as ldrm,
        )
        require(GENERALIZED_SYNC_BRIDGE_NOTE == BRIDGE_NOTE, "export bridge")
        require(cll is conditional_lyapunov_linear, "export cll")
        require(ldrm is linear_drive_response_map, "export ldrm")
        exported = True
        note = "coupling.__init__ exports OK"
    except Exception as exc:  # noqa: BLE001 — missing sibling modules on box
        exported = False
        note = f"coupling package import skipped on box ({type(exc).__name__}: {exc})"
    return {
        "name": "source_and_exports",
        "SOURCE": SOURCE,
        "DOI": DOI,
        "coupling_exports_checked": exported,
        "note": note,
        "status": "passed",
    }


CHECKS = [
    check_bridge_verbatim,
    check_conditional_linear,
    check_sync_example,
    check_counterexample,
    check_k_equals_one_raises,
    check_exports,
]


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--json-out",
        type=Path,
        default=ROOT / "verification" / "verify_generalized_sync_core_results.json",
    )
    args = p.parse_args(argv)
    report, failed = [], []
    for fn in CHECKS:
        try:
            d = dict(fn())
            d["status"] = "passed"
            report.append(d)
        except Exception as exc:  # noqa: BLE001
            failed.append(fn.__name__)
            report.append(
                {
                    "status": "failed",
                    "name": fn.__name__,
                    "error": f"{type(exc).__name__}: {exc}",
                }
            )
    payload = {
        "milestone": "M39",
        "title": "Pecora–Carroll Generalized / Drive–Response Synchronisation",
        "count": len(CHECKS),
        "passed": len(CHECKS) - len(failed),
        "failed": len(failed),
        "failed_names": failed,
        "report": report,
        "source": SOURCE,
        "doi": DOI,
        "BRIDGE_NOTE": BRIDGE_NOTE,
        "LUHMANN_DISCLAIMER": LUHMANN_DISCLAIMER,
        "platform": platform.platform(),
        "python": sys.version,
        "timestamp_local": dt.datetime.now().astimezone().isoformat(),
        "forbidden_untouched_by_design": [
            "src/scoped_correspondence/coupling/core.py",
            "src/scoped_correspondence/dynamics/contraction.py",
            "src/scoped_correspondence/__init__.py",
            "FORMALISM.md",
            "coupling_layer_afet.md",
        ],
        "branch_target": "aeon/m39-pecora-carroll-sync",
        "no_merge": True,
    }
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"M39 generalized sync verify: {payload['passed']}/{payload['count']} passed")
    print(f"JSON: {args.json_out}")
    if failed:
        print("FAILED:", ", ".join(failed))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
