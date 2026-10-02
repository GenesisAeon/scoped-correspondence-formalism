# SCF: Geltungsbereiche, Komposition und belastbare Evidenz

## Eigenständiger Implementierungsplan für Claude-Code — J0 bis J12

**Projekt:** GenesisAeon / scoped-correspondence-formalism  
**Für:** Johann Benjamin Römer  
**Stand:** 27. September 2026  
**Geprüfter Referenzcommit:** `4a7ed38640ac7d393017eb5556291c879c3bceac`  
**Repository:** <https://github.com/GenesisAeon/scoped-correspondence-formalism>  
**Dokumentation:** CC BY 4.0; begleitender Prüfcode: GPL-3.0-or-later.

Dieser Plan macht aus den vorgeschlagenen Erweiterungen einen umsetzbaren Ausbau des vorhandenen SCF. Er enthält den Pflichtumfang, mathematische Definitionen, vorgeschlagene Schnittstellen, unabhängig berechnete Kontrollwerte, negative Kontrollen, Quellen und Abschlusskriterien. Die neuen API-Namen sind **Vorschläge**, keine Behauptung über bereits existierenden Code.

Als Grundlage dienen die im Gespräch vorliegende Zusammenfassung des Formalismenberichts, die am Referenzcommit überprüften SCF-Schnittstellen und die unten verzeichneten Primärquellen. Eine vollständige Prüfung sämtlicher 33 Kandidaten des ursprünglichen Berichts wird damit nicht behauptet. Dieser Plan ist selbstständig verwendbar; Claude benötigt weder das frühere Gespräch noch den ursprünglichen Bericht.

**Lieferstatus dieses Dokuments:** Implementierungsvorgabe, keine bereits implementierte Erweiterung. Die beigefügten 23 Kontrollgruppen wurden unabhängig von SCF ausgeführt. Das ist keine neue SCF-Regression und kein Nachweis eines grünen Repository-CI-Laufs.

---

## 1. Direktauftrag an Claude-Code

> Lies diesen Plan vollständig und anschließend die aktuellen Arbeitsregeln des Repositorys. Prüfe zuerst den tatsächlichen Arbeitsstand, den Branch und eventuell vorhandene Änderungen. Verifiziere die unten genannten bestehenden APIs am aktuellen Commit. Leite alle Kontrollgruppen J-C01 bis J-C23 selbst her; der beigefügte Code ist eine zusätzliche unabhängige Referenz, kein Ersatz für diese Prüfung.
>
> Implementiere den Pflichtumfang J0–J12 paketweise. Beginne mit einer separat eingecheckten Roadmap, einer verifizierten API-Tabelle mit tatsächlichen Datei-/Zeilenangaben und der Kontrollfalltabelle. Verwende bestehende SCF-Module, bevor du ähnliche Funktionalität neu schreibst. Ein Paket pro Commit; für jedes Paket Dokumentation, gezielte Positiv- und Negativprüfungen, bisherige Prüfungen dieses Plans, vollständige Regression und Linkprüfung nach `CLAUDE.md`.
>
> Ein mathematisch nicht entscheidbarer oder vom aktuellen Verfahren nicht entschiedener Fall ist ein zulässiges Ergebnis. Budgetabbruch, ungültige Eingabe, gescheiterte Anwendbarkeit und tatsächliches Gegenbeispiel bleiben unterscheidbar. Beschreibe genau, was bewiesen, numerisch untersucht oder empirisch ausgewertet wurde.
>
> Die begrenzten endlichen Kausalmodule J9/J10 gehören zum beauftragten Kern dieses Plans. Die ausdrücklich als optional markierten allgemeinen Solver, neuen Datenerhebungen und zusätzlichen Forschungsprogramme gehören nicht dazu. Halte sie als offene Erweiterungen fest. Führe Commit/Push nur im jeweils autorisierten Implementierungsworkflow durch; dieses Dokument selbst verändert keine Berechtigungen und verlangt keine Änderung fremder Arbeitsstände.

## 2. Ziel und wissenschaftlicher Gewinn

SCF soll eine konkrete Aussage beantworten können:

> Unter welchen Annahmen, auf welchem Bereich und mit welchem Fehler darf eine Beziehung zwischen Modellen verwendet, verkettet oder auf einen anderen Kontext übertragen werden?

Der nächste Ausbau verbindet vorhandene Mathematik mit prüfbaren Geltungsbereichen. Er erweitert das System in drei Richtungen:

1. **Strukturell:** typisierte Größen, explizite Bereiche, Verfeinerung und kompatible Verkettung.
2. **Evidenziell:** Nachweise über ganze unterstützte Bereiche; Identifizierbarkeit und statistische Unsicherheit ohne Vermischung mit Modellwahrheit.
3. **Kausal:** endliche Eingriffsmodelle, überprüfbare Abstraktion und eine begrenzte Transportregel mit ausgewiesenen Voraussetzungen.

Das passt zur ursprünglichen SCF-Idee: Gemeinsame mathematische Strukturen dürfen untersucht werden, ohne die beteiligten Gegenstände gleichzusetzen. Eine Dimensionsübereinstimmung, ein kleiner Residualfehler und ein empirischer Prognoseerfolg beantworten dabei verschiedene Fragen.

### 2.1 Korrekturen gegenüber einer zu pauschalen Lückenbeschreibung

| Ausgangsaussage | Präzisierung für die Implementierung |
|---|---|
| „Korrespondenzen haben keine Algebra.“ | T4 und eine Kompositionsfehlerschranke sind bereits vorhanden. Es fehlen vor allem maschinenprüfbare Voraussetzungen, Bereichsverträglichkeit und die Integration in ein wiederverwendbares Ergebnisformat. |
| „Scope ist nur ein Punkttest.“ | `Scope.contains` ist ein Mitgliedschaftstest. Das ist sinnvoll, aber kein Nachweis einer universellen Aussage über ein Kontinuum. Dieser zusätzliche Nachweistyp wird ergänzt. |
| „Gewichtetes Conformal liefert bei Drift ehrliche Abdeckung.“ | Der Pflichtumfang behandelt Covariate Shift mit unverändertem $Y\mid X$, korrekten Dichteverhältnissen und passender Stichprobenstruktur. Beliebiger zeitlicher Drift ist davon nicht abgedeckt. |
| „DM zeigt, ob ein Modell wirklich gewinnt.“ | DM ist eine bedingte Inferenz über gepaarte Verlustdifferenzen unter Zeitreihenannahmen. Effektgröße, Untersuchungsdesign und praktische Bedeutung bleiben eigenständige Größen. |
| „MOND mit null und Halos mit zwei Parametern sind nicht vergleichbar.“ | Ein sauber gehaltener Testvergleich ist bereits sinnvoll. Unterschiede der Flexibilität können sich im Testfehler zeigen; ein nachträglicher pauschaler Parameterabzug auf Testverluste ist nicht gerechtfertigt. |
| „Strukturelle Identifizierbarkeit fehlt völlig.“ | Es gibt bereits Symmetrie-, Rang- und Profilbeispiele. Neu sind eingeschränkte exakte Verfahren, explizite lokale/globale Aussagen und konsistente Ergebnisberichte. |
| „Reduktion mit Fehlergarantie ist ein neues Gebiet.“ | Markov-Reduktionsschranken existieren. J11 integriert sie in die Vertragsstruktur; es baut keinen zweiten Solver daneben. |

### 2.2 Ausdrückliche Grenzen

Der Pflichtumfang verspricht keine automatische physikalische Theorieentdeckung, keine Zertifizierung beliebiger Python-Funktionen, keine allgemeine kausale Identifikation aus Beobachtungsdaten und keinen universellen Transportabilitätsalgorithmus. Er liefert auch keine neue astrophysikalische Skala und keinen Beleg für eine kosmologische Hypothese.

Ein Resultat kann innerhalb eines mathematischen Modells exakt sein, während die Anwendbarkeit dieses Modells auf ein reales System offenbleibt. Diese Trennung muss in der API und in den veröffentlichten Ergebnissen sichtbar sein.

## 3. Bereits vorhandene Anschlüsse

Die folgenden Pfade und Funktionen wurden für den Referenzstand abgeglichen. Claude ergänzt in J0 die aktuellen Zeilennummern und notiert Änderungen gegenüber diesem Stand. Veraltete Zeilennummern werden hier bewusst nicht als aktuelle Referenzen ausgegeben.

| Bestehender Ort | Anschluss | Verwendung im Ausbau |
|---|---|---|
| `src/scoped_correspondence/correspondence/contract.py` | `ModelRef`, `StateMap`, `TimeMap`, `Scope`, `Correspondence` | Bestehende Objektwelt erhalten; zusätzliche Verträge und Bereichsbeschreibungen daneben. |
| derselbe Pfad | `t4_composition_residual` | Referenz für die Kompositionsidentität von Vektorfeldresiduen. |
| `context_transformations.md` | T4 und Schranke $M\varepsilon_1+A\varepsilon_2$ | Vorhandene Herleitung präzisieren und implementierbar machen. |
| `correspondence/approximation.py` unter `src/scoped_correspondence/` | `ApproximationCertificate`, `verify_approximate_simulation` | Stichprobenzertifikate weiterhin als Stichproben kennzeichnen. |
| `correspondence/controlled_markov.py` | `check_controlled_correspondence` | Aktionsweise Bedingung $P^aC=CQ^{\omega(a)}$, Zeilenkonvention. |
| `closure/error_bounds.py` | `transient_reduction_bound`, `stationary_reduction_bound`, `compare_to_propagated_error_bound` | Bestehende L1-Reduktionsschranken anschließen. |
| `identifiability/core.py` | `parameter_scaling_invariance`, `identifiability_jacobian_rank` | Bestehende Symmetrie- und Rangbeispiele behalten; Aussageumfang erweitern. |
| `dynamics/linear_reservoirs.py` | Exakte lineare Reservoirentwicklung | Kontrollfall für Einheiten, Identifizierbarkeit und Modellreduktion. |
| `validation/rolling_origin.py` | `RawHorizonPrediction`, `raw_predictions_by_horizon_step`, `rolling_origin_backtest` | Gepaarte Rohvorhersagen statt Tests auf aggregierten RMSE-Werten. |
| `validation/scoring_rules.py` | Intervall-, Poisson- und NB-Scores | Vorzeichenkonvention und passende Verluste wiederverwenden. |
| `validation/conformal.py` | Split-Conformal-Kalibrierung | Gewichtete Quantile ergänzen, bestehende Logik nicht duplizieren. |
| `validation/galaxy_pilot.py` | `evaluate_baselines_on_holdout`, Sensitivitätsfunktionen für Modus A/B | Gemeinsame Störparameter, refit nur auf Trainingsradien, gleiche Testpunkte. |
| `epistemic/records.py` und weitere H-Module | Evidenzarten, endliche Audits, Beobachtungsfasern, Entscheidungsvergleiche | Adapter und gemeinsame Darstellung; keine Umdeutung kontinuierlicher Mengen in endliche Kandidatenlisten. |
| `scripts/run_verification_suite.py` | `_EXPLICIT_CATEGORY`; Kategorien math/data/all/links | Jede neue Prüfung ausdrücklich registrieren. |
| `docs/real_data_provenance.md` | Datenherkunft, Abruf, Hash, Lizenz | Gilt für neue Realdaten ebenso wie für vorhandene Piloten. |

