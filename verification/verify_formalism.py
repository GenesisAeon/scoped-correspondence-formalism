#!/usr/bin/env python3
"""Reproduce bounded mathematical checks for Formalism revision 2.

Uses only the standard library. This is not an empirical validation or a run
of the GenesisAeon package test suites. Output: verification_results.json.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import math
from pathlib import Path
import platform
import re
import sys


RESULTS: list[dict] = []


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def close(a: float, b: float, tol: float = 1e-9) -> None:
    require(math.isclose(a, b, rel_tol=tol, abs_tol=tol), f"{a} != {b}")


def run_check(name: str, kind: str, function) -> None:
    try:
        evidence = function()
        RESULTS.append(dict(name=name, kind=kind, status="passed", evidence=evidence))
    except Exception as exc:
        RESULTS.append(dict(name=name, kind=kind, status="failed", error=str(exc)))


def cusp(x: float, a: float, b: float, tau: float = 1.0) -> float:
    if tau <= 0:
        raise ValueError("tau must be positive")
    return (-x**3 + a*x + b)/tau


def derivative(function, x: float, h: float = 1e-5) -> float:
    return (function(x+h)-function(x-h))/(2*h)


def cbrt(x: float) -> float:
    return math.copysign(abs(x)**(1/3), x)


def real_cubic_roots(a: float, b: float) -> list[float]:
    """Distinct real roots of x^3-a*x-b, using Cardano/trigonometric forms."""
    discriminant = 4*a**3-27*b**2
    if discriminant > 1e-12:
        angle = math.acos(max(-1.0, min(1.0, b/(2*(a/3)**1.5))))
        return sorted(2*math.sqrt(a/3)*math.cos((angle+2*k*math.pi)/3)
                      for k in range(3))
    if discriminant < -1e-12:
        q = math.sqrt(b*b/4-a**3/27)
        return [cbrt(b/2+q)+cbrt(b/2-q)]
    if abs(a)+abs(b) < 1e-12:
        return [0.0]
    r = cbrt(b/2)
    return sorted([-r, 2*r])


def quadratic(matrix: list[list[float]], x: list[float]) -> float:
    return sum(x[i]*matrix[i][j]*x[j] for i in range(2) for j in range(2))


def entropy_binary(p: float) -> float:
    if not 0 <= p <= 1:
        raise ValueError("p outside [0,1]")
    return -sum(v*math.log2(v) for v in (p, 1-p) if v)


def frame_score(width: float, reference: float, rho: float, alpha: float = 1) -> float:
    if width < 0 or reference <= 0 or alpha <= 0 or not 0 <= rho < 1:
        raise ValueError("outside the declared frame-hypothesis domain")
    buffer = width/reference
    pressure = alpha*rho/(1-rho)
    if buffer+pressure == 0:
        raise ValueError("undefined 0/0")
    return buffer/(buffer+pressure)


def c01_sigmoid_independence():
    p = lambda u: 1/(1+math.exp(-4*u))
    slope = derivative(p, 0)
    close(slope, 1)
    rates = [-derivative(lambda x: -(x-p(0))/tau, p(0)) for tau in (1, 10)]
    close(rates[0], 1)
    close(rates[1], .1)
    require(rates[0] != rates[1], "same sigmoid did not permit distinct rates")
    return dict(beta=4, midpoint_slope=slope, recovery_rates=rates)


def c02_coordinate_mismatch():
    a, theta, b = 2., 1., 0.
    old = lambda r: -r**3+a*(r-theta)+b
    new = lambda r: cusp(r-theta, a, b)
    rates = [-derivative(old, theta), -derivative(new, theta)]
    close(old(theta), -1)
    close(new(theta), 0)
    close(rates[0], 1)
    close(rates[1], -2)
    return dict(old_drift=old(theta), centered_drift=new(theta), negative_derivatives=rates)


def c03_positive_a_insufficient():
    roots = real_cubic_roots(1, 1)
    require(len(roots) == 1, "a=1,b=1 should have one real root")
    close(cusp(roots[0], 1, 1), 0)
    return dict(a=1, b=1, discriminant=-23, real_roots=roots)


def c04_probability_not_distance():
    # Independent geometric quadrature of the positive half of [-3,3].
    points = [-3+6*(i+.5)/1000 for i in range(1000)]
    probability = sum(x > 0 for x in points)/len(points)
    close(probability, .5)
    distances = [math.sqrt(a) for a in (1, 4)]
    require(distances[0] != distances[1], "distance should change")
    return dict(a=[1, 4], saddle_distances=distances, basin_probabilities=[probability]*2,
                assumption="positive half-line is the basin for the symmetric cubic, a>0")


def c05_directed_matrix_not_thermodynamics():
    value = quadratic([[0, 1], [0, 0]], [1, -1])
    close(value, -1)
    return dict(matrix=[[0, 1], [0, 0]], force=[1, -1], quadratic_form=value)


def c06_information_window():
    values = [100*t/1000 for t in (1, 10)]
    rates = [100*t/(1000*t) for t in (1, 10)]
    require(values[0] != values[1], "raw I/C should depend on window")
    close(rates[0], rates[1])
    return dict(raw_seconds=values, dimensionless_fractions=rates)


def c07_raw_frame_units():
    metres, centimetres = 1/(1+1), 100/(100+1)
    require(not math.isclose(metres, centimetres), "raw ratio should expose unit error")
    return dict(metres=metres, centimetres=centimetres)


def c08_s8_not_probability():
    s8 = 1.2*math.sqrt(.3/.3)
    require(s8 > 1, "S8 counterexample missing")
    return dict(sigma8=1.2, omega_m=.3, S8=s8)


def p01_cusp_branches_and_time():
    records = []
    for a in (.25, 1., 4.):
        for tau in (.5, 1., 10.):
            for x in (-math.sqrt(a), 0., math.sqrt(a)):
                close(cusp(x, a, 0, tau), 0)
                observed = -derivative(lambda y: cusp(y, a, 0, tau), x)
                expected = -a/tau if x == 0 else 2*a/tau
                close(observed, expected, 2e-8)
                if x == 0:
                    close(-tau*observed, a, 2e-8)
                records.append(dict(a=a, tau=tau, x=x, recovery=observed))
    return dict(equilibria_checked=len(records), examples=records[3:6])


def p02_cusp_region():
    records = []
    for a, b, count in ((1., 0., 3), (1., .2, 3), (1., 1., 1), (-1., .3, 1), (0., 0., 1), (3., 2., 2)):
        roots = real_cubic_roots(a, b)
        require(len(roots) == count, "unexpected root count")
        for x in roots:
            close(cusp(x, a, b), 0)
        records.append(dict(a=a, b=b, discriminant=4*a**3-27*b**2, roots=roots))
    return records


def p03_information_channel():
    # Uniform binary source, BSC(q), independent receiver BSC(r).
    q, r, nu = .1, .2, 100.
    q_total = q+r-2*q*r
    capacity = nu*(1-entropy_binary(q))
    info_rate = nu*(1-entropy_binary(q_total))
    eta = info_rate/capacity
    require(0 <= eta <= 1, "data processing or normalization failed")
    close((info_rate*10)/(capacity*10), eta)
    require(capacity > info_rate > 0, "nontrivial degradation expected")
    return dict(channel="memoryless binary symmetric", capacity_bits_per_second=capacity,
                receiver_information_rate=info_rate, eta_info=eta)


def p04_frame_normalization_and_domain():
    si = frame_score(1, 2, .5)
    cm = frame_score(100, 200, .5)
    close(si, cm)
    rejected = 0
    for args in ((0, 1, 0), (1, 0, .5), (1, 1, 1), (1, 1, 1.1), (-1, 1, .5)):
        try:
            frame_score(*args)
        except ValueError:
            rejected += 1
    require(rejected == 5, "invalid frame arguments not rejected")
    return dict(invariant_score=si, invalid_cases_rejected=rejected,
                status="dimensionally consistent hypothesis, not calibrated")


def p05_symmetric_and_antisymmetric():
    matrix = [[2, 4], [-4, 3]]
    minimum = math.inf
    for x in range(-3, 4):
        for y in range(-3, 4):
            production = quadratic(matrix, [x, y])
            close(production, 2*x*x+3*y*y)
            require(production >= 0, "negative production")
            minimum = min(minimum, production)
    return dict(matrix=matrix, symmetric_part=[[2, 0], [0, 3]], minimum=minimum,
                interpretation="abstract conjugately normalized coordinates")


def p06_heat_balance_and_relaxation():
    ca, cb, g, ta0, tb0 = 2., 5., 3., 310., 290.
    energy0 = ca*ta0+cb*tb0
    equilibrium = energy0/(ca+cb)
    rate = g*(1/ca+1/cb)
    def temperatures(t):
        delta = (ta0-tb0)*math.exp(-rate*t)
        return equilibrium+cb/(ca+cb)*delta, equilibrium-ca/(ca+cb)*delta
    records = []
    for t in (0, .1, 1, 10):
        ta, tb = temperatures(t)
        j = g*(ta-tb)
        force = 1/tb-1/ta
        l = g*ta*tb
        production = j*force
        close(ca*ta+cb*tb, energy0)
        close(l*force, j)
        close(production, g*(ta-tb)**2/(ta*tb))
        require(production >= -1e-14, "negative heat entropy production")
        close(derivative(lambda s: temperatures(s)[0], t), -j/ca, 2e-6)
        close(derivative(lambda s: temperatures(s)[1], t), j/cb, 2e-6)
        records.append(dict(t=t, TA=ta, TB=tb, J=j, X=force, L=l, entropy_production=production))
    require(g/ca != g/cb, "asymmetric drift example missing")
    close((-g/ca)*(-g/cb)-(g/ca)*(g/cb), 0)
    close(g/ca+g/cb, rate)
    return dict(equilibrium_K=equilibrium, transverse_rate_per_second=rate,
                neutral_mode="conserved total energy", trajectory=records)


def p07_self_similarity_of_relaxation():
    # Explicit state and time normalization, not an empirical universality test.
    errors = []
    for rate, amplitude in ((.15, 2), (2.1, 20), (.065, .8)):
        for s in (0, .5, 1, 2):
            t = s/rate
            normalized = amplitude*math.exp(-rate*t)/amplitude
            error = abs(normalized-math.exp(-s))
            errors.append(error)
            close(normalized, math.exp(-s))
    return dict(max_error=max(errors), normalized_equation="dq/ds=-q",
                scope="specified continuous linear models")


def p08_discrete_rate_and_sampling():
    r, target = .15, 1.
    records = []
    for step in (.5, 1., 2.):
        values = [.4]
        for _ in range(10):
            values.append(values[-1]+r*(target-values[-1])*step)
        errors = [target-x for x in values[:-1]]
        changes = [b-a for a, b in zip(values[:-1], values[1:])]
        legacy = sum(e*d for e, d in zip(errors, changes))/sum(e*e for e in errors)
        regressors = [e*step for e in errors]
        corrected = sum(x*d for x, d in zip(regressors, changes))/sum(x*x for x in regressors)
        close(legacy, r*step)
        close(corrected, r)
        discrete_rate = -math.log(abs(1-r*step))/step
        records.append(dict(dt_hours=step, old_per_step_estimate=legacy,
                            proposed_per_hour_estimate=corrected, discrete_rate=discrete_rate))
    close(records[1]['discrete_rate'], .16251892949777494)
    return dict(results=records, scope="unclipped noise-free Euler model; package patch remains open")


def p09_amoc_frozen_control():
    r, k, sigma, gamma = .08, 18., 2.2, .4
    hstar = k*(1-math.tanh(sigma*gamma))
    field = lambda h: r*h*(hstar/k-h/k)
    close(field(hstar), 0)
    measured_rate = -derivative(field, hstar)
    close(measured_rate, r*hstar/k)
    require(measured_rate > 0 and measured_rate < r, "expected conditional rate")
    return dict(hstar=hstar, recovery_rate=measured_rate,
                scope="fixed Gamma in the documented corrected AMOC equation")


def p10_solar_quiet_submodel():
    r, lam = .06, .005
    equilibrium = r/(r+lam)
    field = lambda h: r*(1-h)-lam*h
    close(field(equilibrium), 0)
    close(-derivative(field, equilibrium), .065)
    require(abs(field(.1)) > .05, "reset value should not be fixed point")
    return dict(quiet_equilibrium=equilibrium, quiet_rate=.065,
                scope="constant quiet lambda; not full reset/stochastic process")


def p11_document_links(output_path: Path):
    root = Path(__file__).resolve().parents[1]
    broken = []
    count = 0
    generated_links = 0
    for p in root.glob('*.md'):
        for target in re.findall(r'\]\(([^)]+)\)', p.read_text(encoding='utf-8')):
            if '://' in target or target.startswith('#'):
                continue
            target = target.split('#', 1)[0]
            count += 1
            if (p.parent/target).resolve() == output_path.resolve():
                # This report is written after all checks; it may not exist yet
                # on a clean first run. Its path is declared by the invocation.
                generated_links += 1
                continue
            if target and not (p.parent/target).exists():
                broken.append(f'{p.name}: {target}')
    require(not broken, '; '.join(broken))
    return dict(local_links_checked=count, links_to_this_generated_report=generated_links,
                broken_links=broken,
                scope="current root markdown files; external links and historical files excluded")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=Path(__file__).with_name('verification_results.json'))
    args = parser.parse_args()
    for function in (c01_sigmoid_independence, c02_coordinate_mismatch,
                     c03_positive_a_insufficient, c04_probability_not_distance,
                     c05_directed_matrix_not_thermodynamics, c06_information_window,
                     c07_raw_frame_units, c08_s8_not_probability):
        run_check(function.__name__, 'counterexample', function)
    for function in (p01_cusp_branches_and_time, p02_cusp_region, p03_information_channel,
                     p04_frame_normalization_and_domain, p05_symmetric_and_antisymmetric,
                     p06_heat_balance_and_relaxation, p07_self_similarity_of_relaxation,
                     p08_discrete_rate_and_sampling, p09_amoc_frozen_control,
                     p10_solar_quiet_submodel):
        run_check(function.__name__, 'model_or_document_check', function)
    run_check('p11_document_links', 'model_or_document_check',
              lambda: p11_document_links(args.output))
    failed = [result for result in RESULTS if result['status'] != 'passed']
    report = dict(revision='2', generated_at=dt.datetime.now(dt.timezone.utc).isoformat(),
                  python=platform.python_version(), dependencies='Python standard library only',
                  count=len(RESULTS), passed=len(RESULTS)-len(failed), failed=len(failed),
                  empirical_validation=False, production_package_tests_run=False,
                  checks=RESULTS)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(dict(count=len(RESULTS), passed=report['passed'], failed=failed,
                          report=str(args.output.resolve())), ensure_ascii=False))
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
