# Polyeder, Sakurai und Saturn: belastbare Anschlüsse an SCF

**Recherche, Bewertung und abgegrenzte Optionen für Claude-Code**  
Stand: 01.10.2026 · Grundlage: Johanns Datei `Kandidaten_Polyeder_Sakurai_Saturn_2026-09-30.md`.

## 1. Entscheidungsvorschlag

Alle drei Themen sind anschlussfähig. Sie sollten unterschiedliche Aufgaben erhalten. Das gemeinsame Forschungsziel ist, **welche Eigenschaften eine Abbildung erhält, was Beobachtungen unterscheiden können und wie weit ein Modellschluss trägt**. Daraus folgt keine gemeinsame physikalische Ursache der drei Phänomene.

| Kandidat | Sinnvollster Beitrag | Passung zu SCF | Erster Umfang | Empfehlung |
|---|---|---|---|---|
| Genus-3-Polyeder | Invarianten, Strukturverlust, Nachweis einer Einbettung | Sehr direkt zum Korrespondenz- und Evidenzkern | Zwei kleine Graphen plus exakte Gegenbeispiele | Zuerst als begrenztes mathematisches Beispiel |
| Sakurais Objekt | Interner Energiespeicher, verzögerte Antwort, veränderlicher Messoperator | Sehr gut für Dynamik versus Beobachtung und Nichtidentifizierbarkeit | Analytischer Speicherpuls und synthetische Mehrkanalbeobachtung | Danach als Methodenpilot; echte Sternmodellierung gesondert |
| Saturn-Hexagon | Moden, Symmetrie, Randbedingungen und Mechanismenvergleich | Gut als kontrollierte Erweiterung der Musteranalyse | Fourier-Diagnostik und lineare Wellenkontrolle | Dritter Schritt, zunächst ohne planetare Vollsimulation |

Für Johanns Thema nichtstationärer Treiber ist Sakurai der naheliegendste Einstieg. Für einen kleinen, klar abnehmbaren SCF-Beitrag ist das Polyederbeispiel am stärksten. Saturn hat großes Potenzial, aber auch die größte Gefahr, ein bekanntes Muster durch passend gewählte Parameter lediglich nachzuzeichnen.

**Auftragsgrenze:** Dies ist eine Bewertung mit optionalen Umsetzungspaketen. Die Nachfrage nach Anschlussfähigkeit wird nicht als Auftrag verstanden, alle drei Domänen sofort zu implementieren. Der gesonderte Myonium-Plan MU0–MU7 bleibt unabhängig ausführbar.

## 2. Quellenprüfung und Korrekturen der Ausgangsdatei

Die hochgeladene Sammlung ist ein guter Wegweiser. Für die folgenden Schlussfolgerungen wurden Primärquellen herangezogen. Die ursprüngliche Datei wird durch diese Bewertung ergänzt, nicht überschrieben.

### 2.1 Polyeder: eine neue Vergleichskonstruktion macht den Fall besonders interessant

