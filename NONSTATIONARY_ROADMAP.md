# Nichtstationäre Treiber / Kippen — Roadmap (2026-09-21)

Antwort auf `prompts/Answers/nicht_stationäre_Treiber/SCF_Nichtstationaere_Treiber_und_Kippen.md`
(Astra, 2026-09-21) — unabhängig nachvollzogen (siehe Commit `9e75897`,
alle Kernzahlen bis auf Gleitkomma-Rauschen reproduziert, zwei eigene
Dokufehler gefunden und korrigiert). Johanns Auftrag (2026-09-21):
"lass uns das gern als Roadmap Punkt für Punkt abarbeiten."

Reihenfolge übernimmt Astras Priorisierung (Abschnitt 8 der Quelldatei).
Bestehende Pilotresultate (Cygnus, COVID A/B/C, NOAA, Erdbeben) werden
durch neue Pakete **ergänzt, nicht überschrieben** — gleiche Disziplin wie
bei der Audit-Roadmap.

| # | Paket | Status |
|---|---|---|
| 1 | Gemeinsame rollierende Auswertung + adaptive einfache Modelle | ✅ erledigt (NOAA) |
| 2 | COVID-Heterogenität: Länder statt Weltmittel; Beobachtungsmodell trennen | ✅ erledigt |
| 3 | Treiber-abhängige Dynamik-Schnittstelle (eingefrorene Stabilität vs. echte Trajektorie) | ✅ erledigt |
| 4 | Raten-/Viabilitäts-Kontrollfälle | ✅ erledigt |
| 5 | Je Domäne ein mechanistisches Modell (COVID-Renewal, Energiebilanz-Klima, ETAS-Erdbeben) | ✅ erledigt |

### Paket 1 — Umsetzung (2026-09-21)

`src/scoped_correspondence/validation/rolling_origin.py`: generische,
wiederverwendbare `rolling_origin_backtest(x, y, origins, horizon,
predictors)`-Funktion (Milestone 6e). Angewendet auf NOAA
(`run_noaa_rolling_origin_backtest` in `noaa_temp_pilot.py`): 11 Ursprünge
1969–2019, 5-Jahres-Horizont, drei Prädiktoren (Persistenz, expandierendes
Fenster, letzte 30 Jahre) — jeder Prädiktor sieht nur Daten bis zum
jeweiligen Ursprung. Alle 11×3 Einzelwerte und die 3 gepoolten RMSE-Werte
gegen Astras unabhängig berechnete Zahlen exakt abgeglichen (0 Abweichung
über Gleitkomma-Rauschen hinaus). `verify_rolling_origin.py`: 4/4 bestanden
(Scope-Verletzungen, Hand-Rechnung an einer synthetischen Reihe, voller
Abgleich gegen Astras 11 Ursprünge, unabhängige Handrechnung für
Ursprung=1999). Ergebnis: das letzte-30-Jahre-Fenster gewinnt insgesamt
deutlich (RMSE 0,119 vs. 0,138 Persistenz vs. 0,265 expandierend), aber
nicht an jedem einzelnen Ursprung — dokumentiert in
`docs/noaa_temp_pilot.md`. COVID/Erdbeben folgen als eigene Anwendung
dieser gemeinsamen Infrastruktur, sobald sinnvoll (nicht Teil von Paket 1
selbst, das die Infrastruktur + eine erste Anwendung liefert).

### Paket 2 — Umsetzung (2026-09-21)

`src/scoped_correspondence/validation/covid_country_decomposition.py`
(Milestone 6f): echte China- und Weltdaten frisch von derselben
OWID/JHU-Primärquelle geladen (`data/owid_covid_china_world_daily_2020.csv`,
Herkunft in `data/real_data_manifest.json`), RestOfWorld = World − China
exakt berechnet, nicht separat geladen. Chinas Anteil an den
Weltfallzahlen fällt real von 98,49 % (28.1.) auf 0,12 % (25.3.) — die
dokumentierte Verlagerung des Pandemiezentrums. China (r=−0,0712/Tag,
fallend) und RestOfWorld (r=+0,1459/Tag) getrennt auf demselben
Kalibrierfenster wie Pilot A gefittet, getrennt in den Holdout
extrapoliert und summiert: RMSE 6668,83 gegenüber 17686,65 (Aggregatfit,
gleiches Fenster) und 15932,68 (Persistenz) — schlägt beide deutlich.
Bestätigt Astras Mischungsidentität (Abschnitt 4) direkt an echten Daten:
wechselnde Länderzusammensetzung erklärt einen erheblichen Teil der
scheinbaren Weltraten-Beschleunigung, unabhängig von echten
Ratenänderungen innerhalb der Komponenten. Die Mischungsraten-Diagnose
`mixture_effective_rate_diagnostic()` zeigt zusätzlich: die
Zusammensetzungs-Erklärung trägt gut ab Ende Februar, aber nicht für den
frühen Ratensprung um den 19./20. Februar, der mit Chinas dokumentierter
Fallzähl-Definitionsänderung vom 12./13. Februar zusammenfällt (PAHO/WHO,
Referenz R1 in Astras Bericht) — ein Meldeartefakt, keine
Kompositions- oder echte Ratenänderung.

