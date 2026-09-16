# CREP — Informationsschicht, Revision 2

Stand: 16. September 2026. Verbindliche Notation: [FORMALISM.md](FORMALISM.md).

## 1. Vier Rollen, explizite Messentscheidungen

S/K/R/V strukturieren die Fragen nach Halten, Bewegen, Transformieren und Aufnehmen von Information. Ihre Vollständigkeit als Beschreibung aller Information ist eine Forschungsannahme. Die Revision verlangt keine künstliche Zahl für jede Rolle in jeder Domäne.

| Rolle | Mögliche Operationalisierung | Erforderliche Festlegung |
|---|---|---|
| S — Erhalt | Überlebens-/Retentionswahrscheinlichkeit, Ausfallzeit oder Verzerrung über einen Zeitraum | gespeicherte Größe, Aufgabe, Störung, Beobachtungsdauer |
| K — Übertragung | `K_info`: Kapazität eines bestimmten Kanals in Bit/Zeit | Ein-/Ausgang, Rauschen, Ressourcen, Zeitskala |
| R — Transformation | `R_info=I(X;X')/H(X)` für geeignete diskrete Variablen; zusätzlich Verzerrung | Alphabet, Verteilung, Kodierung, Fehlertoleranz |
| V — Aufnahme | `eta_info=mathcal_I/K_info` | gleicher Kanal, Empfänger, Nutzungsbedingung und Zeitbezug |

Jeder Metrikeintrag enthält mindestens: Name, Definition, Einheit, Zustands-/Beobachtungsbezug, Geltungsbereich, Datenquelle, Schätzverfahren, Unsicherheit und Evidenzstatus. Nicht bestimmbare Werte werden mit Begründung als `not_available` geführt; sie werden nicht durch plausible Konstanten ersetzt.

## 2. S: Informationsretention und dynamische Stabilität

Ein konkretes Retentionsmaß kann beispielsweise

\[
S_{ret}(T,\epsilon)=P[d(g(z(T)),g(z(0)))\le\epsilon]
\]

sein. Hier bezeichnet g den zu erhaltenden Informationsinhalt, d eine festgelegte Verzerrung, T den Zeithorizont und die Wahrscheinlichkeit ein festgelegtes Ensemble von Störungen. Das ist eine vorgeschlagene Messdefinition, kein universelles Naturgesetz. Die Wahl von g und d muss verhindern, dass eine triviale konstante Darstellung als gute Speicherleistung zählt.

Für einen glatten autonomen kontinuierlichen Prozess an einem Fixpunkt kann ergänzend

\[
S_{rec}=-\max\operatorname{Re}\operatorname{eig}(D_zf(z_*))
\]

angegeben werden. Sie misst lokale Rückkehr in der festgelegten Zeit. Ein Speicher kann mehrere stabile Zustände benötigen; ein einziger attraktiver Zustand kann alle anfangs verschiedenen Inhalte löschen. Daher folgt Informationsretention nicht allein aus positiver Rückkehrrate.

Lyapunov-Exponenten beziehen sich auf spezifizierte Trajektorien. Ein stabiler autonomer Grenzzyklus besitzt einen neutralen Phasenmodus; ein chaotischer Attraktor kann trotz positiven Exponenten als Menge bestehen bleiben. Aussagen zur Koordinateninvarianz benötigen geeignete reguläre Transformationen und eine feste Zeitparametrisierung. Beobachtung, Projektion und grobe Zeitabtastung können die Schätzung verändern.