Mizhaevs [arXiv:2609.17700](https://arxiv.org/abs/2609.17700) ist mit Titel *Integer Realization of an Equivelar Octahedron of Genus 3* und den Angaben V=24, E=36, F=8 als Primärquellen-Suchtreffer verifiziert. Der direkte Volltextabruf scheiterte in dieser Recherche. Die vollständige Koordinatenkonstruktion wurde deshalb hier nicht unabhängig geprüft.

Zusätzlich liegt seit 26.09.2026 der vollständig gelesene Vorabdruck von Röst und Vígh vor: [A second eight-faced polyhedron in which every two faces share an edge](https://arxiv.org/html/2609.32998v1). Er beschreibt eine zweite Konstruktion mit denselben groben Kennzahlen, aber anderer Kombinatorik. Bei den doppelt benachbarten Flächen ergibt sich einmal ein Achterzyklus, einmal ergeben sich zwei Viererzyklen. Außerdem korrigiert die Vergleichsanalyse eine Vereinfachung der Sammlung: Mizhaevs Symmetrie wird durch T(x,y,z)=(y,−x,−z) erzeugt, also eine Drehspiegelung, keine reine Vierteldrehung. Abstrakt ist die Gruppe zyklisch von Ordnung vier. Beide Arbeiten sind hier als Vorabdruckbefunde zu behandeln.

**Redaktionelle Konsequenz:** „C4, also nach jeder Vierteldrehung gleich“ ersetzen durch die konkrete Transformation mit Determinante −1. „Ganzzahlige Koordinaten beweisen Nichtdurchdringung“ ebenfalls abschwächen: Sie ermöglichen exakte Prüfungen; deren Durchführung bleibt erforderlich.

### 2.2 Sakurai: ein genaueres Beispiel für Dynamik und Beobachtung

Geprüfte Originalarbeit: Marcolino et al., [The emergence of a [WC] star in Sakurai’s object](https://academic.oup.com/mnras/article/552/1/stag1533/8793699), MNRAS, veröffentlicht 16.09.2026, DOI [10.1093/mnras/stag1533](https://doi.org/10.1093/mnras/stag1533). Sie analysiert VLT/FORS2-Spektren von 2023 mit expandierenden NLTE-Atmosphärenmodellen. Die bevorzugte Temperatur liegt um 30,5 kK; der konservative Bereich beträgt 27–36 kK. Entfernung, Extinktion und Leuchtkraft sind stark entartet; Leuchtkraft und Klumpungsfaktor werden im bevorzugten Modell angenommen. Der Zentralstern ist nicht direkt abgebildet. Die Arbeit lässt modellabhängig weitere Abkühlungsausflüge in der Entwicklung zu.

**Redaktionelle Konsequenz:** Die Aussagen „Helium aufgebraucht, weiterer Puls ausgeschlossen“, „der gesamte Energiespeicher war verbraucht“ und eine sichere unmittelbare Sicht auf den Stern nicht übernehmen. Sehr später Heliumschalenpuls, innere Entwicklung, Staub, Streuung und Wind müssen getrennt werden. Temperatur in Kelvin und die Beobachtungsepoche angeben; die Publikation von 2026 ist keine Messung des Zustands im Oktober 2026. „Staub lichtet sich seit 2021“ bleibt ohne separat geprüfte Messreihe außerhalb des Modellinputs.

### 2.3 Saturn: geometrische Ähnlichkeit genügt nicht zur Mechanismenwahl

Yadav und Bloxham, [Deep rotating convection generates the polar hexagon on Saturn](https://pmc.ncbi.nlm.nih.gov/articles/PMC7322008/), PNAS 2020, DOI [10.1073/pnas.2000317117](https://doi.org/10.1073/pnas.2000317117), zeigen polygonale Jets in einer dreidimensionalen Konvektionssimulation. Die untersuchten Beispiele treffen weder automatisch die sechs Seiten noch die beobachtete Drift; die Arbeit benennt diese Grenzen selbst. Das liefert einen möglichen Mechanismus, keine eindeutige Erklärung allein aus dem Umriss.

Fletcher et al., [A hexagon in Saturn’s northern stratosphere surrounding the emerging summertime polar vortex](https://www.nature.com/articles/s41467-018-06017-3), Nature Communications 2018, DOI [10.1038/s41467-018-06017-3](https://doi.org/10.1038/s41467-018-06017-3), behandeln den hochreichenden, jahreszeitlich veränderlichen Zusammenhang. „Ein zweites Hexagon“ sollte nicht ohne Weiteres als zwei unabhängige Systeme modelliert werden.

**Redaktionelle Konsequenz:** Für einen ersten Pilot reichen diese beiden Primärarbeiten. Südpol-Zehneck, JWST-Ionosphäre, Jupitervergleich und Medienzahlen aus der Ausgangsdatei wurden hier nicht einzeln bis zu ihren Originaldaten auditiert; sie werden deshalb nicht als verifizierte Randbedingungen verwendet. Gasgeschwindigkeit, Rotation des Bezugssystems und Drift des Musters sind unterschiedliche Messgrößen.

## 3. Polyeder: eine präzise Brücke zum Korrespondenzkern

### 3.1 Welche Ebenen auseinanderzuhalten sind

Ein Objekt kann auf mehreren Ebenen beschrieben werden:

| Ebene | Information | Was daraus nicht automatisch folgt |
|---|---|---|
| Kennzahlen | V, E, F, Euler-Charakteristik | Eindeutige Kombinatorik |
| Inzidenz | Welche Flächen an welchen Kanten zusammentreffen | Einbettbarkeit mit ebenen, einfachen Flächen |
| Topologische Fläche | Zusammenhang, Orientierbarkeit, lokale Mannigfaltigkeit | Eine konkrete geometrische Realisierung |
| Geometrische Realisierung | Koordinaten und Flächenzyklen | Dass jede sichtbare oder numerisch nahe Symmetrie exakt ist |
| Beobachtungsabbildung | Gewählte Kennzahlen oder Bilder | Rekonstruktion aller verlorenen Strukturdaten |

Definiere zunächst die Abbildung O(X)=(V,E,F). Die Gleichheit O(X)=O(Y) ist eine Aussage über diesen Messoperator. Sie identifiziert X und Y nicht als kombinatorische Objekte. Ein verfeinerter Operator ergänzt beispielsweise die Zusammenhangskomponenten des Graphen doppelt benachbarter Flächen.

Ein einfacher unabhängiger Kontrollfall genügt schon: C8 und C4⊔C4 haben jeweils acht Knoten, acht Kanten und überall Grad zwei. Der erste Graph hat eine Komponente, der zweite zwei. Damit sind sie nicht isomorph. Dies illustriert exakt, wie eine Verfeinerung der Beobachtung eine zuvor gemeinsame Beobachtungsfaser aufspaltet. Das Skript prüft diesen Graphfakt; es zertifiziert dadurch noch keine der vollständigen Polyederkonstruktionen.

### 3.2 Was ein ehrlicher Flächenprüfer leisten müsste

Erst wenn ein endlicher Flächenkomplex geschlossen, zusammenhängend und orientierbar ist und an jedem Knoten einen Kreis als Link besitzt, darf χ=2−2g zur Genusbestimmung verwendet werden. Kantenanzahl zwei pro Kante reicht allein nicht: Zwei Flächenkomplexe können an einem singulären Knoten zusammengeklebt sein. Zusammenhang und Knotenlinks sind eigene Prüfungen.

Für eine geometrische Zertifizierung kommen hinzu: keine degenerierten oder selbstschneidenden Flächen; exakte Koplanarität; konsistente Randzyklen; erlaubte Schnittmengen jeder Flächenpaarung; keine ungewollten Berührungen oder Durchdringungen. Nichtkonvexe Flächen benötigen korrekte Zerlegung oder einen geeigneten Polygonalgorithmus. Eine Dreiecksfächerung um einen beliebigen Flächenpunkt ist nicht automatisch gültig.

Rationale Eingaben ermöglichen Determinanten und Inzidenztests ohne willkürliche Float-Toleranz. Ein nahezu ebener Punkt mit Abstand 10^-12 darf beim Modus „exakt“ nicht auf die Ebene gerundet werden. Float-Daten benötigen einen anderen, ausdrücklich numerischen Evidenzstatus.

### 3.3 Optionale Pakete TP0–TP3

| Paket | Inhalt | Abnahme / Grenze |
|---|---|---|
| TP0 | Quellen- und Statusnotiz; korrekte Unterscheidung abstrakter Gruppe und räumlicher Transformation | Keine unbewiesene Behauptung einer Koordinatenzertifizierung |
| TP1 | Endliche Beobachtungsabbildungen für C8 und C4⊔C4; Adapter an vorhandene Beobachtungsfasern | Grobe Faser gemeinsam, verfeinerte Faser getrennt; TP-C02 |
| TP2 | Kleiner exakter Inzidenz- und Topologieprüfer mit eigenen synthetischen Flächenfixtures | Rand, nichtmanifold Knoten, inkonsistente Orientierung und getrennte Komponenten werden erkannt; χ allein reicht nicht |
| TP3 | Optionaler exakter Einbettungsprüfer und auditierte Paper-Reproduktion | Nur nach Zugang zu vollständigen Koordinaten, geprüfter Provenienz und eigenständiger Implementierung der geometrischen Tests |

Vorgeschlagene Ablage: zunächst `validation/polyhedral_observation_pilot.py` und `docs/polyhedral_observation_pilot.md`. Ein allgemeines `topology/`-Paket erst, wenn TP2 einen konkret wiederverwendbaren Vertrag bekommt. Kein neuer Topologie-Unterbau allein wegen eines attraktiven Beispiels. Das Thema gehört nicht in eine Rubrik „nichtstationärer Treiber“.

## 4. Sakurai: interner Speicher, Antwortzeit und Sichtbarkeit

### 4.1 Ein wichtiger begrifflicher Gewinn

Ein zeitlich veränderliches Signal braucht nicht zwingend einen von außen exponentiell anwachsenden Treiber. Nichtstationarität kann aus inneren Zuständen, verzögerter Übertragung oder einem veränderten Messoperator entstehen. Ebenso bedeutet eine lineare Differentialgleichung nicht, dass jede Lösung eine Gerade mit homogener Steigung ist.

Diesen Unterschied sollte SCF gerade hier sichtbar machen. Das bestreitet die Bedeutung nichtlinearer Zündprozesse nicht; es verlangt, deren Notwendigkeit anhand unterscheidender Beobachtungen zu prüfen. Ein Sternpuls ist auch nicht automatisch ein irreversibler Kippübergang zwischen zwei Attraktoren. Die Begriffe Puls, Instabilität, Hysterese und Kippen benötigen jeweils eigene Kriterien.

### 4.2 Minimaler analytischer Kontrollfall

Als **eigenes dimensionsloses Freisetzungs- und Relaxationsmodell**, nicht als berechnetes Sakurai-Modell:

\[
\dot f=-\alpha f,\qquad
\dot E=\alpha f-\beta E,\qquad
\dot Q=\beta E,
\quad f(0)=1,\ E(0)=Q(0)=0.
\]

f ist noch nicht freigesetzte Energie, E ein Zwischenspeicher und Q abgeführte Energie. Damit f+E+Q=1. Für α≠β:

\[
f(t)=e^{-\alpha t},\qquad
E(t)=\frac{\alpha}{\beta-\alpha}
       (e^{-\alpha t}-e^{-\beta t}).
\]

Für α=β lautet der stetige Grenzfall E(t)=αt exp(−αt). Bei α=2, β=1 erreicht E sein Maximum bei t=ln 2. Dort sind f=1/4, E=1/2, Q=1/4. Ein Puls mit Anstieg und Erholung entsteht bereits in diesem linearen gekoppelten System.

Der anfängliche Freisetzungsbeginn wird hier vorausgesetzt. Das Modell erklärt keine thermonukleare Zündung, keine Konvektion und keine Sternstruktur. Genau deshalb ist es eine gute Nullkontrolle. Eine spätere nichtlineare Reaktionsrate r(f,T) muss einen klar benannten zusätzlichen Befund erklären und gegen diese Kontrolle verglichen werden.

### 4.3 Beobachtungsmodell und Entartungen

Ein bewusst einfaches Mehrbandmodell lautet:

\[
F_\lambda(t)=\frac{L(t)s_\lambda(T(t))}{4\pi D^2}
 e^{-k_\lambda\tau_d(t)}+B_\lambda(t).
\]

Hier sind sλ eine festgelegte Spektralform, D die Entfernung, τ_d ein Staubparameter, kλ eine bekannte Extinktionskurve und Bλ ein Zusatzbeitrag. Eigene Staubemission, Streuung und Nebellinien benötigen bei realen Daten weitere Terme. Dieses Modell bildet keine vollständige NLTE-Spektralanalyse ab.

Schon in einer normierten Einbandversion F=L exp(−τ) sind (L,τ)=(1,0) und (e,1) beobachtungsäquivalent. Ein Helligkeitsanstieg kann deshalb von L, von τ oder von beidem stammen. Für bekannte Spektralform und unterschiedliche bekannte kλ können zwei Bänder im vereinfachten Logmodell die Entartung auflösen. Bei unbekannter Temperatur, Entfernung oder Hintergrund ist das nicht automatisch der Fall.

Eine zweite mathematische Kontrolle nutzt den transformierten Radius eines vereinfachten Windmodells: Bei festem T, Windtempo und Klumpungsfaktor hält R_*→4R_* zusammen mit Ṁ→8Ṁ die Kombination R_*(v∞/Ṁ)^(2/3) konstant; die Leuchtkraft skaliert dabei um Faktor 16. Die algebraische Invarianz ist exakt. Die Gleichheit realer normierter Spektren bleibt eine modellabhängige Näherung. Diese Ebenen müssen getrennt berichtet werden.

### 4.4 Optionale Pakete SK0–SK4

| Paket | Inhalt | Abnahme / Grenze |
|---|---|---|
| SK0 | Quellenmatrix mit Beobachtungsepochen, gemessenen und angenommenen Parametern | Ein einzelner neuer Temperaturpunkt wird nicht zur dichten Entwicklungszeitreihe |
| SK1 | Freisetzung, Zwischenspeicher, Erhaltung und analytischer Grenzfall α=β | SK-C01; Positivität und Energiebilanz; lineares Nullmodell bleibt erhalten |
| SK2 | Synthetischer Ein- und Mehrband-Messoperator | SK-C02 und SK-C04; bekannte und unbekannte Spektralform getrennt |
| SK3 | Identifizierbarkeit der Windskalierung; dynamischer versus beobachtungsbedingter Wandel | SK-C03; algebraische Invarianz nicht als exakte Spektralidentität ausgeben |
| SK4 | Optionaler echter Spektral- oder Zeitreihenpilot | Nur mit zugänglichen Daten, Unsicherheiten, Epochen und passendem Messmodell; kein automatischer CMFGEN-Nachbau |

Vorgeschlagene Ablage zunächst unter `validation/stellar_pulse_observation.py` mit eigenem Dokument. Vorhandene lineare Zustands- und Gedächtnismodule können den Kontrollfall ergänzen. `closure/linear_memory_projection.py::exact_memory_kernel` ist ein existierender Anschluss für lineare Eliminationen; seine Voraussetzungen müssen zu den gewählten Zuständen passen. Ein neues Sternentwicklungs-Framework wäre für SK1–SK3 unnötig.

Sakurai ist damit ein Testfall **innerhalb etablierter Sternphysik**. Eine Verbindung zu Universen-Vererbung oder kosmologischer Selektion benötigt zusätzliche unterscheidende Vorhersagen. Ein beobachteter Sternpuls allein liefert diese nicht.

## 5. Saturn: Musterdiagnostik vor Mechanismenidentifikation

### 5.1 Der vorhandene SCF-Anschluss ist enger als der Medienbegriff Musterbildung

Am gelesenen Repo-Stand behandelt `pattern_formation/core.py` lineare **2×2-Reaktions-Diffusions-Turinganalyse**. Es enthält `jacobian_stability`, `turing_conditions`, `dispersion_relation` und den Schnakenberg-Kontrollfall. Es ist kein Strömungslöser. `docs/pattern_formation_core.md` bezeichnet den Baustein zudem als Review-Paket und verlangt Johanns Zustimmung für die Promotion zum akzeptierten Kern.

Eine Saturn-Erweiterung darf deshalb nicht ein hexagonales Bild an `turing_conditions` übergeben und eine physikalische Erklärung behaupten. Reaktions-Diffusions-Systeme und rotierende Strömungen können beide Moden tragen, haben aber unterschiedliche Operatoren, Erhaltungssätze und Randbedingungen. Ein gemeinsamer Bericht über Wellenzahl, Wachstumsrate und Phase ist eine mögliche Korrespondenz; die Operatoren werden dadurch nicht gleich.

### 5.2 Ein kleiner, nachvollziehbarer Messoperator

Für ein azimutales Feld u(θ,t) auf einem vollen Kreis:

\[
a_m(t)=\frac{1}{2\pi}\int_0^{2\pi}
 u(\theta,t)e^{-im\theta}\,d\theta.
\]

Das Leistungsspektrum |a_m|² ist unter starrer Drehung invariant. Die Phase trägt Lage und Drift. Für u=ε cos[m(θ−θ0)] gilt a_m=(ε/2)exp(−imθ0). Ein Diagramm nur von |a6| verliert daher Information über die Bewegung des Musters.

Bei θ0=Ω_p t folgt d arg(a_m)/dt=−mΩ_p. Diese Inversion benötigt ausreichend dichte Zeiten, entfaltete Phasen und nichtverschwindende Amplitude. Gasgeschwindigkeit und Ω_p sind nicht gleichzusetzen. Maskierte Bildbereiche, Perspektive, ungleichmäßige Abtastung und Höhenselektion gehören später in einen realen Messoperator.

### 5.3 Lineare Wellenkontrolle mit offenem Mechanismus

Eine selbst hergeleitete Kontrollgleichung ist die lineare barotrope Betaebene:

\[
(\partial_t+U\partial_x)
(\nabla^2\psi-L_D^{-2}\psi)+\beta\partial_x\psi=0.
\]

Für eine Fouriermode ergibt sich:

\[
\omega=Uk-\frac{\beta k}{k^2+l^2+L_D^{-2}}.
\]

Dies ist hier ein definiertes Lehrmodell: gleichförmiger Grundstrom, konstante Koeffizienten, lineare Störung, keine erzwungene planetare Instabilität. Dimensionen: U Länge/Zeit, β 1/(Länge·Zeit), k,l inverse Länge. Alle genannten Größen sind Modellparameter, keine neu abgeleiteten Saturnwerte.

Der dimensionslose Kontrollsatz U=1, β=36, k=6, l=0, L_D^-2=0 liefert ω=0. Er zeigt, wann eine **vorgegebene** Mode stationär ist. Er sagt weder, warum diese Mode wächst, noch warum gerade sechs statt fünf oder sieben ausgewählt wird. Wachstum, Sättigung und Selektion brauchen ein erweitertes Modell und einen Vergleich über mehrere m.

Randbedingungen liefern eine weitere harte Kontrolle: In einem Viertelkreis mit periodischer Fortsetzung müssen Moden exp(imθ) die Bedingung exp(imπ/2)=1 erfüllen. Damit sind nur m∈4ℤ erlaubt; m=6 ist ausgeschlossen. Ein so verkleinertes Rechengebiet kann die gewünschte Struktur bereits durch Konstruktion verhindern. Das ist ein allgemeines Scope-Problem und kein bloßes Detail eines Solvers.

### 5.4 Optionale Pakete SA0–SA4

| Paket | Inhalt | Abnahme / Grenze |
|---|---|---|
| SA0 | Quellen- und Größenregister: Gas, Muster, Bezugssystem, Höhe | Keine vermischten Perioden oder Windgeschwindigkeiten |
| SA1 | Fourier-Messoperator und Rotationskontrolle | SA-C02; Phaseninformation bleibt getrennt vom invarianten Betrag |
| SA2 | Lineare Betaebenen-Dispersion und explizite Domainregeln | SA-C01 und SA-C03; keine behauptete Modenselektion |
| SA3 | Vergleich zweier synthetischer Erzeuger mit gleichem Umriss und unterschiedlichen Zeit-/Höhensignaturen | SCF-Beobachtungsfaser für Form allein; feinere Messung kann unterscheiden |
| SA4 | Optionaler datenbasierter Drift-/Höhenpilot oder importierter Simulationslauf | Realdatenprovenienz; echte Pixel-/Spektralfehler; keine vollständige Gasriesensimulation als Voraussetzung |

Vorgeschlagene Ablage: zuerst `validation/azimuthal_pattern_pilot.py`. Gemeinsame Modenberichte nur additiv an das bestehende Musterpaket anschließen, nachdem dessen Status geklärt ist. Numerische Strömungslöser, anelastische Konvektion und Mehrschichtmodelle sind spätere Forschungsarbeit, nicht eine kleine Nebenfunktion von Turinganalyse.

Der zentrale datenbasierte Vergleich sollte neben dem dominanten m auch Drift, Amplitudenvariation, vertikale Kohärenz und Robustheit gegen Beobachtungsmasken berücksichtigen. Ein Modell wird nicht allein deshalb bevorzugt, weil es einen sechseckigen Umriss zeigt. Trainings- und Auswertefenster sowie die Auswahl der betrachteten Wellenzahlen müssen vor dem Vergleich feststehen.

## 6. Gemeinsame Kontroll- und Evidenzregeln

Das beigefügte Skript enthält zwölf unabhängige Kontrollgruppen für diese Bewertung:

| Kennung | Kontrolle | Was dadurch nicht bewiesen ist |
|---|---|---|
| TP-C01 | Euler-Arithmetik und Inzidenzzählung | Mannigfaltigkeit und Einbettung |
| TP-C02 | C8 versus C4⊔C4 | Vollständige Reproduktion beider Polyeder |
| TP-C03 | T^4=I und det T=−1 | Dass eine beliebige Punktmenge unter T invariant ist |
| TP-C04 | Exakte Koplanarität versus Abweichung 10^-12 | Ein vollständiger Flächenschnitttest |
| SK-C01 | Speicherpuls, Maximum und Bilanz | Physikalische Sternzündung |
| SK-C02 | Einband-Entartung L und Staub | Gleichheit vollständiger Spektren |
| SK-C03 | Transformierter-Radius-Skalierung | Exakte Äquivalenz aller Atmosphärenmodelle |
| SK-C04 | Ranggewinn mit zwei bekannten Extinktionskoeffizienten | Identifizierbarkeit bei beliebig freier Temperatur und Hintergrund |
| SA-C01 | Stationäre Phase im definierten Wellenmodell | Stabilität, Wachstum oder Auswahl von m=6 |
| SA-C02 | Fourier-Rotationskovarianz | Dynamischer Mechanismus |
| SA-C03 | Modenausschluss durch Viertelkreis-Randbedingung | Verhalten eines vollen Planeten |
| SA-C04 | Aliasing von m=6 und m=18 auf zwölf Punkten | Physikalische Gleichheit der Moden |

Alle zwölf Gruppen wurden ausgeführt; zusammen mit den siebzehn Myonium-Gruppen sind es **29/29**. Die Checks verwenden eigene einfache Kontrollfälle und keine realen Beobachtungsdaten. Sie prüfen nicht den zukünftigen SCF-Produktionscode.

Für spätere Implementierungen gilt: algebraische Identität, exakte endliche Prüfung, numerische Näherung, Modellannahme und empirischer Befund getrennt speichern. Bei numerischen Fits Optimiererstatus und Parametergrenzen berichten. Endliche Scans nicht zu globalen Aussagen aufwerten. Quellen- und Lizenzstatus an tatsächlichen Artefakten prüfen; keine Medienabbildungen oder Drittanbieterprogramme ungeprüft übernehmen. Eigene Fixtures erlauben einen funktionsfähigen mathematischen Kern auch ohne Datenfreigabe.

## 7. Empfohlene Reihenfolge und Übergabe an Claude

1. **TP0–TP1:** kurze, sehr klare Demonstration von Beobachtungsfasern und fehlender Strukturinformation. Dies greift SCFs ursprüngliche Frage nach präziser Verwandtschaft unmittelbar auf.
2. **SK0–SK3:** der stärkste Anschluss an nichtstationäre Entwicklung. Das lineare Kontrollmodell schützt vor der vorschnellen Gleichsetzung eines Pulses mit notwendiger Nichtlinearität; der Messoperator schützt vor der Gleichsetzung von Helligkeit und innerem Zustand.
3. **SA0–SA2:** sauberer Einstieg in rotierende Wellen und Musterdiagnostik. SA3 ergänzt erst danach den Mechanismenvergleich.
4. **TP2–TP3, SK4 und SA4:** jeweils eigenständige Ausbauentscheidung nach Aufwand, Datenlage und tatsächlichem Bedarf. Ein vollständiger geometrischer Zertifizierer ist wesentlich anspruchsvoller als Euler-Arithmetik; dasselbe gilt für reale Stern- und Planetendynamik.

**Vorschlag für den nächsten begrenzten Auftrag:**

> Implementiere zunächst TP0–TP1 als kleinen epistemischen Pilot und SK0–SK3 als synthetischen Dynamik-versus-Beobachtung-Pilot. Prüfe aktuelle APIs und Repo-Anweisungen vorab, leite die Kontrollen selbst her und verwende vorhandene endliche Beobachtungsfasern sowie passende lineare Bausteine. Keine automatische Promotion des Turing-Review-Pakets zum Kern. Saturn zunächst mit SA0 dokumentieren; SA1–SA2 erst als eigenes, abgegrenztes Folgepaket. Die optionalen Real- und Geometriedatenzweige sind keine Voraussetzung für diese ersten mathematischen Ergebnisse.

Dieser Vorschlag ist bereit zur Auswahl durch Johann. Er erweitert SCFs Fähigkeiten an überprüfbaren Stellen, ohne aus einer thematischen Nähe bereits eine bestätigte gemeinsame Theorie zu machen.
