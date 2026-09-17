# Architektur-Roadmap — Scoped Correspondence Formalism (Teil 2, noch nicht beauftragt)

Stand: 16. September 2026. Dies ist eine **grobe Sicherungskopie** des vollständigen Astra-Vorschlags in [prompts/Answers/ChatGPTAstra2.md](prompts/Answers/ChatGPTAstra2.md), damit bei einer späteren Entscheidung nichts verloren geht. **Nichts hier ist beauftragt oder begonnen.** Teil 1 (Umbenennung, Glossar, Repo) ist abgeschlossen — siehe [GLOSSARY.md](GLOSSARY.md). Diese Datei ist die Diskussionsgrundlage für die nächste Entscheidung: ob, wie und von wem Teil 2 angegangen wird.

## Worum es geht

Aktuell ist dieses Repository reine Dokumentation plus eigenständige Verify-Skripte (kein installierbares Python-Paket, kein `src/`-Baum). Der Astra-Vorschlag ist ein vollständiger Plan, daraus eine echte Softwarebibliothek zu machen: typisierte Contracts statt Prosa-Formeln, eine `Correspondence`-Kernklasse, getrennte Verification-/Validation-Pipelines, SemVer, und ausgewählte maschinengeprüfte Lean-Lemmata. Das ist ein eigenständiges Projekt, keine Fortsetzung "nebenbei".

**Zeit-/Aufwandsschätzung aus dem Vorschlag** (Annahme: 2–4 Entwickler:innen, mindestens einer mit mathematisch-wissenschaftlichem Schwerpunkt): **16–20 Wochen** bis zu einer ersten stabilen Major-Version.

## Verbindung zum Architektur-Planungsprojekt (unabhängig entstanden, gleicher Zielpunkt)

Johanns Beobachtung (16.9.): `D:\mandala\Architektur--Planungsprojekt\` verfolgt unabhängig denselben Zielpunkt — den Übergang von Unified-Mandala (explorativem Labor) zu einer kanonisierten Referenzarchitektur ("Genesis Core / UTAC Core"), dort aber top-down über einen strengen Planungsprozess statt bottom-up aus einer Formalismus-Korrekturrunde. Beide sollen **nicht automatisch verschmolzen werden** — der Formalismus bleibt hier führend, das Planungsprojekt bekommt einen angepassten Vorschlag, nicht umgekehrt.

**Wie das Planungsprojekt tatsächlich funktioniert** (aus `README.md`/`AGENTS.md`/`ENTRY.yaml` dort):

- Jede Wissenseinheit liegt als **Trylayer-Tripel** vor: `<slug>.yaml` (Metadaten), `<slug>.ai.json` (maschinenlesbarer Volltext), `<slug>.md` (Prosa für Menschen) — Schema in `contracts/trylayer.schema.yaml`.
- Externe Systeme reichen keine rohen Trylayer-Dateien ein, sondern ein einfaches Markdown mit Kopf (`quelle_system`, `datum`) und den Abschnitten `## Problem`, `## Vorschlag`, `## Erwartetes Ergebnis`, `## Alternativen betrachtet` — eine KI-Schnittstelle (hier: Claude) baut daraus das Trylayer-Tripel.
- Ordner nach Reifegrad: `01_Ideen/` (roh, `status: idea`/`draft`) → `02_Plaene/` → `03_Architektur/` (braucht ADR) → `04_Programme/` (braucht ADR + Blindtest). `epistemic_status` muss ehrlich sein — die meisten neuen Vorschläge sind `hypothesis`, nicht `validated`.
- **Genesis-Blindtest** (Regel 6) vor jedem Vorschlag für `architektur`/`programm`: Würde eine Person ganz ohne GenesisAeon-Kontext dieses Modul in einem völlig anderen Kontext installieren wollen und in 5 Minuten ein sinnvolles Ergebnis sehen? Wenn nein: gehört nach `01_Ideen/`, nicht höher.
- `status: accepted`/`core`/`kategorie: adr` bleibt Johanns/einer klar begründeten KI-Entscheidung vorbehalten (Regel 12) — eine KI darf nach `adr/adr-003` fallweise selbst hochstufen, aber mit Begründung im Trylayer-Eintrag UND in der Commit-Message, damit alles per Diff nachvollzieh- und revertierbar bleibt.

