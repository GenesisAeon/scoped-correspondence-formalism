# SCF — Zustände, Eingriffe, Verzögerungen und Entscheidungen

## Ausarbeitungs- und Implementierungsplan C0–C7

**Für:** Johann Benjamin Römer / GenesisAeon  
**Übergabe an:** Claude Code  
**Erstellt:** 25. September 2026  
**Referenzstand:** `d0ab5c5ffc0e14b834ce9e285268cb8a34345e98`  
**Repository:** <https://github.com/GenesisAeon/scoped-correspondence-formalism>  
**Status:** ausgearbeiteter Vorschlag mit unabhängig nachgerechneten Kontrollfällen; neue Funktionen sind noch nicht implementiert.

## 1. Ziel und Entscheidung

Die nächste Ausbaurunde verbindet vorhandene Fähigkeiten zu neuen, überprüfbaren Fragestellungen. SCF besitzt inzwischen Referenzmodelle für Beobachtung, Dynamik, Gedächtnis, Aggregation, Erstpassage, begrenzte Eingriffe und kooperative Entscheidungen. Daraus lassen sich sechs neue Fähigkeiten entwickeln:

1. Verborgene Zustände aus zeitlich verfügbaren Messungen schätzen.
2. Prüfen, ob eine Korrespondenz auch unter ausdrücklich benannten Eingriffen gilt.
3. Die Wirkung unterschiedlicher Verzögerungs- und Verweildauerverteilungen untersuchen.
4. Erholung und Ausfall als konkurrierende Ziele behandeln.
5. Kleine Ressourcennetzwerke über wiederholte Eingriffe steuern.
6. Zusätzliche Information anhand ihres Entscheidungsnutzens und ihrer Kosten bewerten.

Die ersten drei Fähigkeiten erhalten Vorrang. Die weiteren drei sind vollständig spezifiziert, folgen aber als zweite Etappe. C0 behebt zwei beim Anschluss an die neue Zustandsschätzung konkret aufgefallene Zeitachsenprobleme. C7 führt die Ergebnisse zusammen.

**Erfolg bedeutet:** Eine neue Frage ist unter benannten Voraussetzungen reproduzierbar beantwortbar. Ein komplexeres Modell muss weder die Baseline schlagen noch in allen Situationen nützlich sein. Eine Widerlegung einer stärkeren Übertragungsbehauptung ist ein vollwertiges Ergebnis.

Die Arbeit an diesem Dokument umfasst Quelltextprüfung der relevanten Anschlüsse, Primärquellenrecherche und lokale Berechnungen der angegebenen Referenzfälle. Sie umfasst keinen erneuten vollständigen Repo-Audit, keinen neuen Lauf aller Realdatenpiloten und keine Änderung am GitHub-Repository. Der abgeschlossene Reviewzyklus R1–R7 bleibt historisch abgeschlossen; C0 betrifft den danach hinzugekommenen Hydrologie-Anschluss.

## 2. Umfang, Reihenfolge und vorhandene Anschlüsse

| Paket | Neuer Beitrag | Vorhandene Basis | Abschlussprodukt |
|---|---|---|---|
| C0 | Korrekte Kalender- und Informationszeitachse | Hydrologie-Pilot | Zwei Regressionen, korrigierte sechs Ergebnisreihen |
| C1 | Zustandsschätzung und Beobachtbarkeit | Lineare Reservoirs, Beobachtungsmodelle, Validierung | Linearer Filterkern + Hydrologie-Ablation |
| C2 | Aktionsabhängige Korrespondenz | `PC=CQ`, Partitionen, Strukturbrücken | Endlicher Prüfvertrag mit positivem und negativem Eingriffsfall |
| C3 | Verteilte Verzögerungen | Reservoirs, Gedächtniskerne, CTMC | Erlang-/Phasentyp-Modul + gemeinsamer Lastversuch |
| C4 | Konkurrierende Erstpassageziele | CTMC-Erstpassage, Closure | Kommittor, Zeit bis zum Rand, Ereigniserhaltung bei Aggregation |
| C5 | Wiederholte Eingriffe im Ressourcennetz | Puffer, gemeinsame Budgets, CBF | Kleines Flussnetz mit überprüfter Sicherheit zwischen Eingriffen |
| C6 | Dynamischer Informationswert | Endliche Agentenaufgaben, PID, Beobachtung | Exakt ausgewertete wiederholte Aufgabe mit Messkosten |
| C7 | Gemeinsame Auswertung | Fähigkeitsübersicht, Protokoll, CI | Fähigkeitstabellen, Grenzen, Reproduktionsanleitung |

**Empfohlene Ausführung:** C0 → C1 → C2 → C3 → C4 → C5 → C6 → C7. C2 und C3 brauchen C1 mathematisch nicht. C4 verbindet sich mit C2; C5 nutzt C1 zunächst nur konzeptionell, denn statistische Filterkovarianzen liefern keine harten Zustandsgrenzen. C6 benötigt keinen großen Agenten-Stack.

Vorhandene Dateien, deren Semantik erhalten oder bewusst erweitert werden soll:

- `dynamics/linear_reservoirs.py`: `reservoir_step`, `reservoir_interval_discharge`, parallele Varianten, Faltungsdarstellung.
- `validation/hydrology_pilot.py`: bisheriger konditionaler Hindcast; kein historisch authentifizierter Wetterforecast.
- `closure/core.py`: `is_exact_closure`, `closure_error`, `partition_matrix`, `candidate_macro_kernel`.
- `closure/generator_lumpability.py`, `closure/linear_memory_projection.py`.
- `viability/first_passage_ctmc.py`: derzeit insbesondere M/M/1-spezifische Konstruktionen.
- `viability/coupled_buffer_cbf_qp.py`: zwei Puffer, momentane Barriere und Prüfung gehaltener Eingriffe.
- `validation/cooperative_agents_pilot.py`: statische XOR-, Redundanz- und Fehlerkanalaufgaben.
- `docs/domain_expansion_protocol.md`, `docs/structural_relations.md`, `docs/capability_overview.md` und `.json`.
- `scripts/run_verification_suite.py`: neue Prüfskripte ausdrücklich in `_EXPLICIT_CATEGORY` registrieren.

Neue Dateinamen in diesem Plan sind Vorschläge. Vor Implementierung den aktuellen Branch prüfen und gleichwertige inzwischen vorhandene Funktionen wiederverwenden. Die alte Nummerierung B0–B7 nicht überschreiben. Keine gemeinsame Oberklasse einführen, bevor mindestens zwei konkrete Nutzer dieselbe Schnittstelle tatsächlich benötigen.

`docs/structural_relations.md` enthält weiterhin einen gesonderten Status für die Aufnahme als akzeptierter Kern. Dieser Plan verlangt dafür keine Statusänderung. Neue experimentelle Prüfmodule und ihre Dokumentation können den vorhandenen Status respektieren.

## 3. Gemeinsamer wissenschaftlicher Vertrag

### 3.1 Aussagen und Evidenz

Jedes Paket trennt: etablierte Literaturgrundlage, eigene Ableitung im deklarierten Modell, analytischen Kontrollwert, numerischen Vergleich und empirischen Befund. Eine Matrixgleichung, die numerisch bis zu einer Toleranz erfüllt ist, wird als numerisch geprüfte Gleichung berichtet. Der analytische Kontrollfall kann zusätzlich exakt hergeleitet sein.

Eine gute Prognose beweist keine kausale Richtigkeit. Eine beobachtbare Zustandsdarstellung beweist keine identifizierbaren Parameter. Eine gute mittlere Trajektorie garantiert keine erhaltene Erstpassage. Eine nominelle Intervallabdeckung garantiert keine pfadweise Sicherheit.

### 3.2 Zeit und Informationsstand

Vier Zeitangaben unterscheiden: Ereigniszeit, Messintervall, Verfügbarkeit der Messung, Prognoseursprung. Jedes Ergebnis nennt Vorlauf und Auswertezeit. Echte Kalenderlücken bleiben Zeitintervalle; das Entfernen unbewerteter Zeilen darf keine Zeitkompression erzeugen.

Für neue Prognosen gilt: Filterzustand und Hyperparameter hängen ausschließlich von bis zum Ursprung zugelassenen Daten ab. Bei einem konditionalen Hindcast dürfen zukünftige Treiber vorgegeben werden; zukünftige Zielmessungen dürfen den Zustand am Ursprung trotzdem nicht beeinflussen. Prognoseintervalle sind dann ausdrücklich bedingt auf den vorgegebenen Treiberpfad.

Archivierte CAMELS-Tagesdaten besitzen nicht automatisch historische Publikationszeitstempel. Ohne entsprechende Metadaten lautet der Anspruch „retrospektiv mit festgelegtem Informationsschnitt“, nicht „historisch operationell verfügbar“.

### 3.3 Datenvergleich und Generalisierung

Für jede Modellpaarung eine gemeinsame gültige Auswertemenge verwenden und deren Größe berichten. Zusätzlich dürfen modellweise verfügbare Scores erscheinen. Unterschiedliche Nenner dürfen keine versteckte Rangliste erzeugen. Niedrigwassergrenzen, Hyperparameterbereiche und Auswertemetriken werden vor Auswertung des jeweiligen Testfensters fixiert.

