# SCF: Themenbreite wissenschaftlich und implementierbar erweitern

**Konzept, Forschungsprotokolle und Übergabe an Claude Code**  
Stand: 24. September 2026  
Referenz: `GenesisAeon/scoped-correspondence-formalism`, Commit `bd87a445dec1611e5bf919f95e9e7019e1c32ea4`  
Status: ausgearbeiteter Vorschlag; die unten beschriebenen Erweiterungen sind noch nicht implementiert oder empirisch bestätigt.

## 1. Ziel und empfohlene Entscheidung

SCF soll an mehr Gegenständen zeigen können, **welche mathematische Struktur eine Übersetzung erhält, welche Information dabei verloren geht und welche Vorhersagen oder Entscheidungen dadurch tatsächlich besser werden**.

Die erste Ausbaurunde verbindet vier Gebiete:

1. **Warteschlangen und Rechenressourcen:** Laststöße, Rückstau und erstmaliges Erreichen einer Kapazitätsgrenze.
2. **Hydrologie:** schnelle und langsame Abflussreaktionen, Gedächtnis, zeitliche Aggregation und Niedrigwasserereignisse.
3. **Batteriealterung:** irreversible Veränderung, schwankende Beobachtungen und verbleibende Zeit bis zu einer festgelegten Kapazitätsgrenze.
4. **Kooperative Agenten:** Nutzen und Kosten zusätzlicher Information, komplementäre Beobachtungen und Fehlerübertragung durch Kommunikation.

Die Reihenfolge ist bewusst: Warteschlangen bieten genaue Kontrollfälle; Hydrologie ergänzt einen ersten externen Datenpiloten; Batterien erzwingen eine saubere Behandlung von Alterung und Zensierung; Agenten verbinden die vorhandenen Informationsmodule mit überprüfbaren Aufgaben.

**Erfolg bedeutet nicht, dass ein komplexeres Modell gewinnt.** Ein sauber belegtes Null- oder Negativergebnis ist ein abgeschlossenes Forschungspaket. Vorab festgelegte Auswertungen verhindern, dass das Projekt nur passende Beispiele sammelt.

Die hier vorgeschlagenen Modelle, Auswahlregeln, Schnittstellen und Akzeptanzkriterien sind ein eigener Arbeitsentwurf. Die Quellen am Ende belegen die verwendeten mathematischen Grundlagen und die Eigenschaften der Datenangebote; sie bestätigen keine noch nicht durchgeführten SCF-Experimente.

## 2. Anschluss an den geprüften Repo-Stand

Der GitHub-HEAD wurde für diesen Entwurf erneut geprüft und entspricht dem Referenzcommit. Die Quelltexte und bisherigen unabhängigen Befunde wurden herangezogen. **Für diesen Plan wurde keine erneute vollständige Testausführung vorgenommen.** Die Referenz enthält 74 `verify_*.py`-Skripte. Eine grüne CI bestätigt die tatsächlich ausgeführten Prüfungen, keine pauschale externe Validierung.

| Vorhandener Baustein | Konkreter Anschluss | Grenze, die erhalten bleiben muss |
|---|---|---|
| `correspondence/contract.py` | `ModelRef`, `StateMap`, `TimeMap`, `Scope`, `Residual`, `CorrespondenceReport` | Endliche geprüfte Zustands-/Zeitpaare sind kein globaler Beweis. |
| `docs/structural_relations.md` | Brückenkarten, Beziehungstyp, Erhaltenes, Verlorenes, Gegenbeispiel | Das Dokument trägt einen Review-Status. Neue Karten zunächst in diesem Status führen; keine automatische Beförderung zum akzeptierten Kern. |
| `closure/linear_memory_projection.py` | Elimination verborgener linearer Zustände; Matrixexponential-Kernel | Die vorhandene externe Anregung wirkt nur auf den beobachteten Skalar. Anregungen verborgener Zustände benötigen einen zusätzlichen Term. |
| `closure/generator_lumpability.py` | CTMC-Generatoren und `Q C = C Q_macro` | Markovschließung, Erwartungswertvergleich und Pfadkopplung sind unterschiedliche Aussagen. |
| `viability/` | Puffer, Grenzverletzungen, transiente Ausschläge und Eingriffsbudgets | Numerische Suche, kontinuierliche Aussage und zertifizierte Schranke getrennt ausweisen. |
| `validation/rolling_origin.py`, `scoring_rules.py` | Zeitlich korrekte Evaluation und Intervallbewertung | Der generische Backtest reicht Zeitreihenpräfixe weiter; externe Treiber und Verfügbarkeitszeiten benötigen zusätzliche Behandlung. |
| `validation/adaptive_interval_calibration.py` | Nachträgliche Intervallkorrektur | Bestehende ACI-inspirierte Heuristiken erben nicht automatisch einen allgemeinen Abdeckungssatz. |
| `identifiability/` | Profile, Sensitivität und nicht unterscheidbare Parameter | Flache Gitterdaten belegen keine globale Unbeschränktheit. |
| `observation/`, `information_decomposition/` | Beobachtungskanäle, Information und bivariate PID | Informationsmaße sind weder universelle Intelligenzmaße noch alleinige Kausalnachweise. |
| `data/real_data_manifest.json` | Herkunft, lokale Prüfsumme und Datenbeschreibung | Rohdaten, abgeleitete Daten und Simulationen unterscheiden; Herkunftsangaben nicht erfinden. |
| `scripts/run_verification_suite.py` | Vorhandene getrennte Mathe-, Daten- und Linkprüfung | Aktuelle Zuordnung nutzt Textmarker. Neue Datendomänen dürfen nicht versehentlich als reine Mathematik klassifiziert werden. |

Die vorhandenen Bereiche bleiben die primären mathematischen Module. Neue Domänennamen brauchen keine neue Vererbungshierarchie. Zunächst kleine zusätzliche Module in `dynamics`, `viability`, `closure` und `validation`; eine eigene Anwendungsschicht erst dann extrahieren, wenn mehrere Piloten dieselbe tatsächliche Schnittstelle benutzen.

## 3. Wissenschaftliche Leitfragen

### 3.1 Die ursprüngliche Beobachtung schärfen

Die Beobachtung „gleichmäßige Modelle übersehen das Kippen“ wird in getrennte prüfbare Hypothesen übersetzt:

| Hypothese | Kontrollierter Vergleich | Mögliche alternative Erklärung |
|---|---|---|
| Der zeitliche Verlauf eines Treibers ist entscheidend. | Gleiche Gesamtlast, andere Reihenfolge, Dauer oder Spitzenhöhe. | Schon ein lineares System mit zeitabhängigem Eingang kann das erklären. |
| Ein einzelner Erholungsmaßstab reicht nicht. | Eine gegen zwei Zeitskalen bei gleicher Beobachtungsdefinition. | Die zweite Zeitskala verbessert nur die Anpassung, nicht neue Vorhersagen. |
| Rückkopplung erzeugt Nichtlinearität. | Lineare gegen begründet nichtlineare Dynamik bei gleichem Treiber und Messmodell. | Nichtlinearität sitzt im Beobachtungsprozess oder in einer Randbedingung. |
| Mittelwerte unterschätzen das Risiko. | Erwartung/Fluidmodell gegen Ereigniswahrscheinlichkeit. | Fehlkalibrierung, kleine Stichprobe oder falsche Rauschannahme. |
| Zusätzliche Information verbessert Entscheidungen. | Kommunikation randomisiert ein-/ausschalten; Informationsbudget konstant halten. | Redundanz, falsche Information oder zusätzliche Kosten neutralisieren den Nutzen. |

**Exponentielles Treiberwachstum ist eine Kandidatenform, keine Voraussetzung.** Konstante Mittelwerte mit kurzen Laststößen, zeitverzögerte Reaktionen, schrumpfende Reserven und lineare transiente Verstärkung liefern andere Mechanismen. Jedes Experiment benennt, ob es eine Grenzberührung, Grenzverletzung, irreversible Schädigung, Instabilität oder einen Attraktorwechsel untersucht.

### 3.2 Vier Arten von Ergebnis

- **Strukturaussage:** Welche Gleichung oder Operation bleibt bei einer konkreten Abbildung erhalten?
- **Numerisches Ergebnis:** Was liefern ein Algorithmus und seine Fehler-/Konvergenzprüfungen?
- **Empirisches Ergebnis:** Welche Vorhersagegüte zeigt sich auf benannten zurückgehaltenen Daten?
- **Interventionsergebnis:** Welche Änderung verursacht unter einer dokumentierten Versuchsanordnung welche Wirkung?

Diese Angaben ergänzen die bestehenden Brückenkarten. Sie bilden keine Rangliste: Ein numerisch exaktes Spiel beantwortet eine andere Frage als ein unsicherer Umwelt-Datenpilot.

## 4. Gemeinsames fachliches Fundament

### 4.1 Zustände, Eingänge und Beobachtung getrennt modellieren

Als Notationsrahmen, nicht als obligatorische universelle Basisklasse:

\[
dX_t=f(X_t,U_t,\theta)\,dt+G(X_t,U_t,\theta)\,dW_t,
\qquad Y_k\sim p_\eta(\,\cdot\mid X_{[a_k,b_k]},U_{[a_k,b_k]}).
\]

Für deterministische Systeme ist `G=0`; für Warteschlangen kann ein Sprungprozess die SDE ersetzen. Ein täglicher Abfluss ist häufig ein Zeitintervallmittel, eine Kapazitätsmessung ein Versuchsergebnis und ein Agentensignal eine diskrete Beobachtung. Beobachtungen müssen nicht punktweise Zustände sein.

Jeder Pilot deklariert:

- Zustandsvariablen, Einheiten, Vorzeichen und zulässige Bereiche;
- Eingangsgrößen und den Zeitpunkt, zu dem diese bekannt sind;
- Messoperator, Aggregationsintervall, Fehlerannahmen und Qualitätsflags;
- Anfangszustand und Umgang mit nicht beobachteten Anfangswerten;
- Zielgröße, Horizont, Grenzkonvention und Evaluationspopulation.

### 4.2 Die erste Brücke: Bestände und Rückstau

Ein Bestand erfüllt im einfachsten Fall

\[
\dot S(t)=I(t)-O(t).
\]

Eine kontinuierliche Warteschlangen-Näherung erfüllt, solange sie positiv ist,

\[
\dot q(t)=a(t)-s(t).
\]

Mit festem Grenzwert `K` bildet `R=K-q` den Rückstau auf eine verbleibende Reserve ab:

\[
\dot R=s-a.
\]

