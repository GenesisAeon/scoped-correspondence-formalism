# Emergenz, Rekonstruktion und geschlossene Makrodynamik

Revision 3, 16. September 2026. Dieses Dokument formuliert die konkrete Erweiterung des [Formalismus](FORMALISM.md). Die Literaturzuordnung steht in [LITERATURE_CONNECTIONS.md](LITERATURE_CONNECTIONS.md). Die unten ausdrücklich als eigene Ableitung gekennzeichneten Rechnungen sind Modellresultate.

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

## 8. Universelle Muster und nichtuniverselle Skalierungen

**Eigene Umparametrisierung:** In tanh(σΓ) kann Γ′=kΓ, σ′=σ/k für jedes k>0 dieselbe Antwort liefern. Bei Γ=a g ist ohne unabhängige Festlegung von a nur σa identifizierbar. Identische Zahlenwerte von σ sind dann kein koordinatenunabhängiger Vergleich.

RG-Universalität wird nur bei ausgewiesenem Skalenoperator, geeigneter Modellfamilie und nachgewiesenem Skalierungsbereich beansprucht. Eine mögliche empirische Untersuchung prüft dimensionslose Skalierungsfunktionen, Exponenten und geeignete Verhältnisse über mehrere Größen/Skalen, samt Korrekturen und alternativen Fits. `beta_crit` als kritischer Exponent bleibt von `beta_response` der Sigmoidkurve verschieden.

Konjugation, geschlossene Projektion, statistische Skalierung und bloß ähnliche Kurven sind vier getrennte Aussagen. Die Leitidee Selbstähnlichkeit gewinnt dadurch mehrere konkret falsifizierbare Formen.
