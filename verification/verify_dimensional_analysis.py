"""J2 verification (SCOPE_COMPOSITION_EVIDENCE_ROADMAP.md, plan section 8):
exact dimension checks and Buckingham-Pi basis.

Pflichtprüfungen covered explicitly: J-C03 (pendulum null space, g/G),
J-C04 (year->day reservoir invariance, halo rho*r), adding different
dimensions is rejected, exp/log arguments dimensionless, rational
exponents, singular / empty / full-rank matrices with documented
semantics, basis change (span comparison, never a fixed spelling), unit
transformations, energy vs torque as a semantic WARNING, affine
temperature scales not treated as multiplicative, an abstract
dimensionless SCF quantity without an invented SI unit -- plus the
required connections to the linear reservoir module and to galaxy
quantities.

Expected values from the independent J0 derivation
(verification/plan_controls/j_series_independent_controls.py).
"""
from __future__ import annotations

import json
import math
import sys
from fractions import Fraction as F
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from scoped_correspondence.dimensions.core import (
    Add,
    Const,
    Dimension,
    Div,
    Func,
    Mul,
    Pow,
    Q,
    QuantitySpec,
    Sub,
    Unit,
    check_dimension,
    convert,
    multiplicative_scale,
    rescale_for_base_unit_change,
)
from scoped_correspondence.dimensions.pi_groups import buckingham_pi_basis, exact_null_space, same_pi_span
from scoped_correspondence.dynamics.linear_reservoirs import reservoir_step
from scoped_correspondence.errors import ScopeViolationError


def require(condition, msg=""):
    if not condition:
        raise AssertionError(msg)


def raises(fn, exc=ScopeViolationError):
    try:
        fn()
    except exc:
        return True
    return False


LEN = Dimension.of(L=1)
TIME = Dimension.of(T=1)
MASS = Dimension.of(M=1)
ACC = Dimension.of(L=1, T=-2)
G_NEWTON = Dimension.of(M=-1, L=3, T=-2)

PENDULUM = [QuantitySpec("T", TIME), QuantitySpec("l", LEN), QuantitySpec("g", ACC)]
SPECS = {s.name: s for s in PENDULUM}


def check_jc03_pendulum_null_space():
    rep = buckingham_pi_basis(PENDULUM)
    require(rep.rank == 2 and rep.nullity == 1, f"rank 2 / nullity 1 expected, got {rep.rank}/{rep.nullity}")
    require(same_pi_span(rep.basis, [(2, -1, 1)]), f"span must equal (2,-1,1), got {rep.basis}")
    pi = Div(Mul(Q("g"), Pow(Q("T"), 2)), Q("l"))
    r = check_dimension(pi, SPECS)
    require(r.status == "consistent" and r.dimension.is_dimensionless, "g T^2 / l must be dimensionless")
    g_over_G = ACC / G_NEWTON
    require(g_over_G == Dimension.of(M=1, L=-2), f"g/G must be M L^-2, got {g_over_G}")
    return {"basis": [list(b) for b in rep.basis], "monomials": list(rep.monomials), "g_over_G": g_over_G.as_dict()}


def check_jc04_reservoir_unit_change_exact_and_module():
    M0, qy, ky, ty = F(3), F(5), F(2), F(2, 5)
    year_to_day = {"T": 365}
    flow = Dimension.of(M=1, T=-1)
    rate = Dimension.of(T=-1)
    qd = rescale_for_base_unit_change(qy, flow, year_to_day)
    kd = rescale_for_base_unit_change(ky, rate, year_to_day)
    td = rescale_for_base_unit_change(ty, TIME, year_to_day)
    require((qd, kd, td) == (F(5, 365), F(2, 365), F(146)), f"rescaled values wrong: {qd}, {kd}, {td}")
    require(qd / kd == qy / ky == F(5, 2) and kd * td == ky * ty == F(4, 5), "equilibrium and exponent argument must be invariant exactly")
    # connection to dynamics/linear_reservoirs.py: same solution in both unit systems
    annual = reservoir_step(float(M0), float(qy), float(ky), float(ty))
    daily = reservoir_step(float(M0), float(qd), float(kd), float(td))
    require(math.isclose(annual, daily, rel_tol=1e-14, abs_tol=1e-14), f"reservoir_step must agree: {annual} vs {daily}")
    closed = float(qy / ky) + float(M0 - qy / ky) * math.exp(-0.8)
    require(math.isclose(annual, closed, rel_tol=1e-14), f"reservoir_step vs closed form: {annual} vs {closed}")
    return {"annual": annual, "daily": daily, "q_over_k": str(qy / ky), "k_t": str(ky * ty)}


