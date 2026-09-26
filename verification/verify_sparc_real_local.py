#!/usr/bin/env python3
"""Real, LOCAL-ONLY SPARC data check (G4).

Content basis: `docs/sparc_data_provenance.md`. This script looks for the
two raw SPARC files at a documented local path (never committed to this
repository -- their redistribution rights are unresolved) and, if found,
parses ALL real rows with `sparc_data.py` and confirms their SHA-256
against the retrieval record.

Standard CI never has these files and must not need to download them
(Plan §12.1: "Standard-CI darf keine externen Downloads voraussetzen").
When the files are absent, EVERY check below is marked
``"status": "skipped"`` (never "pass") and the script still exits 0 --
Plan §12.1's own distinction ("ein übersprungener Lauf ist kein
bestandener Datencheck") is honored in the report content, not by
failing CI for a deliberately-uncommitted, license-unresolved dataset.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from scoped_correspondence.validation.sparc_data import (  # noqa: E402
    combine_baryonic_v2,
    parse_component_table,
    parse_metadata_table,
)

_DEFAULT_DIR = Path("D:/mandala/scf_external_data/sparc")
_RAW_DIR = Path(os.environ.get("SCF_SPARC_RAW_DIR", str(_DEFAULT_DIR)))

_EXPECTED_SHA256 = {
    "SPARC_Lelli2016c.mrt": "5aa0501f6b0d881fa579030e315e7b5b6ef561a5bd3a07472f9929c7e5728243",
    "MassModels_Lelli2016c.mrt": "9108994b12cc401b94a1768beca61c53ec354779385c9c9cc571049f3043244c",
}


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def require(ok, msg):
    if not bool(ok):
        raise AssertionError(msg)


def _files_present() -> bool:
    return all((_RAW_DIR / name).is_file() for name in _EXPECTED_SHA256)


def check_sha256_matches_provenance_record():
    for name, expected in _EXPECTED_SHA256.items():
        actual = _sha256(_RAW_DIR / name)
        require(actual == expected, f"{name}: sha256 mismatch, expected {expected}, got {actual}")
    return {"ok": True, "dir": str(_RAW_DIR)}


def check_real_metadata_table_parses_and_validates():
    text = (_RAW_DIR / "SPARC_Lelli2016c.mrt").read_text(encoding="utf-8")
    rows = parse_metadata_table(text)
    require(len(rows) == 175, f"expected 175 SPARC galaxies, got {len(rows)}")
    return {"n_rows": len(rows)}


def check_real_component_table_parses_and_validates():
    text = (_RAW_DIR / "MassModels_Lelli2016c.mrt").read_text(encoding="utf-8")
    rows = parse_component_table(text)
    require(len(rows) > 3000, f"expected several thousand component rows, got {len(rows)}")
    galaxies = {r.galaxy for r in rows}
    require(len(galaxies) == 175, f"expected 175 distinct galaxies in component table, got {len(galaxies)}")
    neg_gas = sum(1 for r in rows if r.Vgas_kms < 0)
    require(neg_gas > 0, "expected at least some real rows with the negative-Vgas sign convention")
    return {"n_rows": len(rows), "n_galaxies": len(galaxies), "n_negative_vgas_rows": neg_gas}


def check_metadata_and_component_galaxy_sets_match():
    meta_rows = parse_metadata_table((_RAW_DIR / "SPARC_Lelli2016c.mrt").read_text(encoding="utf-8"))
    comp_rows = parse_component_table((_RAW_DIR / "MassModels_Lelli2016c.mrt").read_text(encoding="utf-8"))
    meta_galaxies = {r.galaxy for r in meta_rows}
    comp_galaxies = {r.galaxy for r in comp_rows}
    require(meta_galaxies == comp_galaxies,
            f"galaxy sets differ: meta-only={sorted(meta_galaxies - comp_galaxies)[:5]}, "
            f"comp-only={sorted(comp_galaxies - meta_galaxies)[:5]}")
    return {"n_common_galaxies": len(meta_galaxies)}


def check_real_baryonic_combination_runs_on_a_negative_gas_row():
    """Exercise combine_baryonic_v2 on a REAL row that has negative Vgas
    (not just the plan's synthetic worked example)."""
    rows = parse_component_table((_RAW_DIR / "MassModels_Lelli2016c.mrt").read_text(encoding="utf-8"))
    neg_row = next(r for r in rows if r.Vgas_kms < 0)
    v2 = combine_baryonic_v2(neg_row.Vgas_kms, neg_row.Vdisk_kms, neg_row.Vbul_kms)
    require(isinstance(v2, float), "combine_baryonic_v2 should return a float")
    return {"galaxy": neg_row.galaxy, "Vgas_kms": neg_row.Vgas_kms, "v_bar_sq": v2}


CHECKS = [
    ("sha256_matches_provenance_record", check_sha256_matches_provenance_record),
    ("real_metadata_table_parses_and_validates", check_real_metadata_table_parses_and_validates),
    ("real_component_table_parses_and_validates", check_real_component_table_parses_and_validates),
    ("metadata_and_component_galaxy_sets_match", check_metadata_and_component_galaxy_sets_match),
    ("real_baryonic_combination_runs_on_a_negative_gas_row", check_real_baryonic_combination_runs_on_a_negative_gas_row),
]


def main() -> int:
    report = {
        "package": "GALAXY_DYNAMICS_ROADMAP.md Paket G4 (SPARC adapter, REAL local files)",
        "timestamp": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "python": sys.version.split()[0],
        "raw_dir": str(_RAW_DIR),
        "checks": {},
    }

    if not _files_present():
        for name, _fn in CHECKS:
            report["checks"][name] = {
                "status": "skipped",
                "reason": f"raw SPARC files not found locally at {_RAW_DIR} "
                          f"(set SCF_SPARC_RAW_DIR, or see docs/sparc_data_provenance.md)",
            }
            print(f"SKIP  {name}: raw files not present at {_RAW_DIR}")
        report["all_skipped"] = True
        out = Path(__file__).with_name("verify_sparc_real_local_results.json")
        out.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
        print(f"\n0/{len(CHECKS)} passed, {len(CHECKS)}/{len(CHECKS)} skipped (no local data -- not a failure)")
        print(f"Report written to {out}")
        return 0

    all_ok = True
    for name, fn in CHECKS:
        try:
            detail = fn()
            report["checks"][name] = {"status": "pass", "detail": detail}
            print(f"PASS  {name}")
        except AssertionError as e:
            all_ok = False
            report["checks"][name] = {"status": "fail", "error": str(e)}
            print(f"FAIL  {name}: {e}")
        except Exception as e:  # noqa: BLE001
            all_ok = False
            report["checks"][name] = {"status": "error", "error": f"{type(e).__name__}: {e}"}
            print(f"ERROR {name}: {type(e).__name__}: {e}")

    out = Path(__file__).with_name("verify_sparc_real_local_results.json")
    out.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    print(f"\n{sum(1 for c in report['checks'].values() if c['status'] == 'pass')}/{len(CHECKS)} checks passed")
    print(f"Report written to {out}")
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
