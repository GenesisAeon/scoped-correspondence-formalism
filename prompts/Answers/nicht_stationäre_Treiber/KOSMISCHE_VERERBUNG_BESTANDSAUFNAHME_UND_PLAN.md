# Kosmische Vererbung, chemische Anreicherung und SCF

**Bestandsaufnahme, unabhängige Kontrollen und Umsetzungsvorschlag für Johann / Claude-Code**  
Stand: 27. September 2026. Status: Review und Planung; keine Änderungen an den untersuchten Repositories.

## 1. Empfehlung

**Die vorhandenen Ansätze in Feldtheorie weiterentwickeln und gezielt an SCF anbinden. Ein zusätzliches Repository ist dafür derzeit nicht nötig.**

Die stärkste Verbindung zum angesprochenen JWST-Ergebnis ist die Weitergabe von Material zwischen Sternengenerationen: Produktion, Rückführung, Transport und erneute Nutzung chemischer Elemente. Dafür existiert mit `StellarLifecycle` und `TheChronicle` bereits eine anschauliche Vorlage. Ein kleiner wissenschaftlicher Pilot kann daraus nachvollziehbare Bilanzen und überprüfbare Vorhersagen entwickeln.

Die Vererbung von Modellparametern zwischen künstlichen Universen ist ein zweiter Forschungsstrang. Hier gibt es mit `UniverseDNA`, `MultiverseManager` und der bestehenden Roadmap SF-001 einen passenden Ausgangspunkt. Zunächst braucht dieser Strang einen fair budgetierten Vergleich von Vererbung, Mutation und Selektion. Eine kosmologische Interpretation folgt erst auf eine explizite physikalische Zuordnung.

SCF soll die gemeinsamen mathematischen Strukturen und die Grenzen der Schlussfolgerungen prüfen: verzögerte Rückführung, Vergröberung, Beobachtungsäquivalenz und Abhängigkeit einer Aussage von Annahmen. Die stellaren Ertragstabellen und die astrophysikalische Interpretation bleiben im Domänenprojekt.

Das entspricht Johanns Hinweis: Ein zusätzlicher Mechanismus kann das etablierte Bild ergänzen. Wissenschaftlich entscheidend ist, welche konkrete Aussage er zusätzlich ermöglicht und wie sich diese prüfen lässt.

## 2. Was tatsächlich untersucht wurde

Gezielte Suche in Repository-Bäumen und Quelltexten, Detaillektüre der relevanten Ausführungspfade, Primärquellenrecherche und kleine unabhängige Reproduktionen. Das ist **keine vollständige Zertifizierung aller sechs Repositories oder ihrer CI**. Bei den großen Sammlungen wurden die einschlägigen Teilbereiche geprüft.

| Repository | geprüfter Stand | Schwerpunkt |
|---|---|---|
| Feldtheorie | `2da5414c8a58ffbcf8a963c9b1f9a96202e3300a` | Stellar Forge, UniverseDNA, Materialkreislauf, Cosmic Loop, SF-001 |
| unified-mandala | `a76052842cbb9e6cb5ba70b36b1350feb35ad70a` | Universumsbäume, frühere Multiversums-Prototypen |
| universums-sim | `2f64548849d96fa6e83facb94463cb768733bf34` | Simulationsarchitektur, Zustände und Konfiguration |
| implosive-origin-utac | `cb073719e99700413e482945a6d2da8e8a19dfdc` | Type-6-ODE und behaupteter Fixpunkt |
| implosive-genesis | `39213d7b79f101365f7c796ace10b0bc15c6b85f` | benachbarte Type-6-/Chronologie-Ansätze |
| scoped-correspondence-formalism | Basisprüfung `9dde420561fc131c29c82f413081cfb2c60f4561`; abschließender Standabgleich `4a7ed38640ac7d393017eb5556291c879c3bceac` | mathematische Anschlüsse; neuer H-Review-Fix und ausgewählte Änderungen im Diff geprüft |

Die Existenz älterer Varianten im Mandala ist belegt. Eine vollständige historische Datierung der ersten Idee wurde nicht vorgenommen.

## 3. Die vorhandenen Ansätze sind verschieden

### 3.1 Stellar Forge: Parametervererbung und rekursive Ausführung

`UniverseDNA` bündelt Gravitation, Fusionsradius, Verdampfungs-/Entropieparameter und einen Parameter für die Glättung der Gravitation. `mutate()` verändert vier Werte multiplikativ; bei der Standardeinstellung liegt die Änderung zwischen −5 % und +5 %. Serialisierung und deterministische Token-Hashes sind vorhanden. [R1]

`MultiverseManager` startet Prozesse, liest Geburtssignale und erzeugt daraus mutierte Nachkommen. Das ist ein nutzbares Gerüst für Abstammung und Parametervariation. Der aktuelle Renderer setzt jedem Universum aber bereits ein Schwarzes Loch mit Masse 25 ein. Der Physikkern löst bei einer Masse über 20 ein Signal aus und erlaubt insgesamt nur ein Signal pro Universum. Die aktive `fusion_step()` bildet selbst keine Sterne oder Schwarzen Löcher. [R2]

**Erreichte Fähigkeit:** rekursive Ausführung mit Parameterweitergabe. **Noch offene Fähigkeit:** Unterschiedliche simulierte Bedingungen führen zu unterschiedlichem reproduktivem Erfolg durch tatsächlich modellierte Entstehung kompakter Objekte.

Daneben existiert ein anderer Stellar-Forge-Kern mit `atomic_kernel.py` und `universal_forces.py`. Er enthält zusätzliche Element- und Remnant-Klassen sowie eine vereinfachte H→He-Fusion. Er ist nicht identisch mit dem vom Multiverse-Renderer verwendeten Kern. Vorhandene Klassen für C, O oder Si sind für sich genommen noch keine implementierte Produktionskette dieser Elemente. [R3]

### 3.2 StellarLifecycle und Chronicle: materielle Weitergabe

`StellarLifecycle` verbraucht Ressourcen zur Geburt von Pop-III-/Pop-II-Agenten und gibt nach deren Ende Helium, Metalle und weitere Ressourcen an `TheChronicle` zurück. Herkunft und Ereignisse werden protokolliert. Das ist die direkteste vorhandene Verbindung zur chemischen Anreicherung. [R4]

