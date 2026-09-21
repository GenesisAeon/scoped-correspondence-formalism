# Scoped Correspondence Formalism – erneute wissenschaftliche Prüfung

Stand: 21. September 2026. Geprüfter Commit: `f8e249fa49a6080f0edde7bff0d7138dc00e4616` auf `master`.
Repository: https://github.com/GenesisAeon/scoped-correspondence-formalism

**Das Repository hat die vorgeschlagenen Ausbaupakete weitgehend als ausführbare Prototypen umgesetzt. Der nächste große Fortschritt liegt in belastbarer Schätzung, unabhängiger Validierung und Verbindungen zwischen den vorhandenen Modulen.** Es gibt inzwischen konkrete Gegenüberstellungen von Aggregation und Heterogenität, eingefrorener Stabilität und echter zeitabhängiger Dynamik sowie statistischen Baselines und mechanistisch motivierten Modellen. Einige Schlussfolgerungen gehen allerdings weiter als die Berechnungen tragen. Beim Klimafit habe ich zudem ein quantitativ erhebliches Optimierungsproblem nachgewiesen.

**Prüfumfang und Reproduzierbarkeit.** Der Git-Baum umfasst 490 Einträge, der Quellcode 76 Python-Dateien. Alle lokalen Quell-, Daten- und Prüfdateien wurden vor der Ausführung gegen ihre Git-Blob-Prüfsummen am genannten Commit abgeglichen. Ausgeführt wurden alle 62 `verify_*.py`-Suiten: 60 liefen unmittelbar erfolgreich. Die beiden übrigen scheiterten ausschließlich an demselben Dokumentlink, dessen 3,26 MB große DOCX über den GitHub-Zugang nicht als Datei verfügbar war. Das Linkziel ist im Commit-Baum mit SHA `085255cc87c9b932df0db232d4fa793ea5895d8f` vorhanden. Eine ergänzende Prüfung fand 173 lokal vorhandene Links und genau diesen einen, im Git-Baum bestätigten Verweis. Es handelt sich damit nicht um einen nachgewiesenen Repository-Linkfehler. Es wurden keine Platzhalter erzeugt, um Tests grün zu machen. Alle tatsächlich ausgeführten mathematischen und datenbezogenen Checks bestanden.

Die Prüfung erfolgte mit Python 3.12.14, NumPy 2.3.5 und SciPy 1.17.0. Zusätzlich zu den vorhandenen Tests wurden eigenständige Gegenrechnungen durchgeführt. GitHub wurde nicht verändert. Historische Archive und sämtliche Literaturbeweise wurden nicht vollständig neu auditiert.

**Was jetzt überzeugend umgesetzt ist.**

| Umsetzung | Nachgeprüfter Fortschritt | Noch offene Aussagegrenze |
|---|---|---|
| Rollierende NOAA-Auswertung | 11 Ursprünge, jeweils fünf Jahre; lokaler 30-Jahres-Trend RMSE ≈ 0,119 °C, Persistenz ≈ 0,138 °C | Diese Auswertung liegt noch nicht vergleichbar für alle neuen Modelle vor. |
| COVID China/Rest der Welt | Prognose-RMSE 6.668,83 gegenüber 17.686,65 für ein gemeinsames Exponentialmodell und 15.932,68 für Persistenz | Eine rückblickend entwickelte Zerlegung auf einem bereits bekannten Testfenster. |
| Rate-induced tipping | Echte nichtautonome Integration; gleiche eingefrorene Stabilität bei unterschiedlichen Ergebnissen | Synthetisches Kontrollmodell; noch keine empirisch identifizierte Kipprate. |
| Puffer unter Lastpuls | Endpunkte, Spitzenhöhe, Dauer und Reserve werden explizit behandelt | Gleiche Spitzenhöhe und gleiche Gesamtlast sind verschiedene Vergleichsbedingungen. |
| Renewal-Modell | Kausale Faltung und nachvollziehbare Beziehung zwischen Wachstumsrate und R | Deterministische Punktschätzung aus geglätteten gemeldeten Fällen. |
| Zweischichten-Energiebilanz | Reale CO₂-Anregung und explizite dynamische Zustände | Optimierung, Referenzniveau, Identifizierbarkeit und Prognoseprüfung offen. |
| ETAS | Ereigniszeiten, Magnituden, Intensität und integrierte Intensität; deutlicher Anpassungsgewinn | Globaler zeitlicher Fit, keine räumliche Zuordnung oder unabhängige Prognoseprüfung. |
| Strukturbrücken B1/B2 | Reaktionsabschluss–FCA und Markov-Intertwining mit positiven Beispielen und Gegenbeispielen | Zwei konkrete Brücken; keine allgemeine Gleichsetzung aller Strukturen. |

