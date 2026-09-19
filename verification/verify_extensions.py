#!/usr/bin/env python3
"""Bounded synthetic checks for revision 3; not a test of empirical universality.

Requires NumPy. Each check records its scope and numerical evidence. No production
package is imported. Assertions use explicit exceptions and remain active under -O.
"""
from __future__ import annotations

import argparse
import datetime as dt
import itertools
import json
import math
from pathlib import Path
import platform
import re
from urllib.parse import unquote

import numpy as np


RESULTS = []
BASE = Path(__file__).resolve().parents[1]


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def near(actual, expected, atol=1e-10, rtol=1e-9):
    if not np.allclose(actual, expected, atol=atol, rtol=rtol):
        raise AssertionError(f"{actual!r} != {expected!r}")


def derivative(f, x, step=1e-5):
    return (f(x + step) - f(x - step)) / (2 * step)


def stochastic(p):
    p = np.asarray(p, dtype=float)
    require(p.ndim == 2 and np.isfinite(p).all(), "finite matrix required")
    require((p >= 0).all(), "negative transition probability")
    near(p.sum(axis=1), np.ones(len(p)))
    return p


def entropy(prob):
    prob = np.asarray(prob, dtype=float)
    return float(-sum(x * math.log2(x) for x in prob if x > 0))


def mutual_channel(p, q):
    p = stochastic(p)
    q = np.asarray(q, dtype=float)
    require(q.shape == (len(p),) and (q >= 0).all(), "invalid input distribution")
    near(q.sum(), 1)
    output = q @ p
    total = 0.0
    for i in range(len(q)):
        for j in range(p.shape[1]):
            if q[i] > 0 and p[i, j] > 0:
                total += q[i] * p[i, j] * math.log2(p[i, j] / output[j])
    return float(total)


def mi_joint(joint):
    px, py = joint.sum(axis=1), joint.sum(axis=0)
    return float(sum(joint[i, j] * math.log2(joint[i, j] / (px[i] * py[j]))
                     for i, j in np.ndindex(joint.shape) if joint[i, j] > 0))


def partitions(n):
    def extend(labels):
        if len(labels) == n:
            yield labels
        else:
            for label in range(max(labels) + 2):
                yield from extend(labels + [label])
    yield from extend([0])


def aggregation(labels):
    c = np.eye(max(labels) + 1)[labels]
    lift = c.T / c.sum(axis=0)[:, None]
    near(lift @ c, np.eye(c.shape[1]))
    return c, lift


def matrices():
    p = np.zeros((4, 4))
    p[:3, :3] = 1 / 3
    p[3, 3] = 1
    bad = np.eye(4)[[2, 3, 0, 1]]
    c, lift = aggregation([0, 0, 0, 1])
    return p, bad, c, lift


def e01_circle_reconstruction():
    alpha = .7
    phases = np.linspace(-math.pi, math.pi, 257, endpoint=False)
    observed = np.cos(phases)
    delayed = np.cos(phases - alpha)
    recovered_sine = (delayed - observed * math.cos(alpha)) / math.sin(alpha)
    near(recovered_sine, np.sin(phases))
    reconstructed = np.arctan2(recovered_sine, observed)
    angle_error = np.angle(np.exp(1j * (reconstructed - phases)))
    near(angle_error, 0)
    return dict(intrinsic_dimension=1, sufficient_coordinates_in_this_model=2,
                max_angle_error=float(np.max(np.abs(angle_error))))


def e02_sampling_alias_and_conditioning():
    theta = .7
    a = np.array([math.cos(theta - j * math.pi) for j in range(8)])
    b = np.array([math.cos(-theta - j * math.pi) for j in range(8)])
    near(a, b)
    near(math.cos(theta), math.cos(-theta))
    amplification = {str(alpha): 1 / abs(math.sin(alpha)) for alpha in (.7, .01)}
    require(amplification['0.01'] > 50 * amplification['0.7'], "conditioning countercase")
    return dict(indistinguishable_delay_vectors=a.tolist(),
                inverse_sine_factors=amplification)


def memory_solution(t, x0, y0):
    w = math.sqrt(3) / 2
    b = (.5 * x0 + y0) / w
    q = x0 * np.cos(w * t) + b * np.sin(w * t)
    qp = -x0 * w * np.sin(w * t) + b * w * np.cos(w * t)
    x = np.exp(-1.5 * t) * q
    xp = np.exp(-1.5 * t) * (qp - 1.5 * q)
    return x, xp, xp + x


