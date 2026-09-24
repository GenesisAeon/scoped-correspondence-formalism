# SCF: unabhängige Nachprüfung der Domänenerweiterung

Stand: 24. September 2026  
Geprüfter Commit: `fcc9a438394a6a7596cc72c6807fdd2aa3f8f971`  
Vergleichsbasis: `bd87a445dec1611e5bf919f95e9e7019e1c32ea4`

## Urteil

Die Erweiterung bringt echte neue Fähigkeiten: exakten Fluidrückstau, endliche CTMC-Erstpassage, lineare Reservoirs, eine Diffusionsreferenz, Kapazitätsmodelle und endliche Kommunikationsaufgaben. Die zentralen Beispielzahlen stimmen. Der frühere Zeiteinheitenfehler ist am ursprünglichen Gegenbeispiel behoben.

**„B0–B7 vollständig abgeschlossen“ ist dennoch nicht der belegte Stand.** Die vorhandenen Tests übersehen mehrere reproduzierbare Fehler; Teile von B1 und der geplanten Batterieauswertung fehlen. Der CAMELS-Datenpilot ist offen, sein bisher angeführter Download-Blocker lässt sich aber technisch auflösen.

Empfehlung: zuerst die unten beschriebenen Korrekturen und die Statusbereinigung; danach die beiden Datenpiloten gemäß ihrem tatsächlichen Protokoll vervollständigen. Eine weitere Domänenrunde sollte auf diesem geprüften Stand aufbauen.

## 1. Was unabhängig bestätigt wurde