Gerade B1/B2 setzen die ursprüngliche Idee gut um: Eine Beziehung wird konstruiert, ihre Voraussetzungen werden benannt, und ein Gegenbeispiel markiert ihre Grenze. Dieses Vorgehen sollte das Vorbild für weitere Verbindungen sein.

**Priorität 1: Den Klimafit korrigieren, bevor seine Residuen physikalisch interpretiert werden.**

Betroffene Stellen: `src/scoped_correspondence/dynamics/energy_balance.py`, `docs/energy_balance.md` und `verification/verify_energy_balance.py`.

Der gespeicherte Ergebnisbericht nennt einen Anpassungsfehler von 0,154203 °C. Mein unveränderter lokaler Lauf liefert 0,118808 °C. Bereits diese Abweichung zwischen Umgebungen ist für einen wissenschaftlichen Kalibrierungsbefund erheblich. Entscheidend ist ein einfacherer Gegenbeweis: Bei unveränderten vier physikalischen Koeffizienten genügt es, allein den Anfangswert T0 von −0,199964 auf +0,050507 °C zu verschieben, um den Fehler des gespeicherten Fits auf 0,109363 °C zu senken. Das ist eine Verbesserung innerhalb genau desselben Modells und derselben Daten.

Ich habe außerdem die lineare Zustandsdynamik bei derselben stückweise linearen CO₂-Anregung mittels Matrixexponential exakt fortgeschrieben und neu optimiert:

| Rechnung auf denselben 67 Jahren 1959–2025 | RMSE |
|---|---:|
| Im Repository gespeicherter Fit | 0,154203 °C |
| Unveränderter Repository-Code in meiner Umgebung | 0,118808 °C |
| Nur T0 verbessern, andere gespeicherte Parameter unverändert | 0,109363 °C |
| Exakte Fortschreibung und gemeinsamer Refit | 0,090232 °C |

Drei Startwerte erreichen beim letzten Verfahren praktisch denselben Fehler. Eine Rückintegration der gefundenen Parameter mit der originalen `solve_ivp`-Funktion ergibt ebenfalls 0,090232 °C; die größte Abweichung der Kurven beträgt etwa 1,34·10⁻⁷ °C. Die Vorwärtsgleichungen wurden also nicht durch ein anderes Modell ersetzt.

**Der bessere Fit ist kein besser identifiziertes Klimamodell.** Der Refit läuft beim Feedbackparameter α an die von mir gesetzte positive Untergrenze exp(−10) ≈ 4,54·10⁻⁵. Das ist ein Warnsignal für Modellmissspezifikation bzw. schwache Identifizierung. Die Rechnung dient als Gegenbeispiel zur Qualität des bisherigen Optimierungsresultats, nicht als neue Schätzung realer Klimakonstanten. Auch der lokale kleinste Singulärwert der Sensitivitätsmatrix ist sehr klein; eine belastbare Unsicherheitsanalyse braucht zusätzlich ein Fehler- und Abhängigkeitsmodell.

