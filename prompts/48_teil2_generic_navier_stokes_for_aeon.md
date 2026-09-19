Auftrag: Teil 2, Milestone — GENERIC ↔ Navier-Stokes (viskose
Dissipation) — Erweiterung von `coupling`. Aus Runde 3 (VON ALLEN VIER
unabhängigen Rechercheagenten übereinstimmend vorgeschlagen — höchste
Konvergenz zusammen mit dem Early-Warning-Kandidaten). Liegengebliebener
Punkt aus Runde 2 (`prompts/33_...md`), jetzt konkret ausgearbeitet.

## Quellen — WICHTIG, bitte genau so verwenden

- Für GENERIC selbst: M. Grmela & H. C. Öttinger, "Dynamics and
  thermodynamics of complex fluids. I", Phys. Rev. E 56, 6620–6632
  (1997), DOI 10.1103/PhysRevE.56.6620; H. C. Öttinger & M. Grmela,
  "... II. Illustrations...", Phys. Rev. E 56, 6633–6655 (1997), DOI
  10.1103/PhysRevE.56.6633. Beide von mehreren Agenten per Crossref
  verifiziert (Titel/Autoren/Band/Seiten/Jahr exakt).
- **Für die konkrete Navier-Stokes-Verbindung NICHT Öttinger-Grmela
  1997 als Hauptbeleg verwenden** — eine unabhängige Prüfung dieser
  Runde hat gezeigt, dass die Abstracts dieser beiden Arbeiten
  tatsächlich nichtisotherme Polymer-Kinetik-Theorien illustrieren,
  NICHT Navier-Stokes. Stattdessen: P. J. Morrison, "Bracket
  formulation for irreversible classical fields", Physics Letters A
  100(8), 423–427 (1984), DOI 10.1016/0375-9601(84)90635-2 (zeigt
  explizit, dass die Navier-Stokes-Fourier-Gleichungen Realisierungen
  dieser Bracket-Formulierung sind); und/oder W. Barham, P. J.
  Morrison, A. Zaidni, "A thermodynamically consistent discretization
  of 1D thermal-fluid models using their metriplectic 4-bracket
  structure", Commun. Nonlinear Sci. Numer. Simul. 145, 108683 (2025),
  DOI 10.1016/j.cnsns.2025.108683 (arXiv:2410.11045) — enthält das 1D-
  Navier-Stokes-Fourier-Modell mit explizitem viskosem Spannungsterm
  `∂ₓ(μ∂ₓu)` und Entropieproduktion `(μ/T)(∂ₓu)²`, direkt aus dem
  arXiv-HTML-Volltext zitierbar.

## Kernformel

GENERIC: `ẋ = J(x)·∇E(x) + M(x)·∇S(x)`, `J^T=-J`, `M^T=M⪰0`,
Degenerationen `J·∇S=0`, `M·∇E=0`. Für einen viskosen Fluss reduziert
sich der dissipative Block `M` auf den Navier-Stokes-Reibungsterm.

## Umfang dieses Auftrags

Neue Datei `src/scoped_correspondence/coupling/generic_navier_stokes.py`.

### 1. `coupling.generic_navier_stokes.two_cell_viscous_example(v1, v2, T, zeta)`

Baut für ein Zwei-Zellen-Scherströmungsmodell (Zustand
`x=(p1,p2,e1,e2)`, Massen `m=1`, `v_i=p_i/m`, gemeinsame Temperatur
`T`) die Größen `E=e1+e2`, `∇E=(v1,v2,1,1)`, `S=s(e1)+s(e2)`,
`∇S=(0,0,1/T,1/T)` (Toy-Entropie, `s'=1/T` konstant angenommen —
dokumentieren), `J=0`, `M=ζT·a·aᵀ` mit `a=(1,-1,-v1,v2)`.

### 2. Pflicht-Aufruf der bestehenden Prüffunktion