def e03_projected_memory():
    residuals = []
    for x0, y0 in [(0., 1.), (0., -1.), (1.2, -.7)]:
        for t in [.1, .5, 1., 2.]:
            x, xp, y = memory_solution(t, x0, y0)
            dx_numeric = derivative(lambda s: memory_solution(s, x0, y0)[0], t)
            dy_numeric = derivative(lambda s: memory_solution(s, x0, y0)[2], t)
            near(dx_numeric, -x + y, atol=2e-9)
            near(dy_numeric, -x - 2 * y, atol=2e-9)
            grid = np.linspace(0, t, 20001)
            values = np.exp(-2 * (t - grid)) * memory_solution(grid, x0, y0)[0]
            integral = (t / (len(grid)-1)) * (values[0]/2 + values[-1]/2 + values[1:-1].sum())
            rhs = -x + math.exp(-2 * t) * y0 - integral
            near(rhs, xp, atol=2e-8)
            residuals.append(float(abs(rhs - xp)))
    near(memory_solution(0, 0, 1)[1], 1)
    near(memory_solution(0, 0, -1)[1], -1)
    return dict(max_memory_residual=max(residuals),
                same_observation_distinct_drifts=[1, -1])


def e04_exact_lumpability():
    p, _, c, lift = matrices()
    q = stochastic(lift @ p @ c)
    near(q, np.eye(2))
    near(p @ c, c @ q)
    for k in range(11):
        near(np.linalg.matrix_power(p, k) @ c, c @ np.linalg.matrix_power(q, k))
    alternate_lift = np.array([[1, 0, 0, 0], [0, 0, 0, 1]])
    near(alternate_lift @ c, np.eye(2))
    near(alternate_lift @ p @ c, q)
    return dict(macro_kernel=q.tolist(), horizons_checked=11, lift_independent=True)


def e05_nonclosed_aggregation():
    _, p, c, lift = matrices()
    q = stochastic(lift @ p @ c)
    near((p @ c)[0], [1, 0])
    near((p @ c)[1], [0, 1])
    require(not np.allclose(p @ c, c @ q), "invalid closure was accepted")
    truth = np.linalg.matrix_power(p, 2) @ c
    reduced = c @ np.linalg.matrix_power(q, 2)
    require(not np.allclose(truth, reduced), "hidden resetting undetected")
    return dict(same_macro_distinct_next_rows=(p @ c)[:2].tolist(),
                two_step_error=float(np.abs(truth-reduced).sum(axis=1).max()/2))


def e06_approximate_error_bound():
    p, bad, c, lift = matrices()
    p = stochastic(.96 * p + .04 * bad)
    q = stochastic(lift @ p @ c)
    delta = float(np.abs(p @ c - c @ q).sum(axis=1).max()/2)
    require(0 < delta < .1, "expected nontrivial small closure defect")
    errors = []
    for k in range(21):
        difference = np.linalg.matrix_power(p, k) @ c - c @ np.linalg.matrix_power(q, k)
        error = float(np.abs(difference).sum(axis=1).max()/2)
        require(error <= min(1, k * delta) + 1e-12, "TV horizon bound failed")
        errors.append(error)
    return dict(delta=delta, max_error=max(errors), horizons=21,
                all_pure_initial_states_checked=True)


def e07_effective_information_ensembles():
    p, _, c, lift = matrices()
    qmacro = np.full(2, .5)
    qmicro = np.full(4, .25)
    kernel = lift @ p @ c
    ei_micro = mutual_channel(p, qmicro)
    ei_macro = mutual_channel(kernel, qmacro)
    matched = mutual_channel(p, qmacro @ lift)
    by_entropies = entropy(qmicro @ p) - sum(qmicro[i] * entropy(p[i]) for i in range(4))
    near(ei_micro, entropy([.25, .75]))
    near(ei_micro, by_entropies)
    near(ei_macro, 1)
    near(matched, 1)
    return dict(EI_uniform_micro=ei_micro, EI_uniform_macro=ei_macro,
                delta_EI=ei_macro-ei_micro, EI_matched_micro=matched,
                lifted_preparation=(qmacro @ lift).tolist())


def e08_fixed_ensemble_data_processing():
    rng = np.random.default_rng(1977)
    comparisons = 0
    for _ in range(10):
        p = rng.uniform(.01, 1, (4, 4)); p /= p.sum(axis=1)[:, None]
        q = rng.uniform(.01, 1, 4); q /= q.sum()
        joint = q[:, None] * p
        micro = mutual_channel(p, q)
        for labels in partitions(4):
            c, _ = aggregation(labels)
            macro = mi_joint(c.T @ joint @ c)
            require(macro <= micro + 1e-12, "fixed-ensemble DPI failed")
            comparisons += 1
    return dict(random_seed=1977, fixed_ensemble_comparisons=comparisons)