Der mittlere jüngste Residuenüberschuss sinkt ohne jeden Aerosolterm von etwa +0,235 auf +0,025 °C. Deshalb trägt dieser Fit die Aussage in `docs/energy_balance.md`, der Fehler sei nun auf fehlendes Aerosolforcing zurückgeführt, nicht. Aerosole sind physikalisch relevant; ihre Bedeutung im konkreten Residuum muss aber durch explizite alternative Anregungen und unabhängige Daten geprüft werden.

Empfohlene Reparatur: exakte Zustandsfortschreibung oder zuverlässige Sensitivitätsgleichungen; explizite Prüfung von Gradient, Abbruchgrund und Startwertabhängigkeit; anschließend Anschluss an die vorhandenen Profile-Likelihood- und Identifizierbarkeitsmodule. Die konkrete Ursache der Optimierungsempfindlichkeit – etwa das Zusammenspiel adaptiver Integration und numerischer Differenzen – ist damit noch nicht abschließend lokalisiert. `optimizer_success=True` allein reicht als Gütekriterium eindeutig nicht.

Zwei weitere Modellierungsfragen gehören dazu: F wird auf 1959 bezogen, die beobachtete Temperatur auf 1901–2000. Bei einer Verschiebung beider Temperaturzustände um δ muss auch F um αδ verschoben werden, damit dieselbe Physik beschrieben wird. Ein passender Forcing-Offset bzw. ein konsistentes Referenzniveau sollte explizit modelliert werden. Außerdem ist T_s(1959)=T_d(1959)=T0 eine zusätzliche Annahme, die historische Ozeanträgheit ausblendet. Ein früherer Modellstart oder ein eigener tiefer Anfangszustand wäre prüfenswert.

Der aktuelle Test verlangt sogar ausdrücklich die stärkere jüngste Unterschätzung als „aerosol-unmasking signature“. Solche Ergebnismuster gehören in den Ergebnisbericht; ein Funktionstest sollte keine bevorzugte kausale Interpretation festschreiben. Ebenso sind der Anpassungsfehler 1959–2025 und der NOAA-Prognosefehler aus rollierenden Fenstern kein fairer Leistungsvergleich.

**Priorität 2: Beim R-Tipping die mathematische Darstellung und die Schwellenbehauptung schärfen.**

In Modulbeschreibung und `docs/rate_dependent_tipping.md` fehlt beim Wechsel in mitbewegte Koordinaten ein Term. Für z=x−u(t) lautet die tatsächliche Gleichung

\[
\dot z=z-z^3-\dot u(t).
\]

Nur für eingefrorenes u verschwindet der letzte Term. Die Implementierung integriert die richtige ursprüngliche x-Gleichung; der Fehler liegt in der Erklärung. Gerade −u̇ ist hier der entscheidende Mechanismus.

Die Aussage einer „quantitatively precise validation“ von χ_max≥0,5 beruht auf einem groben Raster. Meine zusätzlichen Rechnungen ergeben:

| Rate r | χ_max=r/2 | Zweigwechsel |
|---:|---:|---|
| 0,6 | 0,30 | nein |
| 0,7 | 0,35 | nein |
| 0,8 | 0,40 | ja |
| 0,9 | 0,45 | ja |

Die bisherige Aussage stimmt für die damals getesteten Punkte, identifiziert aber keine präzise Schwelle. Schon im selben Modell tritt Kippen unterhalb 0,5 auf. Die neuen Punkte grenzen den beobachteten Wechsel zunächst zwischen r=0,7 und r=0,8 ein; eine kritische Rate braucht gezielte Fortsetzung bzw. Intervallsuche mit Kontrolle des Endhorizonts und der Nähe zur Separatrix. χ bleibt ein nützlicher lokaler Indikator, kein bewiesener Klassifikator.

**Priorität 3: Beim Puffer Peak, Dauer und Gesamtlast getrennt kontrollieren.**

