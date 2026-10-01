# Geltungsbereiche, Komposition und Evidenz — Entwurfsentscheidungen (J0)

Begleitdokument zu [`SCOPE_COMPOSITION_EVIDENCE_ROADMAP.md`](../SCOPE_COMPOSITION_EVIDENCE_ROADMAP.md)
und zum Plan
[`SCF_SCOPE_COMPOSITION_EVIDENCE_IMPLEMENTATION_PLAN.md`](../prompts/Answers/nicht_stationäre_Treiber/SCF_SCOPE_COMPOSITION_EVIDENCE_IMPLEMENTATION_PLAN.md)
(Plan §6, Arbeitsschritt 5: „Pfade, Ergebnisfelder und optionale
Abhängigkeiten festlegen“). Lizenz: CC BY 4.0.

Dieses Dokument legt fest, **wo** neue J-Module liegen, **welche
Ergebnisachsen** sie tragen und **woran** sie anschließen. Es enthält noch
keine Implementierung; jede Festlegung kann in einem späteren Paket
begründet geändert werden — die Änderung wird dann dort dokumentiert, nicht
still vollzogen.

## 1. Pfade (relativ zu `src/scoped_correspondence/`)

| Paket | Neue Module | Anschluss an Bestehendes |
|---|---|---|
| J1 | `validation/forecast_comparison.py` | Adapter um `validation/rolling_origin.py` (`RawHorizonPrediction`, `raw_predictions_by_horizon_step`); ersetzt keine Backtest-Berichte |
| J2 | `dimensions/__init__.py`, `dimensions/core.py`, `dimensions/pi_groups.py` | neues Teilpaket; Kontrollanschluss an `dynamics/linear_reservoirs.py` und an Galaxiengrößen aus `validation/galaxy_pilot.py` |
| J3 | `verification/verify_metamorphic_relations.py`, `scripts/run_targeted_mutations.py` | Mutationen nur auf temporärer Kopie (`tempfile`), nie im Arbeitsbaum |
| J4 | `correspondence/domains.py`, `correspondence/contracts.py`, `correspondence/composition.py`, `assurance/__init__.py`, `assurance/records.py` | `correspondence/contract.py` (`Scope`, `Correspondence.t4_composition_residual`) bleibt unverändert |
| J5 | `assurance/rational_intervals.py`, `assurance/expressions.py`, `assurance/scope_certification.py` | nur `fractions.Fraction`; keine neue Abhängigkeit |
| J6 | `identifiability/exact_linear.py`, `identifiability/structural_reports.py` | `identifiability/core.py`, `epistemic/observation_fibers.py`; `fim_sloppiness.py`/`profile_likelihood*.py` bleiben getrennte Ergebnisarten |
| J7 | `validation/global_sensitivity.py` (+ Galaxienadapter nur bei Bedarf, bevorzugt Erweiterung in `validation/galaxy_pilot.py`) | `distance_inclination_sensitivity(_mode_b)` in `validation/galaxy_pilot.py` |
| J8 | `validation/weighted_conformal.py` | `validation/conformal.py` (Quantilkonvention, Trennung Kalibrierung/Holdout), `validation/adaptive_interval_calibration.py` als Vergleich |
| J9 | `causal/__init__.py`, `causal/finite_scm.py`, `causal/abstraction.py` | `correspondence/controlled_markov.py` als verwandter, nicht ersetzender Anschluss; Fasern über `epistemic/observation_fibers.py` |
| J10 | `causal/selection_diagrams.py`, `causal/transport.py` | J9 |
| J11 | `closure/contract_adapter.py` | `closure/error_bounds.py` (`transient_reduction_bound`, `stationary_reduction_bound`, `compare_to_propagated_error_bound`) — keine zweite Implementierung |
| J12 | `scripts/run_scope_evidence_demo.py` | bestehende spezialisierte CLIs bleiben |

Verifikation: je Paket `verification/verify_<name>.py`, ausdrücklich in
`scripts/run_verification_suite.py::_EXPLICIT_CATEGORY` registriert. Die
unabhängige Planarithmetik liegt getrennt unter
[`verification/plan_controls/`](../verification/plan_controls/) und wird
vom Suite-Runner absichtlich nicht als Produktionsprüfung gezählt.

## 2. Ergebnisachsen (Plan §5.1)

### 2.1 Was bereits existiert und wiederverwendet wird

`epistemic/records.py` stellt die Vokabulare `EVIDENCE_KINDS`,
`EMPIRICAL_STATUSES`, `DOMAIN_RELATIONSHIPS`, `DOMAIN_COVERAGE` sowie
`ClaimReport` (mit `search_complete` ≠ `all_candidates_scanned`) bereit.
Diese Konstanten werden **importiert, nicht kopiert**. Bestehende
H-Berichte behalten ihre Semantik (Plan §5.2).

### 2.2 Warum trotzdem ein kleines `assurance/records.py`

`ClaimReport.logical_status` ist auf **endliche** deklarierte Domänen
zugeschnitten (`entailed_in_scope`, `underdetermined`, …). J5 dagegen
beweist Aussagen über **kontinuierliche** rationale Boxen; dort braucht es
Achsen, die `ClaimReport` nicht hat: Boxpartition, rationale
Einschließungen, Restboxen, und die Unterscheidung „Ausdruck auf dem
Gebiet nicht definiert“ vs. „unbekannt“. Ein solcher Bericht als
`ClaimReport` mit `grid_of_continuous_space` wäre gerade die verbotene
Umdeutung eines Kontinuums in eine Kandidatenliste (Plan §3, Zeile
`epistemic/records.py`).

