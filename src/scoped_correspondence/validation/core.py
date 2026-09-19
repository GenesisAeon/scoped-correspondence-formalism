"""Cygnus X-1 jet PA validation pilot (Milestone 6).

Protocol (immutable before any fit — Johann-fixed):
  - Macro: jet_pa_deg only
  - Split: calib = indices 0..8 (2006.2–2015.2), holdout = 9..17 (2016.1–2023.8)
  - Baseline: persistence = last calib jet_pa_deg constant on holdout
  - Metric: RMSE on 9 holdout epochs
  - Free params (pa_eq, r) estimated ONLY on calib; no Γ_jet / σ reuse

Relaxation model:
  pa(t) = pa_eq + (pa0 - pa_eq) * exp(-r * (t - t_ref))
with t_ref = first calib year, pa0 = first calib jet_pa_deg (fixed, not free).

Recovery rate linkage: fitted r > 0 maps to tau = 1/r via
``dynamics.recovery_rate_from_relaxation(tau)`` (= r). Cubic
``recovery_rate_at_equilibrium`` is not the PA ODE; it is not used for the
fit (documented; YAGNI — only call helpers where the formula fits).
"""

from __future__ import annotations

import math
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

import numpy as np

from scoped_correspondence.dynamics import recovery_rate_from_relaxation
from scoped_correspondence.errors import ScopeViolationError

# --- Fixed protocol (locked in DatasetManifest BEFORE fit) -----------------

CALIB_INDICES: Tuple[int, ...] = tuple(range(0, 9))  # 2006.2–2015.2
HOLDOUT_INDICES: Tuple[int, ...] = tuple(range(9, 18))  # 2016.1–2023.8
MACRO_NAME = "jet_pa_deg"
MACRO_UNIT = "deg"
N_EPOCHS_EXPECTED = 18
DOMAIN_NAME = "cygnus-jet-utac"
CITATIONS = (
    "Stirling et al. 2001",
    "Rushton et al. 2011",
    "Miller-Jones et al. 2021",
    "Prabu et al. 2026",
)
SOURCE_RELATIVE = "data/cygnus_x1_radio_epochs.yaml"
SOURCE_PACKAGE = "GenesisAeon/cygnus-jet-utac"
# Macro unit is degrees (position angle). Declared search domain for pa_eq.


@dataclass(frozen=True)
class Epoch:
    """One VLBI epoch row (year, jet_pa_deg required; mjd optional)."""

    year: float
    jet_pa_deg: float
    mjd: Optional[float] = None
    jet_flux_mJy: Optional[float] = None
    notes: str = ""


@dataclass(frozen=True)
class DatasetManifest:
    """YAGNI typed manifest for this Cygnus PA pilot only."""

    source_path: str
    source_package: str
    citations: Tuple[str, ...]
    macro: str
    macro_unit: str
    n_epochs: int
    calib_indices: Tuple[int, ...]
    holdout_indices: Tuple[int, ...]
    exclusions: Tuple[str, ...] = ()
    license_note: str = (
        "Literature-compiled VLBI epochs; cite Stirling 2001, Rushton 2011, "
        "Miller-Jones 2021, Prabu 2026 as in YAML header. Copied 1:1 from "
        "cygnus-jet-utac; numbers not invented."
    )
    circularity_note: str = (
        "Do NOT reuse cygnus-jet-utac σ / Γ_jet / efficiency. Free parameters "
        "(pa_eq, r) are estimated only on calib epochs. Prior Γ_jet inversion "
        "from fixed efficiency (worked_example_cygnus_jet_utac.md) is excluded."
    )

    def __post_init__(self) -> None:
        # Audit finding A09: the manifest itself accepted overlapping or
        # duplicated calib/holdout indices (split_epochs only checks that
        # the CALLER's indices match the manifest's, not that the manifest
        # is internally sound) -- a manifest built with
        # holdout_indices=calib_indices passed silently, and split_epochs
        # then returned identical calib/holdout epoch lists (a leak). The
        # canonical Cygnus manifest already uses disjoint fixed indices;
        # this hardens the contract for any manifest, not just that one.
        calib = tuple(self.calib_indices)
        holdout = tuple(self.holdout_indices)
        if len(set(calib)) != len(calib):
            raise ScopeViolationError(
                f"DatasetManifest: calib_indices has duplicates: {calib!r}"
            )
        if len(set(holdout)) != len(holdout):
            raise ScopeViolationError(
                f"DatasetManifest: holdout_indices has duplicates: {holdout!r}"
            )
        overlap = set(calib) & set(holdout)
        if overlap:
            raise ScopeViolationError(
                "DatasetManifest: calib_indices and holdout_indices must be "
                f"disjoint (anti data-snooping); overlap={sorted(overlap)!r}"
            )
        for idx in (*calib, *holdout):
            if not (0 <= idx < self.n_epochs):
                raise ScopeViolationError(
                    f"DatasetManifest: index {idx!r} out of range "
                    f"[0, {self.n_epochs})"
                )

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["citations"] = list(self.citations)
        d["calib_indices"] = list(self.calib_indices)
        d["holdout_indices"] = list(self.holdout_indices)
        d["exclusions"] = list(self.exclusions)
        return d


