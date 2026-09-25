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
}


def classify(path: Path) -> str:
    if path.name in _EXPLICIT_CATEGORY:
        return _EXPLICIT_CATEGORY[path.name]
    text = path.read_text(encoding="utf-8", errors="ignore")
    return "data" if any(marker in text for marker in _DATA_MARKERS) else "math"


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
        results.append(
            {
                "script": path.name,
                "returncode": code,
                "seconds": round(time.monotonic() - start, 2),
                "tail": tail,
            }
        )
    passed = sum(r["returncode"] == 0 for r in results)
    failed = [r for r in results if r["returncode"] != 0]
    print(json.dumps({"category": category, "count": len(results), "passed": passed,
                       "failed_count": len(failed)}, indent=2))
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
