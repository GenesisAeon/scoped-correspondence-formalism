Auftrag: Teil 2, Milestone 24 ("Čech-Cohomology-Witness") — natürliche
Erweiterung von `contextuality`, aus `ChatGPTAstra3.md` (Abramsky,
Mansfield & Barbosa 2012, arXiv 1111.3620, "The Cohomology of
Non-Locality and Contextuality", von Claude gegen die Quelle geprüft).
Letzter offener Kandidat aus `EXTENSIONS_ROADMAP.md` — mit diesem
Auftrag sind alle bisher identifizierten 17 Erweiterungskandidaten in
Arbeit oder abgeschlossen.

## Kontext

`contextuality` hat bereits die Sheaf-Kontextualität (F08, LP-basierte
Contextual Fraction) und die CSW-Grapheninvarianten (M19, gemergt).
Abramsky/Mansfield/Barbosa liefern eine DRITTE Charakterisierung: eine
Čech-Kohomologieklasse (mit `Z_2`-Koeffizienten für die hier relevanten
Fälle) als Kontextualitäts-Hindernis (Obstruction). Der entscheidende,
asymmetrische epistemische Status MUSS im Code sichtbar sein:

**Nichtverschwindende Obstruktion ist HINREICHEND für Kontextualität,
aber NICHT NOTWENDIG.** Ein verschwindendes Hindernis beweist NICHT
Nichtkontextualität.

## Umfang dieses Auftrags

### 1. `contextuality.cohomology.cech_obstruction(model)`

Nimmt ein bereits gemergtes `EmpiricalModel` (aus `contextuality/core.py`
— nur Aufruf, `core.py` NICHT ändern) und berechnet die Čech-
Kohomologie-Obstruktion über den bestehenden `bell_222_scenario`
(2,2,2-Bell-Szenario). Implementierungsmethode frei wählbar (z.B.
Rang der Korand-Abbildung über `GF(2)` — kleine, endliche Szenarien
genügen).

### 2. `contextuality.cohomology.CohomologyWitness`

Typisiert: `obstruction_nonzero: bool`, `degree: int`,
`coefficient_ring: str` (hier `"Z_2"`), `proves_contextuality: bool`
(gleich `obstruction_nonzero`, NIEMALS umgekehrt interpretiert).

### 3. Pflicht-Negativtest (WICHTIGER als der Positivtest)

Ein Test, der explizit zeigt: verschwindende Obstruktion wird NICHT
als Nichtkontextualitäts-Beweis ausgegeben. Konkret NICHT erlaubt:

```python
is_contextual = not obstruction_vanishes  # VERBOTEN
```

### 4. Durchgerechnete Beispiele über bestehende Szenarien

- `classical_factorizable_model(bell_222_scenario())` (M7, bereits
  gemergt, `CF=0`): Obstruktion verschwindet.
- `pr_box_model(bell_222_scenario())` (M7, bereits gemergt, `CF=1`,
  maximal kontextuell): Obstruktion nicht null — als Kreuzprobe gegen
  die bereits vorhandene `contextual_fraction`-LP (beide Methoden
  müssen für den PR-Box-Fall Kontextualität anzeigen, auch wenn sie
  unterschiedliche mathematische Werkzeuge sind).

### 5. Explizit NICHT Teil dieses Auftrags

- Keine Änderung an `contextuality/core.py` oder `contextuality/csw.py`
  — eigenes, separates Modul, nur Aufruf der bestehenden Szenario-
  Builder.
- Keine allgemeine kombinatorische Kohomologie-Bibliothek für beliebige
  Szenarien — nur der bestehende `bell_222_scenario`-Fall.
- Keine Gleichsetzung mit `contextual_fraction`/CSW als "dieselbe
  Zahl" — alle drei bleiben unabhängige, unterschiedlich begründete
  Charakterisierungen desselben Konzepts.

## Verifikation

`verify_cech_cohomology_core.py`: (1) klassisches Modell → Obstruktion
verschwindet, (2) PR-Box → Obstruktion nicht null, (3) Pflicht-
Negativtest wie oben (`test_vanishing_obstruction_does_not_certify_
noncontextuality`), (4) Kreuzprobe gegen die bereits gemergte
`contextual_fraction`-LP für beide Fälle.

## Abnahmebedingungen (Astra-Standard, unverändert)

1. Textformeln (LaTeX/Markdown), keine Bildformeln.
2. `verify_cech_cohomology_core.py` mit reproduzierbarem JSON-Report
   unter `verification/`.
3. Durchgerechnetes Beispiel mit Zahlen AUS DEM SKRIPTLAUF.
4. Explizites Mapping auf Abramsky/Mansfield/Barbosa 2012 (arXiv oben)
   und `contextuality/core.py`s `EmpiricalModel`/`bell_222_scenario`.
5. KEINE Mutation von FORMALISM.md, `sheaf_contextuality.md` oder
   einem der anderen sechs Kerndokumente.
6. Johann-OK vor jeder Aufnahme in einen "Kern"-Status.

## Lieferformat

Eigener Branch `aeon/m24-cech-cohomology-witness` auf
`GenesisAeon/scoped-correspondence-formalism`, direkt gepusht. Kann
PARALLEL zu Milestone 21 (`closure`), 22 (`observation`) und 23
(`identifiability`) bearbeitet werden. Bitte NICHT
`src/scoped_correspondence/__init__.py` anfassen. Claude reviewed und
merged erst nach Johanns OK.
