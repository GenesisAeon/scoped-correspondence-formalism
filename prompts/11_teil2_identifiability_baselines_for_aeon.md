Auftrag: Teil 2, Milestone 5 ("Identifiability & Baseline Metrics") — ein
Modul, auf `correspondence`/`observation`/`dynamics`/`coupling`/`closure`/
`viability`/`membership` (Milestones 1-4, alle gemergt) aufbauend.

## Kontext

`src/scoped_correspondence/{correspondence,observation,dynamics,coupling,
closure,viability,membership}/` existieren bereits und sind verifiziert
(30/30 neue Prüfungen über M1-M4). Dieser Auftrag ist die erste Hälfte
von ARCHITECTURE_ROADMAP.md's "Uncertainty & Validation"-Meilenstein
(Woche 9-12): den bereits durchgerechneten Teil — Messmodell/Konditionierung,
Identifizierbarkeit, Referenzmodelle/Baselines — als Code, mit exakten
Legacy-Ankern wie bei M1-M3.

**Wichtige Abgrenzung:** Der ROADMAP-Meilenstein verlangt zusätzlich "Dataset
Manifest, Train/Holdout, ein echter Pilot mit realen Daten". Das ist
AUSDRÜCKLICH NICHT Teil dieses Auftrags (siehe Abschnitt 3 unten) —
`ROADMAP.md` §3 dieses Repos verlangt selbst erst eine bewusste
Domänen-/Datensatzentscheidung (Zustände, Systemgrenzen, Eingaben,
Zeitskalen, Beobachtungen VOR dem Test festlegen), und das ist Johanns
Entscheidung, nicht Aeons. Dieser Auftrag bleibt bei bereits vorliegenden,
formal durchgerechneten Beispielen (wie jedes bisherige Milestone).

## Umfang dieses Auftrags (bewusst begrenzt)

### 1. `identifiability` (Konditionierung, Nichtidentifizierbarkeit, Baselines)

Quelle: `verify_extensions.py` (e02, e07, e08, e09, e12), FORMALISM.md §10
("Typ 1... spezifizierter Vorteil... gegenüber einer festgelegten Baseline"),
§12 (Reparametrisierung `Γ'=kΓ, σ'=σ/k`). Mindestens:

- `delay_amplification(alpha) -> float`: Konditionierungsfaktor `1/|sin α|`
  aus `e02_sampling_alias_and_conditioning` — zeigt, warum manche
  Beobachtungsgeometrien (α nahe 0 oder π) numerisch schlecht konditioniert
  sind. Zusätzlich das Beispiel „nicht unterscheidbare Delay-Vektoren"
  (gleiche `cos`-Werte bei `theta` und `-theta` unter Alias) als zweite
  Funktion oder als Teil desselben Berichts.
- `parameter_scaling_invariance(sigma, gamma, scale) -> dict`: reproduziert
  `e12_parameter_scaling_nonidentifiability` — `tanh(σγ)` bleibt unter
  `σ'=σ/k, γ'=kγ` exakt gleich; zusätzlich die Jacobian-Rang-1-Prüfung
  (Kollinearität von `∂/∂σ` und `∂/∂a` bei `tanh(σ·a·g)`) als eigene
  Funktion `identifiability_jacobian_rank(sigma, a, g) -> int`.
- `svd_emergence_vs_ei(...)`: reproduziert `e09_svd_does_not_imply_ei` —
  ein positiver SVD-Emergenzwert (`delta_svd`) impliziert keinen positiven
  EI-Gewinn (hier exakt 0 bei einer uniformen 4x4-Matrix). Muss beide
  Werte explizit nebeneinander zurückgeben, nicht nur einen.
- `fixed_ensemble_data_processing(...)`: reproduziert
  `e08_fixed_ensemble_data_processing` — Data-Processing-Inequality bei
  fester Ensemble-Verteilung über alle 15 Partitionen von 4 Zuständen
  (`macro <= micro` für jede Partition).
