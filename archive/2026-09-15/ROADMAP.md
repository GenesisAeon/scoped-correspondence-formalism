# Roadmap: Flächendeckende Anwendung des CREP-UTAC-AFET-Formalismus

Stand: 2026-09-15. Entschieden (Johann, per Rückfrage): zweiphasig, mit
explizitem Go/No-Go dazwischen. Umsetzung ab Phase 2: Claude schreibt
einen präzisen Prompt pro Repo, GrokBot implementiert, Claude reviewt.

## Phase 0 -- abgeschlossen

- Formalismus Entwurf 1 (drei Schichten: `information_layer_crep.md`,
  `system_layer_utac.md`, `coupling_layer_afet.md`).
- Methodik "viele Systeme pro Paket" entwickelt und an `afet-tensions`
  durchgespielt (`worked_example_afet_tensions.md`): Individuations-
  kriterium, Kopplungsmatrix, Reziprozitäts-Check.
- Zwei reale Fehler in `afet-tensions` gefunden (Γ_domain-Zirkelbezug,
  `beta_eff`-Rundtrip) -- dokumentiert, nicht repariert.
- Numerische Verifikation der Kernformeln (`verification/`).

## Phase 1 -- Validierung, KEIN Versions-Bump, KEIN Zenodo (aktuell)

Ziel: prüfen, ob die Methodik an strukturell anderen Paketen trägt, bevor
sie skaliert wird -- nicht Vollständigkeit, sondern Härtung.

**Wichtige Korrektur (2026-09-15, nach Durchspielen):** die komplette
climate/ecology-Serie (P59, P60, P87–P97, P99–P103, P105–P121, siehe
`worked_example_arctic_climate_utac.md`) ist per kanonischer Entscheidung
vom 2026-08-31 (`PACKAGE_REGISTRY.md`) bewusst von jeder CREP/UTAC/AFET-
Anbindung ausgenommen. `arctic-climate-utac` (P127) fällt in dieses
Muster; als reguläres Individuations-Testbeispiel daher durch
`aeon-jurist` ersetzt.

**Ergänzung (2026-09-15, Johanns Vorschlag):** die climate/ecology-Serie
bleibt trotzdem NICHT komplett außen vor -- sie wird nur anders behandelt
als die übrigen Pakete. Analyse-Dokumente für diese Serie entstehen
AUSSCHLIESSLICH hier in `crep-utac-afet-formalism/` (eigene
`worked_example_<paket>.md`-Dateien), NIEMALS als Code-Änderung, Bridge
oder sonstiger Eingriff am jeweiligen Originalpaket selbst. Das trennt
"wir untersuchen, ob/wie der Formalismus theoretisch anwendbar wäre" von
"das Paket bekommt eine Bridge" -- respektiert damit exakt den
Zugänglichkeits-Grund der 2026-08-31-Entscheidung (Grund 2, siehe
`worked_example_arctic_climate_utac.md`), ohne die Serie von der
Betrachtung komplett auszuschließen. Diese Pakete zählen für die
Go/No-Go-Kriterien unten trotzdem NICHT als reguläre Individuations-
Testfälle -- sie sind eine eigene, dritte Analyse-Spur.

**Drei Pakete, Stand nach Korrektur:**
1. ✅ **`resilience-core`** (P40) -- abgeschlossen, siehe
   `worked_example_resilience_core.md`. Schon in `METRIC_REGISTRY.md` als
   CREP-nicht-konform dokumentiert; guter zweiter Datenpunkt für dasselbe
   Fehlermuster wie bei `afet-tensions`, plus ein bereits real
   implementiertes Onsager-Kopplungsbeispiel.
2. ⚠️ ~~`arctic-climate-utac`~~ -- N/A durch bestehende Policy, siehe
   `worked_example_arctic_climate_utac.md`. Wertvoller Fund (dritter
   Enumerations-Ausgang: "explizit ausgenommen"), zählt aber nicht als
   Individuations-Testfall.
