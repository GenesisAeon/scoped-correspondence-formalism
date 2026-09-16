# Architektur-Roadmap — Scoped Correspondence Formalism (Teil 2, noch nicht beauftragt)

Stand: 16. September 2026. Dies ist eine **grobe Sicherungskopie** des vollständigen Astra-Vorschlags in [prompts/Answers/ChatGPTAstra2.md](prompts/Answers/ChatGPTAstra2.md), damit bei einer späteren Entscheidung nichts verloren geht. **Nichts hier ist beauftragt oder begonnen.** Teil 1 (Umbenennung, Glossar, Repo) ist abgeschlossen — siehe [GLOSSARY.md](GLOSSARY.md). Diese Datei ist die Diskussionsgrundlage für die nächste Entscheidung: ob, wie und von wem Teil 2 angegangen wird.

## Worum es geht

Aktuell ist dieses Repository reine Dokumentation plus eigenständige Verify-Skripte (kein installierbares Python-Paket, kein `src/`-Baum). Der Astra-Vorschlag ist ein vollständiger Plan, daraus eine echte Softwarebibliothek zu machen: typisierte Contracts statt Prosa-Formeln, eine `Correspondence`-Kernklasse, getrennte Verification-/Validation-Pipelines, SemVer, und ausgewählte maschinengeprüfte Lean-Lemmata. Das ist ein eigenständiges Projekt, keine Fortsetzung "nebenbei".

**Zeit-/Aufwandsschätzung aus dem Vorschlag** (Annahme: 2–4 Entwickler:innen, mindestens einer mit mathematisch-wissenschaftlichem Schwerpunkt): **16–20 Wochen** bis zu einer ersten stabilen Major-Version.

## Grobe Meilensteine (aus Astras Vorschlag, ungekürzt in der Quelldatei)

| Meilenstein | Zeitraum | Inhalt | Exit-Kriterium |
|---|---|---|---|
| **Naming & Contract Freeze** | Woche 1–2 | Glossar (✅ bereits erledigt als Teil 1), Kerninterfaces, Test-ID-Schema, ADR zur Migration | eindeutige öffentliche Terminologie; kein CREP/UTAC/AFET in neuen Kern-APIs |
| **Core Extraction** | Woche 3–5 | `observation`, `dynamics`, `coupling`, `correspondence` als echte Module; Legacy-Adapter; bestehende Formeln portieren | 19 Basis- + relevante Transformations-Tests laufen gegen neuen Kern |
| **Closure & Viability** | Woche 6–8 | Closure/Reconstruction, Lift/Restrict, Viability, Membership/Shared Resources | bestehende Rekonstruktions-, Closure-, Viability-Fälle portiert |
| **Uncertainty & Validation** | Woche 9–12 | Messmodell, Unsicherheit, Identifizierbarkeit, Dataset Manifest, Train/Holdout, Baselines; **ein echter Pilot mit realen Daten** | erste reale Studie erzeugt reproduzierbaren `ValidationReport` |
| **Optional Modules Hardening** | Woche 13–14 | F08/F09 neu kapseln; TWO_BIT_COPY als Regressionstest; Scope Guards; API-Entkopplung Algorithmus/Konzept | F08/F09 grün unter neuer API; bekannte Pathologien als Regressionstests |
| **Thermo & Memory** | Woche 15–17 | GENERIC-Contracts, Projektionsprüfung, Memory/Delay Closure | bestehende GENERIC-/Gedächtnistests plus neue Projektionschecks |
| **Formal Hooks & Stable Release** | Woche 18–20 | ausgewählte Lean-Lemmata (Komposition, Residuenabschätzung, sichere Eingriffsübertragung aus `context_transformations.md` §8), Dokumentationsaudit, Migration Guide, `4.0.0` | reproduzierbare Release-Suite + eingefrorene öffentliche API |

**Wichtigste Priorität laut Vorschlag:** Nicht F08/F09 oder neue Theorie sind der Engpass, sondern die **Empirical Validation Pipeline** (Woche 9–12) — die bestehende Theorie an echte Daten anschließen. Das deckt sich mit der bisherigen Roadmap dieses Repos ([ROADMAP.md](ROADMAP.md)).

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
3. Passt das in ein bereits geplantes Monorepo/Architektur-Repo (siehe Johanns Hinweis vom 16.9.) — falls ja, sollte diese Datei dorthin verweisen statt eigenständig zu bleiben?
4. Falls verfolgt: in welcher Reihenfolge — wie oben vorgeschlagen (Correspondence Core zuerst), oder anders priorisiert?
