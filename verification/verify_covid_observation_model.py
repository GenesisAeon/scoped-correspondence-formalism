#!/usr/bin/env python3
"""COVID count observation model: testing overdispersion on real raw daily counts (Milestone 52).

MECHANISTIC_VALIDATION_ROADMAP.md package 5, response to
prompts/Answers/nicht_stationäre_Treiber/SCF_Review_f8e249f.md (Astra,
2026-09-21): "Negativ-Binomial-Beobachtungsmodell für Überdispersion
(Notwendigkeit über Residuen/Prognosescores prüfen, nicht a priori
annehmen)" and "Echte tägliche Rohzahlen statt überlappender
Siebentagesmittel als Zählmodell-Eingabe."

Checks (all numbers from this script run):
  1. neg_binom_log_score at dispersion=0 exactly equals poisson_log_score
     (the Poisson limit); ScopeViolationError for negative dispersion /
     non-positive predicted_mean / non-integer observed_count.
  2. fit_neg_binom_dispersion recovers a KNOWN true dispersion parameter
     from simulated NB-distributed data (scipy.stats.nbinom.rvs) to
     within normal sampling error -- an independent recovery check, not
     a self-consistency tautology.
  3. On the REAL raw World daily case counts (2020-01-28 to 2020-03-25),
     with dispersion fit on a CALIB half and evaluated (Poisson vs.
     negative-binomial log-score) on a disjoint HOLDOUT half: the
     negative-binomial model wins decisively (much lower mean log-score)
     and the fitted dispersion is strictly positive -- genuine
     overdispersion, TESTED not assumed, and not a circular result
     (dispersion fit and evaluation windows are disjoint).

IMPORTANT SCOPE LIMITATION: cases_7day_avg is used as a GIVEN reference
mean (not independently modeled) -- a full latent-state/observation-
process separation (e.g. a state-space model for the true latent
incidence) is a larger undertaking, left for future work.
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
from scipy.stats import nbinom as nbinom_dist

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from scoped_correspondence.errors import ScopeViolationError  # noqa: E402
from scoped_correspondence.validation.scoring_rules import (  # noqa: E402
    fit_neg_binom_dispersion,
    neg_binom_log_score,
    poisson_log_score,
)
from scoped_correspondence.validation.covid_observation_model import (  # noqa: E402
    DATA_PROVENANCE_NOTE,
    SOURCE,
    run_covid_observation_model_comparison,
)


def require(ok, msg):
    if not bool(ok):
        raise AssertionError(msg)


def near(a, b, atol=1e-9):
    if abs(float(a) - float(b)) > atol:
        raise AssertionError(f"{a!r} != {b!r} (atol={atol})")


def check_neg_binom_log_score_hand_checks():
    poisson_limit = neg_binom_log_score(7, 5.5, 0.0)
    hand_poisson = poisson_log_score(7, 5.5)
    near(poisson_limit, hand_poisson, atol=1e-12)

    bad_dispersion = False
    try:
        neg_binom_log_score(3, 5.0, -0.1)
    except ScopeViolationError:
        bad_dispersion = True
    require(bad_dispersion, "expected ScopeViolationError for negative dispersion")

    bad_mean = False
    try:
        neg_binom_log_score(3, -1.0, 0.2)
    except ScopeViolationError:
        bad_mean = True
    require(bad_mean, "expected ScopeViolationError for non-positive predicted_mean")

    bad_count = False
    try:
        neg_binom_log_score(3.5, 5.0, 0.2)
    except ScopeViolationError:
        bad_count = True
    require(bad_count, "expected ScopeViolationError for non-integer observed_count")

    return {
        "poisson_limit_score": poisson_limit,
        "hand_poisson_score": hand_poisson,
        "raised_on_negative_dispersion": bad_dispersion,
        "raised_on_bad_mean": bad_mean,
        "raised_on_bad_count": bad_count,
    }


def check_fit_neg_binom_dispersion_recovery():
    rng = np.random.default_rng(42)
    mu_true, alpha_true = 200.0, 0.08
    p = 1.0 / (1.0 + alpha_true * mu_true)
    n = mu_true * p / (1.0 - p)
    sim = nbinom_dist.rvs(n, p, size=3000, random_state=rng)
    means = np.full(3000, mu_true)
    fitted = fit_neg_binom_dispersion(sim, means)
    # Generous tolerance: MLE from a finite sample, not an exact identity.
    require(abs(fitted - alpha_true) < 0.03, f"fitted dispersion {fitted!r} too far from true {alpha_true!r}")

    too_few = False
    try:
        fit_neg_binom_dispersion([1, 2], [1.0])
    except ScopeViolationError:
        too_few = True
    require(too_few, "expected ScopeViolationError for mismatched lengths")

    return {"true_dispersion": alpha_true, "fitted_dispersion": fitted, "n_simulated": 3000, "raised_on_mismatched_lengths": too_few}


def check_real_data_overdispersion(data_path):
    report = run_covid_observation_model_comparison(data_path)
    require(report.n_calib >= 10 and report.n_holdout >= 10, "expected a substantial calib/holdout split")
    require(report.fitted_dispersion > 0, "expected genuine overdispersion (dispersion > 0), not assumed but tested")
    require(
        report.neg_binom_wins,
        f"expected negative-binomial to win on real raw daily counts; poisson={report.mean_poisson_log_score_holdout!r} nb={report.mean_neg_binom_log_score_holdout!r}",
    )
    require(
        report.mean_neg_binom_log_score_holdout < report.mean_poisson_log_score_holdout / 2,
        "expected a decisive (not marginal) improvement from allowing overdispersion",
    )
    return report.to_dict()


CHECKS = [
    ("neg_binom_log_score_hand_checks", check_neg_binom_log_score_hand_checks),
    ("fit_neg_binom_dispersion_recovery", check_fit_neg_binom_dispersion_recovery),
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=ROOT / "data" / "owid_covid_world_daily_2020_2023.csv")
    parser.add_argument("--json-out", type=Path, default=Path(__file__).with_name("verify_covid_observation_model_results.json"))
    args = parser.parse_args()

    data_path = args.data.resolve()
    checks = CHECKS + [("real_data_overdispersion", lambda: check_real_data_overdispersion(data_path))]

    report = {
        "package": "MECHANISTIC_VALIDATION_ROADMAP.md package 5 (COVID observation model)",
        "source": SOURCE,
        "data_provenance_note": DATA_PROVENANCE_NOTE,
        "timestamp": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "python": sys.version.split()[0],
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "platform": platform.platform(),
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
