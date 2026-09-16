# CREP–UTAC–AFET — konsolidierter Formalismus, Revision 3.2

Stand: 16. September 2026. Baut auf den Korrekturen und Literaturanschlüssen der Revisionen 2–3.1 auf. Revision 3.2 ergänzt Transformationen, überlappende Systemzugehörigkeit und gemeinsame Viabilitätsbedingungen. Historie: [DESIGN.md](DESIGN.md), [Revision 2](REVISION_2026-09-16.md), [Revision 3](REVISION_3_2026-09-16.md), [neue Vertiefung](REVISION_3_2.md). Zwei optionale, separat verifizierte Module ergänzen den Kern, ohne ihn zu ändern: [Sheaf-Kontextualität](sheaf_contextuality.md) (F08) und [PID/Redundancy Bottleneck](pid_redundancy_bottleneck.md) (F09) — Herkunft und Prüflauf in [Aeons Review](reviews/2026-09-16_gemini_extensions_review_aeon.md) und [FOLLOWUP_TICKETS.md](FOLLOWUP_TICKETS.md).

## 1. Absicht und Status

„Crep war Information, UTAC dann Systeme, und AFET war die Kopplung für Thermodynamik. So war es mal gedacht.“ — Johann, 15. September 2026.

Diese Rollen werden beibehalten. Der Rahmen verbindet sie durch Beobachtungsmodelle, Dynamiken und Kopplungsgesetze mit angegebenen Voraussetzungen. Er behauptet keine mathematische Gleichheit aller drei Beschreibungsebenen. Seine mögliche Einheit liegt im konsistenten Umgang mit Zuständen, Beobachtungen, Eingaben und Evidenz.

**Johanns Leitthese ist eine über Ebenen zusammensetzbare und zerlegbare Selbstähnlichkeit dynamischer Beschreibungen.** Größen, Parameter und Dynamiken hängen vom jeweiligen System, seinem Zustand, seinen Kopplungen und der betrachteten Ebene ab. Eine Beschreibung kann in übergeordnete Dynamiken eingehen und auf einer feineren Ebene durch weitere dynamische Teilmodelle ausgearbeitet werden. Wiederkehrend sind bestimmte Beziehungs-, Organisations- oder Entwicklungsmuster.

Johann behauptet damit weder RG-Universalität noch feststehende domänenübergreifende Konstanten. Die kritisierten Gleichsetzungen und Konstantenbehauptungen stammen aus konkreten früheren Ausarbeitungen. Die bisherige Darstellung rückte diese Dokumentbefunde stellenweise zu nahe an seine persönliche These; Revision 3.1 korrigiert diese Zuschreibung.

### System, Zustand und Ebene gehören zur Formel

Als reine Schreibkonvention kann eine kontinuierliche Instanz beispielsweise lauten:

\[
\dot z_i^{(\ell)}=f_i^{(\ell)}\!\left(z^{(\ell)},u^{(\ell)},t;
\theta_i^{(\ell)}(z^{(\ell)},u^{(\ell)},t)\right).
\]

ℓ bezeichnet die Beschreibungsebene, i eine Komponente. Der vollständige Zustand z kann gekoppelte Komponenten enthalten; θ steht für system- und zustandsabhängige Modellgrößen. Die Gleichung ist eine Notationshilfe, kein neues Bewegungsgesetz. Dasselbe Prinzip gilt für diskrete, stochastische und hybride Modelle.

Zusammensetzen verlangt eine angegebene Regel für Teilmodelle, Kopplungen und die resultierende Beschreibung. Zerlegen verlangt eine gewählte Auflösung und eine begründete Beschreibung der Teile und ihrer Beziehungen. Untersucht wird, welche Muster bei diesen Übergängen wiederkehren und wie ihre Größen und Dynamiken sich dabei verändern. Eine Vergröberung kann Information verlieren; eine feinere Darstellung kann zusätzliche Zustände oder Gedächtnis benötigen.

Konstante Parameter in den gerechneten Beispielen sind begrenzte Modellfälle. Bei zustandsabhängigen Parametern bezieht sich eine Linearisierung auf das vollständige eingesetzte Vektorfeld einschließlich dieser Abhängigkeiten. Eine lokal eingefrorene Rechnung wird als solche gekennzeichnet.

### Selbstähnlichkeit präzise untersuchen

