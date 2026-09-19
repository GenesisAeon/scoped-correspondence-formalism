Auftrag: Teil 2, Milestone — Floquet-Multiplikatoren für periodische
Orbits — Erweiterung von `dynamics`. Aus Runde 3 (von einem der vier
unabhängigen Agenten vorgeschlagen; von Claude live gegen Crossref
verifiziert, siehe unten — Johanns Entscheidung: einzeln gefundene,
aber eindeutig belastbare Kandidaten werden unabhängig vom
Konvergenzgrad übernommen).

## Quelle

G. Floquet, "Sur les équations différentielles linéaires à
coefficients périodiques", Annales scientifiques de l'École normale
supérieure 12, 47–88 (1883), DOI 10.24033/asens.220. **Von Claude
selbst live per Crossref-API verifiziert** (Titel/Autor/Zeitschrift/
Band/Seiten/Jahr exakt bestätigt, 2026-09-19). Moderne Numerik-
Referenz: J.-P. Lessard, Castelli, SIAM J. Appl. Dyn. Syst. (2013),
DOI 10.1137/120873960.

## Kernformel

Sei `x*(t)` eine `T`-periodische Lösung von `ẋ=f(x)`. Die
Variationsgleichung `Φ̇ = Df(x*(t))·Φ`, `Φ(0)=I` liefert die
Monodromiematrix `M=Φ(T)`. Eigenwerte `μᵢ` von `M` sind die
Floquet-Multiplikatoren; `μᵢ=e^(λᵢT)`. Bei autonomem System ist stets
ein Multiplikator `μ=1` (Phasenrichtung). Orbitale asymptotische
Stabilität, wenn alle ÜBRIGEN `|μᵢ|<1`; Instabilität, wenn ein
`|μᵢ|>1`.

## Umfang dieses Auftrags

Neue Datei `src/scoped_correspondence/dynamics/floquet.py`.

### 1. `dynamics.floquet.floquet_multipliers(M)`

Für eine gegebene Monodromiematrix `M` (2×2, vom Aufrufer bereits
berechnet — KEIN eigener ODE-Integrator/Variationsgleichungslöser in
diesem Auftrag): Eigenwerte, Beträge, Stabilitätsklassifikation.

### 2. `dynamics.floquet.classify_orbital_stability(multipliers, tol=1e-9)`

Klassifiziert: "stable" (alle `|μ|<1` außer höchstens einem `μ≈1`),
"unstable" (mind. ein `|μ|>1`), "neutral" (Rest exakt auf dem
Einheitskreis, konservativer Fall).

### 3. Durchgerechnetes Beispiel (Pflicht)

Für eine 2×2-Monodromiematrix in Flächenform (`det M=1`,
Hamiltonsch/konservativ oder gedämpft):

- `tr M=1.5, det M=1`: `μ± = (1.5 ± i√1.75)/2`, `|μ±|=1` — neutral
  (konservativer Fall).
- `tr M=2.5, det M=1`: `μ± = (2.5 ± 1.5)/2 = {2, 0.5}` — instabil
  (`μ=2>1`). Beide Fälle im Skriptlauf exakt reproduzieren (die
  charakteristische Gleichung `μ²-tr(M)μ+det(M)=0` explizit lösen,
  nicht nur `numpy.linalg.eigvals` blind aufrufen — beide Wege
  gegeneinander prüfen).

### 4. Explizit NICHT Teil dieses Auftrags

- KEIN Variationsgleichungs-/ODE-Integrator — die Monodromiematrix wird
  als gegeben angenommen (vom Aufrufer berechnet oder im Beispiel
  hartkodiert mit Herleitung im Docstring).
- KEINE Verwechslung mit M14 (Kontraktionsanalyse — globale metrische
  Kontraktion, keine periodischen Orbits) — im Docstring festhalten.
- KEINE Änderung an `dynamics/core.py`.

## Verifikation

`verify_floquet_core.py`: (1) beide Fälle oben exakt reproduziert
(Eigenwerte aus charakteristischem Polynom UND aus `numpy.linalg.eigvals`
übereinstimmend), (2) Grenzfall `tr M=2, det M=1` (doppelter
Multiplikator `μ=1`) korrekt als Randfall behandelt (nicht als
"stable" fehlklassifiziert).

## Abnahmebedingungen (Astra-Standard, unverändert)

1. Textformeln (LaTeX/Markdown), keine Bildformeln.
2. Neues Dokument `docs/floquet_core.md`.
3. `verify_floquet_core.py` mit reproduzierbarem JSON-Report unter
   `verification/`.
4. Durchgerechnetes Beispiel mit Zahlen AUS DEM SKRIPTLAUF.
5. Explizites Mapping auf Floquet (1883).
6. KEINE Mutation von FORMALISM.md oder einem der anderen sieben
   Kerndokumente.
7. Johann-OK vor jeder Aufnahme in einen "Kern"-Status.

## Lieferformat

Eigener Branch `aeon/m34-floquet-multipliers`. Kann PARALLEL zu den
anderen Runde-3-Milestones bearbeitet werden — mehrere betreffen
ebenfalls `dynamics` (Fenichel/GSPT, Panarchy-Cusp, Scheffer
Early-Warning); jede erhält eine EIGENE neue Datei in `dynamics/`,
sodass nur `dynamics/__init__.py` und `pyproject.toml` beim Merge
triviale, erwartbare Konflikte haben können. Bitte NICHT
`src/scoped_correspondence/__init__.py` oder `dynamics/core.py`
anfassen. Claude reviewed und merged erst nach Johanns OK.