MUSS `coupling.core.check_generic_structure(J, M, ∇E, ∇S)`
(unverändert) auf dem Ergebnis aufrufen — NICHT die Struktur-Checks neu
implementieren.

### 3. Durchgerechnetes Beispiel (Pflicht)

`v1=3, v2=1, T=300, ζ=0.5`: `a=(1,-1,-3,1)`. Zeigen: `a·∇E =
1·3+(-1)·1+(-3)·1+1·1 = 0` (Degeneriertheit strukturell, nicht
erzwungen). `M∇S = -a·(ζT·(a·∇S))`. Mit `a·∇S = (-3+1)/300 = -1/150`:
`M∇S = 150·a·(-1/150) = -a = (-1,1,3,-1)`. Damit `ṗ1=-1N` — das ist
`-ζ(v1-v2) = -0.5·2 = -1`, der diskrete Navier-Stokes-Reibungsterm.
Entropieproduktion `∇S·M∇S = ζ(v1-v2)²/T = 0.5·4/300 =
0.006666...W/K ≥0`. `check_generic_structure` MUSS `ok=True` mit allen
fünf Residuen exakt `0.0` zurückgeben — dies im JSON-Report zeigen.

Zusätzlich: Newtonsche Reibungskraft-Übersetzung: mit Fläche `A=1m²`,
Zellabstand `Δy=0.01m` gilt `ζ = ηA/Δy` ⇒ `η=0.005 Pa·s` — als
dokumentierter, nicht als geprüfter Zusatzwert.

### 4. Explizit NICHT Teil dieses Auftrags

- KEIN 3D-Navier-Stokes-Löser, KEINE PDE-Diskretisierung — nur die
  0D/Zwei-Zellen-Reduktion.
- KEINE Änderung an `coupling/core.py` — nur Aufruf von
  `check_generic_structure`.
- KEINE Vermischung mit `LijTransport`/`AijInfluence` — das neue `M`
  ist ein GENERIC-Reibungsoperator, KEIN Onsager-Transportkoeffizient;
  im Docstring explizit festhalten, dass dies weder `A_ij` noch `L_ij`
  ist und keine gemeinsame Basisklasse hat.

## Verifikation

`verify_generic_navier_stokes.py`: (1) Beispiel oben exakt
reproduziert, INKLUSIVE des tatsächlichen Aufrufs von
`check_generic_structure` mit `ok=True` und allen Residuen `0.0` im
JSON, (2) Kontrollfall `v1=v2` (kein Geschwindigkeitsgradient) → `M∇S=0`,
keine Dissipation.

## Abnahmebedingungen (Astra-Standard, unverändert)

1. Textformeln (LaTeX/Markdown), keine Bildformeln.
2. Neues Dokument `docs/generic_navier_stokes_core.md`.
3. `verify_generic_navier_stokes.py` mit reproduzierbarem JSON-Report
   unter `verification/`.
4. Durchgerechnetes Beispiel mit Zahlen AUS DEM SKRIPTLAUF.
5. Explizites Mapping auf Grmela & Öttinger (1997, GENERIC selbst) UND
   Morrison (1984) bzw. Barham-Morrison-Zaidni (2025, die tatsächliche
   NS-Verbindung) UND `coupling.core.check_generic_structure`.
6. KEINE Mutation von FORMALISM.md, `coupling_layer_afet.md` oder
   einem der anderen sechs Kerndokumente.
7. Johann-OK vor jeder Aufnahme in einen "Kern"-Status.

## Lieferformat

Eigener Branch `aeon/m38-generic-navier-stokes`. Kann PARALLEL zu den
anderen Runde-3-Milestones bearbeitet werden (auch zu Milestone 39,
Pecora-Carroll, das ebenfalls `coupling` betrifft — eigene neue Datei,
nur `coupling/__init__.py`/`pyproject.toml` können triviale Konflikte
haben). Bitte NICHT `src/scoped_correspondence/__init__.py` oder
`coupling/core.py` anfassen. Claude reviewed und merged erst nach
Johanns OK.
