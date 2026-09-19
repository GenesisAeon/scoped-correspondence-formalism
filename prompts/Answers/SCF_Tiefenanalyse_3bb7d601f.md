# Tiefenanalyse: Scoped Correspondence Formalism

**Untersuchter Stand:** master, Commit 3bb7d601f3aa57ca09f72cd5c85c3d97e9ca4b19, 19. September 2026, 20:09:13 UTC. Paketversion: 0.41.0a1.

**Gesamturteil:** Das Repository enthält einen brauchbaren methodischen Kern für begrenzte Beziehungen zwischen Systembeschreibungen und inzwischen eine umfangreiche mathematische Forschungsbibliothek. Die Trennung von Beobachtung, Dynamik, Kopplung und Evidenz ist eine wesentliche Stärke. Die technische Verlässlichkeit reicht jedoch noch nicht für eine stabile Referenzbibliothek: Mehrere nachgerechnete Randfälle ergeben falsche Resultate oder zu starke Zertifikatsaussagen. Der als empirisch bezeichnete Cygnus-Pilot hat zudem eine ungeklärte, mit der zugänglichen Originalquelle nicht konsistente Datenherkunft.

Die nächsten wertvollen Schritte sind deshalb ein Datenherkunftsaudit, die Reparatur der nachgewiesenen Fehler und ein gemeinsamer Prüfvertrag für alle Bausteine. Die theoretische Breite ist bereits groß genug, um anschließend wenige vollständige Anwendungen zu untersuchen.

## 1. Untersuchungsumfang und Beleglage

Erfasst wurden der vollständige GitHub-Dateibaum mit **397 Dateien**, die letzten 30 zurückgegebenen Commits, aktuelle Issues/offene Pull Requests, Releases und Actions-Läufe. Lokal wurden **275 Textdateien anhand ihrer Git-Blob-SHA verifiziert**, darunter sämtliche aktuellen Python-Quelldateien und Prüfsuiten, die aktuelle Dokumentation sowie ausgewählte verlinkte Archiv- und Reviewtexte.

Der aktuelle Quellbestand umfasst:

| Bestandteil | Umfang |
|---|---:|
| Python unter src | 66 Dateien, 14.826 Zeilen einschließlich Dokumentation |
| Python-Prüfskripte unter verification | 50 Dateien, 14.505 Zeilen |
| Modulbeschreibungen unter docs | 45 Markdown-Dateien |
| Unterpakete | 18, davon 16 fachliche Bausteine sowie validation und legacy |
| Ausgeführte aktuelle Prüfsuiten | 50 |
| Bestehende benannte Checks | 271 |
| Davon bestanden | 269 |
| Unabhängige Audit-Prüfgruppen | 15 |
| Wheel-Build | erfolgreich |

Die Kernverträge und besonders fehleranfällige Implementierungen wurden detailliert gelesen; der übrige Bestand wurde über API-Inventar, Modulbeschreibungen, Prüfskripte und Ergebnisse erschlossen. Die Analyse behauptet keine zeilenweise Vollprüfung sämtlicher historischer Texte, keine unabhängige Reproduktion jedes zitierten Fachartikels und keinen maschinengeführten Beweis aller Resultate. Historische Binärdokumente wurden nicht vollständig eingelesen.

Das Repository wurde auf GitHub nicht verändert. Alle Befunde beziehen sich auf den festgehaltenen Commit.

## 2. Was das Projekt tatsächlich beschreibt

Die konsolidierte Leitidee ist eine **über Beschreibungsebenen untersuchbare Wiederkehr von Strukturen**: Größen, Parameter, Kontexte, Kopplungen und Zeitskalen dürfen sich ändern. Ob eine bestimmte Beziehung erhalten bleibt, wird jeweils geprüft.