Landauers Löschgrenze ist keine generelle Mindestleistung für das Halten eines Bits. Unter den üblichen isothermen Bedingungen betrifft sie die logische irreversible Löschung; eine Erhaltungsleistung hängt vom konkreten Speicher und seiner Störungsumgebung ab. [Plenio und Vitelli](https://arxiv.org/abs/quant-ph/0103108).

## 3. K: Kapazität benötigt einen Kanal

Für einen diskreten gedächtnislosen Kanal mit festgelegten Beschränkungen ist die Kapazität pro Nutzung `C_use=max_p(X) I(X;Y)`. Bei einer festgelegten Nutzungsrate ν kann daraus `K_info=ν*C_use` werden. Kanäle mit Gedächtnis benötigen eine passende Ratenfassung.

Für den bandbegrenzten Kanal mit additivem weißem gaußschem Rauschen und mittlerer Leistungsbeschränkung gilt speziell

\[
K_{info}=B\log_2(1+P/N).
\]

B ist hier eine Bandbreite in Hz. Eine allgemeine Zahl von Freiheitsgraden ist ohne zusätzliche Modellierung kein Ersatz. [Shannon (1948), insbesondere Theorem 17](https://people.math.harvard.edu/~ctm/home/text/others/shannon/entropy/entropy.pdf).

Kapazität ist weder Ausbreitungsgeschwindigkeit noch tatsächlicher Nutzdurchsatz. Sender, Übertragungsweg und gewählter Empfängereingang gehören zur Kanaldefinition. Änderungen am Empfänger können bereits diesen Kanal ändern; eine pauschale Empfängerunabhängigkeit wird nicht angenommen.

## 4. R: Informationsretention und Genauigkeit

Für diskrete Variablen mit `0<H(X)<∞` gilt `0≤I(X;X')≤H(X)`. Der Quotient ist daher normiert. Bei `H(X)=0` ist er undefiniert. Für kontinuierliche Daten sind eine begründete Diskretisierung oder andere klar definierte Maße nötig; differentielle Entropie liefert diese Normierung nicht allgemein.

`R_info=1` kann auch bei einer invertierbaren Umkodierung gelten. Soll „gleiche Kopie“ geprüft werden, müssen beispielsweise `P(X'≠X)` oder `E[d(X,X')]` dazukommen. Korrekte klassische Kopien sind möglich.

Rate-Distortion-Theorie verbindet Datenrate und eine gewählte Verzerrungsfunktion. Quanten-No-Cloning betrifft die universelle Kopie beliebiger unbekannter Quantenzustände. Biologische Fehlerschwellen gelten für bestimmte Replikationsmodelle. Diese Ergebnisse werden nicht zu einer gemeinsamen universellen Kopierschranke gleichgesetzt und begründen den Quotienten nicht automatisch.

## 5. V: Nutzungsgrad mit konsistentem Zeitbezug

Bei existierender Informationsrate `mathcal_I` und bekannter Kapazität `K_info>0` desselben Kanals wird

\[
\eta_{info}=\mathcal I/K_{info}
\]

verwendet. Für eine passende Blockbetrachtung lautet der Nenner `K_info*Delta_t`. Bei Kapazität null ist der Nutzungsquotient undefiniert; vollständige Übertragungsunfähigkeit kann getrennt als Eigenschaft des Kanals dokumentiert werden.

Für eine Markov-Kette `X→Y→Z` gilt die Datenverarbeitungsungleichung `I(X;Z)≤I(X;Y)`. Sie verlangt die Markov-Bedingung. Zusätzliche Seiteninformation muss im Modell enthalten sein. Ein positiver MI-Wert allein beweist keine gerichtete Kausalität.

K und V können als Kapazität und realisierte Nutzung getrennt berichtet werden. Das beweist keine statistische Unabhängigkeit, keine universelle Ko-Adaption und keine Gleichheit mit einem Transportkoeffizienten. Die frühere Argumentation über multiplizierte Friis-Faktoren reicht dafür nicht aus.

## 6. Komposition und Emergenz als prüfbare Fragestellungen

Für eine gewählte Größe M ist ein Residuum `Delta_M=M_composition-M_baseline` sinnvoll, wenn die Baseline begründet, vorab festgelegt und mit denselben Ressourcen, Beobachtungen und Einheiten bestimmt ist. Eine Summe von Einzelwerten ist nicht für jede Größe eine physikalisch sinnvolle Nullhypothese.

Positive Residuen können Interaktionen, aber auch bessere Messzugänge, zusätzliche Modellflexibilität oder eine schwache Baseline widerspiegeln. Unsicherheit und unabhängige Vorhersageprüfung gehören zur Auswertung. Weder die bloße Definition des Residuums noch die rekursive Wiederanwendung der Rollen schließt Zirkularität aus.

Eine neue Beschreibungsdimension wird als Modellvergleich untersucht: Liefert ein zusätzlicher Zustand oder ein Gedächtnisterm robuste Vorhersagegewinne gegenüber gleich sorgfältig angepassten Alternativen? Eine neue Kategorie oder ein Zweiglabel allein beweist keine zusätzliche physikalische Dimension.

## 7. Anschluss an bestehende Pakete

Die vorhandenen C/R/E/P-Bridges bleiben unter ihren konkreten Definitionen lesbar. Eine Übersetzung zu S/K/R/V braucht pro Feld eine eigene Begründung. Schnittstellennamen werden nicht stillschweigend mit neuer Bedeutung gefüllt. Beobachtungen, synthetische Größen, festgelegte Defaults und unabhängig kalibrierte Parameter bleiben unterscheidbar.
