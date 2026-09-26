#!/usr/bin/env python3
"""Independent checks for the G4 SPARC data adapter (synthetic fixtures only).

Content basis: `SCF_GALAXY_DYNAMICS_IMPLEMENTATION_PLAN.md` §9 and
`docs/sparc_data_provenance.md`. Purely synthetic, hand-crafted fixture
lines -- no real SPARC file is read here (category "math"; the real-file
check lives in `verify_sparc_real_local.py`, category "data").
"""
from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from scoped_correspondence.validation.sparc_data import (  # noqa: E402
    combine_baryonic_v2,
    parse_component_line,
    parse_component_table,
    parse_metadata_line,
    parse_metadata_table,
    scale_distance,
    scale_inclination,
)


def require(ok, msg):
    if not bool(ok):
        raise AssertionError(msg)


def near(a, b, atol=0.0, rtol=1e-9, msg=""):
    if not np.allclose(a, b, atol=atol, rtol=rtol):
        raise AssertionError(f"{msg}: {a!r} != {b!r} (atol={atol}, rtol={rtol})")


# A hand-crafted component-table line, laid out at the byte positions
# confirmed against the real file (docs/sparc_data_provenance.md):
# 1-11 ID, 13-18 D, 20-25 R, 27-32 Vobs, 34-38 e_Vobs, 40-45 Vgas,
# 47-52 Vdisk, 54-59 Vbul, 61-67 SBdisk, 69-76 SBbul.
_SYNTH_COMPONENT_LINE = (
    "TestGal      3.36   0.16   1.99  1.50   1.86   3.75   0.00   30.32     0.00 "
)

# A hand-crafted metadata-table line: 19 whitespace-separated tokens in
# the confirmed real field order (galaxy, T, D, e_D, f_D, inc, e_inc, L36,
# e_L36, Reff, SBeff, Rdisk, SBdisk, MHI, RHI, Vflat, e_Vflat, Q, ref).
_SYNTH_METADATA_LINE = "TestGal 5 10.00 0.50 2 60.0 5.0 1.000 0.010 2.00 50.00 1.00 40.00 0.500 3.00 100.0 5.0 1 Xy99"


def check_parse_component_line_synthetic():
    row = parse_component_line(_SYNTH_COMPONENT_LINE)
    near(row.D_mpc, 3.36, msg="D_mpc")
    near(row.R_kpc, 0.16, msg="R_kpc")
    near(row.Vobs_kms, 1.99, msg="Vobs_kms")
    near(row.e_Vobs_kms, 1.50, msg="e_Vobs_kms")
    near(row.Vgas_kms, 1.86, msg="Vgas_kms")
    near(row.Vdisk_kms, 3.75, msg="Vdisk_kms")
    near(row.Vbul_kms, 0.00, msg="Vbul_kms")
    near(row.SBdisk_sollum_pc2, 30.32, msg="SBdisk")
    near(row.SBbul_sollum_pc2, 0.00, msg="SBbul")
    require(row.galaxy.strip() == "TestGal", "galaxy name")
    return {"parsed": row.galaxy}


def check_parse_component_line_too_short_raises():
    try:
        parse_component_line("TestGal   1.0")
        raise AssertionError("expected ValueError for a too-short line")
    except ValueError:
        pass
    return {"ok": True}


def check_parse_metadata_line_synthetic():
    row = parse_metadata_line(_SYNTH_METADATA_LINE)
    require(row.galaxy == "TestGal", "galaxy")
    require(row.T == 5, "T")
    near(row.D_mpc, 10.00, msg="D_mpc")
    near(row.inc_deg, 60.0, msg="inc_deg")
    require(row.Q == 1, "Q")
    require(row.ref == "Xy99", "ref")
    return {"parsed": row.galaxy}


def check_parse_metadata_line_wrong_token_count_raises():
    try:
        parse_metadata_line("TestGal 5 10.00 0.50")  # far fewer than 19 tokens
        raise AssertionError("expected ValueError for wrong token count")
    except ValueError:
        pass
    return {"ok": True}


def check_r5_metadata_inf_sbeff_rejected():
    """R5 regression (SCF_REVIEW_G0_G7_5563e67.md): SBeff was previously
    NOT in the finiteness check list, so `inf` passed the parser AND the
    later `SBeff>0` eligibility test (`inf>0` is True, `log10(inf)`
    doesn't raise) -- it would have silently corrupted tercile sorting."""
    tokens = _SYNTH_METADATA_LINE.split()
    tokens[10] = "inf"  # SBeff is the 11th token (0-indexed 10)
    bad_line = " ".join(tokens)
    text = "\n".join(["-" * 20, bad_line])
    try:
        parse_metadata_table(text)
        raise AssertionError("expected ValueError for infinite SBeff")
    except ValueError as e:
        require("SBeff" in str(e), f"expected an SBeff-related error, got: {e}")
    return {"ok": True}


