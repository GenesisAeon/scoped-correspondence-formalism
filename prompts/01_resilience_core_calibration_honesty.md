# Phase-2-Prompt 1/N: resilience-core -- Kalibrierungs-Skripte ehrlich machen

**Repo:** `D:\mandala\resilience-core` (GenesisAeon Package 40, PyPI `resilience-core`)
**Ziel dieses Tickets:** zwei Kalibrierungs-Skripte konsistent ehrlich
machen, in die Testsuite einbinden, und einen bekannten Zirkelbezug
dokumentieren. **Keine Wertaenderung an bestehenden Konstanten, kein
Versions-Bump** (folgt separat nach Review).

## Kontext (verifiziert, 2026-09-15)

Das Paket hat drei Kalibrierungs-Skripte unter
`src/resilience_core/benchmarks/`:

- `amoc_calibration.py` ist **vorbildlich ehrlich**: Docstring und
  Rueckgabe-Dict sagen explizit `"calibration_status": "OPEN — pending
  amoc-utac (P18) timeseries"`, berechnet `R_REQUIRED_FOR_TARGET = 3.54`
  (den r-Wert, der noetig waere, um den Atlas-Zielwert Rho=0.65 zu
  erreichen), und behauptet an keiner Stelle, dass der Default-Parameter-
  Output (`r=1.0`) den Zielwert treffen sollte.
- `arctic_calibration.py` und `sandpile_calibration.py` tun das NICHT:
  beide behaupten `RHO_ARCTIC_EXPECTED`/`RHO_SANDPILE_EXPECTED` als
  Zielwerte und berechnen ein `rho_in_range`-Flag, als sollte der
  Default-Parameter-Output diese Ziele treffen. Tatsaechlich (mit den
  aktuellen Default-Parametern ausgefuehrt):
  - `run_arctic_calibration()` liefert `rho=0.0`, `rho_in_range=False`
    (Ziel war `0.05 +/- 0.02`).
  - `run_sandpile_calibration()` liefert `rho=0.222`, `rho_in_range=False`
    (Ziel war `0.75 +/- 0.10`).
  - Keines der beiden Skripte wird von der automatischen Testsuite
    aufgerufen (`grep -r "arctic_calibration\|sandpile_calibration"
    tests/` findet nichts) -- der Fehlschlag ist seit Erstellung
    unbemerkt geblieben.
  - `tests/test_rho.py` selbst ist an dieser Stelle bereits ehrlich
    (Docstring-Kommentar Zeilen 3-10: erklaert, dass die Zielwerte
    domaenenspezifisches r brauchen, testet nur relative Ordnung). Der
    Widerspruch besteht NUR zwischen diesem ehrlichen Kern-Test-Kommentar
    und den beiden unehrlichen Kalibrierungs-Skripten.
  - Ursache beim Arctic-Fall: `GAMMA_MAX = 0.920` in `constants.py` ist
    wortwoertlich der Arctic-Benchmark-Gamma-Wert selbst (Kommentar:
    "Maximum observed Gamma in the CREP Atlas (ERA5 Arctic)"). Die
    Kritikalitaetsmarge `1-Gamma/Gamma_max` wird fuer die Arctic-Domaene
    bei ihrem eigenen Benchmark-Wert dadurch IMMER exakt Null, per
    Konstruktion.

## Aufgabe

### 1. `arctic_calibration.py` und `sandpile_calibration.py` an `amoc_calibration.py`s Ehrlichkeits-Muster angleichen

Fuer beide Dateien:
- Berechne (analog zu AMOC) den tatsaechlich benoetigten `r`-Wert, um den
  behaupteten Zielwert mit den aktuellen Default-Parametern (sigma=2.2,
  c_critical=0.5) zu erreichen. Formel (aus `rho_calculator.py`):
  `rho = r * tanh(sigma*gamma)^2 * (1 - gamma/gamma_max) * coupling_factor`
  -- nach `r` aufloesen, mit `coupling_factor=1.0` (keine Kopplung
  registriert), fuer Sandpile. **Fuer Arctic ist das nicht moeglich, da
  `(1-gamma/gamma_max)` bei `gamma=gamma_max=0.920` exakt Null ist,
  unabhaengig von r** -- das muss im Skript selbst als Befund benannt
  werden (siehe Punkt 2), nicht rechnerisch umgangen werden.