`verify_covid_country_decomposition.py`: 5/5 bestanden (Lader-Scope-
Verletzungen, Komponentenraten-Vorzeichen + Dekompositions-Sieg,
Hand-Nachrechnung aller drei RMSE-Werte direkt aus der CSV, Hand-
Nachrechnung der Mischungsraten-Diagnose an drei Stichtagen, exakte
Kompositions-Kopfzahlen). Pilot A/B/C bleiben unverändert; dies ist Pilot
D, dokumentiert in `docs/covid_pilot.md`.

### Paket 3 — Umsetzung (2026-09-21)

`src/scoped_correspondence/dynamics/rate_dependent.py` (Milestone 42):
neue, bewusst getrennte Schnittstelle für eingefrorene (quasistatische)
Stabilität (`frozen_equilibria_shifted_pitchfork`) versus echte
Trajektorienintegration eines nichtautonomen Systems
(`integrate_trajectory`, `scipy.integrate.solve_ivp`) plus Klassifikation
(`classify_tracking`). Astras Kanonisches Kontrollbeispiel reproduziert:
`ẋ=(x−u)−(x−u)³`, `u(t)=1+tanh(rt)` — eingefrorene Gleichgewichte `x=u`
(instabil, Ableitung +1) und `x=u±1` (stabil, Ableitung −2), unabhängig
von `u`: keine eingefrorene Bifurkation entlang irgendeines Treiberwegs.
Bei `r=0,1` (langsam) verfolgt die Trajektorie den oberen Zweig
(`x−u→+1`); bei `r=2` (schnell) wechselt sie zum unteren (`x−u→−1`) —
beide Ergebnisse einschließlich der Integrations-Verfeinerungsdifferenzen
(1,487×10⁻¹⁰ bzw. 1,364×10⁻⁸) exakt (Ziffer für Ziffer) gegen Astras
Zahlen abgeglichen. Ein zusätzlicher Raten-Sweep (r=0,05 bis 5) zeigt: das
Verfolgen scheitert erst oberhalb einer kritischen Rate zwischen 0,5 und
1,0 — ein echter Ratenffekt, kein Zufallsergebnis.

`verify_rate_dependent.py`: 4/4 bestanden (Hand-Herleitung der
eingefrorenen Gleichgewichte, Scope-Verletzungen von
`integrate_trajectory`/`classify_tracking`, exakte Reproduktion von
Astras Zahlen, Monotonie-Check des Raten-Sweeps). `dynamics/core.py`,
`gspt.py`, `panarchy_cusp.py` und `early_warning.py` bleiben unverändert
— dieses Modul beantwortet eine andere Frage als deren quasistatische
Werkzeuge. Dokumentiert in `docs/rate_dependent_tipping.md`.

### Paket 4 — Umsetzung (2026-09-21)