Dabei ist die ausdrücklich dokumentierte Zuschreibung wichtig: Die früheren Gleichsetzungen und universellen Zahlenbehauptungen werden im Formalismus als Fehler konkreter Ausarbeitungen behandelt. Johanns ursprüngliche Leitthese wird dort nicht mit diesen Fehlern gleichgesetzt. [FORMALISM.md](https://github.com/GenesisAeon/scoped-correspondence-formalism/blob/3bb7d601f3aa57ca09f72cd5c85c3d97e9ca4b19/FORMALISM.md)

Der Kern lässt sich in sechs aufeinander aufbauenden Fragen lesen:

1. **Beobachtung:** Welche Information erfasst eine Darstellung?
2. **Dynamik:** Wie entwickelt sich der deklarierte Zustand?
3. **Kopplung:** Wie wirken Komponenten und Eingaben aufeinander?
4. **Korrespondenz:** Wie werden zwei Beschreibungen und ihre Zeiten verbunden?
5. **Geschlossenheit:** Reicht der gröbere Zustand für seine weitere Entwicklung?
6. **Aufgabentauglichkeit:** Ermöglicht diese Beschreibung die gewünschten Prognosen und Eingriffe?

Das ist als Forschungssystem sinnvoll. Es erlaubt insbesondere negative Befunde: Eine gewählte Aggregation kann ungeschlossen sein; eine Intervention kann an gemeinsamem Ressourcenbedarf scheitern; eine statistische Zerlegung kann maßabhängig sein; eine vorgeschlagene Ähnlichkeit kann außerhalb ihres Bereichs versagen.

### 2.1 Die stärkste verbindende Formel

Für autonome Modelle und einen konstanten positiven Zeitfaktor:

\[
T\circ\Phi_j^t \approx \Phi_k^{ct}\circ T,\qquad c>0.
\]

Diese Beziehung sagt mehr als „beide Kurven sehen ähnlich aus“: Zustandstransformation, Zeitabbildung und Entwicklungsoperatoren müssen zusammenpassen.

Die Aussage hängt allerdings von Zusatzangaben ab:

- Ist T invertierbar oder eine informationsverlierende Projektion?
- Welche Anfangszustände und Zeiten sind gemeint?
- Welche Norm, Einheiten und Fehlergrenzen gelten?
- Wurde T vor der Prüfung festgelegt oder an Prüfdaten angepasst?
- Ist das Ergebnis punktweise numerisch, analytisch oder empirisch belegt?

Das Repository formuliert diese Fragen in der Prosa gut. Die zentrale Python-Implementierung bildet sie erst teilweise ab. [Correspondence-Vertrag](https://github.com/GenesisAeon/scoped-correspondence-formalism/blob/3bb7d601f3aa57ca09f72cd5c85c3d97e9ca4b19/src/scoped_correspondence/correspondence/contract.py)

### 2.2 Geschlossenheit ist der entscheidende Filter

Für endliche Markov-Modelle:

\[
PC=CQ.
\]

P beschreibt die Mikrodynamik, C die Aggregation und Q die Makrodynamik. Die Gleichung verlangt, dass Entwicklung und Aggregation miteinander verträglich sind.

Der Formalismus unterscheidet zu Recht zwischen dem bloßen Konstruieren eines Kandidaten Q=ΛPC und einer tatsächlich geschlossenen Makrodynamik. Auch die Abschätzung

\[
\mathrm{TV}(pP^kC,pCQ^k)\leq \min(1,k\delta_{\mathrm{cl}})
\]

ist unter den angegebenen stochastischen Voraussetzungen nachvollziehbar: Der Ein-Schritt-Defekt akkumuliert über den Zeithorizont, während stochastische Entwicklung die Totalvariation nicht vergrößert.

Dies ist einer der überzeugendsten Teile des Projekts. Er verhindert, dass ein handlicher Makrozustand allein wegen seiner Einfachheit als eigenständiges System ausgegeben wird. [Emergenz und Geschlossenheit](https://github.com/GenesisAeon/scoped-correspondence-formalism/blob/3bb7d601f3aa57ca09f72cd5c85c3d97e9ca4b19/emergence_and_closure.md)

### 2.3 Resilienz wird sinnvoll mehrdimensional

Die Trennung von Antwortsteilheit, lokaler Erholungsrate, Beckenstruktur und kontrollierter Viabilität ist fachlich notwendig.

Für das skalare Puffermodell

\[
\dot z=-r(z-z_{\mathrm{eq}})+u-w,\quad
0\leq u\leq U,\quad 0\leq w\leq W,\quad z\geq b
\]

lautet die robuste Invarianzbedingung:

\[
r(z_{\mathrm{eq}}-b)+U-W\geq0.
\]

Zwei Systeme können dieselbe Erholungsrate r besitzen und dennoch unterschiedliche dauerhafte Belastungen verkraften. Ebenso können zwei Aufgaben einzeln erfüllbar sein, zusammen aber ihr gemeinsames Budget überschreiten. Diese Modellfälle operationalisieren den Unterschied zwischen schneller Erholung und ausreichendem Puffer sehr klar. [Viabilitätsbeispiel](https://github.com/GenesisAeon/scoped-correspondence-formalism/blob/3bb7d601f3aa57ca09f72cd5c85c3d97e9ca4b19/worked_example_viability.md)

### 2.4 Information, Emergenz und Thermodynamik bleiben unterscheidbar

Positiv sind insbesondere:

- Informationsretention I/H wird auf die passende diskrete Situation begrenzt.
- EI wird mit Interventionsverteilung und Vergleichsmaßstab versehen.
- PID und EI werden getrennt ausgewertet.
- Der TWO_BIT_COPY-Fall zeigt, dass verschiedene Redundanzmaße unterschiedliche Antworten liefern.
- Ein SVD-Wert wird nicht automatisch als kausaler Emergenzgewinn interpretiert.
- GENERIC-Strukturprüfungen werden von einem vollständigen thermodynamischen Nachweis unterschieden.
- Ein semantischer Score wird nicht als thermodynamische Entropie eingesetzt.

Diese Trennungen sind substanzieller als die bloße Umbenennung der älteren Akronyme. [Informationszerlegung](https://github.com/GenesisAeon/scoped-correspondence-formalism/blob/3bb7d601f3aa57ca09f72cd5c85c3d97e9ca4b19/docs/information_decomposition_core.md), [Thermodynamik](https://github.com/GenesisAeon/scoped-correspondence-formalism/blob/3bb7d601f3aa57ca09f72cd5c85c3d97e9ca4b19/docs/thermo_core.md)

## 3. Karte des aktuellen Softwarebestands

Die folgenden Angaben beschreiben die tatsächlich implementierte Reichweite. Ein Modulname kann einen sehr viel größeren wissenschaftlichen Gegenstand benennen als die hier realisierte Berechnung.

| Baustein | Implementierte Inhalte | Wesentliche Reichweitengrenze |
|---|---|---|
| correspondence | Zustandstransformation, Scope, Zeitfaktor, Residuen, T1–T4, Fehlerbudget | Stichproben und vorgegebene Abbildungen; keine allgemeine Beweissuche oder Bisimulationsbibliothek |
| observation | Shannon-Hartley, Retention, Informationsnutzung, Directed Information, Arimoto-Blahut | deklarierte Kanalmodelle bzw. kleine endliche Verteilungen |
| dynamics | Sigmoid, kubische Normalform, lokale Raten, Kontraktion, Landau, GSPT, Floquet, Cusp-Hysterese, Frühwarnsignale | überwiegend analytische Modellfälle; Floquet erhält die Monodromiematrix als Eingabe |
| coupling | additive Kopplung, Einfluss/Transport, GENERIC-Prüfung, Dirac-Komposition, Dissipativität, Casimir, Synchronisation, viskoses Zweizellenmodell | vorgegebene Operatoren und begrenzte lineare/endlichdimensionale Fälle |
| closure | diskrete und kontinuierliche Lumpability, Fehlerschranken, Kreisrekonstruktion, Projektionsgedächtnis, BGK-Transportkoeffizienten | keine allgemeine Rekonstruktions- oder Boltzmann-Lösung |
| viability | skalarer Puffer, gekoppelte Budgets, skalare Barrier-Bedingung, polyedrischer Tangentialkegel | kein allgemeiner Viabilitätskern; Nagumo-Auswertung an gelieferten Punkten |
| membership | binäre überlappende Zugehörigkeit, Bestandszählung, Eingriffsschnittmengen, Formal Concept Analysis | keine ausgearbeitete gewichtete Zugehörigkeitssemantik |
| identifiability | Parametersymmetrien, Jacobian-Rang, Delay-Konditionierung, EI-Vergleiche, Profile Likelihood, Fisher-Spektrum | lokale oder niedrigdimensionale Diagnostik; keine universelle Identifizierbarkeitsentscheidung |
| contextuality | endliche Kontexttabellen, Contextual Fraction, globales Modell, GF(2)-Kohomologiewitness, CSW | kleine deklarierte Szenarien; Witness und vollständige Entscheidung bleiben verschieden |
| information_decomposition | Williams-Beer, Blackwell/RB(0), bivariate BROJA-PID | zwei Quellen und kleine Alphabete; BROJA-Grenze bei 64 gemeinsamen Zustandskombinationen |
| thermo | Wärme-GENERIC, Projektion, stochastische Reversibilitätsgegenfälle, Schnakenberg, Crooks/Jarzynski | Modell- und Verteilungsprüfungen, keine empirische Thermodynamik aus beliebigen Daten |
| metarules | Regelzustand, Prioritätsauflösung, Auswirkungen verborgener Regeln auf Geschlossenheit | diskrete Beispiele und explizit bezeichnete fallengelassene Anforderungen |
| pattern_formation | Zweikomponenten-Turingkriterien, Dispersionsrelation, Schnakenberg-Modell | lineare Stabilitätsanalyse; keine räumliche PDE-Simulation |
| free_boundary | eindimensionale Stefan-Neumann-Ähnlichkeitslösung und Schmelzfront | spezieller Phasenwechselmodellfall |
| percolation | Verzweigungsprozess auf einem verwurzelten Baum, kritischer Wert, Aussterben/Überleben | kein allgemeines Gitter- oder Netzwerkperkolationspaket |
| chemical_organization | Reaktionsgeschlossenheit, stöchiometrische Selbsterhaltung, LP-Zeuge | keine vollständige Autopoiesistheorie; Reaktionsmengen und Stöchiometrie müssen zusammenpassen |
| validation | Cygnus-PA-Pilot, festgelegter Split, Persistenzvergleich; separat Split Conformal Prediction | ein domänenspezifischer Pilot; keine allgemeine validierte Datenplattform |
| legacy | Adapter für frühere Namen und Formeln | Migrationshilfe |

Quellen: [Quellbaum](https://github.com/GenesisAeon/scoped-correspondence-formalism/blob/3bb7d601f3aa57ca09f72cd5c85c3d97e9ca4b19/src/scoped_correspondence), [Moduldokumentation](https://github.com/GenesisAeon/scoped-correspondence-formalism/blob/3bb7d601f3aa57ca09f72cd5c85c3d97e9ca4b19/docs), [Erweiterungsfahrplan](https://github.com/GenesisAeon/scoped-correspondence-formalism/blob/3bb7d601f3aa57ca09f72cd5c85c3d97e9ca4b19/EXTENSIONS_ROADMAP.md).

Eine wichtige gemeinsame Grenze: Bei mehreren Erweiterungen ist „implementiert“ gleichbedeutend mit „ein spezieller literaturgestützter Rechenfall besitzt eine API und ein Verify-Skript“. Daraus folgt keine vollständige Implementierung des übergeordneten Theoriegebiets.

## 4. Reproduktion und Qualität der vorhandenen Prüfungen

### 4.1 Tatsächlich ausgeführte Ergebnisse

Umgebung: Python 3.12.14, NumPy 2.3.5, SciPy 1.17.0, Linux.

Alle 50 aktuellen Verify-Skripte wurden ausgeführt. **48 enden erfolgreich. Zwei enden mit Fehlerstatus; insgesamt bestehen 269 von 271 benannten Checks.**

Die zwei verbleibenden Fehler sind:

- p11_document_links in verify_formalism.py;
- e16_current_document_links in verify_extensions.py.

Beide beanstanden denselben URI-kodierten Link in EXTENSIONS_ROADMAP.md. Im Git-Baum existiert der Dateiname mit Leerzeichen. Die Prüfer verwenden den Link mit „%20“ unmittelbar als Dateisystempfad. Es handelt sich um einen Fehler der Linkprüfung, nicht um ein widerlegtes Modellresultat und nicht um einen fehlenden Zielnamen im Repository.

Zu Beginn fehlten im lokalen Arbeitsausschnitt einige nur verlinkte Archivtexte. Diese wurden ergänzt und die beiden betroffenen Suiten erneut ausgeführt. Der oben genannte Endstand enthält ausschließlich den verbleibenden Kodierungsfehler. Das große historische DOCX musste zur Feststellung dieses Fehlers nicht heruntergeladen werden: Die Git-Baumeinträge bestätigen die unterschiedliche Pfadschreibweise. [Prüfer 1](https://github.com/GenesisAeon/scoped-correspondence-formalism/blob/3bb7d601f3aa57ca09f72cd5c85c3d97e9ca4b19/verification/verify_formalism.py), [Prüfer 2](https://github.com/GenesisAeon/scoped-correspondence-formalism/blob/3bb7d601f3aa57ca09f72cd5c85c3d97e9ca4b19/verification/verify_extensions.py)

Ein Wheel für **scoped-correspondence 0.41.0a1** ließ sich erfolgreich bauen. Damit ist das Projekt tatsächlich paketierbare Software.

### 4.2 Was die grünen Checks belegen

Sie belegen, dass die vorhandenen Beispiele, Migrationen und Gegenbeispiele unter dieser Umgebung weitgehend reproduzierbar sind.

Die Zahl 271 darf aber nicht als Anzahl unabhängiger wissenschaftlicher Bestätigungen gelesen werden:

- Manche Checks vergleichen eine neue API mit älteren gespeicherten Beispielwerten.
- Mehrere Checks prüfen Warntexte, Quellenzeichenketten oder Namensregeln.
- Ein Check kann viele Zahlen enthalten; mehrere Checks können dieselbe zugrunde liegende Rechnung wiederverwenden.
- Synthetische Fälle testen die Implementierung eines vorgegebenen Modells.
- Ein Datenpilot kann rechnerisch bestehen, obwohl seine Quellen noch nicht ausreichend belegt sind.

Diese Prüfungen sind als Regression und Dokumentation nützlich. Sie ersetzen keine unabhängige Datenherkunftsprüfung und decken die unten genannten Randfälle nicht ab.

### 4.3 Entwicklungsinfrastruktur

Am festgehaltenen Stand wurden keine GitHub-Actions-Läufe und keine Releases zurückgegeben; der Dateibaum enthält keine Workflow-Konfiguration. Offene Pull Requests wurden nicht zurückgegeben. Die Paketabhängigkeiten sind in pyproject.toml lediglich als NumPy und SciPy angegeben, ohne festgeschriebene reproduzierbare Umgebung.

Für eine stabile Referenzversion fehlen insbesondere ein zentraler Prüfaufruf, eine automatische CI-Ausführung, eine geklärte API-Stabilität und die geplanten formalen Beweishaken. Die uneinheitlichen JSON-Schemata der 50 Prüfsuiten erschweren außerdem eine gemeinsame Auswertung. [Paketkonfiguration](https://github.com/GenesisAeon/scoped-correspondence-formalism/blob/3bb7d601f3aa57ca09f72cd5c85c3d97e9ca4b19/pyproject.toml), [Architekturfahrplan](https://github.com/GenesisAeon/scoped-correspondence-formalism/blob/3bb7d601f3aa57ca09f72cd5c85c3d97e9ca4b19/ARCHITECTURE_ROADMAP.md)

## 5. Priorisierte Befunde

Die Prioritäten sind Audit-Empfehlungen: **P0** blockiert den betreffenden wissenschaftlichen Status; **P1** bezeichnet nachgewiesene Ergebnis- oder Vertragsfehler; **P2** betrifft Reichweite, Dokumentation und Konsolidierung.

### A01 — P0: Der empirische Status des Cygnus-Piloten ist nicht gesichert

Die YAML-Datei bezeichnet 18 Werte von 2006,2 bis 2023,8 als literaturkompilierte VLBI-Beobachtungen. Es fehlen aber pro Zeile Tabellen-/Datensatzkennung, Messunsicherheit, Originaldatum und dokumentierte Transformation.

Der zugängliche Prabu-Preprint nennt Beobachtungen aus 1998, 2001, 2009/2010 und 2016; neun Aufnahmen untersuchen eine einzelne Umlaufperiode 2016. Er beschreibt eine stabile mittlere Positionsrichtung mit orbitaler Variation. Seine Beobachtungstabelle entspricht somit nicht der jährlichen Repository-Reihe. [Prabu et al., Originalarbeit und Extended Data Table 1](https://arxiv.org/html/2512.09645v1)

Unabhängig davon enthält die Repository-Datei interne Kalenderabweichungen: Der letzte Datensatz trägt Jahr 2023,8 und MJD 60322. Dieser MJD bezeichnet den **13. Januar 2024**. Mehrere weitere MJD-/Jahrespaare stimmen ebenfalls nicht mit einer präzisen Dezimaljahrinterpretation überein.

**Bewertung:** Aus diesen Befunden folgt nicht sicher, wie die Zahlen entstanden sind. Wohl aber ist „erster echter Datenpilot“ derzeit ein nicht ausreichend belegter Status. Die Reihe sollte bis zu einer nachvollziehbaren zeilenweisen Herkunftsklärung als unbestätigter Datensatz behandelt werden.

Die Wiederholung von vier Literaturangaben und der Hinweis „1:1 aus einem anderen Repository übernommen“ sichern die Herkunft einzelner Messwerte nicht.

**Reparaturziel:** Für jede Zeile Quelle, Tabelle/Zeile, Datum, Einheit, Winkelkonvention und Unsicherheit hinterlegen; Extraktionsweg dokumentieren. Falls das nicht möglich ist, den Pilot explizit als Demonstration mit unbestätigten oder synthetischen Daten einstufen. [Datendatei](https://github.com/GenesisAeon/scoped-correspondence-formalism/blob/3bb7d601f3aa57ca09f72cd5c85c3d97e9ca4b19/data/cygnus_x1_radio_epochs.yaml), [Pilotbeschreibung](https://github.com/GenesisAeon/scoped-correspondence-formalism/blob/3bb7d601f3aa57ca09f72cd5c85c3d97e9ca4b19/docs/cygnus_pilot.md)

### A02 — P1: Zustandsabhängige Zeit wird wie ein konstanter Zeitfaktor verwendet

TimeMap erlaubt ausdrücklich a(z,t)=dτ/dt. conjugacy_residual berechnet die Zielzeit dennoch als a(z₀,t)·t.

Für eine zustandsabhängige Geschwindigkeit ist stattdessen entlang der Quelltrajektorie zu integrieren:

\[
\tau(t)=\int_0^t a(\Phi_j^s(z_0),s)\,ds.
\]

Eigenes exaktes Gegenbeispiel:

\[
\dot x=x,\quad \frac{dy}{d\tau}=1,\quad T(x)=x,\quad a(x)=x,\quad x_0=1.
\]

Dann gilt x(t)=exp(t), τ(t)=exp(t)−1 und y(τ(t))=exp(t). Die Korrespondenz ist exakt. Bei t=1 meldet der Code trotzdem ein Residuum **0,7182818284590451**.

**Reparaturziel:** Den konstanten Flussvergleich auf konstante positive Zeitfaktoren begrenzen oder eine explizite akkumulierte Zeitabbildung einführen. Null, negative und nichtendliche Zeitfaktoren abweisen. T2s lokale Kettenregel und globale Zeitabbildung als unterschiedliche Operationen behandeln. [contract.py](https://github.com/GenesisAeon/scoped-correspondence-formalism/blob/3bb7d601f3aa57ca09f72cd5c85c3d97e9ca4b19/src/scoped_correspondence/correspondence/contract.py)

### A03 — P1: Ein NaN kann ein positives Approximationszertifikat erzeugen

Bei Residuen in der Reihenfolge [0, NaN] liefert Python max einen Wert von 0. Der zugrunde liegende CorrespondenceReport meldet zwar ok=False, aber verify_approximate_simulation ignoriert dieses Ergebnis und prüft nur max_residual≤epsilon.

Reproduziert mit epsilon=0:

| Größe | Ergebnis |
|---|---|
| Einzelresiduen | 0 und NaN |
| maximal berichtetes Residuum | 0 |
| CorrespondenceReport.ok | False |
| ApproximationCertificate.ok | **True** |

Auch eine leere Prüfpunktmenge ergibt derzeit ein positives Korrespondenzergebnis.

**Reparaturziel:** Endlichkeit und Form aller Zustände, Flussergebnisse und Residuen prüfen; leere Evidenz abweisen; ungültige Auswertung als eigenen Fehlerstatus führen. Ein numerisch gescheiterter Vergleich darf kein Zertifikat ausstellen. [approximation.py](https://github.com/GenesisAeon/scoped-correspondence-formalism/blob/3bb7d601f3aa57ca09f72cd5c85c3d97e9ca4b19/src/scoped_correspondence/correspondence/approximation.py), [contract.py](https://github.com/GenesisAeon/scoped-correspondence-formalism/blob/3bb7d601f3aa57ca09f72cd5c85c3d97e9ca4b19/src/scoped_correspondence/correspondence/contract.py)

### A04 — P1: Die kubische Fixpunktsuche verliert nahe der Bifurkation Lösungen

Für a=10⁻⁵ und b=0 besitzt x³−ax=0 exakt drei verschiedene reelle Nullstellen:

\[
x\in\{-0{,}0031622776601683794,\ 0,\ +0{,}0031622776601683794\}.
\]

fixed_points gibt **[−0.0, 0.0]** zurück. Ursache ist die absolute Diskriminantenschwelle 10⁻¹²: Der positive Wert 4a³=4·10⁻¹⁵ wird als degenerierter Fall behandelt.

Das ist besonders relevant, weil das Modul gerade Schwellen und den Verlust von Stabilität untersucht.

**Reparaturziel:** Skalenbewusste Behandlung der Koeffizienten und Diskriminante, Residuenkontrolle der Wurzeln, sichere Entdoppelung. Die symmetrische Familie b=0 bietet einen analytisch einfachen Regressionstest über mehrere Größenordnungen. [dynamics/core.py](https://github.com/GenesisAeon/scoped-correspondence-formalism/blob/3bb7d601f3aa57ca09f72cd5c85c3d97e9ca4b19/src/scoped_correspondence/dynamics/core.py)

### A05 — P1: Perkolation behandelt einen Randfall falsch und verschweigt fehlende Konvergenz

**Fall 1:** m=1, p=1 ist eine unendliche Kette mit sicher offenen Kanten. Aussterben hat Wahrscheinlichkeit 0, Überleben Wahrscheinlichkeit 1. Der Code gibt das Gegenteil aus: Q=1 und θ=0.

**Fall 2:** Bei m=2 und p=0,5001 ergibt sich analytisch

\[
Q_*=\left(\frac{1-p}{p}\right)^2
=0{,}9992003199040257.
\]

Nach 1.000 Iterationen wird jedoch Q=0,9956266708148596 zurückgegeben. Das verbleibende Residuum liegt bei ungefähr 3,91·10⁻⁶, obwohl 10⁻¹² angefordert wurde. Die Komfortfunktion percolation_probability verwirft Iterationszahl und Residuum.

| Überlebenswahrscheinlichkeit | Wert |
|---|---:|
| Exakt | 0,0007996800959743 |
| Implementierung | 0,0043733291851404 |

Zudem erlaubt die API nichtganzzahlige Verzweigungsfaktoren, obwohl die verwendete Potenz als Binomial-Nachkommen-PGF einen ganzzahligen maximalen Nachwuchs voraussetzt.

**Reparaturziel:** Degenerierten deterministischen Fall separat behandeln; ganzzahligen Verzweigungsfaktor verlangen; Konvergenzstatus bis in die Komfort-API erhalten; nahe dem kritischen Punkt geeignete Nullstellensuche oder kontrollierte Fehlergrenzen einsetzen. [percolation/core.py](https://github.com/GenesisAeon/scoped-correspondence-formalism/blob/3bb7d601f3aa57ca09f72cd5c85c3d97e9ca4b19/src/scoped_correspondence/percolation/core.py)

### A06 — P1: Die Viabilitätsprüfungen erzwingen ihre eigenen Voraussetzungen nicht vollständig

**Nagumo:** Für K=[0,1], z=2 und f(z)=1 meldet tangent_cone_condition ok=True. Keine Randbedingung ist dort aktiv; der Code prüft aber nicht, dass der Punkt überhaupt in K liegt.

**Control Barrier:** Das Modul soll ausschließlich h(x)=x unterstützen. Es prüft dafür nur h(x)=x am einzelnen Auswertungspunkt. Die andere Funktion h(x)=1−x erfüllt diese Gleichheit bei x=0,5. Bei u=1 meldet das Zertifikat safe=True und einen positiven Randwert; korrekt wäre

\[
h'(x)u+h(x)=-1+0{,}5=-0{,}5.
\]

Diese Funktion liegt außerhalb des deklarierten Umfangs, wird aber entgegen der angekündigten Ablehnung akzeptiert.

Darüber hinaus ist die punktweise CBF-Bedingung kein Nachweis für das Festhalten eines konstanten Eingriffs: Bei x₀=1 und u=−0,5 besteht die Bedingung zunächst, während x(3)=−0,5 außerhalb des sicheren Bereichs liegt. Eine geeignete Regel muss die Bedingung entlang der Entwicklung erhalten.

**Reparaturziel:** Zustandszulässigkeit prüfen; unterstützte Barrieren konstruktiv typisieren; momentane Eingriffsbedingung von einer nachgewiesenen Invarianz unter einer Regel trennen. [nagumo.py](https://github.com/GenesisAeon/scoped-correspondence-formalism/blob/3bb7d601f3aa57ca09f72cd5c85c3d97e9ca4b19/src/scoped_correspondence/viability/nagumo.py), [control_barrier.py](https://github.com/GenesisAeon/scoped-correspondence-formalism/blob/3bb7d601f3aa57ca09f72cd5c85c3d97e9ca4b19/src/scoped_correspondence/viability/control_barrier.py)

### A07 — P1: Ein endlicher flacher Scan wird als unbeschränktes Likelihood-Intervall ausgegeben

Für χ²(θ)=θ² ist der Parameter identifizierbar. Bei Schwelle Δ=1 ist das globale Likelihood-Niveauintervall exakt [−1,1].

Auf dem kleinen Scan {−0,001;0;0,001} klassifiziert der Code das Profil wegen seiner geringen Varianz als „flat“ und meldet unbounded=True.

Ein endlicher Scan kann lediglich zeigen, dass eine Grenze im gescannten Bereich nicht aufgelöst wurde. Er kann die Unbeschränktheit außerhalb des Bereichs nicht beweisen. Auch „nicht flach“ ist für sich genommen keine vollständige Identifizierbarkeitsdiagnose.

**Reparaturziel:** „Im Scan nicht aufgelöst“, „Grenze außerhalb des Scans“ und „analytisch unbeschränkt“ getrennt ausgeben; Skalen- und Rasterabhängigkeit berichten. [profile_likelihood.py](https://github.com/GenesisAeon/scoped-correspondence-formalism/blob/3bb7d601f3aa57ca09f72cd5c85c3d97e9ca4b19/src/scoped_correspondence/identifiability/profile_likelihood.py)

### A08 — P2: Floquet-Spektrum und tatsächliche Orbitstabilität werden nicht vollständig unterschieden

Die Eigenwertberechnung reproduziert die vorgesehenen Beispiele. Die Klassifikation aus den Beträgen allein ist jedoch für die Bezeichnung „orbital stability“ zu schwach.

Für

\[
M=\begin{pmatrix}1&1\\0&1\end{pmatrix}
\]

sind beide Multiplikatoren 1. Die API nennt dies neutral. Es gilt aber

\[
M^n=\begin{pmatrix}1&n\\0&1\end{pmatrix},
\]

also unbeschränktes lineares Wachstum in einer Richtung.

Außerdem wird das Multiplikatorenpaar (1; 0,5) ebenfalls als neutral bezeichnet, obwohl bei einem autonomen periodischen Orbit die bekannte Phasenrichtung den trivialen Multiplikator 1 besitzt und die transversale Richtung stabil sein kann.

**Reparaturziel:** Spektralklassifikation so benennen; bei Einheitsmultiplikatoren eine offene Bewertung ausgeben oder Semisimplizität und Phasenrichtung zusätzlich erfassen. Eine rein spektrale Grenzlage darf nicht als bereits bestimmte Langzeitstabilität erscheinen. [floquet.py](https://github.com/GenesisAeon/scoped-correspondence-formalism/blob/3bb7d601f3aa57ca09f72cd5c85c3d97e9ca4b19/src/scoped_correspondence/dynamics/floquet.py)

### A09 — P1: Der allgemeine Split-Vertrag akzeptiert überlappende Daten

Der kanonische Cygnus-Ablauf verwendet tatsächlich getrennte feste Indizes. In diesem Lauf wurde kein Holdout in den Fit gegeben.

Der öffentliche DatasetManifest kann jedoch mit identischen Kalibrierungs- und Holdoutindizes erzeugt werden. split_epochs akzeptiert ihn; im Gegenbeispiel sind alle neun Datensätze identisch.

Der bisherige Guard prüft nur, ob die übergebenen Indizes dem Manifest entsprechen. Er prüft nicht die Gültigkeit des Manifests selbst.

**Reparaturziel:** Disjunktheit, Eindeutigkeit, gültige Indexbereiche und Datenidentität im Manifest erzwingen. Ein nachträglich erzeugtes oder geändertes Manifest ist außerdem kein Nachweis einer vorherigen Festlegung. [validation/core.py](https://github.com/GenesisAeon/scoped-correspondence-formalism/blob/3bb7d601f3aa57ca09f72cd5c85c3d97e9ca4b19/src/scoped_correspondence/validation/core.py)

### A10 — P2: Einige vermeintliche Grenzen sind nur durch Prosa abgesichert

Weitere reproduzierte Beispiele:

| Funktion | Eingabe | Ergebnis | Problem |
|---|---|---|---|
| retention | I=NaN, H=1 | 1 | ungültige Information wird zu perfekter Retention |
| realized_rate | Rate=2, Kapazität=1 | 2 | Verletzung des beschriebenen Nutzungsbereichs bleibt unmarkiert |
| is_exact_closure | P=2I, C=I, Q=2I | True | Matrixidentität besteht, obwohl P und Q keine stochastischen Kerne sind |

Daneben gibt slow_manifold_distance_bound im GSPT-Modul lediglich abs(epsilon) zurück. Die Dokumentation bezeichnet dies ausdrücklich als Größenordnungsschätzung. Ohne System, kompakte Teilmenge, Konstanten und zulässigen ε-Bereich entsteht daraus keine numerische Abstandsschranke. Der Funktionsname ist deshalb stärker als die vorhandene Berechnung.

Ebenso prüft verify_conjugacy kein Homeomorphismusmerkmal von T. Ein konstantes T auf einen Ziel-Fixpunkt kann korrekt ein verschwindendes Residuum erzeugen, ohne eine Konjugation zu sein. Das ist eine echte Unterscheidung der Beziehungstypen, keine Frage der Rechengenauigkeit.

**Reparaturziel:** Deklarierte Voraussetzungen, tatsächlich geprüfte Voraussetzungen und Reichweite des Ergebnisses maschinenlesbar trennen. [observation/core.py](https://github.com/GenesisAeon/scoped-correspondence-formalism/blob/3bb7d601f3aa57ca09f72cd5c85c3d97e9ca4b19/src/scoped_correspondence/observation/core.py), [closure/core.py](https://github.com/GenesisAeon/scoped-correspondence-formalism/blob/3bb7d601f3aa57ca09f72cd5c85c3d97e9ca4b19/src/scoped_correspondence/closure/core.py), [gspt.py](https://github.com/GenesisAeon/scoped-correspondence-formalism/blob/3bb7d601f3aa57ca09f72cd5c85c3d97e9ca4b19/src/scoped_correspondence/dynamics/gspt.py)

### A11 — P2: Die Einstiegstexte widersprechen dem aktuellen Softwarestand

Die README führt weiterhin primär Revision 3.2 und die älteren eigenständigen Verify-Skripte vor. ARCHITECTURE_ROADMAP.md behauptet am Anfang noch, es gebe weder installierbares Paket noch src-Baum und Teil 2 sei nicht begonnen. Weiter unten werden dieselben Meilensteine als erledigt aufgeführt.

In EXTENSIONS_ROADMAP.md steht GSPT zunächst auf „offen“, später als M33 auf „gemergt“. Viele Modultexte tragen weiterhin „review package only“, während der Ausbau als gemergt dokumentiert ist.

Diese Widersprüche erschweren fachliche Bewertung und Wiederverwendung. Sie erklären auch, warum eine Analyse allein anhand der README einen erheblich veralteten Eindruck erhält.

**Reparaturziel:** Einen aktuellen Einstieg mit Installation, drei kleinen End-to-End-Beispielen, Modullandkarte, Versionsstatus und tatsächlichen Prüfergebnissen erstellen; historische Pläne ausdrücklich historisieren. [README](https://github.com/GenesisAeon/scoped-correspondence-formalism/blob/3bb7d601f3aa57ca09f72cd5c85c3d97e9ca4b19/README.md), [Architekturfahrplan](https://github.com/GenesisAeon/scoped-correspondence-formalism/blob/3bb7d601f3aa57ca09f72cd5c85c3d97e9ca4b19/ARCHITECTURE_ROADMAP.md), [Erweiterungsfahrplan](https://github.com/GenesisAeon/scoped-correspondence-formalism/blob/3bb7d601f3aa57ca09f72cd5c85c3d97e9ca4b19/EXTENSIONS_ROADMAP.md)

## 6. Was der Cygnus-Fit rechnerisch zeigt

Die veröffentlichten Werte sind exakt reproduzierbar:

| Größe | Reproduzierter Wert |
|---|---:|
| RMSE Relaxationsmodell, Holdout | 3,0710033394° |
| RMSE Persistenz, Holdout | 3,7045017659° |
| Angepasstes Gleichgewicht | 8.416,3034303° |
| Angepasste Rate r | 0,00015 pro Jahr |
| Daraus τ=1/r | 6.666,6666667 Jahre |

Die enorme Gleichgewichtslage und winzige Rate machen das Modell im beobachteten Bereich nahezu linear:

\[
PA(t)\approx PA_0 + r(PA_{\mathrm{eq}}-PA_0)(t-t_0).
\]

Als zusätzliche **explorative Audit-Diagnose** wurde bei unverändertem Split eine am ersten Kalibrierungswert verankerte Gerade angepasst. Ihr Holdout-RMSE ist **3,0792926034°**. Das liegt nur etwa 0,0083° vom Relaxationsmodell entfernt. Eine freie OLS-Gerade ergibt 3,7688628778°.

Daraus folgt:

- Der dokumentierte Vorteil gegenüber Persistenz ist rechnerisch real für diese Datei.
- Die Daten tragen im bisherigen Vergleich kaum zusätzliche Evidenz für den Relaxationsmechanismus gegenüber dessen linearem Grenzverhalten.
- Die geschätzte Erholungszeit besitzt auf dieser Grundlage keine belastbare physikalische Interpretation.
- Die nachträglich ergänzten Vergleichsmodelle sind keine neue unabhängige Validierung.
- Der Pilot schätzt eine Zeitreihe in einer Domäne; er prüft keinen Transfer einer vorab festgelegten Korrespondenz zwischen zwei Beschreibungsebenen.

Die schwache Identifikation ist in der vorhandenen Dokumentation bereits teilweise offen benannt. Der neue Audit-Befund ergänzt die fast gleichwertige lineare Beschreibung und den ungeklärten Datenstatus. [Pilotimplementierung](https://github.com/GenesisAeon/scoped-correspondence-formalism/blob/3bb7d601f3aa57ca09f72cd5c85c3d97e9ca4b19/src/scoped_correspondence/validation/core.py), [Pilotbericht](https://github.com/GenesisAeon/scoped-correspondence-formalism/blob/3bb7d601f3aa57ca09f72cd5c85c3d97e9ca4b19/verification/verify_cygnus_pilot_results.json)

## 7. Übergreifende wissenschaftliche Einordnung

### 7.1 Wo der eigenständige Wert liegen kann

Die einzelnen mathematischen Werkzeuge stammen überwiegend aus etablierten Gebieten. Ihre Implementierung ist nicht automatisch ein neuer Satz.

Der mögliche eigene Beitrag liegt in einem konsequenten gemeinsamen Umgang mit:

- Geltungsbereichen;
- Transformationen und Komposition;
- Informationsverlust und Gedächtnis;
- Eingriffsübertragung und Ressourcenbedingungen;
- verschiedenen Evidenzarten;
- expliziten Gegenbeispielen.

Daraus kann eine nützliche Prüfsprache für Modelle entstehen. Wissenschaftlich sichtbar würde dieser Beitrag durch Anwendungen, bei denen sie eine falsche Übertragung erkennt, einen bislang übersehenen Fehler begrenzt oder eine unabhängig geprüfte Vorhersage verbessert.

Eine Sammlung von 16 Modulen allein belegt noch keinen durchgängigen Formalismus. Dafür müssen die Schnittstellen an vollständigen Modellketten funktionieren.

### 7.2 Lokale Ähnlichkeit benötigt einen Vergleichsmaßstab

Viele stabile Systeme zeigen nach Linearisierung exponentielle Erholung. Wenn sowohl T als auch Zeitfaktor und Normierung frei angepasst werden, kann eine Ähnlichkeit sehr leicht entstehen.

Eine anspruchsvollere Korrespondenzfrage lautet deshalb: Welche eingeschränkte, vorher festgelegte Abbildung überträgt welche Struktur über welchen Bereich, und woran könnte sie scheitern?

Geeignete Prüfgegenstände wären beispielsweise eine erhaltene Bilanz, ein übertragbares Eingriffsgesetz, eine explizite Makrodynamik oder eine belastbare Fehlergrenze. Ein ähnlicher Kurvenverlauf ist dafür ein Anfangsbefund.

### 7.3 Die Abgrenzung kann stellenweise zu weit gehen

Die Vorsicht gegenüber früheren Identitätsbehauptungen ist nachvollziehbar. Formulierungen wie „NO mathematical kinship“ oder „no shared mathematics“ gehen aber über die notwendige Aussage hinaus.

Unterschiedliche Gegenstände können auf einer präzise definierten Abstraktionsebene Gemeinsamkeiten besitzen. Ein konkretes Beispiel: Das wiederholte Ergänzen aller aus einer Artenmenge erzeugbaren Reaktionsprodukte definiert auf einem endlichen Universum einen extensiven, monotonen, idempotenten Mengenoperator. Auch die doppelte Ableitung der Formal Concept Analysis besitzt diese allgemeinen Operator-Eigenschaften.

Das identifiziert weder chemische Selbsterhaltung mit FCA noch Markov-Lumpability mit einem Konzeptverband. Es zeigt lediglich, dass eine wohldefinierte mathematische Brücke möglich ist. Gerade solche begrenzten strukturellen Beziehungen passen zur ursprünglichen Leitidee.

**Empfehlung:** „Keine Identität voraussetzen“ als Regel erhalten. „Jede gemeinsame Struktur ausschließen“ vermeiden. Eine mögliche Brücke erhält ihren eigenen Vertrag und Nachweis.

### 7.4 Mehrere KI-Reviews sind hilfreich, aber keine externe Validierung

Die Review-Historie dokumentiert Quellenprüfungen, Gegenrechnungen und Korrekturen. Das ist wertvoll. Übereinstimmende Vorschläge oder gleiche Zahlen mehrerer Modelle garantieren jedoch keine voneinander unabhängige Evidenz.

Die jetzt gefundenen Fehler zeigen den Bedarf an andersartigen Prüfungen: adversariale Randfälle, selbst hergeleitete Gegenbeispiele, Datenquellen auf Zeilenebene und externe Fachprüfung. Ein DOI-String im Test kann die Existenz einer Quellenangabe sichern; den richtigen Transfer eines Satzes in den Code muss eine gesonderte Prüfung leisten.

## 8. Empfohlene Reihenfolge

| Priorität | Arbeitspaket | Konkretes Abschlusskriterium |
|---|---|---|
| 1 | Cygnus-Datenherkunft klären | Jede verwendete Zeile auf Originaldaten zurückführbar oder Pilotstatus ehrlich korrigiert |
| 2 | NaN-/Leermengen-Zertifikate und Zeitabbildung reparieren | A02/A03 scheitern kontrolliert oder liefern analytisch korrekte Resultate |
| 3 | Kubische Wurzeln und Perkolation härten | Kleine Skalen, kritische Nähe und deterministische Randfälle korrekt; Konvergenz sichtbar |
| 4 | Viabilität und Profilberichte präzisieren | Zulässigkeit geprüft; punktweise Befunde und globale Aussagen getrennt |
| 5 | Gemeinsame Report- und Scope-Struktur | geprüfte/angenommene Voraussetzungen, Evidenzart, Norm, Bereich, Konvergenz und Provenienz in jedem Bericht |
| 6 | Einstieg und CI konsolidieren | Aktuelle README; ein reproduzierbarer Prüfaufruf; Linkprüfung dekodiert URI-Pfade |
| 7 | Eine vollständige Modellkette demonstrieren | Beobachtung → Aggregation → Geschlossenheit → Eingriff → Fehler-/Sicherheitsbewertung |
| 8 | Eine unabhängige empirische Korrespondenzprüfung | Transformation und Vergleichsmodelle vorab festgelegt; bestätigte Daten und unangetasteter Holdout |

Für die erste integrierte Modellkette eignen sich die bereits gerechneten zwei gekoppelten Puffer oder das Wärmebeispiel besonders gut. Beide besitzen transparente Zustände, Bilanzen und analytische Vergleichsmöglichkeiten. Der Pufferfall erlaubt zusätzlich einen anschaulichen negativen Befund: Eine korrekte Summenprognose kann lokale Gefährdung verbergen.

Eine gemeinsame Berichtsstruktur sollte mindestens angeben:

| Feld | Zweck |
|---|---|
| Beziehungstyp | Konjugation, Projektion, punktweiser Vergleich, Bilanzbeziehung usw. |
| Evidenzart | analytische Ableitung, numerische Probe, Gegenbeispiel, Kalibrierung, unabhängiger Holdout |
| Geltungsbereich | Zustände, Parameter, Kontexte und Zeithorizont |
| Voraussetzungen | getrennt nach angenommen und tatsächlich geprüft |
| Numerischer Status | Endlichkeit, Konvergenz, Toleranzen, Konditionierung |
| Aussageweite | Einzelpunkt, endliches Raster, gesamte Menge oder asymptotischer Bereich |
| Provenienz | Quellcommit, Datenhash, Originaldatenquelle und Verarbeitung |
| Offene Punkte | explizit unbekannte oder nicht geprüfte Eigenschaften |

Die mathematische Sprache im Formalismus bietet hierfür bereits eine gute Grundlage. Die Implementierung sollte diese Präzision verbindlich tragen.

## 9. Reproduzierbare Audit-Belege

Das begleitende Archiv enthält:

- independent_probes.py und independent_probe_results.json;
- run_verification.py und suite_summary.json;
- aktuelle JSON-Ausgaben der 50 Prüfsuiten;
- die zugehörigen Ausführungslogs;
- Repository-Bauminventar und verifizierten Commit;
- einen Nachweis der 275 übereinstimmenden Git-Blob-Hashes;
- Hinweise zur Reproduktion.

Die unabhängigen Proben verändern keine Repository-Datei. Ausführung aus einer Umgebung mit NumPy und SciPy:

    python independent_probes.py /pfad/zum/scoped-correspondence-formalism

Der Audit-Runner erwartet eine separate Kopie des Repositorys unter audit/run_snapshot. So bleiben die eingecheckten Referenzergebnisse beim erneuten Ausführen erhalten.

Die tragfähigste Leistung des Projekts ist seine explizite Behandlung begrenzter Korrespondenzen, einschließlich möglicher Fehler und Gegenbefunde. Damit daraus eine verlässliche Forschungsinfrastruktur wird, müssen Datennachweis, numerische Randfälle und die Reichweite von Zertifikaten jetzt dieselbe Sorgfalt erhalten wie die mathematische Prosa.