**Konkreter, angepasster Vorschlag für den Formalismus (nicht umgekehrt):**

1. **Zuerst nur die Methodik einreichen, nicht die volle Softwarebibliothek.** Ein `01_Ideen/claude/`-Trylayer-Tripel, das die Kernlektion des Scoped Correspondence Formalism zusammenfasst — Rollen statt Akronym-Identität, Scope als First-Class Concept, Verification-vs-Validation-Trennung, `VAL-SPLIT`-artige Disziplin gegen Kalibrierung-als-Bestätigung — als eigenständiger, GenesisAeon-unabhängiger Denkbaustein. Das würde den Genesis-Blindtest ehrlich bestehen: die Methodik selbst ist domänenneutral, unabhängig von CREP/UTAC/AFET-Historie verständlich.
2. **F08/F09 (Contextuality, Information Decomposition) und die zehn Astra-Module bleiben vorerst in `01_Ideen/`, nicht `03_Architektur/`.** Sie sind noch nicht empirisch validiert (siehe `VERIFICATION.md`: 66 grüne Prüfungen sind synthetisch, keine reale Datenprüfung) — `epistemic_status: hypothesis`, ehrlich so gekennzeichnet, keine Selbsthochstufung auf `core`.
3. **Die Formalismus-Inhalte selbst (`FORMALISM.md` etc.) wandern NICHT eins-zu-eins in Trylayer-Dateien.** Das Planungsprojekt bekommt eine verdichtete Zusammenfassung plus Link zurück auf dieses Repo als Quelle der Wahrheit — keine Duplizierung der 66 Prüfungen oder der Revisionshistorie dort.
4. **Reihenfolge:** Diese Einreichung ist unabhängig von und deutlich billiger als die 16-20-Wochen-Softwarebibliothek oben — kann parallel oder vorher passieren, ohne auf eine Entscheidung über Teil 2 zu warten.

**Noch nicht ausgeführt** — nur in dieser Roadmap vorgemerkt. Nächster Schritt bei Freigabe: Rohformat-Markdown nach `AGENTS.md`-Vorlage entwerfen, Johann zur Durchsicht vorlegen, dann als Trylayer-Tripel unter `01_Ideen/claude/` im Planungsprojekt anlegen und `python scripts/validate_trylayer.py` dort laufen lassen.

## Grobe Meilensteine (aus Astras Vorschlag, ungekürzt in der Quelldatei)

