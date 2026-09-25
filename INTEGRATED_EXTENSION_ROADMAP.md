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
| C3 | Verweildauern und verteilte Verzögerungen | ✅ erledigt |
| C4 | Konkurrierende Ziele, Kommittoren, Ereigniserhaltung | ✅ erledigt |
| C5 | Kleine Ressourcennetzwerke mit wiederholten Eingriffen | ✅ erledigt |
| C6 | Wiederholte Kooperation und Wert zusätzlicher Information | ✅ erledigt |
| C7 | Gemeinsame Auswertung und Fähigkeitsübersicht | ✅ erledigt |

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

## C3 — Verweildauern und verteilte Verzögerungen (erledigt)

`dynamics/phase_type_delays.py`: Erlang/Phasentyp-Ketten, exakte Fortpflanzung
unter stückweise konstantem Eingang über den Standard-Trick der erweiterten
Matrixexponential (kein ODE-Löser, keine Toleranz zu wählen, exakt auch bei
singulärem `T`).

Hand-nachgerechnete Kontrollwerte vor jedem Code: Erlang(1) und Erlang(2)
mit `τ=1` haben beide mittlere Verweildauer 1; die CDF-Rangfolge KEHRT SICH
zwischen `t=0,25` (`F1>F2`) und `t=2` (`F1<F2`) um — eine kleinere Varianz
ist nicht bei jedem Horizont "schneller". Erlang(2)-Impulsantwort-Peak bei
`t=0,5`, Höhe `2/e`.

**Realer Fehler vor jeder Ergebnisveröffentlichung gefunden:** Die erste
Implementierung des festen Experiments (`validation/distributed_delay_pilot.py`,
`n∈{1,2,4,8}`, `τ=1`, Rechteckimpuls `u=5` auf `[0,0,2)`, Horizont 5,
`R(0)=0,1`, `dR/dt=0,4-y(t)`) prüfte nur die Endpunkte jedes stückweise
konstanten Segments auf Vorzeichenwechsel — das übersieht ein Abtauchen-und-
Erholen INNERHALB eines Segments. Da `R` hier zunächst fällt und sich später
wieder erholt, meldete der fehlerhafte Code für alle vier `n` fälschlich
"kein Grenzdurchgang". Behoben durch dichte Segment-Abtastung + `brentq`-
Verfeinerung, gegengeprüft durch direkte Auswertung von `R` am gemeldeten
Zeitpunkt (`|R|<1e-8`).

**Reales Ergebnis:** Ein echter Grenzdurchgang (`R≤0`) tritt für JEDES der
vier `n` ein (0,406 / 0,845 / 1,037 / 1,093 — später bei größerem `n`).
Peak-Ausgang und Puffer-Minimum ranken `n` aber NICHT gleich: `n=4` hat
einen kleineren Ausgangs-Peak als `n=1` (0,888<0,906), aber ein
schlechteres (negativeres) Minimum (-0,1088<-0,0928) — exakt die im Plan
genannte Warnung, dass Peak- und Minimum-Änderung nicht dieselbe Richtung
haben müssen.

Verifiziert: `verify_phase_type_delays.py` (6/6),
`verify_distributed_delay_pilot.py` (5/5). Docs: `docs/distributed_delays.md`.
`capability_overview.md`/`.json` erweitert.

## C4 — Konkurrierende Ziele, Kommittoren, Ereigniserhaltung (erledigt)

`viability/competing_first_passage.py`: Kommittor `q(x)=P(B vor A|Start x)`
und mittlere Zeit `m(x)` als lineare Gleichungssysteme (nie explizite
Inverse), plus Grenzwahrscheinlichkeiten über festem Horizont via
Matrixexponential.

Hand-nachgerechneter 4-Zustands-Kontrollfall vor jedem Code:
`(q_i,q_j)=(0,6;0,9)`, `(m_i,m_j)=(0,6;0,4)`, `p_B(H=1)=(0,467359895563;
0,829637179582)`. Ratenskalierung um `c`: `q` unverändert, `m` durch `c`
geteilt, Grenzwahrscheinlichkeiten bei `H→H/c` ebenfalls unverändert.