Die gegenwärtigen Regeln sind jedoch illustrative Vorgaben: Lebensdauern von wenigen Ticks, feste Ertragsformeln, ein schwarzer Lochsamen bei jedem Pop-III-Ende und eine fest zugewiesene Pop-II-Metallizität von 0,15. Ressourcenstücke, angezeigte Sonnenmassen und Tickzeiten bilden noch kein einheitliches physikalisches Einheitensystem. Auch sind `METALS`, `HEAVY_METALS` und einzelne Elemente bisher verschiedene Ressourcenbezeichner ohne verbindliche chemische Bilanzdefinition.

`TheChronicle` bietet eine interessante Idee für Materialherkunft. Als globaler Singleton mit frei buchbaren Ressourcen ist es noch kein isolierter Massenbilanzkern. Sein Ereigniszähler darf insbesondere nicht als kosmische Zeit ausgelegt werden.

**Weiterverwendbar:** Ereignisprotokoll, Generationenbezug und Ressourcenfluss. **Zu entwickeln:** ein kleiner, separat testbarer physikalischer Rechenkern mit klaren Einheiten, Zustandsinstanzen, Erträgen und Rückführungszeiten.

### 3.3 Cosmic Loop: Vererbung eines Modell-Scores

`CosmicSeed` überträgt Generation, Vorfahren-ECM und Mutationsstärke. Der ECM-Wert beeinflusst eine vorgeschriebene Keimwahrscheinlichkeit und die Streuung neuer Parameter. Der Erfolg höherer ECM-Werte ist damit teilweise bereits in die Regeln eingebaut. [R5]

Das neue `G` wird jeweils um 1 herum gezogen; der konkrete Gravitationswert des Elternuniversums wird nicht als Zentrum der Mutation weitergegeben. Frühere Evolutionsstufen werden durch Wahrscheinlichkeitsregeln ersetzt. Der spätere Score stammt aus einem kleinen `HiveMind`-Versuch. Fehlversuche werden vom Endloslauf erneut versucht.

Das kann als künstlicher stochastischer Such- und Vererbungsprozess untersucht werden. Es liefert derzeit keine abgeleitete Beziehung zwischen kosmischer Chemie, Bewusstsein und Naturkonstanten. Ein sinnvoller Versuch muss festlegen, ob ein Fehlversuch Aussterben, Ressourcenverbrauch oder einen erlaubten Neustart bedeutet.

### 3.4 Mandala: frühere Universumsbäume

`sims/fractal_universe_tree.py` ist ausdrücklich ein Toy-Modell: Mutation eines Parameters, zufällige EVC-/CREP-Werte, eine vorgeschriebene Strafe für Entfernung vom Nullwert und anschließende Selektion. Die Breitenbegrenzung behält die ersten akzeptierten Kinder. Das kann eine Abhängigkeit von der Erzeugungsreihenfolge erzeugen. `--epi` und `--abundance` sind unbenutzte Platzhalter. [R6]

Damit ist der gedankliche Vorläufer tatsächlich vorhanden. Für neue Forschung sollte er als nachvollziehbarer Prototyp erhalten und mit dem SF-001-Versuch verglichen werden. Sein zufälliger Fitnessanteil eignet sich als Kontrollfall, nicht als astrophysikalische Messung.

Weitere einschlägig benannte Mandala-Dateien reichen von statischen Szenarienlisten bis zu einer einfachen Sinusentwicklung. Der gelesene Test `cosmo.bh.test.ts` enthält lediglich `expect(true).toBe(true)` und prüft daher die im Testnamen genannte Flächenrelation nicht. Namen allein sind hier kein Fähigkeitsnachweis.

### 3.5 Benachbarte Kosmologie-Repositories

`universums-sim` hat eine weiter ausgearbeitete Laufzeitarchitektur mit Konfiguration, Zeitschritten, Ereignissen und Zustandssnapshots. In den untersuchten Kernteilen wurde keine vergleichbare stellare Ertrags- oder Vererbungsbilanz gefunden. Ein späterer räumlicher Adapter ist denkbar; für einen ersten Reservoir-Piloten wäre die gesamte Laufzeit eine unnötig große Abhängigkeit. [R7]

`implosive-origin-utac` und `implosive-genesis` untersuchen andere mathematische Objekte: implosive Dynamik, Übergänge und kosmologische Deutungen. Eine gemeinsame Type-6-Bezeichnung stellt noch keine mathematische Identität ihrer Gleichungen her. Sie sollten als eigene Hypothesenstränge dokumentiert bleiben. Im erstgenannten Projekt wurde zudem ein konkreter analytischer Fehler bestätigt, siehe F7. [R8]

## 4. Konkrete Review-Befunde

Die Priorität bezeichnet die Bedeutung für den vorgeschlagenen Forschungsweg. P1 muss vor entsprechenden wissenschaftlichen Schlussfolgerungen geklärt werden; P2 betrifft experimentelle Belastbarkeit und Wartbarkeit. Bewusst vereinfachte Spielregeln sind als solche kein Softwarefehler.

