# Vom Prüfstand zur verbundenen Untersuchung — Roadmap (2026-09-24)

Antwort auf `prompts/Answers/nicht_stationäre_Treiber/Astra4.txt` und die
zugehörige `SCF_Faehigkeiten_und_Ausbauplan_2026-09-24.md` (Astra, 2026-09-24)
— eine Fähigkeits-/Reifegrad-Bestandsaufnahme des gesamten Repos bei Commit
`0d43898`, kein Fehler-Review. Anders als die vorherigen Roadmaps trägt diese
keine konkreten Bugfixes nach, sondern ein **Ausbauprogramm**: "Jetzt die
vorhandenen Bausteine zu durchgängigen Untersuchungen verbinden."

Johanns Auftrag (2026-09-24): "Ja, gerne als Roadmap und dann abarbeiten."

Gleiche Disziplin wie bei `NONSTATIONARY_ROADMAP.md` und
`MECHANISTIC_VALIDATION_ROADMAP.md`: additive Module, echte Daten,
Hand-Nachrechnung vor Code, `verify_*.py` mit Scope-Verletzungen, volle
Suiten-Regression nach jedem Paket, bestehende Ergebnisse bleiben unverändert
stehen (neue Erkenntnisse ergänzen, nicht überschreiben), jede starke Aussage
verweist auf ihre tatsächliche Begründung und deren Grenzen.

Astras eigene Priorisierung (6 Prioritäten, von ihr selbst zu 3
Arbeitspaketen verdichtet):

| # | Priorität | Kern | Status |
|---|---|---|---|
| 0 | Konsolidierung | README-Überclaims korrigieren, Modulübersicht, eingecheckter Testaufruf + CI | ✅ erledigt |
| 1 | Adaptive Intervallkalibrierung | Rollierende Referenz vs. Adaptive Conformal Inference / Conformal PID Control | ⏸ geplant |
| 2 | Dynamik vs. Messprozess | Latentes Infektionsgeschehen (COVID-Pilot), Energiebilanz-Referenzkonsistenz | ⏸ geplant |
| 3 | Gemeinsame Operatorstrukturen | Mori-Zwanzig-Gedächtnisrahmen für Puffer/Energiebilanz/Renewal/ETAS | ⏸ geplant |
| 4 | Transiente Verstärkung | Nichtnormale Kopplung, `A=[[-1,k],[0,-1]]`-Beispiel, zwei gekoppelte Puffer | ⏸ geplant |
| 5 | Begrenzte Eingriffe | Control-Barrier-Function-QPs, zwei Puffer mit gemeinsamem Ressourcenbudget | ⏸ geplant |

Astras eigene Arbeitspaket-Verdichtung (Reihenfolge bindend, siehe
Originaltext): **(1) Konsolidierung** (= Priorität 0) → **(2) Empirischer
Nutzen** (= Prioritäten 1+2) → **(3) Mathematische Verbindung** (=
Prioritäten 3+4+5, ein gekoppeltes Zwei-Puffer-Labor).