Prüfe zusätzlich die bereits vorhandenen adaptiven Conformal-, Profil-Likelihood-, Fisher-Informations- und Reduktionsmodule, bevor neue Dateinamen endgültig festgelegt werden. In diesem Plan relativ angegebene Modulpfade beziehen sich auf `src/scoped_correspondence/`.

## 4. Reihenfolge und Paketgrenzen

| Phase | Paket | Konkretes Ergebnis | Abhängigkeiten |
|---|---|---|---|
| A — Aussagen absichern | J0 | Bestandsaufnahme, Roadmap, Quellen- und Kontrollfallregister | keine |
| A | J1 | Gepaarte Prognosevergleiche mit bedingter Inferenz | J0 |
| A | J2 | Dimensionsprüfung und Buckingham-Π-Basis | J0 |
| A | J3 | Metamorphe Prüfungen und gezielte Fehlermutationen | J1/J2; später fortschreiben |
| B — SCF-Kern | J4 | Bereiche, Verträge, Verfeinerung, Komposition | J2 |
| B | J5 | Exakte Intervallnachweise für unterstützte Ausdrücke | J4 |
| C — Unsicherheit | J6 | Begrenzte strukturelle Identifizierbarkeit | J2/J4 |
| C | J7 | Gemeinsame Sensitivität und Unsicherheit der Modellvergleiche | J1/J6 |
| C | J8 | Gewichtetes Split Conformal bei Covariate Shift | J1/J2 |
| D — Eingriffe und Übertragung | J9 | Endliche SCMs und interventionelle Abstraktion | J4; bestehende epistemische Module |
| D | J10 | Geprüfte Standardisierung zwischen Umgebungen | J9 |
| E — Integration | J11 | Vorhandene Reduktionsschranken als Verträge | J4/J5 |
| E | J12 | CLI, Fähigkeitsbilanz, Abschlussregression | alle Pflichtpakete |

Die Abhängigkeiten sind wichtiger als die Nummernfolge. J11 kann nach J5 bearbeitet werden, sofern die Roadmap die Reihenfolge nachvollziehbar dokumentiert. Der kleinste eigenständig wertvolle Meilenstein ist J0–J5: Er verbessert den Kern auch ohne die späteren Kausalmodule.

**Planungsregel:** keine Kalenderdauer erfinden. Fortschritt wird an erfüllten Abnahmekriterien gemessen. Wenn ein Paket größer wird, in Unterpakete mit eigenem Status teilen; den Umfang nicht unbemerkt reduzieren.

## 5. Ergebnissemantik für alle Pakete

### 5.1 Getrennte Achsen

Neue Berichte müssen mindestens folgende Informationen sinnvoll abbilden:

| Achse | Inhalt |
|---|---|
| Aussage | Behauptung, Quantoren, Eingänge, Zielgröße und mathematische Bedeutung. |
| Bereich | Deklarierter Bereich, geprüfter Bereich, Zeitintervall, Eingriffsmenge. |
| Annahmen | Explizite Voraussetzungen mit Herkunft: vorgegeben, hergeleitet oder empirisch gestützt. |
| Verfahrensstatus | abgeschlossen, Budget erschöpft, ungültige Eingabe, nicht unterstützte Struktur, numerischer Fehler. |
| Urteil | bewiesen / widerlegt / unentschieden innerhalb des angegebenen Aussageumfangs. Stichproben können zusätzlich `observed_pass`/`observed_fail` berichten. |
| Evidenz | Vorhandene SCF-Evidenzart plus genaueres Verfahren und Nachweisobjekt. |
| Arithmetik | exakte rationale Rechnung, validierte Einschließung oder Gleitkommaschätzung. |
| Empirie | nicht geprüft, nur synthetisch geprüft oder auf deklarierten Daten ausgewertet. |
| Vollständigkeit | Vollständigkeit der Schlussfolgerung getrennt von vollständigem Durchlaufen aller Kandidaten. |
| Zeugen | Gegenbeispiel, zwei ununterscheidbare Modelle, Restboxen oder andere überprüfbare Belege. |

Ein gefundenes Gegenbeispiel kann die Widerlegung bereits abschließen, obwohl nicht der ganze Bereich abgesucht wurde. Ein Budgetabbruch ohne Gegenbeispiel beweist dagegen nichts Universelles. Ein leeres Gebiet macht eine All-Aussage logisch vakuos; es ist keine praktisch verwendbare Garantie. Leere Bereiche müssen deshalb ausdrücklich markiert werden.

### 5.2 Technische Umsetzung ohne große Migration

Schlage ein kleines Modul `assurance/records.py` mit einem `ProofReport` und einem `ClaimBundle` als typisierter Sammlung vor. Der genaue Name kann nach Bestandsprüfung angepasst werden. Bestehende H-Berichte behalten ihre Semantik und werden über Adapter referenziert. Kein globaler Umbau sämtlicher vorhandener Dataclasses als Voraussetzung dieses Plans.

Ein `ProofReport` darf die logische Aussage, die unterstützte Ausdrucksklasse, die Methode und die Nachweisabhängigkeiten speichern. Bei Intervallnachweisen gehören Boxpartition und rationale Einschließungen dazu. Eine Zertifikats-ID oder ein Hash identifiziert den Inhalt; sie beweist nicht seine Wahrheit.

JSON muss endlich und standardskonform bleiben: `NaN` und nichtstandardmäßiges `Infinity` nicht als Zahlen ausgeben. Unbeschränkte Intervalle erhalten beispielsweise `{"kind":"whole_real_line"}`; exakte Brüche bekommen Zähler/Nenner oder eine dokumentierte rationale Zeichenkette. `null` bedeutet fehlend, nicht automatisch „unendlich“ oder „falsch“.

## 6. J0 — Bestandsaufnahme und reproduzierbarer Start

**Ziel:** Ein geprüfter Implementierungsstart verhindert Doppelentwicklungen und übernommene Fehler aus dem Plan.

**Dateien:** `SCOPE_COMPOSITION_EVIDENCE_ROADMAP.md`, `docs/scope_composition_design.md`; ein Quellenregister in einem dieser Dokumente reicht zunächst aus.

**Arbeitsschritte:**

1. Aktuellen Commit, Branch, Python-Version und relevante Paketversionen erfassen. Vorhandene Änderungen erhalten.
2. Tabelle aus Abschnitt 3 am aktuellen Code bestätigen; aktuelle Signaturen und Zeilenangaben ergänzen. Abweichungen sichtbar auflösen.
3. Alle J-C-Kontrollen ohne SCF-Import unabhängig nachrechnen. Bei Abweichungen zuerst Kontrollfall/Plan klären, dann erst Produktionscode schreiben.
4. Bestehende Tests und Laufzeiten feststellen; keinen Testzähler aus dem Gespräch als aktuellen Befund übernehmen.
5. Pfade, Ergebnisfelder und optionale Abhängigkeiten festlegen. Standardbibliothek plus vorhandenes NumPy/SciPy genügen für den Pflichtkern.
6. Roadmap allein als erstes Paket abschließen. Noch keine neuen Produktionsmodule in diesen Commit mischen.

**Abnahme:** bestätigte Schnittstellentabelle, alle 23 Kontrollgruppen dokumentiert, Quellenstatus pro Referenz, Paketstatus und explizite Liste optionaler Arbeiten. Ein unbekannter aktueller CI-Status bleibt unbekannt, bis er tatsächlich überprüft wurde.

## 7. J1 — Gepaarte Prognosevergleiche

### Ziel und Datenvertrag

Neue Datei etwa `validation/forecast_comparison.py`. Ergänze einen Adapter um `RawHorizonPrediction`; ersetze nicht die bisherigen Backtest-Berichte.

Vorgeschlagenes `PairedForecastRecord` enthält mindestens `series_id`, `origin`, `target_time`, `horizon`, beobachteten Wert, beide Vorhersagen, Modell-/Fit-IDs und Daten-/Split-IDs. Für jeden Vergleich müssen beide Vorhersagen dieselbe Beobachtung mit demselben Horizont und derselben verfügbaren Informationsmenge betreffen.

Ein Join darf fehlende Partner nicht unbemerkt entfernen. Berichte Anzahl angefragter, gepaarter, ausgeschlossener und ungültiger Punkte mit Gründen. Unterschiedliche Beobachtungswerte unter derselben ID sind ein Eingabefehler.

### Mathematischer Kern

Für eine vorab festgelegte Verlustfunktion sei

\[
d_t=L(y_t,\hat y_{A,t})-L(y_t,\hat y_{B,t}).
\]

Negative mittlere Differenzen sprechen im ausgewerteten Design für A. Für chronologisch geordnete, regelmäßig interpretierbare Differenzen kann die langfristige Varianz mittels Bartlett-HAC geschätzt werden:

\[
\widehat\gamma_\ell=\frac1n\sum_{t=\ell+1}^n(d_t-\bar d)(d_{t-\ell}-\bar d),\quad
\widehat V=\widehat\gamma_0+2\sum_{\ell=1}^{L}\left(1-\frac{\ell}{L+1}\right)\widehat\gamma_\ell,
\quad DM=\frac{\bar d}{\sqrt{\widehat V/n}}.
\]

Die Normalreferenz ist asymptotisch. Die Anwendung setzt insbesondere geeignete Stationarität/Abhängigkeit und Momente der Verlustdifferenzen voraus. Eine empirische Diagnose kann diese Annahmen nicht beweisen. DM ist keine generelle Auswahlprüfung für jedes geschätzte oder verschachtelte Modell. [S01–S03]

### Verbindliche Implementierungsregeln

- API etwa `compare_paired_forecasts(..., loss, hac_lag, applicability)`; Verlust, Horizont und Lagwahl werden gespeichert.
- Ergebnisse enthalten mittlere Differenz, Stichprobengröße, Standardfehler, Intervall und gegebenenfalls asymptotischen p-Wert. Ohne begründete Anwendbarkeit bleiben inferenzielle Felder leer und der deskriptive Vergleich erhalten.
- Überlappende Horizonte nicht als unabhängige Beobachtungen ausgeben. Pro Horizont eine geeignete Serie bilden; Lagwahl begründen. `h-1` ist keine universell ausreichende Wahl für jede Abhängigkeitsstruktur.
- Verschiedene Flusseinzugsgebiete oder Galaxien nicht zu einer künstlichen Zeitreihe aneinanderhängen. Mehrere Serien zunächst einzeln und in einer transparenten Übersicht berichten.
- Bei Strukturbrüchen, sehr kurzen Reihen, unklarer zeitlicher Ordnung oder verschachtelten Modellen keine automatische DM-Freigabe. Ein zusätzlicher Blockbootstrap wäre ein gesondert spezifiziertes Verfahren, kein universeller Ersatz.
- Bei null oder numerisch unbrauchbarer Varianz `degenerate_variance`; nicht `p=0`, kein automatischer sicherer Sieger.
- Für eine vorab deklarierte Familie mehrerer Tests Holm-Korrektur anbieten. Explorative Nachauswahl der besten von vielen Konfigurationen wird durch einen einzelnen p-Wert nicht repariert.
- „Kein signifikanter Unterschied“ bedeutet nicht nachgewiesene Gleichwertigkeit. Eine Äquivalenzprüfung mit praktischer Toleranz ist eine spätere eigene Funktion.

