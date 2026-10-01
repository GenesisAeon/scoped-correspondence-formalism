"""H7 (Followup-Review-Fix R8b, SCF_REVIEW_H0_H7_9dde420.md): shared
machine-readable (JSON) and human-readable (Markdown) export for ANY
epistemic report dataclass (`ClaimReport`, `SupportReport`,
`InconsistentCoreReport`, `FiberReport`, `IdentifiedSetReport`,
`ActionSetReport`, `DecisionReport`, `MacroObservabilityReport`,
`InformationModeResult`, ...).

No new proof kernel and no new free-text report language is introduced
here -- this only walks the ALREADY EXISTING dataclass fields (via
`dataclasses.fields`) and renders them, preserving every status axis as
its own row rather than collapsing them. `Fraction` values are
serialized EXACTLY (as a `{numerator, denominator}` object in JSON, and
as an explicit `n/d (exact)` string in Markdown) -- never silently
converted to a lossy float.
"""
from __future__ import annotations

import dataclasses
import json
import math
from fractions import Fraction
from typing import Any, Optional


def _serialize_value(v: Any) -> Any:
    if isinstance(v, Fraction):
        return {"__fraction__": True, "numerator": v.numerator, "denominator": v.denominator}
    if isinstance(v, float) and not math.isfinite(v):
        # Followup-Review-Fix E3 (SCF_REVIEW_J_SERIES_6b3a331): unbounded is a
        # legitimate value and gets an explicit marker; NaN is invalid (unknown
        # belongs in the data model as None), never a bare NaN token or 0.
        if math.isnan(v):
            raise ValueError("report contains NaN: invalid value -- use None for unknown, a marker for unbounded")
        return {"__nonfinite__": "+inf" if v > 0 else "-inf"}
    if dataclasses.is_dataclass(v) and not isinstance(v, type):
        return _serialize_dataclass(v)
    if isinstance(v, (tuple, list)):
        return [_serialize_value(x) for x in v]
    if isinstance(v, dict):
        return {str(k): _serialize_value(val) for k, val in v.items()}
    return v


def _serialize_dataclass(report: Any) -> dict:
    if not dataclasses.is_dataclass(report):
        raise TypeError(f"report_to_json/report_to_markdown require a dataclass instance, got {type(report).__name__}")
    return {"_type": type(report).__name__, **{f.name: _serialize_value(getattr(report, f.name)) for f in dataclasses.fields(report)}}


def report_to_json(report: Any, *, indent: int = 2) -> str:
    """Serialize any epistemic report dataclass to JSON. `Fraction`
    values are serialized as exact `{numerator, denominator}` objects,
    never coerced to a lossy float; everything else falls back to
    `str(...)` only if `json` cannot represent it directly.

    Schema for non-finite floats (Followup-Review-Fix E3, 2026-10-01; the
    output is strict JSON, ``allow_nan=False``): ``+inf``/``-inf`` become
    ``{"__nonfinite__": "+inf" | "-inf"}`` (unbounded); NaN raises
    ``ValueError`` (invalid). Migration: before this fix a NaN/inf float was
    emitted as a bare ``NaN``/``Infinity`` token, which is not valid JSON."""
    return json.dumps(_serialize_dataclass(report), indent=indent, default=str, allow_nan=False)


def _markdown_value(v: Any, depth: int = 0) -> str:
    if isinstance(v, Fraction):
        return f"`{v.numerator}/{v.denominator}` (exact)"
    if dataclasses.is_dataclass(v) and not isinstance(v, type):
        return "; ".join(f"{f.name}={_markdown_value(getattr(v, f.name), depth + 1)}" for f in dataclasses.fields(v))
    if isinstance(v, (tuple, list)):
        if len(v) == 0:
            return "*(empty)*"
        if depth >= 2:
            return f"[{len(v)} item(s)]"
        return "; ".join(_markdown_value(x, depth + 1) for x in v)
    if isinstance(v, dict):
        if len(v) == 0:
            return "*(empty)*"
        return "; ".join(f"{k}={_markdown_value(val, depth + 1)}" for k, val in v.items())
    return str(v)


def report_to_markdown(report: Any, *, title: Optional[str] = None) -> str:
    """A small, generic, human-readable Markdown rendering: one table row
    per declared field, so every status axis (logical status, search
    completeness, evidence kind, empirical status, coverage, ...) stays
    its own visible row -- never summarized into one collapsed line."""
    if not dataclasses.is_dataclass(report):
        raise TypeError(f"report_to_markdown requires a dataclass instance, got {type(report).__name__}")
    name = title or type(report).__name__
    lines = [f"# {name}", "", "| Field | Value |", "|---|---|"]
    for f in dataclasses.fields(report):
        value = getattr(report, f.name)
        lines.append(f"| `{f.name}` | {_markdown_value(value)} |")
    return "\n".join(lines) + "\n"


__all__ = ["report_to_json", "report_to_markdown"]
