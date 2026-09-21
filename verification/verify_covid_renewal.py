#!/usr/bin/env python3
"""COVID renewal-equation R_t estimator (Milestone 44) -- real per-row data.

NONSTATIONARY_ROADMAP.md package 5a, response to
prompts/Answers/nicht_stationäre_Treiber/SCF_Nichtstationaere_Treiber_und_Kippen.md
(Astra, 2026-09-21) section 5.4: a genuine renewal-equation R_t estimator
(Cori et al. 2013), rather than another global exponential curve, applied
to the same real World COVID series as covid_pilot.py.

Checks (all numbers from this script run):
  1. discretized_generation_interval sums to 1, has zero mass at s=0, and
     matches a hand-recomputed Gamma discretization for a spot-checked s.
  2. Self-consistency: for pure exponential growth I_t=I_0*e^{r t}, the
     directly-computed instantaneous_r is CONSTANT and matches
     wallinga_lipsitch_r(r) exactly (to floating-point precision) -- the
     renewal-equation estimator and the closed-form relation must agree
     on their own shared assumption.
  3. run_covid_renewal_analysis on the real World series: R_t dips below
     1 during the documented containment/dip period (late Feb 2020) and
     rises well above 1 during the global-acceleration period (March
     2020) -- consistent with, but independently computed from, the
     component-decomposition finding in covid_country_decomposition.py.
  4. Cross-check: Wallinga-Lipsitch R implied by Pilot A's near-flat rate
     is close to the epidemic threshold (R~1); implied by Pilot B's
     fast-growth rate is close to the directly-computed March R_t values
     (both ~1.5-1.9) -- two independent methods agreeing.
  5. Scope violations: degenerate generation-interval parameters, too-short
     incidence series for instantaneous_r.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import platform
import sys
from pathlib import Path

import numpy as np
import scipy
from scipy.stats import gamma as gamma_dist

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from scoped_correspondence.errors import ScopeViolationError  # noqa: E402
from scoped_correspondence.validation.covid_renewal import (  # noqa: E402
    DATA_PROVENANCE_NOTE as RENEWAL_DATA_PROVENANCE_NOTE,
    DEFAULT_S_MAX,
    GENERATION_INTERVAL_MEAN_DAYS,
    GENERATION_INTERVAL_SD_DAYS,
    discretized_generation_interval,
    instantaneous_r,
    run_covid_renewal_analysis,
    wallinga_lipsitch_r,
)
from scoped_correspondence.validation.covid_pilot import fit_exponential_growth, run_covid_pilot  # noqa: E402
from scoped_correspondence.validation.covid_pilot import (  # noqa: E402
    run_covid_pilot_short_window,
)


def require(ok, msg):
    if not bool(ok):
        raise AssertionError(msg)


def near(a, b, atol=1e-6):
    if abs(float(a) - float(b)) > atol:
        raise AssertionError(f"{a!r} != {b!r} (atol={atol})")


def check_generation_interval_hand_check():
    w = discretized_generation_interval()
    require(abs(float(np.sum(w)) - 1.0) < 1e-12, "weights must sum to 1")
    require(w[0] == 0.0, "no zero-day generation interval")
    require(len(w) == DEFAULT_S_MAX + 1, "weights array length must be s_max+1")

    # Hand recompute w[3] directly from the Gamma CDF, independent of the module.
    theta = GENERATION_INTERVAL_SD_DAYS**2 / GENERATION_INTERVAL_MEAN_DAYS
    k = GENERATION_INTERVAL_MEAN_DAYS / theta
    hand_w3 = gamma_dist.cdf(3.5, a=k, scale=theta) - gamma_dist.cdf(2.5, a=k, scale=theta)
    hand_w3_normalized = hand_w3 / sum(
        gamma_dist.cdf(s + 0.5, a=k, scale=theta) - gamma_dist.cdf(s - 0.5, a=k, scale=theta) for s in range(1, DEFAULT_S_MAX + 1)
    )
    near(w[3], hand_w3_normalized, atol=1e-12)

    degenerate = False
    try:
        discretized_generation_interval(mean_days=-1.0)
    except ScopeViolationError:
        degenerate = True
    require(degenerate, "expected ScopeViolationError for non-positive mean_days")

    return {"weights_sum": float(np.sum(w)), "w0": float(w[0]), "hand_checked_w3": float(w[3])}


def check_self_consistency_exponential_growth():
    w = discretized_generation_interval()
    r_true = 0.1
    n = 200
    incidence = np.exp(r_true * np.arange(n))
    r_t = instantaneous_r(incidence, w)
    wl = wallinga_lipsitch_r(r_true, w)
    tail = r_t[~np.isnan(r_t)][-50:]
    require(np.allclose(tail, wl, atol=1e-8), "instantaneous_r must be constant and match wallinga_lipsitch_r for pure exponential growth")

    too_short = False
    try:
        instantaneous_r(np.array([1.0, 2.0]), w)
    except ScopeViolationError:
        too_short = True
    require(too_short, "expected ScopeViolationError for too-short incidence series")

    return {"r_true": r_true, "wallinga_lipsitch_R": wl, "instantaneous_r_tail_mean": float(tail.mean()), "matches": True}


def check_real_data_r_t_shape(data_path):
    report = run_covid_renewal_analysis(data_path)
    dates = report.dates
    r_t = report.r_t
    by_date = dict(zip(dates, r_t))

    dip_dates = [d for d in dates if "2020-02-20" <= d <= "2020-02-28"]
    require(len(dip_dates) > 0, "dip window must be present in the data")
    dip_values = [by_date[d] for d in dip_dates if not np.isnan(by_date[d])]
    require(len(dip_values) > 0, "dip window must have computable R_t values")
    require(min(dip_values) < 1.0, f"R_t must dip below 1 during the containment period, got min={min(dip_values)!r}")

    late_dates = [d for d in dates if d >= "2020-03-15"]
    require(len(late_dates) > 0, "late window must be present")
    late_values = [by_date[d] for d in late_dates if not np.isnan(by_date[d])]
    require(len(late_values) > 0, "late window must have computable R_t values")
    require(min(late_values) > 1.3, f"R_t must be well above 1 during the acceleration phase, got min={min(late_values)!r}")

    return {
        "n_dates": len(dates),
        "dip_window_min_Rt": min(dip_values),
        "late_window_min_Rt": min(late_values),
        "late_window_max_Rt": max(late_values),
    }


def check_wallinga_lipsitch_cross_check(data_path):
    report_a, fit_a = run_covid_pilot(data_path)
    report_b, fit_b = run_covid_pilot_short_window(data_path)
    renewal = run_covid_renewal_analysis(
        data_path,
        cross_check_rates={"Pilot_A": fit_a.r, "Pilot_B": fit_b.r},
    )
    r_implied_a = renewal.wallinga_lipsitch_cross_check["Pilot_A"]
    r_implied_b = renewal.wallinga_lipsitch_cross_check["Pilot_B"]
    require(abs(r_implied_a - 1.0) < 0.1, f"Pilot A's near-flat rate must imply R close to 1, got {r_implied_a!r}")
    require(1.3 < r_implied_b < 2.2, f"Pilot B's fast-growth rate must imply R in a plausible fast-growth range, got {r_implied_b!r}")

    dates = renewal.dates
    by_date = dict(zip(dates, renewal.r_t))
    late_values = [by_date[d] for d in dates if d >= "2020-03-15" and not np.isnan(by_date[d])]
    require(
        min(late_values) - 0.5 < r_implied_b < max(late_values) + 0.5,
        f"Pilot B's implied R ({r_implied_b!r}) must be in the same ballpark as the directly-computed late R_t range {min(late_values)!r}-{max(late_values)!r}",
    )

    return {
        "fitted_r_pilot_a": fit_a.r,
        "fitted_r_pilot_b": fit_b.r,
        "wallinga_lipsitch_R_pilot_a": r_implied_a,
        "wallinga_lipsitch_R_pilot_b": r_implied_b,
        "directly_computed_late_Rt_range": [min(late_values), max(late_values)],
    }


CHECKS = [
    ("generation_interval_hand_check", check_generation_interval_hand_check),
    ("self_consistency_exponential_growth", check_self_consistency_exponential_growth),
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=ROOT / "data" / "owid_covid_world_daily_2020_2023.csv")
    parser.add_argument("--json-out", type=Path, default=Path(__file__).with_name("verify_covid_renewal_results.json"))
    args = parser.parse_args()

    data_path = args.data.resolve()
    checks = CHECKS + [
        ("real_data_r_t_shape", lambda: check_real_data_r_t_shape(data_path)),
        ("wallinga_lipsitch_cross_check", lambda: check_wallinga_lipsitch_cross_check(data_path)),
    ]

    report = {
        "package": "NONSTATIONARY_ROADMAP.md package 5a (COVID renewal-equation R_t)",
        "source": "prompts/Answers/nicht_stationäre_Treiber/SCF_Nichtstationaere_Treiber_und_Kippen.md",
        "timestamp": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "python": sys.version.split()[0],
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "platform": platform.platform(),
        "data_provenance_note": RENEWAL_DATA_PROVENANCE_NOTE,
        "checks": {},
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
