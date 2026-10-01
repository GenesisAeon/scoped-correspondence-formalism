# SCF — Geltungsbereiche, Komposition und belastbare Evidenz — Roadmap (2026-10-01)

Antwort auf [`SCF_SCOPE_COMPOSITION_EVIDENCE_IMPLEMENTATION_PLAN.md`](prompts/Answers/nicht_stationäre_Treiber/SCF_SCOPE_COMPOSITION_EVIDENCE_IMPLEMENTATION_PLAN.md)
(27. September 2026, geprüfter Referenzcommit `4a7ed38640ac7d393017eb5556291c879c3bceac`).
Entwurfsentscheidungen (Pfade, Ergebnisachsen, JSON-Regeln, Budgets):
[`docs/scope_composition_design.md`](docs/scope_composition_design.md).

Johanns Auftrag (2026-09-27, Direktauftrag im Plan selbst, Abschnitt 1;
bestätigt 2026-10-01: „arbeite das Schritt für Schritt ab“): ein Paket pro
Commit, Dokumentation und gezielte Positiv-/Negativprüfungen je Paket,
bisherige Prüfungen dieses Plans sowie volle Regression und Linkprüfung
nach `CLAUDE.md` vor jedem Commit — dieselbe Disziplin wie bei den G0–G7-,
C0–C7- und H0–H7-Serien.

**Arbeitsweg dieser Serie:** Die J-Pakete werden auf dem Branch
`j-series` in einem isolierten Git-Worktree umgesetzt und dorthin
gepusht (nicht direkt auf `master`); die Übernahme nach `master` ist
Johanns Entscheidung. Eine erste Vorbereitung von J0 entstand am
2026-10-01 in einer anderen Session ohne Commit-Möglichkeit; ihr Inhalt
wurde hier geprüft, ergänzt und korrigiert (siehe „Gegenüber der
Vorbereitung geändert“), nicht ungeprüft übernommen.

## Pakete

| Phase | Paket | Inhalt | Abhängigkeit | Status |
|---|---|---|---|---|
| A | J0 | Bestandsaufnahme, Roadmap, Kontrollfallregister | keine | ✅ erledigt (dieser Commit) |
| A | J1 | Gepaarte Prognosevergleiche (DM/HAC) | J0 | ⬜ offen |
| A | J2 | Dimensionen, Einheiten, Buckingham-Π | J0 | ⬜ offen |
| A | J3 | Metamorphe Prüfungen, Fehlermutationen | J1/J2 | ⬜ offen |
| B | J4 | Bereichsverträge, Verfeinerung, Komposition | J2 | ⬜ offen |
| B | J5 | Exakte Intervallnachweise | J4 | ⬜ offen |
| C | J6 | Begrenzte strukturelle Identifizierbarkeit | J2/J4 | ⬜ offen |
| C | J7 | Gemeinsame Sensitivität (Sobol) | J1/J6 | ⬜ offen |
| C | J8 | Gewichtetes Split Conformal | J1/J2 | ⬜ offen |
| D | J9 | Endliche SCMs, interventionelle Abstraktion | J4 | ⬜ offen |
| D | J10 | Geprüfte Standardisierung/Transport | J9 | ⬜ offen |
| E | J11 | Vorhandene Reduktionsschranken als Verträge | J4/J5 | ⬜ offen |
| E | J12 | CLI, Fähigkeitsbilanz, Abschlussregression | alle | ⬜ offen |

Geplante Reihenfolge: J0 → J1 → J2 → J3 (Basissatz) → J4 → J5 → J11 → J6
→ J7 → J8 → J9 → J10 → J12. J11 wird nach J5 vorgezogen, wie Plan §4
ausdrücklich erlaubt: es braucht nur J4/J5 und schließt den Kern
(Komposition + Bereichsnachweis + vorhandene Reduktionsschranken) zu einem
durchgehenden Strang. Kleinster eigenständig wertvoller Meilenstein:
J0–J5. Wird ein Paket zu groß, wird es in Unterpakete mit eigenem Status
geteilt, nicht stillschweigend verkleinert (Plan §4).