Die sechs bekannten CAMELS-Gebiete sind ein Entwicklungs-/Explorationspanel: Ihre bisherigen Ergebnisse wurden bereits angesehen. Eine neue Methode auf denselben Reihen wird dadurch nicht zu einer unabhängigen Bestätigung. C1 enthält eine getrennte Anschlussoption für ein nach Metadaten vorab gewähltes zusätzliches Panel.

Keine gepoolte Rangliste über inkompatible Einheiten. Kein universeller Gewinn von Nichtlinearität, Gedächtnis, Vernetzung oder Kommunikation. Der Einfluss einer Erweiterung wird möglichst durch einen Vergleich geprüft, bei dem die übrigen Komponenten gleich bleiben.

### 3.4 Numerik und Berichte

- Öffentliche numerische Eingaben auf Endlichkeit, Form, Einheiten und zulässige Werte prüfen. Nichtganzzahlige Zustandszahlen nicht runden.
- Solverfehler, mathematische Unzulässigkeit, fehlende Identifikation und uneindeutige Ergebnisse getrennt ausgeben.
- Zeitskalierung, Zustandspermutation und Grenzfälle dort testen, wo sie eine reale Fehlermöglichkeit aufdecken.
- JSON mit `allow_nan=False` erzeugen; fehlende Größen als `null` plus Status. `default=str` allein verhindert die Ausgabe von `NaN` nicht — die entsprechende Formulierung im vorhandenen Protokoll bei seiner Erweiterung präzisieren.
- Ein Laufmanifest enthält Commit, Konfiguration, Paketversionen, Datenhashes und Auswertungsmodus. Bestehendes Check-JSON beibehalten; kein Umbau aller historischen Ergebnisdateien.
- Neue Daten benötigen die bestehende Provenienz- und Lizenzbehandlung. Für C1 werden zunächst die bereits eingecheckten CAMELS-Auszüge genutzt.

## 4. C0 — Hydrologische Zeitachse vor der Erweiterung korrigieren

### 4.1 Befund A: Zielwert im ersten Persistenzwert

Im Referenzstand steht in `run_catchment_hydro_pilot`:

```python
pred_persist_test = np.concatenate([[Q_test[0]], Q_test[:-1]])
```

Damit wird der erste Testtag mit seiner eigenen Zielmessung vorhergesagt. Für `Q_test=[10,12,13]` erzeugt die unveränderte Anweisung `[10,10,12]`. Wenn der tatsächlich vorher verfügbare Tageswert 7 war, muss der erste Persistenzwert 7 sein. Der erste absolute Fehler beträgt dann 3 statt künstlich 0.

**Umsetzung:** Den Lag auf der vollständigen Kalenderachse bilden und erst danach die Testtage auswählen. Fehlt die benötigte Vorgängermessung, den Fall gemäß vorab festgelegter Regel als nicht auswertbar markieren oder eine explizite alternative Baseline verwenden. Niemals durch den aktuellen Zielwert ersetzen. Für einen Vorlauf von h Tagen stammt die Persistenzvorhersage vom Prognoseursprung; sie darf nicht zwischendurch mit später bekannt gewordenen Werten aktualisiert werden.

**Regression:** Eine Änderung des ersten Testzielwerts darf die dazu schon ausgegebene Prognose nicht verändern. Die Prognose des nächsten Ursprungs darf sich ändern, sobald dieser Wert verfügbar geworden ist.

### 4.2 Befund B: Fünf Jahre werden dynamisch übersprungen

Die Simulation verwendet gegenwärtig:

```python
combined_mask = train_mask | test_mask
P_full = P_filled[combined_mask]
```

Bei Training 1991–2005 und Test 2011–2020 wird der Speicherzustand vom Ende 2005 unmittelbar in den ersten simulierten Tag 2011 übernommen. Die tatsächlichen 1826 Tage 2006–2010 fehlen samt Niederschlag und Entleerung.

Zur isolierten Reproduktion wurde die unveränderte Pilotfunktion aus dem gelesenen Quelltext ausgeführt; Fit und Reservoirsimulation wurden durch protokollierende Stubs ersetzt. Auf einer vollständigen Tagesachse 2005–2011 mit Training 2005 und Test 2011 erhielt jede Simulation 730 statt 2556 Schritte. Das weist den Fehler im Kalenderzuschnitt nach; es ist kein erneuter hydrologischer Datenfit.

Ein unabhängiger physikalischer Kontrollfall: Ein Speicher mit Anfangswert 1, `k=0.01/Tag` und ohne Zufluss behält nach 1826 Tagen nur

\[
e^{-0.01\cdot1826}=1.17431000339\cdot10^{-8}.
\]

Ein einfaches Zusammenschieben der Perioden lässt diesen Entleerungsvorgang vollständig aus.

**Umsetzung:** Zustand über die vollständige Achse fortschreiben. Fit-, Assimilations- und Scoremasken getrennt verwalten. Die Zwischenjahre dürfen für Zustandsfortschreibung genutzt werden, ohne sie in Fit oder Testscore aufzunehmen. Alternativ wäre ein expliziter Neustart mit separater Initialisierung zulässig, aber kein stilles Übernehmen des alten Zustands.

**Abnahme C0:** beide Regressionen bestanden; sechs bestehende Datenreihen neu gerechnet; alte und korrigierte Werte gegenübergestellt; Dokumentation und davon abhängige Fähigkeitssätze aktualisiert. Die Größenordnung der Scoreänderung und jede Änderung der Modellrangfolge bleiben bis dahin offen.

## 5. C1 — Zustandsschätzung und Beobachtbarkeit

### 5.1 Forschungsfrage und begrenzter Erstumfang

Verbessert die laufende Korrektur verborgener Speicherzustände die Vorhersage, und wann enthalten die Beobachtungen überhaupt genügend Information, um diese Zustände zu unterscheiden?

Erstumfang: lineare diskrete Zustandsmodelle mit angegebenen Matrizen, gaußschen unabhängigen Anfangs-/Prozess-/Messfehlern für die exakte Wahrscheinlichkeitsinterpretation, fehlenden Beobachtungen und ausdrücklich bekannten Zeitabständen. Unter schwächeren Annahmen die Aussage auf den optimalen linearen Schätzer begrenzen. Kein allgemeiner nichtlinearer Filter und keine automatische Trennung aller Unsicherheitsursachen.

Vorgeschlagene Dateien: `observation/linear_state_estimation.py`, `validation/hydrology_state_estimation.py`, zugehörige Dokumentation und zwei getrennte Prüfskripte für Mathematik und echte Daten.

### 5.2 Mathematischer Kern

Für Zustand als Spaltenvektor:

\[
x_{t+1}=F_tx_t+G_tu_t+w_t,\quad y_t=H_tx_t+D_tu_t+v_t,
\]

mit Kovarianzen W und R. Vorhersage und Messkorrektur werden getrennte Funktionen. Innovation, Innovationskovarianz, Mittelwert und Zustandskovarianz werden berichtet. Die Kalman-Rekursion ist die Literaturbasis [S1]; diese API-Zerlegung ist der Implementierungsvorschlag.

Numerisch: lineare Gleichungssysteme lösen, keine explizite Matrixinverse im produktiven Filter; Kovarianzkorrektur in Joseph-Form. Für den ersten Umfang positive definite Innovationskovarianz verlangen. Deterministische/noisefreie Beobachtungsgleichungen mit singulärer Innovationskovarianz entweder mathematisch eigens behandeln oder mit klarem Scopefehler ablehnen; kein heimlicher Pseudoinversen-Fallback.

Beobachtbarkeit bei festen F,H:

\[
\mathcal O=[H;HF;\ldots;HF^{n-1}].
\]

Analytische Rangresultate von numerischen Rangdiagnosen unterscheiden. Bei numerischen Diagnosen Skalierung und Singulärwerte mitberichten. Gleiche Reservoirraten können einen ununterscheidbaren Differenzmodus erzeugen. Fast gleiche Raten können trotz formaler Beobachtbarkeit eine schwache Rekonstruktion ergeben.

### 5.3 Kontrollfall mit festen Zahlen

\[
F=\operatorname{diag}(1/2,1/4),\quad H=(1,1),\quad
m^-=0,\ P^-=I,\ R=1,\ y=3,\ W=0.
\]

Dann:

\[
K=(1/3,1/3)^T,\quad m^+=(1,1)^T,\quad
P^+=\begin{pmatrix}2/3&-1/3\\-1/3&2/3\end{pmatrix}.
\]

Die nächste Beobachtung besitzt Erwartungswert 0.75 und Varianz 1.125 einschließlich Messrauschen. `det([H;HF])=-0.25`: beide Zustände sind bei bekannten Parametern beobachtbar. Bei `F=0.5 I` fällt der Rang auf 1; der Unterschied der beiden Zustände bleibt verborgen.

