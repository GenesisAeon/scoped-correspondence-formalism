# Themenbreite erweitern — Roadmap (2026-09-24)

Antwort auf `prompts/Answers/nicht_stationäre_Treiber/Astra7.txt` und die
zugehörige `SCF_DOMAIN_EXPANSION_IMPLEMENTATION_PLAN.md` (Astra, 2026-09-24,
Referenzcommit `bd87a44`) — ein ausgearbeiteter Vorschlag, SCF an vier neuen
Anwendungsdomänen zu erproben: Warteschlangen, Hydrologie, Batteriealterung,
kooperative Agenten. Anders als `CAPABILITY_EXPANSION_ROADMAP.md` (die
bestehende Module härtete) fügt dieser Plan **neue Domänenmodule** hinzu.

Johanns Auftrag (2026-09-24): "Volle Roadmap B0–B7" (nach expliziter
Rückfrage zum Umfang, inkl. der beiden echten Datenpiloten CAMELS-DE und
NASA-Batterie).

Gleiche Disziplin wie bei den vorherigen Roadmaps: additive Module, Hand-
Nachrechnung vor Code, unabhängige Reproduktion jedes Astra-Befunds vor dem
Fix, `verify_*.py` mit Scope-Verletzungen, volle Suiten-Regression nach
jedem Paket, negative/neutrale Ergebnisse zählen genauso wie positive.

## Pakete

| Paket | Inhalt | Status |
|---|---|---|
| B0 | Zeiteinheitenfehler in `_analytic_component_critical_times` (skalenabhängige absolute Diskriminantenschwelle) | ✅ erledigt |
| B1 | Protokoll, Provenienz, Testzuordnung, diese Roadmap | ✅ erledigt (vervollständigt in Paket 8 nach R6) |
| B2a | Fluidrückstau und Bestandsbrücke | ✅ erledigt |
| B2b | CTMC-Erstpassage und Queue-Pilot | ✅ erledigt |
| B3a | Lineare Reservoirs und Gedächtnisbrücke | ✅ erledigt |
| B3b | CAMELS-DE-Datenpilot (echte externe Daten) | ⛔ blockiert (dokumentiert, nicht praktikabel in dieser Umgebung) |
| B4 | Diffusions-Erstpassage (Brownsche Bewegung mit Drift) | ✅ erledigt |
| B5a | Kapazitätsmodelle und Beobachtungs-Ablation | ✅ erledigt |
| B5b | NASA-Batteriedatenpilot (echte externe Daten, Lizenz laut Astra ungeklärt) | ✅ erledigt (Lizenz-Blocker sauber behandelt) |
| B6a | Endliche kooperative Agentenaufgaben | ✅ erledigt |
| B6b | Wiederholte Aufgabe / OpenSpiel | ausdrücklich optional, nicht Teil dieser Runde |
| B7 | Gemeinsamer Ergebnisvergleich, Fähigkeitsübersicht | ✅ erledigt |

Themenatlas (Ökologie, Energie, Verkehr, Lieferketten, Neurowissenschaft,
Astronomie) ist explizit **zweite Ausbaurunde**, nicht Teil dieses Auftrags.

## B0 — Zeiteinheitenfehler (erledigt)

Unabhängig reproduziert: `A=[[-0.1,-10],[10,-0.1]]`, `x0=[0,1]`, `H=10`,
Grenze `0.95` klassifiziert bei `c=1` korrekt als `transient_violation`
(Peak `0.9844639845000663` bei `t≈0.1561`, deckt sich mit der analytischen
Herleitung `arctan(100)/10`). Unter `A_new=c*A`, `H_new=H/c`, `c=1e-6`
(exakte Zeit-Umskalierung derselben Trajektorie) meldete der Code
fälschlich `no_violation_in_horizon` mit Peak `0.186` am Horizontende
`t=1e7` — der absolute Diskriminanten-Schwellwert `±1e-9` griff nicht mehr,
da `D` selbst wie `c²` skaliert.

**Fix:** `_analytic_component_critical_times` vergleicht jetzt den
skaleninvarianten relativen Diskriminanten `D / scale` (mit
`scale = max(tr(A)², 4·|det(A)|)`, skaliert exakt wie `D` unter `A→c·A`)
gegen eine dimensionslose Schwelle `1e-9`. `scale == 0` (erzwingt `D == 0`,
z. B. Nullmatrix) wird direkt dem Doppelwurzel-Zweig zugeordnet.