## J0 — Bestandsaufnahme und reproduzierbarer Start (erledigt)

### Arbeitsstand und Umgebung (Plan §6, Schritt 1)

- Start-Commit: `4a7ed38640ac7d393017eb5556291c879c3bceac` auf `master`
  (= `origin/master`), **identisch mit dem Referenzcommit des Plans** —
  keine Code-Drift zwischen Plan und Arbeitsstand.
- Vorhandene Änderungen im Haupt-Checkout erhalten (nur unversionierte
  Plan-/Review-Eingänge, keine geänderten Tracked-Dateien); J-Arbeit
  läuft in einem separaten Worktree auf Branch `j-series`.
- Umgebung: Python 3.11.9, NumPy 2.4.6, SciPy 1.15.3, Windows 10
  (10.0.19045). `pyproject.toml`: `requires-python >=3.10`,
  Laufzeitabhängigkeiten nur `numpy`, `scipy`.

### Beilage geprüft

`SCF_SCOPE_COMPOSITION_EVIDENCE_CONTROL_CASES.zip`: alle vier SHA-256-
Summen aus `SHA256SUMS.txt` stimmen; der darin enthaltene Plan ist
bytegleich mit der eingecheckten Plandatei. Frischer Lauf von
`verify_plan_control_cases.py`: **23/23**, Ergebnis-JSON identisch mit
dem mitgelieferten `control_results.json`.

### Vorhandene APIs bestätigt (Plan §6, Schritt 2 — Code direkt geprüft)

Alle Zeilen am Start-Commit per `grep` gegen den Quelltext geprüft
(Pfade relativ zu `src/scoped_correspondence/`):

| Baustein | Datei:Zeile | Bestätigt |
|---|---|---|
| `ModelRef`, `StateMap`, `TimeMap`, `Scope`, `Correspondence` | `correspondence/contract.py:26,36,48,64,113` | ✅ |
| `Scope.contains` (Punkt-Mitgliedschaft, kein Universalnachweis) | `correspondence/contract.py:72` | ✅ |
| `Correspondence.t4_composition_residual` | `correspondence/contract.py:304` | ✅ |
| `ApproximationCertificate`, `verify_approximate_simulation` | `correspondence/approximation.py:55,87` | ✅ |
| `check_controlled_correspondence` | `correspondence/controlled_markov.py:149` | ✅ |
| `transient_reduction_bound`, `stationary_reduction_bound`, `compare_to_propagated_error_bound` | `closure/error_bounds.py:212,339,404` | ✅ |
| `parameter_scaling_invariance`, `identifiability_jacobian_rank` | `identifiability/core.py:222,255` | ✅ |
| Fisher-Information / Profil-Likelihood (Plan §3, Zusatzprüfung) | `identifiability/fim_sloppiness.py`, `identifiability/profile_likelihood.py`, `identifiability/profile_likelihood_nlp.py` | ✅ vorhanden, bleiben getrennte Ergebnisarten (J6) |
| Lineare Reservoirs (`reservoir_step`, `LinearReservoirSpec`, …) | `dynamics/linear_reservoirs.py:100,242` | ✅ |
| `rolling_origin_backtest`, `RawHorizonPrediction`, `raw_predictions_by_horizon_step` | `validation/rolling_origin.py:70,228,238` | ✅ |
| `interval_score`, Poisson-/NB-Scores | `validation/scoring_rules.py:80,113,153` | ✅ |
| `calibrate_split_conformal`, `predict_interval`, `assert_disjoint_calib_holdout`, `SplitConformalReport` | `validation/conformal.py:43,112,125,157` | ✅ |
| Adaptive Kalibrierung (ACI/PID, Plan §3, Zusatzprüfung) | `validation/adaptive_interval_calibration.py:154,173,376` | ✅ Vergleichsanschluss für J8 |
| `evaluate_baselines_on_holdout`, `distance_inclination_sensitivity(_mode_b)` | `validation/galaxy_pilot.py:421,642,712` | ✅ |
| `AssumptionSpec`, `FiniteDomainSpec`, `ClaimSpec`, `ClaimReport` | `epistemic/records.py:78,104,133,149` | ✅ |
| `report_to_json`, `report_to_markdown` | `epistemic/reporting.py:42,68` | ✅ (Befund B2 unten) |
| `_EXPLICIT_CATEGORY` | `scripts/run_verification_suite.py:64` | ✅ |
| `docs/real_data_provenance.md` | — | ✅ |

