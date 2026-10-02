"""Finite velocity mixture and measurement operator (Paket MU2, plan §6.1-§6.2).

q(v) is a normalised FLUX distribution of live atoms arriving at plane 1
(not a spatial density), here a finite mixture of velocity classes with
positive weights summing to 1. Per class i:

    S_i = exp(-2 L / (v_i tau))                 survival plane 1 -> plane 3
    phi_i = phi0 + s K(v_i) a + phi_sys_i       with K(v) = 2 pi L^2 / (d v^2)
    W = sum_i q_i A_i eps_i S_i                 (weight of detected signal)
    F = sum_i q_i A_i eps_i S_i C_i exp(i phi_i) / W   (complex contrast)

Expected counts for scan bin j with its OWN measurement time t_j, scan phase
alpha_j and orientation s_j in {-1, +1}:

    lambda_j = t_j b + t_j R W (1 + Re(exp(i alpha_j) F))

F adds expected intensity modulations of different velocity classes; it
claims no quantum coherence between atoms. W = 0 means no signal; F = 0
means the modulation phase is undefined (``arg(0)`` is never reported).
Phase averages or the phase at the mean velocity do NOT replace the sum
(E[1/v^2] != 1/E[v]^2).

Rates, background, contrast and offsets are SHARED within a declared block
(here: one ``ForwardModel``); a free mean per bin would destroy the
identifiability of interest and is not offered.
"""
from __future__ import annotations

import cmath
import math
from dataclasses import dataclass
from fractions import Fraction
from typing import List, Optional, Sequence, Tuple

from scoped_correspondence.errors import ScopeViolationError
from scoped_correspondence.muonium.kinematics import Geometry, _num


@dataclass(frozen=True)
class VelocityClass:
    v: float  # [m/s]
    weight: float  # flux fraction at plane 1
    transmission: float  # A: mean transmission -- no default: A = C = 1 would violate A (1 + C) <= 1
    contrast: float  # C
    efficiency: float = 1.0  # eps: detection efficiency
    phi_sys: float = 0.0  # systematic phase of this class [rad]

    def __post_init__(self) -> None:
        _num(self.v, "v", positive=True)
        _num(self.weight, "weight", positive=True)
        for name in ("transmission", "efficiency", "contrast"):
            x = _num(getattr(self, name), name)
            if not 0 <= x <= 1:
                raise ScopeViolationError(f"{name} must lie in [0, 1], got {x}")
        _num(self.phi_sys, "phi_sys")


@dataclass(frozen=True)
class ScanBin:
    t: float  # measurement time of THIS bin [s]
    alpha: float  # scan phase [rad]
    s: int = 1  # orientation

    def __post_init__(self) -> None:
        _num(self.t, "bin measurement time", positive=True)
        _num(self.alpha, "alpha")
        if self.s not in (-1, 1):
            raise ScopeViolationError("orientation s must be -1 or +1")


@dataclass(frozen=True)
class ForwardModel:
    L: float
    d: float
    tau: float
    classes: Tuple[VelocityClass, ...]
    rate: float  # R at the declared entrance (plane 1)
    background: float  # b [1/s]
    phi0: float = 0.0
    transmission_is_probability: bool = True
    weight_tol: float = 1e-12

    def __post_init__(self) -> None:
        _num(self.L, "L", positive=True)
        _num(self.d, "d", positive=True)
        _num(self.tau, "tau", positive=True)
        if not self.classes:
            raise ScopeViolationError("at least one velocity class is required")
        tot = sum(c.weight for c in self.classes)
        exact = all(isinstance(c.weight, (int, Fraction)) for c in self.classes)
        if (tot != 1) if exact else abs(tot - 1) > self.weight_tol:
            raise ScopeViolationError(f"velocity-class weights must sum to 1, got {tot}")
        if self.rate < 0 or self.background < 0:
            raise ScopeViolationError("rate and background must be >= 0")
        _num(self.rate, "rate")
        _num(self.background, "background")
        if self.transmission_is_probability:
            for c in self.classes:
                if c.transmission * (1 + c.contrast) > 1 + 1e-15:
                    raise ScopeViolationError("A (1 + C) <= 1 is required when A is a transmission probability")

    def survival(self, v: float) -> float:
        return math.exp(-2 * self.L / (v * self.tau))

    def K(self, v: float) -> float:
        return Geometry(L=self.L, d=self.d, v=v).K()

    def class_terms(self) -> List[float]:
        return [c.weight * c.transmission * c.efficiency * self.survival(c.v) for c in self.classes]

    def detected_weights(self) -> Optional[List[float]]:
        """Velocity mixture of DETECTED atoms (survival and efficiency
        applied): slow atoms decay more often. None if W = 0."""
        terms = self.class_terms()
        W = sum(terms)
        return None if W == 0 else [t / W for t in terms]

    def complex_contrast(self, a: float, s: int = 1) -> Tuple[float, Optional[complex]]:
        """Returns (W, F); F is None when W = 0 (no signal)."""
        terms = self.class_terms()
        W = sum(terms)
        if W == 0:
            return 0.0, None
        acc = 0j
        for c, w in zip(self.classes, terms):
            phi = self.phi0 + s * self.K(c.v) * a + c.phi_sys
            acc += w * c.contrast * cmath.exp(1j * phi)
        return W, acc / W

    def modulation_phase(self, a: float, s: int = 1, *, tol: float = 1e-15) -> Optional[float]:
        """arg(F), or None when |F| <= tol (phase undefined)."""
        _, F = self.complex_contrast(a, s)
        if F is None or abs(F) <= tol:
            return None
        return cmath.phase(F)

    def expected_counts(self, a: float, bins: Sequence[ScanBin]) -> List[float]:
        _num(a, "a")
        out = []
        for b in bins:
            W, F = self.complex_contrast(a, b.s)
            mod = 0.0 if F is None else (cmath.exp(1j * b.alpha) * F).real
            out.append(b.t * self.background + b.t * self.rate * W * (1 + mod))
        return out


def total_measurement_time(bins: Sequence[ScanBin]) -> float:
    """The sum of the per-bin times -- a total time is never re-used per bin."""
    return sum(b.t for b in bins)


def equal_time_bins(total_time: float, alphas: Sequence[float], s: int = 1) -> List[ScanBin]:
    """Split a TOTAL time across bins (so the bins sum to it)."""
    _num(total_time, "total time", positive=True)
    if not alphas:
        raise ScopeViolationError("need at least one scan phase")
    return [ScanBin(total_time / len(alphas), a, s) for a in alphas]


__all__ = ["VelocityClass", "ScanBin", "ForwardModel", "total_measurement_time", "equal_time_bins"]
