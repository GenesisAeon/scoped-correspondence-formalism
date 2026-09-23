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
| 2 | Gemeinsame zeitliche Prognoseprüfung (alle Mechanismus-Module) | ✅ erledigt |
| 3 | Probabilistische Ergebnisse (Vorhersageintervalle, Scoring-Regeln) | ✅ erledigt |
| 4 | Zwei neue Strukturbrücken (Impulsantwort; Kern/Verzweigung) | ✅ erledigt |
| 5 | Beobachtungs- und Zustandsmodelle (COVID Negativ-Binomial, Mehrländer) | ✅ erledigt |
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

## Paket 2 — Umsetzung (2026-09-21)

Astras Kernkritik: jedes neue Modell wurde bisher gegen sein EIGENES
Trainingsfenster bewertet (In-Sample-RMSE), nicht gegen dieselben Zielgrößen,
Ursprünge und Horizonte wie die anderen. `validation/rolling_origin.py`
(Paket 1 der ersten Roadmap) existiert bereits generisch — neues Modul
`validation/mechanistic_rolling_origin.py` (Milestone 48) wendet es zum
ersten Mal auf `covid_renewal.py`, `energy_balance.py` und `etas.py` an,
jeweils an die eigene Domäne angepasst (ein Punktprozess braucht eine
andere Auswertung als eine kontinuierliche Jahresreihe). Modellwahl
(Startwerte, Bounds, Fensterwahl) bleibt bei den bereits ausgelieferten
Fit-Funktionen fixiert — nichts wurde anhand der Rolling-Origin-Leistung
nachjustiert.