Für den verwendeten Puls ΔW(t)=A exp[−(t/τ)²] ist die Gesamtlast A√π τ. Bei konstantem A ändert eine Variation von τ deshalb zugleich die Dauer und die gesamte Belastung. Der vorhandene Befund „kürzere Pulse sind ungefährlicher“ ist unter dieser Bedingung korrekt.

Als ergänzende Gegenkontrolle habe ich die Gesamtlast auf eins fixiert, also A=1/(√π τ), und denselben Puffer gerechnet:

| τ | Minimum bei gleicher Spitzenhöhe A=1 (Repo) | Minimum bei gleicher Gesamtlast 1 |
|---:|---:|---:|
| 0,05 | −0,081 | −0,912 |
| 0,20 | −0,265 | −0,747 |
| 0,50 | −0,495 | −0,558 |
| 1,00 | −0,695 | −0,392 |
| 2,00 | −0,858 | −0,242 |
| 5,00 | −0,965 | −0,109 |

Die Richtung kehrt sich um: Bei gleicher Gesamtlast sind die kürzeren Pulse hier gefährlicher. Auch dieser Vergleich verändert eine zweite Größe, nun die Spitzenhöhe; gerade deshalb sollte eine Antwortfläche über Amplitude und Dauer beide Familien sichtbar machen. Eine universelle Aussage über „Tempo“ allein ist nicht identifiziert. Die vorhandene Rechnung ist somit ein guter erster Kontrollfall, aber noch keine allgemeine Regel für schnelle Belastung.

**Priorität 4: ETAS zeigt einen starken Anpassungsgewinn, noch keine nachgewiesene Kritikalität.**

Der große AIC-Abstand von ungefähr 1.304 zugunsten des zeitlichen ETAS-Modells ist reproduzierbar. Er begründet einen starken relativen Anpassungsgewinn gegenüber der gewählten homogenen Poisson-Referenz. Er beweist weder, dass Selbstanregung die einzige Erklärung ist, noch dass der globale Katalog physikalisch ein kritischer Verzweigungsprozess wäre. Auch eine zeitvariable Hintergrundrate bzw. ein Cox-Prozess kann Clustering erzeugen; diese Alternativen wurden nicht verglichen. Eine Simulation der Jahreszahlen zur direkten Prüfung des ursprünglichen Fano-Befunds fehlt ebenfalls.

Besonders empfindlich ist die angegebene Verzweigungszahl n≈1,024. Ihr Zeitfaktor integriert den Omori-Kern bis unendlich:

\[
n=K\,E[e^{\alpha(M-M_0)}]\,\frac{c^{1-p}}{p-1}.
\]

Beim gespeicherten p=1,02492 liegt nur etwa **29,96 %** der gesamten Kernmasse innerhalb einer Zeitspanne von 9.756 Tagen, also selbst innerhalb der vollen Kataloglänge. Rund 70 % stammen aus dem darüber hinaus extrapolierten Ausläufer. Später im Beobachtungsfenster auftretende Ereignisse sind natürlich noch kürzer beobachtet.

Bei unveränderten übrigen Parametern ergibt eine reine Sensitivitätsrechnung n≈1,62 für p=1,015, n≈1,02 für p=1,02492 und n≈0,69 für p=1,04. Das ist ausdrücklich kein Konfidenzintervall und kein jeweils neu optimierter Fit. Es zeigt, wie empfindlich die Interpretation am kaum beobachteten langen Ausläufer hängt.

