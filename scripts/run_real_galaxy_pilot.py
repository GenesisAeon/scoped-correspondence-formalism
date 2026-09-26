#!/usr/bin/env python3
"""Reproducible local CLI for the G5 SPARC pilot (SCF_REVIEW_G0_G7_5563e67.md
finding R6's acceptance criterion): explicit raw-data path + hash check,
separate Mode A / Mode B result files, real profile-likelihood curves and
distance/inclination sensitivity scenarios for every selected galaxy.

This does NOT generate plot images -- that remains open follow-up work
(honestly flagged, not fabricated); the JSON/CSV outputs below are
structured so that plots can be produced deterministically from them.

Usage:
    python scripts/run_real_galaxy_pilot.py --sparc-dir D:/mandala/scf_external_data/sparc \\
        --out-dir D:/mandala/scf_external_data/galaxy_pilot_results

Never downloads anything and never modifies repository source files. Exits
non-zero (without running the pilot) if the two raw files' SHA-256 don't
match the retrieval record in docs/sparc_data_provenance.md.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from scoped_correspondence.validation.galaxy_pilot import (  # noqa: E402
    distance_inclination_sensitivity,
    evaluate_baselines_on_holdout,
    fit_burkert_descriptive,
    galaxy_component_rows,
    profile_likelihood_burkert,
    select_frozen_sample,
    train_test_split_outer,
)
from scoped_correspondence.validation.sparc_data import (  # noqa: E402
    parse_component_table,
    parse_metadata_table,
)

_EXPECTED_SHA256 = {
    "SPARC_Lelli2016c.mrt": "5aa0501f6b0d881fa579030e315e7b5b6ef561a5bd3a07472f9929c7e5728243",
    "MassModels_Lelli2016c.mrt": "9108994b12cc401b94a1768beca61c53ec354779385c9c9cc571049f3043244c",
}


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sparc-dir", required=True, type=Path,
                     help="Directory containing SPARC_Lelli2016c.mrt and MassModels_Lelli2016c.mrt")
    ap.add_argument("--out-dir", required=True, type=Path, help="Directory to write result files into")
    ap.add_argument("--psi-half-width", type=float, default=1.0,
                     help="Profile-likelihood psi grid half-width around each galaxy's best-fit psi (dex)")
    ap.add_argument("--psi-n-points", type=int, default=41, help="Number of psi grid points per galaxy")
    args = ap.parse_args()

    for name, expected in _EXPECTED_SHA256.items():
        p = args.sparc_dir / name
        if not p.is_file():
            print(f"ABORT: missing raw file {p}", file=sys.stderr)
            return 2
        actual = _sha256(p)
        if actual != expected:
            print(f"ABORT: sha256 mismatch for {name}: expected {expected}, got {actual}", file=sys.stderr)
            return 2

    meta_rows = parse_metadata_table((args.sparc_dir / "SPARC_Lelli2016c.mrt").read_text(encoding="utf-8"))
    comp_rows = parse_component_table((args.sparc_dir / "MassModels_Lelli2016c.mrt").read_text(encoding="utf-8"))
    sel = select_frozen_sample(meta_rows, comp_rows)
    meta_by_id = {m.galaxy: m for m in meta_rows}

    args.out_dir.mkdir(parents=True, exist_ok=True)
    timestamp = dt.datetime.now().astimezone().isoformat(timespec="seconds")

    all_12 = list(sel.dev_galaxies) + list(sel.eval_galaxies)
    mode_a = {
        "generated_at": timestamp,
        "sparc_dir": str(args.sparc_dir),
        "selection": {
            "n_eligible_total": sel.n_eligible_total,
            "tercile_sizes": list(sel.tercile_sizes),
            "dev_galaxies": list(sel.dev_galaxies),
            "eval_galaxies": list(sel.eval_galaxies),
            "exclusions_count": len(sel.exclusions),
        },
        "fits": [],
        "profile_likelihood": {},
        "sensitivity": {},
    }
    profile_csv_rows = []
    sensitivity_csv_rows = []

    for g in all_12:
        rows = galaxy_component_rows(comp_rows, g)
        fit = fit_burkert_descriptive(rows, galaxy=g)
        mode_a["fits"].append({
            "galaxy": g, "set": "dev" if g in sel.dev_galaxies else "eval",
            "n_points": len(rows), "rho0_msun_pc3": fit.rho0_msun_pc3, "r0_pc": fit.r0_pc,
            "mu_h": fit.mu_h, "psi": fit.psi, "eta": fit.eta, "status": fit.status,
            "boundary_hit": fit.boundary_hit, "rmse_kms": fit.rmse_kms, "n_invalid_points": fit.n_invalid_points,
        })

        psi_grid = [fit.psi + args.psi_half_width * (2.0 * i / (args.psi_n_points - 1) - 1.0)
                    for i in range(args.psi_n_points)]
        points = profile_likelihood_burkert(rows, psi_grid)
        mode_a["profile_likelihood"][g] = [
            {"psi": p.psi, "eta_min": p.eta_min, "q": p.q, "status": p.status,
             "boundary_hit": p.boundary_hit, "feasible": p.feasible}
            for p in points
        ]
        for p in points:
            profile_csv_rows.append([g, p.psi, p.eta_min, p.q, p.status, p.boundary_hit, p.feasible])

        scenarios = distance_inclination_sensitivity(rows, meta_by_id[g])
        mode_a["sensitivity"][g] = [
            {"name": s.name, "rho0_msun_pc3": s.rho0_msun_pc3, "r0_pc": s.r0_pc,
             "mu_h": s.mu_h, "status": s.status, "boundary_hit": s.boundary_hit}
            for s in scenarios
        ]
        for s in scenarios:
            sensitivity_csv_rows.append([g, s.name, s.rho0_msun_pc3, s.r0_pc, s.mu_h, s.status, s.boundary_hit])

    mode_b = {
        "generated_at": timestamp,
        "sparc_dir": str(args.sparc_dir),
        "scores": [],
    }
    score_csv_rows = []
    for g in sel.eval_galaxies:
        rows = galaxy_component_rows(comp_rows, g)
        split = train_test_split_outer(rows)
        scores = evaluate_baselines_on_holdout(g, split)
        for s in scores:
            mode_b["scores"].append({
                "galaxy": s.galaxy, "baseline": s.baseline, "mae_kms": s.mae_kms, "rmse_kms": s.rmse_kms,
                "n_test": s.n_test, "n_invalid": s.n_invalid,
                "train_status": s.train_status, "train_boundary_hit": s.train_boundary_hit,
            })
            score_csv_rows.append([s.galaxy, s.baseline, s.mae_kms, s.rmse_kms, s.n_test, s.n_invalid,
                                    s.train_status, s.train_boundary_hit])

    (args.out_dir / "galaxy_pilot_mode_a_results.json").write_text(
        json.dumps(mode_a, indent=2, default=bool), encoding="utf-8")
    (args.out_dir / "galaxy_pilot_mode_b_results.json").write_text(
        json.dumps(mode_b, indent=2, default=bool), encoding="utf-8")

    with open(args.out_dir / "galaxy_pilot_profile_likelihood.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["galaxy", "psi", "eta_min", "q", "status", "boundary_hit", "feasible"])
        w.writerows(profile_csv_rows)

    with open(args.out_dir / "galaxy_pilot_sensitivity.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["galaxy", "scenario", "rho0_msun_pc3", "r0_pc", "mu_h", "status", "boundary_hit"])
        w.writerows(sensitivity_csv_rows)

    with open(args.out_dir / "galaxy_pilot_mode_b_scores.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["galaxy", "baseline", "mae_kms", "rmse_kms", "n_test", "n_invalid",
                     "train_status", "train_boundary_hit"])
        w.writerows(score_csv_rows)

    print(f"Wrote Mode A ({len(mode_a['fits'])} fits, {len(mode_a['profile_likelihood'])} profile scans, "
          f"{len(mode_a['sensitivity'])} sensitivity scans) and Mode B ({len(mode_b['scores'])} scores) "
          f"to {args.out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