- GitHub enthält die sieben angegebenen neuen Commits; HEAD ist `fcc9a43`.
- Der [CI-Lauf 36032506204](https://github.com/GenesisAeon/scoped-correspondence-formalism/actions/runs/36032506204) war erfolgreich, einschließlich Mathe-, Daten- und Linkjob.
- Alle 41 geänderten/neuen Dateien wurden am festgehaltenen Commit abgerufen und gegen ihren Git-Blob-SHA geprüft.
- Die neun betroffenen mathematischen/synthetischen Prüfsuiten wurden lokal unter **NumPy 2.4.6** ausgeführt: **59/59 Einzelchecks bestanden**.
- Die gesamte 82-Skripte-Suite wurde in diesem Review nicht nochmals lokal ausgeführt. Ihre grüne CI und die gezielten lokalen Läufe sind unterschiedliche Belege.
- NASA-Rohdaten wurden hier nicht erneut heruntergeladen. Die vier realen Zellresultate bleiben in diesem Review als dokumentierter Entwicklerlauf eingeordnet, nicht als von mir unabhängig reproduzierte Datenanalyse.

| Kontrollfall | Unabhängiges Ergebnis |
|---|---:|
| Queue: `n0=0, K=5, H=10, lambda=0.5, mu=1` | `P(tau_K<=H)=0.055981825032509924` |
| Dieselben Raten im deterministischen Fluidmodell | maximaler Rückstau `0` |
| Diffusion: `x0=1, mu=1, sigma=1, H=1` | `0.09041777356648555` |
| Ursprünglicher B0-Fall, Zeitskalierung `c=1e-6,1,1e6` | immer `transient_violation`; Betrag des Peaks etwa `0.9844639845000663` |
| B0-Peakzeit nach Rückskalierung | etwa `0.1560796660108231` |

Die Queue-Zahl ist eine Wahrscheinlichkeit des **Erreichens von K** im angegebenen M/M/1-Modell und Horizont. Sie ist weder eine universelle Überlastquote noch allein durch `rho=0.5` bestimmt. Das Fluidmodell berechnet eine deterministische Trajektorie; „0 % Risiko“ sollte als Kurzform dieses Modellereignisses kenntlich bleiben. Der Fluidrückstau ist insbesondere nicht generell gleich `E[N_t]` der stochastischen Warteschlange.

## 2. R1 — AR(1)-Prognose verwendet die falsche Rauschstreuung

**Priorität: hoch.** Datei: `src/scoped_correspondence/dynamics/capacity_degradation.py`, Funktionen `fit_capacity_trend` und `predict_capacity_distribution`.

Der Fit speichert `std(residuals)` als `residual_std`. Die Simulation verwendet genau diese Größe als Standardabweichung der neuen Innovationen in

\[
r_{n+1}=\phi r_n+\epsilon_n.
\]

Das sind bei korrelierten Residuen unterschiedliche Größen. Für einen stationären AR(1)-Prozess gilt

\[
\operatorname{Var}(r)=\frac{\sigma_\epsilon^2}{1-\phi^2}.
\]

Wer die gesamte Residuenstreuung nochmals als Innovationsstreuung verwendet, vergrößert die langfristige Varianz zusätzlich um `1/(1-phi²)`. Das verfälscht prädiktive Intervalle und Erstpassagewahrscheinlichkeiten.

**Reproduktion:** 12 000 synthetische Punkte, wahres `phi=0.8`, Innovations-SD `0.01`, `np.random.default_rng(20260924)`, `r[0]=0`; Innovationen ab Index 1 ziehen, Kapazität `2-0.00001*n+r[n]`. Linearer Fit mit `fit_ar1=True`. Der tatsächliche Code liefert:

| Größe | Wert |
|---|---:|
| geschätztes `phi` | `0.7965957525382641` |
| tatsächliche/geschätzte Innovations-SD aus `r[n+1]-phi*r[n]` | `0.010013708750366442` |
| vom Generator stattdessen verwendete SD | `0.016563884532507258` |
| Verhältnis der beiden Varianzen | `2.736115820333416` |

Die bestehende Prüfung `check_observation_ablation` prüft lediglich, ob `phi` ungefähr wiedergefunden wird. Sie prüft weder die prädiktive Varianz noch den Nutzen der zwei Beobachtungsmodelle auf zurückgehaltenen Zielen.

**Korrektur:** `innovation_std` getrennt schätzen und speichern, etwa aus den AR-Innovationsresiduen mit dokumentierter Schätzkonvention. IID-Residuenstreuung und AR-Innovationsstreuung nicht austauschbar behandeln. Innovationsmittel, Trendunsicherheit und Unsicherheit von `phi` können zunächst als separate verbleibende Modellgrenzen dokumentiert werden.

**Abnahme:** Bei festem Anfangsresiduum lautet die bedingte h-Schritt-Varianz

\[
\sigma_\epsilon^2\sum_{j=0}^{h-1}\phi^{2j}.
\]

Diese analytische Referenz für `h=1,2,10` prüfen; `phi=0` reduziert auf unabhängige Abweichungen. Anschließend die echte 2×2-Auswertung Mittelwertmodell × Beobachtungsmodell durchführen.

## 3. R2 — AR-Prognose ignoriert die tatsächlichen Zyklusabstände

**Priorität: hoch.** Dieselbe Datei, `predict_capacity_distribution`.

Der Code aktualisiert das Residuum einmal pro ausgegebenem Arrayelement. `future_cycle_indices` bestimmt nur den Mittelwert. Damit wird eine Vorhersage für Zyklus 10 bei der Anfrage `[10]` als ein Schritt behandelt, bei `[1,...,10]` dagegen als zehn Schritte.

**Exaktes Gegenbeispiel ohne Zufallsfehler:** konstanter Mittelwert 2, `phi=0.8`, letztes Residuum 1 bei Zyklus 0, Innovationsstreuung 0.

| Anfrage | Vorhersage für Zyklus 10 |
|---|---:|
| nur `[10]` | `2.8` |
| `[1,2,...,10]` | `2.1073741824` |
| mathematisch korrekt | `2+0.8**10 = 2.1073741824` |

**Korrektur:** Prognoseursprung explizit führen oder eindeutig aus dem Fit ableiten. Bei einem Abstand `d` die mittlere Fortsetzung `phi**d*r` und Innovationsvarianz `sigma_epsilon²*sum(phi**(2*j), j=0,...,d-1)` verwenden; alternativ alle Zwischenzyklen intern simulieren. Gültige, streng steigende ganzzahlige Zyklen prüfen. Ein kontinuierlicher oder unregelmäßiger Zeitbegriff benötigt ein eigenes Modell.

**Abnahme:** Die marginale Verteilung eines Zielzyklus bleibt gleich, wenn andere Ausgabezeitpunkte hinzugefügt oder weggelassen werden. Bei deterministischem Residuum muss die Gleichheit unmittelbar numerisch bestehen. Gleiche Seeds allein garantieren bei unterschiedlich implementierten Zufallsziehungen keine pfadweise Identität; das Testziel ist zunächst die gleiche Verteilung.

## 4. R3 — Reservoir-Faltung übersieht schnelle Kernel vollständig

**Priorität: hoch.** Datei: `src/scoped_correspondence/dynamics/linear_reservoirs.py`, Funktion `convolution_discharge`.

Für einen Speicher mit `S0=0`, `alpha=1`, konstantem Zufluss `u=1`, Rate `k=100000` und `t=1` gilt exakt:

\[
q(1)=\int_0^1 k e^{-k(1-s)}\,ds=1-e^{-100000}\approx1.
\]

Der aktuelle Funktionsaufruf

```python
convolution_discharge(1, [0], [1], [100000], lambda s: 1)
```

liefert **`2.0614532085245143e-45`**. Die unabhängige geschlossene Schrittrekursion plus `q=kS` liefert 1.

`quad` bekommt das gesamte Intervall ohne Kenntnis der schmalen Zeitskala und kann alle relevanten Beiträge nahe dem rechten Rand übersehen. `limit=200` erzwingt keine Auflösung einer Struktur, die bei der anfänglichen Auswertung praktisch unsichtbar bleibt. Außerdem wird die zurückgegebene Fehlerschätzung verworfen.

**Korrektur:** Kernel-Zeitskalen in die Quadratur einbauen. Für `k>0` kann komponentenweise `v=k(t-s)` transformiert werden; auch das transformierte Intervall muss sinnvoll aufgeteilt werden. Ein Integral von `exp(-v)` blind über `[0,100000]` an denselben adaptiven Integrator zu geben, würde das Problem lediglich verschieben. Bei stückweise konstantem Eingang exakte Intervallbeiträge verwenden. Bei abgeschnittenem Kernschwanz eine Schranke aus einem tatsächlich bekannten Eingangsmaximum ableiten oder den Fehler als nicht zertifiziert markieren. Sprungstellen des Eingangs explizit übergeben.

**Abnahme:** Konstantzufluss über kleine bis große `kt`, mindestens einschließlich `100000`; mehrere Reservoirraten; Anfangsterm; stückweise Eingänge. Eine exakte Faltungsidentität macht ihre numerische Auswertung nicht automatisch exakt.

### R3b — Auslöschung beim mittleren Abfluss

`reservoir_interval_discharge(1,0,1,1e-17)` liefert 0, obwohl

\[
\bar q=\frac{1-e^{-\Delta}}{\Delta}\approx1.
\]

Der stabile Zustandsupdate reicht nicht, wenn anschließend zwei nahezu gleiche Speicherwerte subtrahiert werden. Dieses Extrembeispiel belegt die fehlende numerische Grenzbehandlung; es ist kein nachgewiesener Fehler der üblichen Tagesfälle.

Eine stabile direkte Form ist mit `z=k*Delta` und `E(z)=(1-exp(-z))/z`:

\[
\bar q=kS_0 E(z)+\alpha u\,[1-E(z)].
\]

Für kleine `z` `expm1` und Reihenentwicklungen für `E` bzw. `1-E` verwenden; `k=0` explizit. Parallelreservoir-Abfluss anschließend aus den stabilen Einzelbeiträgen summieren.

## 5. R4 — Zwei Grenzfälle geben das falsche Ereignisergebnis zurück

### R4a: Konstanter rauschfreier Puffer soll angeblich sicher irgendwann null erreichen

Datei: `viability/first_passage_diffusion.py`, `diffusion_ever_hitting_probability`.

```python
diffusion_lower_hitting_probability(1, 0, 0, 100)  # 0.0, korrekt
diffusion_ever_hitting_probability(1, 0, 0)        # 1.0, falsch
```

Hier ist `X_t=1` für alle Zeiten. Die richtige jemalige Treffwahrscheinlichkeit ist 0. Der Code behandelt `mu<=0` vor dem deterministischen Spezialfall `sigma=0` und übernimmt dadurch eine Aussage, die bei `mu=0` echte Diffusion voraussetzt.

**Korrektur:** nach der Prüfung des Anfangszustands zuerst den rauschfreien Fall entscheiden: für `x0>0` ist die jemalige Treffwahrscheinlichkeit bei `mu<0` gleich 1, bei `mu>=0` gleich 0. Erst anschließend die stochastische Fallunterscheidung verwenden.

### R4b: Bereits unterschrittene Batteriegrenze wird als nicht erreicht gemeldet

Datei: `dynamics/capacity_degradation.py`, `first_mean_eol_crossing`.

Für `C0=1`, `a=0.1`, Schwelle `1.4`, Horizont `10` liefern sowohl das lineare Modell als auch das Potenzmodell mit `p=2` `None`. Nach der im Projekt verwendeten Definition des ersten Erreichens `C<=C_EOL` ist das Ereignis bereits bei 0 eingetreten.

**Korrektur:** Anfangswert zuerst gegen die geschlossene Grenzmenge prüfen. Die erste Gleichheitswurzel von oben ist nicht für alle Anfangswerte dieselbe Frage wie die Erstpassage in die Grenzmenge. Docstring und Statusfelder daran ausrichten.

## 6. R5 — Ungültige Werte werden teilweise zu plausiblen Risikoergebnissen

**Priorität: hoch für die öffentliche API.** Betroffen sind mehrere neue Module.

| Eingabe | Tatsächliche Ausgabe | Erforderliches Verhalten |
|---|---|---|
| `diffusion_lower_hitting_probability(nan,1,1,1)` | `1.0` | ungültige Eingabe zurückweisen |
| `fluid_queue_piecewise(0,[0,1],[nan],[1]).peak()` | `(0.0,0.0)` | ungültige Rate zurückweisen |
| `run_queueing_pilot(0,0.4,1,0,1)` | stochastische Treffwahrscheinlichkeit `1.0` | Zählzustands-/Schwellensemantik validieren |

Im ersten Fall verwandelt `min(1.0, nan)` die nicht berechenbare Wahrscheinlichkeit in 1. Im zweiten Fall verdeckt `max(0.0, nan)` die ungültige Rechnung. Vergleichsprüfungen wie `x<0` fangen NaN nicht ab.

Im dritten Fall rundet der Pilot die Schwelle `0.4` auf 0. Ohne Ankünfte aus Zustand 0 kann `N>=0.4`, also `N>=1`, überhaupt nicht eintreten. Das gerundete Modell erklärt die Grenze hingegen für bereits erreicht. Auch Anfangszahlen werden still gerundet.

**Korrektur:** Alle numerischen Eingaben vor Berechnung und vor frühen Rückgaben auf Endlichkeit und Form prüfen. Nichtnegative Raten, Zeiten und Bestände entsprechend dem deklarierten Modell verlangen. Für CTMC-Zählzustände Ganzzahlen fordern; falls reelle Schwellen erlaubt sein sollen, ihre Übersetzung durch `ceil` ausdrücklich festlegen und berichten. Kein stilles Runden auf die nächste ganze Zahl.

Große Ergebnisabweichungen außerhalb `[0,1]` nicht pauschal abschneiden. Rundungskorrekturen dürfen nur kleine begründete Gleitkommafehler korrigieren. NaN in fehlenden Realwerten gehört in einen expliziten Missing-Data-Pfad.

## 7. R6 — B1 und die Batterieauswertung sind nur teilweise umgesetzt

### B1

Die Roadmap erklärt ihre eigene Erstellung zum Kernabschluss von B1. Im ursprünglichen Auftrag gehörten jedoch auch ein konkretes Versuchsprotokoll, Ereignis-/Berichtskonventionen, Informationsverfügbarkeit, Provenienz und verlässliche Testgruppenzuordnung dazu.

Im Diff fehlen insbesondere:

- `docs/domain_expansion_protocol.md` oder ein gleichwertig ausgearbeitetes Protokoll;
- Erweiterungen des Datenmanifests bzw. ein separates Manifest für extern gehaltene Dateien;
- eine explizite Registrierung der neuen Testgruppen; der vorhandene Textmarker-Mechanismus blieb unverändert;
- ein gemeinsamer Bericht mit Schema-/Versions-/Konfigurationsangaben;
- die vorgesehenen Tests der historischen Informationsverfügbarkeit.

Ein großes Framework war ausdrücklich nicht verlangt. Diese kleinen konkreten Anforderungen sind aber auch nicht durch eine Roadmapdatei erfüllt. Status vorerst **teilweise umgesetzt**; benötigte Teile pilotnah nachholen.

### B5a/B5b

Der reale Batteriepilot prüft drei Mittelwertmodelle mit einer einzigen 60/40-Zeitteilung je Zelle. Er ruft den AR-Modus und `predict_capacity_distribution` nicht auf. Es gibt dort keine vollständige 2×2-Beobachtungs-Ablation, keine prädiktiven Intervallmetriken und keine prognostischen Ereigniswahrscheinlichkeiten. Die vorliegenden Zahlen widerlegen oder bestätigen daher die geplante Beobachtungsmodell-Frage noch nicht.

Die Funktion `run_leave_one_cell_out_panel` trainiert jedes Modell unabhängig auf dem Präfix genau der Zelle, die danach bewertet wird. Das ist eine **personalisierte zeitliche Zellenauswertung**, kein Leave-one-cell-out-Transferexperiment. Die Dokumentation relativiert das zwar, der API-Name und die Testüberschrift bleiben irreführend. Umbenennen oder ein echtes äußeres Zellensplit-Protokoll ergänzen; ein Transferexperiment ist für einen ehrlich benannten personalisierten Pilot nicht zwingend.

Weitere konkrete Ergänzungen:

1. Feste Zyklusursprünge und Horizonte statt ausschließlich einer vom späteren Reihenende abhängigen 60-%-Position. Der heutige Lauf ist ein legitimer retrospektiver Holdout, aber keine Auswertung eines zu einem vorab bekannten Zyklus gestarteten Einsatzprotokolls.
2. 2×2-Ablation mit nach R1/R2 korrekten Beobachtungsmodellen; Abdeckung, Breite und Interval Score auf zurückgehaltenen Daten.
3. Tatsächlich bekannter Ereignisstatus je Prognosehorizont und explizite Behandlung der Zensierung.
4. Der Adapter wirft aktuell alle Metadaten außer Kapazität und Reihenfolge weg. Mindestens Zell-ID, ursprüngliche Entladeposition, Zeitpunkt und Protokollkontext erhalten, damit fehlende Werte oder Bedingungenwechsel später prüfbar sind.
5. Reproduktionsskript/CLI für lokale `.mat`-Dateien und ein Manifest externer Artefakte mit vollständigen SHA-256-Werten. Die Tabelle enthält nur 16 Hexstellen; das sind gekürzte Fingerabdrücke, keine vollständigen SHA-256-Prüfsummen.
6. Der reale Pilot verarbeitet negative Mittelwert-Extrapolationen aktuell ohne eigenen Scope-Status in seinem MAE. Wenn negative Werte laut Modellvertrag eine Bereichsverletzung sind, muss der Aufrufer sie auch ausweisen.

Die Entscheidung, unklar lizenzierte Rohdaten nicht automatisch einzuchecken, ist nachvollziehbar. Sie verhindert weder ein lokales reproduzierbares Auswertungsskript noch ein vollständiges externes Datenmanifest. NASAs Katalog bezeichnet die Lizenz tatsächlich als „License not specified“; das ist eine Feststellung zum Katalog, kein hier abgegebenes Rechtsurteil über alle Nutzungsarten.

## 8. R7 — CAMELS-Blocker: selektiver ZIP-Zugriff funktioniert

**Positiver Befund:** Ein vollständiger Download des Archivs ist für einen kleinen Pilot technisch nicht zwingend.

Direkt gegen den im Plan genannten Zenodo-Release geprüft:

```text
URL: https://zenodo.org/records/13837553/files/camels_de.zip
Request: Range: bytes=-65557
Response: HTTP 206
Accept-Ranges: bytes
Content-Range: bytes 2175612867-2175678423/2175678424
```

Im ZIP-Endverzeichnis:

- 3194 Einträge;
- Central Directory: Offset `2175279341`, Länge `399061` Bytes;
- die Datei `CAMELS_DE_topographic_attributes.csv` liegt als eigener komprimierter Member vor.

Ich habe tatsächlich diesen Member über seinen lokalen Header und komprimierten Bytestrom geladen, entpackt und gegen seine CRC32 geprüft:

| Größe | Wert |
|---|---:|
| komprimierter Member | 103 944 Bytes |
| entpackter Inhalt | 246 997 Bytes |
| Transfer einschließlich ZIP-Ende, Verzeichnis und lokalem Header | 568 592 Bytes |
| CRC32-Prüfung | bestanden |
| SHA-256 des entpackten Inhalts | `5e9c7ec874e6b2495a49ac67a65cb0d046cd68e9090a5bd7d68b9aa1e9bed064` |

Zusätzlich wurde eine **vollständige hydrometeorologische Zeitreihe** selektiv gelesen und CRC-geprüft: `timeseries/CAMELS_DE_hydromet_timeseries_DE210480.csv`, 25 568 Datenzeilen, 3 025 961 entpackte Bytes bei 1 091 960 zusätzlich übertragenen Bytes einschließlich lokalem Header. SHA-256: `ce12ca14cb9fd55f96d60f571ae95afffb1e2945f3f8185186f5f4a1f8488510`. Der Header enthält unter anderem `discharge_vol_obs`, `discharge_spec_obs`, `precipitation_mean` und Temperaturfelder. Dies ist ein technischer Extraktionsbeleg; die Datenqualität und Eignung dieses Gebiets für das geplante Panel wurden noch nicht bewertet. Die Inhalte wurden für die Prüfung im Arbeitsspeicher verarbeitet, nicht als neuer Datensatz ins Repo übernommen.

**Schluss:** „Keine einzelne Datei per Zenodo-Dateiliste“ ist nicht gleichbedeutend mit „kein selektiver Archivzugriff“. Der bisherige generelle Größenblocker ist durch diesen Gegenbeleg entkräftet. Das ist noch kein durchgeführter Hydro-Datenpilot und garantiert nicht, dass jede Ausführungsumgebung denselben Zugriff erlaubt.

**Arbeitsauftrag für B3b:** kleiner HTTP-Range-Reader oder eine passende bestehende Bibliothek; ZIP-Verzeichnis einmal lesen, benötigte Metadaten und sechs ausgewählte Zeitreihen extrahieren. `206`, exakten `Content-Range`, Längen, ETag/Version, ZIP64-Fälle bei allgemeiner Verwendung und CRC prüfen. Wenn ein Server Range ignoriert und `200` mit dem gesamten Archiv liefert, früh abbrechen statt unbemerkt einen Großdownload zu starten. Anforderungsumfang begrenzen und reproduzierbare Extraktionshashes speichern.

Bei jedem neuen Lauf Offset-/Längenangaben aus dem dann geprüften Verzeichnis lesen. Die obigen Zahlen sind Befunde zu den tatsächlich erhaltenen Bytes, keine dauerhaft zu hartcodierenden Eigenschaften.

## 9. Kleinere wissenschaftliche und redaktionelle Nacharbeiten

### Brückenkarte am reflektierenden Rand

`R=K-q` ist eine sinnvolle genaue Zustandsabbildung. Für die reflektierte Queue gilt jedoch

\[
dq=(a-s)dt+dL,\qquad dR=(s-a)dt-dL,
\]

mit einem nur bei `q=0` aktiven Regulator `L`. Der einfache Satz `dot R=s-a` gilt dort nicht allgemein. Beispiel `q0=0, a=0, s=1, K=5`: tatsächlich `q=0`, `R=5` konstant; ohne Regulatorterm würde `R` wachsen. Dies entspricht der oberen Speicherbegrenzung bzw. Überlaufregel. Im Moduldocstring wird zusätzlich `q=0` fälschlich mit leerem Vorrat gleichgesetzt; unter dieser Abbildung ist der Vorrat dann voll. Leerstand entspricht `q=K`.

Die Werte des implementierten Mappings sind dadurch nicht automatisch falsch. Falsch bzw. unvollständig ist die behauptete randübergreifende Erhaltung der unreflektierten Bilanzgleichung. Brückenkarte und Docstrings korrigieren.

### Monte-Carlo-Abnahme der Diffusion

Die gitterbasierte Ereigniswahrscheinlichkeit unterschätzt die kontinuierliche Wahrscheinlichkeit. **Eine endliche Monte-Carlo-Schätzung muss aber nicht stets darunter liegen.** Der Test verlangt dennoch `p_mc<=p_exact+1e-9`. Stichprobenfehler kann diesen Vergleich auch bei korrektem Simulator verletzen. Außerdem ersetzt eine großzügige Bernoulli-Toleranz keine separate Abschätzung des Diskretisierungsbias.

Sauberer: Bridge-korrigierte Simulation gegen exakte Wahrscheinlichkeit; Monte-Carlo-Konfidenzprüfung passend zum Zufallsfehler. Gitterbias separat durch gekoppelte Pfade/Verfeinerung untersuchen. Für gekoppelte Pfade gilt die Ereignis-Inklusion gitterweise, nicht der strikte Vergleich einer Stichprobenquote mit einem Erwartungswert.

### B0: Bestätigter Fix versus allgemeiner Exaktheitsanspruch

Die relative Diskriminante behebt das ursprüngliche Zeiteinheiten-Gegenbeispiel. Nahe null wird aber weiterhin innerhalb einer festen relativen Toleranz der Doppelwurzelfall angenommen. Das ist eine Näherung, kein Beweis einer exakt mehrfachen Wurzel. Für diese weitere Frage wurde hier kein neuer praktisch relevanter Fehlklassifikationsfall nachgewiesen. Den bestätigten Fix deshalb anerkennen, aber den allgemeinen Anspruch „EXACT and robust“ entsprechend einschränken oder durch eine begründete stabile Grenzbehandlung absichern.

## 10. Konkrete Reihenfolge für Claude Code

```text
Arbeite vom aktuellen HEAD aus; Referenz dieses Reviews ist fcc9a43.

1. R1/R2: Residuen- und Innovationsstreuung trennen; echte Zyklusabstände
   in der AR-Prognose berücksichtigen. Analytische Mittelwerte/Varianzen
   und sparse-vs-dense Zielanfragen als Regressionen.

2. R3: schnelle Reservoirkernel zuverlässig integrieren; Mittelabfluss
   ohne Auslöschung berechnen. Konstantzufluss k=100000 und dt=1e-17
   unabhängig gegen geschlossene Formeln prüfen.

3. R4/R5: deterministische Diffusionsgrenze, bereits erreichte
   Batteriegrenze, NaN/Inf/negative Raten und Zählzustände korrigieren.
   Ungültige Eingaben nicht durch min/max/round zu plausiblen Ausgaben machen.

4. Roadmapstatus nach R6 bereinigen. B1 konkret pilotnah vervollständigen.
   Batteriepanel korrekt benennen; lokale Datenreproduktion mit vollständigen
   Hashes und Metadaten ermöglichen. Nach den AR-Fixes die fehlende
   prädiktive 2x2-Ablation ausführen, inklusive neutraler Ergebnisse.

5. B3b mit selektivem ZIP-Zugriff wieder aufnehmen. Das Review belegt
   funktionierende HTTP-Range-Requests und eine CRC-geprüfte Extraktion.
   Erst Auswahl und Datenprotokoll fixieren, dann das Panel bewerten.

6. Brücken-Randregel und Monte-Carlo-Testsemantik korrigieren.
   Vorhandene Originalregressionen erhalten, betroffene Prüfungen sowie
   erforderliche volle Repo-Gates ausführen. Ergebnisse und Grenzen aktualisieren.

Keine Modellgewinne erzwingen. Keine Datenanalyse als unabhängig
bestätigt bezeichnen, die nur als früherer manueller Lauf dokumentiert ist.
```

## 11. Kleiner eigenständiger Reproduktionsblock

Im Repo mit installiertem Paket oder `PYTHONPATH=src` ausführen. Die Ausgaben zeigen den geprüften Fehlerzustand; nach einer Korrektur müssen sie sich entsprechend ändern.

```python
import numpy as np
from scoped_correspondence.dynamics.capacity_degradation import (
    CapacityTrendFit, predict_capacity_distribution, first_mean_eol_crossing,
)
from scoped_correspondence.dynamics.linear_reservoirs import (
    convolution_discharge, reservoir_interval_discharge,
)
from scoped_correspondence.viability.first_passage_diffusion import (
    diffusion_ever_hitting_probability, diffusion_lower_hitting_probability,
)
from scoped_correspondence.validation.queueing_pilot import run_queueing_pilot

fit = CapacityTrendFit('linear', {'C0': 2., 'a': 0.}, 0., .8, (0.,), (2.,))
print('Zyklus 10, sparse:', predict_capacity_distribution(
    fit, 1., [10.], np.random.default_rng(1), 1)[0, 0])
print('Zyklus 10, dense:', predict_capacity_distribution(
    fit, 1., range(1, 11), np.random.default_rng(1), 1)[0, -1])
print('Korrekt:', 2 + .8**10)

print('Schneller Kernel:', convolution_discharge(1, [0], [1], [100000], lambda s: 1))
print('Korrekt:', -np.expm1(-100000.))
print('Kleiner Zeitschritt:', reservoir_interval_discharge(1, 0, 1, 1e-17))
print('Korrekt:', -np.expm1(-1e-17)/1e-17)

print('Konstante positive Bahn, jemals null:', diffusion_ever_hitting_probability(1, 0, 0))
print('Korrekt: 0')
fit_low = CapacityTrendFit('linear', {'C0': 1., 'a': .1}, 0., None, (0.,1.), (1.,.9))
print('Bereits unter EOL:', first_mean_eol_crossing(fit_low, 1.4, 10))
print('Korrekt: 0')

print('NaN-Eingabe:', diffusion_lower_hitting_probability(float('nan'), 1, 1, 1))
print('Muss ungültige Eingabe melden')
print('Gerundete Queue-Grenze:', run_queueing_pilot(0, .4, 1, 0, 1).to_dict())
```

## 12. Quellen und Nachprüfbarkeit

- [Geprüfter Commit](https://github.com/GenesisAeon/scoped-correspondence-formalism/commit/fcc9a438394a6a7596cc72c6807fdd2aa3f8f971)
- [Roadmap am geprüften Commit](https://github.com/GenesisAeon/scoped-correspondence-formalism/blob/fcc9a438394a6a7596cc72c6807fdd2aa3f8f971/DOMAIN_EXPANSION_ROADMAP.md)
- [Kapazitätsmodelle](https://github.com/GenesisAeon/scoped-correspondence-formalism/blob/fcc9a438394a6a7596cc72c6807fdd2aa3f8f971/src/scoped_correspondence/dynamics/capacity_degradation.py)
- [Reservoir-Implementierung](https://github.com/GenesisAeon/scoped-correspondence-formalism/blob/fcc9a438394a6a7596cc72c6807fdd2aa3f8f971/src/scoped_correspondence/dynamics/linear_reservoirs.py)
- [Diffusions-Erstpassage](https://github.com/GenesisAeon/scoped-correspondence-formalism/blob/fcc9a438394a6a7596cc72c6807fdd2aa3f8f971/src/scoped_correspondence/viability/first_passage_diffusion.py)
- [NASA-Katalog: Datenbeschreibung und nicht spezifizierte Lizenz](https://data.nasa.gov/dataset/li-ion-battery-aging-datasets), erneut gelesen am 24.09.2026.
- [CAMELS-DE, fixierter Zenodo-Release](https://zenodo.org/records/13837553) und [Archivvorschau](https://zenodo.org/records/13837553/preview/camels_de.zip?include_deleted=0), erneut geprüft am 24.09.2026. Der Nachweis des selektiven Downloads stammt aus den tatsächlich ausgeführten HTTP-Anfragen und CRC-Prüfungen dieses Reviews.
- [statsmodels AutoRegResults](https://www.statsmodels.org/stable/generated/statsmodels.tsa.ar_model.AutoRegResults.html), offizielle Referenz für die Trennung von Innovationen und übrigen AR-Ergebnisgrößen; die Varianzformeln und Gegenbeispiele oben sind unmittelbar aus der Rekursion abgeleitet.

Die Repository-Dateien wurden für dieses Review nicht verändert oder gepusht. Die Fehlerreproduktionen liefen in einer lokalen Prüfsnapshot-Umgebung.