def cygnus_pa_manifest(source_path: str | Path) -> DatasetManifest:
    """Build the locked Cygnus PA manifest (split fixed before any fit)."""
    return DatasetManifest(
        source_path=str(source_path),
        source_package=SOURCE_PACKAGE,
        citations=CITATIONS,
        macro=MACRO_NAME,
        macro_unit=MACRO_UNIT,
        n_epochs=N_EPOCHS_EXPECTED,
        calib_indices=CALIB_INDICES,
        holdout_indices=HOLDOUT_INDICES,
        exclusions=(),
    )


@dataclass(frozen=True)
class FittedRelaxation:
    """Calib-only least-squares fit of PA relaxation."""

    pa_eq: float
    r: float
    t_ref: float
    pa0: float
    tau: Optional[float]
    s_rec_from_dynamics: Optional[float]
    n_calib: int
    note: str = "fitted_parameters estimated exclusively on calibration epochs"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ValidationReport:
    domain: str
    macro: str
    split: Dict[str, Any]
    model_rmse_holdout: float
    baseline_rmse_holdout: float
    model_beats_baseline: bool
    fitted_parameters: Dict[str, Any]
    source_citation: str
    baseline_value: float
    n_holdout: int
    notes: Tuple[str, ...] = ()

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["notes"] = list(self.notes)
        return d


# --- Minimal YAML loader for this one file (stdlib; no PyYAML required) ----

_EPOCH_KEY_RE = re.compile(
    r"^\s*(year|mjd|jet_pa_deg|jet_flux_mJy|notes)\s*:\s*(.*)$"
)


def _parse_scalar(raw: str) -> Any:
    s = raw.strip()
    if s.startswith('"') and s.endswith('"'):
        return s[1:-1]
    if s.startswith("'") and s.endswith("'"):
        return s[1:-1]
    if s == "" or s.lower() in {"null", "~"}:
        return None
    try:
        if "." in s or "e" in s.lower():
            return float(s)
        return int(s)
    except ValueError:
        return s


def load_cygnus_epochs(path: str | Path) -> List[Epoch]:
    """Load epochs from ``cygnus_x1_radio_epochs.yaml`` (structure-specific)."""
    text = Path(path).read_text(encoding="utf-8")
    epochs: List[Epoch] = []
    in_epochs = False
    current: Dict[str, Any] = {}

    def flush() -> None:
        nonlocal current
        if not current:
            return
        if "year" not in current or "jet_pa_deg" not in current:
            raise ValueError(f"incomplete epoch row: {current!r}")
        epochs.append(
            Epoch(
                year=float(current["year"]),
                jet_pa_deg=float(current["jet_pa_deg"]),
                mjd=float(current["mjd"]) if current.get("mjd") is not None else None,
                jet_flux_mJy=(
                    float(current["jet_flux_mJy"])
                    if current.get("jet_flux_mJy") is not None
                    else None
                ),
                notes=str(current.get("notes") or ""),
            )
        )
        current = {}

    for line in text.splitlines():
        if line.startswith("#"):
            continue
        stripped = line.strip()
        if stripped == "epochs:":
            in_epochs = True
            continue
        if not in_epochs:
            continue
        # end of epochs list when a top-level key appears (no indent)
        if stripped and not line.startswith(" ") and not line.startswith("\t"):
            if stripped.endswith(":") and not stripped.startswith("-"):
                flush()
                break
        if stripped.startswith("- "):
            flush()
            rest = stripped[2:]
            m = _EPOCH_KEY_RE.match("  " + rest) if ":" in rest else None
            if m:
                current[m.group(1)] = _parse_scalar(m.group(2))
            continue
        m = _EPOCH_KEY_RE.match(line)
        if m:
            current[m.group(1)] = _parse_scalar(m.group(2))
    flush()
    if len(epochs) != N_EPOCHS_EXPECTED:
        raise ValueError(
            f"expected {N_EPOCHS_EXPECTED} epochs, got {len(epochs)} from {path}"
        )
    return epochs


