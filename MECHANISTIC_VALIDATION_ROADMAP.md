# Von Prototyp zu belastbarer Schätzung — Roadmap (2026-09-21)

Antwort auf `prompts/Answers/nicht_stationäre_Treiber/SCF_Review_f8e249f.md`
(Astra, 2026-09-21) — die Zweitprüfung des `NONSTATIONARY_ROADMAP.md`-Ergebnisses
(Commit `f8e249f`). Die dort gefundenen konkreten Fehler (Energiebilanz-
Optimierer, fehlender `-u̇`-Term, χ-Schwellenüberdehnung, Puffer-Richtungsumkehr,
ETAS-Verzweigungsraten-Fragilität) wurden bereits behoben (Commit `20efc63`).
Diese Roadmap trägt Astras **verbleibende, größere Vorschläge** — "der nächste
große Fortschritt liegt in belastbarer Schätzung, unabhängiger Validierung und
Verbindungen zwischen den vorhandenen Modulen" — als eigenes, Punkt-für-Punkt
abzuarbeitendes Programm nach, in Astras eigener Priorisierung (Abschnitt
"Welche Erweiterungen jetzt den höchsten Nutzen haben").

Johanns Auftrag (2026-09-21): "Ja, lass uns das als Roadmap abarbeiten."

Gleiche Disziplin wie bei `NONSTATIONARY_ROADMAP.md`: additive Module, echte
Daten, Hand-Nachrechnung vor Code, `verify_*.py` mit Scope-Verletzungen,
volle Suiten-Regression nach jedem Paket, bestehende Ergebnisse bleiben
unverändert stehen (neue Erkenntnisse ergänzen, nicht überschreiben).

| # | Paket | Status |
|---|---|---|
| 1 | Numerisch zuverlässige Kalibrierung + Profile-Likelihood-Anschluss | ⏸ geplant |
| 2 | Gemeinsame zeitliche Prognoseprüfung (alle Mechanismus-Module) | ⏸ geplant |
| 3 | Probabilistische Ergebnisse (Vorhersageintervalle, Scoring-Regeln) | ⏸ geplant |
| 4 | Zwei neue Strukturbrücken (Impulsantwort; Kern/Verzweigung) | ⏸ geplant |
| 5 | Beobachtungs- und Zustandsmodelle (COVID Negativ-Binomial, Mehrländer) | ⏸ geplant |
| 6 | Mehrdimensionale R-Tipping-/Viabilitätskarten | ⏸ geplant |

## Paket 1 — Numerisch zuverlässige Kalibrierung + Profile-Likelihood-Anschluss

**Bereits erledigt** (Commit `20efc63`, Teil der Fehlerkorrektur, nicht Teil
dieses Pakets): exakte Matrixexponential-Fortschreibung + physikalisch
motivierte `PARAM_BOUNDS` + Mehrfachstart für `energy_balance.py`, `at_bound`-
Flag, `solve_ivp`-Gegenrechnung. Auch bereits vorhanden: die Prüfung auf
lückenlose Kalenderjahre in `fit_energy_balance_model` (Astras Hinweis zur
Jahresindex-Kompression war zum Zeitpunkt der Zweitprüfung noch offen, ist
aber inzwischen durch die Korrektur mit erledigt).

**Noch offen (dieses Paket):**
- Anschluss an `identifiability.profile_likelihood` für `energy_balance.py`
  (und exploratorisch für `covid_renewal.py`/`etas.py`, wo sinnvoll): welche
  Parameterkombinationen sind bei gegebener Datenlage tatsächlich
  unterscheidbar? Astras Beobachtung (kleinster Singulärwert der
  Sensitivitätsmatrix sehr klein) braucht eine echte Charakterisierung, nicht
  nur die jetzige Bound-Sättigungs-Meldung.
