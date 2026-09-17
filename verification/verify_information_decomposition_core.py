#!/usr/bin/env python3
"""Equivalence checks for Information Decomposition core (Milestone 7 / F09+F12).

Matches legacy verify_pid_rb_results.json p01–p07 EXACTLY, plus TWO_BIT_COPY
(Red_williams_beer=1, RB0_blackwell=0). Does NOT edit verify_pid_rb.py.
"""
from __future__ import annotations

import argparse
import datetime as dt
import itertools
import json
import math
import platform
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from scoped_correspondence.information_decomposition import (  # noqa: E402
    ARXIV_RB,
    ARXIV_WB,
    compare_to_EI_q,
    ei_q_channel,
    pid_atoms_williams_beer,
    rb0_blackwell,
    two_bit_copy_report,
)
from scoped_correspondence.information_decomposition.core import (  # noqa: E402
    assert_nonnegative_atoms,
    entropy,
    joint_from_samples,
)


def require(ok, msg):
    if not bool(ok):
        raise AssertionError(msg)


def near(a, b, atol=1e-10, rtol=1e-9):
    if not np.allclose(a, b, atol=atol, rtol=rtol):
        raise AssertionError(f"{a!r} != {b!r}")


def load_legacy():
    path = ROOT / "verification" / "verify_pid_rb_results.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    by_id = {c["id"]: c for c in data["checks"]}
    return data, by_id


def evidence(legacy_id: str):
    _, by_id = load_legacy()
    require(legacy_id in by_id, f"missing legacy {legacy_id}")
    require(by_id[legacy_id]["status"] == "passed", f"legacy {legacy_id} not passed")
    return by_id[legacy_id]["evidence"]


def _match_atoms(got, expected, atol=1e-12):
    for k in expected:
        if isinstance(expected[k], (int, float)):
            near(got[k], expected[k], atol=atol)
        else:
            require(got[k] == expected[k], f"{k}: {got[k]!r} != {expected[k]!r}")


def unique_gate(n=4000, seed=901):
    rng = np.random.default_rng(seed)
    y = rng.integers(0, 2, size=n)
    r1 = y.copy()
    r2 = rng.integers(0, 2, size=n)
    return joint_from_samples(r1, r2, y, 2, 2, 2)


def xor_gate(n=4000, seed=902):
    rng = np.random.default_rng(seed)
    r1 = rng.integers(0, 2, size=n)
    r2 = rng.integers(0, 2, size=n)
    y = r1 ^ r2
    return joint_from_samples(r1, r2, y, 2, 2, 2)


def and_gate_exact():
    j = np.zeros((2, 2, 2))
    for r1, r2 in itertools.product((0, 1), repeat=2):
        y = r1 & r2
        j[r1, r2, y] = 0.25
    return j


def full_redundancy_copy():
    j = np.zeros((2, 2, 2))
    j[0, 0, 0] = 0.5
    j[1, 1, 1] = 0.5
    return j


def p01_unique_gate():
    expected = evidence("p01_unique_gate")
    j = unique_gate()
    atoms = pid_atoms_williams_beer(j)
    assert_nonnegative_atoms(atoms)
    require(atoms["Red"] < 0.05, f"UNIQUE Red~0, got {atoms['Red']}")
    require(atoms["Unq1"] > 0.8, f"UNIQUE Unq1, got {atoms['Unq1']}")
    require(atoms["Syn"] < 0.05, f"UNIQUE Syn~0, got {atoms['Syn']}")
    _match_atoms(atoms, expected)
    return atoms


def p02_xor_synergy():
    expected = evidence("p02_xor_synergy")
    j = xor_gate()
    atoms = pid_atoms_williams_beer(j)
    assert_nonnegative_atoms(atoms)
    require(atoms["I_R1"] < 0.05 and atoms["I_R2"] < 0.05, "XOR single MI~0")
    require(atoms["Syn"] > 0.9, f"XOR Syn~1, got {atoms['Syn']}")
    require(atoms["Red"] < 0.05, f"XOR Red~0, got {atoms['Red']}")
    _match_atoms(atoms, expected)
    return atoms


def p03_and_and_full_redundancy():
    expected = evidence("p03_and_and_full_redundancy")
    j_and = and_gate_exact()
    atoms_and = pid_atoms_williams_beer(j_and)
    assert_nonnegative_atoms(atoms_and)
    require(atoms_and["Red"] > 0.0, "AND Red>0")
    near(atoms_and["Red"], atoms_and["I_R1"], atol=0.05)
    near(atoms_and["Unq1"], 0.0, atol=1e-8)
    near(atoms_and["Unq2"], 0.0, atol=1e-8)
    j_full = full_redundancy_copy()
    atoms_full = pid_atoms_williams_beer(j_full)
    assert_nonnegative_atoms(atoms_full)
    near(atoms_full["Red"], 1.0, atol=1e-8)
    near(atoms_full["Syn"], 0.0, atol=1e-8)
    near(atoms_full["Unq1"], 0.0, atol=1e-8)
    out = {"AND": atoms_and, "FULL_COPY_RED": atoms_full}
    _match_atoms(out["AND"], expected["AND"])
    _match_atoms(out["FULL_COPY_RED"], expected["FULL_COPY_RED"])
    return out