def check_jc04_halo_product_invariance():
    rho = QuantitySpec("rho", Dimension.of(M=1, L=-3), kind="density")
    rs = QuantitySpec("r_s", LEN)
    d = check_dimension(Mul(Q("rho"), Q("r_s")), {"rho": rho, "r_s": rs})
    require(d.dimension == Dimension.of(M=1, L=-2), "rho*r has surface-density dimension M L^-2")
    # inputs rho=6, r=2, lambda=3 come from the plan's bundle (J0 finding B1)
    r, lam, rv = F(6), F(3), F(2)
    require((r / lam) * (lam * rv) == r * rv == 12, "rho*r preserved (=12)")
    require((r / lam) * (lam * rv) ** 3 != r * rv ** 3, "negative control: rho*r^3 (a mass scale) is NOT preserved")
    return {"rho_r": 12, "dimension": d.dimension.as_dict()}


def check_addition_of_different_dimensions_rejected():
    r = check_dimension(Add(Q("l"), Q("T")), SPECS)
    require(r.status == "inconsistent" and r.dimension is None and "cannot +" in r.violations[0], f"must reject: {r.to_dict()}")
    r2 = check_dimension(Sub(Mul(Q("g"), Q("T")), Div(Q("l"), Q("T"))), SPECS)
    require(r2.status == "consistent" and r2.dimension == Dimension.of(L=1, T=-1), "g*T - l/T is a velocity")
    require(raises(lambda: check_dimension(Q("unknown"), SPECS)), "unknown quantity is an input error, not a violation")
    return {"violation": r.violations[0]}


def check_function_arguments_dimensionless():
    bad = check_dimension(Func("exp", Q("T")), SPECS)
    require(bad.status == "inconsistent" and "must be dimensionless" in bad.violations[0], "exp(T) must be rejected")
    specs = dict(SPECS, k=QuantitySpec("k", Dimension.of(T=-1)))
    good = check_dimension(Func("exp", Mul(Q("k"), Q("T"))), specs)
    require(good.status == "consistent" and good.dimension.is_dimensionless, "exp(k*T) is dimensionless")
    logbad = check_dimension(Func("log", Q("l")), SPECS)
    require(logbad.status == "inconsistent", "log(l) must be rejected")
    require(raises(lambda: check_dimension(Func("sqrt", Q("l")), SPECS)), "unsupported function is an input error")
    return {"exp_T": bad.violations[0]}


def check_rational_exponents():
    period = Pow(Div(Q("l"), Q("g")), F(1, 2))
    r = check_dimension(period, SPECS)
    require(r.dimension == TIME, f"sqrt(l/g) must have dimension T, got {r.dimension}")
    half = check_dimension(Pow(Q("l"), F(1, 2)), SPECS)
    require(half.dimension.exponents[1] == F(1, 2), "L^(1/2) must be kept exactly")
    require(raises(lambda: Dimension.of(L=0.5)), "float exponents are rejected (exactness)")
    require(raises(lambda: rescale_for_base_unit_change(F(1), Dimension.of(L=F(1, 2)), {"L": 1000})), "non-integer exponent rescaling is refused")
    return {"sqrt_l_over_g": str(r.dimension)}


def check_singular_empty_and_full_rank_matrices():
    require(raises(lambda: buckingham_pi_basis([])), "empty quantity list is an input error")
    require(raises(lambda: buckingham_pi_basis([QuantitySpec("a", LEN), QuantitySpec("a", TIME)])), "duplicate names are an input error")
    dimless = buckingham_pi_basis([QuantitySpec("eta", Dimension.none()), QuantitySpec("phi", Dimension.none())])
    require(dimless.rank == 0 and dimless.nullity == 2 and same_pi_span(dimless.basis, [(1, 0), (0, 1)]), "each dimensionless quantity is its own group")
    full = buckingham_pi_basis([QuantitySpec("m", MASS), QuantitySpec("x", LEN), QuantitySpec("t", TIME)])
    require(full.rank == 3 and full.nullity == 0 and full.basis == (), "full column rank: no Pi group (valid result)")
    # dependent columns: l and 2l-type duplicate dimension
    dup = buckingham_pi_basis([QuantitySpec("x1", LEN), QuantitySpec("x2", LEN)])
    require(dup.nullity == 1 and same_pi_span(dup.basis, [(1, -1)]), "x1/x2 is the single group")
    require(exact_null_space([[0, 0]], 2) == [[1, 0], [0, 1]], "zero matrix: whole space")
    return {"dimless": dimless.to_dict(), "full_rank_nullity": full.nullity}