- Explizite Diagnose von Gradient, Abbruchgrund (`termination_status`) und
  Startwertabhängigkeit im JSON-Ergebnisbericht selbst (nicht nur im
  Docstring behauptet) — für `energy_balance.py` UND `etas.py` (dort:
  Konvergenzstatus samt Budget und Startwerten explizit ausweisen).
- ETAS: Beobachtungsbeginn/-ende explizit als Parameter statt implizit als
  erste/letzte Ereigniszeit (Astras konkreter Kritikpunkt); Vorhistorie vor
  `t=0` berücksichtigen, falls verfügbar.
- Ein gemeinsamer Ergebnisvertrag (Astras Vorschlag): ein
  `EstimationContract`-artiges Dataclass-Feld-Set
  (`numerically_verified`, `optimizer_converged`, `parameters_identified`,
  `out_of_sample_evaluated`, `mechanism_discriminated`), das alle neuen
  Fit-Ergebnisklassen (`EnergyBalanceFitResult`, `ETASFitResult`,
  `RenewalReport`) konsistent ausweisen, damit ein grüner Test nicht
  versehentlich als empirische Bestätigung gelesen wird.

## Paket 2 — Gemeinsame zeitliche Prognoseprüfung

Astras Kernkritik: jedes neue Modell wurde bisher gegen sein EIGENES
Trainingsfenster bewertet (In-Sample-RMSE), nicht gegen dieselben Zielgrößen,
Ursprünge und Horizonte wie die anderen. `validation/rolling_origin.py`
(Paket 1 der ersten Roadmap) existiert bereits generisch — dieses Paket
wendet es zum ersten Mal auf `covid_renewal.py`, `energy_balance.py` und
`etas.py` an:
- Modellwahl (Startwerte, Bounds, Fensterwahl) ausschließlich mit
  zurückliegenden Daten fixieren, VOR dem Blick auf die Prognoseperiode.
- Fehler getrennt nach Horizont ausweisen (nicht nur gepoolt).
- Direkter Vergleich: mechanistisches Modell vs. Persistenz vs. der
  jeweils bereits vorhandenen einfachen statistischen Baseline (z.B.
  `noaa_temp_pilot.md`s 30-Jahres-Trend für `energy_balance.py`).

## Paket 3 — Probabilistische Ergebnisse

Bisher liefern alle Module Punktschätzungen (RMSE, AIC). Astra verlangt
echte Vorhersageverteilungen:
- Vorhersageintervalle (z.B. aus Parameterunsicherheit via Paket 1, oder
  aus Residualstreuung) mit ausgewiesener Deckung (coverage) und Breite auf
  Holdout-Daten.
- Log-Score für Zähl-/Ereignismodelle (ETAS, COVID-Fallzahlen), CRPS oder
  Intervall-Score für kontinuierliche Ziele (Energiebilanz-Temperatur)
  (Gneiting & Raftery 2007).
- Ausdrücklicher Hinweis: `conformal_prediction`-Modul existiert bereits,
  aber seine Austauschbarkeitsannahme gilt NICHT ungeprüft für
  nichtstationäre, abhängige Zeitreihen — erst prüfen, dann anwenden.

## Paket 4 — Zwei neue Strukturbrücken

