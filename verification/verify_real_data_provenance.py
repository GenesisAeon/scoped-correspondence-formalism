#!/usr/bin/env python3
"""Provenance/sanity checks for real (non-illustrative) datasets under data/.

Added 2026-09-20 as the direct fix for the failure mode found in
AUDIT_ROADMAP.md item 1 (Cygnus per-epoch data of unconfirmed origin, see
docs/cygnus_pilot.md). Every dataset listed in data/real_data_manifest.json
was fetched directly from its primary source with a recorded URL and
retrieval timestamp; this script re-hashes each file and confirms it still
matches, then runs a minimal structural sanity check per dataset (row
count, expected columns, date range) -- it does NOT re-download anything
and does NOT build a validation pilot; see docs/real_data_provenance.md.

Checks:
  1. Every file in the manifest exists and its sha256 matches exactly.
  2. usgs_earthquakes_m6plus_2000_2026.csv: expected header columns,
     row count, all magnitudes >= 6.0, dates within the declared range.
  3. noaa_global_temp_anomaly_1880_2025.csv: expected NOAA comment header,
     146 annual rows, years strictly increasing, values are floats.
  4. owid_covid_world_daily_2020_2023.csv: expected header columns, all
     rows have location=="World", dates within the declared range.

JSON {count, passed, failed, report}; numbers from this run. Read-only:
does not modify any data/ file.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import platform
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
MANIFEST_PATH = DATA / "real_data_manifest.json"


def require(ok, msg):
    if not bool(ok):
        raise AssertionError(msg)


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def check_manifest_hashes():
    """Every manifest entry's file exists and its sha256 matches exactly."""
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    results = []
    for entry in manifest["datasets"]:
        path = ROOT / entry["file"]
        require(path.is_file(), f"{entry['file']} must exist")
        actual = sha256_of(path)
        require(
            actual == entry["sha256"],
            f"{entry['file']}: sha256 mismatch (manifest={entry['sha256']!r}, actual={actual!r})",
        )
        results.append({"id": entry["id"], "file": entry["file"], "sha256": actual})
    return {"entries_checked": len(results), "results": results}


def check_usgs_earthquakes():
    """Header, row count, magnitude>=6.0, dates within declared range."""
    path = DATA / "usgs_earthquakes_m6plus_2000_2026.csv"
    with path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    require(len(rows) == 3974, f"expected 3974 rows, got {len(rows)}")
    mags = [float(r["mag"]) for r in rows]
    require(all(m >= 6.0 for m in mags), "all magnitudes must be >= 6.0")
    dates = [r["time"][:10] for r in rows]
    require(min(dates) >= "2000-01-01", f"earliest date out of range: {min(dates)}")
    require(max(dates) <= "2026-09-20", f"latest date out of range: {max(dates)}")
    require("place" in rows[0] and "depth" in rows[0], "expected columns present")
    return {
        "row_count": len(rows),
        "min_magnitude": min(mags),
        "max_magnitude": max(mags),
        "date_range": [min(dates), max(dates)],
    }


def check_noaa_temp_anomaly():
    """NOAA comment header, 146 annual rows, strictly increasing years."""
    path = DATA / "noaa_global_temp_anomaly_1880_2025.csv"
    lines = path.read_text(encoding="utf-8").splitlines()
    comment_lines = [ln for ln in lines if ln.startswith("#")]
    require(len(comment_lines) >= 3, "expected NOAA's own comment header lines")
    require(
        any("Global Land and Ocean" in ln for ln in comment_lines),
        "expected NOAA title comment",
    )
    data_lines = [ln for ln in lines if ln and not ln.startswith("#")]
    reader = csv.DictReader(data_lines)
    rows = list(reader)
    require(len(rows) == 146, f"expected 146 annual rows, got {len(rows)}")
    years = [int(r["Year"]) for r in rows]
    require(years == sorted(years), "years must be strictly increasing")
    require(years[0] == 1880 and years[-1] == 2025, f"unexpected year range: {years[0]}-{years[-1]}")
    values = [float(r["Departure from Average"]) for r in rows]
    require(all(-5.0 < v < 5.0 for v in values), "anomaly values out of plausible range")
    return {
        "row_count": len(rows),
        "year_range": [years[0], years[-1]],
        "value_range_c": [min(values), max(values)],
    }


def check_owid_covid_world():
    """Header, all rows location=='World', dates within declared range."""
    path = DATA / "owid_covid_world_daily_2020_2023.csv"
    with path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    require(len(rows) == 1143, f"expected 1143 rows, got {len(rows)}")
    require(all(r["location"] == "World" for r in rows), "every row must be location=='World'")
    dates = [r["date"] for r in rows]
    require(min(dates) == "2020-01-22", f"unexpected earliest date: {min(dates)}")
    require(max(dates) == "2023-03-09", f"unexpected latest date: {max(dates)}")
    require(dates == sorted(dates), "dates must be strictly increasing")
    require("new_cases" in rows[0] and "new_deaths" in rows[0], "expected columns present")
    return {
        "row_count": len(rows),
        "date_range": [min(dates), max(dates)],
        "all_rows_world_only": True,
    }


CHECKS = [
    ("manifest_sha256", check_manifest_hashes),
    ("usgs_earthquakes_sanity", check_usgs_earthquakes),
    ("noaa_temp_anomaly_sanity", check_noaa_temp_anomaly),
    ("owid_covid_world_sanity", check_owid_covid_world),
]


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--json-out",
        type=Path,
        default=Path(__file__).with_name("verify_real_data_provenance_results.json"),
    )
    args = p.parse_args(argv)

    report = {
        "purpose": "provenance + sanity checks for data/real_data_manifest.json entries",
        "manifest": "data/real_data_manifest.json",
        "docs": "docs/real_data_provenance.md",
        "timestamp": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "checks": {},
        "disclaimer": (
            "Read-only re-hash and structural sanity check; does not "
            "re-download data and does not constitute a validation pilot."
        ),
    }
    passed = 0
    failed = 0
    errors = []
    for name, fn in CHECKS:
        try:
            report["checks"][name] = {"status": "passed", "detail": fn()}
            passed += 1
            print(f"PASS  {name}")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            errors.append({"check": name, "error": f"{type(exc).__name__}: {exc}"})
            report["checks"][name] = {"status": "failed", "error": f"{type(exc).__name__}: {exc}"}
            print(f"FAIL  {name}: {exc}")

    summary = {"count": len(CHECKS), "passed": passed, "failed": failed, "errors": errors, "report": report}
    args.json_out.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(f"\n{passed}/{len(CHECKS)} passed; wrote {args.json_out}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