def check_r5_component_nan_distance_rejected():
    """R5 regression: D_mpc was previously NOT in the component table's
    finiteness check list, so `nan` passed silently -- undetectable by
    any downstream cross-table distance consistency check."""
    bad_line = _SYNTH_COMPONENT_LINE[:12] + "   nan" + _SYNTH_COMPONENT_LINE[18:]
    text = "\n".join(["-" * 20, bad_line])
    try:
        parse_component_table(text)
        raise AssertionError("expected ValueError for NaN D_mpc")
    except ValueError as e:
        require("D_mpc" in str(e), f"expected a D_mpc-related error, got: {e}")
    return {"ok": True}


def check_r5_cross_table_distance_mismatch_rejected():
    """R5 regression: a self-constructed, otherwise-valid dataset with
    metadata distance 10 Mpc and component distance 100 Mpc for the same
    galaxy previously passed selection entirely -- no cross-table
    reference-distance check existed."""
    from scoped_correspondence.validation.sparc_data import validate_cross_table_consistency

    meta_text = "\n".join(["-" * 20, _SYNTH_METADATA_LINE])
    meta_rows = parse_metadata_table(meta_text)  # D_mpc = 10.00

    mismatched_component_line = _SYNTH_COMPONENT_LINE[:12] + "100.00" + _SYNTH_COMPONENT_LINE[18:]
    comp_text = "\n".join(["-" * 20, mismatched_component_line])
    comp_rows = parse_component_table(comp_text)  # D_mpc = 100.00

    try:
        validate_cross_table_consistency(meta_rows, comp_rows)
        raise AssertionError("expected ValueError for a 10 vs 100 Mpc cross-table distance mismatch")
    except ValueError as e:
        require("D_mpc mismatch" in str(e), f"expected a D_mpc-mismatch error, got: {e}")
    return {"ok": True}


def check_metadata_table_duplicate_galaxy_raises():
    text = "\n".join(["-" * 20, _SYNTH_METADATA_LINE, _SYNTH_METADATA_LINE])
    try:
        parse_metadata_table(text)
        raise AssertionError("expected ValueError for duplicate galaxy name")
    except ValueError:
        pass
    return {"ok": True}


def check_component_table_duplicate_radius_raises():
    line2 = _SYNTH_COMPONENT_LINE  # identical R_kpc as line 1 -> duplicate within same galaxy
    text = "\n".join(["-" * 20, _SYNTH_COMPONENT_LINE, line2])
    try:
        parse_component_table(text)
        raise AssertionError("expected ValueError for duplicate radius within a galaxy")
    except ValueError as e:
        require("duplicate radii" in str(e), f"expected a duplicate-radius error, got: {e}")
    return {"ok": True}


def check_component_table_non_positive_radius_raises():
    bad_line = "TestGal      3.36   0.00   1.99  1.50   1.86   3.75   0.00   30.32     0.00 "
    text = "\n".join(["-" * 20, bad_line])
    try:
        parse_component_table(text)
        raise AssertionError("expected ValueError for non-positive radius")
    except ValueError as e:
        require("radius" in str(e), f"expected a radius-related error, got: {e}")
    return {"ok": True}


def check_no_separator_found_raises():
    try:
        parse_metadata_table("just some text\nwith no dash separator line\n")
        raise AssertionError("expected ValueError when no '---' separator is present")
    except ValueError:
        pass
    return {"ok": True}


# ---------------------------------------------------------------------------
def check_sign_convention_700_not_900():
    """Plan §9.3's own worked example: v_gas=-10, v_disk=40, v_bul=0,
    Upsilon_d=0.5 -> v_bar^2=700, NOT 900 (which a naive all-squared
    combination would give)."""
    v2 = combine_baryonic_v2(v_gas=-10.0, v_disk=40.0, v_bul=0.0, upsilon_d=0.5, upsilon_b=0.7)
    near(v2, 700.0, rtol=1e-12, msg="v_bar^2")
    naive_wrong = 10.0**2 + 0.5 * 40.0**2  # the WRONG plain-squared combination (drops the sign)
    require(abs(naive_wrong - 900.0) < 1e-9, "sanity: naive wrong combination should be 900")
    require(abs(v2 - naive_wrong) > 100.0, "correct and naive-wrong combinations must differ substantially")
    return {"v_bar_sq": v2, "naive_wrong_would_be": naive_wrong}


