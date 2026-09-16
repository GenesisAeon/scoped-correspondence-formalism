# Review: F08/F09, Gemini und die nächsten Erweiterungen

Stand: 16. September 2026. Bezug: die zuletzt hochgeladenen Übersichtsdateien. Eigenständiger Review mit Ergänzungsvorschlägen; keine neue konsolidierte Revision.

## 1. Ergebnis und Prüfgrenze

Die sichtbare Integration geht in die richtige Richtung: VB1 bleibt eine Konsistenzanforderung an gemeinsame Bestände; Sheaf-Kontextualität ist ein optionales Modul. EI bleibt eine eigene Größe; PID und Redundancy Bottleneck kommen mit eigenen Definitionen hinzu. Damit wurden mehrere zu weit gehende Forderungen aus Geminis Text bereits sinnvoll begrenzt.

Johanns Leitthese bleibt ausdrücklich **Selbstähnlichkeit unter Transformation, Zerlegung und Zusammensetzung mit kontextabhängigen Werten und Regeln**. Weder eine universelle Konstante noch eine Identität der drei Schichten ist dafür erforderlich. Gleiche Werte sind möglich, unterschiedliche Werte ebenso; entscheidend sind die angegebenen Beziehungen und Geltungsbedingungen.

Geprüft wurden die Inhalte von:

- FORMALISM(1).md und README(1).md;
- LITERATURE_CONNECTIONS.md und VERIFICATION.md;
- apply_manifest_F08_F09.json;
- Analyse und Erweiterung von CREP-UTAC-AFET.md, einschließlich der eingebetteten Formeln.

Das Manifest dokumentiert sieben Moduldateien und gemeldete Läufe mit 6/6 beziehungsweise 7/7 Prüfungen. Die beiden Modultexte, ihre beiden Python-Skripte, ihre beiden Ergebnisdateien und requirements_sheaf_pid.txt liegen diesem Review **nicht** vor. Ein Manifest enthält Soll-Prüfsummen; ohne die zugehörigen Dateiinhalte kann ich deren Übereinstimmung nicht prüfen. Die gemeldeten Läufe werden daher nicht als eigene Reproduktion ausgegeben.

Unabhängig davon wurden **11 eigene Prüfgruppen ausgeführt: 11/11 bestanden**. Sie prüfen konkrete mathematische Aussagen und Gegenbeispiele, nicht die unbekannten F08/F09-Implementierungen. Code und Messwerte stehen im beigefügten Verifikationsordner.

## 2. Was von Gemini verwendbar ist

| Vorschlag | Nutzen für den Formalismus | Erforderliche Präzisierung |
|---|---|---|
| PID und Redundancy Bottleneck | Quellenbeiträge genauer unterscheiden | Maß, Zielvariable, Ensemble und Optimierungsverfahren deklarieren; keine automatische Kausalitätsaussage |
| Sheaf-Kontextualität | Gemeinsame Darstellbarkeit lokaler Wahrscheinlichkeitsmodelle prüfen | Messidentitäten, Kontexte und Randverträglichkeit angeben; keine allgemeine Kennzahl für Mehrfachzugehörigkeit |
| Strukturierte Cospans | Schnittstellen und Zusammensetzung formalisieren | Typen und physische Semantik zuerst festlegen; kategoriale Komposition beweist keine dynamische Verträglichkeit |
| Netzwerksteuerbarkeit | Erreichbarkeit und mögliche Eingriffspunkte untersuchen | Beschränkte Eingriffe, Störungen, Beobachtbarkeit und Viabilität gesondert prüfen |

Die pauschale Einordnung als quantenmechanisch begründetes Gesamtgerüst oder als nun geschlossenes Axiomensystem wird durch diese Anschlüsse nicht getragen. Jeder Anschluss beantwortet eine bestimmte Frage unter eigenen Voraussetzungen.

## 3. F09: einen zusätzlichen Kopiertest aufnehmen

Für unabhängige faire Bits \(A,B\) und die unveränderte Ausgabe \(Y=(A,B)\) gilt:

\[
I(A;Y)=I(B;Y)=1,\qquad I(A,B;Y)=2.
\]

Williams–Beers \(I_{\min}\) liefert trotzdem:

\[
(R,U_A,U_B,S)=(1,0,0,1)\ \text{Bit}.
\]

Eigene Nachrechnung: Für jeden Zielwert liefert jede Quelle ein Bit spezifische Information. Deren Minimum ist ein Bit; die PID-Summenbeziehungen ergeben anschließend ein Bit Synergie. Die Blackwell-Redundanz ist hier dagegen null: Ein gemeinsamer nachgeschalteter Kanal müsste für alle vier Bitpaare gleichzeitig \(\alpha_a(q)=\beta_b(q)\) erfüllen. Damit ist er unabhängig vom Ziel.

