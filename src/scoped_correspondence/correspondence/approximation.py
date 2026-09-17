"""Approximate simulation certificate for a fixed StateMap T (Milestone 10).

Girard & Pappas 2007 (DOI 10.1109/TAC.2007.895849) define approximate
simulation via a pseudometric with an explicit error budget ε; exact
conjugacy is the zero-error special case. FORMALISM.md §1 /
``correspondence/contract.py`` already expose the pointwise residual of

    T ∘ Φ_j^t  −  Φ_k^{c t} ∘ T

via ``Correspondence.conjugacy_residual`` / ``verify_conjugacy``.

This module interprets those residuals against a user budget ``epsilon``.
It implements **only** the fixed-``StateMap`` specialty already present
on ``Correspondence`` — **not** the full relational approximate
simulation of Girard & Pappas (arbitrary relation between states).

Disclaimer (analogous to ``check_generic_structure``): an
``ApproximationCertificate`` with ``ok=True`` does **not** prove the
existence of a general simulation / bisimulation relation. It only
certifies that the residuals of the given fixed map ``T`` stay within
``epsilon`` on the sampled ``(state, time)`` pairs inside the declared
``Scope``. ``relation_kind`` is therefore always ``"fixed_map_bound"``.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence, Union

import numpy as np

from scoped_correspondence.correspondence.contract import (
    Correspondence,
    Residual,
    Scope,
)

State = Union[float, np.ndarray]

FIXED_MAP_BOUND = "fixed_map_bound"

_DEFAULT_ASSUMPTIONS: tuple[str, ...] = (
    "fixed StateMap T specialty only — not full relational approximate simulation "
    "(Girard & Pappas 2007)",
    "certificate does NOT prove existence of a general simulation / bisimulation "
    "relation (analogous to check_generic_structure disclaimer)",
    "uses Correspondence.conjugacy_residual / verify_conjugacy unchanged "
    "(FORMALISM.md §1 / correspondence/contract.py)",
    "ok means max conjugacy residual over the sampled (state, time) grid "
    "is <= epsilon; not a continuum quantification beyond the samples",
)


@dataclass(frozen=True)
class ApproximationCertificate:
    """ε-budget certificate for conjugacy residuals of a fixed StateMap T.

    ``relation_kind`` is always ``\"fixed_map_bound\"`` — never
    ``\"simulation\"`` / ``\"bisimulation\"``, because the full relational
    Girard–Pappas contract is out of scope.

    Passing (``ok=True``) does **not** prove existence of a general
    simulation relation; it only bounds the residuals of the given ``T``
    on the sampled pairs (see module docstring).
    """

    epsilon: float
    max_residual: float
    ok: bool  # max_residual <= epsilon
    relation_kind: str  # MUST be "fixed_map_bound"
    scope: Scope
    assumptions: tuple[str, ...]
    residuals: tuple[Residual, ...]
    source: str = "Girard & Pappas 2007, DOI 10.1109/TAC.2007.895849"

    def __post_init__(self) -> None:
        if self.relation_kind != FIXED_MAP_BOUND:
            raise ValueError(
                f"ApproximationCertificate.relation_kind must be "
                f"{FIXED_MAP_BOUND!r} (fixed StateMap specialty); "
                f"got {self.relation_kind!r}. Do not use "
                f"'simulation'/'bisimulation' — full relational check "
                f"is out of scope."
            )


def verify_approximate_simulation(
    correspondence: Correspondence,
    states: Sequence[State],
    times: Sequence[float],
    epsilon: float,
) -> ApproximationCertificate:
    """Interpret conjugacy residuals against an ε budget (fixed-T specialty).

    Calls **only** ``Correspondence.verify_conjugacy`` (which itself uses
    ``conjugacy_residual``). Does **not** edit ``contract.py``.

    Returns an ``ApproximationCertificate`` with
    ``relation_kind=\"fixed_map_bound\"``. This does **not** prove
    existence of a general simulation relation — only that the given
    fixed ``StateMap`` residuals stay within ``epsilon`` on the sample.
    """
    if float(epsilon) < 0.0:
        raise ValueError(f"epsilon must be >= 0; got {epsilon!r}")

    report = correspondence.verify_conjugacy(states, times)
    max_residual = float(report.max_residual)
    ok = bool(max_residual <= float(epsilon))

    assumptions = _DEFAULT_ASSUMPTIONS + (
        f"scope: {correspondence.scope.description}",
        *tuple(correspondence.scope.assumptions),
    )

    return ApproximationCertificate(
        epsilon=float(epsilon),
        max_residual=max_residual,
        ok=ok,
        relation_kind=FIXED_MAP_BOUND,
        scope=correspondence.scope,
        assumptions=assumptions,
        residuals=report.residuals,
        source="Girard & Pappas 2007, DOI 10.1109/TAC.2007.895849",
    )


__all__ = [
    "FIXED_MAP_BOUND",
    "ApproximationCertificate",
    "verify_approximate_simulation",
]