**Brücke zu C2:** Ein handkonstruierter 6-Zustands/3-Klassen-Generator,
exakt vergröberbar (wiederverwendet `closure.generator_lumpability.
is_exact_generator_lumpability`, nicht neu implementiert). Die zwei
Mikro-Zustände derselben Interior-Klasse erhalten IDENTISCHEN Kommittor und
IDENTISCHE mittlere Zeit, die exakt mit dem 3-Zustands-Makro-Kommittor
übereinstimmen — geprüft sowohl auf Randwertproblem-Ebene als auch über
feste Horizonte.

Verifiziert: `verify_competing_first_passage.py` (5/5). Docs:
`docs/competing_first_passage.md`. `capability_overview.md`/`.json`
erweitert. Kein Realdaten-Pilot in diesem Paket.

## C5 — Kleine Ressourcennetzwerke mit wiederholten Eingriffen (erledigt)

`viability/resource_network_control.py`: `dx/dt=Bf+u-d`, Sicherheit über
das ganze Regelintervall via `x_lower+Δ(Bf+u-d_upper)≥0` (Endpunktprüfung
genügt, da affin), mit VIER klar getrennten Status
(`certified_safe`/`boundary_touch`/`strict_violation`/`not_certified`) —
ein Erstberühren bei `x=0` ist erlaubt, keine Verletzung.

Hand-nachgerechneter Drei-Puffer-Kontrollfall vor jedem Code:
`x=(0,2;0,4;0,6)`, `d=(1,1,1)`; `Δ=1` → minimal `(0,8;0,6;0,4)`, Summe 1,8,
quadratische Kosten 1,16; `Δ=2` → minimal `(0,9;0,8;0,7)`, Summe 2,4,
unzulässig bei Budget 2; Halten der `Δ=1`-Eingriffe für 2 Zeiteinheiten
endet bei `(-0,2;-0,4;-0,6)`.

**Realer Fehler vor jeder Ergebnisveröffentlichung gefunden:** Die erste
Implementierung des 3-Knoten-Netzwerkpanels (`validation/resource_network_pilot.py`)
nutzte `whole_interval_safety`s auf Unsicherheit ausgelegten
`not_certified`-Zweig auch zur Fortschreibung eines bereits negativen, aber
SICHER BEKANNTEN Zustands — das fror dessen Trajektorie fälschlich ein.
Gefunden über einen unabhängigen Handrechnungs-Gegencheck, behoben durch
eine eigene `propagate_state`-Funktion und einen neuen, getrennten Status
`already_violated`.

**Reales Ergebnis (3 Knoten, Kette `0→1→2` + Zusatzkante `2→0`, bewusst über
Kapazität hinausgehende Lastspitze):** Eine feste Umverteilungsregel
(`fixed_routing`) endet SCHLECHTER als gar keine Reaktion, sobald die
Lastspitze abgeklungen ist (`-1,5` gegenüber `-0,3` bei `none`, Δ=1) — die
feste Regel "weiß" nicht, dass die Notlage vorbei ist. Der myopische, nur
pro Intervall optimierende Regler baut vor einer BEKANNTEN künftigen Spitze
KEINE Reserve auf und unterbietet bei feiner Zeitauflösung (Δ=0,25) sogar
die naive `none`-Baseline am Minimum — exakt die im Plan selbst genannte
Warnung, dass ein erfolgreiches Einzel-QP weder unendliche Sicherheit noch
rekursive Zulässigkeit beweist.

Verifiziert: `verify_resource_network_control.py` (5/5),
`verify_resource_network_pilot.py` (5/5). Docs:
`docs/resource_network_control.md`, `docs/resource_network_pilot.md`.
`capability_overview.md`/`.json` erweitert.

## C6 — Wiederholte Kooperation und Wert zusätzlicher Information (erledigt)

`validation/sequential_information_pilot.py`: binärer verborgener Zustand,
Glaubenszustand `b`, Übergang `T(b)=p+(1-2p)b`; optimaler Wert via
Bellman-Rückwärtsrekursion (volle Enumeration, kein POMDP-Löser, keine
LLM-Abhängigkeit).

