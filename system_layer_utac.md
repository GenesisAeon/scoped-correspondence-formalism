# UTAC — Systemschicht, Revision 3

Stand: 16. September 2026. Notation und Evidenzregeln: [FORMALISM.md](FORMALISM.md).

## 1. Ein Systemmodell angeben

Der Ausgangspunkt ist eine begründete Systemgrenze mit Zustand z, Eingabe u und Beobachtung y. Für kontinuierliche Modelle gilt `dot z=f(z,u,t)`, für diskrete Modelle `z_(n+1)=F(z_n,u_n)`. Hybride Modelle ergänzen Ereignisbedingungen und Reset-Abbildungen. Die konkrete physikalische oder semantische Bedeutung wird pro Domäne erklärt.

Ob f analytisch gelöst, numerisch integriert oder als exakter Update umgesetzt wird, entscheidet nicht über die Existenz der modellierten Dynamik. Eine Uhr mit `phi(t)=omega*t mod 2*pi` hat die Dynamik `dot phi=omega`, auch ohne Integrator. Ein Ausgabewrapper kann dagegen ausschließlich bereits berechnete Größen darstellen.

Die Softwareklassifikation unterscheidet: dynamisches Modell, Speicher/Monitor, Beobachtungs-/Ausgabeabbildung, Rechenwerkzeug und Orchestrator. Kombinationen sind möglich. Eine Klasse entspricht nicht notwendig einem System; die Implementierungsgrenze legt keine natürliche Individuation fest.

## 2. Komposition und Individuation

`Delta_S=S_composition-S_baseline` ist eine mögliche Hypothese über zusätzliche Stabilität. Dafür braucht es eine konkrete Partition, dieselbe Stabilitätsmetrik, vergleichbare Randbedingungen und eine unabhängige Baseline. Der Schwellenwert für einen relevanten Effekt wird vor der Prüfung festgelegt, einschließlich Unsicherheit.

Die frühere Definition „System genau dann, wenn Excess-S>0“ wird nicht als allgemeines Kriterium fortgeführt. Sie würde unter anderem neutral stabile, getriebene oder chaotische Systeme unzureichend behandeln. Die Gleichsetzung mit operationaler Geschlossenheit/Autopoiesis ist nicht bewiesen. Eine engere Klasse „durch Komposition zusätzlich stabilisierte Einheit“ kann mit dieser Hypothese untersucht werden.

## 3. Statische Antwort und dynamische Erholung

Eine mögliche Antwortkurve ist

\[
p(u)=p_{max}/(1+\exp[-\beta_{response}(u-\Theta_u)]).
\]

Ihr Anstieg im Mittelpunkt beträgt `p_max*beta_response/4`. Die Einheit von β ist `1/[u]`. Die Kurve legt weder eine ODE noch eine Erholungszeit fest.

Für `dot z=-(z-p(u))/tau` mit festem u ist das Gleichgewicht z*=p(u), der lokale Eigenwert −1/τ und `S_rec=1/tau`. Für `dot H=rH(1-H/H*)` mit konstantem H*>0 ist dagegen `S_rec=r`. Beide Beziehungen folgen aus dem jeweils angegebenen Modell. Es gibt keine allgemeine Gleichheit `beta_response=S_rec`.

Für einen glatten autonomen Fixpunkt:

\[
A=D_zf(z_*),\quad S_{rec}=-\max\operatorname{Re}\operatorname{eig}(A).
\]

`S_rec>0` bedeutet lokale exponentielle asymptotische Stabilität der Linearisierung. Bei Null-Eigenwerten entscheidet die lineare Analyse nicht allein. Für periodische, nichtautonome, stochastische und hybride Prozesse sind passende Trajektorien-, Floquet-, stochastische oder Ereignisanalysen nötig. Erhaltungsgrößen können neutrale Modi erzeugen; dann ist der zulässige Störungsraum anzugeben.

Ein diskreter linearer Modus `delta z_(n+1)=m*delta z_n` hat bei festem Δt den Exponenten `log|m|/Delta_t`. Für Euler-Relaxation ist m=1−rΔt. Die kontinuierliche Rate r und die diskrete Rate stimmen nur im Grenzfall kleiner Schritte überein.

## 4. Resilienzgrößen getrennt operationalisieren

| Begriff | Mögliche Messgröße | Einschränkung |
|---|---|---|
| Rückkehr | `S_rec`, Halbwertszeit, endliche Erholungszeit | lokaler bzw. aufgabenspezifischer Begriff |
| Resistance | Zustandsänderung pro spezifizierter Störung oder erforderliche Störungsstärke | Definition, Einheit und Zeitraum nötig; nicht automatisch β oder S |
| Precariousness | Abstand des aktuellen Zustands zu einer angegebenen Grenze | Metrik und Grenze müssen existieren |
| Latitude | charakteristische Breite eines relevanten Beckens | nicht automatisch dessen Wahrscheinlichkeit |
| Basin Stability | `B_prob=P_mu(z0 gehört zum Zielbecken)` | abhängig von Störungsverteilung μ und Zielattraktor |
| Rate | `dot z` oder `dot u` | Zustandsrate und Geschwindigkeit der äußeren Ansteuerung unterscheiden |
| Panarchy | konkret modellierte skalenübergreifende Abhängigkeiten | kein vorgegebener einzelner Zahlenwert |

