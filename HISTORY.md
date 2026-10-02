# Projektgeschichte und Audit-Trail

Ausgelagert aus `README.md` (2026-09-27), damit die README als knappe
Einstiegsseite lesbar bleibt. Dieser Datei-Inhalt ist die vollständige,
chronologisch gewachsene Historie — jede Behauptung hier ist an einen
Commit, ein Review-Dokument oder einen `verify_*.py`-Lauf gebunden.
Nichts wurde beim Verschieben inhaltlich verändert oder gekürzt.

## Branch `j-series` → Release `0.42.0a1` (2026-10-01/02)

Die Integration in `master` ist als Release `0.42.0a1` vorgesehen, siehe
[RELEASE_NOTES.md](RELEASE_NOTES.md).

- 2026-10-02: Claude hat die Integration auf Johanns OK gemergt (Merge
  `ea96409`, interner Tag `v0.42.0a1`).
- Danach wurde das Repo öffentlich gestellt und mit Zenodo verknüpft.
- Der erste öffentliche Release ist `0.42.0` (PyPI + Zenodo).

**Review-Kette:** `SCF_REVIEW_J_SERIES_6b3a331` → `SCF_FOLLOWUP_REVIEW_637bc1c`
→ `SCF_PMF_REVIEW_51b1a38`. Das letzte Review gab das Merge-GO für
`5c3054f`.

Auf dem Branch `j-series` wurden in einer
Sitzung vier Serien nach der Paket-pro-Commit-Disziplin umgesetzt, jede mit
eigener Roadmap, handhergeleiteten Kontrollen und gezielten Mutanten:

- **J0–J12** Scope, Komposition und Evidenz
  ([SCOPE_COMPOSITION_EVIDENCE_ROADMAP.md](SCOPE_COMPOSITION_EVIDENCE_ROADMAP.md)).
- **MU0–MU7** Myonium-Gravitations-Messmodell, synthetisch; echte
  Strahldaten wegen Lizenz zurückgestellt
  ([MUONIUM_GRAVITY_ROADMAP.md](MUONIUM_GRAVITY_ROADMAP.md)).
- **TP/SK/SA** Kandidatenpiloten Polyeder, Sakurai, Saturn
  ([CANDIDATE_PILOTS_ROADMAP.md](CANDIDATE_PILOTS_ROADMAP.md)).
- **ON0–ON7** adaptive modulare Netzwerke (organoid-motiviert): synthetischer
  Kern abgeschlossen, Realdatenzweig blockiert
  ([ORGANOID_NETWORK_ROADMAP.md](ORGANOID_NETWORK_ROADMAP.md)).

Stand am Ende: `--category all` 138/138, Linkprüfung 0 defekt,
gezielte Mutanten 105 (104 per Inhaltsassertion getötet, 1 vorregistriert
äquivalent; [Bericht](verification/targeted_mutations_report.json)). Offene
Quellenfragen und Entscheidungen: [DEEP_RESEARCH_BACKLOG.md](DEEP_RESEARCH_BACKLOG.md).

**Externe Review `SCF_REVIEW_J_SERIES_6b3a331` (2026-10-01)**, gleicher Tag,
Commit `Followup-Review-Fix`:

- **Befunde:** R1 bis R5 sowie E3 und E4 wurden unverändert reproduziert und
  behoben, jeder mit einem Regressionstest auf das exakte Gegenbeispiel.
  - R1 und R2: falsche Schranken in `closure/error_bounds.py`, einem Modul
    von vor der J-Serie.
  - R3 und R5: ungültige Eingaben in den ON-Decodern.
  - R4: NaN-Masse in DI bzw. BROJA.
  - E3: striktes JSON.
  - E4: exaktes α.
- **Methodik:** Die Punkte §5.1 bis §5.3 sind umgesetzt. Das gepaarte
  Benchmark-Protokoll ändert nur die eingefrorenen Werte.