| ID | Priorität / Art | Befund | Erforderlicher nächster Schritt |
|---|---|---|---|
| F1 | P1 / Aussagegrenze | Vorgegebenes Schwarzes Loch und höchstens ein Geburtssignal machen den Multiverse-Demopfad ungeeignet, Selektion nach Schwarzlochproduktion zu zeigen. | Demo explizit kennzeichnen; eigenes Reproduktionsmodell und Nullkontrollen für SF-001. |
| F2 | P1 / Parametervertrag | `fusion_threshold` und `entropy_rate` beeinflussen den geprüften aktiven Physikpfad nicht. Die managerweite Zufallsinitialisierung ist nicht reproduzierbar durchgereicht. | Aktive/inaktive Parameter ausweisen; Seed-Hierarchie bis in Mutation und Anfangszustände führen. |
| F3 | P1 / numerischer Bug | `gravity_step()` aktualisiert Positionen innerhalb der Kraftschleife. Spätere Teilchen sehen bereits veränderte Positionen. | Kräfte aus demselben alten Zustand bestimmen; anschließend alle Zustände aktualisieren. Impuls- und Permutationstest. |
| F4 | P2 / Schnittstellenbruch | `cosmic_cycle_demo` importiert nicht mehr vorhandene freie Funktionen; `run_multiverse` ruft beim Abbruch ein fehlendes `terminate_all()` auf. | Unterstützte Ausführungspfade festlegen, Demo reparieren oder begründet stilllegen; sauberer Prozessabbau. |
| F5 | P1 / physikalischer Scope | Ressourcen-, Lebensdauer- und Ertragsregeln von StellarLifecycle sind illustrative Vorgaben ohne geschlossene physikalische Bilanz. | Separate Einheiten- und Ertragsverträge; Toy-Ausgabe nicht als Anreicherungsvorhersage verwenden. |
| F6 | P2 / Versuchsbedeutung | Cosmic Loop vererbt Score/Variationsbreite, nicht durchgängig die Elternparameter; wiederholtes Keimen verändert die Bedeutung von Überleben. | Vererbungsoperator und Stichprobenauswahl präzisieren; Neustarts und Aussterben getrennt erfassen. |
| F7 | P1 / analytischer Bug, benachbartes Repo | Type-6-`fixed_point()` ist keine Nullstelle der implementierten ODE. | Mathematisches Modell entscheiden; Fixpunkt, Integrator, Übergang und E-Faltungs-Begriff gemeinsam korrigieren. |
| F8 | P2 / Kontrollmodell | Mandala-Fitness enthält Zufallsplatzhalter; die Breitenbegrenzung folgt der Listenreihenfolge. | Als historischen Kontrollfall bewahren; für neue Versuche faire Auswahl und externe Auswertung. |

### 4.1 Unabhängig ausgeführte Kontrollen

Das beigefügte `reproduce_review.py` verwendet die unveränderten Quellmodule. Es lädt den relevanten Unterpaketpfad isoliert; die fachfremden, sofortigen Importe im übergeordneten `simulation/__init__.py` werden dabei nicht ausgeführt. Dies ist ein Modultest, kein Test der vollständigen Paketinitialisierung. Signale werden ausschließlich in temporären Verzeichnissen erzeugt. Es startet keine Kindprozesse und keinen unbeschränkten Renderer.

- **Vorhandene Tests:** Alle fünf fixturefreien Funktionen aus `tests/test_universe_dna.py` direkt ausgeführt; bestanden. `pytest` war in dieser Laufzeit nicht installiert. Es wird kein vollständiger Pytest-/Repository-Lauf behauptet.
- **Geburtssignale:** Kein schwarzes Loch → 0 Signale; ein schwarzes Loch → 1; zwei schwarze Löcher → weiterhin 1. Auch ein zweiter Aufruf erzeugt keinen weiteren Nachkommen. Der echte Initialisierer enthält einen vorgegebenen schwarzen Lochagenten mit Masse 25.
- **Parameterwirkung:** Änderung von Fusionsradius 0,5→20 und Entropierate 0,001→0,7 ergibt für den geprüften Zwei-Teilchen-Pfad über fünf Schritte bit-identische Zustände. Änderung von `gravity_const` verändert sie als Positivkontrolle.
- **Gravitation:** Zwei gleiche Teilchen bei x=−1 und x=+1, anfangs in Ruhe: Nach einem Schritt beträgt der Gesamtimpuls −0,00015595164086283989 in den Modelleinhheiten. Umkehr der Listenreihenfolge ergibt das entgegengesetzte Vorzeichen. Das Ergebnis darf physikalisch nicht von dieser Reihenfolge abhängen.
- **Import:** `cosmic_cycle_demo` scheitert am fehlenden `accretion_step`; der Fehler wurde ausgeführt und nicht nur aus dem Dateinamen vermutet.
- **Abbruchvertrag:** `MultiverseManager` besitzt kein `terminate_all`, obwohl der neue Einstiegspunkt es aufruft. Der unbeschränkte Managerlauf selbst wurde nicht gestartet.
- **Type-6:** Der behauptete Fixpunkt hat eine deutlich positive Ableitung; die numerische Entwicklung nähert sich stattdessen dem analytisch richtigen positiven Fixpunkt.

Diese Bestätigungen sind **Nachweise der Befunde**, keine bestandenen Release-Tests für das fehlerhafte Verhalten. Bei einer Reparatur müssen die Fehler-Reproduktionen durch Tests der korrigierten Invarianten ergänzt bzw. ersetzt werden.

### 4.2 Der Type-6-Fehler exakt

Für H>0 implementiert der Code

\[
\dot H=-rH\left(1-\frac{K_{\min}}{H}\right)\tanh(\sigma\gamma)
       =-a(H-K_{\min}),\quad a=r\tanh(\sigma\gamma).
\]

Bei a>0 ist der positive stabile Fixpunkt **H*=K_min**. Die exakte Lösung lautet

\[
H(t)=K_{\min}+(H(0)-K_{\min})e^{-at}.
\]

`fixed_point()` liefert dagegen `K_min*tanh(sigma*gamma)`. Mit den Standardwerten:

| Größe | Wert |
|---|---:|
| wahrer positiver Fixpunkt | 0,01 |
| Rückgabe von `fixed_point()` | 0,00019310099346675974 |
| Ableitung an dieser Rückgabe | +0,00018937219409897478 |
| numerisches H bei t=1000 | 0,010000003992621851 |
| exaktes H bei t=1000 | 0,010000004067856305 |
| `at_fixed_point` am numerischen Endpunkt | false |

Zusätzlich nennt der Klassen-Docstring die andere Gleichung mit `(1-H/K_min)`. Für positive a und H>K_min hätte diese ein anderes Vorzeichen und würde dort wachsen. Es genügt daher nicht, nur eine Zahl im Test zu ändern. Eine separat postulierte Zündschwelle darf unterhalb des Fixpunkts liegen; der aktuelle positive Relaxationspfad erreicht sie von oben aber nicht. Auch `ln(H0/H*)` ist ohne Zusammenhang zwischen H, Zeit und Skalenfaktor keine hergeleitete Zahl kosmologischer E-Faltungen.

