#!/usr/bin/env python3
"""Hand-checkable verification for Dissipativity / Supply Rates (M15)."""
from __future__ import annotations
import argparse, datetime as dt, json, platform, sys
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
from scoped_correspondence.coupling.dissipativity import (
    STORAGE_INEQUALITY_TOL, SOURCE, DissipativityCertificate,
    check_storage_inequality, make_dissipativity_certificate,
    neutral_interconnection_supply,
)
def require(ok, msg):
    if not ok: raise AssertionError(msg)
def near(a, b, atol=1e-12, rtol=1e-9):
    if not np.isclose(float(a), float(b), atol=atol, rtol=rtol):
        raise AssertionError(f"{a!r} != {b!r}")
def vdot_single(x, u):
    return -x*x + x*u
def check_worked():
    x1, x2 = 1.0, 2.0
    y1, y2 = x1, x2
    u1, u2 = -y2, y1
    supply = neutral_interconnection_supply(y1, u1, y2, u2)
    near(supply, 0.0)
    vdot_total = vdot_single(x1, u1) + vdot_single(x2, u2)
    near(vdot_total, -5.0)
    require(check_storage_inequality(vdot_total, supply), "closed-loop")
    cert = make_dissipativity_certificate(vdot_total, supply)
    require(cert.ok and "NOT" in (DissipativityCertificate.__doc__ or "") and "thermodynamic" in (DissipativityCertificate.__doc__ or "").lower(), "cert/doc")
    require("10.1007/BF00276493" in SOURCE, "DOI")
    return {"name": "worked_example_x1_1_x2_2", "V_dot_total": vdot_total, "expected_V_dot_total": -5.0, "status": "passed"}
def check_second():
    x1, x2 = 0.5, 1.5
    u1, u2 = -x2, x1
    supply = neutral_interconnection_supply(x1, u1, x2, u2)
    vdot_total = vdot_single(x1, u1) + vdot_single(x2, u2)
    near(vdot_total, -2.5)
    require(check_storage_inequality(vdot_total, supply), "ok")
    return {"name": "second_state_pair_0p5_1p5", "V_dot_total": vdot_total, "expected_V_dot_total": -2.5, "status": "passed"}
def check_violate():
    ok = check_storage_inequality(1.0, 0.0, tol=STORAGE_INEQUALITY_TOL)
    require(ok is False, "violate")
    cert = make_dissipativity_certificate(1.0, 0.0)
    require(cert.ok is False, "cert false")
    return {"name": "intentional_violate", "check_ok": ok, "cert_ok": cert.ok, "status": "passed"}
def check_exports():
    from scoped_correspondence.coupling import (
        DISSIPATIVITY_SOURCE, DissipativityCertificate as DC,
        check_storage_inequality as csi, neutral_interconnection_supply as nis,
    )
    require(DC is DissipativityCertificate and csi is check_storage_inequality and nis is neutral_interconnection_supply, "exports")
    require("10.1007/BF00276493" in DISSIPATIVITY_SOURCE, "DOI")
    return {"name": "source_and_exports", "SOURCE": SOURCE, "doi": "10.1007/BF00276493", "status": "passed"}
CHECKS = [check_worked, check_second, check_violate, check_exports]
def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--json-out", type=Path, default=ROOT/"verification"/"verify_dissipativity_core_results.json")
    args = p.parse_args(argv)
    report, failed = [], []
    for fn in CHECKS:
        try:
            d = dict(fn()); d["status"]="passed"; report.append(d)
        except Exception as exc:
            failed.append(fn.__name__)
            report.append({"status":"failed","name":fn.__name__,"error":f"{type(exc).__name__}: {exc}"})
    payload = {
        "milestone":"M15","title":"Dissipativity / Supply Rates",
        "count":len(CHECKS),"passed":len(CHECKS)-len(failed),"failed":len(failed),
        "failed_names":failed,"report":report,"source":SOURCE,"doi":"10.1007/BF00276493",
        "platform":platform.platform(),"python":sys.version,
        "timestamp_local":dt.datetime.now().astimezone().isoformat(),
        "forbidden_untouched_by_design":[
            "src/scoped_correspondence/coupling/core.py",
            "src/scoped_correspondence/coupling/dirac_composition.py",
            "src/scoped_correspondence/__init__.py","FORMALISM.md","coupling_layer_afet.md",
            "closure/","validation/",
        ],
        "key_number_V_dot_total_at_1_2": -5.0,
    }
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(payload, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    if failed:
        print("FAILED", failed, file=sys.stderr); return 1
    print(f"OK: {payload['passed']}/{payload['count']} passed; V_dot_total(1,2)=-5")
    return 0
if __name__ == "__main__":
    raise SystemExit(main())
