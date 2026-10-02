# SCF: Myonium, Gravitationsmessung und identifizierbare Abweichungen

**Umsetzungsplan für Claude-Code — MU0–MU7**  
Stand: 01.10.2026 · Auftrag: Johann · Status: vorgeschlagen, nicht im Repo implementiert.

## 1. Auftrag und wissenschaftlicher Gewinn

Baue eine kleine, eigenständige Domäne für **Messplanung und Evidenzprüfung bei Myonium-Gravitation**. Ihr Kern ist die Frage: Unter welchen Annahmen kann eine beobachtete Zählratenmodulation einer effektiven Beschleunigung zugeordnet werden, und welche Störgrößen erzeugen dieselben Beobachtungen?

Das passt zu SCF: Zustandsdynamik, Messoperator, Identifizierbarkeit und Schlussfolgerung werden explizit getrennt. Ein erfolgreicher Abschluss kann ebenso eine nachgewiesene Nichtidentifizierbarkeit wie eine präzise Schätzung sein. Das Modul muss keine neue Gravitationstheorie vertreten. Es kann das Standardmodell der Messung verbessern und mögliche Abweichungen testbar machen.

**Lieferumfang:** analytischer Kontrollfall; vorwärts gerichtetes Zählmodell; synthetische Experimente; Profile mit Diagnostik; Gegenbeispiele zur Identifizierbarkeit; bedingte Sensitivitätsanalyse; ehrliche Evidenzberichte. Echte Daten sind eine gesonderte, freigabepflichtige Ausbaustufe nach dem vorhandenen Provenienzprotokoll.

**Nicht Gegenstand:** eine vollständige LEMING-Simulation, eine neue Quantengravitation, eine kosmologische Vererbungstheorie, eine Widerlegung Einsteins oder eine bereits erfolgte Messung der Myonium-Gravitation. Aus dieser Planung folgt auch keine physikalische Bestätigung für CREP, UTAC oder AFET.

Das Begleitdokument `SCF_POLYEDER_SAKURAI_SATURN_ANSCHLUSSBEWERTUNG.md` behandelt Johanns zusätzliche Kandidaten. Diese sind keine Abhängigkeiten von MU0–MU7.

## 2. Ausgangspunkt und Quellenstatus