3. **`aeon-jurist`** (Ersatz für Slot 2) -- Nicht-Physik-Domäne
   (Rechtsprechung/Klassifikation), um zu prüfen, ob die Methodik ohne
   physikalische Kontrollparameter trägt.
4. **`scope-resilience`** -- hat mit `Ρ_sem` schon einen bewusst eigenen
   Namen statt CREP laut `METRIC_REGISTRY.md`; semantische statt
   physikalische Domäne.

**Für jedes Paket, dieselbe Tiefe wie bei `afet-tensions`:**
- **Schritt 0 (neu, 2026-09-15):** `DISCLAIMER.md`/`PACKAGE_REGISTRY.md`
  auf eine bestehende Ausnahme-Policy prüfen, BEVOR irgendeine Analyse
  beginnt -- siehe `worked_example_arctic_climate_utac.md`.
- Enumeration aller Klassen/Module mit potenziellem eigenem Zustand.
- Individuationskriterium anwenden -- wie viele sind wirklich Systeme?
- Kopplungen zwischen gefundenen Systemen im Code suchen, Richtung prüfen
  (reziprok oder nicht?).
- Alle Zahlenbehauptungen numerisch nachrechnen, nicht nur symbolisch
  prüfen.
- Ergebnis als eigenes `worked_example_<paket>.md` in diesem Ordner.

**Go/No-Go-Kriterien nach Phase 1** (damit die Entscheidung nicht aus dem
Bauch heraus fällt):
- Individuationskriterium war in mindestens 2 von 3 Paketen ohne neue
  Ad-hoc-Erweiterung anwendbar.
- Keine weitere fundamentale Struktur-/Namenskollision gefunden, die
  bereits getroffene Entscheidungen (R/R_ctrl, S/K/R/V-Definitionen)
  entwertet.
- Mindestens einmal eine reale Kopplungsmatrix zwischen ≥2 Systemen
  erfolgreich aufgestellt (wie bei `afet-tensions`).
- Mindestens ein Paket mit sinnvoll berechenbarer Latitude/Precariousness.

**Ergebnis: alle vier Kriterien erfüllt (2026-09-15).** Alle vier
Worked-Examples abgeschlossen (`afet-tensions`, `resilience-core`,
`aeon-jurist`, `scope-resilience`), plus der Policy-Bonus-Fund
(`arctic-climate-utac`). **GO fuer Phase 2**, von Johann bestaetigt.
Drei starke cross-domain-Funde zusaetzlich nach `semantic-map`
uebernommen (Gateway-Knoten + zwei Einzelfunde, siehe
`nodes/meta/crep_utac_afet_formalism_overview.json` und Geschwister in
`D:\mandala\semantic-map`).

Nur wenn diese vier zutreffen: Übergang zu Phase 2. Sonst: Formalismus an
den gefundenen Lücken nachschärfen, Phase 1 mit neuen Paketen wiederholen.

## Phase 2 -- Repo-für-Repo-Sprint (erst nach explizitem Go)

**Workflow pro Repo:**
1. Claude liest das Repo, enumeriert Systeme/Kopplungen (wie Phase 1).
2. Claude schreibt einen präzisen, selbstständigen Prompt für GrokBot:
   welche Klassen sind Systeme, welche Kopplungen umsetzen, welche
   bekannten Zirkelbezüge/Platzhalter beheben, welche neuen
   S/K/R/V-Methoden ergänzen -- mit exakten Dateipfaden und Vorher/
   Nachher-Erwartung.
3. GrokBot implementiert.
4. Claude reviewt: numerisch nachrechnen (nicht nur lesen), bestehende
   Tests laufen lassen, neue Tests für neue Formeln ergänzen.
5. Erst nach bestandenem Review: Versions-Bump + CHANGELOG-Eintrag.
6. Zenodo-Release nur, wenn Johann das für dieses konkrete Repo
   ausdrücklich freigibt -- kein Automatismus pro Repo.

**Sequenzierung (Vorschlag, noch nicht entschieden):** nach
Paket-Familien clustern (z.B. alle `-utac`-Klima-Pakete zusammen, da sie
strukturell ähnlich sind), nicht alphabetisch oder zufällig -- spätere
Repos einer Familie profitieren vom Prompt-Template des ersten.