### Kontrollen und Pilot

**J-C01:** Für $d=(-1,0,1,2)$, $L=1$: Mittel $1/2$, $\gamma_0=5/4$, $\gamma_1=5/16$, $\widehat V=25/16$, Standardfehler $5/8$, DM $4/5$. Das ist ein Arithmetiktest, keine Rechtfertigung einer asymptotischen Anwendung bei vier Punkten.

**J-C02:** Rohe p-Werte $(0.01,0.04,0.03)$ ergeben in Originalreihenfolge Holm-Werte $(0.03,0.06,0.06)$. [S04]

Weitere Pflichtprüfungen: Modelltausch kehrt Vorzeichen um; positive Skalierung aller Verluste ändert DM nicht; konstante Differenzen; falsche Paarung; fehlende Partner; verschiedene Horizonte; ungültige Zahlen; vorab deklarierte Testfamilie.

Ein vorhandener ausreichend langer Realdatenpilot wird angeschlossen, vorzugsweise ein klar definiertes Hydrologie- oder Energiebilanzexperiment. Falls dessen Design die Inferenzannahmen nicht trägt, ist das korrekte Ergebnis eine deskriptive Auswertung mit dokumentierter Grenze. Es besteht keine Pflicht, einen signifikanten Erfolg zu erzeugen.

**Abnahme:** `verify_forecast_comparison.py` als math; vorhandener Datenadapter gegebenenfalls separates data-Skript. Jede veröffentlichte Siegerformulierung benennt Population/Zeitraum, Horizont, Verlust, Effektgröße und Inferenzstatus.

## 8. J2 — Dimensionen, Einheiten und Buckingham Π

**Dateien:** etwa `dimensions/core.py`, `dimensions/pi_groups.py`, `docs/dimensional_correspondence.md`.

### Umfang

Implementiere Dimensionsvektoren mit rationalen Exponenten und eine exakte Nullraumberechnung der Dimensionsmatrix. Einheitenfaktoren und Dimensionen sind verschieden: Meter und Kilometer haben dieselbe Dimension, aber andere numerische Skalen. Zusätzlich kann eine semantische Größenart, etwa Energie oder Drehmoment, angegeben werden. Gleiche Dimension allein begründet keine Austauschbarkeit.

Für $n$ Größen und Dimensionsmatrix $D$ liefert jeder Vektor $v\in\ker D$ ein dimensionsloses Monom $\Pi=\prod_jq_j^{v_j}$. Die Anzahl unabhängiger Gruppen ist $n-\operatorname{rang}D$. Unterschiedliche Nullraumbasen sind gleichberechtigt; Tests dürfen nicht zufällige Basisschreibweisen festschreiben. Der Satz liefert keine Dynamik und keinen universellen Zahlenfaktor. [S05]

**Vorgeschlagene API:** `Dimension`, `QuantitySpec`, `check_dimension(expression)`, `buckingham_pi_basis(specs)`.

### Kontrollen

**J-C03:** Variablen $(T,l,g)$, Zeilen Länge/Zeit:

\[
D=\begin{pmatrix}0&1&1\\1&0&-2\end{pmatrix},\qquad
v=(2,-1,1),\qquad \Pi=gT^2/l.
\]

Rang zwei, Nullität eins. Außerdem hat $g/G$ die Dimension $M/L^2$. Das legt weder einen Zahlenwert noch eine bestimmte physikalische Deutung der Oberflächendichte fest.

**J-C04:** Für das Reservoir $M'=q-kM$ bleibt die exakte Lösung unter Jahr→Tag erhalten, wenn $t_d=365t_y$, $k_d=k_y/365$, $q_d=q_y/365$. Testfall $M_0=3,q_y=5,k_y=2,t_y=0.4$. Eine Umparametrisierung $\rho'=\rho/\lambda,r'=\lambda r$ erhält $\rho r$; daraus folgt keine Erhaltung jeder anderen Halo-Observable.

Pflichtprüfungen: Addition verschiedener Dimensionen ablehnen; Argumente von exp/log dimensionslos; rationale Exponenten; singuläre/leerwertige Matrizen mit dokumentierter Semantik; Änderung der Basis; Einheitentransformation; Energie versus Drehmoment als semantische Warnung. Affine Temperaturskalen nicht als reine multiplikative Einheiten behandeln. Eine bewusst abstrakte dimensionslose SCF-Größe bekommt keine erfundene SI-Einheit.

**Abnahme:** exakte Dimensionsprüfung und Π-Basis, API-Dokumentation, `verify_dimensional_analysis.py`; mindestens ein Anschluss an Reservoir- und ein Anschluss an Galaxiengrößen.

## 9. J3 — Metamorphe Prüfungen und gezielte Fehlermutationen

**Ziel:** Nachweisen, dass wichtige Verifikation tatsächlich relevante Fehler entdeckt. Keine globale Mutation aller Dateien und kein Ausbau zu einem eigenen Testframework.

**Dateien:** `verification/verify_metamorphic_relations.py`, `scripts/run_targeted_mutations.py`, `docs/metamorphic_validation.md`.

Metamorphe Prüfungen vergleichen Ergebnisse unter bekannten Transformationen, wenn einzelne Zielwerte schwer vorzugeben sind. Die Relation selbst braucht mathematische Begründung. [S06]

Verbindliche Relationen:

- Einheitenwechsel aus J-C04 und gleichzeitige Permutation von Markov-Zuständen/Partitionen.
- Identität und zulässige Assoziation von Korrespondenzen.
- A/B-Tausch im Prognosevergleich.
- Gemeinsame positive Skalierung aller Conformal-Gewichte.
- Vertauschung unabhängiger Sobol-Eingänge samt Ergebnisetiketten.
- Umbenennung von SCM-Variablen und konsistente Umbenennung der Eingriffe.

Der Mutationslauf arbeitet ausschließlich auf einer temporären Kopie oder einem isolierten Worktree. Mutation, Zielprüfung, erwartete Fehlerwirkung und Rücksetzung stehen im Bericht. Mindestens sechs gezielte Mutanten: Ungleichung umdrehen; Zeitfaktor in T4 entfernen; Lipschitzfaktor entfernen; Testpunktmasse bei Conformal weglassen; Faktor zwei bei TV/L1 verwechseln; Scope-Verträglichkeit umgehen. Die letzten Mutanten werden mit den entsprechenden späteren Paketen aktiviert.

Ausgabe getrennt nach `killed`, `survived`, `invalid`, `timeout`, `equivalent_or_unresolved`. Syntaxfehler und nicht ausführbare Mutanten gelten nicht als erfolgreicher mathematischer Fehlernachweis. Äquivalente Mutanten nicht heimlich in den Nenner aufnehmen. Ein hoher Mutationsanteil ist keine Vollständigkeitsgarantie.

**Abnahme:** gezielter Basissatz bei J3, vollständiger vereinbarter Satz bei J12; jede unentdeckte Mutation führt zu einer begründeten Testergänzung oder wird mit ihrer Nichtrelevanz dokumentiert. Keine mutierte Produktionsdatei bleibt im Arbeitsbaum.

## 10. J4 — Bereichsverträge, Verfeinerung und Komposition

### 10.1 Unterstützte Bereiche

**Dateien:** etwa `correspondence/domains.py`, `correspondence/contracts.py`, `correspondence/composition.py`.

Erste Version unterstützt explizite endliche Mengen und rationale achsenparallele Boxen. Opaque Prädikate bleiben nutzbar für Punktprüfungen, liefern aber ohne zusätzlichen Nachweis keine universelle Inklusion. Exakte affine Abbildungen dürfen Bilder/Urbildbedingungen berechnen; komplexere Abbildungen können J5 verwenden.

Vorgeschlagene Funktionen: `domain_contains`, `certify_subset`, `preimage_constraint`, `compose_correspondences`, `check_refinement`. Eine resultierende Schnittmenge muss nicht wieder eine Box sein. Erhalte nötigenfalls die Bedingung symbolisch, nutze eine ausgewiesene innere/äußere Approximation oder liefere `unsupported`; ersetze sie nicht still durch eine zu große Box.

Unterscheide **Anfangszustandsbereich** und **Bereich einer ganzen Trajektorie**. Aus $x_0\in D$ folgt nicht, dass die Bewegung in $D$ bleibt. Die Invarianz eines Gebiets ist eine eigene Voraussetzung bzw. ein eigenes Zertifikat.

### 10.2 Funktionaler Vertrag

Ein Vertrag beschreibt einen Annahmebereich $A$ und eine Garantie $G$, beispielsweise eine Fehlergrenze unter einer Metrik. Verfeinerung bedeutet im hier implementierten funktionalen Spezialfall: Die Implementierung akzeptiert mindestens alle spezifizierten Eingaben und erfüllt dort mindestens die spezifizierte Garantie. Die umfassende Theorie reaktiver Assume–Guarantee-Verträge wird damit nicht vollständig implementiert. [S07]

Für $T_1:A\to B$ und $T_2:B\to C$ ist der zulässige Anfangsbereich grundsätzlich

\[
D_{12}=D_1\cap T_1^{-1}(D_2).
\]

Hinzu kommen gegebenenfalls Bedingungen an Parameter, Kontexte, Zeithorizonte und erreichte Zustände. Gleiche Modellnamen sind kein Kompatibilitätsbeweis: Modellidentität bzw. explizite Verbindung, Zustandskoordinaten, Größenarten und Uhren müssen passen.

### 10.3 Zwei verschiedene Fehlerrechnungen

**Flussfehler:** Für die tatsächlichen Flüsse $\Phi_A,\Phi_B,\Phi_C$ und positive konstante Zeitfaktoren $c_1,c_2$ seien passende Fehlergrenzen $\delta_1(t),\delta_2(s)$ bekannt. Ist $T_2$ auf dem relevanten Gebiet einschließlich der notwendigen Verbindungsstrecken $L_2$-Lipschitz, dann gilt

\[
\delta_{12}(t)\le L_2\delta_1(t)+\delta_2(c_1t).
\]

Die zweite Flussfehlergrenze wird zeitlich ausgewertet, aber nicht zusätzlich mit $c_1$ multipliziert. Dies folgt unmittelbar aus Dreiecksungleichung und Lipschitzbedingung.

**Vektorfeldresiduen:** Mit

\[
r_1=DT_1f_A-a_1(f_B\circ T_1),\qquad
r_2=DT_2f_B-a_2(f_C\circ T_2)
\]

gilt dagegen

\[
r_{12}=(DT_2\circ T_1)r_1+a_1(r_2\circ T_1),\qquad
\|r_{12}\|\le M\varepsilon_1+A\varepsilon_2.
\]

Hier beschränkt $M$ den Operatornormfaktor und $A$ den Betrag von $a_1$. Das ist der bereits vorhandene T4-Anschluss. Ein kleines Vektorfeldresiduum ist ohne zusätzliche Dynamikabschätzung noch keine gleich große Flussabweichung.