## 5. Wissenschaftliche Einordnung des JWST-Anschlusses

Zhu et al. berichten Metallabsorption um drei helle Galaxien bei z≈7,2–9,3. Die Arbeit beschreibt frühe Anreicherung und bewegtes Gas; sie stellt ausdrücklich fest, dass Modelle raschen Beginn solcher Prozesse erwarten. Das Ergebnis ist mit frühem Baryonenrecycling vereinbar. Eine eindeutige Beschleunigungsgeometrie oder universumsweite homogene Anreicherung folgt daraus nicht. Die gemessenen Ionenlinien sind außerdem kein unmittelbarer Messwert der mittleren Metallizität eines ganzen Gasreservoirs. [P1]

Die frühere Aussage im zitierten Chat, das Paper widerspreche einfach den Standard-Anreicherungsmodellen, ist deshalb zu stark. Ein guter eigener Beitrag wäre eine genauere Untersuchung von Rückführungszeiten, unvollständiger Mischung und Beobachtbarkeit innerhalb etablierter Stern- und Galaxienphysik.

### 5.1 Konkrete wissenschaftliche Bausteine

| Primärquelle / Werkzeug | Nutzen für den vorgeschlagenen Pilot | Begrenzung |
|---|---|---|
| SYGMA / NuPyCEE, Ritter et al. [P2] | Zeitabhängige Rückgabe von Sternpopulationen, Erträge, Abhängigkeit von Massenfunktion und Metallizität. | Verfügbare Tabellenbereiche und Ertragskonventionen einzeln prüfen. |
| OMEGA / NuPyCEE [P3] | Referenz für chemische Entwicklung einer gemischten Zone. | Ein Zonenmittel beschreibt keine räumliche Metallverteilung. |
| Weinberg, Andrews & Freudenburg [P4] | Analytische chemische Entwicklungsmodelle und verzögerte Beiträge als unabhängige Kontrollfälle. | Modellannahmen des jeweiligen Kontrollfalls explizit übernehmen. |
| Heger & Woosley, metallfreie Sterne [P5] | Pop-III-spezifische Ertrags- und Remnant-Szenarien für 10–100 Sonnenmassen. | Keine pauschale Extrapolation auf andere Massen, Rotationen oder Explosionsmodelle. |
| Sarmento, Scannapieco & Côté [P6] | Rolle unaufgelöster Mischung und unbekannter Pop-III-Eigenschaften. | Anregung für einen kleinen Versuch; eine kosmologische Simulation wird dadurch nicht ersetzt. |
| Woosley & Heger, Paarinstabilität [P7] | Kontrollbeispiel: Metallausstoß und Schwarzlochbildung sind nicht allgemein monoton gekoppelt. | Sternentwicklung und Remnantbildung benötigen getrennte Annahmen. |
| Smolins ursprüngliche CNS-Hypothese [P8] | Präzise historische Hypothese zur Selektion kosmischer Parameter durch Reproduktion. | Der Reproduktionsmechanismus und die kosmologische Deutung sind nicht durch den JWST-Befund bestätigt. |

NuPyCEE ist ein sinnvoller Referenzkandidat. Es wurde für diesen Review nicht installiert oder als Abhängigkeit eingeführt. Vor einer Integration sind API, konkrete Tabellen, Versionsbindung und die Rechte am jeweils genutzten Datenbestand separat zu prüfen. Die Lizenz eines Software-Repositories beantwortet nicht automatisch alle Fragen zu extern zugeladenen Ertragstabellen.

### 5.2 Drei getrennte Bedeutungen von Vererbung

1. **Materielle Weitergabe:** Spätere Sterne entstehen aus zuvor verändertem Gas. Das ist ein physikalisch anschlussfähiger Stoffkreislauf.
2. **Vererbung in künstlichen Modellpopulationen:** Elternparameter beeinflussen die Parameter ihrer Nachkommen. Diese mathematische Eigenschaft lässt sich unmittelbar in Simulationen prüfen.
3. **Kosmologische Vererbung:** Schwarze Löcher erzeugen Nachfolgeuniversen mit veränderten Naturparametern. Dafür braucht es zusätzliche physikalische Annahmen und unterscheidbare Konsequenzen.

Smolins Hypothese wird nicht dadurch getestet, dass eine Simulation Nachkommen nach einer selbst gewählten Schwarzloch-Fitness bevorzugt. Der Versuch muss zunächst zeigen, was seine Regeln tatsächlich implizieren. Für den nächsten physikalischen Schritt wären dimensionslose Parameter wie α oder Gm_p²/(ℏc) sinnvoller als die isolierte Änderung eines dimensionsbehafteten G ohne Erklärung, welche übrigen Größen fest bleiben.

Ein hoher Metallausstoß ist zudem kein allgemeiner Ersatzindikator für viele Schwarze Löcher. Vollständige Sternzerstörung kann Metalle auswerfen, ohne einen schwarzen Lochrest zu hinterlassen; andere Endzustände binden Material. Deshalb sind Metallproduktion, Remnantzahl, Remnantmasse und Rückführung getrennte Zielgrößen. [P5, P7]

## 6. Der aussichtsreichste neue Pilot

**Arbeitstitel: „Chemische Weitergabe, Mischung und Beobachtbarkeit“**. Er gehört als kleines Forschungsexperiment nach Feldtheorie, mit einer späteren SCF-Auswertung.

Die Frage lautet: **Welche Informationen über vergangene Sternengenerationen bleiben in späteren Gaszuständen erhalten, und welche davon können konkrete Messungen unterscheiden?**

### 6.1 Minimaler physikalischer Kern

Gasmasse M_g, Sternbildungsrate ψ, Zufluss I, Abfluss O und gesamte Rückgabe E werden in konsistenten Einheiten geführt, beispielsweise Sonnenmassen und Myr:

\[
\dot M_g=I-\psi+E-O.
\]

Für Element i mit Gasmassenanteil Z_i:

\[
\frac{d(M_gZ_i)}{dt}=Z_{i,\mathrm{in}}I-Z_i\psi+E_i-Z_{i,\mathrm{out}}O.
\]