Zwei Teile, wie von Astra angefragt ("der oben gerechnete Fall sowie ein
Pufferfall"):

**Teil A — χ-Diagnose** (`dynamics/rate_dependent.py`, erweitert):
`local_chi_diagnostic()` implementiert Astras Formel χ=|D_u x*·u̇|/(κ·d_Grenze)
generisch. Für das kanonische Beispiel aus Paket 3 sind D_u x*=1 und der
Abstand stabiler↔instabiler Zweig=1 exakte Konstanten, also
χ_max=r/2 in geschlossener Form. `chi_diagnostic_for_cubic_example(r)`
zeigt: χ steigt monoton mit der Rate und sagt die Richtung des
Kipp-Verhaltens über den gesamten getesteten Bereich (r=0,05 bis 5)
korrekt voraus. **Korrektur (2026-09-21, externe Zweitprüfung durch
Astra):** die ursprünglich genannte präzise Schwelle χ_max≥0,5 war nur
grob durch das ursprüngliche Punktraster eingegrenzt (r=0,5→χ=0,25→Nein
vs. r=1,0→χ=0,5→Ja); ein feineres, unabhängig nachgerechnetes Raster
zeigt den tatsächlichen Übergang zwischen r=0,7 (χ=0,35, Nein) und r=0,8
(χ=0,40, Ja) — nicht bei 0,5. χ bleibt ein korrekt gerichteter lokaler
Indikator, aber kein bewiesener präziser Schwellenwert. Details in
`docs/rate_dependent_tipping.md`.

**Teil B — Puffer-Lastspitzenfall** (neues Modul
`viability/rate_dependent_buffer.py`, Milestone 43): dasselbe Skalar-
Puffermodell wie `viability/core.has_safe_transfer`, jetzt mit echt
zeitveränderlicher Last W(t) = W0 + Spitzenhöhe·exp(-(t/τ)²) — gleiche
Last vor und nach der Spitze, eingefrorener Zustand an der Basislast
sicher, eingefrorener Zustand am Spitzenwert absichtlich unsicher. Das
**Spiegelbild-Ergebnis** zu Paket 3: schnellere (kürzere) Spitzen sind
hier SICHERER, nicht gefährlicher — der Puffer wirkt wie ein Tiefpassfilter
und dämpft kurze Störungen, bevor sie den eingefrorenen Extremwert
erreichen. Erst Spitzen, die lang genug relativ zur Relaxationsrate r
sind, lassen den Puffer nahe an den eingefrorenen schlimmsten Fall
herankommen. Zusätzlich die Reserve-Dimension bei fester Spitzenbreite:
schärfere Sicherheitsschwelle b bricht, großzügigere nicht — scharfer
Übergang exakt am Trajektorienminimum. χ ist hier bewusst NICHT
anwendbar (setzt voraus, dass der eingefrorene Pfad die Grenze nie
überschreitet) — als expliziter Scope-Hinweis dokumentiert.

`verify_rate_viability_control_cases.py`: 5/5 bestanden (χ-Korrelation
mit dem Kippverhalten, Tempo-Dimension mit unabhängiger Hand-
Nachintegration, Reserve-Dimension, Gleichlast-Gegenfall, Scope-
Verletzungen). `has_safe_transfer` wird nur aufgerufen, nicht verändert.

**Korrektur (2026-09-21, externe Zweitprüfung durch Astra):** das
"schnellere Spitzen sind sicherer"-Ergebnis gilt nur bei FESTER
Spitzenhöhe — dabei sinkt mit kürzerem τ auch die insgesamt gelieferte
Zusatzlast (das Integral der Gaußspitze, Höhe·√π·τ). Bei stattdessen
FESTER Gesamtlast (`equal_total_load_height`, neue Funktion in
`rate_dependent_buffer.py`) kehrt sich die Aussage um: kürzere Spitzen
sind hier GEFÄHRLICHER, da dieselbe Gesamtlast in kürzerer Zeit
konzentriert wird und den Puffer überfordert, bevor er reagieren kann.
Keine der beiden Aussagen ist falsch — sie beantworten unterschiedliche
Fragen (spitzenwert- vs. gesamtenergiebegrenzte Störung); eine einzelne
"schneller ist sicherer/gefährlicher"-Aussage ohne Angabe der
Randbedingung ist nicht identifiziert. Details in
`docs/rate_dependent_tipping.md`.

### Paket 5 — Umsetzung (2026-09-21)

Drei Teile, wie von Astra in Abschnitt 5.4 vorgeschlagen — je Domäne ein
echtes mechanistisches Modell statt eines bloßen Trend-/Konstantratenfits:

**Teil A — COVID-Renewal** (`validation/covid_renewal.py`, Milestone 44):
Cori-et-al.-2013-Renewal-Gleichung `Λ_t=Σ_s w_s·I_{t−s}`, `R_t=I_t/Λ_t`,
Generationsintervall als Gamma-Verteilung diskretisiert (Nishiura, Linton
& Akhmetzhanov 2020: Mittel 4,7 Tage, SD 2,9 Tage) — auf den echten
Welt-COVID-Daten (dieselbe Quelle wie Pilot A). Selbstkonsistenz-Check:
ein rein exponentieller Verlauf liefert eine KONSTANTE `instantaneous_r`,
die exakt mit der Wallinga-&-Lipsitch-(2007)-Umrechnung
`R=1/Σ_s w_s·e^{−rs}` übereinstimmt (auf 1e-8). Am echten Datensatz fällt
`R_t` Ende Februar 2020 unter 1 und steigt Mitte März auf 1,5–1,9 — Pilot
As gefittete Rate (0,00744/Tag) entspricht `R≈1,036`, Pilot Bs Rate
(0,1210/Tag) entspricht `R≈1,680`, beide konsistent mit dem direkt
berechneten März-`R_t`-Bereich. `verify_covid_renewal.py`: 4/4 bestanden.
Dokumentiert in `docs/covid_renewal.md`.

**Teil B — Energiebilanz-Klima** (`dynamics/energy_balance.py`, Milestone
45): Zweischichten-Energiebilanzmodell (Geoffroy et al. 2013),
CO2-Strahlungsantrieb `F=5,35·ln(CO2/CO2_ref)` (Myhre et al. 1998) mit
echten Mauna-Loa-CO2-Jahresmitteln (neu geladen,
`data/noaa_mauna_loa_co2_annual_1959_2025.txt`, NOAA GML, sha256 in
`data/real_data_manifest.json`). `verify_energy_balance.py`: 4/4 bestanden.
Dokumentiert in `docs/energy_balance.md`.

**Korrektur (2026-09-21, externe Zweitprüfung durch Astra):** der zuerst
gemeldete Fit (RMSE 0,154 °C, unbeschränktes `least_squares(method="lm")`
ab 4 Startwerten) erwies sich als schlecht konvergiertes lokales Optimum
— derselbe unveränderte Code konvergierte in einer anderen Umgebung
(neueres scipy/numpy) ab denselben Startwerten auf RMSE 0,119 °C, eine
gründlichere Suche erreichte RMSE ~0,090 °C. Behoben durch (a) exakte
Matrixexponential-Fortschreibung derselben linearen ODE statt
`solve_ivp` im Optimierer-Kern (unabhängig gegen `solve_ivp` rückbestätigt,
maximale Abweichung 8,1·10⁻⁸ °C — dieselbe Physik, kein anderes Modell)
und (b) explizite, physikalisch motivierte Parametergrenzen
(`PARAM_BOUNDS`) plus mehrere verschiedene Startwerte, die jetzt
zuverlässig zum selben Optimum konvergieren (RMSE 0,0904 °C). **Der
eigentliche ehrliche Befund ist nicht die bessere RMSE, sondern dass
`alpha` selbst unter dieser physikalisch motivierten unteren Grenze
(0,3 W/m²/K) exakt an dieser Grenze landet** — ein unbeschränkter Refit
(nur als externe Diagnose gerechnet, nicht ausgeliefert) läuft sogar bis
`alpha≈4,5·10⁻⁵` (praktisch keine Strahlungsrückkopplung), ein klassisches
Überanpassungs-/Identifizierbarkeitsartefakt, kein besseres Klimamodell.
Die ursprünglich berichtete "Aerosol-Unmasking"-Asymmetrie (+0,10 °C früh
vs. +0,24 °C spät) schrumpft unter dem korrigierten Fit um etwa eine
Größenordnung (-0,009 °C vs. +0,026 °C) und wird hiermit **zurückgezogen**
— sie war größtenteils ein Artefakt der schlechten Konvergenz, nicht in
erster Linie ein reales physikalisches Signal. Zusätzlich dokumentiert:
`F` bezieht sich auf CO2 von 1959, die Temperaturreihe auf den Mittelwert
1901–2000 — zwei unterschiedliche Referenzniveaus, bewusst nicht durch
einen sechsten freien Parameter aufgelöst, angesichts der bereits
dokumentierten schwachen Identifizierbarkeit. Details in
`docs/energy_balance.md`.

**Teil C — ETAS-Erdbeben** (`dynamics/etas.py`, Milestone 46): Ogata-1988-
Selbsterregungs-Punktprozess `λ(t|H_t)=μ+Σ_{t_i<t} K·exp(α(M_i−M0))/(t−t_i+c)^p`
auf demselben USGS-M≥6,0-Katalog wie `docs/earthquake_pilot.md` (kein
neuer Datensatz nötig). Direkter Test der dort bereits gefundenen
Überdispersion (Fano-Faktor 3,16, D=60,01 auf 19 Freiheitsgraden,
p≈3,85e-6 gegen eine Gleichraten-Poisson-Nullhypothese): der ETAS-Fit
schlägt diese Nullhypothese deutlich (AIC-Lücke ≈1304). Zwei ehrliche
Nebenbefunde: `p` konvergiert auf ≈1,02 (sehr langsam abklingender, fast
logarithmischer Kern) — plausibel ein Mischungsartefakt des global
gepoolten Katalogs (viele Regionen mit unterschiedlichen, typischerweise
schnelleren Einzelraten summieren sich zu einem scheinbar langsameren
Populationsverlauf) — und die Verzweigungsrate liegt bei ≈1,02, also
genau an der Kritikalitätsschwelle. Aus Performancegründen (exakte
O(N²)-Likelihood, N=3974) nutzt der Standardfit einen einzelnen,
physikalisch motivierten Startpunkt statt Astras/`energy_balance.py`s
Mehrfachstart-Schema — unabhängig getestet über 140/250/~1400
Optimierungsschritte, alle innerhalb von 0,3 Nats desselben Optimums
(Basin stabil, keine Artefakte des Zeitbudgets). `verify_etas.py`: 4/4
bestanden (Hand-Nachrechnung des Kompensators gegen `scipy.integrate.quad`,
unabhängige Doppelschleifen-Nachrechnung der Log-Likelihood an einem
synthetischen Katalog, geschlossene Poisson-Null-Formel, echter
Katalog-Fit). Dokumentiert in `docs/etas_earthquakes.md`, verlinkt aus
`docs/earthquake_pilot.md`.

**Korrektur (2026-09-21, externe Zweitprüfung durch Astra):** die
Verzweigungsrate ist fragiler als oben dargestellt. Ihr Kernzeitintegral
läuft bis unendlich; beim gefitteten p=1,0249 liegen nur ≈30,0 % dieser
Masse innerhalb der Kataloglänge von 9756 Tagen — der Rest stammt aus
einem weit über die Daten hinaus extrapolierten Ausläufer. Eine reine
Sensitivitätsrechnung (nur p verändert, übrige Parameter unverändert,
kein Refit) ergibt Verzweigungsraten von 1,62 (p=1,015) bis 0,51
(p=1,06) — winzige Änderungen an p kippen die Interpretation zwischen
deutlich über- und unterkritisch. Da p selbst plausibel ein
Mischungsartefakt ist (siehe oben), wird die "genau an der
Kritikalitätsschwelle"-Aussage hiermit auf illustrativ zurückgestuft; der
belastbare Befund bleibt der AIC-Vorsprung, nicht der konkrete
Verzweigungsraten-Wert. Ebenfalls korrigiert: `docs/etas_earthquakes.md`
sprach fälschlich von "multiple Nelder-Mead starts" — Standard ist ein
einzelner Startpunkt (siehe oben).

**Wichtige Scope-Grenze für alle drei Teile:** jedes Modell ist bewusst
vereinfacht (COVID-Renewal nutzt dieselbe Weltaggregat-Grenze wie Pilot A;
Energiebilanz ist CO2-only, ohne Aerosole/andere Treibhausgase; ETAS ist
rein zeitlich und global gepoolt ohne räumlichen Kern) — keines der drei
beansprucht, physikalisch/epidemiologisch/seismologisch kalibrierte
Konstanten zu liefern. Alle drei sind eigenständige, additive Module;
`covid_pilot.py`, `noaa_temp_pilot.py` und `earthquake_pilot.py`/deren
Ergebnisse bleiben unverändert.

## Arbeitsweise

- Claude implementiert direkt (Astras Vorschlag ist Konzept + Rechenbelege,
  kein Code-Beitrag zum Paket selbst).
- Jede neue Zahl wird gegen Astras unabhängig berechnete Werte geprüft,
  wo verfügbar (Paket 1: NOAA-Rolling-Origin-Zahlen aus dem Bericht).
- Bestehende `docs/*_pilot.md`-Ergebnisse bleiben unverändert stehen;
  neue Auswertungen werden als eigener Abschnitt ergänzt.
- Volle Suiten-Regression nach jedem Paket (62/62 nach Paket 5).
