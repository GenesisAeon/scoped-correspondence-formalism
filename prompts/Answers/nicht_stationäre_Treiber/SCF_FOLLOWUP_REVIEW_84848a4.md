# SCF: Folgereview des Fix-Commits 84848a4

**Datum:** 26. September 2026. **Prüfstand:** `84848a464bfba6a6d1160de303b2eacc429114eb`.

## Ergebnis

Die zentralen Korrekturen aus dem vorherigen Review sind nachvollziehbar umgesetzt. Insbesondere stimmen jetzt Burkerts kleine Radien, der NFW-Ursprungsvertrag, die Datenvalidierung und die Skip-Zählung. Die gemeldeten Sensitivitätsfaktoren **5,1662 für NGC3521** und **2,6480 für UGC02487** lassen sich reproduzieren.

**Eine vollständige Freigabe der neuen Profil-Likelihood-Auswertung ist noch nicht möglich.** Der einzelne lokale Optimierer liefert auf echten Pilotdaten mehrfach ein deutlich zu großes vermeintliches Minimum. Zudem übersieht die Grenzerkennung Randlösungen. Der Fehler betrifft die neuen Produktprofile, nicht den bereits korrigierten Burkert-Massenfaktor.

Zwei fachliche Restpunkte bleiben: Vergleichsscores werden bei ungültigen Punkten auf unterschiedlichen Teilmengen berechnet; die bisherige D/i-Sensitivität betrifft ausschließlich den deskriptiven Burkert-Fit. Eine zusätzliche explorative Gegenrechnung des MOND-Außenradientests zeigt tatsächlich D/i-Abhängigkeit, aber keinen verschwundenen Ausreißer in den fünf einzeln variierten Szenarien.

## Tatsächlich geprüfter Umfang