Die erste Implementierung komponiert positive konstante Zeitfaktoren. Zustandsabhängige Zeitabbildungen verbleiben in den vorhandenen Punkt-/Numerikroutinen; ein allgemeiner verifizierter Kompositionsnachweis dafür ist optional und braucht eine eigene Herleitung.

### 10.4 Handkontrollen

**J-C05:** $T_1(x)=2x,D_1=D_2=[0,1]$. Zulässiger Kompositionsbereich $[0,1/2]$. $x=3/4$ liefert $T_1x=3/2\notin D_2$.

**J-C06:** $f_A=-x,f_B=-2y,f_C=-4z,T_1=2x,T_2=3y,c_1=c_2=1/2$. Exakte Korrespondenzen, zusammengesetzter Zeitfaktor $1/4$. Bei Horizont $H_1=4$ in A-Zeit und $H_2=1$ in B-Zeit gilt $H_{12}=\min(H_1,H_2/c_1)=2$.

**J-C07:** Flussgrenzen $L_2=3,\delta_1=1/10,\delta_2=1/5$ ergeben $1/2$. Separater Vektorfeldfall: $T_1=2x,T_2=3y,f_A=x,f_B=0,f_C=-1,a_1=2,a_2=3$. Dann $r_1=2x,r_2=3,r_{12}=6x+6$. Auf $[0,1/2]$ ist die Schranke $3\cdot1+2\cdot3=9$, am Rand erreicht. Bei $x=1/4$ ist das Residuum $15/2$.

**J-C08:** Spezifikation: Bereich $[0,1]$, Fehler höchstens $1/5$. Implementierung: Bereich $[-1,2]$, Fehler höchstens $1/10$. Verfeinerung gilt; die umgekehrte Richtung gilt nicht.

Weitere Pflichtprüfungen: inkompatible Zwischenmodelle, Einheiten, Uhren oder Metriken; leere Schnittmenge; fehlender Lipschitznachweis; positive/negative Skalen; Identität; Assoziativität der exakten Abbildungen und Gleichwertigkeit der daraus entstehenden Scope-Bedingungen. Unterschiedliche konservative Fehlerabschätzungen verschiedener Klammerungen dürfen verschieden sein, ohne die Abbildungsassoziativität zu verletzen.

**Abnahme:** `verify_correspondence_contracts.py` mit exakten Kontrollen, expliziten Nichtentscheidungen und nachvollziehbaren Beweisabhängigkeiten.

## 11. J5 — Nachweise über ganze unterstützte Bereiche

### 11.1 Kleiner rigoroser Kern

**Dateien:** etwa `assurance/rational_intervals.py`, `assurance/expressions.py`, `assurance/scope_certification.py`, `docs/validated_scopes.md`.

Für die erste Version ist keine neue numerische Bibliothek nötig: rationale Intervallendpunkte mit `fractions.Fraction` erlauben exakt einschließende Grundoperationen. Unterstütze einen kleinen Ausdrucksbaum mit Konstanten, Variablen, Addition, Subtraktion, Multiplikation, ganzzahligen nichtnegativen Potenzen und Division, sofern der Nennerbereich null ausschließt. Automatische Differentiation kann später darauf aufbauen; sie ist für den ersten Scope-Nachweis nicht erforderlich.

Ausdrucksbäume werden validiert. Ein beliebiger Python-Callback wird nicht durch häufigeres Auswerten zu einem beweisfähigen Ausdruck. Dezimale Konstanten kommen als Zeichenketten/rationale Werte hinein. Falls binäre Floats zugelassen werden, ist deren exakter Binärwert ausdrücklich das Problem; `Fraction(str(float))` darf nicht heimlich eine andere Semantik erzeugen.

Intervallarithmetik muss die mathematische Bildmenge einschließen. Ein optionaler Gleitkommabackend benötigt gerichtete Rundung bzw. einen verifizierten Einschluss; gewöhnliches NumPy-Intervallrechnen genügt nicht. Etablierte validierte Arithmetik ist ein später möglicher Anschluss. [S08]

### 11.2 Prüfalgorithmus

API etwa `certify_bound(expression, box, epsilon, budget)`:

1. Validität von Ausdruck, rationaler Box, Toleranz und Budget prüfen.
2. Einschluss auf der Box berechnen.
3. Wenn daraus die universelle Schranke folgt, Box als bewiesen ablegen.
4. Wenn ein exakt ausgewerteter Punkt die Schranke verletzt, Gegenbeispiel zurückgeben. Optional ist auch eine ganze nachweislich verletzende Teilbox ein Zeuge.
5. Sonst deterministisch unterteilen. Alle entstandenen Teilboxen müssen den ursprünglichen Bereich abdecken.
6. Nach Budgetende ungelöste Boxen erhalten; kein universeller Erfolg.

Die erste Version beweist algebraische Aussagen und unterstützte Vektorfeldresiduen. Eine numerische ODE-Lösung mit `atol`/`rtol` ist kein validierter Flussnachweis. Eine spätere validierte ODE-Integration ist ein eigenes Paket.

### 11.3 Kontrollen

**J-C09:** $p(x)=x(1-x)$ auf $[0,1]$. Endpunkte liefern null; das Maximum beträgt $1/4$ bei $x=1/2$. Bei 64 gleich großen Teilintervallen ist die größte natürliche Intervallobergrenze

\[
\max_{i=0,\ldots,63}\frac{i+1}{64}\left(1-\frac i{64}\right)=\frac{33}{128}=0.2578125.
\]

Damit ist $p\le13/50=0.26$ bewiesen. Die Behauptung $p\le6/25=0.24$ wird durch $x=1/2$ widerlegt. Ein naiver Intervallalgorithmus muss die scharfe Grenze $1/4$ unter endlichem Budget nicht beweisen können; `unknown` ist hier zulässig.

**J-C10:** Natürliche Intervallrechnung liefert für $x-x$, $x\in[0,1]$, zunächst $[-1,1]$, obwohl der Ausdruck identisch null ist. Ohne dokumentierte symbolische Vereinfachung darf daraus keine scharfe Nullschranke entstehen. Für $1/x$ auf $[-1,1]$ ist die Funktion auf dem ganzen Gebiet nicht definiert; dies wird als Singularität/fehlende Definitionsvoraussetzung ausgewiesen, nicht als endliche Garantie.

Pflichtprüfungen: genaue Grenzberührung, negative Koeffizienten, Nenner nahe null, einmalige oder wiederholte Variablen, mehrdimensionale Boxen, vollständige Abdeckung der Partition, Restbox bei Budgetende, leeres Gebiet, exakte Rekonstruktion eines Zertifikats. Mindestens ein Residuum aus J4 wird über eine Box zertifiziert.

**Abnahme:** `verify_validated_scopes.py`; getrennte Ergebnisse für bewiesen, widerlegt, unbekannt und nicht definierte Eingabe. Jeder bewiesene Fall ist aus gespeichertem Ausdruck, Bereich, Arithmetik und Einschlüssen erneut prüfbar.

## 12. J6 — Strukturelle Identifizierbarkeit mit präzisem Umfang

**Dateien:** etwa `identifiability/exact_linear.py`, `identifiability/structural_reports.py`, `docs/structural_identifiability.md`.

### Pflichtkern

Implementiere zunächst exakte affine Beobachtungsabbildungen $z=A\theta+b$ mit rationaler Matrix. Auf dem unbeschränkten Parameterraum $\mathbb R^p$ bestehen Beobachtungsfasern aus affinen Nullräumen. Eine lineare Kombination $c^\top\theta$ ist genau dann durch diese Beobachtung eindeutig bestimmt, wenn $c$ im Zeilenraum von $A$ liegt. Parameterrestriktionen können einzelne Fasern verkleinern; deshalb den verwendeten Parameterbereich ausdrücklich ausweisen.

API etwa `analyze_affine_identifiability(A, b, parameter_domain)` mit Rang, Nullraumbasis, identifizierbaren Kombinationen und exakter Faserbeschreibung. Für allgemeine nichtlineare Abbildungen gibt es dadurch noch keinen vollständigen Solver.

Ergänze zwei dokumentierte analytische Beispiele für globale beziehungsweise lokale Identifizierbarkeit. Ein numerisch voller Jacobi-Rang allein zertifiziert keine globale Eindeutigkeit. Fisher-Information, Profil-Likelihood und strukturelle Identifizierbarkeit bleiben getrennte Ergebnisse.

### Kontrollen

**J-C11:** $A=\begin{pmatrix}1&1\\2&2\end{pmatrix}$. Rang eins, Nullvektor $(1,-1)$. Die Summe der beiden Parameter ist identifizierbar, ihre Aufteilung auf $\mathbb R^2$ nicht.

**J-C12:** $\dot x=-kx$, $y=cx$, $k,c,x_0>0$. Aus idealer kontinuierlicher Beobachtung erhält man

\[
y(0)=cx_0,\qquad \dot y(0)=-kcx_0,\qquad
k=-\dot y(0)/y(0).
\]

$k$ und das Produkt $cx_0$ sind identifizierbar; $c,x_0$ einzeln bleiben unter $(c,x_0)\mapsto(c/\lambda,\lambda x_0)$ unverändert beobachtbar. Mit $k=2,c=3,x_0=5$ sind Anfangswert und Ableitung $15,-30$. Für $\lambda=7$ erhält man $c'=3/7,x'_0=35$. Ist $c$ bekannt, entfällt diese Mehrdeutigkeit. Die Positivitätsannahme schließt den degenerierten Nullsignal-Fall bewusst aus.

**J-C13:** $y=\theta^2$ hat bei $y=4$ auf $\mathbb R$ die Faser $\{-2,2\}$. An $\theta=2$ ist die Ableitung vier: lokale Eindeutigkeit, aber keine globale. Auf $\theta>0$ bleibt nur $\theta=2$.

### Anschluss und optionale Erweiterung

Verknüpfe die Berichte mit den bestehenden Beobachtungsfasern und den vorhandenen praktischen Identifizierbarkeitsanalysen. Ein Galaxien-Profil mit breitem Konfidenzbereich beweist nicht automatisch strukturelle Nichtidentifizierbarkeit.

Ein allgemeiner rationaler ODE-Solver ist optional. Dafür ist ein Adapter zu SIAN beziehungsweise StructuralIdentifiability.jl sinnvoller als ein eigener symbolischer Algorithmus. Dessen Klassen von lokalen/globalen und generischen Aussagen, Zufallsverfahren, Parameterdomänen und Wahrscheinlichkeitsparameter müssen erhalten bleiben. Eine algorithmische Erfolgswahrscheinlichkeit ist kein Konfidenzniveau für reale Messdaten. [S09–S10]

**Abnahme:** `verify_structural_identifiability.py`; exakte affine Fälle, analytische Reservoirkontrolle, diskrete Mehrdeutigkeit, bekannte/ unbekannte Anfangsbedingungen und ausdrücklicher `unsupported`-Status außerhalb des implementierten Umfangs. Kein simuliertes „allgemeines Identifizierbarkeitstool“ durch numerische Rangtests.

## 13. J7 — Gemeinsame Sensitivität statt einzelner Parameterbewegungen

