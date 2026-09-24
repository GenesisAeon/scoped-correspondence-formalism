# SCF: Fähigkeiten und sinnvoller Ausbau

Stand: 24. September 2026. Grundlage: Repository GenesisAeon/scoped-correspondence-formalism, Commit `0d4389804adf8d026923d2d9c08db5e3e902769a`, Paketversion `0.41.0a1`. Dies ist eine Bestandsaufnahme mit Ausbauvorschlägen; keine erneute Ausführung sämtlicher Tests und keine Änderung des Repositories.

**Einordnung**

SCF ist inzwischen eine installierbare wissenschaftliche Pythonbibliothek für präzise Modellbeziehungen, ausgewählte dynamische Systeme, Sicherheitsgrenzen und empirische Modellprüfung. Sein besonderes Potenzial liegt in einer gemeinsamen Arbeitsweise: Gegenstände und Abbildungen angeben, Annahmen begrenzen, erhaltene Strukturen prüfen, Fehler quantifizieren und Aussagen durch Gegenbeispiele begrenzen.

Viele Bausteine sind bewusst kleine Referenzmodelle. Numerische Prüfungen ausgewählter Fälle sind von allgemeinen mathematischen Beweisen zu unterscheiden. Die vorhandenen Realwelt-Piloten sind Forschungsexperimente; ihre Existenz allein begründet keine verlässliche operative Vorhersage.

**Was heute konkret möglich ist**

| Bereich | Konkrete Fähigkeit | Wesentliche Grenze |
|---|---|---|
| Modellkorrespondenz | Zustands- und Zeitabbildungen definieren; prüfen, ob Abbilden und zeitliche Entwicklung zusammenpassen; Residuen und Kompositionsfehler bestimmen. | Ein Zertifikat auf abgetasteten Zustands-Zeit-Paaren gilt für diese Prüfung; daraus folgt keine globale Äquivalenz. |
| Beobachtung und Information | Diskrete Kanalkapazität, gerichtete Information sowie redundante, einzigartige und synergistische Information untersuchen; endliche Kontextmodelle auf gemeinsame Darstellung prüfen. | Ergebnisse hängen von Verteilungen, gewählter Informationszerlegung und endlicher Modellklasse ab. Informationsabhängigkeit begründet allein keine Kausalität. |
| Dynamik und Kippen | Ausgewählte kubische Systeme, Hysterese, Erholung, zeitabhängige Antriebe, langsame/schnelle Dynamik und Frühwarnbeispiele berechnen. | Kein universeller Detektor realer Kipppunkte; lokale Kennzahlen und einzelne Normalformen benötigen ihre jeweiligen Voraussetzungen. |
| Viabilität | Puffer, Belastungspulse, Reservegrenzen und gekoppelte Sicherheitsbedingungen untersuchen; mehrdimensionale Parameterkarten mit expliziten ungeklärten Fällen erzeugen. | Sicherheit gilt bezüglich der definierten Grenze, Modellklasse und untersuchten Zeitspanne. Die aktuelle Kontrollbarriere ist ein skalares Referenzbeispiel. |
| Reduktion und Gedächtnis | Markov-Aggregationen und Generator-Lumpability prüfen; Schließungsfehler und Fehlerfortpflanzung untersuchen; an kleinen Beispielen Gedächtniseffekte darstellen. | Noch keine allgemeine datenbasierte Reduktionspipeline mit automatisch identifizierten Gedächtniskernen. |
| Kopplung und Thermodynamik | Einfluss, Transport, energietreue und dissipative Kopplung unterscheiden; ausgewählte GENERIC-, Dirac- und Entropiebeziehungen prüfen. | Strukturbedingungen ausgewählter Modelle sind keine pauschale physikalische Validierung beliebiger gekoppelter Systeme. |
| Datenbasierte Prüfung | Temperatur-/Forcing-, COVID- und Erdbebenmodelle fitten und mit Referenzmodellen vergleichen; Rolling-Origin-Auswertung, Zähldatenmodelle, Intervallbewertungen und Identifizierbarkeitsdiagnostik verwenden. | Datenfenster, Datenverfügbarkeit und Modellannahmen begrenzen die Schlussfolgerungen. Einige Versuche sind bedingte Rückrechnungen mit später beobachteten Treibern. |
| Reproduzierbare Referenzfälle | 69 Verifikationsskripte, Ergebnisdateien, analytische Beispiele und Gegenbeispiele als nachvollziehbare Prüfgrundlage nutzen. | Die Zahl zählt Skripte, keine unabhängigen Theoreme. Ein eingecheckter einheitlicher Testaufruf und eine GitHub-CI fehlen im geprüften Baum. |