Unabhängige Prüfung: Konditionierung einer gemeinsam gaußschen Verteilung gegen sequenzielle Filterung, nicht zweimal dieselbe Filterfunktion aufrufen. Weitere Checks: fehlende Messung = reine Prädiktion; zwei ungemessene Schritte = korrekt zusammengesetzte Zweischrittfortpflanzung; spätere Messwertänderung lässt frühere Prognosen unverändert; Zustandspermutation ändert Beobachtungsvorhersagen nicht.

### 5.4 Tagesmittel richtig an Reservoirs anschließen

Die CAMELS-Auswertung verwendet Tagesmittel des Abflusses. Daher nicht versehentlich den momentanen Endabfluss `sum(k_i*S_i)` als Messoperator verwenden.

Mit konstantem Zufluss u über ein Intervall Δ, Raten k_i und Anteilen α_i gilt, abgeleitet aus dem bestehenden Reservoirmodell:

\[
F_{ii}=e^{-k_i\Delta},\quad
G_i=\alpha_i\Delta E(k_i\Delta),\quad
E(z)=\frac{1-e^{-z}}z,\ E(0)=1,
\]

\[
\bar q=H_\Delta S_{\rm start}+D_\Delta u,\quad
(H_\Delta)_i=k_iE(k_i\Delta),\quad
D_\Delta=\sum_i\alpha_i[1-E(k_i\Delta)].
\]

`expm1` beziehungsweise die vorhandenen stabilen Formeln wiederverwenden. Bei k_i=0 ist der Beitrag zum Abfluss null, während der Speicher Zufluss akkumuliert.

Die Messung des Tagesmittels betrifft den Anfangszustand und den Zufluss des gesamten Tages. Für den ersten stochastischen Adapter ein explizites diskretes Modell verwenden: Das Intervall ist bedingt auf seinen Anfangszustand deterministisch; unabhängiges Prozessrauschen wird am Übergang zum nächsten Intervall hinzugefügt. Nach Eingang von y_t erst den zugehörigen Anfangszustand korrigieren und dann zum nächsten Intervall propagieren. Das ist ein deklariertes Fehlermodell, keine Behauptung kontinuierlich wirkenden hydrologischen Weißrauschens.

Wird später Prozessrauschen innerhalb des Tages modelliert, entstehen mögliche Kreuzkovarianzen zwischen Intervallmessung und Endzustand. Diese müssen dann gemeinsam hergeleitet werden. Die Standardrekursion mit unabhängigen Fehlern darf nicht unverändert als exakt bezeichnet werden.

### 5.5 Realdatenversuch und Abnahme

Nach C0 ein 2×2-Panel: ein/zwei Speicher × ohne/mit Zustandskorrektur. Je Speicherzahl dieselben bereits im Training gefitteten dynamischen Parameter in beiden Varianten verwenden. So wird tatsächlich die Zustandskorrektur isoliert. Persistenz, Saisonreferenz und eine einfache trainierte AR(1)-Abflussbaseline ergänzen; letztere prüft, ob ein Gewinn vor allem durch Ausnutzung der zeitlichen Korrelation entsteht.

Protokoll vor dem Lauf einfrieren:

- Dynamische Parameter nur 1991–2005 fitten; Filterrauschen ausschließlich innerhalb dieses Trainingsbereichs mit zeitlich geordnetem innerem Validierungsfenster wählen. Kandidatenraum klein und protokolliert halten, z.B. skalierte diagonale W und skalares R.
- Zustand über 2006–2010 weiterführen; diese Jahre nicht nachträglich zum Tuning verwenden. Messkorrektur dort für die Filtervarianten ausdrücklich zulassen und dokumentieren.
- Test 2011–2020; Vorläufe 1, 3, 7 Tage; Vorhersage des jeweiligen Ziel-Tagesmittels. Kein Update mit Zielmessungen zwischen Ursprung und Ziel innerhalb derselben Prognose.
- Primär konditionaler Hindcast mit beobachteten zukünftigen Niederschlägen. Eine getrennte Treiberbaseline kann historische Niederschlagsszenarien verwenden, erbt aber keine operationelle Wetterprognosequalität.
- Primär MAE/RMSE auf gemeinsamen Fällen; für probabilistische Varianten zusätzlich 80%-Abdeckung, Intervallbreite und Intervallscore. Filtervarianz bei festgehaltenen Parametern als bedingte Unsicherheit kennzeichnen.
- Niedrigwassergrenze ausschließlich aus Training; Ergebnisse getrennt nach Vorlauf und Gebiet. Unsicherheit von Scoreunterschieden mit zeitlichen Blöcken statt unabhängigen Tagesstichproben untersuchen; keine Signifikanzpflicht als Erfolgskriterium.

Gaußsche Filter können negative Speicher oder Abflüsse liefern. Solche Ergebnisse samt Häufigkeit und Größenordnung berichten; niemals still auf null setzen und danach weiterhin exakte Kalman-Posterioren behaupten. Für physikalisch garantierte Positivität wäre später ein gesondertes Modell erforderlich. Direkte Sicherheitsentscheidungen auf Basis unbeschränkt gaußscher Zustandsfehler gehören nicht zur deterministischen Garantie dieses Pakets.

**Abnahme C1:** Kontrollfälle bestanden, Tagesmitteloperator gegengeprüft, Zukunftsleckagetest bestanden, sechs echte Gebiete vollständig ausgewertet, Null-/Negativergebnisse dokumentiert. Beobachtbarkeit bei gegebenen Parametern und deren Schätzunsicherheit getrennt berichtet. Ein neues, nach Metadaten vorab gewähltes Sechserpanel ist eine klar benannte Bestätigungsphase C1c; Auswahlregel, Protokollhash und unveränderte Auswertung müssen vor dem Lesen seiner Modellresultate feststehen.

## 6. C2 — Korrespondenzen unter deklarierten Aktionen

### 6.1 Wissenschaftlicher Anspruch

Erhält eine Mikro-Makro-Abbildung die Dynamik auch dann, wenn auf beiden Ebenen zugeordnete Eingriffe vorgenommen werden?

Das ist ein begrenzter, endlicher Anschluss an kausale Abstraktion [S2]. Kontrollierte Markov-Kerne sind hier vorgegebene Modelle. Der Prüfer entdeckt aus Beobachtungsdaten keine Kausalität und implementiert zunächst auch nicht die gesamte Theorie struktureller Kausalmodelle.

Vorschlag: `correspondence/controlled_markov.py`, `docs/controlled_correspondence.md`, `verification/verify_controlled_correspondence.py`. Vorhandene Closure-Prüfungen intern nutzen.

### 6.2 Vertrag und zulässiger Transfer

Zustandsverteilungen sind Zeilenvektoren. P^a ist ein zeilenstochastischer Mikrokern, Q^b ein Makrokern. C ist zunächst eine deterministische Partition: genau eine 1 je Mikrozeile, keine leere Makroklasse. ω ordnet jeder zugelassenen Mikroaktion eine Makroaktion zu.

Für jede deklarierte Aktion a wird geprüft:

\[
P^aC=CQ^{\omega(a)}.
\]

Der Bericht enthält die Aktionsmenge, ω, Defekt je Aktion, maximierende Mikrozeile, betroffene Makroklasse und den Ergebnisstatus. Ein Mittelwert über Aktionen darf einen einzelnen fehlgeschlagenen Eingriff nicht verstecken. Leere Aktionslisten ergeben keinen positiven Prüfbescheid.

Die Gleichung erlaubt durch wiederholtes Einsetzen den Transfer vorgegebener Aktionsfolgen. Für rückgekoppelte Strategien braucht es zusätzlich eine gemeinsame Politik, die nur die Makrohistorie verwendet, plus eine festgelegte zulässige Verfeinerung ihrer Aktionen. Mikrostrategien, die verborgene Unterschiede innerhalb einer Makroklasse ausnutzen, sind dadurch nicht automatisch abgedeckt.

Weitere Eigenschaften separat prüfen:

- **Ereignisse:** Ziel-/Sicherheitsmengen müssen Vereinigungen ganzer Partitionsblöcke sein.
- **Kosten:** `c_X(x,a)=c_Y(C(x),ω(a))` für den ausdrücklich übertragenen Kostenbegriff.
- **Zulässigkeit:** Aktionsbeschränkungen müssen auf der gewählten Verfeinerung erfüllt sein.

Erst nach diesen Zusatzprüfungen sind entsprechende Wahrscheinlichkeits- und Kostenvergleiche gerechtfertigt. Zustandskorrespondenz allein überträgt keine verborgene Ressourcengrenze.

### 6.3 Handrechenbares positives und negatives Beispiel

Vier Mikrozustände, zwei Klassen: `{0,1}` und `{2,3}`. Setze

\[
C=\begin{pmatrix}1&0\\1&0\\0&1\\0&1\end{pmatrix},\quad
P(a,b)=\begin{pmatrix}
a&0&1-a&0\\0&a&0&1-a\\b&0&1-b&0\\0&b&0&1-b
\end{pmatrix}.
\]

Dann ist `P(a,b) C = C Q(a,b)` mit

\[
Q(a,b)=\begin{pmatrix}a&1-a\\b&1-b\end{pmatrix}.
\]