- **Nachlieferung:** Das MU-/Kandidaten-Oracle wurde gegen die Produktion
  geprüft.
- **Stand danach:**
  - `--category all` 139/139;
  - Linkprüfung 0 defekt;
  - Mutanten 116 (115 getötet, 1 vorregistriert äquivalent). Ein
    J3-Mutant wurde nach der E4-Änderung auf die neue Rangzeile umgezielt.
- Details: Abschnitt „Followup-Review-Fix“ in
  [ORGANOID_NETWORK_ROADMAP.md](ORGANOID_NETWORK_ROADMAP.md).

## Aktueller Stand (2026-09-20)

Seit dem 16. September 2026 ist dieses Repository ein **installierbares
Python-Paket** (`scoped-correspondence`, aktuell `0.41.0a1`) unter
`src/scoped_correspondence/` — nicht mehr nur Dokumentation und
eigenständige Skripte. Die Milestone-Zählung (`M1` beginnend am
16. September) ist seither über `M54` hinausgewachsen; ein einzelner
aktueller Endstand wird hier bewusst nicht mehr genannt, weil er mit jedem
Paket sofort wieder veraltet — siehe stattdessen
[docs/capability_overview.md](docs/capability_overview.md) für den
tatsächlichen, laufend aktualisierten Modulstand. Der untenstehende
"Revision 3.2"-Abschnitt beschreibt den Stand VOR dieser Umstellung und ist
als historischer Kontext erhalten (siehe
[REVISION_3_2026-09-16.md](REVISION_3_2026-09-16.md)); die aktuelle
Modul-/Paketstruktur steht in der README.

### Status, Prüfungen und offene Punkte

- **Unabhängige `verify_*.py`-Suiten** unter `verification/` laufen
  aktuell alle grün, per eingecheckten, getrennten Prüfaufrufen (Astra,
  2026-09-24, [CAPABILITY_EXPANSION_ROADMAP.md](CAPABILITY_EXPANSION_ROADMAP.md)
  Paket 0 — vorher nur als nicht eingechecktes `audit_review/run_all_local.py`
  lokal vorhanden):
  `python scripts/run_verification_suite.py --category math`,
  `--category data` (lädt echte Datensätze, siehe
  [docs/real_data_provenance.md](docs/real_data_provenance.md)),
  `--category links` (interne Markdown-Linkprüfung). Läuft auch automatisch
  in [GitHub Actions](.github/workflows/verify.yml). Siehe
  [VERIFICATION.md](VERIFICATION.md) für die Einzelläufe und ihre
  Aussagekraft, sowie [docs/capability_overview.md](docs/capability_overview.md)
  für eine kompakte Fragestellung/Voraussetzungen/Evidenz/Grenzen-Übersicht
  je Modul.
- Ein externer Code-Audit ("Tiefenanalyse", 2026-09-20) fand 9 echte
  Korrektheitslücken (P0/P1/P2) in bereits gemergtem Code; alle wurden
  am selben Tag behoben, gegen das jeweilige Audit-Gegenbeispiel verifiziert
  und gegen alle Suiten regressionsgetestet. Details, Priorisierung und
  verbleibende Punkte: [AUDIT_ROADMAP.md](AUDIT_ROADMAP.md).
- [docs/structural_relations.md](docs/structural_relations.md) definiert
  eine Prüfsprache für Strukturbeziehungen zwischen Modellen (Beziehungstyp,
  Konstruktion, Geltungsbereich, geprüfte vs. angenommene Voraussetzungen,
  Reichweite) — als Gegengewicht zu pauschalen "keine gemeinsame
  Mathematik"-Formulierungen, ohne unbegründete Identitäten wieder zu öffnen.
