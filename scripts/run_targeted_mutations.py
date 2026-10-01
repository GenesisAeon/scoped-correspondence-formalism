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
COPY_DIRS = ("src", "verification", "data", "scripts")  # scripts: CLI mutants (MU7) and verify scripts that call a CLI


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
COMP = "src/scoped_correspondence/correspondence/composition.py"
DOM = "src/scoped_correspondence/correspondence/domains.py"
RI = "src/scoped_correspondence/assurance/rational_intervals.py"
SC = "src/scoped_correspondence/assurance/scope_certification.py"
CA = "src/scoped_correspondence/closure/contract_adapter.py"
EL = "src/scoped_correspondence/identifiability/exact_linear.py"
SR = "src/scoped_correspondence/identifiability/structural_reports.py"
MK = "src/scoped_correspondence/muonium/kinematics.py"
MF = "src/scoped_correspondence/muonium/forward.py"
ML = "src/scoped_correspondence/muonium/likelihood.py"
MI = "src/scoped_correspondence/muonium/identifiability.py"
MD = "src/scoped_correspondence/muonium/design.py"
ME = "src/scoped_correspondence/muonium/evidence.py"
MP = "scripts/run_muonium_pilot.py"

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
    # --- J4 (activates the remaining plan-mandated classes) -------------------
    Mutant("j4_lipschitz_factor_removed", "J4", COMP,
           "        flow = l2.lipschitz.constant * l1.flow_error_bound + l2.flow_error_bound",
           "        flow = l1.flow_error_bound + l2.flow_error_bound",
           ("verify_correspondence_contracts.py",), "plan §9: Lipschitzfaktor entfernen"),
    Mutant("j4_scope_compatibility_bypassed", "J4", COMP, "    mism = compatibility(l1, l2)\n    if mism:",
           "    mism = compatibility(l1, l2)\n    if False:",
           ("verify_correspondence_contracts.py",), "plan §9: Scope-Verträglichkeit umgehen"),
    Mutant("j4_time_factor_added_not_multiplied", "J4", COMP, "time_factor=c1 * c2,", "time_factor=c1 + c2,",
           ("verify_correspondence_contracts.py",), "J-C06 composite clock factor"),
    Mutant("j4_horizon_scaled_wrong_way", "J4", COMP, "    horizon = min(l1.horizon, l2.horizon / c1)",
           "    horizon = min(l1.horizon, l2.horizon * c1)", ("verify_correspondence_contracts.py",), "J-C06 horizon"),
    Mutant("j4_delta2_multiplied_by_c1", "J4", COMP,
           "        flow = l2.lipschitz.constant * l1.flow_error_bound + l2.flow_error_bound",
           "        flow = l2.lipschitz.constant * l1.flow_error_bound + c1 * l2.flow_error_bound",
           ("verify_correspondence_contracts.py",), "plan §10.3: delta2 evaluated at c1 t, not multiplied by c1"),
    Mutant("j4_negative_scale_not_swapped", "J4", DOM, "            if a < 0:\n                l, h = h, l", "            if False:\n                l, h = h, l",
           ("verify_correspondence_contracts.py",), "negative scales"),
    Mutant("j4_preimage_ignores_first_domain", "J4", DOM, "            bounds[j][0] = max(bounds[j][0], l)", "            bounds[j][0] = l",
           ("verify_correspondence_contracts.py",), "D12 = D1 ∩ T1^-1(D2)"),
    Mutant("j4_sampled_bound_not_downgraded", "J4", COMP,
           '    ranks = [(_EVIDENCE_ORDER.index(k) if k in _EVIDENCE_ORDER else 0) for k in kinds]\n    return _EVIDENCE_ORDER[min(ranks)]',
           '    ranks = [(_EVIDENCE_ORDER.index(k) if k in _EVIDENCE_ORDER else 0) for k in kinds]\n    return _EVIDENCE_ORDER[max(ranks)]',
           ("verify_correspondence_contracts.py",), "weakest component evidence wins"),
    Mutant("j4_lipschitz_segment_coverage_ignored", "J4", COMP,
           "    elif l2.lipschitz is None or not l2.lipschitz.covers_connecting_segments:",
           "    elif l2.lipschitz is None:", ("verify_correspondence_contracts.py",), "certificate must cover connecting segments"),
    # --- J5 -------------------------------------------------------------------
    Mutant("j5_interval_mul_misses_products", "J5", RI, "        return Interval(min(p), max(p))",
           "        return Interval(min(p[0], p[3]), max(p[0], p[3]))", ("verify_validated_scopes.py",),
           "enclosure must contain the image (all four endpoint products)"),
    Mutant("j5_split_drops_right_half", "J5", SC, "            queue.extend(_split(b))\n    cert", "            queue.append(_split(b)[0])\n    cert",
           ("verify_validated_scopes.py",), "partition must cover the domain"),
    Mutant("j5_point_check_skipped", "J5", SC, "            if not _ok(v, eps, side):", "            if False:",
           ("verify_validated_scopes.py",), "counterexamples must be reported"),
    Mutant("j5_singularity_ignored", "J5", SC, "            except UndefinedAtPoint:\n                return",
           "            except UndefinedAtPoint:\n                continue\n                return", ("verify_validated_scopes.py",),
           "undefined input is a separate result"),
    Mutant("j5_recheck_volume_ignored", "J5", SC, "    if axes and total != _volume(cert.domain, axes):", "    if False:",
           ("verify_validated_scopes.py",), "re-check must detect a missing partition box"),
    Mutant("j5_even_power_not_tight", "J5", RI, "        return Interval(0, max(a, b))", "        return Interval(-max(a, b), max(a, b))",
           ("verify_validated_scopes.py",), "x^2 on [-1,2] is [0,4]"),
    Mutant("j5_lower_side_uses_upper_test", "J5", SC, "        if (enc.hi <= eps) if side == \"upper\" else (enc.lo >= eps):",
           "        if (enc.hi <= eps):", ("verify_validated_scopes.py",), "side of the claim"),
    # --- J11 ------------------------------------------------------------------
    Mutant("j11_inf_norm_uses_columns", "J11", CA, "    r_inf = max(sum(abs(v) for v in row) for row in resid)  # max absolute ROW sum",
           "    r_inf = max(sum(abs(resid[i][j]) for i in range(len(resid))) for j in range(len(resid[0])))",
           ("verify_reduction_contracts.py",), "matrix inf-norm is the max absolute ROW sum"),
    Mutant("j11_tv_not_halved", "J11", CA, "    exact_bound = l1 / 2 if contract.norm == \"TV\" else l1",
           "    exact_bound = l1", ("verify_reduction_contracts.py",), "plan §9/§17: TV/L1 factor two"),
    Mutant("j11_initial_error_dropped", "J11", CA, "    l1 = e0 + k * r_inf", "    l1 = k * r_inf",
           ("verify_reduction_contracts.py",), "initial error enters the bound"),
    Mutant("j11_orientation_check_removed", "J11", CA,
           "            bad.append(f\"{label} matrix is not {'a generator' if contract.continuous_time else 'row-stochastic'}{hint}\")",
           "            pass", ("verify_reduction_contracts.py",), "orientation of all matrices"),
    Mutant("j11_tv_lifting_guard_removed", "J11", CA, "    if contract.norm == \"TV\" and not (lifting_stochastic and p0_prob):",
           "    if False:", ("verify_reduction_contracts.py",), "stochastic lifting condition for TV"),
    Mutant("j11_float_inputs_promoted", "J11", CA, "    if not _all_exact(Pi, A, P, pi0, p0):", "    if False:",
           ("verify_reduction_contracts.py",), "numerical bound vs rigorous proof"),
    Mutant("j11_hoelder_constant_wrong", "J11", CA, "    L = max(abs(w) for w in f) * (2 if contract.norm == \"TV\" else 1)",
           "    L = sum(abs(w) for w in f) / len(f)", ("verify_reduction_contracts.py",), "observation Lipschitz certificate"),
    # --- J6 -------------------------------------------------------------------
    Mutant("j6_rowspace_test_inverted", "J6", EL, "    return exact_rank(Aq + [cq]) == exact_rank(Aq)",
           "    return exact_rank(Aq + [cq]) > exact_rank(Aq)", ("verify_structural_identifiability.py",),
           "c identifiable iff c in the row space"),
    Mutant("j6_inconsistent_observation_accepted", "J6", EL, "        if M[i][p] != 0:\n            return None", "        if False:\n            return None",
           ("verify_structural_identifiability.py",), "observation outside the image = empty fibre"),
    Mutant("j6_domain_restriction_assumed", "J6", EL, '            restriction = "not_evaluated"', '            restriction = "exact"',
           ("verify_structural_identifiability.py",), "restriction for >1-dim null space is not assumed"),
    Mutant("j6_negative_direction_not_swapped", "J6", EL, "                a, c = min(a, c), max(a, c)", "                pass",
           ("verify_structural_identifiability.py",), "line-box intersection with negative direction"),
    Mutant("j6_witness_not_checked", "J6", SR, "    same = (c2 * x02 == y0) and (-k * c2 * x02 == dy0)", "    same = True",
           ("verify_structural_identifiability.py",), "witness pair must be verified exactly",
           equivalent_reason=("(c/lam)*(lam*x0) == c*x0 holds algebraically for EVERY lam > 0, and positivity is "
                              "enforced before; inside the J-C12 family the exact check cannot evaluate to False, "
                              "so 'always True' is behaviourally equivalent (the check documents, it cannot fail)")),
    # --- MU1-MU7 ----------------------------------------------------------------
    Mutant("mu1_single_path_factor_used_as_relative", "MU1", MK, "    return a * T * T\n", "    return a * T * T / 2\n",
           ("verify_muonium_kinematics.py",), "relative displacement aT^2 vs single path aT^2/2"),
    Mutant("mu1_survival_one_transit", "MU1", MK, "    return math.exp(-2 * float(geom.L) / (float(geom.v) * float(t_eff)))",
           "    return math.exp(-float(geom.L) / (float(geom.v) * float(t_eff)))", ("verify_muonium_kinematics.py",), "survival over 2T"),
    Mutant("mu1_unequal_times_accepted", "MU1", MK, "    if t1 != t2:", "    if False:", ("verify_muonium_kinematics.py",), "equal flight times scope"),
    Mutant("mu1_eta_zero_denominator_invented", "MU1", MK, "    if den == 0:\n        return None", "    if den == 0:\n        return 0",
           ("verify_muonium_kinematics.py",), "eta undefined, not invented"),
    Mutant("mu2_survival_ignored_in_weights", "MU2", MF, "        return [c.weight * c.transmission * c.efficiency * self.survival(c.v) for c in self.classes]",
           "        return [c.weight * c.transmission * c.efficiency for c in self.classes]", ("verify_muonium_forward.py",),
           "detected mixture includes survival"),
    Mutant("mu2_phase_reported_for_zero_contrast", "MU2", MF, "        if F is None or abs(F) <= tol:\n            return None",
           "        if F is None:\n            return None", ("verify_muonium_forward.py",), "no arg(0)"),
    Mutant("mu2_transmission_guard_removed", "MU2", MF, "                if c.transmission * (1 + c.contrast) > 1 + 1e-15:", "                if False:",
           ("verify_muonium_forward.py",), "A (1 + C) <= 1"),
    Mutant("mu2_bin_time_not_applied", "MU2", MF, "            out.append(b.t * self.background + b.t * self.rate * W * (1 + mod))",
           "            out.append(self.background + self.rate * W * (1 + mod))", ("verify_muonium_forward.py",), "per-bin measurement times"),
    Mutant("mu3_artificial_floor", "MU3", ML, "            if nj > 0:\n                return math.inf", "            if nj > 0:\n                lj = 1e-300",
           ("verify_muonium_likelihood.py",), "no artificial positive floor"),
    Mutant("mu3_zero_count_deviance_term", "MU3", ML, "            total += 2 * lj\n", "            total += lj\n",
           ("verify_muonium_likelihood.py",), "zero-count deviance term 2 lambda"),
    Mutant("mu3_modes_collapsed", "MU3", ML, "            modes.append([r])", "            modes.append([r]) if not modes else modes[0].append(r)",
           ("verify_muonium_likelihood.py",), "all modes reported"),
    Mutant("mu3_noninteger_counts_accepted", "MU3", ML,
           "        if isinstance(n, bool) or not isinstance(n, (int, np.integer)) or n < 0:",
           "        if isinstance(n, bool) or n < 0:", ("verify_muonium_likelihood.py",), "raw integer counts only"),
    Mutant("mu4_parity_odd_dropped", "MU4", MI, '    odd = sorted(k for k, v in parities.items() if v == "odd")', "    odd = []",
           ("verify_muonium_identifiability.py",), "odd bias stays with gravity"),
    Mutant("mu4_calibration_linear", "MU4", MI, "    return (1 + e) ** 2", "    return 1 + 2 * e",
           ("verify_muonium_identifiability.py",), "(1+e)^2 exactly"),
    Mutant("mu5_scan_information_wrong_trig", "MU5", MD, "        I += n * C * C * math.sin(a + phi) ** 2 / lam_rel",
           "        I += n * C * C * math.cos(a + phi) ** 2 / lam_rel", ("verify_muonium_design.py",), "Fisher information of the scan"),
    Mutant("mu5_pseudo_inverse", "MU5", MD, "    cov = None if singular else tuple(tuple(float(x) for x in row) for row in np.linalg.inv(M))",
           "    cov = tuple(tuple(float(x) for x in row) for row in np.linalg.pinv(M))", ("verify_muonium_design.py",), "no pseudo-inverse"),
    Mutant("mu5_budget_decay_ignored", "MU5", MD, '    N = N0 * math.exp(-2 * T / tau) if budget == "incoming_atoms" else N0', "    N = N0",
           ("verify_muonium_design.py",), "named budget: T_opt = 2 tau"),
    Mutant("mu5_bound_touch_hidden", "MU5", MD, "    touches = inside[0] == 0 or inside[-1] == len(grid) - 1", "    touches = False",
           ("verify_muonium_design.py",), "intervals ending at search bounds are flagged"),
    Mutant("mu6_synthetic_labelled_empirical", "MU6", ME, '    "synthetic_measurement": ("numerical_sample", "synthetic_only"),',
           '    "synthetic_measurement": ("empirical_evaluation", "evaluated_on_declared_data"),', ("verify_muonium_evidence.py",),
           "synthetic results are not empirical"),
    Mutant("mu6_real_data_marked_passed", "MU6", ME, '    return {"check": "muonium_real_beam_data", "result": "skipped",',
           '    return {"check": "muonium_real_beam_data", "result": "passed",', ("verify_muonium_evidence.py", "verify_muonium_pilot_cli.py"),
           "a skipped data check is never passed"),
    Mutant("mu7_headline_overclaims", "MU7", MP, '    out["headline"] = f"synthetic {scenario} scenario of an idealised model -- no statement about measured muonium gravity"',
           '    out["headline"] = f"Einstein widerlegt? synthetic {scenario}"', ("verify_muonium_pilot_cli.py",), "no overclaiming headline"),
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
