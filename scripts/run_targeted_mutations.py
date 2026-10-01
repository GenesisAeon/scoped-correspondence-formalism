"""Targeted mutation run (Paket J3, SCOPE_COMPOSITION_EVIDENCE_ROADMAP.md).

Plan ``SCF_SCOPE_COMPOSITION_EVIDENCE_IMPLEMENTATION_PLAN.md`` section 9:
show that important verification scripts actually detect relevant errors.
This is NOT a global mutation of all files and NOT a test framework: a
small, explicit registry of hand-chosen mutants, each with the verification
script(s) expected to catch it and the reason why.

Every mutant runs on a TEMPORARY COPY of ``src/``, ``verification/`` and
``data/`` -- never in the working tree. The script hashes every mutated
source file in the real repository before and after the run and fails if
anything changed.

Outcome per mutant (plan section 9):

- ``killed``     -- at least one target script failed on the mutant.
                    ``kill_kind`` separates ``assertion`` (a FAIL line: a
                    content check caught it) from ``error`` (only an
                    exception/crash -- reported, but weaker evidence).
- ``survived``   -- all target scripts still passed.
- ``invalid``    -- the snippet was not found exactly once, the mutated file
                    does not compile, or the UNMUTATED baseline of a target
                    already fails. Never counted as a detected error.
- ``timeout``    -- a target exceeded the time limit.
- ``equivalent_or_unresolved`` -- survived, but registered in advance as
                    (possibly) equivalent with a stated reason. Excluded
                    from the kill-ratio denominator, listed separately.

A high kill ratio is NOT a completeness guarantee.

Usage:
    python scripts/run_targeted_mutations.py [--only ID ...] [--package J1]
        [--output verification/targeted_mutations_report.json] [--timeout 300]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

REPO = Path(__file__).resolve().parents[1]
COPY_DIRS = ("src", "verification", "data")


@dataclass(frozen=True)
class Mutant:
    id: str
    package: str  # package whose checks are expected to kill it
    file: str  # repo-relative path
    find: str
    replace: str
    targets: Tuple[str, ...]  # verify_*.py names
    expected: str  # which plan error class / what should catch it
    equivalent_reason: Optional[str] = None  # set only if registered as possibly equivalent


FC = "src/scoped_correspondence/validation/forecast_comparison.py"
DC = "src/scoped_correspondence/dimensions/core.py"
DP = "src/scoped_correspondence/dimensions/pi_groups.py"
CONTRACT = "src/scoped_correspondence/correspondence/contract.py"
CONFORMAL = "src/scoped_correspondence/validation/conformal.py"
EB = "src/scoped_correspondence/closure/error_bounds.py"

#: The registry. Plan-mandated classes (section 9): invert an inequality;
#: drop the time factor in T4; drop a Lipschitz factor (J4); drop the test
#: point mass in conformal; confuse the factor two between TV and L1; bypass
#: scope compatibility (J4). The last ones are added with their packages.
MUTANTS: Tuple[Mutant, ...] = (
    # --- plan-mandated classes on EXISTING code -----------------------------
    Mutant("t4_time_factor_removed", "J3", CONTRACT,
           "composed = d_tkj(y) * r_ji + float(a_ji(x)) * r_kj",
           "composed = d_tkj(y) * r_ji + r_kj",
           ("verify_correspondence_core.py", "verify_metamorphic_relations.py"),
           "plan §9: Zeitfaktor in T4 entfernen"),
    Mutant("conformal_test_point_mass_dropped", "J3", CONFORMAL,
           "k = int(math.ceil((n + 1) * (1.0 - float(alpha))))",
           "k = int(math.ceil(n * (1.0 - float(alpha))))",
           ("verify_conformal_prediction_core.py",),
           "plan §9: Testpunktmasse bei Conformal weglassen (n+1 -> n)"),
    Mutant("tv_l1_factor_two", "J3", EB,
           "        return float(0.5 * l1_bound)",
           "        return float(l1_bound)",
           ("verify_error_bounds_core.py",),
           "plan §9: Faktor zwei bei TV/L1 verwechseln"),
    Mutant("tv_comparison_inequality_inverted", "J3", EB,
           "    leq = michel_tv <= elementary_tv + 1e-12",
           "    leq = michel_tv >= elementary_tv - 1e-12",
           ("verify_error_bounds_core.py",),
           "plan §9: Ungleichung umdrehen"),
    # --- J1 ------------------------------------------------------------------
    Mutant("j1_bartlett_weight_removed", "J1", FC, "weight = 1 - Fraction(l, lag + 1)", "weight = 1",
           ("verify_forecast_comparison.py",), "J-C01 exact HAC value"),
    Mutant("j1_degenerate_guard_removed", "J1", FC, "            if degenerate:", "            if False:",
           ("verify_forecast_comparison.py",), "no p-value / DM for degenerate variance"),
    Mutant("j1_applicability_bypassed", "J1", FC, "        if not reasons:\n            V =", "        if True:\n            V =",
           ("verify_forecast_comparison.py",), "inference gates"),
    Mutant("j1_loss_difference_sign_swapped", "J1", FC, "d = [x - y for x, y in zip(la, lb)]", "d = [y - x for x, y in zip(la, lb)]",
           ("verify_forecast_comparison.py",), "sign convention A-B"),
    Mutant("j1_missing_partner_dropped", "J1", FC,
           'excluded.append(PairingIssue(origin, step, "missing_partner_in_model_b"))', "pass",
           ("verify_forecast_comparison.py",), "no silent drop of unpaired points"),
    Mutant("j1_observed_mismatch_ignored", "J1", FC, "        if a.observed != b.observed:", "        if False:",
           ("verify_forecast_comparison.py",), "wrong pairing is an input error"),
    Mutant("j1_series_too_short_inverted", "J1", FC,
           "        if n < applicability.min_series_length:", "        if n > applicability.min_series_length:",
           ("verify_forecast_comparison.py",), "plan §9: Ungleichung umdrehen (Mindestlänge)"),
    # --- J2 ------------------------------------------------------------------
    Mutant("j2_add_dimension_check_removed", "J2", DC, "            if dl != dr:", "            if False:",
           ("verify_dimensional_analysis.py",), "adding different dimensions"),
    Mutant("j2_func_arg_check_removed", "J2", DC, "            if d is not None and not d.is_dimensionless:", "            if False:",
           ("verify_dimensional_analysis.py",), "exp/log arguments dimensionless"),
    Mutant("j2_pow_ignores_exponent", "J2", DC, "            return (None if d is None else d ** p), None", "            return d, None",
           ("verify_dimensional_analysis.py",), "rational exponents"),
    Mutant("j2_kind_warning_removed", "J2", DC, "            if kl and kr and kl != kr:", "            if False:",
           ("verify_dimensional_analysis.py",), "energy vs torque warning"),
    Mutant("j2_affine_guard_removed", "J2", DC, "    if unit.is_affine:\n        raise", "    if False:\n        raise",
           ("verify_dimensional_analysis.py",), "affine scales are not multiplicative"),
    Mutant("j2_rescale_sign_flipped", "J2", DC, "        v *= fac ** int(e)", "        v *= fac ** (-int(e))",
           ("verify_dimensional_analysis.py", "verify_metamorphic_relations.py"), "J-C04 unit change"),
    Mutant("j2_nullspace_sign_dropped", "J2", DP, "            v[pc] = -rref[row_i][f]", "            v[pc] = rref[row_i][f]",
           ("verify_dimensional_analysis.py",), "J-C03 null space"),
    Mutant("j2_span_check_ignores_joint_rank", "J2", DP, "    return ra == rb == rab", "    return ra == rb",
           ("verify_dimensional_analysis.py",), "basis change compares spans"),
)


@dataclass
class Outcome:
    id: str
    package: str
    file: str
    expected: str
    targets: List[str]
    status: str
    kill_kind: Optional[str] = None
    detail: List[str] = field(default_factory=list)
    seconds: float = 0.0


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _run_target(root: Path, script: str, timeout: float) -> Tuple[str, List[str]]:
    """Returns (result, lines) with result in pass|fail|error|timeout."""
    try:
        p = subprocess.run([sys.executable, str(root / "verification" / script)], cwd=root / "verification",
                           capture_output=True, text=True, timeout=timeout,
                           # PYTHONDONTWRITEBYTECODE: a same-length mutation written within the
                           # same second as the baseline run would otherwise pass Python's
                           # mtime+size pyc check and execute the STALE, unmutated bytecode
                           # (found by verify_targeted_mutation_runner.py) -- a false "survived".
                           env={**__import__("os").environ, "PYTHONPATH": str(root / "src"), "PYTHONIOENCODING": "utf-8",
                                "PYTHONDONTWRITEBYTECODE": "1"})
    except subprocess.TimeoutExpired:
        return "timeout", ["TIMEOUT"]
    out = (p.stdout or "") + (p.stderr or "")
    if p.returncode == 0:
        return "pass", []
    fails = [l for l in out.splitlines() if l.startswith("FAIL")]
    tail = [l for l in out.strip().splitlines()[-3:]]
    # "error" means ONLY an uncaught exception (a crash). Any other nonzero
    # exit is a failure the script itself reported -- older verify scripts
    # report failures as JSON ("failed": [...]) rather than FAIL lines.
    if "Traceback (most recent call last)" in out and not fails:
        return "error", tail
    return "fail", fails[:3] or tail


def run(mutants: Sequence[Mutant], timeout: float, repo: Path = REPO) -> Dict[str, object]:
    files = sorted({m.file for m in mutants if (repo / m.file).exists()})
    before = {f: _sha(repo / f) for f in files}
    tmp = Path(tempfile.mkdtemp(prefix="scf_mut_"))
    try:
        for d in COPY_DIRS:
            if (repo / d).exists():
                shutil.copytree(repo / d, tmp / d, ignore=shutil.ignore_patterns("__pycache__"))
        baseline: Dict[str, str] = {}
        for t in sorted({t for m in mutants for t in m.targets}):
            if not (tmp / "verification" / t).exists():
                baseline[t] = "missing"
                continue
            baseline[t], _ = _run_target(tmp, t, timeout)
        outcomes: List[Outcome] = []
        for m in mutants:
            start = time.monotonic()
            o = Outcome(m.id, m.package, m.file, m.expected, list(m.targets), status="invalid")
            path = tmp / m.file
            orig = path.read_text(encoding="utf-8") if path.exists() else ""
            bad_base = [t for t in m.targets if baseline.get(t) != "pass"]
            if not path.exists():
                o.detail = [f"file not found: {m.file}"]
            elif orig.count(m.find) != 1:
                o.detail = [f"snippet found {orig.count(m.find)} times (need exactly 1)"]
            elif bad_base:
                o.detail = [f"baseline of target not passing: {t}={baseline.get(t)}" for t in bad_base]
            else:
                mutated = orig.replace(m.find, m.replace)
                try:
                    compile(mutated, str(path), "exec")
                except SyntaxError as e:
                    o.detail = [f"mutated file does not compile: {e}"]
                else:
                    path.write_text(mutated, encoding="utf-8")
                    try:
                        results = [(t,) + _run_target(tmp, t, timeout) for t in m.targets]
                    finally:
                        path.write_text(orig, encoding="utf-8")
                    kinds = [r for _, r, _ in results]
                    o.detail = [f"{t}: {r} {lines[:1]}" for t, r, lines in results]
                    if "fail" in kinds:
                        o.status, o.kill_kind = "killed", "assertion"
                    elif "error" in kinds:
                        o.status, o.kill_kind = "killed", "error"
                    elif "timeout" in kinds:
                        o.status = "timeout"
                    elif m.equivalent_reason:
                        o.status = "equivalent_or_unresolved"
                        o.detail.append(f"registered reason: {m.equivalent_reason}")
                    else:
                        o.status = "survived"
            o.seconds = round(time.monotonic() - start, 2)
            outcomes.append(o)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    after = {f: _sha(repo / f) for f in files}
    if before != after:
        raise SystemExit("ABORT: a source file in the real working tree changed during the mutation run")
    counts: Dict[str, int] = {}
    for o in outcomes:
        counts[o.status] = counts.get(o.status, 0) + 1
    killed = counts.get("killed", 0)
    survived = counts.get("survived", 0)
    return {
        "plan": "SCF_SCOPE_COMPOSITION_EVIDENCE_IMPLEMENTATION_PLAN.md section 9",
        "python": platform.python_version(),
        "n_mutants": len(outcomes),
        "counts": counts,
        "killed_by_assertion": sum(1 for o in outcomes if o.kill_kind == "assertion"),
        "killed_by_error_only": sum(1 for o in outcomes if o.kill_kind == "error"),
        "kill_ratio_excluding_equivalent": None if killed + survived == 0 else f"{killed}/{killed + survived}",
        "working_tree_unchanged": True,
        "note": "A high kill ratio is not a completeness guarantee; invalid/timeout are not detections.",
        "baseline_targets": baseline,
        "mutants": [o.__dict__ for o in outcomes],
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--only", nargs="*", default=None, help="mutant ids to run")
    ap.add_argument("--package", default=None, help="only mutants of this package")
    ap.add_argument("--timeout", type=float, default=300.0)
    ap.add_argument("--output", type=Path, default=None)
    args = ap.parse_args()
    sel = [m for m in MUTANTS if (args.only is None or m.id in args.only) and (args.package is None or m.package == args.package)]
    if not sel:
        print("no mutants selected")
        return 2
    report = run(sel, args.timeout)
    for o in report["mutants"]:
        print(f"{o['status']:<26} {o['kill_kind'] or '':<10} {o['id']}")
    print(json.dumps({k: report[k] for k in ("n_mutants", "counts", "killed_by_assertion", "killed_by_error_only", "kill_ratio_excluding_equivalent")}, indent=2))
    if args.output:
        args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return 0 if report["counts"].get("survived", 0) == 0 and report["counts"].get("invalid", 0) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
