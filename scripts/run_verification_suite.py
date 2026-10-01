"""Checked-in unified verification entry point.

Runs the `verify_*.py` scripts under `verification/` against the real
working repo (not a snapshot), grouped into three categories per Astra's
2026-09-24 capability-assessment recommendation
(`prompts/Answers/nicht_stationäre_Treiber/SCF_Faehigkeiten_und_Ausbauplan_2026-09-24.md`,
Priority 0): "mathematische Prüfungen, Datenprüfungen und Linkprüfung
dürfen getrennte Befehle haben."

- ``math``  — scripts that check analytic/synthetic examples only.
- ``data``  — scripts that load a real dataset under ``data/`` (identified
  by referencing the shared provenance manifest or a known real-data file;
  see `docs/real_data_provenance.md`).
- ``links`` — a lightweight internal-link checker over all tracked
  Markdown files (relative links must resolve to an existing file; bare
  ``http(s)`` links are only counted, not fetched).
- ``all``   — math + data (default). Does not include ``links`` by
  default since it checks a different kind of thing (documentation
  hygiene, not model correctness); request it explicitly.

This is the checked-in replacement for the previously untracked
`audit_review/run_all_local.py` (that script and its whole directory
remain gitignored scratch output; this one is the source of truth and is
also what CI runs).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
import urllib.parse
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
VER = REPO / "verification"

# A verify_*.py script is classified "data" if it references a real,
# externally-sourced dataset (see docs/real_data_provenance.md) rather than
# only synthetic/analytic examples.
_DATA_MARKERS = (
    "real_data",
    "real_data_manifest",
    "data/cygnus",
    "data/owid",
    "data/noaa",
    "data/usgs",
    "mauna_loa",
    "owid",
    "jhu",
)

# Explicit per-script category registration (DOMAIN_EXPANSION_ROADMAP.md Paket
# B1, response to SCF_Review_fcc9a43.md finding R6: "keine explizite
# Registrierung der neuen Testgruppen"). Checked BEFORE the text-marker
# heuristic below, so a future edit that happens to add/remove a marker
# substring in one of these files cannot silently reclassify it. Every
# verify_*.py script added in the domain-expansion round is listed here even
# where the heuristic would already classify it correctly -- registration is
# explicit, not merely "happens to work".
_EXPLICIT_CATEGORY = {
    "verify_queueing.py": "math",
    "verify_queueing_first_passage.py": "math",
    "verify_queueing_pilot.py": "math",
    "verify_linear_reservoirs.py": "math",
    "verify_first_passage_diffusion.py": "math",
    "verify_capacity_degradation.py": "math",
    # Runs entirely against a synthetic fixture -- no real NASA data or network
    # access, despite the module it tests being about real-world battery data.
    "verify_battery_aging_pilot.py": "math",
    "verify_cooperative_agents_pilot.py": "math",
    # Runs entirely against a synthetic (exact-recovery) generating process and
    # a local HTTP test server -- no real CAMELS-DE data or external network
    # access, despite testing modules that are USED for a real data pilot
    # (see docs/hydrology_pilot.md for the real, manually-reproduced results).
    "verify_hydrology_pilot.py": "math",
    "verify_http_range_reader.py": "math",
    # Purely synthetic control cases and cross-checks against already-verified
    # closed-form reservoir formulas -- no real CAMELS-DE data or network access,
    # despite connecting to the same module used for a real data pilot (see
    # docs/hydrology_state_estimation.md for the real, manually-reproduced results).
    "verify_linear_state_estimation.py": "math",
    "verify_hydrology_state_estimation.py": "math",
    "verify_controlled_correspondence.py": "math",
    "verify_phase_type_delays.py": "math",
    "verify_distributed_delay_pilot.py": "math",
    "verify_competing_first_passage.py": "math",
    "verify_resource_network_control.py": "math",
    "verify_resource_network_pilot.py": "math",
    "verify_sequential_information_pilot.py": "math",
    # G1 (GALAXY_DYNAMICS_ROADMAP.md): purely analytic/synthetic profile
    # checks against independent scipy.integrate.quad routes -- no real
    # SPARC data (that arrives only with G4/G5).
    "verify_galaxy_profiles.py": "math",
    "verify_galaxy_homology.py": "math",
    "verify_galaxy_observation_maps.py": "math",
    "verify_sparc_adapter.py": "math",
    # Deliberately "data": looks for the real, license-unresolved SPARC
    # files at a documented LOCAL-ONLY path (never committed, see
    # docs/sparc_data_provenance.md) and skips cleanly (exit 0, each
    # check marked "skipped") when they are absent -- Standard-CI never
    # needs them.
    "verify_sparc_real_local.py": "data",
    "verify_galaxy_pilot.py": "math",
    # H0-H7 (EPISTEMIC_AUDIT_ROADMAP.md): purely finite/analytic/synthetic
    # control cases (K1-K8) -- no real dataset of any kind, including H6b's
    # galaxy example (synthetic Burkert/NFW profiles, the same ones G1
    # already classifies as "math" above).
    "verify_epistemic_finite.py": "math",
    "verify_epistemic_supports.py": "math",
    "verify_epistemic_identification.py": "math",
    "verify_epistemic_decisions.py": "math",
    "verify_epistemic_buffer_pilot.py": "math",
    "verify_epistemic_adapters.py": "math",
    "verify_epistemic_reporting.py": "math",
    # J1 (SCOPE_COMPOSITION_EVIDENCE_ROADMAP.md): exact/synthetic paired
    # forecast comparison checks (J-C01, J-C02, gates, pairing) -- no real data.
    "verify_forecast_comparison.py": "math",
    # J1 real-data adapter: reads data/noaa_global_temp_anomaly_1880_2025.csv
    # (hash-checked against data/real_data_manifest.json).
    "verify_forecast_comparison_noaa.py": "data",
    # J2: exact dimension checks / Buckingham-Pi; reservoir and galaxy
    # connections are symbolic or synthetic -- no real dataset.
    "verify_dimensional_analysis.py": "math",
    # J3: metamorphic relations (synthetic/exact) and the mutation-runner
    # self-test on a throw-away toy repository. The targeted mutation run
    # itself (scripts/run_targeted_mutations.py) is deliberately NOT part of
    # the suite -- every mutant re-runs whole verify scripts.
    "verify_metamorphic_relations.py": "math",
    "verify_targeted_mutation_runner.py": "math",
    # J4: exact domains, functional contracts, typed composition.
    "verify_correspondence_contracts.py": "math",
    # J5: exact rational interval certification over boxes.
    "verify_validated_scopes.py": "math",
    # J11: existing Michel-Siegle reduction bounds as contracts (exact
    # rational examples incl. closure.error_bounds.paper_example_matrices).
    "verify_reduction_contracts.py": "math",
    # J6: exact affine / analytic structural identifiability reports.
    "verify_structural_identifiability.py": "math",
    # MU1-MU7 (MUONIUM_GRAVITY_ROADMAP.md): idealised model, synthetic
    # counts and analytic counterexamples only -- the real beam data
    # (MU-S5, license InC-NC) is deferred and never read here.
    "verify_muonium_kinematics.py": "math",
    "verify_muonium_forward.py": "math",
    "verify_muonium_likelihood.py": "math",
}


def classify(path: Path) -> str:
    if path.name in _EXPLICIT_CATEGORY:
        return _EXPLICIT_CATEGORY[path.name]
    text = path.read_text(encoding="utf-8", errors="ignore")
    return "data" if any(marker in text for marker in _DATA_MARKERS) else "math"


def _script_was_all_skipped(path: Path) -> bool:
    """SCF_REVIEW_G0_G7_5563e67.md finding R7: a script that skips all its
    checks (missing optional local data, e.g. `verify_sparc_real_local.py`)
    exits 0 by design -- but that must not be summarized as "passed" by
    the runner. Every `verify_*.py` writes its own report to
    `<script_stem>_results.json`; if that report sets `"all_skipped":
    true`, this script's run counts as SKIPPED, not PASSED. Scripts
    without that field (the overwhelming majority) are unaffected."""
    results_path = path.with_name(path.stem + "_results.json")
    try:
        data = json.loads(results_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    return bool(data.get("all_skipped", False))


def run_math_and_data(category: str) -> int:
    env = dict(os.environ, PYTHONPATH=str(REPO / "src"), PYTHONIOENCODING="utf-8")
    scripts = sorted(VER.glob("verify_*.py"))
    selected = [p for p in scripts if category == "all" or classify(p) == category]
    results = []
    for path in selected:
        start = time.monotonic()
        try:
            proc = subprocess.run(
                [sys.executable, str(path)],
                cwd=VER,
                env=env,
                text=True,
                capture_output=True,
                timeout=120,
            )
            code = proc.returncode
            tail = (proc.stdout + proc.stderr).strip().splitlines()[-3:]
        except subprocess.TimeoutExpired:
            code = 124
            tail = ["TIMEOUT"]
        skipped = code == 0 and _script_was_all_skipped(path)
        results.append(
            {
                "script": path.name,
                "returncode": code,
                "skipped": skipped,
                "seconds": round(time.monotonic() - start, 2),
                "tail": tail,
            }
        )
    passed = sum(r["returncode"] == 0 and not r["skipped"] for r in results)
    skipped_scripts = [r for r in results if r["skipped"]]
    failed = [r for r in results if r["returncode"] != 0]
    print(json.dumps({
        "category": category, "count": len(results),
        "passed": passed, "skipped": len(skipped_scripts), "failed_count": len(failed),
    }, indent=2))
    for r in skipped_scripts:
        print("SKIP", r["script"], "(all checks skipped -- see its own results.json, not counted as passed)")
    for r in failed:
        print("FAIL", r["script"], r["tail"])
    return 0 if not failed else 1


_MD_LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")


def run_links() -> int:
    md_files = [p for p in REPO.rglob("*.md") if "archive" not in p.parts and ".git" not in p.parts]
    broken = []
    external_count = 0
    checked_relative = 0
    for md in md_files:
        text = md.read_text(encoding="utf-8", errors="ignore")
        for target in _MD_LINK.findall(text):
            target = target.split(" ", 1)[0].strip()  # drop optional "title"
            if not target or target.startswith("#"):
                continue
            if target.startswith("http://") or target.startswith("https://") or target.startswith("mailto:"):
                external_count += 1
                continue
            target_path = urllib.parse.unquote(target.split("#", 1)[0])
            if not target_path:
                continue
            resolved = (md.parent / target_path).resolve()
            checked_relative += 1
            if not resolved.exists():
                broken.append(f"{md.relative_to(REPO)} -> {target}")
    print(json.dumps({
        "category": "links",
        "markdown_files_scanned": len(md_files),
        "relative_links_checked": checked_relative,
        "external_links_counted_not_fetched": external_count,
        "broken_relative_links": len(broken),
    }, indent=2))
    for b in broken:
        print("BROKEN", b)
    return 0 if not broken else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--category",
        choices=["all", "math", "data", "links"],
        default="all",
        help="Which check group to run (default: all = math+data, excludes links).",
    )
    args = parser.parse_args()
    if args.category == "links":
        return run_links()
    return run_math_and_data(args.category)


if __name__ == "__main__":
    raise SystemExit(main())
