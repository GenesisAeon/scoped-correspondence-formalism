# Audit Roadmap — Tiefenanalyse 3bb7d601f (2026-09-19)

Externe Code-Tiefenanalyse (`prompts/Answers/SCF_Tiefenanalyse_3bb7d601f.md`,
Belege in `prompts/Answers/../../` via `SCF_Auditbelege_3bb7d601f.zip`,
lokal entpackt nach `audit_review/` — nicht Teil des Pakets, nur zur
eigenen Nachprüfung). **Von Claude vollständig unabhängig nachvollzogen:**
das mitgelieferte `independent_probes.py` wurde selbst gegen den
aktuellen Stand ausgeführt (nicht nur der Berichtstext gelesen) — jeder
P0/P1-Befund reproduziert exakt. Das ist die bisher wertvollste externe
Prüfung des Projekts.

Johanns Auftrag (2026-09-19): "Mach gerne eine Roadmap und arbeite das
in sinnvollen Schritten alles ab" — plus ein explizit hervorgehobener
Punkt aus dem Bericht (Abschnitt 7.3): die Abgrenzung gegen unbegründete
Identitäten ist richtig, geht aber stellenweise zu weit ("NO
mathematical kinship" statt der eigentlich gemeinten "keine Identität
ohne eigenen Beweis"). Der mögliche eigenständige Beitrag liegt in einer
verlässlichen, maschinenlesbaren Prüfsprache — angenommene vs. tatsächlich
geprüfte Voraussetzungen und die Reichweite eines Ergebnisses überall
getrennt auszuweisen.

## Reihenfolge (folgt dem Audit-Vorschlag, Abschnitt 8)

| # | Paket | Priorität | Status |
|---|---|---|---|
| 1 | Cygnus-Datenherkunft klären (A01) | P0 | ✅ erledigt (2026-09-20, als unverifiziert gekennzeichnet — siehe unten) |
| 2 | NaN-/Leermengen-Zertifikate + Zeitabbildung (A02, A03) | P1 | ✅ erledigt |
| 3 | Kubische Wurzeln + Perkolation härten (A04, A05) | P1 | ✅ erledigt |
| 4 | Viabilität + Profile-Likelihood präzisieren (A06, A07) | P1 | ✅ erledigt |
| 5 | Restliche Input-Guards (retention/realized_rate/is_exact_closure) | P1/P2 | ✅ erledigt |
| 6 | Floquet Jordan-Block-Erkennung (A08) | P2 | ✅ erledigt |
| 7 | Split-Manifest-Vertrag härten (A09) | P1 | ✅ erledigt |
| 8 | Link-Checker-Bug (URI-Encoding) | P2 | ✅ erledigt |
| 9 | Übergreifende "kein gemeinsames X"-Sprache entschärfen (Abschnitt 7.3) | P2 | ✅ erledigt |
| 10 | Gemeinsames Report-/Scope-Schema entwerfen und dokumentieren | P2 | ✅ erledigt |
| 11 | README/ARCHITECTURE_ROADMAP konsolidieren (A11) | P2 | ✅ erledigt |
| 12 | Vollständige Modellkette demonstrieren | P2 (später) | ⏸ zurückgestellt |
| 13 | Unabhängige empirische Korrespondenzprüfung | P2 (später) | ⏸ zurückgestellt |

### Paket 1 — Auflösung (2026-09-20)

Nachbarpaket `D:\mandala\cygnus-jet-utac` (Commit `9178fb6`, Autor `Claude
<noreply@anthropic.com>`) enthält dieselbe Epochentabelle byte-identisch
sowie `data/prabu2026_measurements.yaml` mit nur 4 aggregierten
Prabu-2026-Kennzahlen (Anfangs-/End-Positionswinkel, 18-Jahres-Basislinie).
Keine Quelle für 18 einzeln datierte Epochen gefunden; der MJD/Jahr-Drift
wächst systematisch (0 bis ~90 Tage). Wahrscheinlichste Erklärung:
KI-Interpolation zu den 4 echten Werten, keine archivierte
Einzelmessungsreihe. **Johanns Entscheidung:** als unverifiziert
kennzeichnen, Pilot als illustrative Methodendemonstration im Repo
belassen (Rechnung bleibt korrekt und reproduzierbar). Umgesetzt in
`data/cygnus_x1_radio_epochs.yaml` (Header-Warnung), `validation/core.py`
(`DATA_PROVENANCE_WARNING`-Konstante, in `ValidationReport.notes` und
`DatasetManifest.license_note`), `verify_cygnus_pilot.py`
(`empirical_validation: False` + neuer Check), `docs/cygnus_pilot.md` und
README.md.

Pakete 12/13 sind bewusst zurückgestellt — sie sind größere, eigene
Vorhaben (siehe Audit Abschnitt 8, Punkte 7–8), keine Bugfixes. Sie
werden nach Abschluss der Pakete 1–11 neu bewertet.

## Arbeitsweise

Anders als bei den Erweiterungs-Milestones (M1–M41): das sind
Korrekturen an bereits gemergtem, bereits geprüftem Code, keine neue
mathematische Erweiterung, die Literaturrecherche braucht. Claude
implementiert direkt (kein Aeon-Auftrag), mit dem exakt selben Maßstab:
jede Korrektur wird gegen das Audit-Gegenbeispiel UND mindestens einen
selbst konstruierten Zusatzfall von Hand nachgerechnet, bevor committet
wird. Kerndokumente (FORMALISM.md + sieben Layer-Dokumente) bleiben wie
immer unangetastet, sofern nicht ausdrücklich Teil eines Pakets.

## Einzelbefunde und Fix-Notizen

Wird pro Paket beim Abschluss ergänzt (siehe `FOLLOWUP_TICKETS.md` F56
für die laufende Zusammenfassung).