**Energiebilanz** (`run_energy_balance_rolling_origin_backtest`): dieselben
11 Ursprünge (1969–2019, Schritt 5) und derselbe 5-Jahres-Horizont wie
`noaa_temp_pilot.py`, plus ein neuer Prädiktor (Refit auf Kalibrierjahre,
Projektion durch reales, bereits beobachtetes CO2-Forcing). Ergebnis:
das mechanistische Modell schlägt ALLE drei Baselines (RMSE 0,1064 vs.
0,1171 last30 vs. 0,1343 expanding vs. 0,1376 Persistenz) — und zwar an
JEDEM einzelnen Vorlaufjahr (1–5), nicht nur im Mittel (neue Funktion
`rolling_origin.error_by_horizon_step`, additiv, `rolling_origin_backtest`
selbst unverändert — direkte Antwort auf Astras "Fehler getrennt nach
Horizont"-Anfrage).

**COVID-Renewal** (`run_covid_renewal_rolling_origin_backtest`): mehrere
Ursprünge im selben Januar–März-2020-Fenster, 7-Tage-Horizont. Neue
Funktion `covid_renewal.project_incidence_constant_r` (Vorwärtsprojektion
bei konstant angenommenem R, hand-geprüft: eine reine Exponentialreihe,
bei ihrem eigenen Wallinga-Lipsitch-R projiziert, setzt sich exakt als
dieselbe Exponentialreihe fort). Ergebnis: Renewal-Projektion schlägt
Persistenz (1029 vs. 5696) und einfache Exponentialextrapolation (1029
vs. 2012) deutlich.

**ETAS-Erdbeben** (`run_etas_forecast_check`): derselbe Kalibrier-/
Holdout-Split wie `earthquake_pilot.py` (2000–2019/2020–2025), ETAS-Fit
mit explizitem `t_end=2020-01-01`-Beobachtungsfenster (Paket 1), neue
Funktion `etas_expected_count_first_order` (Hintergrundrate + direkte
Auslösung aus der Kalibrier-Historie — bewusst OHNE Kaskaden neu
ausgelöster Nachbeben, siehe Docstring). **Ehrliches, nicht
nachjustiertes gemischtes Ergebnis:** ETAS schlägt die Persistenz-
Baseline hier NICHT (RMSE 26,31 vs. 22,96), schlägt aber die
Gleichraten-Poisson-Baseline (28,78). Zusätzlich: die kalibrier-nur
gefittete Verzweigungsrate liegt bei 0,854 (unterkritisch) — deutlich
anders als die 1,02 (nahe-kritisch) auf dem VOLLEN Katalog (Paket 1) —
ein weiterer Beleg für die dort bereits gefundene Fragilität dieser
Kennzahl über verschiedene Fitfenster hinweg.

`verify_mechanistic_rolling_origin.py`: 3/3 bestanden (inkl. unabhängiger
Hand-Nachrechnung eines Energiebilanz-Ursprungs durch direkten Refit+
Projektion außerhalb der privaten Prädiktor-Closure, und Integritätsprüfung
der ETAS-Holdout-Zahlen gegen `earthquake_pilot.py`s eigene dokumentierte
Werte). `verify_covid_renewal.py`: 5/5 bestanden (neuer Hand-Check für
`project_incidence_constant_r`). Dokumentiert in
`docs/mechanistic_rolling_origin.md`.

## Paket 3 — Umsetzung (2026-09-21)

Bisher lieferten alle Module nur Punktschätzungen (RMSE, AIC). Zwei neue
additive Module: `validation/scoring_rules.py` (Milestone 49: Intervall-
Score und Poisson-Log-Score, Gneiting & Raftery 2007, plus
`empirical_coverage`) und `validation/mechanistic_probabilistic_evaluation.py`
(Milestone 50: wendet das auf alle drei Paket-2-Domänen an). Neue Funktion
`rolling_origin.raw_predictions_by_horizon_step` (additiv, ergänzt
`error_by_horizon_step` um die rohen vorzeichenbehafteten Residuen, die
für Quantil-Intervalle gebraucht werden).

**Warum nicht `validation/conformal.py`?** Dessen eigene Dokumentation
nennt die Deckung bereits "marginal unter Austauschbarkeit" — aber die
Rolling-Origin-Residuen hier stammen aus ÜBERLAPPENDEN, seriell
korrelierten Kalibrierfenstern auf ausdrücklich nichtstationären Reihen,
genau der Situation, in der Austauschbarkeit keine sichere
Standardannahme ist (Astras expliziter Hinweis, Paket 3). Statt eine
nicht anwendbare Garantie überzustülpen, nutzt dieses Paket
Leave-One-Origin-Out-Quantile (kontinuierliche Ziele) bzw. ein Poisson-
Intervall (ETAS-Zähldaten), mit EMPIRISCH berichteter Deckung.

**Kernbefund: Punktgenauigkeit ≠ Intervallqualität.** Das Energiebilanz-
Modell schlägt in Paket 2 jede Baseline bei der Punktprognose — sauber
bewertet kehrt sich das um: sein Intervall-Score (0,4665) ist der
SCHLECHTESTE aller vier Prädiktoren (Persistenz 0,4076, expanding 0,4382,
last30 0,4211). Kein Widerspruch, sondern genau das, wofür echte
Scoring-Regeln da sind: ein Modell kann im Mittel genauer sein und
trotzdem eine weniger effiziente Unsicherheitsschätzung haben. Bei COVID
stimmen beide Rankings dagegen überein (`renewal_constant_R` gewinnt
RMSE UND Intervall-Score, 3796 vs. 9052/20241). Bei ETAS bestätigt der
Poisson-Log-Score ebenfalls Paket 2s Befund: Persistenz gewinnt (5,356
vs. 6,131/6,360), keine Nachjustierung.

**Ehrlicher Kleinstichproben-Hinweis:** Leave-One-Origin-Out-Quantile
nutzen nur 10 (Energiebilanz) bzw. 5 (COVID) andere Ursprünge je
Vorlaufzeit — dünne Dezile, explizit als exploratorisch ausgewiesen, nicht
als belastbare Schwanzquantile.

`verify_mechanistic_probabilistic_evaluation.py`: 5/5 bestanden
(Hand-Nachrechnung von `interval_score`/`poisson_log_score`/
`poisson_prediction_interval` direkt gegen scipy, unabhängige
Hand-Nachrechnung eines Leave-One-Origin-Out-Intervalls an einem
synthetischen Beispiel, alle drei Domänen). Dokumentiert in
`docs/mechanistic_probabilistic_evaluation.md`.

## Paket 4 — Umsetzung (2026-09-21)

Astras eigene mathematische Beobachtung (Abschnitt "Die mathematisch
ergiebigste neue Verbindung"): mehrere neue Module verarbeiten eine
Vorgeschichte mit einem zeitlichen Kern — eine präzise strukturelle
Verwandtschaft, dokumentiert im bestehenden Bridge-Card-Schema aus
`docs/structural_relations.md` (Quelle/Ziel, Kernabbildung, Skalierung,
erhaltene Größe, Gegenbeispiel bei verletzten Voraussetzungen — wie
B1/B2), NICHT als vorschnelle gemeinsame Kernel-API. Zwei neue Brücken
(B7, B8, Nummerierung von B1/B2 fortgesetzt — B3-B6 bleiben für das
ursprüngliche Konzeptdokument reserviert), beide OHNE neues
Produktionsmodul, nur mit bereits vorhandenen Repo-APIs:

**B7 — Impulsantwort-Systeme: Energiebilanz ↔ Puffer.** Für das
Energiebilanzmodell hat die Zustandsmatrix A zwei reelle, negative
Eigenwerte (kein gedämpftes Schwingen) — Zeitskalen ≈3,64 Jahre (schnell,
Oberfläche) und ≈274 Jahre (langsam, Tiefsee), ein 75-facher Abstand,
exakt geprüft statt nur behauptet. Die Übertragungsfunktion
`G(s)=C(sI-A)⁻¹B` stimmt mit Astras Formel
`(C_d·s+γ)/((C_s·s+α+γ)(C_d·s+γ)-γ²)` auf Maschinengenauigkeit überein
(vier getestete s-Werte). Beide Modelle werden unabhängig über direkte
Faltung (Homogenlösung + numerische Quadratur, NICHT erneuter Aufruf von
`solve_ivp`/`scipy.linalg.expm`) rekonstruiert und stimmen mit den
Produktionsfunktionen auf `1e-6`–`1e-11` überein. **Gegenbeispiel:** eine
zeitveränderliche Relaxationsrate im Puffer bricht die
Faltungsdarstellung um das ~1000-fache stärker als die
Übereinstimmungsgenauigkeit oben (0,101 vs. `1e-6`–`1e-11`) — bestätigt,
dass die Brücke echte Zeitinvarianz braucht, nicht nur "irgendein linear
aussehendes System."

**B8 — Positive Kerne / Verzweigungsoperatoren: COVID-Renewal ↔
ETAS-Hawkes.** Bei konstantem R ist die Renewal-Rekursion exakt ein
stationärer linearer Hawkes-Prozess mit Reproduktionskern `R·w_s`; dessen
Gesamtmasse ist exakt R (geprüft: `Σw_s=1`, `R·Σw_s=R` für R=1,68).
Nach Hawkes & Oakes (1974) IST diese Gesamtmasse die erwartete Zahl
direkter Nachkommen — R selbst ist also die Verzweigungsrate, berechnet
nach demselben allgemeinen Prinzip wie `etas_branching_ratio` für den
strukturell anderen Omori-Utsu-Kern. Rückwärts-Konsistenzprüfung über
`wallinga_lipsitch_r` bestätigt das Roundtrip auf `1e-9`.
**Gegenbeispiele (durch Verweis auf bereits verifizierte Ergebnisse,
nicht neu berechnet):** echtes R_t ist NICHT konstant (fällt unter 1,
steigt über 1,5 im selben Fenster) — genau deshalb musste
`project_incidence_constant_r` (Paket 2) konstantes R annehmen, dessen
Prognosefehler sind die sichtbaren Kosten davon. ETAS' eigene
Verzweigungsrate ist aus einem STRUKTURELL ANDEREN Grund fragil (nur
~30 % der Kernmasse innerhalb der Kataloglänge, Paket 1) — dieselbe Art
Größe scheitert aus verschiedenen Gründen.

`verify_structural_bridges_b7_b8.py`: 2/2 bestanden. Dokumentiert als
neue Abschnitte B7/B8 in `docs/structural_relations.md` (fortlaufende
Bridge-Card-Schema-Anwendung), verlinkt aus `docs/energy_balance.md`,
`docs/rate_dependent_tipping.md`, `docs/covid_renewal.md` und
`docs/etas_earthquakes.md`.

## Paket 5 — Umsetzung (2026-09-22)

Vier Teile, wie von Astra angefragt:

**Teil A — COVID-Beobachtungsmodell** (`validation/covid_observation_model.py`,
Milestone 52): echte tägliche Rohzahlen (`new_cases`, nicht `cases_7day_avg`)
als Zählmodell-Eingabe. `cases_7day_avg` dient als gegebener Referenzmittelwert
μ_t (bewusst NICHT selbst modelliert — ein vollständiges Latent-State-
/Beobachtungsprozess-Modell wäre ein größeres, zurückgestelltes Vorhaben).
Neue Funktionen in `scoring_rules.py` (Milestone 49, erweitert):
`neg_binom_log_score`/`fit_neg_binom_dispersion` (NB2-Parametrisierung).
Dispersion wird auf einer Kalibrierhälfte des Fensters gefittet und auf
der disjunkten Holdout-Hälfte bewertet (kein Zirkelschluss). **Ergebnis:
deutliche, nicht nur marginale Überdispersion** — mittlerer Poisson-
Log-Score 944,5 vs. Negativ-Binomial-Log-Score 9,71 (Faktor ~100),
gefittete Dispersion α=0,539. Physikalisch plausibel: rohe Tageszahlen
tragen starke Wochentags-Meldeartefakte, die `cases_7day_avg` per
Konstruktion glättet.

**Teil B — Mehrländer/Mehrfenster** (`validation/covid_multi_country.py`,
Milestone 51): `covid_pilot.py`s Exponentialwachstums-Prozedur
UNVERÄNDERT auf Deutschland und die USA über Pilot As exaktes
Original-Fenster angewendet — neue echte Daten frisch geladen
(`data/owid_covid_germany_usa_daily_2020.csv`, sha256 in
`data/real_data_manifest.json`). **Beide Fits scheitern korrekt** (ein
Null-Tageswert in beiden Kalibrierfenstern, für die der Log-linear-Fit
undefiniert ist) — ein ehrlicher, informativer Befund: einzelne Länder
haben in der frühesten Phase Null-/Beinahe-Null-Tage, die das
Weltaggregat wegglättet; kein Bug, keine stillschweigende Fensteranpassung
pro Land. Zusätzlich dasselbe Verfahren auf das Weltaggregat in einem
NEUEN, unabhängigen Zeitfenster angewendet (verankert an der WHO-Omikron-
VOC-Einstufung 2021-11-26, dieselbe Kalibrier-/Holdout-Länge wie Pilot A):
**dieser Fit gelingt und schlägt die Baseline** (RMSE 19181 vs. 42841).

**Teil C — Energiebilanz, vollständiges Forcing** (`validation/energy_balance_full_forcing.py`,
Milestone 53): echte Daten aus "Indicators of Global Climate Change 2025"
(Forster, Smith, Walsh, Gillett et al., DOI 10.5281/zenodo.7883757, Git-Tag
`v2026.06.02` — derselbe Stand wie in Astras Zitat), frisch geladen
(`data/climateindicator_erf_best_aggregates_1750_2025.csv`). Nutzt
`fit_energy_balance_model_from_series` UNVERÄNDERT mit drei verschiedenen
echten Forcing-Eingaben. Gegenprüfung: die beiden unabhängig ermittelten
CO2-only-Forcing-Reihen (dieser Datensatz vs. Myhre-Formel aus Mauna-Loa-
Konzentrationen) stimmen nach Referenzierung auf dasselbe Basisjahr gut
überein (max. Abweichung 0,056 W/m² über 67 Jahre). **Ursprüngliches
Ergebnis:** reales Gesamtforcing verbessert den Fit gegenüber CO2-only
spürbar, aber nicht dramatisch (RMSE 0,0879 vs. 0,0938/0,0904).
**Korrektur (Paket 7, siehe unten):** dieses Ranking erwies sich als nicht
robust gegenüber der Referenzniveau-Wahl der drei Forcing-Reihen und
kehrt sich unter konsistenter Referenzierung um.

`verify_covid_observation_model.py`: 3/3 bestanden.
`verify_covid_multi_country.py`: 4/4 bestanden.
`verify_energy_balance_full_forcing.py`: 3/3 bestanden.
`verify_real_data_provenance.py`: 8/8 bestanden (zwei neue Datensätze).
Dokumentiert in `docs/covid_observation_model.md`,
`docs/covid_multi_country.md` und einem neuen Abschnitt in
`docs/energy_balance.md`.

## Paket 7 — Astra-Review-Korrekturen (Commit `3e8dce3`, 2026-09-23)

Antwort auf `prompts/Answers/nicht_stationäre_Treiber/SCF_Review_3e8dce3.md`
(Astra, Review des Pakets-5-Commits). Fünf Befunde, alle unabhängig am
Code nachgeprüft (nicht nur der Review vertraut) und behoben:

1. **Data-Leakage in Prognoseintervallen** (hoch, `mechanistic_probabilistic_evaluation.py`,
   `leave_one_origin_out_intervals`): Kalibrierungsresiduen stammten aus
   ALLEN anderen Ursprüngen, auch späteren. Astras Gegenbeispiel
   reproduziert: ein früheres Intervall `[1,2; 2,8]` wurde durch Ändern
   nur des letzten Ursprungs zu `[1,2; 80,4]`. **Fix:** neuer
   Pflichtparameter `step_size`, Kalibrierung nur noch aus Ursprüngen mit
   bereits verfügbarer Zielbeobachtung (`origin' + step*step_size <=
   origin`); Versuche mit zu wenig Vorgeschichte werden jetzt explizit als
   `skipped_trials` (Grund `insufficient_lookback`) ausgewiesen statt die
   ganze Auswertung abzubrechen oder die Lücke zu verschleiern. Neuer
   zentraler Regressionstest exakt nach Astras Vorschlag: „Spätere Daten
   dürfen frühere Prognosen nicht verändern." Ergebnis: Energiebilanz
   40/55, COVID-Renewal 19/42 zeitlich zulässige Versuche (Rest ehrlich
   als „nicht genug Vorgeschichte" markiert, nicht stillschweigend
   fallengelassen).
2. **Zirkulärer COVID-Referenzmittelwert** (hoch, `covid_observation_model.py`):
   `predicted_mean` (`cases_7day_avg`) enthielt den eigenen Zielwert.
   Astras Gegenbeispiel (12.3.2020, +700 Tageszählung → Referenzmittelwert
   +100) reproduziert. **Fix:** neue vorwärtsgerichtete Referenzgröße
   `_lagged_means` (7-Tage-Mittel ausschließlich aus den Tagen VOR dem
   bewerteten Tag). Ergebnis überlebt die Korrektur und wird sogar
   deutlicher: Poisson-Fehlanpassung 1692,76 (vorher 944,5, da der
   zirkuläre Mittelwert Poisson künstlich begünstigte),
   Negativ-Binomial-Score bleibt bei ~9,95 — die Überdispersion ist jetzt
   auf einer echt zirkelfreien Basis bestätigt. Alte
   `cases_7day_avg`-Variante bleibt als explizit „retrospektiv, deskriptiv"
   gekennzeichneter Vergleichswert erhalten.
3. **B8-Stationaritätsbehauptung mathematisch falsch** (hoch für den
   Formalismus, `docs/structural_relations.md`): die Kernmassen-Identität
   (`R * Σw = R`) ist korrekt und braucht keine Stationarität; die
   ZUSÄTZLICHE Behauptung, konstantes `R` mache die Rekursion zu einem
   „stationären" Hawkes-Prozess, ist falsch. `R=1,68` ist superkritisch
   (`n>1`); mit `μ=1` ergibt die Stationaritätsformel `μ/(1-n) ≈ -1,47`,
   eine unmögliche negative Rate. **Fix:** Behauptung entfernt/korrigiert,
   subkritisches Gegenbeispiel `R=0,8` (Mittel `5,0`, korrekt stationär)
   und `R=1,68` explizit als Gegenbeispiel zur Stationarität (nicht als
   Beleg dafür) ergänzt, in Doku und `verify_structural_bridges_b7_b8.py`.
4. **Offenes Scan-Ende ≠ bewiesene Unbeschränktheit** (mittel,
   `docs/energy_balance.md`): die Identifizierbarkeits-Tabelle nannte
   `C_s`, `C_d`, `alpha` „unbounded (fully flat — practically
   unidentified)". Direkt nachgeprüft: `classify_identifiability`
   klassifiziert alle fünf Parameter tatsächlich als `"identifiable"`
   (gekrümmt, nicht flach); `likelihood_interval`s `unbounded_reason` ist
   für alle fünf `"open_at_grid_boundary"` — das Intervallende liegt
   außerhalb des gescannten ±50%-Fensters, nicht: es existiert nicht.
   **Fix:** Tabelle und Interpretation in `docs/energy_balance.md` sowie
   die zugehörigen Prüf-/Interpretationstexte in
   `verify_energy_balance.py` korrigiert auf „innerhalb des ±50%-Fensters
   nicht eingegrenzt", mit explizitem Verweis auf die tatsächliche
   Klassifikation.
5. **Inkonsistente Forcing-Referenzniveaus** (Klimavergleich,
   `energy_balance_full_forcing.py`): der Cross-Check glich Referenzniveaus
   an, die drei eigentlichen Fits erhielten aber die unangeglichenen
   Reihen. Astras Sensitivitätsprüfung reproduziert: unter konsistenter
   Referenzierung (alle drei Reihen auf `F=0` im ersten Überlappungsjahr)
   **kehrt sich die Rangfolge um** — CO2-only schlägt dann Gesamtforcing
   (0,0902 vs. 0,0943), statt umgekehrt (0,0879 vs. 0,0938 in der
   ursprünglichen, nicht angeglichenen Fassung). **Fix:** beide Varianten
   (`_raw_reference` und `_rereferenced`) werden jetzt parallel berechnet
   und berichtet; `verify_energy_balance_full_forcing.py` prüft explizit,
   dass die beiden Konventionen aktuell widersprechen, statt eine
   Richtung als Tatsache zu behaupten. Keine vollständige physikalische
   Neuinitialisierung (bräuchte einen explizit modellierten
   Forcing-/Beobachtungsoffset) — als Folgearbeit vermerkt, nicht verdeckt.

Alle fünf Fixes einzeln mit `verify_mechanistic_probabilistic_evaluation.py`
(5/5), `verify_covid_observation_model.py` (3/3),
`verify_structural_bridges_b7_b8.py` (2/2), `verify_energy_balance.py`
(5/5) und `verify_energy_balance_full_forcing.py` (3/3) bestätigt; volle
Suiten-Regression (`audit_review/run_all_local.py`) am selben Tag
gefahren.

## Paket 6 — Mehrdimensionale R-Tipping-/Viabilitätskarten ✅ erledigt (2026-09-23)

Erweitert Paket 3/4 der ersten Roadmap (bereits mit der
Gleichlast-Gegenkontrolle in Commit `20efc63` begonnen) und schließt den
in `docs/rate_dependent_tipping.md` offen benannten Punkt ("A full
characterization would need a response surface over amplitude AND
duration jointly").

Neues Modul `viability/multidim_tipping_maps.py` (Milestone 54), setzt
`viability/rate_dependent_buffer.py` und `dynamics/rate_dependent.py`
UNVERÄNDERT zu echten 2D-Antwortflächen zusammen, mit fünf statt zwei
Ergebniszuständen (`tracking`, `switched`, `unresolved`, `out_of_scope`,
`integration_error` — genau Astras geforderte Kategorien):

- **`buffer_response_surface`**: reproduziert beide bekannten 1D-Tabellen
  (gleiche Spitzenlast, gleiche integrierte Last) exakt als
  Einzel-Spalten-Schnitte derselben Funktion, dann echt mehrdimensional.
- **Reserve-Achse fast geschenkt:** `b` kommt in der Puffer-ODE gar nicht
  vor, nur im Grenzwertvergleich danach — die kritische Reserve ist daher
  exakt `critical_b = z_min` derselben einen Trajektorie, ohne
  Nachintegration oder Nullstellensuche (`buffer_reserve_frontier`).
  `out_of_scope` echt ausgelöst (nicht nur defensiv programmiert) durch
  eine Grenze oberhalb der frozen-sicheren Basislast.
- **`tracking_response_surface`** (kubisches Beispiel): `x0_offset` als
  echte zweite (Reserve-)Achse neben der Rate `r`. Ehrliches Nullresultat
  bei der Standard-Vorlaufzeit `margin=10` (Achse wirkt sich gar nicht
  aus — das System vergisst seinen Startpunkt vollständig, bevor der
  eigentliche Treiber sich bewegt), aber echter, gemessener Effekt bei
  kürzerer Vorlaufzeit `margin=3` nahe der kritischen Rate — inklusive
  eines echten, nicht konstruierten `unresolved`-Falls (r=0,75,
  x0_offset=0,6: Trajektorie hat sich bis t1 nicht innerhalb der Toleranz
  eingependelt).
- **Bewusst offen gelassen:** globale Schwellengeometrie (Kanten-Zustände,
  verbindende Orbits, Wieczorek/Xie/Ashwin 2023) für eine bewiesene
  globale Charakterisierung statt empirisch bestimmter Gitter-Grenzen;
  `integration_error` ist defensiv programmiert, aber in keinem
  getesteten Gitter tatsächlich ausgelöst (ein echter Solver-Fehler war
  nur über eine pathologisch langsame, fast hängende Parameterkombination
  reproduzierbar — bewusst nicht als Testfall übernommen); Astras
  zeitabhängige-Wirkungskerne-Erweiterung bleibt dokumentierter
  Ausbauvorschlag, nicht implementiert.

`verify_multidim_tipping_maps.py`: 6/6 bestanden. Dokumentiert in einem
neuen Abschnitt in `docs/rate_dependent_tipping.md`.

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
