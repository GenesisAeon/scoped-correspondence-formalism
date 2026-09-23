# Review: Scoped Correspondence Formalism

Geprüfter Stand: 22. September 2026 · Bericht abgeschlossen: 23. September 2026 · Repository `GenesisAeon/scoped-correspondence-formalism` · Commit `3e8dce358e37017b375aaaae5b6f0bfe63f4d94f` · Vergleich mit `f8e249f`.

**Die Umsetzung ist ein deutlicher Fortschritt. Als nächsten Schritt empfehle ich einen gezielten Durchgang zur Absicherung der Validierung, anschließend das bereits geplante Paket 6.** Die neuen Module machen Hypothesen prüfbarer. Einige neue Schlussfolgerungen überschreiten jedoch das, was ihre Experimente zeigen. Besonders wichtig sind zeitlich verfügbare Informationen, die Stationaritätsannahme der Hawkes-Brücke und konsistente Referenzen im Klimamodell.

**Prüfumfang und Belastbarkeit**

Ich habe den aktuellen Repository-Baum und die neuen Implementierungen gelesen, eine isolierte Ausführungskopie erstellt und 160 Quell-, Daten- und Verifikationsdateien gegen ihre Git-Blob-SHAs geprüft: keine Abweichung. Alle **66 ausgeführten mathematischen Verifikationsskripte bestanden**. Umgebung: Python 3.12.14, NumPy 2.3.5, SciPy 1.17.0. Zusätzlich wurden vier unabhängige Gegenproben und drei Klimareferenz-Refits ausgeführt.

Zwei Dokumentationsskripte (`verify_formalism.py`, `verify_extensions.py`) wurden nicht erneut ausgeführt: Eine benötigte binäre DOCX-Datei ließ sich nicht lokal beziehen. Sie ist im aktuellen Git-Baum nachgewiesen; 175 weitere lokale Dokumentlinks waren auflösbar. Die Aussage lautet deshalb 66 ausgeführte Skripte bestanden, nicht vollständige Ausführung aller 68 Skripte. Es wurden keine Änderungen im GitHub-Repository vorgenommen.

Die grünen Prüfungen belegen die getesteten Rechenwege. Die folgenden Gegenbeispiele zeigen, dass einige Prüfungen die wissenschaftliche Interpretation noch nicht ausreichend absichern.

**Was seit der letzten Review überzeugend verbessert wurde**

| Änderung | Bewertung und verbleibende Grenze |
|---|---|
| Exakter EBM-Propagator, beschränkte Optimierung, mehrere Startpunkte | Der frühere schlechte Klimafit ist behoben. RMSE rund 0,09036 °C; Übereinstimmung mit unabhängiger ODE-Integration auf ungefähr 9 × 10⁻⁸ °C. Der Rückkopplungsparameter α liegt weiterhin am unteren Suchrand. |
| Korrigierte Tracking-Gleichung und vorsichtigere χ-Aussage | Der lokale Indikator wird angemessener von einer globalen Kippschwelle getrennt. |
| Puffervergleich bei gleicher Gesamtlast | Die zuvor vermischten Effekte von Pulsform und Lastmenge werden tatsächlich getrennt untersucht. |
| Gemeinsame Prognoseursprünge und Vergleichsmodelle | Eine wesentliche Verbesserung gegenüber Vergleichen auf unterschiedlichen Ausschnitten. |
| Profile, Optimierungsmetadaten und explizites ETAS-Beobachtungsende | Die Grenzen der Parameterschätzung werden sichtbar. Die Interpretation offener Profile muss noch präzisiert werden. |
| B7: Energiebilanz und Puffer als lineare Systeme mit Wirkungskernen | Eine sinnvolle mathematische Verwandtschaft mit konkreter Konstruktion und Gegenbeispiel bei zeitabhängigen Koeffizienten. |
| Weitere Länder, Zeitfenster und reales Gesamtforcing | Nützliche Erweiterung der Datenbasis; die zusätzlichen Fälle ersetzen noch keine vorab festgelegte externe Validierung. |

Die neue EBM-Auswertung ergibt einen gepoolten Prognose-RMSE von etwa 0,1064 °C gegenüber 0,1171 °C für den Trend der letzten 30 Jahre, 0,1343 °C für den expandierenden Trend und 0,1376 °C für Persistenz. Dabei erhält das EBM den tatsächlich später beobachteten CO₂-Verlauf. Das ist ein ausdrücklich deklarierter **bedingter Hindcast**. Ein Vorteil bei einem praktisch verfügbaren Informationsstand ist damit noch nicht gezeigt.

