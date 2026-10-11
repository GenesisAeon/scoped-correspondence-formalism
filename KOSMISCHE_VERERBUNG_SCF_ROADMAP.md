# SCF — Kosmische Vererbung: Mittelwert gegen Verteilung — Roadmap (2026-10-11)

Antwort auf [`KOSMISCHE_VERERBUNG_BESTANDSAUFNAHME_UND_PLAN.md`](prompts/Answers/nicht_stationäre_Treiber/KOSMISCHE_VERERBUNG_BESTANDSAUFNAHME_UND_PLAN.md)
(27.09.2026) samt Beilage `KOSMISCHE_VERERBUNG_REVIEW_REPRO.zip`.

**Auftrag und Arbeitsteilung (Johann, 2026-10-11):**
- Den Domänenteil des Plans (V0–V6: Stellar Forge, chemischer Bilanzkern, Ertragstabellen) setzt eine **eigene Session in Feldtheorie** um.
- SCF übernimmt nur, was laut Plan §8 hierher gehört: die SCF-Seite von V5 (Kontrollfall „Mittelwert gegen Verteilung“, Plan §6.2) und später V7 (Adapter und Bericht).
- Die Schnittstelle wird über `D:\mandala\KOSMISCHE_VERERBUNG_KOORDINATION.md` abgestimmt. Die Datei liegt außerhalb des Repos.

**Disziplin nach `CLAUDE.md`:** Herleitung vor Code, ein Paket pro Commit, volle Regression und Linkprüfung vor jedem Commit. Branch `kv-series`, kein Push ohne Johanns Freigabe.

**Leitfrage (Plan §6.2):** Reicht eine mittlere Metallizität als makroskopischer Zustand, oder braucht die Vorhersage zusätzlich einen unberührten Gasanteil, eine Verteilung oder ein Gedächtnis?

**Aussagegrenzen:**
- SCF prüft hier **mathematische Struktur**: Beobachtungsfasern und exakte Lumpability.
- Ergebnisse sind `synthetic_only`. Es gibt keine astrophysikalische Aussage und keine JWST-Aussage.
- Erträge, Lebensdauern und Einheiten gehören in die Domäne (Feldtheorie).

## Pakete

| Paket | Inhalt | Status |
|---|---|---|
| KV0 | Quellen, Umfang, API-Audit, Handkontrollen MV-K1–MV-K4 | ✅ erledigt (dieser Commit) |
| KV1 | `verify_kv_mean_vs_distribution.py`: MV-K1–MV-K4 gegen die Produktions-APIs, mit Negativkontrollen; `docs/kosmische_vererbung_scf.md` | offen |
| KV2 | Linearer Kontrollfall (Plan §8, „exakter linearer Kontrollfall vor nichtlinearer Anwendung“): zwei Reservoire, Bedingung für einen geschlossenen Mittelwert, Gedächtniskern bei weggelassenem Zustand | wartet auf die Schnittstelle (Einheiten, Massen) |
| KV3 | Adapter für die Ausgaben der Feldtheorie-Seite (V5/V7): Beobachtungsoperator, Fasern auf deren Handfällen | wartet auf Feldtheorie V3/V5 |
| KV4 | Bericht und Abschluss (V7) | offen |

## KV0 — Quellen, Umfang, Handkontrollen

### Quellen

- Plan und Beilage liegen in diesem Commit unverändert unter `prompts/Answers/nicht_stationäre_Treiber/`:
  - Plan: SHA-256 `0c67329e…38f6`;
  - ZIP: SHA-256 `fe9a7b24…c15e`.
  - Die ZIP enthält `reproduce_review.py`, `findings.json` und Quellmanifeste der Domänen-Repos. Sie betrifft F1–F8 (Feldtheorie, Nachbar-Repos), nicht SCF.
- Der Plan wurde gegen SCF `9dde420` bzw. `4a7ed38` geschrieben. Die Anschlüsse aus §8 wurden am aktuellen Stand `873adb8` (0.42.0) neu geprüft; siehe die folgende Tabelle.

### Bestätigte Schnittstellen (selbst gelesen, Stand `873adb8`)

| Zweck (Plan §8) | API | Ort |
|---|---|---|
| Unterscheidbare Vorgeschichten | `observation_fiber(domain, assumptions, observation, observed, …)` | `src/scoped_correspondence/epistemic/observation_fibers.py:75` |
| Identifizierte Wertemenge | `identified_values(fiber, target)`: Wertemenge, nie Intervall | `epistemic/observation_fibers.py:152` |
| Dynamik und Ereignisbeobachtbarkeit getrennt (K8) | `macro_dynamics_and_observability(...)` | `epistemic/observation_fibers.py:225` |
| Endlicher Modellraum, Annahmen | `FiniteDomainSpec`, `AssumptionSpec`, `evaluate_bool` | `epistemic/records.py:104`, `:78`, `:59` |
| Exakte Lumpability | `check_lumpability(P, C, tol)`: `max_defect` = größte Spaltenspanne der Blocksummen innerhalb einer Klasse | `correspondence/controlled_markov.py:117` |
| Kontrollierte Korrespondenz | `check_controlled_correspondence(P_by_action, C, omega, tol)` | `correspondence/controlled_markov.py:149` |
| Partition und Ereignis | `partition_indicator(labels)`, `is_union_of_classes(event, C)` | `correspondence/controlled_markov.py:54`, `:305` |
| Weggelassene Reservoirzustände (KV2) | `exact_memory_kernel(B, D, C)`, `run_memory_projection_comparison(...)` | `closure/linear_memory_projection.py:92`, `:283` |
| Verteilte Rückführung (KV2, optional) | `PhaseType`, `erlang_phase_type`, `propagate_phase_type` | `dynamics/phase_type_delays.py:55`, `:61`, `:192` |
| Stoffrückgabe (KV2, optional) | `parallel_reservoir_step`, `memory_kernel` | `dynamics/linear_reservoirs.py:143`, `:182` |

