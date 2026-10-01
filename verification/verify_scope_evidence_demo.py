"""J12 verification (SCOPE_COMPOSITION_EVIDENCE_ROADMAP.md, plan section 18):
the scope/evidence demo CLI shows each of the six mandatory demonstrations
with the intended outcome and standard JSON only.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CLI = REPO / "scripts" / "run_scope_evidence_demo.py"


def require(c, m=""):
    if not c:
        raise AssertionError(m)


def main():
    p = subprocess.run([sys.executable, str(CLI)], capture_output=True, text=True, timeout=300)
    results, n_passed, checks = {}, 0, []
    try:
        require(p.returncode == 0, f"CLI failed: {p.stderr[-400:]}")
        require("NaN" not in p.stdout and "Infinity" not in p.stdout, "standard JSON only")
        out = json.loads(p.stdout)
        c = out["incompatible_chain_and_restricted_scope"]
        checks.append(("1_incompatible_then_restricted", c["incompatible_attempt"]["status"] == "incompatible"
                       and c["after_fixing_units"]["scope"]["bounds"] == [["0", "1/2"]]))
        d = out["continuous_domain_certificate_and_counterexample"]
        checks.append(("2_certificate_and_counterexample", d["claim_proved"]["verdict"] == "proved"
                       and d["claim_refuted"]["counterexample"] == {"x": "1/2"}))
        o = out["observationally_equivalent_interventionally_different"]
        checks.append(("3_observation_vs_intervention", o["Y=X"]["observational"] == o["Y=U"]["observational"]
                       and (o["Y=X"]["P(Y=1|do(X=1))"], o["Y=U"]["P(Y=1|do(X=1))"]) == ("1", "1/2")))
        t = out["transportable_and_not_certified_query"]
        checks.append(("4_transport", t["transportable"]["outcome"] == "certified_applicable" and t["transportable"]["Q(Y=1|do(X=0))"] == "3/4"
                       and t["not_certified"]["outcome"] == "not_certified_by_this_rule"))
        f = out["forecast_comparison_with_inferential_limit"]
        checks.append(("5_forecast_limit", f["inference_status"] == "not_applicable" and any(r.startswith("series_too_short") for r in f["reasons"])
                       and "descriptive comparison only" in f["sentence"]))
        w = out["weighted_calibration_with_visible_unboundedness"]
        checks.append(("6_weighted_unbounded_visible", {"kind": "whole_real_line"} in w["intervals"] and w["unbounded_fraction"] == 0.5))
    except AssertionError as e:
        checks.append(("cli_runs", False))
        results["error"] = str(e)
    for name, ok in checks:
        print(("PASS  " if ok else "FAIL  ") + name)
        results[name] = ok
        n_passed += int(ok)
    print(f"\n{n_passed}/{len(checks)} checks passed")
    Path(__file__).with_name("verify_scope_evidence_demo_results.json").write_text(
        json.dumps({"n_passed": n_passed, "n_total": len(checks), "results": results}, indent=2), encoding="utf-8")
    return 0 if checks and n_passed == len(checks) else 1


if __name__ == "__main__":
    raise SystemExit(main())