def check_distance_scaling_and_g_bar_cancellation():
    """Plan §9.4: r=alpha_D*r_ref, v^2=alpha_D*v_ref^2 for fixed angular
    profile; g_bar=v_bar^2/r is distance-INDEPENDENT at the same angular
    position (the plan's own dimensional-consistency check)."""
    r_ref, v_ref = 5.0, 20.0  # kpc, km/s
    for alpha_D in (0.5, 1.0, 2.0, 3.7):
        r, v = scale_distance(r_ref, v_ref, alpha_D)
        near(r, alpha_D * r_ref, msg=f"r scaling at alpha_D={alpha_D}")
        near(v * abs(v), alpha_D * v_ref * abs(v_ref), msg=f"v^2 scaling at alpha_D={alpha_D}")
        g_bar_ref = (v_ref * abs(v_ref)) / r_ref
        g_bar = (v * abs(v)) / r
        near(g_bar, g_bar_ref, rtol=1e-9, msg=f"g_bar cancellation at alpha_D={alpha_D}")
    return {"ok": True}


def check_inclination_scaling_round_trip():
    """Plan §9.4: v_obs(i)=v_obs_ref*sin(i_ref)/sin(i); scaling to i then
    back to i_ref must recover the original value exactly."""
    v_ref, e_ref = 100.0, 5.0
    i_ref, i_other = 60.0, 45.0
    v_scaled, e_scaled = scale_inclination(v_ref, e_ref, i_ref, i_other)
    v_back, e_back = scale_inclination(v_scaled, e_scaled, i_other, i_ref)
    near(v_back, v_ref, rtol=1e-12, msg="v round-trip")
    near(e_back, e_ref, rtol=1e-12, msg="e round-trip")
    require(abs(v_scaled - v_ref) > 1e-6, "a genuine inclination change must actually change v_obs")
    return {"v_scaled": v_scaled, "e_scaled": e_scaled}


CHECKS = [
    ("parse_component_line_synthetic", check_parse_component_line_synthetic),
    ("parse_component_line_too_short_raises", check_parse_component_line_too_short_raises),
    ("parse_metadata_line_synthetic", check_parse_metadata_line_synthetic),
    ("parse_metadata_line_wrong_token_count_raises", check_parse_metadata_line_wrong_token_count_raises),
    ("metadata_table_duplicate_galaxy_raises", check_metadata_table_duplicate_galaxy_raises),
    ("component_table_duplicate_radius_raises", check_component_table_duplicate_radius_raises),
    ("component_table_non_positive_radius_raises", check_component_table_non_positive_radius_raises),
    ("no_separator_found_raises", check_no_separator_found_raises),
    ("sign_convention_700_not_900", check_sign_convention_700_not_900),
    ("distance_scaling_and_g_bar_cancellation", check_distance_scaling_and_g_bar_cancellation),
    ("inclination_scaling_round_trip", check_inclination_scaling_round_trip),
    ("r5_metadata_inf_sbeff_rejected", check_r5_metadata_inf_sbeff_rejected),
    ("r5_component_nan_distance_rejected", check_r5_component_nan_distance_rejected),
    ("r5_cross_table_distance_mismatch_rejected", check_r5_cross_table_distance_mismatch_rejected),
]


def main() -> int:
    report = {
        "package": "GALAXY_DYNAMICS_ROADMAP.md Paket G4 (SPARC adapter, synthetic fixtures only)",
        "timestamp": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "python": sys.version.split()[0],
        "checks": {},
    }
    all_ok = True
    for name, fn in CHECKS:
        try:
            detail = fn()
            report["checks"][name] = {"status": "pass", "detail": detail}
            print(f"PASS  {name}")
        except AssertionError as e:
            all_ok = False
            report["checks"][name] = {"status": "fail", "error": str(e)}
            print(f"FAIL  {name}: {e}")
        except Exception as e:  # noqa: BLE001
            all_ok = False
            report["checks"][name] = {"status": "error", "error": f"{type(e).__name__}: {e}"}
            print(f"ERROR {name}: {type(e).__name__}: {e}")

    out = Path(__file__).with_name("verify_sparc_adapter_results.json")
    out.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    print(f"\n{sum(1 for c in report['checks'].values() if c['status'] == 'pass')}/{len(CHECKS)} checks passed")
    print(f"Report written to {out}")
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
