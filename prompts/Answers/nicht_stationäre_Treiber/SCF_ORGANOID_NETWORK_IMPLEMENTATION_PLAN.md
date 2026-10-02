# SCF: Adaptive modulare Netzwerke und beobachtbare Information

**Eigenständiger Implementierungsplan für Claude-Code — ON0–ON7**  
Stand: 01.10.2026 · Auftraggeber: Johann Benjamin Römer  
Status: zur Implementierung vorbereitet; Produktionscode und reale Reanalyse stehen aus.  
Dokumentation: CC BY 4.0. Der unabhängige Kontrollcode im Begleitpaket ist GPL-3.0-or-later.

## 1. Auftrag und Ergebnisziel

Implementiere einen kleinen SCF-Piloten, der untersucht, **wann Kopplung und Anpassung eines modularen Netzwerks die Unterscheidbarkeit seiner Eingänge verbessern und welchen Anteil der Beobachtungszugang daran hat**.

Das konkrete biologische Motiv ist die Studie zu wiederholt stimulierten Organoidnetzwerken von Chow et al. Der erste Produktionsumfang ist ein mathematischer und synthetischer Prüfrahmen. Er muss auch Fälle korrekt behandeln, in denen zusätzliche Module keinen Vorteil bringen, ein Decoder besser wird, obwohl die Information gleich bleibt, oder gerichtete statistische Abhängigkeit ohne direkte kausale Verbindung entsteht.

Vier Ebenen bleiben getrennt:

1. **System:** Zustandsdynamik und anpassbare Kopplungen.
2. **Beobachtung:** ausgewählte Orte, Zeitfenster, Aggregation und Messrauschen.
3. **Auslesen:** Decoder, Training und Testprotokoll.
4. **Schluss:** Aussage über genau den geprüften Scope und seine Evidenz.

Erwarteter Gewinn für SCF: ein gemeinsamer Pilot für Beobachtungsfasern, Informationsmaße, begrenzte Plastizität, Gerichtetheit und statistische Vergleiche. Es wird keine allgemeine Schwelle „ab drei Modulen entsteht Lernen“ vorausgesetzt. Auch wird kein universeller Intelligenzscore eingeführt.

**Verbindlich:** ON0–ON7 einschließlich synthetischem Kern, Gegenkontrollen, Dokumentation und CLI. **Optional:** eine Reanalyse echter Organoiddaten in ON6b, zusätzliche Decoder und größere Netzwerkmodelle. Fehlende Rohdaten dürfen den mathematischen Kern nicht blockieren.

## 2. Quellenlage und wissenschaftliche Einordnung

### 2.1 Ausgangsstudie: gesicherter Befund und Reichweite

