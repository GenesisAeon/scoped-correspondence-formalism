#!/usr/bin/env python3
"""Hand-checkable verification for Contraction Analysis (Milestone 14).

Checks (all numbers from this script run):
  1. Example A: a=-1, tau=1 → rate=1.0, is_globally_contracting=True;
     finite-diff on cusp_field confirms f' <= -1
  2. Example B: a=1, tau=1 → rate=None, is_globally_contracting=False
     (bistability scope, not an error)
  3. Example C: a=-2, tau=2 → rate=1.0; FD bound holds
  4. Analytical: sup f' = a/tau at x=0; source cites Lohmiller & Slotine DOI

Stdlib only (math). JSON {count, passed, failed, report}; numbers from this run.
Calls real cusp_field (dynamics/core.py unchanged; CALL only).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import platform
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from scoped_correspondence.dynamics.contraction import (  # noqa: E402
    METRIC_EUCLIDEAN_1D,
    SOURCE,
    ContractionCertificate,
    contraction_rate_cusp,
    make_contraction_certificate,
    verify_contraction_bound,
)
from scoped_correspondence.dynamics.core import cusp_field  # noqa: E402
from scoped_correspondence.errors import ScopeViolationError  # noqa: E402


def require(ok, msg):
    if not bool(ok):
        raise AssertionError(msg)


def near(a, b, atol=1e-9, rtol=1e-9):
    if not math.isclose(float(a), float(b), abs_tol=atol, rel_tol=rtol):
        raise AssertionError(f"{a!r} != {b!r}")


SAMPLES = [-2.0, -1.0, -0.5, 0.0, 0.5, 1.0, 2.0]


def check_example_a_contracting():
    """a=-1, tau=1 → rate=1.0 True; FD f' <= -1."""
    a, tau = -1.0, 1.0
    rate = contraction_rate_cusp(a, tau)
    near(rate, 1.0)
    cert = verify_contraction_bound(a, tau, SAMPLES)
    require(isinstance(cert, ContractionCertificate), "cert type")
    near(cert.rate, 1.0)
    require(cert.is_globally_contracting is True, "globally contracting")
    require(cert.metric == METRIC_EUCLIDEAN_1D, "metric")
    require(cert.a == a and cert.tau == tau, "params")
    require(cert.max_estimated_fprime is not None, "max_fp set")
    # Analytical f' at 0 is a/tau = -1; FD should be near that and <= -rate
    require(cert.max_estimated_fprime <= -rate + 1e-4, "max_fp <= -rate")
    # Direct FD at x=0 via cusp_field CALL
    eps = 1e-6
    fp0 = (cusp_field(eps, a, 0.0, tau) - cusp_field(-eps, a, 0.0, tau)) / (2 * eps)
    near(fp0, a / tau, atol=1e-6)
    require(fp0 <= -rate + 1e-5, "fp0 <= -rate")
    return {
        "a": a,
        "tau": tau,
        "rate": cert.rate,
        "is_globally_contracting": cert.is_globally_contracting,
        "max_estimated_fprime": cert.max_estimated_fprime,
        "fp0_finite_diff": fp0,
        "sup_fprime_analytical": a / tau,
        "n_samples": cert.n_samples,
        "source": cert.source,
    }


def check_example_b_bistability_scope():
    """a=1, tau=1 → rate=None False (bistability scope, not error)."""
    a, tau = 1.0, 1.0
    rate = contraction_rate_cusp(a, tau)
    require(rate is None, f"rate expected None, got {rate!r}")
    cert = verify_contraction_bound(a, tau, SAMPLES)
    require(cert.rate is None, "cert.rate None")
    require(cert.is_globally_contracting is False, "not globally contracting")
    require(cert.metric == METRIC_EUCLIDEAN_1D, "metric")
    # Must NOT raise — bistability scope
    analytical = make_contraction_certificate(a, tau)
    require(analytical.rate is None, "analytical None")
    require(analytical.is_globally_contracting is False, "analytical False")
    # sup f' = a/tau = +1 > 0
    near(a / tau, 1.0)
    return {
        "a": a,
        "tau": tau,
        "rate": None,
        "is_globally_contracting": False,
        "sup_fprime_analytical": a / tau,
        "note": "bistability / non-contraction scope — not an error",
        "max_estimated_fprime": cert.max_estimated_fprime,
        "raised": False,
    }


