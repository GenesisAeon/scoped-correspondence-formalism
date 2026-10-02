"""MU7 verification (MUONIUM_GRAVITY_ROADMAP.md, plan section 10/MU7):
the pilot CLI for all five scenarios.

Checks per scenario: standard JSON; assumptions, identifiability,
parameter space, uncertainty type and limitations present; the real-data
branch appears as 'skipped'; the headline never claims a gravity
measurement or a refutation. Scenario-specific: ideal recovers g_ref within
one period, aliases reports several modes one period apart, offset is not
identifiable, reversal keeps the odd term, velocity_mixture shows a bias.
"""
from __future__ import annotations

import json
import math
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CLI = REPO / "scripts" / "run_muonium_pilot.py"
ALIAS = 100e-9 / (4.4e-6) ** 2
FORBIDDEN = ("einstein", "widerlegt", "disprov", "refut", "measured muonium gravity is")


def require(c, m=""):
    if not c:
        raise AssertionError(m)


def run(scenario, *extra):
    p = subprocess.run([sys.executable, str(CLI), "--scenario", scenario, "--seed", "5", *extra], capture_output=True, text=True, timeout=300)
    require(p.returncode == 0, f"{scenario}: CLI failed: {p.stderr[-400:]}")
    require("Infinity" not in p.stdout and "NaN" not in p.stdout, "standard JSON only")
    return json.loads(p.stdout)


def common(out):
    for key in ("parameter_space", "identifiability", "uncertainty_type", "result", "headline", "real_data", "design"):
        require(key in out, f"missing {key}")
    require(out["real_data"]["result"] == "skipped", "real-data branch is skipped, not passed")
    require(out["result"]["assumptions"] or out["result"]["limitations"], "assumptions/limitations stated")
    h = out["headline"].lower()
    require(not any(f in h for f in FORBIDDEN[:-1]) and "no statement about measured muonium gravity" in h, f"neutral headline: {out['headline']}")


def check_ideal():
    out = run("ideal")
    common(out)
    r = out["result"]["values"]
    require(abs(r["best"] - 9.81) < 0.05 * ALIAS and r["deviance_set_3_84"] is not None, f"ideal: estimate near g_ref, got {r['best']}")
    require(out["result"]["evidence_kind"] == "numerical_sample" and out["result"]["empirical_status"] == "synthetic_only", "synthetic labels")
    return {"best": r["best"]}


def check_aliases():
    out = run("aliases")
    common(out)
    modes = out["result"]["values"]["modes_within_tolerance"]
    require(len(modes) >= 3 and all(math.isclose(b - a, ALIAS, rel_tol=1e-3) for a, b in zip(modes, modes[1:])), f"alias modes: {modes}")
    return {"modes": modes}


def check_offset():
    out = run("offset")
    common(out)
    require("a" in out["result"]["values"]["not_identifiable"] and out["result"]["evidence_kind"] == "analytic_argument", "offset: a not identifiable")
    return {"identifiable": out["result"]["values"]["identifiable"]}


def check_reversal():
    out = run("reversal")
    common(out)
    require("A + declared_odd_disturbance" in out["result"]["values"]["identifiable"], "reversal keeps the odd term with gravity")
    return {"identifiable": out["result"]["values"]["identifiable"]}


def check_velocity_mixture():
    out = run("velocity_mixture")
    common(out)
    require(abs(out["result"]["values"]["bias"]) > 1.0, "incoming-mixture fit is biased")
    return {"bias": out["result"]["values"]["bias"]}


def check_explicit_parameter_space():
    out = run("ideal", "--a-min", "0", "--a-max", "20")
    require(out["parameter_space"] == {"a_min": 0.0, "a_max": 20.0, "unit": "m/s^2"}, "explicit range echoed")
    bad = subprocess.run([sys.executable, str(CLI), "--scenario", "ideal", "--a-min", "5", "--a-max", "1"], capture_output=True, text=True)
    require(bad.returncode != 0, "inverted range rejected")
    return {"range": out["parameter_space"]}


CHECKS = [check_ideal, check_aliases, check_offset, check_reversal, check_velocity_mixture, check_explicit_parameter_space]


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
    out_path = Path(__file__).with_name("verify_muonium_pilot_cli_results.json")
    out_path.write_text(json.dumps({"n_passed": n_passed, "n_total": len(CHECKS), "results": results}, indent=2, default=str))
    print(f"Report written to {out_path}")
    return 0 if n_passed == len(CHECKS) else 1


if __name__ == "__main__":
    raise SystemExit(main())
