# SCF: unabhängiger Review der Pakete C0–C7

**Johann Benjamin Römer / GenesisAeon · Review vom 25. September 2026**  
Geprüfter Stand: [`4ed0cd98c52626d0e5932b15d22212ab27ad300b`](https://github.com/GenesisAeon/scoped-correspondence-formalism/tree/4ed0cd98c52626d0e5932b15d22212ab27ad300b).  
Vergleichsbasis nach C0: `45f1ee30d006e2eae726ba6bd49db21d95e93821`.

## 1. Urteil

**Die Erweiterung ist substanziell und die wesentlichen positiven Pilotbefunde lassen sich bestätigen. Vor einem Abschluss als gehärtete allgemeine API sind aber weitere Korrekturen nötig.**

Besonders überzeugend sind der passende Tagesmittel-Messoperator, die explizite Aktionsabbildung bei Vergröberungen, die Trennung konkurrierender Zielereignisse und der kleine exakt überprüfbare Bellman-Pilot. Die Einordnung des hydrologischen Ergebnisses ist grundsätzlich richtig: Zustandskorrektur verbessert die mechanistischen Modelle deutlich, übertrifft die Persistenz aber nur bei einem der sechs Gebiete. Auch negative Ergebnisse zur myopischen Netzsteuerung werden offen dokumentiert.

Der wichtigste neue Fund betrifft erneut die Differenz zwischen **kontinuierlicher Dynamik und abgetastetem Ereignisnachweis**. C3 verfeinert eine gefundene Nullstelle präzise, kann aber weiterhin einen schmalen negativen Ausschlag vollständig übersehen. Daneben sind die Sicherheitszusage des Netzwerk-QP bei negativem Anfangszustand und die Absorptionsprüfung über einen bloß erfolgreichen linearen Solver nicht belastbar.

Ich würde zuerst die nachfolgenden Korrekturen durchführen und danach den Galaxienplan beginnen. Die neue Domäne bleibt fachlich sinnvoll; sie soll auf korrigierten Kernverträgen aufbauen.

## 2. Was tatsächlich geprüft wurde

- Der GitHub-Branch `master` zeigte beim Abruf auf den geprüften Commit. Der [zugehörige Actions-Lauf 36128193996](https://github.com/GenesisAeon/scoped-correspondence-formalism/actions/runs/36128193996) war `completed/success`.
- Die Änderungen C1–C7 wurden einschließlich Produktionsmodule, neun neuer Verifikationsskripte, Dokumentation, Roadmap und Fähigkeitsübersicht gelesen. C0 wurde anhand des aktuellen Hydrologiecodes und seiner Regressionen mitgeprüft.
- Sämtliche lokalen Produktions-Pythondateien und Verifikations-Pythondateien wurden gegen die Git-Blob-Hashes des exakten Commits abgeglichen. Die sechs CAMELS-CSV-Dateien stimmen ebenfalls mit Git-Blob-Hashes und den SHA-256-Werten des Manifests überein.
- Die **neun neuen C1–C6-Verifikationsskripte bestanden**. Unabhängige Gegenbeispiele decken zusätzliche, dort nicht geprüfte Fälle auf.
- Der lokale Gesamtlauf umfasste **77 mathematische und 16 Daten-Skripte**. Nach Ergänzung der benötigten vorhandenen Ergebnisartefakte bestanden 75 mathematische und alle 16 Daten-Skripte vollständig. Zwei weitere mathematische Skripte scheiterten ausschließlich an ihrer eingebetteten Dokument-Linkprüfung: Eine im Git-Baum vorhandene DOCX-Anlage ließ sich über den verwendeten Textzugang nicht lokal herunterladen. Das ist **kein festgestellter Fehler im Repository**. Die übrigen Prüfungen dieser beiden Skripte bestanden. Der komplette grüne CI-Lauf wurde beobachtet, nicht als vollständig lokal reproduziert ausgegeben.
- Die fehlenden lokalen Linkziele der gelesenen Markdown-Dateien wurden zusätzlich gegen den Git-Baum geprüft: alle neun sind dort vorhanden. Ein vollständiger lokaler Linkcheck über jede Repository-Datei wird damit nicht behauptet.
- Alle sechs hydrologischen Einzugsgebiete wurden für ein und zwei Speicher mit einer eigenständig formulierten Rekurrenz nachgerechnet. Die dokumentierte Wahl `W=10^6 I` wurde dabei als Eingabe übernommen; die fehlerhafte innere Hyperparameterkalibrierung wurde dadurch nicht validiert.
- C6 wurde mit einem anders formulierten dynamischen Programm über das Alter der letzten perfekten Beobachtung in **100 Fällen** überprüft. Maximaler Unterschied: `4.44e-16`.

Umgebung der Gegenrechnungen: Python 3.12.14, NumPy 2.3.5, SciPy 1.17.0. Kein Produktionscode wurde geändert, kein Commit erzeugt oder gepusht. Die Reproduktionsdateien sind im Begleitarchiv `SCF_REVIEW_C0_C7_4ed0cd9_REPRODUCTIONS.zip` enthalten.

## 3. Befunde nach Priorität

P1 bedeutet hier: Eine zentrale mathematische oder Sicherheitszusage kann falsch sein. P2 bedeutet: Korrektheits-, Methoden- oder Auswertungsfehler mit enger abgegrenztem Einfluss. P3 bezeichnet eine redaktionelle Korrektur.

| ID | Priorität | Paket | Befund |
|---|---|---|---|
| R1 | P1 | C3 | Endliches Suchraster kann negative Pufferausschläge vollständig übersehen |
| R2 | P1 | C5 | QP zertifiziert Sicherheit trotz negativem Anfangszustand |
| R3 | P2 | C2 | Minimax-Zeile verlässt bei drei Makroklassen den Wahrscheinlichkeitssimplex |
| R4 | P1 | C3/C4 | Erfolgreiches `solve` beweist keine sichere Absorption; unendliche Zeiten werden endlich ausgegeben |
| R5 | P2 | C5 | Fehlgeschlagener Optimierer wird ohne Unzulässigkeitsnachweis als `infeasible` klassifiziert |
| R6 | P2 | C5 | Gemeldete Erstpassagezeiten sind Intervallendpunkte, keine tatsächlichen Ereigniszeiten |
| R7 | P2 | C5 | Akzeptierte Regelintervalle können ganze Lastsprünge auslassen |
| R8 | P2 | C1 | Beim inneren Kalibrierungssplit fehlt ein Zustandsübergang; Test wiederholt denselben Fehler |
| R9 | P2 | C1 | Ungültige Kovarianzen passieren die API und erzeugen negative Posteriorvarianz |
| R10 | P2 | C1 | Persistenzvergleich verwendet teilweise andere Tage; negative Speicher werden mit falscher Zähleinheit berichtet |
| R11 | P3 | C7 | Vergleichstabelle verwechselt Persistenz mit offenem Regelkreis |

## 4. R1 — Der C3-Dip-Fix bleibt rasterabhängig

**Ort:** [`validation/distributed_delay_pilot.py`](https://github.com/GenesisAeon/scoped-correspondence-formalism/blob/4ed0cd98c52626d0e5932b15d22212ab27ad300b/src/scoped_correspondence/validation/distributed_delay_pilot.py), `run_fixed_experiment`, insbesondere ab Zeile 140.

Der Code sucht auf mindestens 500 Teilintervallen nach einem Wert `R<=0`. Erst wenn ein solcher Punkt gefunden wurde, wird mit Brent verfeinert. Dadurch wird die Nullstelle innerhalb eines gefundenen Intervalls genau, die Vollständigkeit der Suche aber nicht garantiert. Ein kürzerer negativer Abschnitt zwischen zwei Rasterpunkten verschwindet vollständig.

### Geschlossener Gegenfall

Ein Erlang-Speicher mit `n=1`, `tau=1`, Pulsstärke 5, Pulsdauer `d=0.2`, Zufluss 0.4 und Horizont 5. Nach dem Puls gilt exakt:

\[
A=5(1-e^{-0.2}),\qquad
R(t)=R_0+0.4t-1+A e^{-(t-0.2)},\quad t\ge0.2.
\]

Das Minimum liegt bei

\[
t_*=0.2+\log(A/0.4)=1.0179568433377355.
\]

Wähle

\[
R_0=1-0.4(t_*+1)-10^{-7}=0.19281716266490573.
\]

Dann ist `R(t*)=-1e-7`. Der tatsächliche erste Grenzdurchgang liegt bei ungefähr `1.0172498198798665`.

Der aktuelle Aufruf

```python
run_fixed_experiment(1, R0=0.19281716266490573)
```

liefert gleichzeitig:

```text
first_passage_time = None
R_min_value       = -9.999996652965137e-08
R_min_time        = 1.0179572525923066
```

Damit widerspricht der gemeldete fehlende Grenzdurchgang sogar dem eigenen negativen Minimum. Das Problem liegt weit über bloßem Rundungsrauschen.

### Konkreter Reparaturweg

Die Ereignissuche muss auf nachweislich monotonen Abschnitten von `R` arbeiten. Für den hier deklarierten positiven Rechteckpuls durch eine Erlang-Kette ist das besonders übersichtlich:

- Während des Pulses ist der Ausgang eine skalierte Erlang-CDF.
- Nach dem Puls ist der Ausgang eine Differenz zweier verschobener Erlang-CDFs.
- Für `n=1` liegt sein Maximum genau bei `d`.
- Für `n>1`, Stufenrate `k=n/tau`, liegt sein unbeschränkt betrachtetes Maximum bei

\[
t_{\rm peak}=\frac{d}{1-e^{-kd/(n-1)}}.
\]

Diese eigene Ableitung folgt aus `h_n(t)=h_n(t-d)`. Den Nenner stabil mit `-expm1(-k*d/(n-1))` auswerten. Randfälle wie Pulsdauer null separat behandeln. Die Formel benötigt die angegebenen Erlang- und Pulsannahmen; sie gilt nicht pauschal für jede Phasentyp-Verteilung.

Die monotonen Ausgangsabschnitte erlauben ein vollständiges Einklammern der Wurzeln von `R'=inflow-y`. Segmentränder und sämtliche stationären Punkte von `R` ergeben anschließend die Intervalle für die eigentliche Nullstellensuche. Tangentiale Berührung muss als eigener Fall behandelt werden. Ein größeres festes Raster allein repariert den Fehler nicht.

Zusätzlich Segmentränder bei Minimum und Ausgangsmaximum explizit auswerten. Der aktuelle `minimize_scalar`-Ansatz trifft beispielsweise das `n=1`-Maximum am Pulsende nur näherungsweise: statt `t=0.2` und `A≈0.90634623461` werden ungefähr `t=0.20000342107` und `0.90634313394` gemeldet. „Exakte Fortpflanzung“ ist keine Garantie für eine exakte Extremsuche.

**Abnahme:** obiger schmaler Dip; echte Tangentialberührung; Minimum am Segmentrand; keine Verletzung; vorhandene Beispiele. Änderungen an diagnostischem Sampling dürfen den Ereignisstatus nicht verändern.

## 5. R2 — Wiederherstellung am Intervallende ist keine Sicherheit über das Intervall

**Ort:** [`viability/resource_network_control.py`](https://github.com/GenesisAeon/scoped-correspondence-formalism/blob/4ed0cd98c52626d0e5932b15d22212ab27ad300b/src/scoped_correspondence/viability/resource_network_control.py), `solve_network_qp`, insbesondere die direkte Statuskonstruktion ab Zeile 218.

Minimalfall: ein Knoten, keine Kanten, `x0=-0.1`, Bedarf 0, `Delta=1`, maximaler Zufluss und Gesamtbudget jeweils 1, quadratische Kosten. Der Solver findet korrekt für seine reine Endpunktbedingung `u≈0.1`. Die Bahn lautet `x(t)=-0.1+0.1t`.

Aktuelle Ausgabe:

```text
status   = solved
feasible = True
safety.status = boundary_touch
x_end ≈ 0
```

Tatsächlich ist die Bahn für jedes `0<=t<1` negativ. Eine am Ende wiederhergestellte Zulässigkeit ist keine ganzintervallige Sicherheit. Der Codekommentar, dass ein sicher bekannter negativer Anfangswert bereits durch die Solverbedingung berücksichtigt sei, beseitigt diesen mathematischen Unterschied nicht.

**Fix:** QP-Lösbarkeit, Wiederherstellung und Sicherheitszertifizierung getrennt führen. Für eine affine Bahn gilt komponentenweise `min(x0,x_end)>=0`. Ist `x_lower` nur eine negative untere Unsicherheitsschranke, folgt daraus `not_certified`, nicht zwingend ein sicher negativer wahrer Zustand. Ist der wahre Anfangszustand bekannt negativ, ist die Verletzung bereits eingetreten. Ein optionaler Wiederherstellungsregler kann trotzdem sinnvoll sein, benötigt aber einen anderen Sicherheitsstatus.

Erfolgreiche Solverausgaben zudem gegen alle tatsächlich verwendeten Nebenbedingungen nachprüfen. Ein Solver-Erfolgsflag ersetzt keine Residuenprüfung. Eine eventuell gewünschte robuste obere Kapazitätsgarantie mit `K` braucht passende obere Zustands- und untere Bedarfsschranken; allein `x_lower` und `d_upper` reichen dafür nicht.

**Abnahme:** negativer bekannter Start, negative Unsicherheitsschranke, Nullstart mit positiver Steigung, reine Berührung am Horizont und der vorhandene Drei-Puffer-Kontrollfall.

## 6. R3 — Die Minimax-Makrozeile muss eine Wahrscheinlichkeitsverteilung bleiben

**Ort:** [`correspondence/controlled_markov.py`](https://github.com/GenesisAeon/scoped-correspondence-formalism/blob/4ed0cd98c52626d0e5932b15d22212ab27ad300b/src/scoped_correspondence/correspondence/controlled_markov.py), `best_minimax_macro_row`, ab Zeile 227.

Der koordinatenweise Mittelpunkt von Minimum und Maximum minimiert einen unbeschränkten Maximumsabstand. Er muss aber nicht im Wahrscheinlichkeitssimplex liegen.

Konkreter gültiger Markov-Fall:

```python
C, _ = partition_indicator([0, 0, 0, 1, 2])
P = np.eye(5)
P[:3] = 0
P[0, 0] = 1
P[1, 3] = 1
P[2, 4] = 1
row, error = best_minimax_macro_row(P, C, 0)
```

Die drei Mikrozustände der ersten Klasse haben Blocksummen `(1,0,0)`, `(0,1,0)` und `(0,0,1)`. Der Code liefert `(0.5,0.5,0.5)`, Summe 1.5, Fehler 0.5. Das ist keine Makro-Übergangszeile.

Das korrekte Simplexproblem hat Lösung `(1/3,1/3,1/3)` mit Fehler `2/3`. Beweis: Für jede der drei Zielkoordinaten muss `q_j>=1-epsilon` gelten. Aus `sum(q)=1` folgt `epsilon>=2/3`; die Gleichverteilung erreicht die Schranke. Ein unabhängiges lineares Programm bestätigt das Ergebnis.

**Fix:**

\[
\min_{q,\epsilon}\epsilon\quad\text{mit}\quad
q\ge0,\ \sum_jq_j=1,\ |q_j-b_{ij}|\le\epsilon.
\]

Alternativ den bisherigen Helfer ausdrücklich auf den Zweiklassenfall begrenzen. Bloßes nachträgliches Normieren des Mittelpunkts ist kein allgemeiner Minimax-Beweis.

**Abnahme:** Zweiklassen-Kontrolle unverändert; der obige Dreiklassenfall; weitere Simplexfälle gegen unabhängiges LP. Der exakte C2-Kontrollfall und die per Aktion geprüfte starke Lumpability werden durch diesen Fund nicht widerlegt.

## 7. R4 — Numerische Invertierbarkeit ersetzt keine Absorptionsprüfung

**Orte:** [`viability/competing_first_passage.py`](https://github.com/GenesisAeon/scoped-correspondence-formalism/blob/4ed0cd98c52626d0e5932b15d22212ab27ad300b/src/scoped_correspondence/viability/competing_first_passage.py), `mean_hitting_time`/`committor`; außerdem [`dynamics/phase_type_delays.py`](https://github.com/GenesisAeon/scoped-correspondence-formalism/blob/4ed0cd98c52626d0e5932b15d22212ab27ad300b/src/scoped_correspondence/dynamics/phase_type_delays.py), `validate_phase_type`.

Betrachte Zustände `(A,i,j,B)` und den gültigen Generator

\[
L=\begin{pmatrix}
0&0&0&0\\
0&-0.3&0.3&0\\
0&0.4&-0.4&0\\
0&0&0&0
\end{pmatrix}.
\]

Die inneren Zustände bilden eine geschlossene Klasse. Weder A noch B ist erreichbar. Die mittlere Randtreffzeit ist deshalb unendlich.

Im geprüften NumPy-/LAPACK-Lauf wirft `solve` dennoch keine Ausnahme. Die API liefert für beide inneren Zustände ungefähr **`3.152519739159347e16`**. Der endliche Horizont zeigt zugleich korrekt `p_unresolved=1`. Die riesige Zahl ist ein Rundungsartefakt einer singulären Aufgabe, keine endliche Wartezeit.

Dasselbe `2x2`-Innenfeld als `PhaseType(alpha=[1,0], T=L_DD, r=[0,0])` passiert `validate_phase_type` und bekommt eine endliche mittlere Verweildauer. Seine Absorptionswahrscheinlichkeit ist aber null. Das konkrete Solververhalten kann sich mit numerischer Bibliothek ändern; die notwendige strukturelle Ablehnung darf davon nicht abhängen.

**Fix:** Erreichbarkeit beziehungsweise geschlossene Klassen explizit prüfen. Für den deklarierten endlichen C4-Geltungsbereich muss jeder betrachtete innere Zustand über positive Übergangsraten einen Randzustand erreichen können. Bei Phasentypen entsprechend einen Zustand mit positiver Austrittsrate erreichen lassen; festlegen, ob alle Phasen oder nur von `alpha` erreichbare Phasen gefordert werden. Danach den linearen Solve und eine skalierte Residuen-/Konditionsprüfung ausführen. Ein pauschaler absoluter Eigenwertgrenzwert würde erneut Probleme bei einer Zeitumskalierung erzeugen.

Die endliche Horizontverteilung darf für nicht absorbierende Ketten durchaus berechnet werden; dort ist ungelöste Masse ein legitimes Ergebnis. Die API mit Voraussetzung sicherer Absorption muss dagegen ihren Scope einhalten.

**Abnahme:** geschlossene Zweierklasse mit obigen Dezimalraten; tatsächlich absorbierende Kette; sehr kleine, aber positive Austrittsraten; reine Zeitumskalierung. Der veröffentlichte C4-Kontrollfall `q=(0.6,0.9)`, `m=(0.6,0.4)` bestätigt sich unabhängig.

## 8. R5 — Eine ungünstige Ecke beweist keine Unzulässigkeit

**Ort:** `resource_network_control.py`, fehlgeschlagener Optimiererzweig ab Zeile 202.

Wenn kein SLSQP-Lauf erfolgreich ist, prüft der Code die Ecke `(u_max, edge_cap)`. Erfüllt diese nicht die Bedingungen, wird `infeasible` ausgegeben. Diese Folgerung ist falsch: Maximale Einzelzuflüsse können das gemeinsame Budget überschreiten, und maximale Kantenflüsse können gerade einen Quellknoten leeren.

Kontrollfall ohne Kanten:

```text
x0 = (0.2, 0.4, 0.6)
d = (1, 1, 1)
Delta = 1
u_max = (1, 1, 1)
Gesamtbudget = 2
```

Der zulässige Zeuge `u=(0.8,0.6,0.4)` hat Summe 1.8 und endet bei `(0,0,0)`. Die geprüfte großzügige Ecke hat Summe 3 und verletzt das Budget.

Im Reproduktionsskript wird **gezielt ein numerischer Solverfehlschlag simuliert**. Daraufhin meldet die API `infeasible`, obwohl der obige Zeuge existiert. Damit ist die Fehlerbehandlung widerlegt; es wird nicht behauptet, dass der unveränderte SLSQP diesen einfachen Kontrollfall normalerweise nicht lösen könne.

**Fix:** Ohne zusätzlichen Nachweis `optimizer_failed` liefern. Optional ein separates lineares Zulässigkeitsproblem mit denselben Nebenbedingungen lösen und dessen Status sowie Toleranzen transparent berichten. Das Versagen einer einzelnen Kandidatenlösung darf nie zum Nachweis der Leere der gesamten zulässigen Menge werden.

**Abnahme:** erzwungener Solverfehlschlag bei bekannt zulässigem Problem; unabhängiges wirklich unzulässiges Problem; Kante mit bei Maximalfluss schlechterer Sicherheit. Die im Pilot bisher als unzulässig markierten Intervalle nach dem Fix neu klassifizieren, ohne im Voraus eine Änderung ihrer tatsächlichen Zulässigkeit zu unterstellen.

## 9. R6 — Ereigniszeiten im Netzwerk-Pilot sind falsch auf das Regelraster gerundet

**Ort:** [`validation/resource_network_pilot.py`](https://github.com/GenesisAeon/scoped-correspondence-formalism/blob/4ed0cd98c52626d0e5932b15d22212ab27ad300b/src/scoped_correspondence/validation/resource_network_pilot.py), Zeilen 166/168; Ergebnistabelle in `docs/resource_network_pilot.md` und entsprechende Regression.

Schon die unveränderte Baseline `none` im offiziellen Panel reicht als Gegenfall. Vor `t=1` beträgt die Reserve des ersten Knotens 0.6. Auf `[1,2)` ist die Nettosteigung `-0.9`. Daher

\[
x_0(t)=0.6-0.9(t-1),\qquad \tau_{\rm touch}=1+\frac{0.6}{0.9}=\frac53.
\]

Der Code meldet bei `Delta=1` Erstkontakt und Verletzung bei 2.0; bei `Delta=0.25` bei 1.75. Es handelt sich in beiden Fällen um dieselbe physikalische Baseline. Die wahre Kontaktzeit ist ungefähr 1.6666666667.

**Fix:** Im affinen Segment `x_i(t0+s)=x_i0+b_i*s` die Kandidaten `s=-x_i0/b_i` für fallende Komponenten und gültiges `s` exakt berechnen. Für alle Ereignisse Anfang, Segmentinneres und Horizont unterscheiden. Die Strenge der Verletzung sauber definieren: Beim Durchgang in `x<0` ist das Infimum der Eintrittszeiten die Nullstelle, obwohl der Zustand genau dort noch null ist. Eine bloße Berührung am letzten Horizont ohne anschließenden negativen Zustand innerhalb des betrachteten Zeitraums ist keine strikte Verletzung.

Die aktuelle Regression, die für den optimierten Fall eine strikte Verletzung bei exakt 4.0 verlangt, muss fachlich neu hergeleitet werden; das Abschreiben des Intervallendpunkts ist keine unabhängige Kontrolle. Kosten und affine Intervallminima werden durch die Korrektur der Ereigniszeit nicht automatisch falsch, müssen bei einem Controllerfix aber ohnehin neu ausgegeben werden.

**Abnahme:** Baselinekontakt bei `5/3` unabhängig von `Delta=1` oder `0.25`; reine Horizontberührung; Start auf der Grenze mit auswärts gerichteter Steigung; negative Startreserve; mehrere gleichzeitig betroffene Knoten.

## 10. R7 — Der Pilot akzeptiert Intervalle, die Lastsprünge auslassen

**Ort:** `resource_network_pilot.py`, Eingangsprüfung ab Zeile 99 und Verwendung von `_demand(t0)`.

Es wird nur geprüft, ob das Regelintervall den Gesamthorizont 6 teilt. `control_interval=2` wird deshalb akzeptiert. Die Last wird dann bei 0, 2 und 4 abgefragt; beide Zusatzlasten auf `[1,2)` und `[3,4)` verschwinden vollständig.

```python
run_network_pilot("none", 2.0, False)
```

liefert `min_reserve=0.6`, keinen Erstkontakt und keine Verletzung. Die identische Baseline mit vollständig berücksichtigtem Lastplan erreicht tatsächlich eine Reserve von −0.3.

Die offiziellen Vergleichswerte 0.25 und 1 sind von diesem konkreten Eingabefehler nicht betroffen. Die öffentlich aufrufbare Funktion schützt ihre behauptete Annahme aber nicht.

**Fix:** Entweder den Pilot explizit auf die beiden deklarierten Werte beschränken oder verlangen, dass alle Last- und Ausfallzeitpunkte auf dem Regelgitter liegen. Allgemeiner: Simulationsabschnitte an allen Ereigniszeiten teilen, während die gewählte Steuerung bis zum nächsten Reglerzeitpunkt konstant bleibt. Eine Zustandsfortschreibung an einem Lastsprung bedeutet nicht automatisch, dort den Regler neu entscheiden zu lassen.

Auch `Delta<=0`, NaN und unendliche Intervalle zurückweisen. Eine relative, skalierte Teilbarkeitsprüfung verwenden.

**Abnahme:** Intervall 2 wird nachvollziehbar zurückgewiesen oder mit beiden Lastspitzen korrekt simuliert. Die Baselinebahn darf nicht von der bloßen Beobachtungs- oder Integrationsaufteilung abhängen.

## 11. R8 — Ein Tag fehlt an der inneren Kalibrierungsgrenze

**Ort:** [`validation/hydrology_state_estimation.py`](https://github.com/GenesisAeon/scoped-correspondence-formalism/blob/4ed0cd98c52626d0e5932b15d22212ab27ad300b/src/scoped_correspondence/validation/hydrology_state_estimation.py), `calibrate_process_noise`, Zeilen 246/247; dazu `verify_hydrology_state_estimation.py` in der Hilfsrechnung `inner_val_mae`.

Die gespeicherten Posterioren gehören zum **Tagesanfang nach Korrektur durch die Tagesmittelmessung**. Der letzte Trainingsposterior ist damit noch nicht der Prior des ersten Validierungstags. Der Code übergibt ihn aber unmittelbar als `m0,P0` des Validierungsblocks.

Es fehlt genau der Übergang:

\[
m_{\rm val,0}^-=F m_{\rm train,last}^+ +G u_{\rm train,last},
\qquad
P_{\rm val,0}^-=F P_{\rm train,last}^+F^\top+W.
\]

Eine Nachrechnung mit 150 Tagen, einem Niederschlagspuls am letzten Tag des 120-Tage-Innen-Trainings, `c=1`, `k=log(2)` und `w_scale=0.001` ergibt:

| Größe | Übergebener Wert | Erforderlicher Wert |
|---|---:|---:|
| mittlerer Anfangsspeicher der Validierung | −0.09056897198571676 | 0.6760630344516233 |
| Anfangsvarianz | 0.0010592686844891233 | 0.001264817171122281 |

Der vorhandene Kalibrierungstest wiederholt die gleiche Übergabe ohne `predict` und kann den Fehler daher nicht erkennen.

**Fix:** Den erforderlichen letzten Übergang explizit ausführen oder jeden Kandidaten über den zusammenhängenden Innen-Trainings- und Validierungszeitraum filtern und erst die Scoringmaske trennen. Das zweite Vorgehen vermeidet zusätzlich den unnötigen Verlust des ersten grundsätzlich prognostizierbaren Validierungstags.

Der äußere endgültige Vollspannenlauf enthält diesen konkreten Splitfehler nicht. Der Befund widerlegt daher nicht automatisch die Test-MAE; er betrifft die Auswahl der Rauschparameter. Nach Korrektur Kalibrierung und Pilot neu ausführen und vermerken, ob sich die Auswahl ändert.

**Zusätzliche Methodenpräzisierung:** Die dynamischen Parameter und `R` wurden bereits auf dem gesamten äußeren Training 1991–2005 geschätzt. Die Aussage „first 80% fits, last 20% validates“ ist insofern keine strikt verschachtelte Validierung aller Parameter. Entweder die Basisparameter im inneren Trainingsabschnitt neu schätzen und danach auf dem gesamten äußeren Training refitten, oder diesen begrenzten Status der inneren Auswahl ausdrücklich benennen. Das ist kein Nachweis einer Verwendung der Testziele 2011–2020.

**Abnahme:** Gesplittete und ungesplittete Filterrekurrenz mit richtigem Übergang stimmen überein, einschließlich Kovarianz und einem Puls genau am Split. Testzieländerungen beeinflussen weder Training noch frühere Lead-Prognosen.

## 12. R9 — Joseph-Form schützt nicht vor ungültigen Kovarianzen

**Ort:** [`observation/linear_state_estimation.py`](https://github.com/GenesisAeon/scoped-correspondence-formalism/blob/4ed0cd98c52626d0e5932b15d22212ab27ad300b/src/scoped_correspondence/observation/linear_state_estimation.py), `KalmanState`, `make_state`, `predict`, `update`.

Die API prüft Formen und teilweise Endlichkeit/Symmetrie, aber nicht durchgehend, ob `P`, `W` und `R` zulässige Kovarianzmatrizen sind. Die positive Definitheit von `S=HPH^T+R` allein reicht nicht.

Minimalfall:

```python
state = make_state([0.0], [[1.0]])
report = update(state, [1.0], np.array([[1.0]]), np.array([[-0.5]]))
```

Die API akzeptiert die negative Messvarianz. `S=0.5` besteht die vorhandene Innovationsprüfung, der Gewinn wird 2 und die Joseph-Form liefert anschließend **Posteriorvarianz −1**.

Dies ist ein Scope-Validierungsfehler für ungültige Eingaben, kein Beleg für negative Kovarianzen in den nachgerechneten CAMELS-Läufen. Die mathematisch richtige Joseph-Form garantiert Positivsemidefinitheit nur unter den passenden Voraussetzungen.

**Fix:** Gemeinsame Validierung für endliche, symmetrische, positiv semidefinite `P/W/R`; endliche Mittelwerte, Messungen und Eingaben. Den öffentlichen direkten `KalmanState`-Konstruktor berücksichtigen. Numerische Symmetrisierung nur für nachweislich kleine Rundungsabweichungen verwenden. `S` bleibt im aktuellen Scope strikt positiv definit; diese zusätzliche Voraussetzung ersetzt die anderen nicht. Keine stillen Eigenwertkorrekturen, die ein anderes statistisches Modell erzeugen.

**Abnahme:** obige negative Messvarianz abweisen; negative Prozess-/Priorvarianz; asymmetrische Matrizen; NaN; legitime singuläre `P` bei positiv definitem `S`; vorhandener Kontrollfall unverändert.

## 13. R10 — Vergleichsmengen und Zähleinheiten in C1 nachschärfen

### R10a: Persistenz steht noch außerhalb der gemeinsamen Scoringmaske

Der aktuelle C1-Pilot vereinheitlicht die Fälle der korrigierten und offenen Varianten über die Leads. Die Persistenzspalte wird dagegen aus dem älteren Hydrologie-Pilot übernommen, der wegen fehlender Vortagesmessungen eine eigene Maske hat.

Der Unterschied ist in den echten Daten vorhanden:

| Gebiet | Tage für korrigierte Prognose | Tage für Persistenz |
|---|---:|---:|
| DEA11490 | 3354 | 3353 |
| DE110500 | 3649 | 3647 |

Für DEA11490, zwei Speicher, ändert sich die Lead-1-MAE auf der gemeinsamen Menge von `0.055674826` auf `0.055690395`. Für DE110500, zwei Speicher, von `0.407481717` auf `0.407557889`. Die zentralen Rangfolgen ändern sich in dieser Nachrechnung nicht. Dennoch ist die als gemeinsam dargestellte Vergleichsmenge bisher nicht vollständig gemeinsam.

**Fix:** Persistenz im selben C1-Auswertungslauf erzeugen und für den primären direkten Vergleich in die gemeinsame Maske aufnehmen. Eigene verfügbare Fallzahlen als Zusatzanalyse sind zulässig, wenn sie getrennt beschriftet werden. Die Lead-1-Persistenz nicht ohne Weiteres als fairen Lead-3/7-Vergleich ausgeben; dafür die entsprechende Information am jeweiligen Prognoseursprung verwenden.

### R10b: Negative Komponenten sind keine negativen Tage

`run_filter_full_span` berechnet `np.sum(means < 0)`, nennt das Feld aber `n_negative_storage_days`. Bei mehreren Speichern können an einem Tag mehrere Komponenten negativ sein.

Die unabhängige Nachrechnung zeigt beispielsweise:

| Gebiet, zwei Speicher | Negative Komponenten-Zeitpunkte | Tage mit mindestens einer negativen Komponente |
|---|---:|---:|
| DEA11180 | 152 | 121 |
| DE110500 | 2063 | 1809 |
| DEG10330 | 2350 | 2315 |

Zudem hat die volle Zeitspanne 1991–2020 **10958 Tage**, nicht ungefähr 5479, wie der aktuelle Erläuterungstext als Vollspannen-Nenner angibt. 5479 entspricht dem Trainingszeitraum 1991–2005.

**Fix:** beide Zählungen getrennt ausgeben; für Tage `np.any(means < 0, axis=1).sum()` verwenden. Trainings-, Lücken- und Testperiode sowie Nenner explizit unterscheiden. Wenn Magnituden negativer Zustände zugesagt werden, zusätzlich Minimum oder geeignete Quantile berichten.

**Abnahme:** synthetischer Zweikomponentenfall mit gleichzeitiger Negativität; obige echten Zählungen; Vergleichsmasken mit gezielt fehlender Vortagsmessung.

## 14. R11 — Ein Satz in C7 kehrt den C1-Befund um

**Ort:** [`INTEGRATED_EXTENSION_ROADMAP.md`](https://github.com/GenesisAeon/scoped-correspondence-formalism/blob/4ed0cd98c52626d0e5932b15d22212ab27ad300b/INTEGRATED_EXTENSION_ROADMAP.md), Vergleichstabelle C1, Zeile 275.

Dort steht sinngemäß, an fünf von sechs Gebieten bleibe der **offene Regelkreis** der einfachere, nicht schlechtere Ausgangspunkt. Die Tabellen zeigen das Gegenteil: Die Korrektur verbessert den offenen Regelkreis; **Persistenz** bleibt an fünf Gebieten besser.

Vorgeschlagene Fassung:

> Die Zustandskorrektur verbessert die offenen mechanistischen Modelle auf dem untersuchten Panel. Als einfachere Referenz bleibt die Persistenz bei fünf von sechs Gebieten der korrigierten Lead-1-Prognose überlegen; bei DEA11490 gewinnt die Zustandskorrektur.

Keine Änderung der empirischen Grundinterpretation nötig, sondern ein Austausch des falsch bezeichneten Vergleichsmodells.

## 15. Bestätigte Ergebnisse und ihre Reichweite

### Hydrologie

Folgende Lead-1-MAE in mm/Tag ergaben sich mit eigenständig implementierter Filterrekurrenz und neu ausgeführter Dynamikparametrierung. `W=10^6 I` wurde entsprechend dem veröffentlichten Ergebnis fest vorgegeben. Das sind die bisherigen verfügbaren Fallmengen; R10a enthält die notwendige gemeinsame Maske.

| Gebiet | Korrigiert, 1 Speicher | Korrigiert, 2 Speicher | Persistenz |
|---|---:|---:|---:|
| DEA11490 | 0.060611 | 0.055675 | 0.064004 |
| DE211310 | 0.103381 | 0.103429 | 0.094507 |
| DEE10610 | 0.698502 | 0.749541 | 0.560812 |
| DEA11180 | 0.082401 | 0.082573 | 0.077704 |
| DE110500 | 0.407695 | 0.407482 | 0.383623 |
| DEG10330 | 0.273311 | 0.292647 | 0.233418 |

Auch die nachgerechneten Lead-3/7- und Niedrigwasserwerte passen zur dokumentierten Größenordnung und Rundung. Die unabhängige Rechnung bestätigt die Verbesserung gegenüber dem offenen Modell auf diesem Panel. Sie bestätigt keine neue, bisher unabhängige Gebietsauswahl, keine operationalen Niederschlagsvorhersagen und keine bereits kalibrierte Gesamtunsicherheit.

Die starke Präferenz für großes Prozessrauschen ist fachlich informativ: Der Beobachtung wird viel mehr vertraut als der frei fortgeschriebenen Dynamik. Sinnvolle Anschlussfrage nach den Fixes: Wie viel Zusatznutzen liefert diese mechanistische Form gegenüber einer ebenso sauber evaluierten einfachen autoregressiven oder persistenzbasierten Zustandskorrektur?

### Kontrollierte Vergröberung und konkurrierende Ziele

Die aktionsweise Bedingung `P^a C = C Q^omega(a)` ist ein passender SCF-Ausbau. Dass mehrere Mikroaktionen mit gleichem Makrolabel auch untereinander konsistent sein müssen, wird ausdrücklich geprüft. Die exakte Brücke zum Kommittor ist konzeptionell stark. R3 betrifft den ergänzenden approximativen Minimax-Helfer; R4 betrifft den vorausgesetzten Absorptionsbereich.

### Wiederholte Beobachtung

Für `p=0.1`, `c=0.2`, zwei Entscheidungen, ergibt sich unabhängig `V_2(0.5)=1.7`. Die alternative Alterszustands-Rekurrenz stimmt für fünf Horizonte, vier Umschaltwahrscheinlichkeiten und fünf Beobachtungskosten bis auf Gleitkommarundung mit dem Code überein. Das Prinzip, eine kostenpflichtige optionale Beobachtung bei Bedarf abzulehnen, ist korrekt berücksichtigt.

Das vollständige Delay-/Horizon-Panel, allgemeine verrauschte wiederholte Beobachtungen und eine breitere POMDP-Klasse bleiben zusätzliche Aufgaben. Der vorhandene kleine exakte Fall ist auch ohne diese Erweiterungen wertvoll.

### Ressourcennetzwerk

Die negativen Pilotresultate gegen myopische Optimierung sind plausibel und dürfen bestehen bleiben. Sie sind kein Nachweis, dass eine zusätzlich frei abschaltbare Kante ein korrekt gelöstes identisches Optimierungsproblem verschlechtert. Genau diese Unterscheidung wird bereits sinnvoll getroffen. Vor der nächsten Ergebnisfreigabe müssen jedoch Statusklassifikation und Ereigniszeiten korrigiert und die betroffenen Tabellen neu erzeugt werden.

## 16. Arbeitsreihenfolge für Claude Code

1. **R1 und R2 zuerst:** kontinuierliche Ereignisvollständigkeit und ganzintervallige Sicherheit herstellen. Handrechnungen vor Änderungen unabhängig reproduzieren.
2. **R4:** graphbasierte Absorptionsvoraussetzung in C3/C4 einführen; numerische Lösbarkeit und mathematische Erreichbarkeit trennen.
3. **R3 und R5:** gültiges Simplex-Minimaxproblem und ehrliche Solverfehlerklassifikation.
4. **R6/R7:** exakte affine Ereigniszeiten, explizite Behandlung aller Last- und Ausfallzeitpunkte; Regressionen und Ergebnistabellen aktualisieren.
5. **R8/R9:** Kalibrierungsübergang korrigieren, inneres Auswertungsprotokoll präzisieren und Kovarianzvoraussetzungen absichern.
6. **R10/R11:** gemeinsame Vergleichsmengen, korrekte Tageszählung und redaktionelle Korrektur. Hydrologische Kalibrierung und Auswertung nach R8 tatsächlich neu laufen lassen.
7. Danach vorhandene mathematische, Daten- und Linkprüfungen sowie die neuen Gegenfälle ausführen; Ergebnisse und etwaige Änderungen der Rangfolgen berichten.

Keine Einführung eines neuen universellen Prüf-Frameworks nötig. Die Korrekturen passen in die bestehenden kleinen Module. Die zurückgestellten C1c-, C4b-, C3↔C5- und C6-Aufgaben bleiben getrennt von diesen Korrektheitsfixes.

Der Begleitplan `SCF_GALAXY_DYNAMICS_IMPLEMENTATION_PLAN.md` ist auf diesen Commit aktualisiert. Seine Quellen- und mathematischen Vorarbeiten können bereits gelesen werden; Implementierungen, die sich auf betroffene Sicherheits- oder Identifizierbarkeitszusagen stützen, sollten nach den entsprechenden Fixes erfolgen.

## 17. Reproduktionsmaterial

Das Archiv `SCF_REVIEW_C0_C7_4ed0cd9_REPRODUCTIONS.zip` enthält:

- `reproduce_review.py`: kompakte Gegenrechnungen zu R1–R9 und unabhängige positive C4/C6-Kontrollen.
- `review_probes.json`: tatsächlich erhaltene Ergebnisse auf dem geprüften Stand.
- `check_hydrology_panel.py`: unabhängige Filterrekurrenz für das echte Sechs-Gebiete-Panel, einschließlich gemeinsamer Persistenzmaske und negativer Speicherzählungen.
- `hydrology_panel.json`: Parameter und Ergebnisse der zwölf nachgerechneten Fälle.
- `README.md`: Ausführung, Commitbindung und Grenzen.

Ausführung aus einem echten Checkout des genannten Commits, mit dessen vorhandenen Daten und installierten Abhängigkeiten:

```bash
PYTHONPATH=/absoluter/pfad/zum/repo/src python reproduce_review.py
```

Für das Hydrologieskript liegt der Checkout standardmäßig im Unterordner `repo` neben dem Skript; alternativ die dortige `root`-Definition anpassen. Es werden keine externen Daten heruntergeladen und keine Produktionsdateien verändert. Der Fit verwendet zur Beschleunigung die mathematisch gleiche lineare Reservoirrekurrenz über `scipy.signal.lfilter`; diese Route wird vorab gegen die vorhandenen Einzel- und Doppelspeicherformeln geprüft. Die Filterkorrektur selbst ist separat implementiert.

Die Gegenrechnungen dokumentieren das Verhalten **vor** einer Reparatur. Nach Änderungen sind die genannten korrekten Ergebnisse und Abnahmekriterien maßgeblich; die fehlerhaften Zahlen aus `review_probes.json` dürfen nicht als neue Sollwerte festgeschrieben werden.