**Genaue Aussage:** Bei identischen passend übersetzten Ein-/Ausgängen und Anfangswerten stimmen diese idealisierten Gleichungen bis zum Eintritt einer nicht mitübersetzten Randregel überein. An `q=0` benötigt das Fluidmodell Reflexion; für `R` entspricht das einer oberen Begrenzung. Ein physischer Wasserspeicher kann bei Leerstand Nachfrage nicht mehr bedienen; eine unbeschränkte Warteschlange wächst weiter. Diese Fortsetzungen sind nicht gleich.

Die Brückenkarte umfasst deshalb den gestoppten Prozess bis zum ersten Grenzereignis und benennt die Fortsetzungsregeln separat. Für Batterieenergie gilt ebenfalls eine Bilanz, aber Ladezustand und alternde nutzbare Kapazität sind zwei verschiedene Größen. Kapazitätsverlust wird nicht als bloßer leerer Speicher behandelt.

**Negativtest:** Ein konstanter Abfluss und ein speicherabhängiger Abfluss `kS` dürfen nicht durch bloße Umbenennung als identische Dynamik durchgehen. Ebenso muss eine Änderung des Grenzwerts `K(t)` im Transformationsgesetz den zusätzlichen Term `dK/dt` erzeugen.

### 4.3 Beziehungen zwischen stochastischen Modellen

Für eine endliche CTMC mit Zeilenwahrscheinlichkeiten gilt `p'(t)=p(t)Q`. Bei einer Zustandsaggregation `C` lautet eine exakte Schließungsbedingung

\[
Q_X C=CQ_Y \quad\Longrightarrow\quad e^{tQ_X}C=C e^{tQ_Y}.
\]

Die vorhandenen Generator-Lumpability-Funktionen wiederverwenden. Ein passend ähnlicher Mittelwert beweist diese Identität nicht. Ein Vergleich zweier separat gezogener Zufallspfade ist ebenfalls kein Test auf gleiche Verteilung. Zunächst endliche Generatoren, endliche Ereignisse und überprüfbare Aggregationen verwenden; keine allgemeine stochastische Konjugations-API vorweg bauen.

### 4.4 Ereignisse sind eigene Objekte

Für eine Grenzfunktion `g` lautet ein möglicher Zeitpunkt

\[
\tau_{\le}=\inf\{t\ge0:g(X_t)\le0\}.
\]

Das ist das **erste Erreichen** der geschlossenen Grenzmenge. Eine strikte Verletzung `g<0` muss gesondert definiert werden. Selbst wenn zwei Infima gleich sind, kann am Horizont eine Berührung vorliegen, ohne dass dort bereits eine strikte Verletzung aufgetreten ist. Aus `infimum <= H` deshalb nicht allgemein auf ein realisiertes striktes Ereignis schließen.

Ein Ereignisbericht enthält mindestens:

`event_definition`, `boundary`, `comparison`, `horizon`, `time_resolution`, `initial_status`, `event_observed`, `first_event_time`, `censoring`, `numerical_method`, `error_statement`.

Bei täglichen Daten ist der Beginn höchstens täglich aufgelöst. Bei vorzeitig endenden Messungen lautet das Ergebnis rechtszensiert; weder `0`, noch ein erfundener späterer Zeitpunkt, noch „tritt niemals ein“ einsetzen.

## 5. Gemeinsames Daten- und Evaluationsprotokoll

### 5.1 Herkunft und Datenmodell

Den bestehenden Manifestmechanismus erweitern. Ein Schemaentwurf muss mit alten Einträgen kompatibel bleiben. Für neue Quellen ergänzen:

| Feld | Zweck |
|---|---|
| `dataset_id`, `source_url`, `version_or_release`, `retrieved_at_utc` | Nachvollziehbare Herkunft und fixierter Stand. |
| `raw_sha256`, `derived_sha256`, `processing_script`, `processing_commit` | Rohquelle und Transformation auseinanderhalten. Bei nicht gespeicherten Originalbytes keinen Hash erfinden. |
| `license`, `license_source`, `redistribution_status` | Tatsächlich geprüfte Nutzungsangaben; unklar bleibt unklar. |
| `entity_id`, `time_start`, `time_end`, `available_at` | Messintervall, Objekt und Informationsverfügbarkeit. |
| `units`, `aggregation`, `quality_flag`, `missing_reason` | Semantik und Datenqualität. |
| `selection_rule`, `excluded_entities`, `exclusion_reasons` | Auswahl unabhängig vom späteren Modellerfolg nachvollziehen. |
| `origin_type` | `observed`, `derived`, `simulated` oder `model_filled`. |

Nicht jedes reale Archiv liefert historische Verfügbarkeitszeiten. Dann das Feld als unbekannt markieren und nur eine retrospektive Auswertung behaupten. **Automatisch erzeugte Zeitstempel sind kein Ersatz für historische Datenverfügbarkeit.**

Große Downloads bleiben außerhalb des Repo. Kleine redistribuierbare Ausschnitte, Transformationsskript, Checksummen und ein Auswahlmanifest reichen für den Standardlauf. Ohne geklärte Weiterverteilung: lokaler Downloader plus synthetische Parser-Fixture; den fehlenden Datenlauf ausdrücklich als nicht ausgeführt berichten.

### 5.2 Zeit, Objekte und Testdaten

1. Datenprüfung und Auswahlregeln vor der Modellbewertung festlegen.
2. Zeitlich trainieren, abstimmen und testen. Keine zufällige Zeilenmischung bei Zeitreihen.
3. Parameter, Skalierung, Schwellen, Merkmalswahl, Imputation und Intervallkalibrierung nur aus dem jeweils verfügbaren Präfix lernen.
4. Zusätzlich nach Objekten trennen, wenn eine Übertragung auf neue Einzugsgebiete oder Batterien behauptet wird.
5. Zukunftstreiber unterscheiden: bekanntes Versuchsprogramm, wirklich verfügbare Vorhersage, angenommene Fortsetzung oder später gemessener Eingang.
6. Alle Modelle erhalten dieselben zulässigen Informationen und dasselbe Auswertungsziel. Größere Modelle bekommen kein exklusives Zukunftswissen.
7. Überlappende Vorhersagehorizonte erzeugen abhängige Fehler. Ergebnisse pro Objekt und Zeitblock ausgeben; keine unabhängigen Bernoulli-Versuche aus überlappenden Tagen konstruieren.
8. Finale Testdaten erst nach Fixierung von Modellwahl und Protokoll auswerten. Nachträgliche Änderungen als neue explorative Runde kennzeichnen.

**Zwei Modi explizit benennen:** `conditional_hindcast` darf später beobachtete Eingänge verwenden und beantwortet „Wie reagiert das Modell auf diese bekannten Eingänge?“. `forecast_as_of_origin` darf nur zum Prognoseursprung verfügbare Information verwenden. Diese Ergebnisse nicht in derselben Rangliste vermischen.

### 5.3 Ergebnisse und Metriken

| Frage | Primäre Ausgabe | Ergänzung |
|---|---|---|
| Wie gut sind Zustands-/Messprognosen? | MAE in benannter Einheit; bei Bedarf RMSE | Fehler pro Horizont und Objekt. |
| Sind Intervalle nützlich? | Abdeckung, mittlere Breite, vorhandener Interval Score | Nominalniveau und Fallzahl immer gemeinsam. |
| Ist ein Grenzereignis wahrscheinlich? | Brier Score `mean((p-event)^2)` | Ereignisrate, Kalibration und Vergleich gegen Trainings-Basisrate. |
| Wann tritt ein Ereignis ein? | Zeitfehler nur bei sinnvoll vergleichbaren beobachteten Ereignissen | Zensierung separat; später zensierungsgeeignete Survival-Auswertung. |
| Ist eine Verteilung plausibel? | Log-Score, falls eine tatsächlich normierte prädiktive Verteilung vorliegt | Kein Pseudo-Log-Score nur aus einem Intervall. |
| Hilft eine Intervention? | Erfolg/Risiko und Ressourcenverbrauch | Kostenparameter sowie unzulässige Fälle ausweisen. |

Wenige vorab gewählte primäre Maße. Weitere diagnostische Maße dürfen nicht nachträglich zum alleinigen Erfolgskriterium werden. Ungültige Scores wie ein NSE bei konstanter Zielreihe als undefiniert behandeln.

### 5.4 Bericht und Reproduzierbarkeit

Ein kleiner serialisierbarer Bericht genügt; die vorhandenen Reporttypen nicht ohne Not ersetzen. Neue Berichte enthalten `schema_version`, Commit, Paketversionen, Daten- und Konfigurationshash, Seeds, trainierte Parameter, Split-IDs, einzelne Prognosen und aggregierte Ergebnisse. Fehlende Werte werden JSON-`null` plus Statusgrund; kein unkontrolliertes `NaN` oder `Infinity`.

Jede Schlussfolgerung verknüpft eine konkrete Behauptung mit einer Brückenkarte oder einer Ergebniszeile. `passed` bezeichnet eine Prüfung; ein positiver empirischer Effekt erhält ein separates Ergebnisfeld.

## 6. Paket B0 — Zeiteinheiten und numerische Aussagegrenzen

**Priorität: vor neuen kontinuierlichen Sicherheitsbehauptungen.** Dokumentations- und Datenvorbereitung können unabhängig davon erfolgen.

Im Referenzcommit verwendet `_analytic_component_critical_times` in `viability/transient_amplification.py` eine absolute Diskriminantenschwelle von `±1e-9`. Dadurch kann dieselbe Trajektorie in anderen Zeiteinheiten dem falschen Eigenwertfall zugeordnet werden.

Das bereits unabhängig reproduzierte Gegenbeispiel:

\[
A=\begin{pmatrix}-0.1&-10\\10&-0.1\end{pmatrix},\quad x_0=(0,1),\quad H=10,
\quad |x_1|\text{-Grenze}=0.95.
\]

Hier ist `x1(t)=-exp(-0.1*t)*sin(10*t)`. Das globale Betragsmaximum über diesen Horizont liegt am ersten Ausschlag bei

\[
t_*={\arctan(100)\over 10}\approx0.15607966601082315,
\qquad |x_1(t_*)|\approx0.9844639845000666.
\]

Unter `A_new=c*A`, `H_new=H/c` mit `c=1e-6` bleibt die Zustandskurve identisch. Der aktuelle Code meldete dennoch etwa `0.1862815091` und `no_violation_in_horizon`; korrekt bleibt `transient_violation`.

**Arbeitsauftrag:**