Primärliteratur (vollständige Zitate: siehe
`SCF_Faehigkeiten_und_Ausbauplan_2026-09-24.md`, Abschnitt "Primärliteratur
für die Erweiterungen"):

- Gibbs & Candès (2024), JMLR 25 — Adaptive Conformal Inference unter
  beliebigem Distribution Shift.
- Angelopoulos, Candès & Tibshirani (2023), NeurIPS — Conformal PID Control
  für Zeitreihen.
- Chorin, Hald & Kupferman (2000), PNAS 97 — Mori-Zwanzig-Projektion.
- Trefethen, Trefethen, Reddy & Driscoll (1993), Science 261 — Hydrodynamic
  Stability Without Eigenvalues.
- Ames, Xu, Grizzle & Tabuada (2017), IEEE TAC 62 — Control Barrier Function
  Quadratic Programs.

## Paket 0 — Konsolidierung

**Befund (Astra):** Die README enthält Aussagen, die in Fachseiten und Code
bereits präzisiert wurden — die "exakte" Vorhersage von Kippverhalten durch
eine Kennzahl, "rigoros" bestätigte Nichtidentifizierbarkeit ohne den
inzwischen etablierten Scope-Vorbehalt (siehe Paket 9,
`flat_in_scanned_range` vs. `established_unbounded`), sowie ein veralteter
Bezug auf "Milestones M1-M41", der die seither hinzugekommenen Module (bis
mindestens Milestone 54+) nicht abbildet. Zusätzlich: der in der README
erwähnte lokale Gesamttestläufer `audit_review/run_all_local.py` ist nicht
eingecheckt.

**Umsetzung (2026-09-24):**

- **README-Korrekturen** (`README.md`): (1) die "Milestones M1-M41"-Angabe
  entfernt — die Zählung ist seither über M54 hinausgewachsen und ein
  fixer Endstand veraltet bei jedem Paket sofort; verweist jetzt auf diese
  Übersicht. (2) "χ-Diagnose sagt das Kippverhalten aus Paket 3 exakt
  voraus" korrigiert zu "sagt die RICHTUNG ... korrekt voraus" mit
  explizitem Verweis auf die bereits in `NONSTATIONARY_ROADMAP.md` Paket 4
  dokumentierte Korrektur (χ≥0,5 war rastergebunden, tatsächlicher
  Übergang zwischen r=0,7 und r=0,8). (3) "C_s/C_d/alpha sind praktisch
  nicht identifizierbar, rigoros bestätigt" korrigiert zu "auf diesem
  Fenster schwach eingeschränkt, nicht in absolutem Sinn als
  unidentifizierbar erwiesen" — exakt die in Paket 9 bereits im Code und
  in `docs/energy_balance.md` etablierte Semantik, jetzt auch in der
  README konsistent.
- **Modulübersicht** (neu: `docs/capability_overview.md` +
  `docs/capability_overview.json`): pro Modul (alle 18 Pakete unter
  `src/scoped_correspondence/`) Fragestellung, Modellklasse,
  Voraussetzungen, Evidenzart, zugehörige `verify_*.py`-Skripte und
  bekannte Grenzen — als maschinenlesbare UND lesbare Fassung, identischer
  Inhalt.
- **Eingecheckter Testaufruf** (neu: `scripts/run_verification_suite.py`,
  ersetzt das nicht eingecheckte `audit_review/run_all_local.py` als
  Quelle der Wahrheit): drei getrennte Kategorien wie von Astra verlangt —
  `--category math` (55 Skripte, rein analytisch/synthetisch),
  `--category data` (14 Skripte, laden echte Datensätze — Klassifikation
  automatisch über Referenzen auf `data/real_data_manifest.json` u.ä.),
  `--category links` (neuer interner Markdown-Linkchecker: 179
  Markdown-Dateien, 216 relative Links geprüft, 0 defekt — ein
  ursprünglich als "defekt" gemeldeter Link erwies sich als
  URL-kodierter Leerzeichen-Dateiname, `urllib.parse.unquote` behoben).
- **GitHub Actions CI** (neu: `.github/workflows/verify.yml`): drei
  getrennte Jobs (math/data/links), jeweils mit `pip install -e .` +
  `verification/requirements.txt`.
- **Ergebnis:** 55/55 math, 14/14 data, 0/0 defekte Links — alle drei
  Kategorien grün, reproduzierbar über die neuen eingecheckten Befehle.

## Paket 1-5

Werden nacheinander begonnen, sobald Paket 0 abgeschlossen und regressionsgetestet ist. Jeweils eigener Abschnitt mit Umsetzungsdatum, Ergebnis und Verifikationsstand, analog zu den Paketen in `MECHANISTIC_VALIDATION_ROADMAP.md`.
