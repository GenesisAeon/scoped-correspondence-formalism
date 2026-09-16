# AFET — Kopplungsschicht, Revision 2

Stand: 16. September 2026. AFET beschreibt hier Kopplungen mit explizitem Typ. Thermodynamik ist eine begründungspflichtige Spezialisierung. Notation: [FORMALISM.md](FORMALISM.md).

## 1. Drei Arten von Beziehung

| Typ | Nachweis | Was daraus noch nicht folgt |
|---|---|---|
| Informations-/Datenbeziehung | festgelegte Zufallsvariablen oder tatsächlicher Aufrufpfad | gerichtete physikalische Kausalität oder Entropieproduktion |
| Dynamische Kopplung | ein Zustand/Eingang verändert die zeitliche Entwicklung eines anderen | thermodynamischer Transportkoeffizient oder Reziprozität |
| Thermodynamische Kopplung | definierte Bilanz, Flüsse, konjugierte Kräfte und zulässige Stoff-/Energiegrößen | universelle Anwendbarkeit auf beliebige Software- oder semantische Kanten |

Die Typen können im selben Modell verbunden sein. Jede Verbindung braucht eine angegebene Abbildung mit Einheiten und Annahmen. Keine der drei Beschreibungen ersetzt die anderen automatisch.

## 2. Dynamische Kopplung

Ein möglicher Ansatz ist

\[
\dot z_i=f_i(z_i,u_i)+\sum_{j\ne i}g_{ij}(z_i,z_j,u).
\]

Die lokale Sensitivität `A_ij=partial(dot z_i)/partial z_j` hat die Einheit `[z_i]/([z_j]*Zeit)`. Eine gerichtete Einflussmatrix kann diese Dynamik approximieren. Eine reine Gewichtssumme in einer Registry ist zunächst ein Score, solange die Zuordnung zu einer zeitlichen Gleichung fehlt.

Bei der Codeprüfung werden Methodenvorhandensein und tatsächlicher Aufruf unterschieden. Ein verfügbarer Erholungsverlauf belegt nicht, dass er in `run_cycle()` mitläuft. Ein algebraischer Modulator kann ein reales Element des Datenflusses sein, ohne selbst ein zweites dynamisches System darzustellen.

## 3. Thermodynamischer Spezialfall

Wähle thermodynamische Zustandsgrößen und Bilanzgrenzen so, dass die **innere** Entropieproduktion als

\[
\dot S_{prod}=\sum_i J_i X_i
\]

geschrieben werden kann. Entropieströme durch die Systemgrenze sind gegebenenfalls gesondert zu bilanzieren; die Entropie eines offenen Teilsystems muss nicht monoton wachsen. X sind entropiekonjugierte Kräfte, nicht beliebige Zustands- oder Schwellenwertdifferenzen.

Nahe einem festgelegten Referenzzustand ist ein linearer Ansatz `J=LX` möglich. Die Einheiten folgen komponentenweise aus `[L_ij]=[J_i]/[X_j]`.

### 3.1 Zweiter Hauptsatz und Reziprozität unterscheiden

Zerlege `L=L_s+L_a`, wobei `L_s=(L+L^T)/2` symmetrisch und `L_a=(L-L^T)/2` antisymmetrisch ist. Dann gilt

\[
X^TLX=X^TL_sX,\qquad X^TL_aX=0.
\]

Nichtnegative Produktion für alle zulässigen Kräfte verlangt einen positiv-semidefiniten symmetrischen Anteil auf diesem Kraftraum. Bei Nebenbedingungen kann der zulässige Raum kleiner als der gesamte Koordinatenraum sein. Für unterschiedlich dimensionierte Komponenten sind Einheiten und gegebenenfalls eine konjugierte Normierung vor numerischen Eigenwertprüfungen festzulegen.

