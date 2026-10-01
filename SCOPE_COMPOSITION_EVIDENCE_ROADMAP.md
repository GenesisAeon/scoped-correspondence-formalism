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
| A | J0 | Bestandsaufnahme, Roadmap, Kontrollfallregister | keine | ✅ erledigt |
| A | J1 | Gepaarte Prognosevergleiche (DM/HAC) | J0 | ✅ erledigt |
| A | J2 | Dimensionen, Einheiten, Buckingham-Π | J0 | ✅ erledigt |
| A | J3 | Metamorphe Prüfungen, Fehlermutationen | J1/J2 | ✅ erledigt (Basissatz; Vollsatz in J12) |
| B | J4 | Bereichsverträge, Verfeinerung, Komposition | J2 | ✅ erledigt |
| B | J5 | Exakte Intervallnachweise | J4 | ✅ erledigt |
| C | J6 | Begrenzte strukturelle Identifizierbarkeit | J2/J4 | ✅ erledigt |
| C | J7 | Gemeinsame Sensitivität (Sobol) | J1/J6 | ⬜ offen |
| C | J8 | Gewichtetes Split Conformal | J1/J2 | ⬜ offen |
| D | J9 | Endliche SCMs, interventionelle Abstraktion | J4 | ⬜ offen |
| D | J10 | Geprüfte Standardisierung/Transport | J9 | ⬜ offen |
| E | J11 | Vorhandene Reduktionsschranken als Verträge | J4/J5 | ✅ erledigt |
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
- CI-Status: Start-Commit grün (siehe oben). J0-Commit `22854bd` auf
  `j-series`: Remote-CI `verify` **success** (nachgetragen in J1).

## J1 — Gepaarte Prognosevergleiche (erledigt)

Dokumentation: [`docs/forecast_comparison.md`](docs/forecast_comparison.md).
Code: `validation/forecast_comparison.py` (Kern),
`validation/forecast_comparison_pilot.py` (NOAA-Realdatenpilot).

- **Paarung:** `pair_raw_predictions` verbindet `RawHorizonPrediction`
  über `(origin, step)`; fehlende Partner und nicht endliche Werte werden
  mit Grund gezählt, abweichende Beobachtungen unter demselben Schlüssel
  sind Eingabefehler.
- **Inferenz nur bei deklarierter Anwendbarkeit:**
  `InferenceApplicability` (Begründungstext, deklarierte Mindestlänge
  ohne Standardwert, verschachtelt/Strukturbruch/Ordnung) — sonst
  bleiben alle Inferenzfelder leer, der deskriptive Vergleich bleibt.
  `degenerate_variance` statt `p=0`. Ergebnisse je
  `(series_id, horizon)`, nie gepoolt oder verkettet.
- **Holm** nur auf vorab deklarierten Familien
  (`incomplete_family`/`not_predeclared` statt stiller Verkleinerung).
- **Siegerformulierung** ausschließlich über `describe_comparison`
  (Serie/Zeitraum, $n$, Horizont, Verlust, Effektgröße, Inferenzstatus).

Prüfungen:

- `verify_forecast_comparison.py` (math): **14/14** — J-C01 exakt
  ($\hat V=25/16$, SE $5/8$, DM $4/5$), J-C02, Modelltausch,
  Verlustskalierung (exakt $\hat V\cdot c^2$), konstante Differenzen,
  falsche Paarung, fehlende Partner, ungültige Zahlen, Horizonte,
  Serien, Anwendbarkeitsschranken, Lagvalidierung, deklarierte Familie,
  Ergebnissatz + standardkonformes JSON.
- `verify_forecast_comparison_noaa.py` (data): **6/6** — Manifest-Hash,
  vollständige Paarung, Primärergebnis rein deskriptiv, bedingtes
  Ergebnis trägt seine Annahme, mittlere Verluste = bestehendes
  `error_by_horizon_step` (RMSE²), bedingter DM = unabhängige
  NumPy-HAC-Rechnung im Prüfskript (beides relativ $10^{-10}$).