def e09_svd_does_not_imply_ei():
    p = np.full((4, 4), .25)
    spectrum = np.linalg.svd(p, compute_uv=False)
    near(spectrum, [1, 0, 0, 0])
    rank = int((spectrum > 1e-12).sum())
    delta_svd = float(spectrum.sum() * (1/rank - 1/4))
    near(delta_svd, .75)
    near(mutual_channel(p, np.full(4, .25)), 0)
    count = 0
    for labels in partitions(4):
        c, lift = aggregation(labels)
        reduced = lift @ p @ c
        near(reduced, np.tile(reduced[0], (len(reduced), 1)))
        near(mutual_channel(reduced, np.full(len(reduced), 1/len(reduced))), 0)
        count += 1
    near(count, 15)
    block = matrices()[0]
    bs = np.linalg.svd(block, compute_uv=False)
    near(bs, [1, 1, 0, 0])
    near(bs.sum() * (1/2 - 1/4), .5)
    return dict(rank=rank, singular_values=spectrum.tolist(), delta_svd=delta_svd,
                EI=0, all_partitions_checked=count, spectral_rank_tolerance=1e-12)


def e10_inverse_is_not_detailed_balance():
    p = np.eye(3)[[1, 2, 0]]
    inverse = stochastic(np.linalg.inv(p))
    near(p @ inverse, np.eye(3))
    mu = np.full(3, 1/3)
    near(mu @ p, mu)
    flow = mu[:, None] * p
    require(not np.allclose(flow, flow.T), "cycle incorrectly passed detailed balance")
    near(flow[0, 1], 1/3); near(flow[1, 0], 0)
    return dict(stochastic_inverse=True, detailed_balance=False,
                forward_flow=float(flow[0, 1]), reverse_flow=float(flow[1, 0]))


def e11_topological_conjugacy_rates():
    transform = lambda x: math.copysign(x*x, x)
    for x, t in itertools.product([-2, -.2, 0, .3, 4], [0, .2, 1, 3]):
        near(transform(x * math.exp(-t)), transform(x) * math.exp(-2*t))
    near(-derivative(lambda x: -x, 0), 1)
    near(-derivative(lambda y: -2*y, 0), 2)
    return dict(time_factor=1, local_rates=[1, 2],
                transformation='sign(x)*abs(x)**2; inverse not differentiable at zero')


def e12_parameter_scaling_nonidentifiability():
    sigma = 2.2
    maximum = 0.
    for gamma, scale in itertools.product(np.linspace(-2, 2, 31), [.1, 2, 100]):
        original = math.tanh(sigma * gamma)
        transformed = math.tanh((sigma/scale) * (scale*gamma))
        near(original, transformed)
        maximum = max(maximum, abs(original-transformed))
    # Response derivatives wrt sigma and unknown amplitude a are collinear.
    a = 3.
    g = np.linspace(-1, 1, 21)
    sech2 = 1 / np.cosh(sigma*a*g)**2
    jacobian = np.column_stack([a*g*sech2, sigma*g*sech2])
    near(jacobian @ np.array([sigma, -a]), np.zeros(len(g)))
    require(np.linalg.matrix_rank(jacobian, tol=1e-10) == 1, "expected unidentifiable product")
    return dict(max_response_error=maximum, response_jacobian_rank=1,
                identified_combination='sigma*a')


def e13_generic_heat_structure():
    checked = 0
    for ca, cb, conductance, ta, tb in itertools.product([2., 5.], [3., 7.], [.1, 3.], [250., 310.], [260., 310.]):
        energy = np.array([ca*ta, cb*tb])
        entropy_fn = lambda e: ca*np.log((e[0]/ca)/300) + cb*np.log((e[1]/cb)/300)
        gradient = np.array([1/ta, 1/tb])
        numeric = []
        for axis in range(2):
            v = np.zeros(2); v[axis] = 1e-3
            numeric.append((entropy_fn(energy+v)-entropy_fn(energy-v))/(2e-3))
        near(gradient, numeric, atol=1e-10)
        m = conductance*ta*tb*np.array([[1, -1], [-1, 1]])
        near(m, m.T)
        require(np.linalg.eigvalsh(m).min() >= -1e-10, "M not PSD")
        near(m @ np.ones(2), 0)
        flow = m @ gradient
        heat_current = conductance*(ta-tb)
        near(flow, [-heat_current, heat_current])
        production = float(gradient @ m @ gradient)
        near(production, conductance*(ta-tb)**2/(ta*tb))
        require(production >= -1e-12, "negative entropy production")
        near(flow.sum(), 0)
        checked += 1
    return dict(parameter_combinations=checked, gradient_and_balance_checks=True,
                poisson_operator='identically zero; Jacobi identity trivial')