**Verifiziert:** `verify_transient_amplification.py`,
`astra_b0_scale_invariant_discriminant_classification` (9/9 Checks
insgesamt) — identische Peak-Höhe/Klassifikation für `c ∈ {1e-6, 1, 1e6}`,
Peak-Zeit skaliert exakt mit `1/c`; Nullmatrix und exakte Doppelwurzel als
Randfälle abgedeckt; alle bisherigen Regressionen unverändert grün.

Docs: `docs/transient_amplification.md` (neuer Correction-Block).

## B1 — Gemeinsame Versuchskonventionen (erledigt)

Diese Roadmap-Datei selbst erfüllt den Kern von B1 für die erste
Pilotenrunde. Weitergehende Infrastruktur (Manifest-Schema-Erweiterung,
`available_at`-Filterhilfen, Ereignisbericht-Serialisierung) wird direkt an
dem Piloten ergänzt, der sie zuerst tatsächlich braucht (B2b für das
Ereignisbericht-Schema, B3b für die Manifest-Erweiterung) — kein
vorgezogenes generisches Framework ohne konkreten ersten Nutzer, siehe
Plan Abschnitt 7 ("Nicht vorziehen").

## B2a — Fluidrückstau und Bestandsbrücke (erledigt)

`dynamics/queueing.py`: exakter reflektierter Fluidrückstau über
stückweise konstante Ankunfts-/Bedienraten, sampling-frei (jedes Segment
ist monoton, daher lösen Grenzwertdurchgänge eine einzige lineare
Gleichung). Astras festes Beispiel (`q0=0`, `s=1`, `H=10`, `K=5`)
reproduziert: gleichmäßige Ankunft `a=0.8` hält den Rückstau bei 0;
Laststoß `a=4` auf `[0,2]` erreicht Maximum `q=6` bei `t=2`, erstes
Erreichen von `K=5` bei `t=5/3` — beide bei GLEICHER Gesamtlast (8).
Bestandsbrücke `R=K-q` bis zum ersten Kapazitätsdurchbruch exakt;
Negativtest (konstanter vs. zustandsabhängiger Abfluss) bestätigt
Divergenz. Verifiziert: `verify_queueing.py` (5/5). Docs:
`docs/queueing_pilot.md`.

## B2b — CTMC-Erstpassage und Queue-Pilot (erledigt)

`viability/first_passage_ctmc.py`: exakte M/M/1-Erstpassage über
absorbierenden Generator, `P(tau_K<=H)=[p0 exp(H*Q_abs)]_K`. Referenzwert
`lambda=1,mu=2,K=2,H=1` → `0.1777365760981911` unabhängig nachgerechnet
(exakter Treffer, `<1e-12`); reine Ankünfte reduzieren exakt auf die
Poisson-Formel `1-2/e`. `H=0`, bereits erreichtes `K` und `lambda=0` fallen
alle aus derselben Konstruktion ohne Sonderfälle. Event-basierte Simulation
(fester Seed) stimmt innerhalb 5σ-Toleranz überein. Stückweise Raten
multiplizieren Matrixexponentiale in Zeitreihenfolge (Aufteilung mit
identischen Raten ändert nichts; echte Ratenänderung weicht vom naiven
Mittelwert ab). `validation/queueing_pilot.py` zeigt den Kernpunkt in einer
Zahl: bei `rho=0.5<1` bleibt der deterministische Fluidrückstau exakt 0,
während die stochastische Treffwahrscheinlichkeit `≈5,6%` beträgt — ein
Mittelwertmodell allein wäre hier fälschlich "sicher". Verifiziert:
`verify_queueing_first_passage.py` (7/7), `verify_queueing_pilot.py` (3/3).
Docs: `docs/queueing_pilot.md`.

## B4 — Diffusions-Erstpassage (erledigt)