def check_example_c_scaled():
    """a=-2, tau=2 → rate=1.0; FD bound holds."""
    a, tau = -2.0, 2.0
    rate = contraction_rate_cusp(a, tau)
    near(rate, 1.0)
    cert = verify_contraction_bound(a, tau, SAMPLES)
    near(cert.rate, 1.0)
    require(cert.is_globally_contracting is True, "contracting")
    require(cert.max_estimated_fprime <= -rate + 1e-4, "bound")
    return {
        "a": a,
        "tau": tau,
        "rate": cert.rate,
        "is_globally_contracting": True,
        "max_estimated_fprime": cert.max_estimated_fprime,
        "sup_fprime_analytical": a / tau,
    }


def check_source_and_sup_identity():
    """Source cites Lohmiller & Slotine DOI; sup f'=a/tau at x=0."""
    require("Lohmiller" in SOURCE, "Lohmiller in SOURCE")
    require("Slotine" in SOURCE, "Slotine in SOURCE")
    require("10.1016/S0005-1098(98)00019-3" in SOURCE, "DOI in SOURCE")
    # For several (a,tau), analytical rate matches -a/tau when a<0
    cases = [(-0.5, 1.0), (-3.0, 1.5), (-1.0, 0.5)]
    rows = []
    for a, tau in cases:
        rate = contraction_rate_cusp(a, tau)
        near(rate, -a / tau)
        # Analytical f'(0) = a/tau via cusp_field FD
        eps = 1e-6
        fp0 = (
            cusp_field(eps, a, 0.0, tau) - cusp_field(-eps, a, 0.0, tau)
        ) / (2 * eps)
        near(fp0, a / tau, atol=1e-5)
        rows.append({"a": a, "tau": tau, "rate": rate, "fp0": fp0})
    # a=0 → None
    require(contraction_rate_cusp(0.0, 1.0) is None, "a=0 → None")
    # tau<=0 raises
    raised = False
    try:
        contraction_rate_cusp(-1.0, 0.0)
    except ScopeViolationError:
        raised = True
    require(raised, "tau=0 raises ScopeViolationError")
    return {
        "source": SOURCE,
        "doi": "10.1016/S0005-1098(98)00019-3",
        "metric": METRIC_EUCLIDEAN_1D,
        "cases": rows,
        "a0_rate_is_none": True,
        "tau0_raises": True,
    }


CHECKS = [
    ("example_a_a_neg1_rate_1", check_example_a_contracting),
    ("example_b_a_pos1_rate_none_bistability", check_example_b_bistability_scope),
    ("example_c_a_neg2_tau2_rate_1", check_example_c_scaled),
    ("source_lohmiller_slotine_sup_identity", check_source_and_sup_identity),
]


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--json-out",
        type=Path,
        default=Path(__file__).with_name("verify_contraction_core_results.json"),
    )
    args = p.parse_args(argv)

    report = {
        "checks": {},
        "meta": {
            "milestone": "M14",
            "title": "Contraction Analysis",
            "platform": platform.platform(),
            "python": sys.version.split()[0],
            "timestamp_utc": dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z"),
            "source": SOURCE,
        },
    }
    passed = 0
    failed = 0
    errors = []

    for name, fn in CHECKS:
        try:
            detail = fn()
            report["checks"][name] = {"status": "passed", "detail": detail}
            passed += 1
            print(f"PASS  {name}")
        except Exception as exc:  # noqa: BLE001 — collect all failures
            failed += 1
            errors.append({"check": name, "error": f"{type(exc).__name__}: {exc}"})
            report["checks"][name] = {
                "status": "failed",
                "error": f"{type(exc).__name__}: {exc}",
            }
            print(f"FAIL  {name}: {exc}")

    out = {
        "count": len(CHECKS),
        "passed": passed,
        "failed": failed,
        "errors": errors,
        "report": report,
    }
    args.json_out.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(f"\n{passed}/{len(CHECKS)} passed; wrote {args.json_out}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
