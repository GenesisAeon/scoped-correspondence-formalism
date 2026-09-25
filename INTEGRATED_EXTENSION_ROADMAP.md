# SCF — Zustände, Eingriffe, Verzögerungen und Entscheidungen — Roadmap (2026-09-25)

Antwort auf `prompts/Answers/nicht_stationäre_Treiber/SCF_INTEGRATED_EXTENSION_IMPLEMENTATION_PLAN.md`
(Astra, 2026-09-25, Referenzcommit `d0ab5c5`) — sechs neue Fähigkeiten
(Zustandsschätzung, aktionsabhängige Korrespondenz, verteilte
Verzögerungen, konkurrierende Erstpassageziele, wiederholte
Netzwerk-Eingriffe, dynamischer Informationswert), plus C0 (zwei konkrete
Zeitachsenfehler im gerade abgeschlossenen Hydrologie-Piloten) und C7
(Konsolidierung).

Johanns Auftrag (2026-09-25): "Volle Roadmap C0–C7" (nach expliziter
Rückfrage zum Umfang, analog zur B0–B7-Entscheidung).

Gleiche Disziplin wie bei den vorherigen Roadmaps: additive Module, Hand-
Nachrechnung vor Code, unabhängige Reproduktion jedes Astra-Befunds vor dem
Fix, `verify_*.py` mit Scope-Verletzungen, volle Suiten-Regression nach
jedem Paket, negative/neutrale Ergebnisse zählen genauso wie positive.

## Pakete

| Paket | Inhalt | Status |
|---|---|---|
| C0 | Hydrologische Zeitachse korrigieren (zwei reale Bugs) | ✅ erledigt |
| C1 | Zustandsschätzung und Beobachtbarkeit | ⏳ offen |
| C2 | Korrespondenzen unter deklarierten Aktionen | ⏳ offen |
| C3 | Verweildauern und verteilte Verzögerungen | ⏳ offen |
| C4 | Konkurrierende Ziele, Kommittoren, Ereigniserhaltung | ⏳ offen |
| C5 | Kleine Ressourcennetzwerke mit wiederholten Eingriffen | ⏳ offen |
| C6 | Wiederholte Kooperation und Wert zusätzlicher Information | ⏳ offen |
| C7 | Gemeinsame Auswertung und Fähigkeitsübersicht | ⏳ offen |

Reihenfolge (Plan Abschnitt 2): C0 → C1 → C2 → C3 → C4 → C5 → C6 → C7.

## C0 — Hydrologische Zeitachse korrigieren (erledigt)

Zwei reale Bugs in `validation/hydrology_pilot.py`, unabhängig am
tatsächlichen Code reproduziert, bevor etwas geändert wurde:

**Befund A:** Die Persistenz-Baseline sagte den ersten Testtag mit seinem
eigenen Zielwert voraus (`pred_persist_test[0] = Q_test[0]`) — eine
selbstreferenzielle, künstlich perfekte "Vorhersage". Reproduziert exakt:
`Q_test=[10,12,13]` ergab `[10,10,12]`.

**Befund B:** Der Reservoirzustand wurde über `train_mask | test_mask`
(die Vereinigung der zwei getrennten Perioden) fortgeschrieben — die
~1826 Tage (2006–2010) zwischen Training und Test wurden dabei
stillschweigend übersprungen; der Zustand Ende 2005 floss unmittelbar in
den ersten simulierten Testtag 2011 ein. Reproduziert exakt an einem
synthetischen Fall mit exaktem Erzeugungsprozess und echter Lücke: die
alte Vereinigungskonstruktion ergab MAE `~1,1·10⁻³` gegenüber der wahren
Trajektorie; die korrigierte Konstruktion über die volle Kalenderspanne
ergibt MAE `0,0`.

**Fix:** Simulation über die VOLLE ZUSAMMENHÄNGENDE Kalenderspanne vom
Trainingsbeginn bis zum Testende (nie eine Vereinigung disjunkter
Teilperioden) — behebt beide Befunde gemeinsam, da die Persistenz-Baseline
jetzt denselben vollständigen Spannen-Array für ihren Ein-Tag-Verzug
verwendet.

**Gemessene Auswirkung auf die 6 echten Einzugsgebiete: klein.** Die
Modellrangfolge bleibt für alle 6 Gebiete unverändert (Persistenz gewinnt
weiterhin insgesamt auf allen 6; Zwei-Speicher schlägt weiterhin
Ein-Speicher auf allen 6) — die korrigierten Zahlen weichen von den
ursprünglich berichteten nur in der 3.–4. signifikanten Stelle ab, da die
gefitteten Speicherraten dieser 6 Gebiete schnell genug sind, dass die
tatsächlich beobachteten Niederschläge 2006–2010 den Zustand bis 2011
ohnehin in eine vergleichbare Lage bringen. Das ist eine Eigenschaft
dieser 6 Gebiete, keine allgemeine Garantie.

Verifiziert: `verify_hydrology_pilot.py` (7/7, zwei neue Regressionen
`c0_finding_a_...` und `c0_finding_b_...`). Docs: `docs/hydrology_pilot.md`
(neuer Correction-Block, korrigierte Tabellen).

## Nächste Schritte

C1 (Zustandsschätzung und Beobachtbarkeit) als nächstes — laut Plan der
mit Abstand größte Einzelaufwand der ersten Etappe.