- HEAD entsprach beim Abruf dem genannten Commit. Der GitHub-CI-Lauf [36249524929](https://github.com/GenesisAeon/scoped-correspondence-formalism/actions/runs/36249524929) wurde zuletzt als `completed/success` bestätigt.
- Alle aktiven Pythondateien unter `src/`, `scripts/` und `verification/` des lokalen Snapshots stimmen mit den Git-Blob-Hashes überein. Historische Archivdateien waren nicht Gegenstand der Prüfung.
- Die sechs Galaxy/SPARC-Skripte lokal ausgeführt: **52/52 analytische/synthetische Einzelprüfungen plus 5/5 echte Datenchecks**, ohne Skip. Die gesamte historische 99-Skripte-Suite wurde lokal nicht erneut ausgeführt.
- Die neue CLI vollständig ausgeführt: zwölf Fits, zwölf Profile mit je 41 Punkten, zwölf Sensitivitätsanalysen und 18 Modus-B-Scores. Beide Quelldateien stimmen weiterhin mit den festgelegten SHA-256-Werten überein.
- Alle 492 Profilpunkte durch eine separat formulierte, vektorisierte Zielfunktion gegengeprüft. Niedrigere zulässige Kandidaten durch eine zusätzliche Suche über eta einschließlich der Endpunkte gesucht. Den stärksten Befund außerdem durch unabhängige Integration der Dichte bestätigt.
- Den Skip-Fall über den unveränderten Runner nachgerechnet und eine synthetische Kontrolle für unterschiedliche Auswertungsmengen ergänzt.
- Eine zusätzliche, ausdrücklich **explorative** D/i-Auswertung auf UGC02487s bereits bekanntem Außenradien-Test gerechnet. Keine neue konfirmatorische Evaluation, keine Auswahl günstiger Szenarien und kein Nachfitten der Halo-Parameter auf Testpunkten.
- Python 3.12.14, NumPy 2.3.5, SciPy 1.17.0. Keine Repository-Änderungen oder Pushes durch dieses Review. Keine SPARC-Rohdaten im Reproduktionspaket.

## Abgleich mit R1–R7

| Alter Befund | Stand dieses Reviews |
|---|---|
| R1: halbe Burkert-Masse im Reihenzweig | Behoben. Bei `rho0=0.05`, `r0=3000 pc`, `r=0.3 pc` ist das Verhältnis zur unabhängigen Massenquadratur `0.9999999999999999`. |
| R2: ungleiche Fits und verlorene Status | Kernkorrektur umgesetzt: gemeinsamer Fithelfer und Status/Randkennzeichnung im Score. NGC3109/NFW bleibt als grenzabhängig sichtbar. Vollständige Fitparameter und tatsächlich benutzte Grenzen fehlen weiterhin im Modus-B-Export. |
| R3: ungültige Vorhersage still auf null gesetzt | Für Endausgaben behoben, aber die neue Auswertung auf modellspezifisch gültigen Teilmengen benötigt noch einen gemeinsamen Vergleichsvertrag, siehe F2. |
| R4: NFW-Null als zentraler Grenzwert | Behoben. Exakt `r=0` wird für `g` zurückgewiesen; einseitiger Grenzwert separat geprüft. |
| R5: Datenvalidierung | Die benannten Lücken sind geschlossen; alle Floatfelder und tabellenübergreifende Entfernungen werden berücksichtigt. Physikalische Grenzen für spätere Sensitivitätsszenarien bleiben eine separate Aufgabe. |
| R6: Produktprofile und Sensitivitäten fehlen | Wesentlich ausgebaut und reproduzierbare CLI vorhanden. Neuer numerischer Profilfehler F1; Modus-B-Sensitivität und Grafiken ausdrücklich offen. |
| R7: Skip als passed | Behoben. Gegenprobe: `count=1, passed=0, skipped=1, failed_count=0`, Exitcode 0. |

## F1 — P1: Die Profilroutine übersieht kleinere zulässige Werte

**Ort:** `src/scoped_correspondence/validation/galaxy_pilot.py`, `profile_likelihood_burkert`, insbesondere Zeilen 527–542.

Die Routine soll für jedes feste Produkt

\[
q(\psi)=\min_{\eta\in I(\psi)}\chi^2(\psi,\eta)
\]

berechnen. Tatsächlich wird ein einzelner Aufruf von `minimize_scalar(..., method="bounded")` über das ganze zulässige Intervall verwendet. Dieses Verfahren sucht ein **lokales** Minimum. SciPy weist ausdrücklich auf diese Beschränkung bei mehreren Minima hin: [offizielle Dokumentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.minimize_scalar.html).

### Ein Gegenbeispiel aus dem echten Pilot

NGC3917, festes `psi=3.376763543341262`, ursprüngliche Parametergrenzen:

| Auswertung | eta | chi² |
|---|---:|---:|
| Ausgabe der Profilroutine | 2,6655339350918434 | 1253,4958125153437 |
| Zulässiger oberer Rand | 5,5 | 459,7879046693124 |

Der zweite Wert stammt aus einer eigenständigen Dichtequadratur für alle Radien. Er benötigt keinen konkurrierenden Optimierer. Bei `eta=5.5` liegen `r0=10^5.5 pc` und `log10(rho0)=psi-5.5` innerhalb der deklarierten Grenzen. Deshalb ist bereits dieser eine zulässige Punkt ein vollständiges Gegenbeispiel zur behaupteten Minimalität: Das wahre Minimum kann höchstens 459,7879 betragen, niemals 1253,4958.

Auch ein ausschließliches Nachprüfen der Endpunkte reicht nicht: Bei derselben Galaxie und `psi=3.276763543341262` liefert die Routine `q=1113.1341772`, während ein anderer **innerer** Kandidat bei `eta=5.4666860147` nur `q=420.2070548` erreicht. Die unabhängige Hilfssuche findet dort zwei lokale Becken.

### Umfang der nachgewiesenen Abweichungen

Ein Profilpunkt wird hier gezählt, wenn die Differenz zum gefundenen besseren Kandidaten größer als `1e-4 * max(1, q_candidate)` ist. Diese Schwelle hält bloße letzte Rundungsstellen aus der Zählung heraus.

| Galaxie | Nachgewiesene bessere Kandidaten / 41 | Größte chi²-Differenz |
|---|---:|---:|
| F583-4 | 15 | 123,40 |
| NGC0024 | 4 | 408,83 |
| NGC3917 | 14 | 793,71 |
| NGC3893 | 6 | 90,11 |
| NGC3521 | 16 | 201,12 |
| F568-V1 | 7 | 162,39 |
| NGC3726 | 12 | 80,92 |

Insgesamt **74 von 492 Punkten bei sieben von zwölf Galaxien**. Für die übrigen fünf Galaxien wurden innerhalb dieser Gegenprüfung keine entsprechend großen Abweichungen gefunden. Dies ist kein Beweis globaler Optimalität der Hilfssuche. Für den Fehlernachweis genügt jeweils ein direkt nachgerechneter besserer zulässiger Wert.

### Warum mehrere Becken fachlich plausibel sind

Bei festem `mu_h=rho0*r0`, `x=r/r0` und Burkert-Klammer `B(x)` gilt für den Haloanteil

\[
v_h^2(r)=2\pi G\mu_h r\,\frac{B(x)}{x^2}.
\]

Für `x -> 0` und für `x -> infinity` geht `B(x)/x²` gegen null. Eine vorgegebene Geschwindigkeit unterhalb des Maximums kann an einem einzelnen Radius daher auf zwei Skalenlängenästen erreicht werden. Bei mehreren Radien können verschiedene lokale Anpassungsbecken verbleiben. Das ist eine konkrete Verbindung zwischen Beobachtungsäquivalenz und praktischer Identifizierbarkeit; eine unimodale Zielfunktion darf hier nicht vorausgesetzt werden.

### Zwei zusätzliche Randfehler derselben Routine

1. **Randkennzeichnung:** Der Code prüft die Entfernung zur Grenze mit `1e-6`, der Optimierer kann jedoch schon einige `1e-6` davor stoppen. Beispiel NGC0024, `psi=3.6250359949019417`: Ausgabe `eta=5.499995009877191`, `boundary_hit=False`; der explizite Endpunkt `eta=5.5` verbessert `q` von 1299,98115 auf 1299,95602. Im Hilfsvergleich liegen 22 ausgewählte Minimumkandidaten auf einer Grenze, während der aktuelle Export keinen einzigen Randtreffer meldet. Die Dokumentationsaussage „keine der 12×41 Rasterpunkte trifft eine Grenze“ ist damit nicht haltbar.
2. **Einpunktintervalle:** `eta_lo >= eta_hi` wird vollständig als unzulässig markiert. Bei Gleichheit existiert aber genau ein zulässiger Punkt. Unter den Standardgrenzen sind `psi=-3` mit `eta=1` und `psi=6.5` mit `eta=5.5` zulässig; beide werden derzeit als `infeasible_bounds` ausgegeben.

### Korrekturauftrag und Abnahme

- Endpunkte stets ausdrücklich auswerten; `lo==hi` direkt auswerten, nur `lo>hi` als leer behandeln.
- Mehrere lokale Becken suchen und verfeinern, etwa mit kontrolliertem Bracketing über eta sowie unabhängigen Starts. Ein zusätzlicher grober Scan allein ist kein globaler Beweis. Numerische Verfeinerung und Suchstatus sichtbar machen.
- Randstatus anhand des tatsächlich gewählten Kandidaten, der aktiven Grenze und abgestimmter Toleranzen bestimmen; nicht ausschließlich einen beliebigen festen Abstand zum lokalen Optimierergebnis prüfen.
- Bei Verwendung erweiterter Fitgrenzen dieselben Grenzen in die Profilierung übernehmen und exportieren. Ein Bestfit außerhalb des Profilbereichs darf nicht mit einem anders begrenzten Profil verrechnet werden.
- Regressionen: beide NGC3917-Gegenbeispiele; NGC0024-Randfall; beide Einpunktintervalle; synthetischer Fall mit mehreren getrennten Becken. Für CI eigenständig erzeugte Fixtures nutzen; reale Beispiele bleiben lokal hashgeprüft.
- Alle zwölf Kurven und die Aussagen in `docs/galaxy_pilot.md §6.1` neu erzeugen. Aus den aktuellen Kurven noch keine Identifizierbarkeits- oder Intervallbehauptungen ableiten.

## F2 — P2: MAE/RMSE auf unterschiedlichen Punktmengen sind kein gemeinsamer Modellvergleich

**Ort:** `galaxy_pilot.py`, `_predict_v_with_validity`, `_final_rmse_and_invalid` und `evaluate_baselines_on_holdout`.

Die neue Kennzeichnung ungültiger Vorhersagen ist eine Verbesserung. Der Score wird aber für jede Baseline nur über deren eigene gültige Punkte gebildet. So kann eine Baseline gerade einen schwierigen Punkt verlieren und mit einem kleinen RMSE neben vollständig ausgewerteten Modellen stehen. `n_invalid` macht den Ausfall sichtbar, löst aber die fehlende Vergleichbarkeit noch nicht.

**Selbst erzeugtes Beispiel:** Drei Testpunkte, darunter ein Punkt mit negativem baryonischem Gesamtbeitrag, dessen Halo-Gesamtsumme positiv bleibt. MOND ist dort außerhalb seines skalaren Geltungsbereichs.

| Baseline | n_test | n_invalid | Tatsächlich bewertet | ausgegebener RMSE |
|---|---:|---:|---:|---:|
| Burkert | 3 | 0 | 3 | 538,8184 |
| NFW | 3 | 0 | 3 | 533,2543 |
| MOND | 3 | 1 | 2 | 0,0 |

Die beiden gültigen MOND-Punkte wurden absichtlich so konstruiert, dass sie exakt passen. Der schwierige dritte Punkt fehlt nur in dessen Score. Das ist kein nachgewiesener Fehler in den zwölf Referenzgalaxien, bei denen keine solchen Ausfälle auftreten; es ist eine verbleibende Lücke für die verallgemeinerte Auswertungs-API.

**Korrekturauftrag:** Vorab einen Vergleichsvertrag festlegen. Beispielsweise ist bei einem ungültigen Punkt die betreffende Baseline für den vollständigen Testsatz `out_of_domain`, mit `primary_score=null`; ein Teilmengenscore wird separat als Diagnose ausgegeben. Alternativ dieselbe explizit ausgewiesene gemeinsame Maske für alle Modelle verwenden und den Verlust an Abdeckung berichten. `n_scored`, Punkt-IDs und Geltungsbereichsstatus exportieren. Fehlgeschlagene Fits dürfen ebenfalls nur diagnostische Scores besitzen.

Strikte JSON-Ausgabe verwenden: nichtendliche diagnostische Werte als `null` plus Status serialisieren. Das gegenwärtige `json.dumps` kann bei vollständig ungültigen Ergebnissen das nichtstandardkonforme Literal `NaN` schreiben.

**Abnahme:** Der obige Kontrollfall erzeugt keinen gewöhnlichen vollständigen Vergleichsscore „MOND RMSE=0 bei n_test=3“. Reihenfolge und Ausfälle bleiben in Ergebnisdatei und Tabelle nachvollziehbar.

## Was die Sensitivitätsresultate jetzt aussagen

Die Faktoren sind als **Max/Min der fünf deskriptiven Szenarien** reproduziert:

| Galaxie | Minimum mu_h | Maximum mu_h | Max/Min |
|---|---:|---:|---:|
| NGC3521 | 336,31284 | 1737,46597 | 5,16622 |
| UGC02487 | 615,93892 | 1630,99474 | 2,64798 |

Einheiten: M_sun/pc². Referenz plus jeweils einzeln `D±sigma_D` und `i±sigma_i`; keine gemeinsame Wahrscheinlichkeitsverteilung. Der Faktor ist weder ein kalibriertes Intervall noch eine Zerlegung der gesamten Unsicherheit. Er zeigt, dass die geschätzte Halo-Produktgröße unter diesen Annahmen deutlich beweglich ist.

Die aktuelle Sensitivitätsfunktion verwendet vollständige Kurven und refittet nur Burkert. Daraus allein folgt noch keine Änderung eines MOND-Testscores. Die Formulierung „ein erheblicher Teil der Unsicherheit stammt aus …“ sollte deshalb zu einer direkt belegten Aussage über Szenarienempfindlichkeit abgeschwächt werden.

### Zusätzliche explorative UGC02487-Gegenrechnung

Dieselbe vorgegebene Liste von fünf Szenarien auf den bisherigen 70/30-Radiensplit angewendet. Burkert und NFW jeweils nur auf den inneren Punkten neu gefittet; MOND bleibt mit festem `a0` ohne lokalen Fit. Alle drei Modelle erhalten jeweils dieselbe Datenumrechnung.

Bei Inklinationsänderung werden beobachtete Geschwindigkeit und Fehler mit `k=sin(i_ref)/sin(i_neu)` skaliert. Um reine Änderung der Geschwindigkeitsskala aus dem Vergleich herauszuhalten, stehen in der Tabelle die RMSE-Werte zurückgerechnet auf die **Referenz-Geschwindigkeitsskala**, also `RMSE_szenario/k`. Bei Entfernungsszenarien ist `k=1`.

| Szenario | Burkert | NFW | MOND |
|---|---:|---:|---:|
| Referenz | 14,5660 | 9,7009 | 62,1372 |
| D + sigma_D | 14,4819 | 9,4965 | 42,6309 |
| D − sigma_D | 14,5107 | 9,8171 | 83,1863 |
| i + sigma_i | 14,3443 | 9,3170 | 30,9482 |
| i − sigma_i | 14,4321 | 9,8478 | 95,4022 |

Alle Werte in km/s auf der erläuterten Referenzskala; keine ungültigen Punkte oder endgültigen Halo-Randtreffer in diesen Läufen. Der direkte, noch nicht zurückskalierte MOND-RMSE bei `i+sigma_i` beträgt 27,7275 km/s.

**Interpretation:** D/i-Annahmen beeinflussen den MOND-Ausreißer tatsächlich stark. In den fünf einzeln variierten Szenarien bleibt NFW beim bedingten Test vorne und MOND deutlich abweichend. Damit ist ein Beitrag der Annahmen konkret gezeigt, aber keine vollständige Erklärung und keine Entscheidung zwischen physikalischen Theorien. Gemeinsame D/i-Variationen, andere M/L-Annahmen oder eine andere MOND-Beschreibung wurden hier nicht geprüft. Der bereits bekannte Test macht diese Zusatzanalyse explorativ; das günstigste Szenario darf nicht nachträglich zum ursprünglichen Referenzbefund werden.

## Verbleibende Berichtsarbeit

- In `docs/galaxy_pilot.md §6.2` steht NGC3726 zweimal: einmal 2,20× und einmal 1,16×. Der zweite Eintrag ist zu entfernen; die Tabelle hat sonst 13 Zeilen für zwölf Galaxien.
- Die CLI erzeugt tatsächlich drei CSV-Dateien, während der Text von zwei spricht.
- Der Export enthält bisher nur die Anzahl der Ausschlüsse, nicht die bereits vorhandenen Ausschlussgründe; Modus B enthält Scores und Status, aber keine Trainingsparameter oder tatsächlichen Grenzen. Für die geplante Reproduktionsspur ergänzen.
- Die CLI berechnet Modus A einschließlich aller Evaluationspunkte vor Modus B. Der aktuelle Code übernimmt daraus keine Fitparameter, deshalb ist hier kein konkretes Datenleck nachgewiesen. Für einen überprüfbaren zukünftigen Ablauf trotzdem Modus B und dessen Konfiguration zuerst einfrieren und exportieren, danach Modus A ergänzen.
- Plot-Erzeugung und Modus-B-Sensitivität sind inzwischen ausdrücklich offen vermerkt. Das ist eine angemessene Einschränkung. Gesamtabschlussformulierungen entsprechend daran anpassen.
- Der kommentarbasierte Begriff „clip-then-let-the-residual-grow“ beim Optimieren ist ungenau: Im Bereich negativer Gesamtbeschleunigung ist die gekappte Vorhersage konstant null, der Residualbeitrag wächst dort nicht mit weiterer Negativität. Für einen allgemeinen Adapter eine dokumentierte Zulässigkeits- oder Strafstrategie vorsehen; die aktuellen zwölf Referenzfits sind dadurch nicht als falsch nachgewiesen.

## Enger nächster Auftrag für Claude-Code

1. **F1 beheben und unabhängig regressieren.** Alle zwölf Profile neu rechnen; alte falsche Kurven als überholt kennzeichnen. Die ursprünglichen Bestfit- und Sensitivitätszahlen nicht allein wegen des Profilfehlers verändern.
2. **F2 abschließen.** Gemeinsame Auswertungsregel, aussagekräftige Status, `n_scored` und strikte JSON-Serialisierung.
3. **Berichtsartefakte vervollständigen.** Auswahlgründe, Trainingsparameter, verwendete Grenzen, numerische Profilstatus und die redaktionellen Korrekturen.
4. **D/i-Analyse auf Modus B erweitern**, vorab definierte Szenarien für alle Baselines und sichtbarer explorativer Status. Die obige UGC02487-Tabelle dient als unabhängig reproduzierter Kontrollfall.
5. Gezielte Gegenbeispiele, vorhandene Gesamtsuite und Linkchecks ausführen. Reale Daten zusätzlich lokal hashgeprüft. G6 bleibt von dieser Arbeit unabhängig und weiterhin an den Volltext gebunden.

Die wissenschaftliche Leitfrage ist jetzt präzise: **Welche Produktwerte erlauben die Daten nach vollständiger Suche über den Störparameter, und welche Modellunterschiede bleiben unter denselben Beobachtungsannahmen bestehen?** Genau dafür eignet sich SCF als Prüfrahmen.

## Reproduktion

Im ZIP: beide Review-Skripte, die erzeugten Diagnose-JSON-Dateien, die ursprünglichen CLI-Ergebnisdateien dieser Reviewrunde und dieses Dokument. Keine Rohdateien, Rohdatenzeilen oder Repositorykopie. Abhängigkeiten: SCF-Umgebung mit NumPy/SciPy.

Zuerst die eingecheckte CLI am Prüfcommit ausführen:

```bash
python /pfad/zum/repo/scripts/run_real_galaxy_pilot.py \
  --sparc-dir /pfad/zu/lokalen/sparc-dateien --out-dir pilot_results
```

Dann die Gegenrechnungen:

```bash
python audit_new_profiles.py --repo /pfad/zum/repo \
  --sparc /pfad/zu/lokalen/sparc-dateien --pilot pilot_results \
  --output profile_audit.json

python audit_followup_cases.py --repo /pfad/zum/repo \
  --sparc /pfad/zu/lokalen/sparc-dateien --output followup_cases.json
```

Beide Reviewprogramme prüfen die festgelegten Dateihashes und laden nichts herunter. Der zweite Aufruf benötigt für die isolierte Skip-Prüfung einen temporären symbolischen Link. Bei später veränderten APIs die Skripte entsprechend anpassen; beobachtete alte Fehlerwerte nicht als dauerhafte Sollwerte festschreiben.

## Quellen

- [Commit und vollständiger Diff](https://github.com/GenesisAeon/scoped-correspondence-formalism/commit/84848a464bfba6a6d1160de303b2eacc429114eb)
- [Profilierung, Fit und Scores](https://github.com/GenesisAeon/scoped-correspondence-formalism/blob/84848a464bfba6a6d1160de303b2eacc429114eb/src/scoped_correspondence/validation/galaxy_pilot.py)
- [Lokale CLI](https://github.com/GenesisAeon/scoped-correspondence-formalism/blob/84848a464bfba6a6d1160de303b2eacc429114eb/scripts/run_real_galaxy_pilot.py)
- [Pilotdokumentation](https://github.com/GenesisAeon/scoped-correspondence-formalism/blob/84848a464bfba6a6d1160de303b2eacc429114eb/docs/galaxy_pilot.md)
- [SciPy: lokaler Charakter von minimize_scalar](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.minimize_scalar.html)
- [Offizielle SPARC-Metadaten](https://astroweb.case.edu/SPARC/SPARC_Lelli2016c.mrt) und [Komponententabelle](https://astroweb.case.edu/SPARC/MassModels_Lelli2016c.mrt). Hashes im Code und Quellenprotokoll; ursprüngliche Bytes lokal erneut geprüft.

Die Zahlen zu Gegenbeispielen und Sensitivitäten stammen aus den beigefügten eigenen Rechnungen. Die Suche nach niedrigeren Profilwerten wird ausdrücklich nicht als mathematischer Beweis globaler Optimalität ihrer eigenen Kandidaten ausgegeben.
