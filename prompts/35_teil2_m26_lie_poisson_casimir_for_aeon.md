Auftrag: Teil 2, Milestone 26 ("Lie-Poisson-Struktur / Casimir-
Invarianten") — natürliche Erweiterung von `coupling`, aus einer
unabhängigen Claude-Agenten-Recherche (Runde 2 zu `prompts/33_...md`).

## Quellen

- V. Arnold, "Sur la géométrie différentielle des groupes de Lie de
  dimension infinie et ses applications à l'hydrodynamique des fluides
  parfaits", Annales de l'Institut Fourier 16(1), 319–361 (1966), DOI
  10.5802/aif.233.
- J. E. Marsden & T. S. Ratiu, "Introduction to Mechanics and Symmetry",
  Springer New York (1999), DOI 10.1007/978-0-387-21792-5 (Lehrbuch-
  Referenz für die endlich-dimensionale Lie-Poisson-Formulierung, die
  hier tatsächlich implementiert wird — NICHT die unendlich-
  dimensionale Fluid-Version aus Arnold selbst; siehe Abgrenzung unten).

Beide DOIs wurden per Crossref-API verifiziert.

## Kontext

`coupling.core.check_generic_structure(J, M, grad_E, grad_S)` verlangt
bereits, als eine von fünf Bedingungen, `J @ grad_S == 0`. Das IST per
Definition die Aussage, dass die Entropie `S` eine Casimir-Funktion der
Poisson-Struktur `J` ist — der Code verlangt das bereits, ohne das
Konzept zu benennen oder eine Methode zu haben, um Casimir-Funktionen
zu FINDEN oder eine gegebene Kandidatenfunktion unabhängig zu prüfen.

**Explizite Abgrenzung (WICHTIG, nicht verwässern):** Fluiddynamik wird
hier NUR als motivierende Quelle des Theorems zitiert. Dieser Auftrag
verlangt AUSSCHLIESSLICH den endlich-dimensionalen Fall (z.B. den
starren Körper auf so(3)*) — KEIN Fluid-PDE-Löser, KEINE Behauptung,
dass `coupling` "Fluiddynamik ist" oder dass irgendein bestehender
Baustein mit Fluiddynamik gleichgesetzt wird. Die strukturelle
Ähnlichkeit ist ein Grund, dies als eigenständige, separat geprüfte
Erweiterung von `coupling` zu bauen — kein Beweis für irgendeine
Gleichsetzung.

## Umfang dieses Auftrags

### 1. `coupling.casimir.casimir_residual(J, grad_C)`

Für eine gegebene antisymmetrische Matrix `J` (wie in
`check_generic_structure`) und den Gradienten `grad_C` einer
Kandidatenfunktion `C`: gibt `J @ grad_C` (Vektor) und dessen Norm
zurück. `C` ist eine Casimir-Funktion von `J` genau dann, wenn dieses
Residuum (numerisch) Null ist — das gilt dann für JEDEN Hamiltonian.

### 2. `coupling.casimir.hat_map(z)`

Hilfsfunktion: für `z=(z1,z2,z3) ∈ ℝ³` die schiefsymmetrische Matrix

    J(z) = [[0,-z3,z2],[z3,0,-z1],[-z2,z1,0]]

(die kanonische Lie-Poisson-Struktur auf so(3)*, starrer Körper).

### 3. Pflicht-Kompatibilitätsprüfung

Zeigen, dass `casimir_residual(J, grad_S)` für ein bereits gemergtes
`check_generic_structure`-Beispiel (aus `coupling/core.py`s eigenen
Tests oder `thermo/core.py`s GENERIC-Beispiel) GENAU dasselbe Ergebnis
liefert wie das bestehende `report["residuals"]["max_abs_J_grad_S"]" —
per direktem Aufruf von `check_generic_structure`, NICHT durch
Neuimplementierung der Logik.

### 4. Durchgerechnetes Beispiel (Starrkörper auf so(3)*)

`z=(1,2,3)`, `J=hat_map(z)`. Prüfen:
- `J` ist exakt schiefsymmetrisch (`J.T + J == 0` bis auf Toleranz).
- Casimir `C(z)=|z|²/2`, `grad_C=(1,2,3)`: `casimir_residual` ergibt
  exakt `(0,0,0)`.
- Hamiltonian `H(z)=Σ zᵢ²/(2·Iᵢ)` mit Trägheitsmomenten `I=(1,2,3)`:
  `grad_H=(1,1,1)`, `ż=J@grad_H`. Zeigen: `dC/dt = grad_C · ż = 0` UND
  `dH/dt = grad_H · ż = 0` — beide Erhaltungsgrößen exakt (kleine
  Ganzzahlen, von Hand nachrechenbar).

### 5. Explizit NICHT Teil dieses Auftrags

- KEINE unendlich-dimensionale/Fluid-PDE-Implementierung.
- KEINE Änderung an `coupling/core.py` — nur Aufruf von
  `check_generic_structure` zur Kompatibilitätsprüfung.
- KEINE Behauptung, dass `coupling` "Fluiddynamik" oder irgendein
  anderer Baustein "ist" — im Docstring explizit als eigenständige,
  separat verifizierte Erweiterung kennzeichnen.
- KEIN allgemeiner Casimir-Finder (z.B. symbolisches Lösen von
  `J∇C=0`) — nur die Residuum-Prüfung für eine GEGEBENE Kandidatin.

## Verifikation

`verify_casimir_residual.py`: (1) Starrkörper-Beispiel oben exakt
reproduziert (Zahlen aus dem Skriptlauf), (2) Kompatibilitätsprüfung
gegen `check_generic_structure` wie oben, (3) Negativfall: eine
Funktion `C'` wählen, die KEINE Casimir-Funktion von `J(z)` ist (z.B.
`grad_C' = (1,0,0)`), und zeigen, dass das Residuum ungleich Null ist.

## Abnahmebedingungen (Astra-Standard, unverändert)

1. Textformeln (LaTeX/Markdown), keine Bildformeln.
2. `verify_casimir_residual.py` mit reproduzierbarem JSON-Report unter
   `verification/`.
3. Durchgerechnetes Beispiel mit Zahlen AUS DEM SKRIPTLAUF.
4. Explizites Mapping auf Arnold (1966)/Marsden & Ratiu (1999) UND auf
   `coupling.core.check_generic_structure`s bestehende `J∇S=0`-
   Bedingung.
5. KEINE Mutation von FORMALISM.md, `coupling_layer_afet.md` oder einem
   der anderen sechs Kerndokumente.
6. Johann-OK vor jeder Aufnahme in einen "Kern"-Status.

## Lieferformat

Eigener Branch `aeon/m26-lie-poisson-casimir` auf
`GenesisAeon/scoped-correspondence-formalism`, direkt gepusht. Kann
PARALLEL zu Milestone 25 (`observation`), 27 (`membership`), 28
(`viability`) und 29 (`dynamics`) bearbeitet werden. Bitte NICHT
`src/scoped_correspondence/__init__.py` anfassen. Claude reviewed und
merged erst nach Johanns OK.