def split_epochs(
    epochs: Sequence[Epoch],
    manifest: DatasetManifest,
    *,
    calib_indices: Optional[Sequence[int]] = None,
    holdout_indices: Optional[Sequence[int]] = None,
) -> Tuple[List[Epoch], List[Epoch]]:
    """Split by manifest indices; refuse any other index set (anti data-snooping)."""
    req_c = tuple(manifest.calib_indices)
    req_h = tuple(manifest.holdout_indices)
    use_c = tuple(calib_indices) if calib_indices is not None else req_c
    use_h = tuple(holdout_indices) if holdout_indices is not None else req_h
    if use_c != req_c or use_h != req_h:
        raise ScopeViolationError(
            "split_epochs: requested indices differ from DatasetManifest "
            f"(anti data-snooping). requested calib={use_c} holdout={use_h}; "
            f"manifest calib={req_c} holdout={req_h}"
        )
    if len(epochs) != manifest.n_epochs:
        raise ScopeViolationError(
            f"split_epochs: n_epochs={len(epochs)} != manifest.n_epochs={manifest.n_epochs}"
        )
    calib = [epochs[i] for i in req_c]
    holdout = [epochs[i] for i in req_h]
    return calib, holdout


def persistence_baseline(calibration_pa: Sequence[float]) -> float:
    """Last calibration jet_pa_deg, held constant on all holdout epochs."""
    if len(calibration_pa) == 0:
        raise ScopeViolationError("persistence_baseline: empty calibration_pa")
    return float(calibration_pa[-1])


def predict_relaxation_pa(
    t: float,
    *,
    pa_eq: float,
    r: float,
    t_ref: float,
    pa0: float,
) -> float:
    """pa(t) = pa_eq + (pa0 - pa_eq) * exp(-r * (t - t_ref))."""
    return float(pa_eq + (pa0 - pa_eq) * math.exp(-r * (t - t_ref)))


def _pa_eq_given_r(
    times: np.ndarray,
    pas: np.ndarray,
    *,
    r: float,
    t_ref: float,
    pa0: float,
) -> float:
    """Closed-form least-squares pa_eq for fixed r (linear in pa_eq)."""
    e = np.exp(-r * (times - t_ref))
    # y = pa_eq*(1-e) + pa0*e  =>  y - pa0*e = pa_eq*(1-e)
    a = 1.0 - e
    b = pas - pa0 * e
    # Prefer rows with |a| large enough; if all a~0 (r=0), pa_eq free -> mean
    if float(np.max(np.abs(a))) < 1e-15:
        return float(np.mean(pas))
    # least squares: pa_eq = (a·b) / (a·a)
    return float(np.dot(a, b) / np.dot(a, a))


def _sse(times: np.ndarray, pas: np.ndarray, pa_eq: float, r: float, t_ref: float, pa0: float) -> float:
    pred = pa_eq + (pa0 - pa_eq) * np.exp(-r * (times - t_ref))
    err = pas - pred
    return float(np.dot(err, err))