Hinzu kommen spezialisierte Beispiele etwa für Reaktionsnetzwerke, Musterbildung, freie Grenzen und Perkolation. Diese verbreitern den Vergleichsraum. Eine weitere bloße Sammlung solcher Beispiele hat derzeit weniger Nutzen als ihre systematische Verbindung.

**Was die aktuellen Daten bereits aussagen**

Bei nominell 80 % erreichten die untersuchten mechanistischen Intervalle zuletzt 52,5 % empirische Abdeckung für die Energiebilanz und 26,3 % für das COVID-Renewal-Modell. Dahinter stehen 40 beziehungsweise 19 bewertete Prognosefälle; daraus ist kein präziser langfristiger Leistungswert abzuleiten. Die beobachtete Unterdeckung macht aber deutlich, dass Punktprognosegüte und Unsicherheitsgüte getrennt beurteilt werden müssen. Das COVID-Modell kann beim Intervallscore besser abschneiden und trotzdem deutlich zu selten abdecken.

Die korrigierte Profil-API trennt jetzt sauber zwischen flach im gescannten Bereich und global nachgewiesener Unbeschränktheit. Diese Unterscheidung sollte zum Muster für weitere numerische Diagnosen werden: Ergebnis, untersuchter Bereich und Beweisstatus gemeinsam ausgeben.

Das Repository untersucht inzwischen mehr als exponentielle Treiber. Für die ursprüngliche Beobachtung ist die präzisere Forschungsfrage: Welcher Anteil eines Übergangs entsteht durch den zeitlichen Treiber, welcher durch Zustand, Erholungszeit, Rückkopplung, Kopplung oder Sicherheitsgrenze? Schon ein lineares Puffermodell kann eine endliche Sicherheitsgrenze überschreiten. Umgekehrt beweist exponentielles Wachstum allein keinen Attraktorwechsel.

**Priorität 0: Den tatsächlichen Stand konsistent sichtbar machen**

Die README enthält noch Aussagen, die in Fachseiten und Code bereits eingeschränkt wurden: beispielsweise die exakte Vorhersage von Kippverhalten durch eine Kennzahl sowie rigoros bestätigte praktische Nichtidentifizierbarkeit. Auch der Bezug auf Milestones M1–M41 bleibt hinter späteren Modulen zurück. Ein referenzierter lokaler Gesamt-Testläufer ist ausdrücklich nicht eingecheckt.

Vorschlag: Eine kleine maschinenlesbare Übersicht pro Modul mit Fragestellung, Modellklasse, Voraussetzungen, Evidenzart, Prüfsammlung und bekannten Grenzen. Die README zeigt daraus nur die wichtigste aktuelle Zusammenfassung. Einen dokumentierten Gesamtaufruf samt CI ergänzen; mathematische Prüfungen, Datenprüfungen und Linkprüfung dürfen getrennte Befehle haben.

Abnahme: Frische Installation nach dokumentiertem Weg; reproduzierbarer Prüfaufruf; jede starke README-Aussage verweist auf eine aktuelle, entsprechend begrenzte Begründung. Eine stabile Veröffentlichung sollte diesen konsolidierten Umfang beschreiben.

