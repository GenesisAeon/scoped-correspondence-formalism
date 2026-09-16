# Phase-2-Prompt 3/N: afet-tensions -- unabhaengiger Refit von GAMMA_DOMAIN und kappa

**Repo:** `D:\mandala\afet-tensions` (GenesisAeon Package 34, PyPI `afet-tensions`)
**Ziel:** die beiden zirkulaeren Konstanten `GAMMA_DOMAIN` und `kappa`
(S8-Evolutions-ODE-Rate) durch unabhaengig aus echten Daten gefittete
Werte ersetzen, mit voller Reproduzierbarkeit und ehrlicher
Unsicherheitsangabe. **Diese Aenderung wirkt sich auf reale
Vorhersagen des Pakets aus (H0, S8, DESI, Euclid) -- das ist beabsichtigt,
nicht zu vermeiden.** Kein Versions-Bump in diesem Schritt (folgt nach
Review).

## Kontext: warum das noetig ist (verifiziert 2026-09-15)

`GAMMA_DOMAIN` wurde bisher algebraisch geloest, damit `h0_effective()`
exakt das bereits bekannte H0-Verhaeltnis reproduziert
(`GAMMA_DOMAIN = log(H0_RATIO) / ((BETA_LOCAL-BETA_CMB)*SIGMA_PHI)`) --
kein unabhaengiger Vorhersagewert. `kappa=0.000708` (die Rate der
Γ(z)-Differentialgleichung in `crep_redshift.py`) war implizit auf dieses
zirkulaere Γ_domain zugeschnitten.

Die 5 echten H0-Messungen liegen bereits im Paket unter
`data/hubble_tension_data.yaml`, die 4 echten S8-Messungen unter
`data/s8_measurements.yaml` -- beide Dateien werden vom Code bisher NICHT
programmatisch gelesen (nur als Referenz gebuendelt). Dieses Ticket macht
sie zur tatsaechlichen Kalibrierungsgrundlage.

## Aufgabe 1: neues Skript `scripts/fit_gamma_domain_and_kappa.py`

Reproduzierbarer, eigenstaendiger Fit (nutzt bereits vorhandene
Abhaengigkeiten `pyyaml`, `scipy` -- keine neuen noetig):

```python
"""Reproducible independent fit of GAMMA_DOMAIN and kappa from real data.

Replaces the circular 2-point construction previously in constants.py.
GAMMA_DOMAIN is fit via weighted least-squares across the 5 real H0
measurements in data/hubble_tension_data.yaml. kappa (the S8-evolution
ODE rate in crep_redshift.py) is then fit, holding the new GAMMA_DOMAIN
fixed, via weighted least-squares across the 3 real weak-lensing S8
measurements in data/s8_measurements.yaml (Planck is excluded from the
kappa fit: it is used as the z=1100 boundary condition/anchor, not a
free-fit target -- s8_at_z(1100) always returns S8_CMB by construction).

Run this script to reproduce/update both constants whenever the bundled
data files are revised.
"""
from __future__ import annotations

import math
from pathlib import Path

import yaml
from scipy.optimize import minimize_scalar

from afet_tensions.constants import BETA_CMB, BETA_LOCAL, H0_CMB, S8_CMB, SIGMA_PHI
from afet_tensions.crep_redshift import CREPRedshiftEvolution

DATA_DIR = Path(__file__).parent.parent / "data"


def _beta_for(measurement_type: str) -> float:
    return BETA_LOCAL if measurement_type == "late_universe" else BETA_CMB


def _h0_pred(gamma: float, beta: float) -> float:
    return H0_CMB * math.exp(beta * SIGMA_PHI * gamma)


def fit_gamma_domain() -> dict[str, object]:
    data = yaml.safe_load((DATA_DIR / "hubble_tension_data.yaml").read_text(encoding="utf-8"))
    measurements = data["measurements"]

    def chi2(gamma: float) -> float:
        return sum(
            ((m["h0"] - _h0_pred(gamma, _beta_for(m["type"]))) / m["sigma"]) ** 2
            for m in measurements
        )

    result = minimize_scalar(chi2, bounds=(0.01, 5.0), method="bounded")
    dof = len(measurements) - 1
    residuals = [
        {
            "name": m["name"],
            "observed": m["h0"],
            "predicted": _h0_pred(result.x, _beta_for(m["type"])),
            "residual_sigma": (m["h0"] - _h0_pred(result.x, _beta_for(m["type"]))) / m["sigma"],
        }
        for m in measurements
    ]
    return {"gamma_domain": result.x, "chi2": result.fun, "dof": dof,
            "chi2_per_dof": result.fun / dof, "residuals": residuals}


def fit_kappa(gamma_domain: float) -> dict[str, object]:
    data = yaml.safe_load((DATA_DIR / "s8_measurements.yaml").read_text(encoding="utf-8"))
    # Weak-lensing surveys only -- treated as z=0 per the package's own
    # existing s8_late()/s8_at_z(0.0) convention (no per-survey z bundled).
    # Planck excluded: it is the z=1100 anchor, not a free-fit target.
    wl_surveys = [m for m in data["surveys"] if m["method"].lower().startswith("weak")]

    def chi2(kappa: float) -> float:
        crep = CREPRedshiftEvolution(kappa=kappa, gamma_cmb=gamma_domain)
        pred = crep.s8_at_z(0.0)
        return sum(((m["s8"] - pred) / m["sigma"]) ** 2 for m in wl_surveys)

    result = minimize_scalar(chi2, bounds=(1e-6, 0.01), method="bounded")
    crep_check = CREPRedshiftEvolution(kappa=result.x, gamma_cmb=gamma_domain)
    pred = crep_check.s8_at_z(0.0)
    dof = len(wl_surveys) - 1
    residuals = [
        {"name": m["name"], "observed": m["s8"], "predicted": pred,
         "residual_sigma": (m["s8"] - pred) / m["sigma"]}
        for m in wl_surveys
    ]
    return {"kappa": result.x, "s8_z0_predicted": pred, "chi2": result.fun,
            "dof": dof, "chi2_per_dof": result.fun / dof if dof else float("nan"),
            "residuals": residuals}


if __name__ == "__main__":
    import json
    gamma_result = fit_gamma_domain()
    kappa_result = fit_kappa(gamma_result["gamma_domain"])
    print(json.dumps({"gamma_domain_fit": gamma_result, "kappa_fit": kappa_result}, indent=2))
```