- Der Cygnus-X1-Pilot (`data/cygnus_x1_radio_epochs.yaml`,
  [docs/cygnus_pilot.md](docs/cygnus_pilot.md)) ist als **unverifiziert**
  gekennzeichnet (Entscheidung 2026-09-20, `AUDIT_ROADMAP.md` Punkt 1): die
  Einzelepochen-Granularität stammt wahrscheinlich aus einer KI-Interpolation
  zu vier echten Paper-Kennzahlen (Prabu et al. 2026), nicht aus realen
  archivierten Einzelmessungen. Der Pilot bleibt als **illustrative
  Methodendemonstration** im Repo (Rechnung korrekt und reproduzierbar),
  gilt aber nicht als unabhängig verifizierte empirische Validierung.
- Das Formal-Hooks-/Stable-Release-Milestone aus
  [ARCHITECTURE_ROADMAP.md](ARCHITECTURE_ROADMAP.md) ist der einzige noch
  offene ursprüngliche Meilenstein; eine SemVer-`1.0`-Stabilisierung steht
  noch aus (aktuell `0.41.0a1`, Alpha).
- Drei echte, direkt von der Primärquelle geladene Datensätze (USGS-Erdbeben
  M≥6.0 seit 2000, NOAA-Globaltemperaturanomalie 1880–2025, OWID/JHU-Covid-
  Weltzeitreihe) liegen seit 2026-09-20 mit vollständiger Provenienz vor
  (URL, Abrufzeitpunkt, sha256) — siehe
  [docs/real_data_provenance.md](docs/real_data_provenance.md) und
  `data/real_data_manifest.json`. Alle drei haben inzwischen einen
  vollständigen Validierungspilot: **Covid**
  ([docs/covid_pilot.md](docs/covid_pilot.md), M6b, plus zwei
  Folgeuntersuchungen B/C) — Exponentialwachstum überspannt einen echten
  Regimewechsel, `model_beats_baseline=False`; **NOAA-Temperatur**
  ([docs/noaa_temp_pilot.md](docs/noaa_temp_pilot.md), M6c) — derselbe
  Fehlertyp auf einer völlig anderen Domäne, `model_beats_baseline=False`;
  **USGS-Erdbeben** ([docs/earthquake_pilot.md](docs/earthquake_pilot.md),
  M6d) — konstante Rate vs. Persistenz, `model_beats_baseline=False`
  (gewöhnliche Stichprobenvarianz, kein Regimewechsel). Keines der
  Ergebnisse wurde nachträglich angepasst.
- Eine externe Review (Astra, 2026-09-21,
  `prompts/Answers/nicht_stationäre_Treiber/`) reproduzierte alle drei
  Piloten unabhängig, fand zwei Fehler in `docs/earthquake_pilot.md`
  (korrigiert) und schlug ein Folgeprogramm vor — siehe
  [NONSTATIONARY_ROADMAP.md](NONSTATIONARY_ROADMAP.md). Paket 1
  (gemeinsame rollierende Auswertung, `validation/rolling_origin.py`) und
  Paket 2 (COVID-Länderdekomposition China vs. Rest der Welt,
  `validation/covid_country_decomposition.py` — bestätigt Astras
  Mischungsidentität direkt an echten Daten) und Paket 3
  (Treiber-abhängige Dynamik-Schnittstelle, `dynamics/rate_dependent.py`
  — eingefrorene Stabilität getrennt von echter Trajektorienintegration,
  reproduziert Astras rateninduziertes Kipp-Kontrollbeispiel Ziffer für
  Ziffer) und Paket 4 (Raten-/Viabilitäts-Kontrollfälle: χ-Diagnose sagt
  die RICHTUNG des Kippverhaltens aus Paket 3 über den gesamten getesteten
  Bereich korrekt voraus — die anfangs genannte präzise Schwelle χ≥0,5 war
  dagegen nur grob rastergebunden und wurde später auf den tatsächlichen
  Übergang zwischen r=0,7 und r=0,8 korrigiert (siehe unten, Zweitprüfung);
  ein neuer Puffer-Lastspitzenfall, `viability/rate_dependent_buffer.py`,
  zeigt das Spiegelbild-Ergebnis — schnellere Störungen sind hier sicherer,
  nicht gefährlicher) sind umgesetzt und gegen die Review-Zahlen
  abgeglichen. Paket 5 (je Domäne ein mechanistisches Modell:
  COVID-Renewal `validation/covid_renewal.py`, Energiebilanz-Klima
  `dynamics/energy_balance.py` mit echten Mauna-Loa-CO2-Daten, ETAS-
  Erdbeben `dynamics/etas.py` — erklärt die in Paket 4/`earthquake_pilot.md`
  gefundene Überdispersion mechanistisch, AIC-Lücke ≈1304 gegen die
  Poisson-Nullhypothese) ist ebenfalls umgesetzt, womit alle 5 Pakete aus
  [NONSTATIONARY_ROADMAP.md](NONSTATIONARY_ROADMAP.md) abgeschlossen sind.
