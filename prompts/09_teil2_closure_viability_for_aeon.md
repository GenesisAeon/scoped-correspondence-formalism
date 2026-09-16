Auftrag: Teil 2, Milestone 3 ("Closure & Reconstruction" + "Viability &
Safe Control") — zwei Module, auf `correspondence`/`observation`/
`dynamics`/`coupling` (Milestones 1-2, gemergt) aufbauend. Membership &
Shared Resources bewusst NICHT Teil dieses Auftrags, siehe unten.

## Kontext

`src/scoped_correspondence/{correspondence,observation,dynamics,coupling}/`
existieren bereits und sind verifiziert (18/18 Prüfungen, siehe
FOLLOWUP_TICKETS.md F16/F17). Dieser Auftrag baut zwei weitere Module
auf derselben Basis.

## Umfang dieses Auftrags (bewusst begrenzt)

### 1. `closure` (Makro-Geschlossenheit + Rekonstruktion)

Quelle: `emergence_and_closure.md` (PC=CQ, Fehlerschranke), FORMALISM.md
§9 ("Eigene Makrodynamik als prüfbare Eigenschaft"),
`worked_example_reconstruction.md`. Mindestens:
- `is_exact_closure(P, C, Q, tol=1e-10) -> bool` — prüft `PC=CQ` exakt
  (FORMALISM.md §9).
- `closure_error(P, C, Q) -> float` — `delta_cl = max_i TV((PC)_i,(CQ)_i)`
  und die zugehörige Fehlerschranke `TV(pP^kC,pCQ^k) <= min(1,k*delta_cl)`
  als zweite Funktion `propagated_error_bound(delta_cl, k)`.
- `reconstruct_from_projection(...)`: mindestens der Kreisrekonstruktions-
  Fall aus `worked_example_reconstruction.md` (zwei Koordinaten
  genügen bei d=1) als konkrete, lauffähige Funktion — keine
  allgemeine Takens-Bibliothek, nur der bereits durchgerechnete Fall.
- Verifikation gegen: `e01_circle_reconstruction`, `e04_exact_lumpability`,
  `e05_nonclosed_aggregation`, `e06_approximate_error_bound`,
  `e03_projected_memory` (alle in verify_extensions.py) sowie
  `t07_unequal_rates_break_closure` und `t15_changing_partition_exact_closure`
  (verify_transformations.py). Zahlen müssen exakt übereinstimmen.

### 2. `viability` (Sichere Eingriffsübertragung)

Quelle: `context_transformations.md` §8 ("Erhaltung ausführbarer
Eingriffe" — der Satz mit Beweis aus dem F08/F09-Nachreview, bereits
gemergt), `worked_example_viability.md`. Mindestens:
- `has_safe_transfer(...)`: prüft die drei Bedingungen aus §8
  (Ausführbarkeit, Nachfolgerverträglichkeit, sichere Darstellung)
  für ein gegebenes Makro-Policy-Kandidat — mindestens für den
  skalaren Fall aus `worked_example_viability.md`.
- `shared_budget_conflict(...)`: der gekoppelte-Puffer-Fall (r10 /
  `t10_shared_budget_conflict`) — zeigt, wann ein gemeinsames Budget
  eine Anforderung nicht gleichzeitig für alle möglichen Mikrozustände
  erfüllen kann.
- **Explizit NICHT hierher:** ein allgemeiner Viability-Kernel-Solver
  (Polytope/Level-Sets) — das ist laut ARCHITECTURE_ROADMAP.md ein
  eigenes, größeres Modul (`Viability & Safe Control`, Aufwand L) für
  einen späteren Auftrag. Hier nur die bereits bewiesenen/durchgerechneten
  Fälle als Code.
- Verifikation gegen: `t05_scalar_boundary_and_hitting`,
  `t09_orthant_boundary_conditions`, `t10_shared_budget_conflict`
  (alle verify_transformations.py). Zahlen müssen exakt übereinstimmen.

### 3. NICHT Teil dieses Auftrags

`membership` (überlappende Systemzugehörigkeit, `M_eα`,
`context_transformations.md` §1/§6) — eigener, späterer Auftrag, weil
er inhaltlich auf `closure` und `viability` aufbaut (gemeinsame
Eingriffsmenge `T5` braucht beide). `predictive_states`
(`e15_predictive_states`) — optionaler Bonus, nur falls Zeit bleibt,
kein Blocker für diesen Auftrag.

## Abnahmebedingungen (Astra-Standard, unverändert)

1. Textformeln (LaTeX/Markdown), keine Bildformeln.
2. `verify_*.py` mit reproduzierbarem JSON-Report unter `verification/`.
3. Durchgerechnetes Beispiel mit Zahlen AUS DEM SKRIPTLAUF.
4. Explizites Mapping auf FORMALISM.md §9 / `context_transformations.md`
   §8 — jede neue Funktion referenziert ihre Herkunftsstelle.
5. KEINE Mutation von FORMALISM.md oder einem der sieben Layer-/
   Erweiterungsdokumente.
6. Johann-OK vor jeder Aufnahme in einen "Kern"-Status.

## Lieferformat

Eigener Branch `aeon/m3-closure-viability` auf
`GenesisAeon/scoped-correspondence-formalism`, direkt gepusht. Kein
Push/Merge direkt nach `master`. Claude reviewed (Diff, Skripte selbst
nachrechnen, mindestens einen Fall pro Modul von Hand gegenprüfen) und
merged erst nach Johanns OK — wie bei M1/M2.