1. Gegenbeispiel zuerst mit dem aktuellen HEAD reproduzieren; bei zwischenzeitlichem Fix vorhandene Regression prüfen.
2. Für `H>0` mit dimensionsloser Zeit `s=t/H` und Matrix `B=H*A` arbeiten; `H=0` gesondert behandeln.
3. Diskriminantenberechnung und Zweigwahl skalenbewusst und nahe mehrfachen Wurzeln numerisch stabil gestalten. Dimensionslosigkeit allein behebt Auslöschung nahe einer doppelten Wurzel nicht.
4. Ein numerisch unsicheres Vorzeichen nicht als bewiesene Doppelwurzel ausgeben. Eine stabile Grenzformel, präzisere Rechnung oder ein explizit unbestimmtes Ergebnis verwenden.
5. Auch absolute Schwellen für Stabilität, Ableitungskoeffizienten und Abtastdichte auf Einheitenabhängigkeit prüfen, soweit sie denselben Klassifikationspfad beeinflussen.

**Abnahme:** gleiche Höhe und Klassifikation für `c in {1e-6,1,1e6}`, skaliertes Peak-Timing; schneller reeller Ausschlag `1000*t*exp(-100*t)` weiterhin korrekt; Endpunkte, Nullmatrix und exakt doppelte Wurzeln abgedeckt. Für die gut konditionierten Referenzfälle Zielabweichung der Höhe `<=1e-10`; Zeitfehler relativ zur charakteristischen Zeit prüfen. Keine pauschale Genauigkeitsgarantie auf beliebig schlecht konditionierten Matrizen.

Für Spline-Extrema explizit weiter zwischen dem Extremum des Interpolanten und dem Extremum der wahren Trajektorie unterscheiden. Eine kleinere Schrittweite ist eine Konvergenzprüfung, noch keine rigorose Fehlerschranke.

## 7. Paket B1 — Gemeinsame Versuchskonventionen

**Lieferumfang:**

- `DOMAIN_EXPANSION_ROADMAP.md` als kompakte Repo-Roadmap dieses Plans, mit Status je Teilaufgabe;
- `docs/domain_expansion_protocol.md`: Mess-/Ereignis-/Zeitkonventionen und Berichtsschema;
- vorhandenes Datenmanifest rückwärtskompatibel erweitern;
- kleine Hilfen für `available_at`-Filterung, Ergebnisserialisierung und Ereignisdefinition nur dort ergänzen, wo mindestens ein Pilot sie benutzt;
- Testgruppenzuordnung für neue Verifikationsskripte explizit registrieren, zunächst mit Fallback für Altbestände;
- veraltete feste Testzahlen in README aktualisieren oder durch einen Hinweis auf den aktuellen Runner ersetzen.

**Abnahme:**

1. Änderungen ausschließlich an Daten mit `available_at > origin` verändern keine davor ausgegebene Prognose, Schwelle, Parameterschätzung oder Intervallbreite.
2. Zukunftstreiber im Hindcast-Modus verändern die Hindcast-Ausgabe erwartungsgemäß; derselbe Zugriff ist im Prognosemodus nicht zugelassen.
3. Fehlende und modellergänzte Zielwerte werden nicht als gemessene Testwerte gezählt.
4. Ein als Datenprüfung registriertes neues Skript wird vom Datenjob tatsächlich ausgewählt.
5. Der Standardtest benötigt weder Netzwerkzugriff noch Zugangsdaten.

**Nicht vorziehen:** allgemeine Datenbank, Plugin-Framework, universeller Simulator oder umfassende Schema-Migration aller Altmodule. Das Protokoll wird an den ersten Piloten erprobt.

## 8. Paket B2 — Warteschlangen: von Lastmittelwerten zu Ereignisrisiken

### 8.1 Forschungsfrage

Wann verliert eine gemittelte Lastbeschreibung die Information, die für ein kurzfristiges Kapazitätsereignis nötig ist? Drei verschiedene Modelle getrennt auswerten: deterministischer Fluidrückstau, zeitdiskrete Arbeitslast und stochastische Kundenzahl.

### 8.2 Deterministischer Kontrollfall

Für stückweise konstante Ankunfts- und Bedienraten kann der reflektierte Fluidrückstau jedes Intervall exakt durchlaufen:

\[
q(t+\Delta)=\max\{0,q(t)+(a-s)\Delta\}.
\]

Diese Endpunktformel gilt auf einem Intervall mit konstantem Nettoeingang. Bei wechselnden Raten alle Wechselzeitpunkte berücksichtigen. Grenzereignisse innerhalb des Intervalls analytisch bestimmen, nicht nur Endpunkte vergleichen.

**Festes Beispiel:** `q0=0`, Bedienrate `s=1`, Horizont `H=10`, Schwelle `K=5`.

- Gleichmäßige Ankunftsrate `a=0.8`: gesamte Ankunftsmenge 8, Rückstau stets 0.
- Laststoß `a=4` während `[0,2]`, danach 0: gleiche Gesamtmenge 8, Maximum `q=6` bei `t=2`, erstes Erreichen von 5 bei `t=5/3`.

Das Beispiel braucht weder exponentielles Wachstum noch nichtlineare innere Dynamik. Es isoliert den Verlust zeitlicher Information durch Mittelung. Über die Abbildung `R=5-q` entsteht gleichzeitig eine präzise Bestands-Brückenkarte bis zum ersten Leerstand.

### 8.3 Stochastische Referenz

Eine M/M/1-Warteschlange hat Poisson-Ankünfte mit Rate `lambda`, unabhängige exponentielle Bedienzeiten mit Rate `mu` und einen Server. Für die unbeschränkte stationäre Version gilt bei `rho=lambda/mu<1`: `pi_n=(1-rho)*rho**n` und `E[N]=rho/(1-rho)` [S3].

**Die stationäre Randwahrscheinlichkeit `P(N>=K)` ist nicht `P(max_{t<=H} N_t>=K)`.** Für das zweite Ziel die Zustände `0,...,K` verwenden und `K` absorbierend machen. Mit Zeilenkonvention:

\[
P(\tau_K\le H)=[p_0 e^{HQ_{\mathrm{abs}}}]_K.
\]

Vor Erreichen von `K` ist diese endliche Konstruktion exakt für das Erreichungsereignis der unbeschränkten M/M/1-Kette; eine entfernte künstliche obere Abschneidegrenze ist nicht erforderlich.

Bei stückweise konstanten Raten die Matrixexponentiale in zeitlicher Reihenfolge multiplizieren. Ein gemittelter Generator erzeugt im Allgemeinen eine andere Entwicklung. Ein ereignisbasierter Simulator mit festem Seed dient als zweite Umsetzung; beim nächsten Ratenwechsel neu ansetzen, statt ein Ereignis unter veralteter Rate über den Wechsel hinweg auszuführen.

**Abnahme:**

- `H=0`, bereits erreichtes `K`, `lambda=0`, `mu=0` und ungültige Raten;
- reine Ankünfte: `P(tau_K<=H)=P(Poisson(lambda*H)>=K-n0)`;
- Referenz `lambda=1, mu=2, K=2, n0=0, H=1`: ungefähr `0.1777365760981911`;
- nur Ankünfte mit `lambda=1, K=2, H=1`: `1-2/e ≈ 0.2642411176571153`;
- Simulation stimmt innerhalb einer vorab festgelegten Monte-Carlo-Toleranz mit der analytischen Referenz überein; analytische Identitäten tragen die harten deterministischen Tests;
- Kapazität **erreichen**, einen neuen Auftrag **ablehnen** und eine Wartezeitgrenze **überschreiten** sind verschiedene Ereignistypen;
- Mittelwertmodell darf bei stochastischem Risiko keinen deterministischen Sicherheitsbeweis ausgeben.

### 8.4 Optionale Trace-Anbindung

Google veröffentlicht Cluster-Traces samt Schema [S4]. Ein beschränkter Ausschnitt kann später zeitliche Lastmuster liefern. Ressourcenverbrauch und Scheduler-Zustände sind aber nicht automatisch ein beobachteter Ein-Server-Warteprozess. Vor Verwendung klären, ob Ankunft, Start, Ende, Zensierung, Maschinenwechsel und Bedienbedarf tatsächlich rekonstruierbar sind.

Der erste Abschluss von B2 bleibt ein **synthetisch und analytisch validierter Rechenressourcen-Pilot**. Ein nur mit realen Lastmustern getriebener Simulator heißt `trace_driven_simulation`, nicht extern validierter Scheduler. Keine unbeschränkten Cloud-Abfragen oder Großdownloads als Testvoraussetzung.

**Vorgeschlagene Dateien:** `dynamics/queueing.py`, `viability/first_passage_ctmc.py`, `validation/queueing_pilot.py`, zugehörige Matheprüfungen, `docs/queueing_pilot.md`. Vor dem Anlegen ähnliche bestehende Funktionen suchen.

## 9. Paket B3 — Hydrologie: Zeitskalen und beobachteter Abfluss

### 9.1 Daten und präzise Fragestellung

CAMELS-DE v1.0 beschreibt tägliche hydrometeorologische Reihen und Attribute für 1582 deutsche Einzugsgebiete. Das Datenpapier unterscheidet gemessene bzw. beobachtungsbasierte Reihen von simuliertem Abfluss und abgeleiteter potenzieller Verdunstung; letztere ist keine direkte Verdunstungsmessung [S1]. Den DOI-Release fixieren, keine Versionsstände still vermischen.

**Erste Frage:** Verbessert ein Modell mit zwei Abfluss-Zeitskalen gegenüber einem Speicher die zurückgehaltene Abflussvorhersage und die Beschreibung niedriger Abflüsse? Der erste Pilot schätzt keine direkt beobachtete Gesamtwasserreserve und beweist keinen ökologischen Kipppunkt.

### 9.2 Modelltreppe

| Modell | Zweck |
|---|---|
| Persistenz des zuletzt beobachteten Abflusses | Schwierigkeit kurzer Horizonte sichtbar machen. |
| Saisonaler Trainingsreferenzwert | Jahresgang berücksichtigen. |
| Ein lineares Reservoir | Eine Reaktionszeit als mechanistische Referenz. |
| Zwei parallele lineare Reservoirs | Zwei Reaktionszeiten mit gleichem Eingang und Messoperator. |
| Erst in einer Folgeversion: nichtlinearer Abfluss/Schnee-/Verdunstungsbaustein | Nur bei klar benannter Restabweichung und ausreichenden Eingangsgrößen. |

Für Reservoir `j`:

\[
\dot S_j=\alpha_j u(t)-k_j S_j,\qquad
q(t)=\sum_j k_j S_j(t),\quad \alpha_j\ge0,\quad \sum_j\alpha_j=1.
\]

Für einen ersten reduzierten Niederschlags-Abfluss-Piloten darf `u=cP` mit `0<=c<=1` gesetzt werden. `c` ist dann ein effektiver, ausschließlich auf Trainingsdaten geschätzter Abflussanteil. **Das ist keine vollständige Wasserbilanz mit identifizierter tatsächlicher Verdunstung.** Schnee, Eingriffe und stark veränderliche Verluste können den Geltungsbereich verletzen und sind im Bericht sichtbar zu halten.

Bei konstantem Eingang über ein Intervall:

\[
S_j(t+\Delta)=e^{-k_j\Delta}S_j(t)
+\alpha_j u\,{1-e^{-k_j\Delta}\over k_j}.
\]

Für `k_j→0` den stetigen Grenzfall `S_j+alpha_j*u*Delta` verwenden, numerisch etwa mit `expm1`. Der mittlere modellierte Abfluss über das Intervall folgt aus der Bilanz:

\[
\bar q={\sum_j S_j(t)+u\Delta-\sum_j S_j(t+\Delta)\over\Delta}.
\]

Den täglichen Messwert mit diesem Intervallmittel vergleichen, sofern das Datenfeld so definiert ist. Einen Endpunktwert nicht stillschweigend als Tagesmittel behandeln.

**Kontrollzahlen:** `S0=3`, `u=2`, `k=0.5`, `Delta=1`, ein Reservoir: `S1≈3.393469340287367`, mittlerer Abfluss `≈1.6065306597126332`.

### 9.3 Gedächtnisbrücke

Für beliebigen Eingang entsteht im linearen Modell ein Faltungskern

\[
q(t)=\sum_j k_j S_j(0)e^{-k_jt}
+\int_0^t\left(\sum_j\alpha_j k_j e^{-k_j(t-s)}\right)u(s)\,ds.
\]

Der Zwei-Speicher-Kern ist damit eine gewichtete Summe zweier Exponentialkerne. Die Darstellung ist unter den genannten Modellannahmen exakt. Sie validiert noch nicht die tatsächlichen physikalischen Speicher eines Einzugsgebiets.

Bei einer allgemeineren Blockreduktion mit Anregung verborgener Zustände,

\[
\dot x=Ax+Bz+f_x(t),\qquad \dot z=Cx+Dz+f_z(t),
\]

kommt neben dem vorhandenen Kernel `B exp(Du) C` und Anfangsterm ein weiterer Term hinzu:

\[
\int_0^t B e^{D(t-s)} f_z(s)\,ds.
\]

Claude soll diesen Term entweder sauber implementieren und unabhängig prüfen oder die Hydro-Faltung zunächst direkt implementieren. Die bisherige API darf nicht mit einem in Wahrheit zusätzlich erzwungenen verborgenen Block aufgerufen werden, als wäre dessen Anregung null. Grundlage der Projektionsperspektive: [S5]; die konkrete Reservoirrechnung oben ist die Herleitung für diesen Pilot.

### 9.4 Datenprotokoll

- Zunächst sechs Einzugsgebiete als überschaubares technisches Pilotpanel, nicht als repräsentative Deutschlandstudie.
- Auswahl vor Score-Berechnung anhand verfügbarer Metadaten und Datenqualität: ausreichend lange beobachtete Abflussreihe, geringe Lücken, verschiedene Rückhalte-/Abflusscharakteristika, dokumentierter Umgang mit Schnee und Regulierung. Keine Auswahl nach dem Gewinn des Zwei-Speicher-Modells.
- IDs, Auswahlregel, ausgeschlossene Kandidaten und Release festhalten. Konkrete IDs erst nach tatsächlicher Metadatenprüfung festlegen.
- Vorschlag bei gemeinsamer Datenverfügbarkeit: Training 1991–2005, Abstimmung 2006–2010, finaler Test 2011–2020. Bei ungeeigneter Abdeckung vor Modellbewertung auf eine dokumentierte alternative Zeitteilung wechseln.
- Den Zustand am Beginn jedes Auswertungsfensters aus vergangenem Eingang fortschreiben; Warm-up ausschließlich vor dem bewerteten Fenster. Unsicherheit verborgener Startspeicher prüfen.
- Abfluss `m³/s` und flächenbezogenen Abfluss `mm/Tag` mit dokumentierter Gebietsfläche umrechnen: `q_mm_day=86.4*q_m3_s/area_km2`.
- Modellergänzte Abflüsse nicht als beobachtete Zielwerte verwenden. Vortrainierte HBV-/LSTM-Ausgaben sind nur eine faire Vergleichsreferenz, wenn deren Trainingszeitraum zum eigenen Split passt.

### 9.5 Zwei Auswertungen

**A: Bedingter Hindcast.** Tatsächlich beobachteten Niederschlag verwenden, Parameter trainieren und auf späteren Zeitblöcken unverändert auswerten. Vergleicht Reaktionsmodelle unter bekanntem Eingang. Keine operative Wetter-/Abflussvorhersage behaupten.

**B: Prognose vom Ursprung.** Erst als separat markierte Teilaufgabe: zukünftigen Niederschlag durch eine aus dem Trainingspräfix bestimmte Annahme oder eine historisch verfügbare Vorhersage bereitstellen. Identische Eingänge für alle Modelle. Wenn keine solche Quelle implementiert ist, bleibt B explizit zurückgestellt.

Primäre Auswertung: MAE des Abflusses und Fehler in Niedrigwasserfenstern. Für Ereignisse einen Trainingsschwellenwert, zum Beispiel das 10-%-Quantil beobachteten Trainingsabflusses, vorab fixieren; Nullschwelle bei intermittierenden Flüssen gesondert behandeln. Ereignisbeginn, Dauer und Schwellenvergleich tagesgenau definieren. Für saisonale Quantile den Kalendermechanismus vorab festlegen.

### 9.6 Abnahme

1. Reservoir-Update gegen geschlossene Lösung; Tagesbilanz gegen unabhängig integrierten Abfluss.
2. Zwei gleiche Raten `k1=k2` reduzieren auf eine Zeitskala; `alpha2=0` und passender zweiter Anfangszustand auf den Ein-Speicher-Fall.
3. Nichtnegative Eingänge und Zustände erzeugen im definierten Modell keine negativen Speicher oder Abflüsse.
4. Exakte Zustandsdarstellung und Faltung einschließlich Anfangsterm stimmen auf Kontrollfällen überein.
5. Verschiedene Anfangsaufteilungen bei gleicher beobachteter Anfangsgröße als Identifizierbarkeitsfall untersuchen. Labeltausch `1↔2` berücksichtigen, z. B. durch `k_fast>=k_slow`.
6. Mindestens ein Fall zeigt, wann die Ein-Speicher-Näherung genügt; ein anderer kontrollierter Fall zeigt unterschiedliche zwei Zeitskalen.
7. Panel vollständig berichten, auch wenn die zweite Zeitskala keinen Testgewinn bringt. Keine Signifikanzbehauptung aus einer kleinen Zahl korrelierter Gebiete.

**Vorgeschlagene Dateien:** `dynamics/linear_reservoirs.py`, `validation/hydrology_pilot.py`, `docs/hydrology_pilot.md`, Datenadapter/Manifest und getrennte Mathe-/Datenprüfungen.

## 10. Paket B4 — Stochastische Reserven und Erstpassage

**Neue Fähigkeit:** Aus einem positiven erwarteten Pufferstand folgt keine verschwindende Wahrscheinlichkeit einer zwischenzeitlichen Grenzerreichung. Das Repo erhält eine kleine, exakt überprüfbare Referenz für diesen Unterschied.

### 10.1 Geschlossener Referenzfall

Für den bis zur unteren Grenze betrachteten Prozess

\[
X_t=x_0+\mu t+\sigma W_t,\quad x_0>0,\quad \sigma>0,
\quad \tau_0=\inf\{t\ge0:X_t\le0\}
\]

gilt mit der Standardnormalverteilungsfunktion `Phi`:

\[
P(\tau_0\le H)=
\Phi\!\left({-x_0-\mu H\over\sigma\sqrt H}\right)
+\exp\!\left(-{2\mu x_0\over\sigma^2}\right)
\Phi\!\left({-x_0+\mu H\over\sigma\sqrt H}\right).
\]

Grundlage sind die Erstpassage-/Maximumsresultate für Brownsche Bewegung mit Drift [S6, S15]. Die Vorzeichenkonvention hier betrifft eine **untere** Grenze und muss in der Implementierung mit der Herleitung übereinstimmen. Als unabhängige numerische Kontrolle lässt sich die Dichte `f(t)=x0/(sigma*sqrt(2*pi*t**3))*exp(-(x0+mu*t)**2/(2*sigma**2*t))` von 0 bis H integrieren.

Kontrollwerte bei `x0=1, sigma=1, H=1`:

- `mu=0`: `2*Phi(-1)≈0.31731050786291415`.
- `mu=1`: `≈0.09041777356648555`, obwohl `E[X1]=2`.
- Für positive Drift ist die Wahrscheinlichkeit eines jemaligen Erreichens `exp(-2*mu*x0/sigma**2)`; das ist eine Modellaussage für den unendlichen Horizont, keine aus einem endlichen Scan extrapolierte Aussage.

### 10.2 Implementationsgrenzen

- `H=0`, `x0<=0` und `sigma=0` separat behandeln. Bei `sigma=0` die deterministische Gerade und die definierte Berührungskonvention verwenden.
- Exponentialfaktor und kleine Normalverteilungswahrscheinlichkeit im Lograum kombinieren; ein Zwischenüberlauf darf nicht eine mathematisch endliche Wahrscheinlichkeit zerstören.
- Große Verstöße gegen `[0,1]` als Fehler melden. Nur begründete kleine Rundungsabweichungen korrigieren.
- Zeitumrechnung `t'=t/c`: `mu'=c*mu`, `sigma'=sqrt(c)*sigma`, `H'=H/c`. Auch die Rauschskala muss transformiert werden.
- Diese gaußsche Referenz ist kein vollständiges Modell eines nichtnegativen Wasserspeichers mit Reflexion, Sprüngen oder zustandsabhängigem Rauschen.

### 10.3 Simulation und Abnahme

Eine rein zeitgerasterte Simulation übersieht Durchgänge zwischen zwei positiven Endpunkten. Für konstante Diffusion im obigen Modell ist die bedingte Brownian-Bridge-Durchgangswahrscheinlichkeit innerhalb eines Schritts `Delta` bei positiven Endpunkten `x,y` gleich `exp(-2*x*y/(sigma**2*Delta))` [S15]. Nur unter dieser Modellannahme verwenden.

Abnahme über geschlossene Kontrollwerte, Einheiteninvarianz, deterministischen Grenzfall und Monotonie in Horizont/Anfangsreserve. Ein Vergleich mit Simulation muss Monte-Carlo-Fehler und zeitliche Diskretisierung getrennt behandeln. Die Referenzformel ist primärer Test; eine Monte-Carlo-Stichprobe ist keine universelle Sicherheitsgarantie. Keine exakte Durchgangszeit aus einer bloßen Bridge-Entscheidung erfinden: dafür wäre ein eigener Sampler nötig.