`viability/first_passage_diffusion.py`: exakte Erstpassagewahrscheinlichkeit
für Brownsche Bewegung mit Drift an einer unteren Schranke, log-raum-stabile
Kombination (`logsumexp`). Kontrollwerte `x0=1,sigma=1,H=1`: `mu=0` →
`0.31731050786291415`, `mu=1` → `0.09041777356648555` trotz `E[X_1]=2` —
unabhängig nachgerechnet, exakter Treffer. Unendlicher Horizont
(`exp(-2*mu*x0/sigma^2)`) explizit von der endlichen Aussage getrennt.
Einheiteninvarianz (`t'=t/c, mu'=c*mu, sigma'=sqrt(c)*sigma, H'=H/c`) über
12 Größenordnungen exakt bestätigt. Deterministischer Grenzfall (`sigma=0`)
und Randfälle (`H=0`, `x0<=0`) explizit behandelt. Unabhängige
Euler-Maruyama-Simulation (fester Seed) stimmt innerhalb 6σ-Toleranz
überein und liegt strukturell als Unterschätzung vor (Gitterpunkte
übersehen Durchgänge zwischen den Punkten) — dafür zusätzlich die
Bridge-Formel `exp(-2xy/(sigma^2*Delta))` bereitgestellt. Verifiziert:
`verify_first_passage_diffusion.py` (7/7). Docs:
`docs/first_passage_diffusion.md`.

## B6a — Endliche kooperative Agentenaufgaben (erledigt)

`validation/cooperative_agents_pilot.py`: drei vollständig enumerierte
Kontrollaufgaben, nutzt den vorhandenen BROJA-PID-Löser unverändert (keine
neue Informationsbibliothek). XOR: `0,5` ohne Nachricht (Ausschöpfung aller
4 möglichen Entscheidungsregeln), `1,0` mit korrekt übertragenem Bit; PID
bestätigt die Lehrbuch-Synergie-Signatur (`redundancy=0, unique=0,
synergy=1 bit`) direkt am Löser, nicht nur behauptet. Redundanzaufgabe:
`1,0` mit/ohne Kommunikation, PID zeigt reine Redundanz. Fehlerkanal:
`epsilon ∈ {0, 0,1, 0,5, 1}` für festen (`1-epsilon`) und optimalen
Dekoder (`max(epsilon,1-epsilon)`) — bei `epsilon=1` ist die
systematisch invertierte Nachricht vom informierten Dekoder vollständig
rekonstruierbar. Kostenschwelle `lambda<0,5` für Senden im XOR-Fall exakt
bei Gleichheit geprüft; Redundanzaufgabe gewinnt bei keinem `lambda>0`.
Verifiziert: `verify_cooperative_agents_pilot.py` (6/6). Docs:
`docs/cooperative_agents_pilot.md`.

## B3a — Lineare Reservoirs und Gedächtnisbrücke (erledigt)

`dynamics/linear_reservoirs.py`: exakte Reservoir-Update-Formel
(`-expm1(-kΔ)/k` statt naivem `(1-exp(-kΔ))/k` zur Vermeidung von
Auslöschung nahe `k→0`), Kontrollzahlen `S0=3,u=2,k=0.5,Δ=1` →
`S1≈3.393469340287367`, `q̄≈1.6065306597126332` — unabhängig nachgerechnet
und gegen `solve_ivp` gegengeprüft. Identifizierbarkeit geprüft: `k1=k2`
reduziert auf Ein-Speicher-Fall, `alpha2=0` ebenso, Labeltausch `1↔2`
ändert die Gesamtsumme nicht, verschiedene Anfangsaufteilungen bei
gleichem `S0` divergieren jedoch messbar (nicht identifizierbar aus der
Summe allein). Faltungsdarstellung (Mori-Zwanzig-Kernel, spezialisiert auf
diesen diagonalen Fall) gegen die diskrete Schrittrekursion geprüft (`<1e-8`).
Die allgemeinere Erweiterung von `linear_memory_projection.py` um einen
angeregten verborgenen Block wurde gemäß der im Plan explizit erlaubten
Alternative NICHT gebaut — stattdessen direkt die Hydro-Faltung
implementiert. Verifiziert: `verify_linear_reservoirs.py` (9/9). Docs:
`docs/linear_reservoirs.md`.

## B5a — Kapazitätsmodelle und Beobachtungs-Ablation (erledigt)

`dynamics/capacity_degradation.py`: drei phänomenologische Mittelwertmodelle
(Persistenz, linear, Potenzgesetz) getrennt von einer 2×2-Beobachtungs-
Ablation (unabhängig vs. AR(1)-Residuen) — bewusst KEINE getrennte
Identifikation von irreversibler Alterung, reversiblen Effekten und
Messfehler aus einer einzelnen Reihe (nicht identifizierbar). Exakte
Rekonstruktion rauschfreier linearer und Potenzgesetz-Kurven; `p=1`
reduziert exakt auf den linearen Fall (Residuum ~0 bei linear generierten
Daten). AR-Block ohne vorprogrammierten Gewinn bei unabhängigen Residuen
(`|phi|<0,15` bei n=500), erkennt echte Korrelation (`phi=0,8`) auf
`<0,1` genau. Mittelwert-Grenzpunkt und beobachtetes Erstereignis explizit
getrennt gehalten. Negative Extrapolationen werden offen als
Modellbereichsverletzung ausgegeben, nicht stillschweigend abgeschnitten;
beobachtete Kapazitätsanstiege bleiben unangetastet in den Rohdaten.
Verifiziert: `verify_capacity_degradation.py` (7/7). Docs:
`docs/capacity_degradation.md`.