- **Gezielte Mutanten** (temporäre Kopie, nicht im Arbeitsbaum): 6/6
  erkannt — Bartlett-Gewicht entfernt, Degenerationswächter entfernt,
  Anwendbarkeit umgangen, Vorzeichen der Verlustdifferenz vertauscht,
  fehlender Partner still verworfen, Beobachtungsabweichung ignoriert.
  **Korrektur während J1:** Der erste Test für konstante Differenzen
  erzeugte bitgleiche Gleitkommadifferenzen ($\hat V=0$ exakt) und hätte
  den Wächter nur über einen `ZeroDivisionError` „geprüft“. Ersetzt durch
  mathematisch konstante, numerisch in den letzten Bits schwankende
  Differenzen; ohne Wächter entstünde dort DM $\approx1{,}4\cdot10^{15}$
  — jetzt durch eine inhaltliche Assertion erkannt.

**Realdatenpilot (Design vorab im Code fixiert):** NOAA-Jahresanomalie,
30-Jahre-Trend (A) vs. Persistenz (B), jährliche Ursprünge ab 1960,
$h=1$ ($n=65$) und $h=5$ ($n=61$), quadratischer Fehler. **Primär
deskriptiv** (Stationarität der Verlustdifferenzen nicht belegt): A hat
bei beiden Horizonten den geringeren mittleren Verlust (Differenz
$-0{,}00185$ bzw. $-0{,}0130$ °C²). **Bedingt** unter *angenommener*
Stationarität: $h=1$ DM $-1{,}04$, $p=0{,}30$ (nicht unterscheidbar —
keine Gleichwertigkeit); $h=5$ DM $-3{,}64$, $p=0{,}00027$. Keine
vorab deklarierte Familie, daher keine Mehrfachtestkorrektur.

Quellen S01–S04: DOIs/Links lösen auf (geprüft 2026-10-01); kein
Volltextaudit behauptet.

Regression mit J1: `--category all` **108/108** bestanden (106 bisherige
+ 2 neue), 0 übersprungen, 11 min 33 s; `--category links` 0 kaputt.
Aufgefrischte Ergebnis-JSONs bestehender Prüfungen enthielten nur
Zeitstempel/Pfade sowie einen Link-Zähler (201→207), der lediglich die
neu hinzugekommenen Docs widerspiegelt — nicht mitcommittet.

## J2 — Dimensionen, Einheiten und Buckingham-Π (erledigt)

Dokumentation: [`docs/dimensional_correspondence.md`](docs/dimensional_correspondence.md).
Code: neues Teilpaket `dimensions/` (`core.py`, `pi_groups.py`).

- `Dimension` (rationale Exponenten über SI-Basis), `Unit` (Skala,
  Offset für affine Skalen), `QuantitySpec` mit optionaler semantischer
  Größenart; `check_dimension` über validierte Ausdrucksbäume (kein
  Parser, kein `eval`); `convert`, `multiplicative_scale` (lehnt affine
  Einheiten ab), `rescale_for_base_unit_change`.
- `buckingham_pi_basis`: exakter Rang und rationaler Nullraum, primitive
  ganzzahlige Basis; Vergleiche nur über `same_pi_span`.

Prüfungen: `verify_dimensional_analysis.py` (math) **11/11** — J-C03
(Pendel: Rang 2, Spann $(2,-1,1)$; $g/G$: $ML^{-2}$), J-C04 Reservoir
(Jahr→Tag exakt, Anschluss `reservoir_step` relativ $10^{-14}$) und Halo
($\rho r=12$ erhalten, $\rho r^3$ nicht), Addition verschiedener
Dimensionen, exp/log-Argumente, rationale Exponenten,
singuläre/leere/vollrangige Matrizen, Basiswechsel über den Spann,
Galaxiengrößen ($V,r,G,M,a_0$: Nullität 2, Spann
$\{V^2r/GM,\ a_0r/V^2\}$), Einheiten inkl. °C absolut vs. Differenz,
Energie vs. Drehmoment als semantische Warnung, abstrakte dimensionslose
SCF-Größe. **Gezielte Mutanten:** 9/9 durch inhaltliche Assertions
erkannt. Eine anfangs enthaltene inhaltsleere Assertion
(`not hasattr(eta, "unit")`, prüft nur das Klassendesign) wurde vor dem
Commit entfernt, um keinen Prüfumfang vorzutäuschen.