- Ersetze `RHO_..._EXPECTED`/`rho_in_range` durch dasselbe Format wie bei
  AMOC: `..._WITH_DEFAULT_R`, `..._ATLAS_TARGET`, `R_REQUIRED_FOR_TARGET`
  (wo berechenbar), `"calibration_status": "OPEN — pending real
  <domain>-Zeitreihendaten"`.
- Fuer Sandpile: `R_REQUIRED_FOR_TARGET` sollte berechenbar sein (analog
  zu AMOCs 3.54) -- bitte den tatsaechlichen Zahlenwert einsetzen, nicht
  raten.
- Fuer Arctic: da `(1-gamma/gamma_max)=0` strukturell bedingt ist, kein
  `R_REQUIRED_FOR_TARGET` behaupten (waere durch Null teilen/undefiniert).
  Stattdessen im Docstring UND im Rueckgabe-Dict explizit festhalten:
  `"calibration_status": "OPEN -- GAMMA_MAX equals this domain's own
  benchmark Gamma value, so criticality_margin is structurally zero here;
  see constants.py comment"`.

### 2. `constants.py`: `GAMMA_MAX` mit einem Known-Issue-Kommentar versehen

Direkt oberhalb von `GAMMA_MAX: float = 0.920` einen Kommentar ergaenzen,
der erklaert: dieser Wert ist identisch mit dem Arctic-Benchmark-Gamma
selbst, wodurch die Kritikalitaetsmarge fuer die Arctic-Domaene bei ihrem
eigenen Benchmark-Wert strukturell immer exakt Null wird, unabhaengig von
r/sigma. **Wert NICHT aendern** -- nur dokumentieren, analog zum bereits
vorhandenen Muster in `afet-tensions/src/afet_tensions/constants.py`
(Kommentar oberhalb von `GAMMA_DOMAIN`, dort schon umgesetzt -- als
Vorbild fuer Formulierungsstil verwenden, per Datei-Lesen falls Zugriff
besteht).

### 3. Testsuite-Anbindung

In `tests/` eine neue Testdatei `test_calibration_scripts.py` (oder
Erweiterung von `test_rho.py`) ergaenzen, die:
- `run_amoc_calibration()`, `run_arctic_calibration()`,
  `run_sandpile_calibration()` tatsaechlich aufruft,
- prueft, dass jedes Ergebnis-Dict einen `calibration_status`-Schluessel
  hat (nach der Aenderung aus Punkt 1 auch fuer Arctic/Sandpile),
- **nicht** behauptet, dass `rho` die Atlas-Zielwerte trifft (das bleibt
  laut den Skripten selbst offen) -- nur, dass die Skripte fehlerfrei
  laufen und ihre Statusfelder konsistent gefuellt sind.
Ziel: kuenftige stille Divergenz zwischen Skript-Verhalten und
Dokumentation wird von CI erfasst, auch wenn die zugrunde liegende
Kalibrierungsfrage offen bleibt.

## Akzeptanzkriterien

- `pytest` läuft weiterhin komplett gruen (bestehende + neue Tests).
- Kein bestehender Zahlenwert (`GAMMA_MAX`, `SIGMA`, `SIGMA_PHI`,
  `C_CRITICAL` etc.) wurde veraendert.
- Alle drei Kalibrierungs-Skripte folgen jetzt demselben ehrlichen
  Berichtsformat wie `amoc_calibration.py`.
- `GAMMA_MAX` hat einen erklaerenden Kommentar zum Arctic-Zirkelbezug.
- Kein Versions-Bump, kein CHANGELOG-Eintrag, kein Zenodo-Release --
  das macht Claude nach Review in einem separaten Schritt.

## Bitte NICHT tun

- Keine neuen Abhaengigkeiten hinzufuegen.
- Kein Refactoring ausserhalb der genannten Dateien.
- Keine Aenderung an `eigenrate.py`, `coupling.py`, `frame_principle.py`,
  `system.py` -- die sind nicht Teil dieses Tickets.