## B5b — NASA-Batteriedatenpilot (erledigt, Lizenz-Blocker sauber behandelt)

Astras Lizenzbedenken unabhängig bestätigt: NASAs eigene CKAN-API
(`data.nasa.gov/api/3/action/package_show?id=li-ion-battery-aging-datasets`)
meldet `license_title: "License not specified"`. Gemäß Plan Abschnitt 5.1
("lokaler Downloader plus synthetische Parser-Fixture") wurden Rohdaten und
abgeleitete Zyklenwerte NICHT ins Repo übernommen — kein Manifest-Eintrag
in `data/real_data_manifest.json` (dessen eigener Prüfer verlangt eine
tatsächlich vorhandene Datei je Eintrag). `verify_battery_aging_pilot.py`
läuft vollständig gegen eine synthetische Fixture (6/6, kein Netzwerk
nötig). Ein echter lokaler Lauf (4 Zellen B0005/6/7/18, ~210 MB ZIP,
sha256 aller Dateien notiert) wurde dennoch durchgeführt und ehrlich als
manuelle, nicht CI-gebundene Reproduktion dokumentiert
(`docs/battery_aging_pilot.md`): gemischtes Ergebnis (linear gewinnt bei
2 Zellen, Potenzgesetz bei 2 Zellen, Persistenz nie), B0007 zeigt echte
Rechtszensierung (min. beobachtete Kapazität 1,4005 Ah, nie ≤1,4 Ah
innerhalb 168 Zyklen). Verifiziert: `verify_battery_aging_pilot.py` (6/6).
Docs: `docs/battery_aging_pilot.md`.

## B3b — CAMELS-DE-Datenpilot (blockiert, konkret dokumentiert)

Netzwerkzugriff auf Zenodo funktioniert (`zenodo.org/records/13837553`,
HTTP 200 bestätigt), aber der Datensatz liegt nur als EIN EINZIGES Archiv
vor: `camels_de.zip`, `2.178.320.889` Bytes (≈2,18 GB) — kein Teildownload
einzelner Einzugsgebiete über die Zenodo-API möglich, kein Zwischenformat
mit selektivem Zugriff verfügbar. Für die verfügbare Umgebung (begrenzter
Arbeitsspeicher/Zeit für einen einzelnen Download- und Entpackschritt
dieser Größe innerhalb eines Werkzeugaufrufs) nicht praktikabel.