| Meilenstein | Zeitraum | Inhalt | Exit-Kriterium |
|---|---|---|---|
| **Naming & Contract Freeze** | Woche 1–2 | Glossar ✅, Test-ID-Namespace ✅ (`verification/test_id_namespace.md`), `Correspondence`-Kern ✅ (`src/scoped_correspondence/correspondence/`, 5/5 verifiziert gegen Legacy-Fälle e11/T01–T04, gemergt 2026-09-16 via `prompts/07_teil2_correspondence_core_for_aeon.md`) | eindeutige öffentliche Terminologie; kein CREP/UTAC/AFET in neuen Kern-APIs — **erledigt** |
| **Core Extraction** | Woche 3–5 | `observation` ✅, `dynamics` ✅, `coupling` ✅, `correspondence` ✅ (alle vier gemergt 2026-09-16, `src/scoped_correspondence/`), Legacy-Adapter ✅ (`legacy/adapters.py`) | 13/13 neue Prüfungen exakt gegen Legacy-Werte verifiziert (p01-p03, p06, e11, T01-T04), 66 bestehende Prüfungen weiter grün — **erledigt** |
| **Closure & Viability** | Woche 6–8 | `closure` ✅, `viability` ✅, `membership` ✅ (alle gemergt 2026-09-16, Membership als eigener Folgeauftrag `prompts/10_teil2_membership_for_aeon.md`) | 11/11 neue Prüfungen exakt reproduziert (e01/e03/e04/e05/e06/t07/t15 für Closure; t05/t07/t09/t10 für Viability) plus 4/4 frische Membership-Prüfungen (keine Legacy-Fälle vorhanden, siehe F19) + t10-Kreuzprobe, alle 66 bereits bestehenden Prüfungen weiter grün — **erledigt** |
| **Uncertainty & Validation** | Woche 9–12 | `identifiability` ✅ (gemergt 2026-09-17); Domänen-Survey ✅ (F21, Johann wählte `cygnus-jet-utac`/`jet_pa_deg`); `validation` ✅ — erster echter Datenpilot (gemergt 2026-09-17 via `prompts/13_teil2_m6_cygnus_pilot_for_aeon.md`) | 6/6 Identifiability-Prüfungen + 6/6 Pilot-Prüfungen, `model_rmse_holdout=3,071` vs. `baseline_rmse_holdout=3,705` (Persistenz), `model_beats_baseline=True` — schwach identifiziert (faktisch linearer Trend), ehrlich berichtet; reproduzierbarer `ValidationReport` erzeugt — **erledigt (eine Domäne, ein Makro; Domänenvergleich/Universalität ausdrücklich nicht Teil davon)** |
| **Optional Modules Hardening** | Woche 13–14 | `contextuality` ✅ (F08 + F13-Scope-Guard), `information_decomposition` ✅ (F09 + F12 TWO_BIT_COPY, gemergt 2026-09-17 via `prompts/14_teil2_m7_optional_modules_hardening_for_aeon.md`) | 7/7 + 8/8 neue Prüfungen exakt gegen `verify_sheaf_contextuality_results.json`/`verify_pid_rb_results.json` reproduziert; F13-Guard live getestet (löst bei fehlendem/`False`-Argument aus); TWO_BIT_COPY von Hand hergeleitet (Red=1 vs. RB(0)=0) — **erledigt** |
| **Thermo & Memory** | Woche 15–17 | `thermo` ✅ (e13 GENERIC-Wärmebeispiel, e10 Drei-Zyklus-Gegenfall, neue `project_generic_structure`-Projektionsprüfung, gemergt 2026-09-17 via `prompts/15_teil2_m8_thermo_memory_for_aeon.md`); Memory/Delay Closure bereits durch M3s `closure.memory_solution`/`projected_memory_rhs` abgedeckt | 6/6 neue Prüfungen exakt gegen `extension_results.json` reproduziert, drei Zahlen von Hand bestätigt (Entropieproduktion, Summen-/Einzel-Projektion) — **erledigt** |
| **Formal Hooks & Stable Release** | Woche 18–20 | ausgewählte Lean-Lemmata (Komposition, Residuenabschätzung, sichere Eingriffsübertragung aus `context_transformations.md` §8), Dokumentationsaudit, Migration Guide, `4.0.0` | reproduzierbare Release-Suite + eingefrorene öffentliche API |

**Wichtigste Priorität laut Vorschlag:** Nicht F08/F09 oder neue Theorie sind der Engpass, sondern die **Empirical Validation Pipeline** (Woche 9–12) — die bestehende Theorie an echte Daten anschließen. Das deckt sich mit der bisherigen Roadmap dieses Repos ([ROADMAP.md](ROADMAP.md)).