- Eine Zweitprüfung dieses Ergebnisses (Astra, 2026-09-21,
  `SCF_Review_f8e249f.md`) fand einen echten Optimierer-Fehler
  (Energiebilanz-Fit konvergierte zu einem schlechten lokalen Optimum,
  RMSE 0,154 statt erreichbarer 0,090) und mehrere Überdehnungen
  (fehlender `-u̇`-Term, χ-Schwellenpräzision, Puffer-Richtungsabhängigkeit,
  ETAS-Verzweigungsraten-Fragilität) — alle unabhängig nachvollzogen und
  behoben (Commit `20efc63`). Die verbleibenden, größeren Vorschläge
  (belastbare Schätzung, gemeinsame Prognoseprüfung, Strukturbrücken,
  Beobachtungsmodelle) sind als eigene Roadmap aufgenommen:
  [MECHANISTIC_VALIDATION_ROADMAP.md](MECHANISTIC_VALIDATION_ROADMAP.md).
  Paket 1 (Profile-Likelihood-Anschluss: `energy_balance.py`s C_s/C_d/alpha
  sind auf einem ±50%-Raster um den Fit weit offen — die früher
  behauptete "praktisch nicht identifizierbar, rigoros bestätigt" war
  selbst eine Überdehnung und wurde in
  [Paket 9](MECHANISTIC_VALIDATION_ROADMAP.md) korrigiert: korrekt ist
  "auf diesem Fenster schwach eingeschränkt, nicht in absolutem Sinn als
  unidentifizierbar erwiesen" — siehe
  [docs/energy_balance.md](docs/energy_balance.md)), Paket 2 (gemeinsame Rolling-Origin-Prognoseprüfung: das
  Energiebilanzmodell schlägt jede statistische Baseline an jedem
  Vorlaufjahr; die COVID-Renewal-Projektion schlägt beide Baselines; ETAS
  schlägt die Persistenz-Baseline NICHT — ehrlich berichtet) und Paket 3
  (echte Vorhersageintervalle + Scoring-Regeln: Punktgenauigkeit ≠
  Intervallqualität — das Energiebilanzmodell gewinnt Paket 2s RMSE, hat
  aber den SCHLECHTESTEN Intervall-Score aller vier Prädiktoren),
  Paket 4 (zwei neue Strukturbrücken B7/B8 in
  [docs/structural_relations.md](docs/structural_relations.md): Energiebilanz
  und Puffer sind beide Faltungs-/Impulsantwort-Systeme; COVID-Renewals
  Reproduktionszahl R und ETAS' Verzweigungsrate sind bei konstantem R
  exakt dieselbe Größe nach Hawkes & Oakes 1974) und Paket 5
  (Beobachtungsmodelle: rohe COVID-Tageszahlen sind deutlich
  überdispers gegenüber Poisson, getestet statt angenommen, Faktor ~100
  im Log-Score; Deutschland/USA scheitern ehrlich an Pilot As exaktem
  2020-Fenster wegen echter Null-Tage, dasselbe Verfahren gewinnt aber
  auf einem neuen 2021-Omikron-Fenster; reales Gesamtforcing aus den
  "Indicators of Global Climate Change 2025" verbessert die Energiebilanz
  spürbar gegenüber CO2-only) sind umgesetzt.