Konkret verbessern: Konvergenzstatus samt Budget und Startwerten im JSON-Bericht ausgeben; Profile für p und n; regionale, räumlich begrenzte Kataloge; Beobachtungsbeginn und -ende explizit übergeben statt erster/letzter Ereigniszeit; Vorhistorie berücksichtigen; zeitvariable Poisson-/Cox-Referenzen und Tests außerhalb des Anpassungsfensters. `minmagnitude=6` ist ein Auswahlfilter, kein eigener Nachweis der Katalogvollständigkeit. Im Text steht zudem „multiple Nelder-Mead starts“, während die Voreinstellung tatsächlich einen Start nutzt und typischerweise ohne formale Konvergenz endet. Die dokumentierten zusätzlichen Offline-Läufe können den AIC-Abstand stützen, ersetzen aber keine Unsicherheitsanalyse der Parameter.

Für eine echte Intensitätsprüfung eignet sich das Time-Rescaling-Theorem: Die integrierten Intensitäten zwischen aufeinanderfolgenden Ereignissen sollten unter einem korrekt spezifizierten bedingten Modell unabhängig exponentialverteilt mit Mittelwert eins sein. Nach Parameterschätzung müssen Referenzbänder entsprechend kalibriert oder an zurückgehaltenen Daten geprüft werden [3].

**Priorität 5: COVID-Ergebnisse als Modellvergleich und Sensitivitätsanalyse ausbauen.**

Die China/Rest-Zerlegung ist ein sinnvoller Fortschritt. Sie erklärt, warum eine globale Durchschnittsrate unzureichend sein kann. Die beiden Komponenten wurden auf ihren Trainingsdaten angepasst; das ist sauber getrennt. Da Zerlegung und Modellfamilie aber nach Kenntnis der bisherigen Resultate auf demselben März-Testfenster entwickelt wurden, handelt es sich um explorative Evidenz. Ein im Code festgeschriebener Split ist keine unabhängige prospektive Bestätigung.

Die Renewal-Rechnung und die Umrechnung einer Exponentialrate in R verwenden dieselbe Fallzeitreihe und denselben angenommenen Intervallkern. Ihre Übereinstimmung ist eine mathematische bzw. rechnerische Konsistenzprüfung, keine unabhängige empirische Bestätigung. Zusätzlich sind gemeldete, gleitend gemittelte Fälle ein Beobachtungsproxy für Infektionen. Das gemessene serielle Intervall darf nur unter passenden Definitionen und Annahmen als Ersatz des Generationenintervalls dienen [4, 5].

Meine illustrative Sensitivitätsrechnung bei festem Wachstum r=0,121004 pro Tag ergibt R≈1,42, 1,68 und 2,09 für angenommene mittlere Intervalle von 3, 4,7 und 7 Tagen bei gleichem Variationskoeffizienten. Das sind alternative Annahmen, keine epidemiologischen Unsicherheitsgrenzen. Sie zeigen, warum eine einzige R-Kurve zu wenig über die robuste quantitative Aussage verrät.

Nächster sinnvoller Schritt: mehrere Länder, festgehaltene zukünftige Testfenster, partielle gemeinsame Parameterschätzung und ein explizites Beobachtungsmodell für Meldeverzug und Untererfassung. Die vorhandenen täglichen Rohzahlen sind für ein Zählmodell geeigneter als überlappende Siebentagesmittel. Eine Negativ-Binomial-Beobachtung kann Überdispersion erfassen; ihre Notwendigkeit muss über Residuen und Prognosescores geprüft werden.

**Die mathematisch ergiebigste neue Verbindung: kausale Wirkungskerne und Verzweigungsoperatoren.**

Mehrere neue Module verarbeiten eine Vorgeschichte mit einem zeitlichen Kern. Das schafft eine präzise strukturelle Verwandtschaft:

| Gegenstand | Gemeinsame mathematische Struktur | Eigene Bedeutung und Voraussetzung |
|---|---|---|
| Linearer Puffer | Faltung der Last mit exp(−rt) | Deterministischer Zustand, r>0, definierte Sicherheitsgrenze |
| Zweischichten-EBM | Impulsantwort C exp(At) B | Energiefluss → Temperatur; feste Koeffizienten und konsistente Referenzen |
| Renewal-Modell | Gewichtete Summe vergangener Inzidenzen | Nichtnegative Intervallgewichte; Infektionen/Beobachtungen sauber unterscheiden |
| ETAS/Hawkes | Selbstanregender zeitlicher Kern | Bedingte Ereignisintensität; Markierungs- und Historienannahmen |