Alle acht ursprünglichen Meilensteine (Naming & Contract Freeze bis Thermo & Memory) sind inzwischen erledigt. **Formal Hooks & Stable Release** bleibt der letzte ursprüngliche Meilenstein. Parallel dazu läuft seit M9 eine zweite Linie — "Ast verbreitern": natürliche, einzeln zitierfähige mathematische Erweiterungen bestehender Bausteine, aus zwei unabhängig verifizierten DeepResearch-Antworten. Vollständige Liste mit Quellen und Status: [EXTENSIONS_ROADMAP.md](EXTENSIONS_ROADMAP.md).

## Zehn vorgeschlagene Module (Kurzfassung — volle API-Skizzen in der Quelldatei)

| Modul | Aufgabe | Priorität | Aufwand |
|---|---|---|---|
| Correspondence Core | Transformation + Scope + Zeitabbildung + Residuum als First-Class Contract | hoch | M |
| Closure & Reconstruction | Autonome Makrodynamik prüfen, Lift/Restrict, Markov-Lumpability | hoch | M–L |
| Viability & Safe Control | Viability Kernels, ausführbare Eingriffe (baut auf `context_transformations.md` §8 auf) | hoch | L |
| Membership & Shared Resources | Überlappende Systemzugehörigkeit, gemeinsame Ressourcen | mittel–hoch | M |
| Uncertainty & Identifiability | Messfehler, Parameterunsicherheit, Identifizierbarkeit | hoch | L |
| Memory & Non-Markovian Closure | Delay States/Memory Kernel bei nicht-Markovscher Projektion | mittel | L |
| Contextuality | F08 produktisiert | mittel | S–M |
| Information Decomposition | F09 produktisiert | mittel | M |
| Thermodynamics / GENERIC | Typisierte thermodynamische Spezialisierung | mittel–hoch | M–L |
| Formal Verification Hooks | Ausgewählte Lean-Lemmata, kein Vollbeweis-Zwang | mittel | L |
| **Empirical Validation Pipeline** | Data Provenance, Calibration/Holdout, Baselines, Unsicherheit | **sehr hoch** | L |

## Kernprinzip, das erhalten bleiben muss

`VAL-SPLIT-*`-artige Tests, die mechanisch erzwingen, dass eine Transformation/Skalierung/Modellklasse, die anhand von Testdaten gewählt wurde, nicht anschließend als unabhängige empirische Bestätigung gilt. Das ist die maschinelle Version genau der Disziplin, die diese ganze Revisionsrunde erst nötig gemacht hat (Kalibrierung mit Bestätigung verwechseln). Jede Testausgabe sollte einen Typ tragen (`mathematical` / `numerical` / `counterexample` / `contract` bei Verification; `synthetic` / `empirical_in_sample` / `empirical_holdout` / `external_replication` bei Validation), damit ein synthetischer Rechentest nie versehentlich als empirischer Nachweis erscheinen kann.

## Migrationsprinzip für bestehende Tests

Keine Neunummerierung. Die 19+16+18+6+7=66 bestehenden Prüfungen bekommen eine Namespace-/Alias-Schicht (`VER-CORE-*`, `VER-REC-*`, `VER-CLS-*`, `VER-COR-T01…T18`, `VER-CTX-*`, `VER-PID-*` usw.), damit ihre wissenschaftliche Provenienz erhalten bleibt statt verloren zu gehen.

## Nächster Schritt

Keine Ausführung ohne separate Entscheidung. Offene Fragen für dieses Gespräch:

1. Wird das überhaupt verfolgt, oder bleibt das Repo bei "Dokumentation + Verify-Skripte"?
2. Falls ja: selbst umsetzen, an Aeon/GrokBot delegieren, oder Team-Aufbau wie in der Schätzung angenommen?
3. Soll die Methodik-Einreichung ins `Architektur--Planungsprojekt` (siehe oben) jetzt vorbereitet werden, unabhängig von einer Entscheidung über Teil 2 — oder erst nach mehr Erfahrung mit dem neuen Vokabular?
4. Falls Teil 2 verfolgt wird: in welcher Reihenfolge — wie oben vorgeschlagen (Correspondence Core zuerst), oder anders priorisiert?