- `effective_information_baseline(...)`: reproduziert
  `e07_effective_information_ensembles` — EI hängt von der gewählten
  Interventionsverteilung ab (uniform micro/macro vs. „matched" via Lift);
  macht explizit, dass `ΔEI` nur relativ zu einer benannten Baseline-
  Verteilung eine Aussage ist (FORMALISM.md §10, erster Satz von Typ 1).

### 2. Optionaler Bonus (nur falls Zeit bleibt, kein Blocker)

`predictive_states(...)` aus `e15_predictive_states` (bedingte
Zukunftsverteilungen eines binären Markov-Kanals, exakte endliche
Beispiele, keine gelernte Epsilon-Machine) — wie schon bei M3 als Bonus
vorgemerkt und dort nicht bearbeitet.

### 3. Explizit NICHT Teil dieses Auftrags

- **Dataset Manifest, Train/Holdout-Split, `ValidationReport`-Schema für
  echte Studien, jeglicher realer Datenpilot.** Das ist der zweite,
  spätere Teil des ROADMAP-Meilensteins "Uncertainty & Validation" und
  braucht zuerst Johanns Domänen-/Datensatzentscheidung (welches Paket,
  welche Makrovariable, welche Zeitreihe) — siehe `ROADMAP.md` §3
  ("Vor dem Test festlegen: 1. Zustände... 2. Transformation T... 3.
  Bereich... 4. Vergleichsmodelle, Daten..."). Kein synthetischer
  Platzhalter-Pilot, der später falsch als „echte Validierung" zitiert
  werden könnte.
- Messfehlermodelle für kontinuierliche Rauschprozesse (Sensor-/
  Beobachtungsrauschen) — nicht durch einen bestehenden Legacy-Fall
  gedeckt, eigener späterer Auftrag falls benötigt.
- Änderungen an `correspondence/`, `observation/`, `dynamics/`,
  `coupling/`, `closure/`, `viability/`, `membership/` oder
  `legacy/adapters.py` — nur Aufruf/Kreuzprobe, keine Refaktorierung.

## Verifikation

`verify_identifiability_core.py` gegen: `e02_sampling_alias_and_conditioning`,
`e07_effective_information_ensembles`, `e08_fixed_ensemble_data_processing`,
`e09_svd_does_not_imply_ei`, `e12_parameter_scaling_nonidentifiability`
(alle in `verify_extensions.py`). Zahlen müssen exakt übereinstimmen
(inkl. `delta_svd=0.75`, Jacobian-Rang `1`, `EI_uniform_macro=1`,
`EI_matched_micro=1`, 15 geprüfte Partitionen in e08/e09).

## Abnahmebedingungen (Astra-Standard, unverändert)

1. Textformeln (LaTeX/Markdown), keine Bildformeln.
2. `verify_identifiability_core.py` mit reproduzierbarem JSON-Report unter
   `verification/`.
3. Durchgerechnetes Beispiel mit Zahlen AUS DEM SKRIPTLAUF (Legacy-Werte
   exakt reproduziert — keine erfundenen Zahlen).
4. Explizites Mapping auf FORMALISM.md §10/§12 und die genannten
   `e`-Funktionen — jede neue Funktion referenziert ihre Herkunftsstelle.
5. KEINE Mutation von FORMALISM.md oder einem der sieben Layer-/
   Erweiterungsdokumente.
6. Johann-OK vor jeder Aufnahme in einen "Kern"-Status.

## Lieferformat

Eigener Branch `aeon/m5-identifiability-baselines` auf
`GenesisAeon/scoped-correspondence-formalism`, direkt gepusht. Kein
Push/Merge direkt nach `master`. Claude reviewed (Diff, Skript selbst
nachrechnen, mindestens einen Fall von Hand gegenprüfen) und merged erst
nach Johanns OK — wie bei M1-M4.