def p04_nonnegative_atoms():
    expected = evidence("p04_nonnegative_atoms")
    samples = [unique_gate(), xor_gate(), and_gate_exact(), full_redundancy_copy()]
    checked = []
    for j in samples:
        atoms = pid_atoms_williams_beer(j)
        assert_nonnegative_atoms(atoms)
        checked.append({k: atoms[k] for k in ("Red", "Unq1", "Unq2", "Syn")})
    out = {"gates_checked": 4, "atoms": checked}
    require(out["gates_checked"] == expected["gates_checked"], "gates_checked")
    for got, exp in zip(out["atoms"], expected["atoms"]):
        for k in exp:
            near(got[k], exp[k], atol=1e-12)
    return out


def p05_rb0_blackwell():
    expected = evidence("p05_rb0_blackwell")
    j_u = unique_gate(n=8000, seed=905)
    rb_u = rb0_blackwell(j_u)
    require(rb_u < 0.05, f"UNIQUE RB(0)~0, got {rb_u}")
    j_f = full_redundancy_copy()
    rb_f = rb0_blackwell(j_f)
    near(rb_f, 1.0, atol=1e-8)
    j_x = xor_gate(n=8000, seed=906)
    rb_x = rb0_blackwell(j_x)
    require(rb_x < 0.05, f"XOR RB(0)~0, got {rb_x}")
    j_a = and_gate_exact()
    rb_a = rb0_blackwell(j_a)
    require(rb_a > 0.0, "AND RB(0)>0")
    hy = entropy([0.75, 0.25])
    ref = hy - 0.5
    near(rb_a, ref, atol=1e-8)
    out = {
        "UNIQUE_RB0": rb_u,
        "XOR_RB0": rb_x,
        "AND_RB0": rb_a,
        "AND_RB0_exact_ref": ref,
        "FULL_COPY_RB0": rb_f,
        "note": "RB(0)=Blackwell I_cap; I_min Red reported separately in other tests",
        "arxiv": ARXIV_RB,
    }
    for k in (
        "UNIQUE_RB0",
        "XOR_RB0",
        "AND_RB0",
        "AND_RB0_exact_ref",
        "FULL_COPY_RB0",
    ):
        near(out[k], expected[k], atol=1e-12)
    require(out["note"] == expected["note"], "note")
    require(out["arxiv"] == expected["arxiv"], "arxiv")
    return out


def p06_ei_q_beside_pid_smoke():
    expected = evidence("p06_ei_q_beside_pid_smoke")
    P = np.array(
        [
            [1 / 3, 1 / 3, 1 / 3, 0],
            [1 / 3, 1 / 3, 1 / 3, 0],
            [1 / 3, 1 / 3, 1 / 3, 0],
            [0, 0, 0, 1],
        ],
        dtype=float,
    )
    q = np.array([1 / 6, 1 / 6, 1 / 6, 1 / 2])
    ei = ei_q_channel(P, q)
    j = xor_gate(n=2000, seed=916)
    atoms = pid_atoms_williams_beer(j)
    cmp = compare_to_EI_q(P, q, j)
    require(
        "Syn is not" in cmp["claim"] or "beside" in cmp["claim"].lower(),
        "must disclaim EI=Syn",
    )
    require(abs(cmp["EI_q"] - ei) < 1e-12, "EI consistency")
    out = {
        "EI_q": cmp["EI_q"],
        "pid_summary": cmp["pid_summary"],
        "claim": cmp["claim"],
        "canonical_pair": (
            "micro->macro (worked_example_causal_emergence.md style channel for EI_q)"
        ),
        "pid_on": "XOR synergy gate (separate toy; atoms not equated to EI_q)",
    }
    near(out["EI_q"], expected["EI_q"], atol=1e-12)
    for k, v in expected["pid_summary"].items():
        near(out["pid_summary"][k], v, atol=1e-12)
    require(out["claim"] == expected["claim"], "claim")
    require(out["canonical_pair"] == expected["canonical_pair"], "canonical_pair")
    require(out["pid_on"] == expected["pid_on"], "pid_on")
    return out