Für das EBM lässt sich beispielsweise die Übertragungsfunktion von F nach T_s direkt herleiten:

\[
G(s)=\frac{C_d s+\gamma}{(C_s s+\alpha+\gamma)(C_d s+\gamma)-\gamma^2}.
\]

Damit werden schnelle und langsame Relaxation, Gedächtnis und Filterwirkung explizit. Für ein stationäres lineares Hawkes-Modell mit passender Markierungsverteilung ist die Gesamtmasse seines mittleren Kerns die erwartete Zahl direkter Nachkommen. Die Verzweigungsdarstellung ist ein etablierter mathematischer Anschluss [2]. Bei mehreren Typen wird aus dieser Größe eine nichtnegative Matrix; ihr Spektralradius ist unter den jeweiligen Verzweigungsannahmen die relevante Schwellenstruktur. Hier bieten sich konkrete Verbindungen zu Renewal-Modellen und den vorhandenen baumartigen Perkolationsbeispielen an. Allgemeine räumliche Perkolation oder das nichtlineare R-Tipping sind dadurch nicht identifiziert.

Ein guter nächster Brückenbeleg wäre: Quellen- und Zielobjekt angeben, Kernabbildung konstruieren, Einheiten und Positivität prüfen, erhaltene Größe benennen und ein Gegenbeispiel bei verletzten Voraussetzungen ergänzen. Erst danach lohnt sich eine gemeinsame Kernel-API. Diese Verbindung kann innerhalb des bestehenden Strukturbrückenschemas dokumentiert werden.

Eine zweite nützliche Ableitung erweitert die bereits diskutierte Mischung konstanter Exponentialraten. Für positive differenzierbare Komponenten y_i, lokale Raten r_i=d(log y_i)/dt und Gewichte w_i=y_i/Σ_j y_j gilt

\[
r_{\rm eff}=\sum_iw_i r_i,
\qquad
\dot r_{\rm eff}=\operatorname{Var}_w(r_i)+\sum_iw_i\dot r_i.
\]

Der erste Term beschreibt den Zusammensetzungseffekt, der zweite die Veränderung innerhalb der Komponenten. Das ist ein präziser Anschluss an die Heterogenitätsfrage. Bei beobachteten Daten müssen Ableitungen und ihre Unsicherheit geschätzt werden. Der aktuelle COVID-Diagnostikwert mit beobachteten Gewichten und über das ganze Fenster konstant gefitteten Raten ist nicht automatisch diese exakte lokale Identität.

**Welche Erweiterungen jetzt den höchsten Nutzen haben.**

| Reihenfolge | Konkretes Paket | Nachweis, an dem es gemessen werden sollte |
|---|---|---|
| 1 | Numerisch zuverlässige EBM-Kalibrierung und Profile der neuen mechanistischen Modelle | Vorwärtslösungen stimmen überein; Optimierungsstationarität, Randlösungen und Parameterunsicherheit werden sichtbar. |
| 2 | Gemeinsame zeitliche Prognoseprüfung | Gleiche Zielgrößen, Ursprünge und Horizonte; Modellwahl nur mit zurückliegenden Daten; getrennte Fehler nach Horizont. |
| 3 | Probabilistische Ergebnisse | Vorhersageintervalle plus Deckung und Breite; Log-Score für Zähl-/Ereignismodelle, CRPS oder Intervallscore für kontinuierliche Ziele [6]. |
| 4 | Zwei neue Strukturbrücken | EBM/Puffer über Impulsantworten; Renewal/Hawkes/Verzweigung über positive Kerne und explizite Voraussetzungen. |
| 5 | Beobachtungs- und Zustandsmodelle | Latente Dynamik, Messprozess und tatsächliche Prognoseaufgabe werden getrennt; Meldeverzug bzw. Detektionsgrenzen sind prüfbar. |
| 6 | Mehrdimensionale R-Tipping-/Viabilitätskarten | Amplitude, Dauer, Pulsform und Reserve getrennt variieren; unterschiedliche Normierungen dokumentieren; Grenzfälle und Endhorizonte prüfen [1]. |

