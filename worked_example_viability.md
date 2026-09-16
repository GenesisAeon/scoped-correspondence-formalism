# Worked Example — Pufferfähigkeit, Transformation und gemeinsame Ressourcen

Revision 3.2, 16. September 2026. Synthetische Modelle mit vollständigen Annahmen und eigenen Ableitungen. Das Beispiel vertieft UTAC-Pufferfähigkeit und wendet die [Kernerweiterung zu Transformation und Kontext](context_transformations.md) an. Es ist kein kalibriertes Klima-, biologisches oder wirtschaftliches Modell.

## 1. Was hier mit Viabilität gemeint ist

Ein zulässiger Zustandsbereich K beschreibt die zu schützende Aufgabe. Für einen Horizont H interessiert die Menge der Anfangszustände, von denen eine **gemeinsam ausführbare, nicht vorausschauende Steuerstrategie** den Zustand unter allen zugelassenen Störungsverläufen bis H in K halten kann. Das ist hier die Definition des robusten Viabilitätskerns für die angegebene Informations- und Eingriffsstruktur.

Wir unterscheiden die Existenz einer geeigneten Strategie, die Sicherheit einer tatsächlich gewählten Strategie und die Invarianz des **gesamten** Bereichs K. Der sichere Bereich selbst muss nicht vollständig viabel sein. Aussagen für einzelne Anfangszustände, einen endlichen Horizont und unbegrenzte Zeit sind verschieden.

