"""Minimal Correspondence contract (Milestone 1).

Content basis:
- FORMALISM.md §1: T ∘ Φ_j^t ≈ Φ_k^{c t} ∘ T (conjugacy / semiconjugacy schema)
- context_transformations.md §3–5: T1–T4 (chain rule, time reparam, compatibility, composition)

Legacy names (CREP/UTAC/AFET, "self-similarity") stay in documents; public API uses
Observation/Dynamics/Coupling/Correspondence terminology from GLOSSARY.md.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Mapping, Optional, Sequence, Union

import numpy as np

State = Union[float, np.ndarray]
VectorField = Callable[[State], State]
FlowMap = Callable[[State, float], State]
StateTransform = Callable[[State], State]
BoolPred = Callable[[State], bool]


@dataclass(frozen=True)
class ModelRef:
    """Reference to a dynamical description (source or target side)."""

    name: str
    field: Optional[VectorField] = None
    flow: Optional[FlowMap] = None
    notes: str = ""


@dataclass(frozen=True)
class StateMap:
    """State transformation T: source → target (FORMALISM.md §1)."""

    map_fn: StateTransform
    name: str = "T"
    differentiable: bool = True

    def __call__(self, state: State) -> State:
        return self.map_fn(state)


@dataclass(frozen=True)
class TimeMap:
    """Time correspondence: constant scale c, or state/time-dependent a(z,t)=dτ/dt (T2)."""

    name: str = "time_map"
    constant_scale: Optional[float] = None
    scale_fn: Optional[Callable[[State, float], float]] = None

    def scale_at(self, state: State, time: float) -> float:
        if self.constant_scale is not None:
            return float(self.constant_scale)
        if self.scale_fn is not None:
            return float(self.scale_fn(state, time))
        return 1.0


@dataclass(frozen=True)
class Scope:
    """First-class validity domain for a correspondence (Revision 3.2)."""

    description: str
    assumptions: tuple[str, ...] = ()
    state_ok: Optional[BoolPred] = None
    time_horizon: Optional[tuple[float, float]] = None

    def contains(self, state: State, time: Optional[float] = None) -> bool:
        if self.state_ok is not None and not bool(self.state_ok(state)):
            return False
        if time is not None and self.time_horizon is not None:
            lo, hi = self.time_horizon
            if not (lo <= float(time) <= hi):
                return False
        return True


@dataclass(frozen=True)
class ErrorMetric:
    name: str = "abs"
    atol: float = 1e-10
    rtol: float = 1e-9

    def near(self, a: Any, b: Any) -> bool:
        return bool(np.allclose(a, b, atol=self.atol, rtol=self.rtol))


@dataclass(frozen=True)
class Residual:
    """Documented deviation from an exact correspondence identity."""

    value: float
    kind: str
    at_state: Any = None
    at_time: Any = None
    detail: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class CorrespondenceReport:
    ok: bool
    max_residual: float
    residuals: tuple[Residual, ...]
    evidence: Mapping[str, Any]
    kind: str


@dataclass(frozen=True)
class Correspondence:
    """Typed correspondence: maps + scope + residual/error measure.

    Sketch (ARCHITECTURE_ROADMAP / Astra):
        Correspondence(source, target, state_map, scope, time_map=..., metric=...)
    """

    source: ModelRef
    target: ModelRef
    state_map: StateMap
    scope: Scope
    time_map: Optional[TimeMap] = None
    metric: Optional[ErrorMetric] = None
    context_map: Optional[Callable[..., Any]] = None
    parameter_map: Optional[Callable[[State], State]] = None

    def _metric(self) -> ErrorMetric:
        return self.metric if self.metric is not None else ErrorMetric()

    def conjugacy_residual(self, state: State, time: float) -> Residual:
        """Residual of T∘Φ_j^t − Φ_k^{c t}∘T (FORMALISM.md §1)."""
        if self.source.flow is None or self.target.flow is None:
            raise ValueError("conjugacy_residual requires source.flow and target.flow")
        if not self.scope.contains(state, time):
            raise ValueError("state/time outside declared scope")
        c = 1.0 if self.time_map is None else self.time_map.scale_at(state, time)
        left = self.state_map(self.source.flow(state, time))
        right = self.target.flow(self.state_map(state), c * time)
        value = float(np.max(np.abs(np.asarray(left, dtype=float) - np.asarray(right, dtype=float))))
        return Residual(value=value, kind="conjugacy", at_state=state, at_time=time, detail={"c": c})

    def verify_conjugacy(
        self,
        states: Sequence[State],
        times: Sequence[float],
    ) -> CorrespondenceReport:
        residuals = []
        for x in states:
            for t in times:
                residuals.append(self.conjugacy_residual(x, t))
        max_r = max((r.value for r in residuals), default=0.0)
        ok = all(self._metric().near(r.value, 0.0) for r in residuals)
        return CorrespondenceReport(
            ok=ok,
            max_residual=max_r,
            residuals=tuple(residuals),
            evidence={"n_pairs": len(residuals), "max_conjugacy_residual": max_r},
            kind="conjugacy",
        )

    def local_rate(self, which: str, at: State = 0.0, step: float = 1e-5) -> float:
        """Local linearization rate -f'(at) for source or target field."""
        model = self.source if which == "source" else self.target
        if model.field is None:
            raise ValueError(f"{which}.field required for local_rate")
        f = model.field
        df = (f(at + step) - f(at - step)) / (2 * step)
        return float(-df)

    def t1_residual(
        self,
        pi: Callable[[Any, Any, float], float],
        x: Callable[[float], float],
        c: Callable[[float], float],
        predicted_dot: Callable[[float, float], float],
        time: float,
        step: float = 1e-5,
    ) -> Residual:
        """T1: compare d/dt π(x(t),c(t),t) to predicted chain-rule RHS."""
        numeric = (
            pi(x(time + step), c(time + step), time + step)
            - pi(x(time - step), c(time - step), time - step)
        ) / (2 * step)
        y = pi(x(time), c(time), time)
        pred = predicted_dot(time, y)
        value = abs(numeric - pred)
        return Residual(
            value=value,
            kind="T1",
            at_time=time,
            detail={"numeric": numeric, "predicted": pred, "y": y},
        )

    def t2_dy_dtau(
        self,
        y_of_t: Callable[[float], float],
        tau_of_t: Callable[[float], float],
        transformed_rhs: Callable[[float], float],
        time: float,
        step: float = 1e-5,
    ) -> Residual:
        """T2: (dy/dt)/(dτ/dt) vs transformed RHS."""
        dy = (y_of_t(time + step) - y_of_t(time - step)) / (2 * step)
        dtau = (tau_of_t(time + step) - tau_of_t(time - step)) / (2 * step)
        numeric = dy / dtau
        pred = transformed_rhs(time)
        return Residual(
            value=abs(numeric - pred),
            kind="T2",
            at_time=time,
            detail={"numeric": numeric, "predicted": pred},
        )

    def t3_compatibility_residual(
        self,
        fine_field: VectorField,
        coarse_field: VectorField,
        R: StateTransform,
        state: State,
        step: float = 1e-5,
    ) -> Residual:
        """T3: DR(ξ) F_fine(ξ) − F(R(ξ)) for scalar R via FD."""
        xi = float(state)
        dR = (R(xi + step) - R(xi - step)) / (2 * step)
        left = dR * float(fine_field(xi))
        right = float(coarse_field(R(xi)))
        return Residual(
            value=abs(left - right),
            kind="T3",
            at_state=xi,
            detail={"left": left, "right": right},
        )

    def t4_composition_residual(
        self,
        t_ji: StateTransform,
        t_kj: StateTransform,
        f_i: VectorField,
        f_j: VectorField,
        f_k: VectorField,
        a_ji: Callable[[State], float],
        a_kj: Callable[[State], float],
        state: State,
        step: float = 1e-5,
    ) -> Residual:
        """T4 residual composition identity (context_transformations.md §5)."""
        x = float(state)

        def d_tji(xx: float) -> float:
            return (t_ji(xx + step) - t_ji(xx - step)) / (2 * step)

        def d_tkj(yy: float) -> float:
            return (t_kj(yy + step) - t_kj(yy - step)) / (2 * step)

        def d_comp(xx: float) -> float:
            return (t_kj(t_ji(xx + step)) - t_kj(t_ji(xx - step))) / (2 * step)

        y = t_ji(x)
        r_ji = d_tji(x) * float(f_i(x)) - float(a_ji(x)) * float(f_j(y))
        r_kj = d_tkj(y) * float(f_j(y)) - float(a_kj(y)) * float(f_k(t_kj(y)))
        direct = d_comp(x) * float(f_i(x)) - float(a_ji(x)) * float(a_kj(y)) * float(f_k(t_kj(y)))
        composed = d_tkj(y) * r_ji + float(a_ji(x)) * r_kj
        return Residual(
            value=abs(direct - composed),
            kind="T4",
            at_state=x,
            detail={"direct": direct, "composed": composed, "r_ji": r_ji, "r_kj": r_kj},
        )