Quelle S05: DOI löst auf (link.aps.org, geprüft 2026-10-01).

Regression mit J2: `--category all` **109/109** bestanden, 0
übersprungen, 11 min 50 s; `--category links` 0 kaputt. Aufgefrischte
Ergebnis-JSONs bestehender Prüfungen: nur Zeitstempel/Pfade/Link-Zähler,
nicht mitcommittet. Remote-CI für J1-Commit `e2e6c49`: `verify`
**success**.

## J3 — Metamorphe Prüfungen und gezielte Fehlermutationen (erledigt, Basissatz)

Dokumentation: [`docs/metamorphic_validation.md`](docs/metamorphic_validation.md).

- `verify_metamorphic_relations.py` (math) **6/6**: MR1 Einheitenwechsel
  (50 exakte Zufallsfälle, Anschluss `reservoir_step`), MR2 gleichzeitige
  Permutation von Zuständen/Klassen/Aktionen in
  `check_controlled_correspondence` (exakte und nicht exakte Fälle), MR3
  Identität und Assoziativität über `t4_composition_residual` inkl. der
  T4-Identität selbst, MR4 A/B-Tausch, MR5 Conformal-Permutation und
  -Skalierung. **Ausstehend und ausdrücklich ausgewiesen:** MR6 (J8),
  MR7 (J7), MR8 (J9).
- `scripts/run_targeted_mutations.py`: explizites Mutantenregister, Läufe
  nur auf temporärer Kopie, Hash-Nachweis des unveränderten Arbeitsbaums,
  Ausgänge `killed` (`assertion`/`error`) / `survived` / `invalid` /
  `timeout` / `equivalent_or_unresolved`.
- `verify_targeted_mutation_runner.py` (math) **1/1**: Selbsttest aller
  Ausgangsklassen an einem Wegwerf-Spielrepository.
- **Mutationsbericht** [`verification/targeted_mutations_report.json`](verification/targeted_mutations_report.json):
  **19/19** erkannt, alle durch Assertions — davon 4 planpflichtige
  Klassen am Bestandscode (T4-Zeitfaktor, Conformal-Testpunktmasse
  $n+1\to n$, TV/L1-Faktor ½, umgedrehte Ungleichung), 7 J1, 8 J2.
  Lipschitzfaktor und Scope-Verträglichkeit werden mit J4 aktiviert.

**Drei Korrekturen innerhalb von J3, vor dem Commit:**

1. MR3 prüfte zunächst nicht die T4-Identität (`direct = composed`)
   selbst; der als Ziel eingetragene T4-Mutant wäre von MR3 nicht erfasst
   worden. Ergänzt.
2. **Runner-Fehler „veralteter Bytecode“** (durch den Selbsttest
   gefunden): Gleich lange Mutationen innerhalb derselben Sekunde
   bestanden Pythons mtime+Größe-Prüfung, ausgeführt wurde der
   unmutierte Bytecode — ein falsches „überlebt“. Behoben mit
   `PYTHONDONTWRITEBYTECODE=1`. Der Fehler kann nur falsche Überlebende
   erzeugen; frühere „erkannt“-Ergebnisse (J1/J2) bleiben gültig, und der
   Lauf vor dem Fix ergab ebenfalls 19/19.
3. **Runner-Fehler „Einstufung“:** Ältere Prüfskripte melden
   Fehlschläge als JSON statt mit `FAIL`-Zeilen und wurden als Absturz
   gezählt (`verify_correspondence_core.py` meldet den T4-Mutanten als
   fehlgeschlagenes `MIG-COR-T04`). Jetzt: `error` nur bei ungefangener
   Exception.

