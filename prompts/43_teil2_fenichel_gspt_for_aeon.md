Auftrag: Teil 2, Milestone — Fenichel / Geometric Singular Perturbation
Theory (GSPT) — Erweiterung von `dynamics`. Aus Runde 3 (vier
unabhängige Rechercheagenten, alle vier haben dies vorgeschlagen bzw.
als bereits bekannten offenen Punkt bestätigt — ursprünglich seit
Runde 1 in `EXTENSIONS_ROADMAP.md` als "offen" geführt).

## Quelle

N. Fenichel, "Geometric singular perturbation theory for ordinary
differential equations", J. Differential Equations 31, 53–98 (1979),
DOI 10.1016/0022-0396(79)90152-9. Per Crossref-API verifiziert
(Titel/Autor/Jahr/Band/Seiten exakt bestätigt). Sekundärreferenz für
die Störungsreihenform: C. Kuehn, "Multiple Time Scale Dynamics",
Springer 2015, DOI 10.1007/978-3-319-12316-5 (bereits in
`EXTENSIONS_ROADMAP.md` als Begleitzitat genannt).

## Kernformel

Fast-langsam-System `ε ẋ = f(x,y)`, `ẏ = g(x,y)`. Kritische
Mannigfaltigkeit `C_0 = {(x,y): f(x,y)=0}`. Ist `C_0` kompakt und
NORMAL HYPERBOLISCH (Eigenwerte von `D_x f|_{C_0}` haben Realteil
≠ 0), existiert für hinreichend kleines `ε>0` eine glatte, lokal
invariante langsame Mannigfaltigkeit `C_ε`, `O(ε)`-nah an `C_0`. An
Faltpunkten (Verlust der Normalhyperbolizität) gilt die Aussage
lokal NICHT.

## Umfang dieses Auftrags

Neue Datei `src/scoped_correspondence/dynamics/gspt.py`.

### 1. `dynamics.gspt.critical_manifold_fold_points(...)`

Für das Van-der-Pol-Standardbeispiel `S(x) = x³/3 - x` (kritische
Mannigfaltigkeit `y = S(x)`): findet die Faltpunkte `S'(x)=0` ⇒
`x=±1`, gibt `(x, S(x))` für beide zurück.

### 2. `dynamics.gspt.is_normally_hyperbolic(x, tol=1e-9)`

Prüft `S'(x) = x²-1 ≠ 0` (mit Toleranz) am gegebenen Punkt.

### 3. `dynamics.gspt.slow_manifold_distance_bound(epsilon, x)` (optional, falls im Beispiel gebraucht)

Dokumentierter `O(ε)`-Abstand `dist(C_ε, C_0)` an einem Punkt fernab
der Falten — als grobe, explizit als Ordnungsabschätzung markierte
Schranke, KEINE exakte Formel (Fenichel liefert nur Existenz + Ordnung,
keine geschlossene Form).

### 4. Durchgerechnetes Beispiel (Pflicht)

Van-der-Pol-Normalform `S(x)=x³/3-x`: Faltpunkte bei `x=±1`,
`S(1)=1/3-1=-2/3`, `S(-1)=-1/3+1=2/3` (exakt, im Skriptlauf
nachrechnen). Normalhyperbolizität: `S'(2)=3>0` (attraktiv),
`S'(0)=-1<0` (Falte/repulsiv im lokalen Sinn), `S'(1.5)=1.25>0`.
Zeigen, dass `is_normally_hyperbolic` bei `x=±1` `False` liefert (dort
scheitert die Voraussetzung), bei `x=2, x=0, x=1.5` `True`.

### 5. Explizit NICHT Teil dieses Auftrags

- KEINE volle Canard-/Blow-up-Theorie an den Faltpunkten.
- KEINE Verwechslung mit M14 (Kontraktionsanalyse, globale metrische
  Kontraktion) oder M29 (Landau-Exponentenvergleich) — im Docstring
  festhalten, dass dies ein drittes, unabhängiges `dynamics`-Thema ist.
- KEINE Änderung an `dynamics/core.py` — nur additive neue Datei.

## Verifikation

`verify_gspt_core.py`: (1) Faltpunkte exakt reproduziert, (2)
Normalhyperbolizität an mindestens 4 Testpunkten (2 positiv, 2
negativ/Grenzfall), (3) Quellenangabe im JSON-Report.

## Abnahmebedingungen (Astra-Standard, unverändert)

1. Textformeln (LaTeX/Markdown), keine Bildformeln.
2. Neues Dokument `docs/gspt_core.md`.
3. `verify_gspt_core.py` mit reproduzierbarem JSON-Report unter
   `verification/`.
4. Durchgerechnetes Beispiel mit Zahlen AUS DEM SKRIPTLAUF.
5. Explizites Mapping auf Fenichel (1979)/Kuehn (2015).
6. KEINE Mutation von FORMALISM.md oder einem der anderen sieben
   Kerndokumente.
7. Johann-OK vor jeder Aufnahme in einen "Kern"-Status.

## Lieferformat

Eigener Branch `aeon/m33-fenichel-gspt`. Kann PARALLEL zu den anderen
Runde-3-Milestones bearbeitet werden — mehrere betreffen ebenfalls
`dynamics` (Floquet, Panarchy-Cusp, Scheffer Early-Warning); jede
erhält eine EIGENE neue Datei in `dynamics/`, sodass nur
`dynamics/__init__.py` und `pyproject.toml` beim Merge triviale,
erwartbare Konflikte haben können (wie bei allen bisherigen
Parallel-Batches). Bitte NICHT `src/scoped_correspondence/__init__.py`
oder `dynamics/core.py` anfassen. Claude reviewed und merged erst nach
Johanns OK.