E_i bezeichnet hier **die gesamte zurückgegebene Masse des Elements**, einschließlich bereits bei der Sternbildung vorhandenen Materials. Netto neu synthetisierte Erträge müssen bei der Einlesung davon unterschieden werden. Sonst entsteht leicht eine Doppelzählung.

Ein zeitabhängiger Rückgabekern kann schematisch als

\[
E_i(t)=\int_0^t\psi(t-\tau)\,k_i(\tau,Z_{\mathrm{birth}}(t-\tau))\,d\tau
\]

geschrieben werden. Der Kern hat die Einheit zurückgegebene Elementmasse pro gebildeter Sternmasse und Zeit. Physikalische Tabellen dürfen Metallizitätsabhängigkeit besitzen; dann ist das Gesamtsystem nicht einfach eine zeitinvariante lineare Faltung.

Zunächst wird eine wohlgemischte Zone als Kontrollfall gerechnet. Erst danach folgen getrennte Reservoire für sternbildendes Gas und umgebendes Gas sowie endliche Transport-/Mischungszeiten. H, He, C, O und Si sind eine sinnvolle erste Auswahl, ergänzt um eine explizite Restkategorie für nicht einzeln verfolgte Masse. Sternmasse, Remnants und ausgetragenes Material gehören zur Gesamtbilanz. Nukleare Massendefekte können im ersten Umfang als dokumentierte baryonische Massenapproximation behandelt werden.

Die erste auswertbare Erweiterung ist **Materialherkunft als mitgeführte Bilanz**: Welcher Anteil des Elements stammt aus welcher Generation, welchem Ertragsmodell und welchem Rückführungskanal? Solche Markierungen schaffen keine neue Physik; sie machen die Abhängigkeit einer Vorhersage prüfbar.

### 6.2 Besonders gut passende SCF-Frage: Mittelwert versus Verteilung

Zwei gleich große Gaspakete mit Metallizitäten 0 und 0,02 besitzen dieselbe mittlere Metallizität 0,01 wie zwei Pakete mit jeweils 0,01. Ihr Anteil unberührten Gases unterscheidet sich jedoch: 50 % gegenüber 0 %.

Eine Beobachtung, die ausschließlich den Mittelwert erfasst, kann diese Zustände nicht unterscheiden. Wenn spätere Sternbildung lokal auf Metallizität reagiert, kann ihre weitere Entwicklung trotzdem verschieden sein. Genau hier greifen Beobachtungsfasern und die Prüfung, ob ein makroskopischer Zustand für die Dynamik ausreicht.

Das ist eine präzise neue Arbeitsfrage im Sinne von SCF: **Reicht ein mittlerer Metallgehalt aus, oder braucht die Vorhersage zusätzlich einen unberührten Gasanteil, eine Verteilung oder ein Gedächtnis?** Sie passt unmittelbar zu Johanns Skepsis gegenüber pauschaler Homogenität. Sie setzt dabei voraus, dass die heterogene Erweiterung ihren Nutzen gegenüber dem einfachen Kontrollmodell tatsächlich zeigt.

### 6.3 Messmodell und tatsächlicher Neuigkeitswert

Für einen späteren Spektralvergleich wird ein Beobachtungsmodell benötigt: Elementmenge → Ionisation und Sichtliniengeometrie → Säulendichte bzw. Linienprofil → Instrument und Messfehler. Ein chemischer Reservoirwert darf nicht unmittelbar einer Absorptionslinien-Stärke gleichgesetzt werden.

Der mögliche eigene Beitrag liegt in der Verbindung von Herkunftsbilanz, verzögerter Weitergabe, heterogener Mischung und der Frage, welche Hypothesen beobachtbar auseinanderliegen. Ein weiterer Einzonen-Ertragsrechner allein wäre angesichts bestehender Werkzeuge wenig neu.

## 7. Der getrennte Vererbungsversuch

Die vorhandene Feldtheorie-Roadmap beschreibt SF-001 sowie S00/S01 bereits sehr passend: gleiches Budget je Modell, begrenzte Gesamtpopulation, neutrale Verzweigung, Selektion und Mutation getrennt, unabhängige Erfolgskriterien. Genau dort sollte die Arbeit fortgesetzt werden. [R9]

Für einen ersten exakten Kontrollfall seien M_ji die Wahrscheinlichkeit für einen Nachkommen des Typs j bei Eltern des Typs i und b_i die mittlere Nachkommenzahl. M ist spaltenstochastisch. Dann gilt für erwartete Populationsgrößen im entsprechenden unabhängigen Verzweigungsmodell:

\[
n_{g+1}=M\,\mathrm{diag}(b)\,n_g.
\]

Die deterministische Frequenzrekursion lautet bei positivem Nenner

\[
p_{g+1}=\frac{M\,\mathrm{diag}(b)p_g}{\mathbf1^\top\mathrm{diag}(b)p_g}.
\]

Für endliche zufällige Populationen ist diese normalisierte Rekursion nicht ohne Weiteres gleich dem Erwartungswert der zufälligen Frequenzen. Aussterben und Populationsbegrenzung brauchen eigene Regeln.

**Vorab festgelegte Kontrollfälle:**

- M=I und b=(1,1): Zusammensetzung bleibt im deterministischen Kontrollfall unverändert.
- M=I, b=(1,2), n₀=(1,1): n₂=(1,4), p₂=(0,2; 0,8).
- M=π1ᵀ: Die nächste Typverteilung ist π, unabhängig vom Elterntyp. Das ist eine Kontrolle mit vollständig gelöschter Typvererbung, während b weiterhin die Gesamtgröße beeinflussen kann.
- Alle b_i=0: Aussterben; keine Normalisierung durch null und keine scheinbare stationäre Population.
- Dieselben physikalischen Startzustände in anderer Listen-/Prozessreihenfolge: identische deterministische Resultate bzw. dieselbe klar definierte Verteilung.

