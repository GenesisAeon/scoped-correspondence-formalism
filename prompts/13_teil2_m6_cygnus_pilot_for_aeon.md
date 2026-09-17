Auftrag: Teil 2, Milestone 6 ("Uncertainty & Validation" — erster echter
Datenpilot) — Domäne von Johann entschieden nach dem Survey (F21):
**cygnus-jet-utac**, Makrovariable **`jet_pa_deg`** (Jet-Positionswinkel).

## Kontext

Das ist der erste Auftrag in diesem Repo, der auf **echten, gemessenen
Daten** arbeitet — nicht auf Legacy-Formeln, nicht auf synthetischen
Beispielen. Entsprechend anders ist die Abnahme: es zählt nicht "Zahlen
stimmen exakt mit einem bereits bekannten Ergebnis überein" (das gibt es
hier nicht), sondern "der Test wurde ehrlich vorab festgelegt und ehrlich
berichtet — auch wenn das Modell verliert".

Datei: `data/cygnus_x1_radio_epochs.yaml` im Paket `cygnus-jet-utac`
(18 VLBI-Epochen, 2006.2–2023.8, Felder `year`, `mjd`, `jet_pa_deg`,
`jet_flux_mJy`). Diese Datei muss 1:1 aus dem Paket übernommen werden
(gleicher Wortlaut/Zahlen wie im Survey F21 bestätigt) — nicht neu
erfinden oder aus dem Gedächtnis reproduzieren.

**Wichtige Vorgeschichte (worked_example_cygnus_jet_utac.md):** Für
dieses Paket ist bereits dokumentiert, dass `Γ_jet` aus einem
eingesetzten Wirkungsgrad bei festgelegtem σ **invers** berechnet wurde —
eine bekannte Zirkularität. **Dieser Pilot darf keinen bestehenden
σ/Γ_jet/Wirkungsgrad-Wert aus `cygnus-jet-utac` übernehmen.** Alle freien
Parameter werden ausschließlich aus den Kalibrierungs-Epochen dieses
Auftrags neu geschätzt.

## Vorab festgelegt (nicht verhandelbar, nicht nach dem Fit änderbar)

- **Makrovariable:** `jet_pa_deg` (Grad). `jet_flux_mJy` ist explizit
  NICHT Teil dieses Auftrags (optionaler Bonus für einen späteren
  Auftrag, falls gewünscht).
- **Split:** Kalibrierung = erste 9 Epochen (2006.2–2015.2), Holdout =
  letzte 9 Epochen (2016.1–2023.8). Diese Aufteilung ist zeitlich, fix,
  und wird VOR jedem Fit im Dataset Manifest festgeschrieben — kein
  Nachjustieren des Splits, egal wie der Fit ausfällt.