In den folgenden konstanten Modellen existieren eindeutige globale Lösungen für beschränkte messbare Eingänge. Die analytischen Garantien benötigen keine Beobachtung der zukünftigen Störung. Allgemeine Barrierenverfahren untersuchen Randrichtungen und zulässige Rückkopplungen unter entsprechenden Regularitäts- und Durchführbarkeitsbedingungen. [Ames et al., 2019](https://arxiv.org/abs/1903.11199).

## 2. Skalarer Ausgangsfall

\[
\dot z=-r(z-z_{eq})+u-w,\qquad r>0,
\quad 0\le u\le U,\quad 0\le w\le W,\quad K=[b,\infty).
\]

z, z_eq und b sind Bestandsgrößen; r hat die Einheit 1/Zeit; u,w,U,W sind Bestandsraten. z_eq ist das unbelastete Referenzniveau. Die lokale Rückkehrrate bei konstanten Eingaben ist r. Sie bleibt unverändert, wenn die Belastung die Gleichgewichtslage über die zulässige Grenze verschiebt.

Am Rand z=b liefert die stärkste zulässige Maßnahme gegen die stärkste Belastung

\[
\dot z\big|_{b,u=U,w=W}=r(z_{eq}-b)+U-W.
\]

Ist dieser Ausdruck nichtnegativ, hält u=U den gesamten Bereich K unter jeder messbaren Belastung w(t)∈[0,W] invariant. Ist er negativ, treibt w=W bereits vom Rand aus nach außen, selbst bei maximalem Eingriff. Damit ist für dieses Modell die Bedingung notwendig und hinreichend für robuste kontrollierte Invarianz des gesamten K.

\[
W_{crit}=r(z_{eq}-b)+U
\]

ist die maximal dauerhaft abfangbare Belastungsrate des gesamten Bereichs, sofern W_crit≥0. Bei W_crit<0 ist selbst W=0 am Rand nicht dauerhaft abfangbar. W_crit ist weder eine Wahrscheinlichkeit noch ein Zustandsabstand.

### Gleiches Erholungsmaß, unterschiedliche Pufferfähigkeit

Für r=1, z_eq=1, b=0, U=0 und z(0)=1, in deklarierten Bestand-/Zeiteinheiten:

| Konstante Belastung | Gleichgewicht | Verlauf |
|---|---|---|
| w=0,5 | z*=0,5 | z(t)=0,5+0,5e^(−t), bleibt zulässig |
| w=1,5 | z*=−0,5 | z(t)=−0,5+1,5e^(−t), erreicht b bei ln 3 und unterschreitet b danach |

Allgemeiner ist unter u=U und w=W das Gleichgewicht \(z_*=z_{eq}+(U-W)/r\). Bei \(z_*<b<z_0\) gilt für den ersten Grenzkontakt

\[
t_{hit}=\frac1r\log\frac{z_0-z_*}{b-z_*}.
\tag{V1}
\]

Für z_*=b wird b von innen nur asymptotisch erreicht. V1 erklärt, warum eine nicht dauerhaft abfangbare Belastung trotzdem zeitweise erträglich sein kann.

## 3. Zwei gekoppelte Bestände unter mehreren Anforderungen

Die Zustände x₁ und x₂ haben dieselbe Bestandseinheit. Jeder Bestand kann intern weiter aufgeschlüsselt werden; zugleich wirken eine lokale Versorgungsaufgabe, eine übergreifende Reserveanforderung und ein gemeinsames Eingriffsbudget auf ihn. Diese Zugehörigkeiten müssen keine disjunkten Teile eines Baums sein.

Alle folgenden Zahlenbeispiele verwenden eine feste Bestandseinheit BE und Zeiteinheit ZE; Bestände werden in BE, r_i und k in ZE⁻¹ und Eingriffs-/Belastungsraten in BE/ZE angegeben.

Das gemeinsame physische Modell ist

\[
\begin{aligned}
\dot x_1&=-r_1(x_1-e_1)+u_1-w_1+k(x_2-x_1),\\
\dot x_2&=-r_2(x_2-e_2)+u_2-w_2+k(x_1-x_2),
\end{aligned}
\tag{V2}
\]

mit konstanten r_i>0, k≥0, 0≤w_i≤W_i und

\[
u_1\ge0,\quad u_2\ge0,\quad u_1+u_2\le U.
\tag{V3}
\]

e_i sind Referenzbestände, r_i und k Raten. Der Austausch kann in beide Richtungen fließen und bilanziert sich intern zu null. Das Modell setzt homogene Bestandseinheiten und diese lineare Austauschregel voraus. Ein thermodynamischer Entropienachweis ist damit nicht mitgeliefert.

Die lokalen Anforderungen seien x_i≥b_i. Ein weiterer Systemzusammenhang kann dieselben Bestände anhand von x₁+x₂≥B beurteilen. Für x₁=x₂=0,4, b₁=b₂=0,1 und B=1 sind beide lokalen Reserven 0,3 positiv, die gemeinsame Reserve −0,2 hingegen negativ. Bei B=0,5 ist sie positiv. Der physische Zustand ist in beiden Beurteilungen derselbe; die Aufgabe und ihre Grenze unterscheiden sich.

Ein systembezogener Anteil von x₁ kann sich ebenfalls ändern, wenn Bezugsgruppe oder andere Mitglieder wechseln. Eine solche Kennzahl wird weder nochmals als verfügbarer Bestand verbucht noch als zusätzlicher physischer Antrieb behandelt.

## 4. Summe und Verteilung als Transformation

Für r₁=r₂=r definiere

\[
s=x_1+x_2,\qquad d=x_1-x_2,
\quad v=u_1+u_2,\quad \omega=w_1+w_2.
\]

Addition und Subtraktion von V2 ergeben exakt

\[
\begin{aligned}
\dot s&=-r[s-(e_1+e_2)]+v-\omega,\\
\dot d&=-(r+2k)d+r(e_1-e_2)+(u_1-u_2)-(w_1-w_2).
\end{aligned}
\tag{V4}
\]

Die Summendynamik hat dasselbe Bilanzmuster wie der skalare Ausgangsfall und ist bei gegebenen v,ω geschlossen. Das ist ein exakter selbstähnlicher Kompositionsfall dieser Modellfamilie. Die unterschiedlichen Antriebe der Verteilung bleiben in d. Bei konstanten Eingaben sind die beiden Erholungsraten r und r+2k; die Wahl einer Sicht beeinflusst, welche Rate beobachtet wird.

Die vollständige Transformation ist invertierbar: x₁=(s+d)/2, x₂=(s−d)/2. Die Projektion auf s allein ist es nicht. Für b₁=b₂=0 gilt

\[
x_1\ge0\ \text{und}\ x_2\ge0
\quad\Longleftrightarrow\quad s\ge|d|.
\tag{V5}
\]

Die Zustände (0,5;0,5) und (−0,25;1,25) haben beide s=1, erfüllen die lokale Aufgabe aber unterschiedlich. Auch ein exakt prognostiziertes positives s kann eine lokale Grenzverletzung verdecken. Ein vorher festgelegter gültiger Bereich |d|≤D erlaubt stattdessen die robuste hinreichende Bedingung s≥D.

Eine Regel v=κ(s) schließt die Summendynamik auch unter dieser Rückkopplung. Eine Regel, die den Gesamtzufluss zusätzlich von d oder einem verborgenen Prioritätszustand abhängig macht, kann diese Schließung in s wieder verlieren. Geschlossenheit hängt daher ebenfalls von den geltenden Regeln ab.

### Ungleiche Raten machen die innere Verteilung dynamisch relevant

Setze \(\bar r=(r_1+r_2)/2\), \(\Delta r=(r_1-r_2)/2\) und

\[
B_s=r_1e_1+r_2e_2+v-\omega,\qquad
B_d=r_1e_1-r_2e_2+(u_1-u_2)-(w_1-w_2).
\]

Dann

\[
\dot s=-\bar r s-\Delta r d+B_s,\qquad
\dot d=-\Delta r s-(\bar r+2k)d+B_d.
\tag{V6}
\]

Bei r₁≠r₂ liefern gleiche Summen und gleiche sichtbare Eingänge im Allgemeinen verschiedene Summenableitungen. Beispielsweise erzeugen r₁=1, r₂=2, e_i=u_i=w_i=0 und die Zustände (1;0) bzw. (0;1) die Ableitungen −1 bzw. −2 bei s=1. Ein neu angepasster einzelner Ratenwert beseitigt diese Zustandsabhängigkeit nicht.

Mit λ=\bar r+2k lässt sich d exakt eliminieren:

\[
\dot s(t)=-\bar r s(t)+B_s(t)-\Delta r e^{-\lambda t}d(0)
+(\Delta r)^2\int_0^t e^{-\lambda(t-\tau)}s(\tau)\,d\tau
-\Delta r\int_0^t e^{-\lambda(t-\tau)}B_d(\tau)\,d\tau.
\tag{V7}
\]

Der Preis für das Weglassen von d sind Anfangsdatenabhängigkeit und Gedächtnis. Bei Rückkopplungen, in denen B_d selbst von versteckten Zuständen abhängt, ist deren Verlauf dadurch noch nicht bekannt. V7 folgt direkt durch Lösung der linearen d-Gleichung; der allgemeine Projektionsanschluss ist [Mori–Zwanzig](https://arxiv.org/abs/1611.06277).

## 5. Gemeinsame Viabilität ist eine gemeinsame Durchführbarkeitsfrage

Für den gesamten Bereich K={x₁≥b₁,x₂≥b₂} definiere

\[
a_i=\max\!\left(0,\ W_i-r_i(e_i-b_i)-k(b_j-b_i)\right),\qquad j\ne i.
\tag{V8}
\]

**Eigener Satz für V2–V3 mit konstanten Parametern:** Der gesamte Bereich K ist robust kontrolliert invariant genau dann, wenn

\[
a_1+a_2\le U.
\tag{V9}
\]

**Notwendigkeit:** Am gemeinsamen Eckpunkt (b₁,b₂) können beide Belastungen zugleich maximal sein. Beide Randableitungen müssen nichtnegativ sein. Das verlangt u_i≥a_i und damit V9.

**Hinreichend:** Wähle konstant u_i=a_i. An jeder Randfläche x_i=b_i ist x_j≥b_j. Wegen k≥0 ist die Ableitung dort mindestens r_i(e_i−b_i)+a_i−W_i+k(b_j−b_i)≥0. Äquivalent ergibt h_i=x_i−b_i ein lineares System mit nichtnegativen Kopplungen und nichtnegativem Antrieb; seine Lösung bleibt für h(0)≥0 nichtnegativ. Die konstante Steuerung ist gemeinsam zulässig und funktioniert für alle erlaubten Störungsverläufe.

Bei zusätzlichen Einzelgrenzen u_i≤U_i wird a_i≤U_i mitgefordert. V9 gilt für die ganze unbeschränkte untere Orthante und genau diese Modellannahmen. Es berechnet nicht automatisch den Viabilitätskern beliebiger zusätzlicher Anforderungen oder eines anderen Dynamikmodells.

### Konkreter Konflikt: einzeln möglich, gemeinsam unmöglich

Wähle r₁=r₂=1, e₁=e₂=0,2, b₁=b₂=0, W₁=W₂=0,7 und k=0,5. Dann ist a₁=a₂=0,5; das erforderliche gemeinsame Budget ist U=1.

| Situation | Erlaubte Unterstützung | Ergebnis am kritischen Rand |
|---|---|---|
| Teilaufgabe 1 isoliert bewertet | alleiniger Zugriff auf U=0,75 | 0,2+0,75−0,7=0,25: erfüllbar |
| Teilaufgabe 2 isoliert bewertet | alleiniger Zugriff auf dasselbe U=0,75 | ebenfalls erfüllbar |
| Beide gleichzeitig | u₁+u₂≤0,75 | Bedarf 0,5+0,5=1: nicht erfüllbar |
| Beide gleichzeitig | u₁+u₂≤1 | u₁=u₂=0,5 hält den gesamten Bereich sicher |

Die beiden isolierten Möglichkeiten dürfen nicht als gleichzeitig verfügbare Unterstützung addiert werden. In der gemeinsamen Aufgabe lautet die Anforderung „es gibt **einen** zulässigen Eingriff, der beide schützt“.

Auch große konstante k helfen am symmetrischen Eckpunkt nicht: Dort ist x₁=x₂ und der Austausch null. Kopplung verteilt vorhandene Bestände; sie erzeugt keinen zusätzlichen Bestand.

### Endlicher Puffer und optimale Grenzzeit im symmetrischen Fall

Bei U=0,75, x₁(0)=x₂(0)=1 und maximalen Belastungen liefert die symmetrische Maximalsteuerung u₁=u₂=0,375

\[
x_i(t)=-0,125+1,125e^{-t},\qquad t_{hit}=\log 9.
\tag{V10}
\]

Für jede zulässige Steuerung gilt gleichzeitig \(\dot s\le-s-0,25\), also \(s(t)\le-0,25+2,25e^{-t}\). Nach ln 9 wird die rechte Seite negativ. Dann können nicht beide Bestände nichtnegativ sein. Die symmetrische Strategie erreicht diese obere Schranke; ln 9 ist damit für diesen Anfangszustand die maximal garantierbare Dauer bis zum gemeinsamen Grenzkontakt. Für alle schwächeren Belastungen schützt dieselbe Strategie mindestens ebenso lange.

Die linearen Raten bleiben 1 und 2, auch wenn U verändert wird. Pufferfähigkeit und lokale Rückkehrmessung beantworten unterschiedliche Fragen.

## 6. Weiter zerlegen, ohne die Bilanz zu verdoppeln

Ein Bestand x₁ kann selbst ein System aus p und q sein, x₁=p+q. Mit interner Rate j und deklarierten Teilzuflüssen und Verlusten gilt

\[
\dot p=I_p-L_p-j,\qquad \dot q=I_q-L_q+j,
\quad \dot x_1=I_p+I_q-L_p-L_q.
\]

Damit diese feinere Realisierung V2 erfüllt, muss die letzte rechte Seite dessen erster Gleichung entsprechen. Das ist eine zusätzliche Kompatibilitätsanforderung. Aus x₁ allein lassen sich p und q nicht eindeutig bestimmen.

p kann zusätzlich einer quer zur bisherigen Zerlegung liegenden Funktionsgruppe angehören, etwa gemeinsam mit einem Teil von x₂. Diese neue Sicht darf andere Anforderungen und Messgrößen haben. Physische Kopplungen dieser Gruppe müssen im gemeinsamen feinen Modell bilanziert werden; sie werden nicht allein durch die Benennung der Gruppe erzeugt. Auch hier kann p selbst weiter zerlegt werden, sofern die jeweiligen Bilanz- und Transformationsbedingungen erfüllt sind.

## 7. Bewegliche Grenzen, veränderliche Regeln und endliche Eingriffsreserven

### Bewegliche Grenze und Normierung

Für \(h_i=x_i-b_i(t)\) ist die Randbedingung \(\dot x_i-\dot b_i\ge0\). Eine steigende Mindestreserve benötigt eine entsprechende zusätzliche Änderungsrate. Bei zeitabhängigen, extern vorgegebenen r_i,e_i,k,W_i,b_i mit k≥0 wird in V8 deshalb zusätzlich \(\dot b_i\) innerhalb der Klammer addiert. Sind die so erhaltenen a_i(t) messbar, ausführbar und erfüllen a₁(t)+a₂(t)≤U(t) fast überall, liefert u_i(t)=a_i(t) unter den üblichen Existenzbedingungen dieselbe Invarianzrechnung für die beweglichen Grenzen. Zustandsabhängige Koeffizienten benötigen eine erneute Prüfung über die gesamten Randflächen.

Für \(q_i=(x_i-b_i)/s_i(t)\), s_i>0, gilt

\[
\dot q_i=\frac{\dot x_i-\dot b_i}{s_i}-q_i\frac{\dot s_i}{s_i}.
\]

Ein kontextbezogener Reservewert kann sich ändern, obwohl der physische Bestand unverändert bleibt. Das muss beim Vergleich zwischen Systemzugehörigkeiten mitgeführt werden.

### Eine zusätzliche Gesamtanforderung

Fordert ein weiterer Zusammenhang s≥B(t), kommt am aktiven Rand die Bedingung \(\dot s-\dot B\ge0\) hinzu. Bei gleichem r lautet sie \(-r[B-(e_1+e_2)]+v-\omega-\dot B\ge0\). An einem Schnitt mehrerer aktiver Ränder muss derselbe Eingriff alle Bedingungen erfüllen. Die lokale Prüfung V9 allein deckt diese neue Aufgabe nicht ab.

### Regelwechsel

Eine Priorität kann bestimmen, wie ein knappes Budget verteilt wird. Sie macht ein Budgetdefizit nicht ungeschehen. Wechselt eine Anforderung sprunghaft, ist zusätzlich zu den Flussbedingungen die Sicherheit nach dem Wechsel zu prüfen: Ein plötzlich erhöhtes b kann den aktuellen Zustand sofort unzulässig machen, auch wenn er direkt zuvor sicher war. Bei einem physischen Reset muss dessen Zustandsabbildung ebenfalls geprüft werden.

### Ratenbudget und Bestandsbudget

V3 beschränkt die momentane Rate. Stammt der Eingriff aus einem endlichen Vorrat q, muss dieser zusätzlich modelliert werden, beispielsweise

\[
\dot q=-(u_1+u_2),\qquad q\ge0.
\]

Im Zahlenbeispiel aus Abschnitt 5, mit maximalen Belastungen, ist \(D=W_1+W_2-r(e_1+e_2)=1\) eine positive Defizitrate. Dann gilt

\[
\frac{d}{dt}(s+q)=-rs-D\le-D
\]

solange beide Bestände sicher sind. Somit ist \(H\le(s(0)+q(0))/D\) eine notwendige obere Schranke einer garantierten Dauer. Selbst U≥1 erlaubt mit endlichem q(0) ohne Nachlieferung keine unbegrenzte Sicherheit. Die Schranke muss nicht erreichbar sein; Verteilungs- und Ratenbeschränkungen können früher begrenzen. q ist hier ein eigener Vorrat, keine nochmalige Buchung von x₁ oder x₂.

## 8. Einordnung und Prüfung

Das Beispiel liefert ein zusammenhängendes Transformationsmuster: lokale Bestände werden zusammengesetzt, die Summe wird als eigene Einheit beschrieben, die interne Verteilung wird bei Bedarf wieder hinzugefügt, und gemeinsam genutzte Ressourcen verbinden mehrere Aufgaben. Wiederkehrend ist die Bilanzstruktur; die jeweiligen Dynamiken, Werte und Regeln bleiben modellabhängig.

Die neue [Prüfübersicht](TRANSFORMATION_VERIFICATION.md) dokumentiert unabhängige numerische Kontrollen der Ableitungen, erreichbare Randfälle, Ressourcenkonflikte und Gegenfälle zur Schließung. Die analytischen Invarianz- und Unmöglichkeitsargumente stehen oben; ein diskretes Simulationsraster allein wäre dafür kein Beweis.

Für eine empirische Anwendung sind Bestandsmessung, Zeitmaßstab, Störungsmenge, Regelzustände, Eingriffsverzögerung und tatsächlich verfügbare Ressourcen zu bestimmen. Zu berichten sind mindestens Reserve, lokale Raten, gemeinsame Machbarkeit, Zeithorizont und Unsicherheit. Die Rechnung leitet den bisherigen Frame-Score weder her noch kalibriert sie ihn.
