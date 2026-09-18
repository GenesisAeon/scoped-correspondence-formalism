Auftrag: Teil 2, Milestone 18 ("Schnakenberg Network Thermodynamics") —
natürliche Erweiterung von `thermo`, aus `ChatGPTAstra3.md` (Schnakenberg
1976, DOI 10.1103/RevModPhys.48.571, von Claude gegen die Quelle
geprüft).

## Kontext

`thermo.stochastic_inverse_not_detailed_balance` (M8, gemergt) zeigt an
einer DETERMINISTISCHEN Drei-Zyklus-Permutation, dass stochastische
Invertierbarkeit kein Detailed Balance impliziert. Schnakenberg (1976)
liefert die quantitative Vertiefung für STOCHASTISCHE Kreisläufe mit
echten Raten: für eine kontinuierliche Markov-Kette mit stationärer
Verteilung `p` und Ratenmatrix `k` sind die Kantenströme und lokalen
Affinitäten

\[
J_{ij}=p_ik_{ij}-p_jk_{ji},\qquad
A_{ij}=\ln\frac{p_ik_{ij}}{p_jk_{ji}},
\]

und die Entropieproduktion

\[
\dot S_{prod}=\frac12\sum_{i,j}J_{ij}A_{ij}\ge0.
\]

Onsager-Reziprozität erscheint hier nur als Near-Equilibrium-
Spezialfall, KEINE generelle Identität beliebiger Kopplungsmatrizen
(explizit im Docstring festhalten — Anschluss an die bereits
etablierte `thermo`-Disziplin, keine `A_ij≡L_ij`-artige Gleichsetzung).

## Umfang dieses Auftrags

### 1. `thermo.schnakenberg.stationary_currents(p, k)`

Berechnet `J_ij` für alle Kantenpaare eines gegebenen Ratenmatrix-
Generators `k` (off-diagonal ≥0) mit stationärer Verteilung `p`.

### 2. `thermo.schnakenberg.cycle_affinity(p, k, i, j)`

Berechnet `A_ij = ln(p_i k_ij / (p_j k_ji))`.

### 3. `thermo.schnakenberg.entropy_production_rate(p, k)`

Berechnet `Ṡ_prod = (1/2)·Σ_{i,j} J_ij·A_ij`, validiert `>= 0` (Pflicht-
Check, kein optionaler Hinweis — negative Werte müssen
`ScopeViolationError` auslösen als Zeichen eines inkonsistenten `p`/`k`).

### 4. Durchgerechnetes Beispiel (bereits von Claude bestätigt)

Symmetrischer Drei-Zyklus: Uhrzeigersinn-Rate `2`, Gegen-Uhrzeigersinn-
Rate `1`. Stationäre Verteilung wegen Symmetrie `p_1=p_2=p_3=1/3`
(NICHT annehmen — im Skript aus der Ratenmatrix per Gleichgewichts-
bedingung herleiten oder explizit verifizieren, dass `p@k=0`). Auf
jeder im Uhrzeigersinn orientierten Kante:

\[
J=\frac13(2-1)=\frac13,\qquad A=\ln2.
\]

Über die drei Kanten: `Ṡ_prod = 3·(1/3)·ln2 = ln2 ≈ 0,6931`. Diese
Zahl im Skript exakt reproduzieren (Toleranz dokumentieren).

Explizit vermerken: dieses `Ṡ_prod=ln2` hat KEINERLEI Bezug zu einem
früher verwendeten `σ=2,2`-Wert oder sonstigen Ökosystem-Defaults —
eigenständige, frisch berechnete Zahl.

### 5. Explizit NICHT Teil dieses Auftrags

- Keine Änderung an `thermo/core.py` — eigenes, separates Modul.
- Keine Verbindung zum bereits vorhandenen deterministischen Drei-
  Zyklus-Beispiel (M8) als gemeinsame Formel — beide bleiben getrennte,
  unterschiedliche Beispiele (deterministisch vs. stochastisch mit
  Raten).
- Keine allgemeine Netzwerktheorie für beliebige Graphtopologien — nur
  der Drei-Zyklus-Fall.

## Verifikation

`verify_schnakenberg_core.py`: keine bestehende Legacy-Prüfung —
frisches Beispiel. Mindestens: (1) `p@k≈0` (Stationaritätsprüfung),
(2) `J=1/3` je Kante, `A=ln2`, (3) `Ṡ_prod=ln2` exakt, (4) ein
zweiter, absichtlich AUS DEM GLEICHGEWICHT gebrachter Fall mit anderer
Rate zur Gegenprobe (nichtnegative Entropieproduktion bleibt erhalten,
konkreter anderer Zahlenwert).

## Abnahmebedingungen (Astra-Standard, unverändert)

1. Textformeln (LaTeX/Markdown), keine Bildformeln.
2. `verify_schnakenberg_core.py` mit reproduzierbarem JSON-Report unter
   `verification/`.
3. Durchgerechnetes Beispiel mit Zahlen AUS DEM SKRIPTLAUF.
4. Explizites Mapping auf Schnakenberg 1976 (DOI oben) und `thermo/core.py`s
   Drei-Zyklus-Thematik (nur als Kontext, keine gemeinsame Formel).
5. KEINE Mutation von FORMALISM.md, `coupling_layer_afet.md` oder
   einem der anderen sechs Kerndokumente.
6. Johann-OK vor jeder Aufnahme in einen "Kern"-Status.

## Lieferformat

Eigener Branch `aeon/m18-schnakenberg-thermodynamics` auf
`GenesisAeon/scoped-correspondence-formalism`, direkt gepusht. Kann
PARALLEL zu Milestone 17 (`information_decomposition`), 19
(`contextuality`) und 20 (`identifiability`) bearbeitet werden. Bitte
NICHT `src/scoped_correspondence/__init__.py` anfassen. Claude reviewed
und merged erst nach Johanns OK.