Beim ETAS-Vergleich liegt die verwendete Näherung mit RMSE etwa 26,31 zwischen Persistenz (22,96) und homogener Rate (28,78). Das ist ein informativer negativer bzw. gemischter Befund für diese Näherung. Sie berücksichtigt jedoch nicht alle Nachkommen zukünftig auftretender Ereignisse. Auch eine Poisson-Verteilung um diesen Mittelwert ist noch keine vollständige ETAS-Prognoseverteilung.

**1. Hohe Priorität: Prognoseintervalle verwenden spätere Beobachtungen**

Fundstelle: [`mechanistic_probabilistic_evaluation.py`](https://github.com/GenesisAeon/scoped-correspondence-formalism/blob/3e8dce358e37017b375aaaae5b6f0bfe63f4d94f/src/scoped_correspondence/validation/mechanistic_probabilistic_evaluation.py), Funktion `leave_one_origin_out_intervals`, insbesondere Zeile 128.

Die Kalibrierung schließt den Fehler des gerade bewerteten Prognoseursprungs aus, verwendet aber Fehler aller anderen Ursprünge, auch späterer. Damit wird ein retrospektives Leave-one-out-Intervall berechnet. Es ist kein Intervall, das zum damaligen Prognosezeitpunkt hätte ausgegeben werden können. Die Bezeichnung als Schutz vor Informationslecks ist in diesem zeitlichen Sinn unzutreffend. Zeitreihenvalidierung setzt voraus, dass nur bereits verfügbare Beobachtungen verwendet werden [1].

**Ausgeführtes Gegenbeispiel:** Vier Ursprünge, jeweils ein Schritt Vorhersage, Punktprognose stets null. Das Intervall des ersten Ursprungs beträgt `[1,2; 2,8]`. Ändere ich ausschließlich den beobachteten Wert des letzten Ursprungs von 3 auf 100, wird das frühere Intervall `[1,2; 80,4]`. Seine eigene Beobachtung und Punktprognose bleiben unverändert.

**Reparatur:** Für einen Ursprung o dürfen nur Fehler kalibrieren, deren Zielbeobachtung zu o bereits verfügbar war. Ein früherer Ursprung allein genügt bei mehrschrittigen Prognosen nicht. Ohne Meldeverzögerung muss beispielsweise `origin_i + horizon_i <= o` gelten; mit Verzögerung entscheidet `available_at`. Bei zu wenig Vorgeschichte ist ein expliziter Status für unzureichende Kalibrierung erforderlich. Danach Intervallwerte und Rangfolgen neu berechnen.

**Abnahme:** Werden beliebige Daten nach dem Informationsstichtag verändert, bleiben die vorher ausgegebenen Punktprognosen und Intervalle unverändert. Der Test muss die gesamte Auswertung einschließlich Merkmalsbildung und Modellauswahl betreffen.

**2. Hohe Priorität: COVID-Referenzmittelwert enthält seinen eigenen Zielwert**

Fundstelle: [`covid_observation_model.py`](https://github.com/GenesisAeon/scoped-correspondence-formalism/blob/3e8dce358e37017b375aaaae5b6f0bfe63f4d94f/src/scoped_correspondence/validation/covid_observation_model.py), Zeilen 107–120.

Die Verwendung echter Tageszählungen und die getrennte Dispersionsschätzung sind Verbesserungen. Der als `predicted_mean` bewertete Sieben-Tage-Mittelwert enthält allerdings die aktuelle Tageszählung selbst. Die Trennung der Dispersionskalibrierung beseitigt diese Zielwertabhängigkeit nicht.

**Ausgeführtes Gegenbeispiel am 12. März 2020:** Beobachtung 6.756, Referenzmittelwert 5.033,2857. Erhöhe ich nur die Tageszählung um 700 und aktualisiere ihre davon abgeleiteten Wochenaggregate konsistent, steigt der vermeintliche Prognosemittelwert um 100 auf 5.133,2857. Alle früheren Rohbeobachtungen und die gefittete Dispersion bleiben gleich.

Der Poisson/NB-Vergleich kann als **deskriptive Bewertung der Streuung um einen retrospektiven Glättungswert** stehen bleiben. Er zeigt noch keine zirkelfreie Prognosegüte und isoliert Überdispersion nicht von einer falsch spezifizierten Mittelwertkurve, Trendverzögerung oder Meldeeffekten. Das Verhältnis zweier logarithmischer Scores sollte außerdem nicht als „100-mal bessere Prognose“ interpretiert werden.

**Reparatur und Abnahme:** μₜ ausschließlich aus bis t−1 verfügbarer Information erzeugen, zunächst etwa mit dem vorhandenen Renewal-Modell und einem verzögerten Mittelwert als Vergleich. Dispersion nur aus dem jeweiligen Trainingsfenster schätzen; auf späteren rohen Tageszählungen bewerten. Eine Änderung von yₜ darf μₜ nicht verändern. Ein vollständiges latentes Zustandsmodell kann weiterhin ein eigener späterer Schritt bleiben.

**3. Hohe Priorität für den Formalismus: B8 trennt Kernstruktur und Stationarität nicht sauber**

Fundstelle: [`docs/structural_relations.md`](https://github.com/GenesisAeon/scoped-correspondence-formalism/blob/3e8dce358e37017b375aaaae5b6f0bfe63f4d94f/docs/structural_relations.md), Abschnitt B8, insbesondere Zeilen 300–322; parallel die Roadmap und der Verifikationstext.

Die Identität Σₛ φₛ = R für φₛ = Rwₛ mit normierten nichtnegativen Gewichten ist korrekt und nützlich. Unter einer entsprechenden Verzweigungskonstruktion ist dies die mittlere Zahl direkter Nachkommen. Dafür allein ist keine Stationarität erforderlich.

Nicht korrekt ist der zusätzliche Schluss, konstantes R mache die Renewal-Rekursion zu einem stationären linearen Hawkes-Prozess. Zeitlich konstante Koeffizienten garantieren keine stationäre Prozessverteilung. Bei einem linearen Hawkes-Prozess mit positiver Immigration μ und endlichem stationären Mittel verlangt die Mittelwertgleichung

\[
\bar\lambda=\mu+n\bar\lambda,
\qquad \bar\lambda=\frac{\mu}{1-n}
\]

den subkritischen Fall n < 1. Genau dieser Bereich trägt die klassische stationäre Clusterrepräsentation [2]. Das im Repo geprüfte R = 1,68 ist superkritisch. Bei μ = 1 ergäbe die vermeintlich stationäre Formel −1,4706, also eine unmögliche negative mittlere Rate. Als Modell nichtstationären Verzweigungswachstums ist R = 1,68 dagegen durchaus sinnvoll.

Zudem ist eine deterministische Inzidenzrekursion nicht selbst ein stochastischer Punktprozess. Eine präzise Brücke muss festhalten, ob sie die Kernmasse, eine Gleichung für den Erwartungswert, eine bedingte Intensität oder die vollständige Prozessverteilung erhält. Der Übergang zwischen diskreter Renewal-Zeit und kontinuierlicher Hawkes-Zeit benötigt ebenfalls eine explizite Konstruktion.

**Abnahme:** Den gültigen Kernmassenbefund behalten; ein subkritisches Beispiel R = 0,8 ergänzen; R = 1,68 als Gegenbeispiel zur Stationaritätsbehauptung verwenden. Die Brückenkarte sollte auf jeder Seite Objekt, Abbildung, erhaltene Größe und erforderliche Annahmen ausweisen.

**4. Mittlere Priorität: Ein begrenzter Scan kann Unbeschränktheit nicht beweisen**

Fundstelle: [`identifiability/profile_likelihood.py`](https://github.com/GenesisAeon/scoped-correspondence-formalism/blob/3e8dce358e37017b375aaaae5b6f0bfe63f4d94f/src/scoped_correspondence/identifiability/profile_likelihood.py), Funktion `likelihood_interval`, insbesondere `unbounded_reason="open_at_grid_boundary"`; außerdem die neue Interpretation der NLP-Profile.

**Ausgeführtes Gegenbeispiel:** Für χ²(θ) = θ² und Schwelle 1 ist das globale Intervall exakt [−1, 1]. Ein Scan nur bei −0,5, 0 und 0,5 führt in der aktuellen API dennoch zu `unbounded=True`. Tatsächlich ist lediglich innerhalb des Scans keine Intervallgrenze gefunden worden. Die gleichzeitig mögliche Klassifikation `identifiable` zeigt zusätzlich, dass die Statusbegriffe verschiedene Dinge meinen.

**Reparatur:** Getrennte Status für geschlossene Grenze, offenes Scanende, erreichte Parametergrenze und fehlgeschlagene Optimierung. Profile bei Bedarf adaptiv erweitern und die Konvergenz jeder bedingten Optimierung dokumentieren. Ohne weitergehenden Nachweis „im untersuchten Bereich nicht eingegrenzt“ formulieren. Für formale Konfidenzaussagen müssen auch die verwendete Likelihood, Fehlervarianz und gegebenenfalls zeitliche Residualabhängigkeit zu den Schwellen passen.

**5. Vor Interpretation des Gesamtforcing-Vergleichs: Referenzniveaus konsistent modellieren**

Fundstelle: [`energy_balance_full_forcing.py`](https://github.com/GenesisAeon/scoped-correspondence-formalism/blob/3e8dce358e37017b375aaaae5b6f0bfe63f4d94f/src/scoped_correspondence/validation/energy_balance_full_forcing.py), Zeilen 122–136.

Für den Vergleich der beiden CO₂-Eingaben werden ihre Referenzniveaus angeglichen; die drei eigentlichen Fits erhalten dagegen die nicht angeglichenen Reihen. 1959 beginnt Myhre bei 0, ERF-CO₂ bei 0,699576193 und ERF-Gesamt bei 0,587283068 W/m². Die ERF-Reihen beziehen sich auf 1750, die Myhre-Reihe auf 1959; die beobachtete Temperaturanomalie hat wiederum ihre eigene Referenzperiode.

**Ausgeführte Sensitivitätsprüfung mit unveränderter Fitfunktion:**

| Eingabe | RMSE, °C | Erreichte Parametergrenzen |
|---|---:|---|
| ERF-CO₂ minus eigener Wert 1959 | 0,09025 | α unten |
| ERF-Gesamt minus eigener Wert 1959 | 0,09425 | C_d oben, α unten |
| Myhre plus ERF-CO₂-Wert 1959 | 0,09404 | C_s oben, α unten, γ oben |

Damit kann die ursprüngliche Rangfolge „Gesamtforcing besser als CO₂-only“ bereits unter einer Änderung des Referenzniveaus umkehren. **Diese Gegenprobe ist keine physikalisch korrigierte Neuanalyse und beweist nicht, dass Gesamtforcing schlechter wäre.** Sie zeigt, dass die Interpretation des kleinen RMSE-Unterschieds noch von der Referenzbehandlung abhängt.

Eine konsistente Transformation der beiden Temperaturzustände T′ = T − δ verlangt bei dieser Modellform auch F′ = F − αδ. Nur F am Anfang auf null zu setzen repariert deshalb nicht das gesamte Modell. Geeignete nächste Optionen sind ein ausdrücklich modellierter Forcing-/Beobachtungsoffset oder eine physikalisch konsistente Initialisierung samt Vorgeschichte. Den tiefen Anfangszustand nicht ohne Begründung mit der Oberflächentemperatur gleichsetzen. Anschließend alle Eingaben im selben Modell und Validierungsprotokoll vergleichen; Randlösungen weiterhin offen ausweisen.

**Empfohlene Reihenfolge mit überprüfbaren Ergebnissen**

| Schritt | Konkretes Ergebnis | Fertig, wenn … |
|---|---|---|
| 1. Informationsgrenzen vereinheitlichen | Prognosezeit, Zielzeit und Datenverfügbarkeit für alle Auswertungen | Änderungen späterer Daten frühere Prognosen und Intervalle nicht verändern; COVID-Zielwert den eigenen Mittelwert nicht verändert. |
| 2. Mathematische Aussagen präzisieren | Korrigierte B8-Karte und differenzierte Profilstatus | Subkritisches und superkritisches Beispiel korrekt eingeordnet sind; das quadratische Profilgegenbeispiel besteht. |
| 3. Klimareferenz reparieren | Gemeinsame Referenz- und Initialisierungsdefinition | Alle Forcing-Varianten nach derselben dokumentierten Konvention verglichen werden. |
| 4. Ergebnisse neu einfrieren | Versionierter Benchmark mit Daten-Hash, Parametern, Informationsstichtag, Punktwerten und Intervallen | Die bereinigten Scores reproduzierbar sind und bedingte Hindcasts separat ausgewiesen werden. |
| 5. Paket 6 ausführen | Mehrdimensionale R-Tipping-/Viabilitätskarten | Amplitude, Rate, Dauer, Form und Reserve gezielt getrennt werden; Grenzlagen numerisch aufgelöst und unentschiedene Endzustände sichtbar bleiben. |

Paket 6 ist bereits der passende nächste größere Inhalt. Besonders informativ wären Schnitte bei gleicher Spitzenlast und bei gleicher integrierter Last. Ergebniszustände sollten mindestens Tracking, Wechsel, noch nicht entschieden, außerhalb des Scopes und Integrationsfehler unterscheiden. Numerische Karten sind zunächst empirisch bestimmte Grenzen; globale Schwellengeometrie mit Kanten-Zuständen und verbindenden Orbits ist der passende mathematische Anschluss [3].

**Der natürlichste neue mathematische Anschluss: zeitabhängige Wirkungskerne**

B7 liefert bei konstanten Koeffizienten den Einstieg. Für einen skalaren linearen Puffer mit zeitabhängiger Erholungsrate ist die Antwort auf eine frühere Anregung durch

\[
G(t,s)=\exp\!\left(-\int_s^t r(v)\,dv\right)
\]

gegeben. Sie hängt von beiden Zeitpunkten und der dazwischenliegenden Entwicklung ab. Im mehrdimensionalen Fall übernimmt der Evolutionsoperator Φ(t,s) diese Rolle. Um einen bewegten Gleichgewichtszweig x*(u) hat der Trackingfehler e = x − x*(u) lokal die Struktur

\[
\dot e=A(t)e-D_u x^*(u(t))\dot u(t)+\mathcal R(e,t).
\]

Die linearisierte Antwort integriert somit die gesamte Treibergeschichte, gewichtet mit Φ(t,s). Das verbindet Puffer, Energiebilanz, Zeitmaßstäbe und Tracking unmittelbar. Für globale Kippaussagen werden zusätzlich nichtlineare Restgliedkontrolle und Einzugsgebietsgeometrie benötigt. Die vorgeschlagene Verbindung ist eine mathematische Ableitung und ein Ausbauvorschlag, noch kein neues empirisch validiertes Ergebnis des Repos.

Damit lässt sich die ursprüngliche Beobachtung genauer untersuchen: Nicht nur „linear gegen exponentiell“, sondern **welche Treibergeschichte trifft auf welche Erholung, Reserve und Rückkopplung?** Ein nichtlinearer Treiber kann ein lineares System an eine vorgegebene Sicherheitsgrenze führen; ein nichtlineares System kann unter linearer Rampe kippen. Die bisherigen Ergebnisse widerlegen deshalb bestimmte Modelle unter bestimmten Bedingungen, nicht pauschal die gesamte Klasse linearer oder homogener Modelle.

Für die Datenarbeit danach sehe ich drei gezielte Optionen: ein COVID-Zählmodell mit vorwärts bestimmtem Mittelwert und getrennten Meldeeffekten; zusätzliche Klimabeobachtungen wie Ozeanwärme zur Einschränkung der beiden Speicher; ETAS-Prognosen mit vollständig berücksichtigten zukünftigen Kaskaden. Die Nullzählungen in Deutschland und den USA sprechen bereits für eine Poisson-/NB-Schätzung mit Log-Link anstelle der Regression logarithmierter Beobachtungen: Der bisherige Fehler bei null widerlegt diese konkrete Schätzroutine, nicht exponentielle Mittelwertmodelle allgemein.

**Quellen und Reproduktion**

Repositoryaussagen und Zahlen stammen aus dem oben fixierten Commit und eigenen Ausführungen. Die Gegenproben samt Ergebnissen und 66 Ausführungslogs befinden sich im begleitenden Archiv `SCF_Review_3e8dce3_Rechenbelege.zip`. Es enthält keine Kopie des Repositorys oder seiner Rohdaten. Für die Reproduktion wird ein eigener Checkout des angegebenen Commits benötigt.

1. Hyndman & Athanasopoulos, *Forecasting: Principles and Practice*, Abschnitt 5.10, [Time series cross-validation](https://otexts.com/fpp3/tscv.html). Begründet die zeitliche Trennung von Training und Prognosezielen.
2. Hawkes & Oakes (1974), *A cluster process representation of a self-exciting process*, Journal of Applied Probability 11, 493–503, [DOI 10.2307/3212693](https://doi.org/10.2307/3212693). [Vom Autor bereitgestellter Volltext](https://www.researchgate.net/publication/248498983_A_cluster_process_representation_of_a_self-exciting_process), insbesondere Bedingung (4), Lemma 1 und Theorem 1.
3. Wieczorek, Xie & Ashwin (2023), *Rate-Induced Tipping: Thresholds, Edge States and Connecting Orbits*, Nonlinearity, [arXiv:2111.15497](https://arxiv.org/abs/2111.15497), [DOI 10.1088/1361-6544/accb37](https://doi.org/10.1088/1361-6544/accb37).
