#!/usr/bin/env python3
"""Battery aging pilot pipeline + NASA .mat parser (DOMAIN_EXPANSION_ROADMAP.md Paket B5b).

Runs entirely against SYNTHETIC data -- no network access or redistributed
data required. The NASA PCoE dataset's own catalog reports an unspecified
license (independently confirmed via its CKAN API), so per plan section
5.1 the real dataset is neither downloaded here nor committed to this
repo; a genuine local run against the real data (four cells) WAS performed
during development and is reported as a one-time manual reproduction in
docs/battery_aging_pilot.md, explicitly separate from this automated check.

Checks:

  1. The parser (``extract_discharge_capacities``) correctly filters
     charge/impedance/discharge cycle types on the SAME interleaving
     pattern confirmed against the real dataset's structure.
  2. Exact linear synthetic series: MAE~0 for the matching model family,
     and the mean-model EOL crossing matches a hand-derived value.
  3. Right-censoring: a series that never reaches the EOL threshold within
     its observed window is reported as censored, with
     ``observed_first_eol_cycle=None`` -- never a fabricated 0 or a false
     "never" claim about cycles beyond the observed window.
  4. A cell whose true generating process changes AFTER the training
     prefix does not alter the fit (temporal split leakage guard).
  5. Personalized cell panel: each cell's fit uses ONLY its own data (no
     cross-cell leakage) -- checked by verifying one cell's result is
     unaffected by a large change to another cell's series.
  6. SCF_Review_fcc9a43.md finding R6: the parser retains cycle_index
     (position in the FULL charge/discharge/impedance sequence) and
     ambient temperature per discharge cycle, not only the bare capacity.
  7. SCF_Review_fcc9a43.md finding R6: a fixed absolute training-cycle
     origin is supported, and negative (model-domain-violating)
     extrapolated predictions are counted explicitly, not silently folded
     into the MAE average.
  8. SCF_Review_fcc9a43.md finding R6: per-cell metadata is attached to
     the result unchanged, not discarded.
  9. ScopeViolationError guards.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from scoped_correspondence.errors import ScopeViolationError  # noqa: E402
from scoped_correspondence.data.nasa_battery_adapter import (  # noqa: E402
    extract_discharge_capacities, extract_discharge_records, synthetic_fixture,
)
from scoped_correspondence.validation.battery_aging_pilot import (  # noqa: E402
    run_cell_pilot, run_personalized_cell_panel,
)


def require(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)


def check_parser_filters_cycle_types():
    caps = extract_discharge_capacities(synthetic_fixture())
    require(caps == [1.856, 1.846, 1.835], f"got {caps}")
    try:
        extract_discharge_capacities({"cycle": [{"type": "charge", "data": {}}]})
        raise AssertionError("should reject a struct with no discharge cycles")
    except ScopeViolationError:
        pass
    try:
        extract_discharge_capacities({"cycle": [{"type": "discharge", "data": {}}]})
        raise AssertionError("should reject a discharge cycle missing Capacity")
    except ScopeViolationError:
        pass
    return {"parsed": caps}


def check_exact_linear_recovery():
    n = 20
    caps = (2.0 - 0.03 * np.arange(n)).tolist()
    r = run_cell_pilot("SYN_LINEAR", caps, c_eol=1.4, train_fraction=0.6)
    require(r.model_results["linear"]["mae_holdout"] < 1e-9,
            f"linear MAE should be ~0 for exact linear data; got {r.model_results['linear']['mae_holdout']}")
    want_eol = (2.0 - 1.4) / 0.03
    got_eol = r.model_results["linear"]["mean_eol_crossing_cycle"]
    require(abs(got_eol - want_eol) < 1e-6, f"EOL crossing: got {got_eol}, want {want_eol}")
    return {"mae": r.model_results["linear"]["mae_holdout"], "eol": got_eol}


def check_censoring():
    n = 20
    caps = (2.0 - 0.001 * np.arange(n)).tolist()  # never drops below 1.0 within window
    r = run_cell_pilot("SYN_CENSORED", caps, c_eol=1.0, train_fraction=0.6)
    require(r.censored is True, "should be censored")
    require(r.observed_first_eol_cycle is None, "censored cell must report observed_first_eol_cycle=None, not a fabricated value")
    return r.to_dict()


def check_leakage_guard():
    n = 20
    caps = (2.0 - 0.03 * np.arange(n)).tolist()
    r_before = run_cell_pilot("SYN", caps, c_eol=1.4, train_fraction=0.6)

    caps_modified = list(caps)
    n_train = r_before.n_train
    for i in range(n_train, n):
        caps_modified[i] = 999.0  # drastically change everything AFTER the training prefix

    r_after = run_cell_pilot("SYN", caps_modified, c_eol=1.4, train_fraction=0.6)
    for model in ("persistence", "linear", "power"):
        require(r_before.model_results[model]["params"] == r_after.model_results[model]["params"],
                f"{model}: fit params changed after modifying only post-training-prefix values")
    return {"checked_models": 3}


def check_panel_no_cross_cell_leakage():
    n = 20
    caps_a = (2.0 - 0.03 * np.arange(n)).tolist()
    caps_b = (1.9 - 0.02 * np.arange(n)).tolist()
    panel_before = run_personalized_cell_panel({"A": caps_a, "B": caps_b}, c_eol=1.4, train_fraction=0.6)

    caps_b_modified = [999.0] * n
    panel_after = run_personalized_cell_panel({"A": caps_a, "B": caps_b_modified}, c_eol=1.4, train_fraction=0.6)

    require(panel_before["A"].model_results == panel_after["A"].model_results,
            "cell A's fit must be unaffected by drastic changes to cell B (no cross-cell leakage)")
    return {"cell_A_unaffected": True}


def check_r6_metadata_retained_by_parser():
    """SCF_Review_fcc9a43.md finding R6: the parser must retain cycle_index
    (position in the FULL charge/discharge/impedance sequence) and ambient
    temperature per discharge cycle, not only the bare capacity value."""
    records = extract_discharge_records(synthetic_fixture())
    require(len(records) == 3, f"expected 3 discharge records; got {len(records)}")
    require([r.cycle_index for r in records] == [1, 4, 7],
            f"cycle_index should reflect position in the FULL sequence; got {[r.cycle_index for r in records]}")
    require([r.discharge_index for r in records] == [0, 1, 2], "discharge_index should be 0,1,2 in order")
    require(all(r.ambient_temperature == 24 for r in records), "ambient_temperature must be retained")
    # backward compatibility: extract_discharge_capacities must be unchanged
    require(extract_discharge_capacities(synthetic_fixture()) == [r.capacity for r in records],
            "extract_discharge_capacities must match extract_discharge_records's capacities exactly")
    return {"n_records": len(records), "cycle_indices": [r.cycle_index for r in records]}


def check_r6_fixed_origin_and_negative_extrapolation_flag():
    """SCF_Review_fcc9a43.md finding R6: support a FIXED absolute training-cycle
    origin (not only a fraction of the eventual series length), and expose
    negative (model-domain-violating) extrapolated predictions explicitly rather
    than folding them silently into the MAE average."""
    n = 30
    caps = (2.0 - 0.03 * np.arange(n)).tolist()  # C0=2, a=0.03: goes negative around cycle 67
    r_fixed = run_cell_pilot("SYN_FIXED_ORIGIN", caps, c_eol=1.4, n_train=20)
    require(r_fixed.n_train == 20, f"n_train should be exactly the fixed 20; got {r_fixed.n_train}")

    # a persistence fit on a strongly-declining prefix, evaluated far enough out to
    # go negative under the LINEAR model, must report the negative count > 0, not hide it.
    n2 = 10
    caps2 = (0.5 - 0.1 * np.arange(n2)).tolist()  # C0=0.5, a=0.1 -> goes negative after cycle 5
    r_neg = run_cell_pilot("SYN_NEGATIVE_EXTRAPOLATION", caps2, c_eol=-100.0, train_fraction=0.6)
    require(r_neg.model_results["linear"]["n_negative_extrapolation_predictions"] > 0,
            f"linear model's held-out predictions should include negative extrapolations; "
            f"got {r_neg.model_results['linear']['n_negative_extrapolation_predictions']}")
    return {"n_train_fixed": r_fixed.n_train,
            "n_negative": r_neg.model_results["linear"]["n_negative_extrapolation_predictions"]}


def check_r6_metadata_passthrough():
    """SCF_Review_fcc9a43.md finding R6: per-cell metadata must be attached to the
    result unchanged, not discarded."""
    n = 20
    caps = (2.0 - 0.03 * np.arange(n)).tolist()
    meta = {"A": {"discharge_index_offset": 0, "protocol": "CC-CV"}}
    panel = run_personalized_cell_panel({"A": caps}, c_eol=1.4, train_fraction=0.6, cell_metadata=meta)
    require(panel["A"].metadata == meta["A"], f"metadata not passed through: got {panel['A'].metadata}")
    return {"metadata": panel["A"].metadata}


def check_scope_violation_guards():
    try:
        run_cell_pilot("X", [1.0, 2.0, 3.0], c_eol=1.0)
        raise AssertionError("should reject too few observations")
    except ScopeViolationError:
        pass
    try:
        run_cell_pilot("X", list(range(20)), c_eol=1.0, train_fraction=1.5)
        raise AssertionError("should reject train_fraction outside (0,1)")
    except ScopeViolationError:
        pass
    try:
        run_personalized_cell_panel({}, c_eol=1.0)
        raise AssertionError("should reject empty panel")
    except ScopeViolationError:
        pass
    return {"checked": 3}


CHECKS = [
    ("parser_filters_cycle_types", check_parser_filters_cycle_types),
    ("exact_linear_recovery", check_exact_linear_recovery),
    ("censoring", check_censoring),
    ("leakage_guard", check_leakage_guard),
    ("panel_no_cross_cell_leakage", check_panel_no_cross_cell_leakage),
    ("r6_metadata_retained_by_parser", check_r6_metadata_retained_by_parser),
    ("r6_fixed_origin_and_negative_extrapolation_flag", check_r6_fixed_origin_and_negative_extrapolation_flag),
    ("r6_metadata_passthrough", check_r6_metadata_passthrough),
    ("scope_violation_guards", check_scope_violation_guards),
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json-out", type=Path, default=Path(__file__).with_name("verify_battery_aging_pilot_results.json"))
    args = parser.parse_args()

    report = {
        "package": "DOMAIN_EXPANSION_ROADMAP.md Paket B5b (battery aging pilot, synthetic-only CI check)",
        "timestamp": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "python": sys.version.split()[0],
        "checks": {},
    }

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

    args.json_out.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    print(f"\n{sum(1 for c in report['checks'].values() if c['status'] == 'pass')}/{len(CHECKS)} checks passed")
    print(f"Report written to {args.json_out}")
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