**Dateien:** etwa `validation/global_sensitivity.py`, `validation/galaxy_joint_sensitivity.py`, `docs/joint_sensitivity.md`. Der zweite Adapter wird nur erstellt, wenn der bestehende Galaxienadapter ihn tatsächlich benötigt; möglichst dort vorhandene Funktionen erweitern.

### 13.1 Zuerst das Unsicherheitsmodell

Definiere getrennt:

- **Szenarienraum:** Welche Kombinationen gelten als plausibel oder prüfenswert? Daraus folgt noch keine Wahrscheinlichkeit.
- **Eingangsverteilung:** Welche gemeinsame Verteilung wird für eine probabilistische Sensitivitätsanalyse angenommen?
- **Messunsicherheit und Modellunsicherheit:** Was stammt aus dokumentierten Messfehlern, was aus frei gewählten Modellvarianten?
- **Zielgröße:** Parameterwert, Vorhersage, Testverlust oder Differenz zweier Testverluste.

Ein Raster gemeinsamer Szenarien ist bereits eine deutliche Verbesserung gegenüber ausschließlich einzelner Parameteränderung. Ohne begründete gemeinsame Verteilung dürfen Häufigkeiten von „Siegern“ nicht als empirische Wahrscheinlichkeiten verkauft werden.

### 13.2 Sobol-Kern

Für unabhängige Eingänge und positive endliche Ausgangsvarianz gelten

\[
S_i=\frac{\operatorname{Var}(\operatorname E[f(X)\mid X_i])}{\operatorname{Var}(f(X))},
\qquad
S_{T_i}=1-\frac{\operatorname{Var}(\operatorname E[f(X)\mid X_{-i}])}
{\operatorname{Var}(f(X))}.
\]

Implementiere zunächst erste und totale Indizes. Definiere exakt, welche Spalte in einer gemischten Stichprobenmatrix ersetzt wird. Bei unabhängigen Matrizen $A,B$ und $A_B^{(i)}$ mit der i-ten Spalte aus $B$ sind beispielsweise konsistente Pick-Freeze-Schätzer:

\[
\widehat S_i=\frac{\operatorname{mean}[f(B)(f(A_B^{(i)})-f(A))]}{\widehat V},
\qquad
\widehat S_{T_i}=\frac{\operatorname{mean}[(f(A)-f(A_B^{(i)}))^2]}{2\widehat V}.
\]

Varianzschätzung und endliche Stichprobennormalisierung müssen dokumentiert werden. Endliche Monte-Carlo-Schätzungen können außerhalb $[0,1]$ liegen; nicht still auf diesen Bereich beschneiden. Abhängige Eingänge erfordern eine andere Zerlegung. [S11–S12]

### Kontrollen

**J-C14:** $X,Y$ unabhängig gleichverteilt auf $[0,1]$.

| Funktion | Varianz | Erste Indizes | Totale Indizes |
|---|---:|---|---|
| $X+2Y$ | $5/12$ | $(1/5,4/5)$ | $(1/5,4/5)$ |
| $XY$ | $7/144$ | $(3/7,3/7)$ | $(4/7,4/7)$ |

Beim Produkt beträgt die reine Interaktion $1/7$. Ergänze konstante Ausgabe als undefinierten Varianzfall und $Y=X$ als negative Kontrolle für die Unabhängigkeitsvoraussetzung.

Die Integrale hinter diesen Werten werden exakt hergeleitet. Der Schätzer wird anschließend mit dokumentierter Zufallsquelle und Konvergenzkriterium geprüft; eine exakte Gleichheit mit dem analytischen Wert wird bei endlicher Monte-Carlo-Stichprobe nicht verlangt.

### 13.3 Galaxienpilot

Gemeinsam zu variierende Größen sind zunächst Entfernung $D$, Inklination $i$, Scheiben- und Bulge-Masse-zu-Licht-Verhältnisse. Physikalische Grenzen, mögliche Abhängigkeiten und die Herkunft der Unsicherheiten stehen im Eingangsmanifest. Falls eine Größe nicht bekannt ist, verwende ausgewiesene Szenarien statt erfundener Fehlerbalken.

Die bestehende Transformation des Piloten ist wiederzuverwenden: Radien skalieren mit Entfernung, entsprechende baryonische Geschwindigkeitsbeiträge mit deren Quadratwurzel; beobachtete Geschwindigkeit und Fehler reagieren auf die angenommene Inklination. Prüfe diese Konventionen am aktuellen Adapter.

Für jeden gemeinsamen Eingangspunkt:

1. Dieselbe physikalische Transformation auf alle zu vergleichenden Modelle anwenden.
2. Trainings- und Test-IDs unverändert halten.
3. Modellparameter ausschließlich auf den transformierten Trainingsdaten neu fitten.
4. Testverluste auf den gehaltenen Außenradien berechnen.
5. Nicht konvergierte Fits, Randtreffer und ungültige Vorhersagen ausdrücklich berichten.

Primäre Zielgröße ist die Differenz der gehaltenen Testverluste. Ein diskreter Sieger allein verdeckt Größe und Unsicherheit des Unterschieds. Wiederholte Fitstarts und Fitgrenzen gehören zum reproduzierbaren Versuchsprotokoll.

Wenn $a_0$ zusätzlich gefittet wird, entsteht eine andere MOND-Modellvariante; das muss vorab definiert und separat bezeichnet werden. Kein nachträgliches Optimieren an den Testgalaxien. AIC/BIC sind nicht der Standard für diesen gehaltenen Vergleich; ein späterer In-Sample-Vergleich bräuchte gemeinsame Likelihood, Parameterzählung und die jeweiligen Regularitätsbedingungen.

SPARC-Rohdaten bleiben an den bestehenden lokalen, hashgeprüften Datenweg und das Lizenzprotokoll gebunden. Fehlende Daten führen zu `not_run`/`blocked_missing_data`, nicht zu einem bestandenen Realdatencheck. Der mathematische Pflichtkern mit synthetischen Daten ist davon unabhängig.

**Abnahme:** `verify_global_sensitivity.py` plus gegebenenfalls data-Adapter; gemeinsame Szenarien mindestens eines vorhandenen Piloten, für dessen Daten Zugriff/Provenienz geklärt sind. Im Galaxienfall ist ein offen ausgewiesener Datenblocker zulässig, kein vorgetäuschter Abschluss der empirischen Teilaufgabe.

## 14. J8 — Gewichtetes Split Conformal mit begrenzter Garantie

**Dateien:** etwa `validation/weighted_conformal.py`, `docs/weighted_conformal.md`.

### Verfahren und Garantieumfang

Der Vorhersager wird auf einer separaten Trainingsmenge fixiert. Kalibrierungspunkte sind i.i.d. aus $P$, ein unabhängiger Zielpunkt aus $Q$; $P(Y\mid X)=Q(Y\mid X)$ und $Q_X\ll P_X$. Für bekannte, bis auf einen positiven Faktor korrekte Gewichte $w=dQ_X/dP_X$ verwendet man beim Testpunkt $x$:

\[
q(x)=\operatorname{Quantile}_{1-\alpha}
\left(\sum_i\frac{w(X_i)}{\sum_jw(X_j)+w(x)}\delta_{R_i}
+\frac{w(x)}{\sum_jw(X_j)+w(x)}\delta_{+\infty}\right).
\]

Bei absoluten Residuen ist das Intervall $[\hat f(x)-q(x),\hat f(x)+q(x)]$. Unter diesen Voraussetzungen gilt die marginale Abdeckungsaussage über Kalibrierung und Zielpunkt. Sie ist keine konditionale Garantie für jedes feste $x$. Geschätzte Gewichte liefern ohne weitere Fehlerkontrolle nicht automatisch dieselbe exakte Garantie. [S13]

### API und Ergebnisfelder

`weighted_split_quantile(scores, calibration_weights, test_weight, alpha)` bildet den kleinen mathematischen Kern. Eine zweite Funktion erzeugt Intervalle und den Anwendungsbericht. Speichere Gewichtsherkunft, Normalisierung, maximale Gewichte, effektive Stichprobengröße als Diagnose, unbegrenzte Intervallhäufigkeit und empirische Abdeckung.

Gewichte müssen endlich und nichtnegativ sein; der ausgewertete Zielpunkt braucht einen positiven Testgewichtswert. Gemeinsame Skalierung darf nichts ändern. Clipping ist eine Verfahrensänderung und darf eine Garantie nicht unverändert erben. Zeitliches Autokorrelationsproblem und Concept Shift werden durch eine Gewichtung der Kovariaten nicht automatisch behoben.

### Kontrollen

**J-C15:**

| Residuen | Kalibriergewichte | Testgewicht | $\alpha$ | Quantil |
|---|---|---:|---:|---:|
| $(1,2,3)$ | $(1,1,1)$ | 1 | $1/4$ | 3 |
| $(1,2,3)$ | $(1,1,1)$ | 4 | $1/4$ | $+\infty$ |
| $(1,2,3)$ | $(1,2,1)$ | 1 | $2/5$ | 2 |

Insbesondere darf die Testpunktmasse bei $+\infty$ nicht fehlen.

**J-C16 — eigene endliche vollständige Rechnung:** Vier Kalibrierpunkte; $P_X(1)=1/10$, $Q_X(1)=9/10$, $Y=X$, Vorhersager null, $\alpha=1/5$. Die korrekten Gewichte sind $w(0)=1/9,w(1)=9$. Enumeriere alle $2^5=32$ Kalibrier-/Zielkombinationen mit ihrer jeweiligen Wahrscheinlichkeit.

- Ungewichtete Abdeckung: $1-(9/10)^4(9/10)=40951/100000=40.951\%$.
- Gewichtete Abdeckung: $1$.
- Wahrscheinlichkeit eines unbeschränkten gewichteten Intervalls: $89991/100000=89.991\%$.

Dieser Fall zeigt gleichzeitig den Abdeckungsgewinn und seine mögliche Nutzlosigkeit für präzise Entscheidungen. Deshalb stehen Abdeckung, Intervallbreite und Unbeschränktheit nebeneinander.

**J-C17:** Gleiches $X$, vier Kalibrierwerte $Y=0$, Zielwert $Y=1$, gleiche Gewichte und $\alpha=1/5$. Quantil null, Abdeckung null. Hier verletzt Concept Shift die Voraussetzungen; das ist kein Widerspruch zum Satz.

Weitere Pflichtprüfungen: ties an der Quantilschwelle, gemeinsame Gewichtsskalierung, Nullgewichte, ungültige Gewichte, fehlende Trainings-/Kalibriertrennung, fehlender Support, kleine Stichproben, Serialisierung unbeschränkter Intervalle.

Im vorhandenen `conformal.py` die Formulierung zu `q=+inf` prüfen: Das resultierende Vorhersageintervall ist die ganze reelle Gerade; es ist kein leeres Intervall. Eine entsprechende missverständliche Dokumentationsstelle im Referenzstand wird bei diesem Anschluss korrigiert.

**Abnahme:** `verify_weighted_conformal.py`; vollständige Rechnung J-C16, negative Kontrolle J-C17 und sauberer Vergleich mit fester und bereits vorhandener adaptiver Kalibrierung. Ein Realdatentest darf neutral oder schlechter ausfallen.