**Priorität 1: Prognoseintervalle unter wechselnden Bedingungen**

Ansatzpunkte bestehen bereits in `validation/conformal.py` sowie den mechanistischen Rolling-Origin- und Wahrscheinlichkeitsauswertungen. Die Erweiterung wäre eine systematische Online-Kalibrierung und ihr fairer Vergleich, nicht die erstmalige Einführung konformer Vorhersage.

Zuerst eine robuste einfache Referenz: vergangene Prognosefehler fortlaufend sammeln und daraus nach Prognosehorizont getrennte Intervalle kalibrieren. Danach Adaptive Conformal Inference beziehungsweise Conformal PID Control als Kandidaten vergleichen. Das PID in dieser Literatur bezeichnet Proportional-Integral-Differential-Regelung; es ist von der Partial Information Decomposition im Repo zu unterscheiden.

Abnahme:

- Für jeden Prognoseursprung sind ausschließlich damals verfügbare Beobachtungen und Treiber zulässig.
- Kalibrierung und Bewertung verwenden getrennte, vorab festgelegte Abschnitte.
- Berichtet werden Abdeckung, Breite und Intervallscore, zusätzlich nach Horizont und ausgewählten Regimefenstern.
- Überlappende Vorhersagen werden bei Unsicherheitsangaben zur Leistungsbewertung berücksichtigt.
- Ein langfristiges Abdeckungsresultat wird nicht als garantierte bedingte Abdeckung zu jedem Zeitpunkt dargestellt.

Eine sinnvolle gemeinsame Erweiterung ist ein Feld für Beobachtungszeit und tatsächliche Verfügbarkeit. Historisch revidierte Reihen erlauben ohne archivierte Datenstände noch keine echte Echtzeit-Rückprüfung.

**Priorität 2: Zustandsdynamik und Messprozess auseinanderhalten**

Der COVID-Pilot besitzt bereits einfache Poisson-/Negativ-Binomial-Beobachtungsmodelle. Der nächste Schritt wäre ein latentes Infektionsgeschehen mit Renewal-Dynamik, ergänzt um Meldeverzug, Wochentagseffekte und Überdispersion. So lässt sich prüfen, ob Fehler aus der Dynamik oder aus dem Messprozess stammen.

Bei der Energiebilanz stehen eine konsistente Temperaturreferenz, Anfangszustände beider Schichten und gegebenenfalls eine zusätzliche beobachtbare Größe wie Wärmeinhalt im Vordergrund. Mehr Daten sind nur dann hilfreich, wenn sie tatsächlich eine bisher schlecht bestimmte Parameterkombination einschränken. Bei ETAS wäre eine prädiktive Simulation vollständiger Nachbeben-Kaskaden ein eigenständiger nächster Schritt; eine Poisson-Verteilung um eine erwartete Ereigniszahl repräsentiert die Kaskadenunsicherheit nicht automatisch.

Abnahme: Zunächst einen Pilot ausbauen, vorzugsweise COVID. Alte und neue Varianten auf denselben festgelegten Prognoseursprüngen vergleichen. Neben Mittelwertfehlern müssen Verteilungsdiagnostik und Kalibrierung einen nachvollziehbaren Nutzen zeigen.

**Priorität 3: Gemeinsame Operatorstrukturen und Gedächtnis**

Hier lässt sich die ursprüngliche Idee der präzisen Verwandtschaft besonders gut weiterentwickeln. Für lineare zeitabhängige Systeme gilt beispielsweise

\[
\dot x(t)=A(t)x(t)+B(t)u(t),\qquad
x(t)=\Phi(t,t_0)x_0+\int_{t_0}^{t}\Phi(t,s)B(s)u(s)\,ds.
\]

