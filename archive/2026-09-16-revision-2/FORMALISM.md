# CREP–UTAC–AFET — konsolidierter Formalismus, Revision 2

Stand: 16. September 2026. Ersetzt die aktuellen mathematischen Aussagen von Entwurf 1. Historie und Rücknahmen: [DESIGN.md](DESIGN.md), [REVISION_2026-09-16.md](REVISION_2026-09-16.md).

## 1. Absicht und Status

„Crep war Information, UTAC dann Systeme, und AFET war die Kopplung für Thermodynamik. So war es mal gedacht.“ — Johann, 15. September 2026.

Diese Rollen werden beibehalten. Der Rahmen verbindet sie durch Beobachtungsmodelle, Dynamiken und Kopplungsgesetze mit angegebenen Voraussetzungen. Er behauptet keine mathematische Gleichheit aller drei Beschreibungsebenen. Seine mögliche Einheit liegt im konsistenten Umgang mit Zuständen, Beobachtungen, Eingaben und Evidenz.

**Leitidee ist Selbstähnlichkeit, wie von Johann am 16. September ausdrücklich klargestellt.** Die Revision korrigiert Gleichsetzungen, die in die Dokumente gelangt waren. Wiederkehrende Organisations- oder Dynamikformen erlauben unterschiedliche Variablen, Einheiten, Parameter und Randbedingungen.

### Selbstähnlichkeit präzise untersuchen

| Aussageebene | Zulässige Aussage | Erforderlicher Nachweis |
|---|---|---|
| Strukturelle Analogie | Zwei Fälle zeigen ein vergleichbares Organisationsmuster. | genaue Beschreibung von Gemeinsamkeiten und Unterschieden |
| Mathematische Selbstähnlichkeit | Eine angegebene Transformation erhält eine bestimmte Struktur exakt oder näherungsweise. | Transformation, Skalen, Parameterabbildung, Bereich und gegebenenfalls Fehlermaß |
| Empirische Selbstähnlichkeit | Die behauptete Strukturbeziehung bewährt sich an unabhängig geprüften Daten. | Messmodell, Unsicherheit, Referenzmodelle und zurückgehaltene Daten |

Für autonome deterministische Modelle mit Entwicklungsoperatoren `Phi_j^t` könnte eine konkrete Prüffrage lauten:

\[
T\circ\Phi_j^t\;\approx\;\Phi_k^{c t}\circ T,\qquad c>0.
\]

T bildet Zustände ab, c die Zeitskala; Parameter und zulässige Anfangszustände sind vorzugeben. Für eine näherungsweise Beziehung werden Zeitraum, Norm und akzeptierte Abweichung festgelegt. Bei kontrollierten, stochastischen oder grob beobachteten Systemen müssen zusätzlich Eingaben, Übergangsverteilungen bzw. Informationsverlust berücksichtigt werden. Diese Gleichung ist ein Prüfschema, kein bereits nachgewiesenes Gesetz des Ökosystems.

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

Ein allgemeiner dynamischer Kopplungsansatz ist

\[
\dot z_i=f_i(z_i,u_i)+\sum_{j\ne i}g_{ij}(z_i,z_j,u).
\]

Eine Informationsabhängigkeit oder ein Funktionsaufruf ist ein eigener Evidenztyp und belegt nicht automatisch einen solchen dynamischen Term.

Für den thermodynamischen Spezialfall müssen Flüsse J und entropiekonjugierte Kräfte X identifiziert sein. Erst dann wird der lineare Ansatz

\[
J=LX,\qquad \dot S_{prod}=X^TLX\ge0
\]

geprüft. Dafür muss `L_s=(L+L^T)/2` auf dem zulässigen Kraftraum positiv semidefinit sein. Symmetrie/Reziprozität erfordert zusätzliche mikroskopische Voraussetzungen und gegebenenfalls die Onsager-Casimir-Paritäten. Ein asymmetrischer Drift-Jacobian ist kein Beweis für gebrochene thermodynamische Reziprozität.

**Es gibt keine allgemeine Identität zwischen `eta_info`, Panarchy, `A_ij` und `L_ij`.** Panarchy bezeichnet hier skalenübergreifende Abhängigkeiten; ihre jeweilige Operationalisierung wird genannt. exp und tanh bleiben mögliche, begründungspflichtige Antwortfunktionen. Aus „Rate“ bzw. „normiert“ folgt keine eindeutige Funktionswahl.

Siehe [Kopplungsschicht](coupling_layer_afet.md) und [Wärmebeispiel](worked_example_heat_exchange.md).

## 7. Evidenz und Grenzen

Jede Aussage erhält einen Status: Definition, Standardresultat mit Voraussetzungen, Ableitung im angegebenen Modell, synthetische Prüfung, Codebefund, empirische Schätzung, Hypothese oder nicht untersucht. Eine passende Formel und ein grüner Test allein sind keine empirische Bewährung.

Die ursprünglichen Behauptungen `beta=S`, `V=Panarchy=L`, die unzentriert/zentriert vermischte Herleitung und die allgemeinen exp/tanh- sowie Dimensionsentstehungsbeweise sind zurückgenommen. Der frühere Gemini-Gegencheck ist als historisches Reviewereignis dokumentiert; seine behauptete Vollständigkeit trägt angesichts der Gegenbeispiele nicht. Die Quelle `Gemini.txt` liegt dieser Revision nicht vor, sodass über dessen genaue Prüfmethode keine Aussage getroffen wird.

Die bereits umgesetzten Paketkorrekturen bleiben gültige Arbeitsschritte. Diese Revision liefert konsistente Modellbeschreibungen und reproduzierbare Rechnungen. Ihre empirische Eignung über Domänen hinweg bleibt Gegenstand der [Roadmap](ROADMAP.md).