def e14_viability_at_fixed_recovery_rate():
    for burden in [.5, 1.5]:
        equilibrium = 1-burden
        solution = lambda t: equilibrium + (1-equilibrium)*math.exp(-t)
        for t in [.1, .5, 1, 2]:
            near(derivative(solution, t), -(solution(t)-1)-burden, atol=1e-9)
        near(-derivative(lambda z: -(z-1)-burden, equilibrium), 1)
    crossing = math.log(3)
    near(-.5+1.5*math.exp(-crossing), 0)
    require(-.5+1.5*math.exp(-(crossing+.1)) < 0, "must exit after crossing")
    for r, zeq, boundary, maximum_control in [(1., 1., 0., 0.), (.2, 4., 1., .5)]:
        critical = r*(zeq-boundary)+maximum_control
        for offset in [-.1, 0., .1]:
            burden = critical+offset
            near(-r*(boundary-zeq)+maximum_control-burden, -offset)
    return dict(recovery_rates=[1, 1], equilibria=[.5, -.5],
                first_boundary_time=crossing, safe_region='z >= 0')


def e15_predictive_states():
    transition = np.array([[.8, .2], [.2, .8]])
    def future_distribution(last, kernel):
        values = []
        for future in itertools.product([0, 1], repeat=3):
            probability = 1.
            previous = last
            for symbol in future:
                probability *= kernel[previous, symbol]
                previous = symbol
            values.append(probability)
        return np.array(values)
    # Independently enumerate joint path probabilities and condition on histories.
    representatives = {}
    maximum_error = 0.
    for history in itertools.product([0, 1], repeat=4):
        history_mass = .5
        for previous, following in zip(history, history[1:]):
            history_mass *= transition[previous, following]
        joint_masses = []
        for future in itertools.product([0, 1], repeat=3):
            path = history + future
            mass = .5
            for previous, following in zip(path, path[1:]):
                mass *= transition[previous, following]
            joint_masses.append(mass)
        conditioned = np.array(joint_masses) / history_mass
        reference = future_distribution(history[-1], transition)
        near(conditioned, reference)
        maximum_error = max(maximum_error, float(np.abs(conditioned-reference).max()))
        if history[-1] in representatives:
            near(conditioned, representatives[history[-1]])
        representatives[history[-1]] = conditioned
    # Two distinct last symbols imply distinguishable next-symbol laws.
    require(not np.allclose(transition[0], transition[1]), "states should differ")
    near(future_distribution(0, transition).sum(), 1)
    iid = np.full((2, 2), .5)
    near(future_distribution(0, iid), future_distribution(1, iid))
    return dict(persistent_binary_chain_predictive_states=2, iid_predictive_states=1,
                joint_paths_enumerated=128, max_conditioning_error=maximum_error,
                scope='exact finite-state examples, not a learned epsilon-machine')


def e16_current_document_links(output):
    checked = 0
    for path in list(BASE.glob('*.md')) + [BASE/'verification/README.md']:
        content = path.read_text(encoding='utf-8')
        require(sum(line.startswith('```') for line in content.splitlines()) % 2 == 0,
                f"unbalanced fences: {path.name}")
        for target in re.findall(r'\]\(([^)]+)\)', content):
            if '://' in target or target.startswith('#'):
                continue
            target = unquote(target.split('#', 1)[0])
            resolved = (path.parent/target).resolve()
            if resolved == output.resolve():
                continue
            require(resolved.exists(), f"broken link {path.name}: {target}")
            checked += 1
    return dict(local_links_checked=checked)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=Path(__file__).with_name('extension_results.json'))
    args = parser.parse_args()
    checks = [(name, fn) for name, fn in sorted(globals().items())
              if re.fullmatch(r'e\d\d_.*', name) and callable(fn)]
    for name, function in checks:
        try:
            evidence = function(args.output) if name.startswith('e16_') else function()
            RESULTS.append(dict(name=name, status='passed', evidence=evidence))
        except Exception as exc:
            RESULTS.append(dict(name=name, status='failed', error=str(exc)))
    failed = [r['name'] for r in RESULTS if r['status'] != 'passed']
    report = dict(revision='3', generated_at=dt.datetime.now(dt.timezone.utc).isoformat(),
                  python=platform.python_version(), numpy=np.__version__, count=len(RESULTS),
                  passed=len(RESULTS)-len(failed), failed=len(failed),
                  empirical_validation=False, production_package_tests_run=False,
                  full_literature_reproductions_run=False, checks=RESULTS)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
    print(json.dumps(dict(count=report['count'], passed=report['passed'], failed=failed,
                          report=str(args.output.resolve())), ensure_ascii=False))
    return int(bool(failed))


if __name__ == '__main__':
    raise SystemExit(main())