Das ist kein automatischer Implementierungsfehler von \(I_{\min}\). Es zeigt, dass seine Bezeichnungen nicht maßunabhängig gelesen werden dürfen. Dieser bekannte Kopierfall motiviert auch das Identitätsaxiom in alternativen PID-Konstruktionen. [Harder, Salge und Polani, 2013](https://arxiv.org/abs/1207.2080).

**Empfehlung:** Neben der redundanten Kopie \(A=B=Y\) ausdrücklich TWO_BIT_COPY mit unabhängigem \(A,B\) prüfen. In Ergebnistabellen „\(I_{\min}\)-Synergie“ schreiben. Ein positiver Wert allein soll keine neu entstandene Wechselwirkung oder kausale Eigenständigkeit attestieren. Die gemeinsam berichteten I_min-Atome und RB-Werte dürfen sich unterscheiden, weil ihre Redundanzbegriffe verschieden sind.

### Die RB-Formel in Gemini ist nicht die von Kolchinsky

Geminis Bedingung

\[
I(A;Q)=I(B;Q)=I(A,B;Q)
\]

unter \(Q-(A,B)-Y\) ist eine andere Forderung. Bei unabhängigen fairen Eingangsbits zwingt sie den Kanal \(Q\mid A,B\) zur Konstanz. Für \(Y=A\land B\) ergibt sie daher null Zielinformation. Die beiden Quellkanäle über dieses AND-Ziel sind aber identisch und haben Blackwell-Redundanz \(0{,}311278\) Bit. Das wurde unabhängig nachgerechnet. Es ist ein Befund zu **Geminis Formel**, kein nachgewiesener Fehler in F09.

Kolchinskys Konstruktion verwendet eine Quellenidentität \(S\), eine daraus ausgewählte Beobachtung \(Z\) und ein Ziel \(Y\):

\[
\operatorname{RB}(R)=\max_{Q-(Z,S)-Y} I(Q;Y\mid S)
\quad\text{unter}\quad I(Q;S\mid Y)\le R.
\]

Dabei ist \(S\) unabhängig von \(Y\), und \(Z\mid(Y,S=s)\) entspricht dem jeweiligen Quellkanal. Die Quellengewichtung gehört zur Spezifikation. RB(0) entspricht der Blackwell-Redundanz. [Kolchinsky, 2024, Abschnitt II](https://arxiv.org/html/2405.07665v2).

Zwei Folgerungen sind für eine spätere Datenanwendung wichtig:

- Die Optimierung ist nicht pauschal als konvexes Maximierungsproblem oder LP ausweisbar. Schon Identitäts- und Bitflip-Kanal haben jeweils ein Bit Information, ihr gleichgewichtetes Gemisch null; die Zielfunktion ist in dieser Parametrisierung nicht konkav. Kolchinsky behandelt lokale Optima und mehrere Initialisierungen.
- RB(0) kann unter kleinen Verteilungsänderungen unstetig sein; die Arbeit zeigt dies an einer Kopierfamilie. Deshalb sollten RB(0), positive Relaxationsbudgets und Störungsempfindlichkeit getrennt berichtet werden. [Kolchinsky, Abschnitte III–IV](https://arxiv.org/html/2405.07665v2).

## 4. F08: die globale Zustandsannahme ausdrücklich markieren

FORMALISM §13 beschreibt Sichten durch \(Y_\alpha=\pi_\alpha(Z,c,t)\). Bei festgehaltenem Kontext und Zeitpunkt gilt: Sind alle als identisch bezeichneten Observablen gemeinsam definierte Funktionen desselben Zufallszustands, existiert ihre gemeinsame Verteilung bereits als Bildmaß. Ihre Kontextverteilungen besitzen damit eine globale Erweiterung.

**Folge:** Ein positiver Contextual-Fraction-Wert kann nicht zugleich aus genau diesem gemeinsamen Modell mit unveränderten Observablenidentitäten folgen. Er zeigt unter den gewählten empirischen Annahmen, dass diese Art globaler Darstellung nicht passt. Kontextabhängige Funktionen sind möglich; dann muss ausdrücklich geklärt werden, welche Größen über Kontexte hinweg noch als dieselbe Observable gelten.

Das ist der geeignete Anschluss an F08: ein Test einer globalen Darstellungsannahme. Stochastik oder die Zugehörigkeit zu mehreren Systemen allein erzeugen keine Kontextualität. Im Sheaf-Ansatz sind die lokalen Verteilungen und ihre Überschneidungen der Ausgangspunkt. [Abramsky und Brandenburger, 2011](https://arxiv.org/abs/1102.0264).

Für einen endlichen, normierten und randverträglichen Fall lässt sich CF als

\[
\mathrm{CF}(e)=1-\max_{b\ge0}\mathbf1^\top b,
\qquad Mb\le e
\]

berechnen; \(M\) ordnet globalen deterministischen Belegungen ihre lokalen Ereignisse zu. Die Interpretation setzt das deklarierte empirische Modell voraus. [Abramsky, Barbosa und Mansfield, 2017](https://arxiv.org/abs/1705.07918).

Eigene LP-Prüfung: klassische gemeinsame Verteilung CF=0, PR-Box CF=1 und eine ausdrücklich konstruierte Mischung aus PR-Box und weißem Rauschen mit Sichtbarkeit \(v=0{,}625\) ergeben CF=0,25. Das bestätigt einen Referenzfall, **nicht** die unbekannte CHSH-Tabelle eures Skripts.

Die Aussage in §13 „keine Modellierungslücke“ sollte daher bedingt formuliert werden:

> Für ein deklariertes, randverträgliches empirisches Modell kann das Fehlen einer globalen Verteilung eine Eigenschaft dieses Modells sein. Seine Interpretation setzt geprüfte Messidentitäten, Kontextbedingungen und eine Behandlung von Schätzfehlern voraus.

Unverträgliche empirische Ränder werden in unserer Referenzprüfung vor dem CF-Lauf zurückgewiesen. Bei Messdaten braucht es dafür einen offengelegten statistischen Umgang. Unterschiedliche Bestandsangaben, Drift oder irrtümlich gleichgesetzte Variablen werden nicht schon durch einen CF-Wert erklärt.

## 5. Steuerbarkeit, Viabilität und Kosten auseinanderhalten

Geminis Netzwerkanschluss ist nützlich; die Gleichsetzung mit Pufferfähigkeit trägt nicht.

Eigener Gegenfall:

\[
\dot x=x+u,\quad |u|\le0{,}25,\quad K=[-1,1].
\]

Das skalare lineare System besitzt vollen Kalman-Rang. Trotzdem gilt bei \(x=1\) selbst für den günstigsten Eingriff \(\dot x\ge0{,}75\). Der gesamte Bereich \(K\) ist unter diesem Budget nicht kontrolliert invariant. Umgekehrt bleibt bei \(\dot x=-x\), ohne Aktuator, jeder Start in \(K\) sicher: voller Steuerbarkeitsrang ist dafür nicht notwendig.

Strukturelle Steuerbarkeit betrifft zudem generische Parameterkonfigurationen unter ihren Strukturannahmen. Sie ersetzt keine Prüfung eines konkreten Systems mit gekoppelten Parametern und beschränkten Stellgrößen. [Liu, Slotine und Barabási, 2011](https://cdanfort.w3.uvm.edu/csc-reading-group/barabasi-network-controllability-nature-2011.pdf).

Auch gleiche Topologie bedeutet keine gleichen Eingriffskosten: Für \(\dot x=bu\), \(x(0)=0\), \(x(T)=1\) ist das minimale quadratische Stellmaß \(1/(b^2T)\). Eine Verringerung von \(b\) um Faktor zehn erhöht es um Faktor hundert. Erst eine physische Leistungsbilanz entscheidet, ob ein solches Stellmaß Energie darstellt.

Der natürliche Ausbau ist deshalb eine **aufgabenspezifische Transformation, die ausführbare sichere Eingriffe erhält**. Ein konkreter Vorschlag mit Beweis und Gegenbeispielen steht in [NEXT_EXTENSIONS_ACTION_AND_OPEN_SYSTEMS.md](NEXT_EXTENSIONS_ACTION_AND_OPEN_SYSTEMS.md).

## 6. Komposition braucht typisierte Schnittstellen

Für einen Funktor \(L:\mathcal A\to\mathcal X\) haben strukturierte Cospans die Form \(L(a)\to x\leftarrow L(b)\), mit \(a,b\in\mathcal A\) und \(x\in\mathcal X\). Geminis Form \(A\to L(x)\leftarrow B\) passt nicht zu dieser Typisierung. Geeignete Kolimitannahmen ermöglichen die Komposition. [Baez und Courser, 2020](https://arxiv.org/abs/1911.04630).

Die zusätzlich behauptete Äquivalenz zwischen einer Funktorrelation und \(DR\,F_{\mathrm{fine}}=F_{\mathrm{coarse}}\circ R\) folgt daraus nicht. Dazu fehlen insbesondere die Definition des Funktors auf dynamischen Objekten und die passende Semantik.

Verwendbar ist der konkrete Arbeitsauftrag: Schnittstellen tragen Einheiten, Richtungen, gemeinsam identifizierte Bestände, Flüsse, Eingriffsrechte und Budgets. Anschließend wird geprüft, ob ihre Komposition Bilanz, Zulässigkeit und die gewählte Transformationsrelation erhält. Eine Kategorie kann diese Regeln organisieren; sie ersetzt deren Nachweis nicht.

## 7. Kleine Korrekturen in den sichtbaren Übersichten

| Stelle | Präzisierung |
|---|---|
| README: „Revision 3“ | Aktuellen Stand als Revision 3.2 mit optionalen F08/F09-Ergänzungen kennzeichnen |
| README: CF „für stochastische Mehrfach-Systemzugehörigkeit“ | „Prüfung globaler Darstellbarkeit deklarierter lokaler Wahrscheinlichkeitsmodelle“ |
| README: PID „für EI_q“ | „PID einer deklarierten Quellen-Ziel-Verteilung; EI_q separat berichtet“ |
| FORMALISM: sechs Fälle; Literatur/Verifikation: sieben | Benannte Beispiele und Prüfgruppen anhand des tatsächlichen Skripts einheitlich zählen |
| Literatur: Viabilität nur skalar | Um das bereits vorhandene gekoppelte Pufferbeispiel ergänzen |
| Verifikation: „PID-Schätzer … nicht ausgeführt“ | Historischen Geltungsbereich Revision 3 angeben; späteren F09-Status separat belassen |
| Literatur: „Rosas-O-Information“ versus Rosas 2020 | O-Information und den PID-basierten Causal-Emergence-Ansatz bibliografisch trennen |

Die beiden Rosas-Anschlüsse sind verschiedene Arbeiten: [O-Information, 2019](https://arxiv.org/abs/1902.11239) und [Reconciling emergences, 2020](https://doi.org/10.1371/journal.pcbi.1008289). Diese Präzisierung verlangt keine Änderung eurer Entscheidung für I_min und RB.

Die im Manifest dokumentierte unveränderte Kernfassung während der ursprünglichen Modullieferung und die später sichtbare Einbindung widersprechen sich nicht zwingend. Lieferphase und Integrationsphase sollten getrennt datiert werden.

## 8. Reihenfolge der nächsten Arbeit

1. **Bestehende Schnittstellen schärfen:** globale Zustandsannahme/F08, maßspezifische PID-Aussagen, Kopiertest und eindeutige Testzählung.
2. **Handlungserhaltende Transformation ausarbeiten:** gemeinsamer ausführbarer Eingriff für alle noch möglichen Mikrorealisationen, einschließlich geteilter Budgets.
3. **Offene Komposition konkret rechnen:** einen Ressourcen- oder Wärmefall mit Randflüssen und überprüfbarer Bilanz.
4. **Erst danach Messdaten auswerten:** Unsicherheit, Kontextidentitäten, RB-Empfindlichkeit und unabhängige Validierung angeben.

Die dazugehörige Ausarbeitung erweitert bereits vorhandene Bedingungen VB3–VB5. Sie führt keine neue allgemeine Emergenzkonstante ein.

## 9. Reproduktion dieses Reviews

Im Paketverzeichnis:

~~~bash
python -m pip install -r verification/requirements_review.txt
python verification/verify_review_examples.py
~~~

Getestet mit Python 3.12.14, NumPy 2.3.5 und SciPy 1.17.0. Das Skript erzeugt verification/review_results.json und beendet sich bei Fehlern mit Exitcode 1.

| Prüfgruppe | Ergebnis / Bedeutung |
|---|---|
| r01 | I_min für UNIQUE, XOR, AND und redundante Kopie |
| r02 | Zwei-Bit-Kopie: maßabhängige Redundanz und Synergie |
| r03 | AND-Gegenfall zu Geminis RB-Formel |
| r04 | RB-Zielfunktion nicht allgemein konkav im Kanal |
| r05 | CF-Referenzmodelle und explizite verrauschte PR-Familie |
| r06 | Unverträgliche Ränder werden zurückgewiesen |
| r07 | Steuerbarkeitsrang und Invarianz sind verschiedene Anforderungen |
| r08 | Gleiche Topologie, unterschiedliche quadratische Stellkosten |
| r09 | Geschlossenheit unter gemittelter Politik erhält sichere Entscheidungen nicht |
| r10 | Informationsverlust verhindert gemeinsame Pufferzuteilung am Rand |
| r11 | Offene Wärme- und Entropiebilanz mit positivem internem Produktionsanteil |

Alle elf Gruppen bestanden beim dokumentierten Lauf. Endliche Rechenbeispiele ersetzen weder allgemeine Beweise noch empirische Validierung. Insbesondere wird kein vollständiger Viabilitätskern der Puffer berechnet.
