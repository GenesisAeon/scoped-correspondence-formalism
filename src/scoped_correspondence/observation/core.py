"""Observation formulas: K_info, R_info, eta_info (FORMALISM.md §2–§3)."""

from __future__ import annotations

import math
from typing import Optional

from scoped_correspondence.errors import ScopeViolationError

# Canonical unit tags accepted as "rate" (bits or nats per time).
_RATE_UNIT_ALIASES = {
    "bit/time",
    "bits/time",
    "bit/s",
    "bits/s",
    "bit/sec",
    "bits/sec",
    "bit/second",
    "bits/second",
    "nat/time",
    "nats/time",
    "nat/s",
    "nats/s",
}

# Tags that mean absolute information (no time) — not valid for eta_info alone.
_ABS_INFO_ALIASES = {
    "bit",
    "bits",
    "nat",
    "nats",
}


def _norm_unit(unit: str) -> str:
    return unit.strip().lower().replace(" ", "")


def channel_capacity(bandwidth: float, snr: float) -> float:
    """Shannon–Hartley capacity K_info = B * log2(1 + P/N).

    Maps to FORMALISM.md §2 row ``K_info`` (Bit/Zeit; concrete channel model)
    and information_layer_crep.md §3 (band-limited AWGN).

    Parameters
    ----------
    bandwidth:
        Bandwidth B in Hz (1/time).
    snr:
        Signal-to-noise ratio P/N (dimensionless, power ratio).

    Returns
    -------
    K_info in bit/time (same time unit as 1/B).
    """
    if bandwidth < 0:
        raise ScopeViolationError(
            "channel_capacity: bandwidth B must be >= 0 (Hz); "
            f"got {bandwidth!r}"
        )
    if snr < 0:
        raise ScopeViolationError(
            "channel_capacity: snr = P/N must be >= 0; "
            f"got {snr!r}"
        )
    return float(bandwidth * math.log2(1.0 + snr))


def retention(
    mutual_information: float,
    entropy: float,
    *,
    discrete: bool = True,
) -> float:
    """Discrete information retention R_info = I(X;X') / H(X).

    Maps to FORMALISM.md §2 row ``R_info`` and §3 / information_layer_crep.md §4.

    The bound ``0 <= R_info <= 1`` is guaranteed only for discrete X with
    ``0 < H(X) < inf``. Otherwise raises ``ScopeViolationError`` — never
    silently returns a value (differential entropy must not replace H unchecked).
    """
    if not discrete:
        raise ScopeViolationError(
            "retention: R_info = I/H is only defined here for discrete X; "
            "for continuous variables do not substitute differential entropy "
            "(FORMALISM.md §3). Set discrete=True only when X is discrete."
        )
    if not (0.0 < float(entropy) < math.inf):
        raise ScopeViolationError(
            "retention: requires 0 < H(X) < inf for discrete X; "
            f"got H={entropy!r} (FORMALISM.md §2 R_info / §3)"
        )
    # Audit finding: NaN mutual_information passes `< -1e-15` (always False
    # for NaN) and the later [0,1] bound check (also always False for NaN),
    # then max(0.0, min(1.0, nan)) silently returns 1.0 because Python's
    # min/max never replace on a NaN comparison. Reject non-finite input
    # explicitly before any comparison-based check can be skipped this way.
    if not math.isfinite(mutual_information):
        raise ScopeViolationError(
            f"retention: mutual_information must be finite; got {mutual_information!r}"
        )
    if mutual_information < -1e-15:
        raise ScopeViolationError(
            f"retention: mutual information I must be >= 0; got {mutual_information!r}"
        )
    r = float(mutual_information) / float(entropy)
    # Numerical slack for floating point; domain still requires I <= H.
    if r < -1e-12 or r > 1.0 + 1e-12:
        raise ScopeViolationError(
            f"retention: R_info={r!r} outside [0,1]; check I <= H for discrete X"
        )
    return max(0.0, min(1.0, r))


def realized_rate(
    rate: float,
    capacity: float,
    *,
    rate_unit: str = "bit/time",
    capacity_unit: str = "bit/time",
) -> float:
    """Realized information efficiency eta_info = mathcal_I / K_info.

    Maps to FORMALISM.md §2 row ``eta_info`` and §3 / information_layer_crep.md §5.

    Both ``rate`` and ``capacity`` must be rates (information / time) in the
    *same* time unit. Passing absolute bit amounts (no time) raises
    ``ScopeViolationError`` — that quotient would have dimension time
    (see FORMALISM.md §3 / c06_information_window).
    """
    ru = _norm_unit(rate_unit)
    cu = _norm_unit(capacity_unit)

    if ru in _ABS_INFO_ALIASES or cu in _ABS_INFO_ALIASES:
        raise ScopeViolationError(
            "realized_rate: rate and capacity must be information *rates* "
            "(bit/time), not absolute bit amounts; I/K without time is a "
            "duration (FORMALISM.md §3, c06_information_window)"
        )
    if ru not in _RATE_UNIT_ALIASES or cu not in _RATE_UNIT_ALIASES:
        raise ScopeViolationError(
            "realized_rate: unrecognized unit tag(s); expected bit/time-style "
            f"labels, got rate_unit={rate_unit!r}, capacity_unit={capacity_unit!r}"
        )
    # Same physical rate class: bit vs nat must match; time base is symbolic.
    rate_kind = "nat" if ru.startswith("nat") else "bit"
    cap_kind = "nat" if cu.startswith("nat") else "bit"
    if rate_kind != cap_kind:
        raise ScopeViolationError(
            "realized_rate: rate and capacity must use the same information "
            f"unit (bit vs nat); got {rate_unit!r} vs {capacity_unit!r}"
        )
    if float(capacity) <= 0.0:
        raise ScopeViolationError(
            "realized_rate: K_info must be > 0; utilization undefined at "
            f"capacity {capacity!r} (information_layer_crep.md §5)"
        )
    eta = float(rate) / float(capacity)
    if eta < -1e-12:
        raise ScopeViolationError(
            f"realized_rate: eta_info={eta!r} is negative"
        )
    # Audit finding: rate > capacity (eta_info > 1) passed through silently.
    # K_info is defined as the channel's maximum achievable rate (FORMALISM.md
    # §3, c06_information_window); a realized rate above it is a contradiction
    # of that definition (e.g. a measurement/unit error), not a valid
    # over-100%-utilization reading, so it must be flagged rather than
    # returned as an "eta_info" outside its defined [0,1] range.
    if eta > 1.0 + 1e-9:
        raise ScopeViolationError(
            f"realized_rate: eta_info={eta!r} > 1 means rate exceeds capacity "
            f"K_info={capacity!r}; check units/definition of capacity "
            "(information_layer_crep.md §5)"
        )
    return float(eta)


__all__ = ["channel_capacity", "retention", "realized_rate"]