- Die G-Serie (`GALAXY_DYNAMICS_ROADMAP.md`, G0–G7 plus zwei
  Review-Fix-Runden) und die H-Serie (`EPISTEMIC_AUDIT_ROADMAP.md`, H0–H7
  plus Followup-Review-Fix) sind nach demselben Muster abgeschlossen:
  Plan → unabhängige Hand-Nachrechnung der Kontrollfälle → Paket-für-Paket-
  Implementierung mit eigenem `verify_*.py` → externe Review → unabhängige
  Reproduktion jedes Befunds → Fix mit gezieltem Regressionstest → volle
  Suite + Linkprüfung vor jedem Commit. Siehe die jeweiligen Roadmap-
  Dateien für die vollständigen Ergebnistabellen.

---

## Revision 3.2 (historisch, 16. September 2026 — vor dem installierbaren Paket)

**Methodischer Entwurf mit Literaturanschlüssen, prüfbaren Modellrechnungen und optionalen F08/F09-Ergänzungen. Umbenannt von "CREP–UTAC–AFET" am 16. September 2026 — siehe [GLOSSARY.md](GLOSSARY.md) für die vollständige Begriffszuordnung und Begründung.**

Johanns Ausgangsabsicht bleibt die Grundlage: **Observation** (vormals CREP) beschreibt Information, **Dynamics** (vormals UTAC) Systeme und deren Dynamik, **Coupling** (vormals AFET) die Kopplung mit einer ausdrücklich ausgewiesenen thermodynamischen Spezialisierung (**Thermodynamics**). Die zentrale Beziehung zwischen Beschreibungsebenen heißt **Correspondence** (vormals „Selbstähnlichkeit" als Gesamtanspruch) — bewusst schwächer als „Äquivalenz" oder „Identität", weil eine Korrespondenz exakt, näherungsweise, projektiv, kontextabhängig oder empirisch widerlegt sein kann. Die Revision ersetzte bereits die unzutreffenden Größenidentitäten des Entwurfs vom 15. September durch definierte Schnittstellen und bedingte Modellbeziehungen; die neue Namensgebung macht diesen Verzicht auf Universalitätsanspruch jetzt auch im Namen sichtbar statt nur im Text.

Der gemeinsame Rahmen beschreibt, **was an einem System gemessen wird, wie es sich entwickelt und wie andere Systeme darauf wirken**. Seine Leitidee ist die von Johann am 16. September nochmals klargestellte **Selbstähnlichkeit**: wiederkehrende Strukturen mit unterschiedlichen Größen, Parametern und Skalen. Die zuvor eingeschlichenen Gleichsetzungen waren Fehler der Ausarbeitung, nicht die beabsichtigte Ausgangsthese.

Eine strukturelle Analogie ist ein Ausgangspunkt. Mathematische Selbstähnlichkeit benötigt eine angegebene Transformation und einen Geltungsbereich; empirisch geprüfte Selbstähnlichkeit zusätzlich Daten und einen quantifizierten Vergleich. Diese Ebenen werden im Formalismus ausdrücklich auseinandergehalten.

### Einstieg (Revision-3.2-Dokumente)

| Datei | Inhalt |
|---|---|
| [GLOSSARY.md](GLOSSARY.md) | Neues Vokabular (Observation/Dynamics/Coupling/Correspondence), Legacy-Mapping, Begründung der Umbenennung |
| [ARCHITECTURE_ROADMAP.md](ARCHITECTURE_ROADMAP.md) | Grobe, noch nicht beauftragte Roadmap für eine echte Softwarebibliothek (Teil 2) |
| [FORMALISM.md](FORMALISM.md) | Zusammenhängende Übersicht und verbindliche Notation |
| [LITERATURE_CONNECTIONS.md](LITERATURE_CONNECTIONS.md) | Geprüfte Literaturanschlüsse, Voraussetzungen und Übernahmeentscheidungen |
| [emergence_and_closure.md](emergence_and_closure.md) | Rekonstruktion, Makro-Geschlossenheit, EI und konkreter Individuations-Prüfvertrag |
| [information_layer_crep.md](information_layer_crep.md) | S/K/R/V als Rollen mit expliziten Messverfahren |
| [system_layer_utac.md](system_layer_utac.md) | Zustand, Antwort, Erholung, Becken und korrigierte kubische Dynamik |
| [coupling_layer_afet.md](coupling_layer_afet.md) | Datenfluss, dynamische Kopplung und thermodynamischer Sonderfall |
| [worked_example_heat_exchange.md](worked_example_heat_exchange.md) | Vollständig gerechnetes positives Kopplungsbeispiel |
| [worked_example_reconstruction.md](worked_example_reconstruction.md) | Verzögerungskoordinaten, Abtastungsgegenfall und Projektionsgedächtnis |
| [worked_example_causal_emergence.md](worked_example_causal_emergence.md) | EI, Interventionsensembles, Lumpability und zwei SVD-/Reversibilitätsgegenfälle |
| [worked_example_viability.md](worked_example_viability.md) | Dauerhafte Belastbarkeit trotz gleicher Erholungsrate |
| [sheaf_contextuality.md](sheaf_contextuality.md) | Optionales Modul (F08): Prüfung globaler Darstellbarkeit deklarierter lokaler Wahrscheinlichkeitsmodelle (Contextual Fraction), neben VB1 |
| [pid_redundancy_bottleneck.md](pid_redundancy_bottleneck.md) | Optionales Modul (F09): PID-Zerlegung (Williams–Beer/Kolchinsky-RB) einer deklarierten Quellen-Ziel-Verteilung, Mikro→Makro; `EI_q` wird separat berichtet |
| [DESIGN.md](DESIGN.md) | Entscheidungen und zurückgezogene Schlussfolgerungen |
| [ROADMAP.md](ROADMAP.md) | Erreichter Paketstand und nächste fachliche Prüfungen |
| [FOLLOWUP_TICKETS.md](FOLLOWUP_TICKETS.md) | Offene Codefragen und bisherige Reparaturen |
| [REVISION_2026-09-16.md](REVISION_2026-09-16.md) | Historischer Änderungsbericht der Revision 2 |
| [REVISION_3_2026-09-16.md](REVISION_3_2026-09-16.md) | Aktuelle Änderungen, Herkunft und Anwendungshinweise |
| [VERIFICATION.md](VERIFICATION.md) | Reproduktion und Aussagekraft der Prüfungen |
| [TRANSFORMATION_VERIFICATION.md](TRANSFORMATION_VERIFICATION.md) | Reproduktion der 18 Revision-3.2-Prüfungen (Transformation, Viabilität) |
| [context_transformations.md](context_transformations.md) | Kontext, Zugehörigkeiten, Verträglichkeitsbedingungen (Revision 3.2) |

Die acht ursprünglichen Paketbeispiele bleiben auf dem Reparaturstand der Revision 2. Hinzu kommen das erweiterte Wärmebeispiel und drei neue Methodenbeispiele. Die unveränderten ursprünglichen Dokumente stehen unter `archive/2026-09-15/`; der hier vorliegende aktuelle Bestand der Revision 2 unter `archive/2026-09-16-revision-2/`.

### Was die Revision festlegt

- Antwortsteilheit `beta_response` und lokale Erholungsrate `S_rec` sind getrennte Größen.
- Informationsnutzung `eta_info`, dynamischer Einfluss `A_ij` und thermodynamischer Koeffizient `L_ij` erhalten getrennte Definitionen und Einheiten.
- Die korrigierte kubische Modellfamilie lautet `tau * dx/dt = -x^3 + a*x + b`, mit dimensionslosem Zustand x und `tau>0`.
- `a = -tau*S_rec(0)` gilt nur am Gleichgewicht x=0 des symmetrischen Modells b=0. Es ist eine Modellbeziehung, keine allgemeine Parameterelimination.
- Beckenwahrscheinlichkeit, Abstand zur Grenze und lokale Rate werden gesondert gemessen.
- Positive Excess-Stabilität ist eine zu testende Eigenschaft einer gewählten Komposition, kein bereits bewiesenes allgemeines Kriterium für „System-Sein".
- Etablierte Sätze, eigene Modellableitungen, synthetische Prüfungen und reale Messungen werden getrennt gekennzeichnet.
- Takens begründet eine generische Rekonstruktionsgarantie; eine notwendige universelle Dimensionsschwelle folgt daraus nicht.
- Eine eigenständige Makrodynamik erhält eine konkrete Geschlossenheitsprüfung. EI, Synergie und SVD-Diagnose sind verschiedene Zielgrößen.
- GENERIC ist eine optionale thermodynamische Spezialisierung mit nachzuweisenden Energie-/Entropiebedingungen.
- Viabilität ergänzt die Resilienzbeschreibung um zulässige Bereiche, Eingriffe, Belastungen und Zeiträume.
- Zwei optionale Module (F08/F09, extern geprüft von Aeon, Checksummen und Skriptläufe von Claude nachgerechnet) stehen neben dem Kern, ohne ihn zu verändern: Sheaf-Kontextualität für Verträglichkeitsbedingung 1 und PID/Redundancy Bottleneck für `EI_q`.

Die Revision bearbeitet die bereitgestellten Dokumente und neue Verifikationsbeispiele. Die erreichten Korrekturen in den veröffentlichten Einzelpaketen bleiben als Fortschritt dokumentiert.

### Ausführen (Revision-3.2-Basisprüfungen)

```bash
python -m pip install -r verification/requirements.txt
python verification/verify_extensions.py
python verification/verify_formalism.py
python verification/verify_transformations.py
python -m pip install -r verification/requirements_sheaf_pid.txt
python verification/verify_sheaf_contextuality.py
python verification/verify_pid_rb.py
```

Die Basissuite benötigt nur die Python-Standardbibliothek. Die Erweiterungen nutzen NumPy; die beiden optionalen F08/F09-Module zusätzlich SciPy (LP-Löser). Voraussetzungen, Laufberichte und Aussagekraft stehen in [VERIFICATION.md](VERIFICATION.md) und [TRANSFORMATION_VERIFICATION.md](TRANSFORMATION_VERIFICATION.md). Die Modellprüfungen ersetzen keine empirische Validierung und keine Produktionspaket-Testsuite.

### Ergänzend einspielen

Nicht im Paket enthaltene lokale Dateien bleiben bestehen. Der von Johann bereits archivierte ältere Verifikationsordner wird nicht rekonstruiert oder gelöscht. `apply_manifest.json` benennt aktuelle Änderungen mit Ausgangs- und Zielprüfsummen; das vollständige `manifest.json` umfasst auch die beigefügten Archive. Details: [Übergabe](REVISION_3_2026-09-16.md).

### Status (Revision 3.2)

Die Drei-Schichten-Architektur ist ein expliziter Forschungs- und Beschreibungsrahmen. Die aufgeführten Standardmodelle sind unter ihren Voraussetzungen mathematisch prüfbar. Die universelle Anwendbarkeit, ein universeller Individuationsschwellenwert und universelle Zahlenwerte wie 0,84 oder 1/16 sind dadurch nicht nachgewiesen.