Bitte dieses Skript **tatsaechlich ausfuehren** und pruefen, dass es
liefert (Toleranz 1e-6):
- `gamma_domain ≈ 0.6403419953108261` (chi2/dof ≈ 1.398)
- `kappa ≈ 0.00042269029427273555` (chi2/dof ≈ 0.168)

Falls die Zahlen abweichen: NICHT die hier genannten Zielwerte erzwingen
-- das tatsaechliche Skript-Ergebnis ist die Wahrheit, bitte melden statt
uebergehen.

## Aufgabe 2: `constants.py` aktualisieren

```python
# GAMMA_DOMAIN: independently fit via weighted least-squares regression
# across the 5 real H0 measurements in data/hubble_tension_data.yaml
# (2026-09-15), replacing the previous circular 2-point exact-match
# construction (GAMMA_DOMAIN = log(H0_RATIO)/((BETA_LOCAL-BETA_CMB)*SIGMA_PHI),
# which was solved so h0_effective() exactly reproduced the already-known
# H0 ratio by construction, with no independent predictive content).
# Reproducible via scripts/fit_gamma_domain_and_kappa.py.
# Fit quality: chi2/dof ~= 1.40 (5 points, 1 free parameter). Two points
# show moderate tension under the simple two-category (early/late) beta
# model: TRGB residual -1.55 sigma, DESI DR1 residual +1.59 sigma --
# disclosed, not hidden. This is a first independent estimate, not a
# final precision calibration (same honesty standard as AMOC's "OPEN"
# status in benchmarks/amoc_calibration.py).
GAMMA_DOMAIN = 0.6403419953108261
```

Entfernen: die alte `GAMMA_DOMAIN = math.log(...)`-Zeile und den
bisherigen Known-Issue-Kommentar darueber (wird durch den neuen ersetzt,
nicht ergaenzt). `math`-Import in `constants.py` pruefen -- falls sonst
nirgends mehr gebraucht, entfernen.

In `crep_redshift.py`, `CREPRedshiftEvolution.__init__`:
```python
def __init__(self, kappa: float = 0.00042269029427273555, gamma_cmb: float = GAMMA_DOMAIN) -> None:
```
mit einem Kommentar analog zu oben: `kappa` unabhaengig gefittet gegen
die 3 realen Weak-Lensing-S8-Messungen (KiDS-1000, DES Y3, HSC), Planck
als z=1100-Anker ausgenommen. chi2/dof ~= 0.17 (2 dof) -- guter Fit,
Details siehe `scripts/fit_gamma_domain_and_kappa.py`.

## Aufgabe 3: Tests in `tests/test_afet_tensions.py` auf real begruendete Toleranzen umstellen