## 15. J9 — Endliche kausale Modelle und interventionelle Abstraktion

**Dateien:** etwa `causal/finite_scm.py`, `causal/abstraction.py`, `docs/finite_causal_abstraction.md`.

### 15.1 Modellklasse

Implementiere endliche azyklische strukturelle Kausalmodelle. Endogene Variablen besitzen endliche Wertebereiche und deterministische Mechanismen; Zufälligkeit kommt aus einer expliziten endlichen gemeinsamen Verteilung exogener Variablen. Gemeinsame exogene Ursachen müssen darstellbar sein. Unabhängige exogene Größen dürfen nicht still vorausgesetzt werden.

Interventionen ersetzen die jeweilige Strukturgleichung durch einen festgelegten Wert. Validierung umfasst DAG, Mechanismenbereiche, erlaubte Eltern, exogene Wahrscheinlichkeiten, Gesamtmasse eins, Interventionstypen und Rechenbudget. Nicht auf eins summierende Eingaben werden nicht still normalisiert.

API etwa `FiniteSCM`, `interventional_distribution`, `pushforward_distribution`, `check_interventional_abstraction`.

### 15.2 Abstraktionsbedingung

Für Mikro-/Makromodell, Zustandsabbildung $\tau$ und deklarierte Interventionsabbildung $\omega$ wird für **jede erlaubte** Mikrointervention $i$ geprüft:

\[
\tau_\#P_{\mathrm{micro}}^{do(i)}
=P_{\mathrm{macro}}^{do(\omega(i))}.
\]

Zum gewählten exakten Transformationsbegriff gehören eine surjektive, ordnungserhaltende Interventionsabbildung auf den deklarierten Interventionsmengen. Diese Eigenschaften sind zusätzlich zur Verteilungsgleichheit zu prüfen. Die Ordnung ist die konsistente Erweiterung partieller Interventionen. Es handelt sich um Gleichheit interventioneller Verteilungen; daraus folgt keine Gleichheit beliebiger kontrafaktischer Kopplungen. [S14]

Die bekannte aktionsweise Markov-Bedingung ist ein verwandter Anschluss. Ihre Prüfung ersetzt nicht automatisch die SCM-Bedingungen oder die Festlegung zulässiger Eingriffe.

### Kontrollen

**J-C18 — Beobachtung ist nicht Eingriff:** $U$ ist fair binär, $X=U$.

- Modell 1: $Y=X$.
- Modell 2: $Y=U$.

Beide beobachten $(X,Y)=(0,0),(1,1)$ mit Wahrscheinlichkeit je $1/2$. Unter $do(X=1)$ ist $P(Y=1)$ dagegen eins beziehungsweise $1/2$. Die TV-Distanz beträgt $1/2$. Eine epistemische Faser über genau diese zwei Kandidaten weist Mehrdeutigkeit nach; sie behauptet keine vollständige Enumeration aller denkbaren Kausalmodelle.

**J-C19 — exakte und scheiternde Abstraktion:** Mikro: $X_1=U_1,X_2=U_2$ unabhängig fair, $Y=X_1\oplus X_2$. Makro: $Z$ fair, $\bar Y=Z$. Zustandsabbildung $\tau(x_1,x_2,y)=(x_1\oplus x_2,y)$.

Erlaubte Mikrointerventionen sind zunächst Nichtstun und die vier vollständigen Eingriffe $do(X_1=a,X_2=b)$. Die Makromenge enthält Nichtstun, $do(Z=0)$, $do(Z=1)$. Ordne vollständige Eingriffe nach $a\oplus b$ zu. Alle fünf Prüfungen stimmen exakt; die Interventionsabbildung ist surjektiv und ordnungserhaltend auf diesem deklarierten Bereich.

Erweitere nun um $do(X_1=1)$ und **lege dessen Bild auf $do(Z=1)$ fest**. Mikro bleibt $Y$ fair, makro wird $\bar Y=1$ sicher. TV-Distanz $1/2$: Diese konkrete Erweiterung scheitert. Daraus darf nicht behauptet werden, jede denkbare andere Abbildung müsse scheitern.

Pflichtprüfungen: vertauschte Variablennamen; nicht surjektive Abbildung; verletzte Interventionsordnung; fehlender Eingriff; ein einziger verletzender Eingriff bei sonst passenden Fällen; korrelierte exogene Ursachen; ungültige DAGs; Budgetabbruch; exakter versus numerischer Verteilungsvergleich.

**Abnahme:** `verify_finite_causal_models.py` und `verify_causal_abstraction.py`; präziser Interventionsscope in jedem Ergebnis. Kein Graphlernen und kein kausaler Realdatenanspruch in diesem Paket.

## 16. J10 — Eine überprüfbare Transportregel

**Dateien:** etwa `causal/selection_diagrams.py`, `causal/transport.py`, `docs/scoped_transportability.md`.

### 16.1 Pflichtregel

Implementiere eine gezielt begrenzte Standardisierung. Für beobachtete, nicht durch $X$ beeinflusste Kovariaten $Z$:

\[
Q(Y\mid do(X=x))
=\sum_z P(Y\mid do(X=x),Z=z)\,Q(Z=z).
\]

Voraussetzungen: passende Mechanismeninvarianz zwischen Quelle und Ziel, geeignete Quellinterventionen und Support für alle im Ziel relevanten $z$. In einem angegebenen Selektionsdiagramm prüfe S-Admissibilität $Y\perp S\mid X,Z$ in $G_{\bar X}$, also nach Entfernung eingehender Kanten nach $X$. Der Diagrammcheck bewertet eine deklarierte kausale Annahme; er lernt sie nicht aus Daten. [S15]

Baue einen kleinen endlichen DAG-/d-Separationsprüfer. Ein Vorfahrengraph mit Moralisierung oder ein sauber geprüfter Bayes-Ball-Algorithmus ist ausreichend. Explizite latente Knoten sind im Graphen möglich. Allgemeine ADMG-/sID-Unterstützung gehört nicht zum Pflichtkern.

### 16.2 Drei getrennte Ergebnisse

1. **Regel nachgewiesen anwendbar:** Die Formel folgt unter den geprüften/angegebenen Voraussetzungen.
2. **Von dieser Regel nicht zertifiziert:** Eine Voraussetzung fehlt oder ist nicht nachgewiesen. Dies ist kein allgemeiner Nichttransportabilitätsbeweis.
3. **Nichtidentifikation durch Gegenmodelle:** Zwei zugelassene vollständige Quelle-Ziel-Modellfamilien stimmen in allen verfügbaren Daten/Experimenten überein und unterscheiden sich im gesuchten Zielwert.

Die Herkunft der experimentellen Quellverteilungen ist Teil des Berichts. Beobachtungswerte $P(Y\mid X,Z)$ nicht ohne weitere Identifikationsvoraussetzungen anstelle von $P(Y\mid do(X),Z)$ einsetzen.

### Kontrollen

**J-C20:** Quelle $Z\sim Bernoulli(1/2)$, Ziel $Z\sim Bernoulli(3/4)$, in beiden $Y=X\oplus Z$. Quellinterventionen liefern für beide $x$ Erfolgswahrscheinlichkeit $1/2$. Im Ziel:

\[
Q(Y=1\mid do(X=0))=3/4,\qquad
Q(Y=1\mid do(X=1))=1/4,
\]

also mittlerer Effekt $-1/2$. Die ungewichtete Übernahme des Quelleffekts null ist falsch. Negative Supportkontrolle: Wenn die Quelle $Z=1$ nie enthält, das Ziel aber schon, ist die Regel ohne zusätzliche Struktur nicht empirisch auswertbar.

**J-C21 — Nichttransportabilitätszeuge:** In beiden Modellfamilien ist die Quelle $X=U,Y=X$ mit fairem $U$, einschließlich verfügbarer Experimente $do(X=0/1)$. Im Ziel gilt in Familie 1 weiterhin $X=U,Y=X$, in Familie 2 dagegen $X=U,Y=U$. Zielbeobachtungen und sämtliche angegebenen Quellinformationen sind identisch; $Q(Y=1\mid do(X=1))$ beträgt eins bzw. $1/2$. Der deklarierte Selektionsbereich erlaubt einen Mechanismenwechsel bei $Y$. Ein gemeinsamer Graph kann $U\to X,U\to Y,X\to Y$ enthalten; eine nicht wirksame Kante in einer Parametrisierung ist zulässig, da keine Faithfulness-/Minimalitätsannahme gemacht wird.

**J-C23 — Graphprüfung:** Collider $A\to C\leftarrow B$ mit $C\to D$: Ohne Konditionierung sind $A,B$ d-separiert; mit Konditionierung auf $C$ oder seinen Nachfahren $D$ nicht. Im Diagramm $S\to Z\to Y\leftarrow X$ ist $S$ von $Y$ bedingt auf $X,Z$ getrennt, bedingt nur auf $X$ nicht.

Pflichtprüfungen: falsche Richtung des Kantenentfernens bei $do(X)$; Z als Nachfahre von X; fehlender Support; Verletzung der S-Admissibilität; unvollständige Tabellen; Budgetgrenze; vollständige Kontrolle aller verfügbaren Quellinformationen bei einem Gegenmodellpaar.

**Abnahme:** `verify_scoped_transportability.py`. Dokumentation sagt „geprüfte Standardisierungsregel und endliche Gegenmodelle“, nicht „allgemeiner Pearl-Transportabilitätssolver“. Auf dieser Basis kann später ein eigener domänenspezifischer Kausalpilot geplant werden.

## 17. J11 — Vorhandene Reduktionsschranken anschließen

**Ziel:** Eine durchgehende Verbindung zwischen Reduktion, Fehlergrenze, Beobachtungsgröße und zulässiger Entscheidung.

**Dateien:** etwa `closure/contract_adapter.py`, `docs/reduction_contracts.md`; vorhandene Funktionen in `closure/error_bounds.py` wiederverwenden.

Bei Zeilenverteilungen und stochastischem Lifting $A$ lautet ein vorhandener Anschluss schematisch

\[
\|p_0P^k-\pi_0\Pi^kA\|_1
\le \|p_0-\pi_0A\|_1+k\|\Pi A-AP\|_\infty.
\]

Für kontinuierliche Zeit steht die entsprechende Generatorabweichung mit dem Zeitfaktor. Die Matrix-$\infty$-Norm ist hier die maximale absolute Zeilensumme. Diese Reduktionsschranken gehören bereits zum Repository; J11 vereinheitlicht ihre Verwendungsbedingungen und Berichte. [S16]

Eine Fluss-/Verteilungsfehlergrenze darf anschließend durch einen beobachtbaren Operator weitergegeben werden, wenn dessen passende Norm-/Lipschitzschranke vorliegt. Ohne diese Voraussetzung entsteht keine automatische Garantie für eine nachgelagerte Sicherheitsentscheidung.

**J-C22:** Mit identischem Zustandsraum und Lifting $I$:

\[
P=\begin{pmatrix}4/5&1/5\\1/10&9/10\end{pmatrix},\quad
Q=\begin{pmatrix}7/10&3/10\\1/5&4/5\end{pmatrix},\quad
p_0=(1,0).
\]