Quelle S06: DOI löst auf; die HKU-Autorenfassung antwortete mit HTTP 403
(vermutlich Bot-Sperre) — nicht inhaltlich geprüft.

Regression (gemeinsamer Lauf über den Stand mit J3 und J4, beide rein additiv; die
J3-Prüfskripte importieren kein J4-Modul, per `grep` geprüft): `--category all`
**112/112** bestanden, 0 übersprungen, 12 min 7 s; `--category links` 0 kaputt.
Aufgefrischte Ergebnis-JSONs bestehender Prüfungen: nur Zeitstempel/Pfade.

## J4 — Bereichsverträge, Verfeinerung und Komposition (erledigt)

Dokumentation: [`docs/correspondence_contracts.md`](docs/correspondence_contracts.md).
Code: `assurance/records.py` (`ProofReport`, `ClaimBundle`, Adapter zu
`ClaimReport`), `correspondence/domains.py`,
`correspondence/contracts.py`, `correspondence/composition.py`;
`correspondence/contract.py` unverändert.

- Exakte Domänen (`FiniteSet`, `RationalBox`, `HalfspaceSet`,
  `OpaquePredicate` nur punktweise), `certify_subset`, exaktes Urbild
  unter affinen Abbildungen — nicht als Box darstellbare Urbilder bleiben
  symbolisch.
- `check_refinement` (funktionaler Spezialfall); Schnittstellen-
  abweichungen sind `incompatible`, nicht „widerlegt“.
- `compose_correspondences`: Modell-ID/Koordinaten/Einheiten/Uhr müssen
  passen; $D_{12}$ exakt, leer markiert; $c_{12}=c_1c_2$;
  $H_{12}=\min(H_1,H_2/c_1)$; Flussfehler nur mit Lipschitzzertifikat
  inkl. Verbindungsstrecken; Feldresiduum $M\varepsilon_1+A\varepsilon_2$
  getrennt; schwächste Komponentenevidenz bestimmt die Komposition.

Prüfung: `verify_correspondence_contracts.py` (math) **11/11** — J-C05,
J-C06, J-C07, J-C08, inkompatible Zwischenmodelle/Koordinaten/Einheiten/
Uhren/Metriken (auch gleicher Name bei anderer Schnittstelle), leere
Schnittmenge, fehlendes bzw. unvollständiges Lipschitzzertifikat,
Herabstufung bei geschätzten Komponenten, positive/negative Skalen,
Identität, Assoziativität (Abbildungen, Uhren, Horizonte, Scopes exakt
gleich; konstante Schranken hier gleich $11/28$), Domänenklassen,
Berichtsinvarianten und Adapter. **Gezielte Mutanten:** 9/9 durch
Assertions erkannt, darunter die planpflichtigen „Lipschitzfaktor
entfernen“ und „Scope-Verträglichkeit umgehen“ sowie „$\delta_2$
fälschlich mit $c_1$ multipliziert“. Der Gesamtbericht
`verification/targeted_mutations_report.json` steht damit bei **28/28**
(J0–J4), alle durch Assertions; damit sind alle sechs planpflichtigen
Fehlerklassen aus Plan §9 aktiv.

**Korrekturen innerhalb von J4, vor dem Commit:** (a) Zeugenpunkt bei
„Box ⊄ Box“ wählte die Achse über einen Wertvergleich und konnte bei
gleichen Achsengrenzen die falsche Achse treffen — auf Achsenindex
umgestellt. (b) Flussfehlerschranken trugen anfangs keine Evidenzart, ein
numerisch geschätzter Komponentenfehler wäre als „bewiesen“ komponiert
worden — `flow_error_evidence` (Standard `not_evaluated`) ergänzt. (c)
Eine eigene Testerwartung zur Assoziativität setzte $L_3=3/2$ statt
$1/2$ ein; der Code war korrekt ($11/28$), die Assertion wurde
berichtigt.

