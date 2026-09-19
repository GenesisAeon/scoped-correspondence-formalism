#!/usr/bin/env python3
"""Hand-checkable verification for Arimoto–Blahut DMC capacity (Milestone 25).

Checks:
  1. Z-channel ε=0.5: C=log2(1.25), r*=(0.6,0.4); closed form computed IN SCRIPT
  2. BSC p=0.1: C=1-H2(0.1), r* uniform; converges immediately from uniform start
  3. Report iteration counts to tolerance; ScopeViolationError on bad Q
  4. Sources Arimoto 1972 / Blahut 1972; NOT Shannon–Hartley; no rate-distortion;
     core/package-root untouched

JSON {count, passed, failed, report}; numbers from this run.
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

from scoped_correspondence.errors import ScopeViolationError  # noqa: E402
from scoped_correspondence.observation.arimoto_blahut import (  # noqa: E402
    SOURCE,
    SOURCE_ARIMOTO,
    SOURCE_BLAHUT,
    blahut_arimoto_capacity,
    binary_entropy,
    bsc_channel,
    z_channel,
    z_channel_capacity_closed_form,
)
from scoped_correspondence.observation.core import channel_capacity  # noqa: E402


def require(ok, msg):
    if not bool(ok):
        raise AssertionError(msg)


def near(a, b, atol=1e-12, rtol=1e-12):
    if not math.isclose(float(a), float(b), abs_tol=atol, rel_tol=rtol):
        raise AssertionError(f"{a!r} != {b!r} (atol={atol}, rtol={rtol})")


def check_z_channel_half():
    """Z-channel ε=1/2: C=log2(5/4), r*=(0.6,0.4); closed form computed here."""
    eps = 0.5
    # Closed form computed IN SCRIPT (not hardcoded as only reference):
    # β = (1-ε) ε^{ε/(1-ε)} = 0.5 * 0.5^1 = 0.25
    # C = log2(1+β) = log2(1.25)
    beta = (1.0 - eps) * (eps ** (eps / (1.0 - eps)))
    C_analytic = math.log2(1.0 + beta)
    # Critical-point α*=P(X=1): γ*=P(Y=1)=1/(1+2^{H(ε)/(1-ε)}); α*=γ*/(1-ε)
    H_eps = binary_entropy(eps)
    gamma_star = 1.0 / (1.0 + (2.0 ** (H_eps / (1.0 - eps))))
    alpha_star = gamma_star / (1.0 - eps)
    r_analytic = (1.0 - alpha_star, alpha_star)

    # Module closed-form helper must agree (also computed, not a magic constant).
    C_mod, r_mod = z_channel_capacity_closed_form(eps)
    near(C_mod, C_analytic, atol=1e-14)
    near(r_mod[0], r_analytic[0], atol=1e-14)
    near(r_mod[1], r_analytic[1], atol=1e-14)
    near(C_analytic, math.log2(1.25), atol=1e-14)
    near(r_analytic[0], 0.6, atol=1e-14)
    near(r_analytic[1], 0.4, atol=1e-14)

    tol = 1e-14
    res = blahut_arimoto_capacity(z_channel(eps), r0=(0.5, 0.5), tol=tol)
    near(res.capacity, C_analytic, atol=1e-10)
    near(res.r_star[0], 0.6, atol=1e-8)
    near(res.r_star[1], 0.4, atol=1e-8)
    require(res.converged, "Z-channel BA must converge")
    require(res.iterations >= 1, "need at least one BA evaluation")

    return {
        "epsilon": eps,
        "beta": beta,
        "C_analytic_log2_1_25": C_analytic,
        "r_analytic": list(r_analytic),
        "C_ba": res.capacity,
        "r_star": list(res.r_star),
        "iterations": res.iterations,
        "tol": tol,
        "abs_err_C": abs(res.capacity - C_analytic),
        "abs_err_r0": abs(res.r_star[0] - 0.6),
        "abs_err_r1": abs(res.r_star[1] - 0.4),
    }


def check_bsc_p01():
    """BSC p=0.1: C=1-H2(0.1); r* uniform; immediate from uniform start."""
    p = 0.1
    # H2 computed in script (not a pasted constant as only reference)
    H = binary_entropy(p)
    C_analytic = 1.0 - H
    # Cross-check expansion: -p log2 p - (1-p) log2(1-p)
    H_expand = -p * math.log2(p) - (1.0 - p) * math.log2(1.0 - p)
    near(H, H_expand, atol=1e-15)

    tol = 1e-14
    res = blahut_arimoto_capacity(bsc_channel(p), r0=(0.5, 0.5), tol=tol)
    near(res.capacity, C_analytic, atol=1e-12)
    near(res.r_star[0], 0.5, atol=1e-12)
    near(res.r_star[1], 0.5, atol=1e-12)
    require(res.converged, "BSC BA must converge")
    # From uniform start the fixed point is immediate (1 evaluation / update).
    require(
        res.iterations <= 2,
        f"BSC from uniform should converge immediately; got iterations={res.iterations}",
    )

    return {
        "p": p,
        "H2_p": H,
        "C_analytic_1_minus_H2": C_analytic,
        "C_ba": res.capacity,
        "r_star": list(res.r_star),
        "iterations": res.iterations,
        "tol": tol,
        "abs_err_C": abs(res.capacity - C_analytic),
    }


def check_scope_and_sources():
    """Negatives / non-stochastic → ScopeViolationError; sources; no RD / no SH equate."""
    try:
        blahut_arimoto_capacity([[1.0, 0.0], [0.5, -0.1]])
        raise AssertionError("expected ScopeViolationError for negative Q")
    except ScopeViolationError:
        pass
    try:
        blahut_arimoto_capacity([[1.0, 0.0], [0.3, 0.3]])
        raise AssertionError("expected ScopeViolationError for non-row-stochastic Q")
    except ScopeViolationError:
        pass

    require("Arimoto" in SOURCE_ARIMOTO and "1972" in SOURCE_ARIMOTO, SOURCE_ARIMOTO)
    require("10.1109/TIT.1972.1054753" in SOURCE_ARIMOTO, SOURCE_ARIMOTO)
    require("Blahut" in SOURCE_BLAHUT and "1972" in SOURCE_BLAHUT, SOURCE_BLAHUT)
    require("10.1109/TIT.1972.1054855" in SOURCE_BLAHUT, SOURCE_BLAHUT)
    require("Arimoto" in SOURCE and "Blahut" in SOURCE, SOURCE)

    mod_path = (
        ROOT / "src" / "scoped_correspondence" / "observation" / "arimoto_blahut.py"
    )
    text = mod_path.read_text(encoding="utf-8")
    lowered = text.lower()
    require("shannon–hartley" in lowered or "shannon-hartley" in lowered, "must name Shannon-Hartley")
    require(
        "not" in lowered and ("same" in lowered or "replace" in lowered or "additional" in lowered),
        "must distance from Shannon-Hartley channel_capacity",
    )
    require(
        "rate-distortion" in lowered or "rate distortion" in lowered,
        "must mention rate-distortion as out of scope",
    )
    require(
        "out of scope" in lowered or "not implemented" in lowered or "does **not**" in text.lower(),
        "must state rate-distortion not implemented",
    )
    require(
        "does **not** edit" in text.lower() or "does not edit" in lowered,
        "must state core/package __init__ not edited",
    )
    require(
        "from scoped_correspondence.observation.core import channel_capacity" not in text,
        "must not import Shannon-Hartley channel_capacity into BA module",
    )

    # Shannon–Hartley still works untouched and is a different number/object.
    sh = channel_capacity(1.0, 1.0)  # B=1, SNR=1 → 1 bit
    near(sh, 1.0, atol=1e-15)
    z = blahut_arimoto_capacity(z_channel(0.5))
    require(abs(z.capacity - sh) > 0.1, "DMC Z-capacity must differ from SH(B=1,SNR=1)")

    # Forbidden files must exist unchanged relative to delivery (presence check).
    core_path = ROOT / "src" / "scoped_correspondence" / "observation" / "core.py"
    require(core_path.is_file(), "core.py present for local test; APPLY forbids editing it")
    require("def channel_capacity" in core_path.read_text(encoding="utf-8"), "core SH intact")

    return {
        "SOURCE_ARIMOTO": SOURCE_ARIMOTO,
        "SOURCE_BLAHUT": SOURCE_BLAHUT,
        "shannon_hartley_B1_SNR1": sh,
        "z_capacity_distinct": z.capacity,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--json-out",
        type=Path,
        default=ROOT / "verification" / "verify_arimoto_blahut_capacity_results.json",
    )
    args = parser.parse_args()

    checks = [
        ("z_channel_eps_0_5", check_z_channel_half),
        ("bsc_p_0_1", check_bsc_p01),
        ("scope_and_sources", check_scope_and_sources),
    ]
    report = {}
    passed = 0
    failed = 0
    errors = []
    for name, fn in checks:
        try:
            report[name] = fn()
            report[name]["_status"] = "passed"
            passed += 1
            print(f"PASS  {name}")
        except Exception as exc:  # noqa: BLE001 — collect all failures
            failed += 1
            report[name] = {"_status": "failed", "error": repr(exc)}
            errors.append(f"{name}: {exc!r}")
            print(f"FAIL  {name}: {exc!r}")

    payload = {
        "milestone": 25,
        "name": "arimoto_blahut_capacity",
        "count": len(checks),
        "passed": passed,
        "failed": failed,
        "report": report,
        "errors": errors,
        "meta": {
            "timestamp": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
            "python": sys.version.split()[0],
            "platform": platform.platform(),
        },
    }
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"JSON → {args.json_out}")
    print(f"{passed}/{len(checks)} passed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
