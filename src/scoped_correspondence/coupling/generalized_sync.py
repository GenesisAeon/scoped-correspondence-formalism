"""Generalized / drive–response synchronisation (Pecora & Carroll 1990) — Milestone 39.

Mathematical drive–response synchronisation for coupled dynamical systems
(Pecora & Carroll, Phys. Rev. Lett. 64, 821–824, 1990,
DOI 10.1103/PhysRevLett.64.821). This is a **mathematical** account of
synchronisation / dynamical entrainment — **not** Luhmann sociology, and
**not** an identification with GENERIC ``L,M`` or ``A_ij ≡ L_ij``.

mathematische Fassung im Sinne dynamischer Mitführung, KEINE
Luhmann-Soziologie, KEINE Gleichsetzung.

Drive–response setup
--------------------
Drive ``ẋ = f(x)``, response ``ẏ = g(y, x)``. The variational equation
along the response,

    δẏ = D_y g(x(t), y(t)) · δy,

has **conditional Lyapunov exponents** (CLEs). If **all** CLEs are
negative, the response synchronises: ``y(t) → Φ(x(t))`` for a map ``Φ``.

Linear special cases implemented here (hand-checkable only; no chaotic
high-dimensional examples in this milestone):

1. Scalar variational equation ``δẏ = a · δy`` → CLE ``= a``;
   synchronisation ⟺ ``a < 0`` (``conditional_lyapunov_linear``).

2. Linear drive–response pair ``ẋ = -x``, ``ẏ = -k y + c x`` with
   ansatz ``y = φ · x`` → ``φ = c / (k - 1)`` for ``k ≠ 1``, CLE ``= -k``
   (``linear_drive_response_map``). Raises ``ScopeViolationError`` if
   ``k = 1`` (denominator vanishes).

Mandatory bridge note (verbatim; also in JSON report)
-----------------------------------------------------
Das CLE<0-Kriterium hier ähnelt strukturell der bereits gemergten
Kontraktionsanalyse (M14, `dynamics/contraction.py`, Lohmiller &
Slotine 1998) — beide sind Vorzeichenkriterien an einer
Variationsgleichung. Das ist KEINE Identität: M14 prüft globale
metrische Kontraktion EINES Systems, dieses Modul prüft
Drive-Response-Synchronisation ZWISCHEN zwei gekoppelten Systemen in
`coupling`. Eine mögliche künftige `correspondence`-Brücke zwischen
den beiden Kriterien ist denkbar, aber HIER NICHT behauptet oder
implementiert — offener, unbewiesener Kandidat, analog zum
dokumentierten Turing↔dynamics-Brückenkandidaten in
`pattern_formation/core.py`.

Scope
-----
- Linear, scalar, hand-checkable formulas only.
- Does **not** mutate ``coupling/core.py``, ``dynamics/contraction.py``,
  or package-root ``scoped_correspondence.__init__``.
- Does **not** claim CLE ≡ M14 contraction rate.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Union

from scoped_correspondence.errors import ScopeViolationError

Number = Union[int, float]

SOURCE = (
    "Pecora & Carroll 1990, Phys. Rev. Lett. 64, 821–824, "
    "DOI 10.1103/PhysRevLett.64.821"
)

DOI = "10.1103/PhysRevLett.64.821"

# Verbatim mandatory bridge note (ticket §4) — must appear in module
# docstring AND in the JSON verification report text field.
BRIDGE_NOTE: str = """Das CLE<0-Kriterium hier ähnelt strukturell der bereits gemergten
Kontraktionsanalyse (M14, `dynamics/contraction.py`, Lohmiller &
Slotine 1998) — beide sind Vorzeichenkriterien an einer
Variationsgleichung. Das ist KEINE Identität: M14 prüft globale
metrische Kontraktion EINES Systems, dieses Modul prüft
Drive-Response-Synchronisation ZWISCHEN zwei gekoppelten Systemen in
`coupling`. Eine mögliche künftige `correspondence`-Brücke zwischen
den beiden Kriterien ist denkbar, aber HIER NICHT behauptet oder
implementiert — offener, unbewiesener Kandidat, analog zum
dokumentierten Turing↔dynamics-Brückenkandidaten in
`pattern_formation/core.py`."""

LUHMANN_DISCLAIMER: str = (
    "mathematische Fassung im Sinne dynamischer Mitführung, KEINE "
    "Luhmann-Soziologie, KEINE Gleichsetzung."
)


@dataclass(frozen=True)
class LinearDriveResponseResult:
    """Result of ``linear_drive_response_map(c, k)``.

    Fields
    ------
    phi :
        Formal map coefficient ``φ = c / (k - 1)`` (ansatz ``y = φ·x``).
    cle :
        Conditional Lyapunov exponent ``= -k``.
    map_exists :
        ``True`` when the formal map ``φ`` is defined (always ``True``
        for a successful return; ``k = 1`` raises instead).
    sync_achieved :
        ``True`` iff ``cle < 0`` (i.e. ``k > 0``). Separated from
        ``map_exists`` so a formal map can exist without synchronisation
        (counterexample ``c=4, k=-1``: ``φ=-2`` but ``CLE=+1``).
    c, k :
        Input parameters.
    source :
        Primary citation string.
    bridge_note :
        Verbatim M14 / CLE bridge disclaimer.
    """

    phi: float
    cle: float
    map_exists: bool
    sync_achieved: bool
    c: float
    k: float
    source: str = SOURCE
    bridge_note: str = BRIDGE_NOTE

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def conditional_lyapunov_linear(a: Number) -> float:
    """Conditional Lyapunov exponent for scalar ``δẏ = a · δy``.

    Parameters
    ----------
    a :
        Response variational coefficient. CLE ``= a``. Synchronisation
        holds asymptotically iff ``a < 0``.

    Returns
    -------
    float
        The CLE ``a``.

    Raises
    ------
    ScopeViolationError
        If ``a`` is non-finite.

    Notes
    -----
    Source: Pecora & Carroll 1990 DOI 10.1103/PhysRevLett.64.821.

    See module-level ``BRIDGE_NOTE`` (verbatim M14 / CLE bridge disclaimer).
    """
    a_f = float(a)
    if not (a_f == a_f) or a_f in (float("inf"), float("-inf")):
        raise ScopeViolationError(
            f"conditional_lyapunov_linear: a must be finite; got {a!r}"
        )
    return a_f


def linear_drive_response_map(c: Number, k: Number) -> LinearDriveResponseResult:
    """Linear drive–response map ``φ`` and CLE for ``ẋ=-x``, ``ẏ=-k y + c x``.

    Ansatz ``y = φ · x`` yields the algebraic map

        φ = c / (k - 1)    (requires ``k ≠ 1``)

    and the response variational CLE

        CLE = -k.

    Synchronisation (``sync_achieved``) requires ``CLE < 0``, i.e. ``k > 0``.
    The formal map can exist without synchronisation: e.g. ``c=4, k=-1``
    gives ``φ=-2`` (``map_exists=True``) but ``CLE=+1`` (``sync_achieved=False``).

    Parameters
    ----------
    c :
        Drive→response coupling coefficient.
    k :
        Response decay / gain. Must not equal ``1``.

    Returns
    -------
    LinearDriveResponseResult
        ``phi``, ``cle``, ``map_exists``, ``sync_achieved`` as separate fields.

    Raises
    ------
    ScopeViolationError
        If ``k == 1`` (denominator vanishes) or inputs are non-finite.

    Examples
    --------
    >>> r = linear_drive_response_map(4, 3)
    >>> (r.phi, r.cle, r.map_exists, r.sync_achieved)
    (2.0, -3.0, True, True)
    >>> r = linear_drive_response_map(4, -1)
    >>> (r.phi, r.cle, r.map_exists, r.sync_achieved)
    (-2.0, 1.0, True, False)

    Notes
    -----
    Source: Pecora & Carroll 1990 DOI 10.1103/PhysRevLett.64.821.

    Hand check for ``c=4, k=3`` (``φ=2``):
    ``d(y-2x)/dt = ẏ - 2ẋ = (-3y+4x) - 2(-x) = -3(y-2x)`` —
    exponential decay at rate 3.

    See module-level ``BRIDGE_NOTE`` (verbatim M14 / CLE bridge disclaimer).
    """
    c_f = float(c)
    k_f = float(k)
    if not (c_f == c_f) or c_f in (float("inf"), float("-inf")):
        raise ScopeViolationError(
            f"linear_drive_response_map: c must be finite; got {c!r}"
        )
    if not (k_f == k_f) or k_f in (float("inf"), float("-inf")):
        raise ScopeViolationError(
            f"linear_drive_response_map: k must be finite; got {k!r}"
        )
    if k_f == 1.0:
        raise ScopeViolationError(
            "linear_drive_response_map: k=1 makes φ = c/(k-1) undefined "
            "(denominator vanishes); outside scope of the linear map formula"
        )
    phi = c_f / (k_f - 1.0)
    cle = -k_f
    return LinearDriveResponseResult(
        phi=phi,
        cle=cle,
        map_exists=True,
        sync_achieved=(cle < 0.0),
        c=c_f,
        k=k_f,
        bridge_note=BRIDGE_NOTE,
    )


def sync_criterion_cle_negative(cle: Number) -> bool:
    """Return ``True`` iff the conditional Lyapunov exponent is strictly negative."""
    cle_f = float(cle)
    if not (cle_f == cle_f) or cle_f in (float("inf"), float("-inf")):
        raise ScopeViolationError(
            f"sync_criterion_cle_negative: cle must be finite; got {cle!r}"
        )
    return cle_f < 0.0


__all__ = [
    "BRIDGE_NOTE",
    "DOI",
    "LUHMANN_DISCLAIMER",
    "SOURCE",
    "LinearDriveResponseResult",
    "conditional_lyapunov_linear",
    "linear_drive_response_map",
    "sync_criterion_cle_negative",
]