Der Kontrollversuch muss zunächst mit einer ausdrücklich künstlichen Reproduktionsregel auskommen können. Eine Schwarzloch-Fitness ist erst zulässig, wenn ihre Erzeugung und Abhängigkeit von Parametern im gewählten physikalischen Modell definiert sind. Eine Beschriftung als Schwarzes Loch ersetzt das nicht.

## 8. Was genau nach SCF gehört

| Fragestellung | Vorhandener SCF-Anschluss | Neue Arbeit |
|---|---|---|
| Stoffrückgabe und Transport | `dynamics/linear_reservoirs.py` | Referenzfälle und Einheitenmapping; nicht jede metallizitätsabhängige Dynamik ist linear. |
| Verteilte Rückführungszeiten | `dynamics/phase_type_delays.py` | Näherungsfehler gegenüber einem festgelegten Rückgabekern; physikalische Kalibrierung separat. |
| Weggelassene Reservoirzustände | `closure/linear_memory_projection.py` | Exakter linearer Kontrollfall vor nichtlinearer Anwendung. |
| Genügt eine makroskopische Klassifikation? | `correspondence/controlled_markov.py` | Diskretes Mikro-/Makrobeispiel mit klarer Partition. |
| Unterscheidbare Vorgeschichten | `epistemic/observation_fibers.py` | Endliche Gegenmodelle und dokumentierter Beobachtungsoperator. |
| Welche Annahmen tragen eine Aussage? | `epistemic/finite.py`, `supports.py`, `adapters.py` | Domänenbericht mit sauberem empirischem Status. |
| Mutation und differentielle Reproduktion | vorhandene Operator-/Markov-Strukturen als Vergleich | Kleiner allgemeiner Operator, falls nach API-Prüfung tatsächlich eine Lücke bleibt. |

Konventionsgrenze: Der oben definierte M ist spaltenstochastisch. Die bestehenden Markov-APIs dürfen nicht ungeprüft dieselbe Orientierung erhalten. Reproduktion macht M diag(b) im Allgemeinen außerdem zu einem nichtstochastischen positiven Operator; die normalisierte Frequenzabbildung ist dann nicht einfach eine feste Markov-Matrix.

**Aktualisierung beim abschließenden Standabgleich:** SCF steht inzwischen auf `4a7ed38`. Der darin enthaltene Commit `6b1945d` adressiert ausdrücklich die acht Befunde des vorausgehenden H0–H7-Reviews. Im gelesenen Diff sind unter anderem separate Zeugenflags, strikte Bool-Prädikate, dreistufige Löschentscheidungen und die Behandlung nichtendlicher Adapterresiduen als unvollständige Auswertung vorhanden. Die früheren Befunde werden deshalb hier nicht pauschal weiter als offen geführt. Eine vollständige unabhängige Abnahme dieses neuen Fix-Commits war nicht Gegenstand dieses Reviews. Der neue Domänenadapter soll auf einem festgelegten aktuellen SCF-Stand aufsetzen und seine konkreten Fehler-/Budget-/Zeugenfälle selbst prüfen. [R11]

## 9. Warum JWST allein kosmologische Vererbung nicht identifiziert

Sei θ der Satz physikalischer Parameter und η die lokalen astrophysikalischen Bedingungen. Wenn eine Vererbungshypothese nur erklärt, warum θ entstanden sein könnte, aber bei festem θ und η dieselbe Galaxienphysik verwendet, gilt innerhalb dieses Vergleichs:

\[
P(D\mid\theta,\eta,H_{\mathrm{CNS}})
=P(D\mid\theta,\eta,H_{\mathrm{Referenz}}).
\]

Das ist eine **bedingte** Beobachtungsäquivalenz, keine Behauptung, dass alle denkbaren Versionen kosmologischer Vererbung unprüfbar wären. Eine Theorie könnte eine andere, quantitativ begründete Verteilung für θ vorhersagen. Dann wäre eine marginale Vorhersage

\[
P(D\mid H)=\int P(D\mid\theta,\eta,H)\,\pi_H(\theta,\eta)\,d\theta\,d\eta
\]

zu vergleichen. Dafür braucht es eine spezifizierte Verteilung, eine Auswahlregel und unabhängige Kontrollen. Viele Galaxien in unserem Universum sind keine unabhängige Stichprobe vieler Universen mit jeweils neuen Naturkonstanten.

Da der JWST-Befund bereits bekannt ist und die Idee mit angestoßen hat, wäre ein daran entwickelter Vergleich zunächst explorativ bzw. retrospektiv. Ein späterer echter Vorhersagetest braucht eingefrorene Regeln und neue oder zuvor nicht verwendete Beobachtungen. Das sollte im Ergebnisbericht ausdrücklich stehen.

## 10. Arbeitspakete für Claude-Code

Diese Pakete konkretisieren die Empfehlung. Sie sind noch nicht implementiert. Bestehende lokale AGENTS-/Provenienzregeln gelten bei späteren Repository-Änderungen; die folgende Planung erteilt keinen Auftrag zum eigenständigen Push in dieser Review-Sitzung.