Die Meldung von pro-physik ist Anlass, nicht Datenquelle. Die geprüfte aktuelle Originalarbeit ist J. Zhang et al., *Generation of a high-intensity, superthermal muonium beam for gravity and laser spectroscopy experiments*, Nature Physics, veröffentlicht am 14.09.2026, DOI [10.1038/s41567-026-03433-x](https://doi.org/10.1038/s41567-026-03433-x). Sie demonstriert eine Strahlquelle und deren Charakterisierung. Eine Gravitationsmessung wird vorbereitet. Myonium ist das neutrale gebundene System aus positivem Myon und Elektron; es ist kein reines Antimaterieatom. Die schmale Geschwindigkeitsverteilung darf nicht mit einem nahezu ruhenden Strahl verwechselt werden. Die Arbeit nennt eine Geschwindigkeit um 2180 m/s. Diese wenigen Fakten bilden den Quellenbezug; die unten verwendeten Beispielwerte sind ausdrücklich illustrative Designannahmen.

| Kennung | Primärquelle | Geprüft / Verwendung | Grenze |
|---|---|---|---|
| MU-S1 | [Zhang et al., Nature Physics 2026](https://www.nature.com/articles/s41567-026-03433-x) | Verlagsseite und PDF; Status der Quelle und Strahlcharakterisierung | Keine gemessene Fallbeschleunigung daraus ableiten |
| MU-S2 | [arXiv:2512.19923v1](https://arxiv.org/html/2512.19923v1) | Vorabfassung vom 22.12.2025, Titel beginnt mit „Synthesis“ | Zahlen, Unsicherheiten und Formeln nicht unbemerkt mit der Verlagsfassung mischen |
| MU-S3 | [Antognini et al., Studying Antimatter Gravity with Muonium, 2018](https://arxiv.org/pdf/1802.01438), [DOI](https://doi.org/10.3390/atoms6020017) | Historischer Vorschlag und Interferometrie-Kontext | Historische Strahlannahmen sind keine aktuellen Messwerte |
| MU-S4 | [ETH-Mitteilung vom 15.09.2026](https://ethz.ch/de/news-und-veranstaltungen/eth-news/news/2026/09/neuartiger-teilchenstrahl-koennte-einsteins-schwerkraft-theorie-ins-wanken-bringen.html) | Institutionelle Statusmeldung | Zukunftsaussagen sind Planungen |
| MU-S5 | [Datenreferenz 10.3929/ethz-c-000802445](https://doi.org/10.3929/ethz-c-000802445) | In der Originalarbeit genannt | Dateien, Schema, Lizenz und Inhalt für dieses Paket noch nicht geprüft |

Beim Übertragen von Formeln ist insbesondere die Definition der Flugzeit und der Verschiebung zu prüfen: Einzelbahnabsenkung, relative Verschiebung am dritten Gitter und Interferometerphase sind verschiedene Größen. Der folgende Kontrollfall wird deshalb vollständig aus seinen eigenen Annahmen abgeleitet. Unterschiedliche Faktoren in einer Veröffentlichung sind zunächst ein Anlass zur Prüfung ihrer Geometrie und Konventionen, kein automatisch nachgewiesener Fehler.

## 3. Repo-Anschluss und Arbeitsregeln

Geprüfter öffentlicher Repo-Stand: `GenesisAeon/scoped-correspondence-formalism`, Commit `4a7ed38640ac7d393017eb5556291c879c3bceac`. Das ist der beim Erstellen gelesene Stand, keine Behauptung über einen späteren HEAD oder einen hier ausgeführten CI-Lauf.

Vor MU0 aktuellen HEAD, `CLAUDE.md`, gegebenenfalls `AGENTS.md`, Testaufruf und konkurrierende Änderungen prüfen. Neue Dateinamen unten sind **Vorschläge**, keine bereits vorhandenen APIs. Die zuvor erarbeitete J-Roadmap war an diesem Stand nicht implementiert; MU darf sie nicht stillschweigend voraussetzen.

| Bestehender Anschluss | Tatsächlicher Nutzen | Integrationsgrenze |
|---|---|---|
| `identifiability/profile_likelihood.py` | Profilberichte und Intervallklassifikation | Ein flacher Scan beweist keine globale Unbeschränktheit |
| `identifiability/profile_likelihood_nlp.py::profile_parameter_nlp` | Minimierung einer Residuenquadratsumme mit fixiertem Parameter | Kein beliebiger NLL-Optimierer; lokale Least-Squares-Läufe sind keine globale Garantie; aktuelle Rückgabe liefert nicht alle benötigten Optimiererdiagnosen |
| `validation/scoring_rules.py::poisson_log_score` | Poisson-Negativloglikelihood, kleiner ist besser | Bestehende Funktion verlangt positive Mittelwerte; den Grenzfall λ=0 separat exakt behandeln |
| `epistemic/observation_fibers.py` | Endliche Beobachtungsfasern | Endliche Kandidatenlisten nicht als kontinuierliche Vollständigkeit ausgeben |
| `epistemic/finite.py::audit_finite_claim` | Annahmengebundene Aussagen auf endlichen Modellen | Keine experimentelle Evidenz ohne Messdaten |
| `epistemic/adapters.py` | Beispiel für Herkunft und Scope von Evidenz | Keine Umdeklaration synthetischer Resultate als empirische Bestätigung |
| `correspondence/contract.py` | Scope und explizite Korrespondenzverträge | Stichprobenresiduen sind kein Bereichsbeweis |
| `docs/real_data_provenance.md` | Realdatenprotokoll | Quelle, exakter Abruf, Zeitstempel, Hash, Lizenz und Dokumentation erforderlich |

Den numerischen Optimierer für MU bei Bedarf additiv kapseln, statt den bestehenden generischen Profilcode beiläufig umzubauen. Gemeinsame J-Dimensions- oder Vertragsprüfer erst nach Prüfung ihrer tatsächlichen Existenz anschließen.

Für jedes Paket: Herleitung vor Produktionscode; Zielprüfung, alle bisherigen MU-Prüfungen, vollständige Regression und Linkprüfung; danach einzelner Commit. Push entsprechend Johanns Arbeitsauftrag und Repo-Regeln. Diese Übergabe selbst enthält keinen Produktionspatch und keinen Push.

## 4. Messgröße, Scope und Konventionen

Definiere eine empfindliche Achse mit positivem Vorzeichen in Richtung der lokalen Referenzbeschleunigung. `a_mu` bezeichnet die **effektive Beschleunigung des Myoniumatoms entlang dieser Achse**. `g_ref > 0` ist die dazu passende lokale Referenz einschließlich Projektion und deklarierter Korrekturen.

\[
\delta_g=\frac{a_\mu-g_{\rm ref}}{g_{\rm ref}}.
\]

Negative Beschleunigungen nicht durch eine ungeprüfte Positivitätsannahme ausschließen. Ein beschränkter Parameterraum muss als Annahme ausgegeben werden. Optional:

\[
\eta=\frac{2(a_\mu-g_{\rm ref})}{a_\mu+g_{\rm ref}}
     =\frac{2\delta_g}{2+\delta_g}.
\]

Bei verschwindendem Nenner ist η undefiniert. η und δ sind nur für kleine Abweichungen näherungsweise gleich. Aus einer Myonium-Messung lässt sich die Gravitation des Antimyons allein erst mit zusätzlichen Annahmen über Elektron, Bindungsenergie und Zusammensetzung ableiten.

Pflichtfelder jeder Auswertung: Achse und Vorzeichen, Geometrie, SI-Einheiten, Referenzort der Teilchenrate, Definition der Geschwindigkeitsverteilung, Kalibrationsannahmen, Suchbereich, Evidenzart und Gültigkeitsgrenzen.

## 5. Analytisches Idealmodell: drei äquidistante Ebenen

### 5.1 Kinematik

Der Einstieg ist ein **geometrisches Modell mit konstanter longitudinaler Geschwindigkeit und konstanter transversaler Beschleunigung**. Es ersetzt keine vollständige Wellenoptik oder vertikale Apparaturbeschreibung. Bei drei Ebenen zu den Zeiten 0, T, 2T gilt mit Gitterabstand L und Periode d:

\[
T=L/v,\qquad z(t)=z_0+u_0t+\tfrac12at^2,
\]

\[
\Delta z=z(2T)-2z(T)+z(0)=aT^2,
\qquad K(v)=\frac{2\pi L^2}{d v^2},\qquad \phi_g=K(v)a.
\]

Die relative Verschiebung eliminiert Anfangslage und transversale Anfangsgeschwindigkeit. Die Einzelbahnabsenkung nach T ist dagegen aT²/2. Gitterlagen G1, G2, G3 erzeugen die Kombination h=G3−2G2+G1 und einen zugehörigen Phasenoffset −2πh/d. h und ein freier identischer Phasenoffset dürfen nicht als unabhängig identifizierbare Parameter ausgegeben werden.

Scope: L,d,v,T positiv und endlich; gleiche Flugzeiten; konstante Beschleunigung auf der betrachteten Strecke; bekannte empfindliche Achse; kein unmodellierter Wechsel der Geometrie. Ungleiche Zeiten, longitudinal beschleunigte Strahlen, Beugung und echte Geräteeffekte sind getrennte Erweiterungen mit neuer Herleitung.

### 5.2 Referenzwerte, unabhängig nachgerechnet

**Illustrative Eingaben:** g=9,81 m/s²; τ=2,2 µs; T=4,4 µs=2τ; d=100 nm; v=2180 m/s. Insbesondere g ist kein vor Ort gemessener Präzisionswert und τ ist hier gerundet.

| Größe | Ergebnis |
|---|---:|
| Abstand L=vT | 9,592 mm |
| Einzelbahnabsenkung nach einer Lebensdauer τ | 23,7402 pm |
| Relative Verschiebung gT² | 189,9216 pm |
| Phase 2πgT²/d | 0,0119331260663604 rad |
| Überlebensfaktor für 2T | exp(−4)=0,0183156388887342 |
| Phasenänderung für 1 % von g | 119,3312607 µrad |
| Äquivalente relative Gitterverschiebung für 1 % | 1,899216 pm |

Dies sind Kontrollwerte des definierten Modells, keine publizierten LEMING-Ergebnisse. Die letzten Zeilen beschreiben eine äquivalente Störgröße, keine vollständige Anforderungsspezifikation des Experiments.

## 6. Vom Strahl zum beobachteten Zählsignal

### 6.1 Geschwindigkeit, Zerfall und Selektion

`q(v)` soll zunächst eine normierte **Flussverteilung lebender eintreffender Atome an Ebene 1** sein. Sie ist nicht ohne Umrechnung eine räumliche Teilchendichte. Unter dieser Definition beginnt der Überlebensfaktor an Ebene 1:

\[
S(v)=\exp[-2L/(v\tau)]
\]

im nichtrelativistischen Kontrollfall. Für eine andere Ratenreferenz kommen Vor- und Nachflugzeiten hinzu; bei Bedarf τ→γ(v)τ. Bereits in einer gemessenen Rate enthaltene Verluste dürfen nicht ein zweites Mal angewandt werden. Eine Nachweiswahrscheinlichkeit für Zerfallsprodukte in einem endlichen Detektorvolumen ist ein weiterer Messoperator, kein weiterer willkürlicher Lebensdauerfaktor.

Für diskrete Geschwindigkeitsklassen positive Gewichte verwenden und deren Summe prüfen. Eine Unsicherheit des geschätzten Mittelwerts v ist **nicht** die Breite von q(v). Für kontinuierliche q sind Integrationsgrenzen, Restmasse, Quadraturfehler und v→0-Verhalten explizit auszugeben. Die erste Implementierung darf sich auf endliche Mischungen beschränken.

### 6.2 Zählmodell und Phasenmittelung

Für Scanbin j mit Messzeit t_j, Phase α_j und Orientierung s_j∈{−1,+1}:

\[
\lambda_j=t_j b_j+t_j R_j\int_0^\infty q_j(v)A_j(v)\epsilon_j(v)S_j(v)
\{1+C_j(v)\cos[\alpha_j+\phi_{0,j}+s_jK_j(v)a_\mu+\phi_{{\rm sys},j}(v)]\}\,dv.
\]

R ist die Rate am definierten Eingang, A die mittlere Transmission, ε die Nachweiseffizienz und b die Hintergrundrate. Fordere 0≤C≤1, 0≤ε≤1 und bei Interpretation als Transmissionswahrscheinlichkeit A(1+C)≤1. Messzeiten sind pro Bin anzugeben: Eine Gesamtzeit darf nicht für jeden Bin erneut eingesetzt werden.

Die Notation j erlaubt unterschiedliche Einstellungen, **keine beliebig freien Raten und Offsets je Scanpunkt**. Produktionsmodelle teilen R, b, C und Offsets innerhalb deklarierter Blöcke oder binden sie an unabhängige Kalibrationen. Ein frei wählbarer Mittelwert je Bin zerstört die interessierende Identifizierbarkeit.

Bei W=∫qAεS>0 kann man einen komplexen Kontrast definieren:

\[
F=\frac{\int qA\epsilon S C e^{i\phi(v)}\,dv}{W},
\quad\lambda=t b+tR W\{1+\operatorname{Re}(e^{i\alpha}F)\}.
\]

Diese Größe addiert erwartete Intensitätsmodulationen verschiedener Geschwindigkeitsklassen; sie behauptet keine Quantenkohärenz zwischen verschiedenen Atomen. Bei F=0 ist die Phase undefiniert; bei W=0 existiert kein Signal. Mittelwerte der Phasen oder die Phase bei der mittleren Geschwindigkeit ersetzen das Integral im Allgemeinen nicht.

### 6.3 Likelihood und Optimierung

Unabhängige rohe Zählungen im deklarierten Messmodell:

\[
n_j\sim\mathrm{Poisson}(\lambda_j),\quad
\operatorname{NLL}=\sum_j[\lambda_j-n_j\log\lambda_j+\log(n_j!)].
\]

Exakte Grenzfälle: NLL(0;0)=0 und NLL(n>0;0)=∞. Keine künstliche positive Untergrenze, die unmögliche Ereignisse stillschweigend möglich macht. Negative Counts und negative Mittelwerte ablehnen. Hintergrundsubtrahierte oder lebensdauerkorrigierte Werte sind nicht automatisch Poisson-Zählungen. Werden dieselben Ereignisse in mehreren Histogrammen verwendet, ist ihre Abhängigkeit zu berücksichtigen.

Für einen Least-Squares-Anschluss kann die Poisson-Deviance verwendet werden:

\[
D=2\sum_j[\lambda_j-n_j+n_j\log(n_j/\lambda_j)],
\]

mit Nullcount-Term 2λ. Vorzeichenbehaftete Quadratwurzelresiduen ergeben D als Quadratsumme; die Residuen dürfen nicht aus der NLL selbst konstruiert werden. Alternativ einen direkten NLL-Optimierer kapseln. In beiden Fällen Mehrfachstarts, Konvergenz, aktive Grenzen, Zielfunktionswert und fehlgeschlagene Läufe speichern. Lokale Konvergenz ist keine globale Optimalität.

Kalibrationsdaten erhalten ihre eigene Likelihood. Ihre Unsicherheit wird nicht durch Fixieren des Bestfits beseitigt. Bayes-Priors müssen als Priors bezeichnet werden; penalisiertes Fitten nicht unbemerkt als reine Profil-Likelihood berichten.

## 7. Identifizierbarkeit und zwingende Gegenbeispiele

1. **Ein Flugzeitwert und unbekannter Offset:** φ=Ka+φ0 erlaubt (a,φ0)→(a+c,φ0−Kc). Mehr Counts beheben diese strukturelle Nichtidentifizierbarkeit nicht.
2. **Zwei Flugzeiten:** In bereits entfalteten Phasen p_j=u_j A+b mit u=(1,4) lässt sich (A,b) lokal trennen. Dies setzt einen gemeinsamen Offset und richtige Kalibration voraus.
3. **Phasenperiodizität:** Bei einem T erzeugt a→a+d/T² dieselben Counts. Auch zwei Zeiten mit K2=4K1 behalten gemeinsame Aliasse. Voller Rang eines linearen Modells entfalteter Phasen beweist keine globale Eindeutigkeit der periodischen Likelihood.
4. **Beschleunigungsähnliche Störung:** p_j=u_j(A+B)+b trennt A und B auch mit vielen Flugzeiten nicht. Externe Kontrolle oder eine nachgewiesen andere Skalierung ist nötig.
5. **Orientierungsumkehr:** p_s=sA+b trennt einen geraden Offset. Eine ebenfalls ungerade Störung sB bleibt erhalten. Für jede Störgröße eine Paritätstabelle erstellen; apparativer Umbau darf nicht automatisch als perfekte Umkehr gelten.
6. **Geschwindigkeitskalibration:** v_assumed=(1+e)v_true bewirkt im Einzelgeschwindigkeitsmodell a_fit/a_true=(1+e)². Schon 1 % Geschwindigkeitsfehler erzeugt 2,01 % Beschleunigungsfehler.
7. **Kontrastverlust:** Gleich gewichtete Phasen 0 und π haben verschwindenden Kontrast. Das arithmetische Phasenmittel π/2 täuscht hier Information vor.
8. **Nichtidentische Auswahl:** Langsame Atome zerfallen häufiger. Fitten mit der Eingangsmischung statt der detektierten Mischung kann die Gravitation verzerren.

Magnetische Gradienten, elektrische Polarisation, Rotation/Coriolis, Ausrichtung, Gitterdrift, Kollimation und Hintergrund sind mögliche Störklassen. Für die erste Version reicht eine explizit parametrisierte Störphase; quantitative Kraftmodelle brauchen eigene Quellen und Gerätekalibration. Neutralität allein setzt diese Beiträge nicht auf null.

Ein Ergebnisbericht unterscheidet: analytisch bewiesene Entartung; endliche, vollständig geprüfte Kandidatenmenge; numerischer Scan; konditionale Schätzung; reale Evidenz. Grenzen und getrennte Profilkomponenten müssen sichtbar bleiben. Ein Intervall, das an einer Suchgrenze endet, ist nicht automatisch abgeschlossen. Bei periodischer Mehrdeutigkeit Mengen von Intervallen statt eines willkürlich um den bevorzugten Fit gelegten Intervalls zurückgeben.

## 8. Sensitivität und Experimentdesign

Für bekannte lokale Phase, bekannten Kontrast C, keinen Hintergrund und ideale Quadraturmessung gilt:

\[
I_a=N C^2 K^2,\qquad \sigma_a\ge\frac{1}{C\sqrt N\,K}.
\]

Das ist eine lokale Fisher-Grenze unter diesen Bedingungen. Ein Scan hat nicht automatisch dieselbe Information: Vier gleich lange Phasenstufen bei φ=0 und bekanntem Normalisierungsniveau liefern Iφ=NC²/2. Bei N=400 und C=0,2 ergeben sich Iφ=8; ideale Quadratur mit gleicher erwarteter Ereigniszahl ergibt 16. Freie Nuisance-Parameter erfordern die gemeinsame Informationsmatrix; Singularität muss als solche gemeldet werden.

Mit den Referenzwerten und C=0,35 benötigt die ideale lokale Formel für σ_a/g=1 % etwa **5,73265035×10^8 detektierte Signalereignisse**. Dies ist kein Zeitplan für LEMING. Quelle, Verluste, Hintergrund, reale Scanstrategie und Kalibrationsunsicherheit fehlen dieser Übersetzung.

Bei festem eintreffendem Budget und zeitunabhängigem Kontrast ist N(T)=N0 exp(−2T/τ). Daher:

\[
\sigma_a(T)\propto e^{T/\tau}/T^2,
\quad\frac{d\log\sigma_a}{dT}=1/\tau-2/T,
\quad T_{\rm opt}=2\tau.
\]

Andere Verluste und Hintergründe können das Optimum ändern. Eine Optimierung darf nicht gleichzeitig N konstant halten und Zerfallskosten behaupten. Budget immer benennen: detektierte Ereignisse, einfallende Atome oder Messzeit.

Für Intervalle zunächst synthetische Abdeckungsstudien: wahres Modell, absichtlich weggelassener Offset, gemeinsamer Fit mit Kalibrationsdaten und nichtidentifizierbarer Fall. Monte-Carlo-Größe, Seed, Fehlerrate und Binomialunsicherheit angeben. Die Schwelle ΔD≈3,84 ist nur eine asymptotische 95-%-Referenz für einen regulären skalaren Parameter, keine automatische Garantie bei Grenzen, Aliassen oder kleinen Counts. Ein systematisch schlechter Fit ist als negatives Ergebnis zu dokumentieren, nicht durch nachträgliche Auswahl günstiger Szenarien zu verdecken.

## 9. Vorgeschlagene Architektur

Klein anfangen, vorhandene Fehler- und Berichtskonventionen verwenden:

```text
src/scoped_correspondence/muonium/
  __init__.py
  records.py                 # Einheiten, Scope, Design, gemeinsame Nuisance-Blöcke
  kinematics.py              # zweite Differenz, Phase, Zerfall
  forward.py                 # diskrete Mischungen und erwartete Counts
  likelihood.py              # NLL, Deviance, lokale Fitdiagnosen
  identifiability.py         # exakte Gegenbeispiele, Alias- und Nuisance-Berichte
  design.py                  # Fisher und budgetabhängige Sensitivität
  evidence.py                # explizite Evidenzart und epistemischer Anschluss
scripts/run_muonium_pilot.py
docs/muonium_gravity.md
docs/muonium_source_audit.md
MUONIUM_GRAVITY_ROADMAP.md
verification/verify_muonium_*.py
```

Kein neuer Großframework-Zwang. Dataclasses mit serialisierbaren Ergebnissen genügen. Zahlen und Status getrennt speichern; mathematisch undefinierte Werte als `null` plus Grund, nicht als erfundene Null. Infinite NLL intern zulässig, in standardkonformem JSON als Status plus `null`. Jede numerische Rechnung berichtet den Suchbereich und relevante Toleranzen.

Ergebnisfelder mindestens: `evidence_kind`, `source_ids`, `assumptions`, `geometry`, `rate_reference`, `parameter_units`, `calibration_status`, `identifiability_scope`, `aliases_in_search_range`, `optimizer_diagnostics`, `boundary_hits`, `interval_method`, `unresolved_ranges`, `coverage_validation`, `limitations`. Nicht benötigte Felder bleiben explizit unbewertet; kein pauschales `verified=true` für heterogene Aussagen.

## 10. Pakete und Abnahme

### MU0 — Quellenregister und Anschlussinventar

Erstelle Roadmap, Quellenregister und eine Tabelle realer API-Signaturen. Trenne heutige Quelle, historische Vorschläge und eigene Designwerte. Reproduziere die Kontrollfälle unabhängig, bevor du den beigefügten Oracle ausführst. Dokumentiere den aktuellen HEAD und offene Datenfragen. Keine Produktions-API in diesem ersten Paket.

**Abnahme:** Quellstatus korrekt; keine Behauptung eines gemessenen g_mu; bisherige Tests und Links unverändert grün; unabhängige Herleitungen abgelegt.

### MU1 — Kinematik, Einheiten und Geltungsbereich

Implementiere das äquidistante Idealmodell, δ/η, zweite Differenz, Phase und Zerfall. Domänenfehler explizit behandeln. SI intern; Umrechnung am Rand. Herleitung zeigt, welcher Faktor zur Einzelbahn und welcher zur relativen Gitterverschiebung gehört.

**Kontrollen:** MU-C01–C05, MU-C14. Zusätzlich ungleiche Zeiten ablehnen, η-Nenner null, ungültige Geometrie, nichtendliche Eingaben. Negative a bleiben im definierten Scope zulässig.

### MU2 — Endliche Geschwindigkeitsmischung und Messoperator

Implementiere physikalisch konsistente Transmissions- und Effizienzgewichte, komplexen Kontrast und erwartete Counts. Exakte Einzelgeschwindigkeit als Grenzfall. Überlebensgewichtung und Ratenreferenz dürfen nicht verwechselt werden. Kontinuierliche Quadratur ist optional und darf MU2 nicht blockieren.

**Kontrollen:** MU-C06–C07, MU-C16; Nullsignal, F=0, C=0 und C=1; Summe der Messzeiten; unzulässige Gewichte. Keine Phase aus `arg(0)` melden.

### MU3 — Count-Likelihood und Schätzdiagnostik

Implementiere NLL und Deviance mit korrekten Nullfällen. Fit zunächst a bei vollständig bekannter Kalibration; danach a plus ein gemeinsamer Offset, wobei MU4 die Entartung aufdecken muss. Profile nutzen Mehrfachstarts und zeigen alle gefundenen Moden im Suchbereich.

**Kontrollen:** MU-C08, MU-C14–C15; synthetische Erwartungswerte exakt reproduzieren; keine negative oder nichtganzzahlige Zählung akzeptieren. Suchgrenze, Optimiererfehler und schlechte Konvergenz bleiben sichtbar. Kein behaupteter globaler Beweis aus Multistart.

### MU4 — Identifizierbarkeit und Interventionen

Implementiere die acht Gegenbeispiele aus Abschnitt 7. Trenne entfaltete lineare Phase vom periodischen Countmodell. Baue eine kleine endliche Kandidatenliste für `observation_fiber` und einen analytischen Bericht für kontinuierliche Symmetrien. Eine endliche Beobachtungsfaser ist kein Beweis über alle reellen Parameter.

**Kontrollen:** MU-C09–C11, MU-C14, MU-C17. Der Test muss ausdrücklich zeigen, dass mehr Flugzeiten und Umkehrungen nicht jede Störung entfernen. Keine Aussage „Umkehrung beweist Gravitation“.

### MU5 — Design und bedingte Abdeckung

Implementiere Fisher-Matrix und Sensitivität für feste Budgets. Vergleiche Quadratur und Vierphasenscan bei gleichen Ressourcen. Prüfe das analytische T-Optimum im begrenzten Idealmodell. Führe eine kleine reproduzierbare Intervallstudie durch und dokumentiere auch Fehlkalibration und Nichtidentifizierbarkeit.

**Kontrollen:** MU-C04, MU-C12–C13, MU-C16. Fisher-Singularität darf nicht durch eine stillschweigende Pseudoinverse zu scheinbarer Präzision werden. Monte-Carlo-Abnahme anhand vorab festgelegter Szenarien und statistischer Unsicherheit, nicht anhand eines exakten Zufallsanteils. Größere Studien getrennt von schneller CI.

### MU6 — Evidenzadapter und optionales Realdatenfenster

Pflicht: synthetische Berichte mit `evidence_kind=synthetic`, algebraische Resultate mit entsprechendem Scope und endliche Audits mit Kandidatenumfang. Optional: einen Strahlcharakterisierungsdatensatz der Quellenarbeit nach Provenienzprüfung anbinden. Dieser darf nur Strahleigenschaften oder Nachweisparameter kalibrieren, keine nicht gemessene Gravitation.

**Daten-Gate:** Inhalt, Nutzbarkeit, Lizenz, exakter Abruf, Hash, Einheitenschema und Version prüfen. Falls keine passende Datei verfügbar oder die Weitergabe ungeklärt ist, Decoder und eigene Fixtures liefern und den Realdatenzweig `deferred` oder `blocked` markieren. Öffentlich erreichbar bedeutet nicht automatisch frei weiterverteilbar. Read-only-Quellenprüfung nicht mit einer Freigabe zum Einchecken fremder Daten verwechseln.

**Abnahme:** reale Quelle, synthetische Messung und zukünftige Prognose sind in CLI und JSON unterscheidbar. Ein übersprungener Datencheck ist `skipped`, nicht `passed`.

### MU7 — CLI, Fähigkeitsbilanz und Abschluss

CLI mit mindestens `--scenario ideal|offset|reversal|velocity_mixture|aliases`, `--seed`, `--output` und explizitem Parameterraum. Ausgabe nennt Annahmen, Identifizierbarkeit, Profilmoden, Grenzen und Unsicherheitsart. Keine Überschrift „Einstein widerlegt“ für ein eingespritztes synthetisches Signal.

Fähigkeitsübersicht und Roadmap aktualisieren; offen gebliebene Teilpakete sichtbar lassen. Neue Prüfskripte in der vorhandenen `_EXPLICIT_CATEGORY` registrieren. Die synthetischen und algebraischen Checks gehören in `math`; verifizierte reale Datenprüfungen in `data`.

Nach Prüfung der aktuellen Runner-CLI mindestens:

```bash
python scripts/run_verification_suite.py --category all
python scripts/run_verification_suite.py --category links
```

**Abnahme:** alle geforderten Kontrollfälle bestehen; Regression und Links dokumentiert; vorhandene Schätzmodule unverändert oder jede Änderung separat begründet; keine ungetestete Behauptung der globalen Identifizierbarkeit. MU6-Realdaten dürfen offen bleiben, ohne dass MU0–MU7 pauschal als vollständig reale Validierung bezeichnet werden.

## 11. Unabhängige Kontrollsammlung

Das Begleitskript `independent_controls.py` importiert weder SCF noch einen Optimierer. Es enthält 17 MU-Kontrollgruppen und 12 Kontrollgruppen zum Kandidatendokument. Es ist eine ausführbare Herleitungshilfe, **kein Ersatz für Tests der späteren Produktionsimplementierung**. Nicht einfach seine Funktionen in die Produktion kopieren und anschließend gegen dieselbe Rechnung testen.

| Kontrolle | Unabhängiger Sollwert / Zweck |
|---|---|
| MU-C01 | δ=1/10 → η=2/21 |
| MU-C02 | z(2T)−2z(T)+z(0)=aT², exakt rational |
| MU-C03 | Tabelle der SI-Referenzwerte |
| MU-C04 | exp(−4); bedingtes Optimum T=2τ |
| MU-C05 | Einheitenwechsel invariant; 1 % v-Fehler → 2,01 % a-Fehler |
| MU-C06 | E[1/v²]=5/8 ≠ 1/E[v]²=4/9; kontrastlose Gegenphasen |
| MU-C07 | Überleben 1/4 und 1/2 → detektierte Gewichte 1/3 und 2/3 |
| MU-C08 | Poisson-Nullfälle; Deviance gleich zweimal NLL-Differenz zum gesättigten Modell |
| MU-C09 | Entfaltete Phase: Rang 1 bzw. 2; A=1,b=2 aus p=(3,6) |
| MU-C10 | Drei Parameter, Rang 2 trotz mehrerer Flugzeiten |
| MU-C11 | Gerader Offset verschwindet, ungerader Bias bleibt |
| MU-C12 | Iφ=8 bzw. 16 bei gleicher Ereigniszahl |
| MU-C13 | Ereignisbedarf und äquivalenter Gitterversatz unter Idealannahmen |
| MU-C14 | Exakte periodische Mehrdeutigkeit mit Δa=d/T² |
| MU-C15 | Vorzeichen der Quadratur; lokale statt globale arcsin-Inversion |
| MU-C16 | Kein Kontrast → keine Beschleunigungsinformation |
| MU-C17 | Kommensurable Flugzeiten behalten gemeinsame Aliasse |

Ausführen:

```bash
python independent_controls.py --output independent_control_results.json
```

Bei Erstellung bestanden **29/29 Kontrollgruppen**. Es wurde dabei kein Produktionsmodul des Repos getestet, keine Konfidenzintervall-Abdeckung simuliert und kein echter Myonium-Datensatz ausgewertet. Genau diese weiteren Leistungen muss Claude in den genannten Paketen nachholen.

## 12. Startauftrag für Claude-Code

> Setze MU0–MU7 dieses Plans additiv im aktuellen SCF-Repo um. Beginne mit Quellen- und API-Inventar sowie unabhängigen Handrechnungen. Behalte die Trennung von Strahlquelle, Messoperator und Gravitationsevidenz bei. Verwende den vorhandenen epistemischen und Identifizierbarkeits-Anschluss, soweit seine tatsächlichen APIs passen. Prüfe periodische Aliasse, Störparameter und Selektion ausdrücklich. Arbeite paketweise mit Regression und dokumentierten Grenzen. Reale Daten nur nach dem bestehenden Provenienzprotokoll; ein blockierter Datenzweig darf die synthetischen und analytischen Pakete nicht verhindern und darf nicht als bestandene reale Validierung erscheinen. Die drei zusätzlichen Themen aus der Kandidatenbewertung sind eigenständige Optionen und gehören nicht automatisch in diesen Implementierungsauftrag.