Gemäß Plan Abschnitt 16 ("Ein blockierter Datenpilot bleibt offen") und
Abschnitt 5.1 (analytische/synthetische Teile fertigstellen, Datenblock mit
konkretem Grund offen führen): B3a (Reservoir-Mathematik, Gedächtnisbrücke)
ist vollständig abgeschlossen und unabhängig von B3b; nur der ECHTE
Datenpilot (6 Einzugsgebiete, Zeitteilung 1991–2020, Panel-Auswertung nach
Plan Abschnitt 9.4–9.6) bleibt unausgeführt. Kein synthetischer Ersatz wird
als Abschluss dieses Datenpilots ausgegeben (Plan Abschnitt 16: "Ein
synthetischer Ersatz schließt keinen verlangten realen Datenpilot ab").

**Konkreter Blocker für eine Wiederaufnahme:** Zugriff auf einen
Teildownload einzelner CAMELS-DE-Einzugsgebiete (z. B. über eine künftige
gefilterte API, einen Data-Mirror mit Einzeldateien, oder ausreichend
Zeit/Speicher für den vollen 2,18-GB-Download in einer Umgebung mit
entsprechenden Ressourcen).

## B7 — Gemeinsamer Ergebnisvergleich und Fähigkeitsübersicht (erledigt)

`docs/capability_overview.json`/`.md` um 5 neue Einträge erweitert
(Warteschlangen-Trio, lineare Reservoirs, Diffusions-Erstpassage,
Batteriealterungs-Trio, kooperative Agenten) — jeweils mit Frage,
Modellklasse, Annahmen, Evidenzart, Prüfskripten und bekannten Grenzen,
gleiches Schema wie die 18 bestehenden Modul-Einträge.

**Ergebnisvergleich nach Plan Abschnitt 16.2:**

| Domäne | Welche Information verlor die Vereinfachung? | Reichte ein einfacheres Modell? | Was war exakt herleitbar vs. nur an Daten beobachtet? |
|---|---|---|---|
| Warteschlangen (B2) | Zeitliche Form des Lastverlaufs bei gleicher Gesamtlast (Laststoß vs. gleichmäßig) | Nein für Ereignisrisiko: Mittelwertmodell meldet 0% Rückstau, Stochastik ~5,6% Treffwahrscheinlichkeit bei GLEICHEN Raten | Beide Modelle exakt herleitbar (Fluid-ODE, absorbierender CTMC-Generator); kein Datenpilot in dieser Runde |
| Hydrologie (B3) | Zweite Abfluss-Zeitskala; Anfangsspeicher-Aufteilung nicht identifizierbar aus der Summe | Unbeantwortet — echter Datenpilot blockiert (B3b) | Reservoir-Update und Faltung exakt herleitbar; reale Einzugsgebiets-Frage bleibt offen |
| Diffusions-Erstpassage (B4) | Durchgangsrisiko bei positivem Erwartungswert (`E[X_1]=2`, aber `P(Erreichen)≈9%`) | Nein — Mittelwertaussage allein ist irreführend | Vollständig exakt herleitbar (Reflexionsprinzip); keine reale Datenfrage in dieser Runde |
| Batteriealterung (B5) | Ob Alterung linear oder als Potenzgesetz verläuft — uneinheitlich je Zelle | Uneinheitlich: linear gewinnt bei 2/4, Potenzgesetz bei 2/4 realen Zellen, Persistenz nie | Modelle exakt herleitbar; reale Zellen zeigen echte Rechtszensierung (B0007) — Lizenz verhindert Redistribution, Ergebnis nur manuell reproduziert |
| Kooperative Agenten (B6) | Ob getrennte Beobachtungen gemeinsam mehr Information tragen als einzeln (Synergie) | Nein für XOR (0,5→1,0 mit Nachricht); Ja für Redundanz (Kommunikation hilft nie) | Vollständig exakt durch Enumeration; PID-Zerlegung vom vorhandenen Löser bestätigt, nicht neu behauptet |

Keine domänenübergreifende Mittelwert-Rangliste gebildet (Plan Abschnitt
16.2: inkompatible Maßeinheiten). Transferierbar sind die Verfahren
(exakte Diskriminanten-/Erstpassage-/Faltungskonstruktionen), nicht die
Parameterwerte.

**Offene Teilaufgaben, sichtbar gehalten:** B3b (CAMELS-DE, blockiert),
B6b (wiederholte Agentenaufgabe/OpenSpiel, ausdrücklich optional), der
Themenatlas (Ökologie/Energie/Verkehr/Lieferketten/Neurowissenschaft/
Astronomie, zweite Ausbaurunde) und B0's verbleibende Frage nach
absoluten Schwellen in `_adequate_sample_count`/Abtastdichte, die denselben
Klassifikationspfad beeinflussen könnten (Plan Abschnitt 6, Punkt 5) —
nicht erneut geprüft, da sie ausschließlich die REPORTED-Trajektorien-
Auflösung betreffen, nicht die (bereits abtastungsunabhängige)
Klassifikation selbst.

**Volle Regression zum Abschluss dieser Runde:** 66/66 Mathe-, 16/16
Daten-, 0 defekte Links (siehe Commit-Historie für die einzelnen
Zwischenstände je Paket).

## Paket 8 — Astras Zweitreview (SCF_Review_fcc9a43.md)

Astra prüfte den B7-Commit `fcc9a43` unabhängig nach und fand sieben
nummerierte Befunde (R1–R7), mehrere davon real und mit exakten
Gegenbeispielen belegt — alle einzeln nachgerechnet, bevor etwas geändert
wurde (Kontrollwerte trafen exakt auf Astras berichtete Zahlen).

**R1 (hoch, echter Bug):** `predict_capacity_distribution` verwechselte
die AR(1)-Innovationsstreuung mit der gesamten Residuenstreuung (Faktor
`1/(1-phi²)` zu groß). Behoben durch getrennte Schätzung von
`innovation_std` aus der AR-Rekursion selbst.

**R2 (hoch, echter Bug):** dieselbe Funktion schritt das Residuum pro
angefragtem Ausgabeelement genau einen Schritt fort, unabhängig vom
tatsächlichen Zyklusabstand — `predict(...,[10])` und
`predict(...,[1,...,10])` ergaben unterschiedliche Antworten für denselben
Zyklus 10. Behoben durch expliziten `origin_cycle` und exakte
`d`-Schritt-AR(1)-Fortpflanzung.

**R3+R3b (hoch, zwei echte numerische Bugs):** `convolution_discharge`
übersah schnelle Kernel vollständig (`k=100000` ergab `2e-45` statt `≈1`);
`reservoir_interval_discharge` verlor durch Auslöschung bei sehr kleinem
`dt` jede Genauigkeit (`dt=1e-17` ergab `0.0` statt `≈1`). Behoben durch
Substitution `v=k(t-s)` vor der Quadratur bzw. die direkte, auslöschungsfreie
Form `qbar=k·S0·E(z)+alpha·u·(1-E(z))`.

**R4a+R4b (echte Bugs):** `diffusion_ever_hitting_probability` prüfte
`mu<=0` vor dem deterministischen `sigma=0`-Fall (ein konstanter, rauschfreier
Pfad meldete fälschlich sichere Erreichung); `first_mean_eol_crossing`
meldete `None` statt `0.0` für eine bereits unter der Grenze liegende
Mittelwertkurve bei `n=0`. Beide behoben durch Umsortierung der
Fallunterscheidung bzw. vorgezogene `n=0`-Prüfung.

**R5 (hoch für die öffentliche API, echte Bugs):** NaN-Eingaben wurden
über `min(1.0,nan)`/`max(0.0,nan)` in plausibel aussehende, aber falsche
Ergebnisse verwandelt; `run_queueing_pilot` rundete eine reelle Schwelle
(`0.4`→`0`) still auf eine andere CTMC-Anfrage um. Behoben durch explizite
Endlichkeits-/Ganzzahligkeitsprüfungen in allen betroffenen Funktionen
(`queueing.py`, `queueing_pilot.py`, `first_passage_ctmc.py`,
`first_passage_diffusion.py`).

**R6 (Umfang/Benennung, keine numerischen Bugs):** B1 war nur teilweise
umgesetzt — ergänzt um `docs/domain_expansion_protocol.md` (Mess-/Ereignis-
/Zeitkonventionen, Berichtsschema) und explizite Testgruppen-Registrierung
in `run_verification_suite.py`. `run_leave_one_cell_out_panel` wurde in
`run_personalized_cell_panel` umbenannt (personalisierte Zellenauswertung,
kein Transferexperiment); der Adapter behält jetzt Zyklusposition, Temperatur
und Zeitstempel; die Dokumentation zeigt vollständige (64-Hex) statt
gekürzter SHA-256-Werte; negative Extrapolationen werden je Modell explizit
gezählt statt still in den MAE-Durchschnitt einzufließen; ein fester
absoluter `n_train`-Ursprung ist jetzt zusätzlich zur relativen Aufteilung
verfügbar.

**R7 (positiver Gegenbeleg):** Astra zeigte per HTTP-Range-Requests und
CRC32-geprüfter Extraktion, dass selektiver Zugriff auf einzelne
CAMELS-DE-Mitglieder OHNE Volldownload des 2,18-GB-Archivs technisch
funktioniert. Status und Fortsetzung: siehe eigener B3b-Abschnitt unten.

**Kleinere Korrekturen:** Bestandsbrücken-Docstring (zwei unterschiedliche,
nicht zu vermischende Bild­lichkeiten `S≡q` vs. `R=K-q`; Regulatorterm an
der reflektierenden Grenze) präzisiert und mit einer expliziten
Regressionsprüfung belegt; Monte-Carlo-Abnahmetest von einer unzulässigen
strikten Richtungsannahme auf die bereits vorhandene statistische Toleranz
reduziert; B0s "exact and robust"-Anspruch auf die Zweigwahl beschränkt
(die Klassifikation nahe `D/scale≈0` bleibt eine tolerenzbasierte Näherung,
kein Beweis einer exakt mehrfachen Wurzel).

**Ergebnis:** alle R1–R6-Befunde unabhängig reproduziert (exakte
Übereinstimmung mit Astras Zahlen) und behoben; neue Regressionstests in
allen betroffenen `verify_*.py`. Volle Regression: siehe Commit-Nachricht.
