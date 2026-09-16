# Nächste Erweiterungen: ausführbare Transformationen und offene Systeme

Stand: 16. September 2026. Ergänzungsvorschlag zum sichtbaren Formalismus 3.2 mit F08/F09.

Diese Ausarbeitung vertieft VB3–VB5. Alle Zahlen sind deklarierte Modellwerte. Parameter dürfen von Einheit, Systemzugehörigkeit, Zustand, Kontext und Zeit abhängen. Keine der folgenden Beziehungen verlangt domänenübergreifend gleiche Werte.

## 1. Die zentrale Frage

Eine Transformation kann eine Vorhersage erhalten und trotzdem eine Entscheidung unmöglich machen. Deshalb sollte jede Transformation angeben:

1. Welche Zustände oder Beobachtungen sie zusammenfasst.
2. Welche Dynamik und welche Aufgabe erhalten bleiben sollen.
3. Welche Eingriffe nach der Transformation tatsächlich ausführbar sind.
4. Welche Informationen, Ressourcen und Metaregeln dafür verfügbar sind.

Der einschlägige Literaturanschluss sind Feedback Refinement Relations: abstrakte Controller werden unter präzisen Beziehungen auf konkrete Systeme übertragen, einschließlich ihrer Informationsanforderungen. [Reissig, Weber und Rungger, 2017](https://arxiv.org/abs/1503.03715).

Die nachstehende hinreichende Bedingung ist eine eigene, bewusst eingeschränkte Formulierung für diskrete Sicherheit. Sie beansprucht weder die Allgemeinheit noch eine neue Herleitung der gesamten dortigen Theorie.

## 2. Hinreichende Bedingung für die Übertragung sicherer Eingriffe

### 2.1 Festgelegtes Modell

Sei

\[
z_{n+1}\in F(z_n,u_n),\qquad u_n\in U(z_n).
\]

Die nichtleere Nachfolgermenge \(F\) enthält alle im Modell zugelassenen Störungen. Der konkrete sichere Bereich sei \(K\). Eine Projektion \(y=\pi(z)\) liefert den Zustand des abstrakten Modells

\[
y_{n+1}\in\widehat F(y_n,v_n),\qquad v_n\in\widehat U(y_n).
\]

Kontext, Zeit, Ressourcen und Regelzustände müssen in \(z\) enthalten sein, soweit sie für diese Beschreibung erforderlich sind. Die Abbildung \(\pi\) ist auf diesem erweiterten Zustand fest definiert. Unbekannte Komponenten dürfen nicht stillschweigend als beobachtet behandelt werden.

Die Eingriffsschnittstelle

\[
u=\iota(v,y)
\]

darf in dieser Fassung nur den gewählten Makroeingriff und den verfügbaren Makrozustand verwenden. Ein anderer Entwurf kann einen feineren lokalen Beobachter enthalten; dessen Information und Kosten gehören dann ausdrücklich zum Modell.

### 2.2 Drei zu prüfende Bedingungen

Für jeden \(y\in\widehat K\), jeden zugelassenen \(v\in\widehat U(y)\) und **jeden** konkreten Zustand \(z\) mit \(\pi(z)=y\):

\[
\begin{aligned}
\text{Ausführbarkeit:}\quad&
\iota(v,y)\in U(z),\quad F(z,\iota(v,y))\ne\varnothing,\\
\text{Nachfolgerverträglichkeit:}\quad&
\pi\bigl(F(z,\iota(v,y))\bigr)\subseteq\widehat F(y,v),\\
\text{Sichere Darstellung:}\quad&
\pi^{-1}(\widehat K)\subseteq K.
\end{aligned}
\]

Die letzte Bedingung verhindert, dass ein als sicher bezeichneter Makrozustand unerkannte unsichere Mikrorealisationen enthält. Man darf einen engeren erreichbaren Zustandsbereich benutzen, muss dann aber dessen Erreichbarkeit und Invarianz ebenfalls begründen.

Existiert eine Makropolitik \(\widehat\mu\), die für alle \(y\in\widehat K\) eine zulässige Aktion auswählt und

\[
\widehat F(y,\widehat\mu(y))\subseteq\widehat K
\]

erfüllt, dann hält

\[
u_n=\iota\bigl(\widehat\mu(\pi(z_n)),\pi(z_n)\bigr)
\]

jeden Start \(z_0\in\pi^{-1}(\widehat K)\) im konkreten sicheren Bereich.

**Beweis:** Der Eingriff ist für den tatsächlichen Zustand zulässig. Jeder mögliche konkrete Nachfolger projiziert in die abstrakte Nachfolgermenge, diese liegt in \(\widehat K\), und deren vollständiges Urbild liegt in \(K\). Dieselben Voraussetzungen gelten im nächsten Schritt erneut. Induktion liefert die Aussage für alle diskreten Zeiten.

Das ist eine hinreichende, möglicherweise konservative Garantie. Ohne solche Voraussetzungen beweist ein kleiner Vorhersagefehler keine sichere Übertragbarkeit einer Steuerung.

### 2.3 Warum der Quantor entscheidend ist

\[
\forall z\in\pi^{-1}(y)\;\exists u:\text{ sicher}
\quad\not\Rightarrow\quad
\exists u\;\forall z\in\pi^{-1}(y):\text{ sicher}.
\]

Links darf der Eingriff den unbekannten Mikrozustand kennen. Rechts muss derselbe auf Grundlage der tatsächlich vorhandenen Information gewählte Eingriff alle noch möglichen Zustände abdecken. Für einen Controller, der nur \(y\) sieht, ist diese zweite Forderung maßgeblich.

## 3. Durchgerechneter Gegenfall: perfekte gemittelte Geschlossenheit

Es gibt drei Zustände \(L,R,D\). \(L,R\) sind sicher, \(D\) ist ein absorbierender Fehlerzustand. Zwei Eingriffe haben folgende Wirkung:

| Zustand | Aktion a | Aktion b |
|---|---|---|
| L | L | D |
| R | D | R |
| D | D | D |

Die Projektion fasst \(L,R\) zum Makrozustand S zusammen; \(D\) bleibt F. Bei gleichverteilter Wahl von a und b gilt für die gemittelte Übergangsmatrix \(P\) exakt

\[
PC=CQ,\qquad
C=\begin{pmatrix}1&0\\1&0\\0&1\end{pmatrix},
\quad Q=\begin{pmatrix}1/2&1/2\\0&1\end{pmatrix}.
\]

Die Makrodynamik dieser gemittelten Politik ist also geschlossen. Mit Mikroinformation kann man in \(L\) immer a und in \(R\) immer b wählen und sicher bleiben. Wer nur S sieht, kann das nicht: Kein gemeinsamer Eingriff ist für beide Mikrorealisationen sicher. Randomisierung löst die Forderung nach garantierter Sicherheit ebenfalls nicht.

Der Schluss lautet präzise: Geschlossenheit unter **einer gemittelten Politik** garantiert keine Erhaltung der Möglichkeiten eines zustandsabhängigen Controllers. Für Steuerungsaufgaben sind die einzelnen Aktionen und ihre Informationsgrundlagen zu prüfen. Der Gegenfall wurde als r09 ausgeführt.

## 4. Anwendung auf die gekoppelten Puffer

Eine konkrete normierte Variante lautet:

\[
\begin{aligned}
\dot x_1&=-(x_1-0{,}2)-w_1+0{,}1(x_2-x_1)+u_1,\\
\dot x_2&=-(x_2-0{,}2)-w_2+0{,}1(x_1-x_2)+u_2,\\
0&\le w_i\le0{,}7,\qquad u_i\ge0,\qquad u_1+u_2\le0{,}6.
\end{aligned}
\]

Zustände und Zeit sind hier normiert; alle Koeffizienten beziehen sich auf diese Wahl. Betrachtet wird die untere Sicherheitsgrenze \(x_i\ge0\).

An den beiden Zuständen \((0,1)\) und \((1,0)\) sieht die Summenbeobachtung jeweils \(s=x_1+x_2=1\). Unter dem ungünstigsten zulässigen \(w_i\) sind die Randanforderungen:

| Tatsächlicher Zustand | Am aktiven Rand nötiger Eingriff |
|---|---|
| (0,1) | \(u_1\ge0{,}4\) |
| (1,0) | \(u_2\ge0{,}4\) |

Mit Kenntnis des jeweiligen Zustands ist die momentane Randbedingung erfüllbar. Ein für beide möglichen Zustände zugleich geeigneter Eingriff bräuchte \(u_1+u_2\ge0{,}8\), überschreitet also das gemeinsame Budget.

Die Summe hat zwar die geschlossene Gleichung

\[
\dot s=-s+0{,}4-(w_1+w_2)+(u_1+u_2),
\]

doch für lokale Sicherheit fehlt die Verteilung des Bestands. **Dies ist eine momentane Randprüfung, kein berechneter vollständiger Viabilitätskern.** Sie reicht aus, um die fehlende gemeinsame Aktionsmöglichkeit an den angegebenen Zuständen zu zeigen. Ausgeführt als r10.

Damit hat derselbe Gesamtbestand je nach Beobachtung und Systemanforderung unterschiedliche praktische Bedeutung. Die Erweiterung formalisiert genau diese Kontextabhängigkeit, ohne den Bestand selbst zu verdoppeln.

## 5. Information über ihre Bedeutung für Handlungen bewerten

Sei \(B_n\) die Menge der Zustände, die mit Beobachtungen, bisherigen Eingriffen und dem Störungsmodell noch vereinbar sind. Für eine ein-Schritt-Sicherheitsaufgabe definiere

\[
U_{\mathrm{safe}}(B_n)=
\bigcap_{z\in B_n}
\{u\in U(z):F(z,u)\subseteq K\}.
\]

Für eine fortdauernde Garantie muss zusätzlich die Nachfolgermenge der möglichen Zustände wieder in einen geeigneten kontrolliert invarianten Informationsbereich führen. Die bloße ein-Schritt-Bedingung liefert das nicht automatisch.

Bei unverändertem Modell und unveränderter Aufgabe folgt unmittelbar:

\[
B'_n\subseteq B_n
\quad\Longrightarrow\quad
U_{\mathrm{safe}}(B'_n)\supseteq U_{\mathrm{safe}}(B_n).
\]

Genauere Information kann also zusätzliche sichere Eingriffe ermöglichen; sie muss es nicht. Neue Information über eine für die Aufgabe irrelevante Variable verändert die Eingriffsmenge möglicherweise gar nicht.

Das gibt den drei Schichten eine konkrete gemeinsame Aufgabe:

| Schicht | Beitrag zu diesem Prüfvertrag |
|---|---|
| CREP | Welche Zustände oder Unterschiede kann die verfügbare Information auflösen? |
| UTAC | Welche dieser Unterschiede verändern Dynamik, Sicherheitsgrenzen oder Eingriffsbedarf? |
| AFET | Welche Eingriffe sind angesichts der Kopplungen, Ressourcen und gemeinsamen Beschränkungen ausführbar? |

PID kann anschließend untersuchen, wie mehrere Beobachtungen diese Unterscheidungen tragen. Daraus folgt keine Gleichheit von PID-Synergie, Viabilitätsgewinn und thermodynamischer Entropieproduktion. Sie werden an demselben Fall mit jeweils eigener Definition berichtet.

## 6. Selbstähnlichkeit über mehrere Transformationsstufen

Eine Transformation soll eine lesbare Spezifikation mitführen:

\[
\mathcal T=
(\pi,\iota,\text{Zeitabbildung},\text{Informationszugang},
\text{Aufgabe},\text{Fehlerbereich},\text{Geltungsbereich}).
\]

Bei ihrer Zusammensetzung sind Zustands- **und** Eingriffsschnittstellen zu verfolgen. Eine zusammengesetzte Zustandsabbildung allein genügt nicht: Benötigt ein untergeordneter Controller zusätzliche lokale Information, muss diese in der Hierarchie verfügbar sein. Unter Umständen ist eine verteilte Ausführung möglich, obwohl ein ausschließlich auf den obersten Makrozustand beschränkter Controller scheitert.

Die wiederkehrende Struktur liegt in der Art des Prüfvertrags. Die Funktionen, Ressourcen, Sicherheitsbereiche und zulässigen Fehler können auf jeder Ebene variieren. So lässt sich Johanns Selbstähnlichkeitsidee auf ausführbare Transformationen anwenden.

Für approximative Abbildungen kann eine deklarierte Nachfolgerfehlermenge verwendet werden. Eine hinreichende robuste Bedingung ist dann beispielsweise

\[
\pi(F(z,\iota(v,y)))\subseteq
\mathcal B_\varepsilon(\widehat F(y,v))
\subseteq\widehat K.
\]

Hier sind Metrik, Einheiten und Reichweite von \(\varepsilon\) anzugeben. Bei dieser Bedingung stammt die Garantie aus der vollständigen enthaltenen Fehlermenge; ein mittlerer Fitfehler reicht dafür nicht.

Wechselnde Metaregeln erhalten außerdem eigene Übergänge: Zulässigkeit des Wechsels, Zustandsrücksetzung und danach gültige Eingriffsrechte. Sicherheit in jedem isolierten Modus belegt noch keine Sicherheit unter beliebigen Wechseln.

## 7. Zweiter Ausbau: offene Schnittstellen mit Bilanz

Bevor eine allgemeine kategoriale Konstruktion eingeführt wird, sollte ein vollständiger physischer Fall spezifiziert werden. Pro Schnittstelle sind mindestens festzuhalten:

| Angabe | Beispiel |
|---|---|
| Größe und Einheit | Temperatur K; Wärmeleistung W |
| Richtung und Vorzeichen | positive Leistung in das Teilsystem |
| Bestandsidentität | derselbe Speicher wird nur einmal bilanziert |
| Kopplungsgesetz | \(j=k(T_2-T_1)\), \(k\ge0\), Einheit W/K |
| Gültigkeitsbereich | positive Temperaturen; deklarierte Materialannahmen |
| Eingriffe und Budgets | begrenzte Heizleistung, gemeinsame Energiequelle |
| Informationszugang | welche Temperaturen lokal oder global messbar sind |
| Zeit- und Regeländerungen | Abtastung, Umschaltung, Zustandsrücksetzung |

### 7.1 Zwei thermische Speicher mit Randflüssen

Für konstante Wärmekapazitäten \(C_i>0\), Temperaturen \(T_i>0\), Wärmeleitung \(k\ge0\) und von außen zugeführte Leistungen \(p_i\):

\[
C_1\dot T_1=k(T_2-T_1)+p_1,\qquad
C_2\dot T_2=k(T_1-T_2)+p_2.
\]

Mit Referenztemperatur \(T_*>0\) ergeben sich

\[
E=C_1T_1+C_2T_2,\qquad
S=C_1\ln(T_1/T_*)+C_2\ln(T_2/T_*),
\]

bis auf additive Referenzkonstanten. Direktes Differenzieren liefert

\[
\dot E=p_1+p_2,
\]

\[
\dot S=
\underbrace{k\frac{(T_1-T_2)^2}{T_1T_2}}_{\sigma_{\mathrm{int}}\ge0}
+\frac{p_1}{T_1}+\frac{p_2}{T_2}.
\]

Die Entropierate des offenen Teilsystems kann negativ sein, obwohl seine interne Produktion nichtnegativ ist. Energieerhaltung und Gesamtentropiebilanz verlangen die passenden Umgebungsbeiträge.

Eigener numerischer Fall: \(T_1=300\) K, \(T_2=310\) K, \(C_1=2\) J/K, \(C_2=3\) J/K, \(k=1\) W/K und \(p_1=p_2=-100\) W. Dann:

\[
\dot E=-200\ \mathrm W,\qquad
\sigma_{\mathrm{int}}=0{,}00107527\ \mathrm{W/K},
\qquad \dot S=-0{,}65483871\ \mathrm{W/K}.
\]

Nimmt ein Reservoir bei 200 K die abgegebene Wärme auf, gewinnt es \(1\) W/K Entropie. Die kombinierte Entropierate beträgt \(0{,}34516129\) W/K und ist positiv. Ein passiver thermischer Kontakt kann diese momentanen Leistungen bei den angegebenen Temperaturen realisieren. Dies ist eine Zustandsrechnung; konstante Entnahmeleistungen werden nicht für beliebig lange Zeiten oder bis \(T_i\le0\) postuliert. Ausgeführt als r11.

### 7.2 Was diese Komposition überprüfbar macht

Beim Zusammenfügen heben sich die inneren Wärmeleistungen in der Energiebilanz auf; die Randflüsse bleiben. Die positive Entropieproduktion des inneren Kontakts bleibt ebenfalls sichtbar. Für ein GENERIC-Modell des geschlossenen Verbunds wären seine eigenen strukturellen Bedingungen zusätzlich nachzuweisen; diese offene Bilanz allein liefert keine vollständige GENERIC-Repräsentation.

Für die Ressourcenpuffer kann entsprechend eine endliche Versorgungsquelle mit eigener Dynamik ergänzt werden. Die bisher vorgegebene Grenze \(u_1+u_2\le U\) wird dann aus einer modellierten Quelle und ihren Umwandlungsregeln abgeleitet. Dabei sind Eingriffsraten in Puffer-Einheiten erst nach einem expliziten Umwandlungsgesetz als elektrische oder thermische Leistung zu interpretieren.

## 8. Konkrete Abnahmebedingungen für den nächsten Stand

| Priorität | Ergänzung | Prüfung vor einer weitergehenden Aussage |
|---|---|---|
| 1 | F09: TWO_BIT_COPY und Maßkennzeichnung | I_min-Atome \((1,0,0,1)\), Blackwell-Redundanz 0; Unterschied erklärt |
| 1 | F08: gemeinsames Zustandsmodell und Kontextidentitäten | Gemeinsame Verteilung ergibt CF=0; unverträgliche Ränder werden erkannt |
| 2 | Ausführbare Transformation | Mindestens ein positiver Sicherheitsübertragungsfall plus r09/r10 als Gegenfälle |
| 2 | Informationsabhängige Eingriffe | Zustandsmenge, verfügbarer Beobachter und gemeinsames Budget ausdrücklich angegeben |
| 3 | Offene Ressourcenkomposition | Bilanz einschließlich Quelle, Randflüssen und Umwandlungsgesetz erfüllt |
| 3 | Empirische F08/F09-Anwendung | Stichprobenunsicherheit, RB-Empfindlichkeit und alternative Kontextzuordnungen geprüft |

Die beiden Referenzgegenfälle und die Wärmebilanz sind im beigefügten Skript ausgeführt. Der allgemeine Sicherheitssatz ist oben analytisch begründet. Eine Software zur automatischen Controller-Synthese, ein vollständiger Viabilitätskern und ein empirischer Schätzer sind damit noch nicht implementiert.

Die formale Erweiterung kann zunächst als eigene Sektion „Erhaltung ausführbarer Eingriffe“ in context_transformations.md und als Vertiefung von VB4–VB5 aufgenommen werden. F08/F09 müssen dafür weder ersetzt noch zu universellen Diagnosemaßen erklärt werden.