Kein im Plan referenzierter Baustein war falsch benannt oder fehlend.

### J-C01–J-C23 unabhängig hergeleitet (Plan §6, Schritt 3)

Drei getrennte Evidenzquellen, **vor** jeder Implementierung:

1. **Von Hand** aus dem Plantext hergeleitet (alle 23), bevor das
   Plan-Skript gelesen wurde.
2. **Eigenes Skript** [`verification/plan_controls/j_series_independent_controls.py`](verification/plan_controls/j_series_independent_controls.py):
   alle 23 Gruppen, nur `Fraction`/`int`/`bool`, kein SCF-Import, wo
   möglich mit einem *anderen* Algorithmus als die Beilage (siehe
   Spalte). Ergebnis: **23/23**,
   [`j_series_independent_controls_results.json`](verification/plan_controls/j_series_independent_controls_results.json).
   Es ist absichtlich kein `verify_*.py` und wird vom Suite-Runner nicht
   als Produktionsprüfung gezählt (Plan §19.1).
3. **Beilage** des Plans (23/23, siehe oben).

| Fall | Paket | Ergebnis (bestätigt) | Eigener Weg / Zusatzprüfung |
|---|---|---|---|
| J-C01 | J1 | $\bar d=1/2$, $\gamma_0=5/4$, $\gamma_1=5/16$, $\hat V=25/16$, SE $5/8$, DM $4/5$ | exakte Wurzelprüfung $SE^2=\hat V/n$; Vorzeichenumkehr bei Tausch; Verlustskalierung ×3 → $\hat V$×9, DM unverändert |
| J-C02 | J1 | Holm $(0{,}03;0{,}06;0{,}06)$ | Schrittverfahren mit Monotonisierung |
| J-C03 | J2 | Rang 2, Nullität 1, $v=(2,-1,1)$; $g/G$: $M L^{-2}$ | auch $(-4,2,-2)$ als gleichwertige Basis |
| J-C04 | J2/J3 | Reservoir invariant; $\rho r=12$ | **exakt** über $q/k=5/2$ und $kt=4/5$ (Beilage: Float mit Toleranz); Negativkontrolle $\rho r^2$ nicht invariant |
| J-C05 | J4 | $D_{12}=[0,1/2]$; $x=3/4\mapsto3/2\notin D_2$ | — |
| J-C06 | J4 | $c_1=c_2=1/2$, zusammengesetzt $1/4$; $H_{12}=2$ | Zeitfaktor aus Koeffizientenvergleich $DT\,f=a\,(f\circ T)$ |
| J-C07 | J4 | Flussgrenze $1/2$; $r_{12}=6x+6$, Schranke 9 am Rand erreicht, $r_{12}(1/4)=15/2$ | T4-Formel und direkte Berechnung an vier Punkten identisch |
| J-C08 | J4 | Verfeinerung vorwärts ja, rückwärts nein | — |
| J-C09 | J5 | max. natürliche Obergrenze $33/128$ ⇒ $p\le13/50$ bewiesen; $x=1/2$ widerlegt $6/25$ | 64 Teilintervalle exakt |
| J-C10 | J5 | $x-x$: $[-1,1]$; $1/x$ auf $[-1,1]$ nicht definiert | — |
| J-C11 | J6 | Rang 1, Nullvektor $(1,-1)$ | Zeilenraumtest: $\theta_1+\theta_2$ identifizierbar, $\theta_1$ nicht |
| J-C12 | J6 | $y(0)=15$, $\dot y(0)=-30$, $k=2$, $cx_0=15$; $\lambda=7$: $(3/7,35)$ | — |
| J-C13 | J6 | Faser $\{-2,2\}$; lokal eindeutig bei 2; auf $\theta>0$ nur 2 | — |
| J-C14 | J7 | $X+2Y$: $V=5/12$, $S=S_T=(1/5,4/5)$; $XY$: $V=7/144$, $S=(3/7,3/7)$, $S_T=(4/7,4/7)$, Interaktion $1/7$ | **exakte Polynomintegration** der bedingten Erwartungen; konstante Ausgabe: Varianz 0 |
| J-C15 | J8 | Quantile $3,+\infty,2$ | Mutante „Testpunktmasse weglassen“ liefert im Fall 2 fälschlich 3; gemeinsame Gewichtsskalierung ×7 ändert nichts |
| J-C16 | J8 | ungewichtet $40951/100000$; gewichtet 1; unbeschränkt $89991/100000$ | volle 32-Fall-Enumeration, Gesamtmasse 1 geprüft |
| J-C17 | J8 | Quantil 0, Abdeckung 0 | — |
| J-C18 | J9 | Beobachtung gleich; $P(Y=1\mid do(X=1))$: $1$ vs. $1/2$; TV $1/2$ | — |
| J-C19 | J9 | 5 exakte Eingriffe, surjektiv, ordnungserhaltend; Erweiterung TV $1/2$ | **Befund B3** unten |
| J-C20 | J10 | Ziel $3/4,1/4$, Effekt $-1/2$; Quelle $1/2,1/2$ | Supportkontrolle |
| J-C21 | J10 | Zielwert $1$ vs. $1/2$ bei identischer verfügbarer Information | alle Quellbeobachtungen und -experimente geprüft |
| J-C22 | J11 | $\lVert Q-P\rVert_\infty=1/5$; $p_0P^2=(33/50,17/50)$, $p_0Q^2=(11/20,9/20)$; L1 $11/50\le2/5$; TV $11/100\le1/5$ | Zeilensummen = 1 geprüft |
| J-C23 | J10 | Collider: marginal getrennt, durch $C$ oder $D$ geöffnet; $S\perp Y\mid X,Z$ ja, $\mid X$ nein | **Pfadaufzählung** statt Moralisierung |

