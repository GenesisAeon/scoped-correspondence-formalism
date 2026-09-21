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
| 1 | Numerisch zuverlässige Kalibrierung + Profile-Likelihood-Anschluss | ✅ erledigt |
| 2 | Gemeinsame zeitliche Prognoseprüfung (alle Mechanismus-Module) | ⏸ geplant |
| 3 | Probabilistische Ergebnisse (Vorhersageintervalle, Scoring-Regeln) | ⏸ geplant |
| 4 | Zwei neue Strukturbrücken (Impulsantwort; Kern/Verzweigung) | ⏸ geplant |
| 5 | Beobachtungs- und Zustandsmodelle (COVID Negativ-Binomial, Mehrländer) | ⏸ geplant |
| 6 | Mehrdimensionale R-Tipping-/Viabilitätskarten | ⏸ geplant |

## Paket 1 — Umsetzung (2026-09-21)

**Bereits vor diesem Paket erledigt** (Commit `20efc63`, Teil der
Fehlerkorrektur): exakte Matrixexponential-Fortschreibung + physikalisch
motivierte `PARAM_BOUNDS` + Mehrfachstart für `energy_balance.py`, `at_bound`-
Flag, `solve_ivp`-Gegenrechnung. Auch bereits vorhanden: die Prüfung auf
lückenlose Kalenderjahre in `fit_energy_balance_model`.

**Profile-Likelihood-Anschluss** (Milestone 47, neues Modul
`identifiability/profile_likelihood_nlp.py`): `identifiability/profile_likelihood.py`
(M20) ist bewusst auf algebraische Fälle mit höchstens einem freien
Parameter beschränkt (1D-Golden-Section) — `energy_balance.py` hat aber 5
Parameter. `profile_parameter_nlp()` verallgemeinert auf beliebig viele
freie Parameter über echte gebundene NLP-Optimierung
(`scipy.optimize.least_squares`), ruft `classify_identifiability`/
`likelihood_interval` aus M20 unverändert wieder auf (beide sind generisch
über das `Profile`-Format, unabhängig davon, wie `chi2_min` berechnet
wurde). `energy_balance.profile_energy_balance_identifiability()` wendet
das auf alle 5 Parameter an, mit einer wichtigen methodischen Korrektur
unterwegs: die rohe Fehlerquadratsumme hat keine intrinsische Skala, daher
ist ein Wilks-Schwellenwert `Δχ²=1` darauf bedeutungslos — die Funktion
normiert stattdessen mit der reduzierten-Chi-Quadrat-Rausch-Schätzung
`σ̂²=RSS_min/(n_Jahre−n_Parameter)`.

Ergebnis (±50%-Raster um den gefitteten Wert, alle Zahlen aus
`verify_energy_balance_results.json`): `C_s`, `C_d` und `alpha` sind auf
diesem Raster **praktisch nicht identifizierbar** (unbeschränktes
Konfidenzintervall) — eine strenge Bestätigung des bisher nur in Prosa
dokumentierten Befunds, nicht nur eine Behauptung. `gamma`
(untere Grenze ≈1,35, oben offen) und `T0` (obere Grenze ≈−0,0046, unten
offen) zeigen wenigstens einseitige Krümmung.

**Explizite Konvergenzdiagnose:** `EnergyBalanceFitResult` und
`ETASFitResult` weisen jetzt `optimizer_status`/`optimizer_message`
(direkt aus dem scipy-Ergebnis) sowie die tatsächlich verwendeten
Startwerte (`initial_guesses_tried`/`best_initial_guess` bzw.
`initial_guess_used`) im JSON-Bericht aus, statt nur im Docstring
behauptet zu werden.

**ETAS-Beobachtungsfenster:** `fit_etas_model(..., t_end=...)` akzeptiert
jetzt ein explizites Fensterende statt implizit die letzte Ereigniszeit —
eine Verlängerung des Fensters ohne neue Ereignisse macht sowohl die
ETAS- als auch die Poisson-Null-Log-Likelihood nachweislich schlechter
(unabhängig geprüft). Vorhistorie vor `t=0` bleibt bewusst **nicht**
modelliert — eine eigenständige, schwierigere Erweiterung (siehe unten).

**Ergebnisvertrag (bewusst leichtgewichtiger als vorgeschlagen):** statt
einer neuen gemeinsamen `EstimationContract`-Dataclass (die alle
bestehenden Fit-Ergebnisklassen umbauen würde) dokumentieren wir hier
explizit, welche bereits vorhandenen Felder welche Vertragsdimension
abdecken: `optimizer_success`≈`optimizer_converged`; `at_bound`
(Energiebilanz) und die Profile-Likelihood-Klassifikation≈
`parameters_identified`; `out_of_sample_evaluated` und
`mechanism_discriminated` sind für KEINES der drei Modelle bisher wahr
(explizit offen, siehe Paket 2). Eine vollständige gemeinsame Dataclass
bleibt ein dokumentierter, aber bewusst zurückgestellter Vorschlag.

`verify_energy_balance.py`: 5/5 bestanden (neuer Check
`profile_likelihood_identifiability`). `verify_etas.py`: 6/6 bestanden
(neuer Check `observation_window_t_end`). Dokumentiert in
`docs/energy_balance.md` und `docs/etas_earthquakes.md`.

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