## Phase 2 -- Tracking

| # | Repo | Prompt | Status | Review | Version-Bump/Zenodo |
|---|---|---|---|---|---|
| 1 | `resilience-core` (P40) | `prompts/01_resilience_core_calibration_honesty.md` | ✅ GrokBot fertig, ✅ Claude-Review bestanden, ✅ committed+getaggt+gepusht (v1.0.1, Commit c33342f) | Alle Zahlen numerisch nachgerechnet; 107/108 Tests gruen, 1 vorbestehender unabhaengiger Fehlschlag (siehe `FOLLOWUP_TICKETS.md`) | ✅ **Live**: PyPI zeigt `1.0.1` (per JSON-API bestaetigt), GitHub-Release veroeffentlicht (Wheel+Sdist). Ursache des ersten Fehlschlags war ein fehlender PyPI-Trusted-Publisher-Eintrag -- von Johann direkt bei PyPI nachgetragen, danach Re-Run (`gh run rerun --failed`) erfolgreich. "Publish to Zenodo"-Job lief gruen durch, ist aber weiterhin nur der Platzhalter-Echo-Schritt -- ob eine neue Zenodo-Version tatsaechlich archiviert wurde (klassische Webhook-Integration), noch nicht unabhaengig verifiziert. |
| 2 | `scope-resilience` (P41) | `prompts/02_scope_resilience_odE_fixpoint_honesty.md` | ✅ GrokBot fertig, ✅ Claude-Review bestanden, ✅ committed+getaggt+gepusht (v1.0.1, Commit c4c43f0) | Diff nur `semantic_utac.py`, nur Docstring-Zeilen (verifiziert); 144/145 Tests, derselbe vorbestehende CLI-Fehler wie bei resilience-core (bestaetigt, siehe FOLLOWUP_TICKETS.md); GrokBots "145 passed"-Meldung war ungenau (144 passed + 1 failed), inhaltlich aber korrekt | ✅ **Live**: PyPI `1.0.1`, GitHub-Release veroeffentlicht -- lief beim ersten Versuch durch, kein Trusted-Publisher-Problem hier. |
| 3 | `afet-tensions` (P34) | `prompts/03_afet_tensions_independent_refit.md` | ✅ GrokBot fertig, ✅ Claude-Review bestanden, ✅ committed+getaggt+gepusht (v1.0.1, Commit 9de5d5c) | Fit-Skript unabhaengig ausgefuehrt, alle Zahlen bis auf 1e-6 identisch reproduziert; ein echter Fehler gefunden+behoben (README-Code-Fence durch Steuerzeichen korrupt -- `` `\x08ash `` statt ```` ```bash ````, alle anderen Dateien auf weitere Steuerzeichen gescannt, sauber); 62/63 Tests, derselbe CLI-Bug wie in Ticket 1+2 (dritte Bestaetigung, siehe FOLLOWUP_TICKETS.md) | ✅ **Live**: PyPI `1.0.1`, GitHub-Release + Zenodo-Job liefen beim ersten Versuch durch. CHANGELOG.md hatte einen veralteten Eintrag aus einer frueheren Session-Runde (reine Doku-Ankuendigung vor dem echten Fix) -- durch den echten [1.0.1]-Eintrag ersetzt, nicht daneben stehen gelassen. |
| 4 | `resilience-core`+`scope-resilience`+`afet-tensions` (kombiniert) | `prompts/04_diamond_setup_cli_test_contamination.md` | ✅ GrokBot fertig, ✅ Claude-Review bestanden (alle 3 Repos einzeln verifiziert) | resilience-core: Datei geloescht, 95/95 gruen (kein CLI-Bug mehr!). scope-resilience: echte `_cli.py`-Tests, 138/138 gruen, `fastmcp` unabhaengig als nicht-installiert bestaetigt. afet-tensions: echte `cli.py`-Tests, 55/55 gruen, Benchmark-Konsistenz unabhaengig bestaetigt (aktuell alle Targets True). Keine diamond_setup-Reste in einer der drei Dateien (gegengeprueft). | ✅ **Live** (gebuendelt mit Ticket 5, siehe unten) |
| 5 | 12 Pakete (Liste in Prompt) | `prompts/05_ecosystem_wide_diamond_setup_contamination.md` | ✅ GrokBot fertig, ✅ Claude-Review bestanden (alle 12 Repos einzeln nachgetestet, mehrere echte Funde korrigiert) | Waehrend Review ein **vorbestehendes Umgebungsproblem** entdeckt: 8 der 12 Pakete hatten stale editable pip-Installs auf alte `.claude/worktrees/<paket>-vendor-fix/`-Verzeichnisse -- korrigiert, Worktree-Ordner unangetastet gelassen. Danach mehrere echte Funde behoben: `worldview/tests/test_cli.py` faelschlich als Kontamination geloescht (echte CLI-Tests, wiederhergestellt, Coverage 99.59%), `phaethon-chimera`+`worldview` je ein Rich-ANSI-Splitting-Testbug (behoben), `sandpile-utac`'s `__license__="MIT"` widersprach der echten GPL-3.0-Lizenz (korrigiert), `sa-sv-duality`'s Test hatte afet-tensions' DOI kopiert (korrigiert), diverse stale `__version__`-Strings/CITATION.cff-Metadaten in `amazon-utac`/`eml-utac-bridge`/`cellular-genesis`/`sandpile-utac`/`seismic-utac`/`vrig-cosmological` (alle korrigiert und im jeweiligen CHANGELOG dokumentiert). Alle Details in `FOLLOWUP_TICKETS.md`. | ✅ **Alle 12 Pakete live**, siehe Versions-Tabelle unten |