- **Baseline:** Persistenz — der letzte Kalibrierungswert (`jet_pa_deg`
  der 9. Epoche) wird für alle Holdout-Epochen unverändert fortgeschrieben.
  Das ist die Vergleichsgröße aus `ROADMAP.md` §3 Punkt 4 ("Vergleich mit
  einer einfachen Persistenz-/Markov-Baseline").
- **Fehlermetrik:** RMSE zwischen Vorhersage und beobachtetem `jet_pa_deg`
  auf den 9 Holdout-Epochen, für Modell und Baseline getrennt berechnet.

## Umfang dieses Auftrags

### 1. `validation.dataset_manifest` (Dataset Manifest als Typ)

Ein typisiertes Objekt, das dokumentiert: Quelldatei + Pfad, Lizenz/Zitat
(aus der YAML-Kopfzeile: Stirling et al. 2001, Rushton et al. 2011,
Miller-Jones et al. 2021, Prabu et al. 2026), Makrovariable + Einheit,
Gesamtzahl Epochen, Kalibrierungs-/Holdout-Indizes (die exakte, oben
festgelegte Aufteilung), Ausschlüsse (hier: keine). Kein allgemeines
Schema für beliebige zukünftige Datensätze — nur so allgemein, wie dieser
eine Fall es braucht (YAGNI, wie in jedem bisherigen Milestone).

### 2. `validation.split` (Train/Holdout-Split-Utility)

Eine Funktion, die die 18 Epochen anhand der oben fixierten Indizes in
Kalibrierung/Holdout teilt und `ScopeViolationError` wirft, wenn jemand
versucht, mit anderen Indizes als den im Manifest festgelegten zu
splitten (verhindert nachträgliches "Data Snooping").

### 3. Baseline + Kandidatenmodell

- `persistence_baseline(calibration_pa) -> float`: letzter
  Kalibrierungswert, konstant fortgeschrieben.
- Ein Relaxationsmodell `pa_eq + (pa0 - pa_eq) * exp(-r*(t-t_ref))`,
  Parameter `(pa_eq, r)` per kleinste Quadrate NUR auf den 9
  Kalibrierungs-Epochen geschätzt (`t_ref` = erste Kalibrierungsepoche,
  `pa0` = deren `jet_pa_deg`-Wert, keine freie Größe). Nutze
  `dynamics.recovery_rate_at_equilibrium`/`recovery_rate_from_relaxation`
  aus dem bereits gemergten `dynamics`-Modul, wo die Formel passt — nicht
  neu implementieren, wenn eine passende Funktion existiert.

### 4. `ValidationReport`

Enthält: Domäne, Makrovariable, Split-Definition, `model_rmse_holdout`,
`baseline_rmse_holdout`, `model_beats_baseline: bool`,
`fitted_parameters` (mit Angabe, dass sie ausschließlich aus
Kalibrierungsdaten stammen), Quellenangabe. **Ein `model_beats_baseline:
False`-Ergebnis ist ein vollständiger, korrekter Auftragsabschluss —
kein Fehler, kein Grund, den Split oder die Parameter nachträglich zu
ändern.**

### 5. Explizit NICHT Teil dieses Auftrags

- Jede Aussage über andere Domänen, Universalität oder Domänenvergleich
  (`ROADMAP.md` §3 Punkt 4 kommt erst NACH diesem einen abgeschlossenen
  Piloten, als möglicher eigener späterer Auftrag).
- `jet_flux_mJy` oder jede andere Größe aus derselben Datei.
- Wiederverwendung von `cygnus-jet-utac`s bestehenden σ/Γ_jet-Werten.
- Ein allgemeines Dataset-Manifest-Schema für beliebige künftige
  Domänen — nur der hier konkret gebrauchte Fall.
- Änderungen an `correspondence/`, `observation/`, `dynamics/`,
  `coupling/`, `closure/`, `viability/`, `membership/`,
  `identifiability/` — nur Aufruf der bestehenden `dynamics`-Funktionen.

## Verifikation

`verify_cygnus_pilot.py`: lädt `data/cygnus_x1_radio_epochs.yaml` (Pfad
im Bericht angeben — falls diese Datei in diesem Repo nicht existiert,
sie unverändert aus dem `cygnus-jet-utac`-Paket kopieren, mit Quellenangabe
im Manifest), führt Split, Fit, Baseline und RMSE-Berechnung aus,
berichtet alle Zahlen aus DIESEM Skriptlauf. Da es keine bekannte
"richtige" Zahl gibt, prüft das Skript stattdessen: Split-Indizes wie
festgelegt, `ScopeViolationError` bei falschem Split-Versuch, Baseline
korrekt als konstante Fortschreibung, Fit ausschließlich auf
Kalibrierungsdaten (Holdout-Daten dürfen im Fit-Code nicht referenziert
werden — bitte im Bericht explizit bestätigen).

## Abnahmebedingungen (Astra-Standard, angepasst für echte Daten)

1. Textformeln (LaTeX/Markdown), keine Bildformeln.
2. `verify_cygnus_pilot.py` mit reproduzierbarem JSON-Report unter
   `verification/`.
3. Alle Zahlen aus DEM SKRIPTLAUF, inklusive des Ergebnisses, falls das
   Modell die Baseline nicht schlägt — nicht schönrechnen, nicht den
   Split nachträglich ändern.
4. Explizites Mapping auf `ROADMAP.md` §3, `dynamics/core.py`, und die
   Quelldatei `data/cygnus_x1_radio_epochs.yaml`.
5. KEINE Mutation von FORMALISM.md oder einem der sieben Layer-/
   Erweiterungsdokumente.
6. Johann-OK vor jeder Aufnahme in einen "Kern"-Status — bei diesem
   Auftrag zusätzlich: Johann-OK ersetzt keine externe Prüfung, dieser
   Pilot bleibt eine erste Fallstudie, kein Beweis für die Formel.

## Lieferformat

Eigener Branch `aeon/m6-cygnus-pilot` auf
`GenesisAeon/scoped-correspondence-formalism`, direkt gepusht. Claude
reviewed (Diff, Skript selbst nachrechnen, Kalibrierungs-/Holdout-Trennung
im Code stichprobenartig prüfen, mindestens eine RMSE-Zahl von Hand
gegenrechnen) und merged erst nach Johanns OK.