Quelle S07: DOI und ISTA-Nachweis lösen auf (geprüft 2026-10-01).

Regression: gemeinsamer Lauf mit J3 (siehe dort) — **112/112**, 0 kaputte Links.

## J5 — Nachweise über ganze unterstützte Bereiche (erledigt)

Dokumentation: [`docs/validated_scopes.md`](docs/validated_scopes.md).
Code: `assurance/rational_intervals.py` (exakte rationale
Intervallarithmetik, scharfe gerade Potenzen, Nenner mit 0 → Ausnahme),
`assurance/expressions.py` (validierte Ausdrucksbäume, keine Callbacks,
Dezimalstring vs. exakter Binärwert eines Floats),
`assurance/scope_certification.py` (`certify_bound`,
`certify_abs_bound`, `recheck_certificate`).

Prüfung: `verify_validated_scopes.py` (math) **9/9** — J-C09 (64-Zellen-
Obergrenze genau $33/128$; $p\le13/50$ bewiesen und zertifikatsgeprüft;
$x=1/2$ widerlegt $6/25$; scharfe $1/4$ bleibt unentschieden, nie
widerlegt), J-C10 ($x-x$: $[-1,1]$, keine scharfe Nullschranke; $1/x$ auf
$[-1,1]$: `undefined_on_domain` bei 0), Nenner nahe null in drei Fällen
(echter Gegenpunkt / nur Überschätzung → bewiesen / nie getroffener
Singulärpunkt → unentschieden mit Definitionswarnung), negative
Koeffizienten, wiederholte Variablen, 2-D-Box mit Ober- und Untergrenze,
Manipulation eines Zertifikats (fehlende Box, geschönter Einschluss,
strengere Schranke) wird erkannt, Restboxen bei Budgetende, leere Box,
Eingabevalidierung, und das **J4-Residuum** $r_{12}=6x+6$ aus J-C07 als
Ausdrucksbaum: $|r_{12}|\le9$ auf $[0,1/2]$ bewiesen, Grenze bei $1/2$
erreicht. **Gezielte Mutanten:** 7/7 durch Assertions erkannt.

**Korrektur innerhalb von J5, vor dem Commit:** Eine eigene
Testerwartung („$1/x\le1000$ auf $[-1,1/2]$ bleibt unentschieden“) war
falsch — die Aussage ist für $0<x<1/1000$ tatsächlich verletzt, der Code
fand korrekt einen Gegenpunkt (Wert 2048). Die Prüfung trennt jetzt die
drei Fälle oben ausdrücklich.

Quelle S08: offizielle IntervalArithmetic.jl-Doku erreichbar (HTTP 200);
kein Pflichtimport.

Regression: gemeinsamer Lauf über den Stand mit J5, J11 und J6 (alle additiv; J5-Prüfungen importieren weder J11- noch J6-Module) — `--category all` **115/115** bestanden, 0 übersprungen, 12 min 17 s; `--category links` 0 kaputt.

## J11 — Vorhandene Reduktionsschranken als Verträge (erledigt, vor J6 gezogen)

Dokumentation: [`docs/reduction_contracts.md`](docs/reduction_contracts.md).
Code: `closure/contract_adapter.py`; `closure/error_bounds.py`
unverändert und weiterhin die einzige Reduktionsimplementierung.

- Die bestehende Float-Schranke wird aufgerufen und als
  `floating_point_estimate` berichtet; nur bei exakten Eingaben und
  exakt geprüften Voraussetzungen (Thm 4.3 / 5.3) wird dieselbe
  geschlossene Formel zusätzlich rational ausgewertet und als `proved`
  geführt; bei diskreten exakten Eingaben wird außerdem der tatsächliche
  Fehler exakt berechnet.
