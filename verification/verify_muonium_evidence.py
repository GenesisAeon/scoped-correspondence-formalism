"""MU6 verification (MUONIUM_GRAVITY_ROADMAP.md, plan section 10/MU6):
evidence adapter and the (deferred) real-data window.

Checks: synthetic, analytic and finite results map onto the EXISTING
evidence vocabularies; real source, synthetic measurement and future
projection stay distinguishable in JSON; a source-metadata record cannot
carry a muonium gravity value; JSON is standard (no NaN / Infinity); the
real-data branch is 'skipped' (deferred, license InC-NC, schema
unchecked) -- never 'passed'.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from scoped_correspondence.epistemic.records import EMPIRICAL_STATUSES, EVIDENCE_KINDS
from scoped_correspondence.errors import ScopeViolationError
from scoped_correspondence.muonium.evidence import REAL_DATA_STATUS, EvidenceRecord, dumps, real_data_check


def require(c, m=""):
    if not c:
        raise AssertionError(m)


def raises(fn, exc=ScopeViolationError):
    try:
        fn()
    except exc:
        return True
    return False


def check_vocabulary_mapping():
    syn = EvidenceRecord("synthetic_measurement", "injected a = g_ref recovered", ("design",), ("ideal model",), {"a_hat": 9.8})
    ana = EvidenceRecord("analytic_result", "(a, phi0) degenerate at one flight time", (), ("unwrapped phase",))
    fin = EvidenceRecord("finite_audit", "three listed candidates share the counts", (), ("listed candidates only",))
    require((syn.evidence_kind, syn.empirical_status) == ("numerical_sample", "synthetic_only"), "synthetic -> numerical_sample / synthetic_only")
    require((ana.evidence_kind, ana.empirical_status) == ("analytic_argument", "not_tested"), "analytic mapping")
    require((fin.evidence_kind, fin.empirical_status) == ("exhaustive_finite", "not_tested"), "finite mapping")
    for r in (syn, ana, fin):
        require(r.evidence_kind in EVIDENCE_KINDS and r.empirical_status in EMPIRICAL_STATUSES, "existing vocabularies only")
    return {"synthetic": [syn.evidence_kind, syn.empirical_status]}


def check_record_kinds_distinguishable_and_no_gravity_from_source():
    src = EvidenceRecord("real_source_metadata", "beam source characterised (MU-S1)", ("MU-S1",), (), {"beam_velocity_m_per_s": 2180})
    fut = EvidenceRecord("future_projection", "events needed for 1 % (ideal local bound)", (), ("ideal quadrature",), {"events": 5.73e8})
    blob = json.loads(dumps([src.to_dict(), fut.to_dict()]))
    require([b["record_kind"] for b in blob] == ["real_source_metadata", "future_projection"], "kinds survive JSON")
    require(raises(lambda: EvidenceRecord("real_source_metadata", "x", ("MU-S1",), (), {"a_mu": 9.8})),
            "a source record cannot carry a measured muonium acceleration (none exists)")
    return {"kinds": [b["record_kind"] for b in blob]}


def check_standard_json():
    rec = EvidenceRecord("synthetic_measurement", "impossible observation", (), (), {"nll": math.inf, "phase": float("nan")})
    out = json.loads(dumps(rec.to_dict()))
    require(out["values"]["nll"] == {"status": "positive_infinity"} and out["values"]["phase"] == {"status": "undefined"},
            "non-finite values become explicit status markers")
    require("Infinity" not in dumps(rec.to_dict()) and "NaN" not in dumps(rec.to_dict()), "no non-standard JSON tokens")
    return {"nll": out["values"]["nll"]}


def check_real_data_branch_deferred_not_passed():
    chk = real_data_check()
    require(chk["result"] == "skipped" and chk["reason"] == "deferred", "real-data check is skipped/deferred, never passed")
    require(REAL_DATA_STATUS["may_be_committed"] is False and "InC-NC" in REAL_DATA_STATUS["license"], "license blocks committing")
    require(REAL_DATA_STATUS["schema_checked"] is False, "schema not inspected: no decoder against a guessed schema")
    return {"result": chk["result"], "license": REAL_DATA_STATUS["license"]}


CHECKS = [
    check_vocabulary_mapping,
    check_record_kinds_distinguishable_and_no_gravity_from_source,
    check_standard_json,
    check_real_data_branch_deferred_not_passed,
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
    out_path = Path(__file__).with_name("verify_muonium_evidence_results.json")
    out_path.write_text(json.dumps({"n_passed": n_passed, "n_total": len(CHECKS), "results": results}, indent=2, default=str))
    print(f"Report written to {out_path}")
    return 0 if n_passed == len(CHECKS) else 1


if __name__ == "__main__":
    raise SystemExit(main())
