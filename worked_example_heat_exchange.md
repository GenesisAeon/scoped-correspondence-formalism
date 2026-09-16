# Gerechnetes Beispiel: zwei thermisch gekoppelte Körper

Revision 3, 16. September 2026. Das Modell aus Revision 2 wird um die GENERIC-Darstellung ergänzt. Status: analytisches Modell mit synthetischer Prüfung. Kein Fit an Messdaten und keine empirische Bestätigung von AFET.

## 1. System und Voraussetzungen

Zwei intern homogene Körper besitzen positive, konstante Wärmekapazitäten C_A,C_B [J/K] und Temperaturen T_A,T_B [K]. Sie tauschen Wärme über einen Leitwert G>0 [W/K] aus. Das Gesamtmodell ist thermisch isoliert; Volumenänderungen, Arbeit und Stoffaustausch werden ausgeschlossen. Die lineare Leitwertannahme wird für den betrachteten Temperaturbereich als Modell gesetzt.

Der Wärmestrom J [W] ist positiv von A nach B:

\[
J=G(T_A-T_B),\quad
C_A\dot T_A=-J,\quad C_B\dot T_B=J.
\]

Für konstante Wärmekapazitäten bleibt `E=C_A*T_A+C_B*T_B` erhalten, bis auf frei wählbare Energie-Nullpunkte.

## 2. Dynamische Stabilität

Die Differenz `Delta=T_A-T_B` erfüllt

\[
\dot\Delta=-G(1/C_A+1/C_B)\Delta.
\]

Daher ist ihre Rückkehrrate `S_rec,Delta=G*(1/C_A+1/C_B)` [1/s]. Das gemeinsame Gleichgewicht ist

\[
T_{eq}=\frac{C_AT_A(0)+C_BT_B(0)}{C_A+C_B}.
\]

Der vollständige Drift-Jacobian lautet

\[
A=\begin{pmatrix}-G/C_A&G/C_A\\G/C_B&-G/C_B\end{pmatrix}.
\]

Er ist bei C_A≠C_B asymmetrisch. Seine Eigenwerte sind 0 und `-G*(1/C_A+1/C_B)`. Der Nullmodus gehört zur Änderung der erhaltenen Gesamtenergie. Auf der Fläche fester Gesamtenergie klingt die Temperaturdifferenz ab. Das Beispiel zeigt, warum ein pauschaler größter Lyapunov-Exponent ohne Störungsraum die relevante Rückkehr verfehlen kann.

## 3. Entropiebilanz und Transportkoeffizient

Für beide Körper gilt `dS_th=dQ/T`. Damit ist die gesamte innere Produktion

\[
\dot S_{prod}=-J/T_A+J/T_B
=JX,\qquad X=1/T_B-1/T_A.
\]

X hat die Einheit 1/K. Aus dem gewählten Leitwertgesetz folgt für positive Temperaturen

\[
J=L(T_A,T_B)X,\quad L=G T_A T_B,\quad
\dot S_{prod}=\frac{G(T_A-T_B)^2}{T_A T_B}\ge0.
\]

L hat die Einheit W·K. Nahe T_A=T_B=T_0 ist der lineare Referenzkoeffizient `L_0=G*T_0^2`. Der zustandsabhängige Ausdruck ist eine Folge dieses speziellen Leitwertmodells; er macht die lineare Nahgleichgewichtstheorie nicht universell.

Dies ist ein einzelner Austauschkanal. Seine skalare Symmetrie prüft keine nichttriviale Kreuzreziprozität zwischen mehreren Flüssen. Die Asymmetrie von A widerspricht dem thermodynamischen Ansatz nicht: A und L stehen in unterschiedlichen Gleichungen und haben unterschiedliche Einheiten.

## 4. Zahlenbeispiel

Wähle C_A=2 J/K, C_B=5 J/K, G=3 W/K, T_A=310 K, T_B=290 K.

