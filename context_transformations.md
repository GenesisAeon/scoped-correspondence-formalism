# Transformation, Kontext und überlappende Systemzugehörigkeit

Revision 3.2, 16. September 2026. Kernerweiterung des [Formalismus](FORMALISM.md). Die Notation und Prüfverträge sind Projektdefinitionen; die ausdrücklich hergeleiteten Beziehungen sind begrenzte mathematische Aussagen. Die Erweiterung setzt Johanns Leitidee um: dynamische Beschreibungen können sich zusammensetzen, zerlegen und über mehrere Systemzusammenhänge transformieren. Wiederkehrende Muster werden untersucht, während Werte und Funktionen vom jeweiligen Zusammenhang abhängen dürfen.

## 1. Eine Einheit, mehrere Zusammenhänge

Eine Einheit e kann intern gegliedert und zugleich in mehreren Systemen α enthalten sein. Die Zugehörigkeitsrelation wird durch

\[
M_{e\alpha}(t)\in\{0,1\}
\]

notiert. Mehrere Einsen in einer Zeile sind erlaubt. Eine gewichtete Variante benötigt eine eigene Bedeutung ihrer Gewichte; sie sind nicht automatisch Wahrscheinlichkeiten oder Bestandsanteile. M beschreibt Beziehungen zwischen Einheiten und Systemen. Die Partitionsmatrix C einer Markov-Vergröberung ordnet dagegen **Zustände** zu Beobachtungsklassen zu. Beide Matrizen haben unterschiedliche Aufgaben.

Für einen gewählten Untersuchungsbereich sei z ein gemeinsamer, hinreichend detaillierter Zustand. Das verlangt keine Beschreibung des gesamten Universums. Eine Sicht auf System α lautet

\[
y_\alpha=\pi_\alpha(z,c,t),\qquad
\dot z=F(z,u,w,c,t),\qquad \dot c=G(c,z,u,w,t).
\]

c enthält modellierte Kontextgrößen, u Eingriffe und w Störungen. Ein extern vorgegebener Kontextverlauf kann stattdessen als Eingang behandelt werden. Die Grenze zwischen Zustand und Eingang gehört zur Modellentscheidung.

| Gegenstand | Beispiel derselben Einheit e | Was verschieden sein darf |
|---|---|---|
| Physischer Bestand | x_e in festgelegter Einheit | sein tatsächlicher zeitlicher Wert |
| Kontextbezogene Reserve | x_e−b_α und x_e−b_β | Schwellen und damit Reserven |
| Relative Rolle | x_e/Σ_(j∈α)x_j, sofern der Nenner positiv ist | Bezugsgruppe und Anteil |
| Dynamischer Einfluss | Beitrag zu F unter einer Kopplung | Nachbarn, Eingänge und Antwortfunktionen |
| Zulässige Handlung | u in einer kontextabhängigen Menge | Ressourcen, Verpflichtungen und Regeln |

Der Bestand x_e bleibt bei gleicher Messdefinition und demselben Zeitpunkt derselbe. Seine Reserve, Rolle und zulässige Verwendung sind kontextbezogene Größen. Zwei Zugehörigkeiten können auch identische Werte liefern; Variation wird ermöglicht, nicht vorgeschrieben.

## 2. Verträglichkeit gemeinsamer Größen

Wenn zwei Sichten dieselbe Größe enthalten, werden Rückabbildungen auf diese gemeinsame Größe angegeben:

\[
R_{\alpha e}(y_\alpha,c,t)
=R_{\beta e}(y_\beta,c,t)=x_e.
\]

Bei normierten Sichten können die angezeigten Zahlen unterschiedlich sein und dennoch dieselbe Größe rekonstruieren. Schätzungen aus verrauschten Daten benötigen statt exakter Gleichheit ein Mess- und Unsicherheitsmodell.

Aus beliebig gewählten lokalen Beschreibungen folgt nicht automatisch ein gemeinsamer Zustand. Die Menge verträglicher Kombinationen ist als Teilmenge ihres Produktraums zu prüfen. Beispielsweise lassen sich die drei Forderungen x=y, y=z und z=x+1 nicht gleichzeitig erfüllen. Eine widersprüchliche Kombination wird nicht durch eine zusätzliche Ebene aufgelöst; mindestens eine Annahme oder die Interpretation der Variablen muss sich ändern.