Passiv: `(a,b)=(0.7,0.4)`. Eingriff: `(a,b)=(0.8,0.1)`. Beide Beziehungen gelten für jeden Startzustand. Auch die Folge passiv → Eingriff → Eingriff ist exakt übertragbar.

**Gegenfall:** Beim Eingriff die ersten beiden Zeilen durch `[0.9,0,0.1,0]` und `[0,0.7,0,0.3]` ersetzen. Dann erreicht Zustand 0 die zweite Klasse im nächsten Schritt mit Wahrscheinlichkeit 0.1, Zustand 1 mit 0.3. Eine einzige Makrozeile kann beides nicht exakt darstellen. Ihr bester minimax-Wert ist 0.2 mit maximalem Zeilen-TV-Fehler 0.1. Die passive Korrespondenz bleibt trotzdem exakt.

Zweiter Gegenfall: Das Ereignis „Zustand 0 erreicht“ schneidet eine Klasse. Auch das positive Modell erhält dieses Ereignis nicht als binäres Makroereignis ohne zusätzliche Zustandsinformation.

### 6.4 Abnahme und Anschluss

Alle Basiszustände und Aktionen vollständig prüfen; unabhängige direkte Pfadenumeration für kurze Horizonte gegen Matrixprodukte vergleichen. Nichtstochastische Matrizen, ungültige Partitionen, fehlende Aktionszuordnungen und unzulässige Strategieverfeinerung zurückweisen.

Eine vorgegebene Lift-Verteilung darf einen Kandidaten Q erzeugen, ersetzt aber nicht die Prüfung für alle Mikrozeilen. Entsprechenden Gegenfall fest verankern. Approximationen zunächst nur als Defekte berichten. Eine globale Fehler- oder Politikgarantie benötigt ihren eigenen Satz und bleibt außerhalb des ersten Pakets.

**Abnahme C2:** positiver Fall, Eingriffsgegenfall und Ereignisgegenfall reproduziert; Bericht unterscheidet Dynamik-, Ereignis-, Kosten- und Zulässigkeitserhaltung. Keine automatische Aufwertung zur empirisch bewiesenen kausalen Identität.

## 7. C3 — Verweildauern und verteilte Verzögerungen

### 7.1 Leitfrage und Umfang

Wie ändern Form und Streuung einer Verzögerungsverteilung die Antwort eines Systems, wenn mittlere Verzögerung und gesamte Eingangslast festgehalten werden?

Die Literatur zum Generalized Linear Chain Trick [S3] erlaubt die Darstellung geeigneter Verweildauerverteilungen durch zusätzliche Zustände. Für SCF zunächst endliche Erlang-Ketten und kleine Phasentyp-Verteilungen mit konstanten Raten; kein allgemeiner Verzögerungsdifferentialgleichungslöser.

Vorschlag: `dynamics/phase_type_delays.py`, `validation/distributed_delay_pilot.py`, entsprechende Dokumentation und Mathematik-Suiten. Lineare Reservoirs in Reihe sind von den bereits vorhandenen parallelen Reservoirs zu unterscheiden.

### 7.2 Eigene Spezialisierung und Bilanz

Eine Erlang-Kette mit n Stufen und λ=n/τ hat mittlere Verweildauer τ und Varianz τ²/n:

\[
\dot z_1=u-\lambda z_1,\qquad
\dot z_j=\lambda z_{j-1}-\lambda z_j,\qquad
y=\lambda z_n.
\]

Die Impulsantwort für t≥0 lautet

\[
h_n(t)=\frac{\lambda^n t^{n-1}e^{-\lambda t}}{(n-1)!}.
\]

Für eine allgemeine endliche Phasentyp-Verteilung mit Zeilenvektor α, transientem Subgenerator T und Austrittsraten `r=-T 1`:

\[
\dot z=zT+u\alpha,\quad y=zr,\quad
h(t)=\alpha e^{Tt}r,\quad E[\tau]=\alpha(-T)^{-1}\mathbf1.
\]

Voraussetzungen: α≥0, α1=1, nichtnegative Nebendiagonalen von T, nichtpositive Zeilensummen und tatsächliche Transienz der von α erreichbaren Phasen. Ein geschlossener nichtabsorbierender Teil ist keine reguläre Verweildauerverteilung mit endlichem Mittelwert. Insbesondere keine scheinbar plausible CDF aus einem ungeprüften Subgenerator erzeugen.

Die Massenbilanz `d(z1)/dt=u-y` muss gelten. Anfangsbelegung explizit führen; Nullanfang darf nicht stillschweigend auf bereits gefüllte Transportketten übertragen werden.

Für stückweise konstanten Eingang exakte lineare Updates per Matrixexponential beziehungsweise augmentierter Blockmatrix. Kein allgemeines T-Invertieren für jeden Schritt; stabile spezielle Erlang-Formeln als unabhängige Kontrollrechnung nutzen.

### 7.3 Kontrollzahlen und ein wichtiger Gegenfall

Mittlere Verweildauer jeweils 1. Exponentialfall n=1: `h_1(t)=exp(-t)`, `F_1(t)=1-exp(-t)`. Erlang n=2: `h_2(t)=4t exp(-2t)`, `F_2(t)=1-exp(-2t)(1+2t)`.

| Horizont t | F₁(t) | F₂(t) |
|---:|---:|---:|
| 0.25 | 0.221199216929 | 0.090204010431 |
| 1 | 0.632120558829 | 0.593994150290 |
| 2 | 0.864664716763 | 0.908421805556 |

Die Rangfolge wechselt. Eine kleinere Verweildauerstreuung bedeutet somit keine einheitliche Ordnung aller Ankunftswahrscheinlichkeiten über alle Horizonte. Der Erlang-Impuls hat sein Maximum bei t=0.5 mit Höhe `2/e=0.735758882343`; der exponentielle Impuls startet bei Höhe 1.

Diese CDFs beschreiben die Verweildauer eines einzelnen Teilchens beziehungsweise die normierte deterministische Sprungantwort. Sie sind nicht bereits die Durchbruchswahrscheinlichkeit einer stochastischen Warteschlange. Wenn später Wartezeiten modelliert werden, muss der gemeinsame Prozess separat konstruiert werden.

### 7.4 Versuch und Ereignislokalisierung

Vorab festgelegte Familie: n∈{1,2,4,8}, τ=1; gleiche Einheitsmasse als kurzer Rechteckimpuls, gleiche Anfangsbelegung null. Eingangsbreite beispielsweise 0.2. Einen downstream-Puffer mit identischem Abfluss-/Kapazitätsmodell anschließen. Ausweisen: zeitlicher Ausgangspeak, verbleibende Masse, Minimum der Reserve, erster definierter Grenzdurchgang.

Für den ersten gemeinsamen Lauf die Parameter fest setzen: `u(t)=5` auf `[0,0.2)`, danach 0; Horizont 5. Die verzögerte Ausgabe y belastet eine Reserve mit `R(0)=0.1` und `dR/dt=0.4-y(t)`. Ereignis: erstes Erreichen von `R≤0`. Keine Reflexion oder stille Kappung bei null; der ungehemmte Verlauf bleibt zur Diagnose sichtbar. Die Größen sind in einer festgelegten Ressourcen- und Zeiteinheit normiert. Der Versuch darf durch weitere vorab deklarierte Fälle ergänzt werden, seine Parameter werden aber nicht nach einer gewünschten Rangfolge ausgewählt.

Die isolierte Durchlaufverteilung und der nachgeschaltete Puffer sind getrennte Ausgaben. Eine Veränderung des Peaks muss nicht dieselbe Richtung wie eine Veränderung des minimalen Puffers haben. Einheiten und Eingangsintegral bleiben bei jedem Vergleich gleich.

Für allgemeine Phasentyp-Kerne mit mehreren Zeitskalen keine globale Extremsicherheit aus einem festen Zeitraster behaupten. Im Erstumfang analytisch lösbare Erlang-Kontrollfälle exakt behandeln. Für allgemeinere Kurven Root-Bracketing/Verfeinerung mit offengelegter numerischer Reichweite verwenden; bei fehlender vollständiger Lokalisierung `undetermined` statt „garantiert sicher“. Kein Wiederauftreten der früheren Peaksuche-Probleme durch versteckte Rasterannahmen.

Weitere Regressionen: n=1 entspricht einem linearen Ein-Speicher-System; Massenbilanz; identische Segmente zusammenlegen ändert nichts; positive Eingänge erhalten nichtnegative Zustände; Zeiten und Raten konsistent umskalieren; initial belegte Kette trägt ihren eigenen Ausfluss bei.

Der Grenzübergang n→∞ nähert eine feste Verzögerung in geeigneter Verteilungskonvergenz an. Endliche n sind keine exakte feste Verzögerung; insbesondere keine pauschale gleichmäßige Näherung aller Frequenzen und Ereigniszeiten behaupten.

