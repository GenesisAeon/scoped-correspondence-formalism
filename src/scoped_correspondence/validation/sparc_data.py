"""Reproducible SPARC data adapter (G4).

Content basis: `SCF_GALAXY_DYNAMICS_IMPLEMENTATION_PLAN.md` §9 and
`docs/sparc_data_provenance.md`.

The raw SPARC files (`SPARC_Lelli2016c.mrt`, `MassModels_Lelli2016c.mrt`)
are deliberately NOT part of this repository -- their redistribution
rights are unresolved (`docs/sparc_data_provenance.md`). This module only
contains parsing/combination logic; it never embeds or ships any SPARC
content itself.

The COMPONENT table (`MassModels_Lelli2016c.mrt`) is parsed with FIXED
byte ranges (1-indexed, inclusive), confirmed byte-for-byte against its
own live header, which matches `SCF_GALAXY_DYNAMICS_IMPLEMENTATION_PLAN.md`
§9.2 exactly (Plan §9.2: "nicht auf zufällige Whitespace-Zerlegung
vertrauen" -- an empty/blank field inside a fixed column would silently
shift every later field under a naive split-based parser).

The METADATA table (`SPARC_Lelli2016c.mrt`) is parsed differently, for a
concrete, verified reason: its OWN printed byte-by-byte header does NOT
match its own live-served data (discovered 2026-09-26, see
`docs/sparc_data_provenance.md`) -- the header states byte 12-13 for the
Hubble-type field `T`, but every one of the 175 real data rows has `T`'s
digits at bytes 13-14 instead, and the header's stated final byte (113)
does not match the real line length (131). Rather than hardcode a
byte map already shown to be wrong for this file, the metadata table is
parsed via STRICT whitespace tokenization, validated to require exactly
19 fields per row -- empirically confirmed against all 175 real rows
before this choice was made, not assumed. A row with any other token
count raises immediately rather than silently misaligning fields; if a
future SPARC data release ever omits a field for some galaxy (turning it
genuinely blank), this validation is exactly what would catch it.

Lines are split with `str.splitlines()`, which handles both `\n` and the
component table's actual `\r\n` terminators correctly (Plan §9.1's own
"CRLF/LF-Fehler nicht wiederholen" warning, confirmed CRLF via `od -c`
during G4, see `docs/sparc_data_provenance.md`).
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Sequence, Tuple


# ---------------------------------------------------------------------------
# Metadata table (SPARC_Lelli2016c.mrt): parsed by validated whitespace
# tokenization, NOT byte ranges -- see the module docstring for why. Order
# confirmed against the table's own real header (field semantics only,
# not byte positions, which are demonstrably unreliable for this file).
_METADATA_TOKEN_ORDER: List[str] = [
    "galaxy", "T", "D_mpc", "e_D_mpc", "f_D", "inc_deg", "e_inc_deg",
    "L36_1e9_sollum", "e_L36_1e9_sollum", "Reff_kpc", "SBeff_sollum_pc2",
    "Rdisk_kpc", "SBdisk_sollum_pc2", "MHI_1e9_solmass", "RHI_kpc",
    "Vflat_kms", "e_Vflat_kms", "Q", "ref",
]

# Component table (MassModels_Lelli2016c.mrt) -- byte ranges confirmed to
# match SCF_GALAXY_DYNAMICS_IMPLEMENTATION_PLAN.md §9.2 exactly against
# the table's own real header (docs/sparc_data_provenance.md).
_COMPONENT_FIELDS: List[Tuple[str, int, int]] = [
    ("galaxy", 1, 11),
    ("D_mpc", 13, 18),
    ("R_kpc", 20, 25),
    ("Vobs_kms", 27, 32),
    ("e_Vobs_kms", 34, 38),
    ("Vgas_kms", 40, 45),
    ("Vdisk_kms", 47, 52),
    ("Vbul_kms", 54, 59),
    ("SBdisk_sollum_pc2", 61, 67),
    ("SBbul_sollum_pc2", 69, 76),
]


def _slice_fields(line: str, fields: Sequence[Tuple[str, int, int]]) -> dict:
    """Extract each (name, start_1based, end_1based_inclusive) as a raw
    stripped string; raises if the line is too short for the declared schema."""
    max_end = max(end for _, _start, end in fields)
    if len(line) < max_end:
        raise ValueError(f"line too short for the declared byte schema: "
                          f"need >= {max_end} chars, got {len(line)}: {line!r}")
    return {name: line[start - 1:end].strip() for name, start, end in fields}


@dataclass(frozen=True)
class SparcMetadataRow:
    galaxy: str
    T: int
    D_mpc: float
    e_D_mpc: float
    f_D: int
    inc_deg: float
    e_inc_deg: float
    L36_1e9_sollum: float
    e_L36_1e9_sollum: float
    Reff_kpc: float
    SBeff_sollum_pc2: float
    Rdisk_kpc: float
    SBdisk_sollum_pc2: float
    MHI_1e9_solmass: float
    RHI_kpc: float
    Vflat_kms: float
    e_Vflat_kms: float
    Q: int
    ref: str


@dataclass(frozen=True)
class SparcComponentRow:
    galaxy: str
    D_mpc: float
    R_kpc: float
    Vobs_kms: float
    e_Vobs_kms: float
    Vgas_kms: float
    Vdisk_kms: float
    Vbul_kms: float
    SBdisk_sollum_pc2: float
    SBbul_sollum_pc2: float


def parse_metadata_line(line: str) -> SparcMetadataRow:
    tokens = line.split()
    if len(tokens) != len(_METADATA_TOKEN_ORDER):
        raise ValueError(
            f"expected {len(_METADATA_TOKEN_ORDER)} whitespace-separated metadata "
            f"fields, got {len(tokens)}: {line!r}"
        )
    f = dict(zip(_METADATA_TOKEN_ORDER, tokens))
    return SparcMetadataRow(
        galaxy=f["galaxy"],
        T=int(f["T"]),
        D_mpc=float(f["D_mpc"]),
        e_D_mpc=float(f["e_D_mpc"]),
        f_D=int(f["f_D"]),
        inc_deg=float(f["inc_deg"]),
        e_inc_deg=float(f["e_inc_deg"]),
        L36_1e9_sollum=float(f["L36_1e9_sollum"]),
        e_L36_1e9_sollum=float(f["e_L36_1e9_sollum"]),
        Reff_kpc=float(f["Reff_kpc"]),
        SBeff_sollum_pc2=float(f["SBeff_sollum_pc2"]),
        Rdisk_kpc=float(f["Rdisk_kpc"]),
        SBdisk_sollum_pc2=float(f["SBdisk_sollum_pc2"]),
        MHI_1e9_solmass=float(f["MHI_1e9_solmass"]),
        RHI_kpc=float(f["RHI_kpc"]),
        Vflat_kms=float(f["Vflat_kms"]),
        e_Vflat_kms=float(f["e_Vflat_kms"]),
        Q=int(f["Q"]),
        ref=f["ref"],
    )


def parse_component_line(line: str) -> SparcComponentRow:
    f = _slice_fields(line, _COMPONENT_FIELDS)
    return SparcComponentRow(
        galaxy=f["galaxy"],
        D_mpc=float(f["D_mpc"]),
        R_kpc=float(f["R_kpc"]),
        Vobs_kms=float(f["Vobs_kms"]),
        e_Vobs_kms=float(f["e_Vobs_kms"]),
        Vgas_kms=float(f["Vgas_kms"]),
        Vdisk_kms=float(f["Vdisk_kms"]),
        Vbul_kms=float(f["Vbul_kms"]),
        SBdisk_sollum_pc2=float(f["SBdisk_sollum_pc2"]),
        SBbul_sollum_pc2=float(f["SBbul_sollum_pc2"]),
    )


def _data_section(text: str) -> List[str]:
    """Return only the data lines: everything AFTER the LAST line of 10+
    dashes. CDS/Vizier .mrt files (both SPARC tables) end their
    byte-by-byte-description/notes header with exactly such a separator
    line immediately before the first data row -- this is the standard
    machine-readable-table convention, not specific to one table's
    wording, so it is far more robust than matching header text like
    "Title:"/"Note" (which would break on a differently worded header,
    e.g. a continuation line with no recognizable prefix at all).
    Raises if no such separator is found, rather than silently treating
    header text as data."""
    lines = text.splitlines()
    last_sep = None
    for i, ln in enumerate(lines):
        if len(ln) >= 10 and set(ln) == {"-"}:
            last_sep = i
    if last_sep is None:
        raise ValueError("no '---' header/data separator line found -- unexpected file format")
    return [ln for ln in lines[last_sep + 1:] if ln.strip()]


def parse_metadata_table(text: str) -> List[SparcMetadataRow]:
    """Parse the full metadata table text into rows, validating along the way.

    Raises on: non-unique galaxy names, non-finite numeric fields.
    """
    rows = [parse_metadata_line(ln) for ln in _data_section(text)]
    names = [r.galaxy for r in rows]
    if len(names) != len(set(names)):
        dupes = sorted({n for n in names if names.count(n) > 1})
        raise ValueError(f"duplicate galaxy names in metadata table: {dupes}")
    for r in rows:
        for field_name in ("D_mpc", "e_D_mpc", "inc_deg", "e_inc_deg", "Vflat_kms"):
            v = getattr(r, field_name)
            if not math.isfinite(v):
                raise ValueError(f"non-finite {field_name} for galaxy {r.galaxy}: {v}")
    return rows


def parse_component_table(text: str) -> List[SparcComponentRow]:
    """Parse the full component table text into rows, validating along the way.

    Raises on: non-finite numeric fields, non-positive radii, non-positive
    reported velocity errors, duplicate radii within the same galaxy.
    """
    rows = [parse_component_line(ln) for ln in _data_section(text)]
    by_galaxy: dict = {}
    for r in rows:
        for field_name in ("R_kpc", "Vobs_kms", "e_Vobs_kms", "Vgas_kms", "Vdisk_kms", "Vbul_kms"):
            v = getattr(r, field_name)
            if not math.isfinite(v):
                raise ValueError(f"non-finite {field_name} for galaxy {r.galaxy}: {v}")
        if r.R_kpc <= 0:
            raise ValueError(f"non-positive radius for galaxy {r.galaxy}: {r.R_kpc}")
        if r.e_Vobs_kms <= 0:
            raise ValueError(f"non-positive e_Vobs for galaxy {r.galaxy}: {r.e_Vobs_kms}")
        by_galaxy.setdefault(r.galaxy, []).append(r.R_kpc)
    for galaxy, radii in by_galaxy.items():
        if len(radii) != len(set(radii)):
            raise ValueError(f"duplicate radii within galaxy {galaxy}: {sorted(radii)}")
    return rows


# ---------------------------------------------------------------------------
def combine_baryonic_v2(v_gas: float, v_disk: float, v_bul: float,
                         upsilon_d: float = 0.5, upsilon_b: float = 0.7) -> float:
    """v_bar^2 [km^2/s^2] combining SPARC's signed component velocities
    correctly (Plan §9.3): SPARC encodes outward-directed component
    acceleration via a NEGATIVE component velocity, so each term must be
    ``|v|*v``, never a plain square -- squaring everything would silently
    discard this sign convention. `upsilon_d`/`upsilon_b` are external
    M/L-ratio model assumptions (Plan §9.3's first transparent baseline:
    0.5 and 0.7), not measured constants.
    """
    return (abs(v_gas) * v_gas
            + upsilon_d * abs(v_disk) * v_disk
            + upsilon_b * abs(v_bul) * v_bul)


def scale_distance(r_ref_kpc: float, v_component_ref_kms: float, alpha_D: float) -> Tuple[float, float]:
    """Distance-rescaling of a radius and a velocity-squared component
    contribution (Plan §9.4): `r = alpha_D*r_ref`, `v^2 = alpha_D*v_ref^2`
    for fixed angular profile. Returns `(r, v_component)` with the
    velocity re-derived from its rescaled square (sign preserved)."""
    r = alpha_D * r_ref_kpc
    v2_ref = v_component_ref_kms * abs(v_component_ref_kms)
    v2 = alpha_D * v2_ref
    v = math.copysign(math.sqrt(abs(v2)), v2)
    return r, v


def scale_inclination(v_obs_ref_kms: float, e_vobs_ref_kms: float,
                       i_ref_deg: float, i_deg: float) -> Tuple[float, float]:
    """Inclination-rescaling (Plan §9.4): `v_obs(i) = v_obs_ref *
    sin(i_ref)/sin(i)`, with the tabulated velocity error scaled by the
    same factor. Angles are converted to radians exactly once internally."""
    i_ref = math.radians(i_ref_deg)
    i = math.radians(i_deg)
    factor = math.sin(i_ref) / math.sin(i)
    return v_obs_ref_kms * factor, e_vobs_ref_kms * factor