| Aussageebene | Zulässige Aussage | Erforderlicher Nachweis |
|---|---|---|
| Strukturelle Analogie | Zwei Fälle zeigen ein vergleichbares Organisationsmuster. | genaue Beschreibung von Gemeinsamkeiten und Unterschieden |
| Mathematische Selbstähnlichkeit | Eine angegebene Transformation erhält eine bestimmte Struktur exakt oder näherungsweise. | Transformation, Skalen, Parameterabbildung, Bereich und gegebenenfalls Fehlermaß |
| Empirische Selbstähnlichkeit | Die behauptete Strukturbeziehung bewährt sich an unabhängig geprüften Daten. | Messmodell, Unsicherheit, Referenzmodelle und zurückgehaltene Daten |

Für den Sonderfall autonomer deterministischer Modelle mit Entwicklungsoperatoren `Phi_j^t` und konstanter Zeitskalierung könnte eine konkrete Prüffrage lauten:

\[
T\circ\Phi_j^t\;\approx\;\Phi_k^{c t}\circ T,\qquad c>0.
\]

T bildet Zustände ab, c die Zeitskala; Parameter und zulässige Anfangszustände sind vorzugeben. Für eine näherungsweise Beziehung werden Zeitraum, Norm und akzeptierte Abweichung festgelegt. Bei kontrollierten, stochastischen oder grob beobachteten Systemen müssen zusätzlich Eingaben, Übergangsverteilungen bzw. Informationsverlust berücksichtigt werden. Diese Gleichung ist ein Prüfschema, kein bereits nachgewiesenes Gesetz des Ökosystems.

Die Art der Abbildung wird verbindlich ergänzt: eine exakte Beziehung mit einem Homöomorphismus T ist eine Konjugation nach konstanter Zeitskalierung; eine kompatible Projektion kann eine Semikonjugation sein. Eine allgemeine Orbitäquivalenz erlaubt weitergehende Zeitänderungen. Diese Begriffe werden nicht mit RG-Universalität gleichgesetzt. Für differenzierbares T gilt als notwendige lokale Prüfbedingung `DT(z) f_j(z)=c f_k(Tz)`. Topologische Konjugation allein erhält keine numerischen Erholungsraten. [Ausarbeitung und Gegenfall](emergence_and_closure.md).

Eine ähnliche lineare Relaxation nahe zwei stabilen Fixpunkten kann bereits aus allgemeiner Linearisierung folgen. Eine weitergehende Selbstähnlichkeitsbehauptung muss deshalb erklären, welchen zusätzlichen, unterscheidbaren Befund sie vorhersagt. Gemeinsame Defaults oder frei angepasste Skalierungen allein reichen nicht.

| Schicht | Frage | Benötigte Angaben |
|---|---|---|
| CREP / Information | Was bleibt erhalten, wird übertragen oder durch einen Empfänger nutzbar? | Zufallsvariablen, Kanal, Kodierung, Zeitfenster, Schätzverfahren |
| UTAC / Systeme | Wie entwickelt sich ein Zustand unter Eingaben und Störungen? | Zustand z, Zeit t, Eingabe u, Dynamik f, Beobachtung h |
| AFET / Kopplung | Wie wirkt eine Komponente auf eine andere? | Datenpfad oder dynamischer Term; für Thermodynamik zusätzlich Bilanz, Flüsse und konjugierte Kräfte |

## 2. Verbindliche Notation