**Abnahme C3:** CDF-Tabelle, Impulsmaximum, Bilanz und Ein-Speicher-Grenzfall stimmen; Lastversuch für alle vier n vollständig dokumentiert. Ein erster realer Fit von Verzögerungsverteilungen bleibt eine getrennte Studie und ist nicht erforderlich, um diesen mathematischen Baustein ehrlich abzuschließen.

## 8. C4 — Konkurrierende Ziele, Kommittoren und Ereigniserhaltung

### 8.1 Abgegrenzte Fähigkeit

SCF soll für endliche CTMC beantworten können: Wird ein Ausfallbereich B vor einem Erholungsbereich A erreicht? Wie lange dauert es bis zu einem der beiden? Erhält eine Reduktion diese Aussage?

Die Kommittorfunktion ist ein Grundbaustein der Transition-Path-Theorie [S4]. Das erste Paket umfasst das Randwertproblem und endliche Horizonte. Stationäre reaktive Ströme benötigen zusätzliche Voraussetzungen und werden nicht automatisch für absorbierende Ketten ausgegeben.

Vorschlag: `viability/competing_first_passage.py`, `docs/competing_first_passage.md`, `verification/verify_competing_first_passage.py`. Einen generischen endlichen Generatorprüfer nur so weit herausziehen, wie dieses Paket und der vorhandene Queue-Code ihn gemeinsam benötigen.

### 8.2 Definition und wohldefinierte Lösung

Generator L mit Zeilensumme null, disjunkte nichtleere Mengen A,B, Randzeit `τ=τ_A∧τ_B`. Für innere Zustände D:

\[
q_i=P_i(\tau_B<\tau_A),\quad q|_A=0,\ q|_B=1,
\]

\[
L_{DD}q_D=-L_{DB}\mathbf1,\qquad
L_{DD}m_D=-\mathbf1.
\]

Die eindeutige erste Version verlangt: von jedem betrachteten inneren Zustand wird A∪B fast sicher erreicht. Bei endlichen Ketten kann das anhand erreichbarer abgeschlossener Klassen geprüft werden. Andernfalls kann L_DD singulär und die unbedingte mittlere Randzeit unendlich sein. Kein Pseudoinversen-Ergebnis als Trefferwahrscheinlichkeit deklarieren.

Eine spätere allgemeinere Variante darf zusätzliche geschlossene Klassen als Nichttreffer-Ergebnis ausweisen und minimale nichtnegative Trefferlösungen bestimmen. Für den ersten Umfang reicht ein genauer Scopefehler mit Zeugenklasse.

Für endliches H die beiden Ränder absorbierend machen und die Wahrscheinlichkeiten `p_A(H)`, `p_B(H)` sowie `p_unresolved(H)` aus dem Matrixexponential bestimmen. Sie summieren sich zu 1. Ein endlicher Horizont ist nicht das stationäre oder unendliche Kommittorproblem.

### 8.3 Exakter Vier-Zustands-Fall

Reihenfolge `(A,i,j,B)`. A,B absorbierend. Übergänge: `i→A` Rate 1, `i→j` Rate 2, `j→i` Rate 1, `j→B` Rate 3. Dann:

\[
3q_i=2q_j,\quad4q_j=q_i+3
\quad\Rightarrow\quad(q_i,q_j)=(0.6,0.9).
\]

Die mittleren Zeiten bis A∪B sind `(m_i,m_j)=(0.6,0.4)` Zeiteinheiten. Für H=1 ergibt ein separat berechnetes Matrixexponential `p_B=(0.467359895563,0.829637179582)` — kleiner als die jeweiligen unendlichen Trefferwahrscheinlichkeiten.

Multiplikation aller Raten mit c>0 lässt q unverändert und teilt die mittleren Zeiten durch c. Bei gleichzeitigem H→H/c bleiben auch die endlichen Trefferwahrscheinlichkeiten gleich.

### 8.4 Brücke zu C2 und Prüfung

Bei exakter Generator-Lumpability `LC=C L_macro` und Randmengen aus ganzen Blöcken ist die projizierte Kette wohldefiniert. Unter den genannten Eindeutigkeitsbedingungen stimmt der hochgezogene Makrokommittor mit dem Mikrokommittor überein. Dies direkt am Randwertproblem und unabhängig über kurze/geeignete endliche Horizonte prüfen.

Negativfall: Eine Reduktion fasst unterschiedlich riskante innere Zustände zusammen; fehlende Lumpability oder ein von der Grenze geschnittener Block muss ausdrücklich sichtbar werden. Geringer Fehler einer gemittelten Trajektorie reicht als Begründung nicht aus.

**Abnahme C4:** exakte q/m-Werte, endliche Massensumme, Start im Rand, unerreichbarer Rand, zusätzliche geschlossene Klasse, Zeitreskalierung und positiver/negativer Aggregationsfall. Vollständige Transition-Path-Ströme sind als spätere Erweiterung C4b mit Ergodizitätsprüfung benannt, nicht als bereits umgesetzt ausgewiesen.

## 9. C5 — Kleine Ressourcennetzwerke mit wiederholten Eingriffen

### 9.1 Modell und erste Grenzen

Untersucht werden drei bis fünf Speicher, die über gerichtete, kapazitätsbegrenzte Flüsse Ressourcen austauschen. Zustand x, externe Zuführung u, Abflüsse d, gerichtete Kantenflüsse f und Inzidenzmatrix B:

\[
\dot x=Bf+u-d.
\]

Jede Spalte von B enthält −1 am Ursprung und +1 am Ziel. Innere Flüsse erhalten daher die Gesamtressource. Anfangs nur verlustfreie Übertragung und stückweise konstante, während eines Regelintervalls gehaltene Flüsse/Eingriffe. Nichtlineare Druck-Fluss-Beziehungen und stochastische Ausfälle sind weitere Modellklassen.

Vorschlag: `viability/resource_network_control.py`, `validation/resource_network_pilot.py`, je eine Dokumentation und mathematische Verifikation. Den bisherigen Zwei-Puffer-Fall als entkoppelten Spezialfall wiederfinden, ohne seine API umzudeuten.

### 9.2 Sicherheit über das ganze Regelintervall

Für Intervalllänge Δ, sichere Anfangszustände und konstante u,f,d ist jede Komponente von x affin in der Zeit. Bei der unteren Grenze 0 genügt deshalb die Prüfung beider Endpunkte. Mit harten Anfangs- und Störungsgrenzen `x(0)≥x_lower≥0` und `d(t)≤d_upper` ist folgende robuste Bedingung hinreichend:

\[
x_{\rm lower}+\Delta(Bf+u-d_{\rm upper})\ge0.
\]

Der tatsächliche Zustand liegt über einer affinen unteren Schranke, deren beide Endpunkte nichtnegativ sind. Diese kurze eigene Ableitung ist die Garantie des ersten Piloten. Falls obere Kapazitäten K relevant sind, zusätzlich mit x_upper und d_lower eine affine obere Schranke über das ganze Intervall prüfen.

Mögliche quadratische Zielfunktion: `sum_i w_i*u_i² + sum_e v_e*f_e²`, mit deklarierten Einheiten/Gewichten und nichtnegativen Gewichten. Nebenbedingungen: Eingriffsgrenzen, Kantenkapazitäten, gemeinsames momentanes Zuführungsbudget und die Intervallschranken. Ein endliches Gesamtbudget über die Versuchsdauer ist eine eigene Zustandsgröße; nicht mit einem Ratenbudget verwechseln.

Nach jedem Intervall Zustand/Messung aktualisieren und neu optimieren. Protokollieren, ob die Voraussetzungen des nächsten Intervalls noch erfüllt sind. Ein erfolgreiches erstes QP beweist keine unendliche Sicherheit oder rekursive Zulässigkeit.

Die Verbindung zu sampled-data CBFs und Eingangsverzögerungen ist durch [S5] motiviert. Deren weitergehende Sätze werden erst nach Prüfung ihrer Voraussetzungen übernommen. Das erste Paket braucht für sein affines Modell keine pauschale Übernahme einer allgemeinen CBF-Garantie.

### 9.3 Festes Kontrollbeispiel

Drei entkoppelte Puffer, `x=(0.2,0.4,0.6)`, `d=(1,1,1)`, `0≤u_i≤2`, gemeinsames Ratenbudget 2.

- Für Δ=1 sind die kleinsten sicheren Eingriffe `(0.8,0.6,0.4)`, Summe 1.8, quadratische Kosten 1.16.
- Für Δ=2 werden mindestens `(0.9,0.8,0.7)` benötigt, Summe 2.4: unter Budget 2 unzulässig.
- Hält man die für Δ=1 geeigneten Eingriffe zwei Zeiteinheiten, endet x bei `(-0.2,-0.4,-0.6)`.

Hier sind die Sicherheitsmengen geschlossen: x=0 am Intervallende ist zulässig. Eine separat berichtete Erstberührung bei x≤0 ist deshalb nicht gleichbedeutend mit einer strikten Verletzung x<0. Ereignisdefinitionen ausdrücklich unterscheiden.

Für unsichere Anfangszustände gilt: Ein Unsicherheitsintervall, das negative Werte einschließt, bedeutet „Sicherheit nicht für alle möglichen Anfangszustände belegt“. Es bedeutet nicht, dass der wahre Zustand nachweislich schon negativ ist. Dies als eigenen Status behandeln.