| Größe | Wert |
|---|---|
| Wärmestrom J | 60 W |
| thermodynamische Kraft X | `1/290-1/310 ≈ 0.0002224694` 1/K |
| Koeffizient L | 269700 W·K |
| innere Entropieproduktion | `1200/89900 ≈ 0.01334816` W/K |
| dynamischer Einfluss A_AB | 1,5 1/s |
| dynamischer Einfluss A_BA | 0,6 1/s |
| Rückkehrrate der Temperaturdifferenz | 2,1 1/s |
| Gleichgewichtstemperatur | `2070/7 ≈ 295.714286` K |

Die Gleichungen sind analytisch hergeleitet und im Verifikationsskript gegen Bilanz-, Vorzeichen- und Skalierungsbedingungen geprüft.

## 5. Selbstähnlichkeit ohne Größenidentität

Die Differenzentwicklung hat dieselbe mathematische Relaxationsform wie viele andere lineare Modelle. Mit `s=S_rec,Delta*t` und `q=Delta/Delta_0` wird sie zu `dq/ds=-q`. Das ist eine explizite Normierung dieser Modellklasse. G, C_A und C_B bleiben verschiedene physikalische Größen; die Normalform beweist keine gleiche mikroskopische Ursache in anderen Domänen.

Ein neuronales oder semantisches Relaxationsmodell kann unter eigener Normierung eine entsprechende Form besitzen. Ob die gemeinsame Normalform dort aus Daten gestützt wird und über lokale Linearisierung hinaus Vorhersagen ermöglicht, ist separat zu prüfen.

## 6. Informationsschicht

Temperaturmessungen können als Ausgaben `Y_A=T_A+epsilon_A`, `Y_B=T_B+epsilon_B` modelliert werden. Für Informationsraten braucht man zusätzlich Verteilungen, Abtastrate, Signalführung und Rauschmodell. Aus G allein ergibt sich keine Kanalkapazität und kein `eta_info`.

Im vorliegenden Wärmebeispiel bleiben K_info, R_info und eta_info deshalb nicht bestimmt. Das ist eine vollständige Angabe des Geltungsbereichs, keine Aufforderung, fehlende Größen aus einer Namensähnlichkeit zu ergänzen.

## 7. Ergänzung in Revision 3: explizite GENERIC-Struktur

Wähle die inneren Energien e_A=C_A T_A und e_B=C_B T_B als Zustände; die additiven Energienullen seien entsprechend festgelegt. Bei konstanten positiven Wärmekapazitäten und Temperaturen gilt mit T_ref>0:

\[
E=e_A+e_B,\qquad
S_{th}=C_A\ln(T_A/T_{ref})+C_B\ln(T_B/T_{ref}).
\]

Dann sind `grad E=(1,1)` und `grad S_th=(1/T_A,1/T_B)`. Wir setzen

\[
\mathbb J=0,\qquad
\mathbb M=G T_AT_B\begin{pmatrix}1&-1\\-1&1\end{pmatrix}.
\]

M hat die Einheit W·K und ist symmetrisch positiv-semidefinit. Für jeden Vektor v gilt `v^T M v=G*T_A*T_B*(v_A-v_B)^2≥0`. Außerdem ist M grad E=0. Mit J=0 sind Antisymmetrie, Jacobi- und Entropie-Degenerationsbedingung unmittelbar erfüllt.

Die dissipative Dynamik lautet exakt

\[
\mathbb M\nabla S_{th}=(-G(T_A-T_B),\;G(T_A-T_B))^T,
\]

also die Energiebilanz aus Abschnitt 1. Die Entropieproduktion ist wiederum `G*(T_A-T_B)^2/(T_A*T_B)`. Damit ist eine konkrete Zuordnung zum GENERIC-Modul hergestellt. Die Nullrichtung entspricht der erhaltenen Gesamtenergie.

Die Darstellung ist eine eigene Ableitung für dieses Wärmeleitungsmodell. Sie bestätigt keine GENERIC-Struktur der übrigen Pakete. Die Prüfung vergleicht Gradienten per finiten Differenzen, die Energieflüsse und die Entropieproduktion unabhängig voneinander. [Modul und Voraussetzungen](coupling_layer_afet.md).