- Geprüft: Zeilenkonvention/Orientierung (Hinweis auf Transposition statt
  stiller Korrektur), Formen, $\pi_0$ als Wahrscheinlichkeitsvektor,
  stochastisches Lifting, Anfangsfehler, Uhr/Horizont; TV nur für
  Differenzen von Wahrscheinlichkeitsvektoren.
- `reduction_link` + `observation_link` schließen über die
  J4-Komposition an eine Beobachtungsgröße an (exaktes Hölder-Zertifikat).

**Befund:** Die bestehende `transient_reduction_bound` gibt TV als halbe
L1-Schranke aus, ohne zu prüfen, dass Lifting und $p_0$
Wahrscheinlichkeiten sind. Im Adapter abgefangen; die bestehende Funktion
bleibt unverändert (additive Regel).

Prüfung: `verify_reduction_contracts.py` (math) **8/8** — J-C22 (L1
$11/50\le2/5$, TV $11/100\le1/5$, Float-Funktion stimmt überein),
bestehender echter Reduktionsfall `paper_example_matrices` (3 → 2;
$\lVert\Pi A-AP\rVert_\infty=1/4$, Schranke 1 bei $k=4$, exakter Fehler
darunter) mit vollständigem Vertrag, zusammengesetzter
Beobachtungsanschluss ($f=(0,1,2)$: Schranke 2, exakter
Beobachtungsfehler darunter), inkompatible Uhren und Zwischenzustände,
transponierte Matrix, falsche Lifting-Form, nicht stochastisches Lifting
(L1 ja, TV abgelehnt), exakter Anfangsfehler, CTMC-Fall, Float-Eingaben
nie `proved`. **Gezielte Mutanten:** 7/7 durch Assertions erkannt.

**Korrektur innerhalb von J11, vor dem Commit:** Der Adapter rief die
bestehende Float-Funktion zunächst auch bei bestimmten Strukturverletzungen
auf (Schutzbedingung über Teilstrings der Meldung — zu fragil); bei einer
falschen Lifting-Form führte das zu einer Ausnahme. Jetzt: bei **jeder**
Verletzung kein Aufruf.

Quelle S16: arXiv-Eintrag (HTTP 200) und DOI (Weiterleitung) erreichbar.

Regression: gemeinsamer Lauf über den Stand mit J5, J11 und J6 (additiv; die J11-Prüfung importiert kein J6-Modul) — `--category all` **115/115**, `--category links` 0 kaputt.

## J6 — Strukturelle Identifizierbarkeit mit präzisem Umfang (erledigt)

Dokumentation: [`docs/structural_identifiability.md`](docs/structural_identifiability.md).
Code: `identifiability/exact_linear.py` (exakte affine Analyse, Faser,
Zeilenraumtest, deklarierte Bereichseinschränkung; lineare Algebra aus
J2 wiederverwendet), `identifiability/structural_reports.py`
(`StructuralReport` mit getrennten Feldern `method`/`scope`; analytische
Familien J-C12/J-C13; endliche Kandidatenfaser über die bestehende
H3-Beobachtungsfaser; `unsupported`). Bestehende Identifizierbarkeits-,
Fisher- und Profilmodule unverändert.

Prüfung: `verify_structural_identifiability.py` (math) **7/7** — J-C11
(Rang 1, Nullraum $(1,-1)$, Summe ja/Aufteilung nein, konsistente und
inkonsistente Beobachtung, Offset $b$), Bereichseinschränkung (Strecke,
Einzelpunkt „nur auf diesem Bereich“, leer, `not_evaluated` bei
2-D-Nullraum), J-C12 ($k$ und $cx_0$; Zeuge $(3/7,35)$; $c$ bekannt bzw.
**Anfangsbedingung** $x_0$ bekannt; Log-affine Gegenprobe), J-C13
($\{-2,2\}$, lokal vs. global, $\theta>0$), voller numerischer
Jacobi-Rang ≠ globale Eindeutigkeit (inkl. Anschluss an das bestehende
`parameter_scaling_invariance`), endliche Kandidatenfaser nur für die
gelisteten Kandidaten, ausdrückliches `unsupported`.

