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
  5. Leave-one-cell-out panel: each cell's fit uses ONLY its own data (no
     cross-cell leakage) -- checked by verifying one cell's result is
     unaffected by a large change to another cell's series.
  6. ScopeViolationError guards.
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
from scoped_correspondence.data.nasa_battery_adapter import extract_discharge_capacities, synthetic_fixture  # noqa: E402
from scoped_correspondence.validation.battery_aging_pilot import (  # noqa: E402
    run_cell_pilot, run_leave_one_cell_out_panel,
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
    panel_before = run_leave_one_cell_out_panel({"A": caps_a, "B": caps_b}, c_eol=1.4, train_fraction=0.6)

    caps_b_modified = [999.0] * n
    panel_after = run_leave_one_cell_out_panel({"A": caps_a, "B": caps_b_modified}, c_eol=1.4, train_fraction=0.6)

    require(panel_before["A"].model_results == panel_after["A"].model_results,
            "cell A's fit must be unaffected by drastic changes to cell B (no cross-cell leakage)")
    return {"cell_A_unaffected": True}


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
        run_leave_one_cell_out_panel({}, c_eol=1.0)
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