Für das Klimapaket sind die im Juni 2026 veröffentlichten **Indicators of Global Climate Change 2025** besonders passend: Sie stellen effektive Strahlungsanregung, Energieungleichgewicht und weitere Klimazeitreihen einschließlich versionierter Daten bereit. Das ermöglicht den nächsten Vergleich CO₂-only gegen vollständigeres Forcing und zusätzliche Einschränkungen durch Wärmeaufnahme [7]. Auch dort sind Attribution und Unsicherheit ein eigener Analyseschritt.

Für ETAS würde ein fachlich begründeter regionaler Katalog mit ausreichend vielen kleineren Ereignissen mehr bringen als nur weitere Jahre globaler M≥6-Daten. Die Vollständigkeitsschwelle muss geprüft werden; räumliche Eingrenzung, Erfassungsänderungen und Nachbeben nach sehr großen Ereignissen gehören ins Protokoll. Für COVID sind mehrere unabhängige Länder- und Zeitfenster mit unverändertem Verfahren der nächste Datengewinn.

**Weniger neue Namen, mehr überprüfbare Verbindungen.** Profile-Likelihood, Fisher-Sensitivität, Kontraktion, Viabilität, Closure, Conformal Prediction und Strukturbrücken existieren bereits. Sie sollten nun auf die echten neuen Modelle angewendet werden. Insbesondere darf eine Conformal-Garantie mit Austauschbarkeitsannahme nicht ungeprüft auf nichtstationäre, abhängige Zeitreihen übertragen werden. Ein gemeinsamer Ergebnisvertrag könnte `numerically_verified`, `optimizer_converged`, `parameters_identified`, `out_of_sample_evaluated` und `mechanism_discriminated` getrennt ausweisen. So kann ein grüner Algebra-Test nicht versehentlich als empirische Bestätigung gelesen werden.

Technisch wären ein zentraler Teststarter und GitHub Actions sinnvoll; im geprüften Baum gibt es keine `.github/`-Workflows. Schnelle mathematische Checks und aufwendige Datenkalibrierungen können getrennt laufen. Die Referenzumgebung sollte reproduzierbar festgehalten werden, ergänzt um eine kleine Kompatibilitätsmatrix. README nennt noch 51 Suiten, tatsächlich sind es 62; Paketversion und Beschreibung stehen weiterhin bei 0.41.0a1/M41. Neue APIs sollten außerdem nichtendliche Werte, leere Startwertlisten, unsortierte Ereignisse und unregelmäßige Jahresabstände gezielt behandeln. `energy_balance.py` verwendet derzeit die Anzahl überlappender Jahre als Zeitachse; fehlende Kalenderjahre würden dadurch unbemerkt zusammengedrückt.

**Die übergreifende Aussage sollte jetzt präziser werden.** Die Befunde stützen, dass ein konstanter globaler Trend oder eine homogene Ereignisrate wichtige Dynamik übersehen kann. Sie belegen nicht, dass lineare Dynamik generell ungeeignet wäre: Das neue Energiebilanzmodell und der Puffer sind selbst linear in ihren Zuständen und erzeugen zeitlich gekrümmte Antworten. Auch exponentielles Wachstum löst eine lineare Differentialgleichung. Tragfähiger ist die Forschungsfrage, welche Kombination aus veränderlichem Treiber, Heterogenität, Gedächtnis, Rückkopplung und Beobachtungsprozess ein konkretes Ergebnis erklärt – und welche Messung konkurrierende Erklärungen unterscheiden kann.

