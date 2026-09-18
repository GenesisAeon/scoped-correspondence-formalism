Auftrag: Teil 2, Milestone 15 ("Dissipativity / Supply Rates") —
natürliche Erweiterung von `coupling`, aus `ChatGPTAstra3.md` (Willems
1972, DOI 10.1007/BF00276493, von Claude gegen die Quelle geprüft).

## Kontext

`coupling.check_generic_structure` (M2) prüft `J`/`M`-Struktur;
`coupling.dirac_composition` (M12, gemergt) komponiert die
reversible/Poisson-Seite (`J`). Willems (1972) liefert einen
allgemeineren, unabhängigen Kopplungsvertrag über eine Speicherfunktion
`V` und eine Supply Rate `w`:

\[
\dot V(x) \le w(u,y).
\]

Dies ist EIN ALLGEMEINER Dissipativitätsvertrag — KEINE thermodynamische
Identität. Er darf nicht mit `M`/GENERIC-Entropie gleichgesetzt werden
(Astra3s eigene Warnung: "unter `coupling/dissipativity.py`, nicht
`thermo`, solange keine thermodynamische Interpretation bewiesen wird").

## Umfang dieses Auftrags

### 1. `coupling.dissipativity.check_storage_inequality(V_dot, w, tol)`

Prüft `V̇(x) <= w(u,y) + tol` für gegebene numerische Werte (kein
Solver — reiner Ungleichheitscheck mit den bereits berechneten
Größen).

### 2. `coupling.dissipativity.neutral_interconnection_supply(y1, u1, y2, u2)`

Berechnet `y1·u1 + y2·u2` (die Summe der Supply-Terme an der
Schnittstelle).

### 3. `coupling.dissipativity.DissipativityCertificate`

Typisiertes Ergebnis: `V_dot_total`, `supply_total`, `satisfied: bool`,
`source`, mit explizitem Hinweis im Docstring: "Dissipativity ist ein
allgemeiner Energiebilanzvertrag — KEINE thermodynamische Aussage ohne
zusätzlichen Nachweis von Bilanzgrößen und konjugierten Kräften
(vgl. `thermo`-Modul-Disclaimer)."

### 4. Durchgerechnetes Beispiel (bereits von Claude bestätigt)

Zwei Teilsysteme `ẋ_i=-x_i+u_i`, `y_i=x_i`, `V_i=x_i²/2`, also
`V̇_i=-x_i²+y_i·u_i`. Neutrale Interkonnektion `u1=-y2, u2=y1`:

\[
y_1u_1+y_2u_2=-y_1y_2+y_2y_1=0
\Rightarrow
\dot V_{total}=-(x_1^2+x_2^2).
\]

Bei `x1=1, x2=2`: `V̇_total=-5`. Diese Zahl im Skript exakt
reproduzieren, plus mindestens einen zweiten `(x1,x2)`-Fall zur
Gegenprobe.

### 5. Explizit NICHT Teil dieses Auftrags

- Keine Änderung an `coupling/core.py` oder `coupling/dirac_composition.py`.
- Keine thermodynamische Interpretation — `V` bleibt eine abstrakte
  Speicherfunktion, keine Entropie/Energie-Bilanzgröße.
- Keine allgemeine Netzwerk-Interkonnektionstheorie — nur der
  konkrete Zwei-System-Fall mit neutraler Rückkopplung.

## Verifikation

`verify_dissipativity_core.py`: keine bestehende Legacy-Prüfung —
frisches Beispiel (identisch zum bereits in `ChatGPTAstra3.md`
durchgerechneten Fall). Mindestens: (1) `V̇_total=-5` bei `x1=1,x2=2`
exakt, (2) zweiter unabhängiger `(x1,x2)`-Fall, (3) ein absichtlich
verletzter Fall (Supply Rate manipuliert, sodass `check_storage_inequality`
korrekt `False` liefert).

## Abnahmebedingungen (Astra-Standard, unverändert)

1. Textformeln (LaTeX/Markdown), keine Bildformeln.
2. `verify_dissipativity_core.py` mit reproduzierbarem JSON-Report
   unter `verification/`.
3. Durchgerechnetes Beispiel mit Zahlen AUS DEM SKRIPTLAUF.
4. Explizites Mapping auf Willems 1972 (DOI oben) und `coupling/core.py`.
5. KEINE Mutation von FORMALISM.md oder einem der sieben Layer-/
   Erweiterungsdokumente (explizit inklusive `coupling_layer_afet.md`).
6. Johann-OK vor jeder Aufnahme in einen "Kern"-Status.

## Lieferformat

Eigener Branch `aeon/m15-dissipativity` auf
`GenesisAeon/scoped-correspondence-formalism`, direkt gepusht. Kann
PARALLEL zu Milestone 14 (`dynamics`) und Milestone 16 (`viability`)
bearbeitet werden. Package-root `src/scoped_correspondence/__init__.py`
bitte NICHT anfassen (Konfliktvermeidung, wie bei M11–M13). Claude
reviewed jeden Branch einzeln und merged erst nach Johanns OK.
