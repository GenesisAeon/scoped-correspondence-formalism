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
| 1 | Adaptive Intervallkalibrierung | Rollierende Referenz vs. Adaptive Conformal Inference / Conformal PID Control | ✅ erledigt |
| 2 | Dynamik vs. Messprozess | Latentes Infektionsgeschehen (COVID-Pilot), Energiebilanz-Referenzkonsistenz | ✅ erledigt (COVID-Teil; Energiebilanz-Teil zurückgestellt) |
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

## Paket 1 — Adaptive Intervallkalibrierung (2026-09-24)

Neues Modul `validation/adaptive_interval_calibration.py` (Milestone 55),
verifiziert in `verify_adaptive_interval_calibration.py` (5/5 Checks).
Drei Kalibrierungsmethoden teilen dieselbe kausale Quantil-Maschine
(exakt dieselbe strikte zeitliche Zulässigkeit wie
`leave_one_origin_out_intervals`) und unterscheiden sich nur darin, wie
sich das Fehlniveau `alpha_t` über die Zeit entwickelt:

- **`rolling_reference`**: `alpha_t` fest bei `alpha_target` — Astras
  angeforderte einfache Referenz.
- **`aci`**: Adaptive Conformal Inference (Gibbs & Candès 2024), Online-
  Rekursion `alpha_{t+1} = alpha_t + gamma*(alpha_target - err_t)`.
- **`pid`**: NUR der Proportional+Integral-Anteil von Conformal PID
  Control (Angelopoulos, Candès & Tibshirani 2023) — der gelernte
  "Scorecaster" und die begrenzende Sättigungsfunktion des Originalpapers
  sind bewusst NICHT implementiert, explizit als Scope-Grenze dokumentiert
  statt stillschweigend approximiert.

**Coverage-Semantik-Warnung** (wie von Astra verlangt): ACIs echte
Garantie ist eine LANGFRIST-Durchschnittsabdeckung unter beliebigem
Distribution Shift (Gibbs & Candès 2024, Theorem 1) — keine punktweise
oder bedingte Abdeckungsgarantie zu jedem einzelnen Zeitpunkt, und für die
vereinfachte PID-Variante existiert gar keine eigene publizierte Garantie.

**Synthetischer Regressionstest:** ein deterministischer Regimewechsel
(Residuenbetrag oszilliert 30 Schritte in [0,5, 1,5], dann 20 Schritte in
[7,5, 8,5]) zeigt den Mechanismus real wirksam: in den ersten 10 Schritten
nach dem Wechsel unterdeckt die feste Referenz deutlich (≥5/10 Fehltreffer),
während ACI innerhalb weniger Fehltreffer reagiert und nachweislich
schneller erholt (strikter quantitativer Vergleich, nicht nur beobachtet).
Ein zweiter Test (`check_no_lookahead_prefix_replay`) bestätigt: alle drei
Methoden sind exakt kausal — ein Präfix-Replay reproduziert identische
Entscheidungen für die überlappenden frühen Versuche.

**Ergebnis auf echten Daten** (nominell 80%, `alpha_target=0,2`, Details:
[docs/adaptive_interval_calibration.md](docs/adaptive_interval_calibration.md)):
Energiebilanz (n=40 je Prädiktor/Methode) erreicht mit dieser SYMMETRISCHEN
Betrags-Quantil-Konstruktion 70-85% Abdeckung — deutlich besser als die
52,5% der ursprünglichen LOO-Konstruktion (signierte lo/hi-Quantile;
methodisch verschieden, nicht direkt vergleichbar, beide ehrlich berichtet).
Keine der drei Methoden dominiert hier klar. COVID-Renewal (n=19):
`persistence` erreicht 0% Abdeckung bei ALLEN DREI Methoden — die
Residuen wachsen im 2020-Exponentialfenster monoton, sodass kein aus der
Vergangenheit gebautes Quantil je aufholen kann; das ist eine Grenze jeder
reinen Residuen-Quantil-Kalibrierung (adaptiv oder nicht), kein Fehler der
Rekursionen — ehrlicher Schluss: dieser Prädiktor braucht ein strukturell
anderes Unsicherheitsmodell (Priorität 2), keinen besseren Kalibrierungs-
Wrapper. Bei den anderen beiden COVID-Prädiktoren liegen alle drei
Methoden dicht beieinander; `n=19` ist zu klein für eine belastbare
Unterscheidung.

## Paket 2 — Dynamik vs. Messprozess (2026-09-24, COVID-Teil)

