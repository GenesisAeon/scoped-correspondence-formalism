#!/usr/bin/env python3
"""Rolling-origin backtest utility + NOAA application (Milestone 6e).

NONSTATIONARY_ROADMAP.md package 1, response to
prompts/Answers/nicht_stationäre_Treiber/SCF_Nichtstationaere_Treiber_und_Kippen.md
(Astra, 2026-09-21) section 7 ("Zeitlich rollierend auswerten"): a single
train/test split is retained for the original Cygnus/COVID/NOAA/earthquake
pilots' own honest results, but a materially more robust comparison
between competing simple models needs many origins pooled together.

Checks:
  1. rolling_origin_backtest scope violations: non-increasing x, origin not
     present in x, non-positive horizon, no predictors, mismatched
     prediction shape, a predictor that would need test data it never
     receives (checked structurally: predictors only ever see calib_x/
     calib_y/test_x, never test_y).
  2. A hand-constructed toy series with a known closed-form persistence
     RMSE, checked by hand.
  3. run_noaa_rolling_origin_backtest reproduces every one of Astra's 11
     per-origin RMSE triples and the 3 pooled RMSEs from
     SCF_Nichtstationaere_Treiber_und_Kippen.md section 2.2, to 1e-6.
  4. The origin=1999 slice is hand-verified against the raw NOAA values
     independently of the utility (persistence RMSE for 2000-2004 vs.
     the 1999 anomaly).

JSON {count, passed, failed, report}; numbers from this run. Does not
mutate validation/core.py, noaa_temp_pilot.py's original 1880-1999/
2000-2025 pilot, or any other existing pilot.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import platform
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from scoped_correspondence.errors import ScopeViolationError  # noqa: E402
from scoped_correspondence.validation import (  # noqa: E402
    TEMP_ROLLING_ORIGIN_HORIZON_YEARS,
    TEMP_ROLLING_ORIGIN_YEARS,
    load_annual_anomalies,
    rolling_origin_backtest,
    run_noaa_rolling_origin_backtest,
)


def require(ok, msg):
    if not bool(ok):
        raise AssertionError(msg)


def near(a, b, atol=1e-6):
    if abs(float(a) - float(b)) > atol:
        raise AssertionError(f"{a!r} != {b!r} (atol={atol})")


# Astra's exact per-origin numbers from SCF_Nichtstationaere_Treiber_und_Kippen.md
# section 2.2 (independently reproduced fresh against this repo before being
# incorporated -- see commit 9e75897).
ASTRA_ROLLING = {
    1969: (0.10862780491200216, 0.09017719627001416, 0.1258406733166314),
    1974: (0.17169740825067803, 0.10339794277075733, 0.12841179737762082),
    1979: (0.09848857801796104, 0.1833785460686837, 0.18718342577637911),
    1984: (0.1274362585765919, 0.151732186745061, 0.08698100400967576),
    1989: (0.09969954864491613, 0.1643975762635452, 0.08735919992828929),
    1994: (0.16498484778912276, 0.2452589753288475, 0.09739548011171258),
    1999: (0.14825653442597392, 0.2472376722652183, 0.059324555943180306),
    2004: (0.09949874371066199, 0.2647966832512058, 0.06295970974002177),
    2009: (0.050990195135927834, 0.24518681699649844, 0.04803522475119976),
    2014: (0.2097140910859354, 0.44350051928953593, 0.17411503321321203),
    2019: (0.15956190021430552, 0.47130905919043736, 0.1562807820599622),
}
ASTRA_POOLED = {"persistence": 0.13760946056272308, "expanding": 0.2650621200212291, "last30": 0.11930737327903064}


def check_scope_violations():
    x = np.array([0.0, 1.0, 2.0, 3.0, 4.0])
    y = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    ident = lambda cx, cy, tx: np.full(tx.shape, cy[-1])

    cases = {}

    def raises(fn):
        try:
            fn()
            return False
        except ScopeViolationError:
            return True

    cases["non_increasing_x"] = raises(
        lambda: rolling_origin_backtest(np.array([0.0, 2.0, 1.0]), np.array([1.0, 2.0, 3.0]), origins=[0.0], horizon=1, predictors={"p": ident})
    )
    cases["origin_not_in_x"] = raises(
        lambda: rolling_origin_backtest(x, y, origins=[0.5], horizon=1, predictors={"p": ident})
    )
    cases["nonpositive_horizon"] = raises(
        lambda: rolling_origin_backtest(x, y, origins=[1.0], horizon=0, predictors={"p": ident})
    )
    cases["no_predictors"] = raises(
        lambda: rolling_origin_backtest(x, y, origins=[1.0], horizon=1, predictors={})
    )
    cases["no_origins"] = raises(
        lambda: rolling_origin_backtest(x, y, origins=[], horizon=1, predictors={"p": ident})
    )
    cases["wrong_prediction_shape"] = raises(
        lambda: rolling_origin_backtest(x, y, origins=[1.0], horizon=1, predictors={"p": lambda cx, cy, tx: np.array([1.0, 2.0])})
    )
    cases["horizon_beyond_data"] = raises(
        lambda: rolling_origin_backtest(x, y, origins=[4.0], horizon=1, predictors={"p": ident})
    )
    for name, raised in cases.items():
        require(raised, f"expected ScopeViolationError for {name}")
    return cases


def check_toy_series_hand_rmse():
    """x=[0..9], y=x (perfect line). origin=4, horizon=3: test y=[5,6,7]."""
    x = np.arange(10, dtype=float)
    y = x.copy()
    persistence = lambda cx, cy, tx: np.full(tx.shape, cy[-1])
    report = rolling_origin_backtest(x, y, origins=[4.0], horizon=3, predictors={"persistence": persistence})
    obs = [5.0, 6.0, 7.0]
    base = 4.0
    hand_rmse = math.sqrt(sum((o - base) ** 2 for o in obs) / len(obs))
    near(report.pooled_rmse["persistence"], hand_rmse, atol=1e-12)
    require(report.per_origin[0].n_calib == 5, "n_calib at origin=4 must be 5 (x=0..4)")
    require(report.per_origin[0].n_test == 3, "n_test at origin=4, horizon=3 must be 3")
    return {"hand_rmse": hand_rmse, "report_rmse": report.pooled_rmse["persistence"], "n_calib": report.per_origin[0].n_calib}


def check_noaa_rolling_matches_astra(data_path):
    report = run_noaa_rolling_origin_backtest(data_path)
    require(report.origins == tuple(float(y) for y in TEMP_ROLLING_ORIGIN_YEARS), "origins must match the fixed protocol")
    require(report.horizon == float(TEMP_ROLLING_ORIGIN_HORIZON_YEARS), "horizon must be 5 years")
    require(len(report.per_origin) == 11, f"expected 11 origins, got {len(report.per_origin)}")

    per_origin_checked = 0
    for o in report.per_origin:
        expected = ASTRA_ROLLING[int(o.origin)]
        near(o.rmse_by_predictor["persistence"], expected[0])
        near(o.rmse_by_predictor["expanding"], expected[1])
        near(o.rmse_by_predictor["last30"], expected[2])
        per_origin_checked += 1

    for name, expected in ASTRA_POOLED.items():
        near(report.pooled_rmse[name], expected)

    return {
        "origins_checked": per_origin_checked,
        "pooled_rmse": report.pooled_rmse,
        "matches_astra_within_1e-6": True,
    }


def check_origin_1999_hand_verify(data_path):
    """Independent of the utility: origin=1999, test=2000-2004, persistence."""
    points = load_annual_anomalies(data_path)
    by_year = {p.year: p.anomaly_c for p in points}
    base = by_year[1999]
    obs = [by_year[y] for y in range(2000, 2005)]
    hand_rmse = math.sqrt(sum((o - base) ** 2 for o in obs) / len(obs))
    report = run_noaa_rolling_origin_backtest(data_path)
    origin_1999 = next(o for o in report.per_origin if o.origin == 1999.0)
    near(hand_rmse, origin_1999.rmse_by_predictor["persistence"], atol=1e-9)
    return {"base_1999": base, "obs_2000_2004": obs, "hand_rmse": hand_rmse}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=ROOT / "data" / "noaa_global_temp_anomaly_1880_2025.csv")
    parser.add_argument("--json-out", type=Path, default=Path(__file__).with_name("verify_rolling_origin_results.json"))
    args = parser.parse_args()

    data_path = args.data.resolve()
    checks = [
        ("scope_violations", check_scope_violations),
        ("toy_series_hand_rmse", check_toy_series_hand_rmse),
        ("noaa_rolling_matches_astra", lambda: check_noaa_rolling_matches_astra(data_path)),
        ("origin_1999_hand_verify", lambda: check_origin_1999_hand_verify(data_path)),
    ]

    report = {
        "package": "NONSTATIONARY_ROADMAP.md package 1 (rolling-origin evaluation)",
        "source": "prompts/Answers/nicht_stationäre_Treiber/SCF_Nichtstationaere_Treiber_und_Kippen.md",
        "timestamp": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "python": sys.version.split()[0],
        "numpy": np.__version__,
        "platform": platform.platform(),
        "checks": {},
        "disclaimer": (
            "Rolling-origin results are a materially more robust comparison "
            "than a single split but remain a retrospective diagnosis on "
            "already-published historical data, not a prospective forecast "
            "evaluation -- same caveat Astra's review raised about Pilot B/C."
        ),
    }
    passed = 0
    failed = 0
    errors = []
    for name, fn in checks:
        try:
            report["checks"][name] = {"status": "passed", "detail": fn()}
            passed += 1
            print(f"PASS  {name}")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            errors.append({"check": name, "error": f"{type(exc).__name__}: {exc}"})
            report["checks"][name] = {"status": "failed", "error": f"{type(exc).__name__}: {exc}"}
            print(f"FAIL  {name}: {exc}")

    summary = {"count": len(checks), "passed": passed, "failed": failed, "errors": errors, "report": report}
    args.json_out.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(f"\n{passed}/{len(checks)} passed; wrote {args.json_out}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