### 9.4 Netzwerkversuch und notwendiger Negativcheck

Topologien: entkoppelt, gerichtete Kette, Kette mit einer zusätzlichen optionalen Kante. Gleiche Anfangsressourcen, Lastverläufe und Budgets. Strategien: keine Umverteilung, feste Routingregel, Optimierung mit Intervallschranken. Vorab festgelegte Lastpulse und ein zeitlich begrenzter Kantenausfall; der Ausfallzeitpunkt ist entweder bekannt oder als Störung deklariert, nicht rückwirkend in den Regler eingespeist.

Konkretes erstes Panel: drei Knoten, `x(0)=(0.6,0.6,0.6)`, obere Kapazitäten 2, Grundlast je 0.3, Zusatzlast 0.9 an Knoten 0 auf `[1,2)` und an Knoten 2 auf `[3,4)`, Horizont 6. `0≤u_i≤0.6`, Gesamtzuführung höchstens 0.9; Kantenkapazität je 0.4. Kette `0→1→2`, Zusatzkante `2→0`. Regelintervalle 0.25 und 1; bekannte Lastwechsel an Intervallgrenzen. Baseline: `u=(0.3,0.3,0.3)`, keine Flüsse; feste Routingregel zusätzlich je 0.2 entlang der Kette. Im QP normierte Gewichte `w_i=1`, `v_e=0.1`. Ein separater Ausfallfall sperrt `1→2` auf `[3,4)` und deklariert dies im ersten Versuch als zum Ursprung bekannt. Diese Fälle demonstrieren das Modell und sind keine empirischen Netzdaten.

Berichten: minimale Reserve, strikte Grenzverletzung/Erstberührung getrennt, Eingriffskosten, transportierte Menge, Unzulässigkeitszeitpunkt und Ursache. Für kleine Beispiele den Solver unabhängig durch geschlossene Lösungen oder vollständige aktive-Mengen-Prüfung absichern. `optimizer_failed` ist kein Beweis für `infeasible`.

**Struktureller Gegencheck:** Wird eine frei abschaltbare Kante hinzugefügt und bleibt alles andere identisch, enthält die neue zulässige Menge die alte als Spezialfall `f_new=0`. Das optimale Minimum derselben Kostenfunktion kann sich daher nicht verschlechtern. Ein negativer Vernetzungseffekt braucht benannte zusätzliche Mechanismen, etwa vorgeschriebenes Routing, Verzögerungen, nichtabschaltbare Flüsse, Kosten der Verbindung oder begrenzte Information. Einen behaupteten Schaden allein durch Hinzufügen einer optionalen Kante als Fehler markieren.

C3 kann danach eine Transportverzögerung ergänzen. In diesem Fall liegt Ressource während des Transports in expliziten Zwischenzuständen; sie darf nicht gleichzeitig am Ziel gutgeschrieben werden. Der einfache direkte Flussterm und die Garantie oben sind dann entsprechend neu herzuleiten.

**Abnahme C5:** exakte Kontrollwerte; Bilanz einschließlich Transportzuständen, falls vorhanden; Sicherheit innerhalb jedes gesamten Regelintervalls; klare Unterscheidung von Solverfehler, Budgetkonflikt, lokalen Grenzen und nicht zertifizierbarem Anfangszustand. Ein C1-Konfidenzintervall darf nicht ohne zusätzliche probabilistische Argumentation als harte robuste Schranke eingesetzt werden.

## 10. C6 — Wiederholte Kooperation und Wert zusätzlicher Information

### 10.1 Forschungsfrage und Basismodell

Wann lohnt eine zusätzliche Beobachtung oder Nachricht, wenn ein Zustand sich verändert, Information veraltet und jede Abfrage Ressourcen kostet?

Erster Umfang: endlicher verborgener Markov-Zustand, endliche Nachrichten und Aktionen, kurzer endlicher Horizont. Exakte Enumeration oder dynamische Programmierung auf den endlich erreichbaren Glaubenszuständen. Keine LLM-Abhängigkeit und kein generischer POMDP-Frameworkzwang.

Vorschlag: `validation/sequential_information_pilot.py`, bei echtem zweiten Nutzer ein kleiner Kern unter `observation/decision_value.py`, `verification/verify_sequential_information_value.py`.

Der Beobachter kennt X_t; der Entscheider erhält auf eigene Anfrage eine Nachricht und sagt X_t voraus. Zunächst kann die Anfrage keine Zustandsübergänge beeinflussen. Diese Einschränkung trennt Informationsgewinn von physischem Eingriff. Blackwells Vergleich von Experimenten [S6] ist der wissenschaftliche Anschluss für den Wert von Beobachtungskanälen; die dynamische Kostenaufgabe wird hier eigenständig spezifiziert.

### 10.2 Zeitablauf muss Teil des Modells sein

Je Stufe: zugelassene alte Nachrichten treffen ein → Glaubenszustand aktualisieren → gegebenenfalls Messung anfordern und vereinbarte Kosten zahlen → im unmittelbaren Basismodell Antwort erhalten → Entscheidung ausgeben → Zustand wechselt zur nächsten Stufe. Verzögerte Varianten führen ihren eigenen Versand-/Empfangszeitstempel.

Die tatsächliche Treffer-Rückmeldung wird im Basismodell erst nach Episodenende offengelegt. Eine sofortige Rückmeldung könnte sonst selbst eine zusätzliche Messung über X_t liefern und die beabsichtigte Informationslage verändern.

Anfragen werden vom Entscheider anhand seiner verfügbaren Historie ausgelöst. Falls später der informierte Sender abhängig vom verborgenen Zustand selbst entscheidet, ob er sendet, trägt auch Schweigen Information. Dann ist die Nichtnachricht ein explizites Beobachtungssymbol; sie darf nicht still ignoriert werden.

### 10.3 Exakter Zwei-Stufen-Fall

Binärer Zustand mit Anfangswahrscheinlichkeit `P(X_0=1)=0.5`, Wechselwahrscheinlichkeit p=0.1 je Schritt. Eine unmittelbare perfekte Abfrage kostet c=0.2, richtige Entscheidung bringt 1, falsche 0. Zwei Entscheidungen, Gesamtwert als Summe.

- Nie messen: erwarteter Gesamtwert 1.0.
- Immer messen: Gesamtwert `2*(1-0.2)=1.6`.
- Zuerst messen, danach die Zustandsstetigkeit nutzen: `(1-0.2)+0.9=1.7`.

Mit Glaubenszustand b=P(X_t=1) und T(b)=p+(1−2p)b ist die Rekursion für h verbleibende Stufen:

\[
V_0(b)=0,
\]

\[
V_h(b)=\max\left\{
\max(b,1-b)+V_{h-1}(T(b)),\quad
1-c+bV_{h-1}(T(1))+(1-b)V_{h-1}(T(0))
\right\}.
\]

Daraus folgt `V_2(0.5)=1.7`. Direkte Enumeration aller zulässigen Entscheidungs-/Abfragebäume muss denselben Wert ergeben. Das ist ein eigenständig abgeleiteter Referenzfall, keine Behauptung über allgemeine Agentenleistung.

### 10.4 Alterung von Nachrichten und Kosten

Nach einer perfekten Beobachtung von X_0 beträgt ohne weitere Information die optimale Trefferrate für X_d beim symmetrischen binären Übergang:

\[
\frac12+\frac12\left|1-2p\right|^d.
\]

Für p=0.1: d=1 ergibt 0.9, d=2 ergibt 0.82, d=10 ergibt 0.5536870912. Bei p>0.5 muss der optimale Decoder mögliche Alternation berücksichtigen; einfaches Kopieren wäre dann die falsche Referenz. Bei p=0.5 ist jede ältere Beobachtung für die neue unabhängige Stufe nutzlos; eine unmittelbare Messung bleibt nützlich.

Ein perfektes zusätzliches Signal kann bei kostenfreier optionaler Nutzung den optimalen erwarteten Nutzen nicht senken: Die alte Strategie bleibt verfügbar. Dieser Einschluss ist ein Pflichtcheck. Bei positiven Kosten können Immer-Senden und Immer-Messen schlechter sein als selektive Nutzung. Ein schlechter festgelegter Decoder kann mehr Information falsch verwenden; das ist ein Decoderbefund, keine Widerlegung des optimalen Informationswerts.

### 10.5 Versuch und Anschluss an bestehende Agentenaufgaben

Parameterpanel vorab: p∈{0,0.1,0.5,0.9}, c∈{0,0.1,0.2,0.5,0.6}, Verzögerung d∈{0,1,2}, kurzer Horizont H≤5. Zunächst perfekte Nachrichten; danach genau ein symmetrischer Fehlerkanal mit explizit optimalem und naivem Decoder. Berichten: erwartete Trefferzahl, Anzahl/Kosten von Nachrichten, Nettowert und Informationsstand jeder Strategie.