**Gezielte Mutanten:** 4 erkannt, 1 **äquivalent** (vorab mit Begründung
registriert, außerhalb des Nenners): Die Zeugenprüfung
$(c/\lambda)(\lambda x_0)=cx_0$ ist für jedes $\lambda>0$ algebraisch
wahr und kann innerhalb der J-C12-Familie nicht scheitern; „immer wahr“
ändert das Verhalten nicht. Die Prüfung dokumentiert, sie kann nicht
fehlschlagen — so ausgewiesen statt als Testlücke verdeckt.

Quellen S09/S10: SIAN-DOI/arXiv und die SciML-Doku erreichbar; keine
Abhängigkeit im Pflichtkern.

Regression mit J5, J11 und J6 (gemeinsamer Lauf, alle additiv):
`--category all` **115/115** bestanden, 0 übersprungen, 12 min 17 s; `--category links` 0 kaputt. Aufgefrischte Ergebnis-JSONs bestehender Prüfungen: nur Zeitstempel/Pfade. Konsolidierter Mutationsbericht über J0–J6: **47 Mutanten, 46 durch Assertions erkannt, 1 vorab begründet äquivalent (46/46 ohne Äquivalente)** — `verification/targeted_mutations_report.json`.

## Einbindung der Followups vom 2026-10-01

Zwei neue Eingänge unter `prompts/Answers/nicht_stationäre_Treiber/`
(Johann: „bau das ruhig direkt mit ein … fühl dich frei“):

- [`SCF_MUONIUM_GRAVITY_IMPLEMENTATION_PLAN.md`](prompts/Answers/nicht_stationäre_Treiber/SCF_MUONIUM_GRAVITY_IMPLEMENTATION_PLAN.md)
  (MU0–MU7) — eigenständige Domäne mit eigener Roadmap
  (`MUONIUM_GRAVITY_ROADMAP.md`, Pakete `MU<n>`). **Überschneidung mit J
  ist fachlich, nicht konfliktär:** MU1 kann die J2-Dimensionsprüfung
  nutzen (der MU-Plan verlangt, J-Bausteine erst nach Prüfung ihrer
  tatsächlichen Existenz anzuschließen), MU-C09/C10 (entfaltete Phase,
  Rang) sind exakte affine Identifizierbarkeit (J6), MU5 nutzt
  Fisher-/Sensitivitätsbausteine (J6/J7). Daher wird MU **nach J6**
  begonnen, damit keine Doppelentwicklung entsteht.
- [`SCF_POLYEDER_SAKURAI_SATURN_ANSCHLUSSBEWERTUNG.md`](prompts/Answers/nicht_stationäre_Treiber/SCF_POLYEDER_SAKURAI_SATURN_ANSCHLUSSBEWERTUNG.md)
  — Bewertung mit optionalen Paketen. Übernommen wird der dort
  empfohlene **begrenzte** Auftrag: TP0–TP1 (Polyeder-Beobachtungsfasern)
  und SK0–SK3 (Sakurai: Speicherpuls vs. Messoperator); Saturn zunächst
  nur SA0 (Quellen-/Größenregister). TP2–TP3, SK4, SA1–SA4 bleiben offene
  Optionen. Keine Promotion des Turing-Review-Pakets zum Kern.
- **Fehlendes Oracle:** Beide Dokumente verweisen auf ein Begleitskript
  `independent_controls.py` (17 MU- + 12 Kandidaten-Kontrollgruppen,
  „29/29“). Es liegt **nicht** im Eingangsordner (nur die beiden `.md`).
  Alle Kontrollfälle werden daher ausschließlich selbst hergeleitet; die
  Angabe „29/29“ ist hier nicht reproduziert.

Gesamtreihenfolge: J2 → J3 → J4 → J5 → J11 → J6 → MU0–MU7 → J7 → J8 →
J9 → J10 → J12 → TP0–TP1 → SK0–SK3 (+ SA0). Alle auf Branch `j-series`.
