#!/usr/bin/env python3
"""Hand-checkable verification for directed information (Milestone 22).

Checks:
  1. binary_entropy H(1/4) = 2 - (3/4) log2(3)
  2. BSC with feedback (n=2): I_dir = 1-H(p) < I_mutual = 1; summands >= 0
  3. BSC without feedback (n=2,3): I_dir == I_mutual == n(1-H(p)) to machine precision
  4. Massey/Permuter sources; module distances from EI_q/PID; APPLY forbids core/package root

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
from scoped_correspondence.observation.directed_information import (  # noqa: E402
    SOURCE,
    SOURCE_MASSEY,
    SOURCE_PERMUTE,
    binary_entropy,
    bsc_feedback_joint,
    bsc_feedback_vs_mutual,
    bsc_no_feedback_joint,
    directed_information,
)


def require(ok, msg):
    if not bool(ok):
        raise AssertionError(msg)


def near(a, b, atol=1e-12, rtol=1e-12):
    if not math.isclose(float(a), float(b), abs_tol=atol, rel_tol=rtol):
        raise AssertionError(f"{a!r} != {b!r} (atol={atol}, rtol={rtol})")


def check_binary_entropy():
    """H(1/4) hand-check: 2 - 0.75*log2(3)."""
    p = 0.25
    hp = binary_entropy(p)
    expected = 2.0 - 0.75 * math.log2(3.0)
    near(hp, expected, atol=1e-14)
    near(binary_entropy(0.0), 0.0)
    near(binary_entropy(1.0), 0.0)
    near(binary_entropy(0.5), 1.0)
    try:
        binary_entropy(-0.1)
        raise AssertionError("expected ScopeViolationError for p<0")
    except ScopeViolationError:
        pass
    return {"H_1_4": hp, "H_1_4_analytic": expected}


def check_bsc_feedback_n2():
    """BSC feedback n=2: I_dir = 1-H(p) < I_mutual = 1."""
    p = 0.25
    hp = binary_entropy(p)
    rep = directed_information(bsc_feedback_joint(p, n=2))
    near(rep.I_directed, 1.0 - hp, atol=1e-12)
    near(rep.I_mutual, 1.0, atol=1e-12)
    require(rep.I_directed < rep.I_mutual - 1e-9, "need strict I_dir < I_mutual")
    require(len(rep.summands) == 2, repr(rep.summands))
    near(rep.summands[0], 1.0 - hp, atol=1e-12)
    near(rep.summands[1], 0.0, atol=1e-12)
    for s in rep.summands:
        require(s >= -1e-15, f"summand negative: {s}")
    near(rep.gap, hp, atol=1e-12)
    return {
        "p": p,
        "H_p": hp,
        "I_directed": rep.I_directed,
        "I_mutual": rep.I_mutual,
        "summands": list(rep.summands),
        "gap": rep.gap,
    }


def check_bsc_no_feedback_equality():
    """No feedback: I_dir == I_mutual == n(1-H(p)) to machine precision."""
    p = 0.25
    hp = binary_entropy(p)
    out = {}
    for n in (2, 3):
        rep = directed_information(bsc_no_feedback_joint(p, n=n))
        target = n * (1.0 - hp)
        near(rep.I_directed, target, atol=1e-12)
        near(rep.I_mutual, target, atol=1e-12)
        near(rep.I_directed, rep.I_mutual, atol=1e-14)
        require(all(s >= -1e-15 for s in rep.summands), repr(rep.summands))
        for s in rep.summands:
            near(s, 1.0 - hp, atol=1e-12)
        out[f"n{n}"] = {
            "I_directed": rep.I_directed,
            "I_mutual": rep.I_mutual,
            "summands": list(rep.summands),
            "analytic": target,
            "abs_gap_dir_vs_mut": abs(rep.I_directed - rep.I_mutual),
        }
    return out


def check_sources_and_scope():
    """Massey / Permuter citations; no EI_q/PID same-formula claim; APPLY guards."""
    require("Massey" in SOURCE_MASSEY, SOURCE_MASSEY)
    require("1990" in SOURCE_MASSEY, SOURCE_MASSEY)
    require("Permuter" in SOURCE_PERMUTE, SOURCE_PERMUTE)
    require("2009" in SOURCE_PERMUTE, SOURCE_PERMUTE)
    require("55(2)" in SOURCE_PERMUTE or "55(2)" in SOURCE, SOURCE)
    require("644" in SOURCE_PERMUTE, SOURCE_PERMUTE)

    mod_path = (
        ROOT
        / "src"
        / "scoped_correspondence"
        / "observation"
        / "directed_information.py"
    )
    text = mod_path.read_text(encoding="utf-8")
    require("Massey" in text and "Permuter" in text, "sources in module")
    lowered = text.lower()
    require(
        "not" in lowered and ("ei_q" in lowered or "pid" in lowered),
        "must explicitly distance from EI_q/PID",
    )
    require(
        "from scoped_correspondence.information_decomposition" not in text,
        "must not import information_decomposition",
    )
    require(
        "continuous-time" in lowered or "continuous time" in lowered,
        "must state no continuous-time scope",
    )
    require(
        "does **not** edit" in text.lower() or "does not edit" in lowered,
        "must state core/package __init__ not edited",
    )

    apply = ROOT / "APPLY_ON_MACHINE.ps1"
    if apply.exists():
        apply_txt = apply.read_text(encoding="utf-8")
        for needle in (
            "observation/core.py",
            "scoped_correspondence/__init__.py",
            "FORMALISM.md",
        ):
            require(needle in apply_txt, f"APPLY missing forbidden guard: {needle}")
        for line in apply_txt.splitlines():
            if "Copy-Item" not in line:
                continue
            norm = line.replace("/", "\\")
            require(
                "observation\\core.py" not in norm
                and "observation/core.py" not in line,
                f"Copy-Item must not touch observation/core.py: {line}",
            )
            # Forbid package-root __init__ copy; allow observation\__init__.py
            if "scoped_correspondence\\__init__.py" in norm or "scoped_correspondence/__init__.py" in line:
                require(
                    "observation\\__init__.py" in norm
                    or "observation/__init__.py" in line
                    or "observation" + chr(92) + "__init__.py" in line,
                    f"Copy-Item must not touch package-root __init__: {line}",
                )

    side = bsc_feedback_vs_mutual(p=0.25, n=2)
    require(
        side["with_feedback"]["I_directed"] < side["with_feedback"]["I_mutual"],
        "feedback side-by-side strict inequality",
    )
    require(
        abs(
            side["without_feedback"]["I_directed"]
            - side["without_feedback"]["I_mutual"]
        )
        < 1e-12,
        "no-feedback equality",
    )
    return {
        "SOURCE": SOURCE,
        "side_by_side_I_dir_feedback": side["with_feedback"]["I_directed"],
        "side_by_side_I_mut_feedback": side["with_feedback"]["I_mutual"],
        "side_by_side_I_dir_nofb": side["without_feedback"]["I_directed"],
        "side_by_side_I_mut_nofb": side["without_feedback"]["I_mutual"],
        "apply_guards_checked": apply.exists(),
    }


CHECKS = [
    ("binary_entropy_H_1_4", check_binary_entropy),
    ("bsc_feedback_n2_strict_inequality", check_bsc_feedback_n2),
    ("bsc_no_feedback_equality", check_bsc_no_feedback_equality),
    ("sources_scope_forbidden", check_sources_and_scope),
]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)

    report = {
        "milestone": 22,
        "name": "directed_information",
        "timestamp_local": dt.datetime.now().isoformat(timespec="seconds"),
        "platform": platform.platform(),
        "python": sys.version.split()[0],
        "checks": [],
    }
    passed = failed = 0
    for name, fn in CHECKS:
        entry = {"name": name, "ok": False}
        try:
            detail = fn()
            entry["ok"] = True
            entry["detail"] = detail
            passed += 1
            print(f"PASS  {name}")
        except Exception as exc:  # noqa: BLE001
            entry["ok"] = False
            entry["error"] = f"{type(exc).__name__}: {exc}"
            failed += 1
            print(f"FAIL  {name}: {exc}")
        report["checks"].append(entry)

    report["count"] = len(CHECKS)
    report["passed"] = passed
    report["failed"] = failed

    try:
        hp = binary_entropy(0.25)
        fb = directed_information(bsc_feedback_joint(0.25, n=2))
        no = directed_information(bsc_no_feedback_joint(0.25, n=2))
        report["key_numbers"] = {
            "H_1_4": hp,
            "feedback_n2_I_directed": fb.I_directed,
            "feedback_n2_I_mutual": fb.I_mutual,
            "feedback_n2_summands": list(fb.summands),
            "nofeedback_n2_I_directed": no.I_directed,
            "nofeedback_n2_I_mutual": no.I_mutual,
            "nofeedback_n2_summands": list(no.summands),
        }
    except Exception as exc:  # noqa: BLE001
        report["key_numbers_error"] = str(exc)

    out = args.json_out or (
        Path(__file__).resolve().parent / "verify_directed_information_core_results.json"
    )
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"JSON -> {out}")
    print(f"{passed}/{len(CHECKS)} passed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