def p07_arxiv_links():
    expected = evidence("p07_arxiv_links")
    core_path = (
        ROOT
        / "src"
        / "scoped_correspondence"
        / "information_decomposition"
        / "core.py"
    )
    text = core_path.read_text(encoding="utf-8")
    require("1004.2515" in text and "2405.07665" in text, "arxiv ids")
    require("pid-as-ib" in text or "Kolchinsky" in text, "ref impl / Kolchinsky")
    # Legacy script mentions Rosas O-info; core docstring should too for F09 policy
    require(
        "O-info" in text
        or "O-information" in text
        or "Rosas" in text
        or True,  # soft: verify package documents non-use in module doc
        "O-info policy",
    )
    out = {
        "arxiv_wb": ARXIV_WB,
        "arxiv_rb": ARXIV_RB,
        "ref_impl": "github.com/artemyk/pid-as-ib",
    }
    # Ensure core mentions the ref impl string for parity with legacy p07
    if "pid-as-ib" not in text:
        # still pass URLs; add note that package docstring carries Kolchinsky cite
        pass
    require(out["arxiv_wb"] == expected["arxiv_wb"], "wb")
    require(out["arxiv_rb"] == expected["arxiv_rb"], "rb")
    require(out["ref_impl"] == expected["ref_impl"], "ref_impl")
    # Ensure string present in core for documentation parity
    require(
        "pid-as-ib" in text or "artemyk" in text or "2405.07665" in text,
        "core must cite RB source",
    )
    # Force pid-as-ib into evidence match — core header should include it
    require("pid-as-ib" in text, "core.py must mention github.com/artemyk/pid-as-ib")
    require(
        "Rosas" in text or "O-information" in text or "O-info" in text,
        "core.py must mention non-use of Rosas O-information",
    )
    return out


def p08_two_bit_copy():
    """F12: Williams-Beer Red=1 (misleading) beside Blackwell RB(0)=0."""
    rep = two_bit_copy_report()
    near(rep["Red_williams_beer"], 1.0, atol=1e-10)
    near(rep["RB0_blackwell"], 0.0, atol=1e-8)
    require(rep["Red_williams_beer"] == 1.0 or abs(rep["Red_williams_beer"] - 1.0) < 1e-12,
            "Red exactly 1")
    require(abs(rep["RB0_blackwell"]) < 1e-8, "RB0 exactly 0")
    return {
        "Red_williams_beer": rep["Red_williams_beer"],
        "RB0_blackwell": rep["RB0_blackwell"],
        "Unq1": rep["Unq1"],
        "Unq2": rep["Unq2"],
        "Syn": rep["Syn"],
        "I_joint": rep["I_joint"],
        "claim": rep["claim"],
        "mapping": "pid_redundancy_bottleneck.md / F12 TWO_BIT_COPY",
        "expected": {"Red_williams_beer": 1.0, "RB0_blackwell": 0.0},
    }


CHECKS = [
    ("p01_unique_gate", p01_unique_gate),
    ("p02_xor_synergy", p02_xor_synergy),
    ("p03_and_and_full_redundancy", p03_and_and_full_redundancy),
    ("p04_nonnegative_atoms", p04_nonnegative_atoms),
    ("p05_rb0_blackwell", p05_rb0_blackwell),
    ("p06_ei_q_beside_pid_smoke", p06_ei_q_beside_pid_smoke),
    ("p07_arxiv_links", p07_arxiv_links),
    ("p08_two_bit_copy", p08_two_bit_copy),
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).with_name(
            "verify_information_decomposition_core_results.json"
        ),
    )
    args = parser.parse_args()
    results = []
    for name, fn in CHECKS:
        try:
            ev = fn()
            results.append({"id": name, "status": "passed", "evidence": ev})
        except Exception as exc:
            results.append(
                {"id": name, "status": "failed", "error": f"{type(exc).__name__}: {exc}"}
            )
    passed = sum(r["status"] == "passed" for r in results)
    failed = [r["id"] for r in results if r["status"] != "passed"]
    report_obj = {
        "milestone": "M7_information_decomposition_core",
        "kind": "Legacy equivalence p01–p07 + F12 TWO_BIT_COPY",
        "generated_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "python": platform.python_version(),
        "numpy": np.__version__,
        "scipy": __import__("scipy").__version__,
        "count": len(results),
        "passed": passed,
        "failed": len(failed),
        "legacy_results": "verification/verify_pid_rb_results.json",
        "measure_basis": "Williams-Beer I_min",
        "redundancy_modern": "Kolchinsky RB / Blackwell I_cap (RB(0))",
        "arxiv": {"williams_beer": ARXIV_WB, "kolchinsky_rb": ARXIV_RB},
        "checks": results,
    }
    args.output.write_text(
        json.dumps(report_obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    summary = {
        "count": report_obj["count"],
        "passed": report_obj["passed"],
        "failed": failed,
        "report": str(args.output.resolve()),
    }
    print(json.dumps(summary, ensure_ascii=False))
    raise SystemExit(0 if not failed else 1)


if __name__ == "__main__":
    main()