Die Übergangsabbildung \(\Phi\) beschreibt, wie frühere Zustände und Einwirkungen später wirksam werden. Im skalaren Erholungsmodell entsteht der Kern \(\exp[-\int_s^t r(v)\,dv]\). Dieser Zugang erlaubt zeitabhängige Erholung und macht deutlich, weshalb Verlauf und Dauer einer Belastung neben ihrem Maximum relevant sind.

Renewal-, Hawkes/ETAS- und Energiebilanzmodelle besitzen unterschiedliche, jeweils abzugrenzende Integral- oder Antwortstrukturen. Vergleichbar können beispielsweise Positivität, Kernmasse, Gedächtniszeit und bestimmte Verstärkungseigenschaften sein. Gemeinsame Operatorstruktur bedeutet dabei keine Identität ihrer physikalischen oder stochastischen Gegenstände.

An die vorhandenen kleinen Gedächtnisbeispiele kann eine allgemeiner parametrisierte lineare Projektion anschließen. Die Mori–Zwanzig-Perspektive erklärt, weshalb das Eliminieren verborgener Zustände Gedächtnis und einen vom verborgenen Anfangszustand abhängigen Restterm erzeugt. Markov-Schließung ist dann eine zu prüfende Vereinfachung.

Abnahme: Zwei- und Dreizustandsmodelle mit analytischer Referenz; exakte Projektion, gedächtnislose Näherung und endliche Gedächtnisapproximation vergleichen. Nicht nur mittleren Zustandsfehler, sondern auch Fehler bei Minimum, Grenzüberschreitung und Zeitpunkt des Ereignisses messen.

**Priorität 4: Vorübergehende Verstärkung durch nichtnormale Kopplung**

Eine besonders passende neue mathematische Richtung ist transiente Verstärkung. Für

\[
A=\begin{pmatrix}-1&k\\0&-1\end{pmatrix},
\qquad
e^{At}=e^{-t}\begin{pmatrix}1&kt\\0&1\end{pmatrix}
\]

sind beide Eigenwerte negativ. Dennoch kann bei hinreichend großem \(k\) eine Störung zunächst wachsen, bevor sie abklingt. Ein sicherheitsrelevanter Ausschlag benötigt somit weder einen instabilen Eigenwert noch einen exponentiell anwachsenden äußeren Treiber.

Das ergänzt die vorhandenen Module für Kopplung, Kontraktion und Viabilität unmittelbar. Sinnvolle Größen wären endliche Verstärkung \(\|e^{At}\|\), ihre Maximierungszeit und der Abstand zur Sicherheitsgrenze. Norm und Einheitenskalierung müssen explizit sein, weil die gemessene Verstärkung davon abhängt.

Abnahme: Das analytische Dreiecksbeispiel gegen die numerische Berechnung prüfen; danach zwei gekoppelte Puffer mit sicheren Einzelkomponenten untersuchen. Transiente Grenzverletzung, dauerhafter Attraktorwechsel und bloß großer, aber zulässiger Ausschlag bleiben verschiedene Ergebnisse.

**Priorität 5: Von Sicherheitskarten zu begrenzten Eingriffen**

Das aktuelle skalare Kontrollbarrieren-Beispiel lässt sich zu zwei gekoppelten Puffern mit beschränkten Stellgrößen und gemeinsamem Ressourcenbudget erweitern. Control-Barrier-QPs oder robuste modellprädiktive Regelung sind methodische Kandidaten.

Die Leitfrage lautet: Welcher zulässige Eingriff hält das System innerhalb der definierten Grenze, und wann existiert unter den angenommenen Grenzen kein solcher Eingriff? Modellunsicherheit kann zunächst als explizites Intervall einzelner Parameter behandelt werden.

Abnahme: Vergleich ohne Eingriff, mit fester Regel und mit optimiertem Eingriff. Ausgeben: Grenzverletzung, Eingriffskosten und Machbarkeit. Eine unlösbare Optimierungsaufgabe muss sichtbar werden; eine Modellgarantie ist von empirischer Zuverlässigkeit getrennt zu berichten.

