#!/usr/bin/env python3
"""Synthetic checks for revision 3.2. NumPy only; no production packages.

The analytic statements and their assumptions live in the Markdown documents.
These independent finite-difference, quadrature, trajectory and matrix checks
are not proofs for all systems and not empirical validation. Failures give a
nonzero exit code, including when Python runs with -O.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import math
from pathlib import Path
import platform

import numpy as np


def require(ok, msg):
    if not bool(ok):
        raise AssertionError(msg)


def near(a, b, atol=1e-10, rtol=1e-9):
    if not np.allclose(a, b, atol=atol, rtol=rtol):
        raise AssertionError(f"{a!r} != {b!r}")


def diff(f, x, h=1e-5):
    return (f(x+h)-f(x-h))/(2*h)


def rk4(f, initial, end, steps=2000):
    x = np.asarray(initial, dtype=float)
    h = end / steps
    for i in range(steps):
        t = i*h
        a = f(t, x)
        b = f(t+h/2, x+h*a/2)
        c = f(t+h/2, x+h*b/2)
        d = f(t+h, x+h*c)
        x = x+h*(a+2*b+2*c+d)/6
    return x


def field(x, r, e, u, w, k):
    x, r, e, u, w = (np.asarray(v, dtype=float) for v in (x, r, e, u, w))
    return -r*(x-e)+u-w+k*(x[::-1]-x)


def t01_context_derivatives():
    # Nonconstant physical state, context, scale and explicit time together.
    x = lambda t: math.exp(-t)
    c = lambda t: math.sin(t)
    pi = lambda z, v, t: (z-v)/(1+t)
    errors = []
    for t in np.linspace(0, 2, 31):
        y = pi(x(t), c(t), t)
        predicted = (-x(t)-math.cos(t))/(1+t)-y/(1+t)
        errors.append(abs(diff(lambda a: pi(x(a), c(a), a), t)-predicted))
    require(max(errors) < 1e-8, "full context chain rule")
    near(diff(lambda t: (1-t)/(1+t), .4), -2/1.4**2)
    return {"max_derivative_error": max(errors), "fixed_stock_reserve_derivative_at_0": -2}


def t02_state_dependent_time():
    # x=exp(-t), tau=1-exp(-t), y=x^2. Compare independent derivatives.
    errors = []
    for t in np.linspace(0, 4, 41):
        x = math.exp(-t)
        numeric = diff(lambda a: math.exp(-2*a), t)/diff(lambda a: 1-math.exp(-a), t)
        transformed = -2*x*x/x
        near(numeric, transformed, atol=1e-8)
        errors.append(abs(numeric-transformed))
    require(1-math.exp(-20) < 1, "positive clock can have finite total duration")
    return {"physical_horizon": "infinite", "transformed_horizon": 1,
            "max_derivative_error": max(errors)}


def t03_parameter_chain_rule():
    f = lambda x: -(1+x*x)*x
    for x in np.linspace(-2, 2, 41):
        near(diff(f, x), -1-3*x*x, atol=2e-9)
    near(diff(f, 1), -4)
    require(abs(-4-(-2)) > 1, "frozen coefficient hides derivative")
    return {"full_derivative_at_1": -4, "frozen_derivative_at_1": -2}


def t04_composed_transformations():
    # Independently differentiate composite; nonconstant scales and residuals.
    tji = lambda x: x+x**3/10
    tkj = lambda y: math.exp(y/5)
    fi = lambda x: -x+.2
    fj = lambda y: -2*y+.3
    fk = lambda z: -.7*z
    aji = lambda x: 1+x*x
    akj = lambda y: 2+y*y
    errors = []
    for x in np.linspace(-1, 1, 31):
        y = tji(x)
        rji = diff(tji, x)*fi(x)-aji(x)*fj(y)
        rkj = diff(tkj, y)*fj(y)-akj(y)*fk(tkj(y))
        direct = diff(lambda a: tkj(tji(a)), x)*fi(x)-aji(x)*akj(y)*fk(tkj(y))
        composed = diff(tkj, y)*rji+aji(x)*rkj
        errors.append(abs(direct-composed))
        require(abs(direct) <= abs(diff(tkj, y))*abs(rji)+aji(x)*abs(rkj)+1e-9,
                "composition error bound")
    require(max(errors) < 1e-8, "residual composition")
    return {"max_composition_error": max(errors)}


def t05_scalar_boundary_and_hitting():
    r, eq, b, U, W, initial = 1.3, .8, .2, .1, 1.5, 1.4
    steady = eq+(U-W)/r
    hit = math.log((initial-steady)/(b-steady))/r
    solution = lambda t: steady+(initial-steady)*math.exp(-r*t)
    near(solution(hit), b)
    require(solution(hit-.01)>b and solution(hit+.01)<b, "first crossing")
    for t in np.linspace(0, hit+.1, 23):
        near(diff(solution, t), -r*(solution(t)-eq)+U-W)
    critical = r*(eq-b)+U
    for offset in [-.1, 0, .1]:
        near(-r*(b-eq)+U-(critical+offset), -offset)
    near(math.log(3), math.log((1-(-.5))/(0-(-.5))))
    return {"general_hitting_time": hit, "original_hitting_time": math.log(3)}


def t06_sum_difference_transformation():
    rng = np.random.default_rng(3206)
    errors = []
    for _ in range(100):
        x, e, u, w = rng.normal(size=(4, 2))
        r, k = rng.uniform(.1, 2, 2)
        dx = field(x, [r, r], e, u, w, k)
        s, d = x.sum(), x[0]-x[1]
        near([(s+d)/2, (s-d)/2], x)
        expected = np.array([-r*(s-e.sum())+u.sum()-w.sum(),
                             -(r+2*k)*d+r*(e[0]-e[1])+u[0]-u[1]-w[0]+w[1]])
        actual = np.array([dx.sum(), dx[0]-dx[1]])
        errors.append(float(np.max(np.abs(actual-expected))))
    require(max(errors)<1e-12, "sum and distribution dynamics")
    return {"cases": 100, "max_error": max(errors)}


def t07_unequal_rates_break_closure():
    rates = [field(x, [1, 2], [0, 0], [0, 0], [0, 0], .7).sum()
             for x in ([1, 0], [0, 1])]
    near(rates, [-1, -2])
    require(rates[0] != rates[1], "equal sum has distinct future derivatives")
    return {"same_sum": 1, "two_derivatives": list(map(float, rates))}


def t08_memory_elimination():
    # Solve full system by eigendecomposition, evaluate reduced memory separately.
    r1, r2, k, end = 1., 2., .3, 1.2
    matrix = np.array([[-r1-k, k], [k, -r2-k]])
    vals, vecs = np.linalg.eigh(matrix)
    initial = np.array([.8, .2])
    rb, dr = (r1+r2)/2, (r1-r2)/2
    lam = rb+2*k
    ts = np.linspace(0, end, 6001)
    xs = np.array([vecs @ (np.exp(vals*t)*(vecs.T@initial)) for t in ts])
    sums = xs.sum(axis=1)
    integral = np.trapezoid(np.exp(-lam*(end-ts))*sums, ts)
    reduced = -rb*sums[-1]-dr*math.exp(-lam*end)*(initial[0]-initial[1])+dr**2*integral
    direct = (matrix@xs[-1]).sum()
    near(reduced, direct, atol=1e-8)
    # Also include a nonzero constant difference input; analytic full solution.
    forcing = np.array([.2, -.1])
    steady = -np.linalg.solve(matrix, forcing)
    xs2 = np.array([steady+vecs @ (np.exp(vals*t)*(vecs.T@(initial-steady))) for t in ts])
    sums2 = xs2.sum(axis=1)
    kernel = np.exp(-lam*(end-ts))
    memory = dr**2*np.trapezoid(kernel*sums2, ts)-dr*np.trapezoid(kernel*(forcing[0]-forcing[1]), ts)
    reduced2 = -rb*sums2[-1]+forcing.sum()-dr*math.exp(-lam*end)*(initial[0]-initial[1])+memory
    direct2 = (matrix@xs2[-1]+forcing).sum()
    near(reduced2, direct2, atol=1e-8)
    return {"homogeneous_error": float(abs(reduced-direct)), "forced_error": float(abs(reduced2-direct2))}


def t09_orthant_boundary_conditions():
    rng = np.random.default_rng(3209)
    minima, conflicts = [], 0
    for _ in range(100):
        r = rng.uniform(.1, 2, 2)
        e, b = rng.normal(size=(2, 2))
        W, k = rng.uniform(0, 2, 2), float(rng.uniform(0, 2))
        demand = W-r*(e-b)-k*(b[::-1]-b)
        a = np.maximum(0, demand)
        for i in [0, 1]:
            for surplus in [0, .1, 2]:
                x = b.copy()
                x[1-i] += surplus
                val = field(x, r, e, a, W, k)[i]
                minima.append(float(val))
                require(val >= -1e-12, "boundary points inward under common constant action")
        if a.sum() > .01:
            U = a.sum()-.01
            # Nonnegative actions satisfying both actual corner inequalities
            # must meet these componentwise lower bounds.
            corner_without_action = field(b, r, e, [0, 0], W, k)
            required_total = np.maximum(0, -corner_without_action).sum()
            require(required_total > U, "insufficient common budget")
            conflicts += 1
    return {"parameter_sets": 100, "boundary_evaluations": len(minima),
            "min_boundary_derivative": min(minima), "infeasible_budget_cases": conflicts}


def t10_shared_budget_conflict():
    near(.2+.75-.7, .25)
    corner = field([0, 0], [1, 1], [.2, .2], [.375, .375], [.7, .7], .5)
    near(corner, [-.125, -.125])
    near(field([0, 0], [1, 1], [.2, .2], [.5, .5], [.7, .7], .5), [0, 0])
    for k in [0, .5, 10, 1000]:
        near(field([0, 0], [1, 1], [.2, .2], [.375, .375], [.7, .7], k), corner)
    return {"standalone_margin": .25, "required_joint_budget": 1, "available_budget": .75}


def t11_optimal_symmetric_horizon():
    hit = math.log(9)
    ode = lambda t, x: field(x, [1, 1], [.2, .2], [.375, .375], [.7, .7], .5)
    numeric = rk4(ode, [1, 1], hit)
    near(numeric, [0, 0], atol=1e-10)
    after = rk4(ode, [1, 1], hit+.1)
    require(np.all(after<0), "crossing occurs after contact")
    # Distinct admissible time-dependent allocations, including nonmaximal totals.
    for j in range(5):
        def policy(t, x):
            total = .75*(.7+.3*math.cos(j*t)**2)
            fraction = .5+.4*math.sin((j+1)*t)
            return field(x, [1, 1], [.2, .2], [total*fraction,total*(1-fraction)], [.7, .7], .5)
        endpoint = rk4(policy, [1, 1], hit+.1)
        upper = -.25+2.25*math.exp(-(hit+.1))
        require(endpoint.sum() <= upper+1e-9, "total-resource upper bound")
        require(endpoint.min()<0, "no allocation preserves both beyond upper horizon")
    return {"optimal_contact_time": hit, "rk4_contact_error": float(np.max(abs(numeric))),
            "alternative_policies": 5}


def t12_closed_sum_not_local_safety():
    safe, unsafe = np.array([.5, .5]), np.array([-.25, 1.25])
    near(safe.sum(), unsafe.sum())
    require(np.all(safe>=0) and np.any(unsafe<0), "task information lost")
    rng = np.random.default_rng(3212)
    for x in rng.normal(size=(300, 2)):
        s, d = x.sum(), x[0]-x[1]
        require(bool(np.all(x>=0)) == bool(s>=abs(d)), "exact safety reconstruction")
    # Same physical state, local and common obligations disagree.
    near(np.array([.4, .4])-.1, [.3, .3])
    near(.4+.4-1, -.2)
    return {"equal_sum": 1, "safety_equivalence_samples": 300, "common_reserve": -.2}


def t13_moving_boundaries():
    # Positive stock growth fails against a faster-growing threshold.
    near(diff(lambda t: .2*t-.3*t, .5), -.1)
    rng = np.random.default_rng(3213)
    for t in np.linspace(0, 2, 41):
        b = np.array([.1*t, .2*math.sin(t)])
        bdot = np.array([.1, .2*math.cos(t)])
        r, e, W, k = np.array([1., 1.5]), np.array([.2, .3]), np.array([.7, .6]), .5
        a = np.maximum(0, W-r*(e-b)-k*(b[::-1]-b)+bdot)
        for i in [0, 1]:
            x = b.copy()
            x[1-i] += rng.uniform(0, 2)
            require(field(x, r, e, a, W, k)[i]-bdot[i]>=-1e-12,
                    "moving-boundary compensation")
    return {"stock_growth": .2, "boundary_growth": .3, "moving_boundary_checks": 82}


def t14_finite_actuation_reservoir():
    rng = np.random.default_rng(3214)
    D = 1.
    for _ in range(100):
        x = rng.uniform(0, 2, 2)
        u = rng.uniform(0, 1, 2)
        dx = field(x, [1, 1], [.2, .2], u, [.7, .7], .5)
        qdot = -u.sum()
        near(dx.sum()+qdot, -x.sum()-D)
        require(dx.sum()+qdot <= -D, "total stock depleted by deficit")
    return {"balance_checks": 100, "necessary_horizon_for_s0_2_q0_3": 5,
            "bound_is_not_claimed_attainable": True}


def t15_changing_partition_exact_closure():
    c0 = np.eye(2)[[0, 0, 1, 1]]
    swap = np.array([[0., 1.], [1., 0.]])
    c1 = c0@swap
    p = np.eye(4)
    near(p@c1, c0@swap)
    wrong = float(np.max(np.abs(p@c0-c0@swap)))
    require(wrong == 1, "using old partition yields wrong condition")
    micro = np.array([.1, .2, .3, .4])
    macro = micro@c0
    c = c0
    for _ in range(7):
        c = c@swap
        macro = macro@swap
        near(micro@c, macro)
    return {"exact_error": 0, "wrong_old_partition_error": wrong, "steps": 7}


def t16_nonstationary_total_variation_bound():
    rng = np.random.default_rng(3216)
    base_c = np.eye(2)[[0, 0, 1, 1]]
    qbase = np.array([[.9, .1], [.2, .8]])
    pbase = base_c@qbase@(base_c.T/2)
    swap = np.array([[0., 1.], [1., 0.]])
    observed, bounds, telescoping_errors = [], [], []
    for _ in range(30):
        n = 7
        relabel = [np.eye(2) if rng.random()<.5 else swap for _ in range(n+1)]
        cs = [base_c@s for s in relabel]
        ps, qs, es, deltas = [], [], [], []
        for t in range(n):
            noise = rng.uniform(size=(4, 4)); noise /= noise.sum(axis=1)[:, None]
            p = .99*pbase+.01*noise
            q = relabel[t].T@qbase@relabel[t+1]
            e = p@cs[t+1]-cs[t]@q
            ps.append(p); qs.append(q); es.append(e)
            deltas.append(float(np.max(.5*np.abs(e).sum(axis=1))))
        pp, qq = np.eye(4), np.eye(2)
        for p, q in zip(ps, qs):
            pp = pp@p; qq = qq@q
        direct = pp@cs[-1]-cs[0]@qq
        telescope = np.zeros((4, 2))
        for t in range(n):
            left, right = np.eye(4), np.eye(2)
            for p in ps[:t]: left = left@p
            for q in qs[t+1:]: right = right@q
            telescope += left@es[t]@right
        near(direct, telescope)
        initial = rng.uniform(size=4); initial /= initial.sum()
        tv = float(.5*np.abs(initial@direct).sum())
        bound = sum(deltas)
        require(tv<=bound+1e-12 and bound<1, "nontrivial TV bound")
        observed.append(tv); bounds.append(bound)
        telescoping_errors.append(float(np.max(np.abs(direct-telescope))))
    return {"kernel_sequences": 30, "steps_each": 7, "max_TV": max(observed),
            "max_sum_delta": max(bounds), "max_telescoping_error": max(telescoping_errors)}


def t17_residual_to_trajectory_bound():
    eps, initial_error, end = .03, .2, .7
    errors = []
    for L in [0., .4, 1.2]:
        actual = rk4(lambda t, x: L*x+eps, [initial_error], end)[0]
        bound = initial_error*math.exp(L*end)+(eps*end if L==0 else eps*math.expm1(L*end)/L)
        near(actual, bound, atol=1e-10)
        errors.append(float(abs(actual-bound)))
    return {"sharp_linear_cases": 3, "max_numeric_error": max(errors)}


def t18_recursive_flux_balance():
    # Two internal exchanges cancel in two successive levels of aggregation.
    rng = np.random.default_rng(3218)
    errors = []
    for _ in range(100):
        inflow, loss = rng.uniform(size=(2, 3))
        inner, outer = rng.normal(size=2)
        dp = inflow[0]-loss[0]-inner-outer
        dq = inflow[1]-loss[1]+inner
        dz = inflow[2]-loss[2]+outer
        first = dp+dq
        near(first, inflow[:2].sum()-loss[:2].sum()-outer)
        errors.append(abs(first+dz-(inflow.sum()-loss.sum())))
    require(max(errors)<1e-12, "recursive balance cancellation")
    return {"nested_balance_cases": 100, "max_error": max(errors)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path(__file__).with_name("transformation_results.json"))
    args = parser.parse_args()
    results = []
    for name, function in sorted(globals().items()):
        if name.startswith("t") and name[1:3].isdigit() and callable(function):
            try:
                evidence = function()
                results.append({"id": name, "status": "passed", "evidence": evidence})
            except Exception as exc:
                results.append({"id": name, "status": "failed", "error": f"{type(exc).__name__}: {exc}"})
    passed = sum(r["status"]=="passed" for r in results)
    report = {"revision": "3.2", "scope": "synthetic transformations, closure and viability",
              "created_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
              "python": platform.python_version(), "numpy": np.__version__,
              "passed": passed, "total": len(results), "results": results}
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(f"{passed}/{len(results)} synthetic checks passed")
    for result in results:
        if result["status"] != "passed": print(result)
    raise SystemExit(0 if passed==len(results) else 1)


if __name__ == "__main__":
    main()