### Befunde aus J0

- **B1 — Plan-Lücke J-C04:** Plan §8 nennt für die Halo-Umparametrisierung
  keine Zahlen; der Registerwert $\rho r=12$ ist nur mit den Eingaben der
  Beilage ($\rho=6,r=2,\lambda=3$) reproduzierbar. Für J2/J3 werden diese
  Eingaben übernommen und als Beilagenwerte gekennzeichnet.
- **B2 — Nichtstandard-JSON-Risiko:** `epistemic/reporting.report_to_json`
  serialisiert mit der `json.dumps`-Voreinstellung `allow_nan=True`; ein
  Float-`inf`/`nan` würde als `Infinity`/`NaN` ausgegeben (Plan §5.2
  verbietet das). Ob bestehende Berichte je solche Werte enthalten, wurde
  nicht untersucht. Konsequenz für J-Berichte: explizite Marker statt
  Float-Unendlich und `allow_nan=False` (siehe
  [`docs/scope_composition_design.md`](docs/scope_composition_design.md) §2.3).
- **B3 — J-C19 schärfer als im Plan formuliert:** Die absichtlich
  scheiternde Erweiterung $do(X_1=1)\mapsto do(Z=1)$ verletzt nicht nur
  die Verteilungsgleichheit (TV $1/2$), sondern **auch die
  Ordnungserhaltung**: $do(X_1=1)\le do(X_1=1,X_2=1)\mapsto do(Z=0)$,
  aber $do(Z=1)\not\le do(Z=0)$. Die alternative Zuordnung
  $do(X_1=1)\mapsto$ Nichtstun besteht dagegen **beide** Prüfungen
  (mikro bleibt $Z$ fair, $Y=Z$). Das ist ein konkreter Zeuge für die
  Planaussage, dass nicht jede andere Abbildung scheitern muss, und wird
  in `verify_causal_abstraction.py` (J9) als eigene Assertion
  aufgenommen. Die Prüfungen von Ordnung und Verteilung bleiben getrennte
  Ergebnisfelder.