Onsager-Reziprozität ist eine zusätzliche Aussage bei passenden mikroskopischen Voraussetzungen. Zeitumkehrparitäten und zeitumkehrbrechende Felder können Onsager-Casimir-Beziehungen erforderlich machen. Die bloße Abwesenheit einer Rückkante in einem Softwaregraphen ist kein Test dieser Voraussetzungen. [Mielke, Peletier und Renger](https://arxiv.org/abs/1510.06219).

Beispiel für eine unzulässige pauschale Identifikation: Die gerichtete Matrix `[[0,1],[0,0]]` liefert für X=(1,−1) den Wert −1. Dagegen kann eine Matrix mit positivem symmetrischem und antisymmetrischem Anteil nichtnegative Produktion besitzen. Daher wird weder jede Asymmetrie verboten noch jede gerichtete Matrix thermodynamisch zugelassen.

### 3.2 Unterschiedliche Koeffizienten desselben physikalischen Prozesses

Zwei Körper mit Wärmekapazitäten C_A,C_B und Leitwert G können durch

\[
J=G(T_A-T_B),\quad C_A\dot T_A=-J,\quad C_B\dot T_B=J
\]

gekoppelt sein. Mit `X=1/T_B-1/T_A` ist `L(T_A,T_B)=G*T_A*T_B`, während der dynamische Einfluss auf die Temperatur beispielsweise `A_AB=G/C_A` ist. Diese Größen beschreiben denselben Prozess in verschiedenen Beziehungen, mit verschiedenen Einheiten. [Vollständige Rechnung](worked_example_heat_exchange.md).

## 4. Anschluss an Information und Panarchy

`eta_info` ist ein dimensionsloser Nutzungsgrad eines konkret definierten Informationskanals. `L_ij` ist ein Fluss/Kraft-Koeffizient. Eine Beziehung zwischen ihnen müsste zusätzlich Sensorik, Kodierung, Rauschen und den physikalischen Prozess modellieren. Eine reine Größenidentität wird zurückgenommen.

Panarchy dient als Begriff für skalenübergreifende Einwirkungen. Im konkreten Modell können diese etwa durch g_ij, einen Transferoperator oder beobachtete Abhängigkeiten beschrieben werden. Dafür gibt es im vorliegenden Rahmen keinen universellen Skalar.

## 5. Antwortfunktionen exp, tanh und Alternativen

Die Formwahl benötigt ein Modell oder einen transparenten empirischen Vergleich. Aktivierungsmodelle können exponentielle Temperaturabhängigkeiten begründen; bestimmte statistische Zwei-Zustands-Modelle liefern tanh-Antworten. Beschränktheit und die Einheit einer Observable reichen dafür nicht aus.

Eine exponentielle **Zeitentwicklung** aus `dot y=-y/tau` ist zudem nicht dasselbe wie eine exponentielle **statische Antwort** auf einen Kontrollparameter. Die frühere Gleichbehandlung dieser Fälle wird aufgehoben.

S₈ ist eine dimensionslose Fluktuationsamplitude, keine definitionsgemäß auf [0,1] beschränkte Wahrscheinlichkeit. Ihre Normierung begründet keine zwingende tanh-Form. Für `afet-tensions` werden exp/tanh deshalb als vorhandene phänomenologische Ansätze geführt, deren Vorhersageleistung und Parameteridentifizierbarkeit zu prüfen sind.

## 6. Kosten und Kalibrierung

`dot S_prod≥0` enthält den reversiblen bzw. gleichgewichtigen Grenzfall null. Daraus folgt keine strikt positive Mindestleistung jeder Kopplung. Landauers Resultat zur Löschung begründet ebenfalls keine allgemeine laufende Mindestleistung jedes Speichers. [Plenio und Vitelli](https://arxiv.org/abs/quant-ph/0103108).

Die inverse Bestimmung eines Parameters aus Messdaten ist eine legitime Kalibrierungsmethode. Problematisch ist, dieselben Daten anschließend als unabhängige Bestätigung zu zählen. Ein algebraischer Hin-und-zurück-Weg ist eine Identität; eine Mehrdatenanpassung ist eine Kalibrierung; ein separater Vorhersagetest prüft darüber hinausgehende Bewährung. Diese drei Fälle werden unterschiedlich bezeichnet.

Γ_domain wird erst dann zu einem thermodynamischen L, wenn eine gültige Fluss/Kraft-Bilanz und die entsprechende Parameterschätzung das zeigen. Der bereits erfolgte Γ/κ-Refit allein leistet diese Identifikation nicht.

## 7. Prüfkriterien

Eine thermodynamische Anwendung dokumentiert: Systemgrenze, Zustandsgrößen, Bilanzgleichungen, Flüsse, konjugierte Kräfte, Einheiten, Referenzzustand, zulässigen Kraftraum und Parameterschätzung. Danach werden Nichtnegativität, gegebenenfalls Reziprozität und unabhängige Vorhersagen geprüft. Fehlen die Voraussetzungen, bleibt die Beziehung als Datenfluss oder dynamischer Einfluss beschreibbar.