Eine additive Bilanz zählt jede physische Einheit einmal. Wenn x_e sowohl in einem Teilsystem als auch in dessen übergeordnetem System enthalten ist, dürfen beide Summen nicht ungeprüft addiert werden. Für disjunkte Teile sind Summen möglich, für überlappende Mengen benötigt man eine eindeutige Zuordnung oder eine passende Korrektur der Mehrfachzählung. Nichtadditive Größen wie Information oder Leistung brauchen jeweils ihre eigene Kompositionsregel.

## 3. Die Dynamik einer veränderlichen Darstellung

Für deterministische, differenzierbare Verläufe folgt direkt aus der Kettenregel:

\[
\dot y_\alpha
=D_z\pi_\alpha F+D_c\pi_\alpha G+\partial_t\pi_\alpha.
\tag{T1}
\]

Die letzten beiden Terme erfassen Änderungen des Zusammenhangs und der Darstellung. Sie sind auch dann relevant, wenn z gerade konstant bleibt. Für eine streng zunehmende Zeitvariable mit dτ/dt=a(z,c,t)>0 gilt entlang der Bahn

\[
\frac{dy_\alpha}{d\tau}
=\frac{D_z\pi_\alpha F+D_c\pi_\alpha G+\partial_t\pi_\alpha}{a}.
\tag{T2}
\]

a erhält die Einheit τ/Zeit; bei gleichartigen Zeitkoordinaten ist es ein Skalenverhältnis. Eine nur positive, aber gegen null strebende Zeitskalierung kann einen unendlichen Zeithorizont auf einen endlichen abbilden. Für Vergleiche über ganze Horizonte werden deshalb geeignete Schranken für a angegeben.

**Eigene Beispielrechnung.** Sei y=(x−b(t))/s(t) mit s(t)>0. Dann

\[
\dot y=\frac{\dot x-\dot b}{s}-y\frac{\dot s}{s}.
\]

Bei x=1, b=t, s=1+t ist y=(1−t)/(1+t) und y′=−2/(1+t)², obwohl x′=0. Die geänderte Reserve ist real für die geänderte Anforderung; sie behauptet keine Veränderung des Bestands.

T1–T2 sind Aussagen über differenzierbare deterministische Modelle. Ereignisse benötigen Resetregeln. Stochastische Modelle benötigen eine für ihren Prozesstyp korrekte Transformation; die deterministische Kettenregel wird nicht ungeprüft übertragen.

## 4. Wann eine Sicht eine eigene Entwicklung besitzt

Eine Sicht ist relativ zu ihren angegebenen Eingängen geschlossen, wenn die rechte Seite von T1 ausschließlich aus y_α, diesen Eingängen und der Zeit bestimmbar ist. Ist der Kontext nicht sichtbar, muss seine Wirkung trotzdem so bestimmt sein oder durch zusätzliche Zustände, Eingänge beziehungsweise Gedächtnis vertreten werden.

Eine konkrete Prüfung vergleicht alle zulässigen Ausgangszustände, die dieselbe Sicht und dieselben sichtbaren Eingänge erzeugen: Liefern sie unterschiedliche Ableitungen, existiert für diese Darstellung keine eindeutige deterministische Markov-Dynamik. Ein Mittelwert ist eine zusätzliche Modellannahme. Auch gleiche Zustände bei verschiedenen, verborgenen Regelzuständen können diese Eindeutigkeit verletzen.

Bei einer vorgegebenen Kandidatendynamik g wird die Abweichung der transformierten Ableitung als Residuum dokumentiert. Eine kleine lokale Abweichung ist erst zusammen mit einem Horizont und einer Fehlerfortpflanzung aussagekräftig. [Geschlossenheit, Fehler und Emergenz](emergence_and_closure.md) präzisiert diese Tests.

## 5. Zusammensetzen und Zerlegen

Eine feinere Beschreibung \(\xi=(\xi_1,\ldots,\xi_n)\) realisiert eine gröbere Einheit über z=R(ξ). Soll z einer vorgegebenen autonomen Dynamik F folgen, ist im glatten, zeitunabhängigen Fall

