# Glossar und Legacy-Mapping

Stand: 16. September 2026. Entscheidung dokumentiert in [FOLLOWUP_TICKETS.md](FOLLOWUP_TICKETS.md). Vollständige Begründung, Alternativenvergleich und Softwarearchitektur-Ausblick: [prompts/Answers/ChatGPTAstra2.md](prompts/Answers/ChatGPTAstra2.md).

## Warum umbenannt

„CREP–UTAC–AFET" klang bereits wie eine fertige, vereinheitlichte Theorie, bevor die dahinterliegende Mathematik das trug. Genau dieser Klang hat wiederholt dazu verleitet, strukturelle Analogie als Identität zu verkaufen (β=S, V=Panarchy=Onsager-L, geteiltes σ=2,2 als "Universalität"). Revision 3.2 hat diese Gleichsetzungen bereits mathematisch zurückgenommen; die neue Terminologie macht das jetzt auch im Namen sichtbar: **Rollen und geprüfte Beziehungen zwischen ihnen, keine drei vereinheitlichten Größen.**

Namensregeln (aus dem Vergleich mit Kategorientheorie, Sheaf-Theorie, PID-Literatur, equation-free Multiscale Modeling und Software-Architekturstandards):

1. Rollen vor Herkunft — `observation`, nicht `crep`.
2. Starke mathematische Wörter nur bei erfülltem Vertrag — `conjugacy` nur bei echter Konjugation, `sheaf` nur in der Sheaf-Spezialisierung.
3. Konzepte von Algorithmen trennen — `info_decomposition` als Konzept, `redundancy_bottleneck()` als Methode darunter.
4. Richtung sichtbar machen — `project`, `restrict`, `lift`.
5. Scope ist ein First-Class Concept — jede Korrespondenz trägt Domäne, Voraussetzungen, Zeitbezug, Fehlerdefinition.
6. Verification ≠ Validation — Rechenprüfung (synthetisch) und reale Datenprüfung (empirisch) strikt getrennt.
7. Kein neues Akronym als Marke über den Modulen.

## Begriffszuordnung

| Alt | Neu | Bedeutung |
|---|---|---|
| CREP | **Observation** | Messung, Information, Repräsentation, Evidenz — was ist beobachtbar, erhalten, nutzbar? |
| UTAC | **Dynamics** | Zustand, Evolution, Störung, Kontrolle, Stabilität — wie entwickelt sich ein Zustand? |
| AFET | **Coupling** | Wechselwirkung, Fluss, gemeinsame Ressourcen — wie wirkt eine Komponente auf eine andere? |
| AFET-Thermodynamik-Sonderfall | **Thermodynamics** | Bilanzen, Flüsse, GENERIC — eigene Spezialisierung, kein Synonym für Coupling |
| „Selbstähnlichkeit" (als Gesamtanspruch) | **Correspondence** | Beziehung zwischen zwei Modellen/Ebenen inkl. Scope, Zeitabbildung, Residuum — schwächer als Äquivalenz/Identität |
| F08 | **Contextuality** | öffentliches Konzept; `sheaf_contextuality` bleibt der methodenspezifische Dateiname |
| F09 | **Information Decomposition** | öffentliches Konzept; Williams-Beer/Kolchinsky-RB sind Algorithmen darunter, nicht der Konzeptname |
| `verify_*.py`-Suiten | **Verification** | prüft, ob Rechnung/Herleitung korrekt ist — synthetisch, kein empirischer Nachweis |
| (noch nicht existent) | **Validation** | reale Datenprüfung: Kalibrierung, Holdout, Baselines, Unsicherheit — bewusst von Verification getrennt gehalten |

## Was NICHT umbenannt wird

- **Die bereits veröffentlichten ~60 GenesisAeon-Ökosystempakete.** Kein Massen-Umbenennen — zu teuer, zu riskant (PyPI-Releases, CI, Tests) für ein reines Vokabular-Problem, das die eigentliche Wissenschaft nicht berührt. Sie bleiben reproduzierbar mit dem Hinweis „CREP/UTAC/AFET war der frühe Arbeitsname" in ihrer jeweiligen Dokumentation, wo das bereits vermerkt ist.
- **Historische Revisionsdokumente** (`archive/`, `REVISION_*.md`, `DESIGN.md`) — sie beschreiben, was zum jeweiligen Zeitpunkt tatsächlich geschrieben stand, und werden nicht rückwirkend umgeschrieben.
- **Mathematische Kurzsymbole in Formeln** (T, Φ, L, M, π, β, S) — bleiben in Gleichungen Standardnotation; nur die Bedeutungszuordnung ist jetzt explizit getrennt (siehe `FORMALISM.md` §2, Notationstabelle).

## Status dieser Umbenennung

Dies ist **Teil 1** (Namen, Repo, Glossar) eines größeren, noch nicht begonnenen Vorhabens. Teil 2 (eine tatsächliche Softwarebibliothek mit `src/`-Baumstruktur, typisierten Contracts, Verification/Validation-Pipeline) ist grob in [ARCHITECTURE_ROADMAP.md](ARCHITECTURE_ROADMAP.md) skizziert, damit nichts aus dem Astra-Vorschlag verloren geht — aber **nicht** automatisch beauftragt. Die aktuellen Formalismus-Dokumente (`FORMALISM.md`, `information_layer_crep.md`, `system_layer_utac.md`, `coupling_layer_afet.md`, `context_transformations.md`, `emergence_and_closure.md`, `sheaf_contextuality.md`, `pid_redundancy_bottleneck.md`) tragen inhaltlich weiterhin ihre historischen CREP/UTAC/AFET-Bezeichnungen und Dateinamen; ihre vollständige Migration auf die neuen Begriffe ist Teil der „Core Extraction"-Phase in der Roadmap, nicht Teil dieser ersten Runde.