**Ticket-4/5 Versions-Bump-Ergebnis (2026-09-15, in 3 Vierer-Gruppen):**

| Repo | Version | PyPI | GitHub Release | CI |
|---|---|---|---|---|
| resilience-core | 1.0.3 | ✅ | ✅ | ✅ (chronischer Lint-Fehler seit 2026-08-01 behoben) |
| scope-resilience | 1.0.2 | ✅ | ✅ | ✅ |
| afet-tensions | 1.0.2 | ✅ | ✅ | ✅ |
| amazon-utac | 1.2.1 | ✅ | ✅ | ✅ |
| cellular-genesis | 1.0.1 | ✅ | ✅ | ✅ |
| eml-utac-bridge | 1.0.1 | ✅ | ✅ | ✅ |
| phaethon-chimera | 1.0.1 | ✅ | ✅ | ✅ |
| sa-sv-duality | 1.0.1 | ✅ | ✅ | ✅ |
| sandpile-utac | 1.0.2 | ✅ | ✅ | ✅ (Python-3.10-Matrix + mypy strict seit 2026-06-25/07-17 behoben) |
| seismic-utac | 1.0.2 | ✅ | ✅ | ✅ (Python-3.10-Matrix + mypy strict seit 2026-06-25/07-17 behoben) |
| vrig-cosmological | 1.0.1 | ✅ | ✅ | ✅ |
| worldview | 1.0.1 | ✅ | ✅ | ✅ |

Drei PyPI-Trusted-Publisher-Luecken unterwegs gefunden und von Johann
behoben (`cellular-genesis`, `eml-utac-bridge`, `phaethon-chimera` --
hatten dort noch nie funktioniert, seit ihrem initialen v1.0.0-Release),
danach `gh run rerun --failed` erfolgreich fuer alle drei.

**Root Cause zu Ticket 5 (2026-09-15):** beim Review von Ticket 4 aufgefallen,
dass `resilience-core` noch weitere, gleichartig kontaminierte Dateien hat
(`test_preset.py`, `test_validator.py`, `test_protocol.py` -- alle
byte-identische Kopien von diamond-setup's eigener Testsuite, keine
davon testet das jeweilige Paket selbst). Oekosystem-weite Hintergrundsuche
(`grep -rl "diamond-setup's own repository must pass validation"`) fand
dasselbe Muster in **13 Paketen** (12 aktive + 1 Legacy-Kopie in
`Architektur--Planungsprojekt`, letztere bewusst ausgenommen). 4 der 12
Pakete (`phaethon-chimera`, `sa-sv-duality`, `sandpile-utac`,
`seismic-utac`) haben zusaetzlich eine eigene, bisher komplett
ungetestete CLI wie `scope-resilience`/`afet-tensions` -- deren
`test_cli.py` wird durch echte Tests ersetzt, nicht nur geloescht.

