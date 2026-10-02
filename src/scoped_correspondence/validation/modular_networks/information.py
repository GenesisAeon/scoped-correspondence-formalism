"""Information, PID and directedness adapters (Paket ON5, plan §7.3, §7.4).

Thin adapters over the EXISTING implementations -- no new PID, entropy or
directed-information library:

- ``information_signature``: (I(R1;Y), I(R2;Y), I(R1,R2;Y)) of an exact
  finite joint; the signature (0, 0, 1) of XOR is visible WITHOUT committing
  to a redundancy measure;
- ``pid_report``: the existing BROJA bivariate PID (axes r1, r2, y), labelled
  with its measure; another redundancy measure may give other atoms;
- ``directed_report``: the existing Massey directed information. It is NEVER
  labelled causal: a common driver yields directed information without any
  intervention effect (ON-C15); ``intervention_effect`` checks a declared
  finite generator under do(.) separately;
- ``label_confounding``: information between a label and a nuisance variable
  (block time, plate, order) -- if the stimulus is confounded with time, a
  decoder may read time (ON-C16).

Every joint is validated STRICTLY here (non-negative, finite, total mass 1)
because the existing functions renormalise silently (ON0 finding B1).
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Callable, Dict, Hashable, Iterable, Mapping, Sequence, Tuple

import numpy as np

from scoped_correspondence.errors import ScopeViolationError
from scoped_correspondence.information_decomposition.broja import broja_pid_bivariate
from scoped_correspondence.observation.directed_information import directed_information

TOL = 1e-12


def _check_pmf(values: Iterable[float], what: str) -> None:
    vals = [float(v) for v in values]
    if not vals or any(not math.isfinite(v) for v in vals) or any(v < 0 for v in vals):
        raise ScopeViolationError(f"{what}: masses must be finite and non-negative")
    if abs(sum(vals) - 1.0) > TOL:
        raise ScopeViolationError(f"{what}: total mass must be 1 (no silent renormalisation)")


def _mi(joint: Mapping[Tuple[Hashable, Hashable], float]) -> float:
    pa: Dict = {}
    pb: Dict = {}
    for (a, b), p in joint.items():
        pa[a] = pa.get(a, 0.0) + p
        pb[b] = pb.get(b, 0.0) + p
    return float(sum(p * math.log2(p / (pa[a] * pb[b])) for (a, b), p in joint.items() if p > 0))


def information_signature(joint_r1r2y: Mapping[Tuple[Hashable, Hashable, Hashable], float]) -> Tuple[float, float, float]:
    _check_pmf(joint_r1r2y.values(), "joint p(r1, r2, y)")
    m1: Dict = {}
    m2: Dict = {}
    m12: Dict = {}
    for (a, b, y), p in joint_r1r2y.items():
        m1[(a, y)] = m1.get((a, y), 0.0) + p
        m2[(b, y)] = m2.get((b, y), 0.0) + p
        m12[((a, b), y)] = m12.get(((a, b), y), 0.0) + p
    return _mi(m1), _mi(m2), _mi(m12)


@dataclass(frozen=True)
class PIDReport:
    redundancy: float
    unique_r1: float
    unique_r2: float
    synergy: float
    I_joint: float
    converged: bool
    n_starts: int
    start_spread_bits: float  # max spread of the unique-information optima over solver starts
    measure: str = "BROJA (Bertschinger et al. 2014), existing broja_pid_bivariate"
    caveat: str = "atoms depend on the chosen redundancy measure; the signature is measure-free"


def pid_report(joint: np.ndarray) -> PIDReport:
    J = np.asarray(joint, dtype=float)
    if J.ndim != 3:
        raise ScopeViolationError("joint must have axes (r1, r2, y)")
    _check_pmf(J.ravel(), "joint p(r1, r2, y)")
    r = broja_pid_bivariate(J)
    spread = max((max(o) - min(o)) for o in (r.unq1_optima, r.unq2_optima) if o) if (r.unq1_optima or r.unq2_optima) else float("nan")
    return PIDReport(r.redundancy, r.unique_source_1, r.unique_source_2, r.synergy, r.I_joint, bool(r.converged), int(r.n_starts),
                     float(spread))


@dataclass(frozen=True)
class DirectedReport:
    I_directed: float
    I_mutual: float
    summands: Tuple[float, ...]
    interpretation: str = "statistical directedness of the declared sequence model; NOT an intervention effect"
    causal_claim: bool = False


def directed_report(joint_sequences: Mapping[Tuple[Tuple[int, ...], Tuple[int, ...]], float]) -> DirectedReport:
    _check_pmf(joint_sequences.values(), "joint sequence distribution")
    r = directed_information(joint_sequences)
    return DirectedReport(r.I_directed, r.I_mutual, tuple(r.summands))


def intervention_effect(generator: Callable[[Hashable, Dict[str, int]], Dict[str, int]], u_dist: Mapping[Hashable, float],
                        variable: str, values: Sequence[int], target: str) -> bool:
    """True iff do(variable = v) changes the distribution of ``target`` for
    some pair of values, in a DECLARED finite generator (exogenous U with
    distribution u_dist). Separate from any directed-information estimate."""
    _check_pmf(u_dist.values(), "exogenous distribution")
    dists = []
    for v in values:
        d: Dict = {}
        for u, p in u_dist.items():
            t = generator(u, {variable: v})[target]
            d[t] = d.get(t, 0.0) + p
        dists.append(d)
    keys = set().union(*dists)
    return any(abs(a.get(k, 0.0) - b.get(k, 0.0)) > TOL for a in dists for b in dists for k in keys)


def label_confounding(pairs: Mapping[Tuple[Hashable, Hashable], float]) -> float:
    """I(label; nuisance) in bits for a declared design distribution."""
    _check_pmf(pairs.values(), "design distribution p(label, nuisance)")
    return _mi(pairs)


__all__ = ["information_signature", "PIDReport", "pid_report", "DirectedReport", "directed_report", "intervention_effect",
           "label_confounding"]
