Auftrag: Teil 2, Milestone 28 ("Nagumo-Tangentialkegel-Bedingung für
polyedrische Mengen") — natürliche Erweiterung von `viability`, aus
einer unabhängigen Claude-Agenten-Recherche (Runde 2 zu
`prompts/33_...md`).

## Quelle

M. Nagumo, "Über die Lage der Integralkurven gewöhnlicher
Differentialgleichungen", Proceedings of the Physico-Mathematical
Society of Japan, 3rd Series, 24, 551–559 (1942), DOI
10.11429/ppmsj1919.24.0_551. Per WebFetch der J-STAGE-Landingpage
verifiziert (Titel, Autor, Zeitschrift, Band, Seiten, Jahr, ISSN, DOI).
Englische Übersetzung als Sekundärquelle: Menner & Lavretsky, arXiv
2406.18614.

## Kontext

`viability/core.py` deckt bisher nur das SKALARE Intervall `K=[b,∞)`
ab (`has_safe_transfer`). Das bereits gemergte M16
(`viability/control_barrier.py`) liefert eine HINREICHENDE Bedingung
für glatte Barrierefunktionen `h`. Nagumos Satz ist die NOTWENDIGE UND
HINREICHENDE Charakterisierung über den Tangentialkegel — und
funktioniert auch für NICHT-GLATTE Mengen (Polyeder/Boxen), wo M16
nicht direkt anwendbar ist (kein einzelnes glattes `h` existiert an
einer Ecke).

Für ein Polyeder `K = {z : a_i^T z <= b_i, i=1..m}` reduziert sich die
allgemeine Tangentialkegel-Bedingung an einem Randpunkt `z` auf: für
JEDE AKTIVE Nebenbedingung `i` (d.h. `a_i^T z = b_i`) muss gelten
`a_i^T f(z) <= 0`.

## Umfang dieses Auftrags

### 1. `viability.nagumo.active_constraints(z, A, b, tol=1e-9)`

`A` ist eine (m×n)-Matrix, `b` ein m-Vektor (Nebenbedingungen
`A@z <= b`). Gibt die Indizes der Zeilen zurück, für die `A[i]@z`
innerhalb `tol` von `b[i]` liegt.

### 2. `viability.nagumo.tangent_cone_condition(z, f_z, A, b, tol=1e-9)`

Prüft für JEDE aktive Nebenbedingung `i`: `A[i] @ f_z <= tol`.
Rückgabe: `dict` mit `ok: bool`, pro aktiver Zeile die Marge
`b[i]-Rest` bzw. den Wert `A[i]@f_z`, und `active_indices`.

### 3. `viability.nagumo.verify_polyhedral_viability(A, b, f, boundary_samples)`

Sweept über eine gegebene Liste von Randpunkten (vom Aufrufer
bereitgestellt — KEIN eigener Rand-Sampler/Kernel-Solver) und wendet
`tangent_cone_condition` an jedem Punkt an. Rückgabe: Gesamtergebnis +
Einzelheiten pro Punkt.

### 4. Durchgerechnetes Beispiel

Lineares System `ż = A_sys z` mit

    A_sys = [[-1, 0.5], [-0.5, -1]]

Menge `K = [-1,1] × [-1,1]` (als 4 Nebenbedingungen `z1<=1, -z1<=1,
z2<=1, -z2<=1`). Für JEDE der vier Kantenmitten UND alle vier Ecken
zeigen, dass die Tangentialkegel-Bedingung erfüllt ist:

- Kante `z1=1` (z2 variiert in [-1,1]): `f1 = -1+0.5·z2 ∈ [-1.5,-0.5]`,
  also stets `<=0` — Randbedingung erfüllt.
- Ecke `(1,1)`: `f=(-0.5,-1.5)` — beide Komponenten `<0`, liegt im
  Tangentialkegel der Ecke (negativer Quadrant).
- Ecke `(1,-1)`: `f=(-1.5, 0.5)`.
- Ecke `(-1,1)`: `f=(1.5, -0.5)`.
- Ecke `(-1,-1)`: `f=(0.5, 1.5)`.

Alle vier Ecken UND alle vier Kanten müssen im Skriptlauf bestätigt
werden (mindestens 20 Randpunkte pro Kante als Sweep, wie im
Rechercheergebnis verwendet).

### 5. Explizit NICHT Teil dieses Auftrags

- KEIN allgemeiner Viability-Kernel-Solver (Saint-Pierre-Algorithmus)
  — `viability/core.py`s eigener Docstring schließt das bereits
  explizit aus, dabei bleibt es.
- KEINE gekrümmten/nichtlinearen Ränder — nur Polyeder/Boxen.
- KEINE Änderung an `viability/core.py` oder `control_barrier.py` — rein
  additives, separates Modul.
- KEINE Behauptung, dies "ersetze" M16 — im Docstring festhalten, dass
  es eine andere Fallklasse abdeckt (nicht-glatt statt glatt), keine
  Verallgemeinerung im Sinne von "besser", sondern "anders anwendbar".

## Verifikation

`verify_nagumo_tangent_cone.py`: (1) Beispiel oben exakt reproduziert
(alle vier Kanten + vier Ecken, Zahlen aus dem Skriptlauf), (2)
Negativtest: ein `A_sys`, bei dem eine Ecke die Bedingung VERLETZT
(selbst konstruieren), zeigt `ok=False` für genau diese Ecke.

## Abnahmebedingungen (Astra-Standard, unverändert)

1. Textformeln (LaTeX/Markdown), keine Bildformeln.
2. `verify_nagumo_tangent_cone.py` mit reproduzierbarem JSON-Report
   unter `verification/`.
3. Durchgerechnetes Beispiel mit Zahlen AUS DEM SKRIPTLAUF.
4. Explizites Mapping auf Nagumo (1942) UND auf `viability/core.py`s
   bestehende Rolle (Erweiterung der Fallklasse, kein Ersatz für M16).
5. KEINE Mutation von FORMALISM.md, `context_transformations.md`,
   `worked_example_viability.md` oder einem der anderen Kerndokumente.
6. Johann-OK vor jeder Aufnahme in einen "Kern"-Status.

## Lieferformat

Eigener Branch `aeon/m28-nagumo-tangent-cone` auf
`GenesisAeon/scoped-correspondence-formalism`, direkt gepusht. Kann
PARALLEL zu Milestone 25 (`observation`), 26 (`coupling`), 27
(`membership`) und 29 (`dynamics`) bearbeitet werden. Bitte NICHT
`src/scoped_correspondence/__init__.py` anfassen. Claude reviewed und
merged erst nach Johanns OK.