Bestehende XOR-/Redundanztests bleiben erhalten. Als Brücke eine wiederholte XOR-Variante ergänzen, in der beide lokalen Bits zeitlich wechseln. PID weiterhin für eine ausdrücklich definierte Quellen-Ziel-Verteilung berechnen; marginale PID über zusammengeworfene Zeitpunkte ist keine dynamische Erfolgs- oder Kausalitätsgarantie. Informationswerte und Aufgabennutzen nebeneinander ausgeben.

**Abnahme C6:** Zwei-Stufen-Optimum 1.7, Alterungsformel, kostenloser Optionswert, Redundanz-/Unabhängigkeitsgrenzen und Informationsschnitt korrekt; direkte Enumeration gegen Rekursion geprüft. Keine Aussage über allgemeine Intelligenz aus diesen Spielumgebungen ableiten.

## 11. C7 — Integration, Nachweis und Abschluss

### 11.1 Dokumentationsprodukte

Eine neue `INTEGRATED_EXTENSION_ROADMAP.md` führt C0–C7, Teilumfänge, Commit und Ergebnisstatus. Jede neue Fähigkeit bekommt in `docs/capability_overview.md` und `.json` dieselben Felder wie die vorhandenen Module: Frage, Modellklasse, Voraussetzungen, Evidenz, Prüfskript, Grenze.

Eine Vergleichsseite beantwortet pro Paket:

| Frage | Zu berichtender Inhalt |
|---|---|
| Welche Information fehlte zuvor? | Zustand, Eingriffsabbildung, Verweildauerform, konkurrierendes Ziel, Netzrestriktion oder Nachrichtenzeit |
| Was wurde neu prüfbar? | Konkrete Größe und Modellklasse |
| Wann reicht die einfachere Darstellung? | Positiver Reduktions-/Baselinefall |
| Wann scheitert die Übertragung? | Kleinstes reproduzierbares Gegenbeispiel |
| Was ist empirisch untersucht? | Datensatz, Zeitraum, Auswertemodus, vorherige Einsicht in Ergebnisse |
| Was bleibt offen? | Benannte Teilaufgabe mit Voraussetzung, keine pauschale Erfolgsmarkierung |

Mathematik-Suiten benötigen kein Netzwerk. Daten-Suiten nutzen vorhandene kleine Auszüge und dokumentierte Hashes. Online-Downloader und Bestätigungspanel bleiben getrennte Reproduktionsschritte. Die vorhandenen Kategorien math/data/links und deren explizite Registrierung beibehalten.

### 11.2 Übergreifende Abschlusskriterien

1. Alle neuen analytischen Kontrollfälle sind mit unabhängiger Rechnung nachvollzogen.
2. Zeitachse, Intervallmessung und Verfügbarkeit sind im Code und in der Dokumentation gleich definiert.
3. Neue Funktionen sind additiv; historische Tests und bestehende APIs bleiben nutzbar oder erhalten einen klaren Migrationshinweis.
4. Negative und uneindeutige Resultate erscheinen im Hauptbericht.
5. „Exakt“ nennt die Modellannahmen und unterscheidet Formel von Gleitkommaauswertung.
6. Statistische Ungewissheit, numerische Unsicherheit und Modellabweichung sind getrennt.
7. Alle vorgesehenen neuen Prüfskripte sind registriert; vollständige Regression und Linkprüfung am Abschlussstand durchgeführt.
8. Zurückgestellte C1c/C4b und weitergehende nichtlineare/stochastische Erweiterungen sind sichtbar benannt. Die sechs Kernfähigkeiten werden dadurch nicht stillschweigend reduziert.

## 12. Aufwand und natürliche neue Anwendungsgebiete

Die folgenden Größen sind relative Implementierungsrisiken, keine Zeitversprechen:

| Paket | Relativer Aufwand | Größter fachlicher Stolperstein |
|---|---|---|
| C0 | klein | Scoremasken versehentlich als Simulationsachse benutzen |
| C1 | groß | Tagesmitteloperator, Initialisierung, Rauschmodell und Informationsschnitt |
| C2 | mittel | Gleichheit unter einer Startverteilung mit Gleichheit für alle Zustände verwechseln |
| C3 | mittel | Verteilung/Erwartungswert/Prozessrisiko und Serien-/Parallelspeicher verwechseln |
| C4 | mittel | Nichtabsorbierende Klassen, unendlicher Horizont und Ereignisverträglichkeit |
| C5 | groß | Sicherheit zwischen Abtastzeitpunkten, Unsicherheit und rekursive Zulässigkeit |
| C6 | mittel bis groß | Versteckte Informationskanäle durch Schweigen, Feedback und verspätete Nachrichten |
| C7 | klein bis mittel | Mehr Fähigkeiten behaupten, als die ausgeführten Fälle tragen |

Die erste Etappe C0–C3 ist bereits ein sinnvoller eigenständiger Zwischenstand. Der vollständige Umfang dieses Plans bleibt C0–C7.

### 12.1 Energie und Speicher

Erster Pilot: synthetische Last-/Erzeugungsprofile, Speichergrenzen, Lade-/Entladeraten und Messverzögerung. Eigene Energiebilanz samt Wirkungsgraden herleiten. Ein abstrakter Puffer ist nicht automatisch ein vollständiges Batteriemodell. Anschluss an C1/C5; reale Lastdaten erst nach Festlegung von Auflösung, Prognosefrage und zulässigem Informationsstand.

### 12.2 Lieferketten, Produktion und Reparatur

Erster Pilot: zwei Produktionsstufen und ein Reparaturzustand; gleiche mittlere Liefer-/Reparaturdauer, verschiedene Verteilungen. Gemeinsame Nachschubbudgets und Engpässe. C3 liefert Verzögerungen, C4 konkurrierende Wiederanlauf-/Ausfallziele, C5 begrenzte Ressourcen. Ein kleiner vollständig enumerierbarer synthetischer Prozess genügt für die erste Aussage.

### 12.3 Ökologie und wiederholte Belastung

Erster Pilot: endlicher Geburts-/Todesprozess mit Erholungs- und Niedrigbestandsgrenze unter zeitlich definierten Störungen. C4 für konstante Regime, zeitabhängige Generatoren später eigens behandeln. Populationsgrößen brauchen diskrete Prozessannahmen; hydrologische Speicherparameter werden nicht übertragen. Reale Monitoringdaten wären eine spätere, eigenständige Validierung.

### 12.4 Kooperative Systeme und Sensornetze

C6 zuerst exakt; danach zwei Sensoren mit unterschiedlicher Genauigkeit, Kosten und Laufzeit. Prüffrage: Welcher Sensor verändert die Entscheidung, und welche zeitlich veraltete Information kann noch genutzt werden? Das passt zu einer späteren transparenten Agentenkoordination, ohne die Spielresultate bereits auf offene Sprachagenten zu verallgemeinern.

**Erweiterungsregel:** Ein neues Gebiet wird aufgenommen, sobald es eine zusätzliche mathematische Annahme, einen unabhängigen Datenvergleich oder einen neuen Gegenfall beiträgt. Dieselbe Rechnung mit ausgetauschten Variablennamen ist eine Illustration, keine neue Validierung.

## 13. Ausgeführte Kontrollrechnungen dieser Ausarbeitung

Die Kontrollzahlen wurden lokal mit NumPy 2.3.5 / SciPy 1.17.0 nachgerechnet. Referenzfunktionen waren eigenständige kleine Rechnungen; für C0 wurden die unveränderte Pilotfunktion mit protokollierenden Fit-/Simulationsstubs und die originale Persistenzanweisung isoliert ausgeführt. Ein zunächst fehlender `Optional`-Name im Test-Harness wurde ergänzt, anschließend liefen alle unten aufgeführten Rechnungen erfolgreich. Das ist keine Produktions-Testfreigabe der vorgeschlagenen Module.

| Paket | Geprüft | Ergebnis |
|---|---|---|
| C0 | Vollkalender 2005–2011; Training 2005/Test 2011 | 2556 Tage vorhanden, 730 Simulationsschritte, 1826 ausgelassen |
| C0 | Originale Persistenzanweisung | erster Prognosewert = aktueller erster Zielwert |
| C1 | Gauß-Korrektur und Folgeschritt | K=(1/3,1/3), nächste Beobachtung: Mittel 0.75, Varianz 1.125 |
| C2 | Positive Matrizen und aktionsabhängiger Gegenfall | positive Residuen <6e−17; Gegenfall verlangt 0.1 und 0.3 für dieselbe Makrozeile |
| C3 | Geschlossene Erlang-/Exponentialformeln | CDF-Rangfolge wechselt zwischen Horizont 1 und 2 |
| C4 | Zwei lineare Gleichungssysteme und Matrixexponential | q=(0.6,0.9), m=(0.6,0.4), endliche Werte wie oben |
| C5 | Intervallbedingungen und gehaltene Eingriffe | benötigte Budgets 1.8 bzw. 2.4; Kosten bei Δ=1: 1.16 |
| C6 | Bellman-Rekursion im Zwei-Stufen-Fall | optimal 1.7 gegenüber 1.6 immer / 1.0 nie |