**Vorgeschlagene Datei:** `viability/first_passage_diffusion.py` plus Herleitung und Verifikation. Keine allgemeine SDE-Bibliothek als Voraussetzung. B4 kann unabhängig vom Hydro-Datenzugriff umgesetzt werden.

## 11. Paket B5 — Batteriealterung und verbleibende Nutzungsdauer

### 11.1 Frage und Daten

**Frage:** Wann verbessert ein einfaches nichtlineares Alterungsmodell die Prognose künftiger gemessener Kapazität und des Erreichens einer Kapazitätsgrenze gegenüber linearen Referenzen? Wie stark verändert die Mess-/Versuchsvariation diese Aussage?

NASA beschreibt Lade-, Entlade- und Impedanzversuche unter verschiedenen Bedingungen; die genannte Versuchs-Endgrenze beträgt 30 % Verlust der Nennkapazität, von 2 Ah auf 1.4 Ah. Der Katalogeintrag selbst zeigt keine spezifizierte Lizenz [S2]. Den tatsächlichen Datenrelease, Versuchskontext und Nutzungsnachweis prüfen. Die 1.4-Ah-Grenze ist eine mögliche studienspezifische Zieldefinition, kein universeller Batterie-Sicherheitsstandard.

### 11.2 Zustände und Beobachtungen

Ein möglicher fachlicher Rahmen ist

\[
Y_n=C_0-D_n+R_n+\varepsilon_n,
\quad D_{n+1}\ge D_n,
\]

wobei `D` irreversible Alterung, `R` reversible bzw. versuchsabhängige Einflüsse und `epsilon` Messfehler bezeichnet. Aus einer einzelnen Kapazitätsreihe sind diese Komponenten im Allgemeinen nicht eindeutig identifizierbar. Deshalb nicht alle drei als physisch bewiesene Zustände ausgeben.

Der erste implementierbare Vergleich beschränkt sich auf **phänomenologische Kapazitätsprognosen**:

| Variante | Mittlere Kapazität | Beobachtungsabweichung |
|---|---|---|
| Persistenz | letzter zulässiger Wert | Trainingsfehler als Referenz |
| Linear | `m(n)=C0-a*n`, `a>=0` | unabhängige, auf dem Präfix geschätzte Abweichungen |
| Potenzgesetz | `m(n)=C0-a*n**p`, `a>=0`, `p>0` | gleiche Beobachtungsfamilie wie beim linearen Modell |
| Beobachtungs-Ablation | dieselben beiden Mittelwertmodelle | zusätzlich AR(1)-Residuen `r[n+1]=phi*r[n]+epsilon[n]`, `abs(phi)<1` |

Die 2×2-Ablation trennt den Nutzen veränderter mittlerer Alterung von dem Nutzen korrelierter Beobachtungsabweichungen. Das Potenzgesetz ist ein bewusst einfacher Modellkandidat, keine vorab bestätigte elektrochemische Gesetzmäßigkeit. Parametergrenzen, Extrapolationshorizont und Suchbudget vor der Testauswertung festlegen; Randtreffer sichtbar berichten. Bei `a=0` ist `p` nicht identifiziert; bei `n=0` liefert der Mittelwert unabhängig von `p>0` den Wert `C0`. Negative extrapolierte Kapazitäten nicht als physikalische Vorhersage ausgeben oder still durch Abschneiden verbergen, sondern als Modellbereichsverletzung behandeln.

**Nicht erzwingen:** Gemessene Kapazität darf vorübergehend steigen. Monotonie betrifft den angenommenen mittleren Trend oder einen ausdrücklich latenten Schaden, nicht die unbearbeiteten Messwerte. Eine monotonisierende Vorverarbeitung würde gerade die Beobachtungsfrage verdecken.

### 11.3 Prognoseziel und Zensierung

Zwei Ziele getrennt ausgeben:

1. Kapazität bei festen zukünftigen Entladezyklen, z. B. Horizont 10 und 20 vergleichbare Zyklen, soweit die Daten diese Auflösung tragen.
2. Erstes **gemessenes** Erreichen `Y_n<=C_EOL` unter einem festgelegten Messprotokoll. Für probabilistische Prognosen die Beobachtungskomponente mit simulieren und dieselbe Ereignisregel anwenden.

Die Nullstelle der mittleren Kurve ist nur der prognostizierte **mittlere Modell-Grenzpunkt**. Sie ist nicht identisch mit dem ersten beobachteten Grenzereignis. Beide dürfen diagnostisch berichtet, aber nicht unter demselben Namen vermischt werden.

Endet eine Reihe vor dem Ereignis, ist sie rechtszensiert. `RUL > verbleibender Beobachtungszeitraum` ist dann die verfügbare Information. Für den ersten Pilot Kapazitätsmetriken und feste Horizonte auswerten, an denen der Ereignisstatus tatsächlich bekannt ist; Anzahl und Eigenschaften ausgeschlossener zensierter Fälle mitliefern. Eine vollständige Survival-Auswertung ist eine spätere Teilaufgabe, falls genügend Zellen und Ereignisse vorliegen. Kein scheinbar vollständiger RUL-MAE durch Ersetzen fehlender Ereignisse.

### 11.4 Daten- und Splitregeln

- Entladeversuche von Lade-/Impedanzeinträgen unterscheiden. Zyklusindex nicht blind als Index aller Operationen definieren.
- Vergleichbare Protokollabschnitte anhand Metadaten auswählen; geänderte Entladeschlussspannung, Temperatur oder Belastung als Kontextwechsel dokumentieren.
- Alterungszeit, Kalenderzeit, Zyklusanzahl und durchgesetzte Ladung nicht gleichsetzen.
- Für neue Zellen äußere Leave-one-cell-out-Auswertung; Hyperparameter nur auf anderen Trainingszellen und deren zulässigen Präfixen wählen.
- Personalisierte Aktualisierung mit dem bereits beobachteten Präfix der Testzelle ist zulässig, muss aber als solche deklariert werden. Eine zusätzlich behauptete Zero-shot-Prognose braucht einen separaten Versuch.
- Prognoseursprünge in absoluten Zykluszahlen vorab festlegen, etwa nach 20, 40 und 60 vergleichbaren Entladungen, falls vorhanden. Nicht „bei 30 % der später bekannten Lebensdauer“ wählen.
- Zellweise Ergebnisse und Stichprobengröße berichten. Wenige Labormuster begründen keine Aussage über beliebige Chemien oder reale Fahrzeugflotten.

### 11.5 Abnahme

1. Exakte synthetische lineare und Potenzverläufe; der Fall `p=1` stimmt mit dem linearen Modell überein.
2. Bei unabhängigen Abweichungen darf der AR-Baustein keinen vorprogrammierten Gewinn erhalten; bei kontrolliert korrelierten Abweichungen seine Wirkung messen.
3. Zukunftsänderungen einer Testzelle verändern keine früheren Fits/Prognosen; Zell-IDs überschreiten keine Splitgrenze unbemerkt.
4. Beobachtete Kapazitätsanstiege bleiben im Rohdatensatz erhalten.
5. Bereits in der beobachteten Historie erreichte Grenze, nie innerhalb des Messfensters erreichte Grenze, fehlende Kapazitätswerte und Protokollwechsel werden korrekt unterschieden. Ein späterer Kapazitätsanstieg setzt eine bereits eingetretene Erstpassage nicht zurück.
6. Kapazitätsfehler, Intervallbewertung und Ereigniswahrscheinlichkeit je Zelle ausgeben; der Datenpilot ist auch bei einem Sieg der linearen Referenz abgeschlossen.

**Vorgeschlagene Dateien:** `dynamics/capacity_degradation.py`, `validation/battery_aging_pilot.py`, Datenadapter für den gewählten NASA-Release, `docs/battery_aging_pilot.md` und getrennte Verifikationen.

## 12. Paket B6 — Kooperative Agenten: Information wird handlungsrelevant

### 12.1 Ziel

Die vorhandenen Kanal- und PID-Module an eine kleine vollständige Aufgabe anschließen: Wer beobachtet was, welche Nachricht ist erlaubt, welche Entscheidung wird getroffen und welcher Aufwand entsteht? Zunächst endliche, exakt auswertbare Aufgaben. OpenSpiel bietet später eine Umgebung für standardisierte Spiele [S7]; eine neue schwere Abhängigkeit ist für die erste Stufe nicht nötig.

### 12.2 Drei Kontrollaufgaben

**A. Komplementäre Information (XOR).** Unabhängige faire Bits `A,B`, Ziel `Y=A XOR B`. Agent 1 sieht `A`, Agent 2 sieht `B`; Agent 2 entscheidet. Ohne Nachricht beträgt die optimale Erfolgsquote 1/2. Mit einem korrekt übertragenen Bit von Agent 1 erreicht sie 1. Dabei `I(A;Y)=I(B;Y)=0`, aber `I(A,B;Y)=1 bit`. Die vorhandene bivariate PID auf der exakt konstruierten gemeinsamen Verteilung prüfen; Maß und Optimierungstoleranz benennen.

**B. Redundanz.** `A=B=Y`, fair. Agent 2 ist bereits ohne Nachricht perfekt. Zusätzliche Kommunikation schafft bei dieser Aufgabe keinen Genauigkeitsgewinn. Sie kann bei positiven Kosten den Nettoertrag senken.

**C. Fehlerkanal.** Zur XOR-Aufgabe einen unabhängigen Bitfehler mit Wahrscheinlichkeit `epsilon` auf der Nachricht hinzufügen. Eine unveränderte XOR-Dekodierung erreicht `1-epsilon`. Ein über `epsilon` informierter optimaler Dekoder erreicht `max(epsilon,1-epsilon)`; bei `epsilon=0.5` bleibt nur Zufallsniveau. Diese beiden Strategien trennen, damit systematisch invertierte Nachrichten nicht fälschlich als informationlos gelten.

Aus diesen Aufgaben folgen weder menschliche Bewusstseinsaussagen noch allgemeine Intelligenzwerte. Sie beantworten präzise den Nutzen bestimmter Beobachtungs- und Kommunikationsstrukturen.

### 12.3 Kosten und Eingriffe

Für die kontrollierte Ein-Bit-Aufgabe kann die Belohnung als

\[
J=P(\widehat Y=Y)-\lambda\,E[\text{übertragene Bits}]
\]

definiert werden. Bei bekannter, unverzerrter Nachricht verbessert Senden im XOR-Fall den Nettoertrag genau dann, wenn `lambda<0.5`; bei Gleichheit besteht Indifferenz. In der Redundanzaufgabe gewinnt Senden bei positiven Kosten nicht.

Vorab festlegen, ob das **Schweigen** beobachtbar und selbst ein Signal ist. Im einfachsten Kontrollfall ist die Sendeentscheidung für alle Zustände gleich und vor der Beobachtung festgelegt. Andernfalls könnte ein Agent Informationen kostenlos über „senden oder schweigen“ kodieren und die behauptete Bitkosten-Grenze umgehen.