Chow et al., *Modular organoid networks acquire source-signal discrimination through input-driven network refinement*, Communications Biology, veröffentlicht am 28.09.2026, [DOI 10.1038/s42003-026-11036-8](https://doi.org/10.1038/s42003-026-11036-8). Die begutachtete frühe Verlagsfassung samt Methoden wurde geprüft.

Die getesteten Trios zeigten nach wiederholter Stimulation konsistent verbesserte Dekodierbarkeit. Beim zentralen Vergleich waren es fünf Solo-, vier Duo- und fünf Trio-Präparate. Beim Duo lagen beide Eingänge im selben Organoid; beim Trio in getrennten Eingangsorganoiden. Die Konfigurationen verändern deshalb mehr als die Modulzahl. Anfangs wurden Eingangspaare mit ungefähr 50 % SVM-Leistung gewählt. Die ersten 80 von 100 Wiederholungen je Eingang dienten dem Decodertraining, die letzten 20 der Bewertung. Die Decoder wurden für die jeweiligen Auswertungen separat trainiert, mit festen Hyperparametern. Funktionelle Konnektivität wurde unter anderem aus Kofeuer-Beziehungen geschätzt. Diagrammquelldaten sind verlinkt; ein vollständiger Rohsignalbestand wurde hier nicht geprüft.

Daraus folgen die im Plan gesetzten Grenzen: keine universelle Drei-Modul-Schwelle; keine automatische Gleichsetzung von Korrelation mit Synapsen; biologische Replikation und Reizwiederholung auseinanderhalten. Die folgenden Modelle sind eigene methodische Vorschläge, keine Rekonstruktion der biologischen Mechanismen.

### 2.2 Quellenregister für die Umsetzung

| ID | Quelle | Geprüfter Status | Rolle im Plan |
|---|---|---|---|
| ON-S1 | [Chow et al. 2026](https://www.nature.com/articles/s42003-026-11036-8), [Verlags-PDF](https://www.nature.com/articles/s42003-026-11036-8_reference.pdf) | Haupttext und Methoden gelesen; Supplementdateien nicht vollständig auditiert | Biologisches Motiv; Scope und Datenanforderungen |
| ON-S2 | [Duenki & Ikeuchi 2026](https://www.nature.com/articles/s42003-026-09589-9), DOI 10.1038/s42003-026-09589-9 | Primärtext geprüft, veröffentlicht 22.01.2026 | Ergänzender Vergleich mit drei- und viergliedrigen Netzwerken sowie sequenzabhängiger Anpassung; keine Übernahme einer universellen Kritikalitätsbehauptung |
| ON-S3 | [Bertschinger et al. 2014](https://www.mdpi.com/1099-4300/16/4/2161/html), DOI 10.3390/e16042161; [Autoren-Preprint](https://arxiv.org/abs/1311.2852) | Bibliografie und Primärquellenzugang verifiziert; SCF-Implementierung gelesen | Definition der vorhandenen BROJA-Zerlegung |
| ON-S4 | [Lazic 2010](https://pmc.ncbi.nlm.nih.gov/articles/PMC2817684/), DOI 10.1186/1471-2202-11-5 | Bibliografie und Primärquellenfundstelle verifiziert | Replikationseinheit und verschachtelte Messungen |
| ON-S5 | [Varoquaux 2018](https://doi.org/10.1016/j.neuroimage.2017.06.061), [Autoren-Preprint](https://arxiv.org/abs/1706.07581) | Bibliografie und Primärquellenzugang verifiziert | Unsicherheit bei kleinen Stichproben und Cross-Validation |
| ON-S6 | [SCF-Arimoto–Blahut-Dokumentation](https://github.com/GenesisAeon/scoped-correspondence-formalism/blob/4a7ed38640ac7d393017eb5556291c879c3bceac/docs/arimoto_blahut_capacity.md) | Dokumentation und Code geprüft | Bestehende Implementierung, DMC-Scope und dortige Originalquellen |
| ON-S7 | [SCF-Directed-Information-Dokumentation](https://github.com/GenesisAeon/scoped-correspondence-formalism/blob/4a7ed38640ac7d393017eb5556291c879c3bceac/docs/directed_information_core.md) | Dokumentation und Code geprüft | Endliche Sequenzverteilungen und bestehende Kontrollfälle |

Die Originalnotiz `Kandidat_Organoid_Trio_Netzwerke_2026-10-01.md` bleibt als Kandidatensammlung erhalten. Sie wird nicht zur wissenschaftlichen Primärquelle umdeklariert. Quellenstatus, Datenverfügbarkeit und rechtliche Wiederverwendbarkeit sind getrennte Felder.

## 3. Repo-Basis und tatsächliche Anschlüsse

Gelesener öffentlicher Stand: `GenesisAeon/scoped-correspondence-formalism`, Commit `4a7ed38640ac7d393017eb5556291c879c3bceac`. Vor Beginn den aktuellen HEAD und bestehende Arbeit prüfen. Dieser Plan behauptet weder eine hier ausgeführte Repo-Regression noch einen aktuellen GitHub-CI-Lauf.

`CLAUDE.md` verlangt unabhängige Herleitungen, ein allein committedes erstes Roadmap-Paket, paketweise Implementierung und Regression. Diesem Ablauf folgen. Eine eventuell inzwischen umgesetzte J-Roadmap kann geeignete Statistik- oder Scope-Werkzeuge beisteuern, ist aber keine Voraussetzung dieses Plans. Keine vorhandene Funktion nur anhand eines Namens als passend behandeln.

| Vorhandene API | Verifizierter Pfad | Richtige Verwendung / Grenze |
|---|---|---|
| `mutual_information_dmc(r, Q, log_base=2)` | `src/scoped_correspondence/observation/arimoto_blahut.py` | Information eines angegebenen endlichen Kanals unter einem angegebenen Eingangsprior |
| `blahut_arimoto_capacity(Q, r0=None, tol=..., max_iter=..., log_base=2)` | derselbe Pfad | Kapazität des festgehaltenen DMC-Modells; `converged` beachten |
| `directed_information(joint_sequences)` | `src/scoped_correspondence/observation/directed_information.py` | Exakte endliche Sequenzverteilung; kein fertiger Schätzer für lange Spikezüge und kein Kausalitätsbeweis |
| `broja_pid_bivariate(joint_r1r2y, n_starts=..., tol=..., rng=None)` | `src/scoped_correspondence/information_decomposition/broja.py` | Tensorachsen sind Quelle 1, Quelle 2, Ziel; Optimierungsdiagnostik beachten |
| `observation_fiber(...)`, `identified_values(...)` | `src/scoped_correspondence/epistemic/observation_fibers.py` | Exakte endliche Kandidaten und Beobachtungen; keine scheinbar exakten Fasern aus verrauschten Float-Daten |
| `evaluate_xor_task`, `evaluate_redundancy_task`, `evaluate_noisy_xor_task` | `src/scoped_correspondence/validation/cooperative_agents_pilot.py` | Bereits vorhandene positive und negative Informationskontrollen wiederverwenden |
| `FiniteDomainSpec`, `AssumptionSpec` | Von `observation_fibers.py` verwendete Records | Signaturen am aktuellen Stand lesen, keine neuen inkompatiblen Duplikate bauen |
| Kategorien und Gesamtaufruf | `scripts/run_verification_suite.py` | Jedes neue `verify_*.py` explizit in `_EXPLICIT_CATEGORY` registrieren |
| Provenienz | `docs/real_data_provenance.md` | Vor einem realen Import vollständig lesen |

Keine neue PID-, Entropie- oder Kanalkapazitätsbibliothek schreiben. Kleine PMF-Adapter, Decoder- und Datenprüfer ergänzen, sofern nicht inzwischen passende Helfer vorhanden sind.

## 4. Vorab festgelegte Fragen

Die Auswertung soll diese Fragen getrennt beantworten:

- **F1 — Repräsentation:** Ändert sich die bedingte Antwortverteilung P(Y|S), wenn die Kopplung angepasst wird?
- **F2 — Messzugang:** Wie viel dieser Unterscheidbarkeit bleibt nach räumlicher oder zeitlicher Aggregation erhalten?
- **F3 — Decoder:** Beruht ein Scoreunterschied auf vorhandener Information, der Decoderklasse oder einer veränderten Zuordnung zwischen Antwort und Label?
- **F4 — Architektur:** Welche Unterschiede bleiben bei gleicher Zustandszahl, gleichem Anregungsbudget und gleicher Beobachtungsdimension?
- **F5 — Anpassung:** Welche Effekte verschwinden bei eingefrorenen Gewichten, und welche bleiben durch Zustandsdynamik oder Drift erhalten?
- **F6 — Gerichtetheit:** Bleibt gerichtete statistische Information bestehen, wenn gemeinsame Eingänge und Vorgeschichte berücksichtigt werden?

Ein negatives oder gemischtes Ergebnis ist zulässig. Kein Abnahmekriterium verlangt, dass Trios gewinnen oder dass der gewählte Plastizitätsmechanismus die Studie reproduziert.

## 5. Exakter Einstieg: gleiche Gesamtaktivität, unterschiedliche Information

### 5.1 Zweidimensionaler Antwortoperator

S∈{0,1} sei ein fairer Stimulusindex, u0=(1,0), u1=(0,1). Definiere für 0≤δ≤1:

\[
W(\delta)=\begin{pmatrix}1+\delta&1-\delta\\1-\delta&1+\delta\end{pmatrix},
\qquad y_S=W(\delta)u_S.
\]

Die Spaltensummen betragen jeweils 2; det W=4δ. Bei δ=0 sind die Antworten identisch. Bei δ=1/2 entstehen (3/2,1/2) und (1/2,3/2).

Zwei Beobachter:

\[
O_{\rm full}(y)=y,\qquad O_{\rm sum}(y)=y_1+y_2.
\]

Für jedes δ ist O_sum=2. Für δ>0 unterscheidet O_full im rauschfreien Fall die beiden Eingänge. Bei fairem S gilt daher I(S;O_full)=1 Bit und I(S;O_sum)=0 Bit. δ=0 liefert für beide null Information.

**Wichtige Einordnung:** δ ist in diesem ersten Benchmark ein vorgegebener Strukturparameter. Ein Sweep von δ ist noch kein gelernter Mechanismus. Der abrupte Wechsel von null zu einem Bit bei beliebig kleinem δ>0 beruht auf unendlich präziser rauschfreier Beobachtung; er ist keine biologische Kippschwelle.

### 5.2 Rauschen und Bayes-Kontrolle

Für Y=Wu_S+ε mit ε∼N(0,σ²I2), gleichen Priors und σ>0 lautet die optimale Klassifikationsgenauigkeit:

\[
A^*(\delta,\sigma)=\Phi\left(\frac{\sqrt2|\delta|}{\sigma}\right)
=\frac12\left[1+\operatorname{erf}\left(\frac{|\delta|}{\sigma}\right)\right].
\]

Herleitung: Der Abstand der Mittelwerte beträgt 2√2|δ|; die Trennebene liegt in der Mitte. Für δ=σ=1/2 folgt A*=0,9213503964748575. Der Summenbeobachter sieht auch mit diesem Rauschen für beide Klassen dieselbe Verteilung.

Bei σ=0 die Grenzfälle ausdrücklich behandeln: δ=0 → A*=1/2; δ≠0 → A*=1. Keine Division durch null und keine Interpretation des rauschfreien Sprungs als empirisches Ergebnis.

**Noch keine Informationsschätzung aus der Genauigkeit:** A* allein bestimmt die vollständige gegenseitige Information nicht. Das zeigt ON-C06 mit zwei verschiedenen Kanälen gleicher Genauigkeit.

## 6. Adaptiver Netzwerkgenerator mit klar begrenztem Scope

### 6.1 Zwei Zeitskalen

Verwende ein dimensionsloses Zustandsmodell. k bezeichnet schnelle Schritte innerhalb eines Reizversuchs, d die langsame Trainingsphase:

\[
x_{d,k+1}=(1-\ell)x_{d,k}+\ell\tanh(A_d x_{d,k}+B u_{d,k}),
\qquad 0<\ell\le1.
\]

x0=0, B und u sind nichtnegativ. Dadurch bleiben die Zustände in diesem Modell nichtnegativ und bei geeigneten Anfangswerten in [0,1]. Für den Pflichtumfang genügt Messrauschen; Prozessrauschen ist optional und benötigt einen neuen Scope für Zustandsschranken.

Die Ausgabe eines Versuchs ist beispielsweise:

\[
y=H\sum_{k\in\mathcal W}w_kx_{d,k}+\varepsilon,
\qquad\varepsilon\sim N(0,\sigma^2I).
\]

H, Fenster W und Gewichte w werden vorab festgelegt. Keine Auswahl anhand der späteren Testlabels. Einheiten lauten zunächst „Modellschritt“ und dimensionslose Amplitude. Ohne zusätzliche Kalibration keine behaupteten biologischen Millisekunden oder realen Feuerraten.

### 6.2 Vergleichbare Ressourcen

Erster Standardumfang: N=12 Zustände, M∈{1,2,3} gleich große Module. Das ist ein **Vergleich mit festem Gesamtbudget**, keine Nachbildung wachsender Gewebemenge. Biologienahe Vergleiche mit konstanter Größe pro Modul sind eine gesonderte optionale Konfiguration.

Für A_ij gilt: Zeile i empfängt, Spalte j sendet. Diagonale null, A≥0, jede Zeilensumme γ mit 0<γ<1. Bei M>1 und Modulgröße n=N/M:

\[
A_{ij}=\begin{cases}
\gamma(1-c)/(n-1),&i\ne j\text{ im selben Modul},\\
\gamma c/(N-n),&i,j\text{ in verschiedenen Modulen},\\
0,&i=j.
\end{cases}
\]

Bei M=1 stattdessen A_ij=γ/(N−1) für i≠j; c ist dort **nicht anwendbar**. γN ist das gesamte Gewicht, die Eingangs- und Beobachtungsbudgets bleiben gleich. Gleiche Zeilensummen garantieren dabei nicht identische Ausgänge oder identische Graphspektren.

Der besonders wichtige Nullfall: Für N=12, M=2,c=6/11 beziehungsweise M=3,c=8/11 entsteht genau dieselbe Matrix wie bei M=1. Mit identischem B,H, Eingängen, Anfangszustand und Rauschen müssen die Ausgaben identisch sein. **Modulnamen allein dürfen keinen Vorteil erzeugen.**

Für Variabilität dürfen positive, vom Seed abhängige Gewichtsfaktoren eingeführt werden. Intra- und Interanteile separat normalisieren, wenn der anfängliche Wert c exakt erhalten bleiben soll. Ohne solche Asymmetrien kann ein symmetrisches Modell gleiche Antworten liefern; dies ist ein gültiges Ergebnis. Keine Asymmetrie versteckt einbauen und anschließend als spontan entstandenen Befund berichten.

### 6.3 Eingangsarchitektur explizit führen

B besitzt zwei festgelegte, gleich normierte Spalten. H beobachtet eine vorab festgelegte Zahl von Zuständen. Eine mögliche Anordnung verwendet Eingänge an den Zuständen 0 und 4 und Ausgänge 10 und 11 bei zusammenhängenden Modulindizes. Dann liegen die Eingänge bei M=2 im selben, bei M=3 in getrennten Modulen.

Diese Anordnung ist als **gebündelte Architekturänderung** zu kennzeichnen. Ein ergänzender Sweep über festgelegte Eingangsplatzierungen soll untersuchen, ob die Zuordnung zu Modulen entscheidend ist. Weil drei getrennte Rollen nicht auf zwei getrennte Module verteilt werden können, ist nicht jede Rollenbedingung mit jeder Modulzahl kreuzbar. Unmögliche Faktor-Kombinationen als `not_applicable` melden, nicht durch geänderte Aufgaben ersetzen.

Pro Vergleich protokollieren: N, M, zulässige Kanten, γ, tatsächliche Intergewichte, B, H, Messdimension, Reizenergie, Versuchslänge und Decoderbudget. Ein Vorteil bei mehr Messkanälen ist eine andere Aussage als ein Vorteil bei gleicher Beobachtung.

### 6.4 Eine begrenzte unüberwachte Anpassungsregel

Als transparenten synthetischen Kandidaten verwende eine verzögerte Hebb-Regel. Für Trainingszustände und feste Kantenmaske M_ij:

\[
G_{ij}=M_{ij}\,\langle x_{k+1,i}x_{k,j}\rangle_{\rm train},
\quad \widetilde A=(1-\eta)A+\eta G,
\quad A'_{ij}=\gamma\frac{\widetilde A_{ij}}{\sum_j\widetilde A_{ij}},
\quad 0\le\eta<1.
\]

M_ii=0. Unzulässige Kanten bleiben null. Die Regel benutzt lokale Vor-/Nachaktivität, keine externen Stimuluslabels und keinen Zielscore. Sie ist eine gewählte Modellregel, kein aus der Studie identifiziertes biologisches Lernverfahren. Gemeinsame Anregung kann G ebenfalls verändern; das gehört zu den Kontrollen.

Für nichtnegative Zustände und A mit positiver Zeilensumme ist der Nenner wegen η<1 positiv. η=0 muss A exakt erhalten. Bei „keine Verbindung zwischen Modulen“ muss die Maske solche Kanten dauerhaft sperren; bloße Startgewichte null genügen nicht. Die Regel hält das Gesamtgewicht pro Zeile konstant, aber nicht automatisch den Interanteil c. Diesen nach jeder Anpassung berichten.

A wird nur durch die getrennten Trainingsversuche verändert. Während der Probe und des Tests ist A eingefroren. Der schnelle Zustand wird für unabhängige Probeversuche zurückgesetzt; ein Modus ohne Reset muss als Kanal mit Gedächtnis gesondert analysiert werden.

### 6.5 Stabilitätsargument und Grenzen

Für festes A und denselben Eingang ist tanh 1-Lipschitz. Aus ||A||∞=γ folgt:

\[
\|F_A(x)-F_A(z)\|_\infty
\le(1-\ell+\ell\gamma)\|x-z\|_\infty.
\]

Bei ℓ=γ=1/2 beträgt die Schranke 3/4. Das ist ein exakter Kontraktionsnachweis für **eingefrorene Gewichte und identische Eingänge**, kein Beweis, dass der gesamte gekoppelte Lernprozess zu einem eindeutigen Netz konvergiert. Die erste Version bildet weder neuronale Erregungs-/Hemmungsvielfalt noch Spikes oder echte Synapsenbildung ab.

## 7. Messung, Decoder und Information sauber trennen

### 7.1 Drei verschiedene Auslesefragen

| Auswertung | Frage | Was sie nicht automatisch zeigt |
|---|---|---|
| Neu angepasster Decoder pro Epoche, festgelegte Pipeline | Wie gut lassen sich die aktuellen Antworten auslesen? | Zeitlich stabiles Format derselben Repräsentation |
| Vor Anpassung trainierter, danach eingefrorener Decoder | Bleibt die alte Zuordnung lesbar? | Gesamter Informationsgehalt der neuen Antwort |
| Analytischer Bayes-Decoder im bekannten Kontrollmodell | Welche Genauigkeit erlaubt das definierte Modell optimal? | Erreichbarkeit durch beliebige Decoder bei endlichen Daten |

Kontrollfall: Y=S vor der Veränderung und Y=1−S danach. Die Information bleibt ein Bit. Der alte Decoder fällt von 100 % auf 0 %, ein richtig angepasster erreicht wieder 100 %. Ein Scoreabfall ist hier keine Informationsvernichtung.

Als obligatorischer Decoder genügt ein transparenter nächster-Klassenmittelpunkt-Decoder. Für gleiche sphärische Kovarianzen ist er im Populationsgrenzfall passend zur Gaußkontrolle. Seine Normalisierung und Klassenmittel ausschließlich am Trainingsteil bestimmen. Eine lineare probabilistische Baseline kann ergänzt werden. SVM und CNN sind optionale Vergleichsmodelle; der Pflichtpilot braucht keine neue PyTorch-Abhängigkeit.

### 7.2 Endlicher Kanalanschluss

Sei Z=g(Y) eine vorab festgelegte endliche Kodierung der gemessenen Antwort. Aus einem deklarierten Fenster wird Q_d(z|s) geschätzt. g kann ein einfacher Schwellwert oder ein eingefrorener Decoder sein. Es gilt beim passenden Markov-Zusammenhang:

\[
I(S;Z)\le I(S;Y).
\]

Eine Konfusionsmatrix des Decoders beschreibt den zusammengesetzten Kanal **System → Messung → Decoder**. Seine Kapazität ist nicht automatisch die Kapazität des Organoids oder Netzwerks.

Arimoto–Blahut darf pro Fenster nur für ein festgehaltenes, endliches gedächtnisloses Kanalmodell verwendet werden. Die Beziehung zwischen Stimulusprior und Q muss stabil genug sein: Verändert eine andere Eingangsverteilung die Gewichte oder den Zustand, darf man den optimierten Prior nicht als ohne Weiteres realisierbares biologisches Maximum ausgeben.

Pflichtausgaben: Prior, Kontingenztabelle, Kanalzeilen, Stichprobenzahlen, Kodierung, Fenster, Reset-/Gedächtnisannahme, Schätzverfahren, Unsicherheit und Konvergenz. Eine fehlende Stimulusklasse ergibt eine unbekannte Kanalzeile. Keine automatische Gleichverteilung und keine Kapazitätszahl aus einem einzelnen Accuracy-Wert.

Für kleine empirische Tabellen einen deklarierten Umgang mit leeren Zellen und Bias wählen. Pseudocounts sind eine Regularisierungsannahme und müssen sichtbar bleiben. Exakte synthetische PMFs benötigen sie nicht. Keine Hochdimensionalitätsprobleme durch unkontrollierte Binning-Verfeinerung verdecken.

### 7.3 PID: Quellen nicht mit alternativen Labels verwechseln

Für den ersten PID-Anschluss seien R1,R2 zwei **gleichzeitig beobachtete Teilantworten desselben Versuchs** und S der Stimulusindex. Übergabe an BROJA: p(R1,R2,S), Achsen in genau dieser Reihenfolge.

Die beiden einander ausschließenden Stimulusorte nicht einfach als unabhängige Informationsquellen behandeln. „Drei Module“ bedeutet außerdem nicht „drei Quellen“ in einer bivariaten PID. Aus einem gemeinsam guten Decoder folgt keine positive Synergie. Das Beispiel, in dem beide Teilantworten das Label schon allein verraten, kann vollständig redundant sein.

Exakte Pflichtkontrollen: XOR-Signatur (0,0,1 Bit) für Einzel-/Gemeinschaftsinformation und reine Redundanz (1,1,1 Bit). Die bekannten BROJA-Werte mit dem bestehenden Solver reproduzieren. Optimierungsfehler und nichtkonvergierte Läufe sichtbar machen; negative numerische Atome nicht still auf null kappen.

### 7.4 Gerichtetheit und gemeinsame Ursachen

Die vorhandene Directed-Information-API verarbeitet endliche gemeinsame Sequenzverteilungen. Sie ist kein direkter Importweg für beliebig lange kontinuierliche MEA-Aufnahmen.

Exakte Gegenkontrolle: U ist ein faires Bit, A=(U,0), B=(0,U). Dann beträgt I(A→B)=1 Bit, obwohl die strukturellen Gleichungen nur U→A und U→B enthalten. Bedingt auf U verschwindet die Information; eine Intervention auf A1 lässt die Verteilung von B2 unverändert.

Diese Konstruktion muss in ON5 erscheinen. Danach kann der synthetische Pilot seine bekannte Eingangsfolge und verborgenen Zustände zur Diagnose nutzen. Bei realen Daten sind diese meist nicht vollständig beobachtet. Ein statistisches Richtungsmaß ohne diese Kontrolle darf nicht als identifizierte kausale Verdrahtung ausgegeben werden. Ein zusätzlicher bedingter endlicher Adapter ist zulässig, wenn seine Definition vollständig hergeleitet und geprüft wird.

## 8. Vorab festgelegtes Auswertungsprotokoll

### 8.1 Trennung der Datenflüsse

Es gibt drei getrennte Mengen:

1. **Adaptationstrials:** verändern A, ohne externe Antwortlabels zu optimieren.
2. **Decodertraining/innere Validierung:** A bleibt fest; Vorverarbeitung, Klassifikator und gegebenenfalls Hyperparameter werden gelernt.
3. **Äußere Tests:** A, Vorverarbeitung, Kodierung und Decoder bleiben fest.

Das Lesen eines Testlabels für Anpassung, Kanal-Binning, Featurewahl oder frühes Stoppen ist Leakage. Kanal- und Scoreauswertung dürfen Labels selbstverständlich anschließend zur Bewertung verwenden, aber nicht rückwirkend zur Pipelinewahl.

Default: balancierte, randomisierte Reizreihenfolge und getrennte RNG-Ströme für Topologie, Adaptation, Decodertraining und Test. Seeds und komplette Konfiguration speichern. Gleicher Seed allein bedeutet nicht identische Daten über verschiedene Softwareversionen; veröffentlichte Resultate brauchen Konfiguration und Versionsangaben.

### 8.2 Drei unterschiedliche Generalisierungsziele

- **Innerhalb eines Präparats/einer Epoche:** neue unabhängige Versuche derselben Anordnung.
- **Über Epochen:** zukünftige Phase mit festem oder ausdrücklich neu trainiertem Decoder; beides getrennt berichten.
- **Über Präparate:** neue Kultur bzw. neuer Simulationsseed als vollständig zurückgehaltene Gruppe.

Für den dritten Fall müssen Features zwischen Präparaten vergleichbar sein. Elektrodenpositionen oder Neuronenlabels verschiedener Präparate sind nicht automatisch ausgerichtet. Eine gemeinsame Repräsentation nur am Trainingsbestand bestimmen oder biologisch begründet vorab definieren. Ohne das bleibt die Aussage auf präparatinternes Dekodieren beschränkt.

Zeitfenster desselben Versuchs dürfen nicht auf Trainings- und Testseite verteilt werden. Bei korrelierten Folgeversuchen zusätzlich blockweise oder mit Abstand trennen. „Letzte 20 %“ garantiert allein weder Unabhängigkeit noch Schutz vor systematischer Reizreihenfolge.

### 8.3 Statistische Einheit und Vergleich

Primäre Einheit einer biologischen Aussage ist das unabhängige Präparat bzw. je nach Design die Kultur oder der Batch. Bei Simulationen ist es der separat erzeugte Lauf, nicht jeder Zeitschritt. Simulationsseeds ersetzen keine biologischen Replikate.

Zuerst pro Einheit einen vorab definierten Kontrast bilden, etwa Δ_b=Accuracy_after,b−Accuracy_before,b. Gruppeneffekte direkt vergleichen:

\[
\Delta_{\rm stim}-\Delta_{\rm control}.
\]

„In einer Gruppe signifikant, in der anderen nicht“ ist kein Test des Gruppenunterschieds. Eine kausale Deutung des Kontrasts benötigt zusätzlich das passende Zuweisungsdesign oder andere begründete Identifikationsannahmen.

Berichte Einzelwerte, Effektgröße, Unsicherheit und Ausfälle. Bei wenigen Gruppen sind asymptotische Standardfehler und auch Bootstrap-Intervalle fragil. Gepaarte Sign-Flip-Tests nur unter begründeter Vorzeichen-Austauschbarkeit bzw. geeigneter Randomisierung verwenden. Der Kontrollfall mit fünf positiven Differenzen hat beim zweiseitigen vollständigen Sign-Flip-Test minimal p=2/32=0,0625. Das ist eine Eigenschaft dieses Kontrolltests, keine nachträgliche Widerlegung eines parametrischen Tests in der Originalarbeit.

Permutationen müssen die zulässige Austauschbarkeit erhalten: Labels nicht blind über Präparate, Zeitblöcke oder Bedingungen mischen. Bei mehreren vorab definierten primären Kontrasten Korrektur oder simultane Unsicherheit festlegen; weitere Suchen als explorativ kennzeichnen. Keine vielen nachträglichen Tests, bis eine Modulzahl gewinnt.

### 8.4 Auswahl am Ausgangspunkt und fehlende Aktivität

Ein Pilot, der schwer unterscheidbare Eingangspaare auswählt, braucht eine getrennte Auswahlstichprobe. Dieselben verrauschten Daten nicht gleichzeitig für die Auswahl und den Ausgangsscore verwenden. Eine passende synthetische Nullsimulation kann die Folgen dieses Auswahlverfahrens untersuchen. Die Auswahlregel gehört auch in den Kontrollarm.

Fehlende Antwort, technisch defekte Aufnahme und vorhandene, aber informationsarme Antwort sind verschiedene Fälle. Ausschlussgründe und Anzahl pro Bedingung dokumentieren. Keine stille Löschung wenig erfolgreicher Präparate. Ausschlussregeln vor Ergebnisbetrachtung festlegen.

## 9. Pflichtkontrollen und Ergebnisvokabular

Die folgenden 23 Gruppen sind im beigefügten `independent_organoid_controls.py` unabhängig ausgeführt. Das Skript importiert keinen SCF-Code und führt keinen biologischen Datenfit aus. Seine Rechnungen müssen gegen die spätere Produktion getestet werden; Kopieren derselben Funktion in Produktion und Test ist keine unabhängige Prüfung.

| ID | Exakter oder analytischer Sollbefund | Paket |
|---|---|---|
| ON-C01 | W(1/2): Ausgaben (3/2,1/2), (1/2,3/2); Summe je 2; det W=4δ | ON1 |
| ON-C02 | Vollbeobachtung 1 Bit; Summenbeobachtung 0 Bit; grobe Faser enthält beide Eingänge | ON1 |
| ON-C03 | Invertierbare Sensorpermutation erhält Information | ON1 |
| ON-C04 | δ=σ=1/2: Bayes-Accuracy 0,9213503964748575 | ON2 |
| ON-C05 | BSC: ε=1 hat 1 Bit, naive Accuracy 0, optimale 1 | ON2 |
| ON-C06 | Accuracy jeweils 0,75: BSC I≈0,188722; Z-Kanal I≈0,311278, C=log2(5/4)≈0,321928 | ON2 |
| ON-C07 | Y=(S,N), Z=N: I(S;Y)=1, I(S;Z)=0 | ON2 |
| ON-C08 | Y=S xor H: I(S;Y)=0, I(S;Y|H)=1 bei unabhängigen fairen S,H | ON2/ON5 |
| ON-C09 | Codeinvertierung: eingefrorener Decoder 0, angepasster 1; Information unverändert | ON4 |
| ON-C10 | Konstanter Decoder bei Prior 0,9: Accuracy 0,9, balanced Accuracy 0,5, Information 0 | ON4 |
| ON-C11 | Hebb-Kontrolle: zweite Zeile wird (5/12,0,1/12); alle Zeilensummen 1/2 | ON3 |
| ON-C12 | η=0 erhält A; ℓ=γ=1/2 → Kontraktionsschranke 3/4 | ON3 |
| ON-C13 | XOR vollständig informativ; beste einzelne affine Schwelle auf vier Eckpunkten 0,75, XOR-Decoder 1 | ON4 |
| ON-C14 | Analytische PID-Oracles: XOR reine Synergie 1 Bit; Kopie reine Redundanz 1 Bit | ON5 |
| ON-C15 | Gemeinsame Ursache: Directed Information 1 Bit, bedingt auf U null; do(A1) verändert B2 nicht | ON5 |
| ON-C16 | Blockzeit kodiert das Label: scheinbar 1 Bit ohne Reizwirkung; randomisiert 0 Bit | ON4 |
| ON-C17 | 100 Kopien je fünf Präparaten: Gruppen-SEM²=1/2; falsches gepooltes SEM²=2/499 | ON4 |
| ON-C18 | Fünf positive Differenzen: zweiseitiger vollständiger Sign-Flip-Test p=1/16 | ON4 |
| ON-C19 | Mittlere Änderungen 1/4 und 3/20 → Gruppenunterschied 1/10 | ON4 |
| ON-C20 | Gruppenüberlappung ablehnen; Training (0,2) hat Mittel 1, mit Testwert 100 fälschlich 34 | ON4 |
| ON-C21 | Negative, nichtnormierte und nichtendliche Kanäle zurückweisen | ON2 |
| ON-C22 | N=12, M=1/2/3: gleiche Zeilensumme 4/5; bei c=1/4 und M>1 Intergewicht 1/5 | ON3 |
| ON-C23 | M=1, M=2 mit c=6/11, M=3 mit c=8/11: identische Matrix mit Nebendiagonalen 4/55 | ON3 |

Herleitung ON-C11: A hat Zeilen (0,1/2,0), (1/4,0,1/4), (0,1/2,0). Präaktivität (1,0,0), Folgeaktivität (0,1,0), η=γ=1/2. Die rohe zweite Zeile ist (5/8,0,1/8); Normalisierung auf Summe 1/2 ergibt (5/12,0,1/12).

Herleitung ON-C13: Bei XOR liegen die positiven und negativen Klassen jeweils auf gegenüberliegenden Ecken eines Quadrats. Die zwei erforderlichen positiven affinen Summen und die zwei negativen Summen widersprechen sich beim Addieren. Daher keine perfekte einzelne affine Trennung. Eine Fehlklassifikation ist erreichbar; der kleine ganzzahlige Scan im Kontrollskript bestätigt dies, ist aber nicht allein der Beweis über alle reellen Gewichte.

Ergebnisfelder nach `CLAUDE.md` übernehmen: `evidence_kind` getrennt von `empirical_status`; `search_complete` getrennt von `all_candidates_scanned`; Scope und Kandidatenumfang separat. Zulässige Beispielkombinationen:

- exakte endliche PMF: `exhaustive_finite` + `synthetic_only`;
- Kontraktionsherleitung: `analytic_argument` + `not_tested`;
- Monte-Carlo-Benchmark: `numerical_sample` + `synthetic_only`;
- reale Auswertung: `empirical_evaluation` + `evaluated_on_declared_data`.

Zusätzliche Felder: `scope_id`, `configuration_id`, `dataset_hash`, `preparation_id`, `split_id`, `measurement_map`, `decoder_mode`, `stationarity_assumption`, `memory_assumption`, `prior`, `sample_counts`, `excluded_units`, `uncertainty_method`, `optimization_status`, `limitations`. Nicht vorhandene Evidenz als nicht ausgewertet melden; kein generischer Gesamtscore „Emergenz bestätigt“.

## 10. Architektur und Paketplan

### 10.1 Vorgeschlagene neue Dateien

```text
ORGANOID_NETWORK_ROADMAP.md
docs/organoid_network_pilot.md
docs/organoid_network_source_audit.md
src/scoped_correspondence/validation/modular_networks/
  __init__.py
  records.py
  observation_controls.py
  adaptive_model.py
  decoding.py
  evaluation.py
  information_adapters.py
  provenance.py
scripts/run_organoid_network_pilot.py
verification/verify_organoid_observation_controls.py
verification/verify_organoid_adaptive_model.py
verification/verify_organoid_decoding_evaluation.py
verification/verify_organoid_information_adapters.py
```

Alle neuen Dateinamen sind Vorschläge. Wenn das Repo bereits geeignete Helfer hat, wiederverwenden und die finale Zuordnung in ON0 dokumentieren. Produktionsmodule dürfen nicht von `verification/` importieren. Kein Realdatenparser, der still synthetische Platzhalter als Messdaten ausgibt.

### ON0 — Quellen, Umfang und Handkontrollen

Lies den ganzen Plan, aktuelle Repo-Anweisungen und APIs. Leite jede ON-C-Gruppe eigenständig her, bevor Produktionscode entsteht. Erstelle Roadmap mit echten Datei-/Zeilenreferenzen, Quellenstatus, Scope und Kontrollen. Einziger Inhalt des ersten Commits ist dieses nachvollziehbare Startpaket.

**Abnahme:** Drei-Modul-Schwelle nicht vorausgesetzt; Grenzen von Beobachtung und Decoder benannt; Daten-Gate sichtbar; keine J-Abhängigkeit erfunden. Unabhängige Werte stimmen oder eine Abweichung wird vor Umsetzung aufgeklärt.

### ON1 — Exakte Beobachtungs- und Strukturkontrollen

Implementiere W(δ), Summen- und Vollbeobachter, rationale Kontrollwerte und den Anschluss an endliche Beobachtungsfasern. Trenne Funktion, Beobachtung und Stimuluslabel.

**Pflicht:** ON-C01–C03. Zusätzlich δ außerhalb [0,1], ungültige Dimensionen und nichtendliche Eingaben zurückweisen. Verrauschte Float-Ähnlichkeit nicht als exakte Gleichheit behandeln. Keine Annahme, dass unterschiedliche Vektoren bei endlichem Rauschen zuverlässig unterscheidbar sind.

### ON2 — Messrauschen und endliche Kanäle

Implementiere Gaußkontrolle, diskrete Kanaladapter, MI beim beobachteten Prior und bedingte DMC-Kapazität über vorhandene APIs. Kanalzeilen, Kodierung und Unsicherheit im Bericht speichern.

**Pflicht:** ON-C04–C08, ON-C21. Scoregleichheit darf keine Informationsgleichheit implizieren. Nullrauschen, fehlende Klassen und ε=1 korrekt behandeln; negative oder nichtendliche Rauschparameter zurückweisen. Numerische Schätzung, exakte PMF und analytische Antwort getrennt testen. Grobe Beobachtung darf im exakten Datenverarbeitungs-Kontrollfall keine Information hinzufügen.

### ON3 — Begrenzte adaptive Dynamik

Implementiere N=12-Baseline, Modulpartitionen, Ressourcennormalisierung, getrennte Eingangs-/Ausgangsmasken und die deklarierte Hebb-Regel. Eigene RNG-Ströme und vollständige Konfiguration. Kleine Tests verwenden exakte Ein-Schritt-Kontrollen.

**Pflicht:** ON-C11–C12, ON-C22–C23. Zusätzlich dauerhaft gesperrte Interkanten, η=0, positive Normalisierungsnenner, Summenbudget und Stabilitäts-Scope prüfen. Gewichte während Probe/Test unverändert. Ein identischer Operator unter verschiedenen Modulnamen liefert identische Trajektorien. Keine Abnahmebedingung „Trio gewinnt“.

### ON4 — Decoder und hierarchischer Vergleich

Implementiere Training und Test mit Gruppen-/Zeitgrenzen, nächster-Klassenmittelpunkt-Baseline sowie neu trainierten und eingefrorenen Decoder. Vorverarbeitung nur im Training. Effekte auf Ebene unabhängiger Läufe/Präparate auswerten.

**Pflicht:** ON-C09–C10, ON-C13, ON-C16–C20. Die Leakage-Fixtures müssen gegen die Produktions-Splitter und Preprocessor schlagen. Doppelte Versuche dürfen die Zahl biologischer Einheiten nicht erhöhen. Primäre Kontraste vor größeren Runs festlegen; Einzelwerte und Ausfälle berichten. Sign-Flip-Test ohne seine Voraussetzungen nicht als verteilungsfreien Universaltest anbieten.

### ON5 — Information, PID und Gerichtetheit

Verbinde kleine endliche Kanäle und Antwort-PMFs mit vorhandenen APIs. Definiere Quellen, Ziel, Zeitindex und Konditionierung explizit. Keine vollständige Zeitreihen-Schätzbibliothek bauen.

**Pflicht:** ON-C08, ON-C14–C15 plus die vorhandenen XOR-, Redundanz- und Directed-Information-Kontrollen. BROJA-PID-Solver tatsächlich ausführen; die Begleitrechnung hat lediglich analytische Erwartungswerte und MI-Signaturen bestimmt. Konvergenz und schätzbedingte Unsicherheit getrennt berichten. Kausaler Befund nur bei zusätzlichem Identifikationsargument.

### ON6a — Synthetischer Benchmark und Evidenzbericht

Pflichtumfang: kleine, vorab festgelegte Liste von Bedingungen, mindestens eingefrorene/angepasste Gewichte, volle/aggregierte Beobachtung, identischer Operator mit anderen Modulnamen, räumlich geteilte/nichtgeteilte Eingänge und ein Drift-Gegenbeispiel. Ausreichend getrennte Seeds für den deklarierten Vergleich; Anzahl und Präzisionsziel im Protokoll begründen.

Ein schneller deterministischer CI-Lauf prüft Invarianten und die Berichtserzeugung. Eine größere stochastische Effektstudie läuft separat und darf nicht als Zufalls-Gate „p<0,05 in jedem CI-Lauf“ implementiert werden. Unklare oder fehlende Vorteile bleiben im Abschlussbericht erhalten.

**Abnahme:** Konfigurationsdatei vor Resultatinterpretation gespeichert; Budgets vergleichbar oder Unterschiede ausdrücklich benannt; Scores, Information und Ressourcen nicht zu einem unkalibrierten Index vermischt.

### ON6b — Optionaler Realdatenadapter

Echte Daten erst nach dem bestehenden Provenienzprotokoll. Lokale, lesende Quellenprüfung ist Teil des Auftrags; Weiterverteilung und Einchecken fremder Dateien benötigen eine passende Grundlage. Keine unnötige Unterbrechung für die reine Implementierung eigener Parser und Fixtures.

Minimal notwendige Metadaten: Präparat-/Kultur-ID, gegebenenfalls Batch/Spender, Konfiguration, Epoche, Zeit, Reiz-ID, Versuch-ID, Antwortmerkmale bzw. Rohsignalpfad, Eingangs-/Ausgangskarte, Ausschlüsse und Split-Zuordnung. Kein Feld als tatsächlich geliefert voraussetzen. Fehlende Gruppen-IDs können eine unabhängige statistische Auswertung verhindern.

**Getrennte Daten-Gates:**

- **Nur aggregierte Scores:** deskriptive Reproduktion und gegebenenfalls präparatbezogener Scorevergleich; keine Rekonstruktion von Q, PID oder Directed Information aus einer einzigen Accuracy.
- **Versuchslabels und Antworten vorhanden:** Prüfung der Originalpipeline und sauber getrennter Alternativen; Reizartefakte, zeitliche Blöcke und Auswahlregeln auditieren.
- **Geeignete Zeitreihen vorhanden:** zusätzliche Gerichtetheitsanalyse mit begrenztem Alphabet, Zeitauflösung und Konditionierung; nicht automatisch direkte Synapsen rekonstruieren.

Für jede Datei Quelle, exakte URL/Query, Abrufzeit, Version, SHA-256, Format, Einheitenschema und Lizenzstatus erfassen. Die Artikellizenz nicht pauschal auf jede Drittdatei übertragen. Fehlt eine ausreichende Daten- oder Wiederverwendungsgrundlage, `blocked`/`deferred` mit konkretem Grund melden. Keine Autoren anschreiben ohne Johanns ausdrücklichen Auftrag.

### ON7 — CLI, Dokumentation und Abschluss

CLI beispielsweise:

```bash
python scripts/run_organoid_network_pilot.py --scenario exact --output results/exact.json
python scripts/run_organoid_network_pilot.py --scenario adaptive --config configs/organoid_minimal.json --output results/adaptive.json
python scripts/run_organoid_network_pilot.py --scenario confounds --output results/confounds.json
```

Die Pfade sind Zielbeispiele; `configs/organoid_minimal.json` muss erzeugt und dokumentiert werden. Ein Realdatenmodus ist nur bei verfügbarem ON6b-Datensatz zulässig. Keine erfolgreiche leere Auswertung bei fehlenden Dateien.

Roadmap und Fähigkeitsübersicht aktualisieren. Geklärt sein müssen: Was ist analytisch bewiesen? Welche endlichen Kontrollen sind vollständig geprüft? Welche Simulationen wurden ausgeführt? Welche realen Daten wurden tatsächlich ausgewertet? Was bleibt offen?

## 11. Regression, Laufzeit und Definition of Done

Neue Prüfskripte explizit als `math` registrieren, echte Datenprüfungen als `data`. Zusätzlich gezielte Modulprüfungen und alle zuvor implementierten ON-Checks. Nach jedem Paket gemäß `CLAUDE.md`:

```bash
python scripts/run_verification_suite.py --category all
python scripts/run_verification_suite.py --category links
```

Gesamtregression bei längerer Laufzeit im Hintergrund ausführen und Ergebnis prüfen. Pro Paket erst danach Commit und Push gemäß dem bestehenden Arbeitsauftrag. Keine vorhandenen Dokumente oder Verifikationen löschen, um einen grünen Lauf zu erzielen.

**Abschlusskriterien:**

- Alle 23 Kontrollen an der Produktion geprüft; separate Oracle-Herleitung bleibt erhalten.
- Mindestens ein vollständiger synthetischer Pilotlauf samt Konfiguration, Seeds und Ergebnissen.
- Richtiger Umgang mit unbekannten Kanälen, Nullinformation, Codeinvertierung, gemeinsamen Ursachen und fehlenden Gruppen.
- Keine pauschale Drei-Modul-, Kritikalitäts-, Lern- oder Kausalitätsbehauptung.
- Keine Vermischung von Decoderverbesserung, Informationsgewinn und stabiler Lesbarkeit.
- Datenteil kann offen bleiben, aber dann muss der Abschluss „synthetischer Kern abgeschlossen; Realdatenzweig offen“ lauten.
- Keine vollständige reale Replikation behaupten, wenn lediglich aggregierte Diagrammwerte verglichen wurden.

Ein kleines korrektes Modell mit klaren negativen Ergebnissen erfüllt den wissenschaftlichen Auftrag. Eine große Simulation, deren gewünschter Gewinner im Update oder in der Auswahlregel eingebaut ist, erfüllt ihn nicht.

## 12. Übergabepaket und Startprompt

Im Begleitpaket liegen:

- dieses selbsttragende Markdown;
- `independent_organoid_controls.py`;
- `independent_organoid_results.json`;
- eine kurze Startanleitung und SHA-256-Prüfsummen.

Ausführung mit Python-Standardbibliothek:

```bash
python independent_organoid_controls.py --output independent_organoid_results.json
```

Bei Erstellung bestanden **23/23 unabhängige Kontrollgruppen**. Noch nicht ausgeführt sind der adaptive Benchmark, der SCF-BROJA-Solver im neuen Pilot, eine reale Reanalyse und die zukünftigen Produktionsprüfungen. Diese Trennung muss in der Übernahme erhalten bleiben.

> **Startauftrag an Claude-Code:** Setze ON0–ON7 dieses Plans additiv im aktuellen SCF-Repo um. Beginne mit Quellen-/API-Audit und unabhängiger Herleitung aller Kontrollen. Halte Zustandsdynamik, Anpassung, Messoperator, Decoder und Evidenz getrennt. Verwende vorhandene Informations- und Epistemik-Module mit ihrem tatsächlichen Scope. Prüfe Gegenbeispiele ausdrücklich und erzwinge keinen Trio-Vorteil. Der synthetische Kern ist vollständig umzusetzen; der Realdatenzweig ON6b bleibt an seine Daten-Gates gebunden. Arbeite paketweise mit der vorhandenen Regression und dokumentiere fehlende Evidenz sowie zurückgestellte Teilaspekte sichtbar.