Für C0 wurde der Quelltext unter dem oben genannten Commit gelesen. Lokale SHA-256 der UTF-8-Quelltextkopie: `3f73250993d46e7f7225705a11f5fa6062e28d880bbd8d3818ed743efb5c131c`. Dies ist die Prüfsumme der gelesenen Textkopie und kein Git-Blob-SHA.

## 14. Primärquellen und ihre konkrete Rolle

Alle Quellen am 25.09.2026 geprüft. Die Quellen stützen den jeweiligen Methodenanschluss; die konkreten SCF-Pakete, Kontrollzahlen und Versuchsanordnungen sind Vorschläge beziehungsweise eigene Ableitungen dieses Dokuments.

- **[S1] Kalman, R. E. (1960):** *A New Approach to Linear Filtering and Prediction Problems*. Journal of Basic Engineering 82, 35–45. DOI: [10.1115/1.3662552](https://doi.org/10.1115/1.3662552). [Originalarbeit als Hochschul-PDF](https://people.math.harvard.edu/archive/116_fall_03/handouts/Kalman1960.pdf). Grundlage der linearen Zustandsschätzung; keine hydrologische Validierung des hier vorgeschlagenen Adapters.
- **[S2] Beckers, S.; Halpern, J. Y. (2019):** *Abstracting Causal Models*. AAAI. [Autorenfassung](https://arxiv.org/abs/1812.03789). Präzise Unterscheidungen kausaler Abstraktion und Interventionsumfang. C2 ist ein begrenzter kontrollierter Markov-Fall, keine vollständige Umsetzung dieser Theorie.
- **[S3] Hurtado, P. J.; Kirosingh, A. S. (2019):** *Generalizations of the “Linear Chain Trick”: Incorporating more flexible dwell time distributions into mean field ODE models*. Journal of Mathematical Biology 79, 1831–1883. DOI: [10.1007/s00285-019-01412-w](https://doi.org/10.1007/s00285-019-01412-w). [Autorenfassung](https://arxiv.org/abs/1808.07571). Anschluss für Phasentyp-Verweildauern und deren ODE-Darstellung.
- **[S4] Metzner, P.; Schütte, C.; Vanden-Eijnden, E. (2009):** *Transition Path Theory for Markov Jump Processes*. Multiscale Modeling & Simulation 7(3), 1192–1219. DOI: [10.1137/070699500](https://doi.org/10.1137/070699500). [Original-PDF](https://publications.imp.fu-berlin.de/43/1/MeScVE09.pdf). Kommittoren und Übergangspfade; stationäre Stromkonstruktionen haben zusätzliche Voraussetzungen.
- **[S5] Singletary, A.; Chen, Y.; Ames, A. D. (2020):** *Control Barrier Functions for Sampled-Data Systems with Input Delays*. [Autorenfassung](https://arxiv.org/abs/2005.06418). Wissenschaftlicher Anschluss für gehaltene Eingriffe, Zustandsunsicherheit und Verzögerungen. Die affine Intervallschranke in C5 wird hier direkt hergeleitet.
- **[S6] Blackwell, D. (1953):** *Equivalent Comparisons of Experiments*. Annals of Mathematical Statistics 24(2), 265–272. DOI: [10.1214/aoms/1177729032](https://doi.org/10.1214/aoms/1177729032). [Verlagsseite](https://projecteuclid.org/journals/annals-of-mathematical-statistics/volume-24/issue-2/Equivalent-Comparisons-of-Experiments/10.1214/aoms/1177729032.full). Anschluss zwischen Beobachtungskanälen und Entscheidungsnutzen; keine automatische Gleichsetzung mit einem einzelnen Informationsmaß.
- **[S7] Loritz, R. et al. (2024):** *CAMELS-DE: hydro-meteorological time series and attributes for 1582 catchments in Germany*. Earth System Science Data 16, 5625–5642. [Originalpublikation](https://essd.copernicus.org/articles/16/5625/2024/). Datenkontext für den vorhandenen Hydrologie-Piloten; die bisherigen sechs Gebiete bleiben ein kleines Panel.

## 15. Geprüfte Repo-Anker

Alle Links sind auf den Referenzcommit festgelegt:

- [Hydrologischer Pilotcode](https://github.com/GenesisAeon/scoped-correspondence-formalism/blob/d0ab5c5ffc0e14b834ce9e285268cb8a34345e98/src/scoped_correspondence/validation/hydrology_pilot.py)
- [Bisheriger Hydrologie-Bericht](https://github.com/GenesisAeon/scoped-correspondence-formalism/blob/d0ab5c5ffc0e14b834ce9e285268cb8a34345e98/docs/hydrology_pilot.md)
- [Lineare Reservoirs](https://github.com/GenesisAeon/scoped-correspondence-formalism/blob/d0ab5c5ffc0e14b834ce9e285268cb8a34345e98/src/scoped_correspondence/dynamics/linear_reservoirs.py)
- [Closure-Kern](https://github.com/GenesisAeon/scoped-correspondence-formalism/blob/d0ab5c5ffc0e14b834ce9e285268cb8a34345e98/src/scoped_correspondence/closure/core.py)
- [Gekoppelte Puffer](https://github.com/GenesisAeon/scoped-correspondence-formalism/blob/d0ab5c5ffc0e14b834ce9e285268cb8a34345e98/src/scoped_correspondence/viability/coupled_buffer_cbf_qp.py)
- [Kooperative Aufgaben](https://github.com/GenesisAeon/scoped-correspondence-formalism/blob/d0ab5c5ffc0e14b834ce9e285268cb8a34345e98/src/scoped_correspondence/validation/cooperative_agents_pilot.py)
- [Gemeinsames Versuchsprotokoll](https://github.com/GenesisAeon/scoped-correspondence-formalism/blob/d0ab5c5ffc0e14b834ce9e285268cb8a34345e98/docs/domain_expansion_protocol.md)
- [Strukturbeziehungen und Status](https://github.com/GenesisAeon/scoped-correspondence-formalism/blob/d0ab5c5ffc0e14b834ce9e285268cb8a34345e98/docs/structural_relations.md)

## 16. Direkt übergebbarer Arbeitsauftrag an Claude Code

```text
Arbeite SCF_INTEGRATED_EXTENSION_IMPLEMENTATION_PLAN.md am Repository
GenesisAeon/scoped-correspondence-formalism ab. Referenz ist d0ab5c5;
prüfe vor Änderungen den aktuellen Stand und vorhandene Repo-Anweisungen.

Der vollständige vorgeschlagene Umfang ist C0–C7. Die erste fachliche
Etappe ist C0–C3; C4–C6 folgen als eigene Pakete, C7 konsolidiert.
Dieses Dokument enthält noch keine implementierten Erweiterungen.

Beginne mit C0: Reproduziere die beiden konkret benannten Zeitachsenfehler
unabhängig am echten Code, korrigiere sie, ergänze Regressionen und rechne
die sechs bestehenden CAMELS-Gebiete erneut. Berichte Änderungen der
Scores und Rangfolgen, ohne die bisherige Rangfolge vorauszusetzen.

Für jedes weitere Paket:
1. Formuliere die Modellannahmen, Zeit-/Informationskonventionen und den
   genauen neuen Anspruch in einer kurzen Herleitung.
2. Rechne die angegebenen Kontrollfälle unabhängig nach. Behandle auch
   diesen Plan als überprüfbar; dokumentiere nötige Korrekturen.
3. Implementiere den kleinsten vollständigen Umfang unter Wiederverwendung
   bestehender Funktionen. Keine generischen Frameworks ohne ersten Nutzer.
4. Prüfe positive Fälle, Gegenbeispiele und die benannten relevanten Grenzen.
   Prüfergebnisse nicht allein durch Vergleich einer Funktion mit sich
   selbst begründen.
5. Registriere die Suiten explizit und dokumentiere Evidenz und Grenzen.
6. Halte Null-/Negativergebnisse sowie zurückgestellte Teilaufgaben sichtbar.

Besonders beachten: Tagesmittel statt Momentanabfluss in C1; getrennte
Parameteridentifikation und Zustandsbeobachtbarkeit; Aktions- und
Ereigniserhaltung in C2; Verweilzeit-CDF ist kein Queue-Risiko in C3;
geschlossene Klassen in C4; Sicherheit zwischen Regelzeitpunkten in C5;
Informationskanäle über Feedback und Schweigen in C6.

Neue Module und Ergebnisse additiv halten. Den gesonderten Reviewstatus
von docs/structural_relations.md nicht als Nebenwirkung verändern.
Einen sauber dokumentierten Zwischenstand nach C0–C3 bereitstellen und
den Umfang der zweiten Etappe ausdrücklich erhalten.

Führe am vollständigen Abschluss die math-, data- und links-Prüfungen
des Repositories aus und liefere einen Bericht je Paket mit Änderungen,
ausgeführten Prüfungen, echten Datenresultaten und verbleibenden Grenzen.
Commit-/Push-/Merge-Aktionen richten sich nach Johanns ausdrücklichem
Auftrag und den geltenden Repo-Regeln, nicht allein nach diesem Dokument.
```