Interventionen: Kommunikationskanal an/aus, Nachrichten zufällig permutieren, Fehlerwahrscheinlichkeit ändern, einzelne Sensorquelle entfernen. Gleiche Aufgabenverteilung und möglichst gepaarte Zufallsbedingungen verwenden. Das erlaubt kausale Aussagen über die manipulierte Spielumgebung, nicht automatisch über beliebige reale Agentensysteme.

### 12.4 Erweiterung: Erholung nach Fehlinformation

Erst nach Abschluss der statischen Aufgaben eine wiederholte endliche Aufgabe ergänzen: bekannte verborgene Markov-Zustandswechsel, Nachrichtenverzögerung oder begrenzte Verifikationsabfrage. Vergleichen: immer glauben, nie kommunizieren, Bayes-Regel bei bekanntem Modell und budgetierte Verifikation. Metriken: Entscheidungsfehler, Kommunikationsmenge, Verifikationskosten und Zahl der Runden bis zu einem vorab definierten Erholungszustand.

LLM-Agenten sind eine weitere, separate Stufe. Vor deren Einbindung Modellversion, Prompt, Temperatur, Werkzeugrechte, Beobachtungszugang und Kosten protokollieren. Die exakte endliche Aufgabe bleibt als Referenz erhalten; keine Live-LLM-Aufrufe in der regulären CI.

### 12.5 Abnahme

1. Alle Zustände der Kontrollaufgaben vollständig enumerieren; keine Stichprobe als Ersatz für diese kleinen exakten Fälle.
2. XOR: 0.5 ohne Kommunikation, 1 mit fehlerfreiem Bit; Redundanz: 1 auch ohne Bit.
3. Kanalfehler `epsilon in {0,0.1,0.5,1}` korrekt für festen und optimal angepassten Dekoder.
4. Kosten-Grenze einschließlich Gleichheit und Schweigesemantik prüfen.
5. PID-Identitäten, Task-Leistung und Kosten separat berichten; hohe gemeinsame Information allein garantiert keine gute implementierte Strategie.
6. Agentenfunktionen erhalten ausschließlich ihre erlaubten lokalen Beobachtungen. Geheimzustand und Zielwert erst bei Auswertung zugänglich machen.

**Vorgeschlagene Dateien:** `validation/cooperative_agents_pilot.py`, ggf. ein kleines endliches Aufgabenmodul, `docs/cooperative_agents_pilot.md`. Vorhandene `observation`-/PID-Funktionen nutzen, keine zweite Informationsbibliothek entwickeln.

## 13. Weitere mathematische Bausteine nach den ersten Piloten

| Baustein | Konkreter nächster Nutzen | Minimaler nächster Kontrollfall | Wann aufnehmen? |
|---|---|---|---|
| Verteilte Verzögerung | Reaktionszeiten in Ökologie, Verkehr, Lieferketten und Agentennachrichten | Erlang-Kernel gegen äquivalente Zustandskette | Wenn eine konkrete Verzögerungsfrage eine einzelne Relaxationszeit überfordert. |
| Hybride Dynamik | Leerstand, Umschalten, Abschaltung und Wiederanlauf | Zwei kontinuierliche Modi mit expliziter Wechselbedingung und Reset | Wenn eine reale Randregel im Pilot entscheidend wird. |
| Netzwerkflüsse | Gekoppelte Speicher, Bestände und Ressourcenteilung | Drei Knoten mit Flusserhaltung und einer Kapazitätsgrenze | Nach erfolgreichem Einzel-/Zwei-Puffer-Fall. |
| Räumliche Dynamik | Ausbreitung, Stauwellen, ökologische Muster | Diffusion auf einem kleinen Graphen gegen bekannte Eigenmoden | Bei vorhandener räumlicher Zielgröße, nicht nur zusätzlichen Koordinaten. |
| Risiko unter Eingriffen | Ressourcen nach Ereigniswahrscheinlichkeit verteilen | Endliche CTMC mit zwei zulässigen Aktionen und exakter dynamischer Programmierung | Wenn Ereigniswahrscheinlichkeiten selbst überprüft sind. |
| Zustands-/Parameteridentifikation | Verborgene Speicher und Alterungszustände | Zwei Parameterkombinationen mit gleicher Beobachtungsfolge | Schon in den Piloten diagnostisch; komplexe Schätzer erst später. |

### 13.1 Konkrete Verzögerungsbrücke

Für die lineare Kette

\[
\dot z_1=r(u-z_1),\qquad \dot z_i=r(z_{i-1}-z_i),\quad i=2,\ldots,m
\]

ist bei null initialisierten Kettenzuständen der Ausgang `z_m` die Faltung von `u` mit

\[
k_m(s)={r^m s^{m-1}e^{-rs}\over(m-1)!},\qquad s\ge0.
\]

Der Kernel hat Integral 1, Mittelwert `m/r` und Varianz `m/r²`. Unter `r=m/tau` bleibt die mittlere Verzögerung `tau`, während die Varianz `tau²/m` schrumpft. Endliche Ketten sind verteilte Verzögerungen; eine feste diskrete Verzögerung entsteht nur in einem geeigneten Grenzübergang. Für nichtnullige Startwerte kommt ein Anfangsterm hinzu. Der Linear-Chain-Trick und seine verallgemeinerten Verweilzeitdarstellungen sind in [S8] behandelt.

Abnahme: Normierung und Momente, Impuls-/Sprungantwort, Anfangsterm, Übereinstimmung Kette/Faltung. Dies ist eine natürliche spätere Wiederverwendung der Gedächtnisarbeit, kein Bedarf für einen vollständigen DDE-Solver in der ersten Runde.

### 13.2 Netzwerke und hybride Ereignisse

Bei Netzwerkbilanzen `dot x=Bf+u-d` die Orientierung der Inzidenzmatrix `B` und Einheiten deklarieren. Interne Flüsse erhalten die Summe nur bei passenden Randbedingungen. Ein Topologievergleich allein überträgt weder Transportgesetze noch Überlastregeln.

Hybride Modelle benötigen explizite Modi, Wächterbedingungen und Resets. Gleichzeitige Ereignisse, exakte Grenzberührung, Hysterese und mögliche Häufung von Schaltvorgängen müssen semantisch entschieden werden. Deshalb zunächst eine einzelne benötigte Schaltregel testen, keine vage allgemeine „Kippmaschine“ bauen.

## 14. Themenatlas für die zweite Ausbaurunde

Die folgenden Themen sind konkrete Anschlussoptionen. Sie gehören **nicht automatisch zum ersten Implementierungsauftrag**. Jedes beginnt mit einer kleinen Forschungsfrage und einem Daten-/Messbarkeitscheck.

| Gebiet | Erste sinnvolle Frage | Anschluss an erste Runde | Datenanker | Neue Hürde / erlaubter Erstanspruch |
|---|---|---|---|---|
| Ökologie/Biogeochemie | Welche zeitliche Wasserverfügbarkeit erklärt Erholungsverläufe einer benannten gemessenen Ökosystemgröße? | Hydro-Gedächtnis, Beobachtungsmodell, Verzögerung | NEON [S9] | Zuerst überlappende Messprodukte und Qualitätsflags prüfen. Keine universelle Biodiversitäts-Resilienzregel. |
| Energieversorgung/Speicher | Wie oft reicht eine vorgegebene Speicher- und Leistungsreserve unter beobachteter Residuallast nicht aus? | Bestände, Budgets, Erstpassage | SMARD [S10] | Energie und Leistung unterscheiden; Wirkungsgrad und Randregeln angeben. Aggregatdaten ergeben keine Netzstabilitätsstudie. |
| Verkehr | Wann verstärken Reaktionszeiten und Kopplung eine lokale Störung? | Verzögerung, transiente Verstärkung, Flüsse | NGSIM [S11] | Trajektorienfehler und abgeleitete Beschleunigungen prüfen. Räumliche Wellen brauchen ein räumliches Modell. |
| Lieferketten | Wie verändern Lieferverzögerungen und Puffer einen dokumentierten Ausfallschock? | Warteschlangen, Bestände, Netzwerkflüsse | OECD ICIO [S12] | Sektorale Input-Output-Flüsse liefern keine beobachteten tagesgenauen Lager- oder Lieferzeiten. Zunächst strukturell parametrisierte Szenarien. |
| Neurowissenschaft | Welche zusätzliche Stimulusinformation trägt eine zweite Neuronengruppe? | Kanäle, PID, Informations-/Aufgabenunterscheidung | Allen Brain Observatory [S13] | Calcium-/Aktivitätsmessung, Zeitaggregation und Stimulus-Splits beachten. Keine Identität neuronaler Information und Bewusstsein. |
| Astronomie | Wann erklärt ein Beobachtungs-/Periodenmodell Lichtkurven besser als ein Trend? | Messmodell, verborgene Dynamik, ereignisbezogene Auswertung | TESS/MAST [S14] | Qualitätsflags, Beobachtungsfenster und Instrumenteffekte berücksichtigen. Periodizität allein identifiziert keinen physikalischen Mechanismus. |

**Empfohlene Reihenfolge danach:** Energieversorgung oder Ökologie, je nachdem ob zunächst Eingriffe oder Gedächtnis vertieft werden sollen. Verkehr benötigt mehr Raum-/Verzögerungsmodellierung. Lieferketten sind mathematisch attraktiv, aber die Lücke zwischen verfügbaren Aggregatdaten und behaupteter Dynamik muss ausdrücklich bleiben. Neuroscience und Astronomie erweitern vor allem den Beobachtungs- und Informationszweig.

### 14.1 Gemeinsame Auswahlregel für neue Domänen

Eine Domäne wird aufgenommen, wenn alle fünf Fragen eine konkrete Antwort haben:

1. Welche einzelne wissenschaftliche Frage wird beantwortet?
2. Welche vorhandene Struktur wird tatsächlich wiederverwendet?
3. Was ist die stärkste einfache Referenz?
4. Welcher beobachtbare Wert könnte die vorgeschlagene Übertragung widerlegen?
5. Welche fehlenden Variablen oder Daten verhindern derzeit einen stärkeren Anspruch?

Ein weiterer Themenname ohne neue prüfbare Frage vergrößert die Dokumentation, aber nicht die Fähigkeit des Repo.

## 15. Architektur und Schnittstellen: klein anfangen

### 15.1 Vorgeschlagene Verantwortlichkeiten