Hand-nachgerechneter Kontrollfall vor jedem Code: `p=0,1`, `c=0,2`, 2
Entscheidungen ab `b=0,5`. Nie messen: 1,0. Immer messen: 1,6. Einmal
messen, dann Persistenz ausnutzen: 1,7 — genau der Bellman-Optimalwert
`V_2(0,5)=1,7`. Alterung der Information nach perfekter Beobachtung:
Trefferquote `1/2+1/2|1-2p|^d`, für `p=0,1`: `d=1→0,9`, `d=2→0,82`,
`d=10→0,5536870912`.

**Pflichtprüfung "freie Option":** über 2250 Kombinationen
(`h,b,p,c`) geprüft, dass eine optionale, kostenpflichtige Beobachtung den
Optimalwert nie schlechter macht als eine Politik ohne diese Option
überhaupt.

Symmetrischer Fehlerkanal: bei `q=0,7` (schlechter als Zufall) erreicht der
optimale (invertierende) Decoder weiterhin 0,7, während ein naiver Decoder
nur 0,3 erreicht.

Repräsentatives `(p,c)`-Panel (Horizont 5) zeigt: bei `p=0` lohnt sich
"einmal messen, dann für immer sicher wissen"; bei `p=0,5` (kein
Zusammenhang zwischen Schritten) kippt die optimale Entscheidung exakt bei
`c=0,5`. Volles `(p,c,Verzögerung,Horizont)`-Kreuzprodukt aus dem Plan nicht
erschöpfend durchlaufen.

Verifiziert: `verify_sequential_information_pilot.py` (6/6). Docs:
`docs/sequential_information_pilot.md`. `capability_overview.md`/`.json`
erweitert.

## C7 — Integration, Nachweis und Abschluss (erledigt)

`docs/capability_overview.md`/`.json` inkrementell mit jedem Paket um genau
die vom Bestandsschema geforderten Felder erweitert (Frage, Modellklasse,
Voraussetzungen, Evidenzart, Prüfskripte, bekannte Grenzen) — 6 neue
Einträge (C1–C6), gleiches Schema wie die 28 bestehenden Modul-Einträge.

**Vergleichsseite nach Plan Abschnitt 11.1:**

