#!/usr/bin/env python3
"""Equivalence checks for Coupling core (Milestone 2).

Matches legacy verify_formalism.py:
  - p06_heat_balance_and_relaxation

Plus GENERIC structure check (structure only) and A_ij / L_ij type separation.
Stdlib + NumPy. JSON {count, passed, failed, report}.
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

from scoped_correspondence import (  # noqa: E402
    AijInfluence,
    GENERIC_STRUCTURE_TOL,
    LijTransport,
    PairwiseCoupling,
    check_generic_structure,
)
from scoped_correspondence.legacy import (  # noqa: E402
    afet_pairwise_coupling,
    generic_structure_check,
    influence_A,
    onsager_L,
)


def require(ok, msg):
    if not bool(ok):
        raise AssertionError(msg)


def near(a, b, atol=1e-12, rtol=1e-12):
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    if not np.allclose(a, b, atol=atol, rtol=rtol):
        raise AssertionError(f"{a!r} != {b!r}")


def derivative(function, x: float, h: float = 1e-5) -> float:
    return (function(x + h) - function(x - h)) / (2 * h)


def load_formalism_evidence(name: str):
    path = ROOT / "verification" / "verification_results.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    for c in data["checks"]:
        if c.get("name") == name:
            require(c["status"] == "passed", f"legacy {name} not passed")
            return c["evidence"]
    raise AssertionError(f"legacy evidence {name} missing")


def mig_cpl_p06_heat_balance_and_relaxation():
    """Reproduce p06 heat exchange via LijTransport + PairwiseCoupling."""
    expected = load_formalism_evidence("p06_heat_balance_and_relaxation")
    ca, cb, g, ta0, tb0 = 2.0, 5.0, 3.0, 310.0, 290.0
    energy0 = ca * ta0 + cb * tb0
    equilibrium = energy0 / (ca + cb)
    rate = g * (1 / ca + 1 / cb)

    def temperatures(t):
        delta = (ta0 - tb0) * math.exp(-rate * t)
        return (
            equilibrium + cb / (ca + cb) * delta,
            equilibrium - ca / (ca + cb) * delta,
        )

    # Pairwise: dot TA = -J/ca, dot TB = +J/cb with J = g*(TA-TB)
    # g_ij(zi, zj, u): for i=A,j=B -> -g*(zi-zj)/ca; for i=B,j=A -> g*(zj-zi)/cb
    coupling = PairwiseCoupling(
        f={"A": lambda z, u: 0.0, "B": lambda z, u: 0.0},
        g={
            ("A", "B"): lambda zi, zj, u: -g * (zi - zj) / ca,
            ("B", "A"): lambda zi, zj, u: g * (zj - zi) / cb,
        },
        names=("A", "B"),
    )

    records = []
    for t in (0, 0.1, 1, 10):
        ta, tb = temperatures(t)
        j = g * (ta - tb)
        force = 1 / tb - 1 / ta
        L_scalar = g * ta * tb
        production = j * force
        near(ca * ta + cb * tb, energy0)
        near(L_scalar * force, j)
        near(production, g * (ta - tb) ** 2 / (ta * tb))
        require(production >= -1e-14, "negative heat entropy production")
        near(derivative(lambda s: temperatures(s)[0], t), -j / ca, atol=2e-6)
        near(derivative(lambda s: temperatures(s)[1], t), j / cb, atol=2e-6)

        L = LijTransport(matrix=np.array([[L_scalar]]), force_names=("X_AB",))
        near(L.flux([force])[0], j)
        near(L.entropy_production([force]), production)

        rhs = coupling.rhs({"A": ta, "B": tb})
        near(rhs["A"], -j / ca, atol=1e-12)
        near(rhs["B"], j / cb, atol=1e-12)

        records.append(
            dict(t=t, TA=ta, TB=tb, J=j, X=force, L=L_scalar, entropy_production=production)
        )

    require(g / ca != g / cb, "asymmetric drift example missing")
    near((-g / ca) * (-g / cb) - (g / ca) * (g / cb), 0)
    near(g / ca + g / cb, rate)

    near(equilibrium, expected["equilibrium_K"])
    near(rate, expected["transverse_rate_per_second"])
    require(expected["neutral_mode"] == "conserved total energy", "neutral mode label")
    for got, want in zip(records, expected["trajectory"]):
        near(got["t"], want["t"])
        near(got["TA"], want["TA"])
        near(got["TB"], want["TB"])
        near(got["J"], want["J"])
        near(got["X"], want["X"])
        near(got["L"], want["L"])
        near(got["entropy_production"], want["entropy_production"])

    return {
        "equilibrium_K": equilibrium,
        "transverse_rate_per_second": rate,
        "neutral_mode": "conserved total energy",
        "trajectory": records,
        "legacy_id": "p06_heat_balance_and_relaxation",
        "legacy_alias": "VER-CPL-p06_heat_balance_and_relaxation",
    }


def mig_cpl_generic_structure_and_type_separation():
    """GENERIC structure check only; A_ij and L_ij are separate types."""
    ca, cb, conductance, ta, tb = 2.0, 5.0, 3.0, 310.0, 290.0
    J = np.zeros((2, 2))
    M = conductance * ta * tb * np.array([[1.0, -1.0], [-1.0, 1.0]])
    grad_E = np.array([1.0, 1.0])
    grad_S = np.array([1 / ta, 1 / tb])
    report = check_generic_structure(J, M, grad_E, grad_S, tol=GENERIC_STRUCTURE_TOL)
    require(report["ok"], f"GENERIC structure failed: {report}")
    near(float(generic_structure_check(J, M, grad_E, grad_S)["ok"]), 1.0)

    A = AijInfluence(
        matrix=np.array([[-1.0, 0.5], [0.2, -0.8]]), state_names=("z1", "z2")
    )
    L = LijTransport(matrix=M, force_names=("X1", "X2"))
    require(type(A) is not type(L), "A and L must be distinct classes")
    require(not issubclass(type(A), type(L)), "A must not subclass L")
    require(not issubclass(type(L), type(A)), "L must not subclass A")
    shared = set(type(A).__mro__) & set(type(L).__mro__)
    require(shared <= {object}, f"unexpected shared base beyond object: {shared}")
    require(AijInfluence not in type(L).__mro__ and LijTransport not in type(A).__mro__,
            "cross-inheritance")

    A2 = influence_A([[0.0, 1.0], [0.0, 0.0]])
    L2 = onsager_L([[2.0, 0.0], [0.0, 3.0]])
    require(isinstance(A2, AijInfluence) and isinstance(L2, LijTransport), "legacy adapters")
    _ = afet_pairwise_coupling({"x": lambda z, u: -z})

    require("Structure check only" in report["disclaimer"], "disclaimer missing")
    return {
        "generic_ok": report["ok"],
        "tol": GENERIC_STRUCTURE_TOL,
        "residuals": report["residuals"],
        "Aij_class": AijInfluence.__name__,
        "Lij_class": LijTransport.__name__,
        "shared_bases": sorted(c.__name__ for c in shared),
        "formalism_rows": ["A_ij", "L_ij"],
        "disclaimer": report["disclaimer"],
    }


CHECKS = [
    ("MIG-CPL-p06_heat_balance_and_relaxation", mig_cpl_p06_heat_balance_and_relaxation),
    ("MIG-CPL-generic_structure_and_type_separation", mig_cpl_generic_structure_and_type_separation),
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).with_name("verify_coupling_core_results.json"),
    )
    args = parser.parse_args()
    results = []
    for name, fn in CHECKS:
        try:
            evidence = fn()
            results.append({"id": name, "status": "passed", "evidence": evidence})
        except Exception as exc:
            results.append(
                {"id": name, "status": "failed", "error": f"{type(exc).__name__}: {exc}"}
            )
    passed = sum(r["status"] == "passed" for r in results)
    failed = [r["id"] for r in results if r["status"] != "passed"]
    report = {
        "milestone": "M2_coupling_core",
        "kind": "MIG equivalence (legacy verify_formalism vs Coupling API)",
        "generated_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "python": platform.python_version(),
        "numpy": np.__version__,
        "count": len(results),
        "passed": passed,
        "failed": len(failed),
        "empirical_validation": False,
        "checks": results,
    }
    args.output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    summary = {
        "count": report["count"],
        "passed": report["passed"],
        "failed": failed,
        "report": str(args.output.resolve()),
    }
    print(json.dumps(summary, ensure_ascii=False))
    raise SystemExit(0 if passed == len(results) else 1)


if __name__ == "__main__":
    main()