Dann $\|Q-P\|_\infty=1/5$,
$p_0P^2=(33/50,17/50)$,
$p_0Q^2=(11/20,9/20)$.
Der L1-Fehler ist $11/50$, die Schranke $2/5$.
Die TV-Distanz ist $11/100$, ihre entsprechende Schranke $1/5$.

Dieser Fall prüft Norm und Propagation, obwohl das Lifting hier keine Dimensionsreduktion ausführt. Ein bestehendes echtes Reduktionsbeispiel ergänzt den Integrationstest.

Pflichtprüfungen: L1/TV-Faktor; Orientierung aller Matrizen; stochastische Liftingbedingungen; Anfangsfehler; unpassende Zeitskalen; inkompatible Zwischenzustände; vorhandene numerische Grenze versus rigoroser Nachweis. Eine Gleitkommaberechnung einer theoretischen Schranke wird nicht ohne Rundungsanalyse zu einer validierten Einschließung.

**Abnahme:** `verify_reduction_contracts.py`; ein bestehender Reduktionsfall mit vollständigem Vertrag, ein durch J4 zusammengesetzter Beobachtungsanschluss, keine doppelte Implementierung der bestehenden Reduktionsverfahren.

## 18. J12 — Gemeinsame Berichte und Abschluss

### 18.1 CLI und Dokumentation

Ein leichter Einstieg, beispielsweise `scripts/run_scope_evidence_demo.py`, soll ausgewählte Demonstrationen und standardkonformes JSON liefern. Bestehende spezialisierte CLIs bleiben erhalten. Keine neue Plugin-Architektur nur für diesen Plan.

Die Demonstration zeigt mindestens:

1. Eine zunächst inkompatible Verkettung und ihren korrekt eingeschränkten Scope.
2. Einen kontinuierlichen rationalen Bereichsnachweis samt Gegenbeispiel.
3. Einen beobachtungsäquivalenten, aber interventionell verschiedenen Modellvergleich.
4. Eine transportierbare Anfrage und eine von der Regel nicht zertifizierte Anfrage.
5. Einen Prognosevergleich mit sauber ausgewiesener inferenzieller Grenze.
6. Eine gewichtete Kalibrierung, bei der Unbeschränktheit ausdrücklich sichtbar ist.

Aktualisiere Fähigkeitsübersicht, Roadmap und relevante Dokumentationslinks. Die README bekommt einen knappen Fähigkeitsabsatz; Herleitungen und Chronologie bleiben in Fachdocs beziehungsweise HISTORY.

### 18.2 Abschlussmatrix

| Bereich | Erforderlicher Abschluss | Was dadurch nicht behauptet wird |
|---|---|---|
| Dimensionen | Exakte Π-Basis und Dimensionsfehler | Gleiche physikalische Bedeutung gleicher Einheiten |
| Komposition | Kompatible Modell-/Scope-/Zeitverträge | Beliebige Verkettbarkeit |
| Bereichsnachweise | Unterstützte rationale Ausdrücke auf deklarierten Boxen | Allgemeine Blackbox- oder ODE-Zertifizierung |
| Identifizierbarkeit | Exakte affine Analyse und analytische Kontrollfamilien | Vollständiger allgemeiner ODE-Solver |
| Prognosevergleich | Gepaarte Effekte mit anwendbarkeitsabhängiger Inferenz | Universeller Überlegenheitstest |
| Sensitivität | Gemeinsame Szenarien, unabhängiger Sobol-Kern | Unbekannte reale Parameterverteilung als bekannt |
| Conformal | Korrekte gewichtete Quantile und begrenzte Garantie | Abdeckung unter beliebigem Drift |
| Kausalabstraktion | Exakte Prüfung deklarierter endlicher Eingriffe | Kontrafaktische oder ontologische Identität |
| Transport | Eine geprüfte Regel und konkrete Gegenmodellzeugen | Vollständiger Transportabilitätsalgorithmus |
| Reduktion | Vorhandene Schranken nachvollziehbar angeschlossen | Neue allgemeine Reduktionstheorie |

### 18.3 Freigabekriterien

- Jeder Pflichtfall hat eine explizite Assertion; eine absichtlich negative Antwort kann ein bestandener Test sein.
- Alle neuen Verifikationsskripte stehen ausdrücklich in `_EXPLICIT_CATEGORY`.
- Volle Suite und Linkprüfung wurden auf dem tatsächlichen finalen Commit ausgeführt; Ergebnisse und Umgebung sind dokumentiert.
- Realdatenprüfung, synthetische Prüfung, ausgelassene Prüfung und blockierter Datenzugriff werden getrennt gezählt.
- Keine neue Rohdatenveröffentlichung ohne eingehaltenes Provenienz-/Lizenzprotokoll.
- Die abschließende Liste unterscheidet abgeschlossene Pflichtpakete, empirische Blocker und optionale Forschung.
- Für jede behauptete universelle Garantie sind Ausdrucksklasse, Domäne, Annahmen und Beweismethode auffindbar.
- Kontrollskript, Produktionsprüfung und theoretische Herleitung bleiben nachvollziehbar verschiedene Evidenzquellen.

## 19. Teststrategie, Laufzeit und Pflege

### 19.1 Drei Schichten

**Unabhängige Kontrollrechnung:** Das beigefügte `verify_plan_control_cases.py` importiert kein SCF. Es kontrolliert die im Plan genannten Rechenwerte durch Brüche, endliche Enumeration und eine gesonderte Einheitenkontrolle. Es ist kein Produktionsbackend.

**Paketprüfung:** Neue `verify_*.py`-Skripte rufen die tatsächlichen neuen SCF-APIs auf und vergleichen gegen die unabhängigen Werte. Eine bloße Kopie derselben Implementierung als „Referenz“ genügt nicht.

**Integration:** Gezielte vorhandene Beispiele und mindestens eine zusammenhängende Berichtskette prüfen, anschließend die nach `CLAUDE.md` verlangte Regression. Zusätzliche große Zufallsläufe nur für einen konkret verbleibenden statistischen oder numerischen Unsicherheitsgrund.

### 19.2 Ressourcen und Abbruch

Rationale Bruchrechnung und vollständige Enumeration können teuer werden. APIs erhalten daher dokumentierte Grenzen für Boxen, Zustände, Exogenkombinationen oder Rechenschritte. Werte werden in J0 anhand kleiner Benchmarks festgelegt, nicht als angeblich sichere Zahlen erfunden. Überläufe und wachsende Bruchgrößen sind Verfahrensgrenzen; sie dürfen keine mathematische Schlussfolgerung vortäuschen.

Persistente Resultate nennen Algorithmus-/Schema-Version, Commit, numerische Bibliotheksversionen soweit relevant, Zufallsquelle, Parameter und Datenhash. Ein Seed allein garantiert keine plattformübergreifend identischen Floats. Exakte rationale Kontrollen eignen sich für strenge Gleichheit; statistische Schätzer brauchen begründete Toleranzen und Konvergenzprüfungen.

### 19.3 Kommandos

Unabhängige Planprüfung:

~~~bash
python verify_plan_control_cases.py --output control_results.json
~~~

Repository-Gates nach aktueller Arbeitsregel:

~~~bash
python scripts/run_verification_suite.py --category all
python scripts/run_verification_suite.py --category links
~~~

Die Namen neuer Einzelprüfungen werden in der Roadmap festgehalten. Plane längere Gesamtläufe als Hintergrundprozess mit Statusmeldungen ein. Ändere keine Tests nur deshalb, weil ein erwartetes Forschungsresultat ausbleibt.

## 20. Kontrollfallregister

Die Zahlen stammen aus eigener unabhängiger Rechnung. Die wissenschaftlichen Quellen begründen die Verfahrensklassen; sie sind nicht die Quelle dieser konkreten Testparameter.

| ID | Paket | Geprüfter Kern | Ergebnis |
|---|---|---|---|
| J-C01 | J1 | Bartlett-HAC-Arithmetik | DM $4/5$, Standardfehler $5/8$ |
| J-C02 | J1 | Holm-Korrektur | $(.03,.06,.06)$ |
| J-C03 | J2 | Dimensionsnullraum | $(2,-1,1)$; Rang 2 |
| J-C04 | J2/J3 | Einheitenwechsel und Produktinvarianz | Reservoirwert invariant; $\rho r=12$ |
| J-C05 | J4 | Urbild eines Scope | $[0,1/2]$ |
| J-C06 | J4 | Zeitfaktor und Horizont | $1/4$; Horizont 2 |
| J-C07 | J4 | Fluss- versus Feldfehler | $1/2$ versus Feldschranke 9 |
| J-C08 | J4 | Verfeinerungsrichtung | vorwärts ja, rückwärts nein |
| J-C09 | J5 | Bereichseinschluss und Gegenpunkt | $33/128$; Maximum $1/4$ |
| J-C10 | J5 | Abhängigkeit und Singularität | natürliche Einschließung $[-1,1]$; keine endliche Reziprok-Einschließung |
| J-C11 | J6 | Exakte affine Faser | Rang 1, Nullvektor $(1,-1)$ |
| J-C12 | J6 | Reservoir-Identifizierbarkeit | $k=2$, Produkt 15 |
| J-C13 | J6 | Lokal versus global | Faser $\{-2,2\}$ |
| J-C14 | J7 | Additive/interaktive Sensitivität | $1/5,4/5$; $3/7,4/7$ |
| J-C15 | J8 | Gewichtetes Quantil | $3,+\infty,2$ |
| J-C16 | J8 | Vollständige 32-Fall-Abdeckung | $.40951$ versus $1$; unbeschränkt $.89991$ |
| J-C17 | J8 | Concept-Shift-Gegenkontrolle | Abdeckung null |
| J-C18 | J9 | Beobachtungsäquivalenz | Interventions-TV $1/2$ |
| J-C19 | J9 | Abstraktionsscope | fünf exakte Eingriffe; Erweiterungs-TV $1/2$ |
| J-C20 | J10 | Standardisierung | Zielwerte $3/4,1/4$ |
| J-C21 | J10 | Zwei Quelle-Ziel-Familien | Zielwert $1$ versus $1/2$ |
| J-C22 | J11 | Markov-Fehler | L1 $11/50\le2/5$; TV $11/100\le1/5$ |
| J-C23 | J10 | Collider und S-Admissibilität | Konditionierung auf Collider/Nachfahren öffnet Pfad |

**Ausgeführter Stand der Beilage:** 23/23 Kontrollgruppen bestanden. Eine Kontrollgruppe kann mehrere Assertions enthalten; diese Zahl ist weder die Anzahl der zukünftigen Repo-Tests noch die Anzahl abgeschlossener Implementierungspakete. Die Budget-/Statusregeln der geplanten Produktions-APIs werden erst bei deren Implementierung geprüft.

## 21. Quellenregister und Rechercheumfang

Abruf-/Prüfdatum: **27. September 2026**. Die folgenden Einträge wurden über Primärquellen, Verlagsseiten, Autorenfassungen oder offizielle Projektdokumentation abgeglichen. „Geprüft“ bedeutet den jeweils angegebenen Umfang, nicht die Behauptung, jeden Beweis jedes Papers vollständig auditiert zu haben. Die oben ausgeschriebenen Kontrollfälle wurden unabhängig gerechnet.