**Empfohlene Reihenfolge in drei Arbeitspaketen**

1. **Konsolidierung:** aktuelle Fähigkeitsübersicht, README, eingecheckter Testaufruf, CI und ein durchgängiges kleines Beispiel.
2. **Empirischer Nutzen:** ein gemeinsames zeitlich sauberes Prognoseprotokoll; anschließend Online-Kalibrierung und ein verbesserter Messprozess an einem Pilot.
3. **Mathematische Verbindung:** ein gekoppeltes Zwei-Puffer-Labor, das Gedächtnis, transiente Verstärkung, Sicherheitsgrenzen und begrenzte Eingriffe zusammenführt.

Später können wenige präzise algebraische Aussagen formalisiert werden, etwa ein Kompositionsgesetz oder eine TV-Fehlerschranke. Im geprüften Repository liegen noch keine Lean-Dateien. Für den unmittelbaren Nutzen haben die drei genannten Arbeitspakete Vorrang vor einer breiten Formalisierung oder weiteren lose angeschlossenen Themen.

**Repository-Belege**

Alle Links beziehen sich auf den geprüften Commit:

- [README und Paketübersicht](https://github.com/GenesisAeon/scoped-correspondence-formalism/blob/0d4389804adf8d026923d2d9c08db5e3e902769a/README.md)
- [Korrespondenzvertrag](https://github.com/GenesisAeon/scoped-correspondence-formalism/blob/0d4389804adf8d026923d2d9c08db5e3e902769a/src/scoped_correspondence/correspondence/contract.py)
- [Probabilistische Auswertung](https://github.com/GenesisAeon/scoped-correspondence-formalism/blob/0d4389804adf8d026923d2d9c08db5e3e902769a/docs/mechanistic_probabilistic_evaluation.md)
- [Schließung und Gedächtnis](https://github.com/GenesisAeon/scoped-correspondence-formalism/blob/0d4389804adf8d026923d2d9c08db5e3e902769a/docs/closure_core.md)
- [Mehrdimensionale Sicherheitskarten](https://github.com/GenesisAeon/scoped-correspondence-formalism/blob/0d4389804adf8d026923d2d9c08db5e3e902769a/src/scoped_correspondence/viability/multidim_tipping_maps.py)
- [Bisherige Kontrollbarriere](https://github.com/GenesisAeon/scoped-correspondence-formalism/blob/0d4389804adf8d026923d2d9c08db5e3e902769a/docs/control_barrier_core.md)

**Primärliteratur für die Erweiterungen**

- Gibbs, I.; Candès, E. J. (2024): [Conformal Inference for Online Prediction with Arbitrary Distribution Shifts](https://www.jmlr.org/papers/v25/22-1218.html). Journal of Machine Learning Research 25.
- Angelopoulos, A. N.; Candès, E. J.; Tibshirani, R. J. (2023): [Conformal PID Control for Time Series Prediction](https://papers.neurips.cc/paper_files/paper/2023/hash/47f2fad8c1111d07f83c91be7870f8db-Abstract-Conference.html). NeurIPS.
- Chorin, A. J.; Hald, O. H.; Kupferman, R. (2000): [Optimal prediction and the Mori–Zwanzig representation of irreversible processes](https://math.huji.ac.il/~razk/Publications/PDF/CHK00.pdf). PNAS 97, 2968–2973.
- Trefethen, L. N.; Trefethen, A. E.; Reddy, S. C.; Driscoll, T. A. (1993): [Hydrodynamic Stability Without Eigenvalues](https://people.maths.ox.ac.uk/trefethen/ttrd.pdf). Science 261, 578–584.
- Ames, A. D.; Xu, X.; Grizzle, J. W.; Tabuada, P. (2017): [Control Barrier Function Based Quadratic Programs for Safety Critical Systems](https://arxiv.org/abs/1609.06408). IEEE Transactions on Automatic Control 62, 3861–3876.