def check_basis_change_compares_spans():
    galaxy = [QuantitySpec("V", Dimension.of(L=1, T=-1)), QuantitySpec("r", LEN), QuantitySpec("G", G_NEWTON),
              QuantitySpec("M", MASS), QuantitySpec("a0", ACC)]
    rep = buckingham_pi_basis(galaxy)
    require(rep.rank == 3 and rep.nullity == 2, f"galaxy set: rank 3, nullity 2, got {rep.rank}/{rep.nullity}")
    physical = [(2, 1, -1, -1, 0), (-2, 1, 0, 0, 1)]  # V^2 r/(G M), a0 r / V^2
    require(same_pi_span(rep.basis, physical), f"computed basis must span V^2 r/(GM) and a0 r/V^2, got {rep.monomials}")
    combo = [(0, 2, -1, -1, 1)]  # product of the two: a0 r^2/(G M) -- in span, but alone not a basis
    require(not same_pi_span(rep.basis, combo), "a single vector cannot span a 2-dim group space")
    require(same_pi_span(rep.basis, [physical[0], combo[0]]), "an alternative basis with the same span is equally valid")
    require(not same_pi_span(rep.basis, [physical[0], (1, 0, 0, 0, 0)]), "a dimensional vector is not in the span")
    for v in physical:
        expr = None
        for name, e in zip(["V", "r", "G", "M", "a0"], v):
            if e:
                term = Pow(Q(name), e)
                expr = term if expr is None else Mul(expr, term)
        r = check_dimension(expr, {s.name: s for s in galaxy})
        require(r.dimension.is_dimensionless, f"{v} must be dimensionless")
    return {"galaxy_basis": [list(b) for b in rep.basis], "monomials": list(rep.monomials)}


def check_unit_transformations_and_affine_scales():
    m = Unit("m", LEN, F(1))
    km = Unit("km", LEN, F(1000))
    require(convert(F(3, 2), km, m) == 1500 and convert(1500, m, km) == F(3, 2), "km <-> m exact")
    kelvin = Unit("K", Dimension.of(Theta=1), F(1))
    celsius = Unit("degC", Dimension.of(Theta=1), F(1), offset=F(27315, 100))
    require(convert(F(25), celsius, kelvin) == F(29815, 100), "25 degC = 298.15 K (absolute)")
    require(convert(F(25), celsius, kelvin, difference=True) == 25, "a 25 degC DIFFERENCE is 25 K")
    require(raises(lambda: multiplicative_scale(celsius)), "affine unit has no multiplicative scale")
    require(multiplicative_scale(kelvin) == 1, "kelvin is multiplicative")
    require(raises(lambda: convert(1, m, kelvin)), "cross-dimension conversion is an input error")
    require(raises(lambda: Unit("bad", LEN, F(0))), "unit scale must be > 0")
    return {"25degC_in_K": "298.15", "difference": 25}


def check_energy_vs_torque_semantic_warning():
    energy_dim = Dimension.of(M=1, L=2, T=-2)
    specs = {"E": QuantitySpec("E", energy_dim, kind="energy"), "tau": QuantitySpec("tau", energy_dim, kind="torque"),
             "W": QuantitySpec("W", energy_dim, kind="energy")}
    mixed = check_dimension(Add(Q("E"), Q("tau")), specs)
    require(mixed.status == "consistent" and len(mixed.semantic_warnings) == 1 and "different kinds" in mixed.semantic_warnings[0],
            "energy + torque: dimensionally consistent but a semantic warning")
    same = check_dimension(Add(Q("E"), Q("W")), specs)
    require(same.status == "consistent" and not same.semantic_warnings, "energy + energy: no warning")
    return {"warning": mixed.semantic_warnings[0]}


def check_abstract_dimensionless_scf_quantity():
    eta = QuantitySpec("eta_info", Dimension.none(), note="abstract SCF information ratio; no SI unit")
    r = check_dimension(Mul(Q("eta_info"), Const(F(3))), {"eta_info": eta})
    require(r.dimension.is_dimensionless, "abstract dimensionless quantity stays dimensionless")
    require(rescale_for_base_unit_change(F(7, 3), eta.dimension, {"T": 365, "L": 1000}) == F(7, 3), "invariant under any base-unit change")
    return {"eta": "dimensionless"}


CHECKS = [
    check_jc03_pendulum_null_space,
    check_jc04_reservoir_unit_change_exact_and_module,
    check_jc04_halo_product_invariance,
    check_addition_of_different_dimensions_rejected,
    check_function_arguments_dimensionless,
    check_rational_exponents,
    check_singular_empty_and_full_rank_matrices,
    check_basis_change_compares_spans,
    check_unit_transformations_and_affine_scales,
    check_energy_vs_torque_semantic_warning,
    check_abstract_dimensionless_scf_quantity,
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
    out_path = Path(__file__).with_name("verify_dimensional_analysis_results.json")
    out_path.write_text(json.dumps({"n_passed": n_passed, "n_total": len(CHECKS), "results": results}, indent=2, default=str))
    print(f"Report written to {out_path}")
    return 0 if n_passed == len(CHECKS) else 1


if __name__ == "__main__":
    raise SystemExit(main())
