# Nichtstationäre Treiber, wechselnde Raten und Kippprozesse

**Wissenschaftliche Auswertung und Arbeitskonzept · 21. September 2026**

Untersuchter Stand: [GenesisAeon/scoped-correspondence-formalism, Commit 96567288a5ba80e410208226a8cc74d240af0a3c](https://github.com/GenesisAeon/scoped-correspondence-formalism/tree/96567288a5ba80e410208226a8cc74d240af0a3c), zuletzt geändert am 20. September 2026. Die GitHub-Dateien wurden für diese Untersuchung nicht verändert.

**Ergebnis:** Die neuen Versuche stützen den Einwand gegen das Fortschreiben einer einzigen über lange und wechselhafte Zeiträume geschätzten Rate. Sie belegen bislang weder ein allgemeines Versagen linearer Modelle noch einen überwiegend exponentiellen äußeren Treiber oder einen identifizierten Kipppunkt. Der wissenschaftlich produktive nächste Schritt ist ein Modell, das **Treiberverlauf, Systemantwort, Zusammensetzung der beobachteten Population und Messprozess** unterscheidet. Für das eigentliche Kippen passt insbesondere die Theorie nichtautonomer Systeme und des rateninduzierten Kippens.

Die stärkste weiterführende Arbeitshypothese lautet: **Eine zeitlich veränderliche Belastung, eine nachlassende Anpassungsfähigkeit oder eine veränderte Zusammensetzung können eine zuvor brauchbare Makrobeschreibung unbrauchbar machen. Welche Ursache vorliegt, muss mit unterschiedlichen Beobachtungen und Kontrollfällen unterschieden werden.**

## 1. Was tatsächlich geprüft wurde

Erfasst wurden der aktuelle GitHub-Baum mit 458 Einträgen und die jüngsten 25 Commits. Alle 69 aktuellen Python-Quelldateien wurden anhand ihrer Git-Blob-SHA geprüft. Die drei Datendateien stimmen bytegenau mit den SHA-256-Werten des Manifests überein.

| Datensatz | Umfang im Repository | Verwendeter Pilot |
|---|---:|---|
| OWID/JHU, weltweite COVID-Meldungen | 1.143 Tage, 2020–2023 | 45 Kalibrierungstage, 14 Testtage; zwei Folgevarianten |
| NOAA, globale Temperaturabweichung | 146 Jahreswerte, 1880–2025 | 1880–1999 → 2000–2025 |
| USGS, weltweite Erdbeben ab Magnitude 6 | 3.974 Ereignisse bis 20.09.2026 | Jahreszahlen 2000–2019 → 2020–2025; Teiljahr 2026 ausgeschlossen |

Vier einschlägige Prüfsuiten wurden wirklich ausgeführt: Datenherkunft 4/4, COVID 8/8, NOAA 6/6 und Erdbeben 6/6. **24/24 Checks bestanden.** Anschließend wurden die elementaren Schätzer unabhängig mit NumPy nachgerechnet, ohne die Fit-Funktionen des Pakets zu importieren. Die veröffentlichten RMSE-Werte und der COVID-Bruchtermin wurden reproduziert.

Der Hashvergleich bestätigt die Integrität des Repository-Snapshots, nicht für sich allein jede historische Messung. Die Quellen- und Verarbeitungskette ist im aktuellen Datenmanifest dokumentiert. Ein erneuter vollständiger Vergleich mit allen heute abrufbaren Originalarchiven wurde nicht durchgeführt; insbesondere lebende Kataloge können revidiert werden.

Alle zusätzlichen Fenstervergleiche in diesem Bericht sind **retrospektive Diagnosen**, nachdem die ursprünglichen Ergebnisse bekannt waren. Sie wurden nicht als neue unabhängige Bestätigung ausgegeben. Die synthetischen Beispiele sind mathematische Kontrollfälle, keine Anpassungen an die drei Datensätze.

## 2. Was die drei Piloten aussagen

### 2.1 COVID: Schon ein Exponentialmodell kann an einer gemittelten Rate scheitern

Die Originalfamilie lautet

\[
y(t)=y_0\exp(rt).
\]

Sie ist bereits exponentiell in der Zeit. Pilot A schätzt eine einzige relative Wachstumsrate über ein Fenster mit Anstieg, Rückgang und erneutem Anstieg.

| Modell | Kalibrierung | Geschätztes r pro Tag | RMSE im selben Testfenster |
|---|---|---:|---:|
| Persistenz | letzter beobachteter Wert | — | 15.932,68 |
| A: ein Exponentialmodell | 27.01.–11.03.2020 | 0,00744 | 17.428,70 |
| B: dasselbe Exponentialmodell | 26.02.–11.03.2020 | 0,12100 | 5.980,65 |
| C: zwei getrennte log-lineare Segmente | ursprüngliches Gesamtfenster; jüngstes Segment extrapoliert | 0,08103 | 12.603,00 |

Die Einheit des RMSE ist Fälle pro Tag im gleitenden Siebentagesmittel. Im Testfenster 12.–25.03.2020 entspricht das Wachstum zwischen den beiden Endpunkten einer mittleren logarithmischen Rate von 0,15349 pro Tag und einer Verdopplungszeit von rund 4,52 Tagen.

**Belastbare Schlussfolgerung:** Die konstante Rate aus dem langen Fenster beschreibt den späteren Abschnitt schlecht. Das ist Evidenz für eine unangemessene zeitliche Zusammenfassung. Es ist kein Nachweis, dass eine exponentielle Modellfamilie grundsätzlich benötigt oder verworfen werden muss: A und B gehören bereits derselben Familie an.

Auch die Anfangshöhe spielt eine Rolle. Wird nur die Rate aus A verwendet, die Vorhersage aber am letzten beobachteten Wert verankert, sinkt der RMSE auf 15.644,96. Das schlägt Persistenz knapp, bleibt aber weit hinter B. Damit trägt neben der falschen mittleren Rate auch das zu niedrige extrapolierte Niveau zum ursprünglichen Misserfolg bei. Dies ist ein zusätzlicher Diagnosefall, kein nachträglich ersetztes Originalergebnis.

Der unabhängig gescannte optimale Bruchtermin bleibt der **20. Februar 2020**. Pilot C lässt einen Sprung zwischen den Segmenten zu und kann daher sowohl Niveau- als auch Ratenunterschiede abbilden. Ein solcher statistischer Bruch identifiziert keinen physikalischen oder epidemiologischen Kipppunkt. Die Änderung der Falldefinition in Hubei am 12. Februar ist durch PAHO/WHO dokumentiert [R1]. Wie viel des gefundenen Bruchs auf diese Meldedynamik, tatsächliche Ausbreitung oder die Mischung verschiedener Länder entfällt, wurde im Weltaggregat nicht getrennt identifiziert.

### 2.2 NOAA: Ein kürzeres lineares Modell funktioniert wesentlich besser

Original: OLS-Gerade auf 1880–1999, danach unveränderte Extrapolation auf 2000–2025. Ihr RMSE beträgt 0,46044 °C, gegenüber 0,43011 °C für die konstante Fortschreibung des Werts von 1999.

Zur Diagnose wurden vier vollständig ausgewiesene Kalibrierungsfenster mit derselben linearen Modellfamilie verglichen. Alle Parameterschätzungen enden 1999:

| Kalibrierungsfenster | Trend in °C/Jahr | RMSE 2000–2025 in °C |
|---|---:|---:|
| 1880–1999, Original | 0,00532 | 0,46044 |
| 1950–1999 | 0,01079 | 0,26895 |
| 1970–1999 | 0,01636 | 0,14131 |
| 1980–1999 | 0,01268 | 0,20617 |
| Persistenz ab 1999 | 0 | 0,43011 |

Das 30-Jahres-Fenster reduziert hier den Fehler gegenüber der Originalgeraden um rund 69 %. **Linearität allein erklärt das Scheitern damit nicht.** Das zeitliche Fenster und der wechselnde Hintergrund sind entscheidend. Zugleich ist das kürzeste Fenster nicht das beste; eine möglichst kurze Kalibrierung ist keine allgemeine Lösung.

Ein ergänzender, ebenfalls nachträglich definierter Test verwendet elf Ursprungsjahre von 1969 bis 2019 im Fünfjahresabstand, jeweils mit fünf folgenden Testjahren. Für die insgesamt 55 Testjahre ergeben sich:

| Verfahren | Gepoolter RMSE in °C |
|---|---:|
| Persistenz am jeweiligen Ursprung | 0,13761 |
| Linearer Fit ab 1880 bis zum jeweiligen Ursprung | 0,26506 |
| Linearer Fit auf die jeweils letzten 30 Jahre | 0,11931 |

Das Ergebnis stützt eine lokale beziehungsweise adaptive Beschreibung, beweist aber weder das optimale Fenster noch einen Kipppunkt. Die 30-Jahres-Gerade gewinnt auch nicht in jedem einzelnen Block. Kalibrierungsbereiche überlappen, die historischen Daten waren zugänglich, und es wurden keine kausalen Antriebe identifiziert.

Eine globale Temperaturanomalie allein misst keinen externen Treiber. Auch eine Beschleunigung der beobachteten Temperatur legt dessen Funktionsform nicht eindeutig fest. Zudem hängt ein Exponentialfit an eine Temperaturanomalie problematisch vom gewählten Nullpunkt ab; ein Wechsel der Referenzperiode kann die Kurvenform relativ zu null und das Vorzeichen ändern.

### 2.3 Erdbeben: Streuungsmodell und Vorhersagemittel trennen

Der Pilot vergleicht zwei konstante Vorhersagen: das Kalibrierungsmittel von 153,95 Ereignissen pro Jahr und den letzten Kalibrierungswert von 145. Ihre RMSE-Werte betragen 28,78 beziehungsweise 22,96 Ereignisse pro Jahr. Allein dieser Vergleich sagt wenig darüber, ob ein homogener Poisson-Prozess angemessen ist.

Eine zusätzliche Verteilungsdiagnose ergibt schon auf den 20 Kalibrierungsjahren:

\[
\bar N=153{,}95,\qquad s_N^2=486{,}26,\qquad
\frac{s_N^2}{\bar N}=3{,}16.
\]

Unabhängige Poisson-Jahreszahlen mit gleicher Rate besitzen dagegen Varianz gleich Mittelwert. Der übliche näherungsweise Dispersionstest ergibt `D=60,01` bei 19 Freiheitsgraden und einen oberen p-Wert von etwa `3,85 × 10⁻⁶`. Das ist ein explorativer Test genau dieser Nullannahme, keine Wahrscheinlichkeit, dass eine bestimmte alternative Ursache wahr ist.

**Folgerung:** Die Beschreibung als gewöhnliche Stichprobenstreuung eines einfachen homogenen Poisson-Prozesses ist zu knapp. Überdispersion ist mit Ereignisclustern, heterogenen oder wechselnden Raten und weiteren Katalogeffekten vereinbar. Der Test entscheidet nicht zwischen diesen Erklärungen und weist kein Kippen nach. Ein unverändertes langfristiges Mittel und zeitliche Cluster schließen sich ebenfalls nicht aus.

Zwei konkrete Dokumentationspunkte sollten korrigiert werden:

- Die Aussage, kein Testjahr übertreffe das Kalibrierungsmittel, ist falsch: **2021 enthält 157 Ereignisse**, gegenüber dem Mittel 153,95.
- Der Status „reviewed“ beschreibt den Bearbeitungsstatus vorhandener Ereignisse. Er allein beweist weder die Vollständigkeit eines Katalogs noch das Fehlen sämtlicher Erfassungs- oder Revisionsprobleme [R2].

Für Nachbebencluster sind selbstanregende Punktprozesse und ETAS fachlich viel näherliegend als eine globale exponentielle Zeitkurve [R3]. Der weltweite Katalog ab Magnitude 6 lässt allerdings kleinere auslösende Ereignisse aus und vermischt tektonische Regionen. Eine mechanistische ETAS-Auswertung sollte auf einen passend vollständigen regionalen Katalog mit geeigneter Magnitudenschwelle begrenzt werden.

## 3. Vier Begriffe, die nicht zusammenfallen

| Begriff | Bedeutung | Konsequenz für die Beobachtung |
|---|---|---|
| Linearer Zeittrend | `y(t)=a+bt` | Eine konstante absolute Steigung kann über längere wechselhafte Abschnitte ungeeignet sein. |
| Lineare Dynamik | z. B. `ẏ=ry` | Diese lineare homogene Differentialgleichung erzeugt bereits exponentielles Wachstum oder Abklingen. |
| Zeitlich konstante Parameter | z. B. ein einziges r für alle Phasen | Diese Annahme ist im langen COVID-Fenster problematisch. |
| Homogene Population / Raumstruktur | Alle Teilprozesse besitzen dieselben wirksamen Eigenschaften. | Ein Weltaggregat kann diese Annahme verletzen, selbst wenn einzelne Teilprozesse einfach sind. |

Exponentielles Wachstum ist deshalb kein allgemeines Gegenargument gegen lineare Differentialgleichungen. Umgekehrt braucht ein Kippprozess keinen exponentiellen Antrieb. Im lokalen Faltenmodell `ẋ=u(t)−x²` verschwinden bei einer **linear** fallenden Größe `u(t)=u₀−vt` die stationären Lösungen, sobald der eingefrorene Parameter null unterschreitet. Die reale dynamische Passage kann gegenüber dieser statischen Grenze verzögert sein.

Ein exponentiell steigender Messwert reicht auch nicht, um einen exponentiellen äußeren Treiber nachzuweisen. Wenn `u(t)=u₀e^{gt}`, ist dessen logarithmische Rate `d ln u/dt=g` konstant. Steigt dagegen die relative Rate selbst, ist das eine andere Hypothese. Beides sollte mit eigenen Daten und Modellen geprüft werden.

## 4. Eine besonders passende Brücke: Heterogenität erzeugt scheinbare Beschleunigung

Eine eigene elementare Herleitung erklärt, warum diese Frage direkt zur SCF-Geschlossenheit passt. Für positive Komponenten mit zeitlich konstanten Raten

\[
Y(t)=\sum_i c_i e^{r_i t},\qquad c_i>0,
\]

gilt mit `w_i(t)=c_i e^{r_i t}/Y(t)`:

\[
r_{\mathrm{eff}}(t)=\frac{\dot Y}{Y}=\sum_iw_i(t)r_i,
\qquad
\dot r_{\mathrm{eff}}(t)=\sum_iw_i(t)r_i^2-
\left(\sum_iw_i(t)r_i\right)^2\geq0.
\]

Die effektive relative Wachstumsrate nimmt also zu, obwohl **jede einzelne Komponentenrate konstant bleibt**. Schnellere Komponenten übernehmen allmählich einen größeren Anteil. Mit einer abklingenden und einer wachsenden Komponente kann sogar ein Tal mit anschließendem Wachstum entstehen.

Der nachgerechnete synthetische Fall verwendet Amplituden 1000 und 10 sowie Raten −0,1 und +0,15. Zwischen Zeit 0 und 40 steigt die effektive Rate von etwa −0,0975 auf +0,1489. Die Identität für ihre Ableitung wurde analytisch hergeleitet und numerisch kontrolliert. Das Beispiel ist keine Anpassung an COVID.

**Bezug zum Formalismus:** Die Summe `Y=x₁+x₂` ist bei unterschiedlichen `r₁,r₂` im Allgemeinen kein geschlossener Zustand. Zwei unterschiedliche Aufteilungen derselben Summe erzeugen verschiedene Werte von `Ẏ=r₁x₁+r₂x₂`. Die fehlende Information ist die Zusammensetzung. Sie kann durch zusätzliche Zustände, einen Beobachter oder eine ausdrücklich approximative Reduktion behandelt werden.

Das liefert einen konkreten ersten Anschluss: weltweite Meldungen nach Ländern oder Regionen zerlegen und prüfen, ob die wechselnde Gewichtung einen Teil der scheinbar veränderlichen Gesamtrate erklärt. Messänderungen und tatsächlich veränderliche Einzelraten müssen daneben weiterhin modelliert werden.

## 5. Welche wissenschaftlichen Konzepte wir nutzen können

### 5.1 Nichtautonome Systeme und rateninduziertes Kippen — höchste theoretische Nähe

Ein geeigneter allgemeiner Ansatz trennt Zustandsdynamik und Beobachtung:

\[
dx_t=f(x_t,u_t,\theta_t)\,dt+G(x_t,t)\,dW_t,
\qquad y_t\sim p(y\mid x_t,u_t,\psi_t).
\]

`u_t` ist ein gemessener oder ausdrücklich modellierter Treiber, `θ_t` enthält dynamische Parameter, `ψ_t` beschreibt den Messprozess. Diese Größen dürfen nicht alle unbeschränkt aus einer einzelnen Kurve geschätzt werden: Ohne Zusatzinformation sind die Ursachen häufig nicht identifizierbar.

Die einschlägige Literatur unterscheidet insbesondere [R4, R5]:

| Vorgang | Entscheidende Frage |
|---|---|
| Bifurkationsbedingtes Kippen | Verliert oder wechselt ein Attraktor bei verändertem Parameter seine Existenz oder Stabilität? |
| Rateninduziertes Kippen | Kann das System dem sich verschiebenden Attraktor noch folgen, obwohl die eingefrorenen Systeme stabil bleiben? |
| Rauschinduziertes Kippen | Führt eine Fluktuation über eine Grenze zwischen Einzugsgebieten? |
| Verletzung einer Sicherheits-/Viabilitätsgrenze | Verlässt die Trajektorie einen definierten zulässigen Bereich, möglicherweise ohne Attraktorwechsel? |

Diese Mechanismen können zusammenwirken. Ein statistischer Strukturbruch ist zunächst nur eine Beobachtung, die verschiedene dieser oder ganz andere Ursachen haben kann.

**Eigener Kontrollfall:**

\[
\dot x=(x-u)-(x-u)^3,\qquad u(t)=1+\tanh(rt).
\]

Bei eingefrorenem `u` liegen stabile Gleichgewichte bei `x=u±1` und ein instabiles bei `x=u`. Die lokale Ableitung an beiden stabilen Gleichgewichten ist immer `−2`; es gibt entlang des Treiberwegs keine eingefrorene Bifurkation.

Der Start liegt nahe dem oberen Gleichgewicht vor der Treiberänderung. Für denselben Weg von `u≈0` nach `u≈2` ergibt die numerische Integration:

| Änderungsparameter r | Endzustand x | Relativer Zustand x−u | Ergebnis |
|---|---:|---:|---|
| 0,1 | ungefähr 3 | ungefähr +1 | Oberer Attraktor wird weiter verfolgt. |
| 2 | ungefähr 1 | ungefähr −1 | Wechsel zum unteren Attraktor. |

Eine Verfeinerung von Toleranzen und maximaler Schrittweite verändert die berechneten Trajektorien um weniger als `1,4 × 10⁻⁸` in den geprüften Werten. Das ist ein nachgerechneter Raten-Kontrollfall, keine Schätzung einer kritischen Rate aus Realdaten. Die Treiberfunktion ist begrenzt und S-förmig; eine unbeschränkt exponentielle Zeitentwicklung ist hier nicht nötig.

**Anschluss im Repository:** `dynamics/core.py`, `gspt.py`, `panarchy_cusp.py` und `early_warning.py` liefern bereits Bauteile. Die neue Arbeit wäre eine explizite zeitabhängige Anregung mit echter Trajektorienintegration und getrennter Auswertung der eingefrorenen Stabilität. Ein quasistatischer Zweig-Sweep allein entscheidet die Ratenfrage nicht.

### 5.2 Bewegliche Gleichgewichte, Anpassungszeit und Puffer

In einem skalaren lokalen Modell mit stabilem beweglichem Gleichgewicht `x_*(u(t))` und Rückstellrate `κ>0` gilt für den kleinen Nachlauffehler `e=x−x_*` näherungsweise

\[
\dot e\approx-\kappa e-\dot x_*.
\]

Bei genügend langsam wechselnden Koeffizienten folgt `e≈−ẋ_*/κ`. Als **lokale Diagnosegröße**, ausdrücklich ohne universelle Kippschwelle, bietet sich deshalb an:

\[
\chi(t)=\frac{|D_u x_*(u)\,\dot u|}{\kappa(t)\,d_{\mathrm{Grenze}}(t)}.
\]

`d_Grenze` ist ein definierter Abstand zur relevanten Basin- oder Sicherheitsgrenze. Die Größe ist dimensionslos, wenn alle Größen konsistent gewählt sind. Sie kann wachsen, weil der Treiber schneller wird, die Rückstellung schwächer wird, die Gleichgewichtslage empfindlicher reagiert oder der verfügbare Abstand schrumpft. Für mehrdimensionale, nichtnormale Systeme genügt ein einzelner spektraler Wert im Allgemeinen nicht; dort sind Metrik und vorübergehende Verstärkung zusätzlich zu berücksichtigen.

Auch die Empfindlichkeit selbst kann stark zunehmen: Aus `f(x_*(u),u)=0` folgt im skalaren regulären Fall

\[
\frac{dx_*}{du}=-\frac{f_u}{f_x}.
\]

Wenn `f_x` gegen null geht, kann ein gleichmäßig veränderter Treiber eine sehr stark beschleunigte Zustandsänderung auslösen. Das bietet eine weitere prüfbare Alternative zur exponentiellen Treiberhypothese. Diese Ableitungen sind eigene lokale Rechnungen unter den angegebenen Voraussetzungen.

Für die vorhandene Viabilitätslogik ist außerdem ein expliziter Pufferzustand naheliegend: Zufluss, Verlust, Steuerung und Belastung werden bilanziert; das Versagen wird als Verlassen einer zulässigen Menge definiert. Ein schrumpfender Puffer kann entscheidend sein, obwohl der äußere Treiber selbst konstant bleibt.

### 5.3 Zeitvariable Parameter und Strukturbruchmodelle — erster Datenpilot

Ein überschaubarer Ausgangspunkt ist ein Zustandsraummodell für Niveau und Steigung:

\[
m_{t+1}=m_t+b_t\Delta t+\eta_t,
\qquad b_{t+1}=b_t+\zeta_t,
\qquad y_t=m_t+\epsilon_t.
\]

Für positive Zählprozesse kann die latente Größe ein logarithmisches Niveau sein; die Beobachtung erhält dann eine passende Zählverteilung. Die Varianzen der Zustandsänderungen kontrollieren, wie schnell sich das Modell anpassen darf, und müssen innerhalb des Trainingsbereichs gewählt werden.

Als Alternative eignet sich ein Modell mit wenigen diskreten Regimen. Online-Strukturbruchverfahren können eine Verteilung über den Zeitpunkt des letzten Wechsels führen [R6]. Das verbessert die Behandlung von Unsicherheit gegenüber einem einzigen rückblickend festgelegten Bruchdatum. Glatte Ratenänderung, sprunghafte Änderung und eine geänderte Beobachtungsregel sollten als unterschiedliche Kandidaten verglichen werden.

**Scope:** Eine bessere Vorhersage eines Zustandsraummodells ist noch keine Identifikation eines physikalischen Treibers. Der praktische Nutzen liegt zuerst in einer anpassungsfähigeren Prognose mit Unsicherheitsintervallen.

### 5.4 Domänenspezifische Modelle statt derselben Kurvenform für alle Daten

**COVID — Erneuerungsmodelle mit zeitvariablem R.** Ein Standardanschluss ist die Schätzung zeitveränderlicher Reproduktionszahlen nach Cori et al. [R7]. Eine mögliche Modellform verbindet latente Inzidenz mit vorausgehenden Infektionen:

\[
\mathbb E[I_t\mid\mathcal F_{t-1}]
=R_t\sum_{s\ge1}w_s I_{t-s},\qquad \sum_s w_s=1.
\]

Generation-/Serialintervallannahmen, Meldeverzögerungen, Erfassungsanteile und Länderzusammensetzung müssen ausgewiesen werden. Eine Negativ-Binomial-Beobachtung kann als gesondert zu prüfende Erweiterung zusätzliche Streuung abbilden. Verdopplungszeit allein bestimmt `R_t` ohne Intervallannahmen nicht eindeutig. Der Start mit China und Rest der Welt, später einzelnen Ländern, wäre strukturell informativer als eine weitere globale Exponentialkurve.

**Klima — ein getriebenes Zweischichten-Energiebilanzmodell.** Ein passender etablierter Anschluss ist [R8]:

\[
C_s\dot T_s=F(t)-\alpha T_s-\gamma(T_s-T_d),
\qquad C_d\dot T_d=\gamma(T_s-T_d).
\]

Es trennt Strahlungsantrieb, oberflächennahe Temperatur, Wärmeaufnahme des tieferen Ozeans und Rückkopplungsstärke. Bei konstanten Koeffizienten ist dieses Modell linear in den Temperaturen und kann trotzdem verzögerte und gekrümmte Antworten auf veränderliche Antriebe erzeugen. Ein Kipppunkt ist in dieser Form nicht automatisch enthalten. Das verbindet die Fragestellung mit der vorhandenen Projektions- und Gedächtnislogik.

Benötigt werden gemeinsame Zeitreihen von Antrieben und möglichst zusätzlicher Wärmeaufnahme. Eine Temperaturanomalie allein identifiziert die Parameter nicht zuverlässig. NOAA AGGI liefert einen nachvollziehbaren Anschluss für langlebige Treibhausgase ab 1979, umfasst aber nicht alle relevanten Antriebe, etwa Aerosole und Vulkanbeiträge [R9]. Die dokumentierte CO₂-Antriebsform enthält einen logarithmischen Konzentrationsterm. In der groben Näherung `F∝ln(C/C₀)` würde selbst `C=C₀e^{gt}` einen **linearen** Beitrag in der Zeit erzeugen. Das ist ein mathematischer Illustrationsfall, keine Behauptung, reale Konzentrationen oder das gesamte Klima folgten exakt diesen vereinfachten Gesetzen.

**Erdbeben — Zählstreuung und selbstanregende Punktprozesse.** Zunächst sollten Poisson und Negativ-Binomial anhand vollständiger Vorhersageverteilungen verglichen werden. Für Ereigniszeiten beschreibt ETAS die Intensität schematisch als Hintergrund plus Beiträge früherer Ereignisse:

\[
\lambda(t\mid\mathcal H_t)=\mu(t)+
\sum_{t_i<t}\frac{K\exp[\alpha(M_i-M_0)]}{(t-t_i+c)^p}.
\]

Hier wirkt ein Exponentialterm auf die Magnitude des auslösenden Ereignisses; der zeitliche Nachbebenbeitrag folgt einem anderen Gesetz. Die genaue Parametrisierung, räumliche Ergänzung, Vollständigkeit und Stabilität der geschätzten Verzweigung brauchen einen eigenen Scope [R3]. Daraus entsteht kein Verfahren zur zuverlässigen Vorhersage eines einzelnen starken Bebens.

### 5.5 Frühwarnsignale mit passenden Gegenfällen

Die vorhandenen OU-Formeln `Var=σ²/(2κ)` und `ρ(Δt)=exp(−κΔt)` sind nützlich für ein lokal annähernd stationäres lineares Rückstellmodell mit passend behandeltem Rauschen. Sie sollten nicht unmittelbar auf trendende Rohdaten angewendet werden. Die Primärliteratur dokumentiert erhebliche Fehlalarm- und Erkennungsprobleme [R10].

Ein besonders konkretes Problem steckt im COVID-Ziel selbst: Für unabhängige Tagesfehler gleicher Varianz erzeugt ein gleitendes Siebentagesmittel allein durch seine sechs überlappenden Tage eine Lag-1-Korrelation von

\[
\rho_1=6/7\approx0{,}857.
\]

Diese eigene elementare Rechnung setzt noch keine nachlassende Resilienz voraus. Steigende Autokorrelation in einem geglätteten oder trendenden Signal braucht deshalb eine Gegenprüfung gegen den unveränderten Mess- und Glättungsprozess. Auch steigende Rauschstärke kann steigende Varianz erzeugen.

Ein sinnvoller Testkatalog enthält mindestens: echte Abnahme der Rückstellrate, beschleunigten Treiber bei unveränderter eingefrorener Stabilität, Wechsel des Beobachtungsprozesses und wechselnde Komponentenanteile. Ein Frühwarnverfahren muss diese Fälle nicht alle perfekt trennen, sollte seine Fehler daran aber offen ausweisen.

## 6. Wie sich die konkrete Treiberhypothese prüfen lässt

Die Hypothese sollte in mehrere prüfbare Aussagen zerlegt werden:

1. **Treiber benennen und messen.** Welche Größe ist `u(t)`, in welcher Einheit, und wie unterscheidet sie sich vom gemessenen Systemzustand? Bei einer bloßen Ausgabezeitreihe bleibt ein äußerer Treiber möglicherweise unidentifizierbar.
2. **Funktionsform vergleichen.** Konstante Änderung, Exponentialverlauf, begrenzte S-Kurve, glatte Ratenänderung und wenige Regimewechsel anhand von Training und zeitlich späterer Prüfung vergleichen. Positivität und physikalischer Nullpunkt sind für einen Exponentialansatz relevant.
3. **Antrieb und Empfindlichkeit trennen.** Bleibt die Systemantwort bei gegebener Belastung stabil, oder ändern sich Rückstellrate, Sensitivität, Puffer beziehungsweise Einzugsgebiet?
4. **Kippen operationalisieren.** Vorab festlegen, ob ein dauerhafter Attraktorwechsel, ein Verlust der Verfolgung, eine Überschreitung einer Sicherheitsgrenze oder nur eine beschleunigte Zeitreihe untersucht wird.
5. **Tempo bei gleichem Weg variieren.** Im identifizierten Modell oder kontrollierten Experiment dieselben Start-/Endwerte und dieselbe Treiberbahn mit unterschiedlicher Geschwindigkeit durchlaufen. Danach den Treiber festhalten und prüfen, ob der Zustand zurückkehrt oder in einem anderen Attraktor bleibt.
6. **Mechanismen gegeneinander testen.** Positive Rückkopplung, Heterogenität, Messänderung und beschleunigter Treiber müssen als konkurrierende Erklärungen erhalten bleiben. Ein besserer Kurvenfit allein entscheidet keine Kausalität.

Das Wort „meist“ verlangt außerdem eine systematisch definierte Fallmenge. Drei sehr unterschiedliche ausgewählte Piloten ermöglichen keine Häufigkeitsaussage über reale Systeme insgesamt.

## 7. Validierungsprotokoll für den nächsten Schritt

Die vorhandene Trennung von Fit- und Testzeilen ist eine gute Grundlage. Die Codeprüfung ergab keinen direkten Zugriff der Fit-Funktionen auf die Testwerte. Wissenschaftliche Unabhängigkeit verlangt jedoch mehr als unveränderliche Datums-Konstanten im Code.

Pilot B und C wurden nach Kenntnis des negativen A-Ergebnisses entwickelt und am selben Testfenster bewertet. Das ist transparente, sinnvolle Exploration. Die Bezeichnung als jeweils eigenes Protokoll macht diesen Testbereich nicht erneut ungesehen. Ein kalendarischer Anker belegt ebenfalls keine historische Vorregistrierung, wenn die Analyse 2026 mit bereits bekannten historischen Daten entworfen wurde.

Für eine belastbare Fortsetzung:

- **Neue Prüfabschnitte reservieren:** Zeiträume oder Länder, die noch nicht zur Wahl von Modell, Fenster oder Hyperparametern dienten. Rückblickende Prognosen mit revidierten Daten von echten damaligen Echtzeitprognosen unterscheiden.
- **Zeitlich rollierend auswerten:** Modelle erhalten am Prognoseursprung nur damals freigegebene Eingaben. Fensterauswahl und Anpassungsgeschwindigkeit werden in einer inneren zeitlichen Validierung gewählt.
- **Starke einfache Vergleichsmodelle verwenden:** Persistenz, lokale lineare beziehungsweise log-lineare Fits und gegebenenfalls gedämpfte Trends. Ein globaler Langfristfit allein ist eine zu schwache Konkurrenz für komplexere Modelle.
- **Verteilungen prüfen:** Neben RMSE/MAE geeignete Wahrscheinlichkeits-Scores und Intervallabdeckung ausweisen. Bei Zähldaten sind Poisson-/Negativ-Binomial-Annahmen Teil der Prüfung.
- **Abhängigkeiten berücksichtigen:** Gleitende Mittel und serielle Abhängigkeit reduzieren die effektive Zahl unabhängiger Beobachtungen. Ein Testfenster mit 14 geglätteten Tagen liefert keine 14 unabhängigen Replikate.
- **Modellverluste passend wählen:** COVID wird im Lograum angepasst, aber im ursprünglichen Maßstab nach RMSE bewertet. Diese unterschiedliche Gewichtung ist zulässig, muss aber als Zielentscheidung sichtbar sein.
- **Zukünftige Treiber fair behandeln:** Ein Modell mit tatsächlich später eingetretenen Antriebswerten liefert eine bedingte Rückrechnung. Es darf nicht ohne Kennzeichnung mit einer Prognose verglichen werden, die diese Zukunftsinformation nicht kennt.

## 8. Konkrete Priorisierung für SCF

| Reihenfolge | Arbeitspaket | Lieferbares Ergebnis |
|---|---|---|
| 1 | Gemeinsame rollierende Auswertung und adaptive einfache Modelle | Vergleichbare Resultate über mehrere Prognoseursprünge; Unsicherheit, Horizonte und Auswahlregeln dokumentiert. |
| 2 | Heterogenität und Beobachtungsprozess | COVID: Länderkomponenten statt nur Weltmittel; Niveau-/Meldeänderung und Wachstumsänderung getrennt testen. |
| 3 | Treiberabhängige Dynamik | Kleine Schnittstelle für vorgegebene Treiberverläufe; eingefrorene Stabilität und tatsächliche Trajektorie getrennt ausgeben. |
| 4 | Raten- und Viabilitätskontrollfälle | Der oben gerechnete Fall sowie ein Pufferfall: gleiche Belastungsendwerte, unterschiedliches Tempo oder unterschiedliche Reserve. |
| 5 | Je Domäne ein mechanistischer Anschluss | COVID-Erneuerung, getriebenes Energiebilanzmodell oder regionales ETAS; jeweils mit passenden zusätzlichen Daten. |

Technisch bieten sich zunächst additive Beispiele und Auswertungen neben den bestehenden drei Validierungspiloten an. Die neuen Diagnoseergebnisse sollten deren ursprüngliche Resultate nicht überschreiben. Ein kleines Ergebnisformat kann insbesondere festhalten: Treiberdaten vorhanden?, Populationszusammensetzung berücksichtigt?, Messmodell?, zeitlich variable Parameter?, Kippphänomen definiert?, Evidenzstatus und künftig reservierter Testbereich.

**Meine Empfehlung:** Zuerst die rollierende Auswertung und die Zerlegung der COVID-Aggregation, parallel dazu den synthetischen Raten-Kontrollfall in die Dynamiktests aufnehmen. Damit wird die Beobachtung über wechselnde reale Verläufe unmittelbar prüfbar, während der stärkere Kippmechanismus einen eigenen nachvollziehbaren Nachweis bekommt.

## 9. Quellen und Rechenbelege

Repository-Grundlagen, jeweils am festgehaltenen Commit:

- [COVID-Pilot](https://github.com/GenesisAeon/scoped-correspondence-formalism/blob/96567288a5ba80e410208226a8cc74d240af0a3c/docs/covid_pilot.md), [NOAA-Pilot](https://github.com/GenesisAeon/scoped-correspondence-formalism/blob/96567288a5ba80e410208226a8cc74d240af0a3c/docs/noaa_temp_pilot.md), [Erdbeben-Pilot](https://github.com/GenesisAeon/scoped-correspondence-formalism/blob/96567288a5ba80e410208226a8cc74d240af0a3c/docs/earthquake_pilot.md).
- [Datenmanifest](https://github.com/GenesisAeon/scoped-correspondence-formalism/blob/96567288a5ba80e410208226a8cc74d240af0a3c/data/real_data_manifest.json), [Validierungscode](https://github.com/GenesisAeon/scoped-correspondence-formalism/tree/96567288a5ba80e410208226a8cc74d240af0a3c/src/scoped_correspondence/validation).

Primärquellen und offizielle Datendokumentation:

**R1.** PAHO/WHO (14.02.2020): *Epidemiological Update: Novel Coronavirus (COVID-19).* [Originalbericht](https://www.paho.org/sites/default/files/2020-03/2020-feb-14-phe-epi-update-covid19.pdf). Belegt die Änderung der Hubei-Falldefinition; identifiziert nicht allein die Ursache des im Repository gefundenen Bruchs.

**R2.** USGS: *ComCat Event Terms / GeoJSON Summary Format.* [Katalogdokumentation](https://earthquake.usgs.gov/data/comcat/data-eventterms.php), [Datenformat](https://earthquake.usgs.gov/earthquakes/feed/v1.0/geojson.php). Offizielle Beschreibung der Ereignisfelder.

**R3.** Ogata, Y. (1988): *Statistical Models for Earthquake Occurrences and Residual Analysis for Point Processes.* JASA 83, 9–27. [DOI](https://doi.org/10.1080/01621459.1988.10478560), [Originalartikel beim Institute of Statistical Mathematics](https://bemlar.ism.ac.jp/zhuang/Refs/Refs/ogata1988.pdf). Grundlage für ETAS und Punktprozessdiagnostik.

**R4.** Ashwin, P.; Wieczorek, S.; Vitolo, R.; Cox, P. (2012): *Tipping Points in Open Systems: Bifurcation, Noise-induced and Rate-dependent Examples in the Climate System.* Phil. Trans. R. Soc. A 370, 1166–1184. [Autorenversion einschließlich Korrektur](https://arxiv.org/abs/1103.0169), [DOI](https://doi.org/10.1098/rsta.2011.0306).

**R5.** Wieczorek, S.; Xie, C.; Ashwin, P. (2023): *Rate-induced Tipping: Thresholds, Edge States and Connecting Orbits.* Nonlinearity 36, 3238–3293. [Volltext](https://arxiv.org/html/2111.15497v4), [DOI](https://doi.org/10.1088/1361-6544/accb37). Präziser Rahmen für den Verlust der Attraktorverfolgung unter zeitabhängigem Antrieb.

**R6.** Adams, R. P.; MacKay, D. J. C. (2007): *Bayesian Online Changepoint Detection.* [Originalarbeit](https://arxiv.org/abs/0710.3742). Methodischer Anschluss für fortlaufende Strukturbrucherkennung.

**R7.** Cori, A.; Ferguson, N. M.; Fraser, C.; Cauchemez, S. (2013): *A New Framework and Software to Estimate Time-Varying Reproduction Numbers During Epidemics.* American Journal of Epidemiology 178, 1505–1512. [Originalartikel](https://academic.oup.com/aje/article/178/9/1505/89262), [frei zugängliche Archivfassung](https://pmc.ncbi.nlm.nih.gov/articles/PMC3816335/). Ausgangspunkt für zeitvariable Reproduktionszahlen; die vorgeschlagene Beobachtungs- und Heterogenitätserweiterung ist ein eigenes Arbeitsprogramm.

**R8.** Geoffroy, O. et al. (2013): *Transient Climate Response in a Two-Layer Energy-Balance Model. Part I: Analytical Solution and Parameter Calibration Using CMIP5 AOGCM Experiments.* Journal of Climate 26, 1841–1857. [Verlagsseite/DOI](https://doi.org/10.1175/JCLI-D-12-00195.1). Etablierter Anschluss für getrennte schnelle/langsame Temperaturantworten; die Parameter des hiesigen NOAA-Piloten wurden damit noch nicht geschätzt.

**R9.** NOAA Global Monitoring Laboratory: *Annual Greenhouse Gas Index*, insbesondere Tabelle 1 zu Antriebsformeln und Beschreibung der abgedeckten Gase und Zeiträume. [Offizielle Quelle](https://gml.noaa.gov/aggi/aggi.html). Hier für die Modellstruktur herangezogen, nicht als vollständig ausgewerteter neuer Treiberdatensatz.

**R10.** Boettiger, C.; Hastings, A. (2012): *Quantifying Limits to Detection of Early Warning for Critical Transitions.* Journal of the Royal Society Interface 9, 2527–2539. [Originalarbeit/Autorenversion](https://arxiv.org/abs/1204.6231), [DOI](https://doi.org/10.1098/rsif.2012.0125). Grundlage für Fehlalarm- und Erkennungsprüfung von Frühwarnsignalen.

Die Modellpriorisierung und die konkreten SCF-Arbeitspakete sind die Bewertung dieser Ausarbeitung. Die Mischungsidentität, der Nachlaufansatz, die Glättungskorrelation und die numerischen Diagnosevergleiche wurden hier explizit hergeleitet beziehungsweise berechnet; ihnen wird keine wissenschaftliche Neuheit zugeschrieben.

Das Begleitpaket enthält das unabhängig ausführbare Analyseskript, Zahlenresultate, Prüflogs und die Vergleichsgrafik. Reproduktion mit Python 3.12.14, NumPy 2.3.5, SciPy 1.17.0 und Matplotlib. Rohdaten und Repository-Code werden über den angegebenen Commit referenziert. **Datenattribution COVID: Our World in Data / Johns Hopkins University CSSE COVID-19 Data Repository, CC BY 4.0.**
