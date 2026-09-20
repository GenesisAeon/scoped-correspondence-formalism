# Scoped Correspondence Formalism

[![License](https://img.shields.io/badge/code-GPLv3--or--later-blue)](LICENSE)
[![Docs License](https://img.shields.io/badge/docs-CC%20BY%204.0-lightgrey)](LICENSE-DOCS)

## Aktueller Stand (2026-09-20)

Seit dem 16. September 2026 ist dieses Repository ein **installierbares
Python-Paket** (`scoped-correspondence`, aktuell `0.41.0a1`, Milestones
M1-M41 als Review-Paket) unter `src/scoped_correspondence/` — nicht mehr
nur Dokumentation und eigenständige Skripte. Der untenstehende
"Revision 3.2"-Abschnitt beschreibt den Stand VOR dieser Umstellung und ist
als historischer Kontext erhalten (siehe
[REVISION_3_2026-09-16.md](REVISION_3_2026-09-16.md)); die aktuelle
Modul-/Paketstruktur steht hier.

### Installation

```bash
pip install -e .
python -m pip install -r verification/requirements.txt
```

### Kurzbeispiel

```python
from scoped_correspondence.dynamics.core import fixed_points

# Kubische Normalform tau*dx/dt = -x^3 + a*x + b bei b=0, a=3:
# Fixpunkte sind 0 und +-sqrt(a).
print(fixed_points(3.0, 0.0))
# [-1.7320508075688774, ~0.0, 1.7320508075688774]
```

Ein zweites, ausführlicheres Beispiel (`Correspondence`-Vertrag mit
Residuum, Scope und optionaler zustandsabhängiger Zeitabbildung) steht in
[docs/correspondence_core.md](docs/correspondence_core.md).

### Modulübersicht (`src/scoped_correspondence/`)

| Paket | Enthält |
|---|---|
| `correspondence/` | Kernvertrag: `Correspondence`, Konjugationsresiduum, Approximationszertifikate |
| `observation/` | Kanalkapazität, Informationsretention, Arimoto-Blahut, Directed Information |
| `dynamics/` | Kubische Normalform, Kontraktion, Landau/Ising, GSPT, Floquet, Panarchy, Early-Warning |
| `coupling/` | Kopplungslagen, Casimir/Dirac-Komposition, Dissipativität, GENERIC↔Navier-Stokes, generalisierte Synchronisation |
| `closure/` | `PC=CQ`-Makroschließung, Generator-Lumpability, Fehlerschranken, Chapman-Enskog |
| `viability/` | Viability Kernels, Nagumo-Tangentialkegel, Control Barrier Functions |
| `membership/` | Zugehörigkeitsmatrizen, Formal Concept Analysis |
| `identifiability/` | Profile Likelihood, Fisher-Informations-Sloppiness |
| `validation/` | Cygnus-X1-Pilotstudie, Split Conformal Prediction |
| `contextuality/` | Sheaf-Kontextualität, Čech-Kohomologie, CSW-Graph-Invarianten |
| `information_decomposition/` | PID/Redundancy Bottleneck, BROJA |
| `thermo/` | Schnakenberg-Netzwerkthermodynamik, Crooks/Jarzynski |
| `chemical_organization/` | Chemical Organization Theory (Reaktionsabschluss, Selbsterhaltung) |
| `percolation/` | Bethe-Baum-Perkolation / Kesten-Verzweigung |
| `pattern_formation/` | Turing-Instabilität / Dispersionsrelation |
| `free_boundary/` | Stefan-Neumann-Ähnlichkeitslösung |
| `metarules/` | Repo-übergreifende Meta-Regeln |
| `legacy/` | Adapter zu den ursprünglichen Revision-2/3-Prüfskripten |

### Status, Prüfungen und offene Punkte

- **51 unabhängige `verify_*.py`-Suiten** unter `verification/` laufen
  aktuell alle grün (`python audit_review/run_all_local.py` — Skript nicht
  eingecheckt, siehe [VERIFICATION.md](VERIFICATION.md) für die
  eingecheckten Einzelläufe und ihre Aussagekraft).
- Ein externer Code-Audit ("Tiefenanalyse", 2026-09-20) fand 9 echte
  Korrektheitslücken (P0/P1/P2) in bereits gemergtem Code; alle wurden
  am selben Tag behoben, gegen das jeweilige Audit-Gegenbeispiel verifiziert
  und gegen alle 51 Suiten regressionsgetestet. Details, Priorisierung und
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
  `data/real_data_manifest.json`. Noch keine Validierungspilotstudie
  darauf aufgebaut; das ist eigenständige Folgearbeit.

---

## Revision 3.2 (historisch, 16. September 2026 — vor dem installierbaren Paket)

**Methodischer Entwurf mit Literaturanschlüssen, prüfbaren Modellrechnungen und optionalen F08/F09-Ergänzungen. Umbenannt von "CREP–UTAC–AFET" am 16. September 2026 — siehe [GLOSSARY.md](GLOSSARY.md) für die vollständige Begriffszuordnung und Begründung.**

Johanns Ausgangsabsicht bleibt die Grundlage: **Observation** (vormals CREP) beschreibt Information, **Dynamics** (vormals UTAC) Systeme und deren Dynamik, **Coupling** (vormals AFET) die Kopplung mit einer ausdrücklich ausgewiesenen thermodynamischen Spezialisierung (**Thermodynamics**). Die zentrale Beziehung zwischen Beschreibungsebenen heißt **Correspondence** (vormals „Selbstähnlichkeit" als Gesamtanspruch) — bewusst schwächer als „Äquivalenz" oder „Identität", weil eine Korrespondenz exakt, näherungsweise, projektiv, kontextabhängig oder empirisch widerlegt sein kann. Die Revision ersetzte bereits die unzutreffenden Größenidentitäten des Entwurfs vom 15. September durch definierte Schnittstellen und bedingte Modellbeziehungen; die neue Namensgebung macht diesen Verzicht auf Universalitätsanspruch jetzt auch im Namen sichtbar statt nur im Text.

Der gemeinsame Rahmen beschreibt, **was an einem System gemessen wird, wie es sich entwickelt und wie andere Systeme darauf wirken**. Seine Leitidee ist die von Johann am 16. September nochmals klargestellte **Selbstähnlichkeit**: wiederkehrende Strukturen mit unterschiedlichen Größen, Parametern und Skalen. Die zuvor eingeschlichenen Gleichsetzungen waren Fehler der Ausarbeitung, nicht die beabsichtigte Ausgangsthese.

Eine strukturelle Analogie ist ein Ausgangspunkt. Mathematische Selbstähnlichkeit benötigt eine angegebene Transformation und einen Geltungsbereich; empirisch geprüfte Selbstähnlichkeit zusätzlich Daten und einen quantifizierten Vergleich. Diese Ebenen werden im Formalismus ausdrücklich auseinandergehalten.

## Einstieg

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

## Was die Revision festlegt

- Antwortsteilheit `beta_response` und lokale Erholungsrate `S_rec` sind getrennte Größen.
- Informationsnutzung `eta_info`, dynamischer Einfluss `A_ij` und thermodynamischer Koeffizient `L_ij` erhalten getrennte Definitionen und Einheiten.
- Die korrigierte kubische Modellfamilie lautet `tau * dx/dt = -x^3 + a*x + b`, mit dimensionslosem Zustand x und `tau>0`.
- `a = -tau*S_rec(0)` gilt nur am Gleichgewicht x=0 des symmetrischen Modells b=0. Es ist eine Modellbeziehung, keine allgemeine Parameterelimination.
- Beckenwahrscheinlichkeit, Abstand zur Grenze und lokale Rate werden gesondert gemessen.
- Positive Excess-Stabilität ist eine zu testende Eigenschaft einer gewählten Komposition, kein bereits bewiesenes allgemeines Kriterium für „System-Sein“.
- Etablierte Sätze, eigene Modellableitungen, synthetische Prüfungen und reale Messungen werden getrennt gekennzeichnet.
- Takens begründet eine generische Rekonstruktionsgarantie; eine notwendige universelle Dimensionsschwelle folgt daraus nicht.
- Eine eigenständige Makrodynamik erhält eine konkrete Geschlossenheitsprüfung. EI, Synergie und SVD-Diagnose sind verschiedene Zielgrößen.
- GENERIC ist eine optionale thermodynamische Spezialisierung mit nachzuweisenden Energie-/Entropiebedingungen.
- Viabilität ergänzt die Resilienzbeschreibung um zulässige Bereiche, Eingriffe, Belastungen und Zeiträume.
- Zwei optionale Module (F08/F09, extern geprüft von Aeon, Checksummen und Skriptläufe von Claude nachgerechnet) stehen neben dem Kern, ohne ihn zu verändern: Sheaf-Kontextualität für Verträglichkeitsbedingung 1 und PID/Redundancy Bottleneck für `EI_q`.

Die Revision bearbeitet die bereitgestellten Dokumente und neue Verifikationsbeispiele. Die erreichten Korrekturen in den veröffentlichten Einzelpaketen bleiben als Fortschritt dokumentiert. Für die hier aufgeführten weiteren Codefragen liegt noch kein Patch oder neuer Release vor.

## Ausführen

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

## Ergänzend einspielen

Nicht im Paket enthaltene lokale Dateien bleiben bestehen. Der von Johann bereits archivierte ältere Verifikationsordner wird nicht rekonstruiert oder gelöscht. `apply_manifest.json` benennt aktuelle Änderungen mit Ausgangs- und Zielprüfsummen; das vollständige `manifest.json` umfasst auch die beigefügten Archive. Details: [Übergabe](REVISION_3_2026-09-16.md).

## Status

Die Drei-Schichten-Architektur ist ein expliziter Forschungs- und Beschreibungsrahmen. Die aufgeführten Standardmodelle sind unter ihren Voraussetzungen mathematisch prüfbar. Die universelle Anwendbarkeit, ein universeller Individuationsschwellenwert und universelle Zahlenwerte wie 0,84 oder 1/16 sind dadurch nicht nachgewiesen.

## License

This repository is **dual-licensed**:

- **Source code** (`verification/*.py`) — [GNU General Public License v3.0 or later (GPLv3+)](LICENSE).
- **Documentation** (all Markdown/prose content) — [Creative Commons Attribution 4.0 International (CC BY 4.0)](LICENSE-DOCS).