`Theta_u-u` ist ein Abstand im Kontrollparameterraum. Ein Abstand zu einer Separatrix liegt im Zustandsraum. Beides ist nur mit einer begründeten Abbildung vergleichbar. [Begrifflicher Ausgangspunkt: Walker et al.](https://ecologyandsociety.org/vol9/iss2/art5/inline.html).

Basin Stability integriert die Indikatorfunktion des Zielbeckens gegen μ. Monte-Carlo-Sampling schätzt diese Wahrscheinlichkeit. Es misst nicht ohne Weiteres eine Länge. Auch ein System mit nur einem betrachteten Zielattraktor kann eine sinnvolle Basin- oder Überlebensfrage haben; Bistabilität ist keine allgemeine Voraussetzung. [Menck et al.](https://www.pik-potsdam.de/members/kurths/recent-selected-publications/nphys2516.pdf).

## 5. Korrigierte kubische Modellfamilie

Wir wählen ausdrücklich einen **dimensionslosen Zustand x** und feste Kontrollparameter a,b:

\[
\tau\dot x=-x^3+ax+b=-U'(x),\qquad
U(x)=x^4/4-ax^2/2-bx,\quad\tau>0.
\]

τ ist die Zeitskala. Für einen dimensionalen Zustand z muss etwa `x=(z-z_ref)/z_scale` mit `z_scale>0` festgelegt werden. Eine zeitabhängige Referenz erfordert zusätzliche Ableitungsterme und ist nicht impliziert.

Die frühere unzentrierte Formel `dot R_ctrl=-R_ctrl^3+a(R_ctrl-Theta)+b` wird **nicht weiterverwendet**. Sie ist bei Θ≠0 nicht durch bloße Umbenennung gleich der zentrierten kubischen Dynamik. Ebenso wird ein Kontrollparameter nicht ohne Begründung zum dynamischen Zustand erklärt.

Die Gleichgewichte erfüllen `x^3-a*x-b=0`. Der Diskriminant ist

\[
D=4a^3-27b^2.
\]

- D>0: drei verschiedene reelle Gleichgewichte, außen stabil, innen instabil.
- D<0: ein reelles, stabiles Gleichgewicht.
- D=0: mindestens eine Mehrfachwurzel; nicht-hyperbolischer Grenzfall, gesondert untersuchen.

Die Bistabilitätsregion ist also `a>0` und `|b|<2*a^(3/2)/(3*sqrt(3))`. Ein einzelner universeller Schwellenwert `a_crit=0` beschreibt nur den symmetrischen Schnitt b=0.

### 5.1 Ableitung im symmetrischen Fall

Für b=0 ist x=0 immer ein Gleichgewicht. Bei a>0 kommen `x=±sqrt(a)` hinzu. Die lokale Ableitung ist `(a-3*x^2)/tau`. Daher:

\[
S_{rec}(0)=-a/\tau,\qquad
S_{rec}(\pm\sqrt a)=2a/\tau.
\]

`a=-tau*S_rec(0)` ist eine **bedingte Modellidentität** am Referenzgleichgewicht. Bei a>0 ist dieses instabil. Kennt man nur eine Trajektorie nahe dem stabilen Ast, misst man dort eine andere Rate. Ohne bekannte Zeitskala und unabhängige Identifikation eliminiert diese Umparametrisierung keinen freien Parameter.

Für b≠0 ist x=0 kein Gleichgewicht; die Ableitung am Ursprung bleibt eine lokale Ableitung, darf aber nicht als Erholungsrate eines dortigen Fixpunkts bezeichnet werden. Bei a=b=0 zeigt `dot x=-x^3/tau` trotz verschwindender Linearisierung algebraische Rückkehr.

### 5.2 Becken und Dimension

Für a>0,b=0 liegt die Grenze der beiden Becken bei x=0. Der Abstand des positiven Attraktors zur Grenze beträgt `ell_basin=sqrt(a)` in x-Koordinaten. Unter einer symmetrischen Gleichverteilung auf [-3,3] ist die Wahrscheinlichkeit für das positive Becken dagegen 1/2, sowohl bei a=1 als auch bei a=4. Ein Vergleich von Sampling und analytischer Distanz muss dieselbe Zielgröße verwenden.

Diese Bifurkation schafft neue stabile Alternativen innerhalb desselben eindimensionalen Zustandsraums. Ein zusätzliches Vorzeichenlabel ist keine neue unabhängige Dimension. Ein Nachweis zusätzlicher erforderlicher Zustands- oder Gedächtnisdimensionen braucht einen eigenen Modellvergleich.

Die kubische Dynamik ist eine vorgeschlagene Erweiterung des Modellrepertoires. Eine exakte Ableitung der Sigmoidkurve als ihr monostabiler Grenzfall liegt nicht vor.

## 6. Frame-Brücke: dimensionslose, unkalibrierte Hypothese

Ein möglicher Kandidat lautet mit festgelegter Referenzbreite `ell_ref>0`:

\[
B=\ell_{basin}/\ell_{ref},\qquad
P=\alpha\frac{\rho}{1-\rho},\qquad
F_{frame}=\frac{B}{B+P},\quad\alpha>0.
\]

B und P sind dimensionslos. `0≤rho<1` und `B+P>0` sind Voraussetzungen. Bei gemeinsamem Einheitenwechsel von ell und ell_ref bleibt F gleich. Der zusätzliche Maßstab und α müssen unabhängig begründet oder kalibriert werden; die Normierung beseitigt nur den Einheitenfehler.

Im stationären M/M/1-Modell ist `rho=lambda_arrival/mu_service` und die mittlere Kundenzahl `rho/(1-rho)`. Das folgt aus der geometrischen stationären Verteilung. Die mittlere Aufenthaltszeit ist dagegen `1/(mu_service-lambda_arrival)`. Eine Übertragung auf Informationsströme benötigt passende Ankunfts-, Dienst- und Größenannahmen. Ein gemessener Ausgangsdurchsatz allein charakterisiert Überlastung nicht: bei überfüllter Warteschlange kann er an der Dienstkapazität sättigen.

Für rho≥1 wird diese stationäre Formel nicht extrapoliert. Die Stelle B=P=0 ist undefiniert. Weder 0,84 noch 1/16 werden hier als allgemeine Schwelle bestätigt. Es fehlt insbesondere eine unabhängig belegte Verbindung zwischen diesem F, einem Stabilitätsverlust und einer erforderlichen zusätzlichen Beschreibungsdimension.

## 7. Anforderungen an eine Domänenanwendung

Zuerst Modell, Eingaben, Beobachtung und Zeiteinheiten festlegen. Dann verwendete Metriken, schätzbare Parameter und Unsicherheiten angeben. Erst danach Kompositionsvorteile oder zusätzliche Vorhersageleistung gegen geeignete Referenzen prüfen. Das bloße Vorhandensein eines Integrators oder einer bekannten Gleichungsform erfüllt diese empirische Aufgabe nicht.

## 8. Makroeinheiten durch Geschlossenheit untersuchen

Ein eigenes Makromodell muss mit der angegebenen Mikrodynamik verträglich sein. Für endliche Markov-Ketten lautet die hier verwendete starke Aggregationsbedingung `PC=CQ`. Bei approximativer Gültigkeit werden Fehler und Zeithorizont mitberichtet. Bei fehlender Gültigkeit sind verborgene Anfangsdaten und Gedächtnis mögliche Ursachen. [Definitionen und Fehlerschranke](emergence_and_closure.md).

Ein Kompositionsvorteil, eine Markov-Schließung und eine räumliche/biologische Individuation sind unterschiedliche Befunde. Zur Untersuchung einer Makroeinheit dient der aufgabenspezifische Prüfvertrag des Methodendokuments. Die SVD- und EI-Beispiele zeigen, warum ein einzelner positiver Kennwert dafür nicht genügt.

## 9. Pufferfähigkeit über zulässige Bereiche

Neben Becken und Rückkehr kann ein sicherer Bereich K mit konkreten Eingriffen und Störungen definiert werden. Die Frage lautet dann: Aus welchen Anfangszuständen existiert eine zulässige Strategie, die das System unter den zugelassenen Störungen über den festgelegten Horizont in K hält?

Das verlangt eine Informationsstruktur: Darf die Strategie die aktuelle Störung sehen, welche Verzögerungen bestehen, welche Ressourcen sind verfügbar? Ein vollständig bekannter zukünftiger Störungsverlauf ist eine stärkere Annahme als kausale Rückkopplung.

Das [skalare Viabilitätsbeispiel](worked_example_viability.md) kommt ohne solche versteckten Annahmen aus: eine konstante maximal zulässige Maßnahme genügt genau für den dort angegebenen robusten Randfall. Seine Belastungsgrenze hat die Einheit einer Rate; aktueller Abstand, Erholungsrate und Überlebenszeit werden separat berichtet.

## 10. Bedeutung für Typ 2 und Frame

Eine gescheiterte Prognose mit einer kleinen Darstellung kann zusätzliche Zustände oder Gedächtnis motivieren. Der Gewinn wird gegen alternative Modelle gleicher Komplexität und auf unabhängigen Bedingungen geprüft. Ein neuer Attraktorast, eine größere SVD-Rangzahl und eine zusätzliche Delay-Koordinate bedeuten jeweils etwas anderes.

Die Frame-Hypothese aus Abschnitt 6 bleibt ausdrücklich unkalibriert. Weder Einbettungstheoreme noch Viabilitätsbedingungen liefern ohne zusätzliche Herleitung eine universelle numerische Frame-Schwelle.
