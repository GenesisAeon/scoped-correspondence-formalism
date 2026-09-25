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
| C1 | Zustandsschätzung und Beobachtbarkeit | ✅ erledigt |
| C2 | Korrespondenzen unter deklarierten Aktionen | ✅ erledigt |
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

## C1 — Zustandsschätzung und Beobachtbarkeit (erledigt)

`observation/linear_state_estimation.py` (generischer Kalman-Kern:
predict/update, Joseph-Form-Kovarianz, keine explizite Matrixinversion,
Beobachtbarkeitsmatrix/-rang) + `validation/hydrology_state_estimation.py`
(Tagesmittel-Messoperator, der `dynamics/linear_reservoirs.py` exakt
wiederverwendet, Rauschkalibrierung, 2×2-Realdaten-Panel).

Hand-nachgerechneter Kontrollfall vor jedem Code: `F=diag(1/2,1/4)`,
`H=(1,1)`, `m⁻=0`, `P⁻=I`, `R=1`, `y=3`, `W=0` → `K=(1/3,1/3)`, `m⁺=(1,1)`,
`P⁺=[[2/3,-1/3],[-1/3,2/3]]`; unabhängig ein zweites Mal geprüft durch
direkte Konditionierung der analytisch konstruierten gemeinsamen
Gauß-Verteilung (nie den Filter zweimal gegen sich selbst aufrufen).

**Reales Ergebnis (dieselben 6 CAMELS-DE-Einzugsgebiete, 2011–2020):**
Zustandskorrektur mit dem tatsächlichen Tagesmittel-Abfluss verbessert die
MAE gegenüber dem offenen Regelkreis an ALLEN 6 Gebieten und allen drei
Vorlaufzeiten (1/3/7 Tage) deutlich (z. B. DEG10330 Ein-Speicher:
1,098→0,273 bei Vorlaufzeit 1, eine Reduktion um 75 %) — schlägt die
Persistenz-Baseline aus `hydrology_pilot.md` aber nur an einem der 6
Gebiete (DEA11490, dem kleinsten/schnellsten). Die innere Validierung wählt
durchgehend den größten getesteten Prozessrauschen-Skalenwert (`w_scale=1e6`)
— geprüft als echtes Sättigungsplateau (Inner-Validation-MAE 0,1338 bei
`w_scale=1`, 0,0978 bei `1e5`, 0,09776 bei `1e8`), kein verstecktes
Rastermaximum. Der ungebundene Gauß-Filter erzeugt an allen 6 Gebieten an
einem nicht trivialen Anteil der Tage negative Speicherzustände — offen
berichtet, nie genullt.

Verifiziert: `verify_linear_state_estimation.py` (6/6),
`verify_hydrology_state_estimation.py` (7/7). Docs:
`docs/hydrology_state_estimation.md`. `capability_overview.md`/`.json`
erweitert. C1c (unabhängiges, vorab per Metadaten ausgewähltes
Bestätigungspanel) explizit zurückgestellt.

## C2 — Korrespondenzen unter deklarierten Aktionen (erledigt)

`correspondence/controlled_markov.py`: exakte/starke Vergröberung
`P^a C = C Q^{ω(a)}`, geprüft SEPARAT pro deklarierter Mikro-Aktion — nie
gepoolt über Aktionen hinweg.

Hand-nachgerechneter 4-Zustands-Kontrollfall vor jedem Code: 2 Klassen
`{0,1}`,`{2,3}`, heterogene Mikro-Kernel pro Klasse. Passiv `(a,b)=(0,7,0,4)`
und Intervention `(a,b)=(0,8,0,1)` beide exakt (`Q_passiv=[[0.7,0.3],
[0.4,0.6]]`, `Q_intervention=[[0.8,0.2],[0.1,0.9]]`, Abweichung `~1e-16`).
Negativfall: zwei geänderte Intervention-Zeilen brechen die Exaktheit NUR
für diese Aktion (Passiv bleibt exakt) — erkannter Defekt `0,2`, bester
Minimax-Ersatzwert `0,2`, maximaler Restfehler `0,1`, exakt wie im Plan
angegeben.

Zusätzlich implementiert: `is_union_of_classes` (Makro-Ereignisse müssen
ganze Partitionsblöcke sein) und `check_cost_consistency`
(`c_X(x,a)=c_Y(C(x),ω(a))`, fehlender Makro-Gegenwert zählt als Verletzung,
nie als übersprungen).

Verifiziert: `verify_controlled_correspondence.py` (5/5). Docs:
`docs/controlled_correspondence.md`. `capability_overview.md`/`.json`
erweitert.

## Nächste Schritte

C3 (Verweildauern und verteilte Verzögerungen) als nächstes.