| Paket | Ort und Inhalt | Abnahme |
|---|---|---|
| V0 – Bestand verbindlich machen | Feldtheorie: vorhandene SF-001-Roadmap um die Befunde und die beiden Stränge ergänzen; unterstützte Einstiegspunkte, Einheiten und aktive Parameter benennen. | Jede Aussage hat Quellpfad, Status und überprüfbaren nächsten Schritt; kein zweites konkurrierendes Roadmap-System. |
| V1 – Rechenkern und Laufverträge reparieren | Feldtheorie: F2–F4; gemeinsame Zustandsbasis der Kräfte, reproduzierbare Seeds, eindeutige Kind-IDs, begrenzte Gesamtläufe und sauberer Abbruch. Type-6-F7 separat im zugehörigen Repo. | Permutations-/Impulstest, Wiederholbarkeit, Parameter-Positivkontrollen, Import- und Abbruchtest; Type-6-Nullstelle analytisch geprüft. |
| V2 – S00/S01 durchführen | Feldtheorie: kleiner CPU-Versuch für neutrale, selektive und mutationsbehaftete Modellpopulationen; Renderer optional. | Exakte Handfälle aus §7, faire Budgets, explizite Aussterberegel, mehrere Seeds und unabhängige Auswertung. |
| V3 – Chemischen Basiskern bauen | Feldtheorie: instanzbasierte Gas-/Stern-/Remnantbilanz, zunächst synthetische Erträge, vollständige Herkunftsmarkierungen. | Bilanzerhalt, Nichtnegativität, Einheitenumrechnung, keine Rückgabe vor der definierten Lebensdauer. |
| V4 – Physikalische Referenzen anbinden | Feldtheorie: versionierter Ertragstabellenadapter oder schlanker Referenzvergleich mit SYGMA/OMEGA; Pop-III-Gültigkeit explizit. | Manifest, Tabellenbereich, Netto-/Gesamtertragskonvention, Interpolation und belegte Nutzungsbedingungen; fehlende Daten führen zu `not_evaluated`. |
| V5 – Mischung und Beobachtbarkeit | Feldtheorie mit kleinem SCF-Kontrollfall: ein vs. zwei Reservoire; Mittelwert vs. unberührter Anteil; verzögerte Rückführung. | Exakte Degenerationskontrolle aus §6.2, Kausalität, Bilanz, zeitliche Auflösungsprüfung und begrenzte Aussage zur Identifizierbarkeit. |
| V6 – Beobachtungsanschluss | Zuerst synthetische Messdaten, danach ein eng begrenzter realer Pilot mit passendem Messmodell und Auswahlfunktion. | Keine Gleichsetzung von Gesamtmetallizität und Ionenlinien; Unsicherheit, Gegenmodelle und explorativer Status transparent. |
| V7 – SCF-Bericht und Entscheidung | SCF-Adapter auf dem aktuellen Stand einschließlich H-Review-Fix; zusammenfassender Fähigkeitsbericht. | Adapterfälle unabhängig geprüft; mathematischer Befund, angenommene Physik, Simulation und reale Evidenz getrennt; zusätzliche Komplexität nur bei nachgewiesenem Nutzen. |

**Praktische Reihenfolge:** V0 → V1 → V2 und V3; anschließend hat V4/V5 für den aktuellen JWST-Anlass Vorrang. V6 folgt nur, wenn ein ehrlicher Beobachtungsvergleich möglich ist. V7 verwendet den dann tatsächlich erreichten Stand.

### 10.1 Unabhängige Orakel für den chemischen Kern

1. Geschlossenes System ohne Sternbildung: alle Bestände konstant.
2. Geschlossenes System mit Umlagerung: Gas + Sterne + Remnants + gegebenenfalls explizit ausgetragenes Material erfüllen die deklarierte Gesamtbilanz.
3. Ein Sternpuls mit festem Rückgabezeitpunkt: vorher exakt keine Rückgabe, danach genau die festgelegte Masse.
4. Klassisches geschlossenes, wohlgemischtes Modell mit instantaner Rückgabe, konstantem Nettoertrag y pro dauerhaft gebundener Sternmasse und Startmetallizität Z₀:
   \[Z=Z_0+y\ln(M_{g,0}/M_g).\]
   Ertragsdefinition und Voraussetzungen gehören zum Test; die Formel darf nicht unbesehen auf verzögerte Rückgabe übertragen werden.
5. Gleiche mittlere Metallizität bei verschiedener lokaler Verteilung: Beobachtungsäquivalenz des Mittelwerts und Unterschied beim unberührten Anteil exakt nachweisen.
6. Ein linearer Zwei-Reservoir-Fall gegen Matrixexponential oder eine unabhängige geschlossene Lösung; nicht zwei Aufrufe desselben Integrators gegeneinander testen.
7. Gleicher physikalischer Versuch in Myr und Jahren: nach Rückumrechnung gleiche Vorhersage innerhalb deklarierter Toleranz.

### 10.2 Ergebnisformat

Ein Laufbericht sollte mindestens Commit, Konfiguration, Seed-Hierarchie, Einheiten, Ertragsquellen, initiale Bestände, Bilanzfehler, Zeitauflösung, Beobachtungsoperator, betrachtete Alternativen und die tatsächlich geprüfte Aussage enthalten. Zustände wie `evaluated`, `not_evaluated`, `numerical_failure` und `outside_scope` müssen unterscheidbar bleiben. Eine fehlende Auswertung ist kein negativer Befund über die physikalische Hypothese.

## 11. Quellen und prüfbare Pfade

### Repository-Quellen