\[
DR(\xi)\,F_{fine}(\xi)=F(R(\xi))
\tag{T3}
\]

zu prüfen. Bei Eingängen kommen deren Abbildungen hinzu, bei veränderlichem R die Terme aus T1. T3 ist eine Verträglichkeitsbedingung, kein Existenzbeweis für beliebige Zerlegungen.

Ein leicht prüfbares Muster ist eine Bestandsbilanz. Für x=p+q und

\[
\dot p=a_p-\ell_p-j,\qquad
\dot q=a_q-\ell_q+j
\]

folgt \(\dot x=a_p+a_q-\ell_p-\ell_q\): der interne Austausch j fällt aus der äußeren Bilanz. Ob diese Bilanz **geschlossen in x** ist, hängt weiterhin davon ab, ob die verbleibenden Terme aus x und den angegebenen Eingängen berechnet werden können. Verschiedene Verlustraten können die interne Verteilung wieder relevant machen.

Dieses Bilanzmuster lässt sich über mehrere Ebenen wiederholen. Die konkreten Zuflüsse, Verluste und Austauschgesetze dürfen auf jeder Ebene andere Funktionen sein. Damit wird ein selbstähnliches Kompositionsmuster präzisiert, ohne die gesamten Modelle gleichzusetzen.

Eine viele-zu-eins-Abbildung R besitzt gewöhnlich keine eindeutige Umkehrung. Zerlegung benötigt zusätzliche Information oder eine deklarierte Anhebung, etwa eine Verteilung über mit z verträgliche Feinzustände. Gleiches grobes Verhalten kann durch verschiedene innere Mechanismen entstehen.

### Fehler bei mehreren Transformationsschritten

Für autonome glatte Modelle setze

\[
r_{ji}=DT_{ji}f_i-a_{ji}f_j\circ T_{ji},\qquad
r_{kj}=DT_{kj}f_j-a_{kj}f_k\circ T_{kj}.
\]

Dann besitzt \(T_{ki}=T_{kj}\circ T_{ji}\) den Zeitfaktor \(a_{ki}=a_{ji}(a_{kj}\circ T_{ji})\) und das Residuum

\[
r_{ki}=(DT_{kj}\circ T_{ji})r_{ji}
        +a_{ji}(r_{kj}\circ T_{ji}).
\tag{T4}
\]

Das folgt durch Einsetzen und die Kettenregel. Mit verträglichen Normen, \(\|DT_{kj}\|\le M\), \(a_{ji}\le A\) und \(\|r_{ji}\|\le\epsilon_1\), \(\|r_{kj}\|\le\epsilon_2\) ergibt sich \(\|r_{ki}\|\le M\epsilon_1+A\epsilon_2\). Voraussetzungen gelten auf den tatsächlich erreichten Gebieten. Starke Verzerrung kann Fehler verstärken; gute Nachbarvergleiche allein garantieren keine gute Beschreibung über viele Ebenen.

## 6. Einflüsse, Beschränkungen und Metaregeln

Diese drei Aspekte erhalten verschiedene Stellen im Modell:

| Aspekt | Modellort | Konkretes Beispiel |
|---|---|---|
| Einfluss | F, G oder ein Übergangskern | Austausch k(x₂−x₁) |
| Beschränkung | Zustandsbereich K, Eingriffsmenge U | x_i≥b_i; u₁+u₂≤U |
| Metaregel | Regelzustand m, Auswahl- oder Updategesetz | Priorität, zulässiger Wechsel der Kopplung, Beobachtungsfreigabe |

Eine Metaregel kann fest sein oder sich selbst entwickeln, etwa über m′=H(m,z,c,u,t), einen diskreten Update oder ein Ereignis. Dann hängt F gegebenenfalls von m ab. Unbeobachtetes m kann eine sonst geschlossene Beschreibung ungeschlossen machen. Eine rein beschreibende Wahl des Beobachters verändert zunächst π; eine tatsächlich durchgesetzte Regel kann Eingriffe und dadurch den physischen Verlauf verändern.

Mehrere Zugehörigkeiten müssen mit **einem gemeinsam ausführbaren Eingriff** vereinbar sein. Für dieselbe physische Steuergröße wird die zulässige Menge aus den gleichzeitig geltenden Beschränkungen gebildet:

