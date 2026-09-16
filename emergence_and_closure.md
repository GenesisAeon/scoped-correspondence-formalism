# Emergenz, Rekonstruktion und geschlossene Makrodynamik

Revision 3.2, 16. September 2026. Dieses Dokument vertieft die Emergenzfragen des [Formalismus](FORMALISM.md). [Transformation und Kontext](context_transformations.md) definiert die gemeinsame Sprache für veränderliche Darstellungen, überlappende Systemzugehörigkeit und Zerlegung. Die Literaturzuordnung der bisherigen Anschlüsse steht in [LITERATURE_CONNECTIONS.md](LITERATURE_CONNECTIONS.md). Die eigenen Rechnungen sind Modellresultate; empirische Anwendungen bleiben gesondert zu prüfen.

## 1. Ein Modell und seine Darstellung auseinanderhalten

Ein Domänenmodell enthält mindestens Zustandsraum Z, zulässige Eingaben U, Entwicklung Φ bzw. Übergangskern P, Beobachtung h, Zeitmaßstab und Geltungsbereich. Für empirische Aussagen kommen Messfehler, Datenherkunft und Schätzverfahren hinzu. Eine Makrobeschreibung benötigt zusätzlich eine Abbildung π und ein Modell für ihre Entwicklung.

Vier Dimensionsbegriffe werden getrennt:

| Größe | Bedeutung |
|---|---|
| d_state | Dimension des vorausgesetzten Zustandsraums |
| d_attractor | geeignete Dimensionsgröße einer invarianten Menge |
| m_obs | Zahl der verwendeten Beobachtungs-/Verzögerungskoordinaten |
| d_model | Dimension des angepassten Zustandsmodells; diskrete Zustandszahl separat berichten |

Keiner dieser Werte wird aus einem unkalibrierten Frame-Score berechnet. Eine Zunahme von m_obs oder d_model kann einen vorher verdeckten Freiheitsgrad sichtbar machen, Gedächtnis repräsentieren oder Messfehler kompensieren.

## 2. Arten von Strukturabbildungen

Für die Selbstähnlichkeitsprüfung wird die Relation

\[
T\Phi_j^t(z)\approx\Phi_k^{ct}(Tz)
\]

um die folgenden Angaben ergänzt:

- T ist eine invertierbare Koordinatenabbildung, eine Projektion oder eine gelernte Darstellung; diese Fälle werden benannt.
- c>0 ist ein konstanter Zeitfaktor. Eine zustands-/bahnabhängige Zeitänderung benötigt eine eigene Definition.
- Norm, Gebiet, Zeithorizont und Fehlergrenze werden vor dem Test festgelegt. Domäneneinheiten werden durch deklarierte Skalen vergleichbar gemacht.
- Die Abbildung wird auf Trainingsdaten bestimmt und an zurückgehaltenen Bedingungen getestet. Eine beliebig nachjustierte Abbildung ist kein unabhängiger Befund.

Bei differenzierbarem T ergibt Ableiten nach t bei t=0 als notwendige lokale Bedingung

\[
DT(z)f_j(z)=c f_k(Tz).
\]

Diese Gleichung lässt sich direkt prüfen. Eine bloße topologische Konjugation garantiert weder gleiche Raten noch gleiche metrische Entfernungen. **Eigener Gegenfall:** x′=−x und y′=−2y sind auf der reellen Linie durch T(x)=sign(x)|x|² sogar bei c=1 topologisch konjugiert. T hat am Ursprung keine differenzierbare Umkehrung; die linearen Raten sind 1 und 2. Die Art der Regularität gehört deshalb zur Aussage.

## 3. Exakte stochastische Geschlossenheit

Wir verwenden endliche Markov-Ketten und **Zeilenverteilungen**: p_(t+1)=p_t P. C ist eine N×M-Matrix mit genau einer Eins pro Zeile; sie ordnet jeden Mikrozustand einem Makrozustand zu.

Eine M×M-Übergangsmatrix Q liefert für alle Anfangsverteilungen eine geschlossene Makrodynamik, wenn

