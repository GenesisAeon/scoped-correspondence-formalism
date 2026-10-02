"""ON7 verification (ORGANOID_NETWORK_ROADMAP.md, plan section 10/ON7): CLI.

Scenarios exact/confounds reproduce the control values (ON-C02, C04, C06,
C13, C14, C15, C16, C17, C18) through the CLI; adaptive refuses a missing
configuration; the real-data mode is blocked with exit code 2 and never
produces an empty successful evaluation.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CLI = ROOT / "scripts" / "run_organoid_network_pilot.py"


def require(c, m=""):
    if not c:
        raise AssertionError(m)


def run(*args):
    return subprocess.run([sys.executable, str(CLI), *args], capture_output=True, text=True, cwd=ROOT)


def check_exact_and_confounds():
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "exact.json"
        r = run("--scenario", "exact", "--output", str(p))
        require(r.returncode == 0, r.stderr)
        e = json.loads(p.read_text(encoding="utf-8"))
    require(e["full_observer_bits"] == "1" and e["sum_observer_bits"] == "0", "ON-C02 through the CLI")
    require(e["bayes_accuracy_delta_sigma_half"] == 0.9213503964748575 and e["xor_best_single_affine"] == "3/4", "ON-C04/C13")
    require(abs(e["bsc_vs_z_at_accuracy_3_4"]["z_bits"] - 0.311278) < 1e-6 and e["xor_signature"] == [0.0, 0.0, 1.0], "ON-C06/C14")
    r = run("--scenario", "confounds")
    require(r.returncode == 0, r.stderr)
    c = json.loads(r.stdout)
    require(c["block_time_equals_label_bits"] == 1.0 and c["randomised_bits"] == 0.0 and c["common_driver_causal_claim"] is False, "ON-C15/C16")
    require(c["sem2_preparation_vs_pooled"] == ["1/2", "2/499"] and c["sign_flip_p_five_positive"] == "1/16", "ON-C17/C18")
    return {"exact": "ok", "confounds": "ok"}


def check_refusals():
    r = run("--scenario", "real", "--data", "nowhere")
    require(r.returncode == 2 and "blocked" in r.stderr and not r.stdout.strip(), "real mode blocked, no empty success")
    r = run("--scenario", "adaptive", "--config", str(Path(tempfile.gettempdir()) / "missing_organoid_cfg.json"))
    require(r.returncode == 2 and "pre-declared" in r.stderr, "adaptive needs a saved configuration")
    return {"real": "blocked", "adaptive_without_config": "refused"}


CHECKS = [check_exact_and_confounds, check_refusals]


def main():
    results, n_passed = {}, 0
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
    Path(__file__).with_name("verify_organoid_pilot_cli_results.json").write_text(
        json.dumps({"n_passed": n_passed, "n_total": len(CHECKS), "results": results}, indent=2, default=str), encoding="utf-8")
    return 0 if n_passed == len(CHECKS) else 1


if __name__ == "__main__":
    raise SystemExit(main())