**Root Cause zu Ticket 4 (2026-09-15, kein diamond-setup-Bug):** alle drei
`tests/test_cli.py` sind vollstaendige, unangepasste Kopien von
diamond-setup's EIGENER Testsuite (verifiziert: kommt nicht aus
diamond-setup's Scaffold-Templates, reine Copy-Paste-Kontamination).
`resilience-core` hat keine eigene CLI (Datei wird geloescht);
`scope-resilience` und `afet-tensions` haben je eine echte, bisher
0%-getestete eigene CLI (werden durch echte Tests ersetzt).

**Wichtig zu Ticket 3 (2026-09-15):** anders als 1+2 ist das keine reine
Doku-Korrektur -- Γ_domain UND kappa wurden von Claude vorab selbst
unabhaengig gefittet (gewichtete Kleinste-Quadrate gegen die 5 echten
H0- bzw. 3 echten S8-Messungen), NICHT GrokBot ueberlassen. Ergebnis
aendert reale Vorhersagen (H0, S8, DESI, Euclid); LIGO unberuehrt. Vor
dem Prompt gab es eine echte Verzweigung: der ehrliche Γ_domain-Refit
verfehlt S8(z=0) allein um ~2-3σ gegen alle drei realen Surveys --
Johann hat sich explizit dafuer entschieden, kappa im selben Ticket
mitzufitten statt die Abweichung nur offen auszuweisen. Neuer,
gut sitzender kappa-Fit: chi2/dof ≈ 0.17.

**Warum resilience-core zuerst:** klein abgegrenzter, risikoarmer Fix
(Dokumentation + Test-Anbindung, keine neuen Formeln/Werte) -- dient auch
dazu, den GrokBot->Review-Workflow selbst einzufahren, bevor er auf
komplexere Repos angewendet wird. Gewaehlt statt `afet-tensions`, weil
letzteres einen echten Onsager-Refit braucht (siehe
`coupling_layer_afet.md` Abschnitt 4) -- ein groesseres, spaeteres Ticket.

**Tracking:** neue Tabelle in `METRIC_REGISTRY.md` oder hier, analog zur
bestehenden `bridge_adapted`-Migrationstabelle -- welches Repo, welcher
Stand, welches Datum, wer reviewt hat.

## Phase 3 -- Ökosystem-weite Ausrollung (2026-09-15, nach Ticket 4/5-Abschluss)

Johann: "Mach gerne eine große Roadmap für alle Repos [...] Überall
unseren neuen CREP/UTAC/AFET formalissmus integrieren wo er hin gehört
alle Bugs fixen die wir finden, alles neu versionieren [...] Ob wir
genug Fallbeispiele haben um GrokBot oder Agenten von dir zu
beauftragen darfst du frei entscheiden."

**Bestandsaufnahme (per Hintergrund-Agent, 2026-09-15):** 111 reale
Python-Pakete unter `D:\mandala` (109 mit `pyproject.toml`;
`nukleonscanner` hat keinen Python-Code). 12 davon bereits fertig
(Tickets 1-5, siehe oben). **97 verbleibend**, aufgeteilt in fünf klar
unterschiedliche Spuren:

### 3A -- Neue diamond-setup-Kontamination -- ERLEDIGT, aber ALLE DREI waren Fehlalarm