- **B4 — Bestätigung der Planstelle zu `q=+inf`:**
  `validation/conformal.py:65` beschreibt `+inf` als „empty finite
  interval“. Das resultierende Vorhersageintervall ist die ganze reelle
  Gerade, kein leeres Intervall. Korrektur beim J8-Anschluss (Plan §14).

### Bestehende Tests und Laufzeiten (Plan §6, Schritt 4)

Tatsächlich am Start-Commit `4a7ed38` ausgeführt (2026-10-01, Umgebung
wie oben), kein Zähler aus früheren Gesprächen übernommen:

- `python scripts/run_verification_suite.py --category all`:
  **106/106** `verify_*.py` bestanden, 0 übersprungen, 0 fehlgeschlagen;
  Gesamtlaufzeit **11 min 50 s** (seriell, je Skript Timeout 120 s).
  `verify_sparc_real_local.py` lief dabei echt (lokale SPARC-Dateien
  vorhanden), wurde also nicht als „übersprungen“ gezählt.
- `--category links`: 221 Markdown-Dateien, 324 relative Links geprüft,
  **0 kaputt** (516 externe Links nur gezählt).
- Die Suite schreibt die eingecheckten `verification/*_results.json` neu.
  Am Start-Commit änderten sich dabei **ausschließlich** Zeitstempel und
  absolute Datenpfade (geprüft per `git diff`, kein einziger Messwert
  verändert). Weil die Pfade im Worktree auf
  `.claude/worktrees/j-series/…` zeigen würden, werden solche reinen
  Zeitstempel-/Pfadauffrischungen in der J-Serie **nicht** mitcommittet;
  eingecheckt werden nur die Ergebnisdateien neuer bzw. inhaltlich
  geänderter Prüfungen.