| Ort | Verantwortlichkeit |
|---|---|
| `dynamics/` | Domänennahes Vorwärtsmodell ohne Datenzugriff oder Trainings-/Testentscheidung. |
| `viability/` | Ereignisse, Erreichungswahrscheinlichkeiten und Geltungsbedingungen. |
| `closure/` | Nachgewiesene Reduktion, Gedächtnisterme und Schließungsdefekte. |
| `validation/` | Datenadapter, Präfix-Fits, Piloten, Splits und Ergebnisberichte. |
| `data/` | Kleine belegte Datenausschnitte, Manifeste und Protokollkonfigurationen. |
| `verification/` | Unabhängig hergeleitete Kontrollfälle und Datenintegrität. |
| `docs/` | Modellherleitung, Brückenkarte, Versuchskonfiguration, Ergebnisse und Grenzen. |

Alle Dateinamen in diesem Plan sind Vorschläge. Claude prüft zuerst vorhandene Namen und Konventionen. Kein bestehendes öffentliches API ohne Migrationsgrund umbenennen.

### 15.2 Minimaler Funktionsentwurf

Die folgenden Signaturen sind Zielskizzen; sie schreiben keine neuen Basisklassen vor:

```python
reservoir_step(storage, inflow_rate, rate, dt)
reservoir_interval_discharge(storage, inflow_rate, rate, dt)
fluid_queue_piecewise(initial_backlog, breakpoints, arrival_rates, service_rates)
queue_hitting_probability(initial_count, threshold, horizon, arrival_rate, service_rate)
diffusion_lower_hitting_probability(initial_reserve, drift, diffusion, horizon)
fit_capacity_trend(train_cycles, train_capacity, model_spec)
predict_capacity_distribution(fit, origin_state, future_cycle_indices, rng)
evaluate_finite_communication_task(task_distribution, channel, policy, cost_spec)
```

Jede öffentliche Funktion validiert endliche Eingaben, Form, Einheitenkonventionen und physikalisch/mathematisch zulässige Bereiche. Kontrollparameter wie `rng` werden explizit übergeben. Datenabruf und Plot-Erzeugung finden nicht beim Import statt.

**Keine unehrliche Vereinheitlichung:** Ein exakt enumeriertes Spiel, ein numerisch berechnetes Matrixexponential und eine gefittete Zeitreihe dürfen gemeinsame Berichtsfelder nutzen. Sie müssen nicht dieselbe Simulationsmethode oder denselben Wahrheitsstatus vortäuschen.

### 15.3 Abhängigkeiten und Laufzeit

- NumPy und SciPy genügen für die erste mathematische Runde.
- Matplotlib nur für Reproduktionsberichte, sofern bereits als Verifikationsabhängigkeit vorhanden oder begründet ergänzt.
- Datenpakete, OpenSpiel und spätere Domänentools als optionale Abhängigkeiten behandeln; kein Download beim normalen Paketimport.
- Ein Referenzlauf soll auf einer normalen CPU mit kleinen fixierten Datenfenstern nachvollziehbar sein. Größere Panel-/Monte-Carlo-Läufe getrennt vom schnellen CI-Pfad halten.
- Die vorhandene Runner-Zeitgrenze von 120 Sekunden pro Skript berücksichtigen. Keine großen Optimierungsschleifen in einen scheinbar kleinen Regressionstest verstecken.
- Numerische Regressionen mit der tatsächlich verwendeten NumPy-/SciPy-Version dokumentieren. Die NumPy-2.4-Erfahrung bleibt ein konkreter Grund für Kompatibilitätsprüfung, nicht für ein pauschales Festfrieren aller Versionen.

## 16. Arbeitspakete, Reihenfolge und Abschlussregeln

| Paket | Inhalt | Abhängigkeit | Abschlussbeleg | Umfang qualitativ |
|---|---|---|---|---|
| B0 | Zeiteinheitenfehler und numerische Klassifikation | aktueller HEAD | Gegenbeispiel vor/nach Fix, Regression | klein bis mittel |
| B1 | Protokoll, Provenienz und Testzuordnung | bestehende Infrastruktur | keine Zukunftslecks, korrekt ausgewählte Tests | mittel |
| B2a | Fluidrückstau und Bestandsbrücke | B0/B1 für finale Berichte | Laststoß-Orakel, exakte Brückenkarte | klein |
| B2b | CTMC-Erstpassage und Queue-Pilot | B1, B2a | Generator/Poisson-Orakel, Simulationsvergleich | mittel |
| B3a | Reservoirs und Gedächtnisbrücke | B0/B1 | Bilanz/Faltung/Grenzfälle | mittel |
| B3b | CAMELS-Datenpilot | B3a, Datenzugriff | vollständiger retrospektiver Panelbericht | größer |
| B4 | Diffusions-Erstpassage | B1 | geschlossene Wahrscheinlichkeiten, Einheitenprüfung | mittel |
| B5a | Kapazitätsmodelle und Beobachtungs-Ablation | B1 | synthetische Kontrollfälle | mittel |
| B5b | NASA-Datenpilot | B5a, Provenienz | Zell-/Zeittrennung, Zensierungsbericht | größer |
| B6a | Endliche Agentenaufgaben | B1, vorhandene Informationsmodule | vollständige Enumeration und Kostenfälle | mittel |
| B6b | Wiederholte Aufgabe / OpenSpiel | B6a | eigene klar definierte Folgefrage | ausdrücklich optional |
| B7 | Gemeinsame Auswertung und Fähigkeitsübersicht | verfügbare abgeschlossene Pakete | verlinkte Ergebnisse, offene Teilaufgaben sichtbar | mittel |

Die Angaben sind eine relative Arbeits-/Unsicherheitseinschätzung, keine zugesagte Anzahl von Tagen oder Modellaufrufen. Datenzugriff, vorhandene Funktionen und reale Fitprobleme entscheiden über den tatsächlichen Aufwand.

**Erster sinnvoller Übergabestand:** B0, B1, B2a/b und B3a/b. Damit stehen eine exakte Modellbrücke, stochastisches Ereignisrisiko und ein neuer externer Datenpilot bereit. Anschließend B4, B5 und B6a; B7 konsolidiert alle verfügbaren Ergebnisse.

Pro Paket getrennte Änderungen und ein fokussierter Commit. Kleine mathematische Module erst nach Herleitung; Datenpakete erst nach Protokollfixierung. Bei ungeklärtem Datenzugriff analytische/synthetische Teile fertigstellen und den Datenblock mit konkretem Grund offen führen. Ein synthetischer Ersatz schließt keinen verlangten realen Datenpilot ab.

### 16.1 Gemeinsame Definition of Done

Ein Paket ist abgeschlossen, wenn:

1. Modell und Geltungsbereich vorliegen;
2. mindestens ein unabhängig berechenbarer Kontrollfall und ein relevanter Gegenfall geprüft sind;
3. Datenherkunft und Split dokumentiert sind, sofern reale Daten verwendet werden;
4. alle geplanten Baselines und Ablationen ausgewertet wurden;
5. alle Ergebnisse einschließlich Nichtgewinnen im Bericht stehen;
6. behauptete Zahlen durch einen eingecheckten Befehl reproduzierbar sind;
7. betroffene und erforderliche vollständige Repo-Prüfungen erfolgreich sind oder ein bestehender, unabhängig belegter Blocker ausdrücklich ausgewiesen ist;
8. Restpunkte benannt bleiben und der Paketstatus dem tatsächlichen Umfang entspricht.

Ein erzwungener Performancegewinn ist **kein** Abnahmekriterium. Tests prüfen Implementationskorrektheit; wissenschaftliche Versuche prüfen Hypothesen.

### 16.2 Gemeinsamer Ergebnisvergleich in B7

Die Abschlussübersicht fragt für jede Domäne:

- Welche Information verlor die einfachere Darstellung?
- Veränderte dieser Verlust das betrachtete Ereignis oder nur einen nebensächlichen Messfehler?
- Reichte ein zeitabhängiges lineares Modell, eine zweite Zeitskala oder ein anderes Beobachtungsmodell?
- Wo war echte Nichtlinearität nötig, wo blieb ihr Nutzen unbelegt?
- Welche Beziehung ließ sich exakt herleiten, welche nur auf den geprüften Daten beobachten?

Keine domänenübergreifende Mittelwert-Rangliste aus inkompatiblen Maßeinheiten bilden. Transferierbar sind zunächst Verfahren und Strukturbehauptungen; Parameterwerte, Gütemaße und Kausalinterpretationen benötigen eigene Begründungen.

## 17. Direkt verwendbarer Auftrag für Claude Code

Der folgende Block kann zusammen mit diesem gesamten Dokument übergeben werden:

```text
Arbeite am Repository GenesisAeon/scoped-correspondence-formalism.
Die beigefügte SCF_DOMAIN_EXPANSION_IMPLEMENTATION_PLAN.md ist die
fachliche Spezifikation für eine gestufte Erweiterung um Warteschlangen,
Hydrologie, stochastische Erstpassage, Batteriealterung und endliche
kooperative Agentenaufgaben.

1. Lies vorhandene Repo-Anweisungen und prüfe den aktuellen HEAD.
   Referenz des Plans ist bd87a445dec1611e5bf919f95e9e7019e1c32ea4.
   Wenn Funktionen oder Fixes inzwischen existieren, prüfe und verwende sie.
   Dupliziere keine vorhandenen Implementierungen.

2. Lege eine knappe DOMAIN_EXPANSION_ROADMAP.md mit Teilstatus an.
   Bearbeite zuerst B0 und B1, dann B2a/b und B3a/b.
   Führe danach B4, B5a/b und B6a aus; B7 konsolidiert die Ergebnisse.
   B6b und der Themenatlas sind Folgeoptionen und sollen nicht ohne
   einen konkreten weiteren Auftrag als zusätzliche Großprojekte entstehen.

3. Reproduziere insbesondere das Zeiteinheiten-Gegenbeispiel aus B0.
   Schreibe die Herleitung und die Regression vor dem Fix fest.
   Verwende eine numerisch stabile, skalenbewusste Fallbehandlung;
   eine willkürlich kleinere absolute Diskriminantenschwelle genügt nicht.

4. Vor jedem mathematischen Modul: kurze Herleitung, Einheiten,
   Randbedingungen, Ereignisdefinition und unabhängig berechenbare
   Kontrollfälle. Verwende bestehende Correspondence-/Closure-/
   Viability-/Validation-APIs, soweit sie fachlich passen.

5. Vor jedem Datenpilot: Quelle, Release, tatsächliche Nutzungsangaben,
   beobachtete gegenüber abgeleiteten Daten, Auswahlregel und zeitliche/
   objektbezogene Splits dokumentieren. Keine erfundenen Daten, IDs,
   Retrieval-Zeiten oder Prüfsummen. Keine synthetischen Daten als real
   ausgeben. Historisch unbekannte Verfügbarkeit ehrlich markieren.

6. Modelle nur mit zulässigen Präfixen fitten. Verhindere Lecks durch
   Skalierung, Schwellenwahl, Merkmale, Intervallkalibrierung und
   zukünftige Eingänge. Conditional hindcast und echte Prognose trennen.
   Alle Baselines erhalten dieselbe zulässige Information.

7. Berichte auch negative und neutrale Ergebnisse. Ein Paket ist nicht
   davon abhängig, dass Nichtlinearität, Gedächtnis, Kommunikation oder
   ein komplexeres Modell einen vorgegebenen Gewinn erzielt.
   Die Abnahmekriterien prüfen Korrektheit und Vollständigkeit.

8. Halte Standardtests offline und klein. Reale Datenprüfungen müssen
   im Datenjob landen. Nutze mindestens die vorhandenen Befehle:
     python scripts/run_verification_suite.py --category math
     python scripts/run_verification_suite.py --category data
     python scripts/run_verification_suite.py --category links
   Beachte zusätzlich vorhandene projektspezifische Prüfvorgaben.
   Testausfälle nicht durch gelockerte Toleranzen oder entfernte
   Gegenbeispiele verdecken. Erkläre notwendige Toleranzen fachlich.

9. Liefere pro Paket Code, Verifikation, ein worked example mit
   Brückenkarte/Scope und einen maschinenlesbaren Ergebnisbericht.
   Aktualisiere die Fähigkeitsübersicht erst nach tatsächlicher Umsetzung.
   Dokumente mit bestehendem Review-Status nicht still zum akzeptierten
   Kern befördern.

10. Arbeite in überprüfbaren Commits. Nutze für Branch/Push/PR die
    bereits geltenden Nutzer- und Repo-Vorgaben; dieses Dokument allein
    erteilt keine zusätzliche Veröffentlichungsanweisung.
    Halte externe Datenblocker konkret fest und arbeite unabhängig
    mögliche Pakete weiter ab. Ein blockierter Datenpilot bleibt offen.

Abschlussbericht: ausgeführte Pakete, konkrete Resultate pro Baseline,
Commit-Stand, tatsächliche Testläufe, reproduzierbare Befehle sowie
verbliebene methodische und empirische Grenzen. Keine universellen
Sicherheits-, Kausalitäts- oder Intelligenzbehauptungen aus Einzelpiloten.
```

