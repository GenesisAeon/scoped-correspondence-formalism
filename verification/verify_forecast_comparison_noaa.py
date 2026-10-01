"""J1 real-data adapter check (SCOPE_COMPOSITION_EVIDENCE_ROADMAP.md, plan
section 7 "Kontrollen und Pilot"): paired forecast comparison on the
provenance-checked NOAA global annual anomaly series.

The pilot design (models, origins, horizons, loss, lag rule, primary =
descriptive) is fixed in ``validation/forecast_comparison_pilot.py``
BEFORE results were inspected. These checks do NOT assert that any model
"wins"; they assert that

- the data match the manifest hash,
- pairing is complete and every point accounted for,
- the PRIMARY results are descriptive only (no inference released),
- the CONDITIONAL results carry their declared assumption,
- the mean losses agree with an independent route through the existing
  ``error_by_horizon_step`` (RMSE^2), and
- the conditional DM statistic agrees with an independent NumPy HAC
  implementation written here (not imported from the module).

Real data -> registered as "data" in run_verification_suite.py.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "src"))

from scoped_correspondence.validation.forecast_comparison import describe_comparison
from scoped_correspondence.validation.forecast_comparison_pilot import (
    DATA_ID,
    FIRST_ORIGIN,
    HORIZONS,
    MODEL_A,
    MODEL_B,
    declared_lag,
    run_noaa_paired_comparison,
)
from scoped_correspondence.validation.noaa_temp_pilot import (
    _last_30_years_linear_predictor,
    _persistence_predictor,
    load_annual_anomalies,
)
from scoped_correspondence.validation.rolling_origin import error_by_horizon_step


def require(condition, msg=""):
    if not condition:
        raise AssertionError(msg)


PILOT = run_noaa_paired_comparison(REPO)


def _independent_hac_dm(d: np.ndarray, lag: int) -> float:
    n = d.size
    c = d - d.mean()
    acov = np.array([np.dot(c[l:], c[: n - l]) / n for l in range(lag + 1)])
    weights = 1.0 - np.arange(1, lag + 1) / (lag + 1.0)
    v = acov[0] + 2.0 * np.dot(weights, acov[1:])
    return float(d.mean() / math.sqrt(v / n))


def check_provenance_matches_manifest():
    manifest = json.loads((REPO / "data" / "real_data_manifest.json").read_text(encoding="utf-8"))
    entry = next(d for d in manifest["datasets"] if d["id"] == DATA_ID)
    require(PILOT.provenance["sha256"] == entry["sha256"], "sha256 must match the manifest")
    return {"file": PILOT.provenance["file"], "sha256": PILOT.provenance["sha256"]}


def check_pairing_complete_and_accounted():
    points = load_annual_anomalies(REPO / PILOT.provenance["file"])
    last_year = points[-1].year
    out = {}
    for h, rep in zip(HORIZONS, PILOT.pairing):
        expected = last_year - h - FIRST_ORIGIN + 1
        require(rep.n_requested_a == rep.n_requested_b == rep.n_paired == expected, f"h={h}: expected {expected} paired, got {rep.to_dict()}")
        require(not rep.excluded and not rep.invalid, f"h={h}: nothing may be excluded/invalid on this complete series")
        require(all(r.horizon == h for r in rep.records), f"h={h}: only the declared horizon may be paired")
        out[f"h{h}"] = rep.n_paired
    return out


def check_primary_is_descriptive_only():
    out = {}
    for r in PILOT.primary:
        require(r.inference_status == "not_applicable" and "applicability_not_declared" in r.inference_reasons, "primary must not release inference")
        require(r.dm_statistic is None and r.p_value_two_sided is None and r.confidence_interval is None, "primary inferential fields must be empty")
        text = describe_comparison(r)
        require("descriptive comparison only" in text and f"horizon {r.horizon}" in text and "squared_error" in text, text)
        out[f"h{r.horizon}"] = {"mean_loss_difference": r.mean_loss_difference, "direction": r.descriptive_direction, "sentence": text}
    return out


def check_conditional_carries_declared_assumption():
    out = {}
    for r in PILOT.conditional:
        require(r.applicability.declared_justified and "ASSUMED, not tested" in r.applicability.justification, "conditional result must carry its assumption text")
        require(r.inference_status == "asymptotic_normal_reference", f"h={r.horizon}: conditional inference expected, got {r.inference_status}")
        require(r.hac_lag == declared_lag(r.horizon, r.n), "lag must follow the pre-declared rule")
        out[f"h{r.horizon}"] = {"dm": r.dm_statistic, "p": r.p_value_two_sided, "ci": list(r.confidence_interval), "lag": r.hac_lag,
                                "sentence": describe_comparison(r)}
    return out


def check_mean_losses_match_existing_error_by_horizon_step():
    points = load_annual_anomalies(REPO / PILOT.provenance["file"])
    years = np.array([p.year for p in points], dtype=float)
    temps = np.array([p.anomaly_c for p in points], dtype=float)
    out = {}
    for r in PILOT.primary:
        h = r.horizon
        origins = [float(o) for o in range(FIRST_ORIGIN, int(years[-1]) - h + 1)]
        rep = error_by_horizon_step(years, temps, origins=origins, max_horizon_steps=h, step_size=1.0,
                                    predictors={MODEL_A: _last_30_years_linear_predictor, MODEL_B: _persistence_predictor})
        msa, msb = rep.rmse_by_step[MODEL_A][h] ** 2, rep.rmse_by_step[MODEL_B][h] ** 2
        require(math.isclose(msa, r.mean_loss_a, rel_tol=1e-10) and math.isclose(msb, r.mean_loss_b, rel_tol=1e-10),
                f"h={h}: mean losses disagree with error_by_horizon_step: {msa} vs {r.mean_loss_a}, {msb} vs {r.mean_loss_b}")
        out[f"h{h}"] = {"mse_a": msa, "mse_b": msb}
    return out


def check_conditional_dm_matches_independent_numpy_hac():
    out = {}
    for rep, r in zip(PILOT.pairing, PILOT.conditional):
        recs = sorted(rep.records, key=lambda x: x.origin)
        d = np.array([(x.observed - x.prediction_a) ** 2 - (x.observed - x.prediction_b) ** 2 for x in recs])
        dm = _independent_hac_dm(d, r.hac_lag)
        require(math.isclose(dm, r.dm_statistic, rel_tol=1e-10), f"h={r.horizon}: DM {r.dm_statistic} vs independent {dm}")
        out[f"h{r.horizon}"] = dm
    return out


CHECKS = [
    check_provenance_matches_manifest,
    check_pairing_complete_and_accounted,
    check_primary_is_descriptive_only,
    check_conditional_carries_declared_assumption,
    check_mean_losses_match_existing_error_by_horizon_step,
    check_conditional_dm_matches_independent_numpy_hac,
]


def main():
    results = {}
    n_passed = 0
    for check in CHECKS:
        name = check.__name__.removeprefix("check_")
        try:
            results[name] = check()
            print(f"PASS  {name}")
            n_passed += 1
        except AssertionError as e:
            results[name] = {"error": str(e)}
            print(f"FAIL  {name}: {e}")
        except Exception as e:
            results[name] = {"error": f"{type(e).__name__}: {e}"}
            print(f"ERROR {name}: {type(e).__name__}: {e}")
    print(f"\n{n_passed}/{len(CHECKS)} checks passed")
    out_path = Path(__file__).with_name("verify_forecast_comparison_noaa_results.json")
    out_path.write_text(json.dumps({"n_passed": n_passed, "n_total": len(CHECKS), "data_file": PILOT.provenance["file"],
                                    "results": results}, indent=2, default=str, allow_nan=False))
    print(f"Report written to {out_path}")
    return 0 if n_passed == len(CHECKS) else 1


if __name__ == "__main__":
    raise SystemExit(main())