**Primärquellen und konkrete Anschlüsse.**

1. Wieczorek, Xie & Ashwin (2023), *Rate-induced tipping: thresholds, edge states and connecting orbits*. Nonlinearity 36, DOI [10.1088/1361-6544/accb37](https://doi.org/10.1088/1361-6544/accb37); [Autorenversion](https://arxiv.org/abs/2111.15497). Anschluss: globale Schwellengeometrie statt allein lokaler Kennzahl.
2. Hawkes & Oakes (1974), *A cluster process representation of a self-exciting process*. Journal of Applied Probability 11, 493–503, DOI [10.2307/3212693](https://doi.org/10.2307/3212693). Anschluss: Verzweigungsdarstellung unter Stationaritäts- und Endlichkeitsbedingungen.
3. Brown et al. (2002), *The time-rescaling theorem and its application to neural spike train data analysis*. Neural Computation 14, 325–346, [Primärabstract](https://pubmed.ncbi.nlm.nih.gov/11802915/). Anschluss: Diagnose geschätzter bedingter Intensitäten; die Mathematik ist nicht auf neuronale Daten beschränkt.
4. Nishiura, Linton & Akhmetzhanov (2020), *Serial interval of novel coronavirus (COVID-19) infections*. DOI [10.1016/j.ijid.2020.02.060](https://doi.org/10.1016/j.ijid.2020.02.060), [Autoren-PDF](https://nlinton.github.io/files/pubs/Nishiura_2020_SI.pdf). Quelle der im Repo verwendeten frühen Intervallschätzung.
5. Park et al. (2021; online 2020), *Forward-looking serial intervals correctly link epidemic growth to reproduction numbers*. PNAS 118, e2011548118, DOI [10.1073/pnas.2011548118](https://doi.org/10.1073/pnas.2011548118). Anschluss: korrekte zeitliche Definition und Kohortenwahl bei seriellen Intervallen.
6. Gneiting & Raftery (2007), *Strictly Proper Scoring Rules, Prediction, and Estimation*. JASA 102, 359–378, DOI [10.1198/016214506000001437](https://doi.org/10.1198/016214506000001437), [Autoren-PDF](https://sites.stat.washington.edu/people/raftery/Research/PDF/Gneiting2007jasa.pdf). Anschluss: Bewertung ganzer Vorhersageverteilungen.
7. Forster et al. (2026), *Indicators of Global Climate Change 2025*. Earth System Science Data 18, [10.5194/essd-18-3889-2026](https://essd.copernicus.org/articles/18/3889/2026/). Datenstand [v2026.06.02](https://github.com/ClimateIndicator/data/tree/v2026.06.02); archivierte Daten [10.5281/zenodo.20499280](https://doi.org/10.5281/zenodo.20499280).
8. Geoffroy et al. (2013), *Transient Climate Response in a Two-Layer Energy-Balance Model. Part I: Analytical Solution and Parameter Calibration Using CMIP5 AOGCM Experiments*. DOI [10.1175/JCLI-D-12-00195.1](https://doi.org/10.1175/JCLI-D-12-00195.1). Bereits im Repo verwendete Grundlage; analytische Antwort und gezielte Kalibrierung sind der passende Anschluss.

Die neuen numerischen Befunde dieses Berichts stammen aus den beigefügten eigenen Rechenskripten und dem angegebenen Repository-Stand, nicht aus den Literaturquellen. Das Rechenpaket enthält Ergebnis-JSON, Prüfprotokolle, Reproduktionscode und die Vergleichsgrafik. Die Rohdaten und Repository-Quellen bleiben über den angegebenen Commit referenziert. Für die verwendeten COVID-Daten gilt: Data: Our World in Data / Johns Hopkins University CSSE COVID-19 Data Repository (CC BY 4.0).
