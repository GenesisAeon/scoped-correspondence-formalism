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
| 2 | COVID-Heterogenität: Länder statt Weltmittel; Beobachtungsmodell trennen | ⏸ geplant |
| 3 | Treiber-abhängige Dynamik-Schnittstelle (eingefrorene Stabilität vs. echte Trajektorie) | ⏸ geplant |
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

## Arbeitsweise

- Claude implementiert direkt (Astras Vorschlag ist Konzept + Rechenbelege,
  kein Code-Beitrag zum Paket selbst).
- Jede neue Zahl wird gegen Astras unabhängig berechnete Werte geprüft,
  wo verfügbar (Paket 1: NOAA-Rolling-Origin-Zahlen aus dem Bericht).
- Bestehende `docs/*_pilot.md`-Ergebnisse bleiben unverändert stehen;
  neue Auswertungen werden als eigener Abschnitt ergänzt.
- Volle 55-Suiten-Regression nach jedem Paket.
