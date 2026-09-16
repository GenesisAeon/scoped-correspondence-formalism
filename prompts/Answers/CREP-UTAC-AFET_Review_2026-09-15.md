# CREP–UTAC–AFET: Gegenprüfung des bereits eingearbeiteten Standes

Stand: 15. September 2026, einschließlich der nachgereichten Worked Examples. Grundlage: die bereitgestellten Formalismus-Unterlagen mit insgesamt acht Worked Examples, Roadmap und Follow-up-Listen, die beiden früheren TXT-Dateien, gezielte Quellcodeprüfung über GitHub und die unten verlinkten Fachquellen.

**Ergebnis:** Die Absicht ist nachvollziehbar: CREP beschreibt Information, UTAC die Dynamik von Systemen, AFET ihre Kopplung. Die inzwischen umgesetzten Paketkorrekturen sind substanziell. Mehrere im neuen Formalismus behauptete mathematische Identitäten tragen jedoch nicht. Daraus folgt ein gezielter Korrekturbedarf an Definitionen, Herleitungen und gegebenenfalls ihren Nutzern im Code; aus dieser Prüfung folgt kein pauschaler Rückbau der bereits geleisteten Arbeit.

## 1. Was inzwischen umgesetzt ist

`ROADMAP.md` enthält das bestätigte GO für Phase 2 und bereits abgeschlossene Änderungen und Releases. `FOLLOWUP_TICKETS.md` dokumentiert weitere Reparaturen. Die frühen Zusammenfassungen in README und FORMALISM bilden diese spätere Arbeit nicht vollständig ab. Insbesondere ist „Γ-Refit noch zurückgestellt“ inzwischen überholt.

| Bereich | Direkt im Repository gesehen | Bedeutung für diese Gegenprüfung |
|---|---|---|
| `afet-tensions` | `GAMMA_DOMAIN=0.6403419953108261`; separates Fit-Skript für fünf H₀-Messungen und drei Weak-Lensing-Messungen; neues κ | Der alte algebraische Zwei-Punkt-Ansatz wurde ersetzt. Die neue Anpassung ist eine Kalibrierung; eine unabhängige Vorhersageprüfung folgt daraus noch nicht. |
| `scope-resilience` | Die Docstrings erklären nun ausdrücklich, dass `K_sem*tanh(σΓ_sem)` kein hergeleiteter Fixpunkt der angeführten logistischen ODE ist. | Dieser Fehler wurde bereits erkannt und korrigiert. Die Bewertung als semantische Schwelle bleibt eine Modellannahme. |
| `resilience-core` | Bereinigte Kalibrierungsbehauptungen und Tests; `CouplingMatrix` registriert gerichtete Einflüsse und berechnet eine Last sowie einen gekappten Faktor. | Diese konkrete Implementierung ist eine Einflussmatrix. Aus ihr allein lässt sich kein thermodynamischer Onsager-Formalismus ableiten. |
| `beta-clustering-utac` | Changelog dokumentiert σ≈1,28 statt behaupteter 2,2. Der berechnete Wert erscheint im Zyklusergebnis und in `K_eff`; die CREP-Abbildung verwendet weiter ihren bisherigen Standard über `beta_to_gamma`. | Die falsche Herleitungsbehauptung wurde korrigiert. Unterschiedliche Parameterpfade sind ausdrücklich zu kennzeichnen; nicht stillschweigend alle Defaults ersetzen. |
| `utac-core` | Der geprüfte öffentliche `main` verwendet in `core.py` noch das Symbol `R`. | Die in den Unterlagen gemeldete lokale Umbenennung in `R_ctrl` ist auf diesem geprüften Remote-Stand noch nicht sichtbar. Das widerlegt keine lokale Änderung. |

Geprüfte Quellstände und Belege:

- [afet-tensions, Konstanten](https://github.com/GenesisAeon/afet-tensions/blob/1fa06907f8953212fc5a468feddce293f39b9394/src/afet_tensions/constants.py) und [Fit-Skript](https://github.com/GenesisAeon/afet-tensions/blob/1fa06907f8953212fc5a468feddce293f39b9394/scripts/fit_gamma_domain_and_kappa.py).
- [scope-resilience, SemanticUTAC](https://github.com/GenesisAeon/scope-resilience/blob/61bfce858ec854ad734b701a8d3d92dbc17fa8da/src/scope_resilience/semantic_utac.py) und [Changelog](https://github.com/GenesisAeon/scope-resilience/blob/61bfce858ec854ad734b701a8d3d92dbc17fa8da/CHANGELOG.md).
- [resilience-core, Kopplung](https://github.com/GenesisAeon/resilience-core/blob/60a4e69264c149921893e7110fe7e1b6b2c94453/src/resilience_core/coupling.py) und [Changelog](https://github.com/GenesisAeon/resilience-core/blob/60a4e69264c149921893e7110fe7e1b6b2c94453/CHANGELOG.md).
- [beta-clustering-utac, Datenfluss](https://github.com/GenesisAeon/beta-clustering-utac/blob/ce3938ecbc057ba739ce350732b0458faefa786b/src/beta_clustering/system.py) und [Changelog](https://github.com/GenesisAeon/beta-clustering-utac/blob/ce3938ecbc057ba739ce350732b0458faefa786b/CHANGELOG.md).
- [utac-core, öffentlicher Kern](https://github.com/GenesisAeon/utac-core/blob/4c5527751cfa1d3a4e8cc0c8e69b0f2f92661cb0/src/utac_core/core.py).

Das ist eine gezielte Prüfung dieser Dateien, keine vollständige Prüfung aller Pakete, Releases oder CI-Läufe. Die in den Uploads referenzierten Dateien `verification/`, `Gemini.txt` und das Worked Example zu `aeon-jurist` wurden nicht mitgeliefert; deren Inhalt und berichtete Ausführungen sind hier nicht unabhängig verifiziert.

### Die nachgereichten Beispiele erweitern den belegten Fortschritt

Die zusätzliche `FOLLOWUP_TICKETS(1).md` ist inhaltlich identisch zur ersten Kopie. Die sieben zusätzlichen Worked Examples liefern dagegen wesentlichen Kontext: Viele problematische Behauptungen wurden von euch bereits selbst nachgerechnet, relativiert und teils repariert. Das muss im Gesamturteil berücksichtigt werden.

| Paket/Beispiel | Bereits geleistete Arbeit | Verbleibende konkrete Frage |
|---|---|---|
| AMOC, v1.3.3 laut Changelog | Vorzeichen von `h_star()` korrigiert: zunehmendes Γ senkt jetzt den Modell-Fixpunkt. Mehrfach verwendete Formel vereinheitlicht; synthetische Daten und getrennte Γ-Pfade offengelegt. | Die fest vorgegebene Γ-Trajektorie bleibt von der diagnostischen Γ-Berechnung getrennt. Das ist nach dem Nachtrag bewusst dokumentiert, keine übersehene neue Entdeckung dieser Prüfung. |
| Cygnus, v1.0.2 laut Changelog | Inverse Γ-Berechnung und sechs Benchmark-Ziele als Kalibrierung bzw. Konstruktions-/Konsistenzprüfungen gekennzeichnet. | Reale dynamische Implementierung vorhanden; unabhängige astrophysikalische Vorhersageleistung separat prüfen. |
| Neural Avalanche, v1.0.1 laut Changelog | Die behauptete Γ-Universalität zurückgenommen; invertierbarer Γ-Rundtrip und ungenutzter E/I-Monitor offengelegt. | Kontinuierliche Modellrate, diskrete Simulationsrate und empirisch geschätzte Rate unterscheiden. Alte C/R/E/P-Bridge ist ausdrücklich noch nicht S/K/R/V. |
| Solar Flare, v1.0.1 laut Changelog | Reset-Wert korrekt bezeichnet; Rundungsfehler im Γ-Benchmark behoben; etwa 20-fache Zeitskalenabweichung offen dokumentiert. | Stabilität des ruhenden Teilmodells nicht mit Stabilität des vollständigen Reset-Prozesses gleichsetzen; thermodynamische Deutung der gerichteten Abhängigkeit noch unbelegt. |
| Resilience Core | Rechen-Engine von dynamischem System unterschieden; Kalibrierungsdiskrepanzen gefunden und anschließend dokumentiert/getestet. | Die Interpretation des Kopplungsregisters als „korrekte Onsager-Matrix“ bleibt offen; siehe Befund B. |
| Scope Resilience | Proxy-Kennzeichnung, Warnungen für unkalibrierte Parameter und falsche Fixpunktherleitung nachvollzogen. | Eine Zeitreihe und ein Differenzenquotient allein liefern noch kein Individuations- oder Lyapunov-Ergebnis. |
| Arctic Climate | Literaturatlas und Ausnahme-Policy von hypothetischen Formalismus-Anwendungen getrennt. | Die im Beispiel behauptete Aufwertung der allgemeinen Evidenzlage beruft sich auf genau die noch problematischen Identitäten; die Zugänglichkeits-Policy bleibt davon unabhängig. |

Die Änderungen sind in den geprüften öffentlichen Dateien sichtbar: [AMOC-Implementierung](https://github.com/GenesisAeon/amoc-utac/blob/6b9dc57d5e864681737f61308a62048909109c4d/amoc_utac/tipping_predictor.py), [Cygnus-Changelog](https://github.com/GenesisAeon/cygnus-jet-utac/blob/f7372d6fa6a52938777156e251973f805a7bff7e/CHANGELOG.md), [Neural-Changelog](https://github.com/GenesisAeon/neural-avalanche-utac/blob/2e06f35d7e3c084921b07babf330e36695e8dd6b/CHANGELOG.md), [Solar-Changelog](https://github.com/GenesisAeon/solar-flare-utac/blob/86ed000c70be276ba4352cc61105d5c423cd330f/CHANGELOG.md). Die Versionsangaben stammen hier aus diesen Changelogs; die vollständigen Veröffentlichungswege wurden in dieser Gegenprüfung nicht erneut ausgeführt oder unabhängig kontrolliert.

## 2. Befunde mit konkretem Reparaturweg

### A. Logistische Steilheit β ist nicht allgemein die Erholungsrate S

**Stellen:** FORMALISM, Tabelle der Resilienzgrößen; system_layer_utac, Zuordnung von Resistance; coupling_layer_afet, Eingangsvoraussetzung `β=S`.

Eine Antwortkurve `p(u)=1/(1+exp(-βu))` beschreibt eine Abhängigkeit vom Kontrollparameter. Ihr β hat die Einheit `1/[u]`. Eine zeitliche Erholungsrate hat die Einheit `1/Zeit`.

Schon das einfache dynamische Modell

\[
\dot x=-\frac{x-p(u)}{\tau}
\]

hat für jedes positive τ exakt dieselbe logistische Gleichgewichtskurve, aber `S=1/τ`. Für β=4 liefern τ=1 und τ=10 dieselbe Kurvensteigung 1 am Mittelpunkt, jedoch Erholungsraten 1 und 0,1. Auch nach einer Normierung entsteht daraus keine allgemeine Identität.

**Reparatur:** `beta_response`, `return_rate` und eine gegebenenfalls gesondert definierte Resistance auseinanderhalten. Einen Zusammenhang erst aus einer ausdrücklich angegebenen Dynamik ableiten oder mit unabhängigen Daten testen. Die schon erfolgte Fixpunktkorrektur in `scope-resilience` geht genau in diese Richtung.

Das wird sogar durch euer Cygnus-Beispiel gestützt: Für dessen `dot H=rH(1-H/H*)` ist bei festem Γ und `H*>0` die lokale Ableitung am Fixpunkt `−r`, unabhängig von der Steilheit der Funktion `H*(Γ)`. [Geprüfter Cygnus-Integrator](https://github.com/GenesisAeon/cygnus-jet-utac/blob/f7372d6fa6a52938777156e251973f805a7bff7e/cygnus_jet_utac/_genesis_stubs.py).

### B. Informationsnutzung V, Panarchy und Onsager-L sind keine identischen Größen

**Stellen:** information_layer_crep, Abschnitt mit finalen S/K/R/V-Formeln; coupling_layer_afet, Abschnitte 1 und 3; FORMALISM, „Der rote Faden“; worked_example_afet_tensions, Abschnitt 3.

Wenn `I(X;Y)` eine Informationsmenge in Bit und C eine Kapazität in Bit/s ist, hat `I/C` die Einheit Sekunden. Es ist kein dimensionsloser Nutzungsanteil. Eine konsistente Möglichkeit wäre

\[
\eta_{ij}=\frac{\mathcal I_{ij}}{C_{ij}},\qquad
\mathcal I_{ij}\text{ als Informationsrate},
\]

oder `I(Block)/(C Δt)` für ein festgelegtes Zeitfenster. Die Schranke lautet unter passenden Kanalannahmen `0≤η≤1`; für die Informationsrate gilt `𝓘≤C`. Die im Dokument formulierte Schranke `V≤K` vermischt diese beiden Aussagen.

Ein Onsager-Koeffizient hat dagegen die Einheit `[Fluss]/[thermodynamische Kraft]`. „Panarchy“ bezeichnet in der herangezogenen Resilienzliteratur skalenübergreifende Einflüsse; daraus folgt keine Gleichung mit einem einzelnen Informationsquotienten. [Walker et al. (2004)](https://ecologyandsociety.org/vol9/iss2/art5/inline.html).

Für einen thermodynamischen Ansatz müssen die Flüsse und entropiekonjugierten Kräfte so definiert sein, dass `dot S_prod = Xᵀ L X`. Unter dieser Voraussetzung muss der symmetrische Teil von L positiv semidefinit sein. Eine beliebige gerichtete Datenabhängigkeit erfüllt das nicht: Für

\[
L=\begin{pmatrix}0&1\\0&0\end{pmatrix},\quad X=(1,-1)^T
\]

folgt `XᵀLX=-1`. Asymmetrische Anteile sind nicht generell verboten; sie sind aber auch kein Freibrief für eine beliebige Matrix. Die Voraussetzungen der Reziprozität und ihre Verallgemeinerungen gehören ausdrücklich zum Modell. [Mielke, Peletier und Renger](https://arxiv.org/abs/1510.06219).

**Auswirkung auf den aktuellen Code:** Die gerichtete Abhängigkeit in `DESIPrediction.h0_bao()` ist als Datenfluss korrekt erkennbar. Dasselbe gilt für registrierte Einflüsse in `resilience-core`. Beides belegt für sich weder Onsager-Koeffizienten noch eine physikalische Verletzung von Reziprozität.

**Reparatur:** Zunächst drei getrennte Begriffe verwenden: Informationsnutzungsgrad, dynamischer Einfluss und thermodynamischer Transportkoeffizient. Eine Abbildung zwischen ihnen ist eine zusätzliche, zu prüfende Modellannahme.

### C. Die Spitzen-Katastrophe enthält einen Formelwechsel und zu starke Folgerungen

**Stellen:** system_layer_utac, Abschnitte 3.5–3.6; FORMALISM, bistabile Erweiterung und „a ist gar kein neuer Parameter“.

In Abschnitt 3.5 steht sinngemäß `dot R_ctrl=-R_ctrl³+a(R_ctrl-Θ)+b`. Abschnitt 3.6 arbeitet hingegen mit `x=R_ctrl-Θ` und `dot x=-x³+ax` für b=0. Das sind bei Θ≠0 verschiedene Modelle. Bei a=2, Θ=1, b=0 ist am Referenzpunkt der erste Drift −1, der zweite 0. Die zugehörigen negativen lokalen Ableitungen sind 1 beziehungsweise −2.

Für die einheitliche Normalform

\[
\dot x=-x^3+ax+b
\]

gibt es drei verschiedene reelle Fixpunkte genau bei `4a³>27b²`; davon sind die beiden äußeren stabil. `a>0` allein reicht nicht. Das Beispiel a=1, b=1 besitzt nur einen reellen Fixpunkt, bei ungefähr 1,324718.

Im symmetrischen Modell b=0 und bei festgelegter Zeitskala gilt tatsächlich `S(0)=-a`. An den stabilen Ästen `x=±sqrt(a)` ist dagegen `S=2a`. Die Identität am Referenzpunkt ist eine bedingte Umparametrisierung. Sie zeigt nicht, dass a ohne zusätzliche Messung schon bekannt ist. Bei einem Mobilitätsfaktor m in `dot x=-m dU/dx` tritt zudem m in die Rate ein.

Auch ist eine logistische Antwortkurve kein nachgewiesener exakter Grenzfall dieser kubischen Gleichgewichtsbedingung. Eine zusätzliche Beobachtungsfunktion könnte beide verbinden; sie muss angegeben werden.

**Reparatur:** Zustand x und Kontrollparameter u trennen, eine einzige zentrierte Normalform festlegen, den Geltungsbereich der Identität angeben und die kubische Dynamik als vorgeschlagenes Modell kennzeichnen.

### D. Beckenwahrscheinlichkeit, Beckenbreite und Satteldistanz unterscheiden sich

**Stellen:** system_layer_utac, Latitude und Basin Stability; FORMALISM, Resilienztabelle und Frame-Brücke.

Im symmetrischen Modell `dot x=-x³+ax` ist die Entfernung des positiven Attraktors zum Sattel `sqrt(a)`. Unter gleichverteilten Störungen/Anfangszuständen auf `[-3,3]` beträgt die Wahrscheinlichkeit, im positiven Becken zu landen, dagegen sowohl bei a=1 als auch bei a=4 genau 1/2. Die Satteldistanz wächst von 1 auf 2. Die Größen können zusammenhängen, sind aber nicht identisch.

Basin Stability ist eine Wahrscheinlichkeit bezüglich einer festgelegten Verteilung von Störungen. Diese Verteilung gehört zur Definition. Eine euklidische Entfernung benötigt hingegen eine Koordinatenwahl und eine Metrik. [Menck et al. (2013), Originalarbeit](https://www.pik-potsdam.de/members/kurths/recent-selected-publications/nphys2516.pdf).

Die vorgeschlagene Frame-Brücke `Latitude/(Latitude+ρ/(1-ρ))` addiert bei einer dimensionalen Latitude eine Länge und eine dimensionslose Größe. Ein Meter und hundert Zentimeter ergeben dann unterschiedliche Scores: 0,5 beziehungsweise 0,990099 bei Druckterm 1. Eine dimensionslose Breite `Latitude/Latitude_ref` würde dieses Einheitenproblem beheben, benötigt aber einen begründeten Referenzmaßstab. `ρ/(1-ρ)` stammt außerdem aus einem speziellen Warteschlangenmodell; dessen Voraussetzungen sind nicht durch eine allgemeine Informationsrate garantiert.

**Reparatur:** Latitude-Distanz, Basin-Wahrscheinlichkeit und lokale Rate separat ausweisen. Die neue Frame-Brücke bleibt bis zur Normierung und Kalibrierung ein Vorschlag; der Vergleich mit 0,84 ist noch nicht wohldefiniert.

### E. Eine Bifurkation beweist keine neue unabhängige Dimension

**Stellen:** system_layer_utac, Abschnitt 3.5; FORMALISM, „bestätigter SPEZIALFALL“ von Typ-2-Emergenz.

Die Pitchfork-Bifurkation erzeugt zusätzliche Gleichgewichte innerhalb desselben eindimensionalen Zustandsraums. Ein Vorzeichen- oder Zweiglabel kann für eine grobe Beschreibung nützlich sein; es ist aber eine Funktion des bereits vorhandenen Zustands. Eine größere notwendige Modell- oder Gedächtnisdimension ist damit noch nicht gezeigt.

**Reparatur:** „Neue stabile Zustandsalternativen/Ordnungsstruktur“ ist hier belegt. „Neue unabhängige Dimension“ erfordert eine eigene Definition und einen Vergleich mit Modellen gleicher Dimension, zusätzlichen latenten Zuständen oder Gedächtnis.

### F. Die vier Informationsgrößen benötigen explizite Geltungsbereiche

**Stellen:** information_layer_crep, physikalische Verankerung und finale Formeln; FORMALISM, Schicht 1.

- `S=-λ_max` ist nicht für alle Systemtypen dasselbe Stabilitätsmaß. Bei einem stabilen autonomen Grenzzyklus gibt es einen neutralen Phasenexponenten; ein stabiler chaotischer Attraktor kann einen positiven Exponenten besitzen. Lokale Fixpunktstabilität, orbitale Stabilität und Erhalt einer gespeicherten Information sind verschiedene Fragen. Die behauptete Invarianz braucht Bedingungen an Koordinatentransformationen und eine feste Zeitparametrisierung.
- `B log₂(1+SNR)` ist die Shannon-Hartley-Kapazität unter bestimmten Kanal- und Rauschannahmen. Eine beliebige Zahl von Freiheitsgraden als B einzusetzen macht daraus kein domänenuniverselles Gesetz. Das Kanalmodell muss Ein- und Ausgang, Rauschen und Beschränkungen festlegen. [Shannon (1948), insbesondere Theorem 17](https://people.math.harvard.edu/~ctm/home/text/others/shannon/entropy/entropy.pdf).
- `I(X;X')/H(X)` liegt für diskrete Variablen mit endlichem `H(X)>0` zwischen 0 und 1. Für kontinuierliche Variablen mit differentieller Entropie gilt diese Behauptung nicht allgemein. Selbst im diskreten Fall misst die Formel Informationsretention: Auch eine invertierbare Umbenennung erhält den Wert 1, ohne eine identische Kopie zu sein.
- Klassische verlustfreie Kopien sind möglich. Quanten-No-Cloning, Rate-Distortion unter einer festgelegten Verzerrungsfunktion und Fehlerschwellen in Replikationsmodellen sind unterschiedliche Resultate; die angeführten Namen liefern keine gemeinsame universelle Schranke für das definierte R.

**Reparatur:** Die vier Rollen können die gemeinsame Schnittstelle bilden. Konkrete Messverfahren sollten ihren Geltungsbereich, Einheiten, Unsicherheit und Fälle „nicht bestimmbar“ mitliefern. Fehlen die Voraussetzungen, sollte kein künstlicher universeller Zahlenwert entstehen.

### G. Die thermodynamische Begründung und die exp/tanh-Regel sind zu stark

**Stellen:** information_layer_crep, Landauer; coupling_layer_afet, Abschnitte 2–3; FORMALISM, thermodynamischer Boden.

Landauers Prinzip betrifft die irreversible Löschung unter spezifizierten Bedingungen. Es beweist nicht, dass jede Speicherung fortlaufend eine feste Mindestleistung verbraucht. Ebenso bedeutet nichtnegative Entropieproduktion nicht strikt positive Kosten jeder Kopplung; der Wert null ist zugelassen. [Plenio und Vitelli, The physics of forgetting](https://arxiv.org/abs/quant-ph/0103108).

Aus „Rate“ folgt nicht „exponentiell“ und aus „beschränkt“ folgt nicht „tanh“. Arrhenius benötigt ein Aktivierungsmodell; eine Ising-artige Antwort benötigt entsprechende mikroskopische/statistische Annahmen. Eine dimensionslose Amplitude ist außerdem nicht automatisch auf [0,1] beschränkt: `S₈=σ₈ sqrt(Ω_m/0,3)` ergibt beispielsweise für σ₈=1,2 und Ω_m=0,3 den Wert 1,2. [Definition in einer Originalarbeit zur S₈-Spannung](https://arxiv.org/html/2209.06217v2).

**Auswirkung:** Die bestehenden exp/tanh-Funktionen in `afet-tensions` können phänomenologische Modellansätze bleiben. Die neue universelle Begründung dafür ist durch diese Argumente nicht erbracht. Ein besserer Fit entscheidet zudem nicht allein zwischen mikroskopischen Mechanismen.

### H. Das Worked Example wendet sein Individuationskriterium noch nicht nachweisbar an

**Stellen:** worked_example_afet_tensions, Abschnitte 2–5; system_layer_utac, Individuation.

Die Trennung von Rechenmodellen und Ausgabe-Wrappern ist eine hilfreiche Softwareanalyse. Die behauptete wissenschaftliche Schlussfolgerung „genau zwei individuierte Systeme“ folgt aber noch nicht aus dem vorgeschlagenen Kriterium: Das Beispiel berechnet weder Excess-S noch eine unabhängig festgelegte Baseline oder deren Unsicherheit. Eine statische H₀-Antwortfunktion hat für sich keine Erholungsdynamik.

Die Γ-Gleichung ist eine ODE in Rotverschiebung z. Stabilität in kosmischer Zeit verlangt zusätzlich die Umrechnung `dot z=-(1+z)H(z)` im expandierenden FLRW-Modell. Das Vorzeichen der Entwicklung entlang zunehmender z und entlang fortschreitender Zeit ist verschieden.

Der Ausdruck `beta_from_h0(h0_local())` ist ein algebraischer Hin-und-zurück-Weg zur Ausgangskonstante. Das ist redundant, belegt für sich aber keinen wissenschaftlichen Kalibrierungszirkel. Ein Zirkel entsteht, wenn dieselbe Information anschließend als unabhängiger Bestätigungsbefund ausgegeben wird. Der frühere Γ-Kalibrierungsfehler und dieser Rundtrip sollten daher getrennt beschrieben werden.

**Reparatur:** Das Worked Example vorerst als Abhängigkeitsanalyse kennzeichnen; für Individuation Zustand, Dynamik, Partition, Baseline und Messverfahren nachreichen. Positive Excess-Stabilität kann eine Arbeitsdefinition sein; ihre Äquivalenz zu operationaler Geschlossenheit/Autopoiesis ist nicht hergeleitet.

### I. Die zusätzlichen Beispiele zeigen, wo die Klassifikation geschärft werden muss

**Stellen:** Worked Examples zu Cygnus, Neural Avalanche und Solar Flare.

Die Unterscheidung von Engine, Zustand, Diagnostik und Ausgabe ist nützlich. Ob eine Gleichung numerisch integriert oder analytisch ausgewertet wird, darf dabei nicht über „System oder kein System“ entscheiden. `phase(t)=ωt mod 2π` ist eine analytische Lösung von `dot phase=ω`. Ebenso ist `Dst(t)=Dst(0)exp(-t/τ)` eine analytische Lösung einer Relaxationsgleichung. Beide können dynamische Modelle beschreiben; ihre Stabilitätseigenschaften unterscheiden sich, nicht ihre Berechtigung aufgrund der gewählten Rechenmethode. Eine engere Kategorie „selbststabilisierende Einheit“ lässt sich definieren, braucht aber weiterhin den behaupteten Excess-S-Vergleich.

Beim Solar-Paket ist außerdem zwischen einer verfügbaren Methode und ihrer Verwendung zu unterscheiden: `GeomagneticStorm` enthält `dst_recovery()` und `simulate_storm_profile()`. Der geprüfte `run_cycle()` ruft beim Flare jedoch `predict_dst()` auf und protokolliert den Spitzenwert; die Erholung wird dort nicht als zweiter fortlaufender Prozess integriert oder ausgewertet. Eine gerichtete Ereignisabhängigkeit ist belegt, eine vollständig mitlaufende zweite Relaxation in diesem Pfad nicht. [Geomagnetische Methoden](https://github.com/GenesisAeon/solar-flare-utac/blob/86ed000c70be276ba4352cc61105d5c423cd330f/src/solar_flare_utac/geomagnetic.py), [Aufrufpfad](https://github.com/GenesisAeon/solar-flare-utac/blob/86ed000c70be276ba4352cc61105d5c423cd330f/src/solar_flare_utac/system.py).

Die Solar-Rate `r_buildup+λ_quiet=0,065` ist unter konstantem quiet-λ die korrekte Kontraktionsrate des glatten Teilmodells. Sie ist noch nicht der globale Lyapunov-Exponent des Modells mit Schwellenereignissen, Reset und Rauschen. Dafür müssen auch die Ereigniszeitpunkte und Reset-Abbildung in die Störungsentwicklung eingehen.

Bei Neural Avalanche ist `S=r=0,15/h` für die zugehörige kontinuierliche lineare ODE korrekt. Der tatsächlich implementierte unbeschnittene Euler-Schritt hat den Störungsfaktor `1-rΔt`; sein Exponent pro Stunde ist `log|1-rΔt|/Δt`. Bei Δt=1 h ergibt das −0,162519/h. Das widerlegt die ODE nicht, verlangt aber eine saubere Kennzeichnung, welcher Wert berichtet wird. Zusätzlich fehlen `effective_r()` im geprüften Code explizite Zeitschritte: Bei gleichmäßigen Abständen ungleich einer Stunde schätzt es `rΔt` pro Schritt, nicht unmittelbar r pro Stunde. [HomeostaticPlasticity](https://github.com/GenesisAeon/neural-avalanche-utac/blob/2e06f35d7e3c084921b07babf330e36695e8dd6b/neural_avalanche_utac/homeostasis.py).

Auch eine inverse Anpassung `Γ=atanh(η)/σ` ist als Kalibrierung bei festgelegtem σ mathematisch zulässig. Problematisch wäre, die anschließende Rückgewinnung desselben η als unabhängige Bestätigung zu zählen oder Γ und σ aus nur diesem einen Produkt getrennt identifizieren zu wollen. Die inzwischen eingefügten Offenlegungen adressieren genau diese Unterscheidung. „Inverse Kalibrierung“ sollte deshalb nicht pauschal mit „unzulässiger Zirkelschluss“ gleichgesetzt werden.

## 3. Empfohlene Nacharbeit am bereits verbreiteten Stand

1. **Aktuellen Stand konsolidieren:** README/FORMALISM auf die späteren Roadmap- und Follow-up-Ergebnisse verweisen lassen. Γ-Refit als erledigte Kalibrierung führen; lokale und veröffentlichte Änderungen unterscheiden. „Keine neuen Fehler gefunden“ beschreibt ein früheres Review-Ergebnis, keine fortdauernde Fehlerfreiheit.
2. **Zentrale Identitäten korrigieren:** β≡S und V≡Panarchy≡L durch sauber typisierte Größen und explizite Modellabbildungen ersetzen. Die schon umgesetzten Bugfixes und Testbereinigungen bleiben davon unberührt.
3. **Nutzer der alten Bedeutungen suchen:** Vor Änderungen pro betroffenem Paket prüfen, ob eine Formel gerechnet wird, ein Default übernommen wird oder nur ein Name/Kommentar vorkommt. In der hier geprüften Stichprobe ist kein flächendeckender Einbau sämtlicher neuer S/K/R/V-Formeln nachgewiesen.
4. **Einen vollständigen dynamischen Fall härten:** Zustand, Eingabe, Zeitskala, Beobachtung und Kopplung festlegen; lokale Rate, Basin-Wahrscheinlichkeit und Informationsrate getrennt messen. Erst anschließend prüfen, ob die zusätzlichen Größen Vorhersagen verbessern.
5. **Kalibrierung von Bewährung trennen:** Fit-Daten, Benchmark-Daten und zurückgehaltene Daten kennzeichnen. Auch der neue Γ/κ-Fit braucht eine Unsicherheits- und gegebenenfalls Kovarianzbehandlung sowie einen wirklich unabhängigen Vorhersagevergleich.

Die Sonderbehandlung von `Feldtheorie` und die Ausnahmen der Climate/Ecology-Serie aus eurer Roadmap sind bei späteren Codeänderungen weiterhin zu beachten. Diese Gegenprüfung selbst verändert keine Originaldateien oder veröffentlichten Pakete.

## 4. Anschluss an den früheren G03-Stand

Der bereitgestellte Chat-Ausschnitt berichtet für GW-PRED-002 über 20 Wiederholungen einen MAE-Vorteil von **0,00759**, mit 95-%-Bootstrapintervall **[0,00355; 0,01173]**. Der vorab verlangte Mittelwert von 0,01 wird damit nicht erreicht. Die Bestätigungsregel ist nach diesen berichteten Zahlen nicht erfüllt. Das Intervall liegt zwar oberhalb null, umfasst aber 0,01: positive Richtung und unsichere praktische Größenordnung sind getrennt zu berichten.

Gegen die feste COARSE-Referenz nennt derselbe Ausschnitt nur etwa **0,00106**, mit einem deskriptiven Intervall, das null umfasst. Diese Referenzabhängigkeit gehört zum Ergebnis. Sie lässt sich nicht nachträglich durch Auswahl des günstigeren Vergleichs auflösen.

Auf dem geprüften öffentlichen [G03-Stand 296d714](https://github.com/GenesisAeon/Feldtheorie/tree/296d7147b60144b81162607a9c73ccd0acf84c38/experiments/geometric_waste_predictive_v2/runs/confirmatory_001) sind die Vorbereitung und Prüfsummen dokumentiert. Das endgültige Rohdaten-/Ergebnisarchiv lag in den hier geprüften Quellen nicht vor. Die im Chat berichtete Prüfung aller 20.480 Zustände wurde hier deshalb **nicht erneut unabhängig durchgeführt**. Der belastbare Status lautet: „Abschluss und gemischtes Ergebnis berichtet; veröffentlichte Ergebnisartefakte noch abzugleichen.“

Die neue Formalismusarbeit ist keine nachträgliche Bestätigung von G03. Umgekehrt entscheidet der begrenzte Vorhersageversuch nicht über die gesamte Drei-Schichten-Architektur.

## 5. Einordnung der früheren Kosmologie-TXT

Der Text benennt reale Forschungsfragen, zieht aber mehrfach stärkere Schlüsse als die verlinkten Arbeiten.

| Aussage/Problem | Belastbare Einordnung |
|---|---|
| H₀-Spannung | H0DN berichtet 73,50±0,81 km/s/Mpc. Die offizielle Mitteilung nennt je nach Vergleich ungefähr 5–7 Standardabweichungen. Die konkrete 7,1-Zahl der TXT ist hier nicht anhand einer eindeutig bezeichneten Vergleichskombination bestätigt. Auch eine hohe Signifikanz allein entscheidet nicht zwischen übersehenen Systematiken und neuer Physik. [H0DN/ISSI](https://www.issibern.ch/hubble-constant-press-release/). |
| Di Valentino habe Messfehler ausgeschlossen | Die genannte Arbeit betont gerade Modellannahmen, Parameterentartungen und Konsistenz zwischen Datensätzen. Die definitive Behauptung der TXT ist nicht gedeckt. [Di Valentino, Cracks…](https://arxiv.org/abs/2601.01525). |
| Quasardipol über 5σ | In der genannten Arbeit sind es 4,4σ für Quasare und 2,6σ für Radiogalaxien; 5,1σ ist die gemeinsame Signifikanz. Der Befund verdient Prüfung, ist aber keine alleinige Entscheidung zugunsten einer bestimmten Alternative. [Secrest et al. (2022)](https://arxiv.org/abs/2206.05624). |
| Giant Arc/Big Ring seien grundsätzlich unmöglich | Die Bewertung hängt wesentlich von Strukturdefinition und Nullmodell ab. Hier existiert eine konkrete Fachkontroverse: [Sawala et al.](https://arxiv.org/abs/2502.03515) finden ähnliche Muster im Standardmodell; [Lopez und Clowes](https://arxiv.org/abs/2504.14940) widersprechen der Methodik. Das ist keine unstrittige harte Größenverbotsgrenze. |
| Frühe JWST-Galaxien erzwängen neue Dunkle Materie | Die TXT nennt für die konkreten Scheiben-/Altersbehauptungen keine eindeutig prüfbare Originalarbeit. Eine neuere Analyse zeigt, dass Massenunsicherheiten und statistische Verzerrungen die Spannung für ihre untersuchte Stichprobe erheblich reduzieren. Das entscheidet nicht sämtliche JWST-Fragen. [Krishnan und Abazajian](https://arxiv.org/html/2511.13708v3). |
| DESI habe dynamische Dunkle Energie entdeckt | DESI DR2: BAO allein sind mit flachem ΛCDM gut beschreibbar; zusammen mit CMB und Supernovae beträgt die Präferenz für das untersuchte dynamische Modell 2,8–4,2σ, abhängig von der Supernova-Stichprobe. Die Autoren erwähnen mögliche unbekannte Systematiken. [DESI-Originalarbeit](https://arxiv.org/abs/2503.14738). |

Zusätzlich verwechselt die TXT an einer Stelle H₀ mit einer zeitlich konstanten Expansion. H₀ bezeichnet den heutigen Wert des zeitabhängigen Hubble-Parameters; ΛCDM setzt nicht `H(t)=konstant` voraus. Eine Entwicklung dunkler Energie, eine Abnahme von H und eine Abbremsung der Expansion sind ebenfalls unterschiedliche Aussagen.

**Folge für AFET:** Diese Spannungen können geeignete Testfragen motivieren. Eine Bestätigung von AFET erfordert konkrete, vorab festgelegte und gegenüber Vergleichsmodellen unterscheidbare Vorhersagen. Eine Problemliste des Standardmodells übernimmt diese Prüfung nicht.

## 6. Reproduzierbare Gegenbeispiele

Die folgenden acht Prüfungen sind eigene kleine Gegenbeispiele zu Allgemeinbehauptungen. Sie reproduzieren nicht die fehlenden originalen `verification/`-Skripte und testen nicht das gesamte Paketökosystem. Ausführbar mit Python und NumPy.

```python
import json
import math
import numpy as np

out = {}

# 1: Identische stationäre Sigmoidkurve, verschiedene Erholungsraten.
out['sigmoid'] = [dict(beta=4, tau=t, slope=1, recovery=1/t)
                  for t in (1, 10)]
assert out['sigmoid'][0]['recovery'] != out['sigmoid'][1]['recovery']

# 2: Die beiden angegebenen kubischen Dynamiken sind verschieden.
a, theta, b = 2.0, 1.0, 0.0
out['cusp_reference'] = {
    'original_drift': -theta**3 + a*(theta-theta) + b,
    'centered_drift': 0.0,
    'original_negative_derivative': 3*theta**2-a,
    'centered_negative_derivative': -a,
}
assert out['cusp_reference']['original_drift'] == -1

# 3: a>0 allein bedeutet nicht Bistabilität.
roots = np.roots([1, 0, -1, -1])  # a=1, b=1
out['a1_b1_real_roots'] = int(np.sum(np.abs(roots.imag) < 1e-10))
assert out['a1_b1_real_roots'] == 1

# 4: Satteldistanz und Wahrscheinlichkeit eines Beckens.
out['basin'] = [dict(a=a, S_origin=-a, S_branch=2*a,
                     distance=math.sqrt(a), probability=0.5)
                for a in (1, 4)]
assert out['basin'][0]['distance'] != out['basin'][1]['distance']
assert out['basin'][0]['probability'] == out['basin'][1]['probability']

# 5: Eine gerichtete Einflussmatrix ist nicht automatisch dissipativ.
L = np.array([[0., 1.], [0., 0.]])
X = np.array([1., -1.])
out['entropy_quadratic_form'] = float(X @ L @ X)
assert out['entropy_quadratic_form'] == -1

# 6: I/C hängt vom Zeitfenster ab, Rate/C hier nicht.
out['information'] = [dict(seconds=t, I_over_C=100*t/1000,
                            rate_over_C=100/1000) for t in (1, 10)]
assert out['information'][0]['I_over_C'] != out['information'][1]['I_over_C']

# 7: Dimensionsbehaftete Breite ohne Normierung: Einheitenabhängigkeit.
out['frame'] = dict(metres=1/(1+1), centimetres=100/(100+1))
assert not math.isclose(out['frame']['metres'], out['frame']['centimetres'])

# 8: Die Definition von S8 setzt keine Obergrenze 1.
out['S8'] = 1.2 * math.sqrt(0.3/0.3)
assert out['S8'] > 1

print(json.dumps(out, indent=2))
```

Ausführung dieser acht Gegenbeispiele: erfolgreich, Python 3.12.14 / NumPy 2.3.5. Kernwerte: Erholungsraten 1 und 0,1; ursprünglicher kubischer Drift −1 statt 0; ein reeller Fixpunkt bei a=b=1; Satteldistanzen 1 und 2 bei gleicher Beckenwahrscheinlichkeit 0,5; quadratische Entropieform −1; unnormierte Frame-Werte 0,5 und 0,990099; S₈=1,2.
