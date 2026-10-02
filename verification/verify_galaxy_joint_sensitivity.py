"""J7 data check (SCOPE_COMPOSITION_EVIDENCE_ROADMAP.md, plan section 13.3):
joint scenarios (D, i, Upsilon_disk, Upsilon_bulge) for the held-out galaxy
comparison on the LOCAL, hash-checked SPARC files (never committed; see
docs/sparc_data_provenance.md). If the files are absent every check is
skipped and the report sets all_skipped = true -- a skipped real-data check
is never counted as passed.

Checks: the reference scenario reproduces the existing Mode-B evaluation
exactly; train/test radii are the same points in every scenario; the grid
reports comparable and non-comparable scenarios separately; the summary
gives the RANGE of held-out loss differences and sign counts, explicitly
not as probabilities; a scenario outside the physical range is rejected.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "src"))

from scoped_correspondence.errors import ScopeViolationError  # noqa: E402
from scoped_correspondence.validation.galaxy_joint_sensitivity import joint_holdout_sensitivity  # noqa: E402
from scoped_correspondence.validation.galaxy_pilot import (  # noqa: E402
    distance_inclination_sensitivity_mode_b,
    evaluate_baselines_on_holdout,
    galaxy_component_rows,
    select_frozen_sample,
    train_test_split_outer,
)
from scoped_correspondence.validation.global_sensitivity import JointScenarioGrid  # noqa: E402
from scoped_correspondence.validation.sparc_data import parse_component_table, parse_metadata_table  # noqa: E402

RAW = Path(os.environ.get("SCF_SPARC_RAW_DIR", "D:/mandala/scf_external_data/sparc"))
SHA = {
    "SPARC_Lelli2016c.mrt": "5aa0501f6b0d881fa579030e315e7b5b6ef561a5bd3a07472f9929c7e5728243",
    "MassModels_Lelli2016c.mrt": "9108994b12cc401b94a1768beca61c53ec354779385c9c9cc571049f3043244c",
}
GRID = JointScenarioGrid(
    ("D_sigma", "i_sigma", "upsilon_d", "upsilon_b"),
    ((-1.0, 0.0, 1.0), (-1.0, 0.0, 1.0), (0.4, 0.5, 0.6), (0.7,)),
    ("catalogue e_D (documented measurement error)", "catalogue e_inc (documented measurement error)",
     "declared model-variant scenarios around 0.5 (no measured error)", "fixed at the pilot value 0.7"),
)


def require(c, m=""):
    if not c:
        raise AssertionError(m)


def _load():
    for name, sha in SHA.items():
        p = RAW / name
        require(hashlib.sha256(p.read_bytes()).hexdigest() == sha, f"{name}: sha256 mismatch")
    meta = parse_metadata_table((RAW / "SPARC_Lelli2016c.mrt").read_text(encoding="utf-8"))
    comp = parse_component_table((RAW / "MassModels_Lelli2016c.mrt").read_text(encoding="utf-8"))
    sel = select_frozen_sample(meta, comp)
    g = sel.eval_galaxies[0]
    m = {x.galaxy: x for x in meta}[g]
    split = train_test_split_outer(galaxy_component_rows(comp, g))
    return g, m, split


def run_checks():
    g, meta, split = _load()
    rep = joint_holdout_sensitivity(g, split, meta, GRID, baseline_a="C_mond", baseline_b="A_burkert")
    ref = [r for r in rep.results if r.point == {"D_sigma": 0.0, "i_sigma": 0.0, "upsilon_d": 0.5, "upsilon_b": 0.7}][0]
    base = {s.baseline: s.primary_rmse_kms for s in evaluate_baselines_on_holdout(g, split, 0.5, 0.7)}
    require(ref.scores == base, f"reference scenario must reproduce the existing Mode-B evaluation: {ref.scores} vs {base}")
    # Independent route for NON-reference points (found by the J7 mutation run: the reference point alone
    # cannot detect an untransformed test set): the existing one-at-a-time Mode-B sensitivity must be
    # reproduced exactly by the matching joint grid points.
    one_at_a_time = {s.name: {sc.baseline: sc.primary_rmse_kms for sc in s.scores}
                     for s in distance_inclination_sensitivity_mode_b(split, meta, galaxy=g)}
    for name, pt in (("D+sigma_D", {"D_sigma": 1.0, "i_sigma": 0.0}), ("D-sigma_D", {"D_sigma": -1.0, "i_sigma": 0.0}),
                     ("i+sigma_i", {"D_sigma": 0.0, "i_sigma": 1.0}), ("i-sigma_i", {"D_sigma": 0.0, "i_sigma": -1.0})):
        joint = [r for r in rep.results if r.point == dict(pt, upsilon_d=0.5, upsilon_b=0.7)][0]
        require(joint.scores == one_at_a_time[name], f"{name}: joint grid point must equal the existing one-at-a-time scenario")
    require(rep.n_points == 27 and rep.n_comparable + rep.n_not_comparable == 27, "every scenario counted")
    require(any("NOT empirical probabilities" in n for n in rep.notes), "no probability reading of the grid")
    try:
        bad = JointScenarioGrid(GRID.names, ((-1e6,), (0.0,), (0.5,), (0.7,)), GRID.provenance)
        joint_holdout_sensitivity(g, split, meta, bad, baseline_a="C_mond", baseline_b="A_burkert")
        raise AssertionError("an unphysical distance must be rejected")
    except ScopeViolationError:
        pass
    return {
        "galaxy": g, "baselines": ["C_mond", "A_burkert"], "target": "difference of held-out primary RMSE [km/s]",
        "n_points": rep.n_points, "n_comparable": rep.n_comparable, "n_not_comparable": rep.n_not_comparable,
        "difference_range": [rep.min_difference, rep.max_difference],
        "n_mond_better": rep.n_a_better, "n_burkert_better": rep.n_b_better,
        "reference_scores": ref.scores, "notes": list(rep.notes),
    }


def main():
    out = Path(__file__).with_name("verify_galaxy_joint_sensitivity_results.json")
    if not all((RAW / n).is_file() for n in SHA):
        print("SKIP  local SPARC files absent (blocked_missing_data) -- not counted as passed")
        out.write_text(json.dumps({"n_passed": 0, "n_total": 1, "all_skipped": True, "reason": "blocked_missing_data"}, indent=2))
        return 0
    try:
        res = run_checks()
        print("PASS  joint_scenarios_on_local_sparc")
        out.write_text(json.dumps({"n_passed": 1, "n_total": 1, "all_skipped": False, "results": res}, indent=2, default=str))
        return 0
    except AssertionError as e:
        print(f"FAIL  joint_scenarios_on_local_sparc: {e}")
        out.write_text(json.dumps({"n_passed": 0, "n_total": 1, "error": str(e)}, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