**Korrektur nach echter Prüfung (2026-09-15):** die grep-basierte
Fork-Vermutung ("gleiche Dateinamen wie das Kontaminationsmuster") war
zu grob. Direkte Inhaltsprüfung ergab: **keines der drei Pakete hatte
tatsächlich kontaminierte Tests.**
- `cygnus-jet-utac`: `test_cli.py`/`test_preset.py`/`test_validator.py`
  testen ausschließlich das eigene Paket (eigene CLI, eigene
  `__version__`, eigene `constants`/`efficiency`) -- reiner
  Namens-Zufall mit dem Kontaminationsmuster.
- `aeon-trikaya`: `test_cli.py` ruft per `subprocess` die eigene
  `aeon_trikaya.aeon_cli` auf -- legitim.
- `quantum-genesis`: laut eigenem Docstring bereits in einer früheren
  Session korrigiert (`test_cli.py` importiert jetzt
  `quantum_genesis.__version__`, nicht mehr `diamond_setup`).

Kein GrokBot-Prompt nötig. Stattdessen bei der Direktprüfung drei
andere, echte, unabhängige Bugs gefunden und behoben/dokumentiert:

- **`cygnus-jet-utac` (v1.0.0 → v1.0.1, ✅ released):** (1) derselbe
  Python-3.10-CI-Matrix-Bug wie `sandpile-utac`/`seismic-utac`
  (`requires-python` war `>=3.10` trotz `diamond-setup>=2.2.0`-
  Abhängigkeit, CI seit 2026-07-17 rot) -- behoben. (2) ein
  `mypy --strict`-Fehler in `jet.py` (fehlende Ndarray-Typannotation),
  der noch nicht in CI aufgetreten war (kein Push seit 2026-08-01), aber
  mit der aktuellen ungepinnten `numpy`-Version lokal reproduzierte --
  vorab behoben, um keine neue Rot-Phase zu verursachen. (3)
  `__version__` war seit dem 1.0.0-Release bei `"0.1.0"` stehen
  geblieben, UND der zugehörige Test hatte denselben falschen Wert
  hartkodiert (bestand also, während er eine Lüge testete) -- beides
  korrigiert. `CI` (Tests+Lint) jetzt zum ersten Mal seit 2026-07-17
  komplett grün. **Offen:** PyPI Trusted Publishing hat seit dem
  allerersten v1.0.0-Release nie funktioniert (`invalid-publisher`,
  gleiches Muster wie `cellular-genesis`/`eml-utac-bridge`/
  `phaethon-chimera`) -- braucht Johanns pypi.org-Eintrag, siehe
  `FOLLOWUP_TICKETS.md`.
- **`aeon-trikaya`:** hat gar keinen Git-Remote -- rein lokales Repo,
  nie gepusht. Braucht erst Johanns Entscheidung (absichtlich lokal wie
  `vesta-sim`, oder nur noch nicht veröffentlicht?), bevor überhaupt ein
  Release/CI-Fix sinnvoll wäre. Siehe `FOLLOWUP_TICKETS.md`.
- **`quantum-genesis`:** komplett grün, nichts zu tun.

**Nicht bestätigt, nur beobachtet:** `diamond-setup` selbst hat dieselben
vier Dateinamen in seiner eigenen `tests/` -- verifiziert KEIN Bug
(es sind diamond-setups echte Selbsttests, Ursprung der kopierten
Vorlage). 13 weitere Pakete zeigen `test_cli.py` OHNE
`diamond-setup`-Abhängigkeit (`AdvancedWeightingSystems`, `aeon-ai`,
`climate-dashboard`, `cosmic-moment`, `cosmic-web`,
`entropy-governance`, `fieldtheory`, `mandala-visualize`,
`medium-modulation`, `mirror-machine`, `sigillin`, `sonification`,
`utac-core`) -- fast sicher legitime eigene CLI-Tests, kein Bug;
niedrige Priorität, nur bei Gelegenheit spot-checken, kein eigenes
Ticket.

### 3B -- CREP/UTAC/AFET-Integration, echte Kandidaten (20 Pakete)

**Das ist der Kern dessen, was Johann will.** Struktureller Fit
geprüft, nicht nur Namens-Vorkommen (per
[[feedback_utac_crep_prevalence_not_validation]]-Regel: verbreitete
Nutzung ist keine wissenschaftliche Bestätigung). Alle 20 sind reale
dynamische/Schwellenwert-Systeme (keine Governance-/Tooling-/
Klima-Pakete):