| ID | Quelle / stabiler Link | Verwendung und Prüfstatus |
|---|---|---|
| S01 | Diebold & Mariano (1995), *Comparing Predictive Accuracy*. [DOI 10.1080/07350015.1995.10524599](https://doi.org/10.1080/07350015.1995.10524599) | Originalverfahren; bibliografische Angaben und Verlagsnachweis geprüft. Eigene HAC-Kontrollrechnung im Plan. |
| S02 | Diebold (2015), *Comparing Predictive Accuracy, Twenty Years Later: A Personal Perspective on the Use and Abuse of Diebold–Mariano Tests*. [DOI 10.1080/07350015.2014.983236](https://doi.org/10.1080/07350015.2014.983236) | Grenzen von Prognose-/Modellvergleichen; Verlagsnachweis und Zusammenfassung geprüft. Keine Behauptung eines vollständigen Volltextaudits. |
| S03 | Newey & West, *A Simple, Positive Semi-Definite, Heteroskedasticity and Autocorrelation Consistent Covariance Matrix*. [Original-NBER-Arbeit t0055](https://www.nber.org/papers/t0055) | Primärquelle zum HAC-Verfahren; NBER-Nachweis geprüft. Die im Plan verwendete endliche Konvention ist explizit angegeben. |
| S04 | Holm (1979), *A Simple Sequentially Rejective Multiple Test Procedure*. [Originalpaper als PDF](https://www.ime.usp.br/~abe/lista/pdf4R8xPVzCnX.pdf) | Originalarbeit und bibliografischer Nachweis gefunden; Holm-Kontrolle hier unabhängig gerechnet. |
| S05 | Buckingham (1914), *On Physically Similar Systems; Illustrations of the Use of Dimensional Equations*. [DOI 10.1103/PhysRev.4.345](https://doi.org/10.1103/PhysRev.4.345) | Originalquelle und Publikationsdaten geprüft; konkrete Nullraumrechnung unabhängig. |
| S06 | Chen et al. (2018), *Metamorphic Testing: A Review of Challenges and Opportunities*. [DOI 10.1145/3143561](https://doi.org/10.1145/3143561); [Autorenfassung](https://www.cs.hku.hk/data/techreps/document/TR-2017-04.pdf) | Autoren-/Originalnachweis geprüft; der konkrete SCF-Mutationskatalog ist eigener Entwurf. |
| S07 | Benveniste et al. (2018), *Contracts for System Design*. [DOI 10.1561/1000000053](https://doi.org/10.1561/1000000053); [institutioneller Nachweis](https://research-explorer.ista.ac.at/record/5677) | Fachlicher Anschluss; Metadaten und Autorenmaterial geprüft. Implementiert wird nur der ausdrücklich definierte funktionale Spezialfall. |
| S08 | JuliaIntervals, [IntervalArithmetic.jl](https://juliaintervals.github.io/IntervalArithmetic.jl/stable/), [IntervalRootFinding.jl](https://juliaintervals.github.io/IntervalRootFinding.jl/dev/), [TaylorModels.jl](https://juliaintervals.github.io/TaylorModels.jl/dev/) | Offizielle Dokumentation zu validierter Rechnung und nicht entschiedenen Bereichen geprüft. Kein Pflichtimport; rationale Erstversion ist eigenständig. |
| S09 | Hong, Ovchinnikov, Pogudin & Yap (2019), *SIAN: a tool for assessing structural identifiability of parametric ODEs*. [DOI 10.1093/bioinformatics/bty1069](https://doi.org/10.1093/bioinformatics/bty1069); [arXiv:1812.10180](https://arxiv.org/abs/1812.10180) | Primärnachweis und Methodenumfang geprüft; keine Abhängigkeit im Pflichtkern. |
| S10 | SciML, [StructuralIdentifiability.jl: Identifiability](https://docs.sciml.ai/StructuralIdentifiability/stable/identifiability/identifiability/) | Offizielle API-Dokumentation geprüft; besonders lokale/globale Aussagen und probabilistische Verfahrensparameter. |
| S11 | Saltelli et al. (2010), *Variance based sensitivity analysis of model output. Design and estimator for the total sensitivity index*. [DOI 10.1016/j.cpc.2009.09.018](https://doi.org/10.1016/j.cpc.2009.09.018) | Verlags-/Autorenverzeichnis und Originalpaper-Nachweis geprüft. Konventionen und analytische Kontrollen im Plan ausgeschrieben. |
| S12 | Kucherenko, Tarantola & Annoni (2012), *Estimation of global sensitivity indices for models with dependent variables*. [DOI 10.1016/j.cpc.2011.12.020](https://doi.org/10.1016/j.cpc.2011.12.020); [JRC-Originalnachweis](https://publications.jrc.ec.europa.eu/repository/handle/JRC64266) | Primärquelle und Zusammenfassung zum abhängigen Fall geprüft. Kein solcher Algorithmus wird hier vorausgesetzt. |
| S13 | Tibshirani, Barber, Candès & Ramdas (2019), *Conformal Prediction Under Covariate Shift*. [arXiv:1904.06019](https://arxiv.org/abs/1904.06019); [Autoren-Volltext](https://www.stat.berkeley.edu/~ryantibs/papers/weightedcp.pdf) | Relevante Abschnitte zu Covariate Shift, Gewichten, Testpunktmasse, Garantie und Split-Variante eingesehen. J-C15–17 sind eigene Kontrollen. |
| S14 | Rubenstein et al. (2017), *Causal Consistency of Structural Equation Models*. [arXiv:1707.00819](https://arxiv.org/abs/1707.00819); [UAI-Volltext](https://auai.org/uai2017/proceedings/papers/11.pdf) | Insbesondere Definition 3 der exakten Transformation mit surjektiver ordnungserhaltender Eingriffsabbildung eingesehen. Eigener XOR-Kontrollfall. |
| S15 | Pearl & Bareinboim (2014), *External Validity: From Do-Calculus to Transportability Across Populations*. [arXiv:1503.01603](https://arxiv.org/abs/1503.01603); [Volltext](https://arxiv.org/pdf/1503.01603) | S-Admissibilität und Standardisierung für Pretreatment-Kovariaten, insbesondere Definition 8/Korollar 1, eingesehen. Kein Anspruch auf Implementierung des Gesamtverfahrens. |
| S16 | Michel & Siegle (2024), *Formal Error Bounds for the State Space Reduction of Markov Chains*. [arXiv:2403.07618](https://arxiv.org/abs/2403.07618); [DOI 10.1016/j.peva.2024.102464](https://doi.org/10.1016/j.peva.2024.102464) | Primärnachweis sowie die vorhandene SCF-Implementierung abgeglichen. J-C22 kontrolliert den konkret benutzten Spezialfall. |
| R01 | [SCF-Referenzstand](https://github.com/GenesisAeon/scoped-correspondence-formalism/tree/4a7ed38640ac7d393017eb5556291c879c3bceac) | Code-/Dokumentationsgrundlage dieses Plans; kein Nachweis des späteren Arbeitsstands. |
| R02 | [CLAUDE.md am Referenzcommit](https://github.com/GenesisAeon/scoped-correspondence-formalism/blob/4a7ed38640ac7d393017eb5556291c879c3bceac/CLAUDE.md) | Arbeitsregeln vollständig gelesen; in J0 erneut mit dem dann aktuellen Stand abgleichen. |

Die Quellenauswahl vermeidet ungeprüfte DOI-Angaben aus dem Gedächtnis. Bei der Implementierung eines optionalen Backends dessen **aktuelle konkrete Version** und Schnittstelle gesondert prüfen. Ein bekannter Methodenname ersetzt keinen Beleg für die tatsächlich programmierte Variante.

## 22. Bewusst zurückgestellte Erweiterungen

| Erweiterung | Voraussetzung für Aufnahme | Warum noch nicht Pflicht |
|---|---|---|
| Validierte transzendente Funktionen und ODE-Flüsse | Gepinnter verifizierter Backend, Rundungs-/Existenznachweise, unabhängige Flusskontrollen | Deutlich größerer Beweisumfang als rationale Ausdrücke |
| Allgemeine rationale ODE-Identifizierbarkeit | Isolierter SIAN-/SciML-Adapter mit dokumentierter Aussageklasse | Vorhandene Spezialfälle zuerst sauber verbinden |
| Vollständiges ID/sID für Transportabilität | Eigener Algorithmusplan, Gegenbeispielregister und Vollständigkeitsgrenzen | Die Standardisierungsregel ist ein klar abnehmbarer Anfang |
| Kontrafaktische Abstraktion | Explizite exogene Kopplung und stärkere Gleichheitsdefinition | Interventionelle Randverteilungen reichen dafür nicht |
| Sensitivität bei abhängigen Eingängen | Fachlich begründete gemeinsame Verteilung und passende Zerlegung | Unabhängige Sobol-Indizes wären irreführend |
| Allgemeine Driftgarantien | Exakt spezifizierte Driftklasse und passender Satz | Covariate Shift ist nur ein Spezialfall |
| Hierarchische Galaxienpopulation | Größere begründete Stichprobe, Auswahlfunktion, gemeinsame Likelihood und Datenzugang | Der bestehende kleine Pilot trägt keinen universellen Populationsanspruch |
| Zusätzliche Informationskriterien/Bayesvergleiche | Gemeinsames Beobachtungsmodell, identifizierbare Parameter und begründete Priors/Regularität | Keine automatische Reparatur eines gehaltenen Modellvergleichs |
| Allgemeine kategoriale Infrastruktur | Mehrere konkrete Anwendungsfälle, die bestehende kleine Kompositionsregeln überfordern | Identität, Assoziation und typisierte Verträge reichen zunächst |

Institutionentheorie wird hier nicht als Implementierungsziel empfohlen. Kategorielle Sprache kann die vorhandene Struktur erklären; eine große Abstraktionsbibliothek braucht einen nachgewiesenen praktischen Nutzen.

## 23. Was SCF nach diesem Ausbau zusätzlich leisten soll

Eine Nutzerin kann zwei Beziehungen kombinieren und bekommt den zulässigen gemeinsamen Scope, passende Uhren und eine nachvollziehbare Fehlergrenze. Für unterstützte Ausdrücke lässt sich der gesamte deklarierte Bereich prüfen. Bei Beobachtungsmehrdeutigkeit zeigt das System, welche Parameterkombination oder welche Entscheidung trotzdem bestimmbar bleibt.

Ein Prognosevergleich benennt Effekt und inferenzielle Grenzen. Eine Unsicherheitsanalyse berücksichtigt gemeinsame Parameteränderungen. Ein Kalibrierverfahren weist aus, wann gute Abdeckung mit unbrauchbar weiten Intervallen erkauft wird. Kausale Übertragung wird zu einer überprüften Aussage unter einem expliziten Modell und einer benannten Eingriffsmenge.

Das gewünschte Ergebnis ist eine präzisere Fähigkeit, Beziehungen zu begründen, zu begrenzen und gegebenenfalls zu widerlegen — mit genau angegebenem mathematischem und empirischem Geltungsbereich.