| Paket | Welche Information fehlte zuvor? | Was wurde neu prüfbar? | Wann reicht die einfachere Darstellung? | Wann scheitert die Übertragung (kleinstes Gegenbeispiel)? | Was ist empirisch untersucht? | Was bleibt offen? |
|---|---|---|---|---|---|---|
| C1 | Zustand (Speicher nicht direkt beobachtbar, nur Tagesmittel-Abfluss) | Kalman-Zustandskorrektur mit exaktem Tagesmittel-Messoperator; Beobachtbarkeitsrang | Bei DEA11490 (kleinstes/schnellstes Gebiet) schlägt Korrektur sogar Persistenz; an 5/6 Gebieten bleibt der offene Regelkreis der einfachere, nicht schlechtere Ausgangspunkt | `F=0,5·I`: Beobachtbarkeitsrang fällt auf 1 (Zustandsdifferenz für `H=(1,1)` für alle Zeit unsichtbar) | 6 CAMELS-DE-Einzugsgebiete, 1991–2005 Training/2006–2010 Lücke/2011–2020 Test, konditionierter Hindcast; dieselben 6 Gebiete waren bereits Explorationspanel aus B3b, keine unabhängige Bestätigung | C1c: unabhängiges, per Metadaten VOR Ergebniseinsicht ausgewähltes Bestätigungspanel |
| C2 | Eingriffsabbildung (aktionsabhängige Vergröberung ungeprüft) | Exakte/starke Vergröberung `P^a·C=C·Q^ω(a)`, geprüft separat pro Aktion | Wenn alle Mikroaktionen derselben Makroaktion identische Blocksummen liefern (Kontrollfall: Passiv+Intervention beide exakt) | Zwei geänderte Intervention-Zeilen (Austritt 0,1 vs. 0,3 zur zweiten Klasse) — keine einzelne Makro-Zeile passt beide | keins (rein analytischer Kontrollfall) | Keine Näherungsschranke für inexakte Vergröberung implementiert |
| C3 | Verweildauerform (nur Mittelwert, keine Form der Verzögerung) | Erlang/Phasentyp-Kette, exakte Fortpflanzung unter stückweise konstantem Eingang | Wenn nur der Mittelwert zählt (nicht das Timing eines Grenzdurchgangs) | CDF-Rangfolge kehrt sich zwischen `t=0,25` und `t=2` um (Erlang(1) vs. Erlang(2), gleicher Mittelwert) | keins (festes, vorab deklariertes synthetisches Experiment) | Transportverzögerung mit expliziten Zwischenzuständen (Anschluss an C5) nicht gebaut |
| C4 | Konkurrierendes Ziel (nur eine Sicherheitsgrenze, kein zweiter konkurrierender Ausgang) | Kommittor `q(x)`, mittlere Zeit `m(x)`, Grenzwahrscheinlichkeiten über festen Horizont | Bei exakter Vergröberung (Brücke zu C2) reicht die kleinere Makrokette exakt | Singuläres `L_DD` — ein Zustand erreicht `A∪B` nie sicher | keins | Vollständige Transition-Path-Ströme (C4b) mit Ergodizitätsprüfung |
| C5 | Netzrestriktion (Kantenkapazitäten, gemeinsames Budget ungeprüft) | Sicherheit über ganzes Regelintervall, Netz-QP mit vier getrennten Status | Entkoppelter Fall (0 Kanten) reduziert exakt auf die geschlossene Drei-Puffer-Form | Feste Umverteilungsregel wird NACH Abklingen einer Lastspitze schlechter als gar keine Reaktion; myopisches QP baut vor bekannter Spitze keine Reserve auf | keins (deklariertes Modellbeispiel, explizit keine echten Netzdaten) | Transportverzögerung (Anschluss an C3); allgemeiner Netzwerkfall nur durch Mehrfachstarts, nicht durch geschlossene Form/volle aktive-Mengen-Prüfung abgesichert |
| C6 | Nachrichtenzeit (Alterung von Information, Kosten wiederholter Abfrage ungeprüft) | Bellman-Optimalwert für Beobachten-oder-nicht über mehrere Entscheidungen | Bei `p=0,5` (keine Persistenz zwischen Schritten): Messen lohnt exakt bei `c<0,5` | `p=0`: eine Politik, die IMMER misst, ist trotz perfekter, aber kostenpflichtiger Information suboptimal gegenüber "einmal messen, dann für immer sicher wissen" | keins (analytischer Kontrollfall + repräsentatives Parameterpanel) | Volles `(p,c,Verzögerung,Horizont)`-Kreuzprodukt aus dem Plan nicht erschöpfend durchlaufen |

Keine domänenübergreifende Mittelwert-Rangliste gebildet (inkompatible
Einheiten/Fragestellungen, wie schon bei B7). Transferierbar sind die
Verfahren (exakte Randwertprobleme, Blocksummen-/Lumpability-Prüfungen,
Bellman-Rekursionen), nicht die Parameterwerte.

**Zurückgestellte Teilaufgaben, sichtbar gehalten (Plan Abschnitt 11.2,
Punkt 8):** C1c (unabhängiges Bestätigungspanel), C4b (vollständige
Transition-Path-Ströme mit Ergodizitätsprüfung), C3↔C5-Transportverzögerung
mit expliziten Zwischenzuständen, C6's volles Parameter-Kreuzprodukt. Die
sechs Kernfähigkeiten C1–C6 selbst gelten dadurch NICHT als reduziert — jede
hat einen hand-nachgerechneten Kontrollfall, ein registriertes Prüfskript
und (außer C2/C3/C4/C6, die rein analytisch bleiben) mindestens einen realen
oder fest deklarierten Anwendungsfall.

**Volle Regression zum Abschluss dieser Runde:** 77/77 Mathe-Prüfungen,
0 defekte Links (287 geprüfte relative Links über 205 Markdown-Dateien) —
siehe Commit-Historie für die einzelnen Zwischenstände je Paket (C0 bis C6,
je mit eigenem grünen CI-Lauf).