Astras eigene mathematische Beobachtung (Abschnitt "Die mathematisch
ergiebigste neue Verbindung"): mehrere neue Module verarbeiten eine
Vorgeschichte mit einem zeitlichen Kern — eine präzise strukturelle
Verwandtschaft, die im bestehenden `structural_bridges`-Schema (Quelle/Ziel,
Kernabbildung, Einheiten/Positivität, erhaltene Größe, Gegenbeispiel bei
verletzten Voraussetzungen — wie B1/B2) dokumentiert werden sollte, NICHT
als vorschnelle gemeinsame Kernel-API:

1. **EBM/Puffer über Impulsantworten**: für das lineare Energiebilanzmodell
   ist die Übertragungsfunktion `G(s) = (C_d*s+γ)/((C_s*s+α+γ)(C_d*s+γ)-γ²)`
   direkt herleitbar; der lineare Puffer (`viability/rate_dependent_buffer.py`)
   ist eine Faltung mit `exp(-rt)`. Gemeinsame Struktur: lineares
   Impulsantwort-System, schnelle/langsame Relaxation, Gedächtnis- und
   Filterwirkung.
2. **Renewal/ETAS-Hawkes über positive Kerne und Verzweigungsoperatoren**:
   `covid_renewal.py`s gewichtete Summe vergangener Inzidenzen und
   `etas.py`s selbsterregender Kern teilen die Struktur "nichtnegative
   Kernabbildung über eine Vorgeschichte"; für ein stationäres lineares
   Hawkes-Modell ist die Gesamtmasse des mittleren Kerns die erwartete Zahl
   direkter Nachkommen (Hawkes & Oakes 1974) — bei mehreren Typen wird
   daraus eine nichtnegative Matrix, deren Spektralradius die relevante
   Schwellenstruktur ist. Anschluss an die vorhandenen baumartigen
   Perkolationsbeispiele.

## Paket 5 — Beobachtungs- und Zustandsmodelle

Konkret für COVID (Astras Priorität 5): latente Dynamik (wahre
Infektionen), Messprozess (gemeldete, verzögerte, untererfasste Fälle) und
tatsächliche Prognoseaufgabe explizit trennen, statt sie in einem
deterministischen Punktschätzer zu vermengen:
- Echte tägliche Rohzahlen statt überlappender Siebentagesmittel als
  Zählmodell-Eingabe.
- Negativ-Binomial-Beobachtungsmodell für Überdispersion (Notwendigkeit
  über Residuen/Prognosescores prüfen, nicht a priori annehmen).
- Mehrere unabhängige Länder- und Zeitfenster mit unverändertem Verfahren
  (nicht nur die bereits bekannte China/Rest-Zerlegung auf demselben
  März-2020-Fenster).
- Für die Energiebilanz: die 2026 veröffentlichten "Indicators of Global
  Climate Change 2025" (Forster et al. 2026, Zenodo-archiviert) als
  nächste reale Datenquelle für vollständigeres Forcing (CO2-only vs.
  Gesamtforcing-Vergleich).

## Paket 6 — Mehrdimensionale R-Tipping-/Viabilitätskarten

Erweitert Paket 3/4 der ersten Roadmap (bereits mit der
Gleichlast-Gegenkontrolle in Commit `20efc63` begonnen): Amplitude, Dauer,
Pulsform UND Reserve getrennt als eigene Achsen variieren (Antwortfläche
statt einzelner 1D-Sweeps), unterschiedliche Normierungen explizit
dokumentieren, Grenzfälle und Endhorizonte prüfen. Für das
rate-induced-tipping-Beispiel: Anschluss an Wieczorek, Xie & Ashwin (2023)
— globale Schwellengeometrie (Kanten-Zustände, verbindende Orbits) statt
nur des bereits vorhandenen lokalen χ-Indikators.

## Arbeitsweise

- Wie bei `NONSTATIONARY_ROADMAP.md`: additive Module, echte Daten wo neu
  benötigt (mit Herkunftsnachweis in `data/real_data_manifest.json`),
  Hand-Nachrechnung vor Implementierung, `verify_*.py` mit
  Scope-Verletzungen und unabhängiger Gegenrechnung.
- Bestehende Ergebnisse (`NONSTATIONARY_ROADMAP.md` Pakete 1-5,
  `docs/*_pilot.md`) bleiben unverändert stehen; neue Auswertungen werden
  ergänzt.
- Volle Suiten-Regression nach jedem Paket.
- Diese Roadmap ist bewusst GRÖSSER und offener als die erste — nicht
  jedes Paket muss vollständig "erledigt" werden, um Wert zu liefern;
  Zwischenstände werden ehrlich als solche berichtet (siehe Astras eigener
  Ergebnisvertrag-Vorschlag in Paket 1).