- Remote-CI (`.github/workflows/verify.yml`) für den Start-Commit
  `4a7ed38`: per `gh run list --commit` abgefragt — Workflow `verify`,
  `completed`/**`success`** (Lauf vom 2026-09-27T10:00:12Z).

### Pfade, Ergebnisfelder, Abhängigkeiten (Plan §6, Schritt 5)

Festgelegt in [`docs/scope_composition_design.md`](docs/scope_composition_design.md):
neue Teilpakete `assurance/`, `dimensions/`, `causal/`; Wiederverwendung
der Vokabulare aus `epistemic/records.py`; ein kleines
`assurance/records.py` (`ProofReport`, `ClaimBundle`) nur für das, was
`ClaimReport` als Bericht über endliche Domänen nicht abbilden darf
(kontinuierliche Boxen, Restboxen, „nicht definiert“). Keine neue
Laufzeitabhängigkeit.

### Quellenstatus (Plan §21)

Die Quellen S01–S16 belegen Verfahrensklassen, nicht die konkreten
Testparameter (die sind oben unabhängig hergeleitet). In J0 wurden sie
nicht erneut einzeln abgerufen; Status daher: **„laut Plan geprüft
(27.09.2026), in J0 nicht erneut verifiziert“**. Jedes Paket prüft die
für sein Verfahren tragende Quelle bei Implementierung erneut gegen die
tatsächlich programmierte Variante (Plan §21, letzter Absatz) und
vermerkt das Ergebnis in seinem Abschnitt hier.

| Quelle | Paket | Status |
|---|---|---|
| S01–S04 (DM, Diebold 2015, Newey–West, Holm) | J1 | laut Plan geprüft; Neuprüfung in J1 |
| S05 (Buckingham) | J2 | laut Plan geprüft; Neuprüfung in J2 |
| S06 (metamorphes Testen) | J3 | laut Plan geprüft; Neuprüfung in J3 |
| S07 (Contracts for System Design) | J4 | laut Plan geprüft; nur funktionaler Spezialfall |
| S08 (JuliaIntervals) | J5 | laut Plan geprüft; kein Pflichtimport |
| S09–S10 (SIAN, StructuralIdentifiability.jl) | J6 | laut Plan geprüft; optional |
| S11–S12 (Saltelli 2010, Kucherenko 2012) | J7 | laut Plan geprüft; Neuprüfung in J7 |
| S13 (Tibshirani et al. 2019) | J8 | laut Plan geprüft; Neuprüfung in J8 |
| S14 (Rubenstein et al. 2017) | J9 | laut Plan geprüft; Neuprüfung in J9 |
| S15 (Pearl & Bareinboim 2014) | J10 | laut Plan geprüft; Neuprüfung in J10 |
| S16 (Michel & Siegle 2024) | J11 | laut Plan geprüft; Neuprüfung in J11 |

### Gegenüber der Vorbereitung geändert

Die vorbereitende Session hatte die Beilage ausgeführt und vier Fälle
(J-C01, J-C16, J-C19, J-C23) eigenständig nachgerechnet. Ergänzt bzw.
korrigiert wurde:

- Alle 23 statt 4 Fälle eigenständig hergeleitet (Plan §1 und §6:
  „Leite alle Kontrollgruppen J-C01 bis J-C23 selbst her“).
- Befunde B1–B4 neu.
- `docs/scope_composition_design.md` neu (Plan §6, Dateien).
- Umgebung, Teststand und Laufzeiten tatsächlich erhoben statt offen
  gelassen.
- Die Vorbereitungsdateien (`J0_handoff/`) werden nicht eingecheckt: ihr
  Inhalt ist durch die Beilage (eingecheckte ZIP) und das vollständigere
  eigene Skript unter `verification/plan_controls/` ersetzt.

### Explizite Liste optionaler Arbeiten (Plan §22, nicht Pflichtumfang)

Validierte transzendente Funktionen und ODE-Flüsse; allgemeine rationale
ODE-Identifizierbarkeit (SIAN-/SciML-Adapter); vollständiges ID/sID für
Transportabilität; kontrafaktische Abstraktion; Sensitivität bei
abhängigen Eingängen; allgemeine Driftgarantien jenseits Covariate Shift;
hierarchische Galaxienpopulation; zusätzliche Informationskriterien/
Bayesvergleiche; allgemeine kategoriale Infrastruktur. Diese bleiben
offen festgehalten, nicht stillschweigend fallen gelassen.

### Abnahme (Plan §6)

- [x] Schnittstellentabelle am aktuellen Code bestätigt
- [x] Alle 23 Kontrollgruppen dokumentiert und eigenständig hergeleitet
- [x] Quellenstatus pro Referenz (Tabelle oben, ehrlich als „nicht erneut
      verifiziert“ markiert)
- [x] Paketstatus
- [x] Explizite Liste optionaler Arbeiten
- [x] Teststand und Laufzeiten am Start-Commit erhoben
- [x] Keine Produktionsmodule in diesem Commit
- CI-Status: Start-Commit grün (siehe oben). Der Remote-CI-Lauf für
  **diesen** J0-Commit ist **unbekannt**, bis er tatsächlich überprüft
  wurde (Plan §6, Abnahme); Ergebnis wird beim nächsten Paket nachgetragen.
