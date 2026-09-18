Auftrag: Teil 2, Milestone 19 ("CSW-Grapheninvarianten") — natürliche
Erweiterung von `contextuality`, aus der `.docx`-Recherche (Cabello,
Severini & Winter 2014, PRL 112, 040401, von Claude gegen die Quelle
geprüft).

## Kontext

`contextuality` (M7, gemergt) implementiert bereits Abramsky-
Brandenburger empirische Modelle und die Contextual Fraction (LP-
basiert, `contextual_fraction`). Cabello-Severini-Winter (CSW)
liefern eine ZWEITE, graphentheoretische Charakterisierung: jedem
Beobachtungsszenario wird ein Orthogonalitätsgraph `G` zugeordnet
(Knoten = Messergebnisse, Kanten = exklusive Verträglichkeit). Die
Summe der Wahrscheinlichkeiten verträglicher Ereignisse ist beschränkt
durch drei graphentheoretische Invarianten:

\[
\alpha(G)\ \text{(klassisch)}\ \le\ \vartheta(G)\ \text{(Quanten)}\ \le\ \alpha^*(G)\ \text{(allgemein-probabilistisch, No-Signaling)}.
\]

`α(G)` = Stabilitätszahl (Independence Number), `ϑ(G)` = Lovász-
Theta-Funktion, `α*(G)` = gebrochene Überdeckungszahl (Fractional
Packing Number).

**Bekannte, exakte Referenzwerte für das KCBS-Szenario** (5-Zyklus
`C5` als Orthogonalitätsgraph — Klyachko-Can-Binicioğlu-Shumovsky):

\[
\alpha(C_5)=2,\qquad \vartheta(C_5)=\sqrt5\approx2.236,\qquad
\alpha^*(C_5)=\tfrac52=2.5.
\]

`ϑ(C5)=√5` ist Lovász' eigenes klassisches Resultat (1979) für den
Pentagon-Graphen — MUSS im Skript tatsächlich berechnet werden (nicht
nur aus der Literatur übernommen), z.B. über die bekannte "Regenschirm"-
Orthonormaldarstellung (Lovász-Umbrella-Konstruktion für `C5`) oder ein
kleines SDP, falls ein Solver verfügbar ist. Die berechneten Werte
müssen mit den obigen Referenzwerten übereinstimmen (Selbstprüfung).

## Umfang dieses Auftrags

### 1. `contextuality.csw.independence_number(G)`

Für einen gegebenen Graphen (Adjazenzmatrix oder Kantenliste):
Stabilitätszahl `α(G)` (für `C5` exakt `2` — kleine Graphen, Brute-
Force über alle Teilmengen ist hier ausreichend, kein allgemeiner
Solver nötig).

### 2. `contextuality.csw.lovasz_theta(G)`

Lovász-Theta-Funktion. Für `C5` MUSS das Ergebnis `√5` sein (exakte
Konstruktion oder SDP, mit Toleranz dokumentiert).

### 3. `contextuality.csw.fractional_packing_number(G)`

`α*(G)`. Für `C5` exakt `5/2`.

### 4. `contextuality.csw.CSWWitness`

Typisiertes Ergebnis: `classical_bound`, `quantum_bound`,
`general_probabilistic_bound`, `observed_sum`, `classical_violated: bool`.

### 5. Durchgerechnetes Beispiel

Symmetrisches empirisches Modell auf `C5`: jedem der fünf Knoten
Wahrscheinlichkeit `p` (aus dem KCBS-Szenario ableiten oder explizit
als Parameter wählen), Gesamtsumme `5p`. Zeige: klassische Schranke
`α(C5)=2` wird überschritten (`5p>2`), Quantenschranke `√5` wird
eingehalten, allgemein-probabilistische Schranke `5/2` wird eingehalten
— alle drei Fälle mit konkreten Zahlen aus dem Skriptlauf.

### 6. Explizit NICHT Teil dieses Auftrags

- Keine Änderung an `contextuality/core.py` — eigenes, separates Modul.
- Keine allgemeine SDP-Bibliothek für beliebige Graphen — nur `C5`
  (und optional kleine Graphen via Brute-Force für `α(G)`).
- Keine Verbindung zur bestehenden `contextual_fraction`-LP als
  gemeinsame Formel — beide bleiben getrennte Charakterisierungen
  (Sheaf-CF vs. CSW-Graph-Invarianten) desselben Kontextualitäts-
  Konzepts, nicht identifiziert.

## Verifikation

`verify_csw_core.py`: (1) `α(C5)=2`, `ϑ(C5)=√5` (Toleranz), `α*(C5)=5/2`
exakt aus dem Skriptlauf, (2) durchgerechnetes Beispiel mit
Schrankenverletzung/-einhaltung wie oben, (3) Selbstprüfung: berechnete
Werte stimmen mit den Referenzwerten überein.

## Abnahmebedingungen (Astra-Standard, unverändert)

1. Textformeln (LaTeX/Markdown), keine Bildformeln.
2. `verify_csw_core.py` mit reproduzierbarem JSON-Report unter
   `verification/`.
3. Durchgerechnetes Beispiel mit Zahlen AUS DEM SKRIPTLAUF.
4. Explizites Mapping auf Cabello/Severini/Winter 2014 und
   `contextuality/core.py`s bestehende `EmpiricalModel`/`contextual_fraction`.
5. KEINE Mutation von FORMALISM.md, `sheaf_contextuality.md` oder
   einem der anderen sechs Kerndokumente.
6. Johann-OK vor jeder Aufnahme in einen "Kern"-Status.

## Lieferformat

Eigener Branch `aeon/m19-csw-graph-invariants` auf
`GenesisAeon/scoped-correspondence-formalism`, direkt gepusht. Kann
PARALLEL zu Milestone 17 (`information_decomposition`), 18 (`thermo`)
und 20 (`identifiability`) bearbeitet werden. Bitte NICHT
`src/scoped_correspondence/__init__.py` anfassen. Claude reviewed und
merged erst nach Johanns OK.