\[
\mathcal U_{joint}(z,c,m,t)
=\mathcal U_{physical}\cap\bigcap_\alpha\mathcal U_\alpha.
\tag{T5}
\]

Bei lokalen Steuerkoordinaten werden diese Mengen zuvor auf einen gemeinsamen Steuerraum zurückgezogen. Zusätzlich sind gekoppelte Ressourcenbedingungen zu berücksichtigen. Ein leerer Schnitt zeigt einen Regel- oder Ressourcenwiderspruch. Eine Prioritätsregel kann eine Anforderung ausdrücklich aufgeben; sie erfüllt dadurch nicht beide Anforderungen zugleich.

## 7. Anwendung auf CREP, UTAC und AFET

| Schicht | Erweiterte Aufgabe | Prüfbarer Gegenstand |
|---|---|---|
| CREP | Festlegen, welche kontextbezogenen Größen beobachtbar und aufgabengerecht sind | π_α, Messmodell, verlorene Information, Rekonstruktionsbedarf |
| UTAC | Dynamik und Handlungsfähigkeit unter Kontext und Regeln beschreiben | F, G, m, K, zulässige Eingriffe und Zeithorizont |
| AFET | Gleichzeitige Zugehörigkeiten und tatsächliche Kopplungen konsistent zusammensetzen | gemeinsame Variablen, Flüsse, Bilanz und gekoppelte Ressourcenbedingungen |

Thermodynamische Spezialmodelle benötigen weiterhin ihre eigenen Bilanz- und Entropiebedingungen. Eine Zugehörigkeitsrelation allein ist kein thermodynamischer Kopplungskoeffizient.

Der Arbeitsvertrag für eine konkrete Selbstähnlichkeitsbehauptung enthält Ausgangs- und Zielmodell, Darstellung, Eingangsabbildung, Einheiten, Zeitbezug, veränderliche Parameter beziehungsweise Regeln, Geltungsgebiet und das erhaltene Muster. Hinzu kommen Fehler und unabhängige Prüffälle. Die Abbildungen werden nicht nach jedem Gegenbefund beliebig neu gewählt.

Das [gekoppelte Pufferbeispiel](worked_example_viability.md) führt diese Erweiterung vollständig durch: eine Einheit als intern teilbares System, überlappende Aufgaben, gemeinsame Ressourcen, geschlossene Summendynamik und ein zusätzlich benötigter Verteilungszustand. Die [Prüfübersicht](TRANSFORMATION_VERIFICATION.md) trennt Herleitungen, numerische Kontrollen und noch offene empirische Anwendungen.

## 8. Erhaltung ausführbarer Eingriffe (Vertiefung von VB3–VB5, Review 16. September 2026)

Eine Transformation kann eine Vorhersage erhalten und trotzdem eine Entscheidung unmöglich machen. Für ein konkretes Modell \(z_{n+1}\in F(z_n,u_n)\), \(u_n\in U(z_n)\), einen sicheren Bereich K und eine Projektion \(y=\pi(z)\) mit abstraktem Modell \(y_{n+1}\in\widehat F(y_n,v_n)\) und Eingriffsschnittstelle \(u=\iota(v,y)\):

**Hinreichende Bedingung.** Gilt für jedes \(y\in\widehat K\), jedes zulässige \(v\in\widehat U(y)\) und **jeden** konkreten Zustand z mit \(\pi(z)=y\):

\[
\begin{aligned}
\text{Ausführbarkeit:}\quad&\iota(v,y)\in U(z),\ F(z,\iota(v,y))\ne\varnothing,\\
\text{Nachfolgerverträglichkeit:}\quad&\pi(F(z,\iota(v,y)))\subseteq\widehat F(y,v),\\
\text{Sichere Darstellung:}\quad&\pi^{-1}(\widehat K)\subseteq K,
\end{aligned}
\]

und existiert eine Makropolitik \(\widehat\mu\) mit \(\widehat F(y,\widehat\mu(y))\subseteq\widehat K\) für alle \(y\in\widehat K\), dann hält \(u_n=\iota(\widehat\mu(\pi(z_n)),\pi(z_n))\) jeden Start \(z_0\in\pi^{-1}(\widehat K)\) im konkreten sicheren Bereich (Beweis durch Induktion: Ausführbarkeit + Nachfolgerverträglichkeit + sichere Darstellung übertragen sich Schritt für Schritt).