`cygnus-jet-utac`, `amoc-utac`, `neural-avalanche-utac`,
`solar-flare-utac`, `quantum-genesis`, `spiking-aeon`,
`theta-resonance`, `epi-sigillin`, `hikari-ledger`,
`diffusive-routing`, `beta-clustering-utac`, `implosive-origin-utac`,
`phi-scaling-validator`, `genesis-scope`, `ai-emergence-utac`,
`aeon-trikaya`, `kan-physics`, `aeon-sealcore`, `genesis-tip`,
`multi-scale-somatic-coherence`.

**Workflow pro Paket -- KEINE Abkürzung, dieselbe Tiefe wie Phase 1:**
1. **Claude-geführte Worked-Example-Validierung ZUERST** (Individuations-
   kriterium, Kopplungssuche, numerisches Nachrechnen) -- das ist die
   wissenschaftliche Kernarbeit, wird NICHT an GrokBot delegiert.
2. Nur wenn echter, struktureller Fit bestätigt (nicht bloß kosmetisch):
   Claude schreibt einen präzisen GrokBot-Implementierungs-Prompt
   (S/K/R/V-Methoden, Kopplungsmatrix, welche Klassen betroffen sind).
3. GrokBot implementiert, Claude reviewt numerisch, Tests laufen lassen.
4. Erst danach: Version-Bump + CHANGELOG. Zenodo nur mit Johanns
   expliziter Freigabe pro Repo (wie in Phase 2).

**Delegations-Entscheidung (Johanns "frei entscheiden"):** Schritt 1
(Worked-Example-Validierung) ist gut genug durch die 5 bestehenden
Phase-1-Beispiele als Vorlage abgedeckt, um sie an parallele
Claude-Subagenten zu delegieren -- die Methodik selbst ist bereits
vollständig schriftlich fixiert (`worked_example_*.md`), nicht
Freihand-Interpretation. GrokBot bleibt für Schritt 1 ungeeignet
(erfordert wissenschaftliche Abwägung, keine Implementierung). Geplant:
20 Pakete in 5 Vierer-Gruppen, pro Gruppe 4 parallele Forks für die
Worked-Examples, Claude prüft jedes Ergebnis einzeln nach, bevor ein
GrokBot-Prompt für Schritt 2 entsteht.

**Vorgeschlagene Gruppen (thematisch geclustert, nicht alphabetisch):**
- Gruppe 1 (Astro/Plasma): `cygnus-jet-utac`, `amoc-utac`,
  `solar-flare-utac`, `neural-avalanche-utac`
- Gruppe 2 (Quanten/Neuronal): `quantum-genesis`, `spiking-aeon`,
  `theta-resonance`, `ai-emergence-utac`
- Gruppe 3 (Netzwerk/Fluss): `diffusive-routing`,
  `beta-clustering-utac`, `genesis-scope`, `hikari-ledger`
- Gruppe 4 (Ursprung/Skalierung): `implosive-origin-utac`,
  `phi-scaling-validator`, `genesis-tip`, `aeon-sealcore`
- Gruppe 5 (Rest): `epi-sigillin`, `aeon-trikaya`, `kan-physics`,
  `multi-scale-somatic-coherence`

(`aeon-trikaya` und `quantum-genesis` überschneiden sich mit 3A --
Kontaminations-Fix und Formalismus-Bewertung sind unabhängige Schritte,
können in beliebiger Reihenfolge laufen.)

### 3C -- `Feldtheorie` (P70): Sonderfall, eigenes Gespräch nötig

Laut Registry die AFET-Ursprungsquelle selbst (78-System-
Validierungskohorte), lokal bereits bei Version 7.0.2 (Registry veraltet
bei 6.0.0). Das ist vermutlich die Referenzimplementierung, auf die der
NEUE Formalismus zurückverweisen sollte, statt sie wie ein gewöhnliches
Integrationsziel zu behandeln -- braucht eine eigene inhaltliche
Entscheidung mit Johann (wie verhält sich der alte AFET-Ursprung zum neu
hergeleiteten Coupling-Layer? Ersetzen, verweisen, oder beides parallel
dokumentieren?), kein generischer Gruppen-Slot.