\[
PC=CQ.
\]

Ausgeschrieben müssen für alle i,i′ im selben Block A und jeden Zielblock B gelten:

\[
\sum_{j\in B}P_{ij}=\sum_{j\in B}P_{i'j}.
\]

Das ist die hier gemeinte starke/ordinary Lumpability. Daraus folgt durch Induktion P^k C=CQ^k. Die Aussage gilt für den festgelegten P und die Partition; bei Eingaben u wäre sie für jeden zulässigen Kern P(u), mit derselben Partition und passend definierten Makroeingaben, zu prüfen. [Buchholz](https://doi.org/10.2307/3215235).

Eine Anhebungsmatrix Λ ist M×N, zeilenstochastisch und innerhalb jedes Blocks unterstützt; ΛC=I_M. Sie legt fest, wie eine Makropräparation auf Mikrozustände verteilt wird. Dann ist Q=ΛPC ein möglicher Makrokern. **Allein diese Konstruktion garantiert PC=CQ nicht.** Ohne Geschlossenheit entspricht wiederholtes Anwenden von Q im Allgemeinen einem zusätzlichen erneuten Präparieren der versteckten Mikrozustände.

### Eigene elementare Fehlerschranke

Definiere für einen festgelegten Q

\[
\delta=\max_i\frac12\sum_B|(PC-CQ)_{iB}|.
\]

Für jede Anfangsverteilung p und jeden ganzzahligen k≥0 gilt

\[
\operatorname{TV}(pP^kC,pCQ^k)\le\min(1,k\delta).
\]

Begründung: E=PC−CQ und

\[
P^kC-CQ^k=\sum_{j=0}^{k-1}P^{k-1-j}E Q^j.
\]

Linksmultiplikation mit einer Verteilung bildet eine konvexe Kombination der Fehlerzeilen; Rechtsmultiplikation mit Q kontrahiert deren Totalvariation. Die Dreiecksungleichung liefert kδ. Diese Schranke ist häufig grob, aber ohne stationäre Anfangsverteilung gültig. Sie ist keine aus Daten geschätzte Konfidenzgrenze. Für feinere Aggregationsschranken: [Michel–Siegle](https://arxiv.org/abs/2403.07618).

## 4. Was fehlende Geschlossenheit bedeutet

Bei einem linearen Mikromodell

\[
\dot x=Ax+By,\qquad \dot y=C_hx+Dy
\]

ergibt die Variation der Konstanten exakt

\[
\dot x(t)=Ax(t)+Be^{Dt}y(0)
+\int_0^t Be^{D(t-s)}C_hx(s)\,ds.
\]

C_h ist hier ein Matrixblock, nicht die Aggregationsmatrix aus Abschnitt 3. Beseitigen von y lässt somit einen Anfangsdatenbeitrag und ein Gedächtnis zurück. Die Rechnung ist eine direkte lineare Eliminierung; die allgemeinere Mori–Zwanzig-Theorie motiviert entsprechende Projektionsmodelle. [Gouasmi et al.](https://arxiv.org/abs/1611.06277).

**Projektentscheidung:** Ein gescheiterter Markov-Test löst einen Modellvergleich aus: mehr Zustand, Verzögerungen, zusätzlicher Eingang oder expliziter Gedächtniskern. Es folgt kein automatischer Dimensionssprung in der Natur.

Prädiktive Zustände bieten eine alternative Darstellung: Zwei beobachtete Historien gehören zur selben Klasse, wenn ihre bedingten Zukunftsverteilungen gleich sind. Für kontrollierte Modelle muss diese Gleichheit gegenüber den betrachteten zukünftigen Eingabefolgen gelten. Das ist eine hier vorgeschlagene Erweiterungsfrage, keine aus dem stationären unkontrollierten Satz übernommene Garantie.

## 5. Effective Information und Interventionen

Für einen **interventionell interpretierten** endlichen Kern P und eine deklarierte Präparationsverteilung q definieren wir

\[
EI_q(P)=\sum_{i,j}q_iP_{ij}\log_2\frac{P_{ij}}{(qP)_j}.
\]

Nullsummanden werden als null behandelt. Dies ist die gegenseitige Information des experimentell spezifizierten Ein-Schritt-Kanals. Ohne begründete Intervention oder Identifikationsannahmen ist dieselbe Rechnung lediglich eine Kanal-/Beobachtungsgröße. Die Uniformwahl q_i=1/N wird als EI_unif gekennzeichnet. Bei Zustandszahl eins ist EI=0; eine Division durch log₂N ist dort undefiniert.

Ein Makrovergleich lautet beispielsweise

\[
\Delta EI=EI_{q_M}(Q)-EI_{q_Z}(P).
\]

Die Verteilungen q_M und q_Z sowie Λ werden mitberichtet. Uniform auf Makrozuständen ist bei verschieden großen Blöcken nicht dieselbe Präparation wie uniform auf Mikrozuständen. Bei festgehaltener gemeinsamer Verteilung verletzt eine deterministische Vergröberung die Datenverarbeitungsungleichung nicht. Das [Vier-Zustands-Beispiel](worked_example_causal_emergence.md) rechnet den Unterschied aus.

Für Datenanwendungen sind Übergänge, Partition und Testfehler getrennt zu schätzen. Das Optimieren über viele Partitionen wird auf Trainingsdaten begrenzt; Konfidenz- und Robustheitsprüfungen erfolgen mit unabhängigen Trajektorien bzw. zeitlich sinnvoll getrennten Daten. Seltene Zustände und nicht realisierbare Interventionen werden ausgewiesen. NIS+ ist eine mögliche spätere Suchmethode, noch keine ausgeführte Replikation.

## 6. Arbeitsdefinitionen für die beiden Emergenzfragen

Die Typnamen sind projektspezifische Arbeitsbegriffe und behaupten keine kanonische Klassifikation.

**Typ 1: ein Vorteil der gemeinsamen oder gröberen Beschreibung.** Zuerst wird der Vorteil benannt: Prognose, Kontrolle, Robustheit, ΔEI oder Synergie. Dann werden passende Baseline, gleiche Ressourcen und Unsicherheit angegeben. Für ein autonomes Makromodell kommt die Geschlossenheitsprüfung hinzu. Diese Teilfragen werden nicht zu einem unkalibrierten Gesamtscore addiert.

**Typ 2: eine reichere Darstellung wird für die festgelegte Aufgabe benötigt.** Für verschachtelte Modellklassen F_m, festgelegten Prognosehorizont H und Verlustfunktion sei

\[
R_m^*=\inf_{f\in F_m}\mathbb E[\ell(Y_{t+H},f(\text{verfügbare Historie}))].
\]

Wird F_m in F_(m+1) eingebettet, ist R_(m+1)*≤R_m* schon definitionsgemäß. Entscheidend ist ein praktisch relevanter, außerhalb des Trainings bestätigter Gewinn bei berücksichtigter Schätzunsicherheit und Komplexität. Endliche Daten liefern Schätzungen, keine exakten Werte dieser Infima. Ein Versagen in einer gewählten Modellklasse schließt bessere Modelle derselben Dimension außerhalb dieser Klasse nicht aus.

Die Messung von R_m* hängt von Aufgabe, Datenverteilung, Beobachtung und Modellklasse ab. Daher wird der Schwellenwert vor der Untersuchung festgelegt; er wird nicht durch 2d+1, 0,84 oder 1/16 ersetzt.

## 7. Individuation als begrenzter Prüfvertrag

Ein Kandidat für eine eigenständige Makrobeschreibung kann anhand folgender getrennt berichteter Kriterien akzeptiert werden:

1. Eine operational begründete Grenze und eine vorab festgelegte Aufgabe.
2. Genügende Vorhersageleistung bzw. eine begründete Interventionsbeschreibung.
3. Hinreichende dynamische Geschlossenheit über einen angegebenen Horizont; verbleibende Eingänge/Gedächtnisterme offenlegen.
4. Eine sparsamere Darstellung als geeignete Alternativen bei vergleichbarer Leistung.
5. Robustheit gegenüber zulässigen Änderungen von Beobachtung, Partition und Störung.

Dieser Vertrag ist eine **methodische Entscheidung des Projekts**, kein notwendiges und hinreichendes Naturgesetz für Individuen. Ein physikalisch wichtiger Speicher kann geringer EI entsprechen; eine rein statistische Kompression kann gute Vorhersagen liefern, ohne selbst ein abgegrenztes physisches System zu sein.

## 8. Selbstähnliche Muster bei veränderlichen Größen

**Eigene Umparametrisierung:** In tanh(σΓ) kann Γ′=kΓ, σ′=σ/k für jedes k>0 dieselbe Antwort liefern. Bei Γ=a g ist ohne unabhängige Festlegung von a nur σa identifizierbar. Identische Zahlenwerte von σ sind dann kein koordinatenunabhängiger Vergleich.

Johanns Leitthese betrifft variable, system- und zustandsabhängige Dynamiken, die sich zusammensetzen und zerlegen lassen und dabei wiederkehrende Muster zeigen. Werte dürfen zwischen Zusammenhängen variieren oder gleich bleiben. RG-Universalität ist ein optionaler stärkerer Literaturanschluss, keine Voraussetzung oder Ausgangsbehauptung dieses Projekts. Ein solcher gesonderter Test benötigte einen Skalenoperator, eine geeignete Modellfamilie und einen belegten Skalierungsbereich. `beta_crit` als kritischer Exponent bleibt von `beta_response` der Sigmoidkurve verschieden.

Konjugation, geschlossene Projektion, statistische Skalierung und bloß ähnliche Kurven sind vier getrennte Aussagen. Die Leitidee Selbstähnlichkeit gewinnt dadurch mehrere konkret falsifizierbare Formen.

## 9. Geschlossenheit unter veränderlichem Kontext

### 9.1 Eine Darstellung ist ebenfalls veränderlich

Für \(y=\pi(z,c,t)\), \(\dot z=F\) und \(\dot c=G\) gilt

\[
H_\pi(z,c,u,w,t)
=D_z\pi F+D_c\pi G+\partial_t\pi.
\]

Eine Kandidatendynamik \(\dot y=g(y,v,t)\) verwendet einen deklarierten sichtbaren Eingang \(v=\nu(z,c,u,w,t)\). Exakte Geschlossenheit verlangt, dass H_π für alle zulässigen Kombinationen mit gleichem (y,v,t) denselben Wert besitzt und als geeignet reguläres g darstellbar ist. Die Bedingung gilt auf dem betrachteten erreichbaren Gebiet. Gleiche y-Werte allein reichen nicht, wenn die sichtbaren Eingänge verschieden sind.

Eine Darstellung kann also **relativ zu Eingängen geschlossen** sein, ohne isoliert zu sein. Soll g autonom sein, müssen diese Eingänge selbst aus dem Makrozustand bestimmt werden oder als zusätzliche Zustände aufgenommen werden. Das ist besonders bei überlappenden Systemen relevant: Der Einfluss einer anderen Zugehörigkeit wird zum Eingang oder Teil des gemeinsamen Zustands.

Bei \(F=f(z;\theta(z,c,t))\) enthält die Ableitung nach z sowohl \(\partial_z f\) als auch \(\partial_\theta f\,D_z\theta\). Eine Rechnung mit eingefrorenem θ beschreibt einen eigenen Sonderfall. **Kontrollbeispiel:** F(x)=−(1+x²)x hat F′(x)=−1−3x²; Einfrieren von θ=1+x² würde −1−x² liefern.

### 9.2 Von einem lokalen Residuum zum Verlaufsfehler

Definiere in derselben Zeitkoordinate

\[
\rho(t)=H_\pi(z(t),c(t),u(t),w(t),t)-g(y(t),v(t),t).
\]

Sei \(\hat y\) die Lösung des Kandidatenmodells mit **derselben vorgegebenen Eingangsfolge v(t)**. Ist g in y auf dem relevanten Gebiet gleichmäßig L-Lipschitz und \(\|\rho\|\le\epsilon\), folgt durch die Integralgleichung und Grönwall:

\[
\|y(t)-\hat y(t)\|
\le e^{Lt}\|y(0)-\hat y(0)\|
+\epsilon\frac{e^{Lt}-1}{L}.
\tag{E1}
\]

Für L=0 wird der letzte Term zu εt. Die Norm wird mit deklarierten Referenzskalen gewählt; ε hat die passende Zustandsrate. Die Gleichung ist eine eigene elementare Abschätzung, keine Konfidenzgrenze aus endlichen Daten. Für stabil kontrahierende Systeme kann sie sehr grob sein.

Wird v durch Rückkopplung aus dem jeweils geschätzten Zustand gewählt, sind die Eingangsfolgen im Allgemeinen verschieden. Dann muss die gemeinsame Rückkopplungsdynamik analysiert oder ein zusätzlicher Eingangsfehler abgeschätzt werden. Eine im Training kleine mittlere Abweichung belegt zudem keine gleichmäßige ε-Schranke.

### 9.3 Stochastische Vergröberung mit wechselnden Darstellungen

Für eine **vorab festgelegte Folge** zeilenstochastischer Kerne P_t, Partitionsmatrizen C_t und Makrokerne Q_t lautet die Ein-Schritt-Bedingung

\[
P_t C_{t+1}=C_t Q_t.
\tag{E2}
\]

Hier sind Mikrozustandszahl N und Makrozustandszahl M fest; die Zuordnung darf sich ändern. C_(t+1) ist erforderlich, weil der nächste Zustand in der dann geltenden Darstellung beobachtet wird. Ein Vergleich mit C_t auf beiden Seiten könnte eine rein beschreibende Änderung als Dynamikfehler missverstehen.

Mit E_t=P_tC_(t+1)−C_tQ_t und δ_t=max_i TV((P_tC_(t+1))_i,(C_tQ_t)_i) gilt

\[
\operatorname{TV}\!\left(pP_0\cdots P_{n-1}C_n,
                        pC_0Q_0\cdots Q_{n-1}\right)
\le\min\!\left(1,\sum_{t=0}^{n-1}\delta_t\right).
\tag{E3}
\]

**Eigene Ableitung:** Die Differenz der Matrixprodukte ist

\[
\sum_{t=0}^{n-1}
 P_0\cdots P_{t-1}\,E_t\,Q_{t+1}\cdots Q_{n-1}.
\]

Leere Produkte sind Identitäten. Konvexität und Kontraktion der Totalvariation liefern E3 wie im stationären Fall. Für datenabhängig umgeschaltete Darstellungen muss der Auswahlmechanismus in einem gemeinsamen Modell erfasst werden; das Einsetzen einer nachträglich ausgewählten Folge rechtfertigt noch keine bedingungslose probabilistische Garantie.

## 10. Dynamische Geschlossenheit und Aufgabentauglichkeit getrennt prüfen

Eine exakt geschlossene Sicht kann Informationen verlieren, die für eine andere Aufgabe benötigt werden. Sei K der sichere Mikrozustandsbereich. Für eine deterministische Projektion π lassen sich unterscheiden:

\[
K_{\exists}=\pi(K),\qquad
K_{\forall}=\{y\in\pi(Z):\pi^{-1}(y)\subseteq K\}.
\]

K_∃ sagt: Mindestens ein verträglicher Mikrozustand ist sicher. K_∀ sagt: Jeder mit der Beobachtung verträgliche Zustand ist sicher. Diese Mengen bezeichnen momentane Sicherheit; sie sind noch keine Viabilitätskerne über einen Zeithorizont. Bei zusätzlichem Wissen wird die Faser π⁻¹(y) auf die damit verträglichen Zustände eingeschränkt.

**Eigener Gegenfall:** Die Summensicht s=x₁+x₂ unterscheidet (0,5; 0,5) und (−0,25; 1,25) nicht. Der erste Zustand liegt in K={x₁≥0,x₂≥0}, der zweite nicht. Trotzdem kann s eine exakt geschlossene Dynamik besitzen. Das [Pufferbeispiel](worked_example_viability.md) leitet diese Dynamik her. In Z=ℝ² gilt für diese Sicht K_∃=[0,∞), aber K_∀ ist leer, weil jede Summenfaser auch einen negativen Einzelbestand enthält.

Die zusätzliche Koordinate d=x₁−x₂ macht x₁=(s+d)/2 und x₂=(s−d)/2 rekonstruierbar. Lokale Sicherheit ist dann exakt \(s\ge|d|\). Falls nur eine gültige Schranke |d|≤D bekannt ist, ist s≥D hinreichend für alle damit verträglichen Zustände. Herkunft und zeitliche Gültigkeit von D gehören zum Sicherheitsnachweis.

Das illustriert Typ 2 ohne physikalische Dimensionserzeugung: Für die Summenprognose kann s genügen, für den Schutz beider Teile wird hier zusätzliche Verteilungsinformation benötigt. Andere Aufgaben können andere Darstellungen bevorzugen. Ein vollständiger Markov-Zustand muss nicht für jede Entscheidung die sparsamste Darstellung sein.

## 11. Individuation bei überlappender Zugehörigkeit

Die Kriterien aus Abschnitt 7 gelten relativ zu einer Aufgabe und einer Systemgrenze. Eine Einheit muss nicht exklusiv einer einzigen Partition angehören. Zwei Systembeschreibungen können sie gemeinsam verwenden und dennoch verschiedene Eingänge, Beschränkungen oder Beobachtungsgrößen besitzen.

Die Beschreibung nennt deshalb zusätzlich:

1. Gemeinsame physische Variablen und deren Abgleich zwischen den Sichten.
2. Tatsächliche Einflüsse und separat dazu rein beschreibende Kontextänderungen.
3. Gleichzeitig erfüllbare Eingriffe und gemeinsam genutzte Ressourcen.
4. Die Art der Schließung: autonom, eingangsbedingt, approximativ oder mit Gedächtnis.
5. Die Aufgabe, für die diese Darstellung Informationen ausreichend erhält.

Eine gemeinsame oder gröbere Beschreibung kann einen Vorteil zeigen, aber auch einen Konflikt sichtbar machen. Beim gemeinsamen Eingriffsbudget können zwei einzeln beherrschbare Teilaufgaben gemeinsam unbeherrschbar sein. Ein Emergenzbefund muss deshalb nicht positiv ausfallen; sein Vorzeichen und seine Vergleichsbasis werden gemessen, nicht vorgegeben.

## 12. Konkreter Prüfablauf

| Schritt | Festlegung oder Prüfung | Gegenbefund und nächste Modellentscheidung |
|---|---|---|
| Aufgabe | Zielgröße, Horizont, Eingriffsrechte, Fehlermaß | Aufgabenwechsel verlangt neue Bewertung |
| Darstellung | π, Kontext, Einheiten, gemeinsame Variablen | widersprüchliche Sichten zuerst abgleichen |
| Entwicklung | F/P, Eingangsabbildung, Regeln | verborgene Regelzustände ergänzen |
| Geschlossenheit | gleiche Fasern, Ableitungen/Kerne, Residuum | mehr Zustand, Eingang oder Gedächtnis vergleichen |
| Aufgabeninformation | Zielgröße bzw. sichere Fasern | genau die verlorene, entscheidungsrelevante Information ergänzen |
| Transformation | Kompositionsregel und Fehlerfortpflanzung | Verzerrung und beschränkten Geltungsbereich ausweisen |
| Bewährung | unabhängige Trajektorien und Kontexte | Modellvergleich unter gleichen Ressourcen |

Die [neuen Modellprüfungen](TRANSFORMATION_VERIFICATION.md) kontrollieren insbesondere E1–E3, Kontextableitungen, wechselnde Partitionen sowie den Unterschied zwischen geschlossener Summendynamik und lokaler Sicherheit. Sie ergänzen die früheren Prüfungen und ersetzen keine empirische Anwendung.
