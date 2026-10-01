"""Muonium gravity pilot CLI (Paket MU7, MUONIUM_GRAVITY_ROADMAP.md).

Runs ONE synthetic scenario of the idealised three-plane model and prints
standard JSON naming assumptions, identifiability, profile modes, bounds
and the uncertainty type. Every number is a synthetic or analytic result
of declared design assumptions -- not a measurement of muonium gravity.

    python scripts/run_muonium_pilot.py --scenario ideal|offset|reversal|velocity_mixture|aliases
        [--seed 0] [--a-min A --a-max B] [--g-ref 9.81] [--output FILE]

The search range (parameter space) is always printed; if not given, the
declared default is g_ref +- 0.45 d/T^2 (one alias period, excluded
aliases), except for ``aliases``, which deliberately spans several periods.
"""
from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from scoped_correspondence.muonium.design import deviance_interval  # noqa: E402
from scoped_correspondence.muonium.evidence import EvidenceRecord, dumps, real_data_check  # noqa: E402
from scoped_correspondence.muonium.forward import ForwardModel, VelocityClass, equal_time_bins  # noqa: E402
from scoped_correspondence.muonium.identifiability import offset_degeneracy, parity_table  # noqa: E402
from scoped_correspondence.muonium.likelihood import multistart_fit, poisson_nll  # noqa: E402

TAU, D, V = 2.2e-6, 100e-9, 2180.0
T = 2 * TAU
ALIAS = D / T ** 2
BINS = equal_time_bins(4.0, [0.0, math.pi / 2, math.pi, 3 * math.pi / 2])
SCENARIOS = ("ideal", "offset", "reversal", "velocity_mixture", "aliases")
DESIGN = {"g_ref_assumed": None, "tau_s": TAU, "T_s": T, "d_m": D, "v_m_per_s": V, "contrast": 0.35,
          "note": "illustrative design assumptions (plan section 5.2), not measured values"}


def model(classes, tau=TAU, phi0=0.0):
    return ForwardModel(L=V * T, d=D, tau=tau, classes=tuple(classes), rate=2.0e6, background=1.0, phi0=phi0)


def fit_scan(m, counts, lo, hi, n_starts=12):
    nll = lambda x: poisson_nll(counts, m.expected_counts(x[0], BINS))
    fit = multistart_fit(nll, ["a"], [(lo, hi)], n_starts=n_starts)
    grid = np.linspace(lo, hi, 1201)
    ival, touches = deviance_interval(np.array([nll([a]) for a in grid]), grid)
    near = [m_.x[0] for m_ in fit.modes if m_.objective - fit.best.objective <= 1e-6]
    return {"best": fit.best.x[0], "modes_within_tolerance": sorted(near), "fit_notes": list(fit.notes),
            "deviance_set_3_84": ival, "deviance_set_touches_search_bound": touches,
            "interval_method": "profile deviance <= 3.84 on the declared grid (asymptotic reference only)"}


def run(scenario, seed, lo, hi, g_ref):
    rng = np.random.default_rng(seed)
    one = [VelocityClass(V, 1.0, transmission=0.5, contrast=0.35)]
    out = {"scenario": scenario, "seed": seed, "parameter_space": {"a_min": lo, "a_max": hi, "unit": "m/s^2"},
           "design": dict(DESIGN, g_ref_assumed=g_ref), "real_data": real_data_check()}
    if scenario in ("ideal", "aliases"):
        m = model(one)
        counts = rng.poisson(m.expected_counts(g_ref, BINS)).tolist()
        res = fit_scan(m, counts, lo, hi, n_starts=24 if scenario == "aliases" else 12)
        rec = EvidenceRecord("synthetic_measurement", f"injected a = g_ref = {g_ref}; estimate from Poisson counts",
                             ("design",), ("phi0 known (= 0)", "contrast and rate known", "single velocity", "equal flight times"), res,
                             ("synthetic data only", f"alias period d/T^2 = {ALIAS:.6g} m/s^2: values differing by it give the same counts"))
        out["identifiability"] = "a identified up to the periodic alias d/T^2 within the declared range"
    elif scenario == "offset":
        r = offset_degeneracy(3)
        rec = EvidenceRecord("analytic_result", "one flight time with a free phase offset", (),
                             ("unwrapped phase phi = K a + phi0",), {"identifiable": list(r.identifiable), "not_identifiable": list(r.not_identifiable),
                                                                     "symmetry": r.witnesses[0]["symmetry"]},
                             ("structural: more counts do not help",))
        out["identifiability"] = "a NOT identifiable (exact affine analysis)"
    elif scenario == "reversal":
        r = parity_table({"grating_offset": "even", "declared_odd_disturbance": "odd"})
        rec = EvidenceRecord("analytic_result", "orientation reversal with declared parities", (),
                             tuple(r.assumptions), {"identifiable": list(r.identifiable), "not_identifiable": list(r.not_identifiable),
                                                    "parities": r.witnesses[0]}, tuple(r.notes))
        out["identifiability"] = "only A + (odd terms) identifiable; reversal does not prove gravity"
    else:  # velocity_mixture
        classes = [VelocityClass(1500.0, 0.5, transmission=0.5, contrast=0.35), VelocityClass(3000.0, 0.5, transmission=0.5, contrast=0.35)]
        truth, naive = model(classes), model(classes, tau=1.0)
        ph = truth.modulation_phase(g_ref)
        fit = multistart_fit(lambda x: math.remainder(naive.modulation_phase(x[0]) - ph, 2 * math.pi) ** 2, ["a"], [(lo, hi)], n_starts=8)
        rec = EvidenceRecord("synthetic_measurement", "fit with the INCOMING instead of the detected velocity mixture", ("design",),
                             ("noise-free expected phase", "two velocity classes"),
                             {"a_fit_naive": fit.best.x[0], "a_true": g_ref, "bias": fit.best.x[0] - g_ref,
                              "detected_weights": truth.detected_weights()},
                             ("selection bias of the mixture, not a property of gravity",))
        out["identifiability"] = "biased unless the detected mixture is modelled"
    out["result"] = rec.to_dict()
    out["uncertainty_type"] = {"ideal": "Poisson counting + asymptotic deviance reference", "aliases": "periodic aliases",
                               "offset": "structural non-identifiability", "reversal": "structural (parity)",
                               "velocity_mixture": "model misspecification bias"}[scenario]
    out["headline"] = f"synthetic {scenario} scenario of an idealised model -- no statement about measured muonium gravity"
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--scenario", choices=SCENARIOS, required=True)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--g-ref", type=float, default=9.81)
    ap.add_argument("--a-min", type=float, default=None)
    ap.add_argument("--a-max", type=float, default=None)
    ap.add_argument("--output", type=Path, default=None)
    args = ap.parse_args(argv)
    span = 2.5 if args.scenario == "aliases" else 0.45
    lo = args.a_min if args.a_min is not None else args.g_ref - (0.5 if args.scenario == "aliases" else span) * ALIAS
    hi = args.a_max if args.a_max is not None else args.g_ref + span * ALIAS
    if not lo < hi:
        ap.error("--a-min must be smaller than --a-max")
    text = dumps(run(args.scenario, args.seed, lo, hi, args.g_ref))
    if args.output:
        args.output.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