### 3D -- Kosmetische/schwache Treffer (22 Pakete): standardmäßig NICHT integrieren

`mandala-visualize`, `sonification`, `universums-sim`,
`genesis-q4-core`, `HexaAgent`, `entropy-table`, `cosmic-web`,
`climate-dashboard`, `gemeinwohl`, `unified-mandala`,
`unified-mandala-Demo`, `utac-core`, `sigillin`, `mirror-machine`,
`cosmic-moment`, `medium-modulation`, `entropy-governance`,
`implosive-genesis`, `fieldtheory` (klein geschrieben, ungleich
`Feldtheorie`), `AdvancedWeightingSystems`, `aeon-ai`, `genesis-os`.

Erwähnen CREP/UTAC nur namentlich oder sind Governance-/Tooling-/
Visualisierungs-Pakete ohne eigene Dynamik -- genau das Muster, vor dem
[[feedback_utac_crep_prevalence_not_validation]] warnt. Default: keine
erzwungene Integration. Ausnahme nur, wenn ein schneller Blick (nicht
volle Worked-Example-Tiefe) einen echten, bisher übersehenen
strukturellen Fit zeigt.

### 3E -- Climate/Ecology-Serie (~55 Pakete): explizit ausgenommen, separater Strang

Per Policy vom 2026-08-31 (`PACKAGE_REGISTRY.md`) und bereits in Phase 1
bestätigt (`worked_example_arctic_climate_utac.md`): keine Code-
Änderung, keine Bridge, kein Eingriff an den echten Paketen. Wie in
Phase 1 vereinbart bleibt das eine **rein exploratische, von den echten
Paketen getrennte Analyse-Spur** ausschließlich hier in
`crep-utac-afet-formalism/` -- eigene `worked_example_<paket>.md`-Dateien,
falls Johann diesen Strang wieder aufnehmen möchte. Kein Teil des
Versions-Bump-Ziels ("alles neu versionieren"), da an den Paketen selbst
nichts geändert wird.

### Registry-Pflege (niedrige Priorität, kein eigenes Ticket)

`PACKAGE_REGISTRY.md` ist an mehreren Stellen hinter der Realität zurück
(z.B. `amoc-utac` 1.3.2 vs. Registry 1.3.0, `genesis-os` 1.0.12 vs.
1.0.11, `coral-reef-utac` 1.3.0 vs. 1.0.0, `antarctic-ice-shelf-utac`
2.1.0 vs. 2.0.0; Registry-Tabelle endet bei P121, Fließtext erwähnt aber
bereits P132). Bei Gelegenheit synchronisieren, kein eigener
Sprint-Slot.

### Was "alles neu versionieren" hier konkret heißt

Kein künstlicher Versions-Bump für Pakete, die inhaltlich unverändert
bleiben (3D, 3E) -- das wäre Bump ohne Grund. "Up to date" heißt: jedes
Paket, das in 3A/3B/3C tatsächlich einen echten Fix oder eine echte
Integration bekommt, wird sauber versioniert, released, und die
Registry-Drift (siehe oben) wird bei der Gelegenheit mitkorrigiert --
nicht, dass am Ende alle 97 Pakete zwangsweise eine neue Versionsnummer
tragen.

## Was bewusst nicht in dieser Roadmap steckt

- Kein Automatismus "jedes Paket bekommt am Ende einen Zenodo-Release" --
  das bleibt jedes Mal Johanns explizite Einzelentscheidung.
- Keine feste Deadline/Geschwindigkeit -- Tempo richtet sich danach, wie
  viel Claude-Review-Kapazität pro Repo tatsächlich investiert wird, nicht
  danach, wie schnell GrokBot implementieren kann.
- Keine Reihenfolge-Festlegung für Phase 2 vor Abschluss von Phase 1.
