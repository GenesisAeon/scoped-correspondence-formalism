Auftrag: Teil 2, Milestone 17 ("BROJA Bivariate Unique Information") —
natürliche Erweiterung von `information_decomposition`, aus
`ChatGPTAstra3.md` (Bertschinger, Rauh, Olbrich, Jost & Ay 2014, DOI
10.3390/e16042161, von Claude gegen die Quelle geprüft).

## Kontext

`information_decomposition` (M7, gemergt) hat bereits Williams-Beer
`I_min` (`pid_atoms_williams_beer`) und Blackwell-RB
(`rb0_blackwell`/`blackwell_redundancy_finite_y`), inklusive des
TWO_BIT_COPY-Gegenfalls (`two_bit_copy_joint`, `two_bit_copy_report`):
unabhängige faire Bits A,B, Ziel Y=(A,B). Williams-Beer liefert dort
irreführend `Red=1`; Blackwell-RB korrekt `0`.

Bertschinger et al. (2014, "BROJA") definieren ein DRITTES, unabhängiges
Zerlegungsmaß über eine Optimierung: für Ziel `X` und Quellen `Y,Z`

\[
\Delta_P=\{Q:\ Q_{XY}=P_{XY},\ Q_{XZ}=P_{XZ}\},\qquad
\widetilde{UI}(X{:}Y\setminus Z)=\min_{Q\in\Delta_P} I_Q(X;Y\mid Z).
\]

**Namenskonvention für dieses Repo:** In unserer bestehenden API ist
das Ziel `y` (`target`) und die Quellen sind `r1`, `r2` — NICHT `X,Y,Z`
wie im Paper. Mapping: Paper-`X` = unser `y` (Ziel), Paper-`Y` = unser
`r1`, Paper-`Z` = unser `r2`. Diese Zuordnung MUSS im Docstring explizit
stehen, um Verwechslung mit unserer eigenen `y`-Konvention zu
vermeiden.

## Umfang dieses Auftrags

### 1. `information_decomposition.broja.broja_pid_bivariate(joint_r1r2y)`

Löst `min_{Q∈Δ_P} I_Q(y; r1 | r2)` (und symmetrisch für `r2`) über
eine konvexe Optimierung (Methode frei wählbar — z.B.
`scipy.optimize.minimize` mit linearen Nebenbedingungen für die
Randverteilungs-Erhaltung, oder ein iteratives Verfahren; die
zulässige Menge `Δ_P` ist ein Polytop, die Zielfunktion konvex).
**Pflicht:** Konvergenz durch mindestens 3 unabhängige Startpunkte
bestätigen (gleiches Optimum innerhalb Toleranz), da es sonst keinen
geschlossenen Referenzwert gibt.

### 2. `information_decomposition.broja.BivariatePIDReport`

Typisiert: `redundancy`, `unique_source_1`, `unique_source_2`,
`synergy`, `method="broja"`. MUSS zusätzlich `I_joint` berichten und
prüfen, dass `redundancy+unique_1+unique_2+synergy == I_joint`
(Konsistenzprüfung, wie bereits bei `pid_atoms_williams_beer`).

### 3. TWO_BIT_COPY-Kreuzprobe (Pflicht-Testfall)

Wende `broja_pid_bivariate` auf `two_bit_copy_joint()` (M7, bereits
gemergt — nur Aufruf) an. Erwartetes, literaturbekanntes Ergebnis
(BROJA korrigiert die Williams-Beer-Pathologie anders als Blackwell-RB,
aber in dieselbe Richtung): `redundancy≈0`, `unique_source_1≈1`,
`unique_source_2≈1`, `synergy≈0` (jede Quelle trägt exakt ihr eigenes
Bit eindeutig bei, keine Redundanz, keine Synergie — im Gegensatz zu
Williams-Beers `Red=1`). Bericht MUSS alle DREI Maße nebeneinander
zeigen (Williams-Beer, Blackwell-RB, BROJA) — keines ersetzt ein
anderes.

### 4. Explizit NICHT Teil dieses Auftrags

- Keine Änderung an `information_decomposition/core.py` — nur Aufruf
  von `two_bit_copy_joint`, `pid_atoms_williams_beer`, `rb0_blackwell`
  zur Kreuzprobe.
- Keine N-Quellen-Verallgemeinerung — nur der bivariate (2-Quellen)-Fall.
- Kein allgemeiner BROJA-Solver für beliebig große Alphabete — der
  TWO_BIT_COPY-Fall (klein, 2×2×4) genügt für dieses Milestone.

## Verifikation

`verify_broja_pid_core.py`: (1) TWO_BIT_COPY-Ergebnis wie oben
(Toleranz dokumentieren), (2) Konsistenz `Red+Unq1+Unq2+Syn=I_joint`,
(3) Konvergenz-Check über mehrere Startpunkte, (4) Bericht zeigt
Williams-Beer/Blackwell-RB/BROJA nebeneinander für denselben Fall.

## Abnahmebedingungen (Astra-Standard, unverändert)

1. Textformeln (LaTeX/Markdown), keine Bildformeln.
2. `verify_broja_pid_core.py` mit reproduzierbarem JSON-Report unter
   `verification/`.
3. Durchgerechnetes Beispiel mit Zahlen AUS DEM SKRIPTLAUF.
4. Explizites Mapping auf Bertschinger et al. 2014 (DOI oben) und die
   Namenskonvention aus Abschnitt "Kontext".
5. KEINE Mutation von FORMALISM.md, `pid_redundancy_bottleneck.md` oder
   einem der anderen sechs Kerndokumente.
6. Johann-OK vor jeder Aufnahme in einen "Kern"-Status.

## Lieferformat

Eigener Branch `aeon/m17-broja-pid` auf
`GenesisAeon/scoped-correspondence-formalism`, direkt gepusht. Kann
PARALLEL zu Milestone 18 (`thermo`), 19 (`contextuality`) und 20
(`identifiability`) bearbeitet werden — unterschiedliche Module. Bitte
NICHT `src/scoped_correspondence/__init__.py` anfassen
(Konfliktvermeidung, wie bei M11–M16). Claude reviewed und merged erst
nach Johanns OK.