- **R1:** [UniverseDNA](https://github.com/GenesisAeon/Feldtheorie/blob/2da5414c8a58ffbcf8a963c9b1f9a96202e3300a/simulation/v4_stellar_forge/universe_dna.py), [vorhandene DNA-Tests](https://github.com/GenesisAeon/Feldtheorie/blob/2da5414c8a58ffbcf8a963c9b1f9a96202e3300a/tests/test_universe_dna.py).
- **R2:** [MultiverseManager](https://github.com/GenesisAeon/Feldtheorie/blob/2da5414c8a58ffbcf8a963c9b1f9a96202e3300a/simulation/v4_stellar_forge/multiverse_manager.py), [Renderer](https://github.com/GenesisAeon/Feldtheorie/blob/2da5414c8a58ffbcf8a963c9b1f9a96202e3300a/simulation/v4_stellar_forge/big_bang_renderer.py), [aktiver Physikkern](https://github.com/GenesisAeon/Feldtheorie/blob/2da5414c8a58ffbcf8a963c9b1f9a96202e3300a/simulation/v4_stellar_forge/physics_engine.py), [Cosmic-Cycle-Demo](https://github.com/GenesisAeon/Feldtheorie/blob/2da5414c8a58ffbcf8a963c9b1f9a96202e3300a/simulation/v4_stellar_forge/cosmic_cycle_demo.py), [Manager-Einstiegspunkt](https://github.com/GenesisAeon/Feldtheorie/blob/2da5414c8a58ffbcf8a963c9b1f9a96202e3300a/simulation/v4_stellar_forge/run_multiverse.py).
- **R3:** [atomarer Kern](https://github.com/GenesisAeon/Feldtheorie/blob/2da5414c8a58ffbcf8a963c9b1f9a96202e3300a/simulation/v4_stellar_forge/atomic_kernel.py), [Universal Forces](https://github.com/GenesisAeon/Feldtheorie/blob/2da5414c8a58ffbcf8a963c9b1f9a96202e3300a/simulation/v4_stellar_forge/universal_forces.py).
- **R4:** [StellarLifecycle](https://github.com/GenesisAeon/Feldtheorie/blob/2da5414c8a58ffbcf8a963c9b1f9a96202e3300a/src/scenarios/level_2_stellar/stellar_lifecycle.py), [Chronicle](https://github.com/GenesisAeon/Feldtheorie/blob/2da5414c8a58ffbcf8a963c9b1f9a96202e3300a/src/core/chronicle.py), [weiterer Generationen-Prototyp](https://github.com/GenesisAeon/Feldtheorie/blob/2da5414c8a58ffbcf8a963c9b1f9a96202e3300a/src/scenarios/level_3_galactic/stellar_death.py).
- **R5:** [CosmicSeed und UniverseRunner](https://github.com/GenesisAeon/Feldtheorie/blob/2da5414c8a58ffbcf8a963c9b1f9a96202e3300a/src/scenarios/level_7_cosmic_loop/cosmic_physics.py), [Generationenlauf](https://github.com/GenesisAeon/Feldtheorie/blob/2da5414c8a58ffbcf8a963c9b1f9a96202e3300a/src/scenarios/level_7_cosmic_loop/run_eternal_cycle.py).
- **R6:** [Mandala-Universumsbaum](https://github.com/GenesisAeon/unified-mandala/blob/a76052842cbb9e6cb5ba70b36b1350feb35ad70a/sims/fractal_universe_tree.py), [BH-Testplatzhalter](https://github.com/GenesisAeon/unified-mandala/blob/a76052842cbb9e6cb5ba70b36b1350feb35ad70a/tests/unit/cosmo.bh.test.ts).
- **R7:** [universums-sim Kern](https://github.com/GenesisAeon/universums-sim/blob/2f64548849d96fa6e83facb94463cb768733bf34/src/universums_sim/simulation/core.py).
- **R8:** [Type-6-ODE](https://github.com/GenesisAeon/implosive-origin-utac/blob/cb073719e99700413e482945a6d2da8e8a19dfdc/src/implosive_origin/type6_ode.py), [anderer Type-6-Ansatz](https://github.com/GenesisAeon/implosive-genesis/blob/39213d7b79f101365f7c796ace10b0bc15c6b85f/src/implosive_genesis/core/type6.py).
- **R9:** [Feldtheorie-Forschungsroadmap, insbesondere Abschnitt 9 und S00/S01](https://github.com/GenesisAeon/Feldtheorie/blob/2da5414c8a58ffbcf8a963c9b1f9a96202e3300a/experiments/research_roadmap_2026/ROADMAP.md).
- **R10:** [SCF am geprüften Stand](https://github.com/GenesisAeon/scoped-correspondence-formalism/tree/9dde420561fc131c29c82f413081cfb2c60f4561/src/scoped_correspondence). Die in §8 angegebenen relativen Modulpfade beziehen sich darauf.
- **R11:** [SCF-Fix-Commit zum H-Review](https://github.com/GenesisAeon/scoped-correspondence-formalism/commit/6b1945d7ce3d2e8c766578eafc3efd03c864bd9c), [aktueller Stand beim abschließenden Abgleich](https://github.com/GenesisAeon/scoped-correspondence-formalism/tree/4a7ed38640ac7d393017eb5556291c879c3bceac).

### Wissenschaftliche Primärquellen

- **P1:** Zhu et al. (2026), *Early metal-enriched baryon cycling before the midpoint of cosmic reionization*, Nature Astronomy, veröffentlicht 24.09.2026. [DOI/Volltext](https://www.nature.com/articles/s41550-026-02988-2). Die dort angegebenen Daten-/Codeverweise sind Ausgangspunkte einer späteren Provenienzprüfung; sie wurden hier nicht als Datensatz eingebunden.
- **P2:** Ritter et al. (2018), *SYGMA: Stellar Yields for Galactic Modeling Applications*. [Preprint](https://arxiv.org/abs/1711.09172), [Projektdokumentation](https://nugrid.github.io/NuPyCEE/sygma.html).
- **P3:** NuGrid, [NuPyCEE-Übersicht](https://nugrid.github.io/NuPyCEE/overview.html), [OMEGA](https://nugrid.github.io/NuPyCEE/omega.html), [Quellcode](https://github.com/NuGrid/NuPyCEE).
- **P4:** Weinberg, Andrews & Freudenburg (2017), *Equilibrium and Sudden Events in Chemical Evolution*. [Preprint](https://arxiv.org/abs/1604.07435).
- **P5:** Heger & Woosley (2010), *Nucleosynthesis and Evolution of Massive Metal-Free Stars*. [Preprint](https://arxiv.org/abs/0803.3161).
- **P6:** Sarmento, Scannapieco & Côté (2019), *Following the Cosmic Evolution of Pristine Gas III: The Observational Consequences of the Unknown Properties of Population III Stars*. [Preprint](https://arxiv.org/abs/1901.03727).
- **P7:** Woosley & Heger (2021), *The Pair-Instability Mass Gap for Black Holes*. [Preprint](https://arxiv.org/abs/2103.07933).
- **P8:** Smolin (1994), *The fate of black hole singularities and the parameters of the standard models of particle physics and cosmology*. [Originalarbeit](https://arxiv.org/abs/gr-qc/9404011).

## 12. Beilagen und Reichweite

Das Reproduktionspaket enthält dieses Dokument, `reproduce_review.py`, die tatsächlich erzeugten `findings.json`, geprüfte Commitstände, ein Dateimanifest und eine Ausführungsanleitung. Die Original-Repositories und astronomischen Rohdaten werden nicht mitgeliefert.

Die Reproduktionen bestätigen konkrete Codeeigenschaften und mathematische Inkonsistenzen. Sie messen keine kosmische Selektion und passen keine JWST-Daten an. Die Arbeitspakete zeigen, wie aus den vorhandenen Ideen schrittweise überprüfbare Aussagen entstehen können.