## 18. Quellen und überprüfbare Ausgangspunkte

Alle Webquellen wurden am 24. September 2026 für diesen Plan aufgerufen. Die verlinkten Datenangebote sind **Kandidaten und Quellenbeschreibungen**; ihre Rohdaten wurden für dieses Dokument nicht heruntergeladen, modelliert oder auf Prognosegüte untersucht. Release, Variablenverfügbarkeit und Weiterverteilbarkeit sind Teil der Implementierungsarbeit.

### Repository

- [Referenzcommit bd87a44](https://github.com/GenesisAeon/scoped-correspondence-formalism/commit/bd87a445dec1611e5bf919f95e9e7019e1c32ea4)
- [Correspondence-Vertrag am Referenzcommit](https://github.com/GenesisAeon/scoped-correspondence-formalism/blob/bd87a445dec1611e5bf919f95e9e7019e1c32ea4/src/scoped_correspondence/correspondence/contract.py)
- [Strukturelle Beziehungen und Brückenkarten](https://github.com/GenesisAeon/scoped-correspondence-formalism/blob/bd87a445dec1611e5bf919f95e9e7019e1c32ea4/docs/structural_relations.md)
- [Lineare Gedächtnisreduktion](https://github.com/GenesisAeon/scoped-correspondence-formalism/blob/bd87a445dec1611e5bf919f95e9e7019e1c32ea4/src/scoped_correspondence/closure/linear_memory_projection.py)
- [Transiente Verstärkung und B0-Zielstelle](https://github.com/GenesisAeon/scoped-correspondence-formalism/blob/bd87a445dec1611e5bf919f95e9e7019e1c32ea4/src/scoped_correspondence/viability/transient_amplification.py)
- [Vorhandene Ausbau-Roadmap](https://github.com/GenesisAeon/scoped-correspondence-formalism/blob/bd87a445dec1611e5bf919f95e9e7019e1c32ea4/CAPABILITY_EXPANSION_ROADMAP.md)

### Mathematische Grundlagen und erste Datenpiloten

**[S1] CAMELS-DE.** Loritz et al. (2024), *CAMELS-DE: hydro-meteorological time series and attributes for 1582 catchments in Germany*, Earth System Science Data 16, 5625–5642. [Datenpapier](https://essd.copernicus.org/articles/16/5625/2024/), [dort referenzierter Release 1.0](https://doi.org/10.5281/zenodo.13837553). Belegt Datenumfang, tägliche Auflösung und Trennung beobachteter/simulierter Größen. Die hier vorgeschlagenen sechs Gebiete, Zeitteilungen und Reservoirversuche sind eigene Planungsvorschläge.

**[S2] NASA PCoE.** [Li-ion Battery Aging Datasets](https://data.nasa.gov/dataset/li-ion-battery-aging-datasets); ergänzender [offizieller Repository-Einstieg](https://www.nasa.gov/intelligent-systems-division/discovery-and-systems-health/pcoe/pcoe-data-set-repository/). Belegt Versuchstypen, Kapazitätsfelder und die genannte Versuchs-Endgrenze. Keine aus dem bloßen NASA-Hosting abgeleitete Lizenzbehauptung.

**[S3] MIT OpenCourseWare.** *Introduction to Manufacturing Systems*, M/M/1 Queue. [Offizielles Lehrmaterial](https://ocw.mit.edu/courses/2-854-introduction-to-manufacturing-systems-fall-2016/resources/mit2_854f16_mm1queue/). Grundlage der stationären Queue-Referenz; der absorbierende Generator und die Zahlen in B2 sind die konkrete Konstruktion dieses Plans.

**[S4] Google.** [ClusterData2019-Schema](https://github.com/google/cluster-data/blob/master/ClusterData2019.md), [offizielles Datenrepository](https://github.com/google/cluster-data). Quelle möglicher Last-/Scheduler-Traces; kein Beleg für die Gleichheit mit einem M/M/1-Modell.

**[S5] Chorin, Hald & Kupferman (2000).** *Optimal prediction and the Mori–Zwanzig representation of irreversible processes*, PNAS 97, 2968–2973. DOI 10.1073/pnas.97.7.2968. [Autorenfassung](https://math.huji.ac.il/~razk/Publications/PDF/CHK00.pdf). Grundlage der Perspektive auf Gedächtnis durch Projektion; die lineare Blockelimination ist hier unmittelbar nachrechenbar.

**[S6] Karl Sigman, Columbia University.** *Notes on Brownian Motion*. [Offizielles Vorlesungsskript, insbesondere Erstpassage mit Drift](https://www.columbia.edu/~ks20/FE-Notes/4700-07-Notes-BM.pdf). Grundlage des elementaren Diffusions-Kontrollfalls. Numerisch stabile Implementierung und Grenztests sind eigene Entwicklungsanforderungen.

**[S7] Lanctot et al. (2019).** *OpenSpiel: A Framework for Reinforcement Learning in Games*. [Originalarbeit](https://arxiv.org/abs/1908.09453), [offizielles Repository](https://github.com/google-deepmind/open_spiel). Anschluss für spätere Spielumgebungen; XOR-/Redundanz-/Kostenkontrollen sind die hier definierten eigenen Aufgaben.

**[S8] Hurtado & Kirosingh (2019).** *Generalizations of the Linear Chain Trick: Incorporating more flexible dwell time distributions into mean field ODE models*. [Autoren-Preprint](https://arxiv.org/abs/1808.07571). Grundlage der Erlang-/Phasentyp-Verweilzeitdarstellung. Es wird keine neue universelle Verzögerungstheorie behauptet.

**[S15] Yibi Huang, University of Chicago.** *STAT253/317, Lecture 25: The Maximum of Brownian Motion with Drift* (2021). [Offizielles Vorlesungsskript](https://galton.uchicago.edu/~yibi/teaching/stat317/2021/Lectures/Lecture25.pdf). Endlicher Horizont und bedingte Brownian-Bridge-Grenzwahrscheinlichkeit; hier durch Vorzeichenwechsel auf eine untere Grenze übertragen.

### Quellen für die zweite Ausbaurunde

**[S9] NEON.** [Getting Started with NEON Data](https://www.neonscience.org/resources/getting-started-neon-data-resources). Offizielle Übersicht über standardisierte meteorologische, Boden-, biologische und biogeochemische Daten samt Dokumentation. Eine konkrete Kombination passender Produkte ist noch auszuwählen.

**[S10] Bundesnetzagentur / SMARD.** [Download market data](https://www.smard.de/en/downloadcenter/download-market-data). Öffentliche Marktdaten und angegebene CC-BY-4.0-Nutzung. Aggregierte Erzeugung/Last ersetzt keine Netztopologie.

**[S11] FHWA.** [Next Generation Simulation – NGSIM](https://ops.fhwa.dot.gov/trafficanalysistools/ngsim.htm). Offizieller Zugang zu Verkehrsdaten, Algorithmen und Berichten.

**[S12] OECD.** [Inter-Country Input-Output Tables](https://www.oecd.org/en/data/datasets/inter-country-input-output-tables.html). Quelle sektoraler internationaler Input-Output-Beziehungen; keine automatisch beobachteten Lieferkettenereignisse.

**[S13] Allen Institute.** [Allen Brain Observatory / AllenSDK](https://alleninstitute.github.io/AllenSDK/brain_observatory.html). Offizielle Daten-/Werkzeugdokumentation zur Untersuchung neuronaler Reaktionen.

**[S14] STScI / MAST.** [TESS-Missionsdaten](https://archive.stsci.edu/missions-and-data/tess). Offizieller Archivzugang für einen späteren Lichtkurvenpilot.

## 19. Erwarteter Fähigkeitsgewinn

Nach abgeschlossener erster Runde könnte SCF an mehreren klar abgegrenzten Gegenständen beantworten:

- wann zeitliche Mittelung eine Grenzereignisprognose verändert;
- wann eine zusätzliche Zeitskala überprüfbar nützlich ist;
- wie Bestandsdynamik, Messprozess und Ereignisdefinition zusammenwirken;
- wie eine günstige mittlere Entwicklung dennoch mit einem nicht vernachlässigbaren Durchgangsrisiko vereinbar ist;
- wann Alterung und Beobachtungsvariation getrennt modelliert werden müssen;
- wann Kommunikation durch ergänzende Information Aufgaben verbessert und wann sie nur Kosten oder Fehler hinzufügt.

Die wissenschaftliche Breite entsteht durch diese überprüften Beziehungen und ihre Gegenbeispiele. Jede neue Domäne erweitert zugleich die Liste der Bedingungen, unter denen eine Übertragung gelingt oder scheitert.
