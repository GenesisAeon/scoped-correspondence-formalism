"""Free-boundary / one-phase Stefan–Neumann similarity (Milestone 31).

NEW Baustein — not a viability extension. The melt front ``s(t)`` is a
dynamic variable with its own motion law, not a fixed set ``K``.
"""

from scoped_correspondence.free_boundary.core import (
    SOURCE,
    melt_front_position,
    neumann_lambda,
    stefan_number,
    temperature_profile,
)

__all__ = [
    "SOURCE",
    "stefan_number",
    "neumann_lambda",
    "melt_front_position",
    "temperature_profile",
]