Konventionsgrenze (Plan §8): `controlled_markov` erwartet **zeilen**stochastische Kerne. Die Kerne unten sind zeilenstochastisch definiert, und KV1 prüft das.

### Kontrollmodell

- Zwei gleich schwere Gaspakete; Metallizität in Einheiten u = 0,01 auf dem Raster {0, 1, 2}.
- Mikrozustand (z₁, z₂), Index 3·z₁ + z₂, also 9 Zustände.
- Beobachtung h = mittlere Metallizität (z₁ + z₂)/2.
- Zielgröße f₀ = Massenanteil unberührten Gases (z = 0).
- Ein Sternbildungsschritt: Ein gleichverteiltes Paket i (Wahrscheinlichkeit ½) geht z_i → g(z_i).

### MV-K1–MV-K4 unabhängig hergeleitet

Von Hand hergeleitet, dann mit [`verification/plan_controls/kv_series_independent_controls.py`](verification/plan_controls/kv_series_independent_controls.py) nachgerechnet (`Fraction`, kein SCF-Import; [Ergebnisse](verification/plan_controls/kv_series_independent_controls_results.json)). Beide Wege stimmen überein.

| ID | Fall | Erwartung (exakt) |
|---|---|---|
| MV-K1 | Fasern von h, Zielgröße f₀ | y=0: {(0,0)}, f₀ = {1}; y=½: {(0,1),(1,0)}, f₀ = {½}; **y=1: {(0,2),(1,1),(2,0)}, f₀ = {0, ½}, nicht punktidentifiziert** (Menge, kein Intervall); y=3/2: f₀ = {0}; y=2: f₀ = {0}; **y=5/2: leere Faser** (Modell-Fehlanpassung, keine Identifikation). Behauptung „unberührtes Gas vorhanden“ bei y=1: Wahrheitswerte {falsch, wahr}, nicht identifizierbar |
| MV-K1 (gemeinsam) | Beobachtung (h, f₀) | 6 Klassen = 6 Multimengen; f₀ überall punktidentifiziert. **Nur** für 2 Pakete auf 3 Rasterpunkten; keine allgemeine Identität |
| MV-K2 | Pop-III-sensitiver Ertrag g(0)=2, g(z≥1)=min(z+1, 2) | Partition nach Mittelwert: **nicht** lumpable, `max_defect = 1` in Klasse h=1, Spalte h=3/2, Zeilen (0,2) gegen (1,1). Grund: (0,2) → h=1 oder h=2 je ½; (1,1) → h=3/2 sicher. Partition nach (h, f₀) bzw. Multimenge: exakt, Defekt 0 |
| MV-K3 | Z-blinder, gesättigter Ertrag g(z)=min(z+1, 2) | Mittelwert: **nicht** lumpable, `max_defect = ½` (Klasse h=1, Spalte h=1, Zeilen (1,1) gegen (0,2)). Multimenge: exakt |
| MV-K4 | Summenerhaltende Mischung (gleichverteilt auf Zustände gleicher Gesamtmetallmenge) | Mittelwert: **exakt** lumpable (Defekt 0). Ereignis „unberührtes Gas vorhanden“ = Indizes {0, 1, 2, 3, 6}: **keine** Vereinigung von Mittelwertklassen. Exakte Makrodynamik, aber das Ereignis ist makroskopisch nicht beobachtbar (K8) |

### Lesart und Gegenmodell-Warnung

- **MV-K2 gegen MV-K3 ist der wichtigste Befund dieses Pakets.**
  - Der Mittelwert reicht nicht nur bei Pop-III-spezifischen Erträgen nicht. Er reicht auch schon bei reiner **Sättigung** (Deckel bei z = 2) nicht.
  - „Der Mittelwert ist für die Dynamik unzureichend“ ist daher für sich **kein** Beleg für eine besondere Pop-III-Physik.
  - Jede spätere Aussage dieser Art braucht ein Gegenmodell, das dieselbe Unzureichendheit ohne den behaupteten Mechanismus erzeugt.
- **MV-K4:** Exakte Makrodynamik ist nicht dasselbe wie die Beobachtbarkeit einer Zielaussage. Beides wird getrennt berichtet.
- **MV-K1:** Bei y = 1 ist f₀ nur als Menge {0, ½} bestimmt. Ein Intervall [0, ½] würde unzulässige Zwischenwerte suggerieren.

### Prüfpunkte KV0

- [x] Plan und Beilage gelesen, Hashes notiert
- [x] Alle Schnittstellen aus Plan §8 am aktuellen Stand gelesen; Datei:Zeile wie oben
- [x] MV-K1–MV-K4 von Hand hergeleitet und unabhängig nachgerechnet (Fraction)
- [x] Kein Produktionscode in diesem Paket

## Offen / für die Schnittstelle

- **Einheiten und Massen:** Masse in M☉, Zeit in Myr (Plan §6.1). Pakete ungleicher Masse brauchen einen massengewichteten Mittelwert. Das betrifft KV2 und KV3.
- **Reaktion der Sternbildung auf lokales Z** (Domänenregel): Erst sie entscheidet, ob ein realistischer Kern eher MV-K2 oder MV-K3 ähnelt.
- **Beobachtungsoperator** für KV3, laut Plan §6.3 nicht mit Linienstärken gleichzusetzen.