def fit_relaxation_pa(calib: Sequence[Epoch]) -> FittedRelaxation:
    """Least-squares fit of (pa_eq, r) on calib only.

    Holdout must not be passed here. ``t_ref`` / ``pa0`` fixed from first calib
    epoch. Search r >= 0 (relaxation / recovery_rate_from_relaxation); pa_eq
    unrestricted (closed-form given r). Small r with large |pa_eq| can indicate
    a near-linear drift that is only weakly identified as relaxation — reported
    honestly.
    """
    if len(calib) < 2:
        raise ScopeViolationError("fit_relaxation_pa: need >= 2 calib epochs")
    times = np.asarray([e.year for e in calib], dtype=float)
    pas = np.asarray([e.jet_pa_deg for e in calib], dtype=float)
    t_ref = float(times[0])
    pa0 = float(pas[0])

    best_r = 0.0
    best_pa_eq = float(np.mean(pas))
    best_sse = _sse(times, pas, best_pa_eq, best_r, t_ref, pa0)

    for r in np.concatenate(
        [np.linspace(0.0, 2.0, 4001), np.linspace(2.0, 50.0, 481)]
    ):
        r = float(r)
        pa_eq = _pa_eq_given_r(times, pas, r=r, t_ref=t_ref, pa0=pa0)
        sse = _sse(times, pas, pa_eq, r, t_ref, pa0)
        if sse < best_sse:
            best_sse = sse
            best_r = r
            best_pa_eq = float(pa_eq)

    span = max(1e-4, best_r * 0.5 + 1e-4)
    for r in np.linspace(max(0.0, best_r - span), best_r + span, 4001):
        r = float(r)
        pa_eq = _pa_eq_given_r(times, pas, r=r, t_ref=t_ref, pa0=pa0)
        sse = _sse(times, pas, pa_eq, r, t_ref, pa0)
        if sse < best_sse:
            best_sse = sse
            best_r = r
            best_pa_eq = float(pa_eq)

    tau: Optional[float] = None
    s_rec: Optional[float] = None
    if best_r > 0.0:
        tau = float(1.0 / best_r)
        s_rec = float(recovery_rate_from_relaxation(tau))
        if abs(s_rec - best_r) > 1e-12:
            raise RuntimeError("internal: S_rec != r after recovery_rate_from_relaxation")

    return FittedRelaxation(
        pa_eq=best_pa_eq,
        r=best_r,
        t_ref=t_ref,
        pa0=pa0,
        tau=tau,
        s_rec_from_dynamics=s_rec,
        n_calib=len(calib),
    )


def rmse(observed: Sequence[float], predicted: Sequence[float]) -> float:
    if len(observed) != len(predicted) or len(observed) == 0:
        raise ScopeViolationError("rmse: length mismatch or empty")
    o = np.asarray(observed, dtype=float)
    p = np.asarray(predicted, dtype=float)
    return float(np.sqrt(np.mean((o - p) ** 2)))


def run_cygnus_pilot(
    data_path: str | Path,
    *,
    domain: str = DOMAIN_NAME,
) -> Tuple[ValidationReport, DatasetManifest, FittedRelaxation]:
    """Load → lock manifest → split → fit (calib) → baseline → holdout RMSE."""
    path = Path(data_path)
    manifest = cygnus_pa_manifest(path)
    epochs = load_cygnus_epochs(path)
    calib, holdout = split_epochs(epochs, manifest)

    fit = fit_relaxation_pa(calib)  # calib only — holdout not referenced

    calib_pa = [e.jet_pa_deg for e in calib]
    base = persistence_baseline(calib_pa)

    hold_obs = [e.jet_pa_deg for e in holdout]
    hold_years = [e.year for e in holdout]
    model_pred = [
        predict_relaxation_pa(
            t, pa_eq=fit.pa_eq, r=fit.r, t_ref=fit.t_ref, pa0=fit.pa0
        )
        for t in hold_years
    ]
    base_pred = [base] * len(holdout)

    model_rmse = rmse(hold_obs, model_pred)
    baseline_rmse = rmse(hold_obs, base_pred)
    beats = bool(model_rmse < baseline_rmse)

    report = ValidationReport(
        domain=domain,
        macro=manifest.macro,
        split={
            "calib_indices": list(manifest.calib_indices),
            "holdout_indices": list(manifest.holdout_indices),
            "calib_years": [e.year for e in calib],
            "holdout_years": [e.year for e in holdout],
            "rule": "temporal first-9 / last-9; locked in DatasetManifest before fit",
        },
        model_rmse_holdout=model_rmse,
        baseline_rmse_holdout=baseline_rmse,
        model_beats_baseline=beats,
        fitted_parameters=fit.to_dict(),
        source_citation="; ".join(manifest.citations),
        baseline_value=base,
        n_holdout=len(holdout),
        notes=(
            manifest.circularity_note,
            "False model_beats_baseline is a VALID complete result — no retune.",
            "fit_relaxation_pa receives only calib epochs; holdout used solely for RMSE.",
            "recovery_rate_from_relaxation used when r>0 (tau=1/r); "
            "recovery_rate_at_equilibrium not applicable to this PA ODE.",
        ),
    )
    return report, manifest, fit


__all__ = [
    "CALIB_INDICES",
    "HOLDOUT_INDICES",
    "DatasetManifest",
    "Epoch",
    "FittedRelaxation",
    "ValidationReport",
    "cygnus_pa_manifest",
    "fit_relaxation_pa",
    "load_cygnus_epochs",
    "persistence_baseline",
    "predict_relaxation_pa",
    "rmse",
    "run_cygnus_pilot",
    "split_epochs",
]