| Symbol | Bedeutung | Einheit / Einschränkung |
|---|---|---|
| `z(t)` | Systemzustand | Domäneneinheiten, gegebenenfalls Vektor |
| `u(t)` / `R_ctrl` | äußerer Kontrollparameter | Domäneneinheit; kein stiller Wechsel zur Zustandsvariable |
| `beta_response` | Steilheit einer statischen Antwortkurve | `1/[u]` |
| `S_rec` | lokale kontinuierliche Erholungsrate am angegebenen Fixpunkt | `1/Zeit`; kann außerhalb stabiler Fixpunkte ≤0 sein |
| `lambda_L` | Lyapunov-Exponent einer angegebenen Trajektorie | `1/Zeit`; nicht stets ein Fixpunkt-Eigenwert |
| `K_info` | Kanalkapazität als Rate | Bit/Zeit; konkretes Kanalmodell |
| `R_info` | diskrete Informationsretention | dimensionslos; `0<H(X)<∞` |
| `eta_info` | realisierte Informationsrate / Kapazität | dimensionslos; gleicher Kanal und gleiche Zeiteinheit |
| `A_ij` | lokaler dynamischer Einfluss, z.B. `∂f_i/∂z_j` | `[z_i]/([z_j]·Zeit)` |
| `L_ij` | linearer thermodynamischer Transportkoeffizient | `[J_i]/[X_j]` |
| `S_th` | thermodynamische Entropie | J/K oder explizit gewählte Normierung |
| `B_prob`, `ell_basin` | Beckenwahrscheinlichkeit, geometrischer Abstand | dimensionslos bzw. Metrikeinheit |
| `C`, `Lambda`, `Q` | Zustandsaggregation, Mikropräparation und Makro-Übergangskern | zeilenorientierte Markov-Konvention; C ist hier nicht eine CREP-Achse |
| `EI_q` | Information des spezifizierten Interventionskanals | Bit/Schritt; q und Schrittweite angeben |
| `delta_cl` | maximaler Ein-Schritt-Fehler einer Makro-Schließung in Totalvariation | dimensionslos; kein Emergenz-Gesamtscore |
| `G_alpha_svd` | Summe von Potenzen der Singularwerte einer Übergangsmatrix | dimensionslos; nicht das Γ der vorhandenen Pakete |
| `beta_crit` | kritischer Skalierungsexponent in einem ausgewiesenen Modell | kein Synonym für `beta_response` |

S/K/R/V bleiben Namen für die vier Informationsrollen. Eine Rolle ist kein universeller Skalar: jeder konkrete Wert erhält eine Metrikkennung, Einheit, Domäne und Herkunft. `eta_info` ist die hier vorgeschlagene quantitative Instanz der V-Rolle. C/R/E/P aus den bestehenden Bridges und der separate Frame-Score sind keine Synonyme für S/K/R/V.

## 3. Informationsschicht

Für diskrete X und X′ mit endlichem positivem H(X) ist

