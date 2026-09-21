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
| 4 | Raten-/Viabilitäts-Kontrollfälle | ⏸ geplant |
| 5 | Je Domäne ein mechanistisches Modell (COVID-Renewal, Energiebilanz-Klima, ETAS-Erdbeben) | ⏸ geplant |

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

## Arbeitsweise

- Claude implementiert direkt (Astras Vorschlag ist Konzept + Rechenbelege,
  kein Code-Beitrag zum Paket selbst).
- Jede neue Zahl wird gegen Astras unabhängig berechnete Werte geprüft,
  wo verfügbar (Paket 1: NOAA-Rolling-Origin-Zahlen aus dem Bericht).
- Bestehende `docs/*_pilot.md`-Ergebnisse bleiben unverändert stehen;
  neue Auswertungen werden als eigener Abschnitt ergänzt.
- Volle 55-Suiten-Regression nach jedem Paket.
