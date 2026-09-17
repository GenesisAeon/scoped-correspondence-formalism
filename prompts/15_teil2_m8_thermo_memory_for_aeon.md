Auftrag: Teil 2, Milestone 8 ("Thermo & Memory") — F13-Nachbarthema: ein
`thermo`-Modul, das bestehende GENERIC-/Reversibilitäts-Legacy-Fälle
kapselt und eine neue, bisher fehlende Projektionsprüfung ergänzt.

## Kontext

`coupling.check_generic_structure` (M2, gemergt) ist bereits ein reiner
Strukturtest (`J^T=-J`, `M^T=M≥0`, `J·∇S=0`, `M·∇E=0`) — NICHT anfassen,
nur aufrufen. `closure.memory_solution`/`projected_memory_rhs` (M3,
gemergt) decken den "Gedächtnis"-Teil des Meilensteins bereits ab — auch
nicht anfassen. Was fehlt laut `ARCHITECTURE_ROADMAP.md`s eigenem
Exit-Kriterium ("bestehende GENERIC-/Gedächtnistests plus neue
Projektionschecks"):

1. Zwei bestehende Legacy-Prüfungen aus `verify_extensions.py` sind noch
   NIRGENDS im Modul-System gekapselt: `e13_generic_heat_structure`
   (konkretes Zwei-Reservoir-Wärmebeispiel mit echten Zahlen) und
   `e10_inverse_is_not_detailed_balance` (Drei-Zyklus-Gegenbeispiel:
   stochastische Invertierbarkeit ≠ Detailed Balance ≠ thermodynamische
   Reversibilität, zitiert in `coupling_layer_afet.md` §9).
2. Eine neue Projektionsprüfung für `coupling_layer_afet.md` §9
   ("Skalenwechsel bewahrt Thermodynamik nicht automatisch") existiert
   noch nicht als Code — siehe Abschnitt 3 unten.

## Umfang dieses Auftrags

### 1. `thermo.heat_generic_example(ca, cb, conductance, ta, tb) -> dict`

Portiere `e13_generic_heat_structure` 1:1 (Energie, Entropiegradient
`(1/ta, 1/tb)` per finiter Differenz UND analytisch verglichen, M-Matrix
`conductance*ta*tb*[[1,-1],[-1,1]]`, Wärmefluss, Entropieproduktion
`conductance*(ta-tb)²/(ta*tb)`). Rufe danach
`coupling.check_generic_structure(J=zeros(2,2), M=m, grad_E=[1,1],
grad_S=gradient)` auf und gib dessen Ergebnis mit zurück — zeigt, dass
das bereits gemergte Strukturmodul dieses konkrete Beispiel als gültige
GENERIC-Struktur erkennt. `grad_E=[1,1]` deshalb, weil `E(z)=z_a+z_b`
(Gesamtenergie) und `M @ [1,1] = 0` bereits in `e13` exakt geprüft ist
(Energieerhaltung unter der dissipativen Kopplung).

### 2. `thermo.stochastic_inverse_not_detailed_balance() -> dict`

Portiere `e10_inverse_is_not_detailed_balance` 1:1 (Drei-Zyklus-
Permutationsmatrix, gültige stochastische Inverse, aber kein Detailed
Balance — asymmetrischer Fluss). Referenziert `coupling_layer_afet.md`
§9 und `worked_example_causal_emergence.md`.

### 3. `thermo.project_generic_structure(J, M, grad_E, grad_S, Pi) -> dict` (NEU)

Operationalisiert §9 als Code, ohne neue Physik zu erfinden: berechnet
`J' = Pi @ J @ Pi.T`, `M' = Pi @ M @ Pi.T` (Kongruenztransformation unter
einer linearen Projektion `Pi`) und ruft `check_generic_structure` auf
`(J', M', grad_E', grad_S')` — wobei `grad_E'`/`grad_S'` als EXPLIZITE,
separate Parameter verlangt werden (kein stiller Default wie
`Pi @ grad_E`). Docstring/Rückgabe müssen ausdrücklich klarstellen:
**diese Funktion prüft nur, ob die algebraische Struktur unter der
Kongruenztransformation erhalten bleibt — sie behauptet NICHT, dass
`(grad_E', grad_S')` ein tatsächlich gültiges reduziertes
Energie-/Entropiepotential für die projizierten Koordinaten sind.** Das
ist exakt die Warnung aus §9 ("kann ... die gewählte Markov-Beschreibung
ungültig machen").

Zwei konkrete, aus Abschnitt 1 ableitbare Beispiele im Verify-Skript:
- **Summen-Projektion** `Pi=[[1,1]]`: `M' = Pi @ m @ Pi.T = 0` (folgt
  direkt aus dem bereits verifizierten `m @ [1,1] = 0`) — zeigt, dass
  diese Projektion die gesamte Entropieproduktions-Information löscht
  (§9: "verborgene Dissipation entfernen").
- **Einzel-Reservoir-Projektion** `Pi=[[1,0]]`: `M' = m[0,0] =
  conductance*ta*tb` (positiver Skalar, trivial symmetrisch PSD) — zeigt
  den Gegenfall: die Struktur BESTEHT rein algebraisch fort, obwohl kein
  eigenständiges reduziertes `(E',S')`-Paar für `z_a` allein hergeleitet
  wurde. Explizit im Bericht vermerken, dass dieser Fall NICHT als
  "gültiges reduziertes GENERIC-System" fehlinterpretiert werden darf.

### 4. Explizit NICHT Teil dieses Auftrags

- Keine Änderung an `coupling/core.py`, `closure/core.py`, FORMALISM.md
  oder `coupling_layer_afet.md` (Kerndokument) — nur Aufruf der
  bestehenden `check_generic_structure`.
- Keine ODE-Integration/Trajektoriensimulation für das Wärmebeispiel —
  `e13` ist ein Punkt-Strukturtest, kein Zeitverlauf; dabei bleiben.
- Keine allgemeine Mori-Zwanzig-/Non-Markov-Projektionstheorie — der
  "Gedächtnis"-Teil ist mit `closure.memory_solution`/
  `projected_memory_rhs` (M3) bereits abgedeckt, hier nicht neu
  aufrollen.
- Keine Behauptung, dass irgendeine Projektion `Pi` ein "korrektes"
  reduziertes thermodynamisches Modell liefert — nur algebraische
  Struktur-Erhaltung/-Verletzung wird geprüft.

## Verifikation

`verify_thermo_core.py` gegen `extension_results.json`s `e13_generic_
heat_structure` (alle Parameterkombinationen, exakte Zahlen) und
`e10_inverse_is_not_detailed_balance` (exakt), plus die beiden neuen
`project_generic_structure`-Fälle oben (Summen-Projektion `M'=0`,
Einzel-Projektion `M'=conductance*ta*tb` bei mindestens einer
Parameterkombination).

## Abnahmebedingungen (Astra-Standard, unverändert)

1. Textformeln (LaTeX/Markdown), keine Bildformeln.
2. `verify_thermo_core.py` mit reproduzierbarem JSON-Report unter
   `verification/`.
3. Durchgerechnetes Beispiel mit Zahlen AUS DEM SKRIPTLAUF — Legacy-Werte
   exakt reproduziert, Projektionswerte neu und nachvollziehbar.
4. Explizites Mapping auf `coupling_layer_afet.md` §8/§9 und die
   genannten `e`-Funktionen.
5. KEINE Mutation von FORMALISM.md oder einem der sieben Layer-/
   Erweiterungsdokumente (explizit inklusive `coupling_layer_afet.md`).
6. Johann-OK vor jeder Aufnahme in einen "Kern"-Status.

## Lieferformat

Eigener Branch `aeon/m8-thermo-memory` auf
`GenesisAeon/scoped-correspondence-formalism`, direkt gepusht. Claude
reviewed (Diff, Skript selbst nachrechnen, Summen-Projektion von Hand
gegenprüfen) und merged erst nach Johanns OK.