Die folgenden Tests hatten bisher Toleranzen, die implizit die
Zirkelbezug-Konstruktion pruefen (nicht die reale Beobachtung). Bitte wie
folgt ersetzen -- jede neue Toleranz ist die ECHTE gemeldete
Standardabweichung der jeweiligen Referenzmessung, keine erfundene Zahl:

```python
def test_beta_hierarchy_h0_local():
    model = BetaHierarchyModel()
    assert abs(model.h0_local() - 73.04) <= 1.04  # SH0ES (Riess+ 2022) own sigma

def test_beta_hierarchy_h0_cmb():
    model = BetaHierarchyModel()
    assert abs(model.h0_cmb() - 67.4) <= 0.5  # Planck 2018 own sigma

def test_beta_hierarchy_h0_ratio():
    model = BetaHierarchyModel()
    assert abs(model.h0_ratio() - 1.084) <= 0.025  # combined SH0ES/Planck relative uncertainty

def test_crep_s8_at_z0():
    crep = CREPRedshiftEvolution()
    assert abs(crep.s8_at_z(0) - 0.77) <= 0.02  # spans KiDS-1000/DES Y3/HSC within their own sigmas

def test_s8_prediction():
    system = AFETTensions()
    s8_z0 = system.s8_prediction(0.0)
    s8_z1100 = system.s8_prediction(1100.0)
    assert abs(s8_z0 - 0.77) <= 0.02
    assert abs(s8_z1100 - 0.832) <= 0.013
```

`test_crep_s8_at_z_cmb` (0.83±0.01) und `test_beta_hierarchy_inverse`
sollten bereits ohne Aenderung weiterhin bestehen -- bitte pruefen statt
annehmen.

In `benchmark.py`, `TENSIONS_TARGETS` entsprechend aktualisieren:
```python
TENSIONS_TARGETS: dict[str, tuple[float, float]] = {
    "h0_local_km_s_mpc": (73.04, 1.04),
    "h0_cmb_km_s_mpc": (67.4, 0.5),
    "h0_ratio": (1.084, 0.025),
    "s8_z0": (0.77, 0.02),
    "s8_z_cmb": (0.832, 0.013),
    "ligo_omega_rig_Hz": (0.018, 0.002),  # unveraendert, unabhaengig von Gamma_domain/kappa
}
```

## Aufgabe 4: README.md -- Benchmark-Tabelle und Zahlenbeispiele aktualisieren

Die "Benchmark-Targets"-Tabelle und alle Python-API-Beispiele mit
Zahlenwerten (H0-Ratio 1.083, S8-Werte etc.) im README auf die neuen,
real gefitteten Zielwerte/Toleranzen umstellen (siehe Aufgabe 3). Einen
neuen Abschnitt "Kalibrierung" ergaenzen, der kurz erklaert: beide
Konstanten sind jetzt unabhaengig aus echten Daten gefittet (nicht mehr
zirkulaer), mit Link/Verweis auf `scripts/fit_gamma_domain_and_kappa.py`
zur Reproduktion.

## Akzeptanzkriterien

- `scripts/fit_gamma_domain_and_kappa.py` laeuft fehlerfrei und liefert
  die oben genannten Werte (Toleranz 1e-6).
- `pytest` laeuft komplett gruen mit den neuen, real begruendeten
  Toleranzen.
- `git diff` zeigt Aenderungen NUR in: `constants.py`, `crep_redshift.py`
  (nur der `__init__`-Default + Kommentar), `tests/test_afet_tensions.py`,
  `benchmark.py`, `README.md`, plus die neue Datei
  `scripts/fit_gamma_domain_and_kappa.py`.
- Kein Versions-Bump, kein CHANGELOG-Eintrag, kein Zenodo-Release --
  macht Claude nach Review.

## Bitte NICHT tun

- Keine weiteren Konstanten anfassen (`BETA_LOCAL`, `BETA_CMB`, `SIGMA_PHI`,
  `V_RIG`, `OMEGA_RIG_HZ` bleiben unveraendert -- LIGO-Vorhersage ist von
  diesem Ticket unberuehrt).
- Den zweiten, kleineren bekannten Zirkelbezug in `desi_prediction.py`
  (`beta_from_h0(h0_local())` ist ein Rundtrip zu `BETA_LOCAL`) NICHT in
  diesem Ticket anfassen -- separates, bereits vermerktes Ticket.
- Keine Toleranzen "passend machen", falls das Skript andere Zahlen als
  oben liefert -- echtes Ergebnis melden, nicht die Zielwerte hier blind
  uebernehmen.