Astras Vorschlag benannte drei Beobachtungsprozess-Bausteine: Meldeverzug,
Wochentagseffekte, Überdispersion. **Bewusste Scope-Grenze:** ein echtes
Meldeverzug-Modell braucht eine Report-Datum×Episoden-Datum-Matrix
("Meldedreieck"); die OWID/JHU-Tagesreihe liefert nur EINEN bereits
finalen Zählwert pro Kalendertag — kein solches Matrix-Datum ist
verfügbar. Meldeverzug bleibt daher explizit UNMODELLIERT; nur die beiden
Bausteine, die die vorhandenen Daten tatsächlich tragen, werden ergänzt.

Neues Modul `validation/covid_latent_renewal_observation.py` (Milestone
56), verifiziert in `verify_covid_latent_renewal_observation.py`
(3/3 Checks). Neue öffentliche Funktion `scoring_rules
.neg_binom_prediction_interval` (additive Ergänzung, spiegelt die
bestehende `poisson_prediction_interval`).

**Isolierter Vergleich, Astras Vorgabe folgend** ("Alte und neue Varianten
auf denselben festgelegten Prognoseursprüngen vergleichen"): dieselbe
Renewal-Gleichungs-Punktprognose (`_covid_renewal_predictor_factory`,
UNVERÄNDERT) an denselben Ursprüngen/Horizonten wie
`run_covid_renewal_rolling_origin_backtest`. Nur die Beobachtungsschicht
ändert sich:

- **ALT:** Punktprognose direkt als Poisson-Mittelwert für den ROHEN
  Tageszählwert.
- **NEU:** dieselbe Punktprognose × ein gefitteter Wochentag-Meldefaktor,
  als Mittelwert einer Negativ-Binomial-Verteilung (Dispersion auf Calib
  gefittet).

Wochentag-Faktor und Dispersion werden EINMALIG, auf den Tagen strikt VOR
dem ersten ausgewerteten Ursprung, gefittet — vollständig
Out-of-Sample bezüglich jedes bewerteten Versuchs; als Referenzmittelwert
dient die bereits etablierte, nicht-zirkuläre vorwärtsverzögerte
7-Tage-Mittel-Funktion (`covid_observation_model._lagged_means`).

**Ergebnis** (18 Calib-Tage, 42 bewertete Versuche, Details:
[docs/covid_latent_renewal_observation.md](docs/covid_latent_renewal_observation.md)):

| | ALT (Poisson) | NEU (Wochentag × NB) |
|---|---:|---:|
| Mittlerer Log-Score (kleiner = besser) | 1387,5 | **11,8** |
| Empirische Abdeckung (nominell 80%) | 2,4% | **73,8%** |

Ein deutlicher, unzweideutiger Sieg der NEUEN Variante — und ein
eindrückliches Beispiel für Astras Kernpunkt: ein erheblicher Teil der
zuvor beobachteten COVID-Unterdeckung (26,3% pooled, Priorität 0/1) war
nie ein Dynamikproblem. Die Renewal-Gleichung selbst ist zwischen ALT und
NEU UNVERÄNDERT; ihre Ausgabe naiv als Poisson-Mittelwert für einen
wochentagsgeprägten, überdispersen Rohwert zu behandeln erzeugte die
katastrophale Fehlkalibrierung. **Caveat:** die konkreten Wochentag-Werte
stammen aus nur ~2,5 Wochen früher, länderübergreifend aggregierter
2020-Daten — der prädiktive Nutzen ist real und direkt an Holdout-Daten
gemessen, die SPEZIFISCHE inhaltliche Deutung ("Mittwochs wird weltweit
untererfasst") sollte daraus nicht überinterpretiert werden.

**Nicht behoben:** `persistence`s 0%-Abdeckung (Priorität 1) bleibt
bestehen — deren Punktprognose (letzter bekannter Wert) ist im
Exponentialwachstum strukturell der falsche Mittelwert, unabhängig von der
Beobachtungsschicht darum herum.

**Energiebilanz-Teil zurückgestellt:** Astras zweiter Priorität-2-Vorschlag
(konsistente Temperaturreferenz, Anfangszustände beider Schichten,
zusätzliche Beobachtungsgröße wie Wärmeinhalt für die Energiebilanz)
erfordert entweder neue Datensätze (Ozean-Wärmeinhalt) oder eine größere
Restrukturierung des bestehenden Fits — zurückgestellt zugunsten des
COVID-Teils, der mit den bereits vorhandenen Daten direkt umsetzbar war.
Als offener Punkt für eine spätere Runde vermerkt.

## Paket 3-5

Werden nacheinander begonnen. Jeweils eigener Abschnitt mit Umsetzungsdatum, Ergebnis und Verifikationsstand, analog zu den Paketen in `MECHANISTIC_VALIDATION_ROADMAP.md`.