**Warum der Quantor entscheidend ist:**

\[
\forall z\in\pi^{-1}(y)\;\exists u:\text{ sicher}
\quad\not\Rightarrow\quad
\exists u\;\forall z\in\pi^{-1}(y):\text{ sicher}.
\]

Ein Controller, der nur y sieht, braucht die rechte, stärkere Aussage — ein für jeden möglichen Mikrozustand einzeln sicherer Eingriff genügt nicht, wenn er sich je nach Mikrozustand unterscheiden müsste.

### Drei durchgerechnete Gegenfälle (verifiziert, siehe unten)

1. **Perfekte gemittelte Geschlossenheit reicht nicht** (r09): drei Mikrozustände L, R, D (D absorbierend/unsicher); zwei Aktionen a, b mit L→L/R→D unter a und L→D/R→R unter b. Bei gleichverteiltem Zufallseingriff ist die gemittelte Makrodynamik exakt PC=CQ-geschlossen (selbst nachgerechnet: exakte Übereinstimmung). Mit Mikroinformation bleibt man für immer sicher (in L stets a, in R stets b). Ein Controller, der nur den Makrozustand {L,R} sieht, hat **keinen** gemeinsam sicheren Eingriff — Geschlossenheit unter einer gemittelten Politik erhält nicht die Handlungsmöglichkeiten eines zustandsabhängigen Controllers.
2. **Gekoppelte Puffer, gemeinsames Budget** (r10): zwei Bestände mit Austausch und Störung, Eingriffsbudget \(u_1+u_2\le0{,}6\). An den Zuständen (0,1) und (1,0) zeigt die Summenbeobachtung jeweils s=1 — nicht unterscheidbar. Der jeweils nötige Eingriff ist einzeln erfüllbar (\(u_1\ge0{,}4\) bzw. \(u_2\ge0{,}4\)), gemeinsam aber nicht (\(u_1+u_2\ge0{,}8>0{,}6\)) — selbst nachgerechnet: exakte Übereinstimmung. Die Summe hat eine geschlossene Gleichung, für lokale Sicherheit fehlt aber die Verteilung des Bestands.
3. **Offene Wärmebilanz mit Randflüssen** (r11): zwei gekoppelte Wärmespeicher, \(\dot S=\sigma_{int}\ge0\) plus Randterme \(p_i/T_i\) — die Entropierate des offenen Teilsystems kann negativ sein, obwohl die interne Produktion nichtnegativ bleibt. Zeigt, dass Komposition die inneren Flüsse aus der äußeren Bilanz herausfallen lässt, während die interne Entropieproduktion sichtbar bleibt.

**Konsequenz für die drei Schichten:** CREP klärt, welche Zustandsunterschiede die verfügbare Information überhaupt auflösen kann; UTAC, welche dieser Unterschiede Dynamik, Sicherheitsgrenzen oder Eingriffsbedarf verändern; AFET, welche Eingriffe angesichts Kopplungen, Ressourcen und gemeinsamer Beschränkungen tatsächlich ausführbar sind. PID (F09) kann untersuchen, wie mehrere Beobachtungen zu diesen Unterscheidungen beitragen — daraus folgt keine Gleichheit von PID-Synergie, Viabilitätsgewinn und thermodynamischer Entropieproduktion; sie werden am selben Fall mit je eigener Definition berichtet.

Vollständige Herleitung, Beweis und alle elf zugehörigen Prüfungen: [reviews/formalism-review-f08-f09/NEXT_EXTENSIONS_ACTION_AND_OPEN_SYSTEMS.md](reviews/formalism-review-f08-f09/NEXT_EXTENSIONS_ACTION_AND_OPEN_SYSTEMS.md) und [reviews/formalism-review-f08-f09/verification/verify_review_examples.py](reviews/formalism-review-f08-f09/verification/verify_review_examples.py) (11/11, von Claude unabhängig nachgerechnet). Dies ist ein Erweiterungsvorschlag, noch nicht Teil der Kern-Verifikationssuite.