\[
R_{info}=I(X;X')/H(X)\in[0,1].
\]

Das misst erhaltene Information. Kopiergenauigkeit benötigt zusätzlich eine Verzerrungsfunktion oder Fehlerwahrscheinlichkeit. Für kontinuierliche Variablen darf H nicht ungeprüft durch differentielle Entropie ersetzt werden.

Eine geeignete Informationsrate sei `mathcal_I` in Bit/Zeit. Bei bekannter positiver Kapazität gilt unter den zum Kanal passenden Annahmen

\[
\eta_{info}=\mathcal I/K_{info}\in[0,1].
\]

`I(Block)/(K_info*Delta_t)` ist eine mögliche Blockfassung. `I/K_info` ohne Zeitbezug ist bei I in Bit dagegen eine Zeit. Informationstheoretische Kapazität, physikalische Ausbreitungsgeschwindigkeit und ein thermodynamischer Transportkoeffizient sind verschiedene Größen.

Für die S-Rolle ist ein aufgabeabhängiges Retentions- oder Ausfallmaß zulässig. `S_rec` kann ergänzend aus der realisierenden Dynamik bestimmt werden; seine Eignung als Proxy für Informationsspeicherung ist separat zu begründen. Einzelheiten: [Informationsschicht](information_layer_crep.md).

## 4. Systemschicht und Individuation

Ein Systemmodell wird zunächst operational abgegrenzt:

\[
\dot z=f(z,u,t),\qquad y=h(z)+\varepsilon.
\]

Für diskrete oder hybride Systeme werden Update- bzw. Ereignis-/Resetregeln explizit angegeben. Analytische Lösung und numerische Integration sind alternative Berechnungen derselben Dynamik.

Eine vorgeschlagene Komposition kann einen Stabilitätsgewinn zeigen:

\[
\Delta S=S_{composition}-S_{baseline}.
\]

Beide Terme müssen dieselbe Metrik, Zeitskala und Aufgabe verwenden; Partition, Baseline und Auswertung werden vor dem Vergleich festgelegt. Ein positiver Wert belegt nur einen Vorteil gegenüber dieser Baseline. Ein allgemeines notwendiges und hinreichendes Individuationskriterium oder eine Äquivalenz mit Autopoiesis ist nicht hergeleitet.

Die statische UTAC-Antwortkurve bleibt ein möglicher Ansatz:

\[
p(u)=\frac{p_{max}}{1+\exp[-\beta_{response}(u-\Theta_u)]}.
\]

Sie legt keine zeitliche Erholung fest. Beim Modell `dot z=-(z-p(u))/tau` ist für festes u die Erholungsrate `S_rec=1/tau`, unabhängig von `beta_response`.

## 5. Konsistente kubische Erweiterung

Als eigenständige Modellfamilie wird vorgeschlagen:

\[
\tau\dot x=-x^3+ax+b,\qquad
U(x)=x^4/4-ax^2/2-bx,\qquad\tau>0.
\]

x, a, b und U sind hier dimensionslos; τ hat eine Zeiteinheit. Eine Verbindung mit einem dimensionalen Zustand z benötigt eine feste Abbildung, etwa `x=(z-z_ref)/z_scale`. a und b sind Kontrollparameter. U ist zunächst ein mathematisches Potential, nicht automatisch thermodynamische freie Energie.

Für konstante a,b gibt es drei verschiedene reelle Fixpunkte genau bei `4a^3>27b^2`. Die äußeren sind stabil. Für b=0 und a>0 gilt

\[
x_*=\pm\sqrt a,\quad S_{rec}(x_*)=2a/\tau,
\quad S_{rec}(0)=-a/\tau.
\]

Die Beziehung `a=-tau*S_rec(0)` gilt nur am Gleichgewicht x=0 des symmetrischen Modells. Bei a>0 ist dieses Referenzgleichgewicht instabil. Die Beziehung ersetzt keine unabhängige Parameterschätzung. Die kubische Familie ist nicht als exakter Grenzfall der Sigmoidkurve hergeleitet. Eine Pitchfork ändert die Zahl der Gleichgewichte; der Zustandsraum bleibt eindimensional.

`B_prob`, geometrische Beckenweite, Abstand zur aktuellen Grenze und lokale Erholungsrate werden getrennt geführt. Weitere Herleitungen und die vorsichtige Frame-Hypothese: [Systemschicht](system_layer_utac.md).

## 6. Kopplungsschicht

Ein dynamischer Ansatz für paarweise additive Kopplungen ist

\[
\dot z_i=f_i(z_i,u_i)+\sum_{j\ne i}g_{ij}(z_i,z_j,u).
\]

Eine Informationsabhängigkeit oder ein Funktionsaufruf ist ein eigener Evidenztyp und belegt nicht automatisch einen solchen dynamischen Term.

Mehrgliedrige Kopplungen, überlappende Zugehörigkeiten und gemeinsame Ressourcenbedingungen können eine allgemeinere gemeinsame Dynamik F und gekoppelte Eingriffsmengen benötigen. Sie werden nicht auf eine paarweise Summe reduziert, sofern diese Reduktion nicht begründet ist. [Transformation und Kontext](context_transformations.md) ergänzt die entsprechenden Verträglichkeitsregeln.

Für den thermodynamischen Spezialfall müssen Flüsse J und entropiekonjugierte Kräfte X identifiziert sein. Erst dann wird der lineare Ansatz

\[
J=LX,\qquad \dot S_{prod}=X^TLX\ge0
\]

geprüft. Dafür muss `L_s=(L+L^T)/2` auf dem zulässigen Kraftraum positiv semidefinit sein. Symmetrie/Reziprozität erfordert zusätzliche mikroskopische Voraussetzungen und gegebenenfalls die Onsager-Casimir-Paritäten. Ein asymmetrischer Drift-Jacobian ist kein Beweis für gebrochene thermodynamische Reziprozität.

**Es gibt keine allgemeine Identität zwischen `eta_info`, Panarchy, `A_ij` und `L_ij`.** Panarchy bezeichnet hier skalenübergreifende Abhängigkeiten; ihre jeweilige Operationalisierung wird genannt. exp und tanh bleiben mögliche, begründungspflichtige Antwortfunktionen. Aus „Rate“ bzw. „normiert“ folgt keine eindeutige Funktionswahl.

Siehe [Kopplungsschicht](coupling_layer_afet.md) und [Wärmebeispiel](worked_example_heat_exchange.md).

## 7. Evidenz und Grenzen

Jede Aussage erhält einen Status: Definition, Standardresultat mit Voraussetzungen, Ableitung im angegebenen Modell, synthetische Prüfung, Codebefund, empirische Schätzung, Hypothese oder nicht untersucht. Eine passende Formel und ein grüner Test allein sind keine empirische Bewährung.

Die ursprünglichen Behauptungen `beta=S`, `V=Panarchy=L`, die unzentriert/zentriert vermischte Herleitung und die allgemeinen exp/tanh- sowie Dimensionsentstehungsbeweise sind zurückgenommen. Johann berichtet nach lokaler Einsicht in `Gemini.txt`, dass dort die alte Identitätsaussage ausdrücklich positiv bewertet wurde. Das ist eine übermittelte Quellenprüfung; die Datei selbst liegt dieser Revision weiterhin nicht vor. Der berichtete Gegencheck ersetzt die hier ausgeführten mathematischen Prüfungen nicht.

## 8. Beobachtung, Rekonstruktion und Typ 2

Zustandsdimension, Attraktordimension, Zahl der Beobachtungskoordinaten und angepasste Modelldimension werden getrennt angegeben. Takens' generische Einbettungsgarantie ist ein Anschluss für Rekonstruktion, kein universeller Mindestwert oder Entstehungsgesetz zusätzlicher Dimensionen. [Voraussetzungen und Primärquellen](LITERATURE_CONNECTIONS.md).

Die projektinterne Typ-2-Frage lautet: Benötigt eine festgelegte Prognose-/Steuerungsaufgabe eine reichere Darstellung? Verglichen werden zusätzliche Zustände, Verzögerungen, Eingänge und Gedächtnisterme mit gleich sorgfältig angepassten Alternativen. Trainingsgewinn allein genügt nicht. Das [Rekonstruktionsbeispiel](worked_example_reconstruction.md) zeigt eine zweidimensionale Kreiseinbettung und eine Projektion mit unvermeidlicher Anfangsdaten-/Gedächtnisabhängigkeit.

## 9. Eigene Makrodynamik als prüfbare Eigenschaft

Für einen endlichen Mikro-Übergangskern P und eine Partitionsmatrix C lautet die exakte Bedingung

\[
PC=CQ.
\]

Sie garantiert die Verträglichkeit von Zeitentwicklung und Aggregation für alle Anfangsverteilungen. Das bloße Berechnen eines Makrokerns `Q=Lambda P C` aus einer Präparation Λ genügt dafür nicht. Für eine approximative Schließung werden `delta_cl=max_i TV((PC)_i,(CQ)_i)` und ein Horizont k angegeben; die eigene elementare Abschätzung lautet `TV(pP^kC,pCQ^k)≤min(1,k*delta_cl)`. [Definitionen, Beweis und Literatur](emergence_and_closure.md).

Fehlende Geschlossenheit ist ein Befund über die gewählte Darstellung. Projektion kann Gedächtnis erzeugen. Eine Reduktion wird daher nicht allein aufgrund einer kleinen Zustandszahl oder eines hohen Informationsscores als autonome Einheit bezeichnet.

## 10. Emergenzmetriken und Individuation

Für einen deklarierten Interventionskanal wird `EI_q(P)=I_q(Z_t;Z_(t+1))` verwendet. Ein Makrovergleich nennt Partition, Mikropräparation Λ, Makro- und Mikrointerventionsverteilung sowie Zeitschritt. Reine Beobachtungsdaten liefern diese interventionelle Interpretation nicht ohne zusätzliche Annahmen.

Typ 1 bezeichnet hier einen **spezifizierten Vorteil** gemeinsamer oder gröberer Beschreibung: etwa Prognose, Kontrolle, Robustheit, EI oder Synergie gegenüber einer festgelegten Baseline. Diese Ziele bleiben getrennt. Ein positiver SVD-Emergenzwert impliziert keinen positiven EI-Gewinn; ein eigener Rang-eins-Gegenfall steht im [Makrobeispiel](worked_example_causal_emergence.md).

**Optionales Modul (F09, 16. September 2026):** `EI_q` bleibt ein Skalar und kann Redundanz, eindeutige Beiträge und Synergie nicht trennen. [PID und Redundancy Bottleneck](pid_redundancy_bottleneck.md) ergänzt dafür eine Zerlegung (Williams–Beer `I_min`-Atome plus Kolchinsky-Redundancy-Bottleneck) für ein deklariertes Mikro→Makro-Paar, mit sieben Prüfungen im Skript (sechs durchgerechnete Fälle — UNIQUE, XOR, AND, vollständige Kopie, RB(0), `EI_q` daneben statt gleichgesetzt — plus dokumentierte Zitate). `EI_q` wird berichtet, nicht durch die PID-Atome ersetzt. Bekannte Maßabhängigkeit (TWO_BIT_COPY-Fall): siehe Hinweis im Moduldokument.

Eine eigenständige Makrobeschreibung wird über einen aufgabenspezifischen Prüfvertrag untersucht: Grenze, Vorhersage-/Interventionsleistung, dynamische Geschlossenheit, Sparsamkeit und Robustheit. Dies ist ein operationaler Projektvorschlag; ein universelles notwendiges und hinreichendes Individuationskriterium ist weiterhin nicht hergeleitet.

## 11. Thermodynamische und resilienzbezogene Erweiterungen

Für geeignete geschlossene thermodynamische Modelle wird GENERIC als optionales Modul zugelassen:

\[
\dot z=\mathbb J(z)\nabla E(z)+\mathbb M(z)\nabla S_{th}(z),
\]

mit `J^T=-J`, Poisson-/Jacobi-Bedingung, `M^T=M≥0`, `J grad S_th=0` und `M grad E=0`. Dann folgen Energieerhaltung und nichtnegative Entropieproduktion. Die Operatoren erhalten Einheiten passend zu z. Bilanzgrößen und Bedingungen müssen tatsächlich nachgewiesen werden; ein semantischer Score ist keine thermodynamische Entropie. [Ausarbeitung](coupling_layer_afet.md).

Resilienz kann ergänzend über zulässige Zustandsbereiche, kontrollierbare Eingriffe und Störungsbudgets untersucht werden. Das vertiefte [Viabilitätsbeispiel](worked_example_viability.md) zeigt gleiche Erholungsraten bei unterschiedlicher dauerhafter Belastbarkeit sowie einzeln erfüllbare, gemeinsam aber unvereinbare Aufgaben. Für zwei gekoppelte Bestände werden eine exakte Invarianzbedingung, eine optimale Grenzzeit im symmetrischen Fall und der Unterschied zwischen Summenprognose und lokaler Sicherheit hergeleitet. Es liefert keine Herleitung des bisherigen Frame-Scores.

## 12. Selbstähnlichkeit über gekoppelte Beschreibungsebenen

Konjugation, verträgliche Vergröberung und die Komposition gekoppelter Teilmodelle bieten verschiedene Prüffragen zur Leitthese. Verglichen werden angegebene Strukturen bei variablen Größen und dynamischen Abhängigkeiten. Die Beispiele mit konstantem Zeitfaktor decken einen begrenzten Sonderfall ab.

RG-Universalität ist ein optionaler, stärkerer Literaturanschluss für geeignete Teilprobleme. Sie gehört nicht zu Johanns Ausgangsbehauptung und ist keine Voraussetzung dafür, strukturelle Selbstähnlichkeit zu untersuchen. Sollte ein Teilprojekt eine RG-Aussage aufstellen, benötigt diese ihre eigene Herleitung und Prüfung.

Schon die Umparametrisierung `Gamma'=k*Gamma`, `sigma'=sigma/k` erhält tanh(σΓ). Deshalb werden Referenzskalen und Identifizierbarkeit vor dem Vergleich von σ-Werten festgelegt. Eine gemeinsame normierte Grenzfunktion kann untersucht werden; sie wird nicht aus gleichen Defaults abgeleitet.

Der [Literaturabgleich](LITERATURE_CONNECTIONS.md) unterscheidet etablierte Resultate, aktuelle Forschungsansätze und die eigenen begrenzten Rechnungen. Die bisherigen Modellprüfungen sind über [VERIFICATION.md](VERIFICATION.md), die Ergänzungen der Revision 3.2 über [TRANSFORMATION_VERIFICATION.md](TRANSFORMATION_VERIFICATION.md) reproduzierbar.

Die bereits umgesetzten Paketkorrekturen bleiben gültige Arbeitsschritte. Diese Revision liefert konsistente Modellbeschreibungen und reproduzierbare Rechnungen. Ihre empirische Eignung über Domänen hinweg bleibt Gegenstand der [Roadmap](ROADMAP.md).

## 13. Transformation als Verbindung von Einheit, Kontext und System

Dieselbe Einheit kann intern als System beschrieben werden und mehreren, auch überlappenden Systemen angehören. Eine Systemzugehörigkeit bestimmt unter anderem, welche Größen beobachtet, welche Einflüsse berücksichtigt und welche Anforderungen angewendet werden. Verschiedene Zugehörigkeiten dürfen verschiedene relationale Werte hervorbringen; sie müssen das nicht in jedem Zustand tun.

Für einen gemeinsamen Untersuchungszustand z und Kontext c sei

\[
y_\alpha=\pi_\alpha(z,c,t),\qquad
\dot z=F(z,u,w,c,t),\qquad \dot c=G(c,z,u,w,t).
\]

Die dazugehörige deterministische Ableitung ist

\[
\dot y_\alpha=D_z\pi_\alpha F+D_c\pi_\alpha G+\partial_t\pi_\alpha.
\]

Die Darstellung kann sich also selbst verändern. Bei einer Zeitänderung dτ/dt=a>0 wird die gesamte rechte Seite durch a geteilt. Kontextabhängige Parameterfunktionen werden mit ihren Abhängigkeiten differenziert. Diskrete, stochastische und hybride Modelle erhalten die jeweils passenden Transformationsregeln.

Für den Formalismus werden folgende Verträglichkeitsbedingungen eingeführt:

1. **Gemeinsame Größen:** Sichten auf denselben physischen Bestand müssen nach Rücktransformation übereinstimmen. Relationale Größen wie Reserve oder Anteil dürfen verschieden sein. Überlappende Zugehörigkeiten verdoppeln keinen Bestand. Diese Bedingung bleibt für deterministische Bestände unverändert. **Optionales Modul (F08, 16. September 2026):** [Sheaf-Kontextualität](sheaf_contextuality.md) ergänzt sie für stochastische/mehrsichtige Überlappungen, bei denen randverträgliche lokale Verteilungen dennoch kein gemeinsames globales Schnittstück besitzen (Abramsky–Brandenburger). Das ist dann ein Befund (quantifiziert über die Contextual Fraction), keine Modellierungslücke, und ersetzt VB1 nicht. Voraussetzung dafür (siehe Moduldokument §6): die Sichten y_α sind unabhängig spezifizierte Beobachtungsmodelle je Kontext, nicht bloß Projektionen desselben angenommenen z — im letzteren Fall existiert die gemeinsame Verteilung immer trivial, und ein positiver CF-Wert wäre ein Modellierungsfehler.
2. **Dynamische Geschlossenheit:** Eine Makrodynamik muss aus ihren angegebenen Zuständen, Eingängen und Regeln bestimmbar sein. Weggelassene Abhängigkeiten können zusätzliche Zustände oder Gedächtnis verlangen.
3. **Zusammensetzen und Zerlegen:** Für z=R(ξ) wird im glatten autonomen Fall DR·F_fine=F∘R geprüft. Innere Flüsse müssen zur äußeren Bilanz passen. Eine Projektion erlaubt keine eindeutige Rückzerlegung ohne Zusatzinformation.
4. **Gemeinsame Eingriffe:** Gleichzeitig geltende Anforderungen müssen durch einen gemeinsam ausführbaren Eingriff erfüllt werden. Geteilte Budgets und Regelkonflikte werden in einem gemeinsamen Steuerraum erfasst.
5. **Aufgabentauglichkeit:** Geschlossene Dynamik genügt nicht für jede Aufgabe. Beispielsweise kann die Gesamtsumme exakt vorhergesagt werden, während für lokale Sicherheit zusätzlich ihre Verteilung benötigt wird.

Metaregeln können festlegen, welche Eingriffe, Zugehörigkeitswechsel oder Beschreibungen zugelassen sind. Veränderliche Regeln werden als explizite Zustände, Eingänge oder Ereignisgesetze dargestellt. Ihre bloße Benennung ersetzt kein Wirkungsgesetz.

Diese Erweiterung gibt der Leitthese eine prüfbare Form: Selbstähnliche Muster können bei Transformationen und wiederholter Komposition erhalten bleiben, während Werte, Funktionen und Regeln kontextabhängig variieren. [Die Kernausarbeitung](context_transformations.md) definiert auch Fehlerfortpflanzung über mehrere Ebenen. [Emergenz und Geschlossenheit](emergence_and_closure.md) ergänzt bewegliche Darstellungen und Aufgabeninformation; [Pufferfähigkeit](worked_example_viability.md) rechnet einen vollständigen Modellfall durch.
