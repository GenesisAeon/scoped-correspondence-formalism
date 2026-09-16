# Worked Example — Makrodynamik, EI und spektrale Emergenz

Revision 3, 16. September 2026. Es handelt sich um synthetische, exakt definierte Markov-Ketten. Logarithmen für Informationen zur Basis 2; Einheiten Bit pro festgelegtem Schritt. Definitionen: [Emergenz und Geschlossenheit](emergence_and_closure.md).

## 1. Vier Mikrozustände, zwei geschlossene Makrozustände

\[
P=\begin{pmatrix}
1/3&1/3&1/3&0\\
1/3&1/3&1/3&0\\
1/3&1/3&1/3&0\\
0&0&0&1
\end{pmatrix},\qquad
C=\begin{pmatrix}1&0\\1&0\\1&0\\0&1\end{pmatrix}.
\]

Die Blöcke sind A={1,2,3}, B={4}. Die natürliche uniforme Präparation innerhalb der Blöcke ist

\[
\Lambda=\begin{pmatrix}1/3&1/3&1/3&0\\0&0&0&1\end{pmatrix}.
\]

ΛC=I₂, Q=ΛPC=I₂ und PC=CQ. Die Makrodynamik ist daher für jede Anfangsverteilung geschlossen. Dieses einfache redundante Kanalbeispiel liegt in derselben Beispielklasse wie die EI-Literatur; sämtliche Zahlen werden hier unabhängig aus der angegebenen Matrix berechnet.

### Zwei verschiedene Präparationsensembles

Uniform auf den Mikrozuständen gilt q_Z=(1/4,1/4,1/4,1/4). Die zukünftige Blockzugehörigkeit trägt

\[
EI_{unif}(P)=H_2(1/4)=0{,}811278124459\ldots
\]

Bit. Uniform auf den beiden Makrozuständen gilt dagegen q_M=(1/2,1/2), also EI_unif(Q)=1 Bit und ΔEI≈0,188722 Bit.

Die zu q_M passende Mikropräparation ist q_MΛ=(1/6,1/6,1/6,1/2). Unter **dieser selben Präparation** gilt EI_(q_MΛ)(P)=1 Bit: Die Vergröberung erzeugt keine zusätzliche Information. Der positive Unterschied oben entsteht beim Vergleich der beiden ausdrücklich verschieden gewichteten Kanäle.

Das Beispiel zeigt einen deklarierten Vorteil der Makrodarstellung und exakte Geschlossenheit. Aus zwei absorbierenden Makrozuständen folgt weder biologische Individualität noch ein universeller Kompositionsschwellenwert.

## 2. SVD-Größe mit einer unabhängigen Gegenprüfung

Mit s_i als Singularwerten schreiben wir zur Vermeidung einer Kollision mit der Paketgröße Γ:

\[
G_{\alpha,svd}=\sum_i s_i^\alpha,\qquad
\Delta G_{\alpha,svd}=G_{\alpha,svd}(1/r-1/N),
\quad r=\operatorname{rank}(P).
\]

Das ist die Rangfassung aus Definition 3 des SVD-Artikels. Bei verrauschten Daten wird r durch einen deklarierten Schwellenwert ersetzt; die Schwellenabhängigkeit wird mitberichtet. [Zhang et al., Gleichungen 7 und 11](https://www.nature.com/articles/s44260-025-00028-0).

Für P aus Abschnitt 1 sind die Singularwerte (1,1,0,0). Bei α=1 ist ΔG_svd=1/2. Das ist bereits numerisch eine andere Größe als ΔEI≈0,188722 Bit.

### Eigener Gegenfall: unabhängig gezogene Folgezustände

Setze P₀=11ᵀ/4, also alle Einträge gleich 1/4. Alle Zeilen sind identisch. Deshalb ist der Folgezustand unabhängig vom Anfangszustand, **für jede Präparationsverteilung**: EI_q(P₀)=0.

P₀ hat die Singularwerte (1,0,0,0), somit r=1 und ΔG_(1,svd)=1−1/4=3/4. Jede feste zustandsweise Partition hat ebenfalls identische Makroübergangszeilen und daher EI=0. Das Prüfskript kontrolliert dies für sämtliche 15 Partitionen der vier Zustände.

Der positive spektrale Wert erfasst nach dieser Definition entfernbare Redundanz; er genügt nicht als Nachweis eines positiven EI-Vorteils oder einer informativen autonomen Makroeinheit. Das ist eine begrenzte Aussage über die Interpretation des Maßes, keine pauschale Widerlegung des gesamten Artikels.

## 3. Reversibilität benötigt einen eigenen Begriff

\[
P_{cycle}=\begin{pmatrix}0&1&0\\0&0&1\\1&0&0\end{pmatrix}.
\]

P_cycle ist eine Permutationsmatrix mit stochastischer Inverser. Sie ist im Sinne der stochastischen Invertierbarkeit reversibel. Unter der stationären Verteilung μ=(1/3,1/3,1/3) ist jedoch

\[
\mu_1P_{12}=1/3\ne0=\mu_2P_{21}.
\]

Detailed Balance ist verletzt. Eine allgemein behauptete Implikation von stochastischer Invertierbarkeit auf stationäre Detailed Balance wäre falsch. Für thermodynamische Zeitumkehr können darüber hinaus Paritäten von Zustandsgrößen relevant sein; diese werden hier nicht modelliert. AFET darf aus einem hohen SVD-Wert keine Aussage über verschwindende Entropieproduktion ableiten.

## 4. Ein plausibler Makrokern kann trotzdem ungeschlossen sein

\[
P_{bad}=\begin{pmatrix}
0&0&1&0\\
0&0&0&1\\
1&0&0&0\\
0&1&0&0
\end{pmatrix},\qquad A=\{1,2,3\},\quad B=\{4\}.
\]

Von Mikrozustand 1 führt der nächste Schritt sicher nach A; von Mikrozustand 2 sicher nach B. Beide beginnen im selben Makrozustand A. Der Kern Q=ΛP_bad C existiert und ist zeilenstochastisch, aber PC≠CQ. Seine wiederholte Anwendung entspricht nicht allgemein der unbeeinflussten Makrobeobachtung.

Die Fehlergröße δ aus dem Methodendokument und die Schranke min(1,kδ) werden für mehrere Horizonte und alle reinen Anfangszustände geprüft. Zusätzlich wird der positive Fall PC=CQ über mehrere Schritte kontrolliert. Damit wird ein Makro-Ergebnis nicht allein aufgrund eines guten Informationsscores akzeptiert.

## 5. Was noch keine Replikation ist

Diese Rechnungen reproduzieren Definitionen und Grenzfälle auf kleinen Matrizen. Sie führen weder NIS+ aus noch reproduzieren sie die Datensätze oder vollständigen Versuchsreihen der zitierten Arbeiten. Empirische Anwendungen benötigen ein separat festgelegtes Beobachtungs- und Interventionsmodell.

Skript und Laufbericht: [VERIFICATION.md](VERIFICATION.md).