Entscheidung: `assurance/records.py` mit einem `ProofReport` (und einer
typisierten Sammlung `ClaimBundle`), dessen Achsen:

| Feld | Werte | Plan §5.1 |
|---|---|---|
| `claim` | Aussage, Quantor, Zielgröße (Text + strukturierte Felder) | Aussage |
| `declared_domain`, `checked_domain`, `empty_domain` | Bereichsbeschreibung; `empty_domain=True` markiert vakuose All-Aussagen ausdrücklich | Bereich |
| `assumptions` | Tupel von (`id`, Herkunft ∈ {`given`, `derived`, `empirically_supported`}) | Annahmen |
| `procedure_status` | `completed`, `budget_exhausted`, `invalid_input`, `unsupported_structure`, `numerical_failure` | Verfahrensstatus |
| `verdict` | `proved`, `refuted`, `undecided`, `undefined_on_domain`; bei Stichproben zusätzlich `observed_pass`/`observed_fail` | Urteil |
| `evidence_kind` + `method` | aus `EVIDENCE_KINDS` + genaues Verfahren | Evidenz |
| `arithmetic` | `exact_rational`, `validated_enclosure`, `floating_point_estimate` | Arithmetik |
| `empirical_status` | aus `EMPIRICAL_STATUSES` | Empirie |
| `conclusion_complete`, `domain_exhausted` | getrennte Booleans (analog `search_complete`/`all_candidates_scanned`) | Vollständigkeit |
| `witnesses` | Gegenbeispiel, Restboxen, ununterscheidbare Modellpaare | Zeugen |
| `certificate_id` | Inhaltshash; identifiziert, **beweist nicht** | §5.2 |

Ein Adapter `proof_report_from_claim_report` verweist auf bestehende
H-Berichte, statt sie umzudeuten. Ob `ProofReport` später mit
`ClaimReport` verschmolzen wird, ist **nicht** Gegenstand dieses Plans
(kein globaler Umbau, Plan §5.2).

### 2.3 JSON-Regeln (Plan §5.2)

- **Befund J0:** `epistemic/reporting.report_to_json` ruft `json.dumps`
  ohne `allow_nan=False` auf; ein Gleitkomma-`inf`/`nan` in einem
  Bericht würde daher als nichtstandardkonformes `Infinity`/`NaN`
  ausgegeben. Das ist am Referenzcommit kein beobachteter Fehler
  bestehender Berichte (nicht untersucht), aber für die J-Berichte eine
  harte Vorgabe:
- J-Berichte speichern **kein** Float-`inf`/`nan`. Unbeschränkte Bereiche
  bekommen explizite Marker, z. B. `{"kind": "whole_real_line"}`; ein
  gewichtetes Conformal-Quantil `+∞` wird als `{"kind":
  "positive_infinity"}` und das zugehörige Intervall als ganze reelle
  Gerade ausgewiesen — **nicht** als leeres Intervall (vgl. Befund zu
  `validation/conformal.py:65` in der Roadmap, Korrektur in J8).
- Serialisierung neuer Berichte mit `allow_nan=False`, damit ein
  Rückfall laut scheitert statt stilles Nicht-JSON zu schreiben.
- `Fraction` exakt als `{numerator, denominator}` (bestehende Konvention
  aus `epistemic/reporting.py`). `null` heißt *fehlend*, nie „unendlich“
  oder „falsch“.

## 3. Budgets (Plan §19.2)

Jede API mit Enumeration oder Unterteilung bekommt ein explizites,
dokumentiertes Budget (Boxen, Zustände, Exogenkombinationen,
Rechenschritte). Die Standardwerte werden je Paket an einem kleinen
Benchmark festgelegt und dort dokumentiert — nicht hier vorab erfunden.
Budgetabbruch ist `procedure_status="budget_exhausted"` mit
`verdict="undecided"` (sofern kein Gegenbeispiel gefunden wurde) und
behauptet nie Universalität oder Minimalität.

## 4. Abhängigkeiten

Pflichtkern: Standardbibliothek (`fractions`, `itertools`, `dataclasses`,
`json`) plus die bereits deklarierten `numpy`/`scipy`
(`pyproject.toml`). **Keine neue Laufzeitabhängigkeit.** Optionale
Backends (IntervalArithmetic.jl, SIAN, StructuralIdentifiability.jl) sind
ausdrücklich nicht Teil des Pflichtumfangs (Plan §22) und würden bei
Aufnahme mit gepinnter Version und eigener Aussageklasse isoliert
angebunden.

## 5. Ausdrücklich nicht behauptet

Siehe Plan §2.2 und §18.2. Insbesondere: keine Zertifizierung beliebiger
Python-Callables, keine validierten ODE-Flüsse, keine allgemeine kausale
Identifikation, kein allgemeiner Transportabilitätssolver, keine
Driftgarantie jenseits von Covariate Shift. Ein Resultat kann innerhalb
eines Modells exakt sein, während die Anwendbarkeit des Modells auf ein
reales System offenbleibt — diese Trennung bleibt in jedem Bericht
sichtbar (`evidence_kind` vs. `empirical_status`).
